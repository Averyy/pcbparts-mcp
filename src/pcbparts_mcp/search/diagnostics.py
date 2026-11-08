"""Bounded counterfactuals over the normalized search, on a private read connection."""
import sqlite3
import logging
import time
from typing import Any

from .engine import SearchEngine

logger = logging.getLogger(__name__)

MAX_DIAGNOSTIC_QUERIES = 3
DIAGNOSTIC_SECONDS = 0.20
DIAGNOSTIC_VM_STEPS = 2_000_000
DIAGNOSTIC_POST_ROWS = 5_000


def next_search(query: str | None, plan: dict) -> dict | None:
    # Multi-subcategory groups have no public subcategory_ids argument. Don't emit
    # a next call that loses that requirement or invent an unsupported argument.
    if plan.get('subcategory_ids'):
        return None
    names = ('subcategory_id','subcategory_name','category_id','category_name','min_stock',
             'package','packages','manufacturer','mounting_type','match_all_terms','pcba_type')
    # Mounting is not a public argument: retain it through an explicit query word.
    words = ' '.join(v for v in (plan.get('part_number') or query, plan.get('mounting_type')) if v)
    args = {k:plan[k] for k in names if k != 'mounting_type' and plan.get(k) is not None}
    args['query'] = words or None
    args['library_type'] = plan.get('library_type') or 'all'
    args['spec_filters'] = [f.to_dict() for f in plan.get('spec_filters') or []]
    args['strict'] = True
    args['limit'] = 20
    return {'tool':'jlc_search','arguments':args}


def diagnose_empty(db: Any, query: str | None, plan: dict) -> dict:
    started = time.monotonic()
    deadline = started + DIAGNOSTIC_SECONDS
    variants = []
    if plan.get('library_type') not in (None,'all'):
        variants.append(('library_type', {'library_type':None}))
    if plan.get('package') or plan.get('packages'):
        variants.append(('package', {'package':None,'packages':None}))
    if plan.get('min_stock',10) > 10:
        variants.append(('min_stock', {'min_stock':10}))
    out = {'scope':'local_snapshot_stock_ge_10', 'blocking':[], 'tested':[],
           'diagnostics_complete':True, 'extra_queries':0,
           'note':'Only supplied library/package/stock restrictions are tested. Suggested changes may be unsuitable; multiple constraints may interact.'}
    if not variants:
        out['note'] = 'No library/package/stock counterfactual applies; other constraints may interact or lack catalog coverage.'
        return out
    steps = 0
    def interrupted():
        nonlocal steps
        steps += 1000
        return int(steps >= DIAGNOSTIC_VM_STEPS or time.monotonic() >= deadline)
    try:
        conn = sqlite3.connect(db.db_path.resolve().as_uri()+'?mode=ro', uri=True, timeout=0.05)
    except sqlite3.Error:
        logger.warning("Could not open snapshot for optional diagnostics", exc_info=True)
        out['diagnostics_complete'] = False
        out['status'] = 'diagnostic_failed'
        out['note'] += ' Diagnostic snapshot could not be opened.'
        return out
    conn.row_factory = sqlite3.Row
    conn.set_progress_handler(interrupted,1000)
    try:
        engine = SearchEngine(conn, db._subcategories, db._categories, db._subcategory_name_to_id,
                              db._category_name_to_id, db._category_to_subcategories)
        engine.diagnostic_deadline = deadline
        engine.diagnostic_rows_remaining = DIAGNOSTIC_POST_ROWS
        for name, changes in variants[:MAX_DIAGNOSTIC_QUERIES]:
            if time.monotonic() >= deadline:
                raise sqlite3.OperationalError('interrupted')
            variant = {**plan, **changes, 'limit':1, 'offset':0, 'count_unlisted':False, 'spec_sort':None}
            out['extra_queries'] += 1
            result = engine.search(query=query, **variant)
            if result.get('error') or result.get('ignored_filters'):
                out['diagnostics_complete'] = False
                continue
            complete = result.get('counts_complete',True)
            count = result.get('total',0)
            out['tested'].append({'constraint':name,'matches_without':count,
                                  'count_relation':'exact' if complete else 'at_least'})
            out['diagnostics_complete'] &= complete
            if count:
                retained = {key: ([f.to_dict() for f in value] if key == 'spec_filters' else value)
                            for key, value in plan.items() if value is not None and key not in changes
                            and key not in {'spec_sort','preferred_specs','limit','offset','count_unlisted'}}
                retained['query'] = query
                suggestion = {**out['tested'][-1], 'changed_constraints':changes, 'retained_constraints':retained,
                              'next_call':next_search(query,variant)}
                if suggestion['next_call'] is None:
                    suggestion['next_call_note'] = 'Keep the subcategory group shown in filters_applied; no equivalent single public call was generated.'
                out['blocking'].append(suggestion)
        if len(variants) > MAX_DIAGNOSTIC_QUERIES:
            out['diagnostics_complete'] = False
    except sqlite3.OperationalError as exc:
        out['diagnostics_complete'] = False
        if 'interrupt' in str(exc).lower() or 'locked' in str(exc).lower():
            out['status'] = 'budget_exhausted_or_busy'
            out['note'] += ' Diagnostic execution budget exhausted or snapshot busy.'
        else:
            logger.warning("Optional diagnostic query failed", exc_info=True)
            out['status'] = 'diagnostic_failed'
            out['note'] += ' Diagnostic query failed; no absence conclusion can be drawn.'
    finally:
        conn.close()
    out['elapsed_ms'] = round((time.monotonic()-started)*1000)
    return out
