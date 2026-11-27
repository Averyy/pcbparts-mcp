"""Dismissed notices: stored in the dashboard's own database, changed only from its own page."""

import http.client
import json

import pytest

from pcbparts_dashboard import store as store_module
from test_server import assert_security, auth, request, start_server  # noqa: F401 (start_server is a fixture)

SAME = "SAME"


def send(server, method, path, body=None, *, headers=None, raw=None):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        sent = {key: f"http://127.0.0.1:{server.server_port}" if value == SAME else value
                for key, value in (headers or {}).items()}
        connection.request(method, path, body=data, headers=sent)
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


PAGE = {"Content-Type": "application/json", "X-Dashboard-Request": "1", "Sec-Fetch-Site": "same-origin"}


def test_store_keeps_one_count_per_key_and_undo_removes_it(store):
    store.dismiss("per_ip_refusals", 852, "2026-11-27T17:00:00Z", "2026-11-27")
    store.dismiss("failed:cse_get_kicad:cse_lookup_failed", 3, "2026-11-27T17:01:00Z", "2026-11-27")
    store.dismiss("per_ip_refusals", 900, "2026-11-28T17:02:00Z", "2026-11-28")  # dismissed again a day later
    assert store.dismissals() == [
        {"key": "failed:cse_get_kicad:cse_lookup_failed", "count": 3, "day": "2026-11-27", "at": "2026-11-27T17:01:00Z"},
        {"key": "per_ip_refusals", "count": 900, "day": "2026-11-28", "at": "2026-11-28T17:02:00Z"},
    ]
    store.undismiss("per_ip_refusals")
    store.undismiss("never-dismissed")
    assert [d["key"] for d in store.dismissals()] == ["failed:cse_get_kicad:cse_lookup_failed"]


def test_store_drops_the_oldest_dismissals_past_its_limit(store, monkeypatch):
    monkeypatch.setattr(store_module, "MAX_DISMISSALS", 3)
    for i in range(5):
        store.dismiss(f"warning:{i}", 1, f"2026-11-27T17:0{i}:00Z")
    assert [d["key"] for d in store.dismissals()] == ["warning:2", "warning:3", "warning:4"]


def test_dismissals_leave_the_data_revision_alone(store):
    before = store.revision()
    store.dismiss("per_ip_refusals", 1, "2026-11-27T17:00:00Z")
    store.undismiss("per_ip_refusals")
    assert store.revision() == before
    store.set_meta("anything", 1)
    assert store.revision() != before


def test_dismiss_list_and_undo_through_the_endpoint(start_server, clock):
    start, _ = start_server
    server = start(password="private-password")
    status, headers, body = send(server, "GET", "/api/dismissals", headers=auth())
    assert (status, json.loads(body)) == (200, {"dismissals": []})
    assert headers["Cache-Control"] == "no-store"
    assert_security(headers)
    status, _, body = send(server, "POST", "/api/dismissals",
                           {"key": "held_back:digikey:distributor_refused", "count": 7, "day": "2026-11-21"},
                           headers=auth() | PAGE)
    assert status == 200
    assert json.loads(body)["dismissals"] == [
        {"key": "held_back:digikey:distributor_refused", "count": 7, "day": "2026-11-21", "at": "2026-11-21T19:20:00Z"}]
    status, _, body = send(server, "DELETE", "/api/dismissals?key=held_back:digikey:distributor_refused",
                           headers=auth() | PAGE)
    assert (status, json.loads(body)) == (200, {"dismissals": []})


@pytest.mark.parametrize("method", ["GET", "POST", "DELETE"])
def test_dismissals_need_the_password(start_server, method):
    start, _ = start_server
    server = start(password="private-password")
    status, headers, _ = send(server, method, "/api/dismissals?key=a", {"key": "a", "count": 1, "day": "2026-11-21"}, headers=PAGE)
    assert status == 401
    assert headers["WWW-Authenticate"] == 'Basic realm="pcbparts dashboard"'
    assert server.store.dismissals() == []


@pytest.mark.parametrize("method", ["POST", "DELETE"])
@pytest.mark.parametrize("headers, error", [
    ({"Sec-Fetch-Site": "cross-site"}, "Cross-site requests are not accepted"),
    ({"Sec-Fetch-Site": "same-site"}, "Cross-site requests are not accepted"),
    ({"Sec-Fetch-Site": None, "Origin": "https://elsewhere.example"}, "Cross-site requests are not accepted"),
    ({"Sec-Fetch-Site": None, "Origin": "null"}, "Cross-site requests are not accepted"),
    ({"X-Dashboard-Request": None}, "Missing X-Dashboard-Request header"),
    ({"X-Dashboard-Request": "0"}, "Missing X-Dashboard-Request header"),
])
def test_changes_from_another_site_or_without_the_page_header_are_refused(start_server, method, headers, error):
    start, _ = start_server
    server = start(password="private-password")
    server.store.dismiss("kept", 2, "2026-11-21T19:00:00Z", "2026-11-21")
    sent = {key: value for key, value in (PAGE | headers).items() if value is not None}
    status, reply_headers, body = send(server, method, "/api/dismissals?key=kept", {"key": "new", "count": 1, "day": "2026-11-21"},
                                       headers=auth() | sent)
    assert (status, json.loads(body)) == (403, {"error": error})
    assert_security(reply_headers)
    assert server.store.dismissals() == [{"key": "kept", "count": 2, "day": "2026-11-21", "at": "2026-11-21T19:00:00Z"}]


def test_a_same_origin_request_without_fetch_metadata_is_accepted(start_server):
    start, _ = start_server
    server = start(password="private-password")
    headers = {"Content-Type": "application/json", "X-Dashboard-Request": "1", "Origin": SAME}
    assert send(server, "POST", "/api/dismissals", {"key": "a", "count": 1, "day": "2026-11-21"}, headers=auth() | headers)[0] == 200


@pytest.mark.parametrize("body, raw, content_type, status", [
    ({"key": "", "count": 1, "day": "2026-11-21"}, None, "application/json", 400),
    ({"key": "has space", "count": 1, "day": "2026-11-21"}, None, "application/json", 400),
    ({"key": "x" * 201, "count": 1, "day": "2026-11-21"}, None, "application/json", 400),
    ({"key": "ünïcode", "count": 1, "day": "2026-11-21"}, None, "application/json", 400),
    ({"key": "a", "count": -1, "day": "2026-11-21"}, None, "application/json", 400),
    ({"key": "a", "count": 1.5, "day": "2026-11-21"}, None, "application/json", 400),
    ({"key": "a", "count": True, "day": "2026-11-21"}, None, "application/json", 400),
    ({"key": "a", "count": "3", "day": "2026-11-21"}, None, "application/json", 400),
    ({"key": "a", "day": "2026-11-21"}, None, "application/json", 400),
    ({"key": "a", "count": 1}, None, "application/json", 400),
    ({"key": "a", "count": 1, "day": "2026-13-01"}, None, "application/json", 400),
    ({"key": "a", "count": 1, "day": "Nov 21"}, None, "application/json", 400),
    ({"key": "a", "count": 1, "day": "２０２６-11-21"}, None, "application/json", 400),
    (["a", 1], None, "application/json", 400),
    (None, b"{not json", "application/json", 400),
    (None, b"x" * 5000, "application/json", 413),
    ({"key": "a", "count": 1, "day": "2026-11-21"}, None, "text/plain", 415),
])
def test_invalid_dismissals_are_refused_and_store_nothing(start_server, body, raw, content_type, status):
    start, _ = start_server
    server = start(password="private-password")
    headers = auth() | PAGE | {"Content-Type": content_type}
    reply_status, _, reply = send(server, "POST", "/api/dismissals", body, headers=headers, raw=raw)
    assert reply_status == status
    assert "error" in json.loads(reply)
    assert server.store.dismissals() == []


def test_undo_needs_a_valid_key(start_server):
    start, _ = start_server
    server = start(password="private-password")
    for path in ("/api/dismissals", "/api/dismissals?key=", "/api/dismissals?key=a%20b"):
        assert send(server, "DELETE", path, headers=auth() | PAGE)[0] == 400


def test_a_dismissal_keeps_the_cached_data_reply(start_server, store, stats_reply, clock):
    from pcbparts_dashboard.store import timestamp
    start, _ = start_server
    store.save_stats(stats_reply, timestamp(clock()))
    server = start()
    for _ in range(2):  # the first build saves finished Eastern days, a change of its own
        assert request(server, "/api/data")[0] == 200
    cached = server._data_cache
    assert send(server, "POST", "/api/dismissals", {"key": "a", "count": 1, "day": "2026-11-21"}, headers=PAGE)[0] == 200
    assert request(server, "/api/data")[0] == 200
    assert server._data_cache is cached


@pytest.mark.parametrize("host, allowed", [
    ("127.0.0.1:{port}", True), ("localhost:{port}", True), ("LOCALHOST", True), ("[::1]:{port}", True),
    ("127.0.0.2", True), ("evil.example:{port}", False), ("evil.example", False), ("10.0.0.5:{port}", False),
    ("127.0.0.1.evil.example", False),
])
def test_without_a_password_only_requests_naming_this_computer_are_served(start_server, host, allowed):
    """A page whose name resolves to 127.0.0.1 (DNS rebinding) sends its own name as Host."""
    start, _ = start_server
    server = start()
    sent = {"Host": host.format(port=server.server_port), "Sec-Fetch-Site": "same-origin"}
    for method, path, body in (("GET", "/api/data", None), ("POST", "/api/dismissals", {"key": "a", "count": 1, "day": "2026-11-21"})):
        status, headers, reply = send(server, method, path, body, headers=PAGE | sent)
        assert status == (200 if allowed else 403), (method, host)
        assert_security(headers)
        if not allowed:
            assert json.loads(reply) == {"error": "Without a password, this dashboard answers only to localhost"}
    assert (server.store.dismissals() != []) is allowed


def test_with_a_password_any_host_name_is_served(start_server):
    start, _ = start_server
    server = start(password="private-password")
    assert send(server, "GET", "/api/data", headers=auth() | {"Host": "stats.example"})[0] == 200
