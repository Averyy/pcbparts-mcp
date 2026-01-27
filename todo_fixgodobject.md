# TODO: Refactor ComponentDatabase God Object

## Problem

`src/jlcpcb_mcp/db.py` contains a 600+ line `ComponentDatabase` class that handles 14 different responsibilities. This violates the Single Responsibility Principle and makes the code harder to test, maintain, and reuse.

## Current Responsibilities

| Responsibility | Methods | Lines (approx) |
|----------------|---------|----------------|
| Connection management | `_ensure_db()`, `close()`, `_conn`, `_conn_lock` | 40 |
| Database building | `_build_database()` | 20 |
| Cache loading | `_load_caches()` | 25 |
| Name resolution | `resolve_subcategory_name()`, `resolve_category_name()`, `_find_similar_subcategories()` | 80 |
| Package expansion | `_expand_package()` | 15 |
| Manufacturer resolution | `_resolve_manufacturer()` | 20 |
| Attribute aliases | `_get_attribute_names()` | 15 |
| Search | `search()` | 150 |
| Single lookups | `get_by_lcsc()`, `get_by_lcsc_batch()` | 50 |
| Category queries | `find_by_subcategory()`, `get_categories_for_client()` | 70 |
| Row transformation | `_row_to_dict()` | 40 |
| Attribute discovery | `list_attributes()` | 100 |
| Stats | `get_stats()` | 30 |

## Problems

1. **Testing difficulty** - Can't unit test name resolution without setting up a full SQLite database
2. **No reuse** - `client.py` had to reimplement name resolution instead of importing shared logic
3. **Navigation** - 600 lines to scroll through to find anything
4. **Coupling** - All responsibilities are tightly coupled through `self`

## Proposed Refactor

### Phase 1: Extract Pure Functions (Low Risk)

Move stateless logic to separate modules:

```
src/jlcpcb_mcp/
  subcategory_aliases.py    # SUBCATEGORY_ALIASES + resolve_subcategory_name()  [DONE]
  package_expansion.py      # PACKAGE_FAMILIES + expand_package()
  attribute_aliases.py      # ATTRIBUTE_ALIASES + get_attribute_names()
```

### Phase 2: Extract Query Builders (Medium Risk)

```
src/jlcpcb_mcp/
  query_builder.py          # SQL query construction for search()
  spec_filter.py            # SpecFilter class + filter logic (already partially separate)
```

### Phase 3: Split Database Class (Higher Risk)

```
src/jlcpcb_mcp/
  db/
    __init__.py             # Re-export public API
    connection.py           # Connection management, _ensure_db(), close()
    search.py               # search(), find_by_subcategory()
    lookup.py               # get_by_lcsc(), get_by_lcsc_batch()
    metadata.py             # list_attributes(), get_stats(), get_categories_for_client()
    builder.py              # _build_database()
```

## Acceptance Criteria

- [ ] All existing tests pass
- [ ] No new test files needed for Phase 1 (pure functions testable in isolation)
- [ ] `ComponentDatabase` reduced to <200 lines (connection + delegation)
- [ ] Each extracted module has clear single responsibility

## Notes

- Phase 1 is already partially done (SUBCATEGORY_ALIASES moved to subcategory_aliases.py)
- Consider doing this incrementally across multiple PRs
- Keep backward compatibility by re-exporting from original locations initially
