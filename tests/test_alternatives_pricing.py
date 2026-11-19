"""Order savings use live original tiers and batched snapshot replacement tiers, offline."""

import json
from pathlib import Path
import sys

import pytest

from conftest import write_catalog_category
from pcbparts_mcp.alternatives import build_response, unit_price_at_quantity
from pcbparts_mcp.catalog_files import PRICE_TIERS_FILE, write_price_tiers
from pcbparts_mcp.client import JLCPCBClient
from pcbparts_mcp.db import ComponentDatabase

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from build_database import build_database  # noqa: E402
from search_baseline import offline  # noqa: E402


AS_OF = "2026-11-17T22:00:00Z"
ORIGINAL_TIERS = [{"qty": "1000+", "price": 0.09}, {"qty": "1+", "price": 0.2},
                  {"qty": "100+", "price": 0.12}]  # selection must not depend on order
TIERS = {"C2": "1:0.11,100:0.08,1000:0.06", "C3": "1:0.13,100:0.01"}


@pytest.fixture
def pricing_db(tmp_path):
    rows = [{"l": code, "m": code, "f": "Maker", "p": "0402", "s": 5000,
             "t": "b", "c": 2, "$": price, "d": "10k resistor", "a": [["Resistance", "10kΩ"]]}
            for code, price in [("C2", 0.1), ("C3", 0.13)]]
    write_catalog_category(tmp_path, "resistors", rows)
    (tmp_path / "subcategories.json").write_text(json.dumps({
        "2": {"name": "Chip Resistor - Surface Mount", "category_id": 1, "category_name": "Resistors"},
    }), encoding="utf-8")
    write_price_tiers(tmp_path / "catalog" / PRICE_TIERS_FILE, TIERS, AS_OF)
    build_database(tmp_path, tmp_path / "components.db", verbose=False)
    database = ComponentDatabase(db_path=tmp_path / "components.db", data_dir=tmp_path)
    yield database
    database.close()


@pytest.fixture
async def pricing(pricing_db, monkeypatch):
    original = {"lcsc": "C1", "price": 0.2, "prices": ORIGINAL_TIERS,
                "library_type": "extended", "package": "0402", "manufacturer": "Maker",
                "subcategory": "Chip Resistor - Surface Mount", "specs": {"Resistance": "10kΩ"}}
    parts = list(pricing_db.get_by_lcsc_batch(["C2", "C3"]).values())
    client = JLCPCBClient()
    client.set_categories(pricing_db.get_categories_for_client())
    client.set_alternative_price_tiers(pricing_db.get_price_tiers, pricing_db.price_tiers_as_of())

    async def get_part(lcsc):
        return original

    async def search(**kwargs):
        return {"results": parts}

    monkeypatch.setattr(client, "get_part", get_part)
    monkeypatch.setattr(client, "search", search)
    with offline():
        try:
            yield client, original, parts, pricing_db
        finally:
            await client.close()


@pytest.mark.parametrize("boards,original_price,replacement_price", [
    (20, 0.2, 0.1), (25, 0.12, 0.08), (100, 0.12, 0.08),
    (250, 0.09, 0.06), (500, 0.09, 0.06),
], ids=["below", "at", "between", "last", "above"])
async def test_order_quantity_tiers(pricing, boards, original_price, replacement_price):
    client, original, parts, _ = pricing
    result = await client.find_alternatives("C1", board_quantity=boards, placements_per_board=4)
    savings = result["comparison"]["savings"]
    assert savings["component_quantity"] == boards * 4
    assert savings["original_unit_price_at_quantity"] == original_price
    assert savings["replacement_unit_price_at_quantity"] == replacement_price
    assert savings["unit_price_diff_at_quantity"] == pytest.approx(original_price - replacement_price)
    assert savings["order_total"] == pytest.approx(round(3 + (original_price - replacement_price) * boards * 4, 4))
    # Below both parts' second break (80 pieces) each uses its own qty-1 price, not its first break's
    below = boards * 4 < 100
    assert savings["price_basis"] == ("qty 1" if below else "price breaks at component_quantity")
    assert savings["price_tiers_as_of"] == (None if below else AS_OF)
    assert savings["unit_price_diff"] == 0.1  # weekly qty-1 price stays separate from daily tiers
    assert [part["lcsc"] for part in result["alternatives"]] == ["C2", "C3"]
    assert [part["score_breakdown"]["price"] for part in result["alternatives"]] == [10, 7]
    assert result["original"] == original
    for row, part in zip(result["alternatives"], parts):
        assert all(row[key] == value for key, value in part.items())
    assert result["comparison"]["original"]["price"] == 0.2
    assert result["comparison"]["recommended"]["price"] == 0.1


async def test_all_listed_candidates_tiers_take_one_query(pricing):
    client, _, _, database = pricing
    queries = []
    database._conn.set_trace_callback(queries.append)
    try:
        result = await client.find_alternatives("C1", board_quantity=100)
    finally:
        database._conn.set_trace_callback(None)
    reads = [query for query in queries if "FROM price_tiers" in query]
    assert len(result["alternatives"]) == 2
    assert len(reads) == 1
    assert "'C2'" in reads[0] and "'C3'" in reads[0]
    assert result["comparison"]["savings"]["order_total"] == 7


@pytest.mark.parametrize("missing", ["replacement", "original", "empty", "null", "snapshot", "failed"])
async def test_missing_tiers_fall_back_for_both(pricing, monkeypatch, missing):
    client, original, _, database = pricing
    if missing == "replacement":
        client.set_alternative_price_tiers(lambda codes: {"C3": TIERS["C3"]}, AS_OF)
    elif missing == "snapshot":
        monkeypatch.setattr(database, "_price_tiers_as_of", None)
        client.set_alternative_price_tiers(database.get_price_tiers, None)
    elif missing == "failed":
        def fail(codes):
            raise RuntimeError("unavailable")
        client.set_alternative_price_tiers(fail, AS_OF)
    elif missing == "original":
        original.pop("prices")
    else:
        original["prices"] = [] if missing == "empty" else None
    result = await client.find_alternatives("C1", board_quantity=100, placements_per_board=4)
    savings = result["comparison"]["savings"]
    assert savings["price_basis"] == "qty 1"
    assert savings["original_unit_price_at_quantity"] == 0.2
    assert savings["replacement_unit_price_at_quantity"] == 0.1
    assert savings["unit_price_diff_at_quantity"] == savings["unit_price_diff"] == 0.1
    assert savings["order_total"] == 43
    assert savings["price_tiers_as_of"] is None  # no breaks used: nothing they date


async def test_existing_reply_fields_remain(pricing):
    client, _, _, _ = pricing
    result = await client.find_alternatives("C1")
    assert set(result) == {"original", "alternatives", "unverified_alternatives", "summary",
                           "comparison", "confidence", "search_criteria"}
    assert set(result["comparison"]) == {"original", "recommended", "savings"}
    assert set(result["comparison"]["original"]) == {"lcsc", "library_type", "price", "stock"}
    assert set(result["comparison"]["recommended"]) == {"lcsc", "library_type", "price", "stock"}
    assert {"assembly_fee", "is_estimate", "assembly_service_assumption", "loading_fee_per_extended_type_estimate_usd",
            "fee_basis", "unit_price_diff", "board_quantity", "placements_per_board", "component_quantity",
            "order_total", "note"} <= result["comparison"]["savings"].keys()
    assert {"found", "unverified_count", "extended_count", "basic_preferred_count", "message",
            "is_supported_category", "price_note", "stages"} <= result["summary"].keys()


@pytest.mark.parametrize("price,tiers,quantity,expected", [
    (0.2, [], 100, 0.2), (None, [], 100, None), (0.2, [(100, 0.1)], 50, 0.2),
    (0.2, [(1000, 0.05), (1, 0.2), (100, 0.1)], 100, 0.1),
], ids=["none", "unknown", "before", "unsorted"])
def test_unit_price_at_quantity(price, tiers, quantity, expected):
    assert unit_price_at_quantity(price, tiers, quantity) == expected


@pytest.mark.parametrize("missing_price", ["original", "replacement"])
def test_unknown_qty_one_price_keeps_null_total(missing_price):
    original = {"lcsc": "C1", "price": None if missing_price == "original" else 0.2}
    candidate = {"lcsc": "C2", "price": None if missing_price == "replacement" else 0.1}
    result = build_response(original, [(0, candidate, {}, {"specs_verified": [], "specs_unparseable": []})],
                            "Chip Resistor - Surface Mount", "Resistance", "10kΩ", 10)
    savings = result["comparison"]["savings"]
    assert savings["unit_price_diff"] is None
    assert savings["unit_price_diff_at_quantity"] is None
    assert savings["order_total"] is None
    assert savings["price_basis"] == "qty 1"


def test_unreadable_live_tiers_are_skipped():
    from pcbparts_mcp.alternatives import _live_tiers

    prices = [{"qty": "1+", "price": 0.02}, {"qty": "None+", "price": 0.01}, {"qty": "100+"},
              {"price": 0.005}, {"qty": 500, "price": "0.004"}, "junk", {"qty": "0+", "price": 0.001}]
    assert _live_tiers(prices) == [(1, 0.02), (500, 0.004)]
    assert _live_tiers(None) == [] and _live_tiers("1+") == []


def _savings(original_prices, packed, quantity=1, original_price=0.2, replacement_price=0.1):
    original = {"lcsc": "C1", "price": original_price, "prices": original_prices, "library_type": "extended"}
    candidate = {"lcsc": "C2", "price": replacement_price, "library_type": "basic"}
    result = build_response(original, [(0, candidate, {}, {"specs_verified": [], "specs_unparseable": []})],
                            "Chip Resistor - Surface Mount", "Resistance", "10kΩ", 10, board_quantity=quantity,
                            candidate_price_tiers={"C2": packed} if packed is not None else {}, price_tiers_as_of=AS_OF)
    return result["comparison"]["savings"]


def test_quantity_one_uses_each_parts_own_price():
    """The snapshot's first break is the daily scrape's (0.11), the candidate's price the weekly or
    a live one (0.1): at the default quantity the order total must equal assembly_fee + unit_price_diff."""
    savings = _savings(ORIGINAL_TIERS, TIERS["C2"])
    assert (savings["original_unit_price_at_quantity"], savings["replacement_unit_price_at_quantity"]) == (0.2, 0.1)
    assert savings["order_total"] == savings["assembly_fee"] + savings["unit_price_diff"] == 3.1
    assert (savings["price_basis"], savings["price_tiers_as_of"]) == ("qty 1", None)


def test_one_part_past_its_first_break():
    """At 60 the original is on its 50+ break while the replacement is below its second (100):
    the replacement keeps its own qty-1 price."""
    savings = _savings([{"qty": "1+", "price": 0.2}, {"qty": "50+", "price": 0.15}], TIERS["C2"], quantity=60)
    assert (savings["original_unit_price_at_quantity"], savings["replacement_unit_price_at_quantity"]) == (0.15, 0.1)
    assert (savings["price_basis"], savings["price_tiers_as_of"]) == ("price breaks at component_quantity", AS_OF)
    assert savings["order_total"] == pytest.approx(3 + 0.05 * 60)


@pytest.mark.parametrize("packed", ["1:0.1,x:0.05", "garbage", "1:0.1,100"], ids=["qty", "text", "half"])
def test_unreadable_snapshot_tiers_fall_back_to_qty_one(packed):
    """A damaged price_tiers row raised ValueError out of build_response (the whole call failed)."""
    savings = _savings(ORIGINAL_TIERS, packed, quantity=500)
    assert (savings["price_basis"], savings["price_tiers_as_of"]) == ("qty 1", None)
    assert (savings["original_unit_price_at_quantity"], savings["replacement_unit_price_at_quantity"]) == (0.2, 0.1)


@pytest.mark.parametrize("packed", ["1:0.1,100:nan,1000:0.05", "1:0.1,100:-0.01,1000:0.05"], ids=["nan", "negative"])
def test_a_bad_snapshot_break_is_skipped(packed):
    savings = _savings(ORIGINAL_TIERS, packed, quantity=500)
    assert savings["replacement_unit_price_at_quantity"] == 0.1  # 100+ skipped: below its next break, own price
    assert savings["price_basis"] == "price breaks at component_quantity"  # the original's 100+ break


def test_live_tiers_skip_prices_that_arent_finite_or_are_negative():
    from pcbparts_mcp.alternatives import _live_tiers

    prices = [{"qty": "1+", "price": 0.02}, {"qty": "10+", "price": float("nan")}, {"qty": "20+", "price": "inf"},
              {"qty": "50+", "price": -0.01}, {"qty": "100+", "price": 0.01}]
    assert _live_tiers(prices) == [(1, 0.02), (100, 0.01)]


@pytest.mark.parametrize("quantities", [{"board_quantity": 10 ** 200}, {"placements_per_board": 1_000_001},
                                        {"board_quantity": 10 ** 7, "placements_per_board": 10 ** 7}],
                         ids=["boards", "placements", "both"])
async def test_order_quantities_are_capped(pricing, quantities):
    """10**200 boards overflowed the order total's float (an internal error, not a reply)."""
    from pcbparts_mcp.server import _error_kind

    client, _, _, _ = pricing
    reply = await client.find_alternatives("C1", **quantities)
    assert reply == {"error": "board_quantity and placements_per_board must be at most 1,000,000 each"}
    assert _error_kind(reply["error"]) == "bad_request"
    savings = (await client.find_alternatives("C1", board_quantity=10 ** 6, placements_per_board=10 ** 6))["comparison"]["savings"]
    assert savings["component_quantity"] == 10 ** 12 and savings["order_total"] == pytest.approx(3 + 0.03 * 10 ** 12)


async def test_the_server_wires_the_snapshot_tiers(pricing_db, monkeypatch):
    """The real startup (lifespan) hands the database's batch tier lookup and its date to the client,
    so a jlc_find_alternatives call through the server prices at quantity from the snapshot."""
    from fastmcp import Client
    import pcbparts_mcp.server as server

    original = {"lcsc": "C1", "price": 0.2, "prices": ORIGINAL_TIERS, "library_type": "extended", "package": "0402",
                "manufacturer": "Maker", "subcategory": "Chip Resistor - Surface Mount", "specs": {"Resistance": "10kΩ"}}
    parts = list(pricing_db.get_by_lcsc_batch(["C2", "C3"]).values())

    async def get_part(self, lcsc):
        return dict(original)

    async def search(self, **kwargs):
        return {"results": parts}

    monkeypatch.setattr(server, "get_db", lambda: pricing_db)
    monkeypatch.setattr(JLCPCBClient, "get_part", get_part)
    monkeypatch.setattr(JLCPCBClient, "search", search)
    with offline():
        async with Client(server.mcp) as client:
            assert server._client._alternative_price_tiers == pricing_db.get_price_tiers
            reply = (await client.call_tool("jlc_find_alternatives", {"lcsc": "C1", "board_quantity": 250})).structured_content
            # /health says which breaks the server runs with (a failed artifact download shows as none)
            health = json.loads((await server.health(None)).body)
            assert health["price_tiers"] == {"as_of": AS_OF, "parts": 2}
    savings = reply["comparison"]["savings"]
    assert (savings["price_basis"], savings["price_tiers_as_of"]) == ("price breaks at component_quantity", AS_OF)
    assert (savings["original_unit_price_at_quantity"], savings["replacement_unit_price_at_quantity"]) == (0.12, 0.08)
