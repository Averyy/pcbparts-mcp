"""Unit tests for scripts/parse_boards.py — normalization, slugify, BOARDS.md parser."""

import textwrap
from pathlib import Path

import pytest

# Import from scripts
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from parse_boards import (
    slugify,
    normalize_value,
    normalize_footprint,
    normalize_connector_value,
    extract_inline_specs,
    parse_boards_md,
    _clean_pin_name,
)


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_simple(self):
        assert slugify("SparkFun BME280") == "sparkfun-bme280"

    def test_hyphens_preserved(self):
        assert slugify("Bus Pirate 5 REV10A") == "bus-pirate-5-rev10a"

    def test_special_chars(self):
        assert slugify("Adafruit 2.4\" TFT FeatherWing V2") == "adafruit-2-4-tft-featherwing-v2"

    def test_multiple_spaces(self):
        assert slugify("  some   board  ") == "some-board"

    def test_already_slug(self):
        assert slugify("my-board") == "my-board"

    def test_underscores(self):
        assert slugify("Adafruit_SCD-41") == "adafruit-scd-41"


# ---------------------------------------------------------------------------
# parse_boards_md
# ---------------------------------------------------------------------------

class TestParseBoardsMd:
    SAMPLE_MD = textwrap.dedent("""\
        # Reference Boards Registry

        ## All Parseable Boards (3 boards)

        | Board | Org | Repo | Format | Schematic Path | Key Coverage |
        |-------|-----|------|--------|---------------|-------------|
        | SparkFun BME280 | SparkFun | `sparkfun/SparkFun_BME280_Breakout_Board` | eagle | `Hardware/SparkFun_BME280_Breakout.sch` | BME280 I2C/SPI |
        | iCEBreaker | 1BitSquared | `icebreaker-fpga/icebreaker` | kicad7 | `hardware/v1.1a/icebreaker.kicad_sch` | iCE40UP5K FPGA |
        | Adafruit SCD-41 CO2 Sensor | Adafruit | `adafruit/Adafruit-SCD-4x-PCB` | eagle | `Adafruit SCD-41.sch` (407 KB) | NDIR CO2 sensor |
    """)

    def test_parse_count(self, tmp_path):
        md_file = tmp_path / "BOARDS.md"
        md_file.write_text(self.SAMPLE_MD)
        boards = parse_boards_md(md_file)
        assert len(boards) == 3

    def test_parse_eagle_board(self, tmp_path):
        md_file = tmp_path / "BOARDS.md"
        md_file.write_text(self.SAMPLE_MD)
        boards = parse_boards_md(md_file)
        bme = boards["sparkfun-bme280"]
        assert bme["name"] == "SparkFun BME280"
        assert bme["org"] == "SparkFun"
        assert bme["repo"] == "sparkfun/SparkFun_BME280_Breakout_Board"
        assert bme["format"] == "eagle"
        assert bme["schematic_path"] == "Hardware/SparkFun_BME280_Breakout.sch"

    def test_strips_size_annotations(self, tmp_path):
        md_file = tmp_path / "BOARDS.md"
        md_file.write_text(self.SAMPLE_MD)
        boards = parse_boards_md(md_file)
        scd = boards["adafruit-scd-41-co2-sensor"]
        assert scd["schematic_path"] == "Adafruit SCD-41.sch"
        assert "(407 KB)" not in scd["schematic_path"]

    def test_kicad_format(self, tmp_path):
        md_file = tmp_path / "BOARDS.md"
        md_file.write_text(self.SAMPLE_MD)
        boards = parse_boards_md(md_file)
        assert boards["icebreaker"]["format"] == "kicad7"


# ---------------------------------------------------------------------------
# normalize_value — resistors
# ---------------------------------------------------------------------------

class TestNormalizeValueResistors:
    def test_plain_number(self):
        assert normalize_value("100", "R1") == "100ohm"

    def test_k_suffix(self):
        assert normalize_value("4.7K", "R3") == "4.7kohm"

    def test_k_lowercase(self):
        assert normalize_value("10k", "R5") == "10kohm"

    def test_mega(self):
        assert normalize_value("1M", "R2") == "1Mohm"

    def test_embedded_r(self):
        assert normalize_value("4R7", "R1") == "4.7ohm"

    def test_embedded_k(self):
        assert normalize_value("4k7", "R1") == "4.7kohm"

    def test_milliohm(self):
        assert normalize_value("100m", "R1") == "100mohm"

    def test_with_unit_suffix(self):
        assert normalize_value("100ohm", "R1") == "100ohm"

    def test_ferrite_bead(self):
        assert normalize_value("600", "FB1") == "600ohm"


# ---------------------------------------------------------------------------
# normalize_value — capacitors
# ---------------------------------------------------------------------------

class TestNormalizeValueCapacitors:
    def test_100n(self):
        assert normalize_value("100n", "C1") == "100nF"

    def test_0_1u(self):
        assert normalize_value("0.1u", "C2") == "100nF"

    def test_10u(self):
        assert normalize_value("10u", "C3") == "10uF"

    def test_22p(self):
        assert normalize_value("22p", "C4") == "22pF"

    def test_1u(self):
        assert normalize_value("1u", "C5") == "1uF"

    def test_2u2(self):
        assert normalize_value("2u2", "C1") == "2.2uF"


# ---------------------------------------------------------------------------
# normalize_value — inductors
# ---------------------------------------------------------------------------

class TestNormalizeValueInductors:
    def test_10u(self):
        assert normalize_value("10u", "L1") == "10uH"

    def test_2u2(self):
        assert normalize_value("2u2", "L1") == "2.2uH"

    def test_100n(self):
        assert normalize_value("100n", "L1") == "100nH"


# ---------------------------------------------------------------------------
# normalize_value — passthrough
# ---------------------------------------------------------------------------

class TestNormalizeValuePassthrough:
    def test_ic_value(self):
        assert normalize_value("BME280", "U1") == "BME280"

    def test_led(self):
        assert normalize_value("RED", "D1") == "red LED"

    def test_connector(self):
        assert normalize_value("CONN_01X04", "J1") == "CONN_01X04"

    def test_empty_passive_is_dnp(self):
        assert normalize_value("", "R1") == "DNP"

    def test_empty_cap_is_dnp(self):
        assert normalize_value("", "C5") == "DNP"

    def test_empty_ic_stays_empty(self):
        assert normalize_value("", "U1") == ""

    def test_empty_jumper_is_solder_jumper(self):
        assert normalize_value("", "JP3") == "solder jumper"

    def test_unparseable_passive(self):
        assert normalize_value("DNP", "R1") == "DNP"


# ---------------------------------------------------------------------------
# normalize_footprint — KiCad style
# ---------------------------------------------------------------------------

class TestNormalizeFootprintKicad:
    def test_resistor_0402(self):
        assert normalize_footprint("R_0402_1005Metric", "R1") == "0402"

    def test_capacitor_0805(self):
        assert normalize_footprint("C_0805_2012Metric", "C1") == "0805"

    def test_inductor_1206(self):
        assert normalize_footprint("L_1206_3216Metric", "L1") == "1206"

    def test_soic8(self):
        assert normalize_footprint("SOIC-8_3.9x4.9mm_P1.27mm", "U1") == "SOIC-8"

    def test_qfn48(self):
        assert normalize_footprint("QFN-48_7x7mm_P0.5mm", "U1") == "QFN-48"

    def test_sot23(self):
        assert normalize_footprint("SOT-23", "Q1") == "SOT-23"


# ---------------------------------------------------------------------------
# normalize_footprint — Eagle style
# ---------------------------------------------------------------------------

class TestNormalizeFootprintEagle:
    def test_0603_cap(self):
        assert normalize_footprint("0603-CAP", "C1") == "0603"

    def test_0603_res(self):
        assert normalize_footprint("0603-RES", "R1") == "0603"

    def test_0402_cap(self):
        assert normalize_footprint("0402-CAP", "C1") == "0402"

    def test_1206_res(self):
        assert normalize_footprint("1206-RES", "R1") == "1206"

    def test_jumper_pad_3(self):
        assert normalize_footprint("PAD-JUMPER-3-3OF3_NC_BY_TRACE_YES_SILK_FULL_BOX") == "SJ-3"

    def test_jumper_pad_2(self):
        assert normalize_footprint("PAD-JUMPER-2-NC_BY_TRACE_YES_SILK") == "SJ-2"


# ---------------------------------------------------------------------------
# normalize_footprint — edge cases
# ---------------------------------------------------------------------------

class TestNormalizeFootprintEdgeCases:
    def test_empty(self):
        assert normalize_footprint("", "R1") == ""

    def test_already_short(self):
        assert normalize_footprint("BME280", "U1") == "BME280"

    def test_ic_package_no_dimensions(self):
        assert normalize_footprint("BME280_LGA") == "BME280_LGA"


# ---------------------------------------------------------------------------
# Junk part filtering
# ---------------------------------------------------------------------------

class TestJunkFiltering:
    """Test _is_junk_part via import from eagle parser."""

    @pytest.fixture(autouse=True)
    def setup(self):

        from parsers.eagle import _is_junk_part
        self._is_junk = _is_junk_part

    def test_sparkfun_aesthetics_is_junk(self):
        assert self._is_junk("LOGO1", "SparkFun-Aesthetics")

    def test_frame_ref_is_junk(self):
        assert self._is_junk("FRAME1", "some-library")

    def test_fiducial_ref_is_junk(self):
        assert self._is_junk("FID2", "some-library")

    def test_standoff_ref_is_junk(self):
        assert self._is_junk("STANDOFF4", "some-library")

    def test_logo_ref_is_junk(self):
        assert self._is_junk("LOGO3", "some-library")

    def test_bom_exclude_is_junk(self):
        assert self._is_junk("MH1", "microbuilder", bom_attr="EXCLUDE")

    def test_real_part_not_junk(self):
        assert not self._is_junk("U1", "SparkFun-ICs")

    def test_resistor_not_junk(self):
        assert not self._is_junk("R1", "SparkFun-Resistors")

    def test_connector_not_junk(self):
        assert not self._is_junk("JP1", "SparkFun-Connectors")

    def test_logo_deviceset_is_junk(self):
        assert self._is_junk("U$2", "some-library", "LOGO-SFE")

    def test_passer_deviceset_is_junk(self):
        assert self._is_junk("X1", "some-library", "PASSER-04")

    def test_pad_deviceset_is_junk(self):
        assert self._is_junk("U$3", "some-library", "PAD")

    def test_pad_with_size_is_junk(self):
        assert self._is_junk("REF1", "some-library", "PAD-0.6-1.1")

    def test_pad_jumper_not_junk(self):
        assert not self._is_junk("SJ1", "some-library", "PAD-JUMPER-3-3OF3")

    def test_dollar_ref_prefix(self):
        """U$2 style refs should strip $ properly."""
        assert self._is_junk("LOGO$1", "some-library")


# ---------------------------------------------------------------------------
# normalize_value — leading dot
# ---------------------------------------------------------------------------

class TestNormalizeValueLeadingDot:
    def test_dot_1u_cap(self):
        assert normalize_value(".1u", "C1") == "100nF"

    def test_dot_22u_cap(self):
        assert normalize_value(".22u", "C1") == "220nF"

    def test_dot_11_resistor(self):
        assert normalize_value(".11", "R1") == "110mohm"

    def test_dot_01u_cap(self):
        assert normalize_value(".01u", "C1") == "10nF"


# ---------------------------------------------------------------------------
# extract_inline_specs
# ---------------------------------------------------------------------------

class TestExtractInlineSpecs:
    def test_voltage_space(self):
        val, specs = extract_inline_specs("1uF 60V")
        assert val == "1uF"
        assert specs == {"voltage": "60V"}

    def test_voltage_slash(self):
        val, specs = extract_inline_specs("100n/50V")
        assert val == "100n"
        assert specs == {"voltage": "50V"}

    def test_tolerance(self):
        val, specs = extract_inline_specs("75K 1%")
        assert val == "75K"
        assert specs == {"tolerance": "1%"}

    def test_european_voltage(self):
        val, specs = extract_inline_specs("100n/6V3")
        assert val == "100n"
        assert specs == {"voltage": "6.3V"}

    def test_no_specs(self):
        val, specs = extract_inline_specs("100n")
        assert val == "100n"
        assert specs == {}

    def test_voltage_and_tolerance(self):
        val, specs = extract_inline_specs("100n 25V 5%")
        assert val == "100n"
        assert specs == {"voltage": "25V", "tolerance": "5%"}

    def test_empty(self):
        val, specs = extract_inline_specs("")
        assert val == ""
        assert specs == {}


# ---------------------------------------------------------------------------
# normalize_connector_value
# ---------------------------------------------------------------------------

class TestNormalizeConnectorValue:
    def test_m06(self):
        assert normalize_connector_value("M06", "1X06", "JP1") == "1x6 header"

    def test_m04(self):
        assert normalize_connector_value("M04", "1X04", "JP2") == "1x4 header"

    def test_ma08(self):
        assert normalize_connector_value("MA08-1", "MA08-1", "JP1") == "1x8 header"

    def test_from_footprint(self):
        """I2C_STANDARD gets pin count from footprint."""
        assert normalize_connector_value("I2C_STANDARD", "1X04_NO_SILK", "JP1") == "1x4 header"

    def test_conn_pattern(self):
        assert normalize_connector_value("CONN_01X04", "CONN_01X04", "J1") == "1x4 header"

    def test_2x_header(self):
        assert normalize_connector_value("PINHD-2X3", "2X03", "JP1") == "2x3 header"

    def test_usb_preserved(self):
        assert normalize_connector_value("USB-MICRO-B", "USB-MICRO-B", "J1") == "USB-MICRO-B"

    def test_barrel_jack_preserved(self):
        assert normalize_connector_value("BARREL_JACK", "BARREL_JACK", "J1") == "BARREL_JACK"

    def test_non_connector_ref(self):
        """Non-connector refs should pass through."""
        assert normalize_connector_value("BME280", "BME280_LGA", "U1") == "BME280"

    def test_solder_jumper_not_connector(self):
        assert normalize_connector_value("EN I2C PULL", "SJ-3", "SJ1") == "EN I2C PULL"


# ---------------------------------------------------------------------------
# normalize_footprint — Adafruit/Electrolama/Watterott patterns
# ---------------------------------------------------------------------------

class TestNormalizeFootprintNewPatterns:
    def test_adafruit_no_suffix(self):
        assert normalize_footprint("0603-NO", "C1") == "0603"

    def test_adafruit_no_suffix_0805(self):
        assert normalize_footprint("0805-NO", "R1") == "0805"

    def test_adafruit_underscore_prefix(self):
        assert normalize_footprint("_0805MP", "C1") == "0805"

    def test_electrolama_pkg(self):
        assert normalize_footprint("_PKG_C_0402", "C1") == "0402"

    def test_electrolama_pkg_no_underscore(self):
        assert normalize_footprint("PKG_R_0603", "R1") == "0603"

    def test_watterott_c_prefix(self):
        assert normalize_footprint("C0402", "C1") == "0402"

    def test_watterott_r_prefix(self):
        assert normalize_footprint("R0603", "R1") == "0603"

    def test_watterott_m_prefix(self):
        assert normalize_footprint("M0805", "R1") == "0805"

    def test_generalized_suffix(self):
        """0402-ARD and similar suffixed patterns."""
        assert normalize_footprint("0402-ARD", "C1") == "0402"


# ---------------------------------------------------------------------------
# KiCad Pin Names (P1)
# ---------------------------------------------------------------------------

class TestKicadPinNames:
    """Test pinfunction-based net pin naming in KiCad parser."""

    @pytest.fixture(autouse=True)
    def setup(self):

        from parsers.kicad import _parse_sexpr, _extract_nets, _find_all
        self._parse_sexpr = _parse_sexpr
        self._extract_nets = _extract_nets

    def _make_pcb(self, footprint_bodies: str) -> list:
        text = f'(kicad_pcb (net 1 "VCC") (net 2 "GND") {footprint_bodies})'
        tree = self._parse_sexpr(text)
        return tree[0]

    def test_pinfunction_used(self):
        """Pads with pinfunction should use it instead of pad number."""
        pcb = self._make_pcb('''
            (footprint "Package_SO:SOIC-8"
                (property "Reference" "U1")
                (pad "1" smd rect (net 1 "VCC") (pinfunction "VCC"))
                (pad "4" smd rect (net 2 "GND") (pinfunction "GND"))
            )
            (footprint "Resistor_SMD:R_0402"
                (property "Reference" "R1")
                (pad "1" smd rect (net 1 "VCC"))
                (pad "2" smd rect (net 2 "GND"))
            )
        ''')
        nets = self._extract_nets(pcb, {"U1", "R1"})
        all_pins = {pin for n in nets for pin in n.pins}
        assert "U1.VCC" in all_pins
        assert "U1.GND" in all_pins
        assert "U1.1" not in all_pins

    def test_fallback_to_pad_number(self):
        """Pads without pinfunction should use pad number."""
        pcb = self._make_pcb('''
            (footprint "Resistor_SMD:R_0402"
                (property "Reference" "R1")
                (pad "1" smd rect (net 1 "VCC"))
                (pad "2" smd rect (net 2 "GND"))
            )
            (footprint "Resistor_SMD:R_0402"
                (property "Reference" "R2")
                (pad "1" smd rect (net 1 "VCC"))
                (pad "2" smd rect (net 2 "GND"))
            )
        ''')
        nets = self._extract_nets(pcb, {"R1", "R2"})
        all_pins = {pin for n in nets for pin in n.pins}
        assert "R1.1" in all_pins
        assert "R1.2" in all_pins

    def test_duplicate_pinfunction_disambiguated(self):
        """Duplicate pinfunction labels get @pad_num suffix."""
        pcb = self._make_pcb('''
            (footprint "Package_SO:SOIC-8"
                (property "Reference" "U1")
                (pad "1" smd rect (net 1 "VCC") (pinfunction "VCC"))
                (pad "8" smd rect (net 1 "VCC") (pinfunction "VCC"))
                (pad "4" smd rect (net 2 "GND") (pinfunction "GND"))
            )
            (footprint "Resistor_SMD:R_0402"
                (property "Reference" "R1")
                (pad "1" smd rect (net 1 "VCC"))
                (pad "2" smd rect (net 2 "GND"))
            )
        ''')
        nets = self._extract_nets(pcb, {"U1", "R1"})
        all_pins = {pin for n in nets for pin in n.pins}
        assert "U1.VCC@1" in all_pins
        assert "U1.VCC@8" in all_pins
        assert "U1.GND" in all_pins


# ---------------------------------------------------------------------------
# Eagle Multi-Gate (P2/P3)
# ---------------------------------------------------------------------------

class TestEagleMultiGate:
    """Test gate-qualified pin names for multi-gate Eagle parts."""

    def _make_nets_xml(self, pinrefs: list[tuple[str, str, str, str]]) -> str:
        """Build minimal Eagle XML with nets containing pinrefs.

        pinrefs: list of (net_name, part, gate, pin) tuples.
        """
        import xml.etree.ElementTree as ET
        root = ET.Element("eagle")
        drawing = ET.SubElement(root, "drawing")
        schematic = ET.SubElement(drawing, "schematic")
        sheets = ET.SubElement(schematic, "sheets")
        sheet = ET.SubElement(sheets, "sheet")
        nets_elem = ET.SubElement(sheet, "nets")

        # Group pinrefs by net name
        net_groups: dict[str, list] = {}
        for net_name, part, gate, pin in pinrefs:
            net_groups.setdefault(net_name, []).append((part, gate, pin))

        for net_name, pins in net_groups.items():
            net = ET.SubElement(nets_elem, "net", name=net_name)
            segment = ET.SubElement(net, "segment")
            for part, gate, pin in pins:
                ET.SubElement(segment, "pinref", part=part, gate=gate, pin=pin)

        return ET.tostring(root, encoding="unicode")

    def test_multi_gate_qualified(self):
        """Multi-gate parts should have gate-qualified pin names."""
        import xml.etree.ElementTree as ET

        xml_str = self._make_nets_xml([
            ("NET1", "R15", "G$1", "1"),
            ("NET2", "R15", "G$2", "1"),
        ])
        root = ET.fromstring(xml_str)
        part_names = {"R15"}

        # Replicate the two-pass logic from eagle.py
        part_gates: dict[str, set[str]] = {}
        for net_elem in root.iter("net"):
            for pinref in net_elem.iter("pinref"):
                part = pinref.get("part", "")
                gate = pinref.get("gate", "")
                if part in part_names and gate:
                    part_gates.setdefault(part, set()).add(gate)

        multi_gate_parts = {p for p, gates in part_gates.items() if len(gates) > 1}
        assert "R15" in multi_gate_parts

        merged_pins: dict[str, set[str]] = {}
        for net_elem in root.iter("net"):
            net_name = net_elem.get("name", "")
            for pinref in net_elem.iter("pinref"):
                part = pinref.get("part", "")
                pin = pinref.get("pin", "")
                gate = pinref.get("gate", "")
                if part in part_names:
                    if part in multi_gate_parts and gate:
                        pin_str = f"{part}.{gate}.{pin}"
                    else:
                        pin_str = f"{part}.{pin}"
                    merged_pins.setdefault(net_name, set()).add(pin_str)

        assert "R15.G$1.1" in merged_pins["NET1"]
        assert "R15.G$2.1" in merged_pins["NET2"]

    def test_single_gate_unqualified(self):
        """Single-gate parts should NOT have gate-qualified pin names."""
        import xml.etree.ElementTree as ET

        xml_str = self._make_nets_xml([
            ("NET1", "R1", "G$1", "1"),
            ("NET2", "R1", "G$1", "2"),
        ])
        root = ET.fromstring(xml_str)
        part_names = {"R1"}

        part_gates: dict[str, set[str]] = {}
        for net_elem in root.iter("net"):
            for pinref in net_elem.iter("pinref"):
                part = pinref.get("part", "")
                gate = pinref.get("gate", "")
                if part in part_names and gate:
                    part_gates.setdefault(part, set()).add(gate)

        multi_gate_parts = {p for p, gates in part_gates.items() if len(gates) > 1}
        assert "R1" not in multi_gate_parts

        merged_pins: dict[str, set[str]] = {}
        for net_elem in root.iter("net"):
            net_name = net_elem.get("name", "")
            for pinref in net_elem.iter("pinref"):
                part = pinref.get("part", "")
                pin = pinref.get("pin", "")
                gate = pinref.get("gate", "")
                if part in part_names:
                    if part in multi_gate_parts and gate:
                        pin_str = f"{part}.{gate}.{pin}"
                    else:
                        pin_str = f"{part}.{pin}"
                    merged_pins.setdefault(net_name, set()).add(pin_str)

        assert "R1.1" in merged_pins["NET1"]
        assert "R1.2" in merged_pins["NET2"]


# ---------------------------------------------------------------------------
# Decoupling Proximity (P5)
# ---------------------------------------------------------------------------

class TestDecouplingProximity:
    """Test position-based decoupling cap annotation."""

    @pytest.fixture(autouse=True)
    def setup(self):

        from parse_boards import (
            annotate_circuit_roles, Component, Net, Position,
        )
        self.annotate = annotate_circuit_roles
        self.Component = Component
        self.Net = Net
        self.Position = Position

    def test_nearby_ic_included(self):
        """IC within 10mm should appear in decouples annotation."""
        cap = self.Component(ref="C1", value="100nF", footprint="0402")
        ic_near = self.Component(ref="U1", value="STM32", footprint="QFN-48")
        ic_far = self.Component(ref="U2", value="ESP32", footprint="QFN-48")

        nets = [
            self.Net(name="3.3V", pins=["C1.1", "U1.VCC", "U2.VCC"]),
            self.Net(name="GND", pins=["C1.2", "U1.GND", "U2.GND"]),
        ]
        positions = [
            self.Position(ref="C1", x=10.0, y=10.0),
            self.Position(ref="U1", x=12.0, y=10.0),   # 2mm away
            self.Position(ref="U2", x=100.0, y=100.0),  # ~127mm away
        ]

        self.annotate([cap, ic_near, ic_far], nets, positions)
        assert cap.attributes.get("decouples") == "U1"

    def test_far_ic_excluded(self):
        """IC >15mm away should NOT appear in decouples annotation."""
        cap = self.Component(ref="C1", value="100nF", footprint="0402")
        ic_far = self.Component(ref="U1", value="STM32", footprint="QFN-48")

        nets = [
            self.Net(name="3.3V", pins=["C1.1", "U1.VCC"]),
            self.Net(name="GND", pins=["C1.2", "U1.GND"]),
        ]
        positions = [
            self.Position(ref="C1", x=10.0, y=10.0),
            self.Position(ref="U1", x=100.0, y=100.0),
        ]

        self.annotate([cap, ic_far], nets, positions)
        # IC is ~127mm away — beyond 15mm threshold, no annotation
        assert "decouples" not in cap.attributes

    def test_no_positions_single_ic(self):
        """Without position data and single IC, decouples should annotate it."""
        cap = self.Component(ref="C1", value="100nF", footprint="0402")
        ic = self.Component(ref="U1", value="IC1", footprint="QFN")

        nets = [
            self.Net(name="3.3V", pins=["C1.1", "U1.VCC"]),
            self.Net(name="GND", pins=["C1.2", "U1.GND"]),
        ]

        self.annotate([cap, ic], nets)
        assert cap.attributes.get("decouples") == "U1"

    def test_no_positions_multi_ic_skipped(self):
        """Without position data and multiple ICs, no annotation (ambiguous)."""
        cap = self.Component(ref="C1", value="100nF", footprint="0402")
        ics = [self.Component(ref=f"U{i}", value=f"IC{i}", footprint="QFN")
               for i in range(1, 6)]

        nets = [
            self.Net(name="3.3V", pins=["C1.1"] + [f"U{i}.VCC" for i in range(1, 6)]),
            self.Net(name="GND", pins=["C1.2"] + [f"U{i}.GND" for i in range(1, 6)]),
        ]

        self.annotate([cap] + ics, nets)
        assert "decouples" not in cap.attributes


# ---------------------------------------------------------------------------
# _decode_mpn_value — new MPN patterns (P6)
# ---------------------------------------------------------------------------

class TestDecodeMpnValue:
    @pytest.fixture(autouse=True)
    def setup(self):

        from parse_boards import _decode_mpn_value
        self.decode = _decode_mpn_value

    def test_vkmd_polymer(self):
        """VKMD1451H221MV → 220uF."""
        assert self.decode("VKMD1451H221MV", "C") == "220uF"

    def test_eeefk_electrolytic(self):
        """EEEFK1H470P → 47uF."""
        assert self.decode("EEEFK1H470P", "C") == "47uF"

    def test_50svpf_polymer(self):
        """50SVPF18M → 18uF."""
        assert self.decode("50SVPF18M", "C") == "18uF"

    def test_dr73_inductor(self):
        """DR73-100-R → 10uH."""
        assert self.decode("DR73-100-R", "L") == "10uH"

    def test_1206l_fuse(self):
        """1206L012THR → 120mA PTC."""
        assert self.decode("1206L012THR", "F") == "120mA PTC"

    def test_current_sense_r003(self):
        """KRL3216T4-M-R003-F-T1 → 3mohm."""
        assert self.decode("KRL3216T4-M-R003-F-T1", "R") == "3mohm"

    def test_current_sense_r004(self):
        """KRL3216T4-M-R004-F-T1 → 4mohm."""
        assert self.decode("KRL3216T4-M-R004-F-T1", "R") == "4mohm"


# ---------------------------------------------------------------------------
# Value Cleanup (P7)
# ---------------------------------------------------------------------------

class TestValueCleanup:
    def test_backslash_n(self):
        """Literal backslash-n should be removed."""
        assert normalize_value("100\\n", "R1") == "100ohm"

    def test_package_suffix(self):
        """Trailing package suffix should be stripped."""
        assert normalize_value("10k R0402", "R1") == "10kohm"

    def test_parenthetical_package(self):
        """Parenthetical package should be stripped."""
        # DW01+G(SOT23-6) is an IC — passes through unchanged
        assert normalize_value("DW01+G(SOT23-6)", "U1") == "DW01+G"

    def test_kicad_naming_convention_cap(self):
        """C_100n_0402 → 100nF."""
        assert normalize_value("C_100n_0402", "C1") == "100nF"

    def test_kicad_naming_convention_res(self):
        """R_10k_0603 → 10kohm."""
        assert normalize_value("R_10k_0603", "R1") == "10kohm"

    def test_kicad_naming_convention_inductor(self):
        """L_1u_5.5A_Bourns-SRP3212A → 1uH."""
        assert normalize_value("L_1u_5.5A_Bourns-SRP3212A", "L1") == "1uH"

    def test_kicad_naming_convention_zero_ohm(self):
        """R_0R_1206 → 0ohm."""
        assert normalize_value("R_0R_1206", "R1") == "0ohm"

    def test_solder_jumper_nc(self):
        """Eagle JUMPER-SMT_2_NC_TRACE → solder jumper (NC)."""
        assert normalize_value("JUMPER-SMT_2_NC_TRACE", "SJ1") == "solder jumper (NC)"

    def test_solder_jumper_no(self):
        """Eagle JUMPER-SMT_2_NO → solder jumper (NO)."""
        assert normalize_value("JUMPER-SMT_2_NO", "SJ1") == "solder jumper (NO)"

    def test_solderjumper_bare(self):
        """SOLDERJUMPER → solder jumper."""
        assert normalize_value("SOLDERJUMPER", "SJ1") == "solder jumper"

    def test_diode_symbol_schottky(self):
        """D_Schottky → schottky."""
        assert normalize_value("D_Schottky", "D1") == "schottky"

    def test_filter_symbol(self):
        """Filter_EMI_CommonMode → common mode filter."""
        assert normalize_value("Filter_EMI_CommonMode", "FL1") == "common mode filter"

    def test_power_rating_extraction(self):
        """Power rating should be extracted from inline specs."""
        val, specs = extract_inline_specs("100 2W")
        assert val == "100"
        assert specs.get("power") == "2W"

    def test_fractional_power(self):
        val, specs = extract_inline_specs("10k 1/4W")
        assert val == "10k"
        assert specs.get("power") == "1/4W"

    def test_testpoint_symbol(self):
        """TESTPOINT → test point."""
        assert normalize_value("TESTPOINT", "TP1") == "test point"

    def test_tp_symbol(self):
        """TP → test point."""
        assert normalize_value("TP", "D+1") == "test point"

    def test_sw_push_symbol(self):
        """SW_Push → tactile switch."""
        assert normalize_value("SW_Push", "SW1") == "tactile switch"

    def test_mounting_hole_variants(self):
        """MountingHole and HOLE_ variants → mounting hole."""
        assert normalize_value("MountingHole", "H1") == "mounting hole"
        assert normalize_value("MountingHole_Pad", "H1") == "mounting hole"
        assert normalize_value("HOLE_3.2mm", "H1") == "mounting hole"

    def test_european_notation(self):
        """100E → 100ohm, 330E → 330ohm, 4E7 → 4.7ohm."""
        assert normalize_value("100E", "R1") == "100ohm"
        assert normalize_value("330E", "R1") == "330ohm"
        assert normalize_value("4E7", "R1") == "4.7ohm"

    def test_u1_cap_notation(self):
        """u1 → 100nF (shorthand for 0.1uF)."""
        assert normalize_value("u1", "C1") == "100nF"

    def test_led_color_footprint(self):
        """BLUE-0603 → blue LED."""
        assert normalize_value("BLUE-0603", "D1") == "blue LED"

    def test_ic_package_suffix(self):
        """IC value with _UQFN suffix should be stripped."""
        assert normalize_value("TXB0104_UQFN", "U1") == "TXB0104"
        assert normalize_value("MCP23017T-E_QFN", "U1") == "MCP23017T-E"
        assert normalize_value("AP62301_TSOT", "U1") == "AP62301"

    def test_pkl_jumper(self):
        """pkl_jumper → solder jumper."""
        assert normalize_value("pkl_jumper", "SJ1") == "solder jumper"

    def test_oscillator_value(self):
        """25MHz for U ref → 25MHz oscillator."""
        assert normalize_value("25MHz", "U1") == "25MHz oscillator"

    def test_crystal_24m(self):
        """24M for Y ref → 24MHz."""
        assert normalize_value("24M", "Y1") == "24MHz"

    def test_trailing_comma(self):
        """600R, → 600ohm (trailing comma stripped)."""
        assert normalize_value("600R,", "R1") == "600ohm"

    def test_stemma_i2c(self):
        """STEMMA_I2C → STEMMA QT."""
        assert normalize_value("STEMMA_I2C", "CONN1") == "STEMMA QT"

    def test_qwiic(self):
        """QWIIC_RIGHT_ANGLE → Qwiic connector."""
        assert normalize_value("QWIIC_RIGHT_ANGLE", "J1") == "Qwiic connector"

    def test_reflowable_battery(self):
        """RELOWABLE_BATTERY → reflowable battery."""
        assert normalize_value("RELOWABLE_BATTERY", "BT1") == "reflowable battery"

    def test_ldo_voltage(self):
        """LDO_2V5 → 2.5V LDO."""
        assert normalize_value("LDO_2V5", "U1") == "2.5V LDO"

    def test_type_c_mpn(self):
        """TYPE-C-31-M-12 → USB-C."""
        assert normalize_value("TYPE-C-31-M-12", "J1") == "USB-C"

    def test_ferritebead_camelcase(self):
        """FerriteBead → ferrite bead."""
        assert normalize_value("FerriteBead", "FB1") == "ferrite bead"

    def test_fuse_symbol(self):
        """Fuse → fuse."""
        assert normalize_value("Fuse", "F1") == "fuse"

    def test_fuse_with_rating(self):
        """F_7A_1206 → 7A fuse."""
        assert normalize_value("F_7A_1206", "F1") == "7A fuse"

    def test_test_hyphen_point(self):
        """TEST-POINT → test point."""
        assert normalize_value("TEST-POINT", "TP1") == "test point"

    def test_rf_shield(self):
        """RF_SHIELD_FRAME → RF shield."""
        assert normalize_value("RF_SHIELD_FRAME", "SH1") == "RF shield"

    def test_mh_mounting_hole(self):
        """MH → mounting hole."""
        assert normalize_value("MH", "H1") == "mounting hole"

    def test_switch_bare(self):
        """SWITCH → switch."""
        assert normalize_value("SWITCH", "SW1") == "switch"

    def test_tilde_solder_jumper(self):
        """~ for SJ ref → solder jumper."""
        assert normalize_value("~", "SJ1") == "solder jumper"

    def test_tilde_mounting_hole(self):
        """~ for H ref → mounting hole."""
        assert normalize_value("~", "H1") == "mounting hole"

    def test_tilde_test_point(self):
        """~ for TP ref → test point."""
        assert normalize_value("~", "TP1") == "test point"

    def test_tilde_other_ref(self):
        """~ for generic ref → empty string."""
        assert normalize_value("~", "U1") == ""

    def test_nc_normalized(self):
        """nc → NC (case-normalized)."""
        assert normalize_value("nc", "R1") == "NC"
        assert normalize_value("NC", "C1") == "NC"

    def test_tp_short_open(self):
        """TP_SHORT / TP_OPEN → test point."""
        assert normalize_value("TP_SHORT", "TP1") == "test point"
        assert normalize_value("TP_OPEN", "TP2") == "test point"

    def test_na_passive_value(self):
        """NA(47uF C0805) → 47uF (Olimex boards)."""
        assert normalize_value("NA(47uF C0805)", "C1") == "47uF"
        assert normalize_value("NA(10k R0402)", "R1") == "10kohm"
        assert normalize_value("NA(100nF C04020)", "C1") == "100nF"

    def test_na_ic_value(self):
        """NA(RCLAMP0524P(SLP2510P8)) → RCLAMP0524P."""
        assert normalize_value("NA(RCLAMP0524P(SLP2510P8))", "U1") == "RCLAMP0524P"

    def test_na_resistor_with_mpn(self):
        """NA(600R UPZ2012E-601-2R0TF) → 600ohm."""
        assert normalize_value("NA(600R UPZ2012E-601-2R0TF)", "R1") == "600ohm"

    def test_na_ferrite_bead_impedance(self):
        """NA(600R UPZ2012E-601-2R0TF) for L ref → 600ohm (ferrite bead impedance)."""
        assert normalize_value("NA(600R UPZ2012E-601-2R0TF)", "L5") == "600ohm"

    def test_active_low_in_value(self):
        """~{RESET} in value → nRESET."""
        assert normalize_value("~{RESET}", "U1") == "nRESET"

    def test_bare_color_led(self):
        """Bare color names on D/LED refs → 'color LED'."""
        assert normalize_value("RED", "D1") == "red LED"
        assert normalize_value("GREEN", "LED1") == "green LED"
        assert normalize_value("BLUE", "D3") == "blue LED"

    def test_color_abbreviation_led(self):
        """Color abbreviations on D/LED refs → 'color LED'."""
        assert normalize_value("GRN", "D1") == "green LED"
        assert normalize_value("BLU", "D2") == "blue LED"
        assert normalize_value("WHT", "D3") == "white LED"

    def test_sparkfun_logo_junk(self):
        """SparkFun_Logo → logo (junk component)."""
        assert normalize_value("SparkFun_Logo", "G1") == "logo"

    def test_ic_rget_suffix(self):
        """BQ24295_RGET → BQ24295 (strip TI package code)."""
        # _RGET is handled by IC package suffix pattern
        assert normalize_value("BQ24295_RGET", "U1") == "BQ24295"


# ---------------------------------------------------------------------------
# Sanity Bounds (P4)
# ---------------------------------------------------------------------------

class TestSanityBounds:
    def test_reject_cap_over_10f(self):
        """Cap > 10F should return raw value."""
        # A very large number that would exceed 10F
        result = normalize_value("100", "C1")  # 100F would be insane
        # 100 as bare number for C → 100pF (tiny), that's fine
        # Let's test with explicit huge value
        assert normalize_value("20000000u", "C1") == "20000000u"  # 20F > 10F

    def test_reject_inductor_over_100h(self):
        """Inductor > 100H should return raw value."""
        assert normalize_value("200000000u", "L1") == "200000000u"  # 200H > 100H

    def test_reject_resistor_over_1g(self):
        """Resistor > 1Gohm should return raw value."""
        assert normalize_value("2G", "R1") == "2G"  # 2Gohm > 1Gohm

    def test_normal_values_pass(self):
        """Normal values should still work."""
        assert normalize_value("100n", "C1") == "100nF"
        assert normalize_value("10u", "L1") == "10uH"
        assert normalize_value("10k", "R1") == "10kohm"


# ---------------------------------------------------------------------------
# Clean Pin Name (active-low / LaTeX)
# ---------------------------------------------------------------------------

class TestCleanPinName:
    def test_latex_subscript(self):
        """V_{CC} → VCC."""
        assert _clean_pin_name("V_{CC}") == "VCC"

    def test_active_low(self):
        """~{RESET} → nRESET."""
        assert _clean_pin_name("~{RESET}") == "nRESET"

    def test_active_low_in_pin(self):
        """U3.~{INT} → U3.nINT."""
        assert _clean_pin_name("U3.~{INT}") == "U3.nINT"

    def test_net_with_active_low(self):
        """Net-(U3-~{SD_MODE}) → Net-(U3-nSD_MODE)."""
        assert _clean_pin_name("Net-(U3-~{SD_MODE})") == "Net-(U3-nSD_MODE)"

    def test_hierarchical_active_low(self):
        """/~{USB_BOOT_2} → /nUSB_BOOT_2."""
        assert _clean_pin_name("/~{USB_BOOT_2}") == "/nUSB_BOOT_2"

    def test_plain_passthrough(self):
        """Plain pin name passes through."""
        assert _clean_pin_name("U1.SDA") == "U1.SDA"

    def test_slash_escape(self):
        """A5{slash}CC1 → A5/CC1."""
        assert _clean_pin_name("USB1.A5{slash}CC1") == "USB1.A5/CC1"


# ---------------------------------------------------------------------------
# Junk Ref Placeholders
# ---------------------------------------------------------------------------

class TestJunkRefPlaceholders:
    @pytest.fixture(autouse=True)
    def setup(self):

        from parsers.common import is_junk_ref
        self.is_junk = is_junk_ref

    def test_question_mark(self):
        assert self.is_junk("?")

    def test_asterisk(self):
        assert self.is_junk("*")

    def test_empty(self):
        assert self.is_junk("")

    def test_u_question(self):
        assert self.is_junk("U?")

    def test_r_question(self):
        assert self.is_junk("R?")

    def test_normal_ref_not_junk(self):
        assert not self.is_junk("U1")
        assert not self.is_junk("R10")


# ---------------------------------------------------------------------------
# Key ICs from Components (Step 6)
# ---------------------------------------------------------------------------

class TestKeyIcsFromComponents:
    @pytest.fixture(autouse=True)
    def setup(self):

        from parse_boards import _extract_key_ics_from_components, Component
        self.extract = _extract_key_ics_from_components
        self.Component = Component

    def test_basic_extraction(self):
        comps = [
            self.Component(ref="U1", value="STM32F103", footprint="QFN-48"),
            self.Component(ref="U2", value="BME280", footprint="LGA-8"),
            self.Component(ref="R1", value="10kohm", footprint="0402"),
        ]
        result = self.extract(comps)
        assert "STM32F103" in result
        assert "BME280" in result
        assert len(result) == 2  # R1 not included

    def test_skip_dnp(self):
        comps = [
            self.Component(ref="U1", value="DNP", footprint="QFN-48"),
        ]
        assert self.extract(comps) == []

    def test_dedup_by_family(self):
        comps = [
            self.Component(ref="U1", value="STM32F103C8T6", footprint="QFN"),
            self.Component(ref="U2", value="STM32F103RBT6", footprint="QFN"),
        ]
        result = self.extract(comps)
        assert len(result) == 1  # same STM32F103 family

    def test_cap_at_five(self):
        comps = [
            self.Component(ref=f"U{i}", value=f"IC{i}000", footprint="QFN")
            for i in range(1, 8)
        ]
        result = self.extract(comps)
        assert len(result) <= 5
