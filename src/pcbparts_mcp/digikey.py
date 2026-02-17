"""DigiKey Product Information API v4 client."""

import asyncio
import logging
import time
from typing import Any
from urllib.parse import quote

import httpx

from .cache import TTLCache
from .config import (
    DIGIKEY_CLIENT_ID,
    DIGIKEY_CLIENT_SECRET,
    DIGIKEY_BASE_URL,
    DIGIKEY_TOKEN_URL,
    DIGIKEY_CONCURRENT_LIMIT,
    DIGIKEY_CACHE_TTL,
    DIGIKEY_LOCALE_SITE,
    DIGIKEY_LOCALE_LANGUAGE,
    DIGIKEY_LOCALE_CURRENCY,
)

logger = logging.getLogger(__name__)


def _normalize_product(product: dict[str, Any]) -> dict[str, Any]:
    """Normalize a DigiKey Product object into our standard format."""
    desc = product.get("Description", {})
    manufacturer = product.get("Manufacturer", {})
    category = product.get("Category", {})
    status = product.get("ProductStatus", {})
    classifications = product.get("Classifications", {})

    # Get best pricing from first variation
    price_breaks = []
    variations = product.get("ProductVariations", [])
    stock = product.get("QuantityAvailable", 0)
    min_qty = 1

    if variations:
        # Use first variation for pricing
        first_var = variations[0]
        min_qty = first_var.get("MinimumOrderQuantity", 1) or 1
        for sp in first_var.get("StandardPricing", []):
            price_breaks.append({
                "qty": sp.get("BreakQuantity", 0),
                "price": sp.get("UnitPrice", 0),
            })

    unit_price = product.get("UnitPrice") or (price_breaks[0]["price"] if price_breaks else None)

    # Get DigiKey part number from first variation
    digikey_pn = ""
    if variations:
        digikey_pn = variations[0].get("DigiKeyProductNumber", "")

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

    return {
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


class DigiKeyClient:
    """Async client for DigiKey Product Information API v4 with OAuth2."""

    def __init__(
        self,
        client_id: str = DIGIKEY_CLIENT_ID,
        client_secret: str = DIGIKEY_CLIENT_SECRET,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._http: httpx.AsyncClient | None = None
        self._semaphore: asyncio.Semaphore | None = None
        # OAuth2 token state
        self._access_token: str | None = None
        self._token_expires_at: float = 0
        self._token_lock: asyncio.Lock | None = None
        self._cache = TTLCache(ttl=DIGIKEY_CACHE_TTL)

    def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=15.0)
        return self._http

    def _get_semaphore(self) -> asyncio.Semaphore:
        # Safe in single-threaded asyncio: no await between None check and assignment
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(DIGIKEY_CONCURRENT_LIMIT)
        return self._semaphore

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

            response = await self._get_http().post(
                DIGIKEY_TOKEN_URL,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "client_credentials",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            data = response.json()

            # Check for OAuth error responses (some providers return 200 with error)
            if "error" in data:
                error_desc = data.get("error_description", data["error"])
                raise ValueError(f"DigiKey OAuth error: {error_desc}")

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

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make an authenticated request to DigiKey API."""
        token = await self._ensure_token()
        headers = self._auth_headers(token)
        url = f"{DIGIKEY_BASE_URL}{path}"

        async with self._get_semaphore():
            response = await self._get_http().request(method, url, headers=headers, **kwargs)

        # Handle token expiration mid-flight (retry outside semaphore)
        if response.status_code == 401:
            self._access_token = None
            token = await self._ensure_token()
            headers = self._auth_headers(token)
            async with self._get_semaphore():
                response = await self._get_http().request(method, url, headers=headers, **kwargs)

        response.raise_for_status()
        return response.json()

    async def search(
        self,
        keywords: str,
        limit: int = 20,
        offset: int = 0,
        in_stock_only: bool = False,
        manufacturer: str | None = None,
    ) -> dict[str, Any]:
        """Search DigiKey by keywords.

        Args:
            keywords: Search terms
            limit: Results per page (max 50)
            offset: Pagination offset
            in_stock_only: Only show in-stock parts
            manufacturer: Filter by manufacturer name (note: DigiKey uses IDs,
                         so this is passed as a keyword modifier)

        Returns:
            Dict with results, total, offset
        """
        limit = max(1, min(limit, 50))

        body: dict[str, Any] = {
            "Keywords": keywords,
            "Limit": limit,
            "Offset": offset,
        }

        filter_options: dict[str, Any] = {}
        if in_stock_only:
            filter_options["SearchOptions"] = ["InStock"]
        if filter_options:
            body["FilterOptionsRequest"] = filter_options

        # If manufacturer specified, append to keywords since DigiKey
        # manufacturer filter requires numeric IDs we don't have
        if manufacturer:
            body["Keywords"] = f"{keywords} {manufacturer}"

        data = await self._request("POST", "/search/keyword", json=body)
        products = data.get("Products", [])
        total = data.get("ProductsCount", 0)

        # Also include exact matches
        exact = data.get("ExactMatches", [])
        all_products = exact + products

        # Deduplicate by MPN (skip dedup for empty MPNs)
        seen = set()
        unique = []
        for p in all_products:
            mpn = p.get("ManufacturerProductNumber", "")
            if not mpn or mpn not in seen:
                if mpn:
                    seen.add(mpn)
                unique.append(p)

        return {
            "results": [_normalize_product(p) for p in unique[:limit]],
            "total": total,
            "offset": offset,
        }

    async def get_part(self, product_number: str) -> dict[str, Any]:
        """Look up a part by DigiKey PN or manufacturer PN.

        Args:
            product_number: DigiKey part number or manufacturer part number

        Returns:
            Dict with results list and total (consistent with Mouser format)
        """
        cache_key = f"digikey:{product_number.strip()}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # URL-encode to prevent path traversal or special chars altering the URL
        safe_pn = quote(product_number, safe='')
        data = await self._request("GET", f"/search/{safe_pn}/productdetails")
        product = data.get("Product", {})

        if not product:
            return {"error": f"Part not found: {product_number}"}

        result = {
            "results": [_normalize_product(product)],
            "total": 1,
        }
        self._cache.set(cache_key, result)
        return result

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http:
            await self._http.aclose()
            self._http = None
