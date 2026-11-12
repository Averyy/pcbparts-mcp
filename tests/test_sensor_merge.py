"""Tests for sensor build pipeline — merge logic, name cleaning, enrichment."""

import json
import sqlite3
from contextlib import closing
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


@pytest.fixture
def curated_data(tmp_path, monkeypatch):
    """Small scrape input still runs the complete production build pipeline."""
    import build_sensor_db as builder

    monkeypatch.setattr(builder, "MIN_SENSOR_COUNT", 0)
    sensors = tmp_path / "sensors"
    sensors.mkdir()
    for source in builder.SOURCE_ORDER:
        (sensors / f"{source}.json").write_text(json.dumps({"sensors": []}))
    (sensors / "arduino.json").write_text(json.dumps({"sensors": [{
        "id": "ads1293", "name": "ADS1293", "manufacturer": "scraped maker",
        "description": "A scraped description long enough to block the legacy guard",
        "voltage": "1.7-3.6", "type": "scraped type", "measures": ["biometric"],
        "protocol": ["spi"], "platforms": ["arduino"],
    }]}))
    return tmp_path


def _curated_field(value):
    return {"value": value, "evidence": {"document": "Reviewed datasheet", "page": 4},
            "review_date": "2026-11-10"}


@pytest.mark.parametrize("description,expected", [
    ("Six-axis MEMS IMU with SPI connection", "mems"),
    ("Six-axis IMU with SPI connection", None),
])
def test_type_inference_requires_explicit_mems_imu_technology(description, expected):
    sensor = {"type": None, "measures": {"acceleration", "gyroscope"},
              "description": description}
    enrich_types({"testdevice": sensor}, quiet=True)
    assert sensor["type"] == expected


def test_curated_fields_survive_rescrapes_and_all_build_rules(curated_data, monkeypatch):
    import build_sensor_db as builder

    values = {
        "name": "Reviewed ADS1293", "description": "Reviewed biopotential measurement front end",
        "manufacturer": "Reviewed maker", "type": "reviewed technology", "voltage": "2.7-5.5",
        "datasheet_url": "https://www.ti.com/lit/ds/symlink/ads1293.pdf",
        "measures": ["voltage"], "protocols": [],
    }
    corrections = {"ads1293": {field: _curated_field(value) for field, value in values.items()}}
    (curated_data / "sensors" / "curated.json").write_text(json.dumps(corrections))
    # Force competing legacy rules, including rules applied during DB insertion.
    monkeypatch.setitem(builder.NAME_OVERRIDES, "ads1293", "Legacy name")
    monkeypatch.setitem(builder.MEASURE_ADDITIONS, "ads1293", {"temperature"})
    monkeypatch.setitem(builder.MEASURE_REMOVALS, "ads1293", {"voltage"})
    output = curated_data / "sensor.db"
    source = curated_data / "sensors" / "arduino.json"
    for description, voltage in [("Original scraped hardware description", "1.7-3.6"),
                                 ("New scrape overwrites the hardware description", "9.0-12.0")]:
        scrape = json.loads(source.read_text(encoding="utf-8"))
        scrape["sensors"][0].update(description=description, voltage=voltage)
        source.write_text(json.dumps(scrape))
        builder.build(curated_data, output, verbose=False)
        with closing(sqlite3.connect(output)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sensors WHERE id='ads1293'").fetchone()
            for field, value in values.items():
                if field not in {"measures", "protocols"}:
                    assert row[field] == value
            assert list(conn.execute("SELECT measure FROM sensor_measures"))[0][0] == "voltage"
            assert conn.execute("SELECT count(*) FROM sensor_measures").fetchone()[0] == 1
            assert conn.execute("SELECT count(*) FROM sensor_protocols").fetchone()[0] == 0
            assert conn.execute("SELECT platform FROM sensor_platforms").fetchone()[0] == "arduino"
            assert json.loads(row["sources"]) == ["arduino"]
            assert conn.execute("SELECT description FROM sensors_fts WHERE id='ads1293'").fetchone()[0] == values["description"]


@pytest.mark.parametrize("invalid,match", [
    ({"ads1293": {"voltage": {"value": "2.7-5.5", "review_date": "2026-11-10"}}}, "missing evidence"),
    ({"ads1293": {"voltage": {**_curated_field("2.7-5.5"), "evidence": {"text": "unsupported assertion"}}}}, "missing evidence"),
    ({"ads1293": {"voltage": {**_curated_field("2.7-5.5"), "review_date": "2026-02-30"}}}, "review_date"),
    ({"ads1293": {"protocol": _curated_field(["spi"])}}, "unsupported curated field"),
    ({"ads1293": {"description": _curated_field("x" * 201)}}, "200 characters"),
    ({"ads1293": {"measures": _curated_field("voltage")}}, "exact list"),
    ({"ads1293": {"exclude": _curated_field(True)}}, "requires a boolean value and a reason"),
])
def test_invalid_curated_corrections_fail_without_replacing_db(curated_data, invalid, match):
    from build_sensor_db import build

    (curated_data / "sensors" / "curated.json").write_text(json.dumps(invalid))
    output = curated_data / "sensor.db"
    output.write_bytes(b"previous database")
    with pytest.raises(ValueError, match=match):
        build(curated_data, output, verbose=False)
    assert output.read_bytes() == b"previous database"


def test_curated_id_without_a_record_is_skipped_not_fatal(curated_data, capsys):
    """The catalog build gates the monthly scrape commit. A curated ID whose part left every source
    (three missed scrapes, or its pages are gone) made it fail and discard all 14 sources' data
    (pipeline review, 2026-11-10). tests/test_sensor_db.py still requires every curated ID to exist."""
    from build_sensor_db import build

    (curated_data / "sensors" / "curated.json").write_text(json.dumps({"unknownid": {"voltage": _curated_field("2.7-5.5")}}))
    output = curated_data / "sensor.db"
    build(curated_data, output, verbose=False)
    assert output.exists()
    assert "unknownid" in capsys.readouterr().err


def test_curated_only_changes_named_fields_and_supports_null_and_exclusion(curated_data):
    from build_sensor_db import build

    path = curated_data / "sensors" / "curated.json"
    corrections = {"ads1293": {"manufacturer": _curated_field(None)}}
    path.write_text(json.dumps(corrections))
    output = curated_data / "sensor.db"
    build(curated_data, output, verbose=False)
    with closing(sqlite3.connect(output)) as conn:
        assert conn.execute("SELECT manufacturer, voltage, description FROM sensors").fetchone() == (
            None, "1.7-3.6", "A scraped description long enough to block the legacy guard")
    corrections["ads1293"]["exclude"] = {**_curated_field(True), "reason": "Verified non-part"}
    path.write_text(json.dumps(corrections))
    build(curated_data, output, verbose=False)
    with closing(sqlite3.connect(output)) as conn:
        for table in ["sensors", "sensors_fts", "sensor_measures", "sensor_protocols", "sensor_platforms", "sensor_urls"]:
            assert conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0


@pytest.mark.parametrize("voltage,reason", [
    ("3.0-3.6 or 4.5-5.5", "Separate regulator-bypass and regulated supply modes"),
    (None, "no maker or vendor source found; exact-model supply search found no specification"),
])
def test_curated_voltage_modes_and_unknown_survive_build_and_reply(curated_data, voltage, reason):
    from build_sensor_db import build
    from pcbparts_mcp.sensor_db.search import search_sensors

    correction = {**_curated_field(voltage), "reason": reason}
    path = curated_data / "sensors" / "curated.json"
    path.write_text(json.dumps({"ads1293": {"voltage": correction}}))
    output = curated_data / "sensor.db"
    build(curated_data, output, verbose=False)

    with closing(sqlite3.connect(output)) as conn:
        assert conn.execute("SELECT voltage FROM sensors WHERE id='ads1293'").fetchone()[0] == voltage
        result = search_sensors(conn, query="ads1293")["results"][0]
        assert result["voltage"] == voltage
    assert json.loads(path.read_text(encoding="utf-8"))["ads1293"]["voltage"]["reason"] == reason


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

    @pytest.mark.parametrize("prefix", [
        "Arduino library for ", "An Arduino library for the ",
        "MicroPython driver for ", "MicroPython module for the ", "Library for ",
        "DFRobot Standard library for ", "DFRobot Standard library for the ",
    ])
    def test_software_prefix_leaves_hardware(self, prefix):
        assert clean_description(prefix + "XYZ123 temperature sensor") == "XYZ123 temperature sensor"

    @pytest.mark.parametrize("description", [
        "Arduino library for XYZ123",  # No sensing function remains.
        "Arduino library for XYZ123 sensor library",
        "Arduino library for XYZ123 sensor board",
        "MicroPython driver for XYZ123 sensor shield",
        "Library for XYZ123 sensor examples",
        "Arduino library for XYZ123 sensors",  # Generic plural title, no function.
    ])
    def test_software_prefix_guards(self, description):
        assert clean_description(description) == description


@pytest.mark.parametrize("description,expected", [
    ("XYZ123 accelerometer When setting the range property, include xyz123.h", "XYZ123 accelerometer"),
    ('XYZ123 rotary sensor &spi3 { status = "okay"; };', "XYZ123 rotary sensor"),
    ("XYZ123 current monitor. The <zephyr/dt-bindings/sensor/xyz123.h> file provides macros.",
     "XYZ123 current monitor."),
    ("XYZ123 magnetometer. It supports I2C and SPI. When setting the odr property, include xyz123.h.",
     "XYZ123 magnetometer. It supports I2C and SPI."),
    ("XYZ123 magnetometer. When using SPI, the device supports modes 0 and 3.",
     "XYZ123 magnetometer. When using SPI, the device supports modes 0 and 3."),
    ("XYZ123 sensor. This sensor requires a 3.3 V supply.",
     "XYZ123 sensor. This sensor requires a 3.3 V supply."),
    ("XYZ123 sensor. See https://example.com/datasheet.pdf. It supports SPI. When setting the odr, include xyz.h.",
     "XYZ123 sensor. See https://example.com/datasheet.pdf. It supports SPI."),
])
def test_zephyr_instruction_boundaries(description, expected):
    from build_sensor_db import trim_zephyr_description
    assert trim_zephyr_description(description) == expected


@pytest.mark.parametrize("current,alternate,expected", [
    ("Beginner-friendly XYZ123 driver with examples and API functions",
     "XYZ123 digital temperature sensor", "XYZ123 digital temperature sensor"),
    ("Arduino library for XYZ123 temperature sensor",
     "Our XYZ123 breakout board makes your next project easy",
     "XYZ123 temperature sensor"),
    ("Arduino library for XYZ123 visible and ultraviolet light sensor",
     "An ambient light sensor", "XYZ123 visible and ultraviolet light sensor"),
    ("XYZ123 temperature sensor with 16-bit output", "XYZ123 sensor breakout board",
     "XYZ123 temperature sensor with 16-bit output"),
])
def test_merge_prefers_hardware_without_promoting_breakout_marketing(curated_data, current, alternate, expected):
    sensors = curated_data / "sensors"
    for source, description in [("arduino", current), ("sparkfun", alternate)]:
        (sensors / f"{source}.json").write_text(json.dumps({"sensors": [
            {"id": "xyz123", "description": description},
        ]}))
    assert merge_sensors(curated_data, {}, quiet=True)["xyz123"]["description"] == expected


def test_rescraped_prefix_cleanup_preserves_selection(curated_data):
    """A scraper's cleaned title must retain its quality across monthly rebuilds."""
    sensors = curated_data / "sensors"
    (sensors / "arduino.json").write_text(json.dumps({"sensors": [{
        "id": "xyz123", "description": "XYZ123 high accuracy temperature sensor",
        "description_is_library_title": True,
    }]}))
    (sensors / "tasmota.json").write_text(json.dumps({"sensors": [{
        "id": "xyz123", "description": "Temperature sensor",
    }]}))
    assert merge_sensors(curated_data, {}, quiet=True)["xyz123"]["description"] == "Temperature sensor"


def test_build_trims_existing_zephyr_json(curated_data):
    sensors = curated_data / "sensors"
    (sensors / "zephyr.json").write_text(json.dumps({"sensors": [{
        "id": "xyz123", "description": "XYZ123 magnetometer. It supports I2C and SPI. "
        "When setting the odr property, include xyz123.h.",
    }]}))
    assert merge_sensors(curated_data, {}, quiet=True)["xyz123"]["description"] == (
        "XYZ123 magnetometer. It supports I2C and SPI")


@pytest.mark.parametrize("source", ["arduino", "micropython"])
@pytest.mark.parametrize("hardware_available", [False, True])
def test_library_scrapers_select_hardware_and_preserve_cleaned_title_rank(tmp_path, monkeypatch, source, hardware_available):
    import importlib
    from types import SimpleNamespace

    scraper = importlib.import_module(f"scrapers.{source}")
    title = ("Arduino library for " if source == "arduino" else "MicroPython driver for ") + (
        "XYZ123 high accuracy temperature sensor")
    descriptions = [title, "XYZ123 library with beginner-friendly examples and many API functions for reading temperature"]
    if hardware_available:
        descriptions.append("XYZ123 temperature sensor")
    libraries = [{"name": f"Sensor {i}", "version": "1.0", "category": "Sensors", "sentence": d}
                 for i, d in enumerate(descriptions)]
    markdown = "## Sensors\n### Temperature Digital\n" + "\n".join(
        f"* [XYZ123](https://example.com/{i}) - {d}" for i, d in enumerate(descriptions))
    response = SimpleNamespace(raise_for_status=lambda: None, json=lambda: {"libraries": libraries}, text=markdown)
    monkeypatch.setattr(scraper.wafer, "get", lambda *args, **kwargs: response)
    getattr(scraper, f"scrape_{source}")(tmp_path)
    record, = json.loads((tmp_path / f"{source}.json").read_text(encoding="utf-8"))["sensors"]
    assert record["description"] == ("XYZ123 temperature sensor" if hardware_available else
                                     "XYZ123 high accuracy temperature sensor")
    assert record.get("description_is_library_title", False) is not hardware_available


def test_dfrobot_scraper_cleans_library_title(tmp_path, monkeypatch):
    from scrapers import dfrobot

    monkeypatch.setattr(dfrobot, "_run_gh_api", lambda _: [{"name": "DFRobot_XYZ123"}])
    monkeypatch.setattr(dfrobot, "_fetch_library_properties", lambda _: {
        "sentence": "Library for XYZ123 temperature sensor"})
    dfrobot.scrape_dfrobot(tmp_path)
    record, = json.loads((tmp_path / "dfrobot.json").read_text(encoding="utf-8"))["sensors"]
    assert record["description"] == "XYZ123 temperature sensor"
    assert record["description_is_library_title"] is True


def test_zephyr_scraper_trims_before_writing_json(tmp_path, monkeypatch):
    from scrapers import zephyr

    checkout = tmp_path / "checkout"
    bindings = checkout / zephyr.BINDINGS_PATH
    bindings.mkdir(parents=True)
    (bindings / "ti,xyz123.yaml").write_text(
        'description: |\n'
        '  XYZ123 temperature sensor.\n'
        '  It supports I2C and SPI.\n'
        '  When setting the rate property, include xyz123.h.\n'
        'compatible: "ti,xyz123"\n'
        'include: i2c-device.yaml\n')
    monkeypatch.setattr(zephyr.tempfile, "mkdtemp", lambda **_: str(checkout))
    monkeypatch.setattr(zephyr.subprocess, "run", lambda *args, **kwargs: None)
    zephyr.scrape_zephyr(tmp_path)
    record, = json.loads((tmp_path / "zephyr.json").read_text(encoding="utf-8"))["sensors"]
    assert record["description"] == "XYZ123 temperature sensor. It supports I2C and SPI."


@pytest.mark.parametrize("sid,expected", [
    ("atm90e26", "ATM90E26 energy metering device"),
    ("dht11", "Temperature and humidity sensor"),
    ("dht12", "Aosong DHT12 temperature and humidity sensor, I2C interface"),
    ("dht22", "Temperature and humidity sensor"),
    ("ggreg20v3", "Ionizing radiation detector"),
    ("lis2hh12", "Measure acceleration with the LIS2HH12"),
    ("lm75a", "LM75A digital temperature sensor"),
    ("pms5003", "Particle concentration sensor"),
    ("qmc5883l", "Magnetic field sensor"),
    ("sds011", "Laser dust sensor"),
    ("sht3x", "Sht3x series T/H sensor"),
    ("temt6000", "Get a near-human-eye perspective with the TEMT6000 sensor, offering a simple analog output with a peak spectral sensitivity of 570nm"),
    ("bme688", "temperature, humidity, pressure and gas sensor"),
    ("bmi323", "BMI323 6-axis IMU sensor"),
    ("hdc1080", "Texas Instruments HDC1080 humidity and temperature sensor"),
    ("hscdtd008a", "HSCDTD008A geomagnetic sensor"),
    ("ina219", "High-side DC current and voltage sensor"),
    ("pms7003", "Particle concentration sensor"),
    ("sht30", "Temperature and humidity sensor"),
    ("sht31", "SHT31 temperature and humidity sensor"),
])
def test_real_sensor_hardware_description_replacements(real_sensor_merge, sid, expected):
    # Check selection before curated corrections; QMC5883L and TEMT6000 retain
    # their reviewed descriptions in the final database.
    assert real_sensor_merge[sid]["description"] == expected


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
            (sensor_data_dir / "sensors" / "ic_aliases.json").read_text(encoding="utf-8")
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


def test_build_tables_have_no_duplicate_keys():
    """A repeated key in a dict literal silently replaces the earlier entry.

    bm42s3021 was listed twice in IC_PROTOCOLS: ["i2c"], as its page and
    datasheet give, then ["uart"], which won.
    """
    import ast

    source = (Path(__file__).parent.parent / "scripts" / "build_sensor_db.py").read_text(encoding="utf-8")
    duplicates = []
    for node in ast.parse(source).body:
        value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
        if not isinstance(value, (ast.Dict, ast.Set)):
            continue
        keys = value.keys if isinstance(value, ast.Dict) else value.elts
        seen: set = set()
        for key in keys:
            if isinstance(key, ast.Constant):
                if key.value in seen:
                    duplicates.append(f"line {key.lineno}: {key.value!r}")
                seen.add(key.value)
    assert duplicates == []


@pytest.fixture(scope="module")
def measures(tmp_path_factory):
    """Each sensor's measures in a build of the real data."""
    import sqlite3
    from build_sensor_db import build
    out = tmp_path_factory.mktemp("sensors") / "sensor.db"
    build(Path(__file__).parent.parent / "data", out, verbose=False)
    with closing(sqlite3.connect(out)) as conn:
        rows = conn.execute("SELECT sensor_id, measure FROM sensor_measures").fetchall()
    result: dict[str, set[str]] = {}
    for sensor_id, measure in rows:
        result.setdefault(sensor_id, set()).add(measure)
    return result


class TestMeasureCorrections:
    """Measure tags that sources get wrong (todos #49), checked on a build of the real data."""

    def test_bmm150_is_a_magnetometer_not_a_sound_sensor(self, measures):
        # DFRobot's BMM150 library (SEN0419) is tagged sound in the Arduino index
        assert measures["bmm150"] == {"magnetic_field"}

    def test_pmwcs3_measures_soil_moisture(self, measures):
        # ESPHome lists it under temperature only; it reads VWC, EC and soil temperature
        assert {"soil_moisture", "conductivity", "temperature"} <= measures["pmwcs3"]

    def test_cy8cmbr3102_is_also_a_touch_controller(self, measures):
        # The CapSense controller on SparkFun's capacitive soil moisture sensor keeps soil_moisture
        assert {"soil_moisture", "touch"} <= measures["cy8cmbr3102"]

    def test_bm25s2621_does_not_measure_air_humidity(self, measures):
        assert "humidity" not in measures["bm25s2621"]


class TestMeasureWordsThatAreNotMeasures:
    """Library text that named no measurement but was tagged as one (0.9.0): the Arduino index
    descriptions below are quoted from the libraries."""

    @pytest.mark.parametrize("text,wrong", [
        ("The AD7194 is a low noise, complete analog front end for high precision measurement applications.", "sound"),
        ("AD7190: 4.8 kHz Ultra-Low Noise 24-Bit Sigma-Delta ADC with PGA", "sound"),
        ("The BMM150 is a low-power and low noise 3-axis digital geomagnetic sensor", "sound"),
        ("A library to control the Iowa Scaled Engineering I2C-MCP3427 16-bit analog to digital converter", "weight"),
        ("All values are transmitted as scaled integers", "weight"),
        ("Drives the TI TLA2021/TLA2022/TLA2024 family of low-power 12-bit delta-sigma ADCs over I2C: "
         "single-ended and differential reads, programmable gain (PGA/FSR)", "force"),
    ])
    def test_word_is_not_the_measure(self, text, wrong):
        from scrapers.common import infer_measures
        assert wrong not in infer_measures(text)

    @pytest.mark.parametrize("text,measure", [
        ("Low-noise MEMS microphone with I2S output", "sound"),
        ("NAU7802 24-bit low-noise ADC commonly used with load cells and weight scales", "weight"),
        ("Interlink FSR 402 force sensing resistor", "force"),
        ("Sound level meter with low noise floor", "sound"),
    ])
    def test_real_measure_survives_the_same_words(self, text, measure):
        from scrapers.common import infer_measures
        assert measure in infer_measures(text)

    @pytest.mark.parametrize("compatible", [
        "bflb,tsen", "silabs,emu-temp", "raspberrypi,bcm283x-vc-thermal", "realtek,ameba-temp", "nxp,tmpsns",
        "realtek,bee-qdec",
    ])
    def test_zephyr_chip_internal_sensors_are_skipped(self, compatible):
        from scrapers.zephyr import _should_skip
        assert _should_skip(compatible)

    @pytest.mark.parametrize("compatible", ["microcrystal,rv3032-temp", "maxim,max32664c", "bosch,bme280"])
    def test_zephyr_parts_are_kept(self, compatible):
        from scrapers.zephyr import _should_skip
        assert not _should_skip(compatible)


# Real scrape records are essential here: synthetic aliases cannot expose cross-device leaks.
_REAL_DATA = Path(__file__).parent.parent / "data"
_ALIAS_AUDIT = json.loads((_REAL_DATA / "sensors" / "ic_alias_evidence.json").read_text(encoding="utf-8"))
_SPLIT_ALIASES = [(r["alias"], r["target"]) for r in _ALIAS_AUDIT["aliases"]
                  if r["active"] and r["decision"] == "remove"]
_KEPT_ALIASES = [(r["alias"], r["target"]) for r in _ALIAS_AUDIT["aliases"] if r["decision"] == "keep"]


@pytest.fixture(scope="module")
def real_sensor_merge():
    from build_sensor_db import load_aliases
    return merge_sensors(_REAL_DATA, load_aliases(_REAL_DATA), quiet=True)


@pytest.mark.parametrize("child,parent", _SPLIT_ALIASES)
def test_real_sensor_split_identities_stay_separate(real_sensor_merge, child, parent):
    assert child in real_sensor_merge
    assert parent in real_sensor_merge
    assert real_sensor_merge[child] is not real_sensor_merge[parent]


@pytest.mark.parametrize("alias,target", _KEPT_ALIASES)
def test_real_sensor_true_aliases_still_merge(real_sensor_merge, alias, target):
    assert target in real_sensor_merge
    assert alias not in real_sensor_merge


@pytest.mark.parametrize("parent", ["mhz19", "lsm6dsox", "ds18b20", "tfminis", "max30101", "as726x", "tmf882x", "fs3000"])
def test_real_sensor_parents_keep_their_own_source_fields(real_sensor_merge, parent):
    independent = merge_sensors(_REAL_DATA, {}, quiet=True)[parent]
    for field in ("datasheet_url", "voltage", "description", "measures", "protocols", "sources"):
        assert real_sensor_merge[parent][field] == independent[field], (parent, field)


def test_real_sensor_dht22_only_merges_its_verified_am2302_name(real_sensor_merge):
    control = merge_sensors(_REAL_DATA, {"am2302": "dht22"}, quiet=True)
    assert real_sensor_merge["dht22"] == control["dht22"]


def test_real_sensor_wrong_measures_do_not_reach_parents(real_sensor_merge):
    assert "gyroscope" not in real_sensor_merge["adxl345"]["measures"]
    assert "particulate" not in real_sensor_merge["max30101"]["measures"]
    assert "particulate" in real_sensor_merge["max30105"]["measures"]
    assert "IP65" not in real_sensor_merge["tfminis"]["description"]
    assert real_sensor_merge["mhz19"]["datasheet_url"] is None
    assert real_sensor_merge["mhz19"]["voltage"] is None


@pytest.mark.parametrize("raw,expected", [
    ("7Semi_BME68x", "bme68x"), ("7SemiBMP58x", "bmp58x"),
    ("7Semi TMP23x", "tmp23x"), ("MyLD2410", "ld2410"),
    ("My_TMP117", "tmp117"), ("7Semi BMP390", "bmp390"),
    ("Microfire_SHT3x", "sht3x"), ("IoTy coind4", "coind4"),
    ("HLK-LD2410B", "ld2410b"), ("HLKLD2410S", "ld2410s"),
    ("Omron D6F-PH", "d6fph"), ("adafruit_7semi_bno08x", "bno08x"),
    ("BME680", "bme680"), ("BME68x", "bme68x"),
])
def test_library_identity_normalization_preserves_model_and_variant(raw, expected):
    from scrapers.common import normalize_sensor_id
    assert normalize_sensor_id(raw) == expected


@pytest.mark.parametrize("name,sid,expected", [
    ("AD8495", "ad8494", "AD8494"), ("BMP180MI", "bmp085", "BMP085"),
    ("ClosedCube SHT31D", "sht30", "SHT30"), ("7Semi TMP11x", "tmp116", "TMP116"),
    ("KX13X", "kx132", "KX132"), ("107-Arduino-APDS-9950", "apds9950", "APDS-9950"),
    ("Grove ICM20600 AK09918 UNO R4", "icm20600", "ICM20600"),
    ("ME2-CH2O-16×15", "me2ch2o1615", "ME2-CH2O-16×15"),
])
def test_name_requires_complete_model_not_shared_prefix(name, sid, expected):
    assert clean_name(name, sid) == expected


def test_exclusion_survives_fresh_scrape_absence_and_return(curated_data):
    import build_sensor_db as builder
    source = curated_data / "sensors" / "arduino.json"
    correction = {"ads1293": {"exclude": {**_curated_field(True), "reason": "Reviewed non-part"}}}
    (curated_data / "sensors" / "curated.json").write_text(json.dumps(correction))
    record = json.loads(source.read_text(encoding="utf-8"))["sensors"][0]
    output = curated_data / "sensor.db"
    for records in ([record], [], [{**record, "name": "New scrape title", "measures": ["temperature"]}]):
        source.write_text(json.dumps({"sensors": records}))
        builder.build(curated_data, output, verbose=False)
        with closing(sqlite3.connect(output)) as conn:
            for table in ("sensors", "sensors_fts", "sensor_measures", "sensor_platforms", "sensor_urls"):
                assert conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0


def test_shared_driver_transfers_support_without_software_measurements(curated_data):
    import build_sensor_db as builder
    sensors = curated_data / "sensors"
    (sensors / "arduino.json").write_text(json.dumps({"sensors": [
        {"id": "driver123", "name": "Driver", "measures": ["co2"], "voltage": "99",
         "protocol": ["spi"], "platforms": ["arduino"], "urls": ["https://example.com/driver"]},
        {"id": "part123", "name": "PART123", "measures": ["temperature"], "voltage": "3.3",
         "protocol": ["i2c"], "platforms": ["zephyr"]},
    ]}))
    (sensors / "support_transfers.json").write_text(json.dumps({"driver123": {
        "targets": [{"id": "part123"}], "evidence": {"url": "https://example.com/driver"},
    }}))
    (sensors / "curated.json").write_text(json.dumps({"driver123": {
        "exclude": {**_curated_field(True), "reason": "Software supporting physical PART123"},
    }}))
    output = curated_data / "sensor.db"
    builder.build(curated_data, output, verbose=False)
    with closing(sqlite3.connect(output)) as conn:
        assert conn.execute("SELECT id, voltage FROM sensors").fetchall() == [("part123", "3.3")]
        assert conn.execute("SELECT measure FROM sensor_measures").fetchall() == [("temperature",)]
        assert conn.execute("SELECT protocol FROM sensor_protocols").fetchall() == [("i2c",)]
        assert set(conn.execute("SELECT platform FROM sensor_platforms")) == {("arduino",), ("zephyr",)}
        assert conn.execute("SELECT url FROM sensor_urls").fetchall() == [("https://example.com/driver",)]


@pytest.mark.parametrize("slug,model", [
    ("me3-ch2chcl", "ME3-C2H3Cl"), ("mrtd-3011", "RTT-D7211-5.5"),
    ("zc41", "ZC401"), ("zp510", "ZP150"),
])
def test_winsen_model_uses_summary_and_title_agreement(slug, model):
    from scrapers.winsen import _extract_product_model
    html = f"<table><tr><td>Model:</td><td>{model}</td></tr></table>"
    assert _extract_product_model(html, model + " Gas Sensor", f"https://example.com/{slug}.html", {}) == model


def test_winsen_unrelated_copied_table_does_not_reidentify_product():
    from scrapers.winsen import _extract_product_model
    html = "<table><tr><td>Model:</td><td>MQ303B</td></tr></table>"
    assert _extract_product_model(html, "MQ316 Gas Sensor", "https://example.com/mq316.html", {"model": "MQ303B"}) == "MQ316"


def test_arduino_corroborated_title_beats_measurand_and_shortest_title(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from scrapers import arduino

    libraries = [
        {"name": "SparkFun BMV080 Arduino Library", "sentence":
         "Air quality PM1/PM2.5/PM10 sensor BMV080 for particulate matter sensing."},
        {"name": "AD8495", "sentence":
         "Arduino library for AD8494, AD8495, AD8496 and AD8497 thermocouple temperature sensors."},
    ]
    for lib in libraries:
        lib.update(version="1.0.0", category="Sensors")
    monkeypatch.setattr(arduino.wafer, "get", lambda *a, **kw: SimpleNamespace(
        raise_for_status=lambda: None, json=lambda: {"libraries": libraries}))
    arduino.scrape_arduino(tmp_path)
    sensors = {s["id"]: s for s in json.loads((tmp_path / "arduino.json").read_text(encoding="utf-8"))["sensors"]}
    assert "pm1" not in sensors
    assert sensors["bmv080"]["name"] == "BMV080"
    assert sensors["ad8494"]["name"] == "AD8494"


@pytest.mark.parametrize('text,expected', [
    # "6-axis IMU" alone is an accelerometer and gyroscope (the fallback in infer_measures);
    # an empty result dropped such parts from the scrape. Named channels still win below.
    ('6-axis IMU', {'acceleration', 'gyroscope'}),
    ('6-DOF accelerometer and magnetometer', {'acceleration', 'magnetic_field'}),
    ('accelerometer, gyroscope and magnetometer', {'acceleration', 'gyroscope', 'magnetic_field'}),
    ('VOC sensor with temperature compensation and humidity compensation', {'gas', 'voc'}),
    ('temperature sensor with temperature compensation', {'temperature'}),
])
def test_measure_keywords_require_physical_channels(text, expected):
    from scrapers.common import infer_measures

    assert set(infer_measures(text)) == expected


@pytest.mark.parametrize('measures,description,expected', [
    ({'co2'}, '', None),
    ({'particulate'}, '', None),
    ({'current'}, 'power monitor and energy meter', None),
    ({'current'}, 'shunt-based current monitor', 'shunt'),
    ({'co2'}, 'photoacoustic carbon dioxide sensor', 'photoacoustic'),
    ({'co2'}, 'NDIR carbon dioxide sensor', 'ndir'),
])
def test_type_inference_requires_mechanism_evidence(measures, description, expected):
    merged = {'custom': {'type': None, 'measures': measures, 'description': description}}
    enrich_types(merged, quiet=True)
    assert merged['custom']['type'] == expected


@pytest.mark.parametrize('sensor_id,expected', [
    ('phprobe', ['analog']), ('pt1000probe', ['analog']), ('flowmeter', ['gpio']),
    ('surveyordo', ['analog']), ('ezoph', ['i2c', 'uart']), ('phoem', ['i2c']),
    ('unknown', []),
])
def test_atlas_product_interfaces_do_not_come_from_reader_links(sensor_id, expected):
    from scrapers.atlas_scientific import product_protocols

    assert product_protocols(sensor_id) == expected


@pytest.mark.parametrize('title,body,model,expected', [
    ('MB7040 I2CXL-MaxSonar-WR', '', 'MB7040', ['i2c']),
    ('MB7137 I2CXL-TrashSonar-WR', '', 'MB7137', ['i2c']),
    ('MB8000 ToF MaxLidar', '', 'MB8000', ['i2c', 'uart']),
    ('MB1403 HRUSB-MaxSonar-EZ0', '', 'MB1403', ['usb']),
    ('MB1001 ParkSonar-EZ-72', '', 'MB1001', ['gpio', 'uart']),
    ('MB1300 XL-MaxSonar-AE0', '', 'MB1300', ['analog', 'uart']),
    ('MB1000 LV-MaxSonar-EZ0', '', 'MB1000', ['analog', 'pwm', 'uart']),
    ('MB7850 TankSensor', 'RS232 serial, analog voltage, analog envelope', 'MB7850', ['analog', 'uart']),
    ('Kiosk sensor', '', 'MB1712', ['i2c']),
    ('Unknown product', '', 'MB9999', []),
])
def test_maxbotix_product_interfaces(title, body, model, expected):
    from scrapers.maxbotix import product_protocols

    assert product_protocols(title, body, model) == expected


def test_no_manufacturer_wide_probe_or_maxbotix_protocol_default():
    merged = {
        'customprobe': {'protocols': set(), 'sources': ['atlas_scientific']},
        'mb9999': {'protocols': set(), 'sources': ['maxbotix']},
    }
    enrich_protocols(merged, quiet=True)
    assert not merged['customprobe']['protocols']
    assert not merged['mb9999']['protocols']


def test_esphome_aqi_does_not_create_a_gas_channel():
    from scrapers.esphome import KNOWN_IC_MEASURES, _extract_esphome_measures

    assert _extract_esphome_measures('DEVICE_CLASS_AQI UNIT_MICROGRAMS_PER_CUBIC_METER') == {'particulate'}
    assert KNOWN_IC_MEASURES['ads1115'] == ['voltage']


@pytest.mark.parametrize('row,expected', [
    # Actual Winsen thermopile and electrochemical table rows that polluted VDD.
    ('<td>Noise voltage</td><td>38</td><td>nV/Hz1/2</td><td>25℃</td>', None),
    ('<td>Noise voltage</td><td>45</td><td>nV/Hz1/2</td>', None),
    ('<td>Bias voltage</td><td>10Ω (recommended)</td>', None),
    ('<td>Working voltage</td><td>38</td>', None),
    ('<td>Heater Voltage</td><td>VH</td><td>5V±0.1V</td>', None),
    ('<td>Loop Voltage</td><td>VC</td><td>≤24V DC</td>', None),
    ('<td>Working voltage</td><td>DC (5±0.1)V</td>', '4.9-5.1'),
    ('<td>Working voltage (V)</td><td>3.0±0.1</td>', '2.9-3.1'),
    ('<td>Supply voltage</td><td>3.3V±10%</td>', '2.97-3.63'),
    ('<td>I/O supply voltage</td><td>3.3V</td>', None),
    ('<td>Voltage</td><td>VDD</td><td>2.7</td><td>3</td><td>3.3</td><td>V</td>', '2.7-3.3'),
    ('<td>Working voltage</td><td>3.3V / 5V</td>', None),
    ('<td>WorkingVoltage</td><td>3.6~5VDC (Require powered by safety barrier)</td>', '3.6-5'),
    ('<td>Working Voltage</td><td>5V±0.5V (DC),Ripple≤50mV</td>', '4.5-5.5'),
    ('<td>Operating voltage</td><td>5V (Carrying capacity not less than 2A)</td>', '5'),
    ('<td>nominal voltage</td><td>V</td><td>3.1-5.0</td>', '3.1-5'),
    ('<td>nominal voltage</td><td>V</td><td>3.1-5.0</td><td></td>', '3.1-5'),
    ('<td>Supply Voltage</td><td>Min 1.8V; Typical 3.3V; Max 3.6V</td>', '1.8-3.6'),
])
def test_winsen_voltage_requires_supply_label_and_volt_unit(row, expected):
    from scrapers.winsen import _extract_specs, _extract_voltage

    assert _extract_voltage(_extract_specs(f'<table><tr>{row}</tr></table>')) == expected


@pytest.mark.parametrize('feature,expected', [
    ('Output voltage: 0-5V', None),
    ('Noise voltage: 38nV/Hz1/2', None),
    ('Operating voltage: 5', None),
    ('Operating voltage: 3.3V/5V', None),
    ('Operating voltage: 5V±5%', '4.75-5.25'),
    ('Operating voltage: 2.7V to 5.5V', '2.7-5.5'),
])
def test_bestmodules_voltage_requires_supply_label_and_volt_unit(feature, expected):
    from scrapers.bestmodules import _extract_voltage

    assert _extract_voltage([feature]) == expected


@pytest.mark.parametrize('prefix', [
    '7Semi', 'Microfire', 'IoTy', 'HLK', 'Omron', 'My', 'Adafruit',
    'SparkFun_', 'DFRobot_', 'Arduino_', 'Adafruit_CircuitPython_',
])
@pytest.mark.parametrize('sid', ['24ghzradar', 'a02yyuw', 'rs232'])
def test_known_identity_lookup_handles_digit_first_models_and_aliases(prefix, sid, monkeypatch):
    from build_sensor_db import resolve_id
    from scrapers import common

    known = {'24ghzradar', 'a02yyuw', 'rs232'}
    monkeypatch.setattr(common, '_known_sensor_ids', lambda: known)
    assert common.normalize_sensor_id(prefix + sid) == sid
    assert resolve_id(prefix + sid, {'rs232': 'a02yyuw'}, known) == (
        'a02yyuw' if sid == 'rs232' else sid)


def test_reviewer_rescrapes_resolve_before_curated_fields_and_exclusions(curated_data):
    import build_sensor_db as builder

    sensors = curated_data / 'sensors'
    (sensors / 'arduino.json').write_text(json.dumps({'sensors': [
        {'id': '7Semi24GHzRadar', 'name': '7Semi24GHzRadar', 'measures': ['distance']},
        {'id': 'MyA02YYUW', 'name': 'MyA02YYUW', 'measures': ['distance']},
        {'id': 'MyExcluded123', 'name': 'Software wrapper', 'measures': ['temperature']},
    ]}))
    (sensors / 'curated.json').write_text(json.dumps({
        'a02yyuw': {'voltage': _curated_field('3.3-5.0'), 'type': _curated_field('ultrasonic')},
        'excluded123': {'exclude': {**_curated_field(True), 'reason': 'Software wrapper'}},
    }))
    output = curated_data / 'sensor.db'
    builder.build(curated_data, output, verbose=False)
    with closing(sqlite3.connect(output)) as conn:
        assert conn.execute('SELECT id, voltage, type FROM sensors').fetchall() == [
            ('a02yyuw', '3.3-5.0', 'ultrasonic')]
        assert conn.execute('SELECT id FROM sensors_fts').fetchall() == [('a02yyuw',)]


@pytest.mark.parametrize('label', ['Supply voltage', 'Operating voltage', 'Supply/Operating voltage'])
@pytest.mark.parametrize('value,expected', [
    ('3.3V, 5V', None), ('3.3V / 5V', None), ('3.3V or 5V', '3.3 or 5'),
    ('3.3V/5V compatible', '3.3 or 5'), ('either 3.3V or 5V', '3.3 or 5'),
    ('4.5-5.5V or 3.0-3.6V', '3-3.6 or 4.5-5.5'),
    ('1.62-1.98 or 2.97-3.63V', '1.62-1.98 or 2.97-3.63'),
    # Overlapping alternatives would read as selectable modes: give their common range.
    ('3.0-5.5 or 3.0-3.6V', '3-3.6'), ('2.7-5.5V or 3.3V', '3.3'), ('3.3V or 3.3V', '3.3'),
    ('1.8-3.6V or 2.0-5.5V or 4.0-5.5V', None),
    ('3.3V±10% or 5V±10%', '2.97-3.63 or 4.5-5.5'),
    ('3.3V or unspecified', None),
    ('both 3.3V, 5V required', None),
    ('3.3V/5V compatible max', None),
    ('5 V max', None), ('max 5 V', None), ('5 V maximum', None), ('3.3 V min', None),
    # Ceilings in words, negative numbers (absolute-maximum rows) and mV/kV are not supplies
    ('up to 5V', None), ('less than 5V', None), ('below 3.6V', None), ('not exceeding 5.5V', None),
    ('-5V', None), ('-0.3~3.6V', None), ('3.3mV', None), ('3.3 - 5V', '3.3-5'),
    ('Min 1.8V; Typical 3.3V; Max 3.6V', '1.8-3.6'),
    ('5V±0.5V (DC),Ripple≤50mV', '4.5-5.5'),
])
def test_supply_voltage_options_and_one_sided_bounds(label, value, expected):
    from scrapers.common import parse_supply_voltage

    assert parse_supply_voltage(label, value) == expected


@pytest.mark.parametrize('summary', ['', '<table><tr><td>Model</td><td>TEST123</td></tr></table>'])
@pytest.mark.parametrize('body,expected', [
    ('<tr><td>Working voltage</td><td>2.7</td><td>3.0</td><td>3.3</td><td>V</td></tr>', '2.7-3.3'),
    ('<tr><td>Absolute maximum ratings</td></tr><tr><td>Supply voltage</td><td>6V</td></tr>', None),
    ('<tr><td>Maximum limit</td></tr><tr><td>Supply voltage</td><td>6V</td></tr>', None),
    ('<tr><td>Supply/Operating voltage</td><td>3.3V, 5V</td></tr>', None),
    ('<tr><td>Supply/Operating voltage</td><td>5 V max</td></tr>', None),
    ('<tr><td>Supply/Operating voltage</td><td>3.3V/5V compatible</td></tr>', '3.3 or 5'),
    ('<tr><td>Supply voltage</td><td>1.62-1.98 or 2.97-3.63V</td></tr>', '1.62-1.98 or 2.97-3.63'),
])
def test_winsen_first_pass_uses_range_and_absolute_rating_guards(summary, body, expected):
    from scrapers.winsen import _extract_specs, _extract_voltage

    assert _extract_voltage(_extract_specs(summary + '<table>' + body + '</table>')) == expected


@pytest.mark.parametrize('feature,expected', [
    ('Supply/Operating voltage: 3.3V, 5V', None),
    ('Supply/Operating voltage: 5 V max', None),
    ('Supply/Operating voltage: 3.3V/5V compatible', '3.3 or 5'),
    ('Supply voltage: 1.62-1.98 or 2.97-3.63V', '1.62-1.98 or 2.97-3.63'),
])
def test_bestmodules_uses_shared_supply_options_rule(feature, expected):
    from scrapers.bestmodules import _extract_voltage

    assert _extract_voltage([feature]) == expected


def test_winsen_headingless_ratings_table_cannot_override_operating_table():
    from scrapers.winsen import _extract_specs, _extract_voltage

    # Saved RDA223/RDA223-F pages omit external headings from their tables.
    ratings = ('<table><tr><td>Parameter</td><td>Symbol</td><td>Min</td><td>Max</td><td>Unit</td></tr>'
               '<tr><td>Supply voltage</td><td>VDD</td><td>0.3</td><td>5.5</td><td>V</td></tr>'
               '<tr><td>Storage temperature</td><td>TST</td><td>-40</td><td>125</td><td>℃</td></tr></table>')
    operating = ('<table><tr><td>Voltage</td><td>VDD</td><td>2.2</td><td>3.0</td><td>5.0</td><td>V</td></tr></table>')
    assert _extract_voltage(_extract_specs(ratings)) is None
    assert _extract_voltage(_extract_specs('<table></table>' + ratings + operating)) == '2.2-5'


@pytest.mark.parametrize('feature,expected', [
    ('Supply Voltage: DC 3.3V - 5.5V for the fingerprint sensor module, 2.2V – 5.5V for the touch IC', '3.3-5.5'),
    ('Supply Voltage: DC 3.3V ~ 6V for the fingerprint sensor module, 3.3V for the touch IC', '3.3-6'),
])
def test_auxiliary_ic_rail_is_separate_from_sensor_module_supply(feature, expected):
    from scrapers.bestmodules import _extract_voltage

    assert _extract_voltage([feature]) == expected


@pytest.mark.parametrize('raw,expected', [
    ('MQ-5 Sensor. Range: 300～10000ppm（CH4,C3H8）', 'MQ-5 Sensor. Range: 300~10000ppm(CH4,C3H8)'),
    ('Target: benzene，toluene、smoke', 'Target: benzene, toluene, smoke'),
    ('Target: Methane (CH₄), CO₂', 'Target: Methane (CH4), CO2'),
    ('WPCK07 Diffussed\xa0Silicon  Pressure​', 'WPCK07 Diffussed Silicon Pressure'),
    ('Accuracy： ◆ ±0.2℃', 'Accuracy: - ±0.2℃'),
    ('Würth Elektronik WSEN-HIDS', 'Würth Elektronik WSEN-HIDS'),
    (None, None),
])
def test_stored_descriptions_use_plain_punctuation(raw, expected):
    """Maker pages' full-width punctuation and subscript digits hid "CH4"/"CO2" from search."""
    from build_sensor_db import tidy_text

    assert tidy_text(raw) == expected


# The 2026-11-10 live scrape found 52 known parts with no measures, so they were
# carried as "missed" and would drop after three scrapes, taking their curated
# entries with them (an unknown curated ID fails the build that gates the scrape).
@pytest.mark.parametrize('text,expected', [
    ('ADIS1647x 6-DoF MEMS IMU with SPI connection', ['acceleration', 'gyroscope']),
    ('STMicroelectronics LSM6DSV16X 6-axis IMU (Inertial Measurement Unit)', ['acceleration', 'gyroscope']),
    ('ICM45605S High-precision 6-axis motion tracking device', ['acceleration', 'gyroscope']),
    ('STM32duino LSM6DSR iNEMO inertial measurement unit.', ['acceleration', 'gyroscope']),
    ('VEGA_BMI088 Library for communicating with the Bosch BMI088 6 axis IMU.', ['acceleration', 'gyroscope']),
    ('Adafruit 9DOF Library for the Adafruit 9DOF Breakout.', ['acceleration', 'gyroscope']),
    # A named inertial or magnetic measure wins: no gyroscope is invented
    ('QMC5883L 3-axis magnetometer for IMU projects', ['magnetic_field']),
    ('LIS3DH accelerometer for 6DOF IMU', ['acceleration']),
    # Nine axes always include a gyroscope, even when the text names only the accelerometer
    ('An incredibly precise 9DoF orientation sensor featuring 14-bit accelerometer fusion', ['acceleration', 'gyroscope']),
    ('6-DOF accelerometer and magnetometer', ['acceleration', 'magnetic_field']),
    ('Reefwing_xIMU3 Arduino Library for the xIMU3 GUI.', []),
])
def test_imu_wording_without_a_named_measure_means_accelerometer_and_gyroscope(text, expected):
    from scrapers.common import infer_measures

    assert infer_measures(text) == expected


def test_scrapers_keep_parts_whose_text_names_no_measure():
    from scrapers.arduino import KNOWN_IC_MEASURES as arduino
    from scrapers.zephyr import KNOWN_IC_MEASURES as zephyr

    assert {k: arduino[k] for k in ('ad7194', 'ads122c04', 'mcp3427', 'tla2021')} == dict.fromkeys(
        ('ad7194', 'ads122c04', 'mcp3427', 'tla2021'), ['voltage'])
    assert arduino['ina229'] == ['current', 'voltage']
    assert zephyr['icm42686'] == ['acceleration', 'gyroscope'] and zephyr['max32664c'] == ['biometric']


@pytest.mark.parametrize('title,measures', [
    ('WAP01 Piezoelectric Acceleration Sensor: Precise Vibration Monitoring', ['acceleration', 'vibration']),
    ('WVV01 Piezoelectric Velocity Sensor: Stable IEPE Monitoring for Industrial Equipment', ['vibration']),
    ('ZH401- Light Sensor. Range: 1500～6000lx', ['light']),
    ('ZW-HC101 On-line Water Conductivity Sensor. Range: 0.01～20μS/cm', ['conductivity', 'water_quality']),
    ('ZW-RCl201 Residual Chlorine Detection Module', ['water_quality']),
    ('ZPH07- Lithium Battery Aerosol Monitoring Sensor. Range: 0～10000μg/m³', ['particulate']),
    ('ME4-Cl2 Chlorine Gas Sensor', ['gas']),
    ('MH-T5052B Infrared Sulfur Hexafluoride Sensor. Target: SF6', ['gas']),
])
def test_winsen_non_gas_products_are_not_gas_sensors(title, measures):
    """Winsen's classifier defaulted every unmatched product to gas: its vibration, light and
    water-quality sensors were listed under gas in 0.8.24."""
    from scrapers.winsen import SKIP_KEYWORDS, _classify_sensor

    assert sorted(_classify_sensor(title, {})[0]) == measures
    assert "ion generator" in SKIP_KEYWORDS


def test_esphome_light_sensor_entity_without_a_device_class():
    """ESPHome dropped DEVICE_CLASS_ILLUMINANCE from LD2410/LD2412's unitless light entity
    (2026-11-06); Hi-Link's modules still have a photodiode that reports it."""
    from scrapers.esphome import _extract_esphome_measures

    ld2410 = ("from esphome.const import CONF_LIGHT, DEVICE_CLASS_DISTANCE, ICON_LIGHTBULB\n"
              "CONFIG_SCHEMA = {\n    cv.Optional(CONF_LIGHT): sensor.sensor_schema(\n"
              "        icon=ICON_LIGHTBULB,\n    ),\n"
              "    cv.Optional(CONF_DETECTION_DISTANCE): sensor.sensor_schema(device_class=DEVICE_CLASS_DISTANCE),\n}")
    assert _extract_esphome_measures(ld2410) == {"light", "distance"}
    # CONF_LIGHT naming a light output (partition, Gree switch) is not light sensing
    output = "CONFIG_SCHEMA = cv.Schema({cv.Required(CONF_LIGHT): cv.use_id(light.LightState)})"
    assert _extract_esphome_measures(output) == set()


def test_esphome_altitude_and_rainfall_are_not_distance():
    """GY-39's computed altitude (UNIT_METER, DEVICE_CLASS_DISTANCE) and Hydreon's rainfall in mm
    made both "distance" sensors; Hydreon's rain never registered (2026-11-10)."""
    from scrapers.esphome import _extract_esphome_measures

    gy39 = ("from esphome.const import (\n    CONF_ALTITUDE,\n    CONF_PRESSURE,\n    DEVICE_CLASS_DISTANCE,\n"
            "    UNIT_METER,\n    UNIT_PASCAL,\n)\nCONFIG_SCHEMA = {\n"
            "    cv.Optional(CONF_PRESSURE): sensor.sensor_schema(unit_of_measurement=UNIT_PASCAL),\n"
            "    cv.Optional(CONF_ALTITUDE): sensor.sensor_schema(\n        unit_of_measurement=UNIT_METER,\n"
            "        device_class=DEVICE_CLASS_DISTANCE,\n    ),\n}")
    assert _extract_esphome_measures(gy39) == {"pressure"}
    rain = ("from esphome.const import DEVICE_CLASS_PRECIPITATION, UNIT_MILLIMETER\n"
            "ACC = sensor.sensor_schema(unit_of_measurement=UNIT_MILLIMETER, device_class=DEVICE_CLASS_PRECIPITATION)")
    assert _extract_esphome_measures(rain) == {"rain"}
    # a real distance entity still counts
    tof = "cv.Optional(CONF_DISTANCE): sensor.sensor_schema(unit_of_measurement=UNIT_METER)"
    assert _extract_esphome_measures(tof) == {"distance"}


def test_esphome_links_point_at_pages_that_exist():
    """44 of 224 guessed esphome.io/components/sensor/<name>.html links were 404 (2026-11-10):
    dev-only components, pages outside components/sensor/, bus-suffixed page names."""
    from scrapers.esphome import esphome_docs_pages_from_paths, esphome_docs_url

    current = esphome_docs_pages_from_paths([
        "src/content/docs/components/sensor/bme280.mdx",
        "src/content/docs/components/sensor/honeywellabp2_i2c.mdx",
        "src/content/docs/components/hlk_fm22x.mdx",
        "src/content/docs/components/audio_adc/index.mdx",
        "src/content/docs/components/sensor/images/bme280-full.jpg",
    ])
    assert current == {"components/sensor/bme280", "components/sensor/honeywellabp2_i2c",
                       "components/hlk_fm22x", "components/audio_adc"}
    pages = {"current": current, "next": {"components/sensor/lis3dh"}}

    assert esphome_docs_url("bme280", ["bme280_i2c", "bme280_spi"], pages) == \
        "https://esphome.io/components/sensor/bme280/"
    assert esphome_docs_url("honeywellabp2", ["honeywellabp2_i2c"], pages) == \
        "https://esphome.io/components/sensor/honeywellabp2_i2c/"
    assert esphome_docs_url("hlk_fm22x", ["hlk_fm22x"], pages) == "https://esphome.io/components/hlk_fm22x/"
    # merged to dev, documented for the next release only
    assert esphome_docs_url("lis3dh", ["lis3dh"], pages) == "https://next.esphome.io/components/sensor/lis3dh/"
    # no page anywhere (or the docs clone failed): the component's source
    assert esphome_docs_url("tmc2209", ["tmc2209"], pages) == \
        "https://github.com/esphome/esphome/tree/dev/esphome/components/tmc2209"
    assert esphome_docs_url("bme280", ["bme280_i2c"], {}) == \
        "https://github.com/esphome/esphome/tree/dev/esphome/components/bme280_i2c"


def test_tasmota_unquoted_href_ends_at_the_tag():
    """Tasmota's table had href=https://https://gitlab.com/... unquoted; the link came out
    as 'https://https://gitlab.com/Parura57/icp10125-driver><strong>InvenSense'."""
    from scrapers.tasmota import tasmota_doc_url

    cell = ('<a href=https://https://gitlab.com/Parura57/icp10125-driver>'
            '<strong>InvenSense ICP-10125</strong></a>')
    assert tasmota_doc_url(cell) == "https://gitlab.com/Parura57/icp10125-driver"
    assert tasmota_doc_url('<a href=../AHT1x/>AHT10</a>') == "https://tasmota.github.io/docs/AHT1x/"
    assert tasmota_doc_url('<a href="https://github.com/x/y">Y</a>') == "https://github.com/x/y"
    assert tasmota_doc_url("<strong>Xadow Grove</strong>") is None


def test_thermal_radiation_is_temperature_not_ionizing_radiation():
    from scrapers.common import infer_measures
    from scrapers.winsen import _classify_sensor

    assert _classify_sensor('ZMT510-A non-contact boil-dry protection sensor',
                            {'detection_principle': 'Thermal radiation'})[0] == ['ir_temperature']
    assert 'radiation' not in infer_measures('Detects thermal radiation from the pan')
    assert 'radiation' in infer_measures('Geiger counter for gamma radiation')


@pytest.mark.parametrize('text,expected', [
    ('gas sensor with externally supplied temperature and humidity compensation', ['gas']),
    ('VOC sensor with humidity/temperature compensated output', ['gas', 'voc']),
    ('temperature and humidity sensor', ['humidity', 'temperature']),
])
def test_coordinated_compensation_inputs_are_not_measures(text, expected):
    from scrapers.common import infer_measures

    assert infer_measures(text) == expected


def test_winsen_rows_power_supply_output_and_rs485():
    """2026-11-10: "Power Supply | DC 9-36V" (ZW-C1021) was skipped, "Signal Output"/"Output Interface"
    rows were ignored, RS485 modules defaulted to UART, a title kept "| Winsen", and once Power Supply
    rows were read, WPCK68's "3.3VDC for I²C; 3.6VDC for 0.2-2.3V" came out as a 0.2-2.3V supply."""
    from scrapers.common import parse_supply_voltage
    from scrapers.winsen import _clean_title, _extract_protocols, _is_output_key, _is_supply_key

    assert _is_supply_key("power supply") and _is_supply_key("working voltage")
    assert not _is_supply_key("power consumption")
    assert parse_supply_voltage("power supply", "DC 9-36V") == "9-36"
    assert parse_supply_voltage("power supply", "3.3VDC for I²C; 3.6VDC for 0.2-2.3V") is None
    assert all(_is_output_key(k) for k in ("output", "output signal", "signal output", "output interface", "output mode"))
    assert not _is_output_key("output voltage")
    # The 4-20 mA current loop is an analog output beside the RS485 (ZW-pH201, audit 2026-11-10)
    assert _extract_protocols("", {"output": "RS485 / (4–20) mA"}) == ["analog", "rs485"]
    assert _extract_protocols("", {"output": "RS485 serial"}) == ["rs485"]
    assert _extract_protocols("", {"output": "0–3.3 V analog voltage; TTL serial interface (3.3 V)"}) == ["analog", "uart"]
    assert _clean_title("ZW-ORP201 ORP Water Quality Detection Module | Winsen") == "ZW-ORP201 ORP Water Quality Detection Module"


def test_esphome_docs_listing_timeout_falls_back(monkeypatch, tmp_path):
    """A hung docs clone raised TimeoutExpired and failed the whole ESPHome source instead of
    falling back to source-tree links (pipeline review, 2026-11-10)."""
    import subprocess
    from scrapers import esphome

    def hang(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs.get("timeout"))

    monkeypatch.setattr(esphome.subprocess, "run", hang)
    assert esphome._esphome_docs_pages("current", str(tmp_path)) == set()


@pytest.mark.parametrize("text,expected", [
    ("Analog pH sensor module", ["ph", "water_quality"]),
    ("ORP sensor kit", ["orp"]),
    ("dissolved oxygen probe", ["dissolved_oxygen", "water_quality"]),
    ("for measuring the liquid with high electrical conductivity", ["conductivity"]),
    ("STC31 thermal conductivity CO2 sensor", ["co2"]),
    ("oxygen sensor", ["oxygen"]),
])
def test_water_quality_measures(text, expected):
    """pH, ORP, dissolved oxygen and conductivity are measures of their own; DFRobot's SEN0161 pH meter
    was only under water_quality, and dissolved oxygen also landed under the oxygen gas measure."""
    from scrapers.common import infer_measures
    assert infer_measures(text) == expected


@pytest.mark.parametrize("title,specs,expected", [
    ("ZW-pH201 pH Water Quality Detection Module", {"target_gas": "pH"}, ["ph", "water_quality"]),
    ("ZW-PH101 water quality sensor module", {}, ["ph", "water_quality"]),
    ("MW-ORP101 water quality detection sensor", {}, ["orp", "water_quality"]),
    ("ZW-O201 Dissolved Oxygen Detection Module", {}, ["dissolved_oxygen", "water_quality"]),
    ("ZW-NH101 Ammonia& Nitrogen Detection Module", {}, ["water_quality"]),
    ("ME3-PH3 Phosphine Electrochemical Gas Sensor", {"target_gas": "PH3"}, ["gas"]),
    ("ZE03-NH3 Ammonia Gas Module", {"target_gas": "NH3"}, ["gas", "nh3"]),
])
def test_winsen_water_quality_classification(title, specs, expected):
    from scrapers.winsen import _classify_sensor
    assert _classify_sensor(title, specs)[0] == expected


@pytest.mark.parametrize("value,expected", [
    ("5V DC; 4-20mA", "5"), ("24V DC 4-20mA", "24"), ("3.3V 10-20mA", "3.3"),      # a current range isn't volts
    ("DC 5V 0.5-4.5V", None), ("5V; 1-5V", None),                                 # a second voltage outside the range
    ("12V DC (9～16V DC)", "9-16"), ("DC 24V (9V-36V)", "9-36"), ("6–14 V (12 V DC recommended)", "6-14"),
    ("5V DC ± 5%", "4.75-5.25"), ("24V DC (±10%)", "21.6-26.4"), ("5V (regulated ±5%)", "4.75-5.25"),
    ("5V±0.1V (AC or DC)", "4.9-5.1"), ("Min 3.0V, Max 5.5V", "3-5.5"),
    ("DC 12V/24V", None),                                                          # a bare slash list stays rejected
])
def test_supply_voltage_review_round_two(value, expected):
    """Second review round, 2026-11-10: other-unit ranges, a second voltage beside a range, spacing
    before DC, "AC or DC" and a comma between Min and Max."""
    from scrapers.common import parse_supply_voltage
    assert parse_supply_voltage("Supply voltage", value) == expected


def test_platform_prose_ranks_below_hardware_text():
    """A description naming a software platform is library copy; an independent hardware text
    must win a tie with it (0.9.0 review: "Arduino Temp & Humidity Sensors for DHT11 and DHT22")."""
    from build_sensor_db import description_quality

    hardware = "Digital humidity and temperature sensor, 0-100% RH, single-wire interface"
    assert description_quality(hardware) == 2
    for library_copy in ("Arduino Temp & Humidity Sensors for DHT11 and DHT22",
                         "MicroPython DHT22 humidity sensor module",
                         "circuitpython humidity sensor helper"):
        assert description_quality(library_copy) == 1, library_copy
    # a platform name inside a longer word is not platform prose
    assert description_quality("Arduinoesque-free hardware text about a pressure sensor") == 2
    assert description_quality("") == -1


# ── Catalog audit, 2026-11-10: general causes behind 36 contradicted records ──────────────

def test_deneyap_board_titles_do_not_define_a_chip(tmp_path, monkeypatch):
    """A Deneyap board title gave its chip the board's other measures: "Deneyap Temperature&Humidity,
    Barometer Sensor SHT4X" (an SHT4x beside an MS5637) gave SHT4x pressure. Another library's text
    describes the chip; a board title alone is kept as the last resort."""
    import scrapers.arduino as arduino

    libs = [
        {"name": "Deneyap Sicaklik Nem Basinc Olcer", "category": "Sensors", "version": "1.0.0",
         "sentence": "Arduino library for Deneyap Temperature&Humidity, Barometer Sensor SHT4X",
         "repository": "https://github.com/deneyapkart/deneyap-sicaklik-nem-basinc-olcer-arduino-library.git"},
        {"name": "SHT4X", "category": "Sensors", "version": "1.0.0",
         "sentence": "Arduino library for the SHT4X temperature and humidity sensor.",
         "repository": "https://github.com/Sensirion/arduino-i2c-sht4x.git"},
        {"name": "Deneyap 6 Eksen Alaletsel Olcum Birimi", "category": "Sensors", "version": "1.0.0",
         "sentence": "Arduino library for Deneyap 6 Dof IMU LSM6DSM",
         "repository": "https://github.com/deneyapkart/deneyap-6-eksen.git"},
    ]

    class Index:
        def raise_for_status(self):
            pass

        def json(self):
            return {"libraries": libs}

    monkeypatch.setattr(arduino.wafer, "get", lambda *a, **k: Index())
    arduino.scrape_arduino(tmp_path)
    sensors = {s["id"]: s for s in json.loads((tmp_path / "arduino.json").read_text(encoding="utf-8"))["sensors"]}
    assert sensors["sht4x"]["measures"] == ["humidity", "temperature"]
    assert "Deneyap" not in sensors["sht4x"]["description"]
    # Only a board title describes the LSM6DSM: it still supplies the measures
    assert sensors["lsm6dsm"]["measures"] == ["acceleration", "gyroscope"]
    assert arduino.chip_texts(["Deneyap Kart compatible BME280 driver"]) == ["Deneyap Kart compatible BME280 driver"]


_ZH08_TABLE = """<table><tr><td>Model</td><td>ZH08</td></tr></table><table>
<tr><td>Types of Detection</td><td>PM1.0, PM2.5, PM10</td></tr>
<tr><td rowspan="2">Output</td><td>UART_TTL Output (3.3V level)</td></tr>
<tr><td>PWMOutput (3.3V level)</td></tr>
<tr><td>Working voltage</td><td>4.9～5.5V</td></tr></table>"""

_MHZ1911A_TABLE = """<table><tr><td>Model</td><td>MH-Z1911A</td></tr></table><table>
<tr><td>Interface level</td><td>3.3 V(Compatible with 5V)</td><td>Weight</td><td>5 g</td></tr>
<tr><td rowspan="2">Output signal</td><td>Serial Port (UART)(TTL level 3.3V)</td><td>Detection Range</td><td>400~10000ppm</td></tr>
<tr><td>PWM</td><td>Lifespan</td><td>&gt;10 years</td></tr></table>"""

_FRN20_TABLE = """<table><tr><td>Output signal:</td><td>Digital I&sup2;C &amp; Analog 0.5V～4.5VDC;</td></tr></table><table>
<tr><td rowspan="3">Output signal</td><td>Output</td><td>Digital I&sup2;C &amp; Analog 0.5V～4.5VDC</td><td>&nbsp;</td></tr>
<tr><td>IIC communication rate</td><td>100</td><td>kHz</td></tr>
<tr><td>Signal response time</td><td>&le;50</td><td>ms</td></tr></table>"""


@pytest.mark.parametrize("html,expected", [
    (_ZH08_TABLE, ["pwm", "uart"]),            # second output in a rowspan continuation row
    (_MHZ1911A_TABLE, ["pwm", "uart"]),        # continuation row of a two-pair table
    (_FRN20_TABLE, ["analog", "i2c"]),         # value in the third cell; sub-spec rows aren't outputs
])
def test_winsen_secondary_outputs_are_kept(html, expected):
    """The spec table's rowspan'd Output rows lost every output after the first (7 of 19 audited
    Winsen records: MH-Z19 PWM, ZH08 PWM, MH-441D analog, ZW-pH201 4-20 mA ...)."""
    from scrapers.winsen import _extract_protocols, _extract_specs
    assert _extract_protocols(html, _extract_specs(html)) == expected


@pytest.mark.parametrize("output,expected", [
    ("UART-TTL (3.3V compatible with 5V) 0.4~2.0V", ["analog", "uart"]),
    ("UART(3.0V); 0.4~2.0VDC(Requireoutput by safety barrier)", ["analog", "uart"]),
    ("IIC; 0.4-2V DC", ["analog", "i2c"]),
    ("0.5-4.5V / 4-20mA / I²C, Customizable", ["analog", "i2c"]),
    ("PWM, can be used as a 4-20mA control signal", ["pwm"]),
    ("CAN/LIN（Customizable）", ["can"]),
    ("LIN / PWM, Customizable", ["pwm"]),               # LIN has no catalog tag
    ("CAN, 485", ["can", "rs485"]),
    ("High and low levels can be used to drive relays; PWM output", ["gpio", "pwm"]),  # "can" the verb
    ("Low level/High resistance state（Customizable）", ["gpio"]),
    ("Serial Port (UART)(TTL level 3.3V)", ["uart"]),   # "TTL level" is not a switching output
])
def test_winsen_output_wording(output, expected):
    from scrapers.winsen import _extract_protocols
    assert _extract_protocols("", {"output": output}) == expected


@pytest.mark.parametrize("cells,expected", [
    ("<tr><td>Sensitivity</td><td>(0.8±0.15) µA/ppm</td></tr>", ["analog"]),               # ME3 cell
    ("<tr><td>Sensitivity</td><td>≥30nA/ppm</td></tr>", ["analog"]),
    ("<tr><td>Sensitivity(20.9%vol.)</td><td>（80~130）uA</td></tr>", ["analog"]),           # O2 cell
    ("<tr><td>sensitive materials resistance</td><td>RS</td><td>1KΩ～30KΩ</td></tr>", ["analog"]),  # GM-602B
    ("<tr><td>Sensitivity</td><td>±3%FS</td></tr>", []),                                     # a module spec
])
def test_winsen_bare_elements_are_analog(cells, expected):
    """A bare cell or chemiresistor has no output stage. The build's type defaults gave GM-xxxB MEMS
    gas chips an I2C bus (GM-602B, audited) and cells a UART."""
    from scrapers.winsen import _extract_protocols
    assert _extract_protocols(f"<table>{cells}</table>", {}) == expected


def test_winsen_heater_symbol_row_is_not_a_supply():
    """MQ303B's table swaps labels: "Loop Voltage | V H | 0.9V±0.1V" is the heater."""
    from scrapers.winsen import _extract_specs
    html = ("<table><tr><td>x</td><td>y</td></tr></table><table>"
            "<tr><td>Standard Circuit Conditions</td><td>Loop Voltage</td><td>V H</td><td>0.9V±0.1V AC or DC</td></tr>"
            "<tr><td>Heater Voltage</td><td>V c</td><td>≤6V DC</td></tr></table>")
    assert "voltage" not in _extract_specs(html)


def test_winsen_photoconductive_flame_cells_are_photoresistors():
    from scrapers.winsen import _classify_sensor
    assert _classify_sensor("REF-X2212 PbSe Infrared Photoconductivity Flame Sensor", {}) == (["flame"], "photoresistor")
    assert _classify_sensor("ZRP320 Pyro-electric Flame sensor module", {}) == (["flame"], "pyroelectric")


def test_winsen_page_outputs_replace_legacy_protocol_guesses():
    """IC_PROTOCOLS called WAV/WP-series parts UART modules; their pages say 4-20 mA or mV bridge.
    The table still fills a Winsen part whose page names no output."""
    import build_sensor_db as b
    named = {"wav01": {"sources": ["winsen"], "protocols": {"analog"}}}
    unnamed = {"wav01": {"sources": ["winsen"], "protocols": set()}}
    other = {"wav01": {"sources": ["arduino"], "protocols": {"analog"}}}
    for merged in (named, unnamed, other):
        enrich_protocols(merged, quiet=True)
    assert named["wav01"]["protocols"] == {"analog"}
    assert unnamed["wav01"]["protocols"] == set(b.IC_PROTOCOLS["wav01"])
    assert other["wav01"]["protocols"] == {"analog"} | set(b.IC_PROTOCOLS["wav01"])


def test_benewake_interfaces_come_from_the_product_menu():
    """Every Benewake part got UART+I2C; the menu gives CAN/RS-485-only, RS-232-only, Ethernet and
    I/O (switching output: TF-NOVA, audited) per model."""
    from scrapers.benewake import product_interfaces
    html = ('<a class="pro3_list" href="/tf-nova"><div class="pro3_item"> Interface<span>UART, I/O, I²C</span></div></a>'
            '<a class="pro3_list" href="/TF02i/index.html"><div class="pro3_item"> Interface<span>CAN, RS-485</span></div></a>'
            '<a class="pro3_list" href="/TFA170L/index.html"><div class="pro3_item"> Interface<span>RS-232</span></div></a>'
            '<a class="pro3_list" href="/hornrt/index.html"><div class="pro3_item"> Interface<span>1000Base-T</span></div></a>')
    assert product_interfaces(html) == {
        "/tf-nova": ["gpio", "i2c", "uart"], "/TF02i/index.html": ["can", "rs485"],
        "/TFA170L/index.html": ["rs232"], "/hornrt/index.html": [],
    }
    import build_sensor_db as b
    merged = {"tf02i": {"sources": ["benewake"], "protocols": {"can", "rs485"}, "type": "tof"}}
    enrich_protocols(merged, quiet=True)
    assert merged["tf02i"]["protocols"] == {"can", "rs485"}
    assert not hasattr(b, "BENEWAKE_PROTOCOLS")


@pytest.mark.parametrize("body,expected", [
    ("Ranges from 6 inches to 254 inches. 7-foot detection zone for proximity information", ["distance", "proximity", "ultrasonic"]),
    ("5 m maximum range ... plus a preset 1.5 m proximity zone.", ["distance", "proximity", "ultrasonic"]),
    ("Ranges from 6 inches to 254 inches with a 20Hz read rate. Widest detection field.", ["distance", "ultrasonic"]),
])
def test_maxbotix_proximity_zone_outputs(body, expected):
    """ParkSonar/ProxSonar and vehicle-detection sensors report a proximity zone (MB1002, audited)."""
    from scrapers.maxbotix import product_measures
    assert product_measures("ultrasonic", body) == expected


def test_load_cell_pressure_means_force():
    """SparkFun's "5kg of pressure (force)" tagged the TAL220B/TAL221 load cells with pressure."""
    from scrapers.common import infer_measures
    text = ("Load Cell - 5kg, Straight Bar (TAL220B) This straight bar load cell (sometimes called a strain gauge) "
            "can translate up to 5kg of pressure (force) into an electrical signal.")
    assert "pressure" not in infer_measures(text)
    assert "pressure" in infer_measures("Barometric pressure sensor (force-balanced housing)")


def test_thermopile_temperature_is_ir_temperature():
    """TMP006/TMP007, TSD305 and the Grid-EYE lacked ir_temperature beside MLX90614; FS3000 is a
    thermopile air-velocity sensor and reports no temperature."""
    from build_sensor_db import type_implied_measures
    assert type_implied_measures("thermopile", {"temperature"}) == {"ir_temperature"}
    assert type_implied_measures("thermopile", {"flow", "wind"}) == set()
    assert type_implied_measures("mems", {"temperature"}) == set()


@pytest.mark.parametrize("text,expected", [
    ("Aosong DHT (Digital-output Humidity and Temperature Sensor) The Aosong DHT family of sensors provide "
     "temperature and humidity measurements through a bidirectional serial digital signal.  The DHT11 ...",
     "Aosong DHT (Digital-output Humidity and Temperature Sensor) The Aosong DHT family of sensors provide "
     "temperature and humidity measurements through a bidirectional serial digital signal."),
    # No sentence end to keep: end at the last whole word (AD2S1210's "... excitation for reso..")
    ("x" * 120 + " provides sine wave excitation for resolvers and more words to pass the column yyyyyyyyyy",
     "x" * 120 + " provides sine wave excitation for resolvers and more words to pass the..."),
    ("ZP150 Odor Detection Module. Target: Hydrogen sulfide, ammonia, alcohol..",
     "ZP150 Odor Detection Module. Target: Hydrogen sulfide, ammonia, alcohol.."),  # the source's own "..", not a cut
])
def test_descriptions_end_at_a_sentence_or_word(text, expected):
    from build_sensor_db import fit_description, tidy_text
    fitted = fit_description(tidy_text(text))
    assert len(fitted) <= 200
    assert fitted == expected


def test_brand_names_inside_urls_survive_cleaning():
    """Removing "Adafruit" broke "https://cdn-shop.adafruit.com/datasheets/tmp007.pdf"."""
    text = "TMP007 Digital Temperature Sensor. See datasheet at https://cdn-shop.adafruit.com/datasheets/tmp007.pdf"
    assert clean_description(text) == text
    assert clean_description("Adafruit TMP007 sensor breakout") == "TMP007 sensor breakout"


@pytest.fixture(scope="module")
def real_audit_catalog(tmp_path_factory):
    import build_sensor_db as builder
    output = tmp_path_factory.mktemp("audit") / "sensor.db"
    builder.build(_REAL_DATA, output, verbose=False)
    conn = sqlite3.connect(output)
    yield conn
    conn.close()


@pytest.mark.parametrize("sid,field,expected", [
    ("mmc5603nj", "measures", ["magnetic_field", "temperature"]),
    ("mmc5603nj", "protocols", ["i2c", "i3c"]),
    ("sht4x", "measures", ["humidity", "temperature"]),
    ("bno086", "measures", ["acceleration", "gyroscope", "magnetic_field"]),
    ("bno086", "protocols", ["i2c", "spi", "uart"]),
    ("bno086", "manufacturer", "CEVA"),
    ("apds9950", "measures", ["color", "light", "proximity"]),
    ("tmp006", "measures", ["ir_temperature", "temperature"]),
    ("tmp007", "measures", ["ir_temperature", "temperature"]),
    ("gp2y0a41sk0f", "measures", ["distance", "proximity"]),
    ("ld2402", "measures", ["distance", "motion", "proximity", "radar"]),
    ("sp3s", "measures", ["gas", "voc"]),
    ("mb1002", "measures", ["distance", "proximity", "ultrasonic"]),
    ("tal220b", "measures", ["force", "weight"]),
    ("gm602b", "protocols", ["analog"]),
    ("pm2005", "protocols", ["i2c", "uart"]),
    ("bl0940", "protocols", ["spi", "uart"]),
    ("smt100", "protocols", ["analog", "rs485", "uart"]),
    ("mhz19", "protocols", ["pwm", "uart"]),
    ("zh08", "protocols", ["pwm", "uart"]),
    ("mh441d", "protocols", ["analog", "uart"]),
    ("zwph201", "protocols", ["analog", "rs485"]),
    ("wpch01", "protocols", ["analog", "i2c"]),
    ("hydreonrgxx", "protocols", ["gpio", "uart"]),
    ("hwt901b", "protocols", ["can", "rs232", "rs485", "uart"]),
    ("hwt901b", "type", "mems"),
    ("tfnova", "protocols", ["gpio", "i2c", "uart"]),
    ("bm32s2031", "protocols", ["gpio", "uart"]),
    ("bms36t001", "protocols", ["gpio", "uart"]),
    ("bm22s2021", "protocols", ["gpio", "uart"]),
    ("mht5052b", "type", "ndir"),
    ("frn20", "type", "thermal_conduction"),
    ("wpah01", "type", "resistive"),
    ("refx2212hbcd", "type", "photoresistor"),
    ("fcxmldx5", "type", "solid_electrolyte"),
    ("gy39", "manufacturer", "GY Electronics"),
    ("uft6336u", "name", "FT6336U"),
    ("xiaomilywsd02mmc", "name", "LYWSD02MMC"),
])
def test_audited_records_match_maker_sources(real_audit_catalog, sid, field, expected):
    """Real catalog build: each audited field (maker evidence in curated.json or a scraper/build fix)."""
    if field in ("measures", "protocols"):
        table, column = ("sensor_measures", "measure") if field == "measures" else ("sensor_protocols", "protocol")
        value = [r[0] for r in real_audit_catalog.execute(
            f"SELECT {column} FROM {table} WHERE sensor_id=? ORDER BY 1", (sid,))]
    else:
        value = real_audit_catalog.execute(f"SELECT {field} FROM sensors WHERE id=?", (sid,)).fetchone()[0]
    assert value == expected


@pytest.mark.parametrize("sid,needle", [
    ("tmp007", "infrared thermopile"), ("bl0940", "UART or SPI"), ("dfr0300", "K=1"),
    ("icp10100", "barometric pressure"), ("cap1203", "3-channel capacitive touch"),
    ("dht", "bidirectional serial digital signal."),
])
def test_audited_descriptions_name_the_part(real_audit_catalog, sid, needle):
    description = real_audit_catalog.execute("SELECT description FROM sensors WHERE id=?", (sid,)).fetchone()[0]
    assert needle in description


def test_winsen_features_list_outputs_join_the_table_outputs():
    """MH-711A's Features list says "Output method: UART, analog voltage signal, etc." while its spec
    table gives only IIC and 0.4-2V DC; related-product cards further down must not count."""
    from scrapers.winsen import _extract_protocols, _extract_specs

    html = (
        '<h4 class="text-6 pb-2">Features</h4><p><ul><li>Long lifespan</li>'
        "<li>Output method: UART, analog voltage signal, etc.</li></ul></p>"
        "<h4>Specifications</h4><table><tr><td>Model</td><td>MH-711A</td></tr></table>"
        '<table><tr><td rowspan="2">Output Signal</td><td>IIC</td></tr><tr><td>0.4-2V DC</td></tr></table>'
        "<h4>Related products</h4><ul><li>5. Multiple output modes: UART, PWM</li></ul>"
    )
    specs = _extract_specs(html)
    assert _extract_protocols(html, specs) == ["analog", "i2c", "uart"]


def test_winsen_thermopile_gas_detector_is_not_ir_temperature():
    """RTGA71 "Thermopile Gas Sensor" is the IR detector of an NDIR CO2 sensor; ZHMT101's
    "Infrared thermopile NDIR" with a field of view still reads a temperature without contact."""
    from scrapers.winsen import _classify_sensor

    measures, _ = _classify_sensor("RTGA71 Thermopile Gas Sensor", {"target_gas": "CO2"})
    assert "ir_temperature" not in measures and "co2" in measures
    measures, _ = _classify_sensor("ZHMT101- Life Presence Sensor",
                                   {"detection_principle": "Infrared thermopile NDIR", "target_gas": "Life form"})
    assert "ir_temperature" in measures
