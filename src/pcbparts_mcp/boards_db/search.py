"""Boards database search — FTS5 + parametric query builder."""

import sqlite3
from typing import Any


def _escape_like(value: str) -> str:
    """Escape LIKE wildcard characters in user input."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _source_url(source: str | None) -> str | None:
    """Build GitHub URL from source field."""
    return f"https://github.com/{source}" if source else None


# Stop words filtered from FTS queries
_FTS_STOP_WORDS = frozenset({
    # English stop words
    "a", "an", "the", "and", "or", "of", "for", "with", "in", "on", "to", "is",
    "it", "by", "at", "from", "as", "be", "my", "me", "do", "no", "so", "up",
    "if", "am", "are", "was", "has", "have", "had", "not", "but", "will",
    # NOTE: "can" omitted — it's the CAN bus protocol acronym
    "would", "could", "should", "what", "which", "that", "this", "these", "those",
    "how", "when", "where", "who", "than", "then", "also", "just", "very", "really",
    "any", "some", "about", "like", "into", "over", "such",
    # Board search context — too generic as AND requirements
    "board", "boards", "design", "circuit", "schematic", "pcb",
    "reference", "find", "show", "get", "list", "using",
    "project", "open", "source", "hardware",
    # EE domain words — appear in nearly every board, hurt AND precision
    # NOTE: "power", "supply", "driver", "controller" kept OUT — useful in queries like
    #   "USB power delivery", "motor driver", "flight controller", "power supply"
    # "regulator" and "converter" ARE stop words — too generic in EE context,
    #   "buck converter" → just "buck" works better than requiring both
    "voltage", "regulator", "converter",
    "output", "input", "signal", "interface",
    "module", "chip", "defined", "panel", "software",
})

# FTS5 bm25 column weights (higher = more important when ranking).
# Column order: slug, name, description, key_coverage, tags_text, key_ics_text, all_ics_text, org_display
_BM25_WEIGHTS = "10.0, 10.0, 5.0, 5.0, 8.0, 8.0, 3.0, 4.0"

# Query-time term aliases: handle concatenated forms, common synonyms,
# and hyphen mismatches (unicode61 splits on hyphens).
_TERM_ALIASES: dict[str, str] = {
    # Concatenated → hyphenated (unicode61 splits hyphens into sub-tokens)
    "eink": "e-ink",
    "epaper": "e-paper",
    "ebike": "e-bike",
    "esp32s3": "ESP32-S3",
    "esp32c3": "ESP32-C3",
    "esp32c6": "ESP32-C6",
    "esp32s2": "ESP32-S2",
    "nrf52": "nRF52",
    "rs485": "RS-485",
    "rs232": "RS-232",
    "usbc": "USB-C",
    # Synonym expansions
    "bluetooth": "BLE",
    "ble": "BLE",
    "opamp": "op-amp",
    "mosfet": "FET",
    "synthesizer": "synth",
    "oscilloscope": "scope",
    "brushless": "BLDC",
    "accelerometer": "IMU",
    "gyroscope": "IMU",
    "modbus": "RS-485",
    "amplifier": "amp",
    "thermocouple": "thermocouple",  # passthrough — prevent stop word matching
    "lipo": "battery",
    "neopixel": "WS2812",
    "addressable": "WS2812",
    "quadcopter": "drone",
    # Additional EE terms AI models commonly use
    "servo": "motor",
    "stepper": "stepper",  # passthrough — keep as search term
    "h-bridge": "H-bridge",
    "hbridge": "H-bridge",
    "lidar": "LIDAR",
    "rtc": "RTC",
    "zigbee": "Zigbee",
    "ethernet": "ethernet",  # passthrough
    "oled": "OLED",
    "tft": "TFT",
    "sdcard": "SD-card",
    "microsd": "SD-card",
}

# Multi-term synonym groups: all forms expand to an OR query.
# Key can be any form; value is list of FTS sub-tokens to OR together.
_SYNONYM_GROUPS: dict[str, list[str]] = {
    # e-ink / e-paper / EPD are all the same display technology
    # Include all input forms (concatenated, hyphenated, abbreviated)
    "e-ink": ["ink", "paper", "EPD", "eink"],
    "e-paper": ["ink", "paper", "EPD", "eink"],
    "epd": ["ink", "paper", "EPD", "eink"],
    "eink": ["ink", "paper", "EPD", "eink"],
    "epaper": ["ink", "paper", "EPD", "eink"],
}


def _sanitize_fts_query(query: str) -> str:
    """Build FTS5 query from user input.

    - Strips quotes
    - Splits on whitespace
    - Resolves aliases (e.g., "eink" → "e-ink", "bluetooth" → "BLE")
    - Splits hyphenated terms into sub-tokens (matches unicode61 tokenizer)
    - Wraps terms in quotes with prefix matching ("term"*)
    - ANDs all terms together
    - Filters stop words
    """
    clean = query.replace('"', '').replace("'", "")

    # Split on whitespace, expand aliases and hyphenated terms
    raw_terms = clean.split()
    parts_list: list[str] = []  # Each entry is a single FTS fragment or OR group
    for t in raw_terms:
        if len(t) < 2 or t.lower() in _FTS_STOP_WORDS:
            continue

        # Check synonym groups first (e.g., "e-ink" → OR group of all display terms)
        t_lower = t.lower()
        # For hyphenated input, also check the joined form
        joined = t_lower.replace("-", "")
        syn_group = _SYNONYM_GROUPS.get(t_lower) or _SYNONYM_GROUPS.get(joined)
        if syn_group:
            # Build OR group: ("ink"* OR "paper"* OR "EPD"* OR "eink"*)
            or_parts = " OR ".join(f'"{s}"*' for s in syn_group)
            parts_list.append(f"({or_parts})")
            continue

        # Check simple aliases (e.g., "eink" → "e-ink", "bluetooth" → "BLE")
        alias = _TERM_ALIASES.get(t_lower)
        if alias:
            t = alias
        if "-" in t:
            # Hyphenated: add each sub-part (unicode61 tokenizer splits on hyphens)
            sub_parts = [p for p in t.split("-") if len(p) >= 2 and p.lower() not in _FTS_STOP_WORDS]
            for p in sub_parts:
                # Short terms (<=3 chars): exact match to avoid false positives
                # (e.g., "TVS" matching "TV", "CAN" matching "CANDLE")
                parts_list.append(f'"{p}"' if len(p) <= 3 else f'"{p}"*')
        else:
            parts_list.append(f'"{t}"' if len(t) <= 3 else f'"{t}"*')

    # Deduplicate (e.g., "accelerometer gyroscope" → both alias to "IMU")
    seen: set[str] = set()
    unique: list[str] = []
    for p in parts_list:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return " AND ".join(unique) if unique else ""


def search_boards(
    conn: sqlite3.Connection,
    query: str | None = None,
    component: str | None = None,
    tag: str | list[str] | None = None,
    org: str | None = None,
    layers: int | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Search boards with FTS5 + parametric filters.

    Args:
        conn: SQLite connection
        query: Free-text search (FTS5, with LIKE fallback on IC columns)
        component: Find boards using a specific IC/part (checks key_ics then components)
        tag: Tag filter (single or list for AND)
        org: Organization filter (matches org slug or org_display, case-insensitive)
        layers: Layer count filter
        limit: Max results

    Returns:
        {"total": N, "results": [...]}
    """
    # Normalize empty strings to None
    if query is not None and not query.strip():
        query = None
    if component is not None and not component.strip():
        component = None
    if org is not None and not org.strip():
        org = None

    select_cols = (
        "b.id, b.slug, b.name, b.org, b.org_display, b.source, b.format, "
        "b.description, b.key_coverage, b.layers, b.width_mm, b.height_mm, "
        "b.component_count, b.ic_count"
    )
    from_clause = "boards b"
    where_clauses: list[str] = []
    params: list[Any] = []
    joins: list[str] = []

    # Track query modes for ranking
    has_fts = False
    component_boost = False

    # --- Tag filter ---
    if tag is not None:
        tags = [tag] if isinstance(tag, str) else tag[:10]
        for i, t in enumerate(tags):
            alias = f"bt{i}"
            joins.append(f"JOIN board_tags {alias} ON {alias}.board_id = b.id AND {alias}.tag = ?")
            params.append(t)

    # --- Org filter ---
    if org is not None:
        where_clauses.append("(b.org = ? COLLATE NOCASE OR b.org_display = ? COLLATE NOCASE)")
        params.extend([org, org])

    # --- Layers filter ---
    if layers is not None:
        where_clauses.append("b.layers = ?")
        params.append(layers)

    # --- Component search ---
    if component is not None:
        component_boost = True
        comp_pattern = f"%{_escape_like(component)}%"
        where_clauses.append(
            "(b.id IN (SELECT board_id FROM board_key_ics WHERE ic LIKE ? ESCAPE '\\') "
            "OR b.id IN (SELECT board_id FROM board_components WHERE value LIKE ? ESCAPE '\\'))"
        )
        params.extend([comp_pattern, comp_pattern])

    # --- FTS5 query with LIKE fallback ---
    fts_query = None
    if query is not None:
        fts_query = _sanitize_fts_query(query)
        if fts_query:
            has_fts = True
            # FTS match OR LIKE fallback on IC text columns (catches mid-word matches
            # like "SAMD21" in "ATSAMD21G18" that FTS prefix can't find)
            like_pattern = f"%{_escape_like(query.strip())}%"
            where_clauses.append(
                "(b.slug IN (SELECT slug FROM boards_fts WHERE boards_fts MATCH ?) "
                "OR b.key_ics_text LIKE ? ESCAPE '\\' OR b.all_ics_text LIKE ? ESCAPE '\\')"
            )
            params.extend([fts_query, like_pattern, like_pattern])

    # Assemble SQL
    join_sql = "\n    ".join(joins)
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # --- Ranking ---
    # FTS queries: rank by bm25 relevance (primary), component_count (tiebreaker)
    # Component queries: key_ic boost, then component_count
    # Parametric only: component_count
    order_parts = []
    order_params: list[Any] = []

    if has_fts and fts_query:
        # bm25() returns negative values (closer to 0 = better match)
        # Use COALESCE for rows that matched via LIKE fallback (no FTS rank)
        order_parts.append(
            "COALESCE((SELECT bm25(boards_fts, " + _BM25_WEIGHTS + ") "
            "FROM boards_fts WHERE boards_fts MATCH ? AND boards_fts.slug = b.slug), 0)"
        )
        order_params.append(fts_query)

    if component_boost and component:
        comp_pattern = f"%{_escape_like(component)}%"
        order_parts.append(
            "CASE WHEN b.id IN (SELECT board_id FROM board_key_ics WHERE ic LIKE ? ESCAPE '\\') THEN 0 ELSE 1 END"
        )
        order_params.append(comp_pattern)

    order_parts.append("b.component_count DESC")
    order_parts.append("b.name ASC")
    order_by = f"ORDER BY {', '.join(order_parts)}"

    data_sql = f"""
        SELECT DISTINCT {select_cols}
        FROM {from_clause}
        {join_sql}
        WHERE {where_sql}
        {order_by}
        LIMIT ?
    """

    try:
        rows = conn.execute(data_sql, params + order_params + [limit]).fetchall()
    except sqlite3.OperationalError:
        # Malformed FTS query — fall back to empty results
        return {"total": 0, "results": []}

    # Defer COUNT query: skip it when we know the total from the data query
    if len(rows) < limit:
        total = len(rows)
    else:
        count_sql = f"""
            SELECT COUNT(DISTINCT b.id)
            FROM {from_clause}
            {join_sql}
            WHERE {where_sql}
        """
        total = conn.execute(count_sql, params).fetchone()[0]

    if not rows:
        return {"total": total, "results": []}

    # Batch-fetch tags and key_ics for all result board_ids (avoids N+1)
    board_ids = [row[0] for row in rows]
    placeholders = ",".join("?" for _ in board_ids)

    tags_by_board: dict[int, list[str]] = {}
    for r in conn.execute(
        f"SELECT board_id, tag FROM board_tags WHERE board_id IN ({placeholders}) ORDER BY tag",
        board_ids,
    ):
        tags_by_board.setdefault(r[0], []).append(r[1])

    ics_by_board: dict[int, list[str]] = {}
    for r in conn.execute(
        f"SELECT board_id, ic FROM board_key_ics WHERE board_id IN ({placeholders}) ORDER BY ic",
        board_ids,
    ):
        ics_by_board.setdefault(r[0], []).append(r[1])

    # Build match hints — tell the AI WHY each board matched
    # Pre-compute component match type per board (key_ic vs component value)
    key_ic_match_ids: set[int] = set()
    comp_val_match_ids: set[int] = set()
    if component:
        comp_pattern = f"%{_escape_like(component)}%"
        for (bid,) in conn.execute(
            f"SELECT board_id FROM board_key_ics WHERE ic LIKE ? ESCAPE '\\' AND board_id IN ({placeholders})",
            [comp_pattern] + board_ids,
        ):
            key_ic_match_ids.add(bid)
        for (bid,) in conn.execute(
            f"SELECT DISTINCT board_id FROM board_components WHERE value LIKE ? ESCAPE '\\' AND board_id IN ({placeholders})",
            [comp_pattern] + board_ids,
        ):
            comp_val_match_ids.add(bid)

    # Build results
    results = []
    for row in rows:
        board_id = row[0]
        source = row[5]

        # Build match_hints: concise explanation of why this board appeared
        hints: list[str] = []
        if component:
            if board_id in key_ic_match_ids:
                hints.append(f"key IC: {component}")
            elif board_id in comp_val_match_ids:
                hints.append(f"component: {component}")
        if has_fts:
            hints.append("text match")
        if tag is not None:
            tag_list = [tag] if isinstance(tag, str) else tag
            hints.append(f"tag: {', '.join(tag_list)}")
        if org is not None:
            hints.append(f"org: {org}")
        if layers is not None:
            hints.append(f"layers: {layers}")

        entry: dict[str, Any] = {
            "slug": row[1],
            "name": row[2],
            "org": row[3],
            "org_display": row[4],
            "source": source,
            "source_url": _source_url(source),
            "format": row[6],
            "description": row[7],
            "key_coverage": row[8],
            "tags": tags_by_board.get(board_id, []),
            "key_ics": ics_by_board.get(board_id, []),
            "layers": row[9],
            "width_mm": row[10],
            "height_mm": row[11],
            "component_count": row[12],
            "ic_count": row[13],
        }
        if hints:
            entry["matched_by"] = hints
        results.append(entry)

    return {"total": total, "results": results}
