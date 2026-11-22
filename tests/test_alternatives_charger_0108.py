"""Charge/protection setpoints are required matches; every probe runs offline."""

from pathlib import Path
import sys

from fastmcp import Client
import pytest

from pcbparts_mcp import db, server
from pcbparts_mcp.alternatives import is_compatible_alternative
from pcbparts_mcp.client import JLCPCBClient

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import local_alternatives, offline


CHARGE = "Charging Saturation Voltage"
CUTOFF = "End-Off Voltage"


def battery(code="C424093", **overrides):
    # Frozen MCP73831T-2ACI/OT catalog attributes, independent of daily stock.
    specs = {
        "Type of Battery": "Lithium Battery", "Number of Cells": "1",
        "The Chip Type": "Charging IC", "Voltage - Supply": "3.75V~6V",
        "Interface": "-", "Charge Current - Max": "550mA",
        CHARGE: "4.2V", CUTOFF: "-",
    }
    specs.update(overrides)
    return {
        "lcsc": code, "model": code, "subcategory": "Battery Management",
        "package": "SOT-23-5", "library_type": "extended", "stock": 1000,
        "price": 1.0, "specs": {k: v for k, v in specs.items() if v is not None},
    }


def check(original, candidate):
    return is_compatible_alternative(original, candidate, "Battery Management")


@pytest.mark.parametrize("voltage", ["4.20V", "4200mV", "0.0042kV", " 4.2v "],
                         ids=["decimal", "mv", "kv", "case"])
def test_equivalent_charge_voltage_formats(voltage):
    compatible, info = check(battery(), battery(**{CHARGE: voltage}))
    assert compatible
    assert CHARGE in info["specs_verified"]
    assert info["unverified_requirements"] == []


@pytest.mark.parametrize("voltage", ["4.1V", "4.208V", "4.21V", "4.25V", "4.28V", "4.5V"])
def test_charge_voltage_has_no_rating_tolerance(voltage):
    assert not check(battery(), battery(**{CHARGE: voltage}))[0]


@pytest.mark.parametrize("field,original,candidate", [
    (CHARGE, "4.28V", "4.3V"),
    (CUTOFF, "2.8V", "2.85V"),
    (CUTOFF, "2.8V", "2.75V"),
], ids=["overcharge", "cutoff-higher", "cutoff-lower"])
def test_protection_thresholds_must_match(field, original, candidate):
    # Protection ICs use the same catalog fields (e.g. FH8261G3M, C5159068).
    part = battery(**{"The Chip Type": "Protection IC", field: original})
    alternative = {**part, "specs": {**part["specs"], field: candidate}}
    assert not check(part, alternative)[0]


@pytest.mark.parametrize("field", [CHARGE, CUTOFF], ids=["charge", "cutoff"])
@pytest.mark.parametrize("value", [None, "", "-", "unknown", "4.2", "4.2V~4.5V",
                                   "4.2V、unknown", "4.2V trailing"],
                         ids=["absent", "empty", "dash", "unknown", "unitless", "range", "partial", "text"])
def test_unknown_candidate_setpoint_is_required_but_unverified(field, value):
    compatible, info = check(battery(**{field: "4.2V"}), battery(**{field: value}))
    assert compatible
    assert field in info["unverified_requirements"]
    assert field in info["specs_unparseable"]
    assert field not in info["specs_verified"]


@pytest.mark.parametrize("field", [CHARGE, CUTOFF], ids=["charge", "cutoff"])
def test_unreadable_original_setpoint_is_unverified(field):
    compatible, info = check(battery(**{field: "unknown"}), battery(**{field: "4.2V"}))
    assert compatible
    assert field in info["unverified_requirements"]


@pytest.mark.parametrize("value", [None, "", "-"], ids=["absent", "empty", "dash"])
def test_unstated_original_setpoints_do_not_add_requirements(value):
    compatible, info = check(battery(**{CHARGE: value, CUTOFF: value}), battery())
    assert compatible
    assert not {CHARGE, CUTOFF}.intersection(info["specs_verified"] + info["specs_unparseable"])
    assert info["unverified_requirements"] == []


@pytest.mark.parametrize("original,candidate,expected", [
    ("4.2V", "4.2V、4.35V", False),
    ("4.2V、4.35V", "4.2V", False),
    ("4.2V、4.35V", "4.2V、4.5V", False),
    ("4.2V、4.35V", "4350mV、4.20V", True),
], ids=["extra", "missing", "different", "same"])
def test_every_listed_setpoint_must_match(original, candidate, expected):
    compatible, info = check(battery(**{CHARGE: original}), battery(**{CHARGE: candidate}))
    assert compatible is expected
    if expected:
        assert CHARGE in info["specs_verified"]
        assert info["unverified_requirements"] == []


@pytest.mark.parametrize("chip_type", ["Protection IC", "Charging IC、Protection IC"],
                         ids=["protection", "combined"])
def test_charge_voltage_cannot_override_a_different_chip_type(chip_type):
    assert not check(battery(), battery(**{"The Chip Type": chip_type}))[0]


@pytest.mark.parametrize("source", ["live", "snapshot"])
async def test_candidate_lists_and_savings_enforce_required_setpoints(monkeypatch, source):
    original = battery()
    rows = [
        battery("C100", **{CHARGE: "4.20V"}),
        battery("C101", **{CHARGE: "4.5V"}),
        battery("C102", **{CHARGE: "4.21V"}),
        battery("C103", **{CHARGE: None}),
        battery("C104", **{CHARGE: "unknown"}),
        battery("C105", **{"The Chip Type": "Protection IC"}),
        battery("C106", **{"The Chip Type": None}),
    ]
    client = JLCPCBClient()

    async def get_part(lcsc):
        return original

    async def search(**kwargs):
        return {"results": rows} if source == "live" else {"results": [], "error": "offline"}

    async def ensure_categories():
        pass

    def candidates(**kwargs):
        return [p for p in rows if kwargs["accept"](p)] if source == "snapshot" else []

    monkeypatch.setattr(client, "get_part", get_part)
    monkeypatch.setattr(client, "search", search)
    monkeypatch.setattr(client, "_ensure_categories", ensure_categories)
    monkeypatch.setattr(client, "get_subcategory_id_by_name", lambda name: 3098)
    client.set_alternative_candidates(candidates)
    with offline():
        try:
            result = await client.find_alternatives("C424093", same_package=True, limit=10)
        finally:
            await client.close()
    assert [p["lcsc"] for p in result["alternatives"]] == ["C100"]
    unverified = {p["lcsc"]: p for p in result["unverified_alternatives"]}
    assert set(unverified) == {"C103", "C104", "C106"}
    for code in ("C103", "C104"):
        assert CHARGE in unverified[code]["unverified_requirements"]
        assert CHARGE in unverified[code]["unchecked_requirements"]
    assert "The Chip Type" in unverified["C106"]["unverified_requirements"]
    assert result["summary"]["found"] == 1
    assert result["summary"]["unverified_count"] == 3
    assert result["comparison"]["recommended"]["lcsc"] == "C100"


@pytest.mark.parametrize("search_source", ["snapshot", "failed"])
async def test_reported_mcp_call_against_catalog(monkeypatch, search_source):
    with offline():
        async with Client(server.mcp) as client:
            database = db.get_db()
            codes = ("C424093", "C38066", "C625597", "C14879", "C625600", "C625604")
            for code in codes:
                if database.get_by_lcsc(code) is None:
                    pytest.skip(f"{code} left the daily catalog")
            with local_alternatives(server._client, database):
                if search_source == "failed":
                    async def search(**kwargs):
                        return {"results": [], "error": "offline"}

                    monkeypatch.setattr(server._client, "search", search)
                reply = await client.call_tool("jlc_find_alternatives", {
                    "lcsc": "C424093", "same_package": True, "limit": 10,
                })
    result = reply.structured_content
    assert not reply.is_error
    assert result["original"]["specs"][CHARGE] == "4.2V"
    verified = result["alternatives"]
    assert {"C38066", "C625597", "C14879"} <= {p["lcsc"] for p in verified}
    assert not {"C625600", "C625604"}.intersection(
        p["lcsc"] for p in verified + result["unverified_alternatives"]
    )
    for part in verified:
        assert part["specs"][CHARGE] == "4.2V"
        assert part["specs"]["The Chip Type"] == "Charging IC"
        assert CHARGE in part["specs_verified"]
    assert result["summary"]["found"] == len(verified)
