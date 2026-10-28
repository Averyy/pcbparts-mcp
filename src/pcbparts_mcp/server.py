"""PCB Parts MCP Server - Search electronic components for PCB assembly."""

import asyncio
import contextlib
import json
import logging
import math
import re
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from difflib import get_close_matches
from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import NotFoundError, ValidationError
from fastmcp.server.dependencies import get_http_request
from fastmcp.server.middleware import Middleware as FastMCPMiddleware
from mcp.types import ToolAnnotations
from pydantic import BeforeValidator
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import __version__, stats
from .cache import DailyQuota, QuotaStore
from .config import (
    RATE_LIMIT_REQUESTS, HTTP_PORT, DEFAULT_MIN_STOCK, MAX_PAGE_SIZE,
    MOUSER_API_KEY, DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET, CSE_USER,
    DISTRIBUTOR_DAILY_LIMIT, DIGIKEY_PER_MINUTE, MOUSER_PER_MINUTE, MAX_ALTERNATIVES,
    clamp_limit, MAX_LIST_PARAM_ITEMS, MAX_MEASURE_ITEMS, MAX_REQUEST_BODY_BYTES,
    ALLOWED_HOSTS, ALLOWED_ORIGINS, EASYEDA_STORE_PATH, DISTRIBUTOR_QUOTA_PATH, USAGE_STATS_PATH,
    CSE_STORE_PATH,
)
from .client import EasyEDAComponentNotFound, JLCPCBClient
from .mouser import MouserAPIError, MouserClient, MouserError
from .digikey import DigiKeyClient, DigiKeyError
from .cse import CSEClient
from .db_worker import BOARD_POOL, COMPONENT_POOL, RULES_POOL, SENSOR_POOL, offload, run_db
from .db import get_db, close_db
from .sensor_db import get_sensor_db, close_sensor_db
from .boards_db import get_boards_db, close_boards_db
from .search import SpecFilter, get_attribute_names
from .search.mpn import looks_like_mpn, mpn_key
from .search.query_builder import package_family_adjustments
from .smart_parser import ParsedQuery, parse_smart_query, merge_spec_filters
from .alternatives import SPEC_PARSERS
from .search.spec_filter import ATTRIBUTE_ALIASES, SPEC_TO_COLUMN, ConnectorFilter, FuseFilter
from .pinout import parse_easyeda_pins
from .design_rules import get_design_rules as _get_design_rules, _RULES_DIR, _build_index

logger = logging.getLogger(__name__)

# Global state
_client: JLCPCBClient | None = None
_mouser_client: MouserClient | None = None
_digikey_client: DigiKeyClient | None = None
_cse_client: CSEClient | None = None
_categories: list[dict[str, Any]] = []  # Live category cache
_distributor_quotas: dict[str, DailyQuota] = {}  # "mouser"/"digikey" when configured, for /health
_easyeda_seeded = 0  # rows in the seed table, counted at startup (components.db doesn't change)
_easyeda_stored: tuple[float, int | None] = (float("-inf"), None)  # (time.monotonic(), store size)
_cse_stored: tuple[float, dict[str, int] | None] = (float("-inf"), None)  # (time.monotonic(), store counts)

# /health is public, isn't rate limited and is fetched by every landing page visit, so the store
# count it shows is refreshed at most this often (seconds) instead of on every request.
HEALTH_STORE_COUNT_TTL = 60


@asynccontextmanager
async def lifespan(app):
    """Manage client lifecycle, build DB, and load categories on startup."""
    global _client, _mouser_client, _digikey_client, _cse_client, _categories, _easyeda_seeded, _easyeda_stored
    _client = JLCPCBClient(easyeda_store_path=EASYEDA_STORE_PATH or None)

    # Build/load DB on startup (not on first request)
    db = get_db()
    db._ensure_db()
    db_stats = db.get_stats()
    logger.info(f"Database ready: {db_stats.get('total_parts', 0)} parts")

    # Load categories from DB (updated daily by scraper, no API call needed)
    _categories = db.get_categories_for_client()
    _client.set_categories(_categories)
    logger.info(f"Loaded {len(_categories)} categories from database")

    # Seeded EasyEDA footprint answers (data/easyeda/footprints.csv, built into the DB)
    _client.set_easyeda_seed(db.get_easyeda_seed)
    # jlc_find_alternatives also looks in the database for parts that meet the rules
    _client.set_alternative_candidates(db.find_alternative_candidates)
    _easyeda_seeded = db.easyeda_seed_size()
    store_size = _client.easyeda_store_size()
    _easyeda_stored = (time.monotonic(), store_size)
    logger.info(f"EasyEDA footprints: {_easyeda_seeded:,} seeded, " + (
        f"{store_size:,} stored in {EASYEDA_STORE_PATH}" if store_size is not None else "no store (memory only)"))

    # Initialize sensor database (non-fatal if unavailable)
    try:
        sensor_db = get_sensor_db()
        sensor_db._ensure_db()
        sensor_stats = sensor_db.get_stats()
        logger.info(f"Sensor database: {sensor_stats.get('total_sensors', 0)} sensors")
    except Exception as e:
        logger.warning(f"Sensor database not available: {e}")

    # Initialize boards database (non-fatal if unavailable)
    try:
        boards_db = get_boards_db()
        boards_db._ensure_db()
        boards_stats = boards_db.get_stats()
        logger.info(f"Boards database: {boards_stats.get('total_boards', 0)} boards")
    except Exception as e:
        logger.warning(f"Boards database not available: {e}")

    # Validate design rules directory (non-fatal if unavailable)
    if _RULES_DIR.is_dir():
        from . import design_rules
        design_rules._index = _build_index(_RULES_DIR)
        logger.info(f"Design rules: {len(design_rules._index)} rule files")
    else:
        logger.warning(f"Design rules directory not found: {_RULES_DIR}")

    # Mouser/DigiKey daily request counts, kept across restarts when DISTRIBUTOR_QUOTA_PATH is set
    quota_store = QuotaStore(DISTRIBUTOR_QUOTA_PATH) if DISTRIBUTOR_QUOTA_PATH else None
    _distributor_quotas.clear()

    # Initialize Mouser client if API key is configured
    if MOUSER_API_KEY:
        mouser_quota = DailyQuota("Mouser", DISTRIBUTOR_DAILY_LIMIT, store=quota_store, per_minute=MOUSER_PER_MINUTE,
                                  own_key="Mouser API key (free at https://www.mouser.com/api-hub/)")
        _distributor_quotas["mouser"] = mouser_quota
        _mouser_client = MouserClient(MOUSER_API_KEY, quota=mouser_quota)
        logger.info(f"Mouser client initialized (requests today: {mouser_quota.status()['used_today']})")

    # Initialize DigiKey client if credentials are configured
    if DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET:
        digikey_quota = DailyQuota("DigiKey", DISTRIBUTOR_DAILY_LIMIT, store=quota_store, per_minute=DIGIKEY_PER_MINUTE,
                                   own_key="DigiKey API credentials (free at https://developer.digikey.com)")
        _distributor_quotas["digikey"] = digikey_quota
        _digikey_client = DigiKeyClient(DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET, quota=digikey_quota)
        logger.info(f"DigiKey client initialized (requests today: {digikey_quota.status()['used_today']})")

    if _distributor_quotas:
        logger.info(f"Distributor request counts: {f'kept in {quota_store.path}' if quota_store else 'memory only'}")

    # Anonymous daily usage counts for /mcp/stats
    if USAGE_STATS_PATH:
        stats.usage.open(USAGE_STATS_PATH)
    stats.usage.tools = {tool.name for tool in await mcp.list_tools(run_middleware=False)}
    logger.info(f"Usage stats: {f'kept in {USAGE_STATS_PATH}' if USAGE_STATS_PATH else 'memory only'}")
    minute_task = asyncio.create_task(_every_minute())

    # CSE client always available (no API key needed)
    _cse_client = CSEClient(store_path=CSE_STORE_PATH or None)
    cse_counts = _cse_client.store_counts()
    logger.info("CSE client initialized: " + (
        f"{cse_counts['searches']:,} searches and {cse_counts['kicad']:,} KiCad parts stored in {CSE_STORE_PATH}"
        if cse_counts is not None else "no store (memory only)"))

    yield

    minute_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await minute_task
    for quota in _distributor_quotas.values():
        quota.callers.flush()  # the hour so far, so a deploy doesn't lose it
    stats.usage.save()
    if _cse_client:
        await _cse_client.close()
    if _mouser_client:
        await _mouser_client.close()
    if _digikey_client:
        await _digikey_client.close()
    if _client:
        await _client.close()
    await run_db(COMPONENT_POOL, close_db)
    await run_db(SENSOR_POOL, close_sensor_db)
    await run_db(BOARD_POOL, close_boards_db)


async def _every_minute() -> None:
    """Every minute, log the finished hour's per-IP Mouser/DigiKey request counts (one line each)
    and save the usage counts."""
    while True:
        await asyncio.sleep(60)
        try:
            for quota in _distributor_quotas.values():
                quota.callers.flush_if_due()
            stats.usage.save()
        except Exception:
            logger.exception("Minute task failed; trying again in a minute")


# Create MCP server
mcp = FastMCP(
    name="pcbparts",
    instructions="PCB design assistant: JLCPCB part search, Mouser and DigiKey lookups, reference boards, sensor picks and design rules. No auth. Find parts with jlc_search (local, fast, parametric filters); jlc_stock_check only for live stock or out-of-stock parts; mouser_get_part/digikey_get_part only to cross-reference specific part numbers (shared daily limit; batch Mouser lookups). sensor_recommend picks sensors by measurement, protocol or platform. Workflow: get_design_rules / board_search + board_get(focus=IC) → jlc_search → jlc_get_part (datasheet, footprint) → jlc_find_alternatives → cse_get_kicad (KiCad files).",
    lifespan=lifespan,
    # Don't leak raw exception text (SQL, file paths, internals) to anonymous clients.
    # Intentional user-facing errors are returned as dicts, not raised, so masking is UX-free.
    mask_error_details=True,
)


# Our error replies, sorted for the usage counts by the start of their text (stats.OUTCOMES). Anchored
# at the start because many messages end with what the user typed. A message that matches none of
# these counts as "failed", so an unexpected failure shows up. tests/test_usage_stats.py checks every
# error message in the code against this list.
_ERROR_KINDS = [(kind, re.compile(pattern)) for kind, pattern in (
    # a limit turned the request away: ours, Mouser's, DigiKey's, JLCPCB's or EasyEDA's
    ("rate_limited", r"\w+ daily quota exceeded "),
    ("rate_limited", r"\w+ lookups are limited to "),
    ("rate_limited", r"\w+ is limiting requests"),
    ("rate_limited", r"\w+ refused this server's requests"),
    ("rate_limited", r"JLCPCB rate limited"),
    ("rate_limited", r"Couldn't check EasyEDA for .* right now"),
    # the request was invalid
    ("bad_request", r"(Subcategory|Category) not found: "),
    ("bad_request", r"Subcategory ID \S+ not found$"),
    ("bad_request", r"[\w ]+ too long \(max \d+ characters\)$"),
    ("bad_request", r"Too many "),
    ("bad_request", r"Invalid [\w ]+: "),
    ("bad_request", r"Strict search cannot apply every constraint; "),
    ("bad_request", r"Unsupported (library_type|tag|value for \w+): "),
    ("bad_request", r"Must provide "),
    ("bad_request", r"lcsc must be "),
    ("bad_request", r"board_quantity and placements_per_board must be "),
    ("bad_request", r"Give (a|at least one) "),
    ("bad_request", r"Mouser takes up to "),
    ("bad_request", r"Each Mouser part number must be "),
    ("bad_request", r"Query contains (invalid characters|no searchable terms)$"),
    ("bad_request", r"(Invalid slug|Invalid UUID format|UUID is required)$"),
    # it worked and found nothing
    ("not_found", r"Part not found: "),
    ("not_found", r"Part .* not found$"),
    ("not_found", r"Board '.*' not found$"),
    ("not_found", r"No (JLCPCB parts|parts) found for "),
    ("not_found", r"No ECAD model available for "),
    ("not_found", r"No KiCad files found in model archive "),
    ("not_found", r"No EasyEDA symbol (available|UUID) for "),
    ("not_found", r"EasyEDA has no symbol "),
)]


def _error_kind(message: str) -> str:
    return next((kind for kind, pattern in _ERROR_KINDS if pattern.match(message)), "failed")


def _call_outcome(result: Any) -> str:
    """For the usage counts, how a tool call that returned went (stats.OUTCOMES)."""
    content = getattr(result, "structured_content", None)
    if not isinstance(content, dict):
        return "ok"
    if content.get("error"):
        return _error_kind(str(content["error"]))
    if "alternatives" in content:
        if content["alternatives"]:
            return "ok"
        return "similar_only" if (content.get("similar_parts") or content.get("unverified_alternatives")) else "not_found"
    if any(key in content and not content[key] for key in ("results", "matched_files")):
        return "not_found"
    return "ok"


def _exception_outcome(error: Exception) -> str:
    """For the usage counts, how a tool call that raised went: bad arguments or an unknown tool are
    the caller's mistake; anything else broke here."""
    return "bad_request" if isinstance(error, (ValidationError, NotFoundError)) else "failed"


class UsageStatsMiddleware(FastMCPMiddleware):
    """Counts tool calls and connecting apps for /mcp/stats (stats.py). Counting never breaks a call."""

    async def on_initialize(self, context, call_next):
        try:
            client_info = context.message.params.clientInfo
            stats.usage.record_app(client_info.name if client_info else None)
        except Exception:
            logger.exception("Usage stats: couldn't count an app")
        return await call_next(context)

    async def on_call_tool(self, context, call_next):
        start = time.monotonic()
        try:
            result = await call_next(context)
        except Exception as e:
            self._record(context, start, error=e)
            raise
        self._record(context, start, result=result)
        return result

    @staticmethod
    def _record(context, start: float, result: Any = None, error: Exception | None = None) -> None:
        try:
            outcome = _exception_outcome(error) if error is not None else _call_outcome(result)
            stats.usage.record_call(context.message.name, outcome, (time.monotonic() - start) * 1000, _caller_ip())
        except Exception:
            logger.exception("Usage stats: couldn't count a tool call")


mcp.add_middleware(UsageStatsMiddleware())


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
        return _client_ip(request)

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


def _client_ip(request) -> str:
    """Extract client IP, preferring rightmost X-Forwarded-For entry.

    Rightmost is harder to spoof as it's set by the last trusted proxy.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Use rightmost IP (set by our reverse proxy, harder to spoof)
        ips = [ip.strip() for ip in forwarded.split(",")]
        return ips[-1] if ips else "unknown"
    return request.client.host if request.client else "unknown"


def _caller_ip() -> str | None:
    """The calling client's IP inside a tool, for the hourly distributor log. None outside an HTTP
    request (tests, stdio)."""
    try:
        return _client_ip(get_http_request())
    except RuntimeError:
        return None


# Helpers to handle JSON string arrays from MCP clients
def _parse_list_param(value: list[str] | str | None) -> list[str] | None:
    """Accept a list, JSON array, or one literal value; never discard an element."""
    if value is None:
        return None
    if isinstance(value, str):
        if value.lstrip().startswith(("[", "{", '"')):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError("expected a string or JSON array of strings") from exc
        else:
            value = [value]
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise ValueError("expected a string or array of nonempty strings")
    return value or None


def _argument_error(name: str, error: ValueError, valid_values: list[str]) -> dict:
    return {"error": f"Invalid {name}: {error}", "valid_values": valid_values,
            "results": [], "total": 0}


def _check_list_cap(name: str, value: list | None, cap: int = MAX_LIST_PARAM_ITEMS) -> dict | None:
    """Return an error dict if a list-valued param exceeds its cap, else None.

    Caps are well above realistic use — this only rejects abusive payloads that would
    build a huge SQL statement / exceed SQLite's bound-variable limit.
    """
    if value is not None and len(value) > cap:
        return {"error": f"Too many {name} (max {cap}, got {len(value)})", "results": [], "total": 0}
    return None



# Tools

def _normalize_library_type(value: Any) -> Any:
    return value.strip().lower().replace("-", "_") if isinstance(value, str) else value


LibraryType = Annotated[
    Literal["basic", "preferred", "no_fee", "extended", "all"] | None,
    BeforeValidator(_normalize_library_type),
]


SearchSort = Annotated[Literal["stock", "price"] | None, BeforeValidator(_normalize_library_type)]
StockSort = Annotated[Literal["quantity", "price"] | None, BeforeValidator(_normalize_library_type)]


@mcp.tool(
    annotations=ToolAnnotations(
        title="Stock Check (Live API)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def jlc_stock_check(
    query: str | None = None,
    category_id: int | None = None,
    subcategory_id: int | None = None,
    category_name: str | None = None,
    subcategory_name: str | None = None,
    min_stock: int = DEFAULT_MIN_STOCK,
    library_type: LibraryType = None,
    package: str | None = None,
    manufacturer: str | None = None,
    packages: list[str] | str | None = None,
    manufacturers: list[str] | str | None = None,
    sort_by: StockSort = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Live JLCPCB stock and price search. Use jlc_search first (faster, parametric filters); use this
    only to confirm stock before ordering, find parts with stock under 10 or out of stock, or page
    through large result sets.

    Args:
        query: Keywords (e.g., "ESP32", "10uF 25V", "STM32F103")
        category_id: Category ID from jlc_search_help
        subcategory_id: Subcategory ID from jlc_search_help
        category_name: Category name (e.g., "Resistors")
        subcategory_name: Subcategory name (e.g., "Tactile Switches")
        min_stock: Set 0 to include out-of-stock parts
        library_type: "basic", "preferred", "no_fee", "extended" or "all"; ignores case,
            accepts no-fee; invalid values list valid choices
        package: Package (e.g., "0402", "LQFP48")
        manufacturer: Manufacturer
        packages: Several packages (OR); accepts a list, JSON array string, or one bare string
        manufacturers: Several manufacturers (OR); same formats as packages, never comma-split
        sort_by: "quantity" or "price" (case-insensitive)
        page: Page number
        limit: Results per page (max 100)

    Returns:
        Results with pagination. Use jlc_get_part(lcsc=...) for full details.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    # Validate parameters
    if query and len(query) > 500:
        return {"error": "Query too long (max 500 characters)"}
    effective_min_stock = max(0, min_stock)
    effective_page = max(1, page)
    effective_limit = clamp_limit(limit, MAX_PAGE_SIZE)

    # Parse list parameters (handles JSON strings from some MCP clients)
    parsed_lists = {}
    for name, value in (("packages", packages), ("manufacturers", manufacturers)):
        try:
            parsed_lists[name] = _parse_list_param(value)
        except ValueError as exc:
            return _argument_error(name, exc, ["string", "array of strings", "JSON array of strings"])
    parsed_packages = parsed_lists["packages"]
    parsed_manufacturers = parsed_lists["manufacturers"]
    if library_type is not None:
        library_type = _normalize_library_type(library_type)
        if library_type not in ("basic", "preferred", "no_fee", "extended", "all"):
            return {"error": f"Unsupported library_type: '{library_type}'",
                    "valid_values": ["basic", "preferred", "no_fee", "extended", "all"]}
    if sort_by is not None:
        sort_by = _normalize_library_type(sort_by)
        if sort_by not in ("quantity", "price"):
            return _argument_error("sort_by", ValueError("expected quantity or price"), ["quantity", "price"])

    # Reject abusive oversized list params
    for _name, _val in (("packages", parsed_packages), ("manufacturers", parsed_manufacturers)):
        _cap_err = _check_list_cap(_name, _val)
        if _cap_err:
            return _cap_err

    # Resolve category_name to category_id if provided (ID takes precedence)
    resolved_category_id = category_id
    if category_name and not category_id:
        # Ensure categories are loaded before name resolution
        if not _categories:
            return {"error": "Categories not loaded. Server may still be starting up.", "hint": "Try again in a moment"}
        resolved_category_id = _client.match_category_by_name(category_name)
        if resolved_category_id is None:
            return {"error": f"Category not found: '{category_name}'", "hint": "Use jlc_search_help() to see available categories"}

    # Resolve subcategory_name to subcategory_id if provided (ID takes precedence)
    resolved_subcategory_id = subcategory_id
    if subcategory_name and not subcategory_id:
        # Ensure categories are loaded before name resolution
        if not _categories:
            return {"error": "Categories not loaded. Server may still be starting up.", "hint": "Try again in a moment"}
        resolved_subcategory_id = _client.get_subcategory_id_by_name(subcategory_name)
        if resolved_subcategory_id is None:
            return {"error": f"Subcategory not found: '{subcategory_name}'", "hint": "Use jlc_search_help(category='Connectors') to see available subcategories"}

    try:
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
    except ValueError as e:
        # Client raises ValueError with actionable messages (rate limited / WAF / timeout).
        # Return them as a dict so they survive mask_error_details=True.
        return {"error": str(e)}


def _parse_spec_filters(filters: list[dict[str, Any]] | str | None) -> list[SpecFilter] | None:
    """Validate every explicit constraint, including JSON-string client payloads."""
    if filters is None:
        return None
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except json.JSONDecodeError as exc:
            raise ValueError("expected a JSON array of {name, op, value} objects") from exc
    if not isinstance(filters, list):
        raise ValueError("expected an array of {name, op, value} objects")
    result = []
    for f in filters:
        if not isinstance(f, dict):
            raise ValueError("each filter must be a {name, op, value} object")
        name, op, value = f.get("name"), f.get("op"), f.get("value")
        if (not isinstance(name, str) or not name.strip() or isinstance(value, bool)
                or not isinstance(value, (str, int, float)) or not str(value).strip()
                or (isinstance(value, float) and not math.isfinite(value))):
            raise ValueError("name must be nonempty text; value must be text or a number")
        op = op.strip() if isinstance(op, str) else op
        if op == "=>":
            op = ">="
        if op not in ("=", ">=", "<=", ">", "<"):
            raise ValueError("valid operators: =, >=, <=, >, < (=> also accepted)")
        # Attribute names are case-insensitive; retain the catalog/alias spelling for parsers.
        known_names = [*ATTRIBUTE_ALIASES, *(n for names in ATTRIBUTE_ALIASES.values() for n in names),
                       *SPEC_PARSERS, "Module Flash", "Module PSRAM"]
        name = next((n for n in known_names if n.casefold() == name.strip().casefold()), name.strip())
        result.append(SpecFilter(name, op, str(value)))
    return result or None


_REFERENCE_DESIGNATOR = re.compile(
    r"(?:R|C|LED|U|SW|J|Q|D|TP|FB|IC|CN|JP|RN|K|F|Y|X|L|P|VR|RV|BZ|BT|LS|T)\d{1,3}", re.IGNORECASE
)
# Package names and standards look like part numbers but describe the part ("8MHz SOT-416
# crystal", "AEC-Q100 CAN transceiver"). SC/SIP/TO/DO need the dash: SC16IS752 is a part.
_PACKAGE_OR_STANDARD = re.compile(
    r"(?:SOT|SOD|SOIC|SOP|SSOP|TSSOP|HTSSOP|MSOP|ESOP|QFN|VQFN|WQFN|UQFN|DFN|UDFN|WDFN|LQFP|TQFP|QFP"
    r"|BGA|WLCSP|SON|TSOT|DIP|PLCC|LGA)-?\d.*|(?:SC|SIP|TO|DO)-\d.*|AEC-?Q\d+|(?:IEC|IEEE|JESD|IPC)-?\d.*",
    re.IGNORECASE,
)


def _keep_part_number_matches(retry: dict, part_number_text: str, limit: int) -> dict:
    """A part-number retry keeps only parts whose MPN contains a requested part number, or is
    contained in it (JK-nSMD005/60V for nSMD005/60V, IR333-A for LED/IR333-A/5mm): the engine's
    MPN fallback shortens part numbers down to prefixes like "YS" that match unrelated parts.
    Counts follow the kept parts; a retry with more matches than one page is marked incomplete."""
    keys = [re.sub(r"[^0-9a-z]", "", t.casefold()) for t in part_number_text.split()]
    def matches(part: dict) -> bool:
        mpn = re.sub(r"[^0-9a-z]", "", (part.get("model") or "").casefold())
        return any(key in mpn or (len(mpn) >= 5 and mpn in key) for key in keys if key)
    kept = [p for p in retry.get("results", []) if matches(p)]
    complete = (retry.get("total") or 0) <= len(retry.get("results", []))
    counts = {tier: sum(p.get("library_type") == tier for p in kept) for tier in ("basic", "preferred", "extended")}
    retry.update(results=kept[:limit], total=len(kept), library_type_counts=counts,
                 no_fee_available=bool(counts["basic"] or counts["preferred"]))
    if "mpn_matches" in retry:
        retry["mpn_matches"].update({name: sum(p.get("mpn_match") == name for p in kept)
                                     for name in ("full", "same_suffix", "family")})
    if "page_info" in retry:
        retry["page_info"].update(limit=limit, returned=len(retry["results"]))
    if not complete:
        retry["counts_complete"] = False
    return retry


def _protected_mpn_tokens(query: str, parsed: ParsedQuery, *, remaining_text: str | None = None) -> list[str]:
    """Keep original MPN tokens that survived parsing, including hyphen-split tokens. Only tokens
    with 6+ letters and digits: shorter part numbers (LM358, BAV99) come from parsed.model_number,
    and short words like M205 (a fuse size) or CL10 stay droppable."""
    remaining = re.sub(r"[-\s]+", " ", parsed.remaining_text if remaining_text is None else remaining_text).casefold()
    tokens = []
    for token in query.split():
        if _REFERENCE_DESIGNATOR.fullmatch(token) or _PACKAGE_OR_STANDARD.fullmatch(token):
            continue
        # The value parser can take a hyphenated suffix ("BC817-40W" as 40W): search the longest
        # leading part that survived (BC817 finds BC817-40), if it is still a part number
        segments = re.split(r"[-\s]+", token)
        part_number = None
        for n in range(len(segments), 0, -1):
            if re.search(r"(?<!\w)" + re.escape(" ".join(segments[:n]).casefold()) + r"(?!\w)", remaining):
                part_number = token if n == len(segments) else "-".join(segments[:n])
                break
        if part_number is None:
            continue
        short = re.sub(r"[^0-9A-Za-z]", "", part_number)
        if part_number != token and not (len(short) >= 5 and sum(c.isdigit() for c in short) >= 2
                                         and any(c.isalpha() for c in short)):
            continue
        letters = sum(c.isalpha() for c in token)
        digits = sum(c.isdigit() for c in token)
        if letters + digits >= 6 and (looks_like_mpn(token) or (letters >= 2 and digits >= 2)):
            tokens.append(part_number)
    return tokens


@mcp.tool(
    annotations=ToolAnnotations(
        title="Search Components",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
@offload(COMPONENT_POOL)
def jlc_search(
    query: str | None = None,
    subcategory_id: int | None = None,
    subcategory_name: str | None = None,
    spec_filters: list[dict[str, Any]] | str | None = None,
    min_stock: int = DEFAULT_MIN_STOCK,
    library_type: LibraryType = None,
    prefer_no_fee: bool = True,
    package: str | None = None,
    packages: list[str] | str | None = None,
    manufacturer: str | None = None,
    match_all_terms: bool = True,
    sort_by: SearchSort = None,
    limit: int = 20,
    strict: bool = False,
) -> dict:
    """Search in-stock JLCPCB parts locally with natural-language parsing and spec filters.
    Default 20 results; strict=true disables relaxation. Reply: relaxed names query words, a
    query-only library preference or part type left out; ignored_filters explains unapplied/rare filters,
    parsed.adjusted_filters explains moved/omitted specs; counts_complete=false means partial counts;
    valid_values lists accepted inputs on errors.
    When the search shortens a full part number (LM1117-3.3 searches LM1117), parts matching it
    come first: mpn_match is full, same_suffix or family, and mpn_matches counts each.
    A full package (QFN-24-EP(4x4)) keeps its body size and exposed pad; a bare family (QFN-24)
    matches any body, and parsed.adjusted_filters says so.

    Args:
        query: Natural language, e.g. "10k resistor 0603 1%", "100nF 25V capacitor" (adds
            Voltage >= 25V), "n-channel mosfet SOT-23" (picks the subcategory). With explicit
            filters it's a text search within the results.
            PD controller/sink/source/trigger roles take precedence over USB-C connector words.
            Sink/trigger/receiver and source rank listed Receiver/Supply controllers first;
            sink voltage ranks negotiated Output Voltage matches within the role. Missing
            attributes stay in results; strict=true requires listed matches instead.
            Strict sink-and-source requirements are reported as unsupported.
            MOSFET gate/logic-drive voltage is separate from Vds. Listed RDS(on) at or
            below that drive ranks first; other parts remain eligible. rds_on_at_drive
            is the entry at the highest listed gate voltage <= drive, or null without
            such evidence; this does not establish load-current or thermal suitability.
        subcategory_id: Subcategory ID (e.g., 2954 for MOSFETs)
        subcategory_name: Subcategory name (e.g., "MOSFETs", "Schottky Diodes")
        spec_filters: List of {"name", "op", "value"}, e.g. [{"name": "Vgs(th)", "op": "<",
            "value": "2.5V"}]. Values accept text or numbers (unitless uses base units: V, A,
            ohms, F, H, Hz, W, mm, bytes); names ignore case. JSON arrays as strings also work.
            op: =, >=, <=, >, < (=> normalizes to >=); invalid inputs return valid_values. Short names: Vgs(th), Vds, Id, Rds(on), Vr,
            If, Vf, Vceo, Ic, Vout, Iout, Supply Voltage, Capacitance, Resistance, Inductance,
            Voltage, Tolerance, Power, DCR, Isat, Frequency; others by the name jlc_search_help
            shows. Range ops only work on attributes it lists as "numeric"; parts with no value
            ("-") don't match them. On ranges ("2.7V~5.5V": supply, output voltage) = means the
            range includes the value.
        min_stock: Minimum stock (the database only has stock >= 10)
        library_type: "basic", "preferred", "no_fee" (basic or preferred), "extended", "all", or omit;
            case-insensitive, with "no-fee" accepted. Unknown values list the valid choices.
        prefer_no_fee: Sort basic/preferred first
        package: One package (e.g., "0603", "SOT-23"). Bare QFN/QFP/SOIC families include
            vendor variants of any body size. Give e.g. "QFN-24-EP(4x4)" to require that body
            and exposed pad. AxB/BxA, decimal zeros and mm spellings of the body are equivalent.
            A suffix absent from the entire catalog falls back to the bare family unless strict=true.
        packages: Several packages (OR), e.g. ["0402", "0603"]; a bare string is one package,
            or pass a JSON array string. Commas within a package stay literal. Explicit package
            arguments override query packages; "0402 or 0603" in a query also means OR.
        manufacturer: Manufacturer
        match_all_terms: Require every query term (AND)
        sort_by: "stock" (most first) or "price" (cheapest within library tiers when prefer_no_fee);
            omitted defaults to stock unless the query says "cheapest"/"lowest price".
        limit: Max results (default 20, max 100)
        strict: If true, keep query words and parsed requirements; no relaxed retry. Unsupported
            constraints return an error with ignored_filters/parsed.adjusted_filters and no results.
            Default false allows relaxation, reporting omitted requirements.

    Returns:
        results: Matching components with specs; description is omitted when specs are nonempty
        total: Matching population before limit. library_type_counts and no_fee_available use
            the same constraints, including library_type and Python spec checks. If a post-filter
            scan reaches its cap, counts_complete=false marks these as counts of checked matches.
        filters_applied: Applied filters (useful for debugging)
        parsed: What was extracted from query; adjusted_filters lists values the part type has
            no spec for (left out or moved), and any bare package family widened to variants
        relaxed: (when present) query words, query-only library preference or part type left out because no
            part matched them; dropped_filters lists parsed spec filters left out by a part-number
            retry. Explicit arguments are retained, and part-number tokens are never dropped.
        ignored_filters: (when present) unsupported/rare attributes, suggested real names and
            coverage, or filters that could not be applied. Reasons distinguish unapplied filters
            from applied constraints with incomplete attribute coverage.
        hint: (on empty replies without an error) a next step using search help, fewer explicit
            constraints or jlc_stock_check for low-stock parts
    """
    # Validate query length to prevent abuse
    MAX_QUERY_LENGTH = 500
    if query and len(query) > MAX_QUERY_LENGTH:
        return {"error": f"Query too long (max {MAX_QUERY_LENGTH} characters)", "results": [], "total": 0}

    if library_type is not None:
        library_type = _normalize_library_type(library_type)
        valid_libraries = ["basic", "preferred", "no_fee", "extended", "all"]
        if library_type not in valid_libraries:
            return {"error": f"Unsupported library_type: '{library_type}'", "valid_values": valid_libraries,
                    "results": [], "total": 0}

    db = get_db()

    # Parse explicit spec filters
    try:
        parsed_filters = _parse_spec_filters(spec_filters)
    except ValueError as exc:
        return _argument_error("spec_filters", exc, ["{name: text, op: =|>=|<=|>|<, value: text or number}"])
    try:
        parsed_packages = _parse_list_param(packages)
    except ValueError as exc:
        return _argument_error("packages", exc, ["string", "array of strings", "JSON array of strings"])
    if sort_by is not None:
        sort_by = _normalize_library_type(sort_by)
        if sort_by not in ("stock", "price"):
            return _argument_error("sort_by", ValueError("expected stock or price"), ["stock", "price"])
    explicit_filters = list(parsed_filters or [])
    query_library = library_type is None

    # Reject abusive oversized list params before building a large SQL statement
    for _name, _val in (("spec_filters", parsed_filters), ("packages", parsed_packages)):
        _cap_err = _check_list_cap(_name, _val)
        if _cap_err:
            return _cap_err

    # Smart parsing: always parse query to clean up text and extract structured info
    # This handles cases like "lipo charger" where terms don't exist in FTS index
    parsed_query_info = None
    parsed = None
    effective_subcategory_name = subcategory_name
    effective_subcategory_ids: list[int] | None = None
    effective_package = package
    effective_mounting_type: str | None = None
    effective_query = query
    part_number_text = None
    protected_tokens: list[str] = []
    fuse_adjustment = None

    if query:
        # Parse natural language query to extract structured info and clean text
        explicit_subcategory_id = subcategory_id
        if not explicit_subcategory_id and subcategory_name:
            explicit_subcategory_id = db.resolve_subcategory_name(subcategory_name)
        parsed = parse_smart_query(
            query, strict=strict,
            subcategory_hint=db.get_subcategory_name(explicit_subcategory_id) if explicit_subcategory_id else None,
        )
        protected_tokens = _protected_mpn_tokens(query, parsed)
        part_number_text = " ".join(protected_tokens) or (
            parsed.model_number if parsed.model_number and not _REFERENCE_DESIGNATOR.fullmatch(parsed.model_number) else None
        )
        parsed_query_info = {
            "original_query": parsed.original,
            "detected": parsed.detected,
            "subcategory": parsed.subcategory,
            "package": parsed.package,
            "mounting_type": parsed.mounting_type,
            "spec_filters": [f.to_dict() for f in parsed.spec_filters],
            "remaining_text": parsed.remaining_text,
        }

        if parsed.subcategory == "supercapacitors" and not (subcategory_name or subcategory_id):
            if not (parsed.model_number or parsed.remaining_text.strip()):
                return {"results": [], "total": 0, "parsed": parsed_query_info,
                        "hint": "JLCPCB has no supercapacitor subcategory in this catalog; try Mouser or DigiKey."}
            # "supercapacitor charging IC", "CN3125 supercapacitor": the word describes another part.
            parsed.subcategory = None
            parsed.detected.pop("subcategory", None)
            parsed.remaining_text = f"{parsed.remaining_text} supercapacitor".strip()
            parsed_query_info.update(subcategory=None, remaining_text=parsed.remaining_text)

        if library_type is None:
            library_type = parsed.detected.get("library_type")
        if sort_by is None:
            sort_by = parsed.detected.get("sort_by")

        # Apply parsed values only if user didn't provide explicit ones
        if parsed.subcategory and not subcategory_name and not subcategory_id:
            if parsed.subcategories:
                ids = [db.resolve_subcategory_name(name) for name in parsed.subcategories]
                effective_subcategory_ids = [i for i in ids if i]
                parsed_query_info["subcategories"] = parsed.subcategories
            if not effective_subcategory_ids:
                effective_subcategory_name = parsed.subcategory
        if not package and not parsed_packages:
            if parsed.packages:
                parsed_packages = parsed.packages
                parsed_query_info["packages"] = parsed.packages
            elif parsed.package:
                effective_package = parsed.package

        fuse_packages = parsed_packages or ([effective_package] if effective_package else [])
        if (not (subcategory_name or subcategory_id)
                and parsed.detected.get("component_type") in ("fuse", "fuses")
                and db.packages_are_resettable_fuses(fuse_packages)):
            effective_subcategory_name = parsed.subcategory = "resettable fuses"
            parsed.detected["subcategory"] = parsed.subcategory
            parsed.spec_filters = [f.for_subcategory(parsed.subcategory) if isinstance(f, FuseFilter) else f
                                   for f in parsed.spec_filters]
            parsed_query_info.update(subcategory=parsed.subcategory,
                                     spec_filters=[f.to_dict() for f in parsed.spec_filters])
            fuse_adjustment = {
                "filter": "subcategory: disposable fuses", "now": parsed.subcategory,
                "reason": f"{', '.join(fuse_packages)} fuses in the catalog are all resettable",
            }

        if strict:
            query_packages = parsed.packages or ([parsed.package] if parsed.package else [])
            if query_packages and (package or packages):
                explicit_packages = ([package] if package else []) + (_parse_list_param(packages) or [])
                if {p.casefold() for p in explicit_packages} != {p.casefold() for p in query_packages}:
                    parsed_query_info.setdefault("adjusted_filters", []).append({
                        "filter": "packages: " + ", ".join(query_packages), "now": None,
                        "reason": "explicit package arguments override query packages; strict mode cannot omit them",
                    })
            detected_library = parsed.detected.get("library_type")
            if (not query_library and detected_library and library_type != detected_library
                    and not (detected_library == "no_fee" and library_type in ("basic", "preferred"))):
                parsed_query_info.setdefault("adjusted_filters", []).append({
                    "filter": "library_type: " + detected_library, "now": None,
                    "reason": "explicit library_type overrides the query library requirement; strict mode cannot omit it",
                })

        # Filters the parser made up must fit the part type: "5V relay" asked for Voltage Rating,
        # which no relay lists, and found nothing
        searched_ids = effective_subcategory_ids or (
            [i for i in [subcategory_id or db.resolve_subcategory_name(effective_subcategory_name)] if i]
            if (subcategory_id or effective_subcategory_name) else []
        )
        auto_filters, adjusted = _fit_parsed_filters(db, parsed.spec_filters, searched_ids)
        if strict and adjusted:
            auto_filters = parsed.spec_filters
            adjusted = [{**a, "now": a["filter"], "reason": a["reason"].split(", so")[0]
                         + "; strict mode retained the requirement"} for a in adjusted]
        if adjusted:
            parsed_query_info.setdefault("adjusted_filters", []).extend(adjusted)
            parsed_query_info["spec_filters"] = [f.to_dict() for f in auto_filters]
        # Merge auto-detected spec filters with manual ones (manual takes precedence)
        if strict and parsed_filters:
            manual_names = {f.name.casefold() for f in parsed_filters}
            conflicts = [f for f in auto_filters if f.name.casefold() in manual_names
                         and f not in parsed_filters]
            if conflicts:
                parsed_query_info.setdefault("adjusted_filters", []).extend(
                    {"filter": f"{f.name} {f.operator} {f.value}", "now": None,
                     "reason": "explicit filter overrides this parsed requirement; strict mode cannot omit it"}
                    for f in conflicts
                )
        parsed_filters = merge_spec_filters(parsed_filters, auto_filters)
        if parsed.mounting_type:
            effective_mounting_type = parsed.mounting_type

        # Always use cleaned remaining_text for FTS (removes subcategory keywords, etc.)
        if parsed.remaining_text and len(parsed.remaining_text) >= 2:
            effective_query = parsed.remaining_text
        elif (parsed.spec_filters or parsed.subcategory or parsed.package or parsed.packages
              or parsed.gate_drive_v is not None):
            # Query was fully parsed into structured filters, no text needed
            effective_query = None

    search_args: dict[str, Any] = dict(
        subcategory_id=subcategory_id,
        subcategory_name=None if effective_subcategory_ids else effective_subcategory_name,
        subcategory_ids=effective_subcategory_ids,
        spec_filters=parsed_filters,
        library_type=library_type if library_type != "all" else None,
        prefer_no_fee=prefer_no_fee,
        min_stock=max(0, min_stock),
        package=effective_package,
        packages=parsed_packages,
        manufacturer=manufacturer,
        mounting_type=effective_mounting_type,
        match_all_terms=match_all_terms,
        sort_by=sort_by or "stock",
        limit=clamp_limit(limit, MAX_PAGE_SIZE),
    )
    requested_packages = parsed_packages or ([effective_package] if effective_package else [])
    package_adjustments = package_family_adjustments(requested_packages)
    if not strict and requested_packages:
        matched_packages, fallback_adjustments = db.resolve_package_constraints(requested_packages)
        if fallback_adjustments:
            if parsed_packages:
                search_args["packages"] = matched_packages
            else:
                search_args["package"] = matched_packages[0]
            package_adjustments.extend(fallback_adjustments)
    if parsed and parsed.connector_spec:
        connector = parsed.connector_spec
        search_args["connector_manufacturer"] = connector.manufacturer
        if not strict:
            search_args["connector_series"] = connector.series or ("HY" if connector.fts_term == "HY2.0" else None)
    if (parsed and parsed.gate_drive_v is not None and searched_ids
            and all(db.get_subcategory_name(i).lower() == "mosfets" for i in searched_ids)):
        search_args["gate_drive_v"] = parsed.gate_drive_v
    if (parsed and parsed.preferred_specs and searched_ids
            and all(db.get_subcategory_name(i).lower() == "usb pd" for i in searched_ids)):
        search_args["preferred_specs"] = parsed.preferred_specs
        parsed_query_info.setdefault("adjusted_filters", []).extend({
            "filter": f"{f.name} = {f.value}", "now": f"rank {f.name} = {f.value} first",
            "reason": "many USB PD parts don't list this attribute; ranking keeps unlisted parts"
                      + ("; this is the negotiated output, not the supply voltage" if f.name == "Output Voltage" else ""),
        } for f in parsed.preferred_specs)
    # Perform search - db.search() handles name resolution internally
    if parsed and effective_query:
        # Step 8 and the model patterns can discard ordering-code suffixes. Reuse
        # #90's token guards, examining the original text before that truncation.
        searched_key = mpn_key(effective_query)
        for token in _protected_mpn_tokens(query, parsed, remaining_text=query):
            token_key = mpn_key(token)
            if len(token_key) > len(searched_key) and token_key.startswith(searched_key):
                search_args["part_number"] = token
                break
    result = db.search(query=effective_query, **search_args)

    # A library phrase in the query is a preference; an explicit argument is a constraint.
    dropped_library = None
    if (not strict and query_library and library_type not in (None, "all")
            and result.get("total") == 0 and not result.get("error")):
        search_args["library_type"] = None
        dropped_library = library_type
        retry = db.search(query=effective_query, **search_args)
        if retry.get("total"):
            retry["relaxed"] = {
                "dropped_text": library_type,
                "reason": "no part matched the query library tier, so the library preference was left out",
            }
            result = retry

    # Words the parser couldn't place ("dual", "edge mount") are required in the description and
    # can zero a search the part type and filters would answer. Only for words left from a
    # natural-language query, never a part number or the caller's own subcategory or filters.
    if (not strict and result.get("total") == 0 and not result.get("error") and parsed and effective_query
            and not part_number_text and (parsed.subcategory or parsed.spec_filters)
            and not (subcategory_id or subcategory_name or spec_filters)):
        retry = db.search(query=None, **search_args)
        if retry.get("total"):
            retry["relaxed"] = {
                "dropped_text": effective_query,
                "reason": "no part matched these words together with the part type and filters, "
                          "so they were left out",
            }
            if dropped_library:
                retry["relaxed"]["dropped_text"] = dropped_library + " " + effective_query
                retry["relaxed"]["reason"] += "; the library preference was left out"
            unsupported = parsed.detected.get("unsupported_constraints", [])
            if unsupported:
                retry["relaxed"]["reason"] += "; unsupported constraints left out: " + ", ".join(unsupported)
            result = retry

    # A model can be listed under a different part type than the query's alias suggests.
    if (not strict and result.get("total") == 0 and not result.get("error") and parsed
            and part_number_text and parsed.subcategory
            and not (subcategory_id or subcategory_name)):
        retry_args = {**search_args, "subcategory_name": None, "subcategory_ids": None, "limit": MAX_PAGE_SIZE}
        page = search_args["limit"]
        retry = _keep_part_number_matches(db.search(query=part_number_text, **retry_args), part_number_text, page)
        dropped_filters = []
        # Only a full part number may cost the parsed values; "CL10 10uH inductor" keeps its 10uH.
        if not retry.get("total") and not retry.get("error") and protected_tokens:
            dropped_filters = [f.to_dict() for f in (parsed_filters or []) if f not in explicit_filters]
            if dropped_filters:
                retry_args["spec_filters"] = explicit_filters or None
                retry = _keep_part_number_matches(db.search(query=part_number_text, **retry_args),
                                                  part_number_text, page)
        if retry.get("total"):
            part_type = (result.get("filters_applied", {}).get("subcategory_resolved")
                         or effective_subcategory_name or parsed.subcategory)
            retry["relaxed"] = {
                "dropped_part_type": part_type,
                "reason": f"no part matching {part_number_text} is listed under {part_type}, "
                          "so every part type was searched",
            }
            if dropped_filters:
                retry["relaxed"]["dropped_filters"] = dropped_filters
                retry["relaxed"]["reason"] += "; parsed spec filters were left out"
            if dropped_library:
                retry["relaxed"]["reason"] += "; the library preference was left out"
            effective_subcategory_name = None
            effective_subcategory_ids = None
            result = retry

    searched_ids = effective_subcategory_ids or (
        [i for i in [subcategory_id or db.resolve_subcategory_name(effective_subcategory_name)] if i]
        if (subcategory_id or effective_subcategory_name) else []
    )
    unapplied_filters = result.get("ignored_filters", [])
    explicit_issues = _explicit_filter_issues(db, explicit_filters, searched_ids, unapplied_filters)
    if explicit_issues:
        # Report only: do not remove or remap the caller's explicit constraints.
        labels = {f["filter"] for f in explicit_issues}
        result["ignored_filters"] = [f for f in result.get("ignored_filters", []) if f["filter"] not in labels] + explicit_issues
    unsupported = parsed.detected.get("unsupported_constraints", []) if parsed else []
    if strict:
        if unsupported:
            result.setdefault("ignored_filters", []).extend(
                {"filter": value, "reason": "unsupported query constraint"} for value in unsupported
            )
        if unapplied_filters or unsupported or (parsed_query_info and parsed_query_info.get("adjusted_filters")):
            result.update({"error": "Strict search cannot apply every constraint; see ignored_filters and parsed.adjusted_filters and use jlc_search_help(subcategory=...) for supported attributes",
                           "results": [], "total": 0, "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                           "no_fee_available": False})
            if "page_info" in result:
                result["page_info"]["returned"] = 0
            if "mpn_matches" in result:
                result["mpn_matches"].update(full=0, same_suffix=0, family=0)

    # Family matching fulfills a bare request, including in strict mode. Report this
    # after checking unapplied requirements so informational adjustments aren't errors.
    if package_adjustments:
        if parsed_query_info is None:
            parsed_query_info = {}
        parsed_query_info.setdefault("adjusted_filters", []).extend(package_adjustments)

    if fuse_adjustment:
        parsed_query_info.setdefault("adjusted_filters", []).append(fuse_adjustment)

    if parsed and search_args.get("gate_drive_v") is not None:
        drive = f"{parsed.gate_drive_v:g}V"
        parsed_query_info.setdefault("adjusted_filters", []).append({
            "filter": drive, "now": f"rank RDS(on) listed at or below {drive} first",
            "reason": f"voltage read as gate drive, not Vds; parts without listed RDS(on) "
                      f"at or below {drive} remain eligible with null rds_on_at_drive",
        })

    # Add parsing info, including explicit package-family adjustments.
    if parsed_query_info:
        result["parsed"] = parsed_query_info

    if result.get("total") == 0 and not result.get("error") and "hint" not in result:
        hints = []
        if result.get("ignored_filters"):
            hints.append("See ignored_filters for unapplied or sparse attributes.")
        resolved_name = (result.get("filters_applied", {}).get("subcategory_resolved")
                         or (db.get_subcategory_name(searched_ids[0]) if searched_ids else None))
        if resolved_name:
            hints.append(f"Try jlc_search_help(subcategory={json.dumps(resolved_name)}) for attribute names and values.")
        explicit = [name for name, value in (("library_type", None if query_library else library_type),
                    ("package/packages", package or packages), ("manufacturer", manufacturer)) if value]
        if explicit:
            hints.append("Try without " + ", ".join(explicit) + ".")
        if part_number_text:
            hints.insert(0, f"No in-stock part matches {part_number_text}; try "
                            f"jlc_stock_check(query={json.dumps(part_number_text)}) for low or zero stock, "
                            "or search by part type and specs without the part number.")
        else:
            hints.append("Use jlc_stock_check for low-stock parts.")
        result["hint"] = " ".join(hints)

    return result


# A filter the parser made from a value, but whose spec the part type doesn't list: what to try
# instead, in order. A "3.3V level shifter" runs at 3.3V; a "4A high side switch" carries 4A.
_PARSED_FILTER_FALLBACKS: dict[str, list[tuple[str, str]]] = {
    "Voltage Rating": [("Supply Voltage", "="), ("Coil Voltage", "=")],
    "Current Rating": [("Output Current", ">="), ("Maximum Continuous Current", ">=")],
}
# A spec counts as listed by a part type when at least this share of its parts state it: op amps
# have "Voltage - Supply" on 14 of 4,900 parts, and a filter on it would hide the rest
_LISTED_SHARE = 0.1
_DIMENSIONS = re.compile(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*mm", re.IGNORECASE)


def _fit_parsed_filters(
    db: Any, filters: list[SpecFilter], subcategory_ids: list[int]
) -> tuple[list[SpecFilter], list[dict[str, str | None]]]:
    """Keep each parsed filter whose spec the searched part types list; otherwise use a fallback
    spec they do list, or leave it out. Returns the filters and what was changed and why. With no
    part type known, filters are kept as they are."""
    if not subcategory_ids:
        return list(filters), []
    def listed(name: str) -> bool:
        return db.attribute_share(subcategory_ids, get_attribute_names(name)) >= _LISTED_SHARE

    kept: list[SpecFilter] = []
    adjusted: list[dict[str, str | None]] = []
    for spec_filter in filters:
        if isinstance(spec_filter, ConnectorFilter):
            candidates = ["Pitch"] if spec_filter.name == "Pitch" else [
                "Number of Pins", "Number of Contacts", "Number of Positions", "Number of Positions or Pins",
            ]
            # Check each searched subcategory separately; a well-filled large category must
            # not conceal a sparse one. Select the attribute these parts actually use.
            shares = {name: min(db.attribute_share([i], [name]) for i in subcategory_ids) for name in candidates}
            name = max(shares, key=shares.get)
            share = shares[name]
            threshold = .9
            # USB contacts are 86% filled overall (99% for typed Type-C parts), close to
            # the decision's "about 90%". Keep this exception specific to USB contacts.
            if name == "Number of Contacts" and all(db.get_subcategory_name(i).lower() == "usb connectors"
                                                    for i in subcategory_ids):
                threshold = .85
            if share >= threshold:
                kept.append(ConnectorFilter(name, spec_filter.operator, spec_filter.value))
                if name != spec_filter.name:
                    adjusted.append({
                        "filter": f"{spec_filter.name} {spec_filter.operator} {spec_filter.value}",
                        "now": f"{name} {spec_filter.operator} {spec_filter.value}",
                        "reason": f"these connector parts record contact count as {name}",
                    })
            elif all("connector" not in db.get_subcategory_name(i).lower() for i in subcategory_ids):
                # Headers/terminal blocks already had exact string filters before #23.
                # Below the coverage gate, preserve that behavior instead of broadening.
                legacy_filters, legacy_adjusted = _fit_parsed_filters(
                    db, [SpecFilter(spec_filter.name, spec_filter.operator, spec_filter.value)], subcategory_ids,
                )
                kept.extend(legacy_filters)
                adjusted.extend(legacy_adjusted)
            else:
                adjusted.append({
                    "filter": f"{spec_filter.name} {spec_filter.operator} {spec_filter.value}", "now": None,
                    "reason": f"connector attribute coverage is {share:.1%}, below {threshold:.0%}; "
                              "the value was left out and is unverified",
                })
            continue
        if spec_filter.name in ("Module Flash", "Module PSRAM") or listed(spec_filter.name):
            kept.append(spec_filter)
            continue
        label = f"{spec_filter.name} {spec_filter.operator} {spec_filter.value}"
        replacement: list[SpecFilter] = []
        for name, operator in _PARSED_FILTER_FALLBACKS.get(spec_filter.name, []):
            if listed(name):
                replacement = [SpecFilter(name, operator, spec_filter.value)]
                break
        size = _DIMENSIONS.fullmatch(spec_filter.value.strip()) if spec_filter.name == "Dimensions" else None
        if size and listed("Length") and listed("Width"):
            replacement = [SpecFilter("Length", "=", f"{size.group(1)}mm"), SpecFilter("Width", "=", f"{size.group(2)}mm")]
        kept.extend(replacement)
        adjusted.append({
            "filter": label,
            "now": ", ".join(f"{f.name} {f.operator} {f.value}" for f in replacement) or None,
            "reason": f"few or none of these parts list {spec_filter.name}"
                      + ("" if replacement else ", so the value was left out"),
        })
    return kept, adjusted


def _explicit_filter_issues(
    db: Any, filters: list[SpecFilter], ids: list[int], ignored_filters: list[dict]
) -> list[dict]:
    """Disclose unsupported/rare explicit attributes without changing matching."""
    if not ids:
        return []
    # These reasons come from the actual SQL/post-filter builder, not attribute coverage.
    unapplied = {f["filter"]: f["reason"] for f in ignored_filters}
    issues = []
    available = None
    for f in filters:
        if f.name in ("Module Flash", "Module PSRAM"):
            continue
        names = get_attribute_names(f.name)
        column = next((SPEC_TO_COLUMN[n][0] for n in [f.name, *names] if n in SPEC_TO_COLUMN), None)
        if column:
            # The numeric column also covers synonymous stored attributes (e.g. Iq/standby).
            names = list(set(names) | {n for n, info in SPEC_TO_COLUMN.items() if info[0] == column})
        share = db.attribute_share(ids, names)
        if share >= _LISTED_SHARE:
            continue
        if available is None:
            available = sorted({a["name"] for i in ids
                                for a in db.list_attributes(subcategory_id=i).get("attributes", [])})
        # Substrings help with omitted prefixes (Height -> Switch Height), fuzzy matching with typos.
        suggestions = [n for n in available if f.name.casefold() in n.casefold()]
        suggestions += [n for n in get_close_matches(f.name.casefold(), [n.casefold() for n in available], n=3, cutoff=0.3)]
        by_lower = {n.casefold(): n for n in available}
        suggestions = list(dict.fromkeys(by_lower.get(n.casefold(), n) for n in suggestions))[:3]
        label = f"{f.name} {f.operator} {f.value}"
        reason = (f"not applied ({unapplied[label]}); few or none of these parts list {f.name}"
                  if label in unapplied else
                  f"applied, but few or none of these parts list {f.name}, so results may be incomplete or empty")
        issues.append({"filter": label, "reason": reason,
                       "attribute_share": share, "suggestions": suggestions})
    return issues


@mcp.tool(
    annotations=ToolAnnotations(
        title="Search Help & Browse",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
@offload(COMPONENT_POOL)
def jlc_search_help(
    category: str | int | None = None,
    subcategory: str | int | None = None,
) -> dict:
    """List categories, a category's subcategories, or a subcategory's filterable attributes (with
    type and example values) for jlc_search spec_filters. No args lists all categories.

    Args:
        category: Category name (e.g., "Connectors") or ID: lists its subcategories
        subcategory: Subcategory name (e.g., "MOSFETs") or ID: lists its filterable attributes

    Returns:
        No args: List of all categories with id, name, part count, subcategory count
        category: Subcategories with id, name, part count
        subcategory: Filterable attributes with name, alias, type, example values

    Example:
        1. jlc_search_help() → see all categories sorted by part count
        2. jlc_search_help(category="Transistors") → see MOSFETs, BJTs, etc.
        3. jlc_search_help(subcategory="MOSFETs") → see Vgs(th), Vds, Id, Rds(on) filters
        4. jlc_search(query="n-channel", spec_filters=[{"name": "Vgs(th)", "op": "<", "value": "2.5V"}])
    """
    # Subcategory mode: list filterable attributes
    if subcategory is not None:
        db = get_db()
        if isinstance(subcategory, int):
            return db.list_attributes(subcategory_id=subcategory)
        return db.list_attributes(subcategory_name=str(subcategory))

    # Category mode: list subcategories
    if category is not None:
        if not _categories:
            return {"error": "Categories not loaded. Server may still be starting up."}

        matched = None
        if isinstance(category, int):
            matched = next((c for c in _categories if c["id"] == category), None)
        else:
            cat_lower = str(category).lower()
            matched = next((c for c in _categories if c["name"].lower() == cat_lower), None)

        if not matched:
            return {"error": f"Category not found: '{category}'", "hint": "Call jlc_search_help() with no args to see all categories"}

        subcats = sorted(matched.get("subcategories", []), key=lambda s: -s["count"])
        return {
            "category_id": matched["id"],
            "category_name": matched["name"],
            "subcategories": [
                {"id": sub["id"], "name": sub["name"], "count": sub["count"]}
                for sub in subcats
            ],
        }

    # No args: list all categories
    if not _categories:
        return {"error": "Categories not loaded", "categories": []}

    sorted_cats = sorted(_categories, key=lambda c: -c["count"])
    return {
        "categories": [
            {
                "id": cat["id"],
                "name": cat["name"],
                "count": cat["count"],
                "subcategory_count": len(cat.get("subcategories", [])),
            }
            for cat in sorted_cats
        ]
    }


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
    """Full details for one JLCPCB part (all price tiers, datasheet, attributes, EasyEDA footprint
    availability), or the JLCPCB parts matching a manufacturer part number.

    Reply: prices lists quantity tiers, datasheet links the datasheet; has_easyeda_footprint=null
    means unknown, false means absent; MPN lookups return results and total. Non-exact replies
    add match (separators, packing, alias, alternative or related), matched_mpn where applicable,
    and a note naming the part types for related full-text results.

    Args:
        lcsc: LCSC part code (e.g., "C82899")
        mpn: Manufacturer part number (e.g., "LM358P"), over in-stock parts (stock >= 10). Also
            finds other dash/space spellings, the same manufacturer's other packing codes, and BOM
            entries with notes or alternatives; never a different grade. Finds the JLCPCB
            equivalent of a part from another distributor or a reference design.

    Returns:
        For lcsc: Full part details including specs (description only when specs are empty),
        all pricing tiers in prices, datasheet URL,
        component attributes, and EasyEDA footprint availability:
        - has_easyeda_footprint: True if EasyEDA has footprint/symbol, False if not, null if unknown
        - easyeda_symbol_uuid: UUID for direct EasyEDA editor link (null if no footprint)
        - easyeda_footprint_uuid: UUID for footprint (null if no footprint)

        For mpn: List of matching JLCPCB parts from the local database (stock >= 10),
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
        match_info: dict[str, Any] = {}
        results = await run_db(COMPONENT_POOL, db.get_by_mpn, mpn, match_info=match_info)
        if not results:
            return {"error": f"No JLCPCB parts found for MPN '{mpn}'", "mpn": mpn, "results": [],
                    "hint": "The local catalog only lists in-stock parts (stock >= 10). "
                            f"Try jlc_stock_check(query={json.dumps(mpn)}) for low or zero stock, "
                            "or mouser_get_part / digikey_get_part for other distributors."}
        return {
            "mpn": mpn,
            "total": len(results),
            "results": results,
            **match_info,
        }

    # LCSC lookup via live API (existing behavior)
    if not _client:
        raise RuntimeError("Client not initialized")

    try:
        result = await _client.get_part(lcsc)
    except ValueError as e:  # actionable JLCPCB messages (rate limited / WAF / timeout)
        return {"error": str(e)}
    if not result:
        return {"error": f"Part {lcsc} not found"}
    return result



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
    library_type: LibraryType = None,
    has_easyeda_footprint: bool | None = None,
    limit: int = 10,
    board_quantity: int = 1,
    placements_per_board: int = 1,
) -> dict:
    """Find catalog-checked alternatives, ranked no-fee first (same-package passives/crystals first
    within each tier). Reply: summary.found counts verified alternatives; unverified_alternatives
    need manual comparison for missing required matches; specs_unparseable lists specs not verified;
    unchecked_requirements includes pinout/circuit checks still needed; has_easyeda_footprint=null means unknown.

    Args:
        lcsc: LCSC code of the original part (e.g., "C2557")
        min_stock: Minimum stock
        same_package: Only parts with the same package
        library_type: "basic", "preferred", "no_fee" (basic or preferred), "extended", or omit
            for all; case-insensitive, accepts no-fee. Invalid values list valid choices.
        has_easyeda_footprint: True: only parts with an EasyEDA footprint (for Atopile/KiCad);
            False: only parts without; omit: no filter (fastest). Checks at most 15 candidates
            per call and leaves out any it couldn't check; summary.footprint_filter says when.
        limit: Max entries per verified/unverified list (max 50)
        board_quantity: Number of boards for project savings (default 1)
        placements_per_board: Original part placements per board (default 1)

    Returns:
        Original part info (with library_type and has_easyeda_footprint) and list of alternatives,
        best first. Alternatives include library_type, specs, and specs_verified/specs_unparseable
        (what was checked). Stock comes from the live search or the daily database.
        When filtering by footprint, alternatives also include EasyEDA UUIDs.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    if library_type is not None:
        library_type = _normalize_library_type(library_type)
        if library_type not in ("basic", "preferred", "no_fee", "extended", "all"):
            return {"error": f"Unsupported library_type: '{library_type}'",
                    "valid_values": ["basic", "preferred", "no_fee", "extended", "all"]}

    try:
        return await _client.find_alternatives(
            lcsc=lcsc,
            min_stock=min_stock,
            same_package=same_package,
            library_type=library_type if library_type != "all" else None,
            has_easyeda_footprint=has_easyeda_footprint,
            limit=clamp_limit(limit, MAX_ALTERNATIVES),
            board_quantity=board_quantity,
            placements_per_board=placements_per_board,
        )
    except ValueError as e:  # actionable JLCPCB messages (rate limited / WAF / timeout)
        return {"error": str(e)}


def _easyeda_unknown_error(lcsc: str) -> dict[str, str]:
    """Footprint status unknown, not absent: the EasyEDA lookup failed or is paused by its rate limit."""
    return {"error": f"Couldn't check EasyEDA for {lcsc}'s symbol right now (lookup failed or "
                     "EasyEDA is rate-limiting). Try again in a few minutes."}


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
    """Pin numbers and names from a part's EasyEDA symbol, exactly as EasyEDA has them (e.g., VCC,
    GND, PA0).

    Args:
        lcsc: LCSC part code (e.g., "C8304"); finds the symbol for you
        uuid: EasyEDA symbol UUID, instead of lcsc

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
        try:
            part = await _client.get_part(lcsc)
        except ValueError as e:  # actionable JLCPCB messages (rate limited / WAF / timeout)
            return {"error": str(e)}
        if not part:
            return {"error": f"Part not found: {lcsc}"}

        if part.get("has_easyeda_footprint") is None:
            return _easyeda_unknown_error(lcsc)
        if not part.get("has_easyeda_footprint"):
            return {"error": f"No EasyEDA symbol available for {lcsc}"}

        symbol_uuid = part.get("easyeda_symbol_uuid")
        if not symbol_uuid:
            return {"error": f"No EasyEDA symbol UUID for {lcsc}"}

    try:
        # Fetch EasyEDA component data
        easyeda_data = await _client.get_easyeda_component(symbol_uuid)
    except EasyEDAComponentNotFound as e:
        # No part to re-check, or /api/products named this dead UUID for it within the last hour
        if not lcsc or _client.footprint_confirmed_recently(lcsc, symbol_uuid):
            return {"error": str(e)}
        # The stored symbol UUID stopped working (EasyEDA re-linked or removed the part): re-check
        # the part once and follow its new UUID.
        await _client.invalidate_easyeda_footprint(lcsc)
        info = await _client.check_easyeda_footprint(lcsc)
        if info.get("has_easyeda_footprint") is None:
            return _easyeda_unknown_error(lcsc)
        new_uuid = info.get("easyeda_symbol_uuid")
        if not info.get("has_easyeda_footprint") or not new_uuid:
            return {"error": f"No EasyEDA symbol available for {lcsc}"}
        if new_uuid == symbol_uuid:
            return {"error": str(e)}
        symbol_uuid = new_uuid
        try:
            easyeda_data = await _client.get_easyeda_component(symbol_uuid)
        except ValueError as e2:
            return {"error": str(e2)}
    except ValueError as e:
        return {"error": str(e)}
    except Exception:
        logger.error(f"EasyEDA fetch failed for {lcsc or symbol_uuid}", exc_info=True)
        return {"error": "Failed to fetch EasyEDA data. Check server logs for details."}

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



def _redact(message: str, *secrets: str) -> str:
    """Distributor error text goes back to anonymous callers: blank out our credentials in case the
    API ever echoes them."""
    for secret in secrets:
        if secret:
            message = message.replace(secret, "[redacted]")
    return message


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
    """Mouser price, stock and datasheet for specific parts. Use only when the user wants Mouser data;
    find parts with jlc_search first. Shared daily limit: batch up to 10 parts per call (one
    request). Don't retry a quota error.

    Args:
        part_number: Mouser PN or MPN, or up to 10 joined by "|" ("595-LM358P|NE555P"),
            3-40 chars each. Loose match, max 50 results per call: use full PNs when batching;
            match results by mfr_part_number.

    Returns:
        results: Full part details including all attributes, pricing tiers, availability, datasheet
        total: Number of parts found
    """
    if not _mouser_client:
        return {"error": "Mouser API key not configured. Set MOUSER_API_KEY in environment."}
    if part_number and len(part_number) > 500:
        return {"error": "Part number too long (max 500 characters)"}

    try:
        return await _mouser_client.get_part(part_number, caller=_caller_ip())
    except (MouserError, MouserAPIError) as e:  # our own message or Mouser's
        logger.error(f"Mouser part lookup failed: {type(e).__name__}: {e}")
        return {"error": f"Mouser part lookup failed: {_redact(str(e), MOUSER_API_KEY)}"}
    except Exception as e:
        logger.error(f"Mouser part lookup failed: {type(e).__name__}: {e}")
        return {"error": "Mouser part lookup failed. Check server logs for details."}


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
    """DigiKey price, stock and datasheet for one part. Use only when the user wants DigiKey data;
    find parts with jlc_search first. Shared daily limit, one part per call: don't check whole
    BOMs. Don't retry a quota error.

    Args:
        product_number: DigiKey PN or MPN ("296-1395-5-ND", "LM358P"). Use the full number: a
            partial one can find nothing and still uses a request.

    Returns:
        Full product details including all parameters, pricing variations, availability, datasheet
    """
    if not _digikey_client:
        return {"error": "DigiKey API credentials not configured. Set DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET in environment."}
    if product_number and len(product_number) > 500:
        return {"error": "Product number too long (max 500 characters)"}

    try:
        return await _digikey_client.get_part(product_number, caller=_caller_ip())
    except DigiKeyError as e:  # our own message (HTTP status) or DigiKey's OAuth error
        logger.error(f"DigiKey part lookup failed: {type(e).__name__}: {e}")
        return {"error": f"DigiKey part lookup failed: {_redact(str(e), DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET)}"}
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
    """Check whether KiCad, Eagle or Altium symbols, footprints and 3D models exist for a part on
    SamacSys ComponentSearchEngine, with its datasheet. Slow (up to 45 s): only when you need
    ECAD models. For part search use jlc_search; for EasyEDA footprints, jlc_get_part.

    Args:
        query: MPN or keyword (e.g., "LM358P", "STM32F103")
        limit: Max results (1-10)

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

    limit = clamp_limit(limit, 10)

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
    """Download a part's KiCad symbol (.kicad_sym) and footprint (.kicad_mod) as text from SamacSys
    ComponentSearchEngine; works for any manufacturer. Slow (up to 45 s): only when you need the
    KiCad files. For EasyEDA footprints use jlc_get_part.

    Args:
        query: MPN (e.g., "LM358P", "ESP32-WROOM-32E"); picks the best match that has a model
        part_id: cse_part_id from cse_search, to skip the search

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
        title="Sensor Recommend",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
@offload(SENSOR_POOL)
def sensor_recommend(
    query: str | None = None,
    measure: str | list[str] | None = None,
    type: str | None = None,
    protocol: str | None = None,
    platform: str | None = None,
    limit: int = 15,
) -> dict:
    """Recommend sensor ICs and modules for what you want to measure, with protocol and platform
    support. Filter choices come from the catalog; unknown values list valid choices.
    Accepts 1-wire/one-wire and heart rate/blood oxygen aliases. Not for buying parts: use jlc_search.

    Args:
        query: Name, description or manufacturer (e.g., "BME280", "waterproof")
        measure: One, or a list that must all match: temperature, humidity, pressure, distance,
            tof, lidar, ultrasonic, radar, co2, co, gas, voc, formaldehyde, h2s, nh3, ozone,
            oxygen, particulate, light, color, uv, optical, acceleration, gyroscope,
            magnetic_field, tilt, vibration, rotation, motion, pir, proximity, gesture,
            face_recognition, current, voltage, sound, flow, level, force, weight, touch, ph,
            dissolved_oxygen, conductivity, orp, water_quality, moisture, soil_moisture, rain,
            wind, weather, ir_temperature, flame, biometric, radiation, gps. "imu" means
            acceleration, gyroscope or magnetic_field; everyday words (barometric, lux, dust,
            compass) are mapped too.
        type: Sensing technology (e.g., "tof", "ultrasonic", "ndir", "electrochemical", "mems")
        protocol: "i2c", "spi", "uart", "analog", "pwm", "gpio", "one_wire", "rs485", "can" or "i2s"
        platform: "arduino", "esphome", "micropython", "circuitpython", "tasmota", "zephyr" or
            "raspberry_pi". ESP-IDF has no support records; unknown platforms return valid_values.
        limit: Max results (max 100)

    Returns:
        Sensors sorted by platform support (how many platforms have drivers for this sensor).
        Each result includes: name, manufacturer, measures, type, protocol,
        voltage, platforms, platform_count, description, urls, datasheet_url (when available).
    """
    # Handle JSON-string measure param from some MCP clients (filter non-string
    # elements — they bypass Pydantic and get .lower()'d in sensor_db.search)
    if isinstance(measure, str):
        try:
            parsed = json.loads(measure)
            if isinstance(parsed, list):
                measure = [m for m in parsed if isinstance(m, str)] or None
        except json.JSONDecodeError:
            pass

    if query and len(query) > 500:
        return {"error": "Query too long (max 500 characters)", "results": [], "total": 0}

    if isinstance(measure, list):
        cap_err = _check_list_cap("measure", measure, MAX_MEASURE_ITEMS)
        if cap_err:
            return cap_err

    sensor_db = get_sensor_db()
    return sensor_db.search(
        query=query,
        measure=measure,
        type=type,
        protocol=protocol,
        platform=platform,
        limit=clamp_limit(limit, MAX_PAGE_SIZE),
    )


@mcp.tool(
    annotations=ToolAnnotations(
        title="PCB Design Rules",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
@offload(RULES_POOL)
def get_design_rules(topic: str = "") -> dict:
    """Curated PCB design rules for power, protection, interfaces, MCUs, layout and EMC. An empty
    topic lists every rule file.

    Args:
        topic: Exact returned key (e.g., "power/ldo", "INDEX.md") or keyword matched against
            category/filename (e.g., "ldo", "usb", "esd", "esp32")

    Returns:
        content: The matched rule file(s) concatenated with --- separators
        matched_files: List of matched file keys (e.g. ["power/ldo", "power/switching"])
        topic: The search topic used

    Examples:
        get_design_rules("ldo") → LDO design rules (dropout, ESR, PSRR, thermal)
        get_design_rules("usb") → USB design rules (D+/D- routing, CC resistors, power delivery)
        get_design_rules("power") → All power rules (decoupling, LDO, switching, battery, power-path)
        get_design_rules("esp32") → ESP32 design rules (strapping pins, RF, USB-JTAG)
        get_design_rules("") → Full index of all available rule files
    """
    return _get_design_rules(topic)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Search Reference Boards",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
@offload(BOARD_POOL)
def board_search(
    query: str | None = None,
    component: str | None = None,
    tag: str | list[str] | None = None,
    org: str | None = None,
    layers: int | None = None,
    limit: int = 10,
) -> dict:
    """Search ~285 open-source reference board schematics to see how real designs use an IC: its
    passives, decoupling, pull-ups and power topology. Not for buying parts (jlc_search) or
    choosing sensors (sensor_recommend). Then call board_get(slug, focus=IC) for that IC's
    pin-by-pin neighborhood.

    Use component= for an IC name (searches the BOMs; when 2+ boards match it adds a cross-board
    consensus), query= for a function ("motor driver", "USB power delivery"), tag= to browse.
    Tags ignore case/whitespace; usb-c means usb. Unknown tags return valid_values from the catalog.
    Combine them to narrow.

    Args:
        query: Free text over name, description, key coverage, ICs, tags and org (e.g., "ESP32
            battery", "motor driver")
        component: IC or part (e.g., "DRV8825", "STM32F4", "MCP73831")
        tag: One tag or a list (AND), exact names, e.g. power-supply, sensors, motor-control,
            adc-dac, audio, rf-sdr, isolation, battery-charging, can-bus, display, inverter,
            led-driver, level-shifting, signal-conditioning, usb, usb-pd, ethernet, wifi, bluetooth,
            lora, gps-gnss, video, drone-uav, esd-protection, fpga, battery-management,
            current-sensing, energy-harvesting, relay, robotics, rs485, 3d-printer
        org: Organization (e.g., "Adafruit", "SparkFun", "Olimex", "Seeed Studio")
        layers: PCB layer count (e.g., 2, 4, 6, 8)
        limit: Max results (max 50)

    Returns:
        Boards sorted by relevance (BM25 for text queries) then component count.
        Each result includes: slug, name, org, source, source_url, format, description,
        key_coverage (rich functional summary), tags, key_ics, layers, dimensions, component_count,
        matched_by (why this result appeared: key IC, component, text match, tag, etc.).
        When searching by component with 2+ results, includes cross-board consensus. Each
        pin choice count is distinct boards, pct divides by consensus.board_count, boards lists
        supporting slugs, and quantities maps each supporting board to component occurrences.
        When browsing by tag only (no query= or component=), includes tag_consensus showing
        what ICs boards in that category commonly use with board counts and percentages.
        Use board_get with the slug + focus for IC-specific pin neighborhood.
    """
    # Handle JSON-string tag param from some MCP clients
    if isinstance(tag, str):
        try:
            parsed = json.loads(tag)
            if isinstance(parsed, list):
                tag = parsed
        except json.JSONDecodeError:
            pass

    if isinstance(tag, str):
        tag = "usb" if tag.strip().lower() == "usb-c" else tag.strip().lower()
    elif isinstance(tag, list):
        tag = ["usb" if t.strip().lower() == "usb-c" else t.strip().lower() for t in tag if isinstance(t, str)]

    # Validate tag list items
    if isinstance(tag, list):
        tag = [t for t in tag if isinstance(t, str) and len(t) <= 200][:10]

    if query and len(query) > 500:
        return {"error": "Query too long (max 500 characters)", "results": [], "total": 0}
    if component and len(component) > 200:
        return {"error": "Component too long (max 200 characters)", "results": [], "total": 0}
    if org and len(org) > 200:
        return {"error": "Org too long (max 200 characters)", "results": [], "total": 0}

    try:
        boards_db = get_boards_db()
        result = boards_db.search(
            query=query,
            component=component,
            tag=tag,
            org=org,
            layers=layers,
            limit=clamp_limit(limit, 50),
        )

        # Add cross-board consensus when searching by component and multiple boards match
        if component and result.get("total", 0) >= 2:
            consensus = boards_db.get_consensus(component)
            if consensus:
                result["consensus"] = consensus

        # Add tag consensus for tag-only queries (no query=, no component=)
        if tag and not query and not component:
            tag_str = tag if isinstance(tag, str) else (tag[0] if len(tag) == 1 else None)
            if tag_str:
                tag_consensus = boards_db.get_tag_consensus(tag_str)
                if tag_consensus:
                    result["tag_consensus"] = tag_consensus

        return result
    except Exception as e:
        logger.error(f"Board search failed: {type(e).__name__}: {e}")
        return {"error": "Board search failed", "results": [], "total": 0}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Reference Board",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
@offload(BOARD_POOL)
def board_get(
    slug: str,
    focus: str | None = None,
    include_bom: bool = False,
    include_nets: bool = False,
) -> dict:
    """A reference board from board_search. With focus=IC it returns that IC's pin-by-pin
    neighborhood (decoupling, pull-ups, connected parts) and, when 2+ boards use the IC, how the
    others wire it. Reply: focus_match_type says exact, partial or ref matching; consensus
    compares wiring across consensus.board_count boards; passives_omitted counts hidden plain passives.

    Args:
        slug: Board slug from board_search (e.g., "adafruit-esp32-s3-feather")
        focus: IC name (e.g., "MCP73831"; partial match: "ESP32" finds "ESP32-S3") or ref ("U3"):
            returns its pin neighborhood instead of the component list
        include_bom: Also list plain passives (R/C/L); by default only ICs, connectors and
            annotated passives (the rest are counted in passives_omitted)
        include_nets: Add the full netlist, positions and copper pours (can be 100 KB+)

    Returns:
        Default: ICs + connectors + annotated passives + neighborhood summary (ref/value per IC).
        With focus: focused IC's pin-grouped neighborhood + cross-board consensus +
            focus_match_type ("exact", "partial", or "ref") indicating how the focus was matched.
        With include_bom: adds all plain passives to component list.
        With include_nets: adds nets (name + pin list), positions (x/y/rotation), copper pours.
    """
    if not slug or len(slug) > 200:
        return {"error": "Invalid slug"}
    if focus and len(focus) > 200:
        return {"error": "Focus too long (max 200 characters)"}

    try:
        boards_db = get_boards_db()
        result = boards_db.get_board(slug, include_raw=include_nets, include_bom=include_bom, focus=focus)

        if result is None:
            return {"error": f"Board '{slug[:50]}' not found"}

        return result
    except Exception as e:
        logger.error(f"Board get failed: {type(e).__name__}: {e}")
        return {"error": "Board retrieval failed"}


def _easyeda_footprint_counts() -> dict[str, int | None] | None:
    """Seeded and stored footprint answers, so a deploy can be checked without the server's logs.
    stored is None when there's no usable store (memory only). None before startup."""
    global _easyeda_stored
    if _client is None:
        return None
    counted_at, stored = _easyeda_stored
    now = time.monotonic()
    if now - counted_at >= HEALTH_STORE_COUNT_TTL:
        stored = _client.easyeda_store_size()
        _easyeda_stored = (now, stored)
    return {"seeded": _easyeda_seeded, "stored": stored}


def _cse_store_counts() -> dict[str, int] | None:
    """Stored CSE searches and KiCad parts, refreshed at most every HEALTH_STORE_COUNT_TTL. None
    with no usable store (memory only) or before startup."""
    global _cse_stored
    if _cse_client is None:
        return None
    counted_at, counts = _cse_stored
    now = time.monotonic()
    if now - counted_at >= HEALTH_STORE_COUNT_TTL:
        counts = _cse_client.store_counts()
        _cse_stored = (now, counts)
    return counts


# Health check endpoint
async def health(request):
    return JSONResponse({
        "status": "healthy",
        "service": "pcbparts-mcp",
        "version": __version__,
        "easyeda_footprints": _easyeda_footprint_counts(),
        "cse_stored": _cse_store_counts(),
        "distributor_quota": {name: quota.status() for name, quota in _distributor_quotas.items()},
    })


async def usage_stats(request):
    """Anonymous usage counts per UTC day (stats.py), newest first. ?days=N (1-30, default 30); the
    file at USAGE_STATS_PATH keeps a year."""
    try:
        days = int(request.query_params.get("days", "30"))
    except ValueError:
        days = 30
    # The counts change all the time, but a minute old is fine for a page that graphs them
    return JSONResponse(stats.usage.summary(max(1, min(days, stats.PUBLIC_DAYS))),
                        headers={"Cache-Control": "public, max-age=60"})


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose declared body exceeds max_bytes (memory-amplification guard).

    MCP JSON-RPC calls are a few KB; the limit is far above any legitimate request.
    Requests without a Content-Length (chunked) are passed through.
    """

    def __init__(self, app, max_bytes: int = MAX_REQUEST_BODY_BYTES):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > self.max_bytes:
            return JSONResponse({"error": "Request body too large"}, status_code=413)
        return await call_next(request)


# Create ASGI app
def create_app():
    """Create the ASGI application."""
    # Body-size guard runs first (outermost), then rate limiting.
    # FastMCP handles CORS for MCP endpoints.
    middleware = [
        Middleware(BodySizeLimitMiddleware, max_bytes=MAX_REQUEST_BODY_BYTES),
        Middleware(RateLimitMiddleware, requests_per_minute=RATE_LIMIT_REQUESTS),
    ]

    # stateless_http=True required because Claude Code doesn't forward session cookies.
    # allowed_hosts: fastmcp 3.x rejects any Host header not in a localhost-only default with a
    # 421, so the public domain must be allowlisted or all proxied traffic breaks (see config).
    app = mcp.http_app(
        path="/mcp",
        middleware=middleware,
        transport="streamable-http",
        stateless_http=True,
        allowed_hosts=ALLOWED_HOSTS,
        # Browser clients send Origin; behind the TLS-terminating proxy the app sees http://,
        # so the https public origin must be allowlisted or those requests 403 (see config).
        allowed_origins=ALLOWED_ORIGINS,
    )

    # Add health check route
    app.routes.append(Route("/health", health))
    # Under /mcp because the pcbparts.dev proxy forwards only /mcp* and /health to this app
    app.routes.append(Route("/mcp/stats", usage_stats))

    return app


app = create_app()


class _HealthFilterLog(logging.Filter):
    """Suppress noisy /health access logs from Docker healthchecks."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return "/health" not in msg


def main():
    """Run the server."""
    import uvicorn

    # Our startup lines (DB sizes, footprint store) at INFO; everything else stays at WARNING.
    # Without this the root logger had no handler until mcp's first module-level logging call
    # (mcp/shared/session.py) set one up at WARNING, so INFO never printed. uvicorn's and
    # fastmcp's loggers keep their own handlers and don't propagate here.
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("pcbparts_mcp").setLevel(logging.INFO)

    # Suppress /health access log spam (Docker healthchecks every 10-30s)
    logging.getLogger("uvicorn.access").addFilter(_HealthFilterLog())

    uvicorn.run(
        "pcbparts_mcp.server:app",
        host="0.0.0.0",
        port=HTTP_PORT,
        lifespan="on",
    )


if __name__ == "__main__":
    main()
