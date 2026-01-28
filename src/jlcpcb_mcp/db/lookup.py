"""Component lookup functions for the database."""

import sqlite3
from typing import Any

from ..search.result import row_to_dict


def get_by_lcsc(
    conn: sqlite3.Connection,
    lcsc: str,
    subcategories: dict[int, dict[str, Any]],
) -> dict[str, Any] | None:
    """Get a single component by LCSC code.

    Args:
        conn: SQLite connection
        lcsc: LCSC code (e.g., "C1525")
        subcategories: Dict mapping subcategory IDs to info

    Returns:
        Component dict or None if not found
    """
    cursor = conn.execute(
        "SELECT * FROM components WHERE lcsc = ?",
        [lcsc.upper()]
    )
    row = cursor.fetchone()
    return row_to_dict(row, subcategories) if row else None


MAX_BATCH_SIZE = 1000  # Prevent memory/performance issues with huge batches


def get_by_lcsc_batch(
    conn: sqlite3.Connection,
    lcsc_codes: list[str],
    subcategories: dict[int, dict[str, Any]],
) -> dict[str, dict[str, Any] | None]:
    """Get multiple components by LCSC codes in a single query.

    More efficient than calling get_by_lcsc() multiple times.
    Useful for BOM validation.

    Args:
        conn: SQLite connection
        lcsc_codes: List of LCSC codes (e.g., ["C1525", "C25804", "C19702"])
            Maximum 1000 codes per batch.
        subcategories: Dict mapping subcategory IDs to info

    Returns:
        Dict mapping LCSC code to component data (or None if not found).
        Example: {"C1525": {...}, "C25804": {...}, "C99999": None}

    Raises:
        ValueError: If more than MAX_BATCH_SIZE codes are provided.
    """
    if not lcsc_codes:
        return {}

    if len(lcsc_codes) > MAX_BATCH_SIZE:
        raise ValueError(
            f"Batch size {len(lcsc_codes)} exceeds maximum of {MAX_BATCH_SIZE}. "
            "Split into smaller batches."
        )

    # Normalize codes (uppercase, dedupe while preserving order)
    seen = set()
    normalized = []
    for code in lcsc_codes:
        upper = code.upper()
        if upper not in seen:
            seen.add(upper)
            normalized.append(upper)

    # Single query with IN clause
    placeholders = ",".join("?" * len(normalized))
    cursor = conn.execute(
        f"SELECT * FROM components WHERE lcsc IN ({placeholders})",
        normalized
    )

    # Build result dict
    results: dict[str, dict[str, Any] | None] = {code: None for code in normalized}
    for row in cursor:
        part = row_to_dict(row, subcategories)
        results[part["lcsc"]] = part

    return results
