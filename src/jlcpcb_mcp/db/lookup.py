"""Component lookup functions for the database."""

import sqlite3
from typing import Any

from ..search.result import row_to_dict
from ..search.mpn import normalize_mpn


def get_by_mpn(
    conn: sqlite3.Connection,
    mpn: str,
    subcategories: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Find components by manufacturer part number.

    Tries exact match first (case-insensitive), then falls back to
    FTS search with MPN normalization for variant matching.

    Args:
        conn: SQLite connection
        mpn: Manufacturer part number (e.g., "LM358P", "STM32F103C8T6-TR")
        subcategories: Dict mapping subcategory IDs to info

    Returns:
        List of matching component dicts, best matches first.
        Empty list if no matches found.
    """
    mpn = mpn.strip()
    if not mpn:
        return []

    results: list[dict[str, Any]] = []
    seen_lcsc: set[str] = set()

    # 1. Exact match on mpn column (case-insensitive)
    cursor = conn.execute(
        "SELECT * FROM components WHERE LOWER(mpn) = LOWER(?) ORDER BY stock DESC",
        [mpn],
    )
    for row in cursor:
        part = row_to_dict(row, subcategories)
        results.append(part)
        seen_lcsc.add(part["lcsc"])

    # 2. Try normalized MPN variants (strip -TR, insert T, etc.)
    if not results:
        variants = normalize_mpn(mpn)
        for variant in variants:
            cursor = conn.execute(
                "SELECT * FROM components WHERE LOWER(mpn) = LOWER(?) ORDER BY stock DESC",
                [variant],
            )
            for row in cursor:
                part = row_to_dict(row, subcategories)
                if part["lcsc"] not in seen_lcsc:
                    results.append(part)
                    seen_lcsc.add(part["lcsc"])
            if results:
                break

    # 3. Fall back to FTS if no exact matches
    if not results:
        for variant in normalize_mpn(mpn):
            # Quote and add prefix match for FTS
            escaped = variant.replace('"', '""')
            fts_query = f'"{escaped}"*'
            cursor = conn.execute(
                """SELECT c.* FROM components c
                   JOIN components_fts f ON c.lcsc = f.lcsc
                   WHERE f.components_fts MATCH ?
                   ORDER BY c.stock DESC
                   LIMIT 10""",
                [fts_query],
            )
            for row in cursor:
                part = row_to_dict(row, subcategories)
                if part["lcsc"] not in seen_lcsc:
                    results.append(part)
                    seen_lcsc.add(part["lcsc"])
            if results:
                break

    return results


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
