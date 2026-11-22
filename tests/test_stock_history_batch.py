"""BOM history replies share notes while retaining full-window counts and event labels."""

import gzip
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastmcp import Client
from jsonschema import validate

from pcbparts_mcp import server, stats
from pcbparts_mcp.history_db import StockHistoryDatabase, WHAT_IS_RECORDED

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_history_db import build_history_db


@pytest.fixture
def history_db(tmp_path, monkeypatch):
    events = [
        {"l": "C1", "d": f"2026-03-{day:02d}", "s": day * 10,
         "e": "change"} for day in range(3, 13)
    ] + [
        {"l": "C1", "d": "2026-03-01", "s": 0, "e": "gone"},
        {"l": "C1", "d": "2026-03-02", "s": 5, "e": "new"},
        {"l": "C1", "d": "2026-03-12", "s": 1500, "e": "type_change"},
        {"l": "C2", "d": "2026-03-01", "s": 800, "e": "new", "before": 1000},
        {"l": "C2", "d": "2026-03-02", "s": 0, "e": "gone", "before": 800},
        {"l": "C2", "d": "2026-03-03", "s": 250, "e": "new"},
        {"l": "C2", "d": "2026-03-05", "s": 0, "e": "gone", "before": 250},
        {"l": "C2", "d": "2026-03-20", "s": 1500, "e": "type_change"},
        {"l": "C3", "d": "2026-03-20", "s": 0, "e": "gone", "before": 88},
        {"l": "C4", "d": "2026-03-16", "s": 0, "e": "gone", "before": 320},
        {"l": "C4", "d": "2026-03-17", "s": 300, "e": "new"},
        {"l": "C4", "d": "2026-03-18", "s": 0, "e": "gone", "before": 300},
        {"l": "C4", "d": "2026-03-19", "s": 350, "e": "reappear", "before": 0},
        {"l": "C4", "d": "2026-03-20", "s": 200, "e": "change", "before": 300},
    ]
    (tmp_path / "history").mkdir()
    with gzip.open(tmp_path / "history/events.jsonl.gz", "wt", encoding="utf-8") as stream:
        for event in events:
            stream.write(json.dumps(event) + "\n")
    path = tmp_path / "history.db"
    build_history_db(tmp_path, path, verbose=False)
    reader = StockHistoryDatabase(path)
    monkeypatch.setattr(server, "get_history_db", lambda: reader)
    stocks = {"C1": {"stock": 123}, "C2": {"stock": 456}, "C4": {"stock": 789}}
    monkeypatch.setattr(server, "get_db", lambda: SimpleNamespace(
        get_by_lcsc=stocks.get,
        get_by_lcsc_batch=lambda codes: {code: stocks.get(code) for code in codes},
        get_sold_out_rows=lambda codes: dict.fromkeys(codes),
        scraped_at=lambda: "2026-03-21",
    ))
    yield reader
    reader.close()


async def test_single_reply_unchanged(history_db):
    reply = await server.jlc_stock_history(" c2 ", 20)
    expected = {
        "lcsc": "C2",
        "window": {"start": "2026-03-01", "end": "2026-03-20",
                   "history_start": "2026-03-01", "history_end": "2026-03-20"},
        "events": [
            {"date": "2026-03-20", "type": "type_change", "stock_after": 1500, "note": None},
            {"date": "2026-03-05", "type": "gone", "stock_after": None,
             "note": "Missing from this scrape; not a confirmed stockout or evidence it is still unavailable.",
             "stock_before": 250},
            {"date": "2026-03-03", "type": "new", "stock_after": 250, "note": None},
            {"date": "2026-03-02", "type": "gone", "stock_after": None,
             "note": "Missing from this scrape; not a confirmed stockout or evidence it is still unavailable.",
             "stock_before": 800},
            {"date": "2026-03-01", "type": "new", "stock_after": 800, "note": None,
             "stock_before": 1000},
        ],
        "more_events": False,
        "what_is_recorded": dict(WHAT_IS_RECORDED),
        "current_stock": 456,
        "current_stock_as_of": "2026-03-21",
    }
    # JSON comparison checks the order of every key, as well as values.
    assert json.dumps(reply) == json.dumps(expected)


async def test_order_dedupe_and_shared_notes(history_db):
    reply = await server.jlc_stock_history([" c2 ", "c1", "C2", " C1 ", "C999"], 20)
    assert list(reply) == ["window", "parts", "what_is_recorded", "current_stock_as_of"]
    assert [part["lcsc"] for part in reply["parts"]] == ["C2", "C1", "C999"]
    assert [part["current_stock"] for part in reply["parts"]] == [456, 123, None]
    assert reply["window"] == (await server.jlc_stock_history("C1", 20))["window"]
    assert reply["what_is_recorded"] == WHAT_IS_RECORDED
    assert reply["current_stock_as_of"] == "2026-03-21"
    assert all(list(part) == ["lcsc", "current_stock", "summary", "events", "more_events"]
               for part in reply["parts"])
    assert json.dumps(reply).count('"what_is_recorded"') == 1


async def test_full_window_summaries_and_cap(history_db):
    reply = await server.jlc_stock_history(["C1", "C2", "C3", "C999"], 20)
    assert [part["summary"] for part in reply["parts"]] == [
        {"events": 13, "gone": 1, "lowest_recorded": 5, "last_gone": "2026-03-01"},
        {"events": 5, "gone": 2, "lowest_recorded": 250, "last_gone": "2026-03-05"},
        {"events": 1, "gone": 1, "lowest_recorded": None, "last_gone": "2026-03-20"},
        {"events": 0, "gone": 0, "lowest_recorded": None, "last_gone": None},
    ]
    for part in reply["parts"]:
        single = await server.jlc_stock_history(part["lcsc"], 20)
        assert part["events"] == single["events"][:10]
        assert part["more_events"] == (part["summary"]["events"] > 10)
    assert len(reply["parts"][0]["events"]) == 10
    assert reply["parts"][0]["events"][0]["type"] == "type_change"
    shorter = await server.jlc_stock_history(["C1", "C2"], 10)
    assert [part["summary"] for part in shorter["parts"]] == [
        {"events": 3, "gone": 0, "lowest_recorded": 110, "last_gone": None},
        {"events": 1, "gone": 0, "lowest_recorded": 1500, "last_gone": None},
    ]
    exact = await server.jlc_stock_history(["C1"], 17)
    assert len(exact["parts"][0]["events"]) == 10
    assert exact["parts"][0]["more_events"] is False


@pytest.mark.parametrize("days", [20, 4, 2], ids=["all", "edge", "return"])
async def test_suspect_notes_and_before_values_match_single(history_db, days):
    part = (await server.jlc_stock_history(["C4"], days))["parts"][0]
    single = await server.jlc_stock_history("C4", days)
    assert json.dumps(part["events"]) == json.dumps(single["events"])
    returned = next(event for event in part["events"] if event["type"] == "reappear")
    assert returned["stock_before"] == 0
    assert "suspect_scrape" in returned["note"]
    assert single["events"][0]["stock_before"] == 300


async def test_invalid_codes_are_per_part_and_bounded(history_db):
    codes = [" bad ", "C2", "c" + "1" * 100, "C\u0661", "", "  ", "BAD"]
    reply = await server.jlc_stock_history(codes)
    assert [part["lcsc"] for part in reply["parts"]] == ["BAD", "C2", "C" + "1" * 19, "C\u0661", ""]
    for part in reply["parts"]:
        if part["lcsc"] != "C2":
            assert part == {"lcsc": part["lcsc"], **await server.jlc_stock_history(part["lcsc"])}
    assert reply["parts"][1]["current_stock"] == 456


@pytest.mark.parametrize("codes", [[], ["C1"] * 51, "[]", json.dumps(["C1"] * 51)],
                         ids=["empty", "51", "json-empty", "json-51"])
async def test_invalid_batch_size(history_db, codes):
    reply = await server.jlc_stock_history(codes)
    assert "error" in reply and "parts" not in reply
    assert server._error_kind(reply["error"]) == "bad_request"


async def test_json_array_and_literal_string(history_db):
    assert await server.jlc_stock_history('[" c2 ", "C1", "C2"]') == await server.jlc_stock_history([" c2 ", "C1", "C2"])
    assert await server.jlc_stock_history("C1,C2") == await server.jlc_stock_history("bad")
    reply = await server.jlc_stock_history([f"C{n}" for n in range(50)])
    assert len(reply["parts"]) == 50


async def test_input_schema_and_client_stats(history_db, monkeypatch):
    # Replace only the startup/shutdown work: the real MCP schema, call handling and stats run.
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app):
        yield {}

    monkeypatch.setattr(server.mcp, "_lifespan", lifespan)
    async with Client(server.mcp) as client:
        tool = next(tool for tool in await client.list_tools() if tool.name == "jlc_stock_history")
        for value in ("C1", ["C1", "C2"], '["C1"]'):
            validate({"lcsc": value}, tool.inputSchema)
        assert {item["type"] for item in tool.inputSchema["properties"]["lcsc"]["anyOf"]} == {"string", "array"}
        assert "newest 100 events, a list 10 each" in tool.description
        for value, outcome in (("C999", "ok"), (["C999", "bad"], "ok"), (["bad"], "bad_request")):
            reply = await client.call_tool("jlc_stock_history", {"lcsc": value})
            assert server._call_outcome(reply) == outcome
    counts = stats.usage.summary()["days"][0]["tools"]["jlc_stock_history"]
    assert counts["ok"] == 2 and counts["bad_request"] == 1 and counts["not_found"] == 0


def test_batch_queries_use_one_summary_and_indexed_event_reads(history_db):
    history_db._ensure_db()
    queries = []
    history_db._conn.set_trace_callback(queries.append)
    try:
        history_db.history_many(["C1", "C2"], 20)
    finally:
        history_db._conn.set_trace_callback(None)
    assert sum("GROUP BY" in query for query in queries) == 1
    event_reads = [query for query in queries if "ORDER BY date DESC" in query]
    assert len(event_reads) == 2
    for query in event_reads:
        plan = history_db._conn.execute("EXPLAIN QUERY PLAN " + query).fetchall()
        assert any("PRIMARY KEY" in row[3] for row in plan)
        assert all("SCAN stock_events" not in row[3] for row in plan)


def test_legacy_schema_and_empty_history(tmp_path):
    path = tmp_path / "legacy.db"
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("CREATE TABLE stock_events (lcsc TEXT, date TEXT, stock INTEGER, event_type TEXT)")
    reader = StockHistoryDatabase(path)
    try:
        reply = reader.history_many(["C1"])
        assert set(reply["window"].values()) == {None}
        assert reply["parts"][0]["summary"] == {"events": 0, "gone": 0, "lowest_recorded": None, "last_gone": None}
        with closing(sqlite3.connect(path)) as conn, conn:
            conn.execute("INSERT INTO stock_events VALUES ('C1', '2026-03-20', 50, 'change')")
        reader.close()
        assert reader.history_many(["C1"])["parts"][0]["events"] == reader.history("C1")["events"]
    finally:
        reader.close()
