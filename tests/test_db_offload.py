"""SQLite work must leave the event loop available to other requests."""

import asyncio
import time

import httpx
import pytest

from pcbparts_mcp import db, server
from pcbparts_mcp.boards_db import BoardsDatabase
from pcbparts_mcp.sensor_db import SensorDatabase


async def test_slow_search_keeps_loop_and_health_responsive(monkeypatch):
    database = db.get_db()
    original = database.search

    def slow_search(*args, **kwargs):
        time.sleep(0.35)
        return original(*args, **kwargs)

    monkeypatch.setattr(database, "search", slow_search)
    gaps = []
    health_latencies = []
    done = asyncio.Event()

    async def ticker():
        previous = time.perf_counter()
        while not done.is_set():
            await asyncio.sleep(0.01)
            now = time.perf_counter()
            gaps.append(now - previous)
            previous = now

    async def check_health():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.create_app()),
                                     base_url="http://localhost") as client:
            while not done.is_set():
                start = time.perf_counter()
                assert (await client.get("/health")).status_code == 200
                health_latencies.append(time.perf_counter() - start)
                await asyncio.sleep(0.01)

    ticker_task = asyncio.create_task(ticker())
    health_task = asyncio.create_task(check_health())
    await asyncio.sleep(0.03)
    try:
        results = await asyncio.gather(*(server.jlc_search(query="C2040", limit=1) for _ in range(8)))
        assert all(result["results"] for result in results)
        await asyncio.sleep(0.03)
    finally:
        done.set()
        await asyncio.gather(ticker_task, health_task)
    # Deliberately looser than the measured <100 ms target, but fails for one 350 ms DB call.
    assert max(gaps) < 0.25
    assert max(health_latencies) < 0.25


@pytest.mark.parametrize("handler,args,owner,method,reply", [
    (server.jlc_search_help, {"subcategory": "MOSFETs"}, db.get_db, "list_attributes", {"attributes": []}),
    (server.jlc_get_part, {"mpn": "LM358"}, db.get_db, "get_by_mpn", [{"lcsc": "C1"}]),
    (server.sensor_recommend, {"query": "BME280"}, server.get_sensor_db, "search", {"results": [], "total": 0}),
    (server.board_search, {"query": "usb"}, server.get_boards_db, "search", {"results": [], "total": 0}),
    (server.board_get, {"slug": "example"}, server.get_boards_db, "get_board", {"slug": "example"}),
    (server.get_design_rules, {"topic": "usb"}, lambda: server, "_get_design_rules", {"content": "example"}),
])
async def test_other_catalog_paths_run_off_loop(monkeypatch, handler, args, owner, method, reply):
    import threading

    loop_thread = threading.get_ident()

    def work(*args, **kwargs):
        assert threading.get_ident() != loop_thread
        return reply

    monkeypatch.setattr(owner(), method, work)
    result = await handler(**args)
    assert result == ({"mpn": "LM358", "total": 1, "results": reply}
                      if handler is server.jlc_get_part else reply)


@pytest.mark.parametrize("handler,args", [
    (server.board_get, {"slug": "missing-board"}),
    (server.sensor_recommend, {"query": "BME280"}),
    (server.get_design_rules, {"topic": "usb"}),
])
async def test_component_lock_waiters_do_not_starve_other_catalogs(monkeypatch, handler, args):
    import threading

    database = db.get_db()
    entered = threading.Event()
    release = threading.Event()

    def gated_lookup(*args, **kwargs):
        with database._conn_lock:
            entered.set()
            assert release.wait(timeout=5)
            return []

    monkeypatch.setattr(database, "get_by_mpn", gated_lookup)
    tasks = [asyncio.create_task(server.jlc_get_part(mpn="LM358")) for _ in range(8)]
    try:
        for _ in range(200):
            if entered.is_set():
                break
            await asyncio.sleep(0.01)
        assert entered.is_set()
        await asyncio.sleep(0.05)
        result = await asyncio.wait_for(handler(**args), timeout=0.75)
        assert isinstance(result, dict)
        assert not release.is_set()
    finally:
        release.set()
        await asyncio.gather(*tasks)


async def test_offloaded_tools_preserve_schemas():
    from fastmcp.tools import Tool

    tools = await server.mcp.list_tools()
    by_name = {tool.name: tool for tool in tools}
    for handler in (server.jlc_search, server.jlc_search_help, server.sensor_recommend,
                    server.get_design_rules, server.board_search, server.board_get):
        original = Tool.from_function(handler.__wrapped__)
        published = by_name[handler.__name__]
        assert published.parameters == original.parameters
        assert published.description == original.description


@pytest.mark.parametrize("pool_name,max_workers", [
    ("COMPONENT_POOL", 2), ("BOARD_POOL", 1), ("SENSOR_POOL", 1), ("RULES_POOL", 1),
])
async def test_worker_limit_survives_cancellation(pool_name, max_workers):
    import threading
    from pcbparts_mcp import db_worker

    pool = getattr(db_worker, pool_name)

    release = threading.Event()
    lock = threading.Lock()
    active = peak = 0
    saturated = threading.Event()

    def work():
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
            if active == max_workers:
                saturated.set()
        try:
            assert release.wait(timeout=5)
        finally:
            with lock:
                active -= 1

    first = [asyncio.create_task(db_worker.run_db(pool, work)) for _ in range(max_workers * 2)]
    second = []
    try:
        for _ in range(200):
            if saturated.is_set():
                break
            await asyncio.sleep(0.01)
        assert saturated.is_set()
        for task in first:
            task.cancel()
        await asyncio.gather(*first, return_exceptions=True)
        second = [asyncio.create_task(db_worker.run_db(pool, work)) for _ in range(max_workers * 2)]
        await asyncio.sleep(0.05)
        assert peak == max_workers
    finally:
        release.set()
        await asyncio.gather(*first, *second, return_exceptions=True)
    assert peak <= max_workers


@pytest.mark.parametrize("factory,method,args", [
    (db.ComponentDatabase, "get_by_lcsc", ("C2040",)),
    (BoardsDatabase, "get_board", ("missing-board",)),
    (SensorDatabase, "search", ("BME280",)),
])
def test_connection_use_and_close_are_serialized(factory, method, args):
    from concurrent.futures import ThreadPoolExecutor
    import sqlite3
    import threading

    database = factory()
    database._ensure_db()
    entered = threading.Event()
    release = threading.Event()
    closed = threading.Event()
    active = peak = 0
    lock = threading.Lock()

    def trace(sql):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        try:
            entered.set()
            assert release.wait(timeout=5)
            time.sleep(0.005)
        finally:
            with lock:
                active -= 1

    # The catalogs are query-only, including components.db's seeded EasyEDA table.
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        database._conn.execute("CREATE TABLE offload_write_must_fail (id INTEGER)")
    database._conn.set_trace_callback(trace)

    def close():
        database.close()
        closed.set()

    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            reads = [pool.submit(getattr(database, method), *args) for _ in range(3)]
            try:
                assert entered.wait(timeout=2)
                closing = pool.submit(close)
                assert not closed.wait(timeout=0.05)
            finally:
                release.set()
            for read in reads:
                read.result(timeout=5)
            closing.result(timeout=5)
        assert peak == 1
        assert closed.is_set()
    finally:
        database.close()
