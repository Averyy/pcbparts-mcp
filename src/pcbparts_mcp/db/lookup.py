"""Component lookup functions for the database."""

import sqlite3
from collections.abc import Callable
from itertools import islice
from typing import Any

from ..catalog_files import unpack_tiers
from ..mounting import detect_mounting_type
from ..search.result import row_to_dict
from ..search.mpn import (
    ALTERNATIVE_MANUFACTURERS, LCSC_CODE, MPN_ALIASES, MPN_KEY_SQL, PACKING_RULES,
    annotated_mpn_candidates, is_maker_suffixed, is_placeholder_mpn, mpn_key, normalize_mpn,
)


# match_info's private key (never in a reply: callers drop keys starting with "_"): an
# "alternative" match whose annotated candidate itself matched only by full text ("related"), so
# the parts are full-text guesses although match says alternative
VIA = "_via"


def get_by_mpn(
    conn: sqlite3.Connection,
    mpn: str,
    subcategories: dict[int, dict[str, Any]],
    *,
    match_info: dict[str, Any] | None = None,
    sold_out: bool = False,
    full_text: bool = True,
    maker: Callable[[str | None], bool] | None = None,
) -> list[dict[str, Any]]:
    """Find an MPN, preserving exact/normalized/FTS precedence within a candidate.

    Additional recoveries compare separator keys and curated vendor packing or
    ordering aliases. Only after the full input misses are annotations and
    alternatives tried. Optional reply metadata leaves list callers unchanged.
    sold_out=True looks in the parts kept after they left the snapshot instead (sold_out_part rows, most
    stock when last listed first), by the same rules except full-text search, which they're outside.
    full_text=False leaves out full-text search too (jlc_get_parts: sure matches only).
    maker: which manufacturer names to keep (jlc_get_parts' maker given). Each step keeps only those
    makers' parts before deciding it matched, so another maker's exact match doesn't hide this
    maker's own spelling ("1N4007G" from Comchip is its "1N4007-G"); full text keeps 10 of them.
    match_info[VIA] = "related" marks an alternative found by full text (private: see VIA).
    """
    if match_info is not None:
        match_info.clear()
    mpn = mpn.strip()
    if not mpn:
        return []
    table, order = ("sold_out", "last_stock DESC, lcsc") if sold_out else ("components", "stock DESC, lcsc")
    to_dict = sold_out_part if sold_out else row_to_dict

    def parts(rows):
        unique = {}
        for row in rows:
            if row["lcsc"] not in unique and (maker is None or maker(row["manufacturer"])):
                unique[row["lcsc"]] = to_dict(row, subcategories)
        return list(unique.values())

    def keyed(candidate, vendors=()):
        sql = f"SELECT * FROM {table} WHERE {MPN_KEY_SQL} = ?"
        params = [mpn_key(candidate)]
        if vendors:
            sql += f" AND manufacturer COLLATE NOCASE IN ({','.join('?' * len(vendors))})"
            params.extend(vendors)
        return parts(conn.execute(sql + f" ORDER BY {order}", params))

    def matched(results, kind):
        info = {"match": kind, "matched_mpn": results[0]["model"]}
        return results, info

    # A placeholder names no part: only a part actually numbered that way, never
    # full-text matches or alternatives.
    if is_placeholder_mpn(mpn):
        return parts(conn.execute(
            f"SELECT * FROM {table} WHERE LOWER(mpn) = LOWER(?) ORDER BY {order}", [mpn],
        ))

    def find(candidate):
        # 1. Keep the existing exact query and stock ordering unchanged.
        results = parts(conn.execute(
            f"SELECT * FROM {table} WHERE LOWER(mpn) = LOWER(?) ORDER BY {order}", [candidate],
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
                f"SELECT * FROM {table} WHERE LOWER(mpn) = LOWER(?) ORDER BY {order}", [variant],
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

        # An LCSC code passed as an MPN finds that part, not parts whose codes start with it.
        lcsc_code = LCSC_CODE.fullmatch(candidate) is not None
        if lcsc_code:
            results = parts(conn.execute(f"SELECT * FROM {table} WHERE lcsc = ?", [candidate.upper()]))
            if results:
                info = matched(results, "lcsc")[1]
                info["note"] = (f"'{candidate}' is an LCSC code, not a part number; this is that part. "
                                f"jlc_get_part(lcsc=\"{candidate.upper()}\") adds live stock and prices, "
                                "the datasheet and EasyEDA footprint status.")
                return results, info

        # 4. Existing FTS queries, variants, stock order and limit are unchanged,
        # except that an LCSC-shaped input doesn't match other parts' LCSC codes.
        for variant in () if sold_out or not full_text else variants:
            escaped = variant.replace('"', '""')
            columns = "{mpn manufacturer description} : " if lcsc_code else ""
            rows = conn.execute(
                """SELECT c.* FROM components c
                   JOIN components_fts f ON c.lcsc = f.lcsc
                   WHERE f.components_fts MATCH ?
                   ORDER BY c.stock DESC, c.lcsc""" + ("" if maker else "\n                   LIMIT 10"),
                [f'{columns}"{escaped}"*'],
            )
            # The maker's first 10, not the first 10 of every maker narrowed down
            results = parts(islice((row for row in rows if maker(row["manufacturer"])), 10) if maker else rows)
            if results:
                return results, {"match": "related", "note": related_note(
                    results, f"No exact match for '{candidate}'. These parts' part numbers start with it "
                             "or their text mentions it, so check the package and manufacturer.")}

        # 5. Only the named vendor may supply a packing variant. The indexed
        # prefix narrows retrieval; the full rule must preserve device identity.
        for rule in PACKING_RULES:
            source = rule.pattern.fullmatch(key)
            if source is None:
                continue
            prefix = source['base']
            rows = conn.execute(
                f"SELECT * FROM {table} WHERE {MPN_KEY_SQL} >= ? AND {MPN_KEY_SQL} < ? "
                f"AND manufacturer COLLATE NOCASE IN ({','.join('?' * len(rule.manufacturers))}) "
                f"ORDER BY {order}",
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
                if info.get("match") == "related":
                    info[VIA] = "related"
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


def snapshot_prices(price: float | None, tiers: str | None) -> list[dict[str, Any]] | None:
    """A snapshot part's prices in jlc_get_part's shape ([{"qty": "100+", "price": ...}]): the daily
    scrape's price breaks (price_tiers, pack_tiers text), less trailing breaks that only repeat the
    price before them; without breaks, the 1-piece price as the one tier, "1+" (the weekly price,
    as of prices_as_of); None when the part has no price at all."""
    if tiers:
        breaks = unpack_tiers(tiers)
        while len(breaks) > 1 and breaks[-1][1] == breaks[-2][1]:
            breaks.pop()
        return [{"qty": f"{qty}+", "price": value} for qty, value in breaks]
    if price is not None:
        return [{"qty": "1+", "price": price}]
    return None


def get_price_tiers(conn: sqlite3.Connection, codes: list[str]) -> dict[str, str]:
    """price_tiers rows for these LCSC codes, in chunks under SQLite's variable limit."""
    found: dict[str, str] = {}
    for start in range(0, len(codes), 500):
        chunk = codes[start:start + 500]
        found.update(conn.execute(
            f"SELECT lcsc, tiers FROM price_tiers WHERE lcsc IN ({','.join('?' * len(chunk))})", chunk))
    return found


def add_snapshot_prices(conn: sqlite3.Connection, parts: list[dict[str, Any]], with_tiers: bool) -> list[dict[str, Any]]:
    """row_to_dict parts with prices (snapshot_prices) right after price, where the part has one.
    with_tiers: the database has price breaks loaded (ComponentDatabase.price_tiers_as_of)."""
    tiers = get_price_tiers(conn, list(dict.fromkeys(p["lcsc"] for p in parts))) if with_tiers and parts else {}
    priced = []
    for part in parts:
        prices = snapshot_prices(part.get("price"), tiers.get(part["lcsc"]))
        if prices is None:
            priced.append(part)
            continue
        with_prices: dict[str, Any] = {}
        for key, value in part.items():
            with_prices[key] = value
            if key == "price":
                with_prices["prices"] = prices
        priced.append(with_prices)
    return priced


def snapshot_row(row: sqlite3.Row, subcategories: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """A part as jlc_get_parts lists it: jlc_get_part's field names and price shape for what the
    snapshot holds, without specs, datasheet links or EasyEDA status (jlc_get_part has those).
    prices lists the daily scrape's price breaks when the row has them (price_tiers, joined in by
    get_snapshot_rows), else the 1-piece price as its one tier (snapshot_prices)."""
    part = row_to_dict(row, subcategories)
    row_part = {key: part[key] for key in ("lcsc", "model", "manufacturer", "package", "stock", "price")}
    prices = snapshot_prices(part["price"], row["price_tiers"] if "price_tiers" in row.keys() else None)
    if prices is not None:
        row_part["prices"] = prices
    row_part.update((key, part[key]) for key in ("library_type", "preferred", "pcba_type", "category", "subcategory")
                    if key in part)
    row_part["description"] = row["description"]  # row_to_dict leaves it out when specs are listed
    if part.get("no_datasheet"):
        row_part["no_datasheet"] = True
    return row_part


def related_note(results: list[dict[str, Any]], lead: str) -> str:
    """The note on full-text ("related") results: lead (what they are), their part types, and the
    parts among them numbered after the original by another maker."""
    categories = list(dict.fromkeys(p['subcategory'] or 'Uncategorized' for p in results))
    note = f"{lead} Part types: {', '.join(categories)}."
    if copies := [p for p in results if is_maker_suffixed(p)]:
        names = ", ".join(f"{p['model']} ({p['manufacturer']})" for p in copies[:3])
        note += (f" {names} {'is' if len(copies) == 1 else 'are'} numbered after the "
                 "original part but made by another manufacturer; check "
                 f"{'its datasheet' if len(copies) == 1 else 'their datasheets'} "
                 "before substituting.")
    return note


def sold_out_part(row: sqlite3.Row, subcategories: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """A part kept after it left the snapshot (the sold_out table: a scrape no longer lists it, so
    its stock fell under 10 or JLCPCB stopped listing it) in row_to_dict's shape for what is kept:
    stock unknown (None) and no specs, plus gone, gone_since (the UTC date of the first daily
    scrape it was missing from) and last_stock (its stock in the last scrape that listed it). price
    is the last 1-piece price the snapshot had for it (prices.tsv, refreshed weekly: it can be up to
    a week older than last_stock)."""
    library_type = {"b": "basic", "p": "preferred", "e": "extended"}.get(row["library_type"], row["library_type"])
    subcategory_info = subcategories.get(row["subcategory_id"], {})
    category, subcategory = subcategory_info.get("category_name"), subcategory_info.get("name")
    return {
        "lcsc": row["lcsc"],
        "model": row["mpn"],
        "manufacturer": row["manufacturer"],
        "package": row["package"],
        "stock": None,
        "price": row["price"],
        "library_type": library_type,
        "preferred": library_type == "preferred",
        "category": category,
        "subcategory": subcategory,
        "subcategory_id": row["subcategory_id"],
        "mounting_type": detect_mounting_type(row["package"], category=category, subcategory=subcategory),
        "description": row["description"],
        "gone": True,
        "gone_since": row["gone_since"],
        "last_stock": row["last_stock"],
    }


# jlc_get_parts' gone rows: snapshot_row's fields (prices after price) and the gone ones
_SOLD_OUT_ROW_KEYS = ("lcsc", "model", "manufacturer", "package", "stock", "price", "library_type", "preferred",
                      "category", "subcategory", "description", "gone", "gone_since", "last_stock")


def get_sold_out_rows(
    conn: sqlite3.Connection,
    lcsc_codes: list[str],
    subcategories: dict[int, dict[str, Any]],
) -> dict[str, dict[str, Any] | None]:
    """Sold-out parts for LCSC codes (upper-cased, de-duplicated, in order) in one query, as
    jlc_get_parts lists them (snapshot_row's fields, stock None, prices the last 1-piece price, plus
    gone, gone_since and last_stock); None for codes not kept. Raises ValueError beyond
    MAX_BATCH_SIZE codes."""
    codes = list(dict.fromkeys(code.upper() for code in lcsc_codes))
    if len(codes) > MAX_BATCH_SIZE:
        raise ValueError(f"Batch size {len(codes)} exceeds maximum of {MAX_BATCH_SIZE}. Split into smaller batches.")
    results: dict[str, dict[str, Any] | None] = dict.fromkeys(codes)
    if codes:
        for row in conn.execute(f"SELECT * FROM sold_out WHERE lcsc IN ({','.join('?' * len(codes))})", codes):
            part = sold_out_part(row, subcategories)
            listed = {key: part[key] for key in _SOLD_OUT_ROW_KEYS[:6]}
            # One tier at most, never breaks: a client (Backplane's hub) checks a part with one break
            # or fewer live by its lcsc, which is what a gone part's unknown stock needs
            if (prices := snapshot_prices(part["price"], None)) is not None:
                listed["prices"] = prices
            listed.update((key, part[key]) for key in _SOLD_OUT_ROW_KEYS[6:])
            results[row["lcsc"]] = listed
    return results


def get_snapshot_rows(
    conn: sqlite3.Connection,
    lcsc_codes: list[str],
    subcategories: dict[int, dict[str, Any]],
    *,
    with_tiers: bool = False,
) -> dict[str, dict[str, Any] | None]:
    """snapshot_row() for each LCSC code (upper-cased, de-duplicated, in order) in one query; None
    for codes the snapshot doesn't list. with_tiers joins in the price breaks (a database with
    price_tiers loaded). Raises ValueError beyond MAX_BATCH_SIZE codes."""
    codes = list(dict.fromkeys(code.upper() for code in lcsc_codes))
    if len(codes) > MAX_BATCH_SIZE:
        raise ValueError(f"Batch size {len(codes)} exceeds maximum of {MAX_BATCH_SIZE}. Split into smaller batches.")
    results: dict[str, dict[str, Any] | None] = dict.fromkeys(codes)
    if codes:
        placeholders = ",".join("?" * len(codes))
        sql = (f"SELECT c.*, t.tiers AS price_tiers FROM components c LEFT JOIN price_tiers t ON t.lcsc = c.lcsc "
               f"WHERE c.lcsc IN ({placeholders})") if with_tiers else (
            f"SELECT * FROM components WHERE lcsc IN ({placeholders})")
        for row in conn.execute(sql, codes):
            results[row["lcsc"]] = snapshot_row(row, subcategories)
    return results


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
