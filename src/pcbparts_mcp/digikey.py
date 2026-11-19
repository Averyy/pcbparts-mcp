"""DigiKey Product Information API v4 client."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, NamedTuple

import httpx

from . import stats
from .cache import DailyQuota, Pacer, QuotaPool, _header_int
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
from .distributor_store import DistributorStore
from .lifecycle import Reading, digikey_status, last_buy_date, utc_text
from .search.mpn import NOT_SENT_HINTS, distributor_match, not_sent_reason, same_jst_part

logger = logging.getLogger(__name__)


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


def _same_mpn(listed: str, asked: str, maker: str) -> bool:
    """Whether DigiKey's ManufacturerProductNumber is the number asked for: equal ignoring case
    and outer spaces, or for a JST part, equal once the (LF)/(SN) endings are set aside
    (DigiKey sometimes drops them: B2B-PH-K-S(LF)(SN) is listed as B2B-PH-K-S)."""
    return listed.strip().casefold() == asked.strip().casefold() or same_jst_part(listed, asked, maker)


def _answering(reply: dict[str, Any], number: str) -> dict[str, Any]:
    """A found reply whose results say which number they answer (requested: the number asked) and
    how they match it (matched_by: search/mpn.py's distributor_match; part_number is DigiKey's
    number for the packaging described, the one asked when it's one of the product's). Added to
    each reply, not kept: the 3-day answer is shared by every spelling of the number."""
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
    """Async client for DigiKey Product Information API v4 with OAuth2."""

    def __init__(
        self,
        client_id: str = DIGIKEY_CLIENT_ID,
        client_secret: str = DIGIKEY_CLIENT_SECRET,
        quota: DailyQuota | QuotaPool | None = None,
        per_second: float = DIGIKEY_PER_SECOND,
        second_app: tuple[str, str] | None = None,
        store: DistributorStore | None = None,
        clock: Callable[[], float] = time.time,
    ):
        """store: the answer and lifecycle store shared with MouserClient and part_lifecycle (the
        server passes one); without one the client keeps its own in memory."""
        self._apps = [DigiKeyApp(client_id, client_secret)]
        if second_app:
            self._apps.append(DigiKeyApp(*second_app))
        self._http: httpx.AsyncClient | None = None
        self._owns_store = store is None
        self._store = DistributorStore(clock=clock) if store is None else store
        self._quota = QuotaPool([quota]) if isinstance(quota, DailyQuota) else quota
        if self._quota and len(self._quota.quotas) != len(self._apps):
            raise ValueError("Each DigiKey app needs its own daily quota")
        # DigiKey suspends an app for ten minutes for going over its per-second threshold
        self._pacer = Pacer(per_second)
        self._tasks: set[asyncio.Task] = set()  # lookups whose caller may have given up (_shielded)

    def _get_http(self) -> httpx.AsyncClient:
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

    async def _ensure_token(self, app_index: int = 0) -> str:
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
            if self._quota and (paused := self._quota.paused_error()):
                raise DigiKeyRateLimited(paused["error"])
            if self._quota and self._quota.active_index() != app_index:
                # This app's day was used up meanwhile (another lookup's token or product
                # request said so): no token request for it; the lookup moves to the next app
                raise DigiKeyAppSpent("DigiKey app changed while waiting for a token")

            try:
                http = self._get_http()  # built first: a slow first build mustn't eat the gap
                self._pacer.mark()
                response = await http.post(
                    DIGIKEY_TOKEN_URL,
                    data={
                        "client_id": app.client_id,
                        "client_secret": app.client_secret,
                        "grant_type": "client_credentials",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
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
        if self._quota is not None:
            self._quota.note_response(app_index, response.status_code, response.headers)

    def _token_valid(self, app_index: int, margin: float = 100) -> bool:
        """The app has a token good for at least `margin` more seconds."""
        app = self._apps[app_index]
        return bool(app.access_token) and time.time() < app.token_expires_at - margin

    async def _ready_app(self) -> tuple[int | None, str | None]:
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
            if self._quota and self._quota.paused_error():
                return None, None
            index = self._quota.active_index() if self._quota else 0
            if index is not None and not ready(index):
                if index in refreshed:
                    raise DigiKeyError("DigiKey token request returned an expired token")
                try:
                    await self._ensure_token(index)
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
            response = await http.request(method, url, headers=headers, **kwargs)
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

    def retry_after(self) -> int:
        """Seconds until DigiKey may be asked again (60 when the limits don't say)."""
        return (self._quota.retry_after() if self._quota else None) or 60

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
        # Its own task: a caller giving up mid-request doesn't waste it, the answer is still kept
        task = asyncio.create_task(self._fetch(product_number, caller, cache_key))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        task.add_done_callback(lambda done: done.cancelled() or done.exception())
        return await asyncio.shield(task)

    async def _fetch(self, product_number: str, caller: str | None, cache_key: str) -> Lookup:
        """lookup() for a number the store doesn't have: one keyword search, within the limits."""
        # Cache hits cost no quota. Each attempt gets the app's token and its pacer slot, then checks
        # every limit and pause, counts the request and sends it with that token, with no await from
        # the check to the send: a pause or a spent day noticed meanwhile stops it before anything
        # reaches DigiKey, and nothing is counted that isn't sent. At most two requests a lookup:
        # one more after a daily refusal on app 1 (on app 2), or after an early-expired token.
        for attempt in range(2):
            if self._quota and (paused := self._quota.paused_error()):  # fail fast, no queueing
                stats.count_distributor("digikey", "rate_limited")
                return Lookup(paused, "limited", self._store.now())
            # No await from here to the send: acquire() picks the app _ready_app() just checked, and
            # refuses (counting nothing) whenever _ready_app() found nothing may be sent
            try:
                app_index, token = await self._ready_app()
            except DigiKeyRateLimited as e:  # a pause began during a token request
                stats.count_distributor("digikey", "rate_limited")
                return Lookup({"error": str(e)}, "limited", self._store.now())
            if self._quota:
                app_index, quota_error = self._quota.acquire(caller)
                if quota_error:
                    stats.count_distributor("digikey", "rate_limited")
                    return Lookup(quota_error, "limited", self._store.now())
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
            # Kept too (a day), so asking again for a wrong or partial number costs no request
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

    async def close(self) -> None:
        """Close the HTTP client (and the store, if this client made its own). Lookups still in
        flight are cancelled."""
        for task in list(self._tasks):
            task.cancel()
        if self._http:
            await self._http.aclose()
            self._http = None
        if self._owns_store:
            self._store.close()


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
