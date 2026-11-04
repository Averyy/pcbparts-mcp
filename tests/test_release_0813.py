"""0.8.13: eight guitar-pedal boards (GuitarML's two, six of torvalds/1590A) split from the two
multi-board rows that never parsed, and NC pins no longer include pins wired only to a part the
parser drops (a test point, a solder jumper, a pedal's wiring pad)."""

import sys
from pathlib import Path

import yaml

import pcbparts_mcp.server as server

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import parse_boards as pb  # noqa: E402
from parsers.kicad import extract_part_pins as kicad_part_pins  # noqa: E402

BOARDS = Path(__file__).parent.parent / "data" / "boards"

# U1 pin 1 reaches only TP1 (dropped as a test point); pin 2 is on a one-pad "unconnected-" net; the
# exposed pad 9 is split into two pieces on its own net, which still connects it to nothing else
_PCB = """(kicad_pcb (version 20240108)
  (footprint "Package:QFN" (property "Reference" "U1")
    (pad "1" smd rect (net 1 "Net-(TP1-Pad1)") (pinfunction "BOOT") (pintype "input"))
    (pad "2" smd rect (net 2 "unconnected-(U1-SPARE-Pad2)") (pinfunction "SPARE") (pintype "passive"))
    (pad "3" smd rect (net 3 "SDA") (pinfunction "SDA") (pintype "bidirectional"))
    (pad "9" smd rect (net 4 "unconnected-(U1-EP-Pad9)") (pinfunction "EP") (pintype "passive"))
    (pad "9" smd rect (net 4 "unconnected-(U1-EP-Pad9)") (pinfunction "EP") (pintype "passive"))
  )
  (footprint "TestPoint:TP" (property "Reference" "TP1")
    (pad "1" smd circle (net 1 "Net-(TP1-Pad1)") (pintype "passive"))
  )
  (footprint "Resistor_SMD:R_0402" (property "Reference" "R1")
    (pad "1" smd rect (net 3 "SDA") (pintype "passive"))
    (pad "2" smd rect (net 5 "VCC") (pintype "passive"))
  )
)
"""


class TestWiredToDroppedParts:
    def test_kicad(self, tmp_path):
        pcb = tmp_path / "board.kicad_pcb"
        pcb.write_text(_PCB, encoding="utf-8")
        pins, wired = kicad_part_pins(pcb, {"U1", "R1"})
        assert wired["U1"] == {"BOOT", "SDA"}
        comps = [pb.Component(ref="U1", value="x", footprint="")]
        nets = [pb.Net(name="SDA", pins=["R1.1", "U1.SDA"])]
        pb.assign_pin_info("test", comps, nets, pins, wired)
        # BOOT goes to a test point: connected, though no net in the board data shows it
        # The split pad is "EP@9", as nets label a name two pads share
        assert comps[0].nc_pins == {"SPARE": "2", "EP@9": "9"} and comps[0].pin_count == 4


class TestAssignEdgeCases:
    """From a review of the pin code (Dobby, 2026-11-04)."""

    def test_connected_pins_get_the_net_pin_fixes(self):
        # MAX31865's library misspells one ground pin ANGD@1; a fix renames it AGND@1 in the nets
        comps = [pb.Component(ref="U1", value="MAX31865", footprint="")]
        pb.assign_pin_info("adafruit-max31865-rtd", comps, [], {"U1": {"ANGD@1": "16", "NC": "17"}},
                           {"U1": {"ANGD@1"}})
        assert comps[0].nc_pins == {"NC": "17"}

    def test_pad_fallback_with_a_pin_on_two_pads(self):
        comps = [pb.Component(ref="U1", value="x", footprint="")]
        nets = [pb.Net(name="VCC", pins=["U1.1", "U1.2", "C1.1"])]
        pb.assign_pin_info("test", comps, nets, {"U1": {"VCC": "1 2", "NC": "3"}})
        assert comps[0].pin_count == 3 and comps[0].nc_pins == {"NC": "3"}


class TestMergeRewritesOlderFields:
    def test_block_and_wrapped_nc_pins(self, tmp_path, monkeypatch):
        repo = tmp_path / "cache" / "org--repo"
        repo.mkdir(parents=True)
        (repo / "board.kicad_sch").write_text("", encoding="utf-8")
        (repo / "board.kicad_pcb").write_text(_PCB, encoding="utf-8")
        out = tmp_path / "boards"
        out.mkdir()
        (out / "test.yaml").write_text(
            'name: Test\nslug: test\nsource: org/repo\nformat: kicad8\ndescription: "quoted, kept as is"\n'
            "components:\n- ref: R1\n  value: 10kohm\n  footprint: '0402'\n  nc_pins:\n    '2': '2'\n"
            "- ref: U1\n  value: X\n  footprint: QFN\n  pin_count: 4\n  nc_pins: {BOOT: '1',\n\n    SPARE: '2',\n"
            "    EP: '9'}\nnets:\n- name: SDA\n  pins: [R1.1, U1.SDA]\n", encoding="utf-8")
        monkeypatch.setattr(pb, "OUTPUT_DIR", out)
        monkeypatch.setattr(pb, "CACHE_DIR", tmp_path / "cache")
        info = {"format": "kicad8", "schematic_path": "board.kicad_sch", "repo": "org/repo"}
        assert pb.merge_pin_info("test", info) == (2, [])
        text = (out / "test.yaml").read_text(encoding="utf-8")
        assert 'description: "quoted, kept as is"' in text and "  nc_pins: {SPARE: '2', EP@9: '9'}" in text
        data = yaml.safe_load(text)
        # R1's pad 2 is alone on VCC: its block-style entry comes back on one line
        assert [c.get("nc_pins") for c in data["components"]] == [{"2": "2"}, {"SPARE": "2", "EP@9": "9"}]
        assert "  nc_pins: {'2': '2'}" in text and "    '2': '2'" not in text and "    EP: '9'}" not in text
        # Run again: nothing changes
        pb.merge_pin_info("test", info)
        assert (out / "test.yaml").read_text(encoding="utf-8") == text


class TestPedalBoards:
    SLUGS = ["guitarml-classic-boost", "guitarml-ts-rat-combo", "1590a-boost-effect", "1590a-buffered-base",
             "1590a-compressor-effect", "1590a-daisy-seed-base", "1590a-fuzz-effect", "1590a-octaver-effect"]

    def test_boards(self):
        for slug in self.SLUGS:
            board = yaml.safe_load((BOARDS / f"{slug}.yaml").read_text(encoding="utf-8"))
            assert "audio" in board["tags"] and board["key_ics"] and board["nets"], slug
            assert not [c for c in board["components"] if c["ref"].startswith("Box")], slug
        # The unfinished STM32 board (its codec's I2S pins wired to nothing) and the two old rows are out
        md = (BOARDS / "BOARDS.md").read_text(encoding="utf-8")
        assert "1590A STM32 Effect" not in md and "Guitar Pedal Collection" not in md
        assert not (BOARDS / "1590a-stm32-effect.yaml").exists()

    def test_wiring_pads_are_not_nc(self):
        board = yaml.safe_load((BOARDS / "guitarml-classic-boost.yaml").read_text(encoding="utf-8"))
        assert not [c for c in board["components"] if c.get("nc_pins")]

    async def test_search_and_focus(self):
        found = await server.board_search(query="guitar pedal", limit=20)
        slugs = {b["slug"] for b in found["results"]}
        assert {"guitarml-ts-rat-combo", "1590a-fuzz-effect"} <= slugs
        focus = (await server.board_get(slug="guitarml-ts-rat-combo", focus="LM301"))["focus"]
        assert focus["nc_pins"] == {"COMP": "5"} and focus["pin_count"] == 8

    def test_no_power_supply_tag_on_a_guitar_boost(self):
        for slug in ("guitarml-classic-boost", "1590a-boost-effect"):
            board = yaml.safe_load((BOARDS / f"{slug}.yaml").read_text(encoding="utf-8"))
            assert board["tags"] == ["audio"], slug


class TestExistingBoards:
    def test_pins_to_solder_jumpers_are_connected(self):
        board = yaml.safe_load((BOARDS / "absmach-s0.yaml").read_text(encoding="utf-8"))
        parts = {c["ref"]: c for c in board["components"]}
        assert "USB_BOOT" not in parts["U2"]["nc_pins"] and parts["U4"]["nc_pins"] == {"OE": "10"}
