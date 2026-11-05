"""0.8.15: four reports from the avr-trigger-splitter design session (2026-11-04).

- jlc_search's stock and price are the daily snapshot's (C14663: 38,555,997 at $0.0083, while
  jlc_get_part had 37,538,619 at $0.0072); replies now say when it was scraped (data_as_of).
- A spec filter given as an argument is in filters_applied but not in parsed; the description says
  which is which.
- jlc_stock_check("C5947") also listed four TLC5947 drivers, and "C1622" 16.2k resistors.
- Packages read "插件,12.6x4.4mm" (C2681581) beside "Plugin" (C496551).
"""

import gzip
import inspect
import json
import re
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.client import JLCPCBClient
from pcbparts_mcp.db import _iso_utc, get_db
from pcbparts_mcp.mounting import detect_mounting_type, english_package

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import build_database  # noqa: E402
from search_baseline import offline  # noqa: E402


def _sent(tool, param=None):
    """The description fastmcp sends for a tool (its first text section) or a parameter: a docstring's
    Returns section never reaches clients (the 0.8.15 Mouser lifecycle note was there at first)."""
    from fastmcp.utilities.docstring_parsing import parse_docstring
    parsed = parse_docstring(tool)
    return " ".join((parsed.parameters[param] if param else parsed.description).split())


@pytest.fixture
async def no_network():
    # Async so the event loop exists first: on Windows its socket pair is built with connect()
    with offline():
        yield


class TestEnglishPackage:
    @pytest.mark.parametrize("raw, english", [
        ("插件,12.6x4.4mm", "Plugin,12.6x4.4mm"),
        ("插件-3P,7x6.8mm", "Plugin-3P,7x6.8mm"),
        ("插件,P=1.75mm(交错脚)", "Plugin,P=1.75mm(Staggered pins)"),
        ("弯插,10.6x7.5mm", "Plugin,10.6x7.5mm,Right Angle"),
        ("弯插-4P,6x6mm", "Plugin-4P,6x6mm,Right Angle"),
        ("弯插,P=3mm(交错脚)", "Plugin,P=3mm(Staggered pins),Right Angle"),
        ("SMD,P=0.5mm,Surface Mount，Right Angle", "SMD,P=0.5mm,Surface Mount,Right Angle"),
        ("SMD,7.7x3.6mm,卧贴", "SMD,7.7x3.6mm,Right Angle"),
        ("SMD,P=1.25mm,立贴", "SMD,P=1.25mm,Vertical"),
        ("SMD,10.62×3.81mm", "SMD,10.62x3.81mm"),
        ("SOТ23-6", "SOT23-6"),  # Cyrillic Т (C5371028)
        ("螺栓,D38xL75mm", "Bolt,D38xL75mm"),
    ])
    def test_translated(self, raw, english):
        assert english_package(raw) == english

    @pytest.mark.parametrize("package", [None, "", "Plugin", "0603", "SOT-23-6", "白色"])
    def test_left_alone(self, package):
        assert english_package(package) == package

    @pytest.mark.parametrize("raw", ["插件,12.6x4.4mm", "弯插-4P,6x6mm", "SMD,7.7x3.6mm,卧贴", "SOТ23-6"])
    def test_mounting_unchanged_or_found(self, raw):
        mounting = detect_mounting_type(english_package(raw))
        assert mounting == ("smd" if raw.startswith(("SMD", "SO")) else "through_hole")

    def test_live_parts(self):
        part = JLCPCBClient()._transform_part(
            {"componentCode": "C2681581", "componentSpecificationEn": "插件,12.6x4.4mm"}, slim=True)
        assert part["package"] == "Plugin,12.6x4.4mm" and part["mounting_type"] == "through_hole"

    def test_build(self, tmp_path):
        (tmp_path / "categories").mkdir()
        with gzip.open(tmp_path / "categories" / "switches.jsonl.gz", "wt", encoding="utf-8") as f:
            for lcsc, package in (("C2681581", "插件,12.6x4.4mm"), ("C496551", "Plugin")):
                f.write(json.dumps({"l": lcsc, "m": "M" + lcsc, "f": "X", "p": package, "s": 100, "t": "e",
                                    "c": 1, "$": 0.1, "d": "", "a": []}, ensure_ascii=False) + "\n")
        build_database(tmp_path, tmp_path / "c.db", verbose=False)
        conn = sqlite3.connect(tmp_path / "c.db")
        try:
            assert dict(conn.execute("SELECT lcsc, package FROM components")) == {
                "C2681581": "Plugin,12.6x4.4mm", "C496551": "Plugin"}
        finally:
            conn.close()

    def test_catalog(self):
        db = get_db()
        db._ensure_db()
        left = [package for (package,) in db._conn.execute(
            "SELECT DISTINCT package FROM components WHERE package LIKE '%插件%' OR package LIKE '%弯插%' "
            "OR package LIKE '%，%' OR package LIKE '%卧贴%' OR package LIKE '%交错脚%'")]
        assert left == []


class TestDataAsOf:
    def test_iso(self):
        assert _iso_utc("2026-11-04T20:10:49.531605+00:00") == "2026-11-04T20:10:49Z"
        assert _iso_utc("2026-11-04T15:10:49-05:00") == "2026-11-04T20:10:49Z"
        assert _iso_utc("not a date") is None

    def test_build_keeps_scrape_time(self, tmp_path):
        (tmp_path / "categories").mkdir()
        with gzip.open(tmp_path / "categories" / "resistors.jsonl.gz", "wt", encoding="utf-8") as f:
            f.write(json.dumps({"l": "C1", "m": "M1", "f": "X", "p": "0402", "s": 100, "t": "b", "c": 1,
                                "$": 0.01, "d": "", "a": []}) + "\n")
        (tmp_path / "manifest.json").write_text(json.dumps(
            {"scraped_at": "2026-11-04T20:10:49.531605+00:00", "categories": {}}), encoding="utf-8")
        build_database(tmp_path, tmp_path / "c.db", verbose=False)
        from pcbparts_mcp.db import ComponentDatabase
        db = ComponentDatabase(db_path=tmp_path / "c.db", data_dir=tmp_path)
        try:
            assert db.scraped_at() == "2026-11-04T20:10:49Z"
        finally:
            db.close()

    async def test_search_says_when(self, no_network):
        result = await server.jlc_search(query="100nF capacitor X7R", package="0603", library_type="basic")
        assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", result["data_as_of"])
        assert result["data_as_of"] == get_db().scraped_at()

    def test_descriptions(self):
        search = _sent(server.jlc_search)
        assert "daily catalog snapshot" in search and "data_as_of" in search and "1-piece price" in search
        assert "jlc_get_part and jlc_stock_check are live" in search
        assert "live, held up to an hour" in _sent(server.jlc_get_part)


class TestFiltersAppliedVsParsed:
    """The reported search: Voltage >= 25V ran (a 50V part came back) but only filters_applied said so."""

    async def test_explicit_filter_runs(self, no_network):
        kwargs = dict(query="100nF capacitor X7R", package="0603", library_type="all", limit=100)
        plain = await server.jlc_search(**kwargs)
        rated = await server.jlc_search(**kwargs, spec_filters=[{"name": "Voltage", "op": ">=", "value": "25V"}])
        assert {"name": "Voltage", "op": ">=", "value": "25V"} in rated["filters_applied"]["spec_filters"]
        assert all(f["name"] != "Voltage" for f in rated["parsed"]["spec_filters"])
        assert 0 < rated["total"] < plain["total"]
        volts = [float(p["specs"]["Voltage Rating"].rstrip("V")) for p in rated["results"]]
        assert volts and min(volts) >= 25

    def test_description(self):
        doc = _sent(server.jlc_search)
        assert "filters_applied lists every filter that ran" in doc
        assert "parsed shows only what the query text gave" in doc


EXACT = {"lcsc": "C5947", "model": "74HC595D,118", "stock": 430944}
NEIGHBOURS = [{"lcsc": "C702083", "model": "TLC5947RHBR", "stock": 2688},
              {"lcsc": "C181402", "model": "TLC5947RHBT", "stock": 239}]


class TestStockCheckLcscCode:
    class Calls(list):
        client = None

    @pytest.fixture
    def calls(self, monkeypatch):
        calls = self.Calls()

        def client(results):
            async def search(**kwargs):
                calls.append(kwargs)
                return {"results": results, "page": kwargs["page"], "per_page": kwargs["limit"],
                        "total": len(results), "total_pages": 1, "has_more": False}
            monkeypatch.setattr(server, "_client", SimpleNamespace(search=search))
        calls.client = client
        return calls

    @pytest.mark.parametrize("query", ["C5947", " c5947 "])
    async def test_only_that_part(self, calls, query):
        calls.client([*NEIGHBOURS, EXACT])  # the exact part below others, as a stock sort can put it
        result = await server.jlc_stock_check(query=query)
        assert result["results"] == [EXACT] and result["total"] == 1 and not result["has_more"]
        assert "hint" not in result
        # JLCPCB's own order puts the code's part first; a whole page so it's always in it
        assert calls[0]["sort_by"] is None and calls[0]["limit"] == 100 and calls[0]["page"] == 1

    async def test_later_page_is_empty(self, calls):
        calls.client([EXACT, *NEIGHBOURS])
        result = await server.jlc_stock_check(query="C5947", page=2)
        assert result["results"] == [] and result["total"] == 1 and result["page"] == 2
        assert calls[0]["page"] == 1

    async def test_missing_part_says_so(self, calls):
        calls.client(NEIGHBOURS)
        result = await server.jlc_stock_check(query="C5947", package="0402")
        assert result["results"] == [] and result["total"] == 0
        assert "No part C5947 with stock >= 10 matching package" in result["hint"]
        assert 'jlc_get_part(lcsc="C5947")' in result["hint"]

    async def test_text_queries_unchanged(self, calls):
        calls.client(NEIGHBOURS)
        result = await server.jlc_stock_check(query="TLC5947", limit=5)
        assert result["results"] == NEIGHBOURS
        assert calls[0]["sort_by"] == "quantity" and calls[0]["limit"] == 5

    def test_description(self):
        doc = _sent(server.jlc_stock_check, "query")
        assert 'one LCSC code ("C5947") returns that part only' in doc


class TestStockCheckPriceTiers:
    """todo-idea-jlc-stock-check-price-tiers: a BOM line took jlc_stock_check for stock and jlc_get_part
    for the price at the order quantity, two calls and two moments."""

    ITEM = {"componentCode": "C9196", "componentModelEn": "1206B102K202NT", "stockCount": 1640407,
            "componentPrices": [{"startNumber": 1, "productPrice": 0.0228}, {"startNumber": 300, "productPrice": 0.0176},
                                {"startNumber": 30000, "productPrice": 0.0123}]}
    TIERS = [{"qty": "1+", "price": 0.0228}, {"qty": "300+", "price": 0.0176}, {"qty": "30000+", "price": 0.0123}]

    def test_transform(self):
        client = JLCPCBClient()
        assert "prices" not in client._transform_part(self.ITEM, slim=True)
        assert client._transform_part(self.ITEM, slim=True, with_prices=True)["prices"] == self.TIERS
        assert client._transform_part(self.ITEM, slim=False)["prices"] == self.TIERS

    async def test_client_search(self, monkeypatch):
        client = JLCPCBClient()

        async def request(url, params):
            return {"data": {"componentPageInfo": {"list": [self.ITEM], "total": 1}}}
        monkeypatch.setattr(client, "_request", request)
        assert (await client.search(query="C9196", with_prices=True))["results"][0]["prices"] == self.TIERS
        assert "prices" not in (await client.search(query="C9196"))["results"][0]
        no_fee = await client.search(query="C9196", library_type="no_fee", with_prices=True)
        assert no_fee["results"][0]["prices"] == self.TIERS

    async def test_only_lcsc_code_queries_ask(self, monkeypatch):
        asked = []

        async def search(**kwargs):
            asked.append(kwargs["with_prices"])
            return {"results": [], "total": 0}
        monkeypatch.setattr(server, "_client", SimpleNamespace(search=search))
        await server.jlc_stock_check(query="C9196")
        await server.jlc_stock_check(query="1nF 2kV 1206")
        assert asked == [True, False]

    def test_description(self):
        doc = _sent(server.jlc_stock_check, "query")
        assert "with its price tiers (prices, as in jlc_get_part)" in doc


class TestMouserLifecycle:
    """todo-idea-maker-nrnd-status-vs-mouser-lifecycle: mouser_get_part said AP2553W6-7 was Active;
    Diodes' datasheet and DigiKey say NRND, and Mouser itself states no status for it."""

    @pytest.mark.parametrize("raw, lifecycle", [
        ({"IsDiscontinued": "No"}, None),
        ({}, None),
        ({"LifecycleStatus": "Not Recommended for New Designs", "IsDiscontinued": "No"},
         "Not Recommended for New Designs"),
        ({"LifecycleStatus": "End of Life"}, "End of Life"),
        ({"IsDiscontinued": "Yes"}, "Discontinued"),
    ])
    def test_only_what_mouser_states(self, raw, lifecycle):
        from pcbparts_mcp.mouser import _normalize_part
        assert _normalize_part({"MouserPartNumber": "621-AP2553W6-7", **raw})["lifecycle"] == lifecycle

    def test_descriptions(self):
        mouser = _sent(server.mouser_get_part)
        assert "else null: Mouser states none for most parts" in mouser and "digikey_get_part's lifecycle" in mouser
        assert "Mouser's is null where it states none" in _sent(server.jlc_get_part)
        digikey = _sent(server.digikey_get_part)
        assert "other_packaging lists the rest" in digikey and "lifecycle is DigiKey's product status" in digikey


def _switch_db(tmp_path):
    from pcbparts_mcp.db import ComponentDatabase
    (tmp_path / "categories").mkdir()
    with gzip.open(tmp_path / "categories" / "switches.jsonl.gz", "wt", encoding="utf-8") as f:
        for lcsc, package in (("C2681581", "插件,12.6x4.4mm"), ("C1", "Plugin,12.6x4.4mm"), ("C2", "0603")):
            f.write(json.dumps({"l": lcsc, "m": "M" + lcsc, "f": "X", "p": package, "s": 100, "t": "e",
                                "c": 1, "$": 0.1, "d": "", "a": []}, ensure_ascii=False) + "\n")
    build_database(tmp_path, tmp_path / "c.db", verbose=False)
    return ComponentDatabase(db_path=tmp_path / "c.db", data_dir=tmp_path)


class TestPackageFilterRoundTrip:
    """Review finding: a package copied from a reply ("Plugin,12.6x4.4mm") found nothing live, since
    JLCPCB filters on its own spelling ("插件,12.6x4.4mm"); checked live 2026-11-04 (0 parts)."""

    def test_spellings(self, tmp_path):
        db = _switch_db(tmp_path)
        try:
            assert db.upstream_packages(["Plugin,12.6x4.4mm"]) == ["Plugin,12.6x4.4mm", "插件,12.6x4.4mm"]
            assert db.upstream_packages(["插件,12.6x4.4mm"]) == ["插件,12.6x4.4mm", "Plugin,12.6x4.4mm"]
            assert db.upstream_packages(["0603", "SOT-23"]) == ["0603", "SOT-23"]
        finally:
            db.close()

    @pytest.fixture
    def asked(self, tmp_path, monkeypatch):
        db = _switch_db(tmp_path)
        monkeypatch.setattr(server, "get_db", lambda: db)
        asked = []

        async def search(**kwargs):
            asked.append(kwargs)
            return {"results": [], "total": 0}
        monkeypatch.setattr(server, "_client", SimpleNamespace(search=search))
        yield asked
        db.close()

    async def test_stock_check_sends_jlcpcb_spelling(self, asked):
        await server.jlc_stock_check(query="slide switch", package="Plugin,12.6x4.4mm")
        await server.jlc_stock_check(query="slide switch", packages=["Plugin,12.6x4.4mm", "0603"])
        await server.jlc_stock_check(query="resistor", package="0603")
        assert asked[0]["package"] is None
        assert asked[0]["packages"] == ["Plugin,12.6x4.4mm", "插件,12.6x4.4mm"]
        assert asked[1]["packages"] == ["Plugin,12.6x4.4mm", "插件,12.6x4.4mm", "0603"]
        assert asked[2]["package"] == "0603" and asked[2]["packages"] is None

    async def test_search_reads_chinese_input(self, no_network):
        chinese = await server.jlc_search(query="slide switch", package="插件,12.6x4.4mm", limit=50)
        english = await server.jlc_search(query="slide switch", package="Plugin,12.6x4.4mm", limit=50)
        assert chinese["filters_applied"]["package"] == "Plugin,12.6x4.4mm"
        assert [p["lcsc"] for p in chinese["results"]] == [p["lcsc"] for p in english["results"]]
        listed = await server.jlc_search(query="slide switch", packages=["插件,12.6x4.4mm"], limit=50)
        assert listed["filters_applied"]["packages"] == ["Plugin,12.6x4.4mm"]

    def test_catalog_table(self):
        db = get_db()
        db._ensure_db()
        rows = db._conn.execute("SELECT package, upstream FROM package_spellings").fetchall()
        assert rows and all(english_package(upstream) == package != upstream for package, upstream in rows)


class TestOlderDatabase:
    """Review finding: a database built before 0.8.15 keeps "插件,12.6x4.4mm", so jlc_search mustn't
    translate a package filter there, and the start-up warning says to rebuild."""

    @pytest.fixture
    def old_db(self, tmp_path, monkeypatch, caplog):
        db = _switch_db(tmp_path)
        db.close()
        conn = sqlite3.connect(tmp_path / "c.db")
        conn.execute("DROP TABLE package_spellings")
        conn.execute("DROP TABLE metadata")
        conn.execute("UPDATE components SET package = '插件,12.6x4.4mm' WHERE lcsc = 'C2681581'")
        conn.commit()
        conn.close()
        from pcbparts_mcp.db import ComponentDatabase
        db = ComponentDatabase(db_path=tmp_path / "c.db", data_dir=tmp_path)
        monkeypatch.setattr(server, "get_db", lambda: db)
        yield db
        db.close()

    async def test_search_keeps_the_spelling(self, old_db, caplog):
        assert not old_db.english_packages()
        assert "package names keep JLCPCB's Chinese words" in caplog.text
        assert old_db.scraped_at() is None and old_db.upstream_packages(["0603"]) == ["0603"]
        result = await server.jlc_search(package="插件,12.6x4.4mm", limit=5)
        assert result["filters_applied"]["package"] == "插件,12.6x4.4mm"
        assert [p["lcsc"] for p in result["results"]] == ["C2681581"] and "data_as_of" not in result

    def test_new_database(self, tmp_path):
        db = _switch_db(tmp_path)
        try:
            assert db.english_packages()
        finally:
            db.close()


class TestJlcpcbSpellings:
    """Review finding: the catalog has parts with stock >= 10 only, so jlc_stock_check(min_stock=0) can
    list a package no catalog part has; its JLCPCB spellings come from the translation rules."""

    @pytest.mark.parametrize("package, upstream", [
        ("Plugin,9.9x3.3mm", "插件,9.9x3.3mm"),
        ("Plugin-4P,6x6mm,Right Angle", "弯插-4P,6x6mm"),
        ("Plugin,P=3mm(Staggered pins),Right Angle", "弯插,P=3mm(交错脚)"),
        ("SMD,P=0.5mm,Surface Mount,Right Angle", "SMD,P=0.5mm,Surface Mount，Right Angle"),
        ("SMD,7.7x3.6mm,Right Angle", "SMD,7.7x3.6mm,卧贴"),
        ("SMD,P=0.5mm.Right Angle", "SMD,P=0.5mm.卧贴"),
        ("SMD,P=1.25mm,Vertical", "SMD,P=1.25mm,立贴"),
        ("Bolt,D38xL75mm", "螺栓,D38xL75mm"),
        ("Plug", "插头"),
    ])
    def test_rules(self, package, upstream):
        from pcbparts_mcp.mounting import jlcpcb_package_spellings
        spellings = jlcpcb_package_spellings(package)
        assert spellings[0] == package and upstream in spellings
        assert all(english_package(s) == package for s in spellings) and len(spellings) <= 12

    def test_ascii_package_alone(self):
        from pcbparts_mcp.mounting import jlcpcb_package_spellings
        assert jlcpcb_package_spellings("0603") == ["0603"] and jlcpcb_package_spellings("SOT-23-6") == ["SOT-23-6"]

    def test_without_catalog_rows(self, tmp_path):
        db = _switch_db(tmp_path)
        try:  # no part in this catalog has 9.9x3.3mm
            assert db.upstream_packages(["Plugin,9.9x3.3mm"]) == ["Plugin,9.9x3.3mm", "插件,9.9x3.3mm"]
        finally:
            db.close()

    def test_catalog_spellings_all_sent(self):
        db = get_db()
        db._ensure_db()
        rows = db._conn.execute("SELECT package, upstream FROM package_spellings").fetchall()
        assert rows and all(upstream in db.upstream_packages([package]) for package, upstream in rows)
