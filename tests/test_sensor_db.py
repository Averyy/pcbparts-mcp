"""Tests for sensor database search module.

Uses a small in-memory test database built from fixtures to test the
query builder, FTS5, parametric filters, and measure aliases.
"""

import json
import sqlite3

import pytest

from pcbparts_mcp.sensor_db.search import (
    MEASURE_EXPANSIONS,
    MEASURE_QUERY_ALIASES,
    PROTOCOL_ALIASES,
    _resolve_measure,
    _sanitize_fts_query,
    search_sensors,
)

# Schema matching the real sensor.db
SCHEMA = """
CREATE TABLE sensors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    manufacturer TEXT,
    type TEXT,
    voltage TEXT,
    datasheet_url TEXT,
    platform_count INTEGER DEFAULT 0,
    description TEXT,
    source_tier TEXT DEFAULT 'primary',
    sources TEXT
);
CREATE TABLE sensor_measures (
    sensor_id TEXT NOT NULL REFERENCES sensors(id),
    measure TEXT NOT NULL,
    PRIMARY KEY (sensor_id, measure)
);
CREATE TABLE sensor_protocols (
    sensor_id TEXT NOT NULL REFERENCES sensors(id),
    protocol TEXT NOT NULL,
    PRIMARY KEY (sensor_id, protocol)
);
CREATE TABLE sensor_platforms (
    sensor_id TEXT NOT NULL REFERENCES sensors(id),
    platform TEXT NOT NULL,
    PRIMARY KEY (sensor_id, platform)
);
CREATE TABLE sensor_urls (
    sensor_id TEXT NOT NULL REFERENCES sensors(id),
    url TEXT NOT NULL,
    PRIMARY KEY (sensor_id, url)
);
CREATE VIRTUAL TABLE sensors_fts USING fts5(id, name, manufacturer, description);
"""

# Test fixture data
FIXTURES = [
    {
        "id": "bme280",
        "name": "BME280",
        "manufacturer": "Bosch",
        "type": "mems",
        "voltage": "1.8-3.6",
        "platform_count": 7,
        "description": "Combined humidity, pressure, and temperature sensor",
        "source_tier": "primary",
        "measures": ["humidity", "pressure", "temperature"],
        "protocols": ["i2c", "spi"],
        "platforms": ["arduino", "circuitpython", "esphome", "micropython", "tasmota", "zephyr", "raspberry_pi"],
        "urls": ["https://esphome.io/components/sensor/bme280"],
    },
    {
        "id": "scd4x",
        "name": "SCD4X",
        "manufacturer": "Sensirion",
        "type": "photoacoustic",
        "voltage": "2.4-5.5",
        "platform_count": 7,
        "description": "CO2 humidity and temperature sensor",
        "source_tier": "primary",
        "measures": ["co2", "humidity", "temperature"],
        "protocols": ["i2c"],
        "platforms": ["arduino", "circuitpython", "esphome", "micropython", "tasmota", "zephyr", "raspberry_pi"],
        "urls": [],
    },
    {
        "id": "mpu6050",
        "name": "MPU6050",
        "manufacturer": "TDK",
        "type": "mems",
        "voltage": "2.375-3.46",
        "platform_count": 6,
        "description": "Six-axis accelerometer and gyroscope MEMS IMU sensor",
        "source_tier": "primary",
        "measures": ["acceleration", "gyroscope", "temperature"],
        "protocols": ["i2c"],
        "platforms": ["arduino", "circuitpython", "esphome", "micropython", "tasmota", "zephyr"],
        "urls": [],
    },
    {
        "id": "ds18b20",
        "name": "DS18B20",
        "manufacturer": "Analog Devices",
        "type": None,
        "voltage": "3.0-5.5",
        "platform_count": 5,
        "description": "Waterproof digital temperature sensor one wire",
        "source_tier": "primary",
        "measures": ["temperature"],
        "protocols": ["one_wire"],
        "platforms": ["arduino", "esphome", "micropython", "tasmota", "zephyr"],
        "urls": [],
    },
    {
        "id": "mhz19",
        "name": "MHZ19",
        "manufacturer": "Winsen",
        "type": "ndir",
        "voltage": "4.5-5.5",
        "platform_count": 4,
        "description": "NDIR CO2 gas sensor module with UART interface",
        "source_tier": "primary",
        "measures": ["co2", "gas", "temperature"],
        "protocols": ["uart"],
        "platforms": ["arduino", "esphome", "micropython", "tasmota"],
        "urls": [],
    },
    {
        "id": "vl53l0x",
        "name": "VL53L0X",
        "manufacturer": "STMicroelectronics",
        "type": "tof",
        "voltage": "2.6-3.5",
        "platform_count": 5,
        "description": "Time of flight distance ranging sensor",
        "source_tier": "primary",
        "measures": ["distance"],
        "protocols": ["i2c"],
        "platforms": ["arduino", "circuitpython", "esphome", "micropython", "zephyr"],
        "urls": [],
    },
    {
        "id": "breakout1",
        "name": "BREAKOUT1",
        "manufacturer": None,
        "type": None,
        "voltage": None,
        "platform_count": 0,
        "description": "SparkFun only breakout sensor for light detection",
        "source_tier": "breakout_only",
        "measures": ["light"],
        "protocols": ["analog"],
        "platforms": [],
        "urls": [],
    },
]


@pytest.fixture(scope="module")
def test_db():
    """Build a small in-memory test database from fixtures."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)

    for s in FIXTURES:
        conn.execute(
            "INSERT INTO sensors (id, name, manufacturer, type, voltage, datasheet_url, platform_count, description, source_tier, sources) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (s["id"], s["name"], s["manufacturer"], s["type"], s["voltage"], None, s["platform_count"], s["description"], s["source_tier"], json.dumps(["test"])),
        )
        conn.execute(
            "INSERT INTO sensors_fts (id, name, manufacturer, description) VALUES (?, ?, ?, ?)",
            (s["id"], s["name"], s["manufacturer"] or "", s["description"]),
        )
        for m in s["measures"]:
            conn.execute("INSERT INTO sensor_measures VALUES (?, ?)", (s["id"], m))
        for p in s["protocols"]:
            conn.execute("INSERT INTO sensor_protocols VALUES (?, ?)", (s["id"], p))
        for pl in s["platforms"]:
            conn.execute("INSERT INTO sensor_platforms VALUES (?, ?)", (s["id"], pl))
        for u in s["urls"]:
            conn.execute("INSERT INTO sensor_urls VALUES (?, ?)", (s["id"], u))

    conn.commit()
    yield conn
    conn.close()


class TestFTSSanitize:
    def test_basic_query(self):
        assert _sanitize_fts_query("BME280") == '"BME280"*'

    def test_multi_term(self):
        assert _sanitize_fts_query("temperature humidity") == '"temperature"* AND "humidity"*'

    def test_stop_words_filtered(self):
        """Stop words like 'and', 'sensor' are filtered from FTS queries."""
        assert _sanitize_fts_query("temperature and humidity") == '"temperature"* AND "humidity"*'
        assert _sanitize_fts_query("give me all temperature sensors") == '"temperature"*'

    def test_strips_quotes(self):
        assert _sanitize_fts_query('"test"') == '"test"*'

    def test_skips_short_terms(self):
        assert _sanitize_fts_query("a temperature") == '"temperature"*'

    def test_empty(self):
        assert _sanitize_fts_query("") == ""

    def test_prefix_match_format(self):
        """Prefix matching uses FTS5 "term"* syntax."""
        result = _sanitize_fts_query("BM22S")
        assert result == '"BM22S"*'


class TestResolveMeasure:
    def test_imu_expansion(self):
        measures, mode = _resolve_measure("imu")
        assert mode == "or"
        assert set(measures) == {"acceleration", "gyroscope", "magnetic_field"}

    def test_voc_passthrough(self):
        """VOC is a real measure in the DB, not aliased to 'gas'."""
        measures, mode = _resolve_measure("voc")
        assert mode == "single"
        assert measures == ["voc"]

    def test_alias_barometric(self):
        measures, mode = _resolve_measure("barometric")
        assert measures == ["pressure"]

    def test_passthrough(self):
        measures, mode = _resolve_measure("co2")
        assert mode == "single"
        assert measures == ["co2"]

    def test_case_insensitive(self):
        measures, _ = _resolve_measure("IMU")
        assert set(measures) == {"acceleration", "gyroscope", "magnetic_field"}


class TestSearchFTS:
    def test_fts_by_name(self, test_db):
        result = search_sensors(test_db, query="BME280")
        assert result["total"] >= 1
        assert result["results"][0]["id"] == "bme280"

    def test_fts_by_description(self, test_db):
        result = search_sensors(test_db, query="waterproof")
        assert result["total"] >= 1
        assert result["results"][0]["id"] == "ds18b20"

    def test_fts_by_manufacturer(self, test_db):
        result = search_sensors(test_db, query="Bosch")
        assert result["total"] >= 1
        assert any(r["id"] == "bme280" for r in result["results"])

    def test_fts_no_results(self, test_db):
        result = search_sensors(test_db, query="nonexistentsensor12345")
        assert result["total"] == 0
        assert result["results"] == []

    def test_fts_natural_language(self, test_db):
        """Natural language queries filter stop words ('and', 'sensor', etc.)."""
        result = search_sensors(test_db, query="find a good temperature and humidity sensor")
        assert result["total"] >= 1
        assert any(r["id"] == "bme280" for r in result["results"])

    def test_fts_prefix_match(self, test_db):
        """FTS5 prefix matching: 'BME' matches 'BME280'."""
        result = search_sensors(test_db, query="BME")
        assert result["total"] >= 1
        assert any(r["id"] == "bme280" for r in result["results"])

    def test_fts_prefix_partial_model(self, test_db):
        """FTS5 prefix matching: 'VL53' matches 'VL53L0X'."""
        result = search_sensors(test_db, query="VL53")
        assert result["total"] >= 1
        assert any(r["id"] == "vl53l0x" for r in result["results"])

    def test_id_like_fallback(self, test_db):
        """ID LIKE fallback: 'mhz' matches sensor id 'mhz19'."""
        result = search_sensors(test_db, query="mhz")
        assert result["total"] >= 1
        assert any(r["id"] == "mhz19" for r in result["results"])


class TestSearchMeasure:
    def test_single_measure(self, test_db):
        result = search_sensors(test_db, measure="co2")
        assert result["total"] >= 2  # scd4x, mhz19
        ids = {r["id"] for r in result["results"]}
        assert "scd4x" in ids
        assert "mhz19" in ids

    def test_multi_measure_and(self, test_db):
        result = search_sensors(test_db, measure=["temperature", "pressure"])
        assert result["total"] >= 1
        # BME280 has both
        assert any(r["id"] == "bme280" for r in result["results"])
        # DS18B20 only has temperature (no pressure) — should NOT be included
        assert all(r["id"] != "ds18b20" for r in result["results"])

    def test_imu_expansion(self, test_db):
        result = search_sensors(test_db, measure="imu")
        assert result["total"] >= 1
        # MPU6050 has acceleration + gyroscope
        assert any(r["id"] == "mpu6050" for r in result["results"])

    def test_measure_alias(self, test_db):
        result = search_sensors(test_db, measure="barometric")
        # Should resolve to pressure
        assert result["total"] >= 1
        assert any(r["id"] == "bme280" for r in result["results"])

    def test_list_single_item(self, test_db):
        result = search_sensors(test_db, measure=["distance"])
        assert result["total"] >= 1
        assert any(r["id"] == "vl53l0x" for r in result["results"])


class TestSearchProtocol:
    def test_i2c(self, test_db):
        result = search_sensors(test_db, protocol="i2c")
        ids = {r["id"] for r in result["results"]}
        assert "bme280" in ids
        assert "scd4x" in ids
        assert "mhz19" not in ids  # uart only

    def test_uart(self, test_db):
        result = search_sensors(test_db, protocol="uart")
        ids = {r["id"] for r in result["results"]}
        assert "mhz19" in ids
        assert "bme280" not in ids

    def test_gpio_expansion(self, test_db):
        result = search_sensors(test_db, protocol="gpio")
        # Should expand to analog, digital, pwm, one_wire
        ids = {r["id"] for r in result["results"]}
        assert "ds18b20" in ids  # one_wire
        assert "breakout1" in ids  # analog


class TestSearchPlatform:
    def test_filter_platform(self, test_db):
        result = search_sensors(test_db, platform="circuitpython")
        ids = {r["id"] for r in result["results"]}
        assert "bme280" in ids
        assert "mhz19" not in ids  # not on circuitpython

    def test_zephyr(self, test_db):
        result = search_sensors(test_db, platform="zephyr")
        assert result["total"] >= 1
        ids = {r["id"] for r in result["results"]}
        assert "bme280" in ids


class TestSearchType:
    def test_filter_type(self, test_db):
        result = search_sensors(test_db, type="ndir")
        assert result["total"] >= 1
        assert result["results"][0]["id"] == "mhz19"

    def test_tof(self, test_db):
        result = search_sensors(test_db, type="tof")
        assert result["total"] >= 1
        assert any(r["id"] == "vl53l0x" for r in result["results"])

    def test_mems(self, test_db):
        result = search_sensors(test_db, type="mems")
        ids = {r["id"] for r in result["results"]}
        assert "bme280" in ids
        assert "mpu6050" in ids


class TestSearchCombined:
    def test_measure_plus_protocol(self, test_db):
        result = search_sensors(test_db, measure="co2", protocol="uart")
        ids = {r["id"] for r in result["results"]}
        assert "mhz19" in ids
        assert "scd4x" not in ids  # i2c only

    def test_measure_plus_platform(self, test_db):
        result = search_sensors(test_db, measure="temperature", platform="circuitpython")
        ids = {r["id"] for r in result["results"]}
        assert "bme280" in ids
        # ds18b20 is not on circuitpython in fixtures
        assert "ds18b20" not in ids

    def test_fts_plus_measure(self, test_db):
        result = search_sensors(test_db, query="waterproof", measure="temperature")
        assert result["total"] >= 1
        assert result["results"][0]["id"] == "ds18b20"

    def test_all_filters(self, test_db):
        result = search_sensors(test_db, measure="temperature", protocol="i2c", type="mems", platform="arduino")
        ids = {r["id"] for r in result["results"]}
        assert "bme280" in ids


class TestSearchResults:
    def test_result_structure(self, test_db):
        result = search_sensors(test_db, query="BME280")
        assert "total" in result
        assert "results" in result
        r = result["results"][0]
        assert r["id"] == "bme280"
        assert r["name"] == "BME280"
        assert r["manufacturer"] == "Bosch"
        assert r["type"] == "mems"
        assert r["voltage"] == "1.8-3.6"
        assert sorted(r["measures"]) == ["humidity", "pressure", "temperature"]
        assert sorted(r["protocols"]) == ["i2c", "spi"]
        assert "arduino" in r["platforms"]
        assert r["platform_count"] == 7
        assert r["source_tier"] == "primary"

    def test_sort_by_platform_count(self, test_db):
        result = search_sensors(test_db, measure="temperature")
        counts = [r["platform_count"] for r in result["results"]]
        assert counts == sorted(counts, reverse=True)

    def test_limit(self, test_db):
        result = search_sensors(test_db, measure="temperature", limit=2)
        assert len(result["results"]) <= 2
        assert result["total"] > 2  # Should have more total than returned

    def test_no_params_returns_nothing(self, test_db):
        # With no filters at all, should return all sensors
        result = search_sensors(test_db)
        assert result["total"] == len(FIXTURES)
