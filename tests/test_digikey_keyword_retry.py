"""One keyword search per uncached DigiKey lookup, using only fake transports."""

import json
import time

import httpx
import pytest

from pcbparts_mcp import stats
from pcbparts_mcp.cache import DailyQuota
from pcbparts_mcp.config import DIGIKEY_CACHE_TTL, DIGIKEY_NOT_FOUND_TTL
from pcbparts_mcp.digikey import DigiKeyClient, DigiKeyError


def product(mpn="209", manufacturer="Keystone Electronics", number="36-209-ND", stock=56856):
    return {
        "ManufacturerProductNumber": mpn,
        "Manufacturer": {"Name": manufacturer},
        "Description": {"ProductDescription": "Battery holder"},
        "QuantityAvailable": stock,
        "ProductVariations": [{
            "DigiKeyProductNumber": number,
            "MinimumOrderQuantity": 1,
            "PackageType": {"Name": "Bulk"},
            "StandardPricing": [{"BreakQuantity": 1, "UnitPrice": 1.25}],
        }],
        "Parameters": [{"ParameterText": "Battery Size", "ValueText": "AA"}],
    }


class FakeDigiKey:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request):
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 599})
        self.requests.append(request)
        return self.responses.pop(0)


@pytest.fixture
async def digikey():
    clients = []

    def create(fake, quota=None):
        client = DigiKeyClient(client_id="id", client_secret="secret", quota=quota)
        client._http = httpx.AsyncClient(transport=httpx.MockTransport(fake))
        clients.append(client)
        return client

    yield create
    for client in clients:
        await client.close()


def assert_keyword_request(fake, pn="209"):
    assert [(r.method, r.url.path) for r in fake.requests] == [("POST", "/products/v4/search/keyword")]
    assert json.loads(fake.requests[0].content) == {"Keywords": pn, "Limit": 10, "Offset": 0}


async def test_products_only_exact_mpn_is_normalized_and_cached(digikey):
    fake = FakeDigiKey(httpx.Response(200, json={
        "Products": [product("209-5"), product(), product("2090")],
    }))
    client = digikey(fake)
    result = await client.get_part(" 209 ")
    assert result["total"] == 1
    part = result["results"][0]
    assert part["source"] == "digikey"
    assert part["part_number"] == "36-209-ND"
    assert part["mfr_part_number"] == "209"
    assert part["manufacturer"] == "Keystone Electronics"
    assert part["stock"] == 56856
    assert part["description"] == "Battery holder"
    assert part["price"] == 1.25
    assert part["price_breaks"] == [{"qty": 1, "price": 1.25}]
    assert part["min_qty"] == 1
    assert part["packaging"] == "Bulk"
    assert part["parameters"] == {"Battery Size": "AA"}
    assert await client.get_part("209") == result
    assert_keyword_request(fake)
    expires, _ = client._cache._data["digikey:209"]
    assert DIGIKEY_CACHE_TTL - 10 < expires - time.time() <= DIGIKEY_CACHE_TTL


@pytest.mark.parametrize("pn", ["AO3400A", "LM358DR", "NE555DR", "BSS138", "USBLC6-2SC6", "AMS1117-3.3", "SS34", "209"])
async def test_multi_maker_sorted_by_stock_with_stable_ties(digikey, pn):
    fake = FakeDigiKey(httpx.Response(200, json={
        "ExactMatches": [product(pn, "A", stock=1), product(pn, "B", stock=20), product(pn, "C", stock=None)],
        "Products": [product(pn, "D", stock=20), product(pn + "X", "Wrong", stock=999)],
    }))
    result = await digikey(fake).get_part(pn)
    assert result["total"] == 4
    assert [(p["manufacturer"], p["stock"]) for p in result["results"]] == [("B", 20), ("D", 20), ("A", 1), ("C", 0)]
    assert_keyword_request(fake, pn)


async def test_deduplication_strips_and_casefolds_mpn(digikey):
    fake = FakeDigiKey(httpx.Response(200, json={
        "ExactMatches": [product("Ao3400A")],
        "Products": [product(" ao3400a "), product("AO3400AX")],
    }))
    result = await digikey(fake).get_part("AO3400A")
    assert result["total"] == len(result["results"]) == 1
    assert result["results"][0]["mfr_part_number"] == "Ao3400A"
    assert_keyword_request(fake, "AO3400A")


async def test_digikey_exact_match_trusted_and_selects_packaging(digikey):
    p = product("AO3400A", number="785-1000-1-ND")
    p["ProductVariations"].append({
        "DigiKeyProductNumber": "785-1000-2-ND", "MinimumOrderQuantity": 3000,
        "PackageType": {"Name": "Tape & Reel"},
        "StandardPricing": [{"BreakQuantity": 3000, "UnitPrice": 0.05}],
    })
    fake = FakeDigiKey(httpx.Response(200, json={"ExactMatches": [p], "Products": [p]}))
    result = await digikey(fake).get_part("785-1000-2-ND")
    assert result["total"] == 1
    found = result["results"][0]
    assert (found["part_number"], found["min_qty"], found["price"]) == ("785-1000-2-ND", 3000, 0.05)
    assert found["other_packaging"] == [{"part_number": "785-1000-1-ND", "packaging": "Bulk", "min_qty": 1, "price": 1.25}]
    assert_keyword_request(fake, "785-1000-2-ND")


@pytest.mark.parametrize("keyword", [
    httpx.Response(200, json={"ExactMatches": [], "Products": [product("AO3400A")]}),
    httpx.Response(200, json={"ExactMatches": [], "Products": []}),
    httpx.Response(404),
])
@pytest.mark.parametrize("pn", ["209", "AO3400AXQ"])
async def test_miss_has_cached_hint(digikey, keyword, pn):
    fake = FakeDigiKey(keyword)
    client = digikey(fake)
    result = await client.get_part(pn)
    assert result == {
        "error": f"Part not found: {pn}",
        "hint": "DigiKey has no exact match for this number. If you have it, try the DigiKey part number (usually ending in -ND).",
    }
    assert await client.get_part(pn) == result
    assert_keyword_request(fake, pn)
    expires, _ = client._cache._data[f"digikey:{pn}"]
    assert DIGIKEY_NOT_FOUND_TTL - 10 < expires - time.time() <= DIGIKEY_NOT_FOUND_TTL


@pytest.mark.parametrize("pn", ["NOPE-ND", "nope-nd"])
async def test_digikey_number_miss_has_no_hint(digikey, pn):
    fake = FakeDigiKey(httpx.Response(404))
    client = digikey(fake)
    result = await client.get_part(pn)
    assert result == {"error": f"Part not found: {pn}"}
    assert await client.get_part(pn) == result
    assert_keyword_request(fake, pn)


async def test_quota_and_usage_count_one_request_and_no_retry_events(digikey):
    quota = DailyQuota("DigiKey", 1000)
    fake = FakeDigiKey(httpx.Response(200, json={"Products": [product()]}))
    client = digikey(fake, quota)
    result = await client.get_part("209", caller="203.0.113.7")
    assert await client.get_part("209") == result
    assert quota.status()["used_today"] == 1
    assert quota.callers._counts == {"203.0.113.7": 1}
    assert stats.usage.summary()["totals"]["distributors"]["digikey"] == {"sent": 1, "cached": 1, "rate_limited": 0}
    assert_keyword_request(fake)


async def test_quota_refusal_is_recorded_and_not_cached(digikey):
    quota = DailyQuota("DigiKey", 0)
    fake = FakeDigiKey()
    client = digikey(fake, quota)
    result = await client.get_part("209")
    assert "daily quota exceeded" in result["error"]
    assert client._cache.get("digikey:209") is None
    assert await client.get_part("209") == result
    assert fake.requests == [] and quota.status()["used_today"] == 0
    assert stats.usage.summary()["totals"]["distributors"]["digikey"] == {"sent": 0, "cached": 0, "rate_limited": 2}


async def test_rate_limit_is_not_cached_as_not_found(digikey):
    fake = FakeDigiKey(httpx.Response(429), httpx.Response(200, json={"Products": [product()]}))
    client = digikey(fake)
    assert await client.get_part("209") == {"error": "DigiKey is limiting requests (HTTP 429). Try again later."}
    assert client._cache.get("digikey:209") is None
    assert_keyword_request(fake)
    assert (await client.get_part("209"))["total"] == 1
    assert len(fake.requests) == 2


async def test_other_errors_propagate_without_caching(digikey):
    fake = FakeDigiKey(httpx.Response(500))
    client = digikey(fake)
    with pytest.raises(DigiKeyError, match="DigiKey API returned HTTP 500"):
        await client.get_part("209")
    assert client._cache.get("digikey:209") is None
    assert_keyword_request(fake)
