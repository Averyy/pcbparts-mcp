"""One line instead of a traceback for what the MCP SDK (mcp 1.30) logs about callers, not about
this server. Each record keeps its logger and time; only its text, level (WARNING) and traceback
change, and anything that doesn't match exactly is left as it is.

- A client that disconnects before its request body is complete: streamable_http logs "Error
  handling POST request" with starlette's ClientDisconnect (about 30 lines), forwards the error
  into the request's session, where lowlevel.server logs "Received exception from stream: " (the
  error's text, empty here) and sends a log notification into the transport that has just closed,
  so streamable_http_manager logs "Stateless session crashed" with anyio's ClosedResourceError
  (about 30 more). Seen 17 times in 19 hours on prod (2026-11-21).
- A request whose method the SDK doesn't know, such as the 2026-07-28 spec's server/discover
  (the SDK answers -32602): shared/session.py logs "Failed to validate request: 31 validation
  errors for ClientRequest" on the root logger, about 95 lines. Seen 16 times in 19 hours. A known
  method with bad parameters keeps its full message: that one says what was wrong.

install() runs once at startup (server.main); it adds logger filters, so every handler (console
and the persistent file) gets the short line.
"""

from __future__ import annotations

import logging
import re

import anyio

try:  # starlette is a dependency of the SDK; guarded so a rename can't stop the server starting
    from starlette.requests import ClientDisconnect
except ImportError:  # pragma: no cover
    ClientDisconnect = None  # type: ignore[assignment,misc]

_CLOSED = (anyio.ClosedResourceError, anyio.BrokenResourceError)
def _known_methods() -> frozenset[str]:
    """Every method the installed SDK's ClientRequest accepts (empty if its shape changed: then
    nothing is shortened)."""
    try:
        from typing import get_args

        from mcp.types import ClientRequest
        members = get_args(ClientRequest.model_fields["root"].annotation)
        return frozenset(value for member in members for value in get_args(member.model_fields["method"].annotation))
    except Exception:  # pragma: no cover - an SDK whose types differ
        return frozenset()


_KNOWN_METHODS = _known_methods()
_VALIDATION = re.compile(r"^Failed to validate request: (\d+) validation errors? for ClientRequest\b")
# Every request type's "method" error repeats the method asked: "...method\n  Input should be 'ping'
# [type=literal_error, input_value='server/discover', input_type=str]"
_METHOD = re.compile(r"\.method\n\s+Input should be [^\n]*?input_value='([^'\n]{1,100})'")


def _leaves(error: BaseException) -> list[BaseException]:
    if isinstance(error, BaseExceptionGroup):
        return [leaf for inner in error.exceptions for leaf in _leaves(inner)]
    return [error]


def _shorten(record: logging.LogRecord, text: str) -> None:
    record.msg, record.args = text, ()
    record.exc_info = record.exc_text = record.stack_info = None
    record.levelno, record.levelname = logging.WARNING, logging.getLevelName(logging.WARNING)


class _PostDisconnect(logging.Filter):
    """mcp.server.streamable_http: "Error handling POST request" caused by ClientDisconnect."""

    def filter(self, record: logging.LogRecord) -> bool:
        error = record.exc_info[1] if record.exc_info else None
        if (ClientDisconnect is not None and record.msg == "Error handling POST request"
                and isinstance(error, ClientDisconnect)):
            _shorten(record, "Client disconnected before sending its whole request "
                             "(mcp: Error handling POST request, ClientDisconnect)")
        return True


class _ForwardedDisconnect(logging.Filter):
    """mcp.server.lowlevel.server: "Received exception from stream: " with no text, the forwarded
    ClientDisconnect (an error with a message keeps its line and level)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.getMessage() == "Received exception from stream: " and not record.exc_info:
            _shorten(record, "Received exception from stream with no message "
                             "(the request's own error is logged just before; usually a client disconnect)")
        return True


class _SessionGone(logging.Filter):
    """mcp.server.streamable_http_manager: "Stateless session crashed" when every error in it is a
    send into a transport its client had already closed."""

    def filter(self, record: logging.LogRecord) -> bool:
        error = record.exc_info[1] if record.exc_info else None
        if record.msg == "Stateless session crashed" and error is not None:
            leaves = _leaves(error)
            if leaves and all(isinstance(leaf, _CLOSED) for leaf in leaves):
                kind = type(leaves[0]).__name__
                _shorten(record, f"Stateless session ended after its client disconnected "
                                 f"(mcp: Stateless session crashed, {kind})")
        return True


class _UnknownRequest(logging.Filter):
    """root: shared/session.py's "Failed to validate request: N validation errors for
    ClientRequest" for a method the SDK doesn't know, as one line naming it."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name != "root" or not isinstance(record.msg, str) or not _KNOWN_METHODS:
            return True
        if not (count := _VALIDATION.match(record.msg)) or not (method := _METHOD.search(record.msg)):
            return True
        if method.group(1) in _KNOWN_METHODS:
            return True
        _shorten(record, f"Failed to validate request: method {method.group(1)!r}, {count.group(1)} validation "
                         "errors for ClientRequest (answered -32602)")
        return True


_FILTERS = {
    "mcp.server.streamable_http": _PostDisconnect,
    "mcp.server.lowlevel.server": _ForwardedDisconnect,
    "mcp.server.streamable_http_manager": _SessionGone,
    "": _UnknownRequest,  # the root logger: session.py calls logging.warning()
}


def install() -> None:
    """Add the filters (once per logger, so calling again changes nothing)."""
    for name, kind in _FILTERS.items():
        target = logging.getLogger(name)
        if not any(isinstance(existing, kind) for existing in target.filters):
            target.addFilter(kind())
