"""Query notation, charger functions, peak currents and nominal fuse ratings (0.10.8)."""

from contextlib import closing
from pathlib import Path
import sqlite3

import pytest
from fastmcp import Client

from pcbparts_mcp import server
from pcbparts_mcp.parsers import parse_current, parse_voltage
from pcbparts_mcp.smart_parser import parse_smart_query
from pcbparts_mcp.smart_parser.values import normalize_value_notation


def filters(parsed):
    return [(f.name, f.operator, f.value) for f in parsed.spec_filters]


@pytest.fixture
def catalog():
    if not (Path(__file__).parent.parent / "data" / "components.db").exists():
        pytest.skip("local catalog not built")
    return server.get_db()


def require_parts(catalog, *codes):
    for code in codes:
        if catalog.get_part_snapshot(code) is None:
            pytest.skip(f"{code} is no longer in the catalog")


async def search(query=None, **kwargs):
    result = await server.jlc_search(query=query, limit=kwargs.pop("limit", 100), **kwargs)
    assert "error" not in result, result
    return result


def same_population(actual, expected):
    assert actual["total"] == expected["total"]
    assert actual["results"] == expected["results"]


@pytest.fixture
def hold_ratings(catalog):
    with closing(sqlite3.connect(catalog.db_path)) as conn:
        rows = conn.execute("""
            SELECT DISTINCT json_extract(j.value, '$[1]')
            FROM components c, json_each(c.attributes) j
            WHERE c.subcategory_id = ? AND c.package = '1812' AND c.stock >= 10
              AND json_extract(j.value, '$[0]') = 'Hold Current'
        """, (catalog.resolve_subcategory_name("Resettable Fuses"),)).fetchall()
    ratings = sorted({rating for row in rows if (rating := parse_current(row[0])) is not None and rating > 0})
    if not ratings:
        pytest.skip("no stocked 1812 resettable fuses with hold ratings")
    return ratings


def hold_rating_gaps(ratings):
    # Prefer the reported 1A query while it is a gap; stay clear of numeric equality's tolerance.
    candidates = [1.0, *((low + high) / 2 for low, high in zip(ratings, ratings[1:]))]
    return [f"{value:g}A" for value in candidates
            if value < max(ratings) and all(abs(rating - value) > value * .01 for rating in ratings)]


@pytest.fixture
def missing_hold_rating(hold_ratings):
    gaps = hold_rating_gaps(hold_ratings)
    if not gaps:
        pytest.skip("no gap below a stocked 1812 hold rating")
    return gaps[0]


COMMA_QUERIES = [
    ("2,2k 0402 resistor", "2.2k 0402 resistor"),
    ("3,3V LDO", "3.3V LDO"),
    ("4,7uF capacitor 0603", "4.7uF capacitor 0603"),
    ("2,54 mm board stacker pin header 16 pin", "2.54 mm board stacker pin header 16 pin"),
]


@pytest.mark.parametrize("query,dotted", COMMA_QUERIES, ids=["resistor", "ldo", "cap", "reddit"])
@pytest.mark.parametrize("strict", [False, True])
def test_decimal_comma_parse(query, dotted, strict):
    actual = parse_smart_query(query, strict=strict)
    expected = parse_smart_query(dotted, strict=strict)
    assert actual.original == query
    assert filters(actual) == filters(expected)
    assert actual.remaining_text == expected.remaining_text
    assert actual.package == expected.package


@pytest.mark.parametrize("unit", ["k", "M", "R", "V", "A", "W", "uF", "µF", "nF", "pF", "H", "mm", "%", "Ω"])
def test_decimal_comma_units(unit):
    assert normalize_value_notation(f"2,54{unit}") == normalize_value_notation(f"2.54{unit}")


@pytest.mark.parametrize("query,expected", [
    ("1,000uF", "1000uF"), ("10,000", "10000"), ("1,000,000pF", "1000000pF"),
    ("0402,0603", "0402,0603"), ("10k, 0603", "10k, 0603"),
    ("2, 2k", "2, 2k"), ("2,54", "2,54"), ("ABC2,2V", "ABC2,2V"),
], ids=["thousand", "bare", "million", "packages", "tokens", "space", "no_unit", "model"])
def test_other_commas(query, expected):
    assert normalize_value_notation(query) == expected


@pytest.mark.parametrize("query,dotted", COMMA_QUERIES, ids=["resistor", "ldo", "cap", "reddit"])
@pytest.mark.parametrize("strict", [False, True])
async def test_decimal_comma_search(catalog, query, dotted, strict):
    actual = await search(query, strict=strict)
    expected = await search(dotted, strict=strict)
    same_population(actual, expected)
    assert actual["filters_applied"] == expected["filters_applied"]


@pytest.mark.parametrize("voltage", ["4.2V", "4.20V", "4,2V"])
@pytest.mark.parametrize("strict", [False, True])
async def test_charger_setpoint_and_function(catalog, voltage, strict):
    require_parts(catalog, "C32574", "C669680", "C20618071")
    actual = await search(f"{voltage} LiPo charger SOT-23-5", strict=strict)
    expected = await search(subcategory_name="Battery Management", package="SOT-23-5", strict=True,
                            spec_filters=[{"name": "The Chip Type", "op": "=", "value": "Charging IC"},
                                          {"name": "Charging Saturation Voltage", "op": "=", "value": "4.2V"}])
    same_population(actual, expected)
    assert actual["total"] > 0 and not actual.get("ignored_filters")
    assert not {"C669680", "C20618071"} & {p["lcsc"] for p in actual["results"]}
    assert all("Charging IC" in p["specs"]["The Chip Type"] for p in actual["results"])
    assert all("4.2V" in p["specs"]["Charging Saturation Voltage"] for p in actual["results"])


@pytest.mark.parametrize("query", ["LiPo protection IC", "battery protection SOT-23-6", "BMS 4S protection"])
def test_protection_is_not_charging(query):
    assert ("The Chip Type", "=", "Charging IC") not in filters(parse_smart_query(query))


@pytest.mark.parametrize("words", ["6A peak", "peak 6A", "6A peak current", "peak current 6000mA"])
@pytest.mark.parametrize("strict", [False, True])
async def test_peak_current_population(catalog, words, strict):
    require_parts(catalog, "C1855818")
    actual = await search(f"{words} brushed DC motor driver", strict=strict)
    expected = await search(subcategory_name="Brushed DC Motor Drivers", strict=True,
                            spec_filters=[{"name": "Peak Current", "op": ">=", "value": "6A"}])
    same_population(actual, expected)
    assert "C1855818" in {p["lcsc"] for p in actual["results"]}
    assert all(parse_current(p["specs"]["Peak Current"]) >= 6 for p in actual["results"])
    assert not any(f["name"] == "Output Current" for f in actual["filters_applied"]["spec_filters"])
    assert not actual.get("relaxed")


def test_peak_current_requires_supported_context():
    parsed = parse_smart_query("peak 6A", subcategory_hint="Brushed DC Motor Drivers")
    assert filters(parsed) == [("Peak Current", ">=", "6A")]
    parsed = parse_smart_query("6A peak LDO")
    assert ("Output Current", ">=", "6A") in filters(parsed)
    assert not any(f[0] == "Peak Current" for f in filters(parsed))


@pytest.mark.parametrize("context", ["capacitor", "cap", "MLCC", "C0G", "NP0", "X7R", "X5R", "X6S", "X7S", "Y5V", "Z5U", "50V"])
@pytest.mark.parametrize("before", [False, True])
def test_picofarad_context(context, before):
    query = f"{context} 220p" if before else f"220p {context}"
    parsed = parse_smart_query(query)
    assert ("Capacitance", "=", "220pF") in filters(parsed)
    assert not any(f[0] == "Number of Pins" for f in filters(parsed))


@pytest.mark.parametrize("context", ["header", "connector", "socket", "FPC", "board-to-board"])
@pytest.mark.parametrize("strict", [False, True])
def test_connector_context_keeps_pin_shorthand(context, strict):
    parsed = parse_smart_query(f"20p {context} 50V", strict=strict)
    assert not any(f[0] == "Capacitance" for f in filters(parsed))
    assert any(v["type"] == "position_count" and v["normalized"] == "20P" for v in parsed.detected["values"])


def test_pin_structure_with_p_suffix():
    assert ("Pin Structure", "=", "2x20P") in filters(parse_smart_query("2x20p header"))
    parsed = parse_smart_query("560p", subcategory_hint="Multilayer Ceramic Capacitors MLCC - SMD/SMT")
    assert filters(parsed) == [("Capacitance", "=", "560pF")]


@pytest.mark.parametrize("query,explicit", [("220p C0G", "220pF C0G"), ("560p capacitor", "560pF capacitor")], ids=["dielectric", "cap"])
@pytest.mark.parametrize("strict", [False, True])
async def test_picofarad_search(catalog, query, explicit, strict):
    same_population(await search(query, strict=strict), await search(explicit, strict=strict))


async def test_ambiguous_p_note_reaches_mcp_reply(catalog):
    require_parts(catalog, "C3650083")
    async with Client(server.mcp) as client:
        result = (await client.call_tool("jlc_search", {"query": "560p"})).data
    assert {"name": "Number of Pins", "op": "=", "value": "560P"} in result["filters_applied"]["spec_filters"]
    notes = result["parsed"]["detected"]["semantic"]
    assert any("560 pins" in note and "560pF" in note for note in notes)


@pytest.mark.parametrize("strict", [False, True])
async def test_resettable_nominal_hold_rating(catalog, strict):
    require_parts(catalog, "C18198343", "C54300298")
    actual = await search("resettable fuse 2A 33V 1812", strict=strict)
    expected = await search(subcategory_name="Resettable Fuses", package="1812", strict=True,
                            spec_filters=[{"name": "Hold Current", "op": "=", "value": "2A"},
                                          {"name": "Voltage - Max", "op": ">=", "value": "33V"}])
    same_population(actual, expected)
    assert actual["total"] > 0
    assert "C54300298" not in {p["lcsc"] for p in actual["results"]}
    assert all(parse_current(p["specs"]["Hold Current"]) == 2 for p in actual["results"])
    assert all(parse_voltage(p["specs"]["Voltage - Max"]) >= 33 for p in actual["results"])


@pytest.mark.parametrize("query", ["fuse 2A 33V 1812", "resettable fuse 2000mA 33V 1812"], ids=["routed", "units"])
@pytest.mark.parametrize("strict", [False, True])
async def test_nominal_rating_survives_family_routing_and_unit_spelling(catalog, query, strict):
    require_parts(catalog, "C18198343")
    same_population(await search(query, strict=strict), await search("resettable fuse 2A 33V 1812", strict=strict))


async def test_hold_rating_compares_numerically(catalog):
    # 500mA parts must also match a nominal 0.5A query.
    actual = await search("resettable fuse 0.5A 1812", strict=True)
    expected = await search(subcategory_name="Resettable Fuses", package="1812", strict=True,
                            spec_filters=[{"name": "Hold Current", "op": ">=", "value": "500mA"},
                                          {"name": "Hold Current", "op": "<=", "value": "500mA"}])
    if not expected["total"]:
        pytest.skip("no 500mA 1812 fuses remain in the catalog")
    same_population(actual, expected)
    assert actual["total"] > 0


async def test_nominal_hold_falls_back_to_nearest_rating(catalog, missing_hold_rating):
    value = missing_hold_rating
    actual = await search(f"{value} 1812 fuse")
    widened = {"name": "Hold Current", "op": ">=", "value": value}
    expected = await search(subcategory_name="Resettable Fuses", package="1812", strict=True,
                            spec_filters=[widened], sort_spec="Hold Current")
    assert actual["total"] == expected["total"] > 0
    assert actual["results"] == expected["results"]
    assert actual["relaxed"]["widened_filters"] == [
        {"filter": f"Hold Current = {value}", "now": f"Hold Current >= {value}"}]
    assert actual["relaxed"]["reason"]
    assert actual["filters_applied"]["spec_filters"] == [widened]
    ratings = [parse_current(p["specs"]["Hold Current"]) for p in actual["results"]]
    assert all(rating >= parse_current(value) for rating in ratings)
    assert ratings[0] == min(ratings)


async def test_strict_nominal_hold_does_not_widen(catalog, missing_hold_rating):
    value = missing_hold_rating
    actual = await search(f"{value} 1812 fuse", strict=True)
    assert actual["total"] == 0 and actual["results"] == []
    assert actual["filters_applied"]["spec_filters"] == [
        {"name": "Hold Current", "op": "=", "value": value}]
    assert not actual.get("relaxed")


async def test_stocked_nominal_hold_does_not_widen(catalog, hold_ratings):
    rating = min(hold_ratings, key=lambda value: abs(value - 2))
    value = f"{rating:g}A"
    actual = await search(f"{value} 1812 fuse")
    exact = {"name": "Hold Current", "op": "=", "value": value}
    catalog_value = f"{rating * 1000:g}mA" if rating < 1 else value
    expected = await search(subcategory_name="Resettable Fuses", package="1812", strict=True,
                            spec_filters=[{**exact, "value": catalog_value}])
    same_population(actual, expected)
    assert actual["total"] > 0
    assert actual["filters_applied"]["spec_filters"] == [exact]
    assert all(parse_current(p["specs"]["Hold Current"]) == rating for p in actual["results"])
    assert not actual.get("relaxed")


async def test_nearest_hold_rating_paging(catalog, missing_hold_rating, monkeypatch):
    from pcbparts_mcp.search.spec_filter import SpecFilter

    value = missing_hold_rating
    # Sort the entire stock-ranked population independently of the SQL spec sort. Low-stock
    # parts outside the old 100-row window must appear on their correct rating's page too.
    expected = catalog.search(subcategory_name="Resettable Fuses", package="1812", limit=100000,
                              spec_filters=[SpecFilter("Hold Current", ">=", value)])
    if expected["total"] < 130:
        pytest.skip("fewer than 130 stocked fuses above the missing nominal hold rating")
    ordered = sorted(expected["results"], key=lambda p: parse_current(p["specs"]["Hold Current"]))
    original_search = catalog.search
    calls = []

    def capture(*args, **kwargs):
        calls.append(kwargs)
        return original_search(*args, **kwargs)

    monkeypatch.setattr(catalog, "search", capture)
    pages = []
    for offset in (0, 30, 60, 90, 120):
        calls.clear()
        page = await search(f"{value} 1812 fuse", limit=30, offset=offset)
        assert page["total"] == expected["total"]
        assert [p["lcsc"] for p in page["results"]] == [p["lcsc"] for p in ordered[offset:offset + 30]]
        assert page["relaxed"]["widened_filters"] == [
            {"filter": f"Hold Current = {value}", "now": f"Hold Current >= {value}"}]
        assert page["sort"]["spec"] == "Hold Current" and page["sort"]["order"] == "asc"
        assert page["page_info"]["offset"] == offset
        assert page["page_info"]["limit"] == 30
        assert page["page_info"]["returned"] == len(page["results"])
        # Exactly one retry after the nominal search, with the caller's page untouched.
        assert len(calls) == 2
        assert calls[-1]["offset"] == offset and calls[-1]["limit"] == 30
        pages.extend(page["results"])
    assert len({p["lcsc"] for p in pages}) == len(pages)
    ratings = [parse_current(p["specs"]["Hold Current"]) for p in pages]
    assert ratings == sorted(ratings)
    assert all(p["sort_value"] == p["specs"]["Hold Current"] for p in pages)


@pytest.mark.parametrize("words", ["at least 2A", ">=2A", "2A or more", "min 2A"])
@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("kind", ["resettable fuse", "fuse"], ids=["named", "routed"])
async def test_explicit_fuse_minimum(catalog, words, strict, kind):
    require_parts(catalog, "C54300298")
    actual = await search(f"{kind} {words} 33V 1812", strict=strict)
    expected = await search(subcategory_name="Resettable Fuses", package="1812", strict=True,
                            spec_filters=[{"name": "Hold Current", "op": ">=", "value": "2A"},
                                          {"name": "Voltage - Max", "op": ">=", "value": "33V"}])
    same_population(actual, expected)
    assert "C54300298" in {p["lcsc"] for p in actual["results"]}


@pytest.mark.parametrize("words,operator", [("2A", "="), ("at least 2A", ">="), (">=2A", ">="), ("2A or more", ">="), ("min 2A", ">=")])
async def test_ordinary_fuse_nominal_or_minimum(catalog, words, operator):
    actual = await search(f"fuse {words} 250V", subcategory_name="Disposable fuses", strict=True)
    expected = await search(subcategory_name="Disposable fuses", strict=True,
                            spec_filters=[{"name": "Current Rating", "op": operator, "value": "2A"},
                                          {"name": "Voltage Rating (DC)", "op": ">=", "value": "250V"}])
    same_population(actual, expected)
    assert {"name": "Current Rating", "op": operator, "value": "2A"} in actual["filters_applied"]["spec_filters"]


@pytest.mark.parametrize("alias", ["PPTC", "PPTC fuse", "PTC fuse", "polyswitch", "polyfuse"])
@pytest.mark.parametrize("strict", [False, True])
async def test_resettable_aliases(catalog, alias, strict):
    require_parts(catalog, "C48985875")
    actual = await search(f"{alias} 3A 30V 1812", strict=strict)
    expected = await search(subcategory_name="Resettable Fuses", package="1812", strict=True,
                            spec_filters=[{"name": "Hold Current", "op": "=", "value": "3A"},
                                          {"name": "Voltage - Max", "op": ">=", "value": "30V"}])
    same_population(actual, expected)
    assert "C48985875" in {p["lcsc"] for p in actual["results"]}
    assert not actual["parsed"]["remaining_text"]


def test_ptc_thermistors_stay_thermistors():
    assert parse_smart_query("PTC thermistor 10k").subcategory == "ptc thermistors"


@pytest.mark.parametrize("value,spellings", [
    ("0.5A", ["0.5A", "500mA"]), ("500mA", ["0.5A", "500mA"]), ("2.4GHz", ["2.4GHz", "2400MHz"]),
    ("4k7", []), ("10", []), ("2.7V~5.5V", []),
], ids=["amps", "milliamps", "gigahertz", "code", "bare", "range"])
def test_unit_spellings(value, spellings):
    from pcbparts_mcp.search.spec_filter import unit_spellings
    from pcbparts_mcp.parsers import parse_current, parse_frequency
    parsed = parse_current(value) if value.endswith("A") else parse_frequency(value) if "Hz" in value else 1.0
    assert [s for s in unit_spellings(value, parsed) if s in spellings] == spellings


async def test_explicit_equals_any_unit_spelling(catalog):
    # "= 0.5A" found nothing: the prefilter matched only the caller's spelling, the catalog lists "500mA"
    args = {"subcategory_name": "Resettable Fuses", "package": "1210"}
    results = [await search(**args, spec_filters=[{"name": "Hold Current", "op": "=", "value": value}])
               for value in ("0.5A", "0.50A", "500mA", "500000uA")]
    if not results[0]["total"]:
        pytest.skip("no 500mA 1210 resettable fuse in stock")
    for result in results[1:]:
        same_population(result, results[0])


async def test_slash_text_left_out_before_widening(catalog):
    # "1.5A/3A 1206 fuse": the leftover "/3A" emptied the search; the rating itself is stocked
    exact = await search(subcategory_name="Disposable fuses", package="1206",
                         spec_filters=[{"name": "Current Rating", "op": "=", "value": "1.5A"}])
    if not exact["total"]:
        pytest.skip("no 1.5A 1206 fuse in stock")
    result = await search("1.5A/3A 1206 fuse")
    assert "widened_filters" not in (result.get("relaxed") or {})
    assert result["total"] == exact["total"]
