"""Tests for scripts/build_database.py, build_sensor_db.py and build_history_db.py build safety.

Covers audit #5 (cross-category duplicate LCSC: INSERT OR IGNORE first-wins +
count-check abort) and #13 (atomic temp+rename builds, tmp cleanup on failure,
old DB left intact).
"""

import gzip
import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import build_database, MAX_IGNORED_ROWS  # noqa: E402
from build_sensor_db import build_db as build_sensor_db, MIN_SENSOR_COUNT  # noqa: E402
from build_history_db import build_history_db  # noqa: E402


def _part(lcsc: str, **over) -> dict:
    """Minimal part row in the compact scraped-JSONL schema."""
    part = {
        "l": lcsc, "m": f"MPN-{lcsc}", "f": "TestCorp", "p": "0402", "s": 100,
        "t": "b", "c": 1, "$": 0.01, "d": f"part {lcsc}", "a": [],
    }
    part.update(over)
    return part


def _write_category(data_dir: Path, slug: str, parts: list[dict]) -> None:
    cat_dir = data_dir / "categories"
    cat_dir.mkdir(parents=True, exist_ok=True)
    with gzip.open(cat_dir / f"{slug}.jsonl.gz", "wt") as f:
        for part in parts:
            f.write(json.dumps(part) + "\n")


def _row_count(db_path: Path) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM components").fetchone()[0]
    finally:
        conn.close()


def _no_tmp_left(db_path: Path) -> bool:
    tmp = db_path.with_suffix(".db.tmp")
    return not any(Path(str(tmp) + s).exists() for s in ("", "-wal", "-shm"))


class TestBuildDatabase:
    def test_basic_build(self, tmp_path):
        _write_category(tmp_path, "resistors", [_part("C1"), _part("C2")])
        stats = build_database(tmp_path, tmp_path / "components.db", verbose=False)
        assert stats["total_parts"] == 2
        assert _row_count(tmp_path / "components.db") == 2

    def test_connector_columns_and_migration(self, tmp_path):
        from build_database import migrate_connector_columns
        from pcbparts_mcp.search.spec_filter import CONNECTOR_FILTER_COLUMNS

        _write_category(tmp_path, "connectors", [
            _part("C1", a=[[name, "2-pin"] for name in CONNECTOR_FILTER_COLUMNS if name != "Pitch"]
                  + [["Pitch", "2.00mm"], ["Reference Series", " sh "]]),
            _part("C2", a=[[name, "2x20P"] for name in CONNECTOR_FILTER_COLUMNS if name != "Pitch"]
                  + [["Pitch", "2.19mm、2.54mm"]]),
            _part("C3", a=[["Number of Contacts", "16 contacts"], ["Number of Positions", "4.0"],
                           ["Number of Positions or Pins", "2P+2P"], ["Pitch", "0.5mm"]]),
            _part("C4"),
        ])
        db_path = tmp_path / "components.db"
        build_database(tmp_path, db_path, verbose=False)
        with sqlite3.connect(db_path) as conn:
            sql = ("SELECT num_pins, pitch_mm, num_contacts, num_positions, num_positions_or_pins, "
                   "reference_series FROM components ORDER BY lcsc")
            expected = [(2, 2, 2, 2, 2, " sh "), (None,) * 6,
                        (None, .5, 16, 4, None, None), (None,) * 6]
            assert conn.execute(sql).fetchall() == expected
            indexes = {row[1] for row in conn.execute("PRAGMA index_list(components)")}
            assert {"idx_connector_pitch", "idx_connector_contacts", "idx_connector_positions",
                    "idx_connector_positions_or_pins"} <= indexes
            # Recreate the old schema and its permissive pin/pitch values. The
            # migration must use exactly the same extraction as a fresh build.
            for name in indexes:
                if name.startswith("idx_connector_"):
                    conn.execute(f"DROP INDEX {name}")
            for name in ("num_contacts", "num_positions", "num_positions_or_pins", "reference_series"):
                conn.execute(f"ALTER TABLE components DROP COLUMN {name}")
            conn.execute("UPDATE components SET num_pins=2, pitch_mm=2.19 WHERE lcsc='C2'")
            assert migrate_connector_columns(conn) == 4
            assert conn.execute(sql).fetchall() == expected
            assert migrate_connector_columns(conn) == 4
            assert conn.execute(sql).fetchall() == expected

    def test_mosfet_gate_column_migration_and_fallback(self, tmp_path):
        from build_database import migrate_mosfet_gate_column
        from pcbparts_mcp.db import ComponentDatabase

        values = ["21mΩ@10V、25mΩ@4.5V、33mΩ@2.5V", "48mΩ@2.5V", "35mΩ@10V",
                  "19mΩ@3.3V", "14mΩ", "-", "30Ω@0V", "14Ω@350mV", "50mΩ@-4.5V",
                  "180mΩ@4.V", "30mΩ@VGS=4.5V", "34mΩ@V", "60mΩ@4.5"]
        _write_category(tmp_path, "mosfets", [
            _part(f"C{i}", a=[["RDS(on)", value]], s=1000 - i) for i, value in enumerate(values)
        ])
        db_path = tmp_path / "components.db"
        build_database(tmp_path, db_path, verbose=False)
        sql = "SELECT rds_gate_min_v FROM components ORDER BY stock DESC"
        expected = [(v,) for v in (2.5, 2.5, 10, 3.3, None, None, 0, .35, 4.5, 4, 4.5, None, None)]
        with sqlite3.connect(db_path) as conn:
            assert conn.execute(sql).fetchall() == expected
            assert any("idx_mosfet_gate" in row[3] for row in conn.execute(
                "EXPLAIN QUERY PLAN SELECT lcsc FROM components "
                "WHERE subcategory_id=1 AND rds_gate_min_v<=3.3"))
        database = ComponentDatabase(db_path=db_path)
        try:
            indexed = database.search(gate_drive_v=3.3, limit=100)
            assert [p["lcsc"] for p in indexed["results"][:5]] == ["C0", "C1", "C3", "C6", "C7"]
            assert indexed["results"][0]["rds_on_at_drive"] == "33mΩ@2.5V"
            at_five = database.search(gate_drive_v=5, limit=100)
            assert at_five["results"][0]["rds_on_at_drive"] == "25mΩ@4.5V"
            # Prove the indexed path never calls the JSON fallback.
            database._conn.create_function("rds_gate_min", 1, lambda _: 1 / 0)
            assert database.search(gate_drive_v=3.3, limit=100) == indexed
        finally:
            database.close()
        with sqlite3.connect(db_path) as conn:
            conn.execute("DROP INDEX idx_mosfet_gate")
            conn.execute("ALTER TABLE components DROP COLUMN rds_gate_min_v")
        database = ComponentDatabase(db_path=db_path)
        try:
            assert database.search(gate_drive_v=3.3, limit=100) == indexed
            assert database.search(gate_drive_v=5, limit=100) == at_five
            page = database.search(gate_drive_v=3.3, limit=4, offset=3)
            assert page["results"] == indexed["results"][3:7]
            assert page["total"] == len(values)
        finally:
            database.close()
        with sqlite3.connect(db_path) as conn:
            assert migrate_mosfet_gate_column(conn) == len(values)
            assert conn.execute(sql).fetchall() == expected
            assert migrate_mosfet_gate_column(conn) == len(values)
            assert conn.execute(sql).fetchall() == expected

    def test_case_insensitive_mpn_lookup_uses_built_index(self, tmp_path):
        from pcbparts_mcp.db.lookup import get_by_mpn

        _write_category(tmp_path, "ics", [
            _part("C1", m="LM358", s=100), _part("C2", m="lm358", s=200),
            _part("C3", m="ÄBC"), _part("C4", m="äbc"),
            _part("C5", m="ERJ-2RKF2702X"),
        ])
        db_path = tmp_path / "components.db"
        build_database(tmp_path, db_path, verbose=False)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            indexes = {row[1] for row in conn.execute("PRAGMA index_list(components)")}
            assert "idx_mpn_lower" in indexes
            assert "idx_mpn_key" in indexes
            queries = []
            conn.set_trace_callback(queries.append)
            assert [p["lcsc"] for p in get_by_mpn(conn, "lM358", {})] == ["C2", "C1"]
            assert [p["lcsc"] for p in get_by_mpn(conn, "Äbc", {})] == ["C3"]
            # Include the normalized-variant path, using the actual queries from lookup.py.
            assert [p["lcsc"] for p in get_by_mpn(conn, "LM358-TR", {})] == ["C2", "C1"]
            assert [p["lcsc"] for p in get_by_mpn(conn, "erj2rkf2702x", {})] == ["C5"]
            conn.set_trace_callback(None)
            for query in queries:
                if "LOWER(mpn)" in query:
                    plan = [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + query)]
                    assert any("SEARCH components USING INDEX idx_mpn_lower" in row for row in plan)
                if "REPLACE(" in query:
                    plan = [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + query)]
                    assert any("SEARCH components USING INDEX idx_mpn_key" in row for row in plan)
            conn.execute("DROP INDEX idx_mpn_lower")
            assert [p["lcsc"] for p in get_by_mpn(conn, "lM358", {})] == ["C2", "C1"]
            conn.execute("DROP INDEX idx_mpn_key")
            assert [p["lcsc"] for p in get_by_mpn(conn, "erj2rkf2702x", {})] == ["C5"]
        finally:
            conn.close()

    # --- #5: cross-category duplicate LCSC ---------------------------------------

    def test_cross_category_duplicate_does_not_crash(self, tmp_path):
        """Same LCSC in two categories previously raised IntegrityError (PK) and
        aborted the build; OR IGNORE keeps the build alive."""
        _write_category(tmp_path, "aaa", [_part("C1", d="from aaa"), _part("C2")])
        _write_category(tmp_path, "bbb", [_part("C1", d="from bbb"), _part("C3")])
        db_path = tmp_path / "components.db"
        stats = build_database(tmp_path, db_path, verbose=False)
        assert stats["total_parts"] == 3  # C1 counted once
        assert _row_count(db_path) == 3

    def test_duplicate_first_alphabetical_wins(self, tmp_path):
        """Deterministic winner: sorted(glob) inserts aaa first, OR IGNORE keeps it."""
        _write_category(tmp_path, "zzz", [_part("C1", d="from zzz")])
        _write_category(tmp_path, "aaa", [_part("C1", d="from aaa")])
        db_path = tmp_path / "components.db"
        build_database(tmp_path, db_path, verbose=False)
        conn = sqlite3.connect(db_path)
        try:
            desc = conn.execute("SELECT description FROM components WHERE lcsc='C1'").fetchone()[0]
        finally:
            conn.close()
        assert desc == "from aaa"

    def test_mass_row_loss_aborts_and_keeps_old_db(self, tmp_path):
        """> MAX_IGNORED_ROWS dropped rows means corruption, not benign dupes —
        the build must fail loudly and leave the previous DB serving."""
        db_path = tmp_path / "components.db"
        _write_category(tmp_path, "good", [_part(f"C{i}") for i in range(10)])
        build_database(tmp_path, db_path, verbose=False)
        assert _row_count(db_path) == 10

        n_dupes = MAX_IGNORED_ROWS + 1
        dupes = [_part(f"D{i}") for i in range(n_dupes)]
        _write_category(tmp_path, "poison1", dupes)
        _write_category(tmp_path, "poison2", dupes)
        with pytest.raises(ValueError, match="dropped by INSERT OR IGNORE"):
            build_database(tmp_path, db_path, verbose=False)

        assert _row_count(db_path) == 10  # old DB untouched
        assert _no_tmp_left(db_path)

    # --- #13: atomic build -------------------------------------------------------

    def test_atomic_build_replaces_old_db(self, tmp_path):
        """Build should atomically replace an existing database, no temp leftovers."""
        db_path = tmp_path / "components.db"
        _write_category(tmp_path, "resistors", [_part("C1")])
        build_database(tmp_path, db_path, verbose=False)
        _write_category(tmp_path, "resistors", [_part("C1"), _part("C2")])
        build_database(tmp_path, db_path, verbose=False)
        assert _row_count(db_path) == 2
        assert _no_tmp_left(db_path)

    def test_failed_build_keeps_old_db_and_cleans_tmp(self, tmp_path):
        """Failure injection: a build that dies mid-load must leave the old DB
        intact (still serving) and remove its temp files."""
        db_path = tmp_path / "components.db"
        _write_category(tmp_path, "good", [_part("C1")])
        build_database(tmp_path, db_path, verbose=False)

        bad = tmp_path / "categories" / "zzz-corrupt.jsonl.gz"
        with gzip.open(bad, "wt") as f:
            f.write("{this is not json\n")
        with pytest.raises(json.JSONDecodeError):
            build_database(tmp_path, db_path, verbose=False)

        assert _row_count(db_path) == 1  # old DB untouched
        assert _no_tmp_left(db_path)

    def test_interrupt_cleans_tmp(self, tmp_path, monkeypatch):
        """Ctrl-C (KeyboardInterrupt, a BaseException) mid-build must also clean up."""
        db_path = tmp_path / "components.db"
        _write_category(tmp_path, "good", [_part("C1")])
        build_database(tmp_path, db_path, verbose=False)

        import build_database as bd
        monkeypatch.setattr(
            bd, "_build_into_tmp",
            lambda *a, **kw: (_ for _ in ()).throw(KeyboardInterrupt()),
        )
        with pytest.raises(KeyboardInterrupt):
            bd.build_database(tmp_path, db_path, verbose=False)
        assert _row_count(db_path) == 1
        assert _no_tmp_left(db_path)


# --- build_sensor_db.py --------------------------------------------------------


def _sensor(i: int) -> dict:
    return {
        "name": f"Sensor {i}", "manufacturer": "TestCorp", "type": "temperature",
        "voltage": "3.3V", "datasheet_url": None, "description": f"test sensor {i}",
        "source_tier": 1, "sources": ["test"], "platforms": ["arduino"],
        "measures": ["temperature"], "protocols": ["i2c"], "urls": [],
    }


def _merged(n: int) -> dict[str, dict]:
    return {f"S{i}": _sensor(i) for i in range(n)}


def _sensor_count(db_path: Path) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
    finally:
        conn.close()


class TestBuildSensorDb:
    def test_atomic_build_replaces_old_db(self, tmp_path):
        db_path = tmp_path / "sensor.db"
        build_sensor_db(_merged(MIN_SENSOR_COUNT), db_path, quiet=True)
        build_sensor_db(_merged(MIN_SENSOR_COUNT + 5), db_path, quiet=True)
        assert _sensor_count(db_path) == MIN_SENSOR_COUNT + 5
        assert _no_tmp_left(db_path)

    def test_failed_build_keeps_old_db_and_cleans_tmp(self, tmp_path):
        db_path = tmp_path / "sensor.db"
        build_sensor_db(_merged(MIN_SENSOR_COUNT), db_path, quiet=True)

        poisoned = _merged(MIN_SENSOR_COUNT)
        del poisoned["S0"]["measures"]  # KeyError mid-insert
        with pytest.raises(KeyError):
            build_sensor_db(poisoned, db_path, quiet=True)

        assert _sensor_count(db_path) == MIN_SENSOR_COUNT  # old DB untouched
        assert _no_tmp_left(db_path)

    def test_truncated_dataset_rejected_before_touching_db(self, tmp_path):
        """The count floor fires before the old DB or any temp file is touched."""
        db_path = tmp_path / "sensor.db"
        build_sensor_db(_merged(MIN_SENSOR_COUNT), db_path, quiet=True)
        with pytest.raises(ValueError, match="refusing to build"):
            build_sensor_db(_merged(MIN_SENSOR_COUNT - 1), db_path, quiet=True)
        assert _sensor_count(db_path) == MIN_SENSOR_COUNT
        assert _no_tmp_left(db_path)


# --- build_history_db.py -------------------------------------------------------


def _write_history(data_dir: Path, month: str, n: int) -> None:
    hist = data_dir / "history"
    hist.mkdir(parents=True, exist_ok=True)
    with gzip.open(hist / f"{month}.jsonl.gz", "wt", encoding="utf-8") as f:
        for i in range(n):
            f.write(json.dumps({"l": f"C{i}", "d": f"{month}-01", "s": i, "$": 0.1, "t": "e"}) + "\n")


def _event_count(db_path: Path) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM stock_events").fetchone()[0]
    finally:
        conn.close()


class TestBuildHistoryDb:
    def test_atomic_build_replaces_old_db(self, tmp_path):
        db_path = tmp_path / "stock_history.db"
        _write_history(tmp_path, "2026-01", 3)
        build_history_db(tmp_path, db_path, verbose=False)
        _write_history(tmp_path, "2026-02", 2)
        build_history_db(tmp_path, db_path, verbose=False)
        assert _event_count(db_path) == 5
        assert _no_tmp_left(db_path)

    def test_failed_build_keeps_old_db_and_cleans_tmp(self, tmp_path):
        """Invalid UTF-8 raises past the gzip/JSON handlers: the old DB must survive."""
        db_path = tmp_path / "stock_history.db"
        _write_history(tmp_path, "2026-01", 3)
        build_history_db(tmp_path, db_path, verbose=False)

        with gzip.open(tmp_path / "history" / "2026-02.jsonl.gz", "wb") as f:
            f.write(b'{"l": "C9", "d": "2026-02-01", "s": 1, "t": "e"}\n\xff\xfe\n')
        with pytest.raises(UnicodeDecodeError):
            build_history_db(tmp_path, db_path, verbose=False)

        assert _event_count(db_path) == 3  # old DB untouched
        assert _no_tmp_left(db_path)

    def test_interrupt_cleans_tmp(self, tmp_path, monkeypatch):
        db_path = tmp_path / "stock_history.db"
        _write_history(tmp_path, "2026-01", 3)
        build_history_db(tmp_path, db_path, verbose=False)

        import build_history_db as bh
        monkeypatch.setattr(
            bh, "_fill_tmp_and_swap",
            lambda *a, **kw: (_ for _ in ()).throw(KeyboardInterrupt()),
        )
        with pytest.raises(KeyboardInterrupt):
            bh.build_history_db(tmp_path, db_path, verbose=False)
        assert _event_count(db_path) == 3
        assert _no_tmp_left(db_path)


@pytest.mark.parametrize("attribute,value,expected", [
    ("standby current", "1uA", 1e-6),
    ("Supply Current (Iq)", "5mA", .005),
    ("Supply Current (Iq)", "10μA", 1e-5),
])
def test_idle_current_columns(attribute, value, expected):
    from build_database import extract_numeric_columns

    assert extract_numeric_columns([[attribute, value]])["iq_ua"] == pytest.approx(expected)


@pytest.mark.parametrize("missing_schema", [None, "idx_mpn_lower", "idx_mpn_key", "reference_series", "rds_gate_min_v"])
def test_database_age_warning(tmp_path, caplog, missing_schema):
    from pcbparts_mcp.db import ComponentDatabase

    _write_category(tmp_path, "ics", [_part("C1")])
    db_path = tmp_path / "components.db"
    build_database(tmp_path, db_path, verbose=False)
    if missing_schema:
        with sqlite3.connect(db_path) as conn:
            if missing_schema.startswith("idx_"):
                conn.execute(f"DROP INDEX {missing_schema}")
            else:
                if missing_schema == "rds_gate_min_v":
                    conn.execute("DROP INDEX idx_mosfet_gate")
                conn.execute(f"ALTER TABLE components DROP COLUMN {missing_schema}")
    database = ComponentDatabase(db_path=db_path)
    try:
        database._ensure_db()
        database._ensure_db()
        warnings = [r.message for r in caplog.records if r.name == "pcbparts_mcp.db" and r.levelname == "WARNING"]
        assert len(warnings) == int(missing_schema is not None)
        if missing_schema:
            assert "predates this version" in warnings[0]
            if missing_schema == "idx_mpn_lower":
                assert "quiescent-current filters miss parts" in warnings[0]
            elif missing_schema == "idx_mpn_key":
                assert "separator-insensitive" in warnings[0]
                assert "quiescent-current" not in warnings[0]
            elif missing_schema == "rds_gate_min_v":
                assert "MOSFET gate-drive ranking is slow" in warnings[0]
            else:
                assert "connector filters and series ranking are slow" in warnings[0]
            if missing_schema.startswith("idx_"):
                assert "MPN lookups are slow" in warnings[0]
            assert ".venv/bin/python scripts/build_database.py" in warnings[0]
    finally:
        database.close()
