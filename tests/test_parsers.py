"""Tests for the shared parsers module."""

import pytest

from jlcpcb_mcp.parsers import (
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
    ])
    def test_package_extraction(self, query: str, expected_package: str, expected_remaining: str):
        """Test package extraction from various queries."""
        from jlcpcb_mcp.smart_parser.packages import extract_package
        pkg, remaining, _ = extract_package(query)
        assert pkg is not None, f"Should extract package from '{query}'"
        assert pkg.upper() == expected_package.upper(), f"Expected {expected_package}, got {pkg}"
        assert remaining.strip() == expected_remaining.strip()


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
        from jlcpcb_mcp.smart_parser.semantic import remove_noise_words
        result = remove_noise_words(query)
        assert result == expected, f"'{query}' should become '{expected}', got '{result}'"
