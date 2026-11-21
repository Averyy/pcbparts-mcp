"""0.10.5: tool hints and wording. Tools that can call JLCPCB, EasyEDA, Mouser, DigiKey or SamacSys are
marked open-world and the rest read local data only; the server reports its own version; the
distributor tools clarify their shared limits and retain JLCPCB-first guidance. No network."""

from fastmcp import Client

from pcbparts_mcp import __version__, server

OPEN_WORLD = {"jlc_stock_check", "jlc_get_part", "jlc_find_alternatives", "jlc_get_pinout", "mouser_get_part",
              "digikey_get_part", "part_lifecycle", "cse_search", "cse_get_kicad"}


async def tools():
    return {tool.name: tool for tool in await server.mcp.list_tools(run_middleware=False)}


def flat(text: str | None) -> str:
    """The text as one line: docstrings wrap phrases across lines."""
    return " ".join((text or "").split())


async def test_open_world_hints():
    found = await tools()
    assert {name for name, tool in found.items() if tool.annotations.openWorldHint} == OPEN_WORLD
    assert all(tool.annotations.readOnlyHint and not tool.annotations.destructiveHint for tool in found.values())


async def test_server_reports_its_own_version():
    async with Client(server.mcp) as client:
        assert client.initialize_result.serverInfo.version == __version__


async def test_distributor_wording_is_about_shared_limits():
    found = await tools()
    texts = [flat(server.mcp.instructions), *(flat(tool.description) for tool in found.values())]
    assert not any("only when JLCPCB can't answer" in text for text in texts)
    assert "share small daily limits across all users" in flat(server.mcp.instructions)
    for name in ("mouser_get_part", "digikey_get_part"):
        assert "Lookups share a small daily limit across all users" in flat(found[name].description)
        assert "for parts JLCPCB doesn't carry" in flat(found[name].description)
    assert "looked up at Mouser and DigiKey" in flat(found["part_lifecycle"].description)


async def test_samacsys_descriptions_leave_out_internals():
    found = await tools()
    for name in ("cse_search", "cse_get_kicad"):
        assert "CSE_REQUEST_TIMEOUT" not in found[name].description and "retried" not in found[name].description
    assert "CSEARCH_USER" not in found["cse_get_kicad"].description
    assert "the server's own SamacSys account" in flat(found["cse_get_kicad"].description)
