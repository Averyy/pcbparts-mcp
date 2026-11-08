"""Real-catalog regressions for the two 2026-11-08 rating-condition reports."""

import sys
from contextlib import ExitStack
from copy import deepcopy
from pathlib import Path

from fastmcp import Client
import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.db import get_db
from pcbparts_mcp.alternatives import build_response, is_compatible_alternative, score_alternative
from pcbparts_mcp.catalog_evidence import annotate_catalog, reviewed_specs
from pcbparts_mcp.search import SpecFilter

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import local_alternatives, offline  # noqa: E402


@pytest.fixture
async def local_client():
    with ExitStack() as stack:
        stack.enter_context(offline())
        async with Client(server.mcp) as client:
            with local_alternatives(server._client, get_db()):
                yield client


async def test_reported_inductor_call_cannot_recommend_unverified_swap(local_client):
    reply = await local_client.call_tool("jlc_find_alternatives", {
        "lcsc": "C913245", "same_package": True, "min_stock": 100,
        "placements_per_board": 3, "board_quantity": 2, "limit": 5,
    })
    result = reply.structured_content
    assert not result["alternatives"]
    assert result["summary"]["found"] == 0
    assert result["search_criteria"]["compatibility_verified"] is False
    assert result["confidence"]["level"] == "low"
    assert result["confidence"]["unchecked_requirements"]
    assert result["comparison"] is None
    candidate = next(p for p in result["unverified_alternatives"] if p["lcsc"] == "C53308978")
    assert "Inductance" in candidate["specs_verified"]
    assert "Current - Saturation(Isat)" not in candidate["specs_verified"]
    assert "Current Rating" not in candidate["specs_verified"]
    assert any("Current - Saturation(Isat)" in r for r in candidate["unverified_requirements"])
    assert candidate["specs"]["DC Resistance(DCR)"] == "20mΩ"
    assert candidate["spec_discrepancies"][0]["datasheet_value"] == "27mΩ"
    assert "JLCPCB" in candidate["no_datasheet_note"]


def test_response_builder_enforces_verification_boundary():
    db = get_db()
    original, candidate = (db.get_by_lcsc(code) for code in ("C913245", "C53308978"))
    eligible, info = is_compatible_alternative(original, candidate, original["subcategory"])
    assert eligible  # It remains available for manual comparison.
    score, breakdown = score_alternative(candidate, original, candidate["price"])
    result = build_response(original, [(score, candidate, breakdown, info)], original["subcategory"],
                            "Inductance", "1uH", 5, board_quantity=2, placements_per_board=3)
    assert result["comparison"] is None
    assert not result["search_criteria"]["compatibility_verified"]
    assert result["summary"]["unverified_count"] == 1


def test_datasheet_evidence_survives_annotation_and_is_not_a_catalog_override():
    part = get_db().get_by_lcsc("C53308978")
    before = deepcopy(part)
    annotate_catalog(part)
    assert part == before  # Idempotent; no duplicate notes.
    assert part["specs"]["DC Resistance(DCR)"] == "20mΩ"
    evidence = part["spec_evidence"]["DC Resistance(DCR)"]
    assert evidence["value"] == "27mΩ" and evidence["basis"] == "maximum"
    assert evidence["document"] == "SRD-WI-22770 Rev A, 2024-06-14"
    assert evidence["printed_page"] == "2/8"
    # A caller changing returned metadata cannot mutate future document evidence.
    part["spec_evidence"]["DC Resistance(DCR)"]["value"] = "20mΩ"
    assert reviewed_specs(part)["DC Resistance(DCR)"]["value"] == "27mΩ"


def test_matching_catalog_numbers_without_document_conditions_stay_unknown():
    db = get_db()
    original, candidate = (db.get_by_lcsc(code) for code in ("C913245", "C5139901"))
    eligible, info = is_compatible_alternative(original, candidate, original["subcategory"])
    assert eligible and info["unverified_requirements"]
    assert "DC Resistance(DCR)" not in info["specs_verified"]
    # The reviewed pair can compare published DCR maxima despite its bad catalog figure.
    candidate = db.get_by_lcsc("C53308978")
    _, info = is_compatible_alternative(original, candidate, original["subcategory"])
    assert "DC Resistance(DCR)" in info["specs_verified"]


async def test_bav99_loading_conditions_and_catalog_filter(local_client):
    result = (await local_client.call_tool("jlc_get_part", {"lcsc": "C2500"})).structured_content
    assert result["specs"]["Current - Rectified"] == "125mA"
    assert "how many diodes are loaded" in result["specs_note"]
    evidence = result["spec_evidence"]["Current - Rectified"]
    assert evidence["single_loaded"] == "215mA"
    assert evidence["both_loaded_per_diode"] == "125mA"
    assert evidence["basis"] == "absolute maximum"
    db = get_db()
    shared = dict(query="BAV99,215", subcategory_name="Switching Diodes", min_stock=0, limit=100)
    assert any(p["lcsc"] == "C2500" for p in db.search(**shared)["results"])
    filtered = db.search(**shared, spec_filters=[SpecFilter("If", ">=", "150mA")])
    assert all(p["lcsc"] != "C2500" for p in filtered["results"])
    single = db.get_by_lcsc("C109218")
    assert "specs_note" not in single
    _, info = is_compatible_alternative(result, result, result["subcategory"])
    assert "Current - Rectified" not in info["specs_verified"]
    assert any("loading" in r for r in info["unverified_requirements"])


def test_common_anode_cathode_and_series_listings_all_warn():
    results = get_db().search(subcategory_name="Switching Diodes", limit=100)["results"]
    pairs = [p for p in results if "Pair" in p["specs"].get("Diode Configuration", "")]
    assert {"1 Pair Series Connection", "1 Pair Common Anode", "1 Pair Common Cathode"} <= {
        p["specs"]["Diode Configuration"] for p in pairs
    }
    for part in pairs:
        assert "loading condition" in part["specs_note"]


@pytest.mark.parametrize("sort_spec,query,expected", [
    ("Isat", "1uH power inductor", "inductance-drop"),
    ("If", "switching diode", "how many diodes"),
])
async def test_sort_discloses_missing_conditions(local_client, sort_spec, query, expected):
    result = (await local_client.call_tool("jlc_search", {
        "query": query, "sort_spec": sort_spec, "limit": 5,
    })).structured_content
    assert expected in result["sort"]["note"]
