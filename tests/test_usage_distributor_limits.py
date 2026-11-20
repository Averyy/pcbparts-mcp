"""0.10.3 anonymous distributor limit counts. No network; fake UTC clocks only."""

import json

import pytest

from pcbparts_mcp import stats
from pcbparts_mcp.stats import DISTRIBUTOR_LIMIT_CAUSES, DISTRIBUTOR_LIMIT_REFUSALS, UsageStats

from test_usage_stats import Clock


def limits(usage, day=0):
    return usage.summary()["days"][day]["distributor_limits"]


class TestCounts:
    def test_counts_fixed_labels_and_hours(self):
        clock = Clock()
        usage = UsageStats(clock=clock)
        for name in ("mouser", "digikey"):
            for label in DISTRIBUTOR_LIMIT_CAUSES:
                usage.record_distributor_limit(name, "held_back", label)
            for label in DISTRIBUTOR_LIMIT_REFUSALS:
                usage.record_distributor_limit(name, "refusals", label)
        usage.record_distributor_limit("mouser", "held_back", "private-key-123")
        usage.record_distributor_limit("unknown", "held_back", "minute_cap")
        usage.record_distributor_limit("mouser", "unknown", "minute_cap")
        usage.record_distributor_limit("mouser", "refusals", "unknown")
        clock.advance(3600)
        usage.record_distributor_limit("mouser", "held_back", "minute_cap")
        counts = limits(usage)
        assert set(counts) == {"mouser", "digikey"}
        assert counts["mouser"]["held_back"] == {
            label: 2 if label in ("minute_cap", "other") else 1 for label in DISTRIBUTOR_LIMIT_CAUSES}
        assert counts["digikey"]["held_back"] == dict.fromkeys(DISTRIBUTOR_LIMIT_CAUSES, 1)
        assert counts["mouser"]["refusals"] == dict.fromkeys(DISTRIBUTOR_LIMIT_REFUSALS, 1)
        assert counts["mouser"]["held_back_hours"] == [0] * 21 + [len(DISTRIBUTOR_LIMIT_CAUSES) + 1, 1, 0]
        assert counts["digikey"]["held_back_hours"] == [0] * 21 + [len(DISTRIBUTOR_LIMIT_CAUSES), 0, 0]
        assert "private-key" not in json.dumps(usage.summary())
        about = usage.summary()["about"]
        for text in ("distributor_limits", "0.10.3", "held_back", "held_back_hours", "refusals",
                     "by UTC hour", *DISTRIBUTOR_LIMIT_CAUSES, *DISTRIBUTOR_LIMIT_REFUSALS):
            assert text in about

    def test_totals_add_only_listed_days_and_hours(self):
        clock = Clock()
        usage = UsageStats(clock=clock)
        for day in range(3):
            for _ in range(day + 1):
                usage.record_distributor_limit("mouser", "held_back", "distributor_daily")
                usage.record_distributor_limit("digikey", "refusals", "daily")
            clock.advance(86400)
        totals = usage.summary(days=2)["totals"]["distributor_limits"]
        assert totals["mouser"]["held_back"]["distributor_daily"] == 5
        assert totals["mouser"]["held_back_hours"] == [0] * 21 + [5, 0, 0]
        assert totals["digikey"]["refusals"]["daily"] == 5

    def test_old_days_null_and_counting_starts_empty(self, tmp_path):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-10-16": {}, "2026-10-17": {}}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(path)
        assert [limits(usage, i) for i in range(2)] == [None, None]
        assert usage.summary()["totals"]["distributor_limits"] == {}
        usage.record_call("jlc_search", "ok", 1)
        assert limits(usage) == {}
        usage.record_distributor_limit("mouser", "held_back", "daily_count")
        usage.save()
        again = UsageStats(clock=Clock())
        again.open(path)
        assert limits(again) == limits(usage) and limits(again, 1) is None
        again.record_distributor_limit("mouser", "held_back", "daily_count")
        assert limits(again)["mouser"]["held_back"]["daily_count"] == 2

    @pytest.mark.parametrize("value", [None, "x", [1], 5, True])
    def test_malformed_field_is_null(self, tmp_path, value):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-10-17": {"distributor_limits": value}}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(path)
        assert limits(usage) is None
        usage.record_distributor_limit("digikey", "held_back", "other")
        assert limits(usage)["digikey"]["held_back"]["other"] == 1

    def test_malformed_stored_counts_cleaned_and_unknown_labels_dropped(self, tmp_path):
        path = tmp_path / "usage.json"
        day = {"callers": 2, "distributor_limits": {
            "private-key": {"held_back": {"minute_cap": 123}}, "digikey": [1],
            "mouser": {"held_back": {"minute_cap": 3, "daily_count": "2", "address_daily": "bad", "other": True,
                                     "distributor_daily": float("inf"), "distributor_minute": 10**400,
                                     "distributor_refused": float("nan"), "private-key": 8},
                       "held_back_hours": [None, "x", 2] + [0] * 21,
                       "refusals": {"daily": 2, "minute": "x", "refused": True, "secret": 1}, "secret": 3}}}
        path.write_text(json.dumps({"days": {"2026-10-17": day}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(path)
        clean = limits(usage)
        assert set(clean) == {"mouser"}
        assert set(clean["mouser"]) == {"held_back", "held_back_hours", "refusals"}
        assert clean["mouser"]["held_back"] == {label: 3 if label == "minute_cap" else 0
                                                for label in DISTRIBUTOR_LIMIT_CAUSES}
        assert clean["mouser"]["refusals"] == {"daily": 2, "minute": 0, "refused": 0}
        assert clean["mouser"]["held_back_hours"] == [0, 0, 2] + [0] * 21
        assert usage.summary()["days"][0]["callers"] == 2
        usage.record_distributor_limit("mouser", "held_back", "minute_cap")
        usage.save()
        assert "secret" not in path.read_text(encoding="utf-8")

    @pytest.mark.parametrize("hours", [None, [], [0] * 23, "x"])
    def test_malformed_hours_start_at_zero(self, tmp_path, hours):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-10-17": {"distributor_limits": {
            "mouser": {"held_back": "x", "held_back_hours": hours, "refusals": [1]}}}}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(path)
        assert limits(usage)["mouser"]["held_back_hours"] == [0] * 24
        usage.record_distributor_limit("mouser", "held_back", "minute_cap")
        assert limits(usage)["mouser"]["held_back_hours"][21] == 1

    def test_helpers_never_break_a_lookup(self, monkeypatch):
        class Broken:
            def record_distributor_limit(self, *args):
                raise RuntimeError("boom")

        monkeypatch.setattr(stats, "usage", Broken())
        stats.count_distributor_limit("mouser", "held_back", "minute_cap")
