"""Logging limits: bounded work, private call rows, refusal aggregation and reliable retention."""

import asyncio
import datetime as dt
import gzip
import json
import logging
import os
import runpy
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastmcp import Client

from pcbparts_mcp import call_log, config, file_logging, server, stats
from test_call_log import DATE, catalog, failed, read_rows, record
from test_usage_stats import Clock


async def test_refusals_one_row_per_finished_minute(tmp_path):
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    await log.open(tmp_path)
    for _ in range(2000):
        log.refusal("per_ip_rate_limit", True)
    await log.flush()
    assert not list(tmp_path.glob("calls-*"))  # a second flush in this minute must not duplicate it
    for _ in range(3):
        log.refusal("per_ip_rate_limit", True)
    log.refusal("per_ip_rate_limit", False)
    log.refusal("too_many_clients", False)
    clock.advance(60)
    await log.flush()
    assert read_rows(tmp_path) == [
        {"t": "2026-10-17T21:15:00Z", "refused": "per_ip_rate_limit", "platform": True, "count": 2003},
        {"t": "2026-10-17T21:15:00Z", "refused": "per_ip_rate_limit", "platform": False, "count": 1},
        {"t": "2026-10-17T21:15:00Z", "refused": "too_many_clients", "platform": False, "count": 1}]
    report = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/usage_report.py"))["report"]
    assert "per_ip_rate_limit: 2004" in report(tmp_path, [DATE])


def test_daily_budget_setting_and_buffer_default(monkeypatch):
    monkeypatch.delenv("CALL_LOG_MAX_ROWS", raising=False)
    assert runpy.run_path(config.__file__)["CALL_LOG_MAX_ROWS"] == 1_000_000
    monkeypatch.setenv("CALL_LOG_MAX_ROWS", "-1")
    assert runpy.run_path(config.__file__)["CALL_LOG_MAX_ROWS"] == 1
    monkeypatch.setenv("CALL_LOG_MAX_ROWS", "bad")
    assert runpy.run_path(config.__file__)["CALL_LOG_MAX_ROWS"] == 1_000_000
    assert call_log.CallLog().row_cap == 20_000


async def test_daily_budget_counts_across_flushes_restart_and_rollover(tmp_path, caplog):
    clock = Clock()
    log = call_log.CallLog(clock=clock, max_rows=2)
    await log.open(tmp_path)
    for _ in range(2):
        record(log)
        await log.flush()
    for _ in range(3):
        record(log)
        await log.flush()
    assert len(read_rows(tmp_path)) == 2 and log.dropped_rows == 3
    assert failed(tmp_path)["queries"][0]["count"] == 5
    assert sum("WARNING" == r.levelname and "excess rows dropped" in r.message for r in caplog.records) == 1
    again = call_log.CallLog(clock=clock, max_rows=2)
    await again.open(tmp_path)
    record(again)
    await again.flush()
    assert len(read_rows(tmp_path)) == 2 and again.dropped_rows == 1
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.call_log"):
        clock.advance(86400)
        await log.flush()  # even an idle day reports the final loss
    assert any(DATE in m and "3 rows dropped" in m for m in caplog.messages)
    record(log)
    await log.flush()
    assert len(read_rows(tmp_path, "2026-10-18")) == 1


def app_record(log, name, caller=None, platform=False):
    log.record("jlc_search", "ok", None, None, 1, name, platform, {}, {}, {}, set(), caller=caller)


async def test_app_gate_at_flush_and_daily_reset(tmp_path):
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    await log.open(tmp_path)
    for i in range(9):
        app_record(log, "niche-name", f"203.0.113.{i}")
    await log.flush()
    assert {r["app"] for r in read_rows(tmp_path)} == {"other"}
    app_record(log, "niche-name", "203.0.113.9")
    for i in range(10):
        app_record(log, "shared-app", f"203.0.113.{i}")
    app_record(log, "203.0.113.99", "203.0.113.99")
    app_record(log, "b3c68182-7b72-40d1-8aa1-f7216eabc123", "203.0.113.1")
    app_record(log, None)
    await log.flush()
    rows = read_rows(tmp_path)
    assert rows[9]["app"] == "niche-name"
    assert {r["app"] for r in rows[10:20]} == {"shared-app"}
    assert [r["app"] for r in rows[-3:]] == ["other", "other", None]
    clock.advance(86400)
    app_record(log, "shared-app", "203.0.113.1")
    await log.flush()
    assert read_rows(tmp_path, "2026-10-18")[0]["app"] == "other"


async def test_well_known_names_exact_case_insensitive(tmp_path):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    names = ["codex-mcp-client", "claude-code", "backplane-check", "mcp", "Anthropic/ClaudeAI",
             "claude-ai", "opencode", "antigravity-client", "openai-mcp (Responses API)", "Cursor"]
    for name in names:
        app_record(log, name.upper())
    app_record(log, "Cursor-suffix")
    app_record(log, "<Cursor>")
    await log.flush()
    assert [r["app"] for r in read_rows(tmp_path)] == names + ["other", "Cursor"]


async def test_app_threshold_platform_ipv6_and_caps(tmp_path, monkeypatch):
    monkeypatch.setattr(call_log, "MAX_TRACKED_APPS", 2)
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    for i in range(20):
        app_record(log, "hosted", f"198.51.100.{i}", True)
        app_record(log, "ipv6", f"2001:db8:1:{i:x}::1")
        app_record(log, "overflow", f"203.0.113.{i}")
    await log.flush()
    assert {r["app"] for r in read_rows(tmp_path)} == {"other"}
    for i in range(9):
        app_record(log, "hosted", f"203.0.113.{i}")
        app_record(log, "ipv6", f"2001:db8:{i+2:x}::1")
    await log.flush()
    assert {r["app"] for r in read_rows(tmp_path)[-2:]} == {"hosted", "ipv6"}
    for _, seen in log._app_days.values():
        assert len(seen) <= 2
        assert all(len(callers) <= 10 and all(isinstance(c, bytes) for c in callers) for callers in seen.values())


def test_popular_terms_ipv6_48():
    usage = stats.UsageStats(clock=Clock())
    for i in range(20):
        usage.record_terms("jlc_search", "ok", "mosfet", f"2001:db8:1:{i:x}::1")
    assert usage.summary()["days"][0]["popular_terms"] == {}
    for i in range(9):
        usage.record_terms("jlc_search", "ok", "mosfet", f"2001:db8:{i+2:x}::1")
    assert usage.summary()["days"][0]["popular_terms"] == {"mosfet": 29}


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits")
async def test_private_modes_existing_new_gzip_and_temporary(tmp_path, monkeypatch):
    directory = tmp_path / "rows"
    directory.mkdir(mode=0o755)
    for filename, text in [(f"calls-{DATE}.jsonl", "{}\n"), (f"failed-{DATE}.json", json.dumps({"date": DATE, "queries": []})),
                           ("calls-2026-10-16.jsonl.gz", ""), ("failed-2026-10-16.json.tmp", "private")]:
        path = directory / filename
        path.write_text(text, encoding="utf-8")
        path.chmod(0o644)
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    await log.open(directory)
    assert directory.stat().st_mode & 0o777 == 0o700
    assert all(p.stat().st_mode & 0o777 == 0o600 for p in directory.iterdir())
    original = call_log.os.replace

    def replace(src, dst):
        assert Path(src).stat().st_mode & 0o777 == 0o600
        original(src, dst)
        assert Path(dst).stat().st_mode & 0o777 == 0o600

    monkeypatch.setattr(call_log.os, "replace", replace)
    record(log)
    await log.flush()
    clock.advance(86400)
    await log.flush()
    assert all(p.stat().st_mode & 0o777 == 0o600 for p in directory.iterdir())


def test_stuck_exit_flushes_rows_and_failed_counts(tmp_path, monkeypatch, caplog):
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    asyncio.run(log.open(tmp_path))
    record(log, outcome="failed", reason="exception")
    log.refusal("per_ip_rate_limit", False)
    usage = stats.UsageStats(clock=clock)
    usage.open(tmp_path / "usage.json")
    usage.record_call("jlc_search", "failed", 1, reason="exception")
    monkeypatch.setattr(call_log, "recorder", log)
    monkeypatch.setattr(stats, "usage", usage)
    monkeypatch.setattr(server.database_pressure, "stalled_seconds", lambda: server.DB_STUCK_WAIT_SECONDS + 1)
    exits = []

    class Writer:
        def __init__(self, *, target, daemon, **kwargs):
            assert daemon
            self.target = target

        def start(self):
            self.target()  # deterministic completion, no production join deadline

        def join(self, timeout):
            assert timeout == server.EXIT_FLUSH_SECONDS

    monkeypatch.setattr(server, "threading", SimpleNamespace(Thread=Writer))

    def exited(code):
        assert len(read_rows(tmp_path)) == 2
        assert failed(tmp_path)["queries"][0]["count"] == 1
        assert json.loads(usage.path.read_text(encoding="utf-8"))["days"][DATE]["tools"]["jlc_search"]["failed"] == 1
        assert not usage._failed_minutes
        exits.append(code)

    monkeypatch.setattr(server, "_exit_process", exited)
    server._exit_if_stuck(server.STUCK_CHECKS_BEFORE_EXIT - 1)
    assert exits == [1]


@pytest.mark.parametrize("tool", ["jlc_get_parts", "part_lifecycle"], ids=["jlc", "life"])
def test_mixed_batch_error_rows(tool):
    args = {"parts": ["OK123", "C404", {"mpn": "BROKEN123", "manufacturer": "Maker"}, "bad", "LIMIT123"]}
    content = {"results": [{"mpn": "OK123", "status": "active"}, {"error": "Part C404 not found"},
                           {"error": "Database not available"}, {"error": "Invalid part: bad input"},
                           {"retry_after": 60}], "counts": {"found": 1, "error": 3}, "total": 5}
    if tool == "part_lifecycle":
        content.pop("counts")
        content["status_counts"] = {"active": 1, "unknown": 4}
    assert list(call_log.failed_texts(tool, "ok", None, args, content)) == [
        ("row_not_found", "C404"), ("row_failed", "BROKEN123 | Maker")]


def test_mouser_mixed_lookup_failed():
    reply = {"results": [{"mfr_part_number": "OK123", "requested": "OK123"}], "total": 1,
             "not_found": ["MISS123", "DNP"], "lookup_failed": ["FAIL123"],
             "not_checked": ["LIMIT123"], "not_sent": {"DNP": "placeholder"}}
    assert list(call_log.failed_texts("mouser_get_part", "ok", None, {}, reply)) == [
        ("row_not_found", "MISS123"), ("row_lookup_failed", "FAIL123")]


async def test_rotation_prunes_before_compression_and_continues(tmp_path, monkeypatch):
    for date in ("2026-10-01", "2026-10-15", "2026-10-16"):
        (tmp_path / f"calls-{date}.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "failed-2026-10-01.json").write_text("{}", encoding="utf-8")
    original = gzip.GzipFile

    def gzip_failure(*args, **kwargs):
        assert not (tmp_path / "calls-2026-10-01.jsonl").exists()
        assert not (tmp_path / "failed-2026-10-01.json").exists()
        if "2026-10-15" in str(kwargs.get("fileobj").name):
            raise OSError("disk full")
        return original(*args, **kwargs)

    monkeypatch.setattr(gzip, "GzipFile", gzip_failure)
    log = call_log.CallLog(clock=Clock(), call_days=3)
    await log.open(tmp_path)
    assert "rotation" in log._errors
    assert (tmp_path / "calls-2026-10-15.jsonl").exists()
    assert (tmp_path / "calls-2026-10-16.jsonl.gz").exists()


@pytest.mark.parametrize("tool", ["jlc_search", "jlc_stock_check"], ids=["search", "stock"])
def test_category_ids_win_over_conflicting_names(tool):
    cat = call_log.ShapeCatalog({1: "Resistors", 3: "Capacitors"},
        {2: ("Chip Resistors", "Resistors"), 4: ("Ceramic Capacitors", "Capacitors")},
        {"resistors": "Resistors", "capacitors": "Capacitors"},
        {"chip resistors": "Chip Resistors", "ceramic capacitors": "Ceramic Capacitors"})
    args = {"category_id": 1, "category_name": "Capacitors", "subcategory_id": 2,
            "subcategory_name": "Ceramic Capacitors"}
    shape = cat.shape(tool, args, {}, {}, set(args))
    assert shape["category"] == "Resistors" and shape["subcategory"] == "Chip Resistors"


async def test_startup_info_on_and_off(tmp_path, caplog):
    log = call_log.CallLog(clock=Clock(), call_days=12, failed_days=3)
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.call_log"):
        await log.open("")
        await log.open(tmp_path)
    assert "Call log: off (CALL_LOG_DIR unset)" in caplog.messages
    assert f"Call log: kept in {tmp_path} (rows 12 days, failed searches 3 days)" in caplog.messages


@pytest.mark.parametrize("tool", ["jlc_get_parts", "part_lifecycle"], ids=["jlc", "life"])
async def test_rejected_huge_batch_bounded_recording(tmp_path, monkeypatch, tool):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    monkeypatch.setattr(call_log, "recorder", log)
    monkeypatch.setattr(server, "time", SimpleNamespace(monotonic=lambda: 10))
    visited = []
    original = call_log._part

    def part(item):
        visited.append(item)
        return original(item)

    monkeypatch.setattr(call_log, "_part", part)
    reply = SimpleNamespace(structured_content={"error": "Too many parts (max 50, got 100000)", "results": [], "total": 0})
    args = {"parts": ["C1"] * 100000}
    context = SimpleNamespace(message=SimpleNamespace(name=tool, arguments=args))
    server.UsageStatsMiddleware()._record(context, 10, result=reply)
    assert len(visited) <= 50
    assert log._rows[-1]["shape"]["batch"] == 100000
    args["parts"] = json.dumps(args["parts"])

    def no_parse(*args, **kwargs):
        raise AssertionError("reparsed rejected batch")

    monkeypatch.setattr(call_log.json, "loads", no_parse)
    visited.clear()
    server.UsageStatsMiddleware()._record(context, 10, result=reply)
    assert len(log._rows) == 2 and len(visited) <= 50
    assert log._rows[-1]["shape"]["batch"] == 100000
    assert not log._failed and not log._errors


def test_closed_day_json_cache_and_invalidation(tmp_path, monkeypatch):
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    usage.open(tmp_path / "usage.json")
    for i in range(3):
        usage.record_call("jlc_search", "ok", 2, app="app")
        clock.advance(86400)
    usage.record_call("jlc_search", "ok", 2, app="app")
    usage.save()
    assert usage.path.read_text(encoding="utf-8") == json.dumps({"days": usage._days}, sort_keys=True)
    original = stats.json.dumps
    encoded = []

    def dumps(value, **kwargs):
        encoded.append(value)
        return original(value, **kwargs)

    monkeypatch.setattr(stats.json, "dumps", dumps)
    usage.record_call("jlc_search", "ok", 3)
    usage.save()
    today = usage._now().date().isoformat()
    # Neither the year nor unchanged closed days may be encoded again.
    assert not any(isinstance(value, dict) and ("days" in value or any(value is day for date, day in usage._days.items() if date != today))
                   for value in encoded)
    late = dt.datetime.fromisoformat(DATE).replace(tzinfo=dt.timezone.utc)
    usage.record_db_wait(1, started_at=late)
    usage.save()
    assert usage.path.read_text(encoding="utf-8") == original({"days": usage._days}, sort_keys=True)
    clock.advance(30 * 86400)
    usage.save()
    assert usage.path.read_text(encoding="utf-8") == original({"days": usage._days}, sort_keys=True)
    assert all(day["tool_apps"] is None for day in usage._days.values())


async def test_row_timestamp_cached_per_second(tmp_path, monkeypatch):
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    formats = []
    original = dt.datetime

    class DateTime(original):
        def strftime(self, fmt):
            formats.append(fmt)
            return super().strftime(fmt)

    monkeypatch.setattr(call_log.dt, "datetime", DateTime)
    await log.open(tmp_path)
    for _ in range(20):
        record(log, outcome="ok", reason=None)
    assert len(formats) == 1
    clock.advance(1)
    record(log, outcome="ok", reason=None)
    assert len(formats) == 2 and log._rows[-1]["t"] == "2026-10-17T21:15:01Z"


async def test_catalog_does_not_delay_readiness(tmp_path, monkeypatch):
    log = call_log.CallLog(clock=Clock())
    monkeypatch.setattr(call_log, "recorder", log)
    monkeypatch.setattr(server, "CALL_LOG_DIR", str(tmp_path))
    ready = asyncio.Event()
    before_ready = []

    def load(db):
        before_ready.append(ready.is_set())
        # A fake slow load: fail immediately if lifespan waits for us before yielding.
        assert ready.is_set(), "catalog scan delayed readiness"
        return catalog()

    # Hold the worker until the client is ready without wall-clock assertions.
    original = server.run_db

    async def run(pool, fn, *args, **kwargs):
        if fn is call_log.load_catalog:
            await ready.wait()
        return await original(pool, fn, *args, **kwargs)

    monkeypatch.setattr(call_log, "load_catalog", load)
    monkeypatch.setattr(server, "run_db", run)
    async with Client(server.mcp):
        ready.set()
    assert before_ready == [True] and log.catalog.packages == {"0603", "SOT-23"}


async def test_minute_task_prunes_application_logs_hourly(monkeypatch):
    ticks = asyncio.Queue()
    for _ in range(60):
        ticks.put_nowait(None)
    pruned = asyncio.Event()
    loop = asyncio.get_running_loop()
    completed = asyncio.Queue()
    original = server._persist_usage
    checks = []
    stats_pruned = []

    async def sleep(seconds):
        assert seconds == 60
        if checks:
            await completed.get()
        await ticks.get()

    async def persist(**kwargs):
        try:
            await original(**kwargs)
        finally:
            completed.put_nowait(None)

    def prune():
        assert len(checks) == 60
        loop.call_soon_threadsafe(pruned.set)

    monkeypatch.setattr(server, "asyncio", SimpleNamespace(**(vars(asyncio) | {"sleep": sleep})))
    monkeypatch.setattr(server, "_persist_usage", persist)
    monkeypatch.setattr(file_logging, "prune_file_logs", prune)
    monkeypatch.setattr(stats.usage, "prune", lambda: stats_pruned.append(True))
    monkeypatch.setattr(server, "_distributor_quotas", {})
    monkeypatch.setattr(server, "_exit_if_stuck", lambda count: checks.append(count))
    task = asyncio.create_task(server._every_minute())
    try:
        await pruned.wait()
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert stats_pruned == [True]


def test_stuck_flush_has_bounded_wait(monkeypatch):
    waits, exits = [], []

    class StuckWriter:
        def __init__(self, *, target, daemon, **kwargs):
            assert daemon

        def start(self):
            pass

        def join(self, timeout):
            waits.append(timeout)

        def is_alive(self):
            return True

    monkeypatch.setattr(server.threading, "Thread", StuckWriter)
    monkeypatch.setattr(server.database_pressure, "stalled_seconds", lambda: server.DB_STUCK_WAIT_SECONDS + 1)
    monkeypatch.setattr(server, "_exit_process", exits.append)
    server._exit_if_stuck(server.STUCK_CHECKS_BEFORE_EXIT - 1)
    assert len(waits) == 1 and 0 < waits[0] <= 5 and exits == [1]


@pytest.mark.parametrize("tool", ["jlc_get_parts", "part_lifecycle"], ids=["jlc", "life"])
async def test_real_rejected_json_batch_notes_avoid_reparse(tmp_path, monkeypatch, tool):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    monkeypatch.setattr(server, "_mouser_client", object())  # only the local input check is reached
    args = {"parts": json.dumps(["C1"] * 100000)}
    token = stats.call_notes.set({})
    try:
        reply = await getattr(server, tool)(**args)
        notes = stats.call_notes.get()
        assert reply == {"error": "Too many parts (max 50, got 100000)", "results": [], "total": 0}
        assert notes["batch_count"] == 100000 and len(notes["batch_items"]) == 50

        def no_parse(*args, **kwargs):
            raise AssertionError("already parsed by the tool")

        monkeypatch.setattr(call_log.json, "loads", no_parse)
        log.record(tool, "bad_request", None, "too_many", 1, None, False, args, reply, notes, {"parts"})
        assert log._rows[0]["shape"] == {"args": ["parts"], "batch": 100000, "input": {"lcsc": 50, "mpn": 0}}
        assert not log._failed and not log._errors
    finally:
        stats.call_notes.reset(token)
