"""Tests for the design_rules module."""

import pytest
from pathlib import Path

from pcbparts_mcp.design_rules import get_design_rules


@pytest.fixture
def rules_dir(tmp_path):
    """Create a minimal rules directory for testing."""
    # INDEX.md
    (tmp_path / "INDEX.md").write_text("# Design Rules Index\n\nAll the rules.")

    # power/
    power = tmp_path / "power"
    power.mkdir()
    (power / "ldo.md").write_text("# LDO Design Rules\nDropout, ESR stability.")
    (power / "switching.md").write_text("# Switching Regulator Rules\nBuck/boost topology.")

    # interfaces/
    ifaces = tmp_path / "interfaces"
    ifaces.mkdir()
    (ifaces / "usb.md").write_text("# USB Design Rules\nUSB-C CC resistors.")
    (ifaces / "i2c.md").write_text("# I2C Design Rules\nPull-up calculation.")

    # mcus/
    mcus = tmp_path / "mcus"
    mcus.mkdir()
    (mcus / "esp32.md").write_text("# ESP32 Design Rules\nStrapping pins.")

    return tmp_path


def test_empty_topic_returns_index(rules_dir):
    result = get_design_rules("", rules_dir=rules_dir)
    assert "Design Rules Index" in result["content"]
    assert result["matched_files"] == ["INDEX.md"]
    assert result["topic"] == ""


def test_single_match(rules_dir):
    result = get_design_rules("ldo", rules_dir=rules_dir)
    assert "LDO Design Rules" in result["content"]
    assert result["matched_files"] == ["power/ldo"]
    assert result["topic"] == "ldo"


def test_category_match(rules_dir):
    result = get_design_rules("power", rules_dir=rules_dir)
    assert "LDO Design Rules" in result["content"]
    assert "Switching Regulator Rules" in result["content"]
    assert len(result["matched_files"]) == 2
    assert "power/ldo" in result["matched_files"]
    assert "power/switching" in result["matched_files"]


def test_no_match_returns_index(rules_dir):
    result = get_design_rules("nonexistent", rules_dir=rules_dir)
    assert "No rules found matching 'nonexistent'" in result["content"]
    assert "Design Rules Index" in result["content"]
    assert result["matched_files"] == []


def test_case_insensitive(rules_dir):
    result = get_design_rules("LDO", rules_dir=rules_dir)
    assert "LDO Design Rules" in result["content"]
    assert result["matched_files"] == ["power/ldo"]


def test_partial_match(rules_dir):
    result = get_design_rules("usb", rules_dir=rules_dir)
    assert "USB Design Rules" in result["content"]
    assert result["matched_files"] == ["interfaces/usb"]


def test_separator_format(rules_dir):
    result = get_design_rules("power", rules_dir=rules_dir)
    assert "\n\n---\n\n" in result["content"]


def test_matched_files_field(rules_dir):
    result = get_design_rules("i2c", rules_dir=rules_dir)
    assert result["matched_files"] == ["interfaces/i2c"]


def test_missing_dir():
    result = get_design_rules("ldo", rules_dir=Path("/nonexistent/path"))
    assert "error" in result
    assert "not available" in result["error"]
    assert result["matched_files"] == []


def test_whitespace_topic_returns_index(rules_dir):
    result = get_design_rules("  ", rules_dir=rules_dir)
    assert "Design Rules Index" in result["content"]
    assert result["matched_files"] == ["INDEX.md"]


def test_broad_match_returns_file_list(tmp_path):
    """When >3 files match, return file list instead of full content."""
    (tmp_path / "INDEX.md").write_text("# Index")
    for name in ["a-power.md", "b-power.md", "c-power.md", "d-power.md"]:
        (tmp_path / name).write_text(f"# {name}\nContent of {name}.")
    result = get_design_rules("power", rules_dir=tmp_path)
    assert len(result["matched_files"]) == 4
    assert "Found 4 rule files" in result["content"]
    assert "more specific topic" in result["content"]
    # Should NOT contain the actual file content
    assert "Content of" not in result["content"]


def test_three_matches_returns_full_content(tmp_path):
    """Exactly 3 matches should still return full content."""
    (tmp_path / "INDEX.md").write_text("# Index")
    for name in ["a-power.md", "b-power.md", "c-power.md"]:
        (tmp_path / name).write_text(f"# {name}\nContent of {name}.")
    result = get_design_rules("power", rules_dir=tmp_path)
    assert len(result["matched_files"]) == 3
    assert "Content of" in result["content"]


def test_alias_resolution(rules_dir):
    """Aliases like 'buck' should resolve to power/switching."""
    result = get_design_rules("buck", rules_dir=rules_dir)
    assert result["matched_files"] == ["power/switching"]
    assert "Switching Regulator Rules" in result["content"]


def test_hyphenated_topic(tmp_path):
    """Hyphenated input like 'op-amp' should match 'op-amp-basics'."""
    (tmp_path / "INDEX.md").write_text("# Index")
    misc = tmp_path / "misc"
    misc.mkdir()
    (misc / "op-amp-basics.md").write_text("# Op-Amp Basics\nSelection guide.")
    result = get_design_rules("op-amp", rules_dir=tmp_path)
    assert result["matched_files"] == ["misc/op-amp-basics"]
    assert "Op-Amp Basics" in result["content"]
