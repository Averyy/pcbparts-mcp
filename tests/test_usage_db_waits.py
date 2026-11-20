"""Anonymous database queue history: fake executors and clocks, no network or real delays."""

import asyncio
import datetime
import json

import pytest

from pcbparts_mcp import config, db_worker, stats
from pcbparts_mcp.stats import UsageStats

from test_db_pressure import Executor
from test_usage_stats import Clock


def waits(usage, day=0):
    return usage.summary()["days"][day]["db_waits"]


def test_counts_threshold_hours_components_and_totals():
    clock = Clock()
    usage = UsageStats(clock=clock)
    assert config.DB_WAIT_COUNTED_SECONDS == 0.1
    usage.record_db_wait(0, True)
    usage.record_db_wait(0.0999, True)  # rounds to 100 ms but has not reached the threshold
    usage.record_db_wait(0.1, True)
    usage.record_db_wait(2.345, False)
    clock.advance(3600)
    usage.record_db_wait(0.25, True)
    first = waits(usage)
    assert first["jobs"] == 5 and first["waited"] == 3 and first["longest_ms"] == 2345
    assert first["waited_hours"] == [0] * 21 + [2, 1, 0]
    assert first["longest_ms_hours"] == [0] * 21 + [2345, 250, 0]
    components = first["components"]
    assert components["jobs"] == 4 and components["waited"] == 2 and components["longest_ms"] == 250
    assert components["waited_hours"] == [0] * 21 + [1, 1, 0]
    assert components["longest_ms_hours"] == [0] * 21 + [100, 250, 0]
    assert set(first) == {"jobs", "waited", "longest_ms", "waited_hours", "longest_ms_hours", "components"}
    assert set(components) == set(first) - {"components"}
    clock.advance(86400)
    usage.record_db_wait(0.5, True)
    clock.advance(86400)
    usage.record_db_wait(0.125, False)
    total = usage.summary()["totals"]["db_waits"]
    assert total["jobs"] == 7 and total["waited"] == 5 and total["longest_ms"] == 2345
    assert total["waited_hours"] == [0] * 21 + [2, 3, 0]
    assert total["longest_ms_hours"] == [0] * 21 + [2345, 500, 0]
    assert total["components"]["jobs"] == 5 and total["components"]["longest_ms"] == 500
    recent = usage.summary(days=2)["totals"]["db_waits"]
    assert recent["jobs"] == 2 and recent["waited"] == 2 and recent["longest_ms"] == 500
    assert recent["components"]["jobs"] == 1
    for text in ("db_waits", "0.10.3", "0.1 s ", "jobs", "waited", "longest_ms", "waited_hours",
                 "longest_ms_hours", "components", "UTC hour", "maximum"):
        assert text in usage.summary()["about"]


def test_old_days_null_and_new_counts_survive_restart(tmp_path):
    path = tmp_path / "stats.json"
    path.write_text(json.dumps({"days": {"2026-10-16": {}, "2026-10-17": {}}}), encoding="utf-8")
    usage = UsageStats(clock=Clock())
    usage.open(path)
    assert waits(usage) is None and waits(usage, 1) is None
    assert usage.summary()["totals"]["db_waits"]["jobs"] == 0
    usage.record_db_wait(0.125, True)
    usage.save()
    again = UsageStats(clock=Clock())
    again.open(path)
    assert waits(again) == waits(usage) and waits(again, 1) is None
    again.record_db_wait(0.25)
    assert waits(again)["jobs"] == 2 and waits(again)["components"]["jobs"] == 1


@pytest.mark.parametrize("value", [None, "bad", [], True, 7])
def test_malformed_field_is_null(tmp_path, value):
    path = tmp_path / "stats.json"
    path.write_text(json.dumps({"days": {"2026-10-17": {"db_waits": value}}}), encoding="utf-8")
    usage = UsageStats(clock=Clock())
    usage.open(path)
    assert waits(usage) is None
    usage.record_db_wait(0)
    assert waits(usage)["jobs"] == 1


def test_stored_values_cleaned_and_unknown_keys_dropped(tmp_path):
    path = tmp_path / "stats.json"
    value = {"jobs": 4.9, "waited": True, "longest_ms": float("inf"),
             "waited_hours": [None, -1, "2", 3, float("nan"), 10**400] + [0] * 18,
             "longest_ms_hours": [0] * 23,
             "components": {"jobs": "bad", "waited": -3, "longest_ms": 250,
                            "waited_hours": "bad", "longest_ms_hours": [250] + [0] * 23,
                            "query": "private"}, "address": "private"}
    path.write_text(json.dumps({"days": {"2026-10-17": {"db_waits": value}}}), encoding="utf-8")
    usage = UsageStats(clock=Clock())
    usage.open(path)
    clean = waits(usage)
    assert clean["jobs"] == 4 and clean["waited"] == 0 and clean["longest_ms"] == 0
    assert clean["waited_hours"] == [0, 0, 0, 3] + [0] * 20
    assert clean["longest_ms_hours"] == [0] * 24
    assert clean["components"]["jobs"] == 0 and clean["components"]["waited"] == 0
    assert clean["components"]["longest_ms"] == 250
    assert clean["components"]["longest_ms_hours"] == [250] + [0] * 23
    usage.record_db_wait(0.125, True)
    usage.save()
    assert "private" not in path.read_text(encoding="utf-8")


async def test_run_db_counts_at_worker_start_not_completion(monkeypatch):
    clock, mono = Clock(), Clock(0)
    usage, pool = UsageStats(clock=clock), Executor()
    pressure = db_worker.DatabasePressure(mono)
    monkeypatch.setattr(stats, "usage", usage)
    monkeypatch.setattr(db_worker, "database_pressure", pressure)
    monkeypatch.setattr(db_worker, "COMPONENT_POOL", pool)

    def work():
        mono.advance(600)  # query execution time is excluded
        clock.advance(86400)  # callback runs after completion, but counts on the start day
        return "answer"

    task = asyncio.create_task(db_worker.run_db(pool, work))
    await pool.submitted.wait()
    mono.advance(0.125)
    pool.run()
    assert await task == "answer"
    summary = usage.summary()
    assert len(summary["days"]) == 1 and summary["days"][0]["date"] == "2026-10-17"
    assert waits(usage)["jobs"] == waits(usage)["components"]["jobs"] == 1
    assert waits(usage)["longest_ms"] == 125
    assert waits(usage)["waited_hours"] == [0] * 21 + [1, 0, 0]


async def test_run_db_all_pools_and_failed_jobs_but_not_cancelled_or_unsubmitted(monkeypatch):
    mono, pool = Clock(0), Executor()
    usage = UsageStats(clock=Clock())
    monkeypatch.setattr(stats, "usage", usage)
    monkeypatch.setattr(db_worker, "database_pressure", db_worker.DatabasePressure(mono))

    def failed():
        raise ValueError("failed query")

    task = asyncio.create_task(db_worker.run_db(pool, failed))
    await pool.submitted.wait()
    mono.advance(0.25)
    pool.run()
    with pytest.raises(ValueError, match="failed query"):
        await task
    assert waits(usage)["jobs"] == 1 and waits(usage)["components"]["jobs"] == 0
    pool.submitted.clear()
    cancelled = asyncio.create_task(db_worker.run_db(pool, lambda: pytest.fail("cancelled job ran")))
    await pool.submitted.wait()
    cancelled.cancel()
    with pytest.raises(asyncio.CancelledError):
        await cancelled
    pool.run()

    def broken(*args):
        raise RuntimeError("submission failed")

    pool.submit = broken
    with pytest.raises(RuntimeError, match="submission failed"):
        await db_worker.run_db(pool, lambda: None)
    assert waits(usage)["jobs"] == 1


async def test_measurement_failure_never_breaks_database_job(monkeypatch):
    pool = Executor()
    monkeypatch.setattr(stats, "usage", UsageStats(clock=Clock()))

    def broken(*args):
        raise ValueError("counter failed")

    monkeypatch.setattr(stats.usage, "record_db_wait", broken)
    task = asyncio.create_task(db_worker.run_db(pool, lambda: "still works"))
    await pool.submitted.wait()
    pool.run()
    assert await task == "still works"


def test_explicit_start_time_places_job_in_its_utc_hour():
    usage = UsageStats(clock=Clock())
    started = datetime.datetime(2026, 10, 18, 0, 0, tzinfo=datetime.timezone.utc)
    usage.record_db_wait(0.5, started_at=started)
    assert usage.summary()["days"][0]["date"] == "2026-10-18"
    assert waits(usage)["waited_hours"] == [1] + [0] * 23
