"""Tests for the offline baseline comparison and result capture."""

from copy import deepcopy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import diff_snapshots, offline, summarize_response


def _call(query="10k resistor", **extra):
    return {"tool": "jlc_search", "args": {"query": query},
            "response": {"total": 1, "results": [{"lcsc": "C1"}]},
            "is_error": False, **extra}


def test_identical_snapshots_have_no_changes(capsys):
    before = {"calls": [_call(), _call()]}
    assert diff_snapshots(before, deepcopy(before)) == 0
    assert "0 changed calls: 0 expected, 0 untagged" in capsys.readouterr().out


def test_changes_group_by_item_and_untagged(capsys):
    before = {"calls": [_call(expect_change="#40"), _call("mosfet")]}
    after = deepcopy(before)
    after["calls"][0]["response"]["total"] = 3
    after["calls"][1]["response"]["results"] = [{"lcsc": "C2"}]
    assert diff_snapshots(before, after) == 0
    output = capsys.readouterr().out
    assert "expected for item #40 (1 changed calls)" in output
    assert "untagged (possible regression) (1 changed calls)" in output
    assert "total: 1 -> 3" in output
    assert '"C1"' in output and '"C2"' in output
    assert "2 changed calls: 1 expected, 1 untagged" in output


def test_added_removed_and_duplicate_calls(capsys):
    before = {"calls": [_call(), _call(), _call("removed", expect_change="#5")]}
    after = {"calls": [_call(), _call(), _call("added")]}
    after["calls"][1]["response"] = {"error": "validation failed"}
    after["calls"][1]["is_error"] = True
    assert diff_snapshots(before, after) == 0
    output = capsys.readouterr().out
    assert "call added" in output and "call removed" in output
    assert "validation failed" in output
    assert "is_error: False -> True" in output
    assert "3 changed calls: 1 expected, 2 untagged" in output


def test_query_order_and_metadata_do_not_count_as_result_changes(capsys):
    before = {"calls": [_call(), _call("mosfet")], "sources_sha256": {"components": "a"}}
    after = {"calls": list(reversed(before["calls"])), "sources_sha256": {"components": "b"}}
    assert diff_snapshots(before, after) == 0
    output = capsys.readouterr().out
    assert "Snapshot metadata changed (sources_sha256)" in output
    assert "0 changed calls" in output


def test_shortlists_keep_specs_filters_and_counts():
    response = {"similar_parts": [{"lcsc": f"C{i}", "specs": {"Voltage": "5V"}}
                                  for i in range(15)],
                "filters_applied": {"spec_filters": list(range(12))},
                "parsed": {"adjusted_filters": [{"filter": "Voltage"}]}}
    result = summarize_response(response)
    assert result["similar_parts_count"] == 15
    assert len(result["similar_parts"]) == 10
    assert result["similar_parts"][0]["specs"] == {"Voltage": "5V"}
    assert result["filters_applied"] == response["filters_applied"]
    assert result["parsed"] == response["parsed"]
    assert len(response["similar_parts"]) == 15


def test_diff_identifies_spec_changes_late_in_shortlist(capsys):
    before = {"calls": [_call()]}
    before["calls"][0]["response"]["results"] = [
        {"lcsc": f"C{i}", "specs": {"Voltage": "5V"}} for i in range(10)
    ]
    after = deepcopy(before)
    after["calls"][0]["response"]["results"][9]["specs"]["Voltage"] = "3V"
    diff_snapshots(before, after)
    assert 'results[9].specs.Voltage: "5V" -> "3V"' in capsys.readouterr().out


def test_network_attempt_aborts_even_if_tool_catches_it():
    import wafer

    with pytest.raises(RuntimeError, match="snapshot aborted"):
        with offline():
            try:
                wafer.AsyncSession()
            except RuntimeError:
                pass
