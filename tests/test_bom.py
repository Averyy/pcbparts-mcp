"""Tests for BOM generation functionality."""

import pytest
from jlcpcb_mcp.bom import (
    BOMPart,
    BOMIssue,
    validate_designators,
    merge_duplicate_parts,
    sort_by_designator,
    generate_comment,
    check_footprint_mismatch,
    get_price_at_quantity,
    calculate_line_cost,
    generate_csv,
    generate_summary,
    validate_manual_part,
    check_stock_issues,
    check_moq_issue,
    check_extended_part,
    check_easyeda_footprint,
)


class TestValidateDesignators:
    """Tests for duplicate designator detection."""

    def test_no_duplicates(self):
        """No issues when all designators are unique."""
        parts = [
            {"lcsc": "C1525", "designators": ["C1", "C2"]},
            {"lcsc": "C25804", "designators": ["R1", "R2"]},
        ]
        issues = validate_designators(parts)
        assert len(issues) == 0

    def test_duplicate_within_same_part(self):
        """Detects duplicate within same part entry."""
        parts = [
            {"lcsc": "C1525", "designators": ["C1", "C1"]},
        ]
        issues = validate_designators(parts)
        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "C1" in issues[0].issue
        assert "Duplicate" in issues[0].issue

    def test_duplicate_across_parts(self):
        """Detects duplicate across different parts."""
        parts = [
            {"lcsc": "C1525", "designators": ["C1", "C2"]},
            {"lcsc": "C25804", "designators": ["C2", "R1"]},
        ]
        issues = validate_designators(parts)
        assert len(issues) == 1
        assert "C2" in issues[0].issue

    def test_multiple_duplicates(self):
        """Reports each duplicate separately."""
        parts = [
            {"lcsc": "C1525", "designators": ["C1", "C2"]},
            {"lcsc": "C25804", "designators": ["C1", "C2", "R1"]},
        ]
        issues = validate_designators(parts)
        assert len(issues) == 2

    def test_empty_designators(self):
        """Error when part has empty designators list."""
        parts = [
            {"lcsc": "C1525", "designators": []},
        ]
        issues = validate_designators(parts)
        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "no designators" in issues[0].issue

    def test_missing_designators_key(self):
        """Error when part has no designators key."""
        parts = [
            {"lcsc": "C1525"},
        ]
        issues = validate_designators(parts)
        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "no designators" in issues[0].issue


class TestMergeDuplicateParts:
    """Tests for merging parts with same LCSC code."""

    def test_no_duplicates(self):
        """No merging when LCSC codes are unique."""
        parts = [
            {"lcsc": "C1525", "designators": ["C1"]},
            {"lcsc": "C25804", "designators": ["R1"]},
        ]
        merged, issues = merge_duplicate_parts(parts)
        assert len(merged) == 2
        assert len(issues) == 0

    def test_merge_same_lcsc(self):
        """Merges designators for same LCSC code."""
        parts = [
            {"lcsc": "C1525", "designators": ["C1", "C2"]},
            {"lcsc": "C1525", "designators": ["C3", "C4"]},
        ]
        merged, issues = merge_duplicate_parts(parts)
        assert len(merged) == 1
        assert merged[0]["lcsc"] == "C1525"
        assert merged[0]["designators"] == ["C1", "C2", "C3", "C4"]
        assert len(issues) == 0

    def test_merge_normalizes_case(self):
        """LCSC codes are normalized to uppercase."""
        parts = [
            {"lcsc": "c1525", "designators": ["C1"]},
            {"lcsc": "C1525", "designators": ["C2"]},
        ]
        merged, issues = merge_duplicate_parts(parts)
        assert len(merged) == 1
        assert merged[0]["lcsc"] == "C1525"
        assert merged[0]["designators"] == ["C1", "C2"]

    def test_manual_parts_not_merged(self):
        """Manual parts (no LCSC) are kept separate."""
        parts = [
            {"designators": ["J1"], "comment": "Connector A", "footprint": "USB-C"},
            {"designators": ["J2"], "comment": "Connector B", "footprint": "USB-C"},
        ]
        merged, issues = merge_duplicate_parts(parts)
        assert len(merged) == 2

    def test_conflicting_comment_warning(self):
        """Warns when same LCSC has conflicting comment overrides."""
        parts = [
            {"lcsc": "C1525", "designators": ["C1"], "comment": "Comment A"},
            {"lcsc": "C1525", "designators": ["C2"], "comment": "Comment B"},
        ]
        merged, issues = merge_duplicate_parts(parts)
        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert "Conflicting comment" in issues[0].issue

    def test_conflicting_footprint_warning(self):
        """Warns when same LCSC has conflicting footprint overrides."""
        parts = [
            {"lcsc": "C1525", "designators": ["C1"], "footprint": "0402"},
            {"lcsc": "C1525", "designators": ["C2"], "footprint": "0603"},
        ]
        merged, issues = merge_duplicate_parts(parts)
        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert "Conflicting footprint" in issues[0].issue

    def test_deduplicates_designators(self):
        """Removes duplicate designators within merged part."""
        parts = [
            {"lcsc": "C1525", "designators": ["C1", "C2"]},
            {"lcsc": "C1525", "designators": ["C2", "C3"]},
        ]
        merged, issues = merge_duplicate_parts(parts)
        assert merged[0]["designators"] == ["C1", "C2", "C3"]


class TestSortByDesignator:
    """Tests for natural designator sorting."""

    def test_simple_sort(self):
        """Sorts C1, C2, C10 correctly (not C1, C10, C2)."""
        parts = [
            BOMPart(lcsc="A", designators=["C10"], quantity=1, comment="", footprint=""),
            BOMPart(lcsc="B", designators=["C2"], quantity=1, comment="", footprint=""),
            BOMPart(lcsc="C", designators=["C1"], quantity=1, comment="", footprint=""),
        ]
        sorted_parts = sort_by_designator(parts)
        assert [p.lcsc for p in sorted_parts] == ["C", "B", "A"]

    def test_groups_by_prefix(self):
        """Groups C, R, U together in order."""
        parts = [
            BOMPart(lcsc="U1", designators=["U1"], quantity=1, comment="", footprint=""),
            BOMPart(lcsc="C1", designators=["C1"], quantity=1, comment="", footprint=""),
            BOMPart(lcsc="R1", designators=["R1"], quantity=1, comment="", footprint=""),
        ]
        sorted_parts = sort_by_designator(parts)
        assert [p.designators[0] for p in sorted_parts] == ["C1", "R1", "U1"]

    def test_mixed_prefixes(self):
        """Handles mixed prefixes and numbers."""
        parts = [
            BOMPart(lcsc="A", designators=["R10"], quantity=1, comment="", footprint=""),
            BOMPart(lcsc="B", designators=["C2"], quantity=1, comment="", footprint=""),
            BOMPart(lcsc="C", designators=["R1"], quantity=1, comment="", footprint=""),
            BOMPart(lcsc="D", designators=["C1"], quantity=1, comment="", footprint=""),
        ]
        sorted_parts = sort_by_designator(parts)
        assert [p.designators[0] for p in sorted_parts] == ["C1", "C2", "R1", "R10"]

    def test_case_insensitive(self):
        """Sort is case-insensitive."""
        parts = [
            BOMPart(lcsc="A", designators=["c2"], quantity=1, comment="", footprint=""),
            BOMPart(lcsc="B", designators=["C1"], quantity=1, comment="", footprint=""),
        ]
        sorted_parts = sort_by_designator(parts)
        assert sorted_parts[0].designators[0] == "C1"


class TestGenerateComment:
    """Tests for Comment field generation."""

    def test_user_override(self):
        """User override takes priority."""
        part_data = {"model": "ABC123", "key_specs": {"Value": "100nF"}, "package": "0402"}
        result = generate_comment(part_data, user_override="Custom Comment")
        assert result == "Custom Comment"

    def test_key_specs_for_passives(self):
        """Uses key_specs for passives (more useful than MPN)."""
        part_data = {
            "model": "CL05B104KO5NNNC",
            "key_specs": {"Capacitance": "100nF", "Voltage": "50V"},
            "package": "0402",
        }
        result = generate_comment(part_data)
        assert "100nF" in result
        assert "50V" in result
        assert "0402" in result

    def test_model_for_ics(self):
        """Falls back to model when key_specs is empty."""
        part_data = {"model": "STM32F103C8T6", "key_specs": {}, "package": "LQFP-48"}
        result = generate_comment(part_data)
        assert result == "STM32F103C8T6"

    def test_model_truncated(self):
        """Model is truncated to 50 chars."""
        part_data = {"model": "A" * 100, "key_specs": {}, "package": "0402"}
        result = generate_comment(part_data)
        assert len(result) == 50

    def test_package_fallback(self):
        """Falls back to package if no model."""
        part_data = {"key_specs": {}, "package": "0402"}
        result = generate_comment(part_data)
        assert result == "0402"

    def test_unknown_fallback(self):
        """Returns Unknown if nothing available."""
        result = generate_comment({})
        assert result == "Unknown"

    def test_no_duplicate_package(self):
        """Doesn't duplicate package if already in specs."""
        part_data = {
            "key_specs": {"Value": "10K", "Package": "0603"},
            "package": "0603",
        }
        result = generate_comment(part_data)
        # Should not have 0603 twice
        assert result.count("0603") == 1


class TestCheckFootprintMismatch:
    """Tests for footprint mismatch detection."""

    def test_no_mismatch(self):
        """No issue when footprints match."""
        result = check_footprint_mismatch("0402", "0402")
        assert result is None

    def test_case_insensitive_match(self):
        """Match is case-insensitive."""
        result = check_footprint_mismatch("SOIC-8", "soic-8")
        assert result is None

    def test_mismatch_detected(self):
        """Detects footprint mismatch."""
        result = check_footprint_mismatch("0402", "0603")
        assert result is not None
        assert result.severity == "warning"
        assert "0402" in result.issue
        assert "0603" in result.issue

    def test_no_user_footprint(self):
        """No issue if user didn't provide footprint."""
        result = check_footprint_mismatch(None, "0603")
        assert result is None

    def test_no_api_footprint(self):
        """No issue if API doesn't have footprint."""
        result = check_footprint_mismatch("0402", None)
        assert result is None


class TestGetPriceAtQuantity:
    """Tests for price tier selection."""

    def test_single_tier(self):
        """Single tier returns that price."""
        prices = [{"qty": "1+", "price": 0.01}]
        assert get_price_at_quantity(prices, 1) == 0.01
        assert get_price_at_quantity(prices, 100) == 0.01

    def test_multiple_tiers(self):
        """Selects correct tier based on quantity."""
        prices = [
            {"qty": "1+", "price": 0.0052},
            {"qty": "10+", "price": 0.0035},
            {"qty": "100+", "price": 0.0023},
        ]
        assert get_price_at_quantity(prices, 1) == 0.0052
        assert get_price_at_quantity(prices, 5) == 0.0052
        assert get_price_at_quantity(prices, 10) == 0.0035
        assert get_price_at_quantity(prices, 50) == 0.0035
        assert get_price_at_quantity(prices, 100) == 0.0023
        assert get_price_at_quantity(prices, 1000) == 0.0023

    def test_empty_prices(self):
        """Returns None for empty price list."""
        assert get_price_at_quantity([], 100) is None

    def test_none_prices(self):
        """Returns None for None."""
        assert get_price_at_quantity(None, 100) is None


class TestCalculateLineCost:
    """Tests for cost calculation."""

    def test_with_board_qty(self):
        """Calculates order_qty = quantity × board_qty."""
        prices = [
            {"qty": "1+", "price": 0.01},
            {"qty": "100+", "price": 0.005},
        ]
        order_qty, price, cost = calculate_line_cost(prices, quantity=3, board_qty=100)
        assert order_qty == 300
        assert price == 0.005  # 300 qualifies for 100+ tier
        assert cost == 1.5  # 0.005 * 300

    def test_without_board_qty(self):
        """Without board_qty, order_qty = quantity."""
        prices = [{"qty": "1+", "price": 0.01}]
        order_qty, price, cost = calculate_line_cost(prices, quantity=3, board_qty=None)
        assert order_qty == 3
        assert price == 0.01
        assert cost == 0.03

    def test_no_prices(self):
        """Returns None costs when no prices available."""
        order_qty, price, cost = calculate_line_cost([], quantity=3, board_qty=100)
        assert order_qty == 300
        assert price is None
        assert cost is None


class TestGenerateCsv:
    """Tests for CSV generation."""

    def test_basic_csv(self):
        """Generates valid JLCPCB CSV format."""
        parts = [
            BOMPart(
                lcsc="C1525",
                designators=["C1", "C2", "C3"],
                quantity=3,
                comment="100nF 50V X7R 0402",
                footprint="0402",
            ),
        ]
        csv = generate_csv(parts)
        lines = csv.strip().split("\n")
        assert lines[0] == "Comment,Designator,Footprint,LCSC Part #"
        assert "C1525" in lines[1]
        assert "100nF 50V X7R 0402" in lines[1]

    def test_designators_with_commas(self):
        """Properly quotes designators containing commas."""
        parts = [
            BOMPart(
                lcsc="C1525",
                designators=["C1", "C2"],
                quantity=2,
                comment="Test",
                footprint="0402",
            ),
        ]
        csv = generate_csv(parts)
        # Designator field should be quoted: "C1,C2"
        assert '"C1,C2"' in csv

    def test_manual_part_empty_lcsc(self):
        """Manual parts have empty LCSC column."""
        parts = [
            BOMPart(
                lcsc=None,
                designators=["J1"],
                quantity=1,
                comment="USB-C Connector",
                footprint="USB-C-SMD",
            ),
        ]
        csv = generate_csv(parts)
        lines = csv.strip().split("\n")
        # Last field should be empty for manual part
        assert lines[1].endswith(",")


class TestGenerateSummary:
    """Tests for summary generation."""

    def test_basic_summary(self):
        """Calculates basic counts and costs."""
        parts = [
            BOMPart(lcsc="A", designators=["C1", "C2"], quantity=2, comment="", footprint="", line_cost=0.50),
            BOMPart(lcsc="B", designators=["R1"], quantity=1, comment="", footprint="", line_cost=0.10),
        ]
        summary = generate_summary(parts, board_qty=None, issues=[])
        assert summary["total_line_items"] == 2
        assert summary["total_components"] == 3
        assert summary["estimated_cost"] == 0.60

    def test_extended_parts_fee(self):
        """Calculates $3 fee per extended part."""
        parts = [
            BOMPart(lcsc="A", designators=["U1"], quantity=1, comment="", footprint="",
                    library_type="extended", line_cost=1.00),
            BOMPart(lcsc="B", designators=["U2"], quantity=1, comment="", footprint="",
                    library_type="extended", line_cost=2.00),
            BOMPart(lcsc="C", designators=["R1"], quantity=1, comment="", footprint="",
                    library_type="basic", line_cost=0.50),
        ]
        summary = generate_summary(parts, board_qty=None, issues=[])
        assert summary["extended_parts_count"] == 2
        assert summary["extended_parts_fee"] == 6.0  # 2 × $3
        assert summary["total_with_fees"] == 9.5  # 3.50 + 6.00

    def test_stock_sufficient_with_no_errors(self):
        """stock_sufficient is True when no stock errors."""
        parts = [BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="")]
        summary = generate_summary(parts, board_qty=100, issues=[])
        assert summary["stock_sufficient"] is True

    def test_stock_insufficient_with_errors(self):
        """stock_sufficient is False when stock errors exist."""
        parts = [BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="")]
        issues = [BOMIssue(lcsc="A", designators=["C1"], severity="error", issue="Insufficient stock: need 100, have 50")]
        summary = generate_summary(parts, board_qty=100, issues=issues)
        assert summary["stock_sufficient"] is False


class TestValidateManualPart:
    """Tests for manual part validation."""

    def test_valid_manual_part(self):
        """No issues for valid manual part."""
        part = {"designators": ["J1"], "comment": "Connector", "footprint": "USB-C"}
        issues = validate_manual_part(part)
        assert len(issues) == 0

    def test_missing_comment(self):
        """Error when comment missing."""
        part = {"designators": ["J1"], "footprint": "USB-C"}
        issues = validate_manual_part(part)
        assert len(issues) == 1
        assert "comment" in issues[0].issue.lower()

    def test_missing_footprint(self):
        """Error when footprint missing."""
        part = {"designators": ["J1"], "comment": "Connector"}
        issues = validate_manual_part(part)
        assert len(issues) == 1
        assert "footprint" in issues[0].issue.lower()

    def test_missing_both(self):
        """Two errors when both missing."""
        part = {"designators": ["J1"]}
        issues = validate_manual_part(part)
        assert len(issues) == 2


class TestCheckStockIssues:
    """Tests for stock issue detection."""

    def test_out_of_stock(self):
        """Error when stock is 0."""
        part = BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="", stock=0)
        issues = check_stock_issues(part, min_stock=0, board_qty=None)
        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "Out of stock" in issues[0].issue

    def test_insufficient_stock(self):
        """Error when stock < required for board_qty."""
        part = BOMPart(lcsc="A", designators=["C1", "C2", "C3"], quantity=3, comment="", footprint="", stock=250)
        issues = check_stock_issues(part, min_stock=0, board_qty=100)
        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "need 300" in issues[0].issue
        assert "have 250" in issues[0].issue

    def test_low_stock_warning(self):
        """Warning when stock < min_stock (no board_qty)."""
        part = BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="", stock=45)
        issues = check_stock_issues(part, min_stock=50, board_qty=None)
        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert "Low stock" in issues[0].issue

    def test_no_warning_with_board_qty(self):
        """min_stock ignored when board_qty provided."""
        part = BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="", stock=45)
        # 45 stock is plenty for 1 × 10 boards
        issues = check_stock_issues(part, min_stock=50, board_qty=10)
        assert len(issues) == 0


class TestCheckMoqIssue:
    """Tests for MOQ warning."""

    def test_below_moq(self):
        """Warning when order_qty < min_order."""
        part = BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="",
                       order_qty=5, min_order=100)
        issue = check_moq_issue(part)
        assert issue is not None
        assert issue.severity == "warning"
        assert "MOQ is 100" in issue.issue

    def test_above_moq(self):
        """No warning when order_qty >= min_order."""
        part = BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="",
                       order_qty=100, min_order=100)
        issue = check_moq_issue(part)
        assert issue is None


class TestCheckExtendedPart:
    """Tests for extended part warning."""

    def test_extended_part(self):
        """Warning for extended library parts."""
        part = BOMPart(lcsc="A", designators=["U1"], quantity=1, comment="", footprint="",
                       library_type="extended")
        issue = check_extended_part(part)
        assert issue is not None
        assert issue.severity == "warning"
        assert "$3" in issue.issue

    def test_basic_part(self):
        """No warning for basic parts."""
        part = BOMPart(lcsc="A", designators=["R1"], quantity=1, comment="", footprint="",
                       library_type="basic")
        issue = check_extended_part(part)
        assert issue is None


class TestCheckEasyedaFootprint:
    """Tests for EasyEDA footprint warning."""

    def test_no_footprint(self):
        """Warning when no EasyEDA footprint."""
        part = BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="",
                       has_easyeda_footprint=False)
        issue = check_easyeda_footprint(part)
        assert issue is not None
        assert issue.severity == "warning"
        assert "EasyEDA" in issue.issue

    def test_has_footprint(self):
        """No warning when footprint exists."""
        part = BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="",
                       has_easyeda_footprint=True)
        issue = check_easyeda_footprint(part)
        assert issue is None

    def test_unknown_footprint(self):
        """No warning when footprint status unknown."""
        part = BOMPart(lcsc="A", designators=["C1"], quantity=1, comment="", footprint="",
                       has_easyeda_footprint=None)
        issue = check_easyeda_footprint(part)
        assert issue is None


@pytest.mark.asyncio
class TestBOMIntegration:
    """Integration tests that hit the real JLCPCB API."""

    @pytest.fixture
    async def client(self):
        from jlcpcb_mcp.client import JLCPCBClient
        client = JLCPCBClient()
        yield client
        await client.close()

    async def test_get_parts_batch(self, client):
        """Test batch fetching of multiple parts."""
        codes = ["C1525", "C25804", "C82899"]
        results = await client.get_parts_batch(codes)

        # All codes should be in results
        assert all(code in results for code in codes)

        # C1525 is a common capacitor, should exist
        assert results["C1525"] is not None
        assert results["C1525"]["lcsc"] == "C1525"

        # Check has EasyEDA info
        assert "has_easyeda_footprint" in results["C1525"]

    async def test_get_parts_batch_with_invalid(self, client):
        """Test batch fetch handles invalid codes gracefully."""
        codes = ["C1525", "C99999999999"]  # Valid and invalid
        results = await client.get_parts_batch(codes)

        assert results["C1525"] is not None
        assert results["C99999999999"] is None

    async def test_full_bom_flow(self, client):
        """Integration test: full BOM validation with real parts."""
        # Simulate what validate_bom does
        parts_input = [
            {"lcsc": "C1525", "designators": ["C1", "C2", "C3"]},  # 100nF capacitor
            {"lcsc": "C25804", "designators": ["R1", "R2"]},  # 10K resistor
        ]

        # Merge (no duplicates in this case)
        merged, merge_issues = merge_duplicate_parts(parts_input)
        assert len(merged) == 2
        assert len(merge_issues) == 0

        # Fetch parts
        lcsc_codes = [p["lcsc"] for p in merged]
        fetched = await client.get_parts_batch(lcsc_codes)

        # Verify we got data
        assert all(fetched.get(code) is not None for code in lcsc_codes)

        # Build BOM parts
        bom_parts = []
        for part in merged:
            lcsc = part["lcsc"]
            data = fetched[lcsc]
            prices = data.get("prices", [])
            order_qty, unit_price, line_cost = calculate_line_cost(
                prices, len(part["designators"]), board_qty=10
            )
            bom_parts.append(BOMPart(
                lcsc=lcsc,
                designators=part["designators"],
                quantity=len(part["designators"]),
                comment=generate_comment(data),
                footprint=data.get("package", "Unknown"),
                stock=data.get("stock"),
                price=unit_price,
                order_qty=order_qty,
                line_cost=line_cost,
                library_type=data.get("library_type"),
            ))

        # Sort and generate CSV
        sorted_parts = sort_by_designator(bom_parts)
        csv = generate_csv(sorted_parts)

        # Verify CSV structure
        lines = csv.strip().split("\n")
        assert lines[0] == "Comment,Designator,Footprint,LCSC Part #"
        assert len(lines) == 3  # Header + 2 parts

        # Verify summary
        summary = generate_summary(sorted_parts, board_qty=10, issues=[])
        assert summary["total_line_items"] == 2
        assert summary["total_components"] == 5  # 3 + 2
