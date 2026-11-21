"""Short datasheet links (0.8.0): jlc_get_part's datasheet_pdf was a ~1.2KB signed link that
expired in 30 minutes; it is now /mcp/datasheet/<lcsc>, which signs a fresh link on each visit."""

import asyncio
import json
import re
from datetime import datetime, timezone
from types import SimpleNamespace

import httpx
import pytest

import pcbparts_mcp.client as client_module
import pcbparts_mcp.server as server
from pcbparts_mcp.client import DATASHEET_SIGNINGS_PER_MINUTE, DatasheetLinkBusy, JLCPCBClient
from pcbparts_mcp import stats

ISSUED = 1793546220.0  # 2026-11-01T15:17:00Z


def signed(at: float, lcsc: str = "C15127") -> str:
    stamp = datetime.fromtimestamp(at, timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return (f"https://jlc-prod-smt.oss-eu-central-1.aliyuncs.com/smtDataManualFile/1-{lcsc}.pdf"
            f"?x-oss-date={stamp}&x-oss-expires=1800&x-oss-signature=abc")


@pytest.fixture
def clock(monkeypatch):
    now = [ISSUED]
    monkeypatch.setattr(client_module.time, "time", lambda: now[0])
    return now


@pytest.fixture
def live(monkeypatch, clock):
    """A client whose JLCPCB search returns a freshly signed link; EasyEDA must not be called."""
    async def sleep(seconds):
        clock[0] += seconds

    client = JLCPCBClient(clock=lambda: clock[0], sleep=sleep)
    calls = []

    async def request(url, params):
        calls.append(params["keyword"])
        items = [] if params["keyword"] == "C1" else [{
            "componentCode": params["keyword"],
            "dataManualFileAccessIdUrl": None if params["keyword"] == "C2" else signed(clock[0], params["keyword"]),
        }]
        return {"data": {"componentPageInfo": {"list": items}}}

    async def easyeda(lcsc):
        raise AssertionError("the datasheet link must not use EasyEDA's rate-limited endpoint")

    async def lcsc_product(lcsc):  # LCSC has no copy of these (never the network)
        calls.append(f"LCSC {lcsc}")
        return None

    monkeypatch.setattr(client, "_request", request)
    monkeypatch.setattr(client, "check_easyeda_footprint", easyeda)
    monkeypatch.setattr(client, "lcsc_product", lcsc_product)
    return client, calls


class TestSigning:
    async def test_signs_once_and_reuses_the_link(self, live, clock):
        client, calls = live
        first = await client.datasheet_pdf_url("c15127")
        assert first == signed(ISSUED) and calls == ["C15127"]
        clock[0] += 1200  # 20 minutes: still 10 left
        assert await client.datasheet_pdf_url("C15127") == first and len(calls) == 1
        clock[0] += 400  # under five minutes left: signed again
        assert await client.datasheet_pdf_url("C15127") == signed(clock[0]) and len(calls) == 2

    async def test_reuses_a_cached_part(self, live, clock):
        client, calls = live
        client._part_cache["C15127"] = (clock[0], {
            "lcsc": "C15127", "datasheet_pdf": signed(ISSUED), "datasheet_pdf_expires": "2026-11-01T15:47:00Z"})
        assert await client.datasheet_pdf_url("C15127") == signed(ISSUED) and calls == []

    async def test_missing_part_or_pdf(self, live, clock):
        client, calls = live
        assert await client.datasheet_pdf_url("C1") is None
        assert await client.datasheet_pdf_url("C2") is None  # no PDF, no maker link: LCSC has none either
        assert await client.datasheet_pdf_url("C2") is None and calls == ["C1", "C2", "LCSC C2"]  # not asked again
        assert await client.datasheet_pdf_url("XYZ") is None and len(calls) == 3

    async def test_budget_for_all_callers(self, live, clock):
        client, calls = live
        for n in range(DATASHEET_SIGNINGS_PER_MINUTE):
            await client.datasheet_pdf_url(f"C{100 + n}")
        assert await client.datasheet_pdf_url("C100") == signed(ISSUED, "C100")  # held links still work
        assert await client.datasheet_pdf_url("C999") == signed(ISSUED + 3, "C999")
        assert clock[0] == ISSUED + 3
        clock[0] += 60  # idle restores the full burst
        for n in range(DATASHEET_SIGNINGS_PER_MINUTE):
            await client.datasheet_pdf_url(f"C{200 + n}")
        assert clock[0] == ISSUED + 63


class TestRoute:
    @pytest.fixture
    def http(self, monkeypatch):
        async def datasheet_pdf_url(lcsc):
            if lcsc == "C429":
                raise DatasheetLinkBusy("This server signs at most 20 new datasheet links a minute", retry_after=17)
            if lcsc == "C502":
                raise ValueError("JLCPCB rate limited — try again later")
            return None if lcsc == "C404" else signed(ISSUED, lcsc)
        monkeypatch.setattr(server, "_client", SimpleNamespace(datasheet_pdf_url=datasheet_pdf_url))
        # The real app, so the route and the middleware in front of it are what's tested
        return httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app), base_url="http://localhost")

    async def test_redirects_to_the_signed_pdf(self, http):
        async with http:
            reply = await http.get("/mcp/datasheet/c15127")
        assert reply.status_code == 302
        assert reply.headers["location"] == signed(ISSUED, "C15127")
        assert reply.headers["cache-control"] == "no-store"

    @pytest.mark.parametrize("lcsc, status", [("C404", 404), ("C429", 429), ("C502", 502)])
    async def test_errors(self, http, lcsc, status):
        async with http:
            reply = await http.get(f"/mcp/datasheet/{lcsc}")
        assert reply.status_code == status and "error" in reply.json()
        assert "JLCPCB rate limited" not in reply.text  # upstream detail stays in the log (0.9.0)

    async def test_busy_says_when(self, http):
        async with http:
            reply = await http.get("/mcp/datasheet/C429")
        assert reply.headers["retry-after"] == "17" and reply.json()["retry_after"] == 17
        # The fields every 429 has (llms.txt), with this budget's own reason
        body = reply.json()
        assert body["reason"] == "datasheet_rate_limit" and body["reason"] in server.RATE_LIMIT_REASONS
        assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", body["resets_at"])
        assert body["tell_user"] == ("pcbparts makes at most 20 new datasheet links a minute for all its users; "
                                     "try again in 17 seconds.")
        assert body["error"].startswith("This server signs at most 20")

    def test_route_is_served(self):
        assert any(getattr(r, "path", None) == "/mcp/datasheet/{lcsc}" for r in server.app.routes)


class TestReplies:
    PART = {"lcsc": "C15127", "datasheet_pdf": signed(ISSUED), "datasheet_pdf_expires": "2026-11-01T15:47:00Z"}

    @pytest.mark.parametrize("host, base", [("pcbparts.dev", "https://pcbparts.dev"),
                                            ("localhost:8080", "http://localhost:8080")])
    def test_short_link_on_this_server(self, monkeypatch, host, base):
        request = SimpleNamespace(headers={"host": host}, url=SimpleNamespace(scheme="http"))
        monkeypatch.setattr(server, "get_http_request", lambda: request)
        short = server._short_datasheet_link(self.PART)
        assert short["datasheet_pdf"] == f"{base}/mcp/datasheet/C15127"
        assert "datasheet_pdf_expires" not in short
        assert self.PART["datasheet_pdf_expires"]  # the cached part is left as it was

    def test_without_an_http_request_the_signed_link_stays(self):
        assert server._short_datasheet_link(self.PART) == self.PART

    async def test_get_part_and_alternatives_use_it(self, monkeypatch):
        monkeypatch.setattr(server, "_datasheet_link_base", lambda: "https://pcbparts.dev")

        class Fake:
            async def get_part(self, lcsc):
                return dict(TestReplies.PART, subcategory="MOSFETs")

            async def find_alternatives(self, **kwargs):
                return {"original": dict(TestReplies.PART), "alternatives": []}
        monkeypatch.setattr(server, "_client", Fake())
        part = await server.jlc_get_part(lcsc="C15127", live=True)  # the snapshot answers without it
        assert part["datasheet_pdf"] == "https://pcbparts.dev/mcp/datasheet/C15127"
        alternatives = await server.jlc_find_alternatives(lcsc="C15127")
        assert alternatives["original"]["datasheet_pdf"] == "https://pcbparts.dev/mcp/datasheet/C15127"


class FakeReply:
    """A wafer-like reply with a JSON body."""

    def __init__(self, payload):
        self.payload, self.status_code, self.retries, self.rotations = payload, 200, 0, 0

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class FakeSession:
    """A wafer-like session: answer(keyword or productCode) gives the JSON body; sent counts requests."""

    def __init__(self, answer):
        self.answer, self.sent = answer, 0

    async def post(self, url, json=None, **kwargs):
        self.sent += 1
        return FakeReply(self.answer(json["keyword"]))

    async def get(self, url, params=None, **kwargs):
        self.sent += 1
        return FakeReply(self.answer(params["productCode"]))


TI_LISTED = "https://www.ti.com.cn/cn/lit/ds/symlink/tps61023.pdf?ts=1700000000000"
LCSC_COPY = "https://datasheet.lcsc.com/datasheet/pdf/f9afa0e15f6569ed1e35edd063d6a18f.pdf?productCode=C3"
# What JLCPCB lists: C919459 (TPS61023DRLR) only the maker's link, C3 only LCSC's viewer page, C4 its
# own PDF and the maker's, C5 LCSC's viewer page with LCSC's pdfUrl on another host, C6 nothing
LISTINGS = {
    "C919459": {"dataManualOfficialLink": TI_LISTED, "dataManualUrl": "https://www.lcsc.com/datasheet/C919459.pdf"},
    "C3": {"dataManualUrl": "https://www.lcsc.com/datasheet/C3.pdf"},
    "C4": {"dataManualFileAccessIdUrl": "SIGNED", "dataManualOfficialLink": TI_LISTED},
    "C5": {"dataManualUrl": "https://www.lcsc.com/datasheet/C5.pdf"},
    "C6": {},
}
LCSC_PRODUCTS = {"C3": LCSC_COPY, "C5": "https://evil.example/x.pdf"}


class TestUnsignedFallback:
    """JLCPCB keeps no PDF of its own for some parts it lists a datasheet for (no_datasheet false),
    so the snapshot reply's /mcp/datasheet link answered 404. It gives what the live reply would:
    the maker's datasheet (maker_datasheet), else LCSC's PDF (on LCSC's host only)."""

    @pytest.fixture
    def listed(self, clock):
        client = JLCPCBClient()

        def jlcpcb(code):
            listing = dict(LISTINGS.get(code, {}))
            if listing.get("dataManualFileAccessIdUrl") == "SIGNED":
                listing["dataManualFileAccessIdUrl"] = signed(clock[0], code)
            items = [{"componentCode": code, **listing}] if code in LISTINGS else []
            return {"code": 200, "data": {"componentPageInfo": {"list": items}}}

        def lcsc(code):
            pdf = LCSC_PRODUCTS.get(code)
            return {"code": 200, "result": {"productCode": code, "pdfUrl": pdf} if pdf else None}

        client._jlcpcb_session, client._lcsc_session = FakeSession(jlcpcb), FakeSession(lcsc)
        return client

    @staticmethod
    def upstream():
        return server.stats.usage.summary()["days"][0]["upstream"]

    async def test_maker_link_without_asking_lcsc(self, listed):
        assert await listed.datasheet_pdf_url("C919459") == "https://www.ti.com/lit/ds/symlink/tps61023.pdf"
        assert (listed._jlcpcb_session.sent, listed._lcsc_session.sent) == (1, 0)
        assert await listed.datasheet_pdf_url("C919459") == "https://www.ti.com/lit/ds/symlink/tps61023.pdf"
        assert listed._jlcpcb_session.sent == 1 and listed._datasheet_tokens == 19  # held, one budget slot
        assert self.upstream()["jlcpcb"]["sent"] == 1 and self.upstream()["jlcpcb"]["cached"] == 1

    async def test_lcsc_copy(self, listed):
        assert await listed.datasheet_pdf_url("C3") == LCSC_COPY
        assert (listed._jlcpcb_session.sent, listed._lcsc_session.sent) == (1, 1)
        assert self.upstream()["lcsc"]["sent"] == 1  # the LCSC request is counted
        assert await listed.datasheet_pdf_url("C3") == LCSC_COPY and listed._lcsc_session.sent == 1

    async def test_jlcpcb_pdf_first(self, listed, clock):
        assert await listed.datasheet_pdf_url("C4") == signed(ISSUED, "C4") and listed._lcsc_session.sent == 0

    @pytest.mark.parametrize("code", ["C5", "C6", "C7"], ids=["other_host", "nothing", "not_listed"])
    async def test_none(self, listed, code):
        assert await listed.datasheet_pdf_url(code) is None
        assert listed._lcsc_session.sent == (0 if code == "C7" else 1)  # an unlisted code isn't asked of LCSC
        assert await listed.datasheet_pdf_url(code) is None and listed._jlcpcb_session.sent == 1  # held 10 minutes

    async def test_cached_live_part_needs_no_request(self, listed):
        listed._part_cache["C919459"] = (ISSUED, {"lcsc": "C919459", "maker_datasheet": "https://www.ti.com/x.pdf"})
        listed._part_cache["C3"] = (ISSUED, {"lcsc": "C3", "datasheet_pdf": LCSC_COPY})
        listed._part_cache["C5"] = (ISSUED, {"lcsc": "C5", "datasheet_pdf": "https://evil.example/x.pdf"})
        assert await listed.datasheet_pdf_url("C919459") == "https://www.ti.com/x.pdf"
        assert await listed.datasheet_pdf_url("C3") == LCSC_COPY
        assert listed._jlcpcb_session.sent == 0
        assert await listed.datasheet_pdf_url("C5") is None and listed._jlcpcb_session.sent == 1  # not that host

    async def test_the_budget_still_applies(self, listed, clock, monkeypatch):
        sleeps = []

        async def sleep(seconds):
            sleeps.append(seconds)
            clock[0] += seconds

        monkeypatch.setattr(listed, "_datasheet_sleep", sleep)
        for n in range(DATASHEET_SIGNINGS_PER_MINUTE):
            LISTINGS.setdefault(f"C{900 + n}", {"dataManualOfficialLink": TI_LISTED})
        try:
            for n in range(DATASHEET_SIGNINGS_PER_MINUTE):
                assert await listed.datasheet_pdf_url(f"C{900 + n}")
            assert await listed.datasheet_pdf_url("C919459")
            assert sleeps == [3]
        finally:
            for n in range(DATASHEET_SIGNINGS_PER_MINUTE):
                LISTINGS.pop(f"C{900 + n}", None)

    async def test_route_redirects_there_and_ignores_the_query(self, listed, monkeypatch):
        monkeypatch.setattr(server, "_client", listed)
        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as http:
            reply = await http.get("/mcp/datasheet/C919459", params={"url": "https://evil.example/x.pdf"})
            missing = await http.get("/mcp/datasheet/C6?next=https://evil.example/")
        assert reply.status_code == 302
        assert reply.headers["location"] == "https://www.ti.com/lit/ds/symlink/tps61023.pdf"
        assert reply.headers["cache-control"] == "no-store"
        assert missing.status_code == 404 and missing.json() == {"error": "No datasheet PDF found for C6"}


def test_a_link_that_is_not_text_is_no_link():
    """LCSC's pdfUrl or a listing's link as a list or a number raised inside the redirect (a 500)."""
    from pcbparts_mcp.client import _on_lcsc, lcsc_datasheet_pdf, maker_datasheet_link
    assert lcsc_datasheet_pdf({"pdfUrl": ["https://datasheet.lcsc.com/x.pdf"]}) is None
    assert lcsc_datasheet_pdf({"pdfUrl": 7}) is None and lcsc_datasheet_pdf({"pdfUrl": ""}) is None
    assert lcsc_datasheet_pdf({"pdfUrl": "https://datasheet.lcsc.com/x.pdf"}) == "https://datasheet.lcsc.com/x.pdf"
    assert _on_lcsc(["https://datasheet.lcsc.com/x.pdf"]) is False and _on_lcsc(None) is False
    assert maker_datasheet_link(12345, ["x"], None, "https://www.onsemi.com/pdf/a.pdf") == "https://www.onsemi.com/pdf/a.pdf"


class TestQueue:
    async def test_slots_up_to_30_seconds_then_429_and_retry(self, live, clock, monkeypatch):
        client, calls = live
        for n in range(20):
            await client.datasheet_pdf_url(f"C{100 + n}")
        sleepers = []
        ready = asyncio.Event()

        async def sleep(seconds):
            released = asyncio.Event()
            sleepers.append((seconds, released))
            if len(sleepers) == 10:
                ready.set()
            await released.wait()

        monkeypatch.setattr(client, "_datasheet_sleep", sleep)
        pending = [asyncio.create_task(client.datasheet_pdf_url(f"C{200 + n}")) for n in range(10)]
        await ready.wait()
        assert [seconds for seconds, _ in sleepers] == list(range(3, 31, 3))
        assert len(calls) == 20
        with pytest.raises(DatasheetLinkBusy) as busy:
            await client.datasheet_pdf_url("C999")
        assert busy.value.retry_after == 3 and "try again in 3s" in str(busy.value)
        assert "25 minutes" in str(busy.value)
        # Held links don't need a slot, even with a full queue.
        assert await client.datasheet_pdf_url("C100") == signed(ISSUED, "C100")
        for (delay, released), task in zip(sleepers, pending):
            clock[0] = ISSUED + delay
            released.set()
            assert await task
        assert len(calls) == 30
        counts = stats.usage.summary()["totals"]["datasheet_links"]
        assert counts["signed"] == 30 and counts["waited"] == 10 and counts["reused"] == 1
        assert stats.usage.summary()["totals"]["upstream"]["jlcpcb"]["rate_limited"] == 1

    async def test_simultaneous_visits_share_one_request(self, live, clock, monkeypatch):
        client, calls = live
        started, release = asyncio.Event(), asyncio.Event()
        request = client._request

        async def held_request(url, params):
            started.set()
            await release.wait()
            return await request(url, params)

        monkeypatch.setattr(client, "_request", held_request)
        first = asyncio.create_task(client.datasheet_pdf_url("C15127"))
        await started.wait()
        followers = [asyncio.create_task(client.datasheet_pdf_url("c15127")) for _ in range(5)]
        release.set()
        answers = await asyncio.gather(first, *followers)
        assert answers == [signed(ISSUED)] * 6 and calls == ["C15127"]
        counts = stats.usage.summary()["totals"]["datasheet_links"]
        assert counts["signed"] == 1 and counts["reused"] == 5
        assert client._datasheet_inflight == {}

    async def test_after_wait_rechecks_held_links(self, live, clock, monkeypatch):
        client, calls = live
        for n in range(20):
            await client.datasheet_pdf_url(f"C{100 + n}")

        async def sleep(seconds):
            clock[0] += seconds
            client._part_cache["C15127"] = (clock[0], {
                "datasheet_pdf": signed(clock[0]), "datasheet_pdf_expires": "2026-11-01T16:00:00Z"})

        monkeypatch.setattr(client, "_datasheet_sleep", sleep)
        assert await client.datasheet_pdf_url("C15127") == signed(ISSUED + 3)
        assert len(calls) == 20
        counts = stats.usage.summary()["totals"]["datasheet_links"]
        assert counts["signed"] == 20 and counts["waited"] == 0 and counts["reused"] == 1
        # Reusing the refreshed link returns the unused slot to the budget.
        assert await client.datasheet_pdf_url("C999") == signed(ISSUED + 3, "C999")
        assert clock[0] == ISSUED + 3 and len(calls) == 21

    async def test_failed_shared_request_is_not_kept(self, live, monkeypatch):
        client, calls = live
        original = client._request

        async def failed(url, params):
            raise ValueError("source failed")

        monkeypatch.setattr(client, "_request", failed)
        with pytest.raises(ValueError, match="source failed"):
            await client.datasheet_pdf_url("C15127")
        monkeypatch.setattr(client, "_request", original)
        assert await client.datasheet_pdf_url("C15127") == signed(ISSUED)
        assert calls == ["C15127"]

    async def test_disconnect_keeps_the_shared_request_and_close_cancels_it(self, live, monkeypatch):
        client, calls = live
        started, release = asyncio.Event(), asyncio.Event()

        async def blocked(url, params):
            started.set()
            await release.wait()

        monkeypatch.setattr(client, "_request", blocked)
        visitor = asyncio.create_task(client.datasheet_pdf_url("C15127"))
        await started.wait()
        shared = client._datasheet_inflight["C15127"]
        visitor.cancel()
        with pytest.raises(asyncio.CancelledError):
            await visitor
        assert not shared.done()
        await client.close()
        assert shared.cancelled() and client._datasheet_inflight == {}

    async def test_a_counter_fault_does_not_break_the_link(self, live, monkeypatch):
        class Broken(stats.UsageStats):
            def record_datasheet_link(self, event):
                raise RuntimeError("counter fault")

        monkeypatch.setattr(stats, "usage", Broken())
        client, calls = live
        assert await client.datasheet_pdf_url("C15127") == signed(ISSUED)
        assert await client.datasheet_pdf_url("C15127") == signed(ISSUED)
        assert calls == ["C15127"]


class TestDatasheetStats:
    async def test_route_counts_statuses_and_ignores_bad_codes(self, live, monkeypatch, stats_headers):
        client, calls = live
        monkeypatch.setattr(server, "_client", client)
        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as http:
            assert (await http.get("/mcp/datasheet/C15127")).status_code == 302
            assert (await http.get("/mcp/datasheet/C15127")).status_code == 302
            assert (await http.get("/mcp/datasheet/C1")).status_code == 404
            assert (await http.get("/mcp/datasheet/C1")).status_code == 404
            assert (await http.get("/mcp/datasheet/XYZ")).status_code == 404

            async def failed(url, params):
                raise ValueError("no upstream")

            monkeypatch.setattr(client, "_request", failed)
            assert (await http.get("/mcp/datasheet/C502")).status_code == 502
            client._datasheet_tokens = -20
            assert (await http.get("/mcp/datasheet/C429")).status_code == 429
            body = (await http.get("/mcp/stats", headers=stats_headers)).json()
        expected = dict(visits=6, reused=2, signed=3, waited=0, refused=1, failed=1, not_found=2)
        assert body["days"][0]["datasheet_links"] == expected
        assert body["totals"]["datasheet_links"] == expected
        assert "C15127" not in json.dumps(body)

    def test_persistence_cleaning_and_old_days(self, tmp_path):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {
            "2026-11-01": {"datasheet_links": {"visits": 4, "reused": "bad", "signed": float("inf"),
                                              "waited": True, "C15127": 999}},
            "2026-10-31": {},
        }}), encoding="utf-8")
        usage = stats.UsageStats(clock=lambda: ISSUED)
        usage.open(path)
        days = usage.summary()["days"]
        assert days[1]["datasheet_links"] is None
        assert days[0]["datasheet_links"] == dict(visits=4, reused=0, signed=0, waited=0, refused=0, failed=0, not_found=0)
        usage.record_datasheet_link("signed")
        usage.record_datasheet_link("C15127")  # arbitrary text cannot reach the saved counts
        usage.save()
        loaded = stats.UsageStats(clock=lambda: ISSUED)
        loaded.open(path)
        assert loaded.summary() == usage.summary()
        assert "C15127" not in path.read_text(encoding="utf-8")
        assert "datasheet_links" in loaded.summary()["about"]

    def test_counting_on_an_old_day_starts_with_zero(self, tmp_path):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-11-01": {}}}), encoding="utf-8")
        usage = stats.UsageStats(clock=lambda: ISSUED)
        usage.open(path)
        assert usage.summary()["days"][0]["datasheet_links"] is None
        usage.record_datasheet_link("visits")
        assert usage.summary()["days"][0]["datasheet_links"]["visits"] == 1
