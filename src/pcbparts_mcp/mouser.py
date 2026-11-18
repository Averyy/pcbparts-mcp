"""Mouser Search API v2 client.

Answers are kept per part number in distributor_store.py for MOUSER_CACHE_TTL (3 days; not found a
day), so a batch reuses parts other calls fetched and sends only the rest. Mouser matches loosely and
doesn't say which part number each result is for, so results are matched back to the numbers asked
(_attribute): a number whose results can't all be put down to it alone isn't kept on its own, and the
whole batch is kept under its joined numbers instead. Concurrent one-part lookups share one request
(_pooled). Every answer's lifecycle goes into the lifecycle store.

Each request picks its API key as it goes out (Mouser takes the key in the query string): the first
key until its day is spent, then the next (MouserKeyPool). A daily refusal from Mouser moves the
request on to the next key.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Callable

import httpx

from . import stats
from .cache import DailyQuota, MouserKeyPool, QuotaPool
from .config import (
    MOUSER_API_KEY,
    MOUSER_BASE_URL,
    MOUSER_NOT_FOUND_TTL,
    MOUSER_POOL_WINDOW,
)
from .distributor_store import DistributorStore
from .lifecycle import MOUSER_NOT_STATED, Reading, mouser_status, utc_text
from .search.mpn import mpn_key

logger = logging.getLogger(__name__)


MOUSER_MAX_BATCH = 10  # part numbers per SearchByPartRequest (Mouser's API docs)


class MouserError(ValueError):
    """A Mouser request failed. The message is ours (no API key), so the tool can show it."""


class MouserRateLimited(MouserError):
    """Mouser refused for its own daily or per-minute limit (1,000 a day, 30 a minute)."""


class MouserKeySpent(MouserRateLimited):
    """Mouser refused one key for its daily limit while another key can still send: the request
    goes out again on that key (_fetch). The message is the refused key's own pause."""


class MouserAPIError(Exception):
    """Mouser API returned an error with a code and message."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"Mouser API error [{code}]: {message}")


# Pre-compiled patterns for parsing Mouser fields
_STOCK_RE = re.compile(r"(\d[\d,]*)\s+In Stock", re.IGNORECASE)
_PRICE_RE = re.compile(r"[^\d.]")


def _parse_stock(availability: str | None) -> int:
    """Parse stock from Mouser's 'Availability' field like '16563 In Stock'."""
    if not availability:
        return 0
    match = _STOCK_RE.search(availability)
    if match:
        return int(match.group(1).replace(",", ""))
    return 0


def _parse_price(price_str: str | None) -> float | None:
    """Parse price from Mouser's format like '$0.414' or '€0.350'."""
    if not price_str:
        return None
    cleaned = _PRICE_RE.sub("", price_str)
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def _parse_unit_weight_g(part: dict[str, Any]) -> float | None:
    """Mouser's UnitWeightKg.UnitWeight (kg) as grams; None when absent or not a positive number."""
    weight = part.get("UnitWeightKg")
    value = weight.get("UnitWeight") if isinstance(weight, dict) else None
    try:
        kg = float(value)
    except (TypeError, ValueError):
        return None
    return round(kg * 1000, 6) if kg > 0 else None


def _part_key(number: str | None) -> str:
    return re.sub(r"[^A-Z0-9]", "", (number or "").upper())


def _touches(result: dict[str, Any], number: str) -> bool:
    """Whether a result can be one of Mouser's loose matches for the number: its Mouser PN or MPN is
    the number or starts with it, or the number ends with its MPN (a Mouser PN such as 595-LM358P).
    Mouser matches loosely: "LM358P" finds LM358P and LM358PE4."""
    asked = _part_key(number)
    if not asked:
        return False
    mouser, mpn = _part_key(result.get("part_number")), _part_key(result.get("mfr_part_number"))
    return mouser.startswith(asked) or mpn.startswith(asked) or bool(mpn) and asked.endswith(mpn)


def _identifies(result: dict[str, Any], number: str) -> bool:
    """Whether the result is the number itself (its MPN or Mouser PN, compared with mpn_key)."""
    key = mpn_key(number)
    return bool(key) and key in (mpn_key(result.get("mfr_part_number") or ""), mpn_key(result.get("part_number") or ""))


def _not_found(numbers: list[str], results: list[dict[str, Any]]) -> list[str]:
    """The asked numbers no result matches (Mouser leaves out numbers it doesn't find)."""
    return [n for n in numbers if not any(_touches(r, n) for r in results)]


def _attribute(numbers: list[str], results: list[dict[str, Any]]
               ) -> tuple[dict[str, list[dict]], list[str | None], list[dict], set[str]]:
    """Match one request's results to the numbers asked (distinct by cache key).

    Returns each number's results (every result that can be its loose match), each result's owner
    (the one number it is, by mpn_key, else the only number it can match; None when that's unclear),
    the results that match no number (extras), and the clean numbers: those whose results all belong
    to them alone, which may be kept per part. A result that matches no number could belong to any,
    so then none is clean. One number owns everything Mouser returned for it.
    """
    if len(numbers) == 1:
        return {numbers[0]: list(results)}, [numbers[0]] * len(results), [], {numbers[0]}
    touched = [[n for n in numbers if _touches(r, n)] for r in results]
    owners: list[str | None] = []
    for result, matches in zip(results, touched):
        exact = [n for n in numbers if _identifies(result, n)]
        owners.append(exact[0] if len(exact) == 1 else matches[0] if not exact and len(matches) == 1 else None)
    per = {n: [r for r, matches in zip(results, touched) if n in matches] for n in numbers}
    extras = [r for r, matches in zip(results, touched) if not matches]
    clean = set() if extras else {
        n for n in numbers if all(owner == n for owner, matches in zip(owners, touched) if n in matches)}
    return per, owners, extras, clean


def _cache_key(number: str) -> str:
    """A part number's key in the answer store: as given, ignoring case and outer spaces."""
    return number.strip().upper()


@dataclass
class PartAnswer:
    """What Mouser returned for one part number: the results that can be its matches, whether any
    really matches it (else the reply's not_found names it), and when Mouser answered."""
    results: list[dict[str, Any]]
    matched: bool
    fetched_at: float

    def as_json(self) -> dict[str, Any]:
        return {"results": self.results, "matched": self.matched}

    @classmethod
    def from_json(cls, data: dict[str, Any], fetched_at: float) -> PartAnswer:
        return cls(list(data.get("results") or []), bool(data.get("matched")), fetched_at)


@dataclass
class _PoolBatch:
    """One-part lookups waiting to go out together (_pooled)."""
    caller: str | None
    future: asyncio.Future
    numbers: dict[str, str] = field(default_factory=dict)  # cache key -> the number as first given
    started: bool = False


def _normalize_part(part: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Mouser Part object into our standard format."""
    # Parse price breaks
    price_breaks = []
    for pb in part.get("PriceBreaks", []):
        price = _parse_price(pb.get("Price"))
        if price is not None:
            price_breaks.append({
                "qty": pb.get("Quantity", 0),
                "price": price,
                "currency": pb.get("Currency", "USD"),
            })

    unit_price = price_breaks[0]["price"] if price_breaks else None

    # Parse parameters
    parameters = {}
    for attr in part.get("ProductAttributes", []):
        name = attr.get("AttributeName")
        value = attr.get("AttributeValue")
        if name and value:
            parameters[name] = value

    stock = _parse_stock(part.get("Availability"))
    # Also check AvailabilityInStock for a more reliable numeric value
    avail_in_stock = part.get("AvailabilityInStock")
    if avail_in_stock:
        try:
            stock = int(str(avail_in_stock).replace(",", ""))
        except (ValueError, TypeError):
            pass

    # Mouser states a status for some parts only (Not Recommended for New Designs, End of Life, New
    # Product). None stated isn't "Active": AP2553W6-7 came back Active while Diodes and DigiKey list it NRND.
    lifecycle = None
    if part.get("LifecycleStatus"):
        lifecycle = part["LifecycleStatus"]
    elif part.get("IsDiscontinued") == "Yes":
        lifecycle = "Discontinued"

    return {
        "source": "mouser",
        "part_number": part.get("MouserPartNumber", ""),
        "mfr_part_number": part.get("ManufacturerPartNumber", ""),
        "manufacturer": part.get("Manufacturer", ""),
        "description": part.get("Description", ""),
        "category": part.get("Category", ""),
        "stock": stock,
        "price": unit_price,
        "price_breaks": price_breaks,
        "datasheet_url": part.get("DataSheetUrl"),
        "product_url": part.get("ProductDetailUrl"),
        "rohs": part.get("ROHSStatus", ""),
        "lifecycle": lifecycle,
        "lifecycle_status": mouser_status(lifecycle)[0],
        "parameters": parameters,
        "min_qty": int(part.get("Min", 1) or 1),
        "unit_weight_g": _parse_unit_weight_g(part),
        "currency": price_breaks[0]["currency"] if price_breaks else "USD",
    }


class MouserClient:
    """Async client for Mouser Search API v2.

    store: the answer and lifecycle store shared with DigiKeyClient and part_lifecycle (the server
    passes one); without one the client keeps its own in memory. pool_window: seconds a one-part
    lookup waits for others to share its request (sleep is injectable for tests). extra_keys:
    more API keys (MOUSER_API_KEY_2, ...), each used once the previous key's day is spent; quota
    then needs one DailyQuota per key (a MouserKeyPool). One DailyQuota is a pool of one key."""

    def __init__(self, api_key: str = MOUSER_API_KEY, quota: DailyQuota | QuotaPool | None = None,
                 store: DistributorStore | None = None, clock: Callable[[], float] = time.time,
                 pool_window: float = MOUSER_POOL_WINDOW, sleep: Callable[[float], Any] = asyncio.sleep,
                 extra_keys: Sequence[str] = ()):
        self._keys = [api_key, *extra_keys]
        self._client: httpx.AsyncClient | None = None
        self._quota = MouserKeyPool([quota]) if isinstance(quota, DailyQuota) else quota
        # Without a quota there's nothing to choose a key by: one key only
        if len(self._quota.quotas if self._quota is not None else [None]) != len(self._keys):
            raise ValueError("Each Mouser API key needs its own daily quota")
        self._owns_store = store is None
        self._store = DistributorStore(clock=clock) if store is None else store
        self._pool_window = pool_window
        self._sleep = sleep
        self._pool: _PoolBatch | None = None
        self._tasks: set[asyncio.Task] = set()  # pool sends in flight (kept so they aren't collected)
        self._waiting: set[asyncio.Future] = set()  # pooled batches not answered yet

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    def _redact(self, text: str) -> str:
        """Mouser's own error text goes back to callers and into logs: blank out every key in case
        Mouser echoes one."""
        for key in sorted({k for k in self._keys if k}, key=len, reverse=True):
            text = text.replace(key, "[redacted]")
        return text

    async def _post(self, path: str, body: dict[str, Any], key_index: int = 0) -> dict[str, Any]:
        """Make an authenticated POST request to Mouser API with the key the quota just reserved
        (no await between the reservation and the send).

        Note: Mouser API v2 requires apiKey as a query parameter (their design).
        """
        url = f"{MOUSER_BASE_URL}{path}?apiKey={self._keys[key_index]}"
        key_quota = self._quota.quotas[key_index] if self._quota is not None else None
        try:
            client = self._get_client()  # built first, so the minute counts from the send
            if self._quota is not None:
                self._quota.mark_sent()
            response = await client.post(url, json=body)
        except httpx.HTTPError:
            # Sanitize: httpx exceptions may include the full URL with API key
            raise MouserError("Mouser API request failed (network/connection error)")
        if key_quota is not None:
            # Only this key's: a daily count in the headers is that key's; a 429's per-minute
            # pause pauses every key anyway (QuotaPool._penalty)
            key_quota.note_response(response.status_code, response.headers)
        try:
            data = response.json()
        except ValueError:
            data = None
        errors = data.get("Errors") if isinstance(data, dict) else None
        errors = [e for e in errors if isinstance(e, dict)] if isinstance(errors, list) else []

        # Mouser reports its limits in the body, with HTTP 403 (seen by other projects in 2026):
        # {"Errors":[{"Code":"TooManyRequests","Message":"Maximum calls per day exceeded.",
        # "ResourceKey":"MaxCallPerDay"}]}, or "Maximum calls per minute exceeded." It sends no
        # rate-limit headers and doesn't say when the daily count resets.
        limit = next((e for e in errors if e.get("Code") == "TooManyRequests"), None)
        if limit is not None or response.status_code == 429:
            raise self._refused_for_limit(limit, key_index)
        if errors:
            err = errors[0]
            raise MouserAPIError(self._redact(str(err.get("Code") or "")),
                                 self._redact(str(err.get("Message") or "Unknown Mouser API error")))
        # Catch HTTP errors to avoid leaking the API key (embedded in URL) into logs
        if response.status_code >= 400:
            raise MouserError(f"Mouser API returned HTTP {response.status_code}")
        if not isinstance(data, dict):
            raise MouserError("Mouser API returned an unreadable response")
        if key_quota is not None:
            key_quota.clear_expired_pause()
        return data

    def _refused_for_limit(self, err: dict | None, key_index: int = 0) -> MouserRateLimited:
        """Pause for the limit Mouser named and return the error to raise. A daily refusal pauses
        only the key that got it (until 00:00 UTC, then hourly); while another key can send, that's
        MouserKeySpent, and the request goes out again on it. A per-minute refusal pauses every key
        (QuotaPool counts a "burst" pause on any key as the pool's)."""
        text = " ".join(str(err.get(key) or "") for key in ("Message", "ResourceKey")).lower() if err else ""
        if self._quota is not None:
            key_quota = self._quota.quotas[key_index]
            if "day" in text:
                key_quota.pause_daily_unknown_reset()
            elif err is not None:  # a TooManyRequests that isn't the daily limit: its per-minute one
                key_quota.pause(key_quota.now() + 60, "burst")
            # a bare 429 already paused for its Retry-After, or its day (note_response)
            paused = self._quota.paused_error()
            if paused:
                return MouserRateLimited(paused["error"])
            if own := key_quota.paused_error():  # only this key's day is over
                return MouserKeySpent(own["error"])
        detail = self._redact(str((err.get("Message") if err else None) or "HTTP 429"))
        return MouserRateLimited(f"Mouser is limiting requests ({detail}). Try again later.")

    async def get_part(self, part_number: str, caller: str | None = None) -> dict[str, Any]:
        """Look up part(s) by Mouser part number or MPN.

        Args:
            part_number: Mouser PN or MPN. Pipe-delimited for batch (up to 10).
            caller: the caller's IP, for the hourly log of who sent requests

        Returns:
            Dict with results list
        """
        # Mouser's SearchByPartRequest takes up to 10 part numbers, each 3-40 characters. Checked
        # here so a malformed batch doesn't spend a request.
        numbers = [n.strip() for n in part_number.split("|") if n.strip()]  # a stray "|" is a join slip
        if not numbers:
            return {"error": "Give at least one Mouser or manufacturer part number."}
        if len(numbers) > MOUSER_MAX_BATCH:
            return {"error": f"Mouser takes up to {MOUSER_MAX_BATCH} part numbers per call, separated by |; "
                             f"got {len(numbers)}. Split the batch."}
        bad = [n for n in numbers if not 3 <= len(n) <= 40]
        if bad:
            return {"error": "Each Mouser part number must be 3-40 characters: "
                             + ", ".join(repr(n[:50]) for n in bad[:3])}
        distinct: dict[str, str] = {}
        for number in numbers:  # once each, as first spelled
            distinct.setdefault(_cache_key(number), number)
        numbers = list(distinct.values())

        answers, extras, error = await self._answers(numbers, caller)
        if error is not None:
            return error
        results: list[dict[str, Any]] = []
        seen = set()
        for result in [r for n in numbers for r in answers[_cache_key(n)].results] + extras:
            identity = (result.get("part_number"), result.get("mfr_part_number"), result.get("manufacturer"))
            if identity not in seen:
                seen.add(identity)
                results.append(result)
        reply: dict[str, Any] = {"results": results, "total": len(results)}
        # Mouser leaves out numbers it doesn't find, so in a batch of 10 a missing part looked checked
        if missing := [n for n in numbers if not answers[_cache_key(n)].matched]:
            reply["not_found"] = missing
        # The oldest answer used: parts fetched by other calls can be up to MOUSER_CACHE_TTL old
        reply["observed_at"] = utc_text(min(answer.fetched_at for answer in answers.values()))
        return reply

    async def lookup(self, numbers: list[str], caller: str | None = None
                     ) -> tuple[dict[str, PartAnswer] | None, dict[str, Any] | None]:
        """Each number's answer, as get_part finds it (store first, then one request for the rest),
        or a limit error. numbers: up to 10 distinct numbers of 3-40 characters (part_lifecycle)."""
        answers, _, error = await self._answers(numbers, caller)
        if error is not None:
            return None, error
        return {n: answers[_cache_key(n)] for n in numbers}, None

    def retry_after(self) -> int:
        """Seconds until Mouser may be asked again (60 when the limits don't say)."""
        return (self._quota.retry_after() if self._quota else None) or 60

    async def _answers(self, numbers: list[str], caller: str | None
                       ) -> tuple[dict[str, PartAnswer], list[dict[str, Any]], dict[str, Any] | None]:
        """Answers by cache key from the store, then from Mouser for the numbers it doesn't have:
        one request (a lone number waits to share it, _pooled). Also the results matching no number
        asked (they're returned to the caller, not kept per part), or a limit error."""
        stats.usage.record_parts_asked("mouser", numbers)
        answers: dict[str, PartAnswer] = {}
        missing = []
        for number in numbers:
            stored = self._store.get_answer("mouser", _cache_key(number))
            if stored is not None:
                answers[_cache_key(number)] = PartAnswer.from_json(*stored)
            else:
                missing.append(number)
        extras: list[dict[str, Any]] = []
        # A batch kept whole (its numbers couldn't all be kept one by one): this call's numbers, or
        # the ones it still needs, sent together before
        for key in dict.fromkeys((_batch_key(numbers), _batch_key(missing))) if missing and len(numbers) > 1 else ():
            if (stored := self._store.get_answer("mouser", key)) is None:
                continue
            batch, fetched_at = stored
            try:
                kept = {_cache_key(n): PartAnswer.from_json(batch["answers"][_cache_key(n)], fetched_at) for n in missing}
            except (KeyError, TypeError, AttributeError):  # not expected: ask Mouser again
                continue
            # The batch lives as long as a found answer; a part it didn't find is good for a day only
            if self._store.now() - fetched_at >= MOUSER_NOT_FOUND_TTL and any(not a.results for a in kept.values()):
                continue
            answers.update(kept)
            extras = list(batch.get("extras") or [])
            missing = []
            break
        if not missing:
            stats.usage.record_distributor("mouser", "cached")
            return answers, extras, None
        if len(missing) == 1:
            fresh, more, error = await self._pooled(missing[0], caller)
        else:
            fresh, more, error = await self._fetch(missing, caller)
        if error is not None:
            return {}, [], error
        answers.update(fresh)
        return answers, extras + more, None

    async def _fetch(self, numbers: list[str], caller: str | None, pooled: bool = False
                     ) -> tuple[dict[str, PartAnswer], list[dict[str, Any]], dict[str, Any] | None]:
        """One request for these numbers (distinct by cache key). Keeps each clean number's answer,
        or, for a caller's own batch with an unclear result, the batch under its joined numbers
        (a pooled request's numbers come from different calls, so that key would never be asked
        again); and every result's lifecycle that can be put down to one number."""
        body = {
            "SearchByPartRequest": {
                "mouserPartNumber": "|".join(numbers),
                "partSearchOptions": "None",
            }
        }
        # Each attempt reserves a request on the key it will use (after the store, so stored
        # answers don't count) and sends it with no await in between, so concurrent lookups can't
        # overdraw a key. One more attempt, on the next key, only after a daily refusal (the refused
        # key stays out for the day): at most as many requests as there are keys.
        for attempt in range(len(self._keys)):
            key_index = 0
            if self._quota:
                key_index, quota_error = self._quota.acquire(caller)
                if quota_error:
                    stats.usage.record_distributor("mouser", "rate_limited")
                    return {}, [], quota_error
            stats.usage.record_distributor("mouser", "sent")
            try:
                data = await self._post("/search/partnumber", body, key_index)
            except MouserKeySpent as e:
                if attempt + 1 < len(self._keys):
                    continue
                return {}, [], {"error": str(e)}
            except MouserRateLimited as e:
                return {}, [], {"error": str(e)}
            break
        fetched_at = self._store.now()
        parts = (data.get("SearchResults") or {}).get("Parts") or []
        results = [_normalize_part(p) for p in parts if isinstance(p, dict)]

        per, owners, extras, clean = _attribute(numbers, results)
        answers = {}
        for number in numbers:
            answer = PartAnswer(per[number], any(_touches(r, number) for r in per[number]), fetched_at)
            answers[_cache_key(number)] = answer
            if number in clean:
                self._store.put_answer("mouser", _cache_key(number), answer.as_json(), bool(answer.results), fetched_at)
        if len(numbers) > 1 and not pooled and len(clean) < len(numbers):
            self._store.put_answer("mouser", _batch_key(numbers), {
                "answers": {key: answer.as_json() for key, answer in answers.items()}, "extras": extras,
            }, bool(results), fetched_at)

        readings = [Reading(r["mfr_part_number"], r.get("manufacturer") or "", "mouser", r["lifecycle_status"],
                            r.get("lifecycle") or MOUSER_NOT_STATED, fetched_at)
                    for r, owner in zip(results, owners) if owner is not None and r.get("mfr_part_number")]
        self._store.put_readings(readings)
        for number in clean:
            if not any(_identifies(r, number) for r in per[number]):
                self._store.put_not_listed(number, "mouser", fetched_at)
        return answers, extras, None

    async def _pooled(self, number: str, caller: str | None
                      ) -> tuple[dict[str, PartAnswer], list[dict[str, Any]], dict[str, Any] | None]:
        """One number's answer from a request shared with other one-part lookups that start within
        pool_window (up to 10 numbers; a full batch goes at once). A result matching none of the
        numbers goes back only to lookups whose number nothing matched."""
        key = _cache_key(number)
        batch = self._pool
        if batch is None or (key not in batch.numbers and len(batch.numbers) >= MOUSER_MAX_BATCH):
            batch = self._pool = _PoolBatch(caller, asyncio.get_running_loop().create_future())
            batch.future.add_done_callback(_consume_exception)
            self._waiting.add(batch.future)
            batch.future.add_done_callback(self._waiting.discard)
            self._spawn(self._send_after_window(batch))
        batch.numbers.setdefault(key, number)
        if len(batch.numbers) >= MOUSER_MAX_BATCH and not batch.started:
            self._spawn(self._send(batch))  # full: no need to wait (the window's end then sends nothing)
        # shield: one caller giving up (a cancelled tool call) mustn't cancel the others' request
        answers, extras, error = await asyncio.shield(batch.future)
        if error is not None:
            return {}, [], error
        answer = answers[key]
        return {key: answer}, (extras if not answer.matched else []), None

    def _spawn(self, coro) -> asyncio.Task:
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def _send_after_window(self, batch: _PoolBatch) -> None:
        try:
            await self._sleep(self._pool_window)
        except asyncio.CancelledError:  # close(): nothing will send this batch now
            if self._pool is batch:
                self._pool = None
            if not batch.started and not batch.future.done():
                batch.future.cancel()
            raise
        await self._send(batch)

    async def _send(self, batch: _PoolBatch) -> None:
        if batch.started:
            return
        batch.started = True
        if self._pool is batch:
            self._pool = None  # later lookups start a new batch
        try:
            result = await self._fetch(list(batch.numbers.values()), batch.caller, pooled=len(batch.numbers) > 1)
        except asyncio.CancelledError:
            if not batch.future.done():
                batch.future.cancel()
            raise
        except Exception as e:  # each waiting lookup raises it, as its own request would have
            if not batch.future.done():
                batch.future.set_exception(e)
        else:
            if not batch.future.done():
                batch.future.set_result(result)

    async def close(self) -> None:
        """Close the HTTP client (and the store, if this client made its own). Lookups still waiting
        for a pooled request are cancelled (a task cancelled before it starts can't do that itself)."""
        self._pool = None
        for future in list(self._waiting):
            future.cancel()
        for task in list(self._tasks):
            task.cancel()
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._owns_store:
            self._store.close()


def _batch_key(numbers: list[str]) -> str:
    """A batch's key in the answer store, for numbers that couldn't be kept one by one."""
    return "batch:" + "|".join(_cache_key(n) for n in numbers)


def _consume_exception(future: asyncio.Future) -> None:
    """Mark a pooled request's exception as seen, so it isn't logged when every waiter gave up."""
    if not future.cancelled():
        future.exception()
