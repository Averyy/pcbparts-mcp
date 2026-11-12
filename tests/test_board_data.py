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


@pytest.mark.parametrize("slug,ref,value,mpn", [
    ("chrono-vfd-driver", "C5", "100nF", None),
    ("chrono-vfd-driver", "R1", "10kohm", None),
    ("axiom-motor-controller", "C44", "680pF", None),
    # Stale Value field: upstream commit 25badce93e changed the part number and description to 47 pF
    ("yardstick-one", "C27", "47pF", "CL05C470JB5NNNC"),
    ("openmd-gan-motor-driver", "L1", "68uH", None),
    ("aqeye-air-quality-sensor", "U3", "LM66100DCKR", "LM66100DCKR"),
    ("beagleconnect-freedom", "R31", "1.2kohm", "RC0402FR-071K2L"),
    ("beagleconnect-freedom", "U6", "GD25Q16CEIGR", "GD25Q16CEIGR"),
    ("beagleconnect-freedom", "C34", "0ohm", None),
    ("uberamp1-8-channel-dsp-amp", "R165", "t3.6k", None),
])
def test_run7_placed_values_and_ordering_identities(slug, ref, value, mpn):
    from board_overrides import BOARD_OVERRIDES
    from parse_boards import Component, _apply_overrides
    part = next(c for c in BOARDS[slug]["components"] if c["ref"] == ref)
    assert part["value"] == value
    assert part.get("mpn") == mpn
    # A fresh parse must apply the same decision rather than resurrect a stale MPN.
    fresh = Component(ref=ref, value=value, footprint=part["footprint"], attributes={"mpn": "stale"})
    _apply_overrides(slug, [fresh])
    assert fresh.value == value
    assert fresh.attributes.get("mpn") == mpn
    assert (slug, ref) in BOARD_OVERRIDES


def test_run7_ratings_and_descriptions_agree_with_ordered_parts():
    def part(slug, ref):
        return next(c for c in BOARDS[slug]["components"] if c["ref"] == ref)
    assert part("usb-armory-mk-ii", "C6")["voltage"] == "10V"
    assert part("usb-armory-mk-ii", "C6")["tolerance"] == "20%"
    assert part("usb-armory-mk-ii", "R1")["tolerance"] == "5%"
    assert part("uberamp1-8-channel-dsp-amp", "C23")["voltage"] == "63V"
    assert "description" not in part("s3xy-bms-tesla-retrofit", "C42")
    assert "description" not in part("opensipm-bias-control", "IC1")
    assert part("hackrf-pro", "U30")["mpn"] == "ET3157"  # explicit Substitution property
    assert part("ulx3s", "D15")["mpn"] == "NSR0530HT1G"  # BOM lists MPN2 alternative

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
    def test_registered_source_paths_exist_in_cached_repo(self, slug):
        # ZIP downloads can retain a cache name from before the board was renamed.
        repo = ROOT / ".cache" / "repos" / BOARDS[slug]["source"].replace("/", "--")
        if not repo.is_dir():
            pytest.skip("Source repository is not cached")
        for field in ("schematic_path", "pcb_path", "bom_path"):
            if path := REGISTRY[slug].get(field):
                assert (repo / path).is_file(), f"{slug}: registered {field} does not exist: {repo / path}"

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
    # Bus Pirate 5's C603/R102 and the LED matrix module's R2/R5 are "DNF" (do not fit) and leave the
    # parts list like "DNP" parts do, as does the Bus Pirate's FCC logo
    @pytest.mark.parametrize("slug,components,nets", [
        ("dangerous-prototypes-buspirate-5-rev10a", 208, 183),
        ("eegfrontier", 29, 34),
        ("halpi2-rs-485", 45, 34),
        ("hv-flyback-converter", 28, 20),
        ("led-matrix-input-module", 29, 18),
        ("healthypi-5", 159, 123),
        ("hadesfcs", 204, 174),
        ("botletics-sim7000-shield-v5", 47, 46),
        ("electronic-load", 111, 79),
        ("ennoid-bms", 228, 152),
        ("ubertooth-one", 88, 71),
    ])
    def test_correct_root_and_layout_counts(self, slug, components, nets):
        board = BOARDS[slug]
        refs = {c["ref"] for c in board["components"]}
        assert len(refs) == len(board["components"]) == components
        assert len(board["nets"]) == nets
        assert all(len(net["pins"]) >= 2 for net in board["nets"])
        assert all(pin.split(".", 1)[0] in refs for net in board["nets"] for pin in net["pins"])

    @pytest.mark.parametrize("slug,source", [("ennoid-bms", "schematic"), ("ubertooth-one", "layout")])
    def test_recovered_legacy_connectivity_source(self, slug, source):
        assert BOARDS[slug]["format"] == "kicad_legacy"
        assert BOARDS[slug]["netlist_source"] == source

    @pytest.mark.parametrize("slug", ["hv-flyback-converter", "led-matrix-input-module"])
    def test_schematic_connectivity_has_pin_counts(self, slug):
        assert BOARDS[slug]["netlist_source"] == "schematic"
        # The data format omits pin_count for ordinary connected two-pin parts.
        assert all(c.get("pin_count", 2) >= 2 for c in BOARDS[slug]["components"])
        assert all(c.get("pin_count", 0) > 2 for c in BOARDS[slug]["components"] if c["ref"].startswith("U"))

    def test_bus_pirate_summary_covers_the_full_design(self):
        board = BOARDS["dangerous-prototypes-buspirate-5-rev10a"]
        parts = {c["ref"]: c for c in board["components"]}
        assert parts["U103"]["value"] == "RP2040"
        assert all(parts[f"U{n}"]["value"] == "AiP74LVC1T45GC363.TR" for n in range(301, 309))
        assert parts["LCD201"]["value"] == "TFT_20_QT200H1201"
        assert parts["LED720"]["value"] == "SK6812"
        assert parts["U501"]["value"] == parts["U502"]["value"] == "AIP74HC595TA"
        assert set(board["key_ics"]) <= {c["value"] for c in parts.values()}
        assert {"debug-tool", "level-shifting", "display", "led-driver", "power-supply", "current-sensing"} <= set(board["tags"])
        assert all(text in board["description"] for text in ("RP2040", "level shifters", "LCD", "LEDs", "PSU", "current sense"))

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


# Run 9: source-backed identity, impedance, copied-description and supplier-code fixes.
@pytest.mark.parametrize("slug,refs,fields", [('0104-usb-hub', 'C1', {'lcsc': 'C13585', 'mpn': None}),
 ('0104-usb-hub', 'C2 C3', {'lcsc': 'C15525', 'mpn': None}),
 ('0104-usb-hub', 'C4 C5 C6', {'lcsc': 'C15008', 'mpn': None}),
 ('0104-usb-hub', 'D4 D5 D6', {'lcsc': 'C72041', 'mpn': None}),
 ('0104-usb-hub', 'F1 F2 F3', {'lcsc': 'C883133', 'mpn': None}),
 ('0104-usb-hub', 'J1', {'lcsc': 'C165948', 'mpn': None}),
 ('0104-usb-hub', 'J2 J3 J4', {'lcsc': 'C386739', 'mpn': None}),
 ('0104-usb-hub', 'R1 R2', {'lcsc': 'C25905', 'mpn': None}),
 ('0104-usb-hub', 'R3 R4 R5', {'lcsc': 'C4109', 'mpn': None}),
 ('0104-usb-hub', 'SW1 SW2 SW3', {'lcsc': 'C194405', 'mpn': None}),
 ('0104-usb-hub', 'Y1', {'lcsc': 'C9002', 'mpn': None}),
 ('4-channel-rf-front-end', 'R5', {'mpn': 'CSR1206-0R002F1', 'value': '2mohm'}),
 ('adafruit-esp32-s3-feather', 'SW1 SW2', {'description': None}),
 ('adafruit-qt-py-esp32-s3', 'Q1 Q2', {'description': None}),
 ('beagleconnect-freedom',
  'L4',
  {'description': 'SMD FIXED Inductor 6.8UH-20%-550MA;0805',
   'manufacturer': 'TDK',
   'mpn': 'MLZ2012N6R8LT000'}),
 ('bus-pirate-6-rev2b', 'L201', {'mpn': 'CBW201209U300T', 'value': '30ohm'}),
 ('canitcam-ov5640', 'U2 U3', {'description': None}),
 ('cm5-minima-rev2', 'U602', {'description': None}),
 ('corevus-g-v0-6', 'C28 C29', {'lcsc': None}),
 ('cynthion', 'J3', {'lcsc': 'C42411', 'mpn': None}),
 ('eez-h24005', 'C112', {'mpn': 'EECS5R5H105', 'value': '1F'}),
 ('eez-h24005', 'VAR1 VAR2 VAR3 VAR4 ZD1 ZD11 ZD12 ZD14 ZD15 ZD6 ZD8 ZD9', {'description': None}),
 ('epdiy-v7', 'R20 R24', {'lcsc': None}),
 ('esp32-uwb-dw3000', 'U2', {'description': None}),
 ('eurorack-pmod', 'U8', {'value': 'LM4040BIM3-3.0/NOPB'}),
 ('hackeeg-ads1299-shield', 'IC2', {'description': None}),
 ('hadesfcs', 'U10', {'mpn': None}),
 ('healthypi-5', 'SW1 SW2 SW4 SW5', {'description': None}),
 ('icebreaker', 'L1 L2', {'value': '600ohm'}),
 ('internal-usb-hub', 'C114 C117 C38 C41 C43 C46 R19 R64 R65 R76 R85', {'lcsc': None}),
 ('internal-usb-hub', 'TH1', {'description': None}),
 ('ldo-leviathan-v1-3',
  'C103 C134 C140 C146 C147 C148 C150 C151 C152 C154 C156 C158 C159 C160 C161 C162 C163 C87 C98 C99',
  {'mpn': None}),
 ('ldo-leviathan-v1-3', 'R35 R36 R40 R41', {'lcsc': None}),
 ('lea-control-board', 'L201 L202', {'value': '600ohm'}),
 ('openmd-gan-motor-driver',
  'C1 C100 C101 C102 C103 C104 C105 C106 C107 C108 C12 C15 C18 C19 C2 C21 C23 C24 C26 C27 C3 C6 C7 C78 C79 '
  'C8 C80 C81 C82 C86 C87 C88 C89 C9 C91 C93 C94 C98 C99 R10 R15 R16 R18 R20 R32 R5',
  {'mpn': None}),
 ('opensipm-tia-v3', 'L2', {'mpn': None}),
 ('orangecrab', 'J3', {'lcsc': 'C167321', 'mpn': 'USB4105-GF-A', 'manufacturer': 'GCT'}),  # primary Mfg/PN over the PN_1 alternate
 ('particle-tracker-eval', 'L10', {'mpn': 'GZ1608D300TF', 'value': '30ohm'}),
 ('particle-tracker-eval', 'U5 U6', {'description': None}),
 ('pipad-cm4-logic-board', 'J4', {'description': None, 'manufacturer': None, 'mouser': None, 'mpn': None}),
 ('powerfeather-powerups', 'R13 U6', {'mpn': None}),
 ('protocentral-openox', 'SW2', {'description': None}),
 ('px4-fmuv2-pixhawk', 'D602 D904', {'description': None}),
 ('px4-optical-flow', 'D1', {'description': None}),
 ('radar-speed-sign-hb100-amplifier', 'J1 J2 J3 J4', {'mpn': None}),
 ('s3xy-bms-tesla-retrofit', 'C112 C34 C69', {'mpn': None}),
 ('rpi-cm4-io-board', 'U3', {'value': 'TRJG0926HENL'}),
 ('rpi-cm5-io-board-rev2', 'U3', {'value': 'TRJG0926HENL'}),
 ('seeed-recamera-b4-can',
  'FB2 FB3 FB4 FB5',
  {'description': None, 'manufacturer': None, 'mpn': None, 'prod_id': None}),
 ('seeed-wio-terminal', 'L6', {'mpn': 'CBC3225T100MR', 'value': '10uH'}),
 ('soldered-capacitive-soil', 'R8', {'mpn': 'tc33x-2-103e', 'value': '10kohm'}),
 ('soldered-drv8825-stepper', 'C1', {'mpn': '12101C335K4T2A', 'value': '3.3uF'}),
 ('soldered-drv8825-stepper', 'C5', {'mpn': '08051C103KAT2A', 'value': '10nF'}),
 ('soldered-drv8825-stepper', 'R4', {'mpn': 'tc33x-2-104e', 'value': '100kohm'}),
 ('sparkfun-lsm6dso', 'L1', {'value': '30ohm'}),
 ('sparkfun-thing-plus-esp32-s3', 'U1 U6', {'description': None}),
 ('sparkfun-um980-triband', 'L2', {'value': '30R@100MHz'}),
 ('tigard', 'U4', {'value': '93LC56BT-I/OT'}),
 ('twisted-fields-rp2040-base', 'C95 R20 R21', {'lcsc': None}),
 ('ulx3s', 'C2', {'digikey': None, 'mpn': 'CC0603JRNPO9BN101', 'newark': None})])
def test_run9_reviewed_source_corrections(slug, refs, fields):
    parts = {c["ref"]: c for c in BOARDS[slug]["components"]}
    for ref in refs.split():
        for field, expected in fields.items():
            assert parts[ref].get(field) == expected, (slug, ref, field)


def test_run9_preserves_unitless_and_unconventional_source_values():
    gardening = next(c for c in BOARDS["anavi-gardening-uhat"]["components"] if c["ref"] == "C1")
    assert gardening["value"] == "0.1"
    buffer = next(c for c in BOARDS["anavi-miracle-controller"]["components"] if c["ref"] == "L1")
    assert buffer["value"] == buffer["mpn"] == "SN74AHCT125D"
    assert buffer["pin_count"] == 14
