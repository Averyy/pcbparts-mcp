"""Configuration for PCB Parts MCP server."""

import os
import random

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

# Request settings
REQUEST_TIMEOUT = 10.0
MAX_RETRIES = 3

# Assembly fee for extended parts (JLCPCB charges per unique extended part type)
EXTENDED_PART_ASSEMBLY_FEE = 3.0
JLCPCB_CONCURRENT_LIMIT = 10  # Max concurrent requests to JLCPCB API (prevents IP blocking)
JLCPCB_REQUEST_JITTER = (0.1, 0.3)  # Random delay range (seconds) between requests
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_MIN_STOCK = 10
MAX_ALTERNATIVES = 50
MAX_BOM_PARTS = 500

# Part cache settings (JLCPCB API)
PART_CACHE_TTL = 3600  # Cache part details for 1 hour
PART_CACHE_MAX_SIZE = 5000  # Max cached parts

# User agent pool - real browser signatures from jlcpcb.com visitors
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
]

# Sec-Ch-Ua values matching the user agents
_SEC_CH_UA = [
    '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    '"Google Chrome";v="133", "Chromium";v="133", "Not_A Brand";v="24"',
]

# Referer URLs - different pages that would call this API
_REFERERS = [
    "https://jlcpcb.com/parts",
    "https://jlcpcb.com/parts/basic_parts",
    "https://jlcpcb.com/parts/componentSearch",
    "https://jlcpcb.com/partdetail/",
]


def get_jlcpcb_headers() -> dict[str, str]:
    """Generate randomized headers that look like a real browser on jlcpcb.com."""
    ua = random.choice(_USER_AGENTS)
    is_firefox = "Firefox" in ua

    headers = {
        "Host": "jlcpcb.com",
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Origin": "https://jlcpcb.com",
        "Referer": random.choice(_REFERERS),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    # Chrome-specific headers
    if not is_firefox:
        headers["Sec-Ch-Ua"] = random.choice(_SEC_CH_UA)
        headers["Sec-Ch-Ua-Mobile"] = "?0"
        platform = '"Windows"' if "Windows" in ua else '"macOS"' if "Mac" in ua else '"Linux"'
        headers["Sec-Ch-Ua-Platform"] = platform
        headers["Priority"] = "u=1, i"

    return headers


def get_random_user_agent() -> str:
    """Get a random user agent from the pool."""
    return random.choice(_USER_AGENTS)


# Mouser API
MOUSER_API_KEY = os.getenv("MOUSER_API_KEY", "")
MOUSER_BASE_URL = "https://api.mouser.com/api/v2"
MOUSER_CONCURRENT_LIMIT = 5
MOUSER_CACHE_TTL = 3600

# DigiKey API
DIGIKEY_CLIENT_ID = os.getenv("DIGIKEY_CLIENT_ID", "")
DIGIKEY_CLIENT_SECRET = os.getenv("DIGIKEY_CLIENT_SECRET", "")
DIGIKEY_BASE_URL = "https://api.digikey.com/products/v4"
DIGIKEY_TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
DIGIKEY_CONCURRENT_LIMIT = 10
DIGIKEY_CACHE_TTL = 3600
DIGIKEY_LOCALE_SITE = os.getenv("DIGIKEY_LOCALE_SITE", "US")
DIGIKEY_LOCALE_LANGUAGE = os.getenv("DIGIKEY_LOCALE_LANGUAGE", "en")
DIGIKEY_LOCALE_CURRENCY = os.getenv("DIGIKEY_LOCALE_CURRENCY", "USD")

# ComponentSearchEngine (SamacSys)
# Search: rs.componentsearchengine.com alligator JSON API (no auth required)
# Downloads: rs.componentsearchengine.com/ga/model.php (requires CSEARCH_USER/CSEARCH_PASS)
CSE_CONCURRENT_LIMIT = 3
CSE_CACHE_TTL = 3600
CSE_KICAD_CACHE_TTL = 60 * 60 * 24  # Cache extracted KiCad files for 24 hours
CSE_KICAD_CACHE_MAX_SIZE = 2000  # Max cached parts (each is a few KB of text)
CSE_USER = os.getenv("CSEARCH_USER", "")
CSE_PASS = os.getenv("CSEARCH_PASS", "")

# Static fallback (used if needed)
JLCPCB_HEADERS = get_jlcpcb_headers()
