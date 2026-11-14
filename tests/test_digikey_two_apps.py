"""DigiKey daily spillover shares bursts, penalties, caches and public status. No network."""

import asyncio
import datetime
import json
import logging
import time
from urllib.parse import parse_qs

from fastmcp import Client
import httpx
import pytest

from pcbparts_mcp import server, stats
from pcbparts_mcp.cache import DailyQuota, Pacer, QuotaPool, QuotaStore
from pcbparts_mcp.digikey import DigiKeyClient, DigiKeyError

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 14, 21, 15, tzinfo=UTC).timestamp()
MIDNIGHT = datetime.datetime(2026, 11, 15, tzinfo=UTC).timestamp()
CREDS = ("first-client-id", "first-client-secret", "second-client-id", "second-client-secret")
HEALTH_KEYS = {"used_today", "limit", "api_remaining", "paused_until", "kept_across_restarts"}
DAILY_HEADERS = {"x-ratelimit-remaining": "0", "x-ratelimit-resettime": "2026-11-15T00:00:00Z"}


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


def pool(clock, limit=1000, path=None, per_minute=100):
    store = QuotaStore(path) if path else None
    quotas = [DailyQuota("DigiKey", limit, store=store, store_key=key, clock=clock,
                         own_key="DigiKey API credentials") for key in ("DigiKey", "DigiKey#2")]
    return QuotaPool(quotas, per_minute=per_minute)


def ok(headers=None):
    return httpx.Response(200, json={"ExactMatches": [{
        "ManufacturerProductNumber": "AO3400A", "Manufacturer": {"Name": "AOS"}, "QuantityAvailable": 10,
    }]}, headers=headers)


class FakeDigiKey:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []
        self.tokens = []

    def __call__(self, request):
        if "oauth2/token" in str(request.url):
            creds = parse_qs(request.content.decode())
            self.tokens.append(creds)
            return httpx.Response(200, json={"access_token": f"token-{creds['client_id'][0]}-{len(self.tokens)}", "expires_in": 599})
        self.requests.append(request)
        assert request.method == "POST" and request.url.path.endswith("/search/keyword")
        assert request.headers["Authorization"].startswith(f"Bearer token-{request.headers['X-DIGIKEY-Client-Id']}-")
        return self.responses.pop(0)

    @property
    def apps(self):
        return [request.headers["X-DIGIKEY-Client-Id"] for request in self.requests]


@pytest.fixture
async def client(clock):
    clients = []

    def create(quotas, *responses):
        fake = FakeDigiKey(*responses)
        result = DigiKeyClient(*CREDS[:2], quota=quotas, second_app=CREDS[2:])
        result._http = httpx.AsyncClient(transport=httpx.MockTransport(fake))

        async def sleep(seconds):
            await asyncio.sleep(0)

        result._pacer = Pacer(5, clock=clock, sleep=sleep)
        clients.append(result)
        return result, fake

    yield create
    for result in clients:
        await result.close()


async def test_first_app_until_its_count_limit_then_second(client, clock):
    quotas = pool(clock, limit=2)
    dk, fake = client(quotas, ok(), ok(), ok())
    for pn in ("A", "B", "C"):
        assert (await dk.get_part(pn))["total"] == 1
    assert fake.apps == [CREDS[0], CREDS[0], CREDS[2]]
    assert [q.status()["used_today"] for q in quotas.quotas] == [2, 1]
    assert [t["client_secret"][0] for t in fake.tokens] == [CREDS[1], CREDS[3]]
    assert dk._apps[0].access_token != dk._apps[1].access_token
    assert dk._apps[0].token_lock is not dk._apps[1].token_lock
    assert all(q.callers is quotas.callers and q._minute is None for q in quotas.quotas)


async def test_success_with_remaining_zero_moves_next_lookup_to_second(client, clock):
    quotas = pool(clock)
    dk, fake = client(quotas, ok(DAILY_HEADERS), ok())
    assert (await dk.get_part("A"))["total"] == 1
    assert quotas.status()["api_remaining"] is None
    assert quotas.status()["paused_until"] is None
    assert (await dk.get_part("B"))["total"] == 1
    assert fake.apps == [CREDS[0], CREDS[2]]
    assert quotas.quotas[0].status()["api_remaining"] == 0


async def test_daily_429_retries_once_on_second_and_counts_both(client, clock):
    quotas = pool(clock)
    dk, fake = client(quotas, httpx.Response(429, headers=DAILY_HEADERS), ok())
    assert (await dk.get_part("AO3400A", caller="203.0.113.7"))["total"] == 1
    assert fake.apps == [CREDS[0], CREDS[2]]
    assert [json.loads(r.content) for r in fake.requests] == [{"Keywords": "AO3400A", "Limit": 10, "Offset": 0}] * 2
    assert [q.status()["used_today"] for q in quotas.quotas] == [1, 1]
    assert quotas.callers._counts == {"203.0.113.7": 2}
    assert stats.usage.summary()["totals"]["distributors"]["digikey"]["sent"] == 2


async def test_both_daily_429s_stop_without_third_attempt(client, clock):
    dk, fake = client(pool(clock), *(httpx.Response(429, headers=DAILY_HEADERS) for _ in range(2)))
    result = await dk.get_part("A")
    assert result["error"].startswith("DigiKey daily quota exceeded on this shared server. It resets at 2026-11-15 00:00 UTC.")
    assert fake.apps == [CREDS[0], CREDS[2]]
    assert await dk.get_part("B") == result
    assert len(fake.requests) == 2


async def test_both_spent_error_has_reset_and_advice_without_request_count(client, clock):
    quotas = pool(clock, limit=1)
    assert quotas.acquire() == (0, None)
    assert quotas.acquire() == (1, None)
    dk, fake = client(quotas)
    result = await dk.get_part("A")
    assert result == {"error": "DigiKey daily quota exceeded on this shared server. It resets at 2026-11-15 00:00 UTC. "
                     "To skip the shared limits, run pcbparts-mcp with your own DigiKey API credentials: "
                     "https://github.com/Averyy/pcbparts-mcp#self-hosting. Meanwhile use jlc_search."}
    assert "requests/day" not in result["error"] and "1000" not in result["error"]
    assert fake.tokens == fake.requests == []


async def test_utc_midnight_returns_to_first_app(client, clock):
    quotas = pool(clock, limit=1)
    dk, fake = client(quotas, ok(), ok(), ok())
    await dk.get_part("A")
    await dk.get_part("B")
    clock.now = MIDNIGHT
    assert (await dk.get_part("C"))["total"] == 1
    assert fake.apps == [CREDS[0], CREDS[2], CREDS[0]]
    assert [q.status()["used_today"] for q in quotas.quotas] == [1, 0]


def test_restart_keeps_both_counts_and_original_store_key(tmp_path, clock):
    path = tmp_path / "quota.json"
    original = DailyQuota("DigiKey", 2, store=QuotaStore(path), clock=clock)
    original.check()
    quotas = pool(clock, limit=2, path=path)
    assert quotas.acquire() == (0, None)
    assert quotas.acquire() == (1, None)
    restarted = pool(clock, limit=2, path=path)
    assert [q.status()["used_today"] for q in restarted.quotas] == [2, 1]
    assert restarted.acquire() == (1, None)
    assert set(json.loads(path.read_text(encoding="utf-8"))) == {"DigiKey", "DigiKey#2"}


@pytest.mark.parametrize("status,headers,wait,wording", [
    (429, {"retry-after": "30", "x-ratelimit-remaining": "900"}, 30, "limiting requests per minute"),
    (429, {}, 60, "limiting requests per minute"),
    (403, {}, 600, "refused this server's requests (HTTP 403)"),
    (403, DAILY_HEADERS, 600, "refused this server's requests (HTTP 403)"),
])
async def test_penalties_pause_both_and_survive_restart(client, clock, tmp_path, status, headers, wait, wording):
    path = tmp_path / "quota.json"
    quotas = pool(clock, path=path)
    dk, fake = client(quotas, httpx.Response(status, headers=headers))
    result = await dk.get_part("A")
    assert wording in result["error"] and f"{wait} s." in result["error"]
    assert await dk.get_part("B") == result
    assert fake.apps == [CREDS[0]]
    # A daily pause on one app must not hide the shorter penalty from the other app.
    quotas.quotas[0].pause(MIDNIGHT, "daily")
    restarted = pool(clock, path=path)
    assert restarted.acquire()[0] is None
    assert wording in restarted.acquire()[1]["error"]
    assert all(q._shared_paused_until == NOW + wait for q in restarted.quotas)
    clock.advance(wait)
    assert restarted.acquire() == (1, None)


def test_shared_minute_budget_spans_both_apps(clock):
    quotas = pool(clock, limit=60)
    assert [quotas.acquire()[0] for _ in range(100)] == [0] * 60 + [1] * 40
    index, result = quotas.acquire()
    assert index is None and "limited to 100 a minute" in result["error"]
    assert [q.status()["used_today"] for q in quotas.quotas] == [60, 40]
    clock.advance(60)
    assert quotas.acquire() == (1, None)


@pytest.mark.parametrize("response", [ok(), httpx.Response(404)])
async def test_cache_is_shared_after_switching_apps(client, clock, response):
    dk, fake = client(pool(clock, limit=1), response, ok())
    first = await dk.get_part("A")
    assert await dk.get_part("A") == first
    await dk.get_part("B")
    assert await dk.get_part("A") == first
    assert fake.apps == [CREDS[0], CREDS[2]]


async def test_concurrent_acquires_cannot_overdraw_either_app(clock):
    quotas = pool(clock, limit=7)

    async def acquire():
        await asyncio.sleep(0)
        return quotas.acquire()[0]

    results = await asyncio.gather(*(acquire() for _ in range(50)))
    assert results == [0] * 7 + [1] * 7 + [None] * 36
    assert [q.status()["used_today"] for q in quotas.quotas] == [7, 7]


async def test_second_app_401_refreshes_only_its_token_once(client, clock):
    quotas = pool(clock, limit=2)
    quotas.acquire(), quotas.acquire()  # app 1's day is spent
    dk, fake = client(quotas, httpx.Response(401), httpx.Response(401))
    with pytest.raises(DigiKeyError, match="DigiKey API returned HTTP 401"):
        await dk.get_part("A")
    assert fake.apps == [CREDS[2], CREDS[2]]
    assert [t["client_id"][0] for t in fake.tokens] == [CREDS[2], CREDS[2]]
    assert dk._apps[0].access_token is None
    # The resend is a request too: counted on app 2's day (review finding)
    assert [q.status()["used_today"] for q in quotas.quotas] == [2, 2]


async def test_second_app_401_can_succeed_after_refresh(client, clock):
    quotas = pool(clock, limit=2)
    quotas.acquire(), quotas.acquire()
    dk, fake = client(quotas, httpx.Response(401), ok())
    assert (await dk.get_part("A"))["total"] == 1
    assert fake.apps == [CREDS[2], CREDS[2]]
    assert len(fake.tokens) == 2
    assert [q.status()["used_today"] for q in quotas.quotas] == [2, 2]


def configure(monkeypatch, second=True):
    for name, value in zip(("DIGIKEY_CLIENT_ID", "DIGIKEY_CLIENT_SECRET", "DIGIKEY_CLIENT_ID_2", "DIGIKEY_CLIENT_SECRET_2"), CREDS):
        monkeypatch.setattr(server, name, value if second or not name.endswith("_2") else "")


@pytest.mark.parametrize("missing", ["DIGIKEY_CLIENT_ID_2", "DIGIKEY_CLIENT_SECRET_2"])
async def test_half_set_second_pair_logs_missing_name_and_runs_one_app(monkeypatch, caplog, missing):
    configure(monkeypatch)
    monkeypatch.setattr(server, missing, "")
    with caplog.at_level(logging.INFO):
        async with Client(server.mcp):
            assert len(server._digikey_client._apps) == 1
            assert len(server._distributor_quotas["digikey"].quotas) == 1
    assert any(r.levelno == logging.ERROR and missing in r.message for r in caplog.records)
    assert "DigiKey client initialized: 1 app(s) (requests today: 0)" in caplog.messages
    assert all(secret not in caplog.text for secret in CREDS)


async def test_health_shape_and_active_app_and_no_credentials(monkeypatch, clock, caplog):
    configure(monkeypatch)
    with caplog.at_level(logging.INFO):
        async with Client(server.mcp):
            assert "DigiKey client initialized: 2 app(s) (requests today: 0, 0)" in caplog.messages
            quotas = pool(clock, limit=2)
            monkeypatch.setitem(server._distributor_quotas, "digikey", quotas)
            quotas.quotas[0].check()
            quotas.quotas[0].note_api_usage(5, 1000)
            status = json.loads((await server.health(None)).body)["distributor_quota"]["digikey"]
            assert set(status) == HEALTH_KEYS
            assert status == {"used_today": 1, "limit": 2, "api_remaining": 5,
                              "paused_until": None, "kept_across_restarts": False}
            quotas.quotas[0].pause(MIDNIGHT, "daily")
            quotas.acquire()
            status = json.loads((await server.health(None)).body)["distributor_quota"]["digikey"]
            assert set(status) == HEALTH_KEYS and status["used_today"] == 1 and status["paused_until"] is None
            quotas.acquire()
            status = json.loads((await server.health(None)).body)["distributor_quota"]["digikey"]
            assert status["used_today"] == 2 and status["paused_until"] == "2026-11-15 00:00 UTC"
            public = json.dumps([status, stats.usage.summary(), quotas.acquire()[1]])
            assert all(secret not in public for secret in CREDS)
            assert "app 2" not in public and "DigiKey#2" not in public


async def test_error_redacts_all_app_credentials(monkeypatch):
    configure(monkeypatch)

    class Broken:
        async def get_part(self, *args, **kwargs):
            raise DigiKeyError("echo " + " ".join(CREDS))

    monkeypatch.setattr(server, "_digikey_client", Broken())
    result = await server.digikey_get_part("A")
    assert result == {"error": "DigiKey part lookup failed: echo " + " ".join(["[redacted]"] * 4)}


def test_one_tally_logs_second_app_count_once_per_hour_and_switch_once_per_day(clock, caplog, tmp_path):
    path = tmp_path / "quota.json"
    quotas = pool(clock, limit=1, path=path)
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
        quotas.acquire("203.0.113.7")
        quotas.acquire("203.0.113.7")
        quotas.callers.flush()
        assert sum("requests moved to app 2" in message for message in caplog.messages) == 1
        assert len([m for m in caplog.messages if "requests sent" in m]) == 1
        assert caplog.messages[-1].endswith("2 from 1 IPs; top: 203.0.113.7 2 (app 2: 1)")
        # Restart in the same day doesn't repeat the switch log.
        restarted = pool(clock, limit=2, path=path)
        restarted.acquire()
        restarted.acquire()
        assert sum("requests moved to app 2" in message for message in caplog.messages) == 1
        clock.now = MIDNIGHT
        restarted.acquire()
        restarted.acquire()
        restarted.acquire()
        assert sum("requests moved to app 2" in message for message in caplog.messages) == 2


def test_reset_time_accounts_for_our_count_and_reports_first_available_app(clock):
    quotas = pool(clock, limit=1)
    assert quotas.acquire() == (0, None)
    assert quotas.acquire() == (1, None)
    quotas.note_response(0, 429, {"x-ratelimit-remaining": "0", "retry-after": "30"})
    assert "2026-11-15 00:00 UTC" in quotas.acquire()[1]["error"]
    assert quotas.status()["paused_until"] == "2026-11-15 00:00 UTC"
    # When API pauses are the only limit, the earlier reset is when requests can resume.
    quotas = pool(clock)
    quotas.quotas[0].pause(NOW + 30, "daily")
    quotas.quotas[1].pause(NOW + 120, "daily")
    assert quotas.status()["paused_until"] == "2026-11-14 21:15 UTC"
    clock.advance(30)
    assert quotas.acquire() == (0, None)
    assert quotas.status()["paused_until"] is None


def preset_tokens(dk):
    """Both apps hold valid tokens, so the test sees only product requests."""
    for app in dk._apps:
        app.access_token, app.token_expires_at = f"token-{app.client_id}-0", time.time() + 600


def held_first_answer(first, later, second_queued):
    """A DigiKey that holds the first product answer until the second lookup is waiting in the
    pacer queue, and checks every request uses its own app's token."""
    sent = []

    async def handler(request):
        assert "oauth2/token" not in str(request.url), "no token requests expected"
        client_id = request.headers["X-DIGIKEY-Client-Id"]
        assert request.headers["Authorization"] == f"Bearer token-{client_id}-0", "token of another app"
        sent.append(client_id)
        if len(sent) == 1:
            await second_queued.wait()
            return first
        return later

    return handler, sent


def queue_until(second_queued, condition):
    """The pacer sleep: mark the lookup as queued, then hold it until `condition()` holds."""
    async def sleep(seconds):
        second_queued.set()
        for _ in range(1000):
            if condition():
                return
            await asyncio.sleep(0)
        raise AssertionError("condition never held")
    return sleep


async def test_lookup_queued_when_first_app_runs_out_goes_to_second_app(clock):
    # Review finding: a lookup already waiting in the pacer queue when DigiKey said app 1's day was
    # used up still went to app 1 (and was refused). It must re-check and go to app 2, with app 2's
    # token. The first answer is held until the second lookup is in the queue.
    quotas, second_queued = pool(clock), asyncio.Event()
    handler, sent = held_first_answer(ok(DAILY_HEADERS), ok(), second_queued)
    dk = DigiKeyClient(*CREDS[:2], quota=quotas, second_app=CREDS[2:])
    dk._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    preset_tokens(dk)
    dk._pacer = Pacer(5, clock=clock, sleep=queue_until(second_queued, lambda: quotas.active_index() == 1))
    try:
        first, second = await asyncio.gather(dk.get_part("A"), dk.get_part("B"))
    finally:
        await dk.close()
    assert first["total"] == 1 and second["total"] == 1
    assert sent == [CREDS[0], CREDS[2]]
    assert [q.status()["used_today"] for q in quotas.quotas] == [1, 1]


async def test_lookup_queued_during_a_penalty_is_neither_sent_nor_counted(clock):
    # Review finding: a lookup counted before the pacer stayed counted (and logged as sent) when a
    # 403 arrived while it waited, although nothing was sent.
    quotas, second_queued = pool(clock), asyncio.Event()
    handler, sent = held_first_answer(httpx.Response(403), ok(), second_queued)
    dk = DigiKeyClient(*CREDS[:2], quota=quotas, second_app=CREDS[2:])
    dk._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    preset_tokens(dk)
    dk._pacer = Pacer(5, clock=clock, sleep=queue_until(second_queued, lambda: quotas.penalty_error() is not None))
    try:
        first, second = await asyncio.gather(dk.get_part("A", caller="203.0.113.7"),
                                             dk.get_part("B", caller="203.0.113.8"))
    finally:
        await dk.close()
    assert "refused this server's requests (HTTP 403)" in first["error"]
    assert "refused this server's requests (HTTP 403)" in second["error"]
    assert sent == [CREDS[0]]
    assert [q.status()["used_today"] for q in quotas.quotas] == [1, 0]
    assert quotas.callers._counts == {"203.0.113.7": 1}
    digikey = stats.usage.summary()["totals"]["distributors"]["digikey"]
    assert digikey["sent"] == 1 and digikey["rate_limited"] == 1


def paced_by(clock, per_second=10):
    """A pacer on the test clock: its sleep advances that clock, so timing is exact and the same on
    every OS (Windows clocks tick every ~15.6 ms, so wall-clock gaps flake). Exact because the
    pacer lets one caller sleep at a time."""
    async def sleep(seconds):
        clock.advance(seconds)
        await asyncio.sleep(0)
    return Pacer(per_second, clock=clock, sleep=sleep)


def gaps_of(times):
    return [round(later - earlier, 6) for earlier, later in zip(times, times[1:])]  # float noise at ~1.8e9 s


async def test_slow_quota_save_does_not_shorten_the_gap(clock, monkeypatch):
    # Review finding: the pacer counted the gap from when a lookup left the queue, before the
    # synchronous quota save; a slow save let the next request go right after. Test clock.
    sent_at, stalls = [], []

    async def handler(request):
        sent_at.append(clock())
        return ok()

    original = DailyQuota._save

    def slow_save(self):
        if not stalls:
            stalls.append(True)
            clock.advance(0.2)  # one 200 ms write, longer than the 100 ms gap
        original(self)

    dk = DigiKeyClient(*CREDS[:2], quota=pool(clock), second_app=CREDS[2:])
    dk._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    preset_tokens(dk)
    dk._pacer = paced_by(clock)
    monkeypatch.setattr(DailyQuota, "_save", slow_save)
    try:
        await asyncio.gather(*(dk.get_part(f"P{i}") for i in range(4)))
    finally:
        await dk.close()
    assert stalls and len(sent_at) == 4
    assert min(gaps_of(sent_at)) >= 0.1, gaps_of(sent_at)


async def test_token_daily_limit_on_first_app_moves_lookup_to_second(clock):
    # Review finding: a token request answered "day used up" for app 1 failed the lookup instead
    # of moving it to app 2.
    calls = []

    async def handler(request):
        if "oauth2/token" in str(request.url):
            client_id = parse_qs(request.content.decode())["client_id"][0]
            calls.append(client_id)
            if client_id == CREDS[0]:
                return httpx.Response(429, headers=DAILY_HEADERS)
            return httpx.Response(200, json={"access_token": f"token-{client_id}-1", "expires_in": 599})
        calls.append("product " + request.headers["X-DIGIKEY-Client-Id"])
        return ok()

    quotas = pool(clock)
    dk = DigiKeyClient(*CREDS[:2], quota=quotas, second_app=CREDS[2:])
    dk._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def sleep(seconds):
        await asyncio.sleep(0)

    dk._pacer = Pacer(5, clock=clock, sleep=sleep)
    try:
        assert (await dk.get_part("A"))["total"] == 1
    finally:
        await dk.close()
    assert calls == [CREDS[0], CREDS[2], "product " + CREDS[2]]
    assert quotas.active_index() == 1


async def test_401_resend_waits_out_a_daily_pause_on_that_app(client, clock):
    # The resend after a 401 is one more request: not to an app whose day DigiKey reported used up
    # meanwhile; the lookup moves to app 2 instead.
    quotas = pool(clock)
    dk, fake = client(quotas, httpx.Response(401), ok())

    async def sleep(seconds):
        if fake.requests:  # learned from another lookup while this one waited
            quotas.quotas[0].pause(MIDNIGHT, "daily")
        await asyncio.sleep(0)

    dk._pacer = Pacer(5, clock=clock, sleep=sleep)
    assert (await dk.get_part("A"))["total"] == 1
    assert fake.apps == [CREDS[0], CREDS[2]]


async def test_failure_logs_are_redacted_like_replies(monkeypatch, caplog):
    # Review finding: the log line carried the unredacted exception text.
    configure(monkeypatch)
    monkeypatch.setattr(server, "MOUSER_API_KEY", "mouser-api-key-value")

    class Broken:
        def __init__(self, error):
            self.error = error

        async def get_part(self, *args, **kwargs):
            raise self.error

    from pcbparts_mcp.mouser import MouserError
    with caplog.at_level(logging.ERROR):
        for client, call in [
            (Broken(DigiKeyError("echo " + " ".join(CREDS))), server.digikey_get_part),
            (Broken(RuntimeError("boom " + " ".join(CREDS))), server.digikey_get_part),
        ]:
            monkeypatch.setattr(server, "_digikey_client", client)
            await call("A")
        for error in (MouserError("echo mouser-api-key-value"), RuntimeError("boom mouser-api-key-value")):
            monkeypatch.setattr(server, "_mouser_client", Broken(error))
            await server.mouser_get_part("AAA")
    assert len(caplog.records) == 4
    assert all(secret not in caplog.text for secret in (*CREDS, "mouser-api-key-value"))
    assert "[redacted]" in caplog.text


def one_app(clock, fake, limit=1000):
    quotas = QuotaPool([DailyQuota("DigiKey", limit, clock=clock)], per_minute=100)
    dk = DigiKeyClient(*CREDS[:2], quota=quotas)
    dk._http = httpx.AsyncClient(transport=httpx.MockTransport(fake))

    async def sleep(seconds):
        await asyncio.sleep(0)

    dk._pacer = Pacer(5, clock=clock, sleep=sleep)
    return dk, quotas


async def test_slow_token_refresh_does_not_release_a_burst(clock):
    # Review finding: lookups that took their pacer slots before a slow token refresh all sent
    # together when it finished. Test clock: a 300 ms refresh, 100 ms pacing.
    sent_at = []

    async def handler(request):
        if "oauth2/token" in str(request.url):
            clock.advance(0.3)
            await asyncio.sleep(0)
            return httpx.Response(200, json={"access_token": "token-x", "expires_in": 599})
        sent_at.append(clock())
        return ok()

    dk = DigiKeyClient(*CREDS[:2], quota=pool(clock), second_app=CREDS[2:])
    dk._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    dk._pacer = paced_by(clock)
    try:
        results = await asyncio.gather(*(dk.get_part(f"P{i}") for i in range(6)))
    finally:
        await dk.close()
    assert all(r["total"] == 1 for r in results) and len(sent_at) == 6
    assert min(gaps_of(sent_at)) >= 0.1, gaps_of(sent_at)


async def test_no_token_request_while_paused_after_a_401(clock):
    # Review finding: a 401 that also said the day was used up was followed by a token request.
    fake = FakeDigiKey(httpx.Response(401, headers=DAILY_HEADERS))
    dk, quotas = one_app(clock, fake)
    try:
        result = await dk.get_part("A")
    finally:
        await dk.close()
    assert result["error"].startswith("DigiKey daily quota exceeded on this shared server.")
    assert len(fake.requests) == 1 and len(fake.tokens) == 1


async def test_no_token_request_during_a_penalty(client, clock):
    quotas = pool(clock)
    dk, fake = client(quotas, httpx.Response(403))
    await dk.get_part("A")
    dk._apps[0].access_token = None  # the next lookup would need a new token
    assert "HTTP 403" in (await dk.get_part("B"))["error"]
    assert len(fake.tokens) == 1 and len(fake.requests) == 1


async def test_401_resend_is_counted_and_refused_once_the_day_is_spent(clock):
    # Review finding: the resend after a 401 wasn't counted, so it could exceed the day.
    fake = FakeDigiKey(httpx.Response(401), ok())
    dk, quotas = one_app(clock, fake, limit=1)
    try:
        result = await dk.get_part("A")
    finally:
        await dk.close()
    assert result["error"].startswith("DigiKey daily quota exceeded on this shared server.")
    assert len(fake.requests) == 1 and quotas.status()["used_today"] == 1


class TokenEndpoint:
    """Product requests answer ok(); token requests answer from `tokens` (callables or Responses)."""

    def __init__(self, *tokens):
        self.tokens = list(tokens)
        self.token_requests = 0
        self.product_requests = 0

    async def __call__(self, request):
        if "oauth2/token" in str(request.url):
            self.token_requests += 1
            answer = self.tokens.pop(0) if len(self.tokens) > 1 else self.tokens[0]
            return await answer() if callable(answer) else answer
        self.product_requests += 1
        return ok()


def token(expires_in=599):
    return httpx.Response(200, json={"access_token": "token-x", "expires_in": expires_in})


async def test_token_endpoint_rate_limit_pauses_lookups(clock):
    # Review finding: a 429 from the token endpoint paused nothing, so every lookup asked again.
    fake = TokenEndpoint(httpx.Response(429, headers={"retry-after": "30"}))
    dk, quotas = one_app(clock, fake)
    try:
        first = await dk.get_part("A")
        second = await dk.get_part("B")
    finally:
        await dk.close()
    assert "limiting requests per minute" in first["error"] and "30 s" in first["error"]
    assert second == first
    assert fake.token_requests == 1 and fake.product_requests == 0
    assert quotas.status()["used_today"] == 0


async def test_lookup_waiting_on_a_token_refresh_sends_nothing_once_a_penalty_begins(clock):
    # Review finding: a lookup queued on the token lock sent its own token request after the
    # first refresh failed, although a 403 suspension had begun meanwhile.
    dk = quotas = None

    async def slow_failing_refresh():
        for _ in range(10):
            await asyncio.sleep(0)  # the other lookup reaches the token lock
        quotas.note_response(0, 403, {})  # another lookup's product request was refused
        return httpx.Response(500)

    fake = TokenEndpoint(slow_failing_refresh, token())
    dk, quotas = one_app(clock, fake)
    try:
        first, second = await asyncio.gather(dk.get_part("A"), dk.get_part("B"), return_exceptions=True)
    finally:
        await dk.close()
    assert isinstance(first, DigiKeyError) and "HTTP 500" in str(first)
    assert "refused this server's requests (HTTP 403)" in second["error"]
    assert fake.token_requests == 1 and fake.product_requests == 0


async def test_short_lived_token_is_refreshed_once_per_lookup_not_forever(clock):
    # Review finding: a token valid for under the 100 s margin was refreshed endlessly.
    fake = TokenEndpoint(token(expires_in=60))
    dk, quotas = one_app(clock, fake)
    try:
        assert (await dk.get_part("A"))["total"] == 1
        assert (await dk.get_part("B"))["total"] == 1
    finally:
        await dk.close()
    assert fake.token_requests == 2 and fake.product_requests == 2


async def test_already_expired_token_fails_instead_of_looping(clock):
    fake = TokenEndpoint(token(expires_in=0))
    dk, quotas = one_app(clock, fake)
    try:
        with pytest.raises(DigiKeyError, match="expired token"):
            await dk.get_part("A")
    finally:
        await dk.close()
    assert fake.token_requests == 1 and fake.product_requests == 0
    assert quotas.status()["used_today"] == 0


async def test_lookups_queued_on_a_spent_apps_token_move_to_the_next_app(clock):
    # Review finding: lookups waiting on app 1's token lock each asked for an app 1 token after
    # the first token request said app 1's day was used up, instead of moving to app 2.
    calls = []

    async def handler(request):
        if "oauth2/token" in str(request.url):
            client_id = parse_qs(request.content.decode())["client_id"][0]
            calls.append(client_id)
            if client_id == CREDS[0]:
                for _ in range(10):
                    await asyncio.sleep(0)  # the other lookups queue on app 1's token lock
                return httpx.Response(429, headers=DAILY_HEADERS)
            return httpx.Response(200, json={"access_token": f"token-{client_id}-1", "expires_in": 599})
        calls.append("product " + request.headers["X-DIGIKEY-Client-Id"])
        return ok()

    quotas = pool(clock)
    dk = DigiKeyClient(*CREDS[:2], quota=quotas, second_app=CREDS[2:])
    dk._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def sleep(seconds):
        await asyncio.sleep(0)

    dk._pacer = Pacer(5, clock=clock, sleep=sleep)
    try:
        results = await asyncio.gather(*(dk.get_part(f"P{i}") for i in range(3)))
    finally:
        await dk.close()
    assert all(r["total"] == 1 for r in results)
    assert calls.count(CREDS[0]) == 1 and calls.count(CREDS[2]) == 1
    assert calls.count("product " + CREDS[2]) == 3 and "product " + CREDS[0] not in calls


@pytest.mark.parametrize("slow_step", ["save", "caller log"])
def test_minute_window_counts_from_the_send(clock, monkeypatch, slow_step):
    # Review findings: the minute budget stamped a request when it was counted, so a slow quota
    # save or caller-log write before the send let one more request than the cap go out within
    # 60 s of sends. mark_sent(), right before the send, moves the stamp.
    from pcbparts_mcp.cache import CallerTally
    quotas = pool(clock, per_minute=2)
    cls, name = (DailyQuota, "_save") if slow_step == "save" else (CallerTally, "record")
    original = getattr(cls, name)
    slow = [True]

    def step(self, *args, **kwargs):
        if slow and slow.pop():
            clock.advance(0.5)  # this request leaves half a second after it was counted
        return original(self, *args, **kwargs)

    monkeypatch.setattr(cls, name, step)
    assert quotas.acquire() == (0, None)
    quotas.mark_sent()  # leaves at NOW + 0.5
    assert quotas.acquire() == (0, None)
    quotas.mark_sent()
    clock.now = NOW + 60  # 60 s after the first was counted, 59.5 s after it left
    assert quotas.acquire()[0] is None
    clock.advance(0.5)
    assert quotas.acquire() == (0, None)


async def test_client_marks_the_minute_at_the_send(client, clock, monkeypatch):
    quotas = pool(clock, per_minute=1)
    dk, fake = client(quotas, ok())
    preset_tokens(dk)
    original = DailyQuota._save

    def slow_save(self):
        clock.advance(0.5)
        original(self)

    monkeypatch.setattr(DailyQuota, "_save", slow_save)
    assert (await dk.get_part("A"))["total"] == 1
    assert list(quotas._minute._sent) == [NOW + 0.5]  # stamped at the send, after the save


async def test_slow_first_http_client_build_does_not_eat_the_gap(clock, monkeypatch):
    # Review finding: the pacer was marked before the HTTP client was lazily built, so a slow
    # first build (loading TLS certificates, say) shortened the gap to the next request. Test clock.
    sent_at = []

    async def handler(request):
        sent_at.append(clock())
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "token-x", "expires_in": 599})
        return ok()

    real_client = httpx.AsyncClient

    def slow_client(*args, **kwargs):
        clock.advance(0.2)
        return real_client(transport=httpx.MockTransport(handler))

    dk = DigiKeyClient(*CREDS[:2], quota=pool(clock), second_app=CREDS[2:])
    dk._pacer = paced_by(clock)
    monkeypatch.setattr(httpx, "AsyncClient", slow_client)
    try:
        results = await asyncio.gather(*(dk.get_part(f"P{i}") for i in range(3)))
    finally:
        await dk.close()
    assert all(r["total"] == 1 for r in results) and len(sent_at) == 4  # a token, then 3 products
    assert min(gaps_of(sent_at)) >= 0.1, gaps_of(sent_at)
