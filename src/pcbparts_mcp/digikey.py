"""DigiKey lookups: API first, with an optional deployment extension where enabled after the API day is spent."""

from __future__ import annotations

import asyncio
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, NamedTuple

import httpx

from . import stats
from .cache import (
    SELF_HOSTING_URL, AddressDailyQuota, CallerTally, DailyQuota, Pacer, QuotaPool, _header_int, _next_utc_midnight,
)
from .client import _sent
from .config import (
    DIGIKEY_CLIENT_ID,
    DIGIKEY_CLIENT_SECRET,
    DIGIKEY_BASE_URL,
    DIGIKEY_TOKEN_URL,
    DIGIKEY_PER_SECOND,
    DIGIKEY_LOCALE_SITE,
    DIGIKEY_LOCALE_LANGUAGE,
    DIGIKEY_LOCALE_CURRENCY,
)
from .extensions import AddressCapReached, BackupFailed, BackupUnavailable, Charge, DigiKeyBackup
from .distributor_store import DistributorStore
from .lifecycle import Reading, digikey_status, last_buy_date, utc_text
from .search.mpn import NOT_SENT_HINTS, distributor_match, not_sent_reason, same_jst_part

logger = logging.getLogger(__name__)

# What a user needs to run the server with DigiKey's own limits, named in the limit errors
OWN_CREDENTIALS = "DigiKey API credentials (free at https://developer.digikey.com)"
# The limit replies' advice, as DailyQuota words it for these credentials
_OWN_CREDENTIALS_ADVICE = (f" To skip the shared limits, run pcbparts-mcp with your own {OWN_CREDENTIALS}: "
                           f"{SELF_HOSTING_URL}. Meanwhile use jlc_search.")


class DigiKeyError(ValueError):
    """A DigiKey request failed. The message is ours (no secrets), so the tool can show it."""


class DigiKeyRateLimited(DigiKeyError):
    """DigiKey answered 429: its own daily or per-minute limit is used up."""


class DigiKeyNotFound(DigiKeyError):
    """DigiKey answered 404: it has no product with that number."""


class DigiKeyDailyLimited(DigiKeyRateLimited):
    """Only a daily 429 may retry the lookup on the next app."""


class DigiKeyTokenRejected(DigiKeyError):
    """DigiKey answered 401: the token expired early. The lookup may try once more."""


class DigiKeyAppSpent(DigiKeyDailyLimited):
    """A token request said this app's day is used up while another app can still send: the
    lookup moves on to that app (_ready_app catches it)."""


@dataclass
class DigiKeyApp:
    """One DigiKey app's credentials and OAuth token. Secrets stay out of repr, so logging an app
    never prints them."""
    client_id: str = field(repr=False)
    client_secret: str = field(repr=False)
    access_token: str | None = field(default=None, repr=False)
    token_expires_at: float = 0
    token_lock: asyncio.Lock | None = field(default=None, repr=False)


def _min_qty(variation: dict[str, Any]) -> int:
    return variation.get("MinimumOrderQuantity") or 1


class Lookup(NamedTuple):
    """DigiKeyClient.lookup's answer. reply: get_part's; kind: "found", "not_found", "limited" or
    "invalid"; fetched_at: when DigiKey answered."""
    reply: dict[str, Any]
    kind: str
    fetched_at: float


class LifecycleAnswer(NamedTuple):
    """DigiKeyClient.lifecycle's answer for one number. kind: "found" (readings: its parts'),
    "not_found", "limited" (retry_after: seconds until it may be asked) or "failed"."""
    kind: str
    readings: list[Reading]
    fetched_at: float
    retry_after: int | None = None


def _same_mpn(listed: str, asked: str, maker: str) -> bool:
    """Whether DigiKey's ManufacturerProductNumber is the number asked for: equal ignoring case
    and outer spaces, or for a JST part, equal once the (LF)/(SN) endings are set aside
    (DigiKey sometimes drops them: B2B-PH-K-S(LF)(SN) is listed as B2B-PH-K-S)."""
    return listed.strip().casefold() == asked.strip().casefold() or same_jst_part(listed, asked, maker)


def _answering(reply: dict[str, Any], number: str) -> dict[str, Any]:
    """A found reply whose results say which number they answer (requested: the number asked) and
    how they match it (matched_by: search/mpn.py's distributor_match; part_number is DigiKey's
    number for the packaging described, the one asked when it's one of the product's). Added to
    each reply, not kept: the stored answer is shared by every spelling of the number."""
    return {**reply, "results": [
        {**result, "requested": number,
         "matched_by": distributor_match(number, result.get("mfr_part_number") or "", result.get("manufacturer") or "",
                                         [result.get("part_number") or ""], "digikey_pn")}
        for result in reply.get("results") or []]}


def _pick_variation(variations: list[dict[str, Any]], product_number: str) -> dict[str, Any]:
    """The packaging the reply is about: the DigiKey number asked for, if it's one of this product's;
    otherwise the smallest order (cut tape before a 3000-piece reel), from DigiKey's own stock before
    Marketplace, without a Digi-Reel fee, in DigiKey's order on a tie."""
    wanted = product_number.strip().upper()
    for variation in variations:
        if wanted and (variation.get("DigiKeyProductNumber") or "").upper() == wanted:
            return variation
    return min(variations, key=lambda v: (_min_qty(v), bool(v.get("MarketPlace")), bool(v.get("DigiReelFee"))))


def _price_breaks(variation: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"qty": sp.get("BreakQuantity", 0), "price": sp.get("UnitPrice", 0)}
            for sp in variation.get("StandardPricing") or []]


def _normalize_product(product: dict[str, Any], product_number: str = "") -> dict[str, Any]:
    """Normalize a DigiKey Product object into our standard format. A product can be sold in
    several packagings (cut tape, reel, Digi-Reel), each with its own DigiKey number, minimum order
    and prices; part_number, price, price_breaks and min_qty all describe the one picked, and
    other_packaging lists the rest."""
    desc = product.get("Description", {})
    manufacturer = product.get("Manufacturer", {})
    category = product.get("Category", {})
    status = product.get("ProductStatus", {})
    classifications = product.get("Classifications", {})

    variations = product.get("ProductVariations") or []
    stock = product.get("QuantityAvailable", 0)
    chosen = _pick_variation(variations, product_number) if variations else {}
    price_breaks = _price_breaks(chosen)
    min_qty = _min_qty(chosen)
    digikey_pn = chosen.get("DigiKeyProductNumber", "")
    # The product's UnitPrice is its single-unit price in whichever packaging sells one, so it's
    # only the fallback: on a reel it isn't the reel's price
    unit_price = price_breaks[0]["price"] if price_breaks else product.get("UnitPrice")
    other_packaging = []
    for variation in variations:
        if variation is chosen:
            continue
        breaks = _price_breaks(variation)
        other = {
            "part_number": variation.get("DigiKeyProductNumber", ""),
            "packaging": (variation.get("PackageType") or {}).get("Name", ""),
            "min_qty": _min_qty(variation),
            "price": breaks[0]["price"] if breaks else None,
        }
        if variation.get("DigiReelFee"):
            other["reel_fee"] = variation["DigiReelFee"]
        if variation.get("MarketPlace"):
            other["marketplace"] = True
        other_packaging.append(other)

    # Parse parameters
    parameters = {}
    for param in product.get("Parameters", []):
        name = param.get("ParameterText")
        value = param.get("ValueText")
        if name and value:
            parameters[name] = value

    # Determine lifecycle
    lifecycle = status.get("Status", "Unknown")
    if product.get("Discontinued"):
        lifecycle = "Discontinued"
    lifecycle_status, _ = digikey_status(status.get("Status"), bool(product.get("Discontinued")),
                                         bool(product.get("EndOfLife")))

    result = {
        "source": "digikey",
        "part_number": digikey_pn,
        "mfr_part_number": product.get("ManufacturerProductNumber", ""),
        "manufacturer": manufacturer.get("Name", ""),
        "description": desc.get("ProductDescription", ""),
        "category": category.get("Name", ""),
        "stock": stock or 0,
        "price": unit_price,
        "price_breaks": price_breaks,
        "datasheet_url": product.get("DatasheetUrl"),
        "product_url": product.get("ProductUrl"),
        "rohs": classifications.get("RohsStatus", ""),
        "lifecycle": lifecycle,
        "lifecycle_status": lifecycle_status,
        "parameters": parameters,
        "min_qty": min_qty,
        "currency": DIGIKEY_LOCALE_CURRENCY,
    }
    if buy_by := last_buy_date(product.get("DateLastBuyChance")):
        result["last_buy_date"] = buy_by
    packaging = (chosen.get("PackageType") or {}).get("Name")
    if packaging:
        result["packaging"] = packaging
    if chosen.get("DigiReelFee"):
        result["reel_fee"] = chosen["DigiReelFee"]
    if chosen.get("MarketPlace"):
        result["marketplace"] = True
    if other_packaging:
        result["other_packaging"] = other_packaging
    return result


class DigiKeyClient:
    """DigiKey answers from the OAuth2 API, or the enabled backup path when its day is spent."""

    def __init__(
        self,
        client_id: str = DIGIKEY_CLIENT_ID,
        client_secret: str = DIGIKEY_CLIENT_SECRET,
        quota: DailyQuota | QuotaPool | None = None,
        per_second: float = DIGIKEY_PER_SECOND,
        second_app: tuple[str, str] | None = None,
        store: DistributorStore | None = None,
        clock: Callable[[], float] = time.time,
        backup: DigiKeyBackup | None = None,
        address_daily: AddressDailyQuota | None = None,
    ):
        """store: the answer and lifecycle store shared with MouserClient and part_lifecycle (the
        server passes one); without one the client keeps its own in memory. backup: the server passes
        an optional deployment extension; credentials use the API until its pool's day is spent.
        address_daily: the per-address day shared with Mouser and the API pool; callers and
        held_back: the backup path's hourly per-IP log lines."""
        self._backup = backup
        self._api_enabled = bool(client_id and client_secret)
        self._backup_active = backup is not None and not self._api_enabled
        self._closed = False
        self._address_daily = address_daily if backup is not None else None
        self.callers = CallerTally("DigiKey backup") if backup is not None else None
        self.held_back = CallerTally("DigiKey backup", top=None, what="calls held back") if backup is not None else None
        self._inflight: dict[str, asyncio.Task] = {}  # cache key -> its running backup lookup
        self._apps = [DigiKeyApp(client_id, client_secret)]
        if second_app:
            self._apps.append(DigiKeyApp(*second_app))
        self._http: httpx.AsyncClient | None = None
        self._owns_store = store is None
        self._store = DistributorStore(clock=clock) if store is None else store
        self._quota = QuotaPool([quota]) if isinstance(quota, DailyQuota) else quota
        if backup is not None and self._quota is not None:
            self._address_daily = self._quota.address_daily or address_daily
            self._quota.address_daily = self._address_daily
        if self._quota and len(self._quota.quotas) != len(self._apps):
            raise ValueError("Each DigiKey app needs its own daily quota")
        # DigiKey suspends an app for ten minutes for going over its per-second threshold
        self._pacer = Pacer(per_second)
        self._tasks: set[asyncio.Task] = set()  # lookups whose caller may have given up (_shielded)

    def _get_http(self) -> httpx.AsyncClient:
        if self._closed:  # shutting down: nothing goes out after close()
            raise httpx.ConnectError("DigiKey client closed")
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=15.0)
        return self._http

    def _redact(self, text: str) -> str:
        """DigiKey's own error text goes into our exceptions, which callers show and log (part_lifecycle
        logs them as they are): blank out every app's client ID and secret in case DigiKey echoes one."""
        secrets = {secret for app in self._apps for secret in (app.client_id, app.client_secret) if secret}
        for secret in sorted(secrets, key=len, reverse=True):
            text = text.replace(secret, "[redacted]")
        return text

    def _get_token_lock(self, app: DigiKeyApp) -> asyncio.Lock:
        # Safe in single-threaded asyncio: no await between None check and assignment
        if app.token_lock is None:
            app.token_lock = asyncio.Lock()
        return app.token_lock

    async def _ensure_token(self, app_index: int = 0, caller: str | None = None) -> str:
        """Get a valid OAuth2 token, refreshing if needed."""
        # Fast path: token is still valid (with 100s safety margin)
        app = self._apps[app_index]
        if app.access_token and time.time() < app.token_expires_at - 100:
            return app.access_token

        async with self._get_token_lock(app):
            # Double-check after acquiring lock
            if app.access_token and time.time() < app.token_expires_at - 100:
                return app.access_token
            # Token requests take a pacer slot too, then check pauses: one may have begun while
            # this waited for the lock or the slot (another lookup's 403, say)
            await self._pacer.wait()
            if self._quota and (error := self._quota.address_error(caller)):
                raise DigiKeyRateLimited(error["error"])
            if self._quota and (paused := self._quota.paused_error()):
                raise DigiKeyRateLimited(paused["error"])
            if self._quota and self._quota.active_index() != app_index:
                # This app's day was used up meanwhile (another lookup's token or product
                # request said so): no token request for it; the lookup moves to the next app
                raise DigiKeyAppSpent("DigiKey app changed while waiting for a token")

            try:
                http = self._get_http()  # built first: a slow first build mustn't eat the gap
                self._pacer.mark()
                response = await _sent("digikey", http.post(
                    DIGIKEY_TOKEN_URL,
                    data={
                        "client_id": app.client_id,
                        "client_secret": app.client_secret,
                        "grant_type": "client_credentials",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                ))
            except httpx.HTTPError:
                raise DigiKeyError("DigiKey token request failed (network/connection error)")
            if response.status_code in (403, 429) and self._quota is not None:
                # The token endpoint's limits pause the server as a product request's do
                self._note_limits(response, app_index)
                if paused := self._quota.paused_error():
                    raise DigiKeyRateLimited(paused["error"])
                if self._quota.active_index() != app_index:  # only this app's day is used up
                    raise DigiKeyAppSpent(f"DigiKey token request refused (HTTP {response.status_code})")
            if response.status_code >= 400:
                raise DigiKeyError(f"DigiKey token request failed (HTTP {response.status_code})")
            data = response.json()

            # Check for OAuth error responses (some providers return 200 with error)
            if "error" in data:
                error_desc = data.get("error_description", data["error"])
                raise DigiKeyError(self._redact(f"DigiKey OAuth error: {error_desc}"))

            app.access_token = data["access_token"]
            expires_in = data.get("expires_in", 599)
            app.token_expires_at = time.time() + expires_in

            logger.debug(f"DigiKey token refreshed, expires in {expires_in}s")
            return app.access_token

    def _auth_headers(self, token: str, app_index: int = 0) -> dict[str, str]:
        """Build required headers for DigiKey API requests."""
        return {
            "Authorization": f"Bearer {token}",
            "X-DIGIKEY-Client-Id": self._apps[app_index].client_id,
            "X-DIGIKEY-Locale-Site": DIGIKEY_LOCALE_SITE,
            "X-DIGIKEY-Locale-Language": DIGIKEY_LOCALE_LANGUAGE,
            "X-DIGIKEY-Locale-Currency": DIGIKEY_LOCALE_CURRENCY,
            "Content-Type": "application/json",
        }

    def _note_limits(self, response: httpx.Response, app_index: int) -> None:
        """DigiKey reports its own count on every response (per day and per DigiKey app, so other
        users of the same credentials count too); see DailyQuota.note_response(). Its API User
        Agreement (section 6) suspends an app for ten minutes, with 403s, for going over its
        per-second threshold, and can end the agreement after three suspensions."""
        if response.status_code in (403, 429):
            label = ("refused" if response.status_code == 403 else
                     "daily" if _header_int(response.headers, "x-ratelimit-remaining") == 0 else "minute")
            stats.count_distributor_limit("digikey", "refusals", label)
        if self._quota is not None:
            self._quota.note_response(app_index, response.status_code, response.headers)

    def _token_valid(self, app_index: int, margin: float = 100) -> bool:
        """The app has a token good for at least `margin` more seconds."""
        app = self._apps[app_index]
        return bool(app.access_token) and time.time() < app.token_expires_at - margin

    async def _ready_app(self, caller: str | None = None) -> tuple[int | None, str | None]:
        """The app the next request will use and its token, right after this lookup's pacer slot.

        Token first, pacer second: a slow token refresh holds lookups before their slots, so they
        still leave 1/per_second apart (paced first, they'd all send together once it finished).
        After the pacer, look again: if the app changed or its token lapsed while waiting, get the
        token and take another slot. No token request goes out while the server is paused, and
        each app's token is refreshed at most once per call: a token just fetched is used while
        it hasn't expired, even inside the usual 100 s margin (a short-lived token would
        otherwise be refreshed forever). (None, None) when nothing may be sent; acquire() then
        returns the error. Raises DigiKeyRateLimited if a pause began during a token request."""
        refreshed: set[int] = set()

        def ready(index: int) -> bool:
            return self._token_valid(index, margin=0 if index in refreshed else 100)

        while True:
            if self._quota and (self._quota.address_error(caller) or self._quota.paused_error()):
                return None, None
            index = self._quota.active_index() if self._quota else 0
            if index is not None and not ready(index):
                if index in refreshed:
                    raise DigiKeyError("DigiKey token request returned an expired token")
                try:
                    await self._ensure_token(index, caller)
                except DigiKeyAppSpent:
                    continue  # that app's day is used up: the next app takes over
                refreshed.add(index)
                continue  # the refresh awaited the network: check pauses and the app again
            await self._pacer.wait()
            index = self._quota.active_index() if self._quota else 0
            if index is None or (self._quota and self._quota.penalty_error()):
                return None, None
            if ready(index):
                return index, self._apps[index].access_token

    async def _request(self, method: str, path: str, *, app_index: int, token: str, **kwargs: Any) -> dict[str, Any]:
        """Send one request with the token _ready_app() checked. The caller took its pacer slot and
        reserved the request on the quota just before, with no await since (see get_part)."""
        headers = self._auth_headers(token, app_index)
        url = f"{DIGIKEY_BASE_URL}{path}"

        try:
            http = self._get_http()  # built first: a slow first build mustn't eat the gap
            self._pacer.mark()  # the gap to the next request counts from this send
            if self._quota:
                self._quota.mark_sent()  # and so does the rolling minute
            response = await _sent("digikey", http.request(method, url, headers=headers, **kwargs))
        except httpx.HTTPError:
            raise DigiKeyError("DigiKey API request failed (network/connection error)")
        self._note_limits(response, app_index)

        # The token expired early: drop it (unless another lookup already replaced it). get_part
        # tries once more through the whole path: pauses, a new token, the pacer, the quota.
        if response.status_code == 401:
            app = self._apps[app_index]
            if app.access_token == token:
                app.access_token = None
            raise DigiKeyTokenRejected("DigiKey API returned HTTP 401")

        if response.status_code in (403, 429):
            paused = self._quota.paused_error() if self._quota else None
            if response.status_code == 429 and _header_int(response.headers, "x-ratelimit-remaining") == 0 and self._quota:
                raise DigiKeyDailyLimited(self._quota.daily_error()["error"])
            if paused or response.status_code == 429:
                raise DigiKeyRateLimited(paused["error"] if paused else "DigiKey is limiting requests (HTTP 429). Try again later.")
        if response.status_code == 404:
            raise DigiKeyNotFound("DigiKey has no product with that number")
        if response.status_code >= 400:
            raise DigiKeyError(f"DigiKey API returned HTTP {response.status_code}")
        return response.json()

    async def get_part(self, product_number: str, caller: str | None = None) -> dict[str, Any]:
        """Look up a part by DigiKey PN or manufacturer PN.

        Args:
            product_number: DigiKey part number or manufacturer part number
            caller: the caller's IP, for the hourly log of who sent requests

        Returns:
            Dict with results list and total (consistent with Mouser format)
        """
        return (await self.lookup(product_number, caller))[0]

    def retry_after(self, caller: str | None = None) -> int:
        """Seconds until DigiKey may be asked again (60 when the limits don't say)."""
        if self._using_backup():
            return (self._seconds_to_utc_midnight() if self._address_capped(caller)
                    else self._backup_wait(self._backup.retry_after()))
        return (self._quota.retry_after(caller) if self._quota else None) or 60

    def _backup_wait(self, wait: int) -> int:
        """The API may become available before the backup's wait ends."""
        if self._api_enabled and self._quota is not None:
            return min(wait, self._quota.retry_after() or 1)
        return wait

    def _seconds_to_utc_midnight(self) -> int:
        now = self._store.now()
        return max(1, math.ceil(_next_utc_midnight(now) - now))

    def _seconds_until(self, moment: float) -> int:
        return max(1, math.ceil(moment - self._store.now()))

    def _held_wait(self, hold: tuple[float, bool], pause: int) -> int:
        """retry_after for a number that found no slot, in a batch a pause then stopped: its
        address's reset when that's what stops it, else no sooner than the pause ends."""
        moment, capped = hold
        return self._seconds_until(moment) if capped else max(self._seconds_until(moment), pause)

    def _address_capped(self, caller: str | None) -> bool:
        return self._address_daily is not None and self._address_daily.capped(caller)

    def _hold_back_for_address(self, caller: str | None, lookups: int = 1) -> None:
        """Counts for backup lookups the per-address day stopped (none of them sent)."""
        for _ in range(lookups):
            stats.count_distributor("digikey", "rate_limited")
            stats.count_distributor_limit("digikey", "held_back", self._address_daily.refusal_cause(caller))
            self.held_back.record(caller)

    @property
    def unmetered(self) -> bool:
        """The active path spends no API quota and isn't paused: part_lifecycle asks it first."""
        return self._using_backup() and self._backup.unmetered and self._backup.can_answer_now()

    def _using_backup(self) -> bool:
        """Only the pool's spent day permits fallback; minute/403 penalties keep precedence.
        Re-evaluating the pool also resets its counts at 00:00 UTC. Log each transition once,
        including when restored quota state starts this process on the backup path."""
        active = self._backup is not None and (not self._api_enabled or (
            self._quota is not None and self._quota.pause_cause() in {"distributor_daily", "daily_count"}))
        if active != self._backup_active:
            self._backup_active = active
            logger.info("DigiKey lookups moved to %s", "the backup (API day spent)" if active else "the API")
        return active

    def backup_status(self) -> dict[str, Any] | None:
        """The extension's pause status for authenticated /mcp/stats when no API pool is configured."""
        return self._backup.status() if self._backup is not None and not self._api_enabled else None

    def can_answer_now(self, caller: str | None = None) -> bool:
        """A lookup could go out on the active backup path (not paused, and caller's address hasn't
        used its day): for the miss hint, which mustn't send a caller to a refusal."""
        return self.unmetered and not self._address_capped(caller)

    async def lookup(self, product_number: str, caller: str | None = None) -> Lookup:
        """get_part's reply, what it was and when DigiKey answered (Lookup). A number DigiKey can't
        list (search/mpn.py's not_sent_reason: a value such as "10k", an LCSC code, not 3-40
        characters...) isn't sent: it gets the not-found reply with not_sent, without a request or
        the quota."""
        product_number = product_number.strip()
        if not product_number:
            return Lookup({"error": "Give a DigiKey or manufacturer part number."}, "invalid", self._store.now())
        if reason := not_sent_reason(product_number):
            stats.count_distributor("digikey", "skipped")
            return Lookup(_not_sent_reply(product_number, reason), "not_found", self._store.now())
        stats.count_parts_asked("digikey", [product_number])
        # Kept per number, ignoring case: DigiKey's search ignores it, and so does its match (_same_mpn)
        cache_key = product_number.upper()
        stored = self._store.get_answer("digikey", cache_key)
        if stored is not None:
            stats.count_distributor("digikey", "cached")
            answer, fetched_at = stored
            if answer.get("not_found"):
                return Lookup(_not_found_reply(product_number), "not_found", fetched_at)
            return Lookup(_answering(answer, product_number), "found", fetched_at)
        if self._using_backup():
            return await self._lookup_backup(product_number, cache_key, caller)
        # Its own task: a caller giving up mid-request doesn't waste it, the answer is still kept
        task = asyncio.create_task(self._fetch(product_number, caller, cache_key))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        task.add_done_callback(lambda done: done.cancelled() or done.exception())
        return await asyncio.shield(task)

    async def _fetch(self, product_number: str, caller: str | None, cache_key: str) -> Lookup:
        """An API refusal can spend the last app's day while this lookup is running. Continue
        through the backup only for that cause, carrying its first send's address charge with it."""
        if self._using_backup():  # the day may have ended while this task was queued
            return await self._lookup_backup(product_number, cache_key, caller)
        charged: set[str] = set()
        result = await self._fetch_api(product_number, caller, cache_key, charged)
        if (result.kind == "limited" and self._using_backup()
                and (charged or not self._address_capped(caller))):
            return await self._lookup_backup(product_number, cache_key, caller, address_charged=bool(charged))
        return result

    async def _fetch_api(self, product_number: str, caller: str | None, cache_key: str,
                         charged: set[str]) -> Lookup:
        """lookup() for a number the store doesn't have: one keyword search, within the limits."""
        # Cache hits cost no quota. Each attempt gets the app's token and its pacer slot, then checks
        # every limit and pause, counts the request and sends it with that token, with no await from
        # the check to the send: a pause or a spent day noticed meanwhile stops it before anything
        # reaches DigiKey, and nothing is counted that isn't sent. At most two requests a lookup:
        # one more after a daily refusal on app 1 (on app 2), or after an early-expired token.
        for attempt in range(2):
            if attempt == 0 and self._quota and (error := self._quota.address_error(caller)):
                stats.count_distributor("digikey", "rate_limited")
                stats.count_distributor_limit("digikey", "held_back", self._quota.address_daily.refusal_cause(caller))
                self._quota.held_back.record(caller)
                return Lookup(error, "limited", self._store.now())
            if self._quota and (paused := self._quota.paused_error()):  # fail fast, no queueing
                # a daily fallback isn't a held-back lookup, nor is one whose first request went out
                if not self._using_backup() and not charged:
                    stats.count_distributor("digikey", "rate_limited")
                    stats.count_distributor_limit("digikey", "held_back", self._quota.pause_cause())
                    self._quota.held_back.record(caller)
                return Lookup(paused, "limited", self._store.now())
            # No await from here to the send: acquire() picks the app _ready_app() just checked, and
            # refuses (counting nothing) whenever _ready_app() found nothing may be sent
            try:
                app_index, token = await self._ready_app(caller if attempt == 0 else None)
            except DigiKeyRateLimited as e:  # a pause began during a token request
                if not charged and (not self._using_backup() or self._address_capped(caller)):
                    stats.count_distributor("digikey", "rate_limited")
                    stats.count_distributor_limit("digikey", "held_back",
                                                  (self._quota.address_daily.refusal_cause(caller)
                                                   if attempt == 0 and self._quota.address_error(caller)
                                                   else self._quota.pause_cause()) if self._quota else "other")
                    if self._quota:
                        self._quota.held_back.record(caller)
                return Lookup({"error": str(e)}, "limited", self._store.now())
            if self._quota:
                app_index, quota_error = self._quota.acquire(caller, check_address=attempt == 0)
                if quota_error:
                    if not charged and (not self._using_backup()
                                        or self._quota.last_refusal_cause in ("address_daily", "address_blocked")):
                        stats.count_distributor("digikey", "rate_limited")
                        stats.count_distributor_limit("digikey", "held_back", self._quota.last_refusal_cause)
                        self._quota.held_back.record(caller)
                    return Lookup(quota_error, "limited", self._store.now())
                charged.add(product_number)
            stats.count_distributor("digikey", "sent")
            try:
                data = await self._request("POST", "/search/keyword", app_index=app_index, token=token, json={
                    "Keywords": product_number, "Limit": 10, "Offset": 0,
                })
            except DigiKeyTokenRejected:
                if attempt == 0:
                    continue
                raise
            except DigiKeyDailyLimited as e:
                if attempt == 0 and app_index == 0 and len(self._apps) == 2:
                    continue
                return Lookup({"error": str(e)}, "limited", self._store.now())
            except DigiKeyRateLimited as e:
                return Lookup({"error": str(e)}, "limited", self._store.now())
            except DigiKeyNotFound:
                data = {}
            break
        fetched_at = self._store.now()
        # DigiKey PN exact matches can have a different MPN; trust ExactMatches in full.
        candidates = list(data.get("ExactMatches") or [])
        candidates.extend(p for p in data.get("Products") or []
                          if _same_mpn(p.get("ManufacturerProductNumber") or "", product_number,
                                       (p.get("Manufacturer") or {}).get("Name") or ""))
        products = []
        seen = set()
        for candidate in candidates:
            mpn = (candidate.get("ManufacturerProductNumber") or "").strip().casefold()
            key = ((candidate.get("Manufacturer") or {}).get("Name", ""), mpn)
            if key not in seen:
                seen.add(key)
                products.append(candidate)
        products.sort(key=lambda p: p.get("QuantityAvailable") or 0, reverse=True)

        if not products:
            # Kept too (DIGIKEY_NOT_FOUND_TTL): asking again for a wrong or partial number costs no request
            self._store.put_answer("digikey", cache_key, {"not_found": True}, False, fetched_at)
            self._store.put_not_listed(product_number, "digikey", fetched_at)
            return Lookup(_not_found_reply(product_number), "not_found", fetched_at)

        results = [_normalize_product(p, product_number) for p in products]
        result = {"results": results, "total": len(products), "observed_at": utc_text(fetched_at)}
        self._store.put_answer("digikey", cache_key, result, True, fetched_at)
        # Each part's lifecycle, filed under the number asked too: DigiKey's match can drop JST's
        # (LF)(SN) endings or take a DigiKey PN, so the asked number can differ from the MPN
        readings = []
        for part, product in zip(results, products):
            if part["mfr_part_number"]:
                status, raw = digikey_status((product.get("ProductStatus") or {}).get("Status"),
                                             bool(product.get("Discontinued")), bool(product.get("EndOfLife")))
                readings.append(Reading(part["mfr_part_number"], part["manufacturer"], "digikey", status, raw,
                                        fetched_at, last_buy_date=part.get("last_buy_date")))
        self._store.put_readings(readings, also_as=product_number)
        return Lookup(_answering(result, product_number), "found", fetched_at)

    async def _lookup_backup(self, product_number: str, cache_key: str, caller: str | None = None,
                           *, address_charged: bool = False) -> Lookup:
        """lookup() through the backup, for a number the store doesn't have. One lookup a number
        at a time: a second caller for it waits for the first's answer (counted as cached, free).
        The caller that starts a lookup is charged one of its address's day as its first request
        goes out (_charge), so a lookup that sends nothing costs nothing."""
        while True:
            task = self._inflight.get(cache_key)
            joined = task is not None
            if not joined:
                if not address_charged and self._address_capped(caller):  # no need to queue it
                    self._hold_back_for_address(caller)
                    return self._address_limited(caller)
                task = asyncio.create_task(self._fetch_backup(product_number, cache_key, caller,
                                                            address_charged=address_charged))
                self._inflight[cache_key] = task
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)
                task.add_done_callback(
                    lambda done: self._inflight.get(cache_key) is done and self._inflight.pop(cache_key))
                task.add_done_callback(lambda done: done.cancelled() or done.exception())
            try:
                result = await asyncio.shield(task)
            except BaseException:  # the shared lookup failed (or this call was cancelled): answered all the same
                if joined:
                    stats.count_distributor("digikey", "cached")
                raise
            if result.kind != "address_capped":
                if joined:
                    stats.count_distributor("digikey", "cached")
                break
            if not joined:  # its own address's day ran out while it waited for a slot
                return self._address_limited(caller)
            # The lookup it joined was its starter's, refused by that address's day: ask again, now
            # charged to this caller if it sends. Drop the finished task first: its cleanup callback
            # may not have run yet, and awaiting a done task doesn't yield, so this would spin on it
            if self._inflight.get(cache_key) is task:
                del self._inflight[cache_key]
        if result.kind == "found":
            return Lookup(_answering(result.reply, product_number), "found", result.fetched_at)
        if result.kind == "not_found":
            return Lookup(_not_found_reply(product_number), "not_found", result.fetched_at)
        return result

    async def _fetch_backup(self, product_number: str, cache_key: str, caller: str | None = None,
                          *, address_charged: bool = False) -> Lookup:
        """One lookup through the backup, kept in the store as an API answer is (found: the stored
        answer, without requested and matched_by)."""
        assert self._backup is not None
        sent: set[str] = set()  # gets the number once its first request goes out
        try:
            answer = await self._backup.lookup(product_number, sent=sent,
                                            charge=self._charge(caller, address_charged=address_charged))
        except AddressCapReached:  # its address's day ran out while it waited for a slot (counted by _charge)
            return self._address_capped_lookup(caller)
        except BackupUnavailable as e:  # a request out was counted as sent by _charge; else held back here
            if not sent and self._held_back_unsent(caller, e, 1, address_charged=address_charged):
                return self._address_capped_lookup(caller)
            return Lookup(_backup_limited(e, self._backup_wait(e.retry_after)), "limited", self._store.now())
        except BackupFailed:  # its request went out (counted by _charge)
            raise DigiKeyError("DigiKey request failed (network/connection or server error)") from None
        fetched_at = self._store.now()
        if not answer.results:
            self._store.put_answer("digikey", cache_key, {"not_found": True}, False, fetched_at)
            self._store.put_not_listed(product_number, "digikey", fetched_at)
            return Lookup({}, "not_found", fetched_at)
        result = {"results": answer.results, "total": len(answer.results), "observed_at": utc_text(fetched_at)}
        # Store the same result shape as an API answer
        self._store.put_answer("digikey", cache_key, result, True, fetched_at)
        self._store.put_readings(self._backup_readings(answer.statuses, fetched_at), also_as=product_number)
        return Lookup(result, "found", fetched_at)

    @staticmethod
    def _backup_readings(statuses: list[tuple[str, str, str | None, str | None]], fetched_at: float) -> list[Reading]:
        """Each part's lifecycle reading from status text and an optional last-buy date."""
        readings = []
        for mpn, maker, status_text, buy_by in statuses:
            if mpn:
                status, raw = digikey_status(status_text)
                readings.append(Reading(mpn, maker, "digikey", status, raw, fetched_at, last_buy_date=buy_by))
        return readings

    def _charge(self, caller: str | None, refused: dict[str, float] | None = None,
                *, address_charged: bool = False) -> Charge:
        """For DigiKeyBackup: called just before a number's first request, with no await between it
        and the send, so the check and the count can't be split by another lookup. False (nothing
        sent) once caller's address has used its day; exempt callers are never counted. Both outcomes
        are counted here, as they happen (sent in /mcp/stats and the hourly "requests sent" line;
        a refusal as held back), so a lookup cancelled or stopped later, or still running at
        shutdown, neither loses nor repeats a count. refused: gets
        each number refused and when its address's day resets (00:00 UTC after the refusal), so a
        batch stopped afterwards doesn't count it again and its retry_after holds past midnight.
        address_charged: this lookup already spent its allowance on an API attempt."""
        day = None if address_charged else self._address_daily

        def charge(number: str, check: bool = False) -> bool:
            """check: before waiting for a slot and the pacer, whether the number may go out at all
            (refused, and counted, if not; nothing recorded otherwise). The call at the send counts."""
            if day is not None and day.capped(caller):
                self._hold_back_for_address(caller)
                if refused is not None:
                    refused[number] = _next_utc_midnight(self._store.now())
                return False
            if check:
                return True
            if day is not None:
                day.record(caller)
            stats.count_distributor("digikey", "sent")
            self.callers.record(caller)
            return True
        return charge

    def _held_back_unsent(self, caller: str | None, error: BackupUnavailable, lookups: int,
                          *, address_charged: bool = False) -> bool:
        """Counts for lookups a BackupUnavailable stopped before their first request: as the address's
        day when caller has used it (it couldn't have sent anyway; the API path checks it first),
        else as the backup's limit. True for the address's day."""
        if lookups <= 0 or address_charged:
            return False
        if self._address_capped(caller):
            self._hold_back_for_address(caller, lookups)
            return True
        for _ in range(lookups):
            stats.count_distributor("digikey", "rate_limited")
            stats.count_distributor_limit("digikey", "held_back", "distributor_refused" if error.paused else "other")
            self.held_back.record(caller)
        return False

    def _address_limited(self, caller: str | None) -> Lookup:
        return Lookup(self._address_daily.error(_OWN_CREDENTIALS_ADVICE, caller), "limited", self._store.now())

    def _address_capped_lookup(self, caller: str | None) -> Lookup:
        """_fetch_backup's answer when its starter's address had used its day: that caller's alone, so
        _lookup_backup lets a caller that joined it ask again with its own."""
        return Lookup(self._address_daily.error(_OWN_CREDENTIALS_ADVICE, caller), "address_capped", self._store.now())

    async def lifecycle(self, numbers: list[str], caller: str | None = None) -> dict[str, LifecycleAnswer]:
        """part_lifecycle's DigiKey readings while the backup path is active, for numbers that may be sent
        (search/mpn.py's not_sent_reason): stored answers first, then one batch for the rest
        (statuses only, no prices; DigiKeyBackup.statuses), each one of caller's address's day; past
        it, "limited" until 00:00 UTC. While the API is active part_lifecycle uses lookup() for each."""
        assert self._backup is not None
        numbers = list(dict.fromkeys(n.strip() for n in numbers if n.strip()))
        stats.count_parts_asked("digikey", numbers)
        answers: dict[str, LifecycleAnswer] = {}
        wanted = []
        for number in numbers:
            stored = self._store.get_answer("digikey", number.upper())
            if stored is None:
                wanted.append(number)
                continue
            stats.count_distributor("digikey", "cached")
            answer, fetched_at = stored
            if answer.get("not_found"):
                answers[number] = LifecycleAnswer("not_found", [], fetched_at)
                continue
            readings = [r for r in self._store.readings(number) if r.source == "digikey" and r.found] or [
                Reading(result.get("mfr_part_number") or number, result.get("manufacturer") or "", "digikey",
                        result.get("lifecycle_status") or "unknown", result.get("lifecycle"), fetched_at,
                        last_buy_date=result.get("last_buy_date"))
                for result in answer.get("results") or []]
            answers[number] = LifecycleAnswer("found", readings, fetched_at)
        if not wanted:
            return answers
        if self._address_capped(caller):  # its day is used: held back without queueing (the charge
            # at each number's first request decides for a batch that runs out midway)
            self._hold_back_for_address(caller, len(wanted))
            now, wait = self._store.now(), self._seconds_to_utc_midnight()
            return {**answers, **{number: LifecycleAnswer("limited", [], now, wait) for number in wanted}}
        sent: set[str] = set()  # the numbers whose first request went out, each charged as it went
        refused: dict[str, float] = {}  # number -> its day's reset, for those the charge refused (and counted)
        # A task of this client's, so close() cancels and waits for it as for a single lookup (and
        # cancelling this call cancels it too)
        # number -> (when it may be asked again, whether its address's day is what stops it), for
        # those that found no slot (counted then)
        held: dict[str, tuple[float, bool]] = {}

        def hold(number: str, error: BackupUnavailable) -> None:
            now = self._store.now()
            capped = self._held_back_unsent(caller, error, 1)
            held[number] = (_next_utc_midnight(now) if capped else now + error.retry_after, capped)

        batch = asyncio.ensure_future(self._backup.statuses(wanted, sent=sent, charge=self._charge(caller, refused),
                                                          held=hold))
        self._tasks.add(batch)
        batch.add_done_callback(self._tasks.discard)
        try:
            found = await batch
        except BackupUnavailable as e:  # the numbers sent were counted by _charge; the rest held back here
            unsent = [n for n in wanted if n not in sent and n not in refused and n not in held]
            backup_wait = self._backup_wait(e.retry_after)  # the API may come back before the backup
            wait = self._seconds_to_utc_midnight() if self._held_back_unsent(caller, e, len(unsent)) else backup_wait
            now = self._store.now()
            return {**answers, **{n: LifecycleAnswer("limited", [], now, self._seconds_until(refused[n]) if n in refused
                                                     else self._backup_wait(self._held_wait(held[n], e.retry_after))
                                                     if n in held else wait if n in unsent else backup_wait)
                                  for n in wanted}}
        except BackupFailed:  # every number tried failed (each sent); one never sent was refused: all counted by _charge
            now = self._store.now()
            return {**answers, **{n: LifecycleAnswer("limited", [], now, self._seconds_until(refused[n])) if n in refused
                                  else LifecycleAnswer("failed", [], now) for n in wanted}}
        fetched_at = self._store.now()
        for number in wanted:
            value = found.get(number)
            if isinstance(value, AddressCapReached):  # the day ran out before its first request (counted by _charge)
                reset = refused.get(number)
                answers[number] = LifecycleAnswer("limited", [], fetched_at, self._seconds_until(reset) if reset
                                                  else self._seconds_to_utc_midnight())
                continue
            if isinstance(value, BackupUnavailable):  # no request slot in time for this one
                if number in held:  # never sent: counted as it gave up; no sooner than a pause begun since
                    answers[number] = LifecycleAnswer("limited", [], fetched_at, self._backup_wait(
                        self._held_wait(held[number], self._backup.paused_for())))
                    continue
                if number not in sent and self._held_back_unsent(caller, value, 1):  # sent: counted by _charge
                    answers[number] = LifecycleAnswer("limited", [], fetched_at, self._seconds_to_utc_midnight())
                    continue
                answers[number] = LifecycleAnswer("limited", [], fetched_at, self._backup_wait(value.retry_after))
                continue
            if not isinstance(value, list):  # its own lookup failed (BackupFailed)
                answers[number] = LifecycleAnswer("failed", [], fetched_at)
                continue
            readings = self._backup_readings(value, fetched_at)
            if readings:
                self._store.put_readings(readings, also_as=number)
                answers[number] = LifecycleAnswer("found", readings, fetched_at)
            else:
                self._store.put_answer("digikey", number.upper(), {"not_found": True}, False, fetched_at)
                self._store.put_not_listed(number, "digikey", fetched_at)
                answers[number] = LifecycleAnswer("not_found", [], fetched_at)
        return answers

    async def stop(self) -> None:
        """Stop lookups before the server saves final counts; provider cleanup can wait until after."""
        self._closed = True
        while self._tasks:  # one started while waiting is cancelled too
            tasks = list(self._tasks)
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            self._tasks.difference_update(tasks)

    async def close(self) -> None:
        """Stop lookups and close owned resources, with the backup last."""
        await self.stop()
        if self._http:
            await self._http.aclose()
            self._http = None
        if self._owns_store:
            self._store.close()
        if self._backup is not None:
            await self._backup.close()


def _backup_limited(error: BackupUnavailable, wait: int | None = None) -> dict[str, Any]:
    """The limit reply when a lookup through the backup can't be made now."""
    wait = error.retry_after if wait is None else wait
    if error.paused:
        return {"error": f"DigiKey lookups are paused on this shared server. Try again in {wait} s. "
                         f"To skip the shared limits, run pcbparts-mcp with your own {OWN_CREDENTIALS}: "
                         f"{SELF_HOSTING_URL}. Meanwhile use jlc_search."}
    return {"error": f"DigiKey lookups are busy on this shared server. Try again in {wait} s."}


def _not_sent_reply(product_number: str, reason: str) -> dict[str, Any]:
    """The not-found reply for a number not sent to DigiKey (search/mpn.py's NOT_SENT_REASONS)."""
    return {"error": f"Part not found: {product_number}", "not_sent": reason,
            "hint": f"Not sent to DigiKey: '{product_number[:60]}' {NOT_SENT_HINTS[reason]}."}


def _not_found_reply(product_number: str) -> dict[str, Any]:
    not_found = {"error": f"Part not found: {product_number}"}
    if not product_number.upper().endswith("-ND"):
        not_found["hint"] = ("DigiKey has no exact match for this number. If you have it, "
                             "try the DigiKey part number "
                             "(usually ending in -ND).")
    return not_found
