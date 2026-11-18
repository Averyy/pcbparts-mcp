"""Configuration for PCB Parts MCP server."""

import math
import os
import re
from collections.abc import Mapping
from pathlib import Path

# Problems with numeric settings (a value that isn't a number, or is out of range), each naming the
# variable and the value used instead; the server logs them at startup. A bad value no longer stops
# the server from importing this module.
CONFIG_WARNINGS: list[str] = []


def number_setting(name: str, default: int | float, minimum: int | float,
                   environ: Mapping[str, str] = os.environ, warnings: list[str] = CONFIG_WARNINGS) -> int | float:
    """The environment variable `name` as a number of default's type (int or float). Unset or blank:
    the default. Not a number (`1,000`, `1e3` for an int), or not finite: the default, with a
    warning. Below minimum: minimum, with a warning."""
    raw = (environ.get(name) or "").strip()
    if not raw:
        return default
    kind = type(default)
    try:
        value = kind(raw)
    except ValueError:
        warnings.append(f"{name}={raw!r} isn't a{'n integer' if kind is int else ' number'}; using {default}")
        return default
    if not math.isfinite(value):
        warnings.append(f"{name}={raw!r} isn't a finite number; using {default}")
        return default
    if value < minimum:
        warnings.append(f"{name}={raw!r} is below {minimum}; using {minimum}")
        return minimum
    return value

# Recorded stock events, built offline from the gzipped JSONL files in data/history/.
STOCK_HISTORY_DB_PATH = Path(os.getenv("JLCPCB_HISTORY_DB_PATH", str(
    Path(os.getenv("JLCPCB_DATA_DIR", str(Path(__file__).resolve().parents[2] / "data")))
    / "stock_history.db"
)))

# Server settings
# Bind address for uvicorn. Set 127.0.0.1 or ::1 for localhost only, :: for every IPv6
# interface, or a specific IPv4/IPv6 address. Empty counts as unset (uvicorn would read "" as every
# IPv4 and IPv6 interface), like MCP_ALLOWED_HOSTS below.
HTTP_HOST = os.getenv("HTTP_HOST", "").strip() or "0.0.0.0"
HTTP_PORT = int(os.getenv("HTTP_PORT", "8080"))
# Requests a rolling minute per address (IPv4) or /64 (IPv6), at least 1
RATE_LIMIT_REQUESTS = number_setting("RATE_LIMIT_REQUESTS", 100, 1)
# The AI platforms' shared outbound addresses (platform_ranges.py) get this many requests a minute
# per address instead of RATE_LIMIT_REQUESTS: claude.ai and ChatGPT connectors call from them for
# many users at once. 1,000 (about 330 tool calls) is about half what the 1-CPU server is estimated to
# sustain for database-served calls (scripts/load_test.py, 2026-11-18: about 1,800 a minute with
# the CPU scaled to the VPS), so one busy platform address can't take the whole server. Never less
# than RATE_LIMIT_REQUESTS (RateLimitMiddleware._limit_for takes the larger).
PLATFORM_RATE_LIMIT = number_setting("PLATFORM_RATE_LIMIT", 1000, 1)
# Shed new tools/call requests if ANY database pool has this many jobs waiting to start (counting
# tool calls admitted that haven't started yet), or its oldest has waited this many seconds.
# Measured 2026-11-18 at a third of a CPU (the VPS estimate,
# knee ~600 calls/min): 8 / 0.25 s kept accepted p95 near 1.5 s past the knee but refused 11-17%
# of calls at 360-600 a minute; 16 / 1.0 s refused ~1% at 360 but let accepted p95 reach ~2.5 s.
# Without a cap, 840 a minute collapsed to p95 12.8 s. 12 / 0.5 s sits between; the CPU quota
# exaggerates queueing at moderate load, so check prod's server_busy counts and tune by env. To turn
# the cap off, set both very large (1000000).
DB_BUSY_MAX_WAITING = number_setting("DB_BUSY_MAX_WAITING", 12, 1)
DB_BUSY_MAX_WAIT_SECONDS = number_setting("DB_BUSY_MAX_WAIT_SECONDS", 0.5, 0.001)
# /health answers 503 (unhealthy) while a database job has waited this long to start: a worker is
# stuck (queries have no timeout), and every tools/call would be refused as busy until a restart.
# Far above anything the busy cap lets a normal spike reach (it sheds new calls at 0.5 s).
DB_STUCK_WAIT_SECONDS = number_setting("DB_STUCK_WAIT_SECONDS", 60.0, 1.0)
# Anthropic's published outbound ranges (https://platform.claude.com/docs/en/api/ip-addresses, "will
# not change without notice"), comma-separated; set empty to give them the normal limit
ANTHROPIC_IP_RANGES = [r.strip() for r in os.getenv("ANTHROPIC_IP_RANGES", "160.79.104.0/21,153.61.208.0/20").split(",")
                       if r.strip()]
# OpenAI's ChatGPT connectors list (https://openai.com/chatgpt-connectors.json, which can change):
# docker-build.yml downloads it on every image build, and the copy in data/platform_ranges/ is the
# fallback. The server never downloads it. Set empty to give OpenAI's addresses the normal limit.
OPENAI_IP_RANGES_FILE = os.getenv("OPENAI_IP_RANGES_FILE", str(
    Path(__file__).resolve().parents[2] / "data" / "platform_ranges" / "openai-chatgpt-connectors.json")).strip()

# Hostnames allowed in the Host header. fastmcp 3.x DNS-rebinding protection defaults to
# localhost-only and 421s everything else — so a request arriving as Host: pcbparts.dev (passed
# through by the reverse proxy) is rejected while the localhost healthcheck still passes. Add the
# public domain here. (127.0.0.1/localhost/::1 and the bind host are always allowed by fastmcp.)
ALLOWED_HOSTS = [h.strip() for h in os.getenv("MCP_ALLOWED_HOSTS", "pcbparts.dev").split(",") if h.strip()] \
    or ["pcbparts.dev"]  # an explicitly-empty env var must not collapse to localhost-only (breaks prod)

# Origins allowed for browser-based clients. TLS terminates at the reverse proxy, so the app
# sees scheme http:// — a browser's `Origin: https://pcbparts.dev` then fails fastmcp's
# same-origin fallback (scheme mismatch → 403). Allowlist the public https origins explicitly.
# Server-side clients (Claude Code, claude.ai) send no Origin header and are unaffected.
ALLOWED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS]

# JLCPCB API endpoints
JLCPCB_SEARCH_URL = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
JLCPCB_DETAIL_URL = "https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail"

# EasyEDA API endpoints
EASYEDA_COMPONENT_URL = "https://easyeda.com/api/products/{lcsc}/components"
EASYEDA_SYMBOL_URL = "https://easyeda.com/api/components/{uuid}"
EASYEDA_CACHE_TTL = 3600  # Cache symbol data (/api/components) for 1 hour
EASYEDA_FOOTPRINT_CACHE_TTL = 86400  # Footprint availability (/api/products) rarely changes: 24 hours
EASYEDA_ERROR_CACHE_TTL = 300  # Cache errors for 5 minutes to avoid hammering failing API
EASYEDA_REQUEST_TIMEOUT = 15.0  # Total budget for EasyEDA (non-critical). wafer>=0.2 enforces
# a session-level timeout= as the TOTAL budget across all retries+rotations (not per-attempt). 5s
# was too tight to work through an EasyEDA WAF challenge. Since 0.5.6 the footprint check
# (/api/products) makes a single attempt, because its 403s are rate-limit blocks that retries prolong;
# symbol fetches (/api/components) still retry within this budget.
EASYEDA_ATTEMPT_TIMEOUT = 5.0  # Per-attempt cap for /api/components so retries can fire inside the budget
EASYEDA_CACHE_MAX_SIZE = 10000  # Max cached entries to prevent unbounded memory growth
# /api/products is rate-limited per IP: measured at 24 requests, then a bare CloudFront 403 that clears
# in about 2 minutes (docs/ref-easyeda-api.md). Stay under it process-wide and back off on the first 403.
EASYEDA_PRODUCTS_BUDGET = 20  # Max /api/products requests...
EASYEDA_PRODUCTS_WINDOW = 120.0  # ...per rolling window (seconds)
EASYEDA_COOLDOWN_BASE = 120.0  # Pause after a 403; doubles on each repeat block
EASYEDA_COOLDOWN_MAX = 1800.0  # Cap for the doubling pause (30 minutes)
EASYEDA_MAX_FOOTPRINT_CHECKS = 15  # Footprint checks per find_alternatives(has_easyeda_footprint=...) call
# find_alternatives(land_compatible=true) compares footprint pads (land.py). Pads come from
# /api/components/{footprint uuid}, which isn't the rate-limited /api/products path, but its own limit
# was never measured, so fetches are capped per call and per process and stop on the first 403/429.
# Footprint UUIDs come from the seed/store only: a land check never asks /api/products.
EASYEDA_LAND_MAX_CHECKS = 30  # Candidates compared per call (more than the default 10 listed)
EASYEDA_LAND_BUDGET = 60  # Max footprint fetches for land checks...
EASYEDA_LAND_WINDOW = 60.0  # ...per rolling window (seconds), process-wide
# EasyEDA edits footprints in place under the same UUID. The server keeps any pads it has
# (data/easyeda/pads.csv, then live fetches in the store); scripts/build_easyeda_pads.py --refresh-days
# re-fetches seeded footprints older than this.
EASYEDA_PADS_REFRESH_DAYS = 90
EASYEDA_PADS_CACHE_MAX_SIZE = 20000  # In-memory pad lists (a few hundred bytes each)
# Persistent footprint answers (docs/ref-easyeda-api.md). The store is a SQLite file that survives
# restarts and redeploys when it sits on a volume (the Docker image sets /app/cache/easyeda.db);
# unset means memory only. Only the server opens it (JLCPCBClient takes the path as an argument).
# "Has a footprint" answers are kept for good (EasyEDA edits records in place and keeps their
# UUIDs); "no footprint" answers are re-checked after EASYEDA_NOT_FOUND_TTL.
EASYEDA_STORE_PATH = os.getenv("EASYEDA_STORE_PATH", "")
EASYEDA_NOT_FOUND_TTL = 7 * 86400  # EasyEDA draws footprints for parts after they go on sale
# jlc_get_pinout re-checks a part whose symbol UUID stopped working, unless /api/products named that
# same UUID this recently (asking again would get the same answer)
EASYEDA_RECHECK_INTERVAL = 3600
EASYEDA_CONCURRENT_LIMIT = 5  # Max concurrent EasyEDA requests to avoid rate limiting
EASYEDA_RATE_LIMIT = 0.1  # Min seconds between requests to EasyEDA
EASYEDA_RATE_JITTER = 0.05  # Random jitter added to rate limit

# Request settings
REQUEST_TIMEOUT = 30.0  # Total budget per JLCPCB call (wafer>=0.2 counts retries+rotations against
# it). 30s restores the pre-wafer-0.2 effective budget (10s *per attempt* × retries/rotations);
# with a 10s total, one slow attempt + retry exhausted the budget and live tools timed out.
# Per-attempt cap so one hung attempt can't consume the whole budget and starve rotations.
JLCPCB_ATTEMPT_TIMEOUT = 5.0
MAX_RETRIES = 3

JLCPCB_CONCURRENT_LIMIT = 10  # Max concurrent requests to JLCPCB API (prevents IP blocking)
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MAX_SEARCH_OFFSET = 10_000  # jlc_search offset: 100 pages of 100
DEFAULT_MIN_STOCK = 10
MAX_ALTERNATIVES = 50
# jlc_get_parts: parts per call, and the matches listed for each MPN (its total counts them all)
GET_PARTS_MAX_ITEMS = 50
GET_PARTS_MAX_MATCHES = 10

# Max element counts for list-valued tool params (reject abusive payloads; well above real use)
MAX_LIST_PARAM_ITEMS = 50
MAX_MEASURE_ITEMS = 20
# Max request body size (MCP JSON-RPC calls are a few KB; guards against memory-amplification)
MAX_REQUEST_BODY_BYTES = 1_000_000


def clamp_limit(limit: int, hi: int) -> int:
    """Clamp a user-supplied result limit to [1, hi].

    Floors at 1: a negative limit reaches SQLite as an unbounded ``LIMIT -1`` (full-table
    fetch / DoS), and 0 is never useful. Upper-bounds at ``hi``.
    """
    return max(1, min(int(limit), hi))

# LCSC's product data, read when JLCPCB lists no datasheet or no specs for a part (9 of 12 such parts
# sampled 2026-11-04 had an LCSC PDF). One request per part per PART_CACHE_TTL at most.
LCSC_PRODUCT_URL = "https://wmsc.lcsc.com/ftps/wm/product/detail"
LCSC_REQUEST_TIMEOUT = 8.0   # total budget
LCSC_ATTEMPT_TIMEOUT = 4.0   # per attempt, so a retry fits in the budget
LCSC_RATE_LIMIT = 0.5        # min seconds between requests

# Part cache settings (JLCPCB API)
PART_CACHE_TTL = 3600  # Cache part details for 1 hour
PART_CACHE_MAX_SIZE = 5000  # Max cached parts

# Wafer session settings for JLCPCB
JLCPCB_RATE_LIMIT = 0.2  # Min seconds between requests
JLCPCB_RATE_JITTER = 0.1  # Random jitter added to rate limit
JLCPCB_MAX_ROTATIONS = 10  # Max fingerprint rotations on 403

# Mouser API
MOUSER_API_KEY = os.getenv("MOUSER_API_KEY", "")


def mouser_extra_keys(environ: Mapping[str, str], first: str = "") -> tuple[list[str], list[str]]:
    """Optional extra Mouser API keys, each used only after the previous key's day is spent
    (MouserKeyPool): MOUSER_API_KEY_2, MOUSER_API_KEY_3, ... read in order until one is unset or
    blank. Returns the keys and a warning for each MOUSER_API_KEY_<n> that's set but not used:
    after that gap (MOUSER_API_KEY_3 without MOUSER_API_KEY_2), or repeating an earlier key. The
    warnings name variables only, never a key."""
    keys: list[str] = []
    seen = {first.strip()} if first.strip() else set()
    warnings: list[str] = []
    used: set[str] = set()
    number = 2
    while key := (environ.get(f"MOUSER_API_KEY_{number}") or "").strip():
        name = f"MOUSER_API_KEY_{number}"
        used.add(name)
        if key in seen:
            warnings.append(f"{name} is ignored: it's the same key as an earlier Mouser key")
        else:
            seen.add(key)
            keys.append(key)
        number += 1
    stop = f"MOUSER_API_KEY_{number}"
    for name in sorted((n for n, value in environ.items()
                        if re.fullmatch(r"MOUSER_API_KEY_\d+", n) and n not in used and (value or "").strip()),
                       key=lambda n: int(n.rsplit("_", 1)[1])):
        warnings.append(f"{name} is ignored: extra Mouser keys are read from MOUSER_API_KEY_2 up, in order, "
                        f"until one is missing ({stop} is)")
    return keys, warnings


MOUSER_EXTRA_API_KEYS, MOUSER_KEY_WARNINGS = mouser_extra_keys(os.environ, MOUSER_API_KEY)
MOUSER_BASE_URL = "https://api.mouser.com/api/v2"
# Mouser/DigiKey answers (stock, prices, lifecycle) are kept per part number for 3 days, in
# distributor_store.py (on the cache volume when DISTRIBUTOR_STORE_PATH is set): clients that
# re-read each part about daily got nothing from a day's cache; 3 days answers about 2 in 3 and
# shares one request between callers. Replies carry observed_at, so callers see the age.
MOUSER_CACHE_TTL = 3 * 86400
# "Part not found" answers are kept for less time: one that wasn't really about the part (an API
# glitch, a part listed later) hides that part for at most this long
MOUSER_NOT_FOUND_TTL = 86400
# Concurrent one-part Mouser lookups that start within this many seconds share one request (up to 10
# part numbers), so separate callers' lookups cost one request instead of several
MOUSER_POOL_WINDOW = 0.1

# DigiKey API
DIGIKEY_CLIENT_ID = os.getenv("DIGIKEY_CLIENT_ID", "")
DIGIKEY_CLIENT_SECRET = os.getenv("DIGIKEY_CLIENT_SECRET", "")
DIGIKEY_CLIENT_ID_2 = os.getenv("DIGIKEY_CLIENT_ID_2", "")
DIGIKEY_CLIENT_SECRET_2 = os.getenv("DIGIKEY_CLIENT_SECRET_2", "")
DIGIKEY_BASE_URL = "https://api.digikey.com/products/v4"
DIGIKEY_TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
DIGIKEY_CACHE_TTL = 3 * 86400  # as MOUSER_CACHE_TTL
DIGIKEY_NOT_FOUND_TTL = 86400  # as MOUSER_NOT_FOUND_TTL

# Lifecycle store (distributor_store.py, part_lifecycle): every lifecycle status Mouser or DigiKey
# states, by maker and MPN. A status changes rarely and with notice (JEDEC JESD48: at least 6 months
# from a discontinuation notice to the last order), so it's kept 90 days; an unknown status a week;
# "not listed" (the distributor has no part with that number: mostly Chinese makers' parts, which
# neither carries) 30 days, so each such part costs a request a month, not a week.
# part_lifecycle takes up to this many parts a call.
LIFECYCLE_TTL = 90 * 86400
LIFECYCLE_UNKNOWN_TTL = 7 * 86400
LIFECYCLE_NOT_LISTED_TTL = 30 * 86400
LIFECYCLE_MAX_PARTS = 50
# part_lifecycle stops sending a maker's parts to a distributor that, over the last MAKER_SKIP_DAYS
# days, said "not listed" for at least MAKER_SKIP_NOT_LISTED of them and listed none (counts per
# maker and distributor in distributor_store.py; no part numbers). Never for a maker it listed in
# that time, and the counts age out, so a maker it starts carrying is asked again.
MAKER_SKIP_DAYS = 30
MAKER_SKIP_NOT_LISTED = 20
DIGIKEY_LOCALE_SITE = os.getenv("DIGIKEY_LOCALE_SITE", "US")
DIGIKEY_LOCALE_LANGUAGE = os.getenv("DIGIKEY_LOCALE_LANGUAGE", "en")
DIGIKEY_LOCALE_CURRENCY = os.getenv("DIGIKEY_LOCALE_CURRENCY", "USD")

# ComponentSearchEngine (SamacSys)
# Search: rs.componentsearchengine.com alligator JSON API (no auth required)
# Downloads: rs.componentsearchengine.com/ga/model.php (requires CSEARCH_USER/CSEARCH_PASS)
DISTRIBUTOR_DAILY_LIMIT = int(os.getenv("DISTRIBUTOR_DAILY_LIMIT", "1000"))
# Our caps per rolling minute, below each API's own: Mouser allows 30 a minute, DigiKey 120 (and
# suspends an app for ten minutes for going over its per-second threshold).
MOUSER_PER_MINUTE = 25
DIGIKEY_PER_MINUTE = 100
# DigiKey requests go out at most this many a second; a burst waits its turn (DigiKeyClient)
DIGIKEY_PER_SECOND = 5
# Mouser/DigiKey daily request counts, and a pause DigiKey asked for, kept across restarts. The
# Docker image sets /app/cache/distributor_quota.json (the pcbparts-cache volume). Unset means
# memory only: every restart starts the day's count from 0, while DigiKey keeps counting.
DISTRIBUTOR_QUOTA_PATH = os.getenv("DISTRIBUTOR_QUOTA_PATH", "")
# Mouser/DigiKey answers and the lifecycle store (distributor_store.py), a SQLite file kept across
# restarts. The Docker image sets /app/cache/distributor.db (the pcbparts-cache volume). Unset means
# memory only: a restart empties both.
DISTRIBUTOR_STORE_PATH = os.getenv("DISTRIBUTOR_STORE_PATH", "")
# Anonymous daily usage counts served at /mcp/stats (stats.py), kept across restarts. The Docker image
# sets /app/cache/usage_stats.json (the pcbparts-cache volume). Unset means memory only.
USAGE_STATS_PATH = os.getenv("USAGE_STATS_PATH", "")

CSE_CONCURRENT_LIMIT = 3
CSE_RATE_LIMIT = 0.15
CSE_STATUS_RETRY_DELAY = 3.0  # seconds before asking again after a status other than "Success"
CSE_REQUEST_TIMEOUT = float(os.getenv("CSE_REQUEST_TIMEOUT", "45"))
CSE_CACHE_TTL = 3600
CSE_KICAD_CACHE_TTL = 60 * 60 * 24  # Cache extracted KiCad files for 24 hours
# SQLite file of CSE searches and KiCad files (cse_store.py), kept across restarts; empty = memory only.
# A search where every part has a model, and a part's KiCad files, are kept a year; a search with a
# part that has no model yet (CSE builds them on request), or with no parts, a week.
CSE_STORE_PATH = os.getenv("CSE_STORE_PATH", "")
CSE_FOUND_TTL = 365 * 86400
CSE_NOT_FOUND_TTL = 7 * 86400
CSE_KICAD_CACHE_MAX_SIZE = 2000  # Max cached parts (each is a few KB of text)
CSE_USER = os.getenv("CSEARCH_USER", "")
CSE_PASS = os.getenv("CSEARCH_PASS", "")
