"""0.10.5: sdk_logs shortens what mcp 1.30 logs about callers (a client that disconnects mid-request,
a method the SDK doesn't know such as server/discover) to one WARNING line each, and leaves every
other record as it is. Reproduced on prod's logs (2026-11-21) and locally over a real socket; here
through a stateless FastMCP app, as in test_rate_limits. No network, no timing."""

import asyncio
import json
import logging
import subprocess
import sys

import anyio
import httpx
import pytest
from fastmcp import FastMCP
from mcp.types import ClientRequest
from pydantic import ValidationError
from starlette.requests import ClientDisconnect

from pcbparts_mcp import sdk_logs

HEADERS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
DISCOVER = {"jsonrpc": "2.0", "id": 7, "method": "server/discover",
            "params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
                                 "io.modelcontextprotocol/clientCapabilities": {}}}}


@pytest.fixture
def installed():
    sdk_logs.install()
    yield
    for name, kind in sdk_logs._FILTERS.items():
        target = logging.getLogger(name)
        for existing in [f for f in target.filters if isinstance(f, kind)]:
            target.removeFilter(existing)


def _app():
    mcp = FastMCP("t")

    @mcp.tool
    def ping() -> str:
        return "pong"

    return mcp.http_app(path="/mcp", transport="streamable-http", stateless_http=True)


def _mcp_records(caplog) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == "root" or r.name.startswith("mcp.")]


def _validation_error() -> ValidationError:
    with pytest.raises(ValidationError) as caught:
        ClientRequest.model_validate(DISCOVER)
    return caught.value


# --- through the app ---

async def test_server_discover_is_one_line_and_still_answered(installed, caplog):
    app = _app()
    with caplog.at_level(logging.WARNING):
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as c:
                reply = await c.post("/mcp", json=DISCOVER, headers=HEADERS)
    data = [json.loads(line[6:]) for line in reply.text.splitlines() if line.startswith("data: ")]
    assert reply.status_code == 200 and data == [
        {"jsonrpc": "2.0", "id": 7, "error": {"code": -32602, "message": "Invalid request parameters", "data": ""}}]
    lines = [(r.name, r.levelname, r.getMessage()) for r in _mcp_records(caplog)]
    assert len(lines) == 1
    name, level, message = lines[0]
    assert (name, level) == ("root", "WARNING") and "\n" not in message
    assert message.startswith("Failed to validate request: method 'server/discover', ")
    assert message.endswith(" validation errors for ClientRequest (answered -32602)")


async def test_client_disconnect_mid_body_is_short_lines_without_tracebacks(installed, caplog):
    app = _app()
    messages = [{"type": "http.request", "body": b'{"jsonrpc":', "more_body": True}, {"type": "http.disconnect"}]

    async def receive():
        return messages.pop(0) if messages else {"type": "http.disconnect"}

    async def send(message):
        pass

    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "POST", "scheme": "http",
             "path": "/mcp", "raw_path": b"/mcp", "query_string": b"", "root_path": "",
             "headers": [(b"host", b"localhost"), (b"accept", HEADERS["Accept"].encode()),
                         (b"content-type", b"application/json")],
             "client": ("127.0.0.1", 50000), "server": ("localhost", 80)}
    with caplog.at_level(logging.WARNING):
        async with app.router.lifespan_context(app):
            await app(scope, receive, send)
            for _ in range(20):  # let the request's session task log its end
                await asyncio.sleep(0)
    records = _mcp_records(caplog)
    assert records and all(r.levelname == "WARNING" and not r.exc_info and "\n" not in r.getMessage()
                           for r in records)
    assert "Client disconnected before sending its whole request (mcp: Error handling POST request, " \
           "ClientDisconnect)" in [r.getMessage() for r in records]


# --- the records as the SDK makes them ---

def test_each_shape_becomes_one_warning_line(installed, caplog):
    with caplog.at_level(logging.WARNING):
        try:
            raise ClientDisconnect()
        except ClientDisconnect:
            logging.getLogger("mcp.server.streamable_http").exception("Error handling POST request")
        logging.getLogger("mcp.server.lowlevel.server").error(
            f"Received exception from stream: {Exception(ClientDisconnect())}")
        try:
            raise BaseExceptionGroup("outer", [BaseExceptionGroup("inner", [anyio.ClosedResourceError()])])
        except BaseExceptionGroup:
            logging.getLogger("mcp.server.streamable_http_manager").exception("Stateless session crashed")
        logging.warning(f"Failed to validate request: {_validation_error()}")
    assert [(r.levelname, r.exc_info, r.getMessage()) for r in caplog.records] == [
        ("WARNING", None, "Client disconnected before sending its whole request "
                          "(mcp: Error handling POST request, ClientDisconnect)"),
        ("WARNING", None, "Received exception from stream with no message "
                          "(the request's own error is logged just before; usually a client disconnect)"),
        ("WARNING", None, "Stateless session ended after its client disconnected "
                          "(mcp: Stateless session crashed, ClosedResourceError)"),
        ("WARNING", None, f"Failed to validate request: method 'server/discover', "
                          f"{_validation_error().error_count()} validation errors for ClientRequest (answered -32602)"),
    ]


def test_other_records_are_left_alone(installed, caplog):
    with caplog.at_level(logging.WARNING):
        try:
            raise RuntimeError("our bug")
        except RuntimeError:
            logging.getLogger("mcp.server.streamable_http").exception("Error handling POST request")
            logging.getLogger("mcp.server.streamable_http_manager").exception("Stateless session crashed")
        try:
            raise BaseExceptionGroup("mixed", [anyio.ClosedResourceError(), ValueError("x")])
        except BaseExceptionGroup:
            logging.getLogger("mcp.server.streamable_http_manager").exception("Stateless session crashed")
        logging.getLogger("mcp.server.lowlevel.server").error("Received exception from stream: boom")
        logging.warning("Failed to validate request: 'NoneType' object has no attribute 'x'")
        logging.getLogger("pcbparts_mcp.server").warning("Failed to validate request: 3 validation errors for ClientRequest")
        with pytest.raises(ValidationError) as known:  # a method the SDK knows, with bad parameters
            ClientRequest.model_validate({"method": "tools/call", "params": {}})
        logging.warning(f"Failed to validate request: {known.value}")
    assert [(r.levelname, bool(r.exc_info)) for r in caplog.records] == [
        ("ERROR", True), ("ERROR", True), ("ERROR", True), ("ERROR", False), ("WARNING", False), ("WARNING", False),
        ("WARNING", False)]
    assert caplog.records[6].getMessage() == f"Failed to validate request: {known.value}"
    assert "CallToolRequest.params.name" in caplog.records[6].getMessage()
    assert caplog.records[3].getMessage() == "Received exception from stream: boom"
    assert caplog.records[4].getMessage() == "Failed to validate request: 'NoneType' object has no attribute 'x'"


def test_install_twice_adds_each_filter_once(installed):
    sdk_logs.install()
    for name, kind in sdk_logs._FILTERS.items():
        assert sum(isinstance(f, kind) for f in logging.getLogger(name).filters) == 1


def test_main_installs_them_for_the_console_and_the_log_file(tmp_path):
    # In its own process, as test_file_logging does: main() configures logging for a real run.
    # run() is replaced before main(): no socket or outside request.
    script = """
import logging
import sys
import anyio
import uvicorn
from starlette.requests import ClientDisconnect
from pcbparts_mcp import server
server.LOG_PATH = sys.argv[1]
def run(app, **options):
    try:
        raise ClientDisconnect()
    except ClientDisconnect:
        logging.getLogger("mcp.server.streamable_http").exception("Error handling POST request")
    try:
        raise BaseExceptionGroup("g", [anyio.ClosedResourceError()])
    except BaseExceptionGroup:
        logging.getLogger("mcp.server.streamable_http_manager").exception("Stateless session crashed")
uvicorn.run = run
server.main()
"""
    path = tmp_path / "application.log"
    done = subprocess.run([sys.executable, "-c", script, str(path)], capture_output=True, text=True,
                          encoding="utf-8", check=True)
    for text in (path.read_text(encoding="utf-8"), done.stderr):
        assert "Traceback" not in text and "ClientDisconnect)" in text and "ClosedResourceError)" in text
        assert "Client disconnected before sending its whole request" in text
        assert "Stateless session ended after its client disconnected" in text


async def test_fastmcps_invalid_arguments_line_keeps_five_problems_and_short_values(installed, caplog):
    """A request can hold 20,000 unknown names; the line names five and counts the rest (0.10.6)."""
    from fastmcp import Client
    mcp = FastMCP("t")

    @mcp.tool
    def ping(text: str = "") -> str:
        return "pong"

    arguments = {"text": "x" * 5000, **{f"name_{n}": "v" * 300 for n in range(50)}}
    with caplog.at_level(logging.WARNING, logger="fastmcp"):
        async with Client(mcp) as client:
            result = await client.call_tool("ping", arguments, raise_on_error=False)
    assert result.is_error
    lines = [r.getMessage() for r in caplog.records if r.getMessage().startswith("Invalid arguments for tool")]
    assert len(lines) == 1 and lines[0].endswith(" and 45 more") and len(lines[0]) < 2000
    assert "'name_0'" in lines[0] and "'name_5'" not in lines[0] and "v" * 101 not in lines[0]
