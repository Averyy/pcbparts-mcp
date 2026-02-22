"""Tests for stock history generation and database building."""

import gzip
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

# Import from scraper script
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from scrape_components import generate_stock_history
from build_history_db import build_history_db


def _write_jsonl_gz(path: Path, parts: list[dict]):
    """Write a list of part dicts to a gzipped JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as f:
        for part in parts:
            f.write(json.dumps(part) + "\n")


def _read_history_events(history_dir: Path) -> list[dict]:
    """Read all events from history JSONL.gz files."""
    events = []
    for gz_file in sorted(history_dir.glob("*.jsonl.gz")):
        with gzip.open(gz_file, "rt") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
    return events


class TestGenerateStockHistory:
    """Test generate_stock_history function."""

    def test_stock_change_tracked_low_stock(self):
        """Stock changes on low-stock parts should be tracked."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            # Old data: part with 50 stock
            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1234", "s": 50, "$": 0.01, "t": "b"},
            ])

            # New data: stock dropped to 25 (delta=25, threshold for <100 is >10)
            results = {"resistors": [{"l": "C1234", "s": 25, "$": 0.01, "t": "b"}]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            assert stats["events"] >= 1
            assert any(e["l"] == "C1234" and e["s"] == 25 for e in events)

    def test_stock_change_ignored_high_stock(self):
        """Stock changes on parts with >1000 stock should be ignored."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1234", "s": 5000, "$": 0.001, "t": "b"},
            ])

            results = {"resistors": [{"l": "C1234", "s": 4500, "$": 0.001, "t": "b"}]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            stock_changes = [e for e in events if e["l"] == "C1234" and "e" not in e]
            assert len(stock_changes) == 0

    def test_stock_change_below_threshold_ignored(self):
        """Small stock changes below tier threshold should be ignored."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            # Stock 200, delta of 5 — threshold for 100-500 is >25
            _write_jsonl_gz(categories_dir / "caps.jsonl.gz", [
                {"l": "C5678", "s": 200, "$": 0.05, "t": "e"},
            ])

            results = {"caps": [{"l": "C5678", "s": 195, "$": 0.05, "t": "e"}]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            stock_changes = [e for e in events if e["l"] == "C5678" and "e" not in e]
            assert len(stock_changes) == 0

    def test_new_part_tracked(self):
        """New parts with 0 < stock <= 1000 should be recorded."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            # Old data has one part
            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1111", "s": 100, "$": 0.01, "t": "b"},
            ])

            # New data has the old part plus a new one
            results = {"resistors": [
                {"l": "C1111", "s": 100, "$": 0.01, "t": "b"},
                {"l": "C2222", "s": 500, "$": 0.02, "t": "e"},
            ]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            new_events = [e for e in events if e["l"] == "C2222" and e.get("e") == "new"]
            assert len(new_events) == 1

    def test_new_part_high_stock_not_tracked(self):
        """New parts with stock > 1000 should NOT be recorded."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1111", "s": 100, "$": 0.01, "t": "b"},
            ])

            results = {"resistors": [
                {"l": "C1111", "s": 100, "$": 0.01, "t": "b"},
                {"l": "C9999", "s": 50000, "$": 0.001, "t": "b"},
            ]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            new_events = [e for e in events if e["l"] == "C9999"]
            assert len(new_events) == 0

    def test_new_part_zero_stock_not_tracked(self):
        """New parts with stock=0 should NOT be recorded (no value in tracking)."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1111", "s": 100, "$": 0.01, "t": "b"},
            ])

            results = {"resistors": [
                {"l": "C1111", "s": 100, "$": 0.01, "t": "b"},
                {"l": "C3333", "s": 0, "$": 0.01, "t": "b"},
            ]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            new_events = [e for e in events if e["l"] == "C3333"]
            assert len(new_events) == 0

    def test_disappeared_part_tracked(self):
        """Parts that disappear from scrape should be marked as gone."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1111", "s": 100, "$": 0.01, "t": "b"},
                {"l": "C2222", "s": 50, "$": 0.02, "t": "e"},
            ])

            # Only C1111 in new data — C2222 disappeared
            results = {"resistors": [{"l": "C1111", "s": 100, "$": 0.01, "t": "b"}]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            gone_events = [e for e in events if e["l"] == "C2222" and e.get("e") == "gone"]
            assert len(gone_events) == 1
            assert gone_events[0]["s"] == 0

    def test_reappeared_part_tracked(self):
        """Parts that go from 0 stock to >0 should be marked as reappear."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1234", "s": 0, "$": 0.01, "t": "b"},
            ])

            results = {"resistors": [{"l": "C1234", "s": 200, "$": 0.01, "t": "b"}]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            reappear = [e for e in events if e["l"] == "C1234" and e.get("e") == "reappear"]
            assert len(reappear) == 1

            # No duplicate stock-change event — reappear covers it
            stock_changes = [e for e in events if e["l"] == "C1234" and "e" not in e]
            assert len(stock_changes) == 0

    def test_reappeared_part_high_stock_tracked(self):
        """Parts reappearing with >1000 stock should still be tracked (availability signal)."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1234", "s": 0, "$": 0.01, "t": "b"},
            ])

            results = {"resistors": [{"l": "C1234", "s": 5000, "$": 0.01, "t": "b"}]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            reappear = [e for e in events if e["l"] == "C1234" and e.get("e") == "reappear"]
            assert len(reappear) == 1
            assert reappear[0]["s"] == 5000

    def test_library_type_change_tracked(self):
        """Library type changes should be recorded as type_change."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1234", "s": 5000, "$": 0.001, "t": "e"},
            ])

            # Type changed from extended to basic
            results = {"resistors": [{"l": "C1234", "s": 5000, "$": 0.001, "t": "b"}]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            type_events = [e for e in events if e["l"] == "C1234" and e.get("e") == "type_change"]
            assert len(type_events) == 1
            assert type_events[0]["t"] == "b"

    def test_no_old_files_skips(self):
        """If no old JSONL files exist, history should be skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            categories_dir.mkdir(parents=True)
            history_dir = Path(tmp) / "history"

            results = {"resistors": [{"l": "C1234", "s": 100, "$": 0.01, "t": "b"}]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            assert stats.get("skipped") is True
            assert not history_dir.exists() or not list(history_dir.glob("*.jsonl.gz"))

    def test_null_stock_treated_as_zero(self):
        """Parts with null/missing stock should be treated as 0."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1234", "s": None, "$": 0.01, "t": "b"},
            ])

            # New data has stock 50 (reappear from 0)
            results = {"resistors": [{"l": "C1234", "s": 50, "$": 0.01, "t": "b"}]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            reappear = [e for e in events if e["l"] == "C1234" and e.get("e") == "reappear"]
            assert len(reappear) == 1

    def test_multiple_categories(self):
        """History should work across multiple category files."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "resistors.jsonl.gz", [
                {"l": "C1111", "s": 50, "$": 0.01, "t": "b"},
            ])
            _write_jsonl_gz(categories_dir / "capacitors.jsonl.gz", [
                {"l": "C2222", "s": 80, "$": 0.02, "t": "e"},
            ])

            results = {
                "resistors": [{"l": "C1111", "s": 30, "$": 0.01, "t": "b"}],
                "capacitors": [{"l": "C2222", "s": 40, "$": 0.02, "t": "e"}],
            }

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            assert any(e["l"] == "C1111" for e in events)
            assert any(e["l"] == "C2222" for e in events)

    def test_tiered_thresholds(self):
        """Verify each tier's threshold behavior."""
        with tempfile.TemporaryDirectory() as tmp:
            categories_dir = Path(tmp) / "categories"
            history_dir = Path(tmp) / "history"

            _write_jsonl_gz(categories_dir / "parts.jsonl.gz", [
                # 500-1000 tier: need delta > 100
                {"l": "C_MID", "s": 700, "$": 0.01, "t": "b"},
                # 100-500 tier: need delta > 25
                {"l": "C_LOW", "s": 300, "$": 0.01, "t": "b"},
                # <100 tier: need delta > 10
                {"l": "C_VLOW", "s": 80, "$": 0.01, "t": "b"},
            ])

            results = {"parts": [
                # 700 -> 650, delta=50 < 100 threshold — NOT tracked
                {"l": "C_MID", "s": 650, "$": 0.01, "t": "b"},
                # 300 -> 250, delta=50 > 25 threshold — tracked
                {"l": "C_LOW", "s": 250, "$": 0.01, "t": "b"},
                # 80 -> 75, delta=5 < 10 threshold — NOT tracked
                {"l": "C_VLOW", "s": 75, "$": 0.01, "t": "b"},
            ]}

            stats = generate_stock_history(categories_dir, history_dir, results)
            events = _read_history_events(history_dir)

            tracked_parts = {e["l"] for e in events if "e" not in e}
            assert "C_LOW" in tracked_parts
            assert "C_MID" not in tracked_parts
            assert "C_VLOW" not in tracked_parts


class TestBuildHistoryDb:
    """Test build_history_db.py using direct function import."""

    def test_build_from_events(self):
        """Build database from history event files."""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            history_dir = data_dir / "history"
            history_dir.mkdir()
            db_path = data_dir / "stock_history.db"

            # Write some events
            events = [
                {"l": "C1234", "d": "2026-02-20", "s": 100, "$": 0.01, "t": "b"},
                {"l": "C1234", "d": "2026-02-21", "s": 80, "$": 0.01, "t": "b"},
                {"l": "C5678", "d": "2026-02-21", "s": 0, "$": 0.02, "t": "e", "e": "gone"},
            ]
            with gzip.open(history_dir / "2026-02.jsonl.gz", "wt") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")

            stats = build_history_db(data_dir, db_path, verbose=False)
            assert stats["total_events"] == 3

            # Verify database
            conn = sqlite3.connect(db_path)
            count = conn.execute("SELECT COUNT(*) FROM stock_events").fetchone()[0]
            assert count == 3

            # Check specific event
            row = conn.execute(
                "SELECT stock, event_type FROM stock_events WHERE lcsc='C5678'"
            ).fetchone()
            assert row == (0, "gone")

            conn.close()

    def test_build_empty_history(self):
        """Building with no history files should create empty database."""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "history").mkdir()
            db_path = data_dir / "stock_history.db"

            stats = build_history_db(data_dir, db_path, verbose=False)
            assert stats["total_events"] == 0

            conn = sqlite3.connect(db_path)
            count = conn.execute("SELECT COUNT(*) FROM stock_events").fetchone()[0]
            assert count == 0
            conn.close()

    def test_build_no_history_dir(self):
        """Building when history dir doesn't exist should create empty database."""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            db_path = data_dir / "stock_history.db"

            stats = build_history_db(data_dir, db_path, verbose=False)
            assert stats["total_events"] == 0

            conn = sqlite3.connect(db_path)
            count = conn.execute("SELECT COUNT(*) FROM stock_events").fetchone()[0]
            assert count == 0
            conn.close()

    def test_deduplication(self):
        """INSERT OR REPLACE should deduplicate same events."""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            history_dir = data_dir / "history"
            history_dir.mkdir()
            db_path = data_dir / "stock_history.db"

            # Same event written twice (simulates crash recovery)
            events = [
                {"l": "C1234", "d": "2026-02-21", "s": 100, "$": 0.01, "t": "b"},
                {"l": "C1234", "d": "2026-02-21", "s": 100, "$": 0.01, "t": "b"},
            ]
            with gzip.open(history_dir / "2026-02.jsonl.gz", "wt") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")

            stats = build_history_db(data_dir, db_path, verbose=False)
            assert stats["total_events"] == 1  # Deduplicated

    def test_validation_rejects_bad_events(self):
        """Events with invalid fields should be skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            history_dir = data_dir / "history"
            history_dir.mkdir()
            db_path = data_dir / "stock_history.db"

            events = [
                # Valid
                {"l": "C1234", "d": "2026-02-21", "s": 100, "$": 0.01, "t": "b"},
                # Invalid stock (negative)
                {"l": "C2222", "d": "2026-02-21", "s": -5, "$": 0.01, "t": "b"},
                # Invalid library type
                {"l": "C3333", "d": "2026-02-21", "s": 50, "$": 0.01, "t": "x"},
                # Invalid event type
                {"l": "C4444", "d": "2026-02-21", "s": 50, "$": 0.01, "t": "b", "e": "bogus"},
                # Invalid date (too short)
                {"l": "C5555", "d": "2026", "s": 50, "$": 0.01, "t": "b"},
                # Missing lcsc
                {"d": "2026-02-21", "s": 50, "$": 0.01, "t": "b"},
            ]
            with gzip.open(history_dir / "2026-02.jsonl.gz", "wt") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")

            stats = build_history_db(data_dir, db_path, verbose=False)
            assert stats["total_events"] == 1  # Only the valid one

    def test_atomic_build_replaces_old_db(self):
        """Build should atomically replace existing database."""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "history").mkdir()
            db_path = data_dir / "stock_history.db"

            # Create initial DB
            build_history_db(data_dir, db_path, verbose=False)
            assert db_path.exists()

            # Build again (should replace, not fail)
            build_history_db(data_dir, db_path, verbose=False)
            assert db_path.exists()

            # No leftover temp files
            assert not db_path.with_suffix(".db.tmp").exists()
