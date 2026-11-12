"""0.8.1 regressions found testing 0.8.0 on production. Searches run on the local catalog and check
every result rather than one part number, so the daily data can change under them."""

import re
import sys
from pathlib import Path

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.alternatives import is_compatible_alternative, package_warning
from pcbparts_mcp.design_rules import get_design_rules
from pcbparts_mcp.mounting import detect_mounting_type
from pcbparts_mcp.pinout import parse_easyeda_pins
from pcbparts_mcp.search.engine import _as_dual_rail, metric_thread_ok
from pcbparts_mcp.smart_parser import parse_smart_query

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_boards_db import part_numbers  # noqa: E402
from search_baseline import offline  # noqa: E402


@pytest.fixture(autouse=True)
async def no_network():
    # Async so the event loop exists first: on Windows its socket pair is built with connect()
    with offline():
        yield


async def search(query: str | None = None, **kwargs):
    result = await server.jlc_search(query=query, limit=kwargs.pop("limit", 50), **kwargs)
    assert "error" not in result, result.get("error")
    return result


def _filters(result: dict) -> list[tuple[str, str, str]]:
    return [(f["name"], f["op"], f["value"]) for f in result["filters_applied"]["spec_filters"]]


class TestColourBesidePartNumber:
    """"NE555 red" applied Illumination Color = Red to every part, found nothing, and said NE555
    wasn't in stock."""

    @pytest.mark.parametrize("query, part, colour", [
        ("NE555 red", "NE555", "red"), ("STM32F103C8T6 blue pill", "STM32F103C8T6", "blue"),
        ("TP4056 blue module", "TP4056", "blue")])
    async def test_colour_is_not_a_filter(self, query, part, colour):
        result = await search(query)
        assert result["total"] > 0
        assert not any(name == "Illumination Color" for name, _, _ in _filters(result))
        assert all(part in p["model"].upper() for p in result["results"])
        assert any(note.startswith(colour) for note in result["parsed"]["detected"]["not_searched"])

    async def test_led_part_type_keeps_the_colour(self):
        result = await search("KT-0603R red LED")
        assert ("Illumination Color", "=", "Red") in _filters(result)

    def test_strict_keeps_the_word_as_text(self):
        parsed = parse_smart_query("NE555 red", strict=True)
        assert "red" in parsed.remaining_text.split()
        assert not any(f.name == "Illumination Color" for f in parsed.spec_filters)

    async def test_hint_says_the_part_is_in_stock(self):
        result = await search("NE555 0201")
        assert result["total"] == 0
        assert re.match(r"\d+ in-stock parts? match NE555, but none with the package", result["hint"])


class TestMultiUnitPinout:
    """MIMXRT1052CVL5B (BGA-196): EasyEDA keeps a multi-unit symbol's pins in subparts, and
    jlc_get_pinout said "missing pin data"."""

    PIN = "P~show~0~{n}~0~0~180~g{n}~0^^0~0^^M0,0h10~#000^^1~0~0~0~{name}~start~~~#000^^1~0~0~0~{n}~end~~~#000"

    def unit(self, *pins):
        return {"dataStr": {"shape": [self.PIN.format(n=n, name=name) for n, name in pins]}}

    def test_subparts_are_read(self):
        data = {"dataStr": {"shape": []}, "subparts": [
            self.unit(("A10", "GPIO_B0_11"), ("B2", "GPIO_AD_00")), self.unit(("A1", "VSS"), ("A2", "VSS"))]}
        pins = parse_easyeda_pins(data)
        assert [(p["number"], p["name"]) for p in pins] == [
            ("A1", "VSS"), ("A2", "VSS"), ("A10", "GPIO_B0_11"), ("B2", "GPIO_AD_00")]

    def test_a_pin_in_two_units_is_listed_once(self):
        data = {"subparts": [self.unit(("1", "VCC"), ("2", "IN")), self.unit(("1", "VCC"), ("3", "OUT"))]}
        assert [p["number"] for p in parse_easyeda_pins(data)] == ["1", "2", "3"]
        # ...even when the units name it differently
        data = {"subparts": [self.unit(("4", "VEE"), ("1", "OUT1")), self.unit(("4", "GND"), ("7", "OUT2"))]}
        assert [(p["number"], p["name"]) for p in parse_easyeda_pins(data)] == [
            ("1", "OUT1"), ("4", "VEE"), ("7", "OUT2")]

    def test_a_complete_top_level_symbol_wins_over_its_units(self):
        """LM358 C328566 draws all 8 pins at the top level and again as two units with other
        names (OUTA, GND), and jlc_get_pinout listed 16 pins."""
        top = [("1", "OUT1"), ("2", "IN1-"), ("3", "IN1+"), ("4", "VEE"),
               ("5", "IN2+"), ("6", "IN2-"), ("7", "OUT2"), ("8", "VCC")]
        data = {**self.unit(*top), "subparts": [
            self.unit(("1", "OUTA"), ("2", "INA-"), ("3", "INA+"), ("4", "GND"), ("8", "V+")),
            self.unit(("5", "INB+"), ("6", "INB-"), ("7", "OUTB"), ("4", "GND"), ("8", "V+"))]}
        assert [(p["number"], p["name"]) for p in parse_easyeda_pins(data)] == top

    def test_unit_electrical_type_fills_the_same_pad(self):
        typed = "P~show~{e}~{n}~0~0~180~g{n}~0^^0~0^^M0,0h10~#000^^1~0~0~0~{name}~start~~~#000^^1~0~0~0~{n}~end~~~#000"
        data = {**self.unit(("1", "OUT1"), ("2", "IN1-")), "subparts": [{"dataStr": {"shape": [
            typed.format(e=2, n=1, name="OUTA"), typed.format(e=0, n=2, name="INA-")]}}]}
        pins = parse_easyeda_pins(data)
        assert [(p["name"], p.get("electrical")) for p in pins] == [("OUT1", "output"), ("IN1-", None)]

    def test_units_fill_pins_a_partial_top_level_lacks(self):
        data = {**self.unit(("1", "OUT1")), "subparts": [self.unit(("1", "OUTA"), ("2", "IN1-"))]}
        assert [(p["number"], p["name"]) for p in parse_easyeda_pins(data)] == [("1", "OUT1"), ("2", "IN1-")]

    async def test_pinout_tool(self, monkeypatch):
        test = self

        class Fake:
            async def get_part(self, lcsc):
                return {"lcsc": lcsc, "model": "MIMXRT1052CVL5B", "subcategory": "Microcontrollers (MCU/MPU/SOC)",
                        "has_easyeda_footprint": True, "easyeda_symbol_uuid": "u"}

            async def get_easyeda_component(self, uuid):
                return {"dataStr": {"shape": []}, "subparts": [test.unit(("A1", "VSS")), test.unit(("B1", "GPIO"))]}
        monkeypatch.setattr(server, "_client", Fake())
        result = await server.jlc_get_pinout(lcsc="C188198")
        assert "error" not in result
        assert result["pin_count"] == 2


def jack(mounting, rank="TRRS", **specs):
    return {"mounting_type": mounting, "specs": {"Connector Type": "3.5mm Headphone Jack", "Rank Number": rank,
                                                 "Mounting Style": "Surface Mount", **specs}}


class TestConnectorMounting:
    """Audio, RF coax, IDC and circular connectors and jumpers don't list Mounting Type, so it was never
    checked: the SMD PJ-320D jack was offered the through-hole PJ-320A-4P first, and a TRS jack for a TRRS one."""

    def test_through_hole_jack_for_an_smd_one(self):
        assert not is_compatible_alternative(jack("smd"), jack("through_hole"), "Audio Connectors")[0]

    def test_trs_jack_for_a_trrs_one(self):
        assert not is_compatible_alternative(jack("smd", "TRRS"), jack("smd", "TRS"), "Audio Connectors")[0]

    def test_same_mounting_and_contacts(self):
        compatible, info = is_compatible_alternative(jack("smd"), jack("smd"), "Audio Connectors")
        assert compatible
        assert {"Mounting Type", "Rank Number"} <= set(info["specs_verified"])
        assert not info["unverified_requirements"]

    def test_coax_connectors(self):
        sma = {"Connector Type": "SMA"}
        smd = {"mounting_type": "smd", "specs": sma}
        tht = {"mounting_type": "through_hole", "specs": sma}
        assert not is_compatible_alternative(smd, tht, "Coaxial Connectors (RF)")[0]
        assert is_compatible_alternative(smd, smd, "Coaxial Connectors (RF)")[0]

    def test_unknown_mounting_stays_unverified(self):
        compatible, info = is_compatible_alternative(jack("smd"), jack("not_sure"), "Audio Connectors")
        assert compatible and "Mounting Type" in info["unverified_requirements"]


def ntc(**b_constants):
    names = {"b50": "B Constant (25℃/50℃)", "b85": "B Constant (25℃/85℃)", "b100": "B Constant (25℃/100℃)"}
    specs = {"Resistance @ 25℃": "10kΩ", **{names[k]: v for k, v in b_constants.items()}}
    return {"specs": specs}


class TestNtcBConstant:
    """Only the 25/100 B constant was compared, which 190 of 1,114 stocked NTCs list: a 10k B3950
    (MF52A103F3950, 25/50 only) had no verified alternative, and B3435 parts ranked beside B3950 ones."""

    def test_the_pair_both_list(self):
        compatible, info = is_compatible_alternative(ntc(b50="3950K"), ntc(b50="3950K", b85="4021K"), "NTC Thermistors")
        assert compatible and "B Constant (25℃/50℃)" in info["specs_verified"]

    def test_a_different_b_constant(self):
        assert not is_compatible_alternative(ntc(b50="3950K"), ntc(b50="3435K"), "NTC Thermistors")[0]

    def test_first_shared_pair(self):
        compatible, info = is_compatible_alternative(ntc(b50="3380K", b85="3434K"), ntc(b85="3434K"), "NTC Thermistors")
        assert compatible and "B Constant (25℃/85℃)" in info["specs_verified"]

    def test_no_shared_pair_is_unverified(self):
        compatible, info = is_compatible_alternative(ntc(b50="3950K"), ntc(b100="4334K"), "NTC Thermistors")
        assert compatible and "B Constant" in info["unverified_requirements"]


class TestPartNumberAcrossPartTypes:
    """"WS2812B LED" found 18 of the 19 WS2812B parts: JLCPCB files WS2812B-V6 under LED Indication -
    Discrete, and the part type limited the search to RGB LEDs(Built-in IC)."""

    async def test_ws2812b_led_finds_every_ws2812b_led(self):
        plain = await search("WS2812B", limit=100)
        led = await search("WS2812B LED", limit=100)
        expected = {p["lcsc"] for p in plain["results"] if p["category"] == "Optoelectronics"}
        assert expected and expected <= {p["lcsc"] for p in led["results"]}
        assert led["parsed"]["subcategory"] == "rgb leds(built-in ic)"

    async def test_without_a_part_number_the_part_type_holds(self):
        result = await search("addressable RGB LED", limit=100)
        assert {p["subcategory"] for p in result["results"]} == {"RGB LEDs(Built-in IC)"}


class TestCellCounts:
    """"2S lithium battery charger" left "2S" out and listed single-cell TP4056 chargers first."""

    @pytest.mark.parametrize("query, cells", [("2S lithium battery charger", 2), ("1S lipo charger", 1),
                                              ("BMS 4S protection", 4)])
    async def test_cell_count(self, query, cells):
        result = await search(query)
        assert ("Number of Cells", "=", str(cells)) in _filters(result)
        assert result["total"] > 0 and not result.get("relaxed")
        for p in result["results"]:
            low, _, high = p["specs"]["Number of Cells"].partition("~")
            assert int(low) <= cells <= int(high or low)

    @pytest.mark.parametrize("query", ["fuse 2s", "NE555 2S", "2S"])
    def test_only_for_battery_parts(self, query):
        assert not any(f.name == "Number of Cells" for f in parse_smart_query(query).spec_filters)


class TestDistributorCodesAsMpn:
    """PowerFeather PowerUPS fills its MPN field with Mouser numbers, which board_get returned as mpn."""

    def test_mouser_number(self):
        assert part_numbers({"mpn": "595-BQ25622RYKR"}, "powerfeather-powerups") == (
            None, None, None, "595-BQ25622RYKR", None)

    def test_digikey_number(self):
        assert part_numbers({"mpn": "455-SM02B-SRSS-TBDKR-ND"}, "powerfeather-powerups")[4] == "455-SM02B-SRSS-TBDKR-ND"

    def test_other_boards_keep_maker_numbers_with_digits_first(self):
        # Johnson's 142-0701-801 SMA jack is the maker's own number
        assert part_numbers({"mpn": "142-0701-801"}, "ads-b-filter-lna")[0] == "142-0701-801"


class TestDualRailLists:
    """TRACO's TMR 3-2422WI (±12V, listed "-12V、+12V") met Output Voltage = 12V and missed ±12V."""

    @pytest.mark.parametrize("value, specs, expected", [
        ("-12V、+12V", {"Number of Outputs": "2"}, "±12V"),
        ("-15V、15V", {"Number of Outputs": "2", "Isolation Voltage(Vrms)": "1.5kV"}, "±15V"),
        # Non-isolated K78 regulators: one output wired either way (LCSC lists R-78E12-0.5 with two)
        ("-12V、12V", {"Number of Outputs": "2"}, "-12V、12V"),
        ("-12V、12V", {}, "-12V、12V"),
        ("-2.5V、15V", {"Number of Outputs": "2", "Isolation Voltage(Vrms)": "3kV"}, "-2.5V、15V"),
        ("-15V~-2.5V、2.5V~15V", {"Number of Outputs": "2"}, "-15V~-2.5V、2.5V~15V"),
    ])
    def test_as_dual_rail(self, value, specs, expected):
        assert _as_dual_rail(value, specs) == expected

    async def test_single_output_filter(self):
        result = await search(None, subcategory_name="DC-DC Power Modules", limit=100,
                              spec_filters=[{"name": "Output Voltage", "op": "=", "value": "12V"}])
        assert result["total"] > 0
        assert not any(_as_dual_rail(p["specs"].get("Output Voltage", ""), p["specs"]).startswith("±")
                       for p in result["results"])


class TestSmallerFixes:
    @pytest.mark.parametrize("topic", ["brown-out", "brownout", "brown out", "reset IC"])
    def test_brown_out_rule(self, topic):
        assert get_design_rules(topic)["matched_files"] == ["protection/voltage-supervisor"]

    @pytest.mark.parametrize("package, mounting", [
        ("LCC-124(24x24)", "smd"), ("TOLL-8", "smd"), ("SC70-6", "smd"), ("SC-59", "smd"),
        ("PowerPAK1212-8", "smd"), ("PowerDI-5", "smd"), ("WLP-16(1.7x1.8)", "smd"), ("DO-221AC", "smd"),
        ("ABS", "smd"), ("P600", "through_hole"), ("TO-46", "through_hole"), ("DO-247-2", "through_hole"),
        ("GBL", "through_hole"), ("KBJ", "through_hole"), ("GBP", "through_hole")])
    def test_mounting_type(self, package, mounting):
        assert detect_mounting_type(package) == mounting

    def test_package_listed_without_body_size(self):
        assert "same package type" in package_warning("WQFN-18", "WQFN-18(3x2.5)")
        assert package_warning("WQFN-18(3x3)", "WQFN-18(3x2.5)").startswith("Different package")
        assert package_warning("SOIC-8", "soic-8") is None

    @pytest.mark.parametrize("text, ok", [
        ("SMTSO-M2.5-5.56-4-1.53", False), ("SMTSO-M2-5.56-1.5-1.53", True), ("M2x5.56xL6.0", True),
        ("M2.5 and M2 nuts", True), ("SMTSO2025CTJ", True)])
    def test_metric_thread(self, text, ok):
        assert metric_thread_ok(text, "M2") is ok

    async def test_m2_standoff_leaves_out_m2_5(self):
        result = await search("M2 standoff SMT", limit=100)
        assert result["total"] > 0 and not result.get("relaxed")
        assert all(metric_thread_ok(f"{p['model']}", "M2") for p in result["results"])

    @pytest.mark.parametrize("query", ["ARM Cortex M4 microcontroller", "Cortex-M4 MCU", "M4 screw"])
    def test_m4_is_not_a_diode_package(self, query):
        assert parse_smart_query(query).package is None

    @pytest.mark.parametrize("query", ["M7 diode", "schottky M4"])
    def test_m7_beside_a_diode(self, query):
        assert parse_smart_query(query).package == "SMA"

    async def test_op_amp_single_supply(self):
        result = await search("op amp single supply", limit=100)
        assert not result.get("relaxed")
        assert result["total"] > 0
        assert all(any(re.search(r"\d", v) for k, v in p["specs"].items()
                       if k in ("Single supply", "Single Supply", "Voltage - Supply"))
                   for p in result["results"])
        with_voltage = await search("op amp single supply 5V")
        assert _filters(with_voltage) == [("Supply Voltage", "=", "5V")] and not with_voltage.get("relaxed")
