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


class Gate:
    """The pool window's sleep: waits until the test opens it."""

    def __init__(self):
        self.opened = asyncio.Event()

    async def __call__(self, seconds):
        await self.opened.wait()


async def settle():
    """Let started lookups reach the pool and its timer start."""
    for _ in range(5):
        await asyncio.sleep(0)


@pytest.fixture
async def make(clock):
    made = []

    def create(quotas, fake, pool_window=0, sleep=None):
        n = len(quotas.quotas)
        client = MouserClient(KEYS[0], quota=quotas, extra_keys=KEYS[1:n], clock=clock, pool_window=pool_window,
                              **({"sleep": sleep} if sleep else {}))
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(fake))
        made.append(client)
        return client

    yield create
    for client in made:
        await client.close()


def mouser_stats():
    return stats.usage.summary()["days"][0]["distributors"]["mouser"]


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
        assert k2.status()["paused_until"] == "2026-11-19 00:00 UTC"
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
                          f"so this server tries again at 2026-11-19 00:00 UTC.{ADVICE}"}
        assert await m.get_part("PART0A") == error
        assert fake.used == [1, 2, 3]  # once on each key, no more
        assert await m.get_part("PART1A") == error and len(fake.keys) == 3
        assert mouser_stats() == {"sent": 3, "cached": 0, "rate_limited": 1}
        assert m.retry_after() == MIDNIGHT - NOW

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


class TestRestart:
    def test_counts_and_pauses_survive(self, tmp_path, clock):
        path = tmp_path / "quota.json"
        quotas = pool(clock, limit=2, path=path)
        assert [quotas.acquire()[0] for _ in range(3)] == [0, 0, 1]
        quotas.quotas[2].pause_daily_unknown_reset()
        restarted = pool(clock, limit=2, path=path)
        assert [q.status()["used_today"] for q in restarted.quotas] == [2, 1, 0]
        assert restarted.quotas[2].status()["paused_until"] == "2026-11-19 00:00 UTC"
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


class TestPooledAndStored:
    async def test_pooled_lookups_share_a_request_on_the_next_key(self, make, clock):
        gate = Gate()
        quotas = pool(clock, limit=(1, 1000, 1000))
        fake = FakeMouser(part("LM358P"), part("NE555P"))
        m = make(quotas, fake, pool_window=0.1, sleep=gate)
        assert quotas.acquire() == (0, None)  # key 1's day is spent
        tasks = [asyncio.create_task(m.get_part(n, caller="198.51.100.1")) for n in ("LM358P", "NE555P", "lm358p")]
        await settle()
        assert fake.keys == []
        gate.opened.set()
        a, b, c = await asyncio.gather(*tasks)
        assert fake.sent == ["LM358P|NE555P"] and fake.used == [2]
        assert [r["mfr_part_number"] for r in a["results"]] == ["LM358P"]
        # The same answer, with requested as each caller spelled it
        assert [r["requested"] for r in c["results"]] == ["lm358p"]
        assert a == {**c, "results": [{**r, "requested": "LM358P"} for r in c["results"]]}
        assert [r["mfr_part_number"] for r in b["results"]] == ["NE555P"]
        # Kept per part: asking again costs nothing on any key
        assert (await m.get_part("NE555P|LM358P"))["total"] == 2
        assert len(fake.keys) == 1
        assert [q.status()["used_today"] for q in quotas.quotas] == [1, 1, 0]
        assert mouser_stats() == {"sent": 1, "cached": 1, "rate_limited": 0}

    async def test_pooled_request_refused_goes_on(self, make, clock):
        gate = Gate()
        quotas = pool(clock)
        fake = FakeMouser(part("LM358P"), part("NE555P"))
        fake.script(KEYS[0], httpx.Response(403, json=DAILY_403))
        m = make(quotas, fake, pool_window=0.1, sleep=gate)
        tasks = [asyncio.create_task(m.get_part(n)) for n in ("LM358P", "NE555P")]
        await settle()
        gate.opened.set()
        a, b = await asyncio.gather(*tasks)
        assert a["total"] == 1 and b["total"] == 1
        assert fake.used == [1, 2] and fake.sent == ["LM358P|NE555P"] * 2
        assert mouser_stats()["sent"] == 2


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
            assert status["used_today"] == 2 and status["paused_until"] == "2026-11-19 00:00 UTC"
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
