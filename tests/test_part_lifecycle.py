"""0.10.0: Mouser answers kept per part (3 days), concurrent one-part Mouser lookups sharing a
request, every Mouser/DigiKey answer feeding the 90-day lifecycle store, and part_lifecycle.
No network: httpx.MockTransport fakes, fake clocks, a gated sleep for the pool window."""

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
from pcbparts_mcp.mouser import MouserClient, MouserError

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


class Gate:
    """The pool window's sleep: waits until the test opens it."""

    def __init__(self):
        self.opened = asyncio.Event()
        self.waits: list[float] = []

    async def __call__(self, seconds: float) -> None:
        self.waits.append(seconds)
        await self.opened.wait()


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
async def setup(clock, monkeypatch):
    """Build the server's clients on one store, as lifespan does. Returns a factory."""
    made = []

    def create(mouser=None, digikey=None, mouser_limit=1000, digikey_limit=1000, gate=None, store=None):
        store = store or DistributorStore(clock=clock)
        mq = DailyQuota("Mouser", mouser_limit, clock=clock, own_key="Mouser API key")
        dq = QuotaPool([DailyQuota("DigiKey", digikey_limit, clock=clock, own_key="DigiKey API credentials")])
        m = d = None
        if mouser is not None:
            m = MouserClient(api_key="k", quota=mq, store=store, pool_window=0.1 if gate else 0,
                             **({"sleep": gate} if gate else {}))
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
    """Let started lookups reach the pool and its timer start."""
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

    async def test_limit_refusals_are_not_kept(self, setup):
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, store, mq, _ = setup(mouser=fake, mouser_limit=0)
        assert "daily quota exceeded" in (await m.get_part("LM358P"))["error"]
        assert store.get_answer("mouser", "LM358P") is None and fake.sent == []
        assert m.retry_after() == MIDNIGHT - NOW


# --- concurrent one-part lookups share a request ---

class TestPool:
    async def test_concurrent_lookups_share_one_request(self, setup):
        gate = Gate()
        fake = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P"))
        m, _, store, mq, _ = setup(mouser=fake, gate=gate)
        tasks = [asyncio.create_task(m.get_part(n, caller="198.51.100.1")) for n in ("LM358P", "NE555P", "lm358p")]
        await settle()
        assert gate.waits == [0.1] and fake.sent == []
        gate.opened.set()
        a, b, c = await asyncio.gather(*tasks)
        assert fake.sent == ["LM358P|NE555P"] and mq.status()["used_today"] == 1
        assert [r["mfr_part_number"] for r in a["results"]] == ["LM358P"]
        assert a == {**c, "results": [{**r, "requested": "LM358P"} for r in c["results"]]}  # c asked "lm358p"
        assert [r["mfr_part_number"] for r in b["results"]] == ["NE555P"]
        assert store.get_answer("mouser", "NE555P") is not None  # clean: kept per part
        assert stats.usage.summary()["days"][0]["distributors"]["mouser"]["sent"] == 1

    async def test_ten_go_at_once(self, setup):
        gate = Gate()  # never opened
        fake = FakeMouser(*(mouser_part(f"PART{i:02}X") for i in range(11)))
        m, _, _, _, _ = setup(mouser=fake, gate=gate)
        tasks = [asyncio.create_task(m.get_part(f"PART{i:02}X")) for i in range(11)]
        done = await asyncio.gather(*tasks[:10])
        assert fake.sent == ["|".join(f"PART{i:02}X" for i in range(10))]
        assert [d["results"][0]["mfr_part_number"] for d in done] == [f"PART{i:02}X" for i in range(10)]
        assert not tasks[10].done()  # the 11th waits in a new batch
        gate.opened.set()
        assert (await tasks[10])["total"] == 1 and len(fake.sent) == 2

    async def test_a_refusal_reaches_every_waiter(self, setup):
        gate = Gate()
        m, _, _, _, _ = setup(mouser=FakeMouser(), gate=gate, mouser_limit=0)
        tasks = [asyncio.create_task(m.get_part(n)) for n in ("LM358P", "NE555P")]
        await settle()
        gate.opened.set()
        a, b = await asyncio.gather(*tasks)
        assert a == b and "daily quota exceeded" in a["error"]

    async def test_a_failure_raises_in_every_waiter(self, setup):
        gate = Gate()
        m, _, _, _, _ = setup(mouser=FakeMouser(responses=[httpx.Response(500)]), gate=gate)
        tasks = [asyncio.create_task(m.get_part(n)) for n in ("LM358P", "NE555P")]
        await settle()
        gate.opened.set()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        assert all(isinstance(r, MouserError) and "HTTP 500" in str(r) for r in results)

    async def test_one_caller_giving_up_leaves_the_others(self, setup):
        gate = Gate()
        fake = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P"))
        m, _, _, _, _ = setup(mouser=fake, gate=gate)
        gone = asyncio.create_task(m.get_part("LM358P"))
        stays = asyncio.create_task(m.get_part("NE555P"))
        await settle()
        gone.cancel()
        gate.opened.set()
        assert (await stays)["results"][0]["mfr_part_number"] == "NE555P"
        assert gone.cancelled() and fake.sent == ["LM358P|NE555P"]

    async def test_close_before_the_timer_starts(self, setup):
        gate = Gate()
        m, _, _, _, _ = setup(mouser=FakeMouser(mouser_part("LM358P")), gate=gate)
        waiting = asyncio.create_task(m.get_part("LM358P"))
        await asyncio.sleep(0)  # the lookup waits; the window's task hasn't started
        await m.close()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(waiting, 1)

    async def test_close_releases_a_waiting_batch(self, setup):
        gate = Gate()  # never opened
        fake = FakeMouser(mouser_part("LM358P"))
        m, _, _, _, _ = setup(mouser=fake, gate=gate)
        waiting = asyncio.create_task(m.get_part("LM358P"))
        await settle()
        await m.close()
        with pytest.raises(asyncio.CancelledError):
            await waiting
        assert fake.sent == []

    async def test_unmatched_result_goes_only_to_unmatched_lookups(self, setup):
        gate = Gate()
        odd = mouser_part("XYZ-1", mouser_pn="123-XYZ1")
        fake = FakeMouser(responses=[httpx.Response(200, json={"Errors": [], "SearchResults": {
            "Parts": [mouser_part("LM358P"), odd]}})])
        m, _, store, _, _ = setup(mouser=fake, gate=gate)
        tasks = [asyncio.create_task(m.get_part(n)) for n in ("LM358P", "OLDNAME1")]
        await settle()
        gate.opened.set()
        found, other = await asyncio.gather(*tasks)
        assert [r["mfr_part_number"] for r in found["results"]] == ["LM358P"]
        assert [r["mfr_part_number"] for r in other["results"]] == ["XYZ-1"] and other["not_found"] == ["OLDNAME1"]
        assert store.get_answer("mouser", "LM358P") is None  # unclear request: nothing kept per part


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

    async def test_mouser_failure_goes_to_digikey(self, setup):
        mouser = FakeMouser(responses=[httpx.Response(503)])
        setup(mouser=mouser, digikey=FakeDigiKey(dk_product("LM358P", status="Obsolete")))
        assert (await lifecycle(["LM358P"]))["results"][0]["status"] == "obsolete"

    async def test_both_fail(self, setup):
        setup(mouser=FakeMouser(responses=[httpx.Response(503)]), digikey=FakeDigiKey(responses=[httpx.Response(500)]))
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

        monkeypatch.setattr(server, "get_db", lambda: Catalog())
        setup(mouser=FakeMouser(mouser_part("LM358P")))
        reply = await lifecycle(["c7950", {"lcsc": "C7950"}, "C99999999"])
        first, second, missing = reply["results"]
        assert (first["input"], first["lcsc"], first["mpn"], first["status"]) == ("c7950", "C7950", "LM358P", "active")
        assert second["mpn"] == "LM358P"
        assert missing["error"] == "Part C99999999 not found" and missing["status"] == "unknown"

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

    async def test_counted_by_the_parts_own_errors_when_none_was_looked_up(self, setup, monkeypatch):
        class Down:
            def get_by_lcsc_batch(self, codes):
                raise OSError("database file is gone")

        class Empty:
            def get_by_lcsc_batch(self, codes):
                return {}

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
