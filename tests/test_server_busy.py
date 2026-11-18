"""Database admission control: fake clocks/executors and in-process HTTP, no upstream traffic."""

import asyncio
import contextvars
import datetime
import json
import logging
import math
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

    @pytest.mark.parametrize("name,value,used,warned", [
        ("DB_BUSY_MAX_WAIT_SECONDS", "inf", 0.5, True),  # was accepted: OverflowError on every POST
        ("DB_BUSY_MAX_WAIT_SECONDS", "nan", 0.5, True),
        ("DB_BUSY_MAX_WAIT_SECONDS", "0", 0.001, True),
        ("DB_BUSY_MAX_WAIT_SECONDS", " 1.5 ", 1.5, False),
        ("DB_BUSY_MAX_WAITING", "12.5", 12, True),  # was a ValueError at import
        ("DB_BUSY_MAX_WAITING", "", 12, False),
        ("DB_BUSY_MAX_WAITING", "1000000", 1000000, False),  # how to turn the cap off (with the wait)
        ("DB_STUCK_WAIT_SECONDS", "-1", 1.0, True),
        ("DB_STUCK_WAIT_SECONDS", "300", 300.0, False),
    ], ids=["inf", "nan", "zero", "float", "intfloat", "blank", "off", "neg", "stuck"])
    def test_bad_settings_fall_back(self, monkeypatch, name, value, used, warned):
        monkeypatch.setenv(name, value)
        settings = runpy.run_path(config.__file__)
        assert settings[name] == used and type(settings[name]) is type(used)
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

    def test_huge_or_infinite_wait_never_overflows(self):
        pressure, pool = DatabasePressure(Clock()), object()
        for _ in range(3):
            pressure.enqueue(pool)
        assert pressure.retry_after(1, math.inf) == 5
        assert pressure.retry_after(1, 1e308) == 5
        assert pressure.retry_after(10**6, 10**6) == 0  # both very large: the cap is off

    def test_reservations_count_as_waiting(self):
        """Tool calls admitted but not started count as one more waiting job in every pool, have
        no age, and are released once."""
        clock, pool = Clock(), object()
        pressure = DatabasePressure(clock)
        held = [pressure.reserve() for _ in range(7)]
        assert pressure.retry_after(8, 0.25) == 0
        token = pressure.enqueue(pool)
        assert pressure.retry_after(8, 0.25) == 2  # 1 queued + 7 admitted
        held[0].release()
        held[0].release()  # idempotent
        assert (pressure.reserved, pressure.retry_after(8, 0.25)) == (6, 0)
        pressure.discard(pool, token)
        held += [pressure.reserve() for _ in range(2)]
        assert pressure.retry_after(8, 0.25) == 2  # 8 admitted, nothing queued yet
        clock.advance(10)
        assert pressure.summary() == {"waiting": 0, "oldest_wait_seconds": 0.0, "admitted_not_started": 8}
        for reservation in held:
            reservation.release()
        assert (pressure.reserved, pressure.retry_after(8, 0.25)) == (0, 0)


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
    # In-process bodies arrive at once; a long deadline keeps a slow CI runner from racing the real
    # 2 s one (the slow-body test sets its own)
    kwargs.setdefault("busy_body_timeout", 60)
    return Starlette(routes=[Route("/mcp", echo, methods=["POST", "GET"]), Route("/health", echo),
                             Route("/mcp/stats", echo)],
                     middleware=[Middleware(server.BodySizeLimitMiddleware),
                                 Middleware(server.RateLimitMiddleware, clock=busy.clock, wall_clock=busy.clock,
                                            **kwargs)])


def client(app):
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost")


class TestBusyHTTP:
    @pytest.mark.parametrize("ip,limit", [("203.0.113.7", 100), ("160.79.104.10", 1000)], ids=["normal", "platform"])
    async def test_shape_headers_recovery_and_ip_charge(self, busy, ip, limit):
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
            assert reply.headers["x-ratelimit-remaining"] == str(limit - 2)  # the busy refusal counted too

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
        async with client(app_for(busy, requests_per_minute=3)) as c:
            assert (await c.get("/mcp")).status_code == 200
            for _ in range(2):
                assert (await c.get("/health")).status_code == 200  # not counted
                assert (await c.get("/mcp/stats")).status_code == 200  # counted, never busy
            assert (await c.get("/mcp/stats")).json()["reason"] == "per_ip_rate_limit"
            assert (await c.get("/health")).status_code == 200

    async def test_busy_refusals_use_up_the_address(self, busy):
        """A flood during an overload: each busy 429 takes one of the address's requests, so it
        then gets per-IP 429s (refused before its body is read), and other addresses carry on."""
        async with client(app_for(busy, requests_per_minute=3)) as c:
            reasons = [(await c.post("/mcp", json=CALL, headers={"X-Forwarded-For": "203.0.113.7"})).json()["reason"]
                       for _ in range(4)]
            assert reasons == ["server_busy"] * 3 + ["per_ip_rate_limit"]
            other = await c.post("/mcp", json=CALL, headers={"X-Forwarded-For": "203.0.113.8"})
            assert other.json()["reason"] == "server_busy"
        assert busy.usage.summary()["days"][0]["per_ip_refusals"]["server_busy"] == 4
        assert busy.tally._counts == {"203.0.113.7": 3, "203.0.113.8": 1}

    async def test_slow_body_refused_as_busy(self, busy):
        """A body that doesn't arrive in time while the server is overloaded is refused as busy, and charged."""
        stalled = asyncio.Event()

        async def chunks():
            yield b'{"jsonrpc":"2.0",'
            await stalled.wait()  # never set: the rest never comes
            yield b"}"

        async with client(app_for(busy, busy_body_timeout=0, requests_per_minute=2)) as c:
            reply = await c.post("/mcp", content=chunks())
            assert reply.status_code == 429 and reply.json()["reason"] == "server_busy"
            assert reply.json()["retry_after"] == 2
            assert (await c.post("/mcp", json=CALL)).json()["reason"] == "server_busy"
            assert (await c.post("/mcp", json=CALL)).json()["reason"] == "per_ip_rate_limit"

    async def test_disconnect_mid_body_under_pressure(self, busy, caplog):
        """The client leaves while the busy peek reads its body: no "No response returned."
        RuntimeError from BodySizeLimitMiddleware, no traceback; charged as without pressure."""
        app = app_for(busy, requests_per_minute=1)
        messages = [{"type": "http.request", "body": b'{"jsonrpc":', "more_body": True}, {"type": "http.disconnect"}]
        sent = []

        async def receive():
            return messages.pop(0) if messages else {"type": "http.disconnect"}

        async def send(message):
            sent.append(message)

        scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "POST",
                 "scheme": "http", "path": "/mcp", "raw_path": b"/mcp", "root_path": "", "query_string": b"",
                 "headers": [(b"host", b"localhost"), (b"content-type", b"application/json")],
                 "client": ("203.0.113.7", 5000), "server": ("localhost", 80)}
        with caplog.at_level(logging.ERROR):
            await app(scope, receive, send)
        assert sent[0]["type"] == "http.response.start" and not caplog.records
        async with client(app) as c:  # that used the address's one request
            reply = await c.post("/mcp", json={"id": 1, "method": "tools/list"}, headers={"X-Forwarded-For": "203.0.113.7"})
            assert reply.json()["reason"] == "per_ip_rate_limit"

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
            assert counts == {"total": 1, "everyone_else": 0, "platform_ranges": 0, "server_busy": 1, "too_many_clients": 0}

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
        # A body read and cut off was charged, so its 413 says where the address stands; a declared
        # size is refused before the limiter sees it
        assert reply.headers.get("x-ratelimit-remaining") == (None if declared == "1000001" else "99")

    async def test_disconnect_reply_carries_rate_headers(self, busy):
        app = app_for(busy)
        messages = [{"type": "http.request", "body": b'{"jsonrpc":', "more_body": True}, {"type": "http.disconnect"}]
        sent = []

        async def receive():
            return messages.pop(0) if messages else {"type": "http.disconnect"}

        async def send(message):
            sent.append(message)

        scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "POST",
                 "scheme": "http", "path": "/mcp", "raw_path": b"/mcp", "root_path": "", "query_string": b"",
                 "headers": [(b"host", b"localhost")], "client": ("203.0.113.7", 5000), "server": ("localhost", 80)}
        await app(scope, receive, send)
        headers = dict(sent[0]["headers"])
        assert sent[0]["status"] == 400 and headers[b"x-ratelimit-remaining"] == b"99"

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
        deadlines = []

        class Watched(server.RateLimitMiddleware):
            async def _peek_body(self, receive, deadline, headers):
                deadlines.append(deadline)
                return await super()._peek_body(receive, deadline, headers)

        # The fixture's 8 queued jobs reach these thresholds (the configured 12 wouldn't)
        app = mcp.http_app(path="/mcp", stateless_http=True,
                           middleware=[Middleware(server.BodySizeLimitMiddleware),
                                       Middleware(Watched, clock=busy.clock, wall_clock=busy.clock,
                                                  busy_max_waiting=8, busy_max_wait=0.25, busy_body_timeout=60)])
        async with app.router.lifespan_context(app):
            async with client(app) as c:
                reply = await c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                     "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                                "clientInfo": {"name": "test", "version": "1"}}},
                                     headers={"Accept": "application/json, text/event-stream"})
        assert reply.status_code == 200 and reply.headers["content-type"].startswith("text/event-stream")
        assert '"name":"busy-test"' in reply.text
        assert deadlines == [60]  # read under pressure, then replayed

    async def test_simultaneous_burst_is_bounded(self, busy):
        """Calls admitted but not started yet count: a burst that arrives at once can't all pass
        the check before any of it is queued (each was admitted on an empty queue before 0.10.0's
        reservations)."""
        for token in busy.tokens:
            busy.pressure.discard(busy.pool, token)  # a healthy server
        inside, release = [], asyncio.Event()
        three_in = asyncio.Event()

        async def held(request):
            body = await request.body()
            if json.loads(body)["method"] == "tools/call":
                inside.append(1)
                if len(inside) == 3:
                    three_in.set()
                await release.wait()  # admitted, not started: as between admission and the tool's first run_db
            return Response(body, media_type="application/json")

        app = Starlette(routes=[Route("/mcp", held, methods=["POST"])],
                        middleware=[Middleware(server.BodySizeLimitMiddleware),
                                    Middleware(server.RateLimitMiddleware, clock=busy.clock, wall_clock=busy.clock,
                                               busy_max_waiting=3, busy_max_wait=0.25, busy_body_timeout=60)])
        async with client(app) as c:
            first = [asyncio.create_task(c.post("/mcp", json=CALL, headers={"X-Forwarded-For": f"203.0.113.{n}"}))
                     for n in range(3)]
            await asyncio.wait_for(three_in.wait(), 30)
            assert busy.pressure.reserved == 3
            late = [await asyncio.wait_for(c.post("/mcp", json=CALL, headers={"X-Forwarded-For": f"198.51.100.{n}"}), 30)
                    for n in range(2)]
            assert [r.json()["reason"] for r in late] == ["server_busy", "server_busy"]
            cheap = await c.post("/mcp", json={"jsonrpc": "2.0", "id": 9, "method": "tools/list"})
            assert cheap.status_code == 200  # other methods still pass
            release.set()
            assert [(await task).status_code for task in first] == [200] * 3
        assert busy.pressure.reserved == 0  # released as each request ended

    async def test_reservation_released_as_the_tool_starts(self, busy):
        """AdmittedCallMiddleware releases a call's reservation as its tool starts, so a live
        lookup waiting on the network never holds one: four in flight, with room for two."""
        assert any(isinstance(m, server.AdmittedCallMiddleware) for m in server.mcp.middleware)
        for token in busy.tokens:
            busy.pressure.discard(busy.pool, token)
        entered = [asyncio.Event() for _ in range(4)]
        release = asyncio.Event()
        mcp = FastMCP("reserve-test")
        mcp.add_middleware(server.AdmittedCallMiddleware())

        @mcp.tool
        async def lookup(n: int) -> str:
            entered[n].set()
            await release.wait()  # a network wait
            return "done"

        app = mcp.http_app(path="/mcp", stateless_http=True,
                           middleware=[Middleware(server.BodySizeLimitMiddleware),
                                       Middleware(server.RateLimitMiddleware, clock=busy.clock, wall_clock=busy.clock,
                                                  busy_max_waiting=2, busy_max_wait=0.25, busy_body_timeout=60)])
        headers = {"Accept": "application/json, text/event-stream"}
        async with app.router.lifespan_context(app):
            async with client(app) as c:
                tasks = []
                for n in range(4):
                    call = {**CALL, "params": {"name": "lookup", "arguments": {"n": n}}}
                    tasks.append(asyncio.create_task(c.post("/mcp", json=call, headers=headers)))
                    await asyncio.wait_for(entered[n].wait(), 30)
                    assert busy.pressure.reserved == 0
                release.set()
                replies = await asyncio.gather(*tasks)
        assert [r.status_code for r in replies] == [200] * 4
        assert all('"done"' in r.text for r in replies)

    async def test_body_charged_before_it_is_read(self, busy):
        """Under pressure, one address's concurrent bodies are bounded by its allowance: each POST
        is charged before its body is read (a dry run let them all buffer at once)."""
        started, stall = [], asyncio.Event()

        def body(n):
            async def chunks():
                started.append(n)
                yield b'{"jsonrpc":"2.0",'
                await stall.wait()
                yield json.dumps(CALL)[1:].encode()
            return chunks()

        async with client(app_for(busy, requests_per_minute=2)) as c:
            tasks = [asyncio.create_task(c.post("/mcp", content=body(n))) for n in range(3)]
            done, _ = await asyncio.wait(tasks, timeout=30, return_when=asyncio.FIRST_COMPLETED)
            assert [task.result().json()["reason"] for task in done] == ["per_ip_rate_limit"]
            assert len(started) == 2
            stall.set()
            replies = await asyncio.gather(*tasks)
        assert sorted(r.json()["reason"] for r in replies) == ["per_ip_rate_limit", "server_busy", "server_busy"]
        assert busy.usage.summary()["days"][0]["per_ip_refusals"]["server_busy"] == 2  # charged once each

    async def test_chunked_body_limited_without_pressure(self, busy):
        """A body with no Content-Length is counted as it arrives even when the server isn't busy
        (before 0.10.0 only a declared length was checked then)."""
        for token in busy.tokens:
            busy.pressure.discard(busy.pool, token)
        read = []

        async def chunks():
            for n in range(3):
                read.append(n)
                yield b"x" * 600_000

        async with client(app_for(busy)) as c:
            reply = await c.post("/mcp", content=chunks())
        assert reply.status_code == 413 and reply.json() == {"error": "Request body too large"}
        assert read == [0, 1]  # not read past the limit
        assert reply.headers["x-ratelimit-remaining"] == "99"  # charged, and says so

    @pytest.mark.parametrize("sizes,status", [((600, 300), 200), ((600, 600), 413)], ids=["under", "over"])
    async def test_body_guard_counts_streamed_bytes(self, sizes, status):
        """BodySizeLimitMiddleware on its own: any route's chunked body is held to the limit."""
        app = Starlette(routes=[Route("/upload", echo, methods=["POST"])],
                        middleware=[Middleware(server.BodySizeLimitMiddleware, max_bytes=1000)])

        async def chunks():
            for size in sizes:
                yield b"x" * size

        async with client(app) as c:
            reply = await c.post("/upload", content=chunks())
        assert reply.status_code == status
        assert len(reply.content) == sum(sizes) if status == 200 else reply.json() == {"error": "Request body too large"}

    async def test_health_shows_pressure_and_fails_only_when_stuck(self, busy):
        """/health shows the pools' pressure, and answers 503 once a job has waited
        DB_STUCK_WAIT_SECONDS to start (a stuck worker), so the container's healthcheck fails; a
        busy spike's waits are far below that."""
        assert config.DB_STUCK_WAIT_SECONDS >= 100 * config.DB_BUSY_MAX_WAIT_SECONDS
        async with client(server.create_app()) as c:
            reply = await c.get("/health")
            assert reply.status_code == 200 and reply.json()["status"] == "healthy"
            assert reply.json()["database_pressure"] == {
                "waiting": 8, "oldest_wait_seconds": 0.0, "admitted_not_started": 0,
                "unhealthy_after_seconds": config.DB_STUCK_WAIT_SECONDS}
            busy.clock.advance(config.DB_STUCK_WAIT_SECONDS - 1)  # far past any spike: still healthy
            assert (await c.get("/health")).status_code == 200
            busy.clock.advance(1)
            stuck = await c.get("/health")
            assert stuck.status_code == 503
            assert stuck.json()["status"] == "unhealthy" and "stuck worker" in stuck.json()["problem"]
            assert stuck.json()["version"]  # the rest is still there
            for token in busy.tokens:
                busy.pressure.discard(busy.pool, token)
            assert (await c.get("/health")).json()["status"] == "healthy"


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

    def test_a_busy_but_moving_queue_never_exits(self, stuck):
        token = stuck.pressure.enqueue(stuck.pool)
        stuck.clock.advance(server.DB_STUCK_WAIT_SECONDS - 1)
        assert server._exit_if_stuck(5) == 0 and stuck.exits == []
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
