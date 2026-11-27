"""The JSON contract consumed by the dashboard frontend."""

from datetime import timedelta

from .config import Settings
from .eastern import EASTERN, EasternRecords, TIMEZONE, eastern_bounds, problems_settings
from .store import Store, parse_timestamp, timestamp, utc_datetime

# The newest server versions that get a scorecard (calls, failures, refusals, response times).
SCORECARD_VERSIONS = 6


def _number(value) -> bool:
    return type(value) in (int, float)


# A health check can read the version before a start the server listed to the minute ("HH:MM",
# seconds dropped): a check this soon after a listed start that still shows the older version is that.
START_ROUNDING = timedelta(minutes=2)


def version_runs(store: Store, edays: list[dict], current: str | None, current_since: str | None) -> list[dict]:
    """When each server version began running, oldest first: [{version, from, to, exact, after}].

    From the server's own start list (days[].starts, from 0.10.12: exact) and the dashboard's own
    checks of /health (each stored sample, and the first one of every version, kept past pruning), so
    a rollback to a version that lists no starts is a run of its own. A run seen only by the checks
    began after `after` (the last check of the version before) and by `from`.
    """
    events = [(start["at"], start.get("version"), True) for day in edays for start in (day.get("starts") or [])
              if isinstance(start, dict) and isinstance(start.get("at"), str) and start.get("version")]
    events += [(at, version, False) for at, version in store.version_observations()]
    events += [(at, version, False) for version, at in (store.get_meta("version_first_seen", {}) or {}).items()
               if isinstance(at, str)]
    events.sort(key=lambda event: (event[0], not event[2]))
    runs, last_seen = [], None
    for at, version, exact in events:
        if runs and runs[-1]["version"] == version:
            last_seen = at
            continue
        if runs and not exact and runs[-1]["exact"] and len(runs) > 1 and runs[-2]["version"] == version and (
                parse_timestamp(at) - parse_timestamp(runs[-1]["from"]) < START_ROUNDING):
            continue  # the check read the old version in the minute the listed start rounds down
        run = {"version": version, "from": at, "exact": exact}
        if runs and not exact and last_seen:
            run["after"] = last_seen
        runs.append(run)
        last_seen = at
    # A version seen again with no check stored (pruned) starts at the header's since
    if current and current_since and (not runs or runs[-1]["version"] != current) and (
            not runs or current_since > runs[-1]["from"]):
        runs.append({"version": current, "from": current_since, "exact": False})
    for run, following in zip(runs, runs[1:] + [None]):
        run["to"] = following["from"] if following else None
    return runs


def _scorecard(window: dict) -> dict:
    """The few numbers that compare versions, from one window over a version's run."""
    tools = [tool for tool in (window.get("tools") or {}).values() if isinstance(tool, dict)]

    def outcome(key):
        return sum(tool.get(key) or 0 for tool in tools if _number(tool.get(key)))

    held = 0
    for limits in (window.get("distributor_limits") or {}).values():
        for cause, count in ((limits or {}).get("held_back") or {}).items():
            # the block list's holds are information, not something the server got wrong
            if cause != "address_blocked" and _number(count):
                held += count
    refused = (window.get("per_ip_refusals") or {}).get("total")
    links = (window.get("datasheet_links") or {}).get("refused")
    latency = None
    for entry in (window.get("latency") or {}).values():
        counts = entry.get("counts") if isinstance(entry, dict) else None
        if not isinstance(counts, list):
            continue
        latency = latency or [0] * len(counts)
        latency += [0] * (len(counts) - len(latency))
        for index, count in enumerate(counts):
            latency[index] += count if _number(count) else 0
    calls = window.get("calls")
    return {
        "calls": calls if _number(calls) else outcome("calls"),
        "failed": outcome("failed"),
        "rejected": outcome("bad_request"),
        "turned_away": (refused if _number(refused) else 0) + held + (links if _number(links) else 0),
        "latency": latency,
        "approx": bool(window.get("approx")),
    }


def _add_scores(total: dict | None, part: dict) -> dict:
    if total is None:
        return dict(part)
    result = dict(total)
    for key in ("calls", "failed", "rejected", "turned_away"):
        result[key] = (total.get(key) or 0) + (part.get(key) or 0)
    a, b = total.get("latency"), part.get("latency")
    if a is None or b is None:
        result["latency"] = a or b
    else:
        result["latency"] = [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(max(len(a), len(b)))]
    result["approx"] = bool(total.get("approx") or part.get("approx"))
    return result


def run_scorecard(records: EasternRecords, edays: dict[str, dict], start, end) -> dict:
    """A run's scorecard: its whole Eastern days as already computed, and windows only for the hours
    before its first midnight and after its last."""
    first = eastern_bounds(start.astimezone(EASTERN).date())[1]  # the first Eastern midnight after start
    last = eastern_bounds(end.astimezone(EASTERN).date())[0]     # the last one at or before end
    days = []
    cursor = first
    while cursor < last:
        day = edays.get(cursor.astimezone(EASTERN).date().isoformat())
        if day is None or not day.get("complete"):
            return _scorecard(records.window(start, end))
        days.append(day)
        cursor = eastern_bounds(cursor.astimezone(EASTERN).date())[1]
    if not days:
        return _scorecard(records.window(start, end))
    total = None
    for part in ([records.window(start, first)] if start < first else []) + days + ([records.window(last, end)] if last < end else []):
        total = _add_scores(total, _scorecard(part))
    return total


def build_payload(store: Store, settings: Settings, now, *, next_poll=None) -> dict:
    """next_poll: when the poller runs next, or None when this process doesn't poll."""
    moment = utc_datetime(now)
    with store.lock:
        health_at, health = store.newest_health()
        last_success = store.get_meta("last_success_at")
        # Imports do not update live-success metadata, but can still be served on their own.
        as_of = last_success or store.newest_stats_at()
        since, version = problems_settings(store, settings)
        # saved days are upgraded by the polls a few at a time, never while a page waits
        records = EasternRecords(store, parse_timestamp(as_of), version, upgrade=False) if as_of else None
        current_version = health.get("version") if isinstance(health, dict) else None
        version_since = None
        if isinstance(current_version, str) and current_version:
            version_since = {
                "version": current_version,
                "since": since if version == current_version else store.version_fetch_at(current_version),
                # the first fetch that saw it: with since (the last fetch before it), the start lies between
                "first_seen": store.version_fetch_at(current_version),
                "configured": bool(settings.problems_since) and version == current_version,
            }
        edays = records.all_days(parse_timestamp(since) if since else None) if records else []
        runs = version_runs(store, edays, current_version if isinstance(current_version, str) else None,
                            version_since["since"] if version_since else None)
        if records:
            first_day = min(records.days) + "T00:00:00Z" if records.days else None
            by_date = {day["date"]: day for day in edays}
            for run in runs[-SCORECARD_VERSIONS:]:
                start = max(run["from"], first_day) if first_day else run["from"]
                end = min(run["to"] or as_of, as_of)
                if start < end:
                    run.update(run_scorecard(records, by_date, parse_timestamp(start), parse_timestamp(end)))
                    # the run began before the first stored day: the numbers cover only its stored part
                    run["partial"] = start != run["from"]
        kept = store.get_meta("kept_across_restarts")
        return {
            "generated_at": timestamp(moment),
            "poll_minutes": settings.poll_minutes,
            "next_poll_at": timestamp(next_poll) if next_poll else None,
            "last_fetch": store.get_meta("last_fetch"),
            "last_success_at": last_success,
            "warnings": store.get_meta("warnings", []),
            "latency_bounds_ms": store.get_meta("latency_bounds_ms", []),
            "about": store.get_meta("about"),
            "kept_across_restarts": kept.get("value") if isinstance(kept, dict) else None,
            "timezone": TIMEZONE,
            "as_of": as_of,
            "edays": edays,
            "compare_today": records.compare_today() if records else None,
            "problems_since": since,
            "problems_version": version,
            "version_since": version_since,
            "versions": runs,
            "catalog_changes": store.catalog_changes(),
            "health": health,
            "health_at": health_at,
        }
