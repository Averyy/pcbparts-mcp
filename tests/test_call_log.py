"""Private 0.10.5 stores: content boundaries, UTC files, failure isolation and HTTP wiring."""

import asyncio
import datetime as dt
import gzip
import ipaddress
import json
import logging
import runpy
import sqlite3
import threading
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastmcp import Client, FastMCP
from starlette.middleware import Middleware

from pcbparts_mcp import call_log, config, server, stats
from pcbparts_mcp.platform_ranges import PlatformRanges
from test_usage_stats import Clock

DATE = "2026-10-17"


def record(log, tool="jlc_search", outcome="not_found", reason="no_results", args=None, content=None, **kwargs):
    log.record(tool, outcome, reason, kwargs.pop("bad_request_reason", None), 123.4, "<app>", False,
               args or {"query": " Secret  Ω "}, content or {}, kwargs.pop("notes", {}),
               kwargs.pop("params", {"query"}), **kwargs)


def read_rows(path, date=DATE):
    source = path / f"calls-{date}.jsonl"
    opener = open
    if not source.exists():
        source, opener = source.with_suffix(".jsonl.gz"), gzip.open
    with opener(source, "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


def failed(path, date=DATE):
    return json.loads((path / f"failed-{date}.json").read_text(encoding="utf-8"))


def test_settings(monkeypatch):
    for name in ("CALL_LOG_DIR", "CALL_LOG_DAYS", "FAILED_QUERY_DAYS", "FAILED_QUERY_CAP"):
        monkeypatch.delenv(name, raising=False)
    values = runpy.run_path(config.__file__)
    assert [values[key] for key in ("CALL_LOG_DIR", "CALL_LOG_DAYS", "FAILED_QUERY_DAYS", "FAILED_QUERY_CAP")] == ["", 30, 7, 5000]
    monkeypatch.setenv("CALL_LOG_DIR", "/tmp/example")
    monkeypatch.setenv("CALL_LOG_DAYS", "0")
    monkeypatch.setenv("FAILED_QUERY_DAYS", "bad")
    monkeypatch.setenv("FAILED_QUERY_CAP", "-2")
    values = runpy.run_path(config.__file__)
    assert [values[key] for key in ("CALL_LOG_DIR", "CALL_LOG_DAYS", "FAILED_QUERY_DAYS", "FAILED_QUERY_CAP")] == ["/tmp/example", 1, 7, 1]
    docker = (Path(__file__).resolve().parents[1] / "Dockerfile").read_text(encoding="utf-8")
    assert "ENV CALL_LOG_DIR=/app/cache/call-log" in docker
    assert "COPY --chown=appuser:appuser scripts/usage_report.py /app/scripts/" in docker


async def test_disabled_has_no_recording_or_io(tmp_path, monkeypatch):
    log = call_log.CallLog(clock=Clock())

    def no_io(*args, **kwargs):
        raise AssertionError("disabled recorder did I/O")

    monkeypatch.setattr(call_log, "_persist", no_io)
    monkeypatch.setattr(call_log, "_load_failed", no_io)
    await log.open("")
    record(log)
    log.refusal("per_ip_rate_limit", True)
    await log.flush()
    assert log._rows == [] and log._failed == {} and not list(tmp_path.iterdir())


async def test_rows_failed_normalization_cap_restart(tmp_path):
    log = call_log.CallLog(clock=Clock(), failed_cap=2)
    await log.open(tmp_path)
    record(log)
    record(log, args={"query": "secret Ω"})
    record(log, args={"query": "more\x00\u200b text\r"})
    record(log, args={"query": "overflow"})
    record(log, args={"query": "overflow"})
    assert not (tmp_path / f"calls-{DATE}.jsonl").exists()
    await log.flush()
    row = read_rows(tmp_path)[0]
    assert row == {"t": "2026-10-17T21:15:00Z", "tool": "jlc_search", "outcome": "not_found",
                   "reason": "no_results", "bad_request_reason": None, "ms": 123, "app": "other",
                   "platform": False, "shape": {"args": ["query"]}}
    assert "secret" not in json.dumps(read_rows(tmp_path))
    assert failed(tmp_path) == {"date": DATE, "dropped": 2, "queries": [
        {"tool": "jlc_search", "reason": "no_results", "text": "secret ω", "count": 2},
        {"tool": "jlc_search", "reason": "no_results", "text": "more text", "count": 1}]}
    again = call_log.CallLog(clock=Clock(), failed_cap=2)
    await again.open(tmp_path)
    record(again)
    record(again, args={"query": "overflow"})
    await again.flush()
    assert failed(tmp_path)["queries"][0]["count"] == 3 and failed(tmp_path)["dropped"] == 3
    assert len(read_rows(tmp_path)) == 7
    assert len(call_log.normalize_text("İ" * 300)) == 200
    assert call_log.normalize_text(" \x00\u200b\ud800 ") == ""


@pytest.mark.parametrize("reason", sorted(call_log._EXCLUDED))
def test_excluded_not_found_but_all_failed(reason):
    args = {"query": "secret"}
    assert list(call_log.failed_texts("jlc_search", "not_found", reason, args, {})) == []
    assert list(call_log.failed_texts("jlc_search", "failed", reason, args, {})) == [(reason, "secret")]
    assert list(call_log.failed_texts("jlc_search", "not_found", "part_number_unknown", {}, {})) == []


@pytest.mark.parametrize("tool,args,text", [
    ("jlc_search", {"query": "a"}, "a"), ("jlc_stock_check", {"query": "b"}, "b"),
    ("cse_search", {"query": "c"}, "c"), ("board_search", {"query": "d"}, "d"),
    ("sensor_recommend", {"query": "e"}, "e"),
    ("jlc_get_part", {"lcsc": "C1", "mpn": "p"}, "C1"), ("jlc_get_part", {"mpn": "p"}, "p"),
    ("jlc_find_alternatives", {"lcsc": "C2"}, "C2"),
    ("jlc_get_pinout", {"uuid": "uuid"}, "uuid"), ("jlc_get_pinout", {"lcsc": "C3", "uuid": "uuid"}, "C3"),
    ("digikey_get_part", {"part_number": "x"}, "x"),
    ("cse_get_kicad", {"query": "q"}, "q"), ("cse_get_kicad", {"query": "q", "part_id": 1}, None),
    ("get_design_rules", {"topic": "usb"}, "usb"), ("board_get", {"slug": "board"}, "board"),
    ("jlc_stock_history", {"lcsc": "C4"}, None), ("jlc_search_help", {"subcategory": "x"}, None),
], ids=[f"p{i}" for i in range(17)])
def test_primary_text(tool, args, text):
    result = list(call_log.failed_texts(tool, "failed", "exception", args, {}))
    assert result == ([] if text is None else [("exception", text)])
    assert list(call_log.failed_texts(tool, "ok", None, args, {})) == []


def test_batch_text_uses_original_index_and_mouser_exclusions():
    inputs = ["ok", {"mpn": "long" * 40, "manufacturer": "Maker"}, "C99", "not fitted"]
    rows = [{}, {"not_found": True, "input": "truncated"}, {"lookup_failed": True}, {"not_sent": "placeholder"}]
    assert list(call_log.failed_texts("part_lifecycle", "ok", None, {"parts": json.dumps(inputs)}, {"results": rows})) == [
        ("row_not_found", "long" * 40 + " | Maker"), ("row_lookup_failed", "C99")]
    assert list(call_log.failed_texts("jlc_get_parts", "ok", None, {"parts": inputs}, {"results": rows})) == [
        ("row_not_found", "long" * 40 + " | Maker")]
    assert list(call_log.failed_texts("jlc_get_parts", "failed", "exception", {"parts": ["C1", {"mpn": "p"}]}, {})) == [
        ("exception", "C1"), ("exception", "p")]
    reply = {"results": [{"mpn": "ok"}], "not_found": ["missing", "DNP"], "not_sent": {"DNP": "placeholder"}}
    assert list(call_log.failed_texts("mouser_get_part", "ok", None, {}, reply)) == [("row_not_found", "missing")]
    assert list(call_log.failed_texts("mouser_get_part", "failed", "exception", {"part_number": "aa|bb"}, {})) == [
        ("exception", "aa"), ("exception", "bb")]


def catalog():
    return call_log.ShapeCatalog({1: "Resistors"}, {2: ("Chip Resistors", "Resistors")},
                                 {"resistors": "Resistors"}, {"chip resistors": "Chip Resistors"},
                                 frozenset({"0603", "SOT-23"}), frozenset({"Resistance", "Tolerance"}))


def test_shape_catalog_whitelist():
    cat = catalog()
    args = {"query": "SECRET", "manufacturer": "SECRET", "package": "secret", "unused": None,
            "unknown1": "SECRET", "unknown2": "SECRET", "strict": True, "sort_by": "price",
            "match_all_terms": False, "library_type": "basic"}
    reply = {"filters_applied": {"subcategory_resolved": "SECRET", "subcategory_id": 2,
             "category_resolved": "SECRET", "packages": ["0603", "0603 SECRET"],
             "spec_filters": [{"name": "Resistance", "value": "SECRET"}, {"name": "SECRET"}]}}
    shape = cat.shape("jlc_search", args, reply, {}, set(args) - {"unknown1", "unknown2"})
    assert shape == {"args": ["library_type", "manufacturer", "match_all_terms", "package", "query", "sort_by", "strict", "unknown_argument"],
                     "category": "Resistors", "subcategory": "Chip Resistors", "package": "other",
                     "packages": ["0603", "other"], "spec_filters": ["Resistance", "other"],
                     "library_type": "basic", "strict": True, "sort_by": "price", "match_all_terms": False}
    assert "SECRET" not in json.dumps(shape)
    shape = cat.shape("jlc_stock_check", {"subcategory_name": "some words", "package": "0603", "library_type": "basic"},
                      {}, {"stock_shape": {"subcategory_id": 2}}, {"subcategory_name", "package", "library_type"})
    assert shape["subcategory"] == "Chip Resistors" and shape["category"] == "Resistors"
    assert shape["package"] == "0603" and shape["library_type"] == "basic"
    assert cat.shape("board_get", {"slug": "SECRET", "focus": "SECRET"}, {}, {}, {"slug", "focus"}) == {"args": ["focus", "slug"]}
    invalid = {"library_type": [], "strict": "yes", "sort_by": "SECRET", "category_id": [], "subcategory_name": "SECRET"}
    assert cat.shape("jlc_search", invalid, {}, {}, set(invalid)) == {"args": sorted(invalid)}


@pytest.mark.parametrize("name,expected", [
    ("Part_Numbers", "Part_Numbers"), ("parts", "parts"), ("PARTS", "PARTS"),
    ("a", "a"), ("_", "_"), ("a" * 30, "a" * 30),
    ("lm358p", "unknown_argument"), ("part1", "unknown_argument"),
    ("part numbers", "unknown_argument"), ("part-numbers", "unknown_argument"),
    ("part.numbers", "unknown_argument"), ("párts", "unknown_argument"),
    ("a" * 31, "unknown_argument"), ("a" * 1000, "unknown_argument"),
    ("", "unknown_argument"), ("parts\n", "unknown_argument"),
    ("203.0.113.1", "unknown_argument"), ("2001:db8::1", "unknown_argument"),
], ids=[f"name{i}" for i in range(18)])
def test_unrecognized_argument_names(name, expected):
    shape = catalog().shape("board_get", {name: "PRIVATE VALUE"}, {}, {}, set())
    assert shape == {"args": [expected]}


@pytest.mark.parametrize("name", ["partNumber", "MPNsList", "alice_smith", "Texas_Instruments", "q_" * 15])
def test_unknown_argument_ascii_names_keep_original_case(name):
    assert catalog().shape("board_get", {name: "PRIVATE VALUE"}, {}, {}, set()) == {"args": [name]}


def test_declared_argument_names_keep_existing_limits():
    params = {"part1", "Declared_Name", "a" * 40, "b" * 41}
    shape = catalog().shape("board_get", dict.fromkeys(params, "PRIVATE VALUE"), {}, {}, params)
    assert shape == {"args": ["Declared_Name", "a" * 40, "b" * 40, "part1"]}


@pytest.mark.parametrize("count", [18, 19, 25])
def test_unrecognized_argument_names_sorted_deduplicated_and_capped(count):
    words = "search keyword term text list item page size count max min result num number type filter value code key sort order by id name part".split()
    names = ["Name_" + word.capitalize() for word in reversed(words[:count])]
    args = dict.fromkeys(names, False) | {"query": "PRIVATE VALUE", "lm358p": 0, "part1": [],
                                        "unknown_argument": True, "unused": None}
    shape = catalog().shape("jlc_search", args, {}, {}, {"query"})
    expected = sorted([*names, "query", "unknown_argument"])
    assert shape["args"] == expected[:20]
    assert shape.get("args_omitted", 0) == max(0, len(expected) - 20)
    assert ("args_omitted" in shape) == (len(expected) > 20)


def test_batch_and_source_shapes(monkeypatch):
    cat = catalog()
    items = [" C123 ", "MPN", {"mpn": "C1815"}, {"lcsc": "c2", "mpn": "x"}, {"lcsc": "N/A", "mpn": "part"}]
    for tool in ("jlc_get_parts", "part_lifecycle"):
        assert cat.shape(tool, {"parts": json.dumps(items)}, {}, {}, {"parts"}) == {
            "args": ["parts"], "batch": 5, "input": {"lcsc": 2, "mpn": 3}}
    assert cat.shape("jlc_stock_history", {"lcsc": '["C1","C2"]'}, {}, {}, {"lcsc"})["batch"] == 2
    assert cat.shape("mouser_get_part", {"part_number": "a | b | c"}, {}, {}, {"part_number"})["batch"] == 3
    assert cat.shape("mouser_get_part", {"part_number": " a || b | "}, {}, {}, {"part_number"})["batch"] == 2
    assert cat.shape("jlc_get_part", {"mpn": "SECRET", "live": True},
                     {"data_source": {"kind": "snapshot", "provider": "SECRET"}, "live_failed": True}, {}, {"mpn", "live"}) == {
        "args": ["live", "mpn"], "input": "mpn", "live": True, "source": "snapshot", "live_failed": True}
    assert cat.shape("jlc_get_part", {"lcsc": "C1"}, {"data_source": {"kind": "SECRET"}, "live_failed": "SECRET"}, {}, {"lcsc"}) == {
        "args": ["lcsc"], "input": "lcsc", "live": False}
    monkeypatch.setattr(call_log, "MAX_REQUEST_BODY_BYTES", 8)
    assert call_log._items('["0123456789"]') == []
    assert call_log._items("[broken") == []
    assert call_log._items("[" * 2000) == []


def test_catalog_loaded_once_in_one_job():
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE components (package TEXT, attributes TEXT)")
        conn.executemany("INSERT INTO components VALUES (?, ?)", [("0603", '[["Resistance", "10k"]]'),
                                                                   ("0603", '[["Tolerance", "1%"]]')])
        db = SimpleNamespace(_ensure_db=lambda: None, _conn=conn, _categories={1: {"name": "Resistors"}},
                             _subcategories={2: {"name": "Chip Resistors", "category_name": "Resistors"}})
        cat = call_log.load_catalog(db)
        assert cat.packages == {"0603"} and cat.attributes == {"Resistance", "Tolerance"}
    finally:
        conn.close()
    assert cat.shape("jlc_search", {"subcategory_id": 2}, {}, {}, {"subcategory_id"})["category"] == "Resistors"


async def test_startup_rotation_retention_and_midnight(tmp_path):
    clock = Clock()
    for date in ("2026-10-14", "2026-10-16", DATE):
        (tmp_path / f"calls-{date}.jsonl").write_text('{"old":true}\n', encoding="utf-8")
        (tmp_path / f"failed-{date}.json").write_text(json.dumps({"date": date, "dropped": 0, "queries": []}), encoding="utf-8")
    untouched = ["calls-2026-10-14.json", "calls-2026-10-14.jsonl.bak", "failed-2026-10-14.json.bak",
                 "calls-2026-02-31.jsonl", "failed-2026-02-31.json", "other.jsonl.gz"]
    for name in untouched:
        (tmp_path / name).write_text("leave alone", encoding="utf-8")
    log = call_log.CallLog(clock=clock, call_days=2, failed_days=2)
    await log.open(tmp_path)
    assert not (tmp_path / "calls-2026-10-14.jsonl.gz").exists()
    assert not (tmp_path / "failed-2026-10-14.json").exists()
    assert (tmp_path / "calls-2026-10-16.jsonl.gz").exists()
    assert not (tmp_path / "calls-2026-10-16.jsonl").exists()
    assert (tmp_path / f"calls-{DATE}.jsonl").exists()
    record(log)
    clock.advance(86400)
    record(log, outcome="ok", reason=None)
    await log.flush()
    assert len(read_rows(tmp_path)) == 2 and (tmp_path / f"calls-{DATE}.jsonl.gz").exists()
    assert len(read_rows(tmp_path, "2026-10-18")) == 1
    assert not (tmp_path / "calls-2026-10-16.jsonl.gz").exists()
    assert all((tmp_path / name).read_text(encoding="utf-8") == "leave alone" for name in untouched)
    clock.advance(86400 * 3)
    await log.flush()  # idle retention
    assert not log._failed and not list(tmp_path.glob("failed-2026-10-*.json"))


async def test_files_closed_before_replace_and_remove(tmp_path, monkeypatch):
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    await log.open(tmp_path)
    handles = []
    original_open, original_gzip = Path.open, gzip.GzipFile
    original_private = call_log._private_open
    original_replace, original_unlink = call_log.os.replace, Path.unlink

    def opened(path, *args, **kwargs):
        handle = original_open(path, *args, **kwargs)
        handles.append(handle)
        return handle

    def zipped(*args, **kwargs):
        handle = original_gzip(*args, **kwargs)
        handles.append(handle)
        return handle

    def private_open(*args, **kwargs):
        handle = original_private(*args, **kwargs)
        handles.append(handle)
        return handle

    def replaced(src, dest):
        assert handles and all(handle.closed for handle in handles)
        return original_replace(src, dest)

    def removed(path, *args, **kwargs):
        assert all(handle.closed for handle in handles)
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", opened)
    monkeypatch.setattr(call_log, "_private_open", private_open)
    monkeypatch.setattr(gzip, "GzipFile", zipped)
    monkeypatch.setattr(call_log.os, "replace", replaced)
    monkeypatch.setattr(Path, "unlink", removed)
    record(log)
    await log.flush()
    clock.advance(86400)
    await log.flush()
    assert (tmp_path / f"calls-{DATE}.jsonl.gz").exists() and not log._errors


async def test_failures_retry_once_per_streak_and_overflow(tmp_path, monkeypatch, caplog):
    clock = Clock()
    log = call_log.CallLog(clock=clock, row_cap=2)
    await log.open(tmp_path)
    original = call_log._persist

    def broken(*args):
        raise OSError("private text must not reach logs")

    monkeypatch.setattr(call_log, "_persist", broken)
    with caplog.at_level(logging.WARNING, logger="pcbparts_mcp.call_log"):
        for _ in range(4):
            record(log)
        await log.flush()
        await log.flush()
        assert len(log._rows) == 2 and log.dropped_rows == 2
        assert sum("row buffer full" in m for m in caplog.messages) == 1
        assert sum("flush failed" in m for m in caplog.messages) == 1
        monkeypatch.setattr(call_log, "_persist", original)
        await log.flush()
        assert len(read_rows(tmp_path)) == 2 and not log._rows
        assert failed(tmp_path)["queries"][0]["count"] == 4
        monkeypatch.setattr(call_log, "_persist", broken)
        await log.flush()
        assert sum("flush failed" in m for m in caplog.messages) == 2
        clock.advance(86400)
        for _ in range(3):
            record(log)
        assert sum("row buffer full" in m for m in caplog.messages) == 2
    assert "private text" not in caplog.text


async def test_corrupt_load_not_overwritten_and_recovery(tmp_path, caplog):
    dest = tmp_path / f"failed-{DATE}.json"
    dest.write_text("invalid", encoding="utf-8")
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    await log.open(tmp_path)
    record(log)
    await log.flush()
    assert dest.read_text(encoding="utf-8") == "invalid" and len(read_rows(tmp_path)) == 1
    assert sum("load failed" in m for m in caplog.messages) == 1
    clock.advance(86400)
    await log.flush()
    await log.flush()
    assert dest.read_text(encoding="utf-8") == "invalid"
    assert sum("load failed" in m for m in caplog.messages) == 1
    dest.write_text(json.dumps({"date": DATE, "dropped": 1, "queries": [
        {"tool": "jlc_search", "reason": "no_results", "text": "secret Ω", "count": 4}]}), encoding="utf-8")
    await log.flush()
    assert failed(tmp_path)["queries"][0]["count"] == 5
    assert failed(tmp_path)["dropped"] == 1


async def test_unchanged_failed_file_is_not_rewritten(tmp_path, monkeypatch):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    record(log)
    await log.flush()
    original = call_log.os.replace

    def no_replace(*args):
        raise AssertionError("unchanged failed-query store was written")

    monkeypatch.setattr(call_log.os, "replace", no_replace)
    again = call_log.CallLog(clock=Clock())
    await again.open(tmp_path)
    await again.flush()
    assert not again._errors and not again._changed
    monkeypatch.setattr(call_log.os, "replace", original)


async def test_atomic_failed_write_retry(tmp_path, monkeypatch, caplog):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    record(log)
    await log.flush()
    original = call_log.os.replace

    def broken(src, dest):
        if str(dest).endswith(".json"):
            raise PermissionError("injected")
        return original(src, dest)

    monkeypatch.setattr(call_log.os, "replace", broken)
    record(log)
    await log.flush()
    await log.flush()
    assert failed(tmp_path)["queries"][0]["count"] == 1
    assert sum("failed queries failed" in m for m in caplog.messages) == 1
    assert not list(tmp_path.glob("*.tmp"))
    monkeypatch.setattr(call_log.os, "replace", original)
    await log.flush()
    assert failed(tmp_path)["queries"][0]["count"] == 2
    assert len(read_rows(tmp_path)) == 2


async def test_snapshot_during_write_cancel_and_inflight_cap(tmp_path, monkeypatch):
    log = call_log.CallLog(clock=Clock(), row_cap=2)
    await log.open(tmp_path)
    record(log)
    record(log)
    loop, thread = asyncio.get_running_loop(), threading.get_ident()
    entered, release = asyncio.Event(), threading.Event()
    original = call_log._persist

    def write(*args):
        assert threading.get_ident() != thread
        loop.call_soon_threadsafe(entered.set)
        release.wait()
        return original(*args)

    monkeypatch.setattr(call_log, "_persist", write)
    task = asyncio.create_task(log.flush())
    try:
        await entered.wait()
        record(log)
        assert log.dropped_rows == 1  # in-flight rows still occupy the bound
        task.cancel()
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    monkeypatch.setattr(call_log, "_persist", original)
    await log.flush()
    assert len(read_rows(tmp_path)) == 2
    assert failed(tmp_path)["queries"][0]["count"] == 3


async def test_rotation_retry_after_remove_failure(tmp_path, monkeypatch):
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    await log.open(tmp_path)
    record(log)
    await log.flush()
    original = Path.unlink

    def broken(path, *args, **kwargs):
        if path.suffix == ".jsonl":
            raise PermissionError("injected")
        return original(path, *args, **kwargs)

    clock.advance(86400)
    monkeypatch.setattr(Path, "unlink", broken)
    await log.flush()
    assert "rotation" in log._errors
    monkeypatch.setattr(Path, "unlink", original)
    await log.flush()
    assert len(read_rows(tmp_path)) == 1  # source is authoritative until removed


async def test_http_platform_ranges_aliases_final_reason_and_terms(tmp_path, monkeypatch):
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    await log.open(tmp_path)
    log.catalog = catalog()
    monkeypatch.setattr(call_log, "recorder", log)
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    monkeypatch.setattr(server, "time", SimpleNamespace(monotonic=lambda: 10, time=clock))
    mcp = FastMCP("logging")
    reply = {"results": [], "total": 0}

    @mcp.tool
    async def jlc_search(query: str):
        stats.note(reason="no_results_words")
        return reply

    @mcp.tool
    async def digikey_get_part(part_number: str):
        return {"number": part_number}

    @mcp.tool
    async def part_lifecycle(parts: list[str]):
        raise AssertionError("invalid arguments reached the tool")

    tools = await mcp.list_tools(run_middleware=False)
    stats.usage.tools = {t.name for t in tools}
    stats.usage.tool_params = {t.name: set(t.parameters["properties"]) for t in tools}
    mcp.add_middleware(server.ArgumentAliasMiddleware())
    mcp.add_middleware(server.UsageStatsMiddleware())
    ranges = PlatformRanges({"test": [ipaddress.ip_network("198.51.100.0/24")]})
    app = mcp.http_app(stateless_http=True, json_response=True, middleware=[
        Middleware(server.RateLimitMiddleware, requests_per_minute=100, platform_per_minute=200,
                   platform_addresses=ranges, clock=clock, wall_clock=clock)])

    async def rpc(client, method, params, ip):
        return await client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                                 headers={"Accept": "application/json, text/event-stream", "X-Forwarded-For": ip})

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as client:
            await rpc(client, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                             "clientInfo": {"name": "<backplane>", "version": "1"}}, "198.51.100.1")
            for ip in [*(f"198.51.100.{i}" for i in range(1, 16)), *(f"2001:db8:1::{i}" for i in range(1, 16)),
                       *(f"203.0.113.{i}" for i in range(1, 9))]:
                response = await rpc(client, "tools/call", {"name": "jlc_search", "arguments": {"query": "capacitor"}}, ip)
                assert response.status_code == 200
                assert response.json()["result"]["structuredContent"] == reply
            response = await rpc(client, "tools/call", {"name": "digikey_get_part", "arguments": {"mpn": "SECRET"}}, "203.0.113.1")
            assert response.json()["result"]["structuredContent"] == {"number": "SECRET"}
            for tool, args in (("jlc_search", {"query": "SECRET", "Part_Numbers": ["LM358P"]}),
                               ("part_lifecycle", {"Part_Numbers": ["LM358P"]})):
                response = await rpc(client, "tools/call", {"name": tool, "arguments": args}, "203.0.113.1")
                assert response.json()["result"]["isError"]
            await rpc(client, "tools/call", {"name": "jlc_search", "arguments": {"query": []}}, "203.0.113.1")
            await rpc(client, "tools/call", {"name": "SECRET", "arguments": {"Part_Numbers": "SECRET", "lm358p": "SECRET"}}, "203.0.113.1")
    await log.flush()
    rows = read_rows(tmp_path)
    assert rows[0]["app"] == "other" and rows[0]["ms"] == 0
    assert stats.usage.summary()["days"][0]["tool_apps"]["jlc_search"]["backplane"]["calls"] == 1
    assert all(row["platform"] for row in rows[:15]) and not any(row["platform"] for row in rows[15:])
    assert rows[0]["reason"] == "no_results_words"
    assert stats.usage.summary()["days"][0]["reasons"] == {"jlc_search": {"no_results_words": 38}}
    assert stats.usage.summary()["days"][0]["popular_terms"] == {"capacitor": 38}
    assert len(stats.usage._terms["capacitor"][1]) == 10  # platform + one /48 + eight IPv4s
    assert rows[-5]["shape"]["args"] == ["part_number"]
    assert rows[-4]["outcome"] == "bad_request" and rows[-4]["shape"]["args"] == ["Part_Numbers", "query"]
    assert rows[-4]["bad_request_reason"] == "arg:unknown_argument:unexpected_keyword_argument"
    assert rows[-3]["outcome"] == "bad_request" and rows[-3]["shape"]["args"] == ["Part_Numbers"]
    assert rows[-3]["bad_request_reason"] == "arg:parts:missing_argument"
    assert rows[-2]["bad_request_reason"] == "arg:query:string_type"
    assert rows[-1]["tool"] == "unknown" and rows[-1]["shape"] == {"args": ["Part_Numbers", "unknown_argument"]}
    assert rows[-1]["bad_request_reason"] == "unknown_tool"
    assert all(text not in json.dumps(rows) for text in ("SECRET", "LM358P", "lm358p", "203.0.113.1"))
    assert stats.usage.summary()["days"][0]["bad_request_reasons"] == {
        "jlc_search": {"arg:unknown_argument:unexpected_keyword_argument": 1, "arg:query:string_type": 1},
        "part_lifecycle": {"arg:parts:missing_argument": 1}, "unknown": {"unknown_tool": 1}}
    assert "Part_Numbers" not in json.dumps(stats.usage.summary())
    assert failed(tmp_path)["queries"] == [{"tool": "jlc_search", "reason": "no_results_words", "text": "capacitor", "count": 38}]


@pytest.mark.parametrize("full", [False, True], ids=["rate", "clients"])
async def test_http_refusal_rows_no_tool_parse(tmp_path, full, monkeypatch):
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    await log.open(tmp_path)
    monkeypatch.setattr(call_log, "recorder", log)
    ranges = PlatformRanges({"test": [ipaddress.ip_network("198.51.100.0/24")]})
    reached = []

    async def downstream(scope, receive, send):
        reached.append(scope)
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    app = server.RateLimitMiddleware(downstream, requests_per_minute=1, platform_per_minute=1,
                                     platform_addresses=ranges, clock=clock, wall_clock=clock)
    if full:
        app.MAX_TRACKED_IPS = 0
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as client:
        for ip in ("198.51.100.1", "203.0.113.1"):
            if not full:
                assert (await client.post("/mcp", content="not json", headers={"X-Forwarded-For": ip})).status_code == 204
            response = await client.post("/mcp", content="not json", headers={"X-Forwarded-For": ip})
            assert response.status_code == 429 and response.json()["retry_after"] == 60
    clock.advance(60)
    await log.flush()
    reason = "too_many_clients" if full else "per_ip_rate_limit"
    assert read_rows(tmp_path) == [{"t": "2026-10-17T21:15:00Z", "refused": reason, "platform": platform, "count": 1}
                                  for platform in (True, False)]
    assert len(reached) == (0 if full else 2)


async def test_recording_failure_keeps_reply_and_recovers(monkeypatch, caplog):
    context = SimpleNamespace(message=SimpleNamespace(name="jlc_search", arguments={"query": "secret"}))
    reply = SimpleNamespace(structured_content={"results": [], "total": 0})

    async def next_call(context):
        return reply

    original = stats.usage.record_call

    def broken(*args, **kwargs):
        raise ValueError("secret")

    monkeypatch.setattr(stats.usage, "record_call", broken)
    middleware = server.UsageStatsMiddleware()
    for _ in range(2):
        assert await middleware.on_call_tool(context, next_call) is reply
    assert sum("call counts failed" in m for m in caplog.messages) == 1
    monkeypatch.setattr(stats.usage, "record_call", original)
    assert await middleware.on_call_tool(context, next_call) is reply
    monkeypatch.setattr(stats.usage, "record_call", broken)
    assert await middleware.on_call_tool(context, next_call) is reply
    assert sum("call counts failed" in m for m in caplog.messages) == 2
    assert "secret" not in caplog.text


async def test_lifespan_catalog_job_and_shutdown_flush(tmp_path, monkeypatch):
    log = call_log.CallLog(clock=Clock())
    monkeypatch.setattr(call_log, "recorder", log)
    monkeypatch.setattr(server, "CALL_LOG_DIR", str(tmp_path))
    thread = threading.get_ident()
    jobs = []
    release, completed = asyncio.Event(), asyncio.Event()
    original = server._load_call_catalog

    async def delayed_catalog(*args):
        await release.wait()
        await original(*args)
        completed.set()

    def load(db):
        assert threading.get_ident() != thread
        jobs.append(db)
        return catalog()

    monkeypatch.setattr(call_log, "load_catalog", load)
    monkeypatch.setattr(server, "_load_call_catalog", delayed_catalog)
    async with Client(server.mcp) as client:
        try:
            await client.call_tool("get_design_rules", {"topic": "zzzznomatch"})
            assert not jobs  # the unrelated call completed while the catalog job was held
            release.set()
            await completed.wait()
            assert len(jobs) == 1 and log.catalog.packages == {"0603", "SOT-23"}
            assert log._rows and not (tmp_path / f"calls-{DATE}.jsonl").exists()
        finally:
            release.set()
    assert read_rows(tmp_path)[0]["tool"] == "get_design_rules"
    assert failed(tmp_path)["queries"][0]["text"] == "zzzznomatch"


async def test_minute_task_flushes_call_log(tmp_path, monkeypatch):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    record(log)
    monkeypatch.setattr(call_log, "recorder", log)
    monkeypatch.setattr(server, "_distributor_quotas", {})
    original_flush = log.flush
    flushed = asyncio.Event()
    ticks = asyncio.Queue()
    ticks.put_nowait(None)

    async def sleep(seconds):
        assert seconds == 60
        await ticks.get()

    async def flush():
        await original_flush()
        flushed.set()

    monkeypatch.setattr(server, "asyncio", SimpleNamespace(**(vars(asyncio) | {"sleep": sleep})))
    monkeypatch.setattr(log, "flush", flush)
    task = asyncio.create_task(server._every_minute())
    try:
        await flushed.wait()
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert len(read_rows(tmp_path)) == 1 and failed(tmp_path)["queries"][0]["count"] == 1


async def test_stock_check_note_resolves_names_without_changing_reply(tmp_path, monkeypatch):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    log.catalog = catalog()
    monkeypatch.setattr(call_log, "recorder", log)
    reply = {"results": [], "total": 0}

    async def search(**kwargs):
        return dict(reply)

    monkeypatch.setattr(server, "_client", SimpleNamespace(search=search, get_subcategory_id_by_name=lambda name: 2))
    monkeypatch.setattr(server, "_categories", [{"id": 1}])
    stats.usage.tool_params = {"jlc_stock_check": {"query", "subcategory_name"}}
    args = {"query": "words", "subcategory_name": "fuzzy catalog alias"}
    context = SimpleNamespace(message=SimpleNamespace(name="jlc_stock_check", arguments=args))

    async def next_call(context):
        return SimpleNamespace(structured_content=await server.jlc_stock_check(**args))

    result = await server.UsageStatsMiddleware().on_call_tool(context, next_call)
    assert result.structured_content == reply
    await log.flush()
    row = read_rows(tmp_path)[0]
    assert row["reason"] == "no_results_filtered"
    assert row["shape"]["subcategory"] == "Chip Resistors" and row["shape"]["category"] == "Resistors"


def test_usage_report(tmp_path, capsys):
    usage_report = SimpleNamespace(**runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts" / "usage_report.py")))

    rows = [{"tool": "jlc_search", "outcome": "ok", "app": "app", "ms": i, "reason": None} for i in range(1, 101)]
    rows += [{"tool": "jlc_search", "outcome": "bad_request", "app": None, "ms": 1,
              "bad_request_reason": "too_long"},
             {"tool": "part_lifecycle", "outcome": "bad_request", "ms": 1,
              "bad_request_reason": "arg:parts:missing_argument", "shape": {"args": ["Part_Numbers"]}},
             {"refused": "per_ip_rate_limit"}]
    with gzip.open(tmp_path / "calls-2026-10-16.jsonl.gz", "wt", encoding="utf-8") as out:
        out.write("\n".join(json.dumps(row) for row in rows))
    (tmp_path / f"calls-{DATE}.jsonl").write_text(json.dumps({"tool": "board_search", "outcome": "not_found",
        "app": "app", "ms": 10, "reason": "no_results", "shape": {"args": ["Search_Term", "unknown_argument"]}}) + "\n", encoding="utf-8")
    (tmp_path / f"failed-{DATE}.json").write_text(json.dumps({"date": DATE, "dropped": 0, "queries": [
        {"tool": "board_search", "reason": "no_results", "text": "weird search", "count": 9}]}), encoding="utf-8")
    assert usage_report.main(["--dir", str(tmp_path), "--days", "2"], today=dt.date(2026, 10, 17)) == 0
    text = capsys.readouterr().out
    for expected in ("jlc_search / ok: 100", "app / jlc_search: 100", "jlc_search: 50 / 95 / 99",
                     "jlc_search / too_long: 1", "board_search / no_results: 1", "per_ip_rate_limit: 1", '9 "weird search"',
                     "part_lifecycle / bad_request: 1", "part_lifecycle / arg:parts:missing_argument: 1"):
        assert expected in text
    assert usage_report.main(["--dir", str(tmp_path), "--date", DATE]) == 0
    assert "jlc_search" not in capsys.readouterr().out
    assert usage_report.main(["--dir", str(tmp_path)], today=dt.date(2026, 10, 17)) == 0
    assert "board_search" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        usage_report.main(["--days", "0"])
