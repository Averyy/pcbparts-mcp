"""0.10.5 counting only: fixed labels, unchanged replies, fake clocks and mock transports."""

import asyncio
import json
import logging
from types import SimpleNamespace

import httpx
import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ValidationError
from fastmcp.server.middleware import Middleware
from pydantic import ValidationError as PydanticValidationError, validate_call
from wafer import (ChallengeDetected, ConnectionFailed, EmptyResponse, RateLimited, RequestBlocked,
                   ResponseTooLarge, WaferHTTPError, WaferResponse, WaferTimeout)

from pcbparts_mcp import server, stats
from pcbparts_mcp.client import _sent
from pcbparts_mcp.db_worker import COMPONENT_POOL, offload
from pcbparts_mcp.mouser import MouserClient
from test_usage_stats import Clock, ERROR_REPLIES, _render


def day():
    return stats.usage.summary()["days"][0]


def test_new_fields_old_days_and_roundtrip(tmp_path):
    path, clock = tmp_path / "usage.json", Clock()
    path.write_text(json.dumps({"days": {"2026-10-16": {}, "2026-10-17": {}}}), encoding="utf-8")
    usage = stats.UsageStats(clock=clock)
    usage.open(path)
    for saved in usage.summary()["days"]:
        assert all(saved[field] is None for field in stats.SINCE_0_10_5)
    usage.record_start()
    usage.record_call("jlc_search", "not_found", 250, app="backplane", reason="no_results")
    usage.record_call("jlc_search", "bad_request", 1, bad_request_reason="invalid_value")
    usage.record_upstream_status("jlcpcb", "2xx")
    usage.save()
    again = stats.UsageStats(clock=clock)
    again.open(path)
    assert again.summary() == usage.summary()
    current, old = again.summary()["days"]
    assert all(old[field] is None for field in stats.SINCE_0_10_5)
    assert current["versions"] == {stats.__version__: 1}
    assert current["bad_request_reasons"] == {"jlc_search": {"invalid_value": 1}}
    assert current["upstream_status"] == {"jlcpcb": {"2xx": 1}}
    assert current["failed_hours"] == [None] * 21 + [0] * 3


def test_new_fields_validate_on_load(tmp_path):
    path = tmp_path / "usage.json"
    bad = {"bad_request_reasons": {"jlc_search": {"arg:query:string_type": 2, "arg:query:made_up": 9,
                                                "arg:bad name:missing": 9, "SECRET": 9, "other": "bad"}},
           "versions": {"0.10.5": 2, "0.10.5-dev.1": 1, "part number": 9, "x" * 40: 9},
           "upstream_status": {"jlcpcb": {"2xx": 3, "SECRET": 9}, "secret_source": {"2xx": 9}},
           "latency": {"jlc_search": [1, -1, None] + [0] * 8, "bad": [1]},
           "tool_apps": {"jlc_search": {'<bad>': {"calls": 1, "ok": 1, "SECRET": 5}}, "bad": []}}
    path.write_text(json.dumps({"days": {"2026-10-17": bad}}), encoding="utf-8")
    usage = stats.UsageStats(clock=Clock())
    usage.open(path)  # parameters aren't known at open(): validate the label's syntax only
    loaded = usage.summary()["days"][0]
    assert loaded["bad_request_reasons"] == {"jlc_search": {"arg:query:string_type": 2, "other": 0}}
    assert loaded["versions"] == {"0.10.5": 2, "0.10.5-dev.1": 1}
    assert loaded["upstream_status"] == {"jlcpcb": {"2xx": 3}}
    assert loaded["latency"]["jlc_search"]["counts"] == [1] + [0] * 10
    assert list(loaded["tool_apps"]["jlc_search"]) == ["bad"]
    assert "SECRET" not in json.dumps(loaded)
    usage.record_call("jlc_search", "bad_request", 1, bad_request_reason="arg:SECRET:string_type")
    usage.record_call("jlc_search", "bad_request", 1, bad_request_reason="SECRET")
    assert usage.summary()["days"][0]["bad_request_reasons"]["jlc_search"] == {
        "arg:query:string_type": 2, "other": 1, "arg:unknown_argument:string_type": 1}


@pytest.mark.parametrize("field", stats.SINCE_0_10_5)
@pytest.mark.parametrize("value", [None, [], "bad", 1])
def test_invalid_new_field_is_null(tmp_path, field, value):
    path = tmp_path / "usage.json"
    path.write_text(json.dumps({"days": {"2026-10-17": {field: value}}}), encoding="utf-8")
    usage = stats.UsageStats(clock=Clock())
    usage.open(path)
    assert usage.summary()["days"][0][field] is None
    usage.record_call("jlc_search", "ok", 1)
    current = usage.summary()["days"][0][field]
    assert current is not None
    if field == "tool_apps":
        assert current["jlc_search"]["unknown"]["calls"] == 1
    elif field == "latency":
        assert sum(current["jlc_search"]["counts"]) == 1
    else:
        assert current == {}


def test_apps_outcomes_cap_and_totals():
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    for outcome in stats.OUTCOMES:
        usage.record_call("jlc_search", outcome, 100, app="<backplane>")
    for i in range(30):
        usage.record_call("jlc_search", "ok", 1, app=f"app{i}")
    usage.record_call("jlc_get_part", "ok", 1, app="app29")
    apps = usage.summary()["days"][0]["tool_apps"]["jlc_search"]
    assert len(apps) == 31
    assert apps["backplane"] == {"calls": 6, **dict.fromkeys(stats.OUTCOMES, 1)}
    assert "other" not in apps
    assert sum(row["calls"] for row in apps.values()) == 36
    assert usage.summary()["days"][0]["distributor_apps"] == {}
    clock.advance(86400)
    usage.record_call("jlc_search", "not_found", 100, app="backplane", reason="no_results")
    past = usage.summary()["days"][1]["tool_apps"]["jlc_search"]
    assert len(past) == stats.MAX_TOOL_APPS
    assert past["other"]["calls"] == 17
    assert usage.summary()["totals"]["tool_apps"]["jlc_search"]["backplane"]["not_found"] == 2


def test_latency_bounds_percentiles_and_exclusions():
    usage = stats.UsageStats(clock=Clock())
    for ms in stats.LATENCY_BOUNDS_MS:
        usage.record_call("jlc_search", "ok", ms)
    usage.record_call("jlc_search", "failed", 60001, reason="exception")
    usage.record_call("jlc_search", "bad_request", 0)
    usage.record_call("jlc_search", "rate_limited", 0)
    result = usage.summary()
    assert result["latency_bounds_ms"] == list(stats.LATENCY_BOUNDS_MS)
    latency = result["days"][0]["latency"]["jlc_search"]
    assert latency == {"counts": [1] * 11, "p50_ms": 2500, "p95_ms": None, "p99_ms": None}
    assert result["totals"]["latency"]["jlc_search"] == latency
    for outcome in ("similar_only", "not_found"):
        usage.record_call("other_tool", outcome, 100)
    assert usage.summary()["totals"]["latency"]["other_tool"]["p99_ms"] == 100


@pytest.mark.parametrize("finish", ["rollover", "save", "summary", "load"])
def test_busy_app_survives_day_compaction(tmp_path, finish):
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    path = tmp_path / "usage.json"
    usage.open(path)
    # The reserved bucket doesn't use one of today's 50 named slots.
    for outcome in stats.OUTCOMES:
        usage.record_call("jlc_search", outcome, 1, app="other")
    for i in range(stats.MAX_APPS - 1):
        usage.record_call("jlc_search", stats.OUTCOMES[i % len(stats.OUTCOMES)], 1, app=f"app{i}")
    for _ in range(10):
        for outcome in stats.OUTCOMES:
            usage.record_call("jlc_search", outcome, 1, app="busy")
    for i in range(5):
        for outcome in stats.OUTCOMES:
            usage.record_call("jlc_search", outcome, 1, app=f"late{i}")
    apps = {name: row.copy() for name, row in usage.summary()["days"][0]["tool_apps"]["jlc_search"].items()}
    assert len(apps) == stats.MAX_APPS + 1
    assert apps["busy"] == {"calls": 60, **dict.fromkeys(stats.OUTCOMES, 10)}
    assert apps["other"]["calls"] == 36
    totals = {key: sum(row[key] for row in apps.values()) for key in ("calls", *stats.OUTCOMES)}
    usage.save()
    again = stats.UsageStats(clock=clock)
    again.open(path)
    assert again.summary()["days"][0]["tool_apps"]["jlc_search"] == apps
    clock.advance(86400)
    if finish == "rollover":
        usage.record_start()
    elif finish == "save":
        usage.save()
    elif finish == "summary":
        usage.summary()
    else:
        usage = stats.UsageStats(clock=clock)
        usage.open(path)
    compact = usage._days["2026-10-17"]["tool_apps"]["jlc_search"]
    assert len(compact) == stats.MAX_TOOL_APPS
    assert compact["busy"] == apps["busy"]
    assert {key: sum(row.get(key, 0) for row in compact.values()) for key in totals} == totals
    assert compact["other"]["calls"] > apps["other"]["calls"]
    usage.save()
    saved = json.loads(path.read_text(encoding="utf-8"))["days"]["2026-10-17"]["tool_apps"]["jlc_search"]
    assert saved == compact
    assert all(count for row in saved.values() for key, count in row.items() if key != "calls")


@pytest.mark.parametrize("first", ["summary", "save"])
def test_idle_retention_without_calls(tmp_path, first):
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    path = tmp_path / "usage.json"
    usage.open(path)
    usage.record_call("jlc_search", "ok", 1, app="busy")
    usage.save()
    clock.advance(86400 * 31)
    getattr(usage, first)()
    old = usage._days["2026-10-17"]
    assert old["tool_apps"] is old["latency"] is None
    assert old["tools"]["jlc_search"]["calls"] == 1
    usage.save()
    saved = json.loads(path.read_text(encoding="utf-8"))["days"]["2026-10-17"]
    assert saved["tool_apps"] is saved["latency"] is None
    assert usage.summary()["totals"]["tool_apps"] is usage.summary()["totals"]["latency"] is None


def test_loaded_today_does_not_prevent_retention(tmp_path):
    clock = Clock()
    old = stats.UsageStats(clock=clock)
    old.record_call("jlc_search", "ok", 1, app="busy")
    clock.advance(86400 * 31)
    today = stats.UsageStats(clock=clock)
    today.record_call("jlc_search", "ok", 1, app="busy")
    path = tmp_path / "usage.json"
    path.write_text(json.dumps({"days": {**old._days, **today._days}}), encoding="utf-8")
    usage = stats.UsageStats(clock=clock)
    usage.open(path)
    usage.record_start()  # today already exists, so _day() doesn't create it
    usage.save()
    saved = json.loads(path.read_text(encoding="utf-8"))["days"]
    assert saved["2026-10-17"]["tool_apps"] is saved["2026-10-17"]["latency"] is None
    assert saved["2026-11-17"]["tool_apps"] == {"jlc_search": {"busy": {"calls": 1, "ok": 1}}}
    assert usage.summary()["days"][0]["tool_apps"] == today.summary()["days"][0]["tool_apps"]


def test_retention_only_clears_high_cardinality_fields(tmp_path):
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    usage.open(tmp_path / "usage.json")
    usage.record_start()
    usage.record_call("jlc_search", "ok", 1, app="backplane")
    clock.advance(86400 * 29)
    usage.record_start()
    assert usage.summary()["days"][-1]["tool_apps"] is not None
    clock.advance(86400)
    usage.record_start()
    old = usage.summary()["days"][-1]
    assert old["latency"] is old["tool_apps"] is None
    assert old["versions"] == {stats.__version__: 1} and old["tools"]["jlc_search"]["calls"] == 1
    usage.save()
    again = stats.UsageStats(clock=clock)
    again.open(tmp_path / "usage.json")
    assert again.summary()["days"][-1]["latency"] is None


async def test_argument_validation_and_alias_order(monkeypatch):
    errors, arguments = [], []
    mcp = FastMCP("validation")

    @mcp.tool
    async def digikey_get_part(part_number: str) -> dict:
        return {"number": part_number}

    class Observe(Middleware):
        async def on_call_tool(self, context, call_next):
            arguments.append(context.message.arguments)
            try:
                return await call_next(context)
            except Exception as exc:
                errors.append(exc)
                raise

    mcp.add_middleware(server.ArgumentAliasMiddleware())
    mcp.add_middleware(server.UsageStatsMiddleware())
    mcp.add_middleware(Observe())
    stats.usage.tools = {"digikey_get_part"}
    stats.usage.tool_params = {"digikey_get_part": {"part_number"}}
    async with Client(mcp) as client:
        for args in ({}, {"part_number": []}, {"part_number": "P1", "SECRET": 1}):
            result = await client.call_tool("digikey_get_part", args, raise_on_error=False)
            assert result.is_error
        result = await client.call_tool("digikey_get_part", {"mpn": []}, raise_on_error=False)
        assert result.is_error
        result = await client.call_tool("digikey_get_part", {"mpn": "P1"})
        assert result.structured_content == {"number": "P1"}
    assert arguments[-2:] == [{"part_number": []}, {"part_number": "P1"}]
    assert all(isinstance(exc, ValidationError) and isinstance(exc.__cause__, PydanticValidationError)
               for exc in errors)
    # Function-call validation preserves its bounded Pydantic types.
    assert [exc.__cause__.errors()[0]["type"] for exc in errors] == [
        "missing_argument", "string_type", "unexpected_keyword_argument", "string_type"]
    assert day()["bad_request_reasons"] == {"digikey_get_part": {
        "arg:part_number:missing_argument": 1, "arg:part_number:string_type": 2,
        "arg:unknown_argument:unexpected_keyword_argument": 1}}
    assert day()["reasons"] == {} and "SECRET" not in json.dumps(stats.usage.summary())


async def test_notes_cross_offload_and_reset():
    mcp = FastMCP("notes")

    @mcp.tool
    @offload(COMPONENT_POOL)
    def miss() -> dict:
        stats.note(reason="no_results_words")
        return {"results": [], "total": 0}

    @mcp.tool
    async def fail() -> dict:
        stats.note(reason="part_number_unknown")
        raise RuntimeError("test failure")

    mcp.add_middleware(server.UsageStatsMiddleware())
    async with Client(mcp) as client:
        result = await client.call_tool("miss", {})
        assert result.structured_content == {"results": [], "total": 0}
        await client.call_tool("fail", {}, raise_on_error=False)
    assert day()["reasons"] == {"miss": {"no_results_words": 1}, "fail": {"exception": 1}}
    assert stats.call_notes.get() is None
    stats.note(reason="no_results")
    assert stats.call_notes.get() is None


@pytest.mark.parametrize("split", ["part_number_sold_out", "part_number_unknown", "no_results_filtered",
                                  "no_results_part_number", "no_results_words"],
                         ids=["sold", "unknown", "filters", "mpn", "words"])
@pytest.mark.parametrize("predecessor", ["no_results", "part_number_not_in_stock", "blocked_by_min_stock"],
                         ids=["empty", "part", "stock"])
async def test_notes_only_split_their_predecessor(split, predecessor):
    content = {"results": [], "total": 0}
    if predecessor == "part_number_not_in_stock":
        content["hint"] = "No in-stock part matches TEST1; try jlc_stock_check"
    elif predecessor == "blocked_by_min_stock":
        content["why_empty"] = {"blocking": [{"constraint": "min_stock"}]}
    assert server._empty_reason(content) == predecessor
    context = SimpleNamespace(message=SimpleNamespace(name="miss"))

    async def next_call(context):
        stats.note(reason=split)
        return SimpleNamespace(structured_content=content)

    result = await server.UsageStatsMiddleware().on_call_tool(context, next_call)
    expected = split if predecessor == (
        "part_number_not_in_stock" if split.startswith("part_number_") else "no_results") else predecessor
    assert result.structured_content == content
    assert day()["reasons"] == {"miss": {expected: 1}}


async def test_in_stock_mpn_min_stock_reason(monkeypatch):
    from test_usage_reasons import offline

    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=Clock()))
    with offline():
        async with Client(server.mcp) as client:
            row = server.get_db()._conn.execute(
                "SELECT mpn FROM components WHERE mpn LIKE 'LM358%' AND stock >= 10 "
                "AND stock < 1000000 LIMIT 1").fetchone()
            if row is None:
                pytest.skip("No stocked LM358 variant in this catalog")
            reply = await client.call_tool("jlc_search", {"query": row[0], "min_stock": 1000000, "strict": True})
            assert reply.structured_content["total"] == 0
            reason = server._empty_reason(reply.structured_content)
            assert reason == "blocked_by_min_stock"
            assert day()["reasons"]["jlc_search"] == {reason: 1}


@pytest.mark.parametrize("args,kwargs,kind", [
    (("p",), {"keyword": "k"}, "missing_argument"),
    (("p", "v"), {"keyword": "k", "SECRET": 1}, "unexpected_keyword_argument"),
    (("p", "v", "extra"), {"keyword": "k"}, "unexpected_positional_argument"),
    (("p", "v"), {"value": "again", "keyword": "k"}, "multiple_argument_values"),
    (("p", "v"), {}, "missing_keyword_only_argument"),
    ((), {"value": "v", "keyword": "k"}, "missing_positional_only_argument"),
], ids=["missing", "kw", "pos", "dup", "kwonly", "posonly"])
def test_validate_call_error_types_roundtrip(tmp_path, monkeypatch, args, kwargs, kind):
    @validate_call
    def tool(pos: str, /, value: str, *, keyword: str):
        return value

    with pytest.raises(PydanticValidationError) as caught:
        tool(*args, **kwargs)
    error = ValidationError("invalid arguments")
    error.__cause__ = caught.value
    clock = Clock()
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    stats.usage.tool_params = {"tool": {"pos", "value", "keyword"}}
    label = server._bad_request_reason("tool", {}, error)
    assert label.endswith(":" + kind)
    path = tmp_path / "usage.json"
    stats.usage.open(path)
    stats.usage.record_call("tool", "bad_request", 0, bad_request_reason=label)
    stats.usage.save()
    again = stats.UsageStats(clock=clock)
    again.open(path)
    assert again.summary()["days"][0]["bad_request_reasons"] == {"tool": {label: 1}}


def test_all_bad_request_replies_have_fixed_labels():
    for template, outcome in ERROR_REPLIES.items():
        if outcome == "bad_request":
            label = server._bad_request_reason("jlc_search", {"error": _render(template)}, None)
            assert label in stats.BAD_REQUEST_REASONS - {"other"}, template


@pytest.mark.parametrize("content", [
    {"status_counts": {}, "results": [{"error": "Invalid value: x"}]},
    {"counts": {"errors": 1}, "results": [{"error": "Invalid value: x"}]},
    {"parts": [{"error": "Invalid value: x"}], "what_is_recorded": "stock"},
], ids=["life", "parts", "history"])
def test_invalid_batches_are_separate_from_reasons(content):
    assert server._call_outcome(SimpleNamespace(structured_content=content)) == "bad_request"
    assert server._bad_request_reason("tool", content, None) == "all_inputs_invalid"


async def test_unknown_tool_is_bounded():
    mcp = FastMCP("unknown")
    mcp.add_middleware(server.UsageStatsMiddleware())
    stats.usage.tools = set()
    async with Client(mcp) as client:
        await client.call_tool("SECRET", {}, raise_on_error=False)
    assert day()["bad_request_reasons"] == {"unknown": {"unknown_tool": 1}}
    assert "SECRET" not in json.dumps(stats.usage.summary())


async def test_real_mouser_miss_shape():
    client = MouserClient(api_key="key")
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json={"Errors": [], "SearchResults": {"NumberOfResult": 0, "Parts": []}})))
    try:
        reply = await client.get_part("ABC123XYZ")
    finally:
        await client.close()
    assert reply["results"] == [] and reply["total"] == 0 and reply["not_found"] == ["ABC123XYZ"]
    assert server._empty_reason(reply) == "part_not_found"
    assert server._empty_reason({**reply, "not_sent": {"ABC123XYZ": "value_or_placeholder"}}) == "not_sent"


@pytest.mark.parametrize("result,label", [
    (SimpleNamespace(status_code=200), "2xx"), (SimpleNamespace(status_code=302), "3xx"),
    (SimpleNamespace(status_code=404), "4xx"), (SimpleNamespace(status_code=429), "429"),
    (SimpleNamespace(status_code=503), "5xx"), (WaferHTTPError(404, "url"), "4xx"),
    (WaferHTTPError(503, "url"), "5xx"), (RateLimited("url"), "429"),
    (WaferTimeout("url", 1), "timeout"), (TimeoutError(), "timeout"),
    (ConnectionFailed("url", "reason"), "connection"), (EmptyResponse("url", 200), "connection"),
    (ChallengeDetected("waf", "url", 403), "challenge"), (RequestBlocked("waf", "url", 403), "challenge"),
    (ResponseTooLarge("url", 2, 1), "too_large"), (RuntimeError("secret"), "other_error"),
    (httpx.ReadTimeout("url"), "timeout"), (httpx.ConnectError("url"), "connection"),
    (asyncio.CancelledError(), "cancelled"),
    (WaferResponse(status_code=200, headers={}, url="url", challenge_type="waf"), "challenge"),
    (WaferResponse(status_code=403, headers={}, url="url", challenge_type="waf"), "challenge"),
], ids=["ok", "redirect", "4xx", "429", "5xx", "http4", "http5", "rate", "wafer-time", "time",
        "conn", "empty", "waf", "block", "large", "other", "http-time", "http-conn", "cancel", "waf200", "waf403"])
@pytest.mark.parametrize("source", stats.UPSTREAM_SOURCES,
                         ids=["jlc", "lcsc", "products", "components", "pads", "cse", "dk"])
async def test_upstream_classes(result, label, source, monkeypatch):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=Clock()))

    async def request():
        if isinstance(result, BaseException):
            raise result
        return result

    if isinstance(result, BaseException):
        with pytest.raises(type(result)):
            await _sent(source, request())
    else:
        assert await _sent(source, request()) is result
    counts = day()
    assert counts["upstream_status"] == {source: {label: 1}}
    assert sum(counts["upstream_status"][source].values()) == counts["upstream"][source]["sent"] == 1


async def test_status_counting_failure_does_not_change_request(monkeypatch):
    def broken(*args):
        raise RuntimeError("count failed")

    monkeypatch.setattr(stats.usage, "record_upstream_status", broken)

    async def request():
        return "reply"

    assert await _sent("cse", request()) == "reply"


async def test_digikey_sent_sibling_cancellation(monkeypatch):
    from pcbparts_mcp.digikey_site import DigiKeySite

    clock = Clock()
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    site = DigiKeySite(clock=clock)
    started = asyncio.Event()

    async def pending():
        started.set()
        await asyncio.Event().wait()

    async def failing():
        await started.wait()
        raise ConnectionFailed("url", "test failure")

    with pytest.raises(ConnectionFailed):
        await site._all([_sent("digikey", pending()), _sent("digikey", failing())])
    counts = day()
    assert counts["upstream_status"] == {"digikey": {"connection": 1, "cancelled": 1}}
    assert sum(counts["upstream_status"]["digikey"].values()) == counts["upstream"]["digikey"]["sent"] == 2


@pytest.mark.parametrize("method", ["search", "model"])
async def test_cse_sent_cancellation(monkeypatch, method):
    from pcbparts_mcp import cse

    clock = Clock()
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    monkeypatch.setattr(cse, "CSE_USER", "user")
    monkeypatch.setattr(cse, "CSE_PASS", "pass")
    started = asyncio.Event()

    async def pending(request):
        started.set()
        await asyncio.Event().wait()

    client = cse.CSEClient(clock=clock)
    client._http = httpx.AsyncClient(transport=httpx.MockTransport(pending))
    task = asyncio.create_task(client.search("TEST1") if method == "search" else client.get_kicad(part_id=1))
    try:
        await started.wait()
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        await client.close()
    counts = day()
    assert counts["upstream_status"] == {"cse": {"cancelled": 1}}
    assert sum(counts["upstream_status"]["cse"].values()) == counts["upstream"]["cse"]["sent"] == 1


def test_failed_minutes_fake_clock(caplog):
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    usage.record_call("jlc_get_part", "failed", 1, reason="jlcpcb_unavailable")
    usage.record_call("jlc_get_part", "failed", 1, reason="jlcpcb_unavailable")
    usage.record_call("jlc_get_part", "bad_request", 1)
    with caplog.at_level(logging.WARNING, logger="pcbparts_mcp.stats"):
        usage.flush_failed_calls()
        assert caplog.messages == []
        clock.advance(60)
        usage.record_call("cse_get_kicad", "failed", 1, reason="cse_invalid_zip")
        usage.flush_failed_calls()
        assert caplog.messages == [
            "Failed tool calls 2026-10-17 21:15 UTC: jlc_get_part jlcpcb_unavailable 2"]
        usage.flush_failed_calls(shutdown=True)
        usage.flush_failed_calls(shutdown=True)
    assert caplog.messages[-1] == "Failed tool calls 2026-10-17 21:16 UTC: cse_get_kicad cse_invalid_zip 1"
    assert len(caplog.messages) == 2 and not usage._failed_minutes


@pytest.mark.parametrize("args,reason", [
    ({"query": "ZZQ9981XK"}, "no_results_part_number"),
    ({"query": "purple impossible widgets"}, "no_results_words"),
    ({"query": "ZZQ9981XK", "package": "0402"}, "no_results_filtered"),
    ({"manufacturer": "TI"}, "no_results_filtered"),
    ({"manufacturers": ["TI"]}, "no_results_filtered"),
    ({"category_id": 1}, "no_results_filtered"),
    ({"subcategory_id": 1}, "no_results_filtered"),
    ({"library_type": "all"}, "no_results_filtered"),
    ({"packages": ["0402"]}, "no_results_filtered"),
], ids=["mpn", "words", "package", "maker", "makers", "category", "subcat", "library", "packages"])
async def test_stock_empty_split_leaves_reply_unchanged(monkeypatch, args, reason):
    reply = {"results": [], "total": 0}

    class Live:
        async def search(self, **kwargs):
            return reply.copy()

    monkeypatch.setattr(server, "_client", Live())
    monkeypatch.setattr(server, "get_db", lambda: SimpleNamespace(
        mpns_containing=lambda fragment: [], upstream_packages=lambda wanted: wanted))
    context = SimpleNamespace(message=SimpleNamespace(name="jlc_stock_check"))

    async def next_call(context):
        return SimpleNamespace(structured_content=await server.jlc_stock_check(**args))

    result = await server.UsageStatsMiddleware().on_call_tool(context, next_call)
    assert result.structured_content == reply
    assert day()["reasons"] == {"jlc_stock_check": {reason: 1}}
    assert stats.call_notes.get() is None


async def test_stock_existing_hint_reason_wins(monkeypatch):
    class Live:
        async def search(self, **kwargs):
            return {"results": [], "total": 0, "hint": "No part C1 with stock >= 10"}

    monkeypatch.setattr(server, "_client", Live())
    token = stats.call_notes.set({})
    try:
        result = await server.jlc_stock_check(query="C1", package=None)
        assert server._empty_reason(result) == "stock_below_minimum"
        assert stats.call_notes.get() == {}
    finally:
        stats.call_notes.reset(token)


async def test_sold_out_label_only_real_offloaded_search(monkeypatch):
    from threading import current_thread, main_thread
    from test_usage_reasons import offline

    with offline():
        async with Client(server.mcp) as client:
            db = server.get_db()
            seen = []

            def sold_out(mpn):
                assert current_thread() is not main_thread()
                assert stats.call_notes.get() is not None
                seen.append(mpn)
                return [{"gone": True}]

            monkeypatch.setattr(db, "get_sold_out_by_mpn", sold_out)
            first = await client.call_tool("jlc_search", {"query": "ZZQ9981XK"})
            assert day()["reasons"]["jlc_search"] == {"part_number_sold_out": 1}
            monkeypatch.setattr(db, "get_sold_out_by_mpn", lambda mpn: [])
            second = await client.call_tool("jlc_search", {"query": "ZZQ9981XK"})
            assert day()["reasons"]["jlc_search"] == {"part_number_sold_out": 1, "part_number_unknown": 1}

            def broken(mpn):
                raise RuntimeError("label lookup failed")

            monkeypatch.setattr(db, "get_sold_out_by_mpn", broken)
            third = await client.call_tool("jlc_search", {"query": "ZZQ9981XK"})
            assert day()["reasons"]["jlc_search"]["part_number_not_in_stock"] == 1
            assert first.structured_content == second.structured_content == third.structured_content
            assert first.content == second.content == third.content and not first.is_error
            assert seen == ["ZZQ9981XK"]


async def test_minute_task_flushes_failed_calls(monkeypatch, caplog):
    clock = Clock()
    usage = stats.UsageStats(clock=clock)
    monkeypatch.setattr(stats, "usage", usage)
    usage.record_call("jlc_get_part", "failed", 1, reason="jlcpcb_unavailable")
    clock.advance(60)
    flushed = asyncio.Event()
    ticks = asyncio.Queue()
    ticks.put_nowait(None)
    original = usage.flush_failed_calls

    def flush():
        original()
        flushed.set()

    async def sleep(seconds):
        assert seconds == 60
        await ticks.get()

    monkeypatch.setattr(usage, "flush_failed_calls", flush)
    monkeypatch.setattr(server, "asyncio", SimpleNamespace(**(vars(asyncio) | {"sleep": sleep})))
    with caplog.at_level(logging.WARNING, logger="pcbparts_mcp.stats"):
        task = asyncio.create_task(server._every_minute())
        try:
            await flushed.wait()
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
    assert "Failed tool calls 2026-10-17 21:15 UTC: jlc_get_part jlcpcb_unavailable 1" in caplog.messages


async def test_shutdown_flushes_failed_minute(monkeypatch, caplog):
    usage = stats.UsageStats(clock=Clock())
    monkeypatch.setattr(stats, "usage", usage)
    with caplog.at_level(logging.WARNING, logger="pcbparts_mcp.stats"):
        async with Client(server.mcp):
            usage.record_call("jlc_get_part", "failed", 1, reason="jlcpcb_unavailable")
    assert "Failed tool calls 2026-10-17 21:15 UTC: jlc_get_part jlcpcb_unavailable 1" in caplog.messages


@pytest.mark.parametrize("error,label", [(httpx.ReadTimeout("url"), "timeout"),
                                         (httpx.ConnectError("url"), "connection"),
                                         (None, "5xx")], ids=["timeout", "conn", "http5"])
async def test_cse_status_search_and_model(monkeypatch, error, label):
    from pcbparts_mcp import cse

    monkeypatch.setattr(cse, "CSE_RATE_LIMIT", 0)
    monkeypatch.setattr(cse, "CSE_USER", "user")
    monkeypatch.setattr(cse, "CSE_PASS", "pass")

    def reply(request):
        if error:
            raise error
        return httpx.Response(503)

    client = cse.CSEClient()
    client._http = httpx.AsyncClient(transport=httpx.MockTransport(reply))
    try:
        with pytest.raises(ValueError):
            await client.search("ZZQ9981XK")
        result = await client.get_kicad(part_id=1)
        assert result["error"].startswith("CSE model download failed")
    finally:
        await client.close()
    assert day()["upstream_status"] == {"cse": {label: 2}}
    assert day()["upstream"]["cse"]["sent"] == 2


async def test_real_server_registers_parameters_and_bad_arguments():
    async with Client(server.mcp) as client:
        tools = await server.mcp.list_tools(run_middleware=False)
        assert stats.usage.tool_params == {tool.name: set(tool.parameters["properties"]) for tool in tools}
        for args in ({}, {"part_number": []}, {"part_number": "P1", "SECRET": 1}):
            result = await client.call_tool("digikey_get_part", args, raise_on_error=False)
            assert result.is_error
        assert day()["bad_request_reasons"]["digikey_get_part"] == {
            "arg:part_number:missing_argument": 1, "arg:part_number:string_type": 1,
            "arg:unknown_argument:unexpected_keyword_argument": 1}
        assert day()["reasons"] == {}
