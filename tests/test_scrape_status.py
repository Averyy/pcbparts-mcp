"""Tests for check_scrape_status.check_status (sensor scrape gating)."""

import json
import sys
from pathlib import Path

# Import from scraper script
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from check_scrape_status import check_status
from scrapers import SCRAPERS

RUN_AT = "2026-07-01T06:00:00+00:00"
FRESH = "2026-07-01T06:05:00+00:00"  # written during the run
STALE = "2026-03-01T17:30:01+00:00"  # left over from a previous run


def _write_source(sensors_dir: Path, key: str, *, scraped_at: str = FRESH,
                  sensor_count: int = 42, errors: int = 0) -> None:
    """Write a minimal per-source JSON matching write_source_json's shape."""
    sensors_dir.mkdir(parents=True, exist_ok=True)
    (sensors_dir / f"{key}.json").write_text(json.dumps({
        "source": key,
        "source_url": "https://example.com",
        "scraped_at": scraped_at,
        "stats": {"sensor_count": sensor_count, "errors": errors},
        "sensors": [],
    }))


def _status(keys: list[str], run_at: str = RUN_AT, **overrides) -> dict:
    """Build a status dict with all keys ok, applying per-key overrides."""
    sources = {key: {"ok": True, "error": None} for key in keys}
    sources.update(overrides)
    return {"run_at": run_at, "sources": sources}


class TestCheckStatus:
    def test_all_ok_no_failures(self, tmp_path):
        keys = ["src_a", "src_b"]
        for key in keys:
            _write_source(tmp_path, key)
        failures = check_status(_status(keys), tmp_path, keys=keys)
        assert failures == []

    def test_missing_status_entry_reported(self, tmp_path):
        _write_source(tmp_path, "src_a")
        _write_source(tmp_path, "src_b")
        # src_b never ran, so it has no status entry
        status = _status(["src_a"])
        failures = check_status(status, tmp_path, keys=["src_a", "src_b"])
        assert len(failures) == 1
        assert "src_b" in failures[0]
        assert "no status entry" in failures[0]

    def test_ok_false_reported_with_error(self, tmp_path):
        keys = ["src_a", "src_b"]
        for key in keys:
            _write_source(tmp_path, key)
        status = _status(keys, src_b={"ok": False, "error": "gh api exploded"})
        failures = check_status(status, tmp_path, keys=keys)
        assert len(failures) == 1
        assert "src_b" in failures[0]
        assert "gh api exploded" in failures[0]

    def test_missing_json_file_reported(self, tmp_path):
        keys = ["src_a", "src_b"]
        _write_source(tmp_path, "src_a")
        # src_b.json was never written despite ok status
        failures = check_status(_status(keys), tmp_path, keys=keys)
        assert len(failures) == 1
        assert "src_b" in failures[0]
        assert "missing" in failures[0]

    def test_stale_scraped_at_reported(self, tmp_path):
        keys = ["src_a", "src_b"]
        _write_source(tmp_path, "src_a")
        _write_source(tmp_path, "src_b", scraped_at=STALE)
        failures = check_status(_status(keys), tmp_path, keys=keys)
        assert len(failures) == 1
        assert "src_b" in failures[0]
        assert "stale" in failures[0]

    def test_zero_sensor_count_reported(self, tmp_path):
        keys = ["src_a", "src_b"]
        _write_source(tmp_path, "src_a")
        _write_source(tmp_path, "src_b", sensor_count=0)
        failures = check_status(_status(keys), tmp_path, keys=keys)
        assert len(failures) == 1
        assert "src_b" in failures[0]
        assert "sensor_count is 0" in failures[0]

    def test_too_many_errors_reported(self, tmp_path):
        keys = ["src_a", "src_b"]
        _write_source(tmp_path, "src_a")
        _write_source(tmp_path, "src_b", errors=6)
        failures = check_status(_status(keys), tmp_path, keys=keys)
        assert len(failures) == 1
        assert "src_b" in failures[0]
        assert "6" in failures[0]

    def test_errors_at_threshold_pass(self, tmp_path):
        """errors == 5 is the boundary — allowed, only >5 fails."""
        keys = ["src_a"]
        _write_source(tmp_path, "src_a", errors=5)
        failures = check_status(_status(keys), tmp_path, keys=keys)
        assert failures == []

    def test_unreadable_json_reported(self, tmp_path):
        keys = ["src_a"]
        tmp_path.mkdir(exist_ok=True)
        (tmp_path / "src_a.json").write_text("{not json")
        failures = check_status(_status(keys), tmp_path, keys=keys)
        assert len(failures) == 1
        assert "src_a" in failures[0]

    def test_invalid_run_at_reported(self, tmp_path):
        keys = ["src_a"]
        _write_source(tmp_path, "src_a")
        failures = check_status(_status(keys, run_at="not-a-date"), tmp_path, keys=keys)
        assert any("run_at" in f for f in failures)

    def test_multiple_failures_all_reported(self, tmp_path):
        """One failure per bad source — a single bad source must not mask others."""
        keys = ["src_a", "src_b", "src_c"]
        _write_source(tmp_path, "src_a", scraped_at=STALE)
        _write_source(tmp_path, "src_c", sensor_count=0)
        status = _status(keys, src_b={"ok": False, "error": "boom"})
        failures = check_status(status, tmp_path, keys=keys)
        assert len(failures) == 3
        assert {f.split(":")[0] for f in failures} == set(keys)

    def test_default_keys_use_scraper_registry(self, tmp_path):
        """Without explicit keys, every registered scraper is checked."""
        failures = check_status({"run_at": RUN_AT, "sources": {}}, tmp_path)
        assert len(failures) == len(SCRAPERS)
