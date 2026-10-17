"""jlc_search on natural-language queries that returned nothing, the wrong parts, or an error
before 0.6.5. Each runs the tool on the real database and checks every result, not one part
number, so the daily data can change under it."""

import json
from pathlib import Path

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.parsers import parse_current, parse_length_mm, parse_memory_size, parse_resistance, parse_voltage
from pcbparts_mcp.search.engine import _range_passes
from pcbparts_mcp.subcategory_aliases import SUBCATEGORY_ALIASES, SUBCATEGORY_GROUPS

SUBCATEGORIES = {
    info["name"].lower()
    for info in json.loads((Path(__file__).parent.parent / "data" / "subcategories.json").read_text(encoding="utf-8")).values()
}


async def search(query: str | None = None, **kwargs):
    result = await server.jlc_search(query=query, limit=kwargs.pop("limit", 50), **kwargs)
    assert "error" not in result, result.get("error")
    return result


def covers(value: str | None, target: float) -> bool:
    """A supply/output range ("2.7V~5.5V", "1.71V~1.89V、2.25V~5.5V", "3.3V") includes target."""
    return bool(value) and _range_passes(value, parse_voltage, "=", target)


class TestRangePasses:
    @pytest.mark.parametrize("value,op,target,expected", [
        ("2.7V~5.5V", "=", 3.3, True),
        ("2.7V~5.5V", "=", 12, False),
        ("4.5V~40V", ">=", 30, True),   # max input reaches 30V (the first number is 4.5)
        ("4.5V~40V", "<=", 3, False),
        ("1.71V~1.89V、2.25V~5.5V", "=", 3.3, True),
        ("-15V~-5V、5V~15V", "=", -12, True),
        ("3.3V", "=", 3.3, True),
        ("5V", "=", 3.3, False),
        ("-", "=", 3.3, False),
    ])
    def test_range(self, value, op, target, expected):
        assert _range_passes(value, parse_voltage, op, target) is expected


class TestAliases:
    def test_targets_are_subcategories(self):
        assert sorted({t for t in SUBCATEGORY_ALIASES.values() if t not in SUBCATEGORIES}) == []

    def test_group_members_are_subcategories(self):
        assert sorted({m for g in SUBCATEGORY_GROUPS.values() for m in g if m not in SUBCATEGORIES}) == []


class TestZeroResultQueries:
    """These returned 0 parts: the parser added "Voltage Rating >=" or "Current Rating >=" (its
    defaults) to part types that don't list them."""

    async def test_relay_coil_voltage(self):
        result = await search("5V relay")
        assert result["total"] > 0
        assert all(parse_voltage(p["specs"]["Coil Voltage"]) == 5 for p in result["results"])
        # "relay" covers power relays too (the SRD-05VDC is one)
        assert "Power Relays" in {p["subcategory"] for p in result["results"]}

    async def test_level_shifter_supply(self):
        result = await search("3.3V level shifter")
        assert result["total"] > 0
        for part in result["results"]:
            sides = [part["specs"].get(k) for k in ("Voltage - Supply", "Voltage - Supply(VCCA)", "Voltage - Supply(VCCB)")]
            assert any(covers(v, 3.3) for v in sides), part["specs"]

    async def test_op_amp_voltage_left_out(self):
        """Op amps don't list a supply voltage (14 of ~4,900), so 5V is left out and said so."""
        result = await search("op amp 5V rail to rail")
        assert result["total"] > 0
        adjusted = result["parsed"]["adjusted_filters"]
        assert adjusted and adjusted[0]["now"] is None

    async def test_buck_converter(self):
        result = await search("12V buck converter 2A")
        assert result["total"] > 0
        for part in result["results"]:
            assert "buck" in part["specs"]["Topology"].lower().split("、")
            assert parse_current(part["specs"]["Output Current"]) >= 2
            assert covers(part["specs"]["Output Voltage"], 12)

    async def test_tactile_switch_size(self):
        result = await search("tactile switch 6x6 SMD")
        assert result["total"] > 0
        for part in result["results"]:
            assert parse_length_mm(part["specs"]["Length"]) == 6 and parse_length_mm(part["specs"]["Width"]) == 6

    async def test_high_side_switch(self):
        result = await search("high side switch 4A")
        assert result["filters_applied"]["subcategory_resolved"] == "Power Distribution Switches"
        assert result["total"] > 0
        assert all(parse_current(p["specs"]["Maximum Continuous Current"]) >= 4 for p in result["results"])

    async def test_leftover_words_left_out(self):
        result = await search("dual NPN transistor SOT-363")
        assert result["total"] > 0
        assert result["relaxed"]["dropped_text"] == "dual"

    async def test_ntc_resistance(self):
        """"Resistance @ 25℃": names with non-ASCII never matched (the JSON stores \\u2103)."""
        result = await search("NTC 10k")
        assert result["total"] > 0
        assert all(parse_resistance(p["specs"]["Resistance @ 25℃"]) == 10_000 for p in result["results"])

    async def test_mosfet_driver(self):
        result = await search("MOSFET driver")
        assert result["filters_applied"]["subcategory_resolved"] == "Gate Drivers"
        assert result["total"] > 0

    async def test_input_and_output_voltage(self):
        result = await search("buck 24V input 3.3V output 1A")
        filters = {(f["name"], f["op"], f["value"]) for f in result["filters_applied"]["spec_filters"]}
        assert {("Supply Voltage", "=", "24V"), ("Output Voltage", "=", "3.3V")} <= filters
        assert result["total"] > 0
        for part in result["results"]:
            assert covers(part["specs"]["Voltage - Supply"], 24) and covers(part["specs"]["Output Voltage"], 3.3)


class TestWrongResults:
    async def test_ldo_output_is_exact(self):
        """">= 3.3V" put 5V LDOs (AMS1117-5.0, L78M05) among "3.3V LDO" results."""
        result = await search("3.3V LDO 500mA")
        assert result["total"] > 0
        assert all(parse_voltage(p["specs"]["Output Voltage"]) == 3.3 for p in result["results"])

    async def test_zener_voltage_is_exact(self):
        result = await search("zener 5.1V")
        assert result["total"] > 0
        assert all(parse_voltage(p["specs"]["Zener Voltage(Nom)"]) == 5.1 for p in result["results"])

    async def test_boost_converter_is_boost(self):
        result = await search("boost converter")
        assert result["total"] > 0
        assert all("boost" in p["specs"]["Topology"].lower().split("、") for p in result["results"])

    async def test_p_channel_includes_polarity_from_number(self):
        """AO3401A's Type is "-"; it says 1 P-Channel in Number."""
        result = await search("P-channel MOSFET SOT-23", library_type="basic")
        assert "C15127" in [p["lcsc"] for p in result["results"]]

    async def test_inductor_covers_power_inductors(self):
        result = await search("22uH inductor 3A")
        assert result["total"] > 50  # was 5: Inductors (SMD) only
        assert {"Power Inductors", "Molding Power Inductors"} & {p["subcategory"] for p in result["results"]}

    async def test_usb_type_a(self):
        result = await search("USB-A receptacle")
        assert result["total"] > 0
        assert all(p["specs"]["Connector Type"] == "Type-A" for p in result["results"])

    async def test_sma_series(self):
        result = await search("SMA connector right angle edge mount")
        assert result["total"] > 0
        assert all(p["specs"]["RF Series"] == "SMA" for p in result["results"])

    async def test_magjacks_not_limited_to_filtered(self):
        """"RJ45 with magnetics" returned only the 19 jacks described "Filtered"."""
        result = await search("RJ45 with magnetics")
        assert result["total"] > 100
        assert any("Filtered" not in (p.get("description") or "") for p in result["results"])
        assert result["parsed"]["detected"]["not_searched"]

    async def test_rs485_transceiver_at_3v3(self):
        result = await search("RS485 transceiver 3.3V")
        assert result["filters_applied"]["subcategory_resolved"] == "RS-485 / RS-422 ICs"
        assert result["total"] > 0
        assert all(covers(p["specs"]["Voltage - Supply"], 3.3) for p in result["results"])

    async def test_buzzer_runs_at_voltage(self):
        """Its Voltage Rating is a list ("3V、5V、12V"); ">= 5V" put 12V buzzers first."""
        result = await search("buzzer 5V")
        assert result["total"] > 0
        assert all(covers(p["specs"]["Voltage - Supply"], 5) for p in result["results"])

    async def test_np0_finds_c0g(self):
        """C0G, NP0 and COG are one dielectric; the basic 47pF part (C1671) is listed as C0G."""
        result = await search("47pF NP0 0603", library_type="basic")
        assert "C1671" in [p["lcsc"] for p in result["results"]]


class TestErrors:
    async def test_ferrite_impedance_doesnt_raise(self):
        """'Impedance @ Frequency' is registered as "special"; the filter code called it."""
        result = await search("ferrite bead 0603 600")
        assert result["total"] > 0
        assert all(parse_resistance(p["specs"]["Impedance @ Frequency"].split("@")[0]) == 600 for p in result["results"])

    async def test_memory_size_filter_applies(self):
        """It was dropped without a word: all 6,772 MCUs came back."""
        everything = await search(subcategory_name="Microcontrollers (MCU/MPU/SOC)", limit=1)
        result = await search(
            subcategory_name="Microcontrollers (MCU/MPU/SOC)",
            spec_filters=[{"name": "Program Memory Size", "op": ">=", "value": "1MB"}],
        )
        assert 0 < result["total"] < everything["total"]
        for part in result["results"]:
            # The column holds whichever the part lists (as the database build reads them)
            flash = next(part["specs"][k] for k in ("Flash", "Program Memory Size", "Program Storage Size") if k in part["specs"])
            assert parse_memory_size(flash) >= 1024 * 1024

    async def test_unusable_filter_is_reported(self):
        result = await search(subcategory_name="MOSFETs", spec_filters=[{"name": "Configuration", "op": ">=", "value": "2"}])
        assert result["ignored_filters"][0]["filter"] == "Configuration >= 2"

    async def test_non_ascii_value(self):
        result = await search(subcategory_name="Coaxial Connectors (RF)", spec_filters=[{"name": "Impedance", "op": "=", "value": "50Ω"}])
        assert result["total"] > 0


class TestTotals:
    """total counted parts the search didn't return (repo audit, 2026-07-02, item 1)."""

    async def test_library_type_total(self):
        """The counts query drops the library_type filter: basic MOSFETs reported ~31,000."""
        result = await search(subcategory_name="MOSFETs", library_type="basic", limit=100)
        assert result["total"] == len(result["results"]) == result["library_type_counts"]["basic"]

    async def test_post_filtered_total_counts_parts_that_pass(self):
        """Python-checked filters (a current here) were counted before the check."""
        from pcbparts_mcp.db import get_db

        result = await search("high side switch 4A", limit=100)
        db = get_db()
        expected = 0
        for (attributes,) in db._conn.execute(
            "SELECT attributes FROM components WHERE subcategory_id = ? AND stock >= 10",
            [db.resolve_subcategory_name("Power Distribution Switches")],
        ):
            current = parse_current(dict(json.loads(attributes)).get("Maximum Continuous Current", ""))
            expected += current is not None and current >= 4
        assert result["total"] == expected

    async def test_pages_follow_the_checked_order(self):
        first = await search("12V buck converter 2A", limit=5)
        second = await server.jlc_search(query="12V buck converter 2A", limit=10)
        assert [p["lcsc"] for p in second["results"][:5]] == [p["lcsc"] for p in first["results"]]
