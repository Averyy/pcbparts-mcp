import base64
import gzip
import http.client
import json
import socket
import threading
from dataclasses import replace

import pytest

from pcbparts_dashboard.server import create_server, validate_bind


@pytest.fixture
def start_server(settings, store, clock, tmp_path):
    opened = []
    static = tmp_path / "assets"
    static.mkdir()
    (static / "index.html").write_text("<!doctype html><title>Dashboard test</title>")

    def start(*, password=None, username="admin", collector=None):
        server = create_server(
            replace(settings, password=password, username=username), store,
            clock=clock, collector=collector, static_dir=static,
        )
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        thread.start()
        opened.append((server, thread))
        return server

    yield start, static
    for server, thread in opened:
        server.shutdown()
        thread.join()
        server.server_close()


def request(server, path, *, method="GET", headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        connection.request(method, path, headers=headers or {})
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


def auth(user="admin", password="private-password"):
    return {"Authorization": "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()}


def assert_security(headers):
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Referrer-Policy"] == "no-referrer"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Content-Security-Policy"] == (
        "default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    )


def test_static_index_routes(start_server):
    start, static = start_server
    server = start()
    for path in ("/", "/index.html", "/static/index.html"):
        status, headers, body = request(server, path)
        assert status == 200
        assert body == (static / "index.html").read_bytes()
        assert headers["Content-Type"] == "text/html; charset=utf-8"
        assert_security(headers)


@pytest.mark.parametrize("extension, content_type", [
    ("html", "text/html"), ("js", "text/javascript"), ("css", "text/css"),
    ("svg", "image/svg+xml"), ("png", "image/png"), ("woff2", "font/woff2"),
    ("json", "application/json"),
])
def test_static_content_types(start_server, extension, content_type):
    start, static = start_server
    (static / f"asset.{extension}").write_bytes(b"sample")
    status, headers, body = request(start(), f"/static/asset.{extension}")
    assert (status, body) == (200, b"sample")
    assert headers["Content-Type"].split(";")[0] == content_type


@pytest.mark.parametrize("path", [
    "/static/../outside.txt", "/static/%2e%2e/outside.txt", "/static/%2E%2E%2Foutside.txt",
    "/static/nested/../../outside.txt", "/static//etc/passwd", "/static/%2Fetc/passwd",
    "/static/..%5Coutside.txt", "/static/%00", "/static/", "/static/missing.js",
    "/static/outside-link.txt", "/static/linked-directory/outside.txt",
])
def test_static_traversal_and_missing_files_return_json_404(start_server, tmp_path, path):
    start, static = start_server
    outside = tmp_path / "outside.txt"
    outside.write_text("must not be served")
    (static / "outside-link.txt").symlink_to(outside)
    (static / "linked-directory").symlink_to(tmp_path, target_is_directory=True)
    status, headers, body = request(start(), path)
    assert status == 404
    assert json.loads(body) == {"error": "Not found"}
    assert_security(headers)


@pytest.mark.parametrize("path, method", [("/", "GET"), ("/api/data", "GET"), ("/api/refresh", "POST"), ("/missing", "GET"), ("/missing", "PUT")])
def test_basic_auth_required_for_every_route_except_healthz(start_server, path, method):
    start, _ = start_server
    status, headers, body = request(start(password="private-password"), path, method=method)
    assert status == 401
    assert headers["WWW-Authenticate"] == 'Basic realm="pcbparts dashboard"'
    assert json.loads(body)["error"] == "Authentication required"
    assert_security(headers)
    if path.startswith("/api/"):
        assert headers["Cache-Control"] == "no-store"


def test_basic_auth_success_bad_credentials_and_open_healthz(start_server):
    start, _ = start_server
    server = start(password="private-password")
    assert request(server, "/", headers=auth())[0] == 200
    assert request(server, "/api/data", headers=auth())[0] == 200
    for headers in (auth(password="wrong"), auth(user="wrong"), {"Authorization": "Basic %%%"}, {"Authorization": "Bearer private-password"}, {"Authorization": "Basic " + base64.b64encode(b"admin").decode()}):
        assert request(server, "/", headers=headers)[0] == 401
    status, headers, body = request(server, "/healthz")
    assert status == 200 and json.loads(body) == {"ok": True}
    assert_security(headers)


def test_unicode_auth_and_colon_in_password(start_server):
    start, _ = start_server
    server = start(username="réader", password="päss:word")
    assert request(server, "/", headers=auth("réader", "päss:word"))[0] == 200


@pytest.mark.parametrize("host", ["127.0.0.1", "127.0.0.2", "::1", "localhost"])
def test_loopback_allowed_without_password(settings, host):
    validate_bind(replace(settings, host=host))


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.168.1.2", "example.com"])
def test_nonloopback_refused_without_password(settings, store, host):
    with pytest.raises(ValueError, match="DASHBOARD_PASSWORD.*non-loopback"):
        create_server(replace(settings, host=host), store)
    validate_bind(replace(settings, host=host, password="private-password"))


@pytest.mark.parametrize("encoding, compressed", [
    ("gzip", True), ("br, gzip;q=0.5", True), ("*;q=1", True),
    ("gzip;q=0", False), ("*;q=1, gzip;q=0", False), ("identity", False),
    ("gzip;q=bad", False), ("gzip;q=2", False), ("GZip", True),
])
def test_gzip_negotiation_and_payload(start_server, store, stats_reply, clock, encoding, compressed):
    from pcbparts_dashboard.store import timestamp
    start, _ = start_server
    store.save_stats(stats_reply, timestamp(clock()))
    status, headers, body = request(start(), "/api/data", headers={"Accept-Encoding": encoding})
    assert status == 200
    assert headers["Cache-Control"] == "no-store"
    assert headers["Vary"] == "Accept-Encoding"
    assert int(headers["Content-Length"]) == len(body)
    assert (headers.get("Content-Encoding") == "gzip") is compressed
    if compressed:
        body = gzip.decompress(body)
    payload = json.loads(body)
    assert [day["date"] for day in payload["edays"]] == ["2026-11-18", "2026-11-19", "2026-11-20", "2026-11-21"]
    assert "days" not in payload and "compare" not in payload
    assert payload["timezone"] == "America/New_York"
    assert payload["as_of"] == timestamp(clock())
    assert payload["generated_at"] == timestamp(clock())
    assert_security(headers)


def test_refresh_rate_limit_full_and_shared_poll_lock(start_server, clock):
    start, _ = start_server
    calls = []

    def collect(settings, store, *, days, now):
        calls.append((days, now))
        return {"ok": True, "error": None, "days_requested": days, "days_stored": 0, "fetched_at": now.isoformat()}

    server = start(collector=collect)
    assert request(server, "/api/refresh?full=1", method="POST")[0] == 200
    assert calls[0][0] == 365
    status, headers, body = request(server, "/api/refresh", method="POST")
    assert status == 429 and json.loads(body)["retry_after"] == 60
    assert headers["Retry-After"] == "60"
    assert headers["Cache-Control"] == "no-store"
    assert_security(headers)
    clock.advance(59.5)
    assert json.loads(request(server, "/api/refresh", method="POST")[2])["retry_after"] == 1
    clock.advance(0.5)
    assert request(server, "/api/refresh", method="POST")[0] == 200
    assert calls[-1][0] is None
    clock.advance(60)
    with server.runner.lock:
        assert request(server, "/api/refresh", method="POST")[0] == 429
    assert len(calls) == 2
    # The poller uses this exact runner; its collection also starts the cooldown.
    assert server.runner.run()[0] == 200
    assert request(server, "/api/refresh", method="POST")[0] == 429


@pytest.mark.parametrize("headers, allowed", [
    ({}, True),  # curl and other non-browser clients send neither header
    ({"Sec-Fetch-Site": "same-origin"}, True),
    ({"Sec-Fetch-Site": "none"}, True),
    ({"Sec-Fetch-Site": "cross-site"}, False),
    ({"Sec-Fetch-Site": "same-site"}, False),
    ({"Sec-Fetch-Site": "cross-site", "Origin": "SAME"}, False),
    ({"Origin": "SAME"}, True),
    ({"Origin": "https://elsewhere.example"}, False),
    ({"Origin": "null"}, False),
])
def test_refresh_refuses_requests_made_for_another_site(start_server, headers, allowed):
    start, _ = start_server
    calls = []

    def collect(settings, store, *, days, now):
        calls.append(days)
        return {"ok": True, "error": None, "days_requested": days, "days_stored": 0, "fetched_at": now.isoformat()}

    server = start(password="private-password", collector=collect)
    sent = {key: f"http://127.0.0.1:{server.server_port}" if value == "SAME" else value for key, value in headers.items()}
    status, reply_headers, body = request(server, "/api/refresh", method="POST", headers=auth() | sent)
    assert_security(reply_headers)
    if allowed:
        assert status == 200 and calls == [None]
    else:
        assert status == 403 and json.loads(body) == {"error": "Cross-site requests are not accepted"}
        assert calls == []
        assert server.runner.last_started is None  # a refused request must not start the cooldown
    # Without credentials the answer is 401 either way: the check never runs before auth.
    assert request(server, "/api/refresh", method="POST", headers=sent)[0] == 401


def test_unexpected_refresh_exception_releases_lock_and_hides_details(start_server, clock, caplog):
    start, _ = start_server

    def broken(*_args, **_kwargs):
        raise RuntimeError("do-not-log-secret")

    server = start(collector=broken)
    status, headers, body = request(server, "/api/refresh", method="POST")
    assert status == 500 and json.loads(body) == {"error": "Collection failed"}
    assert_security(headers)
    assert not server.runner.lock.locked()
    assert "do-not-log-secret" not in caplog.text


@pytest.mark.parametrize("path, method", [("/missing", "GET"), ("/api/missing", "GET"), ("/api/data", "POST"), ("/api/refresh", "GET"), ("/missing", "PATCH")])
def test_unknown_routes_return_json_404(start_server, path, method):
    start, _ = start_server
    status, headers, body = request(start(), path, method=method)
    assert status == 404 and json.loads(body) == {"error": "Not found"}
    assert_security(headers)


def test_silent_connections_time_out_without_a_log_line(start_server, capsys, monkeypatch):
    from pcbparts_dashboard.server import DashboardHandler

    assert DashboardHandler.timeout == 30
    # The timeout is a socket timeout; with a tiny one the server hangs up on a client that
    # connects and sends nothing, and the test only waits on that close.
    monkeypatch.setattr(DashboardHandler, "timeout", 0.05)
    start, _ = start_server
    server = start(password="private-password")
    with socket.create_connection(("127.0.0.1", server.server_port), timeout=5) as silent:
        assert silent.recv(1) == b""
    monkeypatch.setattr(DashboardHandler, "timeout", 30)  # an ordinary request must not race the tiny one
    assert request(server, "/healthz")[0] == 200
    assert capsys.readouterr().err.strip() == 'GET "/healthz" 200'


def test_access_log_omits_query_and_headers(start_server, capsys):
    start, _ = start_server
    request(start(password="private-password"), "/api/data?secret=hidden-query", headers=auth())
    log = capsys.readouterr().err
    assert log.strip() == 'GET "/api/data" 200'
    assert "hidden-query" not in log
    assert "private-password" not in log
    assert auth()["Authorization"] not in log
