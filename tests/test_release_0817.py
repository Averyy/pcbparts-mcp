"""0.8.17: tool docstrings hold only what MCP clients receive.

fastmcp sends a docstring's first text section and its Args text (fastmcp/utilities/docstring_parsing.py);
a Returns or Examples section, or text after Args, is dropped. 0.8.15's Mouser lifecycle note sat
under Returns and never reached clients, and 14 tools had about 9,000 such characters.
"""

import asyncio
import inspect
from pathlib import Path

import pytest
from fastmcp.utilities.docstring_parsing import parse_docstring
from griffe import Docstring, DocstringSectionKind

import pcbparts_mcp.server as server


def _tools():
    return sorted(t.name for t in asyncio.run(server.mcp.list_tools()))


@pytest.mark.parametrize("name", _tools())
def test_every_section_is_sent(name):
    fn = getattr(server, name)
    doc = inspect.getdoc(fn)
    sections = Docstring(doc, lineno=1, parser="google").parse()
    kinds = [section.kind for section in sections]
    assert kinds in ([DocstringSectionKind.text], [DocstringSectionKind.text, DocstringSectionKind.parameters]), (
        f"{name}: only a first text section and Args reach clients, not {[k.value for k in kinds]}")
    sent = parse_docstring(fn)
    # Every word of the docstring reaches the client, in the description or a parameter's text
    sent_words = set(" ".join([sent.description or "", *sent.parameters.values()]).split())
    doc_words = set(doc.split()) - {"Args:"} - {f"{p}:" for p in sent.parameters}
    assert doc_words <= sent_words, f"{name}: not sent: {sorted(doc_words - sent_words)[:10]}"


@pytest.mark.parametrize("name, phrase", [
    ("jlc_stock_check", "JLCPCB matches whole part numbers and their starts"),
    ("jlc_search", "daily catalog snapshot (stock >= 10)"),
    ("jlc_search", "one standard_only part moves the whole order to Standard assembly"),
    ("jlc_search", "true keeps requirements, errors on unsupported constraints"),
    ("jlc_search", "Repeated = on one spec is OR (Supply Voltage/Vin: all)"),
    ("jlc_search", "= on a range means it includes the value"),
    ("jlc_search", "Unitless uses V, A, ohms, F, H, Hz, W, mm, bytes"),
    ("jlc_search", "Operating Temperature: <= -40 reaches down to -40°C; >= 85 up to 85°C"),
    ("jlc_search", "Dropout at a load: 0.3V@500mA"),
    ("jlc_get_part", "MPN lookup always uses the daily snapshot"),
    ("jlc_get_parts", "MPNs never match by full text"),
    ("jlc_find_alternatives", "Stock is live or snapshot"),
    ("jlc_get_pinout", "Numbers match footprint pads"),
    ("jlc_get_pinout", "mm from origin, y down"),
    ("jlc_get_pinout", "Absent electrical means unknown"),
    ("mouser_get_part", "batch up to 10 full part numbers"),
    ("sensor_recommend", "Calculated CO2 is eco2, not co2"),
    ("sensor_recommend", "imu alone: acceleration OR gyroscope OR magnetic_field; with others: all three"),
    ("sensor_recommend", "gpio includes analog/pwm/one_wire; digital includes gpio/pwm/one_wire"),
    ("get_design_rules", "Empty topic lists files"),
    ("board_search", "board_get(slug, focus=IC)"),
    ("board_get", "part numbers with jlc_get_part or mouser_get_part"),
], ids=["stock", "snapshot", "assembly", "strict", "repeat_eq", "range_eq", "units", "temperature",
        "dropout", "mpn", "batch", "alternatives", "pads", "coordinates", "electrical",
        "mouser", "co2", "imu", "protocol", "rules", "boards", "lookup"])
def test_calling_guidance_is_sent(name, phrase):
    sent = parse_docstring(getattr(server, name))
    assert phrase in " ".join(" ".join([sent.description, *sent.parameters.values()]).split())


@pytest.mark.parametrize("phrase", [
    "`total` counts all matches before `limit`/`offset`",
    "`not_found` (unmatched or not sent)",
    "`platform_count` descending, name",
    "otherwise the files discussing it most (`note`)",
    "`matched_by`: key IC/component/text/tag",
], ids=["pagination", "unmatched", "sensors", "rules", "boards"])
def test_reply_guidance_is_in_reference(phrase):
    reference = (Path(__file__).parents[1] / "landing" / "llms.txt").read_text(encoding="utf-8")
    assert phrase in reference


def _untyped_arrays(schema, path="parameters"):
    """Paths of arrays whose items schema says nothing (no type, anyOf or $ref)."""
    found = []
    if isinstance(schema, dict):
        if schema.get("type") == "array":
            items = schema.get("items")
            if not isinstance(items, dict) or not ({"type", "anyOf", "$ref"} & items.keys()):
                found.append(path)
        for key, value in schema.items():
            found += _untyped_arrays(value, f"{path}.{key}")
    elif isinstance(schema, list):
        for index, value in enumerate(schema):
            found += _untyped_arrays(value, f"{path}[{index}]")
    return found


def test_every_array_types_its_items():
    """Some clients (Gemini's function declarations) reject an array whose items have no type, and
    one rejected declaration fails the whole request, every server's tools with it."""
    tools = asyncio.run(server.mcp.list_tools())
    assert {t.name: _untyped_arrays(t.parameters) for t in tools if _untyped_arrays(t.parameters)} == {}
