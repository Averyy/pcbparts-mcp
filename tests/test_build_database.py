"""Tests for scripts/build_database.py and build_sensor_db.py build safety.

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
