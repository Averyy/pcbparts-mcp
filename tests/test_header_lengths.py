"""Header body and pin lengths (0.9.2): named in a query they bind to their attribute, and they
compare as numbers.

"pin header 1x16P 2.54mm insulation height 5mm" read 5mm as a second Pitch; two different
pitches never match, so it found nothing. Insulation Height also took only = (Pitch-style string
match), so "Insulation Height > 2.5mm" was ignored and taller headers couldn't be asked for.
"""

import pytest

from pcbparts_mcp import server
from pcbparts_mcp.parsers import parse_length_mm
from pcbparts_mcp.smart_parser.parser import parse_smart_query


def _filters(parsed):
    return [(f.name, f.operator, f.value) for f in parsed.spec_filters]


def test_named_insulation_height_is_not_a_second_pitch():
    parsed = parse_smart_query("pin header 1x16P 2.54mm single row male insulation height 5mm")
    filters = _filters(parsed)
    assert ("Insulation Height", "=", "5mm") in filters
    assert [f for f in filters if f[0] == "Pitch"] == [("Pitch", "=", "2.54mm")]
    assert "insulation" not in parsed.remaining_text.lower()


@pytest.mark.parametrize(("query", "expected"), [
    ("female header 2.54mm insulation height at least 8.5mm", ("Insulation Height", ">=", "8.5mm")),
    ("pin header 2.54mm 8.5mm insulation height", ("Insulation Height", "=", "8.5mm")),
    ("pin header body height under 3mm", ("Insulation Height", "<", "3mm")),
    ("pin header insulation height: 2.5 mm", ("Insulation Height", "=", "2.5mm")),
    ("pin header mating pin length > 6mm", ("Length of Mating Pin", ">", "6mm")),
    ("pin header 2.54mm tail length 3mm", ("Length of End Connection Pin", "=", "3mm")),
    ("pin header length of end connection pin at most 2.8mm", ("Length of End Connection Pin", "<=", "2.8mm")),
])
def test_header_length_phrasings(query, expected):
    filters = _filters(parse_smart_query(query))
    assert expected in filters
    assert len([f for f in filters if f[0] == "Pitch"]) <= 1


def test_lengths_bind_only_where_listed():
    # Female headers list no pin lengths: "tail length" stays a word, not a filter they can't meet
    filters = _filters(parse_smart_query("female header tail length 3mm"))
    assert not any(f[0] == "Length of End Connection Pin" for f in filters)


def test_two_pitches_search_the_first_and_say_so():
    parsed = parse_smart_query("pin header 2.54mm 5mm")
    assert [f for f in _filters(parsed) if f[0] == "Pitch"] == [("Pitch", "=", "2.54mm")]
    assert any(note.startswith("5mm:") for note in parsed.detected["not_searched"])


def test_two_pitches_are_unsupported_in_strict_mode():
    parsed = parse_smart_query("pin header 2.54mm 5mm", strict=True)
    assert parsed.detected["unsupported_constraints"] == ["5mm"]


def test_same_pitch_twice_is_one_pitch():
    parsed = parse_smart_query("pin header 2.54mm 2.54mm")
    assert "not_searched" not in parsed.detected


@pytest.mark.parametrize("name", ["Insulation Height", "Length of Mating Pin", "Length of End Connection Pin"])
async def test_lengths_take_range_filters(name):
    result = await server.jlc_search(subcategory_name="Pin Headers", limit=100,
                                     spec_filters=[{"name": name, "op": ">", "value": "2.5mm"}])
    assert not result.get("ignored_filters")
    assert result["total"] > 0
    assert all(parse_length_mm(p["specs"][name]) > 2.5 for p in result["results"])


async def test_reported_query_finds_matching_headers():
    result = await server.jlc_search(query="pin header 2.54mm single row male insulation height 5mm", limit=100)
    applied = {(f["name"], f["op"], f["value"]) for f in result["filters_applied"]["spec_filters"]}
    assert {("Insulation Height", "=", "5mm"), ("Pitch", "=", "2.54mm")} <= applied
    # = on a numeric spec allows 1% (5.04mm matches 5mm), as for Height and Diameter
    assert all(parse_length_mm(p["specs"]["Insulation Height"]) == pytest.approx(5, rel=0.01)
               and p["specs"]["Pitch"] == "2.54mm" for p in result["results"])
