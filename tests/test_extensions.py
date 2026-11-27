"""Optional provider routing and startup; in-memory answers and HTTP mock transports only."""

import asyncio
import importlib.util
import logging
import json
import sys
from types import SimpleNamespace

import httpx
import pytest
from fastmcp import Client

from pcbparts_mcp import call_log, extensions, server, stats
from pcbparts_mcp import client as client_module
from pcbparts_mcp.cache import CARRY_MIN, AddressDailyQuota, DailyQuota, Pacer, QuotaPool
from pcbparts_mcp.digikey import DigiKeyClient
from pcbparts_mcp.distributor_store import DistributorStore
from pcbparts_mcp.mouser import MouserClient
from pcbparts_mcp.lifecycle import Entry, LifecycleLookup
from digikey_ext import FakeExt
from test_digikey_two_apps import Clock, CREDS, DAILY_HEADERS, MIDNIGHT, FakeDigiKey, ok


def mouser_client(store, parts):
    def answer(request):
        numbers = json.loads(request.content)["SearchByPartRequest"]["mouserPartNumber"].split("|")
        sent.append(numbers)
        hits = [p for p in parts if p["ManufacturerPartNumber"] in numbers]
        return httpx.Response(200, json={"Errors": [], "SearchResults": {"NumberOfResult": len(hits), "Parts": hits}})

    sent: list[list[str]] = []
    client = MouserClient(api_key="k", quota=DailyQuota("Mouser", 1000, day_start_hour=6), store=store)
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(answer))
    return client, sent


CALLER = "203.0.113.7"


@pytest.fixture
async def hybrid():
    made = []

    def create(*responses, limit=1000, address_limit=10, apps=2, per_minute=100, ext=None):
        clock = Clock()
        day = AddressDailyQuota(address_limit, key=lambda ip: ip, clock=clock)
        pool = QuotaPool([DailyQuota("DigiKey", limit, clock=clock) for _ in range(apps)],
                         per_minute=per_minute, address_daily=day)
        store = DistributorStore(clock=clock)
        ext = ext or FakeExt()

        async def sleep(seconds):  # the pacer's and the transient retry's waits: the fake clock
            clock.advance(seconds)
            await asyncio.sleep(0)

        client = DigiKeyClient(*CREDS[:2], quota=pool, second_app=CREDS[2:] if apps == 2 else None,
                               ext=ext, store=store, sleep=sleep)
        api = FakeDigiKey(*responses)
        client._http = httpx.AsyncClient(transport=httpx.MockTransport(api))
        client._pacer = Pacer(5, clock=clock, sleep=sleep)
        result = SimpleNamespace(client=client, api=api, pool=pool, day=day, clock=clock,
                                 ext=ext, store=store)
        made.append(result)
        return result

    yield create
    for item in made:
        await item.client.close()
        item.store.close()


async def test_api_then_ext_then_api_at_utc_reset(hybrid, caplog):
    h = hybrid(ok(), ok(), ok(), limit=1)
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.digikey"):
        for number in ("PART-A", "PART-B"):
            assert (await h.client.lookup(number, CALLER)).kind == "found"
        assert not h.ext.lookups
        assert (await h.client.lookup("LM358DR", CALLER)).kind == "found"
        assert (await h.client.lookup("AD7747ARUZ", CALLER)).kind == "found"
        assert h.api.apps == [CREDS[0], CREDS[2]]
        assert h.day.remaining(CALLER) == 6
        assert h.client.unmetered and h.client.can_answer_now(CALLER)
        h.clock.now = MIDNIGHT
        assert not h.client.unmetered and not h.client.can_answer_now(CALLER)
        assert (await h.client.lookup("PART-C", CALLER)).kind == "found"
        assert h.api.apps == [CREDS[0], CREDS[2], CREDS[0]]
        assert h.day.remaining(CALLER) == 9
    moves = [r.message for r in caplog.records if r.message.startswith("DigiKey lookups moved")]
    assert moves == ["DigiKey lookups moved to ext (API day spent)", "DigiKey lookups moved to the API"]


@pytest.mark.parametrize("apps", [1, 2])
async def test_daily_refusal_continues_same_lookup_charged_once(hybrid, apps):
    h = hybrid(*(httpx.Response(429, headers=DAILY_HEADERS) for _ in range(apps)), apps=apps, address_limit=1)
    answer = await h.client.lookup("LM358DR", CALLER)
    assert answer.kind == "found" and answer.reply["results"][0]["requested"] == "LM358DR"
    assert h.day.remaining(CALLER) == 0
    assert len(h.api.requests) == apps and h.ext.lookups
    before = list(h.ext.lookups)
    assert (await h.client.lookup("lm358dr", CALLER)).kind == "found"  # stored answers stay free
    held = await h.client.lookup("AD7747ARUZ", CALLER)
    assert held.kind == "limited" and held.reply["error"].startswith("This address has used")
    assert h.ext.lookups == before
    assert not h.pool.held_back._counts  # the completed fallback wasn't held back by the API day
    assert h.client.held_back._counts[CALLER] == 1


async def test_transient_failure_on_the_api_days_last_request_continues_through_the_ext(hybrid):
    # The 503 used the API's last request of the day, so its retry can't go out: the lookup goes on
    # through ext, carrying its address charge (charged once in all)
    h = hybrid(httpx.Response(503), limit=1, apps=1, address_limit=1)
    answer = await h.client.lookup("LM358DR", CALLER)
    assert answer.kind == "found" and answer.reply["results"][0]["requested"] == "LM358DR"
    assert len(h.api.requests) == 1 and h.ext.lookups == ["LM358DR"]
    assert h.day.remaining(CALLER) == 0
    totals = stats.usage.summary()["totals"]["distributors"]["digikey"]
    assert totals["sent"] == 2 and totals["ext_sent"] == 1 and totals["rate_limited"] == 0
    assert "retries" not in totals  # the retry never went out


async def test_token_daily_refusal_falls_back_before_charging(hybrid):
    h = hybrid(address_limit=1)
    await h.client._http.aclose()
    requests = []

    def token_refusal(request):
        assert "oauth2/token" in str(request.url)
        requests.append(request)
        return httpx.Response(429, headers=DAILY_HEADERS)

    h.client._http = httpx.AsyncClient(transport=httpx.MockTransport(token_refusal))
    assert (await h.client.lookup("LM358DR", CALLER)).kind == "found"
    assert len(requests) == 2 and h.day.remaining(CALLER) == 0
    assert all(q.status()["used_today"] == 0 for q in h.pool.quotas)
    assert not h.pool.held_back._counts


async def test_final_success_is_used_before_next_lookup_falls_back(hybrid):
    h = hybrid(ok(DAILY_HEADERS), apps=1)
    assert (await h.client.lookup("PART-A", CALLER)).kind == "found"
    assert not h.ext.lookups
    assert (await h.client.lookup("LM358DR", CALLER)).kind == "found"
    assert len(h.api.requests) == 1 and h.day.remaining(CALLER) == 8


@pytest.mark.parametrize("cause", ["minute", "403", "minute_cap", "address"])
async def test_other_holds_do_not_spill(hybrid, cause):
    h = hybrid(address_limit=1, per_minute=1)
    if cause == "minute":
        h.pool.note_response(0, 429, {"retry-after": "60"})
    elif cause == "403":
        h.pool.note_response(0, 403, {})
    elif cause == "minute_cap":
        h.pool._minute.try_acquire()
    else:
        h.day.record(CALLER)
    answer = await h.client.lookup("LM358DR", CALLER)
    assert answer.kind == "limited"
    assert not h.api.requests and not h.ext.lookups and not h.client.unmetered
    assert not h.client.can_answer_now(CALLER)


@pytest.mark.parametrize("status", [403, 429])
async def test_shared_penalty_still_wins_when_all_daily_counts_are_spent(hybrid, status):
    h = hybrid(limit=1)
    for _ in range(2):
        h.pool.acquire()
    h.pool.note_response(0, status, {})
    assert (await h.client.lookup("LM358DR", CALLER)).kind == "limited"
    assert not h.ext.lookups and not h.client.unmetered
    assert h.day.remaining(CALLER) == 10


async def test_ext_pause_uses_ext_error_and_retry_while_api_day_is_spent(hybrid):
    h = hybrid(limit=0)
    h.ext.pause()
    answer = await h.client.lookup("LM358DR", CALLER)
    assert answer.kind == "limited" and answer.reply["error"].startswith("DigiKey lookups are paused")
    assert h.client.retry_after(CALLER) == h.ext.retry_after()
    assert not h.client.unmetered and not h.client.can_answer_now(CALLER)
    assert not h.api.tokens and not h.ext.lookups and h.day.remaining(CALLER) == 10


@pytest.mark.parametrize("paused", [False, True], ids=["busy", "paused"])
@pytest.mark.parametrize("credentials", [False, True], ids=["extension", "fallback"])
async def test_ext_wait_ends_at_api_reset(hybrid, monkeypatch, paused, credentials):
    h = hybrid(ok(), apps=1)
    h.clock.now = MIDNIGHT - 120
    h.pool.note_response(0, 429, DAILY_HEADERS)
    h.client._api_enabled = credentials
    h.ext.paused = paused
    h.ext.available = False
    monkeypatch.setattr(h.ext, "retry_after", lambda: 14400)
    wait = 120 if credentials else 14400
    answer = await h.client.lookup("LM358DR", CALLER)
    expected = extensions.ExtUnavailable(wait, paused=paused)
    from pcbparts_mcp.digikey import _ext_limited
    assert answer.reply == _ext_limited(expected)
    assert h.client.retry_after(CALLER) == wait
    if credentials:
        h.clock.now = MIDNIGHT
        assert (await h.client.lookup("LM358DR", CALLER)).kind == "found"
        assert not h.ext.lookups and len(h.api.requests) == 1


@pytest.mark.parametrize("paused", [False, True], ids=["available", "paused"])
async def test_daily_refusal_then_ext_counts_only_unsent_lookups_as_held(hybrid, paused):
    h = hybrid(httpx.Response(429, headers=DAILY_HEADERS), apps=1, address_limit=1)
    h.ext.paused = paused
    answer = await h.client.lookup("LM358DR", CALLER)
    assert answer.kind == ("limited" if paused else "found")
    totals = stats.usage.summary()["totals"]
    assert totals["parts_asked"]["digikey"]["total"] == 1
    assert totals["distributors"]["digikey"]["sent"] == (1 if paused else 2)
    assert totals["distributors"]["digikey"]["ext_sent"] == (0 if paused else 1)  # the API attempt is not
    assert totals["distributors"]["digikey"]["rate_limited"] == 0
    assert not any(totals["distributor_limits"]["digikey"]["held_back"].values())
    assert not h.pool.held_back._counts and not h.client.held_back._counts
    assert h.day.remaining(CALLER) == 0


async def test_ext_hourly_lines_are_distinct_from_api_lines(hybrid, monkeypatch, caplog):
    h = hybrid(apps=1)
    monkeypatch.setattr(server, "_distributor_quotas", {"digikey": h.pool})
    monkeypatch.setattr(server, "_digikey_client", h.client)
    with caplog.at_level(logging.INFO):
        for tally in server._caller_tallies():
            tally.record(CALLER)
            tally.flush()
    for label in ("DigiKey", "DigiKey ext"):
        for action in ("requests sent", "calls held back"):
            assert sum(message.startswith(f"{label} {action}") for message in caplog.messages) == 1


class CountingExt(FakeExt):
    """Counts one in-memory HTTP reply per lookup under the digikey_ext upstream source, through
    the same client helper an extension uses."""

    async def lookup(self, number, sent=None, charge=None):
        answer = await super().lookup(number, sent, charge)

        async def reply():
            return httpx.Response(200)

        await client_module._sent("digikey_ext", reply())
        return answer


async def test_ext_lookups_count_ext_sent_and_api_lookups_do_not(hybrid, monkeypatch):
    h = hybrid(ok(), ok(), ok(), limit=1, ext=CountingExt())
    usage = stats.UsageStats(clock=h.clock)
    monkeypatch.setattr(stats, "usage", usage)

    def day():
        return usage.summary()["days"][0]

    for number in ("PART-A", "PART-B"):  # one on each app; then the API's day is spent
        assert (await h.client.lookup(number, CALLER)).kind == "found"
    assert day()["distributors"]["digikey"] == {"sent": 2, "cached": 0, "rate_limited": 0, "ext_sent": 0}
    assert "digikey_ext" not in day()["upstream"]
    api_requests = day()["upstream"]["digikey"]["sent"]
    assert (await h.client.lookup("LM358DR", CALLER)).kind == "found"
    assert (await h.client.lookup("lm358dr", CALLER)).kind == "found"  # a stored answer: nothing sent
    assert h.ext.lookups == ["LM358DR"]
    assert day()["distributors"]["digikey"] == {"sent": 3, "cached": 1, "rate_limited": 0, "ext_sent": 1}
    assert day()["upstream"]["digikey_ext"] == {"sent": 1, "retries": 0, "cached": 0, "rate_limited": 0, "waited": 0}
    assert day()["upstream"]["digikey"]["sent"] == api_requests  # ext's requests stay apart
    assert day()["upstream_status"]["digikey_ext"] == {"2xx": 1}
    h.clock.now = MIDNIGHT  # the API is back: its lookups count in sent only
    assert (await h.client.lookup("PART-C", CALLER)).kind == "found"
    assert usage.summary()["days"][0]["distributors"]["digikey"] == {
        "sent": 1, "cached": 0, "rate_limited": 0, "ext_sent": 0}
    assert usage.summary()["totals"]["distributors"]["digikey"]["ext_sent"] == 1


async def test_ext_batch_counts_ext_sent_per_number_sent(context, monkeypatch):
    usage = stats.UsageStats(clock=lambda: MIDNIGHT)
    monkeypatch.setattr(stats, "usage", usage)
    ext = FakeExt()
    client = DigiKeyClient("", "", ext=ext, store=context.store, address_daily=context.address_daily)
    try:
        answers = await client.lifecycle(["PART-A", "PART-B"], CALLER)
        assert [answers[n].kind for n in ("PART-A", "PART-B")] == ["found", "limited"]
        # PART-B was refused by the address's day before its first request: neither sent nor ext_sent
        assert usage.summary()["days"][0]["distributors"]["digikey"] == {
            "sent": 1, "cached": 0, "rate_limited": 1, "ext_sent": 1}
    finally:
        await client.close()


async def test_shutdown_saves_before_ext_close_starts(monkeypatch, tmp_path):
    closing, release = asyncio.Event(), asyncio.Event()
    events = []

    class BlockingExt(FakeExt):
        async def close(self):
            events.append("ext close")
            closing.set()
            await release.wait()
            await super().close()

    ext = BlockingExt()
    monkeypatch.setattr(server, "load_digikey_ext", lambda context: ext)
    monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", str(tmp_path / "quota.json"))
    monkeypatch.setattr(server, "USAGE_STATS_PATH", str(tmp_path / "usage.json"))
    monkeypatch.setattr(server, "CALL_LOG_DIR", str(tmp_path / "calls"))
    save_address = server._save_address_counts
    save_stats = stats.usage.save_async
    flush_log = call_log.recorder.flush

    def save_counts():
        save_address()
        events.append("address saved")

    async def save():
        await save_stats()
        events.append("stats saved")

    async def flush(*, shutdown=False):
        await flush_log(shutdown=shutdown)
        if shutdown:
            events.append("call log flushed")

    monkeypatch.setattr(server, "_save_address_counts", save_counts)
    monkeypatch.setattr(stats.usage, "save_async", save)
    monkeypatch.setattr(call_log.recorder, "flush", flush)
    cm = server.lifespan(None)
    await cm.__aenter__()
    client = server._digikey_client
    assert (await client.lookup("LM358DR", CALLER)).kind == "found"
    for _ in range(CARRY_MIN - 1):
        server._address_daily.record(CALLER)
    for tally in server._caller_tallies():
        original = tally.flush

        def flush_tally(original=original):
            original()
            events.append("tally flushed")

        monkeypatch.setattr(tally, "flush", flush_tally)
    # Cancellation must still finish before the last stats save.
    pending = asyncio.Event()

    async def in_flight():
        try:
            pending.set()
            await asyncio.Event().wait()
        finally:
            events.append("lookup stopped")

    task = asyncio.create_task(in_flight())
    client._tasks.add(task)
    await pending.wait()
    shutdown = asyncio.create_task(cm.__aexit__(None, None, None))
    try:
        await asyncio.wait_for(closing.wait(), 10)
        assert events.index("lookup stopped") < events.index("stats saved")
        assert all(events.index(name) < events.index("ext close") for name in (
            "address saved", "tally flushed", "stats saved", "call log flushed"))
        assert (tmp_path / "distributor_address_counts.json").is_file()
        assert (tmp_path / "usage.json").is_file()
        assert not shutdown.done()
    finally:
        release.set()
        await shutdown


@pytest.mark.parametrize("route", ["api", "ext", "paused", "metered", "unavailable"])
async def test_lifecycle_order_and_miss_hint_follow_active_path(hybrid, monkeypatch, route):
    h = hybrid(limit=0 if route != "api" else 1000)
    ext_sent = h.ext.batches
    if route == "paused":
        h.ext.pause()
    elif route == "metered":
        h.ext.unmetered = False
    elif route == "unavailable":
        h.ext.available = False
    part = {"MouserPartNumber": "595-LM358DR", "ManufacturerPartNumber": "LM358DR",
            "Manufacturer": "Texas Instruments", "Description": "", "Category": "",
            "AvailabilityInStock": "5", "Min": "1", "PriceBreaks": [], "ProductAttributes": []}
    mouser, sent = mouser_client(h.store, [part])
    monkeypatch.setattr(server, "_digikey_client", h.client)
    monkeypatch.setattr(server, "_caller_ip", lambda: CALLER)
    assert bool(server._other_distributors_clause()) is (route == "ext")
    try:
        (answer,) = await LifecycleLookup(h.store, mouser, h.client).answer([Entry("LM358DR", mpn="LM358DR")])
        assert answer["source"] == ("digikey" if route == "ext" else "mouser")
        assert bool(sent) is (route != "ext")
        assert bool(ext_sent) is (route == "ext")
    finally:
        await mouser.close()


async def test_not_found_cache_is_shared_across_routes(hybrid):
    h = hybrid(httpx.Response(200, json={"Products": [], "ExactMatches": []}), limit=1, apps=1)
    miss = await h.client.lookup("NOT-A-PART", CALLER)
    assert miss.kind == "not_found" and h.client.unmetered
    assert (await h.client.lookup("not-a-part", CALLER)).kind == "not_found"
    assert not h.ext.lookups and h.day.remaining(CALLER) == 9
    # An ext miss must survive the next API day too.
    ext_miss = await h.client.lookup("TP4056", CALLER)
    assert ext_miss.kind == "not_found"
    h.clock.now = MIDNIGHT
    assert (await h.client.lookup("TP4056", CALLER)).kind == "not_found"
    assert len(h.api.requests) == 1


async def test_server_wires_both_paths_and_preserves_private_api_status(monkeypatch):
    ext = FakeExt()
    monkeypatch.setattr(server, "load_digikey_ext", lambda context: ext)
    monkeypatch.setattr(server, "MOUSER_API_KEY", "test-key")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "test-id")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(server, "DISTRIBUTOR_DAILY_LIMIT", 1)
    monkeypatch.setattr(server, "_digikey_client", None)
    async with Client(server.mcp):
        client = server._digikey_client
        pool = server._distributor_quotas["digikey"]
        assert client._ext is not None and client._ext.started
        assert client._address_daily is pool.address_daily is server._address_daily
        assert server._mouser_client._quota.address_daily is client._address_daily
        assert not client.unmetered
        pool.acquire()
        assert client.unmetered and client.ext_status() is None
        assert server._distributor_quota_status()["digikey"] == pool.status()
        assert client.callers in server._caller_tallies() and pool.callers in server._caller_tallies()
    assert ext.closed


@pytest.fixture
def context():
    clock = Clock()
    store = DistributorStore(clock=clock)
    day = AddressDailyQuota(1, key=lambda ip: ip, clock=clock)
    yield extensions.ExtensionContext(day, store, "")
    store.close()


def test_public_environment_has_no_extension():
    assert importlib.util.find_spec("pcbparts_extensions") is None


def test_loader_absent_module(context, monkeypatch, caplog):
    monkeypatch.setitem(sys.modules, "pcbparts_extensions", None)
    with caplog.at_level(logging.INFO, logger=extensions.__name__):
        assert extensions.load_digikey_ext(context) is None
    assert not [r for r in caplog.records if r.name == extensions.__name__]


def test_loader_ignores_module_without_provider(context, monkeypatch, caplog):
    monkeypatch.setitem(sys.modules, "pcbparts_extensions", SimpleNamespace())
    with caplog.at_level(logging.INFO, logger=extensions.__name__):
        assert extensions.load_digikey_ext(context) is None
    assert [r.message for r in caplog.records if r.name == extensions.__name__] == [
        "Optional deployment extension has no DigiKey provider"]


@pytest.mark.parametrize("enabled", [False, True], ids=["disabled", "enabled"])
def test_loader_discovers_factory_and_passes_context(context, monkeypatch, tmp_path, caplog, enabled):
    monkeypatch.delitem(sys.modules, "pcbparts_extensions", raising=False)
    monkeypatch.syspath_prepend(str(tmp_path))
    (tmp_path / "pcbparts_extensions.py").write_text(
        "from digikey_ext import FakeExt\n"
        "seen = None\n"
        "def digikey_ext(context):\n"
        "    global seen\n"
        "    seen = context\n"
        f"    return {'FakeExt()' if enabled else 'None'}\n", encoding="utf-8")
    try:
        with caplog.at_level(logging.INFO, logger=extensions.__name__):
            result = extensions.load_digikey_ext(context)
        assert sys.modules["pcbparts_extensions"].seen is context
        assert isinstance(result, FakeExt) if enabled else result is None
        lines = [r.message for r in caplog.records if r.name == extensions.__name__]
        assert lines == (["Optional deployment extension loaded"] if enabled else [])
    finally:
        sys.modules.pop("pcbparts_extensions", None)


BROKEN_EXTENSIONS = {
    "dependency": ("import missing_extension_dependency\n", "ModuleNotFoundError"),
    "import": ("from os import no_such_name_in_os  # /private/path/detail\n", "ImportError"),
    "module": ("raise RuntimeError('/private/path/detail')\n", "RuntimeError"),
    "factory": ("def digikey_ext(context):\n    raise RuntimeError('/private/path/detail')\n", "RuntimeError"),
}


def write_extension(monkeypatch, tmp_path, body):
    monkeypatch.delitem(sys.modules, "pcbparts_extensions", raising=False)
    monkeypatch.syspath_prepend(str(tmp_path))
    (tmp_path / "pcbparts_extensions.py").write_text(body, encoding="utf-8")


@pytest.mark.parametrize("kind", BROKEN_EXTENSIONS)
def test_loader_contains_broken_extensions(context, monkeypatch, tmp_path, caplog, kind):
    body, error = BROKEN_EXTENSIONS[kind]
    write_extension(monkeypatch, tmp_path, body)
    try:
        with caplog.at_level(logging.INFO, logger=extensions.__name__):
            assert extensions.load_digikey_ext(context) is None
        records = [r for r in caplog.records if r.name == extensions.__name__]
        assert [(r.levelname, r.getMessage()) for r in records] == [
            ("ERROR", f"Optional deployment extension failed to load ({error}); continuing without it")]
        assert "private" not in caplog.text and records[0].exc_info is None  # its type only, no message
    finally:
        sys.modules.pop("pcbparts_extensions", None)


@pytest.mark.parametrize("kind", ["import", "factory", "start"])
async def test_server_starts_api_only_with_a_broken_extension(monkeypatch, tmp_path, caplog, kind):
    if kind == "start":
        class Broken(FakeExt):
            async def start(self):
                raise RuntimeError("/private/path/detail")

        broken = Broken()
        monkeypatch.setitem(sys.modules, "pcbparts_extensions", SimpleNamespace(digikey_ext=lambda context: broken))
    else:
        write_extension(monkeypatch, tmp_path, BROKEN_EXTENSIONS[kind][0])
    monkeypatch.setattr(server, "_digikey_client", None)
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "id")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "secret")
    try:
        with caplog.at_level(logging.ERROR, logger=extensions.__name__):
            async with Client(server.mcp):
                client = server._digikey_client
                assert client is not None and client._ext is None and not client.unmetered
                api = FakeDigiKey(ok())
                client._http = httpx.AsyncClient(transport=httpx.MockTransport(api))
                assert (await client.lookup("PART-A", CALLER)).kind == "found"
                assert len(api.requests) == 1
        assert any("Optional deployment extension failed to load" in r.getMessage() for r in caplog.records)
        assert "private" not in caplog.text
        if kind == "start":
            assert broken.closed  # what it had opened is closed again
    finally:
        sys.modules.pop("pcbparts_extensions", None)


@pytest.mark.parametrize("credentials", [False, True], ids=["off", "api"])
async def test_server_without_extension(monkeypatch, credentials):
    monkeypatch.setitem(sys.modules, "pcbparts_extensions", None)
    monkeypatch.setattr(server, "_digikey_client", None)
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "id" if credentials else "")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "secret" if credentials else "")
    monkeypatch.setattr(server, "DISTRIBUTOR_DAILY_LIMIT", 1)
    async with Client(server.mcp):
        if not credentials:
            assert server._digikey_client is None
            assert await server.digikey_get_part(part_number="LM358DR") == {
                "error": "DigiKey API credentials not configured. Set DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET in environment."}
            assert "digikey" not in server._distributor_quota_status()
        else:
            client = server._digikey_client
            assert client._ext is None
            api = FakeDigiKey(ok())
            client._http = httpx.AsyncClient(transport=httpx.MockTransport(api))
            assert (await client.lookup("PART-A")).kind == "found"
            assert (await client.lookup("PART-B")).kind == "limited"
            assert len(api.requests) == 1 and not client.unmetered


async def test_server_extension_provider(monkeypatch):
    ext = FakeExt()
    contexts = []

    def factory(context):
        contexts.append(context)
        return ext

    monkeypatch.setitem(sys.modules, "pcbparts_extensions", SimpleNamespace(digikey_ext=factory))
    monkeypatch.setattr(server, "_digikey_client", None)
    async with Client(server.mcp):
        client = server._digikey_client
        assert client._ext is ext and ext.started and client.unmetered
        assert contexts[0].store is server._distributor_store
        assert contexts[0].address_daily is client._address_daily is server._address_daily
        assert contexts[0].store_path == server.DISTRIBUTOR_STORE_PATH
        assert (await client.lookup("LM358DR", CALLER)).kind == "found"
        assert client._http is None and ext.lookups == ["LM358DR"]
        assert set(server._distributor_quota_status()["digikey"]) == {"paused_until", "resets_at"}
    assert ext.closed


async def test_ext_batch_respects_address_allowance(context):
    ext = FakeExt()
    client = DigiKeyClient("", "", ext=ext, store=context.store, address_daily=context.address_daily)
    try:
        answers = await client.lifecycle(["PART-A", "PART-B"], CALLER)
        assert answers["PART-A"].kind == "found"
        assert answers["PART-B"].kind == "limited"
        assert context.address_daily.remaining(CALLER) == 0
        assert not client.can_answer_now(CALLER)
    finally:
        await client.close()


@pytest.mark.parametrize("mode", ["pause", "busy"])
async def test_lifecycle_ext_wait_ends_at_api_reset(mode):
    import datetime
    now = datetime.datetime(2026, 11, 25, 23, 58, tzinfo=datetime.timezone.utc).timestamp()
    store = DistributorStore(clock=lambda: now)
    pool = QuotaPool([DailyQuota("DigiKey", 1, clock=lambda: now)])
    pool.acquire()  # the API's day is spent; it resets in 120 s

    class Ext(FakeExt):
        def retry_after(self):
            return 14400

        async def statuses(self, numbers, sent=None, charge=None, held=None):
            self.paused = mode == "pause"
            error = extensions.ExtUnavailable(14400, paused=self.paused)
            if self.paused:
                raise error
            held(numbers[0], error)
            return {numbers[0]: error}

    client = DigiKeyClient("id", "secret", quota=pool, ext=Ext(), store=store)
    try:
        answer = await LifecycleLookup(store, None, client).answer([Entry("LM358DR", mpn="LM358DR")])
        assert answer[0]["retry_after"] == 120 == client.retry_after()
    finally:
        await client.close()
        store.close()


async def test_api_retry_held_after_a_send_is_not_also_held_back(monkeypatch):
    # An expired-token 401 sends the lookup's first request; our per-minute cap then holds its
    # retry. The lookup was sent, so it counts once as sent and never as held back.
    from test_digikey_two_apps import Clock
    monkeypatch.setattr(stats, "usage", stats.UsageStats())
    clock = Clock()
    day = AddressDailyQuota(50, key=lambda ip: ip, clock=clock)
    pool = QuotaPool([DailyQuota("DigiKey", 1000, clock=clock)], per_minute=1, address_daily=day)
    client = DigiKeyClient(*CREDS[:2], quota=pool, store=DistributorStore(clock=clock))

    def handler(request):
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "t", "expires_in": 599})
        return httpx.Response(401)

    client._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def sleep(seconds):
        clock.advance(seconds)
        await asyncio.sleep(0)

    client._pacer = Pacer(5, clock=clock, sleep=sleep)
    try:
        answer = await client.lookup("LM358DR", "203.0.113.7")
        totals = stats.usage.summary()["totals"]
        assert answer.kind == "limited"
        assert totals["distributors"]["digikey"]["sent"] == 1
        assert totals["distributors"]["digikey"]["ext_sent"] == 0
        assert totals["distributors"]["digikey"]["rate_limited"] == 0
        held = (totals["distributor_limits"].get("digikey") or {}).get("held_back", {})
        assert not any(held.values())
        assert day._counts.get("203.0.113.7") == 1
    finally:
        await client.close()
