"""Offline #91 regressions: catalog evidence plus identity/precedence controls."""

import json
from pathlib import Path
import sqlite3
import sys

import pytest

from pcbparts_mcp import server
from pcbparts_mcp.db import get_db
from pcbparts_mcp.db.lookup import get_by_mpn
from pcbparts_mcp.search.mpn import MPN_KEY_SQL, annotated_mpn_candidates, is_maker_suffixed, mpn_key

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline

RECOVERIES = [json.loads(line) for line in
              (Path(__file__).parent / "baseline/mpn_recoveries.jsonl").read_text().splitlines()]


@pytest.fixture(autouse=True)
async def no_network():
    with offline():
        yield


@pytest.mark.parametrize("case", RECOVERIES, ids=lambda case: case["input"])
async def test_recorded_recovery(case):
    reply = await server.jlc_get_part(mpn=case["input"])
    # The daily catalog changes: an input that is stocked now must come back as the exact match
    # (TLV76701DRVT wasn't when recorded), and a target no longer stocked can't be recovered.
    if reply.get("results") and "match" not in reply:
        assert all(p["model"].casefold() == case["input"].casefold() for p in reply["results"])
        return
    stocked = get_db().get_by_lcsc_batch([p["lcsc"] for p in case["expected"]])
    if not any(stocked.values()):
        pytest.skip(f"no recorded target is stocked any more ({', '.join(stocked)})")
    assert "error" not in reply
    expected = {(p["lcsc"], p["mpn"]) for p in case["expected"]}
    assert expected.intersection((p["lcsc"], p["model"]) for p in reply["results"])
    assert reply["match"] == {
        "separator_spelling": "separators", "packing_or_finish": "packing",
        "embedded_reel_code": "packing", "alternatives_or_annotations": "alternative",
        "vendor_ordering_alias": "alias",
    }[case["pattern"]]
    assert reply["matched_mpn"]
    if case["pattern"] == "separator_spelling":
        assert all(mpn_key(p["model"]) == mpn_key(case["input"]) for p in reply["results"])
    if case["pattern"] in {"packing_or_finish", "embedded_reel_code", "vendor_ordering_alias"}:
        assert all(p["manufacturer"] in {e["manufacturer"] for e in case["expected"]}
                   for p in reply["results"])


@pytest.mark.parametrize("mpn", [
    "AD8137ARZ-R7", "AVR128DB48T-E/6LX", "AVR128DB48T-E_6LX",
    "LT3957AEUHE#PBF", "STM32L052K8U3",
    "1N4448WQ-7-F", "824032815 or 824031815", "DMC2400UV-7",
    "MMSZ5233BS-7-F", "PESD36VS1UL,315", "SMF4L24AT1G",
])
async def test_no_grade_or_other_manufacturer_substitution(mpn):
    reply = await server.jlc_get_part(mpn=mpn)
    assert reply["results"] == []
    assert reply["error"] == f"No JLCPCB parts found for MPN '{mpn}'"
    assert "match" not in reply


async def test_plus_radio_alias_excludes_non_plus():
    reply = await server.jlc_get_part(mpn="NRF24L01+")
    assert reply["match"] == "alias"
    assert reply["matched_mpn"] == "NRF24L01P-R"
    assert all(p["model"].startswith("NRF24L01P") and p["manufacturer"] == "Nordic Semicon"
               for p in reply["results"])
    # The explicitly requested original chip still works, with its exact reply.
    original = await server.jlc_get_part(mpn="NRF24L01-REEL7")
    assert original["results"] and "match" not in original


async def test_related_ssd1306_names_every_part_type():
    reply = await server.jlc_get_part(mpn="SSD1306")
    assert reply["match"] == "related"
    categories = {p["subcategory"] for p in reply["results"]}
    assert len(categories) >= 2
    assert any("OLED" in c for c in categories)
    assert any("Inductor" in c for c in categories)
    ordered_categories = list(dict.fromkeys(p["subcategory"] for p in reply["results"]))
    assert reply["note"] == (
        "No exact match for 'SSD1306'. These parts' part numbers start with it "
        "or their text mentions it, so check the package and manufacturer. "
        f"Part types: {', '.join(ordered_categories)}."
    )


@pytest.mark.parametrize("mpn", ["AO3400A", "ao3400a", " LM358P "])
async def test_exact_reply_is_unchanged(mpn):
    reply = await server.jlc_get_part(mpn=mpn)
    assert set(reply) == {"mpn", "total", "results"}
    assert all(p["model"].lower() == mpn.strip().lower() for p in reply["results"])


@pytest.mark.parametrize("mpn", ["ADS1291/2", "ESP-07/12"])
async def test_short_slash_shorthand_is_not_an_alternative(mpn):
    assert annotated_mpn_candidates(mpn) == []
    assert (await server.jlc_get_part(mpn=mpn))["results"] == []


async def test_length_guard_still_precedes_annotation_parsing():
    mpn = ("MAX25206ATPA_VY+,MAX25207ATPA_VY+,MAX25208ATPA_VY+ "
           "(Note the changes to DNP resistors on the schematics)")
    assert len(mpn) == 104
    assert await server.jlc_get_part(mpn=mpn) == {"error": "MPN too long (max 100 characters)"}


@pytest.mark.parametrize("query,candidate", [
    ("AP2112/RT9080-3.3", "AP2112"),
    ("LDO: SPX3819M5-L-3-3", "SPX3819M5-L-3-3"),
    ("TL072 OP AMP", "TL072"),
    ("TL074 OP AMP", "TL074"),
])
async def test_first_candidate_keeps_existing_exact_and_fts_results(query, candidate):
    # These four recorded targets lose to an earlier exact hit or the existing
    # ten-result FTS limit. Do not reorder candidates or substitute vendor/grade.
    reply = await server.jlc_get_part(mpn=query)
    control = await server.jlc_get_part(mpn=candidate)
    assert reply["results"] == control["results"]
    assert reply["match"] == "alternative" and reply["matched_mpn"] == candidate


@pytest.mark.parametrize("query,expected", [
    ("MCP73831-2ACI/OT", []), ("PESD5V0S1UL,118", []), ("B6B-ZR(LF)(SN)", []),
    ("MAX25208ATPA/VY+", []), ("SMBJ48D-M3/I", []),
    ("PCA21125T/Q900/1,1", []),
    ("ESP32-WROVER(_PCB,_IPEX,-xB)_and_ESP-WROOM-32-Universal", []),
    ("TBC if fitted, 10p-22p", []),
    ("STM32F407VGT6/LT8361EMSE", ["STM32F407VGT6", "LT8361EMSE"]),
    ("MCU-STM32F407VGT6", ["STM32F407VGT6"]),
    ("LL4148 L1", ["LL4148"]),
    ("ZZNOEXIST123; LM358P", ["ZZNOEXIST123", "LM358P"]),
])
def test_annotation_boundaries(query, expected):
    assert annotated_mpn_candidates(query) == expected


@pytest.fixture
def catalog():
    connections = []

    def make(rows):
        conn = sqlite3.connect(":memory:")
        connections.append(conn)
        conn.row_factory = sqlite3.Row
        conn.execute("""CREATE TABLE components (
            lcsc TEXT, mpn TEXT, manufacturer TEXT, package TEXT DEFAULT 'SOT-23',
            stock INTEGER DEFAULT 100, price REAL DEFAULT 1, library_type TEXT DEFAULT 'b',
            subcategory_id INTEGER DEFAULT 1, description TEXT DEFAULT '', attributes TEXT DEFAULT '[]')""")
        conn.execute("CREATE INDEX idx_mpn_lower ON components(LOWER(mpn))")
        conn.execute(f"CREATE INDEX idx_mpn_key ON components({MPN_KEY_SQL})")
        conn.execute("CREATE VIRTUAL TABLE components_fts USING fts5(lcsc, mpn, manufacturer, description)")
        for n, (mpn, vendor) in enumerate(rows, 1):
            conn.execute("INSERT INTO components(lcsc, mpn, manufacturer) VALUES (?, ?, ?)", [f"C{n}", mpn, vendor])
        conn.execute("INSERT INTO components_fts SELECT lcsc, mpn, manufacturer, description FROM components")
        return conn

    yield make
    for conn in connections:
        conn.close()


@pytest.mark.parametrize("query,target,wrong_identity,vendor", [
    ("AD8630ARZ-REEL7", "AD8630ARZ", "AD8630YRZ", "Analog Devices"),
    ("LT8364EMSE#TRPBF", "LT8364EMSE#PBF", "LT8364IMSE#PBF", "Analog Devices"),
    ("LM5155QDSSRQ1", "LM5155QDSSTQ1", "LM5155QDSST", "Texas Instruments"),
    ("GRM155R61A104KA01D", "GRM155R61A104KA01J", "GRM155R61A105KA01J", "Murata Electronics"),
    ("RC0603FR-1015KL", "RC0603FR-0715KL", "RC0603FR-0718KL", "YAGEO"),
    ("BSP135H6433XTMA1", "BSP135H6327", "BSP135NH6327", "Infineon Technologies"),
    ("C1210C102KGRACTU", "C1210C102KGRAC7800", "C1210C103KGRAC7800", "KEMET"),
])
def test_packing_preserves_device_and_manufacturer(catalog, query, target, wrong_identity, vendor):
    conn = catalog([(target, vendor), (target, "Other Manufacturer"), (wrong_identity, vendor)])
    info = {}
    result = get_by_mpn(conn, query, {}, match_info=info)
    assert [p["lcsc"] for p in result] == ["C1"]
    assert info == {"match": "packing", "matched_mpn": target}


def test_no_unlisted_generic_suffix_stripping(catalog):
    conn = catalog([("RANDOM123", "Texas Instruments"), ("ABC123", "Analog Devices")])
    assert get_by_mpn(conn, "RANDOM123R", {}) == []
    assert get_by_mpn(conn, "ABC123REEL7", {}) == []


def test_plus_alias_never_falls_through_to_non_plus_or_other_vendor(catalog):
    conn = catalog([("NRF24L01-REEL7", "Nordic Semicon"), ("NRF24L01P-R", "Other Manufacturer")])
    assert get_by_mpn(conn, "NRF24L01+", {}) == []


def test_separator_key_preserves_meaningful_punctuation_and_exact_precedence(catalog):
    conn = catalog([("PART3.3", "Vendor"), ("PART33", "Vendor"), ("PART3_3", "Vendor")])
    info = {"stale": True}
    assert mpn_key("ab-12_ /3.3,+#:") == "AB123.3,+#:"
    assert [p["lcsc"] for p in get_by_mpn(conn, "part_3.3", {}, match_info=info)] == ["C1"]
    assert info == {"match": "separators", "matched_mpn": "PART3.3"}
    queries = []
    conn.set_trace_callback(queries.append)
    assert [p["lcsc"] for p in get_by_mpn(conn, "PART33", {}, match_info=info)] == ["C2"]
    assert info == {}
    assert len(queries) == 1 and "LOWER(mpn)" in queries[0]


def test_normalized_variant_also_uses_separator_key(catalog):
    conn = catalog([("MCP73831T2ACIMC", "Microchip Tech")])
    info = {}
    assert get_by_mpn(conn, "MCP73831-2ACI/MC", {}, match_info=info)[0]["model"] == "MCP73831T2ACIMC"
    assert info["match"] == "packing"


@pytest.mark.parametrize("mpn", ["N/A", "n/a", "NA", "NC", "NF", "NP", "TBD", "DNF", "DNP", " n.a. "])
async def test_placeholder_finds_nothing(mpn):
    # N/A used to list JST ...-N-A connectors; NC, LEDs whose part numbers start with NC.
    reply = await server.jlc_get_part(mpn=mpn)
    assert reply["results"] == []
    assert reply["error"] == f"No JLCPCB parts found for MPN '{mpn}'"
    assert "placeholder" in reply["hint"] and "match" not in reply


async def test_lcsc_code_as_mpn_finds_only_that_part():
    # C2040 also listed resistors whose LCSC codes start with C2040.
    reply = await server.jlc_get_part(mpn="c2040")
    assert [(p["lcsc"], p["model"]) for p in reply["results"]] == [("C2040", "RP2040")]
    assert reply["match"] == "lcsc" and reply["matched_mpn"] == "RP2040"
    assert 'jlc_get_part(lcsc="C2040")' in reply["note"]


@pytest.mark.parametrize("mpn", ["C1815", "C945"])
async def test_part_number_beats_lcsc_code(mpn):
    # 2SC1815's short name is also LCSC C1815, a capacitor: the part number wins.
    reply = await server.jlc_get_part(mpn=mpn)
    assert reply["results"] and all(p["model"] == mpn for p in reply["results"])
    assert "match" not in reply


async def test_missing_lcsc_code_points_to_live_lookup():
    # C3198 listed ten resistors with codes C3198xx; this code is past any assigned one.
    reply = await server.jlc_get_part(mpn="c9999999999")
    assert reply["results"] == []
    assert reply["hint"].startswith("'c9999999999' looks like an LCSC code: "
                                    "jlc_get_part(lcsc=\"C9999999999\")")


def test_lcsc_code_precedence(catalog):
    conn = catalog([("RP2040", "Raspberry Pi"), ("C1", "Vendor"), *[(f"PART{n}", "Vendor") for n in range(3, 13)]])
    info = {}
    assert [p["lcsc"] for p in get_by_mpn(conn, "C1", {}, match_info=info)] == ["C2"]
    assert info == {}
    assert [p["lcsc"] for p in get_by_mpn(conn, "C10", {}, match_info=info)] == ["C10"]
    assert info["match"] == "lcsc"
    # Not in the catalog: full-text search skips other parts' LCSC codes.
    assert get_by_mpn(conn, "C99", {}) == []


@pytest.mark.parametrize("mpn,copy", [
    ("ICM-42688-P", "ICM-42688-P(TOKMAS) (Tokmas)"),
    ("MAX16171ATA/VY+T", "MAX16171ATA/VY(TOKMAS) (Tokmas)"),
])
async def test_other_manufacturers_copy_is_named(mpn, copy):
    reply = await server.jlc_get_part(mpn=mpn)
    if reply.get("results") and "match" not in reply:
        pytest.skip(f"{mpn} itself is stocked now")
    assert reply["match"] == "related"
    assert reply["note"].endswith(f" {copy} is numbered after the original part but made by another "
                                  "manufacturer; check its datasheet before substituting.")


@pytest.mark.parametrize("model,manufacturer,copy", [
    ("ICM-42688-P(TOKMAS)", "Tokmas", True),
    ("SP3485EEN(UMW)", "UMW(Youtai Semiconductor Co., Ltd.)", True),
    ("TP4054(LX)", "lingxingic", True),
    ("AO4407A(ES)", "ElecSuper", True),
    ("SN74LVC1G08DBVR(AT)", "AOTE", True),
    ("B2B-PH-K-S(LF)(SN)", "JST", False),
    ("ABC123(LF)", "Littelfuse", False),
    ("ABC123(BJ)", "TOSHIBA", False),
    ("DF40C-30DP-0.4V(51)", "HRS(Hirose)", False),
    ("ABC123(H)", "DEGSON", False),
    ("ICM-42688-P", "TDK InvenSense", False),
])
def test_maker_suffix_is_the_makers_name_or_initials(model, manufacturer, copy):
    assert is_maker_suffixed({"model": model, "manufacturer": manufacturer}) is copy


def test_maker_suffix_needs_its_own_manufacturer(catalog):
    conn = catalog([("ABC123(TOKMAS)", "Tokmas"), ("ABC123(LF)", "Vendor"), ("ABC123(XBLW)", "XBLW")])
    info = {}
    get_by_mpn(conn, "ABC123", {}, match_info=info)
    assert info["note"].endswith(" ABC123(TOKMAS) (Tokmas), ABC123(XBLW) (XBLW) are numbered after the "
                                 "original part but made by another manufacturer; check their datasheets "
                                 "before substituting.")
