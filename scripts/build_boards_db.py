"""Build boards.db — Reference board database from parsed OSHW YAML schematics.

Loads YAML files from data/boards/, parses BOARDS.md for key_coverage text,
and builds a SQLite database with FTS5 for searching reference designs.

Usage:
    python scripts/build_boards_db.py [--data-dir data/] [--output data/boards.db] [--quiet]

Also exposes build(data_dir, output, verbose) for auto-build from connection.py.
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from pcbparts_mcp.boards_db.nets import classify_role, is_power_net  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Org display name mapping
# ---------------------------------------------------------------------------

ORG_DISPLAY_NAMES = {
    "adafruit": "Adafruit",
    "sparkfun": "SparkFun",
    "OLIMEX": "Olimex",
    "SolderedElectronics": "Soldered Electronics",
    "AnaviTechnology": "ANAVI Technology",
    "Seeed-Studio": "Seeed Studio",
    "greatscottgadgets": "Great Scott Gadgets",
    "DangerousPrototypes": "Dangerous Prototypes",
    "beagleboard": "BeagleBoard",
    "antmicro": "Antmicro",
    "blues": "Blues",
    "PX4": "PX4",
    "Duet3D": "Duet3D",
    "bitcraze": "Bitcraze",
    "particle-iot": "Particle",
    "prusa3d": "Prusa",
    "ExpressLRS": "ExpressLRS",
    "FrameworkComputer": "Framework",
    "icebreaker-fpga": "1BitSquared",
    "eez-open": "EEZ",
    "LibreSolar": "Libre Solar",
    "CircuitSetup": "CircuitSetup",
    "Protocentral": "ProtoCentral",
}

# Patterns to exclude from all_ics (passive values, power symbols, etc.)
# NOTE: this matches against component VALUES on U/IC refs only.
# Be careful not to filter real ICs: TPS/TPD/TPA (TI), NCP/NCV (ON Semi),
# 74xx logic, 24xx/93xx EEPROMs, TP4056 (charger) etc.
_PASSIVE_RE = re.compile(
    r"^("
    r"GND|VCC|VDD|V\d|NC\b|DNP|NM\b|"
    r"MOUNT|FIDUCIAL|"
    r"LED|DIODE|FUSE|"
    r"[A-Z]?CONN|HEADER|"
    r"TEST|"
    r"\d+\.?\d*\s*V\b|"          # voltage labels: 3.3V, 2.5V LDO
    r"\d+V\d|"                    # voltage reg names: 1V8, 3V3, 2V5
    r"\d+\.?\d*\s*mm\b|"          # physical sizes: 3.5mm audio jack
    r"\d+x\d+|"                   # header sizes: 1x4, 2x10
    r"\d+\.?\d*\s*[kMG]?B\b|"     # memory sizes: 8MB, 128KB
    r"\d+\.?\d*\s*[mkM]?Hz\b|"    # frequencies: 16MHz, 25MHz
    r"\d+\s"                      # digit then space: "8 megabytes"
    r")",
    re.IGNORECASE,
)


def _extract_org(source: str) -> tuple[str, str]:
    """Extract org slug and display name from source field.

    Returns (org_slug, org_display).
    """
    org = source.split("/")[0] if "/" in source else source
    display = ORG_DISPLAY_NAMES.get(org)
    if display is None:
        # Fallback: capitalize first letter if all lowercase, else keep as-is
        display = org.capitalize() if org.islower() else org
    return org, display


def _extract_all_ics(components: list[dict]) -> list[str]:
    """Extract IC part names from U/IC reference components.

    Returns deduplicated list of IC values, excluding passive patterns.
    """
    seen = set()
    ics = []
    for comp in components:
        ref = comp.get("ref", "")
        if not (ref.upper().startswith("U") or ref.upper().startswith("IC")):
            continue
        value = comp.get("value", "")
        if not value or _PASSIVE_RE.match(value):
            continue
        # Normalize for dedup
        key = value.strip()
        if key not in seen:
            seen.add(key)
            ics.append(key)
    return ics


def _board_slug(name: str) -> str:
    """The slug parse_boards.py gives a BOARDS.md row (and writes into the board's YAML)."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower().strip()).strip("-")


def _parse_boards_md(boards_md_path: Path) -> dict[str, str]:
    """Parse BOARDS.md markdown table to extract key_coverage by board slug.

    Keyed by board, not repo: 16 repos hold several boards (the iCEBreaker and iCEBreaker-Bitsy),
    which all got the last row's text, and ZIP downloads (RPi CM4/CM5 IO) matched no source.
    """
    if not boards_md_path.exists():
        logger.warning(f"BOARDS.md not found at {boards_md_path}")
        return {}

    coverage = {}
    text = boards_md_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.startswith("|") or line.startswith("| Board") or line.startswith("|---"):
            continue
        cols = [c.strip() for c in line.split("|")]
        # cols = ['', Board, Org, Repo, Format, SchematicPath, KeyCoverage, '']
        if len(cols) < 7 or not cols[1]:
            continue
        coverage[_board_slug(cols[1])] = cols[6].strip()
    return coverage


def _count_ics(components: list[dict]) -> int:
    """Count components with U or IC reference prefix."""
    return sum(1 for c in components if c.get("ref", "").upper().startswith("U") or c.get("ref", "").upper().startswith("IC"))


# Rails and roles are shared with board_get's focus view
_is_power_net = is_power_net
_classify_role = classify_role


def _extract_neighborhoods(board: dict) -> list[dict]:
    """Extract pin-grouped component neighborhoods for each IC on a board.

    For each IC (U/IC ref), traverse nets to find directly connected components,
    classify by role, group by pin name.

    Returns list of neighborhood dicts, one per IC.
    """
    components = board.get("components", []) or []
    nets = board.get("nets", []) or []
    if not components or not nets:
        return []

    # Build ref→component lookup
    comp_by_ref = {c["ref"]: c for c in components}

    # Find IC refs: U/IC prefix components + any component matching a key_ic
    key_ics_lower = {ic.lower() for ic in (board.get("key_ics", []) or [])}
    ic_refs = []
    seen_ic_refs = set()
    for c in components:
        ref = c["ref"]
        if ref in seen_ic_refs:
            continue
        is_u_or_ic = ref.upper().startswith("U") or ref.upper().startswith("IC")
        is_key_ic = key_ics_lower and any(
            ki in c.get("value", "").lower() for ki in key_ics_lower
        )
        if is_u_or_ic or is_key_ic:
            ic_refs.append(ref)
            seen_ic_refs.add(ref)
    if not ic_refs:
        return []

    # Build decouples reverse index: ic_ref → list of decoupling cap refs
    decouples_for_ic: dict[str, list[str]] = {}
    for c in components:
        target = c.get("decouples")
        if target:
            decouples_for_ic.setdefault(target, []).append(c["ref"])

    neighborhoods = []

    for ic_ref in ic_refs:
        ic_comp = comp_by_ref.get(ic_ref, {})
        ic_value = ic_comp.get("value", "")
        if not ic_value or _PASSIVE_RE.match(ic_value):
            continue

        pins: dict[str, list[dict]] = {}
        seen_refs_per_pin: dict[str, set] = {}

        # Traverse nets to find connections
        for net in nets:
            ic_pin_names = []
            for pin in net["pins"]:
                if pin.startswith(f"{ic_ref}."):
                    ic_pin_names.append(pin.split(".", 1)[1])

            if not ic_pin_names:
                continue

            # Skip power rails for pin connections (decoupling handled separately)
            if _is_power_net(net["name"]):
                continue

            # Find other components on this net
            for other_pin in net["pins"]:
                other_ref = other_pin.split(".")[0]
                if other_ref == ic_ref:
                    continue
                other_comp = comp_by_ref.get(other_ref)
                if not other_comp:
                    continue

                role = _classify_role(other_ref, other_comp, ic_ref)
                entry = {
                    "ref": other_ref,
                    "value": other_comp.get("value", ""),
                    "role": role,
                }

                # Add to each IC pin that sees this net
                for pin_name in ic_pin_names:
                    if pin_name not in seen_refs_per_pin:
                        seen_refs_per_pin[pin_name] = set()
                    if other_ref not in seen_refs_per_pin[pin_name]:
                        seen_refs_per_pin[pin_name].add(other_ref)
                        pins.setdefault(pin_name, []).append(entry)

        # Add decoupling caps (often on power nets we skipped)
        decap_refs = decouples_for_ic.get(ic_ref, [])
        for cap_ref in decap_refs:
            cap_comp = comp_by_ref.get(cap_ref, {})
            already = any(
                cap_ref in seen_refs_per_pin.get(p, set())
                for p in pins
            )
            if not already:
                pins.setdefault("_decoupling", []).append({
                    "ref": cap_ref,
                    "value": cap_comp.get("value", ""),
                    "role": "decoupling",
                })

        if pins:
            neighborhoods.append({
                "ref": ic_ref,
                "value": ic_value,
                "pins": pins,
            })

    return neighborhoods


def build(data_dir: Path | str, output: Path | str, verbose: bool = True) -> None:
    """Build boards.db from YAML data.

    Args:
        data_dir: Directory containing boards/ subdirectory with YAML files
        output: Output database path
        verbose: Print progress info
    """
    data_dir = Path(data_dir)
    output = Path(output)
    boards_dir = data_dir / "boards"

    if not boards_dir.is_dir():
        raise FileNotFoundError(f"Boards directory not found: {boards_dir}")

    start = time.time()

    # Load all YAML files
    yaml_files = sorted(boards_dir.glob("*.yaml"))
    if not yaml_files:
        raise FileNotFoundError(f"No YAML files found in {boards_dir}")

    if verbose:
        print(f"Loading {len(yaml_files)} board YAML files...")

    boards_data = []
    for yf in yaml_files:
        try:
            data = yaml.safe_load(yf.read_text(encoding="utf-8"))
            if data and isinstance(data, dict) and "name" in data:
                boards_data.append(data)
        except Exception as e:
            logger.warning(f"Failed to parse {yf.name}: {e}")

    if verbose:
        print(f"Parsed {len(boards_data)} boards")

    # Parse BOARDS.md for key_coverage
    boards_md = boards_dir / "BOARDS.md"
    coverage_map = _parse_boards_md(boards_md)
    if verbose:
        print(f"Loaded {len(coverage_map)} key_coverage entries from BOARDS.md")

    output.parent.mkdir(parents=True, exist_ok=True)

    # Build to temp file, rename on success (atomic — old DB stays until new one is ready)
    tmp_output = output.with_suffix(".db.tmp")
    if tmp_output.exists():
        tmp_output.unlink()

    conn = sqlite3.connect(str(tmp_output))
    try:
        _build_tables(conn, boards_data, coverage_map, output, start, verbose)
    except Exception:
        conn.close()
        if tmp_output.exists():
            tmp_output.unlink()
        raise

    conn.close()
    tmp_output.replace(output)  # rename() raises FileExistsError on Windows when output exists



_LCSC_CODE = re.compile(r"\bC\d{3,}\b", re.IGNORECASE)


# Boards whose design files fill the MPN field with distributor order codes. PowerFeather PowerUPS
# lists Mouser numbers there (187-CL21A226MAYNNNE, 595-BQ25622RYKR) and one DigiKey number
# (455-SM02B-SRSS-TBDKR-ND), which board_get returned as the maker's part number.
DISTRIBUTOR_CODES_AS_MPN = frozenset({"powerfeather-powerups"})


def part_numbers(comp: dict, slug: str | None = None) -> tuple[str | None, ...]:
    """The design files' own part numbers: mpn, manufacturer, LCSC, Mouser and DigiKey.

    6,100 lines list an MPN and 2,291 an LCSC code, which board_get never returned, so agents
    guessed parts from values like "MBR540 / SOD-123". A part number has a digit: some files put
    the maker in the MPN field ("Yageo", "Murata Electronics North America"). An LCSC field can
    be a JLCPCB URL ending in the code.
    """
    def text(key: str) -> str | None:
        value = comp.get(key)
        value = str(value).strip() if value is not None else ""
        return value if value and value not in ("~", "-", "DNP") else None

    def number(key: str) -> str | None:
        value = text(key)
        return value if value and any(ch.isdigit() for ch in value) and len(value) <= 80 else None

    mpn, lcsc = number("mpn"), _LCSC_CODE.search(text("lcsc") or "")
    lcsc = lcsc.group().upper() if lcsc else None
    if mpn and _LCSC_CODE.fullmatch(mpn):
        # The 0104 USB hub lists LCSC codes as MPNs (SL2.1A: "C192893")
        lcsc, mpn = lcsc or mpn.upper(), None
    mouser, digikey = number("mouser"), number("digikey")
    if mpn and slug in DISTRIBUTOR_CODES_AS_MPN:
        if mpn.upper().endswith("-ND"):
            digikey = digikey or mpn
        else:
            mouser = mouser or mpn
        mpn = None
    return mpn, text("manufacturer"), lcsc, mouser, digikey


def _build_tables(
    conn: sqlite3.Connection,
    boards_data: list[dict],
    coverage_map: dict[str, str],
    output: Path,
    start: float,
    verbose: bool,
) -> None:
    """Build all tables, indexes, and FTS. Called within atomic build wrapper."""
    conn.execute("PRAGMA journal_mode=WAL")

    # Create tables
    conn.executescript("""
        CREATE TABLE boards (
            id INTEGER PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            org TEXT,
            org_display TEXT,
            source TEXT,
            format TEXT,
            description TEXT,
            key_coverage TEXT,
            layers INTEGER,
            width_mm REAL,
            height_mm REAL,
            min_trace TEXT,
            min_clearance TEXT,
            min_drill TEXT,
            min_via TEXT,
            component_count INTEGER,
            ic_count INTEGER,
            net_count INTEGER,
            key_ics_text TEXT,
            all_ics_text TEXT,
            nets_json TEXT,
            positions_json TEXT,
            copper_pours_json TEXT,
            neighborhoods_json TEXT
        );

        CREATE TABLE board_tags (
            board_id INTEGER NOT NULL REFERENCES boards(id),
            tag TEXT NOT NULL,
            PRIMARY KEY (board_id, tag)
        );

        CREATE TABLE board_key_ics (
            board_id INTEGER NOT NULL REFERENCES boards(id),
            ic TEXT NOT NULL,
            PRIMARY KEY (board_id, ic)
        );

        CREATE TABLE board_components (
            id INTEGER PRIMARY KEY,
            board_id INTEGER NOT NULL REFERENCES boards(id),
            ref TEXT NOT NULL,
            value TEXT,
            footprint TEXT,
            description TEXT,
            voltage TEXT,
            tolerance TEXT,
            dielectric TEXT,
            decouples TEXT,
            pullup TEXT,
            pulldown TEXT,
            mpn TEXT,
            manufacturer TEXT,
            lcsc TEXT,
            mouser TEXT,
            digikey TEXT
        );
    """)

    # Bulk insert
    tag_rows = []
    key_ic_rows = []
    comp_rows = []

    for board in boards_data:
        slug = board.get("slug", "")
        name = board.get("name", "")
        source = board.get("source", "")
        fmt = board.get("format", "")
        description = board.get("description", "")
        tags = board.get("tags", []) or []
        key_ics = board.get("key_ics", []) or []
        components = board.get("components", []) or []
        nets = board.get("nets", []) or []
        positions = board.get("positions", []) or []
        copper_pours = board.get("copper_pours", []) or []
        outline = board.get("outline", {}) or {}
        design_rules = board.get("design_rules", {}) or {}

        org, org_display = _extract_org(source)
        all_ics = _extract_all_ics(components)
        key_coverage = coverage_map.get(slug, "")
        neighborhoods = _extract_neighborhoods(board)

        key_ics_text = " ".join(key_ics)
        all_ics_text = " ".join(all_ics)

        conn.execute(
            """INSERT INTO boards (
                slug, name, org, org_display, source, format, description, key_coverage,
                layers, width_mm, height_mm, min_trace, min_clearance, min_drill, min_via,
                component_count, ic_count, net_count, key_ics_text, all_ics_text,
                nets_json, positions_json, copper_pours_json, neighborhoods_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                slug, name, org, org_display, source, fmt, description, key_coverage,
                design_rules.get("layers"),
                outline.get("width_mm"),
                outline.get("height_mm"),
                design_rules.get("min_trace"),
                design_rules.get("min_clearance"),
                design_rules.get("min_drill"),
                design_rules.get("min_via"),
                len(components),
                _count_ics(components),
                len(nets),
                key_ics_text,
                all_ics_text,
                json.dumps(nets) if nets else None,
                json.dumps(positions) if positions else None,
                json.dumps(copper_pours) if copper_pours else None,
                json.dumps(neighborhoods) if neighborhoods else None,
            ),
        )
        board_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        for tag in tags:
            tag_rows.append((board_id, tag))
        for ic in key_ics:
            key_ic_rows.append((board_id, ic))
        for comp in components:
            comp_rows.append((
                board_id,
                comp.get("ref", ""),
                comp.get("value"),
                comp.get("footprint"),
                comp.get("description"),
                comp.get("voltage"),
                comp.get("tolerance"),
                comp.get("dielectric"),
                comp.get("decouples"),
                comp.get("pullup"),
                comp.get("pulldown"),
                *part_numbers(comp, slug),
            ))

    conn.executemany("INSERT INTO board_tags (board_id, tag) VALUES (?, ?)", tag_rows)
    conn.executemany("INSERT INTO board_key_ics (board_id, ic) VALUES (?, ?)", key_ic_rows)
    conn.executemany(
        """INSERT INTO board_components (board_id, ref, value, footprint, description,
           voltage, tolerance, dielectric, decouples, pullup, pulldown,
           mpn, manufacturer, lcsc, mouser, digikey)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        comp_rows,
    )

    # Create indexes (after bulk insert for speed)
    conn.executescript("""
        CREATE INDEX idx_board_org ON boards(org);
        CREATE INDEX idx_board_layers ON boards(layers);
        CREATE INDEX idx_board_format ON boards(format);
        CREATE INDEX idx_board_component_count ON boards(component_count DESC);
        CREATE INDEX idx_board_tag ON board_tags(tag);
        CREATE INDEX idx_board_key_ic ON board_key_ics(ic);
        CREATE INDEX idx_comp_board_id ON board_components(board_id);
        CREATE INDEX idx_comp_value ON board_components(value);
    """)

    # Create and populate FTS5
    conn.execute("""
        CREATE VIRTUAL TABLE boards_fts USING fts5(
            slug,
            name,
            description,
            key_coverage,
            tags_text,
            key_ics_text,
            all_ics_text,
            org_display,
            tokenize='porter unicode61'
        )
    """)

    # Populate FTS from boards table + junction data
    fts_rows = conn.execute("""
        SELECT b.id, b.slug, b.name, b.description, b.key_coverage,
               b.key_ics_text, b.all_ics_text, b.org_display
        FROM boards b
        ORDER BY b.id
    """).fetchall()

    # Build tags_text for each board
    tags_by_board = {}
    for row in conn.execute("SELECT board_id, tag FROM board_tags"):
        tags_by_board.setdefault(row[0], []).append(row[1])

    for row in fts_rows:
        board_id = row[0]
        tags_text = " ".join(tags_by_board.get(board_id, []))
        conn.execute(
            "INSERT INTO boards_fts (slug, name, description, key_coverage, tags_text, key_ics_text, all_ics_text, org_display) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (row[1], row[2], row[3], row[4], tags_text, row[5], row[6], row[7]),
        )

    conn.commit()
    conn.execute("ANALYZE")
    conn.execute("VACUUM")

    # Print stats
    total_boards = conn.execute("SELECT COUNT(*) FROM boards").fetchone()[0]
    total_components = conn.execute("SELECT COUNT(*) FROM board_components").fetchone()[0]
    total_tags = conn.execute("SELECT COUNT(*) FROM board_tags").fetchone()[0]
    total_key_ics = conn.execute("SELECT COUNT(*) FROM board_key_ics").fetchone()[0]

    elapsed = time.time() - start

    if verbose:
        print(f"\n--- boards.db stats ---")
        print(f"Boards: {total_boards}")
        print(f"Components: {total_components}")
        print(f"Tags: {total_tags} (junction rows)")
        print(f"Key ICs: {total_key_ics} (junction rows)")

        # Format breakdown
        formats = conn.execute(
            "SELECT format, COUNT(*) FROM boards GROUP BY format ORDER BY 2 DESC"
        ).fetchall()
        print(f"\nFormats: {', '.join(f'{f}: {c}' for f, c in formats)}")

        # Org breakdown (top 10)
        orgs = conn.execute(
            "SELECT org_display, COUNT(*) FROM boards GROUP BY org_display ORDER BY 2 DESC LIMIT 10"
        ).fetchall()
        print(f"Top orgs: {', '.join(f'{o}: {c}' for o, c in orgs)}")

        # Tag breakdown (top 15)
        top_tags = conn.execute(
            "SELECT tag, COUNT(*) FROM board_tags GROUP BY tag ORDER BY 2 DESC LIMIT 15"
        ).fetchall()
        print(f"Top tags: {', '.join(f'{t}: {c}' for t, c in top_tags)}")

        # Coverage stats
        with_coverage = conn.execute(
            "SELECT COUNT(*) FROM boards WHERE key_coverage IS NOT NULL AND key_coverage != ''"
        ).fetchone()[0]
        with_neighborhoods = conn.execute(
            "SELECT COUNT(*) FROM boards WHERE neighborhoods_json IS NOT NULL"
        ).fetchone()[0]
        total_hoods = 0
        for row in conn.execute("SELECT neighborhoods_json FROM boards WHERE neighborhoods_json IS NOT NULL"):
            total_hoods += len(json.loads(row[0]))
        print(f"\nKey coverage: {with_coverage}/{total_boards} boards")
        print(f"Neighborhoods: {with_neighborhoods}/{total_boards} boards, {total_hoods} IC neighborhoods")
        print(f"Built in {elapsed:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="Build boards.db from YAML data")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="Data directory")
    parser.add_argument("--output", type=Path, default=Path("data/boards.db"), help="Output database path")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING if args.quiet else logging.INFO)
    build(args.data_dir, args.output, verbose=not args.quiet)


if __name__ == "__main__":
    main()
