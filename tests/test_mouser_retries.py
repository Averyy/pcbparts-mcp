"""Mouser transient retries use real reservations but fake time and offline HTTP responses."""

import asyncio
import datetime
import json
import logging
import re

import httpx
import pytest

from pcbparts_mcp import stats
from pcbparts_mcp.cache import AddressDailyQuota, DailyQuota, MouserKeyPool, QuotaPool
from pcbparts_mcp.mouser import MouserAPIError, MouserClient, MouserError, MouserKeyRejected

NOW = datetime.datetime(2026, 11, 24, 12, tzinfo=datetime.timezone.utc).timestamp()


class Clock:
    def __init__(self):
        self.now = NOW
        self.waits = []

    def __call__(self):
        return self.now

    async def sleep(self, seconds):
        self.waits.append(seconds)
        self.now += seconds


def answer():
    return httpx.Response(200, json={"SearchResults": {"Parts": []}})


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
async def make(clock):
    made = []

    def create(*responses, **kwargs):
        pending = list(responses)
        requests = []

        def send(request):
            requests.append(request)
            response = pending.pop(0)
            if callable(response):
                response = response(request)
            if isinstance(response, Exception):
                raise response
            return response

        client = MouserClient("secret-key", clock=clock, sleep=clock.sleep, **kwargs)
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(send))
        made.append(client)
        return client, requests

    yield create
    for client in made:
        await client.close()


@pytest.mark.parametrize("failures", [1, 2])
async def test_503_then_success(make, clock, failures):
    client, requests = make(*[httpx.Response(503) for _ in range(failures)], answer())
    assert (await client.get_part("LM358P"))["total"] == 0
    assert len(requests) == failures + 1
    assert clock.waits == [3, 10][:failures]
    counts = stats.usage.summary()["days"][0]
    assert counts["upstream_status"]["mouser"] == {"5xx": failures, "2xx": 1}
    assert counts["distributors"]["mouser"]["retries"] == failures


async def test_three_failures_keep_the_error(make, clock):
    client, requests = make(*[httpx.Response(503) for _ in range(3)])
    with pytest.raises(MouserError) as error:
        await client.get_part("LM358P")
    assert str(error.value) == "Mouser API returned HTTP 503"
    assert len(requests) == 3 and clock.waits == [3, 10]


@pytest.mark.parametrize("header,waits", [
    ("7", [7]), ("0", [0]), ("30", [30]), ("31", []),
    ("Tue, 24 Nov 2026 12:00:11 GMT", [11]), ("Tue, 24 Nov 2026 12:00:31 GMT", []),
    ("Tue, 24 Nov 2026 11:59:59 GMT", [0]), ("invalid", [3]),
], ids=["seconds", "zero", "max", "over", "date", "date_over", "past", "invalid"])
async def test_retry_after(make, clock, header, waits, caplog):
    client, requests = make(httpx.Response(503, headers={"Retry-After": header}), answer())
    if waits:
        assert (await client.get_part("LM358P"))["total"] == 0
    else:
        with pytest.raises(MouserError, match="Mouser API returned HTTP 503"):
            await client.get_part("LM358P")
    assert clock.waits == waits and len(requests) == len(waits) + 1
    assert all(type(wait) is int for wait in clock.waits)  # whole seconds stay whole
    line, = diagnostics(caplog)
    # the log reads delay=7 (and 0) for whole seconds, not 7.0
    assert re.search(rf"retry={bool(waits)} delay={waits[0] if waits else None}(?![.\d])", line), line


@pytest.mark.parametrize("delays,waits", [([20, 20], [20]), ([20, 10], [20, 10]), ([30, None], [30])],
                         ids=["over", "exact", "default_over"])
async def test_total_wait_is_bounded(make, clock, delays, waits):
    client, requests = make(*[httpx.Response(503, headers={"Retry-After": str(d)} if d is not None else {})
                              for d in delays], answer())
    if len(waits) == 2:
        await client.get_part("LM358P")
    else:
        with pytest.raises(MouserError, match="HTTP 503"):
            await client.get_part("LM358P")
    assert clock.waits == waits and len(requests) == len(waits) + 1


@pytest.mark.parametrize("failure", [httpx.ConnectError, httpx.ReadError, httpx.WriteError, httpx.RemoteProtocolError])
async def test_transport_errors_retry_without_logging_the_exception(make, clock, caplog, failure):
    client, requests = make(failure("https://example.test/?apiKey=secret-key&part=PRIVATE123"), answer())
    await client.get_part("LM358P")
    assert clock.waits == [3] and len(requests) == 2
    assert failure.__name__ in caplog.text
    assert "secret-key" not in caplog.text and "PRIVATE123" not in caplog.text


@pytest.mark.parametrize("failure", [httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout])
async def test_timeouts_do_not_retry(make, clock, failure):
    client, requests = make(failure("secret-key"))
    with pytest.raises(MouserError) as error:
        await client.get_part("LM358P")
    assert str(error.value) == "Mouser API request failed (network/connection error)"
    assert len(requests) == 1 and clock.waits == []


@pytest.mark.parametrize("with_quota", [False, True])
async def test_closed_client_fails_without_retry_or_send_counts(make, clock, monkeypatch, with_quota):
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    quota = pool(clock) if with_quota else None
    client, requests = make(answer(), quota=quota)
    await client.close()
    with pytest.raises(MouserError, match=r"^Mouser API request failed \(network/connection error\)$"):
        await client.get_part("LM358P")
    assert requests == [] and clock.waits == []
    counts = stats.usage.summary()["days"][0]
    assert "mouser" not in counts["upstream_status"]
    assert "mouser" not in counts["distributors"]
    assert not client._guard.outcomes
    if quota is not None:
        assert quota.status()["used_today"] == 0


@pytest.mark.parametrize("status", [400, 401, 403, 404])
async def test_4xx_do_not_retry(make, clock, status):
    client, requests = make(httpx.Response(status, text="unreadable"))
    with pytest.raises(MouserError) as error:
        await client.get_part("LM358P")
    assert str(error.value) == f"Mouser API returned HTTP {status}"
    assert len(requests) == 1 and clock.waits == []


@pytest.mark.parametrize("status", [200, 503])
async def test_errors_are_not_transient(make, clock, status):
    client, requests = make(httpx.Response(status, json={"Errors": [{"Code": "BadPart", "Message": "bad part"}]}))
    with pytest.raises(MouserAPIError, match="BadPart"):
        await client.get_part("LM358P")
    assert len(requests) == 1 and clock.waits == []


async def test_key_rejection_is_not_transient(make, clock):
    client, requests = make(httpx.Response(200, json={
        "Errors": [{"Code": "InvalidIdentifier", "Message": "Invalid unique identifier.", "PropertyName": "API Key"}]}),
        quota=DailyQuota("Mouser", 1000, clock=clock, day_start_hour=6))
    with pytest.raises(MouserKeyRejected):
        await client.get_part("LM358P")
    assert len(requests) == 1 and clock.waits == []


@pytest.mark.parametrize("status", [200, 403, 503, 429])
async def test_limit_refusals_do_not_transient_retry(make, clock, status):
    client, requests = make(httpx.Response(status, json={"Errors": [
        {"Code": "TooManyRequests", "Message": "Maximum calls per day exceeded.", "ResourceKey": "MaxCallPerDay"}]}),
        quota=DailyQuota("Mouser", 1000, clock=clock, day_start_hour=6))
    reply = await client.get_part("LM358P")
    assert reply["error"].startswith("Mouser daily quota exceeded")
    assert len(requests) == 1 and clock.waits == []


@pytest.mark.parametrize("body", ["html", None, [], {}, {"SearchResults": None},
                                 {"Errors": [], "SearchResults": {"Parts": None}}],
                         ids=["html", "null", "list", "empty", "no_results", "no_parts"])
async def test_unreadable_replies_retry(make, clock, body):
    failure = httpx.Response(200, text=body) if body == "html" else httpx.Response(200, content=json.dumps(body))
    client, requests = make(failure, answer())
    await client.get_part("LM358P")
    assert len(requests) == 2 and clock.waits == [3]


def pool(clock, *, kind=MouserKeyPool, per_minute=25, keys=1, address_limit=1, limit=1000):
    address = AddressDailyQuota(address_limit, key=lambda caller: caller, clock=clock)
    return kind([DailyQuota("Mouser", limit, clock=clock, day_start_hour=6) for _ in range(keys)],
                per_minute=per_minute, address_daily=address)


@pytest.mark.parametrize("kind", [QuotaPool, MouserKeyPool])
async def test_retries_neither_check_nor_count_the_address(make, clock, caplog, kind):
    quota = pool(clock, kind=kind)
    client, requests = make(httpx.Response(503), httpx.Response(502), answer(), quota=quota)
    assert (await client.get_part("LM358P", caller="203.0.113.1"))["total"] == 0
    assert quota.quotas[0]._count == len(requests) == 3
    assert quota.address_daily._counts == {"203.0.113.1": 1}
    with caplog.at_level(logging.INFO):
        quota.callers.flush()
    assert "Mouser requests sent" in caplog.text and "3 from 1 IPs" in caplog.text
    assert "This address has used its 1" in (await client.get_part("NE555P", caller="203.0.113.1"))["error"]
    assert len(requests) == 3


async def test_minute_cap_holds_the_retry(make, clock):
    quota = pool(clock, per_minute=1)
    client, requests = make(httpx.Response(503), quota=quota)
    reply = await client.get_part("LM358P", caller="203.0.113.1")
    assert "limited to 1 a minute" in reply["error"]
    assert quota.quotas[0]._count == len(requests) == 1
    assert quota.last_refusal_cause == "minute_cap"
    counts = stats.usage.summary()["days"][0]
    assert counts["distributors"]["mouser"] == {"sent": 1, "cached": 0, "rate_limited": 1}
    assert counts["distributor_limits"]["mouser"]["held_back"]["minute_cap"] == 1


async def test_retry_cannot_overdraw_a_count_based_pool(make, clock):
    quota = pool(clock, kind=QuotaPool, limit=1)
    client, requests = make(httpx.Response(503), quota=quota)
    assert "daily quota exceeded" in (await client.get_part("LM358P"))["error"]
    assert quota.quotas[0]._count == len(requests) == 1


async def test_retry_reserves_the_current_key(make, clock):
    quota = pool(clock, keys=2)

    def rotate(request):
        quota.refuse_daily(0, quota.sent(0), quota.quotas[0]._count)  # a concurrent call refused this key
        return httpx.Response(503)

    client, requests = make(rotate, answer(), quota=quota, extra_keys=["other-key"])
    await client.get_part("LM358P", caller="203.0.113.1")
    assert [r.url.params["apiKey"] for r in requests] == ["secret-key", "other-key"]
    assert [q._count for q in quota.quotas] == [1, 1]
    assert quota.address_daily._counts == {"203.0.113.1": 1}


async def test_limit_reply_during_retry_stops_it(make, clock):
    quota = pool(clock)
    client, requests = make(httpx.Response(503), httpx.Response(429, headers={"Retry-After": "17"}), quota=quota)
    assert "Try again in 17 s" in (await client.get_part("LM358P"))["error"]
    assert len(requests) == 2 and clock.waits == [3]


async def test_batch_is_resent_whole_and_kept_per_part(make, clock):
    parts = [{"ManufacturerPartNumber": n, "MouserPartNumber": f"595-{n}", "Manufacturer": "TI"}
             for n in ("LM358P", "NE555P")]
    client, requests = make(httpx.Response(503), httpx.Response(200, json={"SearchResults": {"Parts": parts}}))
    assert (await client.get_part("LM358P|NE555P"))["total"] == 2
    assert len(requests) == 2 and requests[0].content == requests[1].content
    assert json.loads(requests[1].content)["SearchByPartRequest"]["mouserPartNumber"] == "LM358P|NE555P"
    for number in ("LM358P", "NE555P"):
        assert (await client.get_part(number))["total"] == 1
        assert client._store.get_answer("mouser", number) is not None
    assert len(requests) == 2


async def test_cancelled_caller_keeps_retry_and_answer(make, clock):
    client, requests = make(httpx.Response(503), answer())
    sleeping, release = asyncio.Event(), asyncio.Event()

    async def sleep(seconds):
        await clock.sleep(seconds)
        sleeping.set()
        await release.wait()

    client._sleep = sleep
    caller = asyncio.create_task(client.get_part("LM358P"))
    await sleeping.wait()
    tasks = tuple(client._tasks)
    caller.cancel()
    with pytest.raises(asyncio.CancelledError):
        await caller
    release.set()
    await asyncio.gather(*tasks)
    assert client._store.get_answer("mouser", "LM358P") is not None
    await client.get_part("LM358P")
    assert len(requests) == 2 and clock.waits == [3]


@pytest.mark.parametrize("recovery", ["parts", "errors", "limit"])
async def test_outage_guard_across_callers(make, clock, caplog, recovery):
    readable = {"parts": answer(), "errors": httpx.Response(200, json={"Errors": [{"Code": "BadPart"}]}),
                "limit": httpx.Response(429)}[recovery]
    client, requests = make(*[httpx.Response(503) for _ in range(11)], readable, readable,
                            httpx.Response(503), answer())
    for index, expected in enumerate((3, 6, 9, 10, 11)):
        with pytest.raises(MouserError, match="HTTP 503"):
            await client.get_part(f"PART{index}A", caller=str(index))
        assert len(requests) == expected
    assert clock.waits == [3, 10] * 3
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.mouser"):
        for index in range(2):
            if recovery == "errors":
                with pytest.raises(MouserAPIError):
                    await client.get_part(f"RECOVER{index}")
            else:
                await client.get_part(f"RECOVER{index}")
    await client.get_part("PART5A")
    assert len(requests) == 15 and clock.waits == [3, 10] * 3 + [3]
    entered = [r for r in caplog.records if "retry guard entered" in r.message]
    cleared = [r for r in caplog.records if "retry guard cleared" in r.message]
    assert len(entered) == len(cleared) == 1
    assert entered[0].levelno == logging.WARNING and "10/10" in entered[0].message
    assert cleared[0].levelno == logging.INFO and "11/13" in cleared[0].message


async def test_guard_stops_an_already_waiting_retry(make, clock):
    client, requests = make(*[httpx.Response(503, headers={"Retry-After": "31"} if i else {}) for i in range(10)])
    sleeping, release = asyncio.Event(), asyncio.Event()

    async def sleep(seconds):
        sleeping.set()
        await release.wait()

    client._sleep = sleep
    waiting = asyncio.create_task(client.get_part("WAIT123"))
    await sleeping.wait()
    for i in range(9):
        with pytest.raises(MouserError):
            await client.get_part(f"PART{i}A")
    release.set()
    with pytest.raises(MouserError):
        await waiting
    assert len(requests) == 10


def diagnostics(caplog):
    return [r.message for r in caplog.records if r.name == "pcbparts_mcp.mouser" and "transient failure:" in r.message]


async def test_log_headers_body_redaction_and_throttle(make, clock, caplog):
    body = "busy\n\tsecret-key other-key " + "x" * 250
    headers = {"Retry-After": "3", "Server": "other-key", "Content-Type": "text/html"}
    quota = pool(clock, keys=2)
    client, requests = make(*[httpx.Response(503, text=body, headers=headers) for _ in range(3)],
                            httpx.Response(502, text="next"), answer(), quota=quota, extra_keys=["other-key"])
    with pytest.raises(MouserError):
        await client.get_part("LM358P")
    line, = diagnostics(caplog)
    assert "HTTP 503 attempt=1 key=1 retry=True delay=3" in line
    assert "Retry-After='3' Server='[redacted]' Content-Type='text/html'" in line
    assert f"body_length={len(body)}" in line
    assert "body=" + repr(("busy [redacted] [redacted] " + "x" * 250)[:200]) in line
    assert "secret-key" not in caplog.text and "other-key" not in caplog.text
    clock.now = NOW + 60
    await client.get_part("NE555P")
    assert len(diagnostics(caplog)) == 2
    assert "2 more since 12:00 UTC" in diagnostics(caplog)[1]
    assert "HTTP 502" in diagnostics(caplog)[1]


@pytest.mark.parametrize("is_json", [True, False])
async def test_unreadable_log_omits_body(make, caplog, is_json):
    response = (httpx.Response(200, json={"SearchResults": "PRIVATE123", "Errors": [], "secret-key": "PRIVATE456"})
                if is_json else httpx.Response(200, text="<html>PRIVATE123 secret-key</html>"))
    client, _ = make(response, answer())
    await client.get_part("LM358P")
    line, = diagnostics(caplog)
    assert "HTTP 200 attempt=1 key=1 retry=True delay=3" in line
    assert f"json={is_json}" in line and "top_keys=" in line and "body_length=" in line
    if is_json:
        assert "top_keys=('SearchResults', 'Errors', '[redacted]')" in line
    assert "PRIVATE" not in caplog.text and "secret-key" not in caplog.text and "body=" not in line


async def test_final_attempt_is_logged_as_no_retry(make, clock, caplog):
    def failure(request):
        clock.now += 60
        return httpx.Response(503)

    client, _ = make(failure, failure, failure)
    with pytest.raises(MouserError):
        await client.get_part("LM358P")
    assert "attempt=3 key=1 retry=False delay=None" in diagnostics(caplog)[-1]
