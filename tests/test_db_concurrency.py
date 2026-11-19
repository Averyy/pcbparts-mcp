"""Component reads run concurrently (0.10.2): each COMPONENT_POOL worker thread queries on its own
read connection, with no lock held while a query runs; initialization and close() still happen
once and safely. Threads are coordinated with events and barriers only; every timeout is a hang
guard, never a measurement (see test_windows_safe.py).

Under 0.10.1's design (one connection behind a reentrant lock) the overlap tests fail: the second
query waits for the lock, so the barrier or the wait_for times out."""

import asyncio
import json
import queue
import sqlite3
import sys
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pytest

from conftest import write_catalog_category
from pcbparts_mcp import db as db_module
from pcbparts_mcp import db_worker, server
from pcbparts_mcp.db import ComponentDatabase
from pcbparts_mcp.db_worker import COMPONENT_POOL, run_db

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import build_database  # noqa: E402

HANG = 30  # seconds: only reached when a test is failing


def first_statement_meets(barrier: threading.Barrier, met: list) -> Callable[[str], None]:
    """A trace callback: each thread's first statement waits inside SQLite (in sqlite3_step, on its
    own connection) until the barrier's other parties are inside theirs too."""
    seen = threading.local()

    def trace(sql):
        if getattr(seen, "done", False):
            return
        seen.done = True
        try:
            barrier.wait(timeout=HANG)
            met.append(True)
        except threading.BrokenBarrierError:
            met.append(False)
    return trace


@pytest.fixture
def tiny(tmp_path, monkeypatch):
    """A three-part catalog and a database built from it; builds through ComponentDatabase are
    counted (calls)."""
    rows = [{"l": code, "m": mpn, "f": "Maker", "p": "0402", "s": 5000, "t": "b", "c": 2, "$": 0.1,
             "d": "10k resistor", "a": [["Resistance", "10kΩ"]]}
            for code, mpn in [("C2", "RES-A"), ("C3", "RES-B"), ("C4", "RES-C")]]
    write_catalog_category(tmp_path, "resistors", rows)
    (tmp_path / "subcategories.json").write_text(json.dumps({
        "2": {"name": "Chip Resistor - Surface Mount", "category_id": 1, "category_name": "Resistors"},
    }), encoding="utf-8")
    path = tmp_path / "components.db"
    build_database(tmp_path, path, verbose=False)
    calls = {"build": 0, "load": 0}
    load = db_module.load_caches

    def counted_build(data_dir, db_path):
        calls["build"] += 1
        build_database(data_dir, db_path, verbose=False)

    def counted_load(conn):
        calls["load"] += 1
        return load(conn)

    monkeypatch.setattr(db_module, "build_database", counted_build)
    monkeypatch.setattr(db_module, "load_caches", counted_load)
    return type("Tiny", (), {"path": path, "data_dir": tmp_path, "calls": calls})


def delete_database(path: Path) -> None:
    """Delete the database and its WAL files: fails on Windows while any connection is open."""
    for name in (path.name, path.name + "-wal", path.name + "-shm"):
        (path.parent / name).unlink(missing_ok=True)
    assert not path.exists()


class WatchedCondition(threading.Condition):
    """ComponentDatabase's state condition, reporting which thread starts waiting on it."""
    def __init__(self):
        super().__init__(threading.RLock())
        self.waits = queue.Queue()

    def wait(self, timeout=None):
        self.waits.put(threading.current_thread().name)
        return super().wait(timeout)


async def test_two_queries_are_inside_sqlite_at_once():
    """Each query blocks inside SQLite until the other's has started: only possible when two
    worker threads query at the same moment, each on its own connection."""
    database = ComponentDatabase()
    met = []
    database.set_trace_callback(first_statement_meets(threading.Barrier(2), met))
    try:
        first, second = await asyncio.gather(run_db(COMPONENT_POOL, database.get_by_lcsc, "C2040"),
                                             run_db(COMPONENT_POOL, database.get_by_mpn, "LM358DR"))
        assert met == [True, True]
        assert first["lcsc"] == "C2040" and second
        assert len(database._connections) == 2  # one per worker thread
    finally:
        await run_db(COMPONENT_POOL, database.close)


async def test_quick_lookup_finishes_while_a_slow_search_runs():
    """One worker is held inside a search's query; a part lookup submitted through run_db still
    completes, on another worker, before the search is let go."""
    database = ComponentDatabase()
    expected = database.search(query="LM358", limit=5)
    slow, held, release = threading.local(), threading.Event(), threading.Event()

    def trace(sql):
        if getattr(slow, "on", False) and not release.is_set():
            held.set()
            assert release.wait(timeout=HANG)

    def slow_search():
        slow.on = True
        try:
            return database.search(query="LM358", limit=5)
        finally:
            slow.on = False

    database.set_trace_callback(trace)
    search = asyncio.ensure_future(run_db(COMPONENT_POOL, slow_search))
    try:
        assert await asyncio.to_thread(held.wait, HANG)
        part = await asyncio.wait_for(run_db(COMPONENT_POOL, database.get_by_mpn, "LM358DR"), timeout=HANG)
        assert part and part[0]["model"] == "LM358DR"
        assert not search.done() and not release.is_set()
    finally:
        release.set()
        result = await search
        await run_db(COMPONENT_POOL, database.close)
    assert result == expected


SEARCHES = [
    {"query": "mosfet n-channel 30v 5a sot-23"},
    {"query": "usb c connector 16 pin"},
    {"query": "tvs diode 5v sot-23"},
    {"query": "LDO 3.3V 500mA"},
    {"query": "buck converter 5v 3a"},
    {"query": "fuse 1206"},  # fills the fuse-package cache
    {"query": "buck converter", "package": "QFN-16-EP(3x3)"},  # fills the package catalog
    {"query": "10k resistor 0603", "sort_spec": "RDS(on)"},  # fills the spec-sort part types
    {"subcategory_name": "MOSFETs", "sort_spec": "RDS(on)", "sort_order": "asc", "limit": 5},
    {"query": "100nF 0402 capacitor", "spec_filters": [{"name": "Voltage", "op": ">=", "value": "25V"}]},
    {"query": "mosfet", "spec_filters": [{"name": "Operating Temperature", "op": "<=", "value": "-40"}]},
]
MPNS = ["LM358DR", "NE555DR", "AMS1117-3.3", "BSS138", "AO3400A", "STM32F103C8T6", "CH340G", "TP4056",
        "SS34", "USBLC6-2SC6"]


def _timeless(value):
    """A reply without its elapsed_ms fields (the only ones that vary run to run)."""
    if isinstance(value, dict):
        return {k: _timeless(v) for k, v in value.items() if k != "elapsed_ms"}
    if isinstance(value, list):
        return [_timeless(v) for v in value]
    return value


async def test_concurrent_answers_match_serial(monkeypatch):
    """Real searches and part lookups through the tools give the same replies when they run on
    three workers at once (the first three statements meet inside SQLite, and every cache starts
    empty) as one at a time on another fresh instance."""
    calls = [lambda c=c: server.jlc_search(**c) for c in SEARCHES]
    calls += [lambda m=m: server.jlc_get_part(mpn=m) for m in MPNS]

    concurrent_db = ComponentDatabase()
    met = []
    concurrent_db.set_trace_callback(first_statement_meets(threading.Barrier(3), met))
    monkeypatch.setattr(db_module, "_db", concurrent_db)
    try:
        concurrent = await asyncio.gather(*(call() for call in calls))
        assert met == [True, True, True]
        assert len(concurrent_db._connections) == 3
        filled = concurrent_db._search_engine
        assert filled._package_names and filled._fuse_package_types and filled._sort_spec_subcategories
    finally:
        await run_db(COMPONENT_POOL, concurrent_db.close)

    serial_db = ComponentDatabase()
    monkeypatch.setattr(db_module, "_db", serial_db)
    try:
        serial = [await call() for call in calls]
    finally:
        await run_db(COMPONENT_POOL, serial_db.close)
    assert all(reply.get("results") for reply in serial)
    assert _timeless(concurrent) == _timeless(serial)


def test_initialization_and_build_happen_once(tiny, monkeypatch):
    """Three threads hit a fresh instance whose database file is missing at the same moment: the
    database is built once and loaded once, and each thread then reads on its own connection."""
    delete_database(tiny.path)
    database = ComponentDatabase(db_path=tiny.path, data_dir=tiny.data_dir)
    entered = threading.Semaphore(0)
    begin = database._begin

    def counted_begin():
        entered.release()
        return begin()

    database._begin = counted_begin
    build = db_module.build_database

    def build_after_all_entered(data_dir, db_path):
        for _ in range(3):  # every thread has started its call before the build finishes
            assert entered.acquire(timeout=HANG)
        build(data_dir, db_path)

    monkeypatch.setattr(db_module, "build_database", build_after_all_entered)
    start = threading.Barrier(3)

    def read():
        start.wait(timeout=HANG)
        return database.get_by_lcsc("C3")

    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            answers = [f.result(timeout=HANG) for f in [pool.submit(read) for _ in range(3)]]
        assert [a["model"] for a in answers] == ["RES-B"] * 3
        assert tiny.calls == {"build": 1, "load": 1}
        assert len(database._connections) == 3
    finally:
        database.close()
    delete_database(tiny.path)


def test_close_closes_every_threads_connection(tiny):
    """close() closes the connection of every thread that read, wherever it is called from, so the
    database file can then be deleted; a later call opens it again (here: builds it again)."""
    database = ComponentDatabase(db_path=tiny.path, data_dir=tiny.data_dir)
    start = threading.Barrier(3)

    def read():
        start.wait(timeout=HANG)
        return database.get_by_lcsc("C2")["model"]

    with ThreadPoolExecutor(max_workers=3) as pool:
        assert [f.result(timeout=HANG) for f in [pool.submit(read) for _ in range(3)]] == ["RES-A"] * 3
        connections = list(database._connections)
        assert len(connections) == 3
        database.close()  # from a thread that never read
        for conn in connections:
            with pytest.raises(sqlite3.ProgrammingError, match="closed"):
                conn.execute("SELECT 1")
        assert database._connections == [] and database._conn is None
        delete_database(tiny.path)
        # As before 0.10.2: the next call initializes again, building the missing database
        again = [pool.submit(lambda: database.get_by_lcsc("C4")["model"]) for _ in range(3)]
        assert [f.result(timeout=HANG) for f in again] == ["RES-C"] * 3
    assert tiny.calls["build"] == 1
    database.close()
    delete_database(tiny.path)


def test_close_waits_for_a_running_query_and_holds_back_the_next(tiny):
    """close() while one thread is inside a query and another is about to start one: close waits
    for the running query (its connection isn't closed under it), the next query waits for close,
    then runs on a new connection."""
    database = ComponentDatabase(db_path=tiny.path, data_dir=tiny.data_dir)
    database._state = WatchedCondition()
    held, release = threading.Event(), threading.Event()

    def trace(sql):
        if threading.current_thread().name == "running" and not release.is_set():
            held.set()
            assert release.wait(timeout=HANG)

    database.set_trace_callback(trace)
    answers = {}

    def call(name, code):
        answers[name] = database.get_by_lcsc(code)["model"]

    running = threading.Thread(target=call, args=("running", "C2"), name="running")
    closer = threading.Thread(target=database.close, name="closer")
    waiting = threading.Thread(target=call, args=("waiting", "C3"), name="waiting")
    threads = [running, closer, waiting]
    try:
        running.start()
        assert held.wait(timeout=HANG)
        first = list(database._connections)
        closer.start()
        assert database._state.waits.get(timeout=HANG) == "closer"  # waiting for the running query
        waiting.start()
        assert database._state.waits.get(timeout=HANG) == "waiting"  # waiting for close
        assert closer.is_alive() and "running" not in answers and "waiting" not in answers
        assert database._connections == first and database._generation == 0
    finally:
        release.set()
        for thread in threads:
            if thread.ident is not None:
                thread.join(timeout=HANG)
    assert not any(thread.is_alive() for thread in threads)
    assert answers == {"running": "RES-A", "waiting": "RES-B"}
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        first[0].execute("SELECT 1")
    assert database._generation == 1 and len(database._connections) == 1
    assert database._connections[0] is not first[0]
    database.close()
    delete_database(tiny.path)


async def test_repeated_lifespans_reopen_each_workers_connection(tiny):
    """init, close, init again on the real pool (as repeated app lifespans do): every round each
    worker gets a new connection, and the previous round's are closed."""
    database = ComponentDatabase(db_path=tiny.path, data_dir=tiny.data_dir)
    previous = []
    for _ in range(3):
        met = []
        database.set_trace_callback(first_statement_meets(threading.Barrier(3), met))
        answers = await asyncio.gather(*(run_db(COMPONENT_POOL, database.get_by_mpn, "RES-A") for _ in range(3)))
        assert met == [True, True, True]
        assert [a[0]["lcsc"] for a in answers] == ["C2"] * 3
        current = list(database._connections)
        assert len(current) == 3 and not any(conn in previous for conn in current)
        await run_db(COMPONENT_POOL, database.close)
        for conn in current:
            with pytest.raises(sqlite3.ProgrammingError, match="closed"):
                conn.execute("SELECT 1")
        previous = current
    delete_database(tiny.path)
    assert tiny.calls == {"build": 0, "load": 3}


async def test_health_shows_a_running_query():
    """/health's database_pressure counts the job a worker is running (run_db's real pressure)."""
    database = ComponentDatabase()
    held, release = threading.Event(), threading.Event()
    slow = threading.local()

    def trace(sql):
        if getattr(slow, "on", False) and not release.is_set():
            held.set()
            assert release.wait(timeout=HANG)

    def held_lookup():
        slow.on = True
        try:
            return database.get_by_lcsc("C2040")
        finally:
            slow.on = False

    database.set_trace_callback(trace)
    job = asyncio.ensure_future(run_db(COMPONENT_POOL, held_lookup))
    try:
        assert await asyncio.to_thread(held.wait, HANG)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.create_app()),
                                     base_url="http://localhost") as client:
            reply = await client.get("/health")
        shown = reply.json()["database_pressure"]
        assert reply.status_code == 200 and shown["running"] >= 1 and shown["longest_running_seconds"] >= 0
        assert db_worker.database_pressure.running()[COMPONENT_POOL].running >= 1
    finally:
        release.set()
        assert (await job)["lcsc"] == "C2040"
        await run_db(COMPONENT_POOL, database.close)
