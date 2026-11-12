"""Exact opt-in facets, checked against independently paginated real search results."""

import json
from collections import Counter
from types import SimpleNamespace

import pytest

from pcbparts_mcp import server
from pcbparts_mcp.search import facets as facet_work
from pcbparts_mcp.search.diagnostics import (
    DIAGNOSTIC_POST_ROWS, DIAGNOSTIC_SECONDS, DIAGNOSTIC_VM_STEPS,
)
from pcbparts_mcp.search.engine import CompiledSearch


CASES = [
    {"query": "100nF 0402 capacitor"},
    {"subcategory_id": 2956, "package": "SOT-23-5",
     "spec_filters": [{"name": "Output Voltage", "op": "=", "value": "3.3V"}]},
    {"query": "USB-C receptacle"},
    {"query": "Bluetooth"},
    {"query": "10k resistor", "manufacturer": "Yageo"},
    {"query": "capacitor", "package": "0402"},
    {"query": "dual edge mount USB-C receptacle"},
    {"subcategory_id": 2956, "package": "SOT-23-5", "spec_filters": [
        {"name": "Output Voltage", "op": "=", "value": "3.3V"},
        {"name": "Output Voltage", "op": "=", "value": "-5V"}]},
    {"query": "ESP32-S3 module 8MB flash"},
    {"query": "100nF 0402 capacitor", "library_type": "no_fee"},
    {"query": "USB-C receptacle", "pcba_type": "economic"},
]


async def call(**args):
    result = await server.jlc_search(**args)
    assert "error" not in result, result
    assert "_facet_plan" not in result
    return result


async def enumerate_results(args):
    # Use the public result pages without facets: no facet SQL or counters are reused.
    parts = []
    while True:
        page = await call(**args, limit=100, offset=len(parts))
        assert page.get("counts_complete", True)
        parts.extend(page["results"])
        if len(parts) == page["total"]:
            break
        assert page["results"]
    assert len({p["lcsc"] for p in parts}) == len(parts)
    return parts


@pytest.mark.parametrize("args", CASES)
async def test_exact_facets_against_real_results(args, monkeypatch):
    # Correctness is independent of machine speed; production budgets are tested separately.
    monkeypatch.setattr(facet_work, "FACET_SECONDS", 5)
    monkeypatch.setattr(facet_work, "FACET_VM_STEPS", 100_000_000)
    monkeypatch.setattr(facet_work, "FACET_POST_ROWS", 50_000)
    result = await call(**args, facets=True, limit=3)
    facets = result["facets"]
    assert facets["status"] == "complete"
    assert facets["complete"] is True
    assert facets["scope"] == "filtered_snapshot"
    assert facets["elapsed_ms"] >= 0
    parts = await enumerate_results(args)
    assert facets["matched_total"] == len(parts) > 0
    for field in ("manufacturer", "package", "library_type"):
        counts = Counter(p[field] for p in parts)
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0] or ""))
        expected = [{"value": value, "count": count} for value, count in ordered[:15]]
        facet = facets[field]
        assert facet["buckets"] == expected
        assert facet["omitted_buckets"] == max(0, len(counts) - 15)
        assert facet["omitted_count"] == sum(count for _, count in ordered[15:])
        assert sum(b["count"] for b in facet["buckets"]) + facet["omitted_count"] == len(parts)
    assert {b["value"] for b in facets["library_type"]["buckets"]} <= {"basic", "preferred", "extended"}
    if args.get("library_type") == "no_fee":
        assert {b["value"] for b in facets["library_type"]["buckets"]} <= {"basic", "preferred"}
    if args.get("query", "").startswith("dual edge"):
        assert "relaxed" in result


@pytest.mark.parametrize("args", [CASES[0], CASES[1], CASES[6]])
async def test_pagination_invariance_and_default_off_bytes(args, monkeypatch):
    monkeypatch.setattr(facet_work, "FACET_SECONDS", 5)
    first = await call(**args, facets=True, limit=1)
    later = await call(**args, facets=True, limit=7, offset=20)
    first_facets = first.pop("facets")
    later_facets = later.pop("facets")
    first_facets.pop("elapsed_ms")
    later_facets.pop("elapsed_ms")
    assert first_facets == later_facets
    default = await call(**args, limit=1)
    explicit = await call(**args, facets=False, limit=1)
    assert "facets" not in default
    assert json.dumps(first) == json.dumps(default) == json.dumps(explicit)


@pytest.mark.parametrize("budget,value,args", [
    ("FACET_SECONDS", 0, {"subcategory_id": 2929}),
    ("FACET_VM_STEPS", 1, {"subcategory_id": 2980}),
    ("FACET_POST_ROWS", 1, CASES[1]),
])
async def test_budget_exhaustion_preserves_results(budget, value, args, monkeypatch):
    expected = await call(**args, limit=3)
    monkeypatch.setattr(facet_work, budget, value)
    actual = await call(**args, limit=3, facets=True)
    facets = actual.pop("facets")
    assert json.dumps(actual) == json.dumps(expected)
    assert facets["status"] == "incomplete"
    assert facets["complete"] is False
    assert facets["matched_total"] is None
    assert not {"manufacturer", "package", "library_type"} & facets.keys()


def test_default_budgets_match_diagnostics():
    assert facet_work.FACET_SECONDS == DIAGNOSTIC_SECONDS == 0.2
    assert facet_work.FACET_VM_STEPS == DIAGNOSTIC_VM_STEPS == 2_000_000
    assert facet_work.FACET_POST_ROWS == DIAGNOSTIC_POST_ROWS == 5_000


def test_unavailable_snapshot(tmp_path):
    result = facet_work.collect_facets(SimpleNamespace(db_path=tmp_path / "missing.db"),
                                       CompiledSearch("WHERE stock >= ?", [10], []))
    assert result["status"] == "unavailable"
    assert result["matched_total"] is None
    assert result["complete"] is False
    assert not (tmp_path / "missing.db").exists()


async def test_strict_error_has_no_exact_facets():
    result = await server.jlc_search(query="mosfet excluding AO3400", strict=True, facets=True)
    assert result.get("error")
    # Validation can fail before a search is compiled; any reported facets must be unavailable.
    if "facets" in result:
        assert result["facets"]["status"] == "unavailable"
        assert result["facets"]["matched_total"] is None


@pytest.mark.parametrize("query", ["FUSB302B USB PD", "nSMD005/60V 1206 fuse"])
async def test_part_type_retry_facets_use_kept_mpns(query, monkeypatch):
    monkeypatch.setattr(facet_work, "FACET_SECONDS", 5)
    result = await call(query=query, facets=True, limit=1)
    assert "dropped_part_type" in result["relaxed"]
    parts = await enumerate_results({"query": query})
    facets = result["facets"]
    assert facets["complete"]
    assert facets["matched_total"] == len(parts) > 1
    for field in ("manufacturer", "package", "library_type"):
        counts = Counter(p[field] for p in parts)
        assert {b["value"]: b["count"] for b in facets[field]["buckets"]} == counts


def test_engine_mpn_normalization_captures_successful_variant(monkeypatch):
    monkeypatch.setattr(facet_work, "FACET_SECONDS", 5)
    db = server.get_db()
    result = db.search(query="STM32F103C8T6-TR", capture_plan=True, limit=100)
    assert result["mpn_normalized"]["matched_query"] == "STM32F103C8T6"
    facets = facet_work.collect_facets(db, result.pop("_facet_plan"))
    independently_searched = db.search(query="STM32F103C8T6", limit=100)
    assert facets["status"] == "complete"
    assert facets["matched_total"] == independently_searched["total"] > 0
    for field in ("manufacturer", "package", "library_type"):
        counts = Counter(p[field] for p in independently_searched["results"])
        assert {b["value"]: b["count"] for b in facets[field]["buckets"]} == counts


async def test_empty_final_search_has_exact_zero_facets():
    result = await call(subcategory_id=2929, manufacturer="facet-test-no-such-manufacturer", facets=True)
    facets = result["facets"]
    assert result["total"] == facets["matched_total"] == 0
    assert facets["status"] == "complete"
    for field in ("manufacturer", "package", "library_type"):
        assert facets[field] == {"buckets": [], "omitted_buckets": 0, "omitted_count": 0}


def test_capture_plan_is_not_reported_as_a_constraint(monkeypatch):
    """facets=true marks the search to keep its plan; why_empty listed that as a retained constraint."""
    from pcbparts_mcp import server
    seen = {}

    def fake_diagnose(db, query, args):
        seen.update(args)
        return {}
    import pcbparts_mcp.search.diagnostics as diagnostics
    monkeypatch.setattr(diagnostics, "diagnose_empty", fake_diagnose)
    import asyncio, inspect
    r = server.jlc_search(query="zzqqxx no such part 123456789", facets=True)
    asyncio.run(r) if inspect.isawaitable(r) else r
    assert seen and "capture_plan" not in seen


async def test_why_empty_budget_exhaustion_is_reported_not_logged_as_failure(monkeypatch, caplog):
    """A why_empty counterfactual that runs out of budget was caught inside the search engine,
    logged as "Search SQL execution failed" with a traceback and returned as a "query too complex"
    error, so diagnostics never said its budget ran out (10 such logs per 3,164-query corpus run)."""
    from pcbparts_mcp.search import diagnostics
    monkeypatch.setattr(diagnostics, "DIAGNOSTIC_VM_STEPS", 1)
    with caplog.at_level("ERROR"):
        result = await server.jlc_search(subcategory_id=2956, package="0201", limit=1)
    assert result["total"] == 0
    assert result["why_empty"]["status"] == "budget_exhausted_or_busy"
    assert result["why_empty"]["diagnostics_complete"] is False
    assert not [r for r in caplog.records if "Search SQL execution failed" in r.getMessage()]


@pytest.mark.parametrize("args", [
    {"query": "supercapacitor"},             # early hint: no supercapacitor subcategory
    {"query": "LDO not AMS1117"},            # part-number exclusion error
    {"query": "x", "library_type": "bogus"},  # argument error
])
async def test_facets_block_on_every_reply(args):
    """facets=true promises a facets block; early hints and argument errors returned without one
    (server review, 2026-11-10)."""
    result = await server.jlc_search(**args, facets=True, limit=1)
    assert result["facets"]["status"] == "unavailable"
    assert "facets" not in await server.jlc_search(**args, limit=1)
