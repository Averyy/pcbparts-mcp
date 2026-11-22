import json

import httpx

from pcbparts_dashboard import cli
from pcbparts_dashboard.collector import collect
from pcbparts_dashboard.store import Store


def test_collect_command_uses_settings_and_prints_one_result(settings, clock, stats_reply, monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_settings", lambda: settings)
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, json=stats_reply if request.url.path == "/mcp/stats" else {"status": "healthy"}
    ))) as client:
        monkeypatch.setattr(cli, "collect", lambda config, store, **kwargs: collect(config, store, client=client, now=clock(), **kwargs))
        assert cli.main(["collect", "--days", "5"]) == 0
    output = capsys.readouterr().out
    assert len(output.splitlines()) == 1
    assert json.loads(output)["days_requested"] == 5
    assert settings.stats_token not in output


def test_failed_collect_returns_nonzero(settings, clock, monkeypatch, capsys):
    from dataclasses import replace
    monkeypatch.setattr(cli, "load_settings", lambda: replace(settings, stats_token=None))
    monkeypatch.setattr(cli, "collect", lambda config, store, **kwargs: collect(config, store, now=clock(), **kwargs))
    assert cli.main(["collect"]) == 1
    assert not json.loads(capsys.readouterr().out)["ok"]


def test_import_command(settings, tmp_path, stats_reply, monkeypatch, capsys):
    path = tmp_path / "mcp-stats_2026-11-21_1417-EST.json"
    path.write_text(json.dumps(stats_reply))
    monkeypatch.setattr(cli, "load_settings", lambda: settings)
    assert cli.main(["import", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["files_imported"] == 1
    with Store(settings.db_path) as store:
        assert store.all_days() == list(reversed(stats_reply["days"]))


def test_serve_command_overrides(settings, monkeypatch):
    monkeypatch.setattr(cli, "load_settings", lambda: settings)
    called = []
    monkeypatch.setattr(cli, "serve", lambda config, store, **kwargs: called.append((config, kwargs)))
    assert cli.main(["serve", "--host", "localhost", "--port", "8001", "--no-poll"]) == 0
    config, kwargs = called[0]
    assert (config.host, config.port) == ("localhost", 8001)
    assert kwargs == {"no_poll": True}


def test_serve_refusal_is_clear(settings, monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_settings", lambda: settings)
    assert cli.main(["serve", "--host", "0.0.0.0", "--no-poll"]) == 1
    assert "DASHBOARD_PASSWORD" in capsys.readouterr().err
