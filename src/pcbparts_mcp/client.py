"""JLCPCB API client for searching electronic components."""

import asyncio
import heapq
import logging
import re
import time
from typing import Any, Literal
from urllib.parse import quote

import wafer
from wafer import (
    ChallengeDetected,
    ConnectionFailed,
    EmptyResponse,
    RateLimited,
    WaferHTTPError,
    WaferTimeout,
)

from .config import (
    JLCPCB_SEARCH_URL,
    JLCPCB_DETAIL_URL,
    EASYEDA_COMPONENT_URL,
    EASYEDA_SYMBOL_URL,
    EASYEDA_CACHE_TTL,
    EASYEDA_ERROR_CACHE_TTL,
    EASYEDA_REQUEST_TIMEOUT,
    EASYEDA_CACHE_MAX_SIZE,
    EASYEDA_CONCURRENT_LIMIT,
    EASYEDA_RATE_LIMIT,
    EASYEDA_RATE_JITTER,
    JLCPCB_CONCURRENT_LIMIT,
    JLCPCB_RATE_LIMIT,
    JLCPCB_RATE_JITTER,
    JLCPCB_MAX_ROTATIONS,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    DEFAULT_MIN_STOCK,
    MAX_ALTERNATIVES,
    PART_CACHE_TTL,
    PART_CACHE_MAX_SIZE,
)
from .subcategory_aliases import SUBCATEGORY_ALIASES, resolve_subcategory_name as _resolve_subcategory_name
from .manufacturer_aliases import KNOWN_MANUFACTURERS, MANUFACTURER_ALIASES
from .mounting import detect_mounting_type
from .alternatives import (
    COMPATIBILITY_RULES,
    is_compatible_alternative,
    verify_primary_spec_match,
    score_alternative,
    build_response,
    build_unsupported_response,
)

logger = logging.getLogger(__name__)

# UUID format pattern for EasyEDA symbols (32-char hex)
_UUID_PATTERN = re.compile(r'^[0-9a-f]{32}$', re.IGNORECASE)


def _normalize_manufacturer_name(name: str) -> str:
    """Normalize manufacturer name for matching: lowercase, remove punctuation, collapse spaces."""
    normalized = re.sub(r'[.,\-\(\)&]', ' ', name.lower())  # Replace punctuation with space
    return re.sub(r'\s+', ' ', normalized).strip()  # Collapse multiple spaces


def _normalize_package_for_matching(pkg: str) -> str:
    """Normalize package name for fuzzy matching.

    Strips height suffixes from tantalum/electrolytic capacitor packages.
    These have identical footprints but different heights.

    Examples:
        'CASE-B-3528-21(mm)' -> 'CASE-B-3528'
        'CASE-B-3528-19(mm)' -> 'CASE-B-3528'
        'CASE-A-3216-18(mm)' -> 'CASE-A-3216'
        'SOT-23-3L' -> 'SOT-23-3L' (no change)
        'QFN-24-EP(4x4)' -> 'QFN-24-EP(4x4)' (no change)
    """
    # Only normalize known tantalum/electrolytic case packages: CASE-A through CASE-X
    # Pattern: CASE-{letter}-{dims}-{height}(mm) -> CASE-{letter}-{dims}
    # This is very specific to avoid false matches on other package types
    pkg = re.sub(r"^(CASE-[A-Z]-\d{4})-\d{1,2}\(mm\)$", r"\1", pkg)
    return pkg

# Build case-insensitive lookup for exact manufacturer names
# This allows "molex" to match "MOLEX" without explicit aliases
_MANUFACTURER_EXACT_NAMES: dict[str, str] = {name.lower(): name for name in KNOWN_MANUFACTURERS}

# Build normalized lookups (without punctuation) for fuzzy matching
_MANUFACTURER_ALIASES_NORMALIZED: dict[str, str] = {
    _normalize_manufacturer_name(k): v for k, v in MANUFACTURER_ALIASES.items()
}
_MANUFACTURER_EXACT_NORMALIZED: dict[str, str] = {
    _normalize_manufacturer_name(name): name for name in KNOWN_MANUFACTURERS
}

class JLCPCBClient:
    """Async client for JLCPCB component search API with anti-detection via wafer."""

    def __init__(self):
        self._jlcpcb_session: wafer.AsyncSession | None = None
        self._easyeda_session: wafer.AsyncSession | None = None
        # Category cache - lazily populated from API or set externally
        self._categories: list[dict[str, Any]] = []
        self._category_map: dict[int, dict[str, Any]] = {}  # id -> category
        self._category_name_map: dict[str, int] = {}  # lowercase name -> category_id (O(1) lookup)
        self._subcategory_map: dict[int, tuple[int, dict[str, Any]]] = {}  # id -> (parent_id, subcategory)
        self._subcategory_name_map: dict[str, int] = {}  # name -> subcategory_id
        # EasyEDA footprint cache: lcsc -> (timestamp, result_dict, is_error)
        self._easyeda_cache: dict[str, tuple[float, dict[str, Any], bool]] = {}
        # EasyEDA component cache: uuid -> (timestamp, result_dict, is_error)
        self._easyeda_component_cache: dict[str, tuple[float, dict[str, Any] | ValueError, bool]] = {}
        # Part details cache: lcsc -> (timestamp, result_dict | None)
        self._part_cache: dict[str, tuple[float, dict[str, Any] | None]] = {}
        # Locks for thread-safe cache access during concurrent async operations
        self._easyeda_cache_lock: asyncio.Lock | None = None
        self._easyeda_component_cache_lock: asyncio.Lock | None = None
        self._part_cache_lock: asyncio.Lock | None = None
        # Semaphore to limit concurrent EasyEDA requests (avoid rate limiting)
        self._easyeda_semaphore: asyncio.Semaphore | None = None
        # Semaphore to limit concurrent JLCPCB requests (prevents IP blocking at scale)
        self._jlcpcb_semaphore: asyncio.Semaphore | None = None

    def _get_easyeda_cache_lock(self) -> asyncio.Lock:
        """Lazy init lock (must be created in async context)."""
        if self._easyeda_cache_lock is None:
            self._easyeda_cache_lock = asyncio.Lock()
        return self._easyeda_cache_lock

    def _get_easyeda_component_cache_lock(self) -> asyncio.Lock:
        """Lazy init lock (must be created in async context)."""
        if self._easyeda_component_cache_lock is None:
            self._easyeda_component_cache_lock = asyncio.Lock()
        return self._easyeda_component_cache_lock

    def _get_part_cache_lock(self) -> asyncio.Lock:
        """Lazy init lock (must be created in async context)."""
        if self._part_cache_lock is None:
            self._part_cache_lock = asyncio.Lock()
        return self._part_cache_lock

    def set_categories(self, categories: list[dict[str, Any]]) -> None:
        """Set pre-loaded categories to avoid redundant API calls.

        Call this after fetch_categories() to share the cache.
        """
        self._categories = categories
        self._category_map.clear()
        self._category_name_map.clear()
        self._subcategory_map.clear()
        self._subcategory_name_map.clear()

        for cat in categories:
            self._category_map[cat["id"]] = cat
            self._build_category_name_mappings(cat)
            for sub in cat.get("subcategories", []):
                self._subcategory_map[sub["id"]] = (cat["id"], sub)
                # Store lowercase for case-insensitive matching
                self._subcategory_name_map[sub["name"].lower()] = sub["id"]

    def _build_category_name_mappings(self, cat: dict[str, Any]) -> None:
        """Build O(1) name lookup mappings for a category.

        Handles case-insensitive matching and simple singular forms.
        Only adds singular mapping for simple -s plurals (not -ies, -es, etc.)
        to avoid incorrect mappings like "Batteries" -> "Batterie".
        """
        name_lower = cat["name"].lower()
        self._category_name_map[name_lower] = cat["id"]

        # Only map singular form for simple -s plurals (not -ies, -es, -ses, -xes, -ches, -shes)
        # e.g., "capacitors" -> "capacitor", "resistors" -> "resistor"
        # but NOT "batteries" -> "batterie" or "switches" -> "switche"
        if (
            name_lower.endswith("s")
            and not name_lower.endswith("ies")
            and not name_lower.endswith("ses")
            and not name_lower.endswith("xes")
            and not name_lower.endswith("ches")
            and not name_lower.endswith("shes")
        ):
            self._category_name_map[name_lower[:-1]] = cat["id"]

    def _get_jlcpcb_session(self) -> wafer.AsyncSession:
        """Get or create persistent JLCPCB session.

        Wafer handles TLS fingerprint rotation, header generation, rate limiting,
        and retry logic automatically.
        """
        if self._jlcpcb_session is None:
            self._jlcpcb_session = wafer.AsyncSession(
                timeout=REQUEST_TIMEOUT,
                max_retries=MAX_RETRIES,
                max_rotations=JLCPCB_MAX_ROTATIONS,
                rate_limit=JLCPCB_RATE_LIMIT,
                rate_jitter=JLCPCB_RATE_JITTER,
                cache_dir=None,
                rotate_every=1,
                headers={
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                },
            )
        return self._jlcpcb_session

    def _get_easyeda_session(self) -> wafer.AsyncSession:
        """Get or create persistent EasyEDA session."""
        if self._easyeda_session is None:
            self._easyeda_session = wafer.AsyncSession(
                timeout=EASYEDA_REQUEST_TIMEOUT,
                max_retries=MAX_RETRIES,
                rate_limit=EASYEDA_RATE_LIMIT,
                rate_jitter=EASYEDA_RATE_JITTER,
            )
        return self._easyeda_session

    async def close(self):
        """Release persistent HTTP sessions."""
        self._jlcpcb_session = None
        self._easyeda_session = None

    async def _ensure_categories(self) -> None:
        """Ensure categories are loaded (lazy initialization)."""
        if self._categories:
            return

        self._categories = await self.fetch_categories()

        # Build lookup maps
        for cat in self._categories:
            self._category_map[cat["id"]] = cat
            self._build_category_name_mappings(cat)
            for sub in cat.get("subcategories", []):
                self._subcategory_map[sub["id"]] = (cat["id"], sub)
                # Store lowercase for case-insensitive matching
                self._subcategory_name_map[sub["name"].lower()] = sub["id"]

    def _get_category(self, category_id: int) -> dict[str, Any] | None:
        """Get category by ID from cache."""
        return self._category_map.get(category_id)

    def _get_subcategory(self, subcategory_id: int) -> tuple[int, dict[str, Any]] | None:
        """Get subcategory by ID from cache. Returns (parent_id, subcategory) or None."""
        return self._subcategory_map.get(subcategory_id)

    def get_subcategory_id_by_name(self, name: str) -> int | None:
        """Get subcategory ID by name from cache.

        Supports:
        - Common aliases like "mosfet", "mlcc", "ldo" via SUBCATEGORY_ALIASES
        - Case-insensitive exact match
        - Partial match with shortest-match priority (e.g., "crystal" -> "crystals")
        """
        return _resolve_subcategory_name(name, self._subcategory_name_map)

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

        Lookup order:
        1. Check aliases exactly (case-insensitive)
        2. Check exact manufacturer names (case-insensitive)
        3. Check aliases with normalized punctuation
        4. Check manufacturer names with normalized punctuation
        5. Return original name unchanged
        """
        name_lower = name.lower()
        # Check aliases first (abbreviations and alternate names)
        if name_lower in MANUFACTURER_ALIASES:
            return MANUFACTURER_ALIASES[name_lower]
        # Check if it matches a known manufacturer name (case-insensitive)
        if name_lower in _MANUFACTURER_EXACT_NAMES:
            return _MANUFACTURER_EXACT_NAMES[name_lower]
        # Try normalized matching (ignore punctuation like . , - & etc)
        name_normalized = _normalize_manufacturer_name(name)
        if name_normalized in _MANUFACTURER_ALIASES_NORMALIZED:
            return _MANUFACTURER_ALIASES_NORMALIZED[name_normalized]
        if name_normalized in _MANUFACTURER_EXACT_NORMALIZED:
            return _MANUFACTURER_EXACT_NORMALIZED[name_normalized]
        # Return original unchanged
        return name

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

    def match_category_by_name(self, query: str) -> int | None:
        """Match a query string against category names.

        Returns category_id if query matches a category name (case-insensitive).
        Handles common variations like singular/plural ("capacitor" -> "Capacitors"),
        and common abbreviations like "LED" -> Optoelectronics.

        Note: Requires categories to be loaded first via set_categories() or _ensure_categories().
        """
        if not query or not self._categories:
            return None

        query_lower = query.lower().strip()

        # O(1) lookup for exact match or singular form
        if query_lower in self._category_name_map:
            return self._category_name_map[query_lower]

        # Check explicit abbreviation mappings (resolved dynamically)
        abbrev_match = self._resolve_abbreviation(query_lower)
        if abbrev_match is not None:
            return abbrev_match

        # Fallback: prefix matching for partial names (e.g., "resistor" matches "resistors")
        for cat in self._categories:
            cat_name = cat["name"].lower()
            if cat_name.startswith(query_lower) and len(query_lower) >= 4:
                return cat["id"]

        return None

    async def _request(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute request to JLCPCB API.

        Wafer handles TLS fingerprinting, header rotation, rate limiting,
        retries, and 403 recovery automatically.

        Uses a semaphore to limit concurrent requests across all users, preventing
        IP-based blocking when the server handles many simultaneous requests.
        """
        # Limit concurrent requests to JLCPCB to prevent IP blocking at scale
        async with self._get_jlcpcb_semaphore():
            session = self._get_jlcpcb_session()
            # Sanitize logged values to prevent log injection (control chars can manipulate terminal/logs)
            raw_keyword = str(params.get('keyword', params))
            log_keyword = raw_keyword if raw_keyword.isprintable() else ''.join(
                c if c.isprintable() or c == ' ' else f'\\x{ord(c):02x}'
                for c in raw_keyword
            )
            logger.debug(f"JLCPCB request: {log_keyword}")
            try:
                response = await session.post(
                    url,
                    json=params,
                    headers={
                        "Origin": "https://jlcpcb.com",
                        "Referer": "https://jlcpcb.com/parts",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Dest": "empty",
                    },
                )
            except ChallengeDetected as e:
                logger.warning(f"JLCPCB WAF challenge ({e.challenge_type}): {log_keyword}")
                raise ValueError("JLCPCB blocked request with WAF challenge — try again later")
            except RateLimited:
                logger.warning(f"JLCPCB rate limited: {log_keyword}")
                raise ValueError("JLCPCB rate limited — try again later")
            except EmptyResponse:
                logger.warning(f"JLCPCB empty response: {log_keyword}")
                raise ValueError("JLCPCB returned empty response — try again later")
            except ConnectionFailed as e:
                logger.warning(f"JLCPCB connection failed ({e.reason}): {log_keyword}")
                raise ValueError("JLCPCB connection failed — try again later")
            except WaferTimeout:
                logger.warning(f"JLCPCB request timeout: {log_keyword}")
                raise ValueError("JLCPCB request timed out — try again later")
            logger.debug(f"JLCPCB response: {response.status_code}")
            try:
                response.raise_for_status()
            except WaferHTTPError as e:
                logger.warning(f"JLCPCB HTTP {e.status_code}: {log_keyword}")
                raise ValueError(f"JLCPCB returned HTTP {e.status_code} — try again later")
            data = response.json()

            # Check for API-level errors
            if data.get("code") != 200:
                error_msg = data.get("message", "Unknown API error")
                raise ValueError(f"JLCPCB API error: {error_msg}")

            return data

    def _get_easyeda_semaphore(self) -> asyncio.Semaphore:
        """Get or create semaphore for rate-limiting EasyEDA requests."""
        if self._easyeda_semaphore is None:
            self._easyeda_semaphore = asyncio.Semaphore(EASYEDA_CONCURRENT_LIMIT)
        return self._easyeda_semaphore

    def _get_jlcpcb_semaphore(self) -> asyncio.Semaphore:
        """Get or create semaphore for rate-limiting JLCPCB requests.

        Limits concurrent outbound requests to prevent IP-based blocking
        when multiple users hit the server simultaneously.
        """
        if self._jlcpcb_semaphore is None:
            self._jlcpcb_semaphore = asyncio.Semaphore(JLCPCB_CONCURRENT_LIMIT)
        return self._jlcpcb_semaphore

    def _cleanup_easyeda_cache_unlocked(self) -> None:
        """Remove expired entries and enforce max cache size. Must hold lock."""
        now = time.time()
        # Remove expired entries
        expired = [
            k for k, (ts, _, is_error) in self._easyeda_cache.items()
            if now - ts >= (EASYEDA_ERROR_CACHE_TTL if is_error else EASYEDA_CACHE_TTL)
        ]
        for k in expired:
            del self._easyeda_cache[k]

        # If still over max size, remove oldest entries
        if len(self._easyeda_cache) > EASYEDA_CACHE_MAX_SIZE:
            sorted_keys = sorted(
                self._easyeda_cache.keys(),
                key=lambda k: self._easyeda_cache[k][0]  # Sort by timestamp
            )
            for k in sorted_keys[:len(self._easyeda_cache) - EASYEDA_CACHE_MAX_SIZE]:
                del self._easyeda_cache[k]

    async def _cache_easyeda_result(self, lcsc: str, result: dict[str, Any], is_error: bool) -> None:
        """Cache EasyEDA result with lock protection."""
        async with self._get_easyeda_cache_lock():
            self._easyeda_cache[lcsc] = (time.time(), result, is_error)
            if len(self._easyeda_cache) >= int(EASYEDA_CACHE_MAX_SIZE * 0.9):
                self._cleanup_easyeda_cache_unlocked()

    async def check_easyeda_footprint(self, lcsc: str) -> dict[str, Any]:
        """Check if a part has an EasyEDA footprint/symbol available.

        Args:
            lcsc: LCSC part code (e.g., "C12345")

        Returns:
            Dict with:
            - has_easyeda_footprint: True/False/None (None = unknown/error)
            - easyeda_symbol_uuid: UUID string or None
            - easyeda_footprint_uuid: UUID string or None
        """
        lcsc = lcsc.strip().upper()

        # Validate LCSC format (C followed by digits)
        if not lcsc or not lcsc.startswith("C") or not lcsc[1:].isdigit():
            return {
                "has_easyeda_footprint": None,
                "easyeda_symbol_uuid": None,
                "easyeda_footprint_uuid": None,
            }

        # Check cache first (with TTL awareness for errors vs successes)
        now = time.time()
        async with self._get_easyeda_cache_lock():
            if lcsc in self._easyeda_cache:
                timestamp, result, is_error = self._easyeda_cache[lcsc]
                ttl = EASYEDA_ERROR_CACHE_TTL if is_error else EASYEDA_CACHE_TTL
                if now - timestamp < ttl:
                    return result

        # Default result for errors/timeouts
        unknown_result: dict[str, Any] = {
            "has_easyeda_footprint": None,
            "easyeda_symbol_uuid": None,
            "easyeda_footprint_uuid": None,
        }

        # Use semaphore to limit concurrent requests
        async with self._get_easyeda_semaphore():
            session = self._get_easyeda_session()
            try:
                # URL-encode the LCSC code for safety
                url = EASYEDA_COMPONENT_URL.format(lcsc=quote(lcsc, safe=''))

                response = await session.get(url)

                # 404 means no footprint exists
                if response.status_code == 404:
                    result: dict[str, Any] = {
                        "has_easyeda_footprint": False,
                        "easyeda_symbol_uuid": None,
                        "easyeda_footprint_uuid": None,
                    }
                    await self._cache_easyeda_result(lcsc, result, False)
                    return result

                response.raise_for_status()
                data = response.json()

                # Check response structure
                if data.get("success") is True:
                    # Symbol UUID is in result.uuid, footprint UUID is in packageDetail.uuid
                    result_data = data.get("result", {})
                    package_detail = result_data.get("packageDetail", {})
                    result = {
                        "has_easyeda_footprint": True,
                        "easyeda_symbol_uuid": result_data.get("uuid"),
                        "easyeda_footprint_uuid": package_detail.get("uuid") if package_detail else None,
                    }
                else:
                    # success: false means no footprint
                    result = {
                        "has_easyeda_footprint": False,
                        "easyeda_symbol_uuid": None,
                        "easyeda_footprint_uuid": None,
                    }

                await self._cache_easyeda_result(lcsc, result, False)
                return result

            except Exception as e:
                # Log the error for debugging, cache with shorter TTL to avoid hammering
                logger.warning(f"EasyEDA footprint check failed for {lcsc}: {type(e).__name__}: {e}")
                await self._cache_easyeda_result(lcsc, unknown_result, True)
                return unknown_result

    def _cleanup_easyeda_component_cache_unlocked(self) -> None:
        """Clean up expired entries if cache is too large. Must hold lock."""
        if len(self._easyeda_component_cache) > EASYEDA_CACHE_MAX_SIZE:
            now = time.time()
            expired = [
                k for k, (ts, _, is_err) in self._easyeda_component_cache.items()
                if now - ts > (EASYEDA_ERROR_CACHE_TTL if is_err else EASYEDA_CACHE_TTL)
            ]
            for k in expired:
                del self._easyeda_component_cache[k]

    async def _cache_easyeda_component_result(
        self, uuid: str, result: dict[str, Any] | ValueError, is_error: bool
    ) -> None:
        """Cache EasyEDA component result with lock protection."""
        async with self._get_easyeda_component_cache_lock():
            self._easyeda_component_cache[uuid] = (time.time(), result, is_error)
            self._cleanup_easyeda_component_cache_unlocked()

    def _cleanup_part_cache_unlocked(self) -> None:
        """Clean up expired part cache entries if cache is too large. Must hold lock."""
        if len(self._part_cache) >= int(PART_CACHE_MAX_SIZE * 0.9):
            now = time.time()
            # Remove expired entries
            expired = [
                k for k, (ts, _) in self._part_cache.items()
                if now - ts >= PART_CACHE_TTL
            ]
            for k in expired:
                del self._part_cache[k]

            # If still over max size, remove oldest entries
            if len(self._part_cache) > PART_CACHE_MAX_SIZE:
                sorted_keys = sorted(
                    self._part_cache.keys(),
                    key=lambda k: self._part_cache[k][0]  # Sort by timestamp
                )
                for k in sorted_keys[:len(self._part_cache) - PART_CACHE_MAX_SIZE]:
                    del self._part_cache[k]

    async def _cache_part_result(self, lcsc: str, result: dict[str, Any] | None) -> None:
        """Cache part result with lock protection."""
        async with self._get_part_cache_lock():
            self._part_cache[lcsc] = (time.time(), result)
            self._cleanup_part_cache_unlocked()

    async def get_easyeda_component(self, uuid: str) -> dict[str, Any]:
        """Fetch component symbol data from EasyEDA API.

        Args:
            uuid: EasyEDA symbol UUID (32-character hex string)

        Returns:
            Dict with component data including dataStr.shape array containing pin elements.

        Raises:
            ValueError: If UUID is invalid or API request fails.
        """
        if not uuid or not isinstance(uuid, str):
            raise ValueError("UUID is required")

        # Validate UUID format (32-char hex)
        uuid = uuid.strip()
        if not _UUID_PATTERN.match(uuid):
            raise ValueError("Invalid UUID format")

        # Check cache first
        now = time.time()
        async with self._get_easyeda_component_cache_lock():
            if uuid in self._easyeda_component_cache:
                timestamp, cached_result, is_error = self._easyeda_component_cache[uuid]
                ttl = EASYEDA_ERROR_CACHE_TTL if is_error else EASYEDA_CACHE_TTL
                if now - timestamp < ttl:
                    if is_error:
                        raise cached_result  # Re-raise cached error
                    return cached_result  # type: ignore

        # Use semaphore to limit concurrent requests
        async with self._get_easyeda_semaphore():
            session = self._get_easyeda_session()
            try:
                url = EASYEDA_SYMBOL_URL.format(uuid=quote(uuid, safe=''))

                response = await session.get(url)
                response.raise_for_status()
                data = response.json()

                # Check response structure
                if not data.get("success"):
                    error = ValueError("Failed to fetch component data from EasyEDA")
                    logger.warning(f"EasyEDA API error for {uuid}: {data.get('message', 'Unknown error')}")
                    await self._cache_easyeda_component_result(uuid, error, True)
                    raise error

                result = data.get("result", {})
                if "dataStr" not in result:
                    error = ValueError("Invalid EasyEDA response - missing dataStr")
                    await self._cache_easyeda_component_result(uuid, error, True)
                    raise error

                # Cache successful result
                await self._cache_easyeda_component_result(uuid, result, False)
                return result

            except ValueError:
                raise  # Don't retry validation errors
            except Exception as e:
                logger.warning(f"EasyEDA component fetch failed for {uuid}: {type(e).__name__}: {e}")
                error = ValueError("Failed to fetch component data from EasyEDA")
                await self._cache_easyeda_component_result(uuid, error, True)
                raise error

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
                # Handled in search() with two parallel API calls (basic + preferred)
                pass

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

        # Map library type: preferred parts have componentLibraryType=expand but
        # preferredComponentFlag=True — they have no assembly fee (same as basic)
        lib_type = item.get("componentLibraryType", "")
        is_preferred = item.get("preferredComponentFlag", False)
        if is_preferred:
            library_type = "preferred"
        elif lib_type == "base":
            library_type = "basic"
        elif lib_type == "expand":
            library_type = "extended"
        else:
            library_type = lib_type

        # Note: API returns firstSortName as subcategory, secondSortName as category
        stock = item.get("stockCount")
        package = item.get("componentSpecificationEn")
        subcategory = item.get("firstSortName")
        category = item.get("secondSortName")
        # Get subcategory_id from API or lookup by name
        subcategory_id = item.get("firstSortId")
        if not subcategory_id and subcategory:
            subcategory_id = self._subcategory_name_map.get(subcategory.lower())
        result: dict[str, Any] = {
            "lcsc": item.get("componentCode"),
            "model": item.get("componentModelEn"),
            "manufacturer": item.get("componentBrandEn"),
            "package": package,
            "stock": stock,
            "price": round(price, 4) if price else None,
            "price_10": round(price_10, 4) if price_10 else None,
            "library_type": library_type,
            "preferred": item.get("preferredComponentFlag", False),
            "category": category,
            "subcategory": subcategory,
            "subcategory_id": subcategory_id,
            "mounting_type": detect_mounting_type(package, category=category, subcategory=subcategory),
        }

        # Include key specs in slim mode
        # All attributes as a dict for compatibility checking and display
        attrs = item.get("attributes") or []  # Handle null/None
        result["specs"] = {
            a.get("attribute_name_en"): a.get("attribute_value_name")
            for a in attrs
            if a.get("attribute_name_en")
        }

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

            # Full attributes list (beyond specs)
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
            matched_category = self.match_category_by_name(query)
            if matched_category:
                category_id = matched_category
                query = None  # Use category filter instead of keyword

        # no_fee = basic + preferred, but the JLCPCB API can't OR these in one call.
        # Make two parallel requests and merge results.
        if library_type == "no_fee":
            shared = dict(
                query=query, category_id=category_id, subcategory_id=subcategory_id,
                min_stock=min_stock, package=package, manufacturer=manufacturer,
                packages=packages, manufacturers=manufacturers,
                sort_by=sort_by, page=page, limit=limit,
            )
            basic_params = self._build_search_params(**shared, library_type="basic")
            preferred_params = self._build_search_params(**shared, library_type="preferred")

            # Sequential to respect rate limits (same hostname)
            basic_data = await self._request(JLCPCB_SEARCH_URL, basic_params)
            preferred_data = await self._request(JLCPCB_SEARCH_URL, preferred_params)

            basic_info = (basic_data.get("data") or {}).get("componentPageInfo") or {}
            pref_info = (preferred_data.get("data") or {}).get("componentPageInfo") or {}

            basic_items = basic_info.get("list") or []
            pref_items = pref_info.get("list") or []

            # Interleave basic and preferred so both types get fair representation
            seen: set[str] = set()
            items: list[dict[str, Any]] = []
            bi, pi = 0, 0
            while len(items) < limit and (bi < len(basic_items) or pi < len(pref_items)):
                if bi < len(basic_items):
                    lcsc = basic_items[bi].get("componentCode")
                    if lcsc and lcsc not in seen:
                        seen.add(lcsc)
                        items.append(basic_items[bi])
                    bi += 1
                if len(items) < limit and pi < len(pref_items):
                    lcsc = pref_items[pi].get("componentCode")
                    if lcsc and lcsc not in seen:
                        seen.add(lcsc)
                        items.append(pref_items[pi])
                    pi += 1

            total = (basic_info.get("total") or 0) + (pref_info.get("total") or 0)
            results = [self._transform_part(item, slim=True) for item in items]
        else:
            # Standard single-call path
            params = self._build_search_params(
                query=query, category_id=category_id, subcategory_id=subcategory_id,
                min_stock=min_stock, library_type=library_type, package=package,
                manufacturer=manufacturer, packages=packages, manufacturers=manufacturers,
                sort_by=sort_by, page=page, limit=limit,
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
        """Get full details for a specific part, including EasyEDA footprint availability.

        Results are cached for 1 hour to reduce API calls. Stock/price changes
        are infrequent enough that this is acceptable for most use cases.
        """
        # Normalize LCSC code to uppercase (e.g., c20917 -> C20917)
        lcsc = lcsc.strip().upper()

        # Validate LCSC code format (C followed by digits)
        if not lcsc or not lcsc.startswith("C") or not lcsc[1:].isdigit():
            return None

        # Check cache first
        now = time.time()
        async with self._get_part_cache_lock():
            if lcsc in self._part_cache:
                timestamp, cached_result = self._part_cache[lcsc]
                if now - timestamp < PART_CACHE_TTL:
                    return cached_result

        # Search for the exact part code
        params = {
            "keyword": lcsc,
            "currentPage": 1,
            "pageSize": 10,
            "searchSource": "search",
        }

        response = await self._request(JLCPCB_SEARCH_URL, params)
        data = response.get("data", {})
        component_info = data.get("componentPageInfo") or {}
        items = component_info.get("list") or []

        # Find exact match
        for item in items:
            if item.get("componentCode") == lcsc:
                result = self._transform_part(item, slim=False)
                # Add EasyEDA footprint availability
                easyeda_info = await self.check_easyeda_footprint(lcsc)
                result.update(easyeda_info)
                # Cache the result
                await self._cache_part_result(lcsc, result)
                return result

        # Cache negative result (part not found)
        await self._cache_part_result(lcsc, None)
        return None

    async def find_alternatives(
        self,
        lcsc: str,
        min_stock: int = DEFAULT_MIN_STOCK,
        same_package: bool = False,
        library_type: str | None = None,
        has_easyeda_footprint: bool | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Find alternative parts similar to a given component.

        Uses spec-aware compatibility checking to ensure alternatives are safe to use.
        For supported subcategories, verifies primary spec matches and same_or_better rules.
        For unsupported subcategories, returns similar_parts for manual comparison.

        Args:
            lcsc: LCSC part code to find alternatives for (e.g., "C2557")
            min_stock: Minimum stock for alternatives (default: DEFAULT_MIN_STOCK)
            same_package: If True, only return parts with the same package size
            library_type: Filter by library type ("basic", "preferred", "no_fee", "extended")
                          Use "no_fee" to find basic/preferred alternatives for extended parts.
            has_easyeda_footprint: If True, only return parts with EasyEDA footprints.
                                   If False, only parts without footprints.
                                   If None (default), don't filter by footprint.
                                   Note: filtering is slower as it checks each part.
            limit: Maximum alternatives to return (default: 10, max: 50)

        Returns:
            Dict with original part info, alternatives (verified compatible), and
            similar_parts (for unsupported categories requiring manual verification).
        """
        # Validate and cap limit
        effective_limit = max(1, min(limit, MAX_ALTERNATIVES))
        effective_min_stock = max(0, min_stock)

        # Ensure categories are loaded for subcategory lookup
        await self._ensure_categories()

        # Get the original part details (includes EasyEDA info)
        original = await self.get_part(lcsc)
        if not original:
            return {"error": f"Part {lcsc.strip().upper()} not found"}

        # Check if category is supported for compatibility checking
        subcategory_name = original.get("subcategory")
        rules = COMPATIBILITY_RULES.get(subcategory_name) if subcategory_name else None
        is_supported = rules is not None

        # Get primary spec for search query
        # For supported: use rules["primary"]
        # For unsupported: no primary spec (can't verify compatibility anyway)
        if is_supported and rules:
            primary_attr = rules.get("primary")
        else:
            primary_attr = None

        primary_value = None
        if primary_attr:
            primary_value = original.get("specs", {}).get(primary_attr)

        # Find subcategory ID using O(1) lookup
        subcategory_id = None
        if subcategory_name:
            subcategory_id = self.get_subcategory_id_by_name(subcategory_name)

        # Build search params - fetch extra for filtering
        # Higher multiplier when same_package=True since we post-filter by package
        # (need more candidates to find matching package variants)
        search_multiplier = 5 if is_supported else 3
        if same_package:
            search_multiplier = 10  # More candidates for package filtering
        extra_for_footprint = 20 if has_easyeda_footprint is not None else 0
        search_params: dict[str, Any] = {
            "min_stock": effective_min_stock,
            "sort_by": "quantity",  # Best availability first
            "limit": effective_limit * search_multiplier + extra_for_footprint,
            "library_type": "all",  # Don't filter here - let scoring prioritize
        }

        # Add primary spec as query for more relevant results
        # Skip generic/unhelpful values that return no results
        GENERIC_VALUES = {"Others", "Other", "-", "N/A", "None", ""}
        if primary_value and primary_value not in GENERIC_VALUES:
            search_params["query"] = primary_value
        elif not is_supported:
            # For unsupported categories with generic primary values,
            # use manufacturer to find similar parts from same vendor
            # (e.g., find other ESP32 variants from Espressif)
            manufacturer = original.get("manufacturer")
            if manufacturer:
                search_params["manufacturer"] = manufacturer

        if subcategory_id:
            search_params["subcategory_id"] = subcategory_id

        # Note: We don't pass package to search anymore - we do fuzzy post-filtering
        # This allows matching variants like CASE-B-3528-21(mm) vs CASE-B-3528-19(mm)

        result = await self.search(**search_params)

        # Filter out the original part
        original_lcsc = original.get("lcsc", "").upper()
        candidates = [
            p for p in result.get("results", [])
            if p.get("lcsc", "").upper() != original_lcsc
        ]

        # Filter by same package if requested (using fuzzy matching)
        if same_package and original.get("package"):
            orig_pkg_normalized = _normalize_package_for_matching(original["package"])
            candidates = [
                p for p in candidates
                if _normalize_package_for_matching(p.get("package", "")) == orig_pkg_normalized
            ]

        # For SUPPORTED categories: verify primary spec matches and compatibility
        # For UNSUPPORTED categories: skip verification, just return similar_parts
        compatible: list[dict[str, Any]] = []
        verification_info_map: dict[str, dict[str, Any]] = {}

        if is_supported:
            # Verify primary spec matches (JLCPCB search may return fuzzy matches)
            verified = [
                p for p in candidates
                if not primary_attr or verify_primary_spec_match(original, p, primary_attr)
            ]
            # Then check full compatibility
            for p in verified:
                is_compat, verify_info = is_compatible_alternative(original, p, subcategory_name or "")
                if is_compat:
                    compatible.append(p)
                    verification_info_map[p.get("lcsc", "")] = verify_info
        else:
            # For unsupported categories, skip strict verification
            # Just return similar parts from same subcategory for manual comparison
            compatible = candidates
            for p in compatible:
                verification_info_map[p.get("lcsc", "")] = {"specs_verified": [], "specs_unparseable": []}

        # Filter by EasyEDA footprint availability if requested
        # Pre-filter to limit EasyEDA API calls (2x limit provides buffer for filtering)
        if has_easyeda_footprint is not None:
            # Only check top candidates to avoid excessive API calls
            max_easyeda_checks = effective_limit * 2
            candidates_to_check = compatible[:max_easyeda_checks]
            candidate_codes = [p.get("lcsc", "") for p in candidates_to_check if p.get("lcsc")]
            easyeda_results = await asyncio.gather(
                *[self.check_easyeda_footprint(code) for code in candidate_codes]
            )
            easyeda_map = dict(zip(candidate_codes, easyeda_results))

            filtered_compatible = []
            for part in candidates_to_check:
                part_lcsc = part.get("lcsc", "")
                if not part_lcsc:
                    continue
                easyeda_info = easyeda_map.get(part_lcsc, {})
                has_fp = easyeda_info.get("has_easyeda_footprint")
                if has_fp is None:
                    continue
                if has_fp == has_easyeda_footprint:
                    part.update(easyeda_info)
                    filtered_compatible.append(part)
            compatible = filtered_compatible

        # Filter by library_type if specified (after compatibility check)
        if library_type and library_type != "all":
            if library_type == "no_fee":
                compatible = [p for p in compatible if p.get("library_type") in ("basic", "preferred")]
            elif library_type == "basic":
                compatible = [p for p in compatible if p.get("library_type") == "basic"]
            elif library_type == "preferred":
                compatible = [p for p in compatible if p.get("preferred", False)]
            elif library_type == "extended":
                compatible = [p for p in compatible if p.get("library_type") == "extended"]

        # Score and rank alternatives
        min_price = min((p.get("price") for p in compatible if p.get("price")), default=None)
        scored: list[tuple[int, dict[str, Any], dict[str, int], dict[str, Any]]] = []
        for part in compatible:
            score, breakdown = score_alternative(part, original, min_price)
            verify_info = verification_info_map.get(part.get("lcsc", ""), {"specs_verified": [], "specs_unparseable": []})
            scored.append((score, part, breakdown, verify_info))

        # Use heapq for efficient top-k selection instead of full sort
        top_scored = heapq.nlargest(effective_limit, scored, key=lambda x: x[0])

        # Build response (different structure for supported vs unsupported)
        if is_supported:
            return build_response(
                original, top_scored, subcategory_name or "", primary_attr, primary_value, effective_limit
            )
        else:
            return build_unsupported_response(
                original, top_scored, subcategory_name or "", primary_attr, effective_limit
            )

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
