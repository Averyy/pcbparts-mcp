"""0.10.2: jlc_get_part(lcsc=...) answers from the daily snapshot by default (no request of any
kind); live=true, or a code the snapshot doesn't list (gone, new, unknown), asks JLCPCB as before.
When that live lookup fails (JLCPCB didn't answer), the database's row answers, marked live_failed;
jlc_stock_check does the same for one LCSC code. /health shows the snapshot's age, and /mcp/stats
how the lookups were answered.
No network: small built databases, fake wafer sessions on a real client, offline() and fake clocks."""

import datetime
import json
import sys
import types
from pathlib import Path

import pytest
from fastmcp import Client
from wafer import ChallengeDetected, ConnectionFailed, EmptyResponse, RateLimited, WaferError, WaferHTTPError, WaferTimeout

from conftest import write_catalog_category

import pcbparts_mcp.server as server
from pcbparts_mcp import stats
from pcbparts_mcp.catalog_files import PRICE_TIERS_FILE, write_price_tiers, write_sold_out
from pcbparts_mcp.client import JLCPCBClient, JLCPCBUnavailable
from pcbparts_mcp.db import ComponentDatabase
from pcbparts_mcp.easyeda_store import FootprintAnswer
from pcbparts_mcp.config import LIFECYCLE_TTL
from pcbparts_mcp.lifecycle import MOUSER_NOT_STATED, Reading, utc_text
from pcbparts_mcp.stats import LCSC_LOOKUP_EVENTS, UsageStats

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import build_database  # noqa: E402
from search_baseline import offline  # noqa: E402

SCRAPED_AT = "2026-11-19T15:15:56Z"
SUBCATEGORIES = {
    "11": {"name": "Operational Amplifier", "category_id": 3, "category_name": "Amplifiers/Comparators"},
    "13": {"name": "Multilayer Ceramic Capacitors MLCC - SMD/SMT", "category_id": 2, "category_name": "Capacitors"},
}


def catalog_part(lcsc, mpn, maker, package, stock, library="e", sub=11, price=0.01, attrs=(), no_datasheet=0,
                 pcba=0):
    return {"l": lcsc, "m": mpn, "f": maker, "p": package, "s": stock, "t": library, "c": sub, "$": price,
            "d": f"{mpn} description", "a": [list(a) for a in attrs], "x": pcba, "n": no_datasheet}


CATALOG = [
    catalog_part("C7950", "LM358DR2G", "onsemi", "SOIC-8", 495224, "b", price=0.054,
                 attrs=[("Number of Channels", "2"), ("Gain Bandwidth Product (GBP)", "1MHz")]),
    catalog_part("C5252902", "LM358", "MSKSEMI", "SOP-8", 338940, price=0.039, no_datasheet=1, pcba=2),
    catalog_part("C1525", "CL05B104KO5NNNC", "Samsung Electro-Mechanics", "0402", 37_286_642, "b", sub=13,
                 price=0.0029, attrs=[("Capacitance", "100nF"), ("Temperature Coefficient", "X7R")]),
]
SOLD_OUT = {"C2040": {"l": "C2040", "g": "2026-11-16", "s": 15, "$": 0.7, "t": "e", "c": 11, "m": "RP2040",
                      "f": "Raspberry Pi", "p": "LQFN-56(7x7)", "d": "Dual-core RP2040 microcontroller"}}
TIERS = {"C7950": "1:0.054,10:0.05,100:0.045,1000:0.04"}
SYMBOL, FOOTPRINT = "a" * 32, "b" * 32
LIVE_ONLY = ("min_order", "reel_qty", "datasheet", "lcsc_url")


def _build(root: Path, tiers: bool) -> ComponentDatabase:
    write_catalog_category(root, "amplifiers", CATALOG[:2])
    write_catalog_category(root, "capacitors", CATALOG[2:])
    (root / "subcategories.json").write_text(json.dumps(SUBCATEGORIES), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps(
        {"scraped_at": "2026-11-19T15:15:56.402952+00:00", "prices_updated_at": "2026-11-16T20:00:00+00:00",
         "categories": {}}), encoding="utf-8")
    write_sold_out(root / "catalog", SOLD_OUT)
    if tiers:
        write_price_tiers(root / "catalog" / PRICE_TIERS_FILE, TIERS, "2026-11-19T15:10:00+00:00")
    build_database(root, root / "c.db", verbose=False)
    return ComponentDatabase(db_path=root / "c.db", data_dir=root)


@pytest.fixture(scope="module")
def databases(tmp_path_factory):
    dbs = {"tiers": _build(tmp_path_factory.mktemp("tiers"), True),
           "plain": _build(tmp_path_factory.mktemp("plain"), False)}
    yield dbs
    for db in dbs.values():
        db.close()  # before the temporary directories go (Windows)


class Reply:
    """A wafer-like reply."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.retries = self.rotations = 0
        self.challenge_type = None

    def raise_for_status(self):
        if self.status_code >= 400:
            raise WaferHTTPError(self.status_code, "https://jlcpcb.com")

    def json(self):
        return self._payload


class Session:
    """A fake wafer session: answer() gives each reply, or an exception to raise."""

    def __init__(self, answer):
        self.answer = answer
        self.sent = 0

    async def post(self, url, json=None, **kwargs):
        self.sent += 1
        reply = self.answer(json)
        if isinstance(reply, BaseException):
            raise reply
        return reply

    get = post


def refuse(body):
    raise AssertionError(f"an upstream request was made: {body}")


def live_item(code, stock=7):
    """A JLCPCB search item with what makes no further request: specs and the maker's datasheet
    (no LCSC fallback); the seed answers the footprint (no EasyEDA request)."""
    return {"componentCode": code, "componentModelEn": "LM358DR2G", "componentBrandEn": "onsemi",
            "componentSpecificationEn": "SOIC-8", "stockCount": stock, "componentLibraryType": "base",
            "preferredComponentFlag": False, "firstSortName": "Operational Amplifier",
            "secondSortName": "Amplifiers/Comparators", "firstSortId": 11, "componentProductType": 0,
            "componentPrices": [{"startNumber": 1, "productPrice": 0.06}, {"startNumber": 100, "productPrice": 0.05}],
            "attributes": [{"attribute_name_en": "Number of Channels", "attribute_value_name": "2"}],
            "dataManualUrl": f"https://www.lcsc.com/datasheet/{code}.pdf",
            "dataManualOfficialLink": "https://www.onsemi.com/pdf/datasheet/lm358-d.pdf",
            "minPurchaseNum": 5, "encapsulationNumber": 2500, "lcscGoodsUrl": f"https://www.lcsc.com/product-detail/{code}.html"}


def found(code, stock=7):
    return Reply({"code": 200, "data": {"componentPageInfo": {"list": [live_item(code, stock)], "total": 1}}})


NOT_FOUND = Reply({"code": 200, "data": {"componentPageInfo": {"list": [], "total": 0}}})

# Each way the live lookup can fail ("JLCPCB didn't answer"), and the error today's reply gives
FAILURES = {
    "waf": (lambda: ChallengeDetected("cloudflare", "https://jlcpcb.com", 403),
            "JLCPCB blocked request with WAF challenge — try again later"),
    "rate_limited": (lambda: RateLimited("https://jlcpcb.com"), "JLCPCB rate limited — try again later"),
    "empty": (lambda: EmptyResponse("https://jlcpcb.com", 200), "JLCPCB returned empty response — try again later"),
    "connection": (lambda: ConnectionFailed("https://jlcpcb.com", "reset"), "JLCPCB connection failed — try again later"),
    "timeout": (lambda: WaferTimeout("https://jlcpcb.com", 30), "JLCPCB request timed out — try again later"),
    # Any other wafer failure (too many redirects, an oversized reply) is no answer either
    "other_wafer": (lambda: WaferError("too many redirects"), "JLCPCB connection failed — try again later"),
    "http": (lambda: Reply({}, 503), "JLCPCB returned HTTP 503 — try again later"),
    "api": (lambda: Reply({"code": 500, "message": "busy"}), "JLCPCB API error: busy"),
    # A 200 that isn't a JSON object (an error page): our own message, not the decoder's
    "not_json": (lambda: NotJson(), "JLCPCB returned an unreadable response — try again later"),
    "not_object": (lambda: Reply(["busy"]), "JLCPCB returned an unreadable response — try again later"),
}


class NotJson(Reply):
    def __init__(self):
        super().__init__(None)

    def json(self):
        return json.loads("<html>busy</html>")


@pytest.fixture
async def env(databases, monkeypatch):
    """A real client whose JLCPCB, LCSC and EasyEDA sessions are fakes (refusing by default), the
    footprint seed answering for C7950 only, a database chosen by use(), and short datasheet links
    as on pcbparts.dev. Async so the event loop exists before sockets are blocked (Windows)."""
    client = JLCPCBClient()
    client._jlcpcb_session = Session(refuse)
    client._lcsc_session = client._easyeda_products_session = Session(refuse)
    client.set_categories([{"id": 3, "name": "Amplifiers/Comparators", "subcategories": []}])
    client.set_easyeda_seed(lambda code: FootprintAnswer(True, SYMBOL, FOOTPRINT, 1.0) if code == "C7950" else None)
    monkeypatch.setattr(server, "_client", client)
    monkeypatch.setattr(server, "_datasheet_link_base", lambda: "https://pcbparts.dev")
    state = types.SimpleNamespace(client=client)

    def use(name="tiers"):
        monkeypatch.setattr(server, "get_db", lambda: databases[name])
        return databases[name]

    def answer(handler):
        client._jlcpcb_session = Session(handler)
        return client._jlcpcb_session

    state.use, state.answer = use, answer
    use()
    with offline():
        yield state


def lookups(tool="jlc_get_part"):
    days = stats.usage.summary()["days"]
    return (days[0]["lcsc_lookups"] or {}).get(tool) if days else None


def counted(**events):
    return {event: events.get(event, 0) for event in LCSC_LOOKUP_EVENTS}


def upstream():
    days = stats.usage.summary()["days"]
    return days[0]["upstream"] if days else {}


def outcome(reply):
    return server._call_outcome(types.SimpleNamespace(structured_content=reply))


class TestStoredLifecycle:
    @pytest.mark.parametrize("source,raw", [("mouser", MOUSER_NOT_STATED), ("digikey", "Active")])
    async def test_lcsc_and_mpn_parts_include_lifecycle_without_requests(self, env, stored_lifecycle, source, raw):
        now = stored_lifecycle.now()
        stored_lifecycle.put_readings([Reading("LM358DR2G", "ON Semiconductor", source, "active", raw, now)])
        # raw tells Mouser's unstated active from a stated status
        expected = {"status": "active", "raw": raw, "source": source, "observed_at": utc_text(now)}
        single = await server.jlc_get_part(lcsc="C7950")
        by_mpn = await server.jlc_get_part(mpn="LM358DR2G")
        assert single["lifecycle"] == by_mpn["results"][0]["lifecycle"] == expected
        assert upstream() == {} and stats.usage.summary()["days"][0]["distributors"] == {}

    async def test_older_stated_mouser_beats_unstated(self, env, stored_lifecycle):
        now = stored_lifecycle.now()
        stored_lifecycle.put_readings([Reading("LM358DR2G", "onsemi", "mouser", "nrnd", "Not Recommended", now - 86400),
                                       Reading("LM358DR2G", "onsemi / Fairchild", "mouser", "active", MOUSER_NOT_STATED, now)])
        assert (await server.jlc_get_part(lcsc="C7950"))["lifecycle"] == {
            "status": "nrnd", "raw": "Not Recommended", "source": "mouser", "observed_at": utc_text(now - 86400)}

    @pytest.mark.parametrize("kind", ["missing", "other_maker", "unknown", "expired"])
    async def test_no_usable_reading_is_omitted(self, env, stored_lifecycle, kind):
        if kind != "missing":
            stored_lifecycle.put_readings([Reading("LM358DR2G", "Other Maker" if kind == "other_maker" else "onsemi",
                                                   "digikey", "unknown" if kind == "unknown" else "active", "Active",
                                                   stored_lifecycle.now() - (LIFECYCLE_TTL if kind == "expired" else 0))])
        assert "lifecycle" not in await server.jlc_get_part(lcsc="C7950")
        assert "lifecycle" not in (await server.jlc_get_part(mpn="LM358DR2G"))["results"][0]
        assert upstream() == {}

    @pytest.mark.parametrize("fallback", [False, True])
    async def test_live_or_fallback_reply_also_has_store_reading(self, env, stored_lifecycle, fallback):
        now = stored_lifecycle.now()
        stored_lifecycle.put_readings([Reading("LM358DR2G", "onsemi", "digikey", "nrnd", "Not Recommended", now)])
        session = env.answer((lambda body: RateLimited("https://jlcpcb.com")) if fallback else (lambda body: found("C7950")))
        reply = await server.jlc_get_part(lcsc="C7950", live=True)
        assert reply["lifecycle"]["source"] == "digikey" and session.sent == 1
        assert reply.get("live_failed", False) == fallback

    async def test_gone_and_error_rows(self, env, stored_lifecycle):
        stored_lifecycle.put_readings([Reading("RP2040", "Raspberry Pi", "digikey", "active", "Active",
                                               stored_lifecycle.now())])
        by_mpn = await server.jlc_get_part(mpn="RP2040")
        assert by_mpn["results"][0]["gone"] and by_mpn["results"][0]["lifecycle"]["source"] == "digikey"
        assert "lifecycle" not in await server.jlc_get_part(mpn="NOPE123")
        assert "lifecycle" not in server._with_stored_lifecycle([{"lcsc": "C1", "gone": True}])[0]


class TestSnapshotByDefault:
    async def test_answered_from_the_database_alone(self, env):
        reply = await server.jlc_get_part(lcsc=" c7950 ")
        assert upstream() == {}  # no JLCPCB, LCSC or EasyEDA request, not even a cached answer counted
        assert reply == {
            "lcsc": "C7950", "model": "LM358DR2G", "manufacturer": "onsemi", "package": "SOIC-8", "stock": 495224,
            "price": 0.054,
            "prices": [{"qty": "1+", "price": 0.054}, {"qty": "10+", "price": 0.05}, {"qty": "100+", "price": 0.045},
                       {"qty": "1000+", "price": 0.04}],
            "library_type": "basic", "preferred": False, "category": "Amplifiers/Comparators",
            "subcategory": "Operational Amplifier", "subcategory_id": 11, "mounting_type": "smd",
            "specs": {"Number of Channels": "2", "Gain Bandwidth Product (GBP)": "1MHz"}, "pcba_type": "economic",
            "data_source": {"kind": "snapshot", "provider": "JLCPCB", "observed_at": SCRAPED_AT},
            "datasheet_pdf": "https://pcbparts.dev/mcp/datasheet/C7950",
            "has_easyeda_footprint": True, "easyeda_symbol_uuid": SYMBOL, "easyeda_footprint_uuid": FOOTPRINT,
            "data_as_of": SCRAPED_AT, "prices_as_of": "2026-11-16T20:00:00Z",
            "price_tiers_as_of": "2026-11-19T15:10:00Z", "hint": server._SNAPSHOT_HINT}
        assert not set(LIVE_ONLY) & set(reply)
        assert all(field in reply["hint"] for field in ("live=true", "min_order", "reel_qty", "lcsc_url"))
        assert outcome(reply) == "ok" and lookups() == counted(snapshot=1)

    async def test_without_price_tiers_it_goes_live(self, env):
        """A server without price tiers would answer with the 1-piece price alone: the default goes
        live, as before 0.10.2, so the reply has every tier."""
        env.use("plain")
        jlcpcb = env.answer(lambda body: found(body["keyword"]))
        reply = await server.jlc_get_part(lcsc="C7950")
        assert jlcpcb.sent == 1 and reply["data_source"]["kind"] == "live_lookup"
        assert reply["prices"] == [{"qty": "1+", "price": 0.06}, {"qty": "100+", "price": 0.05}]
        assert "hint" not in reply and lookups() == counted(live=1)

    async def test_without_price_tiers_a_failed_live_lookup_falls_back(self, env):
        env.use("plain")
        jlcpcb = env.answer(lambda body: RateLimited("https://jlcpcb.com"))
        reply = await server.jlc_get_part(lcsc="C7950")
        assert jlcpcb.sent == 1 and reply["live_failed"] is True and reply["data_source"]["kind"] == "snapshot"
        assert reply["prices"] == [{"qty": "1+", "price": 0.054}] and reply["price_tiers_as_of"] is None
        assert lookups() == counted(fallback=1)

    async def test_with_price_tiers_no_request(self, env):
        jlcpcb = env.answer(refuse)
        reply = await server.jlc_get_part(lcsc="C1525")
        assert jlcpcb.sent == 0 and upstream() == {} and reply["data_source"]["kind"] == "snapshot"
        assert reply["price_tiers_as_of"] == "2026-11-19T15:10:00Z" and lookups() == counted(snapshot=1)

    async def test_no_datasheet_and_unknown_footprint(self, env):
        """JLCPCB lists no datasheet: no link that would find nothing (no_datasheet says so). A part
        the seed and store don't know has has_easyeda_footprint null, never an EasyEDA request."""
        reply = await server.jlc_get_part(lcsc="C5252902")
        assert "datasheet_pdf" not in reply and reply["no_datasheet"] is True
        assert "live=true" in reply["no_datasheet_note"]
        assert (reply["has_easyeda_footprint"], reply["easyeda_symbol_uuid"], reply["easyeda_footprint_uuid"]) == (
            None, None, None)
        assert reply["pcba_type"] == "standard_only" and reply["specs"] == {}
        assert reply["description"] == "LM358 description" and "live=true" in reply["specs_note"]
        assert upstream() == {}

    async def test_a_live_answer_already_known_gives_the_footprint(self, env):
        env.client._easyeda_cache["C1525"] = (datetime.datetime.now().timestamp(),
                                              {"has_easyeda_footprint": False, "easyeda_symbol_uuid": None,
                                               "easyeda_footprint_uuid": None}, False)
        assert (await server.jlc_get_part(lcsc="C1525"))["has_easyeda_footprint"] is False
        assert "specs_note" in await server.jlc_get_part(lcsc="C1525")  # MLCC DC bias, as the live reply has

    async def test_lcsc_still_wins_over_mpn(self, env):
        reply = await server.jlc_get_part(lcsc="C7950", mpn="LM358")
        assert reply["lcsc"] == "C7950" and "mpn" not in reply and reply["data_source"]["kind"] == "snapshot"

    async def test_mpn_ignores_live(self, env):
        assert await server.jlc_get_part(mpn="LM358DR2G", live=True) == await server.jlc_get_part(mpn="LM358DR2G")
        assert upstream() == {} and lookups() is None

    async def test_not_a_code_is_not_found_without_reading(self, env):
        assert await server.jlc_get_part(lcsc="LM358") == {"error": "Part LM358 not found"}
        assert lookups() is None


class TestGoesLive:
    async def test_live_true(self, env):
        jlcpcb = env.answer(lambda body: found(body["keyword"]))
        reply = await server.jlc_get_part(lcsc="C7950", live=True)
        assert jlcpcb.sent == 1 and reply["data_source"]["kind"] == "live_lookup"
        assert (reply["stock"], reply["min_order"], reply["reel_qty"]) == (7, 5, 2500)
        assert reply["datasheet"] and reply["lcsc_url"] and reply["maker_datasheet"]
        assert reply["prices"] == [{"qty": "1+", "price": 0.06}, {"qty": "100+", "price": 0.05}]
        assert "hint" not in reply and "live_failed" not in reply
        assert lookups() == counted(live=1)

    @pytest.mark.parametrize("code", ["C2040", "C99999"], ids=["gone", "unknown"])
    async def test_not_in_the_snapshot(self, env, code):
        jlcpcb = env.answer(lambda body: found(body["keyword"], stock=3))
        reply = await server.jlc_get_part(lcsc=code)
        assert jlcpcb.sent == 1 and reply["lcsc"] == code and reply["stock"] == 3 and reply["min_order"] == 5
        assert reply["data_source"]["kind"] == "live_lookup" and lookups() == counted(live=1)

    async def test_a_live_not_found_is_the_not_found_error(self, env):
        """JLCPCB answered: the part doesn't exist. Not a failed lookup, so no fallback."""
        env.answer(lambda body: NOT_FOUND)
        assert await server.jlc_get_part(lcsc="C99999") == {"error": "Part C99999 not found"}
        assert await server.jlc_get_part(lcsc="C7950", live=True) == {"error": "Part C7950 not found"}
        assert lookups() == counted(live=2)


class TestFallback:
    @pytest.mark.parametrize("failure", FAILURES)
    async def test_snapshot_part_with_live_true(self, env, failure):
        make, message = FAILURES[failure]
        jlcpcb = env.answer(lambda body: make())
        reply = await server.jlc_get_part(lcsc="C7950", live=True)
        snapshot = await server.jlc_get_part(lcsc="C7950")
        assert jlcpcb.sent == 1
        assert (reply.pop("live_failed"), reply.pop("live_error")) == (True, message)
        assert reply.pop("note") == ("JLCPCB didn't answer, so this is the daily snapshot of 2026-11-19 (stock >= 10 "
                                     "then). Try live again later.")
        assert reply == {key: value for key, value in snapshot.items() if key != "hint"}
        assert outcome(reply) == "ok" and lookups() == counted(snapshot=1, fallback=1)
        # Not cached as a live answer: the next live=true call asks JLCPCB again
        assert "C7950" not in env.client._part_cache
        await server.jlc_get_part(lcsc="C7950", live=True)
        assert jlcpcb.sent == 2

    @pytest.mark.parametrize("failure", FAILURES)
    async def test_gone_part(self, env, failure):
        make, message = FAILURES[failure]
        jlcpcb = env.answer(lambda body: make())
        reply = await server.jlc_get_part(lcsc="C2040")
        assert jlcpcb.sent == 1
        assert reply == {
            "lcsc": "C2040", "model": "RP2040", "manufacturer": "Raspberry Pi", "package": "LQFN-56(7x7)",
            "stock": None, "price": 0.7, "prices": [{"qty": "1+", "price": 0.7}], "library_type": "extended",
            "preferred": False, "category": "Amplifiers/Comparators", "subcategory": "Operational Amplifier",
            "subcategory_id": 11, "mounting_type": "smd", "description": "Dual-core RP2040 microcontroller",
            "gone": True, "gone_since": "2026-11-16", "last_stock": 15,
            "data_source": {"kind": "snapshot", "provider": "JLCPCB", "observed_at": None},
            "data_as_of": SCRAPED_AT, "prices_as_of": "2026-11-16T20:00:00Z",
            "price_tiers_as_of": "2026-11-19T15:10:00Z", "live_failed": True, "live_error": message,
            "note": reply["note"]}
        assert reply["note"].startswith("JLCPCB didn't answer, so this is what the daily snapshot of 2026-11-19 kept")
        assert "2026-11-16" in reply["note"] and "null (unknown)" in reply["note"]
        assert outcome(reply) == "ok" and lookups() == counted(fallback=1)
        await server.jlc_get_part(lcsc="C2040")
        assert jlcpcb.sent == 2  # not cached

    @pytest.mark.parametrize("failure", FAILURES)
    async def test_neither_is_the_error_as_before(self, env, failure):
        make, message = FAILURES[failure]
        env.answer(lambda body: make())
        reply = await server.jlc_get_part(lcsc="C99999")
        assert reply == {"error": message}
        assert outcome(reply) == ("rate_limited" if failure == "rate_limited" else "failed")
        assert lookups() == counted(live_failed=1)

    async def test_a_live_answer_after_a_failure_is_cached_as_before(self, env):
        failing = [False, True]  # popped from the end: a failure, then an answer
        jlcpcb = env.answer(lambda body: FAILURES["timeout"][0]() if failing.pop() else found(body["keyword"]))
        assert (await server.jlc_get_part(lcsc="C7950", live=True))["live_failed"] is True
        live = await server.jlc_get_part(lcsc="C7950", live=True)
        assert "live_failed" not in live and live["stock"] == 7
        assert await server.jlc_get_part(lcsc="C7950", live=True) == live and jlcpcb.sent == 2  # the hour's cache
        assert lookups() == counted(fallback=1, live=2)


class TestStockCheckFallback:
    async def test_one_code(self, env):
        env.answer(lambda body: RateLimited("https://jlcpcb.com"))
        reply = await server.jlc_stock_check(query="C7950", min_stock=0)
        part = await server.jlc_get_part(lcsc="C7950")
        assert {key: reply[key] for key in ("page", "per_page", "total", "total_pages", "has_more")} == {
            "page": 1, "per_page": 20, "total": 1, "total_pages": 1, "has_more": False}
        assert (reply["live_failed"], reply["live_error"]) == (True, "JLCPCB rate limited — try again later")
        assert reply["note"].startswith("JLCPCB didn't answer, so this is the daily snapshot of 2026-11-19")
        assert "filters" not in reply["note"]  # min_stock=0 can't leave a snapshot part out
        row, = reply["results"]
        assert row["stock"] == 495224 and row["prices"] == part["prices"] and row["data_source"]["kind"] == "snapshot"
        assert {key: row[key] for key in row} == {key: part[key] for key in row}  # the part's snapshot fields
        assert outcome(reply) == "ok" and lookups("jlc_stock_check") == counted(fallback=1)

    async def test_gone_code_and_filters(self, env):
        env.answer(lambda body: WaferTimeout("https://jlcpcb.com", 30))
        reply = await server.jlc_stock_check(query="c2040", min_stock=100, library_type="basic")
        assert reply["results"][0]["gone"] is True and reply["results"][0]["stock"] is None
        assert reply["note"].endswith("The filters and min_stock given weren't applied to it.")

    async def test_unknown_code_keeps_the_error(self, env):
        env.answer(lambda body: WaferTimeout("https://jlcpcb.com", 30))
        reply = await server.jlc_stock_check(query="C99999")
        assert reply["error"] == "JLCPCB request timed out — try again later" and "C99999" in reply["hint"]
        assert lookups("jlc_stock_check") == counted(live_failed=1)

    async def test_keyword_query_keeps_the_error_and_points_to_jlc_search(self, env):
        env.answer(lambda body: RateLimited("https://jlcpcb.com"))
        reply = await server.jlc_stock_check(query="LM358")
        assert reply == {"error": "JLCPCB rate limited — try again later", "hint": server._LIVE_SEARCH_DOWN_HINT}
        assert "jlc_search" in reply["hint"] and lookups("jlc_stock_check") is None

    async def test_live_answers_are_counted(self, env):
        env.answer(lambda body: found("C7950"))
        reply = await server.jlc_stock_check(query="C7950")
        assert reply["results"][0]["stock"] == 7 and "live_failed" not in reply
        assert lookups("jlc_stock_check") == counted(live=1)


class TestOnlyAnOutageFallsBack:
    """The fallback means "JLCPCB didn't answer" (JLCPCBUnavailable). A reply that came but
    couldn't be read is that error, logged, as before 0.10.2: never the snapshot marked live_failed
    (a review probe got live_error "year 33658 is out of range" and "Invalid IPv6 URL")."""

    @pytest.fixture
    def unreadable(self, env, monkeypatch):
        env.answer(lambda body: found(body["keyword"]))

        def transform(item, slim=True, with_prices=False):
            raise ValueError("year 33658 is out of range")
        monkeypatch.setattr(env.client, "_transform_part", transform)
        return env

    async def test_get_part(self, unreadable, caplog):
        reply = await server.jlc_get_part(lcsc="C7950", live=True)
        assert reply == {"error": "year 33658 is out of range"}
        assert lookups() == counted(live_failed=1)
        assert "JLCPCB's reply couldn't be read" in caplog.text

    async def test_stock_check(self, unreadable, caplog):
        assert await server.jlc_stock_check(query="C7950") == {"error": "year 33658 is out of range"}
        # A keyword query too: the error alone, without the "didn't answer" hint
        assert await server.jlc_stock_check(query="LM358") == {"error": "year 33658 is out of range"}
        assert lookups("jlc_stock_check") == counted(live_failed=1)
        assert "JLCPCB's reply couldn't be read" in caplog.text

    async def test_other_exceptions_are_raised_and_counted(self, env, monkeypatch):
        async def broken(*args, **kwargs):
            raise KeyError("productPrice")
        monkeypatch.setattr(env.client, "get_part", broken)
        monkeypatch.setattr(env.client, "search", broken)
        with pytest.raises(KeyError):
            await server.jlc_get_part(lcsc="C7950", live=True)
        with pytest.raises(KeyError):
            await server.jlc_stock_check(query="C7950")
        assert lookups() == counted(live_failed=1) and lookups("jlc_stock_check") == counted(live_failed=1)

    @pytest.mark.parametrize("failure", FAILURES)
    async def test_every_outage_is_one_class(self, env, failure):
        """Each FAILURES case raises JLCPCBUnavailable (a ValueError, so other tools' handlers still
        catch it), with the message the replies give."""
        assert issubclass(JLCPCBUnavailable, ValueError)
        env.answer(lambda body: FAILURES[failure][0]())
        with pytest.raises(JLCPCBUnavailable) as raised:
            await env.client._request("https://jlcpcb.com", {"keyword": "C7950"})
        assert str(raised.value) == FAILURES[failure][1]


class TestMalformedLinks:
    """One malformed datasheet link in JLCPCB's listing failed the whole part (a ValueError or
    OverflowError out of get_part): the link is left out instead, as for any unreadable expiry."""

    @pytest.mark.parametrize("extra, kept", [
        ({"dataManualFileAccessIdUrl":
          "https://jlc.example/1.pdf?x-oss-date=20261119T150000Z&x-oss-expires=1000000000000"}, "maker_datasheet"),
        ({"dataManualFileAccessIdUrl": "https://[jlc.example/1.pdf?Expires=99999999999"}, "maker_datasheet"),
        ({"dataManualFileAccessIdUrl": "https://jlc.example/1.pdf?Expires=1e400"}, "maker_datasheet"),
        ({"dataManualFileAccessIdUrl": "https://jlc.example/1.pdf?Expires=nan"}, "maker_datasheet"),
        ({"dataManualOfficialLink": "https://[maker.example/x.pdf"}, None),
        ({"dataManualOfficialLink": 12345}, None),  # not even text
        ({"dataManualOfficialLink": ["https://maker.example/x.pdf"]}, None),
    ], ids=["year", "ipv6", "inf", "nan", "maker_ipv6", "maker_number", "maker_list"])
    async def test_left_out(self, env, extra, kept):
        env.answer(lambda body: Reply({"code": 200, "data": {"componentPageInfo": {
            "list": [{**live_item(body["keyword"]), **extra}]}}}))
        if kept is None:  # no maker link and no JLCPCB PDF: LCSC is asked for its copy (it has none)
            env.client._lcsc_session = Session(lambda body: Reply({"code": 200, "result": None}))
        reply = await server.jlc_get_part(lcsc="C7950", live=True)
        assert reply["data_source"]["kind"] == "live_lookup" and "datasheet_pdf" not in reply
        maker = "https://www.onsemi.com/pdf/datasheet/lm358-d.pdf"
        assert (reply.get("maker_datasheet") == maker) is (kept is not None)
        assert lookups() == counted(live=1)


def bom_tool_reads(reply):
    """Modelled on the BOM tool's parser: it takes a root object when lcsc is a string; stock that
    isn't an integer (missing or null) is unknown; tiers come from prices or price_breaks (qty "N+"
    or an integer, numeric price); price is the scalar 1-piece price."""
    assert isinstance(reply, dict) and isinstance(reply.get("lcsc"), str)
    stock = reply.get("stock")
    tiers = reply.get("prices") or reply.get("price_breaks") or []
    return {"lcsc": reply["lcsc"], "model": reply["model"], "manufacturer": reply["manufacturer"],
            "stock": stock if isinstance(stock, int) and not isinstance(stock, bool) else "unknown",
            "library_type": reply["library_type"], "preferred": reply["preferred"],
            "tiers": [(int(str(t["qty"]).rstrip("+")), float(t["price"])) for t in tiers],
            "price": reply["price"] if isinstance(reply.get("price"), (int, float)) else None}


async def test_the_bom_tool_reads_the_snapshot_and_gone_replies(env):
    snapshot = bom_tool_reads(await server.jlc_get_part(lcsc="C7950"))
    assert snapshot == {"lcsc": "C7950", "model": "LM358DR2G", "manufacturer": "onsemi", "stock": 495224,
                        "library_type": "basic", "preferred": False,
                        "tiers": [(1, 0.054), (10, 0.05), (100, 0.045), (1000, 0.04)], "price": 0.054}
    env.answer(lambda body: ConnectionFailed("https://jlcpcb.com", "reset"))
    assert bom_tool_reads(await server.jlc_get_part(lcsc="C7950", live=True)) == snapshot
    gone = bom_tool_reads(await server.jlc_get_part(lcsc="C2040"))
    assert gone == {"lcsc": "C2040", "model": "RP2040", "manufacturer": "Raspberry Pi", "stock": "unknown",
                    "library_type": "extended", "preferred": False, "tiers": [(1, 0.7)], "price": 0.7}
    env.use("plain")
    assert bom_tool_reads(await server.jlc_get_part(lcsc="C1525"))["tiers"] == [(1, 0.0029)]


async def test_live_is_an_argument_clients_can_send(env):
    async with Client(server.mcp) as client:
        tool = next(t for t in await client.list_tools() if t.name == "jlc_get_part")
        assert tool.inputSchema["properties"]["live"] == {
            "default": False, "description": tool.inputSchema["properties"]["live"]["description"], "type": "boolean"}
        server._client = env.client  # the lifespan made its own; this test's fakes refuse requests
        reply = (await client.call_tool("jlc_get_part", {"lcsc": "C7950"})).structured_content
        assert reply["data_source"]["kind"] == "snapshot"


class TestHealth:
    @pytest.mark.parametrize("hours, age, stale", [(29.94, 29.9, False), (30.0, 30.0, False), (30.06, 30.1, True)])
    async def test_age_and_stale(self, monkeypatch, hours, age, stale):
        scraped = datetime.datetime(2026, 11, 19, 15, 15, 56, tzinfo=datetime.timezone.utc).timestamp()
        monkeypatch.setattr(server, "_snapshot_as_of", SCRAPED_AT)
        monkeypatch.setattr(server, "_health_clock", lambda: scraped + hours * 3600)
        response = await server.health(None)
        body = json.loads(response.body)
        assert body["snapshot"] == {"data_as_of": SCRAPED_AT, "age_hours": age, "stale": stale}
        assert response.status_code == 200 and body["status"] == "healthy"  # stale is information only

    @pytest.mark.parametrize("value", [None, "not a time"])
    async def test_unknown_time(self, monkeypatch, value):
        monkeypatch.setattr(server, "_snapshot_as_of", value)
        body = json.loads((await server.health(None)).body)
        assert body["snapshot"] == {"data_as_of": value, "age_hours": None, "stale": None}

    async def test_read_at_startup(self, databases, monkeypatch):
        monkeypatch.setattr(server, "get_db", lambda: databases["tiers"])
        monkeypatch.setattr(server, "_snapshot_as_of", None)
        with offline():
            async with Client(server.mcp):
                assert json.loads((await server.health(None)).body)["snapshot"]["data_as_of"] == SCRAPED_AT


class TestStats:
    class Clock:
        def __init__(self):
            self.now = datetime.datetime(2026, 11, 19, 20, 0, tzinfo=datetime.timezone.utc).timestamp()

        def __call__(self):
            return self.now

    def test_counted_saved_and_loaded(self, tmp_path):
        clock = self.Clock()
        usage = UsageStats(clock=clock)
        usage.open(tmp_path / "usage.json")
        for tool, event in (("jlc_get_part", "snapshot"), ("jlc_get_part", "snapshot"), ("jlc_get_part", "live"),
                            ("jlc_get_part", "fallback"), ("jlc_stock_check", "live_failed"),
                            ("jlc_search", "snapshot"), ("jlc_get_part", "exploded")):  # the last two aren't counted
            usage.record_lcsc_lookup(tool, event)
        day = usage.summary()["days"][0]["lcsc_lookups"]
        assert day == {"jlc_get_part": counted(snapshot=2, live=1, fallback=1),
                       "jlc_stock_check": counted(live_failed=1)}
        usage.save()
        again = UsageStats(clock=clock)
        again.open(tmp_path / "usage.json")
        assert again.summary()["days"][0]["lcsc_lookups"] == day
        assert again.summary()["totals"]["lcsc_lookups"] == day
        clock.now += 86400
        again.record_lcsc_lookup("jlc_get_part", "snapshot")
        assert again.summary()["totals"]["lcsc_lookups"]["jlc_get_part"] == counted(snapshot=3, live=1, fallback=1)

    def test_days_before_it_show_null(self, tmp_path):
        """A day saved by 0.10.1 has none: null, not zero lookups, until this version counts one."""
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-11-18": {"tools": {}, "restarts": 1},
                                             "2026-11-19": {"tools": {}, "restarts": 1, "newer": [1]}}}),
                        encoding="utf-8")
        usage = UsageStats(clock=self.Clock())
        usage.open(path)
        assert [d["lcsc_lookups"] for d in usage.summary()["days"]] == [None, None]
        usage.record_lcsc_lookup("jlc_get_part", "live")
        today, yesterday = usage.summary()["days"]
        assert today["lcsc_lookups"] == {"jlc_get_part": counted(live=1)} and yesterday["lcsc_lookups"] is None
        usage.save()
        saved = json.loads(path.read_text(encoding="utf-8"))["days"]
        assert saved["2026-11-19"]["newer"] == [1] and saved["2026-11-18"]["lcsc_lookups"] is None

    async def test_counted_through_the_tools(self, env):
        """Each call counts once, in the per-tool outcome arithmetic too (a fallback is ok)."""
        async with Client(server.mcp) as client:
            server._client = env.client
            env.answer(lambda body: RateLimited("https://jlcpcb.com"))
            for arguments in ({"lcsc": "C7950"}, {"lcsc": "C7950", "live": True}, {"lcsc": "C2040"},
                              {"lcsc": "C99999"}):
                await client.call_tool("jlc_get_part", arguments, raise_on_error=False)
        day = stats.usage.summary()["days"][0]
        assert day["lcsc_lookups"]["jlc_get_part"] == counted(snapshot=1, fallback=2, live_failed=1)
        tools = day["tools"]["jlc_get_part"]
        assert (tools["calls"], tools["ok"], tools["rate_limited"]) == (4, 3, 1)
