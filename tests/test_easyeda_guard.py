"""EasyEDA /api/products guard (0.5.6): request budget, cooldown, footprint cache TTLs, statuses,
session config, and the find_alternatives footprint-filter note. See docs/ref-easyeda-api.md.

Everything runs on fake clocks and a fake session that counts requests; no network.
"""

import asyncio
import datetime
import logging
import types

import pytest

from pcbparts_mcp import client as client_module
from pcbparts_mcp.cache import Cooldown, SlidingWindowBudget
from pcbparts_mcp.client import JLCPCBClient
from pcbparts_mcp.config import (
    EASYEDA_ATTEMPT_TIMEOUT,
    EASYEDA_CACHE_TTL,
    EASYEDA_COOLDOWN_BASE,
    EASYEDA_COOLDOWN_MAX,
    EASYEDA_ERROR_CACHE_TTL,
    EASYEDA_FOOTPRINT_CACHE_TTL,
    EASYEDA_MAX_FOOTPRINT_CHECKS,
    EASYEDA_PRODUCTS_BUDGET,
    EASYEDA_PRODUCTS_WINDOW,
    EASYEDA_REQUEST_TIMEOUT,
)

FOUND = {"success": True, "result": {"uuid": "a" * 32, "packageDetail": {"uuid": "b" * 32}}}
UNKNOWN = {"has_easyeda_footprint": None, "easyeda_symbol_uuid": None, "easyeda_footprint_uuid": None}


class FakeClock:
    def __init__(self, start: float = 1_000_000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None, challenge_type: str | None = None):
        self.status_code = status_code
        self._payload = payload
        self.challenge_type = challenge_type

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict | None:
        return self._payload


class FakeSession:
    """Counts requests. respond(url) returns a FakeResponse or an exception to raise; delay(url)
    is how many event-loop turns the request takes, to control which concurrent request finishes first."""

    def __init__(self, respond, delay=lambda url: 1):
        self.respond = respond
        self.delay = delay
        self.urls: list[str] = []

    async def get(self, url: str):
        self.urls.append(url)
        for _ in range(self.delay(url)):
            await asyncio.sleep(0)
        result = self.respond(url)
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture
def clock(monkeypatch):
    """One fake clock for the guards (monotonic) and the client's caches (time.time)."""
    fake = FakeClock()
    monkeypatch.setattr(client_module, "time", types.SimpleNamespace(time=fake))
    return fake


def make_client(clock: FakeClock, respond, delay=lambda url: 1) -> tuple[JLCPCBClient, FakeSession]:
    client = JLCPCBClient()
    client._easyeda_products_budget = SlidingWindowBudget(EASYEDA_PRODUCTS_BUDGET, EASYEDA_PRODUCTS_WINDOW, clock)
    client._easyeda_products_cooldown = Cooldown(EASYEDA_COOLDOWN_BASE, EASYEDA_COOLDOWN_MAX, clock)
    session = FakeSession(respond, delay)
    client._easyeda_products_session = session
    return client, session


def lcsc_of(url: str) -> str:
    return url.split("/api/products/")[1].split("/")[0]


# --- SlidingWindowBudget ---------------------------------------------------------


class TestSlidingWindowBudget:
    def test_allows_limit_then_refuses(self):
        clock = FakeClock()
        budget = SlidingWindowBudget(3, 120.0, clock)
        assert [budget.try_acquire() for _ in range(4)] == [True, True, True, False]
        assert budget.used == 3  # the refusal recorded nothing

    def test_window_rolls(self):
        clock = FakeClock()
        budget = SlidingWindowBudget(2, 120.0, clock)
        assert budget.try_acquire()  # t=0
        clock.advance(60)
        assert budget.try_acquire()  # t=60
        assert not budget.try_acquire()
        clock.advance(59.9)  # t=119.9: both still inside the window
        assert not budget.try_acquire()
        clock.advance(0.1)  # t=120: the t=0 request ages out, t=60 doesn't
        assert budget.try_acquire()
        assert not budget.try_acquire()

    def test_refusals_dont_push_recovery_back(self):
        clock = FakeClock()
        budget = SlidingWindowBudget(1, 120.0, clock)
        assert budget.try_acquire()
        for _ in range(50):
            clock.advance(2)
            assert not budget.try_acquire()
        clock.advance(20)  # 120s after the only recorded request
        assert budget.try_acquire()

    def test_report_due_once_per_window(self):
        clock = FakeClock()
        budget = SlidingWindowBudget(1, 120.0, clock)
        assert budget.report_due()
        clock.advance(119.9)
        assert not budget.report_due()
        clock.advance(0.1)
        assert budget.report_due()
        assert not budget.report_due()


# --- Cooldown --------------------------------------------------------------------


class TestCooldown:
    def test_doubles_per_repeat_block_and_caps(self):
        clock = FakeClock()
        cooldown = Cooldown(120.0, 1800.0, clock)
        durations = []
        for _ in range(6):
            durations.append(cooldown.trip())
            clock.advance(durations[-1])
            assert not cooldown.active
        assert durations == [120, 240, 480, 960, 1800, 1800]

    def test_block_during_running_pause_doesnt_escalate(self):
        clock = FakeClock()
        cooldown = Cooldown(120.0, 1800.0, clock)
        assert cooldown.trip() == 120
        clock.advance(30)
        assert cooldown.trip() == 90  # same pause, nothing added
        clock.advance(90)
        assert cooldown.trip() == 240  # a later block is the second strike

    def test_stale_success_during_pause_keeps_the_strike(self):
        clock = FakeClock()
        cooldown = Cooldown(120.0, 1800.0, clock)
        cooldown.trip()
        cooldown.record_success()  # a request from before the block came back 200
        assert cooldown.active and cooldown.remaining == 120
        clock.advance(120)
        assert cooldown.trip() == 240  # the next block still escalates

    def test_success_after_pause_clears_strikes(self):
        clock = FakeClock()
        cooldown = Cooldown(120.0, 1800.0, clock)
        cooldown.trip()
        clock.advance(120)
        cooldown.record_success()
        assert cooldown.trip() == 120

    def test_remaining_and_active(self):
        clock = FakeClock()
        cooldown = Cooldown(120.0, 1800.0, clock)
        assert not cooldown.active and cooldown.remaining == 0
        cooldown.trip()
        clock.advance(100)
        assert cooldown.active and cooldown.remaining == pytest.approx(20)


# --- check_easyeda_footprint: statuses and shape --------------------------------


class TestFootprintCheckStatuses:
    async def test_found(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        result, status = await client._check_easyeda_footprint("c1525")
        assert status == "checked"
        assert result == {"has_easyeda_footprint": True, "easyeda_symbol_uuid": "a" * 32, "easyeda_footprint_uuid": "b" * 32}
        assert lcsc_of(session.urls[0]) == "C1525"
        assert await client._check_easyeda_footprint("C1525") == (result, "cached")
        assert len(session.urls) == 1

    @pytest.mark.parametrize("response", [FakeResponse(404), FakeResponse(200, {"success": False})])
    async def test_not_found(self, clock, response):
        client, _ = make_client(clock, lambda url: response)
        result, status = await client._check_easyeda_footprint("C1")
        assert status == "checked"
        assert result["has_easyeda_footprint"] is False

    async def test_invalid_code_sends_nothing(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        for bad in ["", "123", "INVALID", "C12a"]:
            assert await client._check_easyeda_footprint(bad) == (UNKNOWN, "invalid")
        assert session.urls == []

    @pytest.mark.parametrize("failure", [RuntimeError("timed out"), FakeResponse(500)])
    async def test_error_is_cached_and_doesnt_start_a_cooldown(self, clock, failure):
        client, session = make_client(clock, lambda url: failure)
        assert await client._check_easyeda_footprint("C1") == (UNKNOWN, "error")
        assert await client._check_easyeda_footprint("C1") == (UNKNOWN, "error")  # from the error cache
        assert len(session.urls) == 1
        assert not client._easyeda_products_cooldown.active
        await client._check_easyeda_footprint("C2")  # other parts still get checked
        assert len(session.urls) == 2

    @pytest.mark.parametrize("status_code", [403, 429])
    async def test_block_starts_cooldown_and_isnt_cached(self, clock, status_code):
        client, session = make_client(clock, lambda url: FakeResponse(status_code))
        assert await client._check_easyeda_footprint("C1") == (UNKNOWN, "blocked")
        assert client._easyeda_products_cooldown.remaining == EASYEDA_COOLDOWN_BASE
        assert "C1" not in client._easyeda_cache  # the cooldown covers it; no 5-min per-part error
        assert await client._check_easyeda_footprint("C2") == (UNKNOWN, "cooldown")
        assert len(session.urls) == 1

    async def test_budget_skip(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        for n in range(EASYEDA_PRODUCTS_BUDGET):
            await client._check_easyeda_footprint(f"C{n + 1}")
        assert await client._check_easyeda_footprint("C999") == (UNKNOWN, "budget")
        assert "C999" not in client._easyeda_cache
        assert len(session.urls) == EASYEDA_PRODUCTS_BUDGET
        clock.advance(EASYEDA_PRODUCTS_WINDOW)
        assert (await client._check_easyeda_footprint("C999"))[1] == "checked"

    async def test_budget_skips_warn_once_per_window(self, clock, caplog):
        client, _ = make_client(clock, lambda url: FakeResponse(200, FOUND))

        def budget_warnings() -> int:
            return sum(1 for r in caplog.records if r.levelno == logging.WARNING and "budget spent" in r.message)

        with caplog.at_level(logging.WARNING, logger="pcbparts_mcp.client"):
            for n in range(EASYEDA_PRODUCTS_BUDGET):
                await client._check_easyeda_footprint(f"C{n + 1}")
            assert budget_warnings() == 0
            for n in range(5):
                assert (await client._check_easyeda_footprint(f"C{900 + n}"))[1] == "budget"
            assert budget_warnings() == 1
            # Next window: spend it again, and the first skip warns again
            clock.advance(EASYEDA_PRODUCTS_WINDOW)
            for n in range(EASYEDA_PRODUCTS_BUDGET):
                await client._check_easyeda_footprint(f"C{100 + n}")
            assert (await client._check_easyeda_footprint("C999"))[1] == "budget"
            assert budget_warnings() == 2

    async def test_cached_answers_dont_use_budget(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        for _ in range(100):
            await client._check_easyeda_footprint("C1525")
        assert len(session.urls) == 1
        assert client._easyeda_products_budget.used == 1

    async def test_skips_return_fresh_dicts(self, clock):
        """Callers merge these into parts; a shared dict would leak edits between calls."""
        client, _ = make_client(clock, lambda url: FakeResponse(403))
        first, _ = await client._check_easyeda_footprint("C1")
        second, _ = await client._check_easyeda_footprint("C2")
        assert first == second == UNKNOWN and first is not second

    @pytest.mark.parametrize(
        "respond", [lambda url: FakeResponse(200, FOUND), lambda url: FakeResponse(403), lambda url: RuntimeError("x")]
    )
    async def test_public_shape_unchanged(self, clock, respond):
        client, _ = make_client(clock, respond)
        for lcsc in ["C1", "C1", "C2", "bad"]:
            result = await client.check_easyeda_footprint(lcsc)
            assert set(result) == {"has_easyeda_footprint", "easyeda_symbol_uuid", "easyeda_footprint_uuid"}


# --- Cooldown through the client ------------------------------------------------


class TestClientCooldown:
    async def test_doubles_then_resets_after_success(self, clock):
        answers = iter([FakeResponse(403), FakeResponse(403), FakeResponse(200, FOUND), FakeResponse(403)])
        client, session = make_client(clock, lambda url: next(answers))
        cooldown = client._easyeda_products_cooldown

        assert (await client._check_easyeda_footprint("C1"))[1] == "blocked"
        assert cooldown.remaining == 120
        clock.advance(120)
        assert (await client._check_easyeda_footprint("C1"))[1] == "blocked"
        assert cooldown.remaining == 240
        clock.advance(240)
        assert (await client._check_easyeda_footprint("C1"))[1] == "checked"
        assert (await client._check_easyeda_footprint("C2"))[1] == "blocked"
        assert cooldown.remaining == 120  # the success cleared the strikes
        assert len(session.urls) == 4

    async def test_concurrent_blocks_count_once(self, clock):
        """Checks already in flight when the block starts all get 403; that's one block, not five."""
        client, session = make_client(clock, lambda url: FakeResponse(403))
        results = await asyncio.gather(*[client._check_easyeda_footprint(f"C{n}") for n in range(1, 6)])
        assert [status for _, status in results] == ["blocked"] * 5
        assert len(session.urls) == 5
        assert client._easyeda_products_cooldown.remaining == 120
        assert (await client._check_easyeda_footprint("C6"))[1] == "cooldown"
        clock.advance(120)
        await client._check_easyeda_footprint("C7")
        assert client._easyeda_products_cooldown.remaining == 240  # second strike, not the sixth

    async def test_queued_checks_see_a_block_that_started_while_they_waited(self, clock):
        """15 checks, 5 at a time: once the first ones are blocked, the queued ones don't send."""
        client, session = make_client(clock, lambda url: FakeResponse(403))
        results = await asyncio.gather(*[client._check_easyeda_footprint(f"C{n}") for n in range(1, 16)])
        statuses = [status for _, status in results]
        assert statuses.count("blocked") == len(session.urls) <= 5
        assert statuses.count("cooldown") == 15 - len(session.urls)

    async def test_stale_success_doesnt_end_the_pause(self, clock):
        """A request sent before the block that comes back 200 afterwards must not clear the cooldown."""
        def respond(url):
            return FakeResponse(200, FOUND) if lcsc_of(url) == "C1" else FakeResponse(403)

        client, _ = make_client(clock, respond, delay=lambda url: 5 if lcsc_of(url) == "C1" else 1)
        results = await asyncio.gather(client._check_easyeda_footprint("C1"), client._check_easyeda_footprint("C2"))
        assert [status for _, status in results] == ["checked", "blocked"]
        assert client._easyeda_products_cooldown.remaining == 120
        assert (await client._check_easyeda_footprint("C3"))[1] == "cooldown"
        clock.advance(120)
        assert (await client._check_easyeda_footprint("C4"))[1] == "blocked"
        assert client._easyeda_products_cooldown.remaining == 240  # the stale 200 didn't clear the strike


# --- Cache TTLs -------------------------------------------------------------------


class TestCacheTtls:
    @pytest.mark.parametrize("response", [FakeResponse(200, FOUND), FakeResponse(404)])
    async def test_answers_last_24h(self, clock, response):
        client, session = make_client(clock, lambda url: response)
        await client._check_easyeda_footprint("C1")
        clock.advance(EASYEDA_FOOTPRINT_CACHE_TTL - 1)
        assert (await client._check_easyeda_footprint("C1"))[1] == "cached"
        clock.advance(1)
        assert (await client._check_easyeda_footprint("C1"))[1] == "checked"
        assert len(session.urls) == 2
        assert EASYEDA_FOOTPRINT_CACHE_TTL == 24 * 3600

    async def test_errors_last_5_minutes(self, clock):
        client, session = make_client(clock, lambda url: RuntimeError("timed out"))
        await client._check_easyeda_footprint("C1")
        clock.advance(EASYEDA_ERROR_CACHE_TTL - 1)
        await client._check_easyeda_footprint("C1")
        assert len(session.urls) == 1
        clock.advance(1)
        await client._check_easyeda_footprint("C1")
        assert len(session.urls) == 2

    async def test_symbol_cache_still_1h(self, clock):
        """Symbol data (/api/components) keeps its 1h TTL; only footprint answers moved to 24h."""
        symbol = {"success": True, "result": {"dataStr": {"shape": []}}}
        client = JLCPCBClient()
        session = FakeSession(lambda url: FakeResponse(200, symbol))
        client._easyeda_session = session
        await client.get_easyeda_component("c" * 32)
        clock.advance(EASYEDA_CACHE_TTL - 1)
        await client.get_easyeda_component("c" * 32)
        assert len(session.urls) == 1
        clock.advance(1)
        await client.get_easyeda_component("c" * 32)
        assert len(session.urls) == 2


# --- Session config ---------------------------------------------------------------


class TestSessions:
    def test_products_session_sends_one_request(self):
        session = JLCPCBClient()._get_easyeda_products_session()
        assert session.max_retries == 0
        assert session.max_rotations == 0
        assert session.attempt_timeout == datetime.timedelta(seconds=EASYEDA_REQUEST_TIMEOUT)

    def test_symbol_session_pairs_timeout_with_attempt_timeout(self):
        session = JLCPCBClient()._get_easyeda_session()
        assert session.timeout == datetime.timedelta(seconds=EASYEDA_REQUEST_TIMEOUT)
        assert session.attempt_timeout == datetime.timedelta(seconds=EASYEDA_ATTEMPT_TIMEOUT)
        assert EASYEDA_ATTEMPT_TIMEOUT < EASYEDA_REQUEST_TIMEOUT

    async def test_close_drops_the_products_session(self):
        client = JLCPCBClient()
        client._get_easyeda_products_session()
        await client.close()
        assert client._easyeda_products_session is None


# --- find_alternatives footprint filter ---------------------------------------------


ORIGINAL = {"lcsc": "C999999", "subcategory": "Test Subcategory", "package": "0402",
            "library_type": "extended", "price": 0.1, "stock": 100, "specs": {}}


def stub_alternatives(client, monkeypatch, n_candidates: int, supported: bool = False) -> None:
    candidates = [{"lcsc": f"C{n}", "package": "0402", "library_type": "extended", "price": 0.1,
                   "stock": 10_000 - n, "specs": {}} for n in range(1, n_candidates + 1)]

    async def get_part(lcsc):
        return dict(ORIGINAL)

    async def search(**kwargs):
        return {"results": [dict(c) for c in candidates]}

    async def ensure_categories():
        return None

    monkeypatch.setattr(client, "get_part", get_part)
    monkeypatch.setattr(client, "search", search)
    monkeypatch.setattr(client, "_ensure_categories", ensure_categories)
    if supported:
        monkeypatch.setattr(client_module, "COMPATIBILITY_RULES", {"Test Subcategory": {"primary": None}})
        monkeypatch.setattr(
            client_module, "is_compatible_alternative",
            lambda original, part, subcategory: (True, {"specs_verified": [], "specs_unparseable": []}),
        )


class TestFootprintFilter:
    async def test_cap_note(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        stub_alternatives(client, monkeypatch, 60)
        result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=50)
        assert len(session.urls) == EASYEDA_MAX_FOOTPRINT_CHECKS
        note = result["summary"]["footprint_filter"]
        assert note["candidates"] == 60 and note["checked"] == 15 and note["unknown"] == 0
        assert "top 15 of 60 candidates" in note["note"]
        assert "rate-limiting" not in note["note"]
        assert all(p["has_easyeda_footprint"] is True for p in result["similar_parts"])

    async def test_no_note_when_nothing_was_limited(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        stub_alternatives(client, monkeypatch, 60)
        result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=5)
        assert len(session.urls) == 10  # 2 x limit, as before
        assert "footprint_filter" not in result["summary"]

    async def test_no_note_without_the_filter(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        stub_alternatives(client, monkeypatch, 60)
        result = await client.find_alternatives("C999999", limit=50)
        assert session.urls == []
        assert "footprint_filter" not in result["summary"]

    async def test_cap_doesnt_fire_when_few_candidates(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        stub_alternatives(client, monkeypatch, 12)
        result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=50)
        assert len(session.urls) == 12
        assert "footprint_filter" not in result["summary"]

    async def test_cooldown_note(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        stub_alternatives(client, monkeypatch, 20)
        client._easyeda_products_cooldown.trip()
        clock.advance(30)  # 90s left
        result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=5)
        assert session.urls == []
        assert result["similar_parts"] == []
        note = result["summary"]["footprint_filter"]
        assert note["unknown"] == 10
        assert "10 candidate(s) skipped: EasyEDA is rate-limiting" in note["note"]
        assert "about 2 min" in note["note"]

    async def test_block_mid_call_note(self, clock, monkeypatch):
        """The first checks succeed, then EasyEDA blocks: the rest are skipped, not hammered."""
        answers = iter([FakeResponse(200, FOUND)] * 3 + [FakeResponse(403)] * 20)
        client, session = make_client(clock, lambda url: next(answers))
        stub_alternatives(client, monkeypatch, 20)
        result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=5)
        assert len(session.urls) <= 3 + 5  # 3 answers + at most the 5 in flight when the block landed
        assert len(result["similar_parts"]) == 3
        assert result["summary"]["footprint_filter"]["unknown"] == 7
        assert "rate-limiting" in result["summary"]["footprint_filter"]["note"]

    async def test_budget_note(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND))
        stub_alternatives(client, monkeypatch, 20)
        for n in range(EASYEDA_PRODUCTS_BUDGET - 4):
            assert client._easyeda_products_budget.try_acquire()
        result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=5)
        assert len(session.urls) == 4
        note = result["summary"]["footprint_filter"]
        assert note["unknown"] == 6
        assert note["note"] == "6 candidate(s) skipped to stay under EasyEDA's rate limit. Try again in about 2 min."

    async def test_block_and_budget_notes_together(self, clock, monkeypatch):
        """A real block and our own budget are reported separately: only one is EasyEDA's doing.

        One budget slot left, 10 concurrent checks: one takes the slot and gets blocked; the rest
        are skipped by the budget or the cooldown, depending on which they reach first."""
        client, session = make_client(clock, lambda url: FakeResponse(403))
        stub_alternatives(client, monkeypatch, 20)
        for n in range(EASYEDA_PRODUCTS_BUDGET - 1):
            assert client._easyeda_products_budget.try_acquire()
        result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=5)
        assert len(session.urls) == 1
        summary = result["summary"]["footprint_filter"]
        assert summary["unknown"] == 10
        note = summary["note"]
        blocked = int(note.split(" candidate(s) skipped: EasyEDA is rate-limiting")[0].split()[-1])
        over_budget = int(note.split(" candidate(s) skipped to stay under")[0].split()[-1]) if "to stay under" in note else 0
        assert blocked >= 1 and blocked + over_budget == 10
        assert "EasyEDA is rate-limiting footprint lookups from this server. Try again in about 2 min." in note

    async def test_error_note(self, clock, monkeypatch):
        client, _ = make_client(clock, lambda url: RuntimeError("timed out") if lcsc_of(url) == "C2" else FakeResponse(200, FOUND))
        stub_alternatives(client, monkeypatch, 20)
        result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=5)
        note = result["summary"]["footprint_filter"]
        assert note["unknown"] == 1
        assert note["note"] == "1 candidate(s) skipped: their EasyEDA footprint lookup failed."

    async def test_note_on_supported_categories_too(self, clock, monkeypatch):
        client, _ = make_client(clock, lambda url: FakeResponse(200, FOUND))
        stub_alternatives(client, monkeypatch, 60, supported=True)
        result = await client.find_alternatives("C999999", has_easyeda_footprint=True, limit=50)
        assert result["summary"]["is_supported_category"] is True
        assert result["summary"]["footprint_filter"]["checked"] == 15
        assert len(result["alternatives"]) == 15

    async def test_filter_for_parts_without_footprints(self, clock, monkeypatch):
        client, _ = make_client(clock, lambda url: FakeResponse(404) if int(lcsc_of(url)[1:]) % 2 else FakeResponse(200, FOUND))
        stub_alternatives(client, monkeypatch, 20)
        result = await client.find_alternatives("C999999", has_easyeda_footprint=False, limit=5)
        assert {p["lcsc"] for p in result["similar_parts"]} == {"C1", "C3", "C5", "C7", "C9"}
        assert all(p["has_easyeda_footprint"] is False for p in result["similar_parts"])


# --- jlc_get_pinout: unknown is not "no symbol" ---------------------------------------


class TestPinoutUnknownSymbol:
    """While EasyEDA is rate-limiting (or failing), a part's symbol status is unknown. The pinout tool
    used to answer "No EasyEDA symbol available", which is wrong for parts that have one."""

    @staticmethod
    def fake_client(has_footprint):
        class Fake:
            async def get_part(self, lcsc):
                return {"lcsc": lcsc, "has_easyeda_footprint": has_footprint, "easyeda_symbol_uuid": None}
        return Fake()

    async def test_unknown_says_try_again(self, monkeypatch):
        from pcbparts_mcp import server
        monkeypatch.setattr(server, "_client", self.fake_client(None))
        result = await server.jlc_get_pinout(lcsc="c2040")
        assert result["error"] == (
            "Couldn't check EasyEDA for C2040's symbol right now (lookup failed or EasyEDA is "
            "rate-limiting). Try again in a few minutes."
        )

    async def test_absent_still_says_no_symbol(self, monkeypatch):
        from pcbparts_mcp import server
        monkeypatch.setattr(server, "_client", self.fake_client(False))
        result = await server.jlc_get_pinout(lcsc="C2040")
        assert result["error"] == "No EasyEDA symbol available for C2040"
