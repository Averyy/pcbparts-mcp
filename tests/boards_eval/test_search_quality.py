"""Pytest integration for board search quality evaluation.

Runs against the production boards.db — skips if not available.
Run with: pytest tests/boards_eval/ -m quality -v
"""

from __future__ import annotations

import pytest
from pathlib import Path

from pcbparts_mcp.boards_db import BoardsDatabase

from .golden_queries import GOLDEN_BOARD_GETS, GOLDEN_QUERIES
from .metrics import BoardGetReport, evaluate_board_get
from .runner import run_evaluation

# Skip entire module if boards.db doesn't exist
_DB_PATH = Path(__file__).parent.parent.parent / "data" / "boards.db"
pytestmark = [
    pytest.mark.quality,
    pytest.mark.skipif(not _DB_PATH.exists(), reason="boards.db not found"),
]


@pytest.fixture(scope="module")
def boards_db():
    db = BoardsDatabase(db_path=_DB_PATH)
    yield db
    db.close()


@pytest.fixture(scope="module")
def eval_report(boards_db):
    return run_evaluation(boards_db)


# ---------------------------------------------------------------------------
# Aggregate quality gates
# ---------------------------------------------------------------------------


class TestAggregateQuality:
    """Aggregate quality thresholds — these are the gates for accepting changes."""

    def test_must_include_hit_rate(self, eval_report):
        """At least 90% of must_include slugs are found."""
        assert eval_report.must_include_hit_rate >= 0.90, (
            f"must_include hit rate {eval_report.must_include_hit_rate:.0%} < 90%. "
            f"Failures: {[s.query_id for s in eval_report.training_failures if s.must_include_misses]}"
        )

    def test_must_exclude_clean_rate(self, eval_report):
        """At least 95% of queries have no must_exclude violations."""
        assert eval_report.must_exclude_clean_rate >= 0.95, (
            f"must_exclude clean rate {eval_report.must_exclude_clean_rate:.0%} < 95%. "
            f"Violations: {[s.query_id for s in eval_report.training_failures if s.must_exclude_violations]}"
        )

    def test_total_range_rate(self, eval_report):
        """At least 85% of queries return results in expected total range."""
        assert eval_report.total_range_rate >= 0.85, (
            f"total range rate {eval_report.total_range_rate:.0%} < 85%. "
            f"Out of range: {[(s.query_id, s.total_returned, s.expected_range) for s in eval_report.training_failures if not s.total_in_range]}"
        )

    def test_overall_pass_rate(self, eval_report):
        """At least 85% of training queries pass all checks."""
        assert eval_report.pass_rate >= 0.85, (
            f"pass rate {eval_report.pass_rate:.0%} < 85%. "
            f"Failures: {[s.query_id for s in eval_report.training_failures]}"
        )


# ---------------------------------------------------------------------------
# Holdout overfitting detection
# ---------------------------------------------------------------------------


class TestHoldoutQuality:
    """Holdout queries should track training quality — detect overfitting."""

    def test_holdout_must_include_hit_rate(self, eval_report):
        """Holdout must_include hit rate should not drop far below training."""
        gap = eval_report.must_include_hit_rate - eval_report.holdout_must_include_hit_rate
        assert gap <= 0.15, (
            f"Holdout must_include gap too large: training={eval_report.must_include_hit_rate:.0%} "
            f"holdout={eval_report.holdout_must_include_hit_rate:.0%} (gap={gap:.0%} > 15%)"
        )

    def test_holdout_pass_rate(self, eval_report):
        """Holdout pass rate should not drop far below training."""
        gap = eval_report.pass_rate - eval_report.holdout_pass_rate
        assert gap <= 0.20, (
            f"Holdout pass rate gap too large: training={eval_report.pass_rate:.0%} "
            f"holdout={eval_report.holdout_pass_rate:.0%} (gap={gap:.0%} > 20%)"
        )


# ---------------------------------------------------------------------------
# Board GET quality gates
# ---------------------------------------------------------------------------


class TestBoardGetQuality:
    """board_get focus response correctness — prevents silent breakage of focus mode."""

    @pytest.fixture(scope="module")
    def board_get_report(self, boards_db) -> BoardGetReport:
        scores = []
        for gq in GOLDEN_BOARD_GETS:
            result = boards_db.get_board(gq.slug, focus=gq.focus)
            scores.append(evaluate_board_get(result, gq))
        return BoardGetReport(scores=scores)

    def test_board_get_pass_rate(self, board_get_report):
        """All golden board_get queries should pass."""
        failures = board_get_report.failures
        assert board_get_report.pass_rate == 1.0, (
            f"board_get pass rate {board_get_report.pass_rate:.0%}. "
            f"Failures: {[(f.query_id, f.issues) for f in failures]}"
        )

    def test_board_get_individual(self, boards_db):
        """Each board_get golden query passes (parametrized for clear failure messages)."""
        for gq in GOLDEN_BOARD_GETS:
            result = boards_db.get_board(gq.slug, focus=gq.focus)
            score = evaluate_board_get(result, gq)
            assert score.passed, f"{gq.id}: {score.issues}"


# ---------------------------------------------------------------------------
# Per-category quality gates
# ---------------------------------------------------------------------------


class TestCategoryQuality:
    """No category should completely collapse."""

    def test_no_category_below_50_percent_pass(self, eval_report):
        """Every category should have at least 50% pass rate."""
        bad = [
            (name, cat.pass_rate)
            for name, cat in eval_report.categories.items()
            if cat.pass_rate < 0.50
        ]
        assert not bad, f"Categories below 50% pass rate: {bad}"

    def test_component_exact_high_quality(self, eval_report):
        """Component-exact searches should be very reliable."""
        cat = eval_report.categories.get("component-exact")
        if cat:
            assert cat.must_include_hit_rate >= 0.95, (
                f"component-exact must_include rate {cat.must_include_hit_rate:.0%} < 95%"
            )
