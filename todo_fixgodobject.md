# TODO: Refactor ComponentDatabase God Object

## Problem

`src/jlcpcb_mcp/db.py` has grown to **1,596 lines** with `ComponentDatabase` spanning ~1,200 lines. The `search()` method alone is **547 lines**. This violates the Single Responsibility Principle and makes the code harder to test, maintain, and navigate.

## Current State (January 2026)

| Responsibility | Methods | Lines |
|----------------|---------|-------|
| Connection/init | `__init__`, `_ensure_db`, `close` | 40 |
| Database building | `_build_database` | 44 |
| Cache loading | `_load_caches` | 24 |
| Name resolution | `get_subcategory_name`, `get_category_for_subcategory`, `resolve_subcategory_name`, `resolve_category_name`, `_find_similar_subcategories` | 64 |
| Package expansion | `_expand_package` | 17 |
| Manufacturer resolution | `_resolve_manufacturer` | 21 |
| Attribute aliases | `_get_attribute_names` | 16 |
| **Search** | `search` | **547** |
| Single lookups | `get_by_lcsc`, `get_by_lcsc_batch` | 54 |
| Category queries | `find_by_subcategory`, `get_categories_for_client` | 132 |
| Row transformation | `_row_to_dict` | 43 |
| Attribute discovery | `list_attributes` | 147 |
| Stats | `get_stats` | 38 |

Also in db.py but outside the class:
- `SpecFilter` class (lines 316-384, ~70 lines)
- Helper functions: `expand_query_synonyms`, `_escape_like`, `_is_integer`, `generate_value_patterns` (lines 167-314, ~150 lines)

## What's Been Extracted

- [x] `subcategory_aliases.py` - 531 lines (aliases + resolution helpers)
- [x] `manufacturer_aliases.py` - 261 lines
- [x] `parsers.py` - 588 lines (value parsing)
- [x] `smart_parser.py` - 1,152 lines (query interpretation)

## Problems

1. **547-line search() method** - Impossible to understand or modify safely
2. **Testing requires full database** - Can't unit test pure logic in isolation
3. **Navigation nightmare** - 1,600 lines to scroll through
4. **Tight coupling** - All responsibilities interconnected through `self`

## Priority: Break Up search()

The `search()` method (lines 618-1164) is the biggest problem. It handles:
- Parameter validation and normalization
- Subcategory/category name resolution
- Query synonym expansion
- SQL query building with dynamic WHERE clauses
- Spec filter parsing and application
- Package expansion
- Manufacturer resolution
- Result sorting and pagination
- Response formatting

### Recommended Extraction

```
src/jlcpcb_mcp/
  search/
    __init__.py           # Re-export SearchEngine
    engine.py             # SearchEngine class (orchestration only, <100 lines)
    query_builder.py      # SQL WHERE clause construction
    param_resolver.py     # Name→ID resolution, package expansion, mfr resolution
    response.py           # Result formatting, _row_to_dict
```

This would reduce `search()` to ~50-100 lines of orchestration.

## Secondary: Extract Other Query Methods

```
src/jlcpcb_mcp/
  db/
    __init__.py           # Re-export ComponentDatabase (slim version)
    connection.py         # Connection management, _ensure_db(), close()
    lookup.py             # get_by_lcsc(), get_by_lcsc_batch()
    categories.py         # find_by_subcategory(), get_categories_for_client()
    attributes.py         # list_attributes() (147 lines)
    stats.py              # get_stats()
```

## Acceptance Criteria

- [ ] All existing tests pass (774 lines in test_db.py)
- [ ] `search()` method reduced to <100 lines (orchestration only)
- [ ] `ComponentDatabase` reduced to <300 lines
- [ ] Query building logic unit-testable without SQLite
- [ ] Each extracted module has clear single responsibility

## Notes

- Beta status with no external users - breaking changes acceptable
- Do incrementally: extract search() first, then other methods
- Keep backward compatibility by re-exporting from `db.py` initially
- The `SpecFilter` class (lines 316-384) is already somewhat isolated and could move to `search/filters.py`
