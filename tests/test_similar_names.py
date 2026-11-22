"""Unknown subcategory and category names get the same hint and ranked suggestions from
jlc_search, jlc_stock_check and jlc_search_help (0.10.6)."""

import pytest
from fastmcp import Client

from pcbparts_mcp import server
from pcbparts_mcp.subcategory_aliases import (
    CATEGORY_NOT_FOUND_HINT, SUBCATEGORY_NOT_FOUND_HINT, find_similar_categories, find_similar_subcategories,
)

SUBS = {"chip test socket": 1, "chip resistor - surface mount": 2, "through hole resistors": 3,
        "precision op amps": 4, "tactile switches": 5}
INFO = {i: {"name": n.title(), "category_name": "X"} for n, i in SUBS.items()}


def test_most_shared_words_first_plural_or_not():
    names = [s["name"] for s in find_similar_subcategories("Chip Resistors", SUBS, INFO)]
    assert names[0] == "Chip Resistor - Surface Mount"
    assert names.index("Through Hole Resistors") < names.index("Chip Test Socket")


def test_word_order_doesnt_matter_and_a_misspelling_is_still_close():
    assert find_similar_subcategories("Op Amps Precision", SUBS, INFO)[0]["name"] == "Precision Op Amps"
    cats = {"resistors": 10, "capacitors": 11}
    assert find_similar_categories("Resistorz", cats, {10: {"name": "Resistors"}, 11: {"name": "Capacitors"}}) == [
        {"id": 10, "name": "Resistors"}]


def test_nothing_close_suggests_nothing():
    assert find_similar_subcategories("zzqx", SUBS, INFO) == []


async def _reply(tool, arguments):
    async with Client(server.mcp) as client:
        return (await client.call_tool(tool, arguments, raise_on_error=False)).structured_content or {}


@pytest.mark.parametrize(("tool", "arguments"), [
    ("jlc_search", {"query": "10k", "subcategory_name": "Chip Resistors"}),
    ("jlc_stock_check", {"query": "10k", "subcategory_name": "Chip Resistors"}),
    ("jlc_search_help", {"subcategory": "Chip Resistors"}),
])
async def test_every_tool_answers_an_unknown_subcategory_alike(tool, arguments):
    reply = await _reply(tool, arguments)
    assert reply["error"] == "Subcategory not found: 'Chip Resistors'"
    assert reply["hint"] == SUBCATEGORY_NOT_FOUND_HINT
    assert reply["similar_subcategories"][0]["name"] == "Chip Resistor - Surface Mount"


@pytest.mark.parametrize(("tool", "arguments"), [
    ("jlc_search", {"query": "10k", "category_name": "Resistorz"}),
    ("jlc_stock_check", {"query": "10k", "category_name": "Resistorz"}),
    ("jlc_search_help", {"category": "Resistorz"}),
])
async def test_every_tool_answers_an_unknown_category_alike(tool, arguments):
    reply = await _reply(tool, arguments)
    assert reply["error"] == "Category not found: 'Resistorz'"
    assert reply["hint"] == CATEGORY_NOT_FOUND_HINT
    assert reply["similar_categories"][0]["name"] == "Resistors"


async def test_jlc_search_help_takes_a_partial_category_name_like_the_search_tools():
    assert (await _reply("jlc_search_help", {"category": "Resistor"}))["category_name"] == "Resistors"


def test_a_very_long_name_is_matched_on_its_start():
    """Catalog names are under 70 characters: only the first 120 are compared, which bounds the work."""
    from pcbparts_mcp.subcategory_aliases import _SIMILAR_NAME_CHARS, find_similar_subcategories
    names = {"multilayer ceramic capacitors mlcc - smd/smt": 1, "chip resistor - surface mount": 2}
    info = {1: {"name": "Multilayer Ceramic Capacitors MLCC - SMD/SMT", "category_name": "Capacitors"},
            2: {"name": "Chip Resistor - Surface Mount", "category_name": "Resistors"}}
    start = "ceramic capacitor".ljust(_SIMILAR_NAME_CHARS, " ")
    assert (find_similar_subcategories(start + " resistor" * 2000, names, info)
            == find_similar_subcategories(start, names, info))
