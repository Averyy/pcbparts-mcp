"""Offline checks for the load-test's busy classification and verification mode."""

import asyncio
import importlib.util
import json
import types
from pathlib import Path

import httpx
import pytest

SPEC = importlib.util.spec_from_file_location("load_test", Path(__file__).resolve().parents[1] / "scripts/load_test.py")
load = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(load)


@pytest.mark.parametrize("reason,wait,header,busy,failed", [
    ("server_busy", 2, "2", 1, 0), ("per_ip_rate_limit", 60, "60", 0, 1),
    ("server_busy", 0, "0", 0, 1), ("server_busy", 2, "3", 0, 1),
], ids=["busy", "ip", "zero", "mismatch"])
async def test_busy_counted_apart_from_errors(monkeypatch, reason, wait, header, busy, failed):
    now = [0.0]
    monkeypatch.setattr(load, "time", types.SimpleNamespace(perf_counter=lambda: now[0]))

    def handle(request):
        now[0] += 0.125
        method = json.loads(request.content)["method"]
        if method == "tools/call":
            return httpx.Response(429, json={"reason": reason, "retry_after": wait}, headers={"Retry-After": header})
        return httpx.Response(202 if method.startswith("notifications/") else 200, json={})

    step = load.Step(1000)
    async with httpx.AsyncClient(base_url="http://localhost", transport=httpx.MockTransport(handle)) as client:
        await load.mcp_call(client, {}, "jlc_search", {"query": "resistor"}, step)
    assert (step.busy, sum(step.failures.values()), step.ok) == (busy, failed, 0)
    assert step.latency == []  # busy latency never contaminates accepted-call p95
    assert step.busy_latency == ([0.125] if busy else [])


@pytest.mark.parametrize("case,expected", [("ok", True), ("slow", False), ("error", False),
                                         ("tool", False), ("skip", False), ("none", False)],
                         ids=["ok", "slow", "error", "tool", "skip", "none"])
def test_admission_summary(case, expected):
    step = load.Step(1000)
    step.started, step.ok, step.busy = 10, 6, 4
    step.latency = [0.5] * 6
    if case == "slow":
        step.latency[-1] = 3
    elif case == "error":
        step.failures["timeout"] = 1
    elif case == "tool":
        step.tool_errors = 1
    elif case == "skip":
        step.skipped = 1
    elif case == "none":
        step.ok = 0
        step.busy = 10
        step.latency = []
    result = load.summary(step, 60, 0, 2)
    assert result["admission_ok"] is expected
    assert result["sustained"] is False  # the old mode still requires accepting the offered rate


@pytest.mark.parametrize("errors,expected", [(0, True), (1, True), (2, False), (100, False)],
                         ids=["none", "one", "two", "all"])
def test_sustained_needs_answers_not_tool_errors(errors, expected):
    """The default mode: a step whose every call came back as a tool error (isError, counted in ok)
    was sustained. Up to 1% of its answered calls may be tool errors (odd queries)."""
    step = load.Step(100)
    step.started = step.ok = 100
    step.tool_errors = errors
    step.latency = [0.5] * 100
    assert load.summary(step, 60, 0, 2)["sustained"] is expected


ERROR_TEXT = json.dumps({"error": "Board search failed"})
TOOL_RESULTS = {
    "structured": ({"content": [{"type": "text", "text": ERROR_TEXT}],
                    "structuredContent": {"error": "Board search failed"}, "isError": False}, True),
    "text_only": ({"content": [{"type": "text", "text": ERROR_TEXT}], "isError": False}, True),
    "is_error": ({"content": [{"type": "text", "text": "boom"}], "isError": True}, True),
    "answer": ({"content": [{"type": "text", "text": "{}"}], "structuredContent": {"results": [], "error": None},
                "isError": False}, False),
    "row_errors": ({"structuredContent": {"results": [{"input": "DNP", "error": "Invalid part"}],
                                          "counts": {"error": 1}}, "isError": False}, False),
    "plain_text": ({"content": [{"type": "text", "text": "error: not JSON"}], "isError": False}, False),
}


@pytest.mark.parametrize("case", list(TOOL_RESULTS), ids=list(TOOL_RESULTS))
async def test_structured_error_replies_are_tool_errors(monkeypatch, case):
    """Only isError counted as a tool error, so a structured {"error": ...} reply with isError false
    (board_search's, most tools') counted as an answer and let a failing server pass both modes. A
    part's own error inside results is still an answer."""
    result, is_error = TOOL_RESULTS[case]
    monkeypatch.setattr(load, "time", types.SimpleNamespace(perf_counter=lambda: 0.0))

    def handle(request):
        message = json.loads(request.content)
        if message["method"] == "tools/call":
            return httpx.Response(200, json={"jsonrpc": "2.0", "id": 2, "result": result})
        return httpx.Response(202 if message["method"].startswith("notifications/") else 200, json={})

    step = load.Step(100)
    async with httpx.AsyncClient(base_url="http://localhost", transport=httpx.MockTransport(handle)) as client:
        for _ in range(100):
            step.started += 1
            await load.mcp_call(client, {}, "board_search", {"query": "esp32"}, step)
    assert (step.ok, step.tool_errors) == (100, 100 if is_error else 0)
    summary = load.summary(step, 60, 0, 2)
    assert summary["sustained"] is not is_error  # the default mode
    step.busy, step.started = 5, 105  # --expect-busy: busy refusals don't excuse tool errors
    assert load.summary(step, 60, 0, 2)["admission_ok"] is not is_error


@pytest.mark.parametrize("case,expected", [("busy", 0), ("no_busy", 2), ("slow", 2), ("upstream", 3)],
                         ids=["busy", "none", "slow", "upstream"])
async def test_expect_busy_exit_and_upstream_guard(monkeypatch, case, expected):
    class Inputs:
        by_tool = {"jlc_search": [{"query": "resistor"}]}
        lcsc = []
        mpns = ["LM358"]

        def __init__(self, rng):
            self.lcsc = []

    async def warmup(*args):
        return {"structuredContent": {"results": [{"lcsc": f"C{i}"} for i in range(50)]}}

    async def step(*args):
        result = load.Step(1000)
        result.started = 10
        result.busy = 0 if case == "no_busy" else 4
        result.ok = 10 - result.busy
        result.latency = [3 if case == "slow" else 0.5] * result.ok
        return result, 0

    samples = iter([{}, {}, {"upstream.jlcpcb": 1} if case == "upstream" else {}, {}])

    async def sent(*args):
        return next(samples)

    async def sleep(seconds):
        pass

    monkeypatch.setattr(load, "Inputs", Inputs)
    monkeypatch.setattr(load, "mcp_call", warmup)
    monkeypatch.setattr(load, "run_step", step)
    monkeypatch.setattr(load, "upstream_sent", sent)
    monkeypatch.setattr(load.asyncio, "sleep", sleep)
    monkeypatch.setattr(load.sys, "argv", ["load_test.py", "--expect-busy", "--rates", "1000", "--pause", "0"])
    assert await load.main() == expected


def test_busy_mode_does_not_bypass_database_only_guard():
    with pytest.raises(SystemExit, match="could send a live request"):
        load.check_database_only("jlc_get_part", {"lcsc": "C1"})


@pytest.mark.parametrize("url,allow_remote,ok", [
    ("http://127.0.0.1:18080", False, True), ("http://localhost:18080", False, True),
    ("http://[::1]:18080", False, True),
    ("https://PCBPARTS.DEV/mcp", False, False), ("https://pcbparts.dev./mcp", True, False),
    ("https://www.pcbparts.dev", True, False), ("http://192.168.1.20:18080", False, False),
    ("http://192.168.1.20:18080", True, True), ("not a url", True, False),
], ids=["v4", "localhost", "v6", "upper", "dot", "sub", "lan", "lan-ok", "junk"])
def test_target_guard(url, allow_remote, ok):
    """Only this machine unless --allow-remote, and never pcbparts.dev in any spelling."""
    if ok:
        load.check_target(url, allow_remote)
    else:
        with pytest.raises(SystemExit):
            load.check_target(url, allow_remote)


def test_main_refuses_prod_before_any_request(monkeypatch):
    monkeypatch.setattr(load.sys, "argv", ["load_test.py", "--url", "https://PcbParts.dev", "--allow-remote"])

    def no_requests(*args, **kwargs):
        pytest.fail("sent a request")

    monkeypatch.setattr(load, "upstream_sent", no_requests)
    with pytest.raises(SystemExit, match="never pcbparts.dev"):
        asyncio.run(load.main())
