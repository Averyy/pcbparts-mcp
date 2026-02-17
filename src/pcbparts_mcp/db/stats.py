"""Database statistics functions."""

import sqlite3
from typing import Any


def get_stats(
    conn: sqlite3.Connection,
    categories: dict[int, dict[str, Any]],
    subcategories: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    """Get database statistics.

    Args:
        conn: SQLite connection
        categories: Dict mapping category IDs to info
        subcategories: Dict mapping subcategory IDs to info

    Returns:
        Dict with database statistics
    """
    stats = {}

    # Total parts
    cursor = conn.execute("SELECT COUNT(*) FROM components")
    stats["total_parts"] = cursor.fetchone()[0]

    # By library type
    cursor = conn.execute("""
        SELECT library_type, COUNT(*) as cnt
        FROM components
        GROUP BY library_type
    """)
    lib_counts = {}
    for row in cursor:
        lib_type = {"b": "basic", "p": "preferred", "e": "extended"}.get(
            row["library_type"], row["library_type"]
        )
        lib_counts[lib_type] = row["cnt"]
    stats["by_library_type"] = lib_counts

    # Categories count
    stats["categories"] = len(categories)
    stats["subcategories"] = len(subcategories)

    return stats
