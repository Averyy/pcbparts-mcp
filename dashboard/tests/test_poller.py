from datetime import UTC, datetime

import pytest

from pcbparts_dashboard.server import CollectionRunner, Poller, next_poll_at


@pytest.mark.parametrize("at, minutes, expected", [
    ("2026-11-21T19:00:00Z", 60, "2026-11-21T19:00:30Z"),
    ("2026-11-21T19:00:29.999Z", 60, "2026-11-21T19:00:30Z"),
    ("2026-11-21T19:00:30Z", 60, "2026-11-21T20:00:30Z"),
    ("2026-11-21T23:59:59Z", 60, "2026-11-22T00:00:30Z"),
    ("2026-11-21T19:20:00Z", 15, "2026-11-21T19:30:30Z"),
    ("2026-11-21T19:06:59Z", 5, "2026-11-21T19:10:30Z"),
    ("2026-11-21T00:00:30Z", 90, "2026-11-21T01:30:30Z"),
])
def test_wall_clock_alignment(at, minutes, expected):
    assert next_poll_at(datetime.fromisoformat(at), minutes) == datetime.fromisoformat(expected)


def test_poller_collects_immediately_recovers_and_does_not_drift(settings, store, clock, caplog):
    calls = []
    waits = []

    def collect(*_args, **kwargs):
        calls.append(kwargs["now"])
        clock.advance(11)  # Collection duration must not drift the schedule.
        if len(calls) == 2:
            raise RuntimeError("do-not-log-secret")
        return {"ok": True}

    def sleep(seconds):
        waits.append(seconds)
        clock.advance(seconds)
        if len(waits) == 3:
            poller.stop()

    runner = CollectionRunner(settings, store, clock=clock, collector=collect)
    poller = Poller(runner, clock=clock, sleep=sleep)
    assert poller.daemon
    poller.run()  # Deterministic synchronous test; no thread or actual sleeping.
    assert calls == [
        datetime(2026, 11, 21, 19, 20, tzinfo=UTC),
        datetime(2026, 11, 21, 20, 0, 30, tzinfo=UTC),
        datetime(2026, 11, 21, 20, 5, 41, tzinfo=UTC),  # one retry 5 minutes after the failure
    ]
    assert waits == [2419, 300, 3278]
    assert "RuntimeError" in caplog.text
    assert "do-not-log-secret" not in caplog.text
    assert not runner.lock.locked()


def test_start_close_to_slot_respects_minimum_interval(settings, store, clock):
    clock.value = datetime(2026, 11, 21, 19, 0, 15, tzinfo=UTC)
    calls = []
    waits = []

    def sleep(seconds):
        waits.append(seconds)
        clock.advance(seconds)
        if len(waits) == 3:
            poller.stop()

    runner = CollectionRunner(settings, store, clock=clock, collector=lambda *_args, **kw: calls.append(kw["now"]) or {"ok": True})
    poller = Poller(runner, sleep=sleep)
    poller.run()
    assert calls == [datetime(2026, 11, 21, 19, 0, 15, tzinfo=UTC), datetime(2026, 11, 21, 20, 0, 30, tzinfo=UTC)]
    assert waits == [15, 3600, 3600]


def test_stopped_poller_does_not_collect(settings, store, clock):
    def forbidden(*_args, **_kwargs):
        pytest.fail("Stopped poller must not collect")
    poller = Poller(CollectionRunner(settings, store, clock=clock, collector=forbidden))
    poller.stop()
    poller.run()


def test_a_failed_fetch_is_retried_once_after_five_minutes(settings, store, clock):
    """At a deploy the server can still be starting when the dashboard's first fetch runs."""
    calls, waits = [], []
    results = iter([{"ok": False}, {"ok": False}, {"ok": False}, {"ok": True}])

    def sleep(seconds):
        waits.append(seconds)
        clock.advance(seconds)
        if len(waits) == 4:
            poller.stop()

    runner = CollectionRunner(settings, store, clock=clock,
                              collector=lambda *_args, **kw: calls.append(kw["now"]) or next(results))
    poller = Poller(runner, clock=clock, sleep=sleep)
    poller.run()
    # fail at 19:20 -> retry 19:25 fails -> wait for 20:00:30, fails -> one retry 20:05:30 succeeds
    assert waits == [300, 2130, 300, 3300]
    assert calls[1] == datetime(2026, 11, 21, 19, 25, tzinfo=UTC)
