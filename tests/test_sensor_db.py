"""Tests for sensor database search module.

Uses a small in-memory test database built from fixtures to test the
query builder, FTS5, parametric filters, and measure aliases.
"""

import json
import sqlite3
from pathlib import Path

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
        # Should expand to gpio, analog, pwm, one_wire
        ids = {r["id"] for r in result["results"]}
        assert "ds18b20" in ids  # one_wire
        assert "breakout1" in ids  # analog

    def test_gpio_and_digital_match_gpio_sensors(self):
        """The DB stores plain digital pins as "gpio". Before 0.6.3 protocol="gpio" left gpio itself
        out of its expansion and "digital" matched nothing."""
        conn = sqlite3.connect(":memory:")
        conn.executescript(SCHEMA)
        for sid, proto in (("pir1", "gpio"), ("servo1", "pwm"), ("temp1", "one_wire"), ("ldr1", "analog")):
            conn.execute("INSERT INTO sensors (id, name, manufacturer, type, voltage, datasheet_url, platform_count, "
                         "description, source_tier, sources) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (sid, sid.upper(), None, None, None, None, 0, sid, "primary", json.dumps(["test"])))
            conn.execute("INSERT INTO sensors_fts (id, name, manufacturer, description) VALUES (?, ?, ?, ?)",
                         (sid, sid.upper(), "", sid))
            conn.execute("INSERT INTO sensor_protocols VALUES (?, ?)", (sid, proto))
        conn.commit()
        gpio = {r["id"] for r in search_sensors(conn, protocol="gpio")["results"]}
        digital = {r["id"] for r in search_sensors(conn, protocol="digital")["results"]}
        assert gpio == {"pir1", "servo1", "temp1", "ldr1"}
        assert digital == {"pir1", "servo1", "temp1"}
        conn.close()


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


# Exercise import-time query aliases and the complete build against actual scraped records.
_SENSOR_DATA = Path(__file__).parent.parent / "data"
_IDENTITY_AUDIT = json.loads((_SENSOR_DATA / "sensors" / "ic_alias_evidence.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def real_sensor_catalog(tmp_path_factory):
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from build_sensor_db import build
    output = tmp_path_factory.mktemp("sensor-identities") / "sensor.db"
    build(_SENSOR_DATA, output, verbose=False)
    conn = sqlite3.connect(output)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_every_curated_id_is_a_catalog_record(real_sensor_catalog):
    """The build skips a curated ID with no record so the scrape gate can't lose a month of data;
    a typo or a dropped part must still be caught here, in CI."""
    curated = json.loads((_SENSOR_DATA / "sensors" / "curated.json").read_text(encoding="utf-8"))
    ids = {row[0] for row in real_sensor_catalog.execute("SELECT id FROM sensors")}
    missing = sorted(sid for sid, fields in curated.items()
                     if sid not in ids and not fields.get("exclude", {}).get("value"))
    assert not missing


@pytest.mark.parametrize("entry", [r for r in _IDENTITY_AUDIT["aliases"] if r["active"]])
def test_real_sensor_identity_queries_return_the_expected_record_first(real_sensor_catalog, entry):
    expected = entry["target"] if entry["decision"] == "keep" else entry["alias"]
    result = search_sensors(real_sensor_catalog, query=entry["alias"].upper())
    assert result["results"][0]["id"] == expected


@pytest.mark.parametrize("entry", _IDENTITY_AUDIT["identity_run3"]["merges"])
def test_run3_merged_and_current_designation_queries(real_sensor_catalog, entry):
    result = search_sensors(real_sensor_catalog, query=entry["alias"])
    assert result["results"][0]["id"] == entry["target"]


@pytest.mark.parametrize("entry", _IDENTITY_AUDIT["identity_run3"]["old_name_aliases"])
def test_run3_old_display_and_library_names_still_find_merged_part(real_sensor_catalog, entry):
    result = search_sensors(real_sensor_catalog, query=entry["query"])
    assert result["results"][0]["id"] == entry["target"]


@pytest.mark.parametrize("sid", [
    "bsec3", "bme680bsec", "bme68xbsec2", "ubloxgnssv3", "ubloxgnssv4", "bno08xrvc",
    "mb1060", "mb1061", "xiaomibodyscale", "pm25", "lsm303accel",  # ds3501 restored: on-chip temperature sensor
])
def test_run3_excluded_non_parts_are_absent(real_sensor_catalog, sid):
    assert real_sensor_catalog.execute("SELECT id FROM sensors WHERE id=?", (sid,)).fetchone() is None


@pytest.mark.parametrize("sid,platform", [
    ("bme680", "esphome"), ("bme688", "esphome"), ("bme690", "arduino"),
    ("bno08x", "micropython"), ("lsm303dlhc", "circuitpython"), ("lsm303agr", "circuitpython"),
    ("lsm9ds0", "zephyr"), ("lsm9ds1", "zephyr"),
    ("pms5003", "circuitpython"), ("pmsa003i", "circuitpython"),
    ("zedf9p", "arduino"), ("zedf9k", "arduino"), ("zedf9r", "arduino"),
    ("maxm10s", "arduino"), ("zedx20p", "arduino"), ("l76k", "arduino"),
])
def test_run3_driver_support_attached_to_physical_parts(real_sensor_catalog, sid, platform):
    part = search_sensors(real_sensor_catalog, query=sid)["results"][0]
    assert part["id"] == sid
    assert platform in part["platforms"]


def test_sd3031_keeps_readable_temperature_but_not_receiver_gps(real_sensor_catalog):
    part = search_sensors(real_sensor_catalog, query="SD3031")["results"][0]
    assert part["measures"] == ["temperature"]
    assert part["protocols"] == ["i2c"]


@pytest.mark.parametrize("query", ["MPU6500", "LSM6DS3", "MH-Z19C", "DS18S20", "MAX30105", "as726x", "tmf882x", "fs3000"])
def test_real_sensor_punctuated_and_family_queries(real_sensor_catalog, query):
    expected = query.lower().replace("-", "")
    assert search_sensors(real_sensor_catalog, query=query)["results"][0]["id"] == expected


@pytest.mark.parametrize("sid,evidence", _IDENTITY_AUDIT["split_field_evidence"].items())
def test_real_sensor_verified_datasheet_fields(real_sensor_catalog, sid, evidence):
    part = search_sensors(real_sensor_catalog, query=sid)["results"][0]
    curated = json.loads((Path(__file__).resolve().parents[1] / "data/sensors/curated.json").read_text(encoding="utf-8"))
    if not evidence["source_url"]:
        # Later field reviews supersede the identity audit's deliberately unset values.
        for field in evidence["unset_fields"]:
            correction = curated.get(sid, {}).get(field)
            if correction:
                assert correction["evidence"], (sid, field)
                assert part[field] == correction["value"], (sid, field)
            else:
                assert part[field] in (None, []), (sid, field)
        return
    for field in ("manufacturer", "type", "voltage"):
        correction = curated.get(sid, {}).get(field)
        if correction:
            assert correction["evidence"], (sid, field)
        assert part[field] == (correction["value"] if correction else evidence[field]), (sid, field)
    correction = curated.get(sid, {}).get("protocols")
    assert set(part["protocols"]) == set(correction["value"] if correction else evidence["protocols"]), sid


def test_real_sensor_max30105_obsolescence_and_parent_capabilities(real_sensor_catalog):
    child = search_sensors(real_sensor_catalog, query="MAX30105")["results"][0]
    parent = search_sensors(real_sensor_catalog, query="MAX30101")["results"][0]
    assert "Obsolete at Analog Devices" in child["capability_note"]
    assert "smoke/particle" in child["capability_note"]
    assert "particulate" in child["measures"]
    assert "particulate" not in parent["measures"]


@pytest.mark.parametrize("parent,child,parent_voltage,child_voltage", [
    ("mpu6050", "mpu6500", "2.375-3.46", "1.71-3.45"),
    ("lsm9ds1", "lsm9ds0", "1.9-3.6", "2.4-3.6"),
    ("mhz19", "mhz19c", None, "4.9-5.1"),
])
def test_real_sensor_parent_voltage_is_not_borrowed_from_child(
    real_sensor_catalog, parent, child, parent_voltage, child_voltage,
):
    parent_part = search_sensors(real_sensor_catalog, query=parent)["results"][0]
    child_part = search_sensors(real_sensor_catalog, query=child)["results"][0]
    assert parent_part["voltage"] == parent_voltage
    assert child_part["voltage"] == child_voltage
    assert parent_part["datasheet_url"] is None


def test_real_sensor_parent_protocol_and_description_stay_specific(real_sensor_catalog):
    parent = search_sensors(real_sensor_catalog, query="MPU6050")["results"][0]
    assert parent["protocols"] == ["i2c"]
    parent = search_sensors(real_sensor_catalog, query="LSM6DSOX")["results"][0]
    assert "LSM6DS33" not in parent["description"]
    parent = search_sensors(real_sensor_catalog, query="TFmini-S")["results"][0]
    assert "IP65" not in parent["description"] and "±5cm" not in parent["description"]


# Confirm the reviewed hardware facts through the real build and search response.
@pytest.mark.parametrize("sid,field,expected", [
    ('acs723', 'description', 'ACS723 Hall-effect current sensor'),
    ('ad8232', 'description', 'AD8232 measurement IC for the electrical activity of the heart'),
    ('ade7953', 'description', 'Single-phase energy metering IC with power, voltage, and current measurement'),
    ('ads1015', 'description', 'Texas Instruments ADS1015 12-bit analog-to-digital converter with programmable gain amplifier and I2C interface'),
    ('ads1115', 'description', 'Texas Instruments ADS1115 16-bit analog-to-digital converter with I2C interface'),
    ('ads1293', 'voltage', '2.7-5.5'),
    ('as7341', 'voltage', '1.7-2.0'),
    ('bmm350', 'voltage', '1.72-1.98'),
    ('a111', 'voltage', '1.71-1.89'),
    ('mrt311s', 'voltage', None),
    ('mrt511', 'voltage', None),
    ('me4no2', 'voltage', None),
    ('bm22s3031', 'voltage', '2.4-2.6'),
    # Mains is the measured input; the host wires the TTL side's 5V.
    ('pzem004t', 'voltage', '5'),
    # Outputs pull up to +V, so a single "5" would put 5V on 3.3V GPIOs.
    ('ky040', 'voltage', '3.3 or 5'),
    # The 3.3V version is custom on request only.
    ('ams5812', 'voltage', '4.75-5.25'),
    # Family records give the range every member supports (TMP116 needs 1.9V).
    ('tmp11x', 'voltage', '1.9-5.5'),
    ('bma4xx', 'voltage', '1.72-3.6'),
    ('mlx90614', 'voltage', '2.6-3.6 or 4.5-5.5'),
    ('cy8cmbr3102', 'description', 'CY8CMBR3102 capacitive touch sensing controller with I2C interface'),
    ('ekmb1107112', 'description', 'EKMB1107112 passive infrared (PIR) motion sensor'),
    ('ekmc4607112k', 'description', 'EKMC4607112K passive infrared (PIR) motion sensor'),
    ('icm20600', 'description', 'ICM20600 6-axis accelerometer and gyroscope with I2C and SPI interfaces'),
    ('icm42688p', 'description', 'TDK ICM-42688-P 6-axis MEMS accelerometer and gyroscope with I2C, I3C and SPI interfaces'),
    ('ld2420', 'description', 'Hi-Link 24GHz mmWave radar module for motion and presence detection'),
    ('lm35', 'description', 'Texas Instruments LM35 analog temperature sensor with output voltage proportional to temperature in Celsius'),
    ('mcp39f521', 'description', 'Microchip MCP39F521 power monitoring IC'),
    ('mmc5603nj', 'description', 'MEMSIC MMC5603NJ 3-axis magnetic field sensor with I2C and I3C interfaces'),
    ('mr60bha2', 'description', '60GHz mmWave radar module for breathing and heartbeat detection'),
    ('paa5160e1', 'description', 'PAA5160E1 optical motion tracking sensor'),
    ('qmc5883l', 'description', 'QMC5883L magnetic field sensor'),
    ('scd40', 'description', 'Sensirion SCD40 CO2, humidity and temperature sensor with I2C interface'),
    ('scd4x', 'description', 'Sensirion SCD4x family of CO2, temperature and humidity sensors'),
    ('sd3031', 'description', 'SD3031 real-time clock IC with I2C interface, integrated crystal oscillator and temperature sensing'),
    ('sfa40', 'description', 'Sensirion SFA40 electrochemical formaldehyde sensor with temperature and humidity output and I2C interface'),
    ('stc31', 'description', 'Sensirion STC31 thermal conductivity CO2 concentration sensor with temperature output and I2C interface'),
    ('temt6000', 'description', 'TEMT6000 ambient light sensor with analog output'),
])
def test_real_sensor_curated_corrections(real_sensor_catalog, sid, field, expected):
    part = search_sensors(real_sensor_catalog, query=sid)["results"][0]
    assert part["id"] == sid
    assert part[field] == expected


def test_real_sensor_voltages_are_volts_with_separate_modes(real_sensor_catalog):
    """`voltage` is "min-max" or one value in volts, and " or " joins only separate
    supply versions/modes: overlapping alternatives would read as selectable modes."""
    from decimal import Decimal
    import re

    bad = []
    for sid, voltage in real_sensor_catalog.execute("SELECT id, voltage FROM sensors WHERE voltage IS NOT NULL"):
        modes = voltage.split(" or ")
        if not all(re.fullmatch(r"\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?", m) for m in modes):
            bad.append((sid, voltage))
            continue
        bounds = sorted(tuple(map(Decimal, (m.split("-") * 2)[:2])) for m in modes)
        if any(lo > hi for lo, hi in bounds) or any(
                hi >= lo for (_, hi), (lo, _) in zip(bounds, bounds[1:])):
            bad.append((sid, voltage))
    assert not bad


def test_real_sensor_mains_powered_meter_says_so(real_sensor_catalog):
    part = search_sensors(real_sensor_catalog, query="PZEM-004T")["results"][0]
    assert part["id"] == "pzem004t"
    assert "80-260VAC" in part["capability_note"] and "mains" in part["capability_note"]


@pytest.mark.parametrize("sid,expected", [
    ("mhz19", "ndir"),
    ("sps30", "laser"),
    ("gp2y1010au0f", "optical_scattering"),
])
def test_real_sensor_curated_technology_survives_build(real_sensor_catalog, sid, expected):
    curated = json.loads(
        (Path(__file__).resolve().parents[1] / "data/sensors/curated.json").read_text(encoding="utf-8")
    )
    assert curated[sid]["type"]["value"] == expected
    part = search_sensors(real_sensor_catalog, query=sid)["results"][0]
    assert part["id"] == sid
    assert part["type"] == expected


@pytest.mark.parametrize('query,sid', [
    ('ADS1X15', 'ads1015'), ('Arduino_BMI270_BMM150', 'bmi270bmm150'),
    ('AD8495', 'ad8494'), ('7SemiBME68x', 'bme68x'),
    ('IoTy coind4', 'coind4'), ('MRTD-3011', 'rttd721155'),
    ('QMC5883LCompass', 'qmc5883l'),
])
def test_former_and_scraped_names_are_search_only_aliases(real_sensor_catalog, query, sid):
    result = search_sensors(real_sensor_catalog, query=query, limit=100)
    assert sid in {row['id'] for row in result['results']}
    row = next(row for row in result['results'] if row['id'] == sid)
    assert row['name'] == real_sensor_catalog.execute('SELECT name FROM sensors WHERE id=?', (sid,)).fetchone()[0]
    if sid in {'ads1015', 'bmi270bmm150'}:
        assert row['name'] != query


def test_all_persisted_former_and_source_names_find_their_record(real_sensor_catalog):
    aliases = json.loads((_SENSOR_DATA / 'sensors/name_aliases.json').read_text(encoding="utf-8"))
    for sid, names in aliases.items():
        for name in names:
            result = search_sensors(real_sensor_catalog, query=name, limit=2000)
            assert sid in {row['id'] for row in result['results']}, (sid, name)


def test_query_with_no_ascii_terms_does_not_match_everything(real_sensor_catalog):
    """"温度" normalized to "" and its ID pattern "%%" returned all sensors."""
    assert search_sensors(real_sensor_catalog, query="温度")["total"] == 0


def test_control_characters_in_a_sensor_query_are_rejected():
    import asyncio, inspect
    from pcbparts_mcp import server
    r = server.sensor_recommend(query="BME280\x00")
    r = asyncio.run(r) if inspect.isawaitable(r) else r
    assert r["error"] == "Query contains invalid characters"


@pytest.mark.parametrize("query,measure,expect_note", [
    ("é", None, True), ("-", None, True), ("sensor", "co2", True), ("bme280", None, False), ("温度", None, False),
])
async def test_query_without_searchable_words_says_so(query, measure, expect_note):
    """"é" returned the whole catalog as if it matched (server review, 2026-11-10); the filters
    still apply, as in board_search, and a note says the query was ignored."""
    from pcbparts_mcp import server
    result = await server.sensor_recommend(query=query, measure=measure, limit=3)
    assert ("note" in result) is expect_note
    if measure:
        assert all(measure in r["measures"] for r in result["results"])
