"""Persistent application logs: fake UTC clocks, local files, no server or network."""

import datetime
import io
import logging
import os
import runpy
import subprocess
import sys

import pytest

from pcbparts_mcp import file_logging

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 20, 13, 5, 1, tzinfo=UTC).timestamp()


@pytest.fixture
def logs(monkeypatch):
    loggers = [logging.getLogger(), logging.getLogger("pcbparts_mcp"),
               logging.getLogger("uvicorn"), logging.getLogger("uvicorn.error"),
               logging.getLogger("uvicorn.access"), logging.getLogger("fastmcp"),
               logging.getLogger("thirdparty")]
    saved = [(item, list(item.handlers), item.level, item.propagate, item.disabled) for item in loggers]
    for item in loggers:
        item.handlers = []
        item.setLevel(logging.NOTSET)
        item.propagate = True
        item.disabled = False
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("pcbparts_mcp").setLevel(logging.INFO)
    output = io.StringIO()
    console = logging.StreamHandler(output)
    logging.getLogger().addHandler(console)
    for name in ("uvicorn", "uvicorn.access", "fastmcp"):
        item = logging.getLogger(name)
        item.propagate = False
        item.setLevel(logging.INFO)
        item.addHandler(console)
    clock = [NOW]
    monkeypatch.setattr(file_logging.time, "time", lambda: clock[0])
    factory = logging.getLogRecordFactory()

    def record(*args, **kwargs):
        item = factory(*args, **kwargs)
        item.created = clock[0]
        return item

    logging.setLogRecordFactory(record)
    handlers = []

    def configure(path, days=7):
        handler = file_logging.configure_file_logging(str(path), days)
        if handler:
            handlers.append(handler)
        return handler

    yield configure, output, clock
    for item in list(logging.root.manager.loggerDict.values()) + [logging.getLogger()]:
        if isinstance(item, logging.Logger):
            for handler in handlers:
                item.removeHandler(handler)
    for handler in handlers:
        handler.close()
    logging.setLogRecordFactory(factory)
    console.close()
    for item, handlers, level, propagate, disabled in saved:
        item.handlers = handlers
        item.setLevel(level)
        item.propagate, item.disabled = propagate, disabled


def test_file_covers_propagation_boundaries_and_keeps_console(logs, tmp_path):
    configure, output, _ = logs
    path = tmp_path / "logs" / "application.log"
    handler = configure(path)
    assert handler and handler.utc and handler.backupCount == 7 and handler.encoding == "utf-8"
    logging.getLogger("pcbparts_mcp.server").info("hourly held back: café")
    logging.getLogger("thirdparty").warning("upstream warning")
    logging.getLogger("thirdparty").info("unwanted info")
    logging.getLogger("uvicorn.error").warning("uvicorn warning")
    logging.getLogger("uvicorn.error").info("uvicorn startup")
    logging.getLogger("fastmcp.server").warning("framework warning")
    logging.getLogger("uvicorn.access").warning("request path")
    try:
        raise ValueError("query broke")
    except ValueError:
        logging.getLogger("fastmcp.server").exception("framework failed")
    text = path.read_text(encoding="utf-8")
    assert "2026-11-20T13:05:01Z INFO pcbparts_mcp.server: hourly held back: café" in text
    for message in ("upstream warning", "uvicorn warning", "framework warning", "framework failed"):
        assert text.count(message) == 1
        assert message in output.getvalue()
    assert "Traceback (most recent call last)" in text and "ValueError: query broke" in text
    assert all(line.startswith("2026-11-20T13:05:01Z ") for line in text.splitlines())
    assert "request path" not in text and "uvicorn startup" not in text and "unwanted info" not in text
    assert "request path" in output.getvalue() and "uvicorn startup" in output.getvalue()


def test_disabled_path_has_no_effect(logs):
    configure, _, _ = logs
    before = list(logging.getLogger().handlers)
    assert configure("") is None
    assert logging.getLogger().handlers == before


def test_midnight_rotation_and_backup_limit(logs, tmp_path):
    configure, _, clock = logs
    path = tmp_path / "application.log"
    path.touch()
    os.utime(path, (NOW, NOW))
    handler = configure(path, 2)
    for day in range(4):
        clock[0] = NOW + day * 86400
        logging.getLogger("pcbparts_mcp.server").info("day %s", day)
        midnight = datetime.datetime.fromtimestamp(handler.rolloverAt, UTC)
        assert (midnight.hour, midnight.minute, midnight.second) == (0, 0, 0)
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "application.log", "application.log.2026-11-21", "application.log.2026-11-22"]
    assert "day 3" in path.read_text(encoding="utf-8")
    assert "day 2" in (tmp_path / "application.log.2026-11-22").read_text(encoding="utf-8")


def test_restart_rotates_stale_active_file_and_prunes_by_date(logs, tmp_path):
    configure, _, _ = logs
    path = tmp_path / "application.log"
    path.write_text("before downtime\n", encoding="utf-8")
    os.utime(path, (NOW - 20 * 86400, NOW - 20 * 86400))
    for suffix in ("2026-10-01", "2026-11-12", "2026-11-13", "2026-11-19", "notes", "2026-99-99"):
        (tmp_path / f"application.log.{suffix}").write_text("saved", encoding="utf-8")
    assert configure(path)
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "application.log", "application.log.2026-11-13", "application.log.2026-11-19",
        "application.log.2026-99-99", "application.log.notes"]
    assert path.read_text(encoding="utf-8") == ""
    # Also prune old backups when the active file doesn't need a rollover.
    old = tmp_path / "application.log.2026-11-01"
    old.write_text("old", encoding="utf-8")
    os.utime(path, (NOW, NOW))
    assert configure(path) and not old.exists()


def test_unavailable_path_warns_once_and_continues(logs, tmp_path):
    configure, output, _ = logs
    parent = tmp_path / "file"
    parent.write_text("not a directory", encoding="utf-8")
    assert configure(parent / "application.log") is None
    logging.getLogger("pcbparts_mcp.server").info("still running")
    assert output.getvalue().count("continuing without the file") == 1
    assert "still running" in output.getvalue()


@pytest.mark.parametrize("failure", ["write", "flush", "rollover"])
def test_write_failure_disables_file_once(logs, tmp_path, monkeypatch, failure):
    configure, output, clock = logs
    path = tmp_path / "application.log"
    handler = configure(path)

    class BrokenStream:
        def write(self, message):
            if failure == "write":
                raise OSError("disk full")

        def flush(self):
            if failure == "flush":
                raise OSError("disk full")

        def close(self):
            pass

    if failure == "rollover":
        clock[0] = handler.rolloverAt

        def broken(*args):
            raise PermissionError("rotation denied")

        monkeypatch.setattr(handler, "rotate", broken)
    else:
        handler.stream.close()
        handler.stream = BrokenStream()
    logging.getLogger("pcbparts_mcp.server").warning("first warning")
    logging.getLogger("pcbparts_mcp.server").warning("second warning")
    assert handler.failed
    assert output.getvalue().count("continuing without the file") == 1
    assert "first warning" in output.getvalue() and "second warning" in output.getvalue()


@pytest.mark.parametrize(("raw", "expected"), [(None, 7), ("0", 1), ("2", 2), ("bad", 7)])
def test_log_settings(monkeypatch, raw, expected):
    from pcbparts_mcp import config

    monkeypatch.delenv("LOG_KEEP_DAYS", raising=False)
    monkeypatch.delenv("LOG_PATH", raising=False)
    if raw is not None:
        monkeypatch.setenv("LOG_KEEP_DAYS", raw)
    settings = runpy.run_path(config.__file__)
    assert settings["LOG_KEEP_DAYS"] == expected
    assert settings["LOG_PATH"] == ""
    monkeypatch.setenv("LOG_PATH", "/cache/logs/application.log")
    assert runpy.run_path(config.__file__)["LOG_PATH"] == "/cache/logs/application.log"


def test_main_installs_after_uvicorn_configuration_and_preserves_console(tmp_path):
    # Exercise real logging configuration in an isolated process, so dictConfig cannot close
    # pytest's own handlers. run() is replaced before main(): no socket or outside request.
    script = '''
import logging
import sys
import uvicorn
from fastmcp.utilities.logging import configure_logging
import fastmcp
from pcbparts_mcp import server
fastmcp.settings.enable_rich_logging = False
configure_logging()
server.LOG_PATH = sys.argv[1]
def run(app, **options):
    uvicorn.Config(app, **options)
    logging.getLogger("pcbparts_mcp.server").info("application info")
    logging.getLogger("uvicorn.error").warning("uvicorn warning")
    logging.getLogger("fastmcp").warning("framework warning")
    logging.getLogger("uvicorn.access").info('%s - "%s %s HTTP/%s" %d', 'proxy', 'GET', '/mcp', '1.1', 200)
uvicorn.run = run
server.main()
'''
    path = tmp_path / "application.log"
    outputs = [subprocess.run([sys.executable, "-c", script, value], capture_output=True, text=True, check=True)
               for value in ("", str(path))]
    assert outputs[0].stdout == outputs[1].stdout
    assert outputs[0].stderr == outputs[1].stderr
    assert "Logging error" not in outputs[1].stderr
    text = path.read_text(encoding="utf-8")
    assert "application info" in text and "uvicorn warning" in text and "framework warning" in text
    assert 'GET /mcp' not in text
