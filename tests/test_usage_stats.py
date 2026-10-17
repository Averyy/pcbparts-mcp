"""Anonymous usage counts for /mcp/stats, DigiKey request spacing, and cached DigiKey "not found" answers
(0.6.3). No network: httpx.MockTransport and fake clocks."""

import asyncio
import datetime
import json
import time

import httpx
import pytest

from pcbparts_mcp import stats
from pcbparts_mcp.cache import DailyQuota, Pacer, TTLCache
from pcbparts_mcp.digikey import DigiKeyClient
from pcbparts_mcp.mouser import MouserClient
from pcbparts_mcp.stats import KEEP_DAYS, MAX_APPS, PUBLIC_DAYS, UsageStats

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 10, 17, 21, 15, tzinfo=UTC).timestamp()

PRODUCT = {"Product": {"ManufacturerProductNumber": "LM358P", "ProductVariations": [], "Parameters": []}}


class Clock:
    def __init__(self, now: float = NOW):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class FakeDigiKey:
    def __init__(self, *responses: httpx.Response):
        self.responses = list(responses)
        self.product_requests = 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 599})
        self.product_requests += 1
        return self.responses.pop(0)


def digikey(fake: FakeDigiKey, quota: DailyQuota | None = None) -> DigiKeyClient:
    client = DigiKeyClient(client_id="id", client_secret="secret", quota=quota)
    client._http = httpx.AsyncClient(transport=httpx.MockTransport(fake))
    return client


class TestPacer:
    async def test_a_burst_waits_its_turn(self):
        clock, slept = Clock(), []

        async def sleep(seconds):
            slept.append(round(seconds, 6))

        pacer = Pacer(5, clock=clock, sleep=sleep)
        for _ in range(3):
            await pacer.wait()
        assert slept == [0.2, 0.4]  # the first goes at once, then one every 0.2 s

    async def test_concurrent_callers_get_distinct_slots(self):
        clock, slept = Clock(), []

        async def sleep(seconds):
            slept.append(round(seconds, 6))
            await asyncio.sleep(0)  # let the others in while this one waits

        pacer = Pacer(5, clock=clock, sleep=sleep)
        await asyncio.gather(*(pacer.wait() for _ in range(4)))
        assert sorted(slept) == [0.2, 0.4, 0.6]

    async def test_no_wait_once_the_gap_has_passed(self):
        clock, slept = Clock(), []

        async def sleep(seconds):
            slept.append(seconds)

        pacer = Pacer(5, clock=clock, sleep=sleep)
        await pacer.wait()
        clock.advance(0.5)
        await pacer.wait()
        assert slept == []

    async def test_digikey_requests_are_spaced(self):
        clock, slept = Clock(), []

        async def sleep(seconds):
            slept.append(round(seconds, 6))

        fake = FakeDigiKey(*(httpx.Response(200, json=PRODUCT) for _ in range(3)))
        client = digikey(fake)
        client._pacer = Pacer(5, clock=clock, sleep=sleep)
        for number in ("A1", "A2", "A3"):
            await client.get_part(number)
        assert fake.product_requests == 3
        assert slept == [0.2, 0.4]


class TestDigiKeyNotFound:
    async def test_404_is_a_cached_not_found(self):
        quota = DailyQuota("DigiKey", 1000)
        fake = FakeDigiKey(httpx.Response(404, json={"title": "Not Found", "status": 404}))
        client = digikey(fake, quota)
        first = await client.get_part("LM358")
        assert first == {"error": "Part not found: LM358"}
        assert await client.get_part(" LM358 ") == first
        assert fake.product_requests == 1  # the repeat cost no request
        assert quota.status()["used_today"] == 1

    async def test_not_found_is_kept_ten_minutes(self):
        fake = FakeDigiKey(httpx.Response(404), httpx.Response(200, json=PRODUCT))
        client = digikey(fake)
        assert "error" in await client.get_part("NOPE1")  # the 404
        assert "results" in await client.get_part("LM358P")
        left = {key: expires - time.time() for key, (expires, _) in client._cache._data.items()}
        assert 590 < left["digikey:NOPE1"] <= 600
        assert 3590 < left["digikey:LM358P"] <= 3600

    async def test_empty_product_is_a_cached_not_found(self):
        fake = FakeDigiKey(httpx.Response(200, json={"Product": {}}))
        client = digikey(fake)
        assert (await client.get_part("XYZ"))["error"] == "Part not found: XYZ"
        assert (await client.get_part("XYZ"))["error"] == "Part not found: XYZ"
        assert fake.product_requests == 1

    async def test_blank_number_sends_nothing(self):
        quota = DailyQuota("DigiKey", 1000)
        fake = FakeDigiKey()
        result = await digikey(fake, quota).get_part("   ")
        assert result == {"error": "Give a DigiKey or manufacturer part number."}
        assert fake.product_requests == 0 and quota.status()["used_today"] == 0


class TestTTLCacheTtl:
    def test_per_entry_ttl(self, monkeypatch):
        now = [1000.0]
        monkeypatch.setattr("pcbparts_mcp.cache.time.time", lambda: now[0])
        cache = TTLCache(ttl=3600)
        cache.set("long", 1)
        cache.set("short", 2, ttl=600)
        now[0] += 601
        assert cache.get("short") is None and cache.get("long") == 1
        now[0] += 3000
        assert cache.get("long") is None


class TestUsageStats:
    def test_counts_calls_by_outcome(self):
        usage = UsageStats(clock=Clock())
        usage.record_call("jlc_search", "ok", 40)
        usage.record_call("jlc_search", "empty", 20)
        usage.record_call("jlc_search", "error", 30)
        usage.record_call("board_get", "failed", 5)
        day = usage.summary()["days"][0]
        assert day["date"] == "2026-10-17" and day["calls"] == 4
        assert day["tools"]["jlc_search"] == {"calls": 3, "errors": 1, "failed": 0, "empty": 1, "avg_ms": 30}
        assert day["tools"]["board_get"]["failed"] == 1
        assert list(day["tools"]) == ["jlc_search", "board_get"]  # busiest first

    def test_names_that_arent_tools_count_as_unknown(self):
        usage = UsageStats(clock=Clock())
        usage.tools = {"jlc_search"}
        usage.record_call("jlc_search", "ok", 1)
        usage.record_call("<script>", "failed", 1)
        assert set(usage.summary()["days"][0]["tools"]) == {"jlc_search", "unknown"}

    def test_distinct_callers_without_keeping_ips(self, tmp_path):
        clock = Clock()
        usage = UsageStats(clock=clock)
        usage.open(tmp_path / "usage.json")
        for ip in ("203.0.113.7", "203.0.113.7", "198.51.100.2", None):
            usage.record_call("jlc_search", "ok", 1, caller=ip)
        assert usage.summary()["days"][0]["callers"] == 2
        usage.save()
        text = (tmp_path / "usage.json").read_text(encoding="utf-8")
        assert "203.0.113" not in text and "198.51.100" not in text
        clock.advance(86400)  # a new day counts afresh
        usage.record_call("jlc_search", "ok", 1, caller="203.0.113.7")
        assert [d["callers"] for d in usage.summary()["days"]] == [1, 2]

    def test_app_names_are_cleaned_and_capped(self):
        usage = UsageStats(clock=Clock())
        usage.record_app("claude-code")
        usage.record_app("claude-code")
        usage.record_app('<img src=x onerror="alert(1)">' + "x" * 100)
        usage.record_app(None)
        apps = usage.summary()["days"][0]["apps"]
        assert apps["claude-code"] == 2 and apps["unknown"] == 1
        odd = next(name for name in apps if name.startswith("img"))
        assert len(odd) <= 40 and "<" not in odd and '"' not in odd
        for i in range(MAX_APPS):
            usage.record_app(f"app{i}")
        assert usage.summary()["days"][0]["apps"]["other"] > 0

    def test_distributor_events(self):
        usage = UsageStats(clock=Clock())
        for event in ("sent", "sent", "cached", "limited"):
            usage.record_distributor("digikey", event)
        assert usage.summary()["days"][0]["distributors"] == {"digikey": {"sent": 2, "cached": 1, "limited": 1}}

    def test_counts_survive_a_restart(self, tmp_path):
        path, clock = tmp_path / "usage.json", Clock()
        usage = UsageStats(clock=clock)
        usage.open(path)
        usage.record_call("jlc_search", "ok", 10, caller="203.0.113.7")
        usage.record_app("cursor")
        usage.save()
        restarted = UsageStats(clock=clock)
        restarted.open(path)
        restarted.record_call("jlc_search", "ok", 30, caller="198.51.100.2")
        day = restarted.summary()["days"][0]
        assert day["tools"]["jlc_search"]["calls"] == 2 and day["tools"]["jlc_search"]["avg_ms"] == 20
        assert day["apps"] == {"cursor": 1} and day["callers"] == 2
        assert restarted.summary()["kept_across_restarts"] is True

    def test_unreadable_or_malformed_file_starts_from_zero(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(bad)
        assert usage.summary()["days"] == []
        odd = tmp_path / "odd.json"
        odd.write_text(json.dumps({"days": {"2026-10-17": {"tools": ["x"], "apps": {"a": "1"},
                                                          "distributors": {"mouser": {"sent": "2"}}}}}),
                       encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(odd)
        usage.record_call("jlc_search", "ok", 1)  # counting still works on top of the cleaned day
        usage.record_distributor("mouser", "sent")
        day = usage.summary()["days"][0]
        assert day["tools"]["jlc_search"]["calls"] == 1 and day["distributors"]["mouser"]["sent"] == 1

    def test_unwritable_file_keeps_counting_in_memory(self, tmp_path):
        blocker = tmp_path / "file"
        blocker.write_text("", encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(blocker / "usage.json")  # its parent is a file, so writes fail
        usage.record_call("jlc_search", "ok", 1)
        usage.save()
        assert usage.ok is False and usage.summary()["kept_across_restarts"] is False
        assert usage.summary()["days"][0]["calls"] == 1

    def test_keeps_only_recent_days(self):
        clock = Clock()
        usage = UsageStats(clock=clock)
        for _ in range(KEEP_DAYS + 5):
            usage.record_call("jlc_search", "ok", 1)
            clock.advance(86400)
        dates = [d["date"] for d in usage.summary(days=1000)["days"]]
        assert len(dates) == KEEP_DAYS and dates == sorted(dates, reverse=True)
        assert len(usage.summary(days=7)["days"]) == 7


class TestDistributorEvents:
    async def test_digikey_sent_cached_limited(self):
        usage = stats.usage
        fake = FakeDigiKey(httpx.Response(200, json=PRODUCT))
        client = digikey(fake, DailyQuota("DigiKey", 1))
        await client.get_part("LM358P")
        await client.get_part("LM358P")
        await client.get_part("NE555P")  # over the daily limit of 1
        assert usage.summary()["days"][0]["distributors"]["digikey"] == {"sent": 1, "cached": 1, "limited": 1}

    async def test_mouser_sent_and_cached(self):
        body = {"Errors": [], "SearchResults": {"NumberOfResult": 0, "Parts": []}}
        client = MouserClient(api_key="k")
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body)))
        await client.get_part("LM358P")
        await client.get_part("LM358P")
        assert stats.usage.summary()["days"][0]["distributors"]["mouser"] == {"sent": 1, "cached": 1, "limited": 0}


class TestServerWiring:
    async def test_tool_calls_and_apps_are_counted(self):
        from fastmcp import Client
        from fastmcp.exceptions import ToolError
        from pcbparts_mcp import server
        async with Client(server.mcp) as client:
            await client.call_tool("get_design_rules", {"topic": "ldo"})
            await client.call_tool("digikey_get_part", {"product_number": "LM358P"})  # no credentials: error reply
            with pytest.raises(ToolError):
                await client.call_tool("board_get", {"slug": 5, "nope": True})
            with pytest.raises(ToolError):
                await client.call_tool("not_a_tool", {})
            assert len(stats.usage.tools) == 14
        day = stats.usage.summary()["days"][0]
        assert day["tools"]["get_design_rules"]["calls"] == 1
        assert day["tools"]["digikey_get_part"]["errors"] == 1
        assert day["tools"]["board_get"]["failed"] == 1
        assert day["tools"]["unknown"]["failed"] == 1
        assert sum(day["apps"].values()) == 1

    async def test_empty_results_are_counted(self):
        from fastmcp import Client
        from pcbparts_mcp import server
        async with Client(server.mcp) as client:
            await client.call_tool("sensor_recommend", {"query": "zzzzqqqq nonexistent"})
        assert stats.usage.summary()["days"][0]["tools"]["sensor_recommend"]["empty"] == 1

    async def test_over_http(self):
        """The real ASGI app: callers come from the rightmost X-Forwarded-For, apps from initialize,
        and the counts are served at /mcp/stats (the proxy forwards only /mcp* and /health)."""
        from pcbparts_mcp import server
        headers = {"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-06-18"}

        async def rpc(c, method, params, ip):
            return await c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                                headers={**headers, "X-Forwarded-For": ip})

        app = server.app
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as c:
                await rpc(c, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                            "clientInfo": {"name": "probe <b>app</b>", "version": "1"}}, "203.0.113.9")
                call = {"name": "get_design_rules", "arguments": {"topic": "usb"}}
                for ip in ("203.0.113.9", "198.51.100.1, 203.0.113.9", "198.51.100.1"):
                    assert (await rpc(c, "tools/call", call, ip)).status_code == 200
                body = (await c.get("/mcp/stats?days=abc")).json()
                assert len((await c.get("/mcp/stats?days=0")).json()["days"]) == 1
                assert (await c.get("/mcp/stats?days=1000")).status_code == 200
        day = body["days"][0]
        assert day["tools"]["get_design_rules"]["calls"] == 3
        assert day["callers"] == 2
        assert day["apps"] == {"probe bapp/b": 1}
        assert "keep no IPs" in body["about"]

    async def test_public_page_shows_30_days_of_the_year_kept(self, tmp_path, monkeypatch):
        from starlette.requests import Request
        from pcbparts_mcp import server
        clock = Clock()
        usage = UsageStats(clock=clock)
        usage.open(tmp_path / "usage.json")
        monkeypatch.setattr(stats, "usage", usage)
        for _ in range(40):
            usage.record_call("jlc_search", "ok", 1)
            clock.advance(86400)
        usage.save()
        request = Request({"type": "http", "query_string": b"days=1000", "headers": []})
        assert len(json.loads((await server.usage_stats(request)).body)["days"]) == PUBLIC_DAYS == 30
        assert len(json.loads((tmp_path / "usage.json").read_text(encoding="utf-8"))["days"]) == 40
        assert KEEP_DAYS == 365

    async def test_shutdown_saves_the_counts(self, tmp_path, monkeypatch):
        from fastmcp import Client
        from pcbparts_mcp import server
        path = tmp_path / "usage.json"
        monkeypatch.setattr(server, "USAGE_STATS_PATH", str(path))
        async with Client(server.mcp) as client:
            await client.call_tool("get_design_rules", {"topic": "usb"})
        saved = json.loads(path.read_text(encoding="utf-8"))["days"]
        assert next(iter(saved.values()))["tools"]["get_design_rules"]["calls"] == 1
