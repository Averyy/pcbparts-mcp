"""0.8.2 fixes from design-session reports (2026-11-02). Searches run on the local catalog and check
every result rather than one part number, so the daily data can change under them."""

import sys
from pathlib import Path

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.alternatives import likely_drop_in
from pcbparts_mcp.client import JLCPCBClient, maker_datasheet_link
from pcbparts_mcp.design_rules import get_design_rules
from pcbparts_mcp.mouser import _not_found
from pcbparts_mcp.search.spec_filter import switch_circuit
from pcbparts_mcp.smart_parser import parse_smart_query

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline  # noqa: E402

RULES = Path(__file__).parent.parent / "data" / "design-rules" / "rules"


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


def _items(value: str | None) -> set[str]:
    return {item.strip().lower() for item in (value or "").split("、")}


class TestDesignRuleKeys:
    """The INDEX prints "`guides/dfm.md`"; that form found nothing and returned the whole index."""

    @pytest.mark.parametrize("topic, key", [
        ("guides/dfm.md", "guides/dfm"), ("`interfaces/usb.md`", "interfaces/usb"), ("mcus/esp32.md", "mcus/esp32"),
        ("rules/guides/pcb-layout.md", "guides/pcb-layout"), ("power/LDO.MD", "power/ldo"), ("guides/dfm", "guides/dfm")])
    def test_index_form_finds_the_file(self, topic, key):
        assert get_design_rules(topic)["matched_files"] == [key]

    @pytest.mark.parametrize("topic", ["INDEX.md", "`INDEX.md`", ""])
    def test_index(self, topic):
        assert get_design_rules(topic)["matched_files"] == ["INDEX.md"]


class TestDesignRuleText:
    def test_boot_button_goes_straight_to_ground(self):
        text = (RULES / "mcus" / "esp32.md").read_text(encoding="utf-8")
        assert "Boot button pulls to GND through 10 kohm" not in text
        assert "boot button straight to GND" in text

    def test_usb_series_resistors_are_fitted_caps_are_footprints(self):
        # 0.9.0 audit: Espressif's C3/C6/S3 checklists say "It is recommended to populate 22/33 ohm
        # series resistors" and "reserve a footprint for a capacitor to ground"; 0.8.2 had read the
        # footprint advice as applying to the resistors.
        text = (RULES / "mcus" / "esp32.md").read_text(encoding="utf-8")
        assert "22-33 ohm series resistors close to chip" not in text
        assert "Reserve 22-33 ohm series-resistor footprints" not in text
        assert "Populate 22/33 ohm series resistors on S3/C3/C6 USB D+/D-, close to the chip." in text
        assert "reserving a cap-to-ground footprint on each data trace" in text

    def test_srv05_4_capacitance(self):
        text = (RULES / "interfaces" / "usb.md").read_text(encoding="utf-8")
        assert "0.85 pF" not in text
        assert "3 pF typ" in text


class TestLogicGates:
    """"74HC132 quad NAND schmitt" searched NAND FLASH; "quad NAND gate" returned flash chips."""

    @pytest.mark.parametrize("query", [
        "74HC132 quad NAND schmitt", "quad NAND gate", "NOR gate", "CD4011 NAND", "dual NOR gate SN74LVC2G02",
        "hex schmitt NAND 74HC"])
    def test_gate_words_mean_logic_gates(self, query):
        assert parse_smart_query(query).subcategory == "logic gates"

    @pytest.mark.parametrize("query, subcategory", [
        ("NAND flash 1Gb", "nand flash"), ("NAND", "nand flash"), ("SLC NAND", "nand flash"),
        ("MT29F4G08 NAND", "nand flash"), ("quad SPI NOR flash", "nor flash"), ("W25Q128 quad NOR", None),
        ("MOSFET gate driver", "gate drivers")])
    def test_memory_and_drivers_unchanged(self, query, subcategory):
        assert parse_smart_query(query).subcategory == subcategory

    async def test_every_result_is_a_quad_schmitt_nand(self):
        result = await search("quad schmitt NAND gate")
        assert result["total"] > 0
        for part in result["results"]:
            assert "nand gate" in _items(part["specs"]["Logic Type"])
            assert part["specs"]["Number of Gates"] == "4"
            assert _items(part["specs"]["Input type"]) & {"schmitt trigger", "施密特触发器"}

    async def test_single_two_input_and(self):
        result = await search("single 2-input AND gate")
        assert result["total"] > 0
        for part in result["results"]:
            assert "and gate" in _items(part["specs"]["Logic Type"])
            assert (part["specs"]["Number of Gates"], part["specs"]["Inputs per Gates"]) == ("1", "2")

    async def test_logic_type_matches_list_values(self):
        # "AND Gate、NAND Gate" is a NAND gate too
        result = await search(subcategory_name="Logic Gates", spec_filters=[
            {"name": "Logic Type", "op": "=", "value": "NAND Gate"}], limit=1)
        listed = server.get_db()._conn.execute(
            "SELECT COUNT(*) FROM components WHERE subcategory_id = 2168 AND stock >= 10 "
            "AND attributes LIKE '%\"Logic Type\", \"%NAND Gate%'").fetchone()[0]
        assert result["total"] == listed


class TestSwitchCircuit:
    """DP3T found 5 slide switches; "Double pole triple throw" found 443."""

    @pytest.mark.parametrize("value, circuit", [
        ("DP3T", "2P3T"), ("2P3T", "2P3T"), ("Double pole triple throw", "2P3T"), ("SPDT", "1P2T"),
        ("1P2T", "1P2T"), ("SPST-NO", "1P1T-NO"), ("DPST-NO", "2P1T-NO"), ("4PDT", "4P2T"),
        ("triple-pole/single-throw", "3P1T"), ("Four-pole single-throw (4PST)", "4P1T"),
        ("Single pole eight throw", "1P8T"), ("-", None), ("12V", None)])
    def test_spellings(self, value, circuit):
        assert switch_circuit(value) == circuit

    async def test_every_spelling_finds_the_same_switches(self):
        totals = set()
        for value in ("DP3T", "2P3T", "Double pole triple throw"):
            result = await search(subcategory_name="Slide Switches",
                                  spec_filters=[{"name": "Circuit", "op": "=", "value": value}])
            assert all(switch_circuit(p["specs"]["Circuit"]) == "2P3T" for p in result["results"])
            totals.add(result["total"])
        assert len(totals) == 1 and totals.pop() > 5

    @pytest.mark.parametrize("query, circuit", [
        ("slide switch 2P3T", "2P3T"), ("DP3T slide switch", "2P3T"), ("SPDT slide switch", "1P2T"),
        ("double pole double throw toggle switch", "2P2T")])
    async def test_query_words(self, query, circuit):
        result = await search(query)
        assert result["total"] > 0 and not result.get("relaxed")
        assert all(switch_circuit(p["specs"]["Circuit"]) == circuit for p in result["results"])

    async def test_contact_form_stays_exact(self):
        result = await search(subcategory_name="Tactile Switches",
                              spec_filters=[{"name": "Circuit", "op": "=", "value": "SPST-NC"}])
        assert result["total"] > 0
        assert all(p["specs"]["Circuit"] == "SPST-NC" for p in result["results"])

    def test_relays_keep_the_word_as_text(self):
        parsed = parse_smart_query("SPDT relay 5V")
        assert "SPDT" in parsed.remaining_text


class TestTierHint:
    """"No basic part matches; 16 parts do in other library tiers (extended parts add an assembly fee)"
    when one of the 16 was a Preferred part with no fee."""

    async def test_preferred_count_named(self):
        result = await search("2.2M resistor 0603 1%", package="0603", library_type="basic")
        if result["total"]:
            pytest.skip("a basic 2.2M 0603 1% resistor is listed now")
        preferred = await search("2.2M resistor 0603 1%", package="0603", library_type="preferred")
        if not preferred["total"]:
            pytest.skip("no preferred 2.2M 0603 1% resistor today")
        assert f"{preferred['total']} preferred (no assembly fee" in result["hint"]
        assert 'library_type="no_fee"' in result["hint"]

    async def test_extended_only(self):
        result = await search("TPS22917", library_type="basic")
        if result["total"]:
            pytest.skip("TPS22917 is a basic part now")
        assert "extended part" in result["hint"] and "preferred" not in result["hint"].split(";")[1]


class TestNotSearchedWords:
    def test_hyphenated_maker(self):
        notes = parse_smart_query("ESP32-S3 Ai-Thinker").detected["not_searched"]
        assert notes == ["Ai Thinker: words beside a part number aren't searched (strict=true keeps them)"]

    def test_second_part_number(self):
        parsed = parse_smart_query("addressable RGB LED WS2812 SK6812")
        assert parsed.remaining_text == "WS2812"
        assert parsed.detected["not_searched"] == [
            "SK6812: only the first part number (WS2812) is searched; search it separately"]

    @pytest.mark.parametrize("query", ["WS2812B LED 2020", "AMS1117 100mA", "STM32F103C8T6 LQFP48",
                                       "ESP32-S3-WROOM-1 N16R8"])
    def test_values_and_packages_are_not_part_numbers(self, query):
        notes = parse_smart_query(query).detected.get("not_searched", [])
        assert not any("only the first part number" in note for note in notes)


class TestMakerDatasheet:
    """TPS61023DRLR (C919459) had no datasheet link; JLCPCB lists TI's own."""

    @pytest.mark.parametrize("url, expected", [
        ("https://www.ti.com.cn/cn/lit/ds/symlink/tps61023.pdf?ts=1728812468331&ref_url=https%253A%2",
         "https://www.ti.com/lit/ds/symlink/tps61023.pdf"),
        ("https://www.ti.com/cn/lit/gpn/tps631000", "https://www.ti.com/lit/gpn/tps631000"),
        # LM73100's datasheet is lm7310.pdf; a PDF name made from the part number would be a 404
        ("https://www.ti.com/cn/lit/ds/symlink/lm7310.pdf", "https://www.ti.com/lit/ds/symlink/lm7310.pdf"),
        ("https://www.ti.com/lit/ds/symlink/lm358.pdf", "https://www.ti.com/lit/ds/symlink/lm358.pdf"),
        ("https://www.infineon.com/dgdl/x.pdf?fileId=5546d", "https://www.infineon.com/dgdl/x.pdf?fileId=5546d"),
        ("https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/x.pdf", None), ("", None), (None, None)])
    def test_link(self, url, expected):
        assert maker_datasheet_link(url) == expected

    def _part(self, **item):
        base = {"componentCode": "C919459", "componentModelEn": "TPS61023DRLR", "componentPrices": [],
                "attributes": []}
        return JLCPCBClient._transform_part(JLCPCBClient(), {**base, **item}, slim=False)

    def test_maker_link_when_jlcpcb_has_no_pdf(self):
        part = self._part(dataManualUrl="", dataManualOfficialLink="https://www.ti.com/cn/lit/gpn/tps61023")
        assert part["maker_datasheet"] == "https://www.ti.com/lit/gpn/tps61023"
        assert "datasheet_note" not in part

    def test_note_when_there_is_none(self):
        part = self._part(dataManualUrl=None, dataManualOfficialLink="")
        assert "maker_datasheet" not in part and "datasheet_pdf" not in part
        assert "no datasheet PDF" in part["datasheet_note"]

    def test_specs_note_for_empty_listing(self):
        assert "no specs" in self._part()["specs_note"]
        part = self._part(attributes=[{"attribute_name_en": "Circuit", "attribute_value_name": "SPDT"}])
        assert "specs_note" not in part


class TestAlternativesWithoutRules:
    @pytest.mark.parametrize("candidate, note", [
        ("XL-2020RGBC-WS2812B", True), ("WS2812B-2020", True), ("WS2812C-2020-V6", False), ("SK6812MINI", False)])
    def test_maker_copy_counts_as_family(self, candidate, note):
        result = likely_drop_in({"model": "WS2812B-2020-V6"}, {"model": candidate}, same_package=True)
        assert bool(result) is note

    def test_needs_same_package(self):
        assert likely_drop_in({"model": "WS2812B-2020-V6"}, {"model": "XL-2020RGBC-WS2812B"}, False) is None


class TestMouserNotFound:
    def test_batch_names_missing_numbers(self):
        results = [{"part_number": "356-ESP32S3WRM1UN16R2", "mfr_part_number": "ESP32-S3-WROOM-1U-N16R2"},
                   {"part_number": "595-TPS22917DBVR", "mfr_part_number": "TPS22917DBVR"},
                   {"part_number": "N/A", "mfr_part_number": "SRV05-4"}]
        asked = ["ESP32-S3-WROOM-1U-N16R2", "SIM7080G-M", "595-TPS22917DBVR", "TPS22917", "AO3401A", "SRV05-4"]
        assert _not_found(asked, results) == ["SIM7080G-M", "AO3401A"]


class TestSupplyRange:
    """Two supply voltages were grouped as exact strings ("5V"), and a second filter of the same name
    and operator was dropped, so the reply depended on their order."""

    async def test_both_voltages_inside_one_range(self):
        totals = set()
        for values in (("5V", "28V"), ("28V", "5V")):
            result = await search(subcategory_name="Power Distribution Switches", spec_filters=[
                {"name": "Supply Voltage", "op": "=", "value": v} for v in values])
            assert result["total"] > 0
            for part in result["results"]:
                low, high = (float(x.rstrip("V")) for x in part["specs"]["Voltage - Supply"].split("~"))
                assert low <= 5 and high >= 28
            totals.add(result["total"])
        assert len(totals) == 1


class TestOvpSwitch:
    """"OVP load switch" dropped OVP as text and returned high-side USB switches."""

    @pytest.mark.parametrize("query", ["OVP load switch", "overvoltage protection load switch",
                                       "OVP switch 28V", "load switch over-voltage protection"])
    async def test_every_result_lists_ovp(self, query):
        result = await search(query)
        assert result["filters_applied"]["subcategory_resolved"] == "Power Distribution Switches"
        assert result["total"] > 0 and not result.get("relaxed")
        for part in result["results"]:
            assert _items(part["specs"]["Features"]) & {"overvoltage protection", "over voltage protection", "过压保护"}

    async def test_reverse_current_blocking(self):
        result = await search("load switch reverse current blocking")
        assert result["total"] > 0
        assert all("reverse current blocking" in _items(p["specs"]["Features"]) for p in result["results"])


class TestDocumentedFirst:
    """JMEconn's SK23D07 (C56164084) lists no specs, datasheet or footprint, and led on stock."""

    async def test_spec_less_parts_follow(self):
        result = await search(subcategory_name="Slide Switches", limit=100)
        flags = [not p["specs"] for p in result["results"]]
        assert flags == sorted(flags)


class TestUnlistedNames:
    async def test_most_stocked_named(self):
        result = await search("addressable RGB LED 3.3V")
        entries = result.get("unlisted") or []
        if not entries:
            pytest.skip("every addressable LED lists a supply voltage now")
        for entry in entries:
            assert 0 < len(entry["most_stocked"]) <= min(3, entry["parts"])
            assert all(name.startswith("C") for name in entry["most_stocked"])
