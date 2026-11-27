"""PCB Parts MCP Server - Search electronic components for PCB assembly."""

import asyncio
import contextlib
import dataclasses
import datetime
import functools
import hmac
import inspect
import ipaddress
import json
import logging
import math
import os
import difflib
import re
import sqlite3
import threading
import time
import unicodedata
from contextlib import asynccontextmanager
from difflib import get_close_matches
from pathlib import Path
from typing import Annotated, Any, Callable, Literal, NamedTuple

from fastmcp import FastMCP
from fastmcp.exceptions import NotFoundError, ValidationError
from fastmcp.server.dependencies import get_http_request
from fastmcp.server.middleware import Middleware as FastMCPMiddleware
from mcp.types import ToolAnnotations
from pydantic import BeforeValidator, Field, WithJsonSchema, ValidationError as PydanticValidationError
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route

from . import __version__, call_log, file_logging, platform_ranges, stats
# Re-export the classifiers for existing imports and tests.
from .tool_outcomes import (
    _NOT_FOUND_ERRORS, _BAD_REQUEST_ERRORS, _ERROR_KINDS, _NOT_FOUND_REASONS,
    _FAILED_REASONS, _EMPTY_HINT_REASONS, _LCSC_CODE_HINT, _error_kind,
    _call_outcome, _lifecycle_errors, _lifecycle_outcome, _is_parts_reply,
    _parts_outcome, _parts_empty_reason, _first_reason, _empty_reason,
    _why_empty_result, _call_reason,
)
from .cache import (SELF_HOSTING_URL, AddressDailyQuota, CallerTally, DailyQuota, MouserKeyPool,
                    QuotaPool, QuotaStore, _next_utc_midnight, _utc_text)
from .config import (
    RATE_LIMIT_REQUESTS, PLATFORM_RATE_LIMIT, ANTHROPIC_IP_RANGES, OPENAI_IP_RANGES_FILE,
    DB_STUCK_WAIT_SECONDS, CONFIG_WARNINGS,
    HTTP_HOST, HTTP_PORT, DATASHEET_LINK_BASE, LOG_PATH, LOG_KEEP_DAYS, DEFAULT_MIN_STOCK, MAX_PAGE_SIZE, MAX_SEARCH_OFFSET,
    MOUSER_API_KEY, MOUSER_DAY_START_HOUR, DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET,
    DIGIKEY_CLIENT_ID_2, DIGIKEY_CLIENT_SECRET_2, MOUSER_EXTRA_API_KEYS, MOUSER_KEY_WARNINGS,
    DISTRIBUTOR_DAILY_LIMIT, DISTRIBUTOR_DAILY_PER_ADDRESS, DISTRIBUTOR_BLOCKED_ADDRESSES, DIGIKEY_PER_MINUTE,
    MOUSER_PER_MINUTE, MAX_ALTERNATIVES,
    clamp_limit, MAX_LIST_PARAM_ITEMS, MAX_MEASURE_ITEMS, MAX_REQUEST_BODY_BYTES,
    ALLOWED_HOSTS, ALLOWED_ORIGINS, EASYEDA_STORE_PATH, DISTRIBUTOR_QUOTA_PATH, USAGE_STATS_PATH,
    CSE_STORE_PATH, DISTRIBUTOR_STORE_PATH, LIFECYCLE_MAX_PARTS, GET_PARTS_MAX_ITEMS, GET_PARTS_MAX_MATCHES,
    CALL_LOG_DIR, STATS_TOKEN,
)
from .client import (DATASHEET_SIGNINGS_PER_MINUTE, DatasheetLinkBusy, EasyEDAComponentNotFound, JLCPCBClient,
                     JLCPCBUnavailable)
from .mouser import MouserAPIError, MouserClient, MouserError
from .extensions import ExtensionContext, extension_failed, load_digikey_ext
from .digikey import DigiKeyClient, DigiKeyError
from .distributor_store import DistributorStore
from .lifecycle import Entry, LifecycleLookup, Reading, STATUSES, makers_match, utc_text
from .cse import CSEClient
from .mounting import english_package
from .db_worker import BOARD_POOL, COMPONENT_POOL, RULES_POOL, SENSOR_POOL, database_pressure, offload, run_db
from .db import get_db, close_db
from .db.lookup import VIA, related_note
from .history_db import get_history_db, close_history_db
from .sensor_db import get_sensor_db, close_sensor_db
from .boards_db import get_boards_db, close_boards_db
from .search import SpecFilter, get_attribute_names
from .search.mpn import LCSC_CODE, PACKING_RULES, is_placeholder_mpn, looks_like_mpn, mpn_key, normalize_mpn, not_sent_reason
from .subcategory_aliases import (
    CATEGORY_ID_NOT_FOUND_HINT, CATEGORY_NOT_FOUND_HINT, SUBCATEGORY_ID_NOT_FOUND_HINT, SUBCATEGORY_NOT_FOUND_HINT,
)
from .search.query_builder import package_family_adjustments
from .search.spec_sort import SORTABLE_LABELS, SortSpecError, SpecSort
from .smart_parser import ParsedQuery, parse_smart_query, merge_spec_filters
from .smart_parser.mapping import DEFAULT_SPECS
from .smart_parser.types import extract_mounting_type
from .alternatives import SPEC_PARSERS
from .search.spec_filter import ATTRIBUTE_ALIASES, SPEC_TO_COLUMN, BatterySizeFilter, ConnectorFilter, FuseFilter, ScopedTextFilter
from .parsers import parse_resistance
from .pinout import parse_easyeda_footprint, parse_easyeda_pins
from .design_rules import get_design_rules as _get_design_rules, _RULES_DIR, _build_index

logger = logging.getLogger(__name__)

# Global state
_client: JLCPCBClient | None = None
_mouser_client: MouserClient | None = None
_digikey_client: DigiKeyClient | None = None
_cse_client: CSEClient | None = None
# Mouser/DigiKey answers and lifecycle readings, shared by both clients and part_lifecycle
_distributor_store: DistributorStore | None = None
_distributor_stored: tuple[float, dict[str, Any] | None] = (float("-inf"), None)  # (time.monotonic(), counts)
_categories: list[dict[str, Any]] = []  # Live category cache
_distributor_quotas: dict[str, QuotaPool] = {}  # "mouser"/"digikey" when configured
_address_daily: AddressDailyQuota | None = None


def _save_address_counts() -> None:
    if _address_daily is not None and DISTRIBUTOR_QUOTA_PATH:
        _address_daily.save(Path(DISTRIBUTOR_QUOTA_PATH).with_name("distributor_address_counts.json"))


def _caller_tallies() -> list:
    """The hourly per-IP lines of Mouser/DigiKey requests sent and held back: the quota pools', and
    the DigiKey client's ext lookups, including when an API pool is also configured."""
    tallies = [tally for quota in _distributor_quotas.values() for tally in (quota.callers, quota.held_back)]
    if _digikey_client is not None:
        tallies += [tally for tally in (getattr(_digikey_client, "callers", None),
                                        getattr(_digikey_client, "held_back", None)) if tally is not None]
    return tallies
_easyeda_seeded = 0  # rows in the seed table, counted at startup (components.db doesn't change)
_easyeda_stored: tuple[float, int | None] = (float("-inf"), None)  # (time.monotonic(), store size)
_cse_stored: tuple[float, dict[str, int] | None] = (float("-inf"), None)  # (time.monotonic(), store counts)
# Requests the per-IP rate limit turned away, per IP, logged as one line for each hour that had any
# with the five most-refused IPs (the only place refused IPs appear; /mcp/stats counts them without
# IPs; the privacy page describes the line)
_refused_callers = CallerTally("Per-IP rate limit", what="refusals")
# The AI platforms' address lists as loaded at startup (_load_platform_ranges), for /health: how many
# ranges each has and when OpenAI's list was made. None before the app starts.
_platform_ranges_info: dict[str, Any] | None = None
# The database's price breaks, for /health (a deploy whose artifact download failed shows as none):
# {"as_of": ComponentDatabase.price_tiers_as_of(), "parts": price_tiers_parts()}, None before startup
_price_tiers_info: dict[str, Any] | None = None

# /health is public, isn't rate limited and is fetched by every landing page visit, so the store
# count it shows is refreshed at most this often (seconds) instead of on every request.
HEALTH_STORE_COUNT_TTL = 60
# The catalog snapshot's scrape time (ComponentDatabase.scraped_at()), read at startup for /health's
# snapshot (the database doesn't change while the server runs; reading it per request could wait
# on the connection's lock on the event loop). None before startup or when the database has none.
_snapshot_as_of: str | None = None
# /health's snapshot is stale (information only: status and the 503 don't depend on it) when it is
# older than this: the scrape runs daily, so a day plus the scrape and deploy time
SNAPSHOT_STALE_HOURS = 30
_health_clock: Callable[[], float] = time.time  # epoch seconds; replaced in tests


@asynccontextmanager
async def lifespan(app):
    """Manage client lifecycle, build DB, and load categories on startup."""
    global _client, _mouser_client, _digikey_client, _cse_client, _categories, _easyeda_seeded, _easyeda_stored
    global _distributor_store, _distributor_stored, _price_tiers_info, _snapshot_as_of, _address_daily
    _client = JLCPCBClient(easyeda_store_path=EASYEDA_STORE_PATH or None)
    for warning in CONFIG_WARNINGS:  # settings that weren't usable, and the value used instead
        logger.warning(warning)
    if not STATS_TOKEN:
        logger.warning("STATS_TOKEN unset: /mcp/stats refuses every request")

    # Build/load DB on startup (not on first request)
    db = get_db()
    db._ensure_db()
    db_stats = db.get_stats()
    logger.info(f"Database ready: {db_stats.get('total_parts', 0)} parts")
    _snapshot_as_of = db.scraped_at()  # for /health's snapshot

    # Load categories from DB (updated daily by scraper, no API call needed)
    _categories = db.get_categories_for_client()
    _client.set_categories(_categories)
    _client.add_catalog_ids(*db.catalog_ids(), db.subcategory_name_map())
    logger.info(f"Loaded {len(_categories)} categories from database")

    # Seeded EasyEDA footprint answers (data/easyeda/footprints.csv, built into the DB)
    _client.set_easyeda_seed(db.get_easyeda_seed)
    _client.set_easyeda_pads_seed(db.get_easyeda_pads)
    # jlc_find_alternatives also looks in the database for parts that meet the rules
    _client.set_alternative_candidates(db.find_alternative_candidates)
    # and, for RF parts, at every maker's parts in the subcategory to check against the original's band
    _client.set_subcategory_parts(db.subcategory_parts)
    tiers_as_of = db.price_tiers_as_of()
    _client.set_alternative_price_tiers(db.get_price_tiers, tiers_as_of)
    _price_tiers_info = {"as_of": tiers_as_of, "parts": db.price_tiers_parts()}
    logger.info(f"Price tiers: {_price_tiers_info['parts']:,} parts, scraped {tiers_as_of}" if tiers_as_of else
                "Price tiers: none loaded; jlc_get_parts and jlc_get_part(mpn) give the 1-piece price only, "
                "jlc_get_part(lcsc) answers live")
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
    # Same published ranges as RateLimitMiddleware; local files only, never a runtime download.
    address_ranges = platform_ranges.load(ANTHROPIC_IP_RANGES, OPENAI_IP_RANGES_FILE).ranges

    # One count for both distributors: an address's Mouser and DigiKey lookups share the day's cap.
    # Blocked addresses get stored answers only; the log names how many ranges, never which.
    address_daily = _address_daily = AddressDailyQuota(
        DISTRIBUTOR_DAILY_PER_ADDRESS, key=lambda ip: None if ip in address_ranges else _address_key(ip),
        blocked=DISTRIBUTOR_BLOCKED_ADDRESSES)
    if DISTRIBUTOR_BLOCKED_ADDRESSES:
        logger.info(f"Mouser and DigiKey: live lookups blocked for {len(DISTRIBUTOR_BLOCKED_ADDRESSES)} address range(s)")
    if DISTRIBUTOR_QUOTA_PATH:
        carried = address_daily.load(Path(DISTRIBUTOR_QUOTA_PATH).with_name("distributor_address_counts.json"))
        if carried:
            logger.info("Per-address counts: %s addresses carried over from before the restart", carried)
    # Their answers (Mouser 3 days; DigiKey a day, not found 3 days) and lifecycle readings (60 days; nrnd and last-time-buy
    # 30, obsolete a year), kept across restarts when DISTRIBUTOR_STORE_PATH is set
    _distributor_store = DistributorStore(DISTRIBUTOR_STORE_PATH or None)
    _distributor_stored = (float("-inf"), None)
    _distributor_store.prune()
    stored = _distributor_store.counts()
    logger.info(f"Distributor store: {stored['answers']:,} answers and {stored['lifecycle']:,} lifecycle readings "
                + (f"kept in {DISTRIBUTOR_STORE_PATH}" if stored["kept_across_restarts"] else "(memory only)"))

    # Initialize Mouser client if API key is configured. Optional extra keys (MOUSER_API_KEY_2,
    # _3, ...) are each used once Mouser refuses the previous key (MouserKeyPool); the
    # warnings name ignored variables, never a key.
    for warning in MOUSER_KEY_WARNINGS:
        logger.warning(warning)
    if MOUSER_API_KEY:
        key_quotas = [DailyQuota("Mouser", DISTRIBUTOR_DAILY_LIMIT, store=quota_store, day_start_hour=MOUSER_DAY_START_HOUR,
                                 store_key="Mouser" if index == 0 else f"Mouser#{index + 1}",
                                 own_key="Mouser API key (free at https://www.mouser.com/api-hub/)")
                      for index in range(1 + len(MOUSER_EXTRA_API_KEYS))]
        mouser_quota = MouserKeyPool(key_quotas, per_minute=MOUSER_PER_MINUTE, address_daily=address_daily)
        _distributor_quotas["mouser"] = mouser_quota
        _mouser_client = MouserClient(MOUSER_API_KEY, quota=mouser_quota, store=_distributor_store,
                                      extra_keys=MOUSER_EXTRA_API_KEYS)
        counts = ", ".join(str(q.status()["used_today"]) for q in key_quotas)
        logger.info(f"Mouser client initialized: {len(key_quotas)} key(s) (requests today: {counts})")
        for index, quota in enumerate(key_quotas):
            if kept := quota.daily_refusals()[-5:]:
                episodes = "; ".join(
                    f"{utc_text(e['at'])}, count {e['count']}, " +
                    (f"accepted again {utc_text(e['resumed_at'])}" if e["resumed_at"] is not None else "still refused")
                    for e in kept)
                logger.info(f"Mouser key {index + 1} kept daily refusals: {episodes}")
    elif MOUSER_EXTRA_API_KEYS:
        logger.warning("Extra Mouser keys are set without MOUSER_API_KEY: Mouser lookups are off")

    # The DigiKey client: with credentials, the API and its daily quota per app
    ext = load_digikey_ext(ExtensionContext(address_daily, _distributor_store, DISTRIBUTOR_STORE_PATH))
    if ext is not None:
        try:
            await ext.start()
        except Exception as exc:  # a broken extension never takes the server down: API only
            extension_failed(exc)
            try:
                await ext.close()
            except Exception:
                pass
            ext = None
    second_app = None
    if bool(DIGIKEY_CLIENT_ID_2) != bool(DIGIKEY_CLIENT_SECRET_2):
        missing = "DIGIKEY_CLIENT_SECRET_2" if DIGIKEY_CLIENT_ID_2 else "DIGIKEY_CLIENT_ID_2"
        logger.error(f"{missing} is missing; using only the first DigiKey app")
    elif DIGIKEY_CLIENT_ID_2 and DIGIKEY_CLIENT_SECRET_2:
        second_app = (DIGIKEY_CLIENT_ID_2, DIGIKEY_CLIENT_SECRET_2)
    if DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET:
        app_quotas = [DailyQuota("DigiKey", DISTRIBUTOR_DAILY_LIMIT, store=quota_store,
                                store_key="DigiKey" if index == 0 else "DigiKey#2",
                                own_key="DigiKey API credentials (free at https://developer.digikey.com)")
                      for index in range(2 if second_app else 1)]
        digikey_quota = QuotaPool(app_quotas, per_minute=DIGIKEY_PER_MINUTE, address_daily=address_daily)
        _distributor_quotas["digikey"] = digikey_quota
        _digikey_client = DigiKeyClient(DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET, quota=digikey_quota,
                                        second_app=second_app, store=_distributor_store, ext=ext,
                                        address_daily=address_daily)
        counts = ", ".join(str(q.status()["used_today"]) for q in app_quotas)
        logger.info(f"DigiKey client initialized: {len(app_quotas)} app(s) (requests today: {counts})")
    elif ext is not None:
        if DIGIKEY_CLIENT_ID or DIGIKEY_CLIENT_SECRET:
            missing = "DIGIKEY_CLIENT_SECRET" if DIGIKEY_CLIENT_ID else "DIGIKEY_CLIENT_ID"
            logger.error(f"{missing} is missing; using the configured DigiKey extension")
        _digikey_client = DigiKeyClient(client_id="", client_secret="", store=_distributor_store, ext=ext,
                                        address_daily=address_daily)
        logger.info("DigiKey client initialized")
    else:
        _digikey_client = None

    if _distributor_quotas:
        logger.info(f"Distributor request counts: {f'kept in {quota_store.path}' if quota_store else 'memory only'}")

    # Private daily usage counts for /mcp/stats
    if USAGE_STATS_PATH:
        stats.usage.open(USAGE_STATS_PATH)
    stats.usage.record_start()  # this day's restarts, beside its callers and distinct part numbers
    tools = await mcp.list_tools(run_middleware=False)
    stats.usage.tools = {tool.name for tool in tools}
    stats.usage.tool_params = {tool.name: set(tool.parameters.get("properties", {})) for tool in tools}
    await call_log.recorder.open(CALL_LOG_DIR)
    catalog_task = asyncio.create_task(_load_call_catalog(call_log.recorder, db)) if CALL_LOG_DIR else None
    logger.info(f"Usage stats: {f'kept in {USAGE_STATS_PATH}' if USAGE_STATS_PATH else 'memory only'}")
    minute_task = asyncio.create_task(_every_minute())

    # CSE client always available (no API key needed)
    _cse_client = CSEClient(store_path=CSE_STORE_PATH or None)
    cse_counts = await asyncio.to_thread(_cse_client.store_counts)
    logger.info("CSE client initialized: " + (
        f"{cse_counts['searches']:,} searches and {cse_counts['kicad']:,} KiCad parts stored in {CSE_STORE_PATH}"
        if cse_counts is not None else "no store (memory only)"))

    yield

    minute_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await minute_task
    if catalog_task is not None:
        await catalog_task
    # Distributor lookups still in flight are cancelled first, so what they sent is in the hourly
    # lines and the stats saved below
    if _mouser_client:
        await _mouser_client.close()
    if _digikey_client:
        await _digikey_client.stop()
    _save_address_counts()
    for tally in _caller_tallies():
        tally.flush()  # the hour so far, so a deploy doesn't lose it
    _refused_callers.flush()
    try:
        stats.usage.flush_failed_calls(shutdown=True)
    except Exception:
        logger.exception("Usage stats: couldn't flush failed calls")
    await stats.usage.save_async()
    await call_log.recorder.flush(shutdown=True)
    if _cse_client:
        await _cse_client.close()
    if _distributor_store:
        _distributor_store.close()
        _distributor_store = None
    if _client:
        await _client.close()
    await run_db(COMPONENT_POOL, close_db)
    await run_db(COMPONENT_POOL, close_history_db)
    await run_db(SENSOR_POOL, close_sensor_db)
    await run_db(BOARD_POOL, close_boards_db)
    if _digikey_client:
        await _digikey_client.close()


# A database pool that has had calls waiting and started none for DB_STUCK_WAIT_SECONDS, at this
# many minute checks in a row, has a stuck worker (every database call queued behind it waits, and
# /health says unhealthy). A long queue that keeps moving is overload, not this:
# the server exits so Docker's `restart: unless-stopped` starts a fresh one. os._exit, not
# sys.exit: a normal exit would wait for the stuck worker thread and hang. Replaced in tests.
STUCK_CHECKS_BEFORE_EXIT = 2
_exit_process = os._exit
EXIT_FLUSH_SECONDS = 2


async def _load_call_catalog(recorder, db) -> None:
    """Catalog attribute names have no prebuilt metadata; populate shapes after readiness."""
    try:
        recorder.catalog = await run_db(COMPONENT_POOL, call_log.load_catalog, db)
    except Exception as exc:
        recorder._error("catalog", exc)


def _flush_before_exit(message: str) -> None:
    """Synchronous best effort with a deadline: a stuck disk must not prevent the restart."""
    def flush():
        with contextlib.suppress(Exception):
            os.write(2, (message + "\n").encode("utf-8"))
        for operation in (_save_address_counts, lambda: logger.error(message),
                          lambda: stats.usage.flush_failed_calls(shutdown=True), stats.usage.save,
                          lambda: asyncio.run(call_log.recorder.flush(shutdown=True))):
            try:
                operation()
            except Exception:
                logger.exception("Couldn't flush usage logging before exiting")
        for handler in logging.getLogger().handlers:
            with contextlib.suppress(Exception):
                handler.flush()

    writer = threading.Thread(target=flush, daemon=True, name="exit-logging")
    writer.start()
    writer.join(timeout=EXIT_FLUSH_SECONDS)
    # No logging here: a stalled writer may hold a logging-handler lock as well.


def _exit_if_stuck(stuck_checks: int) -> int:
    """The minute task's stuck-worker check: the updated count of checks in a row that found a
    database pool with calls waiting that had started none for DB_STUCK_WAIT_SECONDS
    (DatabasePressure.stalled_seconds); exits the process at STUCK_CHECKS_BEFORE_EXIT. This shouldn't happen (every call is a local SQLite read taking
    milliseconds); it guards against a hung disk or a runaway query."""
    stalled = database_pressure.stalled_seconds()
    stuck_checks = stuck_checks + 1 if stalled >= DB_STUCK_WAIT_SECONDS else 0
    if stuck_checks >= STUCK_CHECKS_BEFORE_EXIT:
        message = (f"Database calls have waited {stalled:.0f} s with none starting (over "
                   f"{DB_STUCK_WAIT_SECONDS:g} s at {stuck_checks} minute checks in a row): a worker "
                   "is stuck; exiting so Docker restarts the server")
        with contextlib.suppress(Exception):
            _flush_before_exit(message)
        _exit_process(1)
    return stuck_checks


async def _every_minute() -> None:
    """Every minute, log failed tool calls by label for finished minutes, the finished hour's sent
    and held-back Mouser/DigiKey counts and per-IP rate limit refusals (one line each, for hours
    that had any), save the usage counts and drop expired
    address-to-app links (AppsByAddress); every hour,
    drop expired Mouser/DigiKey answers from the store; exit if a database worker is stuck
    (_exit_if_stuck)."""
    minutes = 0
    stuck_checks = 0
    persistence = None
    next_prune = 60
    try:
        while True:
            await asyncio.sleep(60)
            minutes += 1
            try:
                stuck_checks = _exit_if_stuck(stuck_checks)
            except Exception:
                logger.exception("Stuck-worker check failed; trying again in a minute")
            try:
                for tally in _caller_tallies():
                    tally.flush_if_due()
                address_days = {id(q.address_daily): q.address_daily for q in _distributor_quotas.values()
                                if q.address_daily is not None}
                if (ext_day := getattr(_digikey_client, "_address_daily", None)) is not None:
                    address_days[id(ext_day)] = ext_day  # Also reset allowances without an API pool
                for address_day in address_days.values():
                    address_day.reset_if_due()
                _refused_callers.flush_if_due()
                stats.usage.flush_failed_calls()
                _apps_by_address.expire()  # expire quiet links even while persistence is stalled
                # Bound outstanding persistence to one task. Cancellation cannot stop an OS
                # write; timing it out and launching another would accumulate stuck workers.
                if persistence is None or persistence.done():
                    prune = minutes >= next_prune
                    persistence = asyncio.create_task(_persist_usage(prune=prune))
                    if prune:
                        next_prune = minutes + 60
            except Exception:
                logger.exception("Minute task failed; trying again in a minute")
    finally:
        if persistence is not None:
            # Finish the detached append before lifespan performs its final flush.
            await persistence


async def _persist_usage(*, prune: bool) -> None:
    try:
        await stats.usage.save_async()
        await call_log.recorder.flush()
        if prune:
            await asyncio.to_thread(stats.usage.prune)
            await asyncio.to_thread(file_logging.prune_file_logs)
            if _distributor_store is not None:
                _distributor_store.prune()
    except Exception:
        logger.exception("Usage persistence failed; trying again in a minute")


# Create MCP server
mcp = FastMCP(
    name="pcbparts",
    version=__version__,  # serverInfo.version: this server's, not fastmcp's
    instructions="PCB design assistant. Start with jlc_search (fast, daily in-stock snapshot); jlc_get_parts for BOMs, jlc_stock_check for live stock. Mouser/DigiKey share small daily limits across all users: use for parts JLCPCB does not carry or a requested distributor; batch Mouser. part_lifecycle for lifecycle. Design workflow: get_design_rules / board_search → board_get(focus=IC) → jlc_search → jlc_get_part → jlc_find_alternatives → cse_get_kicad. Full tool reference (arguments, defaults, limits, replies): https://pcbparts.dev/llms.txt.",
    lifespan=lifespan,
    # Don't leak raw exception text (SQL, file paths, internals) to anonymous clients.
    # Intentional user-facing errors are returned as dicts, not raised, so masking is UX-free.
    mask_error_details=True,
)


def _exception_outcome(error: Exception) -> str:
    """For the usage counts, how a tool call that raised went: bad arguments or an unknown tool are
    the caller's mistake; anything else broke here."""
    return "bad_request" if isinstance(error, (ValidationError, NotFoundError)) else "failed"


def _bad_request_reason(tool: str, content: dict, error: Exception | None) -> str:
    """One bounded label, never parsed from text that can contain caller arguments."""
    if isinstance(error, NotFoundError):
        return "unknown_tool"
    if isinstance(error, ValidationError):
        # FastMCP 3.4 wraps argument validation; body errors stay bare Pydantic errors.
        cause = error.__cause__
        if isinstance(cause, PydanticValidationError):
            errors = cause.errors(include_url=False, include_input=False)
            if errors:
                first = errors[0]
                location = first.get("loc") or ()
                name = location[0] if location else None
                name = name if name in stats.usage.tool_params.get(tool, set()) else "unknown_argument"
                kind = first["type"] if first["type"] in stats.ARG_ERROR_TYPES else "other"
                return f"arg:{name}:{kind}"
        return "other"
    if content.get("error"):
        return _first_reason(_BAD_REQUEST_ERRORS, str(content["error"])) or "other"
    if "status_counts" in content or _is_parts_reply(content) or (
            "parts" in content and "what_is_recorded" in content):
        return "all_inputs_invalid"
    return "other"


class AppsByAddress:
    """The app each caller address last connected with (the clientInfo name it sent with
    initialize, as stats.clean_app_name shows it), so the usage counts can say which apps call the
    Mouser and DigiKey tools (stats distributor_apps): this server is stateless, so a tools/call
    request carries no clientInfo and its session has none. Keyed by _address_key() (an IPv6
    address by its /64). An entry lasts `lifetime` seconds (stats.APP_LINK_MINUTES) from its
    address's last initialize or tool call (each of those, and the minute task, drops the expired
    ones), and at most max_size are kept, the least recently used dropped first. In memory only:
    never written, logged or shown. Kept in order of last use, so neither expiry nor the size bound
    scans the table."""

    def __init__(self, lifetime: float = stats.APP_LINK_MINUTES * 60, max_size: int = 10_000,
                 clock: Callable[[], float] | None = None):
        self.lifetime = lifetime
        self.max_size = max_size
        self._clock = clock or time.monotonic
        self._apps: dict[str, tuple[str, float]] = {}  # key: (app, last use), least recently used first

    def __len__(self) -> int:
        return len(self._apps)

    def expire(self, now: float | None = None) -> None:
        """Drop the entries a lifetime old: the first ones, as the table is in order of last use."""
        now = self._clock() if now is None else now
        while self._apps:
            key, (_, used) = next(iter(self._apps.items()))
            if now - used < self.lifetime:
                break
            del self._apps[key]

    def remember(self, client_ip: str | None, app: Any) -> None:
        """An initialize from client_ip (None: not over HTTP, nothing to link) sent this app name."""
        if not client_ip:
            return
        now, key = self._clock(), _address_key(client_ip)
        self.expire(now)
        self._apps.pop(key, None)  # re-added at the end: the most recently used
        self._apps[key] = (stats.clean_app_name(app), now)
        while len(self._apps) > self.max_size:
            del self._apps[next(iter(self._apps))]

    def app_for(self, client_ip: str | None) -> str | None:
        """The app client_ip last connected with, which this use keeps for another lifetime; None
        if it hasn't connected within one."""
        if not client_ip:
            return None
        now, key = self._clock(), _address_key(client_ip)
        self.expire(now)
        entry = self._apps.pop(key, None)
        if entry is None:
            return None
        self._apps[key] = (entry[0], now)
        return entry[0]


# The server's map; the middleware looks it up at each call, so tests can swap it
_apps_by_address = AppsByAddress()


def _call_app(context, caller: str | None) -> str | None:
    """The app behind a tool call: its session's clientInfo name where the session has one (stdio,
    or a stateful session), else the app its address last connected with; None when neither says
    (or the lookup fails: the call is still counted, under unknown)."""
    try:
        client_info = context.fastmcp_context.session.client_params.clientInfo
    except (AttributeError, RuntimeError):  # stateless HTTP: client_params is None
        client_info = None
    if client_info is not None:
        return client_info.name
    try:
        return _apps_by_address.app_for(caller)
    except Exception:
        logger.exception("Usage stats: couldn't find a call's app")
        return None


# Call-local notes may only split these otherwise-unspecific labels.
_NOTE_REASON_PREDECESSORS = {
    "part_number_sold_out": "part_number_not_in_stock",
    "part_number_unknown": "part_number_not_in_stock",
    "no_results_filtered": "no_results",
    "no_results_part_number": "no_results",
    "no_results_words": "no_results",
}

_observation_errors: set[str] = set()


def _observe(operation: str, fn: Callable, *args, **kwargs):
    """Independent best-effort recording; one content-free warning per failure streak."""
    try:
        value = fn(*args, **kwargs)
        _observation_errors.discard(operation)
        return value
    except Exception as exc:
        if operation not in _observation_errors:
            logger.warning("Usage recording: %s failed (%s)", operation, type(exc).__name__)
        _observation_errors.add(operation)


class UsageStatsMiddleware(FastMCPMiddleware):
    """Counts tool calls and connecting apps for /mcp/stats (stats.py). Counting never breaks a call."""

    async def on_initialize(self, context, call_next):
        try:
            client_info = context.message.params.clientInfo
            name = client_info.name if client_info else None
            stats.usage.record_app(name)
            _apps_by_address.remember(_caller_ip(), name)  # for distributor_apps: calls carry no app
        except Exception:
            logger.exception("Usage stats: couldn't count an app")
        return await call_next(context)

    async def on_call_tool(self, context, call_next):
        start = time.monotonic()
        token = _observe("start notes", stats.call_notes.set, {})
        try:
            try:
                result = await call_next(context)
            except Exception as e:
                self._record(context, start, error=e)
                raise
            self._record(context, start, result=result)
            return result
        finally:
            if token is not None:
                _observe("reset notes", stats.call_notes.reset, token)

    @staticmethod
    def _record(context, start: float, result: Any = None, error: Exception | None = None) -> None:
        try:
            outcome = _exception_outcome(error) if error is not None else _call_outcome(result)
            content = getattr(result, "structured_content", None)
            content = content if isinstance(content, dict) else {}
            reason = _call_reason(outcome, content, error) if outcome in ("not_found", "failed") else None
            notes = stats.call_notes.get() or {}
            if (outcome == "not_found" and error is None and isinstance(notes.get("reason"), str)
                    and _NOTE_REASON_PREDECESSORS.get(notes["reason"]) == reason):
                reason = notes["reason"]
            bad_reason = (_bad_request_reason(context.message.name, content, error)
                          if outcome == "bad_request" else None)
            caller = _caller_ip()
            app = _call_app(context, caller)
            ms = (time.monotonic() - start) * 1000
            tool = context.message.name
            if stats.usage.tools is not None and tool not in stats.usage.tools:
                tool = "unknown"
            if reason is not None and reason not in stats.REASONS:
                reason = "other"
            args = getattr(context.message, "arguments", None) or {}
            platform = False
            try:
                addresses = get_http_request().scope.get("pcbparts.platform_ranges")
                platform = addresses is not None and caller in addresses
            except RuntimeError:  # stdio / in-process calls have no caller address
                pass
            _observe("call counts", stats.usage.record_call, tool, outcome, ms, caller,
                     reason=reason, app=app, bad_request_reason=bad_reason)
            _observe("call log", call_log.recorder.record, tool, outcome, reason, bad_reason, ms, app, platform,
                     args, content, notes, stats.usage.tool_params.get(tool, set()), caller=caller)
            _observe("popular terms", stats.usage.record_terms, tool, outcome, args.get("query"),
                     caller, platform=platform)
            if isinstance(content.get("why_empty"), dict):
                _observe("empty diagnostics", stats.usage.record_why_empty, _why_empty_result(content["why_empty"]))
            _observation_errors.discard("classify call")
        except Exception as exc:
            if "classify call" not in _observation_errors:
                logger.warning("Usage recording: classify call failed (%s)", type(exc).__name__)
            _observation_errors.add("classify call")


# Other names callers send for a tool's argument, each seen in prod's rejected calls: the two
# distributor tools take the same thing, and digikey_get_part's was product_number until 0.10.3
# (clients with that name built in keep working); the two batch tools name their list differently,
# and jlc_get_parts was also sent lcsc_codes and identifiers (2026-11-21, 5 calls in a morning).
# Renamed before the arguments are validated, so the tool list shows one name. 0.10.6: the CSE
# tools take the part number as query, which callers send as the other tools' names.
ARGUMENT_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "mouser_get_part": {"part_number": ("product_number", "mpn", "query")},
    "digikey_get_part": {"part_number": ("product_number", "mpn", "query")},
    "jlc_get_parts": {"parts": ("lcsc", "lcsc_codes", "identifiers", "codes")},
    "jlc_stock_history": {"lcsc": ("parts",)},
    "cse_search": {"query": ("mpn", "part_number")},
    # 0.10.7: cse_search's rows name the ID cse_part_id, and callers pass it back by that name
    "cse_get_kicad": {"query": ("mpn", "part_number"), "part_id": ("cse_part_id",)},
    # the search tools' names, the other way round from VALUE_ALIASES' category/subcategory
    "jlc_search_help": {"category": ("category_name", "category_id"),
                        "subcategory": ("subcategory_name", "subcategory_id")},
}

_LCSC_CODE_ARG = re.compile(r"[Cc][0-9]{1,12}")


def _lcsc_or_mpn(value: Any, arguments: dict) -> tuple[str, Any] | None:
    """jlc_get_part's identifier/part_number: an LCSC code is lcsc, anything else mpn."""
    if isinstance(value, str) and value.strip():
        text = value.strip()
        return ("lcsc", text.upper()) if _LCSC_CODE_ARG.fullmatch(text) else ("mpn", text)
    return None


def _one_lcsc_code(value: Any, arguments: dict) -> tuple[str, Any] | None:
    """jlc_stock_check's lcsc: one LCSC code is a query for that part (a list stays an error that
    points to jlc_get_parts)."""
    if isinstance(value, str) and _LCSC_CODE_ARG.fullmatch(value.strip()):
        return "query", value.strip().upper()
    return None


def _lcsc_only(value: Any, arguments: dict) -> tuple[str, Any] | None:
    """jlc_get_part's query: an LCSC code is lcsc; other text stays an error that points to jlc_search."""
    if isinstance(value, str) and _LCSC_CODE_ARG.fullmatch(value.strip()):
        return "lcsc", value.strip().upper()
    return None


def _joined_part_numbers(value: Any, arguments: dict) -> tuple[str, Any] | None:
    """mouser_get_part's parts: a list (or JSON-array text) of part numbers is its "|"-joined batch.
    More than 10 still gets the tool's own limit error."""
    if isinstance(value, str) and value.lstrip().startswith("["):
        try:
            value = _parse_list_param(value)
        except ValueError:
            return None
    if isinstance(value, list) and value and all(isinstance(item, str) and item.strip() for item in value):
        return "part_number", "|".join(item.strip() for item in value)
    return None


def _id_or_name(prefix: str) -> Callable[[Any, dict], tuple[str, Any] | None]:
    """jlc_search_help's category/subcategory (a number or a name) as the search tools' *_id/*_name."""
    def resolve(value: Any, arguments: dict) -> tuple[str, Any] | None:
        if (number := _as_int(value)) is not None:
            return f"{prefix}_id", number
        if isinstance(value, str) and value.strip():
            return f"{prefix}_name", value
        return None
    return resolve


def _category_conflict(subcategory: str, home: str, category: str) -> dict:
    """Both search tools' reply for a subcategory outside the category given (the subcategory used to
    win unnoticed in jlc_search)."""
    return {"error": f"Invalid subcategory: '{subcategory}' is in {home}, not {category}; give a subcategory "
                     "of that category, or only one of them", "results": [], "total": 0}


_WHOLE_NUMBER_TEXT = re.compile(r"([+-]?[0-9]{1,9})(?:\.0*)?")  # ASCII digits: "²".isdigit() is True


def _as_int(value: Any) -> int | None:
    """A whole number as the tools' int arguments take one (2, 2.0, "2" or "2.0"); None for anything
    else. Every alias and jlc_search_help read IDs and pages with this, so they agree."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e9:
        return int(value)
    if isinstance(value, str) and (match := _WHOLE_NUMBER_TEXT.fullmatch(value.strip())):
        return int(match.group(1))
    return None


def _page_size(arguments: dict) -> int | None:
    """The page size both search tools use: limit (default 20) clamped as they clamp it."""
    limit = _as_int(arguments.get("limit", 20))
    return clamp_limit(limit, MAX_PAGE_SIZE) if limit is not None else None


def _page_to_offset(value: Any, arguments: dict) -> tuple[str, Any] | None:
    """jlc_stock_check pages; jlc_search takes offset: page n is offset (n - 1) * limit (page 0 is
    page 1, as jlc_stock_check takes it)."""
    size, page = _page_size(arguments), _as_int(value)
    if size and page is not None and page >= 0:
        return "offset", max(page - 1, 0) * size
    return None


def _offset_to_page(value: Any, arguments: dict) -> tuple[str, Any] | None:
    """jlc_search's offset on jlc_stock_check: only one that starts a page."""
    size, offset = _page_size(arguments), _as_int(value)
    if size and offset is not None and offset >= 0 and offset % size == 0:
        return "page", offset // size + 1
    return None


# Aliases whose target depends on the value: alias -> (the names that, when given, leave it to
# validation, and how it maps). The tools name the same thing differently: jlc_search_help takes
# category/subcategory as a number or name, the search tools *_id/*_name; jlc_search pages by
# offset, jlc_stock_check by page; jlc_get_part was sent identifier (2026-11-21).
VALUE_ALIASES: dict[str, dict[str, tuple[tuple[str, ...], Callable[[Any, dict], tuple[str, Any] | None]]]] = {
    "jlc_get_part": {**{name: (("lcsc", "mpn"), _lcsc_or_mpn)
                        for name in ("identifier", "part_number", "part_id", "model")},  # model: our replies' MPN field
                     "query": (("lcsc", "mpn"), _lcsc_only)},
    "jlc_search": {"subcategory": (("subcategory_id", "subcategory_name"), _id_or_name("subcategory")),
                   "category": (("category_id", "category_name"), _id_or_name("category")),
                   "page": (("offset",), _page_to_offset)},
    "jlc_stock_check": {"subcategory": (("subcategory_id", "subcategory_name"), _id_or_name("subcategory")),
                        "category": (("category_id", "category_name"), _id_or_name("category")),
                        "offset": (("page",), _offset_to_page),
                        "lcsc": (("query",), _one_lcsc_code)},
    "mouser_get_part": {"parts": (("part_number",), _joined_part_numbers)},
}


def _with_argument_aliases(tool: str, arguments: Any) -> Any:
    """The call's arguments with an alias renamed to the tool's own name: only when that name isn't
    given and exactly one of its aliases is (anything else is left for validation to refuse)."""
    if not isinstance(arguments, dict):
        return arguments
    for name, others in (ARGUMENT_ALIASES.get(tool) or {}).items():
        given = [other for other in others if other in arguments]
        if name not in arguments and len(given) == 1:
            arguments = {name if key == given[0] else key: value for key, value in arguments.items()}
    for alias, (family, resolve) in (VALUE_ALIASES.get(tool) or {}).items():
        if alias in arguments and not any(name in arguments for name in family):
            if (mapped := resolve(arguments[alias], arguments)) is not None:
                target, value = mapped
                arguments = {(target if key == alias else key): (value if key == alias else given)
                             for key, given in arguments.items()}
    # jlc_search reads mounting from the query ("SMD", "through hole"): mounting_type="smd" joins it
    if tool == "jlc_search" and isinstance(arguments.get("mounting_type"), str):
        mounting, rest = extract_mounting_type(arguments["mounting_type"])
        query = arguments.get("query")
        if mounting and not rest and (query is None or isinstance(query, str)):
            word = "SMD" if mounting == "SMD" else "through hole"
            arguments = {key: value for key, value in arguments.items() if key != "mounting_type"}
            arguments["query"] = f"{query} {word}" if query and query.strip() else word
    return arguments


async def _cse_lcsc(arguments: Any) -> Any:
    """cse_get_kicad(lcsc=...): every other part tool takes lcsc, so it's looked up in the catalog
    snapshot and searched by its MPN and maker. A code the snapshot lacks is left for validation to refuse."""
    if not isinstance(arguments, dict) or "lcsc" not in arguments or arguments.get("query") or arguments.get("part_id"):
        return arguments
    code = arguments["lcsc"]
    if not (isinstance(code, str) and _LCSC_CODE_ARG.fullmatch(code.strip())):
        return arguments
    part = await run_db(COMPONENT_POOL, get_db().get_by_lcsc, code.strip().upper())
    model = (part or {}).get("model")
    if not model:
        return arguments
    resolved = {("query" if key == "lcsc" else key): (model if key == "lcsc" else value)
                for key, value in arguments.items()}
    if not resolved.get("manufacturer") and part.get("manufacturer"):
        resolved["manufacturer"] = part["manufacturer"]
    return resolved


_ARG_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,39}")
_ERROR_ITEMS_SHOWN = 5  # unknown names (and other problems) an argument error lists

# What an unknown argument usually means on a tool, said in its error (beyond "did you mean")
_UNKNOWN_ARGUMENT_ADVICE = {
    ("jlc_search", "in_stock"): "jlc_search only lists parts in stock (stock >= 10): leave in_stock out, raise "
                                "min_stock for more, or use jlc_stock_check(min_stock=0) for out-of-stock parts.",
    ("jlc_search", "mounting_type"): "jlc_search reads mounting from the query: add SMD or through hole to query.",
    ("jlc_get_part", "query"): "jlc_get_part looks up one part by lcsc (an LCSC code) or mpn; to search by words or "
                               "values use jlc_search(query=...).",
    # _cse_lcsc took every lcsc it could: this one is malformed or not in the catalog snapshot
    ("cse_get_kicad", "lcsc"): "cse_get_kicad takes lcsc only for a part in the catalog snapshot (searched by its "
                               "MPN); for any other part give its MPN as query.",
}
_LIST_ADVICE = ("{tool} runs one search (query); for many parts at once use jlc_get_parts(parts=[...]), "
                "up to 50 LCSC codes or MPNs.")


def _unknown_argument_error(tool: str, arguments: Any, error: ValidationError, params: set[str]) -> ValidationError | None:
    """A clearer error for arguments the tool doesn't have: its own argument names, the likely
    meant one, and advice for common mix-ups. None for any other validation error (unchanged)."""
    cause = error.__cause__
    if not isinstance(cause, PydanticValidationError):
        return None
    problems = cause.errors(include_url=False, include_input=False)
    unknown = [str(item["loc"][0]) for item in problems
               if item.get("type") == "unexpected_keyword_argument" and item.get("loc")]
    if not unknown or not params:
        return None
    shown = unknown[:_ERROR_ITEMS_SHOWN]  # a request can hold thousands: bounded work and reply
    names = [repr(name) if _ARG_NAME.fullmatch(name) else "named that (not an identifier)" for name in shown]
    more = f" and {len(unknown) - len(shown)} more" if len(unknown) > len(shown) else ""
    lines = [f"{tool} has no argument {', '.join(names)}{more}. Its arguments: {', '.join(sorted(params))}."]
    candidates = sorted(params)
    for name in shown:
        if not _ARG_NAME.fullmatch(name):
            continue
        if advice := _UNKNOWN_ARGUMENT_ADVICE.get((tool, name)):
            lines.append(advice)
        elif tool == "jlc_stock_check" and isinstance(arguments, dict) and (
                isinstance(arguments.get(name), list)
                or (isinstance(arguments.get(name), str) and arguments[name].lstrip().startswith("["))):
            lines.append(_LIST_ADVICE.format(tool=tool))
        elif close := difflib.get_close_matches(name.lower(), candidates, n=1, cutoff=0.6):
            lines.append(f"Did you mean {close[0]!r} instead of {name!r}?")
    others = [item for item in problems if item.get("type") != "unexpected_keyword_argument"]
    for item in others[:_ERROR_ITEMS_SHOWN]:  # the other problems, briefly (no input values or links)
        where = ".".join(str(part) for part in item.get("loc") or ()) or "arguments"
        lines.append(f"{where}: {item.get('msg')}")
    if len(others) > _ERROR_ITEMS_SHOWN:
        lines.append(f"and {len(others) - _ERROR_ITEMS_SHOWN} more problems")
    return ValidationError("\n".join(lines))


_SURROGATE = re.compile("[\ud800-\udfff]")


def _without_surrogates(value: Any, depth: int = 0) -> Any:
    """value with any unpaired surrogate (invalid text a JSON escape can carry) as U+FFFD: SQLite
    can't encode one, so any text argument holding one failed the call with an internal error.
    The same object when nothing changed."""
    if isinstance(value, str):
        return _SURROGATE.sub("\ufffd", value) if _SURROGATE.search(value) else value
    if depth >= 4:
        return value
    if isinstance(value, list):
        items = [_without_surrogates(item, depth + 1) for item in value]
        return items if any(new is not old for new, old in zip(items, value)) else value
    if isinstance(value, dict):
        pairs = [(_without_surrogates(key, depth + 1), _without_surrogates(item, depth + 1)) for key, item in value.items()]
        changed = any(k is not key or v is not item for (k, v), (key, item) in zip(pairs, value.items()))
        return dict(pairs) if changed else value
    return value


class ArgumentAliasMiddleware(FastMCPMiddleware):
    """Accepts ARGUMENT_ALIASES in tool calls. Never breaks a call: on any surprise the call goes on as sent."""

    async def on_call_tool(self, context, call_next):
        try:
            message = context.message
            arguments = _with_argument_aliases(message.name, _without_surrogates(message.arguments))
            if message.name == "cse_get_kicad":
                arguments = await _cse_lcsc(arguments)
            if arguments is not message.arguments:
                context = context.copy(message=message.model_copy(update={"arguments": arguments}))
        except Exception:
            logger.exception("Argument aliases: couldn't read a tool call")
        try:
            return await call_next(context)
        except ValidationError as error:
            # Counted by UsageStatsMiddleware (inside this one) with its usual label first.
            try:
                tool = context.message.name
                params = stats.usage.tool_params.get(tool) or next(
                    (set(t.parameters.get("properties", {})) for t in await mcp.list_tools(run_middleware=False)
                     if t.name == tool), set())
                clearer = _unknown_argument_error(tool, context.message.arguments, error, params)
            except Exception:
                logger.exception("Argument aliases: couldn't explain an argument error")
                clearer = None
            if clearer is None:
                raise
            raise clearer from error.__cause__


mcp.add_middleware(ArgumentAliasMiddleware())
mcp.add_middleware(UsageStatsMiddleware())


# The per-IP rate limit counts each address's requests over a rolling window of this many seconds
RATE_LIMIT_WINDOW = 60

# Why a request was refused: the `reason` in its 429 body (llms.txt lists them).
# Add reasons, never rename one: clients branch on them. (0.10.0's server_busy went with the busy
# cap in 0.10.1.)
RATE_LIMIT_REASONS = {
    "per_ip_rate_limit": "this address sent its limit of requests in the last minute",
    "too_many_clients": "the server is tracking as many addresses as it can (MAX_TRACKED_IPS); "
                        "not about this address's use",
    "datasheet_rate_limit": "the short datasheet links' shared budget for new links (/mcp/datasheet) is spent; "
                            "not about this address's use",
}


class _Allowance(NamedTuple):
    """What the per-IP rate limit decided for one request; its X-RateLimit-* headers and its 429
    say the same."""
    limit: int  # requests a minute this address may send (RateLimitMiddleware._limit_for)
    remaining: int  # requests left in the current window, this one counted; 0 when refused
    reset: int  # whole seconds until the oldest counted request leaves the window, so one more is
    #             allowed (0: none counted); refused: until one request would be allowed again (>= 1)
    at: float  # when it was decided, epoch seconds (the middleware's wall clock), for resets_at
    refused: str | None = None  # why it was refused (a RATE_LIMIT_REASONS key); None: allowed


def _utc_iso(timestamp: float) -> str:
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_platform_ranges() -> platform_ranges.PlatformRanges:
    """The AI platforms' address ranges from config (ANTHROPIC_IP_RANGES, OPENAI_IP_RANGES_FILE),
    logged, and kept for /health. RateLimitMiddleware calls this once, when the app starts and
    Starlette builds it."""
    global _platform_ranges_info
    loaded = platform_ranges.load(ANTHROPIC_IP_RANGES, OPENAI_IP_RANGES_FILE)
    for warning in loaded.warnings:
        logger.warning(warning)
    limit = max(PLATFORM_RATE_LIMIT, RATE_LIMIT_REQUESTS)
    logger.info(f"Platform address ranges: {loaded.summary}; {limit:,} requests a minute per "
                f"platform address, {RATE_LIMIT_REQUESTS:,} for others")
    _platform_ranges_info = {**loaded.ranges.counts, "openai_list_created": loaded.openai_created}
    return loaded.ranges


class RateLimitMiddleware:
    """Rate limiting middleware: RATE_LIMIT_REQUESTS (300) requests a rolling minute per address,
    and PLATFORM_RATE_LIMIT for the AI platforms' shared addresses (platform_ranges.py: Anthropic's
    and OpenAI's published ranges), the limit _limit_for() gives each address. An IPv4 address is
    counted by itself and an IPv6 address by its /64 (_limit_key()), except a platform address.

    Every reply it sees says where the address stands: X-RateLimit-Limit (requests a minute),
    X-RateLimit-Remaining (left in the current window) and X-RateLimit-Reset (whole seconds until
    the oldest counted request leaves the window; see _Allowance). A refusal is a 429 with
    Retry-After and a JSON body: error and retry_after (as before 0.10.0, and clients read
    retry_after: keep it), reason (a RATE_LIMIT_REASONS key), resets_at (UTC) and tell_user (one
    sentence a client can show). Requests the per-IP limit refuses aren't counted. /health isn't
    limited or counted; its headers show where the address stands. /mcp/stats is limited and
    counted like any request (as before 0.10.0). The window runs on a monotonic clock, so a
    wall-clock step can't stretch or shorten it; only resets_at reads the wall clock.

    A request is charged to its address as it starts, before the app reads its body, so an
    exhausted address is refused without reading it and one address's concurrent bodies are
    bounded by its allowance. The body itself goes to the app untouched (BodySizeLimitMiddleware,
    outside this one, bounds it). Pure ASGI so response chunks pass straight through, including
    SSE streams.

    Includes protections against memory exhaustion from IP spoofing:
    - Maximum tracked addresses (10,000): past it, new addresses are refused (too_many_clients)
      while the addresses already tracked carry on, with a warning in the log at most once a minute
    - Stale addresses dropped as they go stale, oldest first (request_counts is kept in order of
      each address's last counted request, so no step scans every address)

    Each refusal (429) is counted in /mcp/stats (per_ip_refusals, no IP, by _refusal_group()) and,
    except too_many_clients, in an hourly most-refused log line (_refused_callers).
    """

    MAX_TRACKED_IPS = 10_000  # Prevent memory exhaustion from spoofed IPs

    def __init__(self, app, requests_per_minute: int = RATE_LIMIT_REQUESTS,
                 clock: Callable[[], float] | None = None, platform_per_minute: int = PLATFORM_RATE_LIMIT,
                 platform_addresses: platform_ranges.PlatformRanges | None = None,
                 wall_clock: Callable[[], float] | None = None):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.platform_per_minute = platform_per_minute
        # None: load them from config (and log how many), once: Starlette builds the middleware
        # when the app starts
        self.platform_addresses = (platform_addresses if platform_addresses is not None
                                   else _load_platform_ranges())
        self._clock = clock  # seconds for the window; None: time.monotonic()
        self._wall_clock = wall_clock  # epoch seconds for resets_at; None: time.time()
        # Counted requests per _limit_key(), in order of each key's last counted request (a counted
        # request moves its key to the end), so the stalest key is always first
        self.request_counts: dict[str, list[float]] = {}
        self._last_cleanup = self._now()
        self._too_many_refused = 0  # too_many_clients refusals since the last warning
        self._too_many_warned_at = float("-inf")

    def _now(self) -> float:
        return self._clock() if self._clock is not None else time.monotonic()

    def _wall(self) -> float:
        return self._wall_clock() if self._wall_clock is not None else time.time()

    def _get_client_ip(self, request) -> str:
        return _client_ip(request)

    def _is_platform(self, client_ip: str) -> bool:
        """Whether the address is in an AI platform's published range (shared by many users)."""
        return client_ip in self.platform_addresses

    def _limit_for(self, client_ip: str) -> int:
        """Requests a minute this address may send: PLATFORM_RATE_LIMIT for an AI platform's
        address (never less than RATE_LIMIT_REQUESTS), RATE_LIMIT_REQUESTS for any other. The
        check, the headers and the 429 all use this."""
        if self._is_platform(client_ip):
            return max(self.platform_per_minute, self.requests_per_minute)
        return self.requests_per_minute

    def _limit_key(self, client_ip: str) -> str:
        """What the address is counted under (_address_key): an IPv6 address by its /64, so its
        2**64 addresses can't each get an allowance and fill the table; except an AI platform's
        address, which is published and counted by itself."""
        return _address_key(client_ip, by_itself=self._is_platform)

    def _cleanup_stale_ips(self, now: float) -> None:
        """Remove addresses with no request left in the window: the first ones, as request_counts
        is in order of last requests, so this stops at the first that still counts."""
        window_start = now - RATE_LIMIT_WINDOW
        while self.request_counts:
            key, timestamps = next(iter(self.request_counts.items()))
            if timestamps and timestamps[-1] > window_start:
                break
            del self.request_counts[key]

    @staticmethod
    def _reset_seconds(timestamps: list[float], limit: int, now: float) -> int:
        """Whole seconds until one more request is allowed: until the oldest counted request leaves
        the window, or with no room, until enough have left for one more. 0 with none counted."""
        if limit <= 0:
            return RATE_LIMIT_WINDOW
        if not timestamps:
            return 0
        leaves_at = timestamps[max(0, len(timestamps) - limit)] + RATE_LIMIT_WINDOW
        return max(1, math.ceil(leaves_at - now))

    def _seconds_until_untracked(self, now: float) -> int:
        """With MAX_TRACKED_IPS addresses tracked, whole seconds until the first of them (the one
        with the oldest last request) goes stale and frees a place (at least 1)."""
        first = next(iter(self.request_counts.values()), None)
        last = first[-1] if first else now
        return max(1, math.ceil(last + RATE_LIMIT_WINDOW - now))

    def _allowance(self, client_ip: str, *, count: bool = True) -> _Allowance:
        """Judge and count a request. count=False only looks (exempt routes)."""
        now = self._now()
        window_start = now - RATE_LIMIT_WINDOW
        limit = self._limit_for(client_ip)
        key = self._limit_key(client_ip)

        if count:
            # Periodic cleanup every minute to remove stale IPs
            if now - self._last_cleanup > RATE_LIMIT_WINDOW:
                self._cleanup_stale_ips(now)
                self._last_cleanup = now
            # A new address while tracking too many: drop the stale ones, then refuse it if still
            # full, to prevent memory exhaustion. Addresses already tracked carry on.
            if key not in self.request_counts and len(self.request_counts) >= self.MAX_TRACKED_IPS:
                self._cleanup_stale_ips(now)
                if len(self.request_counts) >= self.MAX_TRACKED_IPS:
                    return _Allowance(limit, 0, self._seconds_until_untracked(now), self._wall(), "too_many_clients")

        timestamps = [t for t in self.request_counts.get(key, ()) if t > window_start]
        # Checked before adding the current request; a refused request isn't counted
        refused = count and len(timestamps) >= limit
        if count:
            if not refused:
                timestamps.append(now)
                self.request_counts.pop(key, None)  # re-added at the end: the newest last request
            self.request_counts[key] = timestamps
        remaining = 0 if refused else max(0, limit - len(timestamps))
        return _Allowance(limit, remaining, self._reset_seconds(timestamps, limit, now), self._wall(),
                          "per_ip_rate_limit" if refused else None)

    @staticmethod
    def _headers(allowance: _Allowance) -> dict[str, str]:
        return {"X-RateLimit-Limit": str(allowance.limit),
                "X-RateLimit-Remaining": str(allowance.remaining),
                "X-RateLimit-Reset": str(allowance.reset)}

    @classmethod
    def _refusal(cls, allowance: _Allowance, *, shared: bool = False) -> JSONResponse:
        """The 429 for a refused request; shared: the address is an AI platform's (_is_platform)."""
        wait, limit = allowance.reset, allowance.limit
        seconds = f"{wait} second{'' if wait == 1 else 's'}"
        if allowance.refused == "too_many_clients":
            tell_user = f"pcbparts is serving too many addresses at once; try again in {seconds}."
        else:
            allows = f"pcbparts allows {limit:,} request{'' if limit == 1 else 's'} a minute per address"
            if shared:
                allows += ", and this address is shared by many users of the same AI platform"
            tell_user = f"{allows}; try again in {seconds}, or run your own copy for heavy use: {SELF_HOSTING_URL}"
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": wait, "reason": allowance.refused,
                     "resets_at": _utc_iso(math.ceil(allowance.at + wait)), "tell_user": tell_user},
            headers={**cls._headers(allowance), "Retry-After": str(wait)},
        )

    def _refusal_group(self, client_ip: str, reason: str | None = None) -> str:
        """Which stats.REFUSAL_GROUPS group a refused address counts under: platform_ranges for an
        AI platform's address (PLATFORM_RATE_LIMIT), everyone_else for the rest; too_many_clients
        for a full address table, regardless of address. (Nothing counts under server_busy since
        0.10.1: that group holds 0.10.0's stored counts.)"""
        if reason == "too_many_clients":
            return reason
        return "platform_ranges" if self._is_platform(client_ip) else "everyone_else"

    def _count_refusal(self, client_ip: str, reason: str | None = None) -> None:
        """Count a refusal for /mcp/stats (no IP) and for the hourly most-refused log line, or for
        too_many_clients, the once-a-minute warning (those addresses are new, so a tally of them
        says nothing). Counting never breaks the reply."""
        _observe("refusal counts", stats.usage.record_refusal, self._refusal_group(client_ip, reason))
        # Distinct refused addresses (any reason), by the key the limit counts them under: a count only
        _observe("refused address counts",
                 lambda: stats.usage.record_address("rate_limited", self._limit_key(client_ip)))
        _observe("refusal log", call_log.recorder.refusal, reason or "per_ip_rate_limit", self._is_platform(client_ip))
        try:
            if reason == "too_many_clients":
                self._warn_too_many_clients()
            else:
                _refused_callers.record(self._limit_key(client_ip))
        except Exception:
            logger.exception("Couldn't note a rate-limit refusal for the log")

    def _warn_too_many_clients(self) -> None:
        """A warning for the first too_many_clients refusal and then at most once a minute while
        they go on, with the number since the last one."""
        now = self._now()
        self._too_many_refused += 1
        if now - self._too_many_warned_at >= RATE_LIMIT_WINDOW:
            logger.warning(f"Per-IP rate limit: tracking {len(self.request_counts):,} addresses "
                           f"(MAX_TRACKED_IPS {self.MAX_TRACKED_IPS:,}), so new addresses are refused "
                           f"(too_many_clients): {self._too_many_refused:,} refused since the last warning")
            self._too_many_warned_at, self._too_many_refused = now, 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        # The tool recorder must use this instance's exact ranges, including configured overrides.
        scope["pcbparts.platform_ranges"] = self.platform_addresses
        request = Request(scope)
        client_ip = self._get_client_ip(request)
        if request.url.path == "/health":  # not limited or counted
            allowance = self._allowance(client_ip, count=False)
        else:
            # Charged before any body is read: an exhausted address is refused without reading it,
            # and one address's concurrent bodies are bounded by its allowance
            allowance = self._allowance(client_ip)
            if allowance.refused:
                self._count_refusal(client_ip, allowance.refused)
                return await self._refusal(allowance, shared=self._is_platform(client_ip))(scope, receive, send)

        async def send_headers(message):
            if message["type"] == "http.response.start":
                message = {**message, "headers": [*message.get("headers", ()),
                           *((name.lower().encode("latin-1"), value.encode("latin-1"))
                             for name, value in self._headers(allowance).items())]}
            await send(message)

        return await self.app(scope, receive, send_headers)


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


def _address_key(client_ip: str, by_itself: Callable[[str], bool] | None = None) -> str:
    """One caller's key, for the per-IP limit (RateLimitMiddleware._limit_key) and AppsByAddress:
    an IPv4 address by itself (an IPv4-mapped IPv6 address is its IPv4 address), an IPv6 address
    by its /64, the usual allocation to one subscriber, unless by_itself(client_ip) says to keep
    it whole; anything else ("unknown", a hostname, garbage) as it is."""
    try:
        address = ipaddress.ip_address(client_ip.strip())
    except ValueError:
        return client_ip
    if address.version == 6:
        if address.ipv4_mapped is not None:
            return str(address.ipv4_mapped)
        if by_itself is None or not by_itself(client_ip):
            return str(ipaddress.IPv6Network((address, 64), strict=False))
    return str(address)


def _caller_ip() -> str | None:
    """The calling client's IP inside a tool, for the hourly distributor log. None outside an HTTP
    request (tests, stdio)."""
    try:
        return _client_ip(get_http_request())
    except RuntimeError:
        return None


def _encodable(text: str) -> bool:
    """Whether the text can be sent as UTF-8 (no unpaired surrogate)."""
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _sendable(value: Any) -> Any:
    """value with any text that can't be sent as UTF-8 written as its escapes ("\\ud800"), in dict
    keys and values and list items too: a reply holding a lone surrogate can't be serialised."""
    if isinstance(value, str):
        return value if _encodable(value) else value.encode("utf-8", "backslashreplace").decode("utf-8")
    if isinstance(value, dict):
        return {_sendable(key): _sendable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sendable(item) for item in value]
    return value


class _UnencodableArgument(ValueError):
    """A JSON-string argument holds text that can't be encoded as UTF-8 (an unpaired surrogate)."""


def _unencodable_text(value: Any) -> str | None:
    """The first string in value, at any depth (dict keys too), that can't be encoded as UTF-8."""
    stack = [value]
    while stack:  # not recursive: json.loads nests as deep as Python's limit allows
        item = stack.pop()
        if isinstance(item, str):
            if not _encodable(item):
                return item
        elif isinstance(item, dict):
            stack.extend(item.keys())
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return None


def _loads_argument(text: str, check_text: bool = True) -> Any:
    """json.loads of a JSON-string tool argument: every tool reads them through this. It's the one
    way text that can't be encoded as UTF-8 gets in: the MCP layer refuses a lone surrogate in the
    request itself, but json.loads turns an escaped one ("\\ud800" inside the string) into one,
    which SQLite and the reply's serialisation then fail on. Raises json.JSONDecodeError for
    invalid JSON, including what json.loads raises otherwise (both failed the call): RecursionError
    for nesting past Python's limit, and a plain ValueError for an integer over Python's digit limit
    (sys.get_int_max_str_digits, 4,300). With check_text, raises _UnencodableArgument when any
    string in it can't be encoded, which shows that string escaped, never raw. Without check_text
    the caller checks each string itself (jlc_get_parts and part_lifecycle make it that row's
    error)."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        raise
    except (RecursionError, ValueError) as exc:
        reason = "nested too deeply" if isinstance(exc, RecursionError) else "a number too long"
        raise json.JSONDecodeError(reason, text[:100], 0) from exc
    if check_text and (bad := _unencodable_text(value)) is not None:
        raise _UnencodableArgument(f"'{_sendable(bad[:60])}' holds an unpaired surrogate escape (\\ud800 to "
                                   "\\udfff without its pair), which isn't text")
    return value


# Helpers to handle JSON string arrays from MCP clients
def _parse_list_param(value: list[str] | str | None, *, allow_blank: bool = False) -> list[str] | None:
    """Accept a list, JSON array, or one literal value; never discard an element. Text that can't be
    encoded as UTF-8 raises _UnencodableArgument (a ValueError), like any other bad value."""
    if value is None:
        return None
    if isinstance(value, str):
        if value.lstrip().startswith(("[", "{", '"')):
            try:
                value = _loads_argument(value)
            except json.JSONDecodeError as exc:
                raise ValueError("expected a string or JSON array of strings") from exc
        else:
            value = [value]
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or any(not isinstance(v, str) or (not allow_blank and not v.strip()) for v in value):
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


def _sort_word(same: str, other: str) -> Callable[[Any], Any]:
    """jlc_search sorts by "stock" and jlc_stock_check by "quantity" for the same order: each takes
    the other's word (normalized like library_type) so a caller using one tool's word on the other
    isn't refused. The tool list still shows each tool's own word."""
    def normalize(value: Any) -> Any:
        value = _normalize_library_type(value)
        return same if value == other else value
    return normalize


SearchSort = Annotated[Literal["stock", "price", "spec"] | None, BeforeValidator(_sort_word("stock", "quantity"))]


def _normalize_sort_order(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    value = value.strip().lower()
    return {"ascending": "asc", "lowest": "asc", "descending": "desc", "highest": "desc"}.get(value, value)


SortOrder = Annotated[Literal["asc", "desc"] | None, BeforeValidator(_normalize_sort_order)]
StockSort = Annotated[Literal["quantity", "price"] | None, BeforeValidator(_sort_word("quantity", "stock"))]


@mcp.tool(
    annotations=ToolAnnotations(
        title="Stock Check (Live API)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
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
    """Live JLCPCB stock/prices, including stock under 10. Prefer jlc_search for parametric search.
    JLCPCB matches whole part numbers and their starts, not text inside them.

    Args:
        query: Keywords or one exact LCSC code ("C5947"); max 500 characters.
        category_id: Category ID from jlc_search_help.
        subcategory_id: Subcategory ID from jlc_search_help.
        category_name: Category, e.g. "Resistors".
        subcategory_name: Subcategory, e.g. "MOSFETs".
        min_stock: Minimum stock; default 10, 0 includes out-of-stock parts.
        library_type: basic, preferred, no_fee (both), extended, all; default all.
        package: One package, e.g. "0402".
        manufacturer: One maker.
        packages: OR list, JSON array or string; replaces package, max 50; no comma splitting.
        manufacturers: OR list, JSON array or string; replaces manufacturer, max 50.
        sort_by: quantity (most first, default) or price (least first).
        page: Page number; default 1.
        limit: Results per page; default 20, max 100.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    stock_filters_given = any(value is not None for value in (
        category_id, subcategory_id, category_name, subcategory_name, package, packages,
        manufacturer, manufacturers, library_type))

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
            return {"error": f"Category not found: '{category_name}'", "hint": CATEGORY_NOT_FOUND_HINT,
                    "similar_categories": await run_db(COMPONENT_POOL, get_db()._find_similar_categories, category_name)}

    # Resolve subcategory_name to subcategory_id if provided (ID takes precedence)
    resolved_subcategory_id = subcategory_id
    if subcategory_name and not subcategory_id:
        # Ensure categories are loaded before name resolution
        if not _categories:
            return {"error": "Categories not loaded. Server may still be starting up.", "hint": "Try again in a moment"}
        resolved_subcategory_id = _client.get_subcategory_id_by_name(subcategory_name)
        if resolved_subcategory_id is None:
            return {"error": f"Subcategory not found: '{subcategory_name}'", "hint": SUBCATEGORY_NOT_FOUND_HINT,
                    "similar_subcategories": await run_db(COMPONENT_POOL, get_db()._find_similar_subcategories,
                                                          subcategory_name)}

    # The client drops an ID it doesn't know, which searched every category; refused as jlc_search does
    # (a name resolved above is one it knows)
    if subcategory_id is not None and not _client._get_subcategory(subcategory_id):
        return {"error": f"Subcategory ID {subcategory_id} not found", "hint": SUBCATEGORY_ID_NOT_FOUND_HINT}
    if category_id is not None and not _client._get_category(category_id):
        return {"error": f"Category ID {category_id} not found", "hint": CATEGORY_ID_NOT_FOUND_HINT}
    if resolved_subcategory_id and resolved_category_id:
        home_id, sub = _client._get_subcategory(resolved_subcategory_id)
        if home_id != resolved_category_id:
            return _category_conflict(sub["name"], _client._get_category(home_id)["name"],
                                      _client._get_category(resolved_category_id)["name"])

    if call_log.recorder.path is not None:
        stats.note(stock_shape={"category_id": resolved_category_id, "subcategory_id": resolved_subcategory_id,
                                "library_type": library_type})

    # Replies give packages in English ("Plugin,12.6x4.4mm"), but JLCPCB filters on its own spelling
    # ("插件,12.6x4.4mm"): send both, so a package copied from any reply finds its parts
    if wanted := parsed_packages or ([package] if package else None):
        spellings = await run_db(COMPONENT_POOL, get_db().upstream_packages, wanted)
        if spellings != wanted:
            parsed_packages, package = spellings, None

    # A query that is one LCSC code is that part: JLCPCB's keyword search also matches the digits
    # inside part numbers (C5947 found four TLC5947 drivers; C1622 16.2k resistors and a 74LVC162245)
    lcsc_code = (query or "").strip().upper()
    if not LCSC_CODE.fullmatch(lcsc_code):
        lcsc_code = None

    try:
        result = await _client.search(
            query=query,
            category_id=resolved_category_id,
            subcategory_id=resolved_subcategory_id,
            min_stock=effective_min_stock,
            library_type=library_type if library_type != "all" else None,
            package=package,
            manufacturer=manufacturer,
            packages=parsed_packages,
            manufacturers=parsed_manufacturers,
            # JLCPCB's own order is by LCSC code: SMF18A's Preferred part with the most stock
            # (C19077512) was on page 2 of 2. For an LCSC code it puts that part first (C6965 was
            # third by stock, after parts with 6965 in their part number).
            sort_by=None if lcsc_code else sort_by or "quantity",
            page=1 if lcsc_code else effective_page,
            limit=MAX_PAGE_SIZE if lcsc_code else effective_limit,
            # A BOM line's stock and its price at the order quantity, from one reply
            with_prices=bool(lcsc_code),
        )
    except JLCPCBUnavailable as e:
        # JLCPCB didn't answer (rate limited / WAF / timeout ...): its message, as a dict so it survives
        # mask_error_details=True. One LCSC code: the database's row for it, if it has one, marked live_failed.
        if not lcsc_code:
            return {"error": str(e), "hint": _LIVE_SEARCH_DOWN_HINT}
        # A snapshot row has stock >= 10 (a gone one's is unknown, as its note says): only a higher
        # min_stock could have left it out
        filtered = bool(library_type not in (None, "all") or package or parsed_packages or manufacturer or parsed_manufacturers
                        or resolved_category_id or resolved_subcategory_id or effective_min_stock > DEFAULT_MIN_STOCK)
        if (reply := await _stock_check_from_database(lcsc_code, str(e), effective_page, effective_limit,
                                                      filtered)) is not None:
            stats.count_lcsc_lookup("jlc_stock_check", "fallback")
            return reply
        stats.count_lcsc_lookup("jlc_stock_check", "live_failed")
        return {"error": str(e), "hint": f"The daily snapshot doesn't list {lcsc_code} either; try again later."}
    except ValueError as e:  # JLCPCB answered, but its reply couldn't be read: the error, as before 0.10.2
        logger.exception("jlc_stock_check: JLCPCB's reply couldn't be read")
        if lcsc_code:
            stats.count_lcsc_lookup("jlc_stock_check", "live_failed")
        return {"error": str(e)}
    except Exception:  # raised as before (FastMCP logs it); still one lookup counted
        if lcsc_code:
            stats.count_lcsc_lookup("jlc_stock_check", "live_failed")
        raise
    if lcsc_code:
        stats.count_lcsc_lookup("jlc_stock_check", "live")
    if lcsc_code and not result.get("error"):
        exact = [p for p in result.get("results") or [] if (p.get("lcsc") or "").upper() == lcsc_code]
        result.update(results=exact if effective_page == 1 else [], page=effective_page,
                      per_page=effective_limit, total=len(exact), total_pages=len(exact), has_more=False)
        if not exact:
            filters = ", ".join(name for name, value in (
                ("library_type", library_type), ("package", package or parsed_packages),
                ("manufacturer", manufacturer or parsed_manufacturers),
                ("category", resolved_category_id or resolved_subcategory_id)) if value)
            result["hint"] = (f"No part {lcsc_code} with stock >= {effective_min_stock}"
                              + (f" matching {filters}" if filters else "")
                              + f". min_stock=0 includes out-of-stock parts; jlc_get_part(lcsc=\"{lcsc_code}\") "
                              "looks the code up.")
        return result
    # "2812" found no part number with it (only 594D capacitors in a 2812 case) though WS2812B and
    # XL-5050RGBC-2812B contain it: JLCPCB's search matches whole part numbers and their starts.
    # Name in-stock parts that contain it.
    fragment = (query or "").strip()
    if (not result.get("error") and re.fullmatch(r"(?=[\w-]*\d)[\w-]{3,}", fragment)
            and not any(fragment.upper() in (p.get("model") or "").upper() for p in result.get("results") or [])):
        if found := await run_db(COMPONENT_POOL, get_db().mpns_containing, fragment):
            result["hint"] = (f"JLCPCB's search matches whole part numbers and their starts, not text inside "
                              f"them. In-stock parts with {fragment!r} inside their part number include "
                              f"{', '.join(found)}: search one of those (jlc_stock_check(query={json.dumps(found[0])})).")
    try:
        if not result.get("error") and not result.get("results") and _empty_reason(result) == "no_results":
            stats.note(reason=("no_results_filtered" if stock_filters_given else "no_results_part_number"
                               if looks_like_mpn(fragment) else "no_results_words"))
    except Exception:
        logger.exception("Usage stats: couldn't classify an empty live search")
    return result


# On jlc_stock_check's error when JLCPCB's search doesn't answer (any query but one LCSC code the
# database has a row for)
_LIVE_SEARCH_DOWN_HINT = ("JLCPCB's live search didn't answer: meanwhile jlc_search searches the daily snapshot "
                          "(stock >= 10) and jlc_get_parts looks a BOM's parts up in it; try again later.")


async def _stock_check_from_database(code: str, live_error: str, page: int, per_page: int,
                                     filtered: bool) -> dict[str, Any] | None:
    """jlc_stock_check(query=code)'s reply when its live search failed: the part's row from the
    snapshot (or, gone, the one kept after it left) in the live reply's shape, marked live_failed,
    with the error and a note. filtered: the call gave filters or a min_stock, which aren't applied
    to it (the note says so). None when the database has no row for it or can't be read."""
    db = get_db()

    def read() -> tuple[Any, ...]:
        return db.get_part_snapshot(code, gone=True), db.scraped_at(), db.prices_as_of(), db.price_tiers_as_of()

    try:
        part, data_as_of, prices_as_of, tiers_as_of = await run_db(COMPONENT_POOL, read)
    except (OSError, sqlite3.Error):
        logger.exception("jlc_stock_check: snapshot lookup failed")
        return None
    if part is None:
        return None
    note = _live_failed_note(part, data_as_of)
    if filtered:
        note += " The filters and min_stock given weren't applied to it."
    return {"results": [part] if page == 1 else [], "page": page, "per_page": per_page, "total": 1, "total_pages": 1,
            "has_more": False, "data_as_of": data_as_of, "prices_as_of": prices_as_of,
            "price_tiers_as_of": tiers_as_of, "live_failed": True, "live_error": live_error, "note": note}


def _parse_spec_filters(filters: list[dict[str, Any]] | str | None) -> list[SpecFilter] | None:
    """Validate every explicit constraint, including JSON-string client payloads."""
    if filters is None:
        return None
    if isinstance(filters, str):
        try:
            filters = _loads_argument(filters)  # unencodable text: _UnencodableArgument, a ValueError
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
        if name.casefold() == "impedance @ frequency" and "@" in str(value):
            from .parsers import parse_impedance_at_freq
            if parse_impedance_at_freq(str(value)) is None:
                raise ValueError("impedance needs a valid frequency, such as 600Ohm@100MHz")
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
# CAD footprint names copied from a BOM ("BTN_KMR2", "R_0603_1608Metric", "SW_SPST_PTS645")
# name the footprint, not the part. No stocked MPN starts with one of these prefixes.
_FOOTPRINT_NAME = re.compile(
    r"(?:BTN|SW|R|C|CP|L|D|LED|FB|F|FUSE|Y|X|XTAL|CRYSTAL|J|CONN|TP|BZ|BUZZER|BT|RN|RESPACK|U|Q)_\S+",
    re.IGNORECASE,
)


# Fuse currents a query gives as a nominal rating (smart_parser's fuse families)
_NOMINAL_FUSE_CURRENTS = ("Hold Current", "Current Rating")


def _keep_part_number_matches(retry: dict, part_number_text: str, limit: int, offset: int = 0) -> dict:
    """A part-number retry keeps only parts whose MPN contains a requested part number, or is
    contained in it (JK-nSMD005/60V for nSMD005/60V, IR333-A for LED/IR333-A/5mm): the engine's
    MPN fallback shortens part numbers down to prefixes like "YS" that match unrelated parts.
    Counts follow the kept parts; a retry with more matches than one page is marked incomplete."""
    keys = [re.sub(r"[^0-9a-z]", "", t.casefold()) for t in part_number_text.split()]
    def matches_mpn(model: str) -> bool:
        mpn = re.sub(r"[^0-9a-z]", "", (model or "").casefold())
        return any(key in mpn or (len(mpn) >= 5 and mpn in key) for key in keys if key)
    if plan := retry.get("_facet_plan"):
        plan.mpn_predicate = matches_mpn
    kept = [p for p in retry.get("results", []) if matches_mpn(p.get("model"))]
    complete = (retry.get("total") or 0) <= len(retry.get("results", []))
    counts = {tier: sum(p.get("library_type") == tier for p in kept) for tier in ("basic", "preferred", "extended")}
    retry.update(results=kept[offset:offset + limit], total=len(kept), library_type_counts=counts,
                 no_fee_available=bool(counts["basic"] or counts["preferred"]))
    if "mpn_matches" in retry:
        retry["mpn_matches"].update({name: sum(p.get("mpn_match") == name for p in kept)
                                     for name in ("full", "same_suffix", "family")})
    if "page_info" in retry:
        retry["page_info"].update(limit=limit, offset=offset, returned=len(retry["results"]))
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
        if (_REFERENCE_DESIGNATOR.fullmatch(token) or _PACKAGE_OR_STANDARD.fullmatch(token)
                or _FOOTPRINT_NAME.fullmatch(token)):
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



def _facets_on_every_reply(fn):
    """facets=true promises a facets block: argument errors and early hints returned without one
    (the supercapacitor hint, part-number exclusions). They get the unavailable block."""
    signature = inspect.signature(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        if (isinstance(result, dict) and "facets" not in result
                and signature.bind_partial(*args, **kwargs).arguments.get("facets")):
            from .search.facets import collect_facets
            result["facets"] = collect_facets(get_db(), None)
        return result
    return wrapper

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
@_facets_on_every_reply
def jlc_search(
    query: str | None = None,
    subcategory_id: int | None = None,
    subcategory_name: str | None = None,
    category_id: int | None = None,
    category_name: str | None = None,
    spec_filters: list[dict[str, Any]] | str | None = None,
    min_stock: int = DEFAULT_MIN_STOCK,
    library_type: LibraryType = None,
    prefer_no_fee: bool = True,
    package: str | None = None,
    packages: list[str] | str | None = None,
    manufacturer: str | None = None,
    manufacturers: list[str] | str | None = None,
    match_all_terms: bool = True,
    sort_by: SearchSort = None,
    limit: int = 20,
    offset: int = 0,
    strict: bool = False,
    pcba_type: str | None = None,
    sort_spec: str | None = None,
    sort_order: SortOrder = None,
    facets: bool = False,
) -> dict:
    """Fast parametric search of in-stock JLCPCB parts: daily catalog snapshot (stock >= 10),
    1-piece prices refreshed weekly. jlc_stock_check and jlc_get_part(live=true) are live.
    Use jlc_search_help for spec names/types and sortable specs. Check datasheets before choosing.

    Args:
        query: Plain words, e.g. "10k resistor 0603 1%"; max 500 characters.
        subcategory_id: Subcategory ID from jlc_search_help.
        subcategory_name: Subcategory, e.g. "MOSFETs".
        category_id: Category ID; searches all its subcategories (spec names differ).
        category_name: Category, e.g. "Capacitors".
        spec_filters: Up to 50 {name, op, value}, e.g. {"name":"Iq","op":"<","value":"10uA"}; list/JSON array; names: jlc_search_help.
            Unitless uses V, A, ohms, F, H, Hz, W, mm, bytes. Repeated = on one spec is OR
            (Supply Voltage/Vin: all); = on a range means it includes the value.
            Operating Temperature: <= -40 reaches down to -40°C; >= 85 up to 85°C.
            Dropout at a load: 0.3V@500mA.
        min_stock: Minimum stock; default 10 (snapshot floor).
        library_type: basic, preferred, no_fee (both), extended, all; default all.
        prefer_no_fee: Basic/preferred first; default true.
        package: Package, e.g. "QFN-24-EP(4x4)"; bare families allow any body size.
        packages: OR list, JSON array or string; overrides package/query, max 50; no comma splitting.
        manufacturer: One maker.
        manufacturers: OR list, JSON array or string; replaces manufacturer, max 50.
        match_all_terms: Require all text terms; default true.
        sort_by: stock (default), price, spec; query may infer price/spec.
        limit: Results; default 20, range 1-100.
        offset: Results to skip; default 0, max 10000.
        strict: Default false allows reported relaxation; true keeps requirements, errors on unsupported constraints.
        pcba_type: economic or standard_only; one standard_only part moves the whole order to Standard assembly.
        sort_spec: E.g. "Iq", "RDS(on)@4.5V", "Dropout@500mA", "Vf@1A"; implies spec sort; unlisted last.
        sort_order: asc or desc; default stock desc, price/spec asc (query may infer spec order).
        facets: Manufacturer/package/library counts; default false.
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
    if pcba_type is not None:
        pcba_type = re.sub(r"[\s-]+", "_", pcba_type.strip().lower()) if isinstance(pcba_type, str) else pcba_type
        pcba_type = {"economic_and_standard": "economic", "standard": "standard_only"}.get(pcba_type, pcba_type)
        if pcba_type not in ("economic", "standard_only"):
            return {"error": f"Unsupported pcba_type: '{pcba_type}'", "valid_values": ["economic", "standard_only"],
                    "results": [], "total": 0}
        if not db.pcba_type_loaded():
            return {"error": "This catalog doesn't have PCBA types yet (they come with the next daily parts "
                             "update); search without pcba_type and check pcba_type with jlc_get_part.",
                    "results": [], "total": 0}

    # Parse explicit spec filters
    try:
        parsed_filters = _parse_spec_filters(spec_filters)
    except ValueError as exc:
        return _argument_error("spec_filters", exc, ["{name: text, op: =|>=|<=|>|<, value: text or number}"])
    try:
        parsed_packages = _parse_list_param(packages)
    except ValueError as exc:
        return _argument_error("packages", exc, ["string", "array of strings", "JSON array of strings"])
    try:
        parsed_manufacturers = _parse_list_param(manufacturers)
    except ValueError as exc:
        return _argument_error("manufacturers", exc, ["string", "array of strings", "JSON array of strings"])
    # The catalog's packages are in English since 0.8.15: "插件,12.6x4.4mm" from an older reply or a
    # BOM is "Plugin,12.6x4.4mm". A database built before that still has JLCPCB's spelling.
    if db.english_packages():
        package = english_package(package)
        if parsed_packages:
            parsed_packages = [english_package(p) for p in parsed_packages]
    if sort_by is not None:
        sort_by = _normalize_library_type(sort_by)
        if sort_by not in ("stock", "price", "spec"):
            return _argument_error("sort_by", ValueError("expected stock, price or spec"), ["stock", "price", "spec"])
    if sort_order is not None:
        sort_order = _normalize_sort_order(sort_order)
        if sort_order not in ("asc", "desc"):
            return _argument_error("sort_order", ValueError("expected asc or desc"), ["asc", "desc"])
    spec_sort = None
    if sort_spec is not None and not str(sort_spec).strip():
        sort_spec = None
    if sort_spec is not None or sort_by == "spec":
        if sort_by not in (None, "spec"):
            return {"error": f"Give a sort_spec only with sort_by=\"spec\" or no sort_by (sort_by=\"{sort_by}\" "
                             "sorts by something else)", "results": [], "total": 0}
        if sort_spec is None:
            return {"error": "Give a sort_spec with sort_by=\"spec\": the spec to sort on, such as \"RDS(on)\", "
                             "\"Iq\" or \"Dropout@500mA\"", "valid_values": SORTABLE_LABELS, "results": [], "total": 0}
        try:
            spec_sort = SpecSort.parse(sort_spec, sort_order)
        except SortSpecError as exc:
            return {"error": str(exc), "valid_values": exc.valid_values, "results": [], "total": 0}
        sort_by = None
    explicit_filters = list(parsed_filters or [])
    query_library = library_type is None

    # Reject abusive oversized list params before building a large SQL statement
    for _name, _val in (("spec_filters", parsed_filters), ("packages", parsed_packages),
                        ("manufacturers", parsed_manufacturers)):
        _cap_err = _check_list_cap(_name, _val)
        if _cap_err:
            return _cap_err

    # A category name means what it means to jlc_stock_check ("LED" is Optoelectronics); the search
    # then uses that category's exact name
    if category_name and not category_id:
        found = _client.match_category_by_name(category_name) if _client and _categories else None
        if found is None and not (_client and _categories):
            found = db.resolve_category_name(category_name)
        if found is None:
            return {"error": f"Category not found: '{category_name}'", "hint": CATEGORY_NOT_FOUND_HINT,
                    "similar_categories": db._find_similar_categories(category_name), "results": [], "total": 0}
        category_name = db.get_category_name(found) or category_name
    # An ID the catalog doesn't have searched everything (category_id) or found nothing (subcategory_id)
    if subcategory_id is not None and not db.get_subcategory_name(subcategory_id):
        return {"error": f"Subcategory ID {subcategory_id} not found", "hint": SUBCATEGORY_ID_NOT_FOUND_HINT,
                "results": [], "total": 0}
    if category_id is not None and not db.get_category_name(category_id):
        return {"error": f"Category ID {category_id} not found", "hint": CATEGORY_ID_NOT_FOUND_HINT,
                "results": [], "total": 0}
    if (subcategory_id or subcategory_name) and (category_id or category_name):
        explicit_sub = subcategory_id or db.resolve_subcategory_name(subcategory_name)
        explicit_cat = category_id or db.resolve_category_name(category_name)
        home = db.get_category_for_subcategory(explicit_sub) if explicit_sub else None
        if home and explicit_cat and home[0] != explicit_cat:
            return _category_conflict(db.get_subcategory_name(explicit_sub), home[1], db.get_category_name(explicit_cat))

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
    type_left_out = False  # every part type the query named is outside the category given

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
        reported_subcategory = parsed.subcategory
        if (subcategory_id or subcategory_name) and parsed.subcategory:
            # "600ohm 0603" with subcategory_name="Ferrite Beads" said chip resistor, a type not searched
            explicit_id = subcategory_id or db.resolve_subcategory_name(subcategory_name)
            explicit_name = db.get_subcategory_name(explicit_id) if explicit_id else None
            if explicit_name and explicit_name.lower() != parsed.subcategory.lower():
                reported_subcategory = explicit_name.lower()
                parsed.detected.pop("subcategory", None)
                # "addressable RGB LED" with subcategory_id=71 (discrete LEDs): the words name another
                # part type, so they're not searched, and the whole subcategory looked like the answer
                # A generic word in the same family ("capacitor" with Tantalum Capacitors) isn't noted
                parsed_id = db.resolve_subcategory_name(parsed.subcategory)
                parsed_type = db.get_subcategory_name(parsed_id) if parsed_id else None
                other_family = bool(parsed_id) and (db.get_category_for_subcategory(parsed_id)
                                                    != db.get_category_for_subcategory(explicit_id))
                if ((words := parsed.detected.get("component_type")) and (" " in words or other_family)
                        and explicit_name.lower() not in (name.lower() for name in parsed.subcategories or [])):
                    parsed.detected.setdefault("not_searched", []).append(
                        f"{words}: names {parsed_type or parsed.subcategory}, not the subcategory given "
                        f"({explicit_name}), so it isn't searched; leave out the subcategory to search that type")
        parsed_query_info = {
            "original_query": parsed.original,
            "detected": parsed.detected,
            "subcategory": reported_subcategory,
            "package": parsed.package,
            "mounting_type": parsed.mounting_type,
            "spec_filters": [f.to_dict() for f in parsed.spec_filters],
            "remaining_text": parsed.remaining_text,
        }

        if negation := parsed.detected.get("unsupported_negation"):
            return {"error": f"Part-number exclusions are not supported: {negation}. Search positively and exclude that identity during review.",
                    "results": [], "total": 0, "parsed": parsed_query_info}

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
        if parsed.spec_sort and sort_by is None and spec_sort is None:
            # "lowest Iq" in the query; an explicit sort_order still sets the direction
            spec_sort = parsed.spec_sort if sort_order is None else SpecSort(
                parsed.spec_sort.spec, descending=sort_order == "desc")
            if parsed.detected.pop("sort_by", None) == "price":
                parsed_query_info.setdefault("adjusted_filters", []).append({
                    "filter": "cheapest", "now": None,
                    "reason": f"results sort by one thing, and the query also asks for {parsed.detected['sort']['from']}; "
                              "sort_by=\"price\" sorts by price instead"})
        elif sort_by is None and spec_sort is None:
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
                explicit_packages = parsed_packages or ([package] if package else [])
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

        # "WS2812B LED" found 18 of the 19 WS2812B parts: JLCPCB files WS2812B-V6 (122k in stock) under
        # LED Indication - Discrete, not RGB LEDs(Built-in IC). The part number's matches in other
        # part types of the same category join the search.
        if not strict and part_number_text and parsed.subcategory and not (subcategory_name or subcategory_id):
            widened = _part_number_siblings(db, part_number_text, effective_subcategory_ids,
                                            effective_subcategory_name, max(0, min_stock))
            if widened:
                effective_subcategory_ids = widened
                parsed_query_info["subcategories"] = [
                    (db.get_subcategory_name(i) or "").lower() for i in widened]

        # An explicit category keeps only the part types the query words picked inside it: words that
        # name a type in another category would otherwise empty the search
        if (category_id or category_name) and not (subcategory_id or subcategory_name):
            wanted_category = category_id or db.resolve_category_name(category_name)
            if wanted_category:
                def _inside(sub_id: int | None) -> bool:
                    found = db.get_category_for_subcategory(sub_id) if sub_id else None
                    return bool(found) and found[0] == wanted_category
                dropped = []
                if effective_subcategory_ids:
                    dropped = [i for i in effective_subcategory_ids if not _inside(i)]
                    effective_subcategory_ids = [i for i in effective_subcategory_ids if _inside(i)] or None
                if effective_subcategory_name and not _inside(sub_id := db.resolve_subcategory_name(effective_subcategory_name)):
                    dropped.append(sub_id)
                    effective_subcategory_name = None
                if dropped:  # reported, so strict=true refuses instead of searching without the part type
                    names = ", ".join(dict.fromkeys(db.get_subcategory_name(i) or str(i) for i in dropped if i))
                    kept = effective_subcategory_ids or effective_subcategory_name
                    if parsed_query_info.get("subcategories") and effective_subcategory_ids:
                        parsed_query_info["subcategories"] = [
                            (db.get_subcategory_name(i) or "").lower() for i in effective_subcategory_ids]
                    else:
                        parsed_query_info.pop("subcategories", None)
                    if not kept:
                        parsed_query_info["subcategory"] = None
                        type_left_out = True
                    parsed_query_info.setdefault("adjusted_filters", []).append({
                        "filter": f"subcategory: {names or parsed.subcategory}", "now": None,
                        "reason": f"not in category {db.get_category_name(wanted_category)}, so that part type isn't searched"
                                  + ("; strict mode cannot omit it" if strict else "")})

        # Filters the parser made up must fit the part type: "5V relay" asked for Voltage Rating,
        # which no relay lists, and found nothing
        searched_ids = effective_subcategory_ids or (
            [i for i in [subcategory_id or db.resolve_subcategory_name(effective_subcategory_name)] if i]
            if (subcategory_id or effective_subcategory_name) else []
        )
        ohms = {v["normalized"] for v in parsed.detected.get("values", [])
                if v["type"] == "resistance" and "ohm" in v["raw"].lower()}
        auto_filters, adjusted = _fit_parsed_filters(db, parsed.spec_filters, searched_ids, ohms)
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
              or parsed.gate_drive_v is not None or parsed.spec_sort is not None):
            # Query was fully parsed into structured filters, no text needed
            effective_query = None

    # Internal reverse modes keep the existing database search interface and all ranking layers.
    effective_sort_by = sort_by or "stock"
    if spec_sort is None:
        if effective_sort_by == "stock" and sort_order == "asc":
            effective_sort_by = "stock_asc"
        elif effective_sort_by == "price" and sort_order == "desc":
            effective_sort_by = "price_desc"

    search_args: dict[str, Any] = dict(
        subcategory_id=subcategory_id,
        subcategory_name=None if effective_subcategory_ids else effective_subcategory_name,
        subcategory_ids=effective_subcategory_ids,
        category_id=category_id,
        category_name=category_name,
        spec_filters=parsed_filters,
        library_type=library_type if library_type != "all" else None,
        prefer_no_fee=prefer_no_fee,
        min_stock=max(0, min_stock),
        package=effective_package,
        packages=parsed_packages,
        manufacturer=manufacturer,
        manufacturers=parsed_manufacturers,
        mounting_type=effective_mounting_type,
        match_all_terms=match_all_terms,
        sort_by=effective_sort_by,
        limit=clamp_limit(limit, MAX_PAGE_SIZE),
        offset=min(max(0, offset or 0), MAX_SEARCH_OFFSET),
        # A pasted LCSC code (C2040) finds that part, not every code it starts.
        lcsc_codes=bool(query and query.split()) and all(LCSC_CODE.fullmatch(t) for t in query.split()),
        count_unlisted=True,
        pcba_type=pcba_type,
        spec_sort=spec_sort,
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
    orientation = [f for f in (parsed.preferred_specs if parsed else []) if f.name == "Mounting Type"]
    pd_specs = [f for f in (parsed.preferred_specs if parsed else []) if f.name != "Mounting Type"]
    if (pd_specs and searched_ids
            and all(db.get_subcategory_name(i).lower() == "usb pd" for i in searched_ids)):
        search_args["preferred_specs"] = pd_specs
        parsed_query_info.setdefault("adjusted_filters", []).extend({
            "filter": f"{f.name} = {f.value}", "now": f"rank {f.name} = {f.value} first",
            "reason": "many USB PD parts don't list this attribute; ranking keeps unlisted parts"
                      + ("; this is the negotiated output, not the supply voltage" if f.name == "Output Voltage" else ""),
        } for f in pd_specs)
    if orientation:
        search_args["preferred_specs"] = [*(search_args.get("preferred_specs") or []), *orientation]
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
    if facets:
        search_args["capture_plan"] = True
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

    # A CAD footprint name copied from a BOM ("KMR2 BTN_KMR2 switch") is in no part's text and
    # zeroes a search its other words would answer.
    footprint_names = [t for t in (effective_query or "").split() if _FOOTPRINT_NAME.fullmatch(t)]
    if (not strict and footprint_names and result.get("total") == 0 and not result.get("error") and parsed
            and not part_number_text):
        other_words = " ".join(t for t in effective_query.split() if not _FOOTPRINT_NAME.fullmatch(t))
        if other_words or parsed.subcategory or parsed.spec_filters:
            retry = db.search(query=other_words or None, **search_args)
            if retry.get("total"):
                retry["relaxed"] = {
                    "dropped_text": " ".join(footprint_names),
                    "reason": "CAD footprint names aren't in part descriptions, so they were left out",
                }
                if dropped_library:
                    retry["relaxed"]["dropped_text"] = dropped_library + " " + retry["relaxed"]["dropped_text"]
                    retry["relaxed"]["reason"] += "; the library preference was left out"
                result = retry

    # Words the parser couldn't place ("dual", "edge mount") are required in the description and
    # can zero a search the part type and filters would answer. Only for words left from a
    # natural-language query, never a part number or the caller's own subcategory or filters.
    # Without a recognized part type the words are what names it ("gizmo 3.3V 2A"): leaving them out
    # searched the whole catalog on the numbers alone, so the reply stays empty with a hint instead.
    if (not strict and result.get("total") == 0 and not result.get("error") and parsed and effective_query
            and not part_number_text and parsed.subcategory and not type_left_out
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
        retry_args = {**search_args, "subcategory_name": None, "subcategory_ids": None, "limit": MAX_PAGE_SIZE,
                      "offset": 0}
        page = search_args["limit"]
        retry = _keep_part_number_matches(db.search(query=part_number_text, **retry_args), part_number_text, page,
                                          search_args["offset"])
        dropped_filters = []
        # Only a full part number may cost the parsed values; "CL10 10uH inductor" keeps its 10uH.
        if not retry.get("total") and not retry.get("error") and protected_tokens:
            dropped_filters = [f.to_dict() for f in (parsed_filters or []) if f not in explicit_filters]
            if dropped_filters:
                retry_args["spec_filters"] = explicit_filters or None
                retry = _keep_part_number_matches(db.search(query=part_number_text, **retry_args),
                                                  part_number_text, page, search_args["offset"])
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

    # A fuse's current from the query is nominal ("1A 1812 fuse": Hold Current = 1A). With no stocked
    # part rated exactly that, the ratings above it answer, nearest first. After the retries above, so
    # words they leave out ("1.5A/3A") don't pass for a missing rating.
    nominal = [f for f in (search_args["spec_filters"] or []) if isinstance(f, FuseFilter) and f.operator == "="
               and f.name in _NOMINAL_FUSE_CURRENTS and f not in explicit_filters]
    if not strict and nominal and result.get("total") == 0 and not result.get("error"):
        widened = [dataclasses.replace(f, operator=">=") if f in nominal else f for f in search_args["spec_filters"]]
        retry = db.search(query=effective_query, **{**search_args, "spec_filters": widened,
                          "sort_by": "stock", "spec_sort": SpecSort.parse(nominal[0].name)})
        if retry.get("total"):
            search_args["spec_filters"] = widened
            retry["relaxed"] = {
                "widened_filters": [{"filter": f"{f.name} = {f.value}", "now": f"{f.name} >= {f.value}"}
                                    for f in nominal],
                "reason": "no stocked part has exactly this rating, so higher ratings are listed, lowest first",
            }
            if dropped_library:
                retry["relaxed"]["dropped_text"] = dropped_library
                retry["relaxed"]["reason"] += "; the library preference was left out"
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
    if note := _subcategory_note(result.get("results")):
        result["note"] = note

    # A filter on an attribute these parts hardly list is in ignored_filters, with the names they use
    # (tactile switches list Switch Height, not Height); counting every part as unlisted adds nothing
    if result.get("unlisted") and result.get("ignored_filters"):
        flagged = {f.get("filter") for f in result["ignored_filters"]}
        if not (unlisted := [u for u in result["unlisted"] if u["filter"] not in flagged]):
            result.pop("unlisted")
        else:
            result["unlisted"] = unlisted
    if search_args["offset"] and result.get("total") and not result.get("results") and not result.get("error"):
        result["hint"] = (f"offset {search_args['offset']} is past the last of {result['total']} "
                          f"match{'es' if result['total'] != 1 else ''}; use a smaller offset.")
    if result.get("total") == 0 and not result.get("error") and "hint" not in result:
        hints = []
        for item in result.get("unlisted") or []:
            hints.append(f"{item['parts']} part{'s' if item['parts'] != 1 else ''} meet{'' if item['parts'] != 1 else 's'} "
                         "the other constraints but list no value for "
                         f"{item['filter']}, which left {'them' if item['parts'] != 1 else 'it'} out "
                         "(see unlisted); check the datasheets.")
        if result.get("ignored_filters"):
            hints.append("See ignored_filters for unapplied or sparse attributes.")
        resolved_name = (result.get("filters_applied", {}).get("subcategory_resolved")
                         or (db.get_subcategory_name(searched_ids[0]) if searched_ids else None))
        if resolved_name:
            hints.append(f"Try jlc_search_help(subcategory={json.dumps(resolved_name)}) for attribute names and values.")
        explicit = [name for name, value in (("library_type", None if query_library else library_type),
                    ("package/packages", package or packages),
                    ("manufacturer/manufacturers", manufacturer or parsed_manufacturers),
                    ("category", category_id or category_name), ("pcba_type", pcba_type)) if value]
        if explicit:
            hints.append("Try without " + ", ".join(explicit) + ".")
        other_tier_total = 0
        if library_type in ("basic", "preferred", "no_fee") and not query_library:
            other_tier_total = db.search(query=effective_query, **{
                **search_args, "library_type": None, "limit": 1, "count_unlisted": False}).get("total") or 0
            if other_tier_total:
                matched = f" {part_number_text}" if part_number_text else ""
                # "No basic part matches; 16 parts do in other tiers (extended ... fee)" read as if all 16
                # had a fee when one was a Preferred part: name the no-fee tier's count apart
                free_tier = {"basic": "preferred", "preferred": "basic"}.get(library_type)
                free = db.search(query=effective_query, **{
                    **search_args, "library_type": free_tier, "limit": 1, "count_unlisted": False}).get("total") or 0 \
                    if free_tier else 0
                plural = other_tier_total != 1
                if free:
                    tiers = [f"{free} {free_tier} (no assembly fee; library_type=\"no_fee\" searches basic and "
                             "preferred)"]
                    if other_tier_total - free:
                        tiers.append(f"{other_tier_total - free} extended (an assembly fee per unique part)")
                    found = (f"{other_tier_total} part{'s' if plural else ''} do{'' if plural else 'es'} in other "
                             f"library tiers: {' and '.join(tiers)}")
                else:
                    found = (f"{other_tier_total} extended part{'s' if plural else ''} do{'' if plural else 'es'} "
                             "(an assembly fee per unique part)")
                hints.insert(0, f"No {library_type.replace('_', '-')} part matches{matched}; {found}.")
        if (parsed and effective_query and not part_number_text and not parsed.subcategory
                and not (subcategory_id or subcategory_name)):
            hints.insert(0, f"No part type matched {json.dumps(effective_query)}, so those words weren't left out. "
                            "Name the part type in common words, or find it with jlc_search_help() and pass "
                            "subcategory_name.")
        # The words-left-out retry above never runs with the caller's own subcategory or filters,
        # so say when the words alone are what found nothing ("ESD diode RF low capacitance" with
        # a Junction Capacitance filter)
        if (not strict and effective_query and not part_number_text
                and (subcategory_id or subcategory_name or spec_filters)):
            without_words = db.search(query=None, **{**search_args, "limit": 1, "count_unlisted": False}).get("total")
            if without_words:
                hints.insert(0, f"No part's description has all of the words {json.dumps(effective_query)}; "
                                f"without them {without_words} parts match the part type and filters. Words "
                                "aren't left out when you give subcategory_name or spec_filters, so drop "
                                "them or put them in a filter.")
        # A part number found only in other tiers is in stock (TL431 with no_fee: 308 extended parts)
        if part_number_text and not other_tier_total:
            # The part number may be in stock and only the filters beside it miss ("NE555 red" said
            # NE555 wasn't in stock when an LED colour filter emptied the search)
            narrowed = [name for name, value in (
                ("spec_filters", search_args.get("spec_filters")),
                ("package", search_args.get("package") or search_args.get("packages")),
                ("mounting_type", search_args.get("mounting_type")),
                ("manufacturer", manufacturer or parsed_manufacturers),
                ("category", category_id or category_name),
                ("subcategory", search_args.get("subcategory_id") or search_args.get("subcategory_name")
                 or search_args.get("subcategory_ids"))) if value]
            unfiltered = db.search(query=effective_query, **{
                **search_args, "spec_filters": None, "package": None, "packages": None, "mounting_type": None,
                "manufacturer": None, "manufacturers": None, "category_id": None, "category_name": None,
                "subcategory_id": None, "subcategory_name": None, "subcategory_ids": None,
                "preferred_specs": None, "limit": 1, "count_unlisted": False}).get("total") if narrowed else 0
            if unfiltered:
                hints.insert(0, f"{unfiltered} in-stock part{'s' if unfiltered != 1 else ''} match "
                                f"{part_number_text}, but none with the {', '.join(narrowed)} given or read from "
                                "the query (see filters_applied); drop them, or check its specs with jlc_get_part.")
            else:
                try:
                    # The only place search reads the sold_out table, for the usage label only, never the reply.
                    sold_out = db.get_sold_out_by_mpn(part_number_text)
                    stats.note(reason="part_number_sold_out" if sold_out else "part_number_unknown")
                except Exception:
                    logger.exception("Usage stats: couldn't classify an empty part-number search")
                hints.insert(0, f"No in-stock part matches {part_number_text}; try "
                                f"jlc_stock_check(query={json.dumps(part_number_text)}) for low or zero stock, "
                                "or search by part type and specs without the part number.")
        elif not part_number_text:
            hints.append("Use jlc_stock_check for low-stock parts.")
        result["hint"] = " ".join(hints)

    if result.get("total") == 0 and not result.get("error") and not result.get("ignored_filters"):
        from .search.diagnostics import diagnose_empty
        # capture_plan is an execution flag for facets, not a constraint to report
        result["why_empty"] = diagnose_empty(
            db, effective_query, {k: v for k, v in search_args.items() if k != "capture_plan"})

    if facets:
        from .search.facets import collect_facets
        plan = result.pop("_facet_plan", None)
        result["facets"] = collect_facets(db, None if result.get("error") else plan)

    # Stock is the daily snapshot's and price the weekly one's: C14663 read 38,555,997 at $0.0083 here
    # and 37,538,619 at $0.0072 in jlc_get_part, a day later
    if as_of := db.scraped_at():
        result["data_as_of"] = as_of
        result["prices_as_of"] = db.prices_as_of()
    return result


# A filter the parser made from a value, but whose spec the part type doesn't list: what to try
# instead, in order. A "3.3V level shifter" runs at 3.3V; a "4A high side switch" carries 4A.
_PARSED_FILTER_FALLBACKS: dict[str, list[tuple[str, str]]] = {
    "Voltage Rating": [("Supply Voltage", "="), ("Coil Voltage", "=")],
    "Current Rating": [("Output Current", ">="), ("Maximum Continuous Current", ">=")],
    # digital potentiometers; a ferrite bead's "600ohm" is its impedance, though beads list DCR too;
    # "mosfet 10mohm" and "inductor 10uH 100mohm" name a maximum
    "Resistance": [("Resistance Value (Ohms)", "="), ("Impedance @ Frequency", "="), ("RDS(on)", "<="),
                   ("DC Resistance(DCR)", "<=")],
    "Pin Structure": [("Holes Structure", "=")],  # female headers: 1x8P
}
# Only for a value written with an ohm unit: in an inductor query "1m" may be 1mH and "1R0" 1.0uH
_OHM_UNIT_FALLBACKS = {"RDS(on)", "DC Resistance(DCR)"}
# The parser's operator when the query writes no sign; any other operator was written and is kept
_DEFAULT_OPERATORS = {name: operator for name, operator in DEFAULT_SPECS.values()}
# A spec counts as listed by a part type when at least this share of its parts state it: op amps
# have "Voltage - Supply" on 14 of 4,900 parts, and a filter on it would hide the rest
_LISTED_SHARE = 0.1
_DIMENSIONS = re.compile(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*mm", re.IGNORECASE)


def _part_number_siblings(db: Any, part_number: str, ids: list[int] | None,
                          name: str | None, min_stock: int) -> list[int] | None:
    """The part type's subcategories plus others in its category that list the part number, or None.
    Only when the part type itself has some of them: when it has none, the search leaves the part
    type out instead (UWT1H220MCL "capacitor" is an electrolytic). More than 50 matches isn't a
    specific part number."""
    base = list(ids or [i for i in [db.resolve_subcategory_name(name)] if i] if (ids or name) else [])
    if not base:
        return None
    counts = db.subcategories_matching(part_number, min_stock)
    if not any(counts.get(i) for i in base) or sum(counts.values()) > 50:
        return None
    categories = {category[0] for i in base if (category := db.get_category_for_subcategory(i))}
    extra = sorted(i for i in counts if i not in base
                   and (category := db.get_category_for_subcategory(i)) and category[0] in categories)
    return base + extra if extra else None


def _fit_parsed_filters(
    db: Any, filters: list[SpecFilter], subcategory_ids: list[int], ohms: set[str] = frozenset()
) -> tuple[list[SpecFilter], list[dict[str, str | None]]]:
    """Keep each parsed filter whose spec the searched part types list; otherwise use a fallback
    spec they do list, or leave it out. Returns the filters and what was changed and why. With no
    part type known, filters are kept as they are. ohms holds the resistance values the query
    wrote with an ohm unit."""
    if not subcategory_ids:
        return list(filters), []
    def listed(name: str) -> bool:
        return db.attribute_share(subcategory_ids, get_attribute_names(name)) >= _LISTED_SHARE

    kept: list[SpecFilter] = []
    adjusted: list[dict[str, str | None]] = []
    for spec_filter in filters:
        if isinstance(spec_filter, (ScopedTextFilter, BatterySizeFilter)):
            kept.append(spec_filter)
            continue
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
            if name in _OHM_UNIT_FALLBACKS and spec_filter.value not in ohms:
                continue
            if name == "Impedance @ Frequency" and 0 < (parse_resistance(spec_filter.value) or 0) < 1:
                # Under 1 ohm it's a bead's DCR: 45 of 6,400 beads and common mode filters list an
                # impedance that low, and 43 of those are "0Ω@100MHz"
                continue
            if listed(name):
                # "mosfet > 10mohm" became RDS(on) <= 10mOhm
                if spec_filter.operator != _DEFAULT_OPERATORS.get(spec_filter.name, operator):
                    operator = spec_filter.operator
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
    """Browse categories (no args), subcategories, or filterable specs with types, values and sort_spec
    names for jlc_search. Detailed query syntax and reply fields: https://pcbparts.dev/llms.txt.

    Args:
        category: Category name/ID, e.g. "Connectors"; default null.
        subcategory: Subcategory name/ID, e.g. "MOSFETs"; default null; wins over category.
    """
    # Subcategory mode: list filterable attributes
    if subcategory is not None:
        db = get_db()
        if (number := _as_int(subcategory)) is not None:
            return db.list_attributes(subcategory_id=number)
        return db.list_attributes(subcategory_name=str(subcategory))

    # Category mode: list subcategories
    if category is not None:
        if not _categories:
            return {"error": "Categories not loaded. Server may still be starting up."}
        db = get_db()

        # A name resolves as both search tools resolve category_name, so a name one tool takes, every tool takes
        number = _as_int(category)
        wanted = number if number is not None else _client.match_category_by_name(str(category))
        matched = next((c for c in _categories if c["id"] == wanted), None) if wanted is not None else None
        if not matched and wanted is not None:  # a category with no part in the snapshot (jlc_stock_check's)
            known, subcategories = db.catalog_ids()
            if wanted in known:
                matched = {"id": wanted, "name": known[wanted]["name"], "subcategories": [
                    {"id": sub_id, "name": sub["name"], "count": 0}
                    for sub_id, sub in sorted(subcategories.items()) if sub.get("category_id") == wanted]}

        if not matched and number is not None:
            return {"error": f"Category ID {number} not found", "hint": CATEGORY_ID_NOT_FOUND_HINT}
        if not matched:
            return {"error": f"Category not found: '{category}'", "hint": CATEGORY_NOT_FOUND_HINT,
                    "similar_categories": db._find_similar_categories(str(category))}

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
        title="Recorded Stock History",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
@offload(COMPONENT_POOL)
def jlc_stock_history(lcsc: str | list[str], days: Annotated[int, Field(ge=1, le=366, strict=True)] = 180) -> dict:
    """Recorded low-stock events, not live stock: one code gets the newest 100 events, a list 10 each.
    Recording is selective; no events doesn't mean stable stock, and gone isn't a confirmed stockout.
    Use jlc_stock_check for live stock.

    Args:
        lcsc: One LCSC code ("C8314") or up to 50; list/JSON array, deduplicated, never comma-split.
        days: Calendar days ending on the newest recorded date; default 180, range 1-366.
    """
    invalid_code = {"error": "lcsc must be an LCSC C-code (e.g., C6186); use jlc_get_part(mpn=...) to find the code for an MPN"}
    if not isinstance(lcsc, str) or lcsc.lstrip().startswith("["):
        try:
            # Blank list entries are per-part code errors, rather than rejecting the BOM.
            codes = _parse_list_param(lcsc, allow_blank=True)
        except ValueError as exc:
            return _argument_error("lcsc", exc, ["string", "array of strings", "JSON array of strings"])
        if not codes:
            return {"error": "lcsc must be a nonempty list of up to 50 LCSC C-codes"}
        if error := _check_list_cap("lcsc codes", codes, 50):
            return error
        codes = list(dict.fromkeys(code.strip().upper()[:20] for code in codes))
        valid_codes = [code for code in codes if re.fullmatch(r"C[0-9]{1,12}", code)]
        if type(days) is not int or not 1 <= days <= 366:
            return {"error": "Invalid days: use an integer from 1 to 366"}
        try:
            result = get_history_db().history_many(valid_codes, days)
        except (OSError, sqlite3.Error):
            logger.exception("Stock history database unavailable")
            return {"error": "Stock history is not available on this server"}
        db = get_db()
        stock = db.get_by_lcsc_batch(valid_codes)
        missing = [code for code in valid_codes if not stock.get(code)]
        gone = db.get_sold_out_rows(missing) if missing else {}
        histories = {part["lcsc"]: part for part in result["parts"]}
        result["parts"] = [
            {"lcsc": code, **_current_stock(stock.get(code), gone.get(code)), **histories[code]}
            if code in histories else {"lcsc": code, **invalid_code}
            for code in codes
        ]
        result["current_stock_as_of"] = db.scraped_at()
        return result
    lcsc = lcsc.strip().upper()[:20]  # ASCII digits, bounded: "C" + a million digits was echoed back
    if not re.fullmatch(r"C[0-9]{1,12}", lcsc):
        return invalid_code
    if type(days) is not int or not 1 <= days <= 366:
        return {"error": "Invalid days: use an integer from 1 to 366"}
    try:
        result = get_history_db().history(lcsc, days)
    except (OSError, sqlite3.Error):
        logger.exception("Stock history database unavailable")
        return {"error": "Stock history is not available on this server"}
    db = get_db()
    part = db.get_by_lcsc(lcsc)
    result.update(_current_stock(part, None if part else db.get_sold_out_rows([lcsc]).get(lcsc)))
    result["current_stock_as_of"] = db.scraped_at()
    return result


def _current_stock(part: dict[str, Any] | None, gone: dict[str, Any] | None) -> dict[str, Any]:
    """jlc_stock_history's current_stock: the snapshot's stock, else None, with gone_since for a part
    kept after it left the snapshot (its stock unknown: under 10, or no longer listed)."""
    if part:
        return {"current_stock": part["stock"]}
    if gone:
        return {"current_stock": None, "gone_since": gone["gone_since"]}
    return {"current_stock": None}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Part Details",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def jlc_get_part(lcsc: str | None = None, mpn: str | None = None, live: bool = False) -> dict:
    """Part details, price tiers, datasheet_pdf and EasyEDA footprint availability. LCSC lookup uses the
    snapshot; live=true, an absent code or missing price tiers uses JLCPCB live (cached up to an hour).
    MPN lookup always uses the daily snapshot, including gone parts. For batches use jlc_get_parts;
    for lifecycle use part_lifecycle; for footprint pads use jlc_get_pinout(footprint=true).

    Args:
        lcsc: LCSC code, e.g. "C82899"; wins over mpn.
        mpn: MPN, e.g. "LM358P"; max 100 characters; also matches packing/separator variants.
        live: Live lookup for lcsc; default false, ignored for mpn.
    """
    if not lcsc and not mpn:
        return {"error": "Must provide either lcsc or mpn"}

    # MPN lookup via local database
    if mpn and not lcsc:
        if len(mpn) > 100:
            return {"error": "MPN too long (max 100 characters)"}
        if _has_control_characters(mpn):  # a NUL broke the full-text query (an exception, not a reply)
            return dict(_CONTROL_CHARACTERS)
        db = get_db()
        match_info: dict[str, Any] = {}
        results = await run_db(COMPONENT_POOL, db.get_by_mpn, mpn, match_info=match_info, with_prices=True)
        gone_info: dict[str, Any] = {}
        gone = await run_db(COMPONENT_POOL, db.get_sold_out_by_mpn, mpn, match_info=gone_info, with_prices=True)
        kind, listed, info, matched = _mpn_answer(mpn, results, match_info, gone, gone_info)
        if kind == "gone":
            listed = _with_stored_lifecycle(listed)
            # The part asked for left the snapshot: answer from what the catalog had, pointing to the live check
            reply = {"mpn": mpn, "data_as_of": db.scraped_at(), "prices_as_of": db.prices_as_of(),
                     "price_tiers_as_of": db.price_tiers_as_of(), "total": len(listed),
                     **_match_flags(matched, info), "results": listed, **_public(info)}
            if note := _subcategory_note(listed):
                reply["note"] = " ".join(filter(None, [reply.get("note"), note]))
            reply["hint"] = _GONE_HINT
            reply["next_call"] = {"tool": "jlc_stock_check", "arguments": {"query": mpn, "min_stock": 0, "limit": 10}}
            return reply
        if not results:
            if is_placeholder_mpn(mpn):
                hint = (f"'{mpn.strip()}' is a BOM placeholder (part not fitted or not chosen), not a "
                        "part number. Search by value and package with jlc_search instead.")
            else:
                hint = ("The local catalog only lists in-stock parts (stock >= 10). "
                        f"Try jlc_stock_check(query={json.dumps(mpn)}) for low or zero stock"
                        + _other_distributors_clause() + ".")
                if LCSC_CODE.fullmatch(mpn.strip()):
                    hint = (f"'{mpn.strip()}' looks like an LCSC code: "
                            f"jlc_get_part(lcsc=\"{mpn.strip().upper()}\") looks it up live, "
                            "including low or zero stock. " + hint)
            return {"error": f"No part found in the local snapshot for MPN '{mpn}'", "mpn": mpn, "results": [],
                    "hint": hint, "data_source": {"kind": "snapshot", "provider": "JLCPCB", "observed_at": db.scraped_at()},
                    "next_call": None if is_placeholder_mpn(mpn) else {
                        "tool": "jlc_stock_check", "arguments": {"query": mpn, "min_stock": 0, "limit": 10}},
                    "availability": "unknown_outside_snapshot"}
        reply = {
            "mpn": mpn,
            "data_as_of": db.scraped_at(),
            "prices_as_of": db.prices_as_of(),
            "price_tiers_as_of": db.price_tiers_as_of(),
            "total": len(results),
            **_match_flags(results, match_info),
            "results": _with_stored_lifecycle(results),
            **_public(match_info),
        }
        if note := _subcategory_note(results):  # after the match's own note (related parts), never instead
            reply["note"] = " ".join(filter(None, [reply.get("note"), note]))
        if gone:  # gone parts numbered so too: counted only, the reply is about the parts in stock
            reply["gone_matches"] = len(gone)
        return reply

    # LCSC code: the daily snapshot answers, unless live=true, the snapshot doesn't list the part (it
    # left, or is new or unknown) or the server has no price tiers (the snapshot's prices would be the
    # 1-piece price alone); then JLCPCB does, and the database's row if JLCPCB doesn't answer
    if not _client:
        raise RuntimeError("Client not initialized")
    code = lcsc.strip().upper()
    if not LCSC_CODE.fullmatch(code):  # no request, as get_part() makes none for it
        return {"error": f"Part {lcsc} not found"}
    if not live and (reply := await _part_from_database(code)) is not None:
        stats.count_lcsc_lookup("jlc_get_part", "snapshot")
        return _with_stored_lifecycle([reply])[0]

    try:
        result = await _client.get_part(lcsc)
    except JLCPCBUnavailable as e:  # JLCPCB didn't answer (rate limited / WAF / timeout ...): its message
        if (reply := await _part_from_database(code, live_error=str(e))) is not None:
            stats.count_lcsc_lookup("jlc_get_part", "fallback")
            return _with_stored_lifecycle([reply])[0]
        stats.count_lcsc_lookup("jlc_get_part", "live_failed")
        return {"error": str(e)}
    except ValueError as e:  # JLCPCB answered, but its reply couldn't be read: the error, as before 0.10.2
        logger.exception(f"jlc_get_part({code}): JLCPCB's reply couldn't be read")
        stats.count_lcsc_lookup("jlc_get_part", "live_failed")
        return {"error": str(e)}
    except Exception:  # raised as before (FastMCP logs it); still one lookup counted
        stats.count_lcsc_lookup("jlc_get_part", "live_failed")
        raise
    stats.count_lcsc_lookup("jlc_get_part", "live")
    if not result:
        return {"error": f"Part {lcsc} not found"}
    result = _short_datasheet_link(result)
    if note := _subcategory_note([result]):
        result = {**result, "note": note}
    return _with_stored_lifecycle([result])[0]


def _with_stored_lifecycle(parts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach each catalog part's best known status, with one store read per distinct MPN.
    Synchronous like LifecycleLookup's store reads; jlc_get_parts calls this once in its existing
    database job. Never asks a distributor or changes a cached part's row."""
    if _distributor_store is None:
        return parts
    readings: dict[str, list[Reading]] = {}
    enriched = []
    for part in parts:
        mpn, maker = part.get("model"), part.get("manufacturer")
        if part.get("error") or not part.get("lcsc") or not mpn or not maker:
            enriched.append(part)
            continue
        key = mpn_key(mpn)
        if key not in readings:
            readings[key] = _distributor_store.readings(mpn)
        best = min((r for r in readings[key] if r.found and r.status != "unknown" and makers_match(r.maker, maker)),
                   key=Reading.rank, default=None)
        if best is not None:
            part = {**part, "lifecycle": {"status": best.status, "raw": best.raw, "source": best.source,
                                         "observed_at": utc_text(best.observed_at)}}
        enriched.append(part)
    return enriched


# Once on jlc_get_part(lcsc)'s snapshot reply: where it's from, and what live=true adds
_SNAPSHOT_HINT = ("From the daily snapshot (stock >= 10) of data_as_of. live=true gives live stock, plus min_order, "
                  "reel_qty, the datasheet page, maker_datasheet and lcsc_url, and checks an unknown (null) "
                  "EasyEDA footprint.")
_NO_SPECS_IN_SNAPSHOT = ("JLCPCB lists no specs for this part, so searches with spec filters leave it out; "
                         "live=true adds LCSC's where it has them.")


def _snapshot_date(data_as_of: str | None) -> str:
    """The snapshot's date for a note ("2026-11-19"), or "unknown date" without one."""
    return data_as_of[:10] if data_as_of else "unknown date"


def _live_failed_note(part: dict[str, Any], data_as_of: str | None) -> str:
    """What a reply the database gave in place of a failed live lookup is (live_failed)."""
    if part.get("gone"):
        return (f"JLCPCB didn't answer, so this is what the daily snapshot of {_snapshot_date(data_as_of)} kept: "
                f"the part left it on {part.get('gone_since')} (stock under 10, or no longer listed), so stock is "
                "null (unknown) and last_stock is from the last scrape that listed it. Try live again later.")
    return (f"JLCPCB didn't answer, so this is the daily snapshot of {_snapshot_date(data_as_of)} (stock >= 10 "
            "then). Try live again later.")


async def _part_from_database(code: str, live_error: str | None = None) -> dict[str, Any] | None:
    """jlc_get_part(lcsc=code)'s reply from the database alone, with no request of any kind: the
    snapshot's part with the live reply's field names for what the snapshot has (every price
    break in prices when loaded, this server's datasheet_pdf link unless JLCPCB lists no
    datasheet, the footprint where it's already known: ComponentDatabase.get_part_snapshot,
    JLCPCBClient.known_footprint), data_as_of, prices_as_of, price_tiers_as_of and _SNAPSHOT_HINT.
    With live_error (the live lookup failed): marked live_failed, with that error and a note
    instead of the hint, and a part kept after it left the snapshot (gone) answers too. None when
    the database has neither, or can't be read; without live_error also when the database has no
    price tiers (price_tiers_as_of None), so the live reply gives every tier, as before 0.10.2."""
    db, client = get_db(), _client

    def read() -> tuple[Any, ...]:
        if live_error is None and db.price_tiers_as_of() is None:
            return None, None, None, None, None
        part = db.get_part_snapshot(code, gone=live_error is not None)
        seed = client.footprint_seed(code) if part is not None and not part.get("gone") else None
        return part, seed, db.scraped_at(), db.prices_as_of(), db.price_tiers_as_of()

    try:
        part, seed, data_as_of, prices_as_of, tiers_as_of = await run_db(COMPONENT_POOL, read)
    except (OSError, sqlite3.Error):
        logger.exception("jlc_get_part: snapshot lookup failed")
        return None
    if part is None:
        return None
    reply = dict(part)
    if not reply.get("gone"):
        if not reply.get("specs") and "specs_note" not in reply:
            reply["specs_note"] = _NO_SPECS_IN_SNAPSHOT
        # The live reply's short link, which signs JLCPCB's PDF when visited; none for a part
        # JLCPCB lists no datasheet for (no_datasheet), where the link would find nothing
        if not reply.get("no_datasheet") and (base := _datasheet_link_base()):
            reply["datasheet_pdf"] = f"{base}/mcp/datasheet/{code}"
        reply.update(await client.known_footprint(code, seed))
    reply.update(data_as_of=data_as_of, prices_as_of=prices_as_of, price_tiers_as_of=tiers_as_of)
    notes = [_subcategory_note([reply])]
    if live_error is None:
        reply["hint"] = _SNAPSHOT_HINT
    else:
        reply.update(live_failed=True, live_error=live_error)
        notes.append(_live_failed_note(reply, data_as_of))
    if note := " ".join(filter(None, notes)):
        reply["note"] = note
    return reply


# What a gone row is, once per jlc_get_part(mpn) or jlc_get_parts reply that has one
_GONE_HINT = ("gone parts left the daily snapshot (stock >= 10) on gone_since: their stock fell under 10 or JLCPCB "
              "stopped listing them, so stock is null (unknown); last_stock is from the last scrape that listed "
              "them, and price the last 1-piece price the snapshot had for them (refreshed weekly). "
              "jlc_get_part(lcsc=...) checks one live.")


def _public(info: dict[str, Any]) -> dict[str, Any]:
    """Match info as a reply gives it: without get_by_mpn's private keys (db.lookup.VIA)."""
    return {key: value for key, value in info.items() if not key.startswith("_")}


def _mpn_answer(mpn: str, in_stock: list[dict[str, Any]], in_info: dict[str, Any], gone: list[dict[str, Any]],
                gone_info: dict[str, Any]) -> tuple[str, list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    """How an MPN lookup answers, as (kind, parts listed, match info, parts that match it):
    "found": in-stock parts match (their match info; gone ones are only counted). "gone": parts
    numbered so left the snapshot and none in stock matches but by full text (related, or an
    alternative the full text found), or the gone part has the number itself and the only parts in
    stock are another maker's spelled with other separators (Molex's 2081001 gone, TE's 208100-1 in
    stock): the gone ones first, the in-stock ones after them, which the note describes. "none": neither."""
    full_text = in_info.get("match") == "related" or in_info.get(VIA) == "related"
    other_makers_spelling = (in_info.get("match") == "separators" and "match" not in gone_info and not any(
        makers_match(part.get("manufacturer"), kept.get("manufacturer")) for part in in_stock for kept in gone))
    if in_stock and not (gone and (full_text or other_makers_spelling)):
        return "found", in_stock, in_info, in_stock
    if not gone:
        return "none", [], {}, []
    info = dict(gone_info)
    if in_stock and full_text:
        start = in_info["matched_mpn"] if in_info.get("match") == "alternative" else mpn.strip()
        lead = (f"'{mpn.strip()}' itself left the snapshot (the gone parts, listed first); the parts after it "
                f"are in stock, and their part numbers start with '{start}' or their text mentions it, so check "
                "the package and manufacturer.")
        info["note"] = " ".join(filter(None, [info.get("note"), related_note(in_stock, lead)]))
    elif in_stock:
        makers = ", ".join(dict.fromkeys(part["manufacturer"] or "an unnamed maker" for part in in_stock[:3]))
        info["note"] = " ".join(filter(None, [info.get("note"), (
            f"'{mpn.strip()}' itself left the snapshot (the gone parts, listed first); the parts after it are "
            f"in stock from another maker ({makers}), numbered the same apart from separators "
            f"('{in_info.get('matched_mpn')}'), so check they're the same part before substituting.")]))
    return "gone", [*gone, *in_stock], info, gone


def _match_flags(results: list[dict[str, Any]], match_info: dict[str, Any]) -> dict[str, bool]:
    """An MPN lookup's exact and ambiguous. exact: the number itself matched (ignoring case), not a
    separator, packing, alias, alternative, LCSC-code or full-text recovery (those set
    match_info["match"]). ambiguous: several parts (LCSC codes) match, so picking one needs the
    manufacturer or package."""
    return {"exact": "match" not in match_info, "ambiguous": len(results) > 1}


# Once per jlc_get_parts reply rather than on each of up to 50 rows
_GET_PARTS_NOT_FOUND_HINT = (
    "not_found parts aren't in the daily snapshot, which lists in-stock parts only (stock >= 10): "
    "jlc_get_part(lcsc=...) looks a code up live, and jlc_stock_check(query=...) finds low or zero stock. "
    "Part numbers match only as themselves (or with other separators, packing codes or aliases), never by "
    "their text: for a value such as 10k or 100nF, jlc_search finds parts.")

# The fields of each part an MPN row lists (up to 10 per line, so 50 lines stay small); a part's
# description and category are in its LCSC code's row or jlc_get_part
_PARTS_MATCH_KEYS = ("lcsc", "model", "manufacturer", "package", "stock", "price", "prices", "library_type",
                     "preferred", "gone", "gone_since", "last_stock", "lifecycle")

# MPN lookups: (in-stock parts, their match info, gone parts, their match info)
PartsLookup = tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]], dict[str, Any]]


def _parts_lookup(db: Any, mpn: str, maker: str | None, cache: dict[tuple[str, str | None], PartsLookup]) -> PartsLookup:
    """An MPN's sure matches for jlc_get_parts (no full-text guesses), in stock and gone, for the
    maker given (None: any), each (number, maker) looked up once a call. The maker narrows every
    match step, so another maker's exact number doesn't hide this maker's other spelling."""
    key = (mpn, maker.casefold() if maker else None)
    if key not in cache:
        keep = (lambda name: makers_match(name, maker)) if maker else None
        info: dict[str, Any] = {}
        gone_info: dict[str, Any] = {}
        found = db.get_by_mpn(mpn, match_info=info, full_text=False, maker=keep)
        gone = db.get_sold_out_by_mpn(mpn, match_info=gone_info, maker=keep)
        cache[key] = (found, info, gone, gone_info)
    return cache[key]


def _parts_mpn_matches(db: Any, mpn: str, part: dict[str, Any],
                       cache: dict[tuple[str, str | None], PartsLookup]) -> bool:
    """Check a BOM's number against its code using the catalog's spelling/packing/alias rules.
    Compare packing identities first: an exact listing of another packing variant can hide this
    code in get_by_mpn's earlier match tiers."""
    key = mpn_key(part.get("model") or "")
    if key and key in {mpn_key(value) for value in normalize_mpn(mpn)}:
        return True
    for rule in PACKING_RULES:
        if not any(makers_match(part.get("manufacturer"), maker) for maker in rule.manufacturers):
            continue
        asked, listed = rule.pattern.fullmatch(mpn_key(mpn)), rule.pattern.fullmatch(key)
        if asked and listed and rule.identity(asked) == rule.identity(listed):
            return True
    found, _, gone, _ = _parts_lookup(db, mpn, part.get("manufacturer"), cache)
    return any(row["lcsc"] == part["lcsc"] for row in [*found, *gone])


def _get_parts_mpn_row(mpn: str, answer: tuple[str, list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]],
                       everyone: list[dict[str, Any]] | None, gone: list[dict[str, Any]],
                       rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """An MPN's jlc_get_parts row, shaped like jlc_get_part(mpn)'s reply. answer is _mpn_answer's for
    the maker given (if any): the first GET_PARTS_MAX_MATCHES listed are shown, with
    _PARTS_MATCH_KEYS only, and total counts all. everyone: the in-stock parts of every maker, when
    the maker given has none in stock (their makers are other_manufacturers); gone the gone matches
    (counted in gone_matches when in-stock parts answer)."""
    kind, listed, info, matched = answer
    row: dict[str, Any] = {"mpn": mpn, "total": len(listed)}
    # Other makers list the number in stock
    others = list(dict.fromkeys(p["manufacturer"] for p in everyone or []))[:GET_PARTS_MAX_MATCHES]
    if kind == "none":
        row.update(results=[], not_found=True)
        if others:
            row["other_manufacturers"] = others
        return row
    row.update(_match_flags(matched, info))
    row["results"] = [{key: rows[p["lcsc"]][key] for key in _PARTS_MATCH_KEYS if key in rows[p["lcsc"]]}
                      for p in listed[:GET_PARTS_MAX_MATCHES] if p["lcsc"] in rows]
    row.update(_public(info))
    if kind == "found" and gone:
        row["gone_matches"] = len(gone)
    elif kind == "gone" and others and len(listed) == len(matched):
        row["other_manufacturers"] = others  # gone for the maker given; others list it in stock
    return row


def _code_as_mpn_note(code: str) -> str:
    return (f"'{code}' isn't an LCSC code in the snapshot or among the parts that left it, so it was "
            "looked up as a part number.")


# One BOM line in jlc_get_parts / part_lifecycle: a string or an object. Validated as Any, so a bad
# row still gets its own error, but published with typed items: some clients (Gemini) reject an
# array whose items schema has no type, which would fail every tool in the session.
PartsItem = Annotated[Any, WithJsonSchema({"anyOf": [{"type": "string"},
                                                     {"type": "object", "additionalProperties": True}]})]


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Parts (BOM, Daily Snapshot)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
@offload(COMPONENT_POOL)
def jlc_get_parts(parts: list[PartsItem] | dict[str, Any] | str) -> dict:
    """BOM refreshes: up to 50 JLCPCB parts from the daily snapshot, no live requests.
    MPNs never match by full text; search values with jlc_search. For specs or live stock,
    use jlc_get_part (live=true for live stock).

    Args:
        parts: Codes/MPNs or {"mpn","manufacturer","lcsc"}; list/JSON array/string, max 50; lcsc wins; use {"mpn":"C1815"} for code-shaped MPNs.
    """
    items: Any = parts
    if isinstance(items, str) and items.lstrip().startswith(("[", "{")):
        try:
            items = _loads_argument(items, check_text=False)  # unencodable text: that row's error
        except json.JSONDecodeError:  # nested past Python's limit too: not a parts list either
            return _argument_error("parts", ValueError("not a valid JSON array"),
                                   ["LCSC code", "MPN", '{"mpn", "manufacturer"}', "list or JSON array of these"])
    if not isinstance(items, list):
        items = [items]
    stats.note(batch_items=items[:50], batch_count=len(items))
    if not items:
        return {"error": 'Give at least one part: an MPN, an LCSC code or {"mpn": ..., "manufacturer": ...}'}
    if error := _check_list_cap("parts", items, GET_PARTS_MAX_ITEMS):
        return error

    # Inputs read as part_lifecycle reads them; a valid LCSC code wins over an MPN given with it
    entries = [_lifecycle_entry(item) for item in items]
    db = get_db()
    cache: dict[tuple[str, str | None], PartsLookup] = {}

    def answer(mpn: str, maker: str | None) -> tuple[Any, ...] | None:
        """(_mpn_answer for the maker given, its gone matches, every maker's in-stock parts when the
        maker given has none), or None when the database failed on this number alone."""
        try:
            mine, mine_info, gone, gone_info = _parts_lookup(db, mpn, maker, cache)
            result = _mpn_answer(mpn, mine, mine_info, gone, gone_info)
            everyone = _parts_lookup(db, mpn, None, cache)[0] if maker and not mine else None
        except sqlite3.Error:
            logger.exception("jlc_get_parts: lookup failed for one part number")
            return None
        return result, gone, everyone

    def rows_for(codes: list[str], gone_codes: list[str]) -> dict[str, dict[str, Any]]:
        rows = db.get_snapshot_rows(codes) if codes else {}
        # LCSC codes the snapshot doesn't list may be gone; one more read only when there are any
        gone_codes = [*gone_codes, *(code for code, part in rows.items() if part is None)]
        gone_rows = db.get_sold_out_rows(gone_codes) if gone_codes else {}
        return {code: part for code, part in [*gone_rows.items(), *rows.items()] if part}  # never both

    def listed_codes(result: tuple[Any, ...] | None, codes: list[str], gone_codes: list[str]) -> None:
        for part in result[0][1][:GET_PARTS_MAX_MATCHES] if result else ():
            (gone_codes if part.get("gone") else codes).append(part["lcsc"])

    try:
        answers: list[tuple[Any, ...] | None] = []  # per MPN entry: answer(); None for code entries
        codes: list[str] = []
        gone_codes: list[str] = []
        for entry in entries:
            result = None
            if entry.error is None and entry.lcsc:
                codes.append(entry.lcsc)
            elif entry.error is None and entry.mpn:
                result = answer(entry.mpn, entry.maker)
                listed_codes(result, codes, gone_codes)
            answers.append(result)
        listed = rows_for(codes, gone_codes)
        # A plain code string neither lists may be a part number (2SC945 is sold as "C945"): asked as
        # one. A database failure on that lookup is the row's error, as for an MPN given.
        as_mpn: dict[int, tuple[Any, ...]] = {}
        retry_failed: set[int] = set()
        codes, gone_codes = [], []
        for index, entry in enumerate(entries):
            if (entry.error is None and entry.lcsc and not entry.mpn and isinstance(entry.input, str)
                    and entry.lcsc not in listed):
                result = answer(entry.lcsc, None)
                if result is None:
                    retry_failed.add(index)
                elif result[0][0] != "none":
                    as_mpn[index] = result
                    listed_codes(result, codes, gone_codes)
        if codes or gone_codes:
            listed.update(rows_for(codes, gone_codes))
        listed = {part["lcsc"]: part for part in _with_stored_lifecycle(list(listed.values()))}
        mismatches = {}
        for index, entry in enumerate(entries):
            if entry.error is not None or not entry.lcsc or not (part := listed.get(entry.lcsc)):
                continue
            mismatch = {}
            if entry.mpn and not _parts_mpn_matches(db, entry.mpn, part, cache):
                mismatch["mpn"] = entry.mpn
            if entry.maker and not makers_match(entry.maker, part.get("manufacturer")):
                mismatch["manufacturer"] = entry.maker
            if mismatch:
                mismatches[index] = mismatch
        data_as_of, prices_as_of, tiers_as_of = db.scraped_at(), db.prices_as_of(), db.price_tiers_as_of()
    except (OSError, sqlite3.Error):
        logger.exception("jlc_get_parts: catalog lookup failed")
        return {"error": "Database not available"}

    # found: in the snapshot (stock >= 10); gone: answered from the parts kept after they left it
    counts = {"found": 0, "gone": 0, "not_found": 0, "error": 0}
    results = []
    for index, (entry, result) in enumerate(zip(entries, answers)):
        row: dict[str, Any] = {"input": entry.input}
        if index in as_mpn:
            result = as_mpn[index]
            row.update(_get_parts_mpn_row(entry.lcsc, result[0], result[2], result[1], listed))
            row["note"] = " ".join(filter(None, [row.get("note"), _code_as_mpn_note(entry.lcsc)]))
            counts[result[0][0]] += 1
        elif entry.error is not None:
            # not_sent (a placeholder's) is part_lifecycle's: no distributor request is made here
            row.update((key, value) for key, value in entry.error.items() if key != "not_sent")
            counts["error"] += 1
        elif index in retry_failed:
            row["error"] = "Database not available"
            counts["error"] += 1
        elif entry.lcsc:
            part = listed.get(entry.lcsc)
            row.update(part or {"lcsc": entry.lcsc, "not_found": True})
            if part and not part.get("gone") and not part.get("no_datasheet") and (base := _datasheet_link_base()):
                row["datasheet_pdf"] = f"{base}/mcp/datasheet/{entry.lcsc}"
            if index in mismatches:
                row["mismatch"] = mismatches[index]
                row["note"] = " ".join(filter(None, [row.get("note"),
                    "Check this BOM row: the given MPN or manufacturer disagrees with the LCSC code's part."]))
            counts["not_found" if not part else "gone" if part.get("gone") else "found"] += 1
        elif result is None:  # the database failed on this number; the others are answered
            row["error"] = "Database not available"
            counts["error"] += 1
        else:
            (kind, *_), gone, everyone = result
            row.update(_get_parts_mpn_row(entry.mpn, result[0], everyone, gone, listed))
            counts["not_found" if kind == "none" else kind] += 1
        results.append(row)
    reply: dict[str, Any] = {"data_as_of": data_as_of, "prices_as_of": prices_as_of,
                             "price_tiers_as_of": tiers_as_of, "total": len(results),
                             "counts": counts, "results": results}
    hints = [_GONE_HINT] if counts["gone"] else []
    if counts["not_found"]:
        hints.append(_GET_PARTS_NOT_FOUND_HINT)
    if hints:
        reply["hint"] = " ".join(hints)
    return reply


def _datasheet_link_base() -> str | None:
    """This server's public address inside a tool call, for short datasheet links: https for the
    allowlisted public hosts (TLS ends at the proxy, as ALLOWED_ORIGINS assumes), unless configured
    explicitly. None in direct mode, outside an HTTP request, or with a malformed Host."""
    try:
        request = get_http_request()
    except RuntimeError:
        return None
    if DATASHEET_LINK_BASE == "direct":
        return None
    if DATASHEET_LINK_BASE:
        return DATASHEET_LINK_BASE
    host = request.headers.get("host")
    if not host:
        return None
    # Host matching alone can accept userinfo such as pcbparts.dev:80@attacker.example.
    # Validate the entire authority before interpolating it into a client-facing URL.
    authority = re.fullmatch(r"(\[[0-9A-Fa-f:.]+\]|[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.?)(?::([0-9]+))?", host)
    if authority is None:
        return None
    hostname, port = authority.groups()
    try:
        if port is not None and not 1 <= int(port) <= 65535:
            return None
        if hostname.startswith("["):
            ipaddress.IPv6Address(hostname[1:-1])
        elif any(label.startswith("-") or label.endswith("-") for label in hostname.rstrip(".").split(".")):
            return None
    except ValueError:
        return None
    return f"{'https' if hostname in ALLOWED_HOSTS else request.url.scheme}://{host}"


def _short_datasheet_link(part: dict[str, Any]) -> dict[str, Any]:
    """A part reply whose datasheet_pdf is this server's /mcp/datasheet/<lcsc>, which signs a fresh
    JLCPCB link on each visit. The signed link was ~1.2KB of a 3.3KB reply and expired in 30 minutes.
    In direct mode or without an HTTP request the signed link and datasheet_pdf_expires stay. LCSC's copy (no
    expiry; JLCPCB has none to sign) is returned as it is."""
    if (not part.get("datasheet_pdf") or not part.get("datasheet_pdf_expires") or not part.get("lcsc")
            or not (base := _datasheet_link_base())):
        return part
    short = {**part, "datasheet_pdf": f"{base}/mcp/datasheet/{part['lcsc']}"}
    short.pop("datasheet_pdf_expires", None)
    return short


# Attributes LCSC gets wrong for a whole part type, often enough to warn about
_SUBCATEGORY_NOTES = {
    "2G/3G/4G/5G Modules": (
        "Communication Frequency and Communication System come from LCSC and are often incomplete: both the "
        "SIM7080G and the Cat-M-only SIM7080G-M list bands B1-B3 and NB-IoT, where SIMCom's datasheet lists 18 "
        "Cat-M bands. Check bands and network modes in the datasheet (datasheet_pdf in jlc_get_part)."),
}


def _subcategory_note(parts: list[dict[str, Any]] | None) -> str | None:
    """The warning for the listed parts' part types, if any (cellular modules' band lists)."""
    notes = dict.fromkeys(_SUBCATEGORY_NOTES[p["subcategory"]] for p in parts or []
                          if isinstance(p, dict) and p.get("subcategory") in _SUBCATEGORY_NOTES)
    return " ".join(notes) or None



@mcp.tool(
    annotations=ToolAnnotations(
        title="Find Alternative Parts",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
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
    land_compatible: bool = False,
) -> dict:
    """Catalog-checked replacements, no-fee first; unverified candidates need manual comparison.
    Check pinout/circuit; lifecycle isn't checked (part_lifecycle). Stock is live or snapshot.
    Savings use a $3 Economic loading-fee estimate, not a quote. Land checks don't verify pin functions.

    Args:
        lcsc: Original LCSC code, e.g. "C2557".
        min_stock: Minimum stock; default 10.
        same_package: Require same package; default false.
        library_type: basic, preferred, no_fee (both), extended, all; default all.
        has_easyeda_footprint: True/false filter; default null; checks min(2*limit,15) candidates (≤5 live), excludes unknowns.
        limit: Results per verified/unverified list; default 10, max 50.
        board_quantity: Boards for savings; default 1, max 1000000.
        placements_per_board: Placements per board; default 1, max 1000000.
        land_compatible: Compare top 30 candidates' pads for existing copper; default false; adds seconds, cached.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    if library_type is not None:
        library_type = _normalize_library_type(library_type)
        if library_type not in ("basic", "preferred", "no_fee", "extended", "all"):
            return {"error": f"Unsupported library_type: '{library_type}'",
                    "valid_values": ["basic", "preferred", "no_fee", "extended", "all"]}

    try:
        result = await _client.find_alternatives(
            lcsc=lcsc,
            min_stock=min_stock,
            same_package=same_package,
            library_type=library_type if library_type != "all" else None,
            has_easyeda_footprint=has_easyeda_footprint,
            limit=clamp_limit(limit, MAX_ALTERNATIVES),
            board_quantity=board_quantity,
            placements_per_board=placements_per_board,
            land_compatible=land_compatible,
        )
    except ValueError as e:  # actionable JLCPCB messages (rate limited / WAF / timeout)
        return {"error": str(e)}
    if isinstance(result.get("original"), dict):
        result = {**result, "original": _short_datasheet_link(result["original"])}
    return result


def _easyeda_unknown_error(lcsc: str) -> dict[str, str]:
    """Footprint status unknown, not absent: the EasyEDA lookup failed or is paused by its rate limit."""
    return {"error": f"Couldn't check EasyEDA for {lcsc}'s symbol right now (lookup failed or "
                     "EasyEDA is rate-limiting). Try again in a few minutes."}


# Pin names EasyEDA symbols give the two ends of a diode, LED, buzzer or battery holder
# (A/K on BAS316 C109218, C/A on IR333C-A C5130, -/+ on MHP3528IRCT-D C405277)
_ANODE_PIN_NAMES = frozenset({"A", "ANODE", "+"})
_CATHODE_PIN_NAMES = frozenset({"K", "C", "CATHODE", "-", "−"})
# Of 7 well-stocked diodes and LEDs, 3 symbols put the anode on pin 1 (BAS316 C109218, B5819WS
# C7420331, KT-0603R C2286) and 4 the cathode (1N4148WS C2128, SS34 C8678, XL-1608SURC-06 C965799,
# BZT52C5V6 C19077402). Nexperia's BAS316 datasheet has the cathode on pin 1. Each footprint's
# polarity mark sat on the pad its symbol names K, so EasyEDA's own pair agrees; mixing its numbers
# with a datasheet's or another library's footprint puts the part in backwards.
_POLARIZED_PAIR_NOTE = (
    "These pin numbers are EasyEDA's and match its footprint's pads, but polarized two-pin parts have "
    "no standard numbering: EasyEDA puts the anode or + on pin 1 for some parts and the cathode or - "
    "for others, and the maker's datasheet or another library's footprint may number them the other "
    "way. Connect the part by pin name, not number.")


def _is_polarized_pair(pins: list[dict[str, Any]]) -> bool:
    """Two pins, one named for the anode or + end and the other for the cathode or - end."""
    if len(pins) != 2:
        return False
    first, second = (str(p.get("name") or "").strip().upper() for p in pins)
    return ((first in _ANODE_PIN_NAMES and second in _CATHODE_PIN_NAMES)
            or (first in _CATHODE_PIN_NAMES and second in _ANODE_PIN_NAMES))


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Component Pinout",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def jlc_get_pinout(lcsc: str | None = None, uuid: str | None = None, footprint: bool = False) -> dict:
    """EasyEDA symbol pins. Numbers match footprint pads, which may differ from datasheet numbering;
    connect polarized two-pin parts by name. Absent electrical means unknown.
    KiCad files: cse_get_kicad.

    Args:
        lcsc: LCSC code, e.g. "C8304"; wins over uuid.
        uuid: EasyEDA symbol UUID instead of lcsc.
        footprint: Also return footprint and pads (mm from origin, y down); needs lcsc; default false.
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
    if all(p["name"] == p["number"] for p in pins):
        result["note"] = ("The symbol names its pins only by number, so it doesn't say what each pin does "
                          "(e.g. a jack's tip, ring and sleeve); check the datasheet's pin table.")
        if (part or {}).get("subcategory") == "Audio Connectors":
            # PJ-313D from SHOU HAN (C668608) and Hroparts (C95463): same footprint, tip and ring swapped
            result["note"] += (" Jacks with the same footprint from different makers can number the tip, "
                               "ring and sleeve pads differently, so check this part's own datasheet.")
        if not footprint:
            # A client that loaded the tool list before footprint existed (0.8.4) can't send it until it reconnects
            result["note"] += (" footprint=true adds the pad positions to match against its drawing (if your "
                               "jlc_get_pinout has no footprint argument, reconnect to the server to load it).")
    elif _is_polarized_pair(pins):
        result["note"] = _POLARIZED_PAIR_NOTE

    if footprint:
        footprint_uuid = (part or {}).get("easyeda_footprint_uuid")
        if not footprint_uuid:
            result["footprint_error"] = ("Give lcsc to get the footprint" if not lcsc
                                         else f"No EasyEDA footprint UUID for {lcsc}")
        else:
            try:
                parsed_footprint = parse_easyeda_footprint(await _client.get_easyeda_component(footprint_uuid))
            except ValueError as e:
                result["footprint_error"] = str(e)
            else:
                if parsed_footprint:
                    result["footprint"] = parsed_footprint
                else:
                    result["footprint_error"] = f"The EasyEDA footprint {footprint_uuid} has no pads"
    return result



def _redact(message: str, *secrets: str) -> str:
    """Distributor error text goes back to anonymous callers: blank out our credentials (every
    Mouser key and DigiKey app) in case the API ever echoes them."""
    credentials = {MOUSER_API_KEY, *MOUSER_EXTRA_API_KEYS,
                   DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET, DIGIKEY_CLIENT_ID_2, DIGIKEY_CLIENT_SECRET_2}
    for secret in sorted(set(secrets) | credentials, key=len, reverse=True):
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
    """Mouser stock/prices/datasheets: for parts JLCPCB doesn't carry or when the user asks for Mouser.
    Lookups share a small daily limit across all users: batch up to 10 full part numbers; don't retry
    a quota error. Answers cached up to 3 days. Check manufacturer on loose matches.
    For lifecycle use part_lifecycle; Mouser's unstated status doesn't establish absence of NRND.

    Args:
        part_number: Mouser PN/MPN, 3-40 chars each; up to 10 joined by "|", e.g. "595-LM358P|NE555P".
    """
    if not _mouser_client:
        return {"error": "Mouser API key not configured. Set MOUSER_API_KEY in environment."}
    if part_number and len(part_number) > 500:
        return {"error": "Part number too long (max 500 characters)"}

    try:
        return await _mouser_client.get_part(part_number, caller=_caller_ip())
    except (MouserError, MouserAPIError) as e:  # our own message or Mouser's
        message = _redact(str(e))  # every key, in the log as in the reply
        logger.error(f"Mouser part lookup failed: {type(e).__name__}: {message}")
        return {"error": f"Mouser part lookup failed: {message}"}
    except Exception as e:
        logger.error(f"Mouser part lookup failed: {type(e).__name__}: {_redact(str(e))}")
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
async def digikey_get_part(part_number: str) -> dict:
    """API-based DigiKey stock/prices/datasheets: for parts JLCPCB doesn't carry or when the user asks
    for DigiKey. Lookups share a small daily limit across all users: one part per call; don't retry
    a quota error. Answers cached up to a day. For lifecycle use part_lifecycle.

    Args:
        part_number: Full DigiKey PN/MPN, e.g. "296-1395-5-ND"; partial numbers can waste a request.
    """
    if not _digikey_client:
        return {"error": "DigiKey API credentials not configured. Set DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET in environment."}
    if part_number and len(part_number) > 500:
        return {"error": "Part number too long (max 500 characters)"}

    try:
        return await _digikey_client.get_part(part_number, caller=_caller_ip())
    except DigiKeyError as e:  # our own message (HTTP status) or DigiKey's OAuth error
        message = _redact(str(e))  # every app's credentials, in the log as in the reply
        logger.error(f"DigiKey part lookup failed: {type(e).__name__}: {message}")
        return {"error": f"DigiKey part lookup failed: {message}"}
    except Exception as e:
        logger.error(f"DigiKey part lookup failed: {type(e).__name__}: {_redact(str(e))}")
        return {"error": "DigiKey part lookup failed. Check server logs for details."}


# A NUL broke jlc_get_parts' whole batch (SQLite's full-text query); tabs and line breaks inside
# a number are pasting accidents, not part numbers
_CONTROL_CHARACTERS = {"error": "Invalid part: control characters (a NUL, tab or line break) can't be in a part "
                                 "number, maker or LCSC code"}
# An escaped lone surrogate ("\ud800") in a JSON array string becomes text that can't be encoded:
# SQLite raised UnicodeEncodeError and failed jlc_get_parts' whole batch
_UNENCODABLE = {"error": "Invalid part: unpaired surrogate escapes (such as \\ud800) aren't text and can't be in a "
                         "part number, maker or LCSC code"}
_ECHO_MAX = 100  # characters of an input echoed back (part_lifecycle and jlc_get_parts' input)


def _has_control_characters(text: str) -> bool:
    return any(unicodedata.category(c) == "Cc" for c in text)


def _echo_input(item: Any) -> Any:
    """An input as a reply's input echoes it: as given, except a string over 100 characters (its
    first 100 and "...") or anything else whose JSON is over 200 (the first 100 characters of that
    JSON and "...", as text), so a long or deeply nested input isn't sent back whole; text that
    can't be sent as UTF-8 (a lone surrogate) is written as its escapes."""
    if isinstance(item, str):
        return _sendable(item if len(item) <= _ECHO_MAX else item[:_ECHO_MAX] + "...")
    try:
        text = json.dumps(item, ensure_ascii=False)
    except (TypeError, ValueError, RecursionError):
        return "..."
    return _sendable(item if len(text) <= 2 * _ECHO_MAX else text[:_ECHO_MAX] + "...")


def _entry_problem(mpn: str | None, maker: str | None) -> dict[str, Any] | None:
    """Why an input's MPN or maker can't be looked up (the first problem found), or None."""
    if mpn and len(mpn) > 100:
        return {"error": "MPN too long (max 100 characters)"}
    if maker and len(maker) > 100:
        return {"error": "Manufacturer too long (max 100 characters)"}
    if any(value and not _encodable(value) for value in (mpn, maker)):
        return dict(_UNENCODABLE)
    if any(value and _has_control_characters(value) for value in (mpn, maker)):
        return dict(_CONTROL_CHARACTERS)
    if mpn and is_placeholder_mpn(mpn):
        return {"error": f"Invalid part: '{mpn}' is a BOM placeholder (not fitted or not chosen), not a part number",
                "not_sent": "placeholder"}
    return None


def _lifecycle_entry(item: Any) -> Entry:
    """One part_lifecycle or jlc_get_parts input as an Entry (input: _echo_input's), with its error
    if it can't be looked up. A malformed lcsc beside an MPN (a BOM's "N/A" in its LCSC column) is
    set aside, and the MPN looked up. Beside a valid LCSC code, which wins over the MPN in
    jlc_get_parts and supplies what isn't given in part_lifecycle, an MPN or maker that can't be
    looked up (a BOM's "N/A" in its MPN column, over 100 characters, control characters) is set
    aside the same way, not the row's error."""
    echo = _echo_input(item)
    if isinstance(item, str):
        text = item.strip()
        fields = (None, None, text) if re.fullmatch(r"[Cc][0-9]{1,12}", text) else (text, None, None)
    elif isinstance(item, dict) and all(isinstance(item.get(k), (str, type(None))) for k in ("mpn", "manufacturer", "lcsc")):
        fields = (item.get("mpn"), item.get("manufacturer"), item.get("lcsc"))
    else:
        return Entry(echo, error={"error": 'Invalid part: give an MPN, an LCSC code or {"mpn": ..., "manufacturer": ...}'})
    mpn, maker, lcsc = ((value or "").strip() or None for value in fields)
    if lcsc and not re.fullmatch(r"C[0-9]{1,12}", lcsc.upper()):
        if not mpn:
            return Entry(echo, error={"error": "lcsc must be an LCSC C-code (e.g., C6186), or give mpn instead"})
        lcsc = None
    if not mpn and not lcsc:
        return Entry(echo, error={"error": "Give a part number or an LCSC code"})
    if lcsc:
        mpn = None if _entry_problem(mpn, None) else mpn
        maker = None if _entry_problem(None, maker) else maker
    elif problem := _entry_problem(mpn, maker):
        return Entry(echo, error=problem)
    return Entry(echo, mpn=mpn, maker=maker, lcsc=lcsc.upper() if lcsc else None)


def _catalog_identities(codes: list[str]) -> dict[str, dict[str, Any] | None]:
    """part_lifecycle's MPN and maker for LCSC codes: the snapshot's part, or for a code it no longer
    lists, the part kept after it left (gone); None for a code neither has."""
    db = get_db()
    parts = db.get_by_lcsc_batch(codes)
    if missing := [code for code in codes if not parts.get(code)]:
        gone = db.get_sold_out_rows(missing)
        parts.update((code, gone[code]) for code in missing if gone.get(code))
    return parts


@mcp.tool(
    annotations=ToolAnnotations(
        title="Part Lifecycle (BOM)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def part_lifecycle(parts: list[PartsItem] | dict[str, Any] | str) -> dict:
    """Lifecycle check for up to 50 parts; use instead of distributor stock tools for NRND/obsolete status.
    Stored readings reused; unknown parts are looked up at Mouser and DigiKey, sharing daily limits
    across all users. MPNs never match by full text; supply manufacturer to disambiguate.

    Args:
        parts: MPNs, LCSC codes or {"mpn","manufacturer","lcsc"}; list/JSON array/string, max 50; codes resolve from snapshot.
    """
    if not _mouser_client and not _digikey_client:
        return {"error": "Mouser API key not configured, nor DigiKey API credentials. Set MOUSER_API_KEY, "
                         "or DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET, in environment."}
    items: Any = parts
    if isinstance(items, str) and items.lstrip().startswith(("[", "{")):
        try:
            items = _loads_argument(items, check_text=False)  # unencodable text: that row's error
        except json.JSONDecodeError:  # nested past Python's limit too: not a parts list either
            return _argument_error("parts", ValueError("not a valid JSON array"),
                                   ["MPN", "LCSC code", '{"mpn", "manufacturer"}', "list or JSON array of these"])
    if not isinstance(items, list):
        items = [items]
    stats.note(batch_items=items[:50], batch_count=len(items))
    if not items:
        return {"error": 'Give at least one part: an MPN, an LCSC code or {"mpn": ..., "manufacturer": ...}'}
    if error := _check_list_cap("parts", items, LIFECYCLE_MAX_PARTS):
        return error

    entries = [_lifecycle_entry(item) for item in items]
    for entry in entries:
        if entry.error is None:
            stats.count_lifecycle_input("lcsc_code" if entry.lcsc else
                                        "with_manufacturer" if entry.maker else "bare_number")
    # Beside a valid code, a given MPN no distributor lists (not_sent_reason: a value such as "10k",
    # an LCSC code, not 3-40 characters, not ASCII) or one Mouser can't take ("|", below) is set
    # aside for the catalog's; a usable one still wins over it
    for entry in entries:
        if entry.error is None and entry.lcsc and entry.mpn and ("|" in entry.mpn or not_sent_reason(entry.mpn)):
            entry.mpn = None
    codes = list(dict.fromkeys(e.lcsc for e in entries if e.error is None and e.lcsc and not (e.mpn and e.maker)))
    if codes:  # an LCSC code's MPN and maker from the catalog snapshot, or from a part kept after it left it
        try:
            catalog = await run_db(COMPONENT_POOL, _catalog_identities, codes)
        except Exception:
            logger.exception("part_lifecycle: catalog lookup failed")
            catalog = None
        for entry in entries:
            if entry.lcsc not in codes or entry.error is not None:
                continue
            part = catalog.get(entry.lcsc) if catalog is not None else None
            if catalog is None:
                entry.error = {"error": "Database not available"}
            elif not part:
                if not entry.mpn:
                    entry.error = {"error": f"Part {entry.lcsc} not found",
                                   "hint": "The catalog snapshot lists in-stock parts (stock >= 10) and parts that "
                                           "have left it since 2026-11-12, not this one: give its MPN and "
                                           "manufacturer instead."}
            else:
                entry.mpn = entry.mpn or part.get("model") or None
                entry.maker = entry.maker or part.get("manufacturer") or None
                if not entry.mpn:
                    entry.error = {"error": "Give a part number or an LCSC code"}

    for entry in entries:  # Mouser's batches join numbers with "|": one holding it would be several
        if entry.error is None and entry.mpn and "|" in entry.mpn:
            entry.error = {"error": "Invalid part: an MPN can't contain '|' (give each part on its own)"}

    store = _distributor_store or (_mouser_client or _digikey_client)._store
    results = await LifecycleLookup(store, _mouser_client, _digikey_client).answer(entries, caller=_caller_ip())
    counts = dict.fromkeys(STATUSES, 0)
    for result in results:
        counts[result["status"]] += 1
    reply: dict[str, Any] = {"results": results, "total": len(results), "status_counts": counts}
    if waits := [result["retry_after"] for result in results if "retry_after" in result]:
        reply["retry_after"] = min(waits)
    return reply


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
    """Find SamacSys ECAD/3D models; formats unconfirmed. Use cse_get_kicad for KiCad files.
    Slow (about 15 s, longer when busy; cached). Datasheets: jlc_get_part's datasheet_pdf;
    part search: jlc_search; EasyEDA availability: jlc_get_part (live=true if unknown).

    Args:
        query: MPN/keyword, e.g. "LM358P"; max 500 characters.
        limit: Results; default 5, range 1-10.
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
    manufacturer: str | None = None,
) -> dict:
    """Get SamacSys KiCad symbol/footprint text. Slow (search about 15 s, then download; cached).
    Uses the server's own SamacSys account; shared daily download limits apply.
    Datasheets: jlc_get_part's datasheet_pdf; EasyEDA availability: jlc_get_part (live=true if unknown).

    Args:
        query: MPN, e.g. "LM358P"; max 500 characters; default null; provide query or part_id.
        part_id: cse_part_id from cse_search; default null; nonzero ID wins, skips search.
        manufacturer: Maker filter for query; default null (any).
    """
    if not _cse_client:
        return {"error": "CSE client not initialized"}

    if not query and not part_id:
        return {"error": "Must provide either query or part_id"}
    if query and len(query) > 500:
        return {"error": "Query too long (max 500 characters)"}

    try:
        return await _cse_client.get_kicad(query=query, part_id=part_id, manufacturer=manufacturer)
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
    """Choose sensor ICs/modules by measurement, bus and driver support; use jlc_search to buy.
    Unknown measure/protocol/platform returns valid_values. Calculated CO2 is eco2, not co2;
    compensation inputs aren't measurements.

    Args:
        query: Name/maker/text, e.g. "BME280"; max 500 characters.
        measure: Up to 20 (AND), list/JSON array/string, e.g. temperature; imu alone: acceleration OR gyroscope OR magnetic_field; with others: all three.
        type: Technology, e.g. "tof", "ndir", "mems"; unknown gives no matches.
        protocol: Bus, e.g. i2c, spi, one_wire (1-wire); gpio includes analog/pwm/one_wire; digital includes gpio/pwm/one_wire.
        platform: Driver platform, e.g. arduino, esphome, zephyr.
        limit: Results; default 15, range 1-100.
    """
    # Handle JSON-string measure param from some MCP clients (filter non-string
    # elements — they bypass Pydantic and get .lower()'d in sensor_db.search)
    if isinstance(measure, str):
        try:
            parsed = _loads_argument(measure)
            if isinstance(parsed, list):
                measure = [m for m in parsed if isinstance(m, str)] or None
        except json.JSONDecodeError:
            pass
        except _UnencodableArgument as exc:  # echoed by the measure error, it couldn't be sent
            return _argument_error("measure", exc, ["string", "array of strings", "JSON array of strings"])

    if query and len(query) > 500:
        return {"error": "Query too long (max 500 characters)", "results": [], "total": 0}
    # A NUL or other control character reaches FTS5 and raised a generic tool failure
    if query and re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", query):
        return {"error": "Query contains invalid characters", "results": [], "total": 0}

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
    """PCB design rules for power, protection, interfaces, MCUs, layout and EMC.
    Empty topic lists files; narrow a topic matching more than three files to get their full text.

    Args:
        topic: Key/keyword, e.g. "power/ldo", "usb", "stm32g0"; default "" (index); max 500 characters.
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
    """Find reference boards: component for an IC's wiring, query for a function, tag to browse.
    Then board_get(slug, focus=IC) for pin-by-pin connections; 2+ boards add component consensus.
    Use jlc_search to buy parts, sensor_recommend to choose sensors.

    Args:
        query: Function/text, e.g. "motor driver"; max 500 characters.
        component: IC/part name, e.g. "DRV8825"; max 200 characters.
        tag: Tag(s), e.g. usb, motor-control; list/JSON array/string, AND, max 10; unknown returns valid_values.
        org: Organization, e.g. "Espressif"; max 200 characters.
        layers: PCB layer count, e.g. 4.
        limit: Results; default 10, range 1-50.
    """
    # Handle JSON-string tag param from some MCP clients
    if isinstance(tag, str):
        try:
            parsed = _loads_argument(tag)
            if isinstance(parsed, list):
                tag = parsed
        except json.JSONDecodeError:
            pass
        except _UnencodableArgument as exc:  # SQLite failed on it ("Board search failed")
            return _argument_error("tag", exc, ["string", "array of strings", "JSON array of strings"])

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
    """Reference board details; focus returns one part's pin neighborhood and cross-board consensus.
    Look up design-file part numbers with jlc_get_part or mouser_get_part.

    Args:
        slug: Slug from board_search; max 200 characters.
        focus: IC, ref or value words, e.g. "ESP32", "J1", "USB-C"; max 200 characters.
        include_bom: Include plain R/C/L too; default false.
        include_nets: Full netlist, positions and copper pours (can be 100 KB+); default false.
    """
    if not slug or len(slug) > 200:
        return {"error": "Invalid slug"}
    if focus and len(focus) > 200:
        return {"error": "Focus too long (max 200 characters)"}

    try:
        boards_db = get_boards_db()
        result = boards_db.get_board(slug, include_raw=include_nets, include_bom=include_bom, focus=focus)

        if result is None:
            reply: dict[str, Any] = {"error": f"Board '{slug[:50]}' not found"}
            suggestions = boards_db.suggest_slugs(slug)
            if suggestions:
                reply["did_you_mean"] = suggestions
            return reply

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


async def _cse_store_counts() -> dict[str, int] | None:
    """Stored CSE searches and KiCad parts, refreshed at most every HEALTH_STORE_COUNT_TTL. None
    with no usable store (memory only) or before startup."""
    global _cse_stored
    if _cse_client is None:
        return None
    counted_at, counts = _cse_stored
    now = time.monotonic()
    if now - counted_at >= HEALTH_STORE_COUNT_TTL:
        counts = await asyncio.to_thread(_cse_client.store_counts)
        _cse_stored = (now, counts)
    return counts


def _distributor_store_counts() -> dict[str, Any] | None:
    """Stored Mouser/DigiKey answers and lifecycle readings, refreshed at most every
    HEALTH_STORE_COUNT_TTL. None before startup."""
    global _distributor_stored
    if _distributor_store is None:
        return None
    counted_at, counts = _distributor_stored
    now = time.monotonic()
    if now - counted_at >= HEALTH_STORE_COUNT_TTL or counts is None:
        counts = _distributor_store.counts()
        _distributor_stored = (now, counts)
    return counts


def _snapshot_health() -> dict[str, Any]:
    """/health's snapshot: when the catalog snapshot was scraped, its age in hours (0.1) by
    _health_clock and whether that's over SNAPSHOT_STALE_HOURS; age and stale null without a
    readable time."""
    try:
        scraped = datetime.datetime.fromisoformat(_snapshot_as_of).timestamp()  # type: ignore[arg-type]
    except (TypeError, ValueError, OverflowError):
        return {"data_as_of": _snapshot_as_of, "age_hours": None, "stale": None}
    age = (_health_clock() - scraped) / 3600
    return {"data_as_of": _snapshot_as_of, "age_hours": round(age, 1), "stale": age > SNAPSHOT_STALE_HOURS}


def _distributor_quota_status() -> dict[str, Any]:
    """Current private quota detail, including DigiKey's pause when it has no daily quota."""
    reply = {name: quota.status() for name, quota in _distributor_quotas.items()}
    if "digikey" not in reply and _digikey_client is not None and (ext := _digikey_client.ext_status()):
        reply["digikey"] = {**ext, "resets_at": _utc_text(_next_utc_midnight(_health_clock()))}
    if "digikey" in reply and _digikey_client is not None and (ext_pause := _digikey_client.ext_pause()):
        reply["digikey"] = {**reply["digikey"], "ext": ext_pause}
    return reply


def _other_distributors_clause() -> str:
    """", or digikey_get_part for other distributors" when a DigiKey lookup spends no shared daily
    limit and could go out now for this caller; empty otherwise (a spent limit, or the caller's
    address having used its day, would only earn the caller its error: 14,000 refused
    digikey_get_part calls on 2026-11-19)."""
    try:
        if _digikey_client is not None and _digikey_client.can_answer_now(_caller_ip()):
            return ", or digikey_get_part for other distributors"
    except Exception:  # a hint must never fail a lookup
        logger.exception("Couldn't read DigiKey's state for a hint")
    return ""


# Health check endpoint
async def health(request):
    """The server's state. 503 (status "unhealthy") while a database pool has had jobs waiting and
    started none for DB_STUCK_WAIT_SECONDS: a worker is stuck and every database call queued behind
    it waits, so the container's healthcheck fails. A long queue that keeps moving stays healthy."""
    pressure = {**database_pressure.summary(), "unhealthy_after_seconds": DB_STUCK_WAIT_SECONDS}
    stuck = pressure["stalled_seconds"] >= DB_STUCK_WAIT_SECONDS
    reply = {
        "status": "unhealthy" if stuck else "healthy",
        "service": "pcbparts-mcp",
        "version": __version__,
        "easyeda_footprints": _easyeda_footprint_counts(),
        "cse_stored": await _cse_store_counts(),
        "distributor_stored": _distributor_store_counts(),
        "database_pressure": pressure,
        "platform_ranges": _platform_ranges_info,
        "price_tiers": _price_tiers_info,
        "snapshot": _snapshot_health(),
    }
    if stuck:
        reply["problem"] = (f"database jobs have waited {pressure['stalled_seconds']:.0f} s with none "
                            "starting (a stuck worker?); database tool calls wait until it moves")
    return JSONResponse(reply, status_code=503 if stuck else 200)


async def datasheet_redirect(request):
    """/mcp/datasheet/<lcsc> (jlc_get_part's datasheet_pdf): a redirect to the part's datasheet PDF
    on JLCPCB's storage, signed when asked, so the link never goes stale; when JLCPCB keeps none,
    to the maker's datasheet or LCSC's PDF, as the live reply gives (JLCPCBClient.datasheet_pdf_url).
    The target only ever comes from JLCPCB's or LCSC's listing for the code in the path."""
    lcsc = request.path_params["lcsc"].strip().upper()
    counted = bool(re.fullmatch(r"C[0-9]+", lcsc))
    if counted:
        stats.count_datasheet_link("visits")
    if not _client:
        return JSONResponse({"error": "Server is starting; try again in a moment"}, status_code=503)
    try:
        url = await _client.datasheet_pdf_url(lcsc)
    except DatasheetLinkBusy as e:
        if counted:
            stats.count_datasheet_link("refused")
        # The per-IP limiter's 429 fields (llms.txt), with this budget's own reason
        wait = e.retry_after
        seconds = f"{wait} second{'' if wait == 1 else 's'}"
        return JSONResponse({"error": str(e), "retry_after": wait, "reason": "datasheet_rate_limit",
                             "resets_at": _utc_iso(math.ceil(time.time() + wait)),
                             "tell_user": f"pcbparts makes at most {DATASHEET_SIGNINGS_PER_MINUTE} new datasheet "
                                          f"links a minute for all its users; try again in {seconds}."},
                            status_code=429, headers={"Retry-After": str(wait)})
    except ValueError as e:  # JLCPCB rate limit, WAF challenge or timeout: details stay in the log
        if counted:
            stats.count_datasheet_link("failed")
        logger.warning(f"Datasheet link for {lcsc} failed: {e}")
        return JSONResponse({"error": "The datasheet source didn't answer; try again later"}, status_code=502)
    if not url:
        if counted:
            stats.count_datasheet_link("not_found")
        return JSONResponse({"error": f"No datasheet PDF found for {lcsc}"}, status_code=404)
    return RedirectResponse(url, status_code=302, headers={"Cache-Control": "no-store"})


async def usage_stats(request):
    """Private daily usage and current quotas; bearer auth, ?days=1..KEEP_DAYS (default 30)."""
    headers = {"Cache-Control": "private, no-store"}
    if not STATS_TOKEN or not hmac.compare_digest(
            request.headers.get("Authorization", "").encode("utf-8"), f"Bearer {STATS_TOKEN}".encode("utf-8")):
        return JSONResponse({"error": "Unauthorized"}, status_code=401,
                            headers={**headers, "WWW-Authenticate": "Bearer"})
    try:
        days = int(request.query_params.get("days", "30"))
    except ValueError:
        days = 30
    reply = stats.usage.summary(max(1, min(days, stats.KEEP_DAYS)))
    reply["distributor_quota"] = _distributor_quota_status()
    return JSONResponse(reply, headers=headers)


class BodySizeLimitMiddleware:
    """Reject request bodies over max_bytes with a 413 (memory-amplification guard): a declared
    Content-Length before anything is read, and the bytes actually received, so a chunked body or
    a false Content-Length can't run past it either. Past the limit the app is told the client left
    (so it stops reading) and its reply is replaced by the 413, which keeps any X-RateLimit-*
    headers that reply had (RateLimitMiddleware charged the request; the MCP SDK answers a body cut
    off this way with an error reply, which carries them). MCP JSON-RPC calls are a few
    KB; the limit is far above any legitimate request. Pure ASGI, so streamed replies pass straight
    through."""

    def __init__(self, app, max_bytes: int = MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.max_bytes = max_bytes

    @staticmethod
    def _too_large(headers: list[tuple[bytes, bytes]] = ()) -> JSONResponse:
        response = JSONResponse({"error": "Request body too large"}, status_code=413)
        response.raw_headers.extend(headers)
        return response

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        content_length = Request(scope).headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > self.max_bytes:
            return await self._too_large()(scope, receive, send)
        received = 0
        too_large = started = False
        kept_headers: list[tuple[bytes, bytes]] = []

        async def counted_receive():
            nonlocal received, too_large
            if too_large:
                return {"type": "http.disconnect"}
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    too_large = True
                    return {"type": "http.disconnect"}
            return message

        async def guarded_send(message):
            nonlocal started
            if too_large and not started:  # the 413 replaces the app's reply to the cut-off body
                if message["type"] == "http.response.start":
                    kept_headers[:] = [(name, value) for name, value in message.get("headers", ())
                                       if name.lower().startswith(b"x-ratelimit-")]
                return
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self.app(scope, counted_receive, guarded_send)
        except Exception:
            if not too_large or started:
                raise  # the app's own failure; a cut-off body's (the client "left") is answered below
        if too_large and not started:
            await self._too_large(kept_headers)(scope, receive, send)


# Create ASGI app
def create_app():
    """Create the ASGI application."""
    # Body-size guard runs first (outermost), then rate limiting.
    # FastMCP handles CORS for MCP endpoints.
    middleware = [
        Middleware(BodySizeLimitMiddleware, max_bytes=MAX_REQUEST_BODY_BYTES),
        Middleware(RateLimitMiddleware, requests_per_minute=RATE_LIMIT_REQUESTS,
                   platform_per_minute=PLATFORM_RATE_LIMIT),
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
    app.routes.append(Route("/mcp/datasheet/{lcsc}", datasheet_redirect))

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

    log_options = {}
    if LOG_PATH:
        # Configure uvicorn exactly as run() would, before attaching the persistent handler:
        # dictConfig closes existing handlers. Don't let run() configure them a second time.
        from logging.config import dictConfig
        from .file_logging import configure_file_logging

        dictConfig(uvicorn.config.LOGGING_CONFIG)
        configure_file_logging(LOG_PATH, LOG_KEEP_DAYS)
        log_options["log_config"] = None

    # Suppress /health access log spam (Docker healthchecks every 10-30s)
    logging.getLogger("uvicorn.access").addFilter(_HealthFilterLog())
    # One line instead of a traceback for the SDK's client-disconnect and unknown-method records
    from . import sdk_logs
    sdk_logs.install()

    uvicorn.run(
        "pcbparts_mcp.server:app",
        host=HTTP_HOST,
        port=HTTP_PORT,
        lifespan="on",
        # uvicorn turns these on by default (trusting X-Forwarded-For from FORWARDED_ALLOW_IPS,
        # 127.0.0.1 unless set), which would put callers' IPs on every access-log line if the proxy
        # ever connected from there; _client_ip() reads X-Forwarded-For itself
        proxy_headers=False,
        # Docker kills the process 10 s after its stop signal. Without a limit uvicorn waits for every
        # running request first, so one slow call at a deploy meant the shutdown below never ran and
        # the day's per-address counts, the hour's lines and the stats since the last save were lost.
        # After 6 s it cancels what's still running and then shuts down.
        timeout_graceful_shutdown=6,
        **log_options,
    )


if __name__ == "__main__":
    main()
