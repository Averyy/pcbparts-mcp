"""Short datasheet links (0.8.0): jlc_get_part's datasheet_pdf was a ~1.2KB signed link that
expired in 30 minutes; it is now /mcp/datasheet/<lcsc>, which signs a fresh link on each visit."""

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

    monkeypatch.setattr(client, "_request", request)
    monkeypatch.setattr(client, "check_easyeda_footprint", easyeda)
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
        assert await client.datasheet_pdf_url("C2") is None
        assert await client.datasheet_pdf_url("C2") is None and calls == ["C1", "C2"]  # not asked again
        assert await client.datasheet_pdf_url("XYZ") is None and len(calls) == 2

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
        part = await server.jlc_get_part(lcsc="C15127")
        assert part["datasheet_pdf"] == "https://pcbparts.dev/mcp/datasheet/C15127"
        alternatives = await server.jlc_find_alternatives(lcsc="C15127")
        assert alternatives["original"]["datasheet_pdf"] == "https://pcbparts.dev/mcp/datasheet/C15127"
