"""SQL query building functions for component search."""

import re
from typing import Any

from ..alternatives import SPEC_PARSERS
from .spec_filter import (
    SpecFilter,
    SPEC_TO_COLUMN,
    _escape_like,
    generate_value_patterns,
    get_attribute_names,
)


def build_fts_clause(query: str, match_all_terms: bool) -> tuple[str, list[str]]:
    """Build FTS (full-text search) WHERE clause.

    Args:
        query: The search query string
        match_all_terms: True for AND logic, False for OR logic

    Returns:
        Tuple of (sql_clause, params) or (None, []) if invalid query
    """
    # Validate query length
    if len(query) > 500:
        return "", []

    # Validate for control characters
    if any(ord(c) < 32 and c not in '\t\n\r' for c in query) or '\x00' in query:
        return "", []

    # Build FTS5 query: tokenize, quote each term, add prefix matching
    tokens = query.split()
    fts_parts = []
    for token in tokens:
        if not token:
            continue
        escaped = token.replace('"', '""')
        fts_parts.append(f'"{escaped}"*')

    if not fts_parts:
        return "", []

    # Join with space (AND) or OR based on match_all_terms
    if match_all_terms:
        fts_query = " ".join(fts_parts)
    else:
        fts_query = " OR ".join(fts_parts)

    sql = """
        AND lcsc IN (
            SELECT lcsc FROM components_fts
            WHERE components_fts MATCH ?
        )
    """
    return sql, [fts_query]


def build_subcategory_clause(
    subcategory_id: int | None,
    category_id: int | None,
    subcategories: dict[int, dict[str, Any]],
    category_to_subcategories: dict[int, list[int]] | None = None,
) -> tuple[str, list[Any]]:
    """Build subcategory/category filter clause.

    Args:
        subcategory_id: Optional subcategory ID to filter by
        category_id: Optional category ID to filter by (used if no subcategory)
        subcategories: Dict mapping subcategory IDs to their info
        category_to_subcategories: Optional pre-built mapping for O(1) lookup

    Returns:
        Tuple of (sql_clause, params)
    """
    if subcategory_id:
        return "AND subcategory_id = ?", [subcategory_id]
    elif category_id:
        # Get all subcategory IDs for this category
        # Use pre-built mapping if available (O(1)), otherwise iterate (O(n))
        if category_to_subcategories and category_id in category_to_subcategories:
            subcat_ids = category_to_subcategories[category_id]
        else:
            subcat_ids = [
                sid for sid, info in subcategories.items()
                if info["category_id"] == category_id
            ]
        if subcat_ids:
            placeholders = ",".join("?" * len(subcat_ids))
            return f"AND subcategory_id IN ({placeholders})", subcat_ids
    return "", []


def build_library_type_clause(library_type: str | None) -> str:
    """Build library type filter clause.

    Args:
        library_type: One of "basic", "preferred", "extended", or None

    Returns:
        SQL clause string (no params needed)
    """
    if library_type == "basic":
        return "AND library_type = 'b'"
    elif library_type == "preferred":
        return "AND library_type = 'p'"
    elif library_type == "extended":
        return "AND library_type = 'e'"
    return ""


def build_stock_clause(min_stock: int) -> tuple[str, list[int]]:
    """Build minimum stock filter clause.

    Args:
        min_stock: Minimum stock quantity required

    Returns:
        Tuple of (sql_clause, params)
    """
    if min_stock > 0:
        return "AND stock >= ?", [min_stock]
    return "", []


def _expand_package_aliases(pkg: str) -> list[str]:
    """Expand a package name to include common JLCPCB variations.

    JLCPCB uses specific naming conventions that differ from common names:
    - TQFP-44 → QFP-44 (JLCPCB doesn't use "T" prefix)
    - QFN-56 → LQFN-56, WQFN-56, VQFN-56 (various QFN prefixes)
    - UFQFPN-48 → UFQFPN-48 (same)

    Returns list of package patterns to search for.
    """
    pkg_upper = pkg.upper()
    variants = [pkg_upper]

    # QFP variants: TQFP/LQFP/PQFP → also try bare QFP
    qfp_match = re.match(r'^([TLP])?QFP-?(\d+)(.*)$', pkg_upper)
    if qfp_match:
        prefix, pins, suffix = qfp_match.groups()
        # Add bare QFP-XX for TQFP/LQFP/PQFP
        if prefix:
            variants.append(f"QFP-{pins}{suffix or ''}")
        # Also try with other prefixes
        for p in ['', 'T', 'L', 'P', 'H']:
            var = f"{p}QFP-{pins}" if p else f"QFP-{pins}"
            if var not in variants:
                variants.append(var)

    # QFN variants: try LQFN, WQFN, VQFN, TQFN, bare QFN
    qfn_match = re.match(r'^([LWVTU])?QFN-?(\d+)(.*)$', pkg_upper)
    if qfn_match:
        prefix, pins, suffix = qfn_match.groups()
        # Try all common QFN prefixes
        for p in ['', 'L', 'W', 'V', 'T', 'U']:
            var = f"{p}QFN-{pins}" if p else f"QFN-{pins}"
            if var not in variants:
                variants.append(var)

    # UFQFPN is its own thing, keep as-is
    # SOIC/SOP/SO variants
    soic_match = re.match(r'^(SOIC|SO|SOP)-?(\d+)(.*)$', pkg_upper)
    if soic_match:
        _, pins, suffix = soic_match.groups()
        for p in ['SOIC-', 'SOP-', 'SO-']:
            var = f"{p}{pins}"
            if var not in variants:
                variants.append(var)

    return variants


def build_package_clause(packages: list[str]) -> tuple[str, list[str]]:
    """Build package filter clause.

    Args:
        packages: List of package names to match (OR logic)

    Returns:
        Tuple of (sql_clause, params)

    Notes:
        Uses prefix matching (LIKE 'pkg%') to handle parenthetical variations.
        E.g., "DO-214AC" matches both "DO-214AC" and "DO-214AC(SMA)".
        Also expands package aliases (TQFP-44 → QFP-44, QFN-56 → LQFN-56, etc.)
    """
    if packages:
        # Expand packages to include common variations
        expanded_packages = []
        for pkg in packages:
            expanded_packages.extend(_expand_package_aliases(pkg))
        # Dedupe while preserving order
        seen = set()
        unique_packages = []
        for pkg in expanded_packages:
            if pkg not in seen:
                seen.add(pkg)
                unique_packages.append(pkg)

        # Use LIKE with prefix matching to handle parenthetical variations
        # e.g., "DO-214AC" should match "DO-214AC(SMA)"
        or_conditions = []
        params = []
        for pkg in unique_packages:
            # Escape LIKE special characters
            escaped_pkg = pkg.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            or_conditions.append("package LIKE ? ESCAPE '\\'")
            params.append(f"{escaped_pkg}%")
        combined = " OR ".join(or_conditions)
        return f"AND ({combined})", params
    return "", []


def build_manufacturer_clause(manufacturer: str) -> tuple[str, list[str]]:
    """Build manufacturer filter clause.

    Args:
        manufacturer: Manufacturer name (already resolved)

    Returns:
        Tuple of (sql_clause, params)
    """
    if manufacturer:
        return "AND LOWER(manufacturer) = LOWER(?)", [manufacturer]
    return "", []


def build_mounting_type_clause(mounting_type: str | None) -> tuple[str, list[str]]:
    """Build mounting type filter clause.

    Filters based on description text containing mounting type keywords.
    JLCPCB descriptions use "Through Hole" or "Surface Mount" terminology.

    Args:
        mounting_type: "Through Hole", "SMD", or None

    Returns:
        Tuple of (sql_clause, params)
    """
    if not mounting_type:
        return "", []

    mounting_lower = mounting_type.lower()
    if mounting_lower in ("through hole", "tht", "through-hole"):
        # Match "Through Hole" or "Plugin" (JLCPCB's term for THT)
        return "AND (description LIKE ? OR description LIKE ?)", ["%Through Hole%", "%Plugin%"]
    elif mounting_lower in ("smd", "surface mount", "smt"):
        # Match "Surface Mount" or "SMD" in description
        return "AND (description LIKE ? OR description LIKE ?)", ["%Surface Mount%", "%SMD%"]

    return "", []


def _group_multi_value_filters(spec_filters: list[SpecFilter]) -> list[SpecFilter | tuple[str, list[str]]]:
    """Group filters with same spec_name and operator="=" into OR groups.

    For attributes like Interface where a component can have multiple values
    (e.g., "I2C、SPI"), when the user searches for "I2C SPI", we should match
    components that have EITHER value, not require both (OR logic, not AND).

    Args:
        spec_filters: List of SpecFilter objects

    Returns:
        List of either SpecFilter objects or tuples of (spec_name, [values])
        for grouped filters
    """
    from collections import defaultdict

    # Group filters by (normalized_name, operator)
    groups: dict[tuple[str, str], list[SpecFilter]] = defaultdict(list)
    for f in spec_filters:
        key = (f.name.lower(), f.operator)
        groups[key].append(f)

    # Build result list
    result: list[SpecFilter | tuple[str, list[str]]] = []
    processed_keys: set[tuple[str, str]] = set()

    for spec_filter in spec_filters:
        key = (spec_filter.name.lower(), spec_filter.operator)

        if key in processed_keys:
            continue

        filters_in_group = groups[key]

        # If operator is "=" and multiple values exist, create an OR group
        # This applies to Interface, Type, and other categorical attributes
        if spec_filter.operator == "=" and len(filters_in_group) > 1:
            # Create a grouped filter (spec_name, [values])
            values = [f.value for f in filters_in_group]
            result.append((spec_filter.name, values))
            processed_keys.add(key)
        else:
            # Keep individual filter (will be AND'd with other filters)
            result.append(spec_filter)
            processed_keys.add(key)

    return result


def build_spec_filter_clauses(
    spec_filters: list[SpecFilter],
) -> tuple[list[str], list[Any], list[tuple[SpecFilter, set[str], Any, float | None]]]:
    """Build spec filter clauses for SQL and collect post-filter metadata.

    Args:
        spec_filters: List of SpecFilter objects

    Returns:
        Tuple of:
        - sql_clauses: List of SQL WHERE clause parts
        - params: List of SQL parameters
        - post_filter_metadata: List of (spec_filter, attr_names_set, parser, target_value)
          for filters that need Python post-filtering
    """
    sql_clauses: list[str] = []
    params: list[Any] = []
    post_filter_metadata: list[tuple[SpecFilter, set[str], Any, float | None]] = []

    # Group multi-value "=" filters (like multiple Interface values) for OR logic
    grouped_filters = _group_multi_value_filters(spec_filters)

    for item in grouped_filters:
        # Handle grouped filters (spec_name, [values])
        if isinstance(item, tuple):
            spec_name, values = item
            attr_names = get_attribute_names(spec_name)

            # Build OR clause for all values: (Interface LIKE '%I2C%' OR Interface LIKE '%SPI%')
            use_substring_match = spec_name.lower() == "interface"
            is_impedance_at_freq = spec_name.lower() == "impedance @ frequency"

            or_conditions = []
            for value in values:
                for name in attr_names:
                    if use_substring_match:
                        pattern = f'%"{_escape_like(name)}"%{_escape_like(value)}%'
                    elif is_impedance_at_freq:
                        numeric_match = re.match(r'^(\d+(?:\.\d+)?)', value)
                        if numeric_match:
                            numeric_part = numeric_match.group(1)
                            pattern = f'%"{_escape_like(name)}", "{numeric_part}%'
                        else:
                            pattern = f'%"{_escape_like(name)}", "{_escape_like(value)}%'
                    else:
                        pattern = f'%"{_escape_like(name)}", "{_escape_like(value)}"%'
                    or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                    params.append(pattern)

            if or_conditions:
                combined = " OR ".join(or_conditions)
                sql_clauses.append(f"AND ({combined})")

            continue

        # Handle individual filter
        spec_filter = item
        # Get all possible attribute names (including aliases)
        attr_names = get_attribute_names(spec_filter.name)

        # Check if we have a pre-computed column for this spec
        column_info = None
        for name in [spec_filter.name] + attr_names:
            if name in SPEC_TO_COLUMN:
                column_info = SPEC_TO_COLUMN[name]
                break

        if column_info and spec_filter.operator in (">=", "<=", ">", "<", "="):
            column_name, parser = column_info
            # Use the parser if available, otherwise try SPEC_PARSERS
            if parser is None:
                for name in attr_names:
                    parser = SPEC_PARSERS.get(name)
                    if parser:
                        break

            if parser:
                parsed_value = parser(spec_filter.value)
                if parsed_value is not None:
                    # Use SQL numeric comparison on pre-computed column
                    if spec_filter.operator == "=":
                        tolerance = abs(parsed_value) * 0.01 if parsed_value != 0 else 1e-9
                        sql_clauses.append(f"AND {column_name} BETWEEN ? AND ?")
                        params.extend([parsed_value - tolerance, parsed_value + tolerance])
                    elif spec_filter.operator == ">=":
                        sql_clauses.append(f"AND {column_name} >= ?")
                        params.append(parsed_value)
                    elif spec_filter.operator == "<=":
                        sql_clauses.append(f"AND {column_name} <= ?")
                        params.append(parsed_value)
                    elif spec_filter.operator == ">":
                        sql_clauses.append(f"AND {column_name} > ?")
                        params.append(parsed_value)
                    elif spec_filter.operator == "<":
                        sql_clauses.append(f"AND {column_name} < ?")
                        params.append(parsed_value)
                    continue

        # Fall back to LIKE patterns for specs without pre-computed columns
        parser = None
        for name in attr_names:
            parser = SPEC_PARSERS.get(name)
            if parser:
                break

        parsed_value = None
        if parser:
            parsed_value = parser(spec_filter.value)

        if parsed_value is not None and spec_filter.operator in (">=", "<=", ">", "<", "="):
            # Numeric comparison - still need post-filtering for these
            if spec_filter.operator == "=":
                or_conditions = []
                for name in attr_names:
                    value_patterns = generate_value_patterns(name, spec_filter.value, parsed_value)
                    for pattern in value_patterns:
                        or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                        params.append(pattern)
                if or_conditions:
                    combined = " OR ".join(or_conditions)
                    sql_clauses.append(f"AND ({combined})")
            else:
                # For range comparisons, check attribute exists
                or_conditions = []
                for name in attr_names:
                    or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                    pattern = f'%"{_escape_like(name)}"%'
                    params.append(pattern)
                if or_conditions:
                    combined = " OR ".join(or_conditions)
                    sql_clauses.append(f"AND ({combined})")

            # Add to post-filter metadata (needs Python post-filtering)
            attr_names_set = set(attr_names)
            target_value = parser(spec_filter.value) if parser else None
            post_filter_metadata.append((spec_filter, attr_names_set, parser, target_value))

        elif spec_filter.operator == "=":
            # String exact value match (non-numeric)
            use_substring_match = spec_filter.name.lower() == "interface"
            # For "Impedance @ Frequency", use prefix match to match "100Ω@100MHz" from "100Ohm"
            is_impedance_at_freq = spec_filter.name.lower() == "impedance @ frequency"

            or_conditions = []
            for name in attr_names:
                if use_substring_match:
                    pattern = f'%"{_escape_like(name)}"%{_escape_like(spec_filter.value)}%'
                elif is_impedance_at_freq:
                    # Extract numeric part from value like "100Ohm" -> "100"
                    # to match database format "100Ω@100MHz"
                    numeric_match = re.match(r'^(\d+(?:\.\d+)?)', spec_filter.value)
                    if numeric_match:
                        numeric_part = numeric_match.group(1)
                        pattern = f'%"{_escape_like(name)}", "{numeric_part}%'
                    else:
                        pattern = f'%"{_escape_like(name)}", "{_escape_like(spec_filter.value)}%'
                else:
                    pattern = f'%"{_escape_like(name)}", "{_escape_like(spec_filter.value)}"%'
                or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                params.append(pattern)
            if or_conditions:
                combined = " OR ".join(or_conditions)
                sql_clauses.append(f"AND ({combined})")

    return sql_clauses, params, post_filter_metadata


def build_sort_clause(
    sort_by: str,
    prefer_no_fee: bool,
    has_query: bool,
) -> str:
    """Build ORDER BY clause.

    Args:
        sort_by: Sort mode - "stock", "price", or "relevance"
        prefer_no_fee: Whether to prioritize basic > preferred > extended
        has_query: Whether there's a text query (affects relevance sort)

    Returns:
        SQL ORDER BY clause
    """
    lib_type_order = "CASE library_type WHEN 'b' THEN 1 WHEN 'p' THEN 2 ELSE 3 END"

    if sort_by == "price":
        if prefer_no_fee:
            return f"ORDER BY {lib_type_order}, price ASC NULLS LAST"
        else:
            return "ORDER BY price ASC NULLS LAST"
    elif sort_by == "relevance" and has_query:
        if prefer_no_fee:
            return f"ORDER BY {lib_type_order}, stock DESC"
        else:
            return "ORDER BY stock DESC"
    else:
        if prefer_no_fee:
            return f"ORDER BY {lib_type_order}, stock DESC"
        else:
            return "ORDER BY stock DESC"


def needs_numeric_post_filter(spec_filter: SpecFilter) -> bool:
    """Check if a spec filter needs Python post-filtering.

    Returns True if the filter cannot be fully handled by SQL
    and requires Python post-processing.
    """
    attr_names = get_attribute_names(spec_filter.name)

    # Check if this spec has a pre-computed column
    for name in [spec_filter.name] + attr_names:
        if name in SPEC_TO_COLUMN:
            return False  # SQL handles this with indexed column query

    # Check if we need post-filtering for numeric comparison
    if spec_filter.operator in (">=", "<=", ">", "<"):
        return True
    if spec_filter.operator == "=":
        for name in attr_names:
            if SPEC_PARSERS.get(name):
                return True
    return False
