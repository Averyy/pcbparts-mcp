"""Attribute coverage keeps exact shares without scanning for arbitrary names."""

import json
import sqlite3
from contextlib import closing

import pytest

from pcbparts_mcp.db import ComponentDatabase
from pcbparts_mcp.search.spec_filter import like_text


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "components.db"
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("CREATE TABLE components (subcategory_id INTEGER, attributes TEXT)")
        conn.execute("CREATE TABLE subcategories (id INTEGER, category_id INTEGER, name TEXT, category_name TEXT)")
        conn.execute("CREATE TABLE categories (id INTEGER, name TEXT, slug TEXT)")
        conn.executemany("INSERT INTO components VALUES (?, ?)", [
            (1, json.dumps([["Resistance", "10kΩ"], ["Absent", "-"], ["ÄSpec", "2"]], ensure_ascii=False)),
            (1, json.dumps([["Resistance", "-"], ["Tolerance", "1%"]])),
            (2, json.dumps([["Resistance", "1kΩ"], ["Name_%", "3"]])),
        ])
    database = ComponentDatabase(db_path=path)
    database._ensure_db()
    yield database
    database.close()


@pytest.mark.parametrize("ids,names", [
    ([1], ["Resistance"]), ([1, 2], ["resistance"]),
    ([1], ["Resistance", "Tolerance"]), ([2], ["Name_%"]),
    ([1], ["ÄSpec"]), ([1], ["äspec"]),
])
def test_real_attribute_shares_match_like_computation(database, ids, names):
    stated = " OR ".join("(attributes LIKE ? ESCAPE '\\' AND attributes NOT LIKE ? ESCAPE '\\')" for _ in names)
    params = []
    for name in names:
        params += [f'%"{like_text(name)}", "%', f'%"{like_text(name)}", "-"]%']
    row = database._conn.execute(
        f"SELECT COUNT(*), SUM(CASE WHEN {stated} THEN 1 ELSE 0 END) FROM components "
        f"WHERE subcategory_id IN ({','.join('?' * len(ids))})", [*params, *ids],
    ).fetchone()
    assert database.attribute_share(ids, names) == (row[1] or 0) / row[0]


def test_unknown_names_skip_like_scan_and_share_cache(database):
    queries = []
    database._conn.set_trace_callback(queries.append)
    for i in range(50):
        assert database.attribute_share([1, 2], [f"Bogus {i}"]) == 0.0
    assert database.attribute_share([1], ["Absent"]) == 0.0
    assert not any(" LIKE " in query for query in queries)
    assert database._attribute_shares == {}
    assert len([query for query in queries if query.startswith("SELECT attributes FROM components")]) == 2
