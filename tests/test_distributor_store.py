"""0.10.0: Mouser/DigiKey answers (3 days) and lifecycle readings (90 days) in one SQLite store on the
cache volume, and the lifecycle wording normalised. No network; fake clocks."""

import datetime

import pytest

from pcbparts_mcp.config import (
    DIGIKEY_CACHE_TTL, DIGIKEY_NOT_FOUND_TTL, LIFECYCLE_NOT_LISTED_TTL, LIFECYCLE_TTL, LIFECYCLE_UNKNOWN_TTL,
    MOUSER_CACHE_TTL, MOUSER_NOT_FOUND_TTL,
)
from pcbparts_mcp.distributor_store import DistributorStore
from pcbparts_mcp.lifecycle import (
    MOUSER_NOT_STATED, NOT_LISTED_MAKER_KEY, Reading, digikey_status, last_buy_date, maker_key, makers_match,
    mouser_status,
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
    assert (LIFECYCLE_TTL, LIFECYCLE_UNKNOWN_TTL, LIFECYCLE_NOT_LISTED_TTL) == (90 * DAY, 7 * DAY, 30 * DAY)


class TestSchema:
    def test_small_columns_before_the_answer_and_age_indexes(self, store):
        """prune() scans by source and time: the large answer column comes last, so the scan
        doesn't read its overflow pages, and each delete is a range on an index."""
        columns = [row[1] for row in store._conn.execute("PRAGMA table_info(answers)")]
        assert columns == ["source", "key", "found", "fetched_at", "answer"]
        columns = [row[1] for row in store._conn.execute("PRAGMA table_info(lifecycle)")]
        assert columns.index("observed_at") < columns.index("mpn") < columns.index("raw")
        indexes = {row[1] for row in store._conn.execute("SELECT * FROM sqlite_master WHERE type = 'index'")}
        assert {"answers_age", "lifecycle_age"} <= indexes
        plan = " ".join(str(row) for row in store._conn.execute(
            "EXPLAIN QUERY PLAN DELETE FROM answers WHERE source = 'mouser' AND found = 1 AND fetched_at <= 5"))
        assert "answers_age" in plan

    def test_prune_keeps_each_kind_for_its_lifetime(self, store, clock):
        store.put_answer("mouser", "LM358P", {"results": [1]}, True)
        store.put_answer("mouser", "NOPE", {"not_found": True}, False)
        store.put_readings([reading(), reading(mpn="NOPE1", maker="", status="unknown", raw=None, found=False),
                            reading(mpn="ODD1", status="unknown", raw="Odd")])
        clock.advance(DAY)
        store.prune()
        assert store.get_answer("mouser", "LM358P") is not None
        assert store._conn.execute("SELECT COUNT(*) FROM answers").fetchone()[0] == 1  # the miss is gone
        clock.advance(LIFECYCLE_UNKNOWN_TTL - DAY)
        store.prune()
        assert {r[0] for r in store._conn.execute("SELECT mpn FROM lifecycle")} == {"LM358P", "NOPE1"}
        clock.advance(LIFECYCLE_NOT_LISTED_TTL - LIFECYCLE_UNKNOWN_TTL)
        store.prune()
        assert {r[0] for r in store._conn.execute("SELECT mpn FROM lifecycle")} == {"LM358P"}


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

    @pytest.mark.parametrize("found, ttl", [(False, LIFECYCLE_NOT_LISTED_TTL), (True, LIFECYCLE_UNKNOWN_TTL)],
                             ids=["not_listed", "unknown"])
    def test_not_listed_30_days_and_unknown_a_week(self, store, clock, found, ttl):
        """An unknown status a week; "not listed" 30 days (decision 2026-11-18: mostly parts neither
        distributor carries, each costing a request whenever its answer expires)."""
        store.put_readings([reading(maker="" if not found else "TI", status="unknown", raw=None, found=found)])
        clock.advance(ttl - 1)
        assert len(store.readings("LM358P")) == 1
        store.prune()
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

    def test_not_listed_is_the_spellings_own(self, store):
        """DigiKey matches the spelling asked: a miss for LM358-P was found by mpn_key and answered
        LM358P not_found for 30 days."""
        store.put_not_listed("LM358-P", "digikey")
        assert [(r.found, r.source) for r in store.readings(" lm358-p")] == [(False, "digikey")]
        assert store.readings("LM358P") == [] and store.readings("LM358 P") == []
        store.put_not_listed("LM358P", "digikey")  # each spelling its own row
        assert len(store.readings("LM358P")) == len(store.readings("LM358-P")) == 1
        store.put_readings([reading(source="digikey")])  # a listing drops every spelling's miss
        assert [r.found for r in store.readings("LM358-P")] == [True]

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


SAME_MAKERS = [
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
    # JLCPCB's names for whole families against Mouser's and DigiKey's (review 2026-11-18)
    ("Vishay Intertech", "Vishay / Siliconix"),
    ("Vishay Intertech", "Vishay / Dale"),
    ("Vishay Intertech", "Vishay Siliconix"),
    ("Vishay Intertech", "Vishay General Semiconductor - Diodes Division"),
    ("Vishay Dale", "Vishay Intertech"),  # the alias
    ("OSRAM Opto Semicon", "ams OSRAM"),
    ("OSRAM Opto Semicon", "ams-OSRAM USA INC."),
    ("AMS", "ams OSRAM"),  # JLCPCB's "AMS" (AS5047P), though the alias "ams" is Advanced Monolithic Systems
    ("NCC(Nippon Chemi-Con)", "United Chemi-Con"),
    ("Seiko Epson", "EPSON"),
    ("Seiko Epson", "Epson Timing"),
    ("Infineon/Cypress Semicon", "Infineon Technologies"),
    ("Infineon/Cypress Semicon", "Cypress Semiconductor"),
    ("Infineon Technologies", "Cypress Semiconductor"),
    ("SKYWORKS/SILICON LABS", "Silicon Labs"),
    ("SKYWORKS/SILICON LABS", "Skyworks Solutions, Inc."),
    ("GigaDevice Semicon Beijing", "GigaDevice Semiconductor (HK) Limited"),
    ("Analog Devices Inc./Maxim Integrated", "Maxim Integrated"),
    ("HRS(Hirose)", "Hirose Connector"),
    ("ST Microelectronics", "STMicroelectronics"),
    ("ST Micro", "STMicroelectronics"),
    ("ON Semiconductor", "onsemi"),
    # Review 2026-11-18: JLCPCB's "Seiko" is Seiko Instruments; "HK" (HK32 MCUs) is a maker, not a region
    ("Seiko", "Seiko Instruments"),
    ("Seiko", "Seiko Instruments Inc."),
    ("HK", "HK Ltd"),
    ("hk32", "HK"),  # the alias resolves to JLCPCB's "HK"
]
DIFFERENT_MAKERS = [
    ("ST(Semtech)", "STMicroelectronics"),  # a short name must be whole
    ("ST(Semtech)", "ST Microelectronics"),  # an abbreviation before a full name isn't a prefix
    ("ST(Semtech)", "ST"),  # the alias ST is STMicroelectronics
    ("UMW(Youtai Semiconductor Co., Ltd.)", "Texas Instruments"),
    ("Silicon Labs", "Silicon Storage Technology"),
    ("onsemi", "Nexperia"),
    ("Analogix", "Analog Devices"),
    ("Skyworks Solutions", "Silicon Labs"),  # only JLCPCB's combined name is both
    ("Seiko Epson", "Seiko Instruments"),
    ("Vishay Intertech", "Diodes Incorporated"),
    ("HRS(Hirose)", "HRS Electronics"),
    ("OSRAM Opto Semicon", "Advanced Monolithic Systems"),
    ("Seiko", "Seiko Epson"),  # JLCPCB lists Epson as "Seiko Epson" and Seiko Instruments as "Seiko"
    ("Seiko", "EPSON"),
    ("Seiko", "Epson Timing"),
    ("HK", "GigaDevice Semiconductor (HK) Limited"),  # a region inside another maker's name
    ("HK", "HKR(Hong Kong Resistors)"),
]


class TestMakers:
    @pytest.mark.parametrize("a, b", SAME_MAKERS, ids=[f"same{i}" for i in range(len(SAME_MAKERS))])
    def test_same_maker(self, a, b):
        assert makers_match(a, b) and makers_match(b, a)

    @pytest.mark.parametrize("a, b", DIFFERENT_MAKERS, ids=[f"diff{i}" for i in range(len(DIFFERENT_MAKERS))])
    def test_different_makers(self, a, b):
        assert not makers_match(a, b) and not makers_match(b, a)

    def test_also_as_keeps_the_numbers_own_listing(self, store):
        """DigiKey lists a JST part both bare and with (LF)(SN): filing the bare one's reading under
        the number asked mustn't replace that number's own (they can differ)."""
        asked = "B2B-PH-K-S(LF)(SN)"
        store.put_readings([reading(mpn=asked, maker="JST", source="digikey", status="active", raw="Active"),
                            reading(mpn="B2B-PH-K-S", maker="JST", source="digikey", status="obsolete", raw="Obsolete")],
                           also_as=asked)
        assert [(r.mpn, r.status) for r in store.readings(asked)] == [(asked, "active")]
        assert [r.status for r in store.readings("B2B-PH-K-S")] == ["obsolete"]
        store.put_readings([reading(mpn="B2B-PH-K-S", maker="JST", source="digikey", status="obsolete", raw="Obsolete")],
                           also_as="455-1704-ND")  # nothing of its own there: filed under it too
        assert [r.status for r in store.readings("455-1704-ND")] == ["obsolete"]

    def test_one_key_per_maker(self):
        assert maker_key("Texas Instruments Inc.") == maker_key("texas instruments") == "texas instruments"

    def test_a_maker_name_never_has_an_empty_or_not_listed_key(self):
        """JLCPCB's maker "HK" was all region words, so its key was "", which it shared with the "not
        listed" rows (a reading without a maker has it too). JLCPCB's "--" (no letters or digits) was
        "" too."""
        assert maker_key("HK") == maker_key("HK Ltd") == maker_key("hk32") == "hk"
        assert maker_key("--") == "#--" and maker_key("Seiko") == "seiko instruments"
        assert maker_key("GigaDevice Semicon Beijing") == "gigadevice semicon"  # regions still left out
        for name in ("HK", "--", "Ltd", "Asia", "华为", "ß", "*", "Seiko", "Seiko Epson", "NXP USA Inc."):
            assert maker_key(name) not in ("", NOT_LISTED_MAKER_KEY), name
        assert maker_key("") == maker_key("  ") == maker_key(None) == ""

    def test_jlcpcbs_ams_is_keyed_as_ams_osram(self):
        """The key follows what JLCPCB means by "AMS" (ams OSRAM), not its alias; the matching
        still takes "AMS" as either maker."""
        assert maker_key("AMS") == maker_key("ams OSRAM") == maker_key("ams-OSRAM USA INC.") == "ams osram"
        assert maker_key("Advanced Monolithic Systems") == "advanced monolithic systems"
        assert makers_match("AMS", "ams OSRAM") and makers_match("AMS", "Advanced Monolithic Systems")

    @pytest.mark.parametrize("catalog,company,alias_company", [
        ("Samsung", "Samsung Semiconductor", "Samsung Electro-Mechanics"),
        ("FUJITSU", "Fujitsu Components", "RAMXEED/FUJITSU"),
        ("SEMTECH", "Semtech Corporation", "ST(Semtech)"),
        ("GD", "GD (HER rectifiers)", "GigaDevice Semicon Beijing"),
    ], ids=["samsung", "fujitsu", "semtech", "gd"])
    def test_jlcpcbs_short_names_keep_their_own_key(self, catalog, company, alias_company):
        """JLCPCB's short maker names are keyed as the company its catalog means, never merged with
        the company their search alias names (two makers' readings of one number would share a key)."""
        assert maker_key(catalog) == maker_key(company)
        assert maker_key(catalog) != maker_key(alias_company)

    @pytest.mark.parametrize("maker", ["HK", ""], ids=["hk", "none"])
    def test_not_listed_never_replaces_a_reading(self, store, maker):
        """A "not listed" row and a reading by a maker whose key was "" (HK's, or a reading without
        a maker) shared one row, so a later "not listed" overwrote the reading."""
        store.put_readings([reading(mpn="HK32F103VET6", maker=maker, status="obsolete", raw="Obsolete")])
        store.put_not_listed("HK32F103VET6", "mouser")
        assert sorted((r.found, r.status) for r in store.readings("HK32F103VET6")) == [
            (False, "unknown"), (True, "obsolete")]
        store.put_readings([reading(mpn="HK32F103VET6", maker=maker, status="obsolete", raw="Obsolete")])
        assert [r.found for r in store.readings("HK32F103VET6")] == [True]  # the reading drops "not listed"
