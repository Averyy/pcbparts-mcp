"""Tests for sensor build pipeline — merge logic, name cleaning, enrichment."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts/ to path so we can import build_sensor_db
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from build_sensor_db import (
    SKIP_IDS,
    clean_description,
    clean_name,
    enrich_manufacturers,
    enrich_protocols,
    enrich_types,
    merge_sensors,
    normalize_manufacturer,
    resolve_id,
)


class TestCleanName:
    def test_strips_adafruit(self):
        assert "BME280" in clean_name("Adafruit BME280", "bme280")

    def test_strips_sparkfun(self):
        assert "BME280" in clean_name("SparkFun BME280", "bme280")

    def test_strips_library(self):
        result = clean_name("BME280 Library", "bme280")
        assert "Library" not in result

    def test_strips_breakout(self):
        result = clean_name("BME280 Breakout", "bme280")
        assert "Breakout" not in result

    def test_strips_leading_underscore(self):
        result = clean_name("_BME280", "bme280")
        assert not result.startswith("_")

    def test_fallback_to_id(self):
        # Disconnected name (no relation to sensor_id)
        result = clean_name("BaroLibrary", "ms5637")
        assert "MS5637" == result

    def test_strips_prefix(self):
        # "ASTRON_CCS811" should become "CCS811"
        result = clean_name("ASTRON_CCS811", "ccs811")
        assert result == "CCS811"

    def test_lowercase_gets_uppercased(self):
        result = clean_name("bmp3xx", "bmp3xx")
        assert result == "BMP3XX"

    def test_empty_name(self):
        result = clean_name("", "bme280")
        assert result == "BME280"

    def test_preserves_good_name(self):
        result = clean_name("BME280", "bme280")
        assert result == "BME280"

    def test_name_with_spaces(self):
        result = clean_name("BME280 Environmental Sensor", "bme280")
        # Should keep the descriptive part if it follows the IC name
        assert "BME280" in result


class TestCleanDescription:
    def test_strips_adafruit(self):
        result = clean_description("Adafruit BME280 sensor library")
        assert "Adafruit" not in result

    def test_strips_sparkfun(self):
        result = clean_description("SparkFun BME280 Qwiic breakout")
        assert "SparkFun" not in result


class TestNormalizeManufacturer:
    def test_maxim_to_analog_devices(self):
        assert normalize_manufacturer("Maxim") == "Analog Devices"
        assert normalize_manufacturer("Maxim Integrated") == "Analog Devices"

    def test_invensense_to_tdk(self):
        assert normalize_manufacturer("InvenSense") == "TDK"

    def test_passthrough(self):
        assert normalize_manufacturer("Bosch") == "Bosch"
        assert normalize_manufacturer("Sensirion") == "Sensirion"

    def test_none(self):
        assert normalize_manufacturer(None) is None


class TestResolveId:
    def test_alias_resolved(self):
        aliases = {"am2302": "dht22", "bme680": "bme68x"}
        assert resolve_id("am2302", aliases) == "dht22"
        assert resolve_id("bme680", aliases) == "bme68x"

    def test_no_alias(self):
        aliases = {"am2302": "dht22"}
        assert resolve_id("bme280", aliases) == "bme280"

    def test_empty_aliases(self):
        assert resolve_id("bme280", {}) == "bme280"


class TestSkipIds:
    """Verify SKIP_IDS catches known garbage entries."""

    def test_known_skips(self):
        for skip in ["pressuresensor", "i2cencoder", "kelvin2rgb", "ezopmp", "dalybms"]:
            assert skip in SKIP_IDS


class TestMergeSensors:
    """Test merge logic using temp JSON fixtures."""

    @pytest.fixture
    def sensor_data_dir(self, tmp_path):
        """Create a temp data dir with minimal source JSONs."""
        sensors_dir = tmp_path / "sensors"
        sensors_dir.mkdir()

        # IC aliases
        (sensors_dir / "ic_aliases.json").write_text(json.dumps({
            "am2302": "dht22",
        }))

        # Arduino source with DHT22 and BME280
        (sensors_dir / "arduino.json").write_text(json.dumps({
            "source": "arduino",
            "sensors": [
                {
                    "id": "dht22",
                    "name": "DHT22",
                    "measures": ["humidity", "temperature"],
                    "platforms": ["arduino"],
                    "description": "DHT22 humidity sensor",
                    "protocol": ["digital"],
                },
                {
                    "id": "bme280",
                    "name": "BME280",
                    "manufacturer": "Bosch",
                    "measures": ["humidity", "pressure", "temperature"],
                    "platforms": ["arduino"],
                    "description": "Short desc",
                    "protocol": ["i2c"],
                },
            ]
        }))

        # ESPHome source with AM2302 (alias for DHT22) and BME280
        (sensors_dir / "esphome.json").write_text(json.dumps({
            "source": "esphome",
            "sensors": [
                {
                    "id": "am2302",
                    "name": "AM2302",
                    "measures": ["humidity", "temperature"],
                    "platforms": ["esphome"],
                    "description": "AM2302/DHT22 temperature and humidity sensor for ESPHome",
                    "protocol": ["digital"],
                    "urls": ["https://esphome.io/components/sensor/dht"],
                },
                {
                    "id": "bme280",
                    "name": "BME280",
                    "measures": ["pressure", "temperature"],
                    "platforms": ["esphome"],
                    "description": "A longer description for FTS5 indexing and search",
                    "protocol": ["i2c", "spi"],
                },
            ]
        }))

        # SparkFun (tier 3) — new sensor only in breakout
        (sensors_dir / "sparkfun.json").write_text(json.dumps({
            "source": "sparkfun",
            "sensors": [
                {
                    "id": "newchip123",
                    "name": "NEWCHIP123",
                    "measures": ["light"],
                    "platforms": [],
                    "protocol": ["i2c"],
                },
            ]
        }))

        return tmp_path

    def test_alias_merge(self, sensor_data_dir):
        aliases = json.loads(
            (sensor_data_dir / "sensors" / "ic_aliases.json").read_text()
        )
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        # AM2302 should be merged into DHT22
        assert "am2302" not in merged
        assert "dht22" in merged

    def test_platforms_union(self, sensor_data_dir):
        aliases = {"am2302": "dht22"}
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        dht = merged["dht22"]
        assert "arduino" in dht["platforms"]
        assert "esphome" in dht["platforms"]

    def test_measures_union(self, sensor_data_dir):
        aliases = {}
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        bme = merged["bme280"]
        assert "humidity" in bme["measures"]
        assert "pressure" in bme["measures"]
        assert "temperature" in bme["measures"]

    def test_protocols_union(self, sensor_data_dir):
        aliases = {}
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        bme = merged["bme280"]
        assert "i2c" in bme["protocols"]
        assert "spi" in bme["protocols"]

    def test_description_longest_wins(self, sensor_data_dir):
        aliases = {}
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        bme = merged["bme280"]
        # ESPHome has the longer description
        assert len(bme["description"]) > len("Short desc")

    def test_manufacturer_preserved(self, sensor_data_dir):
        aliases = {}
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        bme = merged["bme280"]
        assert bme["manufacturer"] == "Bosch"

    def test_sources_tracked(self, sensor_data_dir):
        aliases = {"am2302": "dht22"}
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        dht = merged["dht22"]
        assert "arduino" in dht["sources"]
        assert "esphome" in dht["sources"]

    def test_url_dedup(self, sensor_data_dir):
        aliases = {"am2302": "dht22"}
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        dht = merged["dht22"]
        # ESPHome contributes a URL
        assert len(dht["urls"]) >= 1

    def test_tier3_new_entry_flagged(self, sensor_data_dir):
        aliases = {}
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        if "newchip123" in merged:
            assert merged["newchip123"]["source_tier"] == "breakout_only"

    def test_tier3_enrichment_upgrades_tier(self, sensor_data_dir):
        aliases = {}
        merged = merge_sensors(sensor_data_dir, aliases, quiet=True)

        # BME280 exists in tier 1 sources → should be "primary"
        bme = merged["bme280"]
        assert bme["source_tier"] == "primary"


class TestEnrichManufacturers:
    def test_enriches_null_manufacturer(self):
        merged = {
            "bme280": {"id": "bme280", "manufacturer": None},
            "sht3x": {"id": "sht3x", "manufacturer": "Sensirion"},
        }
        count = enrich_manufacturers(merged, quiet=True)
        # BME280 should get manufacturer from IC prefix
        assert merged["bme280"]["manufacturer"] == "Bosch"
        # SHT3X already has one — should not change
        assert merged["sht3x"]["manufacturer"] == "Sensirion"
        assert count >= 1

    def test_skips_existing(self):
        merged = {"bme280": {"id": "bme280", "manufacturer": "Already Set"}}
        enrich_manufacturers(merged, quiet=True)
        assert merged["bme280"]["manufacturer"] == "Already Set"


class TestEnrichTypes:
    def test_ic_override(self):
        merged = {
            "ccs811": {"id": "ccs811", "type": None, "measures": {"gas", "voc"}, "description": ""},
        }
        enrich_types(merged, quiet=True)
        assert merged["ccs811"]["type"] == "semiconductor"

    def test_measure_pattern(self):
        merged = {
            "custom_tof": {"id": "custom_tof", "type": None, "measures": {"distance"}, "description": "time of flight sensor"},
        }
        enrich_types(merged, quiet=True)
        assert merged["custom_tof"]["type"] == "tof"

    def test_skips_existing(self):
        merged = {"x": {"id": "x", "type": "already_set", "measures": set(), "description": ""}}
        enrich_types(merged, quiet=True)
        assert merged["x"]["type"] == "already_set"


class TestEnrichProtocols:
    def test_enriches_from_lookup(self):
        merged = {
            "bme280": {"id": "bme280", "protocols": set(), "manufacturer": "Bosch"},
        }
        enrich_protocols(merged, quiet=True)
        assert len(merged["bme280"]["protocols"]) > 0
        assert "i2c" in merged["bme280"]["protocols"]
