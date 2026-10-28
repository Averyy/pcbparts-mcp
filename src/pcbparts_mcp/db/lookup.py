"""Component lookup functions for the database."""

import sqlite3
from typing import Any

from ..search.result import row_to_dict
from ..search.mpn import (
    ALTERNATIVE_MANUFACTURERS, MPN_ALIASES, MPN_KEY_SQL, PACKING_RULES,
    annotated_mpn_candidates, mpn_key, normalize_mpn,
)


def get_by_mpn(
    conn: sqlite3.Connection,
    mpn: str,
    subcategories: dict[int, dict[str, Any]],
    *,
    match_info: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Find an MPN, preserving exact/normalized/FTS precedence within a candidate.

    Additional recoveries compare separator keys and curated vendor packing or
    ordering aliases. Only after the full input misses are annotations and
    alternatives tried. Optional reply metadata leaves list callers unchanged.
    """
    if match_info is not None:
        match_info.clear()
    mpn = mpn.strip()
    if not mpn:
        return []

    def parts(rows):
        unique = {}
        for row in rows:
            if row["lcsc"] not in unique:
                unique[row["lcsc"]] = row_to_dict(row, subcategories)
        return list(unique.values())

    def keyed(candidate, vendors=()):
        sql = f"SELECT * FROM components WHERE {MPN_KEY_SQL} = ?"
        params = [mpn_key(candidate)]
        if vendors:
            sql += f" AND manufacturer COLLATE NOCASE IN ({','.join('?' * len(vendors))})"
            params.extend(vendors)
        return parts(conn.execute(sql + " ORDER BY stock DESC", params))

    def matched(results, kind):
        info = {"match": kind, "matched_mpn": results[0]["model"]}
        return results, info

    def find(candidate):
        # 1. Keep the existing exact query and stock ordering unchanged.
        results = parts(conn.execute(
            "SELECT * FROM components WHERE LOWER(mpn) = LOWER(?) ORDER BY stock DESC", [candidate],
        ))
        if results:
            return results, {}

        # 2. Same expression as idx_mpn_key, also correct on older databases.
        results = keyed(candidate)
        if results:
            return matched(results, "separators")

        # 3. Preserve normalize_mpn's existing variant order and exact queries.
        variants = normalize_mpn(candidate)
        for variant in variants[1:]:
            results = parts(conn.execute(
                "SELECT * FROM components WHERE LOWER(mpn) = LOWER(?) ORDER BY stock DESC", [variant],
            ))
            if not results:
                results = keyed(variant)
            if results:
                return matched(results, "packing")

        # The plus names a different radio. FTS tokenization loses it, so this
        # alias must win (or return nothing) before FTS can find the non-plus chip.
        key = mpn_key(candidate)
        if key == "NRF24L01+":
            target, vendors = MPN_ALIASES[key]
            results = keyed(target, vendors)
            return matched(results, "alias") if results else ([], {})

        # 4. Existing FTS queries, variants, stock order and limit are unchanged.
        for variant in variants:
            escaped = variant.replace('"', '""')
            results = parts(conn.execute(
                """SELECT c.* FROM components c
                   JOIN components_fts f ON c.lcsc = f.lcsc
                   WHERE f.components_fts MATCH ?
                   ORDER BY c.stock DESC
                   LIMIT 10""", [f'"{escaped}"*'],
            ))
            if results:
                categories = list(dict.fromkeys(p['subcategory'] or 'Uncategorized' for p in results))
                return results, {
                    "match": "related",
                    "note": (f"No exact match for '{candidate}'. These parts' part numbers start with it "
                             "or their text mentions it, so check the package and manufacturer. "
                             f"Part types: {', '.join(categories)}."),
                }

        # 5. Only the named vendor may supply a packing variant. The indexed
        # prefix narrows retrieval; the full rule must preserve device identity.
        for rule in PACKING_RULES:
            source = rule.pattern.fullmatch(key)
            if source is None:
                continue
            prefix = source['base']
            rows = conn.execute(
                f"SELECT * FROM components WHERE {MPN_KEY_SQL} >= ? AND {MPN_KEY_SQL} < ? "
                f"AND manufacturer COLLATE NOCASE IN ({','.join('?' * len(rule.manufacturers))}) "
                "ORDER BY stock DESC",
                [prefix, prefix + "\uffff", *rule.manufacturers],
            )
            results = parts(row for row in rows
                            if (target := rule.pattern.fullmatch(mpn_key(row['mpn']))) is not None
                            and rule.identity(source) == rule.identity(target))
            if results:
                return matched(results, "packing")

        # 6. Other ordering aliases recover only candidates that also miss FTS.
        if alias := MPN_ALIASES.get(key):
            target, vendors = alias
            results = keyed(target, vendors)
            if results:
                return matched(results, "alias")
        return [], {}

    results, info = find(mpn)
    if not results:
        # 7. First explicitly supplied alternative that matches wins.
        for candidate in annotated_mpn_candidates(mpn):
            results, info = find(candidate)
            if vendors := ALTERNATIVE_MANUFACTURERS.get(mpn_key(candidate)):
                results = [part for part in results if part['manufacturer'] in vendors]
            if results:
                info.update(match="alternative", matched_mpn=candidate)
                break
    if match_info is not None and results:
        match_info.update(info)
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
