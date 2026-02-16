"""Mouser Search API v2 client."""

import asyncio
import logging
import re
from typing import Any

import httpx

from .cache import TTLCache
from .config import (
    MOUSER_API_KEY,
    MOUSER_BASE_URL,
    MOUSER_CONCURRENT_LIMIT,
    MOUSER_CACHE_TTL,
)

logger = logging.getLogger(__name__)

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

    lifecycle = None
    if part.get("LifecycleStatus"):
        lifecycle = part["LifecycleStatus"]
    elif part.get("IsDiscontinued") == "Yes":
        lifecycle = "Discontinued"
    else:
        lifecycle = "Active"

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
        "parameters": parameters,
        "min_qty": int(part.get("Min", 1) or 1),
        "currency": price_breaks[0]["currency"] if price_breaks else "USD",
    }


class MouserClient:
    """Async client for Mouser Search API v2."""

    def __init__(self, api_key: str = MOUSER_API_KEY):
        self._api_key = api_key
        self._client: httpx.AsyncClient | None = None
        self._semaphore: asyncio.Semaphore | None = None
        self._cache = TTLCache(ttl=MOUSER_CACHE_TTL)

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    def _get_semaphore(self) -> asyncio.Semaphore:
        # Safe in single-threaded asyncio: no await between None check and assignment
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(MOUSER_CONCURRENT_LIMIT)
        return self._semaphore

    async def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        """Make an authenticated POST request to Mouser API.

        Note: Mouser API v2 requires apiKey as a query parameter (their design).
        """
        url = f"{MOUSER_BASE_URL}{path}?apiKey={self._api_key}"
        async with self._get_semaphore():
            response = await self._get_client().post(url, json=body)
            # Catch HTTP errors to avoid leaking the API key (embedded in URL) into logs
            if response.status_code >= 400:
                raise ValueError(f"Mouser API returned HTTP {response.status_code}")
            data = response.json()

        # Check for API errors
        errors = data.get("Errors", [])
        if errors:
            msg = errors[0].get("Message", "Unknown Mouser API error")
            raise ValueError(f"Mouser API error: {msg}")

        return data

    async def search(
        self,
        keyword: str,
        manufacturer: str | None = None,
        in_stock_only: bool = False,
        records: int = 20,
        page: int = 1,
    ) -> dict[str, Any]:
        """Search Mouser by keyword.

        Args:
            keyword: Search terms
            manufacturer: Filter by manufacturer name
            in_stock_only: Only show in-stock parts
            records: Results per page (max 50)
            page: Page number (1-based)

        Returns:
            Dict with results, total, page
        """
        records = max(1, min(records, 50))

        search_options = "None"
        if in_stock_only:
            search_options = "InStock"

        # Use manufacturer-filtered endpoint only when manufacturer is specified;
        # the /keywordandmanufacturer endpoint requires a non-empty manufacturerName
        if manufacturer:
            body = {
                "SearchByKeywordMfrNameRequest": {
                    "keyword": keyword,
                    "manufacturerName": manufacturer,
                    "records": records,
                    "pageNumber": page,
                    "searchOptions": search_options,
                    "searchWithYourSignUpLanguage": "false",
                }
            }
            data = await self._post("/search/keywordandmanufacturer", body)
        else:
            body = {
                "SearchByKeywordRequest": {
                    "keyword": keyword,
                    "records": records,
                    "pageNumber": page,
                    "searchOptions": search_options,
                    "searchWithYourSignUpLanguage": "false",
                }
            }
            data = await self._post("/search/keyword", body)
        search_results = data.get("SearchResults", {})
        parts = search_results.get("Parts", [])
        total = search_results.get("NumberOfResult", 0)

        return {
            "results": [_normalize_part(p) for p in parts],
            "total": total,
            "page": page,
        }

    async def get_part(self, part_number: str) -> dict[str, Any]:
        """Look up part(s) by Mouser part number or MPN.

        Args:
            part_number: Mouser PN or MPN. Pipe-delimited for batch (up to 10).

        Returns:
            Dict with results list
        """
        # Check cache for single lookups
        cache_key = f"mouser:{part_number.strip()}"
        if "|" not in part_number:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        body = {
            "SearchByPartRequest": {
                "mouserPartNumber": part_number,
                "partSearchOptions": "None",
            }
        }

        data = await self._post("/search/partnumber", body)
        search_results = data.get("SearchResults", {})
        parts = search_results.get("Parts", [])

        result = {
            "results": [_normalize_part(p) for p in parts],
            "total": len(parts),
        }

        # Cache single lookups
        if "|" not in part_number:
            self._cache.set(cache_key, result)

        return result

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
