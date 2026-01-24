"""JLCPCB MCP Server - Search electronic components for PCB assembly."""

import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import __version__
from .config import RATE_LIMIT_REQUESTS, HTTP_PORT
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
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - 100 requests/minute per IP."""

    def __init__(self, app, requests_per_minute: int = RATE_LIMIT_REQUESTS):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _check_rate_limit(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60
        self.request_counts[client_ip] = [
            t for t in self.request_counts[client_ip] if t > window_start
        ]
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            return True
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
    min_stock: int = 100,
    library_type: str | None = None,
    package: str | None = None,
    manufacturer: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Search JLCPCB components for PCB assembly.

    Args:
        query: Search keyword (e.g., "ESP32", "100nF 0402", "STM32F103C8T6")
        category_id: Category ID (e.g., 1=Resistors, 2=Capacitors). Use list_categories to get IDs.
        subcategory_id: Subcategory ID (e.g., 2980=Chip Resistors). Use get_subcategories to get IDs.
        min_stock: Minimum stock quantity (default: 100). Set to 0 to include out-of-stock.
        library_type: Filter by fee type - "basic" (no fee), "preferred" (no fee), "no_fee" (basic+preferred), "extended" ($3 fee), or "all"
        package: Filter by package size (e.g., "0402", "0603", "LQFP48")
        manufacturer: Filter by manufacturer (e.g., "STMicroelectronics")
        page: Page number for pagination (default: 1)
        limit: Results per page (default: 20, max: 100)

    Returns:
        Search results with lcsc code, model, manufacturer, package, stock, price, library_type, category.
        Use get_part with the lcsc code to get full details including datasheet and pricing tiers.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    return await _client.search(
        query=query,
        category_id=category_id,
        subcategory_id=subcategory_id,
        min_stock=min_stock,
        library_type=library_type if library_type != "all" else None,
        package=package,
        manufacturer=manufacturer,
        page=page,
        limit=min(limit, 100),
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
