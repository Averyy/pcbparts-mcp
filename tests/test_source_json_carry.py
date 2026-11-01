"""Tests for write_source_json keeping sensors that drop out of a scrape."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from check_scrape_status import check_status
from scrapers.common import REMOVE_AFTER_MISSED_SCRAPES, make_sensor_entry, write_source_json


def _sensor(sensor_id: str, **kwargs) -> dict:
    return make_sensor_entry(sensor_id=sensor_id, name=sensor_id.upper(), measures=["motion"], **kwargs)


def _scrape(tmp_path: Path, ids: list[str], **kwargs) -> dict:
    sensors = [_sensor(i, **kwargs) for i in ids]
    write_source_json("src", "https://example.com", sensors, {"sensor_count": len(sensors)}, tmp_path)
    return json.loads((tmp_path / "src.json").read_text(encoding="utf-8"))


def _ids(data: dict) -> list[str]:
    return [s["id"] for s in data["sensors"]]


def test_first_scrape_writes_what_it_found(tmp_path):
    data = _scrape(tmp_path, ["a", "b"])
    assert _ids(data) == ["a", "b"]
    assert data["missed_scrapes"] == {}
    assert data["stats"] == {"sensor_count": 2, "kept_missing": 0}


def test_missing_sensor_kept_until_third_miss(tmp_path):
    assert REMOVE_AFTER_MISSED_SCRAPES == 3
    _scrape(tmp_path, ["a", "b"])

    data = _scrape(tmp_path, ["a"])
    assert _ids(data) == ["a", "b"]
    assert data["missed_scrapes"] == {"b": 1}
    assert data["stats"] == {"sensor_count": 1, "kept_missing": 1}

    data = _scrape(tmp_path, ["a"])
    assert _ids(data) == ["a", "b"]
    assert data["missed_scrapes"] == {"b": 2}

    data = _scrape(tmp_path, ["a"])
    assert _ids(data) == ["a"]
    assert data["missed_scrapes"] == {}
    assert data["stats"]["kept_missing"] == 0


def test_kept_sensor_keeps_its_last_scraped_fields(tmp_path):
    _scrape(tmp_path, ["a", "b"], voltage="3.3")
    data = _scrape(tmp_path, ["a"])
    kept = data["sensors"][1]
    assert kept == _sensor("b", voltage="3.3")
    assert "missed_scrapes" not in kept  # the count lives beside the sensors, not on them


def test_sensor_that_returns_resets_its_count(tmp_path):
    _scrape(tmp_path, ["a", "b"])
    _scrape(tmp_path, ["a"])
    _scrape(tmp_path, ["a"])

    data = _scrape(tmp_path, ["a", "b"], voltage="5")
    assert _ids(data) == ["a", "b"]
    assert data["missed_scrapes"] == {}
    assert data["sensors"][1]["voltage"] == "5"  # fresh data, not the kept copy

    # The next miss starts counting from 1 again
    assert _scrape(tmp_path, ["a"])["missed_scrapes"] == {"b": 1}


def test_new_sensors_added_at_once(tmp_path):
    _scrape(tmp_path, ["a"])
    data = _scrape(tmp_path, ["a", "c"])
    assert _ids(data) == ["a", "c"]
    assert data["missed_scrapes"] == {}


def test_empty_scrape_keeps_data_but_still_fails_the_gate(tmp_path):
    _scrape(tmp_path, ["a", "b"])
    data = _scrape(tmp_path, [])
    assert _ids(data) == ["a", "b"]
    assert data["stats"] == {"sensor_count": 0, "kept_missing": 2}

    status = {"run_at": "2000-01-01T00:00:00+00:00", "sources": {"src": {"ok": True, "error": None}}}
    assert check_status(status, tmp_path, keys=["src"]) == ["src: sensor_count is 0"]


def test_unreadable_previous_file_is_ignored(tmp_path):
    (tmp_path / "src.json").write_text("{not json", encoding="utf-8")
    data = _scrape(tmp_path, ["a"])
    assert _ids(data) == ["a"]
    assert data["missed_scrapes"] == {}


def test_previous_file_without_counts(tmp_path):
    # Files written before missed_scrapes existed count a first miss as 1
    (tmp_path / "src.json").write_text(json.dumps({
        "source": "src", "stats": {"sensor_count": 2}, "sensors": [_sensor("a"), _sensor("b")],
    }), encoding="utf-8")
    data = _scrape(tmp_path, ["a"])
    assert _ids(data) == ["a", "b"]
    assert data["missed_scrapes"] == {"b": 1}
