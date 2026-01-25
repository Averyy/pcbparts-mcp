"""Configuration for JLCPCB MCP server."""

import os
import random

# Server settings
HTTP_PORT = int(os.getenv("HTTP_PORT", "8080"))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))

# JLCPCB API endpoints
JLCPCB_SEARCH_URL = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
JLCPCB_DETAIL_URL = "https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail"

# EasyEDA API endpoint (for footprint/symbol availability check)
EASYEDA_COMPONENT_URL = "https://easyeda.com/api/products/{lcsc}/components"
EASYEDA_CACHE_TTL = 3600  # Cache footprint availability for 1 hour
EASYEDA_ERROR_CACHE_TTL = 300  # Cache errors for 5 minutes to avoid hammering failing API
EASYEDA_REQUEST_TIMEOUT = 5.0  # Shorter timeout for EasyEDA (non-critical)
EASYEDA_CACHE_MAX_SIZE = 10000  # Max cached entries to prevent unbounded memory growth
EASYEDA_CONCURRENT_LIMIT = 5  # Max concurrent EasyEDA requests to avoid rate limiting

# Request settings
REQUEST_TIMEOUT = 10.0
MAX_RETRIES = 3
JLCPCB_CONCURRENT_LIMIT = 10  # Max concurrent requests to JLCPCB API (prevents IP blocking)
JLCPCB_REQUEST_JITTER = (0.1, 0.3)  # Random delay range (seconds) between requests
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_MIN_STOCK = 50
MAX_ALTERNATIVES = 50

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


# Static fallback (used if needed)
JLCPCB_HEADERS = get_jlcpcb_headers()
