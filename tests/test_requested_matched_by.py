"""0.10.0: mouser_get_part and digikey_get_part results say which number they answer (requested)
and how they match it (matched_by), so a client needn't re-implement our MPN rules: DigiKey lists
B2B-PH-K-S(LF)(SN) as B2B-PH-K-S, which a punctuation-stripping comparison rejects.
No network: httpx.MockTransport fakes, a fake clock, a fake pacer."""

import json
import re

import httpx
import pytest
from fastmcp import Client

import pcbparts_mcp.server as server
from pcbparts_mcp.cache import Pacer
from pcbparts_mcp.digikey import DigiKeyClient
from pcbparts_mcp.distributor_store import DistributorStore
from pcbparts_mcp.mouser import MouserClient
from pcbparts_mcp.search.mpn import MATCHED_BY, distributor_match

NOW = 1_795_000_000.0
NEW_FIELDS = ("requested", "matched_by")


class Clock:
    def __init__(self):
        self.now = NOW

    def __call__(self):
        return self.now


async def no_wait(seconds):
    return None


# --- the vocabulary ---

CASES = [
    ("LM358P", "lm358p", "TI", ["595-LM358P"], "exact"),
    (" LM358P ", "LM358P", "TI", [], "exact"),
    ("LM358-P", "LM358P", "TI", [], "separators"),
    ("AMS1117 3.3", "AMS1117-3.3", "AMS", [], "separators"),
    ("B2B-PH-K-S(LF)(SN)", "B2B-PH-K-S", "JST Sales America Inc.", ["455-1704-ND"], "packing"),
    ("B2B-PH-K-S", "B2B-PH-K-S(LF)(SN)", "JST", [], "packing"),  # not prefix: the same part
    ("595-LM358P", "LM358P", "TI", ["595-LM358P"], "mouser_pn"),
    ("595LM358P", "LM358P", "TI", ["595-LM358P"], "mouser_pn"),
    ("LM358P", "LM358PE4", "TI", ["595-LM358PE4"], "prefix"),
    ("595-LM358", "LM358P", "TI", ["595-LM358P"], "prefix"),
    ("NRF24L01+", "NRF24L01", "Nordic", [], "prefix"),  # the plus names another radio
    ("LM358P", "XYZ-1", "Acme", ["123-XYZ1"], "other"),
    # Only JST's finish codes are set aside: another maker's copy or variant stays unproven
    ("B2B-PH-K-S(LF)(SN)", "B2B-PH-K-S", "SHOU HAN", [], "other"),
    ("LM258DR(UMW)", "LM258DR", "Texas Instruments", [], "other"),
    ("DF13-2P-1.25DSA(50)", "DF13-2P-1.25DSA", "Hirose", [], "other"),
]


@pytest.mark.parametrize("asked, mpn, maker, own, kind", CASES, ids=[f"{c[4]}{i}" for i, c in enumerate(CASES)])
def test_vocabulary(asked, mpn, maker, own, kind):
    assert distributor_match(asked, mpn, maker, own, "mouser_pn") == kind
    assert kind in MATCHED_BY


def test_distributor_number_kinds():
    assert distributor_match("296-1395-5-nd", "LM358P", "TI", ["296-1395-5-ND"], "digikey_pn") == "digikey_pn"
    # A blank MPN or number never matches by accident
    assert distributor_match("---", "", "TI", [""], "digikey_pn") == "other"


# --- Mouser ---

def mouser_part(mpn, maker="Texas Instruments", mouser_pn=None):
    return {"MouserPartNumber": mouser_pn or f"595-{mpn}", "ManufacturerPartNumber": mpn, "Manufacturer": maker,
            "Description": "", "Category": "", "AvailabilityInStock": "100", "Min": "1",
            "PriceBreaks": [{"Quantity": 1, "Price": "$0.50", "Currency": "USD"}], "ProductAttributes": []}


class FakeMouser:
    """Mouser's loose search: every part whose MPN or Mouser PN starts with a number asked, unless
    a raw reply is queued."""

    def __init__(self, *parts, replies=()):
        self.parts = list(parts)
        self.replies = list(replies)
        self.sent = []

    def __call__(self, request):
        numbers = json.loads(request.content)["SearchByPartRequest"]["mouserPartNumber"]
        self.sent.append(numbers)
        hits = self.replies.pop(0) if self.replies else [
            p for p in self.parts if any(
                re.sub(r"[^A-Z0-9]", "", p[field].upper()).startswith(re.sub(r"[^A-Z0-9]", "", n.upper()))
                for n in numbers.split("|") for field in ("ManufacturerPartNumber", "MouserPartNumber"))]
        return httpx.Response(200, json={"Errors": [], "SearchResults": {"Parts": hits}})


@pytest.fixture
async def mouser():
    made = []

    def create(fake):
        store = DistributorStore(clock=Clock())
        client = MouserClient(api_key="k", store=store, pool_window=0, sleep=no_wait)
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(fake))
        made.append((client, store))
        return client

    yield create
    for client, store in made:
        await client.close()
        store.close()


def answered(reply):
    return [(r["mfr_part_number"], r["requested"], r["matched_by"]) for r in reply["results"]]


async def test_mouser_lone_number(mouser):
    fake = FakeMouser(mouser_part("LM358P"), mouser_part("LM358PE4"), mouser_part("NE555P"))
    m = mouser(fake)
    assert answered(await m.get_part(" lm358p ")) == [
        ("LM358P", "lm358p", "exact"), ("LM358PE4", "lm358p", "prefix")]
    # Kept once, answered for each spelling: no request, and the store keeps neither field
    assert answered(await m.get_part("LM358P")) == [("LM358P", "LM358P", "exact"), ("LM358PE4", "LM358P", "prefix")]
    assert fake.sent == ["lm358p"]
    kept = m._store.get_answer("mouser", "LM358P")[0]["results"]
    assert kept and all(field not in r for r in kept for field in NEW_FIELDS)


async def test_mouser_pn_and_odd_result(mouser):
    m = mouser(FakeMouser(replies=[[mouser_part("LM358P")], [mouser_part("XYZ-1", mouser_pn="123-XYZ1")]]))
    assert answered(await m.get_part("595-LM358P")) == [("LM358P", "595-LM358P", "mouser_pn")]
    # Whatever Mouser returns for a lone number is that number's, though our rules can't say how
    assert answered(await m.get_part("LM358P")) == [("XYZ-1", "LM358P", "other")]


async def test_mouser_batch(mouser):
    fake = FakeMouser(mouser_part("LM358P"), mouser_part("NE555P"), mouser_part("B2B-PH-K-S(LF)(SN)", "JST"))
    m = mouser(fake)
    reply = await m.get_part("NE555P|595-LM358P|B2B-PH-K-S|NOPE1")
    assert answered(reply) == [("NE555P", "NE555P", "exact"), ("LM358P", "595-LM358P", "mouser_pn"),
                               ("B2B-PH-K-S(LF)(SN)", "B2B-PH-K-S", "packing")]
    assert reply["not_found"] == ["NOPE1"]
    # The same parts in another batch, from the store, answer that batch's numbers
    again = await m.get_part("b2b-ph-k-s|ne555p")
    assert answered(again) == [("B2B-PH-K-S(LF)(SN)", "b2b-ph-k-s", "packing"), ("NE555P", "ne555p", "exact")]
    assert len(fake.sent) == 1


async def test_mouser_unclear_results_are_null(mouser):
    """LM358PE4 is a loose match for both LM358 and LM358P, and XYZ-1 for neither: requested null."""
    m = mouser(FakeMouser(replies=[[mouser_part("LM358P"), mouser_part("LM358PE4"),
                                    mouser_part("XYZ-1", mouser_pn="123-XYZ1")]]))
    reply = await m.get_part("LM358|LM358P")
    assert answered(reply) == [("LM358P", "LM358P", "exact"), ("LM358PE4", None, None), ("XYZ-1", None, None)]


async def test_mouser_tool_reply(mouser, monkeypatch):
    m = mouser(FakeMouser(mouser_part("LM358P"), mouser_part("LM358PE4")))
    monkeypatch.setattr(server, "_mouser_client", m)
    async with Client(server.mcp) as client:
        result = await client.call_tool("mouser_get_part", {"part_number": "LM358|LM358P"})
    parts = result.structured_content["results"]
    assert [(p["mfr_part_number"], p["requested"], p["matched_by"]) for p in parts] == [
        ("LM358P", "LM358P", "exact"), ("LM358PE4", None, None)]
    # The fields Backplane parses keep their names and meaning
    assert {"mfr_part_number", "lifecycle", "price_breaks"} <= set(parts[0])


# --- DigiKey ---

def dk_product(mpn, maker="Texas Instruments", numbers=("296-1395-5-ND",), stock=100):
    return {"ManufacturerProductNumber": mpn, "Manufacturer": {"Name": maker}, "ProductStatus": {"Status": "Active"},
            "QuantityAvailable": stock, "Parameters": [], "ProductVariations": [
                {"DigiKeyProductNumber": n, "MinimumOrderQuantity": 1 + i * 999, "PackageType": {"Name": "Bulk"},
                 "StandardPricing": [{"BreakQuantity": 1, "UnitPrice": 0.5}]} for i, n in enumerate(numbers)]}


class FakeDigiKey:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.asked = []

    def __call__(self, request):
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 599})
        self.asked.append(json.loads(request.content)["Keywords"])
        return httpx.Response(200, json=self.replies.pop(0))


@pytest.fixture
async def digikey():
    made = []

    def create(fake):
        store = DistributorStore(clock=Clock())
        client = DigiKeyClient(client_id="id", client_secret="secret", store=store)
        client._http = httpx.AsyncClient(transport=httpx.MockTransport(fake))
        client._pacer = Pacer(1e6, clock=Clock(), sleep=no_wait)
        made.append((client, store))
        return client

    yield create
    for client, store in made:
        await client.close()
        store.close()


async def test_digikey_jst_finish(digikey, monkeypatch):
    """research-backplane-code-review problem 5: the asked number and how it matched, so the
    answer is usable without comparing B2B-PH-K-S(LF)(SN) to B2B-PH-K-S."""
    fake = FakeDigiKey({"ExactMatches": [], "Products": [
        dk_product("B2B-PH-K-S", "JST Sales America Inc.", ("455-1704-ND",), 315042)]})
    monkeypatch.setattr(server, "_digikey_client", digikey(fake))
    reply = await server.digikey_get_part(product_number="B2B-PH-K-S(LF)(SN)")
    assert answered(reply) == [("B2B-PH-K-S", "B2B-PH-K-S(LF)(SN)", "packing")]
    again = await server.digikey_get_part(product_number=" b2b-ph-k-s(lf)(sn) ")  # kept: no request
    assert answered(again) == [("B2B-PH-K-S", "b2b-ph-k-s(lf)(sn)", "packing")]
    assert len(fake.asked) == 1


async def test_digikey_pn_and_makers(digikey):
    fake = FakeDigiKey(
        {"ExactMatches": [dk_product("AO3400A", "Alpha & Omega", ("785-1000-1-ND", "785-1000-2-ND"))]},
        {"ExactMatches": [dk_product("AO3400A", "Alpha & Omega", stock=9), dk_product("Ao3400a", "UMW", stock=1)],
         "Products": [dk_product("AO3400A-EV", "EVVO")]},
        {"ExactMatches": [dk_product("LM358PWR", numbers=("296-LM358-ND",))]},
    )
    d = digikey(fake)
    reply = await d.get_part("785-1000-2-ND")
    assert answered(reply) == [("AO3400A", "785-1000-2-ND", "digikey_pn")]
    assert reply["results"][0]["part_number"] == "785-1000-2-ND"
    assert answered(await d.get_part("ao3400a")) == [("AO3400A", "ao3400a", "exact"), ("Ao3400a", "ao3400a", "exact")]
    # DigiKey's own exact match, neither the number's MPN nor its DigiKey PN: other
    assert answered(await d.get_part("LM358-ALT")) == [("LM358PWR", "LM358-ALT", "other")]
    kept = d._store.get_answer("digikey", "AO3400A")[0]["results"]
    assert kept and all(field not in r for r in kept for field in NEW_FIELDS)


async def test_digikey_miss_unchanged(digikey):
    d = digikey(FakeDigiKey({"ExactMatches": [], "Products": []}))
    assert await d.get_part("NOPE-ND") == {"error": "Part not found: NOPE-ND"}


def test_descriptions_say_so():
    from fastmcp.utilities.docstring_parsing import parse_docstring
    for name in ("mouser_get_part", "digikey_get_part"):
        sent = parse_docstring(getattr(server, name)).description
        assert "requested" in sent and "matched_by" in sent, name


# --- Mouser and JST's (LF)/(SN) endings: the same rule as DigiKey's ---

def jst(mpn="B2B-PH-K-S", lifecycle=None):
    part = mouser_part(mpn, "JST", mouser_pn="306-B2BPHKS")
    if lifecycle:
        part["LifecycleStatus"] = lifecycle
    return part


async def test_jst_alone(mouser):
    fake = FakeMouser(replies=[[jst(lifecycle="Not Recommended for New Designs")]])
    m = mouser(fake)
    reply = await m.get_part("B2B-PH-K-S(LF)(SN)")
    assert answered(reply) == [("B2B-PH-K-S", "B2B-PH-K-S(LF)(SN)", "packing")]
    assert "not_found" not in reply
    assert m._store.get_answer("mouser", "B2B-PH-K-S(LF)(SN)") is not None  # kept per part
    # Its lifecycle is filed under the number asked too, and it isn't "not listed"
    assert [(r.mpn, r.status, r.found) for r in m._store.readings("B2B-PH-K-S(LF)(SN)")] == [
        ("B2B-PH-K-S", "nrnd", True)]
    assert answered(await m.get_part("b2b-ph-k-s(lf)(sn)")) == [("B2B-PH-K-S", "b2b-ph-k-s(lf)(sn)", "packing")]
    assert len(fake.sent) == 1


async def test_jst_in_a_batch(mouser):
    fake = FakeMouser(replies=[[jst(), mouser_part("NE555P")]])
    m = mouser(fake)
    reply = await m.get_part("NE555P|B2B-PH-K-S(LF)(SN)")
    assert answered(reply) == [("NE555P", "NE555P", "exact"), ("B2B-PH-K-S", "B2B-PH-K-S(LF)(SN)", "packing")]
    assert "not_found" not in reply
    # Both clean, so both kept per part (no batch entry): each answers alone, with no request
    assert m._store.get_answer("mouser", "B2B-PH-K-S(LF)(SN)") is not None
    assert m._store.get_answer("mouser", "batch:NE555P|B2B-PH-K-S(LF)(SN)") is None
    assert answered(await m.get_part("B2B-PH-K-S(LF)(SN)")) == [("B2B-PH-K-S", "B2B-PH-K-S(LF)(SN)", "packing")]
    assert len(fake.sent) == 1


async def test_jst_spelled_as_listed_wins(mouser):
    m = mouser(FakeMouser(replies=[[jst()]]))
    reply = await m.get_part("B2B-PH-K-S(LF)(SN)|B2B-PH-K-S")
    assert answered(reply) == [("B2B-PH-K-S", "B2B-PH-K-S", "exact")]
    assert "not_found" not in reply  # both numbers found it


@pytest.mark.parametrize("asked, listed, maker", [
    ("LM258DR(UMW)", "LM258DR", "Texas Instruments"),
    ("DF13-2P-1.25DSA(50)", "DF13-2P-1.25DSA", "Hirose Electric"),
    ("B2B-PH-K-S(LF)(SN)", "B2B-PH-K-S", "SHOU HAN"),
    ("B2B-PH-K-S(HF)", "B2B-PH-K-S", "JST"),
], ids=["umw", "hirose", "notjst", "hf"])
async def test_other_endings_still_miss(mouser, asked, listed, maker):
    other = mouser_part(listed, maker, mouser_pn="999-X1")
    m = mouser(FakeMouser(replies=[[other]]))
    alone = await m.get_part(asked)
    assert alone["not_found"] == [asked] and answered(alone) == [(listed, asked, "other")]
    assert [(r.source, r.found) for r in m._store.readings(asked)] == [("mouser", False)]  # not listed
    batch = await mouser(FakeMouser(replies=[[other, mouser_part("NE555P")]])).get_part(f"NE555P|{asked}")
    assert batch["not_found"] == [asked]
    assert answered(batch) == [("NE555P", "NE555P", "exact"), (listed, None, None)]


@pytest.fixture
async def lifecycle_server(monkeypatch):
    made = []

    def create(fake):
        store = DistributorStore(clock=Clock())
        m = MouserClient(api_key="k", store=store, pool_window=0, sleep=no_wait)
        m._client = httpx.AsyncClient(transport=httpx.MockTransport(fake))
        monkeypatch.setattr(server, "_mouser_client", m)
        monkeypatch.setattr(server, "_digikey_client", None)
        monkeypatch.setattr(server, "_distributor_store", store)
        made.append((m, store))
        return m

    yield create
    for m, store in made:
        await m.close()
        store.close()


def reading(reply):
    return [(r["input"], r["status"], r["raw"], r.get("manufacturer"), r.get("source")) for r in reply["results"]]


async def test_jst_part_lifecycle(lifecycle_server):
    fake = FakeMouser(replies=[[jst(lifecycle="Not Recommended for New Designs")]])
    lifecycle_server(fake)
    expected = [("B2B-PH-K-S(LF)(SN)", "nrnd", "Not Recommended for New Designs", "JST", "mouser")]
    assert reading(await server.part_lifecycle(parts=["B2B-PH-K-S(LF)(SN)"])) == expected
    assert reading(await server.part_lifecycle(parts=["B2B-PH-K-S(LF)(SN)"])) == expected  # from the store
    assert len(fake.sent) == 1


async def test_jst_lifecycle_after_get_part(lifecycle_server):
    fake = FakeMouser(replies=[[jst()]])
    m = lifecycle_server(fake)
    await m.get_part("B2B-PH-K-S(LF)(SN)|NE555P")
    reply = await server.part_lifecycle(parts=[{"mpn": "B2B-PH-K-S(LF)(SN)", "manufacturer": "JST"}])
    assert reading(reply) == [({"mpn": "B2B-PH-K-S(LF)(SN)", "manufacturer": "JST"}, "active",
                               "not stated by Mouser", "JST", "mouser")]
    assert len(fake.sent) == 1


# --- review fixes, 2026-11-18 ---

@pytest.mark.parametrize("numbers", ["595-LM358P|LM358P", "LM358P|LM358-P"], ids=["mouser_pn", "separators"])
async def test_one_part_asked_twice_goes_to_the_first(mouser, numbers):
    """Both numbers are the part itself: it answers the first, so the caller gets a usable
    requested (it was null, and neither number was in not_found)."""
    m = mouser(FakeMouser(replies=[[mouser_part("LM358P")]]))
    reply = await m.get_part(numbers)
    first = numbers.split("|")[0]
    assert [(mpn, requested) for mpn, requested, _ in answered(reply)] == [("LM358P", first)]
    assert "not_found" not in reply


async def test_a_shared_requests_odd_result_answers_no_one(monkeypatch):
    """Two callers' one-part lookups share a request; a result matching neither number goes to
    both (unmatched) callers, each with requested null, not their own number."""
    import asyncio

    gate = asyncio.Event()

    async def wait(seconds):
        await gate.wait()

    store = DistributorStore(clock=Clock())
    m = MouserClient(api_key="k", store=store, pool_window=0.1, sleep=wait)
    m._client = httpx.AsyncClient(transport=httpx.MockTransport(FakeMouser(replies=[[
        mouser_part("LM358P"), mouser_part("XYZ-1", mouser_pn="123-XYZ1")]])))
    try:
        tasks = [asyncio.create_task(m.get_part(n)) for n in ("LM358P", "OLDNAME1")]
        for _ in range(5):
            await asyncio.sleep(0)
        gate.set()
        found, other = await asyncio.gather(*tasks)
        assert answered(found) == [("LM358P", "LM358P", "exact")]
        assert answered(other) == [("XYZ-1", None, None)] and other["not_found"] == ["OLDNAME1"]
    finally:
        await m.close()
        store.close()


def test_packing_wording_names_jst_only():
    from fastmcp.utilities.docstring_parsing import parse_docstring
    for name in ("mouser_get_part", "digikey_get_part"):
        sent = " ".join(parse_docstring(getattr(server, name)).description.split())
        assert "packing (JST's (LF)/(SN) endings set aside)" in sent, name
