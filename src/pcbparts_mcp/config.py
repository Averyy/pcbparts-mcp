"""Configuration for PCB Parts MCP server."""

import os

# Server settings
HTTP_PORT = int(os.getenv("HTTP_PORT", "8080"))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))

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
DEFAULT_MIN_STOCK = 10
MAX_ALTERNATIVES = 50

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

# Part cache settings (JLCPCB API)
PART_CACHE_TTL = 3600  # Cache part details for 1 hour
PART_CACHE_MAX_SIZE = 5000  # Max cached parts

# Wafer session settings for JLCPCB
JLCPCB_RATE_LIMIT = 0.2  # Min seconds between requests
JLCPCB_RATE_JITTER = 0.1  # Random jitter added to rate limit
JLCPCB_MAX_ROTATIONS = 10  # Max fingerprint rotations on 403

# Mouser API
MOUSER_API_KEY = os.getenv("MOUSER_API_KEY", "")
MOUSER_BASE_URL = "https://api.mouser.com/api/v2"
MOUSER_CACHE_TTL = 3600

# DigiKey API
DIGIKEY_CLIENT_ID = os.getenv("DIGIKEY_CLIENT_ID", "")
DIGIKEY_CLIENT_SECRET = os.getenv("DIGIKEY_CLIENT_SECRET", "")
DIGIKEY_BASE_URL = "https://api.digikey.com/products/v4"
DIGIKEY_TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
DIGIKEY_CACHE_TTL = 3600
# "Part not found" answers are kept for less time: a 404 that wasn't really about the part
# (an API glitch) hides that part for at most this long
DIGIKEY_NOT_FOUND_TTL = 600
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
# Anonymous daily usage counts served at /mcp/stats (stats.py), kept across restarts. The Docker image
# sets /app/cache/usage_stats.json (the pcbparts-cache volume). Unset means memory only.
USAGE_STATS_PATH = os.getenv("USAGE_STATS_PATH", "")

CSE_CONCURRENT_LIMIT = 3
CSE_RATE_LIMIT = 0.15
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
