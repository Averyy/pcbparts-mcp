"""Mouser/DigiKey request counts that survive restarts (0.6.1), and DigiKey's own rate-limit headers.

On 2026-10-16 two restarts (a data deploy, then the 0.6.0 deploy) reset the in-memory count while
DigiKey kept counting, and DigiKey answered 429 "Daily Ratelimit exceeded" until 00:00Z. No network:
httpx.MockTransport and a fake clock."""

import datetime
import json
import logging

import httpx
import pytest

from pcbparts_mcp import stats
from pcbparts_mcp.cache import SELF_HOSTING_URL, CallerTally, DailyQuota, Pacer, QuotaPool, QuotaStore
from pcbparts_mcp.digikey import DigiKeyClient, DigiKeyError, DigiKeyRateLimited
from pcbparts_mcp.mouser import MouserAPIError, MouserClient

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 10, 16, 21, 15, tzinfo=UTC).timestamp()
MIDNIGHT = datetime.datetime(2026, 10, 17, tzinfo=UTC).timestamp()
MOUSER_RESET = MIDNIGHT + 6 * 3600

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
    "ExactMatches": [{
        "Description": {"ProductDescription": "Test"},
        "Manufacturer": {"Name": "Test"},
        "ManufacturerProductNumber": "TEST123",
        "QuantityAvailable": 100,
        "ProductStatus": {"Status": "Active"},
        "Category": {},
        "Classifications": {},
        "ProductVariations": [],
        "Parameters": [],
    }],
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
    return DailyQuota(name, limit, store=QuotaStore(path) if path else None, clock=clock,
                      day_start_hour=6 if name == "Mouser" else 0)


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


async def _no_wait(seconds):  # the transient retry's wait, never real time
    pass


def digikey(fake: FakeDigiKey, q: DailyQuota | None, clock=None) -> DigiKeyClient:
    client = DigiKeyClient(client_id="id", client_secret="secret", quota=q, sleep=_no_wait)
    client._http = httpx.AsyncClient(transport=httpx.MockTransport(fake))
    if clock is not None:
        async def sleep(seconds):
            clock.advance(seconds)

        client._pacer = Pacer(5, clock=clock, sleep=sleep)
    return client


def ok(remaining: str | None = None) -> httpx.Response:
    headers = {"x-ratelimit-limit": "1000", "x-ratelimit-remaining": remaining} if remaining else {}
    return httpx.Response(200, json=PRODUCT, headers=headers)


class TestLimitCauses:
    @pytest.mark.parametrize("reason,expected", [("daily", "distributor_daily"),
                                                 ("daily_unknown", "distributor_daily"),
                                                 ("burst", "distributor_minute"),
                                                 ("refused", "distributor_refused"),
                                                 ("invalid_key", "other")])
    def test_pause_cause_from_state(self, clock, reason, expected):
        quotas = [quota(clock) for _ in range(2)]
        pool = QuotaPool(quotas)
        assert pool.pause_cause() is None
        for q in quotas:
            q.pause(clock.now + 60, reason)
        assert pool.pause_cause() == expected
        assert pool.acquire()[1] is not None and pool.last_refusal_cause == expected
        assert all(q.remaining == 1000 for q in quotas)
        clock.advance(60)
        assert pool.pause_cause() is None
        assert pool.acquire() == (0, None) and pool.last_refusal_cause is None

    def test_daily_count_and_penalty_precedence(self, clock):
        quotas = [quota(clock, limit=1) for _ in range(2)]
        pool = QuotaPool(quotas)
        assert pool.acquire() == (0, None) and pool.acquire() == (1, None)
        quotas[0].pause(clock.now + 3600, "daily_unknown")
        assert pool.pause_cause() == "daily_count"
        assert pool.acquire()[1] and pool.last_refusal_cause == "daily_count"
        pool.share_penalty(clock.now + 60, "burst")
        assert pool.pause_cause() == "distributor_minute"
        pool.share_penalty(clock.now + 70, "refused")
        assert pool.pause_cause() == "distributor_refused"

    def test_daily_pause_only_matters_with_our_requests_left(self, clock):
        quotas = [quota(clock, limit=1), quota(clock)]
        pool = QuotaPool(quotas)
        pool.acquire()  # first quota spent by our count
        quotas[1].pause(clock.now + 60, "daily")
        assert pool.pause_cause() == "distributor_daily"
        quotas[1]._pause_reason = "invalid_key"
        quotas[0].pause(clock.now + 60, "daily")  # spent by our count, so not distributor_daily
        assert pool.pause_cause() == "other"

    def test_minute_cap_still_refuses_exactly_at_cap(self, clock):
        pool = QuotaPool([quota(clock), quota(clock)], per_minute=2)
        assert pool.acquire() == (0, None) and pool.acquire() == (0, None)
        assert pool.pause_cause() is None
        assert pool.acquire()[1] and pool.last_refusal_cause == "minute_cap"
        clock.advance(59)
        assert pool.acquire()[1] and pool.last_refusal_cause == "minute_cap"
        clock.advance(1)
        assert pool.acquire() == (0, None) and pool.last_refusal_cause is None


class TestDailyRefusalEpisodes:
    def test_open_retry_resume_and_new_episode(self, clock):
        q = quota(clock, name="Mouser")
        q.check()
        assert q.pause_daily_unknown_reset() is True
        first = {"at": NOW, "count": 1, "last_refused_at": NOW, "retries": 0, "resumed_at": None}
        assert q._daily_refusals == [first]
        clock.advance(1)
        assert q.pause_daily_unknown_reset() is False  # concurrent reply, same pause
        assert q.clear_expired_pause() is None and q._daily_refusals == [first]
        clock.advance(3599)
        q.check()
        assert q.pause_daily_unknown_reset() is True
        assert q._daily_refusals == [{**first, "last_refused_at": NOW + 3600, "retries": 1}]
        clock.advance(3600)
        q.check()
        resumed = q.clear_expired_pause()
        assert resumed == {**first, "last_refused_at": NOW + 3600, "retries": 1, "resumed_at": NOW + 7200}
        assert q.clear_expired_pause() is None
        assert q.pause_daily_unknown_reset() is True
        assert len(q._daily_refusals) == 2 and q._daily_refusals[-1]["count"] == 3
        assert "daily_refusals" not in q.status()

    def test_episodes_survive_reload_and_utc_date_changes(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        q = quota(clock, path, name="Mouser")
        q.check()
        q.pause_daily_unknown_reset()
        clock.advance(3600)
        q.check()
        q.pause_daily_unknown_reset()
        assert quota(clock, path, name="Mouser")._daily_refusals == q._daily_refusals
        clock.now = MIDNIGHT
        restarted = quota(clock, path, name="Mouser")
        assert restarted._count == 2 and restarted._daily_refusals == q._daily_refusals
        clock.now = MOUSER_RESET
        assert restarted.status()["used_today"] == 0
        restarted.check()
        resumed = restarted.clear_expired_pause()
        assert resumed["at"] == NOW and resumed["resumed_at"] == MOUSER_RESET and resumed["retries"] == 1
        assert quota(clock, path, name="Mouser")._daily_refusals == restarted._daily_refusals

    def test_only_thirty_most_recent_episodes_kept(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        q = quota(clock, path, name="Mouser")
        for _ in range(35):
            q.check()
            q.pause_daily_unknown_reset()
            clock.advance(3600)
            q.clear_expired_pause()
        assert len(q._daily_refusals) == 30 and q._daily_refusals[0]["at"] == NOW + 5 * 3600
        assert quota(clock, path, name="Mouser")._daily_refusals == q._daily_refusals
        state = json.loads(path.read_text(encoding="utf-8"))
        episode = state["Mouser"]["daily_refusals"][-1]
        state["Mouser"]["daily_refusals"] = [episode] * 35
        path.write_text(json.dumps(state), encoding="utf-8")
        assert len(quota(clock, path, name="Mouser")._daily_refusals) == 30

    @pytest.mark.parametrize("bad", [None, "x", {}, [None], [{}],
                                     [{"at": float("inf"), "count": 1, "last_refused_at": NOW,
                                       "retries": 0, "resumed_at": None}],
                                     [{"at": NOW, "count": True, "last_refused_at": NOW,
                                       "retries": 0, "resumed_at": None}]])
    def test_malformed_history_is_empty_not_broken_quota(self, tmp_path, clock, bad):
        path = tmp_path / "quota.json"
        path.write_text(json.dumps({"Mouser": {"date": "2026-10-16", "count": 7,
                                               "daily_refusals": bad}}), encoding="utf-8")
        q = quota(clock, path, name="Mouser")
        assert q._daily_refusals == [] and q._count == 7
        assert q.pause_daily_unknown_reset() and q._daily_refusals[-1]["count"] == 7

    def test_request_through_closes_episode_whatever_the_last_pause_was_for(self, clock):
        q = quota(clock, name="Mouser")
        q.pause_daily_unknown_reset()
        clock.advance(3600)
        q.pause(clock.now + 60, "burst")  # a per-minute pause replaced the ended daily one's reason
        assert q.clear_expired_pause() is None  # still paused: an answer to an earlier request
        assert q._daily_refusals[-1]["resumed_at"] is None
        clock.advance(60)
        resumed = q.clear_expired_pause()
        assert resumed is not None and resumed["resumed_at"] == NOW + 3660
        assert q.daily_refusals() == [resumed] and q._pause_reason == ""
        assert q.clear_expired_pause() is None  # closed once


class TestDistributorLimitStats:
    @pytest.mark.parametrize("status,headers,label,cause", [
        (429, DAILY_429_HEADERS, "daily", "distributor_daily"),
        (429, {}, "minute", "distributor_minute"),
        (403, {}, "refused", "distributor_refused"),
        (403, DAILY_429_HEADERS, "refused", "distributor_refused")],
        ids=["day", "min", "403", "403zero"])
    async def test_sent_refusals_and_held_back_lookups(self, monkeypatch, clock, status, headers, label, cause):
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        fake = FakeDigiKey(httpx.Response(status, json={}, headers=headers))
        client = digikey(fake, quota(clock), clock=clock)
        try:
            for i in range(4):
                assert "error" in await client.get_part(f"PART{i}A")
            day = stats.usage.summary()["days"][0]
            counts = day["distributor_limits"]["digikey"]
            assert counts["refusals"][label] == 1 and sum(counts["refusals"].values()) == 1
            assert counts["held_back"][cause] == 3
            assert sum(counts["held_back"].values()) == day["distributors"]["digikey"]["rate_limited"] == 3
            assert sum(counts["held_back_hours"]) == 3
            assert day["distributors"]["digikey"]["sent"] == fake.product_requests == 1
        finally:
            await client.close()

    async def test_success_with_zero_remaining_is_not_a_refusal(self, monkeypatch, clock):
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        client = digikey(FakeDigiKey(ok("0")), quota(clock), clock=clock)
        try:
            assert "error" not in await client.get_part("TEST123")
            assert "error" in await client.get_part("PART2A")
            counts = stats.usage.summary()["days"][0]["distributor_limits"]["digikey"]
            assert sum(counts["refusals"].values()) == 0
            assert counts["held_back"]["distributor_daily"] == 1
        finally:
            await client.close()

    @pytest.mark.parametrize("status,headers,label", [(429, {}, "minute"), (429, DAILY_429_HEADERS, "daily"),
                                                     (403, {}, "refused")], ids=["min", "day", "403"])
    async def test_token_refusal_counts(self, monkeypatch, clock, status, headers, label):
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        client = digikey(FakeDigiKey(), quota(clock), clock=clock)
        await client._http.aclose()
        client._http = httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(status, json={}, headers=headers)))
        try:
            assert "error" in await client.get_part("TEST123")
            day = stats.usage.summary()["days"][0]
            assert day["distributor_limits"]["digikey"]["refusals"][label] == 1
            assert sum(day["distributor_limits"]["digikey"]["held_back"].values()) == 1
            assert day["distributors"]["digikey"]["rate_limited"] == 1
            assert day["distributors"]["digikey"]["sent"] == 0  # sent counts lookups, never token requests
        finally:
            await client.close()

    async def test_token_limit_without_explanatory_pause_is_other(self, monkeypatch, clock):
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        client = digikey(FakeDigiKey(), quota(clock), clock=clock)

        async def limited(caller=None):
            raise DigiKeyRateLimited("token limit")

        monkeypatch.setattr(client, "_ready_app", limited)
        try:
            assert "error" in await client.get_part("TEST123")
            day = stats.usage.summary()["days"][0]
            assert day["distributor_limits"]["digikey"]["held_back"]["other"] == 1
            assert day["distributors"]["digikey"]["rate_limited"] == 1
        finally:
            await client.close()

    async def test_acquire_minute_cap_is_counted(self, monkeypatch, clock):
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        q = DailyQuota("DigiKey", 1000, clock=clock, per_minute=1)
        client = digikey(FakeDigiKey(), q, clock=clock)
        client._quota.acquire()  # consume minute without sending a request

        async def ready(caller=None):
            return 0, "tok"

        monkeypatch.setattr(client, "_ready_app", ready)
        try:
            assert "error" in await client.get_part("TEST123")
            day = stats.usage.summary()["days"][0]
            assert day["distributor_limits"]["digikey"]["held_back"]["minute_cap"] == 1
            assert day["distributors"]["digikey"]["rate_limited"] == 1
        finally:
            await client.close()


class TestCountsSurviveRestarts:
    def test_mouser_day_rolls_at_six_but_digikey_at_midnight(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        store = QuotaStore(path)
        mouser = DailyQuota("Mouser", 2, store=store, clock=clock, day_start_hour=6)
        digikey = DailyQuota("DigiKey", 2, store=store, clock=clock)
        mouser.check()
        digikey.check()
        clock.now = MIDNIGHT
        assert mouser.status()["used_today"] == 1
        assert digikey.status()["used_today"] == 0
        assert quota(clock, path, name="Mouser").status()["used_today"] == 1
        clock.now = MOUSER_RESET - 1
        assert mouser.check() is None
        assert mouser.status()["used_today"] == 2 and mouser.retry_after() == 1
        assert "resets at 2026-10-17 06:00 UTC" in mouser.count_error()["error"]
        assert json.loads(path.read_text(encoding="utf-8"))["Mouser"]["date"] == "2026-10-16"
        clock.now = MOUSER_RESET
        assert mouser.status()["used_today"] == 0 and mouser.retry_after() is None
        assert mouser.check() is None
        saved = json.loads(path.read_text(encoding="utf-8"))["Mouser"]
        assert saved["date"] == "2026-10-17" and saved["count"] == 1

    @pytest.mark.parametrize("hour,label,expected", [
        (5, "2026-10-16", 7), (5, "2026-10-17", 7), (5, "2026-10-15", 0),
        (5, "2026-10-18", 0), (6, "2026-10-16", 0), (6, "2026-10-17", 7),
        (6, "2026-10-18", 0), (5, "bad", 0), (5, [], 0),
    ], ids=["same", "old_utc", "older", "future", "expired", "new_day", "future_day", "bad", "bad_list"])
    def test_mouser_stored_date_migration(self, tmp_path, clock, hour, label, expected):
        clock.now = MIDNIGHT + hour * 3600
        path = tmp_path / "quota.json"
        pause = MOUSER_RESET + 123
        path.write_text(json.dumps({"Mouser": {"date": label, "count": 7,
                                               "paused_until": pause, "pause_reason": "daily_unknown"}}),
                        encoding="utf-8")
        for _ in range(2):  # the migrated label is written back and survives another restart
            q = quota(clock, path, name="Mouser")
            assert q.status()["used_today"] == expected
            assert q._paused_until == pause and q._pause_reason == "daily_unknown"
            state = json.loads(path.read_text(encoding="utf-8"))["Mouser"]
            assert state["date"] == ("2026-10-16" if hour < 6 else "2026-10-17")

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
        mouser = DailyQuota("Mouser", 1000, store=store, clock=clock, day_start_hour=6)
        dk = DailyQuota("DigiKey", 1000, store=store, clock=clock)
        mouser.check()
        dk.check()
        dk.check()
        assert set(json.loads(path.read_text(encoding="utf-8"))) == {"Mouser", "DigiKey"}
        store = QuotaStore(path)
        assert DailyQuota("Mouser", 1000, store=store, clock=clock, day_start_hour=6).status()["used_today"] == 1
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
                              "paused_until": None, "resets_at": "2026-10-17 00:00 UTC", "kept_across_restarts": False}


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
        assert first["error"].startswith("DigiKey daily quota exceeded on this shared server.")
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
        fake = FakeDigiKey(httpx.Response(503), httpx.Response(503))  # a 5xx is sent once more (0.10.11)
        client = digikey(fake, quota(clock))
        with pytest.raises(DigiKeyError, match="DigiKey API returned HTTP 503"):
            await client.get_part("TEST123")
        assert fake.product_requests == 2


class TestToolErrors:
    async def test_digikey_tool_shows_what_went_wrong(self, clock, monkeypatch):
        from pcbparts_mcp import server
        fake = FakeDigiKey(httpx.Response(503), httpx.Response(503))  # sent once more, then reported
        monkeypatch.setattr(server, "_digikey_client", digikey(fake, quota(clock)))
        result = await server.digikey_get_part(part_number="TEST123")
        assert result == {"error": "DigiKey part lookup failed: DigiKey API returned HTTP 503"}

    async def test_digikey_tool_returns_the_daily_limit_error(self, clock, monkeypatch):
        from pcbparts_mcp import server
        fake = FakeDigiKey(httpx.Response(429, json=DAILY_429_BODY, headers=DAILY_429_HEADERS))
        monkeypatch.setattr(server, "_digikey_client", digikey(fake, quota(clock)))
        result = await server.digikey_get_part(part_number="LM358P")
        assert result["error"].startswith("DigiKey daily quota exceeded")

    async def test_mouser_tool_shows_the_status_but_never_the_key(self, monkeypatch, clock):
        from pcbparts_mcp import server
        async def sleep(seconds):
            clock.advance(seconds)
        client = MouserClient(api_key="secret-key-123", clock=clock, sleep=sleep)
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
    async def test_health_is_identical_across_distributor_configurations(self, monkeypatch):
        from pcbparts_mcp import server
        from pcbparts_mcp.cache import MouserKeyPool
        from digikey_ext import FakeExt

        monkeypatch.setattr(server, "_health_clock", lambda: NOW)
        monkeypatch.setattr(server, "_distributor_quotas", {})
        monkeypatch.setattr(server, "_digikey_client", None)
        monkeypatch.setattr(server, "_client", None)
        monkeypatch.setattr(server, "_cse_client", None)
        monkeypatch.setattr(server, "_distributor_store", None)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.create_app()),
                                     base_url="http://localhost") as client:
            baseline = (await client.get("/health")).json()
            assert "distributor_quota" not in baseline
            for name, size in (("mouser", 1), ("mouser", 3), ("digikey", 1), ("digikey", 2)):
                quotas = [DailyQuota(name.title(), 1000, clock=lambda: NOW,
                                     day_start_hour=6 if name == "mouser" else 0) for _ in range(size)]
                pool = (MouserKeyPool if name == "mouser" else QuotaPool)(quotas)
                monkeypatch.setattr(server, "_distributor_quotas", {name: pool})
                assert (await client.get("/health")).json() == baseline
                pool.acquire()
                quotas[0].pause(MOUSER_RESET if name == "mouser" else MIDNIGHT, "daily")
                assert (await client.get("/health")).json() == baseline
                pool.share_penalty(MIDNIGHT, "daily")
                assert (await client.get("/health")).json() == baseline
            ext = FakeExt()
            digikey = DigiKeyClient(client_id="", client_secret="", ext=ext, clock=lambda: NOW)
            monkeypatch.setattr(server, "_distributor_quotas", {})
            monkeypatch.setattr(server, "_digikey_client", digikey)
            try:
                assert (await client.get("/health")).json() == baseline
                ext.pause()
                assert (await client.get("/health")).json() == baseline
            finally:
                await digikey.close()

    @pytest.mark.parametrize("name, size", [("mouser", 1), ("mouser", 3), ("digikey", 1), ("digikey", 2)],
                             ids=["m1", "m3", "d1", "d2"])
    @pytest.mark.parametrize("paused", [False, True], ids=["ready", "paused"])
    async def test_quota_state_is_private(self, monkeypatch, stats_headers, name, size, paused):
        from pcbparts_mcp import server
        from pcbparts_mcp.cache import MouserKeyPool
        quotas = [DailyQuota(name.title(), 1000, clock=lambda: NOW,
                             day_start_hour=6 if name == "mouser" else 0) for _ in range(size)]
        pool = (MouserKeyPool if name == "mouser" else QuotaPool)(quotas)
        pool.acquire()
        quotas[0].note_api_usage(999, 1000)
        if paused:
            pool.share_penalty(NOW + 60, "burst")
        monkeypatch.setattr(server, "_distributor_quotas", {name: pool})
        monkeypatch.setattr(server, "_digikey_client", None)
        expected = {"paused_until": "2026-10-16 21:16 UTC" if paused else None,
                    "resets_at": "2026-10-17 06:00 UTC" if name == "mouser" else "2026-10-17 00:00 UTC"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.create_app()),
                                     base_url="http://localhost") as client:
            health = await client.get("/health")
            assert health.status_code == 200
            assert "distributor_quota" not in health.json()
            for headers in ({}, {"Authorization": "Bearer wrong"}):
                refused = await client.get("/mcp/stats", headers=headers)
                assert refused.status_code == 401 and refused.json() == {"error": "Unauthorized"}
            for days in (1, 365):
                response = await client.get(f"/mcp/stats?days={days}", headers=stats_headers)
                assert response.status_code == 200
                assert response.headers["cache-control"] == "private, no-store"
                assert response.json()["distributor_quota"] == {name: {
                    **expected, "used_today": 1, "limit": 1000, "api_remaining": 999,
                    "kept_across_restarts": False,
                    # share_penalty pauses the pool (the top level), not any budget's own pause
                    "budgets": [{"used_today": 1, "limit": 1000, "api_remaining": 999, "paused_until": None,
                                 "in_use": True}] + [{"used_today": 0, "limit": 1000, "api_remaining": None,
                                                      "paused_until": None, "in_use": False}] * (size - 1),
                }}
                assert "distributor_quota" in response.json()["about"]
                assert "distributor_quota" not in response.json()["totals"]

    async def test_stats_shows_counts_kept_in_the_file(self, tmp_path, monkeypatch, stats_headers):
        import json as json_module
        from types import SimpleNamespace
        from fastmcp import Client
        from pcbparts_mcp import server
        path = tmp_path / "quota.json"
        monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", str(path))
        monkeypatch.setattr(server, "MOUSER_API_KEY", "test-key")
        monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "test-id")
        monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "test-secret")
        async with Client(server.mcp):
            assert "distributor_quota" not in json_module.loads((await server.health(None)).body)
            response = await server.usage_stats(SimpleNamespace(headers=stats_headers, query_params={}))
            body = json_module.loads(response.body)["distributor_quota"]
            assert set(body) == {"mouser", "digikey"}
            for status in body.values():
                assert status["used_today"] == 0 and status["kept_across_restarts"] is True
        assert set(json_module.loads(path.read_text(encoding="utf-8"))) == {"Mouser", "DigiKey"}

    async def test_health_without_distributors(self, stats_headers):
        import json as json_module
        from types import SimpleNamespace
        from fastmcp import Client
        from pcbparts_mcp import server
        async with Client(server.mcp):
            # tests have no Mouser/DigiKey credentials, and conftest blanks DISTRIBUTOR_QUOTA_PATH
            assert "distributor_quota" not in json_module.loads((await server.health(None)).body)
            response = await server.usage_stats(SimpleNamespace(headers=stats_headers, query_params={}))
            assert json_module.loads(response.body)["distributor_quota"] == {}


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
        q = DailyQuota("Mouser", 1000, clock=clock, per_minute=2, own_key="Mouser API key", day_start_hour=6)
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
    async def test_daily_429_retries_hourly(self, clock):
        q = quota(clock, name="Mouser")
        fake = FakeMouser(httpx.Response(429, headers=DAILY_429_HEADERS))
        client = mouser(fake, q)
        first = await client.get_part("595-LM358P")
        assert first["error"].startswith("Mouser daily quota exceeded (counted by Mouser). "
                                         "This server tries again at 2026-10-16 22:15 UTC.")
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
        await server.digikey_get_part(part_number="D1")
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


# Mouser's real refusals (reported by other projects in 2026): HTTP 403 with the limit in the body
MOUSER_DAILY_403 = {"Errors": [{"Code": "TooManyRequests", "Message": "Maximum calls per day exceeded.",
                                "ResourceKey": "MaxCallPerDay"}]}
MOUSER_MINUTE_403 = {"Errors": [{"Code": "TooManyRequests", "Message": "Maximum calls per minute exceeded."}]}


class TestMouserRefusals:
    async def test_daily_403_pauses_an_hour_while_our_count_is_below_the_limit(self, tmp_path, clock):
        """With every key refused, an hourly probe can precede the scheduled day-start retry."""
        path = tmp_path / "quota.json"
        fake = FakeMouser(httpx.Response(403, json=MOUSER_DAILY_403))
        client = mouser(fake, quota(clock, path, name="Mouser"))
        error = (await client.get_part("595-LM358P"))["error"]
        assert error.startswith("Mouser daily quota exceeded (counted by Mouser). "
                                 "This server tries again at 2026-10-16 22:15 UTC.")
        assert "your own" not in error  # no own_key text in this quota; the server passes one
        assert (await client.get_part("511-LM358P"))["error"] == error
        assert fake.requests == 1
        # a restart keeps the pause
        restarted = FakeMouser()
        assert "daily quota exceeded" in (await mouser(restarted, quota(clock, path, name="Mouser")).get_part("595-LM358P"))["error"]
        assert restarted.requests == 0

    async def test_refused_again_retries_hourly(self, clock):
        q = quota(clock, name="Mouser")
        fake = FakeMouser(httpx.Response(403, json=MOUSER_DAILY_403), httpx.Response(403, json=MOUSER_DAILY_403),
                          httpx.Response(200, json=MOUSER_OK), httpx.Response(403, json=MOUSER_DAILY_403))
        client = mouser(fake, q)
        await client.get_part("595-LM358P")
        clock.now = MIDNIGHT  # Mouser hasn't reached its 06:00 reset yet
        assert "tries again at 2026-10-17 01:00 UTC" in (await client.get_part("595-LM358P"))["error"]
        clock.now = MIDNIGHT + 3600
        assert (await client.get_part("595-LM358P"))["total"] == 1
        clock.now = MIDNIGHT + 20 * 3600  # refused again later that day: an hour again
        assert "tries again at 2026-10-17 21:00 UTC" in (await client.get_part("511-LM358P"))["error"]
        assert fake.requests == 4

    async def test_refused_with_our_own_count_spent_waits_for_day_start(self, clock):
        q = quota(clock, name="Mouser", limit=1)
        client = mouser(FakeMouser(httpx.Response(403, json=MOUSER_DAILY_403)), q)
        assert "tries again at 2026-10-17 06:01 UTC" in (await client.get_part("595-LM358P"))["error"]

    async def test_daily_refusal_in_a_429_keeps_the_hourly_retry(self, clock):
        """A daily refusal can come as HTTP 429 with the TooManyRequests body: the 429 mustn't also
        set a minute's pause, which replaced the daily one and made a second refusal wait for the
        next midnight instead of an hour (review 2026-11-18)."""
        q = quota(clock, name="Mouser")
        pauses = []
        real_pause = q.pause
        q.pause = lambda until, reason: (pauses.append(reason), real_pause(until, reason))
        fake = FakeMouser(httpx.Response(429, json=MOUSER_DAILY_403), httpx.Response(429, json=MOUSER_DAILY_403))
        client = mouser(fake, q)
        assert "tries again at 2026-10-16 22:15 UTC" in (await client.get_part("595-LM358P"))["error"]
        assert pauses == ["daily_unknown"]  # no "burst" from the 429 itself
        assert q._pause_reason == "daily_unknown"
        clock.now = MIDNIGHT
        assert "tries again at 2026-10-17 01:00 UTC" in (await client.get_part("595-LM358P"))["error"]
        assert fake.requests == 2

    async def test_per_minute_403_pauses_a_minute(self, clock):
        q = quota(clock, name="Mouser")
        fake = FakeMouser(httpx.Response(403, json=MOUSER_MINUTE_403), httpx.Response(200, json=MOUSER_OK))
        client = mouser(fake, q)
        assert (await client.get_part("595-LM358P"))["error"].startswith(
            "Mouser is limiting requests per minute. Try again in 60 s.")
        clock.advance(60)
        assert (await client.get_part("595-LM358P"))["total"] == 1

    async def test_refusal_inside_a_200(self, clock):
        """A 2024 report saw TooManyRequests with "Message": null; the status wasn't recorded."""
        body = {"Errors": [{"Id": 0, "Code": "TooManyRequests", "Message": None, "ResourceKey": "MaxCallPerDay"}],
                "SearchResults": None}
        client = mouser(FakeMouser(httpx.Response(200, json=body)), quota(clock, name="Mouser"))
        assert "daily quota exceeded" in (await client.get_part("595-LM358P"))["error"]

    async def test_other_403s_show_mousers_message_and_dont_pause(self, clock, monkeypatch):
        from pcbparts_mcp import server
        q = quota(clock, name="Mouser")
        body = {"Errors": [{"Code": "Invalid", "Message": "Invalid unique identifier."}]}
        client = mouser(FakeMouser(httpx.Response(403, json=body), httpx.Response(403)), q)
        monkeypatch.setattr(server, "_mouser_client", client)
        assert (await server.mouser_get_part(part_number="595-LM358P")) == {
            "error": "Mouser part lookup failed: Mouser API error [Invalid]: Invalid unique identifier."}
        assert (await server.mouser_get_part(part_number="511-LM358P")) == {
            "error": "Mouser part lookup failed: Mouser API returned HTTP 403"}
        assert q.status()["paused_until"] is None

    async def test_null_message(self):
        body = {"Errors": [{"Code": "Oops", "Message": None}], "SearchResults": None}
        client = mouser(FakeMouser(httpx.Response(200, json=body)), None)
        with pytest.raises(MouserAPIError, match=r"\[Oops\]: Unknown Mouser API error"):
            await client.get_part("595-LM358P")

    async def test_daily_403_without_a_quota(self):
        client = mouser(FakeMouser(httpx.Response(403, json=MOUSER_DAILY_403)), None)
        assert (await client.get_part("595-LM358P"))["error"] == \
            "Mouser is limiting requests (Maximum calls per day exceeded.). Try again later."

    async def test_server_message_names_your_own_key(self, clock):
        q = DailyQuota("Mouser", 1000, clock=clock, own_key="Mouser API key (free at https://www.mouser.com/api-hub/)", day_start_hour=6)
        client = mouser(FakeMouser(httpx.Response(403, json=MOUSER_DAILY_403)), q)
        error = (await client.get_part("595-LM358P"))["error"]
        assert f"run pcbparts-mcp with your own Mouser API key (free at https://www.mouser.com/api-hub/): {SELF_HOSTING_URL}" in error


class TestMouserBatches:
    """Mouser's SearchByPartRequest takes up to 10 part numbers, 3-40 characters each (its API docs)."""

    def recording(self):
        sent = []

        def handler(request: httpx.Request) -> httpx.Response:
            sent.append(json.loads(request.content)["SearchByPartRequest"]["mouserPartNumber"])
            return httpx.Response(200, json=MOUSER_OK)
        return sent, handler

    async def test_more_than_ten_is_refused_without_a_request(self, clock):
        q = quota(clock, name="Mouser")
        sent, handler = self.recording()
        client = MouserClient(api_key="k", quota=q)
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        result = await client.get_part("|".join(f"PART{i:03}" for i in range(11)))
        assert result["error"].startswith("Mouser takes up to 10 part numbers per call, separated by |; got 11.")
        assert sent == [] and q.status()["used_today"] == 0

    async def test_bad_lengths_are_refused_without_a_request(self, clock):
        q = quota(clock, name="Mouser")
        sent, handler = self.recording()
        client = MouserClient(api_key="k", quota=q)
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        for bad in ("AB", "LM358P|AB", "X" * 41):
            assert "must be 3-40 characters" in (await client.get_part(bad))["error"]
        for empty in ("", " | "):
            assert (await client.get_part(empty))["error"] == "Give at least one Mouser or manufacturer part number."
        assert sent == [] and q.status()["used_today"] == 0

    async def test_spaces_are_trimmed_and_identical_batches_cached(self, clock):
        q = quota(clock, name="Mouser")
        sent, handler = self.recording()
        client = MouserClient(api_key="k", quota=q)
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        first = await client.get_part(" 595-LM358P | NE555P |")  # spaces and a stray "|" are dropped
        assert sent == ["595-LM358P|NE555P"]
        assert await client.get_part("595-LM358P|NE555P") == first  # same batch: from the cache
        assert sent == ["595-LM358P|NE555P"] and q.status()["used_today"] == 1
        # 0.10.0: each part is kept on its own, so the same parts in another order cost nothing
        assert (await client.get_part("NE555P|595-LM358P"))["results"] == first["results"]
        assert len(sent) == 1
        await client.get_part("NE555P|LM358DR")  # only the part not kept yet is sent
        assert sent == ["595-LM358P|NE555P", "LM358DR"]

    async def test_ten_is_fine(self, clock):
        sent, handler = self.recording()
        client = MouserClient(api_key="k", quota=quota(clock, name="Mouser"))
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        assert "error" not in await client.get_part("|".join(f"PART{i:03}" for i in range(10)))
        assert len(sent) == 1
