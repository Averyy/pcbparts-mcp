"""JLCPCB API client for searching electronic components."""

import asyncio
import random
from typing import Any, Literal

from curl_cffi import requests as curl_requests

from .config import (
    get_jlcpcb_headers,
    JLCPCB_SEARCH_URL,
    JLCPCB_DETAIL_URL,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    DEFAULT_MIN_STOCK,
    MAX_ALTERNATIVES,
)
from .key_attributes import KEY_ATTRIBUTES
from .manufacturer_aliases import MANUFACTURER_ALIASES

# Browser fingerprints for TLS impersonation
BROWSER_FINGERPRINTS = ["chrome131", "chrome133a", "chrome136", "chrome142"]


class JLCPCBClient:
    """Async client for JLCPCB component search API with browser impersonation."""

    def __init__(self):
        self._sessions: list[curl_requests.AsyncSession] = []
        self._session_index = 0
        # Category cache - lazily populated from API or set externally
        self._categories: list[dict[str, Any]] = []
        self._category_map: dict[int, dict[str, Any]] = {}  # id -> category
        self._subcategory_map: dict[int, tuple[int, dict[str, Any]]] = {}  # id -> (parent_id, subcategory)
        self._subcategory_name_map: dict[str, int] = {}  # name -> subcategory_id

    def set_categories(self, categories: list[dict[str, Any]]) -> None:
        """Set pre-loaded categories to avoid redundant API calls.

        Call this after fetch_categories() to share the cache.
        """
        self._categories = categories
        self._category_map.clear()
        self._subcategory_map.clear()
        self._subcategory_name_map.clear()

        for cat in categories:
            self._category_map[cat["id"]] = cat
            for sub in cat.get("subcategories", []):
                self._subcategory_map[sub["id"]] = (cat["id"], sub)
                self._subcategory_name_map[sub["name"]] = sub["id"]

    def _get_browser(self) -> str:
        """Get a random browser fingerprint."""
        return random.choice(BROWSER_FINGERPRINTS)

    async def _get_session(self) -> curl_requests.AsyncSession:
        """Get or create an HTTP session with browser impersonation.

        Uses a pool of sessions to avoid rate limiting and support concurrency.
        """
        # Create initial session if needed
        if not self._sessions:
            self._sessions.append(curl_requests.AsyncSession(
                impersonate=self._get_browser(),
                timeout=REQUEST_TIMEOUT,
            ))

        # Round-robin through sessions
        session = self._sessions[self._session_index % len(self._sessions)]
        self._session_index += 1

        return session

    async def _new_session(self) -> curl_requests.AsyncSession:
        """Create a new session with a fresh browser fingerprint."""
        session = curl_requests.AsyncSession(
            impersonate=self._get_browser(),
            timeout=REQUEST_TIMEOUT,
        )
        self._sessions.append(session)
        return session

    async def close(self):
        """Close all HTTP sessions."""
        for session in self._sessions:
            await session.close()
        self._sessions = []

    async def _ensure_categories(self) -> None:
        """Ensure categories are loaded (lazy initialization)."""
        if self._categories:
            return

        self._categories = await self.fetch_categories()

        # Build lookup maps
        for cat in self._categories:
            self._category_map[cat["id"]] = cat
            for sub in cat.get("subcategories", []):
                self._subcategory_map[sub["id"]] = (cat["id"], sub)
                self._subcategory_name_map[sub["name"]] = sub["id"]

    def _get_category(self, category_id: int) -> dict[str, Any] | None:
        """Get category by ID from cache."""
        return self._category_map.get(category_id)

    def _get_subcategory(self, subcategory_id: int) -> tuple[int, dict[str, Any]] | None:
        """Get subcategory by ID from cache. Returns (parent_id, subcategory) or None."""
        return self._subcategory_map.get(subcategory_id)

    def get_subcategory_id_by_name(self, name: str) -> int | None:
        """Get subcategory ID by name from cache. O(1) lookup."""
        return self._subcategory_name_map.get(name)

    # Common abbreviations mapped to category name substrings
    # These are resolved dynamically against fetched categories at runtime
    _ABBREVIATION_TO_CATEGORY: dict[str, str] = {
        "led": "Optoelectronics",
        "leds": "Optoelectronics",
        "esd": "Circuit Protection",
        "adc": "Data Acquisition",
        "adcs": "Data Acquisition",
        "bjt": "Transistors",
        "bjts": "Transistors",
        "fet": "Transistors",
        "fets": "Transistors",
    }

    # Sort mode mapping: user-friendly name -> API value
    _SORT_MODE_MAP: dict[str, str] = {
        "quantity": "STOCK_SORT",
        "price": "PRICE_SORT",
    }

    def _resolve_manufacturer(self, name: str) -> str:
        """Resolve manufacturer alias to full name.

        If the name matches an alias (case-insensitive), returns the full name.
        Otherwise returns the original name unchanged.
        """
        return MANUFACTURER_ALIASES.get(name.lower(), name)

    def _resolve_manufacturers(self, names: list[str]) -> list[str]:
        """Resolve a list of manufacturer names/aliases."""
        return [self._resolve_manufacturer(name) for name in names]

    def _resolve_abbreviation(self, abbrev: str) -> int | None:
        """Resolve an abbreviation to a category ID using the live category cache."""
        category_name = self._ABBREVIATION_TO_CATEGORY.get(abbrev)
        if not category_name:
            return None

        # Find category by name (case-insensitive, partial match)
        category_name_lower = category_name.lower()
        for cat in self._categories:
            if category_name_lower in cat["name"].lower():
                return cat["id"]
        return None

    def _match_category_by_name(self, query: str) -> int | None:
        """Match a query string against category names.

        Returns category_id if query matches a category name (case-insensitive).
        Handles common variations like singular/plural ("capacitor" -> "Capacitors"),
        and common abbreviations like "LED" -> Optoelectronics.
        """
        if not query or not self._categories:
            return None

        query_lower = query.lower().strip()

        # Check explicit abbreviation mappings first (resolved dynamically)
        abbrev_match = self._resolve_abbreviation(query_lower)
        if abbrev_match is not None:
            return abbrev_match

        for cat in self._categories:
            cat_name = cat["name"].lower()
            # Exact match
            if query_lower == cat_name:
                return cat["id"]
            # Query is singular form of category (e.g., "capacitor" matches "capacitors")
            if cat_name.endswith("s") and query_lower == cat_name[:-1]:
                return cat["id"]
            # Query matches start of category name (e.g., "resistor" matches "resistors")
            if cat_name.startswith(query_lower) and len(query_lower) >= 4:
                return cat["id"]

        return None

    async def _request(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute request with retry logic and browser impersonation."""
        session = await self._get_session()
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                # Fresh randomized headers for each request
                headers = get_jlcpcb_headers()
                response = await session.post(
                    url,
                    json=params,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                # Check for API-level errors
                if data.get("code") != 200:
                    error_msg = data.get("message", "Unknown API error")
                    raise ValueError(f"JLCPCB API error: {error_msg}")

                return data
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    # On retry, create a new session with a fresh fingerprint
                    session = await self._new_session()
                    await asyncio.sleep(0.3 * (attempt + 1))
                else:
                    raise

        raise last_error  # type: ignore

    def _build_search_params(
        self,
        query: str | None = None,
        category_id: int | None = None,
        subcategory_id: int | None = None,
        min_stock: int | None = None,
        library_type: str | None = None,
        package: str | None = None,
        manufacturer: str | None = None,
        packages: list[str] | None = None,
        manufacturers: list[str] | None = None,
        sort_by: Literal["quantity", "price"] | None = None,
        page: int = 1,
        limit: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        """Build search request parameters."""
        # Enforce valid limit range (1 to MAX_PAGE_SIZE)
        effective_limit = max(1, min(limit, MAX_PAGE_SIZE))
        params: dict[str, Any] = {
            "currentPage": page,
            "pageSize": effective_limit,
            "searchSource": "search",
        }

        # Sorting: quantity (highest first), price (cheapest first)
        if sort_by and sort_by in self._SORT_MODE_MAP:
            params["sortMode"] = self._SORT_MODE_MAP[sort_by]
            params["sortASC"] = "ASC" if sort_by == "price" else "DESC"

        # Keyword search
        if query:
            params["keyword"] = query

        # Category filtering (requires searchType: 3)
        if category_id:
            cat = self._get_category(category_id)
            if cat:
                params["firstSortId"] = category_id
                params["firstSortName"] = cat["name"]
                params["searchType"] = 3

        # Subcategory filtering
        if subcategory_id:
            result = self._get_subcategory(subcategory_id)
            if result:
                parent_cat_id, sub = result
                # Ensure parent category is set
                if not category_id:
                    parent_cat = self._get_category(parent_cat_id)
                    if parent_cat:
                        params["firstSortId"] = parent_cat_id
                        params["firstSortName"] = parent_cat["name"]
                        params["searchType"] = 3
                params["secondSortId"] = subcategory_id
                params["secondSortName"] = sub["name"]

        # Stock filtering
        if min_stock is not None:
            params["startStockNumber"] = min_stock

        # Library type filtering
        if library_type:
            if library_type == "basic":
                params["componentLibraryType"] = "base"
            elif library_type == "extended":
                params["componentLibraryType"] = "expand"
            elif library_type == "preferred":
                params["preferredComponentFlag"] = True
            elif library_type == "no_fee":
                # Combines basic + preferred in single API call
                params["componentLibraryType"] = "base"
                params["preferredComponentFlag"] = True

        # Package filtering (single or multi-select)
        if packages:
            # Multi-select: OR filter across multiple packages
            params["componentSpecificationList"] = packages
        elif package:
            params["componentSpecification"] = package

        # Manufacturer filtering (single or multi-select) with alias resolution
        if manufacturers:
            # Multi-select: OR filter across multiple manufacturers
            params["componentBrandList"] = self._resolve_manufacturers(manufacturers)
        elif manufacturer:
            params["componentBrand"] = self._resolve_manufacturer(manufacturer)

        return params

    def _transform_part(self, item: dict[str, Any], slim: bool = True) -> dict[str, Any]:
        """Transform API response to our format."""
        # Get price from first tier and volume price (10+) from second tier
        prices = item.get("componentPrices", [])
        price = prices[0]["productPrice"] if prices else None
        price_10 = prices[1]["productPrice"] if len(prices) > 1 else None

        # Map library type
        lib_type = item.get("componentLibraryType", "")
        if lib_type == "base":
            library_type = "basic"
        elif lib_type == "expand":
            library_type = "extended"
        else:
            library_type = lib_type

        # Note: API returns firstSortName as subcategory, secondSortName as category
        stock = item.get("stockCount")
        result: dict[str, Any] = {
            "lcsc": item.get("componentCode"),
            "model": item.get("componentModelEn"),
            "manufacturer": item.get("componentBrandEn"),
            "package": item.get("componentSpecificationEn"),
            "stock": stock,
            "price": round(price, 4) if price else None,
            "price_10": round(price_10, 4) if price_10 else None,
            "library_type": library_type,
            "preferred": item.get("preferredComponentFlag", False),
            "category": item.get("secondSortName"),  # Primary category
            "subcategory": item.get("firstSortName"),  # Subcategory
        }

        # Include key specs in slim mode
        # Use subcategory-specific key attributes if available, otherwise top 5
        attrs = item.get("attributes", [])
        if attrs:
            subcategory = item.get("firstSortName")  # API returns subcategory as firstSortName
            key_attr_names = KEY_ATTRIBUTES.get(subcategory)  # Returns None if not found

            if key_attr_names is not None:
                # Filter to only the key attributes, preserving defined order
                # Empty list means intentionally show no key_specs
                attr_map = {
                    a.get("attribute_name_en"): a.get("attribute_value_name")
                    for a in attrs
                    if a.get("attribute_name_en")
                }
                result["key_specs"] = {
                    name: attr_map[name]
                    for name in key_attr_names
                    if name in attr_map
                }
            else:
                # Fallback: first 5 attributes for unknown subcategories
                result["key_specs"] = {
                    a.get("attribute_name_en"): a.get("attribute_value_name")
                    for a in attrs[:5]
                    if a.get("attribute_name_en")
                }
        else:
            # No attributes available
            result["key_specs"] = {}

        if not slim:
            # Full details
            result["description"] = item.get("describe")
            result["min_order"] = item.get("minPurchaseNum")
            result["reel_qty"] = item.get("encapsulationNumber")
            result["datasheet"] = item.get("dataManualUrl")
            result["lcsc_url"] = item.get("lcscGoodsUrl")

            # Transform all prices
            if prices:
                result["prices"] = [
                    {
                        "qty": f"{p['startNumber']}+",
                        "price": round(p["productPrice"], 4),
                    }
                    for p in prices
                ]

            # Full attributes list (beyond key_specs)
            if attrs:
                result["attributes"] = [
                    {
                        "name": a.get("attribute_name_en"),
                        "value": a.get("attribute_value_name"),
                    }
                    for a in attrs
                    if a.get("attribute_name_en")
                ]

        return result

    async def search(
        self,
        query: str | None = None,
        category_id: int | None = None,
        subcategory_id: int | None = None,
        min_stock: int = DEFAULT_MIN_STOCK,
        library_type: str | None = None,
        package: str | None = None,
        manufacturer: str | None = None,
        packages: list[str] | None = None,
        manufacturers: list[str] | None = None,
        sort_by: Literal["quantity", "price"] | None = None,
        page: int = 1,
        limit: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        """Search for components."""
        # Load categories if filtering by category/subcategory, or if we have a query
        # that might match a category name
        if category_id or subcategory_id or query:
            await self._ensure_categories()

        # Auto-match query to category if no category specified
        # e.g., "capacitor" -> category_id=2 (Capacitors)
        if query and not category_id and not subcategory_id:
            matched_category = self._match_category_by_name(query)
            if matched_category:
                category_id = matched_category
                query = None  # Use category filter instead of keyword

        # Build and execute search
        params = self._build_search_params(
            query=query,
            category_id=category_id,
            subcategory_id=subcategory_id,
            min_stock=min_stock,
            library_type=library_type,
            package=package,
            manufacturer=manufacturer,
            packages=packages,
            manufacturers=manufacturers,
            sort_by=sort_by,
            page=page,
            limit=limit,
        )

        response = await self._request(JLCPCB_SEARCH_URL, params)
        data = response.get("data") or {}
        page_info = data.get("componentPageInfo") or {}

        items = page_info.get("list") or []
        total = page_info.get("total") or 0

        results = [self._transform_part(item, slim=True) for item in items]

        # Calculate total pages
        total_pages = (total + limit - 1) // limit if limit > 0 else 0

        return {
            "results": results,
            "page": page,
            "per_page": limit,
            "total": total,
            "total_pages": total_pages,
            "has_more": page * limit < total,
        }

    async def get_part(self, lcsc: str) -> dict[str, Any] | None:
        """Get full details for a specific part."""
        # Normalize LCSC code to uppercase (e.g., c20917 -> C20917)
        lcsc = lcsc.strip().upper()

        # Validate LCSC code format (C followed by digits)
        if not lcsc or not lcsc.startswith("C") or not lcsc[1:].isdigit():
            return None

        # Search for the exact part code
        params = {
            "keyword": lcsc,
            "currentPage": 1,
            "pageSize": 10,
            "searchSource": "search",
        }

        response = await self._request(JLCPCB_SEARCH_URL, params)
        data = response.get("data", {})
        items = data.get("componentPageInfo", {}).get("list", [])

        # Find exact match
        for item in items:
            if item.get("componentCode") == lcsc:
                return self._transform_part(item, slim=False)

        return None

    async def find_alternatives(
        self,
        lcsc: str,
        min_stock: int = 100,
        same_package: bool = False,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Find alternative parts similar to a given component.

        Searches the same subcategory for parts with better availability.

        Args:
            lcsc: LCSC part code to find alternatives for (e.g., "C2557")
            min_stock: Minimum stock for alternatives (default: 100)
            same_package: If True, only return parts with the same package size
            limit: Maximum alternatives to return (default: 10, max: 50)

        Returns:
            Dict with original part info and list of alternatives sorted by stock.
        """
        # Validate and cap limit
        effective_limit = max(1, min(limit, MAX_ALTERNATIVES))
        effective_min_stock = max(0, min_stock)

        # Get the original part details
        original = await self.get_part(lcsc)
        if not original:
            return {"error": f"Part {lcsc.strip().upper()} not found"}

        # Build search params
        search_params: dict[str, Any] = {
            "min_stock": effective_min_stock,
            "sort_by": "quantity",  # Best availability first
            "limit": effective_limit + 5,  # Get extra to filter out original
        }

        # Find subcategory ID using O(1) lookup
        subcategory_name = original.get("subcategory")
        subcategory_id = None
        warning = None
        if subcategory_name:
            subcategory_id = self.get_subcategory_id_by_name(subcategory_name)
            if not subcategory_id:
                warning = f"Subcategory '{subcategory_name}' not found in cache, searching all parts"

        if subcategory_id:
            search_params["subcategory_id"] = subcategory_id

        # Filter by same package if requested
        if same_package and original.get("package"):
            search_params["package"] = original["package"]

        result = await self.search(**search_params)

        # Filter out the original part (normalize LCSC code for comparison)
        original_lcsc = original.get("lcsc", "").upper()
        alternatives = [
            p for p in result.get("results", [])
            if p.get("lcsc", "").upper() != original_lcsc
        ][:effective_limit]

        response: dict[str, Any] = {
            "original": {
                "lcsc": original.get("lcsc"),
                "model": original.get("model"),
                "manufacturer": original.get("manufacturer"),
                "package": original.get("package"),
                "stock": original.get("stock"),
                "price": original.get("price"),
                "subcategory": original.get("subcategory"),
                "key_specs": original.get("key_specs"),
            },
            "alternatives": alternatives,
            "search_criteria": {
                "subcategory": subcategory_name,
                "min_stock": effective_min_stock,
                "same_package": same_package,
            },
        }

        if warning:
            response["warning"] = warning

        return response

    async def fetch_categories(self) -> list[dict[str, Any]]:
        """Fetch current categories and subcategories from JLCPCB API.

        Returns a list of categories, each with:
        - id: Category ID (componentSortKeyId)
        - name: Category name
        - count: Number of components
        - subcategories: List of subcategories with same structure
        """
        # Use searchType=3 to get category data in response
        params = {
            "currentPage": 1,
            "pageSize": 1,
            "searchSource": "search",
            "searchType": 3,
        }

        response = await self._request(JLCPCB_SEARCH_URL, params)
        data = response.get("data", {})
        sort_list = data.get("sortAndCountVoList", [])

        if not sort_list:
            return []

        categories = []
        for cat in sort_list:
            subcategories = []
            for sub in cat.get("childSortList") or []:
                subcategories.append({
                    "id": sub.get("componentSortKeyId"),
                    "name": sub.get("sortName"),
                    "count": sub.get("componentCount", 0),
                })

            categories.append({
                "id": cat.get("componentSortKeyId"),
                "name": cat.get("sortName"),
                "count": cat.get("componentCount", 0),
                "subcategories": subcategories,
            })

        return categories
