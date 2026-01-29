"""Tests for Issue 1 (Interface OR logic) and Issue 2 (Subcategory detection)."""

import pytest
from jlcpcb_mcp.smart_parser import parse_smart_query
from jlcpcb_mcp.search.query_builder import _group_multi_value_filters
from jlcpcb_mcp.search.spec_filter import SpecFilter


class TestIssue2SubcategoryDetection:
    """Test Issue 2: Subcategory detection for temperature+humidity sensors."""

    def test_humidity_temperature_sensor(self):
        """Test 'humidity temperature sensor' maps to correct subcategory."""
        result = parse_smart_query("humidity temperature sensor I2C")
        assert result.subcategory == "temperature and humidity sensor"
        # Check that 'humidity' is not left in the remaining text
        assert "humidity" in result.remaining_text.lower() or result.remaining_text == ""

    def test_temperature_humidity_sensor(self):
        """Test 'temperature humidity sensor' maps to correct subcategory."""
        result = parse_smart_query("temperature humidity sensor I2C")
        assert result.subcategory == "temperature and humidity sensor"

    def test_temp_humidity_sensor(self):
        """Test 'temp humidity sensor' maps to correct subcategory."""
        result = parse_smart_query("temp humidity sensor")
        assert result.subcategory == "temperature and humidity sensor"

    def test_humidity_temp_sensor(self):
        """Test 'humidity temp sensor' maps to correct subcategory."""
        result = parse_smart_query("humidity temp sensor")
        assert result.subcategory == "temperature and humidity sensor"

    def test_temperature_and_humidity_sensor(self):
        """Test 'temperature and humidity sensor' maps to correct subcategory."""
        result = parse_smart_query("temperature and humidity sensor")
        assert result.subcategory == "temperature and humidity sensor"

    def test_humidity_and_temperature_sensor(self):
        """Test 'humidity and temperature sensor' maps to correct subcategory."""
        result = parse_smart_query("humidity and temperature sensor")
        assert result.subcategory == "temperature and humidity sensor"

    def test_popular_sensor_families_with_keyword(self):
        """Test popular sensor family names with 'sensor' keyword map to correct subcategory."""
        # Generic family names (DHT, BME, SHT, AHT) + "sensor" should detect subcategory
        # Note: specific model numbers like "BME280" are extracted as model numbers first
        sensor_queries = ["DHT sensor", "BME sensor", "SHT sensor", "AHT sensor"]
        for query in sensor_queries:
            result = parse_smart_query(query.lower())
            assert result.subcategory == "temperature and humidity sensor", f"Failed for {query}"

    def test_standalone_temperature_sensor_still_works(self):
        """Ensure standalone 'temperature sensor' (without humidity) still works."""
        # This should map to "temperature sensors" (not the combined category)
        # when there's no humidity keyword
        result = parse_smart_query("temperature sensor analog")
        assert result.subcategory == "temperature sensors"


class TestIssue1InterfaceOrLogic:
    """Test Issue 1: Multiple interface filters should use OR logic."""

    def test_multiple_interface_filters_grouped(self):
        """Test that multiple Interface filters are grouped together."""
        filters = [
            SpecFilter("Interface", "=", "I2C"),
            SpecFilter("Interface", "=", "SPI"),
            SpecFilter("Voltage Rating", ">=", "3.3V"),
        ]

        grouped = _group_multi_value_filters(filters)

        # Should have 2 items: 1 grouped Interface, 1 individual Voltage
        assert len(grouped) == 2

        # First item should be grouped Interface with both values
        assert isinstance(grouped[0], tuple)
        spec_name, values = grouped[0]
        assert spec_name == "Interface"
        assert set(values) == {"I2C", "SPI"}

        # Second item should be individual Voltage filter
        assert isinstance(grouped[1], SpecFilter)
        assert grouped[1].name == "Voltage Rating"

    def test_i2c_spi_query_creates_multiple_filters(self):
        """Test that 'I2C SPI' query creates multiple Interface filters."""
        result = parse_smart_query("environmental sensor I2C SPI pressure")

        # Should extract both interfaces as separate filters
        interface_filters = [f for f in result.spec_filters if f.name == "Interface"]
        assert len(interface_filters) == 2

        values = {f.value for f in interface_filters}
        assert values == {"I2C", "SPI"}

    def test_single_interface_not_grouped(self):
        """Test that a single interface filter is not wrapped in a group."""
        filters = [
            SpecFilter("Interface", "=", "I2C"),
            SpecFilter("Voltage Rating", ">=", "3.3V"),
        ]

        grouped = _group_multi_value_filters(filters)

        # Should have 2 items, both individual
        assert len(grouped) == 2
        assert all(isinstance(item, SpecFilter) for item in grouped)

    def test_multiple_same_operator_different_specs(self):
        """Test that filters with same operator but different specs aren't grouped."""
        filters = [
            SpecFilter("Interface", "=", "I2C"),
            SpecFilter("Type", "=", "Digital"),
            SpecFilter("Voltage Rating", ">=", "3.3V"),
        ]

        grouped = _group_multi_value_filters(filters)

        # Should have 3 items, all individual (no grouping across different specs)
        assert len(grouped) == 3
        assert all(isinstance(item, SpecFilter) for item in grouped)

    def test_range_operators_not_grouped(self):
        """Test that range operators (>=, <=, etc.) are never grouped."""
        filters = [
            SpecFilter("Voltage Rating", ">=", "3.3V"),
            SpecFilter("Voltage Rating", "<=", "5V"),
        ]

        grouped = _group_multi_value_filters(filters)

        # Should have 2 items, both individual (range operators don't group)
        assert len(grouped) == 2
        assert all(isinstance(item, SpecFilter) for item in grouped)

    def test_three_interface_values(self):
        """Test grouping three interface values."""
        filters = [
            SpecFilter("Interface", "=", "I2C"),
            SpecFilter("Interface", "=", "SPI"),
            SpecFilter("Interface", "=", "UART"),
        ]

        grouped = _group_multi_value_filters(filters)

        # Should have 1 grouped item with all three values
        assert len(grouped) == 1
        assert isinstance(grouped[0], tuple)
        spec_name, values = grouped[0]
        assert spec_name == "Interface"
        assert set(values) == {"I2C", "SPI", "UART"}


class TestAntennaSubcategoryDetection:
    """Test antenna subcategory detection (Issue from antenna frequency report)."""

    def test_ceramic_antenna(self):
        """Test 'ceramic antenna' correctly detects antenna subcategory."""
        result = parse_smart_query("ceramic antenna")
        assert result.subcategory == "ceramic antenna"

    def test_antenna_generic(self):
        """Test generic 'antenna' maps to antennas subcategory."""
        result = parse_smart_query("antenna 2.4GHz")
        assert result.subcategory == "antennas"

    def test_frequency_antenna_query(self):
        """Test '2.4GHz antenna' detects antenna subcategory."""
        result = parse_smart_query("2.4GHz antenna")
        assert result.subcategory == "antennas"

    def test_wifi_antenna(self):
        """Test 'wifi antenna' maps to antennas subcategory."""
        result = parse_smart_query("wifi antenna")
        assert result.subcategory == "antennas"

    def test_ble_antenna(self):
        """Test 'ble antenna' maps to antennas subcategory."""
        result = parse_smart_query("ble antenna")
        assert result.subcategory == "antennas"

    def test_pcb_antenna(self):
        """Test 'pcb antenna' maps to antennas subcategory."""
        result = parse_smart_query("pcb antenna")
        assert result.subcategory == "antennas"


class TestFrequencyMatching:
    """Test frequency filter extraction and tolerance."""

    def test_frequency_filter_extracted(self):
        """Test that frequency is correctly extracted from antenna queries."""
        result = parse_smart_query("antenna 2.4GHz")

        freq_filters = [f for f in result.spec_filters if "freq" in f.name.lower()]
        assert len(freq_filters) == 1
        assert freq_filters[0].name == "Frequency"
        assert freq_filters[0].operator == "="
        assert freq_filters[0].value == "2.4GHz"

    def test_frequency_with_ceramic_antenna(self):
        """Test frequency extraction in 'ceramic antenna 2.4GHz' query."""
        result = parse_smart_query("2.4GHz ceramic antenna")

        # Should detect ceramic antenna subcategory
        assert result.subcategory == "ceramic antenna"

        # Should extract frequency filter
        freq_filters = [f for f in result.spec_filters if "freq" in f.name.lower()]
        assert len(freq_filters) == 1
        assert freq_filters[0].value == "2.4GHz"

    def test_frequency_tolerance_calculation(self):
        """Test that 2.4GHz and 2.45GHz are within 5% tolerance."""
        from jlcpcb_mcp.parsers import parse_frequency

        f1 = parse_frequency("2.4GHz")
        f2 = parse_frequency("2.45GHz")

        # Calculate percentage difference
        diff_pct = abs(f2 - f1) / f1

        # Should be within 5% (0.05)
        assert diff_pct < 0.05, f"Difference {diff_pct*100:.2f}% exceeds 5% tolerance"

    def test_frequency_parsing_variations(self):
        """Test various frequency format parsing."""
        from jlcpcb_mcp.parsers import parse_frequency

        # All should parse correctly
        assert parse_frequency("2.4GHz") == 2.4e9
        assert parse_frequency("2.45GHz") == 2.45e9
        assert parse_frequency("2400MHz") == 2.4e9
        assert parse_frequency("5GHz") == 5e9
        assert parse_frequency("868MHz") == 868e6


class TestIntegration:
    """Integration tests combining all fixes."""

    def test_humidity_temperature_sensor_i2c_spi(self):
        """Test combined query: humidity+temperature sensor with I2C+SPI."""
        result = parse_smart_query("humidity temperature sensor I2C SPI")

        # Issue 2 fix: Should detect correct subcategory
        assert result.subcategory == "temperature and humidity sensor"

        # Issue 1 fix: Should extract both interfaces
        interface_filters = [f for f in result.spec_filters if f.name == "Interface"]
        assert len(interface_filters) == 2
        values = {f.value for f in interface_filters}
        assert values == {"I2C", "SPI"}

    def test_environmental_sensor_full_query(self):
        """Test the original problematic query from the issue report."""
        result = parse_smart_query("environmental sensor I2C SPI pressure humidity temperature")

        # Should extract both interfaces
        interface_filters = [f for f in result.spec_filters if f.name == "Interface"]
        assert len(interface_filters) == 2
        values = {f.value for f in interface_filters}
        assert values == {"I2C", "SPI"}

        # Keywords should be removed from remaining text
        remaining_lower = result.remaining_text.lower()
        assert "i2c" not in remaining_lower
        assert "spi" not in remaining_lower

    def test_antenna_with_frequency(self):
        """Test antenna query with frequency filter."""
        result = parse_smart_query("ceramic antenna 2.4GHz")

        # Should detect ceramic antenna subcategory
        assert result.subcategory == "ceramic antenna"

        # Should extract frequency filter
        freq_filters = [f for f in result.spec_filters if "freq" in f.name.lower()]
        assert len(freq_filters) == 1
        assert freq_filters[0].value == "2.4GHz"

    def test_wifi_antenna_frequency(self):
        """Test WiFi antenna query with frequency."""
        result = parse_smart_query("wifi antenna 2.4GHz")

        # Should detect antenna subcategory
        assert result.subcategory == "antennas"

        # Should extract frequency
        freq_filters = [f for f in result.spec_filters if "freq" in f.name.lower()]
        assert len(freq_filters) == 1
