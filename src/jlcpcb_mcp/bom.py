"""BOM (Bill of Materials) generation for JLCPCB assembly."""

import csv
import io
import re
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class BOMIssue:
    """Represents an issue found during BOM validation."""

    lcsc: str | None
    designators: list[str]
    severity: Literal["error", "warning"]
    issue: str


@dataclass
class BOMPart:
    """Represents a processed BOM line item."""

    lcsc: str | None
    designators: list[str]
    quantity: int
    comment: str
    footprint: str
    stock: int | None = None
    price: float | None = None
    order_qty: int = 0
    line_cost: float | None = None
    library_type: str | None = None
    min_order: int | None = None
    manufacturer: str | None = None
    model: str | None = None
    has_easyeda_footprint: bool | None = None

    @property
    def designators_str(self) -> str:
        """Comma-joined designators for display."""
        return ",".join(self.designators)


@dataclass
class BOMResult:
    """Result of BOM validation/export."""

    parts: list[BOMPart]
    issues: list[BOMIssue]
    summary: dict[str, Any]
    csv: str | None = None


def validate_designators(parts_input: list[dict[str, Any]]) -> list[BOMIssue]:
    """Check for duplicate and empty designators across all parts.

    Args:
        parts_input: List of part dicts with 'designators' lists

    Returns:
        List of error issues for any duplicate or empty designators
    """
    issues: list[BOMIssue] = []
    seen: dict[str, int] = {}  # designator -> index where first seen

    for idx, part in enumerate(parts_input):
        designators = part.get("designators", [])

        # Check for empty designators list
        if not designators:
            issues.append(BOMIssue(
                lcsc=part.get("lcsc"),
                designators=[],
                severity="error",
                issue="Part has no designators",
            ))
            continue

        for designator in designators:
            if designator in seen:
                issues.append(BOMIssue(
                    lcsc=part.get("lcsc"),
                    designators=[designator],
                    severity="error",
                    issue=f"Duplicate designator: {designator} appears multiple times",
                ))
            else:
                seen[designator] = idx

    return issues


def merge_duplicate_parts(parts_input: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[BOMIssue]]:
    """Merge parts with the same LCSC code, combining designators.

    Args:
        parts_input: List of part dicts

    Returns:
        Tuple of (merged parts list, warning issues for conflicting overrides)
    """
    issues: list[BOMIssue] = []
    merged: dict[str | None, dict[str, Any]] = {}  # lcsc -> merged part
    non_lcsc_parts: list[dict[str, Any]] = []

    for part in parts_input:
        lcsc = part.get("lcsc")
        if not lcsc:
            # Manual parts (no LCSC) are not merged
            non_lcsc_parts.append(part)
            continue

        lcsc = lcsc.strip().upper()
        if lcsc not in merged:
            merged[lcsc] = {
                "lcsc": lcsc,
                "designators": list(part.get("designators", [])),
                "comment": part.get("comment"),
                "footprint": part.get("footprint"),
            }
        else:
            # Merge designators
            existing = merged[lcsc]
            existing["designators"].extend(part.get("designators", []))

            # Check for conflicting overrides
            if part.get("comment") and existing.get("comment") and part["comment"] != existing["comment"]:
                issues.append(BOMIssue(
                    lcsc=lcsc,
                    designators=existing["designators"],
                    severity="warning",
                    issue=f"Conflicting comment overrides for {lcsc}: using '{existing['comment']}'",
                ))
            elif part.get("comment") and not existing.get("comment"):
                existing["comment"] = part["comment"]

            if part.get("footprint") and existing.get("footprint") and part["footprint"] != existing["footprint"]:
                issues.append(BOMIssue(
                    lcsc=lcsc,
                    designators=existing["designators"],
                    severity="warning",
                    issue=f"Conflicting footprint overrides for {lcsc}: using '{existing['footprint']}'",
                ))
            elif part.get("footprint") and not existing.get("footprint"):
                existing["footprint"] = part["footprint"]

    # Deduplicate designators within each merged part
    for part in merged.values():
        part["designators"] = list(dict.fromkeys(part["designators"]))

    return list(merged.values()) + non_lcsc_parts, issues


def _designator_sort_key(designator: str) -> tuple[str, int, str]:
    """Generate sort key for natural ordering of designators.

    Returns tuple of (prefix, number, suffix) for sorting.
    E.g., "C10" -> ("C", 10, ""), "R2A" -> ("R", 2, "A")
    """
    match = re.match(r"([A-Za-z]+)(\d+)(.*)", designator)
    if match:
        prefix, num, suffix = match.groups()
        return (prefix.upper(), int(num), suffix)
    # Fallback for non-standard designators
    return (designator.upper(), 0, "")


def sort_by_designator(parts: list[BOMPart]) -> list[BOMPart]:
    """Sort parts by their first designator using natural ordering.

    Groups by prefix (C, R, U), then numeric sort within each group.
    E.g., C1, C2, C10, R1, R2, U1
    """
    return sorted(parts, key=lambda p: _designator_sort_key(p.designators[0]) if p.designators else ("", 0, ""))


def generate_comment(
    part_data: dict[str, Any],
    user_override: str | None = None,
) -> str:
    """Generate Comment field for BOM.

    Priority:
    1. User-provided override
    2. key_specs + package if concise (≤50 chars)
    3. model (MPN)
    4. package or "Unknown"

    Args:
        part_data: Part data from API
        user_override: Optional user-provided comment

    Returns:
        Comment string for BOM
    """
    if user_override:
        return user_override

    model = part_data.get("model", "")
    key_specs = part_data.get("key_specs", {})
    package = part_data.get("package", "")

    # For passives, use specs (more useful than MPN)
    if key_specs:
        specs_str = " ".join(str(v) for v in key_specs.values() if v)
        if specs_str:
            if package and package.lower() not in specs_str.lower():
                specs_str = f"{specs_str} {package}"
            if len(specs_str) <= 50:
                return specs_str

    # Fall back to model
    if model:
        return model[:50]

    # Last resort
    return package or "Unknown"


def check_footprint_mismatch(
    user_footprint: str | None,
    api_footprint: str | None,
) -> BOMIssue | None:
    """Check if user-provided footprint differs from API footprint.

    Args:
        user_footprint: User-provided footprint override
        api_footprint: Footprint from API

    Returns:
        Warning issue if mismatch, None otherwise
    """
    if not user_footprint or not api_footprint:
        return None

    if user_footprint.strip().lower() != api_footprint.strip().lower():
        return BOMIssue(
            lcsc=None,  # Will be filled by caller
            designators=[],  # Will be filled by caller
            severity="warning",
            issue=f"Footprint mismatch: override is {user_footprint}, part is {api_footprint}",
        )
    return None


def get_price_at_quantity(prices: list[dict[str, Any]], order_qty: int) -> float | None:
    """Find the price tier that matches order quantity.

    Args:
        prices: List of price tiers [{"qty": "1+", "price": 0.01}, ...]
        order_qty: Total units to order

    Returns:
        Unit price at the matching tier, or None if no prices
    """
    if not prices:
        return None

    # Parse price tiers: "1+", "10+", "100+" etc
    parsed_tiers: list[tuple[int, float]] = []
    for tier in prices:
        qty_str = tier.get("qty", "1+")
        try:
            # Handle both "1+" and raw int formats
            qty = int(str(qty_str).rstrip("+"))
            price = float(tier.get("price", 0))
            parsed_tiers.append((qty, price))
        except (ValueError, TypeError):
            continue

    if not parsed_tiers:
        return None

    # Sort by quantity ascending
    parsed_tiers.sort(key=lambda x: x[0])

    # Find the highest tier that order_qty qualifies for
    selected_price = parsed_tiers[0][1]  # Default to lowest tier
    for qty, price in parsed_tiers:
        if order_qty >= qty:
            selected_price = price
        else:
            break

    return selected_price


def calculate_line_cost(
    prices: list[dict[str, Any]],
    quantity: int,
    board_qty: int | None,
) -> tuple[int, float | None, float | None]:
    """Calculate order quantity, unit price, and line cost.

    Args:
        prices: List of price tiers
        quantity: Number of components per board
        board_qty: Number of boards (None = 1)

    Returns:
        Tuple of (order_qty, unit_price, line_cost)
    """
    order_qty = quantity * (board_qty or 1)
    unit_price = get_price_at_quantity(prices, order_qty)

    if unit_price is not None:
        line_cost = round(unit_price * order_qty, 4)
    else:
        line_cost = None

    return order_qty, unit_price, line_cost


def _sanitize_csv_field(value: str) -> str:
    """Sanitize a CSV field to prevent formula injection in Excel.

    Prefixes values starting with formula characters (=, -, +, @, tab, carriage return)
    with a single quote to prevent Excel from interpreting them as formulas.
    """
    if value and value[0] in ('=', '-', '+', '@', '\t', '\r'):
        return "'" + value
    return value


def generate_csv(parts: list[BOMPart]) -> str:
    """Generate JLCPCB-compatible CSV from BOM parts.

    Format:
    Comment,Designator,Footprint,LCSC Part #

    Args:
        parts: List of BOMPart objects

    Returns:
        CSV string
    """
    output = io.StringIO(newline='')
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

    # Header row
    writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])

    # Data rows - sanitize fields to prevent CSV injection
    for part in parts:
        writer.writerow([
            _sanitize_csv_field(part.comment),
            _sanitize_csv_field(part.designators_str),
            _sanitize_csv_field(part.footprint),
            part.lcsc or "",  # LCSC codes are validated, no need to sanitize
        ])

    return output.getvalue()


def generate_summary(
    parts: list[BOMPart],
    board_qty: int | None,
    issues: list[BOMIssue],
) -> dict[str, Any]:
    """Generate BOM summary with costs and counts.

    Args:
        parts: List of BOMPart objects
        board_qty: Number of boards (None = 1)
        issues: List of issues found

    Returns:
        Summary dict
    """
    total_line_items = len(parts)
    total_components = sum(p.quantity for p in parts)

    # Calculate costs
    estimated_cost = 0.0
    extended_parts_count = 0
    for part in parts:
        if part.line_cost is not None:
            estimated_cost += part.line_cost
        if part.library_type == "extended":
            extended_parts_count += 1

    extended_parts_fee = extended_parts_count * 3.0  # $3 per extended part
    total_with_fees = round(estimated_cost + extended_parts_fee, 2)

    # Check if all parts have sufficient stock
    has_stock_errors = any(
        issue.severity == "error" and "stock" in issue.issue.lower()
        for issue in issues
    )
    stock_sufficient = not has_stock_errors

    return {
        "total_line_items": total_line_items,
        "total_components": total_components,
        "estimated_cost": round(estimated_cost, 2),
        "extended_parts_count": extended_parts_count,
        "extended_parts_fee": extended_parts_fee,
        "total_with_fees": total_with_fees,
        "board_qty": board_qty,
        "stock_sufficient": stock_sufficient,
    }


def validate_manual_part(part: dict[str, Any]) -> list[BOMIssue]:
    """Validate a manual part (no LCSC code) has required fields.

    Args:
        part: Part dict without lcsc

    Returns:
        List of error issues for missing fields
    """
    issues: list[BOMIssue] = []
    designators = part.get("designators", [])

    if not part.get("comment"):
        issues.append(BOMIssue(
            lcsc=None,
            designators=designators,
            severity="error",
            issue="Missing required field: comment (required for manual parts)",
        ))

    if not part.get("footprint"):
        issues.append(BOMIssue(
            lcsc=None,
            designators=designators,
            severity="error",
            issue="Missing required field: footprint (required for manual parts)",
        ))

    return issues


def check_stock_issues(
    part: BOMPart,
    min_stock: int,
    board_qty: int | None,
) -> list[BOMIssue]:
    """Check for stock-related issues.

    Args:
        part: BOMPart with stock info
        min_stock: Minimum stock threshold for warnings
        board_qty: Number of boards (for calculating required quantity)

    Returns:
        List of issues (errors for OOS/insufficient, warnings for low stock)
    """
    issues: list[BOMIssue] = []

    if part.stock is None:
        return issues

    # Out of stock
    if part.stock == 0:
        issues.append(BOMIssue(
            lcsc=part.lcsc,
            designators=part.designators,
            severity="error",
            issue="Out of stock (0 available)",
        ))
        return issues

    # Insufficient stock for board_qty
    if board_qty is not None:
        required = part.quantity * board_qty
        if part.stock < required:
            issues.append(BOMIssue(
                lcsc=part.lcsc,
                designators=part.designators,
                severity="error",
                issue=f"Insufficient stock: need {required}, have {part.stock}",
            ))
            return issues

    # Low stock warning (only if board_qty not provided)
    if board_qty is None and min_stock > 0 and part.stock < min_stock:
        issues.append(BOMIssue(
            lcsc=part.lcsc,
            designators=part.designators,
            severity="warning",
            issue=f"Low stock: {part.stock} available",
        ))

    return issues


def check_moq_issue(part: BOMPart) -> BOMIssue | None:
    """Check if order quantity is below minimum order quantity.

    Args:
        part: BOMPart with min_order and order_qty

    Returns:
        Warning issue if below MOQ, None otherwise
    """
    if part.min_order is not None and part.order_qty < part.min_order:
        return BOMIssue(
            lcsc=part.lcsc,
            designators=part.designators,
            severity="warning",
            issue=f"MOQ is {part.min_order}, you need {part.order_qty}",
        )
    return None


def check_extended_part(part: BOMPart) -> BOMIssue | None:
    """Check if part is extended library (has assembly fee).

    Args:
        part: BOMPart with library_type

    Returns:
        Warning issue if extended, None otherwise
    """
    if part.library_type == "extended":
        return BOMIssue(
            lcsc=part.lcsc,
            designators=part.designators,
            severity="warning",
            issue="Extended part: +$3 assembly fee",
        )
    return None


def check_easyeda_footprint(part: BOMPart) -> BOMIssue | None:
    """Check if part has EasyEDA footprint available.

    Args:
        part: BOMPart with has_easyeda_footprint

    Returns:
        Warning issue if no footprint, None otherwise
    """
    if part.has_easyeda_footprint is False:
        return BOMIssue(
            lcsc=part.lcsc,
            designators=part.designators,
            severity="warning",
            issue="No EasyEDA footprint available",
        )
    return None
