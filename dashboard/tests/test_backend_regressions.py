import gzip
import json
import tracemalloc
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta

import httpx
import pytest

from benchmark_backend import api_handler
from pcbparts_dashboard import collector, server as server_module
from pcbparts_dashboard.collector import collect
from pcbparts_dashboard.eastern import EasternRecords, OUTCOMES, RULES_VERSION, persist_eastern_days
from pcbparts_dashboard.payload import build_payload
from pcbparts_dashboard.store import Store, parse_timestamp as dt, timestamp
from test_eastern import save_day


@pytest.mark.parametrize("bad", [
    {"tools": ["invalid"]}, {"tools": {"search": []}},
    {"tools": {"search": {"calls": "10"}}},
    {"tools": {"search": {"avg_ms": float("nan")}}},
    {"hours": {}}, {"hours": ["bad"] * 24},
    {"failed_hours": [float("inf")] * 24},
    {"reasons": {"search": []}}, {"per_ip_refusals": [1]},
    {"distributor_limits": {"mouser": {"held_back": [1]}}},
    {"distributors": []}, {"db_waits": {"components": []}},
    {"latency": {"search": {"counts": "invalid"}}},
    {"apps": {"app": "invalid"}}, {"popular_terms": ["invalid"]},
    pytest.param({"calls": 10**200}, id="huge-day-count"),
    pytest.param({"tools": {"search": {"calls": 10**200, "ok": 10**200}}}, id="huge-tool-count"),
    pytest.param({"hours": [10**200] * 24}, id="huge-hour-count"),
    pytest.param({"calls": 10**12 + 1}, id="day-over-limit"),
    pytest.param({"tools": {"search": {"calls": 10**12 + 1}}}, id="tool-over-limit"),
    pytest.param({"latency": {"search": {"counts": [10**12 + 1]}}}, id="bucket-over-limit"),
    pytest.param({"calls": -1}, id="negative-day-count"),
    pytest.param({"tools": {"search": {"ok": -1}}}, id="negative-tool-count"),
    pytest.param({"hours": [-1] * 24}, id="negative-hour-count"),
])
def test_malformed_nested_stats_leave_store_untouched(settings, store, clock, stats_reply, bad):
    store.save_stats(stats_reply, timestamp(clock() - timedelta(hours=1)))
    store.set_meta("last_success_at", timestamp(clock() - timedelta(hours=1)))
    before = {table: store._connection.execute(f"SELECT * FROM {table}").fetchall()
              for table in ("days", "snapshots", "eastern_days", "health")}
    success = store.get_meta("last_success_at")
    malformed = {"days": [
        {"date": "2026-11-20", "calls": 99999},
        {"date": "2026-11-21", "calls": 99999} | bad,
    ]}
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=json.dumps(malformed))
        if request.url.path == "/mcp/stats" else httpx.Response(503)
    )) as client:
        result = collect(settings, store, client=client, now=clock)
    assert not result["ok"] and result["days_stored"] == 0
    assert "invalid day record" in result["error"]
    assert not store.get_meta("last_fetch")["ok"]
    assert store.get_meta("last_success_at") == success
    assert store.get_meta("last_full_fetch_at") is None
    for table, rows in before.items():
        assert store._connection.execute(f"SELECT * FROM {table}").fetchall() == rows
    assert build_payload(store, settings, clock())["edays"]


@pytest.mark.parametrize("count", [0, 10**12])
def test_counter_validation_includes_zero_and_upper_bound(settings, store, clock, count):
    reply = {"days": [{
        "date": "2026-11-21", "calls": count,
        "tools": {"search": {"calls": count, "ok": count}},
        "hours": [count] + [0] * 23,
    }]}
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json=reply if request.url.path == "/mcp/stats" else {}
    ))) as client:
        assert collect(settings, store, client=client, now=clock)["ok"]
    assert store.all_days() == reply["days"]
    assert store.get_meta("last_success_at") == timestamp(clock())
    assert build_payload(store, settings, clock())["edays"]


class Chunks(httpx.SyncByteStream):
    def __init__(self, body, chunk_size=1024):
        self.body, self.chunk_size, self.read, self.closed = body, chunk_size, 0, False

    def __iter__(self):
        for i in range(0, len(self.body), self.chunk_size):
            chunk = self.body[i:i + self.chunk_size]
            self.read += len(chunk)
            yield chunk

    def close(self):
        self.closed = True


@pytest.mark.parametrize("endpoint", ["stats", "health"])
@pytest.mark.parametrize("status", [200, 503])
@pytest.mark.parametrize("encoding,limit", [("gzip", "decoded"), ("identity", "decoded"), ("identity", "compressed")])
def test_stream_limits_cover_success_and_error_bodies(settings, store, clock, monkeypatch, endpoint, status, encoding, limit):
    monkeypatch.setattr(collector, "STATS_MAX_BYTES", 4096 if limit == "decoded" else 65536, raising=False)
    monkeypatch.setattr(collector, "HEALTH_MAX_BYTES", 4096 if limit == "decoded" else 65536, raising=False)
    monkeypatch.setattr(collector, "MAX_COMPRESSED_BYTES", 4096 if limit == "compressed" else 65536, raising=False)
    body = b'{"days": [], "padding": "' + b"x" * 32768 + b'"}'
    stream = Chunks(gzip.compress(body) if encoding == "gzip" else body)

    def respond(request):
        if endpoint == "health" and request.url.path == "/mcp/stats":
            return httpx.Response(200, json={"days": []})
        return httpx.Response(status, stream=stream, headers={"Content-Encoding": encoding})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = collect(settings, store, client=client, now=clock)
    error = result["error"] if endpoint == "stats" else store.get_meta("last_fetch")["health_error"]
    assert error and limit in error and "limit" in error
    assert result["ok"] is (endpoint == "health")
    assert stream.closed
    if encoding == "identity":
        assert stream.read < len(body)
    if endpoint == "stats":
        assert store.all_days() == [] and store.get_meta("last_success_at") is None


def test_legacy_unsorted_stays_separate_and_upgrades_saved_rules(store):
    tool = dict.fromkeys(OUTCOMES, 0) | {"calls": 100, "ok": 60, "unsorted": 40}
    for day in ("2026-11-20", "2026-11-21"):
        store.merge_day({"date": day, "calls": 100, "tools": {"search": tool}}, "2026-11-22T00:00:00Z")
    records = EasternRecords(store, dt("2026-11-22T00:00:00Z"))
    result = records.eastern_day("2026-11-20")
    assert result["tools"]["search"] == tool | {"avg_ms": None}
    old = deepcopy(result)
    old["tools"]["search"]["ok"] = 100
    store.save_eastern_day(old, "2026-11-22T00:00:00Z", rules_version=3)
    assert RULES_VERSION > 3
    assert EasternRecords(store, records.as_of).eastern_day("2026-11-20")["tools"]["search"]["ok"] == 60


def test_unchanged_final_day_does_not_write_but_partial_day_can_become_final(store):
    record = {"date": "2026-11-20", "calls": 10}
    store.merge_day(record, "2026-11-20T12:00:00Z")
    store.merge_day(record, "2026-11-21T00:00:00Z")
    assert EasternRecords(store, dt("2026-11-22T00:00:00Z"))._final(record["date"])
    changes = store._connection.total_changes
    store.merge_day(record, "2026-11-22T00:00:00Z")
    assert store._connection.total_changes == changes
    assert store.newest_stats_at() == "2026-11-21T00:00:00Z"


@pytest.mark.parametrize("poll", [False, True])
def test_cached_history_does_not_decode_raw_inputs_or_unrelated_snapshots(store, settings, monkeypatch, poll):
    for day in ("2026-10-01", "2026-10-02", "2026-11-20", "2026-11-21"):
        save_day(store, day, snapshots=(5,))
    now = dt("2026-11-22T00:00:30Z")
    persist_eastern_days(store, now, settings)
    queries = []
    store._connection.set_trace_callback(queries.append)
    try:
        if poll:
            persist_eastern_days(store, now, settings)
        else:
            assert build_payload(store, settings, now)["edays"]
    finally:
        store._connection.set_trace_callback(None)
    bulk_reads = [q for q in queries if ("data FROM days" in q or "data FROM snapshots" in q)
                  and "WHERE" not in q]
    assert not bulk_reads
    if poll:
        assert not any("SELECT date, data FROM eastern_days" in q for q in queries)


def test_api_reuses_encoding_until_store_change_or_eastern_rollover(store, settings, clock, monkeypatch):
    builds, compressions = [], []
    build, compress = server_module.build_payload, server_module.gzip.compress

    def counted_build(*args, **kwargs):
        builds.append(True)
        return build(*args, **kwargs)

    def counted_compress(*args, **kwargs):
        compressions.append(True)
        return compress(*args, **kwargs)

    monkeypatch.setattr(server_module, "build_payload", counted_build)
    monkeypatch.setattr(server_module.gzip, "compress", counted_compress)
    handler = api_handler(store, settings, clock())
    handler.server.runner.clock = clock
    replies = []
    handler._send = lambda status, body, *args: replies.append(body)
    handler.do_GET()
    clock.advance(300)
    handler.do_GET()
    assert len(builds) == len(compressions) == 1
    assert replies[0] == replies[1]
    handler.headers = {}
    handler.do_GET()
    assert gzip.decompress(replies[0]) == replies[-1]
    assert len(builds) == len(compressions) == 1
    store.set_meta("last_fetch", {"ok": False, "error": "test"})
    handler.do_GET()
    assert len(builds) == 2
    clock.value = dt("2026-11-22T05:00:00Z")
    handler.do_GET()
    assert len(builds) == 3


@pytest.mark.parametrize("chunks", [1, 7, 65536])
@pytest.mark.parametrize("members", [1, 2])
def test_streamed_gzip_at_the_limit_and_concatenated_members(settings, store, clock, monkeypatch, chunks, members):
    body = b'{"days": [], "padding": "' + b"x" * 16384 + b'"}'
    monkeypatch.setattr(collector, "STATS_MAX_BYTES", len(body))
    split = len(body) // 2
    compressed = gzip.compress(body) if members == 1 else gzip.compress(body[:split]) + gzip.compress(body[split:])
    stream = Chunks(compressed, chunks)
    with httpx.Client(transport=httpx.MockTransport(lambda request: (
        httpx.Response(200, stream=stream, headers={"Content-Encoding": "gzip"})
        if request.url.path == "/mcp/stats" else httpx.Response(200, json={})
    ))) as client:
        assert collect(settings, store, client=client, now=clock)["ok"]
    assert stream.closed


def test_gzip_bomb_is_bounded_before_inflation(settings, store, clock, monkeypatch):
    monkeypatch.setattr(collector, "STATS_MAX_BYTES", 65536)
    compressed = gzip.compress(b"x" * (16 * 1024 * 1024))
    stream = Chunks(compressed, len(compressed))
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(503, stream=stream, headers={"Content-Encoding": "gzip"})
        if request.url.path == "/mcp/stats" else httpx.Response(503)
    )) as client:
        tracemalloc.start()
        try:
            result = collect(settings, store, client=client, now=clock)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
    assert not result["ok"] and "decoded" in result["error"]
    assert peak < 1024 * 1024
    assert stream.closed


def test_truncated_gzip_is_a_failed_fetch(settings, store, clock):
    stream = Chunks(gzip.compress(b'{"days": []}')[:-2], 5)
    with httpx.Client(transport=httpx.MockTransport(
        lambda _: httpx.Response(200, stream=stream, headers={"Content-Encoding": "gzip"})
    )) as client:
        assert not collect(settings, store, client=client, now=clock)["ok"]
    assert stream.closed and store.get_meta("last_success_at") is None


def test_cached_eastern_day_reads_no_raw_day_or_snapshot(store):
    for day in ("2026-11-20", "2026-11-21"):
        save_day(store, day, snapshots=(5,))
    now = dt("2026-11-22T00:00:30Z")
    expected = EasternRecords(store, now).eastern_day("2026-11-20")
    queries = []
    store._connection.set_trace_callback(queries.append)
    try:
        assert EasternRecords(store, now).eastern_day("2026-11-20") == expected
    finally:
        store._connection.set_trace_callback(None)
    assert not any("data FROM days" in q or "data FROM snapshots" in q for q in queries)


def test_api_cache_notices_external_import_and_serializes_concurrent_fills(store, settings, clock, monkeypatch):
    handler = api_handler(store, settings, clock())
    builds = []
    original = server_module.build_payload

    def counted(*args, **kwargs):
        builds.append(True)
        return original(*args, **kwargs)

    monkeypatch.setattr(server_module, "build_payload", counted)
    with ThreadPoolExecutor(max_workers=4) as threads:
        replies = list(threads.map(lambda _: handler.server.data_reply(clock()), range(8)))
    assert len(builds) == 1 and all(reply == replies[0] for reply in replies)
    with Store(settings.db_path) as external:
        external.set_meta("last_fetch", {"ok": False, "error": "external fetch"})
    body, _ = handler.server.data_reply(clock())
    assert len(builds) == 2 and json.loads(body)["last_fetch"]["error"] == "external fetch"


def test_api_cache_notices_external_commit_during_encoding(store, settings, clock, monkeypatch):
    previous = {"ok": True, "at": timestamp(clock())}
    updated = {"ok": False, "error": "external fetch"}
    store.set_meta("last_fetch", previous)
    handler = api_handler(store, settings, clock())
    compress = server_module.gzip.compress
    compressions = []

    with Store(settings.db_path) as external:
        def commit_during_compression(*args, **kwargs):
            compressions.append(True)
            if len(compressions) == 1:
                external.set_meta("last_fetch", updated)
            return compress(*args, **kwargs)

        monkeypatch.setattr(server_module.gzip, "compress", commit_during_compression)
        first, _ = handler.server.data_reply(clock())
        assert json.loads(first)["last_fetch"] == previous
        assert store.get_meta("last_fetch") == updated
        body, compressed = handler.server.data_reply(clock())
        assert json.loads(body)["last_fetch"] == updated
        assert gzip.decompress(compressed) == body
        assert handler.server.data_reply(clock()) == (body, compressed)
        assert len(compressions) == 2


def test_partial_unchanged_fetch_advances_exact_endpoint(store):
    record = {"date": "2026-11-21", "calls": 10}
    store.merge_day(record, "2026-11-21T12:00:00Z")
    store.merge_day(record, "2026-11-21T13:00:00Z")
    point = EasternRecords(store, dt("2026-11-21T13:00:00Z")).at(record["date"], dt("2026-11-21T13:00:00Z"))
    assert point["calls"] == 10 and not point["approx"]
