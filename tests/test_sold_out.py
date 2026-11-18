"""0.10.0: parts that drop out of the daily catalog (stock under 10, or no longer listed) are kept, with
gone_since and their stock unknown, until a scrape lists them again, so their BOM lines answer from the
database instead of a live jlc_stock_check.
The scrape's output step writes them to committed files (data/catalog/sold_out/, no new requests);
the database build loads them into a table apart from components, so search never sees them.
No network: fixture catalogs, a stubbed scrape and small built databases."""

import gzip
import json
import shutil
import sqlite3
import subprocess
import sys
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from conftest import write_catalog_category

import pcbparts_mcp.server as server
from pcbparts_mcp.catalog_files import (
    PRICE_TIERS_FILE, SOLD_OUT_DIR, SOLD_OUT_KEYS, read_catalog, read_sold_out, sold_out_row, write_price_tiers,
    write_sold_out,
)
from pcbparts_mcp.db import ComponentDatabase
from pcbparts_mcp.history_db import StockHistoryDatabase
from pcbparts_mcp.mounting import english_package

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import scrape_components as scrape  # noqa: E402
from build_database import build_database  # noqa: E402
from build_history_db import build_history_db  # noqa: E402
from search_baseline import offline  # noqa: E402

ROOT = Path(__file__).parent.parent


def sold(code, gone, mpn="M1", maker="Maker", package="0402", stock=50, price=0.1, library="e", sub=2,
         description="d"):
    return {"l": code, "g": gone, "s": stock, "$": price, "t": library, "c": sub, "m": mpn, "f": maker,
            "p": package, "d": description}


class TestFiles:
    def test_round_trip_by_month_sorted_and_same_bytes(self, tmp_path):
        rows = {code: sold(code, gone) for code, gone in
                (("C100", "2026-11-16"), ("C9", "2026-11-13"), ("C5", "2026-10-30"), ("C10", "2026-11-14"))}
        rows["C9"]["d"] = "1µF ±10%\ttab"  # any text survives
        assert write_sold_out(tmp_path, rows) == {"2026-10.jsonl": 1, "2026-11.jsonl": 3}
        first = {p.name: p.read_bytes() for p in (tmp_path / SOLD_OUT_DIR).iterdir()}
        write_sold_out(tmp_path, dict(reversed(rows.items())))
        assert {p.name: p.read_bytes() for p in (tmp_path / SOLD_OUT_DIR).iterdir()} == first
        lines = (tmp_path / SOLD_OUT_DIR / "2026-11.jsonl").read_text(encoding="utf-8").splitlines()
        assert [json.loads(line)[0] for line in lines] == ["C9", "C10", "C100"]  # by code number
        assert lines[1] == '["C10","2026-11-14",50,0.1,"e",2,"M1","Maker","0402","d"]'
        assert [row["l"] for row in read_sold_out(tmp_path)] == ["C5", "C9", "C10", "C100"]
        assert {row["l"]: row for row in read_sold_out(tmp_path)} == rows

    def test_no_rows_no_files(self, tmp_path):
        write_sold_out(tmp_path, {"C1": sold("C1", "2026-10-01")})
        assert write_sold_out(tmp_path, {}) == {}
        assert not (tmp_path / SOLD_OUT_DIR).exists() and list(read_sold_out(tmp_path)) == []

    def test_row_from_a_catalog_part(self):
        part = {"l": "C1", "m": "M", "f": "F", "p": "0603", "s": 25, "t": "b", "c": 7, "$": 0.5, "d": "x",
                "a": [["Resistance", "1k"]], "x": 0, "n": 1}
        assert sold_out_row(part, "2026-11-18") == {"l": "C1", "g": "2026-11-18", "s": 25, "$": 0.5, "t": "b",
                                                     "c": 7, "m": "M", "f": "F", "p": "0603", "d": "x"}
        assert list(sold_out_row(part, "2026-11-18")) == list(SOLD_OUT_KEYS)

    def test_a_catalog_part_the_row_cant_hold_as_is(self, tmp_path, caplog):
        """write_catalog takes any model or maker type, a sold-out row only text: such a part made
        every scrape fail (write_sold_out raised) until a scrape listed it again."""
        part = {"l": "C1", "m": 2222, "f": None, "p": ["SOT-23"], "s": 25, "t": "x", "c": 7, "$": 0.5, "d": 1.5}
        row = sold_out_row(part, "2026-11-18")
        assert {key: row[key] for key in ("m", "f", "p", "d", "t")} == {"m": "2222", "f": None, "p": '["SOT-23"]',
                                                                         "d": "1.5", "t": "e"}
        assert write_sold_out(tmp_path, {"C1": row}) == {"2026-11.jsonl": 1}
        assert next(read_sold_out(tmp_path))["m"] == "2222"
        assert "Sold-out part C1" in caplog.text

    @pytest.mark.parametrize("change", [{"g": "2026-11-31"}, {"g": "18/11/2026"}, {"s": "5"}, {"$": float("inf")},
                                        {"t": "x"}, {"c": -1}, {"m": 5}, {"l": "C 1"}],
                             ids=["day", "form", "stock", "price", "type", "sub", "mpn", "code"])
    def test_writer_rejects_bad_rows(self, tmp_path, change):
        row = {**sold("C1", "2026-11-18"), **change}
        with pytest.raises(ValueError):
            write_sold_out(tmp_path, {row["l"]: row})

    @pytest.mark.parametrize("name,text", [
        ("2026-11.jsonl", '["C1","2026-10-31",5,0.1,"e",2,"M","F","P","D"]\n'),  # another month's row
        ("2026-11.jsonl", '["C2","2026-11-01",5,0.1,"e",2,"M","F","P","D"]\n'
                          '["C1","2026-11-01",5,0.1,"e",2,"M","F","P","D"]\n'),  # LCSC order
        ("2026-11.jsonl", '["C1","2026-11-01",5,0.1,"e",2,"M","F","P"]\n'),  # a field short
        ("2026-11.jsonl", '{"l":"C1"}\n'),
        ("2026-11.jsonl", "not json\n"),
        ("november.jsonl", '["C1","2026-11-01",5,0.1,"e",2,"M","F","P","D"]\n'),
    ], ids=["month", "order", "short", "object", "text", "name"])
    def test_reader_rejects_malformed_files(self, tmp_path, name, text):
        (tmp_path / SOLD_OUT_DIR).mkdir()
        (tmp_path / SOLD_OUT_DIR / name).write_text(text, encoding="utf-8")
        with pytest.raises(ValueError):
            list(read_sold_out(tmp_path))

    def test_reader_rejects_a_part_in_two_months(self, tmp_path):
        (tmp_path / SOLD_OUT_DIR).mkdir()
        for month in ("2026-10", "2026-11"):
            (tmp_path / SOLD_OUT_DIR / f"{month}.jsonl").write_text(
                json.dumps(["C1", f"{month}-01", 5, 0.1, "e", 2, "M", "F", "P", "D"]) + "\n", encoding="utf-8")
        with pytest.raises(ValueError, match="duplicate LCSC C1"):
            list(read_sold_out(tmp_path))

    def test_committed_and_in_the_image_build(self):
        """git add skips ignored files without a word: the sold-out files must not be ignored, and
        the image build mounts data/catalog (all of it) for the database build."""
        git = shutil.which("git")
        if git is None or not (ROOT / ".git").exists():
            pytest.skip("needs a git checkout")
        result = subprocess.run([git, "check-ignore", "--no-index", f"data/catalog/{SOLD_OUT_DIR}/2026-11.jsonl"],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 1 and result.stdout == "", result.stdout
        patterns = [line.strip() for line in (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.strip().startswith(("#", "!"))]
        assert not [p for p in patterns if p.rstrip("/") in ("data", "data/catalog") or p.startswith("data/catalog/")]
        assert "source=data/catalog,target=/app/data/catalog" in (ROOT / "Dockerfile").read_text(encoding="utf-8")


class TestUpdate:
    PREVIOUS = [("resistors", {"l": f"C{n}", "m": f"M{n}", "f": "F", "p": "0402", "s": 100 + n, "t": "b", "c": 2,
                               "$": 0.01, "d": "", "a": [], "x": 0}) for n in range(1, 5)]

    def test_entering_staying_and_leaving(self):
        kept = [sold("C8", "2026-11-10"), sold("C9", "2026-11-12")]
        rows, changes = scrape.update_sold_out(self.PREVIOUS, {"C1", "C2", "C9"}, kept, "2026-11-18")
        assert sorted(rows) == ["C3", "C4", "C8"]
        assert rows["C3"] == {"l": "C3", "g": "2026-11-18", "s": 103, "$": 0.01, "t": "b", "c": 2, "m": "M3",
                              "f": "F", "p": "0402", "d": ""}
        assert rows["C8"]["g"] == "2026-11-10"  # gone_since stays while it stays sold out
        assert changes == {"new": 2, "back": 1, "kept": 3}  # C9 is in the catalog again

    def test_no_previous_catalog(self):
        rows, changes = scrape.update_sold_out((), {"C9"}, [sold("C8", "2026-11-10"), sold("C9", "2026-11-12")],
                                               "2026-11-18")
        assert list(rows) == ["C8"] and changes == {"new": 0, "back": 1, "kept": 1}


CATEGORIES = [{"id": 1, "name": "Resistors"}]


def _part(code, sub=2, stock=50, price=0.1):
    return {"l": code, "m": f"M{code}", "f": "Maker", "p": "0402", "c": sub, "s": stock, "$": price, "t": "b",
            "d": "10kΩ", "a": [], "x": 0}


def _day(day):
    return datetime(2026, 11, day, 22, 0, tzinfo=timezone.utc)


def _sold_out(output):
    return {row["l"]: row for row in read_sold_out(output / "catalog")}


class TestScrapeOutputs:
    def test_kept_until_listed_again(self, tmp_path):
        write = scrape.write_scrape_outputs
        manifest = write(tmp_path, CATEGORIES, {"resistors": [_part("C1"), _part("C2"), _part("C3", stock=11)]},
                         scrape.ScrapeProgress(), now=_day(16))
        assert manifest["sold_out_parts"] == 0 and _sold_out(tmp_path) == {}
        manifest = write(tmp_path, CATEGORIES, {"resistors": [_part("C1")]}, scrape.ScrapeProgress(), now=_day(17))
        assert manifest["sold_out_parts"] == 2 and manifest["total_parts"] == 1
        assert _sold_out(tmp_path)["C3"] == {"l": "C3", "g": "2026-11-17", "s": 11, "$": 0.1, "t": "b", "c": 2,
                                             "m": "MC3", "f": "Maker", "p": "0402", "d": "10kΩ"}
        write(tmp_path, CATEGORIES, {"resistors": [_part("C1"), _part("C2", stock=900)]}, scrape.ScrapeProgress(),
              now=_day(18))
        assert list(_sold_out(tmp_path)) == ["C3"] and _sold_out(tmp_path)["C3"]["g"] == "2026-11-17"
        assert [p["l"] for _, p in read_catalog(tmp_path / "catalog")] == ["C1", "C2"]  # never both
        # The same parts as the history's gone events, on the same day
        with gzip.open(tmp_path / "history" / "2026-11" / "2026-11-17.jsonl.gz", "rt", encoding="utf-8") as stream:
            gone = sorted(e["l"] for e in map(json.loads, stream) if e.get("e") == "gone")
        assert gone == ["C2", "C3"]

    def test_gap_parts_only_once_the_gap_is_given_up(self, tmp_path):
        sizes = [300, 300, 300, 50]
        full = {"resistors": [_part(f"C{sub}{i:04d}", sub=sub) for sub in range(1, 5) for i in range(sizes[sub - 1])]}
        short = {"resistors": [p for p in full["resistors"] if p["c"] == 4]}  # three subcategories gone at once
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, full, scrape.ScrapeProgress(), now=_day(16))
        for day in (17, 18):  # carried over the gap for GAP_MAX_DAYS
            manifest = scrape.write_scrape_outputs(tmp_path, CATEGORIES, short, scrape.ScrapeProgress(), now=_day(day))
            assert set(manifest["carried_forward"]) == {"1", "2", "3"} and manifest["sold_out_parts"] == 0
        manifest = scrape.write_scrape_outputs(tmp_path, CATEGORIES, short, scrape.ScrapeProgress(), now=_day(19))
        assert "carried_forward" not in manifest and manifest["sold_out_parts"] == 900
        assert {row["g"] for row in _sold_out(tmp_path).values()} == {"2026-11-19"}

    def test_no_results_leave_the_files_alone(self, tmp_path):
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": [_part("C1"), _part("C2")]},
                                    scrape.ScrapeProgress(), now=_day(16))
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": [_part("C1")]}, scrape.ScrapeProgress(),
                                    now=_day(17))
        manifest = scrape.write_scrape_outputs(tmp_path, CATEGORIES, {}, scrape.ScrapeProgress(), now=_day(18))
        assert "sold_out_parts" not in manifest and list(_sold_out(tmp_path)) == ["C2"]

    def test_a_malformed_file_stops_the_scrape(self, tmp_path):
        scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": [_part("C1")]}, scrape.ScrapeProgress(),
                                    now=_day(16))
        (tmp_path / "catalog" / SOLD_OUT_DIR).mkdir()
        (tmp_path / "catalog" / SOLD_OUT_DIR / "2026-11.jsonl").write_text("[1]\n", encoding="utf-8")
        with pytest.raises(RuntimeError, match="Sold-out parts update failed"):
            scrape.write_scrape_outputs(tmp_path, CATEGORIES, {"resistors": [_part("C1")]}, scrape.ScrapeProgress(),
                                        now=_day(17))

    async def test_published_with_the_catalog(self, tmp_path, monkeypatch):
        """The whole run, as the workflow does it (stubbed requests): published with the catalog, and
        a month whose parts all came back loses its file."""
        listed = {"value": ["C1", "C2"]}

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        async def categories(session):
            return [{"id": 1, "name": "Resistors", "subcategories": [{"id": 2, "name": "Chip Resistor", "count": 2}]}]

        async def scraped(subcategory, session):
            parts = [_part(code) for code in listed["value"]]
            return parts, len(parts)

        monkeypatch.setattr(scrape, "create_scraper_session", Session)
        monkeypatch.setattr(scrape, "fetch_categories", categories)
        monkeypatch.setattr(scrape, "scrape_subcategory", scraped)
        monkeypatch.setattr(scrape, "WORKER_STAGGER", 0)
        monkeypatch.setenv("ALLOW_PART_DROP", "true")  # half the catalog goes below
        await scrape.run_scraper(tmp_path, num_workers=1)
        listed["value"] = ["C1"]
        await scrape.run_scraper(tmp_path, num_workers=1)
        manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        assert list(_sold_out(tmp_path)) == ["C2"] and manifest["sold_out_parts"] == 1
        assert _sold_out(tmp_path)["C2"]["g"] == manifest["scraped_at"][:10]
        listed["value"] = ["C1", "C2"]
        await scrape.run_scraper(tmp_path, num_workers=1)
        assert not [p for p in (tmp_path / "catalog" / SOLD_OUT_DIR).rglob("*") if p.is_file()]
        assert not (tmp_path / ".scrape-staging").exists()


SUBCATEGORIES = {
    "11": {"name": "Operational Amplifier", "category_id": 3, "category_name": "Amplifiers/Comparators"},
    "12": {"name": "MOSFETs", "category_id": 1, "category_name": "Transistors/Thyristors"},
    "13": {"name": "Multilayer Ceramic Capacitors MLCC - SMD/SMT", "category_id": 2, "category_name": "Capacitors"},
}


def catalog_part(lcsc, mpn, maker, package, stock, library="e", sub=11, price=0.01, description=""):
    return {"l": lcsc, "m": mpn, "f": maker, "p": package, "s": stock, "t": library, "c": sub, "$": price,
            "d": description, "a": [], "x": 0}


CATALOG = [
    catalog_part("C7950", "LM358DR2G", "onsemi", "SOIC-8", 495224, "b", price=0.054, description="op amp"),
    catalog_part("C5252902", "LM358", "MSKSEMI", "SOP-8", 338940, price=0.039, description="op amp"),
    catalog_part("C1525", "CL05B104KO5NNNC", "Samsung Electro-Mechanics", "0402", 37_286_642, "b", sub=13,
                 price=0.0029, description="100nF 16V X7R 0402"),
    # Another maker's copy, numbered after Infineon's IRFB4710PBF (gone below): full-text "related" only
    catalog_part("C55112117", "IRFB4710PBF-JSM", "JSMSEMI", "TO-220-3", 92, sub=12, price=0.9651),
]
SOLD_OUT = {
    "C2040": sold("C2040", "2026-11-16", "RP2040", "Raspberry Pi", "LQFN-56(7x7)", 15, 0.7, sub=11,
                  description="Dual-core RP2040 microcontroller"),
    "C9001": sold("C9001", "2026-11-14", "LM358", "Texas Instruments", "SOIC-8", 40, 0.12, "b", sub=11,
                  description="Dual op amp"),
    "C9002": sold("C9002", "2026-10-30", "TPS7A0233PDBVR", "Texas Instruments", "SOT-23-5", 12, 0.3, sub=11),
    "C9003": sold("C9003", "2026-11-15", "HDR-2X5", "Maker", "插件,P=2.54mm", 30, None, sub=11),
    "C1525": sold("C1525", "2026-11-01", "CL05B104KO5NNNC", "Samsung Electro-Mechanics", "0402", 10, 0.003, sub=13),
    "C2660": sold("C2660", "2026-11-13", "IRFB4710PBF", "Infineon Technologies", "TO-220AB", 941, 2.8428, sub=12),
}


def _data_dir(root, sold_out=SOLD_OUT):
    write_catalog_category(root, "amplifiers", CATALOG[:2])
    write_catalog_category(root, "capacitors", CATALOG[2:3])
    write_catalog_category(root, "transistors", CATALOG[3:])
    (root / "subcategories.json").write_text(json.dumps(SUBCATEGORIES), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps(
        {"scraped_at": "2026-11-17T22:00:00+00:00", "prices_updated_at": "2026-11-12T20:00:00+00:00",
         "categories": {}}), encoding="utf-8")
    if sold_out:
        write_sold_out(root / "catalog", sold_out)
    return root


class TestDatabaseBuild:
    def test_loaded_apart_from_the_catalog(self, tmp_path):
        data = _data_dir(tmp_path)
        stats = build_database(data, data / "c.db", verbose=False)
        assert (stats["total_parts"], stats["sold_out_parts"]) == (4, 5)  # C1525 is in the catalog: not gone
        with closing(sqlite3.connect(data / "c.db")) as conn:
            rows = {row[0]: row for row in conn.execute("SELECT * FROM sold_out")}
            assert rows["C2040"] == ("C2040", "RP2040", "Raspberry Pi", "LQFN-56(7x7)", "e", 11, 0.7,
                                     "Dual-core RP2040 microcontroller", 15, "2026-11-16")
            assert rows["C9003"][3] == english_package("插件,P=2.54mm") == "Plugin,P=2.54mm"
            assert conn.execute("SELECT COUNT(*) FROM components").fetchone()[0] == 4
            assert conn.execute("SELECT COUNT(*) FROM components_fts WHERE components_fts MATCH 'RP2040'").fetchone()[0] == 0
            assert conn.execute("SELECT value FROM metadata WHERE key = 'sold_out_parts'").fetchone() == ("5",)

    def test_without_the_files(self, tmp_path):
        data = _data_dir(tmp_path, sold_out=None)
        assert build_database(data, data / "c.db", verbose=False)["sold_out_parts"] == 0
        with closing(sqlite3.connect(data / "c.db")) as conn:
            assert conn.execute("SELECT COUNT(*) FROM sold_out").fetchone()[0] == 0

    def test_a_malformed_file_fails_the_build(self, tmp_path):
        data = _data_dir(tmp_path)
        path = data / "catalog" / SOLD_OUT_DIR / "2026-11.jsonl"
        path.write_text(path.read_text(encoding="utf-8") + "[]\n", encoding="utf-8")
        with pytest.raises(ValueError, match="malformed sold-out row"):
            build_database(data, data / "c.db", verbose=False)
        assert not (data / "c.db").exists()


@pytest.fixture(scope="module")
def databases(tmp_path_factory):
    dbs = {}
    for name, rows in (("kept", SOLD_OUT), ("none", None)):
        data = _data_dir(tmp_path_factory.mktemp(name), sold_out=rows)
        build_database(data, data / "c.db", verbose=False)
        dbs[name] = ComponentDatabase(db_path=data / "c.db", data_dir=data)
    old = tmp_path_factory.mktemp("old")  # a database built before 0.10.0 has no sold_out table
    shutil.copy(next(iter(dbs.values())).db_path, old / "c.db")
    with closing(sqlite3.connect(old / "c.db")) as conn:
        conn.execute("DROP TABLE sold_out")
        conn.commit()
    dbs["old"] = ComponentDatabase(db_path=old / "c.db", data_dir=old)
    yield dbs
    for db in dbs.values():
        db.close()  # before the temporary directories go (Windows)


@pytest.fixture
async def use_db(databases, monkeypatch):
    # Async so the event loop exists before sockets are blocked (Windows builds it with connect())
    def use(name):
        monkeypatch.setattr(server, "get_db", lambda: databases[name])
        return databases[name]
    with offline():
        yield use


def outcome(reply):
    return server._call_outcome(SimpleNamespace(structured_content=reply))


SOLD_ROW = {"lcsc": "C2040", "model": "RP2040", "manufacturer": "Raspberry Pi", "package": "LQFN-56(7x7)",
            "stock": None, "price": 0.7, "prices": [{"qty": "1+", "price": 0.7}], "library_type": "extended",
            "preferred": False, "category": "Amplifiers/Comparators", "subcategory": "Operational Amplifier",
            "description": "Dual-core RP2040 microcontroller", "gone": True, "gone_since": "2026-11-16",
            "last_stock": 15}


class TestGetParts:
    async def test_code_rows(self, use_db):
        use_db("kept")
        reply = await server.jlc_get_parts(["c2040", "C7950", "C99999999", "C9003"])
        gone_row, listed, missing, unpriced = reply["results"]
        assert gone_row == {"input": "c2040", **SOLD_ROW}  # stock null: under 10, or no longer listed
        assert "gone" not in listed and listed["stock"] == 495224
        assert missing == {"input": "C99999999", "lcsc": "C99999999", "not_found": True}
        assert unpriced["price"] is None and "prices" not in unpriced and unpriced["package"] == "Plugin,P=2.54mm"
        assert reply["counts"] == {"found": 1, "gone": 2, "not_found": 1, "error": 0}
        assert sum(reply["counts"].values()) == reply["total"] == 4
        assert reply["hint"].startswith("gone parts left the daily snapshot") and "not_found" in reply["hint"]
        assert reply["hint"].count("gone parts") == 1 and "jlc_get_part(lcsc=...)" in reply["hint"]  # once a reply
        assert outcome(reply) == "ok"
        only_gone = await server.jlc_get_parts(["C2040"])
        assert outcome(only_gone) == "ok" and "not_found parts" not in only_gone["hint"]

    async def test_mpn_rows(self, use_db):
        use_db("kept")
        in_stock, ti, spelled, nothing = (await server.jlc_get_parts([
            "LM358", {"mpn": "LM358", "manufacturer": "Texas Instruments"}, "TPS7A02-33PDBVR", "ZZQ9981XK"]))["results"]
        # Parts in stock: today's row, plus how many numbered so are gone
        assert [p["lcsc"] for p in in_stock["results"]] == ["C5252902"] and in_stock["gone_matches"] == 1
        # An MPN row's matches have the short field list (an LCSC code's row has them all)
        assert ti == {"input": {"mpn": "LM358", "manufacturer": "Texas Instruments"}, "mpn": "LM358", "total": 1,
                      "exact": True, "ambiguous": False,
                      "results": [{"lcsc": "C9001", "model": "LM358", "manufacturer": "Texas Instruments",
                                   "package": "SOIC-8", "stock": None, "price": 0.12,
                                   "prices": [{"qty": "1+", "price": 0.12}], "library_type": "basic",
                                   "preferred": False, "gone": True, "gone_since": "2026-11-14", "last_stock": 40}],
                      "other_manufacturers": ["MSKSEMI"]}
        assert (spelled["match"], spelled["matched_mpn"], spelled["exact"]) == ("separators", "TPS7A0233PDBVR", False)
        assert spelled["results"][0]["gone_since"] == "2026-10-30"
        assert nothing["not_found"] is True

    async def test_one_read_for_codes_the_snapshot_lists(self, use_db):
        db = use_db("kept")
        queries = []
        db._ensure_db()
        db._conn.set_trace_callback(queries.append)
        try:
            await server.jlc_get_parts(["C7950", "C1525", "LM358DR2G"])
        finally:
            db._conn.set_trace_callback(None)
        assert sum("WHERE lcsc IN" in query for query in queries) == 1  # no gone read when all are listed


class TestGetPartByMpn:
    async def test_every_match_gone(self, use_db):
        use_db("kept")
        reply = await server.jlc_get_part(mpn="RP2040")
        assert "error" not in reply and outcome(reply) == "ok"
        assert list(reply) == ["mpn", "data_as_of", "prices_as_of", "price_tiers_as_of", "total", "exact",
                               "ambiguous", "results", "hint", "next_call"]
        part = reply["results"][0]
        assert {k: part[k] for k in SOLD_ROW if k != "prices"} == {k: v for k, v in SOLD_ROW.items() if k != "prices"}
        assert part["prices"] == [{"qty": "1+", "price": 0.7}] and part["mounting_type"] == "smd"
        assert part["data_source"] == {"kind": "snapshot", "provider": "JLCPCB", "observed_at": "2026-11-17T22:00:00Z"}
        assert reply["next_call"] == {"tool": "jlc_stock_check", "arguments": {"query": "RP2040", "min_stock": 0,
                                                                              "limit": 10}}
        assert "under 10" in reply["hint"] and "jlc_get_part(lcsc=...)" in reply["hint"]

    async def test_in_stock_reply_only_adds_a_count(self, use_db):
        use_db("none")
        before = await server.jlc_get_part(mpn="LM358")
        use_db("kept")
        after = await server.jlc_get_part(mpn="LM358")
        assert after.pop("gone_matches") == 1 and after == before

    async def test_misses_unchanged(self, use_db):
        replies = []
        for name in ("none", "kept", "old"):
            use_db(name)
            replies.append(await server.jlc_get_part(mpn="ZZQ9981XK"))
        assert replies[0] == replies[1] == replies[2]
        assert replies[0]["error"] == "No part found in the local snapshot for MPN 'ZZQ9981XK'"
        use_db("none")  # without the files a gone number is a miss, as before
        assert (await server.jlc_get_part(mpn="RP2040"))["error"].startswith("No part found")

    async def test_backplane_reads_the_gone_row(self, use_db):
        """Backplane's pick(): the results[] entry whose model matches; stock not an integer reads as -1,
        their "unknown" (not "out", which their design review reports as an error); prices with qty and
        numeric price (research-backplane-code-review.md, "What they parse")."""
        use_db("kept")
        reply = await server.jlc_get_part(mpn="RP2040")
        match = next(r for r in reply["results"] if r["model"].casefold() == "rp2040")
        assert match["stock"] is None
        assert match["lcsc"] == "C2040" and match["manufacturer"] and match["library_type"] in ("basic", "preferred", "extended")
        assert all(int(tier["qty"].rstrip("+")) >= 1 and isinstance(tier["price"], float) for tier in match["prices"])


async def test_backplane_live_follow_up_needs_one_tier_and_the_code(tmp_path, monkeypatch):
    """Backplane's hub takes the jlc_get_part(mpn) result whose model matches and, when it has one
    price break or fewer, looks its lcsc up live and uses that stock (research-backplane-code-review.md).
    A gone row keeps that working: its lcsc, and its last 1-piece price as its one tier (none
    without a price), on a database with price breaks and even if breaks were kept for its code."""
    data = _data_dir(tmp_path)
    write_price_tiers(data / "catalog" / PRICE_TIERS_FILE, {"C5252902": "1:0.039,100:0.03,1000:0.025"},
                      "2026-11-17T22:00:00+00:00")
    build_database(data, data / "c.db", verbose=False)
    with closing(sqlite3.connect(data / "c.db")) as conn:  # breaks for gone codes, which the build drops
        conn.executemany("INSERT OR REPLACE INTO price_tiers VALUES (?, ?)",
                         [(code, "1:0.7,100:0.6,1000:0.5") for code in ("C2040", "C9001", "C9003")])
        conn.commit()
    db = ComponentDatabase(db_path=data / "c.db", data_dir=data)
    monkeypatch.setattr(server, "get_db", lambda: db)
    try:
        with offline():
            rp2040 = await server.jlc_get_part(mpn="RP2040")
            lm358 = await server.jlc_get_part(mpn="LM358")
            header = await server.jlc_get_part(mpn="HDR-2X5")
            rows = (await server.jlc_get_parts(["RP2040", "C2040"]))["results"]
    finally:
        db.close()  # before the temporary directory goes (Windows)
    assert rp2040["price_tiers_as_of"] and len(lm358["results"][0]["prices"]) == 3  # in-stock parts list breaks
    match = next(r for r in rp2040["results"] if r["model"].casefold() == "rp2040")
    assert (match["gone"], match["lcsc"], match["prices"]) == (True, "C2040", [{"qty": "1+", "price": 0.7}])
    priceless = header["results"][0]
    assert (priceless["gone"], priceless["lcsc"], priceless["price"], "prices" in priceless) == (True, "C9003", None, False)
    assert [r["prices"] for r in (rows[0]["results"][0], rows[1])] == [[{"qty": "1+", "price": 0.7}]] * 2


class TestGoneBeatsRelatedOnly:
    """IRFB4710PBF (Infineon, C2660) left the snapshot; in stock there is only JSMSEMI's
    IRFB4710PBF-JSM, a full-text "related" result. The part asked for answers first."""

    async def test_get_part(self, use_db):
        use_db("none")
        before = await server.jlc_get_part(mpn="IRFB4710PBF")
        assert before["match"] == "related" and [p["lcsc"] for p in before["results"]] == ["C55112117"]
        use_db("kept")
        reply = await server.jlc_get_part(mpn="IRFB4710PBF")
        assert [(p["lcsc"], p.get("gone")) for p in reply["results"]] == [("C2660", True), ("C55112117", None)]
        assert (reply["exact"], reply["ambiguous"], reply["total"]) == (True, False, 2) and "match" not in reply
        assert reply["note"].startswith("'IRFB4710PBF' itself left the snapshot (the gone parts, listed first)")
        assert "Part types: MOSFETs." in reply["note"]
        assert reply["results"][1] == before["results"][0]  # the related part as before
        assert reply["hint"].startswith("gone parts") and reply["next_call"]["tool"] == "jlc_stock_check"
        assert outcome(reply) == "ok"

    async def test_get_parts(self, use_db):
        """jlc_get_parts never lists full-text matches, so the gone part is the whole answer, and
        JSMSEMI's copy, which only its text relates, is no match for JSMSEMI either."""
        use_db("kept")
        reply = await server.jlc_get_parts(["IRFB4710PBF", {"mpn": "IRFB4710PBF", "manufacturer": "JSMSEMI"}])
        asked, copy = reply["results"]
        assert [(p["lcsc"], p["stock"]) for p in asked["results"]] == [("C2660", None)]
        assert (asked["exact"], asked["total"]) == (True, 1) and "note" not in asked
        assert "other_manufacturers" not in asked  # JSMSEMI's is a related part, not this number
        assert copy == {"input": {"mpn": "IRFB4710PBF", "manufacturer": "JSMSEMI"}, "mpn": "IRFB4710PBF",
                        "total": 0, "results": [], "not_found": True}
        assert reply["counts"] == {"found": 0, "gone": 1, "not_found": 1, "error": 0}

    async def test_an_exact_part_in_stock_still_answers(self, use_db):
        use_db("kept")
        reply = await server.jlc_get_part(mpn="LM358")  # MSKSEMI's in stock, Texas Instruments' gone
        assert [p["lcsc"] for p in reply["results"]] == ["C5252902"] and reply["gone_matches"] == 1


class TestLifecycleIdentities:
    async def test_gone_codes_resolve(self, use_db):
        use_db("kept")
        parts = server._catalog_identities(["C2040", "C7950", "C99999"])
        assert (parts["C2040"]["model"], parts["C2040"]["manufacturer"], parts["C2040"]["gone"]) == (
            "RP2040", "Raspberry Pi", True)
        assert parts["C7950"]["model"] == "LM358DR2G" and parts["C99999"] is None
        use_db("old")
        assert server._catalog_identities(["C2040"]) == {"C2040": None}


class TestOtherReadersUnchanged:
    def test_search_and_counts_never_see_them(self, databases):
        kept, none = databases["kept"], databases["none"]
        for query in ("RP2040", "C2040", "TPS7A0233PDBVR", "LM358"):
            assert [p["lcsc"] for p in kept.search(query=query)["results"]] == [
                p["lcsc"] for p in none.search(query=query)["results"]]
        assert kept.search(query="RP2040")["results"] == []
        assert kept.get_stats() == none.get_stats()
        assert kept.get_categories_for_client() == none.get_categories_for_client()
        assert kept.mpns_containing("2040") == [] and kept.subcategories_matching("RP2040") == {}
        assert kept.get_by_lcsc("C2040") is None and kept.get_by_lcsc_batch(["C2040"]) == {"C2040": None}
        assert kept.get_by_mpn("RP2040") == []

    def test_old_database(self, databases):
        old = databases["old"]
        assert old.get_sold_out_by_mpn("RP2040") == [] and old.get_sold_out_rows(["C2040"]) == {"C2040": None}


@pytest.fixture
def history(tmp_path, monkeypatch):
    events = [{"l": "C2040", "d": "2026-11-16", "s": 0, "e": "gone", "before": 15},
              {"l": "C7950", "d": "2026-11-16", "s": 900, "e": "change", "before": 1000}]
    (tmp_path / "history").mkdir()
    with gzip.open(tmp_path / "history/events.jsonl.gz", "wt", encoding="utf-8") as stream:
        for event in events:
            stream.write(json.dumps(event) + "\n")
    build_history_db(tmp_path, tmp_path / "history.db", verbose=False)
    reader = StockHistoryDatabase(tmp_path / "history.db")
    monkeypatch.setattr(server, "get_history_db", lambda: reader)
    yield reader
    reader.close()


class TestStockHistory:
    async def test_current_stock_of_a_gone_part(self, use_db, history):
        use_db("kept")
        one = await server.jlc_stock_history("C2040")
        assert (one["current_stock"], one["gone_since"]) == (None, "2026-11-16")  # null as before, plus when
        assert list(one)[-3:] == ["current_stock", "gone_since", "current_stock_as_of"]
        assert one["events"][0]["type"] == "gone"
        many = await server.jlc_stock_history(["C2040", "C7950", "C99999"])
        assert [(p["current_stock"], p.get("gone_since")) for p in many["parts"]] == [
            (None, "2026-11-16"), (495224, None), (None, None)]
        assert list(many["parts"][0])[:3] == ["lcsc", "current_stock", "gone_since"]

    async def test_listed_and_unknown_parts_unchanged(self, use_db, history):
        replies = {}
        for name in ("none", "kept"):
            use_db(name)
            replies[name] = [await server.jlc_stock_history("C7950"), await server.jlc_stock_history(["C7950", "C99999"])]
        assert replies["none"] == replies["kept"]


def test_backfill_replays_the_committed_catalogs(tmp_path):
    """scripts/backfill_sold_out.py seeds the files from the catalogs in git history, as the daily
    scrape would have written them."""
    git = shutil.which("git")
    if git is None:
        pytest.skip("needs git")
    from backfill_sold_out import backfill

    def commit(parts, day):
        write_catalog_category(tmp_path, "resistors", parts)
        (tmp_path / "data").mkdir(exist_ok=True)
        if (tmp_path / "data" / "catalog").exists():
            shutil.rmtree(tmp_path / "data" / "catalog")
        shutil.copytree(tmp_path / "catalog", tmp_path / "data" / "catalog")
        (tmp_path / "data" / "manifest.json").write_text(json.dumps({"scraped_at": f"{day}T22:00:00+00:00"}),
                                                         encoding="utf-8")
        subprocess.run([git, "add", "data"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run([git, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", day], cwd=tmp_path,
                       check=True, capture_output=True)

    subprocess.run([git, "init", "-q"], cwd=tmp_path, check=True, capture_output=True)
    # As Windows runners set it: git archive would hand back stock.tsv with CRLF, which read_catalog rejects
    subprocess.run([git, "config", "core.autocrlf", "true"], cwd=tmp_path, check=True, capture_output=True)
    commit([_part("C1"), _part("C2"), _part("C3")], "2026-11-12")
    commit([_part("C1"), _part("C3")], "2026-11-13")
    commit([_part("C1")], "2026-11-14")
    commit([_part("C1"), _part("C2")], "2026-11-15")
    rows = backfill(tmp_path)
    assert {code: row["g"] for code, row in rows.items()} == {"C3": "2026-11-14"}
    assert rows["C3"]["s"] == 50 and rows["C3"]["m"] == "MC3"
