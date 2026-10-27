"""Anonymous usage counts for /mcp/stats, DigiKey request spacing, and cached DigiKey "not found" answers
(0.6.3); outcome columns and error sorting (0.6.4). No network: httpx.MockTransport and fake clocks."""

import ast
import asyncio
import datetime
import json
import time
from pathlib import Path

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
        for outcome, ms in (("ok", 40), ("not_found", 20), ("bad_request", 30), ("rate_limited", 10), ("failed", 50)):
            usage.record_call("jlc_search", outcome, ms)
        usage.record_call("board_get", "something new", 5)  # not an outcome: counts as failed
        day = usage.summary()["days"][0]
        assert day["date"] == "2026-10-17" and day["calls"] == 6
        assert day["tools"]["jlc_search"] == {"calls": 5, "ok": 1, "similar_only": 0, "not_found": 1, "bad_request": 1,
                                              "rate_limited": 1, "failed": 1, "avg_ms": 30}
        assert day["tools"]["board_get"]["failed"] == 1
        assert list(day["tools"]) == ["jlc_search", "board_get"]  # busiest first
        for counts in day["tools"].values():  # the outcomes add up to the calls
            assert sum(counts[key] for key in stats.OUTCOMES) == counts["calls"]

    def test_0_6_3_counts_are_converted(self, tmp_path):
        """0.6.3 saved errors/failed/empty and distributor "limited"; error replies can't be sorted
        after the fact, so they stay as unsorted on those days."""
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-10-17": {
            "tools": {"jlc_search": {"calls": 9, "errors": 1, "failed": 0, "empty": 4, "ms": 900},
                      "board_get": {"calls": 2, "errors": 0, "failed": 2, "empty": 0, "ms": 4}},
            "apps": {"cursor": 1}, "callers": 3,
            "distributors": {"mouser": {"sent": 1, "cached": 0, "limited": 2}}}}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(path)
        usage.record_call("jlc_search", "ok", 100)
        day = usage.summary()["days"][0]
        assert day["tools"]["jlc_search"] == {"calls": 10, "ok": 5, "similar_only": 0, "not_found": 4, "bad_request": 0,
                                              "rate_limited": 0, "failed": 0, "unsorted": 1, "avg_ms": 100}
        assert day["tools"]["board_get"]["bad_request"] == 2 and "unsorted" not in day["tools"]["board_get"]
        assert "plus unsorted where shown" in usage.summary()["about"]
        assert day["distributors"]["mouser"] == {"sent": 1, "cached": 0, "rate_limited": 2}
        usage.save()  # saved in the new form, and read back the same
        again = UsageStats(clock=Clock())
        again.open(path)
        assert again.summary()["days"][0]["tools"] == day["tools"]

    def test_totals_add_up_the_days_shown(self):
        clock = Clock()
        usage = UsageStats(clock=clock)
        for day, (calls, app) in enumerate(((2, "cursor"), (3, "claude-code"), (4, "cursor"))):
            for _ in range(calls):
                usage.record_call("jlc_search", "ok", 10 * (day + 1), caller=f"203.0.113.{day}")
            usage.record_call("board_get", "not_found", 1)
            usage.record_app(app)
            usage.record_distributor("mouser", "sent")
            clock.advance(86400)
        summary = usage.summary()
        totals = summary["totals"]
        assert (totals["from"], totals["to"], totals["days"]) == ("2026-10-17", "2026-10-19", 3)
        assert totals["calls"] == 12 == sum(d["calls"] for d in summary["days"])
        assert totals["tools"]["jlc_search"] == {"calls": 9, "ok": 9, "similar_only": 0, "not_found": 0, "bad_request": 0,
                                                 "rate_limited": 0, "failed": 0, "avg_ms": 22}  # (20+60+120)/9
        assert totals["tools"]["board_get"]["not_found"] == 3
        assert totals["apps"] == {"cursor": 2, "claude-code": 1}
        assert totals["distributors"] == {"mouser": {"sent": 3, "cached": 0, "rate_limited": 0}}
        assert "callers" not in totals
        assert usage.summary(days=1)["totals"]["calls"] == 5  # only the newest day
        assert totals["hours"][21] == 12 and sum(totals["hours"]) == 12  # all at 21:xx UTC
        assert UsageStats(clock=clock).summary()["totals"] == {
            "from": None, "to": None, "days": 0, "calls": 0, "hours": [0] * 24, "tools": {}, "apps": {},
            "distributors": {}}

    def test_calls_per_utc_hour(self, tmp_path):
        clock = Clock(datetime.datetime(2026, 10, 18, 0, 30, tzinfo=UTC).timestamp())
        usage = UsageStats(clock=clock)
        usage.open(tmp_path / "usage.json")
        for hours_later in (0, 0, 1, 23):
            clock.now = datetime.datetime(2026, 10, 18, 0, 30, tzinfo=UTC).timestamp() + hours_later * 3600
            usage.record_call("jlc_search", "ok", 1)
        day = usage.summary()["days"][0]
        assert day["hours"][:2] == [2, 1] and day["hours"][23] == 1 and sum(day["hours"]) == day["calls"] == 4
        usage.save()
        again = UsageStats(clock=clock)
        again.open(tmp_path / "usage.json")
        assert again.summary()["days"][0]["hours"] == day["hours"]

    def test_hours_before_the_upgrade_are_unknown(self, tmp_path):
        """A day saved by 0.6.3 has no hours: the ones before the first call after the upgrade are
        null, not 0, so a graph doesn't show a false dip."""
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-10-17": {
            "tools": {"jlc_search": {"calls": 9, "errors": 1, "failed": 0, "empty": 4, "ms": 900}}}}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())  # 21:15 UTC
        usage.open(path)
        assert usage.summary()["days"][0]["hours"] is None
        usage.record_call("jlc_search", "ok", 1)
        hours = usage.summary()["days"][0]["hours"]
        assert hours[:21] == [None] * 21 and hours[21] == 1 and hours[22:] == [0, 0]
        assert usage.summary()["totals"]["hours"][21] == 1 and sum(usage.summary()["totals"]["hours"]) == 1

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
        for event in ("sent", "sent", "cached", "rate_limited"):
            usage.record_distributor("digikey", event)
        assert usage.summary()["days"][0]["distributors"] == {"digikey": {"sent": 2, "cached": 1, "rate_limited": 1}}

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
    async def test_digikey_sent_cached_rate_limited(self):
        usage = stats.usage
        fake = FakeDigiKey(httpx.Response(200, json=PRODUCT))
        client = digikey(fake, DailyQuota("DigiKey", 1))
        await client.get_part("LM358P")
        await client.get_part("LM358P")
        await client.get_part("NE555P")  # over the daily limit of 1
        assert usage.summary()["days"][0]["distributors"]["digikey"] == {"sent": 1, "cached": 1, "rate_limited": 1}

    async def test_mouser_sent_and_cached(self):
        body = {"Errors": [], "SearchResults": {"NumberOfResult": 0, "Parts": []}}
        client = MouserClient(api_key="k")
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body)))
        await client.get_part("LM358P")
        await client.get_part("LM358P")
        assert stats.usage.summary()["days"][0]["distributors"]["mouser"] == {"sent": 1, "cached": 1, "rate_limited": 0}


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
        assert day["tools"]["get_design_rules"]["ok"] == 1
        assert day["tools"]["digikey_get_part"]["failed"] == 1  # not configured: this server can't do it
        assert day["tools"]["board_get"]["bad_request"] == 1  # bad arguments
        assert day["tools"]["unknown"]["bad_request"] == 1  # no such tool
        assert sum(day["apps"].values()) == 1

    async def test_outcomes_through_the_server(self, monkeypatch):
        from fastmcp import Client
        from fastmcp.exceptions import ToolError
        from pcbparts_mcp import server
        async with Client(server.mcp) as client:
            await client.call_tool("sensor_recommend", {"query": "zzzzqqqq nonexistent"})  # nothing found
            await client.call_tool("jlc_search", {"subcategory_name": "Flux Capacitors"})  # invalid filter
            await client.call_tool("board_get", {"slug": "no-such-board"})  # valid request, no such board

            def crash(*args, **kwargs):
                raise RuntimeError("boom")

            monkeypatch.setattr(server, "_get_design_rules", crash)
            with pytest.raises(ToolError):
                await client.call_tool("get_design_rules", {"topic": "ldo"})
        tools = stats.usage.summary()["days"][0]["tools"]
        assert tools["sensor_recommend"]["not_found"] == 1
        assert tools["jlc_search"]["bad_request"] == 1
        assert tools["board_get"]["not_found"] == 1
        assert tools["get_design_rules"]["failed"] == 1  # a crash in our code

    @pytest.mark.parametrize(("content", "outcome"), [
        ({"alternatives": [{"lcsc": "C1"}], "similar_parts": []}, "ok"),
        ({"alternatives": [], "similar_parts": [{"lcsc": "C1"}]}, "similar_only"),
        ({"alternatives": [], "similar_parts": []}, "not_found"),
        ({"alternatives": [], "unverified_alternatives": [{"lcsc": "C1"}]}, "similar_only"),
        ({"alternatives": [{"lcsc": "C2"}], "unverified_alternatives": [{"lcsc": "C1"}]}, "ok"),
        ({"alternatives": [], "similar_parts": [{"lcsc": "C1"}],
          "error": "Board retrieval failed"}, "failed"),
    ])
    def test_alternatives_outcomes(self, content, outcome):
        from fastmcp.tools.tool import ToolResult
        from pcbparts_mcp.server import _call_outcome

        assert _call_outcome(ToolResult(structured_content=content)) == outcome

    def test_similar_only_counts_survive_restart_without_reclassifying_history(self, tmp_path):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-10-17": {
            "tools": {"jlc_find_alternatives": {"calls": 3, "not_found": 3, "ms": 30}},
        }}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(path)
        usage.record_call("jlc_find_alternatives", "similar_only", 10)
        usage.save()
        again = UsageStats(clock=Clock())
        again.open(path)
        counts = again.summary()["totals"]["tools"]["jlc_find_alternatives"]
        assert counts["calls"] == 4
        assert counts["not_found"] == 3
        assert counts["similar_only"] == 1
        assert sum(counts[key] for key in stats.OUTCOMES) == counts["calls"]
        assert "2026-10-26" in again.summary()["about"]
        assert "similar-parts-only replies as not found" in again.summary()["about"]

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
                response = await c.get("/mcp/stats?days=abc")
                assert response.headers["cache-control"] == "public, max-age=60"
                body = response.json()
                assert len((await c.get("/mcp/stats?days=0")).json()["days"]) == 1
                assert (await c.get("/mcp/stats?days=1000")).status_code == 200
        day = body["days"][0]
        assert day["tools"]["get_design_rules"]["calls"] == 3
        assert day["callers"] == 2
        assert day["apps"] == {"probe bapp/b": 1}
        assert "keep no IPs" in body["about"]
        assert "similar_only" in body["about"]
        assert "Cutover 2026-10-26" in body["about"]

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


# --- Error sorting: every error message in the code, and the kind it counts as ---

SRC = Path(__file__).parent.parent / "src" / "pcbparts_mcp"

# {"error": ...} replies, by their text with formatted parts as {}
ERROR_REPLIES = {
    "Invalid {}: {}": "bad_request",
    "Strict search cannot apply every constraint; see ignored_filters and parsed.adjusted_filters and use jlc_search_help(subcategory=...) for supported attributes": "bad_request",
    "lcsc must be an LCSC C-code (e.g., C6186); use jlc_get_part(mpn=...) to find the code for an MPN": "bad_request",
    "board_quantity and placements_per_board must be positive integers": "bad_request",
    "Unsupported library_type: '{}'": "bad_request",
    "Unsupported value for {}: '{}'": "bad_request",
    "Unsupported tag: '{}'": "bad_request",
    "Boards database not available": "failed",
    "Sensor database not available": "failed",
    "Database not available": "failed",
    "Design rules are not available.": "failed",
    "Categories not loaded": "failed",
    "Categories not loaded. Server may still be starting up.": "failed",
    "CSE client not initialized": "failed",
    "CSE credentials not configured. Set CSEARCH_USER and CSEARCH_PASS in environment.": "failed",
    "CSE authentication failed. Check CSEARCH_USER and CSEARCH_PASS.": "failed",
    "CSE model download failed (HTTP {})": "failed",
    "CSE model download failed (network/connection error)": "failed",
    "CSE model download too large ({} bytes, max {})": "failed",
    "CSE returned invalid zip file": "failed",
    "CSE search failed. Check server logs for details.": "failed",
    "CSE get_kicad failed. Check server logs for details.": "failed",
    "Mouser API key not configured. Set MOUSER_API_KEY in environment.": "failed",
    "DigiKey API credentials not configured. Set DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET in environment.": "failed",
    "Mouser part lookup failed: {}": "failed",
    "Mouser part lookup failed. Check server logs for details.": "failed",
    "DigiKey part lookup failed: {}": "failed",
    "DigiKey part lookup failed. Check server logs for details.": "failed",
    "Failed to fetch EasyEDA data. Check server logs for details.": "failed",
    "Invalid EasyEDA response for {}": "failed",
    "Invalid EasyEDA response - missing pin data": "failed",
    "Search failed: query too complex. Reduce the number of filters.": "failed",
    "Board search failed": "failed",
    "Board retrieval failed": "failed",
    "{} daily quota exceeded ({} requests/day on this shared server). It resets at {}.{}": "rate_limited",
    "{} daily quota exceeded ({}). It resets at {}.{}": "rate_limited",
    "{} daily quota exceeded (counted by {}). {} doesn't say when its count resets, so this server tries again at {}.{}": "rate_limited",
    "{} lookups are limited to {} a minute on this shared server. Try again in {} s.{}": "rate_limited",
    "{} is limiting requests per minute. Try again in {} s.{}": "rate_limited",
    "{} refused this server's requests (HTTP 403). Try again in {} s.{}": "rate_limited",
    "Couldn't check EasyEDA for {}'s symbol right now (lookup failed or EasyEDA is rate-limiting). Try again in a few minutes.": "rate_limited",
    "Subcategory not found: '{}'": "bad_request",
    "Category not found: '{}'": "bad_request",
    "Subcategory ID {} not found": "bad_request",
    "Must provide subcategory_id or subcategory_name": "bad_request",
    "Must provide either query or part_id": "bad_request",
    "Must provide either lcsc or mpn": "bad_request",
    "Must provide either lcsc or uuid": "bad_request",
    "Query too long (max 500 characters)": "bad_request",
    "Query too long (max {} characters)": "bad_request",
    "Component too long (max 200 characters)": "bad_request",
    "Org too long (max 200 characters)": "bad_request",
    "Focus too long (max 200 characters)": "bad_request",
    "MPN too long (max 100 characters)": "bad_request",
    "Part number too long (max 500 characters)": "bad_request",
    "Product number too long (max 500 characters)": "bad_request",
    "Too many {} (max {}, got {})": "bad_request",
    "Query contains invalid characters": "bad_request",
    "Query contains no searchable terms": "bad_request",
    "Invalid slug": "bad_request",
    "Give a DigiKey or manufacturer part number.": "bad_request",
    "Give at least one Mouser or manufacturer part number.": "bad_request",
    "Mouser takes up to {} part numbers per call, separated by |; got {}. Split the batch.": "bad_request",
    "Each Mouser part number must be 3-40 characters: {}": "bad_request",
    "Part not found: {}": "not_found",
    "Part {} not found": "not_found",
    "Board '{}' not found": "not_found",
    "No JLCPCB parts found for MPN '{}'": "not_found",
    "No parts found for '{}'": "not_found",
    "No ECAD model available for '{}'": "not_found",
    "No KiCad files found in model archive for part {}": "not_found",
    "No EasyEDA symbol available for {}": "not_found",
    "No EasyEDA symbol UUID for {}": "not_found",
}
NOT_TOOL_REPLIES = {"Rate limit exceeded", "Request body too large"}  # HTTP middleware answers

# Exception messages the tools pass on as {"error": str(e)}
EXCEPTION_MESSAGES = {
    "JLCPCB blocked request with WAF challenge — try again later": "failed",
    "JLCPCB rate limited — try again later": "rate_limited",
    "JLCPCB returned empty response — try again later": "failed",
    "JLCPCB connection failed — try again later": "failed",
    "JLCPCB request timed out — try again later": "failed",
    "JLCPCB returned HTTP {} — try again later": "failed",
    "JLCPCB API error: {}": "failed",
    "UUID is required": "bad_request",
    "Invalid UUID format": "bad_request",
    "EasyEDA has no symbol {}": "not_found",
    "Failed to fetch component data from EasyEDA": "failed",
    "Invalid EasyEDA response - missing dataStr": "failed",
    "DigiKey is limiting requests (HTTP 429). Try again later.": "rate_limited",
    "Mouser is limiting requests ({}). Try again later.": "rate_limited",
}


def _text(node) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _text(node.left) + _text(node.right)
    return "{}"


def _render(template: str) -> str:
    return template.replace("{}", "7")


class TestErrorSorting:
    def test_every_error_reply_in_the_code_is_sorted(self):
        """A new or reworded error message must be added to ERROR_REPLIES with its kind, so it can't
        count as "failed" by accident."""
        from pcbparts_mcp.server import _error_kind
        found = set()
        for path in SRC.rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Dict):
                    for key, value in zip(node.keys, node.values):
                        if isinstance(key, ast.Constant) and key.value == "error":
                            text = _text(value)
                            if text != "{}" and text not in NOT_TOOL_REPLIES:  # "{}": str(e), below
                                found.add(text)
        assert found - set(ERROR_REPLIES) == set(), "classify these in ERROR_REPLIES"
        assert set(ERROR_REPLIES) - found == set(), "no longer in the code: remove from ERROR_REPLIES"
        wrong = {t: (_error_kind(_render(t)), kind) for t, kind in ERROR_REPLIES.items() if _error_kind(_render(t)) != kind}
        assert wrong == {}

    def test_exception_messages_passed_on(self):
        from pcbparts_mcp.server import _error_kind
        client = (SRC / "client.py").read_text(encoding="utf-8")
        raised = {_text(node.args[0]) for node in ast.walk(ast.parse(client))
                  if isinstance(node, ast.Call) and getattr(node.func, "id", "") in ("ValueError", "EasyEDAComponentNotFound")
                  and node.args}
        assert raised - set(EXCEPTION_MESSAGES) == set(), "classify these in EXCEPTION_MESSAGES"
        wrong = {t: _error_kind(_render(t)) for t, kind in EXCEPTION_MESSAGES.items() if _error_kind(_render(t)) != kind}
        assert wrong == {}

    def test_real_limit_messages(self):
        """The messages DailyQuota really produces, in each state."""
        from pcbparts_mcp.server import _error_kind
        clock = Clock()
        quota = DailyQuota("DigiKey", 1, clock=clock, per_minute=1, own_key="DigiKey API credentials")
        assert quota.check() is None
        messages = [quota.check()["error"]]  # daily limit
        for reason in ("daily", "daily_unknown", "refused", "burst"):
            quota.pause(clock() + 1000 * (len(messages) + 1), reason)
            messages.append(quota.paused_error()["error"])
        minute = DailyQuota("Mouser", 10, clock=clock, per_minute=1)
        minute.check()
        messages.append(minute.check()["error"])  # per-minute cap
        assert {_error_kind(m) for m in messages} == {"rate_limited"}, messages

    def test_user_text_cant_change_the_kind(self):
        """Messages are matched from their start, so what a user typed can't move them."""
        from pcbparts_mcp.server import _error_kind
        assert _error_kind("Part not found: Query too long (max 5 characters)") == "not_found"
        assert _error_kind("No JLCPCB parts found for MPN 'daily quota exceeded '") == "not_found"
        assert _error_kind("Something nobody expected") == "failed"

    def test_exceptions(self):
        from fastmcp.exceptions import NotFoundError, ToolError, ValidationError
        from pcbparts_mcp.server import _exception_outcome
        assert _exception_outcome(ValidationError("bad args")) == "bad_request"
        assert _exception_outcome(NotFoundError("Unknown tool")) == "bad_request"
        assert _exception_outcome(ToolError("Error calling tool")) == "failed"
        assert _exception_outcome(RuntimeError("boom")) == "failed"
