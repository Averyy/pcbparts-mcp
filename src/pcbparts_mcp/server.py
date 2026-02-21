"""PCB Parts MCP Server - Search electronic components for PCB assembly."""

import json
import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastmcp import FastMCP
from mcp.types import Icon, ToolAnnotations
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import __version__
from .config import (
    RATE_LIMIT_REQUESTS, HTTP_PORT, DEFAULT_MIN_STOCK, MAX_PAGE_SIZE, MAX_BOM_PARTS,
    MOUSER_API_KEY, DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET, CSE_USER,
)
from .client import JLCPCBClient
from .mouser import MouserClient, MouserAPIError
from .digikey import DigiKeyClient
from .cse import CSEClient
from .db import get_db, close_db
from .search import SpecFilter
from .smart_parser import parse_smart_query, merge_spec_filters
from .bom import (
    BOMPart,
    BOMIssue,
    validate_designators,
    merge_duplicate_parts,
    sort_by_designator,
    generate_comment,
    check_footprint_mismatch,
    calculate_line_cost,
    generate_csv,
    generate_summary,
    validate_manual_part,
    check_stock_issues,
    check_moq_issue,
    check_extended_part,
    check_easyeda_footprint,
)
from .pinout import parse_easyeda_pins

logger = logging.getLogger(__name__)

# Global state
_client: JLCPCBClient | None = None
_mouser_client: MouserClient | None = None
_digikey_client: DigiKeyClient | None = None
_cse_client: CSEClient | None = None
_categories: list[dict[str, Any]] = []  # Live category cache


@asynccontextmanager
async def lifespan(app):
    """Manage client lifecycle, build DB, and load categories on startup."""
    global _client, _mouser_client, _digikey_client, _cse_client, _categories
    _client = JLCPCBClient()

    # Build/load DB on startup (not on first request)
    db = get_db()
    db._ensure_db()
    stats = db.get_stats()
    logger.info(f"Database ready: {stats.get('total_parts', 0)} parts")

    # Load categories from DB (updated daily by scraper, no API call needed)
    _categories = db.get_categories_for_client()
    _client.set_categories(_categories)
    logger.info(f"Loaded {len(_categories)} categories from database")

    # Initialize Mouser client if API key is configured
    if MOUSER_API_KEY:
        _mouser_client = MouserClient(MOUSER_API_KEY)
        logger.info("Mouser client initialized")

    # Initialize DigiKey client if credentials are configured
    if DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET:
        _digikey_client = DigiKeyClient(DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET)
        logger.info("DigiKey client initialized")

    # CSE client always available (no API key needed)
    _cse_client = CSEClient()
    logger.info("CSE client initialized")

    yield

    if _cse_client:
        await _cse_client.close()
    if _mouser_client:
        await _mouser_client.close()
    if _digikey_client:
        await _digikey_client.close()
    if _client:
        await _client.close()
    close_db()


# Create MCP server
mcp = FastMCP(
    name="pcbparts",
    instructions="PCB parts component search for PCB assembly. No auth required. Use search to find components, get_part for details.",
    lifespan=lifespan,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - 100 requests/minute per IP.

    Includes protections against memory exhaustion from IP spoofing:
    - Maximum tracked IPs limit (10,000)
    - Periodic cleanup of stale IPs
    """

    MAX_TRACKED_IPS = 10_000  # Prevent memory exhaustion from spoofed IPs

    def __init__(self, app, requests_per_minute: int = RATE_LIMIT_REQUESTS):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: dict[str, list[float]] = {}
        self._last_cleanup = time.time()

    def _get_client_ip(self, request) -> str:
        """Extract client IP, preferring rightmost X-Forwarded-For entry.

        Rightmost is harder to spoof as it's set by the last trusted proxy.
        """
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # Use rightmost IP (set by our reverse proxy, harder to spoof)
            ips = [ip.strip() for ip in forwarded.split(",")]
            return ips[-1] if ips else "unknown"
        return request.client.host if request.client else "unknown"

    def _cleanup_stale_ips(self, now: float) -> None:
        """Remove IPs with no recent requests. Called periodically."""
        window_start = now - 60
        stale_ips = [
            ip for ip, timestamps in self.request_counts.items()
            if not timestamps or timestamps[-1] < window_start
        ]
        for ip in stale_ips:
            del self.request_counts[ip]

    def _check_rate_limit(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60

        # Periodic cleanup every 60 seconds to remove stale IPs
        if now - self._last_cleanup > 60:
            self._cleanup_stale_ips(now)
            self._last_cleanup = now

        # If tracking too many IPs, do aggressive cleanup
        if len(self.request_counts) >= self.MAX_TRACKED_IPS:
            self._cleanup_stale_ips(now)
            # If still at limit after cleanup, reject to prevent memory exhaustion
            if len(self.request_counts) >= self.MAX_TRACKED_IPS:
                return True  # Rate limit as protection

        # Get or create entry for this IP
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = [now]
            return False

        # Filter old entries
        self.request_counts[client_ip] = [
            t for t in self.request_counts[client_ip] if t > window_start
        ]

        # Check if rate limited before adding current request
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            return True

        # Add current request
        self.request_counts[client_ip].append(now)
        return False

    async def dispatch(self, request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        if self._check_rate_limit(client_ip):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": 60},
                headers={"Retry-After": "60"},
            )
        return await call_next(request)


# Helpers to handle JSON string arrays from MCP clients
def _parse_list_param(value: list[str] | str | None) -> list[str] | None:
    """Parse a list parameter that may come as a JSON string from some MCP clients.

    Claude Code's MCP client sometimes serializes list parameters as JSON strings
    like '["a", "b"]' instead of actual arrays. This handles both cases.
    """
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            logger.debug(f"Failed to parse list parameter as JSON: {value[:100]!r}")
    return None


def _parse_parts_param(value: list[dict[str, Any]] | str) -> list[dict[str, Any]]:
    """Parse a parts list parameter that may come as a JSON string.

    For BOM tools where parts is required, handles both list and JSON string formats.
    Returns empty list on parse failure (will be caught by validation).
    """
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            logger.debug(f"Failed to parse parts parameter as JSON: {value[:100]!r}")
    return []


def _validate_bom_parts(parsed_parts: list[dict[str, Any]]) -> dict | None:
    """Validate parsed BOM parts list.

    Returns error dict if validation fails, None if valid.
    """
    if not parsed_parts:
        return {"error": "No parts provided. The 'parts' parameter must be a non-empty list of part objects."}
    if len(parsed_parts) > MAX_BOM_PARTS:
        return {"error": f"Too many parts ({len(parsed_parts)}). Maximum is {MAX_BOM_PARTS} parts per BOM."}
    return None


# Tools

@mcp.tool(
    annotations=ToolAnnotations(
        title="Search API (Live)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_search_api(
    query: str | None = None,
    category_id: int | None = None,
    subcategory_id: int | None = None,
    category_name: str | None = None,
    subcategory_name: str | None = None,
    min_stock: int = DEFAULT_MIN_STOCK,
    library_type: str | None = None,
    package: str | None = None,
    manufacturer: str | None = None,
    packages: list[str] | str | None = None,
    manufacturers: list[str] | str | None = None,
    sort_by: Literal["quantity", "price"] | None = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Live API search. Full catalog including out-of-stock, but keywords only (no parametric filters).

    Use this when you need:
    - Parts with stock < 100 or out-of-stock parts
    - Real-time stock verification before placing an order
    - Pagination through large result sets

    Args:
        query: Search keywords (e.g., "ESP32", "10uF 25V", "STM32F103")
        category_id: Category ID from list_categories
        subcategory_id: Subcategory ID from get_subcategories
        category_name: Category name (e.g., "Resistors", "Capacitors")
        subcategory_name: Subcategory name (e.g., "Tactile Switches")
        min_stock: Min stock (default DEFAULT_MIN_STOCK). Set 0 for out-of-stock parts
        library_type: "basic", "preferred", "no_fee", "extended", or "all"
        package: Package filter (e.g., "0402", "LQFP48")
        manufacturer: Manufacturer filter
        packages: Multiple packages (OR filter)
        manufacturers: Multiple manufacturers (OR filter)
        sort_by: "quantity" or "price"
        page: Page number (default 1)
        limit: Results per page (default 20, max 100)

    Returns:
        Results with pagination. Use get_part(lcsc) for full details.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    # Validate parameters
    if query and len(query) > 500:
        return {"error": "Query too long (max 500 characters)"}
    effective_min_stock = max(0, min_stock)
    effective_page = max(1, page)
    effective_limit = max(1, min(limit, MAX_PAGE_SIZE))

    # Parse list parameters (handles JSON strings from some MCP clients)
    parsed_packages = _parse_list_param(packages)
    parsed_manufacturers = _parse_list_param(manufacturers)

    # Resolve category_name to category_id if provided (ID takes precedence)
    resolved_category_id = category_id
    if category_name and not category_id:
        # Ensure categories are loaded before name resolution
        if not _categories:
            return {"error": "Categories not loaded. Server may still be starting up.", "hint": "Try again in a moment"}
        resolved_category_id = _client.match_category_by_name(category_name)
        if resolved_category_id is None:
            return {"error": f"Category not found: '{category_name}'", "hint": "Use list_categories to see available categories"}

    # Resolve subcategory_name to subcategory_id if provided (ID takes precedence)
    resolved_subcategory_id = subcategory_id
    if subcategory_name and not subcategory_id:
        # Ensure categories are loaded before name resolution
        if not _categories:
            return {"error": "Categories not loaded. Server may still be starting up.", "hint": "Try again in a moment"}
        resolved_subcategory_id = _client.get_subcategory_id_by_name(subcategory_name)
        if resolved_subcategory_id is None:
            return {"error": f"Subcategory not found: '{subcategory_name}'", "hint": "Use get_subcategories to see available subcategories for a category"}

    return await _client.search(
        query=query,
        category_id=resolved_category_id,
        subcategory_id=resolved_subcategory_id,
        min_stock=effective_min_stock,
        library_type=library_type if library_type != "all" else None,
        package=package,
        manufacturer=manufacturer,
        packages=parsed_packages,
        manufacturers=parsed_manufacturers,
        sort_by=sort_by,
        page=effective_page,
        limit=effective_limit,
    )


def _parse_spec_filters(filters: list[dict[str, str]] | str | None) -> list[SpecFilter] | None:
    """Parse spec filters from various input formats."""
    if filters is None:
        return None

    # Handle JSON string input from some MCP clients
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except json.JSONDecodeError:
            logger.debug(f"Failed to parse spec_filters as JSON: {filters[:100]!r}")
            return None

    if not isinstance(filters, list):
        return None

    result = []
    for f in filters:
        if isinstance(f, dict) and "name" in f and "op" in f and "value" in f:
            op = f["op"]
            if op in ("=", ">=", "<=", ">", "<"):
                result.append(SpecFilter(f["name"], op, f["value"]))
    return result if result else None


@mcp.tool(
    annotations=ToolAnnotations(
        title="Search Components",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_search(
    query: str | None = None,
    subcategory_id: int | None = None,
    subcategory_name: str | None = None,
    spec_filters: list[dict[str, str]] | str | None = None,
    min_stock: int = DEFAULT_MIN_STOCK,
    library_type: str | None = None,
    prefer_no_fee: bool = True,
    package: str | None = None,
    packages: list[str] | str | None = None,
    manufacturer: str | None = None,
    match_all_terms: bool = True,
    sort_by: Literal["stock", "price"] = "stock",
    limit: int = 50,
) -> dict:
    """Fast DB search with natural language parsing and parametric filters. In-stock parts only (stock >= DEFAULT_MIN_STOCK).

    Args:
        query: Search query - supports natural language like:
            - "10k resistor 0603 1%" (auto-detects type, value, package, tolerance)
            - "100nF 25V capacitor" (auto-applies voltage >= 25V filter)
            - "n-channel mosfet SOT-23" (auto-filters to MOSFETs subcategory)
            Or use with explicit filters for text search within results.

        subcategory_id: Subcategory ID (e.g., 2954 for MOSFETs)
        subcategory_name: Subcategory name (e.g., "MOSFETs", "Schottky Diodes")
        spec_filters: Parametric filters for precise searches. Each filter is a dict:
            - name: Attribute name (Vgs(th), Capacitance, Voltage, etc.)
            - op: Operator: "=", ">=", "<=", ">", "<"
            - value: Value with units (e.g., "2.5V", "10uF", "20mΩ")
            Example: [{"name": "Vgs(th)", "op": "<", "value": "2.5V"}]

        min_stock: Minimum stock (default DEFAULT_MIN_STOCK). Database only indexes stock >= DEFAULT_MIN_STOCK.
        library_type: "basic", "preferred", "no_fee", "extended", or None (all)
        prefer_no_fee: Sort basic/preferred first (default True)
        package: Single package filter (e.g., "0603", "SOT-23")
        packages: Multiple packages (OR logic): ["0402", "0603", "0805"]
        manufacturer: Manufacturer filter
        match_all_terms: AND logic for query terms (default True)
        sort_by: "stock" (highest) or "price" (cheapest)
        limit: Max results (default 50, max 100)

    Attribute aliases:
        MOSFETs: Vgs(th), Vds, Id, Rds(on)
        Diodes: Vr, If, Vf
        Passives: Capacitance, Resistance, Inductance, Voltage, Tolerance

    Returns:
        results: Matching components with specs
        total: Total count (before limit)
        filters_applied: Applied filters (useful for debugging)
        parsed: (when using natural language) What was extracted from query
    """
    # Validate query length to prevent abuse
    MAX_QUERY_LENGTH = 500
    if query and len(query) > MAX_QUERY_LENGTH:
        return {"error": f"Query too long (max {MAX_QUERY_LENGTH} characters)", "results": [], "total": 0}

    db = get_db()

    # Parse explicit spec filters
    parsed_filters = _parse_spec_filters(spec_filters)

    # Parse packages array (handles JSON strings from some MCP clients)
    parsed_packages = _parse_list_param(packages)

    # Smart parsing: always parse query to clean up text and extract structured info
    # This handles cases like "lipo charger" where terms don't exist in FTS index
    parsed_query_info = None
    effective_subcategory_name = subcategory_name
    effective_package = package
    effective_mounting_type: str | None = None
    effective_query = query

    if query:
        # Parse natural language query to extract structured info and clean text
        parsed = parse_smart_query(query)
        parsed_query_info = {
            "original_query": parsed.original,
            "detected": parsed.detected,
            "subcategory": parsed.subcategory,
            "package": parsed.package,
            "mounting_type": parsed.mounting_type,
            "spec_filters": [f.to_dict() for f in parsed.spec_filters],
            "remaining_text": parsed.remaining_text,
        }

        # Apply parsed values only if user didn't provide explicit ones
        if parsed.subcategory and not subcategory_name and not subcategory_id:
            effective_subcategory_name = parsed.subcategory
        if parsed.package and not package:
            effective_package = parsed.package
        # Merge auto-detected spec filters with manual ones (manual takes precedence)
        parsed_filters = merge_spec_filters(parsed_filters, parsed.spec_filters)
        if parsed.mounting_type:
            effective_mounting_type = parsed.mounting_type

        # Always use cleaned remaining_text for FTS (removes subcategory keywords, etc.)
        if parsed.remaining_text and len(parsed.remaining_text) >= 2:
            effective_query = parsed.remaining_text
        elif parsed.spec_filters or parsed.subcategory:
            # Query was fully parsed into structured filters, no text needed
            effective_query = None

    # Perform search - db.search() handles name resolution internally
    result = db.search(
        query=effective_query,
        subcategory_id=subcategory_id,
        subcategory_name=effective_subcategory_name,
        spec_filters=parsed_filters,
        library_type=library_type if library_type != "all" else None,
        prefer_no_fee=prefer_no_fee,
        min_stock=max(0, min_stock),
        package=effective_package,
        packages=parsed_packages,
        manufacturer=manufacturer,
        mounting_type=effective_mounting_type,
        match_all_terms=match_all_terms,
        sort_by=sort_by,
        limit=min(limit, 100),
    )

    # Add parsing info if natural language was used
    if parsed_query_info:
        result["parsed"] = parsed_query_info

    return result


@mcp.tool(
    annotations=ToolAnnotations(
        title="List Filterable Attributes",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_list_attributes(
    subcategory_id: int | None = None,
    subcategory_name: str | None = None,
) -> dict:
    """List available filterable attributes for a subcategory.

    Use this to discover what spec_filters can be used with search().
    Shows all attributes in the subcategory with their types and example values.

    Args:
        subcategory_id: Subcategory ID (e.g., 2954 for MOSFETs, 2929 for MLCC)
        subcategory_name: Subcategory name (alternative to ID). E.g., "MOSFETs", "Chip Resistor"

    Returns:
        subcategory_id: Resolved subcategory ID
        subcategory_name: Full subcategory name
        attributes: List of filterable attributes, each with:
            - name: Full attribute name as stored in database
            - alias: Short name for use in spec_filters (e.g., "Vgs(th)" for "Gate Threshold Voltage")
            - type: "numeric" (supports >=, <=, >, <, =) or "string" (= only)
            - count: Number of parts with this attribute
            - example_values: (numeric) Sample values like ["1V~2.5V", "0.5V"]
            - values: (string) All distinct values like ["N-Channel", "P-Channel"]

    Example usage:
        1. list_attributes(subcategory_name="MOSFETs")
        2. Find attribute "Gate Threshold Voltage (Vgs(th))" with alias "Vgs(th)"
        3. Use in search: spec_filters=[{"name": "Vgs(th)", "op": "<", "value": "2.5V"}]

    Tip: Use the alias (short name) in spec_filters for convenience.
    """
    db = get_db()
    return db.list_attributes(
        subcategory_id=subcategory_id,
        subcategory_name=subcategory_name,
    )


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Part Details",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_get_part(lcsc: str | None = None, mpn: str | None = None) -> dict:
    """Get full details for a specific JLCPCB part.

    Args:
        lcsc: LCSC part code (e.g., "C82899")
        mpn: Manufacturer part number (e.g., "LM358P", "STM32F103C8T6").
             Searches local DB by exact MPN match, then normalized variants,
             then full-text search. Useful for finding the JLCPCB equivalent
             of a part from another distributor or reference design.

    One of lcsc or mpn must be provided. If both are provided, lcsc takes precedence.

    Returns:
        For lcsc: Full part details including description, all pricing tiers, datasheet URL,
        component attributes, and EasyEDA footprint availability:
        - has_easyeda_footprint: True if EasyEDA has footprint/symbol, False if not, null if unknown
        - easyeda_symbol_uuid: UUID for direct EasyEDA editor link (null if no footprint)
        - easyeda_footprint_uuid: UUID for footprint (null if no footprint)

        For mpn: List of matching JLCPCB parts from the local database (stock >= DEFAULT_MIN_STOCK),
        sorted by stock. Each result includes lcsc, model (MPN), manufacturer,
        package, stock, price, library_type, category, subcategory, and specs.

        Note: has_easyeda_footprint=True means `ato create part` will work for Atopile/KiCad users.
    """
    if not lcsc and not mpn:
        return {"error": "Must provide either lcsc or mpn"}

    # MPN lookup via local database
    if mpn and not lcsc:
        if len(mpn) > 100:
            return {"error": "MPN too long (max 100 characters)"}
        db = get_db()
        results = db.get_by_mpn(mpn)
        if not results:
            return {"error": f"No JLCPCB parts found for MPN '{mpn}'", "mpn": mpn, "results": []}
        return {
            "mpn": mpn,
            "total": len(results),
            "results": results,
        }

    # LCSC lookup via live API (existing behavior)
    if not _client:
        raise RuntimeError("Client not initialized")

    result = await _client.get_part(lcsc)
    if not result:
        return {"error": f"Part {lcsc} not found"}
    return result


@mcp.tool(
    annotations=ToolAnnotations(
        title="List Categories",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_list_categories() -> dict:
    """Get all primary component categories with their IDs.

    Returns:
        List of categories with id, name, part count, and subcategory count.
        Use category_id with search/search_api, or call get_subcategories for more specific filtering.

    Note: Categories are fetched from JLCPCB API on server startup and cached.
    """
    if not _categories:
        return {"error": "Categories not loaded", "categories": []}

    return {
        "categories": [
            {
                "id": cat["id"],
                "name": cat["name"],
                "count": cat["count"],
                "subcategory_count": len(cat.get("subcategories", [])),
            }
            for cat in _categories
        ]
    }


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Subcategories",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_get_subcategories(category_id: int) -> dict:
    """Get all subcategories for a specific category.

    Args:
        category_id: Primary category ID (e.g., 1 for Resistors, 2 for Capacitors)

    Returns:
        List of subcategories with id, name, and part count.
        Pass subcategory_id to search() for filtered searches.

    Note: Categories are fetched from JLCPCB API on server startup and cached.
    """
    # Find category in live cache
    category = next((c for c in _categories if c["id"] == category_id), None)
    if not category:
        return {"error": f"Category {category_id} not found"}

    return {
        "category_id": category_id,
        "category_name": category["name"],
        "subcategories": [
            {"id": sub["id"], "name": sub["name"], "count": sub["count"]}
            for sub in category.get("subcategories", [])
        ],
    }


@mcp.tool(
    annotations=ToolAnnotations(
        title="Find Alternative Parts",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_find_alternatives(
    lcsc: str,
    min_stock: int = DEFAULT_MIN_STOCK,
    same_package: bool = False,
    library_type: str | None = None,
    has_easyeda_footprint: bool | None = None,
    limit: int = 10,
) -> dict:
    """Find alternative parts similar to a given component.

    Searches the same subcategory for parts with better availability.
    Useful when a part has low stock or you want to compare options.

    Args:
        lcsc: LCSC part code to find alternatives for (e.g., "C2557")
        min_stock: Minimum stock for alternatives (default: DEFAULT_MIN_STOCK)
        same_package: If True, only return parts with the same package size
        library_type: Filter alternatives by library type:
            - "basic": Only basic parts (no assembly fee)
            - "preferred": Only preferred parts (no assembly fee)
            - "no_fee": Basic or preferred (no assembly fee) - best for cost optimization
            - "extended": Only extended parts ($3 assembly fee each)
            - "all" or None (default): All library types
            Use "no_fee" to find cheaper alternatives for an extended part.
        has_easyeda_footprint: Filter by EasyEDA footprint availability:
            - True: Only return parts WITH EasyEDA footprints (for Atopile/KiCad users)
            - False: Only return parts WITHOUT footprints
            - None (default): Don't filter by footprint (fastest)
            Note: Filtering by footprint is slower as it checks each alternative.
        limit: Maximum alternatives to return (default: 10, max: 50)

    Returns:
        Original part info (with library_type and has_easyeda_footprint) and list of alternatives
        sorted by stock. Alternatives include library_type and specs for easy comparison.
        When filtering by footprint, alternatives also include EasyEDA UUIDs.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    return await _client.find_alternatives(
        lcsc=lcsc,
        min_stock=min_stock,
        same_package=same_package,
        library_type=library_type if library_type != "all" else None,
        has_easyeda_footprint=has_easyeda_footprint,
        limit=limit,
    )


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Component Pinout",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_get_pinout(lcsc: str | None = None, uuid: str | None = None) -> dict:
    """Get pin information for a component from EasyEDA symbol data.

    Returns raw pin data exactly as EasyEDA provides it, with no interpretation
    or guessing. Pin names are descriptive (VCC, GND, PA0, etc.) and can be
    read directly by LLMs and users.

    Args:
        lcsc: LCSC part code (e.g., "C8304"). If provided, fetches UUID automatically.
        uuid: EasyEDA symbol UUID directly (alternative to lcsc)

    One of lcsc or uuid must be provided.

    Returns:
        Pin mapping with:
        - lcsc: LCSC code (if provided)
        - model: Part model/name
        - manufacturer: Manufacturer name
        - package: Package type
        - pin_count: Total number of pins
        - pins: List of pins, each with:
            - number: Physical pin number (e.g., "1", "2")
            - name: Pin name exactly as in EasyEDA symbol
            - electrical: (rare) EasyEDA electrical type if set by symbol creator
        - easyeda_symbol_uuid: UUID to view symbol at easyeda.com/component/{uuid}
        - unverified: (only if true) "Symbol not verified by LCSC"

    The electrical field is only included when the symbol creator explicitly
    set it in EasyEDA. Values: "input", "output", "bidirectional", "power".
    Most symbols don't set this field.

    Example output for STM32F103CBT6:
        {"pin_count": 48, "pins": [
            {"number": "1", "name": "VBAT"},
            {"number": "2", "name": "PC13-TAMPER-RTC"},
            {"number": "10", "name": "PA0_WKUPUSART2_CTSADC12_IN0TIM2_CH1_ETR"},
            ...
        ]}

    Example output for MOSFET AO3400:
        {"pin_count": 3, "pins": [
            {"number": "1", "name": "G"},
            {"number": "2", "name": "S"},
            {"number": "3", "name": "D"}
        ]}

    Example output for RP2040 (has electrical types):
        {"pin_count": 57, "pins": [
            {"number": "1", "name": "1", "electrical": "bidirectional"},
            {"number": "2", "name": "2", "electrical": "bidirectional"},
            ...
        ]}
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    if not lcsc and not uuid:
        return {"error": "Must provide either lcsc or uuid"}

    part = None
    symbol_uuid = uuid

    if lcsc:
        # Normalize LCSC code
        lcsc = lcsc.strip().upper()

        # Get UUID and part details from LCSC code
        part = await _client.get_part(lcsc)
        if not part:
            return {"error": f"Part not found: {lcsc}"}

        if not part.get("has_easyeda_footprint"):
            return {"error": f"No EasyEDA symbol available for {lcsc}"}

        symbol_uuid = part.get("easyeda_symbol_uuid")
        if not symbol_uuid:
            return {"error": f"No EasyEDA symbol UUID for {lcsc}"}

    try:
        # Fetch EasyEDA component data
        easyeda_data = await _client.get_easyeda_component(symbol_uuid)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to fetch EasyEDA data: {e}"}

    # Check for valid response
    if not easyeda_data or not isinstance(easyeda_data, dict):
        return {"error": f"Invalid EasyEDA response for {lcsc or symbol_uuid}"}

    # Parse pins from EasyEDA data
    pins = parse_easyeda_pins(easyeda_data)

    if not pins:
        return {"error": "Invalid EasyEDA response - missing pin data"}

    result = {
        "lcsc": lcsc,
        "model": part.get("model") if part else None,
        "manufacturer": part.get("manufacturer") if part else None,
        "package": part.get("package") if part else None,
        "pin_count": len(pins),
        "pins": pins,
        "easyeda_symbol_uuid": symbol_uuid,
    }

    # Flag unverified symbols
    if not easyeda_data.get("verify", True):
        result["unverified"] = "Symbol not verified by LCSC"

    return result


async def _process_bom(
    parts: list[dict[str, Any]],
    board_qty: int | None = None,
    min_stock: int = 0,
) -> tuple[list[BOMPart], list[BOMIssue], dict[str, Any]]:
    """Process BOM parts: validate, fetch, and calculate costs.

    Internal helper used by both validate_bom and export_bom.

    Returns:
        Tuple of (processed parts, issues, summary)

    Raises:
        ValueError: If board_qty is <= 0
    """
    # Validate board_qty
    if board_qty is not None and board_qty <= 0:
        raise ValueError(f"board_qty must be positive, got {board_qty}")

    issues: list[BOMIssue] = []

    # Step 1: Validate designators (check for duplicates and empty)
    issues.extend(validate_designators(parts))

    # Step 2: Merge duplicate LCSC codes
    merged_parts, merge_issues = merge_duplicate_parts(parts)
    issues.extend(merge_issues)

    # Step 3: Validate manual parts have required fields
    for part in merged_parts:
        if not part.get("lcsc"):
            issues.extend(validate_manual_part(part))

    # Step 4: Fetch LCSC parts from local database (faster, no API calls)
    lcsc_codes = [p["lcsc"] for p in merged_parts if p.get("lcsc")]
    db = get_db()
    fetched_parts = db.get_by_lcsc_batch(lcsc_codes) if lcsc_codes else {}

    # Step 5: Build BOMPart objects
    bom_parts: list[BOMPart] = []

    for part in merged_parts:
        lcsc = part.get("lcsc")
        designators = part.get("designators", [])
        user_comment = part.get("comment")
        user_footprint = part.get("footprint")

        if lcsc:
            lcsc = lcsc.strip().upper()
            fetched = fetched_parts.get(lcsc)

            if not fetched:
                issues.append(BOMIssue(
                    lcsc=lcsc,
                    designators=designators,
                    severity="error",
                    issue="Part not found",
                ))
                # Create minimal BOMPart for tracking
                bom_parts.append(BOMPart(
                    lcsc=lcsc,
                    designators=designators,
                    quantity=len(designators),
                    comment=user_comment or "Unknown",
                    footprint=user_footprint or "Unknown",
                ))
                continue

            # Check footprint mismatch
            if user_footprint:
                mismatch = check_footprint_mismatch(user_footprint, fetched.get("package"))
                if mismatch:
                    mismatch.lcsc = lcsc
                    mismatch.designators = designators
                    issues.append(mismatch)

            # Calculate pricing
            # DB stores single price, API returns price tiers - handle both
            db_price = fetched.get("price")
            prices = fetched.get("prices", [])
            if db_price is not None and not prices:
                # Convert single price to simple tier format
                prices = [{"qty": "1+", "price": db_price}]
            order_qty, unit_price, line_cost = calculate_line_cost(
                prices, len(designators), board_qty
            )

            bom_part = BOMPart(
                lcsc=lcsc,
                designators=designators,
                quantity=len(designators),
                comment=generate_comment(fetched, user_comment),
                footprint=user_footprint or fetched.get("package", "Unknown"),
                stock=fetched.get("stock"),
                price=unit_price,
                order_qty=order_qty,
                line_cost=line_cost,
                library_type=fetched.get("library_type"),
                min_order=fetched.get("min_order"),
                manufacturer=fetched.get("manufacturer"),
                model=fetched.get("model"),
                has_easyeda_footprint=fetched.get("has_easyeda_footprint"),
            )
            bom_parts.append(bom_part)

            # Check for stock issues
            issues.extend(check_stock_issues(bom_part, min_stock, board_qty))

            # Check MOQ
            moq_issue = check_moq_issue(bom_part)
            if moq_issue:
                issues.append(moq_issue)

            # Check extended part
            ext_issue = check_extended_part(bom_part)
            if ext_issue:
                issues.append(ext_issue)

            # Check EasyEDA footprint
            eda_issue = check_easyeda_footprint(bom_part)
            if eda_issue:
                issues.append(eda_issue)

        else:
            # Manual part (no LCSC)
            bom_parts.append(BOMPart(
                lcsc=None,
                designators=designators,
                quantity=len(designators),
                comment=user_comment or "Unknown",
                footprint=user_footprint or "Unknown",
                order_qty=len(designators) * (board_qty or 1),
            ))

    # Step 6: Sort by designator
    sorted_parts = sort_by_designator(bom_parts)

    # Step 7: Generate summary
    summary = generate_summary(sorted_parts, board_qty, issues)

    return sorted_parts, issues, summary


@mcp.tool(
    annotations=ToolAnnotations(
        title="Validate BOM",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_validate_bom(
    parts: list[dict[str, Any]] | str,
    board_qty: int | None = None,
    min_stock: int = 0,
) -> dict:
    """Validate a BOM and check part availability without generating CSV.

    Use this for iterative checking during part selection. For final export,
    use export_bom instead.

    Args:
        parts: List of parts, each with:
            - lcsc: (optional) LCSC code like "C1525". If provided, auto-fetches details.
            - designators: (required) List of designators, e.g., ["C1", "C2", "C3"]
            - comment: (optional) Override auto-generated comment, or provide for manual parts
            - footprint: (optional) Override auto-fetched footprint, or provide for manual parts
        board_qty: (optional) Number of boards. Validates stock against total needed.
            Example: board_qty=100 with 3× C1525 per board needs 300 in stock.
        min_stock: (optional) Minimum stock threshold for warnings. Ignored if board_qty provided.

    Returns:
        parts: Structured data for each BOM line with lcsc, designators, quantity,
               comment, footprint, stock, price, order_qty, line_cost, library_type,
               min_order, manufacturer, model, has_easyeda_footprint.
        summary: total_line_items, total_components, estimated_cost, extended_parts_count,
                 extended_parts_fee, total_with_fees, board_qty, stock_sufficient.
        issues: List of problems found. Each has lcsc, designators, severity (error/warning),
                and human-readable issue description. Common issues:
                - "Part not found" (error)
                - "Out of stock (0 available)" (error)
                - "Insufficient stock: need X, have Y" (error)
                - "Duplicate designator: X appears multiple times" (error)
                - "Extended part: +$X assembly fee" (warning)
                - "No EasyEDA footprint available" (warning)

    Note: Issues are reported but don't block the response. Caller decides whether to proceed.
    """
    # Parse and validate parts parameter
    parsed_parts = _parse_parts_param(parts)
    if validation_error := _validate_bom_parts(parsed_parts):
        return validation_error

    try:
        sorted_parts, issues, summary = await _process_bom(parsed_parts, board_qty, min_stock)
    except ValueError as e:
        return {"error": str(e)}

    return {
        "parts": [
            {
                "lcsc": p.lcsc,
                "designators": p.designators,
                "designators_str": p.designators_str,
                "quantity": p.quantity,
                "comment": p.comment,
                "footprint": p.footprint,
                "stock": p.stock,
                "price": p.price,
                "order_qty": p.order_qty,
                "line_cost": p.line_cost,
                "library_type": p.library_type,
                "min_order": p.min_order,
                "manufacturer": p.manufacturer,
                "model": p.model,
                "has_easyeda_footprint": p.has_easyeda_footprint,
            }
            for p in sorted_parts
        ],
        "summary": summary,
        "issues": [
            {
                "lcsc": i.lcsc,
                "designators": i.designators,
                "severity": i.severity,
                "issue": i.issue,
            }
            for i in issues
        ],
    }


@mcp.tool(
    annotations=ToolAnnotations(
        title="Export BOM",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_export_bom(
    parts: list[dict[str, Any]] | str,
    board_qty: int | None = None,
    min_stock: int = 0,
) -> dict:
    """Generate a JLCPCB-compatible BOM CSV file.

    Same as validate_bom but also generates CSV output for upload to JLCPCB.

    Args:
        parts: List of parts, each with:
            - lcsc: (optional) LCSC code like "C1525". If provided, auto-fetches details.
            - designators: (required) List of designators, e.g., ["C1", "C2", "C3"]
            - comment: (optional) Override auto-generated comment, or provide for manual parts
            - footprint: (optional) Override auto-fetched footprint, or provide for manual parts
        board_qty: (optional) Number of boards. Validates stock against total needed.
        min_stock: (optional) Minimum stock threshold for warnings.

    Returns:
        csv: JLCPCB-compatible CSV content (Comment,Designator,Footprint,LCSC Part #)
        parts: Structured data for each BOM line (same as validate_bom)
        summary: Cost and count summary (same as validate_bom)
        issues: List of problems found (same as validate_bom)

    CSV Format:
        Comment,Designator,Footprint,LCSC Part #
        100nF 50V X7R 0402,"C1,C2,C3",0402,C1525
        10K 1% 0603,"R1,R2",0603,C25804

    Note: Prices are estimates and may change. Stock validation is point-in-time.
    """
    # Parse and validate parts parameter
    parsed_parts = _parse_parts_param(parts)
    if validation_error := _validate_bom_parts(parsed_parts):
        return validation_error

    try:
        sorted_parts, issues, summary = await _process_bom(parsed_parts, board_qty, min_stock)
    except ValueError as e:
        return {"error": str(e)}

    # Generate CSV
    csv_content = generate_csv(sorted_parts)

    return {
        "csv": csv_content,
        "parts": [
            {
                "lcsc": p.lcsc,
                "designators": p.designators,
                "designators_str": p.designators_str,
                "quantity": p.quantity,
                "comment": p.comment,
                "footprint": p.footprint,
                "stock": p.stock,
                "price": p.price,
                "order_qty": p.order_qty,
                "line_cost": p.line_cost,
                "library_type": p.library_type,
                "min_order": p.min_order,
                "manufacturer": p.manufacturer,
                "model": p.model,
                "has_easyeda_footprint": p.has_easyeda_footprint,
            }
            for p in sorted_parts
        ],
        "summary": summary,
        "issues": [
            {
                "lcsc": i.lcsc,
                "designators": i.designators,
                "severity": i.severity,
                "issue": i.issue,
            }
            for i in issues
        ],
    }


@mcp.tool(
    annotations=ToolAnnotations(
        title="Mouser Search",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def mouser_search(
    keyword: str,
    manufacturer: str | None = None,
    in_stock_only: bool = False,
    limit: int = 20,
    page: int = 1,
) -> dict:
    """Search Mouser's catalog by keyword. Useful for cross-referencing parts, finding datasheets, and checking broader availability.

    Args:
        keyword: Search terms (e.g., "STM32F103", "LM358", "100nF 0402")
        manufacturer: Filter by manufacturer name (e.g., "Texas Instruments")
        in_stock_only: Only return in-stock parts (default False)
        limit: Results per page (1-50, default 20)
        page: Page number (default 1)

    Returns:
        results: List of parts with mouser_pn, mfr_pn, manufacturer, description,
                 category, stock, price, price_breaks, datasheet_url, product_url, rohs, lifecycle
        total: Total matching results
        page: Current page number
    """
    if not _mouser_client:
        return {"error": "Mouser API key not configured. Set MOUSER_API_KEY in environment."}
    if keyword and len(keyword) > 500:
        return {"error": "Keyword too long (max 500 characters)"}

    try:
        return await _mouser_client.search(
            keyword=keyword,
            manufacturer=manufacturer,
            in_stock_only=in_stock_only,
            records=max(1, min(limit, 50)),
            page=max(1, page),
        )
    except MouserAPIError as e:
        logger.error(f"Mouser search failed: {e}")
        if e.code == "NotFound":
            return {"error": "Manufacturer not found on Mouser. Try searching without the manufacturer filter, or use a different spelling."}
        return {"error": "Mouser search failed. Check server logs for details."}
    except Exception as e:
        logger.error(f"Mouser search failed: {type(e).__name__}: {e}")
        return {"error": "Mouser search failed. Check server logs for details."}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Mouser Part Lookup",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def mouser_get_part(part_number: str) -> dict:
    """Look up parts on Mouser by part number or MPN. Supports batch lookup with pipe-delimited numbers.

    Args:
        part_number: Mouser part number or manufacturer PN (e.g., "595-LM358P" or "LM358P").
                     For batch lookup, pipe-delimit up to 10 numbers: "595-LM358P|511-LM358P"

    Returns:
        results: Full part details including all attributes, pricing tiers, availability, datasheet
        total: Number of parts found
    """
    if not _mouser_client:
        return {"error": "Mouser API key not configured. Set MOUSER_API_KEY in environment."}
    if part_number and len(part_number) > 500:
        return {"error": "Part number too long (max 500 characters)"}

    try:
        return await _mouser_client.get_part(part_number)
    except Exception as e:
        logger.error(f"Mouser part lookup failed: {type(e).__name__}: {e}")
        return {"error": "Mouser part lookup failed. Check server logs for details."}


@mcp.tool(
    annotations=ToolAnnotations(
        title="DigiKey Search",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def digikey_search(
    keywords: str,
    manufacturer: str | None = None,
    in_stock_only: bool = False,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """Search DigiKey's catalog by keyword. Useful for cross-referencing parts, finding datasheets, and checking broader availability.

    Args:
        keywords: Search terms (e.g., "STM32F103", "LM358", "100nF 0402")
        manufacturer: Filter by manufacturer name (e.g., "Texas Instruments")
        in_stock_only: Only return in-stock parts (default False)
        limit: Results per page (1-50, default 20)
        offset: Pagination offset (default 0)

    Returns:
        results: List of parts with digikey_pn, mfr_pn, manufacturer, description,
                 category, stock, price, price_breaks, datasheet_url, product_url, rohs, parameters
        total: Total matching results
        offset: Current pagination offset
    """
    if not _digikey_client:
        return {"error": "DigiKey API credentials not configured. Set DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET in environment."}
    if keywords and len(keywords) > 500:
        return {"error": "Keywords too long (max 500 characters)"}

    try:
        return await _digikey_client.search(
            keywords=keywords,
            manufacturer=manufacturer,
            in_stock_only=in_stock_only,
            limit=max(1, min(limit, 50)),
            offset=max(0, offset),
        )
    except Exception as e:
        logger.error(f"DigiKey search failed: {type(e).__name__}: {e}")
        return {"error": "DigiKey search failed. Check server logs for details."}


@mcp.tool(
    annotations=ToolAnnotations(
        title="DigiKey Part Lookup",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def digikey_get_part(product_number: str) -> dict:
    """Look up a part on DigiKey by product number.

    Args:
        product_number: DigiKey part number or manufacturer PN (e.g., "296-1395-5-ND" or "LM358P")

    Returns:
        Full product details including all parameters, pricing variations, availability, datasheet
    """
    if not _digikey_client:
        return {"error": "DigiKey API credentials not configured. Set DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET in environment."}
    if product_number and len(product_number) > 500:
        return {"error": "Product number too long (max 500 characters)"}

    try:
        return await _digikey_client.get_part(product_number)
    except Exception as e:
        logger.error(f"DigiKey part lookup failed: {type(e).__name__}: {e}")
        return {"error": "DigiKey part lookup failed. Check server logs for details."}


@mcp.tool(
    annotations=ToolAnnotations(
        title="CSE Search (ECAD Models)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def cse_search(
    query: str,
    limit: int = 5,
) -> dict:
    """Search SamacSys ComponentSearchEngine for ECAD model availability and datasheets.

    Use this to check if KiCad/Eagle/Altium symbols, footprints, and 3D models exist for a part.
    No API key required.

    Args:
        query: MPN or keyword (e.g., "LM358P", "STM32F103", "ESP32")
        limit: Max results to return (1-10, default 5)

    Returns:
        results: List of parts with mfr_part_number, manufacturer, description,
                 datasheet_url, has_model (symbol/footprint available),
                 has_3d (3D model available), model_quality (0-4),
                 cse_part_id, pin_count, image_url
        total: Total matching results
    """
    if not _cse_client:
        return {"error": "CSE client not initialized"}
    if query and len(query) > 500:
        return {"error": "Query too long (max 500 characters)"}

    limit = max(1, min(limit, 10))

    try:
        result = await _cse_client.search(query)
        # Return a new dict to avoid mutating the cached result
        return {
            "results": result["results"][:limit],
            "total": result["total"],
        }
    except Exception as e:
        logger.error(f"CSE search failed: {type(e).__name__}: {e}")
        return {"error": "CSE search failed. Check server logs for details."}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get KiCad Symbol & Footprint",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def cse_get_kicad(
    query: str | None = None,
    part_id: int | None = None,
) -> dict:
    """Get KiCad schematic symbol and PCB footprint for any component.

    Downloads from SamacSys ComponentSearchEngine. Works for any manufacturer's part,
    not limited to JLCPCB. Returns the raw .kicad_sym and .kicad_mod file contents
    as text that can be read directly or saved to a KiCad project.

    Args:
        query: MPN to search for (e.g., "LM358P", "STM32F103CBT6", "ESP32-WROOM-32E").
               Finds the best matching part with an available model.
        part_id: CSE part ID from a previous cse_search result (skips search step).
               Use this if you already know the exact part.

    One of query or part_id must be provided.

    Returns:
        kicad_symbol: Raw .kicad_sym file content (pin names, types, graphical symbol)
        kicad_footprint: Raw .kicad_mod file content (pad layout, silkscreen, courtyard)
        part_id: CSE part ID (for future lookups)
        mfr_part_number, manufacturer, description: Part metadata (when searched by query)
    """
    if not _cse_client:
        return {"error": "CSE client not initialized"}

    if not query and not part_id:
        return {"error": "Must provide either query or part_id"}
    if query and len(query) > 500:
        return {"error": "Query too long (max 500 characters)"}

    try:
        return await _cse_client.get_kicad(query=query, part_id=part_id)
    except Exception as e:
        logger.error(f"CSE get_kicad failed: {type(e).__name__}: {e}")
        return {"error": "CSE get_kicad failed. Check server logs for details."}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Server Version",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def get_version() -> dict:
    """Get server version and health status."""
    return {
        "service": "pcbparts-mcp",
        "version": __version__,
        "status": "healthy",
    }


# Health check endpoint
async def health(request):
    return JSONResponse({
        "status": "healthy",
        "service": "pcbparts-mcp",
        "version": __version__,
    })


# Create ASGI app
def create_app():
    """Create the ASGI application."""
    # Middleware list - rate limiting only (FastMCP handles CORS for MCP endpoints)
    middleware = [
        Middleware(RateLimitMiddleware, requests_per_minute=RATE_LIMIT_REQUESTS),
    ]

    # stateless_http=True required because Claude Code doesn't forward session cookies
    app = mcp.http_app(
        path="/mcp",
        middleware=middleware,
        transport="streamable-http",
        stateless_http=True,
    )

    # Add health check route
    app.routes.append(Route("/health", health))

    return app


app = create_app()


def main():
    """Run the server."""
    import uvicorn
    uvicorn.run(
        "pcbparts_mcp.server:app",
        host="0.0.0.0",
        port=HTTP_PORT,
        lifespan="on",
    )


if __name__ == "__main__":
    main()
