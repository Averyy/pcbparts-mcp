from copy import deepcopy
from datetime import timedelta

import pytest

from pcbparts_dashboard.eastern import EasternRecords, eastern_bounds
from pcbparts_dashboard.store import parse_timestamp as dt, timestamp


def save_day(store, day, *, hourly=10, snapshots=()):
    """A completed UTC day and optional exact hourly counter samples."""
    start = dt(day + "T00:00:00Z")
    record = {"date": day, "calls": 24 * hourly, "hours": [hourly] * 24}
    store.merge_day(record, timestamp(start + timedelta(days=1)))
    for hour in snapshots:
        store.add_snapshot({
            "date": day, "calls": hour * hourly,
            "hours": [hourly] * hour + [0] * (24 - hour),
        }, timestamp(start + timedelta(hours=hour, seconds=30)))
    return record


def test_at_exact_snapshot_and_zero_and_final_boundaries(store):
    final = save_day(store, "2026-11-20", snapshots=(5,))
    records = EasternRecords(store, dt("2026-11-22T00:00:00Z"))
    assert records.at("2026-11-20", dt("2026-11-20T00:00:00Z"))["calls"] == 0
    assert records.at("2026-11-20", dt("2026-11-21T00:00:00Z")) == final | {"approx": False}
    for target in ("05:00:00", "04:59:00", "05:02:00"):
        point = records.at("2026-11-20", dt(f"2026-11-20T{target}Z"))
        assert (point["calls"], point["approx"]) == (50, False)
    assert records.at("2026-11-20", dt("2026-11-20T05:02:01Z"))["approx"]
    with pytest.raises(ValueError, match="within its UTC day"):
        records.at("2026-11-20", dt("2026-11-21T00:00:01Z"))


def test_at_interpolates_using_tool_call_share_and_nearest_points(store):
    day = "2026-11-20"
    hours = [10] * 7 + [30] + [10] * 16
    store.merge_day({"date": day, "calls": 260, "hours": hours}, "2026-11-21T00:00:30Z")
    store.add_snapshot({"date": day, "calls": 60, "upstream": {"a": {"failed": 4}},
                        "tools": {"x": {"calls": 60, "avg_ms": 100}}}, "2026-11-20T06:00:00Z")
    store.add_snapshot({"date": day, "calls": 120, "upstream": {"a": {"failed": 12}},
                        "tools": {"x": {"calls": 120, "avg_ms": 200}}}, "2026-11-20T08:00:00Z")
    records = EasternRecords(store, dt("2026-11-21T01:00:00Z"))
    at = records.at(day, dt("2026-11-20T07:00:00Z"))
    assert at["calls"] == 75  # 10 of the 40 calls in the two hourly bins: 1/4, not 1/2.
    assert at["upstream"]["a"]["failed"] == 6
    assert at["tools"]["x"]["avg_ms"] == 140  # Interpolate duration, not averages.
    assert at["hours"] == hours  # Hourly fields are never blended.
    assert at["approx"]
    assert records.at(day, dt("2026-11-20T07:30:00Z"))["calls"] == 97.5


@pytest.mark.parametrize("hours", [None, [0] * 24, [None] + [10] * 23])
def test_at_time_fraction_fallback(store, hours):
    store.merge_day({"date": "2026-11-20", "calls": 240, "hours": hours, "nullable": None},
                    "2026-11-21T00:00:30Z")
    records = EasternRecords(store, dt("2026-11-21T01:00:00Z"))
    point = records.at("2026-11-20", dt("2026-11-20T06:00:00Z"))
    assert (point["calls"], point["approx"], point["nullable"]) == (60, True, None)


def test_at_uses_latest_unfinished_point_without_extrapolating(store):
    record = {"date": "2026-11-21", "calls": 120, "hours": [10] * 12 + [0] * 12}
    store.save_stats({"days": [record]}, "2026-11-21T12:00:00Z")
    records = EasternRecords(store, dt("2026-11-21T14:00:00Z"))
    assert records.at(record["date"], dt("2026-11-21T12:01:30Z")) == record | {"approx": False}
    assert records.at(record["date"], dt("2026-11-21T13:00:00Z")) == record | {"approx": True}
    # Even after midnight, an old partial row is not a final UTC record.
    records = EasternRecords(store, dt("2026-11-22T02:00:00Z"))
    assert records.at(record["date"], dt("2026-11-22T00:00:00Z")) == record | {"approx": True}


@pytest.mark.parametrize("day,next_day,offset,expected", [
    ("2026-11-20", "2026-11-21", 5, 290),
    ("2026-07-20", "2026-07-21", 4, 280),
])
def test_window_crosses_utc_midnight_and_slices_hourly_lists(store, day, next_day, offset, expected):
    save_day(store, day, snapshots=(offset,))
    save_day(store, next_day, hourly=20, snapshots=(offset,))
    records = EasternRecords(store, dt(next_day + "T23:00:00Z") + timedelta(days=1))
    start, end = eastern_bounds(day)
    result = records.window(start, end)
    assert result["calls"] == expected
    assert result["hours"] == [10] * (24 - offset) + [20] * offset
    assert result["hours_in_window"] == 24
    assert not result["approx"]
    assert result["failed_hours"] is None and result["refused_hours"] is None
    assert (result["start"], result["end"]) == (timestamp(start), timestamp(end))


def test_window_nested_counters_folding_clamping_averages_and_histograms(store):
    lo = {
        "date": "2026-11-20", "calls": 10, "callers": 5,
        "tools": {"search": {"calls": 10, "avg_ms": 100, "failed": 4}},
        "tool_apps": {"search": {"kept": {"calls": 4}, "gone": {"calls": 4}, "other": {"calls": 2}}},
        "distributor_apps": {"lookup": {"gone": {"calls": 3, "rate_limited": 2}}},
        "apps": {"kept": 4, "gone": 6}, "popular_terms": {"kept": 3, "gone": 7},
        "latency": {"search": {"counts": [2, 8], "p50_ms": 100}},
        "parts_asked": {"mouser": {"total": 10, "distinct": 8}},
        "always_null": None,
    }
    hi = deepcopy(lo) | {
        "calls": 20,
        "tools": {"search": {"calls": 20, "avg_ms": 200, "failed": 2}},
        "tool_apps": {"search": {"kept": {"calls": 8}, "other": {"calls": 12}}},
        "distributor_apps": {"lookup": {"other": {"calls": 8, "rate_limited": 3}}},
        "apps": {"kept": 8, "other": 12}, "popular_terms": {"kept": 4},
        "latency": {"search": {"counts": [5, 15], "p50_ms": 250, "p95_ms": 500}},
        "parts_asked": {"mouser": {"total": 15, "distinct": 12}},
    }
    next_day = {"date": "2026-11-21", "calls": 10,
                "tools": {"search": {"calls": 10, "avg_ms": 100, "failed": 1}},
                "latency": {"search": {"counts": [1, 9], "p99_ms": 500}}}
    store.merge_day(hi, "2026-11-21T00:00:30Z")
    store.add_snapshot(lo, "2026-11-20T23:00:00Z")
    store.save_stats({"days": [next_day]}, "2026-11-21T01:00:00Z")
    result = EasternRecords(store, dt("2026-11-21T01:00:00Z")).window(
        dt("2026-11-20T23:00:00Z"), dt("2026-11-21T01:00:00Z"))
    assert result["calls"] == 20
    assert result["tools"]["search"] == {"calls": 20, "avg_ms": 200, "failed": 1}
    assert result["tool_apps"]["search"] == {"kept": {"calls": 4}, "other": {"calls": 6}}
    assert result["distributor_apps"]["lookup"] == {"other": {"calls": 5, "rate_limited": 1}}
    assert result["apps"] == {"kept": 4, "other": 12}
    assert result["popular_terms"] == {"kept": 1}
    assert result["latency"] == {"search": {"counts": [4, 16]}}
    assert result["parts_asked"]["mouser"] == {"total": 5, "distinct": None}
    assert result["callers"] is None and result["always_null"] is None
    assert result["approx"]  # failed went backwards and was clamped before summing.
    assert store.all_days()[0] == hi and lo["tool_apps"]["search"]["gone"]["calls"] == 4


def test_window_hourly_nulls_and_wait_maxima(store):
    first = save_day(store, "2026-11-20", snapshots=(23,)) | {
        "failed_hours": [None] * 24,
        "db_waits": {"longest_ms": 9000, "longest_ms_hours": [9000] + [0] * 22 + [100],
                     "waited_hours": [None] * 24, "components": {"longest_ms": 9000}},
        "distributor_limits": {"mouser": {"held_back_hours": [None] * 23 + [2]}},
    }
    second = save_day(store, "2026-11-21", snapshots=(2,)) | {
        "failed_hours": [None, 0] + [0] * 22,
        "db_waits": {"longest_ms": 8000, "longest_ms_hours": [50, None] + [8000] * 22,
                     "waited_hours": [1, 2] + [0] * 22, "components": {"longest_ms": 8000}},
    }
    store.merge_day(first, "2026-11-21T00:00:30Z")
    store.merge_day(second, "2026-11-22T00:00:30Z")
    result = EasternRecords(store, dt("2026-11-22T01:00:00Z")).window(
        dt("2026-11-20T23:00:00Z"), dt("2026-11-21T02:00:00Z"))
    assert result["failed_hours"] == [None, None, 0]
    assert result["db_waits"]["longest_ms_hours"] == [100, 50, None]
    assert result["db_waits"]["longest_ms"] == 100
    assert result["db_waits"]["components"]["longest_ms"] is None
    assert result["db_waits"]["waited_hours"] == [None, 1, 2]
    assert result["distributor_limits"]["mouser"]["held_back_hours"] == [2, None, None]


def test_missing_utc_day_marks_approx_and_preserves_known_fields(store):
    save_day(store, "2026-11-21", snapshots=(5,))
    records = EasternRecords(store, dt("2026-11-22T00:00:00Z"))
    result = records.eastern_day("2026-11-20")
    assert result["approx"] and result["calls"] == 50
    assert result["hours"] == [None] * 19 + [10] * 5
    assert store.all_eastern_days() == {}  # Never freeze a day with missing UTC inputs.
    assert [day["date"] for day in records.all_days()] == ["2026-11-20", "2026-11-21"]


@pytest.mark.parametrize("day,next_day,first,last,length", [
    ("2026-03-08", "2026-03-09", 5, 4, 23),
    ("2026-11-01", "2026-11-02", 4, 5, 25),
])
def test_dst_days_use_real_elapsed_hours(store, day, next_day, first, last, length):
    save_day(store, day, snapshots=(first,))
    save_day(store, next_day, snapshots=(last,))
    records = EasternRecords(store, dt(next_day + "T00:00:00Z") + timedelta(days=1))
    result = records.eastern_day(day)
    assert result["hours_in_window"] == length and len(result["hours"]) == length
    assert result["calls"] == 10 * length
    assert result["complete"] and not result["approx"]


@pytest.mark.parametrize("exact", [False, True])
def test_persisted_days_are_reused_after_pruning(store, monkeypatch, exact):
    for day in ("2026-11-20", "2026-11-21"):
        save_day(store, day, snapshots=(5,) if exact else ())
    first = EasternRecords(store, dt("2026-11-22T00:00:30Z")).eastern_day("2026-11-20")
    row = store._connection.execute("SELECT approx, computed_at FROM eastern_days").fetchone()
    assert row == (int(not exact), "2026-11-22T00:00:30Z")
    store.prune(dt("2027-01-10T00:00:00Z"))
    assert not store.all_snapshots()

    def forbidden(*_args, **_kwargs):
        pytest.fail("A frozen day must not be recomputed or rewritten")

    monkeypatch.setattr(store, "save_eastern_day", forbidden)
    records = EasternRecords(store, dt("2027-01-10T00:00:00Z"))
    monkeypatch.setattr(records, "window", forbidden)
    assert records.eastern_day("2026-11-20") == first


def test_approximate_cache_upgrades_only_when_exact_inputs_arrive(store):
    for day in ("2026-11-20", "2026-11-21"):
        save_day(store, day)
    first = EasternRecords(store, dt("2026-11-22T00:00:30Z")).eastern_day("2026-11-20")
    assert first["approx"]
    store.add_snapshot({"date": "2026-11-20", "calls": 45}, "2026-11-20T05:00:30Z")
    still = EasternRecords(store, dt("2026-11-22T01:00:00Z")).eastern_day("2026-11-20")
    assert still == first  # A different estimate does not replace a saved estimate.
    store.add_snapshot({"date": "2026-11-21", "calls": 55}, "2026-11-21T05:00:30Z")
    upgraded = EasternRecords(store, dt("2026-11-22T02:00:00Z")).eastern_day("2026-11-20")
    assert upgraded["calls"] == sum(upgraded["hours"]) == 240 and not upgraded["approx"]
    assert store._connection.execute("SELECT approx, computed_at FROM eastern_days").fetchone() == (0, "2026-11-22T02:00:00Z")


def test_persistence_waits_for_both_utc_final_records(store):
    save_day(store, "2026-11-20", snapshots=(5,))
    store.save_stats({"days": [{"date": "2026-11-21", "calls": 60, "hours": [10] * 6 + [0] * 18}]},
                     "2026-11-21T06:00:00Z")
    records = EasternRecords(store, dt("2026-11-21T06:00:00Z"))
    assert records.eastern_day("2026-11-20")["complete"]
    assert not store.all_eastern_days()
    save_day(store, "2026-11-21")
    EasternRecords(store, dt("2026-11-22T00:00:00Z")).eastern_day("2026-11-20")
    assert "2026-11-20" in store.all_eastern_days()


def test_problems_before_deploy_partial_deploy_day_and_later_days(store):
    for day in ("2026-11-20", "2026-11-21", "2026-11-22", "2026-11-23"):
        save_day(store, day, snapshots=(5, 18))
    records = EasternRecords(store, dt("2026-11-24T00:00:00Z"))
    since = dt("2026-11-21T18:00:00Z")
    assert records.eastern_day("2026-11-20", since)["problems"] is None
    deploy = records.eastern_day("2026-11-21", since)["problems"]
    assert (deploy["start"], deploy["end"], deploy["calls"], deploy["hours_in_window"]) == (
        timestamp(since), "2026-11-22T05:00:00Z", 110, 11)
    assert len(deploy["hours"]) == 11 and not deploy["approx"]
    later = records.eastern_day("2026-11-22", since)
    assert later["problems"]["calls"] == later["calls"] == 240
    store.prune(dt("2027-01-15T00:00:00Z"))
    records = EasternRecords(store, dt("2027-01-15T00:00:00Z"))
    assert records.eastern_day("2026-11-21", since)["problems"] == deploy
    # A changed cutoff must not leak the old deploy window from the cache.
    assert records.eastern_day("2026-11-21", dt("2026-11-23T00:00:00Z"))["problems"] is None


def test_live_partial_hour_is_not_scaled_twice_and_zero_midnight_window(store):
    save_day(store, "2026-11-21", snapshots=(5,))
    live = {"date": "2026-11-22", "calls": 45, "hours": [10] * 4 + [5] + [0] * 19}
    store.save_stats({"days": [live]}, "2026-11-22T04:30:00Z")
    records = EasternRecords(store, dt("2026-11-22T04:30:00Z"))
    day = records.eastern_day("2026-11-21", dt("2026-11-22T04:00:00Z"))
    assert day["hours"][-1] == 5 and day["hours_in_window"] == 24
    assert day["problems"]["hours"] == [5]
    assert not day["complete"]
    records = EasternRecords(store, dt("2026-11-22T05:00:00Z"))
    midnight = records.eastern_day("2026-11-22")
    assert midnight["calls"] == 0 and midnight["hours_in_window"] == 0
    assert midnight["problems"] is None


@pytest.mark.parametrize("snapshot", [True, False])
def test_compare_today_uses_near_snapshot_or_interpolation_and_scales_last_hour(store, snapshot):
    save_day(store, "2026-11-20", hourly=60, snapshots=(5,))
    if snapshot:
        store.add_snapshot({"date": "2026-11-20", "calls": 930}, "2026-11-20T15:30:30Z")
    records = EasternRecords(store, dt("2026-11-21T15:30:00Z"))
    result = records.compare_today()
    assert result["date"] == "2026-11-20"
    assert result["end"] == "2026-11-20T15:30:00Z"
    assert result["calls"] == 630
    assert result["hours"] == [60] * 10 + [30]
    assert result["hours_in_window"] == 11
    assert result["approx"] and not result["exact_calls"]  # The ending bin is estimated.


@pytest.mark.parametrize("as_of,expected_end,hours", [
    ("2026-03-09T16:00:00Z", "2026-03-08T16:00:00Z", 11),
    ("2026-11-02T17:00:00Z", "2026-11-01T17:00:00Z", 13),
    ("2026-03-09T06:30:00Z", "2026-03-08T07:30:00Z", 3),
    ("2026-11-02T06:30:00Z", "2026-11-01T05:30:00Z", 2),
])
def test_compare_today_uses_calendar_time_across_dst(store, as_of, expected_end, hours):
    save_day(store, expected_end[:10])
    result = EasternRecords(store, dt(as_of)).compare_today()
    assert result["end"] == expected_end
    assert result["hours_in_window"] == hours


def test_compare_today_is_null_without_any_yesterday_inputs(store):
    save_day(store, "2026-11-21", snapshots=(5,))
    # Yesterday overlaps Nov 21 from 00–05 UTC, so it has partial data, flagged approximate.
    assert EasternRecords(store, dt("2026-11-21T19:00:00Z")).compare_today()["approx"]
    assert EasternRecords(store, dt("2026-11-24T19:00:00Z")).compare_today() is None


def test_non_hour_aligned_problem_start_is_supported_as_an_estimate(store):
    save_day(store, "2026-11-20")
    records = EasternRecords(store, dt("2026-11-21T02:00:00Z"))
    result = records.eastern_day("2026-11-20", dt("2026-11-20T18:30:00Z"))["problems"]
    assert result["start"] == "2026-11-20T18:30:00Z" and result["approx"]
    assert result["hours"][0] == 5


def test_window_zero_calls_unknown_fields_and_component_hourly_data(store):
    record = {
        "date": "2026-11-20", "calls": 0, "hours": [0] * 24,
        "tools": {"idle": {"calls": 0, "avg_ms": 0}}, "latency": None,
        "db_waits": {"components": {
            "waited_hours": [None] * 5 + [3] + [None] * 18,
            "longest_ms_hours": [None] * 5 + [123] + [None] * 18,
        }},
        "parts_asked": {"mouser": {"total": 0, "distinct": 0}},
    }
    store.merge_day(record, "2026-11-21T00:00:30Z")
    records = EasternRecords(store, dt("2026-11-21T01:00:00Z"))
    result = records.window(dt("2026-11-20T05:00:00Z"), dt("2026-11-20T07:00:00Z"))
    assert result["calls"] == 0 and result["tools"]["idle"]["avg_ms"] is None
    assert result["latency"] is None and result["parts_asked"]["mouser"]["distinct"] is None
    assert result["db_waits"]["components"] == {
        "waited_hours": [3, None], "longest_ms_hours": [123, None], "longest_ms": 123,
    }
    empty = records.window(dt("2026-11-20T05:30:00Z"), dt("2026-11-20T05:30:00Z"))
    assert empty["calls"] == 0 and empty["hours_in_window"] == 0 and empty["hours"] is None
    assert not empty["approx"]


def test_cached_future_day_is_not_used_for_an_earlier_data_horizon(store):
    save_day(store, "2026-11-20", snapshots=(5, 12))
    save_day(store, "2026-11-21", snapshots=(5,))
    EasternRecords(store, dt("2026-11-22T00:00:00Z")).eastern_day("2026-11-20")
    earlier = EasternRecords(store, dt("2026-11-20T12:00:30Z")).eastern_day("2026-11-20")
    assert earlier["end"] == "2026-11-20T12:00:30Z" and not earlier["complete"]
    assert earlier["calls"] == 70
    assert store.all_eastern_days()["2026-11-20"]["complete"]


def test_cached_partial_problems_can_upgrade_without_recomputing_exact_day(store):
    for day in ("2026-11-20", "2026-11-21"):
        save_day(store, day, snapshots=(5,))
    since = dt("2026-11-20T18:00:00Z")
    original = EasternRecords(store, dt("2026-11-22T00:00:00Z")).eastern_day("2026-11-20", since)
    assert not original["approx"] and original["problems"]["approx"]
    store.add_snapshot({"date": "2026-11-20", "calls": 180, "hours": [10] * 18 + [0] * 6},
                       "2026-11-20T18:00:30Z")
    updated = EasternRecords(store, dt("2026-11-22T01:00:00Z")).eastern_day("2026-11-20", since)
    assert updated["calls"] == original["calls"]
    assert updated["problems"]["calls"] == 110 and not updated["problems"]["approx"]
