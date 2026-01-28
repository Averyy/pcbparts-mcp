"""Search engine for parametric component search."""

import sqlite3
from typing import Any, Literal

from ..alternatives import SPEC_PARSERS
from ..subcategory_aliases import (
    resolve_subcategory_name as _resolve_subcategory_name,
    find_similar_subcategories as _find_similar_subcategories,
)
from .spec_filter import SpecFilter, get_attribute_names
from .resolvers import expand_query_synonyms, expand_package, resolve_manufacturer
from .query_builder import (
    build_fts_clause,
    build_subcategory_clause,
    build_library_type_clause,
    build_stock_clause,
    build_package_clause,
    build_manufacturer_clause,
    build_spec_filter_clauses,
    build_sort_clause,
    needs_numeric_post_filter,
)
from .result import row_to_dict


class SearchEngine:
    """Search engine for parametric component queries.

    Handles SQL query building, execution, and result transformation.
    Instantiated once by ComponentDatabase after caches are loaded.
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        subcategories: dict[int, dict[str, Any]],
        categories: dict[int, dict[str, Any]],
        subcategory_name_to_id: dict[str, int],
        category_name_to_id: dict[str, int],
        category_to_subcategories: dict[int, list[int]] | None = None,
    ):
        """Initialize the search engine.

        Args:
            conn: SQLite connection (must have row_factory set)
            subcategories: Dict mapping subcategory IDs to info
            categories: Dict mapping category IDs to info
            subcategory_name_to_id: Lowercase name -> ID mapping
            category_name_to_id: Lowercase name -> ID mapping
            category_to_subcategories: Pre-built category_id -> [subcategory_ids] mapping
        """
        self._conn = conn
        self._subcategories = subcategories
        self._categories = categories
        self._subcategory_name_to_id = subcategory_name_to_id
        self._category_name_to_id = category_name_to_id
        self._category_to_subcategories = category_to_subcategories or {}

    def resolve_subcategory_name(self, name: str) -> int | None:
        """Resolve subcategory name to ID. Case-insensitive, supports partial match.

        Matching priority:
        1. Common alias (e.g., "MLCC" -> "Multilayer Ceramic Capacitors MLCC - SMD/SMT")
        2. Exact match (e.g., "crystals" -> "crystals")
        3. Shortest containing match (e.g., "crystal" -> "crystals" not "crystal oscillators")

        Returns:
            Subcategory ID if found, None otherwise.
        """
        return _resolve_subcategory_name(name, self._subcategory_name_to_id)

    def resolve_category_name(self, name: str) -> int | None:
        """Resolve category name to ID. Case-insensitive, supports partial match.

        Matching priority:
        1. Exact match
        2. Shortest containing match (most specific)

        Returns:
            Category ID if found, None otherwise.
        """
        name_lower = name.lower()

        # Exact match first
        if name_lower in self._category_name_to_id:
            return self._category_name_to_id[name_lower]

        # Collect all partial matches
        matches: list[tuple[str, int]] = []
        for cat_name_lower, cat_id in self._category_name_to_id.items():
            if name_lower in cat_name_lower:
                matches.append((cat_name_lower, cat_id))

        if not matches:
            return None

        # Return shortest match (most specific)
        matches.sort(key=lambda x: len(x[0]))
        return matches[0][1]

    def _find_similar_subcategories(self, name: str, limit: int = 5) -> list[dict[str, Any]]:
        """Find subcategories similar to the given name (for error suggestions)."""
        return _find_similar_subcategories(
            name, self._subcategory_name_to_id, self._subcategories, limit
        )

    def search(
        self,
        query: str | None = None,
        subcategory_id: int | None = None,
        subcategory_name: str | None = None,
        category_id: int | None = None,
        category_name: str | None = None,
        spec_filters: list[SpecFilter] | None = None,
        library_type: str | None = None,
        prefer_no_fee: bool = True,
        min_stock: int = 100,
        package: str | None = None,
        packages: list[str] | None = None,
        manufacturer: str | None = None,
        match_all_terms: bool = True,
        sort_by: Literal["stock", "price", "relevance"] = "stock",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search components with parametric filtering.

        Args:
            query: Text search (FTS) for lcsc, mpn, manufacturer, description
            subcategory_id: Filter by subcategory ID
            subcategory_name: Filter by subcategory name
            category_id: Filter by category ID
            category_name: Filter by category name
            spec_filters: List of SpecFilter for attribute-based filtering
            library_type: Filter by library type
            prefer_no_fee: Sort preference for basic/preferred first
            min_stock: Minimum stock quantity
            package: Single package filter
            packages: Multiple package filter (OR logic)
            manufacturer: Manufacturer filter
            match_all_terms: FTS matching mode
            sort_by: Sort order
            limit: Max results
            offset: Pagination offset

        Returns:
            Search results with metadata
        """
        # Expand query synonyms
        if query:
            query = expand_query_synonyms(query)

        # Resolve subcategory_name to ID
        resolved_subcategory_id = subcategory_id
        resolved_subcategory_display_name: str | None = None
        if subcategory_name and not subcategory_id:
            resolved_subcategory_id = self.resolve_subcategory_name(subcategory_name)
            if resolved_subcategory_id is None:
                similar = self._find_similar_subcategories(subcategory_name, limit=5)
                return {
                    "error": f"Subcategory not found: '{subcategory_name}'",
                    "hint": "Use list_categories and get_subcategories to see available options",
                    "similar_subcategories": similar,
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }
            resolved_subcategory_display_name = self._subcategories[resolved_subcategory_id]["name"]

        # Resolve category_name to ID
        resolved_category_id = category_id
        resolved_category_display_name: str | None = None
        if category_name and not category_id:
            resolved_category_id = self.resolve_category_name(category_name)
            if resolved_category_id is None:
                return {
                    "error": f"Category not found: '{category_name}'",
                    "hint": "Use list_categories to see available categories",
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }
            resolved_category_display_name = self._categories[resolved_category_id]["name"]

        # Build query
        sql_parts = ["SELECT * FROM components WHERE 1=1"]
        count_parts = ["SELECT COUNT(*) FROM components WHERE 1=1"]
        params: list[Any] = []
        count_params: list[Any] = []

        # FTS clause
        if query:
            # Validate query
            if len(query) > 500:
                return {
                    "error": "Query too long (max 500 characters)",
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }
            if any(ord(c) < 32 and c not in '\t\n\r' for c in query) or '\x00' in query:
                return {
                    "error": "Query contains invalid characters",
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }

            fts_sql, fts_params = build_fts_clause(query, match_all_terms)
            if not fts_sql:
                return {
                    "error": "Query contains no searchable terms",
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }
            sql_parts.append(fts_sql)
            count_parts.append(fts_sql)
            params.extend(fts_params)
            count_params.extend(fts_params)

        # Subcategory/category filter
        subcat_sql, subcat_params = build_subcategory_clause(
            resolved_subcategory_id, resolved_category_id, self._subcategories,
            self._category_to_subcategories
        )
        if subcat_sql:
            sql_parts.append(subcat_sql)
            count_parts.append(subcat_sql)
            params.extend(subcat_params)
            count_params.extend(subcat_params)

        # Library type filter
        lib_type_sql = build_library_type_clause(library_type)
        if lib_type_sql:
            sql_parts.append(lib_type_sql)
            count_parts.append(lib_type_sql)

        # Stock filter
        stock_sql, stock_params = build_stock_clause(min_stock)
        if stock_sql:
            sql_parts.append(stock_sql)
            count_parts.append(stock_sql)
            params.extend(stock_params)
            count_params.extend(stock_params)

        # Package filter (expand families)
        expanded_packages: list[str] = []
        if packages:
            for pkg in packages:
                expanded_packages.extend(expand_package(pkg))
        elif package:
            expanded_packages = expand_package(package)

        pkg_sql, pkg_params = build_package_clause(expanded_packages)
        if pkg_sql:
            sql_parts.append(pkg_sql)
            count_parts.append(pkg_sql)
            params.extend(pkg_params)
            count_params.extend(pkg_params)

        # Manufacturer filter
        if manufacturer:
            resolved_mfr = resolve_manufacturer(manufacturer)
            mfr_sql, mfr_params = build_manufacturer_clause(resolved_mfr)
            sql_parts.append(mfr_sql)
            count_parts.append(mfr_sql)
            params.extend(mfr_params)
            count_params.extend(mfr_params)

        # Spec filters
        post_filter_metadata: list[tuple[SpecFilter, set[str], Any, float | None]] = []
        if spec_filters:
            spec_sqls, spec_params, post_filter_metadata = build_spec_filter_clauses(spec_filters)
            for spec_sql in spec_sqls:
                sql_parts.append(spec_sql)
                count_parts.append(spec_sql)
            params.extend(spec_params)
            count_params.extend(spec_params)

        # Sorting
        sort_clause = build_sort_clause(sort_by, prefer_no_fee, bool(query))
        sql_parts.append(sort_clause)

        # Determine fetch limit (over-fetch if post-filtering needed)
        has_numeric_filters = spec_filters and any(
            needs_numeric_post_filter(sf) for sf in spec_filters
        )
        fetch_limit = limit * 10 if has_numeric_filters else limit
        fetch_limit = min(fetch_limit, 500)

        # Pagination
        sql_parts.append("LIMIT ? OFFSET ?")
        params.extend([fetch_limit, offset])

        # Execute queries
        sql = " ".join(sql_parts)
        count_sql = " ".join(count_parts)

        cursor = self._conn.execute(sql, params)
        rows = cursor.fetchall()

        # Combined count + library type distribution query
        lib_count_sql = count_sql.replace("SELECT COUNT(*)", "SELECT library_type, COUNT(*)")
        lib_count_sql_clean = lib_count_sql
        for pattern in ["AND library_type = 'b'", "AND library_type = 'p'", "AND library_type = 'e'"]:
            lib_count_sql_clean = lib_count_sql_clean.replace(pattern, "")
        lib_count_sql_clean += " GROUP BY library_type"

        lib_cursor = self._conn.execute(lib_count_sql_clean, count_params)
        lib_type_map = {"b": "basic", "p": "preferred", "e": "extended"}
        library_type_counts = {"basic": 0, "preferred": 0, "extended": 0}
        total = 0
        for row in lib_cursor:
            lib_name = lib_type_map.get(row[0], row[0])
            count = row[1]
            if lib_name in library_type_counts:
                library_type_counts[lib_name] = count
            total += count

        # Post-filter for numeric spec comparisons
        results = []
        for row in rows:
            part = row_to_dict(row, self._subcategories)

            if post_filter_metadata:
                passes = True
                part_specs = part.get("specs", {})

                for spec_filter, attr_names_set, parser, target_value in post_filter_metadata:
                    if parser and spec_filter.operator in (">=", "<=", ">", "<", "="):
                        if target_value is None:
                            continue

                        part_value = None
                        for attr_name, attr_value in part_specs.items():
                            if attr_name in attr_names_set:
                                part_value = parser(attr_value)
                                if part_value is not None:
                                    break

                        if part_value is None:
                            passes = False
                            break

                        epsilon = abs(target_value) * 1e-9 if target_value != 0 else 1e-15
                        eq_epsilon = abs(target_value) * 0.01 if target_value != 0 else 1e-9

                        if spec_filter.operator == "=" and abs(part_value - target_value) > eq_epsilon:
                            passes = False
                            break
                        elif spec_filter.operator == ">=" and part_value < target_value - epsilon:
                            passes = False
                            break
                        elif spec_filter.operator == "<=" and part_value > target_value + epsilon:
                            passes = False
                            break
                        elif spec_filter.operator == ">" and part_value <= target_value + epsilon:
                            passes = False
                            break
                        elif spec_filter.operator == "<" and part_value >= target_value - epsilon:
                            passes = False
                            break

                if not passes:
                    continue

            results.append(part)
            if len(results) >= limit:
                break

        no_fee_available = library_type_counts["basic"] > 0 or library_type_counts["preferred"] > 0

        return {
            "results": results,  # Already limited by loop break condition
            "total": total,
            "page_info": {
                "limit": limit,
                "offset": offset,
                "returned": len(results),
            },
            "filters_applied": {
                "query": query,
                "subcategory_id": resolved_subcategory_id,
                "subcategory_name": subcategory_name,
                "subcategory_resolved": resolved_subcategory_display_name,
                "category_id": resolved_category_id,
                "category_name": category_name,
                "category_resolved": resolved_category_display_name,
                "spec_filters": [f.to_dict() for f in (spec_filters or [])],
                "library_type": library_type,
                "prefer_no_fee": prefer_no_fee,
                "min_stock": min_stock,
                "package": package,
                "packages": packages,
                "manufacturer": manufacturer,
                "match_all_terms": match_all_terms,
            },
            "library_type_counts": library_type_counts,
            "no_fee_available": no_fee_available,
        }
