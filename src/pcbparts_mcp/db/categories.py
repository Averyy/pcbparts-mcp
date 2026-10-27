"""Category and subcategory related functions for the database."""

import json
import sqlite3
from typing import Any, Callable

from ..config import DEFAULT_MIN_STOCK
from ..parsers import RESISTANCE_MATCH_TOLERANCE, parse_resistance
from ..alternatives import COMPATIBILITY_RULES, NORMALIZED_MATCH_SPECS, SPEC_PARSERS, STRING_MATCH_SPECS, is_stated
from ..search.result import row_to_dict
from ..search.spec_filter import SPEC_TO_COLUMN, escape_like

# Rows find_alternative_candidates reads at most per call (the SQL already applies every numeric rule)
ALTERNATIVE_SCAN_ROWS = 2000


def get_subcategory_name(
    subcategory_id: int,
    subcategories: dict[int, dict[str, Any]],
) -> str | None:
    """Get subcategory name by ID.

    Args:
        subcategory_id: Subcategory ID
        subcategories: Dict mapping subcategory IDs to info

    Returns:
        Subcategory name or None if not found
    """
    subcat = subcategories.get(subcategory_id)
    return subcat["name"] if subcat else None


def get_category_for_subcategory(
    subcategory_id: int,
    subcategories: dict[int, dict[str, Any]],
) -> tuple[int, str] | None:
    """Get category (id, name) for a subcategory.

    Args:
        subcategory_id: Subcategory ID
        subcategories: Dict mapping subcategory IDs to info

    Returns:
        Tuple of (category_id, category_name) or None if not found
    """
    subcat = subcategories.get(subcategory_id)
    if subcat:
        return subcat["category_id"], subcat["category_name"]
    return None


def get_categories_for_client(
    conn: sqlite3.Connection | None,
    subcategories: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Export categories in format expected by JLCPCBClient.set_categories().

    Returns list of categories with nested subcategories, matching API format.
    Includes real part counts from DB. Omits subcategories with 0 parts.

    Args:
        conn: SQLite connection (for counting parts)
        subcategories: Dict mapping subcategory IDs to info

    Returns:
        List of category dicts with nested subcategories
    """
    # Get real part counts per subcategory from DB
    subcat_counts: dict[int, int] = {}
    if conn:
        cursor = conn.execute(
            "SELECT subcategory_id, COUNT(*) FROM components GROUP BY subcategory_id"
        )
        subcat_counts = dict(cursor.fetchall())

    # Group subcategories by category
    categories_dict: dict[int, dict[str, Any]] = {}

    for subcat_id, info in subcategories.items():
        count = subcat_counts.get(subcat_id, 0)
        if count == 0:
            continue  # Skip empty subcategories

        cat_id = info["category_id"]
        cat_name = info["category_name"]

        if cat_id not in categories_dict:
            categories_dict[cat_id] = {
                "id": cat_id,
                "name": cat_name,
                "count": 0,
                "subcategories": [],
            }

        categories_dict[cat_id]["subcategories"].append({
            "id": subcat_id,
            "name": info["name"],
            "count": count,
        })
        categories_dict[cat_id]["count"] += count

    return list(categories_dict.values())


def find_alternative_candidates(
    conn: sqlite3.Connection,
    subcategories: dict[int, dict[str, Any]],
    original: dict[str, Any],
    subcategory: str,
    subcategory_id: int,
    min_stock: int = DEFAULT_MIN_STOCK,
    library_type: str | None = None,
    accept: Callable[[dict[str, Any]], bool] | None = None,
    limit: int = 50,
    max_rows: int = ALTERNATIVE_SCAN_ROWS,
) -> list[dict[str, Any]]:
    """Parts in a subcategory that can meet the original's compatibility rules (alternatives.py),
    no-fee parts first, then by stock. Used by find_alternatives.

    SQL narrows by the rules' numeric columns, with the same 2% slack as the checks: the primary and
    numeric must_match specs within 2% (resistances 0.1%), same_or_better specs at least as good. String must_match specs
    must be equal, unless they're normalized first. Specs without a column, and polarity, are left to
    `accept` (the full check), which picks from at most `max_rows` rows in order until it has `limit`
    parts.
    """
    rules = COMPATIBILITY_RULES.get(subcategory)
    if not rules:
        return []
    specs = original.get("specs", {})

    sql = ["SELECT * FROM components WHERE subcategory_id = ? AND stock >= ?"]
    params: list[Any] = [subcategory_id, max(min_stock, DEFAULT_MIN_STOCK)]
    library_codes = {"basic": "('b')", "preferred": "('p')", "no_fee": "('b', 'p')", "extended": "('e')"}
    if library_type in library_codes:
        sql.append(f"AND library_type IN {library_codes[library_type]}")

    def column_value(spec: str) -> tuple[str, float] | None:
        """The spec's column and the original's value, when the column holds that spec's parse."""
        column = SPEC_TO_COLUMN.get(spec)
        parser = SPEC_PARSERS.get(spec)
        value = specs.get(spec)
        if column is None or column[1] is not parser or not callable(parser) or not is_stated(value):
            return None
        parsed = parser(value)
        return (column[0], parsed) if parsed is not None else None

    for spec in dict.fromkeys([rules["primary"], *rules.get("must_match", [])]):
        value = specs.get(spec)
        if not is_stated(value):
            continue
        numeric = column_value(spec)
        if numeric:
            column, target = numeric
            share = RESISTANCE_MATCH_TOLERANCE if SPEC_PARSERS.get(spec) is parse_resistance else 0.02
            sql.append(f"AND {column} BETWEEN ? AND ?")
            params.extend([target - abs(target) * share, target + abs(target) * share])
        elif spec in STRING_MATCH_SPECS and spec not in NORMALIZED_MATCH_SPECS:
            # Attributes are stored as JSON pairs: [["Type", "N-Channel"], ...]
            sql.append("AND attributes LIKE ? ESCAPE '\\'")
            params.append("%" + escape_like(json.dumps([spec, value])) + "%")

    for spec, direction in rules.get("same_or_better", {}).items():
        numeric = column_value(spec)
        if not numeric:
            continue
        column, target = numeric
        if direction == "higher":
            sql.append(f"AND {column} >= ?")
            params.append(target * 0.98)
        elif direction == "lower":
            sql.append(f"AND {column} <= ?")
            params.append(target * 1.02)

    sql.append("ORDER BY CASE WHEN library_type IN ('b', 'p') THEN 0 ELSE 1 END, stock DESC LIMIT ?")
    params.append(max_rows)

    results: list[dict[str, Any]] = []
    for row in conn.execute(" ".join(sql), params):
        part = row_to_dict(row, subcategories)
        if accept is None or accept(part):
            results.append(part)
            if len(results) >= limit:
                break
    return results
