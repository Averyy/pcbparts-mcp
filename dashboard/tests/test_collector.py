import json
import os
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import httpx
import pytest

from pcbparts_dashboard.collector import _validate_stats, collect, import_files
from pcbparts_dashboard.payload import build_payload
from pcbparts_dashboard.store import parse_timestamp, timestamp


@pytest.mark.parametrize("mouser_retries", [False, True], ids=["original", "mouser"])
def test_collect_success(settings, store, clock, stats_reply, health_reply, mouser_retries):
    stats_reply["distributor_quota"] = health_reply.pop("distributor_quota")
    if mouser_retries:
        stats_reply["days"][0]["upstream_status"]["mouser"] = {"2xx": 10, "5xx": 3, "connection": 1}
        stats_reply["days"][0]["distributors"]["mouser"]["retries"] = 4
        stats_reply["distributor_quota"]["mouser"]["resets_at"] = "2026-11-24 09:00 UTC"
    requests = []

    def respond(request):
        requests.append(request)
        assert request.headers["User-Agent"] == "pcbparts-dashboard/0.1"
        if request.url.path == "/mcp/stats":
            assert request.headers["Authorization"] == f"Bearer {settings.stats_token}"
            assert request.url.params["days"] == "365"
            assert set(request.extensions["timeout"].values()) == {30.0}
            return httpx.Response(200, json=stats_reply)
        assert "Authorization" not in request.headers
        assert set(request.extensions["timeout"].values()) == {15.0}
        return httpx.Response(200, json=health_reply)

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = collect(settings, store, client=client, now=clock())
        assert not client.is_closed
    assert result == {"ok": True, "error": None, "days_requested": 365, "days_stored": 3, "fetched_at": timestamp(clock())}
    assert len(requests) == 2
    assert store.all_days() == list(reversed(stats_reply["days"]))
    assert store.get_meta("last_success_at") == timestamp(clock())
    assert store.get_meta("last_full_fetch_at") == timestamp(clock())
    assert store.get_meta("last_fetch") == {
        "at": timestamp(clock()), "ok": True, "error": None,
        "days_requested": 365, "status_code": 200, "health_error": None,
    }
    expected_health = {**health_reply, "distributor_quota": stats_reply["distributor_quota"]}
    assert store.newest_health() == (timestamp(clock()), expected_health)
    assert build_payload(store, settings, clock())["health"] == expected_health
    assert settings.stats_token not in json.dumps(result)
    assert settings.stats_token not in json.dumps(store.get_meta("last_fetch"))
    assert all(key in store.all_days()[-1] for key in ("tool_apps", "latency", "popular_terms"))


@pytest.mark.parametrize("with_mouser_http", [False, True], ids=["old", "0.10.9"])
def test_mouser_http_counts_survive_collection_and_eastern_storage(settings, store, with_mouser_http):
    settings = replace(settings, problems_since="2026-11-21T05:00:00Z")

    def record(day, hours, sent, errors, retries):
        row = {"date": day, "calls": hours * 10, "hours": [10] * hours + [0] * (24 - hours),
               "distributors": {"mouser": {"sent": sent}}}
        if with_mouser_http:
            row["distributors"]["mouser"]["retries"] = retries
            row["upstream_status"] = {"mouser": {"2xx": sent - errors, "5xx": errors}}
        return row

    first = record("2026-11-21", 5, 10, 2, 2)
    final = record("2026-11-21", 24, 50, 10, 9)
    next_start = record("2026-11-22", 5, 15, 4, 3)
    next_final = record("2026-11-22", 24, 60, 12, 12)
    for at, days in [
        ("2026-11-21T05:00:30Z", [first]),
        ("2026-11-22T05:00:30Z", [next_start, final]),
        ("2026-11-23T00:00:30Z", [record("2026-11-23", 0, 0, 0, 0), next_final, final]),
    ]:
        with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
            200, json={"days": days} if request.url.path == "/mcp/stats" else {"version": "0.10.9"}
        ))) as client:
            assert collect(settings, store, client=client, now=parse_timestamp(at))["ok"]

    assert store.all_days()[0] == final
    assert store.snapshots_for("2026-11-21")[0][1] == first
    payload = build_payload(store, settings, parse_timestamp(at))
    eastern = next(row for row in payload["edays"] if row["date"] == "2026-11-21")
    saved = store.all_eastern_days()["2026-11-21"]
    for row in (eastern, eastern["problems"], saved, saved["problems"]):
        assert row["distributors"]["mouser"]["sent"] == 55  # 50 - 10 + 15 across UTC midnight.
        if with_mouser_http:
            assert row["distributors"]["mouser"]["retries"] == 10  # 9 - 2 + 3.
            assert row["upstream_status"]["mouser"] == {"2xx": 43, "5xx": 12}
        else:
            assert "retries" not in row["distributors"]["mouser"]
            assert "mouser" not in (row.get("upstream_status") or {})


@pytest.mark.parametrize("paused", [False, True], ids=["ready", "paused"])
@pytest.mark.parametrize("public_quota", [False, True], ids=["current", "old"])
def test_collect_takes_quota_only_from_stats(settings, store, clock, stats_reply, health_reply, paused, public_quota):
    pause = "2026-11-21 20:00 UTC" if paused else None
    if not public_quota:
        health_reply.pop("distributor_quota")
    stats_reply["distributor_quota"] = {
        "mouser": {"used_today": 80, "limit": 1000, "api_remaining": None,
                   "paused_until": pause, "resets_at": "2026-11-22 09:00 UTC", "kept_across_restarts": True},
        "digikey": {"used_today": 10, "limit": 1000, "api_remaining": 990,
                    "paused_until": pause, "resets_at": "2026-11-22 00:00 UTC", "kept_across_restarts": True},
    }
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json=stats_reply if request.url.path == "/mcp/stats" else health_reply
    ))) as client:
        assert collect(settings, store, client=client, now=clock())["ok"]
    payload = build_payload(store, settings, clock())
    assert payload["health_at"] == payload["as_of"] == timestamp(clock())
    assert payload["health"] == {**health_reply, "distributor_quota": stats_reply["distributor_quota"]}
    assert store.newest_health() == (timestamp(clock()), payload["health"])
    assert all("distributor_quota" not in day for day in store.all_days())
    assert "distributor_quota" not in store.snapshots_for(stats_reply["days"][0]["date"])[0][1]


@pytest.mark.parametrize("public_quota", [False, True], ids=["current", "old"])
@pytest.mark.parametrize("stats_quota", [False, True], ids=["missing", "empty"])
def test_missing_stats_quota_does_not_reuse_old_budget(settings, store, clock, stats_reply, public_quota, stats_quota):
    store.save_health({"distributor_quota": {"mouser": {"used_today": 80, "limit": 1000}}},
                      "2026-11-20T19:00:00Z")
    health = {"status": "healthy"}
    if public_quota:
        health["distributor_quota"] = {"mouser": {"used_today": 90, "limit": 1000,
                                                 "paused_until": None, "resets_at": "2026-11-22 06:00 UTC"}}
    if stats_quota:
        stats_reply["distributor_quota"] = {}
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json=stats_reply if request.url.path == "/mcp/stats" else health
    ))) as client:
        assert collect(settings, store, client=client, now=clock())["ok"]
    # Stats wins when it has the field; a pre-0.10.9 server's same-poll /health field is kept.
    expected = ({"status": "healthy", "distributor_quota": {}} if stats_quota
                else health if public_quota else {"status": "healthy"})
    assert build_payload(store, settings, clock())["health"] == expected


def test_old_stored_health_quota_still_reaches_dashboard(settings, store, clock, health_reply):
    store.save_health(health_reply, timestamp(clock()))
    payload = build_payload(store, settings, clock())
    assert payload["health"] == health_reply
    assert payload["health"]["distributor_quota"]["mouser"]["used_today"] == 20


@pytest.mark.parametrize("quota", [None, [], {"mouser": None}, {"mouser": []}],
                         ids=["null", "list", "entry-null", "entry-list"])
def test_invalid_stats_quota_rejected(quota):
    with pytest.raises(ValueError, match="Invalid distributor_quota"):
        _validate_stats({"days": [], "distributor_quota": quota})


@pytest.mark.parametrize("age, requested", [(None, 365), (0, 3), (24 * 3600, 3), (24 * 3600 + 1, 365)])
def test_automatic_day_choice(settings, store, clock, stats_reply, age, requested):
    if age is not None:
        store.set_meta("last_full_fetch_at", timestamp(clock() - timedelta(seconds=age)))
    before = store.get_meta("last_full_fetch_at")
    seen = []

    def respond(request):
        if request.url.path == "/mcp/stats":
            seen.append(request.url.params["days"])
            return httpx.Response(200, json=stats_reply)
        return httpx.Response(200, json={"status": "healthy"})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = collect(settings, store, client=client, now=clock)
    assert result["days_requested"] == requested
    assert seen == [str(requested)]
    assert store.get_meta("last_full_fetch_at") == (timestamp(clock()) if requested == 365 else before)


def test_explicit_days_override_full_fetch(settings, store, clock):
    def respond(request):
        if request.url.path == "/mcp/stats":
            assert request.url.params["days"] == "7"
            return httpx.Response(200, json={"days": []})
        return httpx.Response(200, json={})
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = collect(settings, store, days=7, client=client, now=clock())
    assert result["ok"] and result["days_stored"] == 0
    assert store.get_meta("last_full_fetch_at") is None
    assert store._connection.execute("SELECT count(*) FROM snapshots").fetchone()[0] == 0


@pytest.mark.parametrize("status, body, error", [
    (401, "Bad bearer {token}" + "x" * 400, "HTTP 401"),
    (503, "Unavailable", "HTTP 503"),
    (200, "not JSON {token}", "Invalid stats JSON"),
    (200, '{"error": "{token}"}', "Missing days list"),
    (200, '{"days": {}}', "Missing days list"),
    (200, '{"days": [null]}', "invalid day record"),
    (200, '{"days": [{"date": "2026-11-20", "calls": 1}, {"date": "bad"}]}', "invalid day record"),
    (200, '{"days": [{"date": "2026-11-20", "calls": "bad"}]}', "invalid day record"),
])
def test_stats_failures_are_recorded_and_redacted(settings, store, clock, status, body, error):
    requests = []
    previous = {"date": "2026-11-19", "calls": 12}
    store.merge_day(previous, "2026-11-19T19:00:00Z")
    store.set_meta("last_success_at", "2026-11-19T19:00:00Z")

    def respond(request):
        requests.append(request)
        return httpx.Response(status, text=body.replace("{token}", settings.stats_token))

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = collect(settings, store, client=client, now=clock())
    assert not result["ok"]
    assert result["days_stored"] == 0
    assert error in result["error"]
    assert len(result["error"].split(": ", 1)[-1]) <= 200
    last_fetch = store.get_meta("last_fetch")
    assert last_fetch["status_code"] == status
    assert not last_fetch["ok"]
    assert settings.stats_token not in json.dumps([last_fetch, result])
    assert store.all_days() == [previous]
    assert store.get_meta("last_success_at") == "2026-11-19T19:00:00Z"
    assert store.get_meta("last_full_fetch_at") is None
    assert len(requests) == 1


def test_network_failure_does_not_echo_exception(settings, store, clock):
    def respond(request):
        raise httpx.ConnectError(f"secret in exception: {settings.stats_token}", request=request)
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = collect(settings, store, client=client, now=clock())
    assert not result["ok"]
    assert "ConnectError" in result["error"]
    assert store.get_meta("last_fetch")["status_code"] is None
    assert settings.stats_token not in json.dumps([result, store.get_meta("last_fetch")])


@pytest.mark.parametrize("health_failure", ["status", "json", "timeout"])
def test_health_failure_keeps_stats_success(settings, store, clock, stats_reply, health_failure):
    previous = {"distributor_quota": {"mouser": {"used_today": 80, "limit": 1000}}}
    store.save_health(previous, "2026-11-20T19:00:00Z")
    stats_reply["distributor_quota"] = {"mouser": {"used_today": 90, "limit": 1000}}

    def respond(request):
        if request.url.path == "/mcp/stats":
            return httpx.Response(200, json=stats_reply)
        if health_failure == "timeout":
            raise httpx.ReadTimeout(settings.stats_token, request=request)
        return httpx.Response(503 if health_failure == "status" else 200, text=settings.stats_token)

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = collect(settings, store, client=client, now=clock())
    assert result["ok"] and result["error"] is None
    assert store.get_meta("last_fetch")["health_error"]
    assert settings.stats_token not in json.dumps(store.get_meta("last_fetch"))
    assert store.newest_health() == ("2026-11-20T19:00:00Z", previous)
    assert store.get_meta("last_success_at") == timestamp(clock())


def test_missing_token_records_error_without_request(settings, store, clock):
    result = collect(replace(settings, stats_token=None), store, now=clock())
    assert not result["ok"]
    assert "STATS_TOKEN" in result["error"]
    assert store.get_meta("last_fetch")["error"] == result["error"]


@pytest.mark.parametrize("days", [0, 366, -1, "3", True])
def test_invalid_days_do_not_make_request(settings, store, clock, days):
    result = collect(settings, store, days=days, now=clock())
    assert not result["ok"]
    assert "between 1 and 365" in result["error"]


def test_success_prunes_old_samples(settings, store, clock, stats_reply):
    old = clock() - timedelta(days=46)
    old_record = {"date": old.date().isoformat(), "calls": 1}
    store.save_stats({"days": [old_record]}, timestamp(old))
    store.save_health({"old": True}, timestamp(old))
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json=stats_reply if request.url.path == "/mcp/stats" else {"new": True}
    ))) as client:
        collect(settings, store, client=client, now=clock())
    assert old_record in store.all_days()
    assert store._connection.execute("SELECT fetched_at FROM snapshots").fetchall() == [(timestamp(clock()),)]
    assert store._connection.execute("SELECT fetched_at FROM health").fetchall() == [(timestamp(clock()),)]


@pytest.mark.parametrize("filename, expected", [
    ("mcp-stats_2026-11-21_1417-EST_sample.json", "2026-11-21T19:17:00Z"),
    ("mcp-stats_2026-07-21_1417-EST_summer.json", "2026-07-21T18:17:00Z"),
    ("arbitrary.json", "2026-04-01T01:02:03Z"),
])
def test_import_uses_eastern_filename_or_mtime_and_preserves_live_metadata(store, tmp_path, stats_reply, filename, expected):
    path = tmp_path / filename
    path.write_text(json.dumps(stats_reply))
    modified = datetime(2026, 4, 1, 1, 2, 3, tzinfo=UTC).timestamp()
    os.utime(path, (modified, modified))
    store.set_meta("last_success_at", "2026-01-01T00:00:00Z")
    result = import_files(store, [path])
    assert result == {"ok": True, "files_imported": 1, "days_stored": 3}
    assert store._connection.execute("SELECT fetched_at FROM snapshots").fetchone()[0] == expected
    assert store.get_meta("last_success_at") == "2026-01-01T00:00:00Z"
    assert store.get_meta("last_full_fetch_at") is None
    assert store.get_meta("last_fetch") is None
    assert store.all_days() == list(reversed(stats_reply["days"]))


def test_import_uses_same_merge_rules(store, tmp_path):
    first = tmp_path / "mcp-stats_2026-11-21_1200-EST.json"
    second = tmp_path / "mcp-stats_2026-11-21_1300-EST.json"
    apps = {"search": {"app-alpha": {"calls": 2}}}
    first.write_text(json.dumps({"days": [{"date": "2026-11-21", "calls": 10, "tool_apps": apps}]}))
    second.write_text(json.dumps({"days": [{"date": "2026-11-21", "calls": 12, "tool_apps": None}]}))
    assert import_files(store, [first, second])["files_imported"] == 2
    assert store.all_days() == [{"date": "2026-11-21", "calls": 12, "tool_apps": apps}]
    assert store._connection.execute("SELECT count(*) FROM snapshots").fetchone()[0] == 2


def test_importing_an_older_file_after_a_newer_one_adds_no_warning(store, tmp_path):
    newer = tmp_path / "mcp-stats_2026-11-21_1443-EST.json"
    older = tmp_path / "mcp-stats_2026-11-21_1417-EST.json"
    newer.write_text(json.dumps({"days": [{"date": "2026-11-21", "calls": 120}]}))
    older.write_text(json.dumps({"days": [{"date": "2026-11-21", "calls": 100}]}))
    assert import_files(store, [newer, older])["files_imported"] == 2
    assert store.all_days() == [{"date": "2026-11-21", "calls": 120}]
    assert store.get_meta("warnings", []) == []


def test_first_collect_starts_the_problems_window_and_version_changes_move_it(settings, store, clock):
    version = "0.10.5"

    def respond(request):
        return httpx.Response(200, json={"days": []} if request.url.path == "/mcp/stats" else {"version": version})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        # a new store can't know when 0.10.5 was deployed: it counts problems from its first look
        assert collect(settings, store, client=client, now=clock)["ok"]
        assert store.get_meta("seen_version") == "0.10.5"
        assert store.get_meta("problems_since") == "2026-11-21T19:20:00Z"
        assert store.get_meta("problems_version") == "0.10.5"
        clock.advance(3600)
        assert collect(settings, store, client=client, now=clock)["ok"]
        assert store.get_meta("problems_since") == "2026-11-21T19:20:00Z"
        version = "0.10.6"
        clock.advance(600)
        assert collect(settings, store, client=client, now=clock)["ok"]
        assert store.get_meta("seen_version") == "0.10.6"
        assert store.get_meta("problems_since") == "2026-11-21T20:20:00Z"
        assert store.get_meta("problems_version") == "0.10.6"
        clock.advance(3600)
        collect(settings, store, client=client, now=clock)
        assert store.get_meta("problems_since") == "2026-11-21T20:20:00Z"


def test_explicit_problems_since_prevents_auto_window_move_but_tracks_versions(settings, store, clock):
    settings = replace(settings, problems_since="2026-11-21T18:00:00Z", problems_version="0.10.5")
    store.set_meta("seen_version", "0.10.4")
    store.set_meta("problems_since", "2026-11-20T00:00:00Z")
    store.set_meta("problems_version", "0.10.4")
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json={"days": []} if request.url.path == "/mcp/stats" else {"version": "0.10.6"}
    ))) as client:
        collect(settings, store, client=client, now=clock)
    assert store.get_meta("seen_version") == "0.10.6"
    assert store.get_meta("problems_since") == "2026-11-20T00:00:00Z"
    assert store.get_meta("problems_version") == "0.10.4"


def test_problems_version_override_does_not_suppress_automatic_cutoff(settings, store, clock):
    from pcbparts_dashboard.payload import build_payload

    settings = replace(settings, problems_version="pinned-label")
    store.set_meta("seen_version", "0.10.5")
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json={"days": []} if request.url.path == "/mcp/stats" else {"version": "0.10.6"}
    ))) as client:
        collect(settings, store, client=client, now=clock)
    result = build_payload(store, settings, clock())
    assert result["problems_since"] == "2026-11-21T19:20:00Z"
    assert result["problems_version"] == "pinned-label"
    assert store.get_meta("problems_version") == "0.10.6"


@pytest.mark.parametrize("health", [{}, {"version": None}, {"version": ""}, [], None])
def test_missing_health_version_does_not_move_window(settings, store, clock, health):
    store.set_meta("seen_version", "0.10.5")
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json={"days": []} if request.url.path == "/mcp/stats" else health,
        # httpx's json=None produces an empty body: still a health failure, with no transition.
    ))) as client:
        collect(settings, store, client=client, now=clock)
    assert store.get_meta("seen_version") == "0.10.5"
    assert store.get_meta("problems_since") is None


def test_failed_collect_does_not_change_seen_version(settings, store, clock):
    store.set_meta("seen_version", "0.10.5")
    with httpx.Client(transport=httpx.MockTransport(lambda _request: httpx.Response(503))) as client:
        assert not collect(settings, store, client=client, now=clock)["ok"]
    assert store.get_meta("seen_version") == "0.10.5"
    assert store.get_meta("problems_since") is None


def test_collect_persists_complete_days_before_snapshot_pruning(settings, store, clock, stats_reply):
    for day in ("2026-10-01", "2026-10-02"):
        record = {"date": day, "calls": 240, "hours": [10] * 24}
        store.merge_day(record, "2026-10-03T00:00:30Z")
        store.add_snapshot(record | {"calls": 40}, day + "T04:00:30Z")
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json=stats_reply if request.url.path == "/mcp/stats" else {}
    ))) as client:
        collect(settings, store, client=client, now=clock)
    assert store.all_eastern_days()["2026-10-01"]["calls"] == 240
    assert not store.all_eastern_days()["2026-10-01"]["approx"]
    assert "2026-10-01" not in store.all_snapshots()


def test_import_can_upgrade_approximate_eastern_days_without_moving_success(store, tmp_path):
    final = tmp_path / "mcp-stats_2026-11-22_0000-EST.json"
    final.write_text(json.dumps({"days": [
        {"date": "2026-11-22", "calls": 50, "hours": [10] * 5 + [0] * 19},
        {"date": "2026-11-21", "calls": 240, "hours": [10] * 24},
        {"date": "2026-11-20", "calls": 240, "hours": [10] * 24},
    ]}))
    import_files(store, [final])
    assert store.all_eastern_days()["2026-11-20"]["approx"]
    snapshots = []
    for day in ("2026-11-20", "2026-11-21"):
        path = tmp_path / f"mcp-stats_{day}_0000-EST.json"
        path.write_text(json.dumps({"days": [{"date": day, "calls": 50}]}))
        snapshots.append(path)
    import_files(store, snapshots)
    assert not store.all_eastern_days()["2026-11-20"]["approx"]
    assert store.all_eastern_days()["2026-11-20"]["calls"] == 240
    assert store.get_meta("last_success_at") is None
