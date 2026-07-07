"""Tests for #9: internal errors must not leak to anonymous clients.

Uses fastmcp's in-memory Client against the real server object, so the whole
server-side error path (including mask_error_details=True) is exercised.
Intentional user-facing errors are *returned* as dicts and must pass through
unmasked; *raised* internal exceptions must be masked.
"""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

import pcbparts_mcp.server as server

SECRET = "SECRET-INTERNAL sqlite3.OperationalError near /app/data/components.db"


class _RaisingClient:
    """Stands in for the JLCPCB client; close() so lifespan teardown doesn't choke."""

    def __init__(self, exc: Exception):
        self._exc = exc

    async def get_part(self, lcsc):
        raise self._exc

    async def close(self):
        pass


async def test_internal_exception_is_masked(monkeypatch):
    """A raised non-ValueError (internal bug) must reach the client without its message."""
    async with Client(server.mcp) as client:
        monkeypatch.setattr(server, "_client", _RaisingClient(RuntimeError(SECRET)))
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("jlc_get_part", {"lcsc": "C123"})
        assert "SECRET-INTERNAL" not in str(exc_info.value)
        assert "components.db" not in str(exc_info.value)


async def test_returned_error_dict_passes_through(monkeypatch):
    """Actionable errors are returned as dicts, so masking must not touch them."""
    async with Client(server.mcp) as client:
        monkeypatch.setattr(
            server, "_client",
            _RaisingClient(ValueError("JLCPCB rate limited — try again later")),
        )
        result = await client.call_tool("jlc_get_part", {"lcsc": "C123"})
        assert result.data["error"] == "JLCPCB rate limited — try again later"


async def test_validation_error_passes_through():
    """Bad input errors (returned dicts) stay informative under masking."""
    async with Client(server.mcp) as client:
        result = await client.call_tool("jlc_get_part", {})
        assert result.data["error"] == "Must provide either lcsc or mpn"
