"""Regression tests for the 2026-07 audit 'Do Now' fixes.

Covers: #3 limit floor, #9 error masking, #10 spec_filters validation,
#11 list-param caps, #14 price null/zero handling, #17 UTC quota, #19 WAL.
"""
import datetime
import sys
from pathlib import Path

import pytest

from pcbparts_mcp.config import clamp_limit, MAX_LIST_PARAM_ITEMS
from pcbparts_mcp.cache import DailyQuota, _utc_today
from pcbparts_mcp.client import JLCPCBClient
from pcbparts_mcp.search.spec_filter import SpecFilter
import pcbparts_mcp.server as server

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from scrape_components import transform_part  # noqa: E402


# --- #3: limit floor (clamp_limit) --------------------------------------------------

class TestClampLimit:
    def test_negative_floors_to_one(self):
        assert clamp_limit(-1, 100) == 1

    def test_zero_floors_to_one(self):
        assert clamp_limit(0, 100) == 1

    def test_normal_passes_through(self):
        assert clamp_limit(50, 100) == 50

    def test_over_cap_clamped(self):
        assert clamp_limit(500, 100) == 100

    def test_at_cap(self):
        assert clamp_limit(100, 100) == 100


class TestJlcSearchLimitFloor:
    """End-to-end: a negative limit must NOT fetch the whole table (DoS)."""

    async def test_negative_limit_bounded(self):
        result = await server.jlc_search(query="resistor", limit=-1)
        assert len(result["results"]) <= 1

    async def test_zero_limit_bounded(self):
        result = await server.jlc_search(query="resistor", limit=0)
        assert len(result["results"]) <= 1


# --- #9: error masking --------------------------------------------------------------

def test_mask_error_details_enabled():
    # FastMCP stores the ctor kwarg on the private attr; masking prevents raw exception
    # text (SQL, file paths) from reaching anonymous clients.
    assert server.mcp._mask_error_details is True


# --- #9 follow-up: client ValueErrors must survive masking as {"error": ...} -------

class TestClientErrorsSurviveMasking:
    """mask_error_details=True must NOT hide the client's actionable JLCPCB messages,
    which are raised as ValueError (rate limited / WAF / timeout) — the tools catch them."""

    async def test_stock_check_returns_actionable_error(self, monkeypatch):
        class Fake:
            async def search(self, **kw):
                raise ValueError("JLCPCB rate limited — try again later")
        monkeypatch.setattr(server, "_client", Fake())
        result = await server.jlc_stock_check(query="x")
        assert result["error"] == "JLCPCB rate limited — try again later"

    async def test_get_part_returns_actionable_error(self, monkeypatch):
        class Fake:
            async def get_part(self, lcsc):
                raise ValueError("JLCPCB request timed out — try again later")
        monkeypatch.setattr(server, "_client", Fake())
        result = await server.jlc_get_part(lcsc="C123")
        assert result["error"] == "JLCPCB request timed out — try again later"

    async def test_find_alternatives_returns_actionable_error(self, monkeypatch):
        class Fake:
            async def find_alternatives(self, **kw):
                raise ValueError("JLCPCB blocked request with WAF challenge — try again later")
        monkeypatch.setattr(server, "_client", Fake())
        result = await server.jlc_find_alternatives(lcsc="C123")
        assert "WAF challenge" in result["error"]

    async def test_get_pinout_returns_actionable_error(self, monkeypatch):
        class Fake:
            async def get_part(self, lcsc):
                raise ValueError("JLCPCB rate limited — try again later")
        monkeypatch.setattr(server, "_client", Fake())
        result = await server.jlc_get_pinout(lcsc="C123")
        assert result["error"] == "JLCPCB rate limited — try again later"


# --- #10: spec_filters type validation ----------------------------------------------

class TestSpecFilterValidation:
    def test_non_string_name_skipped(self):
        assert server._parse_spec_filters('[{"name":123,"op":"=","value":{}}]') is None

    def test_non_string_value_skipped(self):
        assert server._parse_spec_filters('[{"name":"Resistance","op":"=","value":{}}]') is None

    def test_valid_filter_kept(self):
        result = server._parse_spec_filters('[{"name":"Resistance","op":">=","value":"10k"}]')
        assert result and result[0].name == "Resistance" and result[0].value == "10k"

    def test_bad_operator_skipped(self):
        assert server._parse_spec_filters('[{"name":"R","op":"!!","value":"1"}]') is None

    def test_specfilter_rejects_non_string(self):
        with pytest.raises(ValueError):
            SpecFilter(123, "=", "x")
        with pytest.raises(ValueError):
            SpecFilter("R", "=", {})

    async def test_jlc_search_bad_spec_filters_no_crash(self):
        # Previously raised AttributeError (uncaught); now handled cleanly.
        result = await server.jlc_search(spec_filters='[{"name":123,"op":"=","value":{}}]')
        assert isinstance(result, dict)


# --- #11: list-param caps -----------------------------------------------------------

class TestListParamCaps:
    def test_under_cap_ok(self):
        assert server._check_list_cap("packages", ["0402", "0603"]) is None

    def test_none_ok(self):
        assert server._check_list_cap("packages", None) is None

    def test_over_cap_error(self):
        err = server._check_list_cap("packages", ["x"] * (MAX_LIST_PARAM_ITEMS + 1))
        assert err is not None and "Too many packages" in err["error"]

    async def test_jlc_search_rejects_huge_package_list(self):
        result = await server.jlc_search(packages=["0402"] * (MAX_LIST_PARAM_ITEMS + 1))
        assert "error" in result


# --- #14: price null / zero handling ------------------------------------------------

class TestPriceHandling:
    def _base_item(self, **over):
        item = {
            "componentCode": "C1", "componentModelEn": "M", "componentBrandEn": "B",
            "componentSpecificationEn": "SMD", "stockCount": 10,
            "componentLibraryType": "base", "preferredComponentFlag": False,
            "firstSortName": "sub", "secondSortName": "cat", "attributes": [],
        }
        item.update(over)
        return item

    def test_client_null_component_prices_no_crash(self):
        # API returns componentPrices: null for some parts -> was len(None) crash.
        c = JLCPCBClient()
        result = c._transform_part(self._base_item(componentPrices=None), slim=True)
        assert result["price"] is None and result["price_10"] is None

    def test_client_zero_price_preserved(self):
        c = JLCPCBClient()
        item = self._base_item(componentPrices=[{"startNumber": 1, "productPrice": 0.0}])
        result = c._transform_part(item, slim=True)
        assert result["price"] == 0.0  # not None

    def test_scraper_null_component_prices_no_crash(self):
        result = transform_part(self._base_item(componentPrices=None), subcategory_id=1)
        assert result["$"] is None

    def test_scraper_zero_price_preserved(self):
        item = self._base_item(componentPrices=[{"productPrice": 0.0}])
        result = transform_part(item, subcategory_id=1)
        assert result["$"] == 0.0


# --- #17: DailyQuota UTC reset ------------------------------------------------------

class TestDailyQuotaUTC:
    def test_utc_today_is_utc(self):
        assert _utc_today() == datetime.datetime.now(datetime.timezone.utc).date()

    def test_resets_on_new_utc_day(self):
        quota = DailyQuota("Test", 1)
        assert quota.check() is None
        assert quota.check() is not None  # over limit
        # Simulate a day passing (in UTC terms)
        quota._date = _utc_today() - datetime.timedelta(days=1)
        assert quota.check() is None  # reset


# --- review fixes: JSON-string list params with non-string elements -----------------

class TestListParamElementTypes:
    """JSON-string list payloads bypass Pydantic — non-string elements must be
    filtered, not crash downstream .lower()/.replace() calls."""

    def test_parse_list_param_filters_non_strings(self):
        assert server._parse_list_param('["0402", 1]') == ["0402"]

    def test_parse_list_param_all_non_strings_is_none(self):
        assert server._parse_list_param('[1, 2]') is None

    async def test_sensor_recommend_int_measures_no_crash(self):
        # Previously: AttributeError 'int' object has no attribute 'lower' in sensor_db
        result = await server.sensor_recommend(measure='[1, 2]', limit=1)
        assert isinstance(result, dict) and "results" in result

    async def test_jlc_search_mixed_packages_no_crash(self):
        result = await server.jlc_search(query="resistor", packages='["0402", 1]', limit=1)
        assert isinstance(result, dict)


# --- review fix: malformed price tiers fail loud (audit #14 advice) ------------------

def test_malformed_price_tier_fails_loud():
    """A tier dict missing productPrice is a JLCPCB type change — raise, don't
    silently return price=None (only a *null* componentPrices list is expected)."""
    c = JLCPCBClient()
    item = {
        "componentCode": "C1", "componentModelEn": "M", "componentBrandEn": "B",
        "componentSpecificationEn": "SMD", "stockCount": 10,
        "componentLibraryType": "base", "preferredComponentFlag": False,
        "firstSortName": "sub", "secondSortName": "cat", "attributes": [],
        "componentPrices": [{"startNumber": 1}],  # tier missing productPrice
    }
    with pytest.raises(KeyError):
        c._transform_part(item, slim=True)


# --- review fix: explicitly-empty MCP_ALLOWED_HOSTS must not collapse to localhost ---

def test_allowed_hosts_empty_env_falls_back(monkeypatch):
    import importlib
    from pcbparts_mcp import config as config_mod
    try:
        monkeypatch.setenv("MCP_ALLOWED_HOSTS", "")
        importlib.reload(config_mod)
        assert config_mod.ALLOWED_HOSTS == ["pcbparts.dev"]
    finally:
        monkeypatch.undo()
        importlib.reload(config_mod)


# --- review fix: sensor build-time floor (deploy-path guard) ------------------------

def test_sensor_db_floor_rejects_truncated():
    from build_sensor_db import build_db, MIN_SENSOR_COUNT
    assert MIN_SENSOR_COUNT >= 1000
    with pytest.raises(ValueError, match="refusing to build"):
        build_db({"S1": {}}, Path("/tmp/pcbparts_floor_test_should_not_exist.db"))


# --- fastmcp 3.x Host-header (DNS-rebinding) protection ------------------------------

def test_host_header_protection():
    """The configured public host must be allowed; unknown hosts get 421 (protection intact)."""
    from starlette.testclient import TestClient
    from pcbparts_mcp.config import ALLOWED_HOSTS
    client = TestClient(server.app)  # no `with` -> skip lifespan; /health needs no app state
    assert client.get("/health", headers={"host": "localhost"}).status_code == 200
    assert client.get("/health", headers={"host": ALLOWED_HOSTS[0]}).status_code == 200
    assert client.get("/health", headers={"host": "rebind.attacker.example"}).status_code == 421


def test_origin_header_protection():
    """Browser Origin for the public https origin must pass even though TLS terminates at the
    proxy (the app sees scheme http, so same-origin matching alone would 403 it); foreign
    origins stay blocked."""
    from starlette.testclient import TestClient
    from pcbparts_mcp.config import ALLOWED_HOSTS
    host = ALLOWED_HOSTS[0]
    client = TestClient(server.app)  # requests arrive as http://, mirroring the proxied app
    ok = client.get("/health", headers={"host": host, "origin": f"https://{host}"})
    assert ok.status_code == 200
    evil = client.get("/health", headers={"host": host, "origin": "https://evil.example"})
    assert evil.status_code == 403


# --- #11: request body size cap ------------------------------------------------------

def test_oversized_body_rejected_413():
    """Bodies over MAX_REQUEST_BODY_BYTES are refused before any parsing."""
    from starlette.testclient import TestClient
    from pcbparts_mcp.config import MAX_REQUEST_BODY_BYTES
    # No `with` -> skip lifespan (middleware needs no app state); without the lifespan the
    # MCP session manager isn't running, so let downstream 500s through instead of raising —
    # the middleware verdict (413 or not) is all this test reads.
    client = TestClient(server.app, raise_server_exceptions=False)
    big = b"x" * (MAX_REQUEST_BODY_BYTES + 1)
    response = client.post("/mcp", content=big, headers={"content-type": "application/json"})
    assert response.status_code == 413
    # Control: a normal-sized request must not trip the middleware (any status but 413)
    response = client.post("/mcp", content=b"{}", headers={"content-type": "application/json"})
    assert response.status_code != 413


# --- #19: ComponentDatabase WAL -----------------------------------------------------

def test_component_db_wal_mode():
    db = server.get_db()
    db._ensure_db()
    mode = db._conn.execute("PRAGMA journal_mode").fetchone()[0]
    assert mode.lower() == "wal"
