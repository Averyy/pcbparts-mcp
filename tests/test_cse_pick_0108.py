"""SamacSys selection uses the number and maker, never description-only matches."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from contextlib import asynccontextmanager
import json

import pytest
from fastmcp import Client

from pcbparts_mcp import cse, server


# Recorded ABS10 search, in SamacSys order; no provider is contacted.
ABS10 = [
    ("AX5DAF1-914.0000C", "ABRACON", "CRYSTAL, 32.768KHZ ... Product Range:ABS10 Series ...", 17358038),
    ("ABS10", "ABRACON", "32.768kHz Capacitance 12.5pF", 17352113),
    ("ABS10M-13", "Diodes Incorporated", "Bridge Rectifier Single Phase Standard 1 kV Surface Mount 4-SOPA", 16568507),
    ("ABS10_HF", "Diodes Incorporated", "Bridge Rectifiers Low Power Bridge ABS/SOPA-4 T&R 5K", 16568506),
    ("ABS10-HF", "Comchip Technology", "Bridge Rectifiers VR=1000V IAV=0.8A", 332673),
    ("ABS10 RGG", "Taiwan Semiconductor", "Bridge Rectifier, 1A 1000V, 4-Pin ABS", 689710),
    ("ABS10-32.768KHZ-9-T", "ABRACON", "Crystal, 32.768 kHz, SMD ... ABS10 Series", 332669),
    ("ABLS10000MHZK4T", "ABRACON", "CRYSTAL ... Product Range:ABS10 Series", 17348406),
]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(cse, "CSE_USER", "test")
    monkeypatch.setattr(cse, "CSE_PASS", "test")
    client = cse.CSEClient()
    rows = [dict(mfr_part_number=mpn, manufacturer=maker, description=description,
                 has_model=True, cse_part_id=part_id) for mpn, maker, description, part_id in ABS10]
    monkeypatch.setattr(client, "search", AsyncMock(return_value={"results": rows, "total": len(rows)}))

    async def download(part_id, info):
        return {"part_id": part_id, **info, "kicad_symbol": "symbol", "kicad_footprint": "footprint"}

    monkeypatch.setattr(client, "_download_kicad", AsyncMock(side_effect=download))
    return client


async def test_abs10_exact_before_description(client):
    reply = await client.get_kicad(query="ABS10")
    assert reply["part_id"] == 17352113
    assert {row["cse_part_id"] for row in reply["other_matches"]} == {16568507, 16568506, 332673, 689710}
    assert "part_id" in reply["note"] and "manufacturer" in reply["note"]


async def test_abs10_maker(client):
    reply = await client.get_kicad(query="ABS10", manufacturer="Diodes Incorporated")
    assert reply["part_id"] == 16568507
    assert "other_matches" not in reply


async def test_lcsc_maker_without_a_model(client, monkeypatch):
    monkeypatch.setattr(server, "get_db", lambda: SimpleNamespace(
        get_by_lcsc=lambda code: {"model": "ABS10", "manufacturer": "MDD"}))
    monkeypatch.setattr(server, "_cse_client", client)
    args = await server._cse_lcsc({"lcsc": "C65028"})
    reply = await server.cse_get_kicad(**args)
    assert "ABS10" in reply["error"] and "MDD" in reply["error"]
    assert len(reply["candidates"]) == 5
    assert reply["candidates"][0]["cse_part_id"] == 17352113
    assert "part_id" in reply["error"]
    client._download_kicad.assert_not_awaited()


async def test_unrelated_query(client):
    reply = await client.get_kicad(query="ZZQ9981XK")
    assert "ZZQ9981XK" in reply["error"]
    assert [row["cse_part_id"] for row in reply["candidates"]] == [row[3] for row in ABS10[:5]]
    client._download_kicad.assert_not_awaited()


@pytest.mark.parametrize("query,numbers,chosen", [
    ("abs-10", ["ABS10_HF", "ABS10", "ABS10M-13"], 2),
    ("ESP32-WROOM-32E", ["ESP32-WROOM", "ESP32-WROOM-32E-N4", "ESP32-WROOM-32E-N8"], 2),
    ("LM358PWR", ["LM358PW", "LM358"], 1),
], ids=["separators", "extension", "packing"])
async def test_match_tiers_keep_provider_order(client, query, numbers, chosen):
    client.search.return_value = {"results": [
        {"mfr_part_number": number, "manufacturer": "Maker", "has_model": True, "cse_part_id": i}
        for i, number in enumerate(numbers, 1)]}
    assert (await client.get_kicad(query=query))["part_id"] == chosen


async def test_part_id_skips_query_and_maker(client):
    reply = await client.get_kicad(query="ZZQ9981XK", manufacturer="MDD", part_id=17358038)
    assert reply["part_id"] == 17358038
    client.search.assert_not_awaited()


async def test_model_and_id_required(client):
    client.search.return_value["results"][1]["has_model"] = False
    client.search.return_value["results"][2]["cse_part_id"] = None
    assert (await client.get_kicad(query="ABS10"))["part_id"] == 16568506


@pytest.mark.parametrize("maker", [None, "MDD"], ids=["any", "maker"])
@pytest.mark.parametrize("empty", [True, False], ids=["empty", "no_models"])
async def test_no_models(client, maker, empty):
    rows = client.search.return_value["results"]
    for row in rows:
        row["has_model"] = False
    if empty:
        rows.clear()
    reply = await client.get_kicad(query="ABS10", manufacturer=maker)
    # Nothing to choose from: the error alone, as before
    assert reply == {"error": "No parts found for 'ABS10'" if empty else "No ECAD model available for 'ABS10'"}
    client._download_kicad.assert_not_awaited()


@pytest.mark.parametrize("query,number", [
    ("ABS1", "ABS10"),            # a digit running on is another number
    ("ABS10", "ABS1"),
    ("TPS7A2033", "TPS7A20"),
    ("MCP73831T-2ACI/OT", "MCP73831"),  # more than a packing suffix
], ids=["longer", "shorter", "digits", "variant"])
async def test_not_the_same_number(client, query, number):
    client.search.return_value = {"results": [
        {"mfr_part_number": number, "manufacturer": "Maker", "has_model": True, "cse_part_id": 5}]}
    reply = await client.get_kicad(query=query)
    assert "error" in reply and reply["candidates"][0]["cse_part_id"] == 5
    client._download_kicad.assert_not_awaited()


@pytest.mark.parametrize("query,number", [
    ("ABS10", "ABS10-32.768KHZ-9-T"),  # a separator ends the number
    ("SS14", "SS14-E3/61T"),
    ("LM358PWR", "LM358PW"),
], ids=["separator", "suffix", "packing"])
async def test_same_number(client, query, number):
    client.search.return_value = {"results": [
        {"mfr_part_number": number, "manufacturer": "Maker", "has_model": True, "cse_part_id": 5}]}
    assert (await client.get_kicad(query=query))["part_id"] == 5


async def test_cached_files_and_search_rows_stay_independent(client):
    client._kicad_cache.set("kicad:17352113", {"kicad_symbol": "cached"})
    reply = await client.get_kicad(query="ABS10")
    assert reply["kicad_symbol"] == "cached" and reply["other_matches"]
    assert all("other_matches" not in row and "note" not in row for row in client.search.return_value["results"])
    assert "other_matches" not in await client.get_kicad(query="ABS10", manufacturer="Abracon LLC")
    client._download_kicad.assert_not_awaited()


async def test_lcsc_explicit_maker_wins(client, monkeypatch):
    monkeypatch.setattr(server, "get_db", lambda: SimpleNamespace(
        get_by_lcsc=lambda code: {"model": "ABS10", "manufacturer": "MDD"}))
    monkeypatch.setattr(server, "_cse_client", client)
    args = await server._cse_lcsc({"lcsc": "C65028", "manufacturer": "Diodes Inc."})
    assert args["manufacturer"] == "Diodes Inc."
    assert (await server.cse_get_kicad(**args))["part_id"] == 16568507


async def test_candidate_fields_and_cap(client):
    reply = await client.get_kicad(query="ABS10", manufacturer="MDD")
    assert len(reply["candidates"]) == 5
    assert all(set(row) == {"mfr_part_number", "manufacturer", "description", "cse_part_id"}
               for row in reply["candidates"])
    assert 17358038 not in {row["cse_part_id"] for row in reply["candidates"]}


async def test_quota_and_stored_files_for_matching_query(client):
    client._clock = lambda: 0
    client._refused_since, client._quota_until = 1, 10
    reply = await client.get_kicad(query="ABS10")
    assert "daily model download limit" in reply["error"]
    client._kicad_cache.set("kicad:17352113", {"kicad_symbol": "stored"})
    assert (await client.get_kicad(query="ABS10"))["kicad_symbol"] == "stored"
    client._download_kicad.assert_not_awaited()


async def test_mcp_maker_argument_and_error_envelope(client, monkeypatch):
    @asynccontextmanager
    async def lifespan(app):
        yield {}

    monkeypatch.setattr(server.mcp, "_lifespan", lifespan)
    monkeypatch.setattr(server, "_cse_client", client)
    monkeypatch.setattr(server, "get_db", lambda: SimpleNamespace(
        get_by_lcsc=lambda code: {"model": "ABS10", "manufacturer": "MDD"}))
    async with Client(server.mcp) as mcp:
        tool = next(tool for tool in await mcp.list_tools() if tool.name == "cse_get_kicad")
        assert "manufacturer" in tool.inputSchema["properties"]
        reply = await mcp.call_tool("cse_get_kicad", {"lcsc": "C65028"})
        assert reply.is_error is False
        assert "MDD" in json.loads(reply.content[0].text)["error"]
        chosen = await mcp.call_tool("cse_get_kicad", {"lcsc": "C65028", "manufacturer": "Diodes Incorporated"})
        assert json.loads(chosen.content[0].text)["part_id"] == 16568507
