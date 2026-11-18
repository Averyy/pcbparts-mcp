"""0.10.0: Mouser/DigiKey answers (3 days) and lifecycle readings (90 days) in one SQLite store on the
cache volume, and the lifecycle wording normalised. No network; fake clocks."""

import datetime

import pytest

from pcbparts_mcp.config import (
    DIGIKEY_CACHE_TTL, DIGIKEY_NOT_FOUND_TTL, LIFECYCLE_TTL, LIFECYCLE_UNKNOWN_TTL, MOUSER_CACHE_TTL,
    MOUSER_NOT_FOUND_TTL,
)
from pcbparts_mcp.distributor_store import DistributorStore
from pcbparts_mcp.lifecycle import (
    MOUSER_NOT_STATED, Reading, digikey_status, last_buy_date, maker_key, makers_match, mouser_status,
)

NOW = datetime.datetime(2026, 11, 18, 12, tzinfo=datetime.timezone.utc).timestamp()
DAY = 86400


class Clock:
    def __init__(self, now: float = NOW):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def store(clock):
    store = DistributorStore(clock=clock)
    yield store
    store.close()


def reading(mpn="LM358P", maker="Texas Instruments", source="mouser", status="active", raw=MOUSER_NOT_STATED,
            observed_at=NOW, found=True):
    return Reading(mpn, maker, source, status, raw, observed_at, found)


def test_lifetimes_as_decided():
    assert (MOUSER_CACHE_TTL, DIGIKEY_CACHE_TTL) == (3 * DAY, 3 * DAY)
    assert (MOUSER_NOT_FOUND_TTL, DIGIKEY_NOT_FOUND_TTL) == (DAY, DAY)
    assert (LIFECYCLE_TTL, LIFECYCLE_UNKNOWN_TTL) == (90 * DAY, 7 * DAY)


class TestAnswers:
    @pytest.mark.parametrize("source", ["mouser", "digikey"])
    def test_found_kept_three_days_not_found_one(self, store, clock, source):
        store.put_answer(source, "LM358P", {"results": [1]}, True)
        store.put_answer(source, "NOPE", {"not_found": True}, False)
        clock.advance(DAY - 1)
        assert store.get_answer(source, "NOPE") == ({"not_found": True}, NOW)
        clock.advance(1)
        assert store.get_answer(source, "NOPE") is None
        clock.advance(2 * DAY - 1)
        assert store.get_answer(source, "LM358P") == ({"results": [1]}, NOW)
        clock.advance(1)
        assert store.get_answer(source, "LM358P") is None

    def test_sources_are_kept_apart(self, store):
        store.put_answer("mouser", "X1", {"m": 1}, True)
        assert store.get_answer("digikey", "X1") is None

    def test_survive_a_restart(self, tmp_path, clock):
        path = tmp_path / "cache" / "distributor.db"
        first = DistributorStore(path, clock=clock)
        assert first.persistent
        first.put_answer("mouser", "LM358P", {"results": []}, False)
        first.put_readings([reading()])
        first.close()
        again = DistributorStore(path, clock=clock)
        try:
            assert again.get_answer("mouser", "LM358P") == ({"results": []}, NOW)
            assert [r.status for r in again.readings("LM358P")] == ["active"]
            assert again.counts() == {"answers": 1, "lifecycle": 1, "kept_across_restarts": True}
        finally:
            again.close()

    def test_unusable_path_keeps_answers_in_memory(self, tmp_path, clock, caplog):
        blocker = tmp_path / "a-file"
        blocker.write_text("not a directory", encoding="utf-8")
        store = DistributorStore(blocker / "distributor.db", clock=clock)
        try:
            assert not store.persistent and "memory only" in caplog.text
            store.put_answer("mouser", "A1", {"ok": 1}, True)
            assert store.get_answer("mouser", "A1") == ({"ok": 1}, NOW)
            assert store.counts()["kept_across_restarts"] is False
        finally:
            store.close()

    def test_closed_store_reads_nothing_and_never_raises(self, clock):
        store = DistributorStore(clock=clock)
        store.close()
        assert store.get_answer("mouser", "A1") is None and store.readings("A1") == []
        assert store.put_answer("mouser", "A1", {}, True) is False
        store.prune()


class TestReadings:
    def test_kept_90_days(self, store, clock):
        store.put_readings([reading(status="nrnd", raw="Not Recommended for New Designs")])
        clock.advance(LIFECYCLE_TTL - 1)
        assert [r.status for r in store.readings("LM358P")] == ["nrnd"]
        clock.advance(1)
        assert store.readings("LM358P") == []

    @pytest.mark.parametrize("found, status", [(False, "unknown"), (True, "unknown")])
    def test_not_listed_and_unknown_kept_a_week(self, store, clock, found, status):
        store.put_readings([reading(maker="" if not found else "TI", status=status, raw=None, found=found)])
        clock.advance(LIFECYCLE_UNKNOWN_TTL - 1)
        assert len(store.readings("LM358P")) == 1
        clock.advance(1)
        assert store.readings("LM358P") == []

    def test_found_by_mpn_key_whatever_the_spelling(self, store):
        store.put_readings([reading(mpn="AMS1117-3.3")])
        assert len(store.readings("ams1117 3.3")) == 1
        assert store.readings("AMS1117-33") == []  # the decimal point is part of the number

    def test_one_per_maker_and_source_newest_wins(self, store, clock):
        store.put_readings([reading(status="active")])
        clock.advance(10)
        store.put_readings([reading(status="nrnd", raw="Not Recommended for New Designs", observed_at=clock())])
        store.put_readings([reading(maker="Texas Instruments Inc.", source="digikey", status="obsolete", raw="Obsolete")])
        got = sorted((r.source, r.status) for r in store.readings("LM358P"))
        assert got == [("digikey", "obsolete"), ("mouser", "nrnd")]

    def test_a_reading_replaces_not_listed_from_that_source_only(self, store):
        store.put_not_listed("X1", "mouser")
        store.put_not_listed("X1", "digikey")
        store.put_readings([reading(mpn="X1")])
        assert sorted((r.source, r.found) for r in store.readings("X1")) == [("digikey", False), ("mouser", True)]
        store.put_not_listed("X1", "mouser")  # a later "not listed" keeps the part's reading
        assert sorted((r.source, r.found) for r in store.readings("X1")) == [("digikey", False), ("mouser", False),
                                                                              ("mouser", True)]

    def test_also_filed_under_the_number_asked(self, store):
        store.put_readings([reading(mpn="B2B-PH-K-S", maker="JST", source="digikey", status="active", raw="Active")],
                           also_as="B2B-PH-K-S(LF)(SN)")
        assert [r.mpn for r in store.readings("B2B-PH-K-S(LF)(SN)")] == ["B2B-PH-K-S"]
        assert len(store.readings("B2B-PH-K-S")) == 1

    def test_prune_drops_expired_rows(self, store, clock):
        store.put_answer("mouser", "OLD", {}, False)
        store.put_readings([reading(mpn="OLD", status="unknown", raw="Discontinued")])
        store.put_readings([reading(mpn="KEEP", status="obsolete", raw="Obsolete")])
        clock.advance(LIFECYCLE_UNKNOWN_TTL)
        store.prune()
        assert store.counts()["answers"] == 0
        assert store._conn.execute("SELECT mpn FROM lifecycle").fetchall() == [("KEEP",)]


class TestStatuses:
    @pytest.mark.parametrize("raw, status, wording", [
        (None, "active", MOUSER_NOT_STATED),  # Mouser leaves normal active parts blank
        ("", "active", MOUSER_NOT_STATED),
        ("New Product", "active", "New Product"),
        ("New at Mouser", "active", "New at Mouser"),
        ("Not Recommended for New Designs", "nrnd", "Not Recommended for New Designs"),
        ("End of Life", "last_time_buy", "End of Life"),
        ("Obsolete", "obsolete", "Obsolete"),
        ("Discontinued", "unknown", "Discontinued"),  # IsDiscontinued: Mouser's own stocking
        ("Something new", "unknown", "Something new"),
    ])
    def test_mouser(self, raw, status, wording):
        assert mouser_status(raw) == (status, wording)

    @pytest.mark.parametrize("text, discontinued, end_of_life, status, wording", [
        ("Active", False, False, "active", "Active"),
        ("Not For New Designs", False, False, "nrnd", "Not For New Designs"),
        ("Last Time Buy", False, False, "last_time_buy", "Last Time Buy"),
        ("Obsolete", False, False, "obsolete", "Obsolete"),
        ("Discontinued at Digi-Key", True, False, "unknown", "Discontinued at Digi-Key"),
        ("Preliminary", False, False, "unknown", "Preliminary"),
        ("Active", False, True, "last_time_buy", "Active (end of life)"),
        ("Active", True, False, "unknown", "Active (discontinued at DigiKey)"),
        ("Obsolete", True, True, "obsolete", "Obsolete (discontinued at DigiKey)"),
        (None, False, False, "unknown", "Unknown"),
    ])
    def test_digikey(self, text, discontinued, end_of_life, status, wording):
        assert digikey_status(text, discontinued, end_of_life) == (status, wording)

    @pytest.mark.parametrize("value, date", [
        ("2027-03-31T00:00:00Z", "2027-03-31"), ("2027-03-31", "2027-03-31"), ("0001-01-01T00:00:00", None),
        (None, None), ("soon", None), (20270331, None),
    ])
    def test_last_buy_date(self, value, date):
        assert last_buy_date(value) == date


class TestMakers:
    @pytest.mark.parametrize("a, b", [
        ("Texas Instruments", "Texas Instruments Inc."),
        ("TI", "Texas Instruments"),
        ("Microchip Tech", "Microchip Technology"),
        ("NXP Semicon", "NXP USA Inc."),
        ("NXP Semicon", "NXP Semiconductors"),
        ("Diodes Incorporated", "Diodes Inc"),
        ("TDK Corporation", "TDK"),
        ("Wurth Elektronik", "Würth Elektronik"),
        ("UMW(Youtai Semiconductor Co., Ltd.)", "UMW"),
        ("ST(Semtech)", "Semtech"),
        ("Alpha & Omega Semicon", "Alpha & Omega Semiconductor Inc."),
    ])
    def test_same_maker(self, a, b):
        assert makers_match(a, b) and makers_match(b, a)

    @pytest.mark.parametrize("a, b", [
        ("ST(Semtech)", "STMicroelectronics"),  # a short name must be whole
        ("UMW(Youtai Semiconductor Co., Ltd.)", "Texas Instruments"),
        ("Silicon Labs", "Silicon Storage Technology"),
        ("onsemi", "Nexperia"),
    ])
    def test_different_makers(self, a, b):
        assert not makers_match(a, b)

    def test_one_key_per_maker(self):
        assert maker_key("Texas Instruments Inc.") == maker_key("texas instruments") == "texas instruments"
