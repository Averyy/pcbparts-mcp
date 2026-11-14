"""Part numbers that start with digits are part numbers (0.9.2).

"9774025151R M2.5 spacer" searched both words; the Wurth listing (C7496631) has no M2.5, so
nothing matched and the retry dropped the part number too, returning 534 unrelated standoffs.
Letter-first part numbers (STM32F103C8T6) are searched alone, with the other words reported.
"""

import pytest

from pcbparts_mcp import server
from pcbparts_mcp.smart_parser.parser import parse_smart_query


@pytest.mark.parametrize(("query", "model"), [
    ("9774025151R M2.5 spacer", "9774025151R"),
    ("9774025151 spacer", "9774025151"),
    ("61300211121 pin header", "61300211121"),
    ("10118194-0001LF micro usb", "10118194-0001LF"),
    ("5023320410 2mm", "5023320410"),
])
def test_digit_first_part_number_is_the_model(query, model):
    assert parse_smart_query(query).model_number == model


@pytest.mark.parametrize("query", [
    "0402 10k",               # packages have 4 digits
    "C7496631",               # LCSC codes start with C
    "123456 spacer",          # six digits
    "1000000uF",              # a whole number with its unit is a value
    "4700000R",
    "4700000 ohm resistor",   # also with a space before the unit
    "10000000 pF",
    "100000 ohm",
])
def test_values_and_codes_are_not_models(query):
    assert parse_smart_query(query).model_number is None


async def test_part_number_with_other_words_finds_the_part():
    if not server.get_db().get_by_lcsc_batch(["C7496631"])["C7496631"]:
        pytest.skip("C7496631 (Wurth 9774025151R) is no longer stocked")
    result = await server.jlc_search(query="9774025151R M2.5 spacer", limit=5)
    assert [p["lcsc"] for p in result["results"]] == ["C7496631"]
    assert any(note.startswith("M2.5:") for note in result["parsed"]["detected"]["not_searched"])


async def test_unknown_part_number_returns_no_unrelated_parts():
    result = await server.jlc_search(query="9999999999R spacer", limit=5)
    assert result["total"] == 0 and not result.get("relaxed")
