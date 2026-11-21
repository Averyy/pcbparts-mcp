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
