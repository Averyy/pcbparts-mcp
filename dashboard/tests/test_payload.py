from dataclasses import replace
from datetime import timedelta

from pcbparts_dashboard.payload import build_payload
from pcbparts_dashboard.store import parse_timestamp, timestamp


def test_empty_payload_shape(store, settings, clock):
    assert build_payload(store, settings, clock()) == {
        "generated_at": timestamp(clock()), "poll_minutes": 60, "next_poll_at": None,
        "last_fetch": None, "last_success_at": None, "warnings": [],
        "latency_bounds_ms": [], "about": None, "kept_across_restarts": None, "edays": [],
        "compare_today": None, "health": None, "health_at": None,
        "as_of": None, "timezone": "America/New_York",
        "problems_since": None, "problems_version": None, "version_since": None,
        "versions": [], "catalog_changes": [],
    }


def test_payload_recuts_days_and_preserves_other_metadata(store, settings, clock, stats_reply, health_reply):
    store.save_stats(stats_reply, timestamp(clock()))
    store.save_health(health_reply, timestamp(clock()))
    store.save_health({"older": True}, timestamp(clock() - timedelta(hours=1)))
    store.set_meta("last_success_at", timestamp(clock()))
    store.set_meta("last_fetch", {"ok": True})
    store.set_meta("warnings", [{"at": timestamp(clock()), "message": "example"}])
    payload = build_payload(store, settings, clock())
    assert "days" not in payload and "compare" not in payload
    assert [day["date"] for day in payload["edays"]] == [
        "2026-11-18", "2026-11-19", "2026-11-20", "2026-11-21",
    ]
    assert all("problems" in day for day in payload["edays"])
    assert payload["edays"][0]["approx"]
    assert payload["edays"][0]["partial_start"]
    assert all(not day["partial_start"] for day in payload["edays"][1:])
    assert all(not day["partial_end"] for day in payload["edays"][:-1])
    assert payload["edays"][-1]["partial_end"]
    assert payload["edays"][-1]["complete"] is False
    assert payload["edays"][-1]["end"] == payload["as_of"] == timestamp(clock())
    assert payload["about"] == stats_reply["about"]
    assert payload["latency_bounds_ms"] == stats_reply["latency_bounds_ms"]
    assert payload["health"] == health_reply
    assert payload["health_at"] == timestamp(clock())
    assert payload["last_success_at"] == timestamp(clock())
    assert payload["last_fetch"] == {"ok": True}
    assert payload["warnings"][0]["message"] == "example"
    assert store.all_days() == list(reversed(stats_reply["days"]))


def test_compare_and_today_follow_last_fetch_not_request_time(store, settings, clock):
    fetched = clock() - timedelta(minutes=40)
    store.set_meta("last_success_at", timestamp(fetched))
    target = fetched - timedelta(days=1)
    store.merge_day({"date": "2026-11-20", "calls": 240, "hours": [10] * 24}, timestamp(fetched))
    store.add_snapshot({"date": "2026-11-20", "calls": 50}, "2026-11-20T05:00:30Z")
    store.add_snapshot({"date": "2026-11-20", "calls": 150}, timestamp(target))
    store.add_snapshot({"date": "2026-11-20", "calls": 200}, timestamp(target + timedelta(minutes=40)))
    payload = build_payload(store, settings, clock())
    assert payload["compare_today"]["calls"] == sum(payload["compare_today"]["hours"]) == 137
    assert payload["compare_today"]["end"] == timestamp(target)
    assert payload["as_of"] == timestamp(fetched)
    assert payload["edays"][-1]["end"] == timestamp(fetched)


def test_problems_settings_override_metadata_and_cached_windows(store, settings, clock, stats_reply):
    store.save_stats(stats_reply, timestamp(clock()))
    store.set_meta("last_success_at", timestamp(clock()))
    store.set_meta("problems_since", "2026-11-20T18:00:00Z")
    store.set_meta("problems_version", "old")
    assert build_payload(store, settings, clock())["problems_version"] == "old"
    configured = replace(settings, problems_since="2026-11-21T18:00:00Z", problems_version="0.10.5")
    payload = build_payload(store, configured, clock())
    assert payload["problems_since"] == "2026-11-21T18:00:00Z"
    assert payload["problems_version"] == "0.10.5"
    assert all(day["problems"] is None for day in payload["edays"][:-1])
    assert payload["edays"][-1]["problems"]["start"] == payload["problems_since"]
    assert payload["edays"][-1]["problems"]["end"] == timestamp(clock())


def test_import_only_payload_uses_newest_input_time_without_faking_live_success(store, settings, clock, stats_reply):
    store.save_stats(stats_reply, "2026-11-21T19:17:00Z")
    result = build_payload(store, settings, clock())
    assert result["as_of"] == "2026-11-21T19:17:00Z"
    assert result["edays"][-1]["end"] == result["as_of"]
    assert result["last_success_at"] is None


def test_stale_fetch_keeps_calendar_days_anchored_to_data(store, settings, clock, stats_reply):
    store.save_stats(stats_reply, timestamp(clock()))
    store.set_meta("last_success_at", timestamp(clock()))
    payload = build_payload(store, settings, clock() + timedelta(days=2))
    assert payload["edays"][-1]["date"] == "2026-11-21"
    assert payload["as_of"] == timestamp(clock())
    assert payload["compare_today"]["date"] == "2026-11-20"


def test_next_poll_at_only_when_polling(store, settings, clock):
    assert build_payload(store, settings, clock())["next_poll_at"] is None
    nxt = parse_timestamp("2026-11-21T20:00:30Z")
    assert build_payload(store, settings, clock(), next_poll=nxt)["next_poll_at"] == timestamp(nxt)
