"""0.8.17: tool docstrings hold only what MCP clients receive.

fastmcp sends a docstring's first text section and its Args text (fastmcp/utilities/docstring_parsing.py);
a Returns or Examples section, or text after Args, is dropped. 0.8.15's Mouser lifecycle note sat
under Returns and never reached clients, and 14 tools had about 9,000 such characters.
"""

import asyncio
import inspect

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
    ("jlc_search", 'pcba_type "standard_only" means one such part moves the whole order'),
    ("jlc_search", "total counts every match before limit and offset"),
    ("jlc_get_part", "MPN lookups search the daily catalog snapshot (stock >= 10)"),
    ("jlc_find_alternatives", "Stock comes from the live search or the daily catalog snapshot"),
    ("jlc_get_pinout", "matches the footprint pad"),
    ("mouser_get_part", "not_found lists the given numbers no result matches"),
    ("sensor_recommend", "sorted by how many platforms have drivers"),
    ("get_design_rules", "found by their text, not their name or keywords"),
    ("board_search", "matched_by says why each appeared"),
    ("board_get", "look them up with jlc_get_part or mouser_get_part"),
])
def test_moved_guidance_is_sent(name, phrase):
    assert phrase in " ".join(parse_docstring(getattr(server, name)).description.split())
