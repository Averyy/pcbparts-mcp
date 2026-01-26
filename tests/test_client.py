"""Tests for JLCPCB API client."""

import pytest
from jlcpcb_mcp.client import JLCPCBClient


class TestClient:
    """Test JLCPCB API client."""

    @pytest.fixture
    def client(self):
        client = JLCPCBClient()
        # Pre-populate category cache for unit tests
        client.set_categories([
            {
                "id": 1,
                "name": "Resistors",
                "count": 1000000,
                "subcategories": [
                    {"id": 2980, "name": "Chip Resistor - Surface Mount", "count": 500000},
                ],
            },
            {
                "id": 5,
                "name": "Transistors/Thyristors",
                "count": 110000,
                "subcategories": [],
            },
            {
                "id": 11,
                "name": "Circuit Protection",
                "count": 159000,
                "subcategories": [],
            },
            {
                "id": 16,
                "name": "Optoelectronics",
                "count": 83000,
                "subcategories": [],
            },
            {
                "id": 29,
                "name": "Data Acquisition",
                "count": 25000,
                "subcategories": [],
            },
        ])
        return client

    def test_build_search_params_keyword(self, client):
        params = client._build_search_params(query="ESP32")
        assert params["keyword"] == "ESP32"
        assert params["currentPage"] == 1
        assert params["pageSize"] == 20

    def test_build_search_params_category(self, client):
        params = client._build_search_params(category_id=1)
        assert params["firstSortId"] == 1
        assert params["firstSortName"] == "Resistors"
        assert params["searchType"] == 3

    def test_build_search_params_subcategory(self, client):
        params = client._build_search_params(subcategory_id=2980)
        assert params["firstSortId"] == 1
        assert params["firstSortName"] == "Resistors"
        assert params["secondSortId"] == 2980
        assert params["secondSortName"] == "Chip Resistor - Surface Mount"
        assert params["searchType"] == 3

    def test_build_search_params_stock(self, client):
        params = client._build_search_params(min_stock=1000)
        assert params["startStockNumber"] == 1000

    def test_build_search_params_library_type_basic(self, client):
        params = client._build_search_params(library_type="basic")
        assert params["componentLibraryType"] == "base"

    def test_build_search_params_library_type_extended(self, client):
        params = client._build_search_params(library_type="extended")
        assert params["componentLibraryType"] == "expand"

    def test_build_search_params_library_type_preferred(self, client):
        params = client._build_search_params(library_type="preferred")
        assert params["preferredComponentFlag"] is True

    def test_build_search_params_library_type_no_fee(self, client):
        """no_fee combines basic + preferred in a single API call."""
        params = client._build_search_params(library_type="no_fee")
        assert params["componentLibraryType"] == "base"
        assert params["preferredComponentFlag"] is True

    def test_build_search_params_sort_by_quantity(self, client):
        """Sort by quantity (highest first)."""
        params = client._build_search_params(sort_by="quantity")
        assert params["sortMode"] == "STOCK_SORT"
        assert params["sortASC"] == "DESC"

    def test_build_search_params_sort_by_price(self, client):
        """Sort by price (cheapest first)."""
        params = client._build_search_params(sort_by="price")
        assert params["sortMode"] == "PRICE_SORT"
        assert params["sortASC"] == "ASC"

    def test_build_search_params_sort_default(self, client):
        """No sorting params when sort_by is None (default relevance)."""
        params = client._build_search_params(query="ESP32")
        assert "sortMode" not in params
        assert "sortASC" not in params

    def test_build_search_params_sort_invalid(self, client):
        """Invalid sort_by value is ignored."""
        params = client._build_search_params(sort_by="invalid")
        assert "sortMode" not in params
        assert "sortASC" not in params

    def test_build_search_params_packages_multi(self, client):
        """Multiple packages use componentSpecificationList (OR filter)."""
        params = client._build_search_params(packages=["0402", "0603", "0805"])
        assert params["componentSpecificationList"] == ["0402", "0603", "0805"]
        assert "componentSpecification" not in params

    def test_build_search_params_packages_empty(self, client):
        """Empty packages list is ignored."""
        params = client._build_search_params(packages=[])
        assert "componentSpecificationList" not in params
        assert "componentSpecification" not in params

    def test_build_search_params_package_single_over_multi(self, client):
        """Multi-select packages takes precedence over single package."""
        params = client._build_search_params(package="0402", packages=["0603", "0805"])
        assert params["componentSpecificationList"] == ["0603", "0805"]
        assert "componentSpecification" not in params

    def test_build_search_params_manufacturers_multi(self, client):
        """Multiple manufacturers use componentBrandList (OR filter) with alias resolution."""
        params = client._build_search_params(manufacturers=["TI", "STM"])
        # Aliases are resolved: TI -> Texas Instruments, STM -> STMicroelectronics
        assert params["componentBrandList"] == ["Texas Instruments", "STMicroelectronics"]
        assert "componentBrand" not in params

    def test_build_search_params_manufacturers_empty(self, client):
        """Empty manufacturers list is ignored."""
        params = client._build_search_params(manufacturers=[])
        assert "componentBrandList" not in params
        assert "componentBrand" not in params

    def test_build_search_params_manufacturer_single_over_multi(self, client):
        """Multi-select manufacturers takes precedence over single manufacturer."""
        params = client._build_search_params(manufacturer="TI", manufacturers=["STM", "NXP"])
        # Aliases resolved: STM -> STMicroelectronics, NXP -> NXP Semicon
        assert params["componentBrandList"] == ["STMicroelectronics", "NXP Semicon"]
        assert "componentBrand" not in params

    def test_manufacturer_alias_resolution(self, client):
        """Manufacturer aliases are resolved to full names."""
        # Single manufacturer alias
        params = client._build_search_params(manufacturer="ti")
        assert params["componentBrand"] == "Texas Instruments"

        # Unknown manufacturer passes through unchanged
        params = client._build_search_params(manufacturer="Unknown Corp")
        assert params["componentBrand"] == "Unknown Corp"

    def test_transform_part_slim(self, client):
        # Note: API returns firstSortName as subcategory, secondSortName as category
        item = {
            "componentCode": "C82899",
            "componentModelEn": "ESP32-WROOM-32-N4",
            "componentBrandEn": "Espressif Systems",
            "componentSpecificationEn": "SMD,25.5x18mm",
            "stockCount": 11117,
            "componentLibraryType": "expand",
            "preferredComponentFlag": False,
            "firstSortName": "IoT Modules",  # subcategory
            "secondSortName": "WiFi Modules",  # category
            "componentPrices": [
                {"startNumber": 1, "endNumber": 9, "productPrice": 4.2016},
                {"startNumber": 10, "endNumber": 29, "productPrice": 3.7052},
            ],
            "attributes": [
                {"attribute_name_en": "Voltage", "attribute_value_name": "3.3V"},
                {"attribute_name_en": "Frequency", "attribute_value_name": "2.4GHz"},
            ],
        }
        result = client._transform_part(item, slim=True)
        assert result["lcsc"] == "C82899"
        assert result["model"] == "ESP32-WROOM-32-N4"
        assert result["manufacturer"] == "Espressif Systems"
        assert result["stock"] == 11117
        assert result["library_type"] == "extended"
        assert result["price"] == 4.2016
        assert result["price_10"] == 3.7052  # Volume pricing
        assert result["category"] == "WiFi Modules"
        assert result["subcategory"] == "IoT Modules"  # Now included in slim
        assert result["key_specs"] == {"Voltage": "3.3V", "Frequency": "2.4GHz"}
        assert "datasheet" not in result
        assert "attributes" not in result  # Full list not in slim

    def test_transform_part_slim_single_price_tier(self, client):
        """Parts with only one price tier should have price_10=None."""
        item = {
            "componentCode": "C12345",
            "componentModelEn": "TEST",
            "componentBrandEn": "Test",
            "componentSpecificationEn": "0402",
            "stockCount": 100,
            "componentLibraryType": "base",
            "preferredComponentFlag": False,
            "firstSortName": "Test Sub",
            "secondSortName": "Test Cat",
            "componentPrices": [{"startNumber": 1, "endNumber": 9, "productPrice": 0.01}],
        }
        result = client._transform_part(item, slim=True)
        assert result["price_10"] is None  # Only one price tier

    def test_transform_part_no_prices(self, client):
        """Parts with no price tiers should have price=None and price_10=None."""
        item = {
            "componentCode": "C12345",
            "componentModelEn": "TEST",
            "componentBrandEn": "Test",
            "componentSpecificationEn": "0402",
            "stockCount": 100,
            "componentLibraryType": "base",
            "preferredComponentFlag": False,
            "firstSortName": "Test Sub",
            "secondSortName": "Test Cat",
            "componentPrices": [],  # Empty price list
        }
        result = client._transform_part(item, slim=True)
        assert result["price"] is None
        assert result["price_10"] is None

    def test_transform_part_no_attributes(self, client):
        """Parts with no attributes should have key_specs as empty dict."""
        item = {
            "componentCode": "C12345",
            "componentModelEn": "TEST",
            "componentBrandEn": "Test",
            "componentSpecificationEn": "0402",
            "stockCount": 100,
            "componentLibraryType": "base",
            "preferredComponentFlag": False,
            "firstSortName": "Test Sub",
            "secondSortName": "Test Cat",
            "componentPrices": [{"startNumber": 1, "endNumber": 9, "productPrice": 0.01}],
            "attributes": [],  # Empty attributes
        }
        result = client._transform_part(item, slim=True)
        assert result["key_specs"] == {}  # Should be empty dict, not missing

    def test_transform_part_missing_attributes_field(self, client):
        """Parts without attributes field should have key_specs as empty dict."""
        item = {
            "componentCode": "C12345",
            "componentModelEn": "TEST",
            "componentBrandEn": "Test",
            "componentSpecificationEn": "0402",
            "stockCount": 100,
            "componentLibraryType": "base",
            "preferredComponentFlag": False,
            "firstSortName": "Test Sub",
            "secondSortName": "Test Cat",
            "componentPrices": [{"startNumber": 1, "endNumber": 9, "productPrice": 0.01}],
            # No "attributes" field at all
        }
        result = client._transform_part(item, slim=True)
        assert result["key_specs"] == {}  # Should be empty dict, not missing

    def test_transform_part_full(self, client):
        # Note: API returns firstSortName as subcategory, secondSortName as category
        item = {
            "componentCode": "C82899",
            "componentModelEn": "ESP32-WROOM-32-N4",
            "componentBrandEn": "Espressif Systems",
            "componentSpecificationEn": "SMD,25.5x18mm",
            "stockCount": 11117,
            "componentLibraryType": "base",
            "preferredComponentFlag": True,
            "firstSortName": "IoT Modules",  # subcategory
            "secondSortName": "WiFi Modules",  # category
            "describe": "WiFi module description",
            "minPurchaseNum": 1,
            "encapsulationNumber": 550,
            "dataManualUrl": "https://example.com/datasheet.pdf",
            "lcscGoodsUrl": "https://lcsc.com/product/C82899",
            "componentPrices": [
                {"startNumber": 1, "endNumber": 9, "productPrice": 4.2016},
                {"startNumber": 10, "endNumber": 29, "productPrice": 3.7052},
            ],
            "attributes": [
                {"attribute_name_en": "Voltage", "attribute_value_name": "3.3V"},
            ],
        }
        result = client._transform_part(item, slim=False)
        assert result["lcsc"] == "C82899"
        assert result["library_type"] == "basic"
        assert result["price"] == 4.2016
        assert result["price_10"] == 3.7052
        assert result["category"] == "WiFi Modules"
        assert result["subcategory"] == "IoT Modules"
        assert result["key_specs"] == {"Voltage": "3.3V"}  # Also in full mode
        assert result["datasheet"] == "https://example.com/datasheet.pdf"
        assert len(result["prices"]) == 2
        assert result["prices"][0]["qty"] == "1+"
        assert len(result["attributes"]) == 1
        assert result["attributes"][0]["name"] == "Voltage"

    # Tests for abbreviation matching

    def test_match_category_abbreviation_led(self, client):
        """LED abbreviation should match Optoelectronics category."""
        assert client.match_category_by_name("led") == 16
        assert client.match_category_by_name("LED") == 16
        assert client.match_category_by_name("Led") == 16

    def test_match_category_abbreviation_led_plural(self, client):
        """LEDs (plural) should also match Optoelectronics."""
        assert client.match_category_by_name("leds") == 16
        assert client.match_category_by_name("LEDs") == 16

    def test_match_category_abbreviation_esd(self, client):
        """ESD abbreviation should match Circuit Protection category."""
        assert client.match_category_by_name("esd") == 11
        assert client.match_category_by_name("ESD") == 11

    def test_match_category_abbreviation_adc(self, client):
        """ADC abbreviation should match Data Acquisition category."""
        assert client.match_category_by_name("adc") == 29
        assert client.match_category_by_name("ADC") == 29
        assert client.match_category_by_name("adcs") == 29

    def test_match_category_abbreviation_transistors(self, client):
        """BJT and FET abbreviations should match Transistors category."""
        assert client.match_category_by_name("bjt") == 5
        assert client.match_category_by_name("BJT") == 5
        assert client.match_category_by_name("bjts") == 5
        assert client.match_category_by_name("fet") == 5
        assert client.match_category_by_name("FET") == 5
        assert client.match_category_by_name("fets") == 5

    def test_match_category_by_name_exact(self, client):
        """Exact category name match."""
        assert client.match_category_by_name("resistors") == 1
        assert client.match_category_by_name("Resistors") == 1

    def test_match_category_by_name_singular(self, client):
        """Singular form should match plural category."""
        assert client.match_category_by_name("resistor") == 1

    def test_match_category_by_name_no_match(self, client):
        """Non-matching query should return None."""
        assert client.match_category_by_name("xyz123") is None
        assert client.match_category_by_name("") is None
        assert client.match_category_by_name(None) is None

    def test_resolve_abbreviation_requires_categories(self, client):
        """Abbreviation resolution requires categories to be loaded."""
        empty_client = JLCPCBClient()
        # No categories set, should return None
        assert empty_client.match_category_by_name("led") is None

    # Tests for subcategory name lookup

    def test_get_subcategory_id_by_name(self, client):
        """Subcategory ID lookup by name should work."""
        # Client fixture has "Chip Resistor - Surface Mount" with id 2980
        assert client.get_subcategory_id_by_name("Chip Resistor - Surface Mount") == 2980

    def test_get_subcategory_id_by_name_not_found(self, client):
        """Non-existent subcategory name should return None."""
        assert client.get_subcategory_id_by_name("NonExistent Subcategory") is None

    def test_get_subcategory_id_by_name_empty_cache(self):
        """Subcategory lookup with empty cache should return None."""
        empty_client = JLCPCBClient()
        assert empty_client.get_subcategory_id_by_name("Anything") is None

    # Tests for LCSC code validation

    @pytest.mark.asyncio
    async def test_get_part_invalid_lcsc_format(self, client):
        """Invalid LCSC codes should return None without making API calls."""
        # Missing C prefix
        assert await client.get_part("12345") is None
        # Non-numeric suffix
        assert await client.get_part("CABC123") is None
        # Empty string
        assert await client.get_part("") is None
        # Just C
        assert await client.get_part("C") is None
        # Whitespace
        assert await client.get_part("   ") is None


@pytest.mark.asyncio
class TestClientIntegration:
    """Integration tests that hit the real JLCPCB API."""

    @pytest.fixture
    async def client(self):
        client = JLCPCBClient()
        yield client
        await client.close()

    async def test_search_keyword(self, client):
        """Test keyword search."""
        result = await client.search(query="ESP32", limit=5)
        assert "results" in result
        assert len(result["results"]) > 0
        assert result["results"][0]["lcsc"].startswith("C")

    async def test_search_pagination_fields(self, client):
        """Test pagination fields in search results."""
        result = await client.search(query="resistor", limit=10)
        # Check all pagination fields exist
        assert "page" in result
        assert "per_page" in result
        assert "total" in result
        assert "total_pages" in result
        assert "has_more" in result
        # Verify total_pages calculation
        expected_pages = (result["total"] + 10 - 1) // 10  # ceil division
        assert result["total_pages"] == expected_pages
        assert result["per_page"] == 10
        assert result["page"] == 1

    async def test_search_results_have_key_specs(self, client):
        """Test that search results include key_specs field."""
        result = await client.search(query="10uF capacitor", limit=5)
        assert len(result["results"]) > 0
        # All results should have key_specs (even if empty dict)
        for part in result["results"]:
            assert "key_specs" in part, f"Part {part['lcsc']} missing key_specs"
            assert isinstance(part["key_specs"], dict)

    async def test_search_category(self, client):
        """Test category filtering."""
        result = await client.search(category_id=1, min_stock=0, limit=5)
        assert result["total"] > 100000  # Resistors should have >100K parts (when min_stock=0)
        assert all(r["category"] == "Resistors" for r in result["results"])

    async def test_search_stock_filter(self, client):
        """Test stock filtering."""
        result = await client.search(category_id=1, min_stock=10000, limit=5)
        assert all(r["stock"] >= 10000 for r in result["results"])

    async def test_search_library_type_no_fee(self, client):
        """Test no_fee library type returns only basic/preferred parts."""
        result = await client.search(query="resistor", library_type="no_fee", limit=10)
        assert len(result["results"]) > 0
        # no_fee should only return basic or preferred parts (no extended)
        for part in result["results"]:
            assert part["library_type"] in ("basic", "preferred") or part["preferred"] is True, (
                f"Part {part['lcsc']} has library_type={part['library_type']}, preferred={part['preferred']}"
            )

    async def test_get_part(self, client):
        """Test getting part details."""
        result = await client.get_part("C82899")
        assert result is not None
        assert result["lcsc"] == "C82899"
        assert "prices" in result
        assert "datasheet" in result

    async def test_fetch_categories(self, client):
        """Test fetching live category data from API."""
        categories = await client.fetch_categories()

        # Minimum thresholds (90% of expected ~51 categories, ~756 subcategories)
        assert len(categories) >= 46, (
            f"Expected at least 46 categories, got {len(categories)}. "
            "JLCPCB API may have changed or is returning incomplete data."
        )

        # Check structure of a category
        cat = categories[0]
        assert "id" in cat
        assert "name" in cat
        assert "count" in cat
        assert "subcategories" in cat

        # Should have subcategories - minimum threshold (90% of expected)
        total_subs = sum(len(c["subcategories"]) for c in categories)
        assert total_subs >= 680, (
            f"Expected at least 680 subcategories, got {total_subs}. "
            "JLCPCB API may have changed or is returning incomplete data."
        )

    async def test_search_sort_by_quantity(self, client):
        """Test sorting by quantity (highest first)."""
        result = await client.search(query="ESP32", sort_by="quantity", limit=10)
        stocks = [r["stock"] for r in result["results"] if r["stock"] is not None]
        # Check descending order (each value >= next)
        for i in range(len(stocks) - 1):
            assert stocks[i] >= stocks[i + 1], "Results should be sorted by quantity descending"

    async def test_search_sort_by_price(self, client):
        """Test sorting by price (cheapest first)."""
        result = await client.search(query="ESP32", sort_by="price", limit=10)
        prices = [r["price"] for r in result["results"] if r["price"] is not None]
        # Check ascending order (each value <= next)
        for i in range(len(prices) - 1):
            assert prices[i] <= prices[i + 1], "Results should be sorted by price ascending"

    async def test_search_packages_multi(self, client):
        """Test multi-select package filter (OR logic)."""
        # Search capacitors with multiple package sizes
        result = await client.search(
            category_id=2,  # Capacitors
            packages=["0402", "0603", "0805"],
            limit=20,
        )
        # Collect packages from results
        result_packages = {r["package"] for r in result["results"]}
        # Should include at least some of the requested packages
        assert result_packages & {"0402", "0603", "0805"}, (
            f"Expected some of ['0402', '0603', '0805'], got {result_packages}"
        )

    async def test_search_manufacturers_multi(self, client):
        """Test multi-select manufacturer filter (OR logic)."""
        result = await client.search(
            query="microcontroller",
            manufacturers=["STMicroelectronics", "Microchip Tech"],
            limit=20,
        )
        # Collect manufacturers from results
        result_mfrs = {r["manufacturer"] for r in result["results"]}
        # Should include at least one of the requested manufacturers
        assert result_mfrs & {"STMicroelectronics", "Microchip Tech"}, (
            f"Expected some of ['STMicroelectronics', 'Microchip Tech'], got {result_mfrs}"
        )

    async def test_search_combined_filters(self, client):
        """Test combining keyword, category, multi-package, and stock filters."""
        result = await client.search(
            query="100nF",  # Attribute value as keyword
            category_id=2,  # Capacitors
            packages=["0402", "0603"],
            min_stock=1000,
            limit=10,
        )
        assert len(result["results"]) > 0, "Should find 100nF capacitors"
        # Verify all results meet stock requirement
        for part in result["results"]:
            assert part["stock"] >= 1000, f"Part {part['lcsc']} has stock {part['stock']} < 1000"

    async def test_search_sorted_with_multi_filters(self, client):
        """Test sorting combined with multi-select filters."""
        result = await client.search(
            category_id=2,  # Capacitors
            packages=["0402", "0603"],
            sort_by="price",
            min_stock=100,
            limit=10,
        )
        assert len(result["results"]) > 0, "Should find capacitors"
        # Verify price sorting (ascending)
        prices = [r["price"] for r in result["results"] if r["price"] is not None]
        for i in range(len(prices) - 1):
            assert prices[i] <= prices[i + 1], "Results should be sorted by price ascending"

    async def test_get_part_invalid_format_returns_none(self, client):
        """Invalid LCSC codes should return None without API errors."""
        result = await client.get_part("INVALID")
        assert result is None

    async def test_get_part_lowercase_works(self, client):
        """Lowercase LCSC codes should work (normalized to uppercase)."""
        result = await client.get_part("c82899")  # lowercase
        assert result is not None
        assert result["lcsc"] == "C82899"  # normalized to uppercase

    async def test_find_alternatives(self, client):
        """Test find_alternatives method on client."""
        # Fetch categories first (required for subcategory lookup)
        categories = await client.fetch_categories()
        client.set_categories(categories)

        # Find alternatives for a common 10k resistor
        result = await client.find_alternatives("C25531", min_stock=100, limit=5)

        # Should not have error
        assert "error" not in result, f"Unexpected error: {result.get('error')}"

        # Check original part info
        assert result["original"]["lcsc"] == "C25531"
        assert result["original"]["subcategory"] is not None

        # Check alternatives
        assert len(result["alternatives"]) > 0, "Should find alternatives"
        # Original should not be in alternatives
        for alt in result["alternatives"]:
            assert alt["lcsc"] != "C25531", "Original should not be in alternatives"

        # Check search criteria in response - new format has compatibility info
        assert "search_criteria" in result
        assert "subcategory" in result["search_criteria"]

    async def test_find_alternatives_invalid_lcsc(self, client):
        """Test find_alternatives with invalid LCSC code returns error dict."""
        result = await client.find_alternatives("INVALID123")
        assert "error" in result
        assert "not found" in result["error"].lower()

    async def test_find_alternatives_same_package(self, client):
        """Test find_alternatives with same_package filter."""
        # Fetch categories first
        categories = await client.fetch_categories()
        client.set_categories(categories)

        # Find alternatives for a common capacitor with same package
        result = await client.find_alternatives("C14663", min_stock=100, same_package=True, limit=5)

        assert "error" not in result
        original_package = result["original"]["package"]

        # All alternatives should have the same package
        for alt in result["alternatives"]:
            assert alt["package"] == original_package, f"Expected {original_package}, got {alt['package']}"

    async def test_check_easyeda_footprint_valid_part(self, client):
        """Test EasyEDA footprint check for a known part."""
        # C1525 is a common capacitor that should have a footprint
        result = await client.check_easyeda_footprint("C1525")
        assert "has_easyeda_footprint" in result
        assert result["has_easyeda_footprint"] in (True, False, None)
        assert "easyeda_symbol_uuid" in result
        assert "easyeda_footprint_uuid" in result

    async def test_check_easyeda_footprint_invalid_format(self, client):
        """Test EasyEDA footprint check with invalid LCSC format returns unknown."""
        # Invalid format should return unknown (None) without crashing
        result = await client.check_easyeda_footprint("INVALID")
        assert result["has_easyeda_footprint"] is None

        result = await client.check_easyeda_footprint("")
        assert result["has_easyeda_footprint"] is None

        result = await client.check_easyeda_footprint("123")
        assert result["has_easyeda_footprint"] is None

    async def test_check_easyeda_footprint_caching(self, client):
        """Test that EasyEDA results are cached."""
        # First call
        result1 = await client.check_easyeda_footprint("C1525")

        # Second call should be cached (no API hit)
        result2 = await client.check_easyeda_footprint("C1525")

        # Results should be identical
        assert result1 == result2

        # Check cache contains the entry
        assert "C1525" in client._easyeda_cache

    async def test_find_alternatives_with_easyeda_filter(self, client):
        """Test find_alternatives with has_easyeda_footprint filter."""
        categories = await client.fetch_categories()
        client.set_categories(categories)

        # Find alternatives with EasyEDA footprints only
        result = await client.find_alternatives(
            "C25531",  # Common 10k resistor
            min_stock=100,
            has_easyeda_footprint=True,
            limit=5,
        )

        assert "error" not in result

        # All alternatives should have EasyEDA info included
        for alt in result["alternatives"]:
            assert "has_easyeda_footprint" in alt
            # When filtering for True, all should have footprints
            assert alt["has_easyeda_footprint"] is True

    async def test_find_alternatives_with_library_type_filter(self, client):
        """Test find_alternatives with library_type filter."""
        categories = await client.fetch_categories()
        client.set_categories(categories)

        # Find basic library alternatives only (no assembly fee)
        result = await client.find_alternatives(
            "C1525",  # Basic capacitor
            min_stock=100,
            library_type="basic",
            limit=5,
        )

        assert "error" not in result
        assert "search_criteria" in result

        # All alternatives should be basic library type
        for alt in result["alternatives"]:
            assert alt["library_type"] == "basic"

    async def test_find_alternatives_with_no_fee_filter(self, client):
        """Test find_alternatives with library_type='no_fee' (basic + preferred)."""
        categories = await client.fetch_categories()
        client.set_categories(categories)

        # Find no-fee alternatives (basic or preferred)
        result = await client.find_alternatives(
            "C1525",  # Basic capacitor
            min_stock=100,
            library_type="no_fee",
            limit=5,
        )

        assert "error" not in result
        assert "search_criteria" in result

        # All alternatives should be basic or preferred (no $3 fee)
        for alt in result["alternatives"]:
            assert alt["library_type"] in ("basic", "preferred") or alt.get("preferred")

    async def test_find_alternatives_includes_library_type_in_original(self, client):
        """Test find_alternatives includes library_type in original part info."""
        categories = await client.fetch_categories()
        client.set_categories(categories)

        result = await client.find_alternatives("C1525", limit=3)

        assert "error" not in result
        assert "original" in result
        assert "library_type" in result["original"]
        assert result["original"]["library_type"] in ("basic", "extended")

    async def test_get_part_includes_easyeda_info(self, client):
        """Test that get_part includes EasyEDA footprint info."""
        result = await client.get_part("C1525")
        assert result is not None
        assert "has_easyeda_footprint" in result
        assert "easyeda_symbol_uuid" in result
        assert "easyeda_footprint_uuid" in result
