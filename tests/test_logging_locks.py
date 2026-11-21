"""Logging under held locks and failed rollbacks; retention retries; canonical app names; stats expiry without traffic."""

import asyncio
import io
import json
import logging
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from pcbparts_mcp import call_log, file_logging, server, stats
from test_call_log import DATE, read_rows
from test_file_logging import logs  # fixture with an injected UTC clock and isolated loggers
from test_logging_limits import app_record
from test_usage_stats import Clock


@pytest.mark.parametrize("rollover", [False, True], ids=["backup", "rollover"])
def test_pruning_scans_and_deletes_without_holding_handler_lock(logs, tmp_path, monkeypatch, rollover):
    configure, _, clock = logs
    handler = configure(tmp_path / "application.log")
    expired = tmp_path / "application.log.2026-01-01"
    expired.write_text("private", encoding="utf-8")
    depth, scans, rotations, deletions = [0], [], [], []

    class Lock:
        def __enter__(self):
            self.acquire()
            return self

        def __exit__(self, *args):
            self.release()

        def acquire(self, blocking=True, timeout=-1):
            depth[0] += 1
            return True

        def release(self):
            depth[0] -= 1

    monkeypatch.setattr(handler, "lock", Lock())
    unlink, remove = Path.unlink, os.remove
    get_files, rotate = handler.getFilesToDelete, handler.rotate

    def scanned():
        scans.append(depth[0])
        return get_files()

    def rotated(*args):
        rotations.append(depth[0])
        return rotate(*args)

    def deleted(fn, path, *args, **kwargs):
        deletions.append(depth[0])
        return fn(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", lambda path, *a, **k: deleted(unlink, path, *a, **k))
    monkeypatch.setattr(os, "remove", lambda path, *a, **k: deleted(remove, path, *a, **k))
    monkeypatch.setattr(handler, "getFilesToDelete", scanned)
    monkeypatch.setattr(handler, "rotate", rotated)
    if rollover:
        clock[0] = handler.rolloverAt
    file_logging.prune_file_logs()
    assert not expired.exists()
    assert scans == [0], "pruning held the logging lock during directory scanning"
    assert rotations == ([1] if rollover else [])
    assert deletions and set(deletions) == {0}, "pruning held the logging lock during deletion"


def test_stuck_exit_survives_handler_lock_owned_by_another_thread(monkeypatch):
    # Simulate the pruning worker owning the lock. An attempted blocking acquire raises a
    # sentinel instead of hanging the test; the injected exit worker/join model the deadline.
    active = ["watchdog"]
    events = []

    class WouldBlock(BaseException):
        pass

    class HeldLock:
        owner = "pruning-worker"

        def __enter__(self):
            self.acquire()

        def __exit__(self, *args):
            self.release()

        def acquire(self):
            events.append(("acquire", active[0], self.owner))
            raise WouldBlock

        def release(self):
            raise AssertionError("unowned lock")

    handler = logging.StreamHandler(io.StringIO())
    logger = logging.Logger("exit-test")
    logger.addHandler(handler)
    monkeypatch.setattr(handler, "lock", HeldLock())
    monkeypatch.setattr(server, "logger", logger)
    monkeypatch.setattr(server.database_pressure, "stalled_seconds", lambda: server.DB_STUCK_WAIT_SECONDS + 1)
    monkeypatch.setattr(server.os, "write", lambda fd, data: events.append(("stderr", fd, data)))
    monkeypatch.setattr(server, "_exit_process", lambda code: events.append(("exit", code)))

    class Writer:
        def __init__(self, *, target, daemon, **kwargs):
            assert daemon
            self.target = target

        def start(self):
            events.append(("start",))

        def join(self, timeout):
            assert timeout == server.EXIT_FLUSH_SECONDS
            active[0] = "exit-worker"
            try:
                self.target()
            except WouldBlock:
                events.append(("deadline", timeout))
            finally:
                active[0] = "watchdog"

    monkeypatch.setattr(server, "threading", SimpleNamespace(Thread=Writer))
    try:
        server._exit_if_stuck(server.STUCK_CHECKS_BEFORE_EXIT - 1)
    except WouldBlock:
        pass
    assert events[-1] == ("exit", 1), "watchdog blocked on the handler before reaching os._exit"
    stderr = next(event for event in events if event[0] == "stderr")
    assert stderr[1] == 2 and b"exiting so Docker restarts" in stderr[2]
    assert ("acquire", "exit-worker", "pruning-worker") in events
    assert not any(event[:2] == ("acquire", "watchdog") for event in events)


async def test_minute_logging_cannot_wait_indefinitely_for_the_file_handler(logs, tmp_path, monkeypatch):
    configure, output, _ = logs
    handler = configure(tmp_path / "application.log")
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    usage.record_call("jlc_search", "failed", 1, reason="exception")
    clock.advance(60)
    checks, attempts = [], []
    ticks = [0]

    class WouldBlock(BaseException):
        pass

    class HeldLock:
        def __enter__(self):
            self.acquire()

        def __exit__(self, *args):
            raise AssertionError("unowned lock")

        def acquire(self, blocking=True, timeout=-1):
            attempts.append((blocking, timeout))
            if blocking and timeout < 0:
                raise WouldBlock
            return False

        def release(self):
            raise AssertionError("unowned lock")

    async def sleep(seconds):
        assert seconds == 60
        ticks[0] += 1
        if ticks[0] == 3:
            raise asyncio.CancelledError

    async def persist(**kwargs):
        pass

    def check(count):
        checks.append(count + 1)
        return count + 1

    monkeypatch.setattr(stats, "usage", usage)
    monkeypatch.setattr(server, "_distributor_quotas", {})
    monkeypatch.setattr(server, "_refused_callers", SimpleNamespace(flush_if_due=lambda: None))
    monkeypatch.setattr(server, "_exit_if_stuck", check)
    monkeypatch.setattr(server, "_persist_usage", persist)
    monkeypatch.setattr(server, "asyncio", SimpleNamespace(**(vars(asyncio) | {"sleep": sleep})))
    original = handler.lock
    monkeypatch.setattr(handler, "lock", HeldLock())
    try:
        await server._every_minute()
    except (WouldBlock, asyncio.CancelledError):
        pass
    finally:
        handler.lock = original
    assert checks == [1, 2], "minute logging blocked subsequent watchdog ticks"
    assert attempts == [(True, file_logging.FILE_LOCK_TIMEOUT_SECONDS)]
    assert 0 < attempts[0][1] <= 0.25
    assert handler.lock_dropped_records == 1
    assert "Failed tool calls" in output.getvalue()
    logging.getLogger("pcbparts_mcp.server").warning("writer available again")
    assert "writer available again" in Path(handler.baseFilename).read_text(encoding="utf-8")


@pytest.mark.parametrize("next_day", [False, True], ids=["today", "midnight"])
async def test_failed_append_and_rollback_repair_before_retry(tmp_path, monkeypatch, next_day):
    clock = Clock()
    source = tmp_path / f"calls-{DATE}.jsonl"
    source.write_bytes(b'{"kept":true}\n')  # bytes: the asserts count it, and text mode adds \r on Windows
    log = call_log.CallLog(clock=clock)
    await log.open(tmp_path)
    rows = [{"t": DATE + "T00:00:00Z", "ms": i, "shape": {"args": ["x" * 1000]}} for i in range(200)]
    for row in rows:
        assert log._append(row)
    original = call_log._private_open
    writes, truncates = [], []

    class Writer:
        def __init__(self, out):
            self.out = out

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.out.close()

        def __getattr__(self, name):
            return getattr(self.out, name)

        def write(self, data):
            writes.append(len(data))
            if len(writes) == 2:
                self.out.write(data[:7])
                raise OSError("partial append")
            return self.out.write(data)

        def truncate(self, offset):
            truncates.append(offset)
            raise OSError("rollback unavailable")

    monkeypatch.setattr(call_log, "_private_open", lambda *a, **k: Writer(original(*a, **k)))
    await log.flush()
    assert len(writes) == 2 and max(writes) <= 64 * 1024
    assert truncates == [len(b'{"kept":true}\n')]
    assert sum(len(json.dumps(row)) for row in rows) > 64 * 1024
    assert source.stat().st_size == len(b'{"kept":true}\n') + writes[0] + 7
    assert log._rows == rows
    if next_day:
        clock.advance(86400)
    # Writes recover first. A still-failing repair must prevent both retry and new rows
    # from appending, and must not compress an unresolved partial file at midnight.
    extra = {"t": DATE + "T00:00:01Z", "ms": 200}
    assert log._append(extra)
    await log.flush()
    writes_before_recovery = len(writes)
    unresolved_stayed_plain = source.exists() and not source.with_suffix(".jsonl.gz").exists()
    monkeypatch.setattr(call_log, "_private_open", original)
    await log.flush()
    assert read_rows(tmp_path) == [{"kept": True}, *rows, extra]
    assert writes_before_recovery == 2, "a retry appended after bytes whose rollback was still unresolved"
    assert unresolved_stayed_plain
    assert not log._rows and "append" not in log._errors


@pytest.mark.parametrize("failure", ["write", "rollover", "prune"], ids=["write", "roll", "prune"])
def test_retention_retries_after_failure(logs, tmp_path, monkeypatch, failure):
    configure, _, clock = logs
    handler = configure(tmp_path / "application.log")
    expired = tmp_path / "application.log.2026-01-01"
    expired.write_text("private", encoding="utf-8")

    def broken(*args, **kwargs):
        raise OSError("transient failure")

    with monkeypatch.context() as patch:
        if failure == "prune":
            patch.setattr(Path, "unlink", broken)
            file_logging.prune_file_logs()
        else:
            patch.setattr(handler, "_write_record" if failure == "write" else "rotate", broken)
            if failure == "rollover":
                clock[0] = handler.rolloverAt
            logging.getLogger("pcbparts_mcp.server").warning("trigger writer failure")
            assert handler.failed
    assert expired.exists()
    clock[0] += 3600
    file_logging.prune_file_logs()
    assert not expired.exists(), "writer failure permanently suppressed retention"
    # Even a failed writer's old active file must expire while no more messages arrive.
    clock[0] += 9 * 86400
    file_logging.prune_file_logs()
    assert not list(tmp_path.glob("application.log.2026-*"))


async def test_well_known_app_uses_list_canonical_spelling(tmp_path):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    app_record(log, "OpEnAi-mCp (ReSpOnSeS aPi)", "203.0.113.1")
    app_record(log, "cUrSoR", "203.0.113.1")
    await log.flush()
    assert [row["app"] for row in read_rows(tmp_path)] == ["openai-mcp (Responses API)", "Cursor"]


# A tab isn't an app-name character: cleaning drops it, as AppsByAddress does for HTTP callers
@pytest.mark.parametrize("names,canonical", [(("Niche Name", "NICHE NAME"), "niche name"),
                                            (("Niche  Name", "niche name"), "niche name"),
                                            (("Niche\tName", "NicheName"), "nichename")], ids=["case", "spaces", "tabs"])
async def test_custom_app_threshold_and_output_share_canonical_name(tmp_path, names, canonical):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    for i in range(10):
        app_record(log, names[i % 2], f"203.0.113.{i}")
    app_record(log, "one-off", "203.0.113.1")
    await log.flush()
    assert [row["app"] for row in read_rows(tmp_path)] == [canonical] * 10 + ["other"]


@pytest.mark.parametrize("operation", ["load", "save", "async", "summary"], ids=["load", "save", "async", "read"])
async def test_stats_expire_without_traffic(tmp_path, operation):
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    source = tmp_path / "usage.json"
    usage.open(source)
    usage.record_start()
    clock.advance(86400)
    usage.record_start()
    usage.save()
    assert DATE in usage._closed_json and not usage._dirty
    clock.advance((stats.KEEP_DAYS - 1) * 86400)
    if operation == "load":
        usage = stats.UsageStats(clock=clock)
        usage.open(source)
    elif operation == "save":
        usage.save()
    elif operation == "async":
        await usage.save_async()
    else:
        usage.summary(days=stats.KEEP_DAYS)
    assert set(usage._days) == {"2026-10-18"}, "expired days survived clock-based maintenance"
    assert DATE not in usage._closed_json
    assert [day["date"] for day in usage.summary(days=stats.KEEP_DAYS)["days"]] == ["2026-10-18"]
    usage.save()
    assert set(json.loads(source.read_text(encoding="utf-8"))["days"]) == {"2026-10-18"}
    clock.advance(86400)
    await usage.save_async()
    assert usage._days == {} and usage._closed_json == {}
    assert json.loads(source.read_text(encoding="utf-8")) == {"days": {}}
