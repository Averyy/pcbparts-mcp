"""The per-IP rate limit's machine-readable replies (0.10.0): X-RateLimit-Limit/Remaining/Reset on
every reply, a Retry-After counted from the rolling window instead of a fixed 60, and 429 bodies
with reason, resets_at and tell_user next to the retry_after clients already read. No network:
ASGI test clients and a fake clock."""

import asyncio
import datetime
import json
from pathlib import Path

import httpx
import pytest
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse, StreamingResponse
from starlette.routing import Route

from pcbparts_mcp import server
from pcbparts_mcp.cache import SELF_HOSTING_URL, CallerTally
from pcbparts_mcp.db_worker import DatabasePressure

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 18, 20, 5, tzinfo=UTC).timestamp()
A, B, C = "203.0.113.7", "198.51.100.1", "192.0.2.9"


class Clock:
    def __init__(self, now: float = NOW):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture(autouse=True)
def tally(monkeypatch):
    """Refusals go to a fresh hourly tally, not the server's."""
    tally = CallerTally("Per-IP rate limit", Clock(), what="refusals")
    monkeypatch.setattr(server, "_refused_callers", tally)
    return tally


@pytest.fixture
def clock():
    return Clock()


async def _ok(request):
    return PlainTextResponse("ok")


def app_with(limit: int, clock: Clock, cls=server.RateLimitMiddleware) -> Starlette:
    routes = [Route("/mcp", _ok, methods=["POST"]), Route("/health", _ok), Route("/mcp/stats", _ok)]
    return Starlette(routes=routes, middleware=[Middleware(cls, requests_per_minute=limit, clock=clock)])


def client(app) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost")


def limits(reply: httpx.Response) -> tuple[str | None, ...]:
    return tuple(reply.headers.get(f"x-ratelimit-{name}") for name in ("limit", "remaining", "reset"))


def post(c: httpx.AsyncClient, ip: str = A):
    return c.post("/mcp", headers={"X-Forwarded-For": ip})


class TestHeaders:
    async def test_rolling_window(self, clock):
        async with client(app_with(3, clock)) as c:
            replies = [await post(c)]
            clock.advance(10)
            replies.append(await post(c))
            clock.advance(15)
            replies.append(await post(c))
            assert [limits(r) for r in replies] == [("3", "2", "60"), ("3", "1", "50"), ("3", "0", "35")]
            clock.advance(5)  # 30 s after the first request
            refused = await post(c)
            assert refused.status_code == 429
            assert limits(refused) == ("3", "0", "30")
            assert refused.headers["retry-after"] == "30"
            assert refused.json() == {
                "error": "Rate limit exceeded",
                "retry_after": 30,
                "reason": "per_ip_rate_limit",
                "resets_at": "2026-11-18T20:06:00Z",
                "tell_user": "pcbparts allows 3 requests a minute per address; try again in 30 seconds, "
                             f"or run your own copy for heavy use: {SELF_HOSTING_URL}",
            }
            clock.advance(29)
            assert (await post(c)).json()["retry_after"] == 1
            clock.advance(1)  # the first request has left the window; refusals weren't counted
            allowed = await post(c)
            assert allowed.status_code == 200
            assert limits(allowed) == ("3", "0", "10")  # the 10 s request is next to leave

    async def test_fractions_round_up(self, clock):
        clock.advance(0.25)
        async with client(app_with(1, clock)) as c:
            assert limits(await post(c)) == ("1", "0", "60")
            clock.advance(59.75)  # 0.25 s left in the window
            refused = await post(c)
            body = refused.json()
            assert (refused.headers["retry-after"], body["retry_after"]) == ("1", 1)  # never 0
            assert body["resets_at"] == "2026-11-18T20:06:01Z"  # rounded up, never early
            assert "pcbparts allows 1 request a minute per address; try again in 1 second," in body["tell_user"]
            clock.advance(1)
            assert (await post(c)).status_code == 200

    async def test_addresses_counted_apart(self, clock):
        async with client(app_with(2, clock)) as c:
            assert [(await post(c, A)).status_code for _ in range(3)] == [200, 200, 429]
            assert limits(await post(c, B)) == ("2", "1", "60")
            # X-Forwarded-For's rightmost address is the caller (set by our proxy)
            assert limits(await post(c, f"{A}, {B}")) == ("2", "0", "60")

    async def test_health_not_counted(self, clock):
        async with client(app_with(2, clock)) as c:
            for _ in range(5):
                health = await c.get("/health", headers={"X-Forwarded-For": A})
                assert (health.status_code, limits(health)) == (200, ("2", "2", "0"))
            await post(c)
            clock.advance(20)
            await post(c)
            assert (await post(c)).status_code == 429
            health = await c.get("/health", headers={"X-Forwarded-For": A})
            assert (health.status_code, limits(health)) == (200, ("2", "0", "40"))
            stats_reply = await c.get("/mcp/stats", headers={"X-Forwarded-For": B})
            assert limits(stats_reply) == ("2", "1", "60")  # stats counts, as before 0.10.0

    async def test_stats_is_limited_per_address(self, clock):
        """/mcp/stats had main's 100 a minute per address; only the busy check passes it by."""
        async with client(app_with(2, clock)) as c:
            assert [(await c.get("/mcp/stats", headers={"X-Forwarded-For": A})).status_code
                    for _ in range(3)] == [200, 200, 429]
            assert (await post(c, A)).status_code == 429  # one allowance for every path
            assert (await c.get("/health", headers={"X-Forwarded-For": A})).status_code == 200

    async def test_limit_for_sets_everything(self, clock):
        class PerAddress(server.RateLimitMiddleware):
            def _limit_for(self, client_ip):
                return 5 if client_ip == A else 2

        async with client(app_with(100, clock, PerAddress)) as c:
            assert limits(await post(c, A)) == ("5", "4", "60")
            assert [(await post(c, B)).status_code for _ in range(3)] == [200, 200, 429]
            refused = await post(c, B)
            assert limits(refused) == ("2", "0", "60")
            assert "allows 2 requests a minute" in refused.json()["tell_user"]
            assert [(await post(c, A)).status_code for _ in range(5)] == [200] * 4 + [429]

    def test_reasons_documented(self):
        llms = (Path(__file__).parent.parent / "landing" / "llms.txt").read_text(encoding="utf-8")
        for reason in server.RATE_LIMIT_REASONS:
            assert f"`{reason}`" in llms


class TestTooManyClients:
    async def test_new_addresses_wait(self, clock, tally, monkeypatch):
        monkeypatch.setattr(server.RateLimitMiddleware, "MAX_TRACKED_IPS", 2)
        async with client(app_with(10, clock)) as c:
            assert (await post(c, A)).status_code == 200
            clock.advance(10)
            assert (await post(c, B)).status_code == 200
            clock.advance(10)
            refused = await post(c, C)
            assert refused.status_code == 429
            assert limits(refused) == ("10", "0", "40")  # A's request leaves the window first
            body = refused.json()
            assert (body["retry_after"], body["reason"]) == (40, "too_many_clients")
            assert body["tell_user"] == "pcbparts is serving too many addresses at once; try again in 40 seconds."
            # Addresses already tracked carry on
            assert limits(await post(c, A)) == ("10", "8", "40")
            assert (await post(c, C)).json()["retry_after"] == 50  # now B leaves first
            clock.advance(50)  # B's last request is a minute old
            assert limits(await post(c, C)) == ("10", "9", "60")
        assert sum(tally._counts.values()) == 2


class TestRealApp:
    async def test_health_and_stats(self):
        async with client(server.create_app()) as c:
            limit = str(server.RATE_LIMIT_REQUESTS)
            health = await c.get("/health", headers={"X-Forwarded-For": A})
            assert (health.status_code, limits(health)) == (200, (limit, limit, "0"))
            usage = await c.get("/mcp/stats", headers={"X-Forwarded-For": A})
            assert usage.status_code == 200
            assert usage.headers["cache-control"] == "public, max-age=60"  # the route's own headers kept
            assert limits(usage)[:2] == (limit, str(server.RATE_LIMIT_REQUESTS - 1))  # counted

    async def test_mcp_stream(self, clock):
        """A real streamable-HTTP MCP reply (SSE) carries the headers and arrives whole."""
        mcp = FastMCP("t")

        @mcp.tool
        def ping() -> str:
            return "pong"

        app = mcp.http_app(path="/mcp", transport="streamable-http", stateless_http=True,
                           middleware=[Middleware(server.RateLimitMiddleware, requests_per_minute=5, clock=clock)])
        headers = {"Accept": "application/json, text/event-stream", "X-Forwarded-For": A}
        calls = [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                  "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                             "clientInfo": {"name": "test", "version": "1"}}},
                 {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "ping", "arguments": {}}}]
        async with app.router.lifespan_context(app):
            async with client(app) as c:
                replies = [await c.post("/mcp", json=call, headers=headers) for call in calls]
        for reply in replies:
            assert reply.status_code == 200
            assert reply.headers["content-type"].startswith("text/event-stream")
        assert [limits(r) for r in replies] == [("5", "4", "60"), ("5", "3", "60")]
        data = [[json.loads(line[len("data: "):]) for line in r.text.splitlines() if line.startswith("data: ")]
                for r in replies]
        assert data[0][0]["result"]["serverInfo"]["name"] == "t"
        assert data[1][0]["result"]["content"][0]["text"] == "pong"


@pytest.mark.parametrize("under_pressure", [False, True], ids=["healthy", "busy"])
async def test_stream_not_buffered(clock, under_pressure):
    """The headers go out with the reply's start and each body chunk is passed on as it comes, so
    an SSE stream isn't held back: the second event is made only once the first has left the
    middleware (buffering would hang until the guard below fails the test)."""
    first_out = asyncio.Event()

    async def events():
        yield b"event: message\ndata: 1\n\n"
        await first_out.wait()
        yield b"event: message\ndata: 2\n\n"

    async def sse(request):
        return StreamingResponse(events(), media_type="text/event-stream")

    pressure = DatabasePressure(clock)
    if under_pressure:
        for _ in range(8):
            pressure.enqueue(server.COMPONENT_POOL)
    app = Starlette(routes=[Route("/mcp", sse, methods=["POST"])],
                    middleware=[Middleware(server.BodySizeLimitMiddleware),  # prod's order
                                Middleware(server.RateLimitMiddleware, requests_per_minute=5, clock=clock,
                                           pressure=pressure)])
    sent = []

    async def send(message):
        sent.append(message)
        if message["type"] == "http.response.body" and message.get("body"):
            first_out.set()

    asked = False

    async def receive():
        nonlocal asked
        if not asked:
            asked = True
            return {"type": "http.request", "body": b'{"id":1,"method":"tools/list"}', "more_body": False}
        await asyncio.Event().wait()  # no disconnect; cancelled once the reply is done
        return {"type": "http.disconnect"}

    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "POST",
             "scheme": "http", "path": "/mcp", "raw_path": b"/mcp", "query_string": b"", "root_path": "",
             "headers": [(b"host", b"localhost"), (b"x-forwarded-for", A.encode())],
             "client": ("127.0.0.1", 50000), "server": ("localhost", 80)}
    await asyncio.wait_for(app(scope, receive, send), 30)
    start = sent[0]
    assert start["type"] == "http.response.start"
    headers = {bytes(name): bytes(value) for name, value in start["headers"]}
    assert headers[b"content-type"].startswith(b"text/event-stream")
    assert (headers[b"x-ratelimit-limit"], headers[b"x-ratelimit-remaining"], headers[b"x-ratelimit-reset"]) == (
        b"5", b"4", b"60")
    assert [m["body"] for m in sent[1:] if m.get("body")] == [b"event: message\ndata: 1\n\n",
                                                             b"event: message\ndata: 2\n\n"]
