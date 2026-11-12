"""jlc_search on natural-language queries that returned nothing, the wrong parts, or an error
before 0.6.5. Each runs the tool on the real database and checks every result, not one part
number, so the daily data can change under it."""

import json
import re
from pathlib import Path

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.db import get_db
from pcbparts_mcp.parsers import (
    parse_capacitance_max, parse_current, parse_isolation_voltage, parse_frequency, parse_inductance, parse_length_mm, parse_memory_size,
    parse_power, parse_q_factor, parse_resistance, parse_voltage,
)
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


class TestMosfetGateDrive:
    @pytest.mark.parametrize("cue", ["logic level 3.3V", "logic-level 3.3V", "gate drive 3.3V",
                                    "3.3V gate", "3.3V gate voltage", "Vgs 3.3V", "3.3V GPIO", "3.3V MCU",
                                    "3.3V microcontroller",
                                    "driven by 3.3V", "driven from 3.3V", "3.3V drive", "3.3V logic"])
    def test_gate_cues(self, cue):
        from pcbparts_mcp.smart_parser import parse_smart_query

        parsed = parse_smart_query(f"n-channel mosfet {cue} SOT-23")
        assert parsed.gate_drive_v == 3.3
        assert not any(f.name == "Vds" for f in parsed.spec_filters)
        assert not parsed.remaining_text
        if "logic level" in cue or "logic-level" in cue:
            assert any(f.name == "Vgs(th)" and f.operator == "<" and f.value == "2.5V"
                       for f in parsed.spec_filters)

    @pytest.mark.parametrize("query", ["logic level mosfet 3.3V 30V", "mosfet 3.3V gate drive 30V",
                                       "mosfet 30V gate drive 3.3V", "mosfet 30V Vgs 3.3V"])
    def test_second_voltage_keeps_drain_meaning(self, query):
        from pcbparts_mcp.smart_parser import parse_smart_query

        parsed = parse_smart_query(query)
        assert parsed.gate_drive_v == 3.3
        assert any(f.name == "Vds" and f.value == "30V" for f in parsed.spec_filters)

    @pytest.mark.parametrize("query,drive,drain", [
        ("logic level mosfet 30V 10A", None, "30V"),
        ("logic level mosfet 30V 3.3V gate drive", 3.3, "30V"),
        ("12V motor drive mosfet", None, "12V"),
        ("mosfet 10V gate drive", 10, None),
        ("logic level n-channel mosfet 5V", 5, None),
        ("mosfet 20V gate voltage", 20, None),
        ("mosfet 21V gate drive", None, "21V"),
        ("mosfet 12V drive", None, "12V"),
        *[(f"n-channel mosfet 5.1V {cue}", None, "5.1V") for cue in
          ("logic level", "logic-level", "logic", "GPIO", "MCU", "microcontroller", "driven by", "driven from")],
    ])
    async def test_drive_cue_voltage_limits(self, query, drive, drain):
        from pcbparts_mcp.smart_parser import parse_smart_query

        parsed = parse_smart_query(query)
        assert parsed.gate_drive_v == drive
        result = await search(query)
        assert result.get("parsed", {}).get("detected", {}).get("gate_drive_v") == drive
        filters = result["filters_applied"].get("spec_filters", [])
        if drain:
            assert {"name": "Vds", "op": ">=", "value": drain} in filters
        else:
            assert not any(f["name"] == "Vds" for f in filters)
        assert all(("rds_on_at_drive" in part) == (drive is not None) for part in result["results"])
        if "logic level" in query or "logic-level" in query:
            assert {"name": "Vgs(th)", "op": "<", "value": "2.5V"} in filters

    @pytest.mark.parametrize("query,drive,drain", [
        ("logic level n-channel mosfet 3.3V 5A SOT-23", 3.3, None),
        ("n-channel mosfet 3.3V gate drive SOT-23", 3.3, None),
        ("n-channel mosfet 5V gate drive SOT-23", 5, None),
        ("logic level mosfet 30V 3.3V gate drive", 3.3, "30V"),
    ])
    @pytest.mark.parametrize("sort_by,prefer_no_fee", [("stock", True), ("price", False)])
    async def test_evidence_and_sql_paging(self, query, drive, drain, sort_by, prefer_no_fee):
        from pcbparts_mcp.smart_parser import parse_smart_query

        result = await search(query, limit=100, sort_by=sort_by, prefer_no_fee=prefer_no_fee)
        filters = result["filters_applied"]["spec_filters"]
        assert not any(f["name"] == "Vds" and f["value"] in ("3.3V", "5V") for f in filters)
        if drain:
            assert {"name": "Vds", "op": ">=", "value": drain} in filters
        parsed = parse_smart_query(query)
        args = dict(subcategory_name=parsed.subcategory, package=parsed.package,
                    spec_filters=parsed.spec_filters, sort_by=sort_by, prefer_no_fee=prefer_no_fee)
        db = server.get_db()
        ranked = db.search(**args, gate_drive_v=drive, limit=40000)
        control = db.search(**args, limit=40000)
        assert ranked["total"] == control["total"] > 0
        assert ranked["library_type_counts"] == control["library_type_counts"]
        assert {p["lcsc"] for p in ranked["results"]} == {p["lcsc"] for p in control["results"]}
        groups = []
        for part in ranked["results"]:
            # Independently read the catalog's condition/value pairs for every part.
            conditions = []
            for entry in re.split(r'[、,;]', part["specs"].get("RDS(on)", "")):
                _, sep, gate = entry.partition("@")
                match = re.fullmatch(r'(?:VGS=)?([+-]?\d+(?:\.\d*)?)(m?)V', gate) if sep else None
                voltage = abs(float(match[1])) / (1000 if match[2] else 1) if match else None
                if voltage is not None and voltage <= drive:
                    conditions.append((voltage, entry))
            expected = max(conditions, key=lambda pair: pair[0])[1] if conditions else None
            assert part["rds_on_at_drive"] == expected
            groups.append(expected is None)
        assert groups == sorted(groups) and not groups[0] and groups[-1]
        boundary = groups.index(True)
        offset = max(0, boundary - 2)
        page = db.search(**args, gate_drive_v=drive, limit=5, offset=offset)
        assert page["results"] == ranked["results"][offset:offset + 5]
        assert page["total"] == ranked["total"]
        assert result["results"] == ranked["results"][:100]
        adjustments = result["parsed"]["adjusted_filters"]
        assert any("gate drive" in a["reason"] and "rank" in a["now"] for a in adjustments)
        assert not result.get("relaxed")

    async def test_drain_control_and_explicit_filters(self):
        control = await search("n-channel mosfet 30V 5A SOT-23")
        assert {"name": "Vds", "op": ">=", "value": "30V"} in control["filters_applied"]["spec_filters"]
        assert all(parse_voltage(p["specs"]["Drain to Source Voltage"]) >= 30 for p in control["results"])
        assert all("rds_on_at_drive" not in p for p in control["results"])
        explicit = await search("n-channel mosfet 3.3V gate drive SOT-23", spec_filters=[
            {"name": "Vds", "op": ">=", "value": "30V"}])
        assert all(parse_voltage(p["specs"]["Drain to Source Voltage"]) >= 30 for p in explicit["results"])

    async def test_strict_keeps_requirements_and_never_relaxes(self):
        result = await search("n-channel mosfet 3.3V gate drive SOT-23", strict=True)
        assert result["total"] > 0 and not result.get("relaxed")
        assert all("rds_on_at_drive" in p for p in result["results"])
        empty = await server.jlc_search(query="n-channel mosfet 3.3V gate drive impossibleword SOT-23", strict=True)
        assert empty["total"] == 0 and not empty.get("relaxed")

    async def test_explicit_mosfet_context(self):
        result = await search("3.3V gate drive", subcategory_name="MOSFETs", strict=True)
        assert result["total"] > 0 and not result.get("relaxed")
        assert all("rds_on_at_drive" in p for p in result["results"])
        assert not result["filters_applied"].get("spec_filters")


class TestBOMWords:
    @pytest.mark.parametrize("line", [
        pytest.param(line, id=line["ref"], marks=pytest.mark.xfail(reason=line["known_gap"]))
        if "known_gap" in line else pytest.param(line, id=line["ref"])
        for line in json.loads((Path(__file__).parent / "baseline" / "feather_bom.json").read_text(encoding="utf-8"))
    ])
    async def test_feather_bom(self, line):
        result = await search(f'{line["value"]} {line["footprint"]} {line["word"]}', limit=100)
        # A line naming one part records the codes it matched; once none is stocked (BME280 sold
        # out on 2026-11-12) there's nothing to find. Passive lines have no targets and never skip.
        if not result["total"] and line.get("targets"):
            stocked = get_db().get_by_lcsc_batch(line["targets"])
            if not any(stocked.values()):
                pytest.skip(f"no recorded target is stocked any more ({', '.join(line['targets'])})")
        assert result["total"] > 0
        for part in result["results"]:
            assert part["subcategory"] in line["subcategories"]
            if "pins" in line:
                assert re.fullmatch(rf'{line["pins"]}(?:P|[- ]?pins?)?', part["specs"]["Number of Pins"], re.I)
                assert parse_length_mm(part["specs"]["Pitch"]) == pytest.approx(line["pitch"])

    @pytest.mark.parametrize("query,subcategory", [
        ("RGB LED diode", "rgb leds"),
        ("infrared LED diode", "infrared led emitters"),
        ("red LED 0603", "led indication - discrete"),
        ("JSTPH", "wire to board connector"),
        ("JST SH", "wire to board connector"),
    ])
    def test_specific_led_types_and_existing_aliases(self, query, subcategory):
        from pcbparts_mcp.smart_parser import parse_smart_query
        assert parse_smart_query(query).subcategory == subcategory

    @pytest.mark.parametrize("query", ["10kohm RESPACK resistor", "10k respack", "10k resistor pack"])
    def test_respack_is_a_resistor_network(self, query):
        from pcbparts_mcp.smart_parser import parse_smart_query
        parsed = parse_smart_query(query)
        assert parsed.subcategory == "resistor networks, arrays"
        assert parsed.remaining_text == ""

    async def test_footprint_name_is_left_out_of_an_empty_search(self):
        # The footprint name was required text, so this found nothing while "KMR2 switch" finds 12.
        result = await search("KMR2 BTN_KMR2 switch")
        control = await search("KMR2 switch")
        assert result["results"] == control["results"] and result["total"] == control["total"] > 0
        assert result["relaxed"]["dropped_text"] == "BTN_KMR2"
        assert (await search("KMR2 BTN_KMR2 switch", strict=True))["total"] == 0
        assert (await search("BTN_KMR2"))["total"] == 0

    @pytest.mark.parametrize("token,footprint", [
        ("BTN_KMR2", True), ("R_0603_1608Metric", True), ("SW_SPST_PTS645", True),
        # Stocked part numbers with a letters-and-underscore prefix stay part numbers.
        ("SMPC_105K0250DB2315", False), ("BV_SD03C", False), ("RTN_250", False), ("NTC_5D-07", False),
    ])
    def test_footprint_names_are_not_part_numbers(self, token, footprint):
        from pcbparts_mcp.smart_parser import parse_smart_query
        assert bool(server._FOOTPRINT_NAME.fullmatch(token)) is footprint
        query = f"{token} switch"
        assert (token in server._protected_mpn_tokens(query, parse_smart_query(query))) is not footprint

    @pytest.mark.parametrize("interface", ["USB-C", "USB C", "USBC", "Type C"])
    def test_pd_controller_role_wins(self, interface):
        from pcbparts_mcp.smart_parser import parse_smart_query
        result = parse_smart_query(f"{interface} PD controller 20V")
        assert result.subcategory == "usb pd"
        assert result.remaining_text == ""

    def test_decimal_pitch_is_not_a_footprint_pin_count(self):
        from pcbparts_mcp.smart_parser.connectors import extract_connector_series
        assert extract_connector_series("JSTPH2.0") == (None, "JSTPH2.0")

    async def test_explicit_pins_override_footprint_default(self):
        result = await search("JST_SH4_RA 6 pin", limit=100)
        assert result["total"] > 0
        for part in result["results"]:
            assert part["specs"]["Number of Pins"] == "6P"
            assert parse_length_mm(part["specs"]["Pitch"]) == 1

    @pytest.mark.parametrize("query", [
        "red LED 0603 diode", "LED1 0603 diode", "LED12 0603 diode", "LED123 0603 diode",
        "red LED12 0603 diode", "red LED 0603 diodes",
    ])
    @pytest.mark.parametrize("strict", [False, True])
    async def test_led_wins_over_diode(self, query, strict):
        result = await search(query, strict=strict, limit=100)
        assert result["total"] > 0
        assert result["parsed"]["remaining_text"] == ""
        for part in result["results"]:
            assert part["subcategory"] == "LED Indication - Discrete"
            assert part["package"] == "0603"
            if "red" in query:
                assert part["specs"]["Illumination Color"] == "Red"
        if "red" in query:
            assert {"name": "Illumination Color", "op": "=", "value": "Red"} in result["filters_applied"]["spec_filters"]

    @pytest.mark.parametrize("name", ["USB C", "USBC", "Type C", "Type-C", "typec"])
    @pytest.mark.parametrize("suffix", ["", " connector", " receptacle", " socket", " plug"])
    async def test_usb_c_spellings(self, name, suffix):
        result = await search(name + suffix, limit=100)
        control = await search("USB-C connector", limit=100)
        assert result["total"] == control["total"] > 0
        assert result["results"] == control["results"]
        assert {"name": "Connector Type", "op": "=", "value": "Type-C"} in result["filters_applied"]["spec_filters"]
        for part in result["results"]:
            assert part["subcategory"] == "USB Connectors"
            assert part["specs"]["Connector Type"] == "Type-C"


class TestUSBPowerDelivery:
    @pytest.mark.parametrize("query", [
        "USB-C PD controller sink 20V 3A", "USB-C PD sink controller",
        "USB PD controller", "USB PD sink trigger 12V",
        "Type-C power delivery receiver", "USB C power-delivery negotiator",
        "USB-C PD negotiation controller", "USB-C PD negotiating",
    ])
    async def test_controller_category(self, query):
        result = await search(query, limit=100)
        control = await search(subcategory_name="USB PD", limit=100)
        assert result["total"] == control["total"] > 0
        assert {p["lcsc"] for p in result["results"]} == {p["lcsc"] for p in control["results"]}
        assert "relaxed" not in result
        for part in result["results"]:
            assert part["subcategory"] == "USB PD"
        if "sink" in query:
            assert not any(f["name"] in ("Supply Voltage", "Voltage - Supply", "Connector Type")
                           for f in result["filters_applied"]["spec_filters"])

    @pytest.mark.parametrize("prefix", ["", "USB ", "USB-C ", "USB C ", "Type-C ", "USBC "])
    @pytest.mark.parametrize("role,kind", [
        ("sink", "Power Receiver Controller"), ("trigger", "Power Receiver Controller"),
        ("receiver", "Power Receiver Controller"), ("source", "Power Supply Controller"),
    ])
    async def test_role_ranks_without_hiding_unlisted_parts(self, prefix, role, kind):
        result = await search(f"{prefix}PD {role}", limit=100)
        control = await search(subcategory_name="USB PD", limit=100)
        assert result["total"] == control["total"] > 0
        assert result["library_type_counts"] == control["library_type_counts"]
        assert {p["lcsc"] for p in result["results"]} == {p["lcsc"] for p in control["results"]}
        groups = []
        for part in result["results"]:
            assert part["subcategory"] == "USB PD"
            groups.append(kind not in part["specs"].get("Type", "").split("、"))
        assert groups == sorted(groups) and not groups[0] and groups[-1]
        assert any(p["specs"].get("Type", "-") == "-" for p in result["results"])
        assert any("rank" in a["now"] and "many" in a["reason"]
                   for a in result["parsed"]["adjusted_filters"])

    @pytest.mark.parametrize("voltage", [12, 20])
    @pytest.mark.parametrize("sort_by,prefer_no_fee", [("stock", True), ("price", False)])
    async def test_negotiated_voltage_and_sql_paging(self, voltage, sort_by, prefer_no_fee):
        from pcbparts_mcp.smart_parser import parse_smart_query
        query = f"USB-C PD sink trigger {voltage}V"
        result = await search(query, sort_by=sort_by, prefer_no_fee=prefer_no_fee, limit=100)
        control = await search(subcategory_name="USB PD", limit=100)
        assert result["total"] == control["total"]
        assert not result["filters_applied"]["spec_filters"]
        # Role first, negotiated output voltage within each role; missing values stay.
        groups = []
        for part in result["results"]:
            assert part["subcategory"] == "USB PD"
            receiver = "Power Receiver Controller" in part["specs"].get("Type", "").split("、")
            output = any(parse_voltage(v) == voltage for v in part["specs"].get("Output Voltage", "").split("、"))
            groups.append((not receiver, not output))
        assert groups == sorted(groups) and groups[0] == (False, False)
        preferences = parse_smart_query(query).preferred_specs
        args = dict(subcategory_name="USB PD", preferred_specs=preferences,
                    sort_by=sort_by, prefer_no_fee=prefer_no_fee)
        for offset in (0, 5, 10, len(result["results"]) - 3):
            page = server.get_db().search(**args, limit=5, offset=offset)
            assert page["results"] == result["results"][offset:offset + 5]
            assert page["total"] == result["total"]
        assert any("Output Voltage" in a["filter"] and "rank" in a["now"]
                   for a in result["parsed"]["adjusted_filters"])

    async def test_unsupported_current_is_disclosed(self):
        result = await search("USB-C PD controller sink 20V 3A")
        assert any("3A" in a["filter"] and a["now"] is None
                   for a in result["parsed"]["adjusted_filters"])

    @pytest.mark.parametrize("role", ["dual-role controller", "sink source controller"])
    async def test_both_roles_rank_dual_controllers_first(self, role):
        result = await search(f"USB-C PD {role}", limit=100)
        groups = []
        for part in result["results"]:
            assert part["subcategory"] == "USB PD"
            kinds = part["specs"].get("Type", "").split("、")
            groups.append(("Power Receiver Controller" not in kinds, "Power Supply Controller" not in kinds))
        assert groups == sorted(groups) and groups[0] == (False, False)

    @pytest.mark.parametrize("role,kind", [("sink", "Power Receiver Controller"), ("source", "Power Supply Controller")])
    async def test_strict_role_requires_listed_matches(self, role, kind):
        result = await search(f"USB-C PD {role}", strict=True, limit=100)
        assert result["total"] > 0
        for part in result["results"]:
            assert part["subcategory"] == "USB PD"
            assert kind in part["specs"]["Type"].split("、")

    @pytest.mark.parametrize("suffix", ["sink 20V 3A", "sink source controller"])
    async def test_strict_unsupported_constraints_are_not_silently_ranked(self, suffix):
        result = await server.jlc_search(query=f"USB-C PD {suffix}", strict=True, limit=100)
        assert result["error"].startswith("Strict search cannot apply every constraint")
        assert result["total"] == 0 and not result["results"]

    async def test_strict_sink_voltage_requires_output_instead_of_supply(self):
        result = await search("USB-C PD sink 20V", strict=True, limit=100)
        assert result["total"] > 0
        for part in result["results"]:
            assert part["subcategory"] == "USB PD"
            assert "Power Receiver Controller" in part["specs"]["Type"].split("、")
            assert covers(part["specs"]["Output Voltage"], 20)
        assert all(f["name"] not in ("Supply Voltage", "Voltage - Supply")
                   for f in result["filters_applied"]["spec_filters"])

    @pytest.mark.parametrize("query,pins", [
        ("USB-C connector", None), ("USB C", None), ("USB-C 16 pin connector", 16),
    ])
    async def test_connector_controls(self, query, pins):
        result = await search(query, limit=100)
        assert result["total"] > 0
        for part in result["results"]:
            assert part["subcategory"] == "USB Connectors"
            assert part["specs"]["Connector Type"] == "Type-C"
            if pins:
                assert part["specs"]["Number of Contacts"] == f"{pins}P"


class TestFuseRatings:
    @pytest.mark.parametrize("query,package,current", [
        ("1812 fuse", "1812", None),
        ("1A 1812 fuse", "1812", 1),
        ("500mA 1210 fuse", "1210", .5),
        ("1.85A 2920 fuse", "2920", 1.85),
        ("2A 2920 fuse", "2920", 2),
        ("fuse 2920", "2920", None),
        ("1812 fuses", "1812", None),
    ])
    @pytest.mark.parametrize("strict", [False, True])
    async def test_generic_fuse_package_routing(self, query, package, current, strict):
        result = await search(query, strict=strict, limit=100)
        filters = [{"name": "Hold Current", "op": ">=", "value": f"{current}A"}] if current else []
        expected = await search(subcategory_name="Resettable Fuses", package=package,
                                spec_filters=filters, limit=100)
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert result["parsed"]["subcategory"] == "resettable fuses"
        assert not result.get("relaxed")
        assert {"filter": "subcategory: disposable fuses", "now": "resettable fuses",
                "reason": f"{package} fuses in the catalog are all resettable"} in result["parsed"]["adjusted_filters"]
        for part in result["results"]:
            assert part["subcategory"] == "Resettable Fuses"
            assert part["package"] == package
            if current:
                assert parse_current(part["specs"]["Hold Current"]) >= current

    @pytest.mark.parametrize("package", ["1812", "2920", "1210", "2018", "2512", "2016", "3425"])
    @pytest.mark.parametrize("via", ["package", "packages"])
    async def test_explicit_package_routes_and_remaps_ratings(self, package, via):
        args = {via: package if via == "package" else [package]}
        result = await search("1A fuse 6V", strict=True, **args)
        assert result["total"] > 0 and not result.get("relaxed")
        assert result["filters_applied"]["spec_filters"] == [
            {"name": "Hold Current", "op": ">=", "value": "1A"},
            {"name": "Voltage - Max", "op": ">=", "value": "6V"},
        ]
        for part in result["results"]:
            assert part["subcategory"] == "Resettable Fuses" and part["package"] == package
            assert parse_current(part["specs"]["Hold Current"]) >= 1
            assert parse_voltage(part["specs"]["Voltage - Max"]) >= 6

    @pytest.mark.parametrize("query", ["1A fuse", "1A fuses"])
    @pytest.mark.parametrize("strict", [False, True])
    async def test_generic_fuse_with_explicit_package(self, query, strict):
        result = await search(query, package="1812", strict=strict)
        expected = await search(subcategory_name="Resettable Fuses", package="1812", spec_filters=[
            {"name": "Hold Current", "op": ">=", "value": "1A"}])
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert result["parsed"]["subcategory"] == "resettable fuses"
        assert not result.get("relaxed")

    @pytest.mark.parametrize("args,packages", [
        ({"query": "1A fuse 1812 or 2920"}, ["1812", "2920"]),
        ({"query": "1A fuse", "packages": ["1812", "1210"]}, ["1812", "1210"]),
    ])
    async def test_resettable_package_alternatives(self, args, packages):
        result = await search(**args, strict=True, limit=100)
        expected = await search(subcategory_name="Resettable Fuses", packages=packages, spec_filters=[
            {"name": "Hold Current", "op": ">=", "value": "1A"}], limit=100)
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert not result.get("relaxed")

    @pytest.mark.parametrize("package", [None, "0402", "0603", "0805", "1206"])
    @pytest.mark.parametrize("strict", [False, True])
    async def test_generic_fuse_routing_unchanged(self, package, strict):
        result = await search("fuse", package=package, strict=strict)
        expected = await search(subcategory_name="Disposable fuses", package=package)
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert not result.get("parsed", {}).get("adjusted_filters")
        assert not result.get("relaxed")

    @pytest.mark.parametrize("query", ["fuses", "1A fuses", "500mA fuses 6V"])
    @pytest.mark.parametrize("package", [None, "0603", "1206"])
    async def test_plural_fuse_matches_singular(self, query, package):
        # "1A 1812 fuses" used to return ferrite beads: the plural wasn't a part-type word.
        result = await search(query, package=package, strict=True)
        expected = await search(re.sub(r"fuses\b", "fuse", query), package=package, strict=True)
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert result["parsed"]["subcategory"] == "disposable fuses"

    async def test_ptc_package_routing_unchanged(self):
        result = await search("PTC 1812 fuse 1A", strict=True)
        expected = await search(subcategory_name="Resettable Fuses", package="1812", spec_filters=[
            {"name": "Hold Current", "op": ">=", "value": "1A"}])
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert not result.get("parsed", {}).get("adjusted_filters")
        assert not result.get("relaxed")

    @pytest.mark.parametrize("via", ["name", "id"])
    @pytest.mark.parametrize("strict", [False, True])
    async def test_explicit_disposable_package_is_not_rerouted(self, via, strict):
        args = {"subcategory_name": "Disposable fuses"} if via == "name" else {
            "subcategory_id": server.get_db().resolve_subcategory_name("Disposable fuses")}
        result = await search("1812 fuse", strict=strict, **args)
        assert result["total"] == 0
        assert not result.get("parsed", {}).get("adjusted_filters")
        assert not result.get("relaxed")

    async def test_package_routing_does_not_remap_explicit_filters(self):
        filters = [{"name": "Voltage Rating (DC)", "op": ">=", "value": "6V"}]
        result = await search("1A fuse", package="1812", spec_filters=filters)
        assert result["total"] == 0
        assert filters[0] in result["filters_applied"]["spec_filters"]
        assert not any(f["name"] == "Voltage - Max" for f in result["filters_applied"]["spec_filters"])

    @pytest.mark.parametrize("packages", [["1812", "1206"], ["1812", "unknown-package"]])
    async def test_package_alternatives_must_all_be_resettable_only(self, packages):
        result = await search("fuse", packages=packages, strict=True)
        expected = await search(subcategory_name="Disposable fuses", packages=packages)
        assert result["total"] == expected["total"]
        assert result["results"] == expected["results"]
        assert not result.get("parsed", {}).get("adjusted_filters")

    @pytest.mark.parametrize("query,package,subcategory", [
        ("1812 fuse", "1206", "Disposable fuses"),
        ("1206 fuse", "1812", "Resettable Fuses"),
    ])
    async def test_explicit_package_controls_routing(self, query, package, subcategory):
        result = await search(query, package=package)
        expected = await search(subcategory_name=subcategory, package=package)
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert not result.get("relaxed")

    def test_package_routing_uses_cached_catalog_data(self):
        import sqlite3
        from pcbparts_mcp.search.engine import SearchEngine

        with sqlite3.connect(":memory:") as conn:
            conn.execute("CREATE TABLE components (package TEXT, subcategory_id INTEGER, stock INTEGER)")
            conn.executemany("INSERT INTO components VALUES (?, ?, ?)", [
                ("9001", 1, 10), ("9001", 2, 9), ("9002", 1, 10), ("9002", 2, 10), ("9003", 1, 9),
            ])
            engine = SearchEngine(conn, {1: {"name": "Resettable Fuses"}, 2: {"name": "Disposable fuses"}},
                                  {}, {"resettable fuses": 1, "disposable fuses": 2}, {})
            assert engine.packages_are_resettable_fuses(["9001"])
            assert not engine.packages_are_resettable_fuses(["9002"])
            assert not engine.packages_are_resettable_fuses(["9003"])
            assert not engine.packages_are_resettable_fuses(["9001", "unknown"])
            statements = []
            conn.set_trace_callback(statements.append)
            assert engine.packages_are_resettable_fuses(["9001"])
            assert not engine.packages_are_resettable_fuses(["9002"])
            assert not statements

    @pytest.mark.parametrize("query,current,package,voltage", [
        ("15A fuse", 15, None, None),
        ("15.0A fuse", 15, None, None),
        ("500mA fuse 1206", .5, "1206", None),
        ("0.5A fuse 1206", .5, "1206", None),
        ("fuse 2A 250V", 2, None, 250),
        ("M205 2A fuse", 2, None, None),
    ])
    @pytest.mark.parametrize("strict", [False, True])
    async def test_disposable_ratings(self, query, current, package, voltage, strict):
        if strict and query == "M205 2A fuse":
            # Strict mode continues to require the unrecognized M205 text.
            result = await search(query, strict=True)
            assert result["total"] == 0
            return
        result = await search(query, strict=strict, limit=100)
        assert result["total"] > 0
        current_filters = [f for f in result["filters_applied"]["spec_filters"] if f["name"] == "Current Rating"]
        assert len(current_filters) == 1
        assert current_filters[0]["op"] == "="
        assert parse_current(current_filters[0]["value"]) == pytest.approx(current)
        for part in result["results"]:
            assert part["subcategory"] == "Disposable fuses"
            assert parse_current(part["specs"]["Current Rating"]) == pytest.approx(current)
            if package:
                assert part["package"] == package
            if voltage:
                assert parse_voltage(part["specs"]["Voltage Rating (DC)"]) >= voltage

    @pytest.mark.parametrize("subcategory,current,voltage_name,voltage", [
        ("Disposable fuses", 2, "Voltage Rating (DC)", 250),
        ("Automotive Fuses", 15, "Voltage Rating (DC)", 32),
        ("Thermal Fuses (TCO)", 15, "Voltage Rating", 250),
        ("Fuse/Current Protector", 2, "Rated voltage", 250),
    ])
    @pytest.mark.parametrize("strict", [False, True])
    @pytest.mark.parametrize("via", ["name", "id"])
    async def test_explicit_subcategory(self, subcategory, current, voltage_name, voltage, strict, via):
        from pcbparts_mcp.db import get_db
        args = {"subcategory_name": subcategory} if via == "name" else {
            "subcategory_id": get_db().resolve_subcategory_name(subcategory),
        }
        result = await search(f"fuse {current}A {voltage}V", strict=strict, limit=100, **args)
        assert result["total"] > 0
        assert {"name": "Current Rating", "op": "=", "value": f"{current}A"} in result["filters_applied"]["spec_filters"]
        assert {"name": voltage_name, "op": ">=", "value": f"{voltage}V"} in result["filters_applied"]["spec_filters"]
        for part in result["results"]:
            assert part["subcategory"] == subcategory
            assert parse_current(part["specs"]["Current Rating"]) == pytest.approx(current)
            assert parse_voltage(part["specs"][voltage_name]) >= voltage

    async def test_resettable_modifiers_are_consumed(self):
        result = await search("PTC resettable fuse 500mA", limit=100)
        expected = await search(subcategory_name="Resettable Fuses", spec_filters=[
            {"name": "Hold Current", "op": ">=", "value": "500mA"},
        ], limit=100)
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert result["filters_applied"]["spec_filters"] == expected["filters_applied"]["spec_filters"]
        for part in result["results"]:
            assert parse_current(part["specs"]["Hold Current"]) >= .5

    @pytest.mark.parametrize("query,current", [
        ("120mA PTC 0603 fuse", .12),
        ("350mA PTC 1206 fuse", .35),
        ("3A PTC 1206 fuse", 3),
        ("50mA PTC 0603 fuse", .05),
        ("PTC 4.5A 1206 1206 fuse", 4.5),
        ("fuse 1206 500mA polyfuse", .5),
        ("poly fuse 500mA 1206", .5),
        ("500mA polyswitch 1206 fuse", .5),
        ("fuse 500mA 1206 resettable", .5),
    ])
    @pytest.mark.parametrize("strict", [False, True])
    @pytest.mark.parametrize("voltage", [None, 6])
    async def test_resettable_wording(self, query, current, strict, voltage):
        result = await search(query + (f" {voltage}V" if voltage else ""), strict=strict, limit=100)
        assert result["total"] > 0
        assert result["parsed"]["subcategory"] == "resettable fuses"
        filters = result["filters_applied"]["spec_filters"]
        assert any(f["name"] == "Hold Current" and f["op"] == ">="
                   and parse_current(f["value"]) == current for f in filters)
        if voltage:
            assert {"name": "Voltage - Max", "op": ">=", "value": f"{voltage}V"} in filters
        for part in result["results"]:
            assert part["subcategory"] == "Resettable Fuses"
            assert parse_current(part["specs"]["Hold Current"]) >= current
            if voltage:
                assert parse_voltage(part["specs"]["Voltage - Max"]) >= voltage

    async def test_cross_family_retry_remaps_voltage(self):
        result = await search("nSMD005/60V 1206 fuse", limit=100)
        assert result["total"] == 5
        assert {p["lcsc"] for p in result["results"]} == {
            "C2830235", "C70064", "C22435712", "C3035892", "C2924934",
        }
        assert result["relaxed"]["dropped_part_type"] == "Disposable fuses"
        assert {"name": "Voltage - Max", "op": ">=", "value": "60V", "subcategory": "Resettable Fuses"} in result["filters_applied"]["spec_filters"]
        for part in result["results"]:
            assert part["subcategory"] == "Resettable Fuses"
            assert parse_voltage(part["specs"]["Voltage - Max"]) >= 60

    async def test_explicit_cross_family_voltage_is_not_remapped(self):
        filters = [{"name": "Voltage Rating (DC)", "op": ">=", "value": "60V"}]
        result = await search("nSMD005/60V 1206 fuse", spec_filters=filters)
        assert result["total"] == 0
        assert result["filters_applied"]["spec_filters"] == filters

    @pytest.mark.parametrize("query", ["fuse 500mA 30V", "resettable fuse 500mA 30V"])
    @pytest.mark.parametrize("scoped", [False, True])
    def test_mixed_families_map_current_and_voltage_per_subcategory(self, query, scoped):
        from pcbparts_mcp.db import get_db
        from pcbparts_mcp.search.spec_filter import FUSE_ATTRIBUTE_MAP
        from pcbparts_mcp.smart_parser import parse_smart_query

        db = get_db()
        families = ["Disposable fuses", "Resettable Fuses"]
        ids = [db.resolve_subcategory_name(name) for name in families]
        result = db.search(spec_filters=parse_smart_query(query).spec_filters,
                           subcategory_ids=ids if scoped else None, limit=10000)
        assert result["total"] == len(result["results"]) > 0
        assert set(families) <= {p["subcategory"] for p in result["results"]}
        for part in result["results"]:
            mapping = FUSE_ATTRIBUTE_MAP[part["subcategory"].lower()]
            current = parse_current(part["specs"]["Hold Current" if part["subcategory"] == "Resettable Fuses" else "Current Rating"])
            assert current >= .5 if part["subcategory"] == "Resettable Fuses" else current == .5
            assert parse_voltage(part["specs"][mapping["voltage"]]) >= 30

    async def test_explicit_current_operator_kept(self):
        filters = [{"name": "Current Rating", "op": ">=", "value": "15A"}]
        result = await search("15A fuse", spec_filters=filters, limit=100)
        expected = await search(subcategory_name="Disposable fuses", spec_filters=filters, limit=100)
        assert result["total"] == expected["total"] > 0
        assert result["results"] == expected["results"]
        assert any(parse_current(p["specs"]["Current Rating"]) > 15 for p in result["results"])

    @pytest.mark.parametrize("query,wanted", [("15A fuse", 15), ("500mA fuse", .5)])
    def test_current_equality_does_not_admit_nearby_ratings(self, query, wanted):
        import sqlite3
        from pcbparts_mcp.smart_parser import parse_smart_query
        from pcbparts_mcp.search.query_builder import build_spec_filter_clauses

        clauses, params, post_filters, ignored = build_spec_filter_clauses(parse_smart_query(query).spec_filters)
        assert not post_filters and not ignored
        with sqlite3.connect(":memory:") as conn:
            conn.execute("CREATE TABLE components (current_max_a REAL)")
            conn.executemany("INSERT INTO components VALUES (?)", [(wanted,), (wanted * .995,), (wanted * 1.005,)])
            assert conn.execute("SELECT current_max_a FROM components WHERE 1=1 " + " ".join(clauses), params).fetchall() == [(wanted,)]


class TestPackageConstraints:
    @staticmethod
    def body(package):
        dimensions = re.search(
            r"\((\d+(?:\.\d+)?)\s*(?:mm)?\s*[x×]\s*(\d+(?:\.\d+)?)\s*(?:mm)?\)",
            package, re.IGNORECASE,
        )
        assert dimensions, package
        return tuple(sorted(map(float, dimensions.groups())))

    @pytest.mark.parametrize("family", ["QFN", "VQFN", "WQFN", "TQFN", "LQFN", "UQFN",
                                        "UFQFPN", "VFQFPN", "HVQFN", "LQFP", "TQFP", "PQFP",
                                        "SOIC", "SOP", "SO", "BGA", "WLCSP", "DIP"])
    def test_parser_retains_whole_package(self, family):
        from pcbparts_mcp.smart_parser.packages import extract_package
        package = f"{family}-24-EP(4x4mm)" if family not in {"BGA", "DIP"} else f"{family}-24(4x4mm)"
        parsed, remaining, _ = extract_package(f"STM32G0 {package}")
        assert parsed == package.upper()
        assert remaining == "STM32G0"

    @pytest.mark.parametrize("requested,wanted", [
        ("QFN-24-EP(4x4)", {"QFN-24-EP(4x4)", "VQFN-24-EP(4.0x4.0mm)"}),
        ("QFN-24(4x4)", {"QFN-24-EP(4x4)", "VQFN-24-EP(4.0x4.0mm)", "QFN-24(4x4)"}),
        ("QFN-24(3.5x5.5)", {"WQFN-24(5.5x3.5)"}),
        ("SOIC-8-150mil", {"SOIC-8-150mil", "SOP-8-150mil"}),
        ("QFN-24-EP", {"QFN-24-EP(4x4)", "VQFN-24-EP(4.0x4.0mm)"}),
    ])
    def test_sql_checks_whole_catalog_packages(self, requested, wanted):
        import sqlite3
        from pcbparts_mcp.search.query_builder import build_package_clause, index_package_names
        names = ["QFN-24-EP(4x4)", "VQFN-24-EP(4.0x4.0mm)", "QFN-24(4x4)",
                 "QFN-24-EP(4.000001x4)", "VQFN-240-EP(4x4)", "WQFN-24(5.5x3.5)",
                 "SOIC-8-150mil", "SOP-8-150mil", "SOIC-8-300mil", "SOIC-80-150mil", "SOIC-8"]
        if requested == "QFN-24-EP":
            wanted = wanted | {"QFN-24-EP(4.000001x4)"}
        with sqlite3.connect(":memory:") as conn:
            conn.execute("CREATE TABLE components (package TEXT)")
            conn.executemany("INSERT INTO components VALUES (?)", [(name,) for name in names])
            sql, params = build_package_clause([requested], index_package_names(names))
            assert {row[0] for row in conn.execute("SELECT package FROM components WHERE 1=1 " + sql, params)} == wanted

    @pytest.mark.parametrize("via", ["package", "packages", "query"])
    @pytest.mark.parametrize("strict", [False, True])
    async def test_exact_qfn_body_and_pad(self, via, strict):
        package = "QFN-24-EP(4x4)"
        args = {"query": f"DC-DC converter {package}"} if via == "query" else {
            "subcategory_name": "DC-DC Converters", via: [package] if via == "packages" else package,
        }
        result = await search(**args, strict=strict, limit=100)
        assert result["results"]
        for part in result["results"]:
            assert re.match(r"(?:[LWVTU]?QFN|[UV]FQFPN|HVQFN)-24-EP\(", part["package"], re.IGNORECASE)
            assert self.body(part["package"]) == (4, 4)

    @pytest.mark.parametrize("via", ["package", "packages", "query"])
    @pytest.mark.parametrize("strict", [False, True])
    async def test_bare_qfn_family_and_disclosure(self, via, strict):
        args = {"query": "STM32G0 QFN-32"} if via == "query" else {
            "query": "STM32G0", via: ["QFN-32"] if via == "packages" else "QFN-32",
        }
        result = await search(**args, strict=strict, limit=100)
        assert result["results"]
        for part in result["results"]:
            assert part["model"].upper().startswith("STM32G0")
            assert re.match(r"(?:[LWVTU]?QFN|[UV]FQFPN|HVQFN)-32(?:\D|$)", part["package"])
        assert any("QFN-32" in f["filter"] and "any body size" in f["reason"]
                   and "QFN-32-EP(5x5)" in f["reason"]
                   for f in result["parsed"]["adjusted_filters"])

    async def test_bare_qfn_keeps_other_bodies(self):
        result = await search(subcategory_name="DC-DC Converters", package="QFN-24", limit=100)
        packages = {part["package"] for part in result["results"]}
        assert any("(4x4)" in pkg for pkg in packages)
        assert any("(3.5x5.5)" in pkg or "(5.5x3.5)" in pkg for pkg in packages)

    @pytest.mark.parametrize("package,body,pad", [
        ("QFN-24-EP(4x4mm)", (4, 4), True),
        ("QFN-24-EP(4.0x4.0)", (4, 4), True),
        ("VQFN-24(3.5x5.5)", (3.5, 5.5), False),
        ("VQFN-24(5.5x3.5)", (3.5, 5.5), False),
        ("LQFP-48(7x7)", (7, 7), False),
        ("SOIC-8(5x6)", (5, 6), False),
    ])
    @pytest.mark.parametrize("via", ["package", "query"])
    async def test_normalized_body_matches(self, package, body, pad, via):
        args = {via: package}
        result = await search(**args, limit=100, strict=True)
        assert result["results"]
        for part in result["results"]:
            assert self.body(part["package"]) == body
            if pad:
                assert "-EP" in part["package"]

    async def test_soic_pad_without_body(self):
        result = await search(package="SOIC-8-EP", strict=True, limit=100)
        assert result["results"]
        for part in result["results"]:
            # The family rule takes the dash as optional: SOP8-EP (XL4301E1) is an SOP-8 with a pad.
            assert re.match(r"(?:SOIC|SOP|SO)-?8(?:\D|$)", part["package"], re.IGNORECASE)
            assert re.search(r"-EP(?=[(-]|$)", part["package"], re.IGNORECASE)

    @pytest.mark.parametrize("package,remaining", [("SOIC-8(3.9x4.9)", None), ("SO-8-1", "mosfet")])
    @pytest.mark.parametrize("via", ["package", "packages", "query"])
    @pytest.mark.parametrize("strict", [False, True])
    async def test_suffix_absent_from_catalog(self, package, remaining, via, strict):
        args = {"query": f"{package} {remaining or ''}".strip()} if via == "query" else {
            "query": remaining, via: [package] if via == "packages" else package,
        }
        result = await search(**args, strict=strict)
        adjustments = result.get("parsed", {}).get("adjusted_filters", [])
        if strict:
            assert result["total"] == 0
            assert not adjustments
        else:
            bare = package.split("(")[0] if "(" in package else "SO-8"
            expected = await search(query=remaining, package=bare)
            assert result["total"] == expected["total"] > 0
            assert result["results"] == expected["results"]
            assert len(adjustments) == 1
            assert adjustments[0]["filter"].casefold() == f"package: {package}".casefold()
            assert adjustments[0]["now"] == bare
            assert f"no catalog package is {package}".casefold() in adjustments[0]["reason"].casefold()
            assert "any body size" in adjustments[0]["reason"]
            assert "check the body in each part's package" in adjustments[0]["reason"]

    @pytest.mark.parametrize("package", ["QFN-24-EP(4x4)", "LQFP-48(7x7)", "SOIC-8(5x6)"])
    async def test_catalog_match_in_another_subcategory_stays_exact(self, package):
        expected = await search(package=package, strict=True)
        assert expected["total"] > 0
        normal = await search(subcategory_name="MOSFETs", package=package)
        strict = await search(subcategory_name="MOSFETs", package=package, strict=True)
        # Diagnostic timing is request-specific; query semantics must stay identical.
        for response in (normal, strict):
            response.get("why_empty", {}).pop("elapsed_ms", None)
        assert normal == strict
        assert not normal.get("parsed", {}).get("adjusted_filters")

    async def test_package_alternatives_only_fall_back_for_absent_suffix(self):
        packages = ["SOIC-8(3.9x4.9)", "LQFP-48(7x7)"]
        result = await search(packages=packages)
        expected = await search(packages=["SOIC-8", "LQFP-48(7x7)"])
        assert result["total"] == expected["total"]
        assert result["results"] == expected["results"]
        adjustments = result["parsed"]["adjusted_filters"]
        assert len(adjustments) == 1
        assert adjustments[0]["filter"] == f"package: {packages[0]}"


class TestConnectorManufacturer:
    queries = ["JST SH", "jst-ph 2 pin", "JST_SH4_RA", "JSTPH2_BATT",
               "JST 2mm male connector", "JST XH 3p connector"]

    @pytest.mark.parametrize("query", queries)
    @pytest.mark.parametrize("sort_by,prefer_no_fee", [("stock", True), ("price", False)])
    async def test_maker_ranking_keeps_population_and_pages(self, query, sort_by, prefer_no_fee, monkeypatch):
        db = server.get_db()
        original = db.search
        calls = []

        def capture(**kwargs):
            calls.append(kwargs)
            return original(**kwargs)

        with monkeypatch.context() as m:
            m.setattr(db, "search", capture)
            result = await search(query, sort_by=sort_by, prefer_no_fee=prefer_no_fee, limit=100)
        assert result["results"][0]["manufacturer"] == "JST"
        args = {**calls[-1], "limit": 20000}
        assert args["connector_manufacturer"] == "JST"
        ranked = original(**args)
        control = original(**{**args, "connector_manufacturer": None})
        assert len(ranked["results"]) == ranked["total"] == control["total"] > 0
        assert ranked["library_type_counts"] == control["library_type_counts"]
        assert ranked["no_fee_available"] == control["no_fee_available"]
        assert {p["lcsc"] for p in ranked["results"]} == {p["lcsc"] for p in control["results"]}
        groups = [p["manufacturer"] != "JST" for p in ranked["results"]]
        assert groups == sorted(groups) and not groups[0] and groups[-1]
        series = args.get("connector_series")
        if series:
            for maker in (False, True):
                series_groups = [p["specs"].get("Reference Series", "").strip().upper() != series
                                 for p, group in zip(ranked["results"], groups) if group == maker]
                assert series_groups == sorted(series_groups)
        boundary = groups.index(True)
        for limit in (1, 5, 20):
            for offset in (0, max(0, boundary - 2), boundary, len(groups) - 3):
                page = original(**{**args, "limit": limit, "offset": offset})
                assert page["results"] == ranked["results"][offset:offset + limit]
                assert page["total"] == ranked["total"]
        assert result["results"] == ranked["results"][:100]

        def unranked(**kwargs):
            kwargs.pop("connector_manufacturer", None)
            return original(**kwargs)

        with monkeypatch.context() as m:
            m.setattr(db, "search", unranked)
            reply = await search(query, sort_by=sort_by, prefer_no_fee=prefer_no_fee, limit=100)
        assert {k: v for k, v in result.items() if k != "results"} == {
            k: v for k, v in reply.items() if k != "results"
        }

    @pytest.mark.parametrize("query", queries)
    async def test_strict_retains_every_constraint(self, query, monkeypatch):
        db = server.get_db()
        original = db.search
        makers = []

        def unranked(**kwargs):
            makers.append(kwargs.pop("connector_manufacturer", None))
            return original(**kwargs)

        ranked = await server.jlc_search(query=query, strict=True, limit=100)
        with monkeypatch.context() as m:
            m.setattr(db, "search", unranked)
            control = await server.jlc_search(query=query, strict=True, limit=100)
        assert makers == ["JST"]
        assert {k: v for k, v in ranked.items() if k != "results"} == {
            k: v for k, v in control.items() if k != "results"
        }
        assert {p["lcsc"] for p in ranked["results"]} == {p["lcsc"] for p in control["results"]}
        assert not ranked.get("relaxed")

    @pytest.mark.parametrize("query", ["Qwiic", "STEMMA QT", "easyC", "Grove", "adjustable connector"])
    async def test_aliases_without_jst_get_no_maker_rank(self, query, monkeypatch):
        from pcbparts_mcp.smart_parser import parse_smart_query

        # Brand specs are shared defaults; a preceding JST query must not mutate them.
        parse_smart_query("JST " + query)
        parsed = parse_smart_query(query)
        assert parsed.connector_spec is None or parsed.connector_spec.manufacturer is None
        db = server.get_db()
        original = db.search
        makers = []

        def capture(**kwargs):
            makers.append(kwargs.get("connector_manufacturer"))
            return original(**kwargs)

        with monkeypatch.context() as m:
            m.setattr(db, "search", capture)
            await search(query)
        assert makers and not any(makers)

    @pytest.mark.parametrize("manufacturer", ["JST", "DEALON"])
    async def test_explicit_manufacturer_still_filters(self, manufacturer):
        result = await search("JST SH", manufacturer=manufacturer)
        assert result["total"] > 0
        assert all(p["manufacturer"] == manufacturer for p in result["results"])
        assert result["filters_applied"]["manufacturer"] == manufacturer


class TestConnectorRequirements:
    @pytest.mark.parametrize("query,attribute,pins,pitch,series", [
        ("USB-C 16 pin connector", "Number of Contacts", 16, None, None),
        ("USB-C 16 contacts connector", "Number of Contacts", 16, None, None),
        ("JST PH 2 pin connector", "Number of Pins", 2, 2, "PH"),
        ("qwiic connector", "Number of Pins", 4, 1, "SH"),
        ("stemma qt connector", "Number of Pins", 4, 1, "SH"),
        ("grove connector", "Number of Pins", 4, 2, "HY"),
        ("FPC connector 0.5mm 24 pin", "Number of Contacts", 24, .5, None),
        ("JST PH 2P connector", "Number of Pins", 2, 2, "PH"),
        ("JST_SH4_RA", "Number of Pins", 4, 1, "SH"),
        ("JST SH JST_SH4_RA connector", "Number of Pins", 4, 1, "SH"),
        ("JST_PH2", "Number of Pins", 2, 2, "PH"),
        ("JSTPH JSTPH2_BATT connector", "Number of Pins", 2, 2, "PH"),
        ("JST_XH3", "Number of Pins", 3, 2.5, "XH"),
        ("JST_SH_SM04B-SRSS-TB_1x04_P1.00mm_Horizontal", "Number of Pins", 4, 1, "SH"),
        ("JST_SH_SM04B_1x04", "Number of Pins", 4, 1, "SH"),
        ("JST-PH 2 pin", "Number of Pins", 2, 2, "PH"),
        ("wire to board connector 2.5mm 2-pin", "Number of Pins", 2, 2.5, None),
        ("pin header 2.54mm 8 pin", "Number of Pins", 8, 2.54, None),
    ])
    async def test_every_part_meets_pins_and_pitch(self, query, attribute, pins, pitch, series):
        result = await search(query, limit=100)
        assert result["total"] > 0
        applied = {f["name"] for f in result["filters_applied"]["spec_filters"]}
        assert attribute in applied
        assert attribute in {f["name"] for f in result["parsed"]["spec_filters"]}
        if pitch is not None:
            assert "Pitch" in applied
        for part in result["results"]:
            assert re.fullmatch(rf"{pins}(?:P|[- ]?pins?)?", part["specs"][attribute], re.I), part
            if pitch is not None:
                assert parse_length_mm(part["specs"]["Pitch"]) == pytest.approx(pitch), part
        if series:
            from pcbparts_mcp.smart_parser import parse_smart_query
            maker = parse_smart_query(query).connector_spec.manufacturer
            groups = [(bool(maker) and p["manufacturer"] != maker,
                       p["specs"].get("Reference Series", "").upper() != series) for p in result["results"]]
            assert groups[0] == (False, False)
            assert groups == sorted(groups)

    async def test_pitch_spellings_are_equivalent(self):
        results = [await search(f"wire to board connector {pitch} 2 pin")
                   for pitch in ("2mm", "2.0mm", "2.00mm")]
        assert all(r["total"] == results[0]["total"] > 0 for r in results)
        assert all(r["results"] == results[0]["results"] for r in results)

    async def test_explicit_filter_overrides_query_count(self):
        result = await search("JST PH 2 pin connector", spec_filters=[
            {"name": "Number of Pins", "op": "=", "value": "3P"},
        ])
        assert result["total"] > 0
        for part in result["results"]:
            assert part["specs"]["Number of Pins"] == "3P"
            assert parse_length_mm(part["specs"]["Pitch"]) == 2

    @pytest.mark.parametrize("series,pitch", [("PH", "2mm"), ("SH", "1mm")])
    @pytest.mark.parametrize("sort_by,prefer_no_fee", [("stock", True), ("price", False)])
    async def test_series_ranking_keeps_other_parts_and_pages_in_sql(self, series, pitch, sort_by, prefer_no_fee):
        result = await search(f"{series} connector 4 pin", sort_by=sort_by, prefer_no_fee=prefer_no_fee)
        db = server.get_db()
        from pcbparts_mcp.search.spec_filter import ConnectorFilter
        args = dict(subcategory_name="wire to board connector", spec_filters=[
            ConnectorFilter("Number of Pins", "=", "4P"), ConnectorFilter("Pitch", "=", pitch),
        ], sort_by=sort_by, prefer_no_fee=prefer_no_fee)
        control = db.search(**args, limit=10000)
        ranked = db.search(**args, connector_series=series, limit=10000)
        assert result["total"] == ranked["total"] == control["total"] > 0
        assert ranked["library_type_counts"] == control["library_type_counts"]
        assert {p["lcsc"] for p in control["results"]} == {p["lcsc"] for p in ranked["results"]}
        groups = [p["specs"].get("Reference Series", "").upper() != series for p in ranked["results"]]
        assert groups == sorted(groups) and not groups[0] and groups[-1]
        assert any(p["specs"].get("Reference Series", "-") == "-" for p in ranked["results"])
        boundary = groups.index(True)
        offset = max(0, boundary - 2)
        page = db.search(**args, connector_series=series, limit=5, offset=offset)
        assert page["results"] == ranked["results"][offset:offset + 5]
        assert page["total"] == ranked["total"]
        assert result["results"] == ranked["results"][:50]

    async def test_sparse_attribute_is_disclosed(self):
        result = await search("USB-C 16 pin connector 0.5mm")
        assert result["total"] > 0
        assert "Pitch" not in {f["name"] for f in result["filters_applied"]["spec_filters"]}
        assert any("Pitch" in f["filter"] and f["now"] is None
                   for f in result["parsed"]["adjusted_filters"])

    @pytest.mark.parametrize("connector_columns", [False, True])
    @pytest.mark.parametrize("name,values,wanted", [
        ("Number of Pins", ["2", "2P", "2-pin", "20P", "2x20P", "2P+2P", "-"], {"2", "2P", "2-pin"}),
        ("Number of Contacts", ["2", "2 contacts", "20", "2+2", "-"], {"2", "2 contacts"}),
        ("Number of Positions", ["2", "2 positions", "2x20P", "-"], {"2", "2 positions"}),
        ("Number of Positions or Pins", ["2", "2P", "2x20P", "-"], {"2", "2P"}),
        ("Pitch", ["2", "2mm", "2.0mm", "2.00mm", "2.54mm", "20mm", "2mm~3mm", "-"],
         {"2", "2mm", "2.0mm", "2.00mm"}),
    ])
    def test_numeric_sql_normalizes_whole_values_only(self, name, values, wanted, connector_columns):
        import sqlite3
        from pcbparts_mcp.search.query_builder import build_spec_filter_clauses
        from pcbparts_mcp.search.spec_filter import CONNECTOR_FILTER_COLUMNS, ConnectorFilter, SpecFilter, connector_value
        with sqlite3.connect(":memory:") as conn:
            conn.create_function("connector_value", 2, connector_value)
            column = CONNECTOR_FILTER_COLUMNS[name]
            conn.execute(f"CREATE TABLE components (attributes TEXT, {column} REAL)")
            conn.executemany("INSERT INTO components VALUES (?, ?)", [
                (json.dumps([[name, v]]), connector_value(name, v)) for v in values
            ])
            clauses, params, post, ignored = build_spec_filter_clauses(
                [ConnectorFilter(name, "=", "2")], connector_columns=connector_columns,
            )
            assert not post and not ignored
            assert ("json_each" in " ".join(clauses)) is not connector_columns
            rows = conn.execute("SELECT attributes FROM components WHERE 1=1 " + " ".join(clauses), params)
            assert {json.loads(row[0])[0][1] for row in rows} == wanted
            # Explicit values continue using their existing exact string comparison.
            clauses, params, _, _ = build_spec_filter_clauses([SpecFilter(name, "=", "2")])
            rows = conn.execute("SELECT attributes FROM components WHERE 1=1 " + " ".join(clauses), params)
            assert [json.loads(row[0])[0][1] for row in rows] == ["2"]

    @pytest.mark.parametrize("subcategory,name,share,applied", [
        ("Wire To Board Connector", "Number of Pins", .899, False),
        ("Wire To Board Connector", "Number of Pins", .9, True),
        ("FFC, FPC (Flat Flexible) Connector Assemblies", "Number of Contacts", .91, True),
        ("USB Connectors", "Number of Contacts", .849, False),
        ("USB Connectors", "Number of Contacts", .85, True),
    ])
    def test_coverage_gate_and_real_attribute(self, subcategory, name, share, applied):
        from types import SimpleNamespace
        from pcbparts_mcp.search.spec_filter import ConnectorFilter
        db = SimpleNamespace(attribute_share=lambda ids, names: share if name in names else 0,
                             get_subcategory_name=lambda sid: subcategory)
        filters, adjusted = server._fit_parsed_filters(db, [ConnectorFilter("Number of Pins", "=", "2P")], [1])
        assert bool(filters) == applied
        if applied:
            assert filters[0].name == name
        else:
            assert adjusted[0]["now"] is None and "unverified" in adjusted[0]["reason"]


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

    async def test_op_amp_voltage_is_the_single_supply(self):
        """Op amps list their supply as "Single supply" (83%); 5V was left out before 0.8.0."""
        result = await search("op amp 5V rail to rail")
        assert result["total"] > 0
        assert {"name": "Supply Voltage", "op": "=", "value": "5V"} in result["filters_applied"]["spec_filters"]
        assert all(_range_passes(p["specs"]["Single supply"], parse_voltage, "=", 5) for p in result["results"])

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
        # Parts that list several series ("SMA、FAKRA") count too
        assert all("SMA" in p["specs"]["RF Series"].split("、") for p in result["results"])

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

    async def test_model_part_type_retry_allows_parsed_specs(self):
        result = await search("FUSB302B USB PD 5V")
        assert result["results"]
        assert all(p["model"].upper().startswith("FUSB302B") for p in result["results"])
        assert result["relaxed"]["dropped_part_type"] == "USB PD"
        assert result["parsed"]["adjusted_filters"]


class TestShortenedOrderingCodes:
    """#66: retain family hits, but identify and rank the complete requested code."""

    @pytest.mark.parametrize("query,forbidden", [
        ("LM1117-3.3", ("ADJ", "5.0")),
        ("AMS1117-3.3", ("5.0",)),
        ("MCP73831T-2ACI/OT", ("/MC",)),
        ("ATMEGA328P-AU", ("ATMEGA328PB",)),
        ("WS2812B-2020-V6", ("5050",)),
    ])
    async def test_every_result_has_the_right_match_group(self, query, forbidden):
        result = await search(query, limit=100)
        counts = result["mpn_matches"]
        assert counts["part_number"] == query
        assert sum(counts[t] for t in ("full", "same_suffix", "family")) == result["total"]
        assert counts["full"] > 0 and counts["family"] > 0
        ranks = {"full": 0, "same_suffix": 1, "family": 2}
        groups = [ranks[p["mpn_match"]] for p in result["results"]]
        assert groups == sorted(groups)
        for part in result["results"]:
            if any(text in part["model"].upper() for text in forbidden):
                assert part["mpn_match"] == "family", part
            if part["mpn_match"] == "full":
                from pcbparts_mcp.search.mpn import mpn_key
                assert mpn_key(part["model"]).startswith(mpn_key(query)), part
            elif part["mpn_match"] == "same_suffix":
                requested = re.split(r"[-/_\s]+", query.upper())
                actual = re.split(r"[-/_\s]+", part["model"].upper())
                assert actual[0] == requested[0] or (requested[0][-1].isdigit()
                    and re.fullmatch(re.escape(requested[0]) + r"[A-Z]+", actual[0])), part
                assert all(segment in actual[1:] for segment in requested[1:]), part
        # The first page may not contain all the precise matches; counts cover the population.
        small = await search(query, limit=1)
        assert small["mpn_matches"] == counts
        assert small["results"] == result["results"][:1]

    @pytest.mark.parametrize("sort_by,prefer_no_fee", [("stock", True), ("price", True), ("price", False)])
    def test_paging_and_existing_order_within_every_group(self, sort_by, prefer_no_fee):
        db = server.get_db()
        args = dict(query="LM1117", sort_by=sort_by, prefer_no_fee=prefer_no_fee)
        control = db.search(**args, limit=1000)
        ranked = db.search(**args, part_number="LM1117-3.3", limit=1000)
        assert ranked["total"] == control["total"] > 0
        assert ranked["library_type_counts"] == control["library_type_counts"]
        assert {p["lcsc"] for p in ranked["results"]} == {p["lcsc"] for p in control["results"]}
        groups = {p["lcsc"]: p["mpn_match"] for p in ranked["results"]}
        expected = []
        for group in ("full", "same_suffix", "family"):
            expected.extend(p["lcsc"] for p in control["results"] if groups[p["lcsc"]] == group)
        assert [p["lcsc"] for p in ranked["results"]] == expected
        pages = []
        for offset in range(0, ranked["total"], 7):
            page = db.search(**args, part_number="LM1117-3.3", limit=7, offset=offset)
            assert page["mpn_matches"] == ranked["mpn_matches"]
            pages.extend(page["results"])
        assert pages == ranked["results"]

    @pytest.mark.parametrize("query", ["ESP32-S3-WROOM-1-N16R8", "LM358",
                                      "STM32 microcontroller LQFP-48 128KB flash",
                                      "8MHz SOT-416 crystal", "AEC-Q100 CAN transceiver", "M205 2A fuse"])
    async def test_unshortened_and_descriptive_queries_have_no_match_metadata(self, query):
        result = await search(query)
        assert "mpn_matches" not in result
        assert all("mpn_match" not in p for p in result["results"])

    @pytest.mark.parametrize("mpn,token,group", [
        ("LM1117IMPX-3.3/NOPB", "LM1117-3.3", "same_suffix"),
        ("LM1117S-3.3", "LM1117-3.3", "same_suffix"),
        ("LM1117S-3.30", "LM1117-3.3", "family"),
        ("LM1117S-3.3V", "LM1117-3.3", "family"),
        ("LM1117MPX-ADJ/NOPB", "LM1117-3.3", "family"),
        ("ATMEGA328PB-AU", "ATMEGA328P-AU", "family"),
        ("ATMEGA328P-AUR", "ATMEGA328P-AU", "full"),
        ("MCP73831T-2ACI/OT-HXY", "MCP73831T-2ACI/OT", "full"),
        ("MCP73831T-2ACI/MC", "MCP73831T-2ACI/OT", "family"),
        ("mcp73831t_2aci ot-hxy", "MCP73831T-2ACI/OT", "full"),
        ("WS2812B-V6-2020", "WS2812B-2020-V6", "same_suffix"),
        ("WS2812B-5050-V6", "WS2812B-2020-V6", "family"),
        ("LM1117S-3#3", "LM1117-3.3", "family"),
    ])
    def test_ordering_segments_are_preserved(self, mpn, token, group):
        from pcbparts_mcp.search.mpn import MPN_MATCH_NAMES, mpn_match_rank
        assert MPN_MATCH_NAMES[mpn_match_rank(mpn, token)] == group

    def test_post_filtered_counts_and_paging(self, monkeypatch):
        from pcbparts_mcp.search import engine
        from pcbparts_mcp.search.spec_filter import SpecFilter
        db = server.get_db()
        args = dict(query="LM1117", spec_filters=[SpecFilter("Output Voltage", "=", "3.3V")])
        control = db.search(**args, limit=1000)
        ranked = db.search(**args, part_number="LM1117-3.3", limit=1000)
        assert ranked["total"] == control["total"] > 0
        for group in ("full", "same_suffix", "family"):
            assert ranked["mpn_matches"][group] == sum(p["mpn_match"] == group for p in ranked["results"])
        page = db.search(**args, part_number="LM1117-3.3", limit=3, offset=2)
        assert page["results"] == ranked["results"][2:5]
        assert page["mpn_matches"] == ranked["mpn_matches"]
        monkeypatch.setattr(engine, "POST_FILTER_SCAN_ROWS", 2)
        partial = db.search(**args, part_number="LM1117-3.3", limit=100)
        assert partial["counts_complete"] is False
        assert sum(partial["mpn_matches"][g] for g in ("full", "same_suffix", "family")) == partial["total"]

    async def test_public_price_sort_uses_match_groups_first(self):
        result = await search("LM1117-3.3", sort_by="price", prefer_no_fee=False, limit=100)
        control = server.get_db().search(query="LM1117", part_number="LM1117-3.3",
                                         sort_by="price", prefer_no_fee=False, limit=100)
        assert result["results"] == control["results"]
        assert result["mpn_matches"] == control["mpn_matches"]


class TestRelease074:
    """LCSC codes in a search, Height on electrolytics, digital pots and ideal diodes, female header
    layouts, barrel jack sizes and comparison signs (0.7.4)."""

    async def test_pasted_lcsc_code_finds_only_that_part(self):
        # "C1525"* also matched every LCSC code starting with C1525 (C15250-C15259...).
        if not server.get_db().get_by_lcsc_batch(["C1525"])["C1525"]:
            pytest.skip("C1525 is no longer stocked")
        for query in ("C1525", "c1525"):
            result = await search(query)
            assert [p["lcsc"] for p in result["results"]] == ["C1525"]

    async def test_lcsc_shaped_part_number_still_matches(self):
        # C1815 is also the 2SC1815's common part number.
        result = await search("C1815")
        assert any(p["lcsc"] != "C1815" and "C1815" in p["model"].upper() for p in result["results"])
        assert all(p["lcsc"] == "C1815" or "C1815" in p["model"].upper() for p in result["results"])

    async def test_several_lcsc_codes(self):
        assert (await search("C1525 C25804"))["total"] == 0  # every term, like any other query
        either = await search("C1525 C25804", match_all_terms=False)
        assert {p["lcsc"] for p in either["results"]} <= {"C1525", "C25804"} and either["total"]

    async def test_reference_designator_is_not_an_lcsc_code(self):
        # The C1 in a BOM line keeps its old prefix match; as an exact code it kept only
        # TDK's C1005... part numbers.
        result = await search("C1 100nF 0402")
        assert result["total"] > 20
        assert any(not p["model"].upper().startswith("C1") for p in result["results"])

    async def test_failed_search_sql_returns_its_error(self, monkeypatch):
        import sqlite3

        db = server.get_db()
        db.search(query="10k resistor", limit=1)
        conn = db._search_engine._conn

        class FailingFTS:
            def execute(self, sql, params=()):
                if "components_fts" in sql:
                    raise sqlite3.OperationalError("fts5: syntax error")
                return conn.execute(sql, params)

            def __getattr__(self, name):
                return getattr(conn, name)

        monkeypatch.setattr(db._search_engine, "_conn", FailingFTS())
        result = await server.jlc_search(query="LM358")  # a text search, so the FTS query runs
        assert result["error"] == "Search failed: query too complex. Reduce the number of filters."

    @pytest.mark.parametrize("subcategory", ["Aluminum Electrolytic Capacitors - SMD",
                                             "Aluminum Electrolytic Capacitors - Leaded"])
    async def test_height_reads_seated_height(self, subcategory):
        # Electrolytics that list only "Height - Seated (Max)" were missing, with a warning that
        # few parts list Height.
        def args(name):
            return dict(subcategory_name=subcategory, spec_filters=[{"name": name, "op": "<=", "value": "7mm"}])
        height = await search(**args("Height"))
        seated = await search(**args("Height - Seated (Max)"))
        assert height["total"] == seated["total"] > 0
        assert "ignored_filters" not in height

    async def test_digital_potentiometer(self):
        # Returned mechanical trimpots: "digital" was left out and "potentiometer" won.
        result = await search("digital potentiometer 10k I2C")
        assert result["total"] > 0
        for part in result["results"]:
            assert part["subcategory"] == "Digital Potentiometers"
            assert parse_resistance(part["specs"]["Resistance Value (Ohms)"]) == 10_000
            assert "I2C" in part["specs"]["Interface"]
        assert (await search("10k potentiometer"))["results"][0]["subcategory"] == "Potentiometers, Variable Resistors"

    @pytest.mark.parametrize("query, allowed", [
        ("ideal diode controller 12V", {"ORing Controllers"}), ("oring controller", {"ORing Controllers"}),
        # Since 0.8.0 also the single-chip ideal diodes filed as Power Distribution Switches
        ("ideal diode", {"ORing Controllers", "Power Distribution Switches"})])
    async def test_ideal_diode_controller(self, query, allowed):
        # Returned 1N4148-type switching diodes rated 12V and up.
        result = await search(query)
        assert result["total"] > 0
        assert all(p["subcategory"] in allowed for p in result["results"])

    @pytest.mark.parametrize("query,layout", [("1x8 female header", "1x8P"),
                                              ("2x20 female header 2.54mm", "2x20P")])
    async def test_female_header_layout(self, query, layout):
        # Female headers list Holes Structure, not the pin headers' Pin Structure, so 1x4 and
        # 1x6 headers came first.
        result = await search(query)
        assert result["total"] > 0
        assert all(p["specs"]["Holes Structure"] == layout for p in result["results"])
        pin_headers = await search(query.replace("female", "pin"))
        assert all(p["specs"]["Pin Structure"] == layout for p in pin_headers["results"])

    async def test_barrel_jack_plug_size_is_reported(self):
        # Jacks list contact diameters (a 5.5x2.1mm jack: 6.4mm and a 2mm pin), not the plug size,
        # and the size was dropped without a word.
        result = await search("5.5x2.1mm barrel jack")
        assert any(note.startswith("5.5x2.1mm:") for note in result["parsed"]["detected"]["not_searched"])

    async def test_comparison_sign_keeps_its_direction(self):
        # "< 25V" became Voltage Rating >= 25V.
        result = await search("capacitor 10uF > 10V < 25V")
        filters = {(f["name"], f["op"], f["value"]) for f in result["filters_applied"]["spec_filters"]}
        assert {("Voltage Rating", ">=", "10V"), ("Voltage Rating", "<", "25V")} <= filters
        assert result["total"] > 0
        assert all(10 <= parse_voltage(p["specs"]["Voltage Rating"]) < 25 for p in result["results"])
        assert "relaxed" not in result
        mosfets = await search("mosfet Vds < 30V")
        assert all(parse_voltage(p["specs"]["Drain to Source Voltage"]) < 30 for p in mosfets["results"])

    @pytest.mark.parametrize("query", ["1n >50V 50V 0603 capacitor", "100nF 50V 0603 capacitor",
                                       "schottky diode 1A Vf < 0.3V"])
    def test_comparison_sign_in_the_default_direction(self, query):
        from pcbparts_mcp.smart_parser import parse_smart_query
        before = {(f.name, f.operator) for f in parse_smart_query(query).spec_filters}
        assert ("Voltage Rating", ">") not in before and ("If", "<") not in before

    @pytest.mark.parametrize("query", ["mosfet < 10mΩ SOT-23", "capacitor < 10µF 0603"])
    def test_comparison_sign_before_unicode_units(self, query):
        # The sign was looked up next to the value as read (10mohm), so "< 10mΩ" lost it.
        from pcbparts_mcp.smart_parser import parse_smart_query
        assert any(f.operator == "<" for f in parse_smart_query(query).spec_filters)

    @pytest.mark.parametrize("query,spec,limit", [("LDO 3.3V < 1uA", "standby current", 1e-6),
                                                  ("LDO 3.3V 1µA", "standby current", 1e-6),
                                                  ("buck converter 10uA", "Quiescent Current", 1e-5)])
    async def test_microamps_on_a_regulator_are_quiescent_current(self, query, spec, limit):
        # No LDO or DC-DC converter lists an output current under 1mA: "< 1uA" found none, and
        # "1uA" (Output Current >= 1uA) passed every LDO.
        result = await search(query)
        assert ("Quiescent Current", "<=") in {(f["name"], f["op"]) for f in result["filters_applied"]["spec_filters"]}
        assert result["total"] > 0
        assert all(parse_current(p["specs"][spec]) <= limit for p in result["results"])
        output = await search("LDO 3.3V 500mA")
        assert ("Output Current", ">=", "500mA") in {
            (f["name"], f["op"], f["value"]) for f in output["filters_applied"]["spec_filters"]}

    @pytest.mark.parametrize("query,spec,op,limit", [("mosfet 10mohm", "RDS(on)", "<=", 0.010),
                                                     ("mosfet < 10mΩ SOT-23", "RDS(on)", "<", 0.010),
                                                     ("mosfet > 10mohm", "RDS(on)", ">", 0.010),
                                                     ("load switch 50mohm", "RDS(on)", "<=", 0.050),
                                                     ("inductor 10uH 100mohm", "DC Resistance(DCR)", "<=", 0.100),
                                                     ("inductor 10uH > 100mohm", "DC Resistance(DCR)", ">", 0.100)])
    async def test_milliohms_are_on_resistance_or_dcr(self, query, spec, op, limit):
        # These parts don't list Resistance, so the value was left out. A written sign keeps its
        # direction on the spec the value moves to.
        result = await search(query)
        assert (spec, op) in {(f["name"], f["op"]) for f in result["filters_applied"]["spec_filters"]}
        assert result["total"] > 0
        passes = {"<=": lambda v: v <= limit * (1 + 1e-9), "<": lambda v: v < limit, ">": lambda v: v > limit}[op]
        assert all(passes(parse_resistance(p["specs"][spec])) for p in result["results"])

    @pytest.mark.parametrize("query,spec,op", [("digital potentiometer < 10k", "Resistance Value (Ohms)", "<"),
                                               ("high side switch < 4A", "Maximum Continuous Current", "<"),
                                               ("high side switch 4A", "Maximum Continuous Current", ">="),
                                               ("level shifter 3.3V", "Supply Voltage", "=")])
    async def test_comparison_sign_survives_a_fallback_spec(self, query, spec, op):
        # The fallback spec took its own operator: "high side switch < 4A" searched >= 4A.
        result = await search(query)
        assert (spec, op) in {(f["name"], f["op"]) for f in result["filters_applied"]["spec_filters"]}
        assert result["total"] > 0

    @pytest.mark.parametrize("query,subcategory,ohms", [("600ohm 0603", "Ferrite Beads", 600),
                                                        ("90ohm", "Common Mode Filters", 90)])
    async def test_ohms_on_a_bead_or_common_mode_filter_are_impedance(self, query, subcategory, ohms):
        # Beads and common mode filters list DCR too, so the DCR fallback read "600ohm" as DCR <= 600Ohm
        # when the part type was passed as subcategory_name. "ferrite bead 600ohm" already meant impedance.
        result = await search(query, subcategory_name=subcategory)
        filters = {(f["name"], f["op"]) for f in result["filters_applied"]["spec_filters"]}
        assert ("Impedance @ Frequency", "=") in filters
        assert ("DC Resistance(DCR)", "<=") not in filters
        assert result["total"] > 0
        assert all(parse_resistance(p["specs"]["Impedance @ Frequency"].split("@")[0]) == ohms for p in result["results"])

    async def test_milliohms_on_a_bead_are_dcr(self):
        # No bead lists an impedance under 1 ohm (apart from "0Ω@100MHz"), so "100mohm" is its DCR
        result = await search("100mohm", subcategory_name="Ferrite Beads")
        assert ("DC Resistance(DCR)", "<=") in {(f["name"], f["op"]) for f in result["filters_applied"]["spec_filters"]}
        assert result["total"] > 0
        assert all(parse_resistance(p["specs"]["DC Resistance(DCR)"]) <= 0.1 * (1 + 1e-9) for p in result["results"])

    @pytest.mark.parametrize("query", ["1m 250mA inductor", "inductor 1R0", "mosfet 10m"])
    async def test_resistance_without_an_ohm_unit_is_not_on_resistance_or_dcr(self, query):
        # A value without an ohm unit isn't an RDS(on)/DCR limit. Since 0.8.0 an inductor query's
        # "1m" is 1mH and "1R0" 1.0uH; "mosfet 10m" is still left out.
        result = await search(query)
        names = {f["name"] for f in result["filters_applied"]["spec_filters"]}
        assert not names & {"RDS(on)", "DC Resistance(DCR)"}
        if "inductor" in query:
            assert "Inductance" in names
        else:
            assert any(a["filter"].startswith("Resistance") and a["now"] is None
                       for a in result["parsed"]["adjusted_filters"])


class TestRelease078:
    """Feedback from a GNSS splitter design session (2026-10-31): ESD capacitance (#67), RF inductor
    SRF and Q, and SMA read as the diode package (#77)."""

    async def test_esd_capacitance_is_a_numeric_budget(self):
        # Junction Capacitance <= 0.5pF was ignored as non-numeric
        result = await search("ESD", spec_filters=[
            {"name": "Junction Capacitance", "op": "<=", "value": "0.5pF"},
            {"name": "Reverse Stand-Off Voltage (Vrwm)", "op": ">=", "value": "6V"},
        ])
        assert not result.get("ignored_filters")
        assert result["total"] > 0
        for p in result["results"]:
            assert parse_capacitance_max(p["specs"]["Junction Capacitance"]) <= 0.5e-12 * (1 + 1e-9)
            assert parse_voltage(p["specs"]["Reverse Stand-Off Voltage (Vrwm)"]) >= 6

    @pytest.mark.parametrize("query", ["0.2pF ESD", "ESD diode 5V 0.2pF", "TVS diode 0.2pF"])
    async def test_esd_query_capacitance_is_junction_capacitance(self, query):
        # "0.2pF ESD" filtered on Capacitance, which no ESD part lists, so the value was dropped
        result = await search(query)
        filters = {(f["name"], f["op"]) for f in result["filters_applied"]["spec_filters"]}
        assert ("Junction Capacitance", "<=") in filters
        assert ("Capacitance", "=") not in filters
        assert result["total"] > 0
        assert all(parse_capacitance_max(p["specs"]["Junction Capacitance"]) <= 0.2e-12 * (1 + 1e-9)
                   for p in result["results"])

    async def test_bare_values_with_an_explicit_esd_subcategory(self):
        result = await search("5V 0.2pF", subcategory_name="ESD and Surge Protection (TVS/ESD)")
        filters = {(f["name"], f["op"]) for f in result["filters_applied"]["spec_filters"]}
        assert filters == {("Reverse Stand-Off Voltage (Vrwm)", ">="), ("Junction Capacitance", "<=")}
        assert result["total"] > 0

    async def test_esd_query_voltage_is_vrwm(self):
        result = await search("ESD diode 5V")
        filters = {(f["name"], f["op"]) for f in result["filters_applied"]["spec_filters"]}
        assert ("Reverse Stand-Off Voltage (Vrwm)", ">=") in filters
        assert ("Voltage Rating", ">=") not in filters

    async def test_two_junction_capacitances_compare_by_the_larger(self):
        result = await search(None, subcategory_name="ESD and Surge Protection (TVS/ESD)", limit=100,
                              spec_filters=[{"name": "Junction Capacitance", "op": "<=", "value": "0.4pF"}])
        assert result["total"] > 0
        assert not any(p["specs"]["Junction Capacitance"] == "0.3pF、0.6pF" for p in result["results"])

    async def test_self_resonant_frequency_filter(self):
        result = await search("68nH", subcategory_name="Inductors (SMD)",
                              spec_filters=[{"name": "Frequency - Self Resonant", "op": ">=", "value": "2GHz"}])
        assert not result.get("ignored_filters")
        assert result["total"] > 0
        assert all(parse_frequency(p["specs"]["Frequency - Self Resonant"]) >= 2e9 for p in result["results"])

    async def test_q_filter(self):
        result = await search("68nH", subcategory_name="Inductors (SMD)",
                              spec_filters=[{"name": "Q @ Frequency", "op": ">=", "value": "30"}])
        assert not result.get("ignored_filters")
        assert result["total"] > 0
        assert all(parse_q_factor(p["specs"]["Q @ Frequency"]) >= 30 for p in result["results"])

    @pytest.mark.parametrize("query, series", [("SMA edge mount connector", "SMA"), ("SMA jack PCB mount", "SMA"),
                                               ("SMB connector", "SMB"), ("SMA female", "SMA")])
    async def test_sma_with_connector_words_is_the_rf_series(self, query, series):
        # "SMA edge mount connector" searched the DO-214AC diode package and found nothing
        result = await search(query)
        assert result["filters_applied"]["package"] is None
        assert result["filters_applied"]["subcategory_resolved"] == "Coaxial Connectors (RF)"
        assert result["total"] > 0
        assert all(series in p["specs"]["RF Series"].split("、") for p in result["results"])

    async def test_sma_in_an_explicit_coax_subcategory(self):
        # The explicit subcategory didn't stop the package reading; "50 ohm" also implied chip resistors
        result = await server.jlc_search(query="SMA female right angle through hole 50 ohm",
                                         subcategory_name="Coaxial Connectors (RF)", limit=20)
        assert result["filters_applied"]["package"] is None
        assert ("RF Series", "=", "SMA") in {(f["name"], f["op"], f["value"])
                                             for f in result["filters_applied"]["spec_filters"]}
        if result["total"] == 0:
            # Words aren't left out with an explicit subcategory; the hint says which found nothing
            assert "without them" in result["hint"]

    @pytest.mark.parametrize("query", ["SMA schottky diode 40V", "TVS SMA 24V", "SS34 SMA", "SMB rectifier"])
    async def test_sma_without_connector_words_is_still_the_package(self, query):
        result = await search(query)
        assert result["filters_applied"]["package"] in ("SMA", "SMB")

    async def test_explicit_diode_subcategory_keeps_the_package(self):
        result = await search("SMA female", subcategory_name="Schottky Diodes")
        assert result["filters_applied"]["package"] == "SMA"

    @staticmethod
    def descriptions(result) -> dict[str, str]:
        """The text a query word is matched against (the full-text index: part number, maker, description)."""
        import sqlite3
        codes = [p["lcsc"] for p in result["results"]]
        with sqlite3.connect(server.get_db().db_path) as conn:
            rows = conn.execute("SELECT lcsc, mpn || ' ' || manufacturer || ' ' || description FROM components "
                                f"WHERE lcsc IN ({','.join('?' * len(codes))})", codes).fetchall()
        return dict(rows)

    @pytest.mark.parametrize("subcategory, query, words", [
        ("RF Cables", "IPEX to SMA 10cm", ("IPEX", "SMA", "10CM")),
        ("RF Cables", "SMA IPEX", ("IPEX", "SMA")),
        ("Antennas", "SMA 2.4GHz", ("SMA",)),
        ("RF Antennas", "SMA", ("SMA",)),
    ])
    async def test_sma_in_rf_cables_and_antennas_is_the_connector(self, subcategory, query, words):
        # 2026-11-02 report: "SMA IPEX" in RF Cables searched the SMA diode package and found nothing,
        # and as an RF Series filter (which these parts don't list) SMA was dropped, matching every part
        result = await search(query, subcategory_name=subcategory)
        assert result["filters_applied"]["package"] is None
        assert result["total"] > 0
        texts = self.descriptions(result)
        assert len(texts) == len(result["results"])
        for lcsc, text in texts.items():
            assert all(word in text.upper() for word in words), (lcsc, text)

    @pytest.mark.parametrize("query", ["IPEX to SMA cable", "SMA pigtail", "u.fl pigtail", "RF cable 10cm",
                                       "SMA to IPEX cable 15cm", "coaxial cable"])
    async def test_rf_cable_queries_search_rf_cables(self, query):
        # "IPEX to SMA cable" searched coax connectors with the SMA diode package: one result
        result = await search(query)
        assert result["filters_applied"]["package"] is None
        assert result["filters_applied"]["subcategory_resolved"] == "RF Cables"
        assert result["total"] > 0
        assert all(p["subcategory"] == "RF Cables" for p in result["results"])
        series = [w for w in ("IPEX", "SMA", "U.FL") if w.lower() in query.lower()]
        for lcsc, text in self.descriptions(result).items():
            text = text.upper().replace("UFL", "U.FL")
            assert all(w in text or (w == "U.FL" and "IPEX" in text) for w in series) or not series, (lcsc, text)

    async def test_hint_names_words_that_zero_a_search_with_filters(self):
        result = await search("ESD purple elephant",
                              spec_filters=[{"name": "Junction Capacitance", "op": "<=", "value": "0.5pF"}])
        assert result["total"] == 0
        assert '"purple elephant"' in result["hint"]
        assert "without them" in result["hint"]

    async def test_no_hint_when_the_words_are_not_the_problem(self):
        result = await search("ESD purple elephant", strict=True,
                              spec_filters=[{"name": "Junction Capacitance", "op": "<=", "value": "0.5pF"}])
        assert "without them" not in (result.get("hint") or "")


class TestRelease079:
    """Feedback from an ESP32 field-node design session (2026-11-01): "addressable RGB LED" searched
    plain RGB LEDs and dropped the word; "LED driver" searched indicator LEDs."""

    @pytest.mark.parametrize("query", ["addressable RGB LED", "smart RGB LED", "individually addressable LED",
                                       "addressable RGB LEDs 2020", "WS2812B LED", "SK6812 mini LED"])
    async def test_addressable_led_is_the_built_in_ic_subcategory(self, query):
        result = await search(query)
        assert result["parsed"]["subcategory"] == "rgb leds(built-in ic)"
        assert result["total"] > 0
        # A part number's parts in other LED subcategories join it (WS2812B-V6 is filed as an indicator LED)
        assert all(p["subcategory"] == "RGB LEDs(Built-in IC)" or re.search(r"ws2812|sk6812", p["model"], re.I)
                   for p in result["results"])
        dropped = (result.get("relaxed") or {}).get("dropped_text", "").lower()
        assert not re.search(r"addressable|smart|ws2812|sk6812", dropped)

    async def test_addressable_led_supply_voltage(self):
        result = await search("addressable RGB LED 3.3V", match_all_terms=False)
        assert {"name": "Supply Voltage", "op": "=", "value": "3.3V"} in result["filters_applied"]["spec_filters"]
        assert result["total"] > 0
        for p in result["results"]:
            low, _, high = p["specs"]["Voltage - Supply"].partition("~")
            assert parse_voltage(low) <= 3.3 <= parse_voltage(high or low)

    @pytest.mark.parametrize("query, subcategory", [("RGB LED", "rgb leds"), ("red LED 0603", "led indication - discrete"),
                                                    ("WS2812", None)])
    async def test_plain_leds_unchanged(self, query, subcategory):
        assert (await search(query, limit=1))["parsed"]["subcategory"] == subcategory

    @pytest.mark.parametrize("query", ["LED driver", "smart LED driver", "constant current LED driver 1A"])
    async def test_led_driver_is_the_led_drivers_subcategory(self, query):
        result = await search(query)
        assert result["parsed"]["subcategory"] == "led drivers"
        assert result["total"] > 0
        assert all(p["subcategory"] == "LED Drivers" for p in result["results"])

    @staticmethod
    def _rated_range(part):
        from pcbparts_mcp.parsers import parse_temp_range
        from pcbparts_mcp.search.spec_filter import TEMPERATURE_RANGE_ATTRIBUTES
        value = next(v for k, v in part["specs"].items() if k in TEMPERATURE_RANGE_ATTRIBUTES)
        return parse_temp_range(value)

    @pytest.mark.parametrize("name", ["Operating Temperature", "operating temperature", "Operating Temperature Range"])
    @pytest.mark.parametrize("op, value, check", [
        ("<=", "-40", lambda lo, hi: lo <= -40), ("<=", "-40°C", lambda lo, hi: lo <= -40),
        (">=", "105", lambda lo, hi: hi >= 105), ("=", "-40~85", lambda lo, hi: lo <= -40 and hi >= 85),
        ("=", "25", lambda lo, hi: lo <= 25 <= hi),
    ])
    async def test_operating_temperature_filter(self, name, op, value, check):
        # "Operating Temperature <= -40" was ignored: "isn't numeric, so only = works on it"
        result = await search("Type-C 16P", subcategory_name="USB Connectors",
                              spec_filters=[{"name": name, "op": op, "value": value}])
        assert not result.get("ignored_filters")
        assert result["total"] > 0
        assert all(check(*self._rated_range(p)) for p in result["results"])

    async def test_junction_range_counts_for_diodes(self):
        result = await search("SS34", subcategory_name="Schottky Diodes",
                              spec_filters=[{"name": "Operating Temperature", "op": ">=", "value": "150"}])
        assert result["total"] > 0
        assert all(self._rated_range(p)[1] >= 150 for p in result["results"])

    async def test_temperature_range_needs_equals(self):
        result = await search(None, subcategory_name="Tactile Switches", limit=1,
                              spec_filters=[{"name": "Operating Temperature", "op": ">", "value": "-40~85"}])
        assert result["ignored_filters"][0]["filter"] == "Operating Temperature > -40~85"

    @pytest.mark.parametrize("query, check", [
        ("tactile switch SMD -40C", lambda lo, hi: lo <= -40),
        ("USB-C receptacle 16 pin −40 °C", lambda lo, hi: lo <= -40),
        ("105C electrolytic capacitor 100uF", lambda lo, hi: hi >= 105),
        ("10k resistor 0603 -55~155℃", lambda lo, hi: lo <= -55 and hi >= 155),
    ])
    async def test_query_temperature(self, query, check):
        # "-40C" was an unsupported constraint ("40C", sign lost) and was left out
        result = await search(query)
        assert "unsupported_constraints" not in result["parsed"]["detected"]
        assert result["total"] > 0
        assert all(check(*self._rated_range(p)) for p in result["results"])

    @pytest.mark.parametrize("query", ["18650 charger 1C", "BC817-40", "I2C sensor", "-40 surface mount",
                                       "LM7912 -12V", "40C"])
    def test_not_temperatures(self, query):
        from pcbparts_mcp.smart_parser.parser import extract_temperatures
        assert extract_temperatures(query) == ([], query)


class TestBacklogClosure:
    """The last open items of the October backlog (closed 2026-11-02)."""

    async def test_supervisor_voltage_is_the_threshold(self):
        result = await search("3.6V supervisor")
        assert result["parsed"]["subcategory"] == "supervisor and reset ics"
        assert result["total"] > 0
        assert all(parse_voltage(p["specs"]["Threshold Voltage"]) == 3.6 for p in result["results"])

    async def test_no_fee_supervisor_says_other_tiers_exist(self):
        # Fell through to LDOs: "supervisor" wasn't a part type
        result = await search("voltage supervisor reset 3V", library_type="no_fee", match_all_terms=False)
        assert result["parsed"]["subcategory"] == "supervisor and reset ics"
        if result["total"] == 0:
            assert re.match(r"No no-fee part matches; \d+ extended parts do \(an assembly fee", result["hint"])

    @pytest.mark.parametrize("query", ["common mode choke 90ohm", "cmc 90ohm"])
    async def test_common_mode_choke(self, query):
        result = await search(query)
        assert result["total"] > 0
        assert all(p["subcategory"] == "Common Mode Filters" and p["specs"]["Impedance @ Frequency"].startswith("90Ω")
                   for p in result["results"])

    async def test_ferrite_sub_ohm_is_dcr(self):
        result = await search("ferrite bead 100mohm")
        assert {"name": "DCR", "op": "<=", "value": "100mOhm"} in result["filters_applied"]["spec_filters"]
        assert result["total"] > 0
        assert all(parse_resistance(p["specs"]["DC Resistance(DCR)"]) <= 0.1 for p in result["results"])

    async def test_jst_word_order(self):
        a, b = await search("jst 4 pin sh"), await search("jst sh 4 pin")
        assert a["total"] == b["total"] > 0 and a["results"] == b["results"]

    @pytest.mark.parametrize("query, op", [("LDO 25nA", "<="), ("LDO Iq < 100nA", "<")])
    async def test_nanoamp_quiescent_current(self, query, op):
        result = await search(query)
        assert "unsupported_constraints" not in result["parsed"]["detected"]
        assert any(f["name"] == "Quiescent Current" and f["op"] == op for f in result["filters_applied"]["spec_filters"])
        from pcbparts_mcp.search.spec_filter import ATTRIBUTE_ALIASES
        names = ATTRIBUTE_ALIASES["Quiescent Current"]
        assert result["total"] > 0
        assert all(parse_current(next(v for k, v in p["specs"].items() if k in names)) <= 1e-7
                   for p in result["results"])

    def test_parse_nanoamps(self):
        assert parse_current("25nA") == pytest.approx(2.5e-8)
        assert parse_current("1.5uA") == pytest.approx(1.5e-6)

    @pytest.mark.parametrize("query, henries", [("10u 250mA inductor", 10e-6), ("1m 250mA inductor", 1e-3),
                                                ("inductor 2R2 0805", 2.2e-6)])
    async def test_bare_inductance(self, query, henries):
        result = await search(query)
        assert result["total"] > 0
        assert all(p["specs"]["Inductance"] and abs(parse_inductance(p["specs"]["Inductance"]) - henries) < henries * 0.01
                   for p in result["results"])

    async def test_resistor_milliohm_unchanged(self):
        result = await search("1m resistor")
        assert {"name": "Resistance", "op": "=", "value": "1mOhm"} in result["filters_applied"]["spec_filters"]

    async def test_slash_separated_bom_current(self):
        result = await search("20V/4.2A/52mohm/1.4W SOT-23-3 mosfet")
        assert {"name": "Id", "op": ">=", "value": "4.2A"} in result["filters_applied"]["spec_filters"]
        assert not result.get("relaxed")

    async def test_relay_current(self):
        result = await search("relay 10A 5V")
        assert result["total"] > 0
        assert all(parse_current(p["specs"]["Switching Current(Max)"]) >= 10 for p in result["results"])

    @pytest.mark.parametrize("query", ["M2 standoff SMT", "mPCIe card latch standoff mini PCIe nut"])
    async def test_standoffs(self, query):
        result = await search(query)
        assert result["total"] > 0
        assert all("standoff" in p["subcategory"].lower() or "nut" in p["subcategory"].lower() for p in result["results"])

    async def test_any_word_search_ranks_more_words_first(self):
        # An op-amp matching one word led on stock
        result = await search("mPCIe card latch standoff mini PCIe nut", match_all_terms=False, limit=5)
        assert all("nut" in p["subcategory"].lower() or "standoff" in p["subcategory"].lower()
                   for p in result["results"])

    async def test_esp32_module(self):
        result = await search("ESP32-C3 module")
        assert result["total"] > 0
        assert all(p["subcategory"] in ("WiFi Modules", "RF Modules", "Bluetooth Modules") for p in result["results"])

    @pytest.mark.parametrize("query", ["3W class D audio amplifier", "class d amplifier 3W"])
    async def test_class_d_output_power(self, query):
        result = await search(query)
        assert result["total"] > 0
        for p in result["results"]:
            assert "Class D" in p["specs"]["Class"].split("、")
            assert max(parse_power(item) or 0 for item in p["specs"]["Output Power"].split("、")) >= 3

    async def test_single_cell_charger(self):
        result = await search("single cell lipo charger")
        assert result["total"] > 0
        for p in result["results"]:
            low, _, high = p["specs"]["Number of Cells"].partition("~")
            assert int(low) <= 1 <= int(high or low)

    @pytest.mark.parametrize("query, subcategory, attribute", [
        ("op amp 5V", "Operational Amplifier", "Single supply"), ("comparator 3.3V", "Comparators", "Single Supply")])
    async def test_op_amp_and_comparator_supply(self, query, subcategory, attribute):
        target = parse_voltage(query.split()[-1])
        result = await search(query)
        assert result["total"] > 0
        for p in result["results"]:
            assert p["subcategory"] == subcategory
            assert any(_range_passes(v, parse_voltage, "=", target) for k, v in p["specs"].items()
                       if k in ("Single supply", "Single Supply", "Voltage - Supply"))

    async def test_ideal_diodes_in_both_part_types(self):
        result = await search("ideal diode", limit=100)
        kinds = {p["subcategory"] for p in result["results"]}
        assert kinds == {"ORing Controllers", "Power Distribution Switches"}
        # Only the Power Distribution Switches that say "ideal diode", not every load switch
        switches = await search("ideal diode", subcategory_name="Power Distribution Switches", limit=100)
        assert 0 < switches["total"] < 30

    async def test_unknown_part_type_keeps_its_words(self):
        # Left out "gizmo" and searched the whole catalog on 3.3V and 2A (XH connectors)
        result = await search("gizmo 3.3V 2A")
        assert result["total"] == 0 and not result.get("relaxed")
        assert result["hint"].startswith('No part type matched "gizmo"')

    async def test_parsed_subcategory_is_the_one_searched(self):
        result = await search("600ohm 0603", subcategory_name="Ferrite Beads")
        assert result["parsed"]["subcategory"] == "ferrite beads"

    @pytest.mark.parametrize("query, expected", [
        ("1.5A/3A 1206 fuse", ("Current Rating", "=", "1.5A")),          # rated/trip: the first only
        ("6V/2.0A/4.0A 1210 fuse", ("Hold Current", ">=", "2.0A")),        # a PTC's hold/trip
        ("20V/4.2A/52mohm/1.4W SOT-23-3 mosfet", ("Id", ">=", "4.2A"))])
    async def test_slash_currents_first_only(self, query, expected):
        result = await search(query)
        currents = [(f["name"], f["op"], f["value"]) for f in result["filters_applied"]["spec_filters"]
                    if f["value"].endswith("A")]
        assert currents == [expected]
        assert result["total"] > 0

    async def test_multiplexer(self):
        result = await search("16 channel analog multiplexer")
        assert result["total"] > 0
        assert all(p["subcategory"] in ("Analog Switches, Multiplexers", "Signal Switches, Multiplexers, Decoders")
                   for p in result["results"])

    async def test_lora(self):
        # "LoRa transceiver 868MHz" left out "LoRa transceiver" (no part type)
        result = await search("lora", limit=100)
        assert {p["subcategory"] for p in result["results"]} <= {"LoRa Modules", "RF Transceiver ICs"}
        chips = await search(None, subcategory_name="RF Transceiver ICs", limit=1)
        assert result["total"] < chips["total"]  # only the transceivers whose text says LoRa

    async def test_supervisor_threshold_window(self):
        # "Threshold Voltage isn't numeric, so only = works on it": a 3.3-3.5V window was dropped
        result = await search(None, subcategory_name="Supervisor and Reset ICs", limit=100, spec_filters=[
            {"name": "Threshold Voltage", "op": ">=", "value": "3.3V"},
            {"name": "Threshold Voltage", "op": "<=", "value": "3.5V"}])
        assert not result.get("ignored_filters")
        assert result["total"] > 0
        assert all(any(3.3 * 0.99 <= parse_voltage(v) <= 3.5 * 1.01 for v in p["specs"]["Threshold Voltage"].split("、"))
                   for p in result["results"])


ISOLATED_POWER = {"Isolated Power Modules", "Isolated DC/DC Converters"}


class TestIsolatedParts:
    """"isolated DC-DC module 5V input 12V output 2W" searched 2,083 non-isolated buck/boost ICs and
    dropped "isolated module": no "isolated" alias existed for any part type."""

    @pytest.mark.parametrize("query", ["isolated DC-DC module 5V input 12V output 2W",
                                       "isolated 5V to 12V DC-DC converter 2W"])
    async def test_isolated_dc_dc(self, query):
        result = await search(query, limit=100)
        assert not result.get("relaxed")
        assert result["total"] > 0
        for p in result["results"]:
            assert p["subcategory"] in ISOLATED_POWER
            assert covers(p["specs"].get("Voltage - Supply") or p["specs"].get("Vin"), 5)
            assert p["specs"].get("Output Voltage", p["specs"].get("Vout")) == "12V"
            assert parse_power(p["specs"]["Output Power"]) >= 2

    async def test_isolation_voltage(self):
        result = await search("isolated DC-DC 5V 3kV", limit=100)
        assert {"name": "Isolation Voltage", "op": ">=", "value": "3kV"} in result["filters_applied"]["spec_filters"]
        assert result["total"] > 0
        assert all(parse_isolation_voltage(p["specs"]["Isolation Voltage(Vrms)"]) >= 3000 for p in result["results"])

    async def test_non_isolated_module(self):
        result = await search("non-isolated DC-DC module 12V to 5V", limit=100)
        assert result["total"] > 0
        assert {p["subcategory"] for p in result["results"]} == {"DC-DC Power Modules"}

    @pytest.mark.parametrize("query, subcategories", [
        ("isolated RS485 transceiver", {"Isolated RS-485/422 Transceivers", "Isolated RS-485/422 Transceivers with power"}),
        ("RS485 transceiver isolated", {"Isolated RS-485/422 Transceivers", "Isolated RS-485/422 Transceivers with power"}),
        ("isolated CAN transceiver", {"Isolated CAN Transceivers", "Isolated CAN Transceivers (with Power)"}),
        ("I2C isolator", {"I2C Isolators", "Isolated I2C (with Power)"}),
        ("isolated gate driver", {"Isolators - Gate Drivers"}),
        ("digital isolator", {"Digital Isolators", "Digital Isolators (with Power)"}),
        ("isolated power supply 5V", ISOLATED_POWER),  # empty since 0.8.0's "no part type" rule
        ("buck module 12V to 5V", {"DC-DC Power Modules"}),
    ])
    async def test_isolated_part_types(self, query, subcategories):
        result = await search(query, limit=100)
        assert not result.get("relaxed")
        assert result["total"] > 0
        assert {p["subcategory"] for p in result["results"]} <= subcategories

    async def test_module_output_current(self):
        # Modules list "Output Current(Max)", which no current filter read
        result = await search("isolated dc-dc 5V to 12V 0.1A", limit=100)
        assert not result["parsed"].get("adjusted_filters")
        assert result["total"] > 0
        assert all(parse_current(p["specs"]["Output Current(Max)"]) >= 0.1 for p in result["results"])


class TestDualRailOutputs:
    """Output Voltage = 12V also returned ±12V modules: two outputs, 24V across them."""

    async def test_single_output_excludes_dual_rail(self):
        result = await search(None, subcategory_id=2117, limit=100, spec_filters=[
            {"name": "Output Voltage", "op": "=", "value": "12V"}, {"name": "Supply Voltage", "op": "=", "value": "5V"},
            {"name": "Output Current(Max)", "op": ">=", "value": "0.1A"}])
        assert result["total"] > 0
        assert all(p["specs"]["Output Voltage"] == "12V" for p in result["results"])

    @pytest.mark.parametrize("query", ["isolated dc-dc 5V to ±12V", "isolated power module +/-12V"])
    async def test_dual_rail_when_asked(self, query):
        result = await search(query, limit=100)
        assert {"name": "Output Voltage", "op": "=", "value": "±12V"} in result["filters_applied"]["spec_filters"]
        assert result["total"] > 0
        # Isolated two-output modules listed as "-12V、12V" are ±12V too (0.8.1)
        from pcbparts_mcp.search.engine import _as_dual_rail
        assert all(_as_dual_rail(p["specs"]["Output Voltage"], p["specs"]) == "±12V" for p in result["results"])


def _colors(value: str) -> list[str]:
    """An Illumination Color list: "Red, Emerald Green" -> ["red", "emerald green"]."""
    return [item.strip().lower() for item in re.split(r"[、,，]", value or "") if item.strip()]


GREENS = {"green", "emerald green", "yellow green"}


class TestLedColours:
    """"green LED" with library_type no_fee found nothing: the only Basic green LED is listed as
    Emerald Green. "bicolor LED red green" returned red LEDs (the colours were OR'd)."""

    async def test_a_colour_word_covers_its_shades(self):
        result = await search("green LED", limit=100)
        values = [f["value"] for f in result["filters_applied"]["spec_filters"]]
        assert values == ["Green", "Emerald Green", "Yellow Green"]
        found = {p["specs"]["Illumination Color"] for p in result["results"]}
        assert found <= {"Green", "Emerald Green", "Yellow Green"} and "Emerald Green" in found
        no_fee = await search("green LED", library_type="no_fee", limit=100)
        assert no_fee["total"] > 0
        assert all(_colors(p["specs"]["Illumination Color"])[0] in GREENS for p in no_fee["results"])

    async def test_white_shades_and_named_shades(self):
        white = await search("white LED 0805", limit=100)
        assert {p["specs"]["Illumination Color"] for p in white["results"]} <= {"White", "Cold White", "Warm White"}
        for query, shade in (("yellow green LED", "Yellow Green"), ("emerald green LED", "Emerald Green"),
                             ("warm white LED", "Warm White")):
            result = await search(query, limit=50)
            assert result["total"] > 0
            assert {p["specs"]["Illumination Color"] for p in result["results"]} == {shade}

    @pytest.mark.parametrize("query, first", [("bicolor LED red green", "red"), ("red green LED", "red"),
                                              ("green red bi-color LED", "green")])
    async def test_two_colours_are_one_bicolour_part(self, query, first):
        result = await search(query, limit=100)
        assert not result.get("relaxed")
        assert result["filters_applied"]["spec_filters"] == [
            {"name": "Illumination Color", "op": "=", "value": "Red + Green" if first == "red" else "Green + Red"}]
        assert result["total"] > 0
        for p in result["results"]:
            colors = _colors(p["specs"]["Illumination Color"])
            assert len(colors) == 2 and "red" in colors and set(colors) & GREENS, colors

    @pytest.mark.parametrize("query, count", [("bicolor LED", 2), ("tricolor LED", 3)])
    async def test_colour_count_words(self, query, count):
        result = await search(query, limit=100)
        assert not result.get("relaxed")
        assert result["total"] > 0
        assert all(len(_colors(p["specs"]["Illumination Color"])) == count for p in result["results"])

    async def test_explicit_filters(self):
        # Two plain values stay either/or; "Red + Green" asks for the pair
        either = await search(subcategory_name="LED Indication - Discrete", limit=100, spec_filters=[
            {"name": "Illumination Color", "op": "=", "value": "Red"},
            {"name": "Illumination Color", "op": "=", "value": "Green"}])
        assert {p["specs"]["Illumination Color"] for p in either["results"]} <= {"Red", "Green"}
        pair = await search(subcategory_name="LED Indication - Discrete", limit=100, spec_filters=[
            {"name": "Illumination Color", "op": "=", "value": "Red + Blue"}])
        assert pair["total"] > 0
        assert all(sorted(_colors(p["specs"]["Illumination Color"])) == ["blue", "red"] for p in pair["results"])


async def test_no_fee_hint_for_a_part_number_in_stock_in_other_tiers():
    # "No in-stock part matches TL431" when 308 extended TL431s were in stock
    result = await search("TL431", library_type="no_fee")
    if result["total"]:
        pytest.skip("a no-fee TL431 is listed now")
    assert result["hint"].startswith("No no-fee part matches TL431; ")
    assert "in-stock" not in result["hint"] and "jlc_stock_check" not in result["hint"]


async def test_stock_check_lists_highest_stock_first(monkeypatch):
    # JLCPCB's own order is by LCSC code: SMF18A's Preferred part with the most stock was on page 2
    from unittest.mock import AsyncMock, Mock
    live = AsyncMock(return_value={"results": [], "total": 0})
    monkeypatch.setattr(server, "_client", Mock(search=live))
    await server.jlc_stock_check(query="SMF18A")
    assert live.await_args.kwargs["sort_by"] == "quantity"
    await server.jlc_stock_check(query="SMF18A", sort_by="price")
    assert live.await_args.kwargs["sort_by"] == "price"


class TestAudioJacks:
    """"2.5mm audio jack" returned 3.5mm jacks and "6.35mm jack" wire-to-board connectors: the size
    was read as a pin pitch, which no audio jack lists."""

    @pytest.mark.parametrize("query, types", [
        ("2.5mm audio jack", {"2.5mm Headphone Jack"}),
        ("6.35mm jack", {"6.35mm Headphone Jack"}),
        ("3.5mm headphone jack", {"3.5mm Headphone Jack"}),
        ("4.4mm jack", {"4.4mm Headphone Jack", "4.4mm audio jack"}),
        ("6.35mm plug", {"6.35mm Headphone Plug"}),
    ])
    async def test_size_is_the_connector_type(self, query, types):
        result = await search(query, limit=100)
        assert not result.get("relaxed") and not result["parsed"].get("adjusted_filters")
        assert result["total"] > 0
        assert {p["specs"]["Connector Type"] for p in result["results"]} <= types

    def test_alternatives_leave_pin_roles_unchecked(self):
        from pcbparts_mcp.alternatives import is_compatible_alternative
        jack = {"specs": {"Connector Type": "3.5mm Headphone Jack", "Mounting Type": "SMD"}}
        compatible, info = is_compatible_alternative(jack, jack, "Audio Connectors")
        assert compatible
        assert any("tip, ring and sleeve" in item for item in info["unchecked_requirements"])

    async def test_pinout_note_warns_about_pad_numbering(self, monkeypatch):
        class Fake:
            async def get_part(self, lcsc):
                return {"lcsc": lcsc, "subcategory": "Audio Connectors", "has_easyeda_footprint": True,
                        "easyeda_symbol_uuid": "u"}

            async def get_easyeda_component(self, uuid):
                pin = "P~show~0~{n}~0~0~180~g{n}~0^^0~0^^M0,0h10~#000^^1~0~0~0~{n}~start~~~#000^^1~0~0~0~{n}~end~~~#000"
                return {"dataStr": {"shape": [pin.format(n=n) for n in (1, 2, 3)]}}
        monkeypatch.setattr(server, "_client", Fake())
        result = await server.jlc_get_pinout(lcsc="C95463")
        assert "tip, ring and sleeve pads differently" in result["note"]


class TestCellularModules:
    """"4G module" found ESP32 WiFi modules, "cellular module" and "Cat-M1 module" nothing, and
    "LTE Cat-M" Cat.1 modules; LCSC's band lists for them are incomplete."""

    @pytest.mark.parametrize("query, network", [
        ("4G module", None), ("cellular module", None), ("LTE modem", None),
        ("Cat-M1 module", "cat-m"), ("LTE Cat-M module", "cat-m"), ("NB-IoT module", "nb-iot"),
        ("GSM module", "gsm"), ("Cat.1 module", "cat.1"),
    ])
    async def test_part_type_and_network(self, query, network):
        result = await search(query, limit=100)
        assert not result.get("relaxed")
        assert result["total"] > 0
        assert {p["subcategory"] for p in result["results"]} == {"2G/3G/4G/5G Modules"}
        if network:
            for p in result["results"]:
                networks = [n.strip().lower() for n in p["specs"]["Communication System"].split("、")]
                assert network in networks or (network == "nb-iot" and "cat.nb1" in networks) \
                    or (network == "cat.1" and "lte cat 1" in networks), networks
        assert "often incomplete" in result["note"]

    async def test_lte_antenna_keeps_its_part_type(self):
        result = await search("LTE antenna", limit=20)
        assert {p["subcategory"] for p in result["results"]} == {"Antennas"}

    async def test_note_on_part_lookups(self):
        result = await server.jlc_get_part(mpn="SIM7080G")
        if not result.get("results"):
            pytest.skip("SIM7080G not stocked")
        assert "datasheet_pdf" in result["note"]
        assert "note" not in await server.jlc_get_part(mpn="TPS2553DBVR")


class TestUnlistedCounts:
    """A -40°C filter left out AO3401A, one of the most-used Basic P-FETs, without saying so: LCSC
    lists its operating temperature as "-"."""

    async def test_count_matches_the_parts_left_out(self):
        args = {"query": "P-channel MOSFET SOT-23", "library_type": "basic", "limit": 100}
        everything = await search(**args)
        filtered = await search(**{**args, "query": "P-channel MOSFET SOT-23 -40°C"})
        kept = {p["lcsc"] for p in filtered["results"]}
        unlisted = [p for p in everything["results"]
                    if p["lcsc"] not in kept and p["specs"].get("Operating Temperature", "-") in ("-", "")]
        entries = filtered.get("unlisted", [])
        if not unlisted:
            assert entries == []
            pytest.skip("every Basic P-FET lists an operating temperature now")
        best = sorted(unlisted, key=lambda p: (-p["stock"], p["lcsc"]))[:3]
        assert entries == [{"filter": "Operating Temperature <= -40", "parts": len(unlisted),
                            "basic_preferred": len(unlisted),
                            "most_stocked": [f"{p['lcsc']} {p['model']}" for p in best]}]

    async def test_only_range_filters_are_counted(self):
        result = await search("10k resistor 0603 1%", limit=5)
        assert "unlisted" not in result  # exact resistance, tolerance and text filters
        ldo = await search("LDO 3.3V 500mA", limit=5)
        assert all(item["filter"].startswith("Output Current >=") for item in ldo.get("unlisted", []))

    async def test_empty_reply_hint_names_them(self):
        result = await search(subcategory_name="MOSFETs", library_type="basic", spec_filters=[
            {"name": "Operating Temperature", "op": "<=", "value": "-70"}, {"name": "Type", "op": "=", "value": "P-Channel"}])
        if result["total"] or not result.get("unlisted"):
            pytest.skip("catalog changed")
        assert "list no value for Operating Temperature <= -70" in result["hint"]


class TestModuleDropIns:
    """SIM7080G-M's drop-in SIM7080G (same 17.6x15.7mm package) ranked behind a 24x24mm A7670E."""

    def test_part_family(self):
        from pcbparts_mcp.alternatives import part_family
        assert part_family("SIM7080G-M") == part_family("SIM7080G") == "SIM7080G"
        assert part_family("A7670E-LASE") == "A7670E"
        assert part_family("ESP-12F") is None and part_family("LED") is None

    def test_likely_drop_in_needs_package_and_family(self):
        from pcbparts_mcp.alternatives import likely_drop_in
        original = {"model": "SIM7080G-M"}
        assert "SIM7080G" in likely_drop_in(original, {"model": "SIM7080G"}, same_package=True)
        assert likely_drop_in(original, {"model": "SIM800C"}, same_package=True) is None  # 2G, other pinout
        assert likely_drop_in(original, {"model": "SIM7080G"}, same_package=False) is None

    def test_flag_in_similar_parts(self):
        from pcbparts_mcp.alternatives import build_unsupported_response
        original = {"lcsc": "C18548266", "model": "SIM7080G-M", "package": "SMD,17.6x15.7mm", "specs": {}}
        part = {"lcsc": "C2943992", "model": "SIM7080G", "package": "SMD,17.6x15.7mm", "stock": 1000}
        reply = build_unsupported_response(original, [(60, part, {}, {})], "2G/3G/4G/5G Modules", None, 10,
                                           drop_ins={"C2943992": "same package and part family (SIM7080G); verify the pinout"})
        assert reply["similar_parts"][0]["likely_drop_in"].endswith("verify the pinout")


async def test_unlisted_skips_filters_already_reported_sparse():
    # No tactile switch lists "Height" (they list Switch Height); ignored_filters says so
    result = await search(subcategory_name="Tactile Switches", limit=5,
                          spec_filters=[{"name": "Height", "op": "<=", "value": "2mm"}])
    assert any(f["filter"] == "Height <= 2mm" for f in result.get("ignored_filters", []))
    assert "unlisted" not in result and "list no value" not in result.get("hint", "")


class TestPaging:
    """jlc_search had no offset: agents copied page= from jlc_stock_check and got a validation error."""

    @pytest.mark.parametrize("query, extra", [
        ("10k resistor 0603", {}),
        ("addressable RGB LED 3.3V", {}),  # a Python-checked range filter
        ("LM1117-3.3", {}),  # part-number ranking
        ("buck converter", {"spec_filters": [{"name": "Supply Voltage", "op": "=", "value": "24V"}]}),
    ])
    async def test_pages_join_up(self, query, extra):
        first_ten = await search(query, limit=10, **extra)
        page1 = await search(query, limit=5, **extra)
        page2 = await search(query, limit=5, offset=5, **extra)
        assert first_ten["total"] == page1["total"] == page2["total"] >= 10
        assert [p["lcsc"] for p in page1["results"] + page2["results"]] == [p["lcsc"] for p in first_ten["results"]]
        assert page2["page_info"] == {"limit": 5, "offset": 5, "returned": 5}

    async def test_offset_past_the_end(self):
        result = await search("10k resistor 0603", limit=5, offset=9999)
        assert result["results"] == [] and result["total"] > 0
        assert "past the last" in result["hint"]

    async def test_offset_is_capped(self):
        result = await search("10k resistor 0603", limit=5, offset=10**9)
        assert result["page_info"]["offset"] == 10_000

    def test_part_number_retry_pages_after_filtering(self):
        retry = {"results": [{"model": m, "library_type": "extended"} for m in
                             ("ABC123-A", "XYZ", "ABC123-B", "ABC123-C", "QQQ")],
                 "total": 5, "page_info": {"limit": 100, "offset": 0, "returned": 5}}
        kept = server._keep_part_number_matches(retry, "ABC123", limit=2, offset=1)
        assert [p["model"] for p in kept["results"]] == ["ABC123-B", "ABC123-C"]
        assert kept["total"] == 3 and kept["page_info"]["offset"] == 1
