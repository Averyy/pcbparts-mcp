import json
import stat
import zlib
from datetime import timedelta

import pytest

from pcbparts_dashboard.store import Store, timestamp

AT = "2026-11-21T19:20:00Z"
LATER = "2026-11-21T20:20:00Z"


def test_database_is_private_persistent_and_wal(tmp_path):
    path = tmp_path / "nested/stats.db"
    with Store(path) as store:
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        assert store._connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        store.merge_day({"date": "2026-11-21", "calls": 3}, AT)
    path.chmod(0o644)
    with Store(path) as reopened:
        assert reopened.all_days() == [{"date": "2026-11-21", "calls": 3}]
        assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_insert_and_higher_count_replace(store):
    initial = {"date": "2026-11-21", "calls": 3, "apps": {"old": 3}}
    assert store.merge_day(initial, AT) == initial
    incoming = {"date": "2026-11-21", "calls": 5, "apps": {"new": 5}, "new_field": 12}
    assert store.merge_day(incoming, LATER) == incoming
    assert store.all_days() == [incoming]
    assert store.get_meta("warnings", []) == []


def test_lower_count_keeps_whole_record_and_warns(store):
    initial = {"date": "2026-11-21", "calls": 12, "tools": {"search": 12}}
    store.merge_day(initial, AT)
    assert store.merge_day({"date": "2026-11-21", "calls": 2, "new": True}, LATER) == initial
    assert store.all_days() == [initial]
    assert store._connection.execute("SELECT fetched_at FROM days").fetchone()[0] == AT
    warning = store.get_meta("warnings")[0]
    assert warning["at"] == LATER
    assert all(part in warning["message"] for part in ("2026-11-21", "12", "2"))


@pytest.mark.parametrize("stored, incoming, expected", [
    ({"key": {"app": 1}}, {}, {"app": 1}),
    ({"key": {"app": 1}}, {"key": None}, {"app": 1}),
    ({"key": {"app": 1}}, {"key": {}}, {"app": 1}),
    ({"key": [1, 2]}, {"key": []}, [1, 2]),
    ({"key": [1]}, {"key": {}}, [1]),
    ({"key": {"app": 1}}, {"key": []}, {"app": 1}),
    ({"key": {}}, {"key": []}, []),
    ({"key": []}, {"key": {}}, {}),
    ({"key": {"app": 1}}, {"key": {"other": 2}}, {"other": 2}),
    ({"key": [1]}, {"key": [2]}, [2]),
    ({"key": 4}, {"key": 0}, 0),
    ({"key": True}, {"key": False}, False),
    ({"key": "old"}, {"key": ""}, ""),
    ({"key": None}, {}, None),
])
def test_equal_count_field_preservation(store, stored, incoming, expected):
    base = {"date": "2026-11-21", "calls": 10}
    store.merge_day(base | stored, AT)
    original = base | incoming
    result = store.merge_day(original, LATER)
    assert result["key"] == expected
    assert original == base | incoming  # Merging never mutates caller input.


def test_missing_calls_are_preserved(store):
    store.merge_day({"date": "2026-11-21", "calls": 10}, AT)
    assert store.merge_day({"date": "2026-11-21", "extra": 1}, LATER)["calls"] == 10


def test_older_reply_with_fewer_calls_is_kept_out_without_a_warning(store):
    # An imported file saved before the stored fetch: fewer calls is expected, not a reset.
    initial = {"date": "2026-11-21", "calls": 12, "tools": {"search": 12}}
    store.merge_day(initial, LATER)
    assert store.merge_day({"date": "2026-11-21", "calls": 2}, AT) == initial
    assert store.all_days() == [initial]
    assert store._connection.execute("SELECT fetched_at FROM days").fetchone()[0] == LATER
    assert store.get_meta("warnings", []) == []
    # The same time counts as a reset: nothing says the reply is older.
    store.merge_day({"date": "2026-11-21", "calls": 3}, LATER)
    assert len(store.get_meta("warnings")) == 1


def test_only_last_twenty_warnings_are_kept(store):
    store.merge_day({"date": "2026-11-21", "calls": 100}, AT)
    for count in range(25):
        store.merge_day({"date": "2026-11-21", "calls": count}, LATER)
    warnings = store.get_meta("warnings")
    assert len(warnings) == 20
    assert "incoming calls 5 " in warnings[0]["message"]
    assert "incoming calls 24 " in warnings[-1]["message"]


def test_stats_store_raw_compressed_snapshot_even_after_reset(store, stats_reply):
    record = stats_reply["days"][0]
    store.merge_day(record | {"calls": record["calls"] + 1}, AT)
    assert store.save_stats(stats_reply, LATER) == 3
    at, date, data = store._connection.execute("SELECT fetched_at, date, data FROM snapshots").fetchone()
    assert (at, date) == (LATER, record["date"])
    assert isinstance(data, bytes)
    assert json.loads(zlib.decompress(data)) == record
    assert store.all_days()[-1]["calls"] == record["calls"] + 1
    assert store.get_meta("about") == stats_reply["about"]
    assert store.get_meta("latency_bounds_ms") == stats_reply["latency_bounds_ms"]


def test_pruning_45_days_keeps_daily_history_and_boundary(store, clock):
    cutoff = clock() - timedelta(days=45)
    samples = [cutoff - timedelta(seconds=1), cutoff, cutoff + timedelta(seconds=1)]
    for index, moment in enumerate(samples):
        record = {"date": moment.date().isoformat(), "calls": index}
        store.merge_day(record, timestamp(moment))
        store.add_snapshot(record, timestamp(moment))
        store.save_health({"sample": index}, timestamp(moment))
    store.prune(clock())
    assert [row[0] for row in store._connection.execute("SELECT fetched_at FROM snapshots ORDER BY fetched_at")] == [timestamp(t) for t in samples[1:]]
    assert [row[0] for row in store._connection.execute("SELECT fetched_at FROM health ORDER BY fetched_at")] == [timestamp(t) for t in samples[1:]]
    assert len(store.all_days()) == 1
    assert store.newest_health() == (timestamp(samples[-1]), {"sample": 2})
