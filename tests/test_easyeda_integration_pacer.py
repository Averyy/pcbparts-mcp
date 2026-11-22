"""Exercise the integration-only patches with real wafer sessions over a fake transport."""

import asyncio
import json
from types import SimpleNamespace

import pytest
import wafer
import wafer._async as wafer_async
import wreq

from easyeda_integration import BLOCKED, EasyEDAIntegrationPacer
from pcbparts_mcp.client import JLCPCBClient
from test_easyeda_critical_ch import _Reply

PRODUCT = "https://easyeda.com/api/products/{}/components"
FOUND = {"success": True, "result": {"uuid": "a" * 32, "packageDetail": {"uuid": "b" * 32}}}


class Clock:
    def __init__(self):
        self.now = 1000.0
        self.waits = []

    def __call__(self):
        return self.now

    async def sleep(self, seconds):
        self.waits.append(seconds)
        self.now += seconds
        await asyncio.sleep(0)


def reply(status=200, payload=FOUND, **headers):
    return _Reply(status, {"content-type": "application/json", **headers}, json.dumps(payload))


@pytest.fixture
async def paced(monkeypatch):
    clock = Clock()
    env = SimpleNamespace(clock=clock, sent=[], respond=lambda url: reply(), clients=[])

    async def transport(client, method, url, **kwargs):
        env.sent.append((clock(), str(url)))
        await asyncio.sleep(0)  # force contention without real waiting
        return env.respond(str(url))

    original_init = wafer.AsyncSession.__init__

    def no_network_pacing(session, **kwargs):
        original_init(session, **{**kwargs, "rate_limit": 0.0, "max_retries": 0, "max_rotations": 0})

    monkeypatch.setattr(wafer.AsyncSession, "__init__", no_network_pacing)
    monkeypatch.setattr(wreq.Client, "request", transport)
    # Advancing the injected clock also exercises wafer's total timeout: the 75s wait
    # must happen before that timeout starts, not turn successful checks into unknowns.
    monkeypatch.setattr(wafer_async, "time", SimpleNamespace(monotonic=clock))
    env.pacer = EasyEDAIntegrationPacer(clock, clock.sleep)
    env.pacer.install(monkeypatch)

    def client():
        result = JLCPCBClient()
        env.clients.append(result)
        return result

    env.client = client
    yield env
    for client in env.clients:
        await client.close()


async def test_all_clients_wait_for_one_rolling_budget(paced):
    clients = [paced.client() for _ in range(3)]
    answers = await asyncio.gather(*[
        clients[i % 3]._check_easyeda_footprint(f"C{i + 1}") for i in range(16)
    ])
    assert all(answer["has_easyeda_footprint"] is True and status == "checked" for answer, status in answers)
    times = [at for at, _ in paced.sent]
    assert times == [1000.0] * 4 + [1075.0] * 4 + [1150.0] * 4 + [1225.0] * 4
    assert all(sum(at <= other < at + 75 for other in times) <= 4 for at in times)
    assert paced.clock.waits == [75.0] * 3
    assert all(client._easyeda_products_budget is paced.pacer.client_budget for client in clients)


async def test_cache_hits_and_invalid_codes_spend_no_slots(paced):
    first, second = paced.client(), paced.client()
    assert (await first.check_easyeda_footprint("C1"))["has_easyeda_footprint"] is True
    paced.respond = lambda url: reply(404)
    assert (await first.check_easyeda_footprint("C2"))["has_easyeda_footprint"] is False
    assert (await second._check_easyeda_footprint(" c1 "))[1] == "cached"
    assert (await second._check_easyeda_footprint("C2"))[1] == "cached"
    assert (await second._check_easyeda_footprint("INVALID"))[1] == "invalid"
    assert len(paced.sent) == 2
    assert paced.pacer.budget.used == 2
    assert paced.clock.waits == []


async def test_products_403_stops_before_critical_ch_resend_and_skips_later_calls(paced):
    first, second = paced.client(), paced.client()
    await first.check_easyeda_footprint("C1")  # even cached answers must skip after the block
    paced.respond = lambda url: reply(403, **{
        "accept-ch": "Sec-CH-UA-Full-Version-List", "critical-ch": "Sec-CH-UA-Full-Version-List"})
    with pytest.raises(pytest.skip.Exception, match=BLOCKED):
        await first.check_easyeda_footprint("C2")
    assert len(paced.sent) == 2  # one success and exactly one 403, no hidden resend
    paced.clock.now += 3600  # a session stop never expires like the production cooldown
    for call, arg in ((second.check_easyeda_footprint, "C1"), (second.get_part, "C3"),
                      (second.get_easyeda_component, "a" * 32), (second.footprint_pads, "b" * 32)):
        with pytest.raises(pytest.skip.Exception, match=BLOCKED):
            await call(arg)
    assert len(paced.sent) == 2
    assert paced.clock.waits == []


async def test_queued_checks_do_not_send_after_first_403(paced):
    clients = [paced.client() for _ in range(3)]
    paced.respond = lambda url: reply(403)
    results = await asyncio.gather(*[
        clients[i % 3].check_easyeda_footprint(f"C{i + 1}") for i in range(9)
    ], return_exceptions=True)
    assert all(isinstance(result, pytest.skip.Exception) for result in results)
    assert len(paced.sent) == 1


async def test_components_403_also_stops_products_but_other_hosts_continue(paced):
    client = paced.client()
    paced.respond = lambda url: reply(403)
    with pytest.raises(pytest.skip.Exception, match=BLOCKED):
        await client.get_easyeda_component("a" * 32)
    with pytest.raises(pytest.skip.Exception, match=BLOCKED):
        await paced.client().check_easyeda_footprint("C1")
    # Unrelated integration tests are unaffected. This also uses the fake transport.
    response = await wafer.AsyncSession().get("https://example.test/api/products/C1/components")
    assert response.status_code == 403
    assert len(paced.sent) == 2
    assert paced.pacer.budget.used == 0


@pytest.mark.parametrize("prefill", [0, 3])
async def test_successful_critical_ch_resend_counts_as_another_send(paced, prefill):
    client = paced.client()
    for i in range(prefill):
        await client.check_easyeda_footprint(f"C{i + 10}")
    paced.respond = lambda url: reply(**{
        "accept-ch": "Sec-CH-UA-Full-Version-List", "critical-ch": "Sec-CH-UA-Full-Version-List"})
    assert (await paced.client().check_easyeda_footprint("C1"))["has_easyeda_footprint"] is True
    assert len(paced.sent) == prefill + 2
    assert paced.clock.waits == ([75.0] if prefill else [])
    assert paced.pacer.budget.used == (1 if prefill else 2)


async def test_staggered_requests_use_a_rolling_window_and_count_transport_failures():
    clock = Clock()
    pacer = EasyEDAIntegrationPacer(clock, clock.sleep)
    sent = []

    async def send(method, url):
        sent.append(clock())
        raise RuntimeError("connection failed")

    for offset in (0, 10, 20, 30, 40, 80):
        clock.now = 1000 + offset
        with pytest.raises(RuntimeError, match="connection failed"):
            await pacer.send(send, "GET", PRODUCT.format("C1"))
    assert sent == [1000, 1010, 1020, 1030, 1075, 1085]
    assert clock.waits == [35, 5]


def test_budget_and_stop_flag_survive_new_event_loops():
    clock = Clock()
    pacer = EasyEDAIntegrationPacer(clock, clock.sleep)
    sent = []

    async def send(method, url):
        sent.append(clock())
        await asyncio.sleep(0)
        return reply(403 if len(sent) == 6 else 200)

    async def batch(count):
        return await asyncio.gather(*[
            pacer.send(send, "GET", PRODUCT.format(f"C{i}")) for i in range(count)
        ], return_exceptions=True)

    asyncio.run(batch(4))
    results = asyncio.run(batch(2))
    assert isinstance(results[-1], pytest.skip.Exception)
    assert sent == [1000] * 4 + [1075] * 2
    assert isinstance(asyncio.run(batch(1))[0], pytest.skip.Exception)
    assert len(sent) == 6


def test_unit_fixture_does_not_install_pacing(monkeypatch):
    from conftest import _pace_easyeda_integration

    def unexpected_fixture(name):
        pytest.fail(f"unit tests must not create {name}")

    request = SimpleNamespace(node=SimpleNamespace(get_closest_marker=lambda name: None),
                              getfixturevalue=unexpected_fixture)
    original = wafer.AsyncSession.request
    _pace_easyeda_integration.__wrapped__(request, monkeypatch)
    assert wafer.AsyncSession.request is original


def test_integration_fixture_reuses_session_pacer_and_rejects_xdist(monkeypatch):
    from conftest import _pace_easyeda_integration, easyeda_integration_pacer

    request = SimpleNamespace(config=SimpleNamespace())
    pacer = easyeda_integration_pacer.__wrapped__(request)
    installed = []
    monkeypatch.setattr(pacer, "install", lambda patch: installed.append(pacer))
    request.node = SimpleNamespace(get_closest_marker=lambda name: True)
    request.getfixturevalue = lambda name: pacer
    _pace_easyeda_integration.__wrapped__(request, monkeypatch)
    _pace_easyeda_integration.__wrapped__(request, monkeypatch)
    assert installed == [pacer, pacer]
    request.config.workerinput = {}
    with pytest.raises(pytest.fail.Exception, match="one process"):
        easyeda_integration_pacer.__wrapped__(request)
