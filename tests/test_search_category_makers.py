"""jlc_search takes category_id/category_name and manufacturers like jlc_stock_check (0.10.6).
Catalog-backed: assertions hold for whatever is in stock, and skip when nothing matches."""

import pytest
from fastmcp import Client

from pcbparts_mcp import server
from pcbparts_mcp.search.query_builder import build_manufacturers_clause


def test_several_makers_are_ored_case_insensitively():
    assert build_manufacturers_clause(["Texas Instruments", "onsemi", "onsemi"]) == (
        "AND LOWER(manufacturer) IN (LOWER(?), LOWER(?))", ["Texas Instruments", "onsemi"])
    assert build_manufacturers_clause(["YAGEO"]) == ("AND LOWER(manufacturer) = LOWER(?)", ["YAGEO"])
    assert build_manufacturers_clause([]) == ("", [])


async def _search(**arguments):
    async with Client(server.mcp) as client:
        result = await client.call_tool("jlc_search", arguments, raise_on_error=False)
    assert not result.is_error, result.content[0].text
    return result.structured_content


async def test_manufacturers_keeps_only_those_makers_and_resolves_aliases():
    reply = await _search(query="LM358", manufacturers=["TI", "onsemi"], limit=50)
    makers = {row["manufacturer"] for row in reply["results"]}
    if not makers:
        pytest.skip("no LM358 from those makers in stock today")
    assert makers <= {"Texas Instruments", "onsemi"}
    assert reply["filters_applied"]["manufacturers"] == ["TI", "onsemi"]
    single = await _search(query="LM358", manufacturer="TI", limit=50)
    assert {row["manufacturer"] for row in single["results"]} <= {"Texas Instruments"}


async def test_manufacturers_replaces_manufacturer_as_packages_replaces_package():
    """As in jlc_stock_check, and as jlc_search's packages always replaced package."""
    reply = await _search(query="LM358", manufacturer="TI", manufacturers='["onsemi"]', limit=50)
    assert {row["manufacturer"] for row in reply["results"]} <= {"onsemi"}


async def test_a_bad_manufacturers_value_is_refused():
    async with Client(server.mcp) as client:
        result = await client.call_tool("jlc_search", {"query": "LM358", "manufacturers": [""]}, raise_on_error=False)
    assert "Invalid manufacturers" in (result.structured_content or {}).get("error", "")


async def test_category_keeps_results_in_it():
    reply = await _search(query="100nF", category_name="Capacitors", limit=30)
    if not reply["results"]:
        pytest.skip("no 100nF parts in stock today")
    assert reply["filters_applied"]["category_resolved"] == "Capacitors"
    assert {row["category"] for row in reply["results"]} == {"Capacitors"}


async def test_query_words_naming_another_categorys_type_dont_empty_a_category_search():
    """'capacitor' picks an MLCC subcategory; with category Resistors that pick is dropped, not ANDed."""
    reply = await _search(query="100nF capacitor", category_name="Resistors", limit=5)
    assert reply["filters_applied"]["category_resolved"] == "Resistors"
    assert not reply["filters_applied"].get("subcategory_resolved")
    kept = await _search(query="100nF capacitor", category_name="Capacitors", limit=5)
    assert kept["filters_applied"]["subcategory_resolved"]  # inside the category: kept


async def test_an_unknown_category_is_a_category_not_found_error():
    async with Client(server.mcp) as client:
        result = await client.call_tool("jlc_search", {"query": "x", "category_name": "Nonsense Parts"},
                                        raise_on_error=False)
    assert "Category not found" in (result.structured_content or {}).get("error", "")


async def test_the_tool_list_shows_the_same_names_as_jlc_stock_check():
    tools = {tool.name: tool for tool in await server.mcp.list_tools()}
    search = set(tools["jlc_search"].parameters["properties"])
    stock = set(tools["jlc_stock_check"].parameters["properties"])
    assert {"category_id", "category_name", "manufacturers"} <= search & stock


def test_an_exact_category_name_wins_over_another_categorys_singular():
    """The catalog has both "other" and "Others": "Other" is the first, not "Others" made singular."""
    from pcbparts_mcp.client import JLCPCBClient
    for order in ([("Others", 2), ("other", 1)], [("other", 1), ("Others", 2)]):
        client = JLCPCBClient()
        client.set_categories([{"id": i, "name": n, "subcategories": []} for n, i in order])
        assert client.match_category_by_name("Other") == 1 and client.match_category_by_name("others") == 2


async def test_every_tool_reads_a_category_name_alike():
    """jlc_search and jlc_search_help read a name as jlc_stock_check always has: "LED" is
    Optoelectronics, not "LED Drivers"."""
    db = server.get_db()
    optoelectronics = db.resolve_category_name("Optoelectronics")
    async with Client(server.mcp):
        assert server._client.match_category_by_name("LED") == optoelectronics
    reply = await _search(query="red", category_name="LED", limit=1)
    assert reply["filters_applied"]["category_resolved"] == "Optoelectronics"
    async with Client(server.mcp) as client:
        help_reply = (await client.call_tool("jlc_search_help", {"category": "LED"})).structured_content
    assert help_reply["category_id"] == optoelectronics


async def test_an_unknown_id_is_an_error_not_every_part_or_none():
    for name, word in (("category_id", "Category"), ("subcategory_id", "Subcategory")):
        async with Client(server.mcp) as client:
            result = await client.call_tool("jlc_search", {"query": "10k", name: 999999999}, raise_on_error=False)
        reply = result.structured_content
        assert reply["error"] == f"{word} ID 999999999 not found" and reply["total"] == 0 and reply["hint"]


async def test_query_words_outside_the_category_are_reported_and_strict_refuses():
    loose = await _search(query="resistor", category_name="Capacitors", limit=1)
    adjusted = loose["parsed"]["adjusted_filters"]
    assert any(a["filter"].startswith("subcategory: ") and "not in category Capacitors, so that part type isn't"
               in a["reason"] for a in adjusted)
    assert loose["parsed"]["subcategory"] is None
    strict = await _search(query="resistor", category_name="Capacitors", strict=True, limit=1)
    assert strict["error"].startswith("Strict search cannot apply every constraint") and strict["total"] == 0



async def _help(**arguments):
    async with Client(server.mcp) as client:
        result = await client.call_tool("jlc_search_help", arguments, raise_on_error=False)
    assert not result.is_error, result.content[0].text
    return result.structured_content


async def test_jlc_search_help_reads_digit_text_as_an_id_and_other_digits_as_names():
    by_number = await _help(subcategory=2954)
    assert (await _help(subcategory="2954"))["subcategory_id"] == by_number["subcategory_id"] == 2954
    assert (await _help(category="²"))["error"].startswith("Category not found")
    assert (await _help(category="9" * 4500))["error"].startswith("Category not found")


async def test_a_subcategory_outside_the_category_is_refused_by_both_tools(monkeypatch):
    reply = await _search(query="x", category_name="Capacitors", subcategory_name="MOSFETs", strict=True)
    assert reply["error"].startswith("Invalid subcategory: 'MOSFETs' is in ") and reply["total"] == 0
    assert "not Capacitors" in reply["error"]

    async def no_live_search(*args, **kwargs):
        raise AssertionError("refused before any JLCPCB request")
    async with Client(server.mcp) as client:
        monkeypatch.setattr(server._client, "search", no_live_search)
        mosfets = server.get_db().resolve_subcategory_name("MOSFETs")
        capacitors = server.get_db().resolve_category_name("Capacitors")
        for arguments, start in (({"subcategory_id": mosfets, "category_id": capacitors}, "Invalid subcategory: "),
                                 ({"category_id": 999999999}, "Category ID 999999999 not found"),
                                 ({"subcategory_id": 999999999}, "Subcategory ID 999999999 not found")):
            result = await client.call_tool("jlc_stock_check", {"query": "LM358", **arguments}, raise_on_error=False)
            assert result.structured_content["error"].startswith(start), result.structured_content


async def test_strict_compares_the_query_package_with_the_list_that_replaces_package():
    reply = await _search(query="resistor 0603", package="0402", packages=["0603"], strict=True, limit=1)
    assert not reply.get("error"), reply.get("error")


async def test_a_maker_spelled_with_punctuation_resolves_as_in_jlc_stock_check():
    reply = await _search(query="LM358", manufacturers=["Texas-Instruments"], limit=20)
    if not reply["results"]:
        pytest.skip("no TI LM358 in stock today")
    assert {row["manufacturer"] for row in reply["results"]} == {"Texas Instruments"}


def test_an_empty_search_suggestion_keeps_the_makers():
    from pcbparts_mcp.search.diagnostics import next_search
    call = next_search("LM358", {"manufacturers": ["onsemi"], "min_stock": 10})
    assert call["arguments"]["manufacturers"] == ["onsemi"]


async def test_jlc_stock_check_filters_by_a_subcategory_with_nothing_in_stock(monkeypatch):
    """jlc_search sends callers to jlc_stock_check for these; its ID used to be dropped (every
    category searched), and round 2's ID check refused it."""
    sent = []

    async def live_search(**kwargs):
        sent.append(server._client._build_search_params(**{k: v for k, v in kwargs.items() if k in (
            "query", "category_id", "subcategory_id")}))
        return {"results": [], "total": 0}
    async with Client(server.mcp) as client:
        listed = {sub["id"] for cat in server._categories for sub in cat.get("subcategories", [])}
        categories, subcategories = server.get_db().catalog_ids()
        empty = next((i for i, sub in subcategories.items() if i not in listed and sub.get("category_id") in categories), None)
        if empty is None:
            pytest.skip("every subcategory has parts in today's snapshot")
        monkeypatch.setattr(server._client, "search", live_search)
        result = await client.call_tool("jlc_stock_check", {"query": "cable", "subcategory_id": empty}, raise_on_error=False)
    assert not (result.structured_content or {}).get("error"), result.structured_content
    assert sent and sent[0]["secondSortId"] == empty and sent[0]["firstSortId"] == subcategories[empty]["category_id"]


async def test_jlc_search_help_unknown_ids_read_as_in_the_search_tools():
    from pcbparts_mcp.subcategory_aliases import CATEGORY_ID_NOT_FOUND_HINT, SUBCATEGORY_ID_NOT_FOUND_HINT
    assert await _help(category=999999999) == {"error": "Category ID 999999999 not found", "hint": CATEGORY_ID_NOT_FOUND_HINT}
    assert await _help(category="999999999") == {"error": "Category ID 999999999 not found", "hint": CATEGORY_ID_NOT_FOUND_HINT}
    for value in (0, 999999999):
        assert await _help(subcategory=value) == {"error": f"Subcategory ID {value} not found", "hint": SUBCATEGORY_ID_NOT_FOUND_HINT}
    assert "similar_" not in CATEGORY_ID_NOT_FOUND_HINT + SUBCATEGORY_ID_NOT_FOUND_HINT  # no such field in these replies


async def test_jlc_search_help_lists_a_category_with_nothing_in_stock():
    categories, _ = server.get_db().catalog_ids()
    async with Client(server.mcp):
        listed = {cat["id"] for cat in server._categories}
    empty = next((i for i in categories if i not in listed), None)
    if empty is None:
        pytest.skip("every category has parts in today's snapshot")
    reply = await _help(category=empty)
    assert reply["category_id"] == empty and reply["category_name"] == categories[empty]["name"]
    assert all(sub["count"] == 0 for sub in reply["subcategories"])


async def test_every_catalog_name_resolves_alike_in_all_three_tools():
    """Names of part types with nothing in stock too: jlc_stock_check refused 277 of them (suggesting
    them back), and resolved "Stepper motor" to Stepper Motor Driver while jlc_search took the
    subcategory of that name."""
    async with Client(server.mcp):
        db, live = server.get_db(), server._client
        categories, subcategories = db.catalog_ids()
        for sub in subcategories.values():
            name = sub["name"]
            assert live.get_subcategory_id_by_name(name) == db.resolve_subcategory_name(name), name
            short = " ".join(name.split()[:2])
            assert live.get_subcategory_id_by_name(short) == db.resolve_subcategory_name(short), short
        assert all(live.match_category_by_name(cat["name"]) == cat_id for cat_id, cat in categories.items())


def test_suggestions_take_part_of_a_word_and_close_spellings():
    db = server.get_db()
    assert "DC-DC Converters" in [s["name"] for s in db._find_similar_subcategories("buck conv")]
    assert "MOSFETs" in [s["name"] for s in db._find_similar_subcategories("mosfett")]
    assert any("Resistor" in s["name"] for s in db._find_similar_subcategories("Resistorz"))


async def test_a_part_type_outside_the_category_doesnt_turn_unmatched_words_into_the_whole_category():
    """"gizmo widget" in Resistors finds nothing; naming a MOSFET as well used to return every resistor."""
    plain = await _search(query="gizmo widget", category_name="Resistors", limit=1)
    with_type = await _search(query="gizmo widget mosfet", category_name="Resistors", limit=1)
    assert plain["total"] == 0 and with_type["total"] == 0 and not with_type.get("relaxed")


async def test_sample_size_is_the_number_of_parts_read():
    """A subcategory with numeric attributes too: a list of values once landed in sample_size."""
    mosfets = await _help(subcategory="MOSFETs")
    assert isinstance(mosfets["sample_size"], int) and 0 < mosfets["sample_size"] <= 1000
    assert any(attr.get("type") == "numeric" for attr in mosfets["attributes"])


async def test_jlc_search_help_reads_numbers_as_the_search_tools_do():
    from pcbparts_mcp.subcategory_aliases import CATEGORY_ID_NOT_FOUND_HINT
    assert (await _help(subcategory="2954.0"))["subcategory_id"] == 2954
    assert await _help(category="-1") == {"error": "Category ID -1 not found", "hint": CATEGORY_ID_NOT_FOUND_HINT}


async def test_a_new_listing_keeps_the_whole_catalogs_names():
    async with Client(server.mcp):
        live, db = server._client, server.get_db()
        stepper = db.resolve_subcategory_name("Stepper motor")
        live.set_categories(server._categories)
        assert live.get_subcategory_id_by_name("Stepper motor") == stepper
