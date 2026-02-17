"""Main parser for smart natural language queries."""

import re
from dataclasses import dataclass, field
from typing import Any

from ..search.spec_filter import SpecFilter
from .packages import extract_package
from .values import ExtractedValue, extract_values
from .models import extract_model_number
from .types import extract_component_type, extract_mounting_type
from .semantic import extract_semantic_descriptors, remove_noise_words, CONNECTOR_NOISE_WORDS
from .mapping import map_value_to_spec, infer_subcategory_from_values
from .connectors import extract_connector_series, ConnectorSpec


@dataclass
class ParsedQuery:
    """Result of parsing a smart query string."""
    original: str
    remaining_text: str  # For FTS search
    subcategory: str | None = None
    spec_filters: list[Any] = field(default_factory=list)  # List of SpecFilter
    package: str | None = None
    model_number: str | None = None
    mounting_type: str | None = None  # "SMD" or "Through Hole"
    connector_spec: ConnectorSpec | None = None  # Extracted connector series/brand
    detected: dict[str, Any] = field(default_factory=dict)


def parse_smart_query(query: str) -> ParsedQuery:
    """Parse a natural language query into structured filters.

    This is a complete rewrite of the original parser with:
    1. Better token classification
    2. Category-aware attribute mapping
    3. Semantic descriptor handling
    4. Comprehensive package patterns
    5. Smart FTS fallback

    Examples:
        "10k resistor 0603 1%" -> R=10k, package=0603, tolerance=1%
        "100V mosfet" -> subcategory=mosfets, Vds>=100V
        "schottky diode SOD-123 1A" -> subcategory=schottky, package=SOD-123, If>=1A
        "TP4056 lithium battery charger" -> model=TP4056, fts="TP4056"

    Args:
        query: The natural language search query

    Returns:
        ParsedQuery with structured filters
    """
    result = ParsedQuery(original=query, remaining_text=query)
    detected: dict[str, Any] = {}
    remaining = query

    # Step 1: Extract model number (if present, it becomes the primary search term)
    model, remaining = extract_model_number(remaining)
    if model:
        result.model_number = model
        detected["model_number"] = model

    # Step 2: Extract package
    package, remaining, pkg_suggested_subcat = extract_package(remaining)
    if package:
        result.package = package
        detected["package"] = package

    # Step 2b: Extract mounting type (PTH/THT -> Through Hole, SMD/SMT -> SMD)
    mounting_type, remaining = extract_mounting_type(remaining)
    if mounting_type:
        result.mounting_type = mounting_type
        detected["mounting_type"] = mounting_type

    # Step 2c: Extract connector series and brand aliases BEFORE component type extraction
    # This must happen early because keywords like "jst sh", "qwiic" are also in subcategory_aliases
    # and would otherwise be consumed as generic "wire to board connector" without series info
    connector_spec, remaining = extract_connector_series(remaining)
    if connector_spec:
        result.connector_spec = connector_spec
        result.subcategory = "wire to board connector"
        detected["connector_spec"] = {
            "series": connector_spec.series,
            "pitch": connector_spec.pitch,
            "pins": connector_spec.pins,
        }
        detected["subcategory"] = result.subcategory
        # NOTE: Don't add pitch/pins as spec filters for connectors - most connectors in the
        # database have empty attributes dicts, so spec filters will match nothing. The pitch
        # and pin info is stored in connector_spec and used for FTS search instead.
        # if connector_spec.pitch:
        #     result.spec_filters.append(SpecFilter("Pitch", "=", f"{connector_spec.pitch}mm"))
        #     detected.setdefault("semantic", []).append(f"pitch={connector_spec.pitch}mm (from series)")
        # if connector_spec.pins:
        #     result.spec_filters.append(SpecFilter("Number of Pins", "=", f"{connector_spec.pins}P"))
        #     detected.setdefault("semantic", []).append(f"pins={connector_spec.pins} (from brand)")

    # Step 3: Extract component type (subcategory)
    subcategory, remaining, matched_keyword = extract_component_type(remaining)
    if subcategory:
        result.subcategory = subcategory
        detected["component_type"] = matched_keyword
        detected["subcategory"] = subcategory

        # Special case: if keyword contains type info, add the Type filter
        # e.g., "n-channel mosfet" should add Type=N-Channel
        if matched_keyword:
            kw_lower = matched_keyword.lower()
            if "n-channel" in kw_lower or kw_lower == "nmos":
                result.spec_filters.append(SpecFilter("Type", "=", "N-Channel"))
                detected.setdefault("semantic", []).append("n-channel (from keyword)")
            elif "p-channel" in kw_lower or kw_lower == "pmos":
                result.spec_filters.append(SpecFilter("Type", "=", "P-Channel"))
                detected.setdefault("semantic", []).append("p-channel (from keyword)")
            elif kw_lower in ("npn", "npn transistor"):
                result.spec_filters.append(SpecFilter("Type", "=", "NPN"))
                detected.setdefault("semantic", []).append("npn (from keyword)")
            elif kw_lower in ("pnp", "pnp transistor"):
                result.spec_filters.append(SpecFilter("Type", "=", "PNP"))
                detected.setdefault("semantic", []).append("pnp (from keyword)")

        # Special case: "radial" or "through hole" with electrolytic -> leaded capacitors
        if subcategory.lower() == "aluminum electrolytic capacitors - smd":
            remaining_lower = remaining.lower()
            if re.search(r'\b(radial|through.?hole|pth|leaded)\b', remaining_lower):
                result.subcategory = "aluminum electrolytic capacitors - leaded"
                detected["subcategory"] = result.subcategory
                detected.setdefault("semantic", []).append("radial/through-hole (leaded)")
                # Remove the modifier from remaining text
                remaining = re.sub(r'\b(radial|through.?hole|pth|leaded)\b', '', remaining, flags=re.IGNORECASE).strip()
                remaining = re.sub(r'\s+', ' ', remaining)
    elif pkg_suggested_subcat:
        # Use package-suggested subcategory (e.g., USB-C -> USB connectors)
        result.subcategory = pkg_suggested_subcat
        detected["subcategory_from_package"] = pkg_suggested_subcat

    # Step 4: Extract numeric values
    values, remaining = extract_values(remaining)
    if values:
        detected["values"] = [{"raw": v.raw, "type": v.unit_type, "normalized": v.normalized} for v in values]

    # Step 4a-pre: Filter out dimension values for display components
    # Display resolutions like "128x64" look like dimensions but should not be treated as such
    if result.subcategory and 'display' in result.subcategory.lower():
        values = [v for v in values if v.unit_type != "dimensions"]
        if values:
            detected["values"] = [{"raw": v.raw, "type": v.unit_type, "normalized": v.normalized} for v in values]

    # Step 4a: Post-process standalone numbers as pin counts for connector types
    # This handles cases like "8 pin header" where "pin header" was extracted first,
    # leaving "8" alone which doesn't match the "N pin" pattern
    connector_words = ("header", "connector", "terminal", "socket", "plug", "receptacle")
    is_connector = matched_keyword and any(word in matched_keyword.lower() for word in connector_words)
    if is_connector:
        # Look for standalone numbers in remaining text that could be pin counts
        standalone_num_match = re.search(r'\b(\d+)\b', remaining)
        if standalone_num_match:
            # Check if this number isn't already captured as a value
            num_val = int(standalone_num_match.group(1))
            # Only treat as pin count if reasonable (1-200 pins) and not already detected
            if 1 <= num_val <= 200:
                already_has_pin_count = any(v.unit_type == "pin_count" for v in values)
                if not already_has_pin_count:
                    values.append(ExtractedValue(
                        raw=standalone_num_match.group(0),
                        value=num_val,
                        unit_type="pin_count",
                        normalized=f"{num_val}P"
                    ))
                    detected.setdefault("values", []).append({
                        "raw": standalone_num_match.group(0),
                        "type": "pin_count",
                        "normalized": f"{num_val}P"
                    })
                    # Remove the number from remaining
                    remaining = remaining[:standalone_num_match.start()] + remaining[standalone_num_match.end():]
                    remaining = re.sub(r'\s+', ' ', remaining).strip()

    # Step 4b: Infer subcategory from values if not already set
    if not result.subcategory and values:
        inferred = infer_subcategory_from_values(values)
        if inferred:
            result.subcategory = inferred
            detected["subcategory_inferred"] = inferred

    # Step 4c: Override subcategory based on keywords in remaining text
    # This handles cases like "10K trimmer" where value was detected first
    remaining_lower = remaining.lower()
    if re.search(r'\b(trimmer|potentiometer|trimpot|variable\s*resistor)\b', remaining_lower):
        # Potentiometer/trimmer keywords should override chip resistor inference
        if not result.subcategory or result.subcategory.lower() == "chip resistor - surface mount":
            result.subcategory = "potentiometers, variable resistors"
            detected["subcategory"] = result.subcategory
            detected.setdefault("semantic", []).append("potentiometer/trimmer (from keyword)")
            # Remove the keyword from remaining
            remaining = re.sub(r'\b(trimmer|potentiometer|trimpot|variable\s*resistor)\b', '', remaining, flags=re.IGNORECASE).strip()
            remaining = re.sub(r'\s+', ' ', remaining)

    # Step 4d: Handle standalone numbers as impedance for ferrite beads
    # "ferrite bead 0603 30" -> the "30" should be parsed as 30Ω impedance
    if result.subcategory and result.subcategory.lower() == "ferrite beads":
        standalone_num_match = re.search(r'\b(\d+)\b', remaining)
        if standalone_num_match:
            num_val = int(standalone_num_match.group(1))
            # Common ferrite bead impedance values: 10-2000Ω typically
            if 1 <= num_val <= 5000:
                # Check if we already have an impedance value
                already_has_impedance = any(v.unit_type == "resistance" for v in values)
                if not already_has_impedance:
                    values.append(ExtractedValue(
                        raw=standalone_num_match.group(0),
                        value=num_val,
                        unit_type="resistance",  # Will map to Impedance @ Frequency
                        normalized=f"{num_val}Ohm"
                    ))
                    detected.setdefault("values", []).append({
                        "raw": standalone_num_match.group(0),
                        "type": "impedance",
                        "normalized": f"{num_val}Ohm"
                    })
                    detected.setdefault("semantic", []).append(f"impedance={num_val}Ω (from standalone number)")
                    # Remove the number from remaining
                    remaining = remaining[:standalone_num_match.start()] + remaining[standalone_num_match.end():]
                    remaining = re.sub(r'\s+', ' ', remaining).strip()

    # Step 5: Extract semantic descriptors
    semantic_filters, remaining = extract_semantic_descriptors(remaining)
    if semantic_filters:
        detected["semantic"] = [f.source for f in semantic_filters]

    # Step 6: Build spec filters from extracted values (category-aware)
    # Note: result.spec_filters may already have filters from Step 3 (keyword-based type filters)

    # Categories where dimensions should be treated as package filters, not spec filters
    # These components use package names like "SMD,4x4mm" rather than a "Dimensions" attribute
    dimension_as_package_categories = {
        "inductors (smd)", "power inductors", "inductors, coils, chokes",
        "led", "leds", "light emitting diodes",
    }
    subcat_lower = (result.subcategory or "").lower()

    for value in values:
        # Special handling: dimensions become package filter for inductors/LEDs
        # e.g., "4x4mm" -> package="SMD,4x4mm" instead of Dimensions="4x4mm"
        if value.unit_type == "dimensions":
            if any(cat in subcat_lower for cat in dimension_as_package_categories):
                # Convert to package format used by JLCPCB (e.g., "SMD,4x4mm")
                if not result.package:
                    result.package = f"SMD,{value.normalized}"
                    detected["package_from_dimensions"] = result.package
                continue  # Don't add as spec filter

        # Special handling: skip spec filters for connectors
        # Most connectors in the database have empty attributes dicts, so spec filters fail
        # Pin count, pitch, etc. should be used in FTS search instead
        if result.subcategory and 'connector' in result.subcategory.lower():
            continue  # Don't add spec filters for connectors

        spec_name, operator = map_value_to_spec(value, subcategory, matched_keyword)
        result.spec_filters.append(SpecFilter(spec_name, operator, value.normalized))

    # Add semantic filters
    for sf in semantic_filters:
        result.spec_filters.append(SpecFilter(sf.spec_name, sf.operator, sf.value))

    # Step 6b: Handle "dual" for MOSFETs
    # "dual" is too common a word to add to NOISE_WORDS, but in MOSFET context
    # it means Number="2 N-Channel" or "2 P-Channel"
    if (result.subcategory and result.subcategory.lower() == "mosfets"
            and re.search(r'\bdual\b', remaining, re.IGNORECASE)):
        # Find which channel type was specified
        channel_type = None
        for sf in result.spec_filters:
            if sf.name == "Type" and sf.value in ("N-Channel", "P-Channel"):
                channel_type = sf.value
                break

        if channel_type:
            # Add Number filter for dual channel
            result.spec_filters.append(SpecFilter("Number", "=", f"2 {channel_type}"))
            detected.setdefault("semantic", []).append(f"dual (-> Number=2 {channel_type})")

        # Remove "dual" from remaining text to prevent FTS failure
        remaining = re.sub(r'\bdual\b', '', remaining, flags=re.IGNORECASE)
        remaining = re.sub(r'\s+', ' ', remaining).strip()

    # Step 6c: Handle "single row" / "double row" for pin headers
    # Convert "16 pin header single row" -> Pin Structure = "1x16P"
    header_keywords = ("header", "pin header", "male header", "female header")
    is_header = matched_keyword and any(kw in matched_keyword.lower() for kw in header_keywords)
    is_header = is_header or (result.subcategory and "header" in result.subcategory.lower())

    if is_header and re.search(r'\b(single|1)\s*row\b', remaining, re.IGNORECASE):
        # Find any "Number of Pins" filter and convert to "Pin Structure" with 1x prefix
        for i, sf in enumerate(result.spec_filters):
            if sf.name == "Number of Pins" and sf.value.endswith("P"):
                pin_count = sf.value[:-1]  # Remove "P" suffix
                if pin_count.isdigit():
                    result.spec_filters[i] = SpecFilter("Pin Structure", "=", f"1x{pin_count}P")
                    detected.setdefault("semantic", []).append(f"single row (-> Pin Structure=1x{pin_count}P)")
        # Remove "single row" from remaining text
        remaining = re.sub(r'\b(single|1)\s*row\b', '', remaining, flags=re.IGNORECASE)
        remaining = re.sub(r'\s+', ' ', remaining).strip()

    if is_header and re.search(r'\b(double|dual|2)\s*row\b', remaining, re.IGNORECASE):
        # Find any "Number of Pins" filter and convert to "Pin Structure" with 2x prefix
        # Note: for double row, the total pins = 2 * pins_per_row, so we need to divide
        for i, sf in enumerate(result.spec_filters):
            if sf.name == "Number of Pins" and sf.value.endswith("P"):
                pin_count = sf.value[:-1]
                if pin_count.isdigit():
                    total = int(pin_count)
                    pins_per_row = total // 2 if total % 2 == 0 else total
                    result.spec_filters[i] = SpecFilter("Pin Structure", "=", f"2x{pins_per_row}P")
                    detected.setdefault("semantic", []).append(f"double row (-> Pin Structure=2x{pins_per_row}P)")
        # Remove "double/dual row" from remaining text
        remaining = re.sub(r'\b(double|dual|2)\s*row\b', '', remaining, flags=re.IGNORECASE)
        remaining = re.sub(r'\s+', ' ', remaining).strip()

    # Step 7: Clean up remaining text
    # Step 7a: Replace connector-specific synonyms
    # "magnetics" is a common term for RJ45 connectors with integrated magnetics (transformers)
    # JLCPCB lists these as "Filtered" in descriptions
    if subcategory and 'connector' in subcategory.lower():
        remaining = re.sub(r'\bmagnetics?\b', 'filtered', remaining, flags=re.IGNORECASE)

    remaining = remove_noise_words(remaining)

    # Step 7b: Remove connector-specific noise words when in connector context
    # Words like "power", "data", "signal" describe USB-C functionality but aren't searchable
    # Also applies to pin headers (male/female not indexed in descriptions)
    if subcategory and ('connector' in subcategory.lower() or 'header' in subcategory.lower()):
        words = remaining.split()
        remaining = ' '.join(w for w in words if w.lower() not in CONNECTOR_NOISE_WORDS)

    # Remove orphaned hyphens and single characters (e.g., "- -F" -> "")
    remaining = re.sub(r'\b[A-Za-z]\b', '', remaining)  # Single letters
    remaining = re.sub(r'\s*-\s*', ' ', remaining)  # Orphaned hyphens
    remaining = re.sub(r'\s+', ' ', remaining).strip()

    # Step 8: Determine what to use for FTS search
    # If we have a model number, use ONLY that for FTS (high precision)
    # If we have structured filters, we may not need FTS at all
    if model:
        result.remaining_text = model  # Search only for the model number
    elif remaining and len(remaining) >= 2:
        result.remaining_text = remaining
    elif result.spec_filters or subcategory:
        # Structured filters exist, FTS may not be needed
        result.remaining_text = ""
    else:
        result.remaining_text = query  # Fall back to original

    # Step 8b: Add connector series term to FTS for better filtering
    # This helps filter by series name in part descriptions/model numbers
    if result.connector_spec and result.connector_spec.fts_term:
        fts_term = result.connector_spec.fts_term
        if result.remaining_text:
            # Add series term if not already present
            if fts_term.lower() not in result.remaining_text.lower():
                result.remaining_text = f"{fts_term} {result.remaining_text}"
        else:
            result.remaining_text = fts_term

    result.detected = detected

    return result


def merge_spec_filters(
    manual_filters: list[Any] | None,
    auto_filters: list[Any] | None,
) -> list[Any] | None:
    """Merge manual and auto-detected spec filters.

    Manual filters take precedence for the same attribute name (case-insensitive).
    Auto-detected filters are added only if no manual filter exists for that attribute.

    Args:
        manual_filters: User-provided spec filters (take precedence)
        auto_filters: Auto-detected filters from smart parsing

    Returns:
        Merged list of filters, or None if both inputs are None/empty
    """
    if not auto_filters:
        return manual_filters
    if not manual_filters:
        return auto_filters

    # Manual filters take precedence - build set of their attribute names
    manual_names = {f.name.lower() for f in manual_filters}

    # Start with manual filters, add auto filters that don't conflict
    merged = list(manual_filters)
    for auto_filter in auto_filters:
        if auto_filter.name.lower() not in manual_names:
            merged.append(auto_filter)

    return merged if merged else None
