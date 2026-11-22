"""The distributor tools take one argument name, part_number, and still accept the names callers
send for it: digikey_get_part's old product_number (built into clients) and mpn."""

import pytest
from fastmcp import Client

from pcbparts_mcp import server


class FakeDistributor:
    def __init__(self):
        self.asked = []

    async def get_part(self, number, caller=None):
        self.asked.append(number)
        return {"results": [{"mfr_part_number": number}], "total": 1}

    async def close(self):
        pass


@pytest.fixture
async def called(monkeypatch):
    """call(tool, arguments) over MCP against fake distributors -> (result, the numbers the tool asked)."""
    monkeypatch.setattr(server, "MOUSER_API_KEY", "")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "")

    async def call(tool, arguments):
        async with Client(server.mcp) as client:  # the server's startup sets its own clients: swap after it
            fakes = {"mouser_get_part": FakeDistributor(), "digikey_get_part": FakeDistributor()}
            monkeypatch.setattr(server, "_mouser_client", fakes["mouser_get_part"])
            monkeypatch.setattr(server, "_digikey_client", fakes["digikey_get_part"])
            result = await client.call_tool(tool, arguments, raise_on_error=False)
        return result, fakes[tool].asked

    return call


async def test_tool_list_shows_one_name_for_both_tools():
    tools = {tool.name: tool for tool in await server.mcp.list_tools()}
    for name in ("mouser_get_part", "digikey_get_part"):
        schema = tools[name].parameters
        assert list(schema["properties"]) == ["part_number"] and schema["required"] == ["part_number"]


@pytest.mark.parametrize("tool", ["mouser_get_part", "digikey_get_part"])
@pytest.mark.parametrize("argument", ["part_number", "product_number", "mpn"])
async def test_each_name_reaches_the_tool(called, tool, argument):
    result, asked = await called(tool, {argument: "LM358P"})
    assert not result.is_error and result.structured_content["total"] == 1
    assert asked == ["LM358P"]


@pytest.mark.parametrize("tool", ["mouser_get_part", "digikey_get_part"])
@pytest.mark.parametrize("arguments", [
    {"part_number": "LM358P", "product_number": "NE555P"},  # the tool's own name plus an alias
    {"product_number": "LM358P", "mpn": "NE555P"},  # two aliases: which one is meant?
    {"number": "LM358P"},  # not a name we accept
    {},
], ids=["both", "two-aliases", "unknown", "none"])
async def test_anything_else_is_refused_as_before(called, tool, arguments):
    result, asked = await called(tool, arguments)
    assert result.is_error and asked == []


def test_only_the_named_tools_and_dict_arguments_are_touched():
    arguments = {"product_number": "LM358P"}
    assert server._with_argument_aliases("jlc_get_part", arguments) is arguments
    assert server._with_argument_aliases("digikey_get_part", None) is None
    assert server._with_argument_aliases("digikey_get_part", {"part_number": "X"}) == {"part_number": "X"}
    assert server._with_argument_aliases("digikey_get_part", arguments) == {"part_number": "LM358P"}
    assert arguments == {"product_number": "LM358P"}  # the caller's dict isn't changed


async def test_batch_tools_accept_each_others_list_name():
    """jlc_get_parts(lcsc=...) and jlc_stock_history(parts=...): both seen in prod's rejected calls."""
    tools = {tool.name: tool for tool in await server.mcp.list_tools()}
    assert "lcsc" not in tools["jlc_get_parts"].parameters["properties"]
    assert "parts" not in tools["jlc_stock_history"].parameters["properties"]
    async with Client(server.mcp) as client:
        by_alias = await client.call_tool("jlc_get_parts", {"lcsc": ["C999999999999"]}, raise_on_error=False)
        by_name = await client.call_tool("jlc_get_parts", {"parts": ["C999999999999"]}, raise_on_error=False)
        assert not by_alias.is_error and by_alias.structured_content == by_name.structured_content
        assert by_alias.structured_content["counts"]["not_found"] == 1
        history_alias = await client.call_tool("jlc_stock_history", {"parts": "C999999999999"}, raise_on_error=False)
        history_name = await client.call_tool("jlc_stock_history", {"lcsc": "C999999999999"}, raise_on_error=False)
        assert history_alias.is_error == history_name.is_error
        assert history_alias.structured_content == history_name.structured_content
        both = await client.call_tool("jlc_stock_history", {"parts": "C1", "lcsc": "C2"}, raise_on_error=False)
        assert both.is_error


async def test_jlc_get_parts_takes_the_list_names_prod_saw_on_2026_11_21():
    """lcsc_codes (4 calls, three as a JSON string) and identifiers (1, a JSON string), refused before 0.10.5."""
    tools = {tool.name: tool for tool in await server.mcp.list_tools()}
    assert set(tools["jlc_get_parts"].parameters["properties"]) == {"parts"}
    async with Client(server.mcp) as client:
        by_name = await client.call_tool("jlc_get_parts", {"parts": ["C999999999999"]}, raise_on_error=False)
        for alias, value in (("lcsc_codes", ["C999999999999"]), ("lcsc_codes", '["C999999999999"]'),
                             ("identifiers", '["C999999999999"]')):
            reply = await client.call_tool("jlc_get_parts", {alias: value}, raise_on_error=False)
            assert not reply.is_error and reply.structured_content == by_name.structured_content, alias
        two = await client.call_tool("jlc_get_parts", {"lcsc_codes": ["C1"], "identifiers": ["C2"]},
                                     raise_on_error=False)
        assert two.is_error  # two aliases at once: left for validation to refuse


# --- 0.10.6: the names the other tools use, and errors that name a tool's own arguments ---

from pcbparts_mcp import stats  # noqa: E402

rename = server._with_argument_aliases


@pytest.mark.parametrize(("given", "expected"), [
    ({"identifier": "C963235"}, {"lcsc": "C963235"}),
    ({"identifier": " c963235 "}, {"lcsc": "C963235"}),
    ({"part_number": "AMS1117-3.3"}, {"mpn": "AMS1117-3.3"}),
    ({"identifier": "C2040", "live": True}, {"lcsc": "C2040", "live": True}),
])
def test_jlc_get_part_takes_identifier_and_part_number(given, expected):
    assert rename("jlc_get_part", given) == expected


@pytest.mark.parametrize("given", [{"lcsc": "C1", "identifier": "C2"}, {"mpn": "X", "part_number": "Y"},
                                   {"identifier": ""}, {"identifier": 5}])
def test_jlc_get_part_leaves_a_clash_or_an_odd_value_to_validation(given):
    assert rename("jlc_get_part", given) == given


@pytest.mark.parametrize("tool", ["jlc_search", "jlc_stock_check"])
@pytest.mark.parametrize(("value", "expected"), [("Fuseholders", {"subcategory_name": "Fuseholders"}),
                                                 (2954, {"subcategory_id": 2954}), ("2954", {"subcategory_id": 2954})])
def test_search_tools_take_jlc_search_helps_subcategory(tool, value, expected):
    assert rename(tool, {"subcategory": value}) == expected
    assert rename(tool, {"subcategory": value, "subcategory_id": 1}) == {"subcategory": value, "subcategory_id": 1}


def test_jlc_stock_check_takes_category():
    assert rename("jlc_stock_check", {"category": "Resistors"}) == {"category_name": "Resistors"}
    assert rename("jlc_stock_check", {"category": 1}) == {"category_id": 1}
    assert rename("jlc_search", {"category": "Resistors"}) == {"category_name": "Resistors"}


@pytest.mark.parametrize(("given", "expected"), [
    ({"page": 1}, {"offset": 0}), ({"page": 3}, {"offset": 40}), ({"page": 2, "limit": 5}, {"offset": 5, "limit": 5}),
    ({"page": 0}, {"offset": 0}), ({"page": -1}, {"page": -1}), ({"page": 2, "offset": 7}, {"page": 2, "offset": 7}),
    # numbers sent as text or as whole floats, as the tools' own int arguments take them
    ({"page": "2"}, {"offset": 20}), ({"page": 2, "limit": "5"}, {"offset": 5, "limit": "5"}), ({"page": 2.0}, {"offset": 20}),
    ({"page": "2.0"}, {"offset": 20}), ({"page": "+2", "limit": "+7"}, {"offset": 7, "limit": "+7"}),
    # pages as long as the tool makes them: limit 200 is clamped to 100, so page 2 starts at 100
    ({"page": 2, "limit": 200}, {"offset": 100, "limit": 200}), ({"page": 3, "limit": 0}, {"offset": 2, "limit": 0}),
])
def test_jlc_search_takes_page(given, expected):
    assert rename("jlc_search", given) == expected


@pytest.mark.parametrize(("given", "expected"), [
    ({"offset": 0}, {"page": 1}), ({"offset": 40}, {"page": 3}), ({"offset": 10, "limit": 5}, {"page": 3, "limit": 5}),
    ({"offset": 7}, {"offset": 7}),  # not a page start: refused, with the tool's argument names
    ({"offset": 200, "limit": 200}, {"page": 3, "limit": 200}), ({"offset": 150, "limit": 200}, {"offset": 150, "limit": 200}),
    ({"offset": "40"}, {"page": 3}),
])
def test_jlc_stock_check_takes_an_offset_that_starts_a_page(given, expected):
    assert rename("jlc_stock_check", given) == expected


@pytest.mark.parametrize("tool", ["cse_search", "cse_get_kicad"])
@pytest.mark.parametrize("name", ["mpn", "part_number"])
def test_cse_tools_take_the_part_number_names(tool, name):
    assert rename(tool, {name: "LM358P"}) == {"query": "LM358P"}


async def test_cse_get_kicad_takes_an_lcsc_code_by_its_mpn(monkeypatch):
    class Db:
        def get_by_lcsc(self, code):
            return {"model": "LM358DR2G"} if code == "C7950" else None

    async def run(pool, fn, *args):
        return fn(*args)
    monkeypatch.setattr(server, "get_db", lambda: Db())
    monkeypatch.setattr(server, "run_db", run)
    assert await server._cse_lcsc({"lcsc": "c7950"}) == {"query": "LM358DR2G"}
    assert await server._cse_lcsc({"lcsc": "C99999999"}) == {"lcsc": "C99999999"}  # unknown: refused as before
    assert await server._cse_lcsc({"lcsc": "C7950", "query": "X"}) == {"lcsc": "C7950", "query": "X"}


def test_each_search_tool_takes_the_others_sort_word():
    assert server._sort_word("stock", "quantity")(" Quantity ") == "stock"
    assert server._sort_word("quantity", "stock")("STOCK") == "quantity"
    assert server._sort_word("stock", "quantity")("price") == "price"


async def _error(tool, arguments):
    async with Client(server.mcp) as client:
        result = await client.call_tool(tool, arguments, raise_on_error=False)
    assert result.is_error
    return result.content[0].text


async def test_an_unknown_argument_names_the_tools_arguments_and_the_likely_one():
    text = await _error("jlc_search", {"query": "LM358", "limt": 3})
    assert text.startswith("jlc_search has no argument 'limt'. Its arguments: category_id, category_name, facets,")
    assert "Did you mean 'limit' instead of 'limt'?" in text and "pydantic.dev" not in text


async def test_common_mix_ups_get_advice():
    assert "jlc_search only lists parts in stock" in await _error("jlc_search", {"query": "x", "in_stock": True})
    assert "use jlc_get_parts(parts=[...])" in await _error("jlc_stock_check", {"lcsc_codes": ["C1", "C2"]})


async def test_other_problems_are_listed_briefly_and_names_are_never_echoed_raw():
    text = await _error("jlc_get_part", {"lcsc": "C1", "bad name!": 1, "live": "maybe"})
    assert "has no argument named that (not an identifier)" in text and "bad name!" not in text
    assert "live: Input should be a valid boolean" in text and "maybe" not in text


async def test_the_stats_label_is_unchanged():
    stats.usage.tool_params = {}
    await _error("jlc_search", {"query": "x", "limt": 3})
    day = stats.usage.summary()["days"][0]
    assert day["bad_request_reasons"]["jlc_search"] == {"arg:unknown_argument:unexpected_keyword_argument": 1}


async def test_thousands_of_unknown_names_get_a_short_error():
    """A request can hold thousands of names: five are listed and matched, the rest counted."""
    arguments = {"query": "x", **{f"subcategory_name_{n}": 1 for n in range(2000)}, "limit": "many"}
    text = await _error("jlc_search", arguments)
    assert "'subcategory_name_4' and 1995 more. Its arguments:" in text and "subcategory_name_5" not in text
    assert text.count("Did you mean") <= 5 and len(text) < 2000


def test_identifier_takes_lcsc_codes_of_up_to_12_digits():
    assert rename("jlc_get_part", {"identifier": "C1234567890", "live": True}) == {"lcsc": "C1234567890", "live": True}
    assert rename("jlc_get_part", {"identifier": "C1234567890123"}) == {"mpn": "C1234567890123"}


def test_an_id_is_ascii_digits_and_anything_else_a_name():
    """"²".isdigit() is True but int("²") fails: it's a name, refused as an unknown one."""
    assert rename("jlc_search", {"subcategory": "2954"}) == {"subcategory_id": 2954}
    assert rename("jlc_search", {"subcategory": "²"}) == {"subcategory_name": "²"}
    assert rename("jlc_search", {"subcategory": 2980.0}) == {"subcategory_id": 2980}


def test_jlc_search_help_takes_the_search_tools_names():
    assert rename("jlc_search_help", {"category_name": "LED"}) == {"category": "LED"}
    assert rename("jlc_search_help", {"subcategory_id": 2954}) == {"subcategory": 2954}
    assert rename("jlc_search_help", {"category": "x", "category_name": "y"}) == {"category": "x", "category_name": "y"}


async def test_cse_get_kicad_lcsc_outside_the_snapshot_says_what_to_send():
    text = await _error("cse_get_kicad", {"lcsc": "C999999999999"})
    assert "cse_get_kicad takes lcsc only for a part in the catalog snapshot" in text


def test_unpaired_surrogates_become_replacement_characters():
    assert server._without_surrogates({"query": "a\ud800b", "parts": ["\udfff"], "n": 1}) == {
        "query": "a�b", "parts": ["�"], "n": 1}
    clean = {"query": "LM358", "parts": ["C1"]}
    assert server._without_surrogates(clean) is clean


async def test_a_surrogate_in_any_text_argument_is_an_ordinary_reply_not_a_failed_call():
    async with Client(server.mcp) as client:
        for arguments in ({"query": "\ud800"}, {"query": "10k", "category_name": "\ud800"},
                          {"query": "10k", "manufacturers": ["\ud800"]}):
            result = await client.call_tool("jlc_search", arguments, raise_on_error=False)
            assert not result.is_error, result.content[0].text
