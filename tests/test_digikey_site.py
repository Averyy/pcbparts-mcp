"""0.10.4: DigiKey lookups without API credentials (digikey_site.py) and their wiring into
DigiKeyClient, part_lifecycle and the server. No network: answers recorded from the site on
2026-11-20 (tests/fixtures/digikey_site/answers.json, trimmed to the fields read), fake sessions and
fake clocks."""

import asyncio
import json
import logging
from pathlib import Path

import httpx
import pytest
import wafer

import pcbparts_mcp.server as server
from pcbparts_mcp import stats
from pcbparts_mcp.cache import DailyQuota, Pacer, QuotaPool
from pcbparts_mcp.digikey import DigiKeyClient, DigiKeyError
from pcbparts_mcp.digikey_site import (
    BASE_URL, DIGIKEY_SITE_PAUSE, DigiKeySite, SiteFailed, SiteUnavailable, decode_state, encode_state, lz_decode, lz_encode,
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
def clock():
    return Clock()


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
    site, session = make_site(clock, Session({"/suggestions": [down, down]}))
    for number in ("TP4056", "AO3400A"):
        with pytest.raises(SiteFailed):
            await site.lookup(number)
    await site.lookup("LM358DR")
    session.script["/suggestions"] = [down, down]
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
    client, _, store = keyless_client(clock, Session({"/suggestions": [wafer.ConnectionFailed(BASE_URL, "reset")]}))
    try:
        with pytest.raises(DigiKeyError):
            await client.lookup("LM358DR")
        assert store.get_answer("digikey", "LM358DR") is None
    finally:
        await client.close()
        store.close()


async def test_no_daily_quota_or_address_cap(clock):
    """Without credentials nothing counts against a day: the per-address cap (Mouser and the
    DigiKey API's) doesn't apply."""
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
    client = MouserClient(api_key="k", quota=DailyQuota("Mouser", 1000), store=store)
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


async def test_server_without_credentials_and_switched_on_builds_the_keyless_client(monkeypatch):
    from fastmcp import Client
    monkeypatch.setenv("DIGIKEY_LOOKUP", "site")
    monkeypatch.setattr(server, "_digikey_client", None)  # put back after: startup sets the global
    async with Client(server.mcp):
        assert server._digikey_client is not None and server._digikey_client.unmetered
        assert "digikey" not in server._distributor_quotas  # no daily quota
        body = json.loads((await server.health(None)).body)
        assert body["distributor_quota"]["digikey"] == {"paused_until": None}


async def test_server_without_credentials_by_default_has_no_digikey(monkeypatch):
    """Off unless switched on: an install without credentials has no DigiKey, as before 0.10.4."""
    from fastmcp import Client
    monkeypatch.setattr(server, "_digikey_client", None)  # startup must leave it so
    async with Client(server.mcp):
        assert server._digikey_client is None
        reply = await server.digikey_get_part(part_number="LM358P")
        assert reply["error"].startswith("DigiKey API credentials not configured")
        assert json.loads((await server.health(None)).body)["distributor_quota"] == {}


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

    site, session = make_site(clock, Slow({LM358DR_SUGGESTIONS: [Reply(403, {}), wafer.ConnectionFailed(BASE_URL, "reset")]}))
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
        return [row.product_id for row in rows]

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
    site, session = make_site(clock, Session({"/suggestions?keywordSearch=TP4056": [down],
                                              "/detail-page/807741": [down]}))
    found = await site.statuses(["LM358DR", "AD7747ARUZ", "TP4056", "SMAJ36CA", "AO3414", "1-1470364-2"])
    assert isinstance(found["TP4056"], SiteFailed)
    assert found["AD7747ARUZ"] == [("AD7747ARUZ", "Analog Devices Inc.", "Last Time Buy", None)]
    assert len(found["SMAJ36CA"]) == 14 and site.status()["paused_until"] is None


async def test_lifecycle_keeps_a_batchs_answers_when_one_number_fails(clock):
    down = wafer.WaferTimeout(BASE_URL, 20)
    client, _, store = keyless_client(clock, Session({"/suggestions?keywordSearch=TP4056": [down]}))
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
