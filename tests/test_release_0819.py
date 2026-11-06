"""0.8.19: Iq as a spec_filters name, and CSE descriptions without a time cap the code doesn't have.

The jlc_get_pinout `unverified` description test is in test_easyeda_store.py (TestPinoutPolarizedPair).
"""

import pytest
from fastmcp.utilities.docstring_parsing import parse_docstring

import pcbparts_mcp.server as server
from pcbparts_mcp.parsers import parse_current
from pcbparts_mcp.search.spec_filter import ATTRIBUTE_ALIASES

LDO_QUERY = "3.3V LDO"


async def _iq_search(name: str) -> dict:
    return await server.jlc_search(query=LDO_QUERY, spec_filters=[{"name": name, "op": "<", "value": "10uA"}],
                                   limit=100)


@pytest.mark.parametrize("name", ["Iq", "iq", "IQ"])
async def test_iq_filters_like_quiescent_current(name):
    # Iq worked in query text ("LDO Iq < 100nA") and sort_spec, but spec_filters ignored it as
    # "isn't numeric"; it now resolves like "standby current" does
    control = await _iq_search("Quiescent Current")
    result = await _iq_search(name)
    assert "ignored_filters" not in result
    assert control["total"] > 0 and result["total"] == control["total"]
    assert result["results"] == control["results"]
    names = ATTRIBUTE_ALIASES["Quiescent Current"]
    assert all(parse_current(next(v for k, v in p["specs"].items() if k in names)) < 1e-5 for p in result["results"])


async def test_help_still_labels_quiescent_current():
    # jlc_search_help names an attribute by its first alias; Iq must not replace Quiescent Current
    help_reply = await server.jlc_search_help(subcategory="ldo")
    labels = {a["alias"] for a in help_reply["attributes"] if a["name"] in ATTRIBUTE_ALIASES["Quiescent Current"]}
    assert labels == {"Quiescent Current"}


def test_iq_in_the_sent_short_names():
    spec_filters = " ".join(parse_docstring(server.jlc_search).parameters["spec_filters"].split())
    assert "Iout, Iq, Supply Voltage" in spec_filters


@pytest.mark.parametrize("name", ["cse_search", "cse_get_kicad"])
def test_cse_descriptions_promise_no_cap(name):
    # Timeouts are per request phase (httpx) and cse_get_kicad searches, then downloads: no 45 s cap
    sent = " ".join(parse_docstring(getattr(server, name)).description.split())
    assert "45 s" not in sent and "about 15 s" in sent
