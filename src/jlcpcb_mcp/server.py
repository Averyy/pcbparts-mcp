"""JLCPCB MCP Server - Search electronic components for PCB assembly."""

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
from .config import RATE_LIMIT_REQUESTS, HTTP_PORT, DEFAULT_MIN_STOCK, MAX_PAGE_SIZE
from .client import JLCPCBClient

logger = logging.getLogger(__name__)

# Global state
_client: JLCPCBClient | None = None
_categories: list[dict[str, Any]] = []  # Live category cache


@asynccontextmanager
async def lifespan(app):
    """Manage client lifecycle and fetch live categories on startup."""
    global _client, _categories
    _client = JLCPCBClient()

    # Fetch live categories from API (once, shared with client)
    try:
        _categories = await _client.fetch_categories()
        _client.set_categories(_categories)  # Share cache with client
        logger.info(f"Loaded {len(_categories)} categories from JLCPCB API")
    except Exception as e:
        logger.warning(f"Failed to fetch categories from API: {e}")
        _categories = []

    yield

    if _client:
        await _client.close()


# Create MCP server
mcp = FastMCP(
    name="jlcmcp",
    instructions="JLCPCB component search for PCB assembly. No auth required. Use search_parts to find components, get_part for details.",
    lifespan=lifespan,
    icons=[
        Icon(src="https://jlcmcp.dev/favicon.svg", mimeType="image/svg+xml"),
        Icon(src="https://jlcmcp.dev/favicon-96x96.png", mimeType="image/png", sizes=["96x96"]),
    ],
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - 100 requests/minute per IP."""

    def __init__(self, app, requests_per_minute: int = RATE_LIMIT_REQUESTS):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: dict[str, list[float]] = defaultdict(list)

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

    def _check_rate_limit(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60
        # Filter old entries
        self.request_counts[client_ip] = [
            t for t in self.request_counts[client_ip] if t > window_start
        ]
        # Clean up empty entries to prevent memory growth
        if not self.request_counts[client_ip]:
            # New or quiet IP - not rate limited, start tracking
            self.request_counts[client_ip] = [now]
            return False
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


# Tools

@mcp.tool(
    annotations=ToolAnnotations(
        title="Search JLCPCB Parts",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
async def search_parts(
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
    limit: int = 20,
) -> dict:
    """Search JLCPCB components for PCB assembly.

    Args:
        query: Search keywords including part numbers, model names, or attribute values
               (e.g., "ESP32", "10uF 25V", "STM32F103"). Attribute values like capacitance,
               voltage rating, resistance work as search terms.
        category_id: Category ID from list_categories (e.g., 1=Resistors, 2=Capacitors)
        subcategory_id: Subcategory ID from get_subcategories
        min_stock: Min stock qty (default 50). Set 0 for all including out-of-stock
        library_type: "basic", "preferred", "no_fee" (both), "extended" ($3/part), or "all"
        package: Single package size filter (e.g., "0402", "LQFP48")
        manufacturer: Single manufacturer filter. Supports aliases (e.g., "TI" -> "Texas Instruments")
        packages: Multiple package sizes (OR filter). E.g., ["0402", "0603", "0805"]
        manufacturers: Multiple manufacturers (OR filter). E.g., ["TI", "STMicroelectronics"]
        sort_by: "quantity" (highest first) or "price" (cheapest first). Default: relevance
        page: Page number (default: 1)
        limit: Results per page (default: 20, max: 100)

    Returns:
        Results include: lcsc, model, manufacturer, package, stock, price, price_10 (volume),
        library_type, preferred, category, subcategory,
        key_specs (essential attributes for the component type - varies by subcategory).
        Pagination: page, per_page, total, total_pages, has_more.
        Use get_part(lcsc) for full details including datasheet and all attributes.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    # Validate parameters
    effective_min_stock = max(0, min_stock)
    effective_page = max(1, page)
    effective_limit = max(1, min(limit, MAX_PAGE_SIZE))

    return await _client.search(
        query=query,
        category_id=category_id,
        subcategory_id=subcategory_id,
        min_stock=effective_min_stock,
        library_type=library_type if library_type != "all" else None,
        package=package,
        manufacturer=manufacturer,
        packages=packages,
        manufacturers=manufacturers,
        sort_by=sort_by,
        page=effective_page,
        limit=effective_limit,
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
async def get_part(lcsc: str) -> dict:
    """Get full details for a specific JLCPCB part.

    Args:
        lcsc: LCSC part code (e.g., "C82899")

    Returns:
        Full part details including description, all pricing tiers, datasheet URL, and component attributes.
    """
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
async def list_categories() -> dict:
    """Get all primary component categories with their IDs.

    Returns:
        List of categories with id, name, part count, and subcategory count.
        Use category_id with search_parts, or call get_subcategories for more specific filtering.

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
async def get_subcategories(category_id: int) -> dict:
    """Get all subcategories for a specific category.

    Args:
        category_id: Primary category ID (e.g., 1 for Resistors, 2 for Capacitors)

    Returns:
        List of subcategories with id, name, and part count.
        Pass subcategory_id to search_parts for filtered searches.

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
async def find_alternatives(
    lcsc: str,
    min_stock: int = 100,
    same_package: bool = False,
    limit: int = 10,
) -> dict:
    """Find alternative parts similar to a given component.

    Searches the same subcategory for parts with better availability.
    Useful when a part has low stock or you want to compare options.

    Args:
        lcsc: LCSC part code to find alternatives for (e.g., "C2557")
        min_stock: Minimum stock for alternatives (default: 100)
        same_package: If True, only return parts with the same package size
        limit: Maximum alternatives to return (default: 10, max: 50)

    Returns:
        Original part info and list of alternatives sorted by stock.
        Alternatives include key_specs for easy comparison.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    return await _client.find_alternatives(
        lcsc=lcsc,
        min_stock=min_stock,
        same_package=same_package,
        limit=limit,
    )


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
        "service": "jlcpcb-mcp",
        "version": __version__,
        "status": "healthy",
    }


# Health check endpoint
async def health(request):
    return JSONResponse({
        "status": "healthy",
        "service": "jlcpcb-mcp",
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
        "jlcpcb_mcp.server:app",
        host="0.0.0.0",
        port=HTTP_PORT,
        lifespan="on",
    )


if __name__ == "__main__":
    main()
