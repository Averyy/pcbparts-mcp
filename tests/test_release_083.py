"""0.8.3 fixes from design-session reports that arrived during 0.8.2 (2026-11-02). Searches run on
the local catalog and check every result rather than one part number, so the daily data can change
under them."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.search.spec_filter import connector_orientation
from pcbparts_mcp.smart_parser import parse_smart_query

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
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


def _filters(parsed) -> list[tuple[str, str]]:
    return [(f.name, f.value) for f in parsed.spec_filters]


class TestPowerMux:
    """"power mux" returned signal multiplexers; LCSC files power muxes (TPS2121) as ORing controllers."""

    @pytest.mark.parametrize("query", ["power mux", "power multiplexer", "USB power path switch", "power selector"])
    async def test_power_path_parts(self, query):
        result = await search(query)
        assert result["total"] > 0
        assert {p["subcategory"] for p in result["results"]} <= {"ORing Controllers", "Power Distribution Switches"}

    async def test_signal_mux_unchanged(self):
        result = await search("mux 8 channel")
        assert all("Multiplexers" in p["subcategory"] for p in result["results"])


class TestConnectorOrientation:
    @pytest.mark.parametrize("value, orientation", [
        ("Surface Mount, Right Angle", "right angle"), ("Right-Angle", "right angle"), ("Side insertion", "right angle"),
        ("Surface Mount,Vertical", "vertical"), ("Straight", "vertical"), ("Through Hole", None), ("-", None)])
    def test_values(self, value, orientation):
        assert connector_orientation(value) == orientation

    async def test_right_angle_first_when_the_words_are_dropped(self):
        # JST's descriptions don't say right angle: the words were dropped and a vertical part led
        result = await search("JST ZH 1.5mm 2 pin SMD right angle wire to board header")
        kinds = [connector_orientation(p["specs"].get("Mounting Type")) for p in result["results"]]
        right = kinds.count("right angle")
        assert right and kinds[:right] == ["right angle"] * right

    async def test_words_still_narrow_where_descriptions_have_them(self):
        result = await search("2.54mm pin header 1x4 right angle")
        assert result["total"] > 0 and not result.get("relaxed")
        assert all(connector_orientation(p["specs"].get("Mounting Type")) == "right angle" for p in result["results"])


class TestBarePitch:
    """"female header 2.54" read the 2 as a pin count and dropped ".54"."""

    @pytest.mark.parametrize("query, expected", [
        ("female header 2.54", [("Pitch", "2.54mm")]),
        ("pin header 2.54 1x4", [("Pin Structure", "1x4P"), ("Pitch", "2.54mm")]),
        ("header 1.27 2x5", [("Pin Structure", "2x5P"), ("Pitch", "1.27mm")]),
        ("pin header 2.54 8", [("Pitch", "2.54mm"), ("Number of Pins", "8P")]),
        ("8 pin header", [("Number of Pins", "8P")]),
        ("pin header 40", [("Number of Pins", "40P")])])
    def test_parse(self, query, expected):
        parsed = parse_smart_query(query)
        assert _filters(parsed) == expected and ".54" not in parsed.remaining_text


class TestPartTypeConflict:
    """"addressable RGB LED" with subcategory_id=71 returned every discrete LED, unexplained."""

    async def test_named_type_differs(self):
        result = await search("addressable RGB LED", subcategory_id=71, match_all_terms=False, limit=1)
        notes = result["parsed"]["detected"]["not_searched"]
        assert any("RGB LEDs(Built-in IC)" in n and "LED Indication - Discrete" in n for n in notes)

    @pytest.mark.parametrize("query, subcategory", [
        ("10uF capacitor", "Tantalum Capacitors"), ("LED", "RGB LEDs(Built-in IC)"),
        ("10k resistor 0603", "Chip Resistor - Surface Mount")])
    async def test_generic_word_in_the_family_isnt_noted(self, query, subcategory):
        result = await search(query, subcategory_name=subcategory, limit=1)
        assert not any("not the subcategory given" in n for n in result["parsed"]["detected"].get("not_searched", []))


class TestEsp32Chip:
    """"ESP32-S3 chip QFN" returned modules; the four S3 chips are filed under three part types."""

    @pytest.mark.parametrize("query", ["ESP32-S3 chip QFN", "ESP32-S3 chip", "ESP32-C3 chip", "ESP32-S3 SoC"])
    async def test_only_chips(self, query):
        result = await search(query)
        assert result["filters_applied"]["package"] == "QFN" and result["total"] > 0
        assert all(p["package"].upper().startswith("QFN") for p in result["results"])

    async def test_module_unchanged(self):
        result = await search("ESP32-S3 module")
        assert result["parsed"]["subcategory"] == "wifi modules"

    @pytest.mark.parametrize("query", ["ESP32-S3-MINI-1 QFN60_ESP32-S2-MINI-1_EXP IC", "ESP32-S3-WROOM-1 chip"])
    def test_module_numbers_and_bom_words(self, query):
        assert parse_smart_query(query).package != "QFN"


class TestStockCheckFragment:
    """jlc_stock_check("2812") matched only 594D capacitors in a 2812 case."""

    @pytest.fixture
    def live(self, monkeypatch):
        async def search(**kwargs):
            return {"results": [{"lcsc": "C1956513", "model": "594D227X96R3C2T"}], "total": 1}
        monkeypatch.setattr(server, "_client", SimpleNamespace(search=search))

    async def test_names_parts_containing_it(self, live):
        result = await server.jlc_stock_check(query="2812")
        named = result["hint"].split("include ")[1].split(":")[0].split(", ")
        assert named and all("2812" in mpn.upper() for mpn in named)

    async def test_no_hint_when_a_result_has_it(self, monkeypatch):
        async def search(**kwargs):
            return {"results": [{"lcsc": "C2843785", "model": "XL-5050RGBC-2812B"}], "total": 1}
        monkeypatch.setattr(server, "_client", SimpleNamespace(search=search))
        assert "hint" not in await server.jlc_stock_check(query="2812")
