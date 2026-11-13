"""A part number that ends in a unit letter is searched as a part number (0.9.1).

jlc_search("9774025151R") read the Wurth spacer's part number as a 9.77 GOhm resistance, filtered
chip resistors and returned nothing; with strict=true the leftover token was an unsupported
constraint and an error. A value's whole-number digits have at most 4 significant digits.
"""

import pytest

from pcbparts_mcp import server
from pcbparts_mcp.smart_parser.parser import parse_smart_query


@pytest.mark.parametrize("query", ["9774025151R", "9774030243R", "123456K7"])
def test_long_digit_run_is_not_a_resistance(query):
    parsed = parse_smart_query(query)
    assert not any(v["type"] == "resistance" for v in parsed.detected.get("values", []))
    assert parsed.subcategory is None
    assert "unsupported_constraints" not in parsed.detected
    assert query.casefold() in parsed.remaining_text.casefold()


@pytest.mark.parametrize(("query", "normalized"), [
    ("100R", "100Ohm"),
    ("1000R", "1000Ohm"),
    ("10000R", "10000Ohm"),
    ("0R", "0Ohm"),
    ("4R7", "4R7"),
    ("4R75", "4R75"),
    ("4k7", "4k7"),
    ("10k", "10kOhm"),
    ("4.99k", "4.99kOhm"),
    ("2.2M", "2.2MOhm"),
    ("100000 ohm", "100000Ohm"),
    ("12345 ohm", "12345Ohm"),  # spelled out, so meant as a resistance however many digits
])
def test_resistance_spellings_still_parse(query, normalized):
    values = parse_smart_query(query).detected.get("values", [])
    assert [v["normalized"] for v in values if v["type"] == "resistance"] == [normalized]


@pytest.mark.parametrize(("query", "token"), [("LED 100mcd", "100mcd"), ("motor 3000rpm", "3000rpm")])
def test_unapplied_values_are_still_reported(query, token):
    assert token in parse_smart_query(query).detected.get("unsupported_constraints", [])


@pytest.mark.parametrize("strict", [False, True])
async def test_search_finds_the_part(strict):
    if not server.get_db().get_by_lcsc_batch(["C7496631"])["C7496631"]:
        pytest.skip("C7496631 (Wurth 9774025151R) is no longer stocked")
    result = await server.jlc_search(query="9774025151R", strict=strict, limit=5)
    assert not result.get("error")
    assert "C7496631" in [p["lcsc"] for p in result["results"]]
