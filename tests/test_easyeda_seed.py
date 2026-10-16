"""scripts/build_easyeda_seed.py: keyword choice, search parsing, merge rules, step logic and
pacing. Fake EasyEDA, tiny components.db, no network."""

import asyncio
import datetime
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import build_easyeda_seed as seedmod  # noqa: E402
from build_easyeda_seed import (  # noqa: E402
    Blocked,
    Pacer,
    SearchPage,
    Seed,
    first_page_purity,
    keyword_candidates,
    keyword_fit,
    parse_search_item,
    parts_todo,
    run_manufacturers,
    run_names,
    run_parts,
    run_validate,
    search_item_maker,
)
from pcbparts_mcp.easyeda_store import SeedRow, read_seed_csv  # noqa: E402

NOW = "2026-10-12T12:00:00Z"  # the seed script's clock in these tests
OLD = "2026-01-01T00:00:00Z"
REAL_TODAY, REAL_CHECKED_NOW = seedmod.today, seedmod.checked_now


@pytest.fixture(autouse=True)
def fixed_clock(monkeypatch):
    monkeypatch.setattr(seedmod, "checked_now", lambda: NOW)
    monkeypatch.setattr(seedmod, "today", lambda: NOW[:10])


def uuid(n: int) -> str:
    return f"{n:032x}"


def add_parts(db: sqlite3.Connection, maker: str, start: int, count: int) -> None:
    db.executemany("INSERT INTO components VALUES (?, ?, 'e', ?, ?)",
                   [(f"C{start + i}", maker, i, f"{maker[:2]}-{start + i}") for i in range(count)])
    db.commit()


@pytest.fixture
def db(tmp_path) -> sqlite3.Connection:
    """Our parts: ACME (C1-C4), Beta(Long Name) (C10-C11), and one TI part."""
    conn = sqlite3.connect(tmp_path / "components.db")
    conn.execute("CREATE TABLE components (lcsc TEXT PRIMARY KEY, manufacturer TEXT, library_type TEXT, stock INTEGER, "
                 "mpn TEXT)")
    conn.executemany("INSERT INTO components VALUES (?, ?, ?, ?, ?)", [
        ("C1", "ACME", "e", 10, "AC-1"), ("C2", "ACME", "b", 5, "AC-2"), ("C3", "ACME", "p", 50, "AC-3"),
        ("C4", "ACME", "e", 500, "AC-4"),
        ("C10", "Beta(Long Name)", "e", 1, "B-10"), ("C11", "Beta(Long Name)", "b", 900, "B-11"),
        ("C20", "Texas Instruments", "e", 7, "TPS1"),
    ])
    conn.commit()
    return conn


@pytest.fixture
def seed(tmp_path) -> Seed:
    return Seed.load(tmp_path / "easyeda" / "footprints.csv", tmp_path / "easyeda" / "seed_state.json")


class FakeEasyEDA:
    """search: {keyword: [page1 items, page2 items, ...]} with a facet per keyword and EasyEDA
    manufacturer names per part; products: {lcsc: SeedRow | None | Exception}."""

    def __init__(self, search=None, facets=None, products=None, fail=None, makers=None):
        self.search_data = search or {}
        self.facets = facets or {}
        self.makers = makers or {}
        self.products_data = products or {}
        self.fail = fail or {}
        self.calls: list[tuple] = []
        self.pacer = Pacer(7.0, clock=lambda: 0.0, sleep=lambda s: asyncio.sleep(0))

    async def search(self, keyword, page, page_size):
        self.calls.append(("search", keyword, page))
        if keyword in self.fail:
            raise self.fail[keyword]
        pages = self.search_data.get(keyword, [])
        items = pages[page - 1] if page <= len(pages) else []
        return SearchPage(self.facets.get(keyword, sum(len(p) for p in pages)), items,
                          {lcsc: self.makers[lcsc] for lcsc, _, _ in items if lcsc in self.makers})

    async def products(self, lcsc):
        self.calls.append(("products", lcsc))
        answer = self.products_data.get(lcsc)
        if isinstance(answer, Exception):
            raise answer
        return answer


# --- Pure helpers ------------------------------------------------------------------------


class TestKeywords:
    @pytest.mark.parametrize("name, expected", [
        ("YAGEO", ["YAGEO"]),
        ("UNI-ROYAL(Uniroyal Elec)", ["UNI-ROYAL", "Uniroyal Elec", "UNI-ROYAL(Uniroyal Elec)"]),
        ("FH (Guangdong Fenghua Advanced Tech)", ["FH", "Guangdong Fenghua Advanced Tech",
                                                  "FH (Guangdong Fenghua Advanced Tech)"]),
        ("HONGLITRONIC(Hongli Zhihui (HONGLITRONIC))", ["HONGLITRONIC", "Hongli Zhihui",
                                                        "HONGLITRONIC(Hongli Zhihui (HONGLITRONIC))"]),
        ("Texas Instruments", ["TI", "Texas Instruments"]),
        ("X(Y)", ["X(Y)"]),  # one-letter forms are too vague to search
    ])
    def test_candidates(self, name, expected):
        assert keyword_candidates(name) == expected

    def test_fit(self):
        assert keyword_fit(44495, 21004) == "ok"  # YAGEO: EasyEDA also lists out-of-stock parts
        assert keyword_fit(4 * 100 + 4001, 100) == "broad"
        assert keyword_fit(3646, 183) == "ok"  # HX: two pages is cheap enough
        assert keyword_fit(219, 21748) == "narrow"  # "Texas Instruments"
        assert keyword_fit(3, 40) == "ok"  # small manufacturers aren't judged on ratio

    def test_fit_purity(self):
        assert keyword_fit(30564, 6495, 0.9) == "ok"  # onsemi: LCSC lists far more than we stock
        assert keyword_fit(30564, 6495, 0.5) == "ok"
        assert keyword_fit(30564, 6495, 0.3) == "broad"
        assert keyword_fit(30564, 6495, None) == "broad"  # too few results in our DB to judge

    def test_first_page_purity(self):
        ours = {f"C{i}": "Big" if i < 20 else "Other" for i in range(25)}
        items = [(f"C{i}", uuid(i), None) for i in range(25)] + [("C999", uuid(999), None)]  # C999 isn't ours
        assert first_page_purity(SearchPage(26, items), ours, "Big") == 0.8
        assert first_page_purity(SearchPage(19, items[:19]), ours, "Big") is None


class TestParseSearchItem:
    def test_maker(self):
        def item(c_para):
            return {"dataStr": {"head": {"c_para": c_para}}}
        assert search_item_maker(item({"Manufacturer": "ADI(亚德诺)", "Supplier Part": "C9669"})) == "ADI(亚德诺)"
        assert search_item_maker(item({"BOM_Manufacturer": " ST(意法半导体) "})) == "ST(意法半导体)"  # older records
        assert search_item_maker(item({"Manufacturer": "null", "BOM_Manufacturer": "X"})) == "X"
        assert search_item_maker(item({"Manufacturer": "null"})) is None
        assert search_item_maker(item({"BOM_Manufacturer": " "})) is None
        assert search_item_maker(item({})) is None
        assert search_item_maker({}) is None

    def test_lcsc_from_lcsc_object_or_c_para(self):
        item = {"uuid": uuid(1), "ownerUuid": seedmod.LCSC_OWNER_UUID, "lcsc": {"number": "C9864"},
                "dataStr": {"head": {"puuid": uuid(2), "c_para": {"Supplier Part": "C9864"}}}}
        assert parse_search_item(item) == ("C9864", uuid(1), uuid(2))
        del item["lcsc"]
        assert parse_search_item(item) == ("C9864", uuid(1), uuid(2))

    @pytest.mark.parametrize("change", [
        {"ownerUuid": "someone-else"},
        {"uuid": None},
        {"lcsc": {"number": "9864"}},
    ])
    def test_rejects(self, change):
        item = {"uuid": uuid(1), "ownerUuid": seedmod.LCSC_OWNER_UUID, "lcsc": {"number": "C9864"},
                "dataStr": {"head": {"puuid": uuid(2)}}}
        item.update(change)
        assert parse_search_item(item) is None

    def test_missing_footprint_uuid(self):
        item = {"uuid": uuid(1), "lcsc": {"number": "C1"}, "dataStr": {"head": {}}}
        assert parse_search_item(item) == ("C1", uuid(1), None)


class TestPacer:
    async def test_spacing(self):
        now = [0.0]
        slept = []

        async def sleep(seconds):
            slept.append(seconds)
            now[0] += seconds
        pacer = Pacer(7.0, clock=lambda: now[0], sleep=sleep)
        await pacer.wait()
        now[0] += 2.0
        await pacer.wait()
        now[0] += 10.0
        await pacer.wait()
        assert slept == [5.0]
        assert pacer.requests == 3


class TestMergeRules:
    def test_search_adds_has_footprint(self, seed):
        seed.add_search_answer("C1", uuid(1), uuid(2))
        assert seed.rows["C1"] == SeedRow("C1", True, uuid(1), uuid(2), NOW, "s")

    @pytest.mark.parametrize("symbol_uuid, footprint_uuid", [("not-hex", None), (uuid(1), "short")])
    def test_malformed_search_result_skipped(self, seed, symbol_uuid, footprint_uuid):
        """A row the CSV reader would reject must never be written."""
        seed.add_search_answer("C1", symbol_uuid, footprint_uuid)
        assert "C1" not in seed.rows and "C1" not in seed.seen

    async def test_products_answer_without_symbol_uuid_left_unanswered(self):
        class FakeClient:
            async def _check_easyeda_footprint(self, lcsc):
                return {"has_easyeda_footprint": True, "easyeda_symbol_uuid": None,
                        "easyeda_footprint_uuid": uuid(2)}, "checked"
        easyeda = seedmod.EasyEDA(FakeClient(), Pacer(7.0, clock=lambda: 0.0, sleep=lambda s: asyncio.sleep(0)))
        assert await easyeda.products("C1") is None

    def test_two_components_for_one_part_are_skipped(self, seed):
        seed.add_search_answer("C1", uuid(1), uuid(2))
        seed.add_search_answer("C1", uuid(1), uuid(2))  # same answer on two pages is fine
        assert "C1" in seed.rows
        seed.add_search_answer("C1", uuid(3), uuid(2))
        assert "C1" not in seed.rows
        assert seed.ambiguous == {"C1"}
        seed.save()
        assert Seed.load(seed.csv_path, seed.state_path).ambiguous == {"C1"}
        seed.add_search_answer("C1", uuid(1), uuid(2))
        assert "C1" not in seed.rows

    def test_two_components_spotted_across_runs_of_one_crawl(self, seed):
        seed.add_search_answer("C1", uuid(1), uuid(2))
        seed.save()
        resumed = Seed.load(seed.csv_path, seed.state_path)
        assert resumed.seen == {"C1": (uuid(1), uuid(2))}
        resumed.add_search_answer("C1", uuid(3), uuid(2))
        assert "C1" not in resumed.rows and resumed.ambiguous == {"C1"}

    def test_unchanged_answer_keeps_its_date(self, seed):
        seed.rows["C1"] = SeedRow("C1", True, uuid(1), uuid(2), OLD, "s")
        seed.rows["C2"] = SeedRow("C2", True, uuid(3), uuid(4), OLD, "s")
        seed.add_search_answer("C1", uuid(1), uuid(2))
        seed.add_search_answer("C2", uuid(3), uuid(9))
        assert seed.rows["C1"] == SeedRow("C1", True, uuid(1), uuid(2), OLD, "s")  # a refresh leaves it alone
        assert seed.rows["C2"] == SeedRow("C2", True, uuid(3), uuid(9), NOW, "s")
        assert set(seed.seen) == {"C1", "C2"}

    def test_products_answer_keeps_the_date_of_the_same_footprint(self, seed):
        seed.rows["C1"] = SeedRow("C1", True, uuid(1), uuid(2), OLD, "s")
        seed.rows["C2"] = SeedRow("C2", False, None, None, OLD, "p")
        seed.rows["C3"] = SeedRow("C3", True, uuid(5), uuid(6), OLD, "s")
        seed.add_products_answer(SeedRow("C1", True, uuid(1), uuid(2), NOW, "p"))
        seed.add_products_answer(SeedRow("C2", False, None, None, NOW, "p"))
        seed.add_products_answer(SeedRow("C3", True, uuid(7), uuid(6), NOW, "p"))
        assert seed.rows["C1"] == SeedRow("C1", True, uuid(1), uuid(2), OLD, "p")
        assert seed.rows["C2"].checked == NOW  # the server re-checks "no footprint" a week after this
        assert seed.rows["C3"] == SeedRow("C3", True, uuid(7), uuid(6), NOW, "p")

    def test_products_answers_are_authoritative(self, seed):
        seed.rows["C1"] = SeedRow("C1", True, uuid(5), uuid(6), OLD, "p")
        seed.add_search_answer("C1", uuid(1), uuid(2))
        assert seed.rows["C1"].symbol_uuid == uuid(5)
        seed.rows["C2"] = SeedRow("C2", False, None, None, "2026-10-12T00:00:01Z", "p")  # earlier today
        seed.add_search_answer("C2", uuid(1), uuid(2))
        assert seed.rows["C2"].has_footprint is False

    def test_search_overrides_an_older_no_footprint(self, seed):
        seed.rows["C1"] = SeedRow("C1", False, None, None, OLD, "p")
        seed.add_search_answer("C1", uuid(1), uuid(2))
        assert seed.rows["C1"] == SeedRow("C1", True, uuid(1), uuid(2), NOW, "s")


# --- Steps -------------------------------------------------------------------------------


class TestManufacturers:
    async def test_records_our_parts_and_progress(self, seed, db, tmp_path):
        fake = FakeEasyEDA(
            search={
                "ACME": [[("C1", uuid(1), uuid(9)), ("C2", uuid(2), uuid(9)), ("C999", uuid(3), uuid(9))],
                         [("C3", uuid(4), None), ("C10", uuid(5), uuid(9))]],
                "Beta": [[("C11", uuid(6), uuid(9))]],
            },
            facets={"ACME": 5, "Beta": 1},
        )
        await run_manufacturers(seed, db, fake, 3, None, None)  # 3 per page: ACME takes 2 pages
        # C999 isn't ours; C10 is ours (another manufacturer's part found under "ACME") and counts
        assert set(seed.rows) == {"C1", "C2", "C3", "C10", "C11"}
        assert all(r.source == "s" and r.has_footprint for r in seed.rows.values())
        progress = seed.state["manufacturers"]
        assert progress["ACME"]["matched"] == 3 and progress["ACME"]["coverage"] == 0.75
        assert progress["Beta(Long Name)"]["keywords"] == ["Beta"]
        assert all(e["done"] for e in progress.values())
        assert progress["ACME"]["tried"][0] | {"returned": 5, "unique": 5} == progress["ACME"]["tried"][0]
        assert seed.state["last_search_at"] > 0
        assert ("search", "ACME", 2) in fake.calls
        # Saved to disk, and a second run has nothing left to do
        assert set(read_seed_csv(seed.csv_path)) == set(seed.rows)
        fake.calls.clear()
        await run_manufacturers(Seed.load(seed.csv_path, seed.state_path), db, fake, 3, None, None)
        assert fake.calls == []
        await run_manufacturers(seed, db, fake, 3, ["Beta(Long Name)"], None, redo=True)
        assert fake.calls == [("search", "Beta", 1)]  # --redo searches a done one again

    async def test_new_crawl_forgets_the_last_crawls_answers(self, seed, db):
        seed.rows["C11"] = SeedRow("C11", True, uuid(7), uuid(9), OLD, "s")
        seed.seen["C11"] = (uuid(7), uuid(9))  # from the last crawl; EasyEDA re-linked it since
        fake = FakeEasyEDA(search={"Beta": [[("C11", uuid(6), uuid(9))]]})
        await run_manufacturers(seed, db, fake, 2000, ["Beta(Long Name)"], None)
        assert seed.rows["C11"] == SeedRow("C11", True, uuid(6), uuid(9), NOW, "s")
        assert not seed.ambiguous

    async def test_broad_keyword_skipped_narrow_one_kept(self, seed, db):
        fake = FakeEasyEDA(
            search={"TI": [[("C20", uuid(1), uuid(2))]], "Texas Instruments": [[]]},
            facets={"TI": 1_000_000},  # too broad for our 1 part
        )
        await run_manufacturers(seed, db, fake, 2000, ["Texas Instruments"], None)
        entry = seed.state["manufacturers"]["Texas Instruments"]
        assert [t["fit"] for t in entry["tried"]] == ["broad", "ok"]
        assert entry["keywords"] == ["Texas Instruments"]
        assert ("search", "TI", 2) not in fake.calls  # no paging through a broad keyword
        assert seed.rows["C20"].source == "s"  # but its first page's answers are kept

    async def test_server_error_falls_back_to_smaller_pages(self, seed, db):
        class Picky(FakeEasyEDA):
            async def search(self, keyword, page, page_size):
                if page_size > seedmod.FALLBACK_PAGE_SIZE:
                    self.calls.append(("search", keyword, page, page_size))
                    raise seedmod.ServerError("search HTTP 500")
                return await super().search(keyword, page, page_size)

        fake = Picky(search={"Beta": [[("C11", uuid(11), uuid(9))]]})
        await run_manufacturers(seed, db, fake, 5000, ["Beta(Long Name)"], None)
        entry = seed.state["manufacturers"]["Beta(Long Name)"]
        assert entry["done"] and entry["tried"][0]["page_size"] == 2000 and "C11" in seed.rows
        assert fake.calls == [("search", "Beta", 1, 5000), ("search", "Beta", 1)]

    async def test_pages_capped(self, seed, db):
        add_parts(db, "Big", 100, 30)
        fake = FakeEasyEDA(search={"Big": [[(f"C{100 + i}", uuid(100 + i), uuid(9)) for i in range(25)]]},
                           facets={"Big": 25_000})
        await run_manufacturers(seed, db, fake, 5000, ["Big"], None)
        attempt = seed.state["manufacturers"]["Big"]["tried"][0]
        assert attempt["pages"] == 5 and attempt["capped"]  # past 10,000 only partly reachable, still fetched
        assert ("search", "Big", 5) in fake.calls
        add_parts(db, "Huge", 200, 30)
        fake = FakeEasyEDA(search={"Huge": [[(f"C{200 + i}", uuid(200 + i), uuid(9)) for i in range(25)]]},
                           facets={"Huge": 10_000_000})
        await run_manufacturers(seed, db, fake, 5000, ["Huge"], None)
        assert max(c[2] for c in fake.calls if c[1] == "Huge") == seedmod.MAX_PAGES

    async def test_big_keyword_searched_when_pure(self, seed, db):
        add_parts(db, "Big", 100, 30)
        add_parts(db, "Ensheng Electronics", 200, 1)
        page1 = [(f"C{100 + i}", uuid(100 + i), uuid(9)) for i in range(25)]
        fake = FakeEasyEDA(
            search={"Big": [page1, [(f"C{125 + i}", uuid(125 + i), uuid(9)) for i in range(5)]],
                    "Ensheng Electronics": [page1]},  # a generic match: someone else's parts
            facets={"Big": 8000, "Ensheng Electronics": 15194},  # far over 4x our parts plus the slack
        )
        await run_manufacturers(seed, db, fake, 400, ["Big", "Ensheng Electronics"], None)
        big = seed.state["manufacturers"]["Big"]
        assert big["tried"][0]["fit"] == "ok" and big["tried"][0]["purity"] == 1.0
        assert big["matched"] == 30 and ("search", "Big", 20) in fake.calls
        ensheng = seed.state["manufacturers"]["Ensheng Electronics"]
        assert ensheng["tried"][0]["fit"] == "broad" and ensheng["tried"][0]["purity"] == 0.0
        assert ("search", "Ensheng Electronics", 2) not in fake.calls

    async def test_failure_leaves_it_to_do(self, seed, db):
        fake = FakeEasyEDA(search={"Beta": [[("C11", uuid(6), uuid(9))]]}, fail={"ACME": TimeoutError("slow")})
        await run_manufacturers(seed, db, fake, 2000, None, None)
        assert not seed.state["manufacturers"]["ACME"].get("done")
        assert seed.state["manufacturers"]["Beta(Long Name)"]["done"]

    async def test_block_stops_the_run(self, seed, db):
        fake = FakeEasyEDA(fail={"ACME": Blocked("search HTTP 403")})
        with pytest.raises(Blocked):
            await run_manufacturers(seed, db, fake, 2000, None, None)
        assert fake.calls == [("search", "ACME", 1)]


class TestNames:
    def low(self, seed, maker, our_parts, tried, keywords, coverage=0.0):
        seed.state["manufacturers"][maker] = {"done": True, "our_parts": our_parts, "tried": tried,
                                             "keywords": keywords, "matched": 0, "coverage": coverage}

    async def test_easyeda_name_found_and_searched(self, seed, db):
        self.low(seed, "ACME", 4, [{"keyword": "ACME", "facet": 0, "pages": 0, "fit": "ok"}], ["ACME"])
        self.low(seed, "Texas Instruments", 1, [], ["TI"], coverage=1.0)  # fine already: skipped
        fake = FakeEasyEDA(
            search={"AC-4": [[("C4", uuid(4), uuid(9)), ("C998", uuid(5), uuid(9))]],
                    "ACM": [[("C1", uuid(1), uuid(9)), ("C2", uuid(2), uuid(9)), ("C4", uuid(4), uuid(9))]]},
            makers={"C4": "ACM(艾克米)", "C998": "Other"},
        )
        await run_names(seed, db, fake, 2000, None, None)
        # The top-stock part's search names the manufacturer; its first candidate fits, so it stops
        assert fake.calls == [("search", "AC-4", 1), ("search", "ACM", 1)]
        entry = seed.state["manufacturers"]["ACME"]
        assert entry["lcsc_name"] == "ACM(艾克米)" and entry["keywords"] == ["ACME", "ACM"]
        assert entry["matched"] == 3 and entry["coverage"] == 0.75 and len(entry["tried"]) == 2
        assert set(seed.rows) == {"C1", "C2", "C4"}
        assert seed.state["last_search_at"] > 0
        fake.calls.clear()
        await run_names(Seed.load(seed.csv_path, seed.state_path), db, fake, 2000, None, None)
        assert fake.calls == []  # done, resumable

    async def test_known_footprint_parts_looked_up_first(self, seed, db):
        self.low(seed, "ACME", 4, [], [])
        seed.rows["C2"] = SeedRow("C2", True, uuid(2), uuid(9), NOW, "s")
        fake = FakeEasyEDA(search={"AC-2": [[("C2", uuid(2), uuid(9))]]}, makers={"C2": "ACME"})
        await run_names(seed, db, fake, 2000, None, None)
        assert fake.calls[0] == ("search", "AC-2", 1)  # C4 has more stock, but C2 is known to be there

    async def test_name_not_found_broad_keyword_retried(self, seed, db):
        self.low(seed, "Beta(Long Name)", 2, [{"keyword": "Beta", "facet": 9000, "pages": 5, "fit": "broad"},
                                               {"keyword": "Long Name", "facet": 9000, "pages": 5, "fit": "broad"}],
                 [])
        fake = FakeEasyEDA(search={"Beta": [[("C11", uuid(11), uuid(9))]]})  # not broad any more
        await run_names(seed, db, fake, 2000, None, None)
        # Both parts searched by MPN (most stock first), neither found, then the old keywords again
        assert fake.calls == [("search", "B-11", 1), ("search", "B-10", 1), ("search", "Beta", 1)]
        entry = seed.state["manufacturers"]["Beta(Long Name)"]
        assert entry["lcsc_name"] is None and entry["keywords"] == ["Beta"] and entry["matched"] == 1

    async def test_failure_and_block(self, seed, db):
        self.low(seed, "ACME", 4, [], [])
        fake = FakeEasyEDA(fail={"AC-4": TimeoutError("slow")})
        await run_names(seed, db, fake, 2000, None, None)
        assert "lcsc_name" not in seed.state["manufacturers"]["ACME"]  # still to do
        fake = FakeEasyEDA(fail={"AC-4": Blocked("search HTTP 403")})
        with pytest.raises(Blocked):
            await run_names(seed, db, fake, 2000, None, None)


class TestParts:
    def test_order_unanswered_by_type_then_stock_then_stale(self, seed, db):
        seed.rows["C3"] = SeedRow("C3", True, uuid(1), None, OLD, "s")
        seed.rows["C2"] = SeedRow("C2", False, None, None, OLD, "p")
        seed.rows["C11"] = SeedRow("C11", False, None, None, NOW, "p")
        assert parts_todo(seed, db, "bp", 30) == ["C2"]  # C11 fresh, C3 has one, C2's "none" is stale
        assert parts_todo(seed, db, "bpe", 30) == ["C4", "C1", "C20", "C10", "C2"]

    async def test_answers_saved_and_block_stops(self, seed, db):
        fake = FakeEasyEDA(products={
            "C11": SeedRow("C11", True, uuid(1), uuid(2), NOW, "p"),
            "C2": None,  # lookup failed: stays unanswered
            "C3": Blocked("/api/products blocked"),
        })
        with pytest.raises(Blocked):
            await run_parts(seed, db, fake, "bp", None, 30)
        assert [c for c in fake.calls] == [("products", "C11"), ("products", "C2"), ("products", "C3")]
        assert set(seed.rows) == {"C11"}

    async def test_max_requests(self, seed, db):
        fake = FakeEasyEDA(products={})
        await run_parts(seed, db, fake, "bpe", 2, 30)
        assert len(fake.calls) == 2


class TestValidate:
    async def test_mismatch_counted_and_replaced(self, seed, monkeypatch):
        seed.rows["C1"] = SeedRow("C1", True, uuid(1), uuid(2), OLD, "s")
        seed.rows["C2"] = SeedRow("C2", True, uuid(3), uuid(4), OLD, "s")
        seed.rows["C3"] = SeedRow("C3", False, None, None, NOW, "p")
        fake = FakeEasyEDA(products={
            "C1": SeedRow("C1", True, uuid(1), uuid(2), NOW, "p"),
            "C2": SeedRow("C2", True, uuid(9), uuid(4), NOW, "p"),
        })
        assert await run_validate(seed, fake, 50) == 1
        assert {c[1] for c in fake.calls} == {"C1", "C2"}  # only search answers are sampled
        assert seed.rows["C2"] == SeedRow("C2", True, uuid(9), uuid(4), NOW, "p")
        assert seed.rows["C1"] == SeedRow("C1", True, uuid(1), uuid(2), OLD, "p")  # confirmed: same date


class TestCli:
    def test_products_steps_wait_after_search(self, seed, db, tmp_path, monkeypatch):
        seed.state["last_search_at"] = seedmod.time.time() - 60
        seed.save()
        db.close()
        monkeypatch.setattr(seedmod, "make_client", lambda: pytest.fail("must not reach EasyEDA"))
        args = ["--db", str(tmp_path / "components.db"), "--csv", str(seed.csv_path), "--state", str(seed.state_path)]
        assert seedmod.main(["validate", *args]) == 3
        assert seedmod.main(["parts", *args]) == 3

    def test_refuses_fast_pacing(self, tmp_path):
        with pytest.raises(SystemExit):
            seedmod.main(["report", "--delay", "3", "--db", str(tmp_path / "x.db")])
        with pytest.raises(SystemExit):
            seedmod.main(["manufacturers", "--redo", "--db", str(tmp_path / "x.db")])  # needs --only
        with pytest.raises(SystemExit):  # EasyEDA answers HTTP 500 to 10,000
            seedmod.main(["report", "--page-size", "10000", "--db", str(tmp_path / "x.db")])

    def test_report(self, seed, db, tmp_path, capsys):
        add_parts(db, "Big", 100, 120)
        seed.rows["C2"] = SeedRow("C2", True, uuid(1), None, NOW, "s")
        for i in range(50):  # 50 of Big's 120, though its last crawl only matched 10
            seed.rows[f"C{100 + i}"] = SeedRow(f"C{100 + i}", True, uuid(i), None, NOW, "s")
        seed.state["manufacturers"]["Big"] = {"done": True, "our_parts": 120, "matched": 10, "coverage": 0.083,
                                              "keywords": ["Big"], "tried": []}
        seed.save()
        db.close()
        assert seedmod.main(["report", "--db", str(tmp_path / "components.db"), "--csv", str(seed.csv_path),
                             "--state", str(seed.state_path)]) == 0
        out = capsys.readouterr().out
        assert "basic" in out and "rows: 51 (51 from search, 0 from /api/products)" in out
        assert "  Big: 50/120 via ['Big']" in out


def test_clock_is_utc():
    before = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    checked, day = REAL_CHECKED_NOW(), REAL_TODAY()
    after = datetime.datetime.now(datetime.timezone.utc)
    moment = datetime.datetime.strptime(checked, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    assert before <= moment <= after
    assert day in {before.strftime("%Y-%m-%d"), after.strftime("%Y-%m-%d")}  # no flake at midnight
