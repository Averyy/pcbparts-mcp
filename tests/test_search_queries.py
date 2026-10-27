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


class TestIssue17MegohmMilliohm:
    """github.com/Averyy/pcbparts-mcp/issues/17: a 1MΩ resistor came back as 1mΩ."""

    CHIP = "Chip Resistor - Surface Mount"

    @pytest.mark.parametrize("args,target", [
        ({"query": "1M resistor"}, 1e6),
        ({"query": "1M resistor 2512"}, 1e6),
        ({"query": "1Mohm resistor"}, 1e6),
        ({"query": "1M ohm resistor 0805"}, 1e6),
        ({"query": "1MOhm 1% 0603"}, 1e6),
        ({"query": "R1 1MΩ 0603 1%"}, 1e6),
        ({"query": "1 MΩ 0402 resistor"}, 1e6),
        ({"query": "1meg resistor"}, 1e6),
        ({"query": "4.99k resistor 0603"}, 4990),
        ({"subcategory_name": CHIP, "spec_filters": [{"name": "Resistance", "op": "=", "value": "1MOhm"}]}, 1e6),
        ({"subcategory_name": CHIP, "spec_filters": [{"name": "Resistance", "op": "=", "value": "1Mohm"}]}, 1e6),
        ({"subcategory_name": CHIP, "spec_filters": [{"name": "Resistance", "op": "=", "value": 1000000}]}, 1e6),
        ({"query": "1mΩ resistor 2512"}, 1e-3),
        ({"query": "1 mOhm current sense resistor"}, 1e-3),
        ({"query": "1milliohm shunt resistor"}, 1e-3),
        ({"subcategory_name": CHIP, "spec_filters": [{"name": "Resistance", "op": "=", "value": "1mOhm"}]}, 1e-3),
    ])
    async def test_every_result_has_the_requested_resistance(self, args, target):
        result = await server.jlc_search(**args, limit=100)
        assert result["total"] > 0  # "R1" (a BOM reference) may be relaxed away; the value never is
        assert any(f["name"] == "Resistance" for f in result["filters_applied"]["spec_filters"])
        # Exact: resistors come in ~1% steps, so 990kΩ or 1.01MΩ is a different part than 1MΩ
        assert all(parse_resistance(p["specs"]["Resistance"]) == pytest.approx(target) for p in result["results"])

    def test_alternatives_need_the_same_resistance(self):
        from pcbparts_mcp.alternatives import _compare_values

        assert _compare_values("1MΩ", "1MΩ", "Resistance")
        for other in ("1mΩ", "990kΩ", "1.01MΩ"):
            assert not _compare_values("1MΩ", other, "Resistance")
        assert not _compare_values("4.99kΩ", "5kΩ", "Resistance")
        assert _compare_values("100nF", "101nF", "Capacitance")  # other values keep their 2% slack


class TestBatch2Values:
    @pytest.mark.parametrize("value,target", [
        ("1M", 1e6), ("4.7M", 4.7e6), ("10M", 1e7), ("10Meg", 1e7),
        ("10MEG", 1e7), ("10m", .01), ("10mΩ", .01), ("10mOhm", .01),
        ("10 milliohm", .01),
    ])
    async def test_resistance_prefix_case(self, value, target):
        for args in (
            {"query": f"{value} resistor 0603"},
            {"subcategory_name": "Chip Resistor - Surface Mount", "package": "0603",
             "spec_filters": [{"name": "Resistance", "op": "=", "value": value}]},
        ):
            result = await search(**args)
            assert result["total"] > 0
            assert all(parse_resistance(p["specs"]["Resistance"]) == pytest.approx(target)
                       for p in result["results"])

    @pytest.mark.parametrize("ascii_query,unicode_query,spec,parser,target", [
        ("2.2uF capacitor 0603", "2.2µF capacitor 0603", "Capacitance", "capacitance", 2.2e-6),
        ("2.2uF capacitor 0603", "2.2μF capacitor 0603", "Capacitance", "capacitance", 2.2e-6),
        ("10uH inductor 1A", "10µH inductor 1A", "Inductance", "inductance", 1e-5),
        ("10uH inductor 1A", "10μH inductor 1A", "Inductance", "inductance", 1e-5),
    ])
    async def test_unicode_units(self, ascii_query, unicode_query, spec, parser, target):
        from pcbparts_mcp.parsers import parse_capacitance, parse_inductance

        parse = {"capacitance": parse_capacitance, "inductance": parse_inductance}[parser]
        expected = await search(ascii_query)
        result = await search(unicode_query)
        assert result["parsed"]["original_query"] == unicode_query
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert all(parse(p["specs"][spec]) == pytest.approx(target) for p in result["results"])

    @pytest.mark.parametrize("query,spec,target", [
        ("10 kΩ 0402 resistor", "Resistance", 10000),
        ("4u7 0805 capacitor", "Capacitance", 4.7e-6),
        ("22uF 6V3 0805", "Voltage Rating", 6.3),
        ("10k resistor 1005", "Resistance", 10000),
    ])
    async def test_common_value_forms(self, query, spec, target):
        from pcbparts_mcp.parsers import parse_capacitance

        result = await search(query)
        assert result["total"] > 0
        parse = {"Resistance": parse_resistance, "Capacitance": parse_capacitance,
                 "Voltage Rating": parse_voltage}[spec]
        for part in result["results"]:
            actual = parse(part["specs"][spec])
            assert actual >= target if spec == "Voltage Rating" else actual == pytest.approx(target)
            if "1005" in query:
                assert part["package"] == "0402"
        if "6V3" in query:
            assert any(f["name"] == "Voltage Rating" and parse_voltage(f["value"]) == 6.3
                       for f in result["filters_applied"]["spec_filters"])

    @pytest.mark.parametrize("value", ["2.2qF", "2.2qf", "2.2uX", "2.2 qF"])
    async def test_unknown_electrical_unit_is_reported_when_relaxed(self, value):
        result = await search(f"{value} capacitor 0603")
        assert result["total"] > 0
        unsupported = result["parsed"]["detected"]["unsupported_constraints"]
        assert unsupported
        assert all(value in result["relaxed"]["reason"] for value in unsupported)

    @pytest.mark.parametrize("query,frequency,capacitance", [
        ("32.768kHz crystal 12.5pF", "32.768kHz", "12.5pF"),
        ("16MHz crystal 12pF", "16MHz", "12pF"),
        ("8MHz crystal 3225 20pF", "8MHz", "20pF"),
    ])
    async def test_crystal_load_capacitance(self, query, frequency, capacitance):
        from pcbparts_mcp.parsers import parse_capacitance

        result = await search(query)
        explicit = await search(subcategory_name="Crystals", package="3225" if "3225" in query else None,
                                spec_filters=[{"name": "Frequency", "op": "=", "value": frequency},
                                              {"name": "Load Capacitance", "op": "=", "value": capacitance}])
        assert result["total"] == explicit["total"] > 0
        assert result["results"] == explicit["results"]
        assert all(parse_capacitance(p["specs"]["Load Capacitance"]) == pytest.approx(parse_capacitance(capacitance))
                   for p in result["results"])

    @pytest.mark.parametrize("name", ["Quiescent Current", "standby current", "Supply Current (Iq)"])
    async def test_explicit_idle_current(self, name):
        result = await search(subcategory_name="Voltage Regulators - Linear, Low Drop Out (LDO) Regulators",
                              spec_filters=[{"name": name, "op": "<", "value": "10uA"}])
        assert result["total"] > 0
        assert not result.get("ignored_filters")
        for part in result["results"]:
            idle = next(part["specs"][k] for k in ("standby current", "Quiescent Current", "Quiescent Current(Iq)", "Supply Current (Iq)")
                        if k in part["specs"])
            assert parse_current(idle) < 1e-5

    @pytest.mark.parametrize("unit", ["uA", "µA", "μA"])
    async def test_named_idle_current(self, unit):
        result = await search(f"3.3V LDO quiescent current < 10{unit}")
        assert result["total"] > 0
        assert {"name": "Quiescent Current", "op": "<", "value": "10uA"} in result["filters_applied"]["spec_filters"]
        for part in result["results"]:
            assert parse_current(part["specs"]["standby current"]) < 1e-5
            assert covers(part["specs"]["Output Voltage"], 3.3)

    async def test_named_forward_voltage(self):
        result = await search("schottky diode 1A Vf < 0.3V")
        assert result["total"] > 0
        assert {"name": "Vf", "op": "<", "value": "0.3V"} in result["filters_applied"]["spec_filters"]
        for part in result["results"]:
            assert parse_voltage(part["specs"]["Voltage - Forward(Vf@If)"]) < .3
            assert parse_current(part["specs"]["Current - Rectified"]) >= 1

    def test_bare_farads_and_oscillator_mapping(self):
        from pcbparts_mcp.smart_parser import parse_smart_query

        parsed = parse_smart_query("1F 5.5V supercapacitor")
        assert any(f.name == "Capacitance" and f.value == "1F" for f in parsed.spec_filters)
        parsed = parse_smart_query("16MHz oscillator 12pF")
        assert any(f.name == "Load Capacitance" and f.value == "12pF" for f in parsed.spec_filters)


class TestBatch2ReviewFixes:
    async def test_adc_relaxation_names_unsupported_resolution(self):
        result = await search("24bit ADC I2C")
        assert result["total"] > 0
        assert "24bit" in result["relaxed"]["reason"]
        assert all(p["subcategory"] == "Analog to Digital Converters (ADC)" for p in result["results"])

    @pytest.mark.parametrize("query,model", [("AMS1117-3V3", "AMS1117"), ("LM2596S-5V0", "LM2596S-5V0")])
    async def test_model_notation_is_not_rewritten(self, query, model):
        from pcbparts_mcp.smart_parser import parse_smart_query

        parsed = parse_smart_query(query)
        assert parsed.model_number == model
        result = await search(query)
        control = await search(model)
        assert result["total"] == control["total"]
        if query.startswith("AMS"):
            assert result["total"] > 0
        assert all(model.lower() in p["model"].lower() for p in result["results"])

    async def test_inductor_shorthand(self):
        from pcbparts_mcp.parsers import parse_inductance

        result = await search("4u7 inductor 0805")
        assert result["total"] > 0
        assert all(parse_inductance(p["specs"]["Inductance"]) == pytest.approx(4.7e-6) for p in result["results"])


class TestBatch2B:
    @pytest.mark.parametrize("topology", ["buck-boost", "buck boost"])
    async def test_compound_topology(self, topology):
        result = await search(f"3.7V to 3.3V {topology} converter")
        control = await search(subcategory_name="DC-DC Converters", spec_filters=[
            {"name": "Topology", "op": "=", "value": "Buck-Boost"},
            {"name": "Supply Voltage", "op": "=", "value": "3.7V"},
            {"name": "Output Voltage", "op": "=", "value": "3.3V"}])
        assert result["total"] == control["total"] > 0
        for part in result["results"]:
            assert "Buck-Boost" in part["specs"]["Topology"].split("、")
            assert covers(part["specs"]["Voltage - Supply"], 3.7)
            assert covers(part["specs"]["Output Voltage"], 3.3)

    async def test_translator_sides_and_direction(self):
        result = await search("3.3V to 5V bidirectional level shifter")
        assert result["total"] > 0
        for part in result["results"]:
            assert part["specs"]["Channel Type"] == "Bidirectional"
            assert covers(part["specs"]["Voltage - Supply(VCCA)"], 3.3)
            assert covers(part["specs"]["Voltage - Supply(VCCB)"], 5)

    @pytest.mark.parametrize("query,allowed", [
        ("motor driver", {"Motor Driver ICs", "Brushed DC Motor Drivers", "Stepper Motor Driver", "Brushless DC (BLDC) Motor Driver"}),
        ("dc motor driver h-bridge", {"Brushed DC Motor Drivers"}),
        ("stepper driver", {"Stepper Motor Driver"}),
        ("bldc driver", {"Brushless DC (BLDC) Motor Driver"}),
    ])
    async def test_motor_categories(self, query, allowed):
        result = await search(query)
        assert result["total"] > (10 if query == "motor driver" else 0)
        assert all(p["subcategory"] in allowed for p in result["results"])

    @pytest.mark.parametrize("query", ["10k resistor through hole", "through hole resistor 10k"])
    async def test_through_hole_resistor(self, query):
        result = await search(query)
        assert result["total"] > 0
        for part in result["results"]:
            assert part["subcategory"] == "Through Hole Resistors"
            assert parse_resistance(part["specs"]["Resistance"]) == 10000

    async def test_module_memory(self):
        import re

        result = await search("ESP32-S3 module 16MB flash 8MB PSRAM")
        assert result["total"] > 0
        for part in result["results"]:
            assert part["subcategory"] == "WiFi Modules"
            assert part["model"].startswith("ESP32-S3-")
            memory = re.search(r"-N(\d+)R(\d+)", part["model"])
            assert memory and int(memory[1]) >= 16 and int(memory[2]) >= 8

    @pytest.mark.parametrize("query,category,spec,target", [
        ("microcontroller 128KB flash", "Microcontrollers (MCU/MPU/SOC)", "Program Storage Size", 128*1024),
        ("SPI flash 16MB", "NOR FLASH", "Memory Size", 16*1024*1024),
    ])
    async def test_flash_capacity(self, query, category, spec, target):
        result = await search(query)
        assert result["total"] > 0
        for part in result["results"]:
            assert part["subcategory"] == category
            raw = next(part["specs"][k] for k in (spec, "Flash", "Program Memory Size") if k in part["specs"])
            assert parse_memory_size(raw) >= target

    @pytest.mark.parametrize("phrase", ["input up to 24V", "Vin 24V", "24V max input", "from 24V", "up to 24V in"])
    async def test_input_voltage_phrases(self, phrase):
        result = await search(f"LDO 3.3V output {phrase}")
        assert result["total"] > 0
        assert {"name": "Supply Voltage", "op": ">=", "value": "24V"} in result["filters_applied"]["spec_filters"]
        for part in result["results"]:
            assert parse_voltage(part["specs"]["Voltage - Supply"]) >= 24
            assert covers(part["specs"]["Output Voltage"], 3.3)

    @pytest.mark.parametrize("phrase,library", [("basic", "basic"), ("basic part", "basic"), ("no assembly fee", "no_fee"), ("no fee", "no_fee"), ("preferred", "preferred")])
    async def test_library_words(self, phrase, library):
        result = await search(f"{phrase} resistor" if library == "preferred" else f"{phrase} 10k resistor 0603")
        assert result["total"] > 0
        assert result["parsed"]["detected"]["library_type"] == library
        allowed = {"basic", "preferred"} if library == "no_fee" else {library}
        assert all(p["library_type"] in allowed for p in result["results"])

    async def test_cheapest_and_explicit_override(self):
        result = await search("cheapest 3.3V LDO")
        explicit = await search("3.3V LDO", sort_by="price")
        assert result["results"] == explicit["results"]
        assert result["parsed"]["detected"]["sort_by"] == "price"
        override = await search("basic cheapest 10k resistor 0603", library_type="extended", sort_by="stock")
        control = await search("10k resistor 0603", library_type="extended", sort_by="stock")
        assert override["results"] == control["results"]
        assert all(p["library_type"] == "extended" for p in override["results"])

    @pytest.mark.parametrize("query,category", [
        ("USB PD sink trigger 12V", "USB PD"), ("eFuse 5V 2A", "Surge Protection Devices (SPDs)"),
        ("lipo fuel gauge I2C", "Battery Management"), ("MEMS microphone", "MEMS Microphones"),
        ("polymer capacitor", "Polymer Aluminum Capacitors"),
    ])
    async def test_hobby_aliases(self, query, category):
        result = await search(query)
        assert result["total"] > 0
        assert all(p["subcategory"] == category for p in result["results"])
        if "fuel gauge" in query:
            assert all(p["specs"]["The Chip Type"] == "Monitoring IC" for p in result["results"])

    @pytest.mark.parametrize("args", [{"protocol": "1-wire"}, {"measure": "heart rate"}, {"measure": "blood oxygen"}])
    async def test_sensor_aliases(self, args):
        result = await server.sensor_recommend(**args)
        assert result["total"] > 0
        for part in result["results"]:
            if "protocol" in args:
                assert "one_wire" in part["protocols"]
            else:
                assert "biometric" in part["measures"]

    async def test_overlapping_sensor_measure_aliases(self):
        single = await server.sensor_recommend(measure="heart rate", limit=100)
        combined = await server.sensor_recommend(measure=["heart rate", "blood oxygen"], limit=100)
        assert single["total"] > 0
        assert combined["total"] == single["total"]
        assert combined["results"] == single["results"]

    async def test_distinct_sensor_measures_still_require_both(self):
        result = await server.sensor_recommend(measure=["temperature", "humidity"], limit=100)
        assert result["total"] > 0
        assert all({"temperature", "humidity"} <= set(p["measures"]) for p in result["results"])

    async def test_board_tag_alias(self):
        result = await server.board_search(tag="USB-C")
        assert result["total"] > 0
        assert all("usb" in p["tags"] for p in result["results"])

    @pytest.mark.parametrize("args", [{"platform": "esp-idf"}, {"protocol": "nonsense"}, {"measure": "nonsense"}])
    async def test_unknown_sensor_enum(self, args):
        result = await server.sensor_recommend(**args)
        assert "error" in result and result["valid_values"]

    async def test_library_case_and_unknowns(self):
        result = await search("10k resistor 0603", library_type="Basic")
        assert all(p["library_type"] == "basic" for p in result["results"])
        invalid = await server.jlc_search(library_type="nonsense")
        assert "error" in invalid and invalid["valid_values"]
        invalid = await server.board_search(tag="nonsense")
        assert "error" in invalid and invalid["valid_values"]

    async def test_known_unavailable_supercapacitor(self):
        result = await search("1F 5.5V supercapacitor")
        assert result["total"] == 0 and result["results"] == []
        assert result["parsed"]["subcategory"] == "supercapacitors"
        assert "Mouser" in result["hint"] and "DigiKey" in result["hint"]

    @pytest.mark.parametrize("query,model", [
        ("supercapacitor charging IC", None), ("supercapacitor balancing", "CN3125"), ("CN3125 supercapacitor", "CN3125"),
    ])
    async def test_supercapacitor_word_still_finds_other_parts(self, query, model):
        result = await search(query)
        assert result["total"] > 0 and "hint" not in result
        assert not any("capacitor" in p["subcategory"].lower() for p in result["results"])
        if model:
            assert any(p["model"] == model for p in result["results"])

    async def test_library_schema_allows_alias_normalization(self):
        from fastmcp import Client

        async with Client(server.mcp) as client:
            tools = await client.list_tools()
            schema = next(t.inputSchema for t in tools if t.name == "jlc_search")
            choices = schema["properties"]["library_type"]["anyOf"][0]["enum"]
            assert choices == ["basic", "preferred", "no_fee", "extended", "all"]
            for alias, allowed in [("Basic", {"basic"}), ("no-fee", {"basic", "preferred"})]:
                response = await client.call_tool("jlc_search", {"query": "10k resistor 0603", "library_type": alias})
                result = response.data
                assert result["total"] > 0
                assert all(p["library_type"] in allowed for p in result["results"])


class TestAdditionalReviewFixes:
    @pytest.mark.parametrize("query", ["ESP8266 ESP-12F module", "ESP-12F", "ESP8266 ESP-12F SMD"])
    async def test_esp12f_is_not_capacitance(self, query):
        result = await search(query)
        assert result["total"] > 0
        assert any("ESP-12F" in p["model"].upper() for p in result["results"])
        assert not any(f["name"] == "Capacitance" for f in result["parsed"]["spec_filters"])
        assert not any(f["name"] == "Capacitance" for f in result["filters_applied"]["spec_filters"])

    @pytest.mark.parametrize("query,model", [("FUSB302B USB PD", "FUSB302B"), ("STUSB4500 USB PD controller", "STUSB4500")])
    async def test_model_can_relax_query_part_type(self, query, model):
        result = await search(query)
        assert result["total"] > 0
        assert all(p["model"].upper().startswith(model) for p in result["results"])
        assert result["relaxed"] == {
            "dropped_part_type": "USB PD",
            "reason": f"no part matching {model} is listed under USB PD, so every part type was searched",
        }

    @pytest.mark.parametrize("constraint", ["strict", "subcategory_name", "subcategory_id"])
    async def test_model_part_type_retry_keeps_explicit_constraints(self, constraint):
        values = {"strict": True, "subcategory_name": "USB PD",
                  "subcategory_id": server.get_db().resolve_subcategory_name("USB PD")}
        kwargs = {constraint: values[constraint]}
        result = await search("FUSB302B USB PD", **kwargs)
        assert result["total"] == 0
        assert "relaxed" not in result

    async def test_model_part_type_retry_requires_no_parsed_specs(self):
        result = await search("FUSB302B USB PD 5V")
        assert "dropped_part_type" not in result.get("relaxed", {})
