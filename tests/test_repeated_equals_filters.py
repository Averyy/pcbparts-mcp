"""Repeated equality filters retain each single filter's matching semantics."""

import sys
from pathlib import Path

from fastmcp import Client
import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.db import get_db
from pcbparts_mcp.search.spec_filter import SpecFilter

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline


LDO = "Voltage Regulators - Linear, Low Drop Out (LDO) Regulators"


@pytest.fixture
async def local_client():
    with offline():
        async with Client(server.mcp) as client:
            yield client


def equals(name, *values):
    return [{"name": name, "op": "=", "value": value} for value in values]


def catalog_matches(subcategory, filters):
    """Read complete control sets without the tool's 100-result page limit."""
    result = get_db().search(
        subcategory_name=subcategory,
        library_type="all",
        spec_filters=[SpecFilter(f["name"], f["op"], f["value"]) for f in filters],
        limit=100_000,
    )
    assert "error" not in result, result
    assert result.get("counts_complete", True)
    assert len(result["results"]) == result["total"]
    return {part["lcsc"]: part for part in result["results"]}


async def search(client, subcategory, filters, **kwargs):
    result = (await client.call_tool("jlc_search", {
        "subcategory_name": subcategory,
        "library_type": "all",
        "spec_filters": filters,
        "strict": True,
        "limit": 100,
        **kwargs,
    })).structured_content
    assert "error" not in result, result
    assert result.get("counts_complete", True)
    return result


async def test_output_voltage_union_and_paging(local_client):
    first = catalog_matches(LDO, equals("Output Voltage", "3.3V"))
    second = catalog_matches(LDO, equals("Output Voltage", "5V"))
    expected = first | second
    assert first and second and first.keys() & second.keys()

    filters = equals("Output Voltage", "3.3V", "5V")
    assert catalog_matches(LDO, filters).keys() == expected.keys()
    tier = {"basic": 0, "preferred": 1, "extended": 2}
    ordered = sorted(expected, key=lambda code: (
        tier[expected[code]["library_type"]], -expected[code]["stock"], code,
    ))
    for offset in (0, 100, max(0, len(expected) - 50)):
        result = await search(local_client, LDO, filters, offset=offset)
        assert result["total"] == len(expected)
        assert [part["lcsc"] for part in result["results"]] == ordered[offset:offset + 100]
        assert result["library_type_counts"] == {
            library: sum(part["library_type"] == library for part in expected.values())
            for library in tier
        }


async def test_adjustable_output_part_in_group(local_client):
    single = await search(local_client, LDO, equals("Output Voltage", "3.3V"), query="C75510")
    if not single["results"]:
        pytest.skip("C75510 is not available in this catalog snapshot")
    assert {part["lcsc"] for part in single["results"]} == {"C75510"}
    grouped = await search(local_client, LDO, equals("Output Voltage", "3.3V", "5V"), query="C75510")
    assert {part["lcsc"] for part in grouped["results"]} == {"C75510"}


async def test_supply_values_still_intersect(local_client):
    first = catalog_matches("Logic Gates", equals("Supply Voltage", "3.3V"))
    second = catalog_matches("Logic Gates", equals("Supply Voltage", "12V"))
    expected = first.keys() & second.keys()
    assert expected
    filters = equals("Supply Voltage", "3.3V", "12V")
    assert catalog_matches("Logic Gates", filters).keys() == expected
    result = await search(local_client, "Logic Gates", filters)
    assert result["total"] == len(expected)
    assert {part["lcsc"] for part in result["results"]} <= expected


@pytest.mark.parametrize("subcategory,name,values", [
    ("Multilayer Ceramic Capacitors MLCC - SMD/SMT", "Temperature Coefficient", ("X7R", "X5R")),
    ("Tantalum Capacitors", "Capacitance", ("22uF", "47uF")),
    ("Chip Resistor - Surface Mount", "Resistance", ("10kΩ", "4.7kΩ")),
])
async def test_categorical_and_scalar_unions(local_client, subcategory, name, values):
    first = catalog_matches(subcategory, equals(name, values[0]))
    second = catalog_matches(subcategory, equals(name, values[1]))
    assert first and second
    expected = first.keys() | second.keys()
    filters = equals(name, *values)
    assert catalog_matches(subcategory, filters).keys() == expected
    result = await search(local_client, subcategory, filters)
    assert result["total"] == len(expected)
    assert {part["lcsc"] for part in result["results"]} <= expected


async def test_mixed_operator_remains_and(local_client):
    upper = {"name": "Output Voltage", "op": "<=", "value": "4V"}
    first = catalog_matches(LDO, [*equals("Output Voltage", "3.3V"), upper])
    second = catalog_matches(LDO, [*equals("Output Voltage", "5V"), upper])
    expected = first.keys() | second.keys()
    assert expected
    filters = [*equals("Output Voltage", "3.3V", "5V"), upper]
    assert catalog_matches(LDO, filters).keys() == expected
    result = await search(local_client, LDO, filters)
    assert result["total"] == len(expected)
    assert {part["lcsc"] for part in result["results"]} <= expected
