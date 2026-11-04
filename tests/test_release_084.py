"""0.8.4 from the design-session idea reports (2026-11-02/03). Searches run on the local catalog and
check every result rather than one part number, so the daily data can change under them."""

import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.alternatives import build_response, build_unsupported_response, score_alternative
from pcbparts_mcp.client import JLCPCBClient, catalog_gap_note
from pcbparts_mcp.design_rules import get_design_rules
from pcbparts_mcp.pinout import parse_easyeda_footprint
from pcbparts_mcp.search.query_builder import build_pcba_type_clause
from pcbparts_mcp.search.result import pcba_type_from_item, row_to_dict
from pcbparts_mcp.search.spec_filter import dropout_at_load, dropout_load_filter
from pcbparts_mcp.smart_parser import parse_smart_query

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import pcba_columns  # noqa: E402
from scrape_components import transform_part  # noqa: E402
from search_baseline import offline  # noqa: E402


@pytest.fixture(autouse=True)
async def no_network():
    # Async so the event loop exists first: on Windows its socket pair is built with connect()
    with offline():
        yield


async def search(query: str | None = None, **kwargs):
    result = await server.jlc_search(query=query, limit=kwargs.pop("limit", 50), **kwargs)
    assert "error" not in result, result.get("error")
    return result


def _items(value: str | None) -> set[str]:
    return {item.strip().lower() for item in (value or "").split("、")}


class TestNoFeeAlternativesNameExtended:
    """jlc_find_alternatives(C13564, no_fee): alternatives [] and extended_count 25, nothing named."""

    ORIGINAL = {"lcsc": "C13564", "model": "NCP18XH103F03RB", "package": "0603", "library_type": "extended",
                "specs": {"Resistance @ 25℃": "10kΩ"}}
    EXAMPLES = [{"lcsc": "C440252", "model": "NCU18XH103F60RB", "manufacturer": "Murata", "package": "0603",
                 "stock": 29372, "price": 0.05}]

    def test_supported(self):
        response = build_response(self.ORIGINAL, [], "NTC Thermistors", "Resistance @ 25℃", "10kΩ", 5,
                                  library_type="no_fee", extended_count=23, extended_examples=self.EXAMPLES)
        assert response["summary"]["extended_examples"] == self.EXAMPLES
        message = response["summary"]["message"]
        assert "C440252 (NCU18XH103F60RB)" in message and 'library_type="extended" to list all 23' in message

    def test_unsupported(self):
        response = build_unsupported_response(self.ORIGINAL, [], "Coaxial Connectors (RF)", None, 5,
                                              extended_count=25, extended_examples=self.EXAMPLES)
        assert response["summary"]["extended_count"] == 25 and response["summary"]["extended_examples"]
        assert "C440252" in response["summary"]["message"]

    def test_nothing_added_without_examples(self):
        response = build_response(self.ORIGINAL, [], "NTC Thermistors", "Resistance @ 25℃", "10kΩ", 5,
                                  library_type="no_fee", extended_count=0)
        assert "extended_examples" not in response["summary"]
        assert "extended_examples" not in build_unsupported_response(self.ORIGINAL, [], "x", None, 5)["summary"]

    def test_unchecked_footprint_isnt_scored_as_none(self):
        _, unchecked = score_alternative({"lcsc": "C1", "stock": 100}, self.ORIGINAL, None)
        _, absent = score_alternative({"lcsc": "C1", "stock": 100, "has_easyeda_footprint": False}, self.ORIGINAL, None)
        _, present = score_alternative({"lcsc": "C1", "stock": 100, "has_easyeda_footprint": True}, self.ORIGINAL, None)
        assert "easyeda" not in unchecked and absent["easyeda"] == 0 and present["easyeda"] == 20

    async def test_known_footprints_added_without_a_request(self):
        client = JLCPCBClient()
        client.set_easyeda_seed(lambda lcsc: None)
        answers = {"C440252": {"has_easyeda_footprint": True}}

        async def stored(lcsc, now):
            return answers.get(lcsc)
        client._stored_footprint = stored
        response = {"alternatives": [{"lcsc": "C440252"}, {"lcsc": "C9"}],
                    "summary": {"extended_examples": [{"lcsc": "C440252"}]}}
        await client._add_known_footprints(response)
        assert response["alternatives"] == [{"lcsc": "C440252", "has_easyeda_footprint": True}, {"lcsc": "C9"}]
        assert response["summary"]["extended_examples"][0]["has_easyeda_footprint"] is True


class TestSchmittLogic:
    """A no-fee "schmitt trigger logic" search found nothing; the basic 74HC14D is an inverter."""

    @pytest.mark.parametrize("query, subcategory, group", [
        ("schmitt trigger logic", "inverters", True), ("schmitt trigger", "inverters", True),
        ("schmitt trigger IC", "inverters", True), ("hex schmitt inverter", "inverters", False),
        ("schmitt buffer", "buffers, drivers, receivers, transceivers", False)])
    def test_parse(self, query, subcategory, group):
        parsed = parse_smart_query(query)
        assert parsed.subcategory == subcategory and bool(parsed.subcategories) is group
        assert {(f.name, f.value) for f in parsed.spec_filters} == {
            ("Input type", "Schmitt trigger"), ("Input type", "施密特触发器")}
        assert "schmitt" not in parsed.remaining_text.lower()

    @pytest.mark.parametrize("query, subcategory", [
        ("quad NAND schmitt", "logic gates"), ("schmitt trigger logic gate", "logic gates"),
        ("schmitt trigger comparator", "comparators")])
    def test_other_part_types_unchanged(self, query, subcategory):
        assert parse_smart_query(query).subcategory == subcategory

    async def test_no_fee_spans_the_logic_subcategories(self):
        result = await search("schmitt trigger logic", library_type="no_fee")
        assert result["total"] > 0
        for part in result["results"]:
            assert part["subcategory"] in ("Inverters", "Logic Gates", "Buffers, Drivers, Receivers, Transceivers")
            assert "schmitt trigger" in _items(part["specs"].get("Input Type") or part["specs"].get("Input type"))
            assert part["library_type"] in ("basic", "preferred")

    async def test_every_subcategory_searched(self):
        result = await search("schmitt trigger", limit=100)
        assert {"Inverters", "Logic Gates", "Buffers, Drivers, Receivers, Transceivers"} >= {
            p["subcategory"] for p in result["results"]}
        assert len(result["filters_applied"]["subcategory_ids"]) == 3


class TestCatalogGapNotes:
    @pytest.mark.parametrize("subcategory, specs, words", [
        ("Power Inductors", {"Current - Saturation(Isat)": "5.4A"}, "inductance drop"),
        ("Multilayer Ceramic Capacitors MLCC - SMD/SMT", {"Temperature Coefficient": "X5R"}, "DC bias"),
        ("Multilayer Ceramic Capacitors MLCC - SMD/SMT", {"Temperature Coefficient": "X7R"}, "DC bias"),
        ("RF Cables", {"Input/Output": "IPEX to SMA"}, "bulkhead")])
    def test_notes(self, subcategory, specs, words):
        assert words in catalog_gap_note(subcategory, specs)

    @pytest.mark.parametrize("subcategory, specs", [
        ("Multilayer Ceramic Capacitors MLCC - SMD/SMT", {"Temperature Coefficient": "C0G"}),
        ("Power Inductors", {"Current - Saturation(Isat)": "-"}), ("MOSFETs", {"Type": "N-Channel"})])
    def test_no_note(self, subcategory, specs):
        assert catalog_gap_note(subcategory, specs) is None

    def test_in_get_part(self):
        item = {"componentCode": "C15008", "componentPrices": [], "firstSortName": "Multilayer Ceramic Capacitors MLCC - SMD/SMT",
                "attributes": [{"attribute_name_en": "Temperature Coefficient", "attribute_value_name": "X5R"}]}
        assert "DC bias" in JLCPCBClient._transform_part(JLCPCBClient(), item, slim=False)["specs_note"]


class TestPcbaType:
    """A design was costed on Economic assembly for two days before its Standard-only MCU module was
    found on the JLCPCB part page. componentProductType matched the page on 11 parts (0 = Economic and
    Standard, 2 = Standard only) and on a whole subcategory's ratio."""

    @pytest.mark.parametrize("product_type, expected", [(0, "economic"), ("0", "economic"), (2, "standard_only"),
                                                        (1, None), (None, None), ("x", None)])
    def test_live_item(self, product_type, expected):
        assert pcba_type_from_item({"componentProductType": product_type}) == expected

    def test_scrape_keeps_it(self):
        item = {"componentCode": "C3013945", "componentProductType": 2, "componentLibraryType": "expand",
                "dataManualUrl": "https://x"}
        part = transform_part(item, 3205)
        assert part["x"] == 2 and "n" not in part
        assert pcba_columns(part) == ("s", 0)
        assert pcba_columns(transform_part({"componentProductType": 0}, 1)) == ("e", 1)  # no datasheet link

    def test_old_data_claims_nothing(self):
        assert pcba_columns({"l": "C1", "t": "b"}) == (None, None)

    def test_row(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE TABLE c (lcsc, mpn, manufacturer, package, stock, price, library_type, subcategory_id, "
                     "description, attributes, pcba_type, no_datasheet)")
        conn.execute("INSERT INTO c VALUES ('C1','M','F','0603',10,0.1,'e',1,'d','[]','s',1)")
        conn.execute("INSERT INTO c VALUES ('C2','M','F','0603',10,0.1,'e',1,'d','[]',NULL,NULL)")
        rows = [row_to_dict(r, {}) for r in conn.execute("SELECT * FROM c ORDER BY lcsc")]
        assert rows[0]["pcba_type"] == "standard_only" and rows[0]["no_datasheet"] is True
        assert "pcba_type" not in rows[1] and "no_datasheet" not in rows[1]

    def test_clause(self):
        assert build_pcba_type_clause("economic") == "AND pcba_type = 'e'"
        assert build_pcba_type_clause("standard_only") == "AND pcba_type = 's'"
        assert build_pcba_type_clause(None) == ""

    def test_get_part(self):
        item = {"componentCode": "C3013945", "componentPrices": [], "attributes": [], "componentProductType": 2}
        assert JLCPCBClient._transform_part(JLCPCBClient(), item)["pcba_type"] == "standard_only"

    async def test_bad_value(self):
        result = await server.jlc_search(query="ESP32-S3 module", pcba_type="cheap")
        assert result["valid_values"] == ["economic", "standard_only"]

    async def test_not_loaded_says_so(self, monkeypatch):
        monkeypatch.setattr(server.get_db(), "pcba_type_loaded", lambda: False)
        result = await server.jlc_search(query="ESP32-S3 module", pcba_type="economic")
        assert "doesn't have PCBA types yet" in result["error"]

    @pytest.mark.parametrize("value, expected", [("economic", "economic"), ("Economic and Standard", "economic"),
                                                 ("standard-only", "standard_only")])
    async def test_filter(self, monkeypatch, value, expected):
        monkeypatch.setattr(server.get_db(), "pcba_type_loaded", lambda: True)
        result = await search("ESP32-S3 module", pcba_type=value)
        assert result["filters_applied"]["pcba_type"] == expected
        assert all(p.get("pcba_type") == expected for p in result["results"])


_SWITCH_FOOTPRINT = {"title": "SW-TH_SK13D07VG4", "dataStr": {
    "head": {"x": 3990.713, "y": 2995.5, "c_para": {"package": "SW-TH_SK13D07VG4", "link": "https://item.szlcsc.com/2774924.html"}},
    "shape": [
        "PAD~OVAL~3966.5~2995.5~5.5118~8.6614~11~~7~1.5748~3966.5 2993.9252 3966.5 2997.0748~0~gge33~6.2992~3966.5004 2997.0748 3966.5004 2993.9252~Y~0~0~0.2~",
        "PAD~OVAL~4014.926~2995.5~5.5118~8.6614~11~~6~1.5748~4014.926 2993.9252 4014.926 2997.0748~0~gge34~6.2992~4014.9256 2997.0748 4014.9256 2993.9252~Y~0~0~0.2~",
        "PAD~ELLIPSE~4006.461~2995.5~6~6~11~~5~1.8~~0~gge35~0~~Y~0~0~0.2~4006.461,2995.5",
        "PAD~ELLIPSE~3998.587~2995.5~6~6~11~~4~1.8~~0~gge36~0~~Y~0~0~0.2~3998.587,2995.5",
        "PAD~ELLIPSE~3990.713~2995.5~6~6~11~~3~1.8~~0~gge37~0~~Y~0~0~0.2~3990.713,2995.5",
        "PAD~ELLIPSE~3974.965~2995.5~6~6~11~~1~1.8~~0~gge38~0~~Y~0~0~0.2~3974.965,2995.5",
        "TRACK~1~3~~3960 2990 4020 2990~gge40~0",
    ]}}


class TestFootprintPads:
    """SK13D07VG4 (C2681581): pins 1, 3-7 with numbers only; the datasheet puts the contacts at
    0/4/6/8 mm plus two frame legs, which only pad positions show."""

    def test_switch(self):
        footprint = parse_easyeda_footprint(_SWITCH_FOOTPRINT)
        assert footprint["name"] == "SW-TH_SK13D07VG4" and footprint["pad_count"] == 6
        assert footprint["source_link"] == "https://item.szlcsc.com/2774924.html"
        x = {p["number"]: p["x"] for p in footprint["pads"]}
        assert [round(x[n] - x["1"], 2) for n in ("3", "4", "5")] == [4.0, 6.0, 8.0]
        legs = [p for p in footprint["pads"] if p["number"] in ("6", "7")]
        assert all(p["hole"] == 0.8 and p["slot_length"] == 1.6 and p["size"] == [1.4, 2.2] for p in legs)
        assert footprint["pitch"] == 2.0 and all(p["layer"] == "through_hole" for p in footprint["pads"])

    def test_rotation_and_size_groups(self):
        data = {"dataStr": {"head": {"x": 0, "y": 0}, "shape": [
            "PAD~RECT~0~0~4~2~1~~1~0~~90~g1~0~~Y~0",
            "PAD~RECT~10~0~2~4~1~~2~0~~0~g2~0~~Y~0",
            "PAD~RECT~20~0~2~4~1~~3~0~~0~g3~0~~Y~0"]}}
        footprint = parse_easyeda_footprint(data)
        assert [p["size"] for p in footprint["pads"]] == [[0.508, 1.016]] * 3
        assert footprint["pad_sizes"] == [{"size": "0.508x1.016 mm rect", "count": 3}]
        assert footprint["pitch"] == 2.54 and footprint["pads"][0]["layer"] == "top"

    def test_no_pads(self):
        assert parse_easyeda_footprint({"dataStr": {"head": {}, "shape": ["TRACK~1~3~~0 0 1 1~g~0"]}}) is None

    @pytest.fixture
    def pinout_client(self, monkeypatch):
        symbol = {"dataStr": {"shape": [
            f"P~show~0~{n}~100~100~180~gge{n}~0^^100~100^^M100,100h10~#0000FF^^1~110~105~0~{n}~start~~~#0000FF"
            f"^^1~100~100~0~{n}~end~~~#0000FF" for n in (1, 3, 4, 5, 6, 7)]}, "verify": True}
        components = {"a" * 32: symbol, "b" * 32: _SWITCH_FOOTPRINT}

        async def get_part(lcsc):
            return {"lcsc": lcsc, "model": "SK13D07VG4", "has_easyeda_footprint": True,
                    "easyeda_symbol_uuid": "a" * 32, "easyeda_footprint_uuid": "b" * 32, "subcategory": "Slide Switches"}

        async def get_easyeda_component(uuid):
            return components[uuid]
        monkeypatch.setattr(server, "_client", SimpleNamespace(get_part=get_part, get_easyeda_component=get_easyeda_component))

    async def test_pinout_footprint(self, pinout_client):
        result = await server.jlc_get_pinout(lcsc="C2681581", footprint=True)
        assert result["footprint"]["pad_count"] == 6 and "footprint=true" not in result["note"]

    async def test_pinout_points_to_it(self, pinout_client):
        result = await server.jlc_get_pinout(lcsc="C2681581")
        assert "footprint" not in result and "footprint=true adds the pad positions" in result["note"]
        # 0.8.12: a client that loaded the tools before 0.8.4 has no footprint argument (2026-11-04 report)
        assert "reconnect to the server to load it" in result["note"]

    async def test_uuid_only(self, pinout_client):
        result = await server.jlc_get_pinout(uuid="a" * 32, footprint=True)
        assert result["footprint_error"] == "Give lcsc to get the footprint"


class TestDropoutAtLoad:
    """"dropout <= 0.3 V at 300-500 mA" couldn't be asked: LDOs list dropout at their own test current."""

    @pytest.mark.parametrize("value, expected", [
        ("0.3V@500mA", (0.3, 0.5)), ("300mV @ 0.5A", (0.3, 0.5)), ("0.3V@(500mA)", (0.3, 0.5)),
        ("300mV at 500mA", (0.3, 0.5)), ("0.3V", None), ("0.3V@", None)])
    def test_filter_value(self, value, expected):
        parsed = dropout_load_filter(value)
        assert parsed == expected if expected is None else parsed == pytest.approx(expected)

    @pytest.mark.parametrize("listed, load, volts, scaled", [
        ("238mV@(500mA)", 0.5, 0.238, False),
        ("110mV@(1A)", 0.5, 0.11, False),            # listed above the load bounds it
        ("180mV@(300mA)", 0.5, 0.3, True),           # scaled up linearly
        ("90mV@(100mA)、230mV@(200mA)", 0.15, 0.23, False),
        ("90mV@(100mA)、230mV@(200mA)", 0.4, 0.46, True),
        ("350mV@200mA", 0.2, 0.35, False)])
    def test_dropout_at_load(self, listed, load, volts, scaled):
        found = dropout_at_load(listed, load)
        assert found[0] == pytest.approx(volts) and found[2] is scaled

    @pytest.mark.parametrize("listed", ["1.7V", "-", "", None])
    def test_no_test_current(self, listed):
        assert dropout_at_load(listed, 0.5) is None

    async def test_search(self):
        result = await search("3.3V LDO", spec_filters=[{"name": "Dropout", "op": "<=", "value": "0.3V@500mA"}], limit=100)
        assert result["total"] > 0
        for part in result["results"]:
            volts, _, _ = dropout_at_load(part["specs"]["Voltage Dropout"], 0.5)
            assert volts <= 0.3 + 1e-9 and part["dropout_at_load"]["load"] == "500mA"
            current = part["specs"].get("Output Current")
            if current and current != "-":
                from pcbparts_mcp.parsers import parse_current
                assert parse_current(current) >= 0.5

    async def test_plain_value_unchanged(self):
        result = await search("3.3V LDO", spec_filters=[{"name": "Voltage Dropout", "op": "<=", "value": "0.3V"}], limit=5)
        assert result["total"] > 0 and all("dropout_at_load" not in p for p in result["results"])


class TestDesignRules:
    def test_efuse_supply(self):
        content = get_design_rules("esp32")["content"]
        assert "VDD3P3_CPU on S3/C3, VDDPST2 on C6" in content and "<= 3.3 V" in content

    def test_reset_rc_depends_on_the_ramp(self):
        content = get_design_rules("esp32")["content"]
        assert "Ensures 50 us minimum stabilization time" not in content
        assert "tau >= 1.65 * ((2.8 V / V_final) * T_ramp + 50 us)" in content

    def test_jlcpcb_numbers_and_stackups(self):
        content = get_design_rules("dfm")["content"]
        assert "JLC04161H-7628" in content and "0.2104 mm, Er 4.4" in content and "0.0994 mm, Er 4.1" in content
        assert "0.30 mm hole / 0.45 mm pad" in content

    @pytest.mark.parametrize("topic, key", [("jlc stackup", "guides/dfm"), ("efuse", "mcus/esp32")])
    def test_topics(self, topic, key):
        assert get_design_rules(topic)["matched_files"] == [key]
