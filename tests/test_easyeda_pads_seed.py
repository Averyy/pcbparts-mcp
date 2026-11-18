"""Footprint pads seed (data/easyeda/pads.csv): the CSV, the components.db build step, the database
lookup, and scripts/build_easyeda_pads.py (todo order, pacing, resume, refresh, stop on refusal).
Fake sessions and clocks only; no network."""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

from pcbparts_mcp.db import ComponentDatabase
from pcbparts_mcp.easyeda_store import (
    PADS_SEED_COLUMNS, PadsRow, pack_pads, read_pads_csv, seed_checked_at, write_pads_csv, write_seed_csv, SeedRow,
)

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import build_easyeda_pads as script  # noqa: E402
from build_database import build_database  # noqa: E402
from test_easyeda_store import _write_category  # noqa: E402

A, B, C = "a" * 32, "b" * 32, "c" * 32
PADS = pack_pads([{"number": "1", "x": -1.0, "y": 0.5}, {"number": "2", "x": 1.0, "y": 0.5, "hole": 0.8}])
DAY = "2026-11-17T00:00:00Z"


class TestPadsCsv:
    def test_round_trip(self, tmp_path):
        path = tmp_path / "pads.csv"
        write_pads_csv(path, [PadsRow(B, "[]", DAY), PadsRow(A, PADS, DAY)])
        assert path.read_text(encoding="utf-8").splitlines()[0] == ",".join(PADS_SEED_COLUMNS)
        assert list(read_pads_csv(path)) == [A, B]  # sorted
        assert read_pads_csv(path)[A] == PadsRow(A, PADS, DAY)

    @pytest.mark.parametrize("line, problem", [
        (f"xyz,[],{DAY}", "isn't 32 hex"),
        (f"{A},not-json,{DAY}", "aren't valid"),
        (f"{A},[],yesterday", "fetched must look like"),
        (f"{A},[]", "expected 3 fields"),
    ])
    def test_bad_rows_fail(self, tmp_path, line, problem):
        path = tmp_path / "pads.csv"
        path.write_text(f"{','.join(PADS_SEED_COLUMNS)}\n{line}\n", encoding="utf-8")
        with pytest.raises(ValueError, match=problem):
            read_pads_csv(path)

    def test_duplicate_fails(self, tmp_path):
        path = tmp_path / "pads.csv"
        path.write_text(f"{','.join(PADS_SEED_COLUMNS)}\n{A},[],{DAY}\n{A},[],{DAY}\n", encoding="utf-8")
        with pytest.raises(ValueError, match="appears twice"):
            read_pads_csv(path)


class TestBuild:
    def test_build_loads_pads(self, tmp_path):
        data_dir = tmp_path / "data"
        _write_category(data_dir, ["C1"])
        write_pads_csv(data_dir / "easyeda" / "pads.csv", [PadsRow(A, PADS, DAY), PadsRow(B, "[]", DAY)])
        db_path = tmp_path / "components.db"
        assert build_database(data_dir, db_path, verbose=False)["easyeda_pads_rows"] == 2
        db = ComponentDatabase(db_path=db_path, data_dir=data_dir)
        try:
            pads, fetched = db.get_easyeda_pads(A)
            assert [p["number"] for p in pads] == ["1", "2"] and pads[1]["hole"] is True
            assert fetched == seed_checked_at(DAY)
            assert db.get_easyeda_pads(B) == ([], seed_checked_at(DAY))
            assert db.get_easyeda_pads(C) is None
        finally:
            db.close()

    def test_no_pads_file(self, tmp_path):
        data_dir = tmp_path / "data"
        _write_category(data_dir, ["C1"])
        db_path = tmp_path / "components.db"
        assert build_database(data_dir, db_path, verbose=False)["easyeda_pads_rows"] == 0
        db = ComponentDatabase(db_path=db_path, data_dir=data_dir)
        try:
            assert db.get_easyeda_pads(A) is None
        finally:
            db.close()

    def test_bad_pads_file_fails_the_build(self, tmp_path):
        data_dir = tmp_path / "data"
        _write_category(data_dir, ["C1"])
        path = data_dir / "easyeda" / "pads.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{','.join(PADS_SEED_COLUMNS)}\n{A},oops,{DAY}\n", encoding="utf-8")
        with pytest.raises(ValueError, match="aren't valid"):
            build_database(data_dir, tmp_path / "components.db", verbose=False)


def _todo_db(tmp_path) -> sqlite3.Connection:
    """components.db with three connectors (stock 5, 500, 50) on footprints A, B, C and a resistor
    (stock 9,000) on C."""
    data_dir = tmp_path / "data"
    _write_category(data_dir, ["C1", "C2", "C3", "C4"])
    write_seed_csv(data_dir / "easyeda" / "footprints.csv", [
        SeedRow(lcsc, True, "d" * 32, fp, DAY, "s") for lcsc, fp in (("C1", A), ("C2", B), ("C3", C), ("C4", C))
    ])
    db_path = tmp_path / "components.db"
    build_database(data_dir, db_path, verbose=False)
    conn = sqlite3.connect(db_path)
    conn.executemany("INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)",
                     [(1, "Connectors", "connectors"), (2, "Resistors", "resistors")])
    conn.executemany("INSERT INTO subcategories (id, name, category_id, category_name) VALUES (?, ?, ?, ?)",
                     [(1, "Wire To Board", 1, "Connectors"), (2, "Chip Resistors", 2, "Resistors")])
    for lcsc, stock, sub in (("C1", 5, 1), ("C2", 500, 1), ("C3", 50, 1), ("C4", 9000, 2)):
        conn.execute("UPDATE components SET stock = ?, subcategory_id = ? WHERE lcsc = ?", (stock, sub, lcsc))
    conn.commit()
    return conn


class TestTodo:
    def test_most_stocked_first_and_skips_seeded(self, tmp_path):
        conn = _todo_db(tmp_path)
        try:
            now = seed_checked_at(DAY)
            assert script.footprints_todo(conn, ("Connectors",), {}, None, now) == [B, C, A]
            have = {B: PadsRow(B, "[]", DAY)}
            assert script.footprints_todo(conn, ("Connectors",), have, None, now) == [C, A]
            assert script.footprints_todo(conn, ("Resistors",), {}, None, now) == [C]
            assert script.footprints_todo(conn, None, {}, None, now) == [C, B, A]  # C4 has 9,000
        finally:
            conn.close()

    def test_refresh_days(self, tmp_path):
        conn = _todo_db(tmp_path)
        try:
            have = {fp: PadsRow(fp, "[]", DAY) for fp in (A, B, C)}
            later = seed_checked_at(DAY) + 91 * 86400
            assert script.footprints_todo(conn, None, have, None, later) == []
            assert script.footprints_todo(conn, ("Connectors",), have, 90, later) == [B, C, A]
            confirmed = {B: "2026-12-17T00:00:00Z"}  # B was confirmed 30 days after its fetch
            assert script.footprints_todo(conn, ("Connectors",), have, 90, later, confirmed) == [C, A]
        finally:
            conn.close()


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def footprint(n_pads: int) -> dict:
    shapes = [f"PAD~RECT~{i * 10}~0~4~12~1~~{i + 1}~0~~0~id{i}~0~~Y~0~0~0.4~" for i in range(n_pads)]
    return {"success": True, "result": {"dataStr": {"head": {"x": 0, "y": 0}, "shape": shapes}}}


class FakeSession:
    def __init__(self, replies: dict):
        self.replies = replies
        self.urls: list[str] = []

    async def get(self, url):
        self.urls.append(url)
        reply = self.replies[url.rsplit("/", 1)[1]]
        if isinstance(reply, Exception):
            raise reply
        return reply


class FakeTime:
    def __init__(self):
        self.now = 0.0
        self.slept: list[float] = []

    def clock(self):
        return self.now

    def wall(self):
        return seed_checked_at(DAY) + self.now

    async def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds


async def run(session, todo, have, out, fake, **kwargs):
    kwargs.setdefault("max_requests", None)
    kwargs.setdefault("save_every", 2)
    return await script.collect(session, todo, have, out, interval=2.0, sleep=fake.sleep, clock=fake.clock,
                                wall=fake.wall, **kwargs)


class TestCollect:
    async def test_fetches_paces_and_saves(self, tmp_path):
        out, fake = tmp_path / "pads.csv", FakeTime()
        session = FakeSession({A: FakeResponse(200, footprint(2)), B: FakeResponse(404),
                               C: FakeResponse(200, {"success": False, "code": 404})})
        counts = await run(session, [A, B, C], {}, out, fake)
        assert counts["added"] == 3 and counts["no_pads"] == 2 and not counts["blocked"]
        assert fake.slept == [2.0, 2.0]  # one request per interval, none before the first
        saved = read_pads_csv(out)
        assert [pad[0] for pad in json.loads(saved[A].pads)] == ["1", "2"]
        assert saved[B].pads == "[]" and saved[C].pads == "[]"

    async def test_block_stops_and_keeps_progress(self, tmp_path):
        out, fake = tmp_path / "pads.csv", FakeTime()
        session = FakeSession({A: FakeResponse(200, footprint(2)), B: FakeResponse(403), C: FakeResponse(200, footprint(1))})
        counts = await run(session, [A, B, C], {}, out, fake, save_every=100)
        assert counts["blocked"] and counts["requests"] == 2
        assert len(session.urls) == 2  # nothing after the refusal
        assert list(read_pads_csv(out)) == [A]  # saved on the way out, though under save_every

    async def test_failures_are_skipped_for_next_run(self, tmp_path):
        out, fake = tmp_path / "pads.csv", FakeTime()
        session = FakeSession({A: RuntimeError("timeout"), B: FakeResponse(500), C: FakeResponse(200, footprint(1))})
        counts = await run(session, [A, B, C], {}, out, fake)
        assert counts["failed"] == 2 and counts["added"] == 1
        assert list(read_pads_csv(out)) == [C]

    async def test_refresh_keeps_unchanged_dates(self, tmp_path):
        out, fake = tmp_path / "pads.csv", FakeTime()
        old_day = "2026-01-01T00:00:00Z"
        have = {A: PadsRow(A, pack_pads(script.parse_easyeda_footprint(footprint(2)["result"])["pads"]), old_day),
                B: PadsRow(B, "[]", old_day)}
        session = FakeSession({A: FakeResponse(200, footprint(2)), B: FakeResponse(200, footprint(1))})
        confirmed: dict[str, str] = {}
        state = tmp_path / "pads_state.json"
        counts = await run(session, [A, B], have, out, fake, confirmed=confirmed, state_path=state)
        assert counts["unchanged"] == 1 and counts["changed"] == 1
        saved = read_pads_csv(out)
        assert saved[A].fetched == old_day  # unchanged row: same line in the CSV
        assert saved[B].fetched != old_day
        assert set(script.load_state(state)) == {A, B}

    async def test_max_requests(self, tmp_path):
        out, fake = tmp_path / "pads.csv", FakeTime()
        session = FakeSession({A: FakeResponse(200, footprint(1)), B: FakeResponse(200, footprint(1))})
        counts = await run(session, [A, B], {}, out, fake, max_requests=1)
        assert counts["requests"] == 1 and len(session.urls) == 1

    def test_state_file_tolerates_garbage(self, tmp_path):
        state = tmp_path / "pads_state.json"
        assert script.load_state(state) == {}
        state.write_text("not json", encoding="utf-8")
        assert script.load_state(state) == {}
        script.save_state(state, {A: DAY})
        assert script.load_state(state) == {A: DAY}
