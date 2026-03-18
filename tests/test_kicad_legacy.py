"""Unit tests for KiCad legacy .sch parser."""

import textwrap
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from parsers.kicad_legacy import parse_schematic, _parse_f_line, _parse_comp_block


# ---------------------------------------------------------------------------
# F-line parsing
# ---------------------------------------------------------------------------

class TestParseFLine:
    def test_basic_f0(self):
        result = _parse_f_line('F 0 "U101" H 2300 2475 50  0000 L CNN')
        assert result == (0, "U101", "")

    def test_basic_f1(self):
        result = _parse_f_line('F 1 "FT230X" H 2300 2375 50  0000 L CNN')
        assert result == (1, "FT230X", "")

    def test_basic_f2(self):
        result = _parse_f_line('F 2 "SSOP16" H 2300 2275 50  0001 L CNN')
        assert result == (2, "SSOP16", "")

    def test_basic_f3(self):
        result = _parse_f_line('F 3 "" H 2300 2175 50  0001 L CNN')
        assert result == (3, "", "")

    def test_custom_field_partnumber(self):
        result = _parse_f_line('F 4 "RC0603FR-0710KL" H 2250 2375 60  0001 C CNN "PartNumber"')
        assert result == (4, "RC0603FR-0710KL", "PartNumber")

    def test_custom_field_manufacturer(self):
        result = _parse_f_line('F 5 "Texas Instruments" H 0 0 50  0001 C CNN "Manufacturer"')
        assert result == (5, "Texas Instruments", "Manufacturer")

    def test_custom_field_mfg(self):
        result = _parse_f_line('F 4 "Lattice" H 0 0 50  0001 C CNN "Mfg"')
        assert result == (4, "Lattice", "Mfg")

    def test_invalid_line(self):
        assert _parse_f_line("not an f line") is None

    def test_empty_custom_field(self):
        result = _parse_f_line('F 4 "" H 0 0 50  0001 C CNN "PartNumber"')
        assert result == (4, "", "PartNumber")


# ---------------------------------------------------------------------------
# L-line / component block parsing
# ---------------------------------------------------------------------------

class TestParseCompBlock:
    def test_l_line_v2_no_lib_prefix(self):
        """KiCad v2 format: L FT230X U101 (no library prefix)."""
        lines = [
            "L FT230X U101",
            "U 1 1 540B18CA",
            "P 2250 2375",
            'F 0 "U101" H 2300 2475 50  0000 L CNN',
            'F 1 "FT230X" H 2300 2375 50  0000 L CNN',
            'F 2 "SSOP-16" H 2300 2275 50  0001 L CNN',
            'F 3 "" H 0 0 50  0001 C CNN',
        ]
        comp = _parse_comp_block(lines, set())
        assert comp is not None
        assert comp.ref == "U101"
        assert comp.value == "FT230X"

    def test_l_line_v4_with_lib_prefix(self):
        """KiCad v4 format: L Connector:USB_C J1 (with library prefix)."""
        lines = [
            "L Connector:USB_C J1",
            "U 1 1 5C1234AB",
            "P 1000 1000",
            'F 0 "J1" H 1000 1100 50  0000 L CNN',
            'F 1 "USB_C" H 1000 900 50  0000 L CNN',
            'F 2 "USB_C_Receptacle" H 0 0 50  0001 C CNN',
            'F 3 "" H 0 0 50  0001 C CNN',
        ]
        comp = _parse_comp_block(lines, set())
        assert comp is not None
        assert comp.ref == "J1"

    def test_skip_power_symbol(self):
        """Components with # prefix in ref are power symbols — skip."""
        lines = [
            "L power:GND #PWR01",
            "U 1 1 5ABC1234",
            "P 1000 1000",
            'F 0 "#PWR01" H 1000 750 50  0001 C CNN',
            'F 1 "GND" H 1000 850 50  0000 C CNN',
            'F 2 "" H 1000 1000 50  0001 C CNN',
            'F 3 "" H 1000 1000 50  0001 C CNN',
        ]
        comp = _parse_comp_block(lines, set())
        assert comp is None

    def test_skip_no_footprint(self):
        """Components with empty footprint field are skipped."""
        lines = [
            "L Device:R R1",
            "U 1 1 5ABC1234",
            "P 1000 1000",
            'F 0 "R1" H 1000 1100 50  0000 L CNN',
            'F 1 "10k" H 1000 900 50  0000 L CNN',
            'F 2 "" H 0 0 50  0001 C CNN',
            'F 3 "" H 0 0 50  0001 C CNN',
        ]
        comp = _parse_comp_block(lines, set())
        assert comp is None

    def test_skip_junk_ref(self):
        """FRAME, LOGO, FID refs are filtered."""
        for prefix in ("FRAME", "LOGO", "FID"):
            lines = [
                f"L Graphic:{prefix} {prefix}1",
                "U 1 1 5ABC1234",
                "P 1000 1000",
                f'F 0 "{prefix}1" H 1000 1100 50  0000 L CNN',
                f'F 1 "{prefix}" H 1000 900 50  0000 L CNN',
                f'F 2 "SomeFootprint" H 0 0 50  0001 C CNN',
                f'F 3 "" H 0 0 50  0001 C CNN',
            ]
            comp = _parse_comp_block(lines, set())
            assert comp is None, f"{prefix} ref should be filtered"

    def test_multi_unit_dedup(self):
        """Same ref with different unit numbers → only one component."""
        lines_unit1 = [
            "L Device:R_Pack04 RN1",
            "U 1 1 5ABC1234",
            "P 1000 1000",
            'F 0 "RN1" H 1000 1100 50  0000 L CNN',
            'F 1 "4x10k" H 1000 900 50  0000 L CNN',
            'F 2 "R_Array_Concave_4x0603" H 0 0 50  0001 C CNN',
            'F 3 "" H 0 0 50  0001 C CNN',
        ]
        lines_unit2 = [
            "L Device:R_Pack04 RN1",
            "U 2 1 5ABC5678",
            "P 2000 1000",
            'F 0 "RN1" H 2000 1100 50  0000 L CNN',
            'F 1 "4x10k" H 2000 900 50  0000 L CNN',
            'F 2 "R_Array_Concave_4x0603" H 0 0 50  0001 C CNN',
            'F 3 "" H 0 0 50  0001 C CNN',
        ]
        seen = set()
        comp1 = _parse_comp_block(lines_unit1, seen)
        comp2 = _parse_comp_block(lines_unit2, seen)
        assert comp1 is not None
        assert comp2 is None  # deduped

    def test_custom_fields_to_attributes(self):
        """F4+ fields with names map to attributes via build_attributes."""
        lines = [
            "L Device:R R1",
            "U 1 1 5ABC1234",
            "P 1000 1000",
            'F 0 "R1" H 1000 1100 50  0000 L CNN',
            'F 1 "10k" H 1000 900 50  0000 L CNN',
            'F 2 "R_0603" H 0 0 50  0001 C CNN',
            'F 3 "" H 0 0 50  0001 C CNN',
            'F 4 "RC0603FR-0710KL" H 0 0 50  0001 C CNN "PartNumber"',
            'F 5 "Yageo" H 0 0 50  0001 C CNN "MANUFACTURER"',
        ]
        comp = _parse_comp_block(lines, set())
        assert comp is not None
        assert comp.attributes.get("mpn") == "RC0603FR-0710KL"
        assert comp.attributes.get("manufacturer") == "Yageo"

    def test_footprint_lib_prefix_stripped(self):
        """Footprint library prefix is stripped: Capacitor_SMD:C_0805 → C_0805."""
        lines = [
            "L Device:C C1",
            "U 1 1 5ABC1234",
            "P 1000 1000",
            'F 0 "C1" H 1000 1100 50  0000 L CNN',
            'F 1 "100nF" H 1000 900 50  0000 L CNN',
            'F 2 "Capacitor_SMD:C_0805_2012Metric" H 0 0 50  0001 C CNN',
            'F 3 "" H 0 0 50  0001 C CNN',
        ]
        comp = _parse_comp_block(lines, set())
        assert comp is not None
        assert comp.package == "C_0805_2012Metric"
        # footprint should be normalized (no library prefix)
        assert "Capacitor_SMD" not in comp.footprint

    def test_value_normalization(self):
        """Value goes through normalize_value (resistors get 'ohm' suffix)."""
        lines = [
            "L Device:R R1",
            "U 1 1 5ABC1234",
            "P 1000 1000",
            'F 0 "R1" H 1000 1100 50  0000 L CNN',
            'F 1 "10k" H 1000 900 50  0000 L CNN',
            'F 2 "R_0402" H 0 0 50  0001 C CNN',
            'F 3 "" H 0 0 50  0001 C CNN',
        ]
        comp = _parse_comp_block(lines, set())
        assert comp is not None
        assert comp.value == "10kohm"


# ---------------------------------------------------------------------------
# Full schematic parsing with files
# ---------------------------------------------------------------------------

class TestParseSchematic:
    def test_multi_sheet_recursion(self, tmp_path):
        """Parent + sub-sheet → components from both."""
        sub_sch = tmp_path / "sub.sch"
        sub_sch.write_text(textwrap.dedent("""\
            EESchema Schematic File Version 4
            $Comp
            L Device:R R2
            U 1 1 5ABC5678
            P 2000 1000
            F 0 "R2" H 2000 1100 50  0000 L CNN
            F 1 "4.7k" H 2000 900 50  0000 L CNN
            F 2 "R_0603" H 0 0 50  0001 C CNN
            F 3 "" H 0 0 50  0001 C CNN
            $EndComp
            $EndSCHEMATC
        """))

        main_sch = tmp_path / "main.sch"
        main_sch.write_text(textwrap.dedent("""\
            EESchema Schematic File Version 4
            $Comp
            L Device:C C1
            U 1 1 5ABC1234
            P 1000 1000
            F 0 "C1" H 1000 1100 50  0000 L CNN
            F 1 "100nF" H 1000 900 50  0000 L CNN
            F 2 "C_0805" H 0 0 50  0001 C CNN
            F 3 "" H 0 0 50  0001 C CNN
            $EndComp
            $Sheet
            S 3000 1000 500 500
            F0 "Power" 50
            F1 "sub.sch" 50
            $EndSheet
            $EndSCHEMATC
        """))

        components, nets = parse_schematic(main_sch)
        refs = {c.ref for c in components}
        assert "C1" in refs
        assert "R2" in refs
        assert len(components) == 2

    def test_missing_subsheet_no_crash(self, tmp_path):
        """Missing sub-sheet file → warning, no crash."""
        main_sch = tmp_path / "main.sch"
        main_sch.write_text(textwrap.dedent("""\
            EESchema Schematic File Version 4
            $Comp
            L Device:C C1
            U 1 1 5ABC1234
            P 1000 1000
            F 0 "C1" H 1000 1100 50  0000 L CNN
            F 1 "100nF" H 1000 900 50  0000 L CNN
            F 2 "C_0805" H 0 0 50  0001 C CNN
            F 3 "" H 0 0 50  0001 C CNN
            $EndComp
            $Sheet
            S 3000 1000 500 500
            F0 "Power" 50
            F1 "nonexistent.sch" 50
            $EndSheet
            $EndSCHEMATC
        """))

        components, nets = parse_schematic(main_sch)
        assert len(components) == 1
        assert components[0].ref == "C1"

    def test_cycle_protection(self, tmp_path):
        """Circular sheet reference → no infinite loop."""
        sch_a = tmp_path / "a.sch"
        sch_b = tmp_path / "b.sch"

        sch_a.write_text(textwrap.dedent("""\
            EESchema Schematic File Version 4
            $Comp
            L Device:R R1
            U 1 1 5ABC1234
            P 1000 1000
            F 0 "R1" H 1000 1100 50  0000 L CNN
            F 1 "10k" H 1000 900 50  0000 L CNN
            F 2 "R_0402" H 0 0 50  0001 C CNN
            F 3 "" H 0 0 50  0001 C CNN
            $EndComp
            $Sheet
            S 3000 1000 500 500
            F0 "SheetB" 50
            F1 "b.sch" 50
            $EndSheet
            $EndSCHEMATC
        """))

        sch_b.write_text(textwrap.dedent("""\
            EESchema Schematic File Version 4
            $Comp
            L Device:C C1
            U 1 1 5DEF5678
            P 2000 1000
            F 0 "C1" H 2000 1100 50  0000 L CNN
            F 1 "100nF" H 2000 900 50  0000 L CNN
            F 2 "C_0603" H 0 0 50  0001 C CNN
            F 3 "" H 0 0 50  0001 C CNN
            $EndComp
            $Sheet
            S 3000 1000 500 500
            F0 "SheetA" 50
            F1 "a.sch" 50
            $EndSheet
            $EndSCHEMATC
        """))

        components, nets = parse_schematic(sch_a)
        refs = {c.ref for c in components}
        assert "R1" in refs
        assert "C1" in refs
        assert len(components) == 2  # no infinite loop, no duplicates
