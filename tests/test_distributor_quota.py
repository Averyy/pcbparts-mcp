"""Mouser/DigiKey request counts that survive restarts (0.6.1), and DigiKey's own rate-limit headers.

On 2026-10-16 two restarts (a data deploy, then the 0.6.0 deploy) reset the in-memory count while
DigiKey kept counting, and DigiKey answered 429 "Daily Ratelimit exceeded" until 00:00Z. No network:
httpx.MockTransport and a fake clock."""

import datetime
import json
import logging

import httpx
import pytest

from pcbparts_mcp.cache import SELF_HOSTING_URL, CallerTally, DailyQuota, QuotaStore
from pcbparts_mcp.digikey import DigiKeyClient, DigiKeyError
from pcbparts_mcp.mouser import MouserClient

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 10, 16, 21, 15, tzinfo=UTC).timestamp()
MIDNIGHT = datetime.datetime(2026, 10, 17, tzinfo=UTC).timestamp()

# What prod got from DigiKey on 2026-10-16 at ~21:15Z
DAILY_429_HEADERS = {
    "x-ratelimit-limit": "1000",
    "x-ratelimit-remaining": "0",
    "x-ratelimit-reset": "9892",
    "retry-after": "9892",
    "x-ratelimit-resettime": "2026-10-17T00:00:00.000Z",
}
DAILY_429_BODY = {
    "type": "https://www.rfc-editor.org/rfc/rfc6585.html#section-4",
    "title": "Too Many Requests",
    "status": 429,
    "detail": "Daily Ratelimit exceeded. Please try again after the number of seconds in the Retry-After header",
}
PRODUCT = {
    "Product": {
        "Description": {"ProductDescription": "Test"},
        "Manufacturer": {"Name": "Test"},
        "ManufacturerProductNumber": "TEST123",
        "QuantityAvailable": 100,
        "ProductStatus": {"Status": "Active"},
        "Category": {},
        "Classifications": {},
        "ProductVariations": [],
        "Parameters": [],
    },
}


class Clock:
    def __init__(self, now: float = NOW):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock():
    return Clock()


def quota(clock, path=None, limit=1000, name="DigiKey"):
    return DailyQuota(name, limit, store=QuotaStore(path) if path else None, clock=clock)


class FakeDigiKey:
    """Answers the token request, then each product request with the next queued response."""

    def __init__(self, *responses: httpx.Response):
        self.responses = list(responses)
        self.product_requests = 0
        self.token_requests = 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if "oauth2/token" in str(request.url):
            self.token_requests += 1
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 599, "token_type": "Bearer"})
        self.product_requests += 1
        return self.responses.pop(0)


def digikey(fake: FakeDigiKey, q: DailyQuota | None) -> DigiKeyClient:
    client = DigiKeyClient(client_id="id", client_secret="secret", quota=q)
    client._http = httpx.AsyncClient(transport=httpx.MockTransport(fake))
    return client


def ok(remaining: str | None = None) -> httpx.Response:
    headers = {"x-ratelimit-limit": "1000", "x-ratelimit-remaining": remaining} if remaining else {}
    return httpx.Response(200, json=PRODUCT, headers=headers)


class TestCountsSurviveRestarts:
    def test_count_survives_a_restart(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        q = quota(clock, path)
        for _ in range(3):
            assert q.check() is None
        restarted = quota(clock, path)
        assert restarted.status()["used_today"] == 3
        assert restarted.remaining == 997

    def test_the_limit_holds_across_restarts(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        q = quota(clock, path, limit=2)
        assert q.check() is None and q.check() is None
        assert "daily quota exceeded" in quota(clock, path, limit=2).check()["error"]

    def test_a_new_utc_day_starts_from_zero(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        quota(clock, path).check()
        clock.now = MIDNIGHT
        assert quota(clock, path).status()["used_today"] == 0

    def test_mouser_and_digikey_share_one_file(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        store = QuotaStore(path)
        mouser = DailyQuota("Mouser", 1000, store=store, clock=clock)
        dk = DailyQuota("DigiKey", 1000, store=store, clock=clock)
        mouser.check()
        dk.check()
        dk.check()
        assert set(json.loads(path.read_text(encoding="utf-8"))) == {"Mouser", "DigiKey"}
        store = QuotaStore(path)
        assert DailyQuota("Mouser", 1000, store=store, clock=clock).status()["used_today"] == 1
        assert DailyQuota("DigiKey", 1000, store=store, clock=clock).status()["used_today"] == 2

    def test_written_at_startup(self, tmp_path, clock):
        """So /health's kept_across_restarts reflects a real write right after a deploy."""
        path = tmp_path / "cache" / "quota.json"
        q = quota(clock, path)
        assert path.exists()
        assert q.status()["kept_across_restarts"] is True

    def test_unreadable_file_starts_from_zero_and_is_replaced(self, tmp_path, clock, caplog):
        path = tmp_path / "quota.json"
        path.write_text("{not json", encoding="utf-8")
        with caplog.at_level(logging.WARNING):
            q = quota(clock, path)
        assert "unreadable" in caplog.text
        q.check()
        assert json.loads(path.read_text(encoding="utf-8"))["DigiKey"]["count"] == 1

    def test_malformed_state_starts_from_zero(self, tmp_path, clock, caplog):
        path = tmp_path / "quota.json"
        path.write_text(json.dumps({"DigiKey": {"date": "2026-10-16", "count": "lots"}}), encoding="utf-8")
        with caplog.at_level(logging.WARNING):
            q = quota(clock, path)
        assert "malformed" in caplog.text
        assert q.status()["used_today"] == 0

    def test_unwritable_file_keeps_counting_in_memory(self, tmp_path, clock, caplog):
        blocker = tmp_path / "not-a-dir"
        blocker.write_text("x", encoding="utf-8")
        with caplog.at_level(logging.WARNING):
            q = quota(clock, blocker / "quota.json")
            assert q.check() is None
            assert q.check() is None
        assert q.status()["used_today"] == 2
        assert q.status()["kept_across_restarts"] is False
        assert caplog.text.count("not writable") == 1  # once, not on every request

    def test_without_a_file(self, clock):
        q = quota(clock)
        q.check()
        assert q.status() == {"used_today": 1, "limit": 1000, "api_remaining": None,
                              "paused_until": None, "kept_across_restarts": False}


class TestPause:
    def test_daily_pause_survives_a_restart_and_ends_at_the_reset(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        q = quota(clock, path)
        q.note_api_usage(0, 1000)
        q.pause(MIDNIGHT, "daily")
        restarted = quota(clock, path)
        error = restarted.check()["error"]
        assert error.startswith("DigiKey daily quota exceeded (1000 requests/day, counted by DigiKey)")
        assert "2026-10-17 00:00 UTC" in error
        assert restarted.status()["used_today"] == 0  # a paused check isn't a request
        assert restarted.status()["paused_until"] == "2026-10-17 00:00 UTC"
        clock.now = MIDNIGHT
        assert restarted.check() is None
        assert restarted.status()["api_remaining"] is None  # yesterday's figure

    def test_burst_pause(self, clock):
        q = quota(clock)
        q.pause(clock.now + 30, "burst")
        assert q.check()["error"] == "DigiKey is limiting requests per minute. Try again in 30 s. Meanwhile use jlc_search."
        clock.advance(30)
        assert q.check() is None

    def test_a_shorter_pause_doesnt_cut_a_longer_one(self, clock):
        q = quota(clock)
        q.pause(MIDNIGHT, "daily")
        q.pause(clock.now + 30, "burst")
        clock.advance(31)
        assert "daily quota exceeded" in q.check()["error"]


class TestDigiKeyLimits:
    async def test_daily_429_pauses_until_digikeys_reset(self, clock):
        """The 2026-10-16 prod case: every call after the limit got 429 until 00:00Z."""
        q = quota(clock)
        fake = FakeDigiKey(httpx.Response(429, json=DAILY_429_BODY, headers=DAILY_429_HEADERS))
        client = digikey(fake, q)
        first = await client.get_part("LM358P")
        assert "DigiKey daily quota exceeded (1000 requests/day, counted by DigiKey)" in first["error"]
        assert "2026-10-17 00:00 UTC" in first["error"]
        assert await client.get_part("NE555P") == first
        assert fake.product_requests == 1  # nothing sent while paused
        assert q.status()["api_remaining"] == 0
        assert q.status()["paused_until"] == "2026-10-17 00:00 UTC"
        await client.close()

    async def test_pause_survives_a_restart(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        fake = FakeDigiKey(httpx.Response(429, json=DAILY_429_BODY, headers=DAILY_429_HEADERS))
        await digikey(fake, quota(clock, path)).get_part("LM358P")
        restarted_fake = FakeDigiKey()
        result = await digikey(restarted_fake, quota(clock, path)).get_part("LM358P")
        assert "daily quota exceeded" in result["error"]
        assert restarted_fake.token_requests == restarted_fake.product_requests == 0

    async def test_last_request_of_the_day_is_served_then_pauses(self, clock):
        q = quota(clock)
        fake = FakeDigiKey(ok(remaining="0"))
        client = digikey(fake, q)
        assert (await client.get_part("TEST123"))["total"] == 1
        assert "daily quota exceeded" in (await client.get_part("NE555P"))["error"]
        assert fake.product_requests == 1

    async def test_digikeys_count_is_recorded(self, clock):
        q = quota(clock)
        await digikey(FakeDigiKey(ok(remaining="640")), q).get_part("TEST123")
        assert q.status()["api_remaining"] == 640
        assert q.status()["used_today"] == 1
        assert q.status()["paused_until"] is None

    async def test_burst_429_pauses_for_retry_after(self, clock):
        q = quota(clock)
        burst = httpx.Response(429, json={"detail": "BurstLimit exceeded"},
                               headers={"retry-after": "30", "x-burstlimit-limit": "120", "x-burstlimit-remaining": "0"})
        fake = FakeDigiKey(burst, ok())
        client = digikey(fake, q)
        assert (await client.get_part("TEST123"))["error"].startswith("DigiKey is limiting requests per minute. Try again in 30 s.")
        assert "Try again in" in (await client.get_part("TEST123"))["error"]
        clock.advance(30)
        assert (await client.get_part("TEST123"))["total"] == 1
        assert fake.product_requests == 2

    async def test_429_without_a_quota(self):
        client = digikey(FakeDigiKey(httpx.Response(429, headers=DAILY_429_HEADERS)), None)
        assert (await client.get_part("TEST123"))["error"] == "DigiKey is limiting requests (HTTP 429). Try again later."

    async def test_other_errors_raise_with_the_status(self, clock):
        client = digikey(FakeDigiKey(httpx.Response(503)), quota(clock))
        with pytest.raises(DigiKeyError, match="DigiKey API returned HTTP 503"):
            await client.get_part("TEST123")


class TestToolErrors:
    async def test_digikey_tool_shows_what_went_wrong(self, clock, monkeypatch):
        from pcbparts_mcp import server
        monkeypatch.setattr(server, "_digikey_client", digikey(FakeDigiKey(httpx.Response(503)), quota(clock)))
        result = await server.digikey_get_part(product_number="TEST123")
        assert result == {"error": "DigiKey part lookup failed: DigiKey API returned HTTP 503"}

    async def test_digikey_tool_returns_the_daily_limit_error(self, clock, monkeypatch):
        from pcbparts_mcp import server
        fake = FakeDigiKey(httpx.Response(429, json=DAILY_429_BODY, headers=DAILY_429_HEADERS))
        monkeypatch.setattr(server, "_digikey_client", digikey(fake, quota(clock)))
        result = await server.digikey_get_part(product_number="LM358P")
        assert result["error"].startswith("DigiKey daily quota exceeded")

    async def test_mouser_tool_shows_the_status_but_never_the_key(self, monkeypatch):
        from pcbparts_mcp import server
        client = MouserClient(api_key="secret-key-123")
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(500)))
        monkeypatch.setattr(server, "_mouser_client", client)
        result = await server.mouser_get_part(part_number="595-LM358P")
        assert result == {"error": "Mouser part lookup failed: Mouser API returned HTTP 500"}

    async def test_echoed_credentials_are_redacted(self, monkeypatch):
        from pcbparts_mcp import server
        body = {"Errors": [{"Code": "InvalidKey", "Message": "Key secret-key-123 is not valid"}], "SearchResults": None}
        client = MouserClient(api_key="secret-key-123")
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body)))
        monkeypatch.setattr(server, "_mouser_client", client)
        monkeypatch.setattr(server, "MOUSER_API_KEY", "secret-key-123")
        result = await server.mouser_get_part(part_number="595-LM358P")
        assert result == {"error": "Mouser part lookup failed: Mouser API error [InvalidKey]: Key [redacted] is not valid"}

    async def test_mouser_tool_shows_mousers_error(self, monkeypatch):
        from pcbparts_mcp import server
        body = {"Errors": [{"Code": "InvalidKey", "Message": "Invalid unique identifier."}], "SearchResults": None}
        client = MouserClient(api_key="secret-key-123")
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body)))
        monkeypatch.setattr(server, "_mouser_client", client)
        result = await server.mouser_get_part(part_number="595-LM358P")
        assert result == {"error": "Mouser part lookup failed: Mouser API error [InvalidKey]: Invalid unique identifier."}
        assert "secret-key-123" not in result["error"]


class TestServerWiring:
    async def test_health_shows_counts_kept_in_the_file(self, tmp_path, monkeypatch):
        import json as json_module
        from fastmcp import Client
        from pcbparts_mcp import server
        path = tmp_path / "quota.json"
        monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", str(path))
        monkeypatch.setattr(server, "MOUSER_API_KEY", "test-key")
        monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "test-id")
        monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "test-secret")
        async with Client(server.mcp):
            body = json_module.loads((await server.health(None)).body)["distributor_quota"]
            assert set(body) == {"mouser", "digikey"}
            for status in body.values():
                assert status["used_today"] == 0 and status["kept_across_restarts"] is True
        assert set(json_module.loads(path.read_text(encoding="utf-8"))) == {"Mouser", "DigiKey"}

    async def test_health_without_distributors(self):
        import json as json_module
        from fastmcp import Client
        from pcbparts_mcp import server
        async with Client(server.mcp):
            # tests have no Mouser/DigiKey credentials, and conftest blanks DISTRIBUTOR_QUOTA_PATH
            assert json_module.loads((await server.health(None)).body)["distributor_quota"] == {}


MOUSER_OK = {
    "Errors": [],
    "SearchResults": {"NumberOfResult": 1, "Parts": [{
        "MouserPartNumber": "595-LM358P", "ManufacturerPartNumber": "LM358P", "Manufacturer": "TI",
        "Description": "", "Category": "", "Availability": "", "Min": "1", "PriceBreaks": [], "ProductAttributes": [],
    }]},
}


class FakeMouser:
    def __init__(self, *responses: httpx.Response):
        self.responses = list(responses)
        self.requests = 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests += 1
        return self.responses.pop(0)


def mouser(fake: FakeMouser, q: DailyQuota | None) -> MouserClient:
    client = MouserClient(api_key="secret-key-123", quota=q)
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(fake))
    return client


class TestOurOwnLimits:
    """Once a limit is used up nothing is counted or sent until it resets, and the error says how
    to get around the shared limits."""

    def test_daily_limit_stops_until_the_utc_reset(self, clock):
        q = DailyQuota("DigiKey", 2, clock=clock, own_key="DigiKey API credentials")
        assert q.check() is None and q.check() is None
        error = q.check()["error"]
        assert error.startswith("DigiKey daily quota exceeded (2 requests/day on this shared server). "
                                "It resets at 2026-10-17 00:00 UTC.")
        assert f"run pcbparts-mcp with your own DigiKey API credentials: {SELF_HOSTING_URL}" in error
        q.check()
        assert q.status()["used_today"] == 2  # blocked checks aren't requests
        clock.now = MIDNIGHT
        assert q.check() is None

    def test_per_minute_cap(self, clock):
        q = DailyQuota("Mouser", 1000, clock=clock, per_minute=2, own_key="Mouser API key")
        assert q.check() is None and q.check() is None
        clock.advance(20)
        error = q.check()["error"]
        assert error.startswith("Mouser lookups are limited to 2 a minute on this shared server. Try again in 40 s.")
        assert "your own Mouser API key" in error
        assert q.status()["used_today"] == 2
        clock.advance(40)
        assert q.check() is None

    def test_without_own_key_text(self, clock):
        q = DailyQuota("Test", 1, clock=clock)
        q.check()
        assert q.check()["error"].endswith("It resets at 2026-10-17 00:00 UTC. Meanwhile use jlc_search.")

    def test_server_names_the_signup_pages(self):
        import inspect
        from pcbparts_mcp import server
        source = inspect.getsource(server.lifespan)
        assert "https://www.mouser.com/api-hub/" in source and "https://developer.digikey.com" in source


class TestDigiKeyRefused:
    async def test_403_pauses_ten_minutes(self, clock):
        """DigiKey's API User Agreement section 6: over its per-second threshold an app is
        suspended for ten minutes and gets 403s; three suspensions can end the agreement."""
        q = quota(clock)
        fake = FakeDigiKey(httpx.Response(403), ok())
        client = digikey(fake, q)
        first = await client.get_part("TEST123")
        assert first["error"].startswith("DigiKey refused this server's requests (HTTP 403). Try again in 600 s.")
        assert "refused" in (await client.get_part("TEST123"))["error"]
        assert fake.product_requests == 1
        clock.advance(600)
        assert (await client.get_part("TEST123"))["total"] == 1

    async def test_403_without_a_quota_is_an_error(self):
        client = digikey(FakeDigiKey(httpx.Response(403)), None)
        with pytest.raises(DigiKeyError, match="HTTP 403"):
            await client.get_part("TEST123")


class TestMouserLimits:
    async def test_daily_429_pauses_until_the_reset(self, clock):
        q = quota(clock, name="Mouser")
        fake = FakeMouser(httpx.Response(429, headers=DAILY_429_HEADERS))
        client = mouser(fake, q)
        first = await client.get_part("595-LM358P")
        assert first["error"].startswith("Mouser daily quota exceeded (1000 requests/day, counted by Mouser). "
                                         "It resets at 2026-10-17 00:00 UTC.")
        assert (await client.get_part("511-LM358P")) == first
        assert fake.requests == 1

    async def test_429_with_retry_after(self, clock):
        q = quota(clock, name="Mouser")
        fake = FakeMouser(httpx.Response(429, headers={"retry-after": "20"}), httpx.Response(200, json=MOUSER_OK))
        client = mouser(fake, q)
        assert (await client.get_part("595-LM358P"))["error"].startswith("Mouser is limiting requests per minute. Try again in 20 s.")
        clock.advance(20)
        assert (await client.get_part("595-LM358P"))["total"] == 1
        assert fake.requests == 2

    async def test_bare_429_pauses_a_minute(self, clock):
        q = quota(clock, name="Mouser")
        client = mouser(FakeMouser(httpx.Response(429)), q)
        assert "Try again in 60 s." in (await client.get_part("595-LM358P"))["error"]

    async def test_429_without_a_quota(self):
        client = mouser(FakeMouser(httpx.Response(429)), None)
        assert (await client.get_part("595-LM358P"))["error"] == "Mouser is limiting requests (HTTP 429). Try again later."

    async def test_counts_and_records_the_caller(self, clock):
        q = quota(clock, name="Mouser")
        client = mouser(FakeMouser(httpx.Response(200, json=MOUSER_OK)), q)
        assert (await client.get_part("595-LM358P", caller="203.0.113.7"))["total"] == 1
        assert q.status()["used_today"] == 1
        assert q.callers._counts == {"203.0.113.7": 1}


class TestCallerTally:
    def test_one_line_per_hour_with_the_top_callers(self, clock, caplog):
        clock.now = datetime.datetime(2026, 10, 16, 20, 5, tzinfo=UTC).timestamp()
        tally = CallerTally("DigiKey", clock, top=2)
        for caller in ["203.0.113.7"] * 3 + ["198.51.100.2"] * 2 + ["192.0.2.44"]:
            tally.record(caller)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            tally.flush_if_due()  # same hour: nothing yet
            assert caplog.text == ""
            clock.now = datetime.datetime(2026, 10, 16, 21, 0, 30, tzinfo=UTC).timestamp()
            tally.flush_if_due()
            tally.flush_if_due()  # once
        assert caplog.messages == [
            "DigiKey requests sent 2026-10-16 20:00-21:00 UTC: 6 from 3 IPs; top: 203.0.113.7 3, 198.51.100.2 2"]

    def test_quiet_hours_log_nothing(self, clock, caplog):
        tally = CallerTally("Mouser", clock)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            clock.advance(7200)
            tally.flush_if_due()
            tally.flush()
        assert caplog.messages == []

    def test_shutdown_logs_the_hour_so_far(self, clock, caplog):
        clock.now = datetime.datetime(2026, 10, 16, 23, 10, tzinfo=UTC).timestamp()
        tally = CallerTally("Mouser", clock)
        tally.record(None)
        clock.advance(27 * 60)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            tally.flush()
        assert caplog.messages == ["Mouser requests sent 2026-10-16 23:00-23:37 UTC: 1 from 1 IPs; top: unknown 1"]

    def test_the_last_hour_of_the_day(self, clock, caplog):
        clock.now = datetime.datetime(2026, 10, 16, 23, 10, tzinfo=UTC).timestamp()
        tally = CallerTally("Mouser", clock)
        tally.record("192.0.2.44")
        clock.now = MIDNIGHT + 5
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            tally.flush_if_due()
        assert caplog.messages == ["Mouser requests sent 2026-10-16 23:00-24:00 UTC: 1 from 1 IPs; top: 192.0.2.44 1"]

    def test_caps_the_callers_it_tracks(self, clock):
        tally = CallerTally("Mouser", clock, max_callers=2)
        for caller in ("a", "b", "c", "d", "a"):
            tally.record(caller)
        assert tally._counts == {"a": 2, "b": 1, "other": 2}

    def test_only_requests_that_go_out_are_recorded(self, clock):
        q = DailyQuota("DigiKey", 1, clock=clock)
        assert q.check("203.0.113.7") is None
        assert q.check("203.0.113.7") is not None  # over the limit: not sent
        q.pause(clock.now + 60, "burst")
        assert q.check("198.51.100.2") is not None  # paused: not sent
        assert q.callers._counts == {"203.0.113.7": 1}


class TestCallerIp:
    def test_none_outside_an_http_request(self):
        from pcbparts_mcp import server
        assert server._caller_ip() is None

    def test_rightmost_forwarded_for(self, monkeypatch):
        from starlette.requests import Request
        from pcbparts_mcp import server
        request = Request({"type": "http", "headers": [(b"x-forwarded-for", b"10.0.0.1, 203.0.113.7")],
                           "client": ("172.18.0.5", 4000)})
        monkeypatch.setattr(server, "get_http_request", lambda: request)
        assert server._caller_ip() == "203.0.113.7"

    async def test_tools_pass_the_caller(self, monkeypatch):
        from pcbparts_mcp import server
        seen = {}

        class Recorder:
            async def get_part(self, number, caller=None):
                seen[number] = caller
                return {"results": [], "total": 0}

        monkeypatch.setattr(server, "_caller_ip", lambda: "203.0.113.7")
        monkeypatch.setattr(server, "_mouser_client", Recorder())
        monkeypatch.setattr(server, "_digikey_client", Recorder())
        await server.mouser_get_part(part_number="M1")
        await server.digikey_get_part(product_number="D1")
        assert seen == {"M1": "203.0.113.7", "D1": "203.0.113.7"}

    async def test_shutdown_logs_the_hour_so_far(self, tmp_path, monkeypatch, caplog):
        from fastmcp import Client
        from pcbparts_mcp import server
        monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", str(tmp_path / "quota.json"))
        monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "test-id")
        monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "test-secret")
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            async with Client(server.mcp):
                server._distributor_quotas["digikey"].callers.record("203.0.113.7")
        assert any(m.startswith("DigiKey requests sent ") and m.endswith("1 from 1 IPs; top: 203.0.113.7 1")
                   for m in caplog.messages)
