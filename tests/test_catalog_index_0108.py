"""Catalog bounds, asymmetric tolerances and maker-suffixed search results."""

import json
import sys
from pathlib import Path

from fastmcp import Client
import pytest

from conftest import write_catalog_category
from pcbparts_mcp import db, server
from pcbparts_mcp.parsers import parse_current, parse_numeric_range, parse_tolerance, parse_voltage
from pcbparts_mcp.search.engine import _passes_post_filters, _range_passes
from pcbparts_mcp.search.mpn import MPN_MATCH_NAMES, mpn_match_rank
from pcbparts_mcp.search.query_builder import build_spec_filter_clauses
from pcbparts_mcp.search.spec_filter import FuseFilter, SpecFilter
from pcbparts_mcp.search.spec_sort import SpecSort, spec_sort_value_json

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import ATTRIBUTE_TO_COLUMN, build_database, extract_numeric_columns
from search_baseline import offline


BOUND_ATTRIBUTES = [
    (name, column, parser) for name, (column, parser) in ATTRIBUTE_TO_COLUMN.items()
    if "_max_" in column
]


@pytest.mark.parametrize("name,column,parser", BOUND_ATTRIBUTES, ids=[f"bound{i}" for i in range(len(BOUND_ATTRIBUTES))])
def test_all_scalar_bound_mappings_use_the_upper_endpoint(name, column, parser):
    assert parser in (parse_voltage, parse_current)
    unit = "V" if parser is parse_voltage else "A"
    for value in (f"500m{unit}~2{unit}", f"2{unit}~500m{unit}", f"500~2000m{unit}"):
        assert extract_numeric_columns([[name, value]])[column] == pytest.approx(2)


@pytest.mark.parametrize("name,value,expected", [
    ("Voltage - Supply", "1V~2V、3V~6V", {"voltage_max_v": 6}),
    ("Voltage Rating", "-7V~12V", {"voltage_max_v": 12}),
    ("Gate Threshold Voltage", "800mV~2V", {"vgs_th_min_v": .8, "vgs_th_max_v": 2}),
    ("Input Voltage", "5.5V~2.7V", {"vin_min_v": 2.7, "vin_max_v": 5.5}),
    ("Frequency Range", "500~2000kHz", {"freq_min_hz": 500000, "freq_max_hz": 2000000}),
    ("Frequency", "2GHz~500MHz", {"freq_min_hz": 500000000, "freq_max_hz": 2000000000}),
    ("Operating Temperature", "+85°C~-40°C", {"temp_min_c": -40, "temp_max_c": 85}),
    ("Output Current", "250mA、500mA", {"iout_max_a": .25}),
], ids=["bands", "signed", "threshold", "input", "freq-unit", "freq-order", "temperature", "scalar-list"])
def test_paired_bounds_and_units(name, value, expected):
    actual = extract_numeric_columns([[name, value]])
    for column, number in expected.items():
        assert actual[column] == pytest.approx(number)


@pytest.mark.parametrize("separator", ["~", "～", "–", " to "], ids=["tilde", "wide", "dash", "word"])
@pytest.mark.parametrize("left,right,bounds", [
    ("2.7V", "5.5V", (2.7, 5.5)), ("5.5V", "2.7V", (2.7, 5.5)),
    ("500mV", "2V", (.5, 2)), ("500", "2000mV", (.5, 2)),
    ("-15V", "-5V", (-15, -5)), ("±2.5V", "±18V", (2.5, 18)),
], ids=["supply", "reversed", "mixed", "shared", "negative", "dual"])
def test_index_and_runtime_range_endpoints_agree(separator, left, right, bounds):
    value = left + separator + right
    low, high = bounds
    assert parse_numeric_range(value, parse_voltage) == pytest.approx(bounds)
    assert extract_numeric_columns([["Voltage - Supply", value]])["voltage_max_v"] == pytest.approx(high)
    for target in (low, (low + high) / 2, high):
        assert _range_passes(value, parse_voltage, "=", target)
    assert _range_passes(value, parse_voltage, ">=", high)
    assert _range_passes(value, parse_voltage, "<=", low)
    assert not _range_passes(value, parse_voltage, ">", high)
    assert not _range_passes(value, parse_voltage, "<", low)
    assert not _range_passes(value, parse_voltage, "=", low - 1)
    assert not _range_passes(value, parse_voltage, "=", high + 1)


@pytest.mark.parametrize("separator", ["~", "～", "–", " to "], ids=["tilde", "wide", "dash", "word"])
@pytest.mark.parametrize("delimiter", ["、", ";", ","], ids=["list", "semi", "comma"])
def test_shared_range_parsing_keeps_gaps_lists_and_dual_supplies(separator, delimiter):
    ranges = f"1V{separator}2V{delimiter}4V{separator}6V"
    assert _range_passes(ranges, parse_voltage, "=", 5)
    assert not _range_passes(ranges, parse_voltage, "=", 3)
    assert _range_passes(f"2.7V{delimiter}5.5V", parse_voltage, "=", 5.5)
    assert not _range_passes(f"2.7V{delimiter}5.5V", parse_voltage, "=", 3.3)
    dual = f"±2.5V{separator}±18V"
    assert _range_passes(dual, parse_voltage, "=", 12)
    assert _range_passes(dual, parse_voltage, "=", 12, dual=True)
    assert not _range_passes(dual, parse_voltage, "=", 12, dual=False)
    assert _range_passes("-12V", parse_voltage, "=", -12, dual=False)
    checks = [(SpecFilter("Voltage - Supply", op, value), {"Voltage - Supply"}, parse_voltage, target)
              for op, value, target in ((">=", "3V", 3), ("<=", "3.5V", 3.5))]
    assert not _passes_post_filters({"Voltage - Supply": ranges}, None, checks)


@pytest.mark.parametrize("value", ["0.5A", "500mA", "500000uA"])
def test_hold_current_is_indexed_and_scoped_in_sql(value):
    assert extract_numeric_columns([["Hold Current", value]])["hold_current_a"] == .5
    clauses, params, post_filters, ignored = build_spec_filter_clauses([
        FuseFilter("Hold Current", "=", value, subcategory_id=1),
        FuseFilter("Current Rating", "=", value, subcategory_id=2),
    ])
    assert "AND (subcategory_id != ? OR hold_current_a = ?)" in clauses
    assert "AND (subcategory_id != ? OR current_max_a = ?)" in clauses
    assert params == [1, .5, 2, .5, 1, 2]
    assert not post_filters and not ignored


@pytest.mark.parametrize("value,expected", [
    ("0%~+100%", 100), ("-20%~+80%", 80), ("-80%~+20%", 80),
    ("-100~+20%", 100), ("+80%/-20%", 80), ("±1%", 1), ("1%", 1), ("-", None),
], ids=["zero", "positive", "negative", "shared-unit", "slash", "symmetric", "plain", "missing"])
def test_tolerance_is_the_largest_absolute_deviation(value, expected):
    assert parse_tolerance(value) == expected
    indexed = extract_numeric_columns([["Tolerance", value]])
    assert indexed.get("tolerance_pct") == expected
    metadata = [(SpecFilter("Tolerance", "<=", "20%"), {"Tolerance"}, parse_tolerance, 20)]
    assert _passes_post_filters({"Tolerance": value}, None, metadata) is (expected is not None and expected <= 20)


@pytest.mark.parametrize("model,maker,asked,group", [
    ("MCP73831T-2ACI/OT", "Microchip Tech", "MCP73831T-2ACI/OT", "full"),
    ("MCP73831T-2ACI/OT-HXY", "HXY MOSFET", "MCP73831T-2ACI/OT", "same_suffix"),
    ("abc123_pkg-acme", "Acme", "ABC123/PKG", "same_suffix"),
    ("ABC123/PKG-ACME", "Acme", "ABC123/PKG-ACME", "full"),
    ("ABC123/PKG-TR", "Tron", "ABC123/PKG", "full"),
    ("ABC123/OTHER-ACME", "Acme", "ABC123/PKG", "family"),
], ids=["exact", "maker", "general", "asked-maker", "packing", "other-package"])
def test_match_group_knows_the_manufacturer(model, maker, asked, group):
    assert MPN_MATCH_NAMES[mpn_match_rank(model, asked, maker)] == group


@pytest.fixture
def small_catalog(tmp_path):
    parts = []
    for code, model, maker, tolerance, stock in (
        ("C1", "ABC123/PKG-ACME", "Acme", "0%~+100%", 900),
        ("C2", "ABC123/PKG", "Original", "±1%", 100),
        ("C3", "ABC123/OTHER", "Original", "-20%~+80%", 800),
    ):
        parts.append({"l": code, "m": model, "f": maker, "p": "SOT-23", "s": stock,
                      "t": "e", "c": 1, "$": .1, "d": model,
                      "a": [["Voltage - Supply", "3.75V~6V"], ["Tolerance", tolerance]]})
    write_catalog_category(tmp_path, "parts", parts)
    path = tmp_path / "components.db"
    build_database(tmp_path, path, verbose=False)
    catalog = db.ComponentDatabase(db_path=path)
    try:
        yield catalog
    finally:
        catalog.close()


def test_indexed_and_runtime_match_groups_counts_and_pages_agree(small_catalog):
    for name in ("Voltage Rating", "Voltage - Supply"):
        args = {"query": "ABC123", "part_number": "ABC123/PKG",
                "spec_filters": [SpecFilter(name, ">=", "4.2V")]}
        reply = small_catalog.search(**args)
        assert [row["lcsc"] for row in reply["results"]] == ["C2", "C1", "C3"]
        assert [row["mpn_match"] for row in reply["results"]] == ["full", "same_suffix", "family"]
        assert reply["mpn_matches"] == {"part_number": "ABC123/PKG", "full": 1, "same_suffix": 1, "family": 1}
        page = small_catalog.search(**args, offset=1, limit=1)
        assert page["results"] == reply["results"][1:2]
        assert page["mpn_matches"] == reply["mpn_matches"]
    assert _range_passes("3.75V~6V", parse_voltage, "=", 4.2)
    assert not _range_passes("1V~2V、5V~6V", parse_voltage, "=", 4.2)


def test_tolerance_filter_and_sort_use_the_same_worst_deviation(small_catalog):
    reply = small_catalog.search(spec_filters=[SpecFilter("Tolerance", "<=", "20%")])
    assert [row["lcsc"] for row in reply["results"]] == ["C2"]
    for direction, codes in (("asc", ["C2", "C3", "C1"]), ("desc", ["C1", "C3", "C2"])):
        reply = small_catalog.search(spec_sort=SpecSort.parse("Tolerance", direction))
        assert [row["lcsc"] for row in reply["results"]] == codes
        assert all(row["sort_value"] == row["specs"]["Tolerance"] for row in reply["results"])
    assert spec_sort_value_json(json.dumps([["Tolerance", "0%~+100%"]]), "Tolerance") == 100
    assert spec_sort_value_json(json.dumps([["Voltage Rating", "0V~25V"]]), "Voltage Rating") == 25


@pytest.fixture
async def local_client():
    if not db.DEFAULT_DB_PATH.exists():
        pytest.skip("Local catalog is not built")
    with offline():
        async with Client(server.mcp) as client:
            yield client


@pytest.mark.parametrize("code,query,name,op,value,present", [
    ("C1855818", "DRV8874PWPR", "Voltage Rating", ">=", "16.8V", True),
    ("C1855818", "DRV8874PWPR", "Voltage - Supply", ">=", "16.8V", True),
    ("C1855818", "DRV8874PWPR", "Voltage - Supply", "=", "16.8V", True),
    ("C1640747", "562R5HKS10", "Tolerance", "<=", "1%", False),
    ("C106221", "CC0603ZRY5V9BB104", "Tolerance", "<=", "20%", False),
], ids=["voltage-index", "voltage-range", "voltage-includes", "tol100", "tol80"])
async def test_reported_filters_in_process(local_client, code, query, name, op, value, present):
    if db.get_db().get_by_lcsc(code) is None:
        pytest.skip(f"{code} is no longer in the snapshot")
    result = await local_client.call_tool("jlc_search", {
        "query": query, "spec_filters": [{"name": name, "op": op, "value": value}], "strict": True,
    })
    assert (code in [part["lcsc"] for part in result.structured_content["results"]]) is present


async def test_reported_charger_ranks_exact_before_maker_suffix(local_client):
    if any(db.get_db().get_by_lcsc(code) is None for code in ("C424093", "C42432883")):
        pytest.skip("A recorded charger is no longer in the snapshot")
    result = (await local_client.call_tool("jlc_search", {"query": "MCP73831T-2ACI/OT 4.2V"})).structured_content
    assert result["results"][0]["lcsc"] == "C424093"
    matches = {part["lcsc"]: part["mpn_match"] for part in result["results"]}
    assert matches["C424093"] == "full"
    assert matches["C42432883"] == "same_suffix"
    assert result["mpn_matches"]["part_number"] == "MCP73831T-2ACI/OT"
