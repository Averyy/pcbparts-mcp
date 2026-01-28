"""Result transformation for component search."""

import json
import logging
import sqlite3
from typing import Any

from ..mounting import detect_mounting_type

logger = logging.getLogger(__name__)


def row_to_dict(
    row: sqlite3.Row,
    subcategories: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    """Convert a database row to a component dict.

    Returns format matching client.py's _transform_part() for consistency.

    Args:
        row: SQLite Row object from query result
        subcategories: Dict mapping subcategory IDs to their info

    Returns:
        Component dict with all fields
    """
    # Parse attributes JSON back to specs dict (with error handling)
    specs: dict[str, str] = {}
    if row["attributes"]:
        try:
            attrs = json.loads(row["attributes"])
            specs = {name: value for name, value in attrs}
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse attributes for {row['lcsc']}: {e}")
            # Continue with empty specs rather than failing

    # Map library_type codes
    lib_type_map = {"b": "basic", "p": "preferred", "e": "extended"}
    library_type = lib_type_map.get(row["library_type"], row["library_type"])

    # Get subcategory info
    subcat_info = subcategories.get(row["subcategory_id"], {})
    package = row["package"]
    category = subcat_info.get("category_name")
    subcategory = subcat_info.get("name")

    return {
        "lcsc": row["lcsc"],
        "model": row["mpn"],
        "manufacturer": row["manufacturer"],
        "package": package,
        "stock": row["stock"],
        "price": row["price"],
        "price_10": None,  # Volume pricing not available in DB
        "library_type": library_type,
        "preferred": library_type in ("basic", "preferred"),
        "category": category,
        "subcategory": subcategory,
        "subcategory_id": row["subcategory_id"],
        "mounting_type": detect_mounting_type(package, category=category, subcategory=subcategory),
        "description": row["description"],
        "specs": specs,
    }
