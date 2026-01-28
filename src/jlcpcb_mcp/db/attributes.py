"""Attribute discovery for component database."""

import json
import logging
import sqlite3
from typing import Any

from ..alternatives import SPEC_PARSERS
from ..search.spec_filter import ATTRIBUTE_ALIASES, _ATTR_FULL_TO_ALIASES
from ..subcategory_aliases import (
    resolve_subcategory_name as _resolve_subcategory_name,
    find_similar_subcategories as _find_similar_subcategories,
)

logger = logging.getLogger(__name__)


def list_attributes(
    conn: sqlite3.Connection,
    subcategories: dict[int, dict[str, Any]],
    subcategory_name_to_id: dict[str, int],
    subcategory_id: int | None = None,
    subcategory_name: str | None = None,
    sample_size: int = 1000,
) -> dict[str, Any]:
    """List available filterable attributes for a subcategory.

    Scans components in the subcategory to discover what attributes exist
    and their value ranges. Useful for understanding what spec_filters
    can be used with search().

    Args:
        conn: SQLite connection
        subcategories: Dict mapping subcategory IDs to info
        subcategory_name_to_id: Dict mapping lowercase names to IDs
        subcategory_id: Subcategory ID (e.g., 2954 for MOSFETs)
        subcategory_name: Subcategory name (alternative to ID)
        sample_size: How many parts to sample (default 1000)

    Returns:
        Dict with subcategory info and list of attributes
    """
    # Resolve subcategory name to ID
    resolved_id = subcategory_id
    if subcategory_name and not subcategory_id:
        resolved_id = _resolve_subcategory_name(subcategory_name, subcategory_name_to_id)
        if resolved_id is None:
            similar = _find_similar_subcategories(
                subcategory_name, subcategory_name_to_id, subcategories, limit=5
            )
            return {
                "error": f"Subcategory not found: '{subcategory_name}'",
                "hint": "Use list_categories and get_subcategories to see available options",
                "similar_subcategories": similar,
            }

    if not resolved_id:
        return {
            "error": "Must provide subcategory_id or subcategory_name",
            "hint": "Use list_categories and get_subcategories to discover subcategory IDs",
        }

    subcat_info = subcategories.get(resolved_id)
    if not subcat_info:
        return {
            "error": f"Subcategory ID {resolved_id} not found",
            "hint": "Use get_subcategories to see valid subcategory IDs for a category",
        }

    # Sample components from this subcategory
    cursor = conn.execute(
        "SELECT attributes FROM components WHERE subcategory_id = ? LIMIT ?",
        [resolved_id, sample_size]
    )

    # Collect attribute statistics
    attr_counts: dict[str, int] = {}
    attr_values: dict[str, set[str]] = {}
    malformed_count = 0

    for row in cursor:
        if not row["attributes"]:
            continue
        try:
            attrs = json.loads(row["attributes"])
            for attr in attrs:
                # Handle malformed attributes gracefully
                if not isinstance(attr, (list, tuple)) or len(attr) != 2:
                    continue
                name, value = attr
                attr_counts[name] = attr_counts.get(name, 0) + 1
                if name not in attr_values:
                    attr_values[name] = set()
                # Only collect up to 100 unique values per attribute
                if len(attr_values[name]) < 100:
                    attr_values[name].add(value)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            malformed_count += 1
            if malformed_count <= 3:  # Log first few occurrences
                logger.debug("Malformed attributes JSON in subcategory %s: %s", resolved_id, e)
            continue

    if malformed_count > 0:
        logger.debug("Skipped %d malformed attribute records in subcategory %s", malformed_count, resolved_id)

    # Use pre-built reverse alias lookup from spec_filter module
    alias_lookup: dict[str, str] = {}
    for full_name, aliases in _ATTR_FULL_TO_ALIASES.items():
        if aliases:
            alias_lookup[full_name] = aliases[0]

    # Build attribute list
    attributes = []
    for name, count in sorted(attr_counts.items(), key=lambda x: -x[1]):
        # Determine if this is a numeric attribute
        is_numeric = name in SPEC_PARSERS or any(
            name in full_names for full_names in ATTRIBUTE_ALIASES.values()
            if any(fn in SPEC_PARSERS for fn in ATTRIBUTE_ALIASES.get(alias_lookup.get(name, ""), [name]))
        )

        # Simpler check: see if any value parses as numeric
        values = list(attr_values.get(name, []))
        parser = SPEC_PARSERS.get(name)
        if not parser:
            # Check aliases
            alias = alias_lookup.get(name)
            if alias and alias in ATTRIBUTE_ALIASES:
                for alias_target in ATTRIBUTE_ALIASES[alias]:
                    if alias_target in SPEC_PARSERS:
                        parser = SPEC_PARSERS[alias_target]
                        break

        # Test if values are numeric
        if parser and values:
            numeric_count = sum(1 for v in values[:10] if parser(v) is not None)
            is_numeric = numeric_count >= len(values[:10]) * 0.5

        attr_info: dict[str, Any] = {
            "name": name,
            "alias": alias_lookup.get(name),
            "type": "numeric" if is_numeric else "string",
            "count": count,
        }

        if is_numeric:
            # For numeric, show example values
            attr_info["example_values"] = values[:5]
        else:
            # For string, show all distinct values (up to limit)
            attr_info["values"] = sorted(values)[:20]

        attributes.append(attr_info)

    return {
        "subcategory_id": resolved_id,
        "subcategory_name": subcat_info["name"],
        "category_name": subcat_info["category_name"],
        "sample_size": sample_size,
        "attributes": attributes,
    }
