"""Tests for the shared parsers module."""

import pytest

from pcbparts_mcp.parsers import (
    parse_resistance,
    parse_capacitance,
    parse_voltage,
    parse_current,
    parse_tolerance,
    parse_power,
    parse_inductance,
    parse_frequency,
    parse_memory_size,
)


class TestParseResistance:
    """Tests for parse_resistance function."""

    @pytest.mark.parametrize("input_val,expected", [
        # European notation - kilo
        ("4k7", 4700),
        ("4K7", 4700),
        ("10k0", 10000),
        ("1k0", 1000),
        # European notation - ohms
        ("4R7", 4.7),
        ("4r7", 4.7),
        ("470R", 470),
        ("470r", 470),
        ("0R", 0.0),
        ("0r", 0.0),
        # European notation - mega
        ("1M5", 1500000),
        ("1m5", 1500000),
        ("2M2", 2200000),
    ])
    def test_european_notation(self, input_val: str, expected: float):
        """Test European notation parsing (4k7 = 4.7kΩ)."""
        result = parse_resistance(input_val)
        assert result == pytest.approx(expected), f"{input_val} should parse to {expected}"

    @pytest.mark.parametrize("input_val,expected", [
        # Milliohm with explicit indicator
        ("17mΩ", 0.017),
        ("17mohm", 0.017),
        ("100mΩ", 0.1),
        ("100mohm", 0.1),
        ("1mΩ", 0.001),
        ("50mOhm", 0.05),
    ])
    def test_milliohm(self, input_val: str, expected: float):
        """Test milliohm parsing."""
        result = parse_resistance(input_val)
        assert result == pytest.approx(expected), f"{input_val} should parse to {expected}"

    @pytest.mark.parametrize("input_val,expected", [
        # Standard notation
        ("10k", 10000),
        ("10K", 10000),
        ("4.7k", 4700),
        ("4.7K", 4700),
        ("100", 100),
        ("470", 470),
        ("1M", 1000000),
        ("2.2M", 2200000),
        # With Ω symbol
        ("10kΩ", 10000),
        ("100Ω", 100),
        ("1MΩ", 1000000),
        # With ohm suffix
        ("10kohm", 10000),
        ("100ohm", 100),
    ])
    def test_standard_notation(self, input_val: str, expected: float):
        """Test standard resistance notation."""
        result = parse_resistance(input_val)
        assert result == pytest.approx(expected), f"{input_val} should parse to {expected}"

    def test_jumper_zero_ohm(self):
        """Test 0R jumper resistor edge cases."""
        assert parse_resistance("0R") == 0.0
        assert parse_resistance("0r") == 0.0
        assert parse_resistance("0") == 0.0
        assert parse_resistance("0Ω") == 0.0
        assert parse_resistance("0 ohm") == 0.0

    def test_empty_returns_none(self):
        """Test empty input returns None."""
        assert parse_resistance("") is None
        assert parse_resistance(None) is None


class TestParseCapacitance:
    """Tests for parse_capacitance function."""

    @pytest.mark.parametrize("input_val,expected", [
        ("100uF", 100e-6),
        ("100µF", 100e-6),
        ("10uF", 10e-6),
        ("4.7uF", 4.7e-6),
        ("100nF", 100e-9),
        ("10nF", 10e-9),
        ("100pF", 100e-12),
        ("10pF", 10e-12),
        ("1mF", 1e-3),
    ])
    def test_capacitance_parsing(self, input_val: str, expected: float):
        """Test capacitance parsing in farads."""
        result = parse_capacitance(input_val)
        assert result == pytest.approx(expected), f"{input_val} should parse to {expected}"


class TestParseVoltage:
    """Tests for parse_voltage function."""

    @pytest.mark.parametrize("input_val,expected", [
        ("5V", 5),
        ("3.3V", 3.3),
        ("12V", 12),
        ("50V", 50),
        ("1kV", 1000),
        ("2.5kV", 2500),
        ("6.3v", 6.3),
    ])
    def test_voltage_parsing(self, input_val: str, expected: float):
        """Test voltage parsing in volts."""
        result = parse_voltage(input_val)
        assert result == pytest.approx(expected), f"{input_val} should parse to {expected}"


class TestParseCurrent:
    """Tests for parse_current function."""

    @pytest.mark.parametrize("input_val,expected", [
        ("2A", 2),
        ("5A", 5),
        ("500mA", 0.5),
        ("100mA", 0.1),
        ("100uA", 0.0001),
        ("50µA", 0.00005),
    ])
    def test_current_parsing(self, input_val: str, expected: float):
        """Test current parsing in amps."""
        result = parse_current(input_val)
        assert result == pytest.approx(expected), f"{input_val} should parse to {expected}"


class TestParseTolerance:
    """Tests for parse_tolerance function."""

    @pytest.mark.parametrize("input_val,expected", [
        ("1%", 1),
        ("5%", 5),
        ("10%", 10),
        ("0.1%", 0.1),
        ("±1%", 1),
        ("±5%", 5),
    ])
    def test_tolerance_parsing(self, input_val: str, expected: float):
        """Test tolerance parsing as percentage."""
        result = parse_tolerance(input_val)
        assert result == pytest.approx(expected), f"{input_val} should parse to {expected}"


class TestParsePower:
    """Tests for parse_power function."""

    @pytest.mark.parametrize("input_val,expected", [
        ("1W", 1),
        ("2W", 2),
        ("100mW", 0.1),
        ("250mW", 0.25),
        ("1/4W", 0.25),
        ("1/8W", 0.125),
        ("1/10W", 0.1),
    ])
    def test_power_parsing(self, input_val: str, expected: float):
        """Test power parsing in watts."""
        result = parse_power(input_val)
        assert result == pytest.approx(expected), f"{input_val} should parse to {expected}"


class TestParseMemorySize:
    """Tests for parse_memory_size function."""

    @pytest.mark.parametrize("input_val,expected", [
        ("128KB", 131072),
        ("256KB", 262144),
        ("1MB", 1048576),
        ("2MB", 2097152),
        ("128Mbit", 16777216),  # 128Mbit = 16MB
        ("64Kbit", 8192),      # 64Kbit = 8KB
    ])
    def test_memory_size_parsing(self, input_val: str, expected: float):
        """Test memory size parsing in bytes."""
        result = parse_memory_size(input_val)
        assert result == pytest.approx(expected), f"{input_val} should parse to {expected}"


class TestModelNumberExtraction:
    """Tests for model number extraction, especially compound names."""

    @pytest.mark.parametrize("query,expected_model", [
        # ESP32 compound module names
        ("ESP32-S3-MINI-1", "ESP32-S3-MINI-1"),
        ("ESP32-S3-MINI", "ESP32-S3-MINI"),
        ("ESP32-C3-MINI", "ESP32-C3-MINI"),
        ("ESP32-S3-WROOM-1", "ESP32-S3-WROOM-1"),
        ("ESP32-S3-MINI-1-N8", "ESP32-S3-MINI-1-N8"),
        ("ESP32-C3", "ESP32-C3"),
        ("ESP32-S3", "ESP32-S3"),
        # Other MCUs
        ("STM32F103C8T6", "STM32F103C8T6"),
        ("RP2040", "RP2040"),
        ("ATMEGA328P", "ATMEGA328P"),
        # Common ICs
        ("TP4056", "TP4056"),
        ("AMS1117", "AMS1117"),
        ("NE555", "NE555"),
    ])
    def test_model_extraction(self, query: str, expected_model: str):
        """Test model number extraction from various queries."""
        from pcbparts_mcp.smart_parser.models import extract_model_number
        model, remaining = extract_model_number(query)
        assert model is not None, f"Should extract model from '{query}'"
        assert model.upper() == expected_model.upper(), f"Expected {expected_model}, got {model}"

    def test_esp32_mini_not_truncated(self):
        """ESP32-S3-MINI should not be truncated to ESP32-S3."""
        from pcbparts_mcp.smart_parser.models import extract_model_number
        model, remaining = extract_model_number("ESP32-S3-MINI-1 module")
        assert model == "ESP32-S3-MINI-1", f"Expected full model name, got '{model}'"
        assert remaining.strip() == "module"


class TestPackageExtraction:
    """Tests for package extraction from queries."""

    @pytest.mark.parametrize("query,expected_package,expected_remaining", [
        # SO-8 variants (the new fix)
        ("30V N-Channel MOSFET SO-8", "SO-8", "30V N-Channel MOSFET"),
        ("mosfet SO8", "SO8", "mosfet"),
        ("SOP-8 mosfet", "SOP-8", "mosfet"),
        ("SOIC-8 driver", "SOIC-8", "driver"),
        # Other common packages
        ("10k resistor 0603", "0603", "10k resistor"),
        ("SOT-23 mosfet", "SOT-23", "mosfet"),
        ("QFN-24 mcu", "QFN-24", "mcu"),
        ("DIP-8 opamp", "DIP-8", "opamp"),
        # Package variations without hyphens (Issue #3 fix)
        ("NPN SOT23", "SOT-23", "NPN"),  # SOT23 normalizes to SOT-23
        ("SOD323 diode", "SOD-323", "diode"),  # SOD323 normalizes to SOD-323
        ("QFN32 mcu", "QFN32", "mcu"),  # QFN doesn't get hyphen added (only SOT/SOD/TO do)
    ])
    def test_package_extraction(self, query: str, expected_package: str, expected_remaining: str):
        """Test package extraction from various queries."""
        from pcbparts_mcp.smart_parser.packages import extract_package
        pkg, remaining, _ = extract_package(query)
        assert pkg is not None, f"Should extract package from '{query}'"
        assert pkg.upper() == expected_package.upper(), f"Expected {expected_package}, got {pkg}"
        assert remaining.strip() == expected_remaining.strip()


class TestModelNumberExcludesPackages:
    """Tests that package names are not detected as model numbers."""

    @pytest.mark.parametrize("query", [
        "NPN SOT23",
        "diode SOD323",
        "driver QFN32",
        "ic TSSOP20",
        "mosfet SOIC8",
        "amp DIP8",
    ])
    def test_package_not_detected_as_model(self, query: str):
        """Package-like strings (SOT23, SOD323, etc.) should NOT be detected as model numbers."""
        from pcbparts_mcp.smart_parser.models import extract_model_number
        model, _ = extract_model_number(query)
        # The package-like string should not be extracted as a model
        if model:
            # If something was extracted, it shouldn't be the package
            package_like = ("SOT", "SOD", "SOP", "SOIC", "QFN", "DFN", "TSSOP", "DIP")
            model_upper = model.upper()
            for prefix in package_like:
                assert not (model_upper.startswith(prefix) and len(model_upper) > len(prefix) and model_upper[len(prefix):].replace("L", "").isdigit()), \
                    f"'{model}' looks like a package and should not be detected as model number"


class TestNoiseWordRemoval:
    """Tests for noise word removal from queries."""

    @pytest.mark.parametrize("query,expected", [
        # Connector terms should be removed
        ("USB-C receptacle", "USB-C"),
        ("USB-C jack", "USB-C"),
        ("USB-C plug", "USB-C"),
        # Generic words should be removed
        ("resistor for power supply", "resistor power supply"),
        ("capacitor with high voltage", "capacitor high voltage"),
    ])
    def test_noise_word_removal(self, query: str, expected: str):
        """Test that noise words are removed from queries."""
        from pcbparts_mcp.smart_parser.semantic import remove_noise_words
        result = remove_noise_words(query)
        assert result == expected, f"'{query}' should become '{expected}', got '{result}'"


class TestFerritBeadImpedance:
    """Tests for ferrite bead impedance parsing."""

    @pytest.mark.parametrize("query,expected_impedance", [
        ("30 ohm ferrite bead 0603", "30Ohm"),
        ("ferrite bead 0603 30", "30Ohm"),
        ("ferrite bead 100 0402", "100Ohm"),
        ("120 ferrite bead", "120Ohm"),
        ("600 ohm ferrite 0603", "600Ohm"),
    ])
    def test_ferrite_impedance_parsing(self, query: str, expected_impedance: str):
        """Test that ferrite bead impedance is parsed from various formats."""
        from pcbparts_mcp.smart_parser.parser import parse_smart_query
        result = parse_smart_query(query)
        assert result.subcategory == "ferrite beads"
        impedance_filters = [f for f in result.spec_filters if "Impedance" in f.name]
        assert len(impedance_filters) == 1, f"Expected 1 impedance filter, got {len(impedance_filters)}"
        assert impedance_filters[0].value == expected_impedance


class TestConnectorSeriesExtraction:
    """Tests for JST connector series and brand alias extraction."""

    @pytest.mark.parametrize("query,expected_series,expected_pitch", [
        # JST series patterns
        ("jst sh 4-pin", "SH", 1.0),
        ("jst-sh connector", "SH", 1.0),
        ("JST SH 1mm 4P", "SH", 1.0),
        ("jst ph battery", "PH", 2.0),
        ("jst xh connector", "XH", 2.5),
        ("jst gh 6pin", "GH", 1.25),
        ("jst zh 1.5mm", "ZH", 1.5),
    ])
    def test_jst_series_extraction(self, query: str, expected_series: str, expected_pitch: float):
        """Test JST series detection and pitch mapping."""
        from pcbparts_mcp.smart_parser.connectors import extract_connector_series
        spec, remaining = extract_connector_series(query)
        assert spec is not None, f"Should detect series in '{query}'"
        assert spec.series == expected_series, f"Expected series {expected_series}, got {spec.series}"
        assert spec.pitch == pytest.approx(expected_pitch), f"Expected pitch {expected_pitch}mm, got {spec.pitch}mm"

    @pytest.mark.parametrize("query,expected_series,expected_pitch,expected_pins", [
        # Brand aliases
        ("qwiic connector", "SH", 1.0, 4),
        ("Qwiic", "SH", 1.0, 4),
        ("stemma qt", "SH", 1.0, 4),
        ("STEMMA QT connector", "SH", 1.0, 4),
        ("easyc connector", "SH", 1.0, 4),
        ("easyC", "SH", 1.0, 4),
        # STEMMA (original, larger) - no pin count
        ("stemma connector", "PH", 2.0, None),
    ])
    def test_brand_alias_expansion(self, query: str, expected_series: str, expected_pitch: float, expected_pins: int | None):
        """Test brand alias expansion (Qwiic, STEMMA QT, easyC)."""
        from pcbparts_mcp.smart_parser.connectors import extract_connector_series
        spec, remaining = extract_connector_series(query)
        assert spec is not None, f"Should detect brand in '{query}'"
        assert spec.series == expected_series, f"Expected series {expected_series}, got {spec.series}"
        assert spec.pitch == pytest.approx(expected_pitch), f"Expected pitch {expected_pitch}mm"
        assert spec.pins == expected_pins, f"Expected pins {expected_pins}, got {spec.pins}"

    def test_no_connector_series(self):
        """Test that non-connector queries return None."""
        from pcbparts_mcp.smart_parser.connectors import extract_connector_series
        spec, remaining = extract_connector_series("10k resistor 0603")
        assert spec is None
        assert remaining == "10k resistor 0603"


class TestConnectorParserIntegration:
    """Tests for connector series integration in the main parser.

    Connector info is stored in connector_spec (not spec_filters) and the
    series name is injected into remaining_text for FTS search.
    """

    def test_jst_sh_4pin_adds_connector_spec(self):
        """JST SH 4-pin should populate connector_spec and inject SH into FTS."""
        from pcbparts_mcp.smart_parser.parser import parse_smart_query
        result = parse_smart_query("jst sh 4-pin")
        assert result.subcategory == "wire to board connector"
        assert result.connector_spec is not None
        assert result.connector_spec.series == "SH"
        assert result.connector_spec.pitch == 1.0
        # FTS includes SH (case-insensitive — already present in "jst sh 4-pin")
        assert "sh" in result.remaining_text.lower()

    def test_qwiic_expands_to_jst_sh(self):
        """Qwiic should expand to JST SH with pitch and pin info."""
        from pcbparts_mcp.smart_parser.parser import parse_smart_query
        result = parse_smart_query("qwiic connector")
        assert result.subcategory == "wire to board connector"
        assert result.connector_spec is not None
        assert result.connector_spec.series == "SH"
        assert result.connector_spec.pitch == 1.0
        assert result.connector_spec.pins == 4
        # FTS includes SH (injected by parser since "qwiic" doesn't contain "sh")
        assert "sh" in result.remaining_text.lower()

    def test_easyc_same_as_qwiic(self):
        """easyC should expand the same as Qwiic."""
        from pcbparts_mcp.smart_parser.parser import parse_smart_query
        result = parse_smart_query("easyc")
        assert result.subcategory == "wire to board connector"
        assert result.connector_spec is not None
        assert result.connector_spec.series == "SH"
        assert result.connector_spec.pitch == 1.0
        assert result.connector_spec.pins == 4
