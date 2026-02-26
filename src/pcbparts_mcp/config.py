"""Configuration for PCB Parts MCP server."""

import os

# Server settings
HTTP_PORT = int(os.getenv("HTTP_PORT", "8080"))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))

# JLCPCB API endpoints
JLCPCB_SEARCH_URL = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
JLCPCB_DETAIL_URL = "https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail"

# EasyEDA API endpoints
EASYEDA_COMPONENT_URL = "https://easyeda.com/api/products/{lcsc}/components"
EASYEDA_SYMBOL_URL = "https://easyeda.com/api/components/{uuid}"
EASYEDA_CACHE_TTL = 3600  # Cache footprint availability for 1 hour
EASYEDA_ERROR_CACHE_TTL = 300  # Cache errors for 5 minutes to avoid hammering failing API
EASYEDA_REQUEST_TIMEOUT = 5.0  # Shorter timeout for EasyEDA (non-critical)
EASYEDA_CACHE_MAX_SIZE = 10000  # Max cached entries to prevent unbounded memory growth
EASYEDA_CONCURRENT_LIMIT = 5  # Max concurrent EasyEDA requests to avoid rate limiting
EASYEDA_RATE_LIMIT = 0.1  # Min seconds between requests to EasyEDA
EASYEDA_RATE_JITTER = 0.05  # Random jitter added to rate limit

# Request settings
REQUEST_TIMEOUT = 10.0
MAX_RETRIES = 3

JLCPCB_CONCURRENT_LIMIT = 10  # Max concurrent requests to JLCPCB API (prevents IP blocking)
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_MIN_STOCK = 10
MAX_ALTERNATIVES = 50

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
DIGIKEY_LOCALE_SITE = os.getenv("DIGIKEY_LOCALE_SITE", "US")
DIGIKEY_LOCALE_LANGUAGE = os.getenv("DIGIKEY_LOCALE_LANGUAGE", "en")
DIGIKEY_LOCALE_CURRENCY = os.getenv("DIGIKEY_LOCALE_CURRENCY", "USD")

# ComponentSearchEngine (SamacSys)
# Search: rs.componentsearchengine.com alligator JSON API (no auth required)
# Downloads: rs.componentsearchengine.com/ga/model.php (requires CSEARCH_USER/CSEARCH_PASS)
DISTRIBUTOR_DAILY_LIMIT = int(os.getenv("DISTRIBUTOR_DAILY_LIMIT", "1000"))

CSE_CONCURRENT_LIMIT = 3
CSE_RATE_LIMIT = 0.15
CSE_CACHE_TTL = 3600
CSE_KICAD_CACHE_TTL = 60 * 60 * 24  # Cache extracted KiCad files for 24 hours
CSE_KICAD_CACHE_MAX_SIZE = 2000  # Max cached parts (each is a few KB of text)
CSE_USER = os.getenv("CSEARCH_USER", "")
CSE_PASS = os.getenv("CSEARCH_PASS", "")
