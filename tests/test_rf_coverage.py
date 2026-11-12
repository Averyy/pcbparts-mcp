"""Frequency coverage for RF similar parts in jlc_find_alternatives (2026-10-31 report: BP2G1+, a
1.2-2 GHz splitter, got 5 MHz-1 GHz CATV splitters and a 2.8-3.7 GHz one as similar parts)."""

import json
import sys
from pathlib import Path

import pytest

from conftest import write_catalog_category

from pcbparts_mcp.parsers import parse_freq_bands
from pcbparts_mcp.rf_coverage import band_coverage, check_candidates

GHZ = 1e9


class TestParseFreqBands:
    @pytest.mark.parametrize("value, bands", [
        ("1.2GHz~2GHz", [(1.2 * GHZ, 2 * GHZ)]),
        ("5MHz~1GHz", [(5e6, GHZ)]),
        ("1164~1610MHz", [(1.164 * GHZ, 1.61 * GHZ)]),  # the lower bound takes the upper's unit
        ("1164-1610MHz", [(1.164 * GHZ, 1.61 * GHZ)]),
        ("100Hz~10kHz", [(100, 1e4)]),  # "Hz" on the lower bound is its own unit
        ("0Hz~4GHz", [(0, 4 * GHZ)]),
        ("869MHz~960MHz、1.805GHz~1.99GHz", [(869e6, 960e6), (1.805 * GHZ, 1.99 * GHZ)]),
        ("2.4GHz", [(2.4 * GHZ, 2.4 * GHZ)]),
    ])
    def test_bands(self, value, bands):
        assert parse_freq_bands(value) == pytest.approx(bands)

    @pytest.mark.parametrize("value", ["-", "", "2GHz~1GHz", "1.5GHz~2GHz、wideband"])
    def test_unreadable(self, value):
        assert parse_freq_bands(value) is None

    def test_a_width_is_not_a_band(self):
        assert parse_freq_bands("7.5kHz", points=False) is None
        assert parse_freq_bands("0MHz~2000MHz", points=False) == [(0, 2 * GHZ)]


class TestBandCoverage:
    REQUIRED = [(1.2 * GHZ, 2 * GHZ)]

    @pytest.mark.parametrize("offered, status, share", [
        ("800MHz~2.1GHz", "full", 1.0),        # GP2S+
        ("1.2GHz~2GHz", "full", 1.0),
        ("1.42GHz~1.66GHz", "partial", 0.3),   # SP-2G+
        ("5MHz~1GHz", "none", 0.0),            # TCP-2-10+
        ("2.825GHz~3.7GHz", "none", 0.0),      # SCN-2-35+
        ("1GHz~1.2GHz", "none", 0.0),          # touches the band's edge only
        ("1GHz~1.4GHz、1.8GHz~3GHz", "partial", 0.5),
        ("1GHz~1.6GHz、1.6GHz~3GHz", "full", 1.0),  # adjoining bands cover it together
        ("2.4GHz", "none", 0.0),               # one frequency outside the band
        ("1.5GHz", "unknown", None),           # one frequency inside it says nothing about the width
    ])
    def test_against_bp2g1(self, offered, status, share):
        assert band_coverage(self.REQUIRED, parse_freq_bands(offered)) == (status, share)

    def test_no_band_listed(self):
        assert band_coverage(self.REQUIRED, None) == ("unknown", None)

    def test_each_required_band_counts(self):
        gnss = parse_freq_bands("1.164GHz~1.215GHz、1.55GHz~1.615GHz")
        assert band_coverage(gnss, parse_freq_bands("1.1GHz~1.3GHz")) == ("partial", 0.5)
        assert band_coverage(gnss, parse_freq_bands("1.1GHz~1.7GHz")) == ("full", 1.0)

    def test_single_frequency_original(self):
        assert band_coverage(parse_freq_bands("2.4GHz"), parse_freq_bands("2.4GHz~2.4835GHz")) == ("full", 1.0)
        assert band_coverage(parse_freq_bands("2.4GHz"), parse_freq_bands("433MHz")) == ("none", 0.0)


def _part(lcsc, band=None, subcategory="RF Power Splitters / Combiners", attribute="Frequency Range"):
    return {"lcsc": lcsc, "subcategory": subcategory, "specs": {attribute: band} if band else {}}


class TestCheckCandidates:
    def test_orders_and_drops(self):
        candidates = [_part("C1", "5MHz~1GHz"), _part("C2", "1.42GHz~1.66GHz"), _part("C3"),
                      _part("C4", "800MHz~2.1GHz"), _part("C5", "1.3GHz~2GHz")]
        summary = check_candidates(_part("C0", "1.2GHz~2GHz"), candidates)
        assert [p["lcsc"] for p in candidates] == ["C4", "C5", "C2", "C3"]
        assert [p["frequency_coverage"] for p in candidates] == [
            {"status": "full", "share": 1.0}, {"status": "partial", "share": 0.88},
            {"status": "partial", "share": 0.3}, {"status": "unknown"},
        ]
        assert {k: summary[k] for k in ("required", "full", "partial", "unknown", "left_out_no_overlap")} == {
            "required": "1.2GHz~2GHz", "full": 1, "partial": 2, "unknown": 1, "left_out_no_overlap": 1,
        }

    def test_filters_list_absolute_bandwidth(self):
        candidates = [_part("C1", "2.4GHz~2.5GHz", "RF Filters", "Absolute Bandwidth")]
        check_candidates(_part("C0", "2.4GHz~2.5GHz", "RF Filters"), candidates)
        assert candidates[0]["frequency_coverage"]["status"] == "full"

    def test_not_rf(self):
        candidates = [_part("C1", "5MHz~1GHz", "MEMS Microphones")]
        assert check_candidates(_part("C0", "1.2GHz~2GHz", "MEMS Microphones"), candidates) is None
        assert "frequency_coverage" not in candidates[0]

    def test_original_without_a_band(self):
        candidates = [_part("C1", "5MHz~1GHz")]
        summary = check_candidates(_part("C0"), candidates)
        assert summary["required"] is None
        assert [p["lcsc"] for p in candidates] == ["C1"]


SPLITTERS = 2559


def _row(lcsc, stock, band, maker="Mini-Circuits", lib="e"):
    return {"l": lcsc, "m": f"MPN-{lcsc}", "f": maker, "p": "SMD", "s": stock, "t": lib, "c": SPLITTERS,
            "$": 1.0, "d": lcsc, "a": [["Frequency Range", band]] if band else []}


@pytest.fixture
def splitter_db(tmp_path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from build_database import build_database
    from pcbparts_mcp.db import ComponentDatabase

    rows = [
        _row("C7459223", 90, "1.2GHz~2GHz"),                      # BP2G1+, the original
        _row("C1001", 9000, "5MHz~1GHz"),                         # TCP-2-10+: most stock, wrong band
        _row("C1002", 8000, "2.825GHz~3.7GHz"),
        _row("C3155018", 5000, "800MHz~2.1GHz"),                  # GP2S+
        _row("C52139901", 3974, "1.1GHz~1.7GHz", maker="MEGSINE"),
        _row("C1003", 3000, None, maker="MEGSINE"),               # no band listed
        _row("C1004", 100, "1.2GHz~2GHz", maker="MEGSINE"),
    ]
    write_catalog_category(tmp_path, "rf", rows)
    (tmp_path / "subcategories.json").write_text(json.dumps(
        {str(SPLITTERS): {"name": "RF Power Splitters / Combiners", "category_id": 9, "category_name": "RF and Wireless"}}))
    build_database(tmp_path, tmp_path / "components.db", verbose=False)
    db = ComponentDatabase(db_path=tmp_path / "components.db", data_dir=tmp_path)
    yield db
    db.close()


async def test_find_alternatives_checks_the_band(splitter_db, monkeypatch):
    from pcbparts_mcp.client import JLCPCBClient

    client = JLCPCBClient()
    client.set_subcategory_parts(splitter_db.subcategory_parts)
    original = {"lcsc": "C7459223", "model": "BP2G1+", "manufacturer": "Mini-Circuits", "package": "SMD",
                "subcategory": "RF Power Splitters / Combiners", "library_type": "extended", "stock": 90,
                "price": 3.0, "specs": {"Frequency Range": "1.2GHz~2GHz"}}
    live = [{"lcsc": "C1001", "manufacturer": "Mini-Circuits", "package": "SMD", "library_type": "extended",
             "stock": 9000, "price": 1.0, "specs": {"Frequency Range": "5MHz~1GHz"}}]
    searched = []

    async def get_part(lcsc):
        return json.loads(json.dumps(original))

    async def search(**kwargs):
        searched.append(kwargs)
        return {"results": [dict(p) for p in live]}

    async def ensure_categories():
        return None

    monkeypatch.setattr(client, "get_part", get_part)
    monkeypatch.setattr(client, "search", search)
    monkeypatch.setattr(client, "_ensure_categories", ensure_categories)
    monkeypatch.setattr(client, "get_subcategory_id_by_name", lambda name: SPLITTERS)

    result = await client.find_alternatives("C7459223", limit=10)
    similar = result["similar_parts"]
    # Every maker's parts in the subcategory, covering parts first; no-overlap parts left out
    assert [p["lcsc"] for p in similar] == ["C3155018", "C1004", "C52139901", "C1003"]
    assert [p["frequency_coverage"]["status"] for p in similar] == ["full", "full", "partial", "unknown"]
    check = result["summary"]["frequency_check"]
    assert check["required"] == "1.2GHz~2GHz"
    assert check["left_out_no_overlap"] == 2
    assert result["alternatives"] == []

    # An explicit library type still limits the database parts
    result = await client.find_alternatives("C7459223", library_type="basic", limit=10)
    assert result["similar_parts"] == []
