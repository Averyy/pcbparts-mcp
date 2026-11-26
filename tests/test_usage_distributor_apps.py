"""0.10.2: /mcp/stats distributor_apps, the calls to the Mouser and DigiKey tools by app, and the
in-memory map (server.AppsByAddress) that links a stateless server's tool calls to the app each
address last connected with. No network: httpx.MockTransport and fake clocks."""

import asyncio
import json

import httpx
import pytest

from pcbparts_mcp import server, stats
from pcbparts_mcp.cache import DailyQuota
from pcbparts_mcp.platform_ranges import PlatformRanges
from pcbparts_mcp.server import AppsByAddress
from pcbparts_mcp.stats import MAX_APPS, UsageStats

from test_usage_stats import PRODUCT, Clock, FakeDigiKey, digikey


def by_app(usage: UsageStats, day: int = 0) -> dict | None:
    return usage.summary()["days"][day]["distributor_apps"]


class TestCounts:
    def test_calls_and_rate_limited_per_tool_and_app(self):
        usage = UsageStats(clock=Clock())
        for tool, outcome, app in (("digikey_get_part", "ok", "backplane-check"),
                                   ("digikey_get_part", "rate_limited", "backplane-check"),
                                   ("digikey_get_part", "rate_limited", "backplane-check"),
                                   ("digikey_get_part", "ok", "claude-ai"),
                                   ("digikey_get_part", "not_found", None),  # no app known
                                   ("mouser_get_part", "rate_limited", "cursor"),
                                   ("part_lifecycle", "failed", "<b>odd</b>"),
                                   ("jlc_search", "ok", "cursor")):  # not a distributor tool
            usage.record_call(tool, outcome, 1, app=app)
        assert by_app(usage) == {
            "mouser_get_part": {"cursor": {"calls": 1, "rate_limited": 1}},
            "digikey_get_part": {"backplane-check": {"calls": 3, "rate_limited": 2},
                                 "claude-ai": {"calls": 1, "rate_limited": 0},
                                 "unknown": {"calls": 1, "rate_limited": 0}},
            "part_lifecycle": {"bodd/b": {"calls": 1, "rate_limited": 0}}}  # cleaned as in apps
        assert list(by_app(usage)["digikey_get_part"]) == ["backplane-check", "claude-ai", "unknown"]
        day = usage.summary()["days"][0]
        for tool, apps in day["distributor_apps"].items():  # the apps add up to the tool's calls
            assert sum(c["calls"] for c in apps.values()) == day["tools"][tool]["calls"]
            assert sum(c["rate_limited"] for c in apps.values()) == day["tools"][tool]["rate_limited"]
        assert "distributor_apps" in usage.summary()["about"]

    def test_names_are_capped_per_tool(self):
        usage = UsageStats(clock=Clock())
        for i in range(MAX_APPS):
            usage.record_call("digikey_get_part", "ok", 1, app=f"app{i}")
        usage.record_call("digikey_get_part", "rate_limited", 1, app="one more")
        usage.record_call("digikey_get_part", "ok", 1, app="app0")  # a name already counted still is
        usage.record_call("mouser_get_part", "ok", 1, app="one more")  # each tool has its own cap
        apps = by_app(usage)["digikey_get_part"]
        assert apps["other"] == {"calls": 1, "rate_limited": 1} and "one more" not in apps
        assert apps["app0"]["calls"] == 2 and len(apps) == MAX_APPS + 1
        assert by_app(usage)["mouser_get_part"] == {"one more": {"calls": 1, "rate_limited": 0}}
        assert all(len(name) <= stats.APP_NAME_LENGTH for name in apps)

    def test_totals_add_up_the_days(self):
        clock = Clock()
        usage = UsageStats(clock=clock)
        for outcome in ("ok", "rate_limited"):
            usage.record_call("digikey_get_part", outcome, 1, app="cursor")
            usage.record_call("part_lifecycle", "ok", 1)
            clock.advance(86400)
        totals = usage.summary()["totals"]["distributor_apps"]
        assert totals == {"digikey_get_part": {"cursor": {"calls": 2, "rate_limited": 1}},
                          "part_lifecycle": {"unknown": {"calls": 2, "rate_limited": 0}}}

    def test_days_before_are_null_and_it_survives_a_save(self, tmp_path):
        path, clock = tmp_path / "usage.json", Clock()
        path.write_text(json.dumps({"days": {"2026-10-16": {"callers": 3}, "2026-10-17": {"callers": 1}}}),
                        encoding="utf-8")
        usage = UsageStats(clock=clock)
        usage.open(path)
        assert [day["distributor_apps"] for day in usage.summary()["days"]] == [None, None]
        assert usage.summary()["totals"]["distributor_apps"] == {}
        usage.record_call("digikey_get_part", "rate_limited", 1, app="cursor")  # 2026-10-17: counts from now
        usage.record_call("jlc_search", "ok", 1, app="cursor")
        usage.save()
        saved = json.loads(path.read_text(encoding="utf-8"))["days"]
        assert saved["2026-10-16"]["distributor_apps"] is None
        assert saved["2026-10-17"]["distributor_apps"] == {
            "digikey_get_part": {"cursor": {"calls": 1, "rate_limited": 1}}}
        again = UsageStats(clock=clock)
        again.open(path)
        assert [day["distributor_apps"] for day in again.summary()["days"]] == [
            {"digikey_get_part": {"cursor": {"calls": 1, "rate_limited": 1}}}, None]
        again.record_call("digikey_get_part", "ok", 1, app="cursor")  # counting goes on from the saved counts
        assert by_app(again)["digikey_get_part"]["cursor"] == {"calls": 2, "rate_limited": 1}

    @pytest.mark.parametrize("value", ["x", [1], 5, True])
    def test_not_a_dict_is_null(self, tmp_path, value):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-10-17": {"distributor_apps": value}}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(path)
        assert by_app(usage) is None
        usage.record_call("mouser_get_part", "ok", 1, app="cursor")
        assert by_app(usage) == {"mouser_get_part": {"cursor": {"calls": 1, "rate_limited": 0}}}

    def test_malformed_values_are_dropped(self, tmp_path):
        """Never stops the server starting: anything malformed in the field is dropped or read as 0,
        and the rest of the file is kept."""
        path = tmp_path / "usage.json"
        day = ('{"callers": 2, "distributor_apps": {"digikey_get_part": [1], "jlc_search": {"a": {"calls": 1}}, '
               '"mouser_get_part": {"a": "x", "b": {"calls": "2", "rate_limited": 1e309}, "c": {"calls": 3, "x": 1}}, '
               '"part_lifecycle": {"d": {"calls": NaN, "rate_limited": 1' + "0" * 400 + '}}}}')
        path.write_text('{"days": {"2026-10-17": ' + day + '}}', encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(path)
        assert by_app(usage) == {"mouser_get_part": {"c": {"calls": 3, "rate_limited": 0},
                                                     "b": {"calls": 0, "rate_limited": 0}},
                                 "part_lifecycle": {"d": {"calls": 0, "rate_limited": 0}}}
        assert usage.summary()["days"][0]["callers"] == 2
        assert path.exists() and not (tmp_path / "usage.json.corrupt").exists()
        usage.record_call("digikey_get_part", "ok", 1, app="b")  # counting works on top of the cleaned day
        usage.record_call("mouser_get_part", "ok", 1, app="b")
        assert by_app(usage)["mouser_get_part"]["b"]["calls"] == 1
        assert by_app(usage)["digikey_get_part"] == {"b": {"calls": 1, "rate_limited": 0}}


class TestAppsByAddress:
    def test_links_an_address_to_its_last_app(self):
        apps = AppsByAddress(clock=Clock())
        apps.remember("203.0.113.9", "cursor")
        apps.remember("198.51.100.7", "claude-ai")
        assert apps.app_for("203.0.113.9") == "cursor" and apps.app_for("198.51.100.7") == "claude-ai"
        apps.remember("203.0.113.9", "backplane-check")  # the last initialize wins
        assert apps.app_for("203.0.113.9") == "backplane-check"
        assert apps.app_for("192.0.2.1") is None  # never connected
        apps.remember(None, "stdio")  # no address (not over HTTP): nothing to link
        assert apps.app_for(None) is None and len(apps) == 2

    def test_keyed_like_the_rate_limit(self):
        """IPv6 by its /64 (an address that rotates within it stays linked), an IPv4-mapped address
        as its IPv4 address."""
        apps = AppsByAddress(clock=Clock())
        apps.remember("2001:db8::1", "cursor")
        apps.remember("::ffff:203.0.113.9", "claude-ai")
        assert apps.app_for("2001:db8::abcd") == "cursor"
        assert apps.app_for("2001:db8:0:1::1") is None  # another /64
        assert apps.app_for("203.0.113.9") == "claude-ai"
        limiter = server.RateLimitMiddleware(None, platform_addresses=PlatformRanges())
        for ip in ("2001:db8::1", "::ffff:203.0.113.9", "203.0.113.9", "unknown"):
            assert server._address_key(ip) == limiter._limit_key(ip)

    def test_names_are_cleaned(self):
        apps = AppsByAddress(clock=Clock())
        apps.remember("203.0.113.9", '<img src=x onerror="alert(1)">' + "x" * 1000)
        apps.remember("198.51.100.7", None)
        name = apps.app_for("203.0.113.9")
        assert len(name) <= stats.APP_NAME_LENGTH and "<" not in name and '"' not in name
        assert apps.app_for("198.51.100.7") == "unknown"

    def test_an_entry_lasts_its_lifetime_from_last_use(self):
        clock = Clock()
        apps = AppsByAddress(lifetime=600, clock=clock)
        assert apps.lifetime == stats.APP_LINK_MINUTES * 60 == AppsByAddress().lifetime == 600
        apps.remember("203.0.113.9", "cursor")
        clock.advance(599)
        assert apps.app_for("203.0.113.9") == "cursor"  # a call keeps it for another lifetime
        clock.advance(599)
        assert apps.app_for("203.0.113.9") == "cursor"
        clock.advance(600)  # quiet for a lifetime: gone
        assert apps.app_for("203.0.113.9") is None
        apps.remember("198.51.100.7", "claude-ai")
        assert len(apps) == 1  # the stale entry was dropped, not kept

    def test_stale_entries_are_dropped_as_others_are_used(self):
        clock = Clock()
        apps = AppsByAddress(lifetime=600, clock=clock)
        for i in range(5):
            apps.remember(f"203.0.113.{i}", "cursor")
        clock.advance(300)
        apps.remember("198.51.100.7", "claude-ai")
        clock.advance(300)
        apps.remember("198.51.100.8", "claude-ai")  # the five are a lifetime old
        assert len(apps) == 2
        assert apps.app_for("198.51.100.7") == "claude-ai"
        clock.advance(600)
        assert apps.app_for("192.0.2.1") is None and len(apps) == 0  # a miss drops them too
        apps.remember("198.51.100.9", "cursor")
        clock.advance(600)
        apps.expire()  # the server's minute task: none outlives its lifetime when no request comes
        assert len(apps) == 0

    def test_size_is_bounded_dropping_the_least_recently_used(self):
        clock = Clock()
        apps = AppsByAddress(max_size=3, clock=clock)
        for i in range(3):
            apps.remember(f"203.0.113.{i}", f"app{i}")
            clock.advance(1)
        assert apps.app_for("203.0.113.0") == "app0"  # used: now the most recent
        apps.remember("203.0.113.3", "app3")
        assert len(apps) == 3
        assert apps.app_for("203.0.113.1") is None  # the least recently used went
        assert [apps.app_for(f"203.0.113.{i}") for i in (0, 2, 3)] == ["app0", "app2", "app3"]
        for i in range(1000):
            apps.remember(f"2001:db8:{i:x}::1", "flood")
        assert len(apps) == 3
        assert AppsByAddress().max_size == 10_000

    async def test_the_minute_task_drops_expired_links(self, monkeypatch):
        clock = Clock()
        apps = AppsByAddress(clock=clock)
        apps.remember("203.0.113.9", "cursor")
        clock.advance(apps.lifetime)
        monkeypatch.setattr(server, "_apps_by_address", apps)
        real_sleep, slept = asyncio.sleep, []

        async def one_minute(seconds):
            slept.append(seconds)
            await real_sleep(0)

        monkeypatch.setattr(server.asyncio, "sleep", one_minute)
        task = asyncio.ensure_future(server._every_minute())
        while len(apps) and len(slept) < 5:
            await real_sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert len(apps) == 0


class TestServerWiring:
    @pytest.fixture(autouse=True)
    def _fixed_clocks(self, monkeypatch):
        """One UTC day for the counts and no expiry for the links, whatever the real time."""
        monkeypatch.setattr(stats, "usage", UsageStats(clock=Clock()))
        monkeypatch.setattr(server, "_apps_by_address", AppsByAddress(clock=Clock()))

    async def test_stateless_http_links_calls_to_apps(self, monkeypatch, stats_headers):
        """The real ASGI app, stateless as on prod: a tools/call carries no clientInfo (its session
        has none), so the app comes from the initialize its address sent before. Two addresses
        with different apps don't mix; an address with no initialize counts under unknown."""
        headers = {"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-06-18"}
        sessions = []
        real_call_app = server._call_app

        def spy(context, caller):
            sessions.append(context.fastmcp_context.session.client_params)
            return real_call_app(context, caller)

        monkeypatch.setattr(server, "_call_app", spy)

        async def rpc(c, method, params, ip):
            return await c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                                headers={**headers, "X-Forwarded-For": ip})

        async def initialize(c, app, ip):
            response = await rpc(c, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                   "clientInfo": {"name": app, "version": "1"}}, ip)
            assert response.status_code == 200 and "mcp-session-id" not in response.headers  # stateless

        async def call(c, tool, arguments, ip):
            assert (await rpc(c, "tools/call", {"name": tool, "arguments": arguments}, ip)).status_code == 200

        app = server.create_app()
        async with app.router.lifespan_context(app):
            # Install the mock DigiKey client after startup has configured the providers.
            monkeypatch.setattr(server, "_digikey_client",
                                digikey(FakeDigiKey(httpx.Response(200, json=PRODUCT)), DailyQuota("DigiKey", 1)))
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as c:
                await initialize(c, "backplane-check", "203.0.113.9")
                await initialize(c, "cursor", "198.51.100.7")
                await call(c, "digikey_get_part", {"part_number": "LM358P"}, "203.0.113.9")  # ok
                await call(c, "digikey_get_part", {"part_number": "NE555P"}, "203.0.113.9")  # day's limit spent
                await call(c, "mouser_get_part", {"part_number": "LM358P"}, "203.0.113.9")  # not configured
                await call(c, "digikey_get_part", {"part_number": "LM358P"}, "198.51.100.7")  # cached
                await call(c, "digikey_get_part", {"part_number": "LM358P"}, "192.0.2.1")  # no initialize
                await call(c, "get_design_rules", {"topic": "usb"}, "203.0.113.9")  # not a distributor tool
                response = await c.get("/mcp/stats", headers=stats_headers)
        assert sessions and all(params is None for params in sessions)  # FastMCP gives no app at call time
        body = response.json()
        day = body["days"][0]
        assert day["distributor_apps"] == {
            "mouser_get_part": {"backplane-check": {"calls": 1, "rate_limited": 0}},
            "digikey_get_part": {"backplane-check": {"calls": 2, "rate_limited": 1},
                                 "cursor": {"calls": 1, "rate_limited": 0},
                                 "unknown": {"calls": 1, "rate_limited": 0}}}
        assert day["tools"]["digikey_get_part"]["rate_limited"] == 1 and day["tools"]["digikey_get_part"]["calls"] == 4
        assert day["apps"] == {"backplane-check": 1, "cursor": 1}
        assert body["totals"]["distributor_apps"] == day["distributor_apps"]
        assert "distributor_apps" in body["about"]
        for ip in ("203.0.113", "198.51.100", "192.0.2"):  # only app names and counts
            assert ip not in response.text

    async def test_a_session_with_client_info_names_its_own_app(self):
        """Over stdio or another stateful session the session's own clientInfo names the app."""
        from fastmcp import Client
        async with Client(server.mcp) as client:
            await client.call_tool("digikey_get_part", {"part_number": "LM358P"})  # not configured: failed
        day = stats.usage.summary()["days"][0]
        assert list(day["distributor_apps"]["digikey_get_part"]) == list(day["apps"]) != ["unknown"]

    async def test_counting_never_breaks_a_call(self, monkeypatch):
        """A map that fails doesn't stop initialize or the call; the call still counts, under unknown."""
        class Broken:
            def remember(self, *args):
                raise RuntimeError("boom")

            app_for = remember

        monkeypatch.setattr(server, "_apps_by_address", Broken())
        app = server.create_app()
        headers = {"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-06-18",
                   "X-Forwarded-For": "203.0.113.9"}
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as c:
                for method, params in (("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                       "clientInfo": {"name": "cursor", "version": "1"}}),
                                       ("tools/call", {"name": "digikey_get_part",
                                                       "arguments": {"part_number": "LM358P"}})):
                    response = await c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": method,
                                                          "params": params}, headers=headers)
                    assert response.status_code == 200 and "result" in response.text
        day = stats.usage.summary()["days"][0]
        assert day["apps"] == {"cursor": 1}
        assert day["distributor_apps"] == {"digikey_get_part": {"unknown": {"calls": 1, "rate_limited": 0}}}
