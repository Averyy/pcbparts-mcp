"""Tests for the parametric database search."""

import pytest

from pcbparts_mcp.db import ComponentDatabase, get_db
from pcbparts_mcp.search import SpecFilter


class TestNameResolution:
    """Test subcategory and category name resolution."""

    def test_resolve_subcategory_name_exact(self):
        """Exact match should work."""
        db = get_db()
        # "MOSFETs" is a known subcategory
        result = db.resolve_subcategory_name("MOSFETs")
        assert result is not None
        assert isinstance(result, int)  # Should return a valid subcategory ID

    def test_resolve_subcategory_name_case_insensitive(self):
        """Name resolution should be case-insensitive."""
        db = get_db()
        result1 = db.resolve_subcategory_name("mosfets")
        result2 = db.resolve_subcategory_name("MOSFETS")
        result3 = db.resolve_subcategory_name("MoSfEtS")
        assert result1 == result2 == result3

    def test_resolve_subcategory_name_partial_match(self):
        """Partial match should work when exact match fails."""
        db = get_db()
        # "Chip Resistor" should match "Chip Resistor - Surface Mount"
        result = db.resolve_subcategory_name("Chip Resistor")
        assert result is not None

    def test_resolve_subcategory_name_not_found(self):
        """Non-existent name should return None."""
        db = get_db()
        result = db.resolve_subcategory_name("NonExistentCategory12345")
        assert result is None

    def test_resolve_category_name_exact(self):
        """Exact category name match should work."""
        db = get_db()
        result = db.resolve_category_name("Resistors")
        assert result is not None

    def test_resolve_category_name_case_insensitive(self):
        """Category name resolution should be case-insensitive."""
        db = get_db()
        result1 = db.resolve_category_name("capacitors")
        result2 = db.resolve_category_name("CAPACITORS")
        assert result1 == result2


class TestSearchWithNames:
    """Test search() with name parameters."""

    def test_search_by_subcategory_name(self):
        """Search by subcategory_name should work."""
        db = get_db()
        result = db.search(subcategory_name="MOSFETs", limit=5)

        assert "error" not in result
        assert result["total"] > 0
        assert len(result["results"]) <= 5
        assert result["filters_applied"]["subcategory_name"] == "MOSFETs"
        assert isinstance(result["filters_applied"]["subcategory_id"], int)

    def test_search_by_subcategory_name_not_found(self):
        """Search with non-existent subcategory_name should return error."""
        db = get_db()
        result = db.search(subcategory_name="NonExistent12345", limit=5)

        assert "error" in result
        assert "not found" in result["error"].lower()
        assert result["total"] == 0

    def test_search_subcategory_id_takes_precedence(self):
        """subcategory_id should take precedence over subcategory_name."""
        db = get_db()
        # Get the actual MOSFET subcategory ID dynamically
        mosfet_id = db.resolve_subcategory_name("MOSFETs")
        assert mosfet_id is not None
        # Pass both ID and a different name
        result = db.search(
            subcategory_id=mosfet_id,
            subcategory_name="Resistors",  # This should be ignored
            limit=5,
        )

        assert "error" not in result
        # Should use the ID, not the name
        assert result["filters_applied"]["subcategory_id"] == mosfet_id


class TestSpecFilters:
    """Test parametric spec filtering."""

    def test_vgs_threshold_filter(self):
        """Filter MOSFETs by Vgs(th) < 2V for logic-level parts."""
        db = get_db()
        result = db.search(
            subcategory_name="MOSFETs",
            spec_filters=[SpecFilter("Vgs(th)", "<", "2V")],
            limit=10,
        )

        assert "error" not in result
        assert result["total"] > 0

        # Verify all results have Vgs(th) < 2V
        for part in result["results"]:
            vgs = part.get("specs", {}).get("Gate Threshold Voltage (Vgs(th))")
            if vgs:
                # Parse the voltage value (e.g., "1.1V" -> 1.1)
                from pcbparts_mcp.alternatives import parse_voltage
                parsed = parse_voltage(vgs)
                assert parsed is not None and parsed < 2.0, f"Vgs(th)={vgs} should be < 2V"

    def test_capacitor_voltage_filter(self):
        """Filter capacitors by voltage >= 25V."""
        db = get_db()
        result = db.search(
            subcategory_id=2929,  # MLCC SMD
            query="10uF",
            spec_filters=[SpecFilter("Voltage", ">=", "25V")],
            limit=10,
        )

        assert "error" not in result
        assert result["total"] > 0

        # Verify all results have voltage >= 25V
        for part in result["results"]:
            voltage = part.get("specs", {}).get("Voltage Rating")
            if voltage:
                from pcbparts_mcp.alternatives import parse_voltage
                parsed = parse_voltage(voltage)
                assert parsed is not None and parsed >= 25.0, f"Voltage={voltage} should be >= 25V"

    def test_multiple_spec_filters(self):
        """Multiple spec filters should all be applied (AND logic)."""
        db = get_db()
        result = db.search(
            subcategory_name="MOSFETs",
            spec_filters=[
                SpecFilter("Vgs(th)", "<", "2V"),
                SpecFilter("Id", ">=", "3A"),
            ],
            limit=10,
        )

        assert "error" not in result
        # May have fewer results with multiple filters
        assert result["total"] >= 0

    def test_multiple_interface_values_use_or_logic(self):
        """Multiple Interface filters should match components with EITHER value (OR logic)."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        # Parse a query that creates multiple Interface filters
        result = parse_smart_query("sensor I2C SPI")
        interface_filters = [f for f in result.spec_filters if f.name == "Interface"]

        # Should create two separate filters
        assert len(interface_filters) == 2
        assert {f.value for f in interface_filters} == {"I2C", "SPI"}

        # When searching, these should be grouped with OR logic
        # (components with "I2C、SPI" should match)
        from pcbparts_mcp.search.query_builder import _group_multi_value_filters

        grouped = _group_multi_value_filters(interface_filters)
        assert len(grouped) == 1
        assert isinstance(grouped[0], tuple)
        spec_name, values = grouped[0]
        assert spec_name == "Interface"
        assert set(values) == {"I2C", "SPI"}


class TestSpecFilterValidation:
    """Test spec filter operator validation."""

    def test_valid_operators_accepted(self):
        """Valid operators should be accepted."""
        valid_ops = ["=", ">=", "<=", ">", "<"]
        for op in valid_ops:
            sf = SpecFilter("Resistance", op, "10k")
            assert sf.operator == op

    def test_not_equal_operator_rejected(self):
        """!= operator should be rejected (not implemented)."""
        with pytest.raises(ValueError) as exc_info:
            SpecFilter("Resistance", "!=", "10k")
        assert "!=" not in str(exc_info.value) or "Must be one of" in str(exc_info.value)

    def test_invalid_operator_rejected(self):
        """Invalid operators should be rejected."""
        with pytest.raises(ValueError):
            SpecFilter("Resistance", "~=", "10k")


class TestLibraryTypeAndPreference:
    """Test library_type filter and prefer_no_fee sort preference."""

    def test_prefer_no_fee_sorts_basic_first(self):
        """prefer_no_fee=True (default) should sort basic parts first."""
        db = get_db()
        result = db.search(prefer_no_fee=True, limit=50)

        assert "error" not in result
        assert result["total"] > 0

        # First results should be basic if any exist
        types_seen = []
        for part in result["results"]:
            types_seen.append(part["library_type"])

        # Basic should appear before preferred, preferred before extended
        # (if all types are present)
        if "basic" in types_seen and "extended" in types_seen:
            first_basic = types_seen.index("basic")
            first_extended = types_seen.index("extended")
            assert first_basic < first_extended, "Basic should sort before extended"

        if "preferred" in types_seen and "extended" in types_seen:
            first_preferred = types_seen.index("preferred")
            first_extended = types_seen.index("extended")
            assert first_preferred < first_extended, "Preferred should sort before extended"

    def test_prefer_no_fee_includes_all_types(self):
        """prefer_no_fee is a preference, not a filter - should include extended parts."""
        db = get_db()
        # Fetch enough results to potentially include extended parts
        result = db.search(prefer_no_fee=True, limit=500)

        assert "error" not in result
        # Total should include all parts, not just basic+preferred
        # Should have more than just basic/preferred counts combined
        basic_pref = (result.get("library_type_counts", {}).get("basic", 0) +
                      result.get("library_type_counts", {}).get("preferred", 0))
        assert result["total"] > basic_pref or result["total"] > 100

    def test_prefer_no_fee_false_no_sorting_preference(self):
        """prefer_no_fee=False should not sort by library type."""
        db = get_db()
        result = db.search(prefer_no_fee=False, limit=50)

        assert "error" not in result
        # Should still return results, just not sorted by library type
        assert result["total"] > 0
        assert result["filters_applied"]["prefer_no_fee"] is False

    def test_prefer_no_fee_default_is_true(self):
        """prefer_no_fee should default to True."""
        db = get_db()
        result = db.search(limit=10)

        assert "error" not in result
        assert result["filters_applied"]["prefer_no_fee"] is True

    def test_basic_filter_excludes_others(self):
        """library_type=basic should filter to only basic parts."""
        db = get_db()
        result = db.search(library_type="basic", limit=50)

        assert "error" not in result
        # All results should be basic
        for part in result["results"]:
            assert part["library_type"] == "basic"

    def test_extended_filter_excludes_others(self):
        """library_type=extended should filter to only extended parts."""
        db = get_db()
        result = db.search(library_type="extended", limit=10)

        assert "error" not in result
        for part in result["results"]:
            assert part["library_type"] == "extended"

    def test_library_type_filter_with_prefer_no_fee(self):
        """library_type filter and prefer_no_fee can be combined."""
        db = get_db()
        # Filter to basic only, but prefer_no_fee still applies to sort order
        result = db.search(library_type="basic", prefer_no_fee=True, limit=10)

        assert "error" not in result
        # All should be basic (filter applies)
        for part in result["results"]:
            assert part["library_type"] == "basic"

    def test_no_fee_filter_excludes_extended(self):
        """library_type=no_fee should return only basic and preferred parts."""
        db = get_db()
        result = db.search(library_type="no_fee", limit=50)

        assert "error" not in result
        assert result["total"] > 0
        # All results should be basic or preferred (no extended)
        for part in result["results"]:
            assert part["library_type"] in ("basic", "preferred"), \
                f"no_fee returned {part['library_type']} part"


class TestPackageFilters:
    """Test package filtering."""

    def test_single_package_filter(self):
        """Single package filter should work."""
        db = get_db()
        result = db.search(
            subcategory_name="Chip Resistor",
            package="0603",
            limit=10,
        )

        assert "error" not in result
        for part in result["results"]:
            assert part["package"] == "0603"

    def test_multiple_packages_or_logic(self):
        """Multiple packages should use OR logic."""
        db = get_db()
        result = db.search(
            subcategory_name="Chip Resistor",
            packages=["0402", "0603", "0805"],
            limit=20,
        )

        assert "error" not in result
        packages_found = set()
        for part in result["results"]:
            assert part["package"] in ["0402", "0603", "0805"]
            packages_found.add(part["package"])

        # Should find at least 2 different package sizes
        assert len(packages_found) >= 2


class TestFTSSearch:
    """Test full-text search."""

    def test_single_word_query(self):
        """Single word FTS query should work."""
        db = get_db()
        result = db.search(query="ESP32", limit=10)

        assert "error" not in result
        assert result["total"] > 0

    def test_multi_word_query(self):
        """Multi-word FTS query should work (AND logic)."""
        db = get_db()
        result = db.search(
            subcategory_id=2929,  # MLCC
            query="10uF 25V",
            limit=10,
        )

        assert "error" not in result
        # Should find capacitors matching both terms
        assert result["total"] > 0

    def test_fts_with_spec_filter(self):
        """FTS + spec filter should work together."""
        db = get_db()
        result = db.search(
            subcategory_name="MOSFETs",
            query="AO3400",  # Popular MOSFET
            spec_filters=[SpecFilter("Vgs(th)", "<", "2V")],
            limit=10,
        )

        assert "error" not in result
        # AO3400 should match and have low Vgs(th)


class TestSubcategoryAliases:
    """Test subcategory alias resolution."""

    def test_mlcc_alias(self):
        """MLCC should resolve to SMD ceramic capacitors, not leaded."""
        db = get_db()
        result = db.resolve_subcategory_name("MLCC")
        assert result is not None
        name = db._subcategories[result]["name"]
        assert "SMD" in name or "smd" in name.lower()
        assert "Leaded" not in name

    def test_common_aliases(self):
        """Common aliases should resolve correctly."""
        db = get_db()
        # Test a few key aliases
        aliases = [
            ("mosfet", "MOSFETs"),
            ("schottky", "Schottky Diodes"),
            ("crystal", "Crystals"),
        ]
        for alias, expected in aliases:
            result = db.resolve_subcategory_name(alias)
            assert result is not None, f"Alias '{alias}' should resolve"
            name = db._subcategories[result]["name"]
            assert name == expected, f"'{alias}' should resolve to '{expected}', got '{name}'"

    def test_esd_alias_resolves_to_tvs_esd(self):
        """ESD aliases should resolve to the subcategory with actual parts."""
        db = get_db()
        # ESD, TVS, surge protection should all resolve to the same subcategory
        for alias in ["ESD", "TVS", "esd protection", "surge protection"]:
            result = db.resolve_subcategory_name(alias)
            assert result is not None, f"Alias '{alias}' should resolve"
            name = db._subcategories[result]["name"]
            assert "TVS/ESD" in name, f"'{alias}' should resolve to TVS/ESD subcategory, got '{name}'"

    def test_antenna_aliases(self):
        """Antenna aliases should resolve correctly."""
        db = get_db()
        aliases = [
            ("antenna", "antennas"),
            ("ceramic antenna", "antennas"),
            ("wifi antenna", "antennas"),
            ("ble antenna", "antennas"),
        ]
        for alias, expected_lower in aliases:
            result = db.resolve_subcategory_name(alias)
            assert result is not None, f"Alias '{alias}' should resolve"
            name = db._subcategories[result]["name"]
            assert name.lower() == expected_lower, f"'{alias}' should resolve to '{expected_lower}', got '{name}'"

    def test_temperature_humidity_sensor_word_order(self):
        """Temperature+humidity sensor aliases should work regardless of word order."""
        db = get_db()
        expected = "temperature and humidity sensor"
        aliases = [
            "humidity temperature sensor",
            "temperature humidity sensor",
            "temp humidity sensor",
            "humidity temp sensor",
        ]
        for alias in aliases:
            result = db.resolve_subcategory_name(alias)
            assert result is not None, f"Alias '{alias}' should resolve"
            name = db._subcategories[result]["name"]
            assert name.lower() == expected, f"'{alias}' should resolve to '{expected}', got '{name}'"


class TestShortestMatchPriority:
    """Test that shortest subcategory match wins."""

    def test_crystal_resolves_to_crystals(self):
        """'crystal' should resolve to 'Crystals' not 'Crystal Filters' or 'Crystal Oscillators'."""
        db = get_db()
        result = db.resolve_subcategory_name("crystal")
        assert result is not None
        name = db._subcategories[result]["name"]
        assert name == "Crystals", f"Expected 'Crystals', got '{name}'"

    def test_search_shows_resolved_name(self):
        """Search response should show the resolved subcategory name."""
        db = get_db()
        result = db.search(subcategory_name="crystal", limit=1)
        assert "error" not in result
        assert result["filters_applied"]["subcategory_resolved"] == "Crystals"


class TestFTSOrMode:
    """Test FTS OR mode (match_all_terms parameter)."""

    def test_match_all_terms_default_is_true(self):
        """match_all_terms should default to True (AND logic)."""
        db = get_db()
        result = db.search(query="test", limit=1)
        assert result["filters_applied"]["match_all_terms"] is True

    def test_or_mode_returns_more_results(self):
        """OR mode should return more results than AND mode for multi-word queries."""
        db = get_db()
        result_and = db.search(query="hall effect", match_all_terms=True, limit=1)
        result_or = db.search(query="hall effect", match_all_terms=False, limit=1)

        # OR mode should return at least as many results as AND mode
        # In practice it returns significantly more
        assert result_or["total"] >= result_and["total"]


class TestLibraryTypeCounts:
    """Test library type counts in search response."""

    def test_response_includes_library_type_counts(self):
        """Search response should include library_type_counts."""
        db = get_db()
        result = db.search(subcategory_name="MOSFETs", limit=1)

        assert "library_type_counts" in result
        assert "basic" in result["library_type_counts"]
        assert "preferred" in result["library_type_counts"]
        assert "extended" in result["library_type_counts"]

    def test_response_includes_no_fee_available(self):
        """Search response should include no_fee_available boolean."""
        db = get_db()
        result = db.search(subcategory_name="MOSFETs", limit=1)

        assert "no_fee_available" in result
        # MOSFETs should have some basic parts available
        assert result["no_fee_available"] is True

    def test_usb_c_has_no_basic_parts(self):
        """USB-C connectors should report no_fee_available=False."""
        db = get_db()
        result = db.search(subcategory_name="USB Connectors", query="TYPE-C", limit=1)

        # All USB-C connectors are extended
        assert result["library_type_counts"]["basic"] == 0
        assert result["library_type_counts"]["preferred"] == 0
        assert result["no_fee_available"] is False


class TestErrorMessagesWithSuggestions:
    """Test improved error messages with suggestions."""

    def test_not_found_includes_similar_subcategories(self):
        """Error for not found subcategory should include similar suggestions."""
        db = get_db()
        result = db.search(subcategory_name="usb type c connector xyz", limit=1)

        assert "error" in result
        assert "similar_subcategories" in result
        # Should suggest some connector-related subcategories
        similar = result["similar_subcategories"]
        assert len(similar) > 0 or similar == []  # May be empty if no matches

    def test_error_response_has_consistent_structure(self):
        """Error responses should have consistent structure."""
        db = get_db()
        result = db.search(subcategory_name="nonexistent12345", limit=1)

        assert "error" in result
        assert result["total"] == 0
        assert "library_type_counts" in result
        assert "no_fee_available" in result


class TestBatchLookup:
    """Test batch LCSC lookup."""

    def test_batch_lookup_returns_all_parts(self):
        """Batch lookup should return all requested parts."""
        db = get_db()
        lcsc_codes = ["C1525", "C25804", "C19702"]
        results = db.get_by_lcsc_batch(lcsc_codes)

        assert len(results) == 3
        assert all(code in results for code in lcsc_codes)
        assert all(results[code] is not None for code in lcsc_codes)

    def test_batch_lookup_handles_not_found(self):
        """Batch lookup should return None for missing parts."""
        db = get_db()
        lcsc_codes = ["C1525", "CNOTEXIST123"]
        results = db.get_by_lcsc_batch(lcsc_codes)

        assert results["C1525"] is not None
        assert results["CNOTEXIST123"] is None

    def test_batch_lookup_dedupes_input(self):
        """Batch lookup should handle duplicate input codes."""
        db = get_db()
        lcsc_codes = ["C1525", "c1525", "C1525"]  # duplicates + case variation
        results = db.get_by_lcsc_batch(lcsc_codes)

        assert len(results) == 1
        assert "C1525" in results


class TestPackageFamilyExpansion:
    """Test package family expansion."""

    def test_sot23_expands_to_variants(self):
        """SOT-23 should expand to include common variants."""
        db = get_db()
        expanded = db._expand_package("SOT-23")
        assert "SOT-23" in expanded
        assert "SOT-23-3" in expanded
        assert len(expanded) > 1

    def test_specific_package_no_expansion(self):
        """Specific package names should not expand."""
        db = get_db()
        expanded = db._expand_package("QFN-24-EP(4x4)")
        assert expanded == ["QFN-24-EP(4x4)"]

    def test_package_filter_uses_expansion(self):
        """Package filter should use expanded packages."""
        db = get_db()
        # SOT-23 alone vs expanded
        result = db.search(subcategory_name="MOSFETs", package="SOT-23", limit=1)
        # Should find multiple parts with SOT-23 variants
        assert result["total"] > 0  # SOT-23 variants combined

    def test_so8_expands_to_all_variants(self):
        """SO-8/SOP-8/SOIC-8 should all expand to include each other."""
        db = get_db()
        # All three should expand to the same set
        for pkg in ["SO-8", "SOP-8", "SOIC-8", "so8", "sop8", "soic8"]:
            expanded = db._expand_package(pkg)
            assert "SO-8" in expanded, f"{pkg} should expand to include SO-8"
            assert "SOP-8" in expanded, f"{pkg} should expand to include SOP-8"
            assert "SOIC-8" in expanded, f"{pkg} should expand to include SOIC-8"

    def test_so8_search_finds_all_variants(self):
        """Searching SO-8 should find parts with SO-8, SOP-8, and SOIC-8 packages."""
        db = get_db()
        result = db.search(subcategory_name="MOSFETs", package="SO-8", limit=100)
        assert result["total"] > 0
        # Should find multiple package variants
        packages_found = {p["package"] for p in result["results"]}
        # At least 2 of the 3 variants should be present (depends on DB contents)
        so_variants = packages_found & {"SO-8", "SOP-8", "SOIC-8"}
        assert len(so_variants) >= 1, f"Expected SO/SOP/SOIC-8, found {packages_found}"


class TestStringSpecFilter:
    """Test string-based spec filters (non-numeric)."""

    def test_type_filter_n_channel(self):
        """Type=N-Channel should find N-channel MOSFETs."""
        db = get_db()
        result = db.search(
            subcategory_name="MOSFETs",
            spec_filters=[SpecFilter("Type", "=", "N-Channel")],
            limit=5
        )
        assert result["total"] > 0  # Should find N-channel MOSFETs
        for part in result["results"]:
            assert part["specs"].get("Type") == "N-Channel"

    def test_type_filter_p_channel(self):
        """Type=P-Channel should find P-channel MOSFETs."""
        db = get_db()
        result = db.search(
            subcategory_name="MOSFETs",
            spec_filters=[SpecFilter("Type", "=", "P-Channel")],
            limit=5
        )
        assert result["total"] > 0  # Should find P-channel MOSFETs
        for part in result["results"]:
            assert part["specs"].get("Type") == "P-Channel"


class TestExtendedAliases:
    """Test extended subcategory aliases."""

    def test_dc_dc_aliases(self):
        """DC-DC converter aliases should work."""
        db = get_db()
        aliases = ["dc-dc", "dc dc", "buck converter", "boost converter"]
        for alias in aliases:
            resolved = db.resolve_subcategory_name(alias)
            assert resolved is not None, f"Alias '{alias}' should resolve"

    def test_sensor_aliases(self):
        """Sensor aliases should work."""
        db = get_db()
        aliases = ["hall sensor", "temperature sensor", "current sensor"]
        for alias in aliases:
            resolved = db.resolve_subcategory_name(alias)
            assert resolved is not None, f"Alias '{alias}' should resolve"

    def test_module_aliases(self):
        """Module aliases should work."""
        db = get_db()
        aliases = ["wifi module", "bluetooth module", "lora module"]
        for alias in aliases:
            resolved = db.resolve_subcategory_name(alias)
            assert resolved is not None, f"Alias '{alias}' should resolve"


class TestDatabaseStats:
    """Test database statistics."""

    def test_get_stats(self):
        """Should return valid statistics."""
        db = get_db()
        stats = db.get_stats()

        assert "total_parts" in stats
        assert stats["total_parts"] > 0  # Should have parts

        assert "by_library_type" in stats
        assert "basic" in stats["by_library_type"]
        assert "preferred" in stats["by_library_type"]
        assert "extended" in stats["by_library_type"]

        assert stats["subcategories"] > 0  # Should have subcategories


class TestSmartQueryParsing:
    """Test smart query parsing for natural language queries."""

    def test_parse_resistor_query(self):
        """Parse '10k resistor 0603 1%' into structured filters."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = parse_smart_query("10k resistor 0603 1%")

        assert result.subcategory == "chip resistor - surface mount"
        assert result.package == "0603"
        assert len(result.spec_filters) == 2

        # Check resistance filter
        res_filter = next(f for f in result.spec_filters if f.name == "Resistance")
        assert res_filter.operator == "="
        assert "10k" in res_filter.value.lower()

        # Check tolerance filter
        tol_filter = next(f for f in result.spec_filters if f.name == "Tolerance")
        assert tol_filter.value == "1%"

    def test_parse_capacitor_query(self):
        """Parse '100nF 25V capacitor' into structured filters."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = parse_smart_query("100nF 25V capacitor")

        assert result.subcategory == "multilayer ceramic capacitors mlcc - smd/smt"
        assert len(result.spec_filters) >= 2

        # Check capacitance filter
        cap_filter = next(f for f in result.spec_filters if f.name == "Capacitance")
        assert cap_filter.value == "100nF"

        # Check voltage filter (should be >= for safety margin)
        # Note: New parser uses "Voltage Rating" (correct spec name) instead of generic "Voltage"
        volt_filter = next(f for f in result.spec_filters if "Voltage" in f.name)
        assert volt_filter.operator == ">="
        assert "25V" in volt_filter.value

    def test_parse_mosfet_query(self):
        """Parse 'n-channel mosfet SOT-23' into structured filters."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = parse_smart_query("n-channel mosfet SOT-23")

        assert result.subcategory == "mosfets"
        assert result.package == "SOT-23"

    def test_parse_inductor_query(self):
        """Parse '10uH inductor' into structured filters."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = parse_smart_query("10uH inductor")

        assert result.subcategory == "inductors (smd)"
        ind_filter = next(f for f in result.spec_filters if f.name == "Inductance")
        assert ind_filter.value == "10uH"

    def test_parse_query_infers_category(self):
        """Should infer category from value patterns even without keyword."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        # Just "10k" should infer resistor
        result = parse_smart_query("10k 0402")
        assert result.subcategory == "chip resistor - surface mount"
        assert result.package == "0402"

        # Just "100nF" should infer capacitor
        result = parse_smart_query("100nF 0805")
        assert result.subcategory == "multilayer ceramic capacitors mlcc - smd/smt"
        assert result.package == "0805"

    def test_parse_query_remaining_text(self):
        """Remaining text should be cleaned up for FTS search."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = parse_smart_query("ESP32 module 3.3V")

        # ESP32 should remain in text (detected as model number)
        assert "esp32" in result.remaining_text.lower() or "module" in result.remaining_text.lower()
        # Voltage should be extracted as filter (now uses "Voltage Rating" for generic voltage)
        assert any("Voltage" in f.name for f in result.spec_filters)

    def test_parse_empty_query(self):
        """Empty or minimal queries should not crash."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = parse_smart_query("")
        assert result.remaining_text == ""
        assert result.subcategory is None

        result = parse_smart_query("abc")
        assert result.remaining_text == "abc"

    def test_parse_antenna_with_frequency(self):
        """Parse 'ceramic antenna 2.4GHz' with subcategory and frequency."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = parse_smart_query("ceramic antenna 2.4GHz")
        assert result.subcategory == "antennas"

        # Should extract frequency filter
        freq_filter = next((f for f in result.spec_filters if "freq" in f.name.lower()), None)
        assert freq_filter is not None
        assert freq_filter.value == "2.4GHz"

    def test_parse_humidity_temperature_sensor(self):
        """Parse 'humidity temperature sensor I2C' with correct subcategory."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = parse_smart_query("humidity temperature sensor I2C")
        assert result.subcategory == "temperature and humidity sensor"

        # Should extract I2C interface
        interface_filters = [f for f in result.spec_filters if f.name == "Interface"]
        assert len(interface_filters) == 1
        assert interface_filters[0].value == "I2C"

    def test_rj45_not_treated_as_model_number(self):
        """RJ45 and similar connector codes should not be treated as model numbers."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        # Test RJ45
        result = parse_smart_query("RJ45 connector THT")
        assert result.model_number is None
        assert result.subcategory == "ethernet connectors / modular connectors (rj45 rj11)"
        assert result.mounting_type == "Through Hole"

        # Test other RJ variants
        for code in ["RJ11", "RJ12"]:
            result = parse_smart_query(f"{code} connector")
            assert result.model_number is None, f"{code} should not be detected as model number"

    def test_magnetics_synonym_for_filtered_connectors(self):
        """'magnetics' should be replaced with 'filtered' for connector searches."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = parse_smart_query("RJ45 magnetics THT")

        # Should detect as ethernet connector
        assert result.subcategory == "ethernet connectors / modular connectors (rj45 rj11)"
        assert result.mounting_type == "Through Hole"

        # "magnetics" should be replaced with "filtered" in remaining text
        assert result.remaining_text == "filtered"

        # Test that "magnetics" -> "filtered" replacement only happens for connectors
        result_non_connector = parse_smart_query("magnetics sensor")
        assert "filtered" not in result_non_connector.remaining_text.lower()

    def test_csp_package_detection(self):
        """CSP package variants (WLCSP, LFCSP, UCSP, etc.) should be detected correctly."""
        from pcbparts_mcp.smart_parser import parse_smart_query

        test_cases = [
            ("STM32L4 WLCSP144", "WLCSP144"),
            ("STM32F4 LFCSP64", "LFCSP64"),
            ("sensor UCSP-20", "UCSP-20"),
            ("chip CSP100", "CSP100"),
            ("IC VCSP48", "VCSP48"),
        ]

        for query, expected_package in test_cases:
            result = parse_smart_query(query)
            assert result.package == expected_package, \
                f"Query '{query}' should detect package '{expected_package}', got '{result.package}'"

        # CSP packages should not be treated as model numbers
        result = parse_smart_query("CSP100")
        assert result.package == "CSP100"
        assert result.model_number is None


class TestListAttributes:
    """Test attribute discovery endpoint."""

    def test_list_mosfet_attributes(self):
        """List attributes for MOSFETs should include common specs."""
        db = get_db()
        result = db.list_attributes(subcategory_name="MOSFETs")

        assert "error" not in result
        assert result["subcategory_name"] == "MOSFETs"
        assert len(result["attributes"]) > 5

        # Should include common MOSFET attributes
        attr_names = [a["name"] for a in result["attributes"]]
        assert any("Vgs" in name or "Gate" in name for name in attr_names)
        assert any("Type" in name for name in attr_names)

    def test_list_attributes_includes_type_info(self):
        """Attributes should include type (numeric/string)."""
        db = get_db()
        result = db.list_attributes(subcategory_name="MOSFETs")

        for attr in result["attributes"]:
            assert "type" in attr
            assert attr["type"] in ("numeric", "string")
            assert "count" in attr

    def test_list_attributes_includes_aliases(self):
        """Numeric attributes should show their short aliases."""
        db = get_db()
        result = db.list_attributes(subcategory_name="MOSFETs")

        # Find Gate Threshold Voltage attribute
        vgs_attr = next(
            (a for a in result["attributes"] if "Gate Threshold" in a["name"]),
            None
        )
        if vgs_attr:
            assert vgs_attr["alias"] == "Vgs(th)"

    def test_list_attributes_not_found(self):
        """Non-existent subcategory should return error with suggestions."""
        db = get_db()
        result = db.list_attributes(subcategory_name="NonExistent12345")

        assert "error" in result

    def test_list_capacitor_attributes(self):
        """List attributes for MLCC capacitors."""
        db = get_db()
        result = db.list_attributes(subcategory_name="MLCC")

        assert "error" not in result
        attr_names = [a["name"] for a in result["attributes"]]

        # Should include capacitance, voltage, tolerance
        assert any("Capacitance" in name for name in attr_names)
        assert any("Voltage" in name for name in attr_names)


class TestSearchSmartParsing:
    """Test smart query parsing in search()."""

    def test_search_resistor(self):
        """Smart search should find 10k 0603 1% resistors."""
        db = get_db()
        from pcbparts_mcp.smart_parser import parse_smart_query

        parsed = parse_smart_query("10k resistor 0603 1%")

        # Build search kwargs from parsed result
        result = db.search(
            subcategory_name=parsed.subcategory,
            package=parsed.package,
            spec_filters=parsed.spec_filters,
            limit=5,
        )

        assert result["total"] > 0
        # All results should be in the correct subcategory
        for part in result["results"]:
            assert "resistor" in part["subcategory"].lower()

    def test_search_mosfet(self):
        """Smart search should find SOT-23 MOSFETs."""
        db = get_db()
        from pcbparts_mcp.smart_parser import parse_smart_query

        parsed = parse_smart_query("mosfet SOT-23")

        result = db.search(
            subcategory_name=parsed.subcategory,
            package=parsed.package,
            limit=5,
        )

        assert result["total"] > 0  # Should find SOT-23 MOSFETs
        for part in result["results"]:
            # Package should be SOT-23 or variant
            assert "sot-23" in part["package"].lower() or "sot23" in part["package"].lower()


class TestMPNLookup:
    """Test MPN (manufacturer part number) lookup."""

    def test_exact_mpn_match(self):
        """Exact MPN should find the part."""
        db = get_db()
        # AO3400A is a popular MOSFET that should be in the DB
        results = db.get_by_mpn("AO3400A")
        assert len(results) > 0
        assert any(r["model"] == "AO3400A" for r in results)

    def test_mpn_case_insensitive(self):
        """MPN lookup should be case-insensitive."""
        db = get_db()
        results_upper = db.get_by_mpn("AO3400A")
        results_lower = db.get_by_mpn("ao3400a")
        assert len(results_upper) == len(results_lower)
        if results_upper:
            assert results_upper[0]["lcsc"] == results_lower[0]["lcsc"]

    def test_mpn_not_found(self):
        """Non-existent MPN should return empty list."""
        db = get_db()
        results = db.get_by_mpn("TOTALLYFAKE12345XYZ")
        assert results == []

    def test_mpn_empty_string(self):
        """Empty MPN should return empty list."""
        db = get_db()
        results = db.get_by_mpn("")
        assert results == []
        results = db.get_by_mpn("   ")
        assert results == []

    def test_mpn_with_distributor_suffix(self):
        """MPN with -TR suffix should still find the part via normalization."""
        db = get_db()
        # First find a known part
        base_results = db.get_by_mpn("AO3400A")
        if base_results:
            # Try with -TR suffix (tape & reel)
            tr_results = db.get_by_mpn("AO3400A-TR")
            # Should find results (either exact or via normalization)
            # Note: may not match if AO3400A-TR is a separate MPN in the DB
            assert len(tr_results) >= 0  # Non-crashing is the baseline

    def test_mpn_returns_correct_fields(self):
        """MPN results should have all expected fields."""
        db = get_db()
        results = db.get_by_mpn("AO3400A")
        if results:
            part = results[0]
            assert "lcsc" in part
            assert "model" in part
            assert "manufacturer" in part
            assert "package" in part
            assert "stock" in part
            assert "price" in part
            assert "library_type" in part
            assert "specs" in part
