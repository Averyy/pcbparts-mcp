"""Offline regressions from the 0.10.9 Mouser review: fake time, no live services."""

import asyncio
import datetime
import inspect
import json
import logging
from types import SimpleNamespace

import httpx
import pytest

from pcbparts_mcp import server, stats
from pcbparts_mcp.cache import AddressDailyQuota, DailyQuota, MouserKeyPool, QuotaPool, QuotaStore, _utc_text
from pcbparts_mcp.mouser import MouserAPIError, MouserClient, MouserError
from test_mouser_keys import DAILY_403, MINUTE_403, KEYS, MOUSER_RESET, NOW
from test_mouser_retries import Clock, answer
from test_part_lifecycle import BROAD, CappedMouser, mouser_part

INVALID = {"Errors": [{"Code": "InvalidIdentifier", "Message": "Invalid unique identifier.",
                       "PropertyName": "API Key"}]}


@pytest.fixture
def clock():
    clock = Clock()
    clock.now = NOW
    return clock


@pytest.fixture
async def make(clock):
    clients = []

    def create(handler, *, keys=3, per_minute=25, address_limit=1000, path=None, limit=1000):
        address = AddressDailyQuota(address_limit, key=lambda caller: caller, clock=clock)
        store = QuotaStore(path) if path else None
        quotas = [DailyQuota("Mouser", limit, clock=clock, store=store, store_key="Mouser" if i == 0 else f"Mouser#{i + 1}", day_start_hour=6)
                  for i in range(keys)]
        pool = MouserKeyPool(quotas, per_minute=per_minute, address_daily=address)
        sent = []

        async def send(request):
            index = KEYS.index(request.url.params["apiKey"])
            sent.append(index)
            result = handler(request, index)
            return await result if inspect.isawaitable(result) else result

        client = MouserClient(KEYS[0], extra_keys=KEYS[1:keys], quota=pool, clock=clock, sleep=clock.sleep)
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(send))
        clients.append(client)
        return client, pool, sent

    yield create
    for client in clients:
        await client.close()


@pytest.mark.parametrize("first", ["daily", "transient", "mixed"])
async def test_retries_and_rotation_count_one_address_lookup(make, clock, first):
    responses = {
        "daily": [httpx.Response(403, json=DAILY_403), answer()],
        "transient": [httpx.Response(503), httpx.Response(502), answer()],
        "mixed": [httpx.Response(403, json=DAILY_403), httpx.Response(503), answer()],
    }[first]
    expected = len(responses)
    client, pool, sent = make(lambda request, index: responses.pop(0), address_limit=1)
    assert (await client.get_part("LM358P", caller="203.0.113.1"))["total"] == 0
    assert pool.address_daily._counts == {"203.0.113.1": 1}
    assert len(sent) == expected
    assert sum(q._count for q in pool.quotas) == expected
    assert "This address has used its 1" in (await client.get_part("NE555P", caller="203.0.113.1"))["error"]
    assert len(sent) == expected


@pytest.mark.parametrize("address_limit", [1, 1000])
async def test_capped_follow_up_counts_one_address_lookup(make, clock, monkeypatch, address_limit):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    fake = CappedMouser(*BROAD, mouser_part("NE555P"))
    client, pool, sent = make(lambda request, index: fake(request), keys=1, address_limit=address_limit)
    reply = await client.get_part("LM358|NE555P", caller="203.0.113.9")
    assert fake.sent == ["LM358|NE555P", "NE555P"] and sent == [0, 0]
    assert reply["total"] == 51 and reply["results"][-1]["mfr_part_number"] == "NE555P"
    assert "not_found" not in reply and "not_checked" not in reply
    assert pool.address_daily._counts == {"203.0.113.9": 1}
    assert pool.quotas[0]._count == 2 and pool._minute.used == 2
    counts = stats.usage.summary()["days"][0]
    assert counts["distributors"]["mouser"]["sent"] == 2
    assert counts["upstream_status"]["mouser"] == {"2xx": 2}
    assert (await client.get_part("NE555P", caller="203.0.113.9"))["total"] == 1
    assert sent == [0, 0] and pool.address_daily._counts == {"203.0.113.9": 1}


@pytest.mark.parametrize("outcome", ["address", "minute", "daily", "503", "timeout", "api"])
@pytest.mark.parametrize("tool", ["parts", "lifecycle"])
async def test_capped_follow_up_preserves_refusal_or_failure(make, clock, monkeypatch, outcome, tool):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    fake = CappedMouser(*BROAD, mouser_part("NE555P"))

    def handler(request, index):
        if len(sent) == 1:
            return fake(request)
        assert json.loads(request.content)["SearchByPartRequest"]["mouserPartNumber"] == "NE555P"
        if outcome == "timeout":
            raise httpx.ReadTimeout("offline")
        return {"daily": httpx.Response(403, json=DAILY_403), "503": httpx.Response(503),
                "api": httpx.Response(200, json={"Errors": [{"Code": "InvalidPartNumber", "Message": "bad number"}]})}[outcome]

    client, pool, sent = make(handler, keys=1, per_minute=1 if outcome == "minute" else 25, address_limit=1)
    if outcome == "address":
        # Exercise the reply handling even if a follow-up returns an address error. The real
        # pool bypasses that cap for follow-ups, as the successful tests above establish.
        request = client._request

        async def refuse_follow_up(numbers, caller, *, budget=None, check_address=True):
            if not check_address:
                assert numbers == ["NE555P"]
                return None, pool.address_error(caller)
            return await request(numbers, caller, budget=budget)

        monkeypatch.setattr(client, "_request", refuse_follow_up)
    limited = outcome in ("address", "minute", "daily")
    if tool == "parts":
        reply = await client.get_part("LM358|NE555P", caller="203.0.113.9")
        assert reply["total"] == 50
        assert "not_found" not in reply and "error" not in reply
        if limited:
            assert reply["not_checked"] == ["NE555P"] and reply["retry_after"] == client.retry_after("203.0.113.9")
            assert "lookup_failed" not in reply
        else:
            assert reply["lookup_failed"] == ["NE555P"]
            assert "not_checked" not in reply and "retry_after" not in reply
    else:
        monkeypatch.setattr(server, "_mouser_client", client)
        monkeypatch.setattr(server, "_digikey_client", None)
        monkeypatch.setattr(server, "_distributor_store", client._store)
        monkeypatch.setattr(server, "_caller_ip", lambda: "203.0.113.9")
        reply = await server.part_lifecycle(parts=["LM358", "NE555P"])
        problem = {"retry_after": client.retry_after("203.0.113.9")} if limited else {"lookup_failed": True}
        assert reply["results"][1] == {"input": "NE555P", "mpn": "NE555P", "status": "unknown", **problem}
    assert client._store.get_answer("mouser", "NE555P") is None
    assert client._store.readings("NE555P") == []
    expected = 1 if outcome in ("address", "minute") else 4 if outcome == "503" else 2
    assert sent == [0] * expected
    assert pool.address_daily._counts == {"203.0.113.9": 1}
    assert pool.quotas[0]._count == expected and pool._minute.used == expected
    assert stats.usage.summary()["days"][0]["distributors"]["mouser"]["sent"] == expected
    assert clock.waits == ([3, 10] if outcome == "503" else [])


@pytest.mark.parametrize("outcome", ["minute", "503"])
async def test_capped_follow_up_keeps_loose_matches_from_first_reply(make, clock, outcome):
    # NE555 has loose matches but not itself in the capped reply: as in 0.10.8, it keeps them
    # when its follow-up is held back or fails, and lands in no list.
    first = {"Errors": [], "SearchResults": {"NumberOfResult": 300, "Parts": [
        *(mouser_part(f"LM358{i:02}X") for i in range(48)), mouser_part("NE555DR"), mouser_part("NE555PWR")]}}

    def handler(request, index):
        return httpx.Response(200, json=first) if len(sent) == 1 else httpx.Response(503)

    client, pool, sent = make(handler, keys=1, per_minute=1 if outcome == "minute" else 25)
    reply = await client.get_part("LM358|NE555")
    assert reply["total"] == 50
    assert {"NE555DR", "NE555PWR"} <= {r["mfr_part_number"] for r in reply["results"]}
    assert {"not_checked", "retry_after", "lookup_failed", "not_found"}.isdisjoint(reply)
    assert len(sent) == (1 if outcome == "minute" else 4)


@pytest.mark.parametrize("scenario", ["recapped", "unmatched", "empty"])
async def test_capped_answers_without_a_problem_remain_not_found(make, scenario):
    if scenario == "recapped":
        fake = CappedMouser(*BROAD, *(mouser_part(f"LM324{i:02}X") for i in range(60)))
        numbers, missing, total, sends = ["LM358", "LM324", "TPS54331DR"], ["TPS54331DR"], 100, 2
    elif scenario == "unmatched":
        def fake(request):
            return httpx.Response(200, json={"SearchResults": {
                "NumberOfResult": 120, "Parts": [mouser_part(f"OTHER{i:02}") for i in range(50)]}})
        numbers, missing, total, sends = ["ABC123", "DEF456"], ["ABC123", "DEF456"], 50, 1
    else:
        fake = CappedMouser(total=3)
        numbers, missing, total, sends = ["XYZ789"], ["XYZ789"], 0, 1
    client, pool, sent = make(lambda request, index: fake(request), keys=1)
    reply = await client.get_part("|".join(numbers))
    assert reply["not_found"] == missing and reply["total"] == total
    assert {"not_checked", "retry_after", "lookup_failed", "error"}.isdisjoint(reply)
    assert len(sent) == sends and pool.retry_after() is None
    for number in missing:
        assert client._store.get_answer("mouser", number) is None
        assert client._store.readings(number) == []


@pytest.mark.parametrize("tool", ["parts", "lifecycle"])
async def test_one_by_one_requests_share_the_lookup_wait_budget(make, clock, monkeypatch, tool):
    tries = {}

    def handler(request, index):
        number = json.loads(request.content)["SearchByPartRequest"]["mouserPartNumber"]
        if "|" in number:
            return httpx.Response(200, json={"Errors": [{"Code": "InvalidPartNumber", "Message": "bad batch"}]})
        tries[number] = tries.get(number, 0) + 1
        return httpx.Response(503) if tries[number] < 3 else answer()

    client, pool, sent = make(handler, keys=1)
    numbers = [f"PART{i}AB" for i in range(10)]
    if tool == "parts":
        reply = await client.get_part("|".join(numbers))
        assert reply["not_found"] == numbers[:2] and reply["lookup_failed"] == numbers[2:]
        assert "not_checked" not in reply and "retry_after" not in reply
    else:
        monkeypatch.setattr(server, "_mouser_client", client)
        monkeypatch.setattr(server, "_digikey_client", None)
        monkeypatch.setattr(server, "_distributor_store", client._store)
        reply = await server.part_lifecycle(parts=numbers)
        assert all(row["not_found"] for row in reply["results"][:2])
        assert reply["results"][2:] == [{"input": n, "mpn": n, "status": "unknown", "lookup_failed": True}
                                        for n in numbers[2:]]
    assert clock.waits == [3, 10, 3, 10, 3] and sum(clock.waits) <= 30
    assert len(sent) == 10 and list(tries.values()) == [3, 3, 2, 1]


@pytest.mark.parametrize("outcome", ["followup", "fallback", "minute", "check"])
async def test_first_request_and_continuations_share_wait_budget(make, clock, outcome):
    fake = CappedMouser(*BROAD, mouser_part("NE555P"))

    def handler(request, index):
        if len(sent) == 1:
            return httpx.Response(503, headers={"Retry-After": "27"})
        if len(sent) == 2:
            if outcome == "fallback":
                return httpx.Response(200, json={"Errors": [{"Code": "InvalidPartNumber", "Message": "bad batch"}]})
            response = fake(request)
            if outcome == "check":
                pool.quotas[0].pause_daily_unknown_reset(clock() + 4)
            return response
        if outcome == "minute":
            return httpx.Response(503)
        # Once 30 seconds have been spent, even an immediate transient retry must stop.
        return httpx.Response(503, headers={"Retry-After": "0"} if len(sent) >= 4 else {})

    client, pool, sent = make(handler, keys=1, per_minute=4 if outcome == "minute" else 25)
    if outcome == "minute":
        # This slot frees 4 seconds after the follow-up's first transient failure; only 3 remain.
        clock.now -= 29
        assert pool.acquire() == (0, None)
        clock.now += 29
    if outcome == "fallback":
        with pytest.raises(MouserError, match="HTTP 503"):
            await client.get_part("LM358|NE555P")
    else:
        reply = await client.get_part("LM358|NE555P")
        if outcome in ("minute", "check"):
            assert reply["not_checked"] == ["NE555P"] and "not_found" not in reply
        else:
            assert reply["lookup_failed"] == ["NE555P"] and "not_checked" not in reply
    assert clock.waits == ([27] if outcome == "check" else [27, 3])
    assert len(sent) == {"followup": 4, "fallback": 5, "minute": 3, "check": 2}[outcome]


async def test_rejected_batch_still_counts_each_single_address_lookup(make):
    responses = [httpx.Response(200, json={"Errors": [{"Code": "InvalidPartNumber", "Message": "bad batch"}]}),
                 answer()]
    client, pool, sent = make(lambda request, index: responses.pop(0), keys=1, address_limit=2)
    reply = await client.get_part("LM358P|NE555P", caller="203.0.113.9")
    assert reply["not_found"] == ["LM358P"] and reply["not_checked"] == ["NE555P"]
    assert sent == [0, 0] and pool.address_daily._counts == {"203.0.113.9": 2}


@pytest.mark.parametrize("occupied_at,expected_waits,success", [
    (-40, [3, 17], True), (-30, [3, 27], True), (-29, [3], False),
], ids=["fits", "exact", "over"])
async def test_transient_retry_waits_for_minute_slot(make, clock, occupied_at, expected_waits, success):
    responses = [httpx.Response(503), answer()]
    client, pool, sent = make(lambda request, index: responses.pop(0), keys=1, per_minute=2, address_limit=1)
    start = clock.now
    clock.now += occupied_at
    assert pool.acquire() == (0, None)
    clock.now = start
    reply = await client.get_part("LM358P", caller="203.0.113.1")
    assert ("error" not in reply) is success
    assert clock.waits == expected_waits
    assert pool.address_daily._counts == {"203.0.113.1": 1}
    assert len(sent) == (2 if success else 1)
    counts = stats.usage.summary()["days"][0]["distributors"]["mouser"]
    assert counts["rate_limited"] == (0 if success else 1)


async def test_five_concurrent_failures_all_retry(make, clock, caplog):
    seen = {}
    sleeping, release = asyncio.Event(), asyncio.Event()
    sleepers = 0

    def handler(request, index):
        seen[request.content] = seen.get(request.content, 0) + 1
        return httpx.Response(503) if seen[request.content] == 1 else answer()

    async def sleep(seconds):
        nonlocal sleepers
        sleepers += 1
        if sleepers == 4:
            sleeping.set()
        await release.wait()

    client, pool, sent = make(handler)
    client._sleep = sleep
    calls = [asyncio.create_task(client.get_part(f"PART{i}A")) for i in range(5)]
    try:
        await sleeping.wait()
    finally:
        release.set()
    replies = await asyncio.gather(*calls, return_exceptions=True)
    assert all(isinstance(reply, dict) and reply.get("total") == 0 for reply in replies)
    assert sorted(seen.values()) == [2] * 5
    assert "retry guard entered" not in caplog.text


async def test_mixed_failures_keep_retries_enabled(make, clock, caplog):
    seen = {}

    def handler(request, index):
        seen[request.content] = seen.get(request.content, 0) + 1
        return httpx.Response(503) if seen[request.content] == 1 else answer()

    client, pool, sent = make(handler, per_minute=100)
    for index in range(20):
        assert (await client.get_part(f"PART{index}A"))["total"] == 0
    assert len(sent) == 40 and clock.waits == [3] * 20
    assert "retry guard entered" not in caplog.text


async def test_guard_uses_window_ratio_and_expires(make, clock, caplog):
    responses = [httpx.Response(503, headers={"Retry-After": "31"}) for _ in range(10)]
    responses += [answer(), answer(), httpx.Response(503), answer()]
    client, pool, sent = make(lambda request, index: responses.pop(0), per_minute=100)
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.mouser"):
        for index in range(10):
            with pytest.raises(MouserError, match="HTTP 503"):
                await client.get_part(f"PART{index}A")
        entered = [r for r in caplog.records if "retry guard entered" in r.message]
        assert len(entered) == 1 and "10/10" in entered[0].message
        await client.get_part("RECOVER1")  # 10/11 still exceeds 90%
        assert not any("retry guard cleared" in r.message for r in caplog.records)
        await client.get_part("RECOVER2")  # 10/12 no longer does
        cleared = [r for r in caplog.records if "retry guard cleared" in r.message]
        assert len(cleared) == 1 and "10/12" in cleared[0].message
        assert (await client.get_part("LM358P"))["total"] == 0
        assert clock.waits == [3]


@pytest.mark.parametrize("age", [299, 310], ids=["recent", "expired"])
async def test_sleeping_retry_rechecks_guard_window(make, clock, caplog, age):
    responses = [httpx.Response(503)]
    responses += [httpx.Response(503, headers={"Retry-After": "31"}) for _ in range(9)]
    responses += [answer()]
    client, pool, sent = make(lambda request, index: responses.pop(0), per_minute=100)
    sleeping, release = asyncio.Event(), asyncio.Event()

    async def sleep(seconds):
        sleeping.set()
        await release.wait()

    client._sleep = sleep
    waiting = asyncio.create_task(client.get_part("LM358P"))
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.mouser"):
        try:
            await sleeping.wait()
            for index in range(9):
                with pytest.raises(MouserError, match="HTTP 503"):
                    await client.get_part(f"PART{index}A")
            clock.now += age
        finally:
            release.set()
        if age < 300:
            with pytest.raises(MouserError, match="HTTP 503"):
                await waiting
            assert len(sent) == 10
        else:
            assert (await waiting)["total"] == 0
            assert len(sent) == 11
            assert any("retry guard cleared" in r.message and "0/0" in r.message for r in caplog.records)


def test_day_start_is_explicit_not_chosen_by_name(clock):
    clock.now = MOUSER_RESET - 1
    for name in ("Mouser", "Other"):
        quota = DailyQuota(name, 1000, clock=clock, day_start_hour=6)
        assert quota.next_reset() == MOUSER_RESET
        assert quota._date == datetime.date(2026, 11, 18)
    assert DailyQuota("Mouser", 1000, clock=clock).next_reset() == MOUSER_RESET - 6 * 3600 + 86400


async def test_absurdly_nested_reply_is_counted_and_retried(make, clock, monkeypatch):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    nested = b"[" * 100_000 + b"]" * 100_000
    client, pool, sent = make(lambda request, index: httpx.Response(200, content=nested), keys=1)
    with pytest.raises(MouserError, match="unreadable"):
        await client._request(["LM358P"], None)
    assert len(sent) == 3
    assert stats.usage.summary()["days"][0]["upstream_status"]["mouser"] == {"2xx": 3}


@pytest.mark.parametrize("offset,success", [(-40, True), (-30, True), (-29, False)])
@pytest.mark.parametrize("first", ["daily", "invalid", "mixed"])
async def test_rotation_waits_within_shared_retry_budget(make, clock, offset, success, first):
    responses = ([httpx.Response(503)] if first == "mixed" else []) + [
        httpx.Response(403, json=INVALID if first == "invalid" else DAILY_403), answer()]
    client, pool, sent = make(lambda request, index: responses.pop(0), keys=2,
                              per_minute=3 if first == "mixed" else 2, address_limit=1)
    started = clock()
    clock.now += offset
    pool.acquire()
    clock.now = started
    reply = await client.get_part("LM358P", caller="203.0.113.1")
    assert ("error" not in reply) is success
    waits = [3] if first == "mixed" else []
    if success:
        waits.append(60 + offset - sum(waits))
    assert clock.waits == waits
    assert len(sent) == (2 if first == "mixed" else 1) + int(success)
    assert pool.address_daily._counts == {"203.0.113.1": 1}


@pytest.mark.parametrize("status", [200, 403, 429, 503])
@pytest.mark.parametrize("body,label", [(DAILY_403, "daily"), (MINUTE_403, "minute")], ids=["day", "minute"])
async def test_mouser_limits_always_count_as_429(make, clock, monkeypatch, status, body, label):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    client, pool, sent = make(lambda request, index: httpx.Response(status, json=body), keys=1)
    assert "error" in await client.get_part("LM358P")
    day = stats.usage.summary()["days"][0]
    assert day["upstream_status"]["mouser"] == {"429": 1}
    assert day["distributor_limits"]["mouser"]["refusals"][label] == 1


@pytest.mark.parametrize("status", [401, 403])
async def test_unexplained_check_counts_refused_and_upstream_4xx(make, clock, monkeypatch, status):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    responses = [httpx.Response(403, json=DAILY_403), httpx.Response(status, text="Forbidden")]
    client, pool, sent = make(lambda request, index: responses.pop(0), keys=1)
    assert "daily quota exceeded" in (await client.get_part("LM358P"))["error"]
    clock.now += 3600
    assert "daily quota exceeded" in (await client.get_part("NE555P"))["error"]
    day = stats.usage.summary()["days"][0]
    assert day["upstream_status"]["mouser"] == {"429": 1, "4xx": 1}
    assert day["distributor_limits"]["mouser"]["refusals"] == {"daily": 1, "minute": 0, "refused": 1}
    assert pool.retry_after() == 3600 and sent == [0, 0]


async def test_mouser_limit_counting_failure_does_not_escape(make, monkeypatch):
    def broken(*args):
        raise RuntimeError("offline counting failure")

    monkeypatch.setattr(stats.usage, "record_upstream_status", broken)
    client, pool, sent = make(lambda request, index: httpx.Response(200, json=DAILY_403), keys=1)
    assert "daily quota exceeded" in (await client.get_part("LM358P"))["error"]


@pytest.mark.parametrize("hour", [0, 6, 9, 23])
async def test_stats_reports_configured_distributor_resets(clock, monkeypatch, stats_headers, hour):
    clock.now = MOUSER_RESET
    mouser = MouserKeyPool([DailyQuota("Mouser", 1000, clock=clock, day_start_hour=hour)])
    digikey = QuotaPool([DailyQuota("DigiKey", 1000, clock=clock)])
    monkeypatch.setattr(server, "_distributor_quotas", {"mouser": mouser, "digikey": digikey})
    response = await server.usage_stats(SimpleNamespace(headers=stats_headers, query_params={}))
    quotas = json.loads(response.body)["distributor_quota"]
    midnight = MOUSER_RESET - 6 * 3600
    assert quotas["mouser"]["resets_at"] == _utc_text(midnight + hour * 3600 + (86400 if hour <= 6 else 0))
    assert quotas["digikey"]["resets_at"] == _utc_text(midnight + 86400)


@pytest.mark.parametrize("count,sent_offset,reply_offset,pause", [
    (499, -7200, -7200, -3600), (499, -120, -120, 60), (500, -120, -120, 60), (1000, -120, -120, 60),
    (500, -2, 1, 60), (500, -2, 60, 3660), (500, -2, 3601, 7201),
    (499, -2, 1, 60), (499, -2, 60, 3660), (499, 30, 3601, 7201), (500, 30, 3601, 86460),
    (499, 20, 20, 60),
], ids=["lowfar", "low", "half", "spent", "cross", "due", "past", "lowcross", "lowdue", "lowlate", "halflate", "margin"])
async def test_daily_refusal_uses_send_count_and_day(make, clock, caplog, count, sent_offset, reply_offset, pause):
    clock.now = MOUSER_RESET + sent_offset

    def handler(request, index):
        if index == 0:
            clock.now = MOUSER_RESET + reply_offset
            pool.quotas[0].status()  # a concurrent health read may reset the day's count
            pool.quotas[0]._count += 50  # other sends must not affect this request's snapshot
            return httpx.Response(403, json=DAILY_403)
        return answer()

    client, pool, sent = make(handler)
    pool.quotas[0]._count = count - 1
    assert (await client.get_part("LM358P"))["total"] == 0
    assert sent == [0, 1]
    quota = pool.quotas[0]
    assert quota._paused_until == MOUSER_RESET + pause
    assert quota.daily_refusals() == [{"at": MOUSER_RESET + sent_offset, "count": count,
                                     "last_refused_at": MOUSER_RESET + reply_offset,
                                     "retries": 0, "resumed_at": None}]
    messages = [r.message for r in caplog.records if "daily refusal at" in r.message]
    assert len(messages) == 1
    assert messages[0].endswith(f"our count {count}/1000; next try at {_utc_text(MOUSER_RESET + pause)}")


async def test_low_count_refusal_at_0537_retries_by_0601(make, clock):
    clock.now = MOUSER_RESET - 23 * 60
    client, pool, sent = make(lambda request, index: answer() if clock() >= MOUSER_RESET
                              else httpx.Response(403, json=DAILY_403), keys=1)
    pool.quotas[0]._count = 40
    assert "tries again at 2026-11-19 06:01 UTC" in (await client.get_part("LM358P"))["error"]
    assert pool.quotas[0]._paused_until == MOUSER_RESET + 60
    clock.now = MOUSER_RESET + 59
    assert (await client.get_part("NE555P"))["total"] == 0 and sent == [0, 0]
    assert clock.waits == [1] and clock.now == MOUSER_RESET + 60
    for minute in (1, 2, 10, 30):
        clock.now = MOUSER_RESET + minute * 60
        assert (await client.get_part(f"NE555P{minute}"))["total"] == 0
    assert sent == [0] * 6 and pool.retry_after() is None


@pytest.mark.parametrize("offset", [35, 45, 55])
@pytest.mark.parametrize("accepted", [True, False], ids=["accepted", "refused"])
async def test_lookups_near_next_try_wait_for_check(make, clock, monkeypatch, offset, accepted):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    clock.now = MOUSER_RESET - 3600
    release = asyncio.Event()
    requests = 0

    async def handler(request, index):
        nonlocal requests
        requests += 1
        if requests == 1:
            return httpx.Response(403, json=DAILY_403)
        if requests == 2:
            assert clock() >= MOUSER_RESET + 60
            assert pool.checking()
            await release.wait()
        return answer() if accepted else httpx.Response(403, json=DAILY_403)

    async def sleep(seconds):
        if pool.checking():
            release.set()
        await clock.sleep(seconds)
        await asyncio.sleep(0)

    client, pool, sent = make(handler, keys=1, address_limit=1)
    client._sleep = sleep
    pool.quotas[0]._count = 900
    assert "error" in await client.get_part("LM358P")
    clock.now = MOUSER_RESET + offset
    pool.address_daily.record("capped")
    assert "This address has used its 1" in (await client.get_part("NE555P", caller="capped"))["error"]
    assert clock.waits == [] and sent == [0]
    try:
        replies = await asyncio.gather(*(client.get_part(f"PART{i}AB", caller=f"caller{i}") for i in range(3)))
    finally:
        release.set()
    assert all(r.get("total") == 0 if accepted else "daily quota exceeded" in r["error"] for r in replies)
    assert clock.waits and set(clock.waits) == {1}
    assert sent == [0] * (4 if accepted else 2)
    assert len(pool.address_daily._counts) == (4 if accepted else 2)
    assert set(pool.address_daily._counts.values()) == {1}
    assert not pool.checking() and pool._checks == {}


@pytest.mark.parametrize("due_in", [30, 31], ids=["exact", "over"])
async def test_next_try_must_fit_remaining_wait_budget(make, clock, due_in):
    client, pool, sent = make(lambda request, index: answer(), keys=1)
    pool.quotas[0].pause_daily_unknown_reset(clock() + due_in)
    reply = await client.get_part("LM358P")
    assert (reply.get("total") == 0) is (due_in == 30)
    assert clock.waits == ([1] * 30 if due_in == 30 else [])
    assert sent == ([0] if due_in == 30 else [])


@pytest.mark.parametrize("check", [False, True], ids=["send", "check"])
@pytest.mark.parametrize("accepted,prior_wait", [(True, 0), (False, 0), (True, 20)],
                         ids=["accepted", "refused", "over"])
async def test_own_daily_refusal_waits_for_nearby_next_try(make, clock, check, accepted, prior_wait):
    clock.now = MOUSER_RESET + 45 - prior_wait
    responses = ([httpx.Response(503, headers={"Retry-After": str(prior_wait)})] if prior_wait else [])
    responses += [httpx.Response(403, json=DAILY_403),
                  answer() if accepted else httpx.Response(403, json=DAILY_403)]
    client, pool, sent = make(lambda request, index: responses.pop(0), keys=1, address_limit=1)
    if check:
        pool.quotas[0].pause_daily_unknown_reset(clock())
    reply = await client.get_part("LM358P", caller="203.0.113.9")
    if accepted and not prior_wait:
        assert reply["total"] == 0 and "error" not in reply
        assert pool.retry_after() is None
    else:
        assert "daily quota exceeded" in reply["error"]
    assert clock.waits == ([prior_wait] if prior_wait else [1] * 15)
    assert sent == [0, 0] and pool.address_daily._counts == {"203.0.113.9": 1}
    assert not pool.checking()


async def test_near_due_check_and_transient_retry_share_wait_budget(make, clock):
    responses = [httpx.Response(503), httpx.Response(503), answer()]
    client, pool, sent = make(lambda request, index: responses.pop(0), keys=1)
    pool.quotas[0].pause_daily_unknown_reset(clock() + 27)
    with pytest.raises(MouserError, match="HTTP 503"):
        await client.get_part("LM358P")
    assert clock.waits == [1] * 27 + [3] and sent == [0, 0]
    assert not pool.checking() and pool._checks == {}


async def test_current_key_stays_until_refused_even_when_earlier_key_is_due(make, clock, tmp_path):
    responses = [httpx.Response(403, json=DAILY_403), answer(), answer(),
                 httpx.Response(403, json=DAILY_403), answer()]
    path = tmp_path / "quota.json"
    client, pool, sent = make(lambda request, index: responses.pop(0), keys=2, path=path)
    assert "error" not in await client.get_part("LM358P")
    clock.now += 3600
    assert "error" not in await client.get_part("NE555P")
    assert sent == [0, 1, 1]
    assert "error" not in await client.get_part("LM324P")
    assert sent == [0, 1, 1, 1, 0]
    assert pool.quotas[0].daily_refusals()[0]["resumed_at"] == clock()
    # The accepted check is now current, including after a restart.
    restarted, restored, used = make(lambda request, index: answer(), keys=2, path=path)
    assert "error" not in await restarted.get_part("LM2904P")
    assert used == [0] and restored.quotas[1]._paused_until == clock() + 3600


async def test_all_refused_keys_check_hourly_and_keep_next_tries_on_restart(make, clock, tmp_path):
    path = tmp_path / "quota.json"
    client, pool, sent = make(lambda request, index: httpx.Response(403, json=DAILY_403), path=path)
    assert "tries again at 2026-11-18 21:00 UTC" in (await client.get_part("LM358P"))["error"]
    assert sent == [0, 1, 2]
    clock.now += 3599
    restarted, restored, used = make(lambda request, index: httpx.Response(403, json=DAILY_403), path=path)
    assert restored.retry_after() == 1
    assert "error" in await restarted.get_part("NE555P")
    assert clock.waits == [1]
    assert used == [0, 1, 2]  # each key gets its own hourly check
    assert restored.retry_after() == 3600
    assert all(q._paused_until == clock() + 3600 for q in restored.quotas)
    assert all(q.daily_refusals()[0]["retries"] == 1 for q in restored.quotas)


@pytest.mark.parametrize("keys", [1, 3])
@pytest.mark.parametrize("accepted", [True, False], ids=["accepted", "refused"])
async def test_concurrent_lookups_hold_one_check_per_due_key(make, clock, keys, accepted):
    entered, release = asyncio.Event(), asyncio.Event()
    checking = False
    arrivals = 0

    async def handler(request, index):
        nonlocal arrivals
        if checking:
            arrivals += 1
            if arrivals == keys:
                entered.set()
            await release.wait()
            return answer() if accepted else httpx.Response(403, json=DAILY_403)
        return httpx.Response(403, json=DAILY_403)

    client, pool, sent = make(handler, keys=keys, address_limit=1)
    assert "error" in await client.get_part("LM358P")
    clock.now += 3600
    checking = True
    checks = asyncio.gather(*(client.get_part(f"PART{i}A") for i in range(keys)))
    waiting = 0

    async def sleep(seconds):
        nonlocal waiting
        waiting += 1
        if waiting == 5:
            release.set()
        await release.wait()
        await asyncio.sleep(0)
        await clock.sleep(seconds)

    client._sleep = sleep
    try:
        await entered.wait()
        assert sent == list(range(keys)) * 2
        assert pool.retry_after() == 60
        assert pool.status()["paused_until"] == _utc_text(clock() + 60)
        # An address cap still refuses immediately, even with a check in flight.
        pool.address_daily.record("capped")
        assert "This address has used its 1" in (await client.get_part("NE555P", caller="capped"))["error"]
        assert clock.waits == []
        replies = await asyncio.gather(*(client.get_part(f"LATER{i}A", caller=f"caller{i}") for i in range(5)))
        assert len(clock.waits) >= 5 and set(clock.waits) == {1}
        assert all((r.get("total") == 0) if accepted else "daily quota exceeded" in r["error"] for r in replies)
        assert len(sent) == keys * 2 + (5 if accepted else 0)
        assert pool.address_daily._counts == {"capped": 1, **({f"caller{i}": 1 for i in range(5)} if accepted else {})}
    finally:
        release.set()
        replies = await checks
    assert all((r.get("total") == 0) if accepted else "daily quota exceeded" in r["error"] for r in replies)
    assert pool.retry_after() is None if accepted else 0 < pool.retry_after() <= 3600


async def test_five_in_flight_daily_refusals_wait_for_rotation_checks(make, clock, monkeypatch):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    clock.now = MOUSER_RESET + 10 * 3600
    entered, release = asyncio.Event(), asyncio.Event()
    arrivals = 0

    async def handler(request, index):
        nonlocal arrivals
        if index == 0:
            arrivals += 1
            if arrivals == 5:
                entered.set()
            await release.wait()
            return httpx.Response(403, json=DAILY_403)
        await asyncio.sleep(0)
        return answer()

    async def sleep(seconds):
        await clock.sleep(seconds)
        await asyncio.sleep(0)  # let the in-flight HTTP checks finish during the fake wait

    client, pool, sent = make(handler, address_limit=1)
    client._sleep = sleep
    for quota in pool.quotas[1:]:
        quota._daily_refusals = [{"at": clock() - 86400, "count": 1000, "last_refused_at": clock() - 86400,
                                 "retries": 0, "resumed_at": None}]
        quota._paused_until, quota._pause_reason = clock() - 3600, "daily_unknown"
    calls = asyncio.gather(*(client.get_part(f"PART{i}AB", caller=f"caller{i}") for i in range(5)))
    try:
        await entered.wait()
        assert sent == [0] * 5
    finally:
        release.set()
        replies = await calls
    assert all(r.get("total") == 0 for r in replies)
    assert len(sent) == 10 and sent.count(0) == 5 and {1, 2} <= set(sent)
    assert clock.waits and sum(clock.waits) <= 30
    assert pool.address_daily._counts == {f"caller{i}": 1 for i in range(5)}
    counts = stats.usage.summary()["days"][0]
    assert counts["distributors"]["mouser"]["rate_limited"] == 0
    assert sum(counts["distributor_limits"]["mouser"]["held_back"].values()) == 0


async def test_transient_retry_waits_for_another_lookups_check(make, clock, monkeypatch):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    retry_sleeping, retry_release = asyncio.Event(), asyncio.Event()
    check_entered, check_release, check_finished = asyncio.Event(), asyncio.Event(), asyncio.Event()
    requests = 0

    async def handler(request, index):
        nonlocal requests
        requests += 1
        if requests == 1:
            return httpx.Response(403, json=DAILY_403)
        if requests == 2:
            return httpx.Response(503)
        if requests == 3:
            check_entered.set()
            await check_release.wait()
            check_finished.set()
        return answer()

    async def sleep(seconds):
        if seconds == 3:
            retry_sleeping.set()
            await retry_release.wait()
        else:
            check_release.set()
            await check_finished.wait()
        await clock.sleep(seconds)

    client, pool, sent = make(handler, keys=1, address_limit=1)
    client._sleep = sleep
    assert "error" in await client.get_part("LM358P")
    clock.now += 3600
    first = asyncio.create_task(client.get_part("NE555P", caller="first"))
    second = None
    try:
        await retry_sleeping.wait()
        second = asyncio.create_task(client.get_part("LM324P", caller="second"))
        await check_entered.wait()
        retry_release.set()
        assert (await first).get("total") == 0
        assert (await second).get("total") == 0
    finally:
        retry_release.set()
        check_release.set()
        await asyncio.gather(first, *([second] if second else []), return_exceptions=True)
    assert clock.waits == [3, 1] and sent == [0] * 4
    assert pool.address_daily._counts == {"first": 1, "second": 1}
    counts = stats.usage.summary()["days"][0]["distributors"]["mouser"]
    assert counts["retries"] == 1 and counts["rate_limited"] == 0


@pytest.mark.parametrize("retry", [False, True], ids=["first", "retry"])
async def test_check_wait_stops_at_shared_30_second_budget(make, clock, retry):
    entered, release = asyncio.Event(), asyncio.Event()
    requests = 0
    other = None

    async def handler(request, index):
        nonlocal requests
        requests += 1
        if requests == 1:
            return httpx.Response(403, json=DAILY_403)
        if retry and requests == 2:
            return httpx.Response(503)
        entered.set()
        await release.wait()
        return answer()

    async def sleep(seconds):
        nonlocal other
        await clock.sleep(seconds)
        if seconds == 3:
            other = asyncio.create_task(client.get_part("LM324P"))
            await entered.wait()

    client, pool, sent = make(handler, keys=1)
    client._sleep = sleep
    assert "error" in await client.get_part("LM358P")
    clock.now += 3600
    started = clock()
    try:
        if not retry:
            other = asyncio.create_task(client.get_part("LM324P"))
            await entered.wait()
        reply = await client.get_part("NE555P")
        assert "daily quota exceeded" in reply["error"]
        assert _utc_text(pool.quotas[0]._paused_until) in reply["error"]
        assert clock() == started + 30
        assert clock.waits == ([3] + [1] * 27 if retry else [1] * 30)
        assert sent == [0] * (3 if retry else 2)
    finally:
        release.set()
        if other is not None:
            assert (await other).get("total") == 0


@pytest.mark.parametrize("elapsed", [0, 35], ids=["early", "near"])
async def test_restart_keeps_hold_without_waiting_for_lost_check(make, clock, tmp_path, elapsed):
    entered, release = asyncio.Event(), asyncio.Event()

    async def handler(request, index):
        if not pool.quotas[0].daily_refusals():
            return httpx.Response(403, json=DAILY_403)
        entered.set()
        await release.wait()
        return answer()

    path = tmp_path / "quota.json"
    client, pool, sent = make(handler, keys=1, path=path)
    assert "error" in await client.get_part("LM358P")
    clock.now += 3600
    pending = asyncio.create_task(client._request(["NE555P"], None))
    try:
        await entered.wait()
        saved = json.loads(path.read_text(encoding="utf-8"))["Mouser"]
        assert saved["pause_reason"] == "checking" and saved["paused_until"] == clock() + 60
        clock.now += elapsed
        restarted, restored, used = make(lambda request, index: answer(), keys=1, path=path)
        assert not restored.checking() and restored.retry_after() == 60 - elapsed
        assert restored.status()["paused_until"] == _utc_text(saved["paused_until"])
        if elapsed == 0:
            assert "daily quota exceeded" in (await restarted.get_part("LM324P"))["error"]
            assert used == [] and clock.waits == []
            clock.now = saved["paused_until"]
        assert not restored.checking()
        assert (await restarted.get_part("LM324P"))["total"] == 0 and used == [0]
        assert sum(clock.waits) == (60 - elapsed if elapsed else 0)
        assert restored.retry_after() is None
        assert restored.quotas[0].daily_refusals()[0]["resumed_at"] == clock()
    finally:
        pending.cancel()
        await asyncio.gather(pending, return_exceptions=True)


@pytest.mark.parametrize("status,body,headers,accepted,wait", [
    (200, {"SearchResults": {"Parts": []}}, {}, True, 0),
    (200, {"Errors": [{"Code": "InvalidPartNumber", "Message": "bad number"}]}, {}, True, 0),
    (403, DAILY_403, {}, False, 3600),
    (429, None, {"x-ratelimit-remaining": "0"}, False, 3600),
    (401, None, {}, False, 3600), (403, {"Errors": [None]}, {}, False, 3600),
    (403, {"Errors": [{"Code": "BadPart", "Message": "bad number"}]}, {}, False, 3600),
    (403, MINUTE_403, {}, False, 60), (429, None, {"retry-after": "20"}, False, 20),
    (403, INVALID, {}, False, 0), (200, INVALID, {}, False, 0),
], ids=["ok", "part", "day", "bareday", "401", "403", "part403", "minute", "429", "invalid", "invalid200"])
async def test_check_outcomes(make, clock, caplog, status, body, headers, accepted, wait):
    responses = [httpx.Response(403, json=DAILY_403), httpx.Response(status, json=body, headers=headers), answer()]
    client, pool, sent = make(lambda request, index: responses.pop(0), keys=1)
    assert "error" in await client.get_part("LM358P")
    clock.now += 3600
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.mouser"):
        try:
            await client._request(["NE555P"], None)
        except (MouserError, MouserAPIError):
            pass
    assert sent == [0, 0]
    assert not pool.checking() and pool._checks == {}
    assert pool.retry_after() == (wait or None)
    episode = pool.quotas[0].daily_refusals()[0]
    assert episode["resumed_at"] == (clock() if accepted else None)
    assert episode["retries"] == int(wait == 3600)
    assert ("accepted again" in caplog.text) is accepted
    if wait:
        assert "error" in await client.get_part("LM324P") and len(sent) == 2
        clock.now += wait
    assert "error" not in await client.get_part("LM324P") and sent == [0, 0, 0]


@pytest.mark.parametrize("failure", ["503", "unreadable", "transport", "timeout", "cancel", "exhausted", "404"])
async def test_unclassified_check_releases_hold_for_retry_or_next_lookup(make, clock, tmp_path, failure):
    attempts = 0

    def handler(request, index):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(403, json=DAILY_403)
        if attempts == 2 or failure == "exhausted":
            if failure == "transport":
                raise httpx.ConnectError("offline")
            if failure == "timeout":
                raise httpx.ReadTimeout("offline")
            if failure == "cancel":
                raise asyncio.CancelledError()
            return {"unreadable": httpx.Response(200, text="bad reply"),
                    "404": httpx.Response(404)}.get(failure, httpx.Response(503))
        return answer()

    path = tmp_path / "quota.json"
    client, pool, sent = make(handler, keys=1, path=path)
    assert "error" in await client.get_part("LM358P")
    clock.now += 3600
    if failure in ("timeout", "cancel", "exhausted", "404"):
        with pytest.raises(asyncio.CancelledError if failure == "cancel" else MouserError):
            await client.get_part("NE555P")
    else:
        assert "error" not in await client.get_part("NE555P")
    assert pool.retry_after() is None
    assert not pool.checking() and pool._checks == {}
    assert len(sent) == (4 if failure == "exhausted" else 2 if failure in ("timeout", "cancel", "404") else 3)
    restarted, restored, used = make(lambda request, index: answer(), keys=1, path=path)
    assert "error" not in await restarted.get_part("LM324P") and used == [0]
    assert restored.quotas[0].daily_refusals()[0]["resumed_at"] is not None


async def test_revoked_check_does_not_block_working_keys(make, clock, tmp_path):
    checking = False

    def handler(request, index):
        if not checking:
            return httpx.Response(403, json=DAILY_403)
        return httpx.Response(403, json=INVALID) if index == 0 else answer()

    path = tmp_path / "quota.json"
    client, pool, sent = make(handler, path=path)
    assert "error" in await client.get_part("LM358P")
    clock.now += 3600
    checking = True
    assert "error" not in await client.get_part("NE555P")
    assert sent == [0, 1, 2, 0, 1]
    assert pool.quotas[0]._pause_reason == "invalid_key"
    assert pool.quotas[0]._paused_until == MOUSER_RESET
    assert pool._checks == {}
    restarted, restored, used = make(handler, path=path)
    assert "error" not in await restarted.get_part("LM324P") and used == [1]
    assert restored.quotas[0]._paused_until == MOUSER_RESET
    # Even after it is due, a revoked key cannot displace the current working key.
    clock.now = MOUSER_RESET
    assert "error" not in await restarted.get_part("LM2904P") and used == [1, 1]


@pytest.mark.parametrize("late", ["accepted", "daily"])
@pytest.mark.parametrize("delay", [0, 3601])
async def test_reply_sent_before_refusal_cannot_change_schedule(make, clock, caplog, late, delay):
    entered, release = asyncio.Event(), asyncio.Event()
    requests = 0

    async def handler(request, index):
        nonlocal requests
        requests += 1
        if requests == 1:
            entered.set()
            await release.wait()
            return answer() if late == "accepted" else httpx.Response(403, json=DAILY_403)
        return httpx.Response(403, json=DAILY_403) if index == 0 else answer()

    client, pool, sent = make(handler, keys=2)
    pending = asyncio.create_task(client.get_part("LM358P"))
    try:
        await entered.wait()
        assert "error" not in await client.get_part("NE555P")
        saved = pool.quotas[0].daily_refusals()
        clock.now += delay
    finally:
        release.set()
        assert "error" not in await pending
    assert pool.active_index() == 1
    assert pool.quotas[0]._paused_until == NOW + 3600
    assert pool.quotas[0].daily_refusals() == saved
    assert len([r for r in caplog.records if "daily refusal at" in r.message]) == 1
    assert "accepted again" not in caplog.text


async def test_slow_check_allows_another_after_hold_and_cannot_release_its_hold(make, clock):
    entered, release = asyncio.Event(), asyncio.Event()
    second_entered, second_release = asyncio.Event(), asyncio.Event()
    requests = 0

    async def handler(request, index):
        nonlocal requests
        requests += 1
        if requests == 1:
            return httpx.Response(403, json=DAILY_403)
        if requests == 2:
            entered.set()
            await release.wait()
            raise httpx.ReadTimeout("offline")
        second_entered.set()
        await second_release.wait()
        return answer()

    client, pool, sent = make(handler, keys=1)
    assert "error" in await client.get_part("LM358P")
    clock.now += 3600
    first = asyncio.create_task(client.get_part("NE555P"))
    second = None
    try:
        await entered.wait()
        clock.now += 60
        second = asyncio.create_task(client.get_part("LM324P"))
        await second_entered.wait()
        release.set()
        with pytest.raises(MouserError):
            await first
        assert sent == [0, 0, 0] and pool.retry_after() == 60
        assert pool.checking()  # the older timeout must not forget the newer check
        assert "error" in await client.get_part("LM2904P")
        assert clock.waits == [1] * 30
    finally:
        release.set()
        second_release.set()
        await asyncio.gather(first, *([second] if second else []), return_exceptions=True)
    assert pool.retry_after() is None
    assert pool._checks == {}


@pytest.mark.parametrize("keys", [1, 3])
async def test_zero_daily_limit_disables_live_requests(make, clock, keys):
    client, pool, sent = make(lambda request, index: answer(), keys=keys, limit=0)
    for moment in (NOW, MOUSER_RESET, MOUSER_RESET + 3600):
        clock.now = moment
        assert "daily quota exceeded" in (await client.get_part("LM358P"))["error"]
    assert sent == [] and pool.retry_after() == MOUSER_RESET + 86400 - clock()


async def test_0108_quota_file_loads_counts_pauses_and_episodes(make, clock, tmp_path):
    clock.now = MOUSER_RESET - 600
    path = tmp_path / "quota.json"
    episode = {"at": clock() - 3600, "count": 500, "last_refused_at": clock() - 3600,
               "retries": 0, "resumed_at": None}
    path.write_text(json.dumps({"Mouser": {"date": "2026-11-19", "count": 500,
                    "paused_until": MOUSER_RESET + 60, "pause_reason": "daily_unknown",
                    "api_remaining": None, "api_limit": None, "daily_refusals": [episode]}}), encoding="utf-8")
    client, pool, sent = make(lambda request, index: answer(), keys=1, path=path)
    assert pool.status()["used_today"] == 500  # old midnight date label survives upgrade before 06:00
    assert pool.status()["paused_until"] == "2026-11-19 06:01 UTC"
    assert "error" in await client.get_part("LM358P") and sent == []
    clock.now = MOUSER_RESET
    assert pool.status()["used_today"] == 0
    clock.now += 60
    assert "error" not in await client.get_part("LM358P") and sent == [0]
    assert pool.quotas[0].daily_refusals() == [{**episode, "resumed_at": clock()}]


async def test_0108_open_episode_under_minute_pause_is_still_a_check(make, clock, tmp_path):
    # 0.10.8 could overwrite an open daily refusal's reason with a later per-minute pause.
    path = tmp_path / "quota.json"
    episode = {"at": clock() - 7200, "count": 1000, "last_refused_at": clock() - 3600,
               "retries": 1, "resumed_at": None}
    path.write_text(json.dumps({"Mouser": {"date": "2026-11-18", "count": 3,
                    "paused_until": clock() - 1, "pause_reason": "burst",
                    "api_remaining": None, "api_limit": None, "daily_refusals": [episode]}}), encoding="utf-8")
    client, pool, sent = make(lambda request, index: httpx.Response(403), keys=1, path=path)
    for number in ("LM358P", "NE555P", "TL072CP"):
        try:
            await client.get_part(number)
        except MouserError:
            pass
    assert sent == [0]  # the unexplained 403 on the check keeps checks hourly
    assert pool.retry_after() == 3600


async def test_dev_mouser_state_keeps_only_current_key(make, clock, tmp_path):
    path = tmp_path / "quota.json"
    old = {"current": 1, "retry_at": MOUSER_RESET + 86400, "buckets": [[int(NOW), 8, 7, 1]], "probe": 0}
    path.write_text(json.dumps({("Mouser" if i == 0 else f"Mouser#{i + 1}"): {"date": "2026-11-18", "count": 5, "mouser": old}
                               for i in range(3)}), encoding="utf-8")
    client, pool, sent = make(lambda request, index: answer(), path=path)
    assert "error" not in await client.get_part("LM358P") and sent == [1]
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["Mouser"]["mouser"] == {"current": 1}
    assert all(set(state.get("mouser", {})) <= {"current"} for state in saved.values())


@pytest.mark.parametrize("status", [401, 403])
async def test_unexplained_check_refusal_after_overlapping_acceptance_still_pauses(make, clock, status):
    entered, release = asyncio.Event(), asyncio.Event()
    requests = 0

    async def handler(request, index):
        nonlocal requests
        requests += 1
        if requests == 1:
            return httpx.Response(403, json=DAILY_403)
        if requests == 2:
            entered.set()
            await release.wait()
            return httpx.Response(status)
        return answer()

    client, pool, sent = make(handler, keys=1)
    assert "error" in await client.get_part("LM358P")
    clock.now += 3600
    pending = asyncio.create_task(client.get_part("NE555P"))
    try:
        await entered.wait()
        clock.now += 60
        assert "error" not in await client.get_part("LM324P")
        assert pool.retry_after() is None
    finally:
        release.set()
        reply = await pending
    assert "daily quota exceeded" in reply["error"]
    assert pool.retry_after() == 3600 and sent == [0, 0, 0]
    assert len(pool.quotas[0].daily_refusals()) == 2
