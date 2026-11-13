"""HTTP_HOST picks the server's bind address (0.9.1, #23); the default stays 0.0.0.0."""

import logging
import os
import subprocess
import sys

import pytest


def _configured_host(value: str | None) -> str:
    """config.HTTP_HOST in a fresh interpreter, so the module reads the env var at import."""
    env = {k: v for k, v in os.environ.items() if k != "HTTP_HOST"}
    if value is not None:
        env["HTTP_HOST"] = value
    out = subprocess.run(
        [sys.executable, "-c", "import pcbparts_mcp.config as c; print(c.HTTP_HOST)"],
        env=env, capture_output=True, text=True, check=True,
    )
    return out.stdout.rstrip("\n")  # only print's newline: spaces in the value must show


@pytest.mark.parametrize(("value", "expected"), [
    (None, "0.0.0.0"),
    ("", "0.0.0.0"),
    ("  ", "0.0.0.0"),
    ("127.0.0.1", "127.0.0.1"),
    ("::1", "::1"),
    ("::", "::"),
    (" 192.168.1.20 ", "192.168.1.20"),
], ids=["unset", "empty", "blank", "ipv4-loopback", "ipv6-loopback", "ipv6-any", "padded"])
def test_http_host_setting(value, expected):
    assert _configured_host(value) == expected


def test_main_binds_to_http_host(monkeypatch):
    import uvicorn

    from pcbparts_mcp import server

    calls = []
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: calls.append(kwargs))
    monkeypatch.setattr(server, "HTTP_HOST", "::1")
    package_logger = logging.getLogger("pcbparts_mcp")
    access_logger = logging.getLogger("uvicorn.access")
    level, filters = package_logger.level, list(access_logger.filters)
    try:
        server.main()
    finally:  # main() sets up logging for a real run; leave it as the other tests expect
        package_logger.setLevel(level)
        access_logger.filters = filters
    assert len(calls) == 1
    assert calls[0]["host"] == "::1"
    assert calls[0]["port"] == server.HTTP_PORT
