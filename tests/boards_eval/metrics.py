"""Evaluation metrics for board search quality.

Pure functions — no database access, no side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .golden_queries import GoldenBoardGet, GoldenQuery


@dataclass
class QueryScore:
    """Evaluation result for a single golden query."""

    query_id: str
    category: str
    holdout: bool

    # Result counts
    total_returned: int
    limit: int

    # Must-include
    must_include_total: int = 0
    must_include_hits: int = 0
    must_include_misses: list[str] = field(default_factory=list)

    # Must-exclude
    must_exclude_total: int = 0
    must_exclude_violations: list[str] = field(default_factory=list)

    # Total range
    total_in_range: bool = True
    expected_range: tuple[int, int] | None = None

    # Ranking
    precision_at_k: float = 0.0
    recall: float = 0.0
    mrr: float = 0.0

    @property
    def passed(self) -> bool:
        """Query passes if all must_include hit and no must_exclude violations and total in range."""
        return (
            len(self.must_include_misses) == 0
            and len(self.must_exclude_violations) == 0
            and self.total_in_range
        )


@dataclass
class CategoryReport:
    """Aggregated metrics for one query category."""

    category: str
    count: int
    must_include_hit_rate: float
    must_exclude_clean_rate: float
    total_range_rate: float
    avg_precision: float
    avg_recall: float
    avg_mrr: float
    pass_rate: float


@dataclass
class EvalReport:
    """Full evaluation report across all queries."""

    scores: list[QueryScore]
    categories: dict[str, CategoryReport]

    # Aggregate metrics (training queries only — excludes holdout)
    must_include_hit_rate: float  # % of must_include slugs found
    must_exclude_clean_rate: float  # % of queries with no must_exclude violations
    total_range_rate: float  # % of queries with total in expected range
    avg_precision: float
    avg_recall: float
    avg_mrr: float
    pass_rate: float

    # Holdout metrics (separate tracking for overfitting detection)
    holdout_must_include_hit_rate: float
    holdout_pass_rate: float

    @property
    def failures(self) -> list[QueryScore]:
        return [s for s in self.scores if not s.passed]

    @property
    def training_failures(self) -> list[QueryScore]:
        return [s for s in self.scores if not s.passed and not s.holdout]

    @property
    def holdout_failures(self) -> list[QueryScore]:
        return [s for s in self.scores if not s.passed and s.holdout]


# ---------------------------------------------------------------------------
# Pure metric functions
# ---------------------------------------------------------------------------


def precision_at_k(returned: list[str], relevant: set[str], k: int) -> float:
    """Fraction of top-k results that are relevant."""
    if not relevant or k <= 0:
        return 1.0  # No ground truth = vacuously correct
    top_k = returned[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for s in top_k if s in relevant)
    return hits / len(top_k)


def recall(returned: list[str], relevant: set[str]) -> float:
    """Fraction of relevant items that appear in results."""
    if not relevant:
        return 1.0
    hits = sum(1 for s in relevant if s in returned)
    return hits / len(relevant)


def mrr(returned: list[str], expected_first: str | None) -> float:
    """Mean reciprocal rank — 1/position of expected_first in results."""
    if not expected_first:
        return 0.0
    for i, slug in enumerate(returned):
        if slug == expected_first:
            return 1.0 / (i + 1)
    return 0.0


# ---------------------------------------------------------------------------
# Query-level evaluation
# ---------------------------------------------------------------------------


def evaluate_query(result: dict, golden: GoldenQuery) -> QueryScore:
    """Evaluate a single search result against its golden query."""
    returned_slugs = [r["slug"] for r in result.get("results", [])]
    total = result.get("total", 0)
    returned_set = set(returned_slugs)
    relevant = set(golden.must_include)

    score = QueryScore(
        query_id=golden.id,
        category=golden.category,
        holdout=golden.holdout,
        total_returned=total,
        limit=golden.limit,
    )

    # Must-include
    score.must_include_total = len(golden.must_include)
    # Check against ALL returned slugs (up to limit), not just returned_set
    for slug in golden.must_include:
        if slug in returned_set:
            score.must_include_hits += 1
        else:
            score.must_include_misses.append(slug)

    # Must-exclude
    score.must_exclude_total = len(golden.must_exclude)
    for slug in golden.must_exclude:
        if slug in returned_set:
            score.must_exclude_violations.append(slug)

    # Total range
    if golden.expected_total_range:
        lo, hi = golden.expected_total_range
        score.total_in_range = lo <= total <= hi
        score.expected_range = golden.expected_total_range

    # Ranking metrics
    score.precision_at_k = precision_at_k(returned_slugs, relevant, golden.limit)
    score.recall = recall(returned_slugs, relevant)
    score.mrr = mrr(returned_slugs, golden.expected_first)

    return score


# ---------------------------------------------------------------------------
# Aggregate scoring
# ---------------------------------------------------------------------------


@dataclass
class BoardGetScore:
    """Evaluation result for a single golden board_get query."""

    query_id: str
    issues: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.issues) == 0


@dataclass
class BoardGetReport:
    """Aggregate board_get evaluation report."""

    scores: list[BoardGetScore] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if not self.scores:
            return 1.0
        return sum(1 for s in self.scores if s.passed) / len(self.scores)

    @property
    def failures(self) -> list[BoardGetScore]:
        return [s for s in self.scores if not s.passed]


# Bare component value strings that indicate parse failures
_JUNK_VALUES = {"R", "C", "L", "D", "F", "FB"}


def evaluate_board_get(result: dict | None, golden: GoldenBoardGet) -> BoardGetScore:
    """Evaluate a single board_get result against its golden query."""
    score = BoardGetScore(query_id=golden.id)

    if result is None:
        score.issues.append("board not found (None)")
        return score

    has_focus = "focus" in result
    has_error = "focus_error" in result

    # focus_found check
    if golden.focus_found and not has_focus:
        if has_error:
            score.issues.append(f"focus not found: {result.get('focus_error', '')}")
        else:
            score.issues.append("focus missing from response")
        return score
    if not golden.focus_found and has_focus:
        score.issues.append("focus found but expected NOT found")
        return score
    if not golden.focus_found:
        # Verify available_ics present on failure
        if "available_ics" not in result:
            score.issues.append("focus_error present but no available_ics")
        return score

    focus = result["focus"]

    # ic_value_contains
    if golden.ic_value_contains:
        if golden.ic_value_contains not in focus.get("value", ""):
            score.issues.append(
                f"ic_value_contains: expected '{golden.ic_value_contains}' "
                f"in '{focus.get('value', '')}'"
            )

    # pins_present
    pins = focus.get("pins", {})
    for pin_name in golden.pins_present:
        if pin_name not in pins:
            score.issues.append(f"pin '{pin_name}' missing")

    # has_decoupling
    if golden.has_decoupling is not None:
        has_decoup = "_decoupling" in pins
        if golden.has_decoupling and not has_decoup:
            score.issues.append("expected _decoupling section, not found")
        elif not golden.has_decoupling and has_decoup:
            score.issues.append("unexpected _decoupling section")

    # has_consensus
    if golden.has_consensus is not None:
        has_cons = "consensus" in result
        if golden.has_consensus and not has_cons:
            score.issues.append("expected consensus, not found")
        elif not golden.has_consensus and has_cons:
            score.issues.append("unexpected consensus present")

    # min_consensus_boards
    if golden.min_consensus_boards is not None and "consensus" in result:
        actual = result["consensus"].get("board_count", 0)
        if actual < golden.min_consensus_boards:
            score.issues.append(
                f"consensus boards {actual} < expected {golden.min_consensus_boards}"
            )

    # no_junk_values — no bare "R"/"C"/"L"/etc. in pin component values
    if golden.no_junk_values:
        for pin_name, components in pins.items():
            for c in components:
                if c.get("value") in _JUNK_VALUES:
                    score.issues.append(
                        f"junk value '{c['value']}' on pin '{pin_name}'"
                    )
                    break  # one per pin is enough

    return score


def aggregate_scores(scores: list[QueryScore]) -> EvalReport:
    """Build a full evaluation report from individual query scores."""
    training = [s for s in scores if not s.holdout]
    holdout = [s for s in scores if s.holdout]

    def _rates(subset: list[QueryScore]) -> dict:
        if not subset:
            return {
                "must_include_hit_rate": 1.0,
                "must_exclude_clean_rate": 1.0,
                "total_range_rate": 1.0,
                "avg_precision": 1.0,
                "avg_recall": 1.0,
                "avg_mrr": 0.0,
                "pass_rate": 1.0,
            }
        total_mi = sum(s.must_include_total for s in subset)
        total_mi_hits = sum(s.must_include_hits for s in subset)
        queries_with_excl = [s for s in subset if s.must_exclude_total > 0]
        clean_excl = sum(1 for s in queries_with_excl if not s.must_exclude_violations)

        return {
            "must_include_hit_rate": total_mi_hits / total_mi if total_mi else 1.0,
            "must_exclude_clean_rate": (
                clean_excl / len(queries_with_excl) if queries_with_excl else 1.0
            ),
            "total_range_rate": (
                sum(1 for s in subset if s.total_in_range) / len(subset)
            ),
            "avg_precision": sum(s.precision_at_k for s in subset) / len(subset),
            "avg_recall": sum(s.recall for s in subset) / len(subset),
            "avg_mrr": sum(s.mrr for s in subset) / len(subset),
            "pass_rate": sum(1 for s in subset if s.passed) / len(subset),
        }

    # Per-category reports
    categories: dict[str, CategoryReport] = {}
    cats = sorted(set(s.category for s in scores))
    for cat in cats:
        cat_scores = [s for s in scores if s.category == cat]
        rates = _rates(cat_scores)
        categories[cat] = CategoryReport(
            category=cat,
            count=len(cat_scores),
            must_include_hit_rate=rates["must_include_hit_rate"],
            must_exclude_clean_rate=rates["must_exclude_clean_rate"],
            total_range_rate=rates["total_range_rate"],
            avg_precision=rates["avg_precision"],
            avg_recall=rates["avg_recall"],
            avg_mrr=rates["avg_mrr"],
            pass_rate=rates["pass_rate"],
        )

    training_rates = _rates(training)
    holdout_rates = _rates(holdout)

    return EvalReport(
        scores=scores,
        categories=categories,
        must_include_hit_rate=training_rates["must_include_hit_rate"],
        must_exclude_clean_rate=training_rates["must_exclude_clean_rate"],
        total_range_rate=training_rates["total_range_rate"],
        avg_precision=training_rates["avg_precision"],
        avg_recall=training_rates["avg_recall"],
        avg_mrr=training_rates["avg_mrr"],
        pass_rate=training_rates["pass_rate"],
        holdout_must_include_hit_rate=holdout_rates["must_include_hit_rate"],
        holdout_pass_rate=holdout_rates["pass_rate"],
    )
