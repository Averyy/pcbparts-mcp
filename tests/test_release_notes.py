"""Release notes must never spill past a missing or malformed publication boundary."""

from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from release_notes import release_notes


ROOT = Path(__file__).resolve().parent.parent


def entry(version, body="- A change.", date="2026-11-21"):
    return f"## {version} ({date})\n\n### Changed\n\n{body}\n\n"


def test_patch_after_minor_is_tag_only():
    changelog = entry("0.10.1") + entry("0.10.0")
    assert release_notes(changelog, "0.10.1", "0.10.0") is None


def test_minor_includes_every_patch_since_last_release():
    expected = entry("0.11.0") + entry("0.10.6") + entry("0.10.5")
    changelog = entry("0.11.1") + expected + entry("0.10.4") + entry("0.10.3")
    assert release_notes(changelog, "0.11.0", "0.10.4") == expected.rstrip() + "\n"


def test_first_run_with_previously_published_patch_is_tag_only():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert release_notes(changelog, "0.10.5", "0.10.4") is None


def test_major_includes_patches():
    expected = entry("1.0.0") + entry("0.11.1")
    assert release_notes(expected + entry("0.11.0"), "1.0.0", "0.11.0") == expected.rstrip() + "\n"


@pytest.mark.parametrize("last_release", [None, ""])
def test_first_release_includes_all_entries(last_release):
    changelog = entry("0.2.0") + entry("0.1.1") + entry("0.1.0")
    assert release_notes(changelog, "0.2.0", last_release) == changelog.rstrip() + "\n"


def test_missing_current_heading_fails():
    with pytest.raises(ValueError, match="missing current-version heading for 0.11.0"):
        release_notes(entry("0.10.4"), "0.11.0", "0.10.4")


def test_missing_boundary_fails_instead_of_including_old_releases():
    changelog = entry("0.11.0") + entry("0.10.5") + entry("0.10.3")
    with pytest.raises(ValueError, match="missing previous-release boundary heading for 0.10.4"):
        release_notes(changelog, "0.11.0", "0.10.4")


@pytest.mark.parametrize("version", ["0.11.0", "0.10.5", "0.10.4"])
@pytest.mark.parametrize("bad_date", ["2026-02-30", "2026-13-01", "2026-1-01", "today"])
def test_malformed_dates_fail_in_current_entries_and_boundary(version, bad_date):
    changelog = "".join(entry(v, date=bad_date if v == version else "2026-11-21")
                        for v in ("0.11.0", "0.10.5", "0.10.4"))
    with pytest.raises(ValueError, match="malformed (date|heading)"):
        release_notes(changelog, "0.11.0", "0.10.4")


@pytest.mark.parametrize("heading", [
    "## 0.10.4", "## 0.10.4 (2026-11-21) extra", "##  0.10.4 (2026-11-21)",
    "##0.10.4 (2026-11-21)", " ## 0.10.4 (2026-11-21)", "### 0.10.4 (2026-11-21)",
], ids=["bare", "suffix", "space", "joined", "indent", "level"])
def test_boundary_heading_format_is_strict(heading):
    changelog = entry("0.11.0") + heading + "\n\n- Already published.\n" + entry("0.10.3")
    with pytest.raises(ValueError, match="malformed heading|missing previous-release boundary"):
        release_notes(changelog, "0.11.0", "0.10.4")


@pytest.mark.parametrize("duplicate", ["0.11.0", "0.10.5", "0.10.4"])
def test_duplicate_heading_even_below_boundary_fails(duplicate):
    changelog = entry("0.11.0") + entry("0.10.5") + entry("0.10.4") + entry(duplicate)
    with pytest.raises(ValueError, match=f"duplicate heading for {duplicate}"):
        release_notes(changelog, "0.11.0", "0.10.4")


@pytest.mark.parametrize("body", ["", " \n\t", "### Fixed\n"], ids=["empty", "space", "heading"])
@pytest.mark.parametrize("version", ["0.11.0", "0.10.5"])
def test_empty_notes_fail_even_for_patch_versions(version, body):
    with pytest.raises(ValueError, match=f"empty notes for {version}"):
        release_notes(entry(version, body=body) + entry("0.10.4"), version, "0.10.4")


def test_empty_intermediate_entry_fails():
    with pytest.raises(ValueError, match="empty notes for 0.10.5"):
        release_notes(entry("0.11.0") + entry("0.10.5", body="") + entry("0.10.4"), "0.11.0", "0.10.4")


@pytest.mark.parametrize("bad_entry", [
    entry("0.10.5", date="2026-02-30"), entry("0.10.5") + entry("0.10.5"),
    "## 0.10.5\n\n- A change.\n",
], ids=["date", "duplicate", "bare"])
def test_patch_still_validates_its_section(bad_entry):
    with pytest.raises(ValueError, match="malformed|duplicate"):
        release_notes(bad_entry + entry("0.10.4"), "0.10.5", "0.10.4")


def test_legacy_headings_below_boundary_are_not_included_or_validated():
    changelog = entry("0.11.0") + entry("0.10.4") + "## 0.5.x (July–October 2026)\n\n- History.\n"
    assert release_notes(changelog, "0.11.0", "0.10.4") == entry("0.11.0").rstrip() + "\n"


@pytest.mark.parametrize("last_release", ["0.11.0", "0.12.0"])
def test_boundary_must_be_older(last_release):
    changelog = entry("0.12.0") + entry("0.11.0")
    with pytest.raises(ValueError, match="boundary .* must be older"):
        release_notes(changelog, "0.11.0", last_release)


@pytest.mark.parametrize("version", ["0.11", "v0.11.0", "0.11.0-rc1", "00.11.0"])
def test_invalid_version_fails(version):
    with pytest.raises(ValueError, match="invalid release version"):
        release_notes(entry("0.11.0"), version)


@pytest.mark.parametrize("version, last_release, exit_code", [
    ("0.11.0", "0.10.4", 0), ("0.10.5", "0.10.4", 0), ("0.11.0", "0.10.0", 1),
], ids=["minor", "patch", "missing"])
def test_cli_outputs_notes_only_after_validation(tmp_path, version, last_release, exit_code):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(entry("0.11.0", body="- µC support.") + entry("0.10.5") + entry("0.10.4"),
                         encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / "scripts/release_notes.py"), version,
         "--last-release", last_release, "--changelog", str(changelog)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert result.returncode == exit_code
    if exit_code:
        assert result.stdout == ""
        assert "missing previous-release boundary" in result.stderr
    elif version == "0.10.5":
        assert result.stdout == result.stderr == ""
    else:
        assert "µC support" in result.stdout
        assert "## 0.10.5" in result.stdout
        assert "## 0.10.4" not in result.stdout
        assert result.stderr == ""
