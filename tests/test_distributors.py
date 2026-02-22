"""Tests for Mouser, DigiKey, and CSE distributor clients."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pcbparts_mcp.mouser import MouserClient, MouserAPIError, _parse_stock, _parse_price, _normalize_part
from pcbparts_mcp.digikey import DigiKeyClient, _normalize_product
from pcbparts_mcp.cse import CSEClient, _normalize_part as cse_normalize_part
from pcbparts_mcp.cache import TTLCache


# --- TTLCache tests ---

class TestTTLCache:
    def test_get_set(self):
        cache = TTLCache(ttl=60)
        cache.set("key", "value")
        assert cache.get("key") == "value"

    def test_get_miss(self):
        cache = TTLCache(ttl=60)
        assert cache.get("missing") is None

    def test_expired_entry(self):
        cache = TTLCache(ttl=0.01)
        cache.set("key", "value")
        time.sleep(0.02)
        assert cache.get("key") is None

    def test_max_size_lru_eviction(self):
        cache = TTLCache(ttl=3600, max_size=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # Should evict "a" (oldest)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("d") == 4
        assert len(cache) <= 3

    def test_len(self):
        cache = TTLCache(ttl=60)
        assert len(cache) == 0
        cache.set("a", 1)
        assert len(cache) == 1


# --- Mouser helper tests ---

class TestMouserParseStock:
    def test_normal(self):
        assert _parse_stock("16563 In Stock") == 16563

    def test_with_commas(self):
        assert _parse_stock("1,234,567 In Stock") == 1234567

    def test_zero(self):
        assert _parse_stock("0 In Stock") == 0

    def test_none(self):
        assert _parse_stock(None) == 0

    def test_empty(self):
        assert _parse_stock("") == 0

    def test_no_number(self):
        assert _parse_stock("None") == 0

    def test_lead_time_not_matched(self):
        """Lead time numbers should NOT be matched as stock."""
        assert _parse_stock("Factory Lead Time: 14 Weeks") == 0


class TestMouserParsePrice:
    def test_usd(self):
        assert _parse_price("$0.414") == 0.414

    def test_cad(self):
        assert _parse_price("$1.23") == 1.23

    def test_euro(self):
        assert _parse_price("€0.350") == 0.350

    def test_none(self):
        assert _parse_price(None) is None

    def test_empty(self):
        assert _parse_price("") is None


class TestMouserNormalizePart:
    def test_full_part(self):
        raw = {
            "MouserPartNumber": "595-LM358P",
            "ManufacturerPartNumber": "LM358P",
            "Manufacturer": "Texas Instruments",
            "Description": "Dual Op Amp",
            "Category": "Operational Amplifiers - Op Amps",
            "Availability": "16563 In Stock",
            "AvailabilityInStock": "16563",
            "DataSheetUrl": "https://example.com/ds.pdf",
            "ProductDetailUrl": "https://www.mouser.com/ProductDetail/...",
            "ROHSStatus": "RoHS Compliant",
            "IsDiscontinued": "No",
            "Min": "1",
            "PriceBreaks": [
                {"Quantity": 1, "Price": "$0.41", "Currency": "USD"},
                {"Quantity": 10, "Price": "$0.29", "Currency": "USD"},
            ],
            "ProductAttributes": [
                {"AttributeName": "Packaging", "AttributeValue": "Tube", "AttributeCost": ""},
            ],
        }
        result = _normalize_part(raw)
        assert result["source"] == "mouser"
        assert result["part_number"] == "595-LM358P"
        assert result["mfr_part_number"] == "LM358P"
        assert result["manufacturer"] == "Texas Instruments"
        assert result["stock"] == 16563
        assert result["price"] == 0.41
        assert len(result["price_breaks"]) == 2
        assert result["price_breaks"][1]["qty"] == 10
        assert result["price_breaks"][1]["price"] == 0.29
        assert result["price_breaks"][0]["currency"] == "USD"
        assert result["datasheet_url"] == "https://example.com/ds.pdf"
        assert result["rohs"] == "RoHS Compliant"
        assert result["lifecycle"] == "Active"
        assert result["parameters"]["Packaging"] == "Tube"
        assert result["min_qty"] == 1
        assert result["currency"] == "USD"

    def test_discontinued_part(self):
        raw = {
            "MouserPartNumber": "123-ABC",
            "ManufacturerPartNumber": "ABC",
            "Manufacturer": "Test",
            "Description": "Test part",
            "Category": "Test",
            "Availability": "0 In Stock",
            "IsDiscontinued": "Yes",
            "Min": "1",
            "PriceBreaks": [],
            "ProductAttributes": [],
        }
        result = _normalize_part(raw)
        assert result["lifecycle"] == "Discontinued"
        assert result["stock"] == 0
        assert result["price"] is None

    def test_missing_fields(self):
        """Handles missing/empty fields gracefully."""
        result = _normalize_part({})
        assert result["source"] == "mouser"
        assert result["part_number"] == ""
        assert result["stock"] == 0
        assert result["price"] is None
        assert result["price_breaks"] == []
        assert result["parameters"] == {}


# --- DigiKey helper tests ---

class TestDigiKeyNormalizeProduct:
    def test_full_product(self):
        raw = {
            "Description": {
                "ProductDescription": "Dual Op Amp",
                "DetailedDescription": "Op Amps - Dual GP",
            },
            "Manufacturer": {"Id": 296, "Name": "Texas Instruments"},
            "ManufacturerProductNumber": "LM358P",
            "UnitPrice": 0.29,
            "ProductUrl": "https://www.digikey.com/...",
            "DatasheetUrl": "https://www.ti.com/ds.pdf",
            "QuantityAvailable": 15234,
            "ProductStatus": {"Id": 0, "Status": "Active"},
            "Discontinued": False,
            "Category": {"CategoryId": 10, "Name": "Op Amps"},
            "Classifications": {"RohsStatus": "ROHS3 Compliant"},
            "ProductVariations": [
                {
                    "DigiKeyProductNumber": "296-1395-5-ND",
                    "MinimumOrderQuantity": 1,
                    "StandardPricing": [
                        {"BreakQuantity": 1, "UnitPrice": 0.41, "TotalPrice": 0.41},
                        {"BreakQuantity": 10, "UnitPrice": 0.346, "TotalPrice": 3.46},
                    ],
                }
            ],
            "Parameters": [
                {"ParameterId": 1, "ParameterText": "Amplifier Type", "ValueText": "General Purpose"},
                {"ParameterId": 2, "ParameterText": "Number of Circuits", "ValueText": "2"},
            ],
        }
        result = _normalize_product(raw)
        assert result["source"] == "digikey"
        assert result["part_number"] == "296-1395-5-ND"
        assert result["mfr_part_number"] == "LM358P"
        assert result["manufacturer"] == "Texas Instruments"
        assert result["stock"] == 15234
        assert result["price"] == 0.29
        assert len(result["price_breaks"]) == 2
        assert result["price_breaks"][0]["qty"] == 1
        assert result["price_breaks"][0]["price"] == 0.41
        assert result["datasheet_url"] == "https://www.ti.com/ds.pdf"
        assert result["rohs"] == "ROHS3 Compliant"
        assert result["lifecycle"] == "Active"
        assert result["parameters"]["Amplifier Type"] == "General Purpose"
        assert result["min_qty"] == 1
        assert result["category"] == "Op Amps"

    def test_discontinued_product(self):
        raw = {
            "Description": {"ProductDescription": "Old part"},
            "Manufacturer": {"Name": "Test"},
            "ManufacturerProductNumber": "OLD123",
            "QuantityAvailable": 0,
            "ProductStatus": {"Status": "Active"},
            "Discontinued": True,
            "Category": {},
            "Classifications": {},
            "ProductVariations": [],
            "Parameters": [],
        }
        result = _normalize_product(raw)
        assert result["lifecycle"] == "Discontinued"
        assert result["stock"] == 0

    def test_missing_fields(self):
        """Handles missing/empty fields gracefully."""
        result = _normalize_product({})
        assert result["source"] == "digikey"
        assert result["mfr_part_number"] == ""
        assert result["stock"] == 0
        assert result["price"] is None
        assert result["price_breaks"] == []
        assert result["parameters"] == {}


# --- Mouser client tests ---

class TestMouserClient:
    @pytest.fixture
    def client(self):
        c = MouserClient(api_key="test-key")
        c._get_client()  # Eagerly init for patching in tests
        return c

    @pytest.mark.asyncio
    async def test_search(self, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Errors": [],
            "SearchResults": {
                "NumberOfResult": 1,
                "Parts": [{
                    "MouserPartNumber": "595-LM358P",
                    "ManufacturerPartNumber": "LM358P",
                    "Manufacturer": "Texas Instruments",
                    "Description": "Dual Op Amp",
                    "Category": "Op Amps",
                    "Availability": "100 In Stock",
                    "Min": "1",
                    "PriceBreaks": [{"Quantity": 1, "Price": "$0.41", "Currency": "USD"}],
                    "ProductAttributes": [],
                }],
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client._client, "post", new_callable=AsyncMock, return_value=mock_response):
            result = await client.search("LM358")

        assert result["total"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["mfr_part_number"] == "LM358P"
        assert result["page"] == 1

    @pytest.mark.asyncio
    async def test_search_with_manufacturer(self, client):
        """When manufacturer is provided, uses the keywordandmanufacturer endpoint."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Errors": [],
            "SearchResults": {"NumberOfResult": 0, "Parts": []},
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client._client, "post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
            await client.search("LM358", manufacturer="TI", in_stock_only=True, records=10, page=2)

        # Verify the request body uses manufacturer endpoint
        call_args = mock_post.call_args
        url = call_args.args[0] if call_args.args else call_args[0][0]
        assert "keywordandmanufacturer" in url
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        req = body["SearchByKeywordMfrNameRequest"]
        assert req["manufacturerName"] == "TI"
        assert req["searchOptions"] == "InStock"
        assert req["records"] == 10
        assert req["pageNumber"] == 2

    @pytest.mark.asyncio
    async def test_search_without_manufacturer(self, client):
        """When no manufacturer, uses the keyword-only endpoint."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Errors": [],
            "SearchResults": {"NumberOfResult": 0, "Parts": []},
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client._client, "post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
            await client.search("LM358")

        call_args = mock_post.call_args
        url = call_args.args[0] if call_args.args else call_args[0][0]
        assert "/search/keyword?" in url
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        assert "SearchByKeywordRequest" in body

    @pytest.mark.asyncio
    async def test_get_part_single(self, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Errors": [],
            "SearchResults": {
                "NumberOfResult": 1,
                "Parts": [{
                    "MouserPartNumber": "595-LM358P",
                    "ManufacturerPartNumber": "LM358P",
                    "Manufacturer": "TI",
                    "Description": "Op Amp",
                    "Category": "Op Amps",
                    "Availability": "500 In Stock",
                    "Min": "1",
                    "PriceBreaks": [],
                    "ProductAttributes": [],
                }],
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client._client, "post", new_callable=AsyncMock, return_value=mock_response):
            result = await client.get_part("595-LM358P")

        assert result["total"] == 1
        assert result["results"][0]["part_number"] == "595-LM358P"

    @pytest.mark.asyncio
    async def test_get_part_batch(self, client):
        """Pipe-delimited batch lookups should work."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Errors": [],
            "SearchResults": {
                "NumberOfResult": 2,
                "Parts": [
                    {"MouserPartNumber": "595-LM358P", "ManufacturerPartNumber": "LM358P",
                     "Manufacturer": "TI", "Description": "", "Category": "",
                     "Availability": "", "Min": "1", "PriceBreaks": [], "ProductAttributes": []},
                    {"MouserPartNumber": "511-LM358P", "ManufacturerPartNumber": "LM358P",
                     "Manufacturer": "ON Semi", "Description": "", "Category": "",
                     "Availability": "", "Min": "1", "PriceBreaks": [], "ProductAttributes": []},
                ],
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client._client, "post", new_callable=AsyncMock, return_value=mock_response):
            result = await client.get_part("595-LM358P|511-LM358P")

        assert result["total"] == 2
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_api_error(self, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Errors": [{"Code": "InvalidKey", "Message": "Invalid API Key"}],
            "SearchResults": None,
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client._client, "post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(MouserAPIError) as exc_info:
                await client.search("test")
            assert exc_info.value.code == "InvalidKey"

    @pytest.mark.asyncio
    async def test_cache_hit(self, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Errors": [],
            "SearchResults": {
                "NumberOfResult": 1,
                "Parts": [{
                    "MouserPartNumber": "595-LM358P", "ManufacturerPartNumber": "LM358P",
                    "Manufacturer": "TI", "Description": "", "Category": "",
                    "Availability": "", "Min": "1", "PriceBreaks": [], "ProductAttributes": [],
                }],
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client._client, "post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
            # First call hits API
            await client.get_part("595-LM358P")
            # Second call should use cache
            await client.get_part("595-LM358P")

        assert mock_post.call_count == 1


# --- DigiKey client tests ---

class TestDigiKeyClient:
    @pytest.fixture
    def client(self):
        c = DigiKeyClient(client_id="test-id", client_secret="test-secret")
        c._get_http()  # Eagerly init for patching in tests
        return c

    def _mock_token_response(self):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "access_token": "test-token-123",
            "expires_in": 599,
            "token_type": "Bearer",
        }
        resp.raise_for_status = MagicMock()
        return resp

    @pytest.mark.asyncio
    async def test_token_refresh(self, client):
        """Token is fetched on first request."""
        token_resp = self._mock_token_response()
        search_resp = MagicMock()
        search_resp.status_code = 200
        search_resp.json.return_value = {
            "Products": [],
            "ProductsCount": 0,
            "ExactMatches": [],
        }
        search_resp.raise_for_status = MagicMock()

        async def mock_request(method, url, **kwargs):
            if "oauth2/token" in url:
                return token_resp
            return search_resp

        # Also need to handle the post call for token
        async def mock_post(url, **kwargs):
            return token_resp

        with patch.object(client._http, "post", side_effect=mock_post):
            with patch.object(client._http, "request", side_effect=mock_request):
                await client.search("test")

        assert client._access_token == "test-token-123"

    @pytest.mark.asyncio
    async def test_token_reuse(self, client):
        """Token is reused when still valid."""
        # Pre-set a valid token
        client._access_token = "existing-token"
        client._token_expires_at = time.time() + 500

        search_resp = MagicMock()
        search_resp.status_code = 200
        search_resp.json.return_value = {
            "Products": [],
            "ProductsCount": 0,
            "ExactMatches": [],
        }
        search_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "request", new_callable=AsyncMock, return_value=search_resp):
            await client.search("test")

        # Token should not have changed
        assert client._access_token == "existing-token"

    @pytest.mark.asyncio
    async def test_search(self, client):
        client._access_token = "token"
        client._token_expires_at = time.time() + 500

        search_resp = MagicMock()
        search_resp.status_code = 200
        search_resp.json.return_value = {
            "Products": [{
                "Description": {"ProductDescription": "Dual Op Amp"},
                "Manufacturer": {"Name": "TI"},
                "ManufacturerProductNumber": "LM358P",
                "UnitPrice": 0.29,
                "QuantityAvailable": 15234,
                "ProductStatus": {"Status": "Active"},
                "Discontinued": False,
                "Category": {"Name": "Op Amps"},
                "Classifications": {},
                "ProductVariations": [{
                    "DigiKeyProductNumber": "296-1395-5-ND",
                    "MinimumOrderQuantity": 1,
                    "StandardPricing": [
                        {"BreakQuantity": 1, "UnitPrice": 0.41, "TotalPrice": 0.41},
                    ],
                }],
                "Parameters": [],
            }],
            "ProductsCount": 1,
            "ExactMatches": [],
        }
        search_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "request", new_callable=AsyncMock, return_value=search_resp):
            result = await client.search("LM358")

        assert result["total"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["mfr_part_number"] == "LM358P"
        assert result["results"][0]["stock"] == 15234

    @pytest.mark.asyncio
    async def test_search_empty_mpn_dedup(self, client):
        """Products with empty MPNs should not be deduplicated against each other."""
        client._access_token = "token"
        client._token_expires_at = time.time() + 500

        search_resp = MagicMock()
        search_resp.status_code = 200
        search_resp.json.return_value = {
            "Products": [
                {
                    "Description": {"ProductDescription": "Kit A"},
                    "Manufacturer": {"Name": "TI"},
                    "ManufacturerProductNumber": "",
                    "QuantityAvailable": 100,
                    "ProductStatus": {"Status": "Active"},
                    "Category": {},
                    "Classifications": {},
                    "ProductVariations": [],
                    "Parameters": [],
                },
                {
                    "Description": {"ProductDescription": "Kit B"},
                    "Manufacturer": {"Name": "TI"},
                    "ManufacturerProductNumber": "",
                    "QuantityAvailable": 50,
                    "ProductStatus": {"Status": "Active"},
                    "Category": {},
                    "Classifications": {},
                    "ProductVariations": [],
                    "Parameters": [],
                },
            ],
            "ProductsCount": 2,
            "ExactMatches": [],
        }
        search_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "request", new_callable=AsyncMock, return_value=search_resp):
            result = await client.search("test kits")

        # Both products should be returned (not deduplicated)
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_get_part(self, client):
        client._access_token = "token"
        client._token_expires_at = time.time() + 500

        detail_resp = MagicMock()
        detail_resp.status_code = 200
        detail_resp.json.return_value = {
            "Product": {
                "Description": {"ProductDescription": "Dual Op Amp"},
                "Manufacturer": {"Name": "TI"},
                "ManufacturerProductNumber": "LM358P",
                "UnitPrice": 0.29,
                "QuantityAvailable": 15234,
                "ProductStatus": {"Status": "Active"},
                "Discontinued": False,
                "Category": {"Name": "Op Amps"},
                "Classifications": {"RohsStatus": "ROHS3 Compliant"},
                "ProductVariations": [],
                "Parameters": [
                    {"ParameterId": 1, "ParameterText": "Type", "ValueText": "General Purpose"},
                ],
            },
        }
        detail_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "request", new_callable=AsyncMock, return_value=detail_resp):
            result = await client.get_part("LM358P")

        # get_part now returns wrapped format consistent with Mouser
        assert result["total"] == 1
        assert result["results"][0]["mfr_part_number"] == "LM358P"
        assert result["results"][0]["parameters"]["Type"] == "General Purpose"

    @pytest.mark.asyncio
    async def test_get_part_not_found(self, client):
        client._access_token = "token"
        client._token_expires_at = time.time() + 500

        detail_resp = MagicMock()
        detail_resp.status_code = 200
        detail_resp.json.return_value = {"Product": {}}
        detail_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "request", new_callable=AsyncMock, return_value=detail_resp):
            result = await client.get_part("NONEXISTENT")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_cache_hit(self, client):
        client._access_token = "token"
        client._token_expires_at = time.time() + 500

        detail_resp = MagicMock()
        detail_resp.status_code = 200
        detail_resp.json.return_value = {
            "Product": {
                "Description": {"ProductDescription": "Test"},
                "Manufacturer": {"Name": "Test"},
                "ManufacturerProductNumber": "TEST123",
                "QuantityAvailable": 100,
                "ProductStatus": {"Status": "Active"},
                "Category": {},
                "Classifications": {},
                "ProductVariations": [],
                "Parameters": [],
            },
        }
        detail_resp.raise_for_status = MagicMock()

        with patch.object(client._http, "request", new_callable=AsyncMock, return_value=detail_resp) as mock_req:
            await client.get_part("TEST123")
            await client.get_part("TEST123")

        assert mock_req.call_count == 1

    @pytest.mark.asyncio
    async def test_token_expired_retry(self, client):
        """When API returns 401, token is refreshed and request retried."""
        client._access_token = "expired-token"
        client._token_expires_at = time.time() + 500

        # First response: 401, second: success
        resp_401 = MagicMock()
        resp_401.status_code = 401

        resp_ok = MagicMock()
        resp_ok.status_code = 200
        resp_ok.json.return_value = {
            "Products": [],
            "ProductsCount": 0,
            "ExactMatches": [],
        }
        resp_ok.raise_for_status = MagicMock()

        call_count = 0

        async def mock_request(method, url, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return resp_401
            return resp_ok

        token_resp = self._mock_token_response()

        async def mock_post(url, **kwargs):
            return token_resp

        with patch.object(client._http, "request", side_effect=mock_request):
            with patch.object(client._http, "post", side_effect=mock_post):
                result = await client.search("test")

        assert result["total"] == 0
        # Token should be refreshed
        assert client._access_token == "test-token-123"

    @pytest.mark.asyncio
    async def test_oauth_error_response(self, client):
        """Token endpoint returning an OAuth error should raise ValueError."""
        error_resp = MagicMock()
        error_resp.status_code = 200
        error_resp.json.return_value = {
            "error": "invalid_client",
            "error_description": "Client not found",
        }
        error_resp.raise_for_status = MagicMock()

        async def mock_post(url, **kwargs):
            return error_resp

        with patch.object(client._http, "post", side_effect=mock_post):
            with pytest.raises(ValueError, match="DigiKey OAuth error"):
                await client._ensure_token()


# --- Server-level graceful degradation tests ---

class TestGracefulDegradation:
    """Test that tools return helpful errors when API keys aren't configured."""

    @pytest.mark.asyncio
    async def test_mouser_search_no_key(self):
        from pcbparts_mcp.server import mouser_search
        import pcbparts_mcp.server as srv
        original = srv._mouser_client
        srv._mouser_client = None
        try:
            result = await mouser_search(keyword="test")
            assert "error" in result
            assert "MOUSER_API_KEY" in result["error"]
        finally:
            srv._mouser_client = original

    @pytest.mark.asyncio
    async def test_mouser_get_part_no_key(self):
        from pcbparts_mcp.server import mouser_get_part
        import pcbparts_mcp.server as srv
        original = srv._mouser_client
        srv._mouser_client = None
        try:
            result = await mouser_get_part(part_number="595-LM358P")
            assert "error" in result
            assert "MOUSER_API_KEY" in result["error"]
        finally:
            srv._mouser_client = original

    @pytest.mark.asyncio
    async def test_digikey_search_no_key(self):
        from pcbparts_mcp.server import digikey_search
        import pcbparts_mcp.server as srv
        original = srv._digikey_client
        srv._digikey_client = None
        try:
            result = await digikey_search(keywords="test")
            assert "error" in result
            assert "DIGIKEY_CLIENT_ID" in result["error"]
        finally:
            srv._digikey_client = original

    @pytest.mark.asyncio
    async def test_digikey_get_part_no_key(self):
        from pcbparts_mcp.server import digikey_get_part
        import pcbparts_mcp.server as srv
        original = srv._digikey_client
        srv._digikey_client = None
        try:
            result = await digikey_get_part(product_number="LM358P")
            assert "error" in result
            assert "DIGIKEY_CLIENT_ID" in result["error"]
        finally:
            srv._digikey_client = original

    @pytest.mark.asyncio
    async def test_mouser_search_keyword_too_long(self):
        from pcbparts_mcp.server import mouser_search
        import pcbparts_mcp.server as srv
        original = srv._mouser_client
        srv._mouser_client = MagicMock()  # Needs to be non-None to pass first check
        try:
            result = await mouser_search(keyword="x" * 501)
            assert "error" in result
            assert "too long" in result["error"]
        finally:
            srv._mouser_client = original

    @pytest.mark.asyncio
    async def test_digikey_search_keywords_too_long(self):
        from pcbparts_mcp.server import digikey_search
        import pcbparts_mcp.server as srv
        original = srv._digikey_client
        srv._digikey_client = MagicMock()
        try:
            result = await digikey_search(keywords="x" * 501)
            assert "error" in result
            assert "too long" in result["error"]
        finally:
            srv._digikey_client = original


# --- CSE normalize tests ---

class TestCSENormalizePart:
    def test_full_api_part(self):
        """Test normalizing a full alligator API response part."""
        raw = {
            "PartNo": "LM358P",
            "Manuf": "Texas Instruments",
            "Desc": "Dual Op Amp",
            "Datasheet": "https://www.ti.com/lit/ds/lm358.pdf",
            "ECAD_M": "https://componentsearchengine.com/model.php?partID=12345",
            "Has3D": "Y",
            "Quality": 3,
            "PartID": 12345,
            "PinCount": 8,
            "ImageL": "https://example.com/img.jpg",
            "ImageS": "https://example.com/img_s.jpg",
        }
        result = cse_normalize_part(raw)
        assert result["source"] == "cse"
        assert result["mfr_part_number"] == "LM358P"
        assert result["manufacturer"] == "Texas Instruments"
        assert result["description"] == "Dual Op Amp"
        assert result["datasheet_url"] == "https://www.ti.com/lit/ds/lm358.pdf"
        assert result["has_model"] is True
        assert result["has_3d"] is True
        assert result["model_quality"] == 3
        assert result["cse_part_id"] == 12345
        assert result["pin_count"] == 8
        assert result["image_url"] == "https://example.com/img.jpg"

    def test_has3d_external(self):
        """Has3D='E' (external) should still count as has_3d=True."""
        raw = {"PartNo": "X", "Manuf": "Y", "Has3D": "E", "ECAD_M": ""}
        result = cse_normalize_part(raw)
        assert result["has_3d"] is True
        assert result["has_model"] is False  # No ECAD_M URL

    def test_has3d_no(self):
        """Has3D='N' or empty means no 3D model."""
        for val in ("N", ""):
            raw = {"PartNo": "X", "Manuf": "Y", "Has3D": val}
            result = cse_normalize_part(raw)
            assert result["has_3d"] is False

    def test_missing_fields(self):
        result = cse_normalize_part({})
        assert result["source"] == "cse"
        assert result["mfr_part_number"] == ""
        assert result["manufacturer"] == ""
        assert result["datasheet_url"] is None
        assert result["has_model"] is False
        assert result["has_3d"] is False
        assert result["model_quality"] == 0
        assert result["cse_part_id"] is None
        assert result["pin_count"] == 0
        assert result["image_url"] is None

    def test_protocol_relative_image(self):
        """Protocol-relative image URLs get https prefix."""
        raw = {"PartNo": "X", "Manuf": "Y", "ImageL": "//cdn.example.com/img.jpg"}
        result = cse_normalize_part(raw)
        assert result["image_url"] == "https://cdn.example.com/img.jpg"

    def test_no_datasheet(self):
        """Empty datasheet string becomes None."""
        raw = {"PartNo": "X", "Manuf": "Y", "Datasheet": ""}
        result = cse_normalize_part(raw)
        assert result["datasheet_url"] is None


# --- CSE client tests ---

class TestCSEClient:
    @pytest.fixture
    def client(self):
        return CSEClient()

    SAMPLE_API_RESPONSE = {
        "status": "Success",
        "partCount": 2,
        "currencyName": "USD",
        "parts": [
            {
                "PartNo": "LM358P",
                "Manuf": "Texas Instruments",
                "ManufID": 18,
                "PartID": 12345,
                "Desc": "Dual Op Amp, 8-Pin PDIP",
                "Datasheet": "https://www.ti.com/lit/ds/lm358.pdf",
                "ECAD_M": "https://componentsearchengine.com/model.php?partID=12345",
                "Has3D": "Y",
                "Quality": 3,
                "PinCount": 8,
                "ImageL": "https://example.com/lm358.jpg",
                "ImageS": "https://example.com/lm358_s.jpg",
                "Package": "",
                "Cost": "",
                "Currency": "",
                "PricingFrom": "",
                "Stock": -1,
                "SupPartURL": "",
            },
            {
                "PartNo": "LM358PWRE4",
                "Manuf": "Texas Instruments",
                "ManufID": 18,
                "PartID": 67890,
                "Desc": "TSSOP Op Amp",
                "Datasheet": "",
                "ECAD_M": "https://componentsearchengine.com/model.php?partID=67890",
                "Has3D": "N",
                "Quality": 2,
                "PinCount": 8,
                "ImageL": "",
                "ImageS": "",
                "Package": "",
                "Cost": "",
                "Currency": "",
                "PricingFrom": "",
                "Stock": -1,
                "SupPartURL": "",
            },
        ],
    }

    SAMPLE_EMPTY_RESPONSE = {
        "status": "Success",
        "partCount": 0,
        "currencyName": "USD",
        "parts": [],
    }

    def _mock_httpx_response(self, json_data, status_code=200):
        """Create a mock httpx.Response that returns json_data."""
        mock_response = MagicMock()
        mock_response.json.return_value = json_data
        mock_response.status_code = status_code
        mock_response.raise_for_status = MagicMock()
        return mock_response

    @pytest.mark.asyncio
    async def test_search(self, client):
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=self._mock_httpx_response(self.SAMPLE_API_RESPONSE))
        client._http = mock_http

        result = await client.search("LM358P")

        assert result["total"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["mfr_part_number"] == "LM358P"
        assert result["results"][0]["has_model"] is True
        assert result["results"][0]["has_3d"] is True
        assert result["results"][0]["datasheet_url"] == "https://www.ti.com/lit/ds/lm358.pdf"
        assert result["results"][0]["pin_count"] == 8
        assert result["results"][1]["mfr_part_number"] == "LM358PWRE4"
        assert result["results"][1]["has_model"] is True
        assert result["results"][1]["has_3d"] is False
        assert result["results"][1]["datasheet_url"] is None  # Empty string -> None

    @pytest.mark.asyncio
    async def test_search_no_results(self, client):
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=self._mock_httpx_response(self.SAMPLE_EMPTY_RESPONSE))
        client._http = mock_http

        result = await client.search("NONEXISTENT_PART_XYZ")

        assert result["total"] == 0
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_search_cached(self, client):
        """Second search with same query uses cache."""
        call_count = 0

        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return self._mock_httpx_response(self.SAMPLE_API_RESPONSE)

        mock_http = AsyncMock()
        mock_http.get = mock_get
        client._http = mock_http

        await client.search("LM358P")
        await client.search("LM358P")

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_search_deduplicates(self, client):
        """Duplicate parts (same MPN+manufacturer) are deduplicated."""
        duped_response = {
            "status": "Success",
            "partCount": 0,
            "parts": [
                {"PartNo": "LM358P", "Manuf": "TI", "PartID": 1, "ECAD_M": "", "Has3D": "N", "Quality": 0, "Datasheet": "", "Desc": "A", "PinCount": 8, "ImageL": "", "ImageS": ""},
                {"PartNo": "LM358P", "Manuf": "TI", "PartID": 2, "ECAD_M": "", "Has3D": "N", "Quality": 0, "Datasheet": "", "Desc": "B", "PinCount": 8, "ImageL": "", "ImageS": ""},
            ],
        }
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=self._mock_httpx_response(duped_response))
        client._http = mock_http

        result = await client.search("LM358P")

        assert len(result["results"]) == 1

    @pytest.mark.asyncio
    async def test_search_with_offset(self, client):
        """Offset parameter is passed to the API."""
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=self._mock_httpx_response(self.SAMPLE_API_RESPONSE))
        client._http = mock_http

        await client.search("LM358P", offset=10)

        # Verify offset was passed in params
        call_args = mock_http.get.call_args
        params = call_args.kwargs.get("params", {})
        assert params.get("offset") == "10"

    @pytest.mark.asyncio
    async def test_search_partcount_fallback(self, client):
        """When partCount is 0 but parts exist, total falls back to len(parts)."""
        response = {
            "status": "Success",
            "partCount": 0,
            "parts": [
                {"PartNo": "X", "Manuf": "Y", "PartID": 1, "ECAD_M": "", "Has3D": "N", "Quality": 0, "Datasheet": "", "Desc": "", "PinCount": 0, "ImageL": "", "ImageS": ""},
            ],
        }
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=self._mock_httpx_response(response))
        client._http = mock_http

        result = await client.search("X")

        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_search_non_success_not_cached(self, client):
        """Non-success API responses should not be cached."""
        error_response = {
            "status": "Error",
            "partCount": 0,
            "parts": [],
        }
        call_count = 0

        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return self._mock_httpx_response(error_response)

        mock_http = AsyncMock()
        mock_http.get = mock_get
        client._http = mock_http

        result1 = await client.search("test_fail")
        assert result1["results"] == []

        # Second call should hit API again (not cached)
        result2 = await client.search("test_fail")
        assert call_count == 2


# --- CSE get_kicad tests ---

class TestCSEGetKicad:
    @pytest.fixture
    def client(self):
        return CSEClient()

    def _make_zip(self, files: dict[str, str]) -> bytes:
        """Create a zip archive in memory with the given filename->content pairs."""
        import io, zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        return buf.getvalue()

    SAMPLE_KICAD_SYM = "(kicad_symbol_lib (version 20211014) (symbol \"LM358P\"))"
    SAMPLE_KICAD_MOD = "(module \"DIP794W53P254L959H508Q8N\" (layer F.Cu))"

    SEARCH_RESPONSE_WITH_MODEL = {
        "status": "Success",
        "partCount": 1,
        "parts": [{
            "PartNo": "LM358P", "Manuf": "Texas Instruments", "ManufID": 18,
            "PartID": 12345, "Desc": "Dual Op Amp",
            "ECAD_M": "https://componentsearchengine.com/model.php?partID=12345",
            "Has3D": "Y", "Quality": 3, "PinCount": 8,
            "Datasheet": "https://example.com/ds.pdf",
            "ImageL": "", "ImageS": "", "Package": "",
            "Cost": "", "Currency": "", "PricingFrom": "", "Stock": -1, "SupPartURL": "",
        }],
    }

    SEARCH_RESPONSE_NO_MODEL = {
        "status": "Success",
        "partCount": 1,
        "parts": [{
            "PartNo": "NOMODEL", "Manuf": "Test", "ManufID": 1,
            "PartID": 99999, "Desc": "No model",
            "ECAD_M": "", "Has3D": "N", "Quality": 0, "PinCount": 0,
            "Datasheet": "", "ImageL": "", "ImageS": "", "Package": "",
            "Cost": "", "Currency": "", "PricingFrom": "", "Stock": -1, "SupPartURL": "",
        }],
    }

    def _mock_httpx_response(self, json_data=None, content=None, status_code=200):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.raise_for_status = MagicMock()
        if json_data is not None:
            mock_response.json.return_value = json_data
        if content is not None:
            mock_response.content = content
        return mock_response

    @pytest.mark.asyncio
    async def test_get_kicad_by_query(self, client):
        """Downloads zip, extracts KiCad files, returns text content."""
        zip_bytes = self._make_zip({
            "LM358P/KiCad/LM358P.kicad_sym": self.SAMPLE_KICAD_SYM,
            "LM358P/KiCad/DIP794.kicad_mod": self.SAMPLE_KICAD_MOD,
            "LM358P/Altium/LM358P.SchLib": b"binary altium data".decode(),
            "LM358P/3D/LM358P.stp": "binary step data",
        })

        search_resp = self._mock_httpx_response(json_data=self.SEARCH_RESPONSE_WITH_MODEL)
        download_resp = self._mock_httpx_response(content=zip_bytes)

        call_urls = []
        async def mock_get(url, **kwargs):
            call_urls.append(str(url))
            if "alligator" in str(url):
                return search_resp
            return download_resp

        mock_http = AsyncMock()
        mock_http.get = mock_get
        client._http = mock_http

        with patch("pcbparts_mcp.cse.CSE_USER", "user"), \
             patch("pcbparts_mcp.cse.CSE_PASS", "pass"):
            result = await client.get_kicad(query="LM358P")

        assert "error" not in result
        assert result["part_id"] == 12345
        assert result["mfr_part_number"] == "LM358P"
        assert result["kicad_symbol"] == self.SAMPLE_KICAD_SYM
        assert result["kicad_footprint"] == self.SAMPLE_KICAD_MOD

    @pytest.mark.asyncio
    async def test_get_kicad_by_part_id(self, client):
        """Can skip search by providing part_id directly."""
        zip_bytes = self._make_zip({
            "X/KiCad/X.kicad_sym": self.SAMPLE_KICAD_SYM,
            "X/KiCad/X.kicad_mod": self.SAMPLE_KICAD_MOD,
        })

        download_resp = self._mock_httpx_response(content=zip_bytes)

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=download_resp)
        client._http = mock_http

        with patch("pcbparts_mcp.cse.CSE_USER", "user"), \
             patch("pcbparts_mcp.cse.CSE_PASS", "pass"):
            result = await client.get_kicad(part_id=12345)

        assert result["part_id"] == 12345
        assert result["kicad_symbol"] == self.SAMPLE_KICAD_SYM
        assert result["kicad_footprint"] == self.SAMPLE_KICAD_MOD

    @pytest.mark.asyncio
    async def test_get_kicad_cached(self, client):
        """Second call uses cache, no download."""
        zip_bytes = self._make_zip({
            "X/KiCad/X.kicad_sym": self.SAMPLE_KICAD_SYM,
            "X/KiCad/X.kicad_mod": self.SAMPLE_KICAD_MOD,
        })

        call_count = 0
        async def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            resp = MagicMock()
            resp.status_code = 200
            resp.content = zip_bytes
            return resp

        mock_http = AsyncMock()
        mock_http.get = mock_get
        client._http = mock_http

        with patch("pcbparts_mcp.cse.CSE_USER", "user"), \
             patch("pcbparts_mcp.cse.CSE_PASS", "pass"):
            await client.get_kicad(part_id=55555)
            result2 = await client.get_kicad(part_id=55555)

        # Cached response should NOT have a special "cached" key anymore
        assert "error" not in result2
        assert call_count == 1  # Only one download

    @pytest.mark.asyncio
    async def test_get_kicad_no_credentials(self, client):
        with patch("pcbparts_mcp.cse.CSE_USER", ""), \
             patch("pcbparts_mcp.cse.CSE_PASS", ""):
            result = await client.get_kicad(query="LM358P")
        assert "error" in result
        assert "CSEARCH_USER" in result["error"]

    @pytest.mark.asyncio
    async def test_get_kicad_no_model_available(self, client):
        """Returns error when search finds parts but none have models."""
        search_resp = self._mock_httpx_response(json_data=self.SEARCH_RESPONSE_NO_MODEL)

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=search_resp)
        client._http = mock_http

        with patch("pcbparts_mcp.cse.CSE_USER", "user"), \
             patch("pcbparts_mcp.cse.CSE_PASS", "pass"):
            result = await client.get_kicad(query="NOMODEL")

        assert "error" in result
        assert "No ECAD model" in result["error"]

    @pytest.mark.asyncio
    async def test_get_kicad_auth_failed(self, client):
        """Returns error on 401."""
        search_resp = self._mock_httpx_response(json_data=self.SEARCH_RESPONSE_WITH_MODEL)
        auth_fail_resp = self._mock_httpx_response(status_code=401)

        async def mock_get(url, **kwargs):
            if "alligator" in str(url):
                return search_resp
            return auth_fail_resp

        mock_http = AsyncMock()
        mock_http.get = mock_get
        client._http = mock_http

        with patch("pcbparts_mcp.cse.CSE_USER", "bad"), \
             patch("pcbparts_mcp.cse.CSE_PASS", "creds"):
            result = await client.get_kicad(query="LM358P")

        assert "error" in result
        assert "authentication failed" in result["error"]

    @pytest.mark.asyncio
    async def test_get_kicad_no_query_or_id(self, client):
        with patch("pcbparts_mcp.cse.CSE_USER", "user"), \
             patch("pcbparts_mcp.cse.CSE_PASS", "pass"):
            result = await client.get_kicad()
        assert "error" in result
        assert "Must provide" in result["error"]


# --- CSE graceful degradation tests ---

class TestCSEGracefulDegradation:
    @pytest.mark.asyncio
    async def test_cse_search_not_initialized(self):
        from pcbparts_mcp.server import cse_search
        import pcbparts_mcp.server as srv
        original = srv._cse_client
        srv._cse_client = None
        try:
            result = await cse_search(query="LM358P")
            assert "error" in result
            assert "not initialized" in result["error"]
        finally:
            srv._cse_client = original

    @pytest.mark.asyncio
    async def test_cse_search_handles_exception(self):
        from pcbparts_mcp.server import cse_search
        import pcbparts_mcp.server as srv
        original = srv._cse_client

        mock_client = MagicMock(spec=CSEClient)
        mock_client.search = AsyncMock(side_effect=ValueError("Connection failed"))
        srv._cse_client = mock_client
        try:
            result = await cse_search(query="LM358P")
            assert "error" in result
            # Error message is now generic (no exception details leaked)
            assert "CSE search failed" in result["error"]
        finally:
            srv._cse_client = original

    @pytest.mark.asyncio
    async def test_cse_get_kicad_not_initialized(self):
        from pcbparts_mcp.server import cse_get_kicad
        import pcbparts_mcp.server as srv
        original = srv._cse_client
        srv._cse_client = None
        try:
            result = await cse_get_kicad(query="LM358P")
            assert "error" in result
            assert "not initialized" in result["error"]
        finally:
            srv._cse_client = original

    @pytest.mark.asyncio
    async def test_cse_get_kicad_no_params(self):
        from pcbparts_mcp.server import cse_get_kicad
        import pcbparts_mcp.server as srv
        original = srv._cse_client
        srv._cse_client = MagicMock(spec=CSEClient)
        try:
            result = await cse_get_kicad()
            assert "error" in result
            assert "Must provide" in result["error"]
        finally:
            srv._cse_client = original

    @pytest.mark.asyncio
    async def test_cse_search_query_too_long(self):
        from pcbparts_mcp.server import cse_search
        import pcbparts_mcp.server as srv
        original = srv._cse_client
        srv._cse_client = MagicMock(spec=CSEClient)
        try:
            result = await cse_search(query="x" * 501)
            assert "error" in result
            assert "too long" in result["error"]
        finally:
            srv._cse_client = original


# --- get_part MPN lookup tests ---

class TestGetPartMPN:
    """Test get_part tool with mpn parameter."""

    @pytest.mark.asyncio
    async def test_get_part_requires_lcsc_or_mpn(self):
        from pcbparts_mcp.server import jlc_get_part
        result = await jlc_get_part()
        assert "error" in result
        assert "Must provide" in result["error"]

    @pytest.mark.asyncio
    async def test_get_part_mpn_too_long(self):
        from pcbparts_mcp.server import jlc_get_part
        result = await jlc_get_part(mpn="x" * 101)
        assert "error" in result
        assert "too long" in result["error"]

    @pytest.mark.asyncio
    async def test_get_part_mpn_not_found(self):
        from pcbparts_mcp.server import jlc_get_part
        result = await jlc_get_part(mpn="TOTALLYFAKE12345XYZ")
        assert "error" in result
        assert result["results"] == []
        assert result["mpn"] == "TOTALLYFAKE12345XYZ"

    @pytest.mark.asyncio
    async def test_get_part_mpn_found(self):
        """MPN lookup should find parts from local DB."""
        from pcbparts_mcp.server import jlc_get_part
        result = await jlc_get_part(mpn="AO3400A")
        if result.get("total", 0) > 0:
            assert result["mpn"] == "AO3400A"
            assert len(result["results"]) > 0
            assert result["results"][0]["model"] == "AO3400A"

    @pytest.mark.asyncio
    async def test_get_part_lcsc_takes_precedence(self):
        """When both lcsc and mpn are provided, lcsc should be used."""
        from pcbparts_mcp.server import jlc_get_part
        import pcbparts_mcp.server as srv
        # Mock the client to track which path is taken
        original = srv._client
        mock_client = MagicMock()
        mock_client.get_part = AsyncMock(return_value={"lcsc": "C1525", "model": "test"})
        srv._client = mock_client
        try:
            result = await jlc_get_part(lcsc="C1525", mpn="AO3400A")
            # Should call client.get_part (LCSC path), not DB lookup
            mock_client.get_part.assert_called_once_with("C1525")
        finally:
            srv._client = original
