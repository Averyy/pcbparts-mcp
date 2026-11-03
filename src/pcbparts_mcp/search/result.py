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

    result = {
        "lcsc": row["lcsc"],
        "model": row["mpn"],
        "manufacturer": row["manufacturer"],
        "package": package,
        "stock": row["stock"],
        "price": row["price"],
        "library_type": library_type,
        # JLCPCB's Preferred flag, as jlc_get_part gives it; library_type says whether there is a fee
        "preferred": library_type == "preferred",
        "category": category,
        "subcategory": subcategory,
        "subcategory_id": row["subcategory_id"],
        "mounting_type": detect_mounting_type(package, category=category, subcategory=subcategory),
        "description": row["description"],
        "specs": specs,
    }
    if specs:
        result.pop("description")
    keys = row.keys()
    if "pcba_type" in keys:  # a DB built before 0.8.4 has neither column
        if pcba := PCBA_TYPE_NAMES.get(row["pcba_type"]):
            result["pcba_type"] = pcba
        if row["no_datasheet"]:
            result["no_datasheet"] = True
    return result


# JLCPCB's PCBA type per part: "economic" parts can be placed by Economic and Standard assembly;
# one "standard_only" part moves the whole order to Standard (higher setup and stencil fees)
PCBA_TYPE_NAMES = {"e": "economic", "s": "standard_only"}


def pcba_type_from_item(item: dict[str, Any]) -> str | None:
    """pcba_type from a live JLCPCB API item (componentProductType 0 or 2), else None."""
    product_type = item.get("componentProductType")
    try:
        product_type = int(product_type) if product_type is not None else None
    except (TypeError, ValueError):
        return None
    return {0: "economic", 2: "standard_only"}.get(product_type)
