"""Tests for JLCPCB MCP server functions."""

import pytest
from jlcpcb_mcp.mounting import detect_mounting_type


class TestDetectMountingType:
    """Test mounting type detection."""

    # SMD packages
    @pytest.mark.parametrize("package", [
        "0402", "0603", "0805", "1206", "1210",  # Imperial sizes
        "SOT-23", "SOT-23-5", "SOT-223", "SOT-89",  # Small outline
        "SOIC-8", "SOP-8", "SSOP-16", "TSSOP-20",  # Small outline ICs
        "QFP-48", "LQFP-64", "TQFP-32",  # Quad flat
        "QFN-24", "DFN-8", "WSON-8",  # No-lead
        "BGA-256", "WLCSP-20",  # Ball grid array
        "DPAK", "TO-252", "TO-263", "D2PAK",  # Power SMD
        "DO-214AC", "SMA", "SMB", "SMC",  # Diode SMD
        "SC-70-5", "SC-88",  # Small chip
        "SMD,4x3mm",  # JLCPCB format with SMD prefix
    ])
    def test_smd_packages(self, package):
        """SMD packages should return 'smd'."""
        assert detect_mounting_type(package) == "smd"

    # Through-hole packages
    @pytest.mark.parametrize("package", [
        "DIP-8", "DIP-16", "PDIP-28",  # Dual in-line
        "TO-220", "TO-220-3", "TO-92", "TO-247",  # Power through-hole
        "DO-41", "DO-35", "DO-201AD",  # Diode through-hole
        "SIP-3", "SIP-9",  # Single in-line
        "Axial", "AXIAL-0.3",  # Axial components
        "Radial", "RADIAL-5mm",  # Radial capacitors
        "PIN Header", "2.54mm,Pin Header",  # Pin headers
        "Plugin", "Plugin,P=2.54mm", "Plugin,D=5mm",  # JLCPCB Plugin format
        "HC-49S", "HC-49U",  # Crystal packages
        "Through hole", "Through-hole",  # Explicit through-hole
        "Push-Pull,P=2.54mm",  # Push-pull headers
    ])
    def test_through_hole_packages(self, package):
        """Through-hole packages should return 'through_hole'."""
        assert detect_mounting_type(package) == "through_hole"

    def test_empty_package_defaults_to_not_sure(self):
        """Empty or None package defaults to not_sure."""
        assert detect_mounting_type("") == "not_sure"
        assert detect_mounting_type(None) == "not_sure"

    def test_case_insensitive(self):
        """Package detection should be case-insensitive."""
        assert detect_mounting_type("qfn-24") == "smd"
        assert detect_mounting_type("QFN-24") == "smd"
        assert detect_mounting_type("dip-8") == "through_hole"
        assert detect_mounting_type("DIP-8") == "through_hole"

    def test_unknown_defaults_to_not_sure(self):
        """Unknown packages default to 'not_sure' instead of guessing."""
        assert detect_mounting_type("CUSTOM-PKG") == "not_sure"
        assert detect_mounting_type("XYZ-123") == "not_sure"
        assert detect_mounting_type("-") == "not_sure"


class TestCategoryBasedMountingType:
    """Test mounting type detection from category/subcategory names."""

    # Subcategory names should take priority
    @pytest.mark.parametrize("subcategory", [
        "Aluminum Electrolytic Capacitors - SMD",
        "Multilayer Ceramic Capacitors MLCC - SMD/SMT",
        "Inductors (SMD)",
        "Chip Resistor - Surface Mount",
        "SMD Quick Terminal",
    ])
    def test_smd_subcategories(self, subcategory):
        """Subcategories with SMD/SMT/Surface Mount should return 'smd'."""
        # Even with unknown package, subcategory should determine mounting
        assert detect_mounting_type("UNKNOWN-PKG", subcategory=subcategory) == "smd"

    @pytest.mark.parametrize("subcategory", [
        "Through Hole Ceramic Capacitors",
        "Through Hole Resistors",
        "Color Ring Inductors / Through Hole Inductors",
    ])
    def test_through_hole_subcategories(self, subcategory):
        """Subcategories with 'Through Hole' in name should return 'through_hole'."""
        # Even with SMD-looking package, subcategory should take priority
        assert detect_mounting_type("0402", subcategory=subcategory) == "through_hole"

    def test_dip_switches_uses_package_not_category(self):
        """'DIP Switches' subcategory should NOT force through-hole - DIP is switch style, not mounting."""
        # Package determines mounting type since "DIP Switches" doesn't indicate mounting
        assert detect_mounting_type("SMD,P=1.27mm", subcategory="DIP Switches") == "smd"
        assert detect_mounting_type("DIP-8", subcategory="DIP Switches") == "through_hole"

    def test_plugin_in_category_uses_package(self):
        """'Ceramic plugin capacitor' subcategory uses package for mounting detection."""
        # "Plugin" in category name is ambiguous - use package instead
        assert detect_mounting_type("Plugin,D5mm", subcategory="Ceramic plugin capacitor") == "through_hole"
        # 0402 is a recognized SMD pattern
        assert detect_mounting_type("0402", subcategory="Ceramic plugin capacitor") == "smd"

    def test_subcategory_overrides_package(self):
        """Subcategory name takes priority over package name."""
        # Package says SMD (0402), but subcategory says through-hole
        assert detect_mounting_type("0402", subcategory="Through Hole Resistors") == "through_hole"
        # Package says through-hole (DIP-8), but subcategory says SMD
        assert detect_mounting_type("DIP-8", subcategory="Inductors (SMD)") == "smd"

    def test_falls_back_to_package_when_no_category_hint(self):
        """When category/subcategory have no mounting hint, use package."""
        # Subcategory "Resistors" has no mounting hint, so package determines it
        assert detect_mounting_type("0402", subcategory="Resistors") == "smd"
        assert detect_mounting_type("DIP-8", subcategory="Resistors") == "through_hole"

    def test_feed_through_not_matched(self):
        """'Feed Through Capacitors' should NOT match through-hole pattern."""
        # "Feed Through" is about signal path, not mounting type
        # Uses package-based detection: 0402 is SMD
        assert detect_mounting_type("0402", subcategory="Feed Through Capacitors") == "smd"

    def test_hot_dip_not_matched(self):
        """'Hot-dip galvanized' should NOT match DIP pattern."""
        # "Hot-dip" is about coating process, not package type
        # "M3" doesn't match any pattern -> not_sure
        assert detect_mounting_type("M3", subcategory="Hot-dip galvanized screw") == "not_sure"


class TestNonPCBCategories:
    """Test that non-PCB categories return 'not_applicable'."""

    @pytest.mark.parametrize("category", [
        "Building materials / Building hardware",
        "Consumables and auxiliary materials",
        "Development Boards & Tools",
        "Hardware Fasteners",
        "Lathes and accessories",
        "Office Daily Use",
        "Pneumatic/hydraulic/valves/pumps",
        "Tool Equipment",
        "Wires and cables",
    ])
    def test_non_pcb_categories_return_not_applicable(self, category):
        """Non-PCB categories should return 'not_applicable' regardless of package."""
        # Even with valid package patterns, non-PCB categories return not_applicable
        assert detect_mounting_type("0402", category=category) == "not_applicable"
        assert detect_mounting_type("DIP-8", category=category) == "not_applicable"
        assert detect_mounting_type("-", category=category) == "not_applicable"

    def test_pcb_category_still_detects_mounting(self):
        """PCB categories should still detect mounting type normally."""
        assert detect_mounting_type("0402", category="Capacitors") == "smd"
        assert detect_mounting_type("DIP-8", category="Resistors") == "through_hole"
