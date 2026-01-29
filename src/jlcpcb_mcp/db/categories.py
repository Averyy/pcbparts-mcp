"""Category and subcategory related functions for the database."""

import sqlite3
from typing import Any

from ..config import DEFAULT_MIN_STOCK
from ..alternatives import SPEC_PARSERS
from ..search.result import row_to_dict
from ..search.spec_filter import escape_like


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
    subcategories: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Export categories in format expected by JLCPCBClient.set_categories().

    Returns list of categories with nested subcategories, matching API format.

    Args:
        subcategories: Dict mapping subcategory IDs to info

    Returns:
        List of category dicts with nested subcategories
    """
    # Group subcategories by category
    categories_dict: dict[int, dict[str, Any]] = {}

    for subcat_id, info in subcategories.items():
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
            "count": 0,  # Count not stored, but not needed for name resolution
        })

    return list(categories_dict.values())


def find_by_subcategory(
    conn: sqlite3.Connection,
    subcategories: dict[int, dict[str, Any]],
    subcategory_id: int,
    primary_spec: str | None = None,
    primary_value: Any = None,
    min_stock: int = DEFAULT_MIN_STOCK,
    library_type: str | None = None,
    prefer_no_fee: bool = True,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Find components in a subcategory, optionally matching a primary spec value.

    Used by find_alternatives to get candidates.

    Args:
        conn: SQLite connection
        subcategories: Dict mapping subcategory IDs to info
        subcategory_id: Subcategory to search in
        primary_spec: Primary spec name to match (e.g., "Resistance")
        primary_value: Value to match for primary spec
        min_stock: Minimum stock (default 50)
        library_type: Filter by library type - "basic", "preferred", or "extended"
        prefer_no_fee: Sort preference (default True)
        limit: Max results to return

    Returns:
        List of component dicts
    """
    sql_parts = ["SELECT * FROM components WHERE subcategory_id = ?"]
    params: list[Any] = [subcategory_id]

    if min_stock > 0:
        sql_parts.append("AND stock >= ?")
        params.append(min_stock)

    # Library type filter
    if library_type:
        if library_type == "basic":
            sql_parts.append("AND library_type = 'b'")
        elif library_type == "preferred":
            sql_parts.append("AND library_type = 'p'")
        elif library_type == "extended":
            sql_parts.append("AND library_type = 'e'")

    # If primary spec value provided, filter by it
    if primary_spec and primary_value:
        parser = SPEC_PARSERS.get(primary_spec)
        if parser:
            # Numeric spec - will post-filter
            pass
        else:
            # String match
            sql_parts.append("AND attributes LIKE ? ESCAPE '\\'")
            pattern = f'%"{escape_like(primary_spec)}","{escape_like(primary_value)}"%'
            params.append(pattern)

    # Sorting: prefer_no_fee sorts basic/preferred first
    if prefer_no_fee:
        lib_type_order = "CASE library_type WHEN 'b' THEN 1 WHEN 'p' THEN 2 ELSE 3 END"
        sql_parts.append(f"ORDER BY {lib_type_order}, stock DESC")
    else:
        sql_parts.append("ORDER BY stock DESC")
    sql_parts.append("LIMIT ?")
    params.append(limit * 2)  # Fetch more for post-filtering

    sql = " ".join(sql_parts)
    cursor = conn.execute(sql, params)

    results = []
    for row in cursor.fetchall():
        part = row_to_dict(row, subcategories)

        # Post-filter for numeric primary spec
        if primary_spec and primary_value:
            parser = SPEC_PARSERS.get(primary_spec)
            if parser:
                target = parser(str(primary_value))
                if target is not None:
                    part_value = part.get("specs", {}).get(primary_spec)
                    if part_value:
                        parsed = parser(part_value)
                        if parsed is None:
                            continue
                        # Allow 2% tolerance
                        if target == 0:
                            if parsed != 0:
                                continue
                        elif abs(parsed - target) / abs(target) > 0.02:
                            continue
                    else:
                        continue  # No matching attribute

        results.append(part)
        if len(results) >= limit:
            break

    return results
