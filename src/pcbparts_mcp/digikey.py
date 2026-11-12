"""DigiKey Product Information API v4 client."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, TYPE_CHECKING
from urllib.parse import quote

import httpx

from . import stats
from .cache import Pacer, TTLCache
from .config import (
    DIGIKEY_CLIENT_ID,
    DIGIKEY_CLIENT_SECRET,
    DIGIKEY_BASE_URL,
    DIGIKEY_TOKEN_URL,
    DIGIKEY_CACHE_TTL,
    DIGIKEY_NOT_FOUND_TTL,
    DIGIKEY_PER_SECOND,
    DIGIKEY_LOCALE_SITE,
    DIGIKEY_LOCALE_LANGUAGE,
    DIGIKEY_LOCALE_CURRENCY,
)

if TYPE_CHECKING:
    from .cache import DailyQuota

logger = logging.getLogger(__name__)


class DigiKeyError(ValueError):
    """A DigiKey request failed. The message is ours (no secrets), so the tool can show it."""


class DigiKeyRateLimited(DigiKeyError):
    """DigiKey answered 429: its own daily or per-minute limit is used up."""


class DigiKeyNotFound(DigiKeyError):
    """DigiKey answered 404: it has no product with that number."""


def _min_qty(variation: dict[str, Any]) -> int:
    return variation.get("MinimumOrderQuantity") or 1


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
        "parameters": parameters,
        "min_qty": min_qty,
        "currency": DIGIKEY_LOCALE_CURRENCY,
    }
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
        quota: DailyQuota | None = None,
        per_second: float = DIGIKEY_PER_SECOND,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._http: httpx.AsyncClient | None = None
        # OAuth2 token state
        self._access_token: str | None = None
        self._token_expires_at: float = 0
        self._token_lock: asyncio.Lock | None = None
        self._cache = TTLCache(ttl=DIGIKEY_CACHE_TTL)
        self._quota = quota
        # DigiKey suspends an app for ten minutes for going over its per-second threshold
        self._pacer = Pacer(per_second)

    def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=15.0)
        return self._http

    def _get_token_lock(self) -> asyncio.Lock:
        # Safe in single-threaded asyncio: no await between None check and assignment
        if self._token_lock is None:
            self._token_lock = asyncio.Lock()
        return self._token_lock

    async def _ensure_token(self) -> str:
        """Get a valid OAuth2 token, refreshing if needed."""
        # Fast path: token is still valid (with 100s safety margin)
        if self._access_token and time.time() < self._token_expires_at - 100:
            return self._access_token

        async with self._get_token_lock():
            # Double-check after acquiring lock
            if self._access_token and time.time() < self._token_expires_at - 100:
                return self._access_token

            try:
                response = await self._get_http().post(
                    DIGIKEY_TOKEN_URL,
                    data={
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "grant_type": "client_credentials",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
            except httpx.HTTPError:
                raise DigiKeyError("DigiKey token request failed (network/connection error)")
            if response.status_code >= 400:
                raise DigiKeyError(f"DigiKey token request failed (HTTP {response.status_code})")
            data = response.json()

            # Check for OAuth error responses (some providers return 200 with error)
            if "error" in data:
                error_desc = data.get("error_description", data["error"])
                raise DigiKeyError(f"DigiKey OAuth error: {error_desc}")

            self._access_token = data["access_token"]
            expires_in = data.get("expires_in", 599)
            self._token_expires_at = time.time() + expires_in

            logger.debug(f"DigiKey token refreshed, expires in {expires_in}s")
            return self._access_token

    def _auth_headers(self, token: str) -> dict[str, str]:
        """Build required headers for DigiKey API requests."""
        return {
            "Authorization": f"Bearer {token}",
            "X-DIGIKEY-Client-Id": self._client_id,
            "X-DIGIKEY-Locale-Site": DIGIKEY_LOCALE_SITE,
            "X-DIGIKEY-Locale-Language": DIGIKEY_LOCALE_LANGUAGE,
            "X-DIGIKEY-Locale-Currency": DIGIKEY_LOCALE_CURRENCY,
            "Content-Type": "application/json",
        }

    def _note_limits(self, response: httpx.Response) -> None:
        """DigiKey reports its own count on every response (per day and per DigiKey app, so other
        users of the same credentials count too); see DailyQuota.note_response(). Its API User
        Agreement (section 6) suspends an app for ten minutes, with 403s, for going over its
        per-second threshold, and can end the agreement after three suspensions."""
        if self._quota is not None:
            self._quota.note_response(response.status_code, response.headers, refused_pause=600)

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make an authenticated request to DigiKey API."""
        token = await self._ensure_token()
        headers = self._auth_headers(token)
        url = f"{DIGIKEY_BASE_URL}{path}"

        try:
            await self._pacer.wait()
            response = await self._get_http().request(method, url, headers=headers, **kwargs)
            self._note_limits(response)

            # Handle token expiration mid-flight
            if response.status_code == 401:
                self._access_token = None
                token = await self._ensure_token()
                headers = self._auth_headers(token)
                await self._pacer.wait()
                response = await self._get_http().request(method, url, headers=headers, **kwargs)
                self._note_limits(response)
        except httpx.HTTPError:
            raise DigiKeyError("DigiKey API request failed (network/connection error)")

        if response.status_code in (403, 429):
            paused = self._quota.paused_error() if self._quota else None
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
        product_number = product_number.strip()
        if not product_number:
            return {"error": "Give a DigiKey or manufacturer part number."}
        cache_key = f"digikey:{product_number}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            stats.usage.record_distributor("digikey", "cached")
            return cached

        # Check daily quota (after cache so cache hits don't count)
        if self._quota:
            quota_error = self._quota.check(caller)
            if quota_error:
                stats.usage.record_distributor("digikey", "rate_limited")
                return quota_error
        stats.usage.record_distributor("digikey", "sent")

        # URL-encode to prevent path traversal or special chars altering the URL
        safe_pn = quote(product_number, safe='')
        try:
            data = await self._request("GET", f"/search/{safe_pn}/productdetails")
        except DigiKeyRateLimited as e:
            return {"error": str(e)}
        except DigiKeyNotFound:
            data = {}
        product = data.get("Product", {})
        products = [product] if product else []

        if not products and product_number.isdigit():
            if self._quota:
                quota_error = self._quota.check(caller)
                if quota_error:
                    stats.usage.record_distributor("digikey", "rate_limited")
                    return quota_error
            stats.usage.record_distributor("digikey", "sent")
            try:
                data = await self._request("POST", "/search/keyword", json={
                    "Keywords": product_number, "Limit": 50, "Offset": 0,
                })
            except DigiKeyRateLimited as e:
                return {"error": str(e)}
            except DigiKeyNotFound:
                data = {}

            seen = set()
            for candidate in (data.get("ExactMatches") or []) + (data.get("Products") or []):
                mpn = candidate.get("ManufacturerProductNumber") or ""
                if mpn.strip().casefold() != product_number.casefold():
                    continue
                key = ((candidate.get("Manufacturer") or {}).get("Name", ""), mpn)
                if key not in seen:
                    seen.add(key)
                    products.append(candidate)
            stats.usage.record_distributor("digikey", "retry_found" if products else "retry_missed")

        if not products:
            # Cached too, so asking again for a wrong or partial number costs no request
            not_found = {"error": f"Part not found: {product_number}"}
            if product_number.isdigit():
                not_found["hint"] = ("DigiKey found no exact match for this all-digit number by lookup or "
                                     "keyword search. If you have it, try the DigiKey part number "
                                     "(usually ending in -ND).")
            self._cache.set(cache_key, not_found, ttl=DIGIKEY_NOT_FOUND_TTL)
            return not_found

        result = {
            "results": [_normalize_product(p, product_number) for p in products],
            "total": len(products),
        }
        self._cache.set(cache_key, result)
        return result

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http:
            await self._http.aclose()
            self._http = None
