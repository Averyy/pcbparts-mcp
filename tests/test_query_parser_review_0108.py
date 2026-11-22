"""Peak comparisons, signed decimal commas and bounded query-normalization work."""

import cProfile
from dataclasses import replace
from pathlib import Path

import pytest

from pcbparts_mcp import server
from pcbparts_mcp.search.spec_filter import SpecFilter
from pcbparts_mcp.smart_parser import parser, values


def filters(parsed):
    return [(f.name, f.operator, f.value) for f in parsed.spec_filters]


@pytest.mark.parametrize("written,operator", [
    ("<", "<"), ("<=", "<="), (">", ">"), (">=", ">="),
    ("under", "<"), ("below", "<"), ("at most", "<="), ("max", "<="),
    ("up to", "<="), ("at least", ">="), ("over", ">"), ("min", ">="),
], ids=["lt", "le", "gt", "ge", "under", "below", "most", "max", "upto", "least", "over", "min"])
@pytest.mark.parametrize("form", [
    "{op} 6A peak", "peak {op} 6A", "peak current {op} 6A", "{op} peak current 6A",
], ids=["value_first", "peak_first", "named", "op_first"])
@pytest.mark.parametrize("strict", [False, True])
def test_peak_comparison(written, operator, form, strict):
    query = form.format(op=written) + " brushed DC motor driver"
    parsed = parser.parse_smart_query(query, strict=strict)
    assert filters(parsed) == [("Peak Current", operator, "6A")]
    assert parsed.remaining_text == ""
    assert parsed.detected["semantic"] == [f"{form.format(op=written)} (-> Peak Current {operator} 6A)"]


@pytest.mark.parametrize("words,operator,value", [
    ("<6A peak", "<", "6A"), ("peak current<=6A", "<=", "6A"),
    ("6A peak", ">=", "6A"), ("peak 6A", ">=", "6A"),
    ("6A peak current", ">=", "6A"), ("peak current 6A", ">=", "6A"),
    ("PEAK CURRENT UNDER 6000 mA", "<", "6000mA"), ("peak up to 6,5A", "<=", "6.5A"),
], ids=["compact", "named_sign", "value", "peak", "value_named", "named", "units", "comma"])
@pytest.mark.parametrize("hint", [False, True])
def test_peak_group_or_explicit_family(words, operator, value, hint):
    parsed = parser.parse_smart_query(
        words if hint else words + " motor driver",
        subcategory_hint="Brushed DC Motor Drivers" if hint else None,
    )
    assert filters(parsed) == [("Peak Current", operator, value)]
    assert parsed.remaining_text == ""


@pytest.mark.parametrize("hint", ["LDO", "Stepper Motor Driver", "Motor Driver ICs", "Pin Headers"])
def test_explicit_unsupported_family_does_not_get_peak(hint):
    parsed = parser.parse_smart_query("peak current under 6A motor driver", subcategory_hint=hint)
    assert not any(f.name == "Peak Current" for f in parsed.spec_filters)


def test_peak_comparisons_stay_with_their_values():
    parsed = parser.parse_smart_query("peak under 6A and peak over 2A brushed DC motor driver")
    assert filters(parsed) == [("Peak Current", "<", "6A"), ("Peak Current", ">", "2A")]
    assert parsed.remaining_text == ""


@pytest.mark.parametrize("sign", ["-", "−", "+"], ids=["minus", "unicode", "plus"])
@pytest.mark.parametrize("strict", [False, True])
def test_signed_decimal_comma(sign, strict):
    query = f"{sign}3,3V LDO"
    dotted = f"{'-' if sign == '−' else sign}3.3V LDO"
    actual = parser.parse_smart_query(query, strict=strict)
    expected = parser.parse_smart_query(dotted, strict=strict)
    assert actual.original == query
    assert replace(actual, original=dotted) == expected
    assert filters(actual) == [("Vout", "=", dotted.split()[0])]
    assert values.normalize_value_notation(query) == dotted


@pytest.mark.parametrize("query", [
    "ABC-3,3V", "ABC+3,3V", "1-3,3V", "--3,3V", "1+-3,3V",
    "1,3,3V", "1.3,3V", "-3,333V", "-3,3VABC", "-3,3",
], ids=["model_minus", "model_plus", "digits", "double", "mixed", "commas", "dot", "thousand", "suffix", "unitless"])
def test_decimal_comma_does_not_rewrite_token_fragments(query):
    assert values.normalize_value_notation(query) == query


def repeated_cases():
    """Full parsed outputs captured before the performance fix, including ambiguity notes."""
    query = ("1p " * 167)[:500]
    yield pytest.param(query, parser.ParsedQuery(
        original=query, remaining_text="",
        spec_filters=[SpecFilter("Number of Pins", "=", "1P")] * 167,
        detected={"semantic": ["1p was read as 1 pins; write 1pF for a capacitor"] * 167,
                  "values": [{"raw": "1p", "type": "position_count", "normalized": "1P"}] * 167},
    ), id="pins")
    query = ("2,2 " * 167)[:500]
    yield pytest.param(query, parser.ParsedQuery(original=query, remaining_text=query.strip()), id="commas")
    query = ("220p C0G " * 100)[:500]
    yield pytest.param(query, parser.ParsedQuery(
        original=query, remaining_text="", subcategory="multilayer ceramic capacitors mlcc - smd/smt",
        spec_filters=[SpecFilter("Capacitance", "=", "220pF")] * 56 + [
            SpecFilter("Temperature Coefficient", "=", name) for name in ("C0G", "NP0", "COG")],
        detected={"values": [{"raw": "220pF", "type": "capacitance", "normalized": "220pF"}] * 56,
                  "subcategory_inferred": "multilayer ceramic capacitors mlcc - smd/smt", "semantic": ["c0g"]},
    ), id="caps")
    query = ("1234567890," * 50)[:500]
    yield pytest.param(query, parser.ParsedQuery(
        original=query, remaining_text="1234567890", model_number="1234567890",
        detected={"model_number": "1234567890"},
    ), id="digits")
    query = ("6A peak " * 100)[:500]
    yield pytest.param(query, parser.ParsedQuery(
        original=query, remaining_text=" ".join(["peak"] * 62),
        spec_filters=[SpecFilter("Current Rating", ">=", "6A")] * 63,
        detected={"values": [{"raw": "6A", "type": "current", "normalized": "6A"}] * 63},
    ), id="peak")
    query = "< 1p " * 100
    yield pytest.param(query, parser.ParsedQuery(
        original=query, remaining_text="",
        spec_filters=[SpecFilter("Number of Pins", "<", "1P")] * 100,
        detected={"semantic": ["1p was read as 1 pins; write 1pF for a capacitor"] * 100,
                  "values": [{"raw": "1p", "type": "position_count", "normalized": "1P"}] * 100},
    ), id="comparisons")


@pytest.mark.parametrize("query,expected", list(repeated_cases()))
def test_repeated_queries_preserve_output_with_bounded_normalization(monkeypatch, query, expected):
    normalize = values.normalize_value_notation
    scanned = []

    def counted(text, **kwargs):
        scanned.append(len(text))
        return normalize(text, **kwargs)

    monkeypatch.setattr(values, "normalize_value_notation", counted)
    monkeypatch.setattr(parser, "normalize_value_notation", counted)
    assert parser.parse_smart_query(query) == expected
    # Two extraction passes, plus at most one pass for written comparisons.
    assert len(scanned) <= 3
    assert sum(scanned) <= 4 * len(query)


@pytest.mark.parametrize("query,expected", [
    (("1p " * 167)[:500], ("1p " * 167)[:500]),
    (("220p C0G " * 100)[:500], ("220p C0G " * 100)[:500].replace("220p", "220pF")),
    ("50V 1p 2p 25V 3p 4p", "50V 1pF 2pF 25V 3pF 4p"),
    ("1p 50V " * 60, "1pF 50V " * 60),
    ("1p 50V connector", "1p 50V connector"),
], ids=["pins", "caps", "neighbours", "voltages", "connector"])
def test_picofarad_context_scans_are_bounded(query, expected):
    # Count regex work, not elapsed time: this also catches per-token prefix scans.
    profile = cProfile.Profile()
    actual = profile.runcall(values.normalize_value_notation, query)
    assert actual == expected
    regex_calls = sum(entry.callcount for entry in profile.getstats()
                      if isinstance(entry.code, str) and "'re.Pattern'" in entry.code)
    assert regex_calls <= 20


@pytest.fixture
def catalog():
    if not (Path(__file__).parent.parent / "data" / "components.db").exists():
        pytest.skip("local catalog not built")
    return server.get_db()


@pytest.mark.parametrize("query,part_type,name,operator,value", [
    ("<6A peak brushed DC motor driver", "brushed DC motor driver", "Peak Current", "<", "6A"),
    ("peak current under 6A motor driver", "motor driver", "Peak Current", "<", "6A"),
    ("peak over 6A motor driver", "motor driver", "Peak Current", ">", "6A"),
    ("-3,3V LDO", "LDO", "Vout", "=", "-3.3V"),
    ("−3,3V LDO", "LDO", "Vout", "=", "-3.3V"),
], ids=["brushed", "group_lt", "group_gt", "minus", "unicode"])
@pytest.mark.parametrize("strict", [False, True])
async def test_review_search_matches_explicit_filter(catalog, query, part_type, name, operator, value, strict):
    actual = await server.jlc_search(query=query, strict=strict, limit=100)
    expected = await server.jlc_search(query=part_type, strict=True, limit=100,
                                      spec_filters=[{"name": name, "op": operator, "value": value}])
    assert "error" not in actual, actual
    assert "error" not in expected, expected
    assert actual["total"] == expected["total"]
    assert actual["results"] == expected["results"]
    assert actual["filters_applied"]["spec_filters"] == expected["filters_applied"]["spec_filters"]
    assert not actual.get("ignored_filters")
