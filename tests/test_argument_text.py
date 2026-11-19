"""JSON-string tool arguments holding text that can't be encoded as UTF-8 (0.10.0).

The MCP layer refuses a lone surrogate in a request, but our own json.loads of a JSON-string
argument turns an escaped one ("\\ud800" inside the string) into one. Every such argument is read
through server._loads_argument: the call gets the tool's usual argument error (bad_request), which
shows the text escaped, never raw (a reply holding a lone surrogate can't be serialised). The
batch tools (jlc_get_parts, part_lifecycle) answer it as that row's error instead (test_get_parts.py,
test_part_lifecycle.py). No network, no catalog: each call is refused before either is used."""

import ast
import json
from pathlib import Path

import pytest
from fastmcp import Client

import pcbparts_mcp.server as server

CALLS = {
    "search_packages": ("jlc_search", {"query": "capacitor", "packages": '["0805", "SOT\\ud800"]'}),
    "search_filters": ("jlc_search", {"query": "capacitor",
                                      "spec_filters": '[{"name": "Capacitance", "op": "=", "value": "1u\\udc00F"}]'}),
    "search_filter_key": ("jlc_search", {"query": "capacitor",
                                         "spec_filters": '[{"na\\ud800me": "Capacitance", "op": "=", "value": "1uF"}]'}),
    "stock_packages": ("jlc_stock_check", {"query": "capacitor", "packages": '["SOT\\ud800"]'}),
    "stock_makers": ("jlc_stock_check", {"query": "capacitor", "manufacturers": '["T\\ud800I"]'}),
    "history": ("jlc_stock_history", {"lcsc": '["C7950", "C1\\ud800"]'}),
    "sensor_measure": ("sensor_recommend", {"measure": '["temperature", "temp\\ud800"]'}),
    "board_tag": ("board_search", {"tag": '["usb\\ud800"]'}),
}


@pytest.fixture
def no_databases(monkeypatch):
    def refuse():
        raise AssertionError("a database was opened for an argument that should have been refused")

    class NoRequests:  # jlc_stock_check's JLCPCB client: never asked
        def __getattr__(self, name):
            raise AssertionError("a JLCPCB request was started for an argument that should have been refused")

    for name in ("get_history_db", "get_sensor_db", "get_boards_db"):
        monkeypatch.setattr(server, name, refuse)
    monkeypatch.setattr(server, "get_db", lambda: object())  # jlc_search takes it before parsing; never used
    monkeypatch.setattr(server, "_client", NoRequests())


@pytest.mark.parametrize("case", list(CALLS), ids=list(CALLS))
async def test_refused_as_an_argument_error(no_databases, case):
    tool, arguments = CALLS[case]
    reply = await getattr(server, tool)(**arguments)
    assert reply["error"].startswith("Invalid ") and server._error_kind(reply["error"]) == "bad_request"
    assert "\\ud800" in reply["error"] or "\\udc00" in reply["error"]  # shown escaped
    json.dumps(reply, ensure_ascii=False).encode("utf-8")  # nothing raw in the reply


async def test_through_the_mcp_layer():
    async with Client(server.mcp) as client:
        result = await client.call_tool("sensor_recommend", {"measure": '["temp\\ud800"]'}, raise_on_error=False)
    assert not result.is_error and result.structured_content["error"].startswith("Invalid measure: ")


def test_a_real_pair_is_text():
    assert server._loads_argument('["\\ud83d\\ude00 LED"]') == ["\U0001f600 LED"]


def test_only_the_batch_tools_check_rows_themselves():
    assert server._loads_argument('[{"mpn": "LM358\\ud800"}]', check_text=False) == [{"mpn": "LM358\ud800"}]
    with pytest.raises(ValueError, match=r"'LM358\\ud800' holds an unpaired surrogate escape"):
        server._loads_argument('[{"mpn": "LM358\\ud800"}]')


@pytest.mark.parametrize("tool,arguments", [
    ("jlc_stock_history", {"lcsc": "[[1]]"}),
    ("jlc_stock_check", {"query": "capacitor", "packages": "[[1]]"}),
], ids=["history", "stock"])
async def test_nesting_past_pythons_limit_is_invalid_json(no_databases, monkeypatch, tool, arguments):
    """json.loads raises RecursionError past Python's nesting limit; uncaught, it failed the call."""
    def too_deep(text):
        raise RecursionError("maximum recursion depth exceeded while decoding a JSON array")

    monkeypatch.setattr(server.json, "loads", too_deep)
    reply = await getattr(server, tool)(**arguments)
    assert server._error_kind(reply["error"]) == "bad_request" and reply["error"].startswith("Invalid ")


def test_every_json_string_argument_goes_through_the_helper():
    """server.py's own json.loads runs only in _loads_argument (tool arguments) and the rate-limit
    middleware's peek at a request body (the method, never echoed)."""
    tree = ast.parse((Path(server.__file__)).read_text(encoding="utf-8"))
    callers = set()
    for function in ast.walk(tree):
        if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(function):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "loads"
                        and isinstance(node.func.value, ast.Name) and node.func.value.id == "json"):
                    callers.add(function.name)
    assert callers == {"_loads_argument", "__call__"}


BIG = "1" * 5000  # past Python's 4,300-digit limit for converting an integer's text


@pytest.mark.parametrize("tool,arguments", [
    ("jlc_get_parts", {"parts": f'["C7950", {BIG}]'}),
    ("part_lifecycle", {"parts": f'["LM358P", {BIG}]'}),
    ("sensor_recommend", {"measure": f"[{BIG}]"}),
    ("board_search", {"tag": f"[{BIG}]"}),
], ids=["get_parts", "lifecycle", "sensor", "board"])
async def test_an_integer_past_the_digit_limit_is_invalid_json(monkeypatch, tool, arguments):
    """json.loads raises a plain ValueError (not JSONDecodeError) for an integer over Python's digit
    limit, which failed these calls with isError. It's invalid JSON like any other: an argument error
    for the parts lists; measure and tag are then taken as plain text, as for other invalid JSON."""
    monkeypatch.setattr(server, "_mouser_client", object())  # part_lifecycle parses only with a distributor

    class Unknown:  # sensor and board databases: the text is no measure or tag they know
        def search(self, **kwargs):
            value = kwargs.get("measure") or kwargs.get("tag")
            assert isinstance(value, str) and value.startswith("[1111")
            error = "Unsupported value for measure: '{}'" if kwargs.get("measure") else "Unsupported tag: '{}'"
            return {"error": error.format(value[:20]), "results": [], "total": 0}  # as the real ones say

        def get_tag_consensus(self, tag):
            return None

    monkeypatch.setattr(server, "get_sensor_db", Unknown)
    monkeypatch.setattr(server, "get_boards_db", Unknown)
    reply = await getattr(server, tool)(**arguments)
    if tool in ("jlc_get_parts", "part_lifecycle"):
        assert reply["error"] == "Invalid parts: not a valid JSON array"
    else:
        assert reply["error"].startswith("Unsupported ")
    assert server._error_kind(reply["error"]) == "bad_request"
