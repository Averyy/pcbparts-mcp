"""Tests for the Best Modules (Holtek) scraper's page parsing (no network)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from scrapers import bestmodules
from scrapers.bestmodules import (
    _clean_html,
    _extract_datasheet_url,
    _extract_features,
    _extract_measures,
    _extract_overview,
    _extract_protocols,
    _extract_sensor_type,
)

CATALOG = '<a href="https://www.bestmodulescorp.com/pub/media/amasty/amfile/attach/BMduino_SG_EN_V4.pdf">Module Catalog</a>'


def _file_link(name: str, file_id: int) -> str:
    return (f'<a href="https://www.bestmodulescorp.com/en/amfile/file/download/file/{file_id}/product/3/" '
            f'class="am-filelink" target="_blank">\n        {name}    </a>')


def _page(title: str, features: list[str], documents: str = "") -> str:
    items = "".join(f"<li>{f}</li>" for f in features)
    return (f"<html><head><title>{title}</title></head><body>{CATALOG}"
            f'<h1 class="page-title"><span class="base">{title}</span></h1>'
            f'<div class="product attribute description"><div class="value" id="product.info.description">'
            f"<p>PRODUCT FEATURES</p><ol>{items}</ol></div></div></div>"
            f'<div id="amfile_attachment">{documents}</div></body></html>')


class TestCleanHtml:
    def test_named_entities_decoded(self):
        assert _clean_html("Standby &lt; 50&mu;A&emsp;&ensp;@3.3V") == "Standby < 50μA @3.3V"

    def test_superscripts_and_subscripts_stay_attached(self):
        assert _clean_html("I<sup>2</sup>C, C<sub>2</sub>H<sub>5</sub>OH, 1000μg/m<sup>3</sup>") == (
            "I2C, C2H5OH, 1000μg/m3"
        )


class TestDatasheetUrl:
    def test_own_datasheet_not_the_site_catalog(self):
        page = _page("PIR", [], _file_link("PIR Sensor Quick Start Guide", 1678) + _file_link("Datasheet V1.50", 1615))
        assert _extract_datasheet_url(page) == (
            "https://www.bestmodulescorp.com/en/amfile/file/download/file/1615/product/3/"
        )

    def test_base_sensor_datasheet_for_a_bmcom_module(self):
        page = _page("PIR", [], _file_link("User's guide", 10) + _file_link("BM22S402x-1 datasheet", 11))
        assert _extract_datasheet_url(page).endswith("/file/11/product/3/")

    def test_users_guide_when_there_is_no_datasheet(self):
        page = _page("Module", [], _file_link("Arduino Library Guide V1.0.2", 20) + _file_link("User Guide V1.00", 21))
        assert _extract_datasheet_url(page).endswith("/file/21/product/3/")

    def test_users_guide_before_a_part_datasheet(self):
        # The sound detector's "LMV324 datasheet" is its op-amp's
        page = _page("Sound", [], _file_link("User's guide", 40) + _file_link("LMV324 datasheet", 41))
        assert _extract_datasheet_url(page).endswith("/file/40/product/3/")

    def test_part_datasheet_when_nothing_else(self):
        page = _page("Light", [], _file_link("Arduino library", 50) + _file_link("VEML7700 datasheet", 51))
        assert _extract_datasheet_url(page).endswith("/file/51/product/3/")

    def test_only_the_catalog_gives_none(self):
        assert _extract_datasheet_url(_page("Tools", [], _file_link("Arduino library", 30))) is None


class TestMeasures:
    def test_operating_temperature_is_not_a_measure(self):
        assert _extract_measures("5.8GHz Microwave Radar Sensor Module", ["Operating temperature: -40°C~85°C"]) == [
            "motion", "radar",
        ]

    def test_temperature_compensation_is_not_a_measure(self):
        features = [
            "Includes a temperature sensor for temperature compensation",
            "Integrated temperature sensor with temperature compensation",
            "Built-in temperature sensor with automatic temperature-compensation algorithm",
            "Built-in temperature and drift compensation",
            "Temperature compensation: -40℃ to 85℃",
        ]
        assert _extract_measures("PIR Motion Digital Sensor", features) == ["motion", "pir"]

    def test_temperature_measurement_line_counts_despite_resolution(self):
        features = ["Temperature measurement range: 0~60℃ (recommended 5℃~55℃) - Accuracy: ±0.8℃ - Resolution: 0.1℃"]
        assert _extract_measures("TDS Sensor Water Quality Detection Module", features) == [
            "temperature", "water_quality",
        ]

    def test_water_level(self):
        assert _extract_measures("Digital Water Level Sensor", ["Measurement range: 0~600mmH2O"]) == ["level"]

    def test_packing_list_is_not_a_measure(self):
        features = ["Packing List : - Infrared temperature measurement module x 1"]
        assert _extract_measures("PIR Detector Module", features) == ["motion", "pir"]


    def test_nothing_matched_is_empty_not_gas(self):
        features = ["Operating Voltage: 5.0V - 7.2V", "Angle control mode: controlled range 0°～140°"]
        assert _extract_measures("Digital Sub-Micro Servo (0.11kg-cm) BM22O2221-A", features) == []
        assert _extract_measures("Development Tools", []) == []

    def test_modules_the_gas_default_used_to_label(self):
        assert _extract_measures("Air Velocity Digital Sensor BM62S2301-1", ["Type: MEMS"]) == ["flow", "wind"]
        assert _extract_measures("BH45B1225 24-Bit ADC Module BMH23M001", []) == ["voltage"]
        assert _extract_measures("MPU-6050 Shake Detection Module BMS81M001", []) == ["vibration"]
        assert _extract_measures("AMG8833 IR Array Sensor Module BMS26M833", []) == ["ir_temperature"]

    def test_keywords_match_whole_words(self):
        # "light" in "time of flight" and "slightly", "dust" in "dustproof"
        assert _extract_measures("VL53L1X Time of Flight Ranging (ToF) Module BML36M001", []) == ["distance", "tof"]
        assert _extract_measures("Electrochemical Alcohol Module", ["The port sits slightly upstream"]) == ["gas"]
        assert _extract_measures("Radar Sensor Module", ["Includes lighting control function"]) == ["motion", "radar"]
        assert "particulate" not in _extract_measures("ToF Module", ["Waterproof & dustproof rating: IP68"])

    def test_operating_conditions_are_not_measures(self):
        assert _extract_measures("NDIR CO2 Digital Sensor", ["Operating humidity: 0 to 95%RH"]) == ["co2"]
        features = ["Operating Environment: Temperature 10°C to 40°C / Humidity <80% RH"]
        assert _extract_measures("Pulse Oximetry Module BMH83M101A", features) == ["biometric"]

    def test_ultrasonic_oxygen_module_measures_no_distance(self):
        title = "Ultrasonic Oxygen Concentration & Flow Detection Module BM62S5601-1"
        assert _extract_measures(title, []) == ["flow", "oxygen"]

    def test_soil_humidity_is_soil_moisture(self):
        title = "Soil Temperature and Moisture Detection Module BM25S2621-1"
        features = ["Humidity measurement - range: 0%RH~100%RH"]
        assert _extract_measures(title, features) == ["moisture", "soil_moisture", "temperature"]


class TestFeatures:
    def test_features_after_a_notice_block(self):
        # BME63M001: a notice closes three <div>s before the features list
        page = (
            '<div id="product.info.description"><div class="value"><div>'
            '<div class="red-block">Use the probe for its channel.</div></div></div></div>'
            '<div class="title"><b>PRODUCT FEATURES</b></div><div class="text"><ol>'
            "<li>Operating voltage: 3.3V~5.5V</li><li>Interface: UART (baud rate: 9600bps)</li></ol></div>"
        )
        assert _extract_features(page) == ["Operating voltage: 3.3V~5.5V", "Interface: UART (baud rate: 9600bps)"]

    def test_features_split_over_several_lists(self):
        page = (
            '<div id="product.info.description"><div class="title"><b>PRODUCT FEATURES</b></div>'
            "<ol><li>Operating voltage: 2.7V to 5.5V</li></ol>\n<ol><li>Interface: I2C / one-wire</li></ol>"
            '<div class="title"><b>DESCRIPTION</b></div><ol><li>Do not apply excessive pressure</li></ol>'
        )
        assert _extract_features(page) == ["Operating voltage: 2.7V to 5.5V", "Interface: I2C / one-wire"]

    def test_resources_lists_are_not_features(self):
        page = (
            '<div id="product.info.description"><p><strong>Features:</strong></p>'
            "<ol><li>UART interface</li></ol><p><strong>RESOURCES</strong></p>"
            "<ol><li>MCU: Holtek HT45F8650</li></ol>"
        )
        assert _extract_features(page) == ["UART interface"]


class TestProtocols:
    def test_one_wire(self):
        assert _extract_protocols(["Interface: I2C (address: 0x5C) / one-wire"]) == ["i2c", "one_wire"]

    def test_internal_adc_is_not_an_analog_output(self):
        assert _extract_protocols(["Integrated 16-bit ADC", "Interface: I2C (address: 0x68)"]) == ["i2c"]

    def test_audio_output_is_analog(self):
        features = ["Provide audio output interface", "Interface: I2C (address: 0x4B)"]
        assert _extract_protocols(features) == ["analog", "i2c"]

    def test_summary_fills_in_when_features_name_none(self):
        assert _extract_protocols([], "supports a UART interface to transmit SpO2 data") == ["uart"]

    def test_page_text_outside_features_and_summary_is_ignored(self):
        # bm25s2621 is RS485 only; its wiring notes mention a UART bridge
        page = _page("Soil Probe", ["Communication Interface: RS485 / Modbus RTU"]).replace(
            "</body>", "<p>If your controller only supports UART, use the RS485 bridge</p></body>"
        )
        features = _extract_features(page)
        assert _extract_protocols(features, _extract_overview(page)) == ["rs485"]


class TestSensorType:
    def test_word_boundaries(self):
        assert _extract_sensor_type("Weight Module", ["The plate shall be level"]) is None

    def test_infrared_thermometer_is_not_pyroelectric(self):
        assert _extract_sensor_type("Infrared Thermometer Module", ["Infrared thermopile sensor"]) == "thermopile"
        assert _extract_sensor_type("Proximity and Ambient Light Sensing Module", ["Infrared LED"]) is None


def test_i2c_written_with_superscript():
    page = _page("PIR", ["Optional communication interfaces: I<sup>2</sup>C or I/O"])
    features = _extract_features(page)
    assert features == ["Optional communication interfaces: I2C or I/O"]
    assert _extract_protocols(features, page) == ["i2c"]


class _Response:
    status_code = 200

    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        pass


def test_scrape_adds_datasheet_temperature_and_skips_compensation(tmp_path, monkeypatch):
    base = "https://www.bestmodulescorp.com/en"
    pages = {
        f"{base}/ht7m2126.html": _page(
            "Miniaturized PIR Module HT7M2126",
            ["Operating temperature: -10 ~ 60°C", "Integrated temperature sensor with temperature compensation",
             "Standby with detecting mode &lt; 50&mu;A"],
            _file_link("Datasheet V1.50", 1615),
        ),
        f"{base}/bm22s4221-1.html": _page(
            "PIR Motion Digital Sensor BM22S4221-1",
            ["Includes a temperature sensor for temperature compensation"],
            _file_link("Datasheet V1.00", 500),
        ),
    }
    listing = "".join(f'<a href="{url}">' for url in pages)

    class Session:
        def get(self, url, **kwargs):
            return _Response(listing if "sensor-module.html" in url else pages[url])

    monkeypatch.setattr(bestmodules, "make_session", lambda *a, **k: Session())
    bestmodules.scrape_bestmodules(tmp_path)

    sensors = {s["id"]: s for s in json.loads((tmp_path / "bestmodules.json").read_text(encoding="utf-8"))["sensors"]}
    # HT7M21xx datasheet: I2C register "Current Temperature (°C)"
    assert sensors["ht7m2126"]["measures"] == ["motion", "pir", "temperature"]
    assert sensors["ht7m2126"]["datasheet_url"].endswith("/file/1615/product/3/")
    assert "&mu;" not in sensors["ht7m2126"]["description"]
    # BM22S4221 datasheet: the sensor only compensates, no temperature read
    assert sensors["bm22s4221"]["measures"] == ["motion", "pir"]


def test_scrape_skips_pages_that_are_not_sensors(tmp_path, monkeypatch):
    base = "https://www.bestmodulescorp.com/en"
    pages = {
        f"{base}/bm22o2221-a.html": _page("Digital Sub-Micro Servo (0.11kg-cm) BM22O2221-A", ["Plastic Gear"]),
        f"{base}/bce-22s4421-1.html": _page("5.8GHz Microwave Radar Sensor Module Demo Board BCE-22S4421-1", []),
        f"{base}/bm22s4421-1.html": _page("5.8GHz Microwave Radar Sensor Module BM22S4421-1", ["UART interface"]),
    }
    listing = "".join(f'<a href="{url}">' for url in pages)

    class Session:
        def get(self, url, **kwargs):
            return _Response(listing if "sensor-module.html" in url else pages[url])

    monkeypatch.setattr(bestmodules, "make_session", lambda *a, **k: Session())
    bestmodules.scrape_bestmodules(tmp_path)

    output = json.loads((tmp_path / "bestmodules.json").read_text(encoding="utf-8"))
    assert [s["id"] for s in output["sensors"]] == ["bm22s4421"]
    assert output["stats"]["skipped"] == 2
