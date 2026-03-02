"""Sensor database search — FTS5 + parametric query builder."""

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

# Load IC aliases for query-time resolution (e.g., "sht31" → "sht3x")
_IC_ALIASES: dict[str, str] = {}
_aliases_path = Path(__file__).parent.parent.parent.parent / "data" / "sensors" / "ic_aliases.json"
if _aliases_path.exists():
    _IC_ALIASES = json.loads(_aliases_path.read_text())


# Query-time measure expansions (OR logic — any match)
MEASURE_EXPANSIONS: dict[str, list[str]] = {
    "imu": ["acceleration", "gyroscope", "magnetic_field"],
}

# Query-time measure aliases (rename before searching)
# IMPORTANT: Only alias terms that DON'T exist as real measures in the DB.
# Sub-measures like pir, voc, lidar, tof, ultrasonic, radar exist in the DB
# and should NOT be aliased to their parent — that loses specificity.
MEASURE_QUERY_ALIASES: dict[str, str] = {
    "barometric": "pressure",
    "altimeter": "pressure",
    "barometer": "pressure",
    "range finder": "distance",
    "rangefinder": "distance",
    "encoder": "rotation",
    "carbon monoxide": "co",
    "compass": "magnetic_field",
    "magnetometer": "magnetic_field",
    "accelerometer": "acceleration",
    "gyro": "gyroscope",
    "lux": "light",
    "ambient light": "light",
    "thermometer": "temperature",
    "hygrometer": "humidity",
    "air quality": "gas",
    "dust": "particulate",
    "pm2.5": "particulate",
    "pm10": "particulate",
    "sonar": "ultrasonic",
}

# Protocol aliases (expand to multiple values — OR logic)
PROTOCOL_ALIASES: dict[str, list[str]] = {
    "gpio": ["analog", "digital", "pwm", "one_wire"],
}


# Stop words filtered from FTS queries — too generic to require in AND matching.
# Includes common English stop words + conversational terms LLMs may pass.
_FTS_STOP_WORDS = frozenset({
    # English stop words
    "a", "an", "the", "and", "or", "of", "for", "with", "in", "on", "to", "is",
    "it", "by", "at", "from", "as", "be", "my", "me", "do", "no", "so", "up",
    "if", "am", "are", "was", "has", "have", "had", "not", "but", "can", "will",
    "would", "could", "should", "what", "which", "that", "this", "these", "those",
    "how", "when", "where", "who", "than", "then", "also", "just", "very", "really",
    "any", "some", "about", "like", "into", "over", "such",
    # Sensor search context words (too generic to require)
    "sensor", "sensors", "module", "modules", "board", "chip", "ic", "breakout",
    "give", "find", "show", "get", "list", "all", "best", "good", "recommend",
    "need", "want", "looking", "search", "use", "using", "used", "make", "work",
    "works", "detect", "measure", "monitor", "read", "reading",
})


def _sanitize_fts_query(query: str) -> str:
    """Wrap each term in quotes with prefix matching, AND together.

    Uses FTS5 prefix syntax ("term"*) so "BM22S" matches "BM22S2021",
    "smoke" matches "smokedetector", etc. Filters common stop words that
    would cause false negatives in AND queries.
    """
    clean = query.replace('"', '').replace("'", "")
    terms = clean.split()
    quoted = [f'"{t}"*' for t in terms if len(t) >= 2 and t.lower() not in _FTS_STOP_WORDS]
    return " AND ".join(quoted) if quoted else ""


def _resolve_measure(measure: str) -> tuple[list[str], str]:
    """Resolve a single measure string to actual measure values and mode.

    Returns:
        (measures, mode) where mode is "or" for expansions, "single" otherwise.
    """
    lower = measure.lower().strip()

    # Check expansions first (e.g., "imu" -> multiple measures with OR)
    if lower in MEASURE_EXPANSIONS:
        return MEASURE_EXPANSIONS[lower], "or"

    # Check aliases (rename)
    if lower in MEASURE_QUERY_ALIASES:
        return [MEASURE_QUERY_ALIASES[lower]], "single"

    return [lower], "single"


def search_sensors(
    conn: sqlite3.Connection,
    query: str | None = None,
    measure: str | list[str] | None = None,
    type: str | None = None,
    protocol: str | None = None,
    platform: str | None = None,
    limit: int = 15,
) -> dict[str, Any]:
    """Search sensors with FTS5 + parametric filters.

    Args:
        conn: SQLite connection
        query: Free-text search (FTS5)
        measure: Single measure or list of measures (AND if list)
        type: Sensing technology filter
        protocol: Interface protocol filter
        platform: Platform support filter
        limit: Max results

    Returns:
        {"total": N, "results": [...]}
    """
    # Build query dynamically
    select_cols = "s.id, s.name, s.manufacturer, s.type, s.voltage, s.datasheet_url, s.platform_count, s.description, s.source_tier"
    from_clause = "sensors s"
    where_clauses: list[str] = []
    params: list[Any] = []
    joins: list[str] = []

    # --- Measure filter ---
    if measure is not None:
        if isinstance(measure, str):
            # Single measure (might be expansion or alias)
            resolved, mode = _resolve_measure(measure)
            if mode == "or":
                # Expansion: OR across multiple measures
                placeholders = ", ".join("?" for _ in resolved)
                joins.append("JOIN sensor_measures sm ON sm.sensor_id = s.id")
                where_clauses.append(f"sm.measure IN ({placeholders})")
                params.extend(resolved)
            else:
                # Single resolved measure
                joins.append("JOIN sensor_measures sm ON sm.sensor_id = s.id")
                where_clauses.append("sm.measure = ?")
                params.append(resolved[0])
        elif isinstance(measure, list) and len(measure) == 1:
            # List with single item — same as single string
            resolved, mode = _resolve_measure(measure[0])
            if mode == "or":
                placeholders = ", ".join("?" for _ in resolved)
                joins.append("JOIN sensor_measures sm ON sm.sensor_id = s.id")
                where_clauses.append(f"sm.measure IN ({placeholders})")
                params.extend(resolved)
            else:
                joins.append("JOIN sensor_measures sm ON sm.sensor_id = s.id")
                where_clauses.append("sm.measure = ?")
                params.append(resolved[0])
        elif isinstance(measure, list) and len(measure) > 1:
            # Multiple measures: AND — sensor must have ALL
            resolved_all: list[str] = []
            for m in measure:
                resolved, _ = _resolve_measure(m)
                resolved_all.extend(resolved)
            n = len(resolved_all)
            placeholders = ", ".join("?" for _ in resolved_all)
            joins.append(
                f"JOIN sensor_measures sm ON sm.sensor_id = s.id AND sm.measure IN ({placeholders})"
            )
            params.extend(resolved_all)
            # GROUP BY + HAVING to ensure ALL measures present
            # We'll handle this in the query assembly below
            where_clauses.append(f"1=1")  # placeholder — real filter is HAVING
            # Store for later
            _having_count = n

    # --- Type filter ---
    if type is not None:
        where_clauses.append("s.type = ?")
        params.append(type.lower().strip())

    # --- Protocol filter ---
    if protocol is not None:
        proto_lower = protocol.lower().strip()
        if proto_lower in PROTOCOL_ALIASES:
            expanded = PROTOCOL_ALIASES[proto_lower]
            placeholders = ", ".join("?" for _ in expanded)
            joins.append(f"JOIN sensor_protocols sp ON sp.sensor_id = s.id")
            where_clauses.append(f"sp.protocol IN ({placeholders})")
            params.extend(expanded)
        else:
            joins.append("JOIN sensor_protocols sp ON sp.sensor_id = s.id")
            where_clauses.append("sp.protocol = ?")
            params.append(proto_lower)

    # --- Platform filter ---
    if platform is not None:
        joins.append("JOIN sensor_platforms spl ON spl.sensor_id = s.id")
        where_clauses.append("spl.platform = ?")
        params.append(platform.lower().strip())

    # --- FTS5 query + ID prefix fallback + alias resolution ---
    if query is not None:
        fts_query = _sanitize_fts_query(query)
        if fts_query:
            # Normalize query to an ID-like form for LIKE + alias lookups
            normalized = re.sub(r"[^a-z0-9]", "", query.lower())
            id_pattern = "%" + normalized + "%"

            # Resolve IC aliases (e.g., "SHT31" → "sht3x")
            alias_target = _IC_ALIASES.get(normalized)

            if alias_target:
                where_clauses.append(
                    "(s.id IN (SELECT id FROM sensors_fts WHERE sensors_fts MATCH ?) OR s.id LIKE ? OR s.id = ?)"
                )
                params.append(fts_query)
                params.append(id_pattern)
                params.append(alias_target)
            else:
                where_clauses.append(
                    "(s.id IN (SELECT id FROM sensors_fts WHERE sensors_fts MATCH ?) OR s.id LIKE ?)"
                )
                params.append(fts_query)
                params.append(id_pattern)

    # Assemble SQL
    join_sql = "\n    ".join(joins)
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Exact-match boost: when a query is provided, sensors whose ID matches
    # the normalized query (or its alias target) sort first.
    # e.g., searching "DHT22" puts dht22 above dht11 even if dht11 has more platforms.
    order_boost = ""
    order_boost_params: list[Any] = []
    if query is not None:
        normalized = re.sub(r"[^a-z0-9]", "", query.lower())
        alias_target = _IC_ALIASES.get(normalized)
        if alias_target:
            order_boost = "CASE WHEN s.id = ? OR s.id = ? THEN 0 ELSE 1 END, "
            order_boost_params = [normalized, alias_target]
        elif normalized:
            order_boost = "CASE WHEN s.id = ? THEN 0 ELSE 1 END, "
            order_boost_params = [normalized]

    order_by = f"ORDER BY {order_boost}s.platform_count DESC, s.name ASC"

    # Check if we need GROUP BY for multi-measure AND
    need_group_by = (
        isinstance(measure, list) and len(measure) > 1
    )

    if need_group_by:
        count_sql = f"""
            SELECT COUNT(*) FROM (
                SELECT s.id
                FROM {from_clause}
                {join_sql}
                WHERE {where_sql}
                GROUP BY s.id
                HAVING COUNT(DISTINCT sm.measure) = ?
            )
        """
        count_params = params + [len(measure)]

        data_sql = f"""
            SELECT {select_cols}
            FROM {from_clause}
            {join_sql}
            WHERE {where_sql}
            GROUP BY s.id
            HAVING COUNT(DISTINCT sm.measure) = ?
            {order_by}
            LIMIT ?
        """
        data_params = params + [len(measure)] + order_boost_params + [limit]
    else:
        count_sql = f"""
            SELECT COUNT(DISTINCT s.id)
            FROM {from_clause}
            {join_sql}
            WHERE {where_sql}
        """
        count_params = params

        data_sql = f"""
            SELECT DISTINCT {select_cols}
            FROM {from_clause}
            {join_sql}
            WHERE {where_sql}
            {order_by}
            LIMIT ?
        """
        data_params = params + order_boost_params + [limit]

    # Execute count
    total = conn.execute(count_sql, count_params).fetchone()[0]

    # Execute data query
    rows = conn.execute(data_sql, data_params).fetchall()

    # Build results with junction table data
    results = []
    for row in rows:
        sensor_id = row[0]

        measures = [r[0] for r in conn.execute(
            "SELECT measure FROM sensor_measures WHERE sensor_id = ? ORDER BY measure", (sensor_id,)
        )]
        protocols = [r[0] for r in conn.execute(
            "SELECT protocol FROM sensor_protocols WHERE sensor_id = ? ORDER BY protocol", (sensor_id,)
        )]
        platforms = [r[0] for r in conn.execute(
            "SELECT platform FROM sensor_platforms WHERE sensor_id = ? ORDER BY platform", (sensor_id,)
        )]
        urls = [r[0] for r in conn.execute(
            "SELECT url FROM sensor_urls WHERE sensor_id = ? ORDER BY url", (sensor_id,)
        )]

        results.append({
            "id": row[0],
            "name": row[1],
            "manufacturer": row[2],
            "type": row[3],
            "voltage": row[4],
            "datasheet_url": row[5],
            "platform_count": row[6],
            "description": row[7],
            "source_tier": row[8],
            "measures": measures,
            "protocols": protocols,
            "platforms": platforms,
            "urls": urls,
        })

    return {"total": total, "results": results}
