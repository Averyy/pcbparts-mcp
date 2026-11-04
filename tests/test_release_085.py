"""0.8.5: jlc_search sorted by a spec (#85). Searches run on the local catalog and check every result's
order rather than one part number, so the daily data can change under them."""

import json
import re
import sys
from pathlib import Path

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.parsers import parse_current, parse_resistance, parse_voltage
from pcbparts_mcp.search.spec_sort import (
    SORTABLE_SPECS,
    SortSpecError,
    SpecSort,
    rds_on_at_drive_ohms,
    spec_sort_value_json,
    vf_at_current,
)
from pcbparts_mcp.smart_parser import parse_smart_query

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import ATTRIBUTE_TO_COLUMN  # noqa: E402
from search_baseline import offline  # noqa: E402

LDO = "Voltage Regulators - Linear, Low Drop Out (LDO) Regulators"
TIERS = {"basic": 0, "preferred": 1, "extended": 2}


@pytest.fixture(autouse=True)
async def no_network():
    # Async so the event loop exists first: on Windows its socket pair is built with connect()
    with offline():
        yield


async def search(query: str | None = None, **kwargs):
    result = await server.jlc_search(query=query, limit=kwargs.pop("limit", 50), **kwargs)
    assert "error" not in result, result.get("error")
    return result


def _ordered(values: list[float | None], descending: bool = False) -> bool:
    """Listed values in order, then only missing ones."""
    listed = [v for v in values if v is not None]
    if values[:len(listed)] != listed:
        return False
    return listed == sorted(listed, reverse=descending)


class TestParse:
    @pytest.mark.parametrize("text,label", [
        ("Rds(on)", "RDS(on)"), ("rds(on)", "RDS(on)"), ("on resistance", "RDS(on)"),
        ("Iq", "Quiescent Current"), ("standby current", "Quiescent Current"),
        ("Dropout", "Voltage Dropout"), ("Voltage Dropout", "Voltage Dropout"),
        ("Vf", "Vf"), ("Voltage - Forward(Vf@If)", "Vf"), ("Clamping Voltage@Ipp", "Clamping Voltage"),
        ("isat", "Isat"), ("GBW", "GBW"), ("flash", "Flash"), ("Voltage", "Voltage Rating"),
        ("Current - Continuous Drain(Id)", "Id"), ("Vrwm", "Standoff Voltage"),
    ])
    def test_names(self, text, label):
        sort = SpecSort.parse(text)
        assert sort.spec.label == label and sort.at is None and not sort.descending

    @pytest.mark.parametrize("text,label,at", [
        ("Rds(on)@4.5V", "RDS(on)", 4.5), ("RDS(on) at 3.3V", "RDS(on)", 3.3),
        ("Dropout@500mA", "Voltage Dropout", 0.5), ("dropout @ (300mA)", "Voltage Dropout", 0.3),
        ("Vf@1A", "Vf", 1.0),
    ])
    def test_conditions(self, text, label, at):
        sort = SpecSort.parse(text, "desc")
        assert sort.spec.label == label and sort.at == pytest.approx(at) and sort.descending

    @pytest.mark.parametrize("text", ["Output Voltage", "Vout", "Supply Voltage", "Vgs(th)", "Slew Rate",
                                      "Gate Charge", "Operating Temperature", "Sampling Rate"])
    def test_ranges_refused_with_reason(self, text):
        with pytest.raises(SortSpecError, match=r"^Can't sort by .+: .{20,}"):
            SpecSort.parse(text)

    @pytest.mark.parametrize("text,match", [
        ("flux capacitance", r"^Unsupported sort_spec: 'flux capacitance'$"),
        ("Isat@1A", r"^Can't sort Isat at a condition"),
        ("Rds(on)@abc", r"^Can't sort RDS\(on\) at 'abc': give a gate voltage"),
        ("Dropout@3.3V", r"^Can't sort Voltage Dropout at '3.3V': give a current"),
    ])
    def test_errors(self, text, match):
        with pytest.raises(SortSpecError, match=match) as error:
            SpecSort.parse(text)
        assert server._error_kind(str(error.value)) == "bad_request"
        assert "RDS(on)" in error.value.valid_values

    def test_every_refusal_is_a_bad_request(self):
        from pcbparts_mcp.search.spec_sort import _REFUSED
        for names in _REFUSED:
            with pytest.raises(SortSpecError) as error:
                SpecSort.parse(names[0])
            assert server._error_kind(str(error.value)) == "bad_request"


class TestColumnsMatchTheBuild:
    """A sort reads the column the database build fills, so each spec's attributes must be the ones
    that fill it, parsed the same way, and any other attribute filling it must be named as another
    source (voltage_max_v also holds supply ranges' first numbers)."""

    @pytest.mark.parametrize("spec", SORTABLE_SPECS, ids=lambda s: s.label)
    def test_spec(self, spec):
        for name in spec.names:
            assert ATTRIBUTE_TO_COLUMN[name] == (spec.column, spec.parser), name
        filling = {name for name, (column, _) in ATTRIBUTE_TO_COLUMN.items() if column == spec.column}
        assert filling - set(spec.names) == set(spec.other_sources)


class TestConditions:
    def test_vf_bounded_by_the_lowest_current_at_or_above(self):
        listed = "190mV@100uA、250mV@1mA、300mV@10mA、410mV@100mA、500mV@200mA"
        assert vf_at_current(listed, 0.05) == (pytest.approx(0.41), "410mV@100mA")
        assert vf_at_current(listed, 0.2) == (pytest.approx(0.5), "500mV@200mA")
        assert vf_at_current("450mV@300mA", 1) is None  # only listed at a lower current
        assert vf_at_current("1V", 1) is None

    def test_rds_at_drive(self):
        attributes = json.dumps([["RDS(on)", "9.8mΩ@10V、13.5mΩ@4.5V"]])
        assert rds_on_at_drive_ohms(attributes, 4.5) == pytest.approx(0.0135)
        assert rds_on_at_drive_ohms(attributes, 12) == pytest.approx(0.0098)
        assert rds_on_at_drive_ohms(attributes, 2.5) is None

    def test_other_source_read_from_its_own_attribute(self):
        attributes = json.dumps([["Voltage Rating", "50V"], ["Voltage - Supply", "1.8V~5.5V"]])
        assert spec_sort_value_json(attributes, "Voltage Rating") == 50
        assert spec_sort_value_json(json.dumps([["Voltage - Supply", "1.8V~5.5V"]]), "Voltage Rating") is None

    def test_zero_is_a_placeholder_at_a_condition_too(self):
        rds = SpecSort.parse("RDS(on)@4.5V")
        assert rds.value_text({"RDS(on)": "0mΩ@4.5V"}) is None
        assert rds_on_at_drive_ohms(json.dumps([["RDS(on)", "0mΩ@4.5V"]]), 4.5) is None
        assert vf_at_current("0mV@1A", 1) is None and SpecSort.parse("Vf@1A").value_text({"Voltage - Forward(Vf@If)": "0mV@1A"}) is None
        assert SpecSort.parse("Dropout@1A").value_text({"Voltage Dropout": "0mV@(1A)"}) is None
        from pcbparts_mcp.search.spec_sort import dropout_sort_value
        assert dropout_sort_value(json.dumps([["Voltage Dropout", "0mV@(1A)"]]), 1) is None
        assert dropout_sort_value(json.dumps([["Voltage Dropout", "180mV@(1A)"]]), 1) == pytest.approx(0.18)

    def test_zero_is_a_placeholder(self):
        iq = SpecSort.parse("Iq")
        assert iq.value_text({"Quiescent Current": "0uA"}) is None
        assert iq.value_text({"Quiescent Current": "25nA"}) == "25nA"
        assert SpecSort.parse("Resistance").value_text({"Resistance": "0Ω"}) == "0Ω"  # jumpers


class TestQueryPhrases:
    @pytest.mark.parametrize("query,label,descending", [
        ("lowest Iq 3.3V LDO", "Quiescent Current", False),
        ("highest isat 4.7uH inductor", "Isat", True),
        ("most flash stm32", "Flash", True),
        ("tightest tolerance 10k resistor 0603", "Tolerance", False),
        ("lowest rds(on) n-channel mosfet SOT-23", "RDS(on)", False),
        ("smallest DCR 10uH power inductor", "DCR", False),
        ("longest life 470uF electrolytic", "Lifetime", True),
    ])
    def test_sort(self, query, label, descending):
        parsed = parse_smart_query(query)
        assert parsed.spec_sort.spec.label == label and parsed.spec_sort.descending == descending
        words = parsed.detected["sort"]["from"].lower()
        assert words not in parsed.remaining_text.lower()

    def test_other_words_kept(self):
        parsed = parse_smart_query("lowest Iq 3.3V LDO")
        assert [f.to_dict() for f in parsed.spec_filters] == [{"name": "Vout", "op": "=", "value": "3.3V"}]
        assert parse_smart_query("most flash stm32").model_number.lower() == "stm32"

    @pytest.mark.parametrize("query", ["lowest power mcu", "low iq ldo", "highest current mosfet", "low esr capacitor",
                                       "at least RAM 8KB MCU", "at most vf 0.4V schottky", "minimum flash 64KB mcu",
                                       "maximum vds 30V mosfet"])
    def test_not_a_sort(self, query):
        assert parse_smart_query(query).spec_sort is None

    def test_cheapest_is_still_price(self):
        parsed = parse_smart_query("lowest price 10k resistor 0603")
        assert parsed.spec_sort is None and parsed.detected["sort_by"] == "price"


class TestSearch:
    async def test_rds_on_ascending_missing_last(self):
        result = await search("n-channel mosfet SOT-23", sort_spec="Rds(on)", limit=100)
        values = [parse_resistance(p["sort_value"].split("@")[0]) if p["sort_value"] else None for p in result["results"]]
        assert result["results"] and _ordered(values)
        assert result["sort"]["spec"] == "RDS(on)" and "not a like-for-like comparison" in result["sort"]["note"]
        assert 'sort_spec="RDS(on)@4.5V"' in result["sort"]["note"]

    async def test_rds_on_at_a_gate_drive(self):
        result = await search("n-channel mosfet SOT-23", sort_spec="Rds(on)@2.5V", limit=100)
        assert result["sort"]["at"] == "2.5V gate drive"
        values = []
        for part in result["results"]:
            if part["sort_value"]:
                gate = re.search(r"@\s*(?:VGS\s*=\s*)?(\d+(?:\.\d+)?)\s*(m?)V", part["sort_value"], re.IGNORECASE)
                assert float(gate[1]) / (1000 if gate[2] else 1) <= 2.5, part["sort_value"]
                values.append(parse_resistance(part["sort_value"].split("@")[0]))
            else:
                values.append(None)
        assert values[0] is not None and _ordered(values)

    async def test_gate_drive_from_the_query(self):
        result = await search("lowest rds(on) n-channel mosfet SOT-23 3.3V gate drive", limit=20)
        assert result["sort"]["at"] == "3.3V gate drive (from the query's gate drive)"
        assert result["parsed"]["detected"]["sort"] == {"spec": "RDS(on)", "order": "asc", "from": "lowest rds(on)"}

    async def test_dropout_at_the_output_current_wanted(self):
        result = await search("lowest dropout ldo 500mA", limit=100)
        assert result["sort"]["at"] == "500mA load (from the Output Current filter)"
        values = []
        for part in result["results"]:
            text = part["sort_value"]
            values.append(parse_voltage(text.split(" at ")[0]) if text else None)
            if text:
                assert " at 500mA (from " in text
                assert parse_current(part["specs"]["Output Current"]) >= 0.5
        assert values[0] is not None and _ordered(values)

    async def test_dropout_load_from_its_filter(self):
        result = await search(subcategory_name=LDO, sort_spec="Dropout",
                              spec_filters=[{"name": "Dropout", "op": "<=", "value": "0.4V@300mA"}], limit=30)
        assert result["sort"]["at"] == "300mA load (from the Dropout filter)"
        assert all(" at 300mA (from " in p["sort_value"] for p in result["results"])

    async def test_vf_at_the_if_wanted(self):
        result = await search("lowest forward voltage schottky 1A", limit=100)
        assert result["sort"]["at"] == "1A forward current (from the If filter)"
        values = []
        for part in result["results"]:
            pair = part["sort_value"]
            values.append(parse_voltage(pair.split("@")[0]) if pair else None)
            if pair:
                assert parse_current(pair.split("@")[1]) >= 1
        assert values[0] is not None and _ordered(values)

    async def test_descending(self):
        result = await search("power inductor 4.7uH", sort_spec="isat", sort_order="descending", limit=100)
        values = [parse_current(p["sort_value"]) if p["sort_value"] else None for p in result["results"]]
        assert result["sort"]["order"] == "desc" and _ordered(values, descending=True)

    async def test_missing_values_come_last(self):
        first = await search(subcategory_name="Aluminum Electrolytic Capacitors - SMD", sort_spec="ESR", limit=100)
        tail = await search(subcategory_name="Aluminum Electrolytic Capacitors - SMD", sort_spec="ESR", limit=100,
                            offset=first["total"] - 100)
        assert first["results"][0]["sort_value"] is not None
        values = [p["sort_value"] for p in tail["results"]]
        assert None in values and all(v is None for v in values[values.index(None):])

    async def test_ties_go_to_library_tier_then_stock(self):
        result = await search("10k resistor 0603", sort_spec="Tolerance", limit=100)
        rows = result["results"]
        for a, b in zip(rows, rows[1:]):
            if a["sort_value"] == b["sort_value"]:
                assert (TIERS[a["library_type"]], -a["stock"]) <= (TIERS[b["library_type"]], -b["stock"])

    async def test_paging_is_stable(self):
        both = await search("n-channel mosfet", sort_spec="Rds(on)@4.5V", limit=40)
        first = await search("n-channel mosfet", sort_spec="Rds(on)@4.5V", limit=20)
        second = await search("n-channel mosfet", sort_spec="Rds(on)@4.5V", limit=20, offset=20)
        assert [p["lcsc"] for p in both["results"]] == [p["lcsc"] for p in first["results"] + second["results"]]

    async def test_with_a_range_filter_checked_in_python(self):
        result = await search(subcategory_name=LDO, sort_spec="Iq", limit=50,
                              spec_filters=[{"name": "Supply Voltage", "op": "=", "value": "12V"}])
        values = [parse_current(p["sort_value"]) if p["sort_value"] else None for p in result["results"]]
        assert result["results"] and _ordered(values)

    async def test_query_direction_overridden(self):
        result = await search("lowest iq ldo", sort_order="desc", limit=20)
        assert result["sort"] == {**result["sort"], "spec": "Quiescent Current", "order": "desc"}

    async def test_none_listed(self):
        result = await search("lowest esr 100uF capacitor", limit=5)
        note = result["sort"]["note"]
        assert note.startswith("None of the ") and "list ESR" in note and "Aluminum Electrolytic" in note
        assert all(p["sort_value"] is None for p in result["results"])

    async def test_sort_phrase_alone(self):
        result = await search("highest gbw", subcategory_name="Operational Amplifier", limit=5)
        assert result["total"] > 1000 and result["results"][0]["sort_value"]

    async def test_cheapest_and_a_spec(self):
        result = await search("cheapest lowest iq ldo", limit=5)
        assert result["sort"]["spec"] == "Quiescent Current"
        assert any(f["filter"] == "cheapest" for f in result["parsed"]["adjusted_filters"])

    async def test_other_sorts_unchanged(self):
        price = await search("10k resistor 0603", sort_by="price", limit=10)
        stock = await search("10k resistor 0603", limit=10)
        for result in (price, stock):
            assert "sort" not in result and all("sort_value" not in p for p in result["results"])

    async def test_search_help_marks_sortable_attributes(self):
        help_ = await server.jlc_search_help(subcategory="MOSFETs")
        marked = {a["name"]: a.get("sort_spec") for a in help_["attributes"]}
        assert marked["RDS(on)"] == "RDS(on)" and marked["Drain to Source Voltage"] == "Vds"
        assert "sort_spec" not in next(a for a in help_["attributes"] if a["name"].startswith("Gate Threshold"))


class TestArguments:
    @pytest.mark.parametrize("kwargs,match", [
        ({"sort_by": "spec"}, r'^Give a sort_spec with sort_by="spec"'),
        ({"sort_order": "desc"}, r"^Give a sort_spec to use sort_order"),
        ({"sort_by": "price", "sort_spec": "Rds(on)"}, r'^Give a sort_spec only with sort_by="spec"'),
        ({"sort_spec": "Output Voltage"}, r"^Can't sort by Output Voltage: "),
        ({"sort_spec": "nonsense"}, r"^Unsupported sort_spec: 'nonsense'$"),
    ])
    async def test_errors(self, kwargs, match):
        result = await server.jlc_search(query="mosfet", **kwargs)
        assert re.match(match, result["error"]) and result["results"] == []
        assert server._error_kind(result["error"]) == "bad_request"

    async def test_sort_by_spec_with_spec(self):
        result = await search("mosfet", sort_by="spec", sort_spec="Vds", sort_order="desc", limit=5)
        assert result["sort"]["spec"] == "Vds" and result["sort"]["order"] == "desc"
