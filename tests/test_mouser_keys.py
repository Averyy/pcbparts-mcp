"""Mouser rotation, history, shared limits and redaction: fake HTTP and time only."""

import asyncio
import datetime
import json
import logging
import runpy
from types import SimpleNamespace

import httpx
import pytest
from fastmcp import Client

from pcbparts_mcp import config, server, stats
from pcbparts_mcp.cache import SELF_HOSTING_URL, DailyQuota, MouserKeyPool, QuotaStore, _utc_text
from pcbparts_mcp.config import mouser_extra_keys
from pcbparts_mcp.mouser import MouserAPIError, MouserClient, MouserError

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 18, 20, tzinfo=UTC).timestamp()
MIDNIGHT = datetime.datetime(2026, 11, 19, tzinfo=UTC).timestamp()
MOUSER_RESET = MIDNIGHT + 6 * 3600
KEYS = ("mouser-key-one-1111", "mouser-key-two-2222", "mouser-key-three-3333")
OWN_KEY = "Mouser API key (free at https://www.mouser.com/api-hub/)"
ADVICE = (f" To skip the shared limits, run pcbparts-mcp with your own {OWN_KEY}: {SELF_HOSTING_URL}."
          " Meanwhile use jlc_search.")
STATUS_KEYS = {"used_today", "limit", "api_remaining", "paused_until", "resets_at", "kept_across_restarts"}
DAILY_403 = {"Errors": [{"Code": "TooManyRequests", "Message": "Maximum calls per day exceeded.",
                         "ResourceKey": "MaxCallPerDay"}]}
MINUTE_403 = {"Errors": [{"Code": "TooManyRequests", "Message": "Maximum calls per minute exceeded."}]}
GAP = "extra Mouser keys are read from MOUSER_API_KEY_2 up, in order, until one is missing"


class Clock:
    def __init__(self):
        self.now = NOW

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock():
    return Clock()


def pool(clock, n=3, limit=1000, path=None, per_minute=25):
    """The server's Mouser pool: n keys, each with its own day (limit: one for all, or one each)."""
    store = QuotaStore(path) if path else None
    limits = limit if isinstance(limit, tuple) else (limit,) * n
    quotas = [DailyQuota("Mouser", limits[i], store=store, store_key="Mouser" if i == 0 else f"Mouser#{i + 1}",
                         clock=clock, own_key=OWN_KEY, day_start_hour=config.MOUSER_DAY_START_HOUR) for i in range(n)]
    return MouserKeyPool(quotas, per_minute=per_minute)


def refuse(quotas, index):
    quotas.refuse_daily(index, quotas.sent(index), quotas.quotas[index]._count)


def part(mpn):
    return {"MouserPartNumber": f"595-{mpn}", "ManufacturerPartNumber": mpn, "Manufacturer": "TI",
            "Description": "", "Category": "", "AvailabilityInStock": "100", "Min": "1",
            "PriceBreaks": [], "ProductAttributes": []}


class FakeMouser:
    """Answers like Mouser's loose search (listed parts whose MPN starts with a number asked), or
    with the next reply scripted for the key the request came with. Records each request's key."""

    def __init__(self, *parts):
        self.parts = list(parts)
        self.scripted: dict[str, list[httpx.Response]] = {}
        self.keys: list[str] = []
        self.sent: list[str] = []

    def script(self, key, *responses):
        self.scripted.setdefault(key, []).extend(responses)

    def __call__(self, request):
        key = request.url.params["apiKey"]
        numbers = json.loads(request.content)["SearchByPartRequest"]["mouserPartNumber"]
        self.keys.append(key)
        self.sent.append(numbers)
        if self.scripted.get(key):
            return self.scripted[key].pop(0)
        asked = [n.upper() for n in numbers.split("|")]
        hits = [p for p in self.parts if any(p["ManufacturerPartNumber"].upper().startswith(a) for a in asked)]
        return httpx.Response(200, json={"Errors": [], "SearchResults": {"NumberOfResult": len(hits), "Parts": hits}})

    @property
    def used(self):
        """Which key (1, 2, 3) each request went out with."""
        return [KEYS.index(key) + 1 for key in self.keys]


@pytest.fixture
async def make(clock):
    made = []

    async def no_sleep(seconds):
        """Waits take no real time and leave the fake clock where it is, as a real sleep would."""


    def create(quotas, fake):
        n = len(quotas.quotas)
        client = MouserClient(KEYS[0], quota=quotas, extra_keys=KEYS[1:n], clock=clock, sleep=no_sleep)
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(fake))
        made.append(client)
        return client

    yield create
    for client in made:
        await client.close()


def mouser_stats():
    return stats.usage.summary()["days"][0]["distributors"]["mouser"]


class TestLimitStatsAndLogs:
    @pytest.mark.parametrize("body,label,cause", [(DAILY_403, "daily", "distributor_daily"),
                                                  (MINUTE_403, "minute", "distributor_minute")],
                             ids=["day", "min"])
    async def test_refusals_sent_and_held_back_add_up(self, make, clock, monkeypatch, body, label, cause):
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        fake = FakeMouser()
        fake.script(KEYS[0], httpx.Response(403, json=body))
        m = make(pool(clock, n=1), fake)
        for i in range(4):
            assert "error" in await m.get_part(f"PART{i}A")
        day = stats.usage.summary()["days"][0]
        counts = day["distributor_limits"]["mouser"]
        assert counts["refusals"][label] == 1 and sum(counts["refusals"].values()) == 1
        assert counts["held_back"][cause] == 3
        assert sum(counts["held_back"].values()) == day["distributors"]["mouser"]["rate_limited"] == 3
        assert sum(counts["held_back_hours"]) == 3
        assert day["distributors"]["mouser"]["sent"] == len(fake.sent) == 1
        public = json.dumps([day, m._quota.status()])
        assert all(text not in public for text in (*KEYS, "daily_refusals", "resumed_at", "key 1"))

    async def test_bare_429_with_none_left_counts_as_a_daily_refusal(self, make, clock, monkeypatch):
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        fake = FakeMouser()
        fake.script(KEYS[0], httpx.Response(429, headers={"x-ratelimit-remaining": "0",
                                                          "x-ratelimit-resettime": "2026-11-20T00:00:00Z"}))
        m = make(pool(clock, n=1), fake)
        assert "error" in await m.get_part("PART0A")
        refusals = stats.usage.summary()["days"][0]["distributor_limits"]["mouser"]["refusals"]
        assert refusals == {"daily": 1, "minute": 0, "refused": 0}

    async def test_minute_cap_still_applies_after_daily_count(self, make, clock, monkeypatch):
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        m = make(pool(clock, n=1, limit=2, per_minute=1), FakeMouser())
        assert "error" not in await m.get_part("PART0A")
        assert "error" in await m.get_part("PART1A")
        clock.advance(60)
        assert "error" not in await m.get_part("PART1A")
        assert "error" in await m.get_part("PART2A")
        day = stats.usage.summary()["days"][0]
        held = day["distributor_limits"]["mouser"]["held_back"]
        assert held["minute_cap"] == 2 and held["daily_count"] == 0
        assert sum(held.values()) == day["distributors"]["mouser"]["rate_limited"] == 2

    async def test_daily_refusal_and_acceptance_logs(self, make, clock, caplog):
        quotas = pool(clock, n=2)
        quotas.quotas[0].pause(MIDNIGHT, "invalid_key")
        fake = FakeMouser()
        fake.script(KEYS[1], httpx.Response(403, json=DAILY_403), httpx.Response(403, json=DAILY_403))
        m = make(quotas, fake)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.mouser"):
            assert "error" in await m.get_part("PART0A")
            assert "error" in await m.get_part("PART1A")
            clock.advance(3600)
            assert "error" in await m.get_part("PART1A")
            clock.advance(3600)
            assert "error" not in await m.get_part("PART2A")
            assert "error" not in await m.get_part("PART3A")
        messages = [(r.levelno, r.getMessage()) for r in caplog.records if r.name == "pcbparts_mcp.mouser"]
        assert len(messages) == 3
        for count, (level, message) in enumerate(messages[:2], 1):
            assert level == logging.WARNING
            assert f"Mouser key 2 daily refusal at 2026-11-18T{19 + count}:00:00+00:00" in message
            assert message.endswith(f"our count {count}/1000; next try at 2026-11-18 {20 + count}:00 UTC")
        assert messages[-1] == (logging.INFO, "Mouser key 2 accepted again at 2026-11-18T22:00:00+00:00; "
                                "daily refusal since 2026-11-18T20:00:00+00:00, after 1 retries")
        assert len(quotas.quotas[1]._daily_refusals) == 1
        assert not any(key in caplog.text for key in (*KEYS, "PART0A", "PART1A"))

    async def test_startup_lists_last_five_kept_episodes_per_key(self, clock, tmp_path, monkeypatch, caplog):
        path = tmp_path / "quota.json"
        quotas = pool(clock, path=path)
        for _ in range(7):
            quotas.quotas[0].check()
            quotas.quotas[0].pause_daily_unknown_reset()
            clock.advance(3600)
            quotas.quotas[0].clear_expired_pause()
        quotas.quotas[1].check()
        quotas.quotas[1].pause_daily_unknown_reset()
        monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", str(path))
        monkeypatch.setattr(server, "MOUSER_API_KEY", KEYS[0])
        monkeypatch.setattr(server, "MOUSER_EXTRA_API_KEYS", list(KEYS[1:]))
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.server"):
            async with Client(server.mcp):
                health = json.loads((await server.health(None)).body)
        messages = [m for m in caplog.messages if "kept daily refusals:" in m]
        assert messages == [
            "Mouser key 1 kept daily refusals: " + "; ".join([
                "2026-11-18T22:00:00+00:00, count 3, accepted again 2026-11-18T23:00:00+00:00",
                "2026-11-18T23:00:00+00:00, count 4, accepted again 2026-11-19T00:00:00+00:00",
                "2026-11-19T00:00:00+00:00, count 5, accepted again 2026-11-19T01:00:00+00:00",
                "2026-11-19T01:00:00+00:00, count 6, accepted again 2026-11-19T02:00:00+00:00",
                "2026-11-19T02:00:00+00:00, count 7, accepted again 2026-11-19T03:00:00+00:00"]),
            "Mouser key 2 kept daily refusals: 2026-11-19T03:00:00+00:00, count 1, still refused"]
        assert not any(key in caplog.text for key in KEYS)
        assert "daily_refusals" not in json.dumps(health)


class TestConfig:
    @pytest.mark.parametrize("value,expected,warned", [
        (None, 6, False), ("", 6, False), (" 5 ", 5, False), ("0", 0, False), ("23", 23, False),
        ("24", 6, True), ("-1", 6, True), ("six", 6, True), ("6.5", 6, True),
    ], ids=["default", "blank", "valid", "zero", "last", "high", "negative", "text", "float"])
    def test_day_start_setting(self, monkeypatch, value, expected, warned):
        if value is None:
            monkeypatch.delenv("MOUSER_DAY_START_HOUR", raising=False)
        else:
            monkeypatch.setenv("MOUSER_DAY_START_HOUR", value)
        settings = runpy.run_path(config.__file__)
        assert settings["MOUSER_DAY_START_HOUR"] == expected
        warnings = [w for w in settings["CONFIG_WARNINGS"] if w.startswith("MOUSER_DAY_START_HOUR=")]
        assert len(warnings) == int(warned)
        assert not warnings or "using 6" in warnings[0]

    @pytest.mark.parametrize("hour", [0, 5, 23])
    def test_configured_hour_controls_day_and_reset(self, monkeypatch, clock, hour):
        monkeypatch.setattr(config, "MOUSER_DAY_START_HOUR", hour)
        reset = MIDNIGHT + hour * 3600
        clock.now = reset - 1
        quotas = pool(clock, n=1)
        quotas.quotas[0]._count = 499
        quotas.acquire()
        q = quotas.quotas[0]
        assert q._date == datetime.date(2026, 11, 18)
        assert q.next_reset() == reset
        refuse(quotas, 0)
        assert q._paused_until == reset + 60
        clock.now = reset
        assert q.status()["used_today"] == 0 and q._date == datetime.date(2026, 11, 19)
        assert DailyQuota("DigiKey", 1000, clock=clock).next_reset() == MIDNIGHT + 86400

    def test_read_in_order_until_one_is_missing(self):
        env = {"MOUSER_API_KEY_2": " b ", "MOUSER_API_KEY_3": "c", "MOUSER_API_KEY_5": "e"}
        assert mouser_extra_keys(env, first="a") == (
            ["b", "c"], [f"MOUSER_API_KEY_5 is ignored: {GAP} (MOUSER_API_KEY_4 is)"])

    def test_gap_at_two_ignores_the_rest(self):
        env = {"MOUSER_API_KEY_3": "c", "MOUSER_API_KEY_10": "j", "MOUSER_API_KEY_1": "x"}
        keys, warnings = mouser_extra_keys(env, first="a")
        assert keys == []
        assert warnings == [f"MOUSER_API_KEY_{n} is ignored: {GAP} (MOUSER_API_KEY_2 is)" for n in (1, 3, 10)]

    def test_blank_is_missing_and_not_warned(self):
        env = {"MOUSER_API_KEY_2": "", "MOUSER_API_KEY_3": "  ", "MOUSER_API_KEY_X": "x", "MOUSER_BASE": "y"}
        assert mouser_extra_keys(env, first="a") == ([], [])

    def test_repeated_key_skipped_reading_goes_on(self):
        env = {"MOUSER_API_KEY_2": "key-aaa", "MOUSER_API_KEY_3": "key-ccc", "MOUSER_API_KEY_4": "key-ccc ",
               "MOUSER_API_KEY_5": "key-eee"}
        keys, warnings = mouser_extra_keys(env, first="key-aaa")
        assert keys == ["key-ccc", "key-eee"]
        assert warnings == [f"MOUSER_API_KEY_{n} is ignored: it's the same key as an earlier Mouser key" for n in (2, 4)]
        assert "key-" not in " ".join(warnings)

    def test_each_key_needs_its_own_quota(self, clock):
        with pytest.raises(ValueError, match="its own daily quota"):
            MouserClient(KEYS[0], quota=pool(clock, n=2), extra_keys=KEYS[1:])
        with pytest.raises(ValueError, match="its own daily quota"):
            MouserClient(KEYS[0], extra_keys=KEYS[1:])  # no quota to choose a key by


class TestSpillover:
    async def test_counts_do_not_rotate_or_gate(self, make, clock):
        quotas = pool(clock, limit=2)
        fake = FakeMouser()
        m = make(quotas, fake)
        for i in range(6):
            assert "error" not in await m.get_part(f"PART{i}A", caller="203.0.113.7")
        assert fake.used == [1] * 6
        assert [q.status()["used_today"] for q in quotas.quotas] == [6, 0, 0]
        assert quotas.callers._counts == {"203.0.113.7": 6}
        assert m._quota.retry_after() is None
        clock.now = MIDNIGHT
        assert "error" not in await m.get_part("PART7A")
        assert fake.used[-1] == 1 and quotas.status()["used_today"] == 7
        clock.now = MOUSER_RESET
        assert "error" not in await m.get_part("PART8A")
        assert fake.used[-1] == 1 and quotas.status()["used_today"] == 1

    async def test_one_key_ignores_our_count(self, make, clock):
        m = make(pool(clock, n=1, limit=1), FakeMouser())
        await m.get_part("PART0A")
        assert "error" not in await m.get_part("PART1A")
        assert m._quota.status()["used_today"] == 2

    async def test_a_single_daily_quota_is_a_pool_of_one(self, clock):
        q = DailyQuota("Mouser", 1000, clock=clock, per_minute=1, day_start_hour=config.MOUSER_DAY_START_HOUR)
        fake = FakeMouser()
        m = MouserClient(KEYS[0], quota=q, clock=clock)
        m._client = httpx.AsyncClient(transport=httpx.MockTransport(fake))
        try:
            await m.get_part("PART0A")
            assert await m.get_part("PART1A") == {"error": "Mouser lookups are limited to 1 a minute on this shared "
                                                           "server. Try again in 60 s. Meanwhile use jlc_search."}
        finally:
            await m.close()
        assert q.status()["used_today"] == 1 and fake.used == [1]

    async def test_concurrent_refusals_advance_once(self, make, clock, caplog):
        quotas = pool(clock)
        keys, both = [], asyncio.Event()

        async def handler(request):
            key = KEYS.index(request.url.params["apiKey"]) + 1
            keys.append(key)
            if key == 1:
                if keys.count(1) == 2:
                    both.set()
                await both.wait()
                return httpx.Response(403, json=DAILY_403)
            return httpx.Response(200, json={"SearchResults": {"Parts": []}})

        m = make(quotas, handler)
        replies = await asyncio.gather(m.get_part("PARTA1"), m.get_part("PARTB1"))
        assert all("error" not in r for r in replies)
        assert keys == [1, 1, 2, 2]
        assert quotas.active_index() == 1
        assert quotas.quotas[0].daily_refusals()[0]["retries"] == 0
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING and "daily refusal at" in r.message]
        assert len(warnings) == 1
        assert "next try at 2026-11-18 21:00 UTC" in warnings[0].message
        assert not any(key in caplog.text for key in KEYS)


class TestDailyRefusals:


    @pytest.mark.parametrize("refusal", [
        httpx.Response(403, json=DAILY_403),
        httpx.Response(200, json={"Errors": [{"Code": "TooManyRequests", "Message": None,
                                              "ResourceKey": "MaxCallPerDay"}]}),
        httpx.Response(429, headers={"x-ratelimit-remaining": "0", "x-ratelimit-resettime": "2026-11-19T00:00:00Z"}),
    ], ids=["403", "200", "429"])
    async def test_refused_before_our_count_moves_on(self, make, clock, refusal):
        """Mouser can count more than we do (another app on the key): its refusal moves the lookup on."""
        quotas = pool(clock)
        fake = FakeMouser(part("LM358P"))
        fake.script(KEYS[0], refusal)
        m = make(quotas, fake)
        assert (await m.get_part("LM358P"))["total"] == 1
        assert "error" not in await m.get_part("NE555P")
        assert fake.used == [1, 2, 2]
        assert [q.status()["used_today"] for q in quotas.quotas] == [1, 2, 0]

    async def test_every_key_refused_gives_the_existing_error(self, make, clock):
        quotas = pool(clock)
        fake = FakeMouser()
        for key in KEYS:
            fake.script(key, httpx.Response(403, json=DAILY_403))
        m = make(quotas, fake)
        error = {"error": "Mouser daily quota exceeded (counted by Mouser). "
                          f"This server tries again at 2026-11-18 21:00 UTC.{ADVICE}"}
        assert await m.get_part("PART0A") == error
        assert fake.used == [1, 2, 3]  # once on each key, no more
        assert await m.get_part("PART1A") == error and len(fake.keys) == 3
        assert mouser_stats() == {"sent": 3, "cached": 0, "rate_limited": 1}
        assert m.retry_after() == 3600  # hourly: our own counts are far below the keys' limits


    async def test_part_lifecycle_with_every_key_spent(self, make, clock, monkeypatch):
        quotas = pool(clock, limit=0)
        fake = FakeMouser()
        m = make(quotas, fake)
        monkeypatch.setattr(server, "_mouser_client", m)
        monkeypatch.setattr(server, "_digikey_client", None)
        reply = await server.part_lifecycle(parts=["LM358P"])
        assert reply["results"][0]["status"] == "unknown"
        assert reply["retry_after"] == reply["results"][0]["retry_after"] == MOUSER_RESET - NOW
        assert fake.keys == []


class TestPerMinute:
    async def test_one_budget_for_every_key(self, make, clock):
        quotas = pool(clock, limit=2, per_minute=5)
        fake = FakeMouser()
        for key in KEYS[:2]:
            fake.script(key, httpx.Response(200, json={"SearchResults": {"Parts": []}}),
                        httpx.Response(403, json=DAILY_403))
        m = make(quotas, fake)
        for i in range(3):
            assert "error" not in await m.get_part(f"PART{i}A")
        assert fake.used == [1, 1, 2, 2, 3]
        assert await m.get_part("PART5A") == {
            "error": f"Mouser lookups are limited to 5 a minute on this shared server. Try again in 60 s.{ADVICE}"}
        clock.advance(60)
        assert "error" not in await m.get_part("PART6A")
        assert fake.used == [1, 1, 2, 2, 3, 3]

    @pytest.mark.parametrize("refusal,wait", [
        (httpx.Response(403, json=MINUTE_403), 60),
        (httpx.Response(429, headers={"retry-after": "20"}), 20),
    ], ids=["403", "429"])
    async def test_mousers_minute_limit_pauses_every_key(self, make, clock, refusal, wait):
        quotas = pool(clock, limit=(1, 1000, 1000))
        fake = FakeMouser()
        fake.script(KEYS[1], refusal)
        m = make(quotas, fake)
        await m.get_part("PART0A")
        refuse(quotas, 0)
        reply = await m.get_part("PART1A")
        assert reply == {"error": f"Mouser is limiting requests per minute. Try again in {wait} s.{ADVICE}"}
        assert await m.get_part("PART2A") == reply
        assert fake.used == [1, 2]  # not sent again on key 3
        clock.advance(wait)
        assert "error" not in await m.get_part("PART3A")
        assert fake.used == [1, 2, 2]  # key 2 again: a minute's pause isn't its day

    @pytest.mark.parametrize("first", ["daily", "minute"])
    @pytest.mark.parametrize("minute,wait", [
        (httpx.Response(403, json=MINUTE_403), 60),
        (httpx.Response(429, headers={"retry-after": "20"}), 20),
    ], ids=["403", "429"])
    async def test_minute_refusal_kept_beside_a_daily_one(self, make, clock, first, minute, wait):
        """Two batches in flight on key 1: one refused for the day, one for the minute, in either
        order. Key 1's daily pause is the longer, but the minute's refusal still pauses every key:
        the pool mustn't send the next request on key 2 at once."""
        quotas = pool(clock, n=2)
        daily = httpx.Response(403, json=DAILY_403)
        replies = [daily, minute] if first == "daily" else [minute, daily]
        both_in, release = asyncio.Event(), asyncio.Event()

        async def handler(request):
            keys.append(KEYS.index(request.url.params["apiKey"]) + 1)
            if len(keys) == 1:
                await both_in.wait()  # both batches are on key 1 before either answer comes back
                return replies[0]
            if len(keys) == 2:
                both_in.set()
                await release.wait()  # answered once the first batch is done with its answer
                return replies[1]
            return httpx.Response(200, json={"Errors": [], "SearchResults": {"NumberOfResult": 0, "Parts": []}})

        keys = []
        m = make(quotas, handler)
        a = asyncio.create_task(m.get_part("PARTA1|PARTA2"))
        b = asyncio.create_task(m.get_part("PARTB1|PARTB2"))
        await a
        release.set()
        paused = {"error": f"Mouser is limiting requests per minute. Try again in {wait} s.{ADVICE}"}
        assert await b == paused
        assert keys == ([1, 1, 2] if first == "daily" else [1, 1])  # the daily refusal's batch moved on before the minute's
        assert await m.get_part("PARTC1|PARTC2") == paused and len(keys) == (3 if first == "daily" else 2)
        assert quotas.quotas[0].status()["paused_until"] == "2026-11-18 21:00 UTC"  # and key 1's day stays over
        clock.advance(wait)
        assert "error" not in await m.get_part("PARTD1|PARTD2")
        assert keys[-1] == 2


class TestRestart:

    def test_first_key_keeps_the_one_key_count(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        before = DailyQuota("Mouser", 2, store=QuotaStore(path), clock=clock, day_start_hour=config.MOUSER_DAY_START_HOUR)
        assert before.check() is None and before.check() is None
        assert pool(clock, limit=2, path=path).acquire() == (0, None)


class TestRedaction:
    @pytest.fixture(autouse=True)
    def keys(self, monkeypatch):
        monkeypatch.setattr(server, "MOUSER_API_KEY", KEYS[0])
        monkeypatch.setattr(server, "MOUSER_EXTRA_API_KEYS", list(KEYS[1:]))

    async def test_tool_replies_and_logs(self, monkeypatch, caplog):
        class Broken:
            def __init__(self, error):
                self.error = error

            async def get_part(self, *args, **kwargs):
                raise self.error

        replies = []
        with caplog.at_level(logging.ERROR):
            for error in (MouserError("echo " + " ".join(KEYS)), MouserAPIError("X", " ".join(KEYS)),
                          RuntimeError("boom " + " ".join(KEYS))):
                monkeypatch.setattr(server, "_mouser_client", Broken(error))
                replies.append(await server.mouser_get_part(part_number="AAA"))
        assert replies[0] == {"error": "Mouser part lookup failed: echo [redacted] [redacted] [redacted]"}
        assert len(caplog.records) == 3 and caplog.text.count("[redacted]") == 9
        assert not any(key in caplog.text or key in json.dumps(replies) for key in KEYS)

    async def test_client_redacts_mousers_own_text(self, make, clock, monkeypatch, caplog):
        """part_lifecycle logs the client's errors without the tool's _redact."""
        body = {"Errors": [{"Code": "InvalidKey", "Message": f"Key {KEYS[1]} is not valid"}]}
        quotas = pool(clock, limit=(1, 1000, 1000))
        fake = FakeMouser()
        fake.script(KEYS[1], httpx.Response(200, json=body), httpx.Response(200, json=body))
        m = make(quotas, fake)
        await m.get_part("PART0A")
        refuse(quotas, 0)
        with pytest.raises(MouserAPIError) as raised:
            await m.get_part("PART1A")
        assert str(raised.value) == "Mouser API error [InvalidKey]: Key [redacted] is not valid"
        monkeypatch.setattr(server, "_mouser_client", m)
        monkeypatch.setattr(server, "_digikey_client", None)
        with caplog.at_level(logging.WARNING):
            reply = await server.part_lifecycle(parts=["LM358P"])
        assert reply["results"][0]["lookup_failed"] is True
        assert "[redacted]" in caplog.text and not any(key in caplog.text for key in KEYS)

    async def test_limit_detail_without_a_quota(self):
        body = {"Errors": [{"Code": "TooManyRequests", "Message": f"Too many calls for {KEYS[0]}"}]}
        m = MouserClient(KEYS[0])
        m._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(403, json=body)))
        try:
            assert await m.get_part("PART0A") == {
                "error": "Mouser is limiting requests (Too many calls for [redacted]). Try again later."}
        finally:
            await m.close()


class TestStored:
    async def test_a_batch_on_the_next_key_is_kept_per_part(self, make, clock):
        quotas = pool(clock, limit=(1, 1000, 1000))
        fake = FakeMouser(part("LM358P"), part("NE555P"))
        m = make(quotas, fake)
        assert quotas.acquire() == (0, None)
        refuse(quotas, 0)
        batch = await m.get_part("LM358P|NE555P", caller="198.51.100.1")
        assert fake.sent == ["LM358P|NE555P"] and fake.used == [2]
        assert [r["mfr_part_number"] for r in batch["results"]] == ["LM358P", "NE555P"]
        # Kept per part: asking again costs nothing on any key, with requested as spelled
        alone = await m.get_part("lm358p")
        assert [(r["mfr_part_number"], r["requested"]) for r in alone["results"]] == [("LM358P", "lm358p")]
        assert (await m.get_part("NE555P|LM358P"))["total"] == 2
        assert len(fake.keys) == 1
        assert [q.status()["used_today"] for q in quotas.quotas] == [1, 1, 0]
        assert mouser_stats() == {"sent": 1, "cached": 2, "rate_limited": 0}

class TestServer:
    async def test_stats_uses_mouser_day_counts_and_reset(self, monkeypatch, clock, stats_headers):
        async with Client(server.mcp):
            quotas = pool(clock, n=1)
            monkeypatch.setitem(server._distributor_quotas, "mouser", quotas)

            async def quota_status():
                assert "distributor_quota" not in json.loads((await server.health(None)).body)
                response = await server.usage_stats(SimpleNamespace(headers=stats_headers, query_params={}))
                status = json.loads(response.body)["distributor_quota"]["mouser"]
                assert set(status) == STATUS_KEYS
                assert status["resets_at"] == _utc_text(quotas._first.next_reset())
                return status

            quotas.acquire()
            quotas.quotas[0].note_api_usage(999, 1000)
            clock.now = MIDNIGHT
            assert (await quota_status())["used_today"] == 1
            assert (await quota_status())["api_remaining"] == 999
            clock.now = MOUSER_RESET - 1
            assert (await quota_status())["used_today"] == 1
            quotas.quotas[0]._count = 500
            refuse(quotas, 0)
            assert (await quota_status())["paused_until"] == "2026-11-19 06:01 UTC"
            clock.now = MOUSER_RESET
            assert (await quota_status())["used_today"] == 0
            assert (await quota_status())["api_remaining"] is None
            clock.advance(60)
            assert (await quota_status())["paused_until"] is None

    async def test_lifespan_pools_every_key(self, monkeypatch, caplog, tmp_path, stats_headers):
        path = tmp_path / "quota.json"
        ignored = f"MOUSER_API_KEY_5 is ignored: {GAP} (MOUSER_API_KEY_4 is)"
        monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", str(path))
        monkeypatch.setattr(server, "MOUSER_API_KEY", KEYS[0])
        monkeypatch.setattr(server, "MOUSER_EXTRA_API_KEYS", list(KEYS[1:]))
        monkeypatch.setattr(server, "MOUSER_KEY_WARNINGS", [ignored])
        monkeypatch.setattr(server, "MOUSER_DAY_START_HOUR", 9)
        with caplog.at_level(logging.INFO):
            async with Client(server.mcp):
                quotas = server._distributor_quotas["mouser"]
                assert isinstance(quotas, MouserKeyPool) and len(quotas.quotas) == 3
                assert all(q._day_start_hour == 9 for q in quotas.quotas)
                assert server._mouser_client._keys == list(KEYS) and quotas._per_minute == 25
                assert "distributor_quota" not in json.loads((await server.health(None)).body)
                response = await server.usage_stats(SimpleNamespace(headers=stats_headers, query_params={}))
                status = json.loads(response.body)["distributor_quota"]["mouser"]
                assert set(status) == STATUS_KEYS
                assert status["paused_until"] is None
                assert status["resets_at"] == _utc_text(quotas._first.next_reset())
        assert "Mouser client initialized: 3 key(s) (requests today: 0, 0, 0)" in caplog.messages
        assert any(r.levelno == logging.WARNING and r.message == ignored for r in caplog.records)
        assert not any(key in caplog.text for key in KEYS)
        assert set(json.loads(path.read_text(encoding="utf-8"))) == {"Mouser", "Mouser#2", "Mouser#3"}

    async def test_extra_keys_without_the_first(self, monkeypatch, caplog):
        monkeypatch.setattr(server, "MOUSER_EXTRA_API_KEYS", list(KEYS[1:]))
        monkeypatch.setattr(server, "_mouser_client", None)  # an earlier test's server leaves its client
        with caplog.at_level(logging.WARNING):
            async with Client(server.mcp):
                assert server._mouser_client is None and "mouser" not in server._distributor_quotas
        assert "Extra Mouser keys are set without MOUSER_API_KEY: Mouser lookups are off" in caplog.messages

    async def test_stats_shows_the_key_in_use_and_health_omits_quotas(self, monkeypatch, clock, stats_headers):
        async with Client(server.mcp):
            quotas = pool(clock)
            monkeypatch.setitem(server._distributor_quotas, "mouser", quotas)

            async def quota_status():
                assert "distributor_quota" not in json.loads((await server.health(None)).body)
                response = await server.usage_stats(SimpleNamespace(headers=stats_headers, query_params={}))
                status = json.loads(response.body)["distributor_quota"]["mouser"]
                assert set(status) == STATUS_KEYS
                return status

            for _ in range(3):
                quotas.acquire()
            assert (await quota_status())["used_today"] == 3
            refuse(quotas, 0)
            quotas.acquire()
            assert (await quota_status())["used_today"] == 1
            refuse(quotas, 1)
            assert (await quota_status())["used_today"] == 0
            quotas.acquire()
            refuse(quotas, 2)
            status = await quota_status()
            assert status["used_today"] == 1 and status["paused_until"] == "2026-11-18 21:00 UTC"
            public = json.dumps([status, quotas.acquire()[1]])
            assert not any(text in public for text in ("Mouser#", "key 2", "key 3", "3000", "2000", *KEYS))

    def test_hourly_line_and_switch_log_name_the_key(self, clock, caplog):
        clock.now = MIDNIGHT  # the log names the date the Mouser day began
        quotas = pool(clock, limit=1)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            for i in range(3):
                quotas.acquire("203.0.113.7")
                refuse(quotas, i)
            quotas.callers.flush()
        assert [m for m in caplog.messages if "moved to" in m] == [
            "Mouser requests moved to key 2 for the day starting 2026-11-18 06:00 UTC", "Mouser requests moved to key 3 for the day starting 2026-11-18 06:00 UTC"]
        assert caplog.messages[-1].endswith("3 from 1 IPs; top: 203.0.113.7 3 (key 2: 1, key 3: 1)")


# Mouser's reply to a key it doesn't know (as other projects record it)
INVALID_KEY = {"Errors": [{"Id": 0, "Code": "Invalid", "Message": "Invalid unique identifier.",
                           "ResourceKey": "InvalidIdentifier", "PropertyName": "API Key"}], "SearchResults": None}


class TestInvalidKey:
    """Review 2026-11-18: a bad extra key (typo, revoked) failed every lookup once key 1's day was
    spent, until midnight, with nothing in the log naming it."""

    async def test_invalid_keys_become_eligible_at_the_mouser_day_start(self, make, clock):
        clock.now = MOUSER_RESET - 1
        quotas = pool(clock, n=2)
        fake = FakeMouser()
        for key in KEYS[:2]:
            fake.script(key, httpx.Response(200, json=INVALID_KEY))
        m = make(quotas, fake)
        reply = await m.get_part("PART0A")
        assert "resets at 2026-11-19 06:00 UTC" in reply["error"]
        assert all(q._paused_until == MOUSER_RESET for q in quotas.quotas)
        assert m.retry_after() == 1 and fake.used == [1, 2]
        clock.advance(1)
        assert "error" not in await m.get_part("PART0A") and fake.used == [1, 2, 2]

    async def test_an_extra_key_rejected_waits_for_the_next_day_and_the_request_moves_on(self, make, clock, caplog):
        quotas = pool(clock, limit=(1, 1000, 1000))
        fake = FakeMouser(part("PART1A"))
        fake.script(KEYS[1], httpx.Response(200, json=INVALID_KEY))
        m = make(quotas, fake)
        assert "error" not in await m.get_part("PART0A")
        refuse(quotas, 0)
        with caplog.at_level(logging.ERROR, logger="pcbparts_mcp.mouser"):
            assert (await m.get_part("PART1A"))["total"] == 1
        assert fake.used == [1, 2, 3]
        assert "Mouser rejected API key 2 as invalid" in caplog.text and "MOUSER_API_KEY_2" in caplog.text
        assert not any(key in caplog.text for key in KEYS)
        assert quotas.quotas[1].status()["paused_until"] == "2026-11-19 06:00 UTC"
        assert "error" not in await m.get_part("PART2A") and fake.used[-1] == 3  # key 2 stays out
        clock.now = MIDNIGHT
        await m.get_part("PART3A")
        await m.get_part("PART4A")
        assert fake.used[-2:] == [3, 3]  # midnight does not change the current key

    async def test_the_last_key_rejected_gives_the_shared_daily_error(self, make, clock):
        quotas = pool(clock, n=2)
        fake = FakeMouser()
        fake.script(KEYS[1], httpx.Response(200, json=INVALID_KEY))
        m = make(quotas, fake)
        await m.get_part("PART0A")
        refuse(quotas, 0)
        reply = await m.get_part("PART1A")
        assert "This server tries again at 2026-11-18 21:00 UTC" in reply["error"]
        assert "key" not in reply["error"].replace("API key", "")  # never a word about extra keys
        assert await m.get_part("PART2A") == reply and len(fake.keys) == 2

    async def test_the_only_key_rejected_shows_mousers_error(self, make, clock):
        """A self-hoster's typo: Mouser's own message, no pause (nothing else could send)."""
        quotas = pool(clock, n=1)
        fake = FakeMouser()
        fake.script(KEYS[0], httpx.Response(200, json=INVALID_KEY), httpx.Response(200, json=INVALID_KEY))
        m = make(quotas, fake)
        with pytest.raises(MouserAPIError, match=r"\[Invalid\]: Invalid unique identifier"):
            await m.get_part("PART0A|PART1A")
        assert len(fake.keys) == 1  # not asked again number by number
        assert quotas.quotas[0].status()["paused_until"] is None


class TestHttpxLog:
    def test_request_lines_never_show_the_key(self, caplog):
        httpx_log = logging.getLogger("httpx")
        assert httpx_log.getEffectiveLevel() >= logging.WARNING  # not logged at all by default
        with caplog.at_level(logging.INFO, logger="httpx"):
            httpx_log.info('HTTP Request: %s %s "%s"', "POST",
                           httpx.URL(f"https://api.mouser.com/api/v2/search/partnumber?apiKey={KEYS[0]}"), "HTTP/1.1 200 OK")
        assert caplog.records and KEYS[0] not in caplog.text and "apiKey=[redacted]" in caplog.text
