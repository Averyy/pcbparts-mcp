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


def test_catalog_build_gate_warns_and_status_check_rejects_missing_curated_id(tmp_path, monkeypatch, capsys):
    import build_sensor_db as builder
    import check_scrape_status as checker

    monkeypatch.setattr(builder, 'MIN_SENSOR_COUNT', 0)
    sensors = tmp_path / 'sensors'
    for key in SCRAPERS:
        _write_source(sensors, key)
    (sensors / '_scrape_status.json').write_text(json.dumps(_status(list(SCRAPERS))))
    (sensors / 'arduino.json').write_text(json.dumps({
        'scraped_at': FRESH, 'stats': {'sensor_count': 1, 'errors': 0},
        'sensors': [{'id': 'ads1293', 'name': 'ADS1293', 'measures': ['voltage']}],
    }))
    (sensors / 'curated.json').write_text(json.dumps({'ads1293': {'voltage': {
        'value': '2.7-5.5', 'evidence': {'url': 'https://example.com/datasheet'},
        'review_date': '2026-11-10',
    }}}))
    database = tmp_path / 'sensor.db'
    database.write_bytes(b'existing catalog must survive validation')
    monkeypatch.setattr(sys, 'argv', ['check_scrape_status.py', '--sensors-dir', str(sensors), '--build-only'])
    assert checker.main() == 0
    assert database.read_bytes() == b'existing catalog must survive validation'
    # A fresh, successful scrape can still lose a curated device. The pre-commit gate lets the
    # month's data land and warns (failing it discarded every source's data); the status check
    # after the commit fails, so the deploy waits for curated.json.
    _write_source(sensors, 'arduino')
    assert checker.check_status(_status(list(SCRAPERS)), sensors) == []
    capsys.readouterr()
    assert checker.main() == 0
    assert "WARN: curated sensor IDs with no catalog record: ads1293" in capsys.readouterr().out
    assert database.read_bytes() == b'existing catalog must survive validation'
    monkeypatch.setattr(sys, 'argv', ['check_scrape_status.py', '--sensors-dir', str(sensors)])
    assert checker.main() == 1
    assert "curated sensor IDs with no catalog record: ads1293" in capsys.readouterr().out


def test_workflow_build_gate_precedes_commit_and_retains_freshness_gate():
    workflow = (Path(__file__).parent.parent / '.github/workflows/scrape-sensors.yml').read_text(encoding="utf-8")
    assert workflow.index('python scripts/scrape_sensors.py') < workflow.index('python scripts/check_scrape_status.py --build-only')
    assert workflow.index('python scripts/check_scrape_status.py --build-only') < workflow.index('git add data/sensors/')
    assert workflow.index('git push') < workflow.index('python scripts/check_scrape_status.py\n') < workflow.index('gh workflow run docker-build.yml')


def test_build_check_validates_the_given_directory_whatever_its_name(tmp_path):
    """A custom --sensors-dir built its parent's "sensors" sibling instead."""
    import shutil
    from pathlib import Path
    from check_scrape_status import check_catalog_build
    root = Path(__file__).parent.parent / "data" / "sensors"
    custom = tmp_path / "cache-copy"
    shutil.copytree(root, custom)
    assert check_catalog_build(custom) == []
    curated = custom / "curated.json"
    import json
    data = json.loads(curated.read_text(encoding="utf-8"))
    data["nosuchsensor"] = {"voltage": {"value": "3.3", "evidence": {"url": "https://example.com"},
                                         "review_date": "2026-11-10"}}
    curated.write_text(json.dumps(data), encoding="utf-8")
    assert "nosuchsensor" in check_catalog_build(custom)[0]
    assert check_catalog_build(custom, allow_stale=True) == []
