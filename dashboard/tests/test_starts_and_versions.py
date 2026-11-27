"""Server 0.10.12's day fields that aren't counters (starts, addresses), version runs and their
scorecards, catalog changes and whether the server keeps its stats across restarts."""

from datetime import timedelta

from pcbparts_dashboard.eastern import EasternRecords
from pcbparts_dashboard.payload import build_payload
from pcbparts_dashboard.store import parse_timestamp as dt


def utc_day(date, **extra):
    return {"date": date, "calls": 240, "hours": [10] * 24,
            "tools": {"jlc_search": {"calls": 240, "ok": 240, "similar_only": 0, "not_found": 0,
                                     "bad_request": 0, "rate_limited": 0, "failed": 0}}, **extra}


def finished(store, *records):
    for record in records:
        store.merge_day(record, record["date"] + "T23:59:59Z")
        store.merge_day(record, "2026-11-29T00:00:00Z")


def test_starts_land_on_the_eastern_day_they_happened_in(store):
    # 03:10 UTC on Nov 27 is 10:10 PM EST on Nov 26; 16:45 UTC is 11:45 AM EST on Nov 27
    finished(store, utc_day("2026-11-26", restarts=0, starts=[]),
             utc_day("2026-11-27", restarts=2, starts=[{"at": "03:10", "version": "0.10.11"},
                                                       {"at": "16:45", "version": "0.10.12"}]),
             utc_day("2026-11-28", restarts=1, starts=[{"at": "02:00:30", "version": "0.10.12"}]))
    records = EasternRecords(store, dt("2026-11-29T00:00:00Z"))
    nov26, nov27 = records.eastern_day("2026-11-26"), records.eastern_day("2026-11-27")
    assert nov26["starts"] == [{"at": "2026-11-27T03:10:00Z", "version": "0.10.11"}]
    assert nov27["starts"] == [{"at": "2026-11-27T16:45:00Z", "version": "0.10.12"},
                               {"at": "2026-11-28T02:00:30Z", "version": "0.10.12"}]
    assert nov26["starts_complete"] and nov27["starts_complete"]


def test_starts_are_incomplete_where_a_day_counted_restarts_it_could_not_list(store):
    # the deploy day: an older server started twice before 0.10.12 began listing starts
    finished(store, utc_day("2026-11-26", restarts=1),
             utc_day("2026-11-27", restarts=3, starts=[{"at": "16:45", "version": "0.10.12"}, {"at": "bad"}, "x"]))
    records = EasternRecords(store, dt("2026-11-29T00:00:00Z"))
    day = records.eastern_day("2026-11-27")
    assert day["starts"] == [{"at": "2026-11-27T16:45:00Z", "version": "0.10.12"}]
    assert day["starts_complete"] is False
    older = records.eastern_day("2026-11-26")  # only the day before 0.10.12 and the deploy day's early hours
    assert older["starts"] == [] and older["starts_complete"] is False
    assert EasternRecords(store, dt("2026-11-29T00:00:00Z")).window(dt("2026-11-26T05:00:00Z"), dt("2026-11-26T20:00:00Z"))["starts"] is None


def test_address_counts_are_upper_bounds_kept_only_where_their_events_happened(store):
    refused = [0] * 24
    refused[2] = 852  # 9 PM EST on Nov 26
    finished(store, utc_day("2026-11-27", refused_hours=refused,
                            per_ip_refusals={"total": 852, "everyone_else": 852},
                            distributor_limits={"mouser": {"held_back": {"address_blocked": 5}, "held_back_hours": [0] * 20 + [5, 0, 0, 0]}},
                            distributors={"mouser": {"rate_limited": 5}}, restarts=0, starts=[],
                            addresses={"rate_limited": 1, "cap_reached": 0, "blocked_tried": 1}))
    records = EasternRecords(store, dt("2026-11-29T00:00:00Z"))
    nov26, nov27 = records.eastern_day("2026-11-26"), records.eastern_day("2026-11-27")
    assert nov26["per_ip_refusals"]["total"] == 852
    assert nov26["addresses"] == {"rate_limited": 1, "cap_reached": 0, "blocked_tried": 0}
    assert nov27["addresses"] == {"rate_limited": 0, "cap_reached": 0, "blocked_tried": 1}
    # older days have no addresses at all
    store.merge_day(utc_day("2026-11-20", per_ip_refusals={"total": 3}), "2026-11-21T00:00:00Z")
    assert EasternRecords(store, dt("2026-11-29T00:00:00Z")).eastern_day("2026-11-20")["addresses"] is None


def test_an_address_count_missing_where_events_happened_is_unknown(store):
    finished(store, utc_day("2026-11-26", per_ip_refusals={"total": 10}, refused_hours=[0] * 23 + [10]),
             utc_day("2026-11-27", per_ip_refusals={"total": 4}, refused_hours=[4] + [0] * 23, restarts=0, starts=[],
                     addresses={"rate_limited": 2, "cap_reached": 0, "blocked_tried": 0}))
    day = EasternRecords(store, dt("2026-11-29T00:00:00Z")).eastern_day("2026-11-26")
    assert day["per_ip_refusals"]["total"] == 14
    assert day["addresses"]["rate_limited"] is None  # Nov 26's 10 came from a day without the count


def test_version_runs_prefer_listed_starts_and_carry_a_scorecard(store, settings):
    failed = [0] * 24
    failed[18] = 4
    finished(store, utc_day("2026-11-27", restarts=1, starts=[{"at": "16:45", "version": "0.10.12"}],
                            failed_hours=failed, tools={"jlc_search": {
                                "calls": 240, "ok": 226, "similar_only": 0, "not_found": 0,
                                "bad_request": 10, "rate_limited": 0, "failed": 4}},
                            latency={"jlc_search": {"counts": [200, 30, 6]}},
                            per_ip_refusals={"total": 0}))
    for version, at in (("0.10.10", "2026-11-26T21:00:00Z"), ("0.10.11", "2026-11-27T12:00:00Z"),
                        ("0.10.12", "2026-11-27T17:00:00Z")):
        store.save_health({"version": version}, at)
    store.set_meta("last_success_at", "2026-11-28T00:00:00Z")
    payload = build_payload(store, settings, dt("2026-11-28T00:00:00Z"))
    runs = [(run["version"], run["from"], run["to"], run["exact"]) for run in payload["versions"]]
    assert runs == [
        ("0.10.10", "2026-11-26T21:00:00Z", "2026-11-27T12:00:00Z", False),
        ("0.10.11", "2026-11-27T12:00:00Z", "2026-11-27T16:45:00Z", False),
        ("0.10.12", "2026-11-27T16:45:00Z", None, True),
    ]
    current = payload["versions"][-1]
    assert current["failed"] == 4  # all in the 18:00 UTC hour, after the 16:45 start
    assert current["calls"] == 72  # 7 h 15 min at 10 an hour
    assert current["turned_away"] == 0 and current["latency"] is not None
    assert current["partial"] is False
    # a run that began before the first stored day is scored over its stored part only
    assert payload["versions"][0]["calls"] == 120 and payload["versions"][0]["partial"] is True


def test_catalog_changes_and_kept_across_restarts(store, settings, stats_reply):
    for at, data_as_of in (("2026-11-27T10:00:00Z", "2026-11-26T11:51:00Z"), ("2026-11-27T11:00:00Z", None),
                           ("2026-11-27T12:00:00Z", "2026-11-27T11:52:00Z"), ("2026-11-27T13:00:00Z", "2026-11-27T11:52:00Z")):
        store.save_health({"version": "0.10.12", "snapshot": {"data_as_of": data_as_of}}, at)
    assert store.catalog_changes() == [
        {"before": "2026-11-27T10:00:00Z", "at": "2026-11-27T12:00:00Z", "data_as_of": "2026-11-27T11:52:00Z"}]
    store.save_stats(stats_reply | {"kept_across_restarts": False}, "2026-11-27T13:00:00Z")
    store.save_stats(stats_reply | {"kept_across_restarts": True}, "2026-11-21T19:17:00Z")  # an older imported file
    payload = build_payload(store, settings, dt("2026-11-27T13:00:00Z"))
    assert payload["kept_across_restarts"] is False
    assert payload["catalog_changes"] == store.catalog_changes()
    store.save_stats(stats_reply | {"kept_across_restarts": True}, "2026-11-27T14:00:00Z")
    assert build_payload(store, settings, dt("2026-11-27T14:00:00Z"))["kept_across_restarts"] is True


def test_addresses_are_unknown_on_the_day_an_older_server_started_it(store):
    """The UTC day 0.10.12 first starts on: its addresses count begins at its start, so it never saw
    the addresses behind the older server's refusals that day; a rollback stops listing starts."""
    refused = [0] * 24
    refused[10], refused[16] = 50, 1
    deploy_day = utc_day("2026-11-27", restarts=3, starts=[{"at": "14:00", "version": "0.10.12"}],
                         refused_hours=refused, per_ip_refusals={"total": 51, "everyone_else": 51},
                         addresses={"rate_limited": 1, "cap_reached": 0, "blocked_tried": 0})
    finished(store, deploy_day)
    day = EasternRecords(store, dt("2026-11-29T00:00:00Z")).eastern_day("2026-11-27")
    assert day["per_ip_refusals"]["total"] == 51
    assert day["addresses"]["rate_limited"] is None
    # a server that lists every start is trusted, up to the list's own limit
    many = [{"at": f"{h:02d}:{m:02d}", "version": "0.10.12"} for h in range(24) for m in (0, 20, 40)][:50]
    store.merge_day(deploy_day | {"restarts": 60, "starts": many, "calls": 300}, "2026-11-29T00:00:00Z")
    assert EasternRecords(store, dt("2026-11-29T00:00:00Z")).eastern_day("2026-11-27")["addresses"]["rate_limited"] == 1


def test_ext_holds_and_refusals_are_dropped_where_a_part_did_not_split_them(store):
    def utc(date, held_hours, ext=None):
        held = sum(held_hours)
        limits = {"held_back": {"address_daily": held}, "held_back_hours": held_hours, "refusals": {"refused": 1}}
        if ext is not None:
            limits |= {"ext_held_back": {"address_daily": ext}, "ext_refusals": {"refused": 1}}
        return utc_day(date, distributors={"digikey": {"sent": 0, "rate_limited": held}}, distributor_limits={"digikey": limits})

    deploy, nxt = [0] * 24, [0] * 24
    deploy[20], nxt[2] = 10, 3  # 10 holds through either path on the unsplit deploy day, 3 (2 through ext) after
    finished(store, utc("2026-11-27", deploy), utc("2026-11-28", nxt, ext=2))
    records = EasternRecords(store, dt("2026-11-29T00:00:00Z"))
    limits = records.eastern_day("2026-11-27")["distributor_limits"]["digikey"]
    assert limits["held_back"] == {"address_daily": 13}
    assert "ext_held_back" not in limits and "ext_refusals" not in limits
    # the next Eastern day is all split: ext's part stays
    limits = records.eastern_day("2026-11-28")["distributor_limits"]["digikey"]
    assert "ext_held_back" in limits


def test_ext_holds_never_exceed_their_cause_after_estimates(store):
    def rec(held, bins):
        return utc_day("2026-11-26", distributors={"digikey": {"sent": 5, "rate_limited": held}},
                       distributor_limits={"digikey": {"held_back": {"address_daily": held, "distributor_refused": 0},
                                                       "ext_held_back": {"address_daily": held, "distributor_refused": 0},
                                                       "held_back_hours": bins}})

    final, partial = [0] * 24, [0] * 24
    final[4], final[7], partial[4] = 100, 200, 100
    store.add_snapshot(rec(0, [0] * 24), "2026-11-26T02:00:30Z")
    store.add_snapshot(rec(100, partial), "2026-11-26T07:00:30Z")  # the dashboard missed 03:00 to 06:00
    store.merge_day(rec(300, final), "2026-11-27T00:00:30Z")
    window = EasternRecords(store, dt("2026-11-27T00:00:30Z")).window(dt("2026-11-26T05:00:00Z"), dt("2026-11-27T00:00:00Z"))
    limits = window["distributor_limits"]["digikey"]
    assert limits["ext_held_back"]["address_daily"] <= limits["held_back"]["address_daily"] == 200


def test_a_rollback_to_a_version_that_lists_no_starts_is_a_run_of_its_own(store, settings):
    from pcbparts_dashboard.eastern import observe_version

    # 0.10.12 starts at 14:00 on Nov 26 (listed), is rolled back to 0.10.11 by 19:00 (which lists no
    # starts), and is deployed again at 02:00 on Nov 27 (listed)
    store.merge_day(utc_day("2026-11-25", restarts=0), "2026-11-26T00:00:30Z")
    store.merge_day(utc_day("2026-11-26", restarts=2, starts=[{"at": "14:00", "version": "0.10.12"}]), "2026-11-27T00:00:30Z")
    store.merge_day(utc_day("2026-11-27", restarts=1, starts=[{"at": "02:00", "version": "0.10.12"}]), "2026-11-27T12:00:30Z")
    for version, at in (("0.10.11", "2026-11-25T10:00:30Z"), ("0.10.11", "2026-11-26T13:00:30Z"),
                        ("0.10.12", "2026-11-26T14:00:40Z"),  # read in the minute the 14:00 start rounds down to
                        ("0.10.11", "2026-11-26T14:00:50Z"),  # an older check's slow reply: not a rollback
                        ("0.10.12", "2026-11-26T17:00:30Z"), ("0.10.11", "2026-11-26T19:00:30Z"),
                        ("0.10.11", "2026-11-27T01:00:30Z"), ("0.10.12", "2026-11-27T03:00:30Z"),
                        ("0.10.12", "2026-11-27T12:00:30Z")):
        store.save_health({"version": version, "status": "healthy"}, at)
        observe_version(store, settings, {"version": version}, dt(at))
    store.set_meta("last_success_at", "2026-11-27T12:00:30Z")
    runs = build_payload(store, settings, dt("2026-11-27T12:00:30Z"))["versions"]
    assert [(r["version"], r["from"], r["exact"], r.get("after")) for r in runs] == [
        ("0.10.11", "2026-11-25T10:00:30Z", False, None),
        ("0.10.12", "2026-11-26T14:00:00Z", True, None),
        ("0.10.11", "2026-11-26T19:00:30Z", False, "2026-11-26T17:00:30Z"),
        ("0.10.12", "2026-11-27T02:00:00Z", True, None),
    ]
    assert runs[2]["to"] == "2026-11-27T02:00:00Z" and runs[3]["to"] is None


def test_scorecards_add_up_whole_days_and_windows_only_at_the_edges(store, settings, monkeypatch):
    for date in ("2026-11-24", "2026-11-25", "2026-11-26", "2026-11-27"):
        store.merge_day(utc_day(date), (dt(date + "T00:00:00Z") + timedelta(days=1, seconds=30)).isoformat().replace("+00:00", "Z"))
    store.save_health({"version": "0.10.11"}, "2026-11-24T10:00:30Z")
    store.save_health({"version": "0.10.11"}, "2026-11-28T00:00:30Z")
    store.set_meta("last_success_at", "2026-11-28T00:00:30Z")
    from pcbparts_dashboard import eastern
    calls = []
    original = eastern.EasternRecords.window
    monkeypatch.setattr(eastern.EasternRecords, "window", lambda self, start, end, **kw: calls.append((start, end, kw)) or original(self, start, end, **kw))
    payload = build_payload(store, settings, dt("2026-11-28T00:00:30Z"))
    run = payload["versions"][-1]
    # Nov 24 10:00:30 UTC to Nov 28 00:00:30: about 3 days 14 hours at 10 calls an hour
    assert abs(run["calls"] - 860) <= 2
    edges = [c for c in calls if (c[1] - c[0]) < timedelta(days=1) and not c[2]]
    assert any(c[0] == dt("2026-11-24T10:00:30Z") for c in edges)


def test_a_saved_exact_day_is_never_replaced_by_an_estimate(store, settings):
    """A rules upgrade needs its boundary snapshots: without them the saved exact day stays."""
    from pcbparts_dashboard import eastern

    def rec(date, upto):
        hours = [10 + h for h in range(24)]
        calls = sum(hours[:upto])
        return {"date": date, "calls": calls, "hours": hours[:upto] + [0] * (24 - upto),
                "tools": {"jlc_search": {"calls": calls, "ok": calls, "similar_only": 0, "not_found": 0,
                                         "bad_request": 0, "rate_limited": 0, "failed": 0}},
                "upstream": {"jlcpcb": {"sent": 3 * calls + (7 if upto > 4 else 0)}}}

    for date, following in (("2026-10-12", "2026-10-13"), ("2026-10-13", "2026-10-14"), ("2026-10-14", "2026-10-15")):
        for hour in range(24):
            store.add_snapshot(rec(date, hour), f"{date}T{hour:02d}:00:30Z")
        store.merge_day(rec(date, 24), f"{following}T00:00:30Z")
    as_of = dt("2026-10-15T00:00:30Z")
    eastern.persist_eastern_days(store, as_of, settings)
    saved = store.eastern_day("2026-10-13")
    assert saved["approx"] is False
    store.save_eastern_day(saved, "2026-10-15T00:00:30Z", rules_version=eastern.RULES_VERSION - 1)
    with store.lock, store._connection:  # 45 days on, pruning has taken the day's first snapshots
        store._connection.execute("DELETE FROM snapshots WHERE fetched_at < '2026-10-13T12:00:00Z'")
    eastern.persist_eastern_days(store, as_of, settings)
    assert store.eastern_day("2026-10-13") == saved
    assert store.eastern_rules_versions()["2026-10-13"] == eastern.RULES_VERSION - 1


def test_saved_days_are_upgraded_a_few_per_poll_and_never_by_a_page(store, settings, monkeypatch):
    from pcbparts_dashboard import eastern

    for day in range(1, 31):
        date = f"2026-10-{day:02d}"
        store.merge_day(utc_day(date), (dt(date + "T00:00:00Z") + timedelta(days=1, seconds=30)).isoformat().replace("+00:00", "Z"))
    as_of = dt("2026-10-31T00:00:30Z")
    eastern.persist_eastern_days(store, as_of, settings)
    rows = store.eastern_rules_versions()
    for date in rows:
        store.save_eastern_day(store.eastern_day(date), "2026-10-31T00:00:30Z", rules_version=eastern.RULES_VERSION - 1)
    store.set_meta("last_success_at", "2026-10-31T00:00:30Z")
    build_payload(store, settings, as_of)
    assert set(store.eastern_rules_versions().values()) == {eastern.RULES_VERSION - 1}
    monkeypatch.setattr(eastern, "BACKLOG_PER_POLL", 10)
    eastern.persist_eastern_days(store, as_of, settings)
    upgraded = sorted(d for d, v in store.eastern_rules_versions().items() if v == eastern.RULES_VERSION)
    assert len(upgraded) == 10 and upgraded[-1] == max(rows)  # newest first
    for _ in range(3):
        eastern.persist_eastern_days(store, as_of, settings)
    assert set(store.eastern_rules_versions().values()) == {eastern.RULES_VERSION}


def test_days_saved_by_the_older_dashboard_lose_their_summed_starts_and_addresses(store):
    store.merge_day(utc_day("2026-11-26"), "2026-11-27T00:00:30Z")
    store.merge_day(utc_day("2026-11-27"), "2026-11-28T00:00:30Z")
    records = EasternRecords(store, dt("2026-11-28T00:00:30Z"))
    saved = records.eastern_day("2026-11-26")
    old = {key: value for key, value in saved.items() if key not in ("starts_complete", "hour_problems")}
    old |= {"starts": [{"at": "03:10", "version": "0.10.12"}], "addresses": {"rate_limited": 0.4}}
    store.save_eastern_day(old, "2026-11-28T00:00:30Z", rules_version=4)
    served = EasternRecords(store, dt("2026-11-28T00:00:30Z"), upgrade=False).eastern_day("2026-11-26")
    assert (served["starts"], served["starts_complete"], served["addresses"]) == (None, False, None)
    # a poll with the day's inputs recomputes it
    fresh = EasternRecords(store, dt("2026-11-28T00:00:30Z")).eastern_day("2026-11-26")
    assert fresh["starts"] is None and fresh["starts_complete"] is False and "hour_problems" in fresh


def snap(date, failed=None, rejected=None):
    """A cumulative UTC record: failed {tool: {reason: n}}, rejected {tool: {label: n}}."""
    failed, rejected = failed or {}, rejected or {}
    tools = {"jlc_search": {"calls": 100, "ok": 100, "similar_only": 0, "not_found": 0, "bad_request": 0, "rate_limited": 0, "failed": 0}}
    for tool in {*failed, *rejected}:
        tools[tool] = {"calls": 100, "ok": 0, "similar_only": 0, "not_found": 0,
                       "bad_request": sum(rejected.get(tool, {}).values()), "rate_limited": 0, "failed": sum(failed.get(tool, {}).values())}
    return {"date": date, "calls": 100, "hours": [4] * 24, "tools": tools,
            "reasons": {tool: dict(reasons) for tool, reasons in failed.items()},
            "bad_request_reasons": {tool: dict(labels) for tool, labels in rejected.items()}}


def test_each_hour_says_which_tools_failed_and_why(store):
    store.add_snapshot(snap("2026-11-27"), "2026-11-27T17:00:30Z")
    store.add_snapshot(snap("2026-11-27", {"cse_search": {"cse_lookup_failed": 7}, "cse_get_kicad": {"cse_invalid_zip": 3}},
                            {"jlc_search": {"arg:limit:int_parsing": 2}}), "2026-11-27T18:00:30Z")
    # the dashboard missed 19:00 and 20:00: the next difference covers three hours
    store.add_snapshot(snap("2026-11-27", {"cse_search": {"cse_lookup_failed": 9}, "cse_get_kicad": {"cse_invalid_zip": 3}},
                            {"jlc_search": {"arg:limit:int_parsing": 2}}), "2026-11-27T21:00:30Z")
    store.merge_day(snap("2026-11-27", {"cse_search": {"cse_lookup_failed": 9}, "cse_get_kicad": {"cse_invalid_zip": 3}},
                         {"jlc_search": {"arg:limit:int_parsing": 2}}), "2026-11-27T21:00:30Z")
    records = EasternRecords(store, dt("2026-11-27T21:00:30Z"))
    hours = records.eastern_day("2026-11-27")["hour_problems"]
    one = hours[12]  # 17:00 UTC, the 12th hour after 05:00
    assert one == {"from": "2026-11-27T17:00:30Z", "to": "2026-11-27T18:00:30Z",
                   "failed": {"cse_search": {"cse_lookup_failed": 7}, "cse_get_kicad": {"cse_invalid_zip": 3}},
                   "rejected": {"jlc_search": {"arg:limit:int_parsing": 2}}}
    span = hours[13:16]
    assert span[0] == span[1] == span[2] == {"from": "2026-11-27T18:00:30Z", "to": "2026-11-27T21:00:30Z",
                                             "failed": {"cse_search": {"cse_lookup_failed": 2}}}
    assert hours[11] is None
    # the check at 21:00:30 is half a minute into the next hour: that hour isn't part of the gap
    assert len(hours) == 17 and hours[16] is None


def test_a_day_rebuilt_from_daily_totals_has_no_hourly_breakdown(store):
    record = snap("2026-11-27", {"cse_search": {"cse_lookup_failed": 7}})
    store.merge_day(snap("2026-11-26"), "2026-11-27T00:00:30Z")
    store.merge_day(record, "2026-11-28T00:00:30Z")
    assert EasternRecords(store, dt("2026-11-28T00:00:30Z")).eastern_day("2026-11-27")["hour_problems"] is None


def test_failures_without_a_reason_are_unlabelled(store):
    lo, hi = snap("2026-11-27"), snap("2026-11-27")
    hi["tools"]["jlc_search"]["failed"] = 4
    hi["reasons"] = {"jlc_search": {"exception": 1}}
    store.add_snapshot(lo, "2026-11-27T17:00:30Z")
    store.add_snapshot(hi, "2026-11-27T18:00:30Z")
    store.merge_day(hi, "2026-11-27T18:00:30Z")
    hours = EasternRecords(store, dt("2026-11-27T18:00:30Z")).eastern_day("2026-11-27")["hour_problems"]
    assert hours[12]["failed"] == {"jlc_search": {"exception": 1, "unlabelled": 3}}


def test_addresses_are_unknown_when_an_older_server_ran_before_the_first_listed_start(store):
    """0.10.12 as the day's first restart: restarts equals the starts listed, yet the refusals
    before it were counted by a server that kept no addresses (its snapshots have none)."""
    refused = [0] * 24
    refused[10] = 500
    old = utc_day("2026-11-27", restarts=0, refused_hours=refused, per_ip_refusals={"total": 500, "everyone_else": 500})
    store.add_snapshot(old, "2026-11-27T12:00:30Z")
    later = list(refused)
    later[16] = 20
    store.merge_day(utc_day("2026-11-27", restarts=1, starts=[{"at": "15:00", "version": "0.10.12"}], refused_hours=later,
                            per_ip_refusals={"total": 520, "everyone_else": 520},
                            addresses={"rate_limited": 1, "cap_reached": 0, "blocked_tried": 0}), "2026-11-28T00:00:30Z")
    window = EasternRecords(store, dt("2026-11-28T00:00:30Z")).window(dt("2026-11-27T00:00:00Z"), dt("2026-11-28T00:00:00Z"))
    assert window["per_ip_refusals"]["total"] == 520
    assert window["addresses"]["rate_limited"] is None


def test_counts_that_went_down_across_a_restart_give_totals_only(store):
    store.add_snapshot(snap("2026-11-27", {"cse_search": {"cse_lookup_failed": 5}}), "2026-11-27T17:00:30Z")
    # a restart that didn't keep the counts, then 7 failures of another kind
    store.add_snapshot(snap("2026-11-27", {"cse_search": {"cse_invalid_zip": 7}}), "2026-11-27T18:00:30Z")
    store.add_snapshot(snap("2026-11-27", {"cse_search": {"cse_invalid_zip": 8}}), "2026-11-27T19:00:30Z")
    store.merge_day(snap("2026-11-27", {"cse_search": {"cse_invalid_zip": 8}}), "2026-11-27T19:00:30Z")
    hours = EasternRecords(store, dt("2026-11-27T19:00:30Z")).eastern_day("2026-11-27")["hour_problems"]
    assert hours[12] is None  # 17:00 to 18:00: the labels can't be told apart
    assert hours[13]["failed"] == {"cse_search": {"cse_invalid_zip": 1}}


def test_an_exact_day_kept_after_a_rule_bump_stops_taking_backlog_slots(store, settings, monkeypatch):
    from pcbparts_dashboard import eastern

    for date, following in (("2026-10-12", "2026-10-13"), ("2026-10-13", "2026-10-14")):
        for hour in range(24):
            store.add_snapshot(utc_day(date) | {"calls": 10 * hour, "hours": [10] * hour + [0] * (24 - hour)}, f"{date}T{hour:02d}:00:30Z")
        store.merge_day(utc_day(date), f"{following}T00:00:30Z")
    as_of = dt("2026-10-14T00:00:30Z")
    eastern.persist_eastern_days(store, as_of, settings)
    saved = store.eastern_day("2026-10-12")
    assert saved["approx"] is False
    monkeypatch.setattr(eastern, "RULES_VERSION", eastern.RULES_VERSION + 1)
    # the recompute comes back an estimate: the exact day stays, checked under the new rules
    original = eastern.EasternRecords.window
    monkeypatch.setattr(eastern.EasternRecords, "window", lambda self, *a, **k: original(self, *a, **k) | {"approx": True})
    eastern.persist_eastern_days(store, as_of, settings)
    assert store.eastern_day("2026-10-12") == saved
    assert store.eastern_rules_versions()["2026-10-12"] == eastern.RULES_VERSION
    visited = []
    day_of = eastern.EasternRecords.eastern_day
    monkeypatch.setattr(eastern.EasternRecords, "eastern_day", lambda self, day, *a: visited.append(day) or day_of(self, day, *a))
    eastern.persist_eastern_days(store, as_of, settings)
    assert "2026-10-12" not in visited
