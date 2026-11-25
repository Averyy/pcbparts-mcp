"""Per-address distributor fairness and held-back logs: fake UTC clocks and HTTP only."""

import asyncio
import ipaddress
import json
import logging
import math
from types import SimpleNamespace

import httpx
import pytest
from fastmcp import Client

from pcbparts_mcp import digikey, platform_ranges, server, stats
from pcbparts_mcp.cache import AddressDailyQuota, DailyQuota, MouserKeyPool, Pacer, QuotaPool, QuotaStore
from pcbparts_mcp.digikey import DigiKeyClient
from pcbparts_mcp.distributor_store import DistributorStore
from pcbparts_mcp.lifecycle import Entry, LifecycleLookup
from pcbparts_mcp.mouser import MouserClient

from test_distributor_quota import Clock, MIDNIGHT


ADDRESS = "192.0.2.1"
OTHER = "192.0.2.2"


@pytest.fixture
def clock(monkeypatch):
    clock = Clock()
    monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
    monkeypatch.setattr(digikey, "time", SimpleNamespace(time=clock))
    return clock


class FakeDistributor:
    def __init__(self, name):
        self.name = name
        self.sent = []
        self.tokens = 0
        self.reply = None

    def __call__(self, request):
        if "oauth2/token" in str(request.url):
            self.tokens += 1
            return httpx.Response(200, json={"access_token": "token", "expires_in": 3600})
        body = json.loads(request.content)
        self.sent.append(body)
        if self.reply is not None:
            return self.reply
        if self.name == "Mouser":
            numbers = body["SearchByPartRequest"]["mouserPartNumber"].split("|")
            return httpx.Response(200, json={"SearchResults": {"Parts": [
                {"ManufacturerPartNumber": number, "Manufacturer": "Test"} for number in numbers]}})
        number = body["Keywords"]
        return httpx.Response(200, json={"ExactMatches": [
            {"ManufacturerProductNumber": number, "Manufacturer": {"Name": "Test"},
             "ProductStatus": {"Status": "Active"}}]})


@pytest.fixture
async def clients(clock):
    made = []

    def make(name, limit=100, minute=None, ranges=None, store=None, shared_limit=1000, extra=False,
             address_daily=None):
        ranges = ranges or platform_ranges.PlatformRanges()
        address_daily = address_daily or AddressDailyQuota(
            limit, key=lambda ip: None if ip in ranges else server._address_key(ip), clock=clock)
        quotas = [DailyQuota(name, shared_limit, clock=clock, day_start_hour=6 if name == "Mouser" else 0)
                  for _ in range(2 if extra else 1)]
        pool_type = MouserKeyPool if name == "Mouser" else QuotaPool
        pool = pool_type(quotas, per_minute=minute, address_daily=address_daily)
        fake = FakeDistributor(name)
        http = httpx.AsyncClient(transport=httpx.MockTransport(fake))
        if name == "Mouser":
            client = MouserClient("key", quota=pool, clock=clock, store=store,
                                  extra_keys=["extra"] if extra else ())
            client._client = http
        else:
            client = DigiKeyClient("id", "secret", quota=pool, clock=clock, store=store,
                                   second_app=("extra", "secret2") if extra else None)
            client._http = http

            async def sleep(seconds):
                clock.advance(seconds)

            client._pacer = Pacer(5, clock=clock, sleep=sleep)
        made.append(client)
        return client, pool, fake

    yield make
    for client in made:
        await client.close()


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
async def test_101st_refused_other_address_and_cached_answers_still_work(clients, name):
    client, pool, fake = clients(name)
    for index in range(100):
        assert "error" not in await client.get_part(f"TEST{index:03}", caller=ADDRESS)
    assert len(fake.sent) == 100
    tokens = fake.tokens
    assert await client.get_part("TEST100", caller=ADDRESS) == {"error": (
        "This address has used its 100 Mouser and DigiKey lookups for today on this shared server; "
        "the count resets at 00:00 UTC. Answers pcbparts already has stored still work. Meanwhile use jlc_search.")}
    assert len(fake.sent) == 100 and fake.tokens == tokens
    assert "error" not in await client.get_part("TEST000", caller=ADDRESS)
    assert len(fake.sent) == 100
    assert "error" not in await client.get_part("TEST100", caller=OTHER)
    assert len(fake.sent) == 101 and pool.quotas[0]._count == 101
    day = stats.usage.summary()["days"][0]
    assert day["distributor_limits"][name.lower()]["held_back"]["address_daily"] == 1
    assert day["distributors"][name.lower()]["rate_limited"] == 1
    assert ADDRESS not in json.dumps(day)
    assert ADDRESS not in json.dumps(pool.status())


def shared_cap(clock, limit):
    """One count for both distributors, as the server wires it."""
    return AddressDailyQuota(limit, key=server._address_key, clock=clock)


async def test_distributors_share_one_count_and_mouser_batch_costs_one_request(clients, clock):
    cap = shared_cap(clock, 2)
    mouser, mq, mf = clients("Mouser", address_daily=cap)
    dk, dq, df = clients("DigiKey", address_daily=cap)
    assert (await mouser.get_part("TEST123|TEST456|TEST789", caller=ADDRESS))["total"] == 3
    assert len(mf.sent) == 1 and cap._counts == {ADDRESS: 1}
    assert "error" not in await dk.get_part("TEST123", caller=ADDRESS)
    assert len(df.sent) == 1 and cap._counts == {ADDRESS: 2}
    # The two lookups together spent the address's day for both distributors
    assert "Mouser and DigiKey lookups" in (await mouser.get_part("TEST999", caller=ADDRESS))["error"]
    assert "Mouser and DigiKey lookups" in (await dk.get_part("TEST999", caller=ADDRESS))["error"]
    assert len(mf.sent) == len(df.sent) == 1
    assert "error" not in await dk.get_part("TEST999", caller=OTHER)


@pytest.mark.parametrize("failure", ["daily", "token"])
async def test_digikey_second_attempt_neither_checks_nor_counts_address(clients, failure):
    client, pool, fake = clients("DigiKey", limit=2, extra=failure == "daily")
    # Force the second attempt through OAuth as well as the product request checks.
    original = fake.__call__

    def respond(request):
        if "oauth2/token" not in str(request.url) and not fake.sent:
            fake.sent.append("refused")
            return (httpx.Response(429, headers={"x-ratelimit-remaining": "0"}) if failure == "daily"
                    else httpx.Response(401))
        return original(request)

    await client._http.aclose()
    client._http = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    pool.address_daily.record(ADDRESS)
    assert "error" not in await client.get_part("LM358P", caller=ADDRESS)
    assert len(fake.sent) == 2 and fake.tokens == 2
    assert pool.address_daily._counts == {ADDRESS: 2}
    assert sum(q._count for q in pool.quotas) == 2
    assert "This address has used its 2" in (await client.get_part("NE555P", caller=ADDRESS))["error"]
    assert len(fake.sent) == 2 and fake.tokens == 2


async def test_one_distributor_alone_spends_the_shared_count(clients, clock):
    cap = shared_cap(clock, 1)
    mouser, _, mf = clients("Mouser", address_daily=cap)
    dk, _, df = clients("DigiKey", address_daily=cap)
    assert "error" not in await dk.get_part("TEST123", caller=ADDRESS)
    assert "error" in await mouser.get_part("TEST999", caller=ADDRESS)
    assert len(df.sent) == 1 and mf.sent == []


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
async def test_platform_addresses_and_none_exempt(clients, name):
    ranges = platform_ranges.PlatformRanges({"test": [ipaddress.ip_network("160.79.104.0/21")]})
    limiter = server.RateLimitMiddleware(None, platform_addresses=ranges)
    client, pool, fake = clients(name, limit=1, ranges=ranges)
    for caller in ("160.79.104.1", "::ffff:160.79.104.1", None):
        assert caller is None or limiter._is_platform(caller)
        for index in range(3):
            assert "error" not in await client.get_part(f"PART{len(fake.sent):03}", caller=caller)
    assert len(fake.sent) == 9 and pool.address_daily._counts == {}


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
async def test_ipv6_64_and_ipv4_mapped_addresses_share_count(clients, name):
    client, _, fake = clients(name, limit=1)
    assert "error" not in await client.get_part("TEST123", caller="2001:db8:1:2::1")
    assert "error" in await client.get_part("TEST456", caller="2001:db8:1:2::abcd")
    assert "error" not in await client.get_part("TEST789", caller="2001:db8:1:3::1")
    assert "error" not in await client.get_part("TEST321", caller=ADDRESS)
    assert "error" in await client.get_part("TEST654", caller="::ffff:192.0.2.1")
    assert len(fake.sent) == 3


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
async def test_utc_day_resets_and_zero_disables(clients, clock, name):
    client, pool, fake = clients(name, limit=1)
    await client.get_part("TEST123", caller=ADDRESS)
    assert "error" in await client.get_part("TEST456", caller=ADDRESS)
    assert client.retry_after(ADDRESS) == math.ceil(MIDNIGHT - clock())
    clock.now = MIDNIGHT
    assert "error" not in await client.get_part("TEST456", caller=ADDRESS)
    assert pool.address_daily._counts == {ADDRESS: 1} and len(fake.sent) == 2
    assert pool.quotas[0].status()["used_today"] == (2 if name == "Mouser" else 1)
    clock.now = MIDNIGHT + 6 * 3600
    assert "error" in await client.get_part("TEST789", caller=ADDRESS)  # address cap is still UTC-day based
    assert client.retry_after(ADDRESS) == 18 * 3600
    assert pool.quotas[0].status()["used_today"] == (0 if name == "Mouser" else 1)
    off, off_pool, off_fake = clients(name, limit=0)
    for number in ("TEST123", "TEST456", "TEST789"):
        assert "error" not in await off.get_part(number, caller=ADDRESS)
    assert len(off_fake.sent) == 3 and off_pool.address_daily._counts == {}


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
async def test_capped_address_does_not_consume_minute_budget(clients, clock, name):
    client, pool, fake = clients(name, limit=1, minute=1)
    await client.get_part("TEST123", caller=ADDRESS)
    clock.advance(60)
    assert "error" in await client.get_part("TEST456", caller=ADDRESS)
    assert pool._minute.used == 0
    assert "error" not in await client.get_part("TEST456", caller=OTHER)
    assert pool._minute.used == 1 and len(fake.sent) == 2


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
async def test_no_token_request_for_initially_capped_address(clients, name):
    client, pool, fake = clients(name, limit=1)
    pool.address_daily.record(ADDRESS)
    assert "error" in await client.get_part("TEST123", caller=ADDRESS)
    assert fake.tokens == 0 and fake.sent == []


async def test_address_capped_while_waiting_for_token_sends_nothing(clients, clock):
    client, pool, fake = clients("DigiKey", limit=1)

    async def wait():
        pool.address_daily.record(ADDRESS)

    client._pacer.wait = wait
    assert "error" in await client.get_part("TEST123", caller=ADDRESS)
    assert fake.tokens == 0 and fake.sent == [] and pool.quotas[0]._count == 0
    day = stats.usage.summary()["days"][0]
    assert day["distributor_limits"]["digikey"]["held_back"]["address_daily"] == 1
    assert pool.held_back._counts == {ADDRESS: 1}


async def test_address_capped_while_waiting_for_lookup_slot_sends_nothing(clients):
    client, pool, fake = clients("DigiKey", limit=1)
    client._apps[0].access_token = "token"
    client._apps[0].token_expires_at = float("inf")

    async def wait():
        pool.address_daily.record(ADDRESS)

    client._pacer.wait = wait
    assert "error" in await client.get_part("TEST123", caller=ADDRESS)
    assert fake.tokens == 0 and fake.sent == [] and pool.quotas[0]._count == 0


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
async def test_cached_misses_still_served(clients, name):
    client, _, fake = clients(name, limit=1)
    fake.reply = httpx.Response(200, json={"SearchResults": {"Parts": []}} if name == "Mouser" else {})
    first = await client.get_part("TEST123", caller=ADDRESS)
    assert "not found" in first.get("error", "").lower() or first.get("not_found")
    assert await client.get_part("TEST123", caller=ADDRESS) == first
    assert len(fake.sent) == 1


async def test_partial_mouser_answers_survive_address_cap(clients):
    client, _, fake = clients("Mouser", limit=1)
    await client.get_part("TEST123", caller=ADDRESS)
    reply = await client.get_part("TEST123|TEST456", caller=ADDRESS)
    assert reply["total"] == 1 and reply["not_checked"] == ["TEST456"]
    assert reply["retry_after"] > 60 and len(fake.sent) == 1


async def test_mouser_rejected_batch_counts_each_actual_request(clients):
    client, pool, fake = clients("Mouser", limit=2)
    original = fake.__call__

    def answer(request):
        body = json.loads(request.content)
        if "|" in body["SearchByPartRequest"]["mouserPartNumber"]:
            fake.sent.append(body)
            return httpx.Response(200, json={"Errors": [{"Code": "BadPart", "Message": "Rejected"}]})
        return original(request)

    await client._client.aclose()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(answer))
    reply = await client.get_part("TEST123|TEST456|TEST789", caller=ADDRESS)
    assert reply["total"] == 1 and reply["not_checked"] == ["TEST456", "TEST789"]
    assert len(fake.sent) == 2 and pool.address_daily._counts == {ADDRESS: 2}


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
async def test_cap_applies_across_pool_credentials(clients, name):
    client, pool, fake = clients(name, limit=1, shared_limit=1, extra=True)
    await client.get_part("TEST123", caller=ADDRESS)
    assert "error" in await client.get_part("TEST456", caller=ADDRESS)
    assert "error" not in await client.get_part("TEST456", caller=OTHER)
    assert len(fake.sent) == 2 and [q._count for q in pool.quotas] == ([2, 0] if name == "Mouser" else [1, 1])


async def test_lifecycle_past_both_caps_and_stored_readings(clients, clock):
    store = DistributorStore(clock=clock)
    try:
        cap = shared_cap(clock, 2)
        mouser, mq, mf = clients("Mouser", store=store, address_daily=cap)
        dk, dq, df = clients("DigiKey", store=store, address_daily=cap)
        await mouser.get_part("TEST123", caller=ADDRESS)
        await dk.get_part("TEST123", caller=ADDRESS)
        lookup = LifecycleLookup(store, mouser, dk)
        rows = await lookup.answer([Entry("TEST123", mpn="TEST123"), Entry("TEST456", mpn="TEST456")], caller=ADDRESS)
        assert rows[0]["status"] == "active" and "retry_after" not in rows[0]
        assert rows[1]["status"] == "unknown" and rows[1]["retry_after"] == math.ceil(MIDNIGHT - clock())
        assert "not_found" not in rows[1] and "lookup_failed" not in rows[1]
        assert len(mf.sent) == len(df.sent) == 1
        assert mq.held_back._counts == dq.held_back._counts == {ADDRESS: 1}
    finally:
        store.close()


async def test_lifecycle_sends_to_neither_distributor_once_the_shared_count_is_spent(clients, clock):
    store = DistributorStore(clock=clock)
    try:
        cap = shared_cap(clock, 1)
        mouser, _, mf = clients("Mouser", store=store, address_daily=cap)
        dk, _, df = clients("DigiKey", store=store, address_daily=cap)
        await mouser.get_part("TEST123", caller=ADDRESS)
        rows = await LifecycleLookup(store, mouser, dk).answer([Entry("TEST456", mpn="TEST456")], caller=ADDRESS)
        assert rows[0]["status"] == "unknown" and rows[0]["retry_after"] == math.ceil(MIDNIGHT - clock())
        assert "not_found" not in rows[0] and "lookup_failed" not in rows[0]
        assert len(mf.sent) == 1 and df.sent == []
        # Another address is unaffected
        other = await LifecycleLookup(store, mouser, dk).answer([Entry("TEST456", mpn="TEST456")], caller=OTHER)
        assert other[0]["status"] == "active"
    finally:
        store.close()


async def test_lifecycle_crowded_followup_does_not_use_second_address_allowance(clients, clock, monkeypatch):
    send = FakeDistributor.__call__

    def first_reply_only(fake, request):
        response = send(fake, request)
        fake.reply = None
        return response

    monkeypatch.setattr(FakeDistributor, "__call__", first_reply_only)
    store = DistributorStore(clock=clock)
    try:
        mouser, pool, fake = clients("Mouser", limit=1, store=store)
        fake.reply = httpx.Response(200, json={"SearchResults": {"Parts": [
            {"ManufacturerPartNumber": f"TEST123{index:02}", "Manufacturer": "Test"} for index in range(50)]}})
        rows = await LifecycleLookup(store, mouser, None).answer(
            [Entry(number, mpn=number) for number in ("TEST123", "TEST456")], caller=ADDRESS)
        # The follow-up finds TEST456 despite the address cap.
        assert rows[1]["status"] == "active" and "lookup_failed" not in rows[1]
        assert "not_found" not in rows[1] and "retry_after" not in rows[1]
        assert store.get_answer("mouser", "TEST456")[0]["matched"] is True
        assert [body["SearchByPartRequest"]["mouserPartNumber"] for body in fake.sent] == ["TEST123|TEST456", "TEST456"]
        assert pool.address_daily._counts == {ADDRESS: 1}
        assert pool.held_back._counts == {}
    finally:
        store.close()


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
@pytest.mark.parametrize("cause", ["minute_cap", "daily_count", "distributor_daily", "distributor_minute",
                                  "distributor_refused", "address_daily"])
async def test_each_cause_logs_one_held_back_line(clients, clock, caplog, name, cause):
    client, pool, fake = clients(name, limit=1, minute=1, extra=True)
    if cause == "minute_cap":
        pool.acquire()
    elif cause == "daily_count":
        for q in pool.quotas:
            if name == "Mouser":
                q._limit = 0  # only the explicit disable still gates Mouser by local configuration
            q._count = q._limit
    elif cause == "address_daily":
        pool.address_daily.record(ADDRESS)
    elif cause == "distributor_daily" and name == "Mouser":
        for index in range(len(pool.quotas)):
            pool.quotas[index].pause_daily_unknown_reset()
    else:
        for q in pool.quotas:
            q.pause(clock() + 3600, {"distributor_daily": "daily", "distributor_minute": "burst",
                                    "distributor_refused": "refused"}[cause])
    assert "error" in await client.get_part("TEST123", caller=ADDRESS)
    assert fake.sent == []
    clock.advance(3600)
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
        pool.held_back.flush_if_due()
        pool.held_back.flush_if_due()
    assert [r.message for r in caplog.records if "calls held back" in r.message] == [
        f"{name} calls held back 2026-10-16 21:00-22:00 UTC: 1 from 1 IPs; all: {ADDRESS} 1"]
    day = stats.usage.summary()["days"][0]
    assert day["distributor_limits"][name.lower()]["held_back"][cause] == 1


def test_address_table_bound_oldest_dropped_day_reset_and_memory_only(clock, tmp_path):
    address_daily = AddressDailyQuota(1, key=server._address_key, clock=clock, max_addresses=3)
    path = tmp_path / "quotas.json"
    quota = DailyQuota("DigiKey", 1000, store=QuotaStore(path), clock=clock)
    pool = QuotaPool([quota], address_daily=address_daily)
    for ip in (ADDRESS, OTHER, "192.0.2.3"):
        assert pool.acquire(ip) == (0, None)
    assert pool.acquire(ADDRESS)[1] is not None
    assert pool.acquire("192.0.2.4") == (0, None)
    assert list(address_daily._counts) == [OTHER, "192.0.2.3", "192.0.2.4"]
    assert pool.acquire(ADDRESS) == (0, None)  # oldest was dropped, as documented
    assert len(address_daily._counts) == 3
    saved = path.read_text(encoding="utf-8")
    assert ADDRESS not in saved and OTHER not in saved and "address_daily" not in saved
    assert ADDRESS not in json.dumps(pool.status())
    clock.now = MIDNIGHT
    assert not address_daily.capped(OTHER) and address_daily._counts == {}
    assert not AddressDailyQuota(1, key=server._address_key, clock=clock).capped(ADDRESS)


def test_default_address_table_bound_is_20000(clock):
    budget = AddressDailyQuota(1, key=lambda ip: ip, clock=clock)
    for index in range(20_001):
        budget.record(str(index))
    assert len(budget._counts) == 20_000 and "0" not in budget._counts


async def test_minute_task_flushes_both_distributors(clients, clock, monkeypatch, caplog):
    pools = {}
    for name in ("Mouser", "DigiKey"):
        client, pool, _ = clients(name, limit=1)
        pool.address_daily.record(ADDRESS)
        await client.get_part("TEST123", caller=ADDRESS)
        pools[name.lower()] = pool
    clock.advance(3600)
    monkeypatch.setattr(server, "_distributor_quotas", pools)
    monkeypatch.setattr(server, "_exit_if_stuck", lambda count: count)
    calls = 0

    async def minute(seconds):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise asyncio.CancelledError

    monkeypatch.setattr(server.asyncio, "sleep", minute)
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"), pytest.raises(asyncio.CancelledError):
        await server._every_minute()
    assert {r.message.split(" calls")[0] for r in caplog.records if "calls held back" in r.message} == {
        "Mouser", "DigiKey"}


async def test_server_wires_default_caps_and_shutdown_flushes_tallies(clock, monkeypatch, caplog):
    monkeypatch.setattr(server, "MOUSER_API_KEY", "test-key")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "test-id")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(server, "ANTHROPIC_IP_RANGES", ["160.79.104.0/21"])
    monkeypatch.setattr(server, "OPENAI_IP_RANGES_FILE", "")
    monkeypatch.setattr(server, "DailyQuota", lambda *args, **kw: DailyQuota(*args, clock=clock, **kw))
    monkeypatch.setattr(server, "AddressDailyQuota", lambda *args, **kw: AddressDailyQuota(*args, clock=clock, **kw))
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
        async with Client(server.mcp):
            pools = list(server._distributor_quotas.values())
            assert len(pools) == 2 and pools[0].address_daily is pools[1].address_daily  # one count for both
            for name, pool in server._distributor_quotas.items():
                assert pool.address_daily.limit == 1000
                pool.address_daily.record(ADDRESS, 1000)
                assert pool.address_error(ADDRESS) is not None
                assert pool.address_error(None) is None
                assert pool.address_error("160.79.104.1") is None
                pool.held_back.record(ADDRESS)
                health = json.loads((await server.health(None)).body)
                assert "address_daily" not in json.dumps(health) and ADDRESS not in json.dumps(health)
    assert [r.message for r in caplog.records if "calls held back" in r.message] == [
        f"{name} calls held back 2026-10-16 21:00-21:15 UTC: 1 from 1 IPs; all: {ADDRESS} 1"
        for name in ("Mouser", "DigiKey")]


async def test_minute_task_drops_previous_day_addresses(clients, clock, monkeypatch):
    _, pool, _ = clients("Mouser", limit=1)
    pool.address_daily.record(ADDRESS)
    clock.now = MIDNIGHT
    monkeypatch.setattr(server, "_distributor_quotas", {"mouser": pool})
    monkeypatch.setattr(server, "_exit_if_stuck", lambda count: count)
    calls = 0

    async def minute(seconds):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise asyncio.CancelledError

    monkeypatch.setattr(server.asyncio, "sleep", minute)
    with pytest.raises(asyncio.CancelledError):
        await server._every_minute()
    assert pool.address_daily._counts == {}


def test_config_default_minimum_and_disabled():
    from pcbparts_mcp import config
    from pcbparts_mcp.config import number_setting

    assert config.DISTRIBUTOR_DAILY_PER_ADDRESS == 1000  # the shipped default since 0.10.5 (200 before)
    for raw, expected in (("", 1000), ("0", 0), ("-1", 0), ("bad", 1000)):
        assert number_setting("DISTRIBUTOR_DAILY_PER_ADDRESS", 1000, 0,
                              environ={"DISTRIBUTOR_DAILY_PER_ADDRESS": raw}, warnings=[]) == expected


async def test_minute_task_drops_previous_day_addresses_without_any_quota_pool(clock, monkeypatch):
    """DigiKey without credentials and no Mouser key: the address day belongs to no pool."""
    from types import SimpleNamespace
    day = AddressDailyQuota(5, key=lambda ip: ip, clock=clock)
    day.record(ADDRESS)
    clock.now = MIDNIGHT
    monkeypatch.setattr(server, "_distributor_quotas", {})
    monkeypatch.setattr(server, "_digikey_client", SimpleNamespace(_address_daily=day, callers=None, held_back=None))
    monkeypatch.setattr(server, "_caller_tallies", lambda: [])
    monkeypatch.setattr(server, "_exit_if_stuck", lambda count: count)
    calls = 0

    async def minute(seconds):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise asyncio.CancelledError

    monkeypatch.setattr(server.asyncio, "sleep", minute)
    with pytest.raises(asyncio.CancelledError):
        await server._every_minute()
    assert day._counts == {}


# --- 0.10.6: who reaches the cap is always named ---

def _tally_lines(caplog):
    return [r.getMessage() for r in caplog.records if r.name == "pcbparts_mcp.cache"]


def test_held_back_lines_name_every_address(caplog):
    from pcbparts_mcp.cache import CallerTally
    now = [1_792_000_000.0]
    tally = CallerTally("DigiKey", lambda: now[0], top=None, what="calls held back")
    for index in range(8):
        for _ in range(index + 1):
            tally.record(f"192.0.2.{index}")
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
        tally.flush()
    (line,) = _tally_lines(caplog)
    assert "36 from 8 IPs; all: 192.0.2.7 8, " in line
    assert all(f"192.0.2.{index} {index + 1}" in line for index in range(8))


def test_a_long_held_back_list_continues_on_lines_that_fit_the_file_log(caplog):
    from pcbparts_mcp.cache import CallerTally
    from pcbparts_mcp.file_logging import MAX_MESSAGE_CHARS
    tally = CallerTally("Mouser", lambda: 1_792_000_000.0, top=None, what="calls held back")
    addresses = [f"2001:db8:{index:x}::/64" for index in range(400)]
    for address in addresses:
        tally.record(address)
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
        tally.flush()
    lines = _tally_lines(caplog)
    assert len(lines) > 1 and all(len(line) <= MAX_MESSAGE_CHARS for line in lines)
    assert "(continued, 2 of " in lines[1]
    named = [item for line in lines for item in line.split("; all: ", 1)[1].split(", ")]
    assert sorted(named) == sorted(f"{address} 1" for address in addresses)


def test_requests_sent_lines_keep_the_top_five(caplog):
    from pcbparts_mcp.cache import CallerTally
    tally = CallerTally("Mouser", lambda: 1_792_000_000.0)
    for index in range(8):
        tally.record(f"192.0.2.{index}")
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
        tally.flush()
    (line,) = _tally_lines(caplog)
    assert "8 from 8 IPs; top: " in line and line.count("192.0.2.") == 5


def test_reaching_the_cap_logs_the_address_once(caplog):
    from pcbparts_mcp.cache import AddressDailyQuota
    now = [1_792_000_000.0]  # 2026-10-14 17:46 UTC
    day = AddressDailyQuota(3, key=lambda ip: None if ip == "exempt" else ip, clock=lambda: now[0])
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
        day.record("192.0.2.1")
        day.record("192.0.2.1")
        assert not _tally_lines(caplog)
        day.record("192.0.2.1")
        day.record("192.0.2.1")
        for _ in range(5):
            day.record("exempt")
    (line,) = _tally_lines(caplog)
    assert line == "Mouser and DigiKey per-address limit: 192.0.2.1 reached its 3 lookups for 2026-10-14 at 17:46 UTC"
