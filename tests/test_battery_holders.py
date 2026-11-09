"""Offline battery-holder parsing and catalog search regressions."""

import sqlite3
import sys
from pathlib import Path

from fastmcp import Client
import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.db import get_db
from pcbparts_mcp.search.query_builder import build_spec_filter_clauses, unlisted_clause
from pcbparts_mcp.search.spec_filter import BatterySizeFilter, SpecFilter
from pcbparts_mcp.smart_parser import merge_spec_filters, parse_smart_query
from pcbparts_mcp.subcategory_aliases import BATTERY_HOLDER_SUBCATEGORIES

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline


HOLDER_IDS = {1651, 3742, 2989, 3739}
HOLDER_NAMES = set(BATTERY_HOLDER_SUBCATEGORIES)
SIZE_WORDS = [
    ("AA", "AA"), ("No. 5", "AA"), ("No.5", "AA"), ("14500", "AA"),
    ("AAA", "AAA"), ("No. 7", "AAA"), ("No.7", "AAA"), ("10440", "AAA"),
    ("C", "C"), ("No. 2", "C"), ("D", "D"), ("No. 1", "D"),
    ("coin", "coin"), ("coin cell", "coin"), ("button cell", "coin"),
]


@pytest.fixture
async def local_client():
    with offline():
        async with Client(server.mcp) as client:
            yield client


async def search(client, query, **kwargs):
    result = (await client.call_tool("jlc_search", {
        "query": query, "library_type": "all", "min_stock": 0, "limit": 100, **kwargs,
    })).structured_content
    assert "error" not in result, result
    return result


async def all_parts(client, query, **kwargs):
    first = await search(client, query, **kwargs)
    parts = list(first["results"])
    for offset in range(100, first["total"], 100):
        parts.extend((await search(client, query, offset=offset, **kwargs))["results"])
    assert len(parts) == first["total"]
    return {part["lcsc"]: part for part in parts}


@pytest.mark.parametrize("kind", ["battery", "cell", "coin cell", "button cell"])
@pytest.mark.parametrize("plural", ["", "s"])
def test_holder_aliases_cover_the_holder_subcategories(kind, plural):
    parsed = parse_smart_query(f"{kind} holder{plural}")
    assert parsed.subcategory in HOLDER_NAMES
    assert set(parsed.subcategories) == {*HOLDER_NAMES, "battery accessories"}
    assert {get_db().resolve_subcategory_name(name) for name in parsed.subcategories} == {*HOLDER_IDS, 1303}
    assert not parsed.remaining_text


async def test_holders_filed_under_battery_accessories_are_kept(local_client):
    # C5375989 and C5377561 say "Battery Holder" but are filed under Battery accessories
    found = await all_parts(local_client, "battery holder")
    assert {"C5375989", "C5377561"} <= set(found)
    accessories = [p["lcsc"] for p in found.values() if p["subcategory"] == "Battery accessories"]
    with sqlite3.connect(f"file:{Path('data/components.db').resolve()}?mode=ro", uri=True) as conn:
        listed = dict(conn.execute("SELECT lcsc, lower(mpn || ' ' || ifnull(description, '')) FROM components "
                                   "WHERE subcategory_id = 1303"))
    assert all("holder" in listed[lcsc] for lcsc in accessories)


@pytest.mark.parametrize("query", ["battery charger", "battery management", "AA battery charger"])
def test_battery_management_is_unchanged(query):
    parsed = parse_smart_query(query)
    assert parsed.subcategory == "battery management"
    assert not parsed.subcategories
    assert not any(isinstance(f, BatterySizeFilter) for f in parsed.spec_filters)


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("words,size", SIZE_WORDS)
def test_size_words_are_consumed_and_supported(words, size, strict):
    parsed = parse_smart_query(f"{words} battery holder", strict=strict)
    assert not parsed.remaining_text
    assert [f.to_dict() for f in parsed.spec_filters if isinstance(f, BatterySizeFilter)] == [
        {"name": "Battery Size", "op": "=", "value": size}]
    assert not parsed.detected.get("unsupported_constraints")


@pytest.mark.parametrize("subcategory", BATTERY_HOLDER_SUBCATEGORIES)
@pytest.mark.parametrize("words,size", SIZE_WORDS)
def test_explicit_holder_subcategories_recognize_sizes(subcategory, words, size):
    parsed = parse_smart_query(words, subcategory_hint=subcategory)
    assert not parsed.remaining_text
    assert [f.value for f in parsed.spec_filters if isinstance(f, BatterySizeFilter)] == [size]


@pytest.mark.parametrize("word", ["AA", "C", "D", "14500", "10440", "No.5", "coin"])
def test_size_handling_is_scoped_to_holders(word):
    for hint in (None, "USB Connectors"):
        parsed = parse_smart_query(word, subcategory_hint=hint)
        assert not any(isinstance(f, BatterySizeFilter) for f in parsed.spec_filters)
    if word in ("AA", "C", "D"):
        assert parse_smart_query(word).remaining_text == word


@pytest.mark.parametrize("size", ["18650", "26650", "21700", "32650"])
def test_other_cell_sizes_stay_plain_text(size):
    parsed = parse_smart_query(f"{size} battery holder")
    assert parsed.remaining_text == size
    assert not any(isinstance(f, BatterySizeFilter) for f in parsed.spec_filters)


def test_size_filter_fitting_merging_and_unlisted_counts():
    filters = [f for f in parse_smart_query("14500 AA AAA battery holder").spec_filters
               if isinstance(f, BatterySizeFilter)]
    assert [f.value for f in filters] == ["AA", "AAA"]
    kept, adjusted = server._fit_parsed_filters(get_db(), filters, sorted(HOLDER_IDS))
    assert kept == filters and not adjusted
    assert merge_spec_filters([SpecFilter("Type", "=", "Battery holder")], filters)[1:] == filters
    manual = SpecFilter("Battery Size", "=", "explicit")
    assert merge_spec_filters([manual], filters) == [manual]
    assert all(unlisted_clause(f, True) is None for f in filters)
    clauses, params, metadata, ignored = build_spec_filter_clauses(filters)
    assert len(clauses) == 1 and len(params) == 1
    assert '"aa"' in params[0] and '"aaa"' in params[0]
    assert not metadata and not ignored


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("query", ["14500 AA battery holder", "14500 battery holder", "AA battery holder"])
async def test_aa_matches_model_or_no5_and_excludes_aaa(local_client, query, strict):
    result = await search(local_client, query, strict=strict)
    ids = await all_parts(local_client, query, strict=strict)
    assert {"C7525429", "C49118398", "C5457110"} <= ids.keys()
    assert "C964881" not in ids
    assert {"name": "Battery Size", "op": "=", "value": "AA"} in result["filters_applied"]["spec_filters"]
    assert not result["parsed"]["detected"].get("unsupported_constraints")
    assert not result.get("relaxed")


@pytest.mark.parametrize("subcategory_id", sorted(HOLDER_IDS))
async def test_explicit_subcategory_applies_size_filter(local_client, subcategory_id):
    result = await search(local_client, "14500 AA", subcategory_id=subcategory_id, strict=True)
    assert {"name": "Battery Size", "op": "=", "value": "AA"} in result["filters_applied"]["spec_filters"]
    assert all(p["subcategory"].lower() == get_db().get_subcategory_name(subcategory_id).lower()
               for p in result["results"])


async def test_multiple_sizes_are_union_including_strict_mode(local_client):
    aa = await all_parts(local_client, "AA battery holder", strict=True)
    aaa = await all_parts(local_client, "AAA battery holder", strict=True)
    assert "C964881" in aaa and "C964881" not in aa
    both = await all_parts(local_client, "AA AAA battery holder", strict=True)
    assert both.keys() == aa.keys() | aaa.keys()
    assert (await all_parts(local_client, "10440 battery holder")).keys() == aaa.keys()
    assert (await all_parts(local_client, "No.5 battery holder")).keys() == aa.keys()


@pytest.mark.parametrize("query,fts", [
    ("AA battery holder", '"aa" OR "no 5"'),
    ("AAA battery holder", '"aaa" OR "no 7"'),
    ("C battery holder", '"c" OR "no 2"'),
    ("D battery holder", '"d" OR "no 1"'),
    ("coin cell holder", '"coin" OR "button" OR "cr"*'),
])
async def test_size_search_matches_catalog_fts_exactly(local_client, query, fts):
    # Compare complete sets, so a future stocked D holder is supported too.
    with sqlite3.connect(f"file:{Path('data/components.db').resolve()}?mode=ro", uri=True) as conn:
        expected = {row[0] for row in conn.execute(
            "SELECT lcsc FROM components WHERE (subcategory_id IN (1651, 3742, 2989, 3739) OR (subcategory_id = 1303 "
            "AND lcsc IN (SELECT lcsc FROM components_fts WHERE components_fts MATCH '\"holder\"*'))) "
            "AND lcsc IN (SELECT lcsc FROM components_fts WHERE components_fts MATCH ?)", (fts,),
        )}
    result = await all_parts(local_client, query)
    assert result.keys() == expected
    if not expected:
        response = await search(local_client, query)
        assert not response["results"] and not response.get("relaxed")


async def test_holder_scope_retains_existing_18650_holders(local_client):
    holders = await all_parts(local_client, "battery holder")
    assert holders and {p["subcategory"].lower() for p in holders.values()} == {*HOLDER_NAMES, "battery accessories"}
    cells = await all_parts(local_client, "18650 battery holder")
    assert {"C5290175", "C2988620"} <= cells.keys() <= holders.keys()
    control = get_db().search(query="18650 battery holder", min_stock=0, library_type="all", limit=100_000)
    assert {p["lcsc"] for p in control["results"]} <= cells.keys()


@pytest.mark.parametrize("strict", [False, True])
def test_hyphenated_letter_survives_without_becoming_a_size(strict):
    parsed = parse_smart_query("BH-D", subcategory_hint="Battery connector", strict=strict)
    assert parsed.remaining_text == "BH-D"
    assert not parsed.spec_filters


def test_orphaned_letters_and_right_joined_letters_still_removed():
    assert parse_smart_query("- -F battery holder").remaining_text == ""
    assert parse_smart_query("D-unknown battery holder").remaining_text == "unknown"
    assert parse_smart_query("D-sub").subcategory == "d-sub / vga connectors"


@pytest.mark.parametrize("subcategory_id", [None, 1651])
async def test_bh_d_no_longer_searches_bh_alone(local_client, subcategory_id):
    kwargs = {"subcategory_id": subcategory_id} if subcategory_id else {}
    actual = await all_parts(local_client, "BH-D", **kwargs)
    broad = get_db().search(query="BH", min_stock=0, library_type="all", limit=100_000, **kwargs)
    assert actual.keys() < {p["lcsc"] for p in broad["results"]}
    # One phrase, "bh" then a word starting with d: BHC LEDs with some other d-word don't match
    assert not [p["model"] for p in actual.values() if "BHC" in p["model"]]


@pytest.mark.parametrize("query", ["USB-C", "Type-C"])
def test_usb_type_c_parsing_is_unchanged(query):
    parsed = parse_smart_query(query)
    assert parsed.subcategory == "usb connectors"
    assert not parsed.remaining_text
    assert [f.to_dict() for f in parsed.spec_filters] == [{"name": "Connector Type", "op": "=", "value": "Type-C"}]


async def test_reported_adjustable_search_stays_in_holder_scope(local_client):
    query = "adjustable battery holder 18650 26650 32650 multi size"
    result = await search(local_client, query, match_all_terms=False)
    assert result["results"]
    assert all(p["subcategory"].lower() in {*HOLDER_NAMES, "battery accessories"} for p in result["results"])
    assert not any(f["name"] == "Output Type" for f in result["filters_applied"]["spec_filters"])
    assert any(f["filter"] == "Output Type = Adjustable" and f["now"] is None
               for f in result["parsed"]["adjusted_filters"])
