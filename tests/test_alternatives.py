"""Tests for the alternatives module - spec parsing and compatibility checking."""

import gzip
import json
from pathlib import Path

import pytest

from pcbparts_mcp.alternatives import (
    # Parsers
    parse_voltage,
    parse_tolerance,
    parse_ppm,
    parse_forward_voltage,
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
    build_response,
    COMPATIBILITY_RULES,
)

SUBCATEGORIES_FILE = Path(__file__).parent.parent / "data" / "subcategories.json"


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

    def test_kilovolts(self):
        assert parse_voltage("5kV") == 5000.0
        assert parse_voltage("3.75kV") == 3750.0
        assert parse_voltage("1.5 kV") == 1500.0

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


class TestParsePpm:
    """Tests for parse_ppm function."""

    def test_with_plus_minus(self):
        assert parse_ppm("±20ppm") == 20.0
        assert parse_ppm("±10ppm") == 10.0
        assert parse_ppm("±50ppm") == 50.0

    def test_without_plus_minus(self):
        assert parse_ppm("20ppm") == 20.0
        assert parse_ppm("30ppm") == 30.0

    def test_with_space(self):
        assert parse_ppm("20 ppm") == 20.0
        assert parse_ppm("±10 ppm") == 10.0

    def test_case_insensitive(self):
        assert parse_ppm("20PPM") == 20.0
        assert parse_ppm("20Ppm") == 20.0

    def test_invalid(self):
        assert parse_ppm("") is None
        assert parse_ppm("abc") is None
        assert parse_ppm("20%") is None


class TestParseForwardVoltage:
    """Tests for parse_forward_voltage function."""

    def test_millivolt_format(self):
        assert parse_forward_voltage("550mV@3A") == 0.55
        assert parse_forward_voltage("350mV@1A") == 0.35
        assert parse_forward_voltage("600 mV @ 2A") == 0.6

    def test_volt_format(self):
        assert parse_forward_voltage("1V@100mA") == 1.0
        assert parse_forward_voltage("1.2V@20mA") == 1.2
        assert parse_forward_voltage("3.3V@10mA") == 3.3

    def test_invalid(self):
        assert parse_forward_voltage("") is None
        assert parse_forward_voltage("abc") is None


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
        from pcbparts_mcp.alternatives import parse_decibels
        assert parse_decibels("85dB") == 85.0
        assert parse_decibels("90 dB") == 90.0
        assert parse_decibels("75.5dB") == 75.5

    def test_invalid(self):
        from pcbparts_mcp.alternatives import parse_decibels
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
            "specs": {
                "Resistance": "10kΩ",
                "Tolerance": "5%",
                "Power(Watts)": "1/4W",
            }
        }
        candidate = {
            "specs": {
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
            "specs": {
                "Resistance": "10kΩ",
                "Tolerance": "1%",  # Tight tolerance
                "Power(Watts)": "1/4W",
            }
        }
        candidate = {
            "specs": {
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
            "specs": {
                "Capacitance": "100nF",
                "Voltage Rating": "25V",
                "Temperature Coefficient": "X7R",
            }
        }
        # X5R dielectric should fail
        candidate = {
            "specs": {
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
            "specs": {
                "Capacitance": "100nF",
                "Voltage Rating": "25V",
                "Temperature Coefficient": "X7R",
                "Tolerance": "10%",
            }
        }
        candidate = {
            "specs": {
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
        original = {"specs": {"Illumination Color": "Red"}}
        candidate = {"specs": {"Illumination Color": "Blue"}}
        is_compat, _ = is_compatible_alternative(
            original, candidate, "LED Indication - Discrete"
        )
        assert is_compat is False

    def test_unsupported_category_passes(self):
        # For unsupported categories, always returns True
        original = {"specs": {"Some Spec": "value"}}
        candidate = {"specs": {"Some Spec": "different"}}
        is_compat, info = is_compatible_alternative(
            original, candidate, "Unknown Category That Does Not Exist"
        )
        assert is_compat is True
        assert info["specs_verified"] == []


class TestVerifyPrimarySpecMatch:
    """Tests for verify_primary_spec_match function."""

    def test_resistance_match(self):
        original = {"specs": {"Resistance": "10kΩ"}}
        candidate = {"specs": {"Resistance": "10kΩ"}}
        assert verify_primary_spec_match(original, candidate, "Resistance") is True

    def test_resistance_mismatch(self):
        original = {"specs": {"Resistance": "10kΩ"}}
        candidate = {"specs": {"Resistance": "20kΩ"}}
        assert verify_primary_spec_match(original, candidate, "Resistance") is False

    def test_missing_spec_passes(self):
        # If we can't verify, we allow through
        original = {"specs": {"Resistance": "10kΩ"}}
        candidate = {"specs": {}}  # Missing spec
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
        assert "Infrared LED Emitters" in COMPATIBILITY_RULES

    def test_every_rule_names_a_jlcpcb_subcategory(self):
        """A rule keyed by a name JLCPCB doesn't use never applies ("LED - High Brightness",
        "Infrared (IR) LEDs" and "Light Bars, Arrays" sat unused from v1.10.1 to 0.6.4)."""
        names = {info["name"] for info in json.loads(SUBCATEGORIES_FILE.read_text(encoding="utf-8")).values()}
        assert sorted(set(COMPATIBILITY_RULES) - names) == []

    def test_timing_covered(self):
        assert "Crystals" in COMPATIBILITY_RULES
        assert "Crystal Oscillators" in COMPATIBILITY_RULES

    def test_switches_covered(self):
        assert "Tactile Switches" in COMPATIBILITY_RULES
        assert "Toggle Switches" in COMPATIBILITY_RULES

    def test_connectors_covered(self):
        assert "Pin Headers" in COMPATIBILITY_RULES
        assert "USB Connectors" in COMPATIBILITY_RULES


def _mosfet(type_=None, number=None, vds="60V", id_="83A", rds="12mΩ@10V"):
    specs = {"Drain to Source Voltage": vds, "Current - Continuous Drain(Id)": id_, "RDS(on)": rds}
    if type_ is not None:
        specs["Type"] = type_
    if number is not None:
        specs["Number"] = number
    return {"specs": specs}


class TestPolarity:
    """Transistors must keep N/P (NPN/PNP) and the count; until 0.6.5 MOSFETs never checked it."""

    def test_p_channel_cant_replace_n_channel(self):
        ok, _ = is_compatible_alternative(_mosfet("N-Channel", "1 N-channel"), _mosfet("P-Channel", "1 P-Channel"), "MOSFETs")
        assert ok is False

    def test_same_channel_passes_and_is_reported(self):
        ok, info = is_compatible_alternative(
            _mosfet("N-Channel", "1 N-channel"), _mosfet("N-Channel", "1 N-Channel", id_="100A"), "MOSFETs"
        )
        assert ok is True
        assert "polarity" in info["specs_verified"]

    def test_dual_cant_replace_single(self):
        ok, _ = is_compatible_alternative(_mosfet("N-Channel", "1 N-channel"), _mosfet("N-Channel", "2 N-Channel"), "MOSFETs")
        assert ok is False

    def test_polarity_from_number_alone(self):
        """5,703 MOSFETs state polarity only in Number (1,241 P-channel)."""
        assert is_compatible_alternative(_mosfet("N-Channel"), _mosfet(number="1 P-Channel"), "MOSFETs")[0] is False
        assert is_compatible_alternative(_mosfet("N-Channel"), _mosfet(number="1 n-channel"), "MOSFETs")[0] is True

    def test_candidate_that_doesnt_say_is_rejected(self):
        assert is_compatible_alternative(_mosfet("N-Channel"), _mosfet(), "MOSFETs")[0] is False
        assert is_compatible_alternative(_mosfet("N-Channel"), _mosfet("-", "-"), "MOSFETs")[0] is False

    def test_conflicting_specs_count_as_unknown(self):
        assert is_compatible_alternative(_mosfet("N-Channel"), _mosfet("P-Channel", "1 n-channel"), "MOSFETs")[0] is False

    def test_original_without_polarity_cant_be_checked(self):
        ok, info = is_compatible_alternative(_mosfet(), _mosfet("P-Channel"), "MOSFETs")
        assert ok is True
        assert "polarity" in info["specs_unparseable"]

    def test_complementary_pair(self):
        orig = _mosfet("N-Channel + P-Channel", "1 N-Channel + 1 P-Channel")
        assert is_compatible_alternative(orig, _mosfet("N-Channel + P-Channel"), "MOSFETs")[0] is True
        assert is_compatible_alternative(orig, _mosfet("N-Channel", "1 N-channel"), "MOSFETs")[0] is False

    def test_digital_transistor_number_formats(self):
        """Original states polarity only in Number, candidate only in type."""
        orig = {"specs": {"type": "-", "Number": "1 NPN (Pre-Biased)"}}
        assert is_compatible_alternative(orig, {"specs": {"type": "PNP"}}, "Digital Transistors")[0] is False
        assert is_compatible_alternative(orig, {"specs": {"Number": "1 NPN Pre-Biased"}}, "Digital Transistors")[0] is True

    def test_logic_level_mosfet_needs_logic_level_alternative(self):
        """IRFZ44N (Vgs(th) 4V) was offered for the logic-level IRLZ34N (1V)."""
        orig = _mosfet("N-Channel", vds="55V", id_="30A", rds="46mΩ@5V")
        orig["specs"]["Gate Threshold Voltage (Vgs(th))"] = "1V"
        cand = _mosfet("N-Channel", vds="55V", id_="49A", rds="17.5mΩ@10V")
        cand["specs"]["Gate Threshold Voltage (Vgs(th))"] = "4V"
        assert is_compatible_alternative(orig, cand, "MOSFETs")[0] is False

    def test_bjt(self):
        orig = {"specs": {"type": "NPN", "Number": "1 NPN"}}
        assert is_compatible_alternative(orig, {"specs": {"type": "NPN", "Number": "2 NPN"}}, "Bipolar (BJT)")[0] is False
        assert is_compatible_alternative(orig, {"specs": {"Number": "1 NPN"}}, "Bipolar (BJT)")[0] is True


class TestUncheckableSpecs:
    def test_original_placeholder_doesnt_demand_a_placeholder(self):
        """An original whose dielectric is "-" used to match only candidates whose dielectric is "-"."""
        orig = {"specs": {"Capacitance": "100nF", "Temperature Coefficient": "-"}}
        cand = {"specs": {"Capacitance": "100nF", "Temperature Coefficient": "X7R"}}
        ok, info = is_compatible_alternative(orig, cand, "Multilayer Ceramic Capacitors MLCC - SMD/SMT")
        assert ok is True
        assert "Temperature Coefficient" in info["specs_unparseable"]
        assert verify_primary_spec_match({"specs": {"type": "-"}}, {"specs": {"type": "NPN"}}, "type") is True

    def test_unparseable_numeric_match_isnt_verified(self):
        """A Zener whose voltage is "-" used to count as verified."""
        ok, info = is_compatible_alternative(
            {"specs": {"Zener Voltage(Nom)": "5.1V"}}, {"specs": {"Zener Voltage(Nom)": "-"}}, "Zener Diodes"
        )
        assert ok is True
        assert "Zener Voltage(Nom)" in info["specs_unparseable"]
        assert "Zener Voltage(Nom)" not in info["specs_verified"]

    def test_primary_is_reported(self):
        orig = {"specs": {"Capacitance": "100nF", "Temperature Coefficient": "X7R"}}
        ok, info = is_compatible_alternative(orig, dict(orig), "Multilayer Ceramic Capacitors MLCC - SMD/SMT")
        assert ok is True
        assert "Capacitance" in info["specs_verified"]

    def test_primary_mismatch_rejected(self):
        orig = {"specs": {"Capacitance": "100nF"}}
        cand = {"specs": {"Capacitance": "10nF"}}
        assert is_compatible_alternative(orig, cand, "Multilayer Ceramic Capacitors MLCC - SMD/SMT")[0] is False

    def test_no_duplicate_entries(self):
        _, info = is_compatible_alternative(_mosfet("N-Channel"), _mosfet("N-Channel"), "MOSFETs")
        assert info["specs_verified"].count("Drain to Source Voltage") == 1


class TestSpecNamesJlcpcbUses:
    """Rules that named specs JLCPCB doesn't use never checked them."""

    def test_tvs_peak_pulse_power(self):
        orig = {"specs": {"Reverse Stand-Off Voltage (Vrwm)": "5V", "Peak Pulse Power Dissipation (Ppp)": "1.5kW@10/1000us"}}
        cand = {"specs": {"Reverse Stand-Off Voltage (Vrwm)": "5V", "Peak Pulse Power Dissipation (Ppp)": "400W@10/1000us"}}
        assert is_compatible_alternative(orig, cand, "ESD and Surge Protection (TVS/ESD)")[0] is False

    def test_gdt_spark_over_voltage(self):
        orig = {"specs": {"Voltage - DC Spark Over (Nom)": "600V", "Number of Poles": "2"}}
        cand = {"specs": {"Voltage - DC Spark Over (Nom)": "90V", "Number of Poles": "2"}}
        assert is_compatible_alternative(orig, cand, "Gas Discharge Tube Arresters (GDT)")[0] is False

    def test_gdt_impulse_current_in_ka(self):
        orig = {"specs": {"Voltage - DC Spark Over (Nom)": "90V", "Impulse Discharge Current": "10kA"}}
        cand = {"specs": {"Voltage - DC Spark Over (Nom)": "90V", "Impulse Discharge Current": "5kA"}}
        assert is_compatible_alternative(orig, cand, "Gas Discharge Tube Arresters (GDT)")[0] is False

    def test_digital_isolator_bare_number_isolation_voltage(self):
        orig = {"specs": {"Number of Forward Channels": "2", "Isolation Voltage(Vrms)": "5000"}}
        cand = {"specs": {"Number of Forward Channels": "2", "Isolation Voltage(Vrms)": "2500"}}
        assert is_compatible_alternative(orig, cand, "Digital Isolators")[0] is False

    def test_ldo_dropout_in_mv(self):
        orig = {"specs": {"Output Voltage": "3.3V", "Voltage Dropout": "100mV@(100mA)"}}
        cand = {"specs": {"Output Voltage": "3.3V", "Voltage Dropout": "350mV@(100mA)"}}
        assert is_compatible_alternative(orig, cand, "Voltage Regulators - Linear, Low Drop Out (LDO) Regulators")[0] is False

    def test_wifi_output_power_in_dbm(self):
        orig = {"specs": {"Voltage - Supply": "3.3V", "Output Power": "20dBm"}}
        cand = {"specs": {"Voltage - Supply": "3.3V", "Output Power": "16dBm"}}
        assert is_compatible_alternative(orig, cand, "WiFi Modules")[0] is False

    def test_tvs_polarity(self):
        """A unidirectional TVS was offered for the bidirectional SMCJ36CA."""
        orig = {"specs": {"Reverse Stand-Off Voltage (Vrwm)": "36V", "Polarity": "Bidirectional", "Type": "TVS"}}
        uni = {"specs": {"Reverse Stand-Off Voltage (Vrwm)": "36V", "Polarity": "Unidirectional", "Type": "TVS"}}
        esd = {"specs": {"Reverse Stand-Off Voltage (Vrwm)": "36V", "Polarity": "Bidirectional", "Type": "ESD"}}
        assert is_compatible_alternative(orig, uni, "ESD and Surge Protection (TVS/ESD)")[0] is False
        assert is_compatible_alternative(orig, esd, "ESD and Surge Protection (TVS/ESD)")[0] is False

    def test_diode_configuration(self):
        """BAT54C (common cathode) and single diodes were offered for the BAT54S (series pair)."""
        orig = {"specs": {"Voltage - DC Reverse(Vr)": "30V", "Diode Configuration": "1 Pair Series Connection"}}
        cc = {"specs": {"Voltage - DC Reverse(Vr)": "30V", "Diode Configuration": "1 Pair Common Cathode"}}
        assert is_compatible_alternative(orig, cc, "Schottky Diodes")[0] is False
        single = {"specs": {"Voltage - DC Reverse(Vr)": "30V", "Diode Configuration": "1 Independent"}}
        standalone = {"specs": {"Voltage - DC Reverse(Vr)": "30V", "Diode Configuration": "Standalone"}}
        assert is_compatible_alternative(single, standalone, "Schottky Diodes")[0] is True

    def test_c0g_is_np0(self):
        """The basic 47pF C0G (C1671) wasn't offered for a 47pF NP0."""
        orig = {"specs": {"Capacitance": "47pF", "Temperature Coefficient": "NP0"}}
        cand = {"specs": {"Capacitance": "47pF", "Temperature Coefficient": "C0G"}}
        assert is_compatible_alternative(orig, cand, "Multilayer Ceramic Capacitors MLCC - SMD/SMT")[0] is True
        x7r = {"specs": {"Capacitance": "47pF", "Temperature Coefficient": "X7R"}}
        assert is_compatible_alternative(orig, x7r, "Multilayer Ceramic Capacitors MLCC - SMD/SMT")[0] is False

    def test_coax_series_and_gender(self):
        """U.FL (IPEX) connectors were offered for an SMA jack."""
        orig = {"specs": {"Connector Type": "Board Side", "Impedance": "50Ω", "RF Series": "SMA", "Interface": "Inner hole"}}
        ipex = {"specs": {"Connector Type": "Board Side", "Impedance": "50Ω", "RF Series": "IPEX", "Interface": "Inner pin"}}
        plug = {"specs": {"Connector Type": "Board Side", "Impedance": "50Ω", "RF Series": "SMA", "Interface": "Male Pin"}}
        jack = {"specs": {"Connector Type": "Board Side", "Impedance": "50Ω", "RF Series": "SMA", "Interface": "Inner Bore"}}
        assert is_compatible_alternative(orig, ipex, "Coaxial Connectors (RF)")[0] is False
        assert is_compatible_alternative(orig, plug, "Coaxial Connectors (RF)")[0] is False
        assert is_compatible_alternative(orig, jack, "Coaxial Connectors (RF)")[0] is True

    def test_module_chip(self):
        orig = {"specs": {"Voltage - Supply": "3V~3.6V", "Utilized IC / Part": "ESP32-S3R8"}}
        c3 = {"specs": {"Voltage - Supply": "3V~3.6V", "Utilized IC / Part": "ESP32-C3FH4"}}
        assert is_compatible_alternative(orig, c3, "WiFi Modules")[0] is False
        # Some listings spell D0WD with a letter O
        wroom = {"specs": {"Voltage - Supply": "3V~3.6V", "Utilized IC / Part": "ESP32-D0WD-V3、ESP32-D0WDR2-V3"}}
        typo = {"specs": {"Voltage - Supply": "3V~3.6V", "Utilized IC / Part": "ESP32-DOWD-V3、ESP32-DOWDR2-V3"}}
        assert is_compatible_alternative(wroom, typo, "WiFi Modules")[0] is True

    def test_buzzer_sound_pressure(self):
        orig = {"specs": {"Voltage - Supply": "5V", "Sound Pressure Level(SPL)": "85dB"}}
        cand = {"specs": {"Voltage - Supply": "5V", "Sound Pressure Level(SPL)": "70dB"}}
        assert is_compatible_alternative(orig, cand, "Buzzers")[0] is False


class TestConditionalSpecs:
    """Dropout, Vf and RDS(on) depend on the test condition after the "@"."""

    def _ok(self, orig, cand, spec="RDS(on)"):
        from pcbparts_mcp.alternatives import _conditional_ok
        return _conditional_ok(orig, cand, spec)

    def test_compares_at_a_shared_condition(self):
        assert self._ok("12mΩ@10V", "15mΩ@4.5V、10mΩ@10V") is True
        assert self._ok("12mΩ@10V", "8mΩ@4.5V、14mΩ@10V") is False

    def test_higher_value_still_fails(self):
        assert self._ok("12mΩ@10V", "15mΩ@4.5V") is False
        assert self._ok("240mV@(50mA)", "300mV@(300mA)", "Voltage Dropout") is False

    def test_lower_value_at_harder_condition_is_better(self):
        assert self._ok("12mΩ@10V", "8mΩ@4.5V") is True
        assert self._ok("240mV@(50mA)", "120mV@(100mA)", "Voltage Dropout") is True
        assert self._ok("550mV@1A", "500mV@3A", "Voltage - Forward(Vf@If)") is True

    def test_lower_value_at_easier_condition_proves_nothing(self):
        assert self._ok("12mΩ@4.5V", "11mΩ@10V") is None
        assert self._ok("240mV@(100mA)", "200mV@(10mA)", "Voltage Dropout") is None

    def test_no_condition_compares_values(self):
        assert self._ok("1.7V", "1.1V@(800mA)", "Voltage Dropout") is True
        assert self._ok("1.1V@(800mA)", "1.7V", "Voltage Dropout") is False

    def test_in_the_rules(self):
        ok, info = is_compatible_alternative(
            _mosfet("N-Channel", rds="12mΩ@4.5V"), _mosfet("N-Channel", rds="11mΩ@10V"), "MOSFETs"
        )
        assert ok is True
        assert "RDS(on)" in info["specs_unparseable"]


class TestSummaryMessage:
    def _message(self, original_lib, alt_libs, primary_value="10kΩ"):
        alts = [(0, {"lcsc": f"C{i}", "library_type": lib}, {}, {"specs_verified": [], "specs_unparseable": []})
                for i, lib in enumerate(alt_libs)]
        return build_response({"library_type": original_lib}, alts, "Chip Resistor - Surface Mount",
                              "Resistance", primary_value, 5)["summary"]["message"]

    def test_saving_only_claimed_for_an_extended_original(self):
        assert "save $3" in self._message("extended", ["basic"])
        assert "save $3" not in self._message("basic", ["basic"])

    def test_no_primary_value(self):
        assert self._message("extended", [], primary_value=None) == "No compatible alternatives found"


# =============================================================================
# DATABASE CANDIDATES (find_alternatives' second source)
# =============================================================================


def _row(lcsc, stock, lib="e", **specs):
    return {"l": lcsc, "m": f"MPN-{lcsc}", "f": "TestCorp", "p": "TO-220", "s": stock, "t": lib,
            "c": 2954, "$": 0.5, "d": lcsc, "a": [[k, v] for k, v in specs.items()]}


C2557 = {
    "lcsc": "C2557", "subcategory": "MOSFETs", "package": "TO-220AB", "library_type": "extended",
    "price": 0.93, "stock": 6313, "manufacturer": "Infineon Technologies",
    "specs": {"Drain to Source Voltage": "60V", "Current - Continuous Drain(Id)": "83A",
              "RDS(on)": "12mΩ@10V", "Type": "N-Channel", "Number": "1 N-channel"},
}

N60 = {"Drain to Source Voltage": "60V", "Type": "N-Channel", "Number": "1 N-channel"}


@pytest.fixture
def mosfet_db(tmp_path):
    """A components DB with a 60V MOSFET mix: small-signal parts with the most stock, then power parts."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from build_database import build_database
    from pcbparts_mcp.db import ComponentDatabase

    rows = [_row(f"C1{i:03}", 100000 - i, "b", **N60, **{"Current - Continuous Drain(Id)": "300mA", "RDS(on)": "3Ω@10V"})
            for i in range(80)]
    rows += [
        _row("C2001", 500, "e", **N60, **{"Current - Continuous Drain(Id)": "100A", "RDS(on)": "8mΩ@10V"}),
        _row("C2002", 900, "e", **{**N60, "Type": "P-Channel", "Number": "1 P-Channel"},
             **{"Current - Continuous Drain(Id)": "100A", "RDS(on)": "8mΩ@10V"}),
        _row("C2003", 300, "p", **N60, **{"Current - Continuous Drain(Id)": "90A", "RDS(on)": "11mΩ@10V"}),
        _row("C2004", 800, "e", **{**N60, "Drain to Source Voltage": "100V"},
             **{"Current - Continuous Drain(Id)": "100A", "RDS(on)": "8mΩ@10V"}),
        _row("C2005", 700, "e", **N60, **{"Current - Continuous Drain(Id)": "82A", "RDS(on)": "12mΩ@10V"}),  # within 2%
        _row("C2006", 5, "e", **N60, **{"Current - Continuous Drain(Id)": "100A", "RDS(on)": "8mΩ@10V"}),  # stock < 10
        _row("C2007", 200, "b", **N60, **{"Current - Continuous Drain(Id)": "90A", "RDS(on)": "10mΩ@10V"}),
    ]
    (tmp_path / "categories").mkdir()
    with gzip.open(tmp_path / "categories" / "transistors.jsonl.gz", "wt") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    (tmp_path / "subcategories.json").write_text(json.dumps(
        {"2954": {"name": "MOSFETs", "category_id": 1, "category_name": "Transistors/Thyristors"}}))
    build_database(tmp_path, tmp_path / "components.db", verbose=False)
    db = ComponentDatabase(db_path=tmp_path / "components.db", data_dir=tmp_path)
    yield db
    db.close()


class TestAlternativeCandidates:
    def test_only_parts_that_meet_the_numbers(self, mosfet_db):
        found = mosfet_db.find_alternative_candidates(C2557, "MOSFETs", 2954, limit=10)
        # 60V within 2%, Id >= 83A (less 2%), RDS(on) <= 12mΩ (plus 2%); no-fee first, then stock.
        # C2002 (P-channel) passes SQL; the polarity check is the caller's accept()
        assert [p["lcsc"] for p in found] == ["C2003", "C2007", "C2002", "C2005", "C2001"]

    def test_accept_picks_in_order(self, mosfet_db):
        found = mosfet_db.find_alternative_candidates(
            C2557, "MOSFETs", 2954, limit=2, accept=lambda p: p["specs"].get("Type") == "N-Channel"
        )
        assert [p["lcsc"] for p in found] == ["C2003", "C2007"]

    def test_library_type(self, mosfet_db):
        found = mosfet_db.find_alternative_candidates(C2557, "MOSFETs", 2954, library_type="no_fee")
        assert [p["lcsc"] for p in found] == ["C2003", "C2007"]

    def test_unsupported_subcategory(self, mosfet_db):
        assert mosfet_db.find_alternative_candidates(C2557, "Not A Rule", 2954) == []

    async def test_find_alternatives_uses_them(self, mosfet_db, monkeypatch):
        """C2557 found nothing: its live candidates were 60V small-signal parts that fail Id and RDS(on)."""
        from pcbparts_mcp.client import JLCPCBClient

        client = JLCPCBClient()
        client.set_alternative_candidates(mosfet_db.find_alternative_candidates)
        small = [{"lcsc": f"C1{i:03}", "package": "SOT-23", "library_type": "basic", "price": 0.01,
                  "stock": 100000 - i, "specs": {**N60, "Current - Continuous Drain(Id)": "300mA", "RDS(on)": "3Ω@10V"}}
                 for i in range(50)]

        async def get_part(lcsc):
            return json.loads(json.dumps(C2557))

        async def search(**kwargs):
            return {"results": [dict(p) for p in small]}

        async def ensure_categories():
            return None

        monkeypatch.setattr(client, "get_part", get_part)
        monkeypatch.setattr(client, "search", search)
        monkeypatch.setattr(client, "_ensure_categories", ensure_categories)
        monkeypatch.setattr(client, "get_subcategory_id_by_name", lambda name: 2954)

        result = await client.find_alternatives("C2557", limit=5)
        assert [a["lcsc"] for a in result["alternatives"]] == ["C2003", "C2007", "C2005", "C2001"]
        assert all("polarity" in a["specs_verified"] for a in result["alternatives"])

        result = await client.find_alternatives("C2557", library_type="preferred", limit=5)
        assert [a["lcsc"] for a in result["alternatives"]] == ["C2003"]


# =============================================================================
# INTEGRATION TESTS (require API calls)
# =============================================================================


@pytest.mark.integration
class TestFindAlternativesIntegration:
    """Integration tests that hit the real JLCPCB API."""

    @pytest.fixture(scope="class")
    async def client(self):
        """Create a shared client for integration tests.

        Class-scoped so all tests share one wafer session (accumulated cookies,
        proper rate limiting).
        """
        from pcbparts_mcp.client import JLCPCBClient
        client = JLCPCBClient()
        yield client
        await client.close()

    @pytest.mark.asyncio
    async def test_resistor_alternatives(self, client):
        """Test finding alternatives for a 10k resistor."""
        # C25804 is a common 10kΩ 0603 resistor
        result = await client.find_alternatives("C25804", limit=5)

        assert "error" not in result
        assert "original" in result
        assert result["original"]["lcsc"] == "C25804"

        # Should be a supported category
        if "alternatives" in result and len(result["alternatives"]) > 0:
            # All alternatives should have same resistance
            for alt in result["alternatives"]:
                specs = alt.get("specs", {})
                resistance = specs.get("Resistance", "")
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

        assert "error" not in result

        # If alternatives found, they should all be red LEDs
        if "alternatives" in result:
            for alt in result["alternatives"]:
                color = alt.get("specs", {}).get("Illumination Color", "").lower()
                # Color should match (red) or be empty (couldn't parse)
                if color:
                    assert "red" in color

    @pytest.mark.asyncio
    async def test_unsupported_category_returns_similar_parts(self, client):
        """Test that unsupported categories return similar_parts instead of alternatives."""
        # C7466 is an STM32 MCU (unsupported category)
        result = await client.find_alternatives("C7466", limit=5)

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

        assert "error" in result

    @pytest.mark.asyncio
    async def test_library_type_filter(self, client):
        """Test filtering by library type."""
        result = await client.find_alternatives("C25804", library_type="no_fee", limit=5)

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

        assert "error" not in result

        # Check that basic/preferred parts are ranked higher
        if "alternatives" in result and len(result["alternatives"]) >= 2:
            alternatives = result["alternatives"]
            # First alternative should have higher or equal score than last
            if "score" in alternatives[0] and "score" in alternatives[-1]:
                assert alternatives[0]["score"] >= alternatives[-1]["score"]
