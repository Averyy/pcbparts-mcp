"""Stock/price directions on the daily catalog; assert ordering, never fixed part numbers."""

from contextlib import closing
from pathlib import Path
import sys

import pytest

from pcbparts_mcp import server

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline


@pytest.fixture(autouse=True)
async def no_network():
    # The event loop must exist before blocking sockets (Windows uses a socket pair).
    with offline():
        yield


async def search(**kwargs):
    reply = await server.jlc_search(**kwargs)
    assert "error" not in reply, reply
    return reply


def order_key(part, sort_by, order, prefer_no_fee):
    key = [{"full": 0, "same_suffix": 1, "family": 2}.get(part.get("mpn_match"), 0)]
    if prefer_no_fee:
        key.append({"basic": 0, "preferred": 1, "extended": 2}[part["library_type"]])
    if sort_by == "price":
        key.append(part["price"] is None)
        value = part["price"] or 0
    else:
        key.append(not part["specs"])
        value = part["stock"]
    return (*key, -value if order == "desc" else value, part["lcsc"])


@pytest.mark.parametrize("query", ["10k resistor 0603", "LM1117-3.3"])
@pytest.mark.parametrize("sort_by", [None, "stock", "price"])
@pytest.mark.parametrize("prefer_no_fee", [True, False])
async def test_defaults_directions_rankings_and_pages(query, sort_by, prefer_no_fee):
    args = dict(query=query, sort_by=sort_by, prefer_no_fee=prefer_no_fee, min_stock=100)
    natural_order = "asc" if sort_by == "price" else "desc"
    reverse_order = "desc" if sort_by == "price" else "asc"
    default = await search(**args, limit=40)
    natural = await search(**args, sort_order=natural_order, limit=40)
    reverse = await search(**args, sort_order=reverse_order, limit=40)
    assert natural == default
    assert reverse["total"] == default["total"]
    assert reverse["library_type_counts"] == default["library_type_counts"]
    if not default["results"]:
        pytest.skip("no matches in today's catalog")
    for reply, order in ((default, natural_order), (reverse, reverse_order)):
        rows = reply["results"]
        assert rows == sorted(rows, key=lambda p: order_key(p, sort_by, order, prefer_no_fee))
        assert all(p["stock"] >= 100 for p in rows)
        assert "sort" not in reply and all("sort_value" not in p for p in rows)
        first = await search(**args, sort_order=order, limit=20)
        second = await search(**args, sort_order=order, limit=20, offset=20)
        assert first["results"] + second["results"] == rows


@pytest.mark.parametrize("sort_by", [None, "stock", "price"])
@pytest.mark.parametrize("spelling,canonical", [
    ("asc", "asc"), ("ascending", "asc"), ("lowest", "asc"),
    ("desc", "desc"), ("descending", "desc"), ("highest", "desc"),
])
async def test_direction_spellings(sort_by, spelling, canonical):
    args = dict(query="10k resistor 0603", sort_by=sort_by)
    expected = await search(**args, sort_order=canonical)
    assert await search(**args, sort_order=spelling) == expected


async def test_default_stock_direction_without_query_or_sort_by():
    args = dict(subcategory_name="MOSFETs", prefer_no_fee=False, min_stock=100)
    default = await search(**args)
    assert default == await search(**args, sort_by="stock", sort_order="desc")
    ascending = await search(**args, sort_order="asc")
    assert ascending == await search(**args, sort_by="stock", sort_order="asc")
    assert ascending["results"] == sorted(
        ascending["results"], key=lambda p: order_key(p, "stock", "asc", False))


async def test_query_inferred_price_direction_and_explicit_stock_override():
    args = dict(query="cheapest 10k resistor 0603", prefer_no_fee=False)
    price = await search(**args, sort_order="desc")
    assert price == await search(**args, sort_by="price", sort_order="desc")
    assert price["results"] == sorted(
        price["results"], key=lambda p: order_key(p, "price", "desc", False))
    stock = await search(**args, sort_by="stock", sort_order="asc")
    assert stock["results"] == sorted(
        stock["results"], key=lambda p: order_key(p, "stock", "asc", False))


async def test_descending_price_with_any_word_search():
    # Price still precedes the number of matching words, in both directions.
    reply = await search(query="LM1117 AMS1117", match_all_terms=False,
                         sort_by="price", sort_order="desc", prefer_no_fee=False, limit=100)
    assert reply["results"]
    assert reply["results"] == sorted(
        reply["results"], key=lambda p: order_key(p, "price", "desc", False))


@pytest.mark.parametrize("sort_by,order", [("stock", "asc"), ("price", "desc")])
async def test_direction_and_pages_with_python_range_filter(sort_by, order):
    args = dict(subcategory_name="Voltage Regulators - Linear, Low Drop Out (LDO) Regulators",
                spec_filters=[{"name": "Supply Voltage", "op": "=", "value": "12V"}],
                sort_by=sort_by, sort_order=order, prefer_no_fee=False)
    reply = await search(**args, limit=40)
    assert reply["results"]
    assert reply["results"] == sorted(
        reply["results"], key=lambda p: order_key(p, sort_by, order, False))
    first = await search(**args, limit=20)
    second = await search(**args, limit=20, offset=20)
    assert first["results"] + second["results"] == reply["results"]


@pytest.mark.parametrize("order", ["asc", "desc"])
async def test_unpriced_parts_last_in_both_directions(order):
    # Discover examples: prices and stock change daily, and some snapshots have no missing prices.
    with closing(server.get_db()._connect()) as conn:
        unpriced = conn.execute(
            "SELECT lcsc FROM components WHERE price IS NULL AND stock >= 10 LIMIT 1"
        ).fetchone()
        priced = conn.execute(
            "SELECT lcsc FROM components WHERE price IS NOT NULL AND stock >= 10 "
            "GROUP BY price ORDER BY price LIMIT 2"
        ).fetchall()
    if unpriced is None or len(priced) < 2:
        pytest.skip("need both missing and distinct listed prices in today's catalog")
    codes = [unpriced[0], *(row[0] for row in priced)]
    args = dict(query=" ".join(codes), match_all_terms=False, prefer_no_fee=False,
                sort_by="price", sort_order=order)
    reply = await search(**args, limit=100)
    rows = reply["results"]
    assert set(codes) <= {p["lcsc"] for p in rows}
    assert rows[-1]["price"] is None
    assert rows == sorted(rows, key=lambda p: order_key(p, "price", order, False))
    first = await search(**args, limit=1)
    rest = await search(**args, limit=99, offset=1)
    assert first["results"] + rest["results"] == rows
