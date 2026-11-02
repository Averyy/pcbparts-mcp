"""Reference-board data checks: summaries agree with the parsed boards, and the parser fixes that
produced wrong outlines, cut-off descriptions, false tags and shortened ESP32 names stay fixed."""

import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_boards_db import _parse_boards_md  # noqa: E402
from parse_boards import (  # noqa: E402
    build_description, extract_key_ics, extract_tags, normalize_value, parse_boards_md,
)
from parsers.kicad import _legacy_arc_extent  # noqa: E402

BOARDS_DIR = ROOT / "data" / "boards"
BOARDS = {d["slug"]: d for d in (yaml.safe_load(f.read_text(encoding="utf-8")) for f in BOARDS_DIR.glob("*.yaml"))}
REGISTRY = parse_boards_md(BOARDS_DIR / "BOARDS.md")

# Part-number-looking words in a Key Coverage text (a digit and two capitals: SIT1050T, ESP32-S3)
_NAME = re.compile(r"\b(?=[A-Za-z0-9+-]*\d)(?=[A-Za-z0-9+-]*[A-Z]{2})[A-Za-z][A-Za-z0-9+]*(?:-[A-Za-z0-9+]+)*\b")
# Interfaces, families and standards that aren't parts
_NOT_A_PART = re.compile(
    r"^(USB\d?|I2C|I2S|LTE|CAT-?M\d?|CERN|OHL|IEEE|CM[45]|RP\d|PCIE?\d*|DDR\d|LPDDR\d|HDMI\d*|RS-?\d+|GPS|"
    r"GNSS|ESP32|STM32|IP\d+|BLE\d*|SPI|QSPI|QFN\d*|SOT\d*|TO-?\d+|V\d|REV\w*|X\d+|AC|DC|PD\d*|3V3|5V|\d.*|"
    r".*-OHL.*|CERN-.*|MK\d|CAN\d*|LoRa\w*|NB-IoT|IPEX\d*|SMA|U\.FL|W\d+|2xAA|MIPI|DSI\d*|CSI\d*|N\d+|OSHWA|"
    r"PMOD\d*|JST\w*|SH\d|PH\d|XH\d|AA|AAA|CR\d+|18650|21700|E\d+|SD\d|UHS-\w+|M\d|NEMA\d+|Wi-?Fi\d*|BT\d|"
    r"SFP\+?|PoE\+?|802\.\w+|ISO\d+|EN\d+|IEC\d+|ANT\d|OLED\d*|TFT\d*)$", re.IGNORECASE)
# Words that name no part: licences, protocols, signals, measured quantities, joined tokens
_NOISE = {"GPL-3", "CC-BY-SA-3", "OHL-W-2", "DShot", "NMEA0183", "DMX512", "HUB75E", "CSI-2", "DDR3L", "FR4",
          "DB9", "SPI+I2C", "Sub-GHz+2", "CO2", "PM2", "PM2.5", "PT100", "PT1000", "GPIO1", "CC1", "CC2", "PX4",
          "QSD2", "MCP2518FD+MCP2558FD"}
# Named on purpose though not among the parsed parts: external modules a board connects to (radar,
# camera, NFC, PSU and StepStick modules), chips inside a named module or SiP, fitted parts the parse
# lost to reused library symbols, and family names. Checked against each board's source (2026-11-02).
_ACCEPTED = {
    "adafruit-ultimate-gps": {"MTK3339"},
    "adsbee-rf-board": {"RP2040"},
    "anavi-miracle-controller": {"WS2812B"},
    "anavi-thermometer": {"DHT22"},
    "beagleboard-pocketbeagle": {"AM3358"},
    "bgeigiescint": {"AFBR-S4N44P014M"},
    "canitcam-ov5640": {"OV5640"},
    "cubesat-ov5640-camera-board": {"OV5640", "OV2640"},
    "dangerous-prototypes-buspirate-5-rev10a": {"AiP74LVC1T45"},
    "duet-2-wifi-v1-04": {"ESP8266"},
    "eez-dib-mio168": {"SI8641BB"},
    "esp32-f9p-io-board": {"ZED-F9P"},
    "esp32-uwb-dw3000": {"DW3000"},
    "esphome-indoor-multi-sensor": {"HLK-LD2450", "HLK-LD2410B", "HLK-LD2420", "SEN0609", "HLK-LD2410S"},
    "espresence": {"HLK-LD2410"},
    "glasgow-interface-explorer": {"FX2LP"},
    "goodwatch": {"MSP430", "CC430F6137"},
    "healthypi-5": {"ATECC608B"},
    "healthypi-move-sensor-board": {"nRF5340"},
    "led-matrix-input-module": {"IS31FL3741A"},
    "lofive": {"RV32IMAC", "FE310"},
    "nfc-copy-cat": {"PN532"},
    "prntrboardv2": {"TMC2209", "TMC2660", "TMC2130"},
    "radar-speed-sign-controller": {"HB100"},
    "radar-speed-sign-hb100-amplifier": {"HB100"},
    "rp2040-radar-presence": {"HLK-LD2410"},
    "sparkfun-qwiic-relay": {"MMBT2222AL", "BAT20J"},
    "twisted-fields-driver-module": {"RP2040"},
    "usb-armory-mk-ii": {"SE050", "MX6ULL", "ATECC608B"},
    "zigbee-rotary-dimmer": {"IRM-01-5"},
}


def _names_not_on_board(slug: str) -> list[str]:
    board, coverage = BOARDS[slug], REGISTRY[slug]["key_coverage"]
    on_board = " ".join(str(c.get(k, "")) for c in board.get("components", [])
                        for k in ("value", "mpn", "description", "footprint", "ref")).upper()
    on_board += " " + " ".join(board.get("key_ics") or []).upper()
    missing = []
    for name in sorted(set(extract_key_ics(coverage)) | {m.group(0) for m in _NAME.finditer(coverage)}):
        if _NOT_A_PART.match(name) or name in _NOISE or name.endswith("-based"):
            continue
        stem = re.sub(r"(X+|[A-Z]?)$", "", name.upper())
        if name.upper() in on_board or (len(stem) >= 4 and stem in on_board):
            continue
        if name not in _ACCEPTED.get(slug, set()):
            missing.append(name)
    return missing


class TestSummariesMatchBoards:
    """BOARDS.md Key Coverage (served as key_coverage) named other parts than the boards had:
    "CAN 2.0 (MCP2562)" on a board with a SIT1050T, after a fix changed only the YAML."""

    def test_every_board_has_a_registry_row(self):
        assert sorted(set(BOARDS) - set(REGISTRY)) == []

    @pytest.mark.parametrize("slug", sorted(BOARDS))
    def test_key_coverage_names_parts_on_the_board(self, slug):
        assert _names_not_on_board(slug) == []

    def test_known_contradictions_are_gone(self):
        assert "SIT1050T" in REGISTRY["olimex-esp32-evb"]["key_coverage"]
        assert "MCP73871" in REGISTRY["adafruit-powerboost-1000c"]["key_coverage"]
        assert "LC709203F" in REGISTRY["adafruit-esp32-s3-feather"]["key_coverage"]
        assert "Crazyflie 1.0" in REGISTRY["crazyflie"]["key_coverage"]
        assert "MPPT" not in BOARDS["solarmeshtasticnode"]["description"]

    def test_symbol_name_is_not_the_fitted_part(self):
        # The iCEBreaker's schematic reuses an ICE5LP4K symbol for its iCE40UP5K
        assert BOARDS["icebreaker"]["key_ics"][0] == "iCE40UP5K"

    def test_boards_sharing_a_repo_keep_their_own_text(self):
        # Keyed by repo, the full iCEBreaker was described as the "ultra-compact" Bitsy
        coverage = _parse_boards_md(BOARDS_DIR / "BOARDS.md")
        assert coverage["icebreaker"] != coverage["icebreaker-bitsy"]
        assert "Ultra-compact" not in coverage["icebreaker"]
        assert all(coverage.get(slug) for slug in BOARDS)  # ZIP downloads (RPi CM4/CM5 IO) too


class TestBoardFields:
    @pytest.mark.parametrize("slug", sorted(BOARDS))
    def test_description_parentheses_are_closed(self, slug):
        description = BOARDS[slug].get("description", "")
        assert description.count("(") == description.count(")"), description

    @pytest.mark.parametrize("slug", sorted(slug for slug, b in BOARDS.items() if b.get("outline")))
    def test_outline_is_a_plausible_board(self, slug):
        outline = BOARDS[slug]["outline"]
        assert min(outline["width_mm"], outline["height_mm"]) >= 5, outline

    def test_new_reference_boards(self):
        assert {"BQ25622E", "MAX17260"} <= set(BOARDS["powerfeather-powerups"]["key_ics"])
        assert "SIM7000" in BOARDS["botletics-sim7000-shield-v5"]["key_ics"]
        assert "cellular" in BOARDS["botletics-sim7000-shield-v5"]["tags"]
        assert BOARDS["seeed-xiao-esp32-s3-sense"]["key_ics"][0] == "ESP32-S3R8"
        qt_py_chip = next(c for c in BOARDS["adafruit-qt-py-esp32-s3"]["components"] if c["ref"] == "X2")
        assert qt_py_chip["mpn"] == "ESP32-S3"  # its Eagle library says ESP32-S2


class TestParserFixes:
    def test_legacy_arc_is_bounded_by_its_sweep(self):
        # (gr_arc (start centre) (end first point) (angle sweep)): the smart plug, a 45 mm circle
        # drawn as two arcs, measured 45 x 1 mm when the centre was read as a point on the edge
        xs, ys = _legacy_arc_extent(["start", "177.5", "92.7"], ["end", "155", "93.2"], -177.45)
        assert max(xs) - min(xs) == pytest.approx(45, abs=0.1)
        assert max(ys) - min(ys) == pytest.approx(22.5, abs=0.6)
        xs, ys = _legacy_arc_extent(["start", "0", "0"], ["end", "10", "0"], 90)
        assert (min(xs), max(xs), min(ys), max(ys)) == pytest.approx((0, 10, 0, 10), abs=1e-9)

    def test_description_does_not_split_inside_parentheses(self):
        coverage = "Multi-sensor: ESP32-S3, radar modules (LD2410, LD2450), BME280"
        assert build_description(coverage) == "Multi-sensor: ESP32-S3, radar modules (LD2410, LD2450)"

    def test_espressif_names_keep_their_variant(self):
        assert normalize_value("ESP32-S3R8", "U1") == "ESP32-S3R8"
        assert normalize_value("ESP32-C3FH4", "U1") == "ESP32-C3FH4"
        assert normalize_value("ESP32-WROVER", "U1") == "ESP32-WROVER"
        assert normalize_value("AT25256B-SSHL-B", "U1") == "AT25256B"  # ordering suffixes still go

    def test_tags(self):
        assert "ham-radio" not in extract_tags("CAN 2.0 (SIT1050T), IR receiver/transmitter (VS1838B)")
        assert "cellular" not in extract_tags("SAW filter, LNA")  # "LTE" is inside "filter"
        assert "cellular" in extract_tags("SIM7000 LTE Cat-M/NB-IoT modem")

    def test_key_ics_from_more_makers(self):
        assert extract_key_ics("SIM7080G modem, SGM6029 buck, GD25Q64 flash, RT9080-3.3 LDO") == [
            "SIM7080G", "SGM6029", "GD25Q64", "RT9080"]
