"""Database queue measurement (/health's database_pressure, the stuck-worker exit) and numeric
settings: fake clocks/executors and in-process HTTP, no upstream traffic. Nothing refuses calls on
the queue since 0.10.1 (0.10.0's busy cap was removed)."""

import asyncio
import contextvars
import datetime
import runpy
import types
from concurrent.futures import Future

import httpx
import pytest

from pcbparts_mcp import config, db_worker, server, stats
from pcbparts_mcp.db_worker import DatabasePressure, PoolPressure, PoolRunning

NOW = datetime.datetime(2026, 11, 18, 20, tzinfo=datetime.timezone.utc).timestamp()


class Clock:
    def __init__(self):
        self.now = NOW

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class Executor:
    """Runs submitted work only when the test asks, with concurrent.futures cancellation rules."""
    def __init__(self):
        self.submitted = asyncio.Event()
        self.jobs = []

    def submit(self, func, *args):
        future = Future()
        self.jobs.append((future, func, args))
        self.submitted.set()
        return future

    def run(self):
        future, func, args = self.jobs.pop(0)
        if future.set_running_or_notify_cancel():
            try:
                future.set_result(func(*args))
            except BaseException as error:
                future.set_exception(error)


def client(app):
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost")


class TestPressure:
    def test_counts_age_and_pools(self):
        clock, a, b = Clock(), object(), object()
        pressure = DatabasePressure(clock)
        first = pressure.enqueue(a)
        clock.advance(0.125)
        second = pressure.enqueue(a)
        other = pressure.enqueue(b)
        clock.advance(0.125)
        assert pressure.snapshot() == {a: PoolPressure(2, 0.25), b: PoolPressure(1, 0.125)}
        assert pressure.summary() == {"waiting": 3, "oldest_wait_seconds": 0.25, "stalled_seconds": 0.25,
                                      "running": 0, "longest_running_seconds": 0.0}
        pressure.discard(a, first)
        assert pressure.snapshot()[a] == PoolPressure(1, 0.125)
        for pool, token in ((a, first), (a, second), (b, other)):
            pressure.discard(pool, token)  # repeated discard is harmless
        assert pressure.snapshot() == {}
        assert pressure.summary() == {"waiting": 0, "oldest_wait_seconds": 0.0, "stalled_seconds": 0.0,
                                      "running": 0, "longest_running_seconds": 0.0}

    def test_running_jobs_and_the_longest_run(self):
        """0.10.2: started jobs count as running until discarded, per pool, with the longest run;
        they're not waiting, so they never make a pool stalled."""
        clock, a, b = Clock(), object(), object()
        pressure = DatabasePressure(clock)
        first, second, other = pressure.enqueue(a), pressure.enqueue(a), pressure.enqueue(b)
        pressure.started(a, first)
        clock.advance(2)
        pressure.started(a, second)
        pressure.started(b, other)
        clock.advance(0.5)
        assert pressure.snapshot() == {}
        assert pressure.running() == {a: PoolRunning(2, 2.5), b: PoolRunning(1, 0.5)}
        assert pressure.summary() == {"waiting": 0, "oldest_wait_seconds": 0.0, "stalled_seconds": 0.0,
                                      "running": 3, "longest_running_seconds": 2.5}
        clock.advance(600)  # a very long query is measured, not stopped or refused
        assert pressure.summary()["longest_running_seconds"] == 602.5 and pressure.stalled_seconds() == 0
        pressure.discard(a, first)
        assert pressure.running()[a] == PoolRunning(1, 600.5)
        for pool, token in ((a, second), (b, other), (b, other)):
            pressure.discard(pool, token)
        assert pressure.running() == {}

    async def test_offload_tracks_wait_only_and_keeps_context(self, monkeypatch):
        pressure, pool = DatabasePressure(Clock()), Executor()
        monkeypatch.setattr(db_worker, "database_pressure", pressure)
        context = contextvars.ContextVar("caller", default="missing")
        context.set("test")

        def work():
            assert pressure.snapshot() == {}  # active work doesn't count as queued
            assert pressure.running() == {pool: PoolRunning(1, 0.0)}  # it counts as running
            return context.get()

        task = asyncio.create_task(db_worker.run_db(pool, work))
        await pool.submitted.wait()
        assert pressure.snapshot()[pool].waiting == 1 and pressure.running() == {}
        pool.run()
        assert await task == "test"
        assert pressure.snapshot() == {} and pressure.running() == {}

    async def test_cancelled_queue_and_failed_submission_leave_no_pressure(self, monkeypatch):
        pressure, pool = DatabasePressure(Clock()), Executor()
        monkeypatch.setattr(db_worker, "database_pressure", pressure)
        task = asyncio.create_task(db_worker.run_db(pool, lambda: pytest.fail("cancelled job ran")))
        await pool.submitted.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        pool.run()
        assert pressure.snapshot() == {} and pressure.running() == {}

        def broken(*args):
            raise RuntimeError("closed pool")

        pool.submit = broken
        with pytest.raises(RuntimeError, match="closed pool"):
            await db_worker.run_db(pool, lambda: None)
        assert pressure.snapshot() == {} and pressure.running() == {}

    async def test_failed_query_leaves_no_pressure(self, monkeypatch):
        pressure, pool = DatabasePressure(Clock()), Executor()
        monkeypatch.setattr(db_worker, "database_pressure", pressure)

        def broken():
            raise ValueError("bad query")

        task = asyncio.create_task(db_worker.run_db(pool, broken))
        await pool.submitted.wait()
        pool.run()
        with pytest.raises(ValueError, match="bad query"):
            await task
        assert pressure.snapshot() == {} and pressure.running() == {}


async def test_live_network_waits_do_not_count(monkeypatch):
    pressure = DatabasePressure(Clock())
    entered, release = asyncio.Event(), asyncio.Event()

    async def lookup(lcsc):
        entered.set()
        await release.wait()
        return {"lcsc": lcsc}

    monkeypatch.setattr(db_worker, "database_pressure", pressure)
    monkeypatch.setattr(server, "_client", types.SimpleNamespace(get_part=lookup))
    # live=true: straight to the live lookup (by default a database read for the snapshot comes first)
    tasks = [asyncio.create_task(server.jlc_get_part(lcsc="C1", live=True)) for _ in range(20)]
    try:
        await entered.wait()
        assert pressure.snapshot() == {} and pressure.running() == {}
    finally:
        release.set()
        await asyncio.gather(*tasks)


class TestSettings:
    @pytest.mark.parametrize("name,value,used,warned", [
        ("DB_STUCK_WAIT_SECONDS", "inf", 60.0, True),
        ("DB_STUCK_WAIT_SECONDS", "nan", 60.0, True),
        ("DB_STUCK_WAIT_SECONDS", "0", 1.0, True),
        ("DB_STUCK_WAIT_SECONDS", "-1", 1.0, True),
        ("DB_STUCK_WAIT_SECONDS", " 1.5 ", 1.5, False),
        ("DB_STUCK_WAIT_SECONDS", "300", 300.0, False),
        ("RATE_LIMIT_REQUESTS", "12.5", 100, True),  # was a ValueError at import
        ("RATE_LIMIT_REQUESTS", "", 100, False),
        ("RATE_LIMIT_REQUESTS", "1000000", 1000000, False),
    ], ids=["inf", "nan", "zero", "neg", "float", "stuck", "intfloat", "blank", "big"])
    def test_bad_settings_fall_back(self, monkeypatch, name, value, used, warned):
        monkeypatch.setenv(name, value)
        settings = runpy.run_path(config.__file__)
        assert settings[name] == used and type(settings[name]) is type(used)
        assert any(w.startswith(f"{name}=") for w in settings["CONFIG_WARNINGS"]) is warned

    @pytest.mark.parametrize("name,value,used,warned", [
        ("HTTP_PORT", "abc", 8080, True),  # these two still raised at import
        ("HTTP_PORT", "", 8080, False),
        ("HTTP_PORT", "0", 1, True),
        ("HTTP_PORT", "70000", 65535, True),
        ("HTTP_PORT", " 9000 ", 9000, False),
        ("DISTRIBUTOR_DAILY_LIMIT", "1,000", 1000, True),
        ("DISTRIBUTOR_DAILY_LIMIT", "0", 0, False),  # no distributor requests: kept answers only
        ("DISTRIBUTOR_DAILY_LIMIT", "-5", 0, True),
        ("DISTRIBUTOR_DAILY_LIMIT", "250", 250, False),
    ], ids=["port_text", "port_blank", "port_zero", "port_high", "port_ok", "limit_comma", "limit_zero",
            "limit_neg", "limit_ok"])
    def test_port_and_daily_limit_fall_back(self, monkeypatch, name, value, used, warned):
        monkeypatch.setenv(name, value)
        settings = runpy.run_path(config.__file__)
        assert settings[name] == used and type(settings[name]) is int
        assert any(w.startswith(f"{name}=") for w in settings["CONFIG_WARNINGS"]) is warned

    @pytest.mark.parametrize("sign", ["", "-"], ids=["pos", "neg"])
    def test_integer_too_large_for_a_float_falls_back(self, sign):
        """math.isfinite converts an int to a float: one past a float's range (about 1.8e308, 309
        digits) raised OverflowError at startup."""
        warnings: list[str] = []
        raw = sign + "9" * 309
        assert config.number_setting("RATE_LIMIT_REQUESTS", 100, 1, {"RATE_LIMIT_REQUESTS": raw}, warnings) == 100
        assert len(warnings) == 1 and warnings[0].startswith("RATE_LIMIT_REQUESTS=") and "out of range" in warnings[0]
        assert len(warnings[0]) < 100  # the value isn't repeated whole
        assert config.number_setting("X", 100, 1, {"X": sign + "1" * 309}, []) == (1 if sign else int("1" * 309))


class TestHealth:
    async def test_shows_pressure_and_fails_only_when_stuck(self, monkeypatch):
        """/health shows the pools' queue, and answers 503 once a job has waited
        DB_STUCK_WAIT_SECONDS to start (a stuck worker), so the container's healthcheck fails."""
        clock, pool = Clock(), object()
        pressure = DatabasePressure(clock)
        tokens = [pressure.enqueue(pool) for _ in range(8)]
        monkeypatch.setattr(server, "database_pressure", pressure)
        async with client(server.create_app()) as c:
            reply = await c.get("/health")
            assert reply.status_code == 200 and reply.json()["status"] == "healthy"
            assert reply.json()["database_pressure"] == {
                "waiting": 8, "oldest_wait_seconds": 0.0, "stalled_seconds": 0.0,
                "running": 0, "longest_running_seconds": 0.0,
                "unhealthy_after_seconds": config.DB_STUCK_WAIT_SECONDS}
            clock.advance(config.DB_STUCK_WAIT_SECONDS - 1)  # a long queue, still moving: healthy
            assert (await c.get("/health")).status_code == 200
            clock.advance(1)
            stuck = await c.get("/health")
            assert stuck.status_code == 503
            assert stuck.json()["status"] == "unhealthy" and "stuck worker" in stuck.json()["problem"]
            assert stuck.json()["version"]  # the rest is still there
            for token in tokens:
                pressure.discard(pool, token)
            assert (await c.get("/health")).json()["status"] == "healthy"

    async def test_shows_running_jobs_and_a_long_query_stays_healthy(self, monkeypatch):
        """0.10.2: running and longest_running_seconds show a long query; it is only measured.
        With nothing waiting behind it the pool isn't stuck, so /health stays 200."""
        clock, pool = Clock(), object()
        pressure = DatabasePressure(clock)
        slow, quick = pressure.enqueue(pool), pressure.enqueue(pool)
        pressure.started(pool, slow)
        clock.advance(1.25)
        pressure.started(pool, quick)
        monkeypatch.setattr(server, "database_pressure", pressure)
        async with client(server.create_app()) as c:
            shown = (await c.get("/health")).json()["database_pressure"]
            assert (shown["running"], shown["longest_running_seconds"], shown["waiting"]) == (2, 1.25, 0)
            clock.advance(config.DB_STUCK_WAIT_SECONDS * 10)
            reply = await c.get("/health")
            assert reply.status_code == 200 and reply.json()["status"] == "healthy"
            assert reply.json()["database_pressure"]["longest_running_seconds"] == 1.25 + config.DB_STUCK_WAIT_SECONDS * 10
            pressure.discard(pool, slow)
            pressure.discard(pool, quick)
            shown = (await c.get("/health")).json()["database_pressure"]
            assert (shown["running"], shown["longest_running_seconds"]) == (0, 0.0)


class TestStuckWorkerExit:
    """The minute task exits the process when a database call has waited past DB_STUCK_WAIT_SECONDS
    at two checks in a row, so Docker restarts a stuck server (it shouldn't happen)."""

    @pytest.fixture
    def stuck(self, monkeypatch):
        clock = Clock()
        pressure = DatabasePressure(clock)
        exits = []
        monkeypatch.setattr(server, "database_pressure", pressure)
        monkeypatch.setattr(server, "_exit_process", exits.append)
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        return types.SimpleNamespace(clock=clock, pressure=pressure, exits=exits, pool=object())

    def test_exits_only_after_two_stuck_checks(self, stuck):
        token = stuck.pressure.enqueue(stuck.pool)
        stuck.clock.advance(server.DB_STUCK_WAIT_SECONDS + 1)
        assert server._exit_if_stuck(0) == 1 and stuck.exits == []
        assert server._exit_if_stuck(1) == 2 and stuck.exits == [1]
        stuck.pressure.discard(stuck.pool, token)

    def test_a_healthy_check_resets_the_count(self, stuck):
        token = stuck.pressure.enqueue(stuck.pool)
        stuck.clock.advance(server.DB_STUCK_WAIT_SECONDS + 1)
        assert server._exit_if_stuck(0) == 1
        stuck.pressure.discard(stuck.pool, token)  # the worker got to it
        assert server._exit_if_stuck(1) == 0 and stuck.exits == []

    def test_a_long_but_moving_queue_never_exits(self, stuck):
        token = stuck.pressure.enqueue(stuck.pool)
        stuck.clock.advance(server.DB_STUCK_WAIT_SECONDS - 1)
        assert server._exit_if_stuck(5) == 0 and stuck.exits == []
        stuck.pressure.discard(stuck.pool, token)

    def test_an_overloaded_queue_that_keeps_starting_jobs_never_exits(self, stuck):
        """Without a cap on the queue, sustained overload makes calls wait far past
        DB_STUCK_WAIT_SECONDS while the worker keeps taking jobs: that isn't a stuck worker, and
        restarting would drop every call in flight. Only a pool that starts nothing is stuck."""
        queue = [stuck.pressure.enqueue(stuck.pool) for _ in range(500)]
        checks = 0
        for _ in range(10):  # ten minutes: a job starts every 2 s, the rest wait for minutes
            for _ in range(30):
                stuck.clock.advance(2)
                stuck.pressure.started(stuck.pool, queue.pop(0))
            assert stuck.pressure.summary()["oldest_wait_seconds"] >= server.DB_STUCK_WAIT_SECONDS
            assert stuck.pressure.stalled_seconds() == 0
            checks = server._exit_if_stuck(checks)
            assert checks == 0 and stuck.exits == []
        stuck.clock.advance(server.DB_STUCK_WAIT_SECONDS + 1)  # then the worker hangs
        assert stuck.pressure.stalled_seconds() == server.DB_STUCK_WAIT_SECONDS + 1
        assert server._exit_if_stuck(0) == 1 and server._exit_if_stuck(1) == 2 and stuck.exits == [1]

    def test_an_idle_pool_is_not_stalled_by_its_next_job(self, stuck):
        """Stalled time runs from the oldest waiting job when the last start was before it: a pool
        idle for an hour isn't stuck the moment a job arrives."""
        first = stuck.pressure.enqueue(stuck.pool)
        stuck.pressure.started(stuck.pool, first)
        stuck.clock.advance(3600)
        assert stuck.pressure.stalled_seconds() == 0
        token = stuck.pressure.enqueue(stuck.pool)
        stuck.clock.advance(5)
        assert stuck.pressure.stalled_seconds() == 5
        assert server._exit_if_stuck(0) == 0
        stuck.pressure.discard(stuck.pool, token)

    async def test_the_minute_task_exits_when_stuck(self, stuck, monkeypatch):
        token = stuck.pressure.enqueue(stuck.pool)
        stuck.clock.advance(server.DB_STUCK_WAIT_SECONDS + 1)
        real_sleep, slept = asyncio.sleep, []

        async def one_minute(seconds):
            slept.append(seconds)
            await real_sleep(0)

        monkeypatch.setattr(server.asyncio, "sleep", one_minute)
        task = asyncio.ensure_future(server._every_minute())
        while not stuck.exits and len(slept) < 10:
            await real_sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert stuck.exits == [1] and len(slept) >= 2
        stuck.pressure.discard(stuck.pool, token)
