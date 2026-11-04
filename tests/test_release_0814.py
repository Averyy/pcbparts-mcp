"""0.8.14: digikey_get_part's part number, price breaks and minimum order belong to one packaging.
TPS62130RGTR (prod, 2026-11-04) came back as the 3000-piece reel 296-37682-2-ND with breaks from
3000 at $1.00, next to price $1.99, the cut tape's single-unit price."""

import inspect

import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp.digikey import DigiKeyClient, _normalize_product


def _variation(pn, package, moq, breaks, **extra):
    return {
        "DigiKeyProductNumber": pn,
        "PackageType": {"Id": 0, "Name": package},
        "MinimumOrderQuantity": moq,
        "StandardPricing": [{"BreakQuantity": q, "UnitPrice": p, "TotalPrice": q * p} for q, p in breaks],
        "MarketPlace": False,
        "DigiReelFee": 0.0,
        **extra,
    }


# In DigiKey's order: the reel first, as for the reported part
REEL = _variation("296-37682-2-ND", "Tape & Reel (TR)", 3000, [(3000, 1.00483), (6000, 0.98422)])
CUT = _variation("296-37682-1-ND", "Cut Tape (CT)", 1, [(1, 1.99), (10, 1.47), (25, 1.34)])
DIGI = _variation("296-37682-6-ND", "Digi-Reel®", 1, [(1, 1.99), (10, 1.47)], DigiReelFee=7.0)
PRODUCT = {
    "ManufacturerProductNumber": "TPS62130RGTR",
    "Manufacturer": {"Name": "Texas Instruments"},
    "UnitPrice": 1.99,
    "QuantityAvailable": 0,
    "ProductVariations": [REEL, DIGI, CUT],
    "Parameters": [],
}


class TestPackaging:
    def test_mpn_gets_the_smallest_order(self):
        result = _normalize_product(PRODUCT, "TPS62130RGTR")
        assert result["part_number"] == "296-37682-1-ND" and result["packaging"] == "Cut Tape (CT)"
        assert (result["price"], result["min_qty"]) == (1.99, 1)
        assert result["price_breaks"][0] == {"qty": 1, "price": 1.99}
        assert "reel_fee" not in result
        # Cut tape before the Digi-Reel: both sell one, but a Digi-Reel adds its reel fee
        assert result["other_packaging"] == [
            {"part_number": "296-37682-2-ND", "packaging": "Tape & Reel (TR)", "min_qty": 3000, "price": 1.00483},
            {"part_number": "296-37682-6-ND", "packaging": "Digi-Reel®", "min_qty": 1, "price": 1.99, "reel_fee": 7.0},
        ]

    @pytest.mark.parametrize("asked", ["296-37682-2-ND", "296-37682-2-nd "])
    def test_digikey_number_gets_that_packaging(self, asked):
        result = _normalize_product(PRODUCT, asked)
        assert result["part_number"] == "296-37682-2-ND"
        assert (result["price"], result["min_qty"]) == (1.00483, 3000)
        assert result["price_breaks"][0]["qty"] == 3000
        assert {o["part_number"] for o in result["other_packaging"]} == {"296-37682-1-ND", "296-37682-6-ND"}

    def test_digi_reel_asked_for_shows_its_fee(self):
        result = _normalize_product(PRODUCT, "296-37682-6-ND")
        assert result["packaging"] == "Digi-Reel®" and result["reel_fee"] == 7.0

    def test_digikey_stock_before_marketplace(self):
        market = _variation("2368-TPS62130RGTR-ND", "Bulk", 1, [(1, 2.5)], MarketPlace=True)
        product = {**PRODUCT, "ProductVariations": [REEL, market, CUT]}
        result = _normalize_product(product, "TPS62130RGTR")
        assert result["part_number"] == "296-37682-1-ND" and "marketplace" not in result
        assert {"part_number": "2368-TPS62130RGTR-ND", "packaging": "Bulk", "min_qty": 1, "price": 2.5,
                "marketplace": True} in result["other_packaging"]
        # A smaller order still wins over DigiKey's own reel
        result = _normalize_product({**PRODUCT, "ProductVariations": [REEL, market]}, "TPS62130RGTR")
        assert result["part_number"] == "2368-TPS62130RGTR-ND" and result["marketplace"] is True

    def test_one_packaging(self):
        result = _normalize_product({**PRODUCT, "ProductVariations": [CUT]}, "TPS62130RGTR")
        assert result["part_number"] == "296-37682-1-ND" and "other_packaging" not in result

    def test_no_pricing_falls_back_to_unit_price(self):
        bare = {**CUT, "StandardPricing": []}
        result = _normalize_product({**PRODUCT, "ProductVariations": [bare]})
        assert (result["price"], result["price_breaks"]) == (1.99, [])


class TestClientPassesTheNumber:
    async def test_get_part(self):
        client = DigiKeyClient("id", "secret")

        async def fake_request(method, path, **kwargs):
            return {"Product": PRODUCT}

        client._request = fake_request
        result = (await client.get_part("296-37682-2-ND"))["results"][0]
        assert result["part_number"] == "296-37682-2-ND" and result["min_qty"] == 3000

    def test_docstring(self):
        doc = inspect.getdoc(server.digikey_get_part)
        assert "other_packaging" in doc and "smallest order" in doc
