"""Short datasheet links (0.8.0): jlc_get_part's datasheet_pdf was a ~1.2KB signed link that
expired in 30 minutes; it is now /mcp/datasheet/<lcsc>, which signs a fresh link on each visit."""

import re
from datetime import datetime, timezone
from types import SimpleNamespace

import httpx
import pytest

import pcbparts_mcp.client as client_module
import pcbparts_mcp.server as server
from pcbparts_mcp.client import DATASHEET_SIGNINGS_PER_MINUTE, DatasheetLinkBusy, JLCPCBClient

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
    client = JLCPCBClient()
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
        clock[0] += 20
        with pytest.raises(DatasheetLinkBusy) as busy:
            await client.datasheet_pdf_url("C999")
        assert busy.value.retry_after == 40 and "try again in 40s" in str(busy.value)
        assert f"at most {DATASHEET_SIGNINGS_PER_MINUTE}" in str(busy.value) and "25 minutes" in str(busy.value)
        clock[0] += 41
        assert await client.datasheet_pdf_url("C999")


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
        assert listed._jlcpcb_session.sent == 1 and len(listed._datasheet_signings) == 1  # held, one budget slot
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

    async def test_the_budget_still_applies(self, listed, clock):
        for n in range(DATASHEET_SIGNINGS_PER_MINUTE):
            LISTINGS.setdefault(f"C{900 + n}", {"dataManualOfficialLink": TI_LISTED})
        try:
            for n in range(DATASHEET_SIGNINGS_PER_MINUTE):
                assert await listed.datasheet_pdf_url(f"C{900 + n}")
            with pytest.raises(DatasheetLinkBusy):
                await listed.datasheet_pdf_url("C919459")
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
