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
        # If IP has no recent requests, delete the key to prevent memory growth
        # from accumulating stale IPs, then start fresh tracking
        if not self.request_counts[client_ip]:
            del self.request_counts[client_ip]
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
    if query and len(query) > 500:
        return {"error": "Query too long (max 500 characters)"}
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
        Full part details including description, all pricing tiers, datasheet URL,
        component attributes, and EasyEDA footprint availability:
        - has_easyeda_footprint: True if EasyEDA has footprint/symbol, False if not, null if unknown
        - easyeda_symbol_uuid: UUID for direct EasyEDA editor link (null if no footprint)
        - easyeda_footprint_uuid: UUID for footprint (null if no footprint)

        Note: has_easyeda_footprint=True means `ato create part` will work for Atopile/KiCad users.
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
    has_easyeda_footprint: bool | None = None,
    limit: int = 10,
) -> dict:
    """Find alternative parts similar to a given component.

    Searches the same subcategory for parts with better availability.
    Useful when a part has low stock or you want to compare options.

    Args:
        lcsc: LCSC part code to find alternatives for (e.g., "C2557")
        min_stock: Minimum stock for alternatives (default: 100)
        same_package: If True, only return parts with the same package size
        has_easyeda_footprint: Filter by EasyEDA footprint availability:
            - True: Only return parts WITH EasyEDA footprints (for Atopile/KiCad users)
            - False: Only return parts WITHOUT footprints
            - None (default): Don't filter by footprint (fastest)
            Note: Filtering by footprint is slower as it checks each alternative.
        limit: Maximum alternatives to return (default: 10, max: 50)

    Returns:
        Original part info (with has_easyeda_footprint) and list of alternatives sorted by stock.
        Alternatives include key_specs for easy comparison.
        When filtering by footprint, alternatives also include EasyEDA UUIDs.
    """
    if not _client:
        raise RuntimeError("Client not initialized")

    return await _client.find_alternatives(
        lcsc=lcsc,
        min_stock=min_stock,
        same_package=same_package,
        has_easyeda_footprint=has_easyeda_footprint,
        limit=limit,
    )


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
    if not _client:
        raise RuntimeError("Client not initialized")

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

    # Step 4: Fetch LCSC parts
    lcsc_codes = [p["lcsc"] for p in merged_parts if p.get("lcsc")]
    fetched_parts = await _client.get_parts_batch(lcsc_codes) if lcsc_codes else {}

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
            prices = fetched.get("prices", [])
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
async def validate_bom(
    parts: list[dict[str, Any]],
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
                - "Extended part: +$3 assembly fee" (warning)
                - "No EasyEDA footprint available" (warning)

    Note: Issues are reported but don't block the response. Caller decides whether to proceed.
    """
    try:
        sorted_parts, issues, summary = await _process_bom(parts, board_qty, min_stock)
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
async def export_bom(
    parts: list[dict[str, Any]],
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
    try:
        sorted_parts, issues, summary = await _process_bom(parts, board_qty, min_stock)
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
