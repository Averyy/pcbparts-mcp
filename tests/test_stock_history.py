"""Local recorded history: real observations, censoring, scrape gaps and runtime boundaries."""

import gzip
import json
import runpy
import sqlite3
import sys
import threading
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from pcbparts_mcp import server
from pcbparts_mcp.history_db import StockHistoryDatabase

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_history_db import build_history_db


@pytest.fixture(scope="module")
def real_history(tmp_path_factory):
    source = StockHistoryDatabase(ROOT / "data/stock_history.db")
    source._ensure_db()
    # A stale local artifact would silently omit the real November observations.
    try:
        assert source._history_start == "2026-02-21"
        assert source._history_end >= "2026-11-09", "Rebuild with scripts/build_history_db.py"
        # Freeze this regression window while daily data continues to accumulate.
        rows = source._conn.execute(
            "SELECT lcsc, date, stock, event_type FROM stock_events "
            "WHERE lcsc IN ('C8314','C12113','C22373856','C3975129','C111113') AND date <= '2026-11-09'"
        ).fetchall()
        rows += source._conn.execute(
            "SELECT lcsc, date, stock, event_type FROM stock_events WHERE date='2026-11-09' LIMIT 1"
        ).fetchall()
        # Global coverage begins before these four parts' first recorded events.
        rows += source._conn.execute(
            "SELECT lcsc, date, stock, event_type FROM stock_events WHERE date='2026-02-21' LIMIT 1"
        ).fetchall()
        records = [{"l": lcsc, "d": day, "s": stock, "e": kind} for lcsc, day, stock, kind in rows]
    finally:
        source.close()
    reader = build_reader(tmp_path_factory.mktemp("real-stock-history"), records)
    yield reader
    reader.close()


@pytest.fixture
def tool_history(monkeypatch, real_history):
    monkeypatch.setattr(server, "get_history_db", lambda: real_history)
    return real_history


def build_reader(tmp_path, events):
    (tmp_path / "history").mkdir()
    with gzip.open(tmp_path / "history/events.jsonl.gz", "wt") as stream:
        for event in events:
            stream.write(json.dumps(event) + "\n")
    db_path = tmp_path / "history.db"
    build_history_db(tmp_path, db_path, verbose=False)
    return StockHistoryDatabase(db_path)


async def test_c8314_real_march_observations(tmp_path, monkeypatch, real_history):
    # Replay an earlier slice of the real records: March is outside today's newest
    # 100 observations, and there is intentionally no date override in this API.
    with sqlite3.connect(real_history.db_path) as conn:
        records = [{"l": "C8314", "d": day, "s": stock, "e": kind}
                   for day, stock, kind in conn.execute(
                       "SELECT date, stock, event_type FROM stock_events "
                       "WHERE lcsc='C8314' AND date <= '2026-03-13' ORDER BY date")]
    reader = build_reader(tmp_path, records)
    monkeypatch.setattr(server, "get_history_db", lambda: reader)
    try:
        reply = await server.jlc_stock_history(" c8314 ", 366)
        assert reply["lcsc"] == "C8314"
        assert reply["window"]["end"] == "2026-03-13"
        assert [(e["date"], e["stock_after"]) for e in reply["events"][:2]] == [
            ("2026-03-13", 280), ("2026-03-12", 344)]
        assert all("stock_before" not in e for e in reply["events"])
        # 344 was a previous *event*, never a defensible before-value for March 13.
        assert "no before-values" in reply["what_is_recorded"]["before"]
    finally:
        reader.close()


@pytest.mark.parametrize("lcsc,gone,returned,stock", [
    ("C22373856", "2026-03-18", "2026-03-19", 340),
    ("C3975129", "2026-03-16", "2026-03-17", 630),
])
async def test_real_scrape_gap_is_not_a_stockout(tool_history, lcsc, gone, returned, stock):
    # Losses on a gap day too small to be corrected stay labelled.
    reply = await server.jlc_stock_history(lcsc, 366)
    events = {e["date"]: e for e in reply["events"]}
    assert events[gone]["type"] == "gone"
    assert events[gone]["stock_after"] is None
    assert "suspect_scrape" in events[gone]["note"]
    assert "not a confirmed stockout" in events[gone]["note"]
    assert events[returned]["type"] == "new"
    assert events[returned]["stock_after"] == stock
    assert "scrape gap" in events[returned]["note"]
    assert "not a confirmed restock" in events[returned]["note"]


async def test_gap_warning_survives_window_boundary(tool_history):
    reply = await server.jlc_stock_history("C22373856", 236)
    assert reply["window"]["start"] == "2026-03-19"
    returned = next(e for e in reply["events"] if e["date"] == "2026-03-19")
    assert "suspect_scrape" in returned["note"]


@pytest.mark.parametrize("lcsc,days", [
    ("C12113", ("2026-03-03", "2026-03-04")),     # its subcategory was among 42 missing on 03-03
    ("C22373856", ("2026-05-15", "2026-05-16")),  # and among 5 on 05-15
    ("C3975129", ("2026-05-15", "2026-05-16")),
])
async def test_corrected_gaps_leave_no_false_events(tool_history, lcsc, days):
    """Bulk-missing subcategories on gap days were corrected in the history files the way the
    scraper now carries them: no gone-then-new pair for a part that was never unavailable."""
    reply = await server.jlc_stock_history(lcsc, 366)
    assert not [e for e in reply["events"] if e["date"] in days]


async def test_high_stock_return_without_recorded_return(tool_history):
    reply = await server.jlc_stock_history("C111113", 366)
    last = reply["events"][0]
    assert (last["date"], last["type"], last["stock_after"]) == ("2026-03-16", "gone", None)
    assert "Returns above 1,000 may be unrecorded" in last["note"]
    assert reply["current_stock"] == server.get_db().get_by_lcsc("C111113")["stock"]
    assert reply["current_stock"] > 1000  # 112,336 on 2026-11-11
    assert reply["current_stock_as_of"] == server.get_db().scraped_at()


async def test_unknown_part_is_a_normal_empty_reply(tool_history):
    reply = await server.jlc_stock_history("C999999999999")  # 12 digits: the longest code accepted
    assert reply["events"] == []
    assert reply["current_stock"] is None
    assert reply["more_events"] is False
    assert server._call_outcome(SimpleNamespace(structured_content=reply)) == "ok"


async def test_empty_history_with_listed_part(tmp_path, monkeypatch):
    reader = build_reader(tmp_path, [])
    monkeypatch.setattr(server, "get_history_db", lambda: reader)
    try:
        reply = await server.jlc_stock_history("C2040")
        assert reply["events"] == []
        assert set(reply["window"].values()) == {None}
        assert reply["current_stock"] == server.get_db().get_by_lcsc("C2040")["stock"]
    finally:
        reader.close()


@pytest.mark.parametrize("days", [1, 180, 366])
async def test_latest_inclusive_window(tool_history, days):
    reply = await server.jlc_stock_history("C8314", days)
    window = reply["window"]
    assert (date.fromisoformat(window["end"]) - date.fromisoformat(window["start"])).days == days - 1
    assert window["history_start"] == "2026-02-21"
    assert window["history_end"] == window["end"] == "2026-11-09"
    assert all(window["start"] <= e["date"] <= window["end"] for e in reply["events"])
    assert "2026-08-07" in reply["what_is_recorded"]["dates"]


@pytest.mark.parametrize("days", [0, -1, 367, True, 1.5, "180"])
async def test_invalid_days(days):
    reply = await server.jlc_stock_history("C8314", days)
    assert reply == {"error": "Invalid days: use an integer from 1 to 366"}
    assert server._call_outcome(SimpleNamespace(structured_content=reply)) == "bad_request"


@pytest.mark.parametrize("lcsc", ["", "STM32F103VBT6", "C8314,C12113", "C8314 OR 1=1"])
async def test_one_code_only(lcsc):
    reply = await server.jlc_stock_history(lcsc)
    assert server._call_outcome(SimpleNamespace(structured_content=reply)) == "bad_request"


async def test_real_events_are_capped_newest_first(tool_history):
    reply = await server.jlc_stock_history("C8314", 366)
    assert len(reply["events"]) == 100
    assert reply["more_events"] is True
    with sqlite3.connect(tool_history.db_path) as conn:
        expected = conn.execute(
            "SELECT date, event_type, stock FROM stock_events WHERE lcsc='C8314' "
            "ORDER BY date DESC, event_type DESC LIMIT 100").fetchall()
        assert conn.execute(
            "SELECT MIN(stock),MAX(stock) FROM stock_events WHERE lcsc='C8314' AND event_type='change'"
        ).fetchone() == (23, 977)
    assert [(e["date"], e["type"], e["stock_after"]) for e in reply["events"]] == [
        (day, kind, None if kind == "gone" else stock) for day, kind, stock in expected]


@pytest.mark.parametrize("broken", [False, True])
async def test_unavailable_database_is_failed(tmp_path, monkeypatch, broken):
    path = tmp_path / "unavailable.db"
    if broken:
        path.write_text("not a SQLite database", encoding="utf-8")
    reader = StockHistoryDatabase(path)
    monkeypatch.setattr(server, "get_history_db", lambda: reader)
    reply = await server.jlc_stock_history("C8314")
    assert reply == {"error": "Stock history is not available on this server"}
    assert server._call_outcome(SimpleNamespace(structured_content=reply)) == "failed"
    assert server._first_reason(server._FAILED_REASONS, reply["error"]) == "service_not_ready"
    assert reader._conn is None
    assert path.exists() == broken  # A missing DB must never be created by a read.


def test_before_values_only_when_recorded(tmp_path):
    reader = build_reader(tmp_path, [
        {"l": "C1", "d": "2026-11-08", "s": 100},
        {"l": "C1", "d": "2026-11-09", "s": 50, "before": 90},
        {"l": "C1", "d": "2026-11-10", "s": 0, "e": "gone", "before": 50},
        {"l": "C2", "d": "2026-11-10", "s": 50, "e": "new", "before": None},
    ])
    try:
        events = reader.history("C1")["events"]
        assert events[0]["stock_before"] == 50 and events[0]["stock_after"] is None
        assert events[1]["stock_before"] == 90  # Not the previous recorded 100.
        assert "stock_before" not in events[2]
        assert "stock_before" not in reader.history("C2")["events"][0]
    finally:
        reader.close()


def test_legacy_database_without_before_column(tmp_path):
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE stock_events (lcsc TEXT, date TEXT, stock INTEGER, event_type TEXT)")
        conn.execute("INSERT INTO stock_events VALUES ('C1','2026-03-13',280,'change')")
    reader = StockHistoryDatabase(path)
    try:
        assert reader.history("C1")["events"] == [
            {"date": "2026-03-13", "type": "change", "stock_after": 280, "note": None}]
    finally:
        reader.close()


async def test_history_and_snapshot_access_off_loop(tool_history, monkeypatch):
    loop_thread = threading.get_ident()
    history, lookup = tool_history.history, server.get_db().get_by_lcsc

    def read(*args):
        assert threading.get_ident() != loop_thread
        return history(*args)

    def snapshot(*args):
        assert threading.get_ident() != loop_thread
        return lookup(*args)

    monkeypatch.setattr(tool_history, "history", read)
    monkeypatch.setattr(server.get_db(), "get_by_lcsc", snapshot)
    assert (await server.jlc_stock_history("C8314"))["events"]


def test_config_respects_data_dir_and_override(tmp_path, monkeypatch):
    monkeypatch.setenv("JLCPCB_DATA_DIR", str(tmp_path / "catalog"))
    monkeypatch.delenv("JLCPCB_HISTORY_DB_PATH", raising=False)
    config = runpy.run_path(str(ROOT / "src/pcbparts_mcp/config.py"))
    assert config["STOCK_HISTORY_DB_PATH"] == tmp_path / "catalog/stock_history.db"
    monkeypatch.setenv("JLCPCB_HISTORY_DB_PATH", str(tmp_path / "override.db"))
    config = runpy.run_path(str(ROOT / "src/pcbparts_mcp/config.py"))
    assert config["STOCK_HISTORY_DB_PATH"] == tmp_path / "override.db"


@pytest.mark.parametrize("code", ["C" + "1" * 1_000_000, "C" + "1" * 13, "C\u0661\u0662"])
async def test_overlong_or_non_ascii_codes_are_refused_without_echo(tool_history, code):
    """0.9.0 limits check: "C" plus a million digits was accepted and echoed in a 1 MB reply."""
    reply = await server.jlc_stock_history(code)
    assert reply == {"error": "lcsc must be an LCSC C-code (e.g., C6186); use jlc_get_part(mpn=...) to find the code for an MPN"}
