"""Shared test setup."""

import pytest

import pcbparts_mcp.server as server


@pytest.fixture(autouse=True)
def _no_real_footprint_store(monkeypatch):
    """Tests that start the real server (its lifespan) must not open the footprint store that
    EASYEDA_STORE_PATH names, or the quota file DISTRIBUTOR_QUOTA_PATH names: in the Docker image
    those are the live files on the volume."""
    monkeypatch.setattr(server, "EASYEDA_STORE_PATH", "")
    monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", "")
