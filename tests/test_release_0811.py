"""0.8.11: board_get focus names a part's unconnected pins (nc_pins) and gives its own pin count
(design-session report, 2026-11-03: the DT1042-04's spare channels looked the same as pins the
extraction dropped). Pin lists come from each board's footprints (KiCad, PADS) or symbols (Eagle)."""

import sys
from pathlib import Path

import pytest
import yaml

import pcbparts_mcp.server as server

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import parse_boards as pb  # noqa: E402
from parsers.eagle import extract_part_pins as eagle_part_pins  # noqa: E402
from parsers.kicad import _extract_nets, _parse_sexpr, extract_part_pins as kicad_part_pins  # noqa: E402
from parsers.pads import extract_part_pins as pads_part_pins  # noqa: E402

BOARDS = Path(__file__).parent.parent / "data" / "boards"

# KiCad 6+: pads from symbol pins carry a pintype; an unconnected pin gets a one-pin "unconnected-" net
_KICAD_PCB = """(kicad_pcb (version 20221018)
  (footprint "Package_TO_SOT_SMD:SOT-23-6"
    (property "Reference" "U2")
    (pad "1" smd rect (net 3 "unconnected-(U2-I{slash}O1-Pad1)") (pinfunction "I/O1") (pintype "passive"))
    (pad "2" smd rect (net 2 "GND") (pinfunction "GND") (pintype "power_in"))
    (pad "3" smd rect (pinfunction "I/O2") (pintype "passive"))
    (pad "4" smd rect (net 4 "D+") (pinfunction "I/O3") (pintype "passive"))
    (pad "5" smd rect (net 1 "VCC") (pinfunction "VCC") (pintype "power_in"))
    (pad "6" smd rect (net 2 "GND") (pinfunction "GND") (pintype "power_in"))
    (pad "MP" smd rect)
    (pad "" np_thru_hole circle)
  )
  (footprint "Resistor_SMD:R_0402"
    (property "Reference" "R1")
    (pad "1" smd rect (net 1 "VCC") (pintype "passive"))
    (pad "2" smd rect (net 2 "GND") (pintype "passive"))
  )
  (footprint "Connector:USB"
    (property "Reference" "J1")
    (pad "1" smd rect (net 4 "D+") (pintype "passive"))
  )
)
"""

# Eagle: a supply pin (direction pwr) joins the net of its name without a wire
_EAGLE_SCH = """<?xml version="1.0" encoding="utf-8"?>
<eagle><drawing><schematic>
<libraries><library name="lib">
<symbols><symbol name="LDO">
  <pin name="IN" direction="pwr"/><pin name="OUT" direction="sup"/><pin name="EN" direction="in"/>
  <pin name="GND" direction="pwr"/><pin name="BP"/>
</symbol></symbols>
<devicesets><deviceset name="LDO"><gates><gate name="G$1" symbol="LDO"/></gates>
<devices><device name="" package="SOT23-5"><connects>
  <connect gate="G$1" pin="IN" pad="1"/><connect gate="G$1" pin="GND" pad="2 6"/>
  <connect gate="G$1" pin="EN" pad="3"/><connect gate="G$1" pin="BP" pad="4"/><connect gate="G$1" pin="OUT" pad="5"/>
</connects></device></devices></deviceset></devicesets>
</library></libraries>
<parts><part name="U2" library="lib" deviceset="LDO" device="" value="LDO"/></parts>
<sheets><sheet><nets>
  <net name="VOUT"><segment><pinref part="U2" gate="G$1" pin="OUT"/><pinref part="C1" gate="G$1" pin="1"/></segment></net>
  <net name="VIN"><segment><pinref part="U2" gate="G$1" pin="IN"/><pinref part="C2" gate="G$1" pin="1"/></segment></net>
</nets></sheet></sheets>
</schematic></drawing></eagle>
"""

# PADS: a decal's terminals with their pad stacks (stack 0 is the default; 4 and 5 have no copper)
_PADS_ASC = """!PADS-POWERPCB-V2005.2-BASIC-250L! DESIGN DATABASE ASCII FILE 1.
*PCB*        GENERAL PARAMETERS OF THE PCB DESIGN
*PARTDECAL*  ITEMS
USB_3P           M 0 0 0 5 3 0 0
T0 0 0 0 1
T100 0 100 0 2
T200 0 200 0 3
T300 0 300 0 6-1
T400 0 400 0 10
PAD 0 3
-2 900000 RF  0.000 2025000 0   0   0
-1 0   R
0  0   R
PAD 4 3
-2 0   R   0
-1 0   R
0  0   R
PAD 5 3
-2 0   R   900000
-1 0   R
0  0   R
*PARTTYPE*   ITEMS
USB_3P USB_3P UND  0   0   0     0 Y
*PART*       ITEMS
J1              USB_3P 1500000 3000000 90.000 G N 0 -1 0 -1 2
*ROUTE*
*SIGNAL* VBUS 0 -2
J1.1                            C1.1
*SIGNAL* GND 0 -2
J1.3                            C1.2
*POUR*       POUR ITEMS
"""


class TestKicadPins:
    def test_every_pin_labelled_as_nets_label_them(self, tmp_path):
        pcb = tmp_path / "board.kicad_pcb"
        pcb.write_text(_KICAD_PCB, encoding="utf-8")
        pins, _ = kicad_part_pins(pcb, {"U2", "R1", "J1"})
        # GND twice: GND@2 and GND@6, as nets name them; MP (no pintype) and the unplated hole aren't pins
        assert pins["U2"] == {"I/O1": "1", "GND@2": "2", "I/O2": "3", "I/O3": "4", "VCC": "5", "GND@6": "6"}
        nets = _extract_nets(_parse_sexpr(_KICAD_PCB)[0], {"U2", "R1", "J1"})
        labels = {p.partition(".")[2] for n in nets for p in n.pins if p.startswith("U2.")}
        assert labels <= pins["U2"].keys()

    def test_nc_pins(self, tmp_path):
        pcb = tmp_path / "board.kicad_pcb"
        pcb.write_text(_KICAD_PCB, encoding="utf-8")
        refs = {"U2", "R1", "J1"}
        nets = _extract_nets(_parse_sexpr(_KICAD_PCB)[0], refs)
        comps = [pb.Component(ref=r, value="x", footprint="") for r in sorted(refs)]
        count, mismatched = pb.assign_pin_info("test", comps, nets, *kicad_part_pins(pcb, refs))
        u2 = next(c for c in comps if c.ref == "U2")
        assert (count, mismatched) == (3, [])
        assert u2.pin_count == 6 and u2.nc_pins == {"I/O1": "1", "I/O2": "3"}
        assert pb.pin_info_fields(u2.pin_count, u2.nc_pins) == {"pin_count": 6, "nc_pins": {"I/O1": "1", "I/O2": "3"}}
        # A two-pin part with both pins connected needs neither field
        r1 = next(c for c in comps if c.ref == "R1")
        assert (r1.pin_count, r1.nc_pins, pb.pin_info_fields(r1.pin_count, r1.nc_pins)) == (2, {}, {})


class TestAssignPinInfo:
    def test_disagreeing_lists_are_left_out(self):
        comps = [pb.Component(ref="U1", value="x", footprint="")]
        nets = [pb.Net(name="A", pins=["U1.SDA", "R1.1"])]
        assert pb.assign_pin_info("test", comps, nets, {"U1": {"SCL": "1", "VDD": "2"}}) == (0, ["U1"])
        assert comps[0].pin_count == 0 and comps[0].nc_pins == {}

    def test_nets_naming_pins_by_pad(self):
        # Older files gave the nets pad numbers ("U1.1"); the pin list now has names
        comps = [pb.Component(ref="U1", value="x", footprint="")]
        nets = [pb.Net(name="A", pins=["U1.1", "R1.1"]), pb.Net(name="B", pins=["U1.3", "R1.2"])]
        pb.assign_pin_info("test", comps, nets, {"U1": {"SDA": "1", "NC": "2", "SCL": "3"}})
        assert comps[0].pin_count == 3 and comps[0].nc_pins == {"NC": "2"}

    def test_pad_order(self):
        fields = pb.pin_info_fields(40, {"B": "10", "A": "2", "C": "A10", "D": "A2"})
        assert list(fields["nc_pins"].values()) == ["2", "10", "A2", "A10"]


class TestEaglePins:
    def test_supply_pins_are_never_nc(self, tmp_path):
        sch = tmp_path / "board.sch"
        sch.write_text(_EAGLE_SCH, encoding="utf-8")
        pins, supply = eagle_part_pins(sch, {"U2"})
        assert pins["U2"] == {"IN": "1", "GND": "2 6", "EN": "3", "BP": "4", "OUT": "5"}
        assert supply == {"U2": {"IN", "GND", "OUT"}}  # OUT and IN also reach C1/C2 (0.8.13)
        comps = [pb.Component(ref="U2", value="LDO", footprint="")]
        nets = [pb.Net(name="VOUT", pins=["U2.OUT", "C1.1"]), pb.Net(name="VIN", pins=["U2.IN", "C2.1"])]
        pb.assign_pin_info("test", comps, nets, pins, supply)
        # GND joins net GND by name; EN and BP are wired to nothing. GND's two pads both count
        assert comps[0].pin_count == 6 and comps[0].nc_pins == {"EN": "3", "BP": "4"}


class TestPadsPins:
    def test_copperless_terminals_are_not_pins(self, tmp_path):
        asc = tmp_path / "board.asc"
        asc.write_text(_PADS_ASC, encoding="latin-1")
        pins, tied = pads_part_pins(asc, {"J1"})
        assert pins == {"J1": {"1": "1", "2": "2", "3": "3"}} and tied == {}


@pytest.fixture(scope="class")
def boards():
    return [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(BOARDS.glob("*.yaml"))]


class TestBoardYamls:

    def test_nc_pins_are_on_no_net(self, boards):
        checked = 0
        for board in boards:
            on_net = {}
            for net in board.get("nets") or []:
                for pin in net["pins"]:
                    ref, _, label = pin.partition(".")
                    on_net.setdefault(ref, set()).add(label)
            for comp in board.get("components") or []:
                nc = comp.get("nc_pins") or {}
                if nc:
                    checked += 1
                    assert not nc.keys() & on_net.get(comp["ref"], set()), (board["slug"], comp["ref"])
                    assert not set(nc.values()) & on_net.get(comp["ref"], set()), (board["slug"], comp["ref"])
                    assert comp["pin_count"] >= len(nc) and "~" not in nc.values()
        assert checked > 1000

    def test_most_ics_have_a_pin_count(self, boards):
        ics = [c for b in boards if b.get("nets") for c in b.get("components") or [] if c["ref"].startswith("U")]
        assert sum("pin_count" in c for c in ics) / len(ics) > 0.9


class TestFocus:
    async def test_reported_case(self):
        board = await server.board_get(slug="sparkfun-thing-plus-esp32-s3", focus="DT1042")
        focus = board["focus"]
        assert (focus["pin_count"], focus["pins_in_nets"]) == (6, 4)
        assert focus["nc_pins"] == {"I/O1": "1", "I/O2": "3"}

    async def test_every_pin_connected(self):
        focus = (await server.board_get(slug="sparkfun-thing-plus-esp32-s3", focus="MCP73831"))["focus"]
        assert focus["pin_count"] == 5 and focus["nc_pins"] == {}

    async def test_summary_pin_count_is_the_parts(self):
        board = await server.board_get(slug="sparkfun-thing-plus-esp32-s3")
        counts = {h["ref"]: h["pin_count"] for h in board["neighborhoods"]}
        assert counts["U2"] == 6

    async def test_eagle(self):
        focus = (await server.board_get(slug="blueesc", focus="U2"))["focus"]
        assert focus["nc_pins"] == {"EN": "3", "BP": "4"}

    async def test_pads(self):
        focus = (await server.board_get(slug="espressif-esp32-devkitc-v4", focus="J1"))["focus"]
        assert focus["value"] == "Micro USB" and focus["pin_count"] == 9 and focus["nc_pins"] == {"4": "4"}
