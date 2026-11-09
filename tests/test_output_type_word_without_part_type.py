"""Output-type words need a part type or model before narrowing a text search."""

import sys
from pathlib import Path

from fastmcp import Client
import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.smart_parser import parse_smart_query

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline


UNTYPED_QUERY = "adjustable bracket 18650 26650 32650 multi size"
OUTPUT_WORDS = [("adjustable", "Adjustable"), ("variable", "Adjustable"), ("fixed", "Fixed")]


@pytest.fixture
async def local_client():
    with offline():
        async with Client(server.mcp) as client:
            yield client


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("word,value", OUTPUT_WORDS)
@pytest.mark.parametrize("text", ["holder", "bracket 18650 26650 32650 multi size"])
def test_output_word_stays_text_without_part_type(word, value, text, strict):
    parsed = parse_smart_query(f"{word} {text}", strict=strict)

    assert not parsed.subcategory and not parsed.subcategories and not parsed.model_number
    assert not any(f.name == "Output Type" for f in parsed.spec_filters)
    assert set(parsed.remaining_text.split()) == {word, *text.split()}
    assert "semantic" not in parsed.detected


def test_multiple_output_words_and_case_stay_text():
    parsed = parse_smart_query("ADJUSTABLE variable fixed holder")

    assert set(parsed.remaining_text.lower().split()) == {"adjustable", "variable", "fixed", "holder"}
    assert not parsed.spec_filters
    assert "semantic" not in parsed.detected


@pytest.mark.parametrize("word,name,operator,value", [
    ("red", "Illumination Color", "=", "Red"),
    ("x7r", "Temperature Coefficient", "=", "X7R"),
    ("precision", "Tolerance", "<=", "0.1%"),
])
def test_other_semantic_descriptors_are_preserved(word, name, operator, value):
    parsed = parse_smart_query(f"adjustable {word} holder")

    assert parsed.remaining_text == "adjustable holder"
    assert [(f.name, f.operator, f.value) for f in parsed.spec_filters] == [(name, operator, value)]
    assert parsed.detected["semantic"] == [word]


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("text,subcategory,grouped", [
    ("LDO 3A", "voltage regulators - linear, low drop out (ldo) regulators", False),
    ("inductor", "inductors (smd)", True),
    ("standoff", "female-female hex standoff", True),
])
def test_resolved_part_types_keep_filter_for_fitting(text, subcategory, grouped, strict):
    parsed = parse_smart_query(f"adjustable {text}", strict=strict)

    assert parsed.subcategory == subcategory
    assert bool(parsed.subcategories) is grouped
    assert any(f.name == "Output Type" and f.value == "Adjustable" for f in parsed.spec_filters)
    assert "adjustable" in parsed.detected["semantic"]


@pytest.mark.parametrize("strict", [False, True])
def test_adjustable_resistor_still_resolves_to_potentiometer(strict):
    parsed = parse_smart_query("adjustable resistor", strict=strict)

    assert parsed.subcategory == "potentiometers, variable resistors"
    assert not parsed.remaining_text


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("word,value", OUTPUT_WORDS)
def test_model_number_keeps_output_filter(word, value, strict):
    parsed = parse_smart_query(f"{word} LM317 holder", strict=strict)

    assert parsed.model_number == "LM317"
    assert any(f.name == "Output Type" and f.value == value for f in parsed.spec_filters)
    assert word in parsed.detected["semantic"]


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("word,value", OUTPUT_WORDS)
def test_no_other_text_keeps_output_filter(word, value, strict):
    parsed = parse_smart_query(f"{word} 3.3V", strict=strict)

    assert not parsed.subcategory and not parsed.subcategories and not parsed.model_number
    assert not parsed.remaining_text
    assert any(f.name == "Output Type" and f.value == value for f in parsed.spec_filters)
    assert word in parsed.detected["semantic"]


def test_explicit_subcategory_hint_keeps_output_filter():
    parsed = parse_smart_query("adjustable holder", subcategory_hint="Voltage Regulators - Linear, Low Drop Out (LDO) Regulators")

    assert any(f.name == "Output Type" and f.value == "Adjustable" for f in parsed.spec_filters)
    assert parsed.detected["semantic"] == ["adjustable"]


async def test_untyped_search_has_no_output_type_filter(local_client):
    result = (await local_client.call_tool("jlc_search", {
        "query": UNTYPED_QUERY, "match_all_terms": False, "limit": 20,
    })).structured_content

    assert not any(f["name"] == "Output Type" for f in result["filters_applied"].get("spec_filters", []))
    assert "semantic" not in result["parsed"]["detected"]


@pytest.mark.parametrize("part_type", ["inductor", "standoff"])
async def test_resolved_part_type_still_reports_adjusted_filter(local_client, part_type):
    result = (await local_client.call_tool("jlc_search", {
        "query": f"adjustable {part_type}", "limit": 1,
    })).structured_content

    assert not any(f["name"] == "Output Type" for f in result["filters_applied"].get("spec_filters", []))
    assert any(f["filter"] == "Output Type = Adjustable" and f["now"] is None
               for f in result["parsed"]["adjusted_filters"])
