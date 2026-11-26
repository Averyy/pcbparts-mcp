"""Private per-address restart counts: fake UTC clocks, no distributor requests."""

import hmac
import json
import logging
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastmcp import Client

from pcbparts_mcp import cache, server
from pcbparts_mcp.cache import AddressDailyQuota, CARRY_MIN, DailyQuota

from test_distributor_quota import Clock, MIDNIGHT


ADDRESS = "192.0.2.1"
OTHER = "192.0.2.2"
IPV6 = "2001:db8:1234:5678::1"


@pytest.fixture
def clock():
    return Clock()


def quota(clock, **kwargs):
    return AddressDailyQuota(1000, key=server._address_key, clock=clock, **kwargs)


def test_same_day_roundtrip_threshold_and_immediate_cap(clock, tmp_path):
    path = tmp_path / "counts.json"
    before = quota(clock)
    before.record(ADDRESS, 1000)
    before.record(OTHER, CARRY_MIN)
    before.record("192.0.2.3", CARRY_MIN - 1)
    before.save(path)

    after = quota(clock)
    assert after.load(path) == 2
    assert not path.exists()
    assert after.capped(ADDRESS)
    assert after.remaining(OTHER) == 900
    assert after.remaining("192.0.2.3") == 1000


def test_unclaimed_counts_survive_another_restart(clock, tmp_path):
    path = tmp_path / "counts.json"
    before = quota(clock)
    before.record(ADDRESS, 200)
    before.record(OTHER, 1000)
    before.save(path)
    after = quota(clock)
    assert after.load(path) == 2
    after.record(ADDRESS, 25)  # record can claim the count without remaining being called first
    assert after.remaining(ADDRESS) == 775
    after.save(path)
    again = quota(clock)
    assert again.load(path) == 2
    assert again.remaining(ADDRESS) == 775
    assert again.remaining(ADDRESS) == 775  # a claimed count is never added twice
    assert again.capped(OTHER)


def test_file_contains_only_keyed_hashes_and_ipv6_group_still_matches(clock, tmp_path):
    path = tmp_path / "counts.json"
    before = quota(clock)
    before.record(ADDRESS, 100)
    before.record(IPV6, 1000)
    before.save(path)
    text = path.read_text(encoding="utf-8")
    assert all(address not in text for address in (ADDRESS, IPV6, server._address_key(IPV6)))
    data = json.loads(text)
    assert set(data) == {"date", "secret", "counts"}
    assert data["date"] == "2026-10-16"
    secret = bytes.fromhex(data["secret"])
    assert len(secret) == 32
    assert data["counts"] == {
        hmac.new(secret, server._address_key(address).encode("utf-8"), "sha256").hexdigest(): count
        for address, count in ((ADDRESS, 100), (IPV6, 1000))
    }
    after = quota(clock)
    assert after.load(path) == 2
    assert after.capped("2001:db8:1234:5678::abcd")
    assert after.remaining("2001:db8:1234:5679::1") == 1000


def test_stale_file_is_deleted_without_carrying_or_warning(clock, tmp_path, caplog):
    path = tmp_path / "counts.json"
    before = quota(clock)
    before.record(ADDRESS, 1000)
    before.save(path)
    clock.now = MIDNIGHT
    after = quota(clock)
    assert after.load(path) == 0
    assert not path.exists()
    assert after.remaining(ADDRESS) == 1000
    assert not caplog.records


def test_day_change_drops_live_and_unclaimed_counts_and_rotates_secret(clock, tmp_path):
    path = tmp_path / "counts.json"
    before = quota(clock)
    before.record(ADDRESS, 1000)
    before.record(OTHER, 1000)
    before.save(path)
    after = quota(clock)
    assert after.load(path) == 2
    assert after._secret == before._secret
    assert after.capped(ADDRESS)
    after.save(path)
    clock.now = MIDNIGHT
    after.reset_if_due()
    assert not after._counts and not after._carried
    assert len(after._secret) == 32 and after._secret != before._secret
    assert after.remaining(ADDRESS) == after.remaining(OTHER) == 1000
    after.save(path)
    assert not path.exists()


@pytest.mark.parametrize("limit", [0, 1000], ids=["off", "small"])
def test_no_qualifying_counts_removes_stale_file(clock, tmp_path, limit):
    path = tmp_path / "counts.json"
    path.write_text("stale", encoding="utf-8")
    day = AddressDailyQuota(limit, key=server._address_key, clock=clock)
    day.record(ADDRESS, 99)
    day.save(path)
    assert not path.exists()
    assert not path.with_name(path.name + ".tmp").exists()


def test_exempt_callers_are_never_written(clock, tmp_path):
    path = tmp_path / "counts.json"
    day = AddressDailyQuota(1000, key=lambda ip: None if ip == ADDRESS else ip, clock=clock)
    day.record(None, 1000)
    day.record(ADDRESS, 1000)
    assert day.remaining(ADDRESS) is None and day.remaining(None) is None
    day.save(path)
    assert not path.exists()
    day.record(OTHER, 100)
    day.save(path)
    assert list(json.loads(path.read_text(encoding="utf-8"))["counts"].values()) == [100]


def test_disabled_quota_consumes_file_without_restoring(clock, tmp_path):
    path = tmp_path / "counts.json"
    before = quota(clock)
    before.record(ADDRESS, 1000)
    before.save(path)
    after = AddressDailyQuota(0, key=server._address_key, clock=clock)
    assert after.load(path) == 0
    assert not path.exists() and not after._carried
    assert after.remaining(ADDRESS) is None


def test_carried_and_live_counts_share_the_table_bound(clock, tmp_path):
    path = tmp_path / "counts.json"
    before = quota(clock)
    for address in (ADDRESS, OTHER, "192.0.2.3"):
        before.record(address, 1000)
    before.save(path)
    after = quota(clock, max_addresses=2)
    assert after.load(path) == 2
    assert after.capped(ADDRESS)
    assert after.remaining("192.0.2.3") == 1000
    after.record("192.0.2.4", 100)
    assert after.remaining(OTHER) == 1000  # the oldest unclaimed entry was dropped
    assert after.capped(ADDRESS)
    after.save(path)
    assert len(json.loads(path.read_text(encoding="utf-8"))["counts"]) == 2


def test_a_full_table_drops_a_small_live_count_before_a_busy_carried_one(clock, tmp_path):
    path = tmp_path / "counts.json"
    before = quota(clock)
    before.record(ADDRESS, 900)
    before.save(path)
    after = quota(clock, max_addresses=2)
    assert after.load(path) == 1
    after.record("192.0.2.3", 1)
    after.record("192.0.2.4", 1)  # full: the live 192.0.2.3 (1 lookup) goes, not the carried 900
    assert after.remaining(ADDRESS) == 100
    assert after.remaining("192.0.2.3") == 1000


@pytest.mark.parametrize("bad", [
    "{", "[]", "{}", "null",
], ids=["json", "list", "missing", "null"])
def test_corrupt_file_warns_once_and_is_deleted(clock, tmp_path, caplog, bad):
    path = tmp_path / "counts.json"
    path.write_text(bad, encoding="utf-8")
    assert quota(clock).load(path) == 0
    assert not path.exists()
    assert len(caplog.records) == 1 and caplog.records[0].levelno == logging.WARNING


@pytest.mark.parametrize(("field", "value"), [
    ("date", "yesterday"), ("date", 20261016),
    ("secret", None), ("secret", "ab"), ("secret", "z" * 64),
    ("secret", "ab" * 31 + "  "), ("counts", []),
    ("counts", {ADDRESS: 100}), ("counts", {"z" * 64: 100}),
    ("counts", {"cd" * 32: True}), ("counts", {"cd" * 32: "100"}),
    ("counts", {"cd" * 32: 100.0}), ("counts", {"cd" * 32: 99}),
    ("counts", {"cd" * 32: -100}),
], ids=["date", "date-int", "null-key", "short-key", "bad-key", "space-key", "counts-list",
        "raw-ip", "bad-hash", "bool", "string", "float", "small", "negative"])
def test_invalid_shape_warns_and_is_deleted(clock, tmp_path, caplog, field, value):
    path = tmp_path / "counts.json"
    data = {"date": "2026-10-16", "secret": "ab" * 32, "counts": {"cd" * 32: 100}}
    data[field] = value
    path.write_text(json.dumps(data), encoding="utf-8")
    after = quota(clock)
    assert after.load(path) == 0
    assert not path.exists() and not after._carried
    assert len(caplog.records) == 1 and caplog.records[0].levelno == logging.WARNING
    assert ADDRESS not in caplog.text


def test_missing_file_is_quiet(clock, tmp_path, caplog):
    assert quota(clock).load(tmp_path / "missing.json") == 0
    assert not caplog.records


def test_load_removes_an_abandoned_temp_file(clock, tmp_path, caplog):
    path = tmp_path / "counts.json"
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text("interrupted write", encoding="utf-8")
    assert quota(clock).load(path) == 0
    assert not tmp.exists()
    assert not caplog.records


def test_unreadable_file_warns_and_is_still_deleted(clock, tmp_path, monkeypatch, caplog):
    path = tmp_path / "counts.json"
    path.write_text("unreadable", encoding="utf-8")

    def refuse(*args, **kwargs):
        raise PermissionError("read denied")

    monkeypatch.setattr(Path, "read_text", refuse)
    assert quota(clock).load(path) == 0
    assert not path.exists()
    assert len(caplog.records) == 1 and caplog.records[0].levelno == logging.WARNING


def test_unwritable_path_only_warns(clock, tmp_path, caplog):
    parent = tmp_path / "file"
    parent.write_text("not a directory", encoding="utf-8")
    day = quota(clock)
    day.record(ADDRESS, 1000)
    day.save(parent / "counts.json")
    assert day.capped(ADDRESS)
    assert len(caplog.records) == 1 and caplog.records[0].levelno == logging.WARNING


@pytest.mark.parametrize("failure", ["open", "dump", "replace"])
def test_failed_save_preserves_previous_file_and_removes_temp(clock, tmp_path, monkeypatch, caplog, failure):
    path = tmp_path / "counts.json"
    day = quota(clock)
    day.record(ADDRESS, 100)
    day.save(path)
    previous = path.read_text(encoding="utf-8")
    day.record(ADDRESS, 100)

    def refuse(*args, **kwargs):
        raise OSError("write failed")

    target, name = {"open": (cache.private_files, "private_open"),
                    "dump": (cache.json, "dump"), "replace": (cache.os, "replace")}[failure]
    monkeypatch.setattr(target, name, refuse)
    day.save(path)
    assert path.read_text(encoding="utf-8") == previous
    assert not path.with_name(path.name + ".tmp").exists()
    assert len(caplog.records) == 1 and caplog.records[0].levelno == logging.WARNING


def test_failed_load_deletion_only_warns(clock, tmp_path, monkeypatch, caplog):
    path = tmp_path / "counts.json"
    day = quota(clock)
    day.record(ADDRESS, 1000)
    day.save(path)

    def refuse(*args, **kwargs):
        raise PermissionError("delete denied")

    monkeypatch.setattr(Path, "unlink", refuse)
    after = quota(clock)
    assert after.load(path) == 1
    assert after.capped(ADDRESS)
    assert len(caplog.records) == 1 and caplog.records[0].levelno == logging.WARNING


@pytest.mark.skipif(os.name == "nt", reason="POSIX file modes")
def test_private_permissions_from_first_byte_and_after_replace(clock, tmp_path, monkeypatch):
    path = tmp_path / "counts.json"
    tmp = path.with_name(path.name + ".tmp")
    day = quota(clock)
    day.record(ADDRESS, 1000)
    original_dump = cache.json.dump

    def check_private(data, out):
        assert tmp.stat().st_mode & 0o777 == 0o600
        assert out.tell() == 0  # the empty file is private before any count or secret is written
        original_dump(data, out)

    monkeypatch.setattr(cache.json, "dump", check_private)
    day.save(path)
    assert path.stat().st_mode & 0o777 == 0o600
    path.chmod(0o644)
    tmp.write_text("leftover", encoding="utf-8")
    tmp.chmod(0o644)
    day.save(path)
    assert path.stat().st_mode & 0o777 == 0o600
    assert not tmp.exists()


@pytest.mark.parametrize("persist", [True, False], ids=["disk", "memory"])
async def test_lifespan_loads_then_saves_after_lookups_stop(clock, tmp_path, monkeypatch, caplog, persist):
    path = tmp_path / "distributor_address_counts.json"
    if persist:
        before = quota(clock)
        before.record(ADDRESS, 998)
        before.save(path)
    monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", str(tmp_path / "quota.json") if persist else "")
    monkeypatch.setattr(server, "DISTRIBUTOR_DAILY_PER_ADDRESS", 1000)  # as quota(): the order is tested, not the default
    monkeypatch.setattr(server, "MOUSER_API_KEY", "test-key")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "test-id")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(server, "ANTHROPIC_IP_RANGES", [])
    monkeypatch.setattr(server, "OPENAI_IP_RANGES_FILE", "")
    monkeypatch.setattr(server, "AddressDailyQuota", lambda *args, **kw: AddressDailyQuota(*args, clock=clock, **kw))
    monkeypatch.setattr(server, "DailyQuota", lambda *args, **kw: DailyQuota(*args, clock=clock, **kw))
    monkeypatch.setattr(server, "_address_daily", None)
    events = []
    tally = SimpleNamespace(flush=lambda: events.append("tally"))
    monkeypatch.setattr(server, "_caller_tallies", lambda: [tally])

    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.server"):
        async with Client(server.mcp):
            day = server._address_daily
            assert all(pool.address_daily is day for pool in server._distributor_quotas.values())
            assert day.remaining(ADDRESS) == (2 if persist else 1000)
            assert not path.exists()
            if not persist:
                day.record(ADDRESS, 998)

            def wrap_stop(client, name, method):
                stop = getattr(client, method)
                recorded = False

                async def tracked_stop():
                    nonlocal recorded
                    await stop()
                    if not recorded:
                        day.record(ADDRESS)
                        events.append(name)
                        recorded = True

                monkeypatch.setattr(client, method, tracked_stop)

            wrap_stop(server._mouser_client, "mouser", "close")
            wrap_stop(server._digikey_client, "digikey", "stop")
            save = day.save

            def tracked_save(destination):
                assert events == ["mouser", "digikey"]
                events.append("save")
                save(destination)

            monkeypatch.setattr(day, "save", tracked_save)
    assert events == ["mouser", "digikey", *(["save"] if persist else []), "tally"]
    messages = [message for message in caplog.messages if message.startswith("Per-address counts:")]
    assert messages == (["Per-address counts: 1 addresses carried over from before the restart"] if persist else [])
    if persist:
        after = quota(clock)
        assert after.load(path) == 1
        assert after.capped(ADDRESS)
    else:
        assert not path.exists()


def test_watchdog_flush_saves_counts(clock, tmp_path, monkeypatch):
    path = tmp_path / "distributor_address_counts.json"
    day = quota(clock)
    day.record(ADDRESS, 1000)
    monkeypatch.setattr(server, "_address_daily", day)
    monkeypatch.setattr(server, "DISTRIBUTOR_QUOTA_PATH", str(tmp_path / "quota.json"))

    class Writer:
        def __init__(self, *, target, daemon, name):
            assert daemon
            self.target = target

        def start(self):
            self.target()

        def join(self, timeout):
            assert timeout == server.EXIT_FLUSH_SECONDS

    monkeypatch.setattr(server, "threading", SimpleNamespace(Thread=Writer))
    server._flush_before_exit("test restart")
    after = quota(clock)
    assert after.load(path) == 1
    assert after.capped(ADDRESS)
