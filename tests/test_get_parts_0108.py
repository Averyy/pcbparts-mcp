"""BOM identity warnings and datasheet links on current snapshot codes, without network."""

from types import SimpleNamespace

import pytest

from pcbparts_mcp import server
from pcbparts_mcp.db import ComponentDatabase


@pytest.fixture
def catalog(monkeypatch):
    db = ComponentDatabase()
    if not db.db_path.exists():
        pytest.skip("catalog database unavailable")
    monkeypatch.setattr(server, "get_db", lambda: db)
    monkeypatch.setattr(server, "_client", SimpleNamespace())
    monkeypatch.setattr(server, "_distributor_store", None)
    try:
        rows = db.get_by_mpn("CL05B104KO5NNNC", full_text=False)
        if not rows:
            pytest.skip("reference capacitor is absent from this snapshot")
        yield db, rows[0]
    finally:
        db.close()


async def test_code_with_wrong_identity(catalog):
    _, part = catalog
    given = {"lcsc": part["lcsc"], "mpn": "BUZZER-ZZQ9981", "manufacturer": "Wrong maker"}
    reply = await server.jlc_get_parts([given])
    row, = reply["results"]
    assert row["mismatch"] == {"mpn": given["mpn"], "manufacturer": given["manufacturer"]}
    assert "BOM" in row["note"]
    assert row["model"] == part["model"]
    assert reply["counts"] == {"found": 1, "gone": 0, "not_found": 0, "error": 0}


async def test_code_datasheet_link(catalog, monkeypatch):
    _, part = catalog
    if part.get("no_datasheet"):
        pytest.skip("reference part no longer has a datasheet")
    monkeypatch.setattr(server, "_datasheet_link_base", lambda: "https://parts.example")
    row, = (await server.jlc_get_parts([part["lcsc"]]))["results"]
    assert row["datasheet_pdf"] == f"https://parts.example/mcp/datasheet/{part['lcsc']}"


async def test_only_disagreeing_fields_are_reported(catalog):
    _, part = catalog
    entries = [
        {"lcsc": part["lcsc"], "mpn": "BUZZER-ZZQ9981", "manufacturer": part["manufacturer"]},
        {"lcsc": part["lcsc"], "mpn": part["model"], "manufacturer": "Wrong maker"},
        {"lcsc": part["lcsc"], "mpn": part["model"].lower(), "manufacturer": "Samsung"},
        {"lcsc": part["lcsc"], "mpn": "CL-05B104KO5NNNC", "manufacturer": part["manufacturer"]},
    ]
    reply = await server.jlc_get_parts(entries)
    first, second, same, separated = reply["results"]
    assert first["mismatch"] == {"mpn": "BUZZER-ZZQ9981"}
    assert second["mismatch"] == {"manufacturer": "Wrong maker"}
    assert "mismatch" not in same and "mismatch" not in separated
    assert reply["counts"] == {"found": 4, "gone": 0, "not_found": 0, "error": 0}
    assert all(row["lcsc"] == part["lcsc"] for row in reply["results"])


@pytest.mark.parametrize("given,model,maker", [
    ("LM358PWT", "LM358PWR", "Texas Instruments"),
    ("MCP73831-2ACI/MC", "MCP73831T-2ACI/MC", "Microchip Tech"),
    ("SCD-41", "SCD41-D-R2", "Sensirion"),
    ("NRF24L01+", "NRF24L01P-R", "Nordic Semicon"),
], ids=["reel", "insert_t", "alias", "plus"])
async def test_packing_and_aliases_are_not_mismatches(catalog, given, model, maker):
    db, _ = catalog
    rows = db.get_by_mpn(model, full_text=False, maker=lambda name: server.makers_match(name, maker))
    if not rows:
        pytest.skip("reference ordering code is absent from this snapshot")
    part = rows[0]
    row, = (await server.jlc_get_parts([{"lcsc": part["lcsc"], "mpn": given, "manufacturer": maker}]))["results"]
    assert "mismatch" not in row
    assert row["model"] == part["model"]


async def test_different_grade_is_a_mismatch(catalog):
    db, _ = catalog
    rows = db.get_by_mpn("LM358DR", full_text=False)
    if not rows:
        pytest.skip("reference op amp is absent from this snapshot")
    row, = (await server.jlc_get_parts([{"lcsc": rows[0]["lcsc"], "mpn": "LM358ADR"}]))["results"]
    assert row["mismatch"] == {"mpn": "LM358ADR"}


async def test_unknown_code_has_no_identity_warning(catalog):
    db, _ = catalog
    code = "C999999999999"
    if db.get_part_snapshot(code, gone=True):
        pytest.skip("unused code is now listed")
    reply = await server.jlc_get_parts([{"lcsc": code, "mpn": "BUZZER-ZZQ9981", "manufacturer": "Wrong maker"}])
    row, = reply["results"]
    assert row["not_found"] and "mismatch" not in row
    assert reply["counts"] == {"found": 0, "gone": 0, "not_found": 1, "error": 0}


@pytest.mark.parametrize("mode", ["host", "public", "direct", "outside"], ids=["host", "public", "direct", "outside"])
async def test_batch_link_modes(catalog, monkeypatch, mode):
    _, part = catalog
    if part.get("no_datasheet"):
        pytest.skip("reference part no longer has a datasheet")
    request = SimpleNamespace(headers={"host": "internal:8080"}, url=SimpleNamespace(scheme="http"))

    def get_request():
        if mode == "outside":
            raise RuntimeError("No HTTP request")
        return request

    monkeypatch.setattr(server, "get_http_request", get_request)
    monkeypatch.setattr(server, "DATASHEET_LINK_BASE", {"host": "", "public": "https://parts.example",
                                                     "direct": "direct", "outside": "https://parts.example"}[mode])
    row, = (await server.jlc_get_parts([part["lcsc"]]))["results"]
    if mode in ("direct", "outside"):
        assert "datasheet_pdf" not in row
    else:
        base = "http://internal:8080" if mode == "host" else "https://parts.example"
        assert row["datasheet_pdf"] == f"{base}/mcp/datasheet/{part['lcsc']}"


async def test_no_datasheet_and_mpn_rows(catalog, monkeypatch):
    db, part = catalog
    monkeypatch.setattr(server, "_datasheet_link_base", lambda: "https://parts.example")
    read_rows = db.get_snapshot_rows

    def no_datasheet(codes):
        return {code: {**row, "no_datasheet": True} if row else row for code, row in read_rows(codes).items()}

    monkeypatch.setattr(db, "get_snapshot_rows", no_datasheet)
    code_row, mpn_row = (await server.jlc_get_parts([part["lcsc"], {"mpn": part["model"]}]))["results"]
    assert code_row["no_datasheet"] and "datasheet_pdf" not in code_row
    assert mpn_row["results"] and all("datasheet_pdf" not in row for row in mpn_row["results"])
