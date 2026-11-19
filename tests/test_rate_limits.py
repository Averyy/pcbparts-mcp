"""The per-IP rate limit's machine-readable replies (0.10.0): X-RateLimit-Limit/Remaining/Reset on
every reply, a Retry-After counted from the rolling window instead of a fixed 60, and 429 bodies
with reason, resets_at and tell_user next to the retry_after clients already read. No network:
ASGI test clients and a fake clock."""

import asyncio
import datetime
import ipaddress
import json
import logging
from pathlib import Path

import httpx
import pytest
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse, Response, StreamingResponse
from starlette.routing import Route

from pcbparts_mcp import server, stats
from pcbparts_mcp.cache import SELF_HOSTING_URL, CallerTally
from pcbparts_mcp.platform_ranges import PlatformRanges

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
    return Starlette(routes=routes, middleware=[Middleware(cls, requests_per_minute=limit, clock=clock,
                                                           wall_clock=clock)])


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
        """/mcp/stats has main's 100 a minute per address, one allowance with every other path."""
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
    async def test_new_addresses_wait(self, clock, tally, monkeypatch, caplog):
        monkeypatch.setattr(server.RateLimitMiddleware, "MAX_TRACKED_IPS", 2)
        usage = stats.UsageStats(clock=clock)
        monkeypatch.setattr(stats, "usage", usage)
        caplog.set_level(logging.WARNING, logger="pcbparts_mcp.server")
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
        # Their own group in /mcp/stats and one warning a minute, not the per-IP hourly line
        # (the refused addresses are new ones, so their tally says nothing)
        assert usage.summary()["days"][0]["per_ip_refusals"] == {
            "total": 2, "everyone_else": 0, "platform_ranges": 0, "server_busy": 0, "too_many_clients": 2}
        assert sum(tally._counts.values()) == 0
        warnings = [r.getMessage() for r in caplog.records if "too_many_clients" in r.getMessage()]
        assert len(warnings) == 1 and "1 refused since the last warning" in warnings[0]

    def test_warning_at_most_once_a_minute(self, clock, monkeypatch, caplog):
        monkeypatch.setattr(server.RateLimitMiddleware, "MAX_TRACKED_IPS", 1)
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        limiter = server.RateLimitMiddleware(None, requests_per_minute=10, clock=clock, wall_clock=clock,
                                             platform_addresses=PlatformRanges())
        limiter._allowance(A)
        caplog.set_level(logging.WARNING, logger="pcbparts_mcp.server")
        for n in range(5):
            clock.advance(10)
            limiter._allowance(A)  # A stays tracked, so the others stay out
            allowance = limiter._allowance(f"198.51.100.{n}")
            assert allowance.refused == "too_many_clients"
            limiter._count_refusal(f"198.51.100.{n}", allowance.refused)
        warnings = [r.getMessage() for r in caplog.records]
        assert len(warnings) == 1 and "1 refused since the last warning" in warnings[0]
        clock.advance(20)  # a minute after the first warning
        limiter._allowance(A)
        limiter._count_refusal(C, limiter._allowance(C).refused)
        assert len(caplog.records) == 2 and "5 refused since the last warning" in caplog.records[1].getMessage()

    def test_no_scan_of_every_address(self, clock, monkeypatch):
        """A refused new address costs O(1), not two passes over all 10,000 tracked addresses
        (request_counts is kept in order of last requests, so the stalest is first)."""
        class Counting(dict):
            seen = 0

            def items(self):
                for item in super().items():
                    Counting.seen += 1
                    yield item

            def values(self):
                for value in super().values():
                    Counting.seen += 1
                    yield value

        monkeypatch.setattr(server.RateLimitMiddleware, "MAX_TRACKED_IPS", 500)
        limiter = server.RateLimitMiddleware(None, requests_per_minute=10, clock=clock, wall_clock=clock,
                                             platform_addresses=PlatformRanges())
        limiter.request_counts = Counting()
        for n in range(500):
            limiter._allowance(f"10.0.{n // 256}.{n % 256}")
        Counting.seen = 0
        for n in range(100):
            assert limiter._allowance(f"10.9.0.{n}").refused == "too_many_clients"
        assert Counting.seen <= 2 * 100
        clock.advance(61)  # every tracked address is stale: dropped oldest first as needed
        assert limiter._allowance("10.9.1.1").refused is None
        assert limiter._allowance("10.0.0.0").refused is None


V6_A, V6_A2, V6_B = "2001:db8:1:2::1", "2001:db8:1:2:ffff:ffff:ffff:ffff", "2001:db8:1:3::1"


class TestIPv6:
    def test_one_allowance_per_slash_64(self, clock):
        limiter = server.RateLimitMiddleware(None, requests_per_minute=2, clock=clock, wall_clock=clock,
                                             platform_addresses=PlatformRanges())
        assert [limiter._allowance(ip).refused for ip in (V6_A, V6_A2, V6_A)] == [None, None, "per_ip_rate_limit"]
        assert limiter._allowance(V6_B).refused is None  # the next /64 is someone else
        assert list(limiter.request_counts) == ["2001:db8:1:2::/64", "2001:db8:1:3::/64"]
        # IPv4 by the full address; IPv4-mapped IPv6 is that IPv4 address
        assert [limiter._allowance(ip).refused for ip in ("192.0.2.1", "::ffff:192.0.2.1", "192.0.2.2")] == [
            None, None, None]
        assert limiter.request_counts["192.0.2.1"] == [clock.now, clock.now]
        assert limiter._limit_key("unknown") == "unknown"

    def test_platform_ipv6_counted_alone(self, clock):
        ranges = PlatformRanges({"openai": [ipaddress.ip_network("2001:db8:1:2::/64")]})
        limiter = server.RateLimitMiddleware(None, requests_per_minute=1, platform_per_minute=1, clock=clock,
                                             wall_clock=clock, platform_addresses=ranges)
        assert [limiter._allowance(ip).refused for ip in (V6_A, V6_A2)] == [None, None]

    async def test_one_slash_64_cant_fill_the_table(self, clock, monkeypatch):
        monkeypatch.setattr(server.RateLimitMiddleware, "MAX_TRACKED_IPS", 3)
        async with client(app_with(100, clock)) as c:
            replies = [await post(c, f"2001:db8:1:2::{n:x}") for n in range(50)]
            assert {r.status_code for r in replies} == {200}
            assert limits(replies[-1]) == ("100", "50", "60")  # one allowance for the /64
            assert (await post(c, A)).status_code == 200  # room for others
            refused = await post(c, V6_B)
            assert refused.status_code == 200
            assert (await post(c, B)).json()["reason"] == "too_many_clients"  # 3 tracked: A, two /64s


class TestClocks:
    async def test_window_ignores_wall_clock_steps(self):
        """The window runs on a monotonic clock: a wall-clock step back (an NTP correction) neither
        lengthens nor shortens a refusal; only resets_at follows the wall clock."""
        window, wall = Clock(1000.0), Clock()
        app = Starlette(routes=[Route("/mcp", _ok, methods=["POST"])],
                        middleware=[Middleware(server.RateLimitMiddleware, requests_per_minute=1, clock=window,
                                               wall_clock=wall)])
        async with client(app) as c:
            assert (await post(c)).status_code == 200
            window.advance(30)
            wall.advance(-3600)  # an hour back
            refused = await post(c)
            assert refused.json()["retry_after"] == 30
            assert refused.json()["resets_at"] == "2026-11-18T19:05:30Z"  # the wall clock's now + 30 s
            window.advance(30)
            assert (await post(c)).status_code == 200


class TestPlatformLimitFloor:
    def test_platform_never_below_normal(self, clock):
        """A self-hoster's RATE_LIMIT_REQUESTS above PLATFORM_RATE_LIMIT doesn't give the AI
        platforms' shared addresses less than everyone else."""
        ranges = PlatformRanges({"anthropic": [ipaddress.ip_network("160.79.104.0/21")]})
        limiter = server.RateLimitMiddleware(None, requests_per_minute=5000, platform_per_minute=1000,
                                             clock=clock, wall_clock=clock, platform_addresses=ranges)
        assert (limiter._limit_for("160.79.104.10"), limiter._limit_for(A)) == (5000, 5000)
        limiter.platform_per_minute = 9000
        assert (limiter._limit_for("160.79.104.10"), limiter._limit_for(A)) == (9000, 5000)


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


async def test_stream_not_buffered(clock):
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

    app = Starlette(routes=[Route("/mcp", sse, methods=["POST"])],
                    middleware=[Middleware(server.BodySizeLimitMiddleware),  # prod's order
                                Middleware(server.RateLimitMiddleware, requests_per_minute=5, clock=clock,
                                           wall_clock=clock)])
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


async def _echo(request):
    return Response(await request.body(), media_type="application/json")


def body_app(clock: Clock, limit: int = 100) -> Starlette:
    """prod's order: the body-size guard outside the rate limiter."""
    return Starlette(routes=[Route("/mcp", _echo, methods=["POST"])],
                     middleware=[Middleware(server.BodySizeLimitMiddleware),
                                 Middleware(server.RateLimitMiddleware, requests_per_minute=limit, clock=clock,
                                            wall_clock=clock)])


def raw_post(path: str = "/mcp", ip: str = A, headers: tuple = ()) -> dict:
    return {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "POST",
            "scheme": "http", "path": path, "raw_path": path.encode(), "root_path": "", "query_string": b"",
            "headers": [(b"host", b"localhost"), (b"content-type", b"application/json"), *headers],
            "client": (ip, 5000), "server": ("localhost", 80)}


class TestBodies:
    """The limiter charges a request as it starts and passes its body to the app untouched (from
    0.10.1; 0.10.0's busy cap read it first); BodySizeLimitMiddleware bounds it."""

    @pytest.mark.parametrize("raw", [b'{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{}}',
                                     b"not json", b"\xff", b"[" * 2000, b""],
                             ids=["call", "invalid", "utf8", "nested", "empty"])
    async def test_body_reaches_the_app_untouched(self, clock, raw):
        async with client(body_app(clock)) as c:
            reply = await c.post("/mcp", content=raw, headers={"X-Forwarded-For": A})
        assert reply.status_code == 200 and reply.content == raw
        assert limits(reply) == ("100", "99", "60")

    async def test_chunked_body_reaches_the_app_whole(self, clock):
        async def chunks():
            yield b'{"jsonrpc":"2.0",'
            yield b'"id":1,"method":"initialize"}'

        async with client(body_app(clock)) as c:
            reply = await c.post("/mcp", content=chunks())
        assert reply.status_code == 200 and reply.json() == {"jsonrpc": "2.0", "id": 1, "method": "initialize"}

    async def test_charged_before_the_body_is_read(self, clock):
        """One address's concurrent bodies are bounded by its allowance: each POST is charged as it
        starts, so the third of three slow bodies is refused without being read."""
        started, stall = [], asyncio.Event()

        def body(n):
            async def chunks():
                started.append(n)
                yield b'{"jsonrpc":"2.0",'
                await stall.wait()
                yield b'"id":1}'
            return chunks()

        async with client(body_app(clock, limit=2)) as c:
            tasks = [asyncio.create_task(c.post("/mcp", content=body(n))) for n in range(3)]
            done, _ = await asyncio.wait(tasks, timeout=30, return_when=asyncio.FIRST_COMPLETED)
            assert [task.result().json()["reason"] for task in done] == ["per_ip_rate_limit"]
            assert len(started) == 2
            stall.set()
            replies = await asyncio.gather(*tasks)
        assert sorted(r.status_code for r in replies) == [200, 200, 429]

    async def test_exhausted_address_refused_before_body_read(self, clock):
        async def chunks():
            pytest.fail("read a body from an exhausted address")
            yield b""

        async with client(body_app(clock, limit=1)) as c:
            assert (await c.post("/mcp", content=b"{}")).status_code == 200
            reply = await c.post("/mcp", content=chunks())
            assert reply.status_code == 429 and reply.json()["reason"] == "per_ip_rate_limit"

    @pytest.mark.parametrize("declared", [None, "1", "1000001"], ids=["chunked", "false", "large"])
    async def test_body_size_guard(self, clock, declared):
        read = []

        async def chunks():
            for n in range(3):
                read.append(n)
                yield b"x" * 600_000

        async with client(body_app(clock)) as c:
            reply = await c.post("/mcp", content=chunks(),
                                 headers={} if declared is None else {"Content-Length": declared})
        assert reply.status_code == 413 and reply.json() == {"error": "Request body too large"}
        # A declared size is refused before anything is read; any other body isn't read past the limit
        assert read == ([] if declared == "1000001" else [0, 1])

    @pytest.mark.parametrize("sizes,status", [((600, 300), 200), ((600, 600), 413)], ids=["under", "over"])
    async def test_body_guard_counts_streamed_bytes(self, sizes, status):
        """BodySizeLimitMiddleware on its own: any route's chunked body is held to the limit."""
        app = Starlette(routes=[Route("/upload", _echo, methods=["POST"])],
                        middleware=[Middleware(server.BodySizeLimitMiddleware, max_bytes=1000)])

        async def chunks():
            for size in sizes:
                yield b"x" * size

        async with client(app) as c:
            reply = await c.post("/upload", content=chunks())
        assert reply.status_code == status
        assert len(reply.content) == sum(sizes) if status == 200 else reply.json() == {"error": "Request body too large"}

    async def test_sdk_cut_off_and_disconnected_bodies(self, clock):
        """With the MCP SDK reading the body: a body cut off at the limit (chunked, or a false
        Content-Length) gets the 413 with the X-RateLimit headers of the SDK's own error reply (the
        request was charged); a declared size over it is refused before the limiter, uncharged. A
        client that leaves mid-body gets a reply too, charged as any request. The SDK logs those
        two as errors, as before 0.10.0."""
        mcp = FastMCP("t")

        @mcp.tool
        def ping() -> str:
            return "pong"

        app = mcp.http_app(path="/mcp", transport="streamable-http", stateless_http=True,
                           middleware=[Middleware(server.BodySizeLimitMiddleware),
                                       Middleware(server.RateLimitMiddleware, requests_per_minute=5, clock=clock,
                                                  wall_clock=clock)])
        headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json",
                   "X-Forwarded-For": A}

        async def chunks():
            for _ in range(3):
                yield b" " * 600_000

        async with app.router.lifespan_context(app):
            async with client(app) as c:
                chunked = await c.post("/mcp", content=chunks(), headers=headers)
                false_length = await c.post("/mcp", content=chunks(), headers={**headers, "Content-Length": "5"})
                declared = await c.post("/mcp", content=b" " * 1_000_001, headers=headers)
                call = await c.post("/mcp", headers=headers, json={
                    "jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "ping", "arguments": {}}})
            for reply in (chunked, false_length, declared):
                assert reply.status_code == 413 and reply.json() == {"error": "Request body too large"}
            assert [limits(r) for r in (chunked, false_length, declared)] == [
                ("5", "4", "60"), ("5", "3", "60"), (None, None, None)]
            assert call.status_code == 200 and '"pong"' in call.text and limits(call) == ("5", "2", "60")

            messages = [{"type": "http.request", "body": b'{"jsonrpc":', "more_body": True}, {"type": "http.disconnect"}]
            sent = []

            async def receive():
                return messages.pop(0) if messages else {"type": "http.disconnect"}

            async def send(message):
                sent.append(message)

            scope = raw_post(headers=((b"accept", b"application/json, text/event-stream"),
                                      (b"x-forwarded-for", A.encode())))
            await asyncio.wait_for(app(scope, receive, send), 30)
        assert sent[0]["type"] == "http.response.start"
        assert dict(sent[0]["headers"])[b"x-ratelimit-remaining"] == b"1"
