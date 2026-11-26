"""Shared test setup."""

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp import call_log, stats
from pcbparts_mcp.catalog_files import read_catalog, write_catalog


@pytest.fixture(autouse=True)
def _offline_wafer_transport(request, monkeypatch):
    """Unit tests cannot create a live transport, including on session retirement."""
    if request.node.get_closest_marker("integration") is not None:
        return
    import wreq
    import wreq.blocking
    from test_easyeda_critical_ch import _Transport

    class OfflineTransport(_Transport):
        def __init__(self, **kwargs):
            super().__init__(None)

        def request(self, *args, **kwargs):
            pytest.fail("Unit tests must supply an offline wafer response")

    monkeypatch.setattr(wreq, "Client", OfflineTransport)
    monkeypatch.setattr(wreq.blocking, "Client", OfflineTransport)


@pytest.fixture(scope="session")
def easyeda_integration_pacer(request):
    """All integration clients share one IP budget and a permanent stop on the first 403."""
    if hasattr(request.config, "workerinput"):
        pytest.fail("EasyEDA integration tests must run in one process (no pytest-xdist)")
    from easyeda_integration import EasyEDAIntegrationPacer
    return EasyEDAIntegrationPacer()


@pytest.fixture(autouse=True)
def _pace_easyeda_integration(request, monkeypatch):
    if request.node.get_closest_marker("integration") is not None:
        request.getfixturevalue("easyeda_integration_pacer").install(monkeypatch)


def write_catalog_category(data_dir, slug, parts):
    """Add or replace a category in a temporary catalog using the production writer."""
    catalog_dir = data_dir / "catalog"
    categories = {}
    if (catalog_dir / "stock.tsv").exists():
        for category, part in read_catalog(catalog_dir):
            categories.setdefault(category, []).append(part)
    categories[slug] = [{"c": 1, "s": None, "$": None, **part} for part in parts]
    prices = {part["l"]: part.get("$") for rows in categories.values() for part in rows}
    write_catalog(catalog_dir, categories, prices)


@pytest.fixture
def stored_lifecycle(monkeypatch):
    """A store with a fixed clock; catalog enrichment must never ask either distributor."""
    from types import SimpleNamespace
    from pcbparts_mcp.distributor_store import DistributorStore

    attempted = []

    async def refuse(*args, **kwargs):
        attempted.append((args, kwargs))
        raise AssertionError("catalog lifecycle made a distributor request")

    store = DistributorStore(clock=lambda: 1_800_000_000)
    monkeypatch.setattr(server, "_distributor_store", store)
    monkeypatch.setattr(server, "_mouser_client", SimpleNamespace(lookup=refuse))
    monkeypatch.setattr(server, "_digikey_client", SimpleNamespace(lookup=refuse))
    yield store
    store.close()
    assert attempted == []


@pytest.fixture(autouse=True)
def _no_real_footprint_store(monkeypatch):
    """Tests that start the real server (its lifespan) must not open the stores that
    EASYEDA_STORE_PATH, CSE_STORE_PATH and DISTRIBUTOR_STORE_PATH name, or the files DISTRIBUTOR_QUOTA_PATH and USAGE_STATS_PATH name: in
    the Docker image those are the live files on the volume. Nor may they build Mouser/DigiKey clients
    from credentials in the shell. Each test also counts usage afresh, with no app remembered for
    any address."""
    monkeypatch.setattr(server, "EASYEDA_STORE_PATH", "")
    monkeypatch.setattr(server, "CSE_STORE_PATH", "")
    monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", "")
    monkeypatch.setattr(server, "DISTRIBUTOR_STORE_PATH", "")
    monkeypatch.setattr(server, "USAGE_STATS_PATH", "")
    monkeypatch.setattr(server, "STATS_TOKEN", "")
    monkeypatch.setattr(server, "CALL_LOG_DIR", "")
    monkeypatch.setattr(call_log, "recorder", call_log.CallLog())
    monkeypatch.setattr(server, "_observation_errors", set())
    for name in ("MOUSER_API_KEY", "DIGIKEY_CLIENT_ID", "DIGIKEY_CLIENT_SECRET", "DIGIKEY_CLIENT_ID_2", "DIGIKEY_CLIENT_SECRET_2"):
        monkeypatch.setattr(server, name, "")
    monkeypatch.setattr(server, "MOUSER_EXTRA_API_KEYS", [])
    monkeypatch.setattr(server, "MOUSER_KEY_WARNINGS", [])
    monkeypatch.setattr(stats, "usage", stats.UsageStats())
    monkeypatch.setattr(server, "_apps_by_address", server.AppsByAddress())


@pytest.fixture
def stats_headers(monkeypatch):
    """Opt in to the private stats handler without depending on a secret in the shell."""
    monkeypatch.setattr(server, "STATS_TOKEN", "test-stats-token")
    return {"Authorization": "Bearer test-stats-token"}
