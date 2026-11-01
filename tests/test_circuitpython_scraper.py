"""Tests for the CircuitPython scraper's drivers.rst parsing (no network)."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from scrapers import circuitpython
from scrapers.circuitpython import extract_sensors, parse_drivers_rst

# Shaped like docs/drivers.rst in adafruit/Adafruit_CircuitPython_Bundle
DRIVERS_RST = """\
.. _adafruit-libndrivers:

Adafruit Sponsored Libraries and Drivers on GitHub
===================================================

These may or may not work with
`MicroPython <https://micropython.org>`_.

Helper Libraries
-----------------

Motor Helpers
^^^^^^^^^^^^^^

.. toctree::

    DRV2605 Haptic Motor Controller with temperature (adafruit_drv2605) <https://docs.circuitpython.org/projects/drv2605/en/latest/>
    EMC2101 Fan Controller and Temperature monitor (adafruit_emc2101) <https://docs.circuitpython.org/projects/emc2101/en/latest/>

Displays
--------

E-Paper / E-Ink
^^^^^^^^^^^^^^^^

.. toctree::

    SSD1306 OLED Display with temperature (adafruit_ssd1306) <https://docs.circuitpython.org/projects/ssd1306/en/latest/>

Motion Sensors
--------------

.. toctree::

    LSM6DS Accelerometer and Gyroscope (adafruit_lsm6ds) <https://docs.circuitpython.org/projects/lsm6ds/en/latest/>

Environmental Sensors
---------------------

.. toctree::

    BME280 Temperature, Humidity and Pressure sensor (adafruit_bme280) <https://docs.circuitpython.org/projects/bme280/en/latest/>

Light Sensors
-------------

.. toctree::

    TSL2591 High Dynamic Range Light Sensor (adafruit_tsl2591) <https://docs.circuitpython.org/projects/tsl2591/en/latest/>

Distance Sensors
----------------

.. toctree::

    VL53L0X ToF (adafruit_vl53l0x) <https://docs.circuitpython.org/projects/vl53l0x/en/latest/>

IO Expansion
------------

.. toctree::

    MCP230xx GPIO Expander (adafruit_mcp230xx) <https://docs.circuitpython.org/projects/mcp230xx/en/latest/>
    MPR121 Capacitive Touch Sensor (adafruit_mpr121) <https://docs.circuitpython.org/projects/mpr121/en/latest/>

Miscellaneous
-------------

.. toctree::

    INA219 High Side DC Current Sensor (adafruit_ina219) <https://docs.circuitpython.org/projects/ina219/en/latest/>
    RFM LoRa & Packet Radio (adafruit_rfm) <https://docs.circuitpython.org/projects/rfm/en/latest/>
"""


def _sensors_by_id(text: str = DRIVERS_RST) -> dict[str, dict]:
    sensors, _ = extract_sensors(parse_drivers_rst(text))
    return {s["id"]: s for s in sensors}


class TestParseDriversRst:
    def test_entries_filed_under_nearest_heading(self):
        sections = {title.split()[0]: section for section, _, title in parse_drivers_rst(DRIVERS_RST)}
        assert sections["DRV2605"] == "motor-helpers"
        assert sections["SSD1306"] == "e-paper-e-ink"
        assert sections["LSM6DS"] == "motion-sensors"
        assert sections["MPR121"] == "io-expansion"
        assert sections["INA219"] == "miscellaneous"

    def test_entry_url_and_title(self):
        entries = parse_drivers_rst(DRIVERS_RST)
        assert ("motion-sensors", "https://docs.circuitpython.org/projects/lsm6ds/en/latest/",
                "LSM6DS Accelerometer and Gyroscope (adafruit_lsm6ds)") in entries

    def test_only_toctree_entries(self):
        # The prose link to micropython.org is not a driver
        urls = [url for _, url, _ in parse_drivers_rst(DRIVERS_RST)]
        assert len(urls) == 11
        assert "https://micropython.org" not in urls

    def test_title_text_kept_raw(self):
        titles = [title for _, _, title in parse_drivers_rst(DRIVERS_RST)]
        assert "RFM LoRa & Packet Radio (adafruit_rfm)" in titles


class TestExtractSensors:
    def test_sensor_sections_included(self):
        sensors = _sensors_by_id()
        assert sensors["lsm6ds"]["measures"] == ["acceleration", "gyroscope"]
        assert sensors["bme280"]["measures"] == ["humidity", "pressure", "temperature"]
        assert sensors["tsl2591"]["platforms"] == ["circuitpython"]

    def test_distance_section_adds_base_measure(self):
        # "VL53L0X ToF" alone infers nothing; the section supplies distance
        assert _sensors_by_id()["vl53l0x"]["measures"] == ["distance"]

    def test_sensors_outside_sensor_sections_included(self):
        sensors = _sensors_by_id()
        assert sensors["mpr121"]["measures"] == ["touch"]          # IO Expansion
        assert sensors["emc2101"]["measures"] == ["temperature"]   # Motor Helpers
        assert sensors["ina219"]["measures"] == ["current"]        # Miscellaneous

    def test_non_sensors_outside_sensor_sections_skipped(self):
        sensors = _sensors_by_id()
        assert "mcp230xx" not in sensors   # no measure in the title
        assert "drv2605" not in sensors    # "motor" despite "temperature"
        assert "ssd1306" not in sensors    # "display" despite "temperature"

    def test_docs_url_and_description(self):
        sensor = _sensors_by_id()["mpr121"]
        assert sensor["urls"] == ["https://docs.circuitpython.org/projects/mpr121/en/latest/"]
        assert sensor["description"] == "MPR121 Capacitive Touch Sensor"

    def test_missing_sensor_section_raises(self):
        text = DRIVERS_RST.replace("Light Sensors\n-------------", "Light\n-----")
        with pytest.raises(ValueError, match="light-sensors"):
            extract_sensors(parse_drivers_rst(text))


class _Response:
    text = DRIVERS_RST

    def raise_for_status(self):
        pass


def test_scrape_writes_github_source(tmp_path, monkeypatch):
    requested = []

    def fake_get(url, **kwargs):
        requested.append(url)
        return _Response()

    monkeypatch.setattr(circuitpython.wafer, "get", fake_get)
    circuitpython.scrape_circuitpython(tmp_path)

    assert requested == [circuitpython.SOURCE_URL]
    assert circuitpython.SOURCE_URL.startswith("https://raw.githubusercontent.com/adafruit/")
    data = json.loads((tmp_path / "circuitpython.json").read_text(encoding="utf-8"))
    assert data["source_url"] == circuitpython.SOURCE_URL
    assert [s["id"] for s in data["sensors"]] == [
        "bme280", "emc2101", "ina219", "lsm6ds", "mpr121", "tsl2591", "vl53l0x",
    ]
    assert data["stats"]["sensor_count"] == 7
