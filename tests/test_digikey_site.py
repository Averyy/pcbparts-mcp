"""0.10.4: DigiKey lookups without API credentials (digikey_site.py) and their wiring into
DigiKeyClient, part_lifecycle and the server. No network: answers recorded from the site on
2026-11-20 (tests/fixtures/digikey_site/answers.json, trimmed to the fields read), fake sessions and
fake clocks."""

import asyncio
import json
import logging
import math
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
import wafer

import pcbparts_mcp.server as server
from pcbparts_mcp import stats
from pcbparts_mcp.cache import AddressDailyQuota, DailyQuota, Pacer, QuotaPool
from pcbparts_mcp.digikey import DigiKeyClient, DigiKeyError
from pcbparts_mcp.digikey_site import (
    BASE_URL, AddressCapReached, DIGIKEY_SITE_PAUSE, DigiKeySite, SiteFailed, SiteUnavailable, decode_state, encode_state, lz_decode, lz_encode,
    parse_detail,
)
from pcbparts_mcp.digikey_site import _new_session as _wafer_session  # the real one: conftest swaps it per test
from pcbparts_mcp.distributor_store import DistributorStore
from pcbparts_mcp.lifecycle import Entry, LifecycleLookup
from pcbparts_mcp.mouser import MouserClient

ANSWERS = json.loads((Path(__file__).parent / "fixtures" / "digikey_site" / "answers.json").read_text(encoding="utf-8"))
NOW = 1_795_003_200.0  # 2026-11-18 12:00 UTC


class Clock:
    def __init__(self, now: float = NOW):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class Reply:
    """A wafer-like reply."""

    def __init__(self, status=200, body=None, content_type="application/json; charset=utf-8", raw=None,
                 challenge_type=None):
        self.status_code = status
        self.headers = {"content-type": content_type} if content_type else {}
        self._body = body
        self.content = raw if raw is not None else (b"" if body is None else json.dumps(body).encode("utf-8"))
        self.challenge_type = challenge_type
        self.retries = 0
        self.rotations = 0

    def json(self):
        return json.loads(self.content) if self._body is None else self._body

    @property
    def text(self):
        return self.content.decode("utf-8")


def recorded(path: str) -> Reply:
    answer = ANSWERS[path]
    return Reply(answer["status"], answer["body"], answer["content_type"])


class Session:
    """Serves the recorded answers by request path. script: path prefix -> list of replies (or
    exceptions) given first, in order. Records every path asked."""

    def __init__(self, script=None):
        self.script = {prefix: list(replies) for prefix, replies in (script or {}).items()}
        self.paths: list[str] = []
        self.headers: list[dict] = []

    async def get(self, url, **kwargs):
        assert url.startswith(BASE_URL)
        path = url[len(BASE_URL):]
        self.paths.append(path)
        self.headers.append(kwargs.get("headers") or {})
        for prefix, replies in self.script.items():
            if path.startswith(prefix) and replies:
                reply = replies.pop(0)
                if isinstance(reply, Exception):
                    raise reply
                return reply
        if path not in ANSWERS:
            raise AssertionError(f"no recorded answer for {path}")
        return recorded(path)

    def kinds(self) -> list[str]:
        return [path.split("?")[0].split("/")[1] for path in self.paths]


@pytest.fixture
def clock(monkeypatch):
    from pcbparts_mcp import digikey_site
    clock = Clock()

    async def wait_for(awaitable, timeout):
        if timeout <= 0:
            awaitable.close()
            raise TimeoutError
        started = clock()
        result = await awaitable
        if clock() - started > timeout:
            raise TimeoutError
        return result

    # Production deadlines must not depend on how long Windows schedules a test task.
    monkeypatch.setattr(digikey_site, "asyncio", SimpleNamespace(**(vars(asyncio) | {"wait_for": wait_for})))
    return clock


def make_site(clock, session=None, **kwargs):
    """A DigiKeySite on the fake clock; its pacer's sleeps move the clock on."""
    session = session or Session()

    async def sleep(seconds):
        clock.advance(seconds)

    site = DigiKeySite(session_factory=lambda: session, clock=clock, sleep=sleep, **kwargs)
    return site, session


# --- lz-string, the site's state parameter ---

def test_state_encoding_is_the_sites():
    """DigiKey's own redirect for SMAJ36CA carries this state for {"2": ["SMAJ36CA"]}."""
    assert encode_state({"2": ["SMAJ36CA"]}) == "N4IgTCBcDaIMoFkCCApAzANgMJJAXQF8g"
    assert decode_state("N4IgTCBcDaIMoFkCCApAzANgMJJAXQF8g") == {"2": ["SMAJ36CA"]}
    for text in ("", "a", '{"9":[{"id":276658,"productId":276658}]}', "ab" * 300, "B2B-PH-K-S(LF)(SN)"):
        assert lz_decode(lz_encode(text)) == text
    assert decode_state("not lz-string!") is None


# --- lookups (recorded answers) ---

async def test_two_makers_most_stock_first_with_every_packaging(clock):
    site, session = make_site(clock)
    answer = await site.lookup("LM358DR")
    ti, rohm = answer.results
    assert [r["manufacturer"] for r in answer.results] == ["Texas Instruments", "Rohm Semiconductor"]
    assert ti == {
        "source": "digikey", "part_number": "296-LM358DRCT-ND", "mfr_part_number": "LM358DR",
        "manufacturer": "Texas Instruments", "description": "IC OP AMP 2CH 8-SOIC", "category": "Integrated Circuits (ICs)",
        "stock": 56827, "price": 0.26, "price_breaks": [
            {"qty": 1, "price": 0.26}, {"qty": 10, "price": 0.175}, {"qty": 25, "price": 0.1544}, {"qty": 100, "price": 0.1322},
            {"qty": 250, "price": 0.12156}, {"qty": 500, "price": 0.11518}, {"qty": 1000, "price": 0.10991}],
        "datasheet_url": "https://www.ti.com/general/docs/suppproductinfo.tsp?distId=10&gotoUrl=https%3A%2F%2Fwww.ti.com%2Flit%2Fgpn%2Flm358",
        "product_url": "https://www.digikey.com/en/products/detail/texas-instruments/LM358DR/276658",
        "rohs": "ROHS3 Compliant", "lifecycle": "Active", "lifecycle_status": "active", "parameters": ti["parameters"],
        "min_qty": 1, "currency": "USD", "packaging": "Cut Tape (CT)",
        # The site's one "Cut Tape (CT) & Digi-Reel" row, rebuilt as the API's two packagings
        "other_packaging": [
            {"part_number": "296-LM358DRDKR-ND", "packaging": "Digi-Reel®", "min_qty": 1, "price": 0.26, "reel_fee": 7.0},
            {"part_number": "296-LM358DRTR-ND", "packaging": "Tape & Reel (TR)", "min_qty": 2500, "price": 0.10436}]}
    # Parameters leave out what other fields carry (maker, series, packaging, status)
    assert ti["parameters"]["Amplifier Type"] == "Standard (General Purpose)"
    assert not {"Mfr", "Manufacturer", "Series", "Packaging", "Part Status", "Base Product Number"} & set(ti["parameters"])
    assert (rohm["lifecycle"], rohm["lifecycle_status"]) == ("Not For New Designs", "nrnd")
    assert sorted(answer.statuses) == [("LM358DR", "Rohm Semiconductor", "Not For New Designs", None),
                                       ("LM358DR", "Texas Instruments", "Active", None)]
    assert answer.product_ids == [276658, 1878950]
    assert session.kinds() == ["suggestions", "detail-page", "detail-page"]  # two exact: no search
    assert session.headers[0] == {"lang": "en", "site": "US", "x-currency": "USD", "authorization": "Bearer",
                                  "accept": "application/json, text/plain, */*"}


async def test_marketplace_maker_and_no_rohs_row(clock):
    site, _ = make_site(clock)
    answer = await site.lookup("AO3400A")
    assert [r["manufacturer"] for r in answer.results] == ["Alpha & Omega Semiconductor Inc.", "GOODWORK", "UMW"]
    goodwork = answer.results[1]
    assert goodwork["marketplace"] is True and goodwork["rohs"] == "Unknown" and goodwork["min_qty"] == 3000


async def test_a_resellers_offer_is_a_marketplace_packaging_of_the_product(clock):
    """SN74V283-10PZA: TI's product (obsolete, no price of its own) with Rochester's stock, as the
    API answers it: Rochester's packaging picked, its stock counted, TI's number listed beside it."""
    site, _ = make_site(clock)
    (part,) = (await site.lookup("SN74V283-10PZA")).results
    assert {k: part[k] for k in ("part_number", "packaging", "min_qty", "price", "stock", "marketplace", "lifecycle")} == {
        "part_number": "2156-SN74V283-10PZA-ND", "packaging": "Bulk", "min_qty": 8, "price": 36.1, "stock": 387,
        "marketplace": True, "lifecycle": "Obsolete"}
    assert part["other_packaging"] == [{"part_number": "296-12485-ND", "packaging": "Tray", "min_qty": 1, "price": None}]


async def test_a_part_digikey_no_longer_sells(clock):
    """No prices: cut tape is picked as the API did; no stock; the status still obsolete."""
    site, _ = make_site(clock)
    (part,) = (await site.lookup("C8051F410-GQR")).results
    assert (part["part_number"], part["packaging"], part["price"], part["price_breaks"], part["stock"]) == (
        "336-4517-1-ND", "Cut Tape (CT)", None, [], 0)
    assert [o["part_number"] for o in part["other_packaging"]] == ["336-4517-2-ND", "336-4517-6-ND"]


async def test_last_time_buy_date(clock):
    site, _ = make_site(clock)
    (part,) = (await site.lookup("AD7747ARUZ")).results
    assert (part["lifecycle_status"], part["last_buy_date"]) == ("last_time_buy", "2027-07-29")
    assert (await site.lookup("AD7747ARUZ")).statuses == [("AD7747ARUZ", "Analog Devices Inc.", "Last Time Buy", "2027-07-29")]


async def test_discontinued_at_digikey_says_nothing_of_the_maker(clock):
    site, _ = make_site(clock)
    nxp = next(r for r in (await site.lookup("74AHC14D,118")).results if r["manufacturer"] == "NXP USA Inc.")
    assert (nxp["lifecycle"], nxp["lifecycle_status"], nxp["price"], nxp["packaging"]) == (
        "Discontinued at DigiKey", "unknown", None, "Tape & Reel (TR)")


async def test_a_digikey_part_number(clock):
    site, _ = make_site(clock)
    (part,) = (await site.lookup("497-6063-ND")).results
    assert (part["mfr_part_number"], part["part_number"]) == ("STM32F103C8T6", "497-6063-ND")


async def test_jst_endings_through_the_search(clock):
    """DigiKey lists B2B-PH-K-S(LF)(SN) as B2B-PH-K-S: the product list has no exact match, the
    search's product page has it, and the JST rule accepts it."""
    site, session = make_site(clock)
    (part,) = (await site.lookup("B2B-PH-K-S(LF)(SN)")).results
    assert (part["mfr_part_number"], part["manufacturer"]) == ("B2B-PH-K-S", "JST Sales America Inc.")
    assert session.kinds() == ["suggestions", "result-page", "detail-page"]


async def test_not_listed_and_near_matches(clock):
    """TP4056: the search sends a category to itself, so nothing (and no endless hops); MA2C700A:
    the search's product page is MA2C700A0F, rejected."""
    site, session = make_site(clock)
    assert (await site.lookup("TP4056")).results == []
    assert session.kinds() == ["suggestions", "result-page", "filter-page", "filter-page"]
    assert (await site.lookup("MA2C700A")).results == []


async def test_many_makers_reads_every_status_and_replies_ten(clock):
    """SMAJ36CA: 13 makers in the product list, a 14th (Meritek) in the search. One comparison
    request gives every status; product pages only for the 10 with most stock."""
    site, session = make_site(clock)
    answer = await site.lookup("SMAJ36CA")
    assert len(answer.results) == 10
    stocks = [r["stock"] for r in answer.results]
    assert stocks == sorted(stocks, reverse=True) and answer.results[0]["manufacturer"] == "MDD"
    assert len(answer.statuses) == 14 and "Meritek" in {maker for _, maker, _, _ in answer.statuses}
    assert session.kinds().count("compare-page") == 1 and session.kinds().count("detail-page") == 10


async def test_statuses_for_many_parts_in_one_comparison(clock):
    """part_lifecycle's path: no prices, one comparison for every product, a page only for the
    Last Time Buy part's date."""
    site, session = make_site(clock)
    found = await site.statuses(["LM358DR", "AD7747ARUZ", "TP4056", "SMAJ36CA", "AO3414", "1-1470364-2"])
    assert found["TP4056"] == []
    assert found["AD7747ARUZ"] == [("AD7747ARUZ", "Analog Devices Inc.", "Last Time Buy", "2027-07-29")]
    assert sorted(found["AO3414"]) == [("AO3414", "Alpha & Omega Semiconductor Inc.", "Not For New Designs", None),
                                       ("AO3414", "GOODWORK", "Active", None)]
    assert len(found["SMAJ36CA"]) == 14
    assert session.kinds().count("compare-page") == 1
    assert session.kinds().count("detail-page") == 1  # AD7747ARUZ's date


def test_gone_and_missing_products():
    """A product DigiKey no longer offers answers isUnavailable (no reading); an id with none, 204."""
    assert parse_detail(ANSWERS["/detail-page/555843"]["body"], 555843) is None


# --- refusals, failures and the pause ---

LM358DR_SUGGESTIONS = "/suggestions?keywordSearch=LM358DR"
F5 = Reply(400, raw=b'"Invalid Request."')


async def test_f5_first_refusal_is_retried_once(clock):
    site, session = make_site(clock, Session({LM358DR_SUGGESTIONS: [F5]}))
    assert len((await site.lookup("LM358DR")).results) == 2
    assert session.kinds()[:2] == ["suggestions", "suggestions"]


@pytest.mark.parametrize("reply", [
    F5,  # twice: the second one is a refusal
    Reply(403, {"error": "no"}),
    Reply(429, {}),
    Reply(200, raw=b"<html>Just a moment...</html>", content_type="text/html"),
    wafer.ChallengeDetected("cloudflare", BASE_URL, 403),
    wafer.RateLimited(BASE_URL, None),
], ids=["f5_twice", "403", "429", "html", "challenge", "rate_limited"])
async def test_a_refusal_pauses_every_lookup(clock, caplog, reply):
    site, session = make_site(clock, Session({LM358DR_SUGGESTIONS: [F5, reply] if reply is F5 else [reply]}))
    with caplog.at_level(logging.ERROR):
        with pytest.raises(SiteUnavailable) as raised:
            await site.lookup("LM358DR")
    assert raised.value.paused and raised.value.sent and raised.value.retry_after == DIGIKEY_SITE_PAUSE
    assert [r.message for r in caplog.records if r.levelno == logging.ERROR][-1].startswith(
        "DigiKey lookups paused for 5 min: ")
    sent = len(session.paths)
    with pytest.raises(SiteUnavailable) as raised:
        await site.lookup("AO3400A")
    assert not raised.value.sent and len(session.paths) == sent  # nothing goes out while paused
    assert site.status()["paused_until"] is not None


async def test_after_a_pause_one_lookup_tests_and_a_second_refusal_doubles(clock):
    site, session = make_site(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {}), Reply(403, {})]}))
    with pytest.raises(SiteUnavailable):
        await site.lookup("LM358DR")
    clock.advance(DIGIKEY_SITE_PAUSE)
    with pytest.raises(SiteUnavailable) as raised:
        await site.lookup("LM358DR")  # the test lookup, refused again
    assert raised.value.retry_after == 2 * DIGIKEY_SITE_PAUSE
    clock.advance(2 * DIGIKEY_SITE_PAUSE)
    assert len((await site.lookup("LM358DR")).results) == 2  # passes: back to normal
    clock.advance(1)
    session.script[LM358DR_SUGGESTIONS] = [Reply(403, {})]
    with pytest.raises(SiteUnavailable) as raised:
        await site.lookup("LM358DR")
    assert raised.value.retry_after == DIGIKEY_SITE_PAUSE  # the doubling started over


async def test_while_one_lookup_tests_the_others_wait_for_it(clock):
    gate = asyncio.Event()
    hold = False

    class Slow(Session):
        async def get(self, url, **kwargs):
            if hold and "keywordSearch=LM358DR" in url:
                await gate.wait()
            return await super().get(url, **kwargs)

    site, session = make_site(clock, Slow({LM358DR_SUGGESTIONS: [Reply(403, {})]}))
    with pytest.raises(SiteUnavailable):
        await site.lookup("LM358DR")
    clock.advance(DIGIKEY_SITE_PAUSE)
    hold = True  # the test lookup's first request waits until released
    testing = asyncio.create_task(site.lookup("LM358DR"))
    await asyncio.sleep(0)
    waiting = asyncio.create_task(site.lookup("AO3400A"))
    for _ in range(5):
        await asyncio.sleep(0)
    assert "/suggestions?keywordSearch=AO3400A&limit=20" not in session.paths  # waits for the test
    gate.set()
    assert len((await testing).results) == 2 and len((await waiting).results) == 3


@pytest.mark.parametrize("reply", [
    Reply(200, {"data": {}}),  # a shape this code doesn't know
    Reply(404, {}),
    Reply(400, {"error": "bad"}),  # a plain 400, not F5's
    Reply(200, {"redirect": {"url": "/en/supplier-centers/x"}}),  # a redirect it doesn't know (the search's)
], ids=["shape", "404", "400", "redirect"])
async def test_an_odd_answer_fails_that_lookup_only(clock, reply):
    """One number's odd answer is that lookup's failure, not a refusal: nothing pauses, and asking
    for that number again and again never pauses the others."""
    script = {"/result-page": [reply] * 5} if "redirect" in reply.content.decode() else {"/suggestions?keywordSearch=TP4056": [reply] * 5}
    site, session = make_site(clock, Session(script))
    for _ in range(5):
        with pytest.raises(SiteFailed):
            await site.lookup("TP4056")
    assert site.status()["paused_until"] is None
    assert len((await site.lookup("LM358DR")).results) == 2


async def test_failures_of_three_different_numbers_in_a_row_pause(clock):
    down = wafer.ConnectionFailed(BASE_URL, "reset")
    site, session = make_site(clock, Session({"/suggestions": [down, Reply(503, {}), down, down, down, down]}))
    for number in ("LM358DR", "AO3400A"):
        with pytest.raises(SiteFailed):
            await site.lookup(number)
    with pytest.raises(SiteUnavailable) as raised:  # the third different number in a row
        await site.lookup("TP4056")
    assert site.status()["paused_until"] is not None
    assert not raised.value.refused  # DigiKey refused nothing: not counted as its refusal


async def test_a_lookup_that_works_resets_the_failure_count(clock):
    down = wafer.WaferTimeout(BASE_URL, 20)
    site, session = make_site(clock, Session({"/suggestions": [down] * 4}))
    for number in ("TP4056", "AO3400A"):
        with pytest.raises(SiteFailed):
            await site.lookup(number)
    await site.lookup("LM358DR")
    session.script["/suggestions"] = [down] * 4
    for number in ("TP4056", "AO3400A"):
        with pytest.raises(SiteFailed):
            await site.lookup(number)
    assert site.status()["paused_until"] is None


# --- concurrency and pacing ---

async def test_at_most_four_requests_in_flight_and_the_rest_wait(clock):
    gate = asyncio.Event()
    in_flight = peak = 0

    class Held(Session):
        async def get(self, url, **kwargs):
            nonlocal in_flight, peak
            in_flight += 1
            peak = max(peak, in_flight)
            await gate.wait()
            in_flight -= 1
            return await super().get(url, **kwargs)

    site, session = make_site(clock, Held(), per_second=1e6)
    tasks = [asyncio.create_task(site.lookup(n)) for n in ("LM358DR", "AO3400A", "497-6063-ND", "AD7747ARUZ",
                                                           "C8051F410-GQR", "74AHC14D,118")]
    for _ in range(10):
        await asyncio.sleep(0)
    assert in_flight == 4
    gate.set()
    await asyncio.gather(*tasks)
    assert peak == 4
    assert stats.usage.summary()["days"][0]["upstream"]["digikey"]["waited"] >= 2


async def test_a_request_that_finds_no_slot_in_time_is_busy_not_a_pause(clock):
    gate = asyncio.Event()

    class Held(Session):
        async def get(self, url, **kwargs):
            await gate.wait()
            return await super().get(url, **kwargs)

    site, _ = make_site(clock, Held(), concurrency=1, slot_wait=0)
    first = asyncio.create_task(site.lookup("LM358DR"))
    await asyncio.sleep(0)
    with pytest.raises(SiteUnavailable) as raised:
        await site.lookup("AO3400A")
    assert not raised.value.paused
    gate.set()
    await first
    assert site.status()["paused_until"] is None


async def test_requests_start_at_most_five_a_second(clock):
    starts = []

    class Timed(Session):
        async def get(self, url, **kwargs):
            starts.append(clock())
            return await super().get(url, **kwargs)

    site, _ = make_site(clock, Timed())
    await asyncio.gather(site.lookup("LM358DR"), site.lookup("AO3400A"))
    assert len(starts) == 7
    assert all(later - earlier >= 0.2 - 1e-9 for earlier, later in zip(starts, starts[1:]))


# --- DigiKeyClient without credentials ---

def keyless_client(clock, session=None, store=None, **site_kwargs):
    site, session = make_site(clock, session, **site_kwargs)
    store = store or DistributorStore(clock=clock)
    return DigiKeyClient(store=store, site=site), session, store


async def test_client_without_credentials_uses_the_site(clock):
    client, session, store = keyless_client(clock)
    try:
        assert client.unmetered and DigiKeyClient("id", "secret", store=store).unmetered is False
        reply = await client.get_part("LM358DR")
        assert [(r["manufacturer"], r["requested"], r["matched_by"]) for r in reply["results"]] == [
            ("Texas Instruments", "LM358DR", "exact"), ("Rohm Semiconductor", "LM358DR", "exact")]
        assert reply["total"] == 2
        stored, _ = store.get_answer("digikey", "LM358DR")
        assert stored == {k: v for k, v in reply.items() if k != "results"} | {"results": [
            {k: v for k, v in r.items() if k not in ("requested", "matched_by")} for r in reply["results"]]}
        assert [r["product_url"].rsplit("/", 1)[1] for r in stored["results"]] == ["276658", "1878950"]
        assert {(r.maker, r.status, r.raw) for r in store.readings("LM358DR")} == {
            ("Texas Instruments", "active", "Active"), ("Rohm Semiconductor", "nrnd", "Not For New Designs")}
        requests = len(session.paths)
        assert (await client.get_part("lm358dr"))["results"][0]["requested"] == "lm358dr"  # stored: no request
        assert len(session.paths) == requests
        day = stats.usage.summary()["days"][0]
        assert day["distributors"]["digikey"] == {"sent": 1, "cached": 1, "rate_limited": 0}
        assert day["upstream"]["digikey"]["sent"] == requests
    finally:
        await client.close()
        store.close()


async def test_not_found_reply_unchanged_and_kept(clock):
    client, session, store = keyless_client(clock)
    try:
        reply = await client.get_part("TP4056")
        assert reply["error"] == "Part not found: TP4056" and "-ND" in reply["hint"]
        assert store.get_answer("digikey", "TP4056")[0] == {"not_found": True}
        assert [(r.source, r.found) for r in store.readings("TP4056")] == [("digikey", False)]
    finally:
        await client.close()
        store.close()


async def test_jst_part_filed_under_the_number_asked(clock):
    client, _, store = keyless_client(clock)
    try:
        reply = await client.get_part("B2B-PH-K-S(LF)(SN)")
        assert reply["results"][0]["matched_by"] == "packing"
        assert [r.mpn for r in store.readings("B2B-PH-K-S(LF)(SN)")] == ["B2B-PH-K-S"]
    finally:
        await client.close()
        store.close()


async def test_paused_reply_and_counts(clock):
    client, _, store = keyless_client(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {})]}))
    try:
        first = await client.lookup("LM358DR")
        assert first.kind == "limited" and first.reply["error"].startswith(
            "DigiKey lookups are paused on this shared server. Try again in 300 s.")
        second = await client.lookup("AO3400A")
        assert second.kind == "limited" and client.retry_after() == 300
        day = stats.usage.summary()["days"][0]
        assert day["distributors"]["digikey"] == {"sent": 1, "cached": 0, "rate_limited": 1}
        limits = day["distributor_limits"]["digikey"]
        assert limits["refusals"]["refused"] == 1 and limits["held_back"]["distributor_refused"] == 1
    finally:
        await client.close()
        store.close()


async def test_a_failed_lookup_is_an_error_not_a_miss(clock):
    client, _, store = keyless_client(clock, Session({"/suggestions": [wafer.ConnectionFailed(BASE_URL, "reset")] * 2}))
    try:
        with pytest.raises(DigiKeyError):
            await client.lookup("LM358DR")
        assert store.get_answer("digikey", "LM358DR") is None
    finally:
        await client.close()
        store.close()


async def test_no_daily_quota_or_address_cap(clock):
    """Without credentials there is no daily quota, and a client built without the per-address day
    has no cap (from 0.10.5 the server passes it: see the address-day tests below)."""
    client, _, store = keyless_client(clock)
    try:
        assert client._quota is None
        for number in ("LM358DR", "AO3400A", "497-6063-ND", "AD7747ARUZ"):
            assert (await client.lookup(number, caller="203.0.113.9")).kind == "found"
    finally:
        await client.close()
        store.close()


async def test_one_lookup_at_a_time_for_a_number(clock):
    gate = asyncio.Event()

    class Held(Session):
        async def get(self, url, **kwargs):
            await gate.wait()
            return await super().get(url, **kwargs)

    client, session, store = keyless_client(clock, Held())
    try:
        first = asyncio.create_task(client.get_part("LM358DR"))
        second = asyncio.create_task(client.get_part("lm358dr"))
        for _ in range(5):
            await asyncio.sleep(0)
        gate.set()
        a, b = await asyncio.gather(first, second)
        assert session.kinds().count("suggestions") == 1
        assert a["results"][0]["requested"] == "LM358DR" and b["results"][0]["requested"] == "lm358dr"
    finally:
        await client.close()
        store.close()


# --- part_lifecycle without DigiKey credentials ---

def mouser_client(store, parts):
    def answer(request):
        numbers = json.loads(request.content)["SearchByPartRequest"]["mouserPartNumber"].split("|")
        sent.append(numbers)
        hits = [p for p in parts if p["ManufacturerPartNumber"] in numbers]
        return httpx.Response(200, json={"Errors": [], "SearchResults": {"NumberOfResult": len(hits), "Parts": hits}})

    sent: list[list[str]] = []
    client = MouserClient(api_key="k", quota=DailyQuota("Mouser", 1000, day_start_hour=6), store=store)
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(answer))
    return client, sent


async def test_lifecycle_asks_digikey_first_then_mouser_for_the_rest(clock):
    client, session, store = keyless_client(clock)
    tp4056 = {"MouserPartNumber": "1-TP4056", "ManufacturerPartNumber": "TP4056", "Manufacturer": "TOPPOWER",
              "Description": "", "Category": "", "AvailabilityInStock": "5", "Min": "1", "PriceBreaks": [],
              "ProductAttributes": []}
    mouser, sent = mouser_client(store, [tp4056])
    try:
        # The parts recorded together (one comparison request for all their products)
        results = await LifecycleLookup(store, mouser, client).answer(
            [Entry({"mpn": "LM358DR", "manufacturer": "Rohm"}, mpn="LM358DR", maker="Rohm"),
             Entry("AD7747ARUZ", mpn="AD7747ARUZ"), Entry("TP4056", mpn="TP4056"), Entry("SMAJ36CA", mpn="SMAJ36CA"),
             Entry("AO3414", mpn="AO3414"), Entry("1-1470364-2", mpn="1-1470364-2")])
        rohm, ltb, toppower, smaj, ao3414, te = results
        assert (ltb["status"], ltb["source"], ltb["last_buy_date"]) == ("last_time_buy", "digikey", "2027-07-29")
        assert (toppower["status"], toppower["source"]) == ("active", "mouser")  # DigiKey doesn't list it
        assert (rohm["status"], rohm["source"], rohm["raw"]) == ("nrnd", "digikey", "Not For New Designs")
        assert len(smaj["makers"]) == 14  # every maker, not only the 10 a lookup's reply lists
        assert {m["manufacturer"]: m["status"] for m in ao3414["makers"]} == {
            "Alpha & Omega Semiconductor Inc.": "nrnd", "GOODWORK": "active"}
        assert (te["status"], te["source"]) == ("obsolete", "digikey")
        assert sent == [["TP4056"]]  # only what DigiKey doesn't list
        assert session.kinds().count("compare-page") == 1
        # Kept: a second call asks nobody
        before = len(session.paths)
        await LifecycleLookup(store, mouser, client).answer([Entry("AD7747ARUZ", mpn="AD7747ARUZ")])
        assert len(session.paths) == before and sent == [["TP4056"]]
    finally:
        await client.close()
        await mouser.close()
        store.close()


async def test_lifecycle_goes_to_mouser_while_digikey_is_paused(clock):
    client, _, store = keyless_client(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {})]}))
    lm358dr = {"MouserPartNumber": "595-LM358DR", "ManufacturerPartNumber": "LM358DR", "Manufacturer": "Texas Instruments",
               "Description": "", "Category": "", "AvailabilityInStock": "5", "Min": "1", "PriceBreaks": [],
               "ProductAttributes": []}
    mouser, sent = mouser_client(store, [lm358dr])
    try:
        (result,) = await LifecycleLookup(store, mouser, client).answer([Entry("LM358DR", mpn="LM358DR")])
        assert (result["source"], result["status"]) == ("mouser", "active") and sent == [["LM358DR"]]
    finally:
        await client.close()
        await mouser.close()
        store.close()


async def test_with_credentials_mouser_stays_first(clock):
    """With API credentials nothing changes: Mouser first, DigiKey's day spared."""
    store = DistributorStore(clock=clock)
    mouser, sent = mouser_client(store, [])
    digikey = DigiKeyClient("id", "secret", quota=QuotaPool([DailyQuota("DigiKey", 1000)]), store=store)
    asked = []
    digikey._http = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={"access_token": "t", "expires_in": 599})
        if "oauth2" in str(request.url) else (asked.append(1), httpx.Response(404))[1]))
    digikey._pacer = Pacer(1e6)
    try:
        await LifecycleLookup(store, mouser, digikey).answer([Entry("ZZTOP1", mpn="ZZTOP1")])
        assert sent == [["ZZTOP1"]] and len(asked) == 1  # Mouser first, then DigiKey for its miss
    finally:
        await digikey.close()
        await mouser.close()
        store.close()


# --- the server ---

@pytest.mark.parametrize("value, on", [("site", True), (" SITE ", True), ("", False), ("api", False), (None, False)])
def test_switched_on_only_by_its_setting(monkeypatch, value, on):
    from pcbparts_mcp import digikey_site
    if value is None:
        monkeypatch.delenv("DIGIKEY_LOOKUP", raising=False)
    else:
        monkeypatch.setenv("DIGIKEY_LOOKUP", value)
    assert digikey_site.enabled() is on


@pytest.mark.parametrize("paused", [False, True], ids=["ready", "paused"])
async def test_server_without_credentials_and_switched_on_builds_the_keyless_client(
        monkeypatch, clock, stats_headers, paused):
    import datetime
    from fastmcp import Client
    from pcbparts_mcp import digikey_site

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 24, 14, tzinfo=datetime.timezone.utc)

    monkeypatch.setattr(digikey_site, "datetime", SimpleNamespace(
        datetime=FixedDateTime, timedelta=datetime.timedelta, timezone=datetime.timezone))
    monkeypatch.setenv("DIGIKEY_LOOKUP", "site")
    monkeypatch.setattr(server, "_digikey_client", None)  # put back after: startup sets the global
    monkeypatch.setattr(server, "_health_clock", lambda: 1795528800)  # 2026-11-24 14:00 UTC
    async with Client(server.mcp):
        assert server._digikey_client is not None and server._digikey_client.unmetered
        assert "digikey" not in server._distributor_quotas  # no daily quota
        server._digikey_client._site, _ = make_site(clock, pause=60)
        if paused:
            server._digikey_client._site._refused("test refusal")
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.create_app()),
                                     base_url="http://localhost") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert "distributor_quota" not in response.json()
            for headers in ({}, {"Authorization": "Bearer wrong"}):
                response = await client.get("/mcp/stats", headers=headers)
                assert response.status_code == 401 and response.json() == {"error": "Unauthorized"}
            response = await client.get("/mcp/stats", headers=stats_headers)
            assert response.status_code == 200
            assert response.json()["distributor_quota"] == {"digikey": {
                "paused_until": "2026-11-24 14:01 UTC" if paused else None,
                "resets_at": "2026-11-25 00:00 UTC",
            }}


async def test_server_without_credentials_by_default_has_no_digikey(monkeypatch):
    """Off unless switched on: an install without credentials has no DigiKey, as before 0.10.4."""
    from fastmcp import Client
    monkeypatch.setattr(server, "_digikey_client", None)  # startup must leave it so
    async with Client(server.mcp):
        assert server._digikey_client is None
        reply = await server.digikey_get_part(part_number="LM358P")
        assert reply["error"].startswith("DigiKey API credentials not configured")
        assert "distributor_quota" not in json.loads((await server.health(None)).body)


async def test_server_with_credentials_uses_the_api(monkeypatch):
    from fastmcp import Client
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "test-id")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "test-secret")
    async with Client(server.mcp):
        assert not server._digikey_client.unmetered and "digikey" in server._distributor_quotas


# --- review fixes (2026-11-20) ---

async def test_a_request_queued_behind_a_refusal_never_goes_out(clock):
    """A lookup's request waiting for a slot when another lookup's request is refused must not be
    sent once the pause has begun."""
    gate = asyncio.Event()

    class Held(Session):
        async def get(self, url, **kwargs):
            await gate.wait()
            return await super().get(url, **kwargs)

    site, session = make_site(clock, Held({LM358DR_SUGGESTIONS: [Reply(403, {})]}), concurrency=1)
    refused = asyncio.create_task(site.lookup("LM358DR"))
    queued = asyncio.create_task(site.lookup("AO3400A"))
    for _ in range(5):
        await asyncio.sleep(0)
    gate.set()
    with pytest.raises(SiteUnavailable):
        await refused
    with pytest.raises(SiteUnavailable) as raised:
        await queued
    assert raised.value.paused and not raised.value.sent and not raised.value.refused
    assert session.kinds() == ["suggestions"] and "LM358DR" in session.paths[0]


async def test_a_refusal_stops_the_rest_of_a_batch(clock):
    """statuses() asks for every number's product list at once: the first refusal cancels the rest."""
    site, session = make_site(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {})]}), concurrency=1)
    with pytest.raises(SiteUnavailable) as raised:
        await site.statuses(["LM358DR", "AD7747ARUZ", "TP4056", "SMAJ36CA", "AO3414", "1-1470364-2"])
    assert raised.value.refused
    assert len(session.paths) == 1


async def test_a_test_lookup_that_fails_leaves_the_next_test_to_one_lookup(clock):
    """After a pause the test lookup fails on the network: the waiting lookups don't all go ahead;
    one of them is the next test and the other waits for it."""
    gate = asyncio.Event()
    hold = False

    class Slow(Session):
        async def get(self, url, **kwargs):
            if hold and "keywordSearch=LM358DR" in url:
                await gate.wait()
            return await super().get(url, **kwargs)

    site, session = make_site(clock, Slow({LM358DR_SUGGESTIONS: [Reply(403, {})] + [wafer.ConnectionFailed(BASE_URL, "reset")] * 2}))
    with pytest.raises(SiteUnavailable):
        await site.lookup("LM358DR")
    clock.advance(DIGIKEY_SITE_PAUSE)
    hold = True
    testing = asyncio.create_task(site.lookup("LM358DR"))
    await asyncio.sleep(0)
    first, second = asyncio.create_task(site.lookup("AO3400A")), asyncio.create_task(site.lookup("497-6063-ND"))
    for _ in range(5):
        await asyncio.sleep(0)
    sent = len(session.paths)
    gate.set()
    with pytest.raises(SiteFailed):
        await testing
    a, b = await asyncio.gather(first, second)
    # One after the other, never interleaved: the second waited for the first (the new test)
    owners = []
    for path in session.paths[sent:]:
        if "LM358DR" in path:  # the failed test lookup's own request, sent once released
            continue
        product = path.rsplit("/", 1)[-1]
        owners.append("a" if "AO3400A" in path or (product.isdigit() and int(product) in a.product_ids) else "b")
    assert owners == sorted(owners) or owners == sorted(owners, reverse=True), owners


def _product(product_id, maker, status, stock, marketplace_only=False, priced=False):
    from pcbparts_mcp.digikey_site import _Product, _Variation
    variation = _Variation(f"{product_id}-ND", "Bulk" if priced else "Tray", 1,
                           [{"qty": 1, "price": 2.0}] if priced else [], marketplace=marketplace_only)
    return _Product(product_id, "X1", maker, status, stock, [variation], marketplace_only,
                    {"description": "", "category": "", "datasheet_url": None, "product_url": None,
                     "rohs": "Unknown", "parameters": {}})


async def test_many_makers_keep_the_makers_own_status_over_a_resellers(clock, monkeypatch):
    """More than ten makers: TI's own listing is obsolete with no stock, Rochester's listing of the
    same part active with stock. TI's status stands (pages are read for both and merged), not the
    reseller's Active."""
    from pcbparts_mcp.digikey_site import _Row
    site, _ = make_site(clock)
    rows = [_Row(1, "X1", "Texas Instruments", "Texas Instruments", "Obsolete", 0, ["1-ND"]),
            _Row(2, "X1", "Texas Instruments", "Rochester Electronics, LLC", "Active", 5000, ["2-ND"])]
    rows += [_Row(10 + i, "X1", f"Maker {i}", f"Maker {i}", "Active", 100, [f"{10 + i}-ND"]) for i in range(11)]
    pages = {1: _product(1, "Texas Instruments", "Obsolete", 0),
             2: _product(2, "Texas Instruments", "Active", 5000, marketplace_only=True, priced=True)}
    pages.update({row.product_id: _product(row.product_id, row.maker, "Active", 100) for row in rows[2:]})
    asked = []

    async def candidates(number):
        return [row.product_id for row in rows], set()

    async def compare(ids):
        return rows

    async def details(ids):
        asked.extend(ids)
        return [pages[i] for i in ids]

    monkeypatch.setattr(site, "_candidates", candidates)
    monkeypatch.setattr(site, "_compare", compare)
    monkeypatch.setattr(site, "_details", details)
    answer = await site.lookup("X1")
    assert {1, 2} <= set(asked)
    ti = next(r for r in answer.results if r["manufacturer"] == "Texas Instruments")
    assert (ti["lifecycle"], ti["stock"], ti["part_number"], ti["marketplace"]) == ("Obsolete", 5000, "2-ND", True)
    assert ("X1", "Texas Instruments", "Obsolete", None) in answer.statuses
    assert len(answer.results) == 10


async def test_a_lookup_that_never_got_a_slot_is_held_back_not_sent(clock):
    gate = asyncio.Event()

    class Held(Session):
        async def get(self, url, **kwargs):
            await gate.wait()
            return await super().get(url, **kwargs)

    client, session, store = keyless_client(clock, Held(), concurrency=1, slot_wait=0)
    try:
        first = asyncio.create_task(client.lookup("LM358DR"))
        await asyncio.sleep(0)
        busy = await client.lookup("AO3400A")
        assert busy.kind == "limited" and busy.reply["error"].startswith("DigiKey lookups are busy")
        gate.set()
        await first
        day = stats.usage.summary()["days"][0]
        assert day["distributors"]["digikey"] == {"sent": 1, "cached": 0, "rate_limited": 1}
        assert day["distributor_limits"]["digikey"]["held_back"]["other"] == 1
        assert day["upstream"]["digikey"]["waited"] == 0  # it never went out
    finally:
        await client.close()
        store.close()


async def test_one_numbers_trouble_in_a_batch_keeps_the_others(clock):
    """A timeout on one number's product list fails that number only; the batch's other answers
    are kept. A Last Time Buy page that fails loses only the date."""
    down = wafer.WaferTimeout(BASE_URL, 20)
    site, session = make_site(clock, Session({"/suggestions?keywordSearch=TP4056": [down] * 2,
                                              "/detail-page/807741": [down] * 2}))
    found = await site.statuses(["LM358DR", "AD7747ARUZ", "TP4056", "SMAJ36CA", "AO3414", "1-1470364-2"])
    assert isinstance(found["TP4056"], SiteFailed)
    assert found["AD7747ARUZ"] == [("AD7747ARUZ", "Analog Devices Inc.", "Last Time Buy", None)]
    assert len(found["SMAJ36CA"]) == 14 and site.status()["paused_until"] is None


async def test_lifecycle_keeps_a_batchs_answers_when_one_number_fails(clock):
    down = wafer.WaferTimeout(BASE_URL, 20)
    client, _, store = keyless_client(clock, Session({"/suggestions?keywordSearch=TP4056": [down] * 2}))
    try:
        answers = await client.lifecycle(["LM358DR", "AD7747ARUZ", "TP4056", "SMAJ36CA", "AO3414", "1-1470364-2"])
        assert answers["TP4056"].kind == "failed" and answers["AD7747ARUZ"].kind == "found"
        assert [r.status for r in store.readings("AD7747ARUZ")] == ["last_time_buy"]
        assert store.get_answer("digikey", "TP4056") is None  # nothing kept for the failed one
    finally:
        await client.close()
        store.close()


async def test_refusals_in_a_row_pause_5_10_20_40_minutes_up_to_12_hours(clock, caplog):
    """Each refusal in a row doubles the pause, from 5 minutes up to 12 hours; the test lookup at
    each pause's end is what gets refused again."""
    site, session = make_site(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {})] * 20}))
    pauses = []
    for _ in range(12):
        with pytest.raises(SiteUnavailable) as raised:
            await site.lookup("LM358DR")
        pauses.append(raised.value.retry_after)
        clock.advance(raised.value.retry_after)
    minutes = [p // 60 for p in pauses]
    assert minutes == [5, 10, 20, 40, 80, 160, 320, 640, 720, 720, 720, 720]
    assert "DigiKey lookups paused for 12 h: " in caplog.text
    assert len(session.paths) == 12  # one test request at each pause's end, nothing between


@pytest.mark.parametrize("status, headers", [
    (403, {}),  # a bare 403: no challenge markers
    (429, {}),
    (429, {"retry-after": "120"}),  # wafer must not sleep it out until its budget is gone
], ids=["403", "429", "429_retry_after"])
async def test_a_refusal_through_wafer_is_one_request_and_a_pause(clock, status, headers):
    """The session as built for DigiKey (a real wafer session over a fake transport): a 403 or 429
    comes straight back, so it pauses after its one request; wafer neither sends it again under a
    new identity nor waits out Retry-After and fails as a timeout."""
    from test_easyeda_critical_ch import _Reply, _Transport
    transport = _Transport(_Reply(status, {"content-type": "application/json", **headers}, json.dumps({"message": "no"})))

    def session():
        made = _wafer_session()
        made._client = transport
        made._rebuild_client = lambda *args, **kwargs: None  # a new identity would build a real client
        return made

    site = DigiKeySite(session_factory=session, clock=clock)
    with pytest.raises(SiteUnavailable) as raised:
        await site.lookup("LM358DR")
    assert raised.value.paused and raised.value.refused
    assert transport.sent == 1


# --- spellings the API's exact matches accepted (found on prod, 2026-11-20) ---

def _detail_as(product_id, mpn, maker):
    """A recorded product page (TI's LM358DR) standing in for another part: its id, MPN and maker."""
    import copy
    body = copy.deepcopy(ANSWERS["/detail-page/276658"]["body"])
    body["data"]["productOverview"].update({"manufacturerProductNumber": mpn, "manufacturer": maker})
    return Reply(200, body)


def _suggestions(*items):
    return Reply(200, {"data": {"suggestedProductNumbers": [
        {"digiKeyProductNumber": f"{pid}-ND", "manufacturerProductNumber": mpn, "productId": pid,
         "navigationUrl": f"/en/products/detail/{slug}/{mpn.replace(' ', '-')}/{pid}"} for mpn, slug, pid in items]}})


@pytest.mark.parametrize("asked, listed, maker", [
    ("MR06X223JTL", "MR06X223 JTL", "Walsin Technology Corporation"),  # a space
    ("EEUFS1H221L", "EEU-FS1H221L", "Panasonic Industry"),  # a dash
], ids=["space", "dash"])
async def test_the_same_part_but_for_separators_is_found(clock, asked, listed, maker):
    """DigiKey lists the part with separators the number asked lacks: the API counted it as an exact
    match (matched_by separators), and so does this."""
    site, session = make_site(clock, Session({
        "/suggestions": [_suggestions((listed, "maker", 501), (listed + "B", "maker", 502))],
        "/detail-page/501": [_detail_as(501, listed, maker)]}))
    (part,) = (await site.lookup(asked)).results
    assert (part["mfr_part_number"], part["manufacturer"]) == (listed, maker)
    assert session.kinds() == ["suggestions", "detail-page"]  # the "B" variant is another part


async def test_digikeys_own_pick_with_leading_zeros_is_found(clock):
    """Molex's 39012045 is listed as 0039012045: DigiKey's search sends the number straight to it,
    so its leading zeros don't make it another part. From the product list alone they would."""
    site, session = make_site(clock, Session({
        "/suggestions": [_suggestions(("0039012046", "molex", 601))],
        "/result-page": [Reply(200, {"redirect": {"url": "/en/products/detail/molex/0039012045/602"}})],
        "/detail-page/602": [_detail_as(602, "0039012045", "Molex")]}))
    (part,) = (await site.lookup("39012045")).results
    assert part["mfr_part_number"] == "0039012045"


@pytest.mark.parametrize("asked, listed", [
    ("DS89C450-MNL+", "DS89C450-MNL"),  # "+" is Maxim's lead-free part, not a separator
    ("MA2C700A", "MA2C700A0F"),  # a near match DigiKey's search lands on
    ("IKW15N120T2", "IKW15N120T2FKSA1"),  # an ordering code beyond the number
], ids=["plus", "near_match", "ordering_code"])
async def test_other_parts_stay_out(clock, asked, listed):
    site, _ = make_site(clock, Session({
        "/suggestions": [_suggestions((listed, "maker", 701))],
        "/result-page": [Reply(200, {"redirect": {"url": f"/en/products/detail/maker/{listed}/701"}})],
        "/detail-page/701": [_detail_as(701, listed, "Maker")] * 2}))
    assert (await site.lookup(asked)).results == []


async def test_separators_in_a_lifecycle_batch(clock):
    """part_lifecycle's batch path takes the same spellings."""
    compare = Reply(200, {"data": {"compareIds": [801], "compareHeaderRows": [
        {"name": "Mfr Part #", "data": [{"label": "MR06X223 JTL"}]}, {"name": "Mfr", "data": [{"value": "Walsin"}]},
        {"name": "Supplier", "data": [{"label": "Walsin"}]}], "compareDataRows": [
        {"name": "Product Status", "data": [{"value": "Active"}]}, {"name": "Stock", "data": [[{"value": "100"}]]},
        {"name": "DK Part #", "data": [[{"value": "801-ND"}]]}]}})
    site, _ = make_site(clock, Session({"/suggestions": [_suggestions(("MR06X223 JTL", "walsin", 801))],
                                        "/compare-page": [compare]}))
    found = await site.statuses(["MR06X223JTL"])
    assert found == {"MR06X223JTL": [("MR06X223 JTL", "Walsin", "Active", None)]}


def _compare_as(product_id, mpn, maker):
    return Reply(200, {"data": {"compareIds": [product_id], "compareHeaderRows": [
        {"name": "Mfr Part #", "data": [{"label": mpn}]}, {"name": "Mfr", "data": [{"value": maker}]},
        {"name": "Supplier", "data": [{"label": maker}]}], "compareDataRows": [
        {"name": "Product Status", "data": [{"value": "Active"}]}, {"name": "Stock", "data": [[{"value": "100"}]]},
        {"name": "DK Part #", "data": [[{"value": f"{product_id}-ND"}]]}]}})


@pytest.mark.parametrize("asked, listed", [
    ("0805", "805"),
    ("0123", "123"),
    ("123", "0123"),
    ("00000123", "000000123"),  # padding a short number doesn't make it a catalog convention
    ("01234567A", "1234567A"),
], ids=["0805", "short", "short_reverse", "padded_short", "alphanumeric"])
@pytest.mark.parametrize("lifecycle", [False, True], ids=["lookup", "lifecycle"])
async def test_significant_leading_zeros_do_not_match_or_cache_another_part(clock, asked, listed, lifecycle):
    client, session, store = keyless_client(clock, Session({
        "/suggestions": [_suggestions()],
        "/result-page": [Reply(200, {"redirect": {"url": f"/en/products/detail/maker/{listed}/901"}})],
        "/detail-page/901": [_detail_as(901, listed, "Maker")],
        "/compare-page": [_compare_as(901, listed, "Maker")]}))
    try:
        if lifecycle:
            answer = (await client.lifecycle([asked]))[asked]
        else:
            answer = await client.lookup(asked)
        # Check the stored reading too: part_lifecycle must never reuse the other part's status.
        assert [(r.mpn, r.found) for r in store.readings(asked)] == [(asked, False)]
        assert answer.kind == "not_found"
        assert store.get_answer("digikey", asked)[0] == {"not_found": True}
        sent = len(session.paths)
        assert (await client.lifecycle([asked]))[asked].kind == "not_found"
        assert len(session.paths) == sent
    finally:
        await client.close()
        store.close()


@pytest.mark.parametrize("lifecycle", [False, True], ids=["lookup", "lifecycle"])
async def test_jst_separators_and_finish_codes_compose(clock, lifecycle):
    asked, listed, maker = "B2BPHKS(LF)(SN)", "B2B-PH-K-S", "JST Sales America Inc."
    client, _, store = keyless_client(clock, Session({
        "/suggestions": [_suggestions((listed, "jst-sales-america-inc", 902))],
        "/result-page": [Reply(200, {"redirect": {"url": f"/en/products/detail/jst/{listed}/902"}})],
        "/detail-page/902": [_detail_as(902, listed, maker)],
        "/compare-page": [_compare_as(902, listed, maker)]}))
    try:
        answer = (await client.lifecycle([asked]))[asked] if lifecycle else await client.lookup(asked)
        assert answer.kind == "found"
        assert [(r.mpn, r.status, r.found) for r in store.readings(asked)] == [(listed, "active", True)]
        if not lifecycle:
            assert answer.reply["results"][0]["matched_by"] == "packing"
            assert (await client.lifecycle([asked]))[asked].kind == "found"
        assert store.get_answer("digikey", asked) is None or not store.get_answer("digikey", asked)[0].get("not_found")
    finally:
        await client.close()
        store.close()


@pytest.mark.parametrize("asked, listed", [("39012045", "0039012045"), ("0039012045", "39012045")],
                         ids=["padded", "unpadded"])
async def test_molex_catalog_padding_remains_valid_in_lifecycle(clock, asked, listed):
    client, _, store = keyless_client(clock, Session({
        "/suggestions": [_suggestions()],
        "/result-page": [Reply(200, {"data": {"exactMatch": [{"id": 903}]}})],
        "/compare-page": [_compare_as(903, listed, "Molex")]}))
    try:
        assert (await client.lifecycle([asked]))[asked].kind == "found"
        assert [(r.mpn, r.status) for r in store.readings(asked)] == [(listed, "active")]
    finally:
        await client.close()
        store.close()


def _fake_wafer_site(clock, monkeypatch, transport, sleep=None, **kwargs):
    """The production wafer configuration, with transport and time replaced before any send."""
    from types import SimpleNamespace
    import wafer._async as wafer_async
    import wafer._base as wafer_base

    async def advance(seconds):
        clock.advance(seconds)

    sleep = sleep or advance
    monkeypatch.setattr(wafer_async, "asyncio", SimpleNamespace(**(vars(asyncio) | {"sleep": sleep})))
    for module in (wafer_async, wafer_base):
        monkeypatch.setattr(module, "time", SimpleNamespace(**(vars(module.time) | {"monotonic": clock})))
    monkeypatch.setattr("wafer._retry.random.uniform", lambda low, high: 0.0)
    session = _wafer_session()
    session._client = transport
    session._rebuild_client = lambda *args, **kwargs: None
    return DigiKeySite(session_factory=lambda: session, clock=clock, sleep=sleep, **kwargs)


async def test_a_5xx_retry_shares_the_pacer_with_concurrent_requests(clock, monkeypatch):
    """Five fresh requests must not be joined by an unpaced retry inside wafer.get()."""
    from test_easyeda_critical_ch import _Reply, _Transport

    clock.now = 0.0
    backoff, release = asyncio.Event(), asyncio.Event()
    starts = []

    async def sleep(seconds):
        if seconds >= 1:  # hold the retry while five freshly paced requests go out
            backoff.set()
            await release.wait()
        else:
            clock.advance(seconds)

    class Transport(_Transport):
        async def request(self, method, url, **kwargs):
            starts.append(clock())
            self.sent += 1
            return _Reply(503 if self.sent == 1 else 200, {"content-type": "application/json"}, "{}")

    transport = Transport(None)
    site = _fake_wafer_site(clock, monkeypatch, transport, sleep)
    first = asyncio.create_task(site._send("/retry"))
    waiting = asyncio.create_task(backoff.wait())
    try:
        done, _ = await asyncio.wait([first, waiting], return_when=asyncio.FIRST_COMPLETED)
        assert waiting in done
        await asyncio.gather(*(site._send(f"/fresh/{i}") for i in range(5)))
        clock.advance(0.01)
        release.set()
        assert (await first).status_code == 200
        assert transport.sent == 7  # six requests and exactly one retry
        assert all(b - a >= 0.2 - 1e-9 for a, b in zip(starts, starts[1:])), starts
        assert all(sum(start <= other < start + 1 - 1e-9 for other in starts) <= 5 for start in starts), starts
        day = stats.usage.summary()["days"][0]
        assert day["upstream"]["digikey"]["sent"] == 7
        assert day["upstream_status"]["digikey"] == {"5xx": 1, "2xx": 6}
    finally:
        release.set()
        first.cancel()
        waiting.cancel()
        await asyncio.gather(first, waiting, return_exceptions=True)
        await site.close()


async def test_simultaneous_retries_keep_the_gap_until_each_send(clock, monkeypatch):
    from test_easyeda_critical_ch import _Reply, _Transport
    clock.now = 0.0
    release, ready = asyncio.Event(), asyncio.Event()
    seen, starts = set(), []

    async def sleep(seconds):
        if seconds >= 1:
            if len(seen) == 4:
                ready.set()
            await release.wait()
        else:
            clock.advance(seconds)

    class Transport(_Transport):
        async def request(self, method, url, **kwargs):
            starts.append(clock())
            status = 200 if url in seen else 503
            seen.add(url)
            return _Reply(status, {"content-type": "application/json"}, "{}")

    site = _fake_wafer_site(clock, monkeypatch, Transport(None), sleep)
    tasks = [asyncio.create_task(site._send(f"/test/{i}")) for i in range(4)]
    try:
        await ready.wait()
        clock.advance(2)
        release.set()
        await asyncio.gather(*tasks)
        assert len(starts) == 8
        assert all(b - a >= 0.2 - 1e-9 for a, b in zip(starts, starts[1:])), starts
    finally:
        release.set()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await site.close()


@pytest.mark.parametrize("kind", ["5xx", "connection", "timeout", "body", "empty"])
@pytest.mark.parametrize("recovers", [True, False], ids=["recovers", "exhausted"])
async def test_wafer_retry_conditions_and_every_attempt_counted(clock, monkeypatch, kind, recovers):
    import wreq
    from test_easyeda_critical_ch import _Reply, _Transport

    class BrokenBody(_Reply):
        async def bytes(self):
            raise OSError("body read failed")

    class Transport(_Transport):
        async def request(self, method, url, **kwargs):
            self.sent += 1
            assert 0 < kwargs["timeout"].total_seconds() <= 8
            if self.sent == 1 or not recovers:
                if kind == "connection":
                    raise OSError("connection reset")
                if kind == "timeout":
                    clock.advance(kwargs["timeout"].total_seconds())
                    raise wreq.exceptions.TimeoutError("attempt timed out")
                if kind == "body":
                    return BrokenBody(200, {"content-type": "application/json"}, "{}")
                return _Reply(503 if kind == "5xx" else 200, {"content-type": "application/json"},
                              "{}" if kind == "5xx" else " \n\t")
            return _Reply(200, {"content-type": "application/json"}, "{}")

    transport = Transport(None)
    site = _fake_wafer_site(clock, monkeypatch, transport)
    try:
        if not recovers and kind in ("connection", "timeout", "body"):
            with pytest.raises(SiteFailed):
                await site._send("/test")
        else:
            response = await site._send("/test")
            assert response.status_code == (503 if kind == "5xx" and not recovers else 200)
        assert transport.sent == 2
        day = stats.usage.summary()["days"][0]
        assert day["upstream"]["digikey"]["sent"] == 2
        assert day["upstream"]["digikey"]["retries"] == 0  # both attempts are now explicit sends
        failure_class = {"5xx": "5xx", "connection": "connection", "timeout": "timeout",
                         "body": "connection", "empty": "2xx"}[kind]
        expected = {failure_class: 1 if recovers else 2}
        if recovers:
            expected["2xx"] = expected.get("2xx", 0) + 1
        assert day["upstream_status"]["digikey"] == expected
    finally:
        await site.close()


@pytest.mark.parametrize("status, body, content_type", [
    (204, "", "application/json"), (404, "{}", "application/json"), (400, "{}", "application/json"),
    (200, "", "application/octet-stream"), (200, "not json", "application/json"),
], ids=["204", "404", "400", "binary", "invalid_json"])
async def test_non_retryable_wafer_replies_still_send_once(clock, monkeypatch, status, body, content_type):
    from test_easyeda_critical_ch import _Reply, _Transport
    transport = _Transport(_Reply(status, {"content-type": content_type}, body))
    site = _fake_wafer_site(clock, monkeypatch, transport)
    try:
        assert (await site._send("/test")).status_code == status
        assert transport.sent == 1
    finally:
        await site.close()


@pytest.mark.parametrize("queued", [False, True], ids=["immediate", "queued"])
async def test_retry_keeps_one_total_budget_and_clamps_the_attempt_timeout(clock, monkeypatch, queued):
    import wreq
    from test_easyeda_critical_ch import _Reply, _Transport
    clock.now = 0.0
    starts, limits = [], []

    class Transport(_Transport):
        async def request(self, method, url, **kwargs):
            starts.append(clock())
            limits.append(kwargs["timeout"].total_seconds())
            self.sent += 1
            clock.advance(limits[-1])
            if self.sent == 1:
                raise wreq.exceptions.TimeoutError("attempt timed out")
            return _Reply(200, {"content-type": "application/json"}, "{}")

    transport = Transport(None)
    site = _fake_wafer_site(clock, monkeypatch, transport, per_second=1 / 15)
    if queued:
        site._pacer.mark()  # the first send waits 15 s before its 20 s budget starts
    try:
        assert (await site._send("/test")).status_code == 200
        assert limits == [8.0, 5.0]  # retry pacing spent part of the shared 20 s budget
        assert starts == ([15.0, 30.0] if queued else [0.0, 15.0])
        assert clock() - starts[0] == 20.0
    finally:
        await site.close()


async def test_retry_does_not_send_after_its_budget_expires_in_the_pacer(clock, monkeypatch):
    from test_easyeda_critical_ch import _Reply, _Transport
    transport = _Transport(_Reply(503, {"content-type": "application/json"}, "{}"))
    site = _fake_wafer_site(clock, monkeypatch, transport, per_second=1 / 25)
    try:
        with pytest.raises(SiteFailed, match="WaferTimeout"):
            await site._send("/test")
        assert transport.sent == 1
        day = stats.usage.summary()["days"][0]
        assert day["upstream"]["digikey"]["sent"] == 1
        assert day["upstream_status"]["digikey"] == {"5xx": 1}
    finally:
        await site.close()


async def test_retry_stops_if_another_lookup_pauses_the_site(clock, monkeypatch):
    from test_easyeda_critical_ch import _Reply, _Transport
    transport = _Transport(_Reply(503, {"content-type": "application/json"}, "{}"))

    async def sleep(seconds):
        clock.advance(seconds)
        site._refused("another lookup was refused")

    site = _fake_wafer_site(clock, monkeypatch, transport, sleep)
    try:
        with pytest.raises(SiteUnavailable) as raised:
            await site.lookup("LM358DR")
        assert raised.value.paused and raised.value.sent
        assert transport.sent == 1
    finally:
        await site.close()


@pytest.mark.parametrize("kind", ["response", "connection", "timeout", "empty"],
                         ids=["503", "conn", "time", "empty"])
async def test_challenge_never_retries_even_if_next_attempt_would_succeed(clock, kind):
    refusal = {"response": Reply(503, {}, challenge_type="waf"),
               "connection": wafer.ConnectionFailed(BASE_URL, "reset"),
               "timeout": wafer.WaferTimeout(BASE_URL, 8),
               "empty": wafer.EmptyResponse(BASE_URL, 503)}[kind]
    refusal.challenge_type = "waf"
    site, session = make_site(clock, Session({"/suggestions": [refusal]}))
    try:
        with pytest.raises(SiteUnavailable) as raised:
            await site.lookup("LM358DR")
        assert raised.value.paused and raised.value.refused
        assert session.kinds() == ["suggestions"]
    finally:
        await site.close()


# --- 0.10.5: the per-address day without credentials too ---

CALLER, OTHER, PLATFORM = "203.0.113.9", "198.51.100.4", "160.79.104.1"
CAP_ERROR = ("This address has used its 2 Mouser and DigiKey lookups for today on this shared server; the count "
             "resets at 00:00 UTC. Answers pcbparts already has stored still work. To skip the shared limits, run "
             "pcbparts-mcp with your own DigiKey API credentials (free at https://developer.digikey.com): ")


def capped_client(clock, session=None, limit=2, **site_kwargs):
    site, session = make_site(clock, session, **site_kwargs)
    store = DistributorStore(clock=clock)
    day = AddressDailyQuota(limit, key=lambda ip: None if ip == PLATFORM else ip, clock=clock)
    return DigiKeyClient(store=store, site=site, address_daily=day), session, store, day


async def test_keyless_lookups_count_against_the_address_day(clock):
    client, session, store, day = capped_client(clock)
    try:
        for number in ("LM358DR", "AO3400A"):
            assert (await client.lookup(number, caller=CALLER)).kind == "found"
        sent = len(session.paths)
        third = await client.lookup("AD7747ARUZ", caller=CALLER)
        assert third.kind == "limited" and third.reply["error"].startswith(CAP_ERROR)
        assert len(session.paths) == sent  # nothing went out
        assert (await client.lookup("lm358dr", caller=CALLER)).kind == "found"  # stored: still free
        assert client.retry_after(CALLER) == math.ceil(NOW + 12 * 3600 - clock())  # to 00:00 UTC
        assert (await client.lookup("AD7747ARUZ", caller=OTHER)).kind == "found"  # another address
        assert (await client.lookup("497-6063-ND", caller=PLATFORM)).kind == "found"  # exempt
        assert day.remaining(CALLER) == 0 and day.remaining(OTHER) == 1 and day.remaining(PLATFORM) is None
        today = stats.usage.summary()["days"][0]
        assert today["distributors"]["digikey"]["rate_limited"] == 1
        assert today["distributor_limits"]["digikey"]["held_back"]["address_daily"] == 1
    finally:
        await client.close()
        store.close()


async def test_a_keyless_lookup_that_sends_nothing_costs_nothing(clock):
    """A refused request was sent (charged); one held back by the pause that follows wasn't."""
    client, _, store, day = capped_client(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {})]}))
    try:
        assert (await client.lookup("LM358DR", caller=CALLER)).kind == "limited"
        assert (await client.lookup("AO3400A", caller=CALLER)).kind == "limited"  # paused: not sent
        assert day.remaining(CALLER) == 1
    finally:
        await client.close()
        store.close()


async def test_a_second_caller_for_a_running_lookup_is_not_charged(clock):
    gate = asyncio.Event()

    class Held(Session):
        async def get(self, url, **kwargs):
            await gate.wait()
            return await super().get(url, **kwargs)

    client, _, store, day = capped_client(clock, Held())
    try:
        first = asyncio.create_task(client.get_part("LM358DR", caller=CALLER))
        second = asyncio.create_task(client.get_part("LM358DR", caller=OTHER))
        for _ in range(5):
            await asyncio.sleep(0)
        gate.set()
        await asyncio.gather(first, second)
        assert (day.remaining(CALLER), day.remaining(OTHER)) == (1, 2)
    finally:
        await client.close()
        store.close()


def charging_statuses(asked):
    """A stand-in for DigiKeySite.statuses keeping its contract: charge() before each number's first
    request, AddressCapReached (nothing sent) when it refuses, sent gets the numbers sent."""
    async def statuses(numbers, sent=None, charge=None, held=None):
        asked.append(list(numbers))
        found = {}
        for number in numbers:
            if charge is not None and not charge(number):
                found[number] = AddressCapReached()
                continue
            sent.add(number)
            found[number] = [(number, "Maker", "Active", None)]
        return found
    return statuses


async def test_keyless_lifecycle_batch_stops_at_the_address_day(clock):
    client, _, store, day = capped_client(clock, limit=3)
    asked: list[list[str]] = []
    client._site.statuses = charging_statuses(asked)
    try:
        day.record(CALLER)  # one lookup earlier today: two left
        entries = [Entry(n, mpn=n) for n in ("PARTA1", "PARTB2", "PARTC3", "PARTD4")]
        results = await LifecycleLookup(store, None, client).answer(entries, caller=CALLER)
        assert asked == [["PARTA1", "PARTB2", "PARTC3", "PARTD4"]]  # the charge refuses the last two
        assert [r["status"] for r in results] == ["active", "active", "unknown", "unknown"]
        assert results[2]["retry_after"] == results[3]["retry_after"] == 12 * 3600
        assert day.remaining(CALLER) == 0
        again = await LifecycleLookup(store, None, client).answer([Entry("PARTE5", mpn="PARTE5")], caller=CALLER)
        assert len(asked) == 1 and again[0]["status"] == "unknown"  # used up: held back without asking
        assert (await LifecycleLookup(store, None, client).answer([Entry("PARTA1", mpn="PARTA1")], caller=CALLER)
                )[0]["status"] == "active"  # kept readings stay free
        held = stats.usage.summary()["days"][0]["distributor_limits"]["digikey"]["held_back"]["address_daily"]
        assert held == 3
    finally:
        await client.close()
        store.close()


async def test_a_batch_whose_day_runs_out_midway_sends_only_what_it_may(clock):
    """Another lookup used the allowance after the batch was split: the site's charge refuses the rest."""
    client, _, store, day = capped_client(clock, limit=3)
    asked: list[list[str]] = []
    inner = charging_statuses(asked)

    async def statuses(numbers, sent=None, charge=None, held=None):
        day.record(CALLER, 2)  # meanwhile: two Mouser lookups from the same address
        return await inner(numbers, sent=sent, charge=charge)

    client._site.statuses = statuses
    try:
        answers = await client.lifecycle(["PARTA1", "PARTB2", "PARTC3"], caller=CALLER)
        assert [answers[n].kind for n in ("PARTA1", "PARTB2", "PARTC3")] == ["found", "limited", "limited"]
        assert answers["PARTB2"].retry_after == 12 * 3600 and day.remaining(CALLER) == 0
        today = stats.usage.summary()["days"][0]
        assert (today["distributors"]["digikey"]["sent"], today["distributors"]["digikey"]["rate_limited"]) == (1, 2)
        assert today["distributor_limits"]["digikey"]["held_back"]["address_daily"] == 2
    finally:
        await client.close()
        store.close()


async def test_keyless_hourly_lines_sent_and_held_back(clock, caplog):
    client, _, store, _ = capped_client(clock, limit=1)
    try:
        await client.lookup("LM358DR", caller=CALLER)
        await client.lookup("AO3400A", caller=CALLER)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            client.callers.flush()
            client.held_back.flush()
        lines = [r.message for r in caplog.records]
        assert any(line.startswith("DigiKey requests sent ") and f"from 1 IPs; top: {CALLER} " in line for line in lines)
        assert any(line.startswith("DigiKey calls held back ") and line.endswith(f"1 from 1 IPs; all: {CALLER} 1")
                   for line in lines)
    finally:
        await client.close()
        store.close()


async def test_server_without_credentials_shares_the_address_day_with_mouser(monkeypatch):
    from fastmcp import Client
    monkeypatch.setenv("DIGIKEY_LOOKUP", "site")
    monkeypatch.setattr(server, "MOUSER_API_KEY", "test-key")
    monkeypatch.setattr(server, "_digikey_client", None)  # put back after: startup sets the global
    async with Client(server.mcp):
        mouser_day = server._distributor_quotas["mouser"].address_daily
        assert server._digikey_client._address_daily is mouser_day and mouser_day.limit == 1000
        tallies = server._caller_tallies()
        assert server._digikey_client.callers in tallies and server._digikey_client.held_back in tallies


# --- review fixes (2026-11-21) ---

BATCH = ["LM358DR", "AD7747ARUZ", "TP4056", "SMAJ36CA", "AO3414", "1-1470364-2"]


async def test_a_refused_batch_charges_only_the_lookups_sent(clock):
    """The first request of six is refused and the rest never go out: one lookup charged and
    counted as sent, five held back (each was charged and counted as sent before)."""
    client, session, store, day = capped_client(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {})]}),
                                                limit=10, concurrency=1)
    try:
        answers = await client.lifecycle(BATCH, caller=CALLER)
        assert len(session.paths) == 1 and {a.kind for a in answers.values()} == {"limited"}
        assert day.remaining(CALLER) == 9
        today = stats.usage.summary()["days"][0]
        assert (today["distributors"]["digikey"]["sent"], today["distributors"]["digikey"]["rate_limited"]) == (1, 5)
        assert (sum(client.callers._counts.values()), sum(client.held_back._counts.values())) == (1, 5)
    finally:
        await client.close()
        store.close()


async def test_a_batch_cancelled_before_sending_costs_nothing(clock):
    client, _, store, day = capped_client(clock, limit=10)
    started = asyncio.Event()

    async def statuses(numbers, sent=None, charge=None, held=None):
        started.set()
        await asyncio.Event().wait()  # held until cancelled, nothing sent

    client._site.statuses = statuses
    try:
        task = asyncio.create_task(client.lifecycle(["PARTA1", "PARTB2", "PARTC3"], caller=CALLER))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert day.remaining(CALLER) == 10
    finally:
        await client.close()
        store.close()


async def test_the_sites_charge_refusal_sends_nothing(clock):
    site, session = make_site(clock)
    with pytest.raises(AddressCapReached):
        await site.lookup("LM358DR", sent=(sent := set()), charge=lambda number, check=False: False)
    found = await site.statuses(["LM358DR", "AO3400A"], sent=(batch := set()), charge=lambda number, check=False: False)
    assert session.paths == [] and sent == set() == batch
    assert {type(v) for v in found.values()} == {AddressCapReached}


def test_the_default_caps_reply_is_counted_as_rate_limited():
    from pcbparts_mcp import tool_outcomes
    error = AddressDailyQuota(1000, key=lambda ip: ip).error(" Meanwhile use jlc_search.")["error"]
    assert error.startswith("This address has used its 1000 Mouser and DigiKey lookups for today")
    assert tool_outcomes._error_kind(error) == "rate_limited"


async def test_a_retried_request_then_a_refusal_charges_its_number_once(clock):
    """The first number's request fails with a 500, is sent again and refused: two requests, one
    number sent (counting requests charged two lookups)."""
    client, session, store, day = capped_client(
        clock, Session({LM358DR_SUGGESTIONS: [Reply(500, {}), Reply(403, {})]}), limit=10, concurrency=1)
    try:
        answers = await client.lifecycle(BATCH, caller=CALLER)
        assert {a.kind for a in answers.values()} == {"limited"}
        assert all(path.startswith(LM358DR_SUGGESTIONS) for path in session.paths) and len(session.paths) == 2
        assert day.remaining(CALLER) == 9
        today = stats.usage.summary()["days"][0]
        assert (today["distributors"]["digikey"]["sent"], today["distributors"]["digikey"]["rate_limited"]) == (1, 5)
    finally:
        await client.close()
        store.close()


async def test_a_batch_cancelled_after_sending_keeps_the_charge_for_what_went_out(clock):
    """Cancelling can't buy lookups back: numbers already sent stay charged and counted."""
    client, _, store, day = capped_client(clock, limit=10)
    started = asyncio.Event()

    async def statuses(numbers, sent=None, charge=None, held=None):
        for number in numbers[:2]:  # two of the three numbers' requests went out
            assert charge(number)
            sent.add(number)
        started.set()
        await asyncio.Event().wait()

    client._site.statuses = statuses
    try:
        task = asyncio.create_task(client.lifecycle(["PARTA1", "PARTB2", "PARTC3"], caller=CALLER))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert day.remaining(CALLER) == 8
        assert stats.usage.summary()["days"][0]["distributors"]["digikey"]["sent"] == 2
        assert sum(client.callers._counts.values()) == 2
    finally:
        await client.close()
        store.close()


async def test_statuses_reports_the_numbers_sent_even_when_stopped(clock):
    site, session = make_site(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {})]}), concurrency=1)
    sent: set[str] = set()
    with pytest.raises(SiteUnavailable):
        await site.statuses(BATCH, sent=sent)
    assert sent == {"LM358DR"} and len(session.paths) == 1


async def test_a_number_sent_before_a_later_slot_timeout_stays_charged(clock):
    """Its product list went out, then its comparison found no slot: still a lookup sent."""
    client, _, store, day = capped_client(clock, limit=10)

    async def statuses(numbers, sent=None, charge=None, held=None):
        for number in numbers:
            assert charge(number)
            sent.add(number)
        return {numbers[0]: [(numbers[0], "Maker", "Active", None)],
                numbers[1]: SiteUnavailable(30, paused=False, sent=False)}

    client._site.statuses = statuses
    try:
        answers = await client.lifecycle(["PARTA1", "PARTB2"], caller=CALLER)
        assert (answers["PARTA1"].kind, answers["PARTB2"].kind) == ("found", "limited")
        assert day.remaining(CALLER) == 8
        today = stats.usage.summary()["days"][0]["distributors"]["digikey"]
        assert (today["sent"], today["rate_limited"]) == (2, 0)
        assert (sum(client.callers._counts.values()), sum(client.held_back._counts.values())) == (2, 0)
    finally:
        await client.close()
        store.close()


class Gated(Session):
    """Holds every request inside get() (after it was charged and counted) until gate is set."""

    def __init__(self, gate, script=None):
        super().__init__(script)
        self.gate = gate

    async def get(self, url, **kwargs):
        await self.gate.wait()
        return await super().get(url, **kwargs)


async def test_a_request_sent_before_midnight_counts_on_that_day(clock):
    """Sent at 23:59:59, answered at 00:00:01: the new day owes nothing for it."""
    gate = asyncio.Event()
    clock.now = NOW + 12 * 3600 - 1  # 23:59:59 UTC
    client, _, store, day = capped_client(clock, Gated(gate), limit=1)
    try:
        first = asyncio.create_task(client.lookup("LM358DR", caller=CALLER))
        for _ in range(5):
            await asyncio.sleep(0)
        clock.advance(2)
        gate.set()
        assert (await first).kind == "found"
        assert day.remaining(CALLER) == 1  # today's allowance untouched
        assert (await client.lookup("AO3400A", caller=CALLER)).kind == "found"
    finally:
        await client.close()
        store.close()


async def test_a_lookup_queued_over_midnight_is_checked_against_the_new_day(clock):
    """Waiting for a slot at midnight while its address uses the new day elsewhere: refused at send."""
    gate = asyncio.Event()
    clock.now = NOW + 12 * 3600 - 1
    session = Gated(gate)
    client, _, store, day = capped_client(clock, session, limit=1, concurrency=1)
    try:
        holder = asyncio.create_task(client.lookup("AO3400A", caller=OTHER))  # takes the only slot
        for _ in range(5):
            await asyncio.sleep(0)
        queued = asyncio.create_task(client.lookup("LM358DR", caller=CALLER))
        for _ in range(5):
            await asyncio.sleep(0)
        clock.advance(2)  # 00:00:01
        day.record(CALLER)  # a Mouser lookup spends CALLER's new day
        gate.set()
        assert (await holder).kind == "found"
        refused = await queued
        assert refused.kind == "limited" and refused.reply["error"].startswith(CAP_ERROR.replace("2 Mouser", "1 Mouser"))
        assert not any("LM358DR" in path for path in session.paths)
    finally:
        await client.close()
        store.close()

# --- review fixes, round 3 (2026-11-21) ---

async def test_a_test_lookup_that_sends_nothing_leaves_the_test_due_and_the_backoff(clock):
    """After a pause, a batch whose every number its charge refuses tests nothing: the next lookup
    is still the test, and a refusal still doubles the pause."""
    site, session = make_site(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {}), Reply(403, {})]}))
    with pytest.raises(SiteUnavailable):
        await site.lookup("LM358DR")
    clock.advance(DIGIKEY_SITE_PAUSE)
    sent_before = len(session.paths)
    found = await site.statuses(["AO3400A"], charge=lambda number, check=False: False)
    assert isinstance(found["AO3400A"], AddressCapReached) and len(session.paths) == sent_before
    assert site._test_due
    with pytest.raises(SiteUnavailable) as raised:
        await site.lookup("LM358DR")  # the real test, refused again
    assert raised.value.retry_after == 2 * DIGIKEY_SITE_PAUSE


async def test_a_caller_that_joined_a_lookup_its_starter_could_not_send_asks_with_its_own_day(clock):
    gate = asyncio.Event()
    session = Gated(gate)
    client, _, store, day = capped_client(clock, session, limit=1, concurrency=1)
    try:
        holder = asyncio.create_task(client.lookup("AO3400A", caller=PLATFORM))  # takes the only slot
        for _ in range(5):
            await asyncio.sleep(0)
        starter = asyncio.create_task(client.lookup("LM358DR", caller=CALLER))  # queued for the slot
        for _ in range(5):
            await asyncio.sleep(0)
        joiner = asyncio.create_task(client.lookup("LM358DR", caller=OTHER))  # joins CALLER's lookup
        for _ in range(5):
            await asyncio.sleep(0)
        day.record(CALLER)  # CALLER's day runs out (a Mouser lookup) before its request goes out
        gate.set()
        assert (await holder).kind == "found"
        refused, answered = await starter, await joiner
        assert refused.kind == "limited" and refused.reply["error"].startswith("This address has used its 1 ")
        assert answered.kind == "found" and answered.reply["results"][0]["requested"] == "LM358DR"
        assert (day.remaining(CALLER), day.remaining(OTHER)) == (0, 0)  # OTHER paid for its own lookup
        today = stats.usage.summary()["days"][0]["distributors"]["digikey"]
        assert today["cached"] == 0  # the join that couldn't answer isn't counted as an answer
    finally:
        await client.close()
        store.close()


async def test_a_request_its_charge_refuses_is_not_counted_as_waited(clock):
    gate = asyncio.Event()
    client, session, store, day = capped_client(clock, Gated(gate), limit=1, concurrency=1)
    try:
        holder = asyncio.create_task(client.lookup("AO3400A", caller=PLATFORM))
        for _ in range(5):
            await asyncio.sleep(0)
        queued = asyncio.create_task(client.lookup("LM358DR", caller=CALLER))
        for _ in range(5):
            await asyncio.sleep(0)
        day.record(CALLER)
        gate.set()
        await holder
        assert (await queued).kind == "limited"
        upstream = stats.usage.summary()["days"][0]["upstream"]["digikey"]
        assert upstream["waited"] == 0 and upstream["sent"] == len(session.paths)
    finally:
        await client.close()
        store.close()


def _first_only():
    """A charge that lets one number's request out, then refuses."""
    allowed = [1]

    def charge(number, check=False):
        if allowed[0]:
            if not check:
                allowed[0] -= 1
            return True
        return False
    return charge


async def test_a_batch_whose_tried_numbers_all_failed_still_fails_beside_refused_ones(clock):
    site, _ = make_site(clock, Session({LM358DR_SUGGESTIONS: [Reply(500, {}), Reply(500, {})]}), concurrency=1)
    with pytest.raises(SiteFailed):
        await site.statuses(["LM358DR", "AO3400A"], charge=_first_only())
    assert site._failing  # counted toward the run of failures that pauses


async def test_lifecycle_tells_a_failed_number_from_one_its_charge_refused(clock):
    client, _, store, day = capped_client(
        clock, Session({LM358DR_SUGGESTIONS: [Reply(500, {}), Reply(500, {})]}), limit=1, concurrency=1)
    try:
        answers = await client.lifecycle(["LM358DR", "AO3400A"], caller=CALLER)
        assert (answers["LM358DR"].kind, answers["AO3400A"].kind) == ("failed", "limited")
        assert math.ceil(NOW + 12 * 3600 - clock()) <= answers["AO3400A"].retry_after <= 12 * 3600  # to 00:00 UTC
        today = stats.usage.summary()["days"][0]
        assert (today["distributors"]["digikey"]["sent"], today["distributors"]["digikey"]["rate_limited"]) == (1, 1)
        assert today["distributor_limits"]["digikey"]["held_back"]["address_daily"] == 1
    finally:
        await client.close()
        store.close()


def test_a_finished_refused_lookup_still_listed_is_not_spun_on(clock):
    """A caller arriving after a shared lookup was refused by its starter's day, before the task's
    cleanup callback ran: awaiting a done task doesn't yield, so it once looped forever on it and
    froze the event loop. Run in its own thread so a regression fails here instead of hanging."""
    import threading

    from pcbparts_mcp.digikey import Lookup
    outcome: list[str] = []

    def run() -> None:
        async def main() -> None:
            client, _, store, _ = capped_client(clock, limit=5)
            try:
                done = asyncio.get_running_loop().create_future()
                done.set_result(Lookup({"error": "refused"}, "address_capped", NOW))
                client._inflight["LM358DR"] = done  # finished, not yet cleaned up

                async def fresh(product_number, cache_key, caller=None):
                    return Lookup({"results": [], "total": 0}, "found", NOW)

                client._fetch_site = fresh
                outcome.append((await client._lookup_site("LM358DR", "LM358DR", OTHER)).kind)
            finally:
                await client.close()
                store.close()
        asyncio.run(main())

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(30)
    assert outcome == ["found"]


async def test_a_queued_lookup_blocked_by_a_pause_and_its_used_day_gets_the_day(clock):
    """Its address's day ran out and a refusal paused the site before it went out: it can't send
    before 00:00 UTC either way, so it gets the address reply (the API path checks the address first)."""
    gate = asyncio.Event()
    session = Gated(gate, {LM358DR_SUGGESTIONS: [Reply(403, {})]})
    client, _, store, day = capped_client(clock, session, limit=1, concurrency=1)
    try:
        holder = asyncio.create_task(client.lookup("LM358DR", caller=PLATFORM))  # refused, pausing all
        for _ in range(5):
            await asyncio.sleep(0)
        queued = asyncio.create_task(client.lookup("AO3400A", caller=CALLER))
        for _ in range(5):
            await asyncio.sleep(0)
        day.record(CALLER)
        gate.set()
        assert (await holder).reply["error"].startswith("DigiKey lookups are paused")
        blocked = await queued
        assert blocked.kind == "limited" and blocked.reply["error"].startswith("This address has used its 1 ")
        limits = stats.usage.summary()["days"][0]["distributor_limits"]["digikey"]
        assert (limits["held_back"]["address_daily"], limits["held_back"]["distributor_refused"]) == (1, 0)
        assert limits["refusals"]["refused"] == 1
    finally:
        await client.close()
        store.close()


async def test_the_hourly_sent_line_counts_a_request_when_it_goes_out(clock):
    """Recorded by the charge, so a lookup still waiting for its answer is in the hour's line."""
    gate = asyncio.Event()
    client, _, store, _ = capped_client(clock, Gated(gate), limit=5)
    try:
        task = asyncio.create_task(client.lookup("LM358DR", caller=CALLER))
        for _ in range(5):
            await asyncio.sleep(0)
        assert client.callers._counts == {CALLER: 1}  # sent, no answer yet
        gate.set()
        await task
        assert client.callers._counts == {CALLER: 1}
    finally:
        await client.close()
        store.close()



# --- review fixes, round 5 (2026-11-21) ---

def _fake_statuses(site, outcome):
    """Replace site._statuses: one request out per number (marked sent), then outcome(numbers)."""
    from pcbparts_mcp import digikey_site

    async def statuses(numbers):
        digikey_site._lookup_sends.get()[0] += len(numbers)
        digikey_site._batch_sent.get().update(numbers)
        return outcome(numbers)
    site._statuses = statuses


async def test_a_probe_whose_numbers_failed_or_found_no_slot_is_no_pass(clock):
    site, _ = make_site(clock)
    site._test_due = True  # after a pause
    _fake_statuses(site, lambda numbers: {numbers[0]: SiteFailed("x"),
                                          numbers[1]: SiteUnavailable(30, paused=False, sent=True)})
    found = await site.statuses(["PARTA1", "PARTB2"])
    assert isinstance(found["PARTA1"], SiteFailed) and isinstance(found["PARTB2"], SiteUnavailable)
    assert site._test_due  # still untested: the next lookup is the test


async def test_one_number_failing_beside_different_refused_ones_never_pauses(clock):
    site, _ = make_site(clock)

    def failing(numbers):
        raise SiteFailed("suggestions: HTTP 500")

    from pcbparts_mcp import digikey_site

    async def statuses(numbers):  # only FAILING goes out; its companion was refused by the charge
        digikey_site._lookup_sends.get()[0] += 1
        digikey_site._batch_sent.get().add("FAILING")
        failing(numbers)
    site._statuses = statuses
    for companion in ("PARTA1", "PARTB2", "PARTC3"):
        with pytest.raises(SiteFailed):
            await site.statuses(["FAILING", companion])
    assert site._failing == {"failing"} and not site._pause.active


async def test_a_caller_joining_a_lookup_that_fails_is_still_counted(clock):
    gate = asyncio.Event()
    session = Gated(gate, {"/suggestions": [wafer.ConnectionFailed(BASE_URL, "reset")] * 2})
    client, _, store, _ = capped_client(clock, session, limit=5)
    try:
        first = asyncio.create_task(client.lookup("LM358DR", caller=CALLER))
        for _ in range(5):
            await asyncio.sleep(0)
        second = asyncio.create_task(client.lookup("LM358DR", caller=OTHER))
        for _ in range(5):
            await asyncio.sleep(0)
        gate.set()
        for task in (first, second):
            with pytest.raises(DigiKeyError):
                await task
        today = stats.usage.summary()["days"][0]["distributors"]["digikey"]
        assert (today["sent"], today["cached"]) == (1, 1)
    finally:
        await client.close()
        store.close()


async def test_a_paused_batch_with_allowance_left_gets_the_pause_not_the_day(clock):
    """One lookup left, two numbers, the site paused before either went out: the address still has
    its lookup, so both get the pause's retry_after and count as the site's hold-back."""
    client, _, store, day = capped_client(clock, Session({LM358DR_SUGGESTIONS: [Reply(403, {})]}), limit=5)
    try:
        await client.lookup("LM358DR", caller=PLATFORM)  # refused: every lookup paused
        day.record(CALLER, 4)  # one left
        answers = await client.lifecycle(["AO3400A", "AD7747ARUZ"], caller=CALLER)
        assert {a.kind for a in answers.values()} == {"limited"}
        assert {a.retry_after for a in answers.values()} == {DIGIKEY_SITE_PAUSE}
        assert day.remaining(CALLER) == 1
        held = stats.usage.summary()["days"][0]["distributor_limits"]["digikey"]["held_back"]
        assert (held["address_daily"], held["distributor_refused"]) == (0, 2)
    finally:
        await client.close()
        store.close()


async def test_refusals_counted_before_a_batch_is_cancelled_stay_counted(clock):
    """One lookup left: the first number goes out and waits, the next two are refused by the
    charge, then the batch is cancelled. The refusals were counted as they happened."""
    client, _, store, day = capped_client(clock, limit=10)
    started = asyncio.Event()

    async def statuses(numbers, sent=None, charge=None, held=None):
        day.record(CALLER, 9)  # one left
        for number in numbers:
            if charge(number):
                sent.add(number)
        started.set()
        await asyncio.Event().wait()

    client._site.statuses = statuses
    try:
        task = asyncio.create_task(client.lifecycle(["PARTA1", "PARTB2", "PARTC3"], caller=CALLER))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        today = stats.usage.summary()["days"][0]
        assert (today["distributors"]["digikey"]["sent"], today["distributors"]["digikey"]["rate_limited"]) == (1, 2)
        assert today["distributor_limits"]["digikey"]["held_back"]["address_daily"] == 2
        assert (sum(client.callers._counts.values()), sum(client.held_back._counts.values())) == (1, 2)
    finally:
        await client.close()
        store.close()


async def test_a_refused_number_in_a_batch_stopped_later_is_counted_once(clock):
    """One lookup left: LM358DR goes out, AO3400A is refused by the charge (counted), then the
    comparison is refused and stops the batch: AO3400A isn't counted a second time."""
    client, _, store, day = capped_client(clock, Session({"/compare-page": [Reply(403, {})]}), limit=1, concurrency=1)
    try:
        answers = await client.lifecycle(["LM358DR", "AO3400A"], caller=CALLER)
        assert {a.kind for a in answers.values()} == {"limited"}
        assert answers["AO3400A"].retry_after > answers["LM358DR"].retry_after  # 00:00 UTC vs the pause
        today = stats.usage.summary()["days"][0]
        assert (today["distributors"]["digikey"]["sent"], today["distributors"]["digikey"]["rate_limited"]) == (1, 1)
        held = today["distributor_limits"]["digikey"]["held_back"]
        assert (held["address_daily"], held["distributor_refused"]) == (1, 0)
        assert (sum(client.callers._counts.values()), sum(client.held_back._counts.values())) == (1, 1)
    finally:
        await client.close()
        store.close()


async def test_a_number_refused_before_midnight_in_a_batch_ending_after_can_retry_at_once(clock):
    """Refused at 23:59:59, the batch done at 00:00:01: its day has reset, so retry_after is about a
    second, not another day."""
    clock.now = NOW + 12 * 3600 - 1
    client, _, store, day = capped_client(clock, limit=1)

    async def statuses(numbers, sent=None, charge=None, held=None):
        found = {}
        for number in numbers:
            if charge(number):
                sent.add(number)
                found[number] = [(number, "Maker", "Active", None)]
            else:
                found[number] = AddressCapReached()
        clock.advance(2)
        return found

    client._site.statuses = statuses
    try:
        answers = await client.lifecycle(["PARTA1", "PARTB2"], caller=CALLER)
        assert answers["PARTA1"].kind == "found"
        assert answers["PARTB2"].kind == "limited" and answers["PARTB2"].retry_after == 1
    finally:
        await client.close()
        store.close()


async def test_closing_the_client_counts_a_lookup_still_in_flight(clock):
    """Shutdown cancels a lookup whose request is out; close() waits for it, so its send is counted
    before the server's last save of the stats."""
    gate = asyncio.Event()
    client, _, store, _ = capped_client(clock, Gated(gate), limit=5)
    try:
        task = asyncio.create_task(client.lookup("LM358DR", caller=CALLER))
        for _ in range(5):
            await asyncio.sleep(0)
        await client.close()
        assert task.done()
        assert stats.usage.summary()["days"][0]["distributors"]["digikey"]["sent"] == 1
    finally:
        await client.close()
        store.close()


async def test_a_batch_still_running_is_already_counted_for_what_it_sent(clock):
    """Sends are counted as they go out (by the charge), so a part_lifecycle batch still waiting is
    already in the stats, and cancelling it doesn't count them again."""
    gate = asyncio.Event()
    client, _, store, _ = capped_client(clock, Gated(gate), limit=5)
    try:
        task = asyncio.create_task(client.lifecycle(["LM358DR"], caller=CALLER))
        for _ in range(5):
            await asyncio.sleep(0)
        assert stats.usage.summary()["days"][0]["distributors"]["digikey"]["sent"] == 1  # before any answer
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert stats.usage.summary()["days"][0]["distributors"]["digikey"]["sent"] == 1  # and not again
    finally:
        await client.close()
        store.close()


async def test_close_stops_a_batch_still_waiting_for_a_slot(clock):
    """A part_lifecycle batch queued for a request slot when the client closes is cancelled with
    it: nothing goes out (or is counted) after close()."""
    gate = asyncio.Event()
    session = Gated(gate)
    client, _, store, _ = capped_client(clock, session, limit=5, concurrency=1)
    try:
        holder = asyncio.create_task(client.lookup("AO3400A", caller=PLATFORM))  # takes the only slot
        for _ in range(5):
            await asyncio.sleep(0)
        batch = asyncio.create_task(client.lifecycle(["LM358DR"], caller=CALLER))
        for _ in range(5):
            await asyncio.sleep(0)
        await client.close()
        assert batch.done() and holder.done()
        gate.set()
        for _ in range(5):
            await asyncio.sleep(0)
        assert not any("LM358DR" in path for path in session.paths)
        assert stats.usage.summary()["days"][0]["distributors"]["digikey"]["sent"] == 1  # the holder's only
    finally:
        await client.close()
        store.close()


async def test_a_batch_with_two_refused_requests_counts_one_refusal(clock):
    """Two requests of one batch in flight, both refused: one refusal, per lookup or batch as in 0.10.4."""
    gate = asyncio.Event()
    session = Gated(gate, {"/suggestions": [Reply(403, {}), Reply(403, {})]})
    site, _ = make_site(clock, session, concurrency=2)
    task = asyncio.create_task(site.statuses(["LM358DR", "AO3400A"]))
    for _ in range(10):  # both requests reach the session (held there)
        await asyncio.sleep(0)
    gate.set()
    with pytest.raises(SiteUnavailable):
        await task
    assert len(session.paths) == 2
    assert stats.usage.summary()["days"][0]["distributor_limits"]["digikey"]["refusals"]["refused"] == 1


async def test_two_lookups_refused_count_two_refusals(clock):
    """Separate lookups each count their own refusal."""
    session = Session({"/suggestions": [Reply(403, {}), Reply(403, {})]})
    site, _ = make_site(clock, session)
    with pytest.raises(SiteUnavailable):
        await site.lookup("LM358DR")
    clock.advance(DIGIKEY_SITE_PAUSE + 1)  # past the first refusal's pause, so the next one sends
    with pytest.raises(SiteUnavailable):
        await site.lookup("AO3400A")
    assert sum(path.startswith("/suggestions") for path in session.paths) == 2
    assert stats.usage.summary()["days"][0]["distributor_limits"]["digikey"]["refusals"]["refused"] == 2


async def test_a_number_that_found_no_slot_is_counted_at_once_even_if_the_batch_is_cancelled(clock):
    client, _, store, _ = capped_client(clock, limit=10)
    started = asyncio.Event()

    async def statuses(numbers, sent=None, charge=None, held=None):
        assert charge(numbers[0])
        sent.add(numbers[0])
        held(numbers[1], SiteUnavailable(30, paused=False))  # gave up waiting for a slot, nothing sent
        started.set()
        await asyncio.Event().wait()  # the first number still waiting for its answer

    client._site.statuses = statuses
    try:
        task = asyncio.create_task(client.lifecycle(["PARTA1", "PARTB2"], caller=CALLER))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        today = stats.usage.summary()["days"][0]
        assert (today["distributors"]["digikey"]["sent"], today["distributors"]["digikey"]["rate_limited"]) == (1, 1)
        assert today["distributor_limits"]["digikey"]["held_back"]["other"] == 1
        assert (sum(client.callers._counts.values()), sum(client.held_back._counts.values())) == (1, 1)
    finally:
        await client.close()
        store.close()


async def test_the_site_tells_a_batch_when_a_number_finds_no_slot(clock):
    """_isolated hands a number's busy SiteUnavailable to the batch's held callback, once, and only
    for a number with nothing sent (one already sent was counted when it went out)."""
    from pcbparts_mcp import digikey_site
    site, _ = make_site(clock)
    told: list[str] = []

    async def busy():
        raise SiteUnavailable(30, paused=False)

    async def run(sent):
        with digikey_site._scope(sent, None, held=lambda number, error: told.append(number)):
            return await site._isolated(site._for_number("LM358DR", busy()))

    assert isinstance(await asyncio.create_task(run(set())), SiteUnavailable) and told == ["LM358DR"]
    told.clear()
    assert isinstance(await asyncio.create_task(run({"LM358DR"})), SiteUnavailable) and told == []


async def test_close_also_stops_a_lookup_started_while_closing(clock):
    client, _, store, _ = capped_client(clock, limit=5)
    later: list[asyncio.Task] = []

    async def first():
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:  # a new lookup arrives while close() waits on this one
            task = asyncio.create_task(asyncio.Event().wait())
            client._tasks.add(task)
            task.add_done_callback(client._tasks.discard)
            later.append(task)
            raise

    task = asyncio.create_task(first())
    client._tasks.add(task)
    task.add_done_callback(client._tasks.discard)
    await asyncio.sleep(0)
    try:
        await client.close()
        assert later and later[0].cancelled() and not client._tasks
    finally:
        store.close()


async def test_nothing_goes_out_after_close_even_for_a_lookup_queued_before_it(clock):
    client, session, store, _ = capped_client(clock, limit=5)
    try:
        queued = asyncio.create_task(client.lookup("LM358DR", caller=CALLER))  # created, not yet run
        await client.close()
        assert (await queued).kind == "limited"
        assert session.paths == []
    finally:
        await client.close()
        store.close()


async def test_a_held_number_retries_from_when_it_gave_up(clock):
    """Gave up waiting for a slot at 23:59:55 (its address used up), the batch done at 00:00:10:
    its day has reset, so retry_after is 1, not the 5 s it was told then."""
    clock.now = NOW + 12 * 3600 - 5
    client, _, store, day = capped_client(clock, limit=1)

    async def statuses(numbers, sent=None, charge=None, held=None):
        assert charge(numbers[0])
        sent.add(numbers[0])
        held(numbers[1], SiteUnavailable(30, paused=False))  # the address is used up now: until 00:00 UTC
        clock.advance(15)
        return {numbers[0]: [(numbers[0], "Maker", "Active", None)], numbers[1]: SiteUnavailable(30, paused=False)}

    client._site.statuses = statuses
    try:
        answers = await client.lifecycle(["PARTA1", "PARTB2"], caller=CALLER)
        assert answers["PARTB2"].kind == "limited" and answers["PARTB2"].retry_after == 1
    finally:
        await client.close()
        store.close()


async def test_a_held_number_in_a_batch_a_pause_then_stops_waits_for_the_pause(clock):
    client, _, store, _ = capped_client(clock, limit=10)

    async def statuses(numbers, sent=None, charge=None, held=None):
        held(numbers[0], SiteUnavailable(90, paused=False))  # no slot within the slot wait
        raise SiteUnavailable(DIGIKEY_SITE_PAUSE, paused=True, sent=True, refused=True)  # a sibling paused all

    client._site.statuses = statuses
    try:
        answers = await client.lifecycle(["PARTA1", "PARTB2"], caller=CALLER)
        assert answers["PARTA1"].retry_after == DIGIKEY_SITE_PAUSE  # not the 90 s it was told on giving up
        assert answers["PARTB2"].retry_after == DIGIKEY_SITE_PAUSE
    finally:
        await client.close()
        store.close()


async def test_a_held_number_in_a_batch_that_ends_normally_waits_for_a_pause_begun_since(clock):
    client, _, store, _ = capped_client(clock, limit=10)

    async def statuses(numbers, sent=None, charge=None, held=None):
        assert charge(numbers[0])
        sent.add(numbers[0])
        held(numbers[1], SiteUnavailable(1, paused=False))  # no slot: try again in a second
        client._site._refused("HTTP 403 from another lookup")  # ... but the site pauses meanwhile
        return {numbers[0]: [(numbers[0], "Maker", "Active", None)], numbers[1]: SiteUnavailable(1, paused=False)}

    client._site.statuses = statuses
    try:
        answers = await client.lifecycle(["PARTA1", "PARTB2"], caller=CALLER)
        assert answers["PARTB2"].retry_after == DIGIKEY_SITE_PAUSE
    finally:
        await client.close()
        store.close()


async def test_the_api_client_sends_nothing_after_close(clock):
    client = DigiKeyClient("id", "secret", store=DistributorStore(clock=clock))
    await client.close()
    with pytest.raises(httpx.ConnectError):
        client._get_http()


async def test_a_number_its_address_cannot_send_takes_no_pacer_turn(clock):
    """Refused before the slot and the pacer: a capped address's batch doesn't hold up others."""
    client, session, store, day = capped_client(clock, limit=1)
    try:
        day.record(CALLER)  # used up after the batch was admitted (the up-front check passed earlier)
        site = client._site
        before = clock()
        found = await site.statuses(["LM358DR", "AO3400A", "AD7747ARUZ"], sent=set(), charge=client._charge(CALLER))
        assert {type(v) for v in found.values()} == {AddressCapReached}
        assert session.paths == [] and clock() == before  # no pacer wait at all
        held = stats.usage.summary()["days"][0]["distributor_limits"]["digikey"]["held_back"]["address_daily"]
        assert held == 3
    finally:
        await client.close()
        store.close()
