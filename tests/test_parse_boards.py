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
    extract_tags,
    parse_boards_md,
    _clean_pin_name,
    _decode_mpn_value,
    find_schematic,
)


class TestBoardConflictAudit:
    @pytest.mark.parametrize("mpn,prefix,expected", [
        ("UMK212BBJ475KG-T", "C", {"value": "4.7uF", "voltage": "50V", "tolerance": "10%"}),
        ("CL21C751JBCNNNC", "C", {"value": "750pF", "voltage": "50V", "tolerance": "5%", "dielectric": "C0G"}),
        ("CL05C470JB5NNNC", "C", {"value": "47pF", "voltage": "50V", "tolerance": "5%", "dielectric": "C0G"}),
        ("CL32B106KMVNNWE", "C", {"value": "10uF", "voltage": "63V", "tolerance": "10%", "dielectric": "X7R"}),
        ("GRM188R71H104KA01D", "C", {"value": "100nF", "voltage": "50V", "tolerance": "10%", "dielectric": "X7R"}),
        ("GRM1555C1H1R0CA01D", "C", {"value": "1pF", "voltage": "50V", "tolerance": "0.25pF", "dielectric": "C0G"}),
        ("CC0201CRNPO9BNR50", "C", {"value": "0.5pF", "voltage": "50V", "tolerance": "0.25pF", "dielectric": "C0G"}),
        ("CC0402MRX5R5BB106", "C", {"value": "10uF", "voltage": "6.3V", "tolerance": "20%", "dielectric": "X5R"}),
        ("C2012X5R1V226M125AC", "C", {"value": "22uF", "voltage": "35V", "tolerance": "20%", "dielectric": "X5R"}),
        ("C0603C220J4GACTU", "C", {"value": "22pF", "voltage": "16V", "tolerance": "5%", "dielectric": "C0G"}),
        ("C0603X103K2RECTU", "C", {"value": "10nF", "voltage": "200V", "tolerance": "10%", "dielectric": "X7R"}),
        ("ECJ-2VB1H104K", "C", {"value": "100nF", "voltage": "50V", "tolerance": "10%", "dielectric": "X7R"}),
        ("URZ1J221MHD1TO", "C", {"value": "220uF", "voltage": "63V", "tolerance": "20%"}),
        ("RC0805FR-0747KL", "R", {"value": "47kohm", "tolerance": "1%"}),
        ("RT0603DRD073K6L", "R", {"value": "3.6kohm", "tolerance": "0.5%"}),
        ("RT0603DRE076K8L", "R", {"value": "6.8kohm", "tolerance": "0.5%"}),
        ("ERJ-2RKF2211X", "R", {"value": "2.21kohm", "tolerance": "1%"}),
        ("CRCW020110K0JNED", "R", {"value": "10kohm", "tolerance": "5%"}),
        ("CR0402-FX-4700GLF", "R", {"value": "470ohm", "tolerance": "1%"}),
        ("RMCF0402ZT0R00", "R", {"value": "0ohm"}),
        ("MCR03EZPFX1001", "R", {"value": "1kohm", "tolerance": "1%"}),
        ("ESR03EZPJ222", "R", {"value": "2.2kohm", "tolerance": "5%"}),
        ("RK73H1ETTP1001F", "R", {"value": "1kohm", "tolerance": "1%"}),
        ("MCMR06X1001FTL", "R", {"value": "1kohm", "tolerance": "1%"}),
        ("WR06X103JTL", "R", {"value": "10kohm", "tolerance": "5%"}),
        ("0603WAF4704T5E", "R", {"value": "4.7Mohm", "tolerance": "1%"}),
        ("HPC 3012BMV-220M", "L", {"value": "22uH", "tolerance": "20%"}),
        ("LQW15AN47NJ00D", "L", {"value": "47nH"}),
        ("MAKK2520H100M", "L", {"value": "10uH"}),
        ("XFL4020-222MEC", "L", {"value": "2.2uH"}),
        ("DR73-100-R", "L", {"value": "10uH"}),
        ("MLZ2012N101LT000", "L", {"value": "100uH"}),
        ("SPM12565VT-100M-D", "L", {"value": "10uH"}),
        ("SRN8040-220M", "L", {"value": "22uH"}),
    ])
    def test_fixed_maker_fields(self, mpn, prefix, expected):
        from audit_board_conflicts import decode_passive_mpn
        assert decode_passive_mpn(mpn, prefix) == expected

    @pytest.mark.parametrize("mpn,prefix", [
        ("CL05B104KO5NNNCC0603KRX7R9BB104C", "C"),
        ("unidentified104K", "C"), ("CL05C470JB5NNNC", "R"),
        ("RC0805FR-0747KL-extra", "R"), ("HPC 9999-220M", "L"),
    ])
    def test_unknown_or_malformed_codes_are_not_decoded(self, mpn, prefix):
        from audit_board_conflicts import decode_passive_mpn
        assert decode_passive_mpn(mpn, prefix) == {}

    def test_description_tolerance_is_not_a_nominal_value(self):
        from audit_board_conflicts import component_conflicts
        for description in ("NPO, +/- 0.1pF", "SMD Inductor 1nH±0.2nH"):
            assert component_conflicts({"ref": "L1", "value": "1nH", "description": description})[0] == []

    def test_same_prefix_different_functional_digits(self):
        from audit_board_conflicts import component_conflicts
        assert component_conflicts({"ref": "U6", "value": "STM32F072CB", "mpn": "STM32F100C4T6B"})[0]
        assert component_conflicts({"ref": "U6", "value": "BQ76940", "mpn": "BQ7694003DBT"})[0] == []
        assert component_conflicts({"ref": "U6", "value": "74LVC1G08", "mpn": "SN74LVC1G08DCKR"})[0] == []

    def test_description_ratings_are_compared_without_changing_the_value(self):
        from audit_board_conflicts import component_conflicts
        comp = {"ref": "C1", "value": "100nF", "mpn": "GRM188R71H104KA01D",
                "description": "100nF 16V X5R 20%"}
        hits, checked = component_conflicts(comp)
        assert checked
        assert {h["spec"] for h in hits} == {"voltage", "dielectric", "tolerance"}
        assert comp["value"] == "100nF"


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

    def test_explicit_pcb_annotation(self, tmp_path):
        md_file = tmp_path / "BOARDS.md"
        md_file.write_text(self.SAMPLE_MD.replace(
            "`hardware/v1.1a/icebreaker.kicad_sch`",
            "`hardware/v1.1a/icebreaker.kicad_sch` (1 sheet; PCB: `PCB/main board.kicad_pcb`)",
        ))
        board = parse_boards_md(md_file)["icebreaker"]
        assert board["schematic_path"] == "hardware/v1.1a/icebreaker.kicad_sch"
        assert board["pcb_path"] == "PCB/main board.kicad_pcb"


# ---------------------------------------------------------------------------
# Subsystem tags: boundaries, explicit stems and semantic exclusions
# ---------------------------------------------------------------------------

class TestExtractTags:
    @pytest.mark.parametrize("coverage, tag", [
        ("Grove I2C", "robotics"),
        ("ESP32-WROVER", "robotics"),
        ("microvolt signal acquisition", "robotics"),
        ("GNSS RTK rover controller", "robotics"),
        ("DFRobot SEN0609", "robotics"),
        ("DDR3L SDRAM", "rf-sdr"),
        ("SiPM photodetector", "sbc"),
        ("contactless smartcard", "rtc"),
        ("SimonK firmware compatible, GPL-3.0", "bluetooth"),
        ("827mA/389mA configurable, NTC foldback", "bluetooth"),
        ("VESC variant", "drone-uav"),
        ("TLV3201 comparator", "audio"),
        ("MAX9934 current sense amplifiers", "audio"),
        ("LM324 error amplifier", "audio"),
        ("MCP4725 DAC setpoint", "audio"),
        ("ADS1115 ADC/DAC frontend", "audio"),
        ("VCOM calibration", "eurorack"),
        ("stallGuard sensorless homing", "sensors"),
        ("nano quadcopter", "adc-dac"),
        ("StealthChop/SpreadCycle", "adc-dac"),
        ("MPPT buck converter with gate drivers", "inverter"),
        ("UCC21520 gate driver, LLC DC-DC converter", "inverter"),
        ("Li-ion battery management (BQ76940)", "battery-charging"),
        ("SAW filter", "cellular"),
    ])
    def test_false_positives(self, coverage, tag):
        assert tag not in extract_tags(coverage)

    @pytest.mark.parametrize("coverage, tag", [
        ("TMC2209 stepper", "motor-control"),
        ("TMC2660", "motor-control"),
        ("WS2812B", "led-driver"),
        ("SK6812MINI-E", "led-driver"),
        ("IS31FL3741A", "led-driver"),
        ("TPS65150", "power-supply"),
        ("TPS651851", "power-supply"),
        ("TPS65186", "power-supply"),
        ("74LVC245", "level-shifting"),
        ("SN65HVD230", "can-bus"),
        ("FT2232H", "usb"),
        ("CC1352P", "zigbee-thread"),
        ("level shifting", "level-shifting"),
        ("level shifters", "level-shifting"),
        ("level-shifting I/O", "level-shifting"),
        ("energy harvesting", "energy-harvesting"),
        ("LoRaWAN", "lora"),
        ("built-in FLASH datalogging", "data-logging"),
        ("SD logging", "data-logging"),
        ("two relays", "relay"),
        ("dual LDOs", "power-supply"),
        ("optoisolated inputs", "isolation"),
        ("LESD5Z5.0CT1G TVS protection", "esd-protection"),
        ("CNC/robotics", "robotics"),
        ("ROVs and thrusters", "robotics"),
        ("BLE 5 sensor board", "bluetooth"),
        ("WiFi/BLE", "bluetooth"),
        ("WiFi+BLE", "bluetooth"),
        ("Thread/BLE coordinator", "bluetooth"),
        ("BLE, USB", "bluetooth"),
        ("BLE5", "bluetooth"),
        ("audio DAC (TLV320DAC3100)", "audio"),
        ("TLV320AIC3206", "audio"),
        ("Eurorack digital macro oscillator", "audio"),
        ("VCO, VCF, VCA, envelope", "eurorack"),
        ("DRV8316CR motor driver", "inverter"),
        ("3-phase BLDC", "inverter"),
    ])
    def test_deliberate_stems_and_bounded_words(self, coverage, tag):
        assert tag in extract_tags(coverage)

    def test_matching_is_case_insensitive_sorted_and_unique(self):
        assert extract_tags("bLe, BLUETOOTH, ws2812b") == ["bluetooth", "led-driver"]

    def test_explicit_stems_still_require_a_left_boundary(self):
        assert "motor-control" not in extract_tags("NOTMC2209")
        assert "led-driver" not in extract_tags("XWS2812B")

    def test_semantic_overrides(self):
        from board_overrides import TAG_OVERRIDES
        assert TAG_OVERRIDES["axiom-motor-controller"] == ["inverter", "motor-control"]
        # HEEV's phase bridge is a separate board (J111 "Trinamic-Bridge"): no inverter on this one
        assert "inverter" not in TAG_OVERRIDES["heev-motor-controller-2018"]
        assert TAG_OVERRIDES["daq-4ch-16-bit-100ksps"] == ["adc-dac"]
        assert TAG_OVERRIDES["mte-usb-hub"] == ["usb"]


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

    @pytest.mark.parametrize("value, expected", [
        ("1MEG", "1Mohm"), ("10MEG", "10Mohm"),
        ("1meg", "1Mohm"), ("1Meg", "1Mohm"),
    ])
    def test_spice_mega_suffix(self, value, expected):
        assert normalize_value(value, "R1") == expected

    @pytest.mark.parametrize("ref", ["C1", "L1"])
    @pytest.mark.parametrize("value", ["1MEG", "1meg", "1Meg", "1M"])
    def test_mega_suffix_is_resistor_only(self, ref, value):
        assert normalize_value(value, ref) == value

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
    @pytest.mark.parametrize("magnitude, expected", [
        ("1000", "1nF"), ("3900", "3.9nF"), ("2200", "2.2nF"), ("4700", "4.7nF"),
        ("1206", "1.206nF"),
    ])
    def test_four_digit_capacitance(self, magnitude, expected):
        value, specs = extract_inline_specs(f"{magnitude} pF 50V 0402")
        assert value == f"{magnitude} pF"
        assert specs == {"voltage": "50V"}
        assert normalize_value(value, "C1") == expected

    @pytest.mark.parametrize("package", ["01005", "0201", "0402", "0603", "0805", "1206", "1210"])
    @pytest.mark.parametrize("template", ["100nF {}", "{} 100nF"])
    def test_embedded_package(self, package, template):
        assert extract_inline_specs(template.format(package)) == ("100nF", {})

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

    def test_makk2520h_inductor(self):
        assert self.decode("MAKK2520H100M", "L") == "10uH"
        assert normalize_value("MAKK2520H100M", "L1") == "10uH"
        assert self.decode("MAKK2520H100M", "C") is None
        assert self.decode("MAKK9999H100M", "L") is None
        assert self.decode("MAKK2520H100M-extra", "L") is None

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

class TestDimensionAttributes:
    @pytest.mark.parametrize("unit", ["mm", "cm", "m", "mil", "in", "inch", "um", "µm"])
    def test_unit_only_height_is_dropped(self, unit):
        from parsers.common import build_attributes
        assert build_attributes({"HEIGHT": f" {unit} ", "MPN": "SJ-3524-SMT-TR"}) == {
            "mpn": "SJ-3524-SMT-TR",
        }

    @pytest.mark.parametrize("height", ["1mm", "0.5mm", "1.20 mm", "2.5"])
    def test_numeric_height_is_preserved(self, height):
        from parsers.common import build_attributes
        assert build_attributes({"HEIGHT": height}) == {"height": height}


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

    def test_na_parts_are_not_assembled(self):
        """Olimex's NA(...) is "not assembled" with the value the part would have; it was read as a
        fitted part (NA(47uF C0805) became a 47uF cap). It is a do-not-fit marker like DNP."""
        from parse_boards import is_junk_value
        for raw, ref in [("NA(47uF C0805)", "C1"), ("NA(10k R0402)", "R1"), ("NA(RCLAMP0524P(SLP2510P8))", "U1"),
                         ("NA(600R UPZ2012E-601-2R0TF)", "L5"), ("NA(47uF/6.3V/20%/X5R/C0805)", "C9")]:
            assert normalize_value(raw, ref) == "NA"
            assert is_junk_value(normalize_value(raw, ref))
        assert normalize_value("NAU7802", "U1") == "NAU7802"

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


class TestInductorValuesAreNotInvented:
    """Values checked against the boards' source files and the makers' part tables."""

    @pytest.mark.parametrize("raw", ["10", "0", "2.5"])
    def test_a_bare_number_has_no_unit_to_assume(self, raw):
        assert normalize_value(raw, "L1") == raw

    @pytest.mark.parametrize("raw", ["2.0pF", "0.5pF", "1uF"])
    def test_a_capacitance_on_an_l_ref_stays_a_capacitance(self, raw):
        assert normalize_value(raw, "L3") == raw

    @pytest.mark.parametrize("raw,expected", [("0 ohm", "0ohm"), ("0ohm", "0ohm"), ("600 OHM", "600ohm")])
    def test_ohms_on_an_l_ref_with_or_without_a_space(self, raw, expected):
        assert normalize_value(raw, "L2") == expected

    @pytest.mark.parametrize("raw", ["100 ohm, 4 A", "220 ohm, 3 A"])  # Duet 3 6HC L2/L4/L13, Duet 2 WiFi L3
    def test_a_bead_keeps_its_current_rating(self, raw):
        assert normalize_value(raw, "L13") == raw

    @pytest.mark.parametrize("raw,expected", [
        ("XFL4020-222MEC", "2.2uH"), ("XEL4030-102MEC", "1uH"), ("MSS1210-153ME", "15uH"), ("MSS1210-104KE", "100uH"),
    ])
    def test_coilcraft_codes_are_in_nanohenries(self, raw, expected):
        assert normalize_value(raw, "L1") == expected

    def test_bourns_code_keeps_the_microhenry_scale(self):
        assert normalize_value("SDR0503-103JL", "L1") == "10mH"

    @pytest.mark.parametrize("raw,expected", [("10uH", "10uH"), ("4.7u", "4.7uH"), ("100nH", "100nH"), ("0nH", "0H")])
    def test_values_with_a_unit_still_normalize(self, raw, expected):
        assert normalize_value(raw, "L1") == expected


class TestAuditedBoardValues:
    @pytest.mark.parametrize("raw,ref,expected", [
        ("DR73-100-R", "L1", "10uH"),  # EHM: suffix must reach the MPN decoder
        ("DR73-220-R", "L2", "22uH"),
        (r"1\nF", "C16", "1nF"),  # SimpleFMCWRadar: literal backslash + n
        (r"1\nF", "C24", "1nF"),
        ("LQP15MN1N2B02D", "L1", "1.2nH"),
        ("LQW15AN6N8G00D", "L2", "6.8nH"),
        ("LQW15AN47NJ00D", "L9", "47nH"),
        ("LQW15AN3N0B00", "L8", "3nH"),  # no packaging suffix
        ("BLM18PG221SN1D", "FB1", "220ohm"),
        ("BLM15PD121SN1D", "FB1", "120ohm"),
        ("BLM18HE152SN1", "L1", "1.5kohm"),
        ("UWT1H220MCL", "C89", "22uF"),
        ("UWT1C100MCL1GB", "C1", "10uF"),
        ("0.1", "C1", "0.1"),  # ANAVI Gardening / Infrared, 0603
        ("4.7", "C2", "4.7"),
    ])
    def test_exact_source_values(self, raw, ref, expected):
        assert normalize_value(raw, ref) == expected

    @pytest.mark.parametrize("raw,ref,expected", [
        ("1F", "C5", "1000000uF"),  # Artemis supercap, explicit farads
        ("1000000uF", "C6", "1000000uF"),
        ("0.1u", "C1", "100nF"),
        ("4.7uF", "C2", "4.7uF"),
        ("10kR", "R1", "10kohm"),
        ("600R", "L1", "600ohm"),
        ("NA(600R UPZ2012E-601-2R0TF)", "L5", "NA"),  # not assembled
        ("4u7-TMK212AB7475KG-T", "C1", "4.7uF"),
        (r"100n\nF", "C1", "100nF"),
        (r"10k\n", "R1", "10kohm"),
        ("LQW15AN6N8G00D", "U1", "LQW15AN6N8G00D"),
    ])
    def test_controls(self, raw, ref, expected):
        assert normalize_value(raw, ref) == expected

    @pytest.mark.parametrize("raw,prefix", [
        ("LQW15AN", "L"), ("LQP15MNXYZB02D", "L"),
        ("LQW15AN6N8G00D-extra", "L"), ("LQW15AN6N8G00D", "C"),
        ("BLM18PGXYZSN1D", "FB"), ("BLM18PG221SN1D-extra", "L"),
        ("BLM18PG221SN1D", "R"), ("UWT1Z220MCL", "C"),
        ("UWT1HXYZMCL", "C"), ("UWT1H220MCL", "L"),
    ])
    def test_unknown_or_wrong_family_codes_pass_through(self, raw, prefix):
        assert _decode_mpn_value(raw, prefix) is None
        assert normalize_value(raw, f"{prefix}1") == raw

    def test_artemis_source_supercaps_keep_explicit_farads(self):
        raw, specs = extract_inline_specs("1F 2.7V")
        assert specs == {"voltage": "2.7V"}
        assert normalize_value(raw, "C5") == "1000000uF"


class TestFindSchematicRoot:
    def test_explicit_root_wins_over_subsheets(self, tmp_path):
        parent = tmp_path / "hardware/mark-two-lan"
        parent.mkdir(parents=True)
        (parent / "pmic.kicad_sch").touch()
        root = parent / "armory.kicad_sch"
        root.touch()
        info = {"format": "kicad7", "schematic_path": "hardware/mark-two-lan/armory.kicad_sch"}
        assert find_schematic(tmp_path, info) == root

    def test_registry_records_usb_armory_root(self):
        assert parse_boards_md()["usb-armory-mk-ii"]["schematic_path"] == "hardware/mark-two-lan/armory.kicad_sch"

    def test_wildcard_fallback_still_finds_schematic(self, tmp_path):
        root = tmp_path / "board.kicad_sch"
        root.touch()
        assert find_schematic(tmp_path, {"format": "kicad7", "schematic_path": "*.kicad_sch"}) == root

    def test_missing_registered_file_fails_even_with_one_candidate(self, tmp_path):
        """The lone file left may be a subsheet (power.kicad_sch), not a renamed root."""
        (tmp_path / "power.kicad_sch").touch()
        with pytest.raises(FileNotFoundError, match="candidates: power.kicad_sch. Register the intended root"):
            find_schematic(tmp_path, {"format": "kicad7", "schematic_path": "main.kicad_sch"})

    @pytest.mark.parametrize("registered", ["missing.kicad_sch", "*.kicad_sch"])
    def test_missing_root_does_not_pick_an_arbitrary_subsheet(self, tmp_path, registered):
        (tmp_path / "IO-expand.kicad_sch").touch()
        (tmp_path / "REV10a.kicad_sch").touch()
        with pytest.raises(FileNotFoundError, match="candidates: .*Register the intended root"):
            find_schematic(tmp_path, {"format": "kicad7", "schematic_path": registered})

    def test_no_schematic_fails_loudly(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Schematic not found"):
            find_schematic(tmp_path, {"format": "kicad7", "schematic_path": "missing.kicad_sch"})


class TestExplicitLayout:
    @pytest.mark.parametrize("fmt", ["kicad9", "kicad_legacy"])
    def test_associated_layout_supplies_only_own_connectivity_and_pins(self, tmp_path, monkeypatch, fmt):
        import parse_boards as parser
        import yaml
        from parsers import kicad, kicad_legacy

        repo = tmp_path / "org--repo"
        (repo / "SCH").mkdir(parents=True)
        (repo / "PCB").mkdir()
        schematic = repo / "SCH/child.kicad_sch"
        schematic.touch()
        # A sibling is deliberately present: an explicit association must take priority.
        schematic.with_suffix(".kicad_pcb").write_text("(kicad_pcb)")
        layout = repo / "PCB/parent.kicad_pcb"
        layout.write_text('''(kicad_pcb
          (gr_rect (start 0 0) (end 100 100) (layer "Edge.Cuts"))
          (footprint "SOIC-8" (property "Reference" "U1") (property "MPN" "wrong-parent-part")
            (at 10 10)
            (pad "1" smd (pinfunction "OUT") (pintype "output") (net 1 "SIGNAL"))
            (pad "2" smd (pinfunction "NC") (pintype "no_connect"))
            (pad "3" smd (pinfunction "PARENT") (pintype "input") (net 2 "PARENT_ONLY")))
          (footprint "R_0603" (property "Reference" "R1") (at 20 20)
            (pad "1" smd (pintype "passive") (net 1 "SIGNAL"))
            (pad "2" smd (pintype "passive") (net 3 "SINGLE")))
          (footprint "SOIC-8" (property "Reference" "U99") (at 30 30)
            (pad "1" smd (net 1 "SIGNAL")) (pad "2" smd (net 2 "PARENT_ONLY"))))''')
        monkeypatch.setattr(parser, "clone_repo", lambda *a, **kw: repo)
        monkeypatch.setattr(parser, "CACHE_DIR", tmp_path)
        monkeypatch.setattr(parser, "OUTPUT_DIR", tmp_path / "output")
        source_parser = kicad_legacy if fmt == "kicad_legacy" else kicad
        monkeypatch.setattr(source_parser, "parse_schematic", lambda *a, **kw: ([
            parser.Component("U1", "LMV321", "SOIC-8"),
            parser.Component("R1", "10kohm", "0603"),
        ], []))
        info = {"name": "Child", "org": "org", "repo": "org/repo", "format": fmt,
                "schematic_path": "SCH/child.kicad_sch", "pcb_path": "PCB/parent.kicad_pcb"}
        board = parser.process_board("child", info)
        assert {c.ref for c in board.components} == {"U1", "R1"}
        assert [(n.name, n.pins) for n in board.nets] == [("SIGNAL", ["R1.1", "U1.OUT"])]
        assert not board.positions and board.outline is None and not board.copper_pours
        assert "mpn" not in board.components[0].attributes
        assert board.components[0].pin_count == 3
        assert board.components[0].nc_pins == {"NC": "2"}  # PARENT is wired, though its net is filtered
        output = tmp_path / "output/child.yaml"
        before = yaml.safe_load(output.read_text())
        for component in before["components"]:
            component.pop("pin_count", None)
            component.pop("nc_pins", None)
        output.write_text(yaml.safe_dump(before, sort_keys=False))
        assert parser.merge_pin_info("child", info) == (2, [])
        restored = yaml.safe_load(output.read_text())["components"]
        assert next(c for c in restored if c["ref"] == "U1")["nc_pins"] == {"NC": "2"}

    def test_missing_explicit_layout_does_not_fall_back(self, tmp_path):
        from parse_boards import find_pcb

        schematic = tmp_path / "board.kicad_sch"
        schematic.with_suffix(".kicad_pcb").touch()
        with pytest.raises(FileNotFoundError, match="Registered PCB not found"):
            find_pcb(tmp_path, {"pcb_path": "missing.kicad_pcb"}, schematic)


class TestReferenceBoardMetadataAndFerrites:
    @pytest.mark.parametrize("raw,ref,expected", [
        ("7427934", "FB1", "7427934"),  # Internal USB Hub: source Value and footprint
        (" 7427934 ", "FB2", "7427934"),
        ("600", "FB1", "600ohm"),
        ("600R", "FB1", "600ohm"),
        ("BLM18PG221SN1D", "FB1", "220ohm"),
        ("7427934", "R1", "7.42793Mohm"),
        # Known decoder hazards are deliberately outside this fix.
        ("SRP05203R3K", "L1", "5.2033mH"),
        ("XAL6030-182MEC", "L1", "1.8mH"),
        ("BDCD002520121R0MS1", "L1", "2520.12mH"),
        ("ECS-MPI4040R2-100-R", "L1", "4.0402mH"),
    ])
    def test_ferrite_mpn_and_unchanged_controls(self, raw, ref, expected):
        assert normalize_value(raw, ref) == expected

    @pytest.mark.parametrize("slug", ["adsbee-rf-board", "prntrboardv2", "usb-armory-mk-ii"])
    def test_key_ic_overrides_agree_with_published_boards(self, slug):
        import yaml
        from board_overrides import BOARD_META_OVERRIDES

        board_path = Path(__file__).resolve().parent.parent / "data" / "boards" / f"{slug}.yaml"
        board = yaml.safe_load(board_path.read_text())
        assert BOARD_META_OVERRIDES[slug]["key_ics"] == board["key_ics"]


class TestEagleTechnologyAttributes:
    def _parse(self, tmp_path, technology='', attributes='', value='PLACED-PART', ref='IC1'):
        from parsers.eagle import parse_schematic

        sch = tmp_path / 'technology.sch'
        sch.write_text(f'''<eagle><drawing><schematic><libraries>
          <library name="test"><devicesets><deviceset name="IC-50V-5%">
            <description>Deviceset default description</description>
            <devices><device name="S" package="SO08"><technologies>
              <technology name=""><attribute name="MPN" value="DEFAULT-PART"/></technology>
              <technology name="SELECTED">
                <attribute name="MPN" value="SELECTED-PART"/>
                <attribute name="VOLTAGERATING" value="25V"/>
                <attribute name="TOLERANCE" value="10%"/>
                <attribute name="DESCRIPTION" value="Selected technology description"/>
              </technology>
              <technology name="OTHER">
                <attribute name="MPN" value="OTHER-PART"/>
                <attribute name="VOLTAGERATING" value="100V"/>
                <attribute name="TOLERANCE" value="20%"/>
                <attribute name="DESCRIPTION" value="Other technology description"/>
                <attribute name="MANUFACTURER" value="Other manufacturer"/>
              </technology>
            </technologies></device></devices>
          </deviceset></devicesets></library></libraries><parts>
          <part name="{ref}" library="test" deviceset="IC-50V-5%" device="S"
                {technology} value="{value}">{attributes}</part>
          </parts></schematic></drawing></eagle>''')
        return parse_schematic(sch)[0][0]

    def test_only_selected_technology_is_inherited(self, tmp_path):
        part = self._parse(tmp_path, 'technology="SELECTED"')
        assert part.value == 'PLACED-PART'
        assert part.attributes == {
            'mpn': 'SELECTED-PART', 'voltage': '25V', 'tolerance': '10%',
            'description': 'Selected technology description',
        }

    @pytest.mark.parametrize('technology', ['', 'technology=""'])
    def test_unnamed_technology_is_selected_by_default(self, tmp_path, technology):
        part = self._parse(tmp_path, technology)
        assert part.attributes == {
            'mpn': 'DEFAULT-PART', 'voltage': '50V', 'tolerance': '5%',
            'description': 'Deviceset default description',
        }

    def test_missing_technology_does_not_inherit_another(self, tmp_path):
        part = self._parse(tmp_path, 'technology="MISSING"')
        assert part.attributes == {
            'voltage': '50V', 'tolerance': '5%',
            'description': 'Deviceset default description',
        }

    def test_placed_inline_specs_override_library_defaults(self, tmp_path):
        part = self._parse(tmp_path, 'technology="SELECTED"', value='1uF 60V', ref='C1')
        assert part.value == '1uF'
        assert part.attributes['voltage'] == '60V'
        assert part.attributes['tolerance'] == '10%'

    def test_instance_attribute_overrides_placed_inline_spec(self, tmp_path):
        part = self._parse(tmp_path, 'technology="SELECTED"',
                           '<attribute name="VOLTAGE" value="16V"/>',
                           value='1uF 60V', ref='C1')
        assert part.value == '1uF'
        assert part.attributes['voltage'] == '16V'

    def test_instance_attributes_override_selected_technology_and_aliases(self, tmp_path):
        part = self._parse(tmp_path, 'technology="SELECTED"', '''
            <attribute name="MANUFACTURER_PART_NUMBER" value="INSTANCE-PART"/>
            <attribute name="VOLTAGE" value="16V"/>
            <attribute name="TOLERANCE" value="1%"/>
            <attribute name="DESCRIPTION" value="Instance description"/>
            <attribute name="VALUE" value="OTHER-LIBRARY-VALUE"/>
        ''')
        assert part.value == 'PLACED-PART'
        assert part.attributes == {
            'mpn': 'INSTANCE-PART', 'voltage': '16V', 'tolerance': '1%',
            'description': 'Instance description',
        }


def test_board_override_can_remove_a_conflicting_inherited_attribute(monkeypatch):
    import parse_boards as parser

    component = parser.Component(ref='IC1', value='PLACED-PART', footprint='SOIC-8',
                                 attributes={'mpn': 'WRONG-PART', 'voltage': '16V'})
    monkeypatch.setattr(parser, '_BOARD_OVERRIDES', {
        ('fixture', 'IC1'): {'mpn': None, 'voltage': None},
    })
    parser._apply_overrides('fixture', [component])
    assert component.value == 'PLACED-PART'
    assert component.attributes == {}


class TestSourceAttributeAliases:
    @pytest.mark.parametrize('destination,aliases', __import__('parsers.common', fromlist=['_ATTRIBUTE_ALIASES'])._ATTRIBUTE_ALIASES.items())
    def test_surveyed_aliases(self, destination, aliases):
        from parsers.common import build_attributes
        for alias in aliases:
            assert build_attributes({alias: 'SOURCE-PART-123'}) == {destination: 'SOURCE-PART-123'}, alias
            assert build_attributes({alias.lower(): 'SOURCE-PART-123'}) == {destination: 'SOURCE-PART-123'}, alias

    @pytest.mark.parametrize('explicit', ['MPN', 'MANUFACTURER_PART_NUMBER', 'Manufacturer Part Number', 'MANF#', 'MFG#'])
    @pytest.mark.parametrize('reverse', [False, True])
    def test_explicit_mpn_beats_generic_pn(self, explicit, reverse):
        from parsers.common import build_attributes
        pairs = [('PN', 'INTERNAL-123'), (explicit, 'MAKER-456')]
        assert build_attributes(dict(reversed(pairs) if reverse else pairs))['mpn'] == 'MAKER-456'

    @pytest.mark.parametrize('reverse', [False, True])
    def test_seeed_internal_code_is_not_an_mpn(self, reverse):
        from parsers.common import build_attributes
        pairs = [('PN', '302010271'), ('Manufacturer Part Number', 'CC0201KRX5R6BB104')]
        assert build_attributes(dict(reversed(pairs) if reverse else pairs)) == {
            'mpn': 'CC0201KRX5R6BB104', 'prod_id': '302010271',
        }

    def test_maker_and_part_conventions_are_distinct(self):
        from parsers.common import build_attributes
        assert build_attributes({'MANF#': 'C1005X6S1E104M050BB', 'MANF': 'TDK Corporation',
                                 'DIGIKEY#': '445-7361-1-ND'}) == {
            'mpn': 'C1005X6S1E104M050BB', 'manufacturer': 'TDK Corporation', 'digikey': '445-7361-1-ND',
        }
        assert build_attributes({'MFR': 'Yageo', 'MFG': 'RC0603FR-07100KL'}) == {
            'manufacturer': 'Yageo', 'mpn': 'RC0603FR-07100KL',
        }
        assert build_attributes({'Mfg': 'Yageo'}) == {'manufacturer': 'Yageo'}
        assert build_attributes({'Supplier': 'Mouser'}) == {}

    @pytest.mark.parametrize('key,supplier_key,supplier,destination', [
        ('Supplier P/N', 'Supplier', 'LCSC', 'lcsc'),
        ('Supplier Part', 'Supplier', 'Mouser', 'mouser'),
        ('Supplier PN', 'Supplier', 'Digi-Key', 'digikey'),
        ('Design Order Code', 'Design Supplier', 'TME', 'tme'),
        ('DIST_ID', 'DIST', 'DIGIKEY', 'digikey'),
    ])
    def test_supplier_numbers_need_supplier_context(self, key, supplier_key, supplier, destination):
        from parsers.common import build_attributes
        assert build_attributes({key: 'ORDER-123', supplier_key: supplier})[destination] == 'ORDER-123'

    @pytest.mark.parametrize('placeholder', ['N/A', 'unknown', 'None', '~', 'template_mpn', '${MPN}'])
    def test_placeholder_does_not_mask_real_alias(self, placeholder):
        from parsers.common import build_attributes
        assert build_attributes({'MPN': placeholder, 'MANF#': 'REAL-123'}) == {'mpn': 'REAL-123'}


class TestElectricalValueProperties:
    @pytest.mark.parametrize('ref,mpn,key,electrical,expected', [
        ('C1', 'CC0402KRX5R7BB104', 'id', '0.1uF', '100nF'),
        ('C15', 'CC0402KRX5R7BB105', 'id', '1uF', '1uF'),
        ('R1', 'RC0402JR-0710KL', 'id', '10K', '10kohm'),
        ('R30', 'RL1206JR-070R51L', 'id', '510m', '510mohm'),
        ('L2', 'FCUL0624-H-R22M=P3', 'id', '220nH', '220nH'),
        ('R2', 'RC0402FR-074K7L', 'Val', '4k7', '4.7kohm'),
        ('R4', 'RC0402FR-0710KL', 'Resistance', '10K', '10kohm'),
        ('L1', 'SRN3015-100M', 'Inductance', '10uH', '10uH'),
        ('C2', 'CAP-123', 'Capacitance', '100nF', '100nF'),
        ('R3', 'RES-123', 'RValue', '3mΩ', '3mohm'),
        ('C3', 'CAP-456', 'CatV', '370nF', '370nF'),
    ])
    def test_kicad_uses_electrical_property_and_retains_mpn(self, tmp_path, ref, mpn, key, electrical, expected):
        from parsers.kicad import parse_schematic
        sch = tmp_path / 'source.kicad_sch'
        sch.write_text(f'''(kicad_sch (uuid "root")
          (symbol (lib_id "Device:Part") (uuid "part")
            (property "Reference" "{ref}") (property "Value" "{mpn}")
            (property "Footprint" "Device:0402") (property "{key}" "{electrical}"))))''')
        parts, _ = parse_schematic(sch)
        assert parts[0].value == expected
        assert parts[0].attributes['mpn'] == mpn

    @pytest.mark.parametrize('value,ref,properties', [
        ('100nF', 'C1', {'id': '1uF'}),
        ('RC0402JR-0710KL', 'R1', {'id': 'inventory-123'}),
        ('TPS563207SDRLR', 'U1', {'id': '5V'}),
        ('R_Small', 'R1', {'id': '10K'}),
        ('RC0402JR-0710KL', 'R1', {'VALUE': '100K'}),
    ])
    def test_generic_ids_and_placed_values_are_preserved(self, value, ref, properties):
        from parsers.common import value_from_properties
        attrs = {}
        assert value_from_properties(value, ref, properties, attrs) == value
        assert attrs == {}

    def test_explicit_mpn_has_priority_over_value_field(self):
        from parsers.common import value_from_properties
        attrs = {'mpn': 'EXPLICIT-123'}
        assert value_from_properties('RC0402JR-0710KL', 'R1', {'id': '10K'}, attrs) == '10K'
        assert attrs['mpn'] == 'EXPLICIT-123'

    @pytest.mark.parametrize('ref', ['R?1', 'R?2', 'U?1'])
    def test_unannotated_refs_are_excluded_and_reported(self, tmp_path, caplog, ref):
        from parsers.common import is_junk_ref
        from parsers.kicad import parse_schematic
        assert is_junk_ref(ref)
        sch = tmp_path / 'unannotated.kicad_sch'
        sch.write_text(f'''(kicad_sch (uuid "root")
          (symbol (uuid "part") (property "Reference" "{ref}")
            (property "Value" "LM317DCYR") (property "Footprint" "Device:SOT-223"))))''')
        assert parse_schematic(sch)[0] == []
        assert f'Excluding unannotated reference {ref}' in caplog.text


@pytest.mark.parametrize('raw,expected', [
    ({'Rating': '6.3V/20%'}, {'voltage': '6.3V', 'tolerance': '20%'}),
    # Unit-labelled current and power are kept too (Duet L2's Rating "2A" was dropped)
    ({'Rating': '1.7A/20%/128mOhm'}, {'tolerance': '20%', 'current': '1.7A'}),
    ({'Power Rating': '5%'}, {'tolerance': '5%'}),
    ({'Rating': '100mW'}, {'power': '100mW'}),
    ({'Rating': '50V', 'Voltage': '16V'}, {'voltage': '16V'}),
    ({'Voltage Rating': '10V,X5R'}, {'voltage': '10V'}),
])
def test_mixed_rating_properties_only_supply_labelled_specs(raw, expected):
    from parsers.common import build_attributes
    assert build_attributes(raw) == expected


def test_uppercase_eagle_supplier_is_a_maker_and_numbered_supplier_is_separate():
    from parsers.common import build_attributes
    assert build_attributes({'SUPPLIER': 'Texas Instruments', 'MPN': 'TPS1234'}) == {
        'manufacturer': 'Texas Instruments', 'mpn': 'TPS1234',
    }
    assert build_attributes({'Supplier PN': '490-10410-2-ND'}) == {'digikey': '490-10410-2-ND'}
    assert build_attributes({'Supplier Part': 'C12345'}) == {'lcsc': 'C12345'}
    assert build_attributes({'Supplier Part': 'ORDER-123'}) == {'partno': 'ORDER-123'}


@pytest.mark.parametrize('slug,schema', __import__('board_overrides').BOARD_PROPERTY_ALIASES.items())
def test_source_specific_importer_fields(slug, schema):
    from parsers.common import build_attributes
    for ref, aliases in schema.items():
        for source, target in aliases.items():
            if target == 'PART_OR_SPECS':
                assert build_attributes({source: 'BAT54JFILM'}, schema, ref)['mpn'] == 'BAT54JFILM'
                assert build_attributes({source: '50V X7R'}, schema, ref)['description'] == '50V X7R'
            elif target == 'Rating':
                assert build_attributes({source: '16V X5R'}, schema, ref)['voltage'] == '16V'
            elif target != 'Supplier':
                expected = {'MPN': 'mpn', 'Manufacturer': 'manufacturer', 'Description': 'description',
                            'PROD_ID': 'prod_id', 'LCSC': 'lcsc', 'DigiKey': 'digikey',
                            'Supplier Part': 'partno'}[target]
                assert build_attributes({source: 'SOURCE-123'}, schema, ref)[expected] == 'SOURCE-123'


def test_source_specific_fields_never_override_named_properties():
    from parsers.common import build_attributes
    from board_overrides import BOARD_PROPERTY_ALIASES
    assert build_attributes({'Field2': 'OLD-123', 'MPN': 'EXPLICIT-456'},
                            BOARD_PROPERTY_ALIASES['ubertooth-one'], 'R1')['mpn'] == 'EXPLICIT-456'
    assert build_attributes({'Field4': 'nf'}, BOARD_PROPERTY_ALIASES['rpi-cm4-io-board'], 'R1') == {}
    assert build_attributes({'Field1': 'Unknown'}) == {}


class TestRun8Connectivity:
    @pytest.mark.parametrize('fmt', ['kicad_legacy', 'kicad9'])
    def test_clone_fetches_legacy_libraries_layouts_and_project_tables(self, tmp_path, monkeypatch, fmt):
        import subprocess
        import parse_boards
        commands = []

        def run(command, **kwargs):
            commands.append(command)
            return subprocess.CompletedProcess(command, 0, stdout='', stderr='')

        monkeypatch.setattr(parse_boards.subprocess, 'run', run)
        parse_boards.clone_repo('org/legacy', fmt, tmp_path)
        sparse = next(c for c in commands if c[:3] == ['git', 'sparse-checkout', 'set'])
        assert set(sparse[4:]) == {
            '*.kicad_sch', '*.kicad_pcb', '*.kicad_pro', '*.sch', '*.lib', '*.dcm',
            '*.net', '*.brd', '*.pro', 'sym-lib-table', 'fp-lib-table',
        }

    def test_legacy_layout_uses_schematic_paths_and_counts_excluded_neighbors(self, tmp_path):
        from parsers.kicad_legacy import read_layout
        from parse_boards import find_pcb
        pcb = tmp_path / 'board.brd'
        pcb.write_text('''PCBNEW-BOARD Version 1
$MODULE X
AR /AAAA
T0 0 0 0 0 0 0 N V 21 N"OLD"
$PAD
Sh "1" R 0 0 0 0 0
Ne 1 "SIGNAL"
$EndPAD
$PAD
Sh "2" R 0 0 0 0 0
Ne 2 "EXCLUDED"
$EndPAD
$PAD
Sh "3" R 0 0 0 0 0
Ne 0 ""
$EndPAD
$PAD
Sh "" R 0 0 0 0 0
Ne 0 ""
$EndPAD
$EndMODULE
$MODULE X
T0 0 0 0 0 0 0 N V 21 N"R1"
$PAD
Sh "1" R 0 0 0 0 0
Ne 1 "SIGNAL"
$EndPAD
$EndMODULE
$MODULE X
T0 0 0 0 0 0 0 N V 21 N"TP1"
$PAD
Sh "1" R 0 0 0 0 0
Ne 2 "EXCLUDED"
$EndPAD
$EndMODULE
''')
        nets, pins, wired = read_layout(pcb, {'U1', 'R1'}, {'/AAAA': 'U1'})
        assert [(n.name, n.pins) for n in nets] == [('SIGNAL', ['R1.1', 'U1.1'])]
        assert pins['U1'] == {'1': '1', '2': '2', '3': '3'}
        assert wired['U1'] == {'1', '2'}
        assert find_pcb(tmp_path, {'format': 'kicad_legacy'}, pcb.with_suffix('.sch')) == pcb
        pcb.with_suffix('.kicad_pcb').touch()
        assert find_pcb(tmp_path, {'format': 'kicad_legacy'}, pcb.with_suffix('.sch')) == pcb.with_suffix('.kicad_pcb')

    def test_eagle_schematic_without_layout_merges_sheets_and_uses_library_urn(self, tmp_path):
        from parsers.eagle import parse_schematic, extract_part_pins
        sch = tmp_path / 'example.sch'
        sch.write_text('''<eagle><drawing><schematic><libraries>
          <library name="same" urn="urn:first"><symbols><symbol name="S">
            <pin name="A"/><pin name="B"/></symbol></symbols><devicesets>
            <deviceset name="IC"><gates><gate name="G" symbol="S"/></gates><devices>
              <device name="" package="SO08"><connects>
                <connect gate="G" pin="A" pad="1"/><connect gate="G" pin="B" pad="2"/>
              </connects></device></devices></deviceset></devicesets></library>
          <library name="same" urn="urn:second"><devicesets>
            <deviceset name="VIRTUAL"><devices><device name=""/></devices></deviceset>
          </devicesets></library></libraries><parts>
            <part name="U1" library="same" library_urn="urn:first" deviceset="IC" device=""/>
            <part name="U2" library="same" library_urn="urn:first" deviceset="IC" device=""/>
            <part name="P1" library="same" library_urn="urn:second" deviceset="VIRTUAL" device=""/>
          </parts><sheets><sheet><nets><net name="BUS[0]" class="0"><segment>
            <pinref part="U1" gate="G" pin="A"/><pinref part="P1" gate="G" pin="1"/>
          </segment></net></nets></sheet><sheet><nets><net name="BUS[0]" class="0"><segment>
            <pinref part="U2" gate="G" pin="B"/>
          </segment></net></nets></sheet></sheets></schematic></drawing></eagle>''')
        components, nets = parse_schematic(sch)
        assert {c.ref for c in components} == {'U1', 'U2'}
        assert [(n.name, n.pins) for n in nets] == [('BUS[0]', ['U1.A', 'U2.B'])]
        pins, wired = extract_part_pins(sch, {'U1', 'U2'})
        assert pins == {'U1': {'A': '1', 'B': '2'}, 'U2': {'A': '1', 'B': '2'}}
        assert wired == {'U1': {'A'}, 'U2': {'B'}}
        assert not sch.with_suffix('.brd').exists()

    def test_native_xml_keeps_duplicate_pin_names_and_excluded_neighbors(self, tmp_path):
        from parsers.kicad_netlist import read_netlist
        netlist = tmp_path / 'fixture.xml'
        netlist.write_text('''<export><components>
          <comp ref="U1"><libsource lib="test" part="IC"/></comp>
          </components><libparts><libpart lib="test" part="IC"><pins>
            <pin num="1" name="GND"/><pin num="2" name="GND"/><pin num="3" name="OUT"/>
          </pins></libpart></libparts><nets>
            <net name="GND"><node ref="U1" pin="1"/><node ref="U1" pin="2"/></net>
            <net name="OUT"><node ref="U1" pin="3"/><node ref="TP1" pin="1"/></net>
            <net name="unconnected"><node ref="U1" pin="3"/></net>
          </nets></export>''')
        nets, pins, connected = read_netlist(netlist, {'U1'})
        assert [(n.name, n.pins) for n in nets] == [('GND', ['U1.GND@1', 'U1.GND@2'])]
        assert pins == {'U1': {'GND@1': '1', 'GND@2': '2', 'OUT': '3'}}
        assert connected == {'U1': {'GND@1', 'GND@2', 'OUT'}}
        with pytest.raises(ValueError, match='missing components'):
            read_netlist(netlist, {'U1', 'U2'})

    def test_legacy_native_export_preserves_mirrors_and_hierarchy_without_editing_sources(self, tmp_path):
        import shutil
        from parsers.kicad_netlist import export_schematic
        if not shutil.which('kicad-cli'):
            pytest.skip('Optional offline schematic exporter is not installed')
        cache = tmp_path / 'root-cache.lib'
        cache.write_text('''EESchema-LIBRARY Version 2.4
DEF Device_R R 0 0 N Y 1 F N
X ~ 1 0 150 0 D 50 50 1 1 P
X ~ 2 0 -150 0 U 50 50 1 1 P
ENDDEF
DEF Device_R3 R 0 0 N Y 1 F N
X ~ 1 0 150 0 D 50 50 1 1 P
X ~ 2 0 -150 0 U 50 50 1 1 P
X ~ 3 0 0 0 U 50 50 1 1 P
ENDDEF
''')
        root = tmp_path / 'root.sch'
        root.write_text('''EESchema Schematic File Version 4
$Comp
L Device:R R1
U 1 1 AAAA
P 1000 1000
F 0 "R1" H 0 0 50 0000 C CNN
F 1 "10k" H 0 0 50 0000 C CNN
F 2 "R_0603" H 0 0 50 0000 C CNN
 1 1000 1000
 0 1 1 0
$EndComp
Wire Wire Line
 1150 1000 2000 1000
NoConn ~ 850 1000
$Sheet
S 2000 500 1000 1000
U BBBB
F0 "Child" 50
F1 "child.sch" 50
F2 "SIGNAL" B L 2000 1000 50
$EndSheet
$EndSCHEMATC
''')
        child = tmp_path / 'child.sch'
        child.write_text('''EESchema Schematic File Version 4
$Comp
L Device:R3 R2
U 1 1 CCCC
P 1000 1000
F 0 "R2" H 0 0 50 0000 C CNN
F 1 "10k" H 0 0 50 0000 C CNN
F 2 "R_0603" H 0 0 50 0000 C CNN
 1 1000 1000
 0 -1 -1 0
$EndComp
Text HLabel 850 1000 0    50   BiDi ~ 0
SIGNAL
NoConn ~ 1150 1000
NoConn ~ 1000 1000
$EndSCHEMATC
''')
        sources = {p: p.read_bytes() for p in (root, child, cache)}
        nets, pins, wired = export_schematic(root, {'R1', 'R2'})
        assert [(n.name, n.pins) for n in nets] == [('/Child/SIGNAL', ['R1.1', 'R2.1'])]
        assert pins == {'R1': {'1': '1', '2': '2'}, 'R2': {'1': '1', '2': '2', '3': '3'}}
        assert wired == {'R1': {'1'}, 'R2': {'1'}}
        assert all(p.read_bytes() == before for p, before in sources.items())
        cache.write_text(cache.read_text().replace('DEF Device_R', 'DEF Missing'))
        with pytest.raises(ValueError, match='no definition for Device:R'):
            export_schematic(root, {'R1', 'R2'})

    def test_native_export_connects_rotated_symbol_and_omits_no_connects(self, tmp_path):
        import shutil
        from parsers.kicad_netlist import export_schematic
        if not shutil.which('kicad-cli'):
            pytest.skip('Optional offline schematic exporter is not installed')
        sch = tmp_path / 'fixture.kicad_sch'
        sch.write_text('''(kicad_sch (version 20230121) (generator eeschema)
          (uuid 00000000-0000-0000-0000-000000000001) (paper "A4")
          (lib_symbols (symbol "Test:R" (pin_names (offset 0)) (in_bom yes) (on_board yes)
            (property "Reference" "R" (at 0 0 0)) (property "Value" "R" (at 0 0 0))
            (symbol "R_1_1"
              (pin passive line (at 0 2.54 270) (length 2.54)
                (name "~" (effects (font (size 1.27 1.27))))
                (number "1" (effects (font (size 1.27 1.27)))))
              (pin passive line (at 0 -2.54 90) (length 2.54)
                (name "~" (effects (font (size 1.27 1.27))))
                (number "2" (effects (font (size 1.27 1.27)))))) ))
          (wire (pts (xy 20 17.46) (xy 27.46 20)) (stroke (width 0) (type default))
            (uuid 00000000-0000-0000-0000-000000000002))
          (label "SIGNAL" (at 20 17.46 0) (effects (font (size 1.27 1.27)))
            (uuid 00000000-0000-0000-0000-000000000003))
          (no_connect (at 20 22.54) (uuid 00000000-0000-0000-0000-000000000004))
          (no_connect (at 32.54 20) (uuid 00000000-0000-0000-0000-000000000005))
          (symbol (lib_id "Test:R") (at 20 20 0) (unit 1) (in_bom yes) (on_board yes)
            (uuid 00000000-0000-0000-0000-000000000006)
            (property "Reference" "R1" (at 20 20 0)) (property "Value" "1k" (at 20 20 0)))
          (symbol (lib_id "Test:R") (at 30 20 90) (unit 1) (in_bom yes) (on_board yes)
            (uuid 00000000-0000-0000-0000-000000000007)
            (property "Reference" "R2" (at 30 20 0)) (property "Value" "1k" (at 30 20 0)))
        )''')
        nets, pins, connected = export_schematic(sch, {'R1', 'R2'})
        assert [(n.name, n.pins) for n in nets] == [('/SIGNAL', ['R1.1', 'R2.1'])]
        assert pins == {'R1': {'1': '1', '2': '2'}, 'R2': {'1': '1', '2': '2'}}
        assert connected == {'R1': {'1'}, 'R2': {'1'}}

    def test_legacy_stable_paths_disambiguate_duplicate_pcb_references(self, tmp_path):
        from parsers.kicad import parse_pcb
        from parsers.kicad_legacy import reference_paths
        sch = tmp_path / 'root.sch'
        sch.write_text('''$Comp
L Connector:X J1
U 1 1 AAAA
F 0 "J1" H 0 0 50 0000 C CNN
$EndComp
$Comp
L Connector:X J2
U 1 1 BBBB
F 0 "J2" H 0 0 50 0000 C CNN
$EndComp
''')
        pcb = tmp_path / 'root.kicad_pcb'
        pcb.write_text('''(kicad_pcb (version 20171130)
          (module X (path /AAAA) (at 0 0) (fp_text reference J)
            (pad 1 thru_hole circle (net 1 "SIGNAL")))
          (module X (path /BBBB) (at 1 0) (fp_text reference J)
            (pad 1 thru_hole circle (net 1 "SIGNAL"))))''')
        positions, _, _, nets, _ = parse_pcb(pcb, {'J1', 'J2'}, reference_paths=reference_paths(sch))
        assert {p.ref for p in positions} == {'J1', 'J2'}
        assert [(n.name, n.pins) for n in nets] == [('SIGNAL', ['J1.1', 'J2.1'])]


def test_legacy_reference_paths_use_each_reused_sheet_annotation(tmp_path):
    from parsers.kicad_legacy import reference_paths
    root = tmp_path / 'root.sch'
    root.write_text('''$Sheet
U AAAA
F1 "child.sch" 50
$EndSheet
$Sheet
U BBBB
F1 "child.sch" 50
$EndSheet
''')
    (tmp_path / 'child.sch').write_text('''$Comp
L Device:R R2
U 1 1 CCCC
AR Path="/AAAA/CCCC" Ref="R1" Part="1"
AR Path="/BBBB/CCCC" Ref="R2" Part="1"
F 0 "R2" H 0 0 50 0000 C CNN
$EndComp
''')
    assert reference_paths(root) == {'/AAAA/CCCC': 'R1', '/BBBB/CCCC': 'R2'}


@pytest.mark.parametrize("raw,ref,expected", [
    ("12101C335K4T2A", "C1", "3.3uF"),
    ("08051C103KAT2A", "C5", "10nF"),
    ("EECS5R5H105", "C112", "1F"),
    ("tc33x-2-103e", "R8", "10kohm"),
    ("tc33x-2-104e", "R4", "100kohm"),
    ("CSR1206-0R002F1", "R5", "2mohm"),
    ("CBC3225T100MR", "L6", "10uH"),
    ("CBW201209U300T", "L201", "30ohm"),
    ("GZ1608D300TF", "L10", "30ohm"),
    # Other part families/references and incomplete identities stay literal.
    ("CBW201209U300T", "C1", "CBW201209U300T"),
    ("08051C103KAT2A", "U1", "08051C103KAT2A"),
    ("GZ1608", "FB1", "GZ1608"),
    ("CBC3225T100MR-extra", "L1", "CBC3225T100MR-extra"),
    ("0.1", "C1", "0.1"),
    ("60R@100MHz", "FB1", "60R@100MHz"),
    ("SN74AHCT125D", "L1", "SN74AHCT125D"),
])
def test_run9_bounded_passive_mpn_values(raw, ref, expected):
    assert normalize_value(raw, ref) == expected


def test_board_meta_overrides_have_no_duplicate_keys():
    """A repeated slug in the dict literal silently replaces the earlier entry."""
    import ast
    from collections import Counter
    src = (Path(__file__).parent.parent / "scripts" / "board_overrides.py").read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") in (
                "BOARD_META_OVERRIDES", "TAG_OVERRIDES", "BOARD_PROPERTY_ALIASES"):
            keys = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
            assert not [k for k, n in Counter(keys).items() if n > 1], node.target.id


# ---------------------------------------------------------------------------
# Reference-board audit (15 boards compared with their sources): parts, pins and specs the parser lost
# ---------------------------------------------------------------------------

def _kicad_sheet(tmp_path, symbols: str, lib_symbols: str = ""):
    sch = tmp_path / "board.kicad_sch"
    sch.write_text(f'''(kicad_sch (version 20230121) (generator eeschema)
      (uuid 00000000-0000-0000-0000-0000000000aa) (paper "A4")
      (lib_symbols {lib_symbols})
      {symbols})''', encoding="utf-8")
    return sch


def _kicad_symbol(ref, value, lib_id, footprint, uuid, extra=""):
    return f'''(symbol (lib_id "{lib_id}") (at 0 0 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)
        (uuid {uuid})
        (property "Reference" "{ref}" (at 0 0 0)) (property "Value" "{value}" (at 0 0 0))
        (property "Footprint" "{footprint}" (at 0 0 0)) {extra})'''


def test_unvalued_fitted_parts_are_named_by_their_symbol(tmp_path):
    """PocketPD's BOOT button SW5 and OpenAirScope's RF-match caps C53/C54 have Value "~" and were
    dropped with their nets; a test-point footprint with no value stays a test point."""
    from parsers.kicad import parse_schematic
    sch = _kicad_sheet(tmp_path, "\n".join([
        _kicad_symbol("SW5", "~", "Centy_Miscellaneous:Button_Side_TS24CA",
                      "Centy_Miscellaneous:Button-SMD_TS24CA", "00000000-0000-0000-0000-000000000001",
                      '(property "LCSC" "C692458" (at 0 0 0))'),
        _kicad_symbol("C53", "~", "Device:C", "Capacitor_SMD:C_0402_1005Metric",
                      "00000000-0000-0000-0000-000000000002"),
        _kicad_symbol("In1", "~", "Connector:Conn_01x01", "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm",
                      "00000000-0000-0000-0000-000000000003"),
    ]))
    parts = {c.ref: c for c in parse_schematic(sch)[0]}
    assert parts["SW5"].value == "Button_Side_TS24CA" and parts["SW5"].attributes["lcsc"] == "C692458"
    assert parts["C53"].value == "C" and parts["C53"].footprint == "0402"
    assert parts["In1"].value == "test point"


def test_board_output_never_silently_drops_an_unvalued_part():
    from parse_boards import BoardData, Component, Net, board_to_dict
    board = BoardData(name="b", slug="b", source="o/r", format="kicad9", components=[
        Component(ref="U1", value="", footprint="QFN-32", attributes={"mpn": "XYZ1234"}),
        Component(ref="SW1", value="", footprint="Button-SMD_TS24CA"),
        Component(ref="R1", value="10kohm", footprint="0402"),
    ], nets=[Net(name="BOOT", pins=["R1.1", "SW1.4"])])
    out = board_to_dict(board)
    assert {c["ref"]: c["value"] for c in out["components"]} == {
        "R1": "10kohm", "SW1": "Button-SMD_TS24CA", "U1": "XYZ1234"}
    assert out["nets"] == [{"name": "BOOT", "pins": ["R1.1", "SW1.4"]}]


def test_eagle_empty_value_reads_as_the_deviceset():
    """Reflow Master's SAMD21 (value="") and SparkFun's named solder jumpers were dropped."""
    from parsers.common import value_or_symbol
    assert value_or_symbol("", "ATSAMD21G") == "ATSAMD21G"
    assert normalize_value(value_or_symbol("", "JUMPER-SMT_2_NC_TRACE"), "MEAS") == "solder jumper (NC)"
    assert normalize_value(value_or_symbol("", "JUMPER-SMT_2_NO"), "VE") == "solder jumper (NO)"
    assert normalize_value("R-EU_0204_7", "R6") == "R"  # a fitted resistor whose source gives no value


@pytest.mark.parametrize("package,footprint", [
    ("PinHeader_2x07_P1.27mm_Vertical", "2X7_P1.27mm"),
    ("PinHeader_1x03_P2.54mm_Vertical", "1X3_P2.54mm"),
    ("PinHeader_2x06_P2.54mm_Horizontal", "2X6_P2.54mm_Horizontal"),
    ("PinHeader_2x05_P1.27mm_Vertical_SMD", "2X5_P1.27mm_SMD"),
    ("PinSocket_1x05_P2.54mm_Vertical", "1X5_P2.54mm"),
    ("Pin_Header_Straight_1x08_Pitch2.54mm", "1X8_P2.54mm"),
    ("Pin_Header_Straight_1x04", "1X4"),  # no pitch in the name: none invented
    ("1X04_1MM_RA", "1X04_P1.00mm_RA"),  # BNO080's Qwiic JST-SH read as a 2.54 mm "1X04"
    ("1X04_NO_SILK", "1X04"),
    ("3.5MM_2X1", "2X1_P3.50mm"),  # Duet's heater terminals
])
def test_connector_footprints_keep_their_pitch(package, footprint):
    assert normalize_footprint(package, "J1") == footprint


@pytest.mark.parametrize("value,package,ref,expected", [
    ("2x7 header", "PinHeader_2x07_P1.27mm_Vertical", "J3", "2x7 1.27mm header"),
    ("1x4 header", "JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal", "J1", "JST SH 4-pin"),
    ("1x3 header", "JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical", "J2", "JST XH 3-pin"),
    ("CONN_02", "TERMBLOCK_1X2-3.5MM", "J1", "1x2 3.50mm screw terminal"),
    ("1x2 screw terminal", "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal", "J2",
     "1x2 5.08mm screw terminal"),
    ("E0 HEAT", "3.5MM_2X1", "J11", "2x1 3.50mm header"),
    ("PWR IN", "PhoenixContact_SPT_2.5_2-H-5.0_1x02_P5.0mm_Horizontal", "J1", "1x2 5.00mm screw terminal"),
    ("1x2 header", "SolderWire-2.5sqmm_1x02_P8.8mm_D2.4mm_OD4.4mm", "J4", "1x2 8.80mm solder wire pads"),
    # A body size is no pin layout: a crystal and a microSD socket became "2x1"/"1x14 header"
    ("DNP", "X2-SMD-3.2X1.5X0.55MM", "X3", "DNP"),
    ("ST-TF-003J", "MICRO-SD9+4P-SMD-16.1X14.5X1.85MM", "J1", "ST-TF-003J"),
    ("M06", "1X06", "JP1", "1x6 header"),  # no pitch named, none added
])
def test_connector_values_keep_pitch_and_series(value, package, ref, expected):
    assert normalize_connector_value(value, package, ref) == expected


def test_sparkfun_i2c_standard_on_a_1mm_package_is_qwiic(tmp_path):
    from parsers.eagle import parse_schematic
    sch = tmp_path / "board.sch"
    sch.write_text('''<?xml version="1.0"?><eagle><drawing><schematic><libraries>
      <library name="SparkX"><packages><package name="1X04_1MM_RA"/><package name="1X04"/></packages>
      <devicesets><deviceset name="I2C_STANDARD"><devices>
        <device name="JS-1MM" package="1X04_1MM_RA"/><device name="SILK" package="1X04"/>
      </devices></deviceset></devicesets></library></libraries>
      <parts><part name="J2" library="SparkX" deviceset="I2C_STANDARD" device="JS-1MM" value="SMD"/>
        <part name="J3" library="SparkX" deviceset="I2C_STANDARD" device="SILK" value="PTH"/></parts>
      <sheets/></schematic></drawing></eagle>''', encoding="utf-8")
    parts = {c.ref: c for c in parse_schematic(sch)[0]}
    assert (parts["J2"].value, parts["J2"].footprint) == ("Qwiic connector", "1X04_P1.00mm_RA")
    assert (parts["J3"].value, parts["J3"].footprint) == ("1x4 header", "1X04")


def test_unrecognised_spec_fields_are_kept():
    """Duet: X2 is CRYSTAL_4PIN with Frequency=12MHz; L2's Rating is 2A, L3's its part number."""
    from parsers.common import build_attributes, value_from_properties
    assert build_attributes({"Rating": "2A"}) == {"current": "2A"}
    assert build_attributes({"Rating": "MPZ2012S221A"}) == {"mpn": "MPZ2012S221A"}
    assert build_attributes({"Rating": "MPZ2012S221A", "MPN": "BLM18"}) == {"mpn": "BLM18"}
    assert build_attributes({"Power": "0.1W", "Temperature": "-55°..+125°", "CLoad": "10pF"}) == {
        "power": "0.1W", "temp_range": "-55°..+125°", "load_capacitance": "10pF"}
    assert build_attributes({"min. Power Rating": "250 mW"}) == {"power": "250mW"}
    attrs: dict = {}
    raw = {"Frequency": "12MHz"}
    assert value_from_properties("CRYSTAL_4PIN", "X2", raw, attrs, symbol="CRYSTAL_4PIN") == "12MHz"
    assert attrs == {}  # a symbol name is no part number
    assert value_from_properties("100MHz", "L2", raw, {}) == "100MHz"  # Frequency is no inductance
    attrs = {}
    assert value_from_properties("74405042022", "L3", {"Inductance": "2.2uH"}, attrs) == "2.2uH"
    assert attrs == {"mpn": "74405042022"}


@pytest.mark.parametrize("package,footprint", [
    ("SOT50P160X60-6N", "SOT50P160X60-6N"),  # SOT-563 (TPS61023DRLT), not "SOT-6"
    ("SOT95P280X145-6N", "SOT95P280X145-6N"),  # SOT-23-6
    ("QFN50P700X700X100-49N", "QFN50P700X700X100-49N"),
    ("SOIC127P600X175-8N", "SOIC127P600X175-8N"),  # 6.00 is the lead span, not a body size
    ("TO229P990X239-3N", "TO229P990X239-3N"),  # a DPAK, not a "TO-3"
])
def test_ipc_footprints_keep_pitch_and_size(package, footprint):
    assert normalize_footprint(package, "U3") == footprint


def test_pins_of_dotted_and_plus_refs_stay_on_their_nets():
    """Olimex's TESTPAD parts +3.3V1/+5V1/+1V1 and the LLC converter's J5.1/T1.1 lost every pin."""
    from parse_boards import BoardData, Component, Net, _apply_net_pin_fixes, board_to_dict, split_pin
    assert split_pin("J5.1.1", {"J5.1"}) == ("J5.1", "1")
    assert split_pin("U1.A.1", {"U1"}) == ("U1", "A.1")  # an Eagle gate pin
    assert split_pin("U1.P0.13", {"U1"}) == ("U1", "P0.13")  # an nRF pin name
    assert split_pin("R1.2") == ("R1", "2")
    nets = [Net(name="+3.3V", pins=["+3.3V1.1", "C1.2"]), Net(name="VIN", pins=["J5.1.1", "F1.1.2"])]
    _apply_net_pin_fixes("test", nets)
    board = BoardData(name="b", slug="b", source="o/r", format="kicad7", nets=nets, components=[
        Component(ref="+3.3V1", value="TESTPAD", footprint="TESTPAD_40-ROUND"),
        Component(ref="C1", value="100nF", footprint="0402"),
        Component(ref="J5.1", value="XT60", footprint="XT60"),
        Component(ref="F1.1", value="Fuse_clips", footprint="~"),
    ])
    assert {n["name"]: n["pins"] for n in board_to_dict(board)["nets"]} == {
        "+3.3V": ["+3.3V1.1", "C1.2"], "VIN": ["F1.1.2", "J5.1.1"]}


def test_power_symbols_are_dropped_by_their_power_flag(tmp_path):
    from parsers.kicad import parse_schematic
    lib = '(symbol "OLIMEX_Power:+3.3V" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes))'
    sch = _kicad_sheet(tmp_path, "\n".join([
        _kicad_symbol("+3.3V1", "TESTPAD", "OLIMEX_OTHER:TESTPAD", "OLIMEX_Other-FP:TEST_PAD40x70_SQUARE",
                      "00000000-0000-0000-0000-000000000011"),
        _kicad_symbol("PWR1", "+3.3V", "OLIMEX_Power:+3.3V", "Fake:Footprint",
                      "00000000-0000-0000-0000-000000000012"),
    ]), lib_symbols=lib)
    assert [c.ref for c in parse_schematic(sch)[0]] == ["+3.3V1"]


def test_board_texts_name_only_what_the_boards_have():
    """Checked against each board's source (2026-11-10): GainBlock.sch has one HMC476 (IC1); the
    Duet 2 WiFi v1.04 sheets have no Ethernet part (the WiFi module is an ESP-07/12); HEEV's phase
    bridge is a separate board reached through J111 "Trinamic-Bridge"."""
    from board_overrides import TAG_OVERRIDES
    registry = parse_boards_md()
    gain = registry["simplefmcwradar-gainblock"]["key_coverage"]
    assert "x3" not in gain and "chain" not in gain and "single amplifier stage" in gain
    duet = registry["duet-2-wifi-v1-04"]["key_coverage"]
    assert "Ethernet" not in duet and "ethernet" not in extract_tags(duet)
    heev = registry["heev-motor-controller-2018"]["key_coverage"]
    assert "FET gate drivers" not in heev and "separate board" in heev and "60V->5V" not in heev
    assert "inverter" not in TAG_OVERRIDES["heev-motor-controller-2018"]


@pytest.mark.parametrize("raw,value,ref,expected", [
    ("2920L110/60MR", "1.1A PTC", "F1", {"mpn": "2920L110/60MR", "voltage": "60V"}),
    ("9A 22uH 37mOhm TMPC1265HP-220MG-D", "22uH", "L1", {"mpn": "TMPC1265HP-220MG-D"}),
    ("FSMD035-1206", "350mA PTC", "FUSE1", {"mpn": "FSMD035-1206"}),
    ("Q12MHz/20pF/10ppm/4P/3.2x2.5mm", "12MHz 20pF", "Q1", {"tolerance": "10ppm"}),
    ("Q12MHz/18pF/30ppm/4P/3.2x2.5mm(ABM8-12.000MHZ-D2Y-T)", "12MHz 18pF", "Q2",
     {"tolerance": "30ppm", "mpn": "ABM8-12.000MHZ-D2Y-T"}),
    ("M95256-WMN6P", "M95256", "U6", {"mpn": "M95256-WMN6P"}),
    ("SGM40567-4.2XG/TR", "SGM40567-4.2", "U4", {"mpn": "SGM40567-4.2XG/TR"}),
    ("4u7-TMK212AB7475KG-T", "4.7uF", "C1", {"mpn": "TMK212AB7475KG-T"}),
    # Nothing an ordering code: a package in parentheses, a part with its package, a symbol name
    ("RP2040(QFN-56_7x7mm_P0.4mm)", "RP2040", "U2", {}),
    ("1N4148W/SOD123", "1N4148W", "D1", {}),
    ("Conn_01x04", "1x4 2.54mm header", "J1", {}),
    ("PINHD-1X9", "1x9 header", "JP1", {}),
    ("10uF-16V", "10uF", "C1", {}),
])
def test_decoded_values_keep_their_part_number_and_ratings(raw, value, ref, expected):
    from parsers.common import keep_source_specs
    attrs: dict = {}
    keep_source_specs(raw, value, ref, attrs)
    assert attrs == expected
    attrs = {"mpn": "GIVEN"}
    keep_source_specs(raw, value, ref, attrs)
    assert attrs.get("mpn") == "GIVEN"  # the source's own MPN field wins


def test_olimex_crystal_keeps_its_load_capacitance():
    assert normalize_value("Q12MHz/20pF/10ppm/4P/3.2x2.5mm", "Q1") == "12MHz 20pF"
    assert normalize_value("Q25MHz/18pF/30ppm/4P/3.2x2.5mm(ABM8-25.000MHZ-D2Y-T)", "Q2") == "25MHz 18pF"


def test_eagle_ratings_in_deviceset_and_device_names():
    from parsers.eagle import _parse_deviceset_specs
    assert _parse_deviceset_specs("1.0UF50V10%(1206)") == {"voltage": "50V", "tolerance": "10%"}  # FemtoBuck C1
    assert _parse_deviceset_specs("0.1UF", "-0603-25V-(+80/-20%)") == {"voltage": "25V"}  # BNO080's caps
    assert _parse_deviceset_specs("22PF", "-0603-50V-5%") == {"voltage": "50V", "tolerance": "5%"}
    assert _parse_deviceset_specs("V_REG_3V3") == {}  # 3V3 is no 3 V rating


def test_invisible_marks_are_stripped():
    """HEEV's DigiKey numbers ended in U+200E; OrangeCrab's maker was wrapped in it."""
    from parsers.common import build_attributes
    assert build_attributes({"DigiKey": "MCP6004-I/SL-ND‎", "Mfg": "‎Yageo‎"}) == {
        "digikey": "MCP6004-I/SL-ND", "manufacturer": "Yageo"}
    assert normalize_value("EMK107ABJ475MA-T‎", "U1") == "EMK107ABJ475MA-T"


@pytest.mark.parametrize("value,junk", [
    ("FID", True), ("MOUNTING", True), ("LOGO", True), ("CE Logo", True), ("Heatsink", True),
    ("DNP 47K", True), ("DNP", True), ("dnp", True), ("DNF", True), ("NM", True), ("nf", True),
    ("NA", True), ("NA R0603", True), ("NA(C0402)", True),
    ("NA(47uF C0805)", False),  # Olimex's not-assembled-with-value form keeps its inner value
    ("10kohm", False), ("Analog", False), ("NAU8810", False), ("Logic analyzer", False),
])
def test_junk_and_do_not_fit_values_case_insensitively(value, junk):
    from parse_boards import is_junk_value
    assert is_junk_value(value) is junk


def test_led_series_resistor_is_not_a_pull():
    """PocketPD R22 was a "pulldown" on D5.K and Soldered MPPT R1 a "pullup" on D1.A."""
    from parse_boards import Component, Net, annotate_circuit_roles
    parts = [Component(ref="R22", value="1kohm", footprint="0402"),
             Component(ref="D5", value="red LED", footprint="0603"),
             Component(ref="R5", value="10kohm", footprint="0402"),
             Component(ref="U1", value="RP2040", footprint="QFN-56")]
    annotate_circuit_roles(parts, [Net(name="GND", pins=["R22.1", "R5.1"]),
                                   Net(name="Net-(D5-K)", pins=["D5.K", "R22.2"]),
                                   Net(name="Net-(U1-RUN)", pins=["R5.2", "U1.RUN"])])
    assert "pulldown" not in parts[0].attributes
    assert parts[2].attributes["pulldown"] == "U1.RUN"


def test_decoupling_tie_breaks_on_the_ref():
    """Two equidistant ICs: the pick followed set order, which changed with the hash seed."""
    from parse_boards import Component, Net, Position, annotate_circuit_roles
    cap = Component(ref="C1", value="100nF", footprint="0402")
    parts = [cap, Component(ref="U10", value="X", footprint="SOIC-8"), Component(ref="U9", value="X", footprint="SOIC-8")]
    annotate_circuit_roles(parts, [Net(name="+3V3", pins=["C1.1", "U10.VCC", "U9.VCC"]),
                                   Net(name="GND", pins=["C1.2", "U10.GND", "U9.GND"])],
                           [Position("C1", 0, 0), Position("U10", 5, 0), Position("U9", -5, 0)])
    assert cap.attributes["decouples"] == "U10"


@pytest.mark.parametrize("package,footprint", [
    ("Xtal_5x3.2", "Xtal_5x3.2"),  # Duet's X2 read "Xtal"
    ("R_Array_Convex_4x0402", "R_Array_Convex_4x0402"),
    ("RESPACK_4X0603", "RESPACK_4X0603"),
    ("Straight_2x01", "Straight_2x01"),
    ("JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "JST_XH_B2B-XH-A_1x02"),
    ("SOIC-8_3.9x4.9mm_P1.27mm", "SOIC-8"),  # standard KiCad packages stay compact
    ("CP_Elec_12.5x13.5", "Electrolytic-12.5x13.5"),  # dc-poe's bulk caps read "Electrolytic"
])
def test_footprint_fallback_keeps_the_size(package, footprint):
    assert normalize_footprint(package, "X1") == footprint


@pytest.mark.parametrize("value,footprint,expected", [
    ("Conn_01x02", "AMASS_XT60-F", "XT60-F"),
    ("1x2 header", "AMASS_XT60PW-M", "XT60PW-M"),
    ("XT30", "XT30_PTH", "XT30"),
    ("XT60 Female", "XT60", "XT60 Female"),
    ("Conn_01x02", "PinHeader_1x02_P2.54mm_Vertical", "1x2 2.54mm header"),
])
def test_xt_power_connectors_are_not_headers(value, footprint, expected):
    """XT60 sockets on the LLC converter, MOCO controller and Twisted Fields driver read
    "1x2 7.20mm header"."""
    from parse_boards import normalize_connector_value
    assert normalize_connector_value(value, footprint, "J1") == expected


def test_a_volt_unit_is_not_an_ordering_suffix():
    """ProtoCentral's "AP2112K-3.3V" normalized to AP2112K-3.3 and was published as an MPN."""
    from parsers.common import keep_source_specs
    attrs = {}
    keep_source_specs("AP2112K-3.3V", "AP2112K-3.3", "U1", attrs)
    assert "mpn" not in attrs
    keep_source_specs("M95256-WMN6P", "M95256", "U6", attrs)
    assert attrs["mpn"] == "M95256-WMN6P"
