"""DISTRIBUTOR_BLOCKED_ADDRESSES and the cap's log line: fake UTC clocks and HTTP only."""

import datetime
import ipaddress
import json
import logging

import pytest

from pcbparts_mcp import config, server, stats
from pcbparts_mcp.cache import CARRY_MIN, AddressDailyQuota
from pcbparts_mcp.config import address_networks_setting
from pcbparts_mcp.digikey import DigiKeyClient
from pcbparts_mcp.distributor_store import DistributorStore
from pcbparts_mcp.file_logging import _DailyFileHandler
from pcbparts_mcp.lifecycle import Entry, LifecycleLookup, Reading

from digikey_backup import FakeBackup
from test_distributor_address_limits import clients, clock  # noqa: F401, F811 (fixtures)
from test_distributor_quota import Clock


BLOCKED = "192.0.2.7"
OPEN = "198.51.100.4"
NETWORKS = (ipaddress.ip_network("192.0.2.0/28"), ipaddress.ip_network("2001:db8:1:2::/64"))
BLOCKED_TEXT = ("Live Mouser and DigiKey lookups are turned off for this address on this shared server. "
                "Answers pcbparts already has stored still work.")
ADVICE = " Meanwhile use jlc_search."


def quota(limit=5, key=server._address_key, clock=lambda: 1_792_000_000.0, **kwargs):
    return AddressDailyQuota(limit, key=key, clock=clock, blocked=NETWORKS, **kwargs)


def held_back(name):
    return stats.usage.summary()["days"][0]["distributor_limits"][name]["held_back"]


class TestConfig:
    def test_addresses_networks_and_whitespace(self):
        warnings = []
        raw = " 192.0.2.7 , 198.51.100.0/24,,2001:db8::/32, 2001:db8:1:2::5/128 , 2001:db8:3:4::/64 "
        networks = address_networks_setting("X", environ={"X": raw}, warnings=warnings)
        assert networks == tuple(ipaddress.ip_network(n) for n in (
            "192.0.2.7/32", "198.51.100.0/24", "2001:db8::/32", "2001:db8:1:2::5/128", "2001:db8:3:4::/64"))
        assert warnings == []

    def test_bare_ipv6_address_is_its_64(self):
        warnings = []
        networks = address_networks_setting("X", environ={"X": "2001:db8:1:2::5"}, warnings=warnings)
        assert networks == (ipaddress.ip_network("2001:db8:1:2::/64"),) and warnings == []
        day = AddressDailyQuota(5, key=server._address_key, blocked=networks)
        assert day.blocked("2001:db8:1:2::6") and not day.blocked("2001:db8:1:3::5")
        single = AddressDailyQuota(5, key=server._address_key, blocked=address_networks_setting(
            "X", environ={"X": "2001:db8:1:2::5/128"}, warnings=warnings))
        assert single.blocked("2001:db8:1:2::5") and not single.blocked("2001:db8:1:2::6")

    def test_host_bits_past_the_prefix_block_the_whole_network_with_a_warning(self):
        warnings = []
        raw = "192.0.2.0/24,198.51.100.7/24,192.0.2.9/1"
        networks = address_networks_setting("X", environ={"X": raw}, warnings=warnings)
        assert networks == tuple(ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "128.0.0.0/1"))
        assert warnings == [f"X: entry {n} has host bits set past its prefix; blocking the whole network"
                            for n in (2, 3)]
        assert "198.51.100" not in "".join(warnings) and "192.0.2" not in "".join(warnings)

    def test_ipv4_mapped_entries_are_ipv4_networks(self):
        warnings = []
        raw = "::ffff:192.0.2.7,::ffff:198.51.100.0/120,::ffff:192.0.2.16/124"
        networks = address_networks_setting("X", environ={"X": raw}, warnings=warnings)
        assert networks == tuple(ipaddress.ip_network(n) for n in ("192.0.2.7/32", "198.51.100.0/24", "192.0.2.16/28"))
        assert warnings == []
        day = AddressDailyQuota(5, key=server._address_key, blocked=networks[:2])
        assert day.blocked("192.0.2.7") and day.blocked("198.51.100.200") and day.blocked("::ffff:198.51.100.1")
        assert not day.blocked("192.0.2.8")

    def test_invalid_entry_warns_by_position_and_is_skipped(self):
        warnings = []
        raw = "192.0.2.300,198.51.100.0/24,not-an-address,2001:db8::/129"
        networks = address_networks_setting("DISTRIBUTOR_BLOCKED_ADDRESSES", environ={
            "DISTRIBUTOR_BLOCKED_ADDRESSES": raw}, warnings=warnings)
        assert networks == (ipaddress.ip_network("198.51.100.0/24"),)
        assert warnings == [f"DISTRIBUTOR_BLOCKED_ADDRESSES: entry {n} isn't an IP address or network; skipped"
                            for n in (1, 3, 4)]
        assert "192.0.2.300" not in "".join(warnings)

    @pytest.mark.parametrize("raw", ["", " ", ",,", None])
    def test_unset_or_blank_blocks_nothing(self, raw):
        warnings = []
        environ = {} if raw is None else {"X": raw}
        assert address_networks_setting("X", environ=environ, warnings=warnings) == ()
        assert warnings == []

    def test_defaults(self):
        assert config.DISTRIBUTOR_BLOCKED_ADDRESSES == ()
        assert config.DISTRIBUTOR_DAILY_PER_ADDRESS == 300


class TestQuota:
    @pytest.mark.parametrize("caller", ["192.0.2.7", "192.0.2.15", " 192.0.2.0 ", "::ffff:192.0.2.7",
                                        "2001:db8:1:2::abcd", "2001:db8:1:2:ffff:ffff:ffff:ffff"])
    def test_blocked(self, caller):
        day = quota()
        assert day.blocked(caller) and day.capped(caller) and day.remaining(caller) == 0
        assert day.refusal_cause(caller) == "address_blocked"
        assert day.error(ADVICE, caller) == {"error": BLOCKED_TEXT + ADVICE}

    @pytest.mark.parametrize("caller", ["192.0.2.16", "198.51.100.4", "2001:db8:1:3::1", "::ffff:192.0.2.16",
                                        "unknown", "", "host.example", None])
    def test_not_blocked(self, caller):
        day = quota()
        assert not day.blocked(caller) and not day.capped(caller)
        assert day.refusal_cause(caller) == "address_daily"

    def test_exempt_caller_is_still_blocked(self):
        day = quota(key=lambda ip: None)  # every address exempt, as the AI platforms' ranges are
        assert day.capped(BLOCKED) and day.remaining(BLOCKED) == 0
        assert day.remaining(OPEN) is None and not day.capped(OPEN)

    def test_cap_off_still_blocks(self):
        day = quota(limit=0)
        assert day.capped(BLOCKED) and day.remaining(BLOCKED) == 0
        assert day.remaining(OPEN) is None and not day.capped(OPEN)

    def test_record_does_not_count_a_blocked_caller(self, caplog):
        day = quota(limit=1)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            for caller in (BLOCKED, "2001:db8:1:2::1", "::ffff:192.0.2.7"):
                day.record(caller, 3)
        assert day._counts == {} and day._first == {}
        assert not caplog.records

    def test_open_caller_keeps_the_cap_and_its_wording(self):
        day = quota(limit=1)
        day.record(OPEN)
        assert day.capped(OPEN) and day.refusal_cause(OPEN) == "address_daily"
        expected = ("This address has used its 1 Mouser and DigiKey lookups for today on this shared server; "
                    "the count resets at 00:00 UTC. Answers pcbparts already has stored still work." + ADVICE)
        assert day.error(ADVICE, OPEN) == {"error": expected}
        assert day.error(ADVICE) == {"error": expected}  # the call without a caller, as before

    def test_nothing_blocked_by_default(self):
        day = AddressDailyQuota(5, key=server._address_key)
        assert not day.blocked(BLOCKED) and not day.capped(BLOCKED)


def blocked_day(clock, limit=300, key=server._address_key):
    return AddressDailyQuota(limit, key=key, clock=clock, blocked=[ipaddress.ip_network("192.0.2.0/24")])


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
async def test_stored_answers_only_and_no_request(clients, clock, name):
    day = blocked_day(clock)
    client, pool, fake = clients(name, address_daily=day)
    assert "error" not in await client.get_part("TEST001", caller=OPEN)
    sent, tokens = len(fake.sent), fake.tokens
    stored = await client.get_part("TEST001", caller=BLOCKED)
    assert stored["results"][0]["mfr_part_number"] == "TEST001"
    assert await client.get_part("TEST002", caller=BLOCKED) == {"error": BLOCKED_TEXT + ADVICE}
    assert len(fake.sent) == sent and fake.tokens == tokens
    assert day._counts == {OPEN: 1} and pool.quotas[0]._count == 1
    assert held_back(name.lower())["address_blocked"] == 1
    assert held_back(name.lower())["address_daily"] == 0
    assert stats.usage.summary()["days"][0]["distributors"][name.lower()]["rate_limited"] == 1
    assert pool.held_back._counts == {BLOCKED: 1}  # the hourly "calls held back" line names it
    assert BLOCKED not in json.dumps(stats.usage.summary()["days"][0])
    assert "error" not in await client.get_part("TEST002", caller=OPEN)  # others are unaffected
    assert server._error_kind(BLOCKED_TEXT + ADVICE) == "rate_limited"


async def test_mouser_batch_gives_stored_parts_and_not_checked(clients, clock):
    client, _, fake = clients("Mouser", address_daily=blocked_day(clock))
    await client.get_part("TEST001", caller=OPEN)
    reply = await client.get_part("TEST001|TEST002", caller=BLOCKED)
    assert [r["mfr_part_number"] for r in reply["results"]] == ["TEST001"]
    assert reply["not_checked"] == ["TEST002"] and reply["retry_after"] > 0
    assert len(fake.sent) == 1


@pytest.mark.parametrize("name", ["Mouser", "DigiKey"])
@pytest.mark.parametrize("limit,exempt", [(0, False), (300, True)])
async def test_blocked_with_cap_off_or_exempt(clients, clock, name, limit, exempt):
    day = blocked_day(clock, limit, key=(lambda ip: None) if exempt else server._address_key)
    client, _, fake = clients(name, address_daily=day)
    assert await client.get_part("TEST001", caller=BLOCKED) == {"error": BLOCKED_TEXT + ADVICE}
    assert fake.sent == [] and fake.tokens == 0
    assert held_back(name.lower())["address_blocked"] == 1
    assert "error" not in await client.get_part("TEST001", caller=OPEN)


async def test_open_caller_reaching_the_cap_counts_address_daily(clients, clock):
    client, _, fake = clients("DigiKey", address_daily=blocked_day(clock, limit=1))
    assert "error" not in await client.get_part("TEST001", caller=OPEN)
    assert (await client.get_part("TEST002", caller=OPEN))["error"].startswith("This address has used its 1 ")
    assert held_back("digikey")["address_daily"] == 1 and held_back("digikey")["address_blocked"] == 0
    assert len(fake.sent) == 1


async def test_part_lifecycle_gives_stored_readings_only(clients, clock):
    store = DistributorStore(clock=clock)
    try:
        day = blocked_day(clock)
        mouser, _, mouser_fake = clients("Mouser", address_daily=day, store=store)
        digikey, _, digikey_fake = clients("DigiKey", address_daily=day, store=store)
        store.put_readings([Reading("TEST001", "Test", "mouser", "active", "Active", clock())])
        results = await LifecycleLookup(store, mouser, digikey).answer(
            [Entry("TEST001", mpn="TEST001"), Entry("TEST002", mpn="TEST002")], caller=BLOCKED)
        assert results[0]["status"] == "active"
        assert results[1]["status"] == "unknown" and results[1]["retry_after"] > 0
        assert mouser_fake.sent == [] and digikey_fake.sent == [] and digikey_fake.tokens == 0
        assert held_back("mouser")["address_blocked"] == 1 and held_back("digikey")["address_blocked"] == 1
    finally:
        store.close()


async def test_digikey_extension_path_sends_nothing(clock):
    store = DistributorStore(clock=clock)
    backup = FakeBackup()
    day = blocked_day(clock)
    client = DigiKeyClient("", "", backup=backup, store=store, address_daily=day, clock=clock)
    try:
        reply = await client.get_part("PART-A", caller=BLOCKED)
        assert reply["error"].startswith(BLOCKED_TEXT + " To skip the shared limits")
        answers = await client.lifecycle(["PART-B", "PART-C"], BLOCKED)
        assert {a.kind for a in answers.values()} == {"limited"}
        assert not client.can_answer_now(BLOCKED) and client.can_answer_now(OPEN)
        assert backup.lookups == [] and backup.batches == []
        assert held_back("digikey")["address_blocked"] == 3
        assert client.held_back._counts == {BLOCKED: 3}
        assert "error" not in await client.get_part("PART-A", caller=OPEN)
        assert backup.lookups == ["PART-A"] and day._counts == {OPEN: 1}
    finally:
        await client.close()
        store.close()


class TestCapLogLine:
    START = datetime.datetime(2026, 11, 26, 0, 0, 30, tzinfo=datetime.timezone.utc).timestamp()

    @staticmethod
    def lines(caplog, tmp_path):
        """The cap lines as the log file's own handler formats them."""
        handler = _DailyFileHandler(str(tmp_path / "application.log"), 1)
        try:
            return [handler.format(r) for r in caplog.records if "per-address limit" in r.getMessage()]
        finally:
            handler.close()

    @staticmethod
    def review(line):
        """The ref doc's second review command: awk's $9, $15, "capped", $17, then $19 to the end."""
        fields = line.split()
        return " ".join([fields[8], fields[14], "capped", fields[16], *fields[18:]])

    def test_first_lookup_time(self, caplog, tmp_path):
        clock = Clock(self.START - 600)  # started the day before
        day = AddressDailyQuota(3, key=server._address_key, clock=clock)
        clock.advance(600)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            day.record(BLOCKED)
            clock.advance(45 * 60)
            day.record(BLOCKED, 2)
        (line,) = self.lines(caplog, tmp_path)
        assert line.endswith(": Mouser and DigiKey per-address limit: 192.0.2.7 reached its 3 lookups for "
                             "2026-11-26 at 00:45 UTC (first lookup 00:00 UTC)")
        fields = line.split()
        assert [fields[i - 1] for i in (9, 15, 17, 21)] == ["192.0.2.7", "2026-11-26", "00:45", "00:00"]
        assert self.review(line) == "192.0.2.7 2026-11-26 capped 00:45 (first lookup 00:00 UTC)"

    def test_first_lookup_after_a_same_day_restart(self, caplog, tmp_path):
        clock = Clock(self.START + 570)  # started at 00:10
        day = AddressDailyQuota(3, key=server._address_key, clock=clock)
        clock.advance(600)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            day.record(OPEN)
            clock.advance(25 * 60)
            day.record(OPEN, 2)
        (line,) = self.lines(caplog, tmp_path)
        assert line.endswith(f"{OPEN} reached its 3 lookups for 2026-11-26 at 00:45 UTC "
                             "(first lookup 00:20 UTC, since a restart at 00:10 UTC)")
        assert line.split()[20] == "00:20"
        assert self.review(line) == f"{OPEN} 2026-11-26 capped 00:45 (first lookup 00:20 UTC, since a restart at 00:10 UTC)"

    def test_count_carried_over_a_restart(self, caplog, tmp_path):
        clock = Clock(self.START)
        path = tmp_path / "counts.json"
        before = AddressDailyQuota(CARRY_MIN + 1, key=server._address_key, clock=clock)
        before.record(OPEN, CARRY_MIN)
        before.save(path)
        after = AddressDailyQuota(CARRY_MIN + 1, key=server._address_key, clock=clock)
        assert after.load(path) == 1
        clock.advance(45 * 60)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            after.record(OPEN)
        (line,) = self.lines(caplog, tmp_path)
        assert line.endswith(f"{OPEN} reached its {CARRY_MIN + 1} lookups for 2026-11-26 at 00:45 UTC "
                             "(first lookup before a restart)")
        assert self.review(line) == f"{OPEN} 2026-11-26 capped 00:45 (first lookup before a restart)"

    def test_first_times_follow_the_table_and_the_day(self):
        clock = Clock(self.START)
        day = AddressDailyQuota(5, key=server._address_key, clock=clock, max_addresses=1)
        day.record(OPEN)
        day.record("198.51.100.5")  # the table is full: the oldest address goes, with its first time
        assert day._first == {"198.51.100.5": self.START}
        clock.advance(86400)
        day.record(OPEN)
        assert day._first == {OPEN: self.START + 86400}


async def test_server_wires_the_block_list_and_logs_only_its_size(clock, monkeypatch, caplog):
    from fastmcp import Client
    from pcbparts_mcp.cache import DailyQuota
    monkeypatch.setattr(server, "MOUSER_API_KEY", "test-key")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_ID", "test-id")
    monkeypatch.setattr(server, "DIGIKEY_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(server, "OPENAI_IP_RANGES_FILE", "")
    monkeypatch.setattr(server, "DISTRIBUTOR_BLOCKED_ADDRESSES", NETWORKS)
    monkeypatch.setattr(server, "DailyQuota", lambda *args, **kw: DailyQuota(*args, clock=clock, **kw))
    monkeypatch.setattr(server, "AddressDailyQuota", lambda *args, **kw: AddressDailyQuota(*args, clock=clock, **kw))
    with caplog.at_level(logging.INFO, logger="pcbparts_mcp.server"):
        async with Client(server.mcp):
            for pool in server._distributor_quotas.values():
                assert pool.address_error(BLOCKED)["error"].startswith(BLOCKED_TEXT)
                assert pool.address_error(OPEN) is None
    lines = [r.getMessage() for r in caplog.records if "live lookups blocked" in r.getMessage()]
    assert lines == ["Mouser and DigiKey: live lookups blocked for 2 address range(s)"]
    assert not any("192.0.2." in r.getMessage() or "2001:db8" in r.getMessage() for r in caplog.records)
