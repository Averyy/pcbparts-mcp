"""Optional, bounded conjunctive facets over the final compiled search."""

import logging
import sqlite3
import time
from collections import Counter
from typing import Any

from .diagnostics import DIAGNOSTIC_POST_ROWS, DIAGNOSTIC_SECONDS, DIAGNOSTIC_VM_STEPS
from .engine import CompiledSearch, PostFilterPredicate, SearchEngine

logger = logging.getLogger(__name__)
FACET_SECONDS = DIAGNOSTIC_SECONDS
FACET_VM_STEPS = DIAGNOSTIC_VM_STEPS
FACET_POST_ROWS = DIAGNOSTIC_POST_ROWS
FACET_BUCKETS = 15
_LIBRARY_NAMES = {"b": "basic", "p": "preferred", "e": "extended"}


class _BudgetExhausted(Exception):
    pass


def collect_facets(db: Any, plan: CompiledSearch | None) -> dict[str, Any]:
    """Publish exact counts only after the whole traversal finishes within its own budget."""
    started = time.monotonic()
    deadline = started + FACET_SECONDS
    out = {"scope": "filtered_snapshot", "matched_total": None, "complete": False,
           "status": "unavailable", "elapsed_ms": 0}
    conn = None
    steps = 0
    budget_hit = False

    def check_budget():
        if time.monotonic() >= deadline:
            raise _BudgetExhausted

    def interrupted():
        nonlocal steps, budget_hit
        steps += 1000
        budget_hit = steps >= FACET_VM_STEPS or time.monotonic() >= deadline
        return int(budget_hit)

    try:
        if plan is None:
            return out
        check_budget()
        conn = sqlite3.connect(db.db_path.resolve().as_uri() + '?mode=ro', uri=True, timeout=0.05)
        conn.row_factory = sqlite3.Row
        conn.set_progress_handler(interrupted, 1000)
        # Register the same SQL functions and schema capabilities as ordinary search.
        SearchEngine(conn, db._subcategories, db._categories, db._subcategory_name_to_id,
                     db._category_name_to_id, db._category_to_subcategories)
        conn.execute("PRAGMA temp_store=MEMORY")
        check_budget()
        counts = {name: Counter() for name in ("manufacturer", "package", "library_type")}
        total = 0

        def add(manufacturer, package, library, count):
            nonlocal total
            total += count
            counts["manufacturer"][manufacturer] += count
            counts["package"][package] += count
            counts["library_type"][_LIBRARY_NAMES.get(library, library)] += count

        if not plan.post_filters and plan.mpn_predicate is None:
            # One joint aggregate, folded into three marginal distributions.
            sql = ("SELECT manufacturer, package, library_type, COUNT(*) FROM components "
                   + plan.where_sql + " GROUP BY manufacturer, package, library_type")
            for manufacturer, package, library, count in conn.execute(sql, plan.params):
                check_budget()
                add(manufacturer, package, library, count)
        else:
            predicate = PostFilterPredicate(plan.post_filters)
            sql = ("SELECT manufacturer, package, library_type, attributes, mpn, subcategory_id"
                   + predicate.sql + " FROM components " + plan.where_sql + " LIMIT ?")
            params = [*predicate.params, *plan.params, FACET_POST_ROWS + 1]
            for index, row in enumerate(conn.execute(sql, params)):
                check_budget()
                if index >= FACET_POST_ROWS:
                    raise _BudgetExhausted
                manufacturer, package, library, attributes, mpn, subcategory = row[:6]
                if (plan.mpn_predicate is None or plan.mpn_predicate(mpn)) and predicate.passes(
                        attributes, package, mpn, subcategory, row[6:]):
                    add(manufacturer, package, library, 1)
        check_budget()
        facets = {}
        for name, values in counts.items():
            ordered = sorted(values.items(), key=lambda item: (-item[1], item[0] or ""))
            shown = ordered[:FACET_BUCKETS]
            facets[name] = {"buckets": [{"value": value, "count": count} for value, count in shown],
                            "omitted_buckets": max(0, len(ordered) - len(shown)),
                            "omitted_count": sum(count for _, count in ordered[FACET_BUCKETS:])}
        check_budget()
        out.update(facets, matched_total=total, complete=True, status="complete")
    except _BudgetExhausted:
        out["status"] = "incomplete"
    except sqlite3.Error:
        if budget_hit:
            out["status"] = "incomplete"
        else:
            logger.warning("Optional search facets unavailable", exc_info=True)
    finally:
        if conn is not None:
            conn.close()
        out["elapsed_ms"] = round((time.monotonic() - started) * 1000)
    return out
