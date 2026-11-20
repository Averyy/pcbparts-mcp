"""Extra Mouser API keys (MOUSER_API_KEY_2, _3, ...): each used only after the previous key's day is
spent, one per-minute budget for all, a daily refusal pausing only the key that got it, the limit
errors unchanged, and every key redacted. No network: httpx.MockTransport fakes and a fake clock."""

import asyncio
import datetime
import json
import logging

import httpx
import pytest
from fastmcp import Client

from pcbparts_mcp import server, stats
from pcbparts_mcp.cache import SELF_HOSTING_URL, DailyQuota, MouserKeyPool, QuotaStore
from pcbparts_mcp.config import mouser_extra_keys
from pcbparts_mcp.mouser import MouserAPIError, MouserClient, MouserError

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 18, 20, tzinfo=UTC).timestamp()
MIDNIGHT = datetime.datetime(2026, 11, 19, tzinfo=UTC).timestamp()
KEYS = ("mouser-key-one-1111", "mouser-key-two-2222", "mouser-key-three-3333")
OWN_KEY = "Mouser API key (free at https://www.mouser.com/api-hub/)"
ADVICE = (f" To skip the shared limits, run pcbparts-mcp with your own {OWN_KEY}: {SELF_HOSTING_URL}."
          " Meanwhile use jlc_search.")
HEALTH_KEYS = {"used_today", "limit", "api_remaining", "paused_until", "kept_across_restarts"}
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
                         clock=clock, own_key=OWN_KEY) for i in range(n)]
    return MouserKeyPool(quotas, per_minute=per_minute)


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

    def create(quotas, fake):
        n = len(quotas.quotas)
        client = MouserClient(KEYS[0], quota=quotas, extra_keys=KEYS[1:n], clock=clock)
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

    async def test_minute_cap_and_daily_count_are_one_cause_each(self, make, clock, monkeypatch):
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        m = make(pool(clock, n=1, limit=2, per_minute=1), FakeMouser())
        assert "error" not in await m.get_part("PART0A")
        assert "error" in await m.get_part("PART1A")
        clock.advance(60)
        assert "error" not in await m.get_part("PART1A")
        assert "error" in await m.get_part("PART2A")
        day = stats.usage.summary()["days"][0]
        held = day["distributor_limits"]["mouser"]["held_back"]
        assert held["minute_cap"] == held["daily_count"] == 1
        assert sum(held.values()) == day["distributors"]["mouser"]["rate_limited"] == 2

    async def test_daily_pause_and_acceptance_logs_once_without_key_text(self, make, clock, caplog):
        quotas = pool(clock, n=2)
        # Start on key 2, to check the log uses the selected key's number.
        quotas.quotas[0].pause(MIDNIGHT, "invalid_key")
        fake = FakeMouser()
        fake.script(KEYS[1], httpx.Response(403, json=DAILY_403), httpx.Response(403, json=DAILY_403))
        m = make(quotas, fake)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.mouser"):
            assert "error" in await m.get_part("PART0A")
            # A concurrent refusal must not open/update an episode or log another pause.
            m._refused_for_limit(DAILY_403["Errors"][0], 1)
            assert "error" in await m.get_part("PART1A")  # unsent while paused
            clock.advance(3600)
            assert "error" in await m.get_part("PART1A")
            clock.advance(3600)
            assert "error" not in await m.get_part("PART2A")
            assert "error" not in await m.get_part("PART3A")  # only first acceptance logs
        messages = [(r.levelno, r.getMessage()) for r in caplog.records if r.name == "pcbparts_mcp.mouser"]
        assert messages == [
            (logging.WARNING, "Mouser key 2 daily refusal at 2026-11-18T20:00:00+00:00: our count 1/1000; "
                              "tries again at 2026-11-18T21:00:00+00:00"),
            (logging.WARNING, "Mouser key 2 daily refusal at 2026-11-18T21:00:00+00:00: our count 2/1000; "
                              "tries again at 2026-11-18T22:00:00+00:00"),
            (logging.INFO, "Mouser key 2 accepted again at 2026-11-18T22:00:00+00:00; "
                           "daily refusal since 2026-11-18T20:00:00+00:00, after 1 retries")]
        assert len(quotas.quotas[1]._daily_refusals) == 1
        assert not any(key in caplog.text for key in KEYS)

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
                "2026-11-19T00:00:00+00:00, count 1, accepted again 2026-11-19T01:00:00+00:00",
                "2026-11-19T01:00:00+00:00, count 2, accepted again 2026-11-19T02:00:00+00:00",
                "2026-11-19T02:00:00+00:00, count 3, accepted again 2026-11-19T03:00:00+00:00"]),
            "Mouser key 2 kept daily refusals: 2026-11-19T03:00:00+00:00, count 1, still refused"]
        assert not any(key in caplog.text for key in KEYS)
        assert "daily_refusals" not in json.dumps(health)


class TestConfig:
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
    async def test_one_then_two_then_three(self, make, clock):
        quotas = pool(clock, limit=2)
        fake = FakeMouser()
        m = make(quotas, fake)
        for i in range(6):
            assert "error" not in await m.get_part(f"PART{i}A", caller="203.0.113.7")
        assert fake.used == [1, 1, 2, 2, 3, 3]
        assert [q.status()["used_today"] for q in quotas.quotas] == [2, 2, 2]
        assert quotas.callers._counts == {"203.0.113.7": 6}
        # Every key spent: the limit error, with the reset time only (no count to give the keys away)
        assert await m.get_part("PART6A") == {
            "error": f"Mouser daily quota exceeded on this shared server. It resets at 2026-11-19 00:00 UTC.{ADVICE}"}
        assert len(fake.keys) == 6
        assert mouser_stats() == {"sent": 6, "cached": 0, "rate_limited": 1}
        assert m.retry_after() == MIDNIGHT - NOW
        clock.now = MIDNIGHT  # a new UTC day starts on key 1 again
        assert "error" not in await m.get_part("PART7A")
        assert fake.used[-1] == 1

    async def test_one_key_errors_word_for_word(self, make, clock):
        m = make(pool(clock, n=1, limit=1), FakeMouser())
        await m.get_part("PART0A")
        assert await m.get_part("PART1A") == {
            "error": f"Mouser daily quota exceeded (1 requests/day on this shared server). "
                     f"It resets at 2026-11-19 00:00 UTC.{ADVICE}"}

    async def test_a_single_daily_quota_is_a_pool_of_one(self, clock):
        q = DailyQuota("Mouser", 1000, clock=clock, per_minute=1)
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

    async def test_concurrent_batches_cannot_overdraw_a_key(self, make, clock):
        quotas = pool(clock, limit=2)
        keys, all_in = [], asyncio.Event()

        async def handler(request):
            keys.append(KEYS.index(request.url.params["apiKey"]) + 1)
            if len(keys) == 6:
                all_in.set()
            await all_in.wait()  # every request is reserved before any answer comes back
            return httpx.Response(200, json={"Errors": [], "SearchResults": {"Parts": []}})

        m = make(quotas, handler)
        replies = await asyncio.gather(*(m.get_part(f"PART{i}A|PART{i}B") for i in range(8)))
        assert sorted(keys) == [1, 1, 2, 2, 3, 3]
        assert sum("error" in r for r in replies) == 2
        assert [q.status()["used_today"] for q in quotas.quotas] == [2, 2, 2]


class TestDailyRefusals:
    async def test_refusal_on_key_two_pauses_only_key_two(self, make, clock):
        quotas = pool(clock, limit=(1, 1000, 1000))
        fake = FakeMouser()
        fake.script(KEYS[1], httpx.Response(403, json=DAILY_403), httpx.Response(403, json=DAILY_403))
        m = make(quotas, fake)
        k1, k2, k3 = quotas.quotas
        assert "error" not in await m.get_part("PART0A")  # key 1, whose day this spends
        assert "error" not in await m.get_part("PART1A")  # key 2 refused: the same call goes on to key 3
        assert fake.used == [1, 2, 3]
        # An hour from the first refusal: our own count for key 2 is far below its limit (decision
        # 2026-11-18: Mouser's day isn't UTC-aligned, so waiting for midnight wasted most of one)
        assert k2.status()["paused_until"] == "2026-11-18 21:00 UTC"
        assert k1.status()["paused_until"] is None and k3.status()["paused_until"] is None
        assert k1._pause_reason == k3._pause_reason == ""
        assert "error" not in await m.get_part("PART2A")  # key 3 while key 2 waits
        assert fake.used == [1, 2, 3, 3]
        clock.now = MIDNIGHT
        assert "error" not in await m.get_part("PART3A")  # key 1's new day
        assert "error" not in await m.get_part("PART4A")  # key 2 refused again: hourly, key 3 answers
        assert fake.used == [1, 2, 3, 3, 1, 2, 3]
        assert k2.status()["paused_until"] == "2026-11-19 01:00 UTC" and k3.status()["paused_until"] is None
        clock.now = MIDNIGHT + 3600
        assert "error" not in await m.get_part("PART5A")  # Mouser has reset key 2's count
        assert fake.used[-1] == 2 and k2._pause_reason == ""
        assert mouser_stats()["sent"] == 8  # one per request that went out

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
        error = {"error": "Mouser daily quota exceeded (counted by Mouser). Mouser doesn't say when its count resets, "
                          f"so this server tries again at 2026-11-18 21:00 UTC.{ADVICE}"}
        assert await m.get_part("PART0A") == error
        assert fake.used == [1, 2, 3]  # once on each key, no more
        assert await m.get_part("PART1A") == error and len(fake.keys) == 3
        assert mouser_stats() == {"sent": 3, "cached": 0, "rate_limited": 1}
        assert m.retry_after() == 3600  # hourly: our own counts are far below the keys' limits

    async def test_refusals_in_flight_keep_the_hourly_retry(self, make, clock):
        """Two batches refused right after midnight: the second refusal mustn't stretch the hourly
        retry to the next midnight."""
        quotas = pool(clock, n=1)
        quotas.quotas[0].pause_daily_unknown_reset()  # refused for the day at 20:00
        clock.now = MIDNIGHT
        arrived, both = [], asyncio.Event()

        async def handler(request):
            arrived.append(request)
            if len(arrived) == 2:
                both.set()
            await both.wait()
            return httpx.Response(403, json=DAILY_403)

        m = make(quotas, handler)
        a, b = await asyncio.gather(m.get_part("PARTA1|PARTA2"), m.get_part("PARTB1|PARTB2"))
        assert len(arrived) == 2 and a == b
        assert "tries again at 2026-11-19 01:00 UTC" in a["error"]
        assert quotas.quotas[0].status()["paused_until"] == "2026-11-19 01:00 UTC"

    async def test_part_lifecycle_with_every_key_spent(self, make, clock, monkeypatch):
        quotas = pool(clock, limit=0)
        fake = FakeMouser()
        m = make(quotas, fake)
        monkeypatch.setattr(server, "_mouser_client", m)
        monkeypatch.setattr(server, "_digikey_client", None)
        reply = await server.part_lifecycle(parts=["LM358P"])
        assert reply["results"][0]["status"] == "unknown"
        assert reply["retry_after"] == reply["results"][0]["retry_after"] == MIDNIGHT - NOW
        assert fake.keys == []


class TestPerMinute:
    async def test_one_budget_for_every_key(self, make, clock):
        quotas = pool(clock, limit=2, per_minute=5)
        fake = FakeMouser()
        m = make(quotas, fake)
        for i in range(5):
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
        await m.get_part("PART0A")  # key 1's day
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
    def test_counts_and_pauses_survive(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        quotas = pool(clock, limit=2, path=path)
        assert [quotas.acquire()[0] for _ in range(3)] == [0, 0, 1]
        quotas.quotas[2].pause_daily_unknown_reset()
        restarted = pool(clock, limit=2, path=path)
        assert [q.status()["used_today"] for q in restarted.quotas] == [2, 1, 0]
        assert restarted.quotas[2].status()["paused_until"] == "2026-11-18 21:00 UTC"
        assert restarted.acquire() == (1, None)
        assert restarted.acquire()[0] is None
        assert set(json.loads(path.read_text(encoding="utf-8"))) == {"Mouser", "Mouser#2", "Mouser#3"}

    def test_first_key_keeps_the_one_key_count(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        before = DailyQuota("Mouser", 2, store=QuotaStore(path), clock=clock)
        assert before.check() is None and before.check() is None
        assert pool(clock, limit=2, path=path).acquire() == (1, None)


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
        await m.get_part("PART0A")  # key 1's day
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
        assert quotas.acquire() == (0, None)  # key 1's day is spent
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
    async def test_lifespan_pools_every_key(self, monkeypatch, caplog, tmp_path):
        path = tmp_path / "quota.json"
        ignored = f"MOUSER_API_KEY_5 is ignored: {GAP} (MOUSER_API_KEY_4 is)"
        monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", str(path))
        monkeypatch.setattr(server, "MOUSER_API_KEY", KEYS[0])
        monkeypatch.setattr(server, "MOUSER_EXTRA_API_KEYS", list(KEYS[1:]))
        monkeypatch.setattr(server, "MOUSER_KEY_WARNINGS", [ignored])
        with caplog.at_level(logging.INFO):
            async with Client(server.mcp):
                quotas = server._distributor_quotas["mouser"]
                assert isinstance(quotas, MouserKeyPool) and len(quotas.quotas) == 3
                assert server._mouser_client._keys == list(KEYS) and quotas._per_minute == 25
                status = json.loads((await server.health(None)).body)["distributor_quota"]["mouser"]
                assert status == {"used_today": 0, "limit": 1000, "api_remaining": None, "paused_until": None,
                                  "kept_across_restarts": True}
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

    async def test_health_shows_the_key_in_use_only(self, monkeypatch, clock):
        async with Client(server.mcp):
            quotas = pool(clock, limit=2)
            monkeypatch.setitem(server._distributor_quotas, "mouser", quotas)

            async def health():
                status = json.loads((await server.health(None)).body)["distributor_quota"]["mouser"]
                assert set(status) == HEALTH_KEYS
                return status

            quotas.acquire()
            assert await health() == {"used_today": 1, "limit": 2, "api_remaining": None,
                                      "paused_until": None, "kept_across_restarts": False}
            quotas.acquire(), quotas.acquire()  # key 1 spent; key 2 has one
            assert (await health())["used_today"] == 1
            quotas.quotas[1].pause_daily_unknown_reset()  # key 2 refused: key 3 is in use
            assert (await health())["used_today"] == 0 and (await health())["paused_until"] is None
            quotas.acquire(), quotas.acquire()
            status = await health()
            # every key out: key 2 tries again first, an hour after its refusal
            assert status["used_today"] == 2 and status["paused_until"] == "2026-11-18 21:00 UTC"
            public = json.dumps([status, stats.usage.summary(), quotas.acquire()[1]])
            assert not any(text in public for text in ("Mouser#", "key 2", "key 3", "3000", "2000", *KEYS))

    def test_hourly_line_and_switch_log_name_the_key(self, clock, caplog):
        quotas = pool(clock, limit=1)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            for _ in range(3):
                quotas.acquire("203.0.113.7")
            quotas.callers.flush()
        assert [m for m in caplog.messages if "moved to" in m] == [
            "Mouser requests moved to key 2 for 2026-11-18 UTC", "Mouser requests moved to key 3 for 2026-11-18 UTC"]
        assert caplog.messages[-1].endswith("3 from 1 IPs; top: 203.0.113.7 3 (key 2: 1, key 3: 1)")


# Mouser's reply to a key it doesn't know (as other projects record it)
INVALID_KEY = {"Errors": [{"Id": 0, "Code": "Invalid", "Message": "Invalid unique identifier.",
                           "ResourceKey": "InvalidIdentifier", "PropertyName": "API Key"}], "SearchResults": None}


class TestInvalidKey:
    """Review 2026-11-18: a bad extra key (typo, revoked) failed every lookup once key 1's day was
    spent, until midnight, with nothing in the log naming it."""

    async def test_an_extra_key_rejected_waits_for_the_next_day_and_the_request_moves_on(self, make, clock, caplog):
        quotas = pool(clock, limit=(1, 1000, 1000))
        fake = FakeMouser(part("PART1A"))
        fake.script(KEYS[1], httpx.Response(200, json=INVALID_KEY))
        m = make(quotas, fake)
        assert "error" not in await m.get_part("PART0A")  # key 1's day
        with caplog.at_level(logging.ERROR, logger="pcbparts_mcp.mouser"):
            assert (await m.get_part("PART1A"))["total"] == 1
        assert fake.used == [1, 2, 3]
        assert "Mouser rejected API key 2 as invalid" in caplog.text and "MOUSER_API_KEY_2" in caplog.text
        assert not any(key in caplog.text for key in KEYS)
        assert quotas.quotas[1].status()["paused_until"] == "2026-11-19 00:00 UTC"
        assert "error" not in await m.get_part("PART2A") and fake.used[-1] == 3  # key 2 stays out
        clock.now = MIDNIGHT
        await m.get_part("PART3A")
        await m.get_part("PART4A")
        assert fake.used[-2:] == [1, 2]  # a new day: key 2 is tried again

    async def test_the_last_key_rejected_gives_the_shared_daily_error(self, make, clock):
        quotas = pool(clock, n=2, limit=(1, 1000))
        fake = FakeMouser()
        fake.script(KEYS[1], httpx.Response(200, json=INVALID_KEY))
        m = make(quotas, fake)
        await m.get_part("PART0A")
        reply = await m.get_part("PART1A")
        assert reply["error"].startswith("Mouser daily quota exceeded on this shared server. It resets at 2026-11-19 00:00 UTC.")
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
