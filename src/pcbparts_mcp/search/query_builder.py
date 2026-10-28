"""SQL query building functions for component search."""

import re
from decimal import Decimal
from functools import lru_cache
from typing import Any

from ..alternatives import DIMENSION_SPEC_FIELDS, SPEC_PARSERS
from ..parsers import RESISTANCE_MATCH_TOLERANCE, parse_current, parse_memory_size, parse_resistance, parse_voltage
from .spec_filter import (
    CONNECTOR_FILTER_COLUMNS,
    LIST_SPECS,
    RANGE_SPECS,
    ConnectorFilter,
    FuseFilter,
    SpecFilter,
    SPEC_TO_COLUMN,
    _escape_like,
    generate_value_patterns,
    like_text,
    get_attribute_names,
    connector_value,
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
    subcategory_ids: list[int] | None = None,
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
    elif subcategory_ids:
        return f"AND subcategory_id IN ({','.join('?' * len(subcategory_ids))})", list(subcategory_ids)
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
        library_type: One of "basic", "preferred", "extended", "no_fee", or None

    Returns:
        SQL clause string (no params needed)
    """
    if library_type == "basic":
        return "AND library_type = 'b'"
    elif library_type == "preferred":
        return "AND library_type = 'p'"
    elif library_type == "extended":
        return "AND library_type = 'e'"
    elif library_type == "no_fee":
        return "AND library_type IN ('b', 'p')"
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


_PACKAGE_ALIAS_FAMILIES = (
    (re.compile(r'^([TLPH]?QFP)-?(\d+)(.*)$'), ('QFP', 'TQFP', 'LQFP', 'PQFP', 'HQFP')),
    # Catalog spellings for quad flat no-lead packages, including ST's QFPN names.
    (re.compile(r'^([LWVTU]?QFN|[UV]FQFPN|HVQFN)-?(\d+)(.*)$'),
     ('QFN', 'LQFN', 'WQFN', 'VQFN', 'TQFN', 'UQFN', 'UFQFPN', 'VFQFPN', 'HVQFN')),
    (re.compile(r'^(SOIC|SO|SOP)-?(\d+)(.*)$'), ('SOIC', 'SOP', 'SO')),
)
_PACKAGE_PARTS = re.compile(r'^([A-Z]+)-?(\d+)(.*)$')
_BODY_SIZE = re.compile(r'(\d+(?:\.\d+)?)\s*(?:MM)?\s*[X×]\s*(\d+(?:\.\d+)?)\s*(?:MM)?')
_EXPOSED_PAD = re.compile(r'-EP(?=[(-]|$)')


def _expand_package_aliases(pkg: str) -> list[str]:
    """Expand family spellings while retaining every requested suffix constraint."""
    pkg_upper = pkg.upper()
    for pattern, names in _PACKAGE_ALIAS_FAMILIES:
        if match := pattern.fullmatch(pkg_upper):
            _, pins, suffix = match.groups()
            return list(dict.fromkeys([pkg_upper, *(f'{name}-{pins}{suffix}' for name in names)]))
    return [pkg_upper]


def package_family_adjustments(packages: list[str]) -> list[dict[str, str]]:
    """Explain the intentional widening of bare alias families, including explicit args."""
    adjustments = []
    for pkg in dict.fromkeys(packages):
        for pattern, _ in _PACKAGE_ALIAS_FAMILIES:
            match = pattern.fullmatch(pkg.upper())
            if match and not match[3]:
                adjustments.append({
                    'filter': f'package: {pkg}',
                    'now': ', '.join(_expand_package_aliases(pkg)),
                    'reason': 'bare package family includes variants with any body size; '
                              f'give the full package (e.g. {match[1]}-{match[2]}-EP(5x5)) for an exact match',
                })
                break
    return adjustments


@lru_cache(maxsize=4096)
def _normalized_package_suffix(package: str) -> tuple[str, str] | None:
    match = _PACKAGE_PARTS.fullmatch(package.upper())
    if not match:
        return None

    def body(match: re.Match) -> str:
        a, b = sorted(Decimal(value) for value in match.groups())
        return f'{a.normalize():f}X{b.normalize():f}'

    return match[2], _BODY_SIZE.sub(body, match[3]).strip()


def package_suffix_matches(candidate: str | None, requested: str) -> bool:
    """Compare size/pad/other suffix constraints on catalog spellings of one family."""
    actual = _normalized_package_suffix(candidate or '')
    wanted = _normalized_package_suffix(requested)
    if actual is None or wanted is None or actual[0] != wanted[0]:
        return False
    actual_suffix, wanted_suffix = actual[1], wanted[1]
    if _EXPOSED_PAD.search(wanted_suffix):
        if not _EXPOSED_PAD.search(actual_suffix):
            return False
        # An EP-only request permits any body size, but still requires the pad.
        if wanted_suffix == '-EP':
            return True
    else:
        # An unrequested pad is allowed; an explicitly requested pad is mandatory.
        actual_suffix = _EXPOSED_PAD.sub('', actual_suffix)
    return actual_suffix == wanted_suffix


def package_has_constraints(pkg: str) -> bool:
    parts = _PACKAGE_PARTS.fullmatch(pkg.upper())
    return bool(parts and parts[3] and (
        len(_expand_package_aliases(pkg)) > 1 or _BODY_SIZE.search(parts[3]) or _EXPOSED_PAD.search(parts[3])
    ))


def package_needs_catalog(pkg: str) -> bool:
    return package_has_constraints(pkg) or len(_expand_package_aliases(pkg)) > 1


def index_package_names(names: list[str]) -> dict[str, list[str]]:
    """Index the catalog's spellings by family and pin count for exact SQL lookups."""
    indexed: dict[str, list[str]] = {}
    for name in names:
        if match := _PACKAGE_PARTS.fullmatch(name.upper()):
            indexed.setdefault(f'{match[1]}-{match[2]}', []).append(name)
    return indexed


def matching_package_names(pkg: str, package_names: dict[str, list[str]]) -> list[str]:
    """Find exact suffix matches across every catalog spelling of a family and pin count."""
    prefixes = [f'{m[1]}-{m[2]}' for alias in _expand_package_aliases(pkg)
                if (m := _PACKAGE_PARTS.fullmatch(alias))]
    return list(dict.fromkeys(
        name for prefix in prefixes for name in package_names.get(prefix, [])
        if package_suffix_matches(name, pkg)
    ))


def resolve_package_constraints(
    packages: list[str], package_names: dict[str, list[str]],
) -> tuple[list[str], list[dict[str, str]]]:
    """Fall back only when the requested suffix has no spelling anywhere in the catalog."""
    resolved = []
    adjustments = []
    for pkg in dict.fromkeys(packages):
        if package_has_constraints(pkg) and not matching_package_names(pkg, package_names):
            parts = _PACKAGE_PARTS.fullmatch(pkg.upper())
            bare = f'{parts[1]}-{parts[2]}'
            resolved.append(bare)
            adjustments.append({
                'filter': f'package: {pkg}',
                'now': bare,
                'reason': f'no catalog package is {pkg}, so the {bare} family of any body size '
                          "was matched; check the body in each part's package",
            })
        else:
            resolved.append(pkg)
    return resolved, adjustments


def build_package_clause(
    packages: list[str], package_names: dict[str, list[str]] | None = None,
) -> tuple[str, list[str]]:
    """Build package filter clause.

    Args:
        packages: List of package names to match (OR logic)
        package_names: Catalog spellings indexed by family and pins, for constrained packages

    Returns:
        Tuple of (sql_clause, params)

    Notes:
        Bare packages use prefix matching (LIKE 'pkg%') for parenthetical variations.
        E.g., "DO-214AC" matches both "DO-214AC" and "DO-214AC(SMA)".
        Also expands package aliases (TQFP-44 → QFP-44, QFN-56 → LQFN-56, etc.)
    """
    if packages:
        or_conditions = []
        params = []
        unconstrained_aliases = []
        family_aliases = []
        constrained_packages = []
        for pkg in dict.fromkeys(packages):
            aliases = _expand_package_aliases(pkg)
            if package_has_constraints(pkg):
                constrained_packages.append((pkg, aliases))
            elif len(aliases) > 1:
                family_aliases.extend(aliases)
            else:
                unconstrained_aliases.extend(aliases)

        def prefix_clause(prefixes: list[str]) -> str:
            conditions = []
            for prefix in dict.fromkeys(prefixes):
                conditions.append("package LIKE ? ESCAPE '\\'")
                params.append(_escape_like(prefix) + '%')
            return '(' + ' OR '.join(conditions) + ')'

        if unconstrained_aliases:
            or_conditions.append(prefix_clause(unconstrained_aliases))
        if family_aliases:
            # Preserve the existing bare-family prefix population while avoiding
            # an additional full-table LIKE scan for every vendor spelling.
            prefixes = tuple(dict.fromkeys(family_aliases))
            matches = [name for names in (package_names or {}).values() for name in names
                       if name.upper().startswith(prefixes)]
            or_conditions.append('package IN (' + ','.join('?' for _ in matches) + ')' if matches else '0')
            params.extend(matches)
        for pkg, aliases in constrained_packages:
            # Resolver mappings can include both a family and its specific variants.
            # The family already covers them; avoid redundant suffix checks in SQL.
            if any(alias.startswith(bare) for alias in aliases for bare in [*unconstrained_aliases, *family_aliases]):
                continue
            # Compare the small package catalog once, then let SQLite use idx_package.
            # This also keeps counts/paging exact without per-component Python callbacks.
            matches = matching_package_names(pkg, package_names or {})
            if matches:
                or_conditions.append('package IN (' + ','.join('?' for _ in matches) + ')')
                params.extend(matches)
            else:
                or_conditions.append('0')
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


# Type = N-Channel / P-Channel / NPN / PNP: the polarity wanted and the one to leave out
_POLARITY_VALUES: dict[str, tuple[str, str]] = {
    "n-channel": ("n-channel", "p-channel"), "p-channel": ("p-channel", "n-channel"),
    "npn": ("npn", "pnp"), "pnp": ("pnp", "npn"),
}


def _polarity_clause(values: list[str]) -> tuple[str, list[Any]]:
    """Transistors whose Type (or type) is the polarity, or whose Number states it ("1 P-Channel",
    "2 NPN Pre-Biased") without the other one. 5,703 MOSFETs state it only in Number (AO3401A's
    Type is "-")."""
    conditions: list[str] = []
    params: list[Any] = []
    for value in values:
        want, other = _POLARITY_VALUES[value.lower()]
        conditions.append("(lower(json_extract(j.value, '$[0]')) = 'type' AND lower(json_extract(j.value, '$[1]')) = ?)")
        conditions.append(
            "(json_extract(j.value, '$[0]') = 'Number' AND lower(json_extract(j.value, '$[1]')) LIKE ? ESCAPE '\\'"
            " AND lower(json_extract(j.value, '$[1]')) NOT LIKE ? ESCAPE '\\')"
        )
        params.extend([want, f"_ {_escape_like(want)}%", f"%{_escape_like(other)}%"])
    sql = f"AND EXISTS (SELECT 1 FROM json_each(components.attributes) j WHERE {' OR '.join(conditions)})"
    return sql, params


def _list_item_clause(attr_names: list[str], values: list[str]) -> tuple[str, list[Any]]:
    """One of the attributes lists one of the values as an item ("Boost、Buck" has Buck)."""
    names = sorted({name.lower() for name in attr_names})  # BJTs call it "type", MOSFETs "Type"
    items = " OR ".join(
        "('、' || lower(json_extract(j.value, '$[1]')) || '、') LIKE ? ESCAPE '\\'" for _ in values
    )
    sql = (
        "AND EXISTS (SELECT 1 FROM json_each(components.attributes) j "
        f"WHERE lower(json_extract(j.value, '$[0]')) IN ({','.join('?' * len(names))}) AND ({items}))"
    )
    return sql, [*names, *(f"%、{_escape_like(v.strip().lower())}、%" for v in values)]


def _parse_impedance_ohms(value: str) -> float | None:
    """Ferrite bead impedance in ohms: "600Ω@100MHz" -> 600, a filter's "600Ohm" -> 600."""
    return parse_resistance(value.split("@")[0])


def _numeric_parser(spec_name: str, attr_names: list[str]) -> Any:
    """The parser for a spec's values, or None. "Impedance @ Frequency" is registered as "special"."""
    if spec_name.lower() == "impedance @ frequency":
        return _parse_impedance_ohms
    for name in attr_names:
        parser = SPEC_PARSERS.get(name)
        if callable(parser):
            return parser
    return None


def _is_range_spec(spec_name: str, attr_names: list[str]) -> bool:
    """Compared range by range. A short name with its own column (Vout) keeps the column: exact."""
    if spec_name in RANGE_SPECS:
        return True
    return spec_name not in SPEC_TO_COLUMN and any(name in RANGE_SPECS for name in attr_names)


def _filter_value(parser: Any, value: str) -> float | None:
    """Unitless explicit numeric values use the attribute parser's base unit."""
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", value.strip()):
        return float(value)
    return parser(value)


def build_spec_filter_clauses(
    spec_filters: list[SpecFilter],
    *,
    connector_columns: bool = False,
) -> tuple[list[str], list[Any], list[tuple[SpecFilter, set[str], Any, float | None]], list[dict[str, str]]]:
    """Build spec filter clauses for SQL and collect post-filter metadata.

    Args:
        spec_filters: List of SpecFilter objects
        connector_columns: Database has the strictly parsed connector columns

    Returns:
        Tuple of:
        - sql_clauses: List of SQL WHERE clause parts
        - params: List of SQL parameters
        - post_filter_metadata: List of (spec_filter, attr_names_set, parser, target_value)
          for filters that need Python post-filtering
        - ignored: filters that couldn't be applied, as {"filter", "reason"} (a range op on a
          spec with no numeric parser, or a value that doesn't parse); the search runs without them
    """
    sql_clauses: list[str] = []
    params: list[Any] = []
    post_filter_metadata: list[tuple[SpecFilter, set[str], Any, float | None]] = []
    ignored: list[dict[str, str]] = []

    # Automatic fuse/connector constraints have scoped numeric semantics. Caller-supplied
    # SpecFilters keep their existing string/operator semantics.
    for f in spec_filters:
        if isinstance(f, FuseFilter):
            scope = "subcategory_id != ? OR " if f.subcategory_id is not None else ""
            if scope:
                params.append(f.subcategory_id)
            if f.name == "Current Rating":
                sql_clauses.append(f"AND ({scope}current_max_a = ?)")
                params.append(parse_current(f.value))
            else:
                sql_clauses.append(
                    f"AND ({scope}EXISTS (SELECT 1 FROM json_each(components.attributes) j "
                    "WHERE json_extract(j.value, '$[0]') = ?))"
                )
                params.append(f.name)
                parser = parse_current if f.name == "Hold Current" else parse_voltage
                post_filter_metadata.append((f, {f.name}, parser, parser(f.value)))
    fuse_scopes = sorted({f.subcategory_id for f in spec_filters
                          if isinstance(f, FuseFilter) and f.subcategory_id is not None})
    if fuse_scopes:
        sql_clauses.append(f"AND subcategory_id IN ({','.join('?' * len(fuse_scopes))})")
        params.extend(fuse_scopes)

    for f in spec_filters:
        if isinstance(f, ConnectorFilter):
            if connector_columns and f.name in CONNECTOR_FILTER_COLUMNS:
                sql_clauses.append(f"AND {CONNECTOR_FILTER_COLUMNS[f.name]} = ?")
                params.append(connector_value(f.name, f.value))
            else:
                sql_clauses.append(
                    "AND EXISTS (SELECT 1 FROM json_each(components.attributes) j "
                    "WHERE json_extract(j.value, '$[0]') = ? "
                    "AND connector_value(?, json_extract(j.value, '$[1]')) = ?)"
                )
                params.extend([f.name, f.name, connector_value(f.name, f.value)])

    # Group multi-value "=" filters (like multiple Interface values) for OR logic
    grouped_filters = _group_multi_value_filters([f for f in spec_filters if not isinstance(f, (ConnectorFilter, FuseFilter))])

    for item in grouped_filters:
        # Handle grouped filters (spec_name, [values])
        if isinstance(item, tuple):
            spec_name, values = item
            attr_names = get_attribute_names(spec_name)

            if spec_name.lower() == "type" and all(v.lower() in _POLARITY_VALUES for v in values):
                clause, clause_params = _polarity_clause(values)
                sql_clauses.append(clause)
                params.extend(clause_params)
                continue
            if spec_name in LIST_SPECS:
                clause, clause_params = _list_item_clause(attr_names, values)
                sql_clauses.append(clause)
                params.extend(clause_params)
                continue

            # Build OR clause for all values: (Interface LIKE '%I2C%' OR Interface LIKE '%SPI%')
            use_substring_match = spec_name.lower() == "interface"
            is_impedance_at_freq = spec_name.lower() == "impedance @ frequency"

            or_conditions = []
            for value in values:
                for name in attr_names:
                    if use_substring_match:
                        pattern = f'%"{like_text(name)}"%{like_text(value)}%'
                    elif is_impedance_at_freq:
                        numeric_match = re.match(r'^(\d+(?:\.\d+)?)', value)
                        if numeric_match:
                            numeric_part = numeric_match.group(1)
                            pattern = f'%"{like_text(name)}", "{numeric_part}%'
                        else:
                            pattern = f'%"{like_text(name)}", "{like_text(value)}%'
                    else:
                        pattern = f'%"{like_text(name)}", "{like_text(value)}"%'
                    or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                    params.append(pattern)

            if or_conditions:
                combined = " OR ".join(or_conditions)
                sql_clauses.append(f"AND ({combined})")

            continue

        # Handle individual filter
        spec_filter = item
        if spec_filter.name in ("Module Flash", "Module PSRAM"):
            target = _filter_value(parse_memory_size, spec_filter.value)
            if target is not None:
                post_filter_metadata.append((spec_filter, {spec_filter.name}, parse_memory_size, target))
            else:
                ignored.append({"filter": f"{spec_filter.name} {spec_filter.operator} {spec_filter.value}",
                                "reason": "memory size could not be parsed"})
            continue
        # Get all possible attribute names (including aliases)
        attr_names = get_attribute_names(spec_filter.name)
        is_range = _is_range_spec(spec_filter.name, attr_names)

        if (spec_filter.operator == "=" and spec_filter.name.lower() == "type"
                and spec_filter.value.lower() in _POLARITY_VALUES):
            clause, clause_params = _polarity_clause([spec_filter.value])
            sql_clauses.append(clause)
            params.extend(clause_params)
            continue

        # Check if we have a pre-computed column for this spec (not for range specs: the column
        # holds the first number of "2.7V~5.5V")
        column_info = None
        if not is_range:
            for name in [spec_filter.name] + attr_names:
                if name in SPEC_TO_COLUMN:
                    column_info = SPEC_TO_COLUMN[name]
                    break

        if column_info and spec_filter.operator in (">=", "<=", ">", "<", "="):
            column_name, parser = column_info
            # Use the parser if available, otherwise try SPEC_PARSERS
            if parser is None:
                parser = _numeric_parser(spec_filter.name, attr_names)

            if parser:
                parsed_value = _filter_value(parser, spec_filter.value)
                if parsed_value is not None:
                    # Use SQL numeric comparison on pre-computed column
                    if spec_filter.operator == "=":
                        share = RESISTANCE_MATCH_TOLERANCE if parser is parse_resistance else 0.01
                        tolerance = abs(parsed_value) * share if parsed_value != 0 else 1e-9
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
        parser = _numeric_parser(spec_filter.name, attr_names)
        is_impedance_at_freq = spec_filter.name.lower() == "impedance @ frequency"

        parsed_value = None
        if parser:
            parsed_value = _filter_value(parser, spec_filter.value)

        if parsed_value is not None and spec_filter.operator in (">=", "<=", ">", "<", "="):
            # Numeric comparison - still need post-filtering for these
            if spec_filter.operator == "=" and is_impedance_at_freq:
                # "600Ohm" -> values starting "600" ("600Ω@100MHz"); the post-filter drops "6000Ω"
                numeric_part = re.match(r'^(\d+(?:\.\d+)?)', spec_filter.value.strip())
                prefix = numeric_part.group(1) if numeric_part else like_text(spec_filter.value)
                or_conditions = ["attributes LIKE ? ESCAPE '\\'" for _ in attr_names]
                params.extend(f'%"{like_text(name)}", "{prefix}%' for name in attr_names)
                sql_clauses.append(f"AND ({' OR '.join(or_conditions)})")
            elif spec_filter.operator == "=" and not is_range:
                or_conditions = []
                for name in attr_names:
                    value_patterns = generate_value_patterns(name, spec_filter.value, parsed_value)
                    for pattern in value_patterns:
                        or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                        params.append(pattern)
                if or_conditions:
                    combined = " OR ".join(or_conditions)
                    sql_clauses.append(f"AND ({combined})")
            elif spec_filter.name not in DIMENSION_SPEC_FIELDS:
                # Range comparisons, and every comparison on a range spec: check the attribute exists
                or_conditions = []
                for name in attr_names:
                    or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                    pattern = f'%"{like_text(name)}"%'
                    params.append(pattern)
                if or_conditions:
                    combined = " OR ".join(or_conditions)
                    sql_clauses.append(f"AND ({combined})")

            # Add to post-filter metadata (needs Python post-filtering)
            attr_names_set = set(attr_names)
            post_filter_metadata.append((spec_filter, attr_names_set, parser, parsed_value))

        elif spec_filter.operator == "=":
            # String exact value match (non-numeric)
            use_substring_match = spec_filter.name.lower() == "interface"

            if spec_filter.name in LIST_SPECS:
                clause, clause_params = _list_item_clause(attr_names, [spec_filter.value])
                sql_clauses.append(clause)
                params.extend(clause_params)
                continue

            or_conditions = []
            for name in attr_names:
                if use_substring_match:
                    pattern = f'%"{like_text(name)}"%{like_text(spec_filter.value)}%'
                elif is_impedance_at_freq:
                    pattern = f'%"{like_text(name)}", "{like_text(spec_filter.value)}%'
                else:
                    pattern = f'%"{like_text(name)}", "{like_text(spec_filter.value)}"%'
                or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                params.append(pattern)
            if or_conditions:
                combined = " OR ".join(or_conditions)
                sql_clauses.append(f"AND ({combined})")
        elif parser is None:
            ignored.append({
                "filter": f"{spec_filter.name} {spec_filter.operator} {spec_filter.value}",
                "reason": f"{spec_filter.name} isn't numeric, so only = works on it "
                          "(jlc_search_help lists which attributes are numeric)",
            })
        else:
            ignored.append({
                "filter": f"{spec_filter.name} {spec_filter.operator} {spec_filter.value}",
                "reason": f"couldn't read {spec_filter.value!r} as a value for {spec_filter.name}",
            })

    return sql_clauses, params, post_filter_metadata, ignored


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
    if _is_range_spec(spec_filter.name, attr_names) or spec_filter.name.lower() == "impedance @ frequency":
        return _numeric_parser(spec_filter.name, attr_names) is not None

    # Check if this spec has a pre-computed column
    for name in [spec_filter.name] + attr_names:
        if name in SPEC_TO_COLUMN:
            return False  # SQL handles this with indexed column query

    # Check if we need post-filtering for numeric comparison
    if spec_filter.operator in (">=", "<=", ">", "<"):
        return True
    if spec_filter.operator == "=":
        for name in attr_names:
            if callable(SPEC_PARSERS.get(name)):
                return True
    return False
