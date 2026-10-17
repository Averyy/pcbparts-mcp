"""Shared test setup."""

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp import stats


@pytest.fixture(autouse=True)
def _no_real_footprint_store(monkeypatch):
    """Tests that start the real server (its lifespan) must not open the stores that
    EASYEDA_STORE_PATH and CSE_STORE_PATH name, or the files DISTRIBUTOR_QUOTA_PATH and USAGE_STATS_PATH name: in
    the Docker image those are the live files on the volume. Nor may they build Mouser/DigiKey clients
    from credentials in the shell. Each test also counts usage afresh."""
    monkeypatch.setattr(server, "EASYEDA_STORE_PATH", "")
    monkeypatch.setattr(server, "CSE_STORE_PATH", "")
    monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", "")
    monkeypatch.setattr(server, "USAGE_STATS_PATH", "")
    for name in ("MOUSER_API_KEY", "DIGIKEY_CLIENT_ID", "DIGIKEY_CLIENT_SECRET"):
        monkeypatch.setattr(server, name, "")
    monkeypatch.setattr(stats, "usage", stats.UsageStats())
