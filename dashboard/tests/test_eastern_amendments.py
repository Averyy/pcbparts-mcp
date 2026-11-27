"""Regression cases for docs/eastern-days-spec-amendments.md (rules version 2)."""

from copy import deepcopy
from dataclasses import replace
import sqlite3

import httpx
import pytest

from pcbparts_dashboard.collector import collect
from pcbparts_dashboard.eastern import EasternRecords, FAILURE_REASONS, OUTCOMES, RULES_VERSION
from pcbparts_dashboard.payload import build_payload
from pcbparts_dashboard.store import Store, parse_timestamp as dt


def series(hour, value):
    result = [0] * 24
    result[hour] = value
    return result


def rare_events():
    return {
        "date": "2026-11-20", "calls": 240, "hours": [10] * 24,
        "failed_hours": series(4, 8), "refused_hours": series(6, 7),
        "tools": {"search": {
            "calls": 240, "ok": 200, "similar_only": 0, "not_found": 32,
            "bad_request": 0, "rate_limited": 0, "failed": 8, "avg_ms": 250,
        }},
        "reasons": {"search": {"exception": 8, "no_results": 32}},
        "per_ip_refusals": {"total": 7, "everyone_else": 5, "platform_ranges": 2},
        "distributors": {"mouser": {"rate_limited": 11}},
        "distributor_limits": {"mouser": {
            "held_back": {"minute_cap": 6, "daily_count": 5},
            "held_back_hours": series(7, 11), "refusals": {"daily": 20},
        }},
        "db_waits": {"jobs": 80, "waited": 13, "waited_hours": series(8, 13),
                     "components": {"jobs": 40, "waited": 17, "waited_hours": series(3, 17)}},
        "upstream": {"jlcpcb": {"failed": 20}},
    }


def records_for(store, record):
    store.merge_day(record, "2026-11-21T00:00:30Z")
    return EasternRecords(store, dt("2026-11-21T01:00:00Z"))


@pytest.mark.parametrize("label", sorted(FAILURE_REASONS))
def test_each_failure_label_uses_failed_hours_and_other_fields_use_calls(store, label):
    record = rare_events()
    record["reasons"]["search"] = {label: 8, "no_results": 32}
    point = records_for(store, record).at(record["date"], dt("2026-11-20T06:00:00Z"))
    assert point["tools"]["search"]["failed"] == 8
    assert point["reasons"]["search"] == {label: 8, "no_results": 8}
    assert point["per_ip_refusals"]["total"] == 0
    assert point["distributors"]["mouser"]["rate_limited"] == 0
    assert point["distributor_limits"]["mouser"]["held_back"] == {"minute_cap": 0, "daily_count": 0}
    assert point["db_waits"]["waited"] == 0
    assert point["db_waits"]["components"]["waited"] == 17
    assert point["db_waits"]["jobs"] == 20
    assert point["upstream"]["jlcpcb"]["failed"] == 5
    assert point["distributor_limits"]["mouser"]["refusals"]["daily"] == 5
    assert point["tools"]["search"]["calls"] == 60
    assert point["tools"]["search"]["avg_ms"] == 250


@pytest.mark.parametrize("missing", [None, [None] * 24, [None] + [0] * 23])
def test_missing_sibling_falls_back_to_call_share_not_elapsed_time(store, missing):
    record = rare_events()
    record["hours"] = [30] * 6 + [10] * 18
    record["failed_hours"] = record["refused_hours"] = missing
    record["distributor_limits"]["mouser"]["held_back_hours"] = missing
    record["db_waits"]["waited_hours"] = missing
    record["db_waits"]["components"]["waited_hours"] = missing
    point = records_for(store, record).at(record["date"], dt("2026-11-20T06:00:00Z"))
    assert point["tools"]["search"]["failed"] == 4
    assert point["per_ip_refusals"]["total"] == 3.5
    assert point["distributors"]["mouser"]["rate_limited"] == 5.5
    assert point["db_waits"]["waited"] == 6.5
    assert point["db_waits"]["components"]["waited"] == 8.5


def test_hourly_totals_override_snapshot_deltas_and_rare_events_stay_on_their_day(store):
    record = rare_events()
    records_for(store, record)
    # A near boundary sample disagrees with the recorded hourly totals.
    sample = deepcopy(record)
    sample["calls"] = 40
    sample["tools"]["search"].update(calls=40, failed=0)
    store.add_snapshot(sample, "2026-11-20T05:00:00Z")
    records = EasternRecords(store, dt("2026-11-21T01:00:00Z"))
    window = records.window(dt("2026-11-20T05:00:00Z"), dt("2026-11-21T00:00:00Z"))
    assert window["calls"] == sum(window["hours"]) == 190
    assert window["tools"]["search"]["failed"] == sum(window["failed_hours"]) == 0
    assert window["reasons"]["search"]["exception"] == 0
    assert window["per_ip_refusals"]["total"] == sum(window["refused_hours"]) == 7
    assert sum(v for k, v in window["per_ip_refusals"].items() if k != "total") == 7
    limits = window["distributor_limits"]["mouser"]
    assert sum(limits["held_back"].values()) == sum(limits["held_back_hours"]) == 11
    assert window["distributors"]["mouser"]["rate_limited"] == 11
    assert window["db_waits"]["waited"] == sum(window["db_waits"]["waited_hours"]) == 13
    assert window["db_waits"]["components"]["waited"] == 0
    assert window["exact_calls"]


def test_partially_recorded_siblings_use_known_bins_and_estimate_only_gaps(store):
    record = rare_events()
    record["refused_hours"] = [None] * 5 + [3] + [None] * 18
    record["per_ip_refusals"] = {"total": 24, "everyone_else": 24}
    window = records_for(store, record).window(dt("2026-11-20T04:00:00Z"), dt("2026-11-20T07:00:00Z"))
    assert window["refused_hours"] == [None, 3, None]
    assert window["per_ip_refusals"] == {"total": 5, "everyone_else": 5}
    assert window["approx"] and window["exact_calls"]


def test_round_once_after_subtraction_and_across_days_with_largest_remainders(store):
    for day in ("2026-11-20", "2026-11-21"):
        store.merge_day({
            "date": day, "calls": 10, "other_count": 10,
            "tools": {"search": {"calls": 10, "ok": 5, "similar_only": 0,
                "not_found": 3, "bad_request": 0, "rate_limited": 0, "failed": 2, "avg_ms": 100}},
            "reasons": {"search": {"no_results": 3, "exception": 1, "unexpected_error": 1}},
            "per_ip_refusals": {"total": 10, "everyone_else": 3, "platform_ranges": 3, "server_busy": 4},
        }, "2026-11-22T00:00:00Z")
    records = EasternRecords(store, dt("2026-11-22T00:00:00Z"))
    assert records.at("2026-11-20", dt("2026-11-20T23:00:00Z"))["calls"] == pytest.approx(10 * 23 / 24)
    window = records.window(dt("2026-11-20T23:00:00Z"), dt("2026-11-21T01:00:00Z"))
    assert window["calls"] == window["other_count"] == 1
    tool = window["tools"]["search"]
    assert sum(tool[key] for key in OUTCOMES) == tool["calls"] == 1
    assert tool["ok"] == 1 and tool["avg_ms"] == pytest.approx(100)
    assert sum(window["reasons"]["search"].values()) == tool["not_found"] + tool["failed"]
    assert window["per_ip_refusals"] == {"total": 1, "everyone_else": 0, "platform_ranges": 0, "server_busy": 1}
    assert window["approx"] and not window["exact_calls"]


def test_fractional_bins_round_once_and_totals_match_the_rounded_chart(store):
    records = records_for(store, {"date": "2026-11-20", "calls": 2, "hours": [1, 1] + [0] * 22})
    window = records.window(dt("2026-11-20T00:30:00Z"), dt("2026-11-20T01:30:00Z"), scale_end=True)
    assert window["hours"] == [0, 0]  # Python nearest-even rounding, once per finished bin.
    assert window["calls"] == 0
    assert window["approx"] and not window["exact_calls"]


def test_without_failure_hours_largest_remainder_rounds_all_six_outcomes_together(store):
    record = {"date": "2026-11-20", "calls": 6,
              "tools": {"search": {"calls": 6, **dict.fromkeys(OUTCOMES, 1)}}}
    window = records_for(store, record).window(dt("2026-11-20T00:00:00Z"), dt("2026-11-20T14:00:00Z"))
    tool = window["tools"]["search"]
    assert tool["calls"] == 4
    assert [tool[key] for key in OUTCOMES] == [1, 1, 1, 1, 0, 0]


def test_recorded_failures_constrain_tool_call_and_outcome_apportionment(store):
    record = {"date": "2026-11-20", "calls": 240, "hours": [10] * 24,
              "failed_hours": series(4, 8), "tools": {
                  "rare": {**dict.fromkeys(OUTCOMES, 0), "calls": 8, "failed": 8},
                  "busy": {**dict.fromkeys(OUTCOMES, 0), "calls": 232, "ok": 232},
              }}
    window = records_for(store, record).window(dt("2026-11-20T04:00:00Z"), dt("2026-11-20T05:00:00Z"))
    assert window["calls"] == sum(t["calls"] for t in window["tools"].values()) == 10
    assert sum(t["failed"] for t in window["tools"].values()) == sum(window["failed_hours"]) == 8
    assert window["tools"]["rare"]["calls"] == 8
    assert window["tools"]["busy"]["calls"] == 2
    assert all(sum(t[key] for key in OUTCOMES) == t["calls"] for t in window["tools"].values())


def test_each_distributor_uses_its_own_held_back_series(store):
    record = rare_events()
    record["distributors"]["digikey"] = {"rate_limited": 5}
    record["distributor_limits"]["digikey"] = {"held_back": {"address_daily": 5}, "held_back_hours": series(4, 5)}
    records = records_for(store, record)
    point = records.at(record["date"], dt("2026-11-20T06:00:00Z"))
    assert point["distributors"]["digikey"]["rate_limited"] == 5
    assert point["distributors"]["mouser"]["rate_limited"] == 0
    window = records.window(dt("2026-11-20T05:00:00Z"), dt("2026-11-20T09:00:00Z"))
    assert window["distributor_limits"]["digikey"]["held_back"]["address_daily"] == 0
    assert window["distributors"]["digikey"]["rate_limited"] == 0
    assert window["distributors"]["mouser"]["rate_limited"] == 11


def baseline_inputs(store, *, baseline_at="2026-11-21T18:04:00Z", new_at="2026-11-21T19:00:00Z"):
    base = {
        "date": "2026-11-21", "calls": 100, "hours": series(17, 90),
        "tools": {"search": {"calls": 100, "ok": 80, "similar_only": 0, "not_found": 10,
                             "bad_request": 0, "rate_limited": 0, "failed": 10, "avg_ms": 100}},
        "failed_hours": series(17, 9), "reasons": {"search": {"exception": 10, "no_results": 10}},
    }
    base["hours"][18] = 10
    base["failed_hours"][18] = 1
    current = deepcopy(base)
    current["calls"] = 150
    current["hours"][18] = 60
    current["tools"]["search"].update(calls=150, ok=130)
    store.save_stats({"days": [base]}, baseline_at)
    store.save_stats({"days": [current]}, "2026-11-21T19:00:00Z")
    store.save_health({"version": "0.10.5"}, new_at)
    return base, current


def test_problems_uses_1804_snapshot_as_is_and_keeps_cutoff_hour_labels(store):
    baseline_inputs(store)
    records = EasternRecords(store, dt("2026-11-21T19:00:00Z"), "0.10.5")
    window = records.eastern_day("2026-11-21", dt("2026-11-21T18:00:00Z"))["problems"]
    assert window["start"] == "2026-11-21T18:00:00Z"
    assert window["hours_in_window"] == 1
    assert window["calls"] == sum(window["hours"]) == 50
    assert window["failed_hours"] == [0]
    assert window["tools"]["search"]["failed"] == 0
    assert window["reasons"]["search"]["exception"] == 0
    assert not window["approx"] and window["exact_calls"]


def test_exact_baseline_totals_recover_missing_snapshot_hourly_fields(store):
    base, _ = baseline_inputs(store)
    base.pop("hours")
    base.pop("failed_hours")
    store.add_snapshot(base, "2026-11-21T18:04:00Z")
    window = EasternRecords(store, dt("2026-11-21T19:00:00Z")).eastern_day(
        "2026-11-21", dt("2026-11-21T18:00:00Z"))["problems"]
    assert window["calls"] == 50 and window["failed_hours"] == [0]
    assert not window["approx"] and window["exact_calls"]


@pytest.mark.parametrize("latest,approx", [(1000, False), (900, True)])
def test_problems_baseline_does_not_subtract_hourly_wait_maxima(store, latest, approx):
    base, current = baseline_inputs(store)
    base["db_waits"] = {"waited": 2, "waited_hours": series(18, 2), "longest_ms_hours": series(18, 900)}
    current["db_waits"] = {"waited": 3, "waited_hours": series(18, 3), "longest_ms_hours": series(18, latest)}
    store.add_snapshot(base, "2026-11-21T18:04:00Z")
    store.save_stats({"days": [current]}, "2026-11-21T19:00:00Z")
    window = EasternRecords(store, dt("2026-11-21T19:00:00Z")).eastern_day(
        "2026-11-21", dt("2026-11-21T18:00:00Z"))["problems"]
    assert window["db_waits"]["waited"] == 1
    assert window["db_waits"]["longest_ms"] == latest
    assert window["approx"] is approx


def test_nearby_problems_baseline_can_cross_a_utc_midnight(store):
    store.merge_day({"date": "2026-11-20", "calls": 10, "hours": series(23, 10)}, "2026-11-21T00:04:00Z")
    store.save_stats({"days": [{"date": "2026-11-21", "calls": 3, "hours": series(0, 3)}]}, "2026-11-21T00:04:00Z")
    store.save_stats({"days": [{"date": "2026-11-21", "calls": 8, "hours": series(0, 8)}]}, "2026-11-21T01:00:00Z")
    window = EasternRecords(store, dt("2026-11-21T01:00:00Z")).eastern_day(
        "2026-11-20", dt("2026-11-20T23:58:00Z"))["problems"]
    assert window["hours"] == [0, 5] and window["calls"] == 5
    assert not window["approx"] and window["exact_calls"]


def test_midnight_problems_baseline_survives_snapshot_pruning(store):
    for day in ("2026-11-20", "2026-11-21"):
        store.merge_day({"date": day, "calls": 240, "hours": [10] * 24}, "2026-11-22T00:00:00Z")
    store.add_snapshot({"date": "2026-11-20", "calls": 52, "hours": [10] * 5 + [2] + [0] * 18},
                       "2026-11-20T05:04:00Z")
    since = dt("2026-11-20T05:00:00Z")
    saved = EasternRecords(store, dt("2026-11-22T00:00:00Z")).eastern_day("2026-11-20", since)
    assert saved["calls"] == 240 and saved["problems"]["calls"] == 238
    store.prune(dt("2027-02-01T00:00:00Z"))
    later = EasternRecords(store, dt("2027-02-01T00:00:00Z")).eastern_day("2026-11-20", since)
    assert later["problems"] == saved["problems"]


@pytest.mark.parametrize("baseline_at,new_at,expected", [
    ("2026-11-21T18:10:00Z", "2026-11-21T19:00:00Z", 50),
    ("2026-11-21T18:10:01Z", "2026-11-21T19:00:00Z", 60),
    ("2026-11-21T18:04:00Z", "2026-11-21T18:04:00Z", 60),
    ("2026-11-21T18:04:00Z", "2026-11-21T18:03:00Z", 60),
])
def test_nearby_baseline_must_be_within_ten_minutes_and_before_new_version(store, baseline_at, new_at, expected):
    baseline_inputs(store, baseline_at=baseline_at, new_at=new_at)
    records = EasternRecords(store, dt("2026-11-21T19:00:00Z"), "0.10.5")
    window = records.eastern_day("2026-11-21", dt("2026-11-21T18:00:00Z"))["problems"]
    assert window["calls"] == expected
    assert window["approx"] is (expected == 60)


def test_auto_cutoff_uses_last_old_health_fetch_and_its_exact_stats_snapshot(store, settings):
    base, current = baseline_inputs(store)
    version = "0.10.4"
    reply = base

    def respond(request):
        return httpx.Response(200, json={"days": [reply]} if request.url.path == "/mcp/stats" else {"version": version})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        collect(settings, store, client=client, now=dt("2026-11-21T18:04:00Z"))
        version = None  # A later stats fetch without a health version is not the baseline.
        collect(settings, store, client=client, now=dt("2026-11-21T18:20:00Z"))
        version, reply = "0.10.5", current
        collect(settings, store, client=client, now=dt("2026-11-21T19:00:00Z"))
    payload = build_payload(store, settings, dt("2026-11-21T19:00:00Z"))
    assert payload["problems_since"] == "2026-11-21T18:04:00Z"
    assert payload["version_since"] == {"version": "0.10.5", "since": payload["problems_since"]}
    window = payload["edays"][-1]["problems"]
    assert window["calls"] == 50 and window["hours"] == [50]
    assert not window["approx"] and window["exact_calls"]


def test_rules_version_migrates_legacy_table_without_discarding_rows(tmp_path):
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE eastern_days(date TEXT PRIMARY KEY, data TEXT NOT NULL, approx INTEGER NOT NULL, computed_at TEXT NOT NULL)")
        connection.execute("INSERT INTO eastern_days VALUES ('2026-11-20', '{}', 1, '2026-11-22T00:00:00Z')")
    with Store(path) as store:
        assert store.eastern_rules_versions() == {"2026-11-20": 1}
        assert store.all_eastern_days() == {"2026-11-20": {}}


@pytest.mark.parametrize("pruned", [False, True])
@pytest.mark.parametrize("old_approx", [False, True])
def test_old_rules_recompute_with_inputs_and_preserve_rows_after_pruning(store, pruned, old_approx):
    for day in ("2026-11-20", "2026-11-21"):
        store.merge_day({"date": day, "calls": 240, "hours": [10] * 24}, "2026-11-22T00:00:00Z")
        store.add_snapshot({"date": day, "calls": 50}, day + "T05:00:00Z")
    records = EasternRecords(store, dt("2026-11-22T00:00:00Z"))
    saved = records.eastern_day("2026-11-20")
    assert store.eastern_rules_versions()["2026-11-20"] == RULES_VERSION
    old = saved | {"calls": 999, "approx": old_approx}
    old["problems"] = old["problems"] | {"calls": 999, "approx": old_approx}
    store.save_eastern_day(old, "2026-11-22T00:00:00Z", rules_version=1)
    if pruned:
        store.prune(dt("2027-02-01T00:00:00Z"))
    updated = EasternRecords(store, dt("2027-02-01T00:00:00Z")).eastern_day("2026-11-20")
    assert updated["calls"] == updated["problems"]["calls"] == (999 if pruned else 240)
    assert store.eastern_rules_versions()["2026-11-20"] == (1 if pruned else RULES_VERSION)


def test_header_version_since_uses_matching_cutoff_or_first_observation_and_survives_pruning(store, settings):
    first, latest = "2026-11-21T19:00:00Z", "2027-02-01T19:00:00Z"
    store.save_health({"version": "0.10.5"}, first)
    store.save_health({"version": "0.10.5"}, latest)
    store.prune(dt(latest))
    assert build_payload(store, settings, dt(latest))["version_since"] == {"version": "0.10.5", "since": first}
    configured = replace(settings, problems_since="2026-11-21T18:00:00Z", problems_version="0.10.5")
    assert build_payload(store, configured, dt(latest))["version_since"]["since"] == configured.problems_since
    mismatch = replace(configured, problems_version="0.10.6")
    assert build_payload(store, mismatch, dt(latest))["version_since"] == {"version": "0.10.5", "since": first}


def test_first_version_fetch_is_recovered_from_legacy_health_before_pruning(store):
    with store._connection:
        store._connection.execute("INSERT INTO health(fetched_at, data) VALUES (?, ?)",
                                  ("2026-11-21T18:04:00Z", '{"version": "0.10.5"}'))
    store.save_health({"version": "0.10.5"}, "2027-02-01T19:00:00Z")
    store.prune(dt("2027-02-01T19:00:00Z"))
    assert store.version_fetch_at("0.10.5") == "2026-11-21T18:04:00Z"


def test_rescale_never_invents_an_even_split():
    # Rules 3: a total with no recorded causes goes under "other", never evenly across causes.
    from pcbparts_dashboard.eastern import _apportion
    causes = ("minute_cap", "daily_count", "address_daily", "address_blocked", "other")
    record = {"distributor_limits": {"digikey": {"held_back": {c: 0 for c in causes}}}}
    paths = [("distributor_limits", "digikey", "held_back", c) for c in causes]
    _apportion(record, paths, 10)
    assert record["distributor_limits"]["digikey"]["held_back"] == {"minute_cap": 0, "daily_count": 0, "address_daily": 0,
                                                                    "address_blocked": 0, "other": 10}
    no_other = {"x": {"a": 0, "b": 0}}
    _apportion(no_other, [("x", "a"), ("x", "b")], 7)
    assert no_other == {"x": {"a": 0, "b": 0}}  # no basis and no "other": left as recorded


def test_old_rules_days_from_before_any_snapshot_are_recomputed_without_snapshots(store):
    # Days that never had snapshots lose nothing by being recomputed from their final records.
    for day in ("2026-11-20", "2026-11-21"):
        store.merge_day({"date": day, "calls": 240, "hours": [10] * 24}, "2026-11-22T00:00:00Z")
    store.add_snapshot({"date": "2026-11-22", "calls": 5}, "2026-11-22T00:30:00Z")
    saved = EasternRecords(store, dt("2026-11-22T01:00:00Z")).eastern_day("2026-11-20")
    store.save_eastern_day(saved | {"calls": 999}, "2026-11-22T01:00:00Z", rules_version=1)
    store.prune(dt("2027-02-01T00:00:00Z"))
    assert store.first_snapshot_date() == "2026-11-22"
    updated = EasternRecords(store, dt("2027-02-01T00:00:00Z")).eastern_day("2026-11-20")
    assert updated["calls"] == 240
    assert store.eastern_rules_versions()["2026-11-20"] == RULES_VERSION


def test_digikey_ext_split_needs_every_utc_part_to_have_it(store):
    # From server 0.10.11, distributors.digikey.ext_sent sits inside sent. A UTC day counted
    # without it has one figure, so an Eastern day taking sent lookups from it has no split at all.
    days = {
        "2026-11-19": {"sent": 48, "cached": 2, "rate_limited": 0},  # before 0.10.11: unsplit
        "2026-11-20": {"sent": 48, "cached": 0, "rate_limited": 0, "ext_sent": 24},
        "2026-11-21": {"sent": 24, "cached": 0, "rate_limited": 0, "ext_sent": 0},
    }
    for day, final, digikey in zip(days, ("2026-11-20", "2026-11-21", "2026-11-22"), days.values()):
        store.merge_day({"date": day, "calls": 240, "hours": [10] * 24,
                         "distributors": {"digikey": digikey, "mouser": {"sent": 24}},
                         "upstream": {"digikey": {"sent": 24}, "digikey_ext": {"sent": 24}}},
                        final + "T00:00:30Z")
    store.merge_day({"date": "2026-11-22", "calls": 0, "hours": [0] * 24}, "2026-11-23T00:00:30Z")
    records = EasternRecords(store, dt("2026-11-23T00:00:30Z"))
    straddling = records.eastern_day("2026-11-19")  # UTC 11-19 05:00 to 11-20 05:00
    assert straddling["distributors"]["digikey"] == {"sent": 48, "cached": 2, "rate_limited": 0}
    assert straddling["distributors"]["mouser"] == {"sent": 24}
    split = records.eastern_day("2026-11-20")  # UTC 11-20 05:00 to 11-21 05:00: both parts split
    assert split["distributors"]["digikey"] == {"sent": 43, "cached": 0, "rate_limited": 0, "ext_sent": 19}
    assert split["upstream"]["digikey_ext"] == {"sent": 24}
    last = records.eastern_day("2026-11-21")  # the UTC 11-22 part sent nothing: the split stands
    assert last["distributors"]["digikey"] == {"sent": 19, "cached": 0, "rate_limited": 0, "ext_sent": 0}


def test_digikey_split_is_decided_from_the_records_not_the_subtracted_part(store):
    # 0.10.11 counted the day from midnight (ext_sent at 10:00), an earlier version ran from 12:00 and
    # dropped the field, and 0.10.11 came back at 14:00 finding the day's counts without it.
    day = "2026-11-20"
    hours = [10] * 24

    def record(calls, digikey):
        return {"date": day, "calls": calls, "hours": hours[:calls // 10] + [0] * (24 - calls // 10),
                "distributors": {"digikey": digikey}}

    store.add_snapshot(record(100, {"sent": 10, "cached": 0, "rate_limited": 0, "ext_sent": 5}), day + "T10:00:30Z")
    store.add_snapshot(record(130, {"sent": 20, "cached": 0, "rate_limited": 0}), day + "T13:00:30Z")
    store.merge_day(record(240, {"sent": 40, "cached": 0, "rate_limited": 0}), "2026-11-21T00:00:30Z")
    records = EasternRecords(store, dt("2026-11-21T01:00:00Z"))
    # lo (05:00) is blended from midnight and the 10:00 record, so it has ext_sent; the final record
    # doesn't: subtracting gave ext_sent 0 and a split that put every later ext lookup under the API
    later = records.window(dt(day + "T05:00:00Z"), dt("2026-11-21T00:00:00Z"))
    assert later["distributors"]["digikey"] == {"sent": 35, "cached": 0, "rate_limited": 0}
    # the hours before the earlier version ran were counted split, by records that all have it
    before = records.window(dt(day + "T00:00:00Z"), dt(day + "T10:00:00Z"))
    assert before["distributors"]["digikey"] == {"sent": 10, "cached": 0, "rate_limited": 0, "ext_sent": 5}


def test_digikey_split_after_a_problems_baseline_then_a_rollback_is_dropped(store):
    # The problems window starts from an exact baseline snapshot (12:05, split); an earlier version
    # then ran and dropped the field, so the records after it count the day's lookups unsplit.
    day = "2026-11-20"

    def record(calls, digikey):
        return {"date": day, "calls": calls, "hours": [10] * (calls // 10) + [0] * (24 - calls // 10),
                "distributors": {"digikey": digikey}}

    store.add_snapshot(record(120, {"sent": 10, "cached": 0, "rate_limited": 0, "ext_sent": 5}), day + "T12:05:00Z")
    store.add_snapshot(record(130, {"sent": 20, "cached": 0, "rate_limited": 0}), day + "T13:00:30Z")
    store.merge_day(record(240, {"sent": 40, "cached": 0, "rate_limited": 0}), "2026-11-21T00:00:30Z")
    records = EasternRecords(store, dt("2026-11-21T01:00:00Z"))
    start, end = dt(day + "T12:00:00Z"), dt("2026-11-21T00:00:00Z")
    baseline = records._problem_baseline(start, end)
    assert baseline is not None and baseline[0] == dt(day + "T12:05:00Z")
    # lo is the baseline record (ext_sent 5), hi the final record (none): subtracted, that read as 0
    problems = records.window(start, end, baseline=baseline)
    assert problems["distributors"]["digikey"] == {"sent": 30, "cached": 0, "rate_limited": 0}
