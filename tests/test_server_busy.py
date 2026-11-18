"""Database admission control: fake clocks/executors and in-process HTTP, no upstream traffic."""

import asyncio
import contextvars
import datetime
import json
import logging
import runpy
import types
from concurrent.futures import Future

import httpx
import pytest
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import Response
from starlette.routing import Route

from pcbparts_mcp import config, db_worker, server, stats
from pcbparts_mcp.cache import CallerTally
from pcbparts_mcp.db_worker import DatabasePressure, PoolPressure

NOW = datetime.datetime(2026, 11, 18, 20, tzinfo=datetime.timezone.utc).timestamp()
CALL = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "ping", "arguments": {}}}


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
        pressure.discard(a, first)
        assert pressure.snapshot()[a] == PoolPressure(1, 0.125)
        for pool, token in ((a, first), (a, second), (b, other)):
            pressure.discard(pool, token)  # repeated discard is harmless
        assert pressure.snapshot() == {}

    def test_thresholds_and_retry(self):
        clock, pool = Clock(), object()
        pressure = DatabasePressure(clock)
        for _ in range(7):
            pressure.enqueue(pool)
        assert pressure.retry_after(8, 0.25) == 0
        pressure.enqueue(pool)
        assert pressure.retry_after(8, 0.25) == 2
        clock.advance(1)
        assert pressure.retry_after(8, 0.25) == 3
        clock.advance(30)
        assert pressure.retry_after(8, 0.25) == 5
        single = DatabasePressure(clock)
        token = single.enqueue(pool)
        clock.advance(0.125)
        assert single.retry_after(8, 0.25) == 0
        clock.advance(0.125)
        assert single.retry_after(8, 0.25) == 2
        single.discard(pool, token)
        assert single.retry_after(8, 0.25) == 0

    def test_queue_threshold_is_per_pool(self):
        pressure = DatabasePressure(Clock())
        for pool in (object(), object()):
            for _ in range(7):
                pressure.enqueue(pool)
        assert pressure.retry_after(8, 0.25) == 0

    async def test_offload_tracks_wait_only_and_keeps_context(self, monkeypatch):
        pressure, pool = DatabasePressure(Clock()), Executor()
        monkeypatch.setattr(db_worker, "database_pressure", pressure)
        context = contextvars.ContextVar("caller", default="missing")
        context.set("test")

        def work():
            assert pressure.snapshot() == {}  # active work doesn't count as queued
            return context.get()

        task = asyncio.create_task(db_worker.run_db(pool, work))
        await pool.submitted.wait()
        assert pressure.snapshot()[pool].waiting == 1
        pool.run()
        assert await task == "test"
        assert pressure.snapshot() == {}

    async def test_cancelled_queue_and_failed_submission_leave_no_pressure(self, monkeypatch):
        pressure, pool = DatabasePressure(Clock()), Executor()
        monkeypatch.setattr(db_worker, "database_pressure", pressure)
        task = asyncio.create_task(db_worker.run_db(pool, lambda: pytest.fail("cancelled job ran")))
        await pool.submitted.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        pool.run()
        assert pressure.snapshot() == {}

        def broken(*args):
            raise RuntimeError("closed pool")

        pool.submit = broken
        with pytest.raises(RuntimeError, match="closed pool"):
            await db_worker.run_db(pool, lambda: None)
        assert pressure.snapshot() == {}

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
        assert pressure.snapshot() == {}

    def test_config_overrides(self, monkeypatch):
        monkeypatch.setenv("DB_BUSY_MAX_WAITING", "3")
        monkeypatch.setenv("DB_BUSY_MAX_WAIT_SECONDS", "0.5")
        settings = runpy.run_path(config.__file__)
        assert (settings["DB_BUSY_MAX_WAITING"], settings["DB_BUSY_MAX_WAIT_SECONDS"]) == (3, 0.5)


@pytest.fixture
def busy(monkeypatch):
    clock = Clock()
    pressure = DatabasePressure(clock)
    pool = object()
    tokens = [pressure.enqueue(pool) for _ in range(8)]
    usage = stats.UsageStats(clock=clock)
    tally = CallerTally("Server busy limit", clock, what="refusals")
    monkeypatch.setattr(stats, "usage", usage)
    monkeypatch.setattr(server, "database_pressure", pressure)
    monkeypatch.setattr(server, "_busy_refused_callers", tally)
    return types.SimpleNamespace(clock=clock, pressure=pressure, pool=pool, tokens=tokens, usage=usage, tally=tally)


async def echo(request):
    return Response(await request.body(), media_type="application/json")


def app_for(busy, **kwargs):
    # The thresholds these tests are written for, independent of the configured defaults
    kwargs.setdefault("busy_max_waiting", 8)
    kwargs.setdefault("busy_max_wait", 0.25)
    return Starlette(routes=[Route("/mcp", echo, methods=["POST", "GET"]), Route("/health", echo),
                             Route("/mcp/stats", echo)],
                     middleware=[Middleware(server.BodySizeLimitMiddleware),
                                 Middleware(server.RateLimitMiddleware, clock=busy.clock, **kwargs)])


def client(app):
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost")


class TestBusyHTTP:
    @pytest.mark.parametrize("ip,limit", [("203.0.113.7", 100), ("160.79.104.10", 1000)], ids=["normal", "platform"])
    async def test_shape_headers_recovery_and_no_ip_charge(self, busy, ip, limit):
        async with client(app_for(busy)) as c:
            reply = await c.post("/mcp", json=CALL, headers={"X-Forwarded-For": ip})
            assert reply.status_code == 429
            assert reply.json() == {"error": "Rate limit exceeded", "retry_after": 2, "reason": "server_busy",
                                    "resets_at": "2026-11-18T20:00:02Z",
                                    "tell_user": "pcbparts is busy answering database calls; try again in 2 seconds."}
            assert [reply.headers[name] for name in ("retry-after", "x-ratelimit-limit", "x-ratelimit-remaining",
                                                      "x-ratelimit-reset")] == ["2", str(limit), "0", "2"]
            for token in busy.tokens:
                busy.pressure.discard(busy.pool, token)
            reply = await c.post("/mcp", json=CALL, headers={"X-Forwarded-For": ip})
            assert reply.status_code == 200 and reply.json() == CALL
            assert reply.headers["x-ratelimit-remaining"] == str(limit - 1)

    @pytest.mark.parametrize("payload", [
        {"id": 1, "method": "initialize"}, {"method": "notifications/initialized"},
        {"id": 1, "method": "tools/list"}, {"id": 1, "method": "ping"},
        {"method": "tools/call"}, [{"id": 1, "method": "tools/call"}], None, 12,
    ], ids=["init", "note", "list", "ping", "noid", "batch", "null", "number"])
    async def test_other_methods_replayed(self, busy, payload):
        async with client(app_for(busy)) as c:
            raw = json.dumps(payload).encode()
            reply = await c.post("/mcp", content=raw)
            assert reply.status_code == 200 and reply.content == raw

    @pytest.mark.parametrize("raw", [b"not json", b"\xff", b"[" * 2000], ids=["invalid", "utf8", "nested"])
    async def test_bad_json_replayed_for_sdk_validation(self, busy, raw):
        async with client(app_for(busy)) as c:
            reply = await c.post("/mcp", content=raw)
            assert reply.status_code == 200 and reply.content == raw

    async def test_health_stats_and_non_posts_never_busy(self, busy):
        async with client(app_for(busy, requests_per_minute=1)) as c:
            assert (await c.get("/mcp")).status_code == 200  # uses up this address's allowance
            for path in ("/health", "/mcp/stats"):
                for _ in range(2):
                    assert (await c.get(path)).status_code == 200
            assert (await c.get("/mcp")).json()["reason"] == "per_ip_rate_limit"

    async def test_exhausted_address_refused_before_body_read(self, busy):
        async def chunks():
            pytest.fail("read a body from an exhausted address")
            yield b""

        async with client(app_for(busy, requests_per_minute=1)) as c:
            assert (await c.post("/mcp", json={"id": 1, "method": "tools/list"})).status_code == 200
            reply = await c.post("/mcp", content=chunks())
            assert reply.status_code == 429 and reply.json()["reason"] == "per_ip_rate_limit"

    async def test_real_health_stats_are_available_under_pressure(self, busy):
        from pcbparts_mcp.config import DB_BUSY_MAX_WAITING  # the real app uses the configured threshold
        for _ in range(max(0, DB_BUSY_MAX_WAITING - len(busy.tokens))):
            busy.tokens.append(busy.pressure.enqueue(busy.pool))
        async with client(server.create_app()) as c:
            assert (await c.post("/mcp", json=CALL)).json()["reason"] == "server_busy"
            assert (await c.get("/health")).status_code == 200
            counts = (await c.get("/mcp/stats")).json()["days"][0]["per_ip_refusals"]
            assert counts == {"total": 1, "everyone_else": 0, "platform_ranges": 0, "server_busy": 1}

    async def test_threshold_overrides(self, busy):
        async with client(app_for(busy, busy_max_waiting=9, busy_max_wait=0.5)) as c:
            assert (await c.post("/mcp", json=CALL)).status_code == 200
            busy.clock.advance(0.25)
            assert (await c.post("/mcp", json=CALL)).status_code == 200
            busy.clock.advance(0.25)
            reply = await c.post("/mcp", json=CALL)
            assert reply.json()["reason"] == "server_busy" and reply.json()["retry_after"] == 5

    @pytest.mark.parametrize("method", ["tools/call", "initialize"], ids=["call", "init"])
    async def test_chunked_body_replayed_or_refused(self, busy, method):
        async def chunks():
            yield b'{"jsonrpc":"2.0",'
            yield json.dumps({"id": 1, "method": method})[1:].encode()

        async with client(app_for(busy)) as c:
            reply = await c.post("/mcp", content=chunks())
            if method == "tools/call":
                assert reply.status_code == 429 and reply.json()["reason"] == "server_busy"
            else:
                assert reply.status_code == 200 and reply.json()["method"] == "initialize"

    @pytest.mark.parametrize("declared", [None, "1", "1000001"], ids=["chunked", "false", "large"])
    async def test_body_size_guard(self, busy, declared):
        read = False

        async def chunks():
            nonlocal read
            read = True
            yield b"x" * 600_000
            yield b"x" * 500_000

        async with client(app_for(busy)) as c:
            reply = await c.post("/mcp", content=chunks(),
                                 headers={} if declared is None else {"Content-Length": declared})
        assert reply.status_code == 413 and reply.json() == {"error": "Request body too large"}
        assert read is (declared != "1000001")  # declared-size guard runs before body inspection

    async def test_stats_saved_per_day_without_ips_and_hourly_log(self, busy, tmp_path, caplog):
        path = tmp_path / "usage.json"
        busy.usage.open(path)
        async with client(app_for(busy)) as c:
            for ip in ("203.0.113.7", "160.79.104.10"):
                assert (await c.post("/mcp", json=CALL, headers={"X-Forwarded-For": ip})).status_code == 429
            busy.clock.advance(86400)
            assert (await c.post("/mcp", json=CALL)).status_code == 429
        busy.usage.save()
        text = path.read_text(encoding="utf-8")
        assert "203.0.113.7" not in text and "160.79.104.10" not in text
        restored = stats.UsageStats(clock=busy.clock)
        restored.open(path)
        summary = restored.summary()
        assert [day["per_ip_refusals"]["server_busy"] for day in summary["days"]] == [1, 2]
        assert summary["totals"]["per_ip_refusals"]["server_busy"] == 3
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            busy.clock.advance(3600)
            busy.tally.flush_if_due()
        assert any(message.startswith("Server busy limit refusals ") for message in caplog.messages)

    async def test_busy_streamable_mcp_replays_cheap_method(self, busy):
        mcp = FastMCP("busy-test")
        app = mcp.http_app(path="/mcp", stateless_http=True,
                           middleware=[Middleware(server.BodySizeLimitMiddleware),
                                       Middleware(server.RateLimitMiddleware, clock=busy.clock)])
        async with app.router.lifespan_context(app):
            async with client(app) as c:
                reply = await c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                     "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                                "clientInfo": {"name": "test", "version": "1"}}},
                                     headers={"Accept": "application/json, text/event-stream"})
        assert reply.status_code == 200 and reply.headers["content-type"].startswith("text/event-stream")
        assert '"name":"busy-test"' in reply.text


async def test_live_network_waits_do_not_count(monkeypatch):
    pressure = DatabasePressure(Clock())
    entered, release = asyncio.Event(), asyncio.Event()

    async def lookup(lcsc):
        entered.set()
        await release.wait()
        return {"lcsc": lcsc}

    monkeypatch.setattr(db_worker, "database_pressure", pressure)
    monkeypatch.setattr(server, "_client", types.SimpleNamespace(get_part=lookup))
    tasks = [asyncio.create_task(server.jlc_get_part(lcsc="C1")) for _ in range(20)]
    try:
        await entered.wait()
        assert pressure.snapshot() == {} and pressure.retry_after(8, 0.25) == 0
    finally:
        release.set()
        await asyncio.gather(*tasks)
