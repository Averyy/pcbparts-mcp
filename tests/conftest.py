"""Shared test setup."""

import pytest

import pcbparts_mcp.server as server


@pytest.fixture(autouse=True)
def _no_real_footprint_store(monkeypatch):
    """Tests that start the real server (its lifespan) must not open the footprint store that
    EASYEDA_STORE_PATH names: in the Docker image that's the live store on the volume."""
    monkeypatch.setattr(server, "EASYEDA_STORE_PATH", "")
