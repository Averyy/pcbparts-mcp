"""`preferred` means the same in jlc_search and jlc_get_part (2026-10-31 report: C1671, C14663
and C8218 were preferred=true in search and false in jlc_get_part)."""

import sqlite3

import pytest

from pcbparts_mcp.client import JLCPCBClient
from pcbparts_mcp.search.result import row_to_dict

API_LIBRARY = {  # library_type code in the local DB -> JLCPCB API fields
    "b": {"componentLibraryType": "base", "preferredComponentFlag": False},
    "p": {"componentLibraryType": "expand", "preferredComponentFlag": True},
    "e": {"componentLibraryType": "expand", "preferredComponentFlag": False},
}


def _row(library_type: str) -> sqlite3.Row:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return conn.execute(
        "SELECT 'C1671' AS lcsc, 'CL10C470JB8NNNC' AS mpn, 'Samsung' AS manufacturer, '0603' AS package, "
        "1000 AS stock, 0.001 AS price, ? AS library_type, 2929 AS subcategory_id, '' AS description, "
        "'[]' AS attributes",
        (library_type,),
    ).fetchone()


@pytest.mark.parametrize("code, expected", [("b", False), ("p", True), ("e", False)])
def test_search_and_get_part_agree(code, expected):
    searched = row_to_dict(_row(code), {})
    looked_up = JLCPCBClient()._transform_part({"componentCode": "C1671", **API_LIBRARY[code]}, slim=False)
    assert searched["preferred"] is looked_up["preferred"] is expected
    assert searched["library_type"] == looked_up["library_type"]
