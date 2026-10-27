"""Batch 3 alternatives regressions: check every candidate using local frozen catalog data."""

from contextlib import ExitStack
from pathlib import Path
import sys
import re

from fastmcp import Client
import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp import db
from pcbparts_mcp.alternatives import COMPATIBILITY_RULES, is_compatible_alternative, is_stated
from pcbparts_mcp.parsers import parse_voltage

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import local_alternatives, offline


@pytest.fixture
async def alternatives_client():
    # Use JLCPCB_DB_PATH when supplied, as in the documented full verification command.
    with ExitStack() as stack:
        stack.enter_context(offline())
        async with Client(server.mcp) as client:
            with local_alternatives(server._client, db.get_db()):
                yield client


async def alternatives(client, lcsc, **kwargs):
    reply = await client.call_tool("jlc_find_alternatives", {"lcsc": lcsc, **kwargs})
    return reply.structured_content


@pytest.mark.parametrize("lcsc,fields", [
    ("C2765186", ["Number of Contacts", "Mounting Type"]),
    ("C424093", ["The Chip Type"]),
    ("C173752", ["Reference Series", "Mounting Type"]),
])
async def test_connector_and_battery_requirements(alternatives_client, lcsc, fields):
    result = await alternatives(alternatives_client, lcsc, limit=50)
    original = result["original"]["specs"]
    assert result["alternatives"] or result.get("unverified_alternatives")
    for part in result["alternatives"]:
        for field in fields:
            if is_stated(original.get(field)):
                assert part["specs"].get(field) == original[field], part


async def test_module_chip_and_memory(alternatives_client):
    result = await alternatives(alternatives_client, "C2913202", limit=50)
    assert result["alternatives"] or result.get("unverified_alternatives")
    for part in result["alternatives"]:
        assert part["model"].startswith("ESP32-S3-"), part
        memory = re.search(r"-N(\d+)R(\d+)", part["model"])
        assert memory and int(memory[1]) >= 16 and int(memory[2]) >= 8
    for part in result["unverified_alternatives"]:
        assert part["unchecked_requirements"]


@pytest.mark.parametrize("lcsc,same_package", [("C9864", True), ("C82942", False)])
async def test_regulator_ranges_and_disclosures(alternatives_client, lcsc, same_package):
    result = await alternatives(alternatives_client, lcsc, same_package=same_package, limit=50)
    assert result["alternatives"]
    for part in result["alternatives"]:
        orig = result["original"]["specs"]
        for field in ("Output Voltage", "Voltage - Supply"):
            original_bounds = [parse_voltage(v) for v in orig[field].split("~")]
            candidate_bounds = [parse_voltage(v) for v in part["specs"][field].split("~")]
            assert candidate_bounds[-1] >= original_bounds[-1]
            if len(original_bounds) == 2:
                assert len(candidate_bounds) == 2 and candidate_bounds[0] <= original_bounds[0]
        assert "pinout" in part["unchecked_requirements"]
    assert result["confidence"]["level"] != "high"
    assert "all critical specs verified" not in result["confidence"]["reason"].lower()


@pytest.mark.parametrize("lcsc", ["C25744", "C25804", "C1525", "C9002"])
async def test_same_package_first_within_library_tier(alternatives_client, lcsc):
    result = await alternatives(alternatives_client, lcsc, limit=50)
    assert result["alternatives"]
    original_package = result["original"]["package"]
    for no_fee in (True, False):
        tier = [p for p in result["alternatives"] if (p["library_type"] in ("basic", "preferred")) == no_fee]
        same = [p["package"] == original_package for p in tier]
        assert same == sorted(same, reverse=True)


async def test_no_fee_empty_message_counts_extended(alternatives_client):
    result = await alternatives(alternatives_client, "C6186", library_type="no_fee")
    assert result["summary"]["found"] == 0
    assert "No basic/preferred" in result["summary"]["message"]
    assert "extended" in result["summary"]["message"]
    assert result["summary"]["extended_count"] > 0


async def test_mpn_argument_is_actionable(alternatives_client):
    result = await alternatives(alternatives_client, "AMS1117-3.3")
    assert "lcsc must be" in result["error"]
    assert "jlc_get_part(mpn=" in result["error"]


async def test_project_savings_do_not_repeat_assembly_fee(alternatives_client):
    result = await alternatives(alternatives_client, "C5137636", board_quantity=100, placements_per_board=4)
    for part in result["alternatives"]:
        assert "total_per_unit" not in part
    savings = result["comparison"]["savings"]
    assert "total_per_unit" not in savings
    assert savings["component_quantity"] == 400
    assert savings["order_total"] == pytest.approx(savings["assembly_fee"] + 400 * savings["unit_price_diff"], abs=0.0001)


async def test_verified_must_match_values_are_present(alternatives_client):
    for lcsc in ("C2913202", "C20917", "C25804", "C1525", "C9002"):
        result = await alternatives(alternatives_client, lcsc, limit=50)
        rules = COMPATIBILITY_RULES[result["original"]["subcategory"]]
        required = {rules["primary"], *rules.get("must_match", [])}
        for part in result["alternatives"]:
            assert not required.intersection(part["specs_unparseable"]), part


@pytest.mark.parametrize("original,candidate,maximum_only,expected", [
    ("5.5V~36V", "5.5V~32V", True, False),
    ("5.5V~36V", "6V~40V", True, False),
    ("1.221V~32.04V", "1.222V~26V", False, False),
    ("5.5V~36V", "4.5V~40V", True, True),
    ("5.5V~36V", "40V", True, None),
    ("6V", "5.5V", True, False),
    ("6V", "5.9V", True, False),
    ("2.7V~5.5V", "2.75V~5.5V", True, False),
    ("6V", "1.8V~6V", True, True),
    ("6V", "12V~18V", True, False),
    ("6V", "1V~3V、8V~12V", True, False),
    ("1V~2V、4V~5V", "1V~5V", False, True),
    ("1V~5V", "1V~2V、4V~5V", False, False),
    ("-15V~-5V", "-20V~-3V", False, True),
    ("1V~5V", "1V~unknown", False, None),
])
def test_complete_range_coverage(original, candidate, maximum_only, expected):
    from pcbparts_mcp.alternatives import voltage_range_covers

    assert voltage_range_covers(original, candidate, maximum_only) is expected


async def test_unknown_module_specs_stay_unverified_and_inference_works(alternatives_client, monkeypatch):
    # Isolate retrieval so missing and placeholder fields cannot be hidden by SQL prefilters.
    original = db.get_db().get_by_lcsc("C2913202")
    rows = []
    for code, model, specs in [
        ("C100", "ESP32-S3-WROOM-1-N32R16", {"Voltage - Supply": "3V~3.6V"}),
        ("C101", "UNKNOWN", {}),
        ("C102", "UNKNOWN", {"Voltage - Supply": "-", "Utilized IC / Part": "-"}),
        ("C103", "ESP32-S3-WROOM-1-N8R8", original["specs"]),
        ("C104", "ESP32-WROVER-E-N16R8", {"Voltage - Supply": "3V~3.6V"}),
    ]:
        rows.append({**original, "lcsc": code, "model": model, "specs": specs})

    async def search(**kwargs):
        return {"results": rows}

    monkeypatch.setattr(server._client, "search", search)
    monkeypatch.setattr(server._client, "_alternative_candidates", None)
    result = await alternatives(alternatives_client, "C2913202")
    assert result["alternatives"] == []
    assert {p["lcsc"] for p in result["unverified_alternatives"]} == {"C100", "C101", "C102"}
    for part in result["unverified_alternatives"]:
        assert "Utilized IC / Part" in part["unverified_requirements"]
        assert "Utilized IC / Part" not in part["specs_verified"]
        if part["lcsc"] == "C100":
            assert {"Module Flash", "Module PSRAM"} <= set(part["specs_verified"])
        else:
            assert "Voltage - Supply" in part["unverified_requirements"]


@pytest.mark.parametrize("chip,family", [
    ("ESP32-DOWD", "ESP32"), ("ESP32-D0WD-V3", "ESP32"),
    ("ESP32-U4WDH", "ESP32"), ("ESP32-PICO-V3-02", "ESP32"), ("ESP32 Chip", "ESP32"),
    ("ESP32-S3R8", "ESP32-S3"), ("ESP32-S3FN8 Chip", "ESP32-S3"),
    ("ESP32-C3FH4", "ESP32-C3"),
])
@pytest.mark.parametrize("reverse", [False, True])
def test_stated_and_inferred_module_chips_are_unverified(chip, family, reverse):
    original = {"model": f"{family}-WROOM-32D-N4",
                "specs": {"Voltage - Supply": "3V~3.6V", "Utilized IC / Part": chip}}
    candidate = {"model": f"{family}-WROOM-32D-N16", "specs": {"Voltage - Supply": "3V~3.6V"}}
    if reverse:
        original["model"] = original["model"].replace("-N4", "-N16")
        original, candidate = candidate, original
    compatible, info = is_compatible_alternative(original, candidate, "WiFi Modules")
    assert compatible
    assert "Utilized IC / Part" in info["specs_unparseable"]
    assert "Utilized IC / Part" in info["unverified_requirements"]
    assert "Utilized IC / Part" not in info["specs_verified"]


def test_two_inferred_classic_module_chips_are_unverified():
    original = {"model": "ESP32-SOLO-1", "specs": {"Voltage - Supply": "3V~3.6V"}}
    candidate = {"model": "ESP32-WROVER-E", "specs": {"Voltage - Supply": "3V~3.6V"}}
    compatible, info = is_compatible_alternative(original, candidate, "WiFi Modules")
    assert compatible
    assert "Utilized IC / Part" in info["specs_unparseable"]
    assert "Utilized IC / Part" in info["unverified_requirements"]
    assert "Utilized IC / Part" not in info["specs_verified"]


@pytest.mark.parametrize("family", ["ESP32-S3", "ESP32-C3", "ESP32-C6", "ESP32-S2", "ESP32-H2", "ESP32-P4"])
def test_different_inferred_module_families_are_rejected(family):
    original = {"model": "ESP32-SOLO-1", "specs": {"Voltage - Supply": "3V~3.6V"}}
    candidate = {"model": f"{family}-WROOM-1", "specs": {"Voltage - Supply": "3V~3.6V"}}
    assert not is_compatible_alternative(original, candidate, "WiFi Modules")[0]


def test_non_esp32_stated_chip_keeps_exact_comparison():
    original = {"model": "ESP32-S3-WROOM-1", "specs": {"Voltage - Supply": "3V~3.6V", "Utilized IC / Part": "LX7 Chip"}}
    candidate = {"model": "ESP32-S3-WROOM-1", "specs": {"Voltage - Supply": "3V~3.6V"}}
    assert not is_compatible_alternative(original, candidate, "WiFi Modules")[0]


@pytest.mark.parametrize("original_library,replacement_library,fee", [
    ("extended", "basic", 3), ("basic", "extended", -3), ("extended", "extended", 0),
])
def test_project_savings_accounts_for_both_fees(original_library, replacement_library, fee):
    from pcbparts_mcp.alternatives import build_response

    original = {"library_type": original_library, "price": 0.2}
    candidate = {"library_type": replacement_library, "price": 0.1}
    scored = [(0, candidate, {}, {"specs_verified": [], "specs_unparseable": []})]
    result = build_response(original, scored, "Chip Resistor - Surface Mount", "Resistance", "10kΩ", 10,
                            board_quantity=100, placements_per_board=4)
    savings = result["comparison"]["savings"]
    assert savings["assembly_fee"] == fee
    assert savings["order_total"] == fee + 40


@pytest.mark.parametrize("kwargs", [{"board_quantity": 0}, {"placements_per_board": -1}])
async def test_invalid_project_quantity(alternatives_client, kwargs):
    result = await alternatives(alternatives_client, "C25804", **kwargs)
    assert result["error"] == "board_quantity and placements_per_board must be positive integers"
