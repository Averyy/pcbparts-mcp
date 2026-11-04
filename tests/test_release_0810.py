"""0.8.10: LCSC's datasheet and specs when JLCPCB lists none, and the inductor DCR / Current Rating note
(design-session reports, 2026-11-03)."""

import sys
from pathlib import Path

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.client import JLCPCBClient, apply_lcsc_fallback, catalog_gap_note

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline  # noqa: E402

# LCSC's product-detail reply for YY-0807RGBJ26-07-FJ (trimmed): JLCPCB lists neither its datasheet nor specs
LCSC_PRODUCT = {
    "productCode": "C54796803",
    "pdfUrl": "https://datasheet.lcsc.com/datasheet/pdf/f9afa0e15f6569ed1e35edd063d6a18f.pdf?productCode=C54796803",
    "paramVOList": [{"paramNameEn": "Fall Time", "paramValueEn": "400ns"},
                    {"paramNameEn": "Rise Time", "paramValueEn": "400ns"},
                    {"paramNameEn": "Color", "paramValueEn": "-"}],
}


@pytest.fixture(autouse=True)
async def no_network():
    # Async so the event loop exists first: on Windows its socket pair is built with connect()
    with offline():
        yield


class TestLcscFallback:
    def test_fills_datasheet_and_specs(self):
        result = {"datasheet": None, "specs": {}, "datasheet_note": "JLCPCB has no datasheet PDF for this part; ..."}
        apply_lcsc_fallback(result, LCSC_PRODUCT)
        assert result["datasheet_pdf"] == LCSC_PRODUCT["pdfUrl"]
        assert result["datasheet"] == "https://www.lcsc.com/datasheet/C54796803.pdf"
        assert result["datasheet_note"] == "JLCPCB has no datasheet for this part; datasheet_pdf is LCSC's copy."
        assert result["specs"] == {"Fall Time": "400ns", "Rise Time": "400ns"}
        assert "spec filters still leave it out" in result["specs_note"]

    def test_keeps_jlcpcb_data(self):
        result = {"datasheet": "https://www.lcsc.com/datasheet/x.pdf", "datasheet_pdf": "https://jlcpcb.example/x.pdf",
                  "specs": {"Resistance": "10kΩ"}}
        apply_lcsc_fallback(result, LCSC_PRODUCT)
        assert result["datasheet_pdf"] == "https://jlcpcb.example/x.pdf" and result["specs"] == {"Resistance": "10kΩ"}
        result = {"maker_datasheet": "https://www.ti.com/lit/ds/symlink/tps61023.pdf", "specs": {}}
        apply_lcsc_fallback(result, LCSC_PRODUCT)
        assert "datasheet_pdf" not in result

    def test_nothing_from_lcsc(self):
        result = {"datasheet": None, "specs": {}, "datasheet_note": "JLCPCB has no datasheet PDF for this part; ..."}
        apply_lcsc_fallback(result, None)
        apply_lcsc_fallback(result, {"productCode": "C1", "pdfUrl": None, "paramVOList": []})
        assert result == {"datasheet": None, "specs": {}, "datasheet_note": "JLCPCB has no datasheet PDF for this part; ..."}

    @pytest.mark.parametrize("item_extra, asks_lcsc", [
        ({}, True),  # no datasheet, no specs
        ({"dataManualOfficialLink": "https://www.ti.com/lit/ds/symlink/tps61023.pdf",
          "attributes": [{"attribute_name_en": "Resistance", "attribute_value_name": "10kΩ"}]}, False),
    ])
    async def test_get_part_asks_lcsc_only_when_needed(self, monkeypatch, item_extra, asks_lcsc):
        client = JLCPCBClient()
        item = {"componentCode": "C54796803", "componentPrices": [], "firstSortName": "LED Indication - Discrete",
                "componentModelEn": "YY-0807RGBJ26-07-FJ", **item_extra}
        asked = []

        async def request(url, params):
            return {"data": {"componentPageInfo": {"list": [item]}}}

        async def lcsc_product(lcsc):
            asked.append(lcsc)
            return LCSC_PRODUCT

        async def footprint(lcsc):
            return {"has_easyeda_footprint": None}

        monkeypatch.setattr(client, "_request", request)
        monkeypatch.setattr(client, "lcsc_product", lcsc_product)
        monkeypatch.setattr(client, "check_easyeda_footprint", footprint)
        result = await client.get_part("C54796803")
        assert asked == (["C54796803"] if asks_lcsc else [])
        assert (result.get("datasheet_pdf") == LCSC_PRODUCT["pdfUrl"]) is asks_lcsc
        assert bool(result.get("maker_datasheet")) is not asks_lcsc


class TestInductorNote:
    def test_isat_and_dcr(self):
        note = catalog_gap_note("Power Inductors", {"Current - Saturation(Isat)": "8.5A", "DC Resistance(DCR)": "27mΩ",
                                                    "Current Rating": "5A"})
        assert "inductance drop" in note and "27 mOhm, its maximum; 22 typical" in note and "Irms" in note

    def test_dcr_without_isat(self):
        assert catalog_gap_note("Inductors (SMD)", {"DC Resistance(DCR)": "0.2Ω"}).startswith("DCR is the typical")

    def test_not_for_ferrite_beads(self):
        assert catalog_gap_note("Ferrite Beads", {"DC Resistance(DCR)": "0.1Ω"}) is None

    async def test_dcr_sort_says_so(self):
        result = await server.jlc_search(query="10uH power inductor", sort_spec="DCR", limit=5)
        assert "typical DCR on some inductors and the maximum on others" in result["sort"]["note"]


class TestLcscLinkStays:
    def test_reply_keeps_lcsc_link(self, monkeypatch):
        from types import SimpleNamespace
        request = SimpleNamespace(headers={"host": "pcbparts.dev"}, url=SimpleNamespace(scheme="https"))
        monkeypatch.setattr(server, "get_http_request", lambda: request)
        part = {"lcsc": "C54796803", "datasheet_pdf": LCSC_PRODUCT["pdfUrl"]}
        # The /mcp/datasheet redirect re-signs JLCPCB's copy, which this part doesn't have
        assert server._short_datasheet_link(part) == part
