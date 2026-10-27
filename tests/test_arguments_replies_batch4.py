"""Batch 4A argument/reply regressions, using only the local catalog."""

import json
import re
import sqlite3
from pathlib import Path
import sys

from fastmcp import Client
import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp import db
from pcbparts_mcp.boards_db.detail import get_consensus
from pcbparts_mcp.design_rules import get_design_rules
from pcbparts_mcp.parsers import parse_esp32_module_memory

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import local_alternatives, offline


@pytest.fixture
async def client():
    with offline():
        async with Client(server.mcp) as value:
            yield value


async def call(client, **args):
    return (await client.call_tool("jlc_search", args)).structured_content


async def test_bare_package_is_required(client):
    result = await call(client, query="100nF capacitor", packages="0603", limit=3)
    assert result["results"]
    assert result["filters_applied"]["packages"] == ["0603"]
    assert all(p["package"] == "0603" for p in result["results"])


@pytest.mark.parametrize("filters", [
    [{"name": "Id", "op": "=>", "value": 3}],
    '[{"name":"Id","op":"=>","value":3}]',
])
async def test_numeric_filter_and_operator_spelling(client, filters):
    result = await call(client, subcategory_name="MOSFETs", spec_filters=filters, limit=3)
    assert result["results"]
    assert result["filters_applied"]["spec_filters"] == [{"name": "Id", "op": ">=", "value": "3"}]
    assert "ignored_filters" not in result


@pytest.mark.parametrize("args", [
    {"packages": '["0603", 2]'}, {"packages": '["0603"'},
    {"spec_filters": '[{"name":"Id","op":"!=","value":"3A"}]'},
    {"spec_filters": 'not json'}, {"spec_filters": [{"name": "Id", "op": "=", "value": {}}]},
])
async def test_malformed_constraints_are_errors(client, args):
    result = await call(client, query="mosfet", **args)
    assert "error" in result and result["valid_values"]


@pytest.mark.parametrize("category,name,suggestion", [
    ("Tactile Switches", "Height", "Switch Height"),
    ("MOSFETs", "Gate Thresh", "Gate Threshold Voltage (Vgs(th))"),
])
async def test_explicit_unknown_attribute_reported(client, category, name, suggestion):
    result = await call(client, subcategory_name=category,
                        spec_filters=[{"name": name, "op": "<=", "value": "2mm"}])
    issue = next(f for f in result["ignored_filters"] if f["filter"].startswith(name))
    assert suggestion in issue["suggestions"]
    assert "few or none" in issue["reason"]


async def test_recovery_hint_names_real_tool(client):
    result = await call(client, subcategory_name="battery chargerzz")
    assert "jlc_search_help(" in result["hint"]
    assert result["similar_subcategories"]
    assert (await client.call_tool("jlc_search_help", {})).structured_content["categories"]


def test_every_design_rule_key_can_be_retrieved():
    for key in get_design_rules("power")["matched_files"]:
        result = get_design_rules(key)
        assert result["matched_files"] == [key]
        assert "No rules found" not in result["content"]


async def test_package_alternatives_match_explicit_or(client):
    natural = await call(client, query="100nF 25V capacitors in 0402 or 0603", limit=100)
    explicit = await call(client, query="100nF 25V capacitors", packages=["0402", "0603"], limit=100)
    assert natural["filters_applied"]["packages"] == ["0402", "0603"]
    assert natural["total"] == explicit["total"]
    assert [p["lcsc"] for p in natural["results"]] == [p["lcsc"] for p in explicit["results"]]
    assert {p["package"] for p in natural["results"]} == {"0402", "0603"}


async def test_final_population_library_counts(client):
    result = await call(client, query="24V input 3.3V output buck converter 1A")
    assert result["total"] > 0
    assert sum(result["library_type_counts"].values()) == result["total"]
    assert result["no_fee_available"] == bool(sum(result["library_type_counts"][t] for t in ("basic", "preferred")))


async def test_compact_default_and_explicit_limit(client):
    result = await call(client, query="n-channel mosfet")
    assert len(result["results"]) == 20
    assert len(json.dumps(result).encode()) < 35000
    assert all("description" not in p for p in result["results"] if p.get("specs"))
    assert all("price_10" not in p for p in result["results"])
    assert len((await call(client, query="n-channel mosfet", limit=100))["results"]) == 100


async def test_query_library_can_relax_but_explicit_cannot(client):
    result = await call(client, query="preferred 10uF 0805 capacitor")
    assert result["total"] > 0
    assert "library preference was left out" in result["relaxed"]["reason"]
    assert result["filters_applied"]["library_type"] is None
    explicit = await call(client, query="10uF 0805 capacitor", library_type="preferred")
    assert explicit["total"] == 0 and "relaxed" not in explicit


@pytest.mark.parametrize("query", ["preferred 10uF 0805 capacitor", "24bit ADC I2C", "3.3V op amp", "flux capacitor 1.21GW"])
async def test_strict_does_not_relax(client, query):
    result = await call(client, query=query, strict=True)
    assert "relaxed" not in result
    if result.get("parsed", {}).get("detected", {}).get("unsupported_constraints") or query == "3.3V op amp":
        assert result.get("ignored_filters") or result["parsed"].get("adjusted_filters")
        assert result["total"] == 0 and "error" in result


def test_n_only_module_has_known_zero_psram():
    assert parse_esp32_module_memory("ESP32-S3-WROOM-1U-N16") == (16, 0)


async def test_n_only_not_unverified_alternative(client):
    with local_alternatives(server._client, db.get_db()):
        result = (await client.call_tool("jlc_find_alternatives", {"lcsc": "C2913202", "limit": 50})).structured_content
    for p in result["alternatives"] + result["unverified_alternatives"]:
        assert not re.search(r"-N\d+(?:$|H\d?$)", p["model"]), p
    result = await call(client, query="ESP32-S3 module 8MB PSRAM", limit=100)
    assert result["results"]
    assert all((parse_esp32_module_memory(p["model"])[1] or 0) >= 8 for p in result["results"])


def test_consensus_counts_distinct_boards():
    conn = sqlite3.connect(":memory:")
    conn.executescript("CREATE TABLE boards(id, slug, neighborhoods_json); CREATE TABLE board_key_ics(board_id, ic); CREATE TABLE board_components(board_id, ref, value);")
    for i, quantity in enumerate((5, 1), 1):
        hood = [{"value": "RP2040", "pins": {"VCC": [{"value": "100nF", "role": "decoupling"}] * quantity}}]
        conn.execute("INSERT INTO boards VALUES (?, ?, ?)", (i, f"board-{i}", json.dumps(hood)))
        conn.execute("INSERT INTO board_key_ics VALUES (?, ?)", (i, "RP2040"))
    result = get_consensus(conn, "RP2040")
    choice = result["pins"]["VCC"]["top_choices"][0]
    assert choice["count"] == 2 and choice["pct"] == 100
    assert choice["boards"] == ["board-1", "board-2"]
    assert choice["quantities"] == {"board-1": 5, "board-2": 1}
    assert result["board_count"] == 2
    conn.close()


async def test_strict_keeps_unmatched_words(client):
    result = await call(client, query="dual n-channel mosfet edge mount", strict=True)
    assert result["filters_applied"]["query"] == "edge mount"
    assert result["total"] == 0 and "relaxed" not in result
    result = await call(client, query="ESP32-S3-WROOM-1 impossibleword", strict=True)
    assert "impossibleword" in result["filters_applied"]["query"]
    assert result["total"] == 0 and "relaxed" not in result
    result = await call(client, query="RJ45 with magnetics", strict=True)
    assert "magnetics" in result["filters_applied"]["query"]
    result = await call(client, query="5V USB connector", strict=True)
    assert result["error"] and result["ignored_filters"] and result["total"] == 0


async def test_strict_reports_explicit_unsupported_filters(client):
    result = await call(client, subcategory_name="MOSFETs", strict=True,
                        spec_filters=[{"name": "Gate Thresh", "op": "<", "value": "1.5V"}])
    assert result["error"] and result["total"] == 0 and result["ignored_filters"]
    assert "relaxed" not in result


async def test_strict_keeps_applied_sparse_filter_results(client):
    args = {"subcategory_name": "Operational Amplifier", "limit": 3,
            "spec_filters": [{"name": "Supply Voltage", "op": "=", "value": "5V"}]}
    normal = await call(client, **args)
    strict = await call(client, **args, strict=True)
    assert normal["results"] and strict["results"] == normal["results"]
    assert strict["total"] == normal["total"]
    assert "error" not in strict
    assert strict["ignored_filters"] == normal["ignored_filters"]
    assert strict["ignored_filters"][0]["reason"].startswith("applied, but few or none")


async def test_many_unknown_explicit_filters_are_reported(client):
    filters = [{"name": f"Bogus attribute {i}", "op": "=", "value": "unknown"} for i in range(50)]
    result = await call(client, subcategory_id=2980, spec_filters=filters, limit=3)
    assert "error" not in result
    assert {issue["filter"] for issue in result["ignored_filters"]} == {
        f"{f['name']} = unknown" for f in filters
    }


async def test_flash_megabit_queries(client):
    flash = await call(client, query="spi flash 128Mb", limit=100)
    assert any(p["model"] == "W25Q128JVSIQ" for p in flash["results"])
    assert any(p["specs"].get("Memory Size") == "128Mbit" for p in flash["results"])
    family = await call(client, query="W25Q64 64Mb flash", limit=100)
    assert family["results"] and "relaxed" not in family
    assert all("W25Q64" in p["model"] for p in family["results"])
    modules = await call(client, query="ESP32-S3 module 64Mb flash", limit=100)
    assert modules["results"]
    assert all((parse_esp32_module_memory(p["model"])[0] or 0) >= 8 for p in modules["results"])


async def test_filter_names_and_sort_ignore_case(client):
    result = await call(client, subcategory_name="MOSFETs", sort_by="PRICE", library_type="BASIC",
                        spec_filters=[{"name": "vgs(th)", "op": "<", "value": 1.5}])
    assert result["results"] and "ignored_filters" not in result
    assert all(p["library_type"] == "basic" for p in result["results"])


async def test_library_counts_include_explicit_library_constraint(client):
    result = await call(client, query="n-channel mosfet", library_type="extended")
    assert result["library_type_counts"]["basic"] == result["library_type_counts"]["preferred"] == 0
    assert result["library_type_counts"]["extended"] == result["total"]
    assert result["no_fee_available"] is False


async def test_capped_post_filter_counts_are_labeled(client, monkeypatch):
    from pcbparts_mcp.search import engine
    monkeypatch.setattr(engine, "POST_FILTER_SCAN_ROWS", 5)
    result = await call(client, query="24V input 3.3V output buck converter 1A")
    assert result["counts_complete"] is False
    assert sum(result["library_type_counts"].values()) == result["total"]


async def test_stock_list_arguments_are_preserved(client, monkeypatch):
    from unittest.mock import AsyncMock
    search = AsyncMock(return_value={"results": [], "total": 0})
    monkeypatch.setattr(server._client, "search", search)
    result = (await client.call_tool("jlc_stock_check", {
        "packages": "SMD,4x4mm", "manufacturers": "Example, Inc.",
        "library_type": "NO-FEE", "sort_by": "PRICE",
    })).structured_content
    assert "error" not in result
    assert search.await_args.kwargs["packages"] == ["SMD,4x4mm"]
    assert search.await_args.kwargs["manufacturers"] == ["Example, Inc."]
    assert search.await_args.kwargs["library_type"] == "no_fee"
    assert search.await_args.kwargs["sort_by"] == "price"
    result = (await client.call_tool("jlc_stock_check", {"manufacturers": '[1]'})).structured_content
    assert result["error"] and result["valid_values"]
    assert search.await_count == 1


async def test_combined_query_library_and_text_relaxation(client):
    result = await call(client, query="preferred 10uF 0805 capacitor impossibleword")
    assert result["total"] > 0
    assert "library preference was left out" in result["relaxed"]["reason"]
    assert "impossibleword" in result["relaxed"]["dropped_text"]
    assert result["filters_applied"]["library_type"] is None


async def test_strict_reports_overridden_requirements(client):
    for args in [
        {"query": "100nF capacitor 0402", "package": "0603"},
        {"query": "basic 100nF capacitor", "library_type": "extended"},
        {"query": "10k resistor", "spec_filters": [{"name": "Resistance", "op": "=", "value": "1k"}]},
    ]:
        result = await call(client, strict=True, **args)
        assert result["error"] and result["parsed"]["adjusted_filters"]
        assert result["total"] == result["page_info"]["returned"] == 0
        assert "relaxed" not in result


def test_rule_index_key_can_be_retrieved():
    assert get_design_rules("INDEX.md")["matched_files"] == ["INDEX.md"]


async def test_numeric_module_memory_uses_bytes(client):
    result = await call(client, subcategory_name="WiFi Modules",
                        spec_filters=[{"name": "Module PSRAM", "op": ">=", "value": 8 * 1024 * 1024}])
    assert result["results"] and "ignored_filters" not in result
    assert all((parse_esp32_module_memory(p["model"])[1] or 0) >= 8 for p in result["results"])


async def test_explicit_unapplied_filter_keeps_query_builder_reason(client):
    result = await call(client, subcategory_name="MOSFETs",
                        spec_filters=[{"name": "Gate Thresh", "op": "<", "value": "1.5V"}])
    unfiltered = await call(client, subcategory_name="MOSFETs")
    issue = result["ignored_filters"][0]
    assert result["total"] == unfiltered["total"]
    assert issue["reason"].startswith("not applied (")
    assert "isn't numeric" in issue["reason"]
    assert "Gate Threshold Voltage (Vgs(th))" in issue["suggestions"]


async def test_explicit_applied_rare_filter_reports_incomplete_results(client):
    result = await call(client, subcategory_name="Tactile Switches",
                        spec_filters=[{"name": "Height", "op": "<=", "value": "2mm"}])
    assert result["total"] == 0
    issue = result["ignored_filters"][0]
    assert issue["reason"].startswith("applied, but few or none")
    assert "incomplete or empty" in issue["reason"]
    assert "Switch Height" in issue["suggestions"]


async def test_explicit_unparseable_rare_filter_is_not_applied(client):
    result = await call(client, subcategory_name="Tactile Switches",
                        spec_filters=[{"name": "Height", "op": "<=", "value": "unknown"}])
    issue = result["ignored_filters"][0]
    assert issue["reason"].startswith("not applied (")
    assert "couldn't read" in issue["reason"]
    assert "Switch Height" in issue["suggestions"]


@pytest.mark.parametrize("strict", [False, True])
async def test_gate_threshold_alias_matches_existing_alias(client, strict):
    args = {"subcategory_name": "MOSFETs", "limit": 100, "strict": strict}
    alias = await call(client, **args, spec_filters=[{"name": "Gate Threshold", "op": "<", "value": "1.5V"}])
    existing = await call(client, **args, spec_filters=[{"name": "Vgs(th)", "op": "<", "value": "1.5V"}])
    assert alias["results"] and alias["total"] == existing["total"]
    assert alias["results"] == existing["results"]
    assert "ignored_filters" not in alias
