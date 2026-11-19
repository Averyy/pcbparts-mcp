"""0.10.0: every price break JLCPCB already sends with the daily scrape, kept out of git
(data/catalog/price_tiers.tsv.gz, handed from the scrape workflow to the image build as an Actions
artifact) and listed in jlc_get_parts and jlc_get_part(mpn) replies, with price_tiers_as_of. Without
the file everything works as before: the 1-piece price only. No network: fixture payloads and a
small built catalog."""

import gzip
import json
import shutil
import sqlite3
import subprocess
import sys
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

from conftest import write_catalog_category

import pcbparts_mcp.server as server
from pcbparts_mcp.catalog_files import (
    PRICE_TIERS_FILE, pack_tiers, price_tiers_scraped_at, read_catalog, read_price_tiers, unpack_tiers,
    write_catalog, write_price_tiers,
)
from pcbparts_mcp.db import ComponentDatabase
from pcbparts_mcp.db.lookup import snapshot_prices

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import scrape_components as scrape  # noqa: E402
from build_database import build_database, load_price_tiers  # noqa: E402
from search_baseline import offline  # noqa: E402

ROOT = Path(__file__).parent.parent
SCRAPED = "2026-11-17T22:00:00+00:00"
# C25531's quantities and discount ratios (a live sample, 2026-11-17: 1, 0.778, 0.667, 0.593, 0.519,
# 0.519 of the 1-piece price; that price is made up): the last break only repeats the one before it
C25531 = [{"startNumber": 1, "productPrice": 0.0270}, {"startNumber": 1000, "productPrice": 0.0210},
          {"startNumber": 3000, "productPrice": 0.0180}, {"startNumber": 10000, "productPrice": 0.0160},
          {"startNumber": 50000, "productPrice": 0.0140}, {"startNumber": 50200, "productPrice": 0.0140}]


def api_item(code, prices, **extra):
    return {"componentCode": code, "componentModelEn": f"M{code}", "componentBrandEn": "Maker",
            "componentSpecificationEn": "0402", "stockCount": 5000, "componentLibraryType": "base",
            "componentPrices": prices, "describe": "", "attributes": [], "componentProductType": 0,
            "dataManualUrl": "x", **extra}


class TestScrapedBreaks:
    def test_every_break_kept_in_order_and_rounded(self):
        part = scrape.transform_part(api_item("C25531", [*reversed(C25531[:2]), {"startNumber": 3000, "productPrice": 0.018049}]), 7)
        assert part["$t"] == "1:0.027,1000:0.021,3000:0.018"
        assert part["$"] == 0.021  # the listing's first tier, as before
        assert unpack_tiers(part["$t"]) == [(1, 0.027), (1000, 0.021), (3000, 0.018)]

    @pytest.mark.parametrize("prices", [None, []])
    def test_no_breaks(self, prices):
        part = scrape.transform_part(api_item("C1", prices), 7)
        assert "$t" not in part and part["$"] is None

    @pytest.mark.parametrize("later", [{"startNumber": 1, "productPrice": 0.09},  # quantity twice
                                       {"startNumber": "ten", "productPrice": 0.09},
                                       {"startNumber": "10.5", "productPrice": 0.09},
                                       {"startNumber": 10.5, "productPrice": 0.09},
                                       {"startNumber": True, "productPrice": 0.09},
                                       {"startNumber": 10, "productPrice": None},
                                       {"startNumber": 0, "productPrice": 0.09},
                                       {"startNumber": 10, "productPrice": float("nan")},
                                       None], ids=["twice", "word", "halftext", "half", "bool", "noprice", "zero",
                                                   "nan", "null"])
    def test_a_malformed_break_leaves_the_one_price(self, later):
        part = scrape.transform_part(api_item("C1", [{"startNumber": 1, "productPrice": 0.1}, later]), 7)
        assert "$t" not in part and part["$"] == 0.1  # an optional file never fails the scrape

    @pytest.mark.parametrize("quantities", [("1", "100"), (1.0, 100.0), (" 1 ", "100.0")], ids=["text", "float", "spaced"])
    def test_whole_number_quantities_in_other_forms(self, quantities):
        """Every part's breaks vanished without a word if JLCPCB sent startNumber as text or 1.0."""
        prices = [{"startNumber": qty, "productPrice": price} for qty, price in zip(quantities, (0.1, 0.08))]
        assert scrape.transform_part(api_item("C1", prices), 7)["$t"] == "1:0.1,100:0.08"


def _part(code, price=0.1, tiers=None, sub=2, stock=50):
    return {"l": code, "c": sub, "s": stock, "$": price, "t": "b", "d": "10Ω", **({"$t": tiers} if tiers else {})}


CATEGORIES = [{"id": 1, "name": "Resistors"}, {"id": 2, "name": "Empty"}]
FIRST = datetime(2026, 11, 17, 22, 0, tzinfo=timezone.utc)


class TestScrapeOutputs:
    def test_tiers_file_written_and_part_files_unchanged(self, tmp_path):
        rows = [_part("C10", 0.5, "1:0.5,100:0.4"), _part("C9", 0.2, "1:0.2"), _part("C11", None)]
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": rows}, scrape.ScrapeProgress(), now=FIRST)
        catalog = tmp_path / "catalog"
        assert price_tiers_scraped_at(catalog / PRICE_TIERS_FILE) == FIRST.isoformat()
        assert list(read_price_tiers(catalog / PRICE_TIERS_FILE)) == [("C9", [(1, 0.2)]), ("C10", [(1, 0.5), (100, 0.4)])]
        committed = [json.loads(line) for path in sorted((catalog / "parts").rglob("*.jsonl"))
                     for line in path.read_text(encoding="utf-8").splitlines()]
        assert committed and all("$t" not in row for row in committed)
        assert (catalog / "prices.tsv").read_text(encoding="utf-8") == "C9\t0.2\nC10\t0.5\nC11\t\n"
        with gzip.open(catalog / PRICE_TIERS_FILE, "rt", encoding="utf-8") as stream:
            assert stream.read() == f"#scraped_at\t{FIRST.isoformat()}\nC9\t1\t0.2\nC10\t1\t0.5\nC10\t100\t0.4\n"

    def test_daily_breaks_beside_the_weekly_price(self, tmp_path):
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": [_part("C1", 0.5, "1:0.5")]},
                                    scrape.ScrapeProgress(), now=FIRST)
        later = datetime(2026, 11, 19, 22, 0, tzinfo=timezone.utc)
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": [_part("C1", 0.45, "1:0.45,10:0.4")]},
                                    scrape.ScrapeProgress(), now=later)
        catalog = tmp_path / "catalog"
        assert (catalog / "prices.tsv").read_text(encoding="utf-8") == "C1\t0.5\n"  # weekly, as before
        assert price_tiers_scraped_at(catalog / PRICE_TIERS_FILE) == later.isoformat()
        assert list(read_price_tiers(catalog / PRICE_TIERS_FILE)) == [("C1", [(1, 0.45), (10, 0.4)])]

    def test_parts_carried_over_a_gap_have_no_breaks(self, tmp_path):
        sizes = [300, 300, 300, 50]
        full = {"resistors": [_part(f"C{sub}{i:04d}", 0.1, "1:0.1", sub=sub) for sub in range(1, 5) for i in range(sizes[sub - 1])]}
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, full, scrape.ScrapeProgress(), now=FIRST)
        short = {"resistors": [p for p in full["resistors"] if p["c"] == 4]}  # three subcategories gone at once
        manifest = scrape.write_scrape_outputs(tmp_path, CATEGORIES, short, scrape.ScrapeProgress(),
                                               now=datetime(2026, 11, 18, 22, 0, tzinfo=timezone.utc))
        assert set(manifest["carried_forward"]) == {"1", "2", "3"}
        codes = [code for code, _ in read_price_tiers(tmp_path / "catalog" / PRICE_TIERS_FILE)]
        assert len(codes) == 50 and all(code.startswith("C4") for code in codes)

    def test_manifest_counts_the_parts_with_breaks(self, tmp_path):
        rows = [_part("C10", 0.5, "1:0.5,100:0.4"), _part("C9", 0.2, "1:0.2"), _part("C11", None)]
        manifest = scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": rows}, scrape.ScrapeProgress(), now=FIRST)
        assert manifest["price_tiers_parts"] == 2
        assert json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))["price_tiers_parts"] == 2

    def test_few_breaks_warn(self, tmp_path, caplog):
        rows = [_part(f"C{n}", 0.1, "1:0.1" if n < 8 else None) for n in range(1, 11)]  # 7 of 10 priced parts
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": rows}, scrape.ScrapeProgress(), now=FIRST)
        assert "::warning title=Few price tiers::7 of 10 priced parts have price breaks" in caplog.text
        caplog.clear()
        rows = [_part(f"C{n}", 0.1, "1:0.1") for n in range(1, 11)]
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": rows}, scrape.ScrapeProgress(), now=FIRST)
        assert "Few price tiers" not in caplog.text

    def test_a_failed_write_never_fails_the_scrape(self, tmp_path, monkeypatch, caplog):
        def broken(path, tiers, scraped_at):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"\x1f\x8b partial")
            raise OSError(28, "No space left on device")

        monkeypatch.setattr(scrape, "write_price_tiers", broken)
        rows = [_part("C10", 0.5, "1:0.5,100:0.4")]
        manifest = scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": rows}, scrape.ScrapeProgress(), now=FIRST)
        assert not (tmp_path / "catalog" / PRICE_TIERS_FILE).exists()  # no partial file for the upload
        assert manifest["price_tiers_parts"] == 0 and manifest["total_parts"] == 1
        assert (tmp_path / "catalog" / "prices.tsv").read_text(encoding="utf-8") == "C10\t0.5\n"
        assert "::warning title=Price tiers not written::OSError" in caplog.text

    def test_no_breaks_no_file(self, tmp_path):
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": [_part("C1", 0.5, "1:0.5")]},
                                    scrape.ScrapeProgress(), now=FIRST)
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": [_part("C1", 0.5)]},
                                    scrape.ScrapeProgress(), now=FIRST)
        assert not (tmp_path / "catalog" / PRICE_TIERS_FILE).exists()  # never an older scrape's breaks

    async def test_published_with_the_catalog(self, tmp_path, monkeypatch):
        items = [api_item("C25531", C25531), api_item("C7", None)]

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        async def categories(session):
            return [{"id": 1, "name": "Resistors", "subcategories": [{"id": 2, "name": "Chip Resistor", "count": 2}]}]

        async def scraped(subcategory, session):
            return [scrape.transform_part(item, subcategory.id) for item in items], len(items)

        monkeypatch.setattr(scrape, "create_scraper_session", Session)
        monkeypatch.setattr(scrape, "fetch_categories", categories)
        monkeypatch.setattr(scrape, "scrape_subcategory", scraped)
        monkeypatch.setattr(scrape, "WORKER_STAGGER", 0)
        await scrape.run_scraper(tmp_path, num_workers=1)
        catalog = tmp_path / "catalog"
        assert [code for code, _ in read_price_tiers(catalog / PRICE_TIERS_FILE)] == ["C25531"]
        assert all("$t" not in part for _, part in read_catalog(catalog))
        assert "$t" not in "".join(p.read_text(encoding="utf-8") for p in (catalog / "parts").rglob("*.jsonl"))
        assert not (tmp_path / ".scrape-staging").exists()


class TestTiersFile:
    def test_round_trip_and_same_bytes(self, tmp_path):
        tiers = {"C100": "1:0.5,10:0.45", "C9": "1:1.0", "C10": "5:0.2"}
        assert write_price_tiers(tmp_path / "a.gz", tiers, SCRAPED) == 3
        write_price_tiers(tmp_path / "b.gz", dict(reversed(tiers.items())), SCRAPED)
        assert (tmp_path / "a.gz").read_bytes() == (tmp_path / "b.gz").read_bytes()
        assert price_tiers_scraped_at(tmp_path / "a.gz") == SCRAPED
        assert list(read_price_tiers(tmp_path / "a.gz")) == [
            ("C9", [(1, 1.0)]), ("C10", [(5, 0.2)]), ("C100", [(1, 0.5), (10, 0.45)])]
        assert pack_tiers([(1, 0.5), (10, 1)]) == "1:0.5,10:1.0"

    @pytest.mark.parametrize("tiers", [{"C1": "0:0.5"}, {"C1": "1:-1.0"}, {"C1": "10:0.5,1:0.6"}, {"C 1": "1:0.5"}],
                             ids=["zero", "negative", "falling", "code"])
    def test_writer_rejects_bad_breaks(self, tmp_path, tiers):
        with pytest.raises(ValueError):
            write_price_tiers(tmp_path / "t.gz", tiers, SCRAPED)

    @pytest.mark.parametrize("text", [
        "C1\t1\t0.5\n",  # no header
        "#scraped_at\tyesterday\nC1\t1\t0.5\n",
        f"#scraped_at\t{SCRAPED}\nC1\t1\n",
        f"#scraped_at\t{SCRAPED}\nC1\tone\t0.5\n",
        f"#scraped_at\t{SCRAPED}\nC1\t1\tNaN\n",
        f"#scraped_at\t{SCRAPED}\nC1\t10\t0.5\nC1\t1\t0.6\n",  # quantities must rise
        f"#scraped_at\t{SCRAPED}\nC2\t1\t0.5\nC1\t1\t0.6\n",  # LCSC order
        f"#scraped_at\t{SCRAPED}\nC1\t1\t0.5\nC2\t1\t0.5\nC1\t10\t0.4\n",  # split up
    ], ids=["header", "time", "fields", "qty", "nan", "falling", "order", "split"])
    def test_reader_rejects_malformed_files(self, tmp_path, text):
        path = tmp_path / "t.gz"
        path.write_bytes(gzip.compress(text.encode("utf-8")))
        with pytest.raises(ValueError):
            price_tiers_scraped_at(path)
            list(read_price_tiers(path))

    def test_truncated_file(self, tmp_path):
        write_price_tiers(tmp_path / "t.gz", {f"C{n}": "1:0.5,10:0.4" for n in range(1, 2000)}, SCRAPED)
        data = (tmp_path / "t.gz").read_bytes()
        (tmp_path / "t.gz").write_bytes(data[: len(data) // 2])
        with pytest.raises(ValueError, match="unreadable"):
            list(read_price_tiers(tmp_path / "t.gz"))

    def test_part_files_never_hold_breaks(self, tmp_path):
        write_catalog(tmp_path, {"resistors": [_part("C1", 0.5, "1:0.5")]}, {"C1": 0.5})
        assert "$t" not in (tmp_path / "parts" / "resistors" / "2.jsonl").read_text(encoding="utf-8")
        (tmp_path / "parts" / "resistors" / "2.jsonl").write_text(
            '{"l":"C1","c":2,"t":"b","$t":"1:0.5"}\n', encoding="utf-8")
        with pytest.raises(ValueError, match="stored in TSV"):
            list(read_catalog(tmp_path))


SUBCATEGORIES = {"2": {"name": "Chip Resistor - Surface Mount", "category_id": 1, "category_name": "Resistors"}}
PARTS = [
    {"l": "C25531", "m": "0402WGF1001TCE", "f": "UNI-ROYAL", "p": "0402", "s": 900000, "t": "b", "c": 2,
     "$": 0.0271, "d": "1kΩ 0402", "a": [], "x": 0},
    {"l": "C2", "m": "RC0402", "f": "YAGEO", "p": "0402", "s": 5000, "t": "b", "c": 2, "$": 0.002, "d": "", "a": [], "x": 0},
    {"l": "C3", "m": "RC0402", "f": "Other", "p": "0402", "s": 100, "t": "e", "c": 2, "$": None, "d": "", "a": [], "x": 0},
]
TIERS = {"C25531": "1:0.027,1000:0.021,3000:0.018,10000:0.016,50000:0.014,50200:0.014",
         "C999": "1:9.0"}  # a part the catalog doesn't list (a file from another day's scrape)


def _data_dir(root, tiers_text=None, tiers=TIERS):
    write_catalog_category(root, "resistors", PARTS)
    (root / "subcategories.json").write_text(json.dumps(SUBCATEGORIES), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps(
        {"scraped_at": "2026-11-18T22:00:00+00:00", "prices_updated_at": "2026-11-12T20:00:00+00:00",
         "categories": {}}), encoding="utf-8")
    path = root / "catalog" / PRICE_TIERS_FILE
    if tiers_text is not None:
        path.write_bytes(gzip.compress(tiers_text.encode("utf-8")))
    elif tiers:
        write_price_tiers(path, tiers, SCRAPED)
    return root


def _meta(db_path):
    with closing(sqlite3.connect(db_path)) as conn:
        return (dict(conn.execute("SELECT key, value FROM metadata WHERE key LIKE 'price_tiers%'")),
                conn.execute("SELECT lcsc, tiers FROM price_tiers ORDER BY lcsc").fetchall())


class TestDatabaseBuild:
    def test_loaded_with_its_scrape_date(self, tmp_path):
        data = _data_dir(tmp_path)
        stats = build_database(data, data / "c.db", verbose=False)
        assert (stats["price_tier_parts"], stats["price_tiers_scraped_at"]) == (1, SCRAPED)
        meta, rows = _meta(data / "c.db")
        assert meta == {"price_tiers_loaded": "1", "price_tiers_parts": "1", "price_tiers_scraped_at": SCRAPED}
        assert rows == [("C25531", TIERS["C25531"])]  # C999 isn't in the catalog

    def test_without_the_file(self, tmp_path):
        data = _data_dir(tmp_path, tiers=None)
        assert build_database(data, data / "c.db", verbose=False)["price_tier_parts"] == 0
        assert _meta(data / "c.db") == ({"price_tiers_loaded": "0", "price_tiers_parts": "0"}, [])

    def test_malformed_file_loads_nothing_and_the_build_succeeds(self, tmp_path, capsys):
        # 30,000 good rows (some batches already inserted, C2, C3 and C25531 among them), then one out of order
        good = "".join(f"C{n}\t1\t0.5\n" for n in range(1, 30000))
        data = _data_dir(tmp_path, tiers_text=f"#scraped_at\t{SCRAPED}\n{good}C5\t1\t0.5\n")
        stats = build_database(data, data / "c.db", verbose=False)
        assert stats["total_parts"] == 3 and stats["price_tier_parts"] == 0
        assert _meta(data / "c.db") == ({"price_tiers_loaded": "0", "price_tiers_parts": "0"}, [])
        assert "price_tiers.tsv.gz not loaded" in capsys.readouterr().out


    @pytest.mark.parametrize("header", ["0001-01-01T00:00:00+14:00", "2024-12-31T23:59:59+00:00",
                                        "2999-01-01T00:00:00+00:00", "9999-12-31T23:59:59-14:00"],
                             ids=["year1", "early", "ahead", "year9999"])
    def test_implausible_scrape_time_loads_nothing(self, tmp_path, header, capsys):
        """The server read the header's time when it opened the database: "0001-01-01T00:00:00+14:00"
        can't be put in UTC, so it raised OverflowError at startup."""
        data = _data_dir(tmp_path, tiers_text=f"#scraped_at\t{header}\nC25531\t1\t0.5\n")
        stats = build_database(data, data / "c.db", verbose=False)
        assert (stats["price_tier_parts"], stats["price_tiers_scraped_at"]) == (0, None)
        assert _meta(data / "c.db") == ({"price_tiers_loaded": "0", "price_tiers_parts": "0"}, [])
        assert "price_tiers.tsv.gz not loaded" in capsys.readouterr().out

    @pytest.mark.parametrize("header,utc", [("2026-11-17T17:00:00-05:00", "2026-11-17T22:00:00+00:00"),
                                            ("2026-11-17T22:00:00", "2026-11-17T22:00:00+00:00")],
                             ids=["offset", "naive"])
    def test_scrape_time_stored_in_utc(self, tmp_path, header, utc):
        data = _data_dir(tmp_path, tiers_text=f"#scraped_at\t{header}\nC25531\t1\t0.5\n")
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.execute("CREATE TABLE components (lcsc TEXT)")
            conn.execute("INSERT INTO components VALUES ('C25531')")
            now = datetime(2026, 11, 18, tzinfo=timezone.utc)
            assert load_price_tiers(conn, data / "catalog", now=now) == (1, utc, None)
            assert load_price_tiers_ahead(conn, data / "catalog", header) == (0, None)

    def test_any_error_reading_the_file_loads_nothing(self, tmp_path, monkeypatch):
        """JSON nested past Python's limit raises RecursionError (not ValueError), which failed the image build."""
        import build_database as build

        def too_deep(path):
            yield "C2", [(1, 0.5)]
            raise RecursionError("maximum recursion depth exceeded while decoding a JSON array")

        monkeypatch.setattr(build, "read_price_tiers", too_deep)
        data = _data_dir(tmp_path)
        stats = build_database(data, data / "c.db", verbose=False)
        assert stats["total_parts"] == 3 and stats["price_tier_parts"] == 0
        assert _meta(data / "c.db") == ({"price_tiers_loaded": "0", "price_tiers_parts": "0"}, [])

    def test_server_opens_a_database_with_an_unusable_time(self, tmp_path):
        data = _data_dir(tmp_path)
        build_database(data, data / "c.db", verbose=False)
        with closing(sqlite3.connect(data / "c.db")) as conn:  # as a build before this check could write it
            conn.execute("UPDATE metadata SET value = '0001-01-01T00:00:00+14:00' WHERE key = 'price_tiers_scraped_at'")
            conn.commit()
        db = ComponentDatabase(db_path=data / "c.db", data_dir=data)
        try:
            assert db.price_tiers_as_of() is None and db.price_tiers_parts() == 0  # no breaks, no crash
            assert db.scraped_at() == "2026-11-18T22:00:00Z"
        finally:
            db.close()  # before the temporary directory goes (Windows)


def load_price_tiers_ahead(conn, catalog_dir, header):
    """load_price_tiers four days before the header's time: refused as ahead of the build's clock."""
    moment = datetime.fromisoformat(header)
    moment = moment.replace(tzinfo=timezone.utc) if moment.tzinfo is None else moment
    conn.execute("DROP TABLE price_tiers")
    loaded, scraped_at, why = load_price_tiers(conn, catalog_dir, now=moment - timedelta(days=4))
    assert "more than 2 days ahead" in why
    return loaded, scraped_at


@pytest.fixture(scope="module")
def databases(tmp_path_factory):
    dbs = {}
    for name, tiers in (("tiers", TIERS), ("plain", None)):
        data = _data_dir(tmp_path_factory.mktemp(name), tiers=tiers)
        build_database(data, data / "c.db", verbose=False)
        dbs[name] = ComponentDatabase(db_path=data / "c.db", data_dir=data)
    yield dbs
    for db in dbs.values():
        db.close()  # before the temporary directories go (Windows)


@pytest.fixture
async def use_db(databases, monkeypatch):
    def use(name):
        monkeypatch.setattr(server, "get_db", lambda: databases[name])
        return databases[name]
    with offline():
        yield use


LADDER = [{"qty": "1+", "price": 0.027}, {"qty": "1000+", "price": 0.021}, {"qty": "3000+", "price": 0.018},
          {"qty": "10000+", "price": 0.016}, {"qty": "50000+", "price": 0.014}]


class TestReplies:
    async def test_get_parts_lists_every_break(self, use_db):
        db = use_db("tiers")
        reply = await server.jlc_get_parts(["C25531", "C2", "C3"])
        assert list(reply)[:4] == ["data_as_of", "prices_as_of", "price_tiers_as_of", "total"]
        assert (reply["data_as_of"], reply["prices_as_of"], reply["price_tiers_as_of"]) == (
            "2026-11-18T22:00:00Z", "2026-11-12T20:00:00Z", "2026-11-17T22:00:00Z")
        tiered, untiered, unpriced = reply["results"]
        assert tiered["price"] == 0.0271  # the weekly 1-piece price keeps its meaning (prices_as_of)
        assert tiered["prices"] == LADDER  # 50200+ only repeated 50000+'s price
        assert list(tiered)[6:8] == ["price", "prices"]
        assert untiered["prices"] == [{"qty": "1+", "price": 0.002}]  # no breaks in that scrape
        assert unpriced["price"] is None and "prices" not in unpriced
        assert db.price_tiers_as_of() == "2026-11-17T22:00:00Z"

    async def test_mpn_rows_and_one_read(self, use_db):
        db = use_db("tiers")
        queries = []
        db._ensure_db()
        db.set_trace_callback(queries.append)
        try:
            reply = await server.jlc_get_parts([{"mpn": "0402WGF1001TCE"}, "C2"])
        finally:
            db.set_trace_callback(None)
        assert reply["results"][0]["results"][0]["prices"] == LADDER
        assert sum("lcsc IN" in query for query in queries) == 1  # rows and their breaks in one read

    async def test_get_part_by_mpn(self, use_db):
        use_db("tiers")
        reply = await server.jlc_get_part(mpn="0402WGF1001TCE")
        assert reply["price_tiers_as_of"] == "2026-11-17T22:00:00Z" and reply["prices_as_of"] == "2026-11-12T20:00:00Z"
        part = reply["results"][0]
        assert part["prices"] == LADDER and part["price"] == 0.0271
        assert list(part)[5:7] == ["price", "prices"] and part["data_source"]["kind"] == "snapshot"
        several = await server.jlc_get_part(mpn="RC0402")
        assert [p.get("prices") for p in several["results"]] == [[{"qty": "1+", "price": 0.002}], None]

    async def test_without_breaks_as_before(self, use_db):
        db = use_db("plain")
        reply = await server.jlc_get_parts(["C25531"])
        assert reply["price_tiers_as_of"] is None and db.price_tiers_as_of() is None
        assert reply["results"][0]["prices"] == [{"qty": "1+", "price": 0.0271}]
        mpn = await server.jlc_get_part(mpn="0402WGF1001TCE")
        assert mpn["price_tiers_as_of"] is None and mpn["results"][0]["prices"] == [{"qty": "1+", "price": 0.0271}]

    async def test_search_unchanged(self, use_db):
        use_db("tiers")
        reply = await server.jlc_search(query="C25531")
        assert reply["results"] and all("prices" not in part for part in reply["results"])
        assert "price_tiers_as_of" not in reply


@pytest.mark.parametrize("price,tiers,expected", [
    (0.5, None, [{"qty": "1+", "price": 0.5}]),
    (None, None, None),
    (0.5, "1:0.5,10:0.5", [{"qty": "1+", "price": 0.5}]),
    (0.5, "1:0.5,10:0.5,100:0.4", [{"qty": "1+", "price": 0.5}, {"qty": "10+", "price": 0.5}, {"qty": "100+", "price": 0.4}]),
    (None, "5:0.3", [{"qty": "5+", "price": 0.3}]),
], ids=["one", "none", "repeat", "middle", "from5"])
def test_snapshot_prices(price, tiers, expected):
    assert snapshot_prices(price, tiers) == expected


class TestHandOver:
    """The file reaches the image build only through the price-tiers artifact, never git."""

    def test_git_ignores_it(self):
        git = shutil.which("git")
        if git is None or not (ROOT / ".git").exists():
            pytest.skip("needs a git checkout")
        result = subprocess.run([git, "check-ignore", "--no-index", f"data/catalog/{PRICE_TIERS_FILE}"],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 0, result.stderr

    def test_docker_build_context_keeps_it(self):
        lines = [line.strip() for line in (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()]
        patterns = [line for line in lines if line and not line.startswith("#")]
        assert patterns[-1] == f"!data/catalog/{PRICE_TIERS_FILE}"  # the last match wins

    def test_scrape_uploads_it_after_the_push_and_before_the_deploy(self):
        """After the push, so a stalled upload never costs the day's commit (the push uses
        GITHUB_TOKEN and starts no build); before "Trigger deploy", whose build downloads it."""
        steps = yaml.safe_load((ROOT / ".github/workflows/scrape-components.yml").read_text(encoding="utf-8"))["jobs"]["scrape"]["steps"]
        names = [step.get("name") for step in steps]
        upload = steps[names.index("Upload price tiers")]
        assert (names.index("Check part count") < names.index("Commit and push data files")
                < names.index("Upload price tiers") < names.index("Trigger deploy"))
        assert "if" not in upload  # uploaded with or without a data change, once the commit step succeeded
        assert upload["uses"].startswith("actions/upload-artifact@v") and upload["continue-on-error"] is True
        assert 1 <= upload["timeout-minutes"] <= 10
        assert upload["with"] == {"name": "price-tiers", "path": f"data/catalog/{PRICE_TIERS_FILE}", "retention-days": 7,
                                  "if-no-files-found": "warn", "compression-level": 0, "overwrite": True}
        assert "sleep 120" in steps[names.index("Trigger deploy")]["run"]

    def test_build_downloads_it_without_failing(self):
        job = yaml.safe_load((ROOT / ".github/workflows/docker-build.yml").read_text(encoding="utf-8"))["jobs"]["build-and-push"]
        assert job["permissions"]["actions"] == "read"
        names = [step.get("name") for step in job["steps"]]
        download = job["steps"][names.index("Download price tiers")]
        assert names.index("Checkout repository") < names.index("Download price tiers") < names.index("Build and push Docker image")
        assert download["continue-on-error"] is True and 1 <= download["timeout-minutes"] <= 10
        script = download["run"]
        # The scrape workflow's own runs on main (a fork's pull request can upload an artifact with the
        # same name, and over 100 newer ones pushed main's off an unpaginated artifact list), any status
        assert "actions/workflows/scrape-components.yml/runs?branch=main" in script and "status=" not in script
        assert "actions/runs/$run/artifacts?name=price-tiers" in script and "repos/$REPO/actions/artifacts?" not in script
        assert script.count("gh api") == script.count("timeout 120 gh api") == 3  # no request can hang the step
        assert f"data/catalog/{PRICE_TIERS_FILE}" in script and "GITHUB_STEP_SUMMARY" in script
        # every failure warns and ends the step successfully
        assert script.count('warn "') == script.count("exit 0") == 6 and "exit 1" not in script
