"""0.10.4: anonymous part_lifecycle input counts, with fake clocks and no requests."""

import json

import pytest

from pcbparts_mcp import server, stats
from pcbparts_mcp.stats import LIFECYCLE_INPUT_FORMS, UsageStats
from test_usage_stats import Clock


def forms(usage, day=0):
    return usage.summary()["days"][day]["lifecycle_inputs"]


def test_fixed_labels_totals_and_persistence(tmp_path):
    clock = Clock()
    usage = UsageStats(clock=clock)
    path = tmp_path / "usage.json"
    usage.open(path)
    for form in LIFECYCLE_INPUT_FORMS:
        usage.record_lifecycle_input(form)
    usage.record_lifecycle_input("private-part-number")
    clock.advance(86400)
    usage.record_lifecycle_input("bare_number")
    assert usage.summary()["totals"]["lifecycle_inputs"] == {
        "bare_number": 2, "with_manufacturer": 1, "lcsc_code": 1}
    assert usage.summary(days=1)["totals"]["lifecycle_inputs"] == {
        "bare_number": 1, "with_manufacturer": 0, "lcsc_code": 0}
    usage.save()
    again = UsageStats(clock=clock)
    again.open(path)
    assert forms(again) == forms(usage) and forms(again, 1) == forms(usage, 1)
    assert "private-part" not in path.read_text(encoding="utf-8")
    assert "0.10.4" in usage.summary()["about"] and "lifecycle_inputs" in usage.summary()["about"]


@pytest.mark.parametrize("value", [None, [], "bad", 3, True])
def test_older_or_malformed_field_is_null_then_counts(tmp_path, value):
    path = tmp_path / "usage.json"
    path.write_text(json.dumps({"days": {"2026-10-16": {}, "2026-10-17": {"lifecycle_inputs": value}}}),
                    encoding="utf-8")
    usage = UsageStats(clock=Clock())
    usage.open(path)
    assert forms(usage) is None and forms(usage, 1) is None
    assert usage.summary()["totals"]["lifecycle_inputs"] == dict.fromkeys(LIFECYCLE_INPUT_FORMS, 0)
    usage.record_lifecycle_input("lcsc_code")
    assert forms(usage) == {"bare_number": 0, "with_manufacturer": 0, "lcsc_code": 1}
    assert forms(usage, 1) is None


def test_malformed_counts_and_unknown_labels_are_dropped(tmp_path):
    path = tmp_path / "usage.json"
    path.write_text(json.dumps({"days": {"2026-10-17": {"lifecycle_inputs": {
        "bare_number": 2, "with_manufacturer": True, "lcsc_code": float("inf"), "private-part": 9}}}}),
                    encoding="utf-8")
    usage = UsageStats(clock=Clock())
    usage.open(path)
    assert forms(usage) == {"bare_number": 2, "with_manufacturer": 0, "lcsc_code": 0}
    usage.record_lifecycle_input("bare_number")
    usage.save()
    assert "private-part" not in path.read_text(encoding="utf-8")


async def test_tool_counts_input_forms_before_catalog_resolution(monkeypatch, stored_lifecycle):
    from pcbparts_mcp.lifecycle import Reading

    class Catalog:
        def get_by_lcsc_batch(self, codes):
            return {"C7950": {"model": "LM358P", "manufacturer": "Texas Instruments"}}

    monkeypatch.setattr(stats, "usage", UsageStats(clock=Clock()))
    monkeypatch.setattr(server, "get_db", lambda: Catalog())
    stored_lifecycle.put_readings([Reading("LM358P", "Texas Instruments", "mouser", "active", "Active",
                                           stored_lifecycle.now())])
    await server.part_lifecycle(["LM358P", "LM358P", {"mpn": "LM358P", "manufacturer": "TI"}, "C7950", None])
    assert forms(stats.usage) == {"bare_number": 2, "with_manufacturer": 1, "lcsc_code": 1}
    assert "LM358P" not in json.dumps(stats.usage.summary())


def test_counting_failure_does_not_break_lookup(monkeypatch):
    class Broken:
        def record_lifecycle_input(self, form):
            raise RuntimeError("boom")

    monkeypatch.setattr(stats, "usage", Broken())
    stats.count_lifecycle_input("bare_number")
