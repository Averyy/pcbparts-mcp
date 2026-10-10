"""Regression tests for EasyEDA /api/products traffic (fixed in 0.5.6).

EasyEDA blocks an IP after ~24 /api/products requests (docs/ref-easyeda-api.md). These tests use
only the public client API, so they also run against the pre-0.5.6 code, where each one fails:
a block was retried 3x, checks kept firing during a block, nothing capped the request rate, the
footprint filter fired up to 100 checks, found footprints expired after 1h, and get_part pinned an
unknown footprint for the part's whole 1h TTL. Nothing here touches the network.
"""

import asyncio
import threading
import types
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from pcbparts_mcp import client as client_module
from pcbparts_mcp.client import JLCPCBClient

FOUND = {"success": True, "result": {"uuid": "a" * 32, "packageDetail": {"uuid": "b" * 32}}}


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload
        self.challenge_type = None

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict | None:
        return self._payload


class FakeSession:
    """Counts requests and answers each with respond(url): a FakeResponse, or an exception to raise."""

    def __init__(self, respond):
        self.respond = respond
        self.urls: list[str] = []

    async def get(self, url: str):
        self.urls.append(url)
        await asyncio.sleep(0)  # let concurrent checks interleave like real requests
        result = self.respond(url)
        if isinstance(result, Exception):
            raise result
        return result


class Clock:
    def __init__(self) -> None:
        self.now = 1_000_000.0

    def time(self) -> float:
        return self.now


@pytest.fixture
def wall(monkeypatch):
    """Fake wall clock for the client's caches (the module only uses time.time)."""
    clock = Clock()
    monkeypatch.setattr(client_module, "time", types.SimpleNamespace(time=clock.time))
    return clock


def client_with(respond) -> tuple[JLCPCBClient, FakeSession]:
    client = JLCPCBClient()
    fake = FakeSession(respond)
    # Footprint checks used _easyeda_session before 0.5.6 and _easyeda_products_session since
    client._easyeda_session = fake
    client._easyeda_products_session = fake
    return client, fake


async def test_blocked_check_sends_exactly_one_request(monkeypatch):
    """A 403 from /api/products is a rate-limit block: retrying it (old: 3 requests) extends it."""
    hits: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            hits.append(self.path)
            body = b"<HTML><BODY><H1>403 ERROR</H1>The request could not be satisfied.</BODY></HTML>"
            self.send_response(403)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        monkeypatch.setattr(
            client_module, "EASYEDA_COMPONENT_URL",
            f"http://127.0.0.1:{server.server_address[1]}/api/products/{{lcsc}}/components",
        )
        client = JLCPCBClient()  # real wafer sessions
        result = await client.check_easyeda_footprint("C8304")
        assert result == {"has_easyeda_footprint": None, "easyeda_symbol_uuid": None, "easyeda_footprint_uuid": None}
        assert len(hits) == 1
    finally:
        server.shutdown()


async def test_no_requests_while_blocked():
    """After a block, other footprint checks wait it out instead of hitting the endpoint (old: 6)."""
    client, fake = client_with(lambda url: FakeResponse(403))
    for lcsc in ["C1", "C2", "C3", "C4", "C5", "C6"]:
        result = await client.check_easyeda_footprint(lcsc)
        assert result["has_easyeda_footprint"] is None
    assert len(fake.urls) == 1


async def test_request_rate_is_capped():
    """At most 20 /api/products requests per rolling 2 minutes, whatever the callers do (old: 25)."""
    client, fake = client_with(lambda url: FakeResponse(200, FOUND))
    results = [await client.check_easyeda_footprint(f"C{n}") for n in range(1, 26)]
    assert len(fake.urls) == 20
    assert [r["has_easyeda_footprint"] for r in results] == [True] * 20 + [None] * 5


async def test_find_alternatives_footprint_filter_checks_at_most_15(monkeypatch):
    """limit=50 used to fire 2 x limit = 100 checks in one call; now at most 15."""
    client, fake = client_with(lambda url: FakeResponse(200, FOUND))
    original = {"lcsc": "C999999", "subcategory": "Unsupported Thing", "package": "0402",
                "library_type": "extended", "price": 0.1, "stock": 100, "specs": {}}
    candidates = [{"lcsc": f"C{n}", "package": "0402", "library_type": "extended", "price": 0.1,
                   "stock": 1000 - n, "specs": {}} for n in range(1, 61)]

    async def get_part(lcsc):
        return dict(original)

    async def search(**kwargs):
        return {"results": [dict(c) for c in candidates]}

    async def ensure_categories():
        return None

    monkeypatch.setattr(client, "get_part", get_part)
    monkeypatch.setattr(client, "search", search)
    monkeypatch.setattr(client, "_ensure_categories", ensure_categories)

    result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=50)
    assert len(fake.urls) == 15
    assert len(result["similar_parts"]) == 15


async def test_found_footprint_stays_cached_past_one_hour(wall):
    """Footprint availability is cached for 24h (old: 1h, so a re-check every hour)."""
    client, fake = client_with(lambda url: FakeResponse(200, FOUND))
    assert (await client.check_easyeda_footprint("C1525"))["has_easyeda_footprint"] is True
    wall.now += 2 * 3600
    assert (await client.check_easyeda_footprint("C1525"))["has_easyeda_footprint"] is True
    assert len(fake.urls) == 1


async def test_get_part_rechecks_unknown_footprint(monkeypatch, wall):
    """A part cached while its footprint was unknown must not stay unknown for the part's 1h TTL."""
    item = {
        "componentCode": "C8304", "componentModelEn": "STM32F103CBT6", "componentBrandEn": "ST",
        "componentSpecificationEn": "LQFP-48", "stockCount": 5000, "componentLibraryType": "expand",
        "preferredComponentFlag": False, "firstSortName": "Microcontrollers (MCU/MPU/SOC)",
        "secondSortName": "Embedded Processors & Controllers",
        "componentPrices": [{"startNumber": 1, "endNumber": 9, "productPrice": 2.5}],
        "attributes": [],
    }

    async def jlcpcb_request(url, params):
        return {"data": {"componentPageInfo": {"list": [item]}}}

    answers = iter([RuntimeError("EasyEDA timed out"), FakeResponse(200, FOUND)])
    client, fake = client_with(lambda url: next(answers))
    monkeypatch.setattr(client, "_request", jlcpcb_request)

    first = await client.get_part("C8304")
    assert first["has_easyeda_footprint"] is None  # EasyEDA failed

    wall.now += 6 * 60  # past the 5-min footprint error TTL, inside the 1h part TTL
    second = await client.get_part("C8304")
    assert second["has_easyeda_footprint"] is True
    assert second["easyeda_symbol_uuid"] == "a" * 32
    assert len(fake.urls) == 2
