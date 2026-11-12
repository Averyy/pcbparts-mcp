"""0.8.6: board_get focus on any part, ground and supply pins, and the USB-C CC rules (design-session
reports, 2026-11-03). Board checks run on the repo's board files."""

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.design_rules import get_design_rules

THING_PLUS = "sparkfun-thing-plus-esp32-s3"
QT_PY = "adafruit-qt-py-esp32-s3"


def _refs(entries):
    return {e["ref"] for e in entries}


class TestFocusOnAnyPart:
    async def test_connector_by_ref(self):
        board = await server.board_get(slug=THING_PLUS, focus="J1")
        focus = board["focus"]
        assert board["focus_match_type"] == "ref" and focus["value"] == "USB-C"
        cc = {pin: entries for pin, entries in focus["pins"].items() if pin.startswith("CC")}
        assert {pin: [(e["ref"], e["value"], e["role"]) for e in entries] for pin, entries in cc.items()} == {
            "CC1": [("R11", "5.1kohm", "pulldown")], "CC2": [("R10", "5.1kohm", "pulldown")]}
        assert {"U2", "U3"} <= _refs(focus["pins"]["D+@A6"])
        assert focus["power_pins"]["GND@GND"]["net"] == "GND" and focus["power_pins"]["GND@GND"]["part_count"] > 8
        assert "focus_error" not in board

    @pytest.mark.parametrize("focus", ["USB", "USB-C", "usb c", "Type-C"])
    async def test_connector_by_value_words(self, focus):
        board = await server.board_get(slug=QT_PY, focus=focus)
        assert board["focus"]["ref"] == "X6" and board["focus_match_type"] == "partial"
        assert _refs(board["focus"]["pins"]["CC1"]) == {"R6"}
        vbus = board["focus"]["power_pins"]["VBUS"]
        assert vbus["net"] == "VBUS" and "D1" in _refs(vbus["parts"])

    async def test_ic_gets_its_ground_pin_and_pin_count(self):
        board = await server.board_get(slug=THING_PLUS, focus="DT1042")
        focus = board["focus"]
        assert focus["ref"] == "U2" and focus["power_pins"]["GND"]["net"] == "GND"
        # SOT-23-6: I/O1 and I/O2 are in no net, so they're in neither list
        assert focus["pins_in_nets"] == 4
        assert not {"I/O1", "I/O2"} & (set(focus["pins"]) | set(focus["power_pins"]))
        assert all("ref" in e and "value" in e for entries in focus["pins"].values() for e in entries)

    async def test_no_match_lists_other_parts(self):
        board = await server.board_get(slug=THING_PLUS, focus="nonsense")
        assert board["focus_error"].startswith("No IC, part ref or part value 'nonsense'")
        assert {"ref": "J1", "value": "USB-C"} in board["available_refs"]
        assert all(not a["ref"].startswith(("R", "C", "L")) or a["ref"].startswith("CONN") for a in board["available_refs"])

    async def test_summary_pin_count(self):
        board = await server.board_get(slug=THING_PLUS)
        counts = {h["ref"]: h["pin_count"] for h in board["neighborhoods"]}
        assert counts["U2"] == 6  # the part's own pins since 0.8.11 (4 in nets: I/O1 and I/O2 are NC)


class TestUsbRules:
    def test_cc_tvs_rated_for_a_short_to_vbus(self):
        content = (get_design_rules(topic="usb"))["content"]
        assert "at least 22 V-tolerant" in content and "TPD2S300" in content  # wording from the 0.9.0 audit
        assert "Never put CC on a spare channel of the D+/D- ESD array" in content
        assert "VRWM <= 5V, breakdown 5-7V" not in content

    def test_cc_windows_labelled_with_thresholds(self):
        content = (get_design_rules(topic="usb"))["content"]
        assert "R2.4 Table 4-36" in content and "0.613-0.745 V" in content and "1.165-1.368 V" in content
        assert "0.20 V Ra/Rd threshold" not in content
        # 0.9.0: the table's Disconnect/Connect Threshold row is 2.043 V, not "below 0.276 V"
        assert "reads disconnect below 0.276" not in content

    def test_esd441_line(self):
        content = (get_design_rules(topic="esd"))["content"]
        # 0.9.0 audit: match the actual DC fault voltage rather than a blanket 22V
        assert "ESD341 (0.66pF) for 3.6V SBU" in content and "match the DC fault voltage" in content
