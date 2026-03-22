"""Board detail retrieval — get_board, get_consensus, get_tag_consensus.

Extracted from __init__.py to keep module sizes manageable.
All functions accept a sqlite3.Connection and return dicts.
"""

import json
import re
import sqlite3
from collections import Counter
from typing import Any

from .search import _escape_like, _source_url

# Ref prefixes that are plain passives (R, C, L, RN, etc.)
# Everything else (U, IC, J, P, X, D, LED, Q, S, F, B, ...) is kept in default view
_PASSIVE_PREFIXES = frozenset({"R", "C", "L", "RN", "FB"})

# Map bare component values (parse failures) to readable names
_JUNK_MAP = {"R": "resistor", "C": "capacitor", "L": "inductor",
             "D": "diode", "F": "fuse", "FB": "ferrite bead"}


def _match_focus(
    neighborhoods: list[dict],
    focus: str,
) -> tuple[dict | None, str | None, list[dict]]:
    """Match a focus term against IC neighborhoods.

    Returns (matched_hood, match_type, partial_matches).
    match_type is "ref", "exact", or "partial".
    partial_matches is populated only when match_type == "partial".
    """
    focus_lower = focus.lower()
    matched = None
    match_type = None
    partial_matches: list[dict] = []

    # Pass 1: check ref match (highest priority)
    for hood in neighborhoods:
        if hood["ref"].lower() == focus_lower:
            return hood, "ref", []

    # Pass 2: check exact value match
    for hood in neighborhoods:
        if hood["value"].lower() == focus_lower:
            return hood, "exact", []

    # Pass 3: check partial value match (collect all for alternatives)
    for hood in neighborhoods:
        val_lower = hood["value"].lower()
        if focus_lower in val_lower or val_lower in focus_lower:
            partial_matches.append(hood)
    if partial_matches:
        matched = partial_matches[0]
        match_type = "partial"

    return matched, match_type, partial_matches


def _clean_junk_values(pins: dict[str, list]) -> dict[str, list]:
    """Clean junk values in neighborhood pins (bare 'R'/'C'/'L' from parse failures)."""
    cleaned: dict[str, list] = {}
    for pin_name, components in pins.items():
        cleaned[pin_name] = [
            {**c, "value": _JUNK_MAP[c["value"]]} if c["value"] in _JUNK_MAP else c
            for c in components
        ]
    return cleaned


def _filter_components(
    conn: sqlite3.Connection,
    board_id: int,
    include_bom: bool,
) -> tuple[list[dict], int]:
    """Fetch and filter board components.

    Returns (components_list, passives_omitted_count).
    passives_omitted_count is 0 when include_bom is True.
    """
    all_components = [
        {
            "ref": r[0], "value": r[1], "footprint": r[2], "description": r[3],
            "voltage": r[4], "tolerance": r[5], "dielectric": r[6],
            "decouples": r[7], "pullup": r[8], "pulldown": r[9],
        }
        for r in conn.execute(
            """SELECT ref, value, footprint, description, voltage, tolerance,
                      dielectric, decouples, pullup, pulldown
               FROM board_components WHERE board_id = ? ORDER BY ref""",
            (board_id,),
        )
    ]
    all_components = [{k: v for k, v in c.items() if v is not None} for c in all_components]

    if include_bom:
        return all_components, 0

    # Filter: keep ICs, connectors, LEDs, etc. + annotated passives
    filtered = []
    for c in all_components:
        prefix = re.match(r"[A-Za-z]+", c["ref"])
        prefix_str = prefix.group() if prefix else ""
        is_passive = prefix_str in _PASSIVE_PREFIXES
        has_annotation = any(k in c for k in ("decouples", "pullup", "pulldown"))
        if not is_passive or has_annotation:
            filtered.append(c)
    omitted = len(all_components) - len(filtered)
    return filtered, omitted


def _enrich_neighborhoods(
    conn: sqlite3.Connection,
    board_id: int,
    neighborhoods: list[dict],
) -> list[dict]:
    """Build neighborhood summaries enriched with IC descriptions."""
    ic_refs = [h["ref"] for h in neighborhoods]
    ic_descriptions: dict[str, str] = {}
    if ic_refs:
        placeholders = ",".join("?" for _ in ic_refs)
        for ref, desc in conn.execute(
            f"SELECT ref, description FROM board_components WHERE board_id = ? AND ref IN ({placeholders})",
            [board_id] + ic_refs,
        ):
            if desc:
                ic_descriptions[ref] = desc

    result = []
    for h in neighborhoods:
        entry: dict[str, Any] = {
            "ref": h["ref"],
            "value": h["value"],
            "pin_count": len(h["pins"]),
        }
        desc = ic_descriptions.get(h["ref"])
        if desc:
            entry["description"] = desc
        result.append(entry)
    return result


def get_board(
    conn: sqlite3.Connection,
    slug: str,
    include_raw: bool = False,
    include_bom: bool = False,
    focus: str | None = None,
    get_consensus_fn: Any = None,
) -> dict[str, Any] | None:
    """Get board detail by slug.

    Args:
        conn: SQLite connection
        slug: Board slug identifier
        include_raw: Include full nets/positions/copper_pours JSON
        include_bom: Include every component (all passives)
        focus: IC name or ref to focus on
        get_consensus_fn: Callable(ic_name) -> dict|None for cross-board consensus
    """
    cols = (
        "id, slug, name, org, org_display, source, format, description, key_coverage, "
        "layers, width_mm, height_mm, min_trace, min_clearance, min_drill, min_via, "
        "component_count, ic_count, net_count, neighborhoods_json"
    )
    if include_raw:
        cols += ", nets_json, positions_json, copper_pours_json"

    cur = conn.cursor()
    cur.row_factory = sqlite3.Row
    row = cur.execute(f"SELECT {cols} FROM boards WHERE slug = ?", (slug,)).fetchone()
    cur.close()
    if not row:
        return None

    tags = [r[0] for r in conn.execute(
        "SELECT tag FROM board_tags WHERE board_id = ? ORDER BY tag", (row["id"],)
    )]
    key_ics = [r[0] for r in conn.execute(
        "SELECT ic FROM board_key_ics WHERE board_id = ? ORDER BY ic", (row["id"],)
    )]

    neighborhoods = json.loads(row["neighborhoods_json"]) if row["neighborhoods_json"] else []

    result: dict[str, Any] = {
        "slug": row["slug"],
        "name": row["name"],
        "org": row["org"],
        "org_display": row["org_display"],
        "source": row["source"],
        "source_url": _source_url(row["source"]),
        "format": row["format"],
        "description": row["description"],
        "key_coverage": row["key_coverage"],
        "layers": row["layers"],
        "width_mm": row["width_mm"],
        "height_mm": row["height_mm"],
        "min_trace": row["min_trace"],
        "min_clearance": row["min_clearance"],
        "min_drill": row["min_drill"],
        "min_via": row["min_via"],
        "component_count": row["component_count"],
        "ic_count": row["ic_count"],
        "net_count": row["net_count"],
        "tags": tags,
        "key_ics": key_ics,
    }

    if focus:
        matched, match_type, partial_matches = _match_focus(neighborhoods, focus)

        if matched:
            matched = {**matched, "pins": _clean_junk_values(matched["pins"])}
            result["focus"] = matched
            result["focus_match_type"] = match_type

            # Auto-include cross-board consensus for the focused IC
            if get_consensus_fn:
                consensus = get_consensus_fn(matched["value"])
                if not consensus and match_type == "partial" and focus != matched["value"]:
                    consensus = get_consensus_fn(focus)
                if consensus:
                    result["consensus"] = consensus

            # Show other ICs that also matched the partial term
            if match_type == "partial" and len(partial_matches) > 1:
                seen_values: set[str] = {matched["value"]}
                alternatives: list[dict[str, str]] = []
                for alt in partial_matches[1:]:
                    if alt["value"] not in seen_values:
                        seen_values.add(alt["value"])
                        alternatives.append({"ref": alt["ref"], "value": alt["value"]})
                if alternatives:
                    result["focus_alternatives"] = alternatives
        else:
            available = [{"ref": h["ref"], "value": h["value"]} for h in neighborhoods]
            if available:
                result["focus_error"] = f"IC '{focus[:50]}' not found on this board"
            else:
                result["focus_error"] = (
                    f"IC '{focus[:50]}' not found — this board has no parsed IC neighborhoods. "
                    "Try include_bom=True to see all components."
                )
                available = [{"value": ic} for ic in key_ics]
            result["available_ics"] = available
    else:
        components, passives_omitted = _filter_components(conn, row["id"], include_bom)
        result["components"] = components
        if passives_omitted:
            result["passives_omitted"] = passives_omitted

        result["neighborhoods"] = _enrich_neighborhoods(conn, row["id"], neighborhoods)

    if include_raw:
        result["nets"] = json.loads(row["nets_json"]) if row["nets_json"] else []
        result["positions"] = json.loads(row["positions_json"]) if row["positions_json"] else []
        result["copper_pours"] = json.loads(row["copper_pours_json"]) if row["copper_pours_json"] else []

    return result


def get_consensus(
    conn: sqlite3.Connection,
    ic_name: str,
) -> dict[str, Any] | None:
    """Get cross-board consensus for how an IC is used across all boards.

    Aggregates neighborhoods from all boards that use the given IC.
    Reports per-pin component choices with counts and percentages.
    Only meaningful when 2+ boards share an IC.
    """
    # Pre-filter: find boards containing this IC via indexed tables,
    # then only load their neighborhoods (avoids full-table JSON scan)
    escaped = _escape_like(ic_name)
    ic_pattern = f"%{escaped}%"
    candidate_ids = conn.execute(
        """SELECT DISTINCT board_id FROM (
            SELECT board_id FROM board_key_ics WHERE ic LIKE ? ESCAPE '\\'
            UNION
            SELECT board_id FROM board_components WHERE ref LIKE 'U%' AND value LIKE ? ESCAPE '\\'
        )""",
        (ic_pattern, ic_pattern),
    ).fetchall()

    if not candidate_ids:
        return None

    placeholders = ",".join("?" for _ in candidate_ids)
    ids = [r[0] for r in candidate_ids]
    rows = conn.execute(
        f"SELECT slug, neighborhoods_json FROM boards WHERE id IN ({placeholders}) AND neighborhoods_json IS NOT NULL",
        ids,
    ).fetchall()

    ic_lower = ic_name.lower()
    all_hoods: list[dict] = []
    board_slugs: list[str] = []

    for slug, hoods_json in rows:
        if not hoods_json:
            continue
        for h in json.loads(hoods_json):
            if ic_lower in h["value"].lower():
                all_hoods.append(h)
                board_slugs.append(slug)
                break  # one match per board

    if len(all_hoods) < 2:
        return None

    # Aggregate per pin
    pin_consensus: dict[str, dict] = {}
    decap_boards: dict[str, set] = {}
    total = len(all_hoods)

    for i, hood in enumerate(all_hoods):
        for pin_name, components in hood["pins"].items():
            if pin_name == "_decoupling":
                for c in components:
                    decap_boards.setdefault(c["value"], set()).add(i)
                continue

            if pin_name not in pin_consensus:
                pin_consensus[pin_name] = {"count": 0, "components": Counter()}
            pin_consensus[pin_name]["count"] += 1
            for c in components:
                key = f"{c['value']} [{c['role']}]"
                pin_consensus[pin_name]["components"][key] += 1

    # Build result — sort by board count descending, cap at 30 pins
    _MAX_CONSENSUS_PINS = 30
    eligible_pins = [
        (pin_name, data)
        for pin_name, data in pin_consensus.items()
        if data["count"] >= 2
    ]
    eligible_pins.sort(key=lambda x: -x[1]["count"])
    pins_truncated = len(eligible_pins) > _MAX_CONSENSUS_PINS
    eligible_pins = eligible_pins[:_MAX_CONSENSUS_PINS]

    pins_result = {}
    for pin_name, data in eligible_pins:
        top_choices = [
            {"value_role": vr, "count": cnt, "pct": round(cnt * 100 / total)}
            for vr, cnt in data["components"].most_common(5)
        ]
        pins_result[pin_name] = {
            "boards_with_pin": data["count"],
            "top_choices": top_choices,
        }

    decoupling = sorted(
        [
            {"value": val, "boards": len(boards), "pct": round(len(boards) * 100 / total)}
            for val, boards in decap_boards.items()
        ],
        key=lambda x: -x["boards"],
    )[:5] if decap_boards else []

    result_dict: dict[str, Any] = {
        "ic": ic_name,
        "board_count": total,
        "boards": board_slugs,
        "decoupling": decoupling,
        "pins": pins_result,
    }
    if pins_truncated:
        result_dict["pins_truncated"] = True
    return result_dict


def get_tag_consensus(
    conn: sqlite3.Connection,
    tag: str,
) -> dict[str, Any] | None:
    """Get IC consensus across all boards with a given tag.

    Aggregates board_key_ics for boards tagged with `tag`.
    Returns top ICs by board count with percentages.
    Only returns results when 2+ boards share the tag.
    """
    rows = conn.execute(
        """SELECT bk.ic, GROUP_CONCAT(DISTINCT b.slug) as board_slugs
           FROM board_tags bt
           JOIN board_key_ics bk ON bt.board_id = bk.board_id
           JOIN boards b ON bt.board_id = b.id
           WHERE bt.tag = ?
           GROUP BY bk.ic
           ORDER BY COUNT(DISTINCT bk.board_id) DESC""",
        (tag,),
    ).fetchall()

    if not rows:
        return None

    board_count_row = conn.execute(
        "SELECT COUNT(DISTINCT board_id) FROM board_tags WHERE tag = ?",
        (tag,),
    ).fetchone()
    board_count = board_count_row[0] if board_count_row else 0

    if board_count < 2:
        return None

    top_ics = []
    for ic, slugs_str in rows[:10]:
        boards_list = sorted(set(slugs_str.split(",")))
        ic_boards = len(boards_list)
        top_ics.append({
            "ic": ic,
            "boards": ic_boards,
            "pct": round(ic_boards * 100 / board_count),
            "example_boards": boards_list[:3],
        })

    return {
        "tag": tag,
        "board_count": board_count,
        "top_ics": top_ics,
    }


def get_stats(conn: sqlite3.Connection) -> dict[str, Any]:
    """Get database statistics."""
    total = conn.execute("SELECT COUNT(*) FROM boards").fetchone()[0]

    formats = {
        row[0]: row[1]
        for row in conn.execute(
            "SELECT format, COUNT(*) FROM boards GROUP BY format ORDER BY 2 DESC"
        )
    }

    top_orgs = {
        row[0]: row[1]
        for row in conn.execute(
            "SELECT org_display, COUNT(*) FROM boards GROUP BY org_display ORDER BY 2 DESC LIMIT 10"
        )
    }

    top_tags = {
        row[0]: row[1]
        for row in conn.execute(
            "SELECT tag, COUNT(*) FROM board_tags GROUP BY tag ORDER BY 2 DESC LIMIT 15"
        )
    }

    return {
        "total_boards": total,
        "formats": formats,
        "top_orgs": top_orgs,
        "top_tags": top_tags,
    }
