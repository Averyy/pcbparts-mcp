"""Call-log and stats recovery from failed writes, torn files, startup errors and leftover files."""

import asyncio
import builtins
import datetime as dt
import gzip
import json
import logging
import os
import re
import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest

from pcbparts_mcp import call_log, config, server, stats
from test_call_log import DATE, read_rows, record
from test_usage_stats import Clock


@pytest.mark.parametrize("blocked", ["stats", "rows"], ids=["stats", "rows"])
async def test_watchdog_keeps_checking_during_hung_persistence(monkeypatch, blocked):
    ticks, checked = asyncio.Queue(), asyncio.Queue()
    entered, release = asyncio.Event(), asyncio.Event()
    writes = []

    async def sleep(seconds):
        assert seconds == 60
        await ticks.get()

    async def hung():
        writes.append(1)
        entered.set()
        await release.wait()

    async def noop():
        pass

    def check(count):
        checked.put_nowait(count + 1)
        return count + 1

    monkeypatch.setattr(server, "asyncio", SimpleNamespace(**(vars(asyncio) | {"sleep": sleep})))
    monkeypatch.setattr(server, "_exit_if_stuck", check)
    monkeypatch.setattr(server, "_distributor_quotas", {})
    monkeypatch.setattr(stats.usage, "save_async", hung if blocked == "stats" else noop)
    monkeypatch.setattr(call_log.recorder, "flush", hung if blocked == "rows" else noop)
    task = asyncio.create_task(server._every_minute())
    try:
        ticks.put_nowait(None)
        await entered.wait()
        assert not checked.empty(), "persistence blocked the first watchdog check"
        assert await checked.get() == 1
        for minute in range(2, 5):
            ticks.put_nowait(None)
            assert await checked.get() == minute
        assert writes == [1]  # bounded to one persistence task, however many ticks pass
    finally:
        release.set()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


async def test_startup_removes_only_recognized_temporary_files(tmp_path):
    removed = [f"calls-{DATE}.jsonl.tmp", f"calls-{DATE}.jsonl.gz.tmp", f"failed-{DATE}.json.tmp",
               "failed-2026-01-01.json.tmp"]
    untouched = ["failed-2026-02-31.json.tmp", "failed-2026-10-17.json.tmp.bak",
                 "calls-2026-10-17.json.tmp", "notes.tmp", "calls-2026-10-17.jsonl.tmp.tmp"]
    for name in removed + untouched:
        (tmp_path / name).write_text("private", encoding="utf-8")
    await call_log.CallLog(clock=Clock()).open(tmp_path)
    assert not any((tmp_path / name).exists() for name in removed)
    assert all((tmp_path / name).read_text(encoding="utf-8") == "private" for name in untouched)


def test_rotation_applies_date_retention_to_temporary_files(tmp_path):
    old = ["calls-2026-09-17.jsonl.tmp", "calls-2026-09-17.jsonl.gz.tmp", "failed-2026-10-10.json.tmp"]
    recent = [f"calls-{DATE}.jsonl.tmp", f"failed-{DATE}.json.tmp"]
    for name in old + recent:
        (tmp_path / name).write_text("private", encoding="utf-8")
    call_log._rotate(tmp_path, dt.date.fromisoformat(DATE), 30, 7)
    assert not any((tmp_path / name).exists() for name in old)
    assert all((tmp_path / name).exists() for name in recent)


@pytest.mark.parametrize("prefix", [b"", b'{"kept":true}\n'], ids=["only", "tail"])
async def test_startup_cuts_incomplete_tail_before_appending(tmp_path, caplog, prefix):
    source = tmp_path / f"calls-{DATE}.jsonl"
    tail = b'{"private":"' + b"x" * 70000 + b"\xce"
    source.write_bytes(prefix + tail)
    log = call_log.CallLog(clock=Clock(), max_rows=2)
    await log.open(tmp_path)
    assert source.read_bytes() == prefix
    assert log._day_rows == (1 if prefix else 0)
    warnings = [r for r in caplog.records if "incomplete" in r.message]
    assert len(warnings) == 1 and warnings[0].levelno == logging.WARNING
    assert str(len(tail)) in warnings[0].message and "private" not in warnings[0].message
    record(log, outcome="ok", reason=None)
    await log.flush()
    assert read_rows(tmp_path)[-1]["tool"] == "jlc_search"


@pytest.mark.parametrize("compressed", [False, True], ids=["plain", "gzip"])
def test_usage_report_skips_and_counts_malformed_lines(tmp_path, compressed):
    report = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/usage_report.py"))["report"]
    row = json.dumps({"tool": "jlc_search", "outcome": "ok", "ms": 1}).encode("utf-8")
    data = row + b'\n{"cut":\n' + row + b'\n{"utf8":"\xce'
    source = tmp_path / f"calls-{DATE}.jsonl"
    if compressed:
        with gzip.open(source.with_suffix(".jsonl.gz"), "wb") as out:
            out.write(data)
    else:
        source.write_bytes(data)
    text = report(tmp_path, [DATE])
    assert "jlc_search / ok: 2" in text
    assert "Malformed call-log lines skipped: 2" in text
    assert "cut" not in text and "utf8" not in text


async def test_startup_failure_retries_preparation_and_restores_budget(tmp_path, monkeypatch):
    (tmp_path / f"calls-{DATE}.jsonl").write_text('{"kept":true}\n', encoding="utf-8")
    original = call_log._prepare_directory

    def broken(*args):
        raise OSError("transient")

    monkeypatch.setattr(call_log, "_prepare_directory", broken)
    log = call_log.CallLog(clock=Clock(), max_rows=3)
    await log.open(tmp_path)
    record(log)
    assert log.dropped_rows == 1
    monkeypatch.setattr(call_log, "_prepare_directory", original)
    await log.flush()
    assert log._day_rows == 1 and "open" not in log._errors
    record(log)
    record(log)
    await log.flush()
    assert len(read_rows(tmp_path)) == 3


def test_batch_classifier_does_not_import_server(monkeypatch):
    original = builtins.__import__

    def guarded(name, *args, **kwargs):
        assert name != "server", "call_log depends on the server module"
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    assert list(call_log.failed_texts("jlc_get_parts", "not_found", "part_not_found", {"parts": ["C1"]},
                                      {"results": [{"error": "Part C1 not found"}]})) == [("row_not_found", "C1")]


def test_stats_startup_prunes_expired_corrupt_file(tmp_path):
    clock = Clock()
    source = tmp_path / "usage.json"
    aside = source.with_name(source.name + ".corrupt")
    aside.write_text("private", encoding="utf-8")
    os.utime(aside, (clock() - 31 * 86400,) * 2)
    stats.UsageStats(clock=clock).open(source)
    assert not aside.exists()


def test_stats_corrupt_retention_and_hourly_prune(tmp_path):
    clock = Clock()
    source = tmp_path / "usage.json"
    source.write_text("broken", encoding="utf-8")
    os.utime(source, (clock(),) * 2)
    usage = stats.UsageStats(clock=clock)
    usage.open(source)
    aside = source.with_name(source.name + ".corrupt")
    assert aside.exists()
    clock.advance(30 * 86400)
    usage.prune()
    assert aside.exists()
    clock.advance(1)
    usage.prune()
    assert not aside.exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits")
def test_stats_modes_repaired_and_private_before_replace(tmp_path, monkeypatch):
    source = tmp_path / "usage.json"
    paths = [source, source.with_name("usage.json.tmp"), source.with_name("usage.json.corrupt")]
    for path in paths:
        path.write_text('{"days":{}}', encoding="utf-8")
        path.chmod(0o644)
    usage = stats.UsageStats(clock=Clock())
    usage.open(source)
    assert all(path.stat().st_mode & 0o777 == 0o600 for path in paths)
    original = os.replace

    def replace(src, dst):
        assert Path(src).stat().st_mode & 0o777 == 0o600
        original(src, dst)
        assert Path(dst).stat().st_mode & 0o777 == 0o600

    monkeypatch.setattr(stats.os, "replace", replace)
    for _ in range(2):
        usage.record_start()
        usage.save()
        assert usage.ok
    source.write_text("broken", encoding="utf-8")
    stats.UsageStats(clock=Clock()).open(source)


async def test_wide_shapes_cap_every_list_and_count_the_rest(tmp_path):
    log = call_log.CallLog(clock=Clock())
    await log.open(tmp_path)
    packages = ["P" * 100 + str(i) for i in range(100)]
    specs = ["S" * 100 + str(i) for i in range(100)]
    params = {f"arg{i:02}" for i in range(40)} | {"packages", "spec_filters"}
    log.catalog = call_log.ShapeCatalog(packages=frozenset(packages), attributes=frozenset(specs))
    args = dict.fromkeys(params, True) | {"packages": packages, "spec_filters": [{"name": n} for n in specs]}
    record(log, outcome="bad_request", reason=None, args=args, params=params)
    shape = log._rows[0]["shape"]
    assert len(shape["packages"]) <= 10 and shape["packages_omitted"] == 90
    assert len(shape["spec_filters"]) <= 20 and shape["spec_filters_omitted"] == 80
    assert len(shape["args"]) <= 20 and shape["args_omitted"] == len(params) - 20
    assert len(json.dumps(log._rows[0]).encode("utf-8")) < 2500


async def test_buffer_byte_budget_includes_inflight_and_retries(tmp_path, monkeypatch):
    log = call_log.CallLog(clock=Clock(), row_cap=100, buffer_bytes=5000)
    await log.open(tmp_path)
    while not log.dropped_rows:
        record(log)
    assert 0 < len(log._rows) < 100
    count = len(log._rows)
    entered, release = asyncio.Event(), asyncio.Event()
    original = asyncio.to_thread

    async def worker(fn, *args, **kwargs):
        if fn is call_log._persist:
            entered.set()
            await release.wait()
            raise OSError("injected")
        return await original(fn, *args, **kwargs)

    monkeypatch.setattr(call_log.asyncio, "to_thread", worker)
    task = asyncio.create_task(log.flush())
    try:
        await entered.wait()
        dropped = log.dropped_rows
        record(log)
        assert log.dropped_rows == dropped + 1
    finally:
        release.set()
        await task
    assert len(log._rows) == count
    monkeypatch.setattr(call_log.asyncio, "to_thread", original)
    await log.flush()
    assert len(read_rows(tmp_path)) == count
    record(log)
    assert len(log._rows) == 1  # acknowledged bytes release the buffer budget


def test_flush_serializes_bounded_chunks_and_rolls_back_whole_day(tmp_path, monkeypatch):
    rows = [{"t": DATE + "T00:00:00Z", "tool": "jlc_search", "shape": {"args": ["x" * 1000]}} for _ in range(200)]
    dest = tmp_path / f"calls-{DATE}.jsonl"
    dest.write_bytes(b'{"kept":true}\n')
    original = call_log._private_open
    writes = []

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
            assert len(data) <= 64 * 1024
            if len(writes) == 2:
                self.out.write(data[:7])
                raise OSError("partial write")
            return self.out.write(data)

    monkeypatch.setattr(call_log, "_private_open", lambda *a, **k: Writer(original(*a, **k)))
    rollbacks = {}
    remaining, _, errors = call_log._persist(tmp_path, rows, {}, dt.date.fromisoformat(DATE), 30, 7, False, rollbacks)
    assert writes and max(writes) <= 64 * 1024
    assert remaining == rows and errors == {"append": "OSError"}
    assert dest.read_bytes() == b'{"kept":true}\n'
    monkeypatch.setattr(call_log, "_private_open", original)
    assert call_log._persist(tmp_path, remaining, {}, dt.date.fromisoformat(DATE), 30, 7, False, rollbacks) == ([], set(), {})
    assert len(read_rows(tmp_path)) == 201


def test_privacy_distinguishes_retention_and_stock_exclusion():
    root = Path(__file__).resolve().parents[1]
    text = (root / "landing/privacy.html").read_text(encoding="utf-8")
    assert "stock_below_minimum" in text and "blocked_by_min_stock" in text
    assert "distributor_apps" in text and "365 days" in text
    assert "Replaced each UTC day" not in text
    assert "50 MB" in text and "2,000 characters" in text and ".corrupt" in text


def test_changelog_preserves_jlcpcb_guidance():
    text = (Path(__file__).resolve().parents[1] / "CHANGELOG.md").read_text(encoding="utf-8")
    entry = text.split("## 0.10.5 ", 1)[1].split("\n## ", 1)[0]
    assert "instead of saying to use them only when JLCPCB can't answer" not in entry
    assert "JLCPCB-first" in entry and "LOG_MAX_BYTES_PER_DAY" in entry
    assert "STATS_TOKEN" in entry.split("### Added", 1)[0]
    assert "tool_apps" in entry.split("### Added", 1)[1].split("### Changed", 1)[0]


def test_reference_examples_and_storage_bounds():
    text = (Path(__file__).resolve().parents[1] / "docs/ref-server-internals.md").read_text(encoding="utf-8")
    examples = [json.loads(body) for body in re.findall(r"```json\n(.*?)\n```", text, re.S)]
    rows = [row for example in examples for row in example.get("queries", [example])]
    assert all(row.get("tool") == "jlc_stock_check" for row in rows if row.get("reason") == "no_results_words")
    for detail in ("LOG_MAX_BYTES_PER_DAY", "2,000", "64 KiB", "8 MiB", "incomplete", ".tmp", ".corrupt"):
        assert detail in text
