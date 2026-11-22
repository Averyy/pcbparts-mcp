"""Persistent application logs: fake UTC clocks, local files, no server or network."""

import datetime
import io
import logging
import os
import runpy
import subprocess
import sys
from unittest.mock import MagicMock

import pytest

from pcbparts_mcp import file_logging

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 20, 13, 5, 1, tzinfo=UTC).timestamp()


@pytest.fixture
def logs(monkeypatch):
    monkeypatch.setattr(file_logging, "_retention", {})
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
        fresh = not os.path.exists(path)
        handler = file_logging.configure_file_logging(str(path), days)
        if handler:
            handlers.append(handler)
            if fresh:
                # The handler dates the file it opens by its mtime, which the filesystem sets from the
                # real time: give a new file the injected clock's (tests failed from 2026-11-22 on)
                os.utime(path, (clock[0], clock[0]))
                handler.rolloverAt = handler.computeRollover(int(clock[0]))
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


@pytest.mark.parametrize("acquired", [True, False], ids=["acquired", "timeout"])
@pytest.mark.parametrize("level", [logging.INFO, logging.WARNING, logging.ERROR], ids=["info", "warn", "error"])
def test_file_lock_wait_is_bounded(logs, tmp_path, monkeypatch, acquired, level):
    configure, _, _ = logs
    path = tmp_path / "application.log"
    handler = configure(path)
    lock = MagicMock()
    lock.acquire.return_value = acquired
    record = logging.LogRecord("pcbparts_mcp.server", level, __file__, 0, "concurrent record", (), None)
    with monkeypatch.context() as patch:
        patch.setattr(handler, "lock", lock)
        assert handler.handle(record) is acquired
    args, kwargs = lock.acquire.call_args_list[0]
    assert args == () and kwargs.keys() == {"timeout"}
    assert 0 < kwargs["timeout"] <= 0.25
    assert kwargs["timeout"] == file_logging.FILE_LOCK_TIMEOUT_SECONDS
    assert ("concurrent record" in path.read_text(encoding="utf-8")) is acquired
    assert not handler.failed
    assert handler.lock_dropped_records == (0 if acquired else 1)
    if acquired:
        assert lock.release.called
    else:
        lock.release.assert_not_called()


def test_lock_drops_reported_once_at_rollover(logs, tmp_path, monkeypatch):
    configure, output, clock = logs
    path = tmp_path / "application.log"
    path.touch()
    os.utime(path, (clock[0],) * 2)
    handler = configure(path)
    caller = logging.getLogger("pcbparts_mcp.server")
    total = 0
    for dropped in (3, 0, 2):
        date = datetime.datetime.fromtimestamp(clock[0], UTC).date()
        lock = MagicMock()
        lock.acquire.return_value = False
        with monkeypatch.context() as patch:
            patch.setattr(handler, "lock", lock)
            for _ in range(dropped):
                caller.warning("held-lock record")
        total += dropped
        assert handler.lock_dropped_records == total
        assert output.getvalue().count("held-lock record") == total
        assert "held-lock record" not in path.read_text(encoding="utf-8")
        clock[0] = handler.rolloverAt
        file_logging.prune_file_logs()
        caller.info("writer recovered")
        file_logging.prune_file_logs()
        text = path.read_text(encoding="utf-8")
        assert text.count("records dropped waiting for the file lock") == (1 if dropped else 0)
        if dropped:
            assert f"{date}: {dropped} records dropped waiting for the file lock" in text
        assert "writer recovered" in text
        assert handler.lock_dropped_records == total


def test_midnight_rotation_and_backup_limit(logs, tmp_path):
    configure, _, clock = logs
    path = tmp_path / "application.log"
    path.touch()
    os.utime(path, (NOW, NOW))
    handler = configure(path, 2)
    for day in range(4):
        clock[0] = NOW + day * 86400
        logging.getLogger("pcbparts_mcp.server").info("day %s", day)
        file_logging.prune_file_logs()
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


@pytest.mark.parametrize(("raw", "expected"), [(None, 30), ("0", 1), ("2", 2), ("bad", 30)])
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
    outputs = [subprocess.run([sys.executable, "-c", script, value], capture_output=True, text=True,
                              encoding="utf-8", check=True)
               for value in ("", str(path))]
    assert outputs[0].stdout == outputs[1].stdout
    assert outputs[0].stderr == outputs[1].stderr
    assert "Logging error" not in outputs[1].stderr
    text = path.read_text(encoding="utf-8")
    assert "application info" in text and "uvicorn warning" in text and "framework warning" in text
    assert 'GET /mcp' not in text


def test_scheduled_prune_expires_idle_backups_and_active_file(logs, tmp_path):
    configure, _, clock = logs
    path = tmp_path / "application.log"
    path.touch()
    os.utime(path, (NOW, NOW))
    handler = configure(path)
    logging.getLogger("pcbparts_mcp.server").info("last call before idle")
    old = tmp_path / "application.log.2026-11-12"
    old.write_text("old", encoding="utf-8")
    clock[0] += 9 * 86400
    file_logging.prune_file_logs()
    assert not old.exists()
    assert not list(tmp_path.glob("application.log.2026-*"))
    assert path.read_text(encoding="utf-8") == ""
    assert handler.stream is not None and not handler.stream.closed


def test_message_truncation_is_file_only(logs, tmp_path):
    configure, output, _ = logs
    path = tmp_path / "application.log"
    assert configure(path)
    message = "Invalid arguments for tool: " + "Ω" * 6000 + "PRIVATE-TAIL"
    logging.getLogger("fastmcp.server").warning("%s", message)
    text = path.read_text(encoding="utf-8")
    assert len(text) < 2200 and "PRIVATE-TAIL" not in text
    assert message in output.getvalue()


@pytest.mark.parametrize("raw,expected", [(None, 50_000_000), ("bad", 50_000_000), ("0", 1), ("1000", 1000)],
                         ids=["default", "bad", "min", "set"])
def test_log_byte_budget_setting(monkeypatch, raw, expected):
    from pcbparts_mcp import config
    monkeypatch.delenv("LOG_MAX_BYTES_PER_DAY", raising=False)
    if raw is not None:
        monkeypatch.setenv("LOG_MAX_BYTES_PER_DAY", raw)
    assert runpy.run_path(config.__file__)["LOG_MAX_BYTES_PER_DAY"] == expected


def test_file_budget_counts_bytes_restart_and_rollover(logs, tmp_path, monkeypatch):
    configure, output, clock = logs
    monkeypatch.setattr(file_logging, "LOG_MAX_BYTES_PER_DAY", 500, raising=False)
    path = tmp_path / "application.log"
    path.write_text("Ω" * 220, encoding="utf-8")
    os.utime(path, (clock[0],) * 2)
    handler = configure(path)
    for _ in range(4):
        logging.getLogger("fastmcp.server").warning("%s", "Ω" * 100)
    assert path.stat().st_size <= 500
    assert handler.dropped_lines == 4
    assert output.getvalue().count("daily byte budget reached") == 1
    clock[0] = handler.rolloverAt
    file_logging.prune_file_logs()
    text = path.read_text(encoding="utf-8")
    assert "2026-11-20: 4 lines dropped" in text
    logging.getLogger("pcbparts_mcp.server").info("new day")
    assert "new day" in path.read_text(encoding="utf-8")
    assert handler.dropped_lines == 0 and path.stat().st_size <= 500


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits")
def test_log_modes_repaired_and_new_files_private(logs, tmp_path, monkeypatch):
    from pathlib import Path
    configure, _, clock = logs
    directory = tmp_path / "logs"
    directory.mkdir(mode=0o755)
    path = directory / "application.log"
    old = directory / "application.log.2026-11-19"
    for source in (path, old):
        source.write_text("old\n", encoding="utf-8")
        source.chmod(0o644)
        os.utime(source, (clock[0],) * 2)
    handler = configure(path)
    assert directory.stat().st_mode & 0o777 == 0o700
    assert all(p.stat().st_mode & 0o777 == 0o600 for p in directory.iterdir())
    original = os.open

    def opened(name, flags, mode=0o777, **kwargs):
        if Path(name).parent == directory:
            assert mode == 0o600
        return original(name, flags, mode, **kwargs)

    monkeypatch.setattr(os, "open", opened)
    clock[0] = handler.rolloverAt
    logging.getLogger("pcbparts_mcp.server").info("after rollover")
    assert all(p.stat().st_mode & 0o777 == 0o600 for p in directory.iterdir())
