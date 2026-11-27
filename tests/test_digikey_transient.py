"""DigiKey API replies that aren't a usable answer: redirects, server errors, unreadable bodies and
dropped connections. A lookup's request goes out once more, then the lookup fails with a clear
error; with the retry guard, Retry-After, the second app, token renewal, stop() and close(). No
network: an httpx MockTransport, a fake clock and fake sleeps."""

import asyncio
import logging
import time

import httpx
import pytest

from pcbparts_mcp import server, stats
from pcbparts_mcp.cache import AddressDailyQuota, DailyQuota, Pacer, QuotaPool
from pcbparts_mcp.digikey import MAX_SEARCH_SENDS, RETRY_WAIT_SECONDS, DigiKeyClient, DigiKeyError
from test_digikey_two_apps import DAILY_HEADERS, Clock, ok

CALLER = "203.0.113.7"


class FakeAPI:
    """Token requests answer with a token unless token= says otherwise; keyword searches pop replies
    (an exception is raised as a connection failure would be)."""

    def __init__(self, *replies, token=None, on_search=None):
        self.replies = list(replies)
        self.token = token
        self.on_search = on_search
        self.searches = 0
        self.tokens = 0
        self.apps = []

    def __call__(self, request):
        if "oauth2/token" in str(request.url):
            self.tokens += 1
            return self.token or httpx.Response(200, json={"access_token": "tok", "expires_in": 599})
        self.searches += 1
        self.apps.append(request.headers["X-DIGIKEY-Client-Id"])
        if self.on_search:
            self.on_search(self.searches)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


@pytest.fixture
async def make():
    made = []

    def create(*replies, token=None, quota=None, on_wait=None, clock=None, second_app=False, on_search=None):
        clock = clock or Clock()
        waits = []

        async def sleep(seconds):  # the retry's wait: recorded, never real time
            waits.append(seconds)
            clock.advance(seconds)
            if on_wait:
                on_wait()
            await asyncio.sleep(0)

        async def pace(seconds):
            clock.advance(seconds)
            await asyncio.sleep(0)

        fake = FakeAPI(*replies, token=token, on_search=on_search)
        dk = DigiKeyClient("id", "secret", quota=quota, sleep=sleep, clock=clock,
                           second_app=("id2", "secret2") if second_app else None)
        dk._http = httpx.AsyncClient(transport=httpx.MockTransport(fake))
        dk._pacer = Pacer(5, clock=clock, sleep=pace)
        made.append(dk)
        return dk, fake, waits

    yield create
    for dk in made:
        await dk.close()


def digikey_counts():
    day = stats.usage.summary()["days"][0]
    return day["distributors"].get("digikey"), day["upstream"].get("digikey"), day["upstream_status"].get("digikey")


@pytest.mark.parametrize("first", [httpx.Response(302), httpx.Response(307, text="moved"), httpx.Response(503),
                                   httpx.Response(200, text="<html>not json</html>"), httpx.Response(200, json=[1]),
                                   httpx.ConnectError("private detail")],
                         ids=["302", "307", "503", "unreadable", "not-object", "connection"])
async def test_one_transient_failure_is_retried_and_answered(make, first, caplog):
    dk, fake, waits = make(first, ok())
    with caplog.at_level(logging.WARNING, logger="pcbparts_mcp.digikey"):
        answer = await dk.get_part("AO3400A")
    assert answer["total"] == 1 and answer["results"][0]["mfr_part_number"] == "AO3400A"
    assert (fake.searches, fake.tokens, waits) == (2, 1, [RETRY_WAIT_SECONDS])
    distributors, upstream, status = digikey_counts()
    assert distributors == {"sent": 2, "cached": 0, "rate_limited": 0, "ext_sent": 0, "retries": 1}
    assert upstream["sent"] == 3  # the token request and both searches: the retry is a real request
    assert sum(status.values()) == 3
    logged = " ".join(r.getMessage() for r in caplog.records)
    assert "sending it again in 3 s" in logged
    assert "not json" not in logged and "moved" not in logged and "private detail" not in logged


@pytest.mark.parametrize("reply,message", [
    (lambda: httpx.Response(302), "DigiKey API returned HTTP 302"),
    (lambda: httpx.Response(307), "DigiKey API returned HTTP 307"),
    (lambda: httpx.Response(502, text="<html>gateway</html>"), "DigiKey API returned HTTP 502"),
    (lambda: httpx.Response(200, text="<html>gateway</html>"), "DigiKey API returned an unreadable reply"),
    (lambda: httpx.Response(200), "DigiKey API returned an unreadable reply"),
    (lambda: httpx.ConnectError("private detail"), "DigiKey API request failed (network/connection error)"),
], ids=["302", "307", "502", "html", "empty", "connection"])
async def test_two_transient_failures_give_a_clear_error(make, monkeypatch, reply, message):
    dk, fake, waits = make(reply(), reply())
    with pytest.raises(DigiKeyError) as raised:
        await dk.get_part("AO3400A")
    assert str(raised.value) == message
    assert "gateway" not in str(raised.value) and "private" not in str(raised.value)
    assert (fake.searches, waits) == (2, [RETRY_WAIT_SECONDS])
    assert dk._store.get_answer("digikey", "AO3400A") is None  # a failure isn't kept as an answer
    # what the tool replies (counted as failed, digikey_failed) instead of the generic failure
    dk2, _, _ = make(reply(), reply())
    monkeypatch.setattr(server, "_digikey_client", dk2)
    assert await server.digikey_get_part("AO3400A") == {"error": f"DigiKey part lookup failed: {message}"}


async def test_other_4xx_answers_are_not_retried(make):
    dk, fake, waits = make(httpx.Response(400, text="bad"), ok())
    with pytest.raises(DigiKeyError, match=r"^DigiKey API returned HTTP 400$"):
        await dk.get_part("AO3400A")
    assert (fake.searches, waits) == (1, [])


@pytest.mark.parametrize("token,message", [
    (httpx.Response(302), "DigiKey token request failed (HTTP 302)"),
    (httpx.Response(503, text="<html>down</html>"), "DigiKey token request failed (HTTP 503)"),
    (httpx.Response(200, text="<html>down</html>"), "DigiKey token request returned an unreadable reply"),
    (httpx.Response(200, json={"expires_in": 599}), "DigiKey token request returned an unreadable reply"),
], ids=["302", "503", "html", "no-token"])
async def test_token_request_failures_are_clear(make, token, message):
    dk, fake, waits = make(ok(), token=token)
    with pytest.raises(DigiKeyError) as raised:
        await dk.get_part("AO3400A")
    assert str(raised.value) == message
    assert (fake.tokens, fake.searches, waits) == (1, 0, [])  # nothing sent without a token


async def test_token_with_odd_expiry_still_works(make):
    dk, fake, _ = make(ok(), token=httpx.Response(200, json={"access_token": "tok", "expires_in": "soon"}))
    assert (await dk.get_part("AO3400A"))["total"] == 1


async def test_the_retry_counts_on_the_day_but_not_on_the_callers_address(make):
    clock = Clock()
    day = AddressDailyQuota(1, key=lambda ip: ip, clock=clock)
    pool = QuotaPool([DailyQuota("DigiKey", 1000, clock=clock)], per_minute=100, address_daily=day)
    dk, fake, waits = make(httpx.Response(302), ok(), quota=pool)
    answer = await dk.get_part("AO3400A", caller=CALLER)
    assert answer["total"] == 1  # the address's one lookup a day was spent on the first attempt only
    assert fake.searches == 2 and waits == [RETRY_WAIT_SECONDS]
    assert day._counts == {CALLER: 1}
    assert pool.quotas[0].status()["used_today"] == 2  # but both requests count on the API's day
    held = (stats.usage.summary()["days"][0]["distributor_limits"].get("digikey") or {}).get("held_back", {})
    assert not any(held.values())


async def test_no_retry_once_the_pool_is_paused(make):
    clock = Clock()
    pool = QuotaPool([DailyQuota("DigiKey", 1000, clock=clock)], per_minute=100)
    # another lookup's refusal pauses every app while this one waits to retry
    dk, fake, waits = make(httpx.Response(503), ok(), quota=pool,
                           on_wait=lambda: pool.share_penalty(pool.quotas[0].now() + 600, "refused"))
    answer = await dk.get_part("AO3400A")
    assert fake.searches == 1 and waits == [RETRY_WAIT_SECONDS]
    assert answer["error"].startswith("DigiKey refused this server's requests (HTTP 403). Try again in 600 s.")
    distributors, _, _ = digikey_counts()
    assert distributors["sent"] == 1 and distributors["rate_limited"] == 0  # it was sent: not held back
    assert "retries" not in distributors


async def test_no_retry_once_the_day_is_spent(make):
    clock = Clock()
    pool = QuotaPool([DailyQuota("DigiKey", 1, clock=clock)], per_minute=100)
    dk, fake, waits = make(httpx.Response(302), ok(), quota=pool)
    answer = await dk.get_part("AO3400A")
    assert fake.searches == 1  # the first attempt used the day's last request
    assert answer["error"].startswith("DigiKey daily quota exceeded on this shared server.")
    assert pool.quotas[0].status()["used_today"] == 1


def pool_of(clock, apps=1, limit=1000, address=None):
    return QuotaPool([DailyQuota("DigiKey", limit, clock=clock) for _ in range(apps)], per_minute=100,
                     address_daily=address)


def valid_token(dk):
    for app in dk._apps:
        app.access_token, app.token_expires_at = "tok", time.time() + 3600


async def test_no_retry_once_the_client_closes_during_the_request(make):
    # close() while the first search is in flight: it fails, and nothing goes out again
    holder = {}
    dk, fake, waits = make(httpx.Response(302), ok(), on_search=lambda n: setattr(holder["dk"], "_closed", True))
    holder["dk"] = dk
    valid_token(dk)  # so the first search, not a token request, is what goes out
    with pytest.raises(DigiKeyError, match=r"^DigiKey API returned HTTP 302$"):
        await dk.get_part("AO3400A")
    assert (fake.tokens, fake.searches, waits) == (0, 1, [])


@pytest.mark.parametrize("ending", ["stop", "close"])
async def test_a_lookup_after_stop_or_close_is_charged_nothing(make, ending):
    clock = Clock()
    address = AddressDailyQuota(10, key=lambda ip: ip, clock=clock)
    pool = pool_of(clock, address=address)
    dk, fake, waits = make(ok(), quota=pool, clock=clock)
    valid_token(dk)
    await (dk.stop() if ending == "stop" else dk.close())
    with pytest.raises(DigiKeyError, match="network/connection error"):
        await dk.get_part("AO3400A", caller=CALLER)
    assert (fake.tokens, fake.searches) == (0, 0)
    assert pool.quotas[0].status()["used_today"] == 0 and address._counts == {}
    distributors = stats.usage.summary()["days"][0]["distributors"].get("digikey") or {}
    assert not distributors.get("sent")


async def test_stop_during_the_retry_wait_sends_nothing_more(make):
    waiting = asyncio.Event()
    dk, fake, waits = make(httpx.Response(503), ok())

    async def hang(seconds):
        waits.append(seconds)
        waiting.set()
        await asyncio.Event().wait()  # until cancelled

    dk._sleep = hang
    lookup = asyncio.create_task(dk.get_part("AO3400A"))
    await waiting.wait()
    await dk.stop()
    with pytest.raises(asyncio.CancelledError):
        await lookup
    assert fake.searches == 1 and waits == [RETRY_WAIT_SECONDS]
    distributors, _, _ = digikey_counts()
    assert distributors["sent"] == 1 and "retries" not in distributors


async def test_a_timeout_is_not_sent_again(make):
    dk, fake, waits = make(httpx.ReadTimeout("private detail"), ok())
    with pytest.raises(DigiKeyError) as raised:
        await dk.get_part("AO3400A")
    assert str(raised.value) == "DigiKey API request failed (network/connection error)"
    assert (fake.searches, waits) == (1, [])


async def test_no_retries_during_an_outage(make, caplog):
    clock = Clock()
    dk, fake, waits = make(httpx.Response(503), ok(), clock=clock)
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.digikey"):
        for _ in range(10):  # ten transient failures in the last five minutes, all of them
            dk._guard.record(transient=True)
        with pytest.raises(DigiKeyError, match=r"^DigiKey API returned HTTP 503$"):
            await dk.get_part("AO3400A")
        assert (fake.searches, waits) == (1, [])
        assert any("DigiKey retry guard entered: 10/10" in r.getMessage() for r in caplog.records)
        clock.advance(310)  # the window passes: retries again
        fake.replies = [httpx.Response(503), ok()]
        assert (await dk.get_part("AO3400A"))["total"] == 1
        assert any("DigiKey retry guard cleared" in r.getMessage() for r in caplog.records)


async def test_an_outage_that_begins_during_the_wait_stops_the_retry(make):
    holder = {}

    def outage():
        for _ in range(10):
            holder["dk"]._guard.record(transient=True)

    dk, fake, waits = make(httpx.Response(502), ok(), on_wait=outage)
    holder["dk"] = dk
    with pytest.raises(DigiKeyError, match=r"^DigiKey API returned HTTP 502$"):
        await dk.get_part("AO3400A")
    assert fake.searches == 1 and waits == [RETRY_WAIT_SECONDS]


@pytest.mark.parametrize("header,wait", [("1", 1.0), ("0", 0.0), ("3", 3.0), ("Thu, 01 Jan 2026 00:00:00 GMT", 0.0),
                                         ("soon", RETRY_WAIT_SECONDS)],
                         ids=["1s", "0s", "3s", "past-date", "unusable"])
async def test_a_short_retry_after_is_honoured(make, header, wait):
    dk, fake, waits = make(httpx.Response(503, headers={"Retry-After": header}), ok())
    assert (await dk.get_part("AO3400A"))["total"] == 1
    assert (fake.searches, waits) == (2, [wait])


@pytest.mark.parametrize("header", ["4", "120", "99999999999999999999"])
async def test_a_longer_retry_after_means_no_retry(make, header):
    dk, fake, waits = make(httpx.Response(503, headers={"Retry-After": header}), ok())
    with pytest.raises(DigiKeyError, match=r"^DigiKey API returned HTTP 503$"):
        await dk.get_part("AO3400A")
    assert (fake.searches, waits) == (1, [])


async def test_a_redirect_ignores_retry_after(make):
    dk, fake, waits = make(httpx.Response(302, headers={"Retry-After": "120"}), ok())
    assert (await dk.get_part("AO3400A"))["total"] == 1
    assert waits == [RETRY_WAIT_SECONDS]


@pytest.mark.parametrize("before", [[httpx.Response(503)], [httpx.Response(401)]], ids=["retry", "renewal"])
async def test_the_second_app_after_a_retry_or_token_renewal(make, before):
    # a transient failure (or an expired token), then app 1's daily refusal while app 2 has its day:
    # the lookup moves to app 2 instead of answering with the daily limit
    clock = Clock()
    pool = pool_of(clock, apps=2)
    dk, fake, waits = make(*before, httpx.Response(429, headers=DAILY_HEADERS), ok(), quota=pool, clock=clock,
                           second_app=True)
    answer = await dk.get_part("AO3400A")
    assert answer["total"] == 1
    assert fake.searches == MAX_SEARCH_SENDS == 3
    assert fake.apps == ["id", "id", "id2"]


@pytest.mark.parametrize("replies,searches,tokens", [
    ([httpx.Response(401), httpx.Response(503), ok()], 3, 2),
    ([httpx.Response(503), httpx.Response(401), ok()], 3, 2),
    ([httpx.Response(401), httpx.Response(401)], 2, 2),
], ids=["401-then-503", "503-then-401", "401-twice"])
async def test_token_renewal_and_a_transient_retry_together(make, replies, searches, tokens):
    dk, fake, waits = make(*replies)
    if replies[-1].status_code == 200:
        assert (await dk.get_part("AO3400A"))["total"] == 1
    else:
        with pytest.raises(DigiKeyError, match="HTTP 401"):
            await dk.get_part("AO3400A")
    assert (fake.searches, fake.tokens) == (searches, tokens)


async def test_a_lookup_never_sends_more_than_three_searches(make):
    clock = Clock()
    pool = pool_of(clock, apps=2)
    dk, fake, waits = make(httpx.Response(503), httpx.Response(401), httpx.Response(429, headers=DAILY_HEADERS), ok(),
                           quota=pool, clock=clock, second_app=True)
    answer = await dk.get_part("AO3400A")
    assert answer["error"].startswith("DigiKey daily quota exceeded")
    assert fake.searches == MAX_SEARCH_SENDS


@pytest.mark.parametrize("body", [{"Message": "An error has occurred."}, {"Products": {"x": 1}}, {}],
                         ids=["message", "products-not-a-list", "empty-object"])
async def test_a_2xx_object_that_isnt_a_search_reply_is_unreadable(make, body):
    dk, fake, waits = make(httpx.Response(200, json=body), httpx.Response(200, json=body))
    with pytest.raises(DigiKeyError, match=r"^DigiKey API returned an unreadable reply$"):
        await dk.get_part("AO3400A")
    assert fake.searches == 2
    assert dk._store.get_answer("digikey", "AO3400A") is None  # never kept as "not found"


@pytest.mark.parametrize("body", [{"Products": [], "ExactMatches": [], "ProductsCount": 0},
                                  {"Products": []}, {"ExactMatches": []}, {"Products": None, "ExactMatches": []}],
                         ids=["full", "products", "exact", "null-products"])
async def test_a_real_no_results_reply_is_still_not_found(make, body):
    dk, fake, waits = make(httpx.Response(200, json=body))
    answer = await dk.get_part("AO3400A")
    assert answer.get("not_found") or "not found" in answer.get("error", "").lower()
    assert (fake.searches, waits) == (1, [])
    assert dk._store.get_answer("digikey", "AO3400A")[0] == {"not_found": True}


async def test_a_huge_token_expiry_falls_back(make):
    dk, fake, _ = make(ok(), token=httpx.Response(200, json={"access_token": "tok", "expires_in": 10**400}))
    assert (await dk.get_part("AO3400A"))["total"] == 1
