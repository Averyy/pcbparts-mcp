"""Startup and exit paths: blocked stderr, failed log and stats startup, app names over HTTP and sessions."""

import json
import os
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastmcp import Client, FastMCP
from mcp.types import Implementation

from pcbparts_mcp import call_log, file_logging, server, stats
from test_call_log import DATE, read_rows
from test_file_logging import logs
from test_usage_stats import Clock


def test_stuck_exit_survives_blocked_stderr(monkeypatch):
    events = []
    active = ["watchdog"]

    class WouldBlock(BaseException):
        pass

    def write(fd, data):
        assert fd == 2 and b"exiting so Docker restarts" in data
        events.append(("write", active[0]))
        raise WouldBlock  # model a full pipe without blocking an actual test thread

    class Writer:
        def __init__(self, *, target, daemon, **kwargs):
            assert daemon
            self.target = target

        def start(self):
            pass

        def join(self, timeout):
            assert timeout == server.EXIT_FLUSH_SECONDS
            active[0] = "worker"
            try:
                self.target()
            except WouldBlock:
                events.append(("deadline", timeout))
            finally:
                active[0] = "watchdog"

    monkeypatch.setattr(server, "threading", SimpleNamespace(Thread=Writer))
    monkeypatch.setattr(server.os, "write", write)
    monkeypatch.setattr(server.database_pressure, "stalled_seconds", lambda: server.DB_STUCK_WAIT_SECONDS + 1)
    monkeypatch.setattr(server, "_exit_process", lambda code: events.append(("exit", code)))
    try:
        server._exit_if_stuck(server.STUCK_CHECKS_BEFORE_EXIT - 1)
    except WouldBlock:
        pass
    assert events == [("write", "worker"), ("deadline", server.EXIT_FLUSH_SECONDS), ("exit", 1)]


@pytest.mark.parametrize("name,expected", [("<Cursor>", "Cursor"), ("Cursor!", "Cursor"), ("Cur\tsor", "Cursor"),
                                         ("Cursor-suffix", "other")], ids=["brackets", "bang", "tab", "suffix"])
async def test_cleaned_app_agrees_over_http_and_session(tmp_path, monkeypatch, name, expected):
    clock = Clock()
    log = call_log.CallLog(clock=clock)
    await log.open(tmp_path)
    monkeypatch.setattr(call_log, "recorder", log)
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    monkeypatch.setattr(server, "_apps_by_address", server.AppsByAddress(clock=clock))
    monkeypatch.setattr(server, "time", SimpleNamespace(monotonic=lambda: 10))
    mcp = FastMCP("app-gate")
    reply = {"results": [], "total": 0}

    @mcp.tool
    async def jlc_search(query: str):
        return reply

    mcp.add_middleware(server.UsageStatsMiddleware())
    app = mcp.http_app(stateless_http=True, json_response=True)

    async def rpc(client, method, params):
        response = await client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                                     headers={"Accept": "application/json, text/event-stream"})
        assert response.status_code == 200
        return response.json()["result"]

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as client:
            await rpc(client, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                             "clientInfo": {"name": name, "version": "1"}})
            assert server._apps_by_address.app_for("127.0.0.1") == stats.clean_app_name(name)
            result = await rpc(client, "tools/call", {"name": "jlc_search", "arguments": {"query": "capacitor"}})
            assert result["structuredContent"] == reply
    async with Client(mcp, client_info=Implementation(name=name, version="1")) as client:
        result = await client.call_tool("jlc_search", {"query": "capacitor"})
        assert result.structured_content == reply
    await log.flush()
    assert [row["app"] for row in read_rows(tmp_path)] == [expected, expected]


@pytest.mark.parametrize("failure", ["unlink", "open"], ids=["unlink", "open"])
def test_file_retention_survives_failed_startup(logs, tmp_path, monkeypatch, failure):
    configure, _, clock = logs
    source = tmp_path / "application.log"
    source.write_text("private active log", encoding="utf-8")
    os.utime(source, (clock[0],) * 2)
    expired = tmp_path / "application.log.2026-01-01"
    expired.write_text("private expired log", encoding="utf-8")
    attempts = []
    unlink = Path.unlink

    def fail_once(path, *args, **kwargs):
        if path == expired and not attempts:
            attempts.append(path)
            raise PermissionError("transient unlink failure")
        return unlink(path, *args, **kwargs)

    def no_writer(*args, **kwargs):
        raise PermissionError("transient open failure")

    with monkeypatch.context() as patch:
        if failure == "unlink":
            patch.setattr(Path, "unlink", fail_once)
        else:
            patch.setattr(file_logging._DailyFileHandler, "_open", no_writer)
        assert configure(source) is None
        assert expired.exists()
    clock[0] += 3600
    file_logging.prune_file_logs()
    assert not expired.exists(), "startup failure permanently suppressed retention"
    assert source.exists(), "recent active file was deleted too early"
    clock[0] += 9 * 86400
    file_logging.prune_file_logs()
    assert not any("private" in p.read_text(encoding="utf-8") for p in tmp_path.iterdir())


@pytest.mark.parametrize("failure", ["chmod", "rename"], ids=["chmod", "rename"])
@pytest.mark.parametrize("age", [0, 31], ids=["recent", "expired"])
async def test_stats_retention_retries_set_aside(tmp_path, monkeypatch, failure, age):
    clock = Clock()
    source = tmp_path / "usage_stats.json"
    aside = source.with_name(source.name + ".corrupt")
    original = b"{unreadable private counts"
    source.write_bytes(original)
    modified = clock() - age * 86400
    os.utime(source, (modified,) * 2)
    aside.write_text("previous private backup", encoding="utf-8")
    os.utime(aside, (clock(),) * 2)
    chmod, replace = Path.chmod, os.replace

    def denied_chmod(path, *args, **kwargs):
        if path == source:
            raise PermissionError("transient chmod failure")
        return chmod(path, *args, **kwargs)

    def denied_rename(src, dst):
        if Path(src) == source:
            raise PermissionError("transient rename failure")
        return replace(src, dst)

    usage = stats.UsageStats(clock=clock)
    with monkeypatch.context() as patch:
        if failure == "chmod":
            patch.setattr(Path, "chmod", denied_chmod)
        else:
            patch.setattr(stats.os, "replace", denied_rename)
        usage.open(source)
        usage.record_start()
        usage.save()
        await usage.save_async()
        assert source.read_bytes() == original
        assert usage.summary()["kept_across_restarts"] is False
        # A backup can expire while the original still cannot be moved aside.
        os.utime(aside, (clock() - 31 * 86400,) * 2)
        usage.prune()
        assert source.read_bytes() == original
        assert not aside.exists(), "disabled stats writes also disabled backup retention"
    clock.advance(3600)
    usage.prune()
    assert not source.exists(), "unreadable original was never retried after filesystem recovery"
    if age:
        assert not aside.exists(), "expired original survived as a corrupt backup"
    else:
        assert aside.read_bytes() == original and aside.stat().st_mtime == modified
    await usage.save_async()
    assert json.loads(source.read_text(encoding="utf-8"))["days"][DATE]["restarts"] == 1
    assert usage.summary()["kept_across_restarts"] is True
    clock.advance(31 * 86400)
    usage.prune()
    assert not aside.exists()
