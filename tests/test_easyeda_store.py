"""Persistent EasyEDA footprint answers (0.6.0): the store, the seed, the client lookup order and the
pinout self-heal. See docs/ref-easyeda-api.md. No network: fake clocks and sessions."""

import gzip
import json
import re
import sys
import types
from pathlib import Path

import pytest

from pcbparts_mcp import client as client_module
from pcbparts_mcp.cache import Cooldown, SlidingWindowBudget
from pcbparts_mcp.client import EasyEDAComponentNotFound, JLCPCBClient
from pcbparts_mcp.config import (
    EASYEDA_COOLDOWN_BASE,
    EASYEDA_COOLDOWN_MAX,
    EASYEDA_FOOTPRINT_CACHE_TTL,
    EASYEDA_NOT_FOUND_TTL,
    EASYEDA_PRODUCTS_BUDGET,
    EASYEDA_PRODUCTS_WINDOW,
    EASYEDA_RECHECK_INTERVAL,
)
from pcbparts_mcp.db import ComponentDatabase
from pcbparts_mcp.easyeda_store import (
    SEED_COLUMNS,
    EasyEDAStore,
    FootprintAnswer,
    SeedRow,
    format_checked,
    pick_answer,
    read_seed_csv,
    seed_checked_at,
    write_seed_csv,
)

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import build_database  # noqa: E402

SYM, FP = "a" * 32, "b" * 32
SYM2, FP2 = "c" * 32, "d" * 32
FOUND = {"success": True, "result": {"uuid": SYM, "packageDetail": {"uuid": FP}}}
DAY = 86400


class FakeClock:
    def __init__(self, start: float = 1_800_000_000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload
        self.challenge_type = None

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, respond):
        self.respond = respond
        self.urls: list[str] = []

    async def get(self, url: str):
        self.urls.append(url)
        result = self.respond(url)
        if isinstance(result, Exception):
            raise result
        return result


_open_clients: list[JLCPCBClient] = []


@pytest.fixture(autouse=True)
def _close_stores():
    """Close every store a test opened (Windows can't delete an open SQLite file)."""
    yield
    while _open_clients:
        store = _open_clients.pop()._easyeda_store
        if store is not None:
            store.close()


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(client_module, "time", types.SimpleNamespace(time=fake))
    return fake


def make_client(clock, respond, store_path: Path | None = None) -> tuple[JLCPCBClient, FakeSession]:
    client = JLCPCBClient(easyeda_store_path=str(store_path) if store_path else None)
    client._easyeda_products_budget = SlidingWindowBudget(EASYEDA_PRODUCTS_BUDGET, EASYEDA_PRODUCTS_WINDOW, clock)
    client._easyeda_products_cooldown = Cooldown(EASYEDA_COOLDOWN_BASE, EASYEDA_COOLDOWN_MAX, clock)
    session = FakeSession(respond)
    client._easyeda_products_session = session
    _open_clients.append(client)
    return client, session


# --- pick_answer -----------------------------------------------------------------------


class TestPickAnswer:
    NOW = 1_800_000_000.0

    def test_has_footprint_never_expires(self):
        old = FootprintAnswer(True, SYM, FP, self.NOW - 5 * 365 * DAY)
        assert pick_answer([old], self.NOW, EASYEDA_NOT_FOUND_TTL) == old

    def test_no_footprint_expires(self):
        fresh = FootprintAnswer(False, None, None, self.NOW - EASYEDA_NOT_FOUND_TTL + 1)
        stale = FootprintAnswer(False, None, None, self.NOW - EASYEDA_NOT_FOUND_TTL)
        assert pick_answer([fresh], self.NOW, EASYEDA_NOT_FOUND_TTL) == fresh
        assert pick_answer([stale], self.NOW, EASYEDA_NOT_FOUND_TTL) is None

    def test_newest_wins(self):
        older_found = FootprintAnswer(True, SYM, FP, self.NOW - 30 * DAY)
        newer_none = FootprintAnswer(False, None, None, self.NOW - DAY)
        assert pick_answer([older_found, newer_none], self.NOW, EASYEDA_NOT_FOUND_TTL) == newer_none
        newer_found = FootprintAnswer(True, SYM2, FP2, self.NOW - 3600)
        assert pick_answer([newer_none, None, newer_found], self.NOW, EASYEDA_NOT_FOUND_TTL) == newer_found

    def test_recheck_marker_overrides_older_answers(self):
        found = FootprintAnswer(True, SYM, FP, self.NOW - DAY)
        marker = FootprintAnswer(None, None, None, self.NOW - 60)
        assert pick_answer([found, marker], self.NOW, EASYEDA_NOT_FOUND_TTL) is None

    def test_nothing(self):
        assert pick_answer([], self.NOW, EASYEDA_NOT_FOUND_TTL) is None
        assert pick_answer([None, None], self.NOW, EASYEDA_NOT_FOUND_TTL) is None


# --- EasyEDAStore ----------------------------------------------------------------------


class TestEasyEDAStore:
    def test_round_trip_and_persistence(self, tmp_path):
        path = tmp_path / "cache" / "easyeda.db"
        store = EasyEDAStore(path)
        assert store.enabled
        store.put("C1", {"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM, "easyeda_footprint_uuid": FP}, 100.0)
        store.put("C2", {"has_easyeda_footprint": False, "easyeda_symbol_uuid": None, "easyeda_footprint_uuid": None}, 200.0)
        store.close()
        reopened = EasyEDAStore(path)
        assert reopened.get("C1") == FootprintAnswer(True, SYM, FP, 100.0)
        assert reopened.get("C2") == FootprintAnswer(False, None, None, 200.0)
        assert reopened.get("C3") is None
        assert len(reopened) == 2
        reopened.close()

    def test_unknown_isnt_stored(self, tmp_path):
        store = EasyEDAStore(tmp_path / "s.db")
        store.put("C1", {"has_easyeda_footprint": None, "easyeda_symbol_uuid": None, "easyeda_footprint_uuid": None})
        assert store.get("C1") is None
        store.close()

    @pytest.mark.parametrize("result", [
        {"has_easyeda_footprint": True, "easyeda_symbol_uuid": None, "easyeda_footprint_uuid": FP},
        {"has_easyeda_footprint": True, "easyeda_symbol_uuid": "not-a-uuid", "easyeda_footprint_uuid": FP},
        {"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM, "easyeda_footprint_uuid": "nope"},
    ])
    def test_answer_that_cant_be_kept_isnt_stored(self, tmp_path, caplog, result):
        """"Has a footprint" never expires, so one without a usable symbol UUID would make
        jlc_get_pinout fail for that part for good."""
        store = EasyEDAStore(tmp_path / "s.db")
        assert store.put("C1", result) is False
        assert store.get("C1") is None
        assert "Not storing EasyEDA footprint answer for C1" in caplog.text
        store.close()

    def test_mark_stale(self, tmp_path):
        store = EasyEDAStore(tmp_path / "s.db")
        store.put("C1", {"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM, "easyeda_footprint_uuid": FP}, 100.0)
        store.mark_stale("C1", 150.0)
        assert store.get("C1") == FootprintAnswer(None, None, None, 150.0)
        store.close()

    def test_unusable_path_falls_back_to_memory(self, tmp_path, caplog):
        blocker = tmp_path / "not-a-dir"
        blocker.write_text("x")
        store = EasyEDAStore(blocker / "easyeda.db")
        assert not store.enabled
        assert "unavailable" in caplog.text
        store.put("C1", {"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM, "easyeda_footprint_uuid": FP})
        store.mark_stale("C1")
        assert store.get("C1") is None
        assert len(store) == 0
        store.close()


# --- Seed CSV and the components.db table -------------------------------------------------


class TestSeedCsv:
    def test_round_trip_sorted_by_number(self, tmp_path):
        path = tmp_path / "easyeda" / "footprints.csv"
        rows = [
            SeedRow("C10000", True, SYM, FP, "2026-10-10T00:00:00Z", "s"),
            SeedRow("C2040", True, SYM2, None, "2026-10-09T00:00:00Z", "p"),
            SeedRow("C9", False, None, None, "2026-10-01T00:00:00Z", "p"),
        ]
        write_seed_csv(path, rows)
        text = path.read_bytes().decode("utf-8")
        assert "\r" not in text  # same bytes on Windows
        lines = text.splitlines()
        assert lines[0] == ",".join(SEED_COLUMNS)
        assert [line.split(",")[0] for line in lines[1:]] == ["C9", "C2040", "C10000"]
        assert lines[1] == "C9,0,,,2026-10-01T00:00:00Z,p"
        assert read_seed_csv(path) == {r.lcsc: r for r in rows}
        assert not list(path.parent.glob("*.tmp"))

    def test_wrong_header_rejected(self, tmp_path):
        path = tmp_path / "f.csv"
        path.write_text("lcsc,has\nC1,1\n", encoding="utf-8")
        with pytest.raises(ValueError, match="expected columns"):
            read_seed_csv(path)

    def test_checked_is_utc(self):
        assert seed_checked_at("2026-10-10T00:00:00Z") == 1791590400
        assert seed_checked_at("2026-10-10T14:03:22Z") == 1791590400 + 14 * 3600 + 3 * 60 + 22
        assert format_checked(1791590400 + 14 * 3600 + 3 * 60 + 22) == "2026-10-10T14:03:22Z"

    def test_has_footprint_without_footprint_uuid_is_fine(self, tmp_path):
        path = tmp_path / "f.csv"
        path.write_text(f"{','.join(SEED_COLUMNS)}\nC1,1,{SYM},,2026-10-10T00:00:00Z,s\n", encoding="utf-8")
        assert read_seed_csv(path)["C1"] == SeedRow("C1", True, SYM, None, "2026-10-10T00:00:00Z", "s")

    @pytest.mark.parametrize("line, problem", [
        (f"X1,1,{SYM},{FP},2026-10-10T00:00:00Z,s", "isn't an LCSC code"),
        (f"C1,1,,{FP},2026-10-10T00:00:00Z,s", "needs a 32-hex symbol_uuid"),
        (f"C1,1,{SYM[:31]},{FP},2026-10-10T00:00:00Z,s", "needs a 32-hex symbol_uuid"),
        (f"C1,1,{SYM},nope,2026-10-10T00:00:00Z,s", "footprint_uuid 'nope'"),
        (f"C1,0,{SYM},,2026-10-10T00:00:00Z,p", "has_footprint=0 with UUIDs"),
        (f"C1,yes,{SYM},{FP},2026-10-10T00:00:00Z,s", "must be 0 or 1"),
        (f"C1,1,{SYM},{FP},2026-10-10,s", "checked must look like"),
        (f"C1,1,{SYM},{FP},2026-10-10T00:00:00Z,x", "source must be s or p"),
        (f"C1,1,{SYM}", "expected 6 fields, got 3"),
        (f"C2,1,{SYM},{FP},2026-10-10T00:00:00Z,s\nC2,0,,,2026-10-10T00:00:00Z,p", "line 3: C2 appears twice"),
    ])
    def test_malformed_rows_rejected(self, tmp_path, line, problem):
        path = tmp_path / "f.csv"
        path.write_text(f"{','.join(SEED_COLUMNS)}\n{line}\n", encoding="utf-8")
        with pytest.raises(ValueError, match=re.escape(problem)) as info:
            read_seed_csv(path)
        assert " line " in str(info.value)


def _write_category(data_dir: Path, parts: list[str]) -> None:
    (data_dir / "categories").mkdir(parents=True, exist_ok=True)
    with gzip.open(data_dir / "categories" / "test.jsonl.gz", "wt", encoding="utf-8") as f:
        for lcsc in parts:
            f.write(json.dumps({"l": lcsc, "m": f"MPN-{lcsc}", "f": "TestCorp", "p": "0402", "s": 100,
                                "t": "b", "c": 1, "$": 0.01, "d": lcsc, "a": []}) + "\n")


class TestSeedInComponentsDb:
    def test_build_loads_seed_and_db_serves_it(self, tmp_path):
        data_dir = tmp_path / "data"
        _write_category(data_dir, ["C1", "C2"])
        write_seed_csv(data_dir / "easyeda" / "footprints.csv", [
            SeedRow("C1", True, SYM, FP, "2026-10-10T00:00:00Z", "s"),
            SeedRow("C2", False, None, None, "2026-10-09T00:00:00Z", "p"),
        ])
        db_path = tmp_path / "components.db"
        stats = build_database(data_dir, db_path, verbose=False)
        assert stats["easyeda_seed_rows"] == 2
        db = ComponentDatabase(db_path=db_path, data_dir=data_dir)
        try:
            assert db.get_easyeda_seed("C1") == FootprintAnswer(True, SYM, FP, seed_checked_at("2026-10-10T00:00:00Z"))
            assert db.get_easyeda_seed("C2") == FootprintAnswer(False, None, None, seed_checked_at("2026-10-09T00:00:00Z"))
            assert db.get_easyeda_seed("C3") is None
            assert db.easyeda_seed_size() == 2
        finally:
            db.close()

    def test_missing_seed_gives_empty_table(self, tmp_path):
        data_dir = tmp_path / "data"
        _write_category(data_dir, ["C1"])
        db_path = tmp_path / "components.db"
        assert build_database(data_dir, db_path, verbose=False)["easyeda_seed_rows"] == 0
        db = ComponentDatabase(db_path=db_path, data_dir=data_dir)
        try:
            assert db.get_easyeda_seed("C1") is None
            assert db.easyeda_seed_size() == 0
        finally:
            db.close()

    def test_malformed_seed_fails_the_build_and_keeps_the_old_db(self, tmp_path):
        data_dir = tmp_path / "data"
        _write_category(data_dir, ["C1"])
        seed_path = data_dir / "easyeda" / "footprints.csv"
        write_seed_csv(seed_path, [SeedRow("C1", True, SYM, FP, "2026-10-10T00:00:00Z", "s")])
        db_path = tmp_path / "components.db"
        build_database(data_dir, db_path, verbose=False)
        seed_path.write_text(f"{','.join(SEED_COLUMNS)}\nC1,1,,,2026-10-10T00:00:00Z,s\n", encoding="utf-8")
        with pytest.raises(ValueError, match="symbol_uuid"):
            build_database(data_dir, db_path, verbose=False)
        db = ComponentDatabase(db_path=db_path, data_dir=data_dir)
        try:
            assert db.get_easyeda_seed("C1").symbol_uuid == SYM
        finally:
            db.close()

    def test_malformed_seed_fails_before_the_components_load(self, tmp_path):
        """The seed is read first, so a bad file fails the build in a second, not after the load."""
        data_dir = tmp_path / "data"
        (data_dir / "categories").mkdir(parents=True)
        (data_dir / "categories" / "broken.jsonl.gz").write_bytes(b"not gzip")  # the load would fail on this
        seed_path = data_dir / "easyeda" / "footprints.csv"
        seed_path.parent.mkdir()
        seed_path.write_text(f"{','.join(SEED_COLUMNS)}\nC1,1,,,2026-10-10T00:00:00Z,s\n", encoding="utf-8")
        with pytest.raises(ValueError, match="symbol_uuid"):
            build_database(data_dir, tmp_path / "components.db", verbose=False)

    def test_db_without_seed_table(self, tmp_path):
        """A components.db built before 0.6.0 has no easyeda_footprints table."""
        data_dir = tmp_path / "data"
        _write_category(data_dir, ["C1"])
        db_path = tmp_path / "components.db"
        build_database(data_dir, db_path, verbose=False)
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("DROP TABLE easyeda_footprints")
        conn.commit()
        conn.close()
        db = ComponentDatabase(db_path=db_path, data_dir=data_dir)
        try:
            assert db.get_easyeda_seed("C1") is None
            assert db.easyeda_seed_size() == 0
        finally:
            db.close()


# --- Client lookup order ---------------------------------------------------------------


class TestClientStore:
    def test_only_an_explicit_path_opens_a_store(self, tmp_path, monkeypatch):
        """Tests and scripts build clients with fake answers; they must never write to the real
        store, even with EASYEDA_STORE_PATH set (it is in the Docker image)."""
        path = tmp_path / "easyeda.db"
        monkeypatch.setenv("EASYEDA_STORE_PATH", str(path))
        monkeypatch.setattr("pcbparts_mcp.config.EASYEDA_STORE_PATH", str(path))
        assert JLCPCBClient()._easyeda_store is None
        assert JLCPCBClient().easyeda_store_size() is None
        assert not path.exists()
        client = JLCPCBClient(easyeda_store_path=str(path))
        _open_clients.append(client)
        assert client._easyeda_store.enabled
        assert client.easyeda_store_size() == 0
        client._easyeda_store.put("C1", {"has_easyeda_footprint": False})
        assert client.easyeda_store_size() == 1
        blocker = tmp_path / "not-a-dir"
        blocker.write_text("x")
        unusable = JLCPCBClient(easyeda_store_path=str(blocker / "s.db"))
        _open_clients.append(unusable)
        assert unusable.easyeda_store_size() is None  # couldn't open: memory only

    async def test_live_answers_survive_a_restart(self, clock, tmp_path):
        path = tmp_path / "easyeda.db"
        first, session = make_client(clock, lambda url: FakeResponse(200, FOUND), path)
        none_url = lambda url: FakeResponse(404)  # noqa: E731
        assert (await first._check_easyeda_footprint("C1"))[1] == "checked"
        first._easyeda_products_session = FakeSession(none_url)
        assert (await first._check_easyeda_footprint("C2"))[0]["has_easyeda_footprint"] is False
        await first.close()

        # New process, same volume: answered from the store, no request
        second, session2 = make_client(clock, lambda url: FakeResponse(200, FOUND), path)
        result, status = await second._check_easyeda_footprint("C1")
        assert status == "stored"
        assert result == {"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM, "easyeda_footprint_uuid": FP}
        assert (await second._check_easyeda_footprint("C2"))[1] == "stored"
        assert session2.urls == []
        # "Has a footprint" stays; "no footprint" is asked again after its TTL
        clock.advance(EASYEDA_NOT_FOUND_TTL)
        assert (await second._check_easyeda_footprint("C1"))[1] == "stored"
        assert (await second._check_easyeda_footprint("C2"))[1] == "checked"
        assert len(session2.urls) == 1
        await second.close()

    @pytest.mark.parametrize("response", [FakeResponse(403), FakeResponse(500), RuntimeError("timeout")])
    async def test_unknowns_arent_stored(self, clock, tmp_path, response):
        path = tmp_path / "easyeda.db"
        client, _ = make_client(clock, lambda url: response, path)
        assert (await client._check_easyeda_footprint("C1"))[0]["has_easyeda_footprint"] is None
        assert client._easyeda_store.get("C1") is None

    async def test_seed_answers_without_a_request(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND), None)
        assert client._easyeda_store is None
        seeds = {"C1": FootprintAnswer(True, SYM2, FP2, clock.now - 400 * DAY),
                 "C2": FootprintAnswer(False, None, None, clock.now - DAY),
                 "C3": FootprintAnswer(False, None, None, clock.now - EASYEDA_NOT_FOUND_TTL)}
        client.set_easyeda_seed(seeds.get)
        assert await client._check_easyeda_footprint("C1") == (
            {"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM2, "easyeda_footprint_uuid": FP2}, "stored")
        assert (await client._check_easyeda_footprint("C2"))[1] == "stored"
        assert session.urls == []
        assert (await client._check_easyeda_footprint("C3"))[1] == "checked"  # expired "no footprint"
        assert len(session.urls) == 1

    async def test_newer_store_answer_beats_older_seed(self, clock, tmp_path):
        client, session = make_client(clock, lambda url: FakeResponse(404), tmp_path / "s.db")
        client.set_easyeda_seed(lambda lcsc: FootprintAnswer(True, SYM, FP, clock.now - 30 * DAY))
        client._easyeda_store.put("C1", {"has_easyeda_footprint": False, "easyeda_symbol_uuid": None,
                                         "easyeda_footprint_uuid": None}, clock.now - DAY)
        assert (await client._check_easyeda_footprint("C1"))[0]["has_easyeda_footprint"] is False
        # ...and a newer seed (monthly refresh) beats an older stored "no footprint"
        client.set_easyeda_seed(lambda lcsc: FootprintAnswer(True, SYM, FP, clock.now - 3600))
        assert (await client._check_easyeda_footprint("C1"))[0]["has_easyeda_footprint"] is True
        assert session.urls == []

    async def test_broken_seed_doesnt_break_lookups(self, clock, caplog):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND), None)

        def broken(lcsc):
            raise RuntimeError("db gone")
        client.set_easyeda_seed(broken)
        assert (await client._check_easyeda_footprint("C1"))[1] == "checked"
        assert "seed lookup failed" in caplog.text

    async def test_memory_cache_still_first(self, clock, tmp_path):
        client, session = make_client(clock, lambda url: FakeResponse(200, FOUND), tmp_path / "s.db")
        await client._check_easyeda_footprint("C1")
        assert (await client._check_easyeda_footprint("C1"))[1] == "cached"
        clock.advance(EASYEDA_FOOTPRINT_CACHE_TTL)
        assert (await client._check_easyeda_footprint("C1"))[1] == "stored"
        assert len(session.urls) == 1

    async def test_stored_answers_dont_use_budget_or_wait_out_a_cooldown(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(403), None)
        client.set_easyeda_seed(lambda lcsc: FootprintAnswer(True, SYM, FP, clock.now) if lcsc == "C1" else None)
        assert (await client._check_easyeda_footprint("C2"))[1] == "blocked"
        assert (await client._check_easyeda_footprint("C1"))[1] == "stored"
        assert client._easyeda_products_budget.used == 1


class TestInvalidate:
    @pytest.mark.parametrize("with_store", [True, False])
    async def test_next_check_asks_easyeda(self, clock, tmp_path, with_store):
        new = {"success": True, "result": {"uuid": SYM2, "packageDetail": {"uuid": FP2}}}
        client, session = make_client(clock, lambda url: FakeResponse(200, new),
                                      tmp_path / "s.db" if with_store else None)
        client.set_easyeda_seed(lambda lcsc: FootprintAnswer(True, SYM, FP, clock.now - DAY))
        if with_store:
            client._easyeda_store.put("C1", {"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM,
                                             "easyeda_footprint_uuid": FP}, clock.now - 60)
        client._part_cache["C1"] = (clock.now, {"lcsc": "C1", "easyeda_symbol_uuid": SYM})
        assert (await client._check_easyeda_footprint("C1"))[0]["easyeda_symbol_uuid"] == SYM

        clock.advance(1)
        await client.invalidate_easyeda_footprint("C1")
        assert "C1" not in client._part_cache
        result, status = await client._check_easyeda_footprint("C1")
        assert (status, result["easyeda_symbol_uuid"]) == ("checked", SYM2)
        assert len(session.urls) == 1
        if with_store:
            assert client._easyeda_store.get("C1").symbol_uuid == SYM2
        # Once memory expires the old seed answer must not come back, and the fresh one is served
        # without another request: from the store, or kept in memory when there's no store
        clock.advance(EASYEDA_FOOTPRINT_CACHE_TTL)
        result, status = await client._check_easyeda_footprint("C1")
        assert (status, result["easyeda_symbol_uuid"]) == ("stored", SYM2)
        assert len(session.urls) == 1
        assert ("C1" in client._easyeda_overrides) is not with_store

    async def test_store_that_cant_write_keeps_the_fresh_answer_in_memory(self, clock, tmp_path):
        new = {"success": True, "result": {"uuid": SYM2, "packageDetail": {"uuid": FP2}}}
        blocker = tmp_path / "not-a-dir"
        blocker.write_text("x")
        client, session = make_client(clock, lambda url: FakeResponse(200, new), blocker / "s.db")
        assert not client._easyeda_store.enabled
        client.set_easyeda_seed(lambda lcsc: FootprintAnswer(True, SYM, FP, clock.now - DAY))
        await client.invalidate_easyeda_footprint("C1")
        assert (await client._check_easyeda_footprint("C1"))[1] == "checked"
        clock.advance(EASYEDA_FOOTPRINT_CACHE_TTL)
        result, status = await client._check_easyeda_footprint("C1")
        assert (status, result["easyeda_symbol_uuid"]) == ("stored", SYM2)
        assert len(session.urls) == 1


    async def test_marker_survives_a_restart(self, clock, tmp_path):
        """If the re-check can't run (EasyEDA blocking) and the server restarts, the old UUID must
        not come back from the store or seed."""
        path = tmp_path / "s.db"
        client, _ = make_client(clock, lambda url: FakeResponse(403), path)
        client._easyeda_store.put("C1", {"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM,
                                         "easyeda_footprint_uuid": FP}, clock.now - DAY)
        clock.advance(1)
        await client.invalidate_easyeda_footprint("C1")
        assert (await client._check_easyeda_footprint("C1"))[1] == "blocked"
        await client.close()

        restarted, session = make_client(clock, lambda url: FakeResponse(200, FOUND), path)
        restarted.set_easyeda_seed(lambda lcsc: FootprintAnswer(True, SYM, FP, clock.now - 2 * DAY))
        assert (await restarted._check_easyeda_footprint("C1"))[1] == "checked"
        assert len(session.urls) == 1


class TestAnswersThatCantBeKept:
    NO_UUID = {"success": True, "result": {"uuid": None, "packageDetail": {"uuid": FP}}}

    async def test_live_answer_without_symbol_uuid_is_asked_again_later(self, clock, tmp_path):
        """Served as EasyEDA gave it (as before 0.6.0), but not stored: once memory expires the
        part is checked again instead of failing in jlc_get_pinout for good."""
        client, session = make_client(clock, lambda url: FakeResponse(200, self.NO_UUID), tmp_path / "s.db")
        result, status = await client._check_easyeda_footprint("C1")
        assert (status, result["has_easyeda_footprint"], result["easyeda_symbol_uuid"]) == ("checked", True, None)
        assert client._easyeda_store.get("C1") is None
        clock.advance(EASYEDA_FOOTPRINT_CACHE_TTL)
        assert (await client._check_easyeda_footprint("C1"))[1] == "checked"
        assert len(session.urls) == 2

    async def test_self_heal_without_store_keeps_the_marker(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, self.NO_UUID))
        client.set_easyeda_seed(lambda lcsc: FootprintAnswer(True, SYM, FP, clock.now - DAY))
        await client.invalidate_easyeda_footprint("C1")
        assert (await client._check_easyeda_footprint("C1"))[1] == "checked"
        assert client._easyeda_overrides["C1"].has_footprint is None  # still a re-check marker
        clock.advance(EASYEDA_FOOTPRINT_CACHE_TTL)
        assert (await client._check_easyeda_footprint("C1"))[1] == "checked"  # not the old seed answer
        assert len(session.urls) == 2


async def health_counts(server):
    response = await server.health(None)
    assert response.status_code == 200
    return json.loads(response.body)["easyeda_footprints"]


class TestServerWiring:
    async def test_lifespan_wires_the_seed_and_no_store_in_tests(self):
        """Without set_easyeda_seed() every footprint check would go to EasyEDA."""
        from fastmcp import Client
        from pcbparts_mcp import server
        async with Client(server.mcp):
            assert server._client._easyeda_seed is not None
            assert server._client._easyeda_store is None  # tests/conftest.py blanks EASYEDA_STORE_PATH

    async def test_lifespan_opens_and_closes_the_store(self, tmp_path, monkeypatch):
        from fastmcp import Client
        from pcbparts_mcp import server
        monkeypatch.setattr(server, "EASYEDA_STORE_PATH", str(tmp_path / "easyeda.db"))
        async with Client(server.mcp):
            store = server._client._easyeda_store
            assert store.enabled and store.path == tmp_path / "easyeda.db"
        assert not store.enabled  # closed at shutdown (Windows can then delete tmp_path)

    async def test_health_shows_seed_and_store_counts(self, tmp_path, monkeypatch):
        """/health is how a deploy gets checked without the server's logs: the seed loaded, and the
        store opened and is filling up."""
        from fastmcp import Client
        from pcbparts_mcp import server
        monkeypatch.setattr(server, "EASYEDA_STORE_PATH", str(tmp_path / "easyeda.db"))
        async with Client(server.mcp):
            seeded = server.get_db().easyeda_seed_size()
            assert await health_counts(server) == {"seeded": seeded, "stored": 0}
            assert server._client._easyeda_store.put("C1", {"has_easyeda_footprint": False})
            assert (await health_counts(server))["stored"] == 0  # not counted on every request
            monkeypatch.setattr(server, "HEALTH_STORE_COUNT_TTL", 0)
            assert await health_counts(server) == {"seeded": seeded, "stored": 1}

    async def test_health_without_a_store(self, monkeypatch):
        from fastmcp import Client
        from pcbparts_mcp import server
        async with Client(server.mcp):
            assert (await health_counts(server))["stored"] is None  # memory only
        monkeypatch.setattr(server, "_client", None)
        assert await health_counts(server) is None  # before startup


class TestConfirmedRecently:
    async def test_live_answers_within_the_interval(self, clock, tmp_path):
        path = tmp_path / "s.db"
        client, _ = make_client(clock, lambda url: FakeResponse(200, FOUND), path)
        await client._check_easyeda_footprint("C1")
        assert client.footprint_confirmed_recently("C1", SYM)
        assert client.footprint_confirmed_recently(" c1 ", SYM)
        assert not client.footprint_confirmed_recently("C1", SYM2)
        assert not client.footprint_confirmed_recently("C2", SYM)
        await client.close()
        # A restart within the hour: the store still knows when EasyEDA named it
        restarted, _ = make_client(clock, lambda url: FakeResponse(200, FOUND), path)
        assert restarted.footprint_confirmed_recently("C1", SYM)
        clock.advance(EASYEDA_RECHECK_INTERVAL)
        assert not restarted.footprint_confirmed_recently("C1", SYM)

    async def test_seed_answers_and_errors_dont_count(self, clock):
        client, _ = make_client(clock, lambda url: FakeResponse(500))
        client.set_easyeda_seed(lambda lcsc: FootprintAnswer(True, SYM, FP, clock.now) if lcsc == "C1" else None)
        assert (await client._check_easyeda_footprint("C1"))[1] == "stored"
        assert (await client._check_easyeda_footprint("C2"))[1] == "error"
        assert not client.footprint_confirmed_recently("C1", SYM)
        assert not client.footprint_confirmed_recently("C2", SYM)


class TestComponentNotFound:
    @staticmethod
    def symbol_client(response) -> JLCPCBClient:
        client = JLCPCBClient()
        client._easyeda_session = FakeSession(lambda url: response)
        return client

    @pytest.mark.parametrize("response", [
        FakeResponse(200, {"success": False, "code": 404, "message": "Component not found"}),  # what EasyEDA sends
        FakeResponse(404),
    ])
    async def test_missing_symbol(self, response):
        client = self.symbol_client(response)
        with pytest.raises(EasyEDAComponentNotFound):
            await client.get_easyeda_component(SYM)
        with pytest.raises(EasyEDAComponentNotFound):  # cached for the error TTL
            await client.get_easyeda_component(SYM)
        assert len(client._easyeda_session.urls) == 1

    @pytest.mark.parametrize("response", [
        FakeResponse(200, {"success": False, "code": 500, "message": "oops"}),
        FakeResponse(500),
        RuntimeError("connection reset"),
    ])
    async def test_other_failures_arent_not_found(self, response):
        client = self.symbol_client(response)
        with pytest.raises(ValueError) as info:
            await client.get_easyeda_component(SYM)
        assert not isinstance(info.value, EasyEDAComponentNotFound)


# --- jlc_get_pinout self-heal ------------------------------------------------------------

SYMBOL_DATA = {"dataStr": {"head": {}, "shape": [
    "P~show~0~1~100~100~180~gge1~0^^100~100^^M100,100h10~#880000^^1~110~105~0~G~start~~~#880000^^1~100~100~0~1~end~~~#0000FF",
]}, "verify": True}


class FakePinoutClient:
    def __init__(self, recheck: dict, components: dict, confirmed_recently: bool = False):
        self.recheck = recheck
        self.components = components
        self.confirmed_recently = confirmed_recently
        self.calls: list[str] = []

    def footprint_confirmed_recently(self, lcsc, symbol_uuid):
        return self.confirmed_recently

    async def get_part(self, lcsc):
        return {"lcsc": lcsc, "has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM, "model": "M"}

    async def get_easyeda_component(self, uuid):
        self.calls.append(f"component {uuid[:1]}")
        answer = self.components[uuid]
        if isinstance(answer, Exception):
            raise answer
        return answer

    async def invalidate_easyeda_footprint(self, lcsc):
        self.calls.append(f"invalidate {lcsc}")

    async def check_easyeda_footprint(self, lcsc):
        self.calls.append(f"check {lcsc}")
        return self.recheck


class TestPinoutSelfHeal:
    GONE = EasyEDAComponentNotFound(f"EasyEDA has no symbol {SYM}")

    async def test_follows_the_new_uuid(self, monkeypatch):
        from pcbparts_mcp import server
        fake = FakePinoutClient(
            {"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM2, "easyeda_footprint_uuid": FP2},
            {SYM: self.GONE, SYM2: SYMBOL_DATA})
        monkeypatch.setattr(server, "_client", fake)
        result = await server.jlc_get_pinout(lcsc="C1")
        assert "error" not in result, result
        assert result["easyeda_symbol_uuid"] == SYM2
        assert fake.calls == ["component a", "invalidate C1", "check C1", "component c"]

    @pytest.mark.parametrize("recheck, error", [
        ({"has_easyeda_footprint": None}, "Couldn't check EasyEDA for C1's symbol right now"),
        ({"has_easyeda_footprint": False, "easyeda_symbol_uuid": None}, "No EasyEDA symbol available for C1"),
        ({"has_easyeda_footprint": True, "easyeda_symbol_uuid": SYM}, f"EasyEDA has no symbol {SYM}"),
    ])
    async def test_gives_up_cleanly(self, monkeypatch, recheck, error):
        from pcbparts_mcp import server
        fake = FakePinoutClient(recheck, {SYM: self.GONE})
        monkeypatch.setattr(server, "_client", fake)
        result = await server.jlc_get_pinout(lcsc="C1")
        assert result["error"].startswith(error)
        assert fake.calls[-1] == "check C1"

    async def test_no_recheck_when_easyeda_named_the_dead_uuid_recently(self, monkeypatch):
        """Otherwise every pinout call for the part would spend one /api/products request."""
        from pcbparts_mcp import server
        fake = FakePinoutClient({}, {SYM: self.GONE}, confirmed_recently=True)
        monkeypatch.setattr(server, "_client", fake)
        result = await server.jlc_get_pinout(lcsc="C1")
        assert result["error"] == f"EasyEDA has no symbol {SYM}"
        assert fake.calls == ["component a"]

    async def test_uuid_lookup_doesnt_self_heal(self, monkeypatch):
        from pcbparts_mcp import server
        fake = FakePinoutClient({}, {SYM: self.GONE})
        monkeypatch.setattr(server, "_client", fake)
        result = await server.jlc_get_pinout(uuid=SYM)
        assert result["error"] == f"EasyEDA has no symbol {SYM}"
        assert fake.calls == ["component a"]
