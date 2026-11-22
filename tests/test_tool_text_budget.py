"""Tool text is sent every turn: keep detail in llms.txt, not tools/list."""

from contextlib import asynccontextmanager

from fastmcp import Client

from pcbparts_mcp.server import mcp


# Client-visible description + argument text, with a little room for wording fixes.
TEXT_CAPS = {
    "jlc_stock_check": 800,
    "jlc_search": 1800,
    "jlc_search_help": 350,
    "jlc_stock_history": 425,
    "jlc_get_part": 600,
    "jlc_get_parts": 375,
    "jlc_find_alternatives": 800,
    "jlc_get_pinout": 375,
    "mouser_get_part": 475,
    "digikey_get_part": 375,
    "part_lifecycle": 425,
    "cse_search": 350,
    "cse_get_kicad": 500,
    "sensor_recommend": 675,
    "get_design_rules": 275,
    "board_search": 600,
    "board_get": 425,
}
TOTAL_TEXT_CAP = 9300


def _argument_text_chars(schema):
    if isinstance(schema, dict):
        return len(schema.get("description", "")) + sum(
            _argument_text_chars(value) for key, value in schema.items() if key != "description")
    if isinstance(schema, list):
        return sum(_argument_text_chars(value) for value in schema)
    return 0


async def test_client_visible_text_budget(monkeypatch):
    # Exercise serialization without startup databases, credentials or upstream requests.
    @asynccontextmanager
    async def schema_only(app):
        yield {}

    monkeypatch.setattr(mcp, "_lifespan", schema_only)
    async with Client(mcp) as client:
        tools = await client.list_tools()

    counts = {
        tool.name: len(tool.description or "") + _argument_text_chars(tool.inputSchema)
        for tool in tools
    }
    assert counts.keys() == TEXT_CAPS.keys(), "Set an explicit text budget for each tool"
    assert {name: (count, TEXT_CAPS[name]) for name, count in counts.items()
            if count > TEXT_CAPS[name]} == {}, "Tool text exceeds its character budget"
    assert sum(counts.values()) <= TOTAL_TEXT_CAP
