import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest

from pcbparts_dashboard.config import Settings
from pcbparts_dashboard.store import Store

FIXTURES = Path(__file__).with_name("fixtures")


class Clock:
    def __init__(self, value=datetime(2026, 11, 21, 19, 20, tzinfo=UTC)):
        self.value = value

    def __call__(self):
        return self.value

    def advance(self, seconds):
        self.value += timedelta(seconds=seconds)


@pytest.fixture(autouse=True)
def forbid_live_http(monkeypatch):
    def forbidden(*_args, **_kwargs):
        pytest.fail("Upstream HTTP must use httpx.MockTransport")
    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", forbidden)


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def settings(tmp_path):
    return Settings(project_root=tmp_path, stats_token="test-token-never-log", port=0)


@pytest.fixture
def store(settings):
    with Store(settings.db_path) as database:
        yield database


@pytest.fixture
def stats_reply():
    return json.loads((FIXTURES / "mcp-stats_2026-11-21_1417-EST_sample.json").read_text())


@pytest.fixture
def health_reply():
    return json.loads((FIXTURES / "health_sample.json").read_text())
