"""Search engine for parametric component search."""

import json
import logging
import math
import re
import sqlite3
from typing import Any, Literal

from ..config import DEFAULT_MIN_STOCK
from ..mosfet import rds_gate_min_json, rds_on_at_drive
from ..alternatives import SPEC_PARSERS, DIMENSION_SPEC_FIELDS
from ..parsers import (
    RESISTANCE_MATCH_TOLERANCE, parse_dimensions_from_package, parse_esp32_module_memory, parse_resistance, parse_voltage,
)
from ..subcategory_aliases import (
    resolve_subcategory_name as _resolve_subcategory_name,
    find_similar_subcategories as _find_similar_subcategories,
)
from .spec_filter import (
    CONNECTOR_COLUMN_NAMES, FUSE_ATTRIBUTE_MAP, RANGE_SPECS, FuseFilter, SpecFilter,
    connector_value, get_attribute_names,
)
from .resolvers import expand_query_synonyms, expand_package, resolve_manufacturer
from .mpn import MPN_MATCH_NAMES, mpn_match_rank, normalize_mpn, looks_like_mpn
from .query_builder import (
    build_fts_clause,
    build_subcategory_clause,
    build_library_type_clause,
    build_stock_clause,
    build_package_clause,
    index_package_names,
    package_needs_catalog,
    package_has_constraints,
    resolve_package_constraints,
    build_manufacturer_clause,
    build_mounting_type_clause,
    build_spec_filter_clauses,
    build_sort_clause,
)
from .result import row_to_dict

logger = logging.getLogger(__name__)


# Post-filtered searches check at most this many SQL matches (MOSFETs with a Vgs(th): ~29k, ~0.2s)
POST_FILTER_SCAN_ROWS = 50_000


def _passes_post_filters(
    part_specs: dict[str, str],
    package: str | None,
    post_filter_metadata: list[tuple[SpecFilter, set[str], Any, float | None]],
    subcategory_id: int | None = None,
) -> bool:
    """Whether a part's specs meet every filter SQL couldn't apply."""
    for spec_filter, attr_names_set, parser, target_value in post_filter_metadata:
        if (isinstance(spec_filter, FuseFilter) and spec_filter.subcategory_id is not None
                and spec_filter.subcategory_id != subcategory_id):
            continue
        if not parser or spec_filter.operator not in (">=", "<=", ">", "<", "=") or target_value is None:
            continue

        if attr_names_set & RANGE_SPECS:
            values = [v for name, v in part_specs.items() if name in attr_names_set]
            if not any(_range_passes(v, parser, spec_filter.operator, target_value) for v in values):
                return False
            continue

        part_value = None
        for attr_name, attr_value in part_specs.items():
            if attr_name in attr_names_set:
                part_value = parser(attr_value)
                if part_value is not None:
                    break

        if part_value is None and spec_filter.name in DIMENSION_SPEC_FIELDS:
            # Recover from package string when the spec field is "-" (null);
            # ~70% of null-height aluminum electrolytics encode dims here.
            diameter_mm, height_mm = parse_dimensions_from_package(package or "")
            part_value = diameter_mm if spec_filter.name == "Diameter" else height_mm

        if part_value is None:
            return False

        epsilon = abs(target_value) * 1e-9 if target_value != 0 else 1e-15

        # Frequency matching needs wider tolerance for RF components
        # Common bands like "2.4GHz WiFi" spans 2.4-2.5GHz, and databases
        # often store "2.45GHz" when users search "2.4GHz"
        is_frequency = any("frequency" in name.lower() for name in attr_names_set)
        if is_frequency:
            # Use 5% tolerance for frequency (allows 2.4GHz to match 2.45GHz)
            eq_epsilon = abs(target_value) * 0.05 if target_value != 0 else 1e-9
        elif parser is parse_resistance:
            eq_epsilon = abs(target_value) * RESISTANCE_MATCH_TOLERANCE if target_value != 0 else 1e-9
        else:
            # Use 1% tolerance for other specs
            eq_epsilon = abs(target_value) * 0.01 if target_value != 0 else 1e-9

        if spec_filter.operator == "=" and abs(part_value - target_value) > eq_epsilon:
            return False
        elif spec_filter.operator == ">=" and part_value < target_value - epsilon:
            return False
        elif spec_filter.operator == "<=" and part_value > target_value + epsilon:
            return False
        elif spec_filter.operator == ">" and part_value <= target_value + epsilon:
            return False
        elif spec_filter.operator == "<" and part_value >= target_value - epsilon:
            return False
    return True


def _signed(parser: Any, text: str) -> float | None:
    """parse_voltage("-15V") is 15; ranges need the sign ("-15V~-5V")."""
    value = parser(text)
    if value is not None and text.strip().startswith("-"):
        return -abs(value)
    return value


def _range_passes(value: str, parser: Any, operator: str, target: float) -> bool:
    """A range-valued spec ("2.7V~5.5V", "1.71V~1.89V、2.25V~5.5V", "3.3V") against a filter:
    = : the target is inside one range; >= / > : one range reaches it; <= / < : one goes down to it.
    1% slack, as other "=" filters have."""
    slack = abs(target) * 0.01 if target else 1e-9
    for item in value.split("、"):
        low_text, sep, high_text = item.partition("~")
        low = _signed(parser, low_text)
        high = _signed(parser, high_text) if sep else low
        if low is None or high is None:
            continue
        low, high = min(low, high), max(low, high)
        if ((operator == "=" and low - slack <= target <= high + slack)
                or (operator == ">=" and high >= target - slack) or (operator == ">" and high > target)
                or (operator == "<=" and low <= target + slack) or (operator == "<" and low < target)):
            return True
    return False


def _spec_preference_rank(attributes: str | None, name: str, target: str) -> int:
    """Rank listed PD role/output matches first, keeping parts with missing attributes."""
    for attr_name, value in json.loads(attributes or "[]"):
        if attr_name != name:
            continue
        if name == "Output Voltage":
            voltage = parse_voltage(target)
            if voltage is not None:
                for item in value.split("、"):
                    output = parse_voltage(item) if "~" not in item else None
                    if output is not None and math.isclose(output, voltage, rel_tol=1e-9, abs_tol=1e-12):
                        return 0
        elif target.casefold() in (item.strip().casefold() for item in value.split("、")):
            return 0
    return 1


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
        self._conn.create_function("mpn_match_rank", 2, mpn_match_rank, deterministic=True)
        self._conn.create_function("connector_value", 2, connector_value, deterministic=True)
        self._conn.create_function("spec_preference_rank", 3, _spec_preference_rank, deterministic=True)
        self._conn.create_function("rds_gate_min", 1, rds_gate_min_json, deterministic=True)
        self._package_names: dict[str, list[str]] | None = None
        self._fuse_package_types: dict[str, set[int]] = {}
        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(components)")
        }
        self._connector_columns = CONNECTOR_COLUMN_NAMES <= columns
        self._mosfet_gate_column = "rds_gate_min_v" in columns
        self._subcategories = subcategories
        self._categories = categories
        self._subcategory_name_to_id = subcategory_name_to_id
        self._category_name_to_id = category_name_to_id
        self._category_to_subcategories = category_to_subcategories or {}

    def _get_package_names(self) -> dict[str, list[str]]:
        if self._package_names is None:
            self._package_names = index_package_names([
                row[0] for row in self._conn.execute("SELECT DISTINCT package FROM components WHERE package IS NOT NULL")
            ])
        return self._package_names

    def resolve_package_constraints(self, packages: list[str]) -> tuple[list[str], list[dict[str, str]]]:
        """Resolve unavailable suffixes using the catalog across all subcategories."""
        if not any(package_has_constraints(pkg) for pkg in packages):
            return packages, []
        return resolve_package_constraints(packages, self._get_package_names())

    def packages_are_resettable_fuses(self, packages: list[str]) -> bool:
        """Whether every requested package has resettable but no disposable fuses."""
        resettable = self.resolve_subcategory_name("Resettable Fuses")
        disposable = self.resolve_subcategory_name("Disposable fuses")
        if not packages or not resettable or not disposable:
            return False
        for package in packages:
            key = package.upper()
            if key not in self._fuse_package_types:
                expanded = [package, *expand_package(package)]
                catalog = self._get_package_names() if any(package_needs_catalog(p) for p in expanded) else None
                clause, params = build_package_clause(expanded, catalog)
                self._fuse_package_types[key] = {
                    row[0] for row in self._conn.execute(
                        "SELECT DISTINCT subcategory_id FROM components "
                        "WHERE subcategory_id IN (?, ?) AND stock >= ? " + clause,
                        [resettable, disposable, DEFAULT_MIN_STOCK, *params],
                    )
                }
            if self._fuse_package_types[key] != {resettable}:
                return False
        return True

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

    def _execute_search(
        self,
        query: str | None,
        subcategory_id: int | None,
        category_id: int | None,
        spec_filters: list[SpecFilter] | None,
        library_type: str | None,
        min_stock: int,
        expanded_packages: list[str],
        manufacturer: str | None,
        mounting_type: str | None,
        match_all_terms: bool,
        sort_by: Literal["stock", "price", "relevance"],
        prefer_no_fee: bool,
        limit: int,
        offset: int,
        subcategory_ids: list[int] | None = None,
        part_number: str | None = None,
        connector_series: str | None = None,
        connector_manufacturer: str | None = None,
        preferred_specs: list[SpecFilter] | None = None,
        gate_drive_v: float | None = None,
    ) -> dict[str, Any]:
        """Execute a search query with pre-resolved parameters.

        This is the core search execution method. It builds SQL, executes queries,
        performs post-filtering, and returns results. Does NOT do parameter resolution
        or validation - callers must handle that.

        Args:
            query: FTS search query (already validated/expanded)
            subcategory_id: Resolved subcategory ID
            category_id: Resolved category ID
            spec_filters: List of SpecFilter objects
            library_type: Library type filter
            min_stock: Minimum stock threshold
            expanded_packages: Pre-expanded package list
            manufacturer: Manufacturer name (already resolved)
            mounting_type: Mounting type filter
            match_all_terms: FTS AND/OR mode
            sort_by: Sort order
            prefer_no_fee: Whether to prefer basic/preferred parts
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            Dict with results, total, library_type_counts, no_fee_available
        """
        sql_parts = ["SELECT * FROM components WHERE 1=1"]
        count_parts = ["SELECT COUNT(*) FROM components WHERE 1=1"]
        params: list[Any] = []
        count_params: list[Any] = []

        # FTS clause
        if query:
            fts_sql, fts_params = build_fts_clause(query, match_all_terms)
            if fts_sql:
                sql_parts.append(fts_sql)
                count_parts.append(fts_sql)
                params.extend(fts_params)
                count_params.extend(fts_params)

        # Subcategory/category filter
        subcat_sql, subcat_params = build_subcategory_clause(
            subcategory_id, category_id, self._subcategories,
            self._category_to_subcategories, subcategory_ids,
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

        # Package filter
        if self._package_names is None and any(package_needs_catalog(pkg) for pkg in expanded_packages):
            self._get_package_names()
        pkg_sql, pkg_params = build_package_clause(expanded_packages, self._package_names)
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

        # Mounting type filter
        if mounting_type:
            mount_sql, mount_params = build_mounting_type_clause(mounting_type)
            if mount_sql:
                sql_parts.append(mount_sql)
                count_parts.append(mount_sql)
                params.extend(mount_params)
                count_params.extend(mount_params)

        # Spec filters
        post_filter_metadata: list[tuple[SpecFilter, set[str], Any, float | None]] = []
        ignored_filters: list[dict[str, str]] = []
        if spec_filters:
            spec_sqls, spec_params_list, post_filter_metadata, ignored_filters = build_spec_filter_clauses(
                spec_filters, connector_columns=self._connector_columns,
            )
            for spec_sql in spec_sqls:
                sql_parts.append(spec_sql)
                count_parts.append(spec_sql)
            params.extend(spec_params_list)
            count_params.extend(spec_params_list)

        # Sorting
        sort_clause = build_sort_clause(sort_by, prefer_no_fee, bool(query))
        ranks = []
        if part_number:
            ranks.append("mpn_match_rank(mpn, ?)")
            params.append(part_number)
        if gate_drive_v is not None:
            gate = "rds_gate_min_v" if self._mosfet_gate_column else "rds_gate_min(components.attributes)"
            ranks.append(f"CASE WHEN {gate} <= ? THEN 0 ELSE 1 END")
            params.append(gate_drive_v)
            sort_clause += ", lcsc"
        if connector_manufacturer:
            ranks.append("CASE WHEN manufacturer = ? THEN 0 ELSE 1 END")
            params.append(connector_manufacturer)
            sort_clause += ", lcsc"
        if connector_series:
            if self._connector_columns:
                ranks.append("CASE WHEN upper(trim(reference_series)) = upper(?) THEN 0 ELSE 1 END")
            else:
                ranks.append(
                    "CASE WHEN EXISTS (SELECT 1 FROM json_each(components.attributes) j "
                    "WHERE json_extract(j.value, '$[0]') = 'Reference Series' "
                    "AND upper(trim(json_extract(j.value, '$[1]'))) = upper(?)) THEN 0 ELSE 1 END"
                )
            params.append(connector_series)
            sort_clause += ", lcsc"  # Stable page boundaries when stock/price ties.
        for preference in preferred_specs or []:
            ranks.append("spec_preference_rank(components.attributes, ?, ?)")
            params.extend([preference.name, preference.value])
        if preferred_specs:
            sort_clause += ", lcsc"  # Keep ranked pages stable across stock/price ties.
        if ranks:
            sort_clause = sort_clause.replace("ORDER BY ", "ORDER BY " + ", ".join(ranks) + ", ", 1)
        sql_parts.append(sort_clause)

        base_params = list(params)

        # Execute queries (post-filtered searches fetch their page in _post_filtered_page)
        sql = " ".join(sql_parts) + " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        count_sql = " ".join(count_parts)

        # Combined count + library type distribution query
        lib_count_sql = count_sql.replace("SELECT COUNT(*)", "SELECT library_type, COUNT(*)")
        lib_count_sql += " GROUP BY library_type"
        mpn_counts = {"part_number": part_number, **dict.fromkeys(MPN_MATCH_NAMES, 0)} if part_number else None
        if part_number and not post_filter_metadata:
            lib_count_sql = count_sql.replace(
                "SELECT COUNT(*)", "SELECT library_type, COUNT(*), mpn_match_rank(mpn, ?) AS mpn_rank"
            ) + " GROUP BY library_type, mpn_rank"
            count_params.insert(0, part_number)

        # Defense-in-depth: list-param caps at the tool boundary keep real queries far from
        # SQLite's limits, but if a statement is still rejected (e.g. too many bound
        # variables), return a clean error dict rather than leak an unhandled exception.
        try:
            rows = [] if post_filter_metadata else self._conn.execute(sql, params).fetchall()
            lib_rows = self._conn.execute(lib_count_sql, count_params).fetchall()
        except sqlite3.OperationalError:
            logger.error("Search SQL execution failed", exc_info=True)
            return {
                "error": "Search failed: query too complex. Reduce the number of filters.",
                "results": [],
                "total": 0,
                "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                "no_fee_available": False,
            }

        lib_type_map = {"b": "basic", "p": "preferred", "e": "extended"}
        library_type_counts = {"basic": 0, "preferred": 0, "extended": 0}
        total = 0
        for row in lib_rows:
            lib_name = lib_type_map.get(row[0], row[0])
            count = row[1]
            if lib_name in library_type_counts:
                library_type_counts[lib_name] += count
            if mpn_counts is not None and not post_filter_metadata:
                mpn_counts[MPN_MATCH_NAMES[row[2]]] += count
            total += count

        if post_filter_metadata:
            # SQL can't apply these, so every candidate is checked: the page comes from the parts
            # that pass, and total counts them (the SQL count also had the ones that fail)
            results, library_type_counts, complete = self._post_filtered_page(
                sql_parts, base_params, post_filter_metadata, limit, offset, mpn_counts
            )
            total = sum(library_type_counts.values())
        else:
            results = [row_to_dict(row, self._subcategories) for row in rows]

        if part_number:
            for part in results:
                part["mpn_match"] = MPN_MATCH_NAMES[mpn_match_rank(part["model"], part_number)]
        if gate_drive_v is not None:
            for part in results:
                part["rds_on_at_drive"] = rds_on_at_drive(part["specs"].get("RDS(on)", ""), gate_drive_v)

        no_fee_available = library_type_counts["basic"] > 0 or library_type_counts["preferred"] > 0

        result = {
            "results": results,
            "total": total,
            "library_type_counts": library_type_counts,
            "no_fee_available": no_fee_available,
            "ignored_filters": ignored_filters,
        }
        if post_filter_metadata and not complete:
            result["counts_complete"] = False
        if mpn_counts is not None:
            result["mpn_matches"] = mpn_counts
        return result

    def _post_filtered_page(
        self,
        sql_parts: list[str],
        params: list[Any],
        post_filter_metadata: list[tuple[SpecFilter, set[str], Any, float | None]],
        limit: int,
        offset: int,
        mpn_counts: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, int], bool]:
        """Check SQL matches against post-filters. Returns the page, library counts of passing
        matches, and whether every match was checked (at most POST_FILTER_SCAN_ROWS are)."""
        scan_sql = " ".join(sql_parts).replace(
            "SELECT * FROM components", "SELECT rowid, attributes, package, mpn, library_type, subcategory_id FROM components", 1
        ) + " LIMIT ?"
        passed = 0
        library_counts = {"basic": 0, "preferred": 0, "extended": 0}
        library_names = {"b": "basic", "p": "preferred", "e": "extended"}
        scanned = 0
        page_ids: list[int] = []
        for rowid, attributes, package, mpn, library, subcategory in self._conn.execute(scan_sql, [*params, POST_FILTER_SCAN_ROWS]):
            scanned += 1
            try:
                specs = {name: value for name, value in json.loads(attributes)} if attributes else {}
            except (json.JSONDecodeError, TypeError, ValueError):
                specs = {}
            # ESP32 module memory is encoded in ordering codes, not catalog attributes.
            # Only derive it for a requested module-memory filter; unknown codes cannot pass.
            if any(f.name in ("Module Flash", "Module PSRAM") for f, *_ in post_filter_metadata):
                flash, psram = parse_esp32_module_memory(mpn)
                if flash is not None:
                    specs["Module Flash"] = f"{flash}MB"
                if psram is not None:
                    specs["Module PSRAM"] = f"{psram}MB"
            if _passes_post_filters(specs, package, post_filter_metadata, subcategory):
                passed += 1
                if mpn_counts is not None:
                    mpn_counts[MPN_MATCH_NAMES[mpn_match_rank(mpn, mpn_counts["part_number"])]] += 1
                name = library_names.get(library, library)
                if name in library_counts:
                    library_counts[name] += 1
                if offset < passed <= offset + limit:
                    page_ids.append(rowid)
        results: list[dict[str, Any]] = []
        if page_ids:
            by_id = {
                row["rowid"]: row for row in self._conn.execute(
                    f"SELECT rowid, * FROM components WHERE rowid IN ({','.join('?' * len(page_ids))})", page_ids
                )
            }
            results = [row_to_dict(by_id[i], self._subcategories) for i in page_ids if i in by_id]
        return results, library_counts, scanned < POST_FILTER_SCAN_ROWS

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
        min_stock: int = DEFAULT_MIN_STOCK,
        package: str | None = None,
        packages: list[str] | None = None,
        manufacturer: str | None = None,
        mounting_type: str | None = None,
        match_all_terms: bool = True,
        sort_by: Literal["stock", "price", "relevance"] = "stock",
        limit: int = 50,
        offset: int = 0,
        subcategory_ids: list[int] | None = None,
        part_number: str | None = None,
        connector_series: str | None = None,
        connector_manufacturer: str | None = None,
        preferred_specs: list[SpecFilter] | None = None,
        gate_drive_v: float | None = None,
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
            mounting_type: Filter by mounting type ("Through Hole" or "SMD")
            match_all_terms: FTS matching mode
            sort_by: Sort order
            limit: Max results
            offset: Pagination offset
            subcategory_ids: Several subcategories (OR), used when no subcategory_id is given
            part_number: Full token shortened by the parser; rank and label MPN matches
            preferred_specs: Ordered equality preferences for sparse PD role/output attributes
            gate_drive_v: Rank listed RDS(on) at or below this gate drive first; retain unknowns

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
                    "hint": "Use jlc_search_help() to browse categories, then jlc_search_help(category='Power Management (PMIC)') for subcategories",
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
                    "hint": "Use jlc_search_help() to see available categories",
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }
            resolved_category_display_name = self._categories[resolved_category_id]["name"]

        # Validate query
        if query:
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

            # Validate FTS will have searchable terms
            fts_sql, _ = build_fts_clause(query, match_all_terms)
            if not fts_sql:
                return {
                    "error": "Query contains no searchable terms",
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }

        # Expand packages
        expanded_packages: list[str] = []
        if packages:
            for pkg in packages:
                expanded_packages.extend(expand_package(pkg))
        elif package:
            expanded_packages = expand_package(package)

        searched = [resolved_subcategory_id] if resolved_subcategory_id else subcategory_ids
        if searched and all(self._subcategories.get(i, {}).get("name", "").lower() in FUSE_ATTRIBUTE_MAP for i in searched):
            # A fuse's literal 2016 package must survive the crystal SMD2016 expansion.
            expanded_packages = list(dict.fromkeys([*expanded_packages, *(packages or ([package] if package else []))]))

        # Automatic fuse ratings follow the searched family, including cross-family retries.
        # In a broad search each mapping applies only to its own subcategory.
        if spec_filters and any(isinstance(f, FuseFilter) for f in spec_filters):
            fuse_ids = [i for i in (searched or self._subcategories)
                        if self._subcategories[i]["name"].lower() in FUSE_ATTRIBUTE_MAP]
            mapped_filters = []
            for f in spec_filters:
                if not isinstance(f, FuseFilter) or not fuse_ids:
                    mapped_filters.append(f)
                    continue
                for i in fuse_ids:
                    mapped_filters.append(f.for_subcategory(
                        self._subcategories[i]["name"], None if searched and len(searched) == 1 else i,
                    ))
            spec_filters = mapped_filters

        # Execute the search
        search_result = self._execute_search(
            query=query,
            subcategory_id=resolved_subcategory_id,
            category_id=resolved_category_id,
            spec_filters=spec_filters,
            library_type=library_type,
            min_stock=min_stock,
            expanded_packages=expanded_packages,
            manufacturer=manufacturer,
            mounting_type=mounting_type,
            match_all_terms=match_all_terms,
            sort_by=sort_by,
            prefer_no_fee=prefer_no_fee,
            limit=limit,
            offset=offset,
            subcategory_ids=None if resolved_subcategory_id else subcategory_ids,
            part_number=part_number,
            connector_series=connector_series,
            connector_manufacturer=connector_manufacturer,
            preferred_specs=preferred_specs,
            gate_drive_v=gate_drive_v,
        )

        results = search_result["results"]
        total = search_result["total"]
        library_type_counts = search_result["library_type_counts"]
        no_fee_available = search_result["no_fee_available"]

        # MPN retry: If no results and query looks like a part number, try normalized variants
        mpn_retry_query: str | None = None
        if total == 0 and query and looks_like_mpn(query):
            variants = normalize_mpn(query)
            # Try each variant (skip first which is original)
            for variant in variants[1:]:
                retry_result = self._execute_search(
                    query=variant,
                    subcategory_id=resolved_subcategory_id,
                    category_id=resolved_category_id,
                    spec_filters=spec_filters,
                    library_type=library_type,
                    min_stock=min_stock,
                    expanded_packages=expanded_packages,
                    manufacturer=manufacturer,
                    mounting_type=mounting_type,
                    match_all_terms=match_all_terms,
                    sort_by=sort_by,
                    prefer_no_fee=prefer_no_fee,
                    limit=limit,
                    offset=offset,
                    subcategory_ids=None if resolved_subcategory_id else subcategory_ids,
                    part_number=part_number,
                    connector_series=connector_series,
                    connector_manufacturer=connector_manufacturer,
                    preferred_specs=preferred_specs,
                    gate_drive_v=gate_drive_v,
                )
                if retry_result["total"] > 0:
                    # Found results with normalized query
                    mpn_retry_query = variant
                    results = retry_result["results"]
                    total = retry_result["total"]
                    library_type_counts = retry_result["library_type_counts"]
                    no_fee_available = retry_result["no_fee_available"]
                    search_result = retry_result
                    break

        response: dict[str, Any] = {
            "results": results,
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
                "subcategory_ids": None if resolved_subcategory_id else subcategory_ids,
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
        if "counts_complete" in search_result:
            response["counts_complete"] = search_result["counts_complete"]
        if "mpn_matches" in search_result:
            response["mpn_matches"] = search_result["mpn_matches"]
        if search_result["ignored_filters"]:
            response["ignored_filters"] = search_result["ignored_filters"]

        # Add MPN retry info if we found results via normalization
        if mpn_retry_query:
            response["mpn_normalized"] = {
                "original_query": query,
                "matched_query": mpn_retry_query,
                "note": "Original query had no results; found matches using normalized MPN variant",
            }

        return response
