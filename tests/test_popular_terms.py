"""0.10.5 popular tokens: thresholds, restart privacy, retention and sparse aggregate files."""

import asyncio
import json
import threading

import pytest

from pcbparts_mcp import stats
from test_usage_stats import Clock


def terms(usage):
    return usage.summary()["days"][0]["popular_terms"]


def test_tokenization():
    assert stats.query_tokens("The (10µF), 10μF; [4.7Ω] | 'TPS63020' \"USB-C\" {SOT-23} <foo/bar> "
                             "...lm358!? --1k-- __x__ +éé+ a an AND or for with of to in on at by from") == [
        "10uf", "4.7ohm", "tps63020", "usb-c", "sot-23", "foo/bar", "lm358", "1k", "éé"]
    assert stats.query_tokens(None) == []
    assert stats.query_tokens("x " + "x" * 41 + " " + "y" * 40) == ["y" * 40]
    assert stats.query_tokens(" ".join(f"token{i}" for i in range(25))) == [f"token{i}" for i in range(20)]
    assert stats.query_tokens("mosfet MOSFET mosfet") == ["mosfet"]


def test_threshold_platforms_and_outcomes(tmp_path):
    usage = stats.UsageStats(clock=Clock())
    usage.open(tmp_path / "u.json")
    usage.record_start()
    for i in range(30):
        usage.record_terms("jlc_search", "ok", "rare rare", f"platform{i}", platform=True)
    for i in range(8):
        usage.record_terms("board_search", "not_found", "rare", f"caller{i}")
    assert len(usage._terms["rare"][1]) == 9
    assert terms(usage) == {}
    usage.save()
    assert "rare" not in usage.path.read_text(encoding="utf-8")
    usage.record_terms("sensor_recommend", "bad_request", "rare", "caller8")
    usage.record_terms("jlc_search_help", "ok", "rare", "caller8")
    usage.record_terms("cse_search", "ok", "rare", None)
    assert terms(usage) == {}
    usage.record_terms("jlc_stock_check", "failed", "rare", "caller8")
    assert terms(usage) == {"rare": 40}
    for i, outcome in enumerate(stats.OUTCOMES):
        usage.record_terms("jlc_search", outcome, "rare", f"another{i}")
    assert terms(usage) == {"rare": 45}
    assert len(usage._terms["rare"][1]) == 10
    assert all(isinstance(value, bytes) for value in usage._terms["rare"][1])


def test_restart_keeps_published_counts_only(tmp_path):
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    path = tmp_path / "u.json"
    usage.open(path)
    for i in range(10):
        usage.record_terms("jlc_search", "ok", "mosfet", f"caller{i}")
    for i in range(9):
        usage.record_terms("cse_search", "ok", "secret", f"caller{i}")
    usage.save()
    assert terms(usage) == {"mosfet": 10}
    again = stats.UsageStats(clock=clock)
    again.open(path)
    again.record_terms("jlc_search", "ok", "mosfet secret", "caller9")
    assert again._term_salt != usage._term_salt
    assert terms(again) == {"mosfet": 11}
    again.save()
    assert "secret" not in path.read_text(encoding="utf-8")
    assert terms(again) == {"mosfet": 11}  # refresh is idempotent
    for i in range(9):
        again.record_terms("cse_search", "ok", "secret", f"caller{i}")
    assert terms(again) == {"mosfet": 11, "secret": 10}


def test_rollover_top_totals_and_retention(tmp_path):
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    usage.open(tmp_path / "u.json")
    for i in range(205):
        for caller in range(10):
            usage.record_terms("jlc_search", "ok", f"term{i:03}", str(caller))
    assert len(terms(usage)) == 200 and "term204" not in terms(usage)
    salt = usage._term_salt
    clock.advance(86400)
    for caller in range(10):
        usage.record_terms("jlc_search", "ok", "term000", str(caller))
    assert usage._term_salt != salt
    assert terms(usage) == {"term000": 10}
    assert usage.summary()["totals"]["popular_terms"]["term000"] == 20
    assert len(usage.summary()["totals"]["popular_terms"]) == 200
    clock.advance(86400 * 30)
    usage.save()
    assert all(day["popular_terms"] is None for day in usage.summary()["days"])
    assert usage.summary()["totals"]["popular_terms"] is None
    assert all(day["popular_terms"] is None for day in json.loads(usage.path.read_text(encoding="utf-8"))["days"].values())


def test_daily_token_cap(monkeypatch):
    monkeypatch.setattr(stats, "MAX_POPULAR_TOKENS", 2)
    usage = stats.UsageStats(clock=Clock())
    for i in range(10):
        usage.record_terms("jlc_search", "ok", "first second third", str(i))
    assert terms(usage) == {"first": 10, "second": 10}
    assert set(usage._terms) == {"first", "second"}


def test_old_day_and_sparse_roundtrip(tmp_path):
    path = tmp_path / "u.json"
    path.write_text(json.dumps({"days": {"2026-10-16": {}}}), encoding="utf-8")
    usage = stats.UsageStats(clock=Clock())
    usage.open(path)
    assert terms(usage) is None
    usage.record_call("jlc_search", "ok", 10, app="app")
    usage.record_call("jlc_search", "failed", 20, app="app", reason="exception")
    before = usage.summary()
    usage.save()
    saved = json.loads(path.read_text(encoding="utf-8"))["days"]["2026-10-17"]
    assert saved["tool_apps"] == {"jlc_search": {"app": {"calls": 2, "ok": 1, "failed": 1}}}
    again = stats.UsageStats(clock=Clock())
    again.open(path)
    assert again.summary() == before
    assert before["days"][0]["tool_apps"]["jlc_search"]["app"]["not_found"] == 0


async def test_save_worker_does_not_clear_new_counts(tmp_path, monkeypatch):
    usage = stats.UsageStats(clock=Clock())
    usage.open(tmp_path / "u.json")
    usage.record_call("jlc_search", "ok", 10)
    loop, thread = asyncio.get_running_loop(), threading.get_ident()
    entered, release = asyncio.Event(), threading.Event()
    original = stats._write_usage

    def write(path, text):
        assert threading.get_ident() != thread
        loop.call_soon_threadsafe(entered.set)
        release.wait()
        original(path, text)

    monkeypatch.setattr(stats, "_write_usage", write)
    task = asyncio.create_task(usage.save_async())
    try:
        await entered.wait()
        usage.record_call("jlc_search", "ok", 20)
        task.cancel()
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert usage._dirty
    monkeypatch.setattr(stats, "_write_usage", original)
    await usage.save_async()
    assert not usage._dirty
    again = stats.UsageStats(clock=Clock())
    again.open(usage.path)
    assert again.summary()["totals"]["calls"] == 2
