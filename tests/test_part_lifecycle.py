"""0.10.0: Mouser answers kept per part (3 days), every Mouser/DigiKey answer feeding the 90-day
lifecycle store, and part_lifecycle. No network: httpx.MockTransport fakes and fake clocks."""

import asyncio
import datetime
import json
import re

import httpx
import pytest
from fastmcp import Client

import pcbparts_mcp.server as server
from pcbparts_mcp import stats
from pcbparts_mcp.cache import DailyQuota, Pacer, QuotaPool
from pcbparts_mcp.digikey import DigiKeyClient
from pcbparts_mcp.distributor_store import DistributorStore
from pcbparts_mcp.lifecycle import Reading
from pcbparts_mcp.mouser import MouserClient, MouserError, _normalize_part

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 18, 12, tzinfo=UTC).timestamp()
MIDNIGHT = datetime.datetime(2026, 11, 19, tzinfo=UTC).timestamp()
DAY = 86400


class Clock:
    def __init__(self, now: float = NOW):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _alnum(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def mouser_part(mpn, maker="Texas Instruments", mouser_pn=None, lifecycle=None):
    part = {"MouserPartNumber": mouser_pn or f"595-{mpn}", "ManufacturerPartNumber": mpn, "Manufacturer": maker,
            "Description": "", "Category": "", "AvailabilityInStock": "100", "Min": "1",
            "PriceBreaks": [{"Quantity": 1, "Price": "$0.50", "Currency": "USD"}], "ProductAttributes": []}
    if lifecycle:
        part["LifecycleStatus"] = lifecycle
    return part


class FakeMouser:
    """Answers like Mouser's loose search: every listed part whose MPN or Mouser PN starts with a
    number asked. responses: raw replies to send first instead."""

    def __init__(self, *parts, responses=()):
        self.parts = list(parts)
        self.responses = list(responses)
        self.sent: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        numbers = json.loads(request.content)["SearchByPartRequest"]["mouserPartNumber"]
        self.sent.append(numbers)
        if self.responses:
            return self.responses.pop(0)
        asked = [_alnum(n) for n in numbers.split("|")]
        hits = [p for p in self.parts
                if any(_alnum(p["ManufacturerPartNumber"]).startswith(a) or _alnum(p["MouserPartNumber"]).startswith(a)
                       for a in asked)]
        return httpx.Response(200, json={"Errors": [], "SearchResults": {"NumberOfResult": len(hits), "Parts": hits}})


def dk_product(mpn, maker="Texas Instruments", status="Active", **extra):
    return {"ManufacturerProductNumber": mpn, "Manufacturer": {"Name": maker}, "ProductStatus": {"Status": status},
            "QuantityAvailable": 10, "ProductVariations": [], "Parameters": [], **extra}


class FakeDigiKey:
    def __init__(self, *products, responses=()):
        self.products = list(products)
        self.responses = list(responses)
        self.asked: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 599})
        keyword = json.loads(request.content)["Keywords"]
        self.asked.append(keyword)
        if self.responses:
            return self.responses.pop(0)
        hits = [p for p in self.products if p["ManufacturerProductNumber"].casefold() == keyword.casefold()]
        return httpx.Response(200, json={"Products": hits}) if hits else httpx.Response(404)


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
async def setup(clock, monkeypatch):
    """Build the server's clients on one store, as lifespan does. Returns a factory."""
    made = []

    def create(mouser=None, digikey=None, mouser_limit=1000, digikey_limit=1000, store=None,
               mouser_per_minute=None):
        store = store or DistributorStore(clock=clock)
        mq = DailyQuota("Mouser", mouser_limit, clock=clock, own_key="Mouser API key", per_minute=mouser_per_minute)
        dq = QuotaPool([DailyQuota("DigiKey", digikey_limit, clock=clock, own_key="DigiKey API credentials")])
        m = d = None
        if mouser is not None:
            m = MouserClient(api_key="k", quota=mq, store=store)
            m._client = httpx.AsyncClient(transport=httpx.MockTransport(mouser))
        if digikey is not None:
            d = DigiKeyClient(client_id="id", client_secret="secret", quota=dq, store=store)
            d._http = httpx.AsyncClient(transport=httpx.MockTransport(digikey))
            d._pacer = Pacer(1e6)
        monkeypatch.setattr(server, "_mouser_client", m)
        monkeypatch.setattr(server, "_digikey_client", d)
        monkeypatch.setattr(server, "_distributor_store", store)
        made.append((m, d, store))
        return m, d, store, mq, dq

    yield create
    for m, d, store in made:
        for c in (m, d):
            if c is not None:
                await c.close()
        store.close()


async def lifecycle(parts):
    return await server.part_lifecycle(parts=parts)


async def settle():
    """Let started lookups reach their requests."""
    for _ in range(5):
        await asyncio.sleep(0)


# --- Mouser answers kept per part ---

class TestMouserPerPart:
    async def test_batch_parts_serve_later_calls(self, setup):
        fake = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P"))
        m, _, _, mq, _ = setup(mouser=fake)
        first = await m.get_part("LM358P|NE555P")
        assert [r["mfr_part_number"] for r in first["results"]] == ["LM358P", "NE555P"]
        alone = await m.get_part("ne555p")
        assert [r["mfr_part_number"] for r in alone["results"]] == ["NE555P"]
        both = await m.get_part("NE555P|LM358P|TL431")  # only TL431 isn't kept yet
        assert fake.sent == ["LM358P|NE555P", "TL431"]
        assert both["not_found"] == ["TL431"] and both["total"] == 2
        assert mq.status()["used_today"] == 2  # kept answers never count

    async def test_unclear_result_keeps_the_batch_not_the_part(self, setup):
        """LM358P can be Mouser's loose match for LM358 too: LM358 isn't kept on its own."""
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, store, _, _ = setup(mouser=fake)
        first = await m.get_part("LM358|LM358P")
        assert first["total"] == 1 and "not_found" not in first
        assert await m.get_part("LM358|LM358P") == first  # the batch, kept under its numbers
        await m.get_part("LM358P")  # LM358P is the part itself: kept on its own
        assert len(fake.sent) == 1
        await m.get_part("LM358")
        assert fake.sent == ["LM358|LM358P", "LM358"]
        # Its lifecycle is kept (it's LM358P's own); LM358 was never "not listed" by an unclear batch
        assert [r.mpn for r in store.readings("LM358P")] == ["LM358P"]

    async def test_a_kept_batch_forgets_its_not_found_parts_after_a_day(self, setup, clock):
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, _, _, _ = setup(mouser=fake)
        assert (await m.get_part("LM358|LM358P|NOPE1"))["not_found"] == ["NOPE1"]
        clock.advance(DAY - 1)
        await m.get_part("LM358|LM358P|NOPE1")
        assert len(fake.sent) == 1
        clock.advance(1)
        fake.parts.append(mouser_part("NOPE1"))  # listed since
        assert "not_found" not in await m.get_part("LM358|LM358P|NOPE1")
        assert fake.sent[1:] == ["LM358|NOPE1"]  # LM358P is kept on its own

    async def test_result_matching_no_number_keeps_nothing_per_part(self, setup):
        odd = mouser_part("XYZ-1", mouser_pn="123-XYZ1")
        fake = FakeMouser(responses=[httpx.Response(200, json={"Errors": [], "SearchResults": {
            "Parts": [mouser_part("LM358P"), odd]}})] * 2)
        m, _, store, _, _ = setup(mouser=fake)
        reply = await m.get_part("LM358P|NE555P")
        assert [r["mfr_part_number"] for r in reply["results"]] == ["LM358P", "XYZ-1"]  # still returned
        assert reply["not_found"] == ["NE555P"]
        assert store.get_answer("mouser", "LM358P") is None and store.get_answer("mouser", "NE555P") is None
        assert store.readings("XYZ-1") == [] and store.readings("NE555P") == []
        assert await m.get_part("LM358P|NE555P") == reply and len(fake.sent) == 1

    async def test_kept_three_days_and_not_found_one(self, setup, clock):
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, _, _, _ = setup(mouser=fake)
        await m.get_part("LM358P")
        await m.get_part("NOPE1")
        clock.advance(DAY - 1)
        await m.get_part("LM358P")
        await m.get_part("NOPE1")
        assert len(fake.sent) == 2
        clock.advance(1)
        await m.get_part("NOPE1")
        assert len(fake.sent) == 3
        clock.advance(2 * DAY - 1)
        await m.get_part("LM358P")
        assert len(fake.sent) == 3
        clock.advance(1)
        await m.get_part("LM358P")
        assert len(fake.sent) == 4

    async def test_observed_at_is_the_oldest_answer(self, setup, clock):
        fake = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P"))
        m, _, _, _, _ = setup(mouser=fake)
        await m.get_part("LM358P")
        clock.advance(3600)
        reply = await m.get_part("NE555P|LM358P")
        assert reply["observed_at"] == "2026-11-18T12:00:00+00:00"
        assert (await m.get_part("NE555P"))["observed_at"] == "2026-11-18T13:00:00+00:00"

    async def test_answers_write_lifecycle(self, setup):
        fake = FakeMouser(mouser_part("AP2553W6-7", maker="Diodes Incorporated",
                                      lifecycle="Not Recommended for New Designs"), mouser_part("LM358P"))
        m, _, store, _, _ = setup(mouser=fake)
        reply = await m.get_part("AP2553W6-7|LM358P|NOPE1")
        assert [r["lifecycle_status"] for r in reply["results"]] == ["nrnd", "active"]
        assert [r["lifecycle"] for r in reply["results"]] == ["Not Recommended for New Designs", None]
        (nrnd,) = store.readings("AP2553W6-7")
        assert (nrnd.status, nrnd.raw, nrnd.maker, nrnd.source) == (
            "nrnd", "Not Recommended for New Designs", "Diodes Incorporated", "mouser")
        assert store.readings("LM358P")[0].raw == "not stated by Mouser"
        assert [(r.found, r.source) for r in store.readings("NOPE1")] == [(False, "mouser")]

    async def test_unrelated_results_dont_make_a_miss_live_three_days(self, setup, clock):
        """A lone number owns whatever Mouser returns for it; when none of it matches, the reply's
        not_found names it and it's kept a day, not as long as a found part."""
        odd = mouser_part("XYZ-1", mouser_pn="123-XYZ1")
        fake = FakeMouser(responses=[httpx.Response(200, json={"Errors": [], "SearchResults": {
            "NumberOfResult": 1, "Parts": [odd]}})] * 2)
        m, _, _, _, _ = setup(mouser=fake)
        reply = await m.get_part("OLDNAME1")
        assert reply["not_found"] == ["OLDNAME1"] and [r["mfr_part_number"] for r in reply["results"]] == ["XYZ-1"]
        clock.advance(DAY - 1)
        assert await m.get_part("OLDNAME1") == reply and len(fake.sent) == 1
        clock.advance(1)
        await m.get_part("OLDNAME1")
        assert len(fake.sent) == 2

    async def test_a_kept_batch_with_an_unmatched_answer_lasts_a_day(self, setup, clock):
        """The kept-batch check reads matched too (an answer can hold results and still not match)."""
        fake = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P"))
        m, _, store, _, _ = setup(mouser=fake)
        found, odd = _normalize_part(mouser_part("LM358P")), _normalize_part(mouser_part("XYZ-1", mouser_pn="123-XYZ1"))
        store.put_answer("mouser", "batch:LM358P|OLDNAME1", {"answers": {
            "LM358P": {"results": [found], "matched": True}, "OLDNAME1": {"results": [odd], "matched": False}},
            "extras": []}, True, clock())
        clock.advance(DAY)
        await m.get_part("LM358P|OLDNAME1")
        assert fake.sent == ["LM358P|OLDNAME1"]

    async def test_limit_refusals_are_not_kept(self, setup):
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, store, mq, _ = setup(mouser=fake, mouser_limit=0)
        assert "daily quota exceeded" in (await m.get_part("LM358P"))["error"]
        assert store.get_answer("mouser", "LM358P") is None and fake.sent == []
        assert m.retry_after() == MIDNIGHT - NOW


# --- Mouser's 50-result cap ---

class CappedMouser(FakeMouser):
    """Mouser's cap: the parts each number asked finds, number by number, cut at `cap` (50), with
    NumberOfResult counting all of them."""

    def __init__(self, *parts, cap=50, total=None):
        super().__init__(*parts)
        self.cap, self.total = cap, total

    def __call__(self, request: httpx.Request) -> httpx.Response:
        numbers = json.loads(request.content)["SearchByPartRequest"]["mouserPartNumber"]
        self.sent.append(numbers)
        hits = []
        for asked in (_alnum(n) for n in numbers.split("|")):
            hits += [p for p in self.parts if _alnum(p["ManufacturerPartNumber"]).startswith(asked) and p not in hits]
        return httpx.Response(200, json={"Errors": [], "SearchResults": {
            "NumberOfResult": len(hits) if self.total is None else self.total, "Parts": hits[:self.cap]}})


BROAD = [mouser_part(f"LM358{i:02}X") for i in range(60)]  # more than one reply holds


class TestResultCap:
    async def test_crowded_numbers_are_asked_again(self, setup):
        fake = CappedMouser(*BROAD, mouser_part("TPS54331DR"), mouser_part("NE555P"))
        m, _, store, mq, _ = setup(mouser=fake)
        reply = await m.get_part("LM358|TPS54331DR|NE555P")
        assert fake.sent == ["LM358|TPS54331DR|NE555P", "TPS54331DR|NE555P"]  # without the number that filled it
        assert "not_found" not in reply and mq.status()["used_today"] == 2
        assert [r["mfr_part_number"] for r in reply["results"]][-2:] == ["TPS54331DR", "NE555P"]
        assert len(reply["results"]) == 52
        # Kept per part from the second reply; LM358's own 50 too, but no "not listed" from the capped one
        assert store.get_answer("mouser", "TPS54331DR") is not None
        assert [r.found for r in store.readings("LM358")] == []
        assert (await m.get_part("TPS54331DR|NE555P"))["total"] == 2 and len(fake.sent) == 2

    async def test_number_of_result_above_the_parts_sent_is_capped_too(self, setup):
        fake = CappedMouser(*BROAD[:40], mouser_part("TPS54331DR"), cap=30)
        m, _, _, _, _ = setup(mouser=fake)
        reply = await m.get_part("LM358|TPS54331DR")
        assert fake.sent == ["LM358|TPS54331DR", "TPS54331DR"] and "not_found" not in reply

    async def test_one_more_request_at_most_and_no_negative_from_a_capped_reply(self, setup):
        """Two broad numbers: the second request is capped too, and TPS54331DR is left unchecked:
        not found in this reply, nothing kept, and part_lifecycle doesn't call it not listed."""
        fake = CappedMouser(*BROAD, *(mouser_part(f"LM324{i:02}X") for i in range(60)), mouser_part("TPS54331DR"))
        digikey = FakeDigiKey(dk_product("TPS54331DR"))
        m, _, store, _, _ = setup(mouser=fake, digikey=digikey)
        result = (await lifecycle(["LM358", "LM324", "TPS54331DR"]))["results"][2]
        assert fake.sent == ["LM358|LM324|TPS54331DR", "LM324|TPS54331DR"]
        assert result == {"input": "TPS54331DR", "mpn": "TPS54331DR", "status": "unknown", "lookup_failed": True}
        assert "TPS54331DR" not in digikey.asked
        assert store.get_answer("mouser", "TPS54331DR") is None and store.readings("TPS54331DR") == []
        assert store.get_answer("mouser", "batch:LM358|LM324|TPS54331DR") is None
        reply = await m.get_part("LM358|LM324|TPS54331DR")  # the broad ones are kept: TPS54331DR goes alone
        assert fake.sent[2:] == ["TPS54331DR"] and "not_found" not in reply

    async def test_a_limit_holding_back_the_second_request(self, setup):
        fake = CappedMouser(*BROAD, mouser_part("TPS54331DR"))
        digikey = FakeDigiKey(dk_product("TPS54331DR"))
        _, _, store, _, _ = setup(mouser=fake, digikey=digikey, mouser_per_minute=1)
        reply = await lifecycle(["LM358", "TPS54331DR"])
        assert fake.sent == ["LM358|TPS54331DR"]  # the minute's one request
        assert reply["results"][1] == {"input": "TPS54331DR", "mpn": "TPS54331DR", "status": "unknown",
                                       "retry_after": 60}
        assert "TPS54331DR" not in digikey.asked  # a minute's wait isn't Mouser not listing it
        assert store.get_answer("mouser", "TPS54331DR") is None and store.readings("TPS54331DR") == []

    async def test_a_single_broad_number_is_not_asked_again(self, setup):
        fake = CappedMouser(*BROAD)
        m, _, store, _, _ = setup(mouser=fake)
        assert (await m.get_part("LM358"))["total"] == 50
        assert fake.sent == ["LM358"]
        assert store.get_answer("mouser", "LM358") is not None  # what Mouser answers for it alone
        assert store.readings("LM358") == []  # no "not listed": the part itself may be past the cap


# --- DigiKey answers in the store ---

class TestDigiKeyStore:
    async def test_end_of_life_and_last_buy_date(self, setup):
        fake = FakeDigiKey(dk_product("TPS1234", status="Active", EndOfLife=True,
                                      DateLastBuyChance="2027-03-31T00:00:00Z"))
        _, d, store, _, _ = setup(digikey=fake)
        reply = await d.get_part("TPS1234")
        result = reply["results"][0]
        assert result["lifecycle"] == "Active"  # unchanged field
        assert (result["lifecycle_status"], result["last_buy_date"]) == ("last_time_buy", "2027-03-31")
        assert reply["observed_at"] == "2026-11-18T12:00:00+00:00"
        (reading,) = store.readings("TPS1234")
        assert (reading.status, reading.raw, reading.last_buy_date) == ("last_time_buy", "Active (end of life)", "2027-03-31")

    async def test_not_found_is_kept_as_not_listed(self, setup):
        fake = FakeDigiKey()
        _, d, store, _, _ = setup(digikey=fake)
        assert (await d.get_part("nope1"))["error"] == "Part not found: nope1"
        assert (await d.get_part("NOPE1"))["error"] == "Part not found: NOPE1"  # kept: no request
        assert fake.asked == ["nope1"]
        assert [(r.found, r.source) for r in store.readings("NOPE1")] == [(False, "digikey")]


# --- part_lifecycle ---

class TestOneSharedCache:
    async def test_lifecycle_then_mouser_get_part_is_one_request(self, setup):
        fake = FakeMouser(mouser_part("LM358P"))
        setup(mouser=fake)
        assert (await lifecycle(["LM358P"]))["results"][0]["status"] == "active"
        reply = await server.mouser_get_part(part_number="LM358P")
        assert reply["results"][0]["mfr_part_number"] == "LM358P"
        assert fake.sent == ["LM358P"]

    async def test_mouser_get_part_then_lifecycle_is_one_request(self, setup):
        fake = FakeMouser(mouser_part("LM358P", lifecycle="Obsolete"))
        _, _, _, mq, _ = setup(mouser=fake)
        await server.mouser_get_part(part_number="LM358P")
        result = (await lifecycle(["LM358P"]))["results"][0]
        assert (result["status"], result["raw"], result["source"]) == ("obsolete", "Obsolete", "mouser")
        assert fake.sent == ["LM358P"] and mq.status()["used_today"] == 1

    async def test_store_outlives_the_answer_cache(self, setup, clock):
        fake = FakeMouser(mouser_part("LM358P"))
        setup(mouser=fake)
        await lifecycle(["LM358P"])
        clock.advance(89 * DAY)
        assert (await lifecycle(["LM358P"]))["results"][0]["status"] == "active"
        assert len(fake.sent) == 1
        clock.advance(DAY)
        await lifecycle(["LM358P"])
        assert len(fake.sent) == 2

    async def test_digikey_answer_then_lifecycle_is_free(self, setup):
        mouser, digikey = FakeMouser(), FakeDigiKey(dk_product("AP2553W6-7", "Diodes Incorporated", "Not For New Designs"))
        setup(mouser=mouser, digikey=digikey)
        await server.digikey_get_part(product_number="AP2553W6-7")
        result = (await lifecycle(["AP2553W6-7"]))["results"][0]
        assert (result["status"], result["raw"], result["source"]) == ("nrnd", "Not For New Designs", "digikey")
        assert mouser.sent == [] and digikey.asked == ["AP2553W6-7"]


class TestLookups:
    async def test_reply_fields(self, setup):
        setup(mouser=FakeMouser(mouser_part("AP2553W6-7", "Diodes Incorporated", lifecycle="Not Recommended for New Designs")))
        reply = await lifecycle(["AP2553W6-7"])
        assert reply == {
            "results": [{"input": "AP2553W6-7", "mpn": "AP2553W6-7", "manufacturer": "Diodes Incorporated",
                         "status": "nrnd", "raw": "Not Recommended for New Designs", "source": "mouser",
                         "observed_at": "2026-11-18T12:00:00+00:00"}],
            "total": 1,
            "status_counts": {"active": 0, "nrnd": 1, "last_time_buy": 0, "obsolete": 0, "unknown": 0},
        }

    async def test_mouser_blank_is_active_and_digikey_not_asked(self, setup):
        mouser, digikey = FakeMouser(mouser_part("LM358P")), FakeDigiKey(dk_product("LM358P", status="Obsolete"))
        setup(mouser=mouser, digikey=digikey)
        result = (await lifecycle(["LM358P"]))["results"][0]
        assert (result["status"], result["raw"]) == ("active", "not stated by Mouser")
        assert digikey.asked == []

    async def test_digikey_when_mouser_does_not_list_it(self, setup):
        mouser = FakeMouser(mouser_part("LM358PE4"))  # a loose match, not the part
        digikey = FakeDigiKey(dk_product("LM358P", status="Discontinued at Digi-Key", Discontinued=True))
        _, _, store, _, _ = setup(mouser=mouser, digikey=digikey)
        result = (await lifecycle(["LM358P"]))["results"][0]
        assert (result["status"], result["raw"], result["source"]) == (
            "unknown", "Discontinued at Digi-Key", "digikey")
        assert digikey.asked == ["LM358P"]
        assert {(r.source, r.found) for r in store.readings("LM358P")} == {("mouser", False), ("digikey", True)}
        # Both answers are kept: a second call sends nothing
        await lifecycle(["LM358P"])
        assert len(mouser.sent) == 1 and digikey.asked == ["LM358P"]

    async def test_neither_lists_it(self, setup):
        setup(mouser=FakeMouser(), digikey=FakeDigiKey())
        reply = await lifecycle(["NOSUCH-1"])
        assert reply["results"][0] == {"input": "NOSUCH-1", "mpn": "NOSUCH-1", "status": "unknown",
                                       "not_found": True, "observed_at": "2026-11-18T12:00:00+00:00"}
        assert server._lifecycle_outcome(reply) == "not_found"
        assert server._call_reason("not_found", reply, None) == "part_not_found"

    async def test_ten_part_requests(self, setup):
        fake = FakeMouser(*(mouser_part(f"PART{i:02}X") for i in range(23)))
        _, _, _, mq, _ = setup(mouser=fake)
        reply = await lifecycle([f"PART{i:02}X" for i in range(23)] + ["part00x"])
        assert sorted(len(s.split("|")) for s in fake.sent) == [3, 10, 10]
        assert mq.status()["used_today"] == 3
        assert reply["status_counts"]["active"] == 24

    async def test_spent_limits_answer_unknown_with_retry_after(self, setup):
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, _, mq, dq = setup(mouser=fake, digikey=FakeDigiKey())
        await m.get_part("LM358P")
        mq._count = mq._limit  # the day's Mouser requests are spent; DigiKey's too
        dq.quotas[0]._count = dq.quotas[0]._limit
        reply = await lifecycle(["LM358P", "NE555P"])
        kept, missed = reply["results"]
        assert kept["status"] == "active"  # kept parts still answer
        assert missed == {"input": "NE555P", "mpn": "NE555P", "status": "unknown", "retry_after": MIDNIGHT - NOW}
        assert reply["retry_after"] == MIDNIGHT - NOW and "error" not in reply
        assert server._lifecycle_outcome(reply) == "ok"
        assert server._lifecycle_outcome({**reply, "results": [missed]}) == "rate_limited"

    async def test_mouser_spent_goes_to_digikey(self, setup):
        mouser, digikey = FakeMouser(mouser_part("LM358P")), FakeDigiKey(dk_product("LM358P"))
        setup(mouser=mouser, digikey=digikey, mouser_limit=0)
        result = (await lifecycle(["LM358P"]))["results"][0]
        assert (result["status"], result["source"]) == ("active", "digikey")
        assert mouser.sent == [] and digikey.asked == ["LM358P"]

    async def test_mouser_failure_is_lookup_failed_without_digikey(self, setup):
        """A failed Mouser lookup says nothing about whether Mouser lists the part: DigiKey's smaller
        day isn't spent on it."""
        mouser, digikey = FakeMouser(responses=[httpx.Response(503)]), FakeDigiKey(dk_product("LM358P", status="Obsolete"))
        setup(mouser=mouser, digikey=digikey)
        reply = await lifecycle(["LM358P"])
        assert reply["results"][0] == {"input": "LM358P", "mpn": "LM358P", "status": "unknown", "lookup_failed": True}
        assert digikey.asked == [] and "retry_after" not in reply

    async def test_our_minute_cap_is_retry_after_without_digikey(self, setup):
        mouser, digikey = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P")), FakeDigiKey(dk_product("NE555P"))
        setup(mouser=mouser, digikey=digikey, mouser_per_minute=1)
        assert (await lifecycle(["LM358P"]))["results"][0]["source"] == "mouser"
        reply = await lifecycle(["NE555P"])
        assert reply["results"][0] == {"input": "NE555P", "mpn": "NE555P", "status": "unknown", "retry_after": 60}
        assert reply["retry_after"] == 60 and digikey.asked == [] and len(mouser.sent) == 1

    async def test_mousers_minute_refusal_is_retry_after_without_digikey(self, setup):
        minute = {"Errors": [{"Code": "TooManyRequests", "Message": "Maximum calls per minute exceeded."}]}
        mouser, digikey = FakeMouser(responses=[httpx.Response(403, json=minute)]), FakeDigiKey(dk_product("LM358P"))
        setup(mouser=mouser, digikey=digikey)
        result = (await lifecycle(["LM358P"]))["results"][0]
        assert (result["status"], result["retry_after"]) == ("unknown", 60)
        assert digikey.asked == []

    async def test_mousers_daily_refusal_goes_to_digikey(self, setup):
        """Mouser's day spent (its refusal, every key): nothing goes to Mouser until the reset, so DigiKey answers."""
        daily = {"Errors": [{"Code": "TooManyRequests", "Message": "Maximum calls per day exceeded.",
                             "ResourceKey": "MaxCallPerDay"}]}
        mouser, digikey = FakeMouser(responses=[httpx.Response(403, json=daily)]), FakeDigiKey(dk_product("LM358P"))
        setup(mouser=mouser, digikey=digikey)
        result = (await lifecycle(["LM358P"]))["results"][0]
        assert (result["status"], result["source"]) == ("active", "digikey")
        assert len(mouser.sent) == 1 and digikey.asked == ["LM358P"]

    async def test_both_fail(self, setup):
        # Mouser not listing it sends it to DigiKey, whose lookup fails
        setup(mouser=FakeMouser(), digikey=FakeDigiKey(responses=[httpx.Response(500)]))
        reply = await lifecycle(["LM358P"])
        assert reply["results"][0]["lookup_failed"] is True
        assert server._lifecycle_outcome(reply) == "failed"
        assert server._call_reason("failed", reply, None) == "lifecycle_lookup_failed"
        assert "lifecycle_lookup_failed" in stats.REASONS

    async def test_only_digikey_configured(self, setup):
        setup(digikey=FakeDigiKey(dk_product("LM358P", status="Last Time Buy")))
        assert (await lifecycle(["LM358P"]))["results"][0]["status"] == "last_time_buy"

    async def test_neither_configured(self, monkeypatch):
        monkeypatch.setattr(server, "_mouser_client", None)
        monkeypatch.setattr(server, "_digikey_client", None)
        assert (await lifecycle(["LM358P"]))["error"].startswith("Mouser API key not configured")


class TestMakers:
    SHARED = (mouser_part("BSS138", "onsemi", "512-BSS138"), mouser_part("BSS138", "Nexperia", "771-BSS138",
                                                                         lifecycle="Obsolete"))

    async def test_several_makers_and_none_given(self, setup):
        setup(mouser=FakeMouser(*self.SHARED))
        result = (await lifecycle(["BSS138"]))["results"][0]
        assert result["status"] == "unknown" and "source" not in result
        assert [(m["manufacturer"], m["status"]) for m in result["makers"]] == [("Nexperia", "obsolete"), ("onsemi", "active")]

    async def test_the_maker_given_picks_one(self, setup):
        fake = FakeMouser(*self.SHARED)
        setup(mouser=fake)
        reply = await lifecycle([{"mpn": "BSS138", "manufacturer": "Nexperia USA Inc."}, {"mpn": "BSS138", "manufacturer": "onsemi"}])
        assert [(r["manufacturer"], r["status"]) for r in reply["results"]] == [("Nexperia", "obsolete"), ("onsemi", "active")]
        assert reply["results"][0]["input"] == {"mpn": "BSS138", "manufacturer": "Nexperia USA Inc."}
        assert len(fake.sent) == 1  # one number, one lookup

    async def test_one_maker_under_two_names(self, setup):
        """Mouser's "NXP Semiconductors" and DigiKey's "NXP USA Inc." are one maker: the stated NRND wins."""
        _, _, store, _, _ = setup(mouser=FakeMouser(), digikey=FakeDigiKey())
        store.put_readings([Reading("PCA9306DP", "NXP Semiconductors", "mouser", "active", "not stated by Mouser", NOW),
                            Reading("PCA9306DP", "NXP USA Inc.", "digikey", "nrnd", "Not For New Designs", NOW - DAY)])
        given, none = (await lifecycle([{"mpn": "PCA9306DP", "manufacturer": "NXP"}, "PCA9306DP"]))["results"]
        assert (given["status"], given["source"]) == ("nrnd", "digikey")
        assert (none["status"], none["source"], "makers" in none) == ("nrnd", "digikey", False)

    async def test_listed_only_under_other_makers(self, setup):
        digikey = FakeDigiKey()
        setup(mouser=FakeMouser(*self.SHARED), digikey=digikey)
        result = (await lifecycle([{"mpn": "BSS138", "manufacturer": "Diodes Incorporated"}]))["results"][0]
        assert result["status"] == "unknown" and result["manufacturer"] == "Diodes Incorporated"
        assert {m["manufacturer"] for m in result["makers"]} == {"onsemi", "Nexperia"}
        assert digikey.asked == ["BSS138"]  # Mouser doesn't list that maker's: DigiKey is asked


class TestInputs:
    async def test_lcsc_codes_use_the_catalog(self, setup, monkeypatch):
        class Catalog:
            def get_by_lcsc_batch(self, codes):
                assert codes == ["C7950", "C99999999"]  # once each
                return {"C7950": {"model": "LM358P", "manufacturer": "Texas Instruments"}}

            def get_sold_out_rows(self, codes):
                assert codes == ["C99999999"]  # only the codes the snapshot doesn't list
                return dict.fromkeys(codes)

        monkeypatch.setattr(server, "get_db", lambda: Catalog())
        setup(mouser=FakeMouser(mouser_part("LM358P")))
        reply = await lifecycle(["c7950", {"lcsc": "C7950"}, "C99999999"])
        first, second, missing = reply["results"]
        assert (first["input"], first["lcsc"], first["mpn"], first["status"]) == ("c7950", "C7950", "LM358P", "active")
        assert second["mpn"] == "LM358P"
        assert missing["error"] == "Part C99999999 not found" and missing["status"] == "unknown"

    async def test_gone_lcsc_codes_use_the_kept_part(self, setup, monkeypatch):
        """A code the snapshot no longer lists, kept after it left (stock under 10 or delisted:
        exactly when lifecycle matters), resolves to its MPN and maker instead of "not found"."""
        class Catalog:
            def get_by_lcsc_batch(self, codes):
                return dict.fromkeys(codes)

            def get_sold_out_rows(self, codes):
                return {"C2660": {"model": "IRFB4710PBF", "manufacturer": "Infineon Technologies", "gone": True},
                        "C99999999": None}

        monkeypatch.setattr(server, "get_db", lambda: Catalog())
        mouser = FakeMouser(mouser_part("IRFB4710PBF", "Infineon Technologies", lifecycle="Obsolete"))
        setup(mouser=mouser)
        gone, missing = (await lifecycle(["C2660", "C99999999"]))["results"]
        assert (gone["mpn"], gone["manufacturer"], gone["status"]) == ("IRFB4710PBF", "Infineon Technologies", "obsolete")
        assert missing["error"] == "Part C99999999 not found" and mouser.sent == ["IRFB4710PBF"]

    async def test_unusable_inputs_get_their_own_error(self, setup):
        fake = FakeMouser(mouser_part("LM358P"))
        setup(mouser=fake)
        reply = await lifecycle(["DNP", "", {"mpn": 5}, {"lcsc": "X12"}, "M" * 101,
                                 {"mpn": "LM358P", "manufacturer": "T" * 101}, "LM358P"])
        errors = [r.get("error", "") for r in reply["results"]]
        assert errors[0].startswith("Invalid part: 'DNP' is a BOM placeholder")
        assert errors[1] == "Give a part number or an LCSC code"
        assert errors[2].startswith("Invalid part: give an MPN")
        assert errors[3].startswith("lcsc must be an LCSC C-code")
        assert errors[4] == "MPN too long (max 100 characters)"
        assert errors[5] == "Manufacturer too long (max 100 characters)"
        assert reply["results"][6]["status"] == "active"
        assert reply["status_counts"]["unknown"] == 6 and fake.sent == ["LM358P"]
        assert server._lifecycle_outcome({**reply, "results": reply["results"][:6]}) == "bad_request"

    async def test_a_pipe_in_an_mpn_is_its_own_error(self, setup):
        """Mouser batches join numbers with "|": "LM358P|NE555P" as one MPN would be two numbers in
        a request, and ten such parts twenty, past Mouser's 10."""
        fake = FakeMouser(*(mouser_part(f"PART{i}X") for i in range(10)), mouser_part("NE555P"))
        setup(mouser=fake)
        parts = [f"PART{i}X|NE555P" for i in range(9)] + [{"mpn": "PART9X|NE555P"}, "NE555P"]
        reply = await lifecycle(parts)
        assert [r.get("error") for r in reply["results"][:10]] == [
            "Invalid part: an MPN can't contain '|' (give each part on its own)"] * 10
        assert reply["results"][10]["status"] == "active" and fake.sent == ["NE555P"]
        assert server._lifecycle_outcome({**reply, "results": reply["results"][:10]}) == "bad_request"

    async def test_counted_by_the_parts_own_errors_when_none_was_looked_up(self, setup, monkeypatch):
        class Down:
            def get_by_lcsc_batch(self, codes):
                raise OSError("database file is gone")

        class Empty:
            def get_by_lcsc_batch(self, codes):
                return {}

            def get_sold_out_rows(self, codes):
                return dict.fromkeys(codes)

        setup(mouser=FakeMouser())
        monkeypatch.setattr(server, "get_db", lambda: Down())
        down = await lifecycle(["C7950"])
        assert down["results"][0]["error"] == "Database not available"
        assert server._lifecycle_outcome(down) == "failed"
        assert server._call_reason("failed", down, None) == "service_not_ready"
        monkeypatch.setattr(server, "get_db", lambda: Empty())
        missing = await lifecycle(["C7950", "DNP"])
        assert server._lifecycle_outcome(missing) == "not_found"
        assert server._call_reason("not_found", missing, None) == "lcsc_not_found"

    async def test_json_array_string_and_a_single_part(self, setup):
        setup(mouser=FakeMouser(mouser_part("LM358P"), mouser_part("NE555P")))
        reply = await lifecycle('["LM358P", {"mpn": "NE555P"}]')
        assert [r["mpn"] for r in reply["results"]] == ["LM358P", "NE555P"]
        assert (await lifecycle("LM358P"))["total"] == 1

    async def test_list_limits(self, setup):
        setup(mouser=FakeMouser())
        assert (await lifecycle(["X1"] * 51))["error"] == "Too many parts (max 50, got 51)"
        assert (await lifecycle([]))["error"].startswith("Give at least one part")
        assert (await lifecycle("[1, 2"))["error"].startswith("Invalid parts: ")


class TestServer:
    async def test_tool_is_counted_and_read_only(self, setup):
        setup(mouser=FakeMouser(), mouser_limit=0)
        async with Client(server.mcp) as client:
            tools = {tool.name: tool for tool in await client.list_tools()}
            assert tools["part_lifecycle"].annotations.readOnlyHint is True
            result = await client.call_tool("part_lifecycle", {"parts": ["LM358P"]})
            assert result.structured_content["results"][0]["retry_after"] > 0
        assert stats.usage.summary()["days"][0]["tools"]["part_lifecycle"]["rate_limited"] == 1

    async def test_health_and_shared_store(self, tmp_path, monkeypatch):
        path = tmp_path / "distributor.db"
        monkeypatch.setattr(server, "DISTRIBUTOR_STORE_PATH", str(path))
        monkeypatch.setattr(server, "MOUSER_API_KEY", "test-key")
        monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "test-id")
        monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "test-secret")
        async with Client(server.mcp):
            body = json.loads((await server.health(None)).body)
            assert body["distributor_stored"] == {"answers": 0, "lifecycle": 0, "kept_across_restarts": True}
            assert server._mouser_client._store is server._distributor_store is server._digikey_client._store
        assert path.exists()


# --- review fixes, 2026-11-18 ---

class TestNotSentReason:
    NOT_SENT = [
        ("10k", "value"), ("4.7k", "value"), ("100nF", "value"), ("4.7uF", "value"), ("1R", "value"),
        ("10k 0402", "value"), ("100nF 50V 0603", "value"), ("4K7 1%", "value"), ("16Ω", "value"),
        ("10 kOhm", "value"), ("22pF/50V", "value"), ("8MHz", "value"),
        # Astra round 6: resistor codes, SI-prefixed units, decimals with a unit
        ("4k7", "value"), ("1R5", "value"), ("2M2", "value"), ("0R1", "value"), ("100R", "value"),
        ("22pF", "value"), ("10uH", "value"), ("1mH", "value"), ("3.3mA", "value"), ("2.2kΩ", "value"),
        ("4.7µF", "value"), ("1.5A", "value"), ("3.3V", "value"), ("0.25W", "value"), ("100mW", "value"),
        ("1.5a", "value"), ("10k 50V", "value"), ("100nF 25V X7R", "value"),
        # Astra round 7: E-series values (3 significant digits at most) in every form
        ("220R", "value"), ("15.8k", "value"), ("1000k", "value"), ("2200R", "value"),
        ("4700pF", "value"), ("4K7", "value"), ("4R75", "value"), ("1.21k 0603", "value"), ("10uH", "value"),
        # Astra round 8: a unit, a decimal point or a multiplier as the decimal point make it a value
        # (3 significant digits at most); a bare code only with 2
        ("47K", "value"), ("1M", "value"), ("4.75k", "value"), ("158kΩ", "value"), ("193mH", "value"),
        ("12.5pF", "value"), ("15K8", "value"), ("100 ohm", "value"), ("47K 1%", "value"),
        ("DNP", "placeholder"), ("N/A", "placeholder"), ("C7950", "lcsc_code"), ("c2040", "lcsc_code"),
        ("AB", "length"), ("X" * 41, "length"), ("LM358P中文", "not_ascii"), ("ＬＭ358", "not_ascii"),
    ]

    @pytest.mark.parametrize("number, reason", NOT_SENT, ids=[f"{r}{i}" for i, (_, r) in enumerate(NOT_SENT)])
    def test_numbers_no_distributor_lists(self, number, reason):
        from pcbparts_mcp.search.mpn import NOT_SENT_HINTS, NOT_SENT_REASONS, not_sent_reason
        assert not_sent_reason(number) == reason
        assert reason in NOT_SENT_REASONS and reason in NOT_SENT_HINTS

    SENT = [
        "1N4148", "LM358", "LM358P", "0805B103K500NT", "2N7002", "1N5819", "1N914", "BAT54", "STM32F103C8T6",
        "TPS54331DR", "595-LM358P", "296-1395-5-ND", "B2B-PH-K-S(LF)(SN)", "9774025151R", "885012206095",
        "RC0603FR-0710KL", "AMS1117-3.3", "SS14", "1206", "X7R", "LM358/NOPB", "74HC595", "C1815-Y",
        # Astra round 6: an integer and one unit letter is a part number (Hammond's 1590A enclosure was
        # read as 1590 amps and never sent), and so is a "voltage" or "power" with nothing else
        "1590A", "1590B", "1590BB", "1590BS", "1550A", "100V", "220W", "1000F", "47H", "1590MA",
        "1590A 0603", "50V 0603", "100V X7R",
        # Astra round 7: Hammond's 1590K, 1590R and 1590M matched as resistor codes; 159 and 155 aren't
        # E-series values, and 1591 has 4 significant digits
        "1590K", "1590R", "1590M", "1550M", "1591K", "1590K 0603",
        # Astra round 8: Hammond's 193M and 158M filter chokes; a bare code with 3 significant digits
        # can't be told from a part number
        "193M", "158M", "158k", "193M 0603",
    ]

    @pytest.mark.parametrize("number", SENT, ids=[f"pn{i}" for i in range(len(SENT))])
    def test_real_part_numbers_are_sent(self, number):
        from pcbparts_mcp.search.mpn import not_sent_reason
        assert not_sent_reason(number) is None



class TestIntegerAndUnitLetterIsSent:
    """Astra review round 6 (2026-11-18): Hammond's 1590A enclosure was taken for 1590 amps, so
    neither distributor was ever asked about it."""

    async def test_mouser_get_part(self, setup):
        fake = FakeMouser(mouser_part("1590A", "Hammond Manufacturing"))
        setup(mouser=fake)
        reply = await server.mouser_get_part(part_number="1590A|100V")
        assert fake.sent == ["1590A|100V"] and "not_sent" not in reply
        assert [r["mfr_part_number"] for r in reply["results"]] == ["1590A"]

    HAMMOND = ["1590K", "1590R", "1590M", "1550M", "1591K", "193M", "158M"]

    async def test_resistor_shaped_part_numbers_through_mouser(self, setup):
        """Astra review round 7: 1590K, 1590R and 1590M passed for resistor codes (1590 kOhm...)."""
        fake = FakeMouser(*(mouser_part(n, "Hammond Manufacturing") for n in self.HAMMOND))
        setup(mouser=fake)
        reply = await server.mouser_get_part(part_number="|".join(self.HAMMOND))
        assert fake.sent == ["|".join(self.HAMMOND)] and "not_sent" not in reply
        assert sorted(r["mfr_part_number"] for r in reply["results"]) == sorted(self.HAMMOND)

    async def test_resistor_shaped_part_numbers_through_digikey(self, setup):
        fake = FakeDigiKey(*(dk_product(n, "Hammond Manufacturing") for n in self.HAMMOND))
        setup(digikey=fake)
        for number in self.HAMMOND:
            reply = await server.digikey_get_part(product_number=number)
            assert reply["results"][0]["manufacturer"] == "Hammond Manufacturing" and "not_sent" not in reply
        assert fake.asked == self.HAMMOND

    async def test_resistor_shaped_part_numbers_through_part_lifecycle(self, setup):
        mouser = FakeMouser(*(mouser_part(n, "Hammond Manufacturing") for n in self.HAMMOND))
        setup(mouser=mouser, digikey=FakeDigiKey())
        parts = [{"mpn": n, "manufacturer": "Hammond Manufacturing"} for n in self.HAMMOND] + ["2200R", "15.8k"]
        rows = (await lifecycle(parts))["results"]
        count = len(self.HAMMOND)
        assert [(r["status"], r.get("source")) for r in rows[:count]] == [("active", "mouser")] * count
        assert [r.get("not_sent") for r in rows[count:]] == ["value", "value"]
        assert sorted(mouser.sent[0].split("|")) == sorted(self.HAMMOND)

    async def test_digikey_get_part(self, setup):
        fake = FakeDigiKey(dk_product("1590A", "Hammond Manufacturing"), dk_product("1590B", "Hammond Manufacturing"))
        setup(digikey=fake)
        for number in ("1590A", "1590B"):
            reply = await server.digikey_get_part(product_number=number)
            assert reply["results"][0]["manufacturer"] == "Hammond Manufacturing" and "not_sent" not in reply
        assert fake.asked == ["1590A", "1590B"]

    async def test_part_lifecycle(self, setup):
        mouser = FakeMouser(mouser_part("1590A", "Hammond Manufacturing"))
        setup(mouser=mouser, digikey=FakeDigiKey())
        rows = (await lifecycle([{"mpn": "1590A", "manufacturer": "Hammond Manufacturing"}, "100V", "10k", "1.5A"]))[
            "results"]
        assert (rows[0]["status"], rows[0]["source"]) == ("active", "mouser") and "not_sent" not in rows[0]
        assert "not_sent" not in rows[1] and [r.get("not_sent") for r in rows[2:]] == ["value", "value"]
        assert sorted(mouser.sent[0].split("|")) == ["100V", "1590A"]


class TestNotSent:
    async def test_mouser_batch_leaves_them_out(self, setup):
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, _, mq, _ = setup(mouser=fake)
        reply = await m.get_part("10k|LM358P|C7950|100nF 50V 0603")
        assert fake.sent == ["LM358P"] and mq.status()["used_today"] == 1
        assert reply["not_found"] == ["10k", "C7950", "100nF 50V 0603"]
        assert reply["not_sent"] == {"10k": "value", "C7950": "lcsc_code", "100nF 50V 0603": "value"}
        assert [r["mfr_part_number"] for r in reply["results"]] == ["LM358P"]
        assert stats.usage.summary()["days"][0]["distributors"]["mouser"]["skipped"] == 3

    async def test_mouser_lone_number_spends_nothing(self, setup):
        fake = FakeMouser()
        m, _, _, mq, _ = setup(mouser=fake, mouser_limit=0)  # not even a spent day stops the answer
        reply = await server.mouser_get_part(part_number="4.7uF")
        assert reply == {"results": [], "total": 0, "not_found": ["4.7uF"], "not_sent": {"4.7uF": "value"},
                         "observed_at": "2026-11-18T12:00:00+00:00"}
        assert fake.sent == [] and mq.status()["used_today"] == 0
        assert server._call_outcome(type("R", (), {"structured_content": reply})()) == "not_found"
        assert server._call_reason("not_found", reply, None) == "not_sent"

    async def test_digikey_lone_number(self, setup):
        fake = FakeDigiKey()
        _, d, _, _, dq = setup(digikey=fake)
        reply = await server.digikey_get_part(product_number="10k 0402")
        assert reply["error"] == "Part not found: 10k 0402"  # what a client reads as a completed miss
        assert reply["not_sent"] == "value" and "component value" in reply["hint"]
        assert fake.asked == [] and dq.status()["used_today"] == 0
        assert server._call_reason("not_found", reply, None) == "not_sent"
        assert (await d.get_part("AB"))["not_sent"] == "length"  # both distributors take 3-40 characters

    async def test_part_lifecycle_rows(self, setup):
        mouser, digikey = FakeMouser(mouser_part("LM358P")), FakeDigiKey()
        setup(mouser=mouser, digikey=digikey)
        reply = await lifecycle(["10k", {"mpn": "C7950"}, "AB", "16Ω", "LM358P", "DNP"])
        rows = reply["results"]
        assert [r.get("not_sent") for r in rows] == ["value", "lcsc_code", "length", "value", None, "placeholder"]
        assert rows[0] == {"input": "10k", "mpn": "10k", "status": "unknown", "not_sent": "value"}
        assert mouser.sent == ["LM358P"] and digikey.asked == []  # "AB" went to DigiKey before
        assert rows[5]["error"].startswith("Invalid part: 'DNP' is a BOM placeholder")
        none = await lifecycle(["10k", "4.7uF"])
        assert server._lifecycle_outcome(none) == "not_found"
        assert server._call_reason("not_found", none, None) == "not_sent"

    async def test_a_kept_reading_still_answers(self, setup):
        _, _, store, _, _ = setup(mouser=FakeMouser())
        store.put_readings([Reading("AB", "Acme", "digikey", "obsolete", "Obsolete", NOW)])
        assert (await lifecycle(["AB"]))["results"][0]["status"] == "obsolete"


def lcsc_catalog(monkeypatch, parts):
    class Catalog:
        def get_by_lcsc_batch(self, codes):
            return {code: parts.get(code) for code in codes}

        def get_sold_out_rows(self, codes):
            return dict.fromkeys(codes)

    monkeypatch.setattr(server, "get_db", lambda: Catalog())


class TestMouserPartial:
    """Decision 2026-11-18: a batch with some parts kept and the rest blocked by a spent limit
    returns the kept parts with not_checked and retry_after, not the limit error."""

    async def test_kept_parts_answer_with_not_checked(self, setup):
        fake = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P"))
        m, _, _, mq, _ = setup(mouser=fake)
        await m.get_part("LM358P")
        mq._count = mq._limit
        reply = await server.mouser_get_part(part_number="LM358P|NE555P|TL431")
        assert "error" not in reply
        assert [r["mfr_part_number"] for r in reply["results"]] == ["LM358P"]
        assert reply["not_checked"] == ["NE555P", "TL431"] and reply["retry_after"] == MIDNIGHT - NOW
        assert "not_found" not in reply and fake.sent == ["LM358P"]

    async def test_nothing_kept_is_the_limit_error_as_before(self, setup):
        m, _, _, _, _ = setup(mouser=FakeMouser(), mouser_limit=0)
        reply = await m.get_part("NE555P|TL431")
        assert set(reply) == {"error"} and "daily quota exceeded" in reply["error"]


ODD_NUMBER = {"Errors": [{"Code": "InvalidCharacters", "Message": "The part number contains invalid characters."}]}


class TestOneNumberMouserRejects:
    async def test_the_others_still_answer(self, setup):
        fake = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P"),
                          responses=[httpx.Response(200, json=ODD_NUMBER), httpx.Response(200, json={"Errors": [], "SearchResults": {"Parts": [mouser_part("LM358P")]}}),
                                     httpx.Response(200, json=ODD_NUMBER), httpx.Response(200, json={"Errors": [], "SearchResults": {"Parts": [mouser_part("NE555P")]}})])
        m, _, store, _, _ = setup(mouser=fake)
        reply = await m.get_part("LM358P|BAD*NUM|NE555P")
        assert fake.sent == ["LM358P|BAD*NUM|NE555P", "LM358P", "BAD*NUM", "NE555P"]
        assert [r["mfr_part_number"] for r in reply["results"]] == ["LM358P", "NE555P"]
        assert reply["lookup_failed"] == ["BAD*NUM"] and "not_found" not in reply
        assert store.get_answer("mouser", "NE555P") is not None  # kept as a one-number answer

    async def test_part_lifecycle_fails_only_that_number(self, setup):
        fake = FakeMouser(responses=[httpx.Response(200, json=ODD_NUMBER),
                                     httpx.Response(200, json={"Errors": [], "SearchResults": {"Parts": [mouser_part("LM358P")]}}),
                                     httpx.Response(200, json=ODD_NUMBER)])
        setup(mouser=fake)
        good, bad = (await lifecycle(["LM358P", "BAD*NUM"]))["results"]
        assert good["status"] == "active" and bad["lookup_failed"] is True

    async def test_a_second_failure_stops_the_singles(self, setup):
        fake = FakeMouser(responses=[httpx.Response(200, json=ODD_NUMBER)] * 3)
        m, _, _, mq, _ = setup(mouser=fake)
        with pytest.raises(Exception, match="invalid characters"):
            await m.get_part("PARTA1|PARTA2|PARTA3|PARTA4")
        assert len(fake.sent) == 3 and mq.status()["used_today"] == 3  # Mouser's fault: no more

    async def test_a_limit_stopping_the_singles(self, setup):
        fake = FakeMouser(responses=[httpx.Response(200, json=ODD_NUMBER)])
        m, _, _, _, _ = setup(mouser=fake, mouser_per_minute=1)
        reply = await m.get_part("PARTA1|PARTA2")
        assert set(reply) == {"error"} and "a minute" in reply["error"]  # nothing kept: the limit error
        fake = FakeMouser(mouser_part("PARTB1"), responses=[httpx.Response(200, json=ODD_NUMBER)])
        m, _, _, _, _ = setup(mouser=fake, mouser_per_minute=2)
        reply = await m.get_part("PARTB1|PARTB2")
        assert [r["mfr_part_number"] for r in reply["results"]] == ["PARTB1"]
        assert reply["not_checked"] == ["PARTB2"] and reply["retry_after"] == 60

    # Astra review round 5 (2026-11-18): with one number left to ask, Mouser rejecting it raised
    # and threw away the kept answers of the rest of the batch

    async def test_a_kept_part_beside_a_rejected_one(self, setup):
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, _, _, _ = setup(mouser=fake)
        await m.get_part("LM358P")
        fake.responses = [httpx.Response(200, json=ODD_NUMBER)]
        reply = await server.mouser_get_part(part_number="LM358P|BAD*NUM")
        assert fake.sent == ["LM358P", "BAD*NUM"]
        assert [r["mfr_part_number"] for r in reply["results"]] == ["LM358P"]
        assert reply["lookup_failed"] == ["BAD*NUM"] and "error" not in reply
        fake.responses = [httpx.Response(200, json=ODD_NUMBER)]
        with pytest.raises(Exception, match="invalid characters"):  # alone: Mouser's error, as before
            await m.get_part("BAD*NUM")

    async def test_part_lifecycle_keeps_the_kept_part(self, setup, clock):
        """part_lifecycle's chunk failed whole: the kept LM358P came back lookup_failed too."""
        fake = FakeMouser(mouser_part("LM358P"))
        _, _, store, _, _ = setup(mouser=fake)
        await server.mouser_get_part(part_number="LM358P")
        store._conn.execute("DELETE FROM lifecycle")  # its reading gone: read from the kept answer
        fake.responses = [httpx.Response(200, json=ODD_NUMBER)]
        good, bad = (await lifecycle(["LM358P", "BAD*NUM"]))["results"]
        assert (good["status"], good["source"]) == ("active", "mouser") and "lookup_failed" not in good
        assert bad["lookup_failed"] is True and fake.sent == ["LM358P", "BAD*NUM"]

class TestShielded:
    async def test_mouser_batch_answer_kept_when_the_caller_gives_up(self, setup):
        release = asyncio.Event()

        async def slow(request):
            await release.wait()
            return httpx.Response(200, json={"Errors": [], "SearchResults": {"Parts": [mouser_part("LM358P"), mouser_part("NE555P")]}})

        m, _, store, _, _ = setup(mouser=slow)
        call = asyncio.create_task(m.get_part("LM358P|NE555P"))
        await settle()
        call.cancel()
        with pytest.raises(asyncio.CancelledError):
            await call
        release.set()
        for _ in range(20):
            await asyncio.sleep(0)
        assert store.get_answer("mouser", "NE555P") is not None

    async def test_digikey_answer_kept_when_the_caller_gives_up(self, setup):
        release = asyncio.Event()

        async def slow(request):
            if "oauth2/token" in str(request.url):
                return httpx.Response(200, json={"access_token": "tok", "expires_in": 599})
            await release.wait()
            return httpx.Response(200, json={"Products": [dk_product("LM358P")]})

        _, d, store, _, _ = setup(digikey=slow)
        call = asyncio.create_task(d.get_part("LM358P"))
        await settle()
        call.cancel()
        with pytest.raises(asyncio.CancelledError):
            await call
        release.set()
        for _ in range(20):
            await asyncio.sleep(0)
        assert store.get_answer("digikey", "LM358P") is not None


class TestStatuses:
    @pytest.mark.parametrize("value", ["Yes", "true", "TRUE", True])
    def test_mouser_discontinued_flag(self, value):
        part = {**mouser_part("LM358P"), "IsDiscontinued": value}
        assert (_normalize_part(part)["lifecycle"], _normalize_part(part)["lifecycle_status"]) == ("Discontinued", "unknown")

    @pytest.mark.parametrize("value", ["No", "false", False, None])
    def test_mouser_not_discontinued(self, value):
        assert _normalize_part({**mouser_part("LM358P"), "IsDiscontinued": value})["lifecycle"] is None

    def test_digikey_nrnd_at_end_of_life_is_last_time_buy(self):
        from pcbparts_mcp.lifecycle import digikey_status
        assert digikey_status("Not For New Designs", end_of_life=True) == (
            "last_time_buy", "Not For New Designs (end of life)")

    async def test_mouser_unknown_status_does_not_ask_digikey(self, setup):
        """Decision 2026-11-18: Mouser listing the part, whatever its status, keeps DigiKey out."""
        mouser = FakeMouser(mouser_part("LM358P", lifecycle="Discontinued"))
        digikey = FakeDigiKey(dk_product("LM358P", status="Obsolete"))
        setup(mouser=mouser, digikey=digikey)
        row = (await lifecycle(["LM358P"]))["results"][0]
        assert (row["status"], row["source"]) == ("unknown", "mouser") and digikey.asked == []


class TestJstBothSpellings:
    """A JST part listed under both spellings in one reply: the one spelled as asked is the
    number's reading (review 2026-11-18: the other overwrote it, flipping between calls)."""

    def both(self):
        bare = mouser_part("B2B-PH-K-S", "JST", "306-B2BPHKS", lifecycle="Obsolete")
        full = mouser_part("B2B-PH-K-S(LF)(SN)", "JST", "306-B2BPHKSLFSN")
        return FakeMouser(responses=[httpx.Response(200, json={"Errors": [], "SearchResults": {"Parts": [bare, full]}})])

    async def test_mouser_store_keeps_the_exact_spelling(self, setup):
        m, _, store, _, _ = setup(mouser=self.both())
        await m.get_part("B2B-PH-K-S(LF)(SN)")
        assert [(r.mpn, r.status) for r in store.readings("B2B-PH-K-S(LF)(SN)")] == [("B2B-PH-K-S(LF)(SN)", "active")]

    async def test_part_lifecycle_reads_the_exact_spelling(self, setup):
        setup(mouser=self.both())
        row = (await lifecycle([{"mpn": "B2B-PH-K-S(LF)(SN)", "manufacturer": "JST"}]))["results"][0]
        assert (row["status"], row["raw"]) == ("active", "not stated by Mouser")


class TestCountingNeverBreaksALookup:
    async def test_counters_raising(self, setup, monkeypatch):
        class Broken(stats.UsageStats):
            def _day(self, date=None):
                raise RuntimeError("counter broke")

        monkeypatch.setattr(stats, "usage", Broken())
        m, d, _, _, _ = setup(mouser=FakeMouser(mouser_part("LM358P")), digikey=FakeDigiKey(dk_product("LM358P")))
        assert (await m.get_part("LM358P"))["total"] == 1
        assert (await d.get_part("LM358P"))["total"] == 1
        assert (await m.get_part("10k"))["not_sent"] == {"10k": "value"}

    async def test_a_lone_surrogate_is_counted(self, setup):
        fake = FakeMouser()
        m, _, _, _, _ = setup(mouser=fake)
        await m.get_part("LM358\ud800")
        assert fake.sent == []  # not ASCII: not sent at all
        stats.usage.record_parts_asked("mouser", ["LM358\ud800"])  # the counter itself copes too
        assert stats.usage.summary()["days"][0]["parts_asked"]["mouser"] == {"total": 1, "distinct": 1}


# --- review fixes C, 2026-11-18 ---

class TestMakerIdentity:
    async def test_seiko_is_not_epson(self, setup, monkeypatch):
        """JLCPCB's "Seiko" is Seiko Instruments: it matched "Seiko Epson" as its first word (and so
        Epson's family), so a kept Epson reading answered it and no lookup went out."""
        mouser = FakeMouser(mouser_part("SC-32S-TEST", "Seiko Instruments"))
        _, _, store, _, _ = setup(mouser=mouser)
        store.put_readings([Reading("SC-32S-TEST", "EPSON", "digikey", "obsolete", "Obsolete", NOW)])
        lcsc_catalog(monkeypatch, {"C97605": {"model": "SC-32S-TEST", "manufacturer": "Seiko"}})
        code, given, epson = (await lifecycle(["C97605", {"mpn": "SC-32S-TEST", "manufacturer": "Seiko"},
                                               {"mpn": "SC-32S-TEST", "manufacturer": "Seiko Epson"}]))["results"]
        assert (code["manufacturer"], code["status"], code["source"]) == ("Seiko Instruments", "active", "mouser")
        assert given["status"] == "active" and mouser.sent == ["SC-32S-TEST"]
        assert (epson["manufacturer"], epson["status"]) == ("EPSON", "obsolete")  # Epson's own still answers

    async def test_jlcpcbs_ams_is_ams_osram(self, setup, monkeypatch):
        """JLCPCB's "AMS" parts are ams OSRAM's (the alias "ams" is Advanced Monolithic Systems,
        JLCPCB's AMS1117 maker): Mouser's ams OSRAM listing answers them."""
        mouser = FakeMouser(mouser_part("AS5047P-ATSM", "ams OSRAM"))
        _, _, store, _, _ = setup(mouser=mouser)
        lcsc_catalog(monkeypatch, {"C976416": {"model": "AS5047P-ATSM", "manufacturer": "AMS"}})
        row = (await lifecycle(["C976416"]))["results"][0]
        assert (row["status"], row["source"], row["manufacturer"]) == ("active", "mouser", "ams OSRAM")
        assert [r.maker for r in store.readings("AS5047P-ATSM")] == ["ams OSRAM"]


class TestSpellingsSharingANumber:
    """["10k", "10-k"] share one mpn_key: the first spelling was sent for both, so Mouser got the
    value "10k", and both replies lost not_sent."""

    @pytest.mark.parametrize("parts", [["10k", "10-k"], ["10-k", "10k"]], ids=["value_first", "value_last"])
    async def test_only_a_spelling_that_may_be_sent_goes_out(self, setup, parts):
        mouser, digikey = FakeMouser(), FakeDigiKey()
        setup(mouser=mouser, digikey=digikey)
        rows = {row["input"]: row for row in (await lifecycle(parts))["results"]}
        assert mouser.sent == ["10-k"] and digikey.asked == ["10-k"]
        # "Not listed" is each spelling's own: the other spelling's miss isn't the value's
        assert rows["10k"] == {"input": "10k", "mpn": "10k", "status": "unknown", "not_sent": "value"}
        assert rows["10-k"]["not_found"] is True and "not_sent" not in rows["10-k"]

    async def test_a_listing_found_for_the_other_spelling_answers_both(self, setup):
        mouser = FakeMouser(mouser_part("10-K", "Acme"))
        setup(mouser=mouser)
        rows = (await lifecycle(["10k", "10-K"]))["results"]
        assert [(r["status"], r["source"]) for r in rows] == [("active", "mouser")] * 2
        assert mouser.sent == ["10-K"] and "not_sent" not in rows[0]

    async def test_a_limit_on_the_other_spelling_isnt_the_values(self, setup):
        mouser = FakeMouser()
        setup(mouser=mouser, mouser_limit=0)
        value, other = (await lifecycle(["10k", "10-k"]))["results"]
        assert value == {"input": "10k", "mpn": "10k", "status": "unknown", "not_sent": "value"}
        assert other["retry_after"] > 0 and mouser.sent == []

    async def test_every_spelling_excluded_sends_nothing(self, setup):
        mouser = FakeMouser()
        setup(mouser=mouser)
        rows = (await lifecycle(["10k", "10K"]))["results"]
        assert [r.get("not_sent") for r in rows] == ["value", "value"] and mouser.sent == []
        assert stats.usage.summary()["days"][0]["distributors"]["mouser"]["skipped"] == 1  # one number

    async def test_mouser_lookup_refuses_them_itself(self, setup):
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, _, mq, _ = setup(mouser=fake)
        answers, error = await m.lookup(["10k", "LM358P"])
        assert fake.sent == ["LM358P"] and list(answers) == ["LM358P"] and error is None
        assert await m.lookup(["C7950", "N/A"]) == ({}, None)
        assert len(fake.sent) == 1 and mq.status()["used_today"] == 1
        assert stats.usage.summary()["days"][0]["distributors"]["mouser"]["skipped"] == 3


class TestCodeBesideAnUnusableMpn:
    """An LCSC code supplies the MPN: an MPN beside it that can't be looked up isn't the row's error."""

    async def test_the_catalogs_mpn_is_used(self, setup, monkeypatch):
        lcsc_catalog(monkeypatch, {"C7950": {"model": "LM358P", "manufacturer": "Texas Instruments"}})
        mouser = FakeMouser(mouser_part("LM358P"))
        setup(mouser=mouser)
        parts = [{"lcsc": "C7950", "mpn": mpn} for mpn in ("N/A", "M" * 101, "LM\x00358", "LM358P|NE555P")]
        parts.append({"lcsc": "C7950", "mpn": "LM358P", "manufacturer": "T" * 101})
        rows = (await lifecycle(parts))["results"]
        assert [(r["mpn"], r["status"], r.get("error")) for r in rows] == [("LM358P", "active", None)] * 5
        assert rows[4]["manufacturer"] == "Texas Instruments" and mouser.sent == ["LM358P"]
        assert rows[0]["input"] == {"lcsc": "C7950", "mpn": "N/A"}

    async def test_a_given_mpn_no_distributor_lists_is_set_aside(self, setup, monkeypatch):
        """A given MPN not_sent_reason rejects beside a valid code answered not_sent instead of the
        code's part; a usable given MPN still wins over the catalog's."""
        lcsc_catalog(monkeypatch, {"C7950": {"model": "LM358P", "manufacturer": "Texas Instruments"}})
        mouser = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P"))
        setup(mouser=mouser)
        parts = [{"lcsc": "C7950", "mpn": mpn} for mpn in ("10k", "C7950", "AB", "LM358P中文", "X" * 41)]
        parts += [{"lcsc": "C7950", "mpn": "10k", "manufacturer": "TI"}, {"lcsc": "C7950", "mpn": "NE555P"}]
        rows = (await lifecycle(parts))["results"]
        assert [(r["mpn"], r["status"], r.get("not_sent")) for r in rows] == [("LM358P", "active", None)] * 6 + [
            ("NE555P", "active", None)]
        assert [r["input"] for r in rows] == parts and rows[5]["manufacturer"] == "Texas Instruments"
        assert len(mouser.sent) == 1 and set(mouser.sent[0].split("|")) == {"LM358P", "NE555P"}
        alone, = (await lifecycle([{"lcsc": "X1", "mpn": "10k"}]))["results"]  # no valid code: as before
        assert (alone["mpn"], alone["not_sent"]) == ("10k", "value")

    async def test_without_a_valid_code_they_stay_errors(self, setup):
        setup(mouser=FakeMouser())
        rows = (await lifecycle([{"lcsc": "N/A", "mpn": "DNP"}, {"lcsc": "X1", "mpn": "M" * 101}]))["results"]
        assert rows[0]["error"].startswith("Invalid part: 'DNP' is a BOM placeholder")
        assert rows[1]["error"] == "MPN too long (max 100 characters)"


# --- Astra review round 2, 2026-11-18 ---

class TestNotListedPerSpelling:
    """A distributor's "not listed" holds for the spelling asked; a listing answers every spelling."""

    async def test_a_digikey_miss_is_kept_for_its_own_spelling(self, setup):
        """DigiKey matches the spelling asked (case aside), but its "not listed" was kept by mpn_key:
        a miss for LM358-P answered LM358P not_found for 30 days without asking, though DigiKey lists
        it. Mouser's is kept the same way (whether its search ignores separators isn't known)."""
        mouser, digikey = FakeMouser(), FakeDigiKey(dk_product("LM358P"))
        _, _, store, _, _ = setup(mouser=mouser, digikey=digikey)
        assert (await lifecycle(["LM358-P"]))["results"][0]["not_found"] is True
        assert {(r.source, r.found) for r in store.readings("lm358-p ")} == {("mouser", False), ("digikey", False)}
        assert store.readings("LM358P") == []  # another spelling: not known
        row = (await lifecycle(["LM358P"]))["results"][0]
        assert (row["status"], row["source"]) == ("active", "digikey")
        assert mouser.sent == ["LM358-P", "LM358P"] and digikey.asked == ["LM358-P", "LM358P"]
        # The listing is kept by mpn_key, so it answers every spelling from now on
        assert (await lifecycle(["LM358-P"]))["results"][0]["source"] == "digikey" and len(digikey.asked) == 2

    async def test_two_spellings_in_one_call_are_each_asked(self, setup):
        mouser, digikey = FakeMouser(), FakeDigiKey(dk_product("LM358P"))
        setup(mouser=mouser, digikey=digikey)
        rows = (await lifecycle(["LM358-P", "LM358P", "lm358p"]))["results"]
        assert [(r["status"], r.get("source")) for r in rows] == [("active", "digikey")] * 3
        assert sorted(digikey.asked) == ["LM358-P", "LM358P"]
        assert sorted(mouser.sent[0].split("|")) == ["LM358-P", "LM358P"]


class TestLoneSurrogates:
    async def test_lone_surrogates_are_one_rows_error(self, setup):
        """An escaped lone surrogate in a JSON array string passed the checks; echoed back, the
        reply couldn't be sent as UTF-8."""
        mouser = FakeMouser(mouser_part("LM358P"))
        setup(mouser=mouser)
        async with Client(server.mcp) as client:
            sent = await client.call_tool("part_lifecycle", {"parts": '["LM358\\ud800", {"mpn": "LM358P", '
                                                                      '"manufacturer": "T\\udfffI"}, "LM358P"]'})
        bad, maker, good = sent.structured_content["results"]
        assert bad == {"input": "LM358\\ud800", "status": "unknown", "error": server._UNENCODABLE["error"]}
        assert maker["error"] == server._UNENCODABLE["error"] and maker["input"]["manufacturer"] == "T\\udfffI"
        assert good["status"] == "active" and mouser.sent == ["LM358P"]


class TestUnreadableMouserReply:
    """A 200 without its parts list ({"Errors": [], "SearchResults": null}) was read as an empty
    one: a day's "not found" and a 30-day Mouser "not listed". It's a failed lookup."""

    BODIES = [{"Errors": [], "SearchResults": None}, {"Errors": []}, {"Errors": [], "SearchResults": {"Parts": None}},
              {"Errors": [], "SearchResults": {"NumberOfResult": 0}}, {"Errors": [], "SearchResults": []}]

    @pytest.mark.parametrize("body", BODIES, ids=["null", "none", "parts_null", "no_parts", "list"])
    async def test_mouser_get_part(self, setup, body):
        mouser = FakeMouser(mouser_part("LM358P"), responses=[httpx.Response(200, json=body)])
        _, _, store, _, _ = setup(mouser=mouser)
        reply = await server.mouser_get_part(part_number="LM358P")
        assert reply == {"error": "Mouser part lookup failed: Mouser API returned an unreadable response"}
        assert server._error_kind(reply["error"]) == "failed"
        assert store.get_answer("mouser", "LM358P") is None and store.readings("LM358P") == []
        assert (await server.mouser_get_part(part_number="LM358P"))["total"] == 1  # asked again
        assert len(mouser.sent) == 2

    async def test_a_batch_keeps_nothing(self, setup):
        mouser = FakeMouser(responses=[httpx.Response(200, json=self.BODIES[0])])
        m, _, store, _, _ = setup(mouser=mouser)
        with pytest.raises(MouserError, match="unreadable"):
            await m.get_part("LM358P|NE555P")
        assert store.get_answer("mouser", "batch:LM358P|NE555P") is None
        assert store.readings("LM358P") == store.readings("NE555P") == []

    async def test_part_lifecycle(self, setup):
        mouser = FakeMouser(responses=[httpx.Response(200, json=self.BODIES[0])])
        digikey = FakeDigiKey(dk_product("TIX0001"))
        _, _, store, _, _ = setup(mouser=mouser, digikey=digikey)
        row = (await lifecycle([{"mpn": "TIX0001", "manufacturer": "TI"}]))["results"][0]
        assert row == {"input": {"mpn": "TIX0001", "manufacturer": "TI"}, "mpn": "TIX0001", "status": "unknown",
                       "manufacturer": "TI", "lookup_failed": True}
        assert digikey.asked == [] and store.readings("TIX0001") == []  # no "not listed", DigiKey not asked


class TestLifecycleByMouserPartNumber:
    """part_lifecycle(["595-LM358P"]): Mouser answered LM358P (its Mouser PN), but only the MPN was
    compared, so the row was not_found after a DigiKey request and a 30-day DigiKey "not listed"."""

    async def test_the_mouser_pn_is_the_part(self, setup):
        mouser, digikey = FakeMouser(mouser_part("LM358P")), FakeDigiKey(dk_product("LM358P"))
        _, _, store, _, _ = setup(mouser=mouser, digikey=digikey)
        row = (await lifecycle(["595-LM358P"]))["results"][0]
        assert row == {"input": "595-LM358P", "mpn": "595-LM358P", "manufacturer": "Texas Instruments",
                       "status": "active", "raw": "not stated by Mouser", "source": "mouser",
                       "observed_at": "2026-11-18T12:00:00+00:00"}
        assert mouser.sent == ["595-LM358P"] and digikey.asked == []
        assert [r for r in store.readings("595-LM358P") if not r.found] == []
        again = (await lifecycle(["595-lm358p"]))["results"][0]  # the kept answer, no request
        assert again["source"] == "mouser" and len(mouser.sent) == 1 and digikey.asked == []

    async def test_another_parts_mouser_pn_is_not(self, setup):
        """A loose match whose Mouser PN only starts with the number is still not the part."""
        mouser, digikey = FakeMouser(mouser_part("LM358PE4", mouser_pn="595-LM358PE4")), FakeDigiKey()
        setup(mouser=mouser, digikey=digikey)
        row = (await lifecycle(["595-LM358P"]))["results"][0]
        assert row["not_found"] is True and digikey.asked == ["595-LM358P"]
