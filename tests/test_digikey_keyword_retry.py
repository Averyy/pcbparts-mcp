"""All-digit DigiKey MPN lookups retry with exact keyword matches, without live requests."""

import json
import time

import httpx
import pytest

from pcbparts_mcp import stats
from pcbparts_mcp.cache import DailyQuota
from pcbparts_mcp.config import DIGIKEY_CACHE_TTL, DIGIKEY_NOT_FOUND_TTL
from pcbparts_mcp.digikey import DigiKeyClient, DigiKeyError


def product(mpn="209", manufacturer="Keystone Electronics", number="36-209-ND"):
    return {
        "ManufacturerProductNumber": mpn,
        "Manufacturer": {"Name": manufacturer},
        "Description": {"ProductDescription": "Battery holder"},
        "QuantityAvailable": 56856,
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


def assert_retry_requests(fake):
    assert [(r.method, r.url.path) for r in fake.requests] == [
        ("GET", "/products/v4/search/209/productdetails"),
        ("POST", "/products/v4/search/keyword"),
    ]
    assert json.loads(fake.requests[1].content) == {"Keywords": "209", "Limit": 50, "Offset": 0}


@pytest.mark.parametrize("details", [httpx.Response(404), httpx.Response(200, json={"Product": {}})])
async def test_only_exact_keyword_matches_are_normalized_and_cached(digikey, details):
    fake = FakeDigiKey(details, httpx.Response(200, json={
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
    assert_retry_requests(fake)
    expires, _ = client._cache._data["digikey:209"]
    assert DIGIKEY_CACHE_TTL - 10 < expires - time.time() <= DIGIKEY_CACHE_TTL


async def test_all_manufacturers_are_returned_in_exact_matches_first_order(digikey):
    fake = FakeDigiKey(httpx.Response(404), httpx.Response(200, json={
        "ExactMatches": [product()],
        "Products": [product(manufacturer="Other Maker", number="OTHER-209-ND")],
    }))
    result = await digikey(fake).get_part("209")
    assert result["total"] == 2
    assert [(p["manufacturer"], p["part_number"]) for p in result["results"]] == [
        ("Keystone Electronics", "36-209-ND"), ("Other Maker", "OTHER-209-ND"),
    ]
    assert_retry_requests(fake)


async def test_duplicates_across_exact_matches_and_products_are_removed(digikey):
    fake = FakeDigiKey(httpx.Response(404), httpx.Response(200, json={
        "ExactMatches": [product("2090"), product()],
        "Products": [product(), product("209-5")],
    }))
    result = await digikey(fake).get_part("209")
    assert result["total"] == len(result["results"]) == 1
    assert result["results"][0]["mfr_part_number"] == "209"
    assert_retry_requests(fake)


async def test_exact_comparison_strips_manufacturer_part_number(digikey):
    fake = FakeDigiKey(httpx.Response(404), httpx.Response(200, json={"Products": [product(" 209 ")]}))
    result = await digikey(fake).get_part("209")
    assert result["total"] == 1
    assert result["results"][0]["mfr_part_number"] == " 209 "
    assert_retry_requests(fake)


@pytest.mark.parametrize("keyword", [
    httpx.Response(200, json={"ExactMatches": [], "Products": [product("2090"), product("209-5")]}),
    httpx.Response(200, json={"ExactMatches": [], "Products": []}),
    httpx.Response(404),
])
async def test_no_exact_match_has_a_cached_hint(digikey, keyword):
    fake = FakeDigiKey(httpx.Response(404), keyword)
    client = digikey(fake)
    result = await client.get_part("209")
    assert result == {
        "error": "Part not found: 209",
        "hint": "DigiKey found no exact match for this all-digit number by lookup or keyword search. "
                "If you have it, try the DigiKey part number (usually ending in -ND).",
    }
    assert await client.get_part("209") == result
    assert_retry_requests(fake)
    expires, _ = client._cache._data["digikey:209"]
    assert DIGIKEY_NOT_FOUND_TTL - 10 < expires - time.time() <= DIGIKEY_NOT_FOUND_TTL


async def test_quota_and_usage_count_both_requests_but_not_cached_repeats(digikey):
    quota = DailyQuota("DigiKey", 1000)
    fake = FakeDigiKey(httpx.Response(404), httpx.Response(200, json={"Products": [product()]}))
    client = digikey(fake, quota)
    result = await client.get_part("209", caller="203.0.113.7")
    assert await client.get_part("209") == result
    assert quota.status()["used_today"] == 2
    assert stats.usage.summary()["totals"]["distributors"]["digikey"] == {
        "sent": 2, "cached": 1, "rate_limited": 0,
    }
    assert_retry_requests(fake)


async def test_quota_refusal_before_retry_is_recorded_and_not_cached(digikey):
    quota = DailyQuota("DigiKey", 1)
    fake = FakeDigiKey(httpx.Response(404))
    client = digikey(fake, quota)
    result = await client.get_part("209")
    assert result == quota.check()
    assert "daily quota exceeded" in result["error"]
    assert client._cache.get("digikey:209") is None
    assert await client.get_part("209") == result
    assert quota.status()["used_today"] == 1
    assert [(r.method, r.url.path) for r in fake.requests] == [
        ("GET", "/products/v4/search/209/productdetails"),
    ]
    assert stats.usage.summary()["totals"]["distributors"]["digikey"] == {
        "sent": 1, "cached": 0, "rate_limited": 2,
    }


async def test_retry_rate_limit_is_not_cached_as_not_found(digikey):
    fake = FakeDigiKey(httpx.Response(404), httpx.Response(429),
                       httpx.Response(404), httpx.Response(200, json={"Products": [product()]}))
    client = digikey(fake)
    result = await client.get_part("209")
    assert result == {"error": "DigiKey is limiting requests (HTTP 429). Try again later."}
    assert client._cache.get("digikey:209") is None
    assert_retry_requests(fake)
    assert (await client.get_part("209"))["total"] == 1
    assert len(fake.requests) == 4


async def test_other_retry_errors_propagate_without_caching(digikey):
    fake = FakeDigiKey(httpx.Response(404), httpx.Response(500))
    client = digikey(fake)
    with pytest.raises(DigiKeyError, match="DigiKey API returned HTTP 500"):
        await client.get_part("209")
    assert client._cache.get("digikey:209") is None
    assert_retry_requests(fake)


async def test_non_digit_miss_sends_one_request_without_hint(digikey):
    fake = FakeDigiKey(httpx.Response(404))
    client = digikey(fake)
    assert await client.get_part("LM358") == {"error": "Part not found: LM358"}
    assert [(r.method, r.url.path) for r in fake.requests] == [
        ("GET", "/products/v4/search/LM358/productdetails"),
    ]


async def test_all_digit_details_success_sends_no_keyword_request(digikey):
    fake = FakeDigiKey(httpx.Response(200, json={"Product": product()}))
    result = await digikey(fake).get_part("209")
    assert result["total"] == 1
    assert result["results"][0]["part_number"] == "36-209-ND"
    assert [(r.method, r.url.path) for r in fake.requests] == [
        ("GET", "/products/v4/search/209/productdetails"),
    ]
