"""0.10.0: jlc_get_parts, up to 50 LCSC codes or MPNs answered from the daily snapshot in one call
(BOM refreshes without live JLCPCB requests), and exact/ambiguous on jlc_get_part(mpn). Rows use
jlc_get_part's field names and price shape, so a client parses both the same way.
No network: a small built catalog and offline()."""

import json
import sqlite3
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastmcp import Client
from jsonschema import validate

from conftest import write_catalog_category

import pcbparts_mcp.server as server
from pcbparts_mcp import stats
from pcbparts_mcp.client import JLCPCBClient
from pcbparts_mcp.db import ComponentDatabase

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import build_database  # noqa: E402
from search_baseline import offline  # noqa: E402

SUBCATEGORIES = {
    "11": {"name": "Operational Amplifier", "category_id": 3, "category_name": "Amplifiers/Comparators"},
    "12": {"name": "MOSFETs", "category_id": 1, "category_name": "Transistors/Thyristors"},
    "13": {"name": "Multilayer Ceramic Capacitors MLCC - SMD/SMT", "category_id": 2, "category_name": "Capacitors"},
    "14": {"name": "Bipolar Transistors - BJT", "category_id": 1, "category_name": "Transistors/Thyristors"},
}


def part(lcsc, mpn, maker, package, stock, library="e", sub=11, price=0.01, description="", attrs=(), **extra):
    return {"l": lcsc, "m": mpn, "f": maker, "p": package, "s": stock, "t": library, "c": sub, "$": price,
            "d": description, "a": [list(a) for a in attrs], "x": 0, **extra}


AMPLIFIERS = [
    part("C7950", "LM358DR2G", "onsemi", "SOIC-8", 495224, "b", price=0.054,
         description="Dual op amp SOIC-8 Operational Amplifier ROHS", attrs=[("Number of Channels", "2")]),
    part("C5252902", "LM358", "MSKSEMI", "SOP-8", 338940, price=0.039, description="op amp"),
    part("C5296727", "LM358", "JSMSEMI", "SOP-8", 196229, price=0.0355, x=2, n=1),
    # one part number from twelve makers: more than a row lists
    *[part(f"C{100 + i}", "LM324", f"Maker{i:02d}", "SOP-14", 5000 - i) for i in range(12)],
    part("C300", "NOPRICE1", "Vendor", "SOIC-8", 100, price=None),
]
TRANSISTORS = [
    part("C20917", "AO3400A", "Alpha & Omega Semicon", "SOT-23", 1_000_000, "p", sub=12, price=0.03),
    part("C6749", "C1815", "CJ", "TO-92", 5000, sub=14),  # 2SC1815's short name is also an LCSC code
    part("C916392", "SS8050", "JSMSEMI", "SOT-23", 2_030_627, sub=14),
    part("C2931495", "SS8050", "JSMSEMI", "TO-92", 33_277, sub=14),
    part("C5000945", "C945", "CJ", "TO-92", 4000, sub=14),  # 2SC945's short name, shaped like an LCSC code
]
CAPACITORS = [
    part("C1815", "CL21B104KBCNNNC", "Samsung Electro-Mechanics", "0805", 10_000, "b", sub=13, price=0.005,
         description="100nF 50V X7R 0805", attrs=[("Capacitance", "100nF")]),
    part("C1525", "CL05B104KO5NNNC", "Samsung Electro-Mechanics", "0402", 37_286_642, "b", sub=13, price=0.0029,
         description="100nF 16V X7R 0402", attrs=[("Capacitance", "100nF")]),
]


@pytest.fixture(scope="module")
def catalog(tmp_path_factory):
    data = tmp_path_factory.mktemp("catalog")
    write_catalog_category(data, "amplifiers", AMPLIFIERS)
    write_catalog_category(data, "transistors", TRANSISTORS)
    write_catalog_category(data, "capacitors", CAPACITORS)
    (data / "subcategories.json").write_text(json.dumps(SUBCATEGORIES), encoding="utf-8")
    (data / "manifest.json").write_text(json.dumps(
        {"scraped_at": "2026-11-17T22:00:00+00:00", "prices_updated_at": "2026-11-12T20:00:00+00:00",
         "categories": {}}), encoding="utf-8")
    build_database(data, data / "c.db", verbose=False)
    db = ComponentDatabase(db_path=data / "c.db", data_dir=data)
    yield db
    db.close()  # before the temporary directory goes (Windows)


@pytest.fixture
async def db(catalog, monkeypatch):
    # Async so the event loop exists before sockets are blocked (Windows builds it with connect())
    monkeypatch.setattr(server, "get_db", lambda: catalog)
    with offline():
        yield catalog


async def get_parts(parts):
    return await server.jlc_get_parts(parts)


def outcome(reply):
    return server._call_outcome(SimpleNamespace(structured_content=reply))


class TestCodeRows:
    async def test_fields_and_price_shape(self, db):
        reply = await get_parts(["c7950", " C1525 ", "C99999999"])
        assert list(reply) == ["data_as_of", "prices_as_of", "price_tiers_as_of", "total", "counts", "results", "hint"]
        assert (reply["data_as_of"], reply["prices_as_of"]) == ("2026-11-17T22:00:00Z", "2026-11-12T20:00:00Z")
        assert reply["price_tiers_as_of"] is None  # built without price_tiers.tsv.gz (test_price_tiers.py has them)
        amp, cap, missing = reply["results"]
        assert amp == {
            "input": "c7950", "lcsc": "C7950", "model": "LM358DR2G", "manufacturer": "onsemi", "package": "SOIC-8",
            "stock": 495224, "price": 0.054, "prices": [{"qty": "1+", "price": 0.054}], "library_type": "basic",
            "preferred": False, "pcba_type": "economic", "category": "Amplifiers/Comparators",
            "subcategory": "Operational Amplifier", "description": "Dual op amp SOIC-8 Operational Amplifier ROHS"}
        assert cap["input"] == " C1525 " and cap["lcsc"] == "C1525" and cap["description"] == "100nF 16V X7R 0402"
        assert missing == {"input": "C99999999", "lcsc": "C99999999", "not_found": True}
        assert reply["counts"] == {"found": 2, "gone": 0, "not_found": 1, "error": 0} and reply["total"] == 3
        assert "jlc_get_part(lcsc=...)" in reply["hint"] and "jlc_stock_check" in reply["hint"]
        assert "data_source" not in json.dumps(reply)  # the times are given once, at the top

    async def test_names_are_jlc_get_parts(self, db):
        """Every row field is one jlc_get_part(lcsc) gives for the same fact, prices in its shape."""
        live = JLCPCBClient()._transform_part({
            "componentCode": "C7950", "componentModelEn": "LM358DR2G", "componentBrandEn": "onsemi",
            "componentSpecificationEn": "SOIC-8", "stockCount": 495224, "componentLibraryType": "base",
            "componentPrices": [{"startNumber": 1, "productPrice": 0.054}, {"startNumber": 10, "productPrice": 0.05}],
            "firstSortName": "Operational Amplifier", "secondSortName": "Amplifiers/Comparators",
            "componentProductType": 0, "describe": "op amp", "attributes": []}, slim=False)
        row = (await get_parts(["C7950"]))["results"][0]
        assert set(row) - {"input"} <= set(live)
        assert row["prices"][0].keys() == live["prices"][0].keys() and row["prices"][0]["qty"] == live["prices"][0]["qty"]
        for key in ("lcsc", "model", "manufacturer", "package", "stock", "price", "library_type", "preferred",
                    "pcba_type", "category", "subcategory"):
            assert row[key] == live[key], key

    async def test_flags_and_missing_price(self, db):
        standard, preferred, unpriced = (await get_parts(["C5296727", "C20917", "C300"]))["results"]
        assert standard["pcba_type"] == "standard_only" and standard["no_datasheet"] is True
        assert standard["description"] == ""  # the catalog's value, as jlc_get_part(mpn) gives it
        assert (preferred["library_type"], preferred["preferred"]) == ("preferred", True)
        assert unpriced["price"] is None and "prices" not in unpriced  # as jlc_get_part: tiers only where listed

    async def test_input_order_kept_and_repeats_answered(self, db):
        reply = await get_parts(["C1525", "C7950", "c1525"])
        assert [row["input"] for row in reply["results"]] == ["C1525", "C7950", "c1525"]
        assert [row["lcsc"] for row in reply["results"]] == ["C1525", "C7950", "C1525"]
        assert reply["counts"]["found"] == 3 and "hint" not in reply


class TestMpnRows:
    async def test_answered_like_jlc_get_part(self, db):
        row = (await get_parts(["LM358"]))["results"][0]
        single = await server.jlc_get_part(mpn="LM358")
        assert (row["input"], row["mpn"]) == ("LM358", "LM358")
        assert (row["total"], row["exact"], row["ambiguous"]) == (single["total"], single["exact"], single["ambiguous"]) == (2, True, True)
        assert [p["lcsc"] for p in row["results"]] == [p["lcsc"] for p in single["results"]] == ["C5252902", "C5296727"]
        for mine, theirs in zip(row["results"], single["results"]):
            assert {k: theirs[k] for k in mine if k in theirs} == {k: v for k, v in mine.items() if k in theirs}
        assert not {"match", "matched_mpn", "note"} & set(row)

    async def test_ten_listed_total_counts_all(self, db):
        row = (await get_parts(["LM324"]))["results"][0]
        assert row["total"] == 12 and len(row["results"]) == 10
        assert [p["lcsc"] for p in row["results"]] == [f"C{100 + i}" for i in range(10)]  # most stock first
        assert row["ambiguous"] is True

    async def test_recoveries_keep_their_match_info(self, db):
        separators, alias_free = (await get_parts(["AO-3400A", "ao3400a"]))["results"]
        single = await server.jlc_get_part(mpn="AO-3400A")
        assert (separators["exact"], separators["match"], separators["matched_mpn"]) == (False, "separators", "AO3400A")
        assert {k: single[k] for k in ("match", "matched_mpn", "exact", "ambiguous")} == {
            k: separators[k] for k in ("match", "matched_mpn", "exact", "ambiguous")}
        assert (alias_free["exact"], alias_free["ambiguous"]) == (True, False) and "match" not in alias_free

    async def test_not_found(self, db):
        reply = await get_parts(["ZZQ9981XK", "C7950"])
        assert reply["results"][0] == {"input": "ZZQ9981XK", "mpn": "ZZQ9981XK", "total": 0, "results": [],
                                       "not_found": True}
        assert reply["counts"] == {"found": 1, "gone": 0, "not_found": 1, "error": 0} and "hint" in reply

    async def test_the_maker_narrows_the_matches(self, db):
        mine, loose, other = (await get_parts([
            {"mpn": "LM358", "manufacturer": "JSMSEMI"}, {"mpn": "SS8050", "manufacturer": "jsmsemi"},
            {"mpn": "AO3400A", "manufacturer": "Nobody Inc"}]))["results"]
        assert (mine["total"], mine["ambiguous"], mine["results"][0]["lcsc"]) == (1, False, "C5296727")
        assert mine["input"] == {"mpn": "LM358", "manufacturer": "JSMSEMI"}
        assert loose["total"] == 2 and loose["ambiguous"] is True  # one maker, two packages: still a choice
        assert other == {"input": {"mpn": "AO3400A", "manufacturer": "Nobody Inc"}, "mpn": "AO3400A", "total": 0,
                         "results": [], "not_found": True, "other_manufacturers": ["Alpha & Omega Semicon"]}

    async def test_no_full_text_guesses(self, db):
        """jlc_get_part(mpn="LM32") answers with full-text related parts (LM324s); a BOM line needs
        sure matches, and short or common tokens ("R", "10k") made full-text lookups take up to 1.7 s
        each, so jlc_get_parts never runs them: not_found, the hint pointing to jlc_search for values.
        Its makers don't list the number, so a miss for a maker given names none of them."""
        assert (await server.jlc_get_part(mpn="LM32"))["match"] == "related"
        reply = await get_parts(["LM32", {"mpn": "LM32", "manufacturer": "Nobody Inc"}, "op amp"])
        assert reply["results"] == [
            {"input": "LM32", "mpn": "LM32", "total": 0, "results": [], "not_found": True},
            {"input": {"mpn": "LM32", "manufacturer": "Nobody Inc"}, "mpn": "LM32", "total": 0, "results": [],
             "not_found": True},
            {"input": "op amp", "mpn": "op amp", "total": 0, "results": [], "not_found": True}]
        assert reply["counts"] == {"found": 0, "gone": 0, "not_found": 3, "error": 0}
        assert "never by their text" in reply["hint"] and "jlc_search finds parts" in reply["hint"]

    async def test_no_full_text_query_runs(self, db):
        queries = []
        db._ensure_db()
        db._conn.set_trace_callback(queries.append)
        try:
            await get_parts(["LM32", "R", "10k", {"mpn": "LM3", "manufacturer": "MSKSEMI"}])
        finally:
            db._conn.set_trace_callback(None)
        assert queries and not any("components_fts" in query for query in queries)

    async def test_the_maker_picks_matched_mpn_too(self, db):
        row = (await get_parts([{"mpn": "LM-358", "manufacturer": "JSMSEMI"}]))["results"][0]
        assert (row["match"], row["matched_mpn"], row["total"]) == ("separators", "LM358", 1)

    async def test_codes_and_part_numbers_shaped_like_codes(self, db):
        code, number, both = (await get_parts(["C1815", {"mpn": "C1815"}, {"lcsc": "C7950", "mpn": "LM324"}]))["results"]
        assert code["model"] == "CL21B104KBCNNNC"  # a C-code string is an LCSC code
        assert number["results"][0]["lcsc"] == "C6749" and number["exact"] is True
        assert both["lcsc"] == "C7950" and "results" not in both  # lcsc wins over mpn, as in jlc_get_part

    async def test_each_number_looked_up_once(self, db, monkeypatch):
        """Once per number and maker: the maker narrows every match step (see TestMakerNarrowsEachStep),
        so a number given with a maker is its own lookup; repeats aren't."""
        asked = []
        lookup = db.get_by_mpn

        def spy(mpn, **kwargs):
            asked.append((mpn, kwargs["maker"] is not None))
            return lookup(mpn, **kwargs)

        monkeypatch.setattr(db, "get_by_mpn", spy)
        queries = []
        db._ensure_db()
        db._conn.set_trace_callback(queries.append)
        try:
            reply = await get_parts(["LM358", {"mpn": "LM358", "manufacturer": "MSKSEMI"}, "C7950", "C1525", "LM324",
                                     "lm358", {"mpn": "LM358", "manufacturer": "msksemi"}])
        finally:
            db._conn.set_trace_callback(None)
        assert asked == [("LM358", False), ("LM358", True), ("LM324", False), ("lm358", False)]
        assert sum("WHERE lcsc IN" in query for query in queries) == 1  # every row's part in one read
        assert [row["total"] for row in reply["results"] if "total" in row] == [2, 1, 12, 2, 1]


class TestReviewFixes:
    """Review of 2026-11-18: inputs that failed a whole batch or were refused before the tool ran,
    lines that missed their part, and replies ten times the size they needed."""

    async def test_mpn_rows_list_short_matches(self, db):
        code_row, mpn_row = (await get_parts(["C7950", "LM358DR2G"]))["results"]
        match = mpn_row["results"][0]
        assert list(match) == ["lcsc", "model", "manufacturer", "package", "stock", "price", "prices",
                               "library_type", "preferred"]
        assert {key: code_row[key] for key in match} == match
        assert {"description", "category", "subcategory", "pcba_type"} <= set(code_row)  # code rows stay whole

    async def test_control_characters_are_one_rows_error(self, db):
        reply = await get_parts(["LM\x00358", {"mpn": "LM358", "manufacturer": "T\x00I"}, "LM358\tDR2G", "C7950"])
        errors = [row.get("error") for row in reply["results"]]
        assert errors == [server._CONTROL_CHARACTERS["error"]] * 3 + [None]
        assert server._error_kind(errors[0]) == "bad_request"
        assert reply["counts"] == {"found": 1, "gone": 0, "not_found": 0, "error": 3}
        # jlc_get_part raised instead (the NUL broke its full-text query)
        assert await server.jlc_get_part(mpn="LM\x00358") == server._CONTROL_CHARACTERS

    async def test_one_number_the_database_fails_on(self, db, monkeypatch):
        lookup = db.get_by_mpn

        def flaky(mpn, **kwargs):
            if mpn == "LM358":
                raise sqlite3.OperationalError("fts5: syntax error")
            return lookup(mpn, **kwargs)

        monkeypatch.setattr(db, "get_by_mpn", flaky)
        reply = await get_parts(["LM358", "LM324", "C7950"])
        assert reply["results"][0] == {"input": "LM358", "error": "Database not available"}
        assert reply["results"][1]["total"] == 12 and reply["results"][2]["lcsc"] == "C7950"
        assert reply["counts"] == {"found": 2, "gone": 0, "not_found": 0, "error": 1}
        alone = await get_parts(["LM358", "DNP"])
        assert outcome(alone) == "failed" and server._call_reason("failed", alone, None) == "service_not_ready"

    async def test_unusable_lcsc_beside_an_mpn(self, db):
        row, = (await get_parts([{"lcsc": "N/A", "mpn": "LM358DR2G"}]))["results"]
        assert row["input"] == {"lcsc": "N/A", "mpn": "LM358DR2G"} and row["results"][0]["lcsc"] == "C7950"
        entry = server._lifecycle_entry({"lcsc": "-", "mpn": "LM358P", "manufacturer": "TI"})  # part_lifecycle's too
        assert (entry.error, entry.mpn, entry.maker, entry.lcsc) == (None, "LM358P", "TI", None)
        alone, = (await get_parts([{"lcsc": "N/A"}]))["results"]
        assert alone["error"].startswith("lcsc must be an LCSC C-code")

    async def test_a_code_string_not_listed_is_tried_as_a_part_number(self, db):
        reply = await get_parts(["C945", {"lcsc": "C945"}, "C99999999", "c945"])
        number, code, missing, lower = reply["results"]
        assert (number["input"], number["mpn"], number["exact"], number["total"]) == ("C945", "C945", True, 1)
        assert number["results"][0]["lcsc"] == "C5000945" and lower["results"] == number["results"]
        assert number["note"] == ("'C945' isn't an LCSC code in the snapshot or among the parts that left it, "
                                  "so it was looked up as a part number.")
        assert code == {"input": {"lcsc": "C945"}, "lcsc": "C945", "not_found": True}  # asked as a code: a code
        assert missing == {"input": "C99999999", "lcsc": "C99999999", "not_found": True}
        assert reply["counts"] == {"found": 2, "gone": 0, "not_found": 2, "error": 0}

    async def test_deeply_nested_json_is_an_argument_error(self, db, monkeypatch):
        """json.loads raises RecursionError past Python's nesting limit (on the event loop's thread at
        least: how deep a worker thread gets varies by version), which failed the call with an exception."""
        monkeypatch.setattr(server, "_mouser_client", object())  # part_lifecycle parses only with a distributor
        deep = "[" * 100_000 + "]" * 100_000
        reply = await server.part_lifecycle(deep)
        assert reply["error"] == "Invalid parts: not a valid JSON array"
        assert server._error_kind(reply["error"]) == "bad_request"

        def too_deep(text):
            raise RecursionError("maximum recursion depth exceeded while decoding a JSON array")

        monkeypatch.setattr(server.json, "loads", too_deep)
        for tool in (server.jlc_get_parts, server.part_lifecycle):
            assert (await tool('[["x"]]'))["error"] == "Invalid parts: not a valid JSON array", tool

    async def test_long_inputs_are_echoed_cut_short(self, db):
        long, padded, nested = (await get_parts(["M" * 5000, {"mpn": "LM358DR2G", "notes": "x" * 1000},
                                                 [[[[["deep"]]]] * 40]]))["results"]
        assert long["input"] == "M" * 100 + "..." and long["error"] == "MPN too long (max 100 characters)"
        assert padded["input"].startswith('{"mpn": "LM358DR2G", "notes": "xxx') and len(padded["input"]) == 103
        assert padded["results"][0]["lcsc"] == "C7950"  # still answered
        assert len(nested["input"]) == 103 and nested["error"].startswith("Invalid part")
        assert server._lifecycle_entry("M" * 5000).input == "M" * 100 + "..."  # part_lifecycle's input too

    async def test_any_item_type_through_the_server(self, db, monkeypatch):
        """The parameter type let pydantic refuse a native list holding null or a number (the whole
        call an error, isError) before the rows could each say what was wrong; and a bare object."""
        @asynccontextmanager
        async def lifespan(app):
            yield {}

        monkeypatch.setattr(server.mcp, "_lifespan", lifespan)
        monkeypatch.setattr(server, "_mouser_client", None)
        monkeypatch.setattr(server, "_digikey_client", None)
        async with Client(server.mcp) as client:
            for name in ("jlc_get_parts", "part_lifecycle"):
                tool = next(tool for tool in await client.list_tools() if tool.name == name)
                for value in ([None, 7, ["x"], "C7950"], {"mpn": "LM358"}, "LM358", '["C7950"]'):
                    validate({"parts": value}, tool.inputSchema)
            mixed = (await client.call_tool("jlc_get_parts", {"parts": [None, 7, ["x"], "C7950"]})).structured_content
            assert [row.get("error", "")[:13] for row in mixed["results"]] == ["Invalid part:"] * 3 + [""]
            assert mixed["counts"] == {"found": 1, "gone": 0, "not_found": 0, "error": 3}
            bare = (await client.call_tool("jlc_get_parts", {"parts": {"mpn": "LM358DR2G"}})).structured_content
            assert bare["results"][0]["input"] == {"mpn": "LM358DR2G"} and bare["counts"]["found"] == 1
            lifecycle = await client.call_tool("part_lifecycle", {"parts": [None, 7]})
            assert lifecycle.is_error is False  # this server has no distributor keys: the call's own error


class TestJlcGetPartFlags:
    async def test_exact_and_ambiguous(self, db):
        one = await server.jlc_get_part(mpn="AO3400A")
        assert (one["exact"], one["ambiguous"], one["total"]) == (True, False, 1)
        several = await server.jlc_get_part(mpn="lm324")
        assert (several["exact"], several["ambiguous"], several["total"]) == (True, True, 12)
        recovered = await server.jlc_get_part(mpn="AO-3400A")
        assert (recovered["exact"], recovered["match"]) == (False, "separators")
        missed = await server.jlc_get_part(mpn="ZZQ9981XK")
        assert "exact" not in missed and missed["error"].startswith("No part found")  # the miss reply is unchanged


class TestInputs:
    async def test_unusable_inputs_get_their_own_error(self, db):
        reply = await get_parts(["DNP", "", {"mpn": 5}, {"lcsc": "X12"}, "M" * 101,
                                 {"mpn": "LM358", "manufacturer": "T" * 101}, 7, "C7950"])
        errors = [row.get("error", "") for row in reply["results"]]
        assert errors[0].startswith("Invalid part: 'DNP' is a BOM placeholder")
        assert errors[1] == "Give a part number or an LCSC code"
        assert errors[2].startswith("Invalid part: give an MPN") and errors[6] == errors[2]
        assert errors[3].startswith("lcsc must be an LCSC C-code")
        assert errors[4] == "MPN too long (max 100 characters)"
        assert errors[5] == "Manufacturer too long (max 100 characters)"
        assert reply["results"][2]["input"] == {"mpn": 5} and reply["results"][7]["model"] == "LM358DR2G"
        assert reply["counts"] == {"found": 1, "gone": 0, "not_found": 0, "error": 7}
        for error in errors[:7]:
            assert server._error_kind(error) == "bad_request"

    async def test_json_array_string_and_one_part(self, db):
        assert await get_parts('["C7950", {"mpn": "LM358"}]') == await get_parts(["C7950", {"mpn": "LM358"}])
        assert await get_parts('{"mpn": "LM358"}') == await get_parts([{"mpn": "LM358"}])
        one = await get_parts("LM358DR2G")
        assert one["total"] == 1 and one["results"][0]["exact"] is True
        split = await get_parts("C7950,C1525")  # never comma-split: one MPN, read as jlc_get_part reads it
        assert split["total"] == 1 and split["results"][0]["input"] == "C7950,C1525"
        single = await server.jlc_get_part(mpn="C7950,C1525")
        assert (split["results"][0]["match"], split["results"][0]["exact"]) == (single["match"], single["exact"]) == (
            "alternative", False)

    async def test_list_limits(self, db):
        assert (await get_parts([f"C{n}" for n in range(1, 52)]))["error"] == "Too many parts (max 50, got 51)"
        assert len((await get_parts([f"C{n}" for n in range(1, 51)]))["results"]) == 50
        assert (await get_parts([]))["error"].startswith("Give at least one part")
        assert (await get_parts("[]"))["error"].startswith("Give at least one part")
        assert (await get_parts("[1, 2"))["error"].startswith("Invalid parts: ")
        for reply in (await get_parts([]), await get_parts(["C1"] * 51), await get_parts("[1, 2")):
            assert server._error_kind(reply["error"]) == "bad_request"


class TestUsageCounts:
    async def test_outcomes_and_reasons(self, db):
        found = await get_parts(["C7950", "C99999999", "DNP"])
        assert outcome(found) == "ok"
        codes = await get_parts(["C99999999", "DNP"])
        assert outcome(codes) == "not_found" and server._call_reason("not_found", codes, None) == "lcsc_not_found"
        numbers = await get_parts(["ZZQ9981XK", {"mpn": "AO3400A", "manufacturer": "Nobody"}])
        assert outcome(numbers) == "not_found"
        assert server._call_reason("not_found", numbers, None) == "mpn_not_in_snapshot"
        both = await get_parts(["ZZQ9981XK", "C99999999"])
        assert server._call_reason("not_found", both, None) == "part_not_found"
        assert outcome(await get_parts(["DNP", ""])) == "bad_request"

    async def test_database_down(self, monkeypatch):
        class Down:
            def __getattr__(self, name):
                def fail(*args, **kwargs):
                    raise sqlite3.OperationalError("disk I/O error")
                return fail

        monkeypatch.setattr(server, "get_db", lambda: Down())
        for parts in (["LM358"], ["C7950"]):
            reply = await get_parts(parts)
            assert reply == {"error": "Database not available"}
            assert outcome(reply) == "failed" and server._call_reason("failed", reply, None) == "service_not_ready"

    async def test_through_the_server(self, db, monkeypatch):
        # Only the startup/shutdown work is replaced: the real schema, call handling and counts run
        @asynccontextmanager
        async def lifespan(app):
            yield {}

        monkeypatch.setattr(server.mcp, "_lifespan", lifespan)
        async with Client(server.mcp) as client:
            tool = next(tool for tool in await client.list_tools() if tool.name == "jlc_get_parts")
            assert tool.annotations.readOnlyHint is True and tool.annotations.openWorldHint is False
            for value in ("C7950", ["C7950", {"mpn": "LM358", "manufacturer": "TI"}], '["C7950"]'):
                validate({"parts": value}, tool.inputSchema)
            assert "BOM refreshes" in tool.description and "use jlc_get_part" in tool.description
            for value in (["C7950", "ZZQ9981XK"], ["ZZQ9981XK"], ["DNP"]):
                await client.call_tool("jlc_get_parts", {"parts": value})
        day = stats.usage.summary()["days"][0]
        assert {k: day["tools"]["jlc_get_parts"][k] for k in ("ok", "not_found", "bad_request")} == {
            "ok": 1, "not_found": 1, "bad_request": 1}
        assert day["reasons"]["jlc_get_parts"] == {"mpn_not_in_snapshot": 1}
