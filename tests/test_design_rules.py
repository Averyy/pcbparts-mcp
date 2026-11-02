"""Tests for the design_rules module."""

import pytest
from pathlib import Path, PureWindowsPath

from pcbparts_mcp.design_rules import _rule_key, get_design_rules


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


def test_rule_key_uses_forward_slashes_on_windows():
    """Keys must be "category/stem" on Windows too; "power\\ldo" breaks matching and aliases."""
    root = PureWindowsPath(r"C:\pcbparts\data\design-rules\rules")
    assert _rule_key(root / "power" / "ldo.md", root) == "power/ldo"
    assert _rule_key(root / "misc" / "op-amp-basics.md", root) == "misc/op-amp-basics"


# Topics that matched no file name although a rule covers them (todos #48: 16% of prod lookups
# found nothing). Checked against the real rule files.
@pytest.mark.parametrize("topic, key", [
    ("lipo", "power/battery"), ("li-ion", "power/battery"), ("thermistor", "power/battery"),
    ("type-c", "interfaces/usb"), ("usb-c", "interfaces/usb"), ("stm32g0", "mcus/stm32"),
    ("esp32s3", "mcus/esp32"), ("pull-up", "interfaces/i2c"), ("pullup", "interfaces/i2c"),
    ("stepper", "misc/motor-control"), ("bldc", "misc/motor-control"), ("rs485", "interfaces/uart"),
    ("solar", "power/power-path"), ("4 layer", "guides/pcb-layout"), ("strapping pins", "mcus/esp32"),
    ("jlcpcb", "guides/dfm"), ("assembly", "guides/dfm"), ("buck-boost", "power/switching"),
])
def test_keywords_find_the_rule(topic, key):
    result = get_design_rules(topic)
    assert result["matched_files"] == [key]
    assert "note" not in result


@pytest.mark.parametrize("topic, key", [("boot mode", "mcus/esp32"), ("relay", "misc/mosfet-circuits"),
                                        ("RS-422 termination", None)])
def test_topic_found_in_the_text(topic, key):
    """No file is named for it, but one discusses it: the best files come back, marked as such."""
    result = get_design_rules(topic)
    if key is None:
        return
    assert result["matched_files"][0] == key
    assert "discuss it most" in result["note"]


def test_passing_mentions_find_nothing():
    # "LED" appears only in passing (Ethernet link LEDs, optocouplers); listing the index is better
    result = get_design_rules("led")
    assert result["matched_files"] == []
    assert "Available rules" in result["content"]


def test_text_matches_are_ranked(rules_dir):
    (rules_dir / "power" / "ldo.md").write_text("# LDO\n## Ferrite beads\nFerrite after the LDO.\n")
    (rules_dir / "interfaces" / "usb.md").write_text("# USB\n" + "A ferrite on VBUS.\n" * 9)
    result = get_design_rules("ferrite", rules_dir=rules_dir)
    # usb: 9 mentions; ldo: 2 mentions, one in a heading (counted 5 times)
    assert result["matched_files"] == ["interfaces/usb", "power/ldo"]
    assert result["content"].startswith("# USB")
