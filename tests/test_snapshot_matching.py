"""0.10.0 review fixes for MPN matching in jlc_get_parts and jlc_get_part(mpn): the maker given
narrows each match step, maker names across catalogs (ST Microelectronics isn't ST(Semtech)), a gone
part asked by its exact number first when the only in-stock match is another maker's spelling or a
full-text alternative, and notes that add up rather than replace each other.
No network: a small built catalog with sold-out rows, and offline()."""

import json
import sys
from pathlib import Path

import pytest

from conftest import write_catalog_category

import pcbparts_mcp.server as server
from pcbparts_mcp.catalog_files import write_sold_out
from pcbparts_mcp.db import ComponentDatabase

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import build_database  # noqa: E402
from search_baseline import offline  # noqa: E402

SUBCATEGORIES = {
    "21": {"name": "Diodes - General Purpose", "category_id": 4, "category_name": "Diodes"},
    "22": {"name": "Schottky Diodes", "category_id": 4, "category_name": "Diodes"},
    "23": {"name": "Microcontrollers (MCU/MPU/SOC)", "category_id": 5, "category_name": "Embedded Processors & Controllers"},
    "24": {"name": "MOSFETs", "category_id": 6, "category_name": "Transistors/Thyristors"},
    "25": {"name": "Signal Relays", "category_id": 7, "category_name": "Relays"},
    "26": {"name": "Pin Headers", "category_id": 8, "category_name": "Connectors"},
    "27": {"name": "2G/3G/4G/5G Modules", "category_id": 9, "category_name": "IoT/Communication Modules"},
}


def part(lcsc, mpn, maker, stock, sub, package="SMD", price=0.1):
    return {"l": lcsc, "m": mpn, "f": maker, "p": package, "s": stock, "t": "e", "c": sub, "$": price,
            "d": f"{mpn} {maker}", "a": [], "x": 0}


# Real makers and stock from the 2026-11-18 catalog (fewer of them)
PARTS = [
    # 1N4007G from many makers; Comchip spells its own 1N4007-G
    part("C111122", "1N4007G", "Shikues", 137139, 21),
    part("C2457", "1N4007G", "MDD(Microdiode Semiconductor)", 135700, 21),
    part("C3029517", "1N4007G", "ST(Semtech)", 5000, 21),
    part("C2857872", "1N4007-G", "Comchip", 1609, 21),
    # 1N5819 from STMicroelectronics and from Semtech (JLCPCB: "ST(Semtech)")
    part("C437199", "1N5819", "KEXIN", 272535, 22),
    part("C110032", "1N5819", "STMicroelectronics", 16908, 22),
    part("C84618", "1N5819", "ST(Semtech)", 4683, 22),
    part("C8734", "STM32F103C8T6", "STMicroelectronics", 216236, 23, "LQFP-48"),
    part("C10487", "SI2302CDS-T1-GE3", "Vishay Intertech", 300000, 24, "SOT-23"),
    part("C20917", "SI2302", "Other Maker", 900000, 24, "SOT-23"),
    # A relay whose DC24 coil left the snapshot; DC12 and DC5 are only full-text matches of G6DN-1A-SL
    part("C2000012", "G6DN-1A-SL DC12", "Omron", 3000, 25),
    part("C2000005", "G6DN-1A-SL DC5", "Omron", 2000, 25),
    # Molex's 2081001 left; TE lists its own 208100-1, a different part spelled with a dash
    part("C3000001", "208100-1", "TE Connectivity", 5000, 26),
    # Same maker, other separators: stays the answer
    part("C3000002", "HDR-100", "MakerX", 800, 26),
    part("C4000001", "SIM7080G", "SIMCom Wireless Solutions", 900, 27),
]
SOLD_OUT = {
    "C2000024": {"l": "C2000024", "g": "2026-11-15", "s": 40, "$": 1.2, "t": "e", "c": 25,
                 "m": "G6DN-1A-SL DC24", "f": "Omron", "p": "SMD", "d": "relay"},
    "C3000009": {"l": "C3000009", "g": "2026-11-14", "s": 20, "$": 0.3, "t": "e", "c": 26,
                 "m": "2081001", "f": "Molex", "p": "SMD", "d": "header"},
    "C3000010": {"l": "C3000010", "g": "2026-11-14", "s": 20, "$": 0.3, "t": "e", "c": 26,
                 "m": "HDR100", "f": "MakerX", "p": "SMD", "d": "header"},
}


@pytest.fixture(scope="module")
def catalog(tmp_path_factory):
    data = tmp_path_factory.mktemp("matching")
    write_catalog_category(data, "parts", PARTS)
    write_sold_out(data / "catalog", SOLD_OUT)
    (data / "subcategories.json").write_text(json.dumps(SUBCATEGORIES), encoding="utf-8")
    (data / "manifest.json").write_text(json.dumps(
        {"scraped_at": "2026-11-18T22:00:00+00:00", "prices_updated_at": "2026-11-12T20:00:00+00:00",
         "categories": {}}), encoding="utf-8")
    build_database(data, data / "c.db", verbose=False)
    db = ComponentDatabase(db_path=data / "c.db", data_dir=data)
    yield db
    db.close()  # before the temporary directory goes (Windows)


@pytest.fixture
async def db(catalog, monkeypatch):
    monkeypatch.setattr(server, "get_db", lambda: catalog)
    with offline():
        yield catalog


async def rows(*parts):
    return (await server.jlc_get_parts(list(parts)))["results"]


class TestMakerNarrowsEachStep:
    async def test_the_makers_own_spelling(self, db):
        """Eleven makers list 1N4007G exactly; Comchip's is 1N4007-G. Filtering the exact matches
        after the lookup found none of Comchip's; each step now looks for the maker's parts."""
        comchip, = await rows({"mpn": "1N4007G", "manufacturer": "Comchip"})
        assert [p["lcsc"] for p in comchip["results"]] == ["C2857872"]
        assert (comchip["exact"], comchip["match"], comchip["matched_mpn"], comchip["total"]) == (
            False, "separators", "1N4007-G", 1)
        anyone, = await rows("1N4007G")  # without a maker, the exact matches as before
        assert anyone["exact"] is True and "C2857872" not in [p["lcsc"] for p in anyone["results"]]

    async def test_full_text_keeps_ten_of_the_maker(self, db):
        """get_by_mpn's maker also applies before full text's 10 (jlc_get_parts doesn't use full
        text; this keeps the option honest for other callers)."""
        found = db.get_by_mpn("G6DN", maker=lambda name: name == "Omron")
        assert {p["lcsc"] for p in found} == {"C2000012", "C2000005"}
        assert db.get_by_mpn("G6DN", maker=lambda name: name == "Nobody") == []


class TestMakerNames:
    """Review case: "ST Microelectronics" matched JLCPCB's "ST(Semtech)" (and not "STMicroelectronics"),
    so the Semtech part came back as an exact match (fixed in lifecycle.makers_match)."""

    async def test_st_microelectronics_is_not_semtech(self, db):
        st, semtech = await rows({"mpn": "1N5819", "manufacturer": "ST Microelectronics"},
                                 {"mpn": "1N5819", "manufacturer": "Semtech"})
        assert [p["lcsc"] for p in st["results"]] == ["C110032"]
        assert (st["exact"], st["ambiguous"], st["results"][0]["manufacturer"]) == (True, False, "STMicroelectronics")
        assert [p["lcsc"] for p in semtech["results"]] == ["C84618"]

    async def test_st_spellings(self, db):
        for maker in ("ST Microelectronics", "STMicroelectronics", "ST Micro", "ST"):
            row, = await rows({"mpn": "STM32F103C8T6", "manufacturer": maker})
            assert [p["lcsc"] for p in row["results"]] == ["C8734"] and row["exact"] is True, maker

    async def test_vishay_divisions(self, db):
        for maker in ("Vishay Siliconix", "Vishay Dale", "Vishay / Siliconix", "Vishay"):
            row, = await rows({"mpn": "SI2302CDS-T1-GE3", "manufacturer": maker})
            assert [p["lcsc"] for p in row["results"]] == ["C10487"], maker
        other, = await rows({"mpn": "SI2302CDS-T1-GE3", "manufacturer": "Diodes Incorporated"})
        assert other["not_found"] is True and other["other_manufacturers"] == ["Vishay Intertech"]


class TestGoneExactNumberFirst:
    async def test_another_makers_spelling_comes_after(self, db):
        """Molex's 2081001 left the snapshot; TE's 208100-1 (a separators match, another maker's
        part) is all that's in stock. The part asked for comes first (user decision, 2026-11-18)."""
        reply = await server.jlc_get_part(mpn="2081001")
        assert [(p["lcsc"], p.get("gone")) for p in reply["results"]] == [("C3000009", True), ("C3000001", None)]
        assert (reply["exact"], reply["ambiguous"], reply["total"]) == (True, False, 2) and "match" not in reply
        assert reply["note"].startswith("'2081001' itself left the snapshot (the gone parts, listed first)")
        assert "TE Connectivity" in reply["note"] and "'208100-1'" in reply["note"]
        assert reply["hint"].startswith("gone parts") and reply["next_call"]["tool"] == "jlc_stock_check"
        row, = await rows("2081001")
        assert [(p["lcsc"], p["stock"]) for p in row["results"]] == [("C3000009", None), ("C3000001", 5000)]
        assert row["exact"] is True and row["note"] == reply["note"]
        te, = await rows({"mpn": "2081001", "manufacturer": "TE Connectivity"})  # TE's own: today's answer
        assert (te["match"], [p["lcsc"] for p in te["results"]]) == ("separators", ["C3000001"])

    async def test_same_maker_keeps_todays_order(self, db):
        reply = await server.jlc_get_part(mpn="HDR100")  # MakerX's HDR100 gone, its HDR-100 in stock
        assert [p["lcsc"] for p in reply["results"]] == ["C3000002"] and reply["match"] == "separators"
        assert reply["gone_matches"] == 1

    async def test_full_text_alternative_comes_after(self, db):
        """"G6DN-1A-SL DC24" misses; its annotated candidate G6DN-1A-SL finds the DC12 and DC5
        coils by full text, labelled alternative. They were the answer and the DC24 relay asked for
        only a gone_matches count."""
        reply = await server.jlc_get_part(mpn="G6DN-1A-SL DC24")
        assert [(p["lcsc"], p.get("gone")) for p in reply["results"]] == [
            ("C2000024", True), ("C2000012", None), ("C2000005", None)]
        assert reply["exact"] is True and "match" not in reply and "_via" not in reply
        assert "start with 'G6DN-1A-SL'" in reply["note"] and "Part types: Signal Relays." in reply["note"]
        row, = await rows("G6DN-1A-SL DC24")  # no full text in jlc_get_parts: the gone part alone
        assert [p["lcsc"] for p in row["results"]] == ["C2000024"] and row["exact"] is True

    async def test_private_flag_never_in_a_reply(self, db):
        info = {}
        db.get_by_mpn("G6DN-1A-SL DC24", match_info=info)
        assert info["match"] == "alternative" and info["_via"] == "related"  # what _mpn_answer reads
        reply = await server.jlc_get_part(mpn="G6DN-1A-SL DC12 or G6DN-1A-SL DC5")
        assert "_via" not in json.dumps(reply)


class TestNotes:
    async def test_part_type_note_adds_to_the_match_note(self, db):
        """SIM7080 finds SIM7080G by full text: the reply's note kept only the cellular-module note
        and lost the one saying it's no exact match."""
        reply = await server.jlc_get_part(mpn="SIM7080")
        assert reply["match"] == "related"
        assert reply["note"].startswith("No exact match for 'SIM7080'.")
        assert "SIMCom's datasheet lists 18 Cat-M bands" in reply["note"]
