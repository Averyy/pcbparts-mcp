"""CLI evaluation harness for board search quality.

Usage:
    uv run python -m tests.boards_eval.runner              # full report
    uv run python -m tests.boards_eval.runner --query comp-mcp73831  # single query
    uv run python -m tests.boards_eval.runner --category text-functional
    uv run python -m tests.boards_eval.runner --holdout    # holdout only
    uv run python -m tests.boards_eval.runner --failures   # only show failures
    uv run python -m tests.boards_eval.runner --board-get  # board_get quality only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .golden_queries import GOLDEN_BOARD_GETS, GOLDEN_QUERIES, GoldenQuery
from .metrics import (
    BoardGetReport, BoardGetScore, EvalReport, QueryScore,
    aggregate_scores, evaluate_board_get, evaluate_query,
)


def run_evaluation(
    db,
    queries: list[GoldenQuery] | None = None,
) -> EvalReport:
    """Run all golden queries against a BoardsDatabase and return an EvalReport."""
    if queries is None:
        queries = GOLDEN_QUERIES

    scores: list[QueryScore] = []
    for gq in queries:
        params: dict = {"limit": gq.limit}
        if gq.query is not None:
            params["query"] = gq.query
        if gq.component is not None:
            params["component"] = gq.component
        if gq.tag is not None:
            params["tag"] = gq.tag
        if gq.org is not None:
            params["org"] = gq.org
        if gq.layers is not None:
            params["layers"] = gq.layers

        result = db.search(**params)
        score = evaluate_query(result, gq)
        scores.append(score)

    return aggregate_scores(scores)


def run_board_get_evaluation(db) -> BoardGetReport:
    """Run all golden board_get queries and return a BoardGetReport."""
    scores: list[BoardGetScore] = []
    for gq in GOLDEN_BOARD_GETS:
        result = db.get_board(gq.slug, focus=gq.focus)
        scores.append(evaluate_board_get(result, gq))
    return BoardGetReport(scores=scores)


def print_board_get_report(report: BoardGetReport) -> None:
    """Print a human-readable board_get evaluation report."""
    print()
    print("Board Get Quality Report")
    print("=" * 60)
    print(f"Total: {len(report.scores)}  Pass: {report.pass_rate:.0%}")
    print()

    if report.failures:
        print(f"Failures ({len(report.failures)}):")
        for s in report.failures:
            print(f"  {s.query_id}: {'; '.join(s.issues)}")
        print()
    else:
        print("Failures: none")
        print()

    for s in report.scores:
        status = "PASS" if s.passed else "FAIL"
        detail = f"{'; '.join(s.issues)}" if s.issues else "ok"
        print(f"  [{status}] {s.query_id}: {detail}")
    print()


def print_report(
    report: EvalReport,
    *,
    show_failures_only: bool = False,
    show_holdout: bool = False,
) -> None:
    """Print a human-readable evaluation report."""
    print()
    print("Board Search Quality Report")
    print("=" * 60)
    print(
        f"Overall (training): P@k={report.avg_precision:.2f}  "
        f"Recall={report.avg_recall:.2f}  "
        f"MRR={report.avg_mrr:.2f}  "
        f"MustInclude={report.must_include_hit_rate:.0%}  "
        f"MustExclude={report.must_exclude_clean_rate:.0%}  "
        f"InRange={report.total_range_rate:.0%}  "
        f"Pass={report.pass_rate:.0%}"
    )
    print(
        f"Holdout:            "
        f"MustInclude={report.holdout_must_include_hit_rate:.0%}  "
        f"Pass={report.holdout_pass_rate:.0%}"
    )
    print()

    # Per-category breakdown
    print("Per Category:")
    for cat_name in sorted(report.categories):
        cat = report.categories[cat_name]
        flag = "" if cat.pass_rate == 1.0 else " <<"
        mrr_str = f"  MRR={cat.avg_mrr:.2f}" if cat.avg_mrr > 0 else ""
        print(
            f"  {cat.category:<22} ({cat.count:>2}): "
            f"P@k={cat.avg_precision:.2f}  "
            f"Recall={cat.avg_recall:.2f}{mrr_str}  "
            f"MustIncl={cat.must_include_hit_rate:.0%}  "
            f"InRange={cat.total_range_rate:.0%}  "
            f"Pass={cat.pass_rate:.0%}{flag}"
        )
    print()

    # Failures
    failures = report.holdout_failures if show_holdout else report.failures
    label = "Holdout Failures" if show_holdout else "Failures"
    if failures:
        print(f"{label} ({len(failures)}):")
        for s in failures:
            issues = []
            if s.must_include_misses:
                issues.append(f"missing: {', '.join(s.must_include_misses)}")
            if s.must_exclude_violations:
                issues.append(f"unexpected: {', '.join(s.must_exclude_violations)}")
            if not s.total_in_range and s.expected_range:
                issues.append(
                    f"total={s.total_returned} expected={s.expected_range[0]}-{s.expected_range[1]}"
                )
            print(f"  {s.query_id}: {'; '.join(issues)}")
        print()
    else:
        print(f"{label}: none")
        print()

    if not show_failures_only:
        # All query details
        print("All Queries:")
        for s in report.scores:
            if show_holdout and not s.holdout:
                continue
            status = "PASS" if s.passed else "FAIL"
            h = " [holdout]" if s.holdout else ""
            detail = f"total={s.total_returned}"
            if s.must_include_total:
                detail += f" hits={s.must_include_hits}/{s.must_include_total}"
            if s.expected_range:
                detail += f" range={s.expected_range[0]}-{s.expected_range[1]}"
            print(f"  [{status}] {s.query_id}{h}: {detail}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Board search quality evaluation")
    parser.add_argument("--query", "-q", help="Run single query by ID")
    parser.add_argument("--category", "-c", help="Run queries in one category")
    parser.add_argument("--holdout", action="store_true", help="Show holdout queries only")
    parser.add_argument("--failures", action="store_true", help="Show failures only")
    parser.add_argument("--board-get", action="store_true", help="Run board_get quality only")
    parser.add_argument(
        "--db-path",
        type=Path,
        help="Path to boards.db (default: data/boards.db)",
    )
    args = parser.parse_args()

    # Import here to avoid import errors when just importing the module
    from pcbparts_mcp.boards_db import BoardsDatabase

    db_path = args.db_path
    db = BoardsDatabase(db_path=db_path) if db_path else BoardsDatabase()

    if args.board_get:
        bg_report = run_board_get_evaluation(db)
        print_board_get_report(bg_report)
        sys.exit(0 if bg_report.pass_rate == 1.0 else 1)

    # Filter queries
    queries = GOLDEN_QUERIES
    if args.query:
        queries = [q for q in queries if q.id == args.query]
        if not queries:
            print(f"Query '{args.query}' not found. Available:")
            for q in GOLDEN_QUERIES:
                print(f"  {q.id}")
            sys.exit(1)
    elif args.category:
        queries = [q for q in queries if q.category == args.category]
        if not queries:
            cats = sorted(set(q.category for q in GOLDEN_QUERIES))
            print(f"Category '{args.category}' not found. Available:")
            for c in cats:
                print(f"  {c}")
            sys.exit(1)

    report = run_evaluation(db, queries)
    print_report(report, show_failures_only=args.failures, show_holdout=args.holdout)

    # Also run board_get evaluation in default mode (no --query/--category filter)
    bg_ok = True
    if not args.query and not args.category:
        bg_report = run_board_get_evaluation(db)
        print_board_get_report(bg_report)
        bg_ok = bg_report.pass_rate == 1.0

    # Exit code: 0 if all pass, 1 if any fail
    sys.exit(0 if report.pass_rate == 1.0 and bg_ok else 1)


if __name__ == "__main__":
    main()
