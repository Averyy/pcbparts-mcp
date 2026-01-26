"""Tests for the alternatives module - spec parsing and compatibility checking."""

import pytest

from jlcpcb_mcp.alternatives import (
    # Parsers
    parse_voltage,
    parse_tolerance,
    parse_power,
    parse_current,
    parse_resistance,
    parse_capacitance,
    parse_inductance,
    parse_frequency,
    parse_impedance_at_freq,
    impedance_at_freq_match,
    # Compatibility functions
    _values_match,
    _spec_ok,
    is_compatible_alternative,
    verify_primary_spec_match,
    score_alternative,
    COMPATIBILITY_RULES,
)


# =============================================================================
# PARSER TESTS
# =============================================================================


class TestParseVoltage:
    """Tests for parse_voltage function."""

    def test_simple_voltage(self):
        assert parse_voltage("25V") == 25.0
        assert parse_voltage("6.3V") == 6.3
        assert parse_voltage("3.3V") == 3.3
        assert parse_voltage("50V") == 50.0

    def test_with_spaces(self):
        assert parse_voltage("25 V") == 25.0
        assert parse_voltage("6.3 V") == 6.3

    def test_case_insensitive(self):
        assert parse_voltage("25v") == 25.0
        assert parse_voltage("25V") == 25.0

    def test_invalid(self):
        assert parse_voltage("") is None
        assert parse_voltage(None) is None  # type: ignore
        assert parse_voltage("abc") is None


class TestParseTolerance:
    """Tests for parse_tolerance function."""

    def test_with_plus_minus(self):
        assert parse_tolerance("±1%") == 1.0
        assert parse_tolerance("±10%") == 10.0
        assert parse_tolerance("±0.5%") == 0.5

    def test_without_plus_minus(self):
        assert parse_tolerance("1%") == 1.0
        assert parse_tolerance("5%") == 5.0

    def test_invalid(self):
        assert parse_tolerance("") is None
        assert parse_tolerance("abc") is None


class TestParsePower:
    """Tests for parse_power function."""

    def test_watts(self):
        assert parse_power("1W") == 1.0
        assert parse_power("0.25W") == 0.25
        assert parse_power("2.5W") == 2.5

    def test_milliwatts(self):
        assert parse_power("100mW") == 0.1
        assert parse_power("250mW") == 0.25

    def test_fractions(self):
        assert parse_power("1/4W") == 0.25
        assert parse_power("1/10W") == 0.1
        assert parse_power("1/2W") == 0.5

    def test_invalid(self):
        assert parse_power("") is None
        assert parse_power("abc") is None


class TestParseCurrent:
    """Tests for parse_current function."""

    def test_amps(self):
        assert parse_current("2A") == 2.0
        assert parse_current("0.5A") == 0.5

    def test_milliamps(self):
        assert parse_current("500mA") == 0.5
        assert parse_current("100mA") == 0.1

    def test_microamps(self):
        assert parse_current("100uA") == 0.0001
        assert parse_current("100µA") == 0.0001

    def test_invalid(self):
        assert parse_current("") is None
        assert parse_current("abc") is None


class TestParseResistance:
    """Tests for parse_resistance function."""

    def test_ohms(self):
        assert parse_resistance("10Ω") == 10.0
        assert parse_resistance("100") == 100.0
        assert parse_resistance("4.7Ω") == 4.7

    def test_kilohms(self):
        assert parse_resistance("10kΩ") == 10000.0
        assert parse_resistance("10K") == 10000.0
        assert parse_resistance("4.7k") == 4700.0

    def test_megohms(self):
        assert parse_resistance("1MΩ") == 1_000_000.0
        assert parse_resistance("4.7M") == 4_700_000.0

    def test_invalid(self):
        assert parse_resistance("") is None
        assert parse_resistance("abc") is None


class TestParseCapacitance:
    """Tests for parse_capacitance function."""

    def test_picofarads(self):
        assert parse_capacitance("100pF") == pytest.approx(100e-12)
        assert parse_capacitance("10p") == pytest.approx(10e-12)

    def test_nanofarads(self):
        assert parse_capacitance("100nF") == pytest.approx(100e-9)
        assert parse_capacitance("10n") == pytest.approx(10e-9)

    def test_microfarads(self):
        assert parse_capacitance("10uF") == pytest.approx(10e-6)
        assert parse_capacitance("10µF") == pytest.approx(10e-6)
        assert parse_capacitance("100u") == pytest.approx(100e-6)

    def test_millifarads(self):
        assert parse_capacitance("1mF") == pytest.approx(1e-3)

    def test_invalid(self):
        assert parse_capacitance("") is None


class TestParseInductance:
    """Tests for parse_inductance function."""

    def test_nanohenries(self):
        assert parse_inductance("100nH") == pytest.approx(100e-9)

    def test_microhenries(self):
        assert parse_inductance("10uH") == pytest.approx(10e-6)
        assert parse_inductance("10µH") == pytest.approx(10e-6)

    def test_millihenries(self):
        assert parse_inductance("1mH") == pytest.approx(1e-3)

    def test_invalid(self):
        assert parse_inductance("") is None


class TestParseFrequency:
    """Tests for parse_frequency function."""

    def test_hertz(self):
        assert parse_frequency("100Hz") == 100.0
        assert parse_frequency("100") == 100.0

    def test_kilohertz(self):
        assert parse_frequency("32.768kHz") == pytest.approx(32768.0)
        assert parse_frequency("100KHz") == pytest.approx(100000.0)

    def test_megahertz(self):
        assert parse_frequency("8MHz") == pytest.approx(8e6)
        assert parse_frequency("16MHz") == pytest.approx(16e6)

    def test_gigahertz(self):
        assert parse_frequency("2.4GHz") == pytest.approx(2.4e9)

    def test_invalid(self):
        assert parse_frequency("") is None


class TestParseDecibels:
    """Tests for parse_decibels function."""

    def test_simple_db(self):
        from jlcpcb_mcp.alternatives import parse_decibels
        assert parse_decibels("85dB") == 85.0
        assert parse_decibels("90 dB") == 90.0
        assert parse_decibels("75.5dB") == 75.5

    def test_invalid(self):
        from jlcpcb_mcp.alternatives import parse_decibels
        assert parse_decibels("") is None
        assert parse_decibels("loud") is None


class TestParserEdgeCases:
    """Tests for parser edge cases and ambiguous inputs."""

    def test_resistance_zero(self):
        assert parse_resistance("0") == 0.0
        assert parse_resistance("0Ω") == 0.0

    def test_resistance_with_extra_text(self):
        # Should extract resistance from longer strings
        assert parse_resistance("10kΩ ±1%") == 10000.0

    def test_capacitance_with_extra_text(self):
        # Should extract capacitance from longer strings
        assert parse_capacitance("100nF ±5%") == pytest.approx(100e-9)

    def test_voltage_zero(self):
        assert parse_voltage("0V") == 0.0

    def test_current_zero(self):
        assert parse_current("0A") == 0.0

    def test_power_zero(self):
        assert parse_power("0W") == 0.0


class TestParseImpedanceAtFreq:
    """Tests for parse_impedance_at_freq function."""

    def test_standard_format(self):
        result = parse_impedance_at_freq("600Ω @ 100MHz")
        assert result is not None
        assert result[0] == pytest.approx(600.0)
        assert result[1] == pytest.approx(100e6)

    def test_kiloohm_format(self):
        result = parse_impedance_at_freq("1kOhm @ 100MHz")
        assert result is not None
        assert result[0] == pytest.approx(1000.0)
        assert result[1] == pytest.approx(100e6)

    def test_invalid(self):
        assert parse_impedance_at_freq("") is None
        assert parse_impedance_at_freq("just some text") is None


class TestImpedanceAtFreqMatch:
    """Tests for impedance_at_freq_match function."""

    def test_matching(self):
        assert impedance_at_freq_match("600Ω @ 100MHz", "600Ω @ 100MHz") is True

    def test_slightly_different_within_tolerance(self):
        # 1% difference should pass
        assert impedance_at_freq_match("600Ω @ 100MHz", "606Ω @ 100MHz") is True

    def test_different_impedance(self):
        assert impedance_at_freq_match("600Ω @ 100MHz", "1200Ω @ 100MHz") is False

    def test_different_frequency(self):
        assert impedance_at_freq_match("600Ω @ 100MHz", "600Ω @ 200MHz") is False


# =============================================================================
# COMPATIBILITY FUNCTION TESTS
# =============================================================================


class TestValuesMatch:
    """Tests for _values_match function."""

    def test_resistance_match(self):
        assert _values_match("10kΩ", "10kΩ", "Resistance") is True
        assert _values_match("10kΩ", "10K", "Resistance") is True  # Same value, different format
        assert _values_match("10kΩ", "20kΩ", "Resistance") is False

    def test_string_match_spec(self):
        assert _values_match("X7R", "X7R", "Temperature Coefficient") is True
        assert _values_match("x7r", "X7R", "Temperature Coefficient") is True  # Case insensitive
        assert _values_match("X7R", "X5R", "Temperature Coefficient") is False

    def test_color_match(self):
        assert _values_match("Red", "red", "Illumination Color") is True
        assert _values_match("Red", "Blue", "Illumination Color") is False

    def test_voltage_match_with_tolerance(self):
        # 2% tolerance for numeric specs
        assert _values_match("25V", "25V", "Voltage Rating") is True
        assert _values_match("25V", "25.4V", "Voltage Rating") is True  # Within 2%
        assert _values_match("25V", "30V", "Voltage Rating") is False


class TestSpecOk:
    """Tests for _spec_ok function."""

    def test_higher_is_better(self):
        # Voltage rating: higher is better
        assert _spec_ok("25V", "50V", "Voltage Rating", "higher") is True
        assert _spec_ok("50V", "25V", "Voltage Rating", "higher") is False

    def test_lower_is_better(self):
        # Tolerance: lower is better
        assert _spec_ok("5%", "1%", "Tolerance", "lower") is True
        assert _spec_ok("1%", "5%", "Tolerance", "lower") is False

    def test_tolerance_margin(self):
        # 2% tolerance in comparison
        assert _spec_ok("10V", "9.9V", "Voltage Rating", "higher") is True  # Within tolerance


class TestIsCompatibleAlternative:
    """Tests for is_compatible_alternative function."""

    def test_resistor_compatible(self):
        original = {
            "key_specs": {
                "Resistance": "10kΩ",
                "Tolerance": "5%",
                "Power(Watts)": "1/4W",
            }
        }
        candidate = {
            "key_specs": {
                "Resistance": "10kΩ",
                "Tolerance": "1%",  # Better tolerance
                "Power(Watts)": "1/2W",  # Higher power
            }
        }
        is_compat, info = is_compatible_alternative(
            original, candidate, "Chip Resistor - Surface Mount"
        )
        assert is_compat is True
        assert "Tolerance" in info["specs_verified"]
        assert "Power(Watts)" in info["specs_verified"]

    def test_resistor_incompatible_tolerance(self):
        original = {
            "key_specs": {
                "Resistance": "10kΩ",
                "Tolerance": "1%",  # Tight tolerance
                "Power(Watts)": "1/4W",
            }
        }
        candidate = {
            "key_specs": {
                "Resistance": "10kΩ",
                "Tolerance": "5%",  # Worse tolerance - should fail
                "Power(Watts)": "1/4W",
            }
        }
        is_compat, _ = is_compatible_alternative(
            original, candidate, "Chip Resistor - Surface Mount"
        )
        assert is_compat is False

    def test_capacitor_must_match_dielectric(self):
        original = {
            "key_specs": {
                "Capacitance": "100nF",
                "Voltage Rating": "25V",
                "Temperature Coefficient": "X7R",
            }
        }
        # X5R dielectric should fail
        candidate = {
            "key_specs": {
                "Capacitance": "100nF",
                "Voltage Rating": "50V",
                "Temperature Coefficient": "X5R",  # Different dielectric
            }
        }
        is_compat, _ = is_compatible_alternative(
            original, candidate, "Multilayer Ceramic Capacitors MLCC - SMD/SMT"
        )
        assert is_compat is False

    def test_capacitor_compatible_higher_voltage(self):
        original = {
            "key_specs": {
                "Capacitance": "100nF",
                "Voltage Rating": "25V",
                "Temperature Coefficient": "X7R",
                "Tolerance": "10%",
            }
        }
        candidate = {
            "key_specs": {
                "Capacitance": "100nF",
                "Voltage Rating": "50V",  # Higher voltage - OK
                "Temperature Coefficient": "X7R",  # Same dielectric
                "Tolerance": "5%",  # Better tolerance
            }
        }
        is_compat, info = is_compatible_alternative(
            original, candidate, "Multilayer Ceramic Capacitors MLCC - SMD/SMT"
        )
        assert is_compat is True

    def test_led_must_match_color(self):
        original = {"key_specs": {"Illumination Color": "Red"}}
        candidate = {"key_specs": {"Illumination Color": "Blue"}}
        is_compat, _ = is_compatible_alternative(
            original, candidate, "LED Indication - Discrete"
        )
        assert is_compat is False

    def test_unsupported_category_passes(self):
        # For unsupported categories, always returns True
        original = {"key_specs": {"Some Spec": "value"}}
        candidate = {"key_specs": {"Some Spec": "different"}}
        is_compat, info = is_compatible_alternative(
            original, candidate, "Unknown Category That Does Not Exist"
        )
        assert is_compat is True
        assert info["specs_verified"] == []


class TestVerifyPrimarySpecMatch:
    """Tests for verify_primary_spec_match function."""

    def test_resistance_match(self):
        original = {"key_specs": {"Resistance": "10kΩ"}}
        candidate = {"key_specs": {"Resistance": "10kΩ"}}
        assert verify_primary_spec_match(original, candidate, "Resistance") is True

    def test_resistance_mismatch(self):
        original = {"key_specs": {"Resistance": "10kΩ"}}
        candidate = {"key_specs": {"Resistance": "20kΩ"}}
        assert verify_primary_spec_match(original, candidate, "Resistance") is False

    def test_missing_spec_passes(self):
        # If we can't verify, we allow through
        original = {"key_specs": {"Resistance": "10kΩ"}}
        candidate = {"key_specs": {}}  # Missing spec
        assert verify_primary_spec_match(original, candidate, "Resistance") is True


class TestScoreAlternative:
    """Tests for score_alternative function."""

    def test_basic_library_gets_high_score(self):
        part = {"library_type": "basic", "stock": 10000, "price": 0.01}
        original = {"manufacturer": "Other"}
        score, breakdown = score_alternative(part, original, 0.01)
        assert breakdown["library_type"] == 1000
        assert score >= 1000

    def test_extended_library_low_score(self):
        part = {"library_type": "extended", "stock": 10000, "price": 0.01}
        original = {"manufacturer": "Other"}
        score, breakdown = score_alternative(part, original, 0.01)
        assert breakdown["library_type"] == 0

    def test_high_stock_bonus(self):
        part = {"library_type": "extended", "stock": 50000, "price": 0.01}
        original = {"manufacturer": "Other"}
        _, breakdown = score_alternative(part, original, 0.01)
        assert breakdown["availability"] == 70  # Excellent availability

    def test_same_manufacturer_bonus(self):
        part = {"library_type": "extended", "stock": 1000, "price": 0.01, "manufacturer": "Samsung"}
        original = {"manufacturer": "Samsung"}
        _, breakdown = score_alternative(part, original, 0.01)
        assert breakdown["same_manufacturer"] == 10


# =============================================================================
# COMPATIBILITY RULES COVERAGE
# =============================================================================


class TestCompatibilityRulesCoverage:
    """Ensure key component types have compatibility rules defined."""

    def test_resistors_covered(self):
        assert "Chip Resistor - Surface Mount" in COMPATIBILITY_RULES
        assert "Through Hole Resistors" in COMPATIBILITY_RULES

    def test_capacitors_covered(self):
        assert "Multilayer Ceramic Capacitors MLCC - SMD/SMT" in COMPATIBILITY_RULES
        assert "Aluminum Electrolytic Capacitors - SMD" in COMPATIBILITY_RULES
        assert "Tantalum Capacitors" in COMPATIBILITY_RULES

    def test_inductors_covered(self):
        assert "Inductors (SMD)" in COMPATIBILITY_RULES
        assert "Power Inductors" in COMPATIBILITY_RULES
        assert "Ferrite Beads" in COMPATIBILITY_RULES

    def test_semiconductors_covered(self):
        assert "MOSFETs" in COMPATIBILITY_RULES
        assert "Bipolar (BJT)" in COMPATIBILITY_RULES
        assert "Schottky Diodes" in COMPATIBILITY_RULES
        assert "Zener Diodes" in COMPATIBILITY_RULES

    def test_leds_covered(self):
        assert "LED Indication - Discrete" in COMPATIBILITY_RULES
        assert "LED - High Brightness" in COMPATIBILITY_RULES

    def test_timing_covered(self):
        assert "Crystals" in COMPATIBILITY_RULES
        assert "Crystal Oscillators" in COMPATIBILITY_RULES

    def test_switches_covered(self):
        assert "Tactile Switches" in COMPATIBILITY_RULES
        assert "Toggle Switches" in COMPATIBILITY_RULES

    def test_connectors_covered(self):
        assert "Pin Headers" in COMPATIBILITY_RULES
        assert "USB Connectors" in COMPATIBILITY_RULES


# =============================================================================
# INTEGRATION TESTS (require API calls)
# =============================================================================


class TestFindAlternativesIntegration:
    """Integration tests that hit the real JLCPCB API."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        from jlcpcb_mcp.client import JLCPCBClient
        return JLCPCBClient()

    @pytest.mark.asyncio
    async def test_resistor_alternatives(self, client):
        """Test finding alternatives for a 10k resistor."""
        # C25804 is a common 10kΩ 0603 resistor
        result = await client.find_alternatives("C25804", limit=5)
        await client.close()

        assert "error" not in result
        assert "original" in result
        assert result["original"]["lcsc"] == "C25804"

        # Should be a supported category
        if "alternatives" in result and len(result["alternatives"]) > 0:
            # All alternatives should have same resistance
            for alt in result["alternatives"]:
                key_specs = alt.get("key_specs", {})
                resistance = key_specs.get("Resistance", "")
                # Should contain "10k" or "10000" or similar
                if resistance:
                    parsed = parse_resistance(resistance)
                    assert parsed is not None
                    assert parsed == pytest.approx(10000, rel=0.02)

    @pytest.mark.asyncio
    async def test_capacitor_alternatives(self, client):
        """Test finding alternatives for a 100nF capacitor."""
        # C1525 is a common 100nF 0402 X7R capacitor
        result = await client.find_alternatives("C1525", limit=5)
        await client.close()

        assert "error" not in result
        assert "original" in result

        # Check summary
        if "summary" in result:
            assert "is_supported_category" in result["summary"]

    @pytest.mark.asyncio
    async def test_led_alternatives(self, client):
        """Test finding alternatives for an LED."""
        # C2286 is a common red LED
        result = await client.find_alternatives("C2286", limit=5)
        await client.close()

        assert "error" not in result

        # If alternatives found, they should all be red LEDs
        if "alternatives" in result:
            for alt in result["alternatives"]:
                color = alt.get("key_specs", {}).get("Illumination Color", "").lower()
                # Color should match (red) or be empty (couldn't parse)
                if color:
                    assert "red" in color

    @pytest.mark.asyncio
    async def test_unsupported_category_returns_similar_parts(self, client):
        """Test that unsupported categories return similar_parts instead of alternatives."""
        # C7466 is an STM32 MCU (unsupported category)
        result = await client.find_alternatives("C7466", limit=5)
        await client.close()

        assert "error" not in result

        # Should indicate it's unsupported
        if "summary" in result:
            assert result["summary"].get("is_supported_category") is False

        # Should have similar_parts instead of alternatives
        if "similar_parts" in result:
            assert isinstance(result["similar_parts"], list)

    @pytest.mark.asyncio
    async def test_invalid_part_returns_error(self, client):
        """Test that invalid part codes return an error."""
        result = await client.find_alternatives("INVALID123")
        await client.close()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_library_type_filter(self, client):
        """Test filtering by library type."""
        result = await client.find_alternatives("C25804", library_type="no_fee", limit=5)
        await client.close()

        assert "error" not in result

        # All alternatives should be basic or preferred
        if "alternatives" in result:
            for alt in result["alternatives"]:
                lib_type = alt.get("library_type")
                assert lib_type in ("basic", "preferred") or lib_type is None

    @pytest.mark.asyncio
    async def test_scoring_prefers_basic_library(self, client):
        """Test that scoring prioritizes basic/preferred library parts."""
        result = await client.find_alternatives("C25804", limit=10)
        await client.close()

        assert "error" not in result

        # Check that basic/preferred parts are ranked higher
        if "alternatives" in result and len(result["alternatives"]) >= 2:
            alternatives = result["alternatives"]
            # First alternative should have higher or equal score than last
            if "score" in alternatives[0] and "score" in alternatives[-1]:
                assert alternatives[0]["score"] >= alternatives[-1]["score"]
