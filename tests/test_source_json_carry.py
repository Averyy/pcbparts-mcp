"""Tests for write_source_json keeping sensors that drop out of a scrape."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from check_scrape_status import check_status
from scrapers.common import REMOVE_AFTER_MISSED_SCRAPES, make_sensor_entry, write_source_json


def _sensor(sensor_id: str, **kwargs) -> dict:
    return make_sensor_entry(sensor_id=sensor_id, name=sensor_id.upper(), measures=["motion"], **kwargs)


def _scrape(tmp_path: Path, ids: list[str], rerun: bool = False, **kwargs) -> dict:
    """One monthly scrape: the previous file is dated a month back unless `rerun`."""
    path = tmp_path / "src.json"
    if path.exists() and not rerun:
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            previous = None  # tests of unreadable files keep them unreadable
        if isinstance(previous, dict):
            previous["scraped_at"] = "2026-01-01T06:00:00+00:00"
            path.write_text(json.dumps(previous), encoding="utf-8")
    sensors = [_sensor(i, **kwargs) for i in ids]
    write_source_json("src", "https://example.com", sensors, {"sensor_count": len(sensors)}, tmp_path)
    return json.loads(path.read_text(encoding="utf-8"))


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


def test_same_day_rerun_does_not_use_up_a_miss(tmp_path):
    """A re-dispatched job or a local run hours after the monthly scrape is the same scrape:
    pages that time out again must not move a sensor closer to removal."""
    _scrape(tmp_path, ["a", "b", "c"])
    data = _scrape(tmp_path, ["a", "c"])
    assert data["missed_scrapes"] == {"b": 1}

    data = _scrape(tmp_path, ["a"], rerun=True)
    assert _ids(data) == ["a", "c", "b"]  # carried ones follow, in the previous file's order
    assert data["missed_scrapes"] == {"b": 1, "c": 1}  # c's first miss still counts

    data = _scrape(tmp_path, ["a"])  # next month
    assert data["missed_scrapes"] == {"b": 2, "c": 2}


def test_sensor_found_under_its_new_id_is_not_carried(tmp_path):
    """0.9.0 strips maker prefixes from ids: Tasmota's hlkld2410 is now ld2410. The old id
    was carried as a missed duplicate of the same row for three scrapes."""
    _scrape(tmp_path, ["hlkld2410", "a"])
    data = _scrape(tmp_path, ["ld2410", "a"])
    assert _ids(data) == ["ld2410", "a"]
    assert data["missed_scrapes"] == {}


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


def test_missed_sensor_whose_pages_are_gone_is_dropped_at_once(tmp_path):
    """The MicroPython SN-GCJA5 driver's repo was deleted (404); carrying it for three more
    scrapes kept a dead link and a false MicroPython claim on the record."""
    sensors = [_sensor("a", urls=["https://github.com/x/a"]), _sensor("b", urls=["https://github.com/x/gone"]),
               _sensor("c", urls=["https://github.com/x/flaky"]), _sensor("d", urls=["https://github.com/x/d"])]
    write_source_json("src", "https://example.com", sensors, {"sensor_count": 4}, tmp_path)
    checked = []

    def gone(urls):
        checked.append(urls)
        return urls == ["https://github.com/x/gone"]

    found = [sensors[0], sensors[3]]  # half found: not a collapsed source
    write_source_json("src", "https://example.com", found, {"sensor_count": 2}, tmp_path, links_gone=gone)
    data = json.loads((tmp_path / "src.json").read_text(encoding="utf-8"))
    assert _ids(data) == ["a", "d", "c"] and data["missed_scrapes"] == {"c": 1}
    assert checked == [["https://github.com/x/gone"], ["https://github.com/x/flaky"]]  # only missed ones


def test_links_gone_needs_every_page_to_answer_404(monkeypatch):
    import scrapers.common as common

    answers = {"https://github.com/x/gone": 404, "https://github.com/x/moved": 301, "https://docs.example/blocked": 403}

    class Session:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def get(self, url, **kwargs):
            return type("R", (), {"status_code": answers[url]})()

    monkeypatch.setattr(common.wafer, "SyncSession", Session)
    assert common._links_gone(["https://github.com/x/gone.git"]) is True
    assert common._links_gone(["https://github.com/x/gone", "https://github.com/x/moved"]) is False
    assert common._links_gone(["https://docs.example/blocked"]) is False
    assert common._links_gone([]) is False


def test_link_checks_are_bounded_and_skipped_for_a_collapsed_source(tmp_path, monkeypatch):
    """A source that suddenly finds nothing would have checked every carried sensor (750 x 30 s)."""
    import scrapers.common as common
    many = [_sensor(f"s{i}", urls=[f"https://github.com/x/{i}"]) for i in range(60)]
    write_source_json("src", "https://example.com", many, {"sensor_count": 60}, tmp_path)
    calls = []
    write_source_json("src", "https://example.com", [], {"sensor_count": 0}, tmp_path,
                      links_gone=lambda urls: calls.append(urls) or True)
    assert calls == []  # collapsed: nothing checked, everything carried
    assert len(json.loads((tmp_path / "src.json").read_text(encoding="utf-8"))["sensors"]) == 60

    write_source_json("src2", "https://example.com", many, {"sensor_count": 60}, tmp_path)
    write_source_json("src2", "https://example.com", many[:35], {"sensor_count": 35}, tmp_path,
                      links_gone=lambda urls: calls.append(urls) or False)
    assert len(calls) == min(25, common.LINK_CHECK_LIMIT)
