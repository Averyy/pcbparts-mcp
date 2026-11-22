from pathlib import Path

import pytest

from pcbparts_dashboard.config import Settings, find_project_root, load_settings


def test_defaults_and_cwd_independence(tmp_path, monkeypatch):
    root = find_project_root()
    monkeypatch.chdir(tmp_path)
    assert find_project_root() == root
    settings = load_settings(project_root=tmp_path, environ={})
    assert settings.db_path == tmp_path / "data/dashboard.db"
    assert settings.stats_token is None
    assert settings.password is None
    assert settings.problems_since is None and settings.problems_version is None
    assert settings.stats_url == "https://pcbparts.dev/mcp/stats"
    assert settings.health_url == "https://pcbparts.dev/health"
    assert (settings.poll_minutes, settings.host, settings.port, settings.username) == (60, "127.0.0.1", 8050, "admin")


def test_local_settings_and_environment_override(tmp_path):
    # Synthetic settings only; tests never load the checkout's secrets.local.
    (tmp_path / "secrets.local").write_text(
        "# local test settings\n\nSTATS_TOKEN='file-token'\nDASHBOARD_PASSWORD=\"file-password\"\n"
        "DASHBOARD_DB=other/stats.db\nPOLL_MINUTES=15\nDASHBOARD_PORT=8060\n"
        "DASHBOARD_HOST=localhost\nDASHBOARD_USER=reader\n"
        "STATS_URL=https://stats.example.test/mcp/stats\nHEALTH_URL=https://stats.example.test/health\n"
    )
    settings = load_settings(project_root=tmp_path, environ={})
    assert settings.stats_token == "file-token"
    assert settings.password == "file-password"
    assert settings.db_path == tmp_path / "other/stats.db"
    assert (settings.poll_minutes, settings.port, settings.host, settings.username) == (15, 8060, "localhost", "reader")
    assert settings.stats_url == "https://stats.example.test/mcp/stats"
    assert settings.health_url == "https://stats.example.test/health"
    assert "file-token" not in repr(settings)
    assert "file-password" not in repr(settings)
    overridden = load_settings(project_root=tmp_path, environ={
        "STATS_TOKEN": "env-token", "DASHBOARD_PASSWORD": "", "POLL_MINUTES": "5",
        "DASHBOARD_DB": str(tmp_path / "absolute.db"),
    })
    assert overridden.stats_token == "env-token"
    assert overridden.password is None
    assert overridden.poll_minutes == 5
    assert overridden.db_path == tmp_path / "absolute.db"


@pytest.mark.parametrize("environment, message", [
    ({"POLL_MINUTES": "4"}, "at least 5"),
    ({"POLL_MINUTES": "secret-value"}, "must be an integer"),
    ({"DASHBOARD_PORT": "65536"}, "between 0 and 65535"),
    ({"DASHBOARD_PORT": "secret-value"}, "must be an integer"),
    ({"PROBLEMS_SINCE": "secret-value"}, "ISO timestamp with a timezone"),
    ({"PROBLEMS_SINCE": "2026-11-21T18:00:00"}, "ISO timestamp with a timezone"),
])
def test_invalid_settings_are_clear_and_do_not_echo_values(tmp_path, environment, message):
    with pytest.raises(ValueError, match=message) as caught:
        load_settings(project_root=tmp_path, environ=environment)
    assert "secret-value" not in str(caught.value)


def test_invalid_settings_file_does_not_echo_line(tmp_path):
    (tmp_path / "secrets.local").write_text("secret-value\n")
    with pytest.raises(ValueError, match="line 1") as caught:
        load_settings(project_root=tmp_path, environ={})
    assert "secret-value" not in str(caught.value)


def test_absolute_database_path(tmp_path):
    settings = Settings(project_root=tmp_path / "project", db_path=Path("/tmp/example-dashboard.db"))
    assert settings.db_path == Path("/tmp/example-dashboard.db").resolve()


def test_problems_settings_from_file_and_environment(tmp_path):
    (tmp_path / "secrets.local").write_text(
        "PROBLEMS_SINCE=2026-11-21T13:00:00-05:00\nPROBLEMS_VERSION=0.10.5\n"
    )
    local = load_settings(project_root=tmp_path, environ={})
    assert local.problems_since == "2026-11-21T18:00:00Z"
    assert local.problems_version == "0.10.5"
    overridden = load_settings(project_root=tmp_path, environ={
        "PROBLEMS_SINCE": "2026-11-22T18:30:00Z", "PROBLEMS_VERSION": "0.10.6",
    })
    assert overridden.problems_since == "2026-11-22T18:30:00Z"
    assert overridden.problems_version == "0.10.6"
    cleared = load_settings(project_root=tmp_path, environ={"PROBLEMS_SINCE": "", "PROBLEMS_VERSION": ""})
    assert cleared.problems_since is None and cleared.problems_version is None
