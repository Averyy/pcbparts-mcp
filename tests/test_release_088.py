"""0.8.8: Espressif's own DevKits as reference boards (PADS layout + BOM), each focused pin's net, ZIP
boards' links and makers, and the ESP32 rule's DevKit facts (design-session idea report, 2026-11-03)."""

import sys
from pathlib import Path

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.design_rules import get_design_rules

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from parsers.pads import parse_pads  # noqa: E402

DEVKIT_C = "espressif-esp32-s3-devkitc-1"

# A two-part layout in PADS ASCII: parts in *PART*, connections as REF.PIN pairs under *ROUTE*
_ASC = """!PADS-POWERPCB-V2005.2-BASIC-250L! DESIGN DATABASE ASCII FILE 1.
*PCB*        GENERAL PARAMETERS OF THE PCB DESIGN
MAXIMUMLAYER 4              Maximum routing layer
*LINES*      LINES ITEMS
DRW1      BOARD    0      0      1
CLOSED 5   190500 0
0      0
30000000 0
30000000 15000000
0      15000000
0      0
*PART*       ITEMS
R1              R0402 1500000 3000000 90.000 G N 0 -1 0 -1 2
U1              SOT223 7500000 3000000 0.000 G M 0 -1 0 -1 2
*ROUTE*
*SIGNAL* EN 0 -2
R1.1                            U1.3
1500000 3000000 1 190500 1280
*SIGNAL* GND 0 -2
R1.2                            U1.2
*SIGNAL* N123 0 -2
U1.1                            U1.4
*POUR*       POUR ITEMS
"""


class TestPadsLayout:
    def test_parse(self, tmp_path):
        asc = tmp_path / "board.asc"
        asc.write_text(_ASC, encoding="latin-1")
        components, nets, positions, outline, rules = parse_pads(asc, None)
        assert [c.ref for c in components] == ["R1", "U1"] and components[1].footprint
        assert {n.name: n.pins for n in nets} == {"EN": ["R1.1", "U1.3"], "GND": ["R1.2", "U1.2"],
                                                  "N123": ["U1.1", "U1.4"]}
        assert (outline.width, outline.height) == (20.0, 10.0) and rules.layers == 4
        assert {p.ref: (p.x, p.y, p.side) for p in positions} == {"R1": (1.0, 2.0, "front"), "U1": (5.0, 2.0, "back")}

    def test_bom(self, tmp_path):
        openpyxl = pytest.importorskip("openpyxl")
        from parsers.pads import read_bom
        book = openpyxl.Workbook()
        sheet = book.active
        sheet.append(["BOM"])
        sheet.append(["ID", "Qty", "Ref Des", "Value", "Package", "ICs", "Description"])
        sheet.append([1, 2, "C1, C3", "0.1 uF/50V (10%)", "0402", "Capacitor", "Ceramic"])
        sheet.append([2, 1, "R2", "10K (5%)", "0402", "Resistor", "Chip"])
        path = tmp_path / "bom.xlsx"
        book.save(path)
        bom = read_bom(path)
        assert bom["C3"] == {"footprint": "0402", "value": "0.1uF", "voltage": "50V", "tolerance": "10%",
                             "description": "Ceramic"}
        assert bom["R2"]["value"] == "10K" and bom["R2"]["tolerance"] == "5%"


class TestEspressifBoards:
    async def test_org_search(self):
        result = await server.board_search(org="Espressif", limit=10)
        slugs = {b["slug"] for b in result["results"]}
        assert {DEVKIT_C, "espressif-esp32-s3-devkitm-1", "espressif-esp32-devkitc-v4"} <= slugs
        assert all(b["source_url"].startswith("https://documentation.espressif.com/") for b in result["results"])

    async def test_native_usb_port(self):
        focus = (await server.board_get(slug=DEVKIT_C, focus="J4"))["focus"]
        pins = {pin: {e["value"] for e in entries} for pin, entries in focus["pins"].items()}
        # Micro-USB D-/D+ to the module's GPIO19/20 through LESD5D5.0 ESD diodes
        assert {"LESD5D5.0CT1G", "ESP32-S3-WROOM-1"} <= pins["2"] and {"LESD5D5.0CT1G", "ESP32-S3-WROOM-1"} <= pins["3"]
        assert focus["pin_nets"]["2"] == "GPIO19" and focus["pin_nets"]["3"] == "GPIO20"

    async def test_module_reset_rc(self):
        focus = (await server.board_get(slug=DEVKIT_C, focus="ESP32-S3"))["focus"]
        assert focus["pin_nets"]["3"] == "CHIP_PU"
        assert {"10kohm", "1uF"} <= {e["value"] for e in focus["pins"]["3"]}

    async def test_not_fitted_parts_say_so(self):
        board = await server.board_get(slug=DEVKIT_C, include_bom=True)
        c14 = next(c for c in board["components"] if c["ref"] == "C14")
        assert c14["value"] == "100nF" and c14["description"].startswith("Not fitted")

    @pytest.mark.parametrize("slug, org, url", [
        ("rpi-cm4-io-board", "Raspberry Pi", "https://pip-assets.raspberrypi.com/"),
        ("seeed-xiao-esp32-s3-sense", "Seeed Studio", "https://files.seeedstudio.com/")])
    async def test_zip_boards_link_and_maker(self, slug, org, url):
        board = await server.board_get(slug=slug)
        assert board["org_display"] == org and board["source_url"].startswith(url)


class TestPinNets:
    async def test_named_pins_too(self):
        focus = (await server.board_get(slug="sparkfun-thing-plus-esp32-s3", focus="DT1042"))["focus"]
        assert focus["pin_nets"]["GND"] == "GND" and len(focus["pin_nets"]) == focus["pins_in_nets"] == 4


class TestEsp32Rule:
    def test_devkit_usb_and_reset(self):
        content = get_design_rules(topic="esp32")["content"]
        assert "one LESD5D5.0CT1G (LRC, 5 V, 15 pF) on each of VBUS, D- and D+" in content
        assert "espressif-esp32-s3-devkitc-1" in content and "esp32-c6-devkitc-1-schematics_v1.4.pdf" in content
        assert "Espressif's DevKits fit exactly 10 kohm + 1 uF on CHIP_PU" in content


class TestThinConsensus:
    """0.8.9: the DevKitM-1 made ESP32-S3-MINI-1 a two-board consensus, which replaced the 33-board
    ESP32 one a partial "ESP32" focus used (CI's board quality gate caught it)."""

    async def test_partial_focus_keeps_the_family_consensus(self):
        board = await server.board_get(slug="adafruit-esp32-s3-feather", focus="ESP32")
        assert board["focus"]["value"].startswith("ESP32-S3") and board["consensus"]["board_count"] >= 10

    async def test_exact_focus_keeps_its_own(self):
        board = await server.board_get(slug=DEVKIT_C, focus="ESP32-S3-WROOM-1")
        assert board["focus_match_type"] == "exact" and board["consensus"]["ic"] == "ESP32-S3-WROOM-1"
