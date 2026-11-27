"""0.10.12's /mcp/stats additions: each day's starts, distinct address counts, every daily budget's
state, when DigiKey lookups moved to ext, and DigiKey's holds and refusals on the ext path.
Fake clocks, in-memory answers and HTTP mock transports only."""

import datetime
import ipaddress
import json
import logging

import httpx
import pytest

from pcbparts_mcp import __version__, server, stats
from pcbparts_mcp.cache import AddressDailyQuota, DailyQuota, MouserKeyPool, QuotaPool
from pcbparts_mcp.extensions import ExtUnavailable
from pcbparts_mcp.platform_ranges import PlatformRanges
from digikey_ext import FakeExt
from test_digikey_two_apps import DAILY_HEADERS, MIDNIGHT, ok
from test_extensions import CALLER, hybrid  # noqa: F401 (hybrid: the shared fixture)

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 27, 14, 5, tzinfo=UTC).timestamp()
TODAY = "2026-11-27"


class Clock:
    def __init__(self, now: float = NOW):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def today(usage=None):
    return (usage or stats.usage).summary()["days"][0]


def digikey_limits():
    return stats.usage.summary()["totals"]["distributor_limits"]["digikey"]


def assert_holds_add_up():
    """held_back (every path) adds up to rate_limited; each ext count is within its total."""
    totals = stats.usage.summary()["totals"]
    limits, distributors = totals["distributor_limits"]["digikey"], totals["distributors"]["digikey"]
    assert sum(limits["held_back"].values()) == distributors["rate_limited"]
    assert all(limits["ext_held_back"][c] <= limits["held_back"][c] for c in stats.DISTRIBUTOR_LIMIT_CAUSES)
    assert limits["ext_refusals"]["refused"] <= limits["refusals"]["refused"]
    return limits


class TestStarts:
    def test_each_start_gives_its_time_and_version(self):
        clock = Clock()
        usage = stats.UsageStats(clock=clock)
        usage.record_start()
        clock.advance(3600 + 7 * 60)
        usage.record_start()
        day = today(usage)
        assert day["restarts"] == 2
        assert day["starts"] == [{"at": "14:05", "version": __version__}, {"at": "15:12", "version": __version__}]

    def test_capped_at_50_a_day_while_restarts_counts_all(self):
        usage = stats.UsageStats(clock=Clock())
        for _ in range(stats.MAX_STARTS + 5):
            usage.record_start()
        day = today(usage)
        assert day["restarts"] == 55 and len(day["starts"]) == 50

    def test_kept_across_a_restart_and_malformed_entries_dropped(self, tmp_path):
        path = tmp_path / "usage.json"
        good = {"at": "06:30", "version": "0.10.11"}
        path.write_text(json.dumps({"days": {TODAY: {"restarts": 7, "starts": [
            good, {"at": "6:30", "version": "0.10.11"}, {"at": "24:00", "version": "0.10.11"},
            {"at": "07:00", "version": "not a version"}, {"at": "07:00"}, "07:00", None,
            {"at": "08:15", "version": "0.10.12", "extra": "dropped"}]}}}), encoding="utf-8")
        usage = stats.UsageStats(clock=Clock())
        usage.open(path)
        assert today(usage)["starts"] == [good, {"at": "08:15", "version": "0.10.12"}]
        usage.record_start()
        usage.save()
        again = stats.UsageStats(clock=Clock())
        again.open(path)
        assert today(again)["starts"][-1] == {"at": "14:05", "version": __version__}
        assert today(again)["restarts"] == 8

    def test_older_days_lack_the_new_keys(self, tmp_path):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-11-20": {"restarts": 1},
                                             "2026-11-21": {"restarts": 1, "starts": "bad", "addresses": []}}}),
                        encoding="utf-8")
        usage = stats.UsageStats(clock=Clock())
        usage.open(path)
        usage.record_start()  # the deploy day: from now on
        days = {day["date"]: day for day in usage.summary()["days"]}
        for date in ("2026-11-20", "2026-11-21"):
            assert "starts" not in days[date] and "addresses" not in days[date]
        assert days[TODAY]["starts"] == [{"at": "14:05", "version": __version__}]
        assert days[TODAY]["addresses"] == {"rate_limited": 0, "cap_reached": 0, "blocked_tried": 0}
        totals = usage.summary()["totals"]
        assert "starts" not in totals and "addresses" not in totals


class TestAddresses:
    def test_distinct_a_day_never_written(self, tmp_path):
        clock = Clock()
        usage = stats.UsageStats(clock=clock)
        path = tmp_path / "usage.json"
        usage.open(path)
        for address in ("203.0.113.7", "203.0.113.7", "198.51.100.1"):
            usage.record_address("rate_limited", address)
        usage.record_address("cap_reached", "203.0.113.7")
        usage.record_address("unknown_event", "203.0.113.8")
        usage.record_address("blocked_tried", None)
        assert today(usage)["addresses"] == {"rate_limited": 2, "cap_reached": 1, "blocked_tried": 0}
        usage.save()
        text = path.read_text(encoding="utf-8")
        assert "203.0.113" not in text and "198.51.100" not in text
        clock.advance(86400)  # a new UTC day, a new set
        usage.record_address("rate_limited", "203.0.113.7")
        assert today(usage)["addresses"]["rate_limited"] == 1

    def test_a_restart_counts_an_address_again(self, tmp_path):
        path = tmp_path / "usage.json"
        usage = stats.UsageStats(clock=Clock())
        usage.open(path)
        usage.record_address("rate_limited", "203.0.113.7")
        usage.save()
        again = stats.UsageStats(clock=Clock())
        again.open(path)
        again.record_address("rate_limited", "203.0.113.7")  # the hashes aren't kept: counted twice
        assert today(again)["addresses"]["rate_limited"] == 2

    def test_malformed_counts_are_cleaned_on_load(self, tmp_path):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {TODAY: {"addresses": {"rate_limited": -3, "cap_reached": "2",
                                                                   "blocked_tried": 4, "other": 9}}}}),
                        encoding="utf-8")
        usage = stats.UsageStats(clock=Clock())
        usage.open(path)
        assert today(usage)["addresses"] == {"rate_limited": 0, "cap_reached": 0, "blocked_tried": 4}

    def test_rate_limit_refusals_by_address_ipv6_by_64(self, monkeypatch):
        clock = Clock()
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        limiter = server.RateLimitMiddleware(None, requests_per_minute=10, clock=clock, wall_clock=clock,
                                             platform_addresses=PlatformRanges())
        for address in ("203.0.113.7", "203.0.113.7", "2001:db8:1:2::1", "2001:db8:1:2::ffff",
                        "2001:db8:1:3::1", "::ffff:203.0.113.7"):
            limiter._count_refusal(address, "per_ip_rate_limit")
        limiter._count_refusal("198.51.100.4", "too_many_clients")
        day = today()
        assert day["addresses"]["rate_limited"] == 4  # 203.0.113.7, two /64s, 198.51.100.4
        assert day["per_ip_refusals"]["total"] == 7

    def test_ai_platform_addresses_count_one_by_one(self, monkeypatch):
        clock = Clock()
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        ranges = PlatformRanges({"test": [ipaddress.ip_network("2001:db8:aa::/48")]})
        limiter = server.RateLimitMiddleware(None, requests_per_minute=10, clock=clock, wall_clock=clock,
                                             platform_addresses=ranges)
        for address in ("2001:db8:aa:1::1", "2001:db8:aa:1::2", "2001:db8:bb:1::1", "2001:db8:bb:1::2"):
            limiter._count_refusal(address, "per_ip_rate_limit")
        assert today()["addresses"]["rate_limited"] == 3  # two platform addresses, one other /64

    def test_cap_reached_once_per_address(self, monkeypatch, caplog):
        clock = Clock()
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        day = AddressDailyQuota(2, key=server._address_key, clock=clock)
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cache"):
            for caller in ("203.0.113.7", "203.0.113.7", "203.0.113.7", "2001:db8::1", "2001:db8::2"):
                day.record(caller)
        assert today()["addresses"]["cap_reached"] == 2  # 203.0.113.7 and 2001:db8::/64
        assert sum("reached its 2 lookups" in m for m in caplog.messages) == 2
        assert "203.0.113" not in json.dumps(stats.usage.summary())

    def test_blocked_addresses_that_tried_a_live_lookup(self, monkeypatch):
        clock = Clock()
        monkeypatch.setattr(stats, "usage", stats.UsageStats(clock=clock))
        blocked = [ipaddress.ip_network("192.0.2.0/24"), ipaddress.ip_network("2001:db8::/32")]
        day = AddressDailyQuota(1, key=server._address_key, clock=clock, blocked=blocked)
        pool = MouserKeyPool([DailyQuota("Mouser", 100, clock=clock)], address_daily=day)
        for caller in ("192.0.2.1", "192.0.2.1", "192.0.2.2", "::ffff:192.0.2.2", "2001:db8:1:1::1",
                       "2001:db8:1:1::2"):
            assert pool.acquire(caller) == (None, pool.address_error(caller))
            assert pool.last_refusal_cause == "address_blocked"
        pool.acquire("203.0.113.7")
        assert pool.acquire("203.0.113.7")[0] is None  # its day is used: not blocked
        assert day.capped("192.0.2.9")  # a check alone isn't a try
        addresses = today()["addresses"]
        assert addresses["blocked_tried"] == 3 and addresses["cap_reached"] == 1
        assert "192.0.2" not in json.dumps(stats.usage.summary())


class TestBudgets:
    @pytest.mark.parametrize("cls", [QuotaPool, MouserKeyPool], ids=["dk", "mouser"])
    def test_one_in_use_and_each_own_state(self, cls):
        clock = Clock()
        quotas = [DailyQuota("X", 2, clock=clock) for _ in range(3)]
        pool = cls(quotas)
        assert [b["in_use"] for b in pool.status()["budgets"]] == [True, False, False]
        quotas[0].note_api_usage(17, 1000)
        quotas[0].pause(NOW + 3600, "daily")  # the first one's day is over
        pool.acquire()
        status = pool.status()
        assert status["budgets"] == [
            {"used_today": 0, "limit": 2, "api_remaining": 17, "paused_until": "2026-11-27 15:05 UTC", "in_use": False},
            {"used_today": 1, "limit": 2, "api_remaining": None, "paused_until": None, "in_use": True},
            {"used_today": 0, "limit": 2, "api_remaining": None, "paused_until": None, "in_use": False}]
        assert status["used_today"] == 1  # the top level stays the one in use
        for quota in quotas[1:]:
            quota.pause(NOW + 3600, "daily")
        status = pool.status()
        # Every day spent, all ending together: the one the pool tries first then (for Mouser, the
        # rotation's current key, the one just used)
        assert [b["in_use"] for b in status["budgets"]] == ([True, False, False] if cls is QuotaPool
                                                             else [False, True, False])
        assert status["paused_until"] == "2026-11-27 15:05 UTC"
        assert status["used_today"] == (0 if cls is QuotaPool else 1)  # the top level is the same budget
        clock.now = NOW + 3600
        assert pool.acquire()[0] == (0 if cls is QuotaPool else 1)


def refuse_mouser(pool, index, sent_count=1):
    """A Mouser daily refusal as MouserClient records one (a short pause for a key that sent little)."""
    pool.refuse_daily(index, pool.sent(index), sent_count)


class TestBudgetInUseWhenEverythingIsSpent:
    def check(self, pool, expected):
        status = pool.status()
        assert [b["in_use"] for b in status["budgets"]] == [i == expected for i in range(len(pool.quotas))]
        budget = status["budgets"][expected]
        assert status["used_today"] == budget["used_today"] and status["limit"] == budget["limit"]
        return status

    def test_mouser_keys_refused_ten_minutes_apart(self):
        clock = Clock()
        pool = MouserKeyPool([DailyQuota("Mouser", 1000, clock=clock, day_start_hour=6) for _ in range(3)])
        for index in range(3):
            assert pool.acquire()[0] == index
            refuse_mouser(pool, index)
            clock.advance(600)
        status = self.check(pool, 0)  # the first refused is the first tried again
        assert status["paused_until"] == "2026-11-27 15:05 UTC" == status["budgets"][0]["paused_until"]
        clock.now = NOW + 3600
        assert pool.acquire()[0] == 0

    def test_mouser_next_is_the_earliest_end_not_the_rotation(self):
        clock = Clock()
        pool = MouserKeyPool([DailyQuota("Mouser", 1000, clock=clock, day_start_hour=6) for _ in range(3)])
        pool.acquire()
        refuse_mouser(pool, 0, sent_count=900)  # it used most of its day: out until the next Mouser day
        for index in (1, 2):
            clock.advance(600)
            assert pool.acquire()[0] == index
            refuse_mouser(pool, index)
        status = self.check(pool, 1)
        assert status["paused_until"] == status["budgets"][1]["paused_until"] == "2026-11-27 15:15 UTC"
        clock.now = NOW + 600 + 3600
        assert pool.acquire()[0] == 1

    def test_both_digikey_apps_spent(self):
        clock = Clock()
        pool = QuotaPool([DailyQuota("DigiKey", 2, clock=clock) for _ in range(2)])
        for _ in range(4):
            pool.acquire()
        status = self.check(pool, 0)  # both reset at 00:00 UTC: the first app is used then
        assert status["used_today"] == 2 and status["paused_until"] == "2026-11-28 00:00 UTC"
        clock.now = datetime.datetime(2026, 11, 28, tzinfo=UTC).timestamp()
        assert pool.acquire()[0] == 0

    def test_digikey_app_whose_day_ends_first(self):
        clock = Clock()
        pool = QuotaPool([DailyQuota("DigiKey", 2, clock=clock) for _ in range(2)])
        midnight = datetime.datetime(2026, 11, 28, tzinfo=UTC).timestamp()
        pool.quotas[0].pause(midnight + 3600, "daily")  # DigiKey said its day ends at 01:00 UTC
        for _ in range(2):
            assert pool.acquire()[0] == 1
        status = self.check(pool, 1)
        assert status["paused_until"] == "2026-11-28 00:00 UTC"
        clock.now = midnight
        assert pool.acquire()[0] == 1


async def test_budgets_reach_stats(monkeypatch, stats_headers):
    from types import SimpleNamespace
    clock = Clock()
    mouser = MouserKeyPool([DailyQuota("Mouser", 5, clock=clock, day_start_hour=6) for _ in range(2)])
    digikey = QuotaPool([DailyQuota("DigiKey", 5, clock=clock)])
    monkeypatch.setattr(server, "_distributor_quotas", {"mouser": mouser, "digikey": digikey})
    monkeypatch.setattr(server, "_digikey_client", None)
    mouser.acquire()
    response = await server.usage_stats(SimpleNamespace(headers=stats_headers, query_params={}))
    quota = json.loads(response.body)["distributor_quota"]
    assert [b["used_today"] for b in quota["mouser"]["budgets"]] == [1, 0]
    assert quota["digikey"]["budgets"] == [
        {"used_today": 0, "limit": 5, "api_remaining": None, "paused_until": None, "in_use": True}]
    assert sum(b["in_use"] for b in quota["mouser"]["budgets"]) == 1
    assert "budgets (from 0.10.12)" in json.loads(response.body)["about"]


class TestExtActiveSince:
    async def test_a_restart_with_the_day_spent_sets_it_at_the_first_check(self, hybrid):
        h = hybrid(apps=1, limit=1)
        h.pool.acquire()  # restored state: the API's day was already spent
        h.clock.advance(120)
        assert h.client.ext_pause() == {"paused_until": None, "active": True, "active_since": "2026-11-14 21:17 UTC"}
        h.clock.advance(600)
        assert h.client.ext_pause()["active_since"] == "2026-11-14 21:17 UTC"
        h.clock.now = MIDNIGHT  # the API's new day: back on the API
        assert h.client.ext_pause() == {"paused_until": None, "active": False, "active_since": None}

    async def test_a_lookup_notices_the_move_first(self, hybrid):
        h = hybrid(ok(DAILY_HEADERS), apps=1)
        assert (await h.client.lookup("PART-A", CALLER)).kind == "found"  # the API's last request today
        h.clock.advance(60)
        assert (await h.client.lookup("LM358DR", CALLER)).kind == "found"  # through ext
        h.clock.advance(3600)
        assert h.client.ext_pause()["active_since"] == "2026-11-14 21:16 UTC"


class RefusingExt(FakeExt):
    """Counts a refusal as an extension does, inside its lookup or batch, then pauses."""

    async def lookup(self, number, sent=None, charge=None):
        if charge is not None and not charge(number):
            from pcbparts_mcp.extensions import AddressCapReached
            raise AddressCapReached()
        if sent is not None:
            sent.add(number)
        stats.count_distributor_limit("digikey", "refusals", "refused")
        self.paused = True
        raise ExtUnavailable(60, paused=True, sent=True, refused=True)

    async def statuses(self, numbers, sent=None, charge=None, held=None):
        stats.count_distributor_limit("digikey", "refusals", "refused")
        self.paused = True
        raise ExtUnavailable(60, paused=True, refused=True)


class TestHoldsByPath:
    async def test_api_holds_are_not_ext(self, hybrid):
        h = hybrid(ok(), address_limit=1)
        assert (await h.client.lookup("PART-A", CALLER)).kind == "found"
        assert (await h.client.lookup("PART-B", CALLER)).kind == "limited"  # its address's day, on the API
        limits = assert_holds_add_up()
        assert limits["held_back"]["address_daily"] == 1 and not any(limits["ext_held_back"].values())

    async def test_ext_address_and_pause_holds(self, hybrid):
        h = hybrid(limit=0, address_limit=1)  # the API's day is spent: lookups go to ext
        assert (await h.client.lookup("PART-A", CALLER)).kind == "found"
        assert (await h.client.lookup("PART-B", CALLER)).kind == "limited"  # the address's day, on ext
        h.ext.pause()
        assert (await h.client.lookup("PART-C", "198.51.100.1")).kind == "limited"  # ext's pause
        lifecycle = await h.client.lifecycle(["PART-D", "PART-E"], CALLER)  # a batch the address's day stops
        assert {answer.kind for answer in lifecycle.values()} == {"limited"}
        limits = assert_holds_add_up()
        assert limits["ext_held_back"] == {**dict.fromkeys(stats.DISTRIBUTOR_LIMIT_CAUSES, 0),
                                           "address_daily": 3, "distributor_refused": 1}
        assert limits["held_back"] == limits["ext_held_back"]  # every hold was on the ext path

    async def test_held_on_the_api_side_after_the_move_is_ext(self, hybrid, monkeypatch):
        h = hybrid(apps=1, limit=1, address_limit=1)

        async def ready(caller):  # meanwhile another lookup spent the API's day, and this address's
            h.pool.acquire()
            h.day.record(CALLER)
            return None, None

        monkeypatch.setattr(h.client, "_ready_app", ready)
        assert (await h.client.lookup("LM358DR", CALLER)).kind == "limited"
        limits = assert_holds_add_up()
        assert limits["held_back"]["address_daily"] == 1 and limits["ext_held_back"]["address_daily"] == 1

    async def test_api_pause_holds_before_the_move_are_the_apis(self, hybrid):
        h = hybrid(apps=1)
        h.pool.note_response(0, 429, {"retry-after": "60"})  # a minute pause: lookups stay on the API
        assert (await h.client.lookup("LM358DR", CALLER)).kind == "limited"
        limits = assert_holds_add_up()
        assert limits["held_back"]["distributor_minute"] == 1 and not any(limits["ext_held_back"].values())

    async def test_ext_refusals(self, hybrid):
        h = hybrid(limit=0, ext=RefusingExt())
        assert (await h.client.lookup("PART-A", CALLER)).kind == "limited"
        h.ext.paused = False
        answers = await h.client.lifecycle(["PART-B"], CALLER)
        assert answers["PART-B"].kind == "limited"
        h.client._note_limits(httpx.Response(403), 0)  # one the API refused
        limits = assert_holds_add_up()
        assert limits["refusals"]["refused"] == 3 and limits["ext_refusals"] == {"refused": 2}
        assert stats.distributor_path.get() is None  # the path doesn't leak out of the calls

    async def test_explicit_path_and_context(self):
        stats.count_distributor_limit("digikey", "held_back", "other", path="ext")
        token = stats.distributor_path.set("ext")
        try:
            stats.count_distributor_limit("digikey", "held_back", "minute_cap")
            stats.count_distributor_limit("digikey", "refusals", "daily")  # ext reports refused only
            stats.count_distributor_limit("mouser", "held_back", "minute_cap")  # no paths for Mouser
        finally:
            stats.distributor_path.reset(token)
        stats.count_distributor_limit("digikey", "refusals", "refused")
        limits = stats.usage.summary()["totals"]["distributor_limits"]
        assert limits["digikey"]["ext_held_back"]["other"] == 1 and limits["digikey"]["ext_held_back"]["minute_cap"] == 1
        assert limits["digikey"]["ext_refusals"] == {"refused": 0} and limits["digikey"]["refusals"]["refused"] == 1
        assert "ext_held_back" not in limits["mouser"] and "ext_refusals" not in limits["mouser"]


class TestLimitsFile:
    def stored(self, tmp_path, digikey, days=None):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": days or {TODAY: {"distributor_limits": {"digikey": digikey}}}}),
                        encoding="utf-8")
        usage = stats.UsageStats(clock=Clock())
        usage.open(path)
        return usage

    def test_a_day_without_path_counts_stays_unsplit(self, tmp_path, monkeypatch):
        usage = self.stored(tmp_path, {"held_back": {"address_daily": 4}, "refusals": {"refused": 1}})
        monkeypatch.setattr(stats, "usage", usage)
        stats.count_distributor_limit("digikey", "held_back", "address_daily", path="ext")
        limits = usage.summary()["days"][0]["distributor_limits"]["digikey"]
        assert limits["held_back"]["address_daily"] == 5
        assert "ext_held_back" not in limits and "ext_refusals" not in limits
        assert "ext_held_back" not in usage.summary()["totals"]["distributor_limits"]["digikey"]

    def test_stored_path_counts_are_kept_and_summed(self, tmp_path):
        good = {"held_back": {"address_daily": 4}, "refusals": {"refused": 2},
                "ext_held_back": {"address_daily": 3}, "ext_refusals": {"refused": 2}}
        usage = self.stored(tmp_path, good, days={
            TODAY: {"distributor_limits": {"digikey": good}},
            "2026-11-26": {"distributor_limits": {"digikey": good}},
            "2026-11-25": {"distributor_limits": {"digikey": {"held_back": {}, "refusals": {}}}},  # nothing held
        })
        day = usage.summary()["days"][0]["distributor_limits"]["digikey"]
        assert day["ext_held_back"]["address_daily"] == 3 and day["ext_held_back"]["other"] == 0
        totals = usage.summary()["totals"]["distributor_limits"]["digikey"]
        assert totals["ext_held_back"]["address_daily"] == 6 and totals["ext_refusals"] == {"refused": 4}

    @pytest.mark.parametrize("bad", [{"address_daily": 5}, {"address_daily": -1}, {"address_daily": 1.0},
                                     {"address_daily": True}, [3]], ids=["over", "neg", "float", "bool", "list"])
    def test_malformed_path_counts_leave_the_day_unsplit(self, tmp_path, bad):
        usage = self.stored(tmp_path, {"held_back": {"address_daily": 4}, "ext_held_back": bad,
                                       "ext_refusals": {"refused": 0}})
        limits = usage.summary()["days"][0]["distributor_limits"]["digikey"]
        assert "ext_held_back" not in limits and limits["ext_refusals"] == {"refused": 0}
        assert "ext_held_back" not in usage.summary()["totals"]["distributor_limits"]["digikey"]

    def test_a_new_day_has_them_from_its_first_count(self):
        stats.count_distributor_limit("digikey", "held_back", "minute_cap")
        limits = today()["distributor_limits"]["digikey"]
        assert limits["ext_held_back"] == dict.fromkeys(stats.DISTRIBUTOR_LIMIT_CAUSES, 0)
        assert limits["ext_refusals"] == {"refused": 0}

    def test_about_describes_the_new_fields(self):
        about = stats.usage.summary()["about"]
        for text in ("ext_held_back and ext_refusals (from 0.10.12)", "starts (from 0.10.12", "addresses (from 0.10.12",
                     "active_since"):
            assert text in about

