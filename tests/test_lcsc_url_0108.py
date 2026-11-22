"""Malformed upstream product links fall back to the LCSC code's product page."""

from pcbparts_mcp.client import JLCPCBClient
import pytest


def test_doubled_scheme():
    reply = JLCPCBClient()._transform_part({
        "componentCode": "C176862",
        "lcscGoodsUrl": "https://lcsc.comhttps://lcsc.com/product-detail/C176862.html",
    }, slim=False)
    assert reply["lcsc_url"] == "https://www.lcsc.com/product-detail/C176862.html"


@pytest.mark.parametrize("value", [
    "http://lcsc.com/product-detail/C176862.html", "https://www.lcsc.com/product-detail/part_C176862.html",
    "HTTPS://LCSC.COM/product-detail/C176862.html", "https://www.lcsc.com:443/product-detail/C176862.html",
], ids=["http", "www", "case", "port"])
def test_valid_links_stay(value):
    result = JLCPCBClient()._transform_part({"componentCode": "C176862", "lcscGoodsUrl": value}, slim=False)
    assert result["lcsc_url"] == value


@pytest.mark.parametrize("value", [
    None, "", "//lcsc.com/x", "ftp://lcsc.com/x", "https://lcsc.com.evil.example/x",
    "https://evil.example/lcsc.com", "https://user@lcsc.com/x", "https://lcsc.com/https://lcsc.com/x",
    "https://lcsc.com/HTTP://lcsc.com/x", "https://lcsc.com:bad/x", "https://lcsc.com:99999/x",
    "https://lcsc.com/has space", "https://lcsc.com/\nfile", "https://lcsc.com\\other", "https://[broken",
    {"url": "https://lcsc.com/x"},
], ids=["null", "empty", "relative", "scheme", "suffix", "foreign", "user", "embedded", "upper",
        "port", "port_range", "space", "newline", "backslash", "bracket", "object"])
def test_bad_links_use_code(value):
    result = JLCPCBClient()._transform_part({"componentCode": "C176862", "lcscGoodsUrl": value}, slim=False)
    assert result["lcsc_url"] == "https://www.lcsc.com/product-detail/C176862.html"


def test_missing_url_and_code_still_null():
    assert JLCPCBClient()._transform_part({}, slim=False)["lcsc_url"] is None
