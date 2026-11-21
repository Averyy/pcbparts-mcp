"""0.10.5: the distributor store's one connection is shared by the event loop and the component
pool's workers (jlc_get_parts reads lifecycle inside its job since 0.10.4). Python's sqlite3 shares
a prepared statement between cursors running the same SQL, so unlocked readers got another part's
reading, none, or a row of NULLs (prod: TypeError in readings(), jlc_get_parts failed). Fixed
iteration counts, no timing."""

import threading
from collections import Counter

import pytest

from pcbparts_mcp.distributor_store import DistributorStore
from pcbparts_mcp.lifecycle import Reading

NOW = 1_795_000_000.0
PARTS = [f"PART{i:03d}-X" for i in range(100)]


def _maker(i: int) -> str:
    return f"Maker{i}"


def _run(threads: list[threading.Thread]) -> None:
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def test_concurrent_reads_and_writes_get_their_own_rows(tmp_path):
    store = DistributorStore(tmp_path / "distributor.db", clock=lambda: NOW)
    try:
        assert store.put_readings([Reading(mpn, _maker(i), "mouser", "obsolete" if i % 2 else "active", None, NOW)
                                   for i, mpn in enumerate(PARTS)])
        for mpn in PARTS:
            assert store.put_answer("mouser", mpn, {"mpn": mpn}, True)
        results: Counter[str] = Counter()
        tally = threading.Lock()

        def count(kind: str) -> None:
            with tally:
                results[kind] += 1

        def read_lifecycle(start: int) -> None:  # a jlc_get_parts job on a component worker
            for step in range(3000):
                i = (start + 7 * step) % len(PARTS)
                try:
                    got = store.readings(PARTS[i])
                except Exception as e:  # noqa: BLE001 - the bug raised TypeError/ValueError/SystemError
                    count(f"raised {type(e).__name__}")
                    continue
                own = [(r.mpn, r.maker) for r in got] == [(PARTS[i], _maker(i))]
                count("ok" if own else "wrong")

        def read_answers() -> None:  # the event loop's Mouser/DigiKey lookups
            for step in range(3000):
                mpn = PARTS[step % len(PARTS)]
                got = store.get_answer("mouser", mpn)
                count("ok" if got is not None and got[0] == {"mpn": mpn} else "wrong")

        def write() -> None:  # fresh readings and answers arriving meanwhile
            for step in range(1500):
                i = step % len(PARTS)
                store.put_readings([Reading(PARTS[i], _maker(i), "mouser", "obsolete" if i % 2 else "active",
                                            None, NOW)])
                store.put_answer("mouser", PARTS[i], {"mpn": PARTS[i]}, True)

        _run([threading.Thread(target=read_lifecycle, args=(start,)) for start in range(3)]
             + [threading.Thread(target=read_answers), threading.Thread(target=write)])
        assert results == Counter(ok=4 * 3000)
    finally:
        store.close()


def test_in_memory_store_is_locked_too():
    store = DistributorStore(None, clock=lambda: NOW)
    try:
        assert not store.persistent
        assert store.put_readings([Reading(mpn, _maker(i), "digikey", "active", None, NOW)
                                   for i, mpn in enumerate(PARTS)])
        wrong: list[str] = []

        def read(start: int) -> None:
            for step in range(3000):
                i = (start + 3 * step) % len(PARTS)
                try:
                    got = store.readings(PARTS[i])
                except Exception as e:  # noqa: BLE001
                    wrong.append(type(e).__name__)
                    continue
                if [(r.mpn, r.maker) for r in got] != [(PARTS[i], _maker(i))]:
                    wrong.append("wrong")

        _run([threading.Thread(target=read, args=(start,)) for start in range(4)])
        assert wrong == []
    finally:
        store.close()


class _ClosedFirst:
    """The store's lock, but close() wins the race: the connection is gone once it's held."""

    def __init__(self, store):
        self.store, self.lock = store, store._lock

    def __enter__(self):
        conn, self.store._conn = self.store._conn, None
        if conn is not None:
            conn.close()
        return self.lock.__enter__()

    def __exit__(self, *exc):
        return self.lock.__exit__(*exc)


@pytest.mark.parametrize("use, expected", [
    (lambda s: s.readings(PARTS[0]), []), (lambda s: s.get_answer("mouser", PARTS[0]), None),
    (lambda s: s.put_answer("mouser", PARTS[0], {}, True), False),
    (lambda s: s.put_readings([Reading(PARTS[0], "M", "mouser", "active", None, NOW)]), False),
    (lambda s: s.prune(), None), (lambda s: s.counts()["answers"], 0),
], ids=["readings", "get_answer", "put_answer", "put_readings", "prune", "counts"])
def test_closed_between_check_and_use_is_a_miss_not_an_error(use, expected):
    store = DistributorStore(None, clock=lambda: NOW)
    store._lock = _ClosedFirst(store)
    assert use(store) == expected
