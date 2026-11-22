"""Public datasheet link settings for private deployments; no upstream requests."""

from types import SimpleNamespace
import runpy

import pytest

from pcbparts_mcp import config, server


@pytest.fixture(autouse=True)
def private_request(monkeypatch):
    request = SimpleNamespace(headers={"host": "pcbparts.ai.svc.cluster.local:8080",
                                       "x-forwarded-host": "untrusted.example"},
                              url=SimpleNamespace(scheme="http"))
    monkeypatch.setattr(server, "get_http_request", lambda: request)
    monkeypatch.setattr(server, "DATASHEET_LINK_BASE", "")
    monkeypatch.setattr(server, "ALLOWED_HOSTS", ["pcbparts.dev"])
    return request


SIGNED_PART = {"lcsc": "C15127", "datasheet_pdf": "https://provider.example/signed.pdf",
               "datasheet_pdf_expires": "2026-11-22T20:00:00Z",
               "datasheet": "https://www.lcsc.com/datasheet/C15127.pdf"}


@pytest.mark.parametrize("host,expected", [
    ("pcbparts.dev", "https://pcbparts.dev"),
    ("pcbparts.dev:80", "https://pcbparts.dev:80"),
    ("localhost:8080", "http://localhost:8080"),
    ("127.0.0.1:8080", "http://127.0.0.1:8080"),
    ("[::1]:8080", "http://[::1]:8080"),
    ("[2001:db8::1]", "http://[2001:db8::1]"),
    ("[::ffff:127.0.0.1]:8080", "http://[::ffff:127.0.0.1]:8080"),
    ("pcbparts.ai.svc.cluster.local:8080", "http://pcbparts.ai.svc.cluster.local:8080"),
    ("parts-api:1", "http://parts-api:1"),
    ("parts-api:65535", "http://parts-api:65535"),
], ids=["public", "public_port", "localhost", "ipv4", "ipv6", "ipv6_bare", "ipv4_mapped",
        "k8s", "min_port", "max_port"])
def test_valid_request_authority(private_request, host, expected):
    private_request.headers["host"] = host
    assert server._datasheet_link_base() == expected
    reply = server._short_datasheet_link(SIGNED_PART)
    assert reply["datasheet_pdf"] == f"{expected}/mcp/datasheet/C15127"
    assert "datasheet_pdf_expires" not in reply


@pytest.mark.parametrize("host", [
    "pcbparts.dev:80@attacker.example", "user@pcbparts.dev", "pcbparts.dev/path",
    "pcbparts.dev?query", "pcbparts.dev#fragment", " pcbparts.dev", "pcbparts.dev ",
    "pcbparts.dev\t", "pcbparts.dev\n", "pcbparts.dev\r\n", "pcbparts.dev%40attacker.example",
    "pcbparts.dev\\attacker.example", "pcbparts.dev:0", "pcbparts.dev:65536", "pcbparts.dev:-1",
    "pcbparts.dev:+80", "pcbparts.dev:abc", "pcbparts.dev:", "pcbparts.dev:８０", "::1",
    "[::1", "[:::1]:8080", "[localhost]:8080", "[fe80::1%25eth0]:8080",
    "parts..example", "-parts.example", "parts-.example", "parts_api", "", None,
], ids=["attack", "userinfo", "path", "query", "fragment", "leading_space", "trailing_space",
        "tab", "newline", "crlf", "percent", "backslash", "zero_port", "large_port", "negative_port",
        "signed_port", "text_port", "empty_port", "unicode_port", "bare_ipv6", "bracket",
        "bad_ipv6", "bracket_host", "scope", "empty_label", "leading_dash", "trailing_dash",
        "underscore", "empty", "missing"])
def test_invalid_request_authority_keeps_signed_link(private_request, host):
    private_request.headers["host"] = host
    assert server._datasheet_link_base() is None
    assert server._short_datasheet_link(SIGNED_PART) == SIGNED_PART


def test_forwarded_authority_and_scheme_are_ignored(private_request):
    private_request.headers.update({"x-forwarded-host": "attacker.example", "x-forwarded-proto": "https"})
    assert server._datasheet_link_base() == "http://pcbparts.ai.svc.cluster.local:8080"
    private_request.url.scheme = "https"
    assert server._datasheet_link_base() == "https://pcbparts.ai.svc.cluster.local:8080"


def test_configured_public_base(monkeypatch):
    monkeypatch.setattr(server, "DATASHEET_LINK_BASE", "https://parts.example")
    reply = server._short_datasheet_link(SIGNED_PART)
    assert reply["datasheet_pdf"] == "https://parts.example/mcp/datasheet/C15127"
    assert "datasheet_pdf_expires" not in reply


@pytest.mark.parametrize("raw,expected", [
    (None, ""), ("", ""), (" direct ", "direct"),
    ("https://parts.example///", "https://parts.example"),
    ("http://localhost:8080/prefix/", "http://localhost:8080/prefix"),
], ids=["unset", "blank", "direct", "slashes", "prefix"])
def test_env_setting(monkeypatch, raw, expected):
    if raw is None:
        monkeypatch.delenv("DATASHEET_LINK_BASE", raising=False)
    else:
        monkeypatch.setenv("DATASHEET_LINK_BASE", raw)
    settings = runpy.run_path(config.__file__)
    assert settings["DATASHEET_LINK_BASE"] == expected
    assert not any("DATASHEET_LINK_BASE" in warning for warning in settings["CONFIG_WARNINGS"])
    monkeypatch.setattr(server, "DATASHEET_LINK_BASE", expected)
    if expected and expected != "direct":
        assert server._short_datasheet_link(SIGNED_PART)["datasheet_pdf"] == f"{expected}/mcp/datasheet/C15127"


@pytest.mark.parametrize("raw", [
    "parts.example", "ftp://parts.example", "https://", "https://parts.example:bad",
    "https://parts.example/?q=1", "https://parts.example/#fragment", "https://user:secret@parts.example",
    "https://parts.example/has space", "https://parts.example/\nfile", "https://parts.example\\path",
    "https://parts.example/https://other.example", "https://[broken",
], ids=["relative", "scheme", "no_host", "port", "query", "fragment", "auth", "space", "control",
        "backslash", "double", "bracket"])
def test_bad_setting_warns_once_and_uses_host(monkeypatch, raw):
    monkeypatch.setenv("DATASHEET_LINK_BASE", raw)
    settings = runpy.run_path(config.__file__)
    assert settings["DATASHEET_LINK_BASE"] == ""
    assert sum("DATASHEET_LINK_BASE" in warning for warning in settings["CONFIG_WARNINGS"]) == 1
    monkeypatch.setattr(server, "DATASHEET_LINK_BASE", settings["DATASHEET_LINK_BASE"])
    assert server._datasheet_link_base() == "http://pcbparts.ai.svc.cluster.local:8080"


@pytest.mark.parametrize("base", ["", "direct", "https://parts.example"], ids=["unset", "direct", "public"])
@pytest.mark.parametrize("invalid_host", [False, True], ids=["normal", "attack"])
async def test_live_part_and_alternatives(base, invalid_host, private_request, monkeypatch):
    monkeypatch.setattr(server, "DATASHEET_LINK_BASE", base)
    monkeypatch.setattr(server, "_distributor_store", None)
    if invalid_host:
        private_request.headers["host"] = "pcbparts.dev:80@attacker.example"

    class Client:
        async def get_part(self, lcsc):
            return dict(SIGNED_PART)

        async def find_alternatives(self, **kwargs):
            return {"original": dict(SIGNED_PART), "alternatives": []}

    monkeypatch.setattr(server, "_client", Client())
    part = await server.jlc_get_part(lcsc="C15127", live=True)
    original = (await server.jlc_find_alternatives(lcsc="C15127"))["original"]
    for row in (part, original):
        assert row["datasheet"] == SIGNED_PART["datasheet"]
        if base == "direct" or (not base and invalid_host):
            assert row["datasheet_pdf"] == SIGNED_PART["datasheet_pdf"]
            assert row["datasheet_pdf_expires"] == SIGNED_PART["datasheet_pdf_expires"]
        else:
            assert row["datasheet_pdf"] == f"{base or 'http://pcbparts.ai.svc.cluster.local:8080'}/mcp/datasheet/C15127"
            assert "datasheet_pdf_expires" not in row


@pytest.mark.parametrize("base", ["", "direct", "https://parts.example"], ids=["unset", "direct", "public"])
@pytest.mark.parametrize("invalid_host", [False, True], ids=["normal", "attack"])
async def test_snapshot_keeps_viewer_and_only_adds_short_link(base, invalid_host, private_request, monkeypatch):
    monkeypatch.setattr(server, "DATASHEET_LINK_BASE", base)
    if invalid_host:
        private_request.headers["host"] = "pcbparts.dev:80@attacker.example"
    snapshot = {"lcsc": "C15127", "datasheet": SIGNED_PART["datasheet"], "specs": {"size": "0402"}}
    monkeypatch.setattr(server, "get_db", lambda: SimpleNamespace(
        price_tiers_as_of=lambda: "2026-11-22", get_part_snapshot=lambda *a, **k: dict(snapshot),
        scraped_at=lambda: "2026-11-22", prices_as_of=lambda: "2026-11-22"))

    async def known_footprint(*args):
        return {}

    monkeypatch.setattr(server, "_client", SimpleNamespace(footprint_seed=lambda code: None,
                                                        known_footprint=known_footprint))
    part = await server.jlc_get_part(lcsc="C15127")
    assert part["datasheet"] == SIGNED_PART["datasheet"]
    assert ("datasheet_pdf" in part) is (base != "direct" and bool(base or not invalid_host))
    assert "datasheet_pdf_expires" not in part


@pytest.mark.parametrize("base", ["", "direct", "https://parts.example"], ids=["unset", "direct", "public"])
@pytest.mark.parametrize("invalid_host", [False, True], ids=["normal", "attack"])
async def test_batch_only_adds_valid_short_link(base, invalid_host, private_request, monkeypatch):
    monkeypatch.setattr(server, "DATASHEET_LINK_BASE", base)
    monkeypatch.setattr(server, "_distributor_store", None)
    if invalid_host:
        private_request.headers["host"] = "pcbparts.dev:80@attacker.example"
    snapshot = {"lcsc": "C15127", "model": "TEST", "stock": 100}
    monkeypatch.setattr(server, "get_db", lambda: SimpleNamespace(
        get_snapshot_rows=lambda codes: {code: dict(snapshot) for code in codes},
        scraped_at=lambda: "2026-11-22", prices_as_of=lambda: "2026-11-22",
        price_tiers_as_of=lambda: "2026-11-22"))
    reply = await server.jlc_get_parts(parts=["C15127"])
    assert reply["counts"]["found"] == 1
    part = reply["results"][0]
    if base == "direct" or (not base and invalid_host):
        assert "datasheet_pdf" not in part
    else:
        assert part["datasheet_pdf"] == f"{base or 'http://pcbparts.ai.svc.cluster.local:8080'}/mcp/datasheet/C15127"
    assert "datasheet_pdf_expires" not in part


@pytest.mark.parametrize("base", ["", "direct", "https://parts.example"], ids=["unset", "direct", "public"])
def test_no_http_request(base, monkeypatch):
    monkeypatch.setattr(server, "DATASHEET_LINK_BASE", base)

    def outside_request():
        raise RuntimeError("No HTTP request")

    monkeypatch.setattr(server, "get_http_request", outside_request)
    assert server._datasheet_link_base() is None
    assert server._short_datasheet_link(SIGNED_PART) == SIGNED_PART
