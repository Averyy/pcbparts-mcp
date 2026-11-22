"""The JSON contract consumed by the dashboard frontend."""

from .config import Settings
from .eastern import EasternRecords, TIMEZONE, problems_settings
from .store import Store, parse_timestamp, timestamp, utc_datetime


def build_payload(store: Store, settings: Settings, now, *, next_poll=None) -> dict:
    """next_poll: when the poller runs next, or None when this process doesn't poll."""
    moment = utc_datetime(now)
    with store.lock:
        health_at, health = store.newest_health()
        last_success = store.get_meta("last_success_at")
        # Imports do not update live-success metadata, but can still be served on their own.
        as_of = last_success or store.newest_stats_at()
        since, version = problems_settings(store, settings)
        records = EasternRecords(store, parse_timestamp(as_of), version) if as_of else None
        current_version = health.get("version") if isinstance(health, dict) else None
        version_since = None
        if isinstance(current_version, str) and current_version:
            version_since = {
                "version": current_version,
                "since": since if version == current_version else store.version_fetch_at(current_version),
            }
        return {
            "generated_at": timestamp(moment),
            "poll_minutes": settings.poll_minutes,
            "next_poll_at": timestamp(next_poll) if next_poll else None,
            "last_fetch": store.get_meta("last_fetch"),
            "last_success_at": last_success,
            "warnings": store.get_meta("warnings", []),
            "latency_bounds_ms": store.get_meta("latency_bounds_ms", []),
            "about": store.get_meta("about"),
            "timezone": TIMEZONE,
            "as_of": as_of,
            "edays": records.all_days(parse_timestamp(since) if since else None) if records else [],
            "compare_today": records.compare_today() if records else None,
            "problems_since": since,
            "problems_version": version,
            "version_since": version_since,
            "health": health,
            "health_at": health_at,
        }
