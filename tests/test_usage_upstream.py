"""/mcp/stats from 0.10.0: requests sent to each service we call and the answers their caches gave
instead (upstream), part numbers asked of Mouser and DigiKey in total and distinct (parts_asked), and
the per-IP rate limit's refusals (per_ip_refusals) with their hourly most-refused-IPs log line. No
network: fake sessions, httpx.MockTransport and fake clocks."""

import ast
import asyncio
import datetime
import json
import logging
import types
from pathlib import Path

import httpx
import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from wafer import RateLimited, WaferTimeout

from pcbparts_mcp import client as client_module
from pcbparts_mcp import server, stats
from pcbparts_mcp.cache import CallerTally, Cooldown, Pacer, SlidingWindowBudget
from pcbparts_mcp.client import DatasheetLinkBusy, JLCPCBClient
from pcbparts_mcp.cse import CSEClient
from pcbparts_mcp.digikey import DigiKeyClient
from pcbparts_mcp.easyeda_store import FootprintAnswer
from pcbparts_mcp.mouser import MouserClient, MouserError
from pcbparts_mcp.stats import (
    EXTENSION_UPSTREAM_SOURCES, PARTS_ASKED, REFUSAL_GROUPS, UPSTREAM_EVENTS, UPSTREAM_SOURCES, UPSTREAM_STATUS_SOURCES,
    UsageStats,
)

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 18, 20, 5, tzinfo=UTC).timestamp()
SRC = Path(__file__).parent.parent / "src" / "pcbparts_mcp"


class Clock:
    def __init__(self, now: float = NOW):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class Reply:
    """A wafer-like reply: status, JSON body, and the retries/rotations wafer reports."""

    def __init__(self, status_code: int = 200, payload=None, retries: int = 0, rotations: int = 0):
        self.status_code = status_code
        self._payload = payload
        self.retries = retries
        self.rotations = rotations
        self.challenge_type = None

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class Session:
    """A fake wafer session: answer(url, json) gives each reply, or an exception to raise."""

    def __init__(self, answer):
        self.answer = answer
        self.sent = 0

    async def _send(self, url, json=None):
        self.sent += 1
        reply = self.answer(url, json)
        if isinstance(reply, Exception):
            raise reply
        return reply

    async def get(self, url, **kwargs):
        return await self._send(url)

    async def post(self, url, json=None, **kwargs):
        return await self._send(url, json)


def upstream() -> dict:
    return stats.usage.summary()["days"][0]["upstream"]


def counts(**events) -> dict:
    return {event: events.get(event, 0) for event in UPSTREAM_EVENTS}


@pytest.fixture
def clock(monkeypatch):
    fake = Clock()
    monkeypatch.setattr(client_module, "time", types.SimpleNamespace(time=fake))
    return fake


def jlcpcb_client(clock, jlcpcb=None, lcsc=None, products=None) -> JLCPCBClient:
    client = JLCPCBClient()
    client._easyeda_products_budget = SlidingWindowBudget(20, 120, clock)
    client._easyeda_products_cooldown = Cooldown(60, 600, clock)
    client._easyeda_land_budget = SlidingWindowBudget(1, 60, clock)
    client._easyeda_land_cooldown = Cooldown(60, 600, clock)
    client._jlcpcb_session = jlcpcb
    client._lcsc_session = lcsc
    client._easyeda_products_session = products
    return client


def search_reply(code: str, **wafer) -> Reply:
    item = {"componentCode": code, "componentLibraryType": "base", "componentModelEn": "RC0402",
            "attributes": [{"attribute_name_en": "Resistance", "attribute_value_name": "10kΩ"}]}
    return Reply(200, {"code": 200, "data": {"componentPageInfo": {"list": [item], "total": 1}}}, **wafer)


class TestUsageStats:
    def test_upstream_counts(self):
        usage = UsageStats(clock=Clock())
        usage.record_upstream("jlcpcb", "sent")
        usage.record_upstream("jlcpcb", "retries", 2)
        usage.record_upstream("jlcpcb", "retries", 0)  # nothing to add
        usage.record_upstream("easyeda_products", "cached")
        usage.record_upstream("easyeda_products", "rate_limited")
        usage.record_upstream("somewhere", "sent")  # not a source: not counted, so the file stays bounded
        usage.record_upstream("lcsc", "exploded")
        day = usage.summary()["days"][0]["upstream"]
        assert day == {"jlcpcb": counts(sent=1, retries=2), "easyeda_products": counts(cached=1, rate_limited=1)}
        assert list(day) == ["jlcpcb", "easyeda_products"]  # in UPSTREAM_SOURCES order

    def test_totals_add_up_the_days(self):
        clock = Clock()
        usage = UsageStats(clock=clock)
        for day in range(3):
            for _ in range(day + 1):
                usage.record_upstream("lcsc", "sent")
            usage.record_parts_asked("mouser", ["LM358P", "NE555P"])
            usage.record_refusal()
            clock.advance(86400)
        totals = usage.summary()["totals"]
        assert totals["upstream"] == {"lcsc": counts(sent=6)}
        # distinct can't be added across days (the same part on two days is one part), like callers
        assert totals["parts_asked"] == {"mouser": {"total": 6}}
        assert totals["per_ip_refusals"] == {"total": 3, "everyone_else": 3, "platform_ranges": 0, "server_busy": 0, "too_many_clients": 0}
        assert [d["parts_asked"]["mouser"] for d in usage.summary()["days"]] == [{"total": 2, "distinct": 2}] * 3

    def test_distinct_parts_ignore_case_and_separators(self):
        clock = Clock()
        usage = UsageStats(clock=clock)
        usage.record_parts_asked("mouser", ["LM358P", "lm358p", " LM358-P ", "LM 358/P", "NE555P"])
        usage.record_parts_asked("digikey", ["LM358P"])  # each distributor counts its own
        usage.record_parts_asked("arrow", ["LM358P"])  # not a distributor we count
        usage.record_parts_asked("mouser", [])
        day = usage.summary()["days"][0]
        assert day["parts_asked"] == {"digikey": {"total": 1, "distinct": 1}, "mouser": {"total": 5, "distinct": 2}}
        clock.advance(86400)  # a new day counts afresh
        usage.record_parts_asked("mouser", ["LM358P"])
        assert usage.summary()["days"][0]["parts_asked"]["mouser"] == {"total": 1, "distinct": 1}

    def test_distinct_parts_are_capped(self, monkeypatch):
        monkeypatch.setattr(stats, "MAX_DISTINCT_PARTS", 2)
        usage = UsageStats(clock=Clock())
        usage.record_parts_asked("digikey", ["A1", "A2", "A3", "A1"])
        assert usage.summary()["days"][0]["parts_asked"]["digikey"] == {"total": 4, "distinct": 2}

    def test_no_part_numbers_or_ips_in_the_file(self, tmp_path):
        path = tmp_path / "usage.json"
        usage = UsageStats(clock=Clock())
        usage.open(path)
        usage.record_parts_asked("mouser", ["LM358P", "TPS63020DSJR"])
        usage.record_refusal()
        usage.record_call("mouser_get_part", "ok", 5, caller="203.0.113.7")
        usage.save()
        text = path.read_text(encoding="utf-8")
        assert "LM358" not in text and "TPS63020" not in text and "203.0.113" not in text
        saved = json.loads(text)["days"]["2026-11-18"]
        assert saved["parts_asked"] == {"mouser": {"total": 2, "distinct": 2}}
        assert saved["per_ip_refusals"] == {"everyone_else": 1}

    def test_refusal_groups(self):
        usage = UsageStats(clock=Clock())
        usage.record_refusal()
        usage.record_refusal("everyone_else")
        usage.record_refusal("platform_ranges")
        usage.record_refusal("203.0.113.7")  # not a group: counts as everyone else
        assert usage.summary()["days"][0]["per_ip_refusals"] == {"total": 4, "everyone_else": 3, "platform_ranges": 1, "server_busy": 0, "too_many_clients": 0}
        assert REFUSAL_GROUPS == ("everyone_else", "platform_ranges", "server_busy", "too_many_clients")

    def test_stored_busy_refusals_from_0_10_0(self, tmp_path):
        """0.10.1 removed the busy cap: nothing counts under server_busy any more, but a day 0.10.0
        stored with busy refusals still loads, shows them and adds them into total and the totals,
        through saves."""
        limiter = server.RateLimitMiddleware(None, platform_addresses=server.platform_ranges.PlatformRanges({}))
        for reason in [*server.RATE_LIMIT_REASONS, None]:
            assert limiter._refusal_group("203.0.113.7", reason) != "server_busy"
        path = tmp_path / "usage.json"
        stored = {"tools": {}, "hours": [0] * 24, "per_ip_refusals": {"everyone_else": 3, "server_busy": 40}}
        path.write_text(json.dumps({"days": {"2026-11-17": stored, "2026-11-18": stored}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())  # 2026-11-18
        usage.open(path)
        usage.record_refusal()  # the upgrade day goes on counting
        today, yesterday = usage.summary()["days"]
        assert yesterday["per_ip_refusals"] == {"total": 43, "everyone_else": 3, "platform_ranges": 0, "server_busy": 40,
                                                "too_many_clients": 0}
        assert today["per_ip_refusals"]["total"] == 44 and today["per_ip_refusals"]["server_busy"] == 40
        assert usage.summary()["totals"]["per_ip_refusals"] == {
            "total": 87, "everyone_else": 7, "platform_ranges": 0, "server_busy": 80, "too_many_clients": 0}
        usage.save()
        assert json.loads(path.read_text(encoding="utf-8"))["days"]["2026-11-18"]["per_ip_refusals"] == {
            "everyone_else": 4, "server_busy": 40}

    def test_a_day_without_refusals_shows_none(self):
        usage = UsageStats(clock=Clock())
        usage.record_call("jlc_search", "ok", 1)
        assert usage.summary()["days"][0]["per_ip_refusals"] == {"total": 0, "everyone_else": 0, "platform_ranges": 0, "server_busy": 0, "too_many_clients": 0}

    def test_days_from_before_0_10_0(self, tmp_path):
        """A 0.9.x day has none of the new counts: upstream and parts_asked are empty and refusals
        are null (not counted, rather than none), until 0.10.0 counts on that day."""
        path = tmp_path / "usage.json"
        old_day = {"tools": {"jlc_search": {"calls": 4, "ok": 4, "ms": 40}}, "hours": [0] * 24, "apps": {},
                   "callers": 2, "distributors": {"mouser": {"sent": 1, "cached": 0, "rate_limited": 0}},
                   "reasons": {}, "why_empty": {}}
        path.write_text(json.dumps({"days": {"2026-11-17": old_day, "2026-11-18": old_day}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())  # 2026-11-18, the deploy day
        usage.open(path)
        summary = usage.summary()
        for day in summary["days"]:
            assert day["upstream"] == {} and day["parts_asked"] == {} and day["per_ip_refusals"] is None
            assert day["tools"]["jlc_search"]["calls"] == 4  # the old counts are kept
        assert summary["totals"]["per_ip_refusals"] == {"total": 0, "everyone_else": 0, "platform_ranges": 0, "server_busy": 0, "too_many_clients": 0}
        usage.record_refusal()  # counted from the deploy on
        usage.save()
        again = UsageStats(clock=Clock())
        again.open(path)
        today, yesterday = again.summary()["days"]
        assert today["per_ip_refusals"] == {"total": 1, "everyone_else": 1, "platform_ranges": 0, "server_busy": 0, "too_many_clients": 0}
        assert yesterday["per_ip_refusals"] is None  # still not counted
        assert json.loads(path.read_text(encoding="utf-8"))["days"]["2026-11-17"]["per_ip_refusals"] is None

    def test_malformed_new_counts_are_dropped(self, tmp_path):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-11-18": {
            "upstream": {"jlcpcb": {"sent": "3", "cached": 2}, "<script>": {"sent": 1}, "lcsc": [1]},
            "parts_asked": {"mouser": [1], "digikey": {"total": 4, "distinct": True}, "LM358P": {"total": 1}},
            "per_ip_refusals": {"everyone_else": "x", "203.0.113.7": 3},
        }}}), encoding="utf-8")
        usage = UsageStats(clock=Clock())
        usage.open(path)
        day = usage.summary()["days"][0]
        assert day["upstream"] == {"jlcpcb": counts(cached=2)}
        assert day["parts_asked"] == {"digikey": {"total": 4, "distinct": 0}}
        assert day["per_ip_refusals"] == {"total": 0, "everyone_else": 0, "platform_ranges": 0, "server_busy": 0, "too_many_clients": 0}
        usage.record_upstream("jlcpcb", "sent")  # counting goes on from the cleaned day
        usage.record_parts_asked("digikey", ["X1"])
        day = usage.summary()["days"][0]
        assert day["upstream"]["jlcpcb"]["sent"] == 1 and day["parts_asked"]["digikey"] == {"total": 5, "distinct": 1}

    def test_about_describes_the_new_fields(self):
        about = UsageStats(clock=Clock()).summary()["about"]
        for text in ("upstream", "parts_asked", "per_ip_refusals", "jlcpcb", "lcsc", "easyeda_products",
                     "easyeda_components", "easyeda_pads", "cse", "retries", "rate_limited", "distinct",
                     "everyone_else", "platform_ranges", "not tool calls"):
            assert text in about, text


class TestJLCPCB:
    async def test_get_part_counts_each_service(self, clock):
        """A part fetched live: one JLCPCB search, one LCSC product lookup (JLCPCB lists no
        datasheet) and one EasyEDA footprint check; asked again, the part cache answers."""
        jlcpcb = Session(lambda url, body: search_reply(body["keyword"], retries=1, rotations=1))
        lcsc = Session(lambda url, body: Reply(200, {"code": 200, "result": {"productCode": "C25744"}}))
        products = Session(lambda url, body: Reply(404))
        client = jlcpcb_client(clock, jlcpcb, lcsc, products)
        first = await client.get_part("C25744")
        assert first["lcsc"] == "C25744" and first["has_easyeda_footprint"] is False
        assert await client.get_part("c25744") == first
        assert (jlcpcb.sent, lcsc.sent, products.sent) == (1, 1, 1)
        assert upstream() == {"jlcpcb": counts(sent=1, retries=2, cached=1), "lcsc": counts(sent=1),
                              "easyeda_products": counts(sent=1)}

    async def test_search_requests(self, clock):
        jlcpcb = Session(lambda url, body: search_reply("C1"))
        client = jlcpcb_client(clock, jlcpcb)
        client.set_categories([{"id": 1, "name": "Resistors", "subcategories": []}])  # as the server does
        await client.search(query="10k resistor 0402", library_type="no_fee")  # basic, then preferred
        await client.search(query="10k resistor 0402")
        assert jlcpcb.sent == 3 and upstream() == {"jlcpcb": counts(sent=3)}

    async def test_failed_requests_still_count(self, clock):
        """A request that failed was still sent; wafer's retries come from the error's reply when
        it has one, and a timeout reports none."""
        errors = [RateLimited("https://jlcpcb.com", response=Reply(429, retries=2, rotations=1)),
                  WaferTimeout("https://jlcpcb.com", 30)]
        client = jlcpcb_client(clock, Session(lambda url, body: errors.pop(0)))
        for _ in range(2):
            with pytest.raises(ValueError):
                await client.get_part("C25744")
        assert upstream() == {"jlcpcb": counts(sent=2, retries=3)}

    async def test_lcsc_failure_counts(self, clock):
        client = jlcpcb_client(clock, lcsc=Session(lambda url, body: WaferTimeout("https://lcsc.com", 8)))
        assert await client.lcsc_product("C25744") is None
        assert upstream() == {"lcsc": counts(sent=1)}

    async def test_datasheet_links(self, clock):
        jlcpcb = Session(lambda url, body: Reply(200, {"code": 200, "data": {"componentPageInfo": {"list": []}}}))
        client = jlcpcb_client(clock, jlcpcb)
        assert await client.datasheet_pdf_url("C1") is None  # one search: JLCPCB has no PDF for it
        assert await client.datasheet_pdf_url("C1") is None  # the missing link is held for a while
        client._datasheet_tokens = -client_module.DATASHEET_SIGNINGS_PER_MINUTE
        with pytest.raises(DatasheetLinkBusy):
            await client.datasheet_pdf_url("C2")  # the next slot is more than 30 s away
        assert upstream() == {"jlcpcb": counts(sent=1, cached=1, rate_limited=1)}


class TestEasyEDA:
    async def test_footprint_checks(self, clock):
        products = Session(lambda url, body: Reply(404))
        client = jlcpcb_client(clock, products=products)
        assert (await client._check_easyeda_footprint("C1"))[1] == "checked"
        assert (await client._check_easyeda_footprint("C1"))[1] == "cached"
        client._easyeda_overrides["C2"] = FootprintAnswer(True, "a" * 32, "b" * 32, clock())
        assert (await client._check_easyeda_footprint("C2"))[1] == "stored"
        assert (await client._check_easyeda_footprint("not a code"))[1] == "invalid"  # nothing to count
        client._easyeda_products_cooldown.trip()
        assert (await client._check_easyeda_footprint("C3"))[1] == "cooldown"
        assert products.sent == 1
        assert upstream() == {"easyeda_products": counts(sent=1, cached=2, rate_limited=1)}

    async def test_footprint_budget(self, clock):
        products = Session(lambda url, body: Reply(404))
        client = jlcpcb_client(clock, products=products)
        client._easyeda_products_budget = SlidingWindowBudget(1, 120, clock)
        assert (await client._check_easyeda_footprint("C1"))[1] == "checked"
        assert (await client._check_easyeda_footprint("C2"))[1] == "budget"
        assert upstream() == {"easyeda_products": counts(sent=1, rate_limited=1)}

    async def test_symbols(self, clock):
        symbol = {"success": True, "result": {"dataStr": {"shape": []}}}
        missing = {"success": False, "code": 404}
        components = Session(lambda url, body: Reply(200, symbol if url.endswith("a" * 32) else missing))
        client = jlcpcb_client(clock)
        client._easyeda_session = components
        await client.get_easyeda_component("a" * 32)
        await client.get_easyeda_component("a" * 32)
        for _ in range(2):  # a missing symbol is kept too, so asking again sends nothing
            with pytest.raises(client_module.EasyEDAComponentNotFound):
                await client.get_easyeda_component("c" * 32)
        assert components.sent == 2
        assert upstream() == {"easyeda_components": counts(sent=2, cached=2)}

    async def test_land_check_pads(self, clock):
        land = Session(lambda url, body: Reply(404))  # EasyEDA has no such footprint: pads []
        client = jlcpcb_client(clock)
        client._easyeda_land_session = land
        assert await client.footprint_pads("a" * 32) == ([], "fetched")
        assert await client.footprint_pads("a" * 32) == ([], "cached")
        assert await client.footprint_pads("c" * 32) == (None, "budget")  # one fetch a minute here
        client._easyeda_land_cooldown.trip()
        assert await client.footprint_pads("d" * 32) == (None, "cooldown")
        assert land.sent == 1
        assert upstream() == {"easyeda_pads": counts(sent=1, cached=1, rate_limited=2)}


class TestCSE:
    async def test_searches_and_downloads(self, monkeypatch):
        import io
        import zipfile

        from pcbparts_mcp import cse as cse_module

        monkeypatch.setattr(cse_module, "CSE_RATE_LIMIT", 0)
        monkeypatch.setattr(cse_module, "CSE_STATUS_RETRY_DELAY", 0)
        monkeypatch.setattr(cse_module, "CSE_USER", "user")
        monkeypatch.setattr(cse_module, "CSE_PASS", "pass")
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("P1/KiCad/P1.kicad_sym", "(kicad_symbol_lib)")
        part = {"PartNo": "P1", "Manuf": "TI", "PartID": 1, "ECAD_M": "https://componentsearchengine.com/m?partID=1",
                "Has3D": "N", "Quality": 3, "PinCount": 8}
        statuses = ["F0R0", "Success"]  # CSE's first answer for a new query isn't always "Success"

        def answer(request: httpx.Request) -> httpx.Response:
            if "partID" in str(request.url):
                return httpx.Response(200, content=archive.getvalue())
            return httpx.Response(200, json={"status": statuses.pop(0), "parts": [part]})

        client = CSEClient()
        client._http = httpx.AsyncClient(transport=httpx.MockTransport(answer))
        await client.search("LM358P")  # asked twice: two requests
        await client.search("lm358p")
        await client.get_kicad(part_id=1)
        await client.get_kicad(part_id=1)
        await client.close()
        assert upstream() == {"cse": counts(sent=3, cached=2)}

    async def test_a_counter_raising_doesnt_break_a_search(self, monkeypatch):
        """Review 2026-11-18: cse.py called the counter unguarded, so a counter fault failed the lookup."""
        from pcbparts_mcp import cse as cse_module

        class Broken(stats.UsageStats):
            def _day(self, date=None):
                raise RuntimeError("counter broke")

        monkeypatch.setattr(stats, "usage", Broken())
        monkeypatch.setattr(cse_module, "CSE_RATE_LIMIT", 0)
        part = {"PartNo": "P1", "Manuf": "TI", "PartID": 1, "Has3D": "N", "Quality": 3, "PinCount": 8}
        client = CSEClient()
        client._http = httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"status": "Success", "parts": [part]})))
        try:
            assert (await client.search("LM358P"))["total"] == 1
            assert (await client.search("LM358P"))["total"] == 1  # cached: counted too
        finally:
            await client.close()


class TestMouserHTTP:
    @pytest.mark.parametrize("result,label,sends", [
        (httpx.Response(200, json={"SearchResults": {"Parts": []}}), "2xx", 1),
        (httpx.Response(200, text="unreadable"), "2xx", 3),
        (httpx.Response(403), "4xx", 1), (httpx.Response(429), "429", 1),
        (httpx.Response(503), "5xx", 3), (httpx.ReadTimeout("private"), "timeout", 1),
        (httpx.ConnectError("private"), "connection", 3), (asyncio.CancelledError(), "cancelled", 1),
        (RuntimeError("unexpected"), "other_error", 1),
    ], ids=["ok", "unreadable", "forbidden", "limit", "server", "timeout", "connection", "cancelled", "other"])
    async def test_every_attempt_counts(self, clock, result, label, sends):
        requests = []

        def send(request):
            requests.append(request)
            if isinstance(result, BaseException):
                raise result
            return result

        async def sleep(seconds):
            clock.advance(seconds)

        client = MouserClient("key", clock=clock, sleep=sleep)
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(send))
        try:
            if label in ("timeout", "connection", "5xx") or (label == "2xx" and sends == 3) or label == "4xx":
                with pytest.raises(MouserError):
                    await client.get_part("LM358P")
            elif isinstance(result, BaseException):
                with pytest.raises(type(result)):
                    await client.get_part("LM358P")
            else:
                await client.get_part("LM358P")
        finally:
            await client.close()
        day = stats.usage.summary()["days"][0]
        assert day["upstream_status"] == {"mouser": {label: sends}}
        assert day["distributors"]["mouser"]["sent"] == len(requests) == sends
        assert day["distributors"]["mouser"].get("retries", 0) == sends - 1

    def test_status_and_retries_survive_save_load_and_totals(self, tmp_path, clock, monkeypatch):
        path = tmp_path / "usage.json"
        usage = UsageStats(clock=clock)
        usage.open(path)
        monkeypatch.setattr(stats, "usage", usage)
        for _ in range(2):
            stats.count_upstream_status("mouser", httpx.Response(503))
            stats.count_upstream_status("mouser", httpx.Response(200))
            stats.count_distributor("mouser", "sent")
            stats.count_distributor("mouser", "sent")
            stats.count_distributor("mouser", "retries")
            clock.advance(86400)
        usage.save()
        reloaded = UsageStats(clock=clock)
        reloaded.open(path)
        view = reloaded.summary()
        assert view == usage.summary()
        assert view["totals"]["upstream_status"]["mouser"] == {"5xx": 2, "2xx": 2}
        assert view["totals"]["distributors"]["mouser"] == {"sent": 4, "cached": 0, "rate_limited": 0, "retries": 2}
        assert "mouser retries (from 0.10.9" in view["about"]
        assert "From 0.10.9 also mouser" in view["about"]


class TestDigiKeyExtCounts:
    """From 0.10.11: ext's HTTP requests under the digikey_ext source, and its lookups in
    distributors.digikey.ext_sent (also in sent, which stays the total)."""

    async def test_the_ext_source_is_counted_through_the_client_helpers(self, monkeypatch):
        usage = UsageStats(clock=Clock())
        monkeypatch.setattr(stats, "usage", usage)
        assert "digikey_ext" in UPSTREAM_SOURCES and "digikey_ext" in UPSTREAM_STATUS_SOURCES

        async def reply(status):
            return Reply(status, retries=1)

        await client_module._sent("digikey_ext", reply(200))
        await client_module._sent("digikey_ext", reply(503))
        client_module._count_upstream("digikey_ext", "cached")
        client_module._count_upstream("digikey_ext", "rate_limited")
        await client_module._sent("digikey", reply(200))  # the API's stay apart
        day = usage.summary()["days"][0]
        assert day["upstream"] == {"digikey": counts(sent=1, retries=1),
                                   "digikey_ext": counts(sent=2, retries=2, cached=1, rate_limited=1)}
        assert list(day["upstream"]) == ["digikey", "digikey_ext"]  # in UPSTREAM_SOURCES order
        assert day["upstream_status"] == {"digikey_ext": {"2xx": 1, "5xx": 1}, "digikey": {"2xx": 1}}

    def test_ext_sent_is_part_of_sent_and_survives_save_load_and_totals(self, tmp_path):
        clock = Clock()
        path = tmp_path / "usage.json"
        usage = UsageStats(clock=clock)
        usage.open(path)
        for _ in range(2):
            usage.record_distributor("digikey", "sent")  # through the API
            usage.record_distributor("digikey", "sent", path="ext_sent")  # through ext
            usage.record_distributor("digikey", "cached")
            usage.record_distributor("digikey", "ext_sent")  # a path alone counts nothing
            usage.record_distributor("mouser", "sent", path="ext_sent")  # not one of Mouser's paths
            usage.record_upstream("digikey_ext", "sent")
            clock.advance(86400)
        usage.record_distributor("digikey", "cached")  # a day without ext lookups still says so
        usage.save()
        reloaded = UsageStats(clock=clock)
        reloaded.open(path)
        view = reloaded.summary()
        assert view == usage.summary()
        assert [d["distributors"]["digikey"] for d in view["days"]] == [
            {"sent": 0, "cached": 1, "rate_limited": 0, "ext_sent": 0},
            *[{"sent": 2, "cached": 1, "rate_limited": 0, "ext_sent": 1}] * 2]
        assert view["days"][1]["distributors"]["mouser"] == {"sent": 1, "cached": 0, "rate_limited": 0}
        assert view["totals"]["distributors"]["digikey"] == {"sent": 4, "cached": 3, "rate_limited": 0, "ext_sent": 2}
        assert view["totals"]["upstream"]["digikey_ext"] == counts(sent=2)
        about = view["about"]
        for text in ("digikey_ext (requests an optional deployment extension sends for DigiKey lookups",
                     "absent without one", "distributors digikey ext_sent (from 0.10.11)",
                     "API lookups are sent - ext_sent", "already there without it",
                     "Totals omit it when any listed day that sent DigiKey lookups lacks it",
                     "a rollback below 0.10.11 drops it, and the digikey_ext request counts, from every stored day"):
            assert text in about, text
        assert "digikey_ext" not in UsageStats(clock=clock).summary()["totals"]["upstream"]  # absent, not 0

    def test_sent_and_ext_sent_land_on_one_day_at_midnight(self):
        """Both come from one clock reading, so a lookup sent as the UTC day ends can't count its
        sent on one day and its path on the next."""
        midnight = datetime.datetime(2026, 11, 19, tzinfo=UTC).timestamp()
        clock = Clock(midnight - 0.5)
        usage = UsageStats(clock=clock)
        usage.record_distributor("digikey", "cached")  # the day's counts, from 0.10.11 on

        def reading():
            now = clock()
            clock.advance(1)  # each read of the clock passes midnight
            return now

        usage._clock = reading
        usage.record_distributor("digikey", "sent", path="ext_sent")
        usage._clock = clock
        days = {d["date"]: d["distributors"] for d in usage.summary()["days"]}
        assert days["2026-11-18"]["digikey"] == {"sent": 1, "cached": 1, "rate_limited": 0, "ext_sent": 1}
        assert "digikey" not in days.get("2026-11-19", {})

    def test_a_day_counted_before_0_10_11_stays_unsplit(self, tmp_path):
        clock = Clock()
        path = tmp_path / "usage.json"
        today = datetime.datetime.fromtimestamp(clock(), UTC).date().isoformat()
        path.write_text(json.dumps({"days": {today: {
            "tools": {}, "apps": {}, "callers": 0,
            "distributors": {"digikey": {"sent": 5, "cached": 1, "rate_limited": 0}},
        }}}), encoding="utf-8")
        usage = UsageStats(clock=clock)
        usage.open(path)
        usage.record_distributor("digikey", "sent", path="ext_sent")  # its earlier sent lookups can't be split
        assert usage.summary()["days"][0]["distributors"]["digikey"] == {"sent": 6, "cached": 1, "rate_limited": 0}
        clock.advance(86400)  # the next day is counted by this version from its start
        usage.record_distributor("digikey", "sent", path="ext_sent")
        usage.record_distributor("digikey", "sent")
        view = usage.summary()
        assert view["days"][0]["distributors"]["digikey"] == {"sent": 2, "cached": 0, "rate_limited": 0, "ext_sent": 1}
        assert view["days"][1]["distributors"]["digikey"] == {"sent": 6, "cached": 1, "rate_limited": 0}
        # the unsplit day sent lookups: totals can't split them, so they keep the single figure
        assert view["totals"]["distributors"]["digikey"] == {"sent": 8, "cached": 1, "rate_limited": 0}
        assert usage.summary(days=1)["totals"]["distributors"]["digikey"]["ext_sent"] == 1

    def test_an_unsplit_day_without_sent_lookups_keeps_the_totals_split(self, tmp_path):
        clock = Clock()
        path = tmp_path / "usage.json"
        today = datetime.datetime.fromtimestamp(clock(), UTC).date().isoformat()
        path.write_text(json.dumps({"days": {today: {
            "tools": {}, "apps": {}, "callers": 0,
            "distributors": {"digikey": {"sent": 0, "cached": 3, "rate_limited": 1}},
        }}}), encoding="utf-8")
        usage = UsageStats(clock=clock)
        usage.open(path)
        clock.advance(86400)
        usage.record_distributor("digikey", "sent", path="ext_sent")
        assert usage.summary()["totals"]["distributors"]["digikey"] == {
            "sent": 1, "cached": 3, "rate_limited": 1, "ext_sent": 1}

    @pytest.mark.parametrize("stored", ["many", True, None, -1, 2.5, 3, 2**60],
                             ids=["text", "bool", "null", "neg", "float", "over-sent", "huge"])
    def test_a_malformed_ext_sent_leaves_the_day_unsplit(self, tmp_path, stored):
        clock = Clock()
        path = tmp_path / "usage.json"
        today = datetime.datetime.fromtimestamp(clock(), UTC).date().isoformat()
        path.write_text(json.dumps({"days": {today: {
            "tools": {}, "apps": {}, "callers": 0,
            "distributors": {"digikey": {"sent": 2, "ext_sent": stored}, "mouser": {"sent": 1, "ext_sent": 3}},
            "upstream": {"digikey_ext": {"sent": 2, "cached": True}},
        }}}), encoding="utf-8")
        usage = UsageStats(clock=clock)
        usage.open(path)
        day = usage.summary()["days"][0]
        assert day["distributors"] == {"digikey": {"sent": 2, "cached": 0, "rate_limited": 0},
                                       "mouser": {"sent": 1, "cached": 0, "rate_limited": 0}}
        assert day["upstream"] == {"digikey_ext": counts(sent=2)}
        usage.record_distributor("digikey", "sent", path="ext_sent")  # and it stays unsplit
        assert usage.summary()["days"][0]["distributors"]["digikey"] == {"sent": 3, "cached": 0, "rate_limited": 0}

    def test_a_path_counts_only_with_sent(self):
        usage = UsageStats(clock=Clock())
        for event in ("cached", "rate_limited", "skipped"):
            usage.record_distributor("digikey", event, path="ext_sent")
        usage.record_distributor("digikey", "sent", path="ext_sent")
        assert usage.summary()["days"][0]["distributors"]["digikey"] == {
            "sent": 1, "cached": 1, "rate_limited": 1, "skipped": 1, "ext_sent": 1}

    def test_a_stored_ext_sent_is_kept(self, tmp_path):
        clock = Clock()
        path = tmp_path / "usage.json"
        today = datetime.datetime.fromtimestamp(clock(), UTC).date().isoformat()
        path.write_text(json.dumps({"days": {today: {
            "tools": {}, "apps": {}, "callers": 0, "distributors": {"digikey": {"sent": 4, "ext_sent": 0}},
        }}}), encoding="utf-8")
        usage = UsageStats(clock=clock)
        usage.open(path)
        usage.record_distributor("digikey", "sent", path="ext_sent")
        assert usage.summary()["days"][0]["distributors"]["digikey"] == {
            "sent": 5, "cached": 0, "rate_limited": 0, "ext_sent": 1}


class TestPartsAsked:
    async def test_mouser(self):
        body = {"Errors": [], "SearchResults": {"NumberOfResult": 0, "Parts": []}}
        client = MouserClient(api_key="k")
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body)))
        await client.get_part("LM358P|NE555P|lm358p")  # the repeat in one call is asked once
        await client.get_part("lm358p")  # answered from the stored answers: still asked
        await client.get_part("LM358-P")  # another spelling: sent, but the same part
        await client.close()
        day = stats.usage.summary()["days"][0]
        assert day["parts_asked"] == {"mouser": {"total": 4, "distinct": 2}}
        assert day["distributors"]["mouser"] == {"sent": 2, "cached": 1, "rate_limited": 0}  # unchanged

    async def test_digikey(self):
        clock = Clock()

        async def sleep(seconds):
            clock.advance(seconds)

        def answer(request: httpx.Request) -> httpx.Response:
            if "oauth2/token" in str(request.url):
                return httpx.Response(200, json={"access_token": "tok", "expires_in": 599})
            return httpx.Response(404)

        client = DigiKeyClient(client_id="id", client_secret="secret")
        client._http = httpx.AsyncClient(transport=httpx.MockTransport(answer))
        client._pacer = Pacer(5, clock=clock, sleep=sleep)
        for number in ("LM358P", "lm358p", "LM358-P", "   "):  # the blank one isn't a lookup
            await client.get_part(number)
        await client.close()
        day = stats.usage.summary()["days"][0]
        assert day["parts_asked"] == {"digikey": {"total": 3, "distinct": 1}}
        assert day["distributors"]["digikey"] == {"sent": 2, "cached": 1, "rate_limited": 0, "ext_sent": 0}


async def _ok(request):
    return PlainTextResponse("ok")


def limited_app(per_minute: int) -> Starlette:
    return Starlette(routes=[Route("/mcp", _ok, methods=["GET", "POST"]), Route("/health", _ok)],
                     middleware=[Middleware(server.RateLimitMiddleware, requests_per_minute=per_minute)])


class TestRefusals:
    @pytest.fixture
    def refused(self, monkeypatch):
        clock = Clock()
        monkeypatch.setattr(server, "time", types.SimpleNamespace(time=clock, monotonic=clock))
        tally = CallerTally("Per-IP rate limit", clock, what="refusals")
        monkeypatch.setattr(server, "_refused_callers", tally)
        return clock, tally

    async def test_counted_without_ips_and_logged_hourly(self, refused, tmp_path, caplog, monkeypatch):
        clock, tally = refused
        usage = UsageStats(clock=clock)
        usage.open(tmp_path / "usage.json")
        monkeypatch.setattr(stats, "usage", usage)
        app = limited_app(2)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as c:
            replies = [await c.post("/mcp", headers={"X-Forwarded-For": ip})
                       for ip in ["203.0.113.7"] * 3 + ["198.51.100.1, 198.51.100.2"] * 4]
            for _ in range(5):
                assert (await c.get("/health", headers={"X-Forwarded-For": "203.0.113.7"})).status_code == 200
        assert [r.status_code for r in replies] == [200, 200, 429, 200, 200, 429, 429]
        refusal = replies[2]
        body = refusal.json()  # error and retry_after unchanged for clients; 0.10.0 adds fields
        assert {key: body[key] for key in ("error", "retry_after")} == {"error": "Rate limit exceeded", "retry_after": 60}
        assert body["reason"] == "per_ip_rate_limit"
        assert refusal.headers["retry-after"] == "60"  # all three at the same moment: a full minute
        assert usage.summary()["days"][0]["per_ip_refusals"] == {"total": 3, "everyone_else": 3, "platform_ranges": 0, "server_busy": 0, "too_many_clients": 0}
        assert usage.summary()["days"][0]["refused_hours"] == [0] * 20 + [3, 0, 0, 0]  # 0.10.1: at 20:05 UTC
        usage.save()
        assert "203.0.113" not in (tmp_path / "usage.json").read_text(encoding="utf-8")
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            tally.flush_if_due()  # the hour isn't over: nothing yet
            assert caplog.messages == []
            clock.advance(3600)
            tally.flush_if_due()
        assert caplog.messages == [
            "Per-IP rate limit refusals 2026-11-18 20:00-21:00 UTC: 3 from 2 IPs; top: 198.51.100.2 2, 203.0.113.7 1"]

    async def test_hours_without_refusals_log_nothing(self, refused, caplog):
        clock, tally = refused
        app = limited_app(100)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as c:
            assert (await c.post("/mcp", headers={"X-Forwarded-For": "203.0.113.7"})).status_code == 200
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            clock.advance(3600)
            tally.flush_if_due()
        assert caplog.messages == []
        assert stats.usage.summary()["days"] == []

    async def test_counting_never_breaks_the_reply(self, refused, monkeypatch):
        def broken(group="everyone_else"):
            raise RuntimeError("boom")

        _, tally = refused
        monkeypatch.setattr(stats.usage, "record_refusal", broken)
        app = limited_app(1)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as c:
            statuses = [(await c.post("/mcp")).status_code for _ in range(2)]
        assert statuses == [200, 429]
        assert sum(tally._counts.values()) == 1  # the log line still gets it

    def test_groups(self):
        """The AI platforms' published addresses count apart (tests/test_platform_ranges.py has the rest)."""
        middleware = server.RateLimitMiddleware(None)
        assert middleware._refusal_group("160.79.104.10") == "platform_ranges"  # Anthropic's
        assert middleware._refusal_group("203.0.113.7") == "everyone_else"

    async def test_shutdown_logs_the_hour_so_far(self, refused, caplog):
        from fastmcp import Client
        clock, tally = refused
        tally.record("203.0.113.7")
        clock.advance(600)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            async with Client(server.mcp) as client:
                await client.list_tools()
        assert "Per-IP rate limit refusals 2026-11-18 20:00-20:15 UTC: 1 from 1 IPs; top: 203.0.113.7 1" in caplog.messages

    async def test_the_minute_task_logs_a_finished_hour(self, refused, monkeypatch, caplog):
        clock, tally = refused
        tally.record("203.0.113.7")
        clock.advance(3600)
        real_sleep, slept = asyncio.sleep, []

        async def one_minute(seconds):
            slept.append(seconds)
            await real_sleep(0)

        monkeypatch.setattr(server.asyncio, "sleep", one_minute)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            task = asyncio.ensure_future(server._every_minute())
            want = "Per-IP rate limit refusals 2026-11-18 20:00-21:00 UTC: 1 from 1 IPs"
            while not any(m.startswith(want) for m in caplog.messages) and len(slept) < 5:
                await real_sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert any(m.startswith(want) for m in caplog.messages), caplog.messages


class TestWiring:
    @staticmethod
    def _calls(names: set[str]):
        for path in SRC.rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Call):
                    name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
                    if name in names:
                        yield path.name, name, node

    def test_every_count_names_a_known_source_and_event(self):
        """record_upstream drops names it doesn't know, so a typo would count nothing."""
        used, bad = set(), []
        for file, name, node in self._calls({"record_upstream", "count_upstream", "_count_upstream", "_sent"}):
            source = node.args[0]
            if file in ("client.py", "stats.py") and isinstance(source, ast.Name) and source.id == "source":
                continue  # the helpers themselves, passing their own arguments on
            if not (isinstance(source, ast.Constant) and source.value in UPSTREAM_SOURCES):
                bad.append(f"{file}: {ast.unparse(node)}")
                continue
            used.add(source.value)
            if name != "_sent" and not (isinstance(node.args[1], ast.Constant) and node.args[1].value in UPSTREAM_EVENTS):
                bad.append(f"{file}: {ast.unparse(node)}")
        assert bad == []
        # and every source is counted somewhere, except the ones only an optional extension sends
        assert used == set(UPSTREAM_SOURCES) - set(EXTENSION_UPSTREAM_SOURCES)

    def test_parts_asked_names_a_distributor(self):
        found = {node.args[0].value for _, _, node in self._calls({"record_parts_asked", "count_parts_asked"})
                 if isinstance(node.args[0], ast.Constant)}
        assert found == set(PARTS_ASKED)

    def test_every_status_counter_names_a_known_source(self):
        used = set()
        for file, _, node in self._calls({"count_upstream_status", "record_upstream_status", "_sent"}):
            source = node.args[0]
            if file in ("client.py", "stats.py") and isinstance(source, ast.Name) and source.id == "source":
                continue
            assert isinstance(source, ast.Constant) and source.value in UPSTREAM_STATUS_SOURCES
            used.add(source.value)
        assert used == set(UPSTREAM_STATUS_SOURCES) - set(EXTENSION_UPSTREAM_SOURCES)
