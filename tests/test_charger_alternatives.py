"""Offline Battery Management regressions using catalog charger attributes."""

import pytest

from pcbparts_mcp.alternatives import is_compatible_alternative


# Compatibility attributes frozen from data/components.db; no API or database needed.
CHARGERS = {
    "C17702457": ("BQ25622ERYKR", "3.9V~18V", "I2C", "3A"),
    "C605432": ("IP2312U_VSET", "4.5V~5.5V", "-", "3A"),
    "C6164243": ("BQ25620RYKR", "3.9V~18V", "I2C", "3.5A"),
    "C424093": ("MCP73831T-2ACI/OT", "3.75V~6V", "-", "550mA"),
}


def charger(lcsc="C17702457", **overrides):
    model, supply, interface, current = CHARGERS[lcsc]
    specs = {
        "Type of Battery": "Lithium Battery",
        "Number of Cells": "1",
        "The Chip Type": "Charging IC",
        "Voltage - Supply": supply,
        "Interface": interface,
        "Charge Current - Max": current,
    }
    specs.update(overrides)
    # None exercises an absent attribute rather than a placeholder string.
    return {"lcsc": lcsc, "model": model, "specs": {k: v for k, v in specs.items() if v is not None}}


def check(original, candidate):
    return is_compatible_alternative(original, candidate, "Battery Management")


@pytest.mark.parametrize("lcsc,expected", [
    ("C605432", False),
    ("C6164243", True),
    ("C424093", False),
])
def test_bq25622_catalog_alternatives(lcsc, expected):
    compatible, info = check(charger(), charger(lcsc))
    assert compatible is expected
    if expected:
        assert {"Voltage - Supply", "Interface", "Charge Current - Max"} <= set(info["specs_verified"])
        assert info["unverified_requirements"] == []


@pytest.mark.parametrize("supply,expected", [
    ("4.5V~5.5V", False),  # IP2312U's input, with matching interface to isolate voltage.
    ("3.75V~6V", False),  # MCP73831's input, with matching interface/current.
    ("4.5V~18V", False),  # A higher minimum alone is incompatible.
    ("3.9V~17.9V", False),  # A lower maximum alone is incompatible (no 2% slack).
    ("3.9V~18V", True),
    ("3V~24V", True),
])
def test_supply_must_cover_both_endpoints(supply, expected):
    compatible, info = check(charger(), charger(**{"Voltage - Supply": supply}))
    assert compatible is expected
    if expected:
        assert "Voltage - Supply" in info["specs_verified"]


@pytest.mark.parametrize("supply", [None, "", "-", "unknown", "18V"])
def test_missing_or_unproven_supply_is_unverified(supply):
    compatible, info = check(charger(), charger(**{"Voltage - Supply": supply}))
    assert compatible
    assert "Voltage - Supply" in info["unverified_requirements"]
    assert "Voltage - Supply" in info["specs_unparseable"]
    assert "Voltage - Supply" not in info["specs_verified"]


@pytest.mark.parametrize("original,candidate,expected", [
    ("I2C", "I2C", True),
    ("I2C", "I2C、SMBus", True),
    ("I2C", " smbus 、 i2c ", True),
    ("I2C", "SMBus", False),
    ("I2C", "I2C-compatible", False),
    ("I2C、SMBus", "SMBus、I2C", True),
    ("I2C、SMBus", "I2C", False),
])
def test_candidate_must_support_all_original_interfaces(original, candidate, expected):
    compatible, info = check(charger(Interface=original), charger(Interface=candidate))
    assert compatible is expected
    if expected:
        assert "Interface" in info["specs_verified"]


@pytest.mark.parametrize("interface", [None, "", "-", "-、-"])
def test_missing_candidate_interface_is_unverified(interface):
    compatible, info = check(charger(), charger(Interface=interface))
    assert compatible
    assert "Interface" in info["unverified_requirements"]
    assert "Interface" not in info["specs_verified"]


@pytest.mark.parametrize("interface", [None, "", "-", "-、-"])
def test_original_without_interface_does_not_require_one(interface):
    compatible, info = check(charger(Interface=interface), charger(Interface="-"))
    assert compatible
    assert "Interface" not in info["specs_verified"]
    assert "Interface" not in info["specs_unparseable"]
    assert info["unverified_requirements"] == []


def test_mcp73831_without_interface_can_have_a_compatible_replacement():
    compatible, info = check(charger("C424093"), charger(**{"Voltage - Supply": "3V~18V"}))
    assert compatible
    assert info["unverified_requirements"] == []


def test_bq25628_two_amp_rating_remains_incompatible():
    candidate = charger("C6164243", **{"Charge Current - Max": "2A"})
    candidate["model"] = "BQ25628"
    compatible, info = check(charger(), candidate)
    assert not compatible
    assert {"Voltage - Supply", "Interface"} <= set(info["specs_verified"])


@pytest.mark.parametrize("chip_type,interface", [
    ("Protection IC", "-"),
    ("Monitoring IC", "I2C"),
])
def test_supply_and_stated_interfaces_also_apply_to_other_battery_ics(chip_type, interface):
    original = charger(**{"The Chip Type": chip_type, "Interface": interface, "Charge Current - Max": "-"})
    candidate = charger(**{"The Chip Type": chip_type, "Interface": interface, "Charge Current - Max": "-"})
    compatible, info = check(original, candidate)
    assert compatible
    assert info["unverified_requirements"] == []
    candidate["specs"]["Voltage - Supply"] = "4.5V~5.5V"
    assert not check(original, candidate)[0]


def test_coax_interface_matching_keeps_existing_exact_semantics():
    original = {"specs": {"Connector Type": "Board Side", "Gender": "Jack", "Mounting Type": "Surface Mount",
                          "Impedance": "50Ω", "RF Series": "SMA", "Interface": "Inner hole"}}
    candidate = {"specs": {**original["specs"], "Interface": "Inner bore"}}
    assert is_compatible_alternative(original, candidate, "Coaxial Connectors (RF)")[0]
    candidate["specs"]["Interface"] = "Inner hole、Inner pin"
    assert not is_compatible_alternative(original, candidate, "Coaxial Connectors (RF)")[0]
