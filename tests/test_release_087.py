"""0.8.7: MOSFET listings mix typical and maximum RDS(on)/Vgs(th) (design-session report, 2026-11-03), and
gate charge, which 0.8.5 refused as unlisted though 30,000 MOSFETs list it as "Gate Charge(Qg)"."""

import sys
from pathlib import Path

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.client import JLCPCBClient, catalog_gap_note
from pcbparts_mcp.parsers import parse_capacitance
from pcbparts_mcp.search.spec_sort import SpecSort
from pcbparts_mcp.smart_parser import parse_smart_query

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline  # noqa: E402


@pytest.fixture(autouse=True)
async def no_network():
    # Async so the event loop exists first: on Windows its socket pair is built with connect()
    with offline():
        yield


def _ordered(values):
    listed = [v for v in values if v is not None]
    return values[:len(listed)] == listed and listed == sorted(listed)


class TestMosfetNote:
    def test_note(self):
        note = catalog_gap_note("MOSFETs", {"RDS(on)": "47mΩ@10V、60mΩ@4.5V、85mΩ@2.5V"})
        assert "typical" in note and "max columns" in note and "IGSS" in note
        assert catalog_gap_note("MOSFETs", {"Gate Threshold Voltage (Vgs(th))": "900mV"}) == note

    @pytest.mark.parametrize("subcategory, specs", [("MOSFETs", {"Type": "P-Channel"}),
                                                    ("Bipolar (BJT)", {"RDS(on)": "1Ω"})])
    def test_no_note(self, subcategory, specs):
        assert catalog_gap_note(subcategory, specs) is None

    def test_in_get_part(self):
        item = {"componentCode": "C15127", "componentPrices": [], "firstSortName": "MOSFETs",
                "attributes": [{"attribute_name_en": "RDS(on)", "attribute_value_name": "47mΩ@10V、60mΩ@4.5V"}]}
        assert "typical" in JLCPCBClient._transform_part(JLCPCBClient(), item, slim=False)["specs_note"]

    async def test_rds_on_sorts_say_so(self):
        for spec in ("RDS(on)", "RDS(on)@4.5V"):
            result = await server.jlc_search(query="p-channel mosfet SOT-23", sort_spec=spec, limit=5)
            assert "typical figure on some parts and the maximum on others" in result["sort"]["note"]


class TestGateCharge:
    def test_parse(self):
        sort = SpecSort.parse("Qg")
        assert sort.spec.label == "Gate Charge" and sort.spec.column == "qg_nc"
        assert parse_smart_query("lowest gate charge n-channel mosfet").spec_sort.spec.label == "Gate Charge"

    async def test_sorted(self):
        result = await server.jlc_search(query="n-channel mosfet SOT-23", sort_spec="Gate Charge", limit=50)
        assert "error" not in result, result.get("error")
        values = [parse_capacitance(p["sort_value"].split("@")[0].split("、")[0]) if p["sort_value"] else None
                  for p in result["results"]]
        assert values[0] is not None and _ordered(values)
        assert "listed at different gate voltages" in result["sort"]["note"]
