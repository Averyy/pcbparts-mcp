"""Mouser Search API v2 client.

Answers are kept per part number in distributor_store.py for MOUSER_CACHE_TTL, a miss for
MOUSER_NOT_FOUND_TTL (3 days each), so a batch reuses parts other calls fetched and sends only the
rest. Mouser matches loosely and doesn't say which part number each result is for, so results are
matched back to the numbers asked (_attribute): a number whose results can't all be put down to it
alone isn't kept on its own, and the whole batch is kept under its joined numbers instead. Every
answer's lifecycle goes into the lifecycle store.

Mouser sends at most 50 results a request (MOUSER_MAX_RESULTS), however many match, so a broad number
can crowd the others out of a batch ("LM358|TPS54331DR" can come back as 50 LM358 parts). A reply cut
at that cap keeps no "not found" or "not listed" for any number, and the numbers it crowded out are
asked once more without the number that filled it (_crowded_out).

Each request picks its API key as it goes out (Mouser takes the key in the query string): stay on the
current key until Mouser refuses its day, then the next in rotation (MouserKeyPool). A daily refusal moves the
request on to the next key, and so does Mouser rejecting a key as invalid when there are several
(that key then waits for the next Mouser day, and the log names its number).

Numbers neither distributor can list (search/mpn.py's not_sent_reason: a value such as "10k", a BOM
placeholder, an LCSC code, non-ASCII) aren't sent: get_part lists them in not_found and not_sent.
When Mouser rejects a request of several numbers, each is asked alone once, so one number it
can't take doesn't fail the others (_one_by_one).
"""

from __future__ import annotations

import asyncio
import logging
import math
import re
import time
from collections.abc import Awaitable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

import httpx

from . import stats
from .cache import DailyQuota, MouserKeyPool, QuotaPool, RetryGuard, _header_int, _utc_text, retry_after_seconds
from .config import (
    MOUSER_API_KEY,
    MOUSER_BASE_URL,
    MOUSER_NOT_FOUND_TTL,
)
from .distributor_store import DistributorStore
from .lifecycle import MOUSER_NOT_STATED, Reading, maker_key, mouser_status, utc_text
from .search.mpn import distributor_match, mpn_key, not_sent_reason, same_jst_part

logger = logging.getLogger(__name__)


class _RedactApiKey(logging.Filter):
    """httpx logs each request's URL at INFO, and Mouser takes the API key in the query string: blank
    it in any such line, whatever level the httpx loggers are set to."""

    _KEY = re.compile(r"(apiKey=)[^&\s\"']+", re.IGNORECASE)

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # a malformed record: leave it to logging's own handling
            return True
        if "apikey=" in message.casefold():
            record.msg, record.args = self._KEY.sub(r"\1[redacted]", message), None
        return True


# The server sets the root logger to WARNING, but a self-hoster's logging setup may not: keep the
# request lines (and any key in them) out of the log either way
for _name in ("httpx", "httpcore"):
    logging.getLogger(_name).setLevel(logging.WARNING)
    logging.getLogger(_name).addFilter(_RedactApiKey())


MOUSER_MAX_BATCH = 10  # part numbers per SearchByPartRequest (Mouser's API docs)
MOUSER_MAX_RESULTS = 50  # parts in one SearchByPartRequest reply at most, however many match


class MouserError(ValueError):
    """A Mouser request failed. The message is ours (no API key), so the tool can show it."""


class _TransientFailure(MouserError):
    """Internal retry signal carrying diagnostics, with the existing public failure message."""

    def __init__(self, message: str, response: httpx.Response | None = None, *,
                 exception_name: str | None = None, json_parsed: bool = False, json_keys: tuple = ()):
        super().__init__(message)
        self.response = response
        self.exception_name = exception_name
        self.json_parsed = json_parsed
        self.json_keys = json_keys


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


class MouserKeyRejected(MouserAPIError):
    """Mouser rejected the only API key as invalid: nothing else can send, so the error is shown as
    Mouser gave it (a self-hoster's typo), and asking each number alone wouldn't help."""


def _daily_limit(error: dict | None, headers: Any) -> bool:
    text = " ".join(str(error.get(key) or "") for key in ("Message", "ResourceKey")).lower() if error else ""
    # A bare 429 whose headers say none are left is the day too.
    return "day" in text or (error is None and _header_int(headers or {}, "x-ratelimit-remaining") == 0)


def _rejects_key(error: dict[str, Any]) -> bool:
    """Whether a Mouser error rejects the API key itself ("Invalid unique identifier.", for the
    property "API Key"), not the request."""
    text = " ".join(str(error.get(k) or "") for k in ("Code", "Message", "ResourceKey", "PropertyName")).casefold()
    return "invalid unique identifier" in text or "invalididentifier" in text or (
        "invalid" in text and ("api key" in text or "apikey" in text))


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
    the number or starts with it, the number ends with its MPN (a Mouser PN such as 595-LM358P), or
    it's the JST part the number names with or without (LF)/(SN) (_same_jst). Mouser matches
    loosely: "LM358P" finds LM358P and LM358PE4."""
    asked = _part_key(number)
    if not asked:
        return False
    mouser, mpn = _part_key(result.get("part_number")), _part_key(result.get("mfr_part_number"))
    return (mouser.startswith(asked) or mpn.startswith(asked) or bool(mpn) and asked.endswith(mpn)
            or _same_jst(result, number))


def _same_jst(result: dict[str, Any], number: str) -> bool:
    """Whether the result is the JST part the number names once JST's (LF)/(SN) endings are set
    aside (B2B-PH-K-S for B2B-PH-K-S(LF)(SN)), as digikey_get_part and matched_by "packing" decide."""
    return same_jst_part(result.get("mfr_part_number") or "", number, result.get("manufacturer") or "")


def _identifies(result: dict[str, Any], number: str, finish: bool = True) -> bool:
    """Whether the result is the number itself: its MPN or Mouser PN, compared with mpn_key, or
    (finish=True) the JST part it names apart from the (LF)/(SN) endings."""
    key = mpn_key(number)
    listed = (mpn_key(result.get("mfr_part_number") or ""), mpn_key(result.get("part_number") or ""))
    return (bool(key) and key in listed) or (finish and _same_jst(result, number))


def _not_found(numbers: list[str], results: list[dict[str, Any]]) -> list[str]:
    """The asked numbers no result matches (Mouser leaves out numbers it doesn't find)."""
    return [n for n in numbers if not any(_touches(r, n) for r in results)]


def _capped(data: dict[str, Any], parts: list[Any]) -> bool:
    """Whether a reply was cut at Mouser's result cap: MOUSER_MAX_RESULTS parts, or a NumberOfResult
    above the parts it sent. Numbers without a match in it may only have been crowded out."""
    total = (data.get("SearchResults") or {}).get("NumberOfResult")
    try:
        total = int(total)
    except (TypeError, ValueError):
        total = None
    return len(parts) >= MOUSER_MAX_RESULTS or (total is not None and total > len(parts))


def _crowded_out(numbers: list[str], per: dict[str, list[dict]]) -> list[str]:
    """In a reply cut at the cap, the numbers to ask again: those without a result that is the
    number itself (_identifies), apart from the number(s) with the most results, which filled the
    reply (asked again, they'd fill it again). [] for a single number (nothing crowded it) or when
    no number has a result (the same request would come back the same)."""
    most = max((len(results) for results in per.values()), default=0)
    if len(numbers) < 2 or not most:
        return []
    return [n for n in numbers if len(per[n]) < most and not any(_identifies(r, n) for r in per[n])]


def _attribute(numbers: list[str], results: list[dict[str, Any]]
               ) -> tuple[dict[str, list[dict]], list[str | None], list[dict], set[str]]:
    """Match one request's results to the numbers asked (distinct by cache key).

    Returns each number's results (every result that can be its loose match), each result's owner
    (the number it is, by mpn_key: the first, when several are; else the only number it can match;
    None when that's unclear),
    the results that match no number (extras), and the clean numbers: those whose results all belong
    to them alone, which may be kept per part. A result that matches no number could belong to any,
    so then none is clean. One number owns everything Mouser returned for it.
    """
    if len(numbers) == 1:
        return {numbers[0]: list(results)}, [numbers[0]] * len(results), [], {numbers[0]}
    touched = [[n for n in numbers if _touches(r, n)] for r in results]
    owners: list[str | None] = []
    for result, matches in zip(results, touched):
        # The number spelled as listed wins over one that differs by JST's (LF)/(SN) endings. Several
        # numbers that are each the part itself (595-LM358P and LM358P, or LM358P and LM358-P: one
        # part asked twice) give it to the first of them
        exact = [n for n in numbers if _identifies(result, n, finish=False)] or [n for n in numbers if _identifies(result, n)]
        owners.append(exact[0] if exact else matches[0] if len(matches) == 1 else None)
    per = {n: [r for r, matches in zip(results, touched) if n in matches] for n in numbers}
    extras = [r for r, matches in zip(results, touched) if not matches]
    clean = set() if extras else {
        n for n in numbers if all(owner == n for owner, matches in zip(owners, touched) if n in matches)}
    return per, owners, extras, clean


def _answering(result: dict[str, Any], number: str | None) -> dict[str, Any]:
    """The result with requested (the number it answers, None when it can't be put down to one of
    the numbers asked) and matched_by (search/mpn.py's distributor_match; None with no number).
    Added to each reply, not kept: kept answers serve every spelling and batch."""
    matched = None if number is None else distributor_match(
        number, result.get("mfr_part_number") or "", result.get("manufacturer") or "",
        [result.get("part_number") or ""], "mouser_pn")
    return {**result, "requested": number, "matched_by": matched}


def _cache_key(number: str) -> str:
    """A part number's key in the answer store: as given, ignoring case and outer spaces."""
    return number.strip().upper()


@dataclass
class PartAnswer:
    """What Mouser returned for one part number: the results that can be its matches, whether any
    really matches it (else the reply's not_found names it), and when Mouser answered. checked is
    False for a number a reply cut at Mouser's cap may have crowded out (no results for it, or none
    that is the part itself while another number filled the reply), even after a follow-up (_fetch):
    Mouser may list it. Such answers are never kept, so a kept answer is always checked.
    problem: the limit error or exception that prevented a follow-up or one-by-one request from
    answering this number. Without a problem, unmatched numbers still go in get_part's not_found."""
    results: list[dict[str, Any]]
    matched: bool
    fetched_at: float
    checked: bool = True
    problem: dict[str, Any] | Exception | None = None

    def as_json(self) -> dict[str, Any]:
        return {"results": self.results, "matched": self.matched}

    @classmethod
    def from_json(cls, data: dict[str, Any], fetched_at: float) -> PartAnswer:
        return cls(list(data.get("results") or []), bool(data.get("matched")), fetched_at)


@dataclass
class _WaitBudget:
    """Waiting spent by all requests in one lookup, capped at 30 seconds."""

    waited: float = 0


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
    elif part.get("IsDiscontinued") is True or str(part.get("IsDiscontinued") or "").strip().casefold() in ("yes", "true"):
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
    passes one); without one the client keeps its own in memory. extra_keys: more API keys
    (MOUSER_API_KEY_2, ...), each used once Mouser refuses the previous key's day; quota then needs one
    DailyQuota per key (a MouserKeyPool). One DailyQuota is a pool of one key."""

    def __init__(self, api_key: str = MOUSER_API_KEY, quota: DailyQuota | QuotaPool | None = None,
                 store: DistributorStore | None = None, clock: Callable[[], float] = time.time,
                 extra_keys: Sequence[str] = (), sleep: Callable[[float], Awaitable[None]] = asyncio.sleep):
        self._keys = [api_key, *extra_keys]
        self._clock, self._sleep = clock, sleep
        self._guard = RetryGuard("Mouser", clock, logger)  # retries off during an outage
        self._failure_minute: int | None = None
        self._suppressed_failures = 0
        self._client: httpx.AsyncClient | None = None
        self._closed = False  # close(): nothing goes out afterwards
        self._quota = MouserKeyPool([quota]) if isinstance(quota, DailyQuota) else quota
        # Without a quota there's nothing to choose a key by: one key only
        if len(self._quota.quotas if self._quota is not None else [None]) != len(self._keys):
            raise ValueError("Each Mouser API key needs its own daily quota")
        self._owns_store = store is None
        self._store = DistributorStore(clock=clock) if store is None else store
        self._tasks: set[asyncio.Task] = set()  # requests in flight (_shielded; kept so they aren't collected)

    def _get_client(self) -> httpx.AsyncClient:
        if self._closed:  # shutting down: nothing goes out after close()
            raise MouserError("Mouser API request failed (network/connection error)")
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
        client = self._get_client()  # a closed client is not an upstream attempt
        rotation = self._quota if isinstance(self._quota, MouserKeyPool) else None
        token = rotation.sent(key_index) if rotation is not None else None
        try:
            data = await self._send(client, path, body, key_index, token)
        except _TransientFailure:
            self._record_outcome(transient=True)
            raise
        except (MouserError, MouserAPIError):
            self._record_outcome(transient=False)
            raise
        else:
            self._record_outcome(transient=False)
            return data
        finally:
            if rotation is not None and token is not None:
                rotation.finished(key_index, token)

    async def _send(self, client: httpx.AsyncClient, path: str, body: dict[str, Any], key_index: int,
                    token: tuple[float, float | None, bool] | None) -> dict[str, Any]:
        url = f"{MOUSER_BASE_URL}{path}?apiKey={self._keys[key_index]}"
        key_quota = self._quota.quotas[key_index] if self._quota is not None else None
        rotation = self._quota if isinstance(self._quota, MouserKeyPool) else None
        sent_count = key_quota._count if key_quota is not None else None
        try:
            if self._quota is not None:
                self._quota.mark_sent()
            response = await client.post(url, json=body)
        except (Exception, asyncio.CancelledError) as exc:
            stats.count_upstream_status("mouser", exc)
            # Sanitize: httpx exceptions may include the full URL with API key
            if isinstance(exc, httpx.HTTPError):
                message = "Mouser API request failed (network/connection error)"
                if isinstance(exc, httpx.TransportError) and not isinstance(exc, httpx.TimeoutException):
                    raise _TransientFailure(message, exception_name=type(exc).__name__) from None
                raise MouserError(message) from None
            raise
        json_parsed = True
        try:
            data = response.json()
        except (ValueError, RecursionError):  # RecursionError: absurdly nested JSON
            data = None
            json_parsed = False
        errors = data.get("Errors") if isinstance(data, dict) else None
        errors = [e for e in errors if isinstance(e, dict)] if isinstance(errors, list) else []

        # Mouser reports its limits in the body, with HTTP 403 (seen by other projects in 2026):
        # {"Errors":[{"Code":"TooManyRequests","Message":"Maximum calls per day exceeded.",
        # "ResourceKey":"MaxCallPerDay"}]}, or "Maximum calls per minute exceeded." It sends no
        # rate-limit headers; the configured Mouser day supplies the expected reset time.
        limit = next((e for e in errors if e.get("Code") == "TooManyRequests"), None)
        stats.count_upstream_status("mouser", response, status="429" if limit is not None else None)
        if rotation is not None and token is not None:
            # Readable request/part errors also confirm that the API accepted the check.
            rejected = any(_rejects_key(e) for e in errors)
            refused = limit is not None or response.status_code in (401, 403, 429) or rejected
            results = data.get("SearchResults") if isinstance(data, dict) else None
            readable = bool(errors) or (isinstance(results, dict) and isinstance(results.get("Parts"), list))
            if not refused and response.status_code < 400 and readable:
                resumed = rotation.finished(key_index, token, accepted=True)
                if resumed:
                    logger.info(f"Mouser key {key_index + 1} accepted again at {utc_text(resumed['resumed_at'])}; "
                                f"daily refusal since {utc_text(resumed['at'])}, after {resumed['retries']} retries")
        if key_quota is not None:
            if rotation is not None:
                # Mouser currently sends no quota headers. If present, retain the counters as
                # telemetry; refusal handling below owns the next try time.
                remaining = _header_int(response.headers, "x-ratelimit-remaining")
                if remaining is not None:
                    key_quota.note_api_usage(remaining, _header_int(response.headers, "x-ratelimit-limit"))
            else:
                key_quota.note_response(200 if limit is not None else response.status_code, response.headers)
        unexplained_check = (token is not None and token[2]
                             and response.status_code in (401, 403) and limit is None and not rejected)
        if limit is not None or response.status_code == 429 or unexplained_check:
            raise self._refused_for_limit(limit, key_index, response.headers, token=token,
                                          sent_count=sent_count, unexplained=unexplained_check)
        if errors:
            err = errors[0]
            code = self._redact(str(err.get("Code") or ""))
            message = self._redact(str(err.get("Message") or "Unknown Mouser API error"))
            if _rejects_key(err) and self._quota is not None:
                raise self._key_rejected(key_index, code, message)
            raise MouserAPIError(code, message)
        # Catch HTTP errors to avoid leaking the API key (embedded in URL) into logs
        if response.status_code >= 400:
            if 500 <= response.status_code < 600:
                raise _TransientFailure(f"Mouser API returned HTTP {response.status_code}", response)
            raise MouserError(f"Mouser API returned HTTP {response.status_code}")
        # A reply without its parts list says nothing about the numbers: never keep a miss.
        results = data.get("SearchResults") if isinstance(data, dict) else None
        if not isinstance(results, dict) or not isinstance(results.get("Parts"), list):
            raise _TransientFailure("Mouser API returned an unreadable response", response,
                                    json_parsed=json_parsed, json_keys=tuple(data) if isinstance(data, dict) else ())
        if key_quota is not None and rotation is None:
            if resumed := key_quota.clear_expired_pause():
                logger.info(f"Mouser key {key_index + 1} accepted again at {utc_text(resumed['resumed_at'])}; "
                            f"daily refusal since {utc_text(resumed['at'])}, after {resumed['retries']} retries")
        return data

    def _record_outcome(self, *, transient: bool) -> None:
        self._guard.record(transient=transient)

    def _retries_disabled(self) -> bool:
        """RetryGuard: off while 90% of at least 10 attempts in five minutes failed transiently."""
        return self._guard.disabled()

    def _retry_delay(self, failure: _TransientFailure, retries: int, waited: float) -> float | None:
        if self._retries_disabled() or retries >= 2 or waited >= 30:
            return None
        delay: float = (3, 10)[retries]
        response = failure.response
        if response is not None and 500 <= response.status_code < 600:
            after = retry_after_seconds(response.headers, self._clock())
            if after is not None:  # unusable: our normal delay
                # whole seconds stay whole, so the log reads delay=5 (and 0), as before
                delay = int(after) if math.isfinite(after) and after == int(after) else after
        return delay if waited + delay <= 30 else None

    def _log_transient(self, failure: _TransientFailure, attempt: int, key_index: int,
                       delay: float | None) -> None:
        """One diagnostic per UTC minute; later failures are counted for the next line."""
        minute = int(self._clock() // 60)
        if minute == self._failure_minute:
            self._suppressed_failures += 1
            return
        more = ""
        if self._suppressed_failures:
            since = datetime.fromtimestamp(self._failure_minute * 60, timezone.utc).strftime("%H:%M")
            more = f"; {self._suppressed_failures} more since {since} UTC"
        self._failure_minute, self._suppressed_failures = minute, 0
        response = failure.response
        detail = failure.exception_name
        if response is not None:
            detail = f"HTTP {response.status_code}"
        headers = response.headers if response is not None else {}
        detail += (f" attempt={attempt} key={key_index + 1} retry={delay is not None} delay={delay}"
                   f" Retry-After={self._redact(repr(headers.get('Retry-After')))}"
                   f" Server={self._redact(repr(headers.get('Server')))}"
                   f" Content-Type={self._redact(repr(headers.get('Content-Type')))}"
                   f" body_length={len(response.content) if response is not None else 0}")
        if response is not None and 500 <= response.status_code < 600:
            body = " ".join(self._redact(response.text).split())[:200]
            detail += f" body={body!r}"
        elif response is not None:
            detail += f" json={failure.json_parsed} top_keys={self._redact(repr(failure.json_keys))}"
        logger.warning("Mouser transient failure: %s%s", detail, more)

    def _refused_for_limit(self, err: dict | None, key_index: int = 0, headers: Any = None,
                           token: tuple[float, float | None, bool] | None = None,
                           sent_count: int | None = None, unexplained: bool = False) -> MouserRateLimited:
        """Pause a daily refusal until its next try and rotate; minute refusals pause every key."""
        daily = unexplained or _daily_limit(err, headers)
        stats.count_distributor_limit("mouser", "refusals", "refused" if unexplained else "daily" if daily else "minute")
        if self._quota is not None:
            key_quota = self._quota.quotas[key_index]
            if daily:
                if isinstance(self._quota, MouserKeyPool):
                    assert token is not None and sent_count is not None
                    if self._quota.refuse_daily(key_index, token, sent_count):
                        logger.warning(f"Mouser key {key_index + 1} daily refusal at {utc_text(key_quota.now())}: "
                                       f"our count {sent_count}/{key_quota._limit}; "
                                       f"next try at {_utc_text(key_quota._paused_until)}")
                else:
                    key_quota.pause_daily_unknown_reset()
            elif err is not None or _header_int(headers or {}, "x-ratelimit-remaining") != 0:
                wait = 60 if err is not None else (_header_int(headers or {}, "retry-after") or 60)
                self._quota.share_penalty(key_quota.now() + wait, "burst")
            paused = self._quota.paused_error()
            if paused:
                return MouserRateLimited(paused["error"])
            if daily:  # only this key's day is over; retry even for a stale in-flight refusal
                return MouserKeySpent(self._quota.daily_error()["error"])
            if own := key_quota.paused_error():
                return MouserKeySpent(own["error"])
        detail = self._redact(str((err.get("Message") if err else None) or "HTTP 429"))
        return MouserRateLimited(f"Mouser is limiting requests ({detail}). Try again later.")

    def _key_rejected(self, key_index: int, code: str, message: str) -> Exception:
        """Mouser rejected this key as invalid (a typo, or revoked). With several keys it waits for
        the next Mouser day, the log names its number (never the key), and the request goes out again
        on the next key (MouserKeySpent), or gets the pool's daily error when none is left. The
        only key's rejection is shown as Mouser gave it."""
        if len(self._keys) == 1:
            return MouserKeyRejected(code, message)
        key_quota = self._quota.quotas[key_index]
        until = key_quota.next_reset()
        key_quota.pause(until, "invalid_key")
        logger.error(f"Mouser rejected API key {key_index + 1} as invalid ({message}); it isn't used again "
                     f"until {utc_text(until)}: check MOUSER_API_KEY" + (f"_{key_index + 1}" if key_index else ""))
        if paused := self._quota.paused_error():
            return MouserRateLimited(paused["error"])
        return MouserKeySpent(self._quota.daily_error()["error"])

    async def get_part(self, part_number: str, caller: str | None = None) -> dict[str, Any]:
        """Look up part(s) by Mouser part number or MPN.

        Args:
            part_number: Mouser PN or MPN. Pipe-delimited for batch (up to 10).
            caller: the caller's IP, for the hourly log of who sent requests

        Returns:
            Dict with results list. Numbers not worth a request (not_sent_reason) are in not_found
            and not_sent. When a limit holds back the request for some numbers while others were
            kept, the kept answers come back with not_checked (the numbers not looked up) and
            retry_after; with nothing kept, the limit error. lookup_failed: numbers Mouser gave an
            error for when asked alone, or unmatched numbers whose follow-up after a capped reply
            failed (the others still answer).
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
        not_sent = {n: reason for n in numbers if (reason := not_sent_reason(n))}
        for _ in not_sent:
            stats.count_distributor("mouser", "skipped")
        sent = [n for n in numbers if n not in not_sent]

        answers: dict[str, PartAnswer] = {}
        extras: list[dict[str, Any]] = []
        error = None
        if sent:
            answers, extras, error = await self._answers(sent, caller)
        checked = {key: answer for key, answer in answers.items() if answer.problem is None}
        limited = [n for n in sent if _cache_key(n) not in answers or isinstance(answers[_cache_key(n)].problem, dict)]
        failed = [n for n in sent if isinstance(getattr(answers.get(_cache_key(n)), "problem", None), Exception)]
        # A limit held back the numbers not kept: with none kept, the limit error as before
        if limited and not checked and not failed:
            return error or answers[_cache_key(limited[0])].problem
        if failed and not checked and not limited:  # Mouser rejected every number: its error, as before
            raise answers[_cache_key(failed[0])].problem
        results: list[dict[str, Any]] = []
        seen = set()
        unowned = set()  # results matching no number their request asked (extras)
        for result, extra in [(r, False) for n in sent if _cache_key(n) in checked for r in checked[_cache_key(n)].results] \
                + [(r, True) for r in extras]:
            identity = (result.get("part_number"), result.get("mfr_part_number"), result.get("manufacturer"))
            if identity not in seen:
                seen.add(identity)
                results.append(result)
                if extra:
                    unowned.add(identity)
        # Which number each result answers, as this caller spelled it, and how: the owner the
        # answers were kept by (_attribute), worked out again over this call's numbers. A result
        # that matched none of its request's numbers answers none, though it may match one of this
        # call's kept from another request.
        answered = [n for n in sent if _cache_key(n) in checked]
        owners = _attribute(answered, results)[1] if answered else [None] * len(results)
        results = [_answering(result, None if (result.get("part_number"), result.get("mfr_part_number"),
                                                result.get("manufacturer")) in unowned else owner)
                   for result, owner in zip(results, owners)]
        reply: dict[str, Any] = {"results": results, "total": len(results)}
        # Mouser leaves out numbers it doesn't find, so in a batch of 10 a missing part looked checked
        if missing := [n for n in numbers if n in not_sent or (_cache_key(n) in checked and not checked[_cache_key(n)].matched)]:
            reply["not_found"] = missing
        if not_sent:
            reply["not_sent"] = not_sent
        if limited:
            reply["not_checked"] = limited
            reply["retry_after"] = self.retry_after(caller)
        if failed:
            reply["lookup_failed"] = failed
        # The oldest answer used: parts fetched by other calls can be up to MOUSER_CACHE_TTL old
        reply["observed_at"] = utc_text(min((answer.fetched_at for answer in checked.values()), default=self._store.now()))
        return reply

    async def lookup(self, numbers: list[str], caller: str | None = None
                     ) -> tuple[dict[str, PartAnswer], dict[str, Any] | None]:
        """Each number's answer, as get_part finds it (store first, then a request for the rest; see
        PartAnswer.checked and problem), and a limit error when one held back the numbers that have
        no answer in it. numbers: up to 10 distinct numbers of 3-40 characters (part_lifecycle). A
        number no distributor can list (not_sent_reason: a value such as "10k", an LCSC code...) is
        never sent and has no answer, as in get_part: callers leave those out, so one here is a bug."""
        if refused := [n for n in numbers if not_sent_reason(n)]:
            logger.error(f"Mouser lookup: {len(refused)} number(s) no distributor can list were given; not sent")
            for _ in refused:
                stats.count_distributor("mouser", "skipped")
            numbers = [n for n in numbers if n not in refused]
            if not numbers:
                return {}, None
        answers, _, error = await self._answers(numbers, caller)
        return {n: answers[_cache_key(n)] for n in numbers if _cache_key(n) in answers}, error

    def retry_after(self, caller: str | None = None) -> int:
        """Seconds until Mouser may be asked again (60 when the limits don't say)."""
        return (self._quota.retry_after(caller) if self._quota else None) or 60

    def held_back(self, caller: str | None = None) -> bool:
        """Whether the limits would hold a request back now (a pause, every key's day, the minute)."""
        return self._quota is not None and self._quota.retry_after(caller) is not None

    def day_spent(self, caller: str | None = None) -> bool:
        """Whether the caller's or every key's day is spent: nothing goes out until a reset,
        not just for a minute. False without a quota (no way to tell)."""
        return self._quota is not None and (self._quota.address_error(caller) is not None
                                           or self._quota.active_index() is None)

    async def _answers(self, numbers: list[str], caller: str | None
                       ) -> tuple[dict[str, PartAnswer], list[dict[str, Any]], dict[str, Any] | None]:
        """Answers by cache key from the store, then from Mouser for the numbers it doesn't have:
        one request, and one more for numbers a capped reply crowded out (_fetch). Also the results
        matching no number asked (they're returned to the caller, not kept per part), and a limit
        error when one held back the request: then the answers are only those the store had. The
        request runs on as its own task (shielded), so its answers are kept even if this caller
        gives up."""
        stats.count_parts_asked("mouser", numbers)
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
            # The batch lives as long as a found answer; a part it didn't find, as long as a miss
            if self._store.now() - fetched_at >= MOUSER_NOT_FOUND_TTL and any(not a.matched for a in kept.values()):
                continue
            answers.update(kept)
            extras = list(batch.get("extras") or [])
            missing = []
            break
        if not missing:
            stats.count_distributor("mouser", "cached")
            return answers, extras, None
        fresh, more, error = await self._shielded(self._fetch(missing, caller))
        if error is not None:
            return answers, extras, error
        answers.update(fresh)
        return answers, extras + more, None

    async def _fetch(self, numbers: list[str], caller: str | None
                     ) -> tuple[dict[str, PartAnswer], list[dict[str, Any]], dict[str, Any] | None]:
        """One request for these numbers (distinct by cache key), and when its reply was cut at
        Mouser's cap, one more for the numbers it crowded out (_crowded_out), within the limits:
        their answers then come from that reply. A limit refusal or failure of that second request
        retains the first reply's other answers and gives the crowded-out numbers with no match that
        limit error or exception as their problem (not_checked or lookup_failed). An answered but still capped
        follow-up leaves unmatched numbers in get_part's not_found, without keeping misses. When
        Mouser rejects a request of several numbers (an error for the request, not a limit), each
        number is asked alone instead (_one_by_one); a lone number it rejects gets the error as its
        answer's problem, as there, so the caller's kept answers still answer (it raised, and a
        batch with the rest kept failed whole). All requests share one 30-second waiting budget."""
        budget = _WaitBudget()
        try:
            data, error = await self._request(numbers, caller, budget=budget)
        except MouserKeyRejected:
            raise
        except MouserAPIError as e:
            if len(numbers) < 2:
                logger.warning(f"Mouser lookup of one number failed: {type(e).__name__}: {e}")
                return {_cache_key(n): PartAnswer([], False, self._store.now(), False, e) for n in numbers}, [], None
            logger.warning(f"Mouser rejected a request of {len(numbers)} numbers ({e}); asking each alone")
            return await self._one_by_one(numbers, caller, budget=budget)
        if error is not None:
            return {}, [], error
        answers, extras, again = self._keep(numbers, data, keep_batch=True)
        if again:
            try:
                data, error = await self._request(again, caller, budget=budget, check_address=False)
            except (MouserError, MouserAPIError) as e:  # the first reply still answers
                logger.warning(f"Mouser: asking again for numbers a capped reply crowded out failed: {e}")
                data, error = None, e
            if data is not None and error is None:
                more, more_extras, _ = self._keep(again, data)
                answers.update(more)
                extras = extras + more_extras
            elif error is not None:
                # Only numbers with no match move: one with loose matches keeps its first-reply results.
                for number in again:
                    if not answers[_cache_key(number)].matched:
                        answers[_cache_key(number)].problem = error
        return answers, extras, None

    async def _one_by_one(self, numbers: list[str], caller: str | None, *, budget: _WaitBudget
                          ) -> tuple[dict[str, PartAnswer], list[dict[str, Any]], dict[str, Any] | None]:
        """Each number asked alone, within the limits, after Mouser rejected the request of all of
        them: the numbers it takes still answer, and an answer's problem says why one wasn't
        checked (Mouser's error for it, or the limit that held its request back). After a second
        number fails the rest aren't asked (the fault is likely Mouser's, not the numbers'): they
        share that error. Each single answer is kept as a one-number request's is."""
        answers: dict[str, PartAnswer] = {}
        extras: list[dict[str, Any]] = []
        failures: list[Exception] = []
        for index, number in enumerate(numbers):
            now = self._store.now()
            if len(failures) >= 2:
                answers[_cache_key(number)] = PartAnswer([], False, now, False, failures[-1])
                continue
            try:
                data, error = await self._request([number], caller, budget=budget)
            except MouserKeyRejected:
                raise
            except (MouserError, MouserAPIError) as e:
                logger.warning(f"Mouser lookup of one number failed: {type(e).__name__}: {e}")
                failures.append(e)
                answers[_cache_key(number)] = PartAnswer([], False, now, False, e)
                continue
            if error is not None:  # a limit: the rest aren't asked either
                for rest in numbers[index:]:
                    answers[_cache_key(rest)] = PartAnswer([], False, now, False, error)
                break
            more, more_extras, _ = self._keep([number], data)
            answers.update(more)
            extras += more_extras
        return answers, extras, None

    async def _shielded(self, coro):
        """Run coro as its own task and wait for it: a caller giving up (a cancelled tool call)
        doesn't cancel the request, whose answer is still kept for the next caller. close()
        cancels it."""
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        task.add_done_callback(_consume_exception)
        return await asyncio.shield(task)

    async def _request(self, numbers: list[str], caller: str | None, *, budget: _WaitBudget | None = None,
                       check_address: bool = True
                       ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        """Mouser's reply or a limit error; a capped-reply follow-up shares the address allowance."""
        body = {
            "SearchByPartRequest": {
                "mouserPartNumber": "|".join(numbers),
                "partSearchOptions": "None",
            }
        }
        # Each attempt reserves a request on the key it will use (after the store, so stored
        # answers don't count) and sends it with no await in between. Rotation on a daily refusal
        # keeps its own bound; only the first attempt checks and counts the address allowance.
        rotations = retries = attempt = 0
        if budget is None:
            budget = _WaitBudget()
        retry_pending = False
        failure: _TransientFailure | None = None
        while True:
            self._get_client()  # fail before reserving or counting a send after close()
            if retry_pending and self._retries_disabled():
                raise MouserError(str(failure)) from None
            key_index = 0
            if self._quota:
                key_index, quota_error = self._quota.acquire(caller, check_address=check_address and attempt == 0)
                if quota_error:
                    if (self._quota.last_refusal_cause == "distributor_daily"
                            and isinstance(self._quota, MouserKeyPool) and budget.waited < 30):
                        next_try = self._quota.retry_after()
                        if self._quota.checking() or (next_try is not None and next_try <= 30 - budget.waited):
                            delay = min(1, 30 - budget.waited)
                            await self._sleep(delay)
                            budget.waited += delay
                            continue
                    if attempt > 0 and self._quota.last_refusal_cause == "minute_cap":
                        # Ignore the admitted caller's address cap when finding the next slot.
                        delay = self._quota.retry_after()
                        if delay is not None and budget.waited < 30 and budget.waited + delay <= 30:
                            await self._sleep(delay)
                            budget.waited += delay
                            continue
                    stats.count_distributor("mouser", "rate_limited")
                    stats.count_distributor_limit("mouser", "held_back", self._quota.last_refusal_cause)
                    self._quota.held_back.record(caller)
                    return None, quota_error
            stats.count_distributor("mouser", "sent")
            if retry_pending:
                stats.count_distributor("mouser", "retries")
                retry_pending = False
            attempt += 1
            try:
                data = await self._post("/search/partnumber", body, key_index)
            except _TransientFailure as exc:
                delay = self._retry_delay(exc, retries, budget.waited)
                self._log_transient(exc, attempt, key_index, delay)
                if delay is None:
                    raise MouserError(str(exc)) from None
                failure = exc
                await self._sleep(delay)
                budget.waited += delay
                retries += 1
                retry_pending = True
                continue
            except MouserKeySpent as e:
                rotations += 1
                if rotations < len(self._keys):
                    continue
                return None, (self._quota.paused_error() if self._quota else None) or {"error": str(e)}
            except MouserRateLimited as e:
                # A sent refusal can leave a nearby next try or another lookup's check:
                # re-enter acquire so it can wait within this lookup's remaining budget.
                if (isinstance(self._quota, MouserKeyPool) and budget.waited < 30
                        and self._quota.pause_cause() == "distributor_daily"):
                    next_try = self._quota.retry_after()
                    if self._quota.checking() or (next_try is not None and next_try <= 30 - budget.waited):
                        continue
                return None, {"error": str(e)}
            return data, None

    def _keep(self, numbers: list[str], data: dict[str, Any], keep_batch: bool = False
              ) -> tuple[dict[str, PartAnswer], list[dict[str, Any]], list[str]]:
        """One reply's answers by cache key, its extras and, when it was cut at the cap, the
        numbers it crowded out (_crowded_out: to ask again). Keeps each clean number's answer, or,
        with keep_batch (a call's own request, not the follow-up for crowded-out numbers, whose
        joined numbers no call asks), for a batch with an unclear result, the batch under its
        joined numbers; and every result's lifecycle that can be put down to one number. A capped
        reply keeps no negative (no answer without a match, no batch, no "not listed") and nothing
        for the numbers it crowded out; their answers, and those of numbers it has no results for,
        aren't checked until they're asked again."""
        fetched_at = self._store.now()
        parts = (data.get("SearchResults") or {}).get("Parts") or []
        parts = [p for p in parts if isinstance(p, dict)]
        capped = _capped(data, parts)
        results = [_normalize_part(p) for p in parts]
        per, owners, extras, clean = _attribute(numbers, results)
        again = _crowded_out(numbers, per) if capped else []
        answers = {}
        for number in numbers:
            matched = any(_touches(r, number) for r in per[number])
            checked = not capped or (bool(per[number]) and number not in again)
            answer = PartAnswer(per[number], matched, fetched_at, checked)
            answers[_cache_key(number)] = answer
            if number in clean and checked and (matched or not capped):
                # Its lifetime follows matched, as the reply's not_found does: unrelated results
                # don't make a part Mouser didn't find live as long as one it did
                self._store.put_answer("mouser", _cache_key(number), answer.as_json(), matched, fetched_at)
        if keep_batch and len(numbers) > 1 and not capped and len(clean) < len(numbers):
            self._store.put_answer("mouser", _batch_key(numbers), {
                "answers": {key: answer.as_json() for key, answer in answers.items()}, "extras": extras,
            }, any(answer.matched for answer in answers.values()), fetched_at)

        readings = [(Reading(r["mfr_part_number"], r.get("manufacturer") or "", "mouser", r["lifecycle_status"],
                             r.get("lifecycle") or MOUSER_NOT_STATED, fetched_at), r, owner)
                    for r, owner in zip(results, owners) if owner is not None and r.get("mfr_part_number")]
        self._store.put_readings([reading for reading, _, _ in readings])
        # A JST part listed without the (LF)/(SN) endings asked is filed under the number asked too,
        # so part_lifecycle finds it by that spelling (as DigiKey's answers are), unless the reply
        # also lists that maker's part spelled as asked: that listing's reading is the number's own
        spelled = {(mpn_key(reading.mpn), maker_key(reading.maker)) for reading, _, _ in readings}
        for reading, result, owner in readings:
            if (mpn_key(owner) != mpn_key(reading.mpn) and _same_jst(result, owner)
                    and (mpn_key(owner), maker_key(reading.maker)) not in spelled):
                self._store.put_readings([reading], also_as=owner)
        if not capped:  # in a capped reply the part itself may be past the cap
            for number in clean:
                if not any(_identifies(r, number) for r in per[number]):
                    self._store.put_not_listed(number, "mouser", fetched_at)
        return answers, extras, again

    async def close(self) -> None:
        """Close the HTTP client (and the store, if this client made its own). Requests still in
        flight are cancelled, and waited for, so they're done before the server's last save of the
        stats."""
        self._closed = True
        while self._tasks:  # one started while waiting is cancelled too
            tasks = list(self._tasks)
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            self._tasks.difference_update(tasks)
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._owns_store:
            self._store.close()


def _batch_key(numbers: list[str]) -> str:
    """A batch's key in the answer store, for numbers that couldn't be kept one by one."""
    return "batch:" + "|".join(_cache_key(n) for n in numbers)


def _consume_exception(future: asyncio.Future) -> None:
    """Mark a shielded request's exception as seen, so it isn't logged when its caller gave up."""
    if not future.cancelled():
        future.exception()
