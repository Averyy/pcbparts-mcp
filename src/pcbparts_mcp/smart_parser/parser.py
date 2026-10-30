"""Main parser for smart natural language queries."""

import re
from dataclasses import dataclass, field, replace
from typing import Any

from ..search.spec_filter import ConnectorFilter, FuseFilter, SpecFilter
from ..subcategory_aliases import SUBCATEGORY_GROUPS
from .packages import extract_package, extract_package_choices
from .values import ExtractedValue, extract_values, normalize_value_notation
from .models import extract_model_number
from .types import PD_ROLE_PATTERN, extract_component_type, extract_mounting_type
from .semantic import extract_gate_drive, extract_semantic_descriptors, remove_noise_words, CONNECTOR_NOISE_WORDS
from .mapping import FUSE_ATTRIBUTE_MAP, map_value_to_spec, infer_subcategory_from_values
from .connectors import extract_connector_series, extract_connector_manufacturer, ConnectorSpec


@dataclass
class ParsedQuery:
    """Result of parsing a smart query string."""
    original: str
    remaining_text: str  # For FTS search
    subcategory: str | None = None
    subcategories: list[str] | None = None  # a generic word's group ("inductor": four subcategories)
    spec_filters: list[Any] = field(default_factory=list)  # List of SpecFilter
    preferred_specs: list[SpecFilter] = field(default_factory=list)  # Sparse PD attributes rank in SQL
    gate_drive_v: float | None = None
    package: str | None = None
    packages: list[str] = field(default_factory=list)
    model_number: str | None = None
    mounting_type: str | None = None  # "SMD" or "Through Hole"
    connector_spec: ConnectorSpec | None = None  # Extracted connector series/brand
    detected: dict[str, Any] = field(default_factory=dict)


def parse_smart_query(query: str, *, strict: bool = False, subcategory_hint: str | None = None) -> ParsedQuery:
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
        subcategory_hint: Explicit searched subcategory, used for fuse ratings and gate drive

    Returns:
        ParsedQuery with structured filters
    """
    result = ParsedQuery(original=query, remaining_text=query)
    detected: dict[str, Any] = {}
    remaining = query.replace("µ", "u").replace("μ", "u").replace("Ω", "ohm")

    # LED12 is a BOM reference here, not an IC model. Normalize before model
    # extraction, but only in the LED/diode conflict covered by this rule.
    if re.search(r'\bdiodes?\b', remaining, re.IGNORECASE):
        remaining = re.sub(r'\bLED\d+\b', 'LED', remaining, flags=re.IGNORECASE)

    # Step 1: Extract model number (if present, it becomes the primary search term)
    model, remaining = extract_model_number(remaining)
    if model:
        result.model_number = model
        detected["model_number"] = model

    remaining = normalize_value_notation(remaining)
    for pattern, key, value in (
        (r"\b(?:no assembly fee|no fee)\b", "library_type", "no_fee"),
        (r"\bbasic(?: part)?\b", "library_type", "basic"),
        (r"\bpreferred\b", "library_type", "preferred"),
        (r"\b(?:cheapest|lowest price)\b", "sort_by", "price"),
    ):
        if re.search(pattern, remaining, re.IGNORECASE):
            detected[key] = value
            remaining = re.sub(pattern, " ", remaining, flags=re.IGNORECASE)

    # Step 2: Extract package
    result.packages, remaining = extract_package_choices(remaining)
    if result.packages:
        detected["packages"] = result.packages
        package, pkg_suggested_subcat = None, None
    else:
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

    # Step 3: Extract component type (subcategory)
    memory_is_spec = bool(model) or bool(re.search(r"\b(module|microcontroller|mcu)\b", remaining, re.IGNORECASE))
    subcategory, remaining, matched_keyword = extract_component_type(remaining, memory_is_spec=memory_is_spec)
    if (model and model.upper().startswith("ESP32") and not subcategory
            and re.search(r"\b(?:flash|psram)\b", remaining, re.IGNORECASE)):
        subcategory = "wifi modules"
        remaining = re.sub(r"\bmodule\b", " ", remaining, flags=re.IGNORECASE)
    if subcategory:
        result.subcategory = subcategory
        detected["component_type"] = matched_keyword
        detected["subcategory"] = subcategory
        group = SUBCATEGORY_GROUPS.get((matched_keyword or "").lower())
        if group:
            result.subcategories = list(group)
            detected["subcategories"] = result.subcategories

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

    # Mounting can change an SMD-only default, but must not replace a compatible category.
    if mounting_type == "Through Hole":
        through_hole = {
            "chip resistor - surface mount": "through hole resistors",
            "aluminum electrolytic capacitors - smd": "aluminum electrolytic capacitors - leaded",
        }.get((result.subcategory or "").lower())
        if through_hole:
            result.subcategory = through_hole
            detected["subcategory"] = through_hole

    # Step 3b: Regulator specifics: buck/boost, and voltages marked input or output
    subcat_now = (result.subcategory or "").lower()
    pd_sink = False
    if subcat_now == "usb pd":
        pd_sink = bool(re.search(r'\b(?:sinks?|triggers?|receivers?)\b', remaining, re.IGNORECASE))
        pd_source = bool(re.search(r'\bsources?\b', remaining, re.IGNORECASE))
        dual_role = re.compile(r'\b(?:dual[-\s]+role|drp)\b', re.IGNORECASE)
        if dual_role.search(remaining):
            pd_sink = pd_source = True
            remaining = dual_role.sub(' ', remaining)
        if strict and pd_sink and pd_source:
            # Repeated Type filters are ORed by the search builder, so they cannot
            # honestly enforce both roles. Report this unsupported strict constraint.
            detected.setdefault("unsupported_constraints", []).append("PD sink and source together")
        for requested, kind in ((pd_sink, "Power Receiver Controller"), (pd_source, "Power Supply Controller")):
            if requested:
                target = result.spec_filters if strict else result.preferred_specs
                target.append(SpecFilter("Type", "=", kind))
        remaining = PD_ROLE_PATTERN.sub(' ', remaining)
    if subcat_now == "dc-dc converters":
        remaining = _add_topology(query, remaining, result, detected)
    if subcat_now in ("dc-dc converters", _LDO):
        remaining = _add_input_output_voltages(remaining, subcat_now, result, detected)
    if subcat_now == "translators, level shifters":
        pair = _VOLTAGE_TO_VOLTAGE.search(remaining)
        if pair:
            for side, value in zip(("VCCA", "VCCB"), pair.groups()):
                result.spec_filters.append(SpecFilter(f"Voltage - Supply({side})", "=", value.replace(" ", "")))
            remaining = remaining[:pair.start()] + " " + remaining[pair.end():]
    if matched_keyword == "fuel gauge":
        result.spec_filters.append(SpecFilter("The Chip Type", "=", "Monitoring IC"))
    if subcat_now in ("wifi modules", "microcontrollers (mcu/mpu/soc)", "nor flash", "nand flash"):
        remaining = _add_memory_sizes(remaining, subcat_now, result, detected)
    if subcat_now == "usb connectors":
        _add_usb_type(query, result, detected)
    if subcat_now == "coaxial connectors (rf)":
        _add_rf_series(query, result, detected)

    # Named comparisons must be consumed before a bare current/voltage gets its default
    # quantity and >= operator (Iq is not load current; Vf is not reverse voltage).
    remaining = _add_named_comparisons(remaining, result, detected)

    if (subcategory_hint or result.subcategory or "").lower() == "mosfets":
        result.gate_drive_v, remaining = extract_gate_drive(remaining)
        if result.gate_drive_v is not None:
            detected["gate_drive_v"] = result.gate_drive_v

    # Step 4: Extract numeric values
    connector_context = bool(result.connector_spec) or any(
        word in subcat_now for word in ("connector", "header", "terminal block", "ffc cable")
    )
    values, remaining = extract_values(remaining, connector_context=connector_context and not strict)
    if values:
        detected["values"] = [{"raw": v.raw, "type": v.unit_type, "normalized": v.normalized} for v in values]

    # Step 4a-pre: Filter out dimension values for display components
    # Display resolutions like "128x64" look like dimensions but should not be treated as such
    if result.subcategory and 'display' in result.subcategory.lower():
        if strict:
            detected.setdefault("unsupported_constraints", []).extend(v.raw for v in values if v.unit_type == "dimensions")
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
    if connector_context and not strict and result.connector_spec:
        # Explicit query values take precedence over the series/ecosystem defaults.
        if result.connector_spec.pitch and not any(v.unit_type == "pitch" for v in values):
            result.spec_filters.append(ConnectorFilter("Pitch", "=", f"{result.connector_spec.pitch:g}mm"))
        if result.connector_spec.pins and not any(v.unit_type in ("pin_count", "position_count") for v in values):
            result.spec_filters.append(ConnectorFilter("Number of Pins", "=", f"{result.connector_spec.pins}P"))

    for value in values:
        if pd_sink and value.unit_type == "voltage":
            # This is the negotiated PD output, not the IC's own supply rail.
            target = result.spec_filters if strict else result.preferred_specs
            target.append(SpecFilter("Output Voltage", "=", value.normalized))
            continue
        # Special handling: dimensions become package filter for inductors/LEDs
        # e.g., "4x4mm" -> package="SMD,4x4mm" instead of Dimensions="4x4mm"
        if value.unit_type == "dimensions":
            if any(cat in subcat_lower for cat in dimension_as_package_categories):
                # Convert to package format used by JLCPCB (e.g., "SMD,4x4mm")
                if not result.package:
                    result.package = f"SMD,{value.normalized}"
                    detected["package_from_dimensions"] = result.package
                elif strict:
                    detected.setdefault("unsupported_constraints", []).append(value.raw)
                continue  # Don't add as spec filter

        # Count/pitch constraints are fitted to the searched subcategory's populated attributes
        # by jlc_search. Keep strict mode and other connector specs on their existing path.
        if connector_context and not strict and value.unit_type in ("pin_count", "position_count", "pitch"):
            spec_name, _ = map_value_to_spec(value, result.subcategory, matched_keyword)
            result.spec_filters.append(ConnectorFilter(spec_name, "=", value.normalized))
            continue
        if 'connector' in subcat_lower:
            if strict:
                detected.setdefault("unsupported_constraints", []).append(value.raw)
            elif value.unit_type == "dimensions" and subcat_lower == "dc power connectors":
                # 5.5x2.1mm is the plug size; jacks list contact diameters instead (a jack
                # for that plug lists a 6.4mm outside contact and a 2mm center pin).
                detected.setdefault("not_searched", []).append(
                    f"{value.raw}: JLCPCB lists DC jacks' contact diameters, not the plug size; "
                    "check the datasheet")
            continue

        # Explicit fuse subcategories override the generic keyword's electrical fields.
        fuse_subcategory = (subcategory_hint or result.subcategory or "").lower()
        is_fuse_rating = fuse_subcategory in FUSE_ATTRIBUTE_MAP and value.unit_type in ("current", "voltage")
        spec_name, operator = map_value_to_spec(value, fuse_subcategory if is_fuse_rating else subcategory, matched_keyword)
        if written := _written_comparison(query, value.raw, operator):
            operator = written
            remaining = re.sub(r'(?<!\S)(?:<=|>=|<|>)(?!\S)', ' ', remaining).strip()
        filter_type = FuseFilter if is_fuse_rating else SpecFilter
        result.spec_filters.append(filter_type(spec_name, operator, value.normalized))

    # Add semantic filters
    for sf in semantic_filters:
        name = "Channel Type" if subcat_now == "translators, level shifters" and sf.spec_name == "Polarity" else sf.spec_name
        result.spec_filters.append(SpecFilter(name, sf.operator, sf.value))

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
    # Step 7a: "magnetics" (an RJ45 jack with built-in transformers). JLCPCB marks only 23 jacks
    # "Filtered" and records magnetics nowhere else, so searching for that word hid the usual
    # magjacks (HR913550A, HR911130A, J1B1211CCD). Leave it out and say so.
    if not strict and subcategory and 'connector' in subcategory.lower() and re.search(r'\bmagnetics?\b', remaining, re.IGNORECASE):
        remaining = re.sub(r'\b(?:integrated\s+)?magnetics?\b', '', remaining, flags=re.IGNORECASE)
        remaining = re.sub(r'\s+', ' ', remaining).strip()
        detected.setdefault("not_searched", []).append(
            "magnetics: JLCPCB doesn't record it for most RJ45 jacks; check the datasheet")

    if not strict:
        remaining = remove_noise_words(remaining)

    # Step 7b: Remove connector-specific noise words when in connector context
    # Words like "power", "data", "signal" describe USB-C functionality but aren't searchable
    # Also applies to pin headers (male/female not indexed in descriptions)
    if not strict and subcategory and ('connector' in subcategory.lower() or 'header' in subcategory.lower()):
        words = remaining.split()
        remaining = ' '.join(w for w in words if w.lower() not in CONNECTOR_NOISE_WORDS)

    # Remove orphaned hyphens and single characters (e.g., "- -F" -> "")
    if not strict:
        remaining = re.sub(r'\b[A-Za-z]\b', '', remaining)  # Single letters
    remaining = re.sub(r'\s*-\s*', ' ', remaining)  # Orphaned hyphens
    remaining = re.sub(r'\s+', ' ', remaining).strip()

    unsupported = re.findall(
        r"\b\d+(?:\.\d+)?(?:[a-zA-Z]+|\s+(?:[a-zA-Z]*[FHAVW]|[a-zA-Z]*ohm))\b",
        remaining,
    )
    if unsupported and not model:
        detected.setdefault("unsupported_constraints", []).extend(unsupported)

    # Step 8: Determine what to use for FTS search
    # If we have a model number, use ONLY that for FTS (high precision)
    # If we have structured filters, we may not need FTS at all
    if model:
        result.remaining_text = f"{model} {remaining}".strip() if strict else model
    elif remaining and len(remaining) >= 2:
        result.remaining_text = remaining
    elif result.spec_filters or subcategory or result.package or result.packages or result.gate_drive_v is not None:
        # Structured filters exist, FTS may not be needed
        result.remaining_text = ""
    else:
        result.remaining_text = query  # Fall back to original

    # Strict mode retains its existing text constraints. Otherwise the series ranks in SQL
    # instead of excluding compatible parts that have no recorded Reference Series.
    if strict and result.connector_spec and result.connector_spec.fts_term:
        fts_term = result.connector_spec.fts_term
        if result.remaining_text:
            # Add series term if not already present
            if fts_term.lower() not in result.remaining_text.lower():
                result.remaining_text = f"{fts_term} {result.remaining_text}"
        else:
            result.remaining_text = fts_term

    if not strict and result.connector_spec:
        result.remaining_text = re.sub(r"\b(?:jst|connectors?)\b", " ", result.remaining_text, flags=re.IGNORECASE)
        result.remaining_text = re.sub(r"\s+", " ", result.remaining_text).strip()

    # Attach ordering after parsing so a maker alone changes no text or filters.
    manufacturer = extract_connector_manufacturer(query)
    if manufacturer:
        result.connector_spec = replace(result.connector_spec or ConnectorSpec(), manufacturer=manufacturer)

    result.detected = detected

    return result


_LDO = "voltage regulators - linear, low drop out (ldo) regulators"
_VOLTAGE = r"(\d+(?:\.\d+)?\s*[mk]?V)\b"
# "24V input", "input 24V", "vin 24V"; "3.3V output", "5V out", "vout 3.3V"; "12V to 5V"
_INPUT_VOLTAGE = re.compile(rf"(?:\b(?:input|vin|from)\s*(?:voltage\s*)?(?:of\s*)?(?:up\s+to\s*)?{_VOLTAGE})|(?:{_VOLTAGE}\s*(?:max\s+)?(?:input|vin)\b)|(?:\bup\s+to\s*{_VOLTAGE}\s*in\b)", re.IGNORECASE)
_OUTPUT_VOLTAGE = re.compile(rf"(?:\b(?:output|vout|out)\s*(?:voltage\s*)?(?:of\s*)?{_VOLTAGE})|(?:{_VOLTAGE}\s*(?:output|out|vout)\b)", re.IGNORECASE)
_VOLTAGE_TO_VOLTAGE = re.compile(rf"{_VOLTAGE}\s*(?:to|->|→)\s*{_VOLTAGE}", re.IGNORECASE)


def _add_topology(text: str, remaining: str, result: ParsedQuery, detected: dict[str, Any]) -> str:
    """"buck converter" and "boost" picked DC-DC converters but not the topology, so "boost
    converter" listed buck converters first. Topology is listed per part ("Boost、Buck")."""
    lowered = text.lower()
    if re.search(r"\bbuck[- ]?boost\b", lowered):
        topology = "Buck-Boost"
    elif re.search(r"\b(buck|step[- ]?down)\b", lowered):
        topology = "Buck"
    elif re.search(r"\b(boost|step[- ]?up)\b", lowered):
        topology = "Boost"
    else:
        return remaining
    result.spec_filters.append(SpecFilter("Topology", "=", topology))
    detected.setdefault("semantic", []).append(f"{topology.lower()} (-> Topology={topology})")
    remaining = re.sub(r"\b(buck[- ]?boost|buck|boost|step[- ]?(?:down|up))\b", "", remaining, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", remaining).strip()


def _add_input_output_voltages(remaining: str, subcategory: str, result: ParsedQuery, detected: dict[str, Any]) -> str:
    """Voltages marked input or output, or "12V to 5V". Input is inside a DC-DC converter's
    supply range; an LDO lists only its maximum input, so that must reach it. Output is inside
    the output range (an adjustable part covers it)."""
    input_filter = ("Supply Voltage", ">=" if subcategory == _LDO else "=")
    output_filter = ("Vout", "=") if subcategory == _LDO else _EXACT_OUTPUT
    found: list[tuple[tuple[str, str], str]] = []

    def take(match: re.Match[str], spec: tuple[str, str]) -> str:
        found.append((spec, next(g for g in match.groups() if g)))
        return " "

    pair = _VOLTAGE_TO_VOLTAGE.search(remaining)
    if pair:
        found.append((input_filter, pair.group(1)))
        found.append((output_filter, pair.group(2)))
        remaining = remaining[:pair.start()] + " " + remaining[pair.end():]
    remaining = _INPUT_VOLTAGE.sub(lambda m: take(m, input_filter), remaining)
    remaining = _OUTPUT_VOLTAGE.sub(lambda m: take(m, output_filter), remaining)
    for (spec_name, operator), raw in found:
        value = re.sub(r"\s+", "", raw)
        result.spec_filters.append(SpecFilter(spec_name, operator, value))
        detected.setdefault("semantic", []).append(f"{raw} (-> {spec_name} {operator} {value})")
    return re.sub(r"\s+", " ", remaining).strip()


def _add_memory_sizes(remaining: str, subcategory: str, result: ParsedQuery, detected: dict[str, Any]) -> str:
    """Memory belongs to the selected MCU/module; bare flash still selects a memory IC.

    ESP32 module N/R codes are checked at search time; no database build change is needed.
    """
    size = r"(\d+(?:\.\d+)?\s*(?:[KM]B|[KM]bit))"
    pattern = re.compile(rf"\b{size}\s*(flash|psram)\b|\b(flash|psram)\s*{size}\b", re.IGNORECASE)

    def take(match: re.Match[str]) -> str:
        raw, kind = (match[1], match[2]) if match[1] else (match[4], match[3])
        if subcategory == "wifi modules":
            name = "Module PSRAM" if kind.lower() == "psram" else "Module Flash"
        elif subcategory == "microcontrollers (mcu/mpu/soc)":
            name = "SRAM" if kind.lower() == "psram" else "Program Storage Size"
        else:
            name = "Memory Size"
        value = raw.replace(" ", "")
        result.spec_filters.append(SpecFilter(name, ">=", value))
        detected.setdefault("semantic", []).append(f"{match[0]} (-> {name} >= {value})")
        return " "

    def take_size(match: re.Match[str]) -> str:
        result.spec_filters.append(SpecFilter("Memory Size", ">=", match[1].replace(" ", "")))
        return " "

    remaining = pattern.sub(take, remaining)
    if subcategory in ("nor flash", "nand flash"):
        # Component extraction already consumed "flash" in "SPI flash 16MB".
        remaining = re.sub(rf"\b{size}\b", take_size, remaining, flags=re.IGNORECASE)
    return remaining


_EXACT_OUTPUT = ("Output Voltage", "=")


def _written_comparison(query: str, raw: str, default: str) -> str | None:
    """A sign written before a value ("< 25V") when it points against the default operator, which
    made "capacitor 10uF < 25V" a Voltage >= 25V filter. ">50V" keeps the default >=. The raw value
    is spelled as extract_values read it ("< 10mΩ" holds 10mohm)."""
    match = re.search(rf"(<=|>=|<|>)\s*{re.escape(raw)}(?![\w.])", normalize_value_notation(query))
    if not match or (default != "=" and match[1][0] == default[0]):
        return None
    return match[1]


_NAMED_COMPARISONS = [
    (re.compile(r"\b(?:quiescent\s+current(?:\s*\(Iq\))?|standby\s+current|Supply\s+Current\s*\(Iq\)|Iq)\s*(<=|>=|<|>|=)\s*(\d+(?:\.\d+)?\s*[um]?A)\b", re.IGNORECASE), "Quiescent Current"),
    (re.compile(r"\bVf\s*(<=|>=|<|>|=)\s*(\d+(?:\.\d+)?\s*[mk]?V)\b", re.IGNORECASE), "Vf"),
]


def _add_named_comparisons(remaining: str, result: ParsedQuery, detected: dict[str, Any]) -> str:
    """Keep the quantity and direction of explicit idle-current and forward-voltage limits."""
    for pattern, name in _NAMED_COMPARISONS:
        def take(match: re.Match[str]) -> str:
            operator, raw = match.groups()
            value = re.sub(r"\s+", "", raw)
            result.spec_filters.append(SpecFilter(name, operator, value))
            detected.setdefault("semantic", []).append(f"{match.group(0)} (-> {name} {operator} {value})")
            return " "
        remaining = pattern.sub(take, remaining)
    return re.sub(r"\s+", " ", remaining).strip()


# USB connectors list "Connector Type": Type-C, Type-A, Micro-B, Type-B, Mini-B
_USB_TYPES = [
    (re.compile(r"\b(?:micro[- ]?usb|micro[- ]?b|usb[- ]?micro)\b", re.IGNORECASE), "Micro-B"),
    (re.compile(r"\b(?:mini[- ]?usb|mini[- ]?b|usb[- ]?mini)\b", re.IGNORECASE), "Mini-B"),
    (re.compile(r"\b(?:usb[- ]?(?:type[- ]?)?c|type[- ]?c)\b", re.IGNORECASE), "Type-C"),
    (re.compile(r"\b(?:usb[- ]?(?:type[- ]?)?a|type[- ]?a)\b", re.IGNORECASE), "Type-A"),
    (re.compile(r"\b(?:usb[- ]?(?:type[- ]?)?b|type[- ]?b)\b", re.IGNORECASE), "Type-B"),
]


def _add_usb_type(query: str, result: ParsedQuery, detected: dict[str, Any]) -> None:
    """"USB-A receptacle" searched every USB connector (USB-C ones first, by stock)."""
    for pattern, connector_type in _USB_TYPES:
        if pattern.search(query):
            result.spec_filters.append(SpecFilter("Connector Type", "=", connector_type))
            detected.setdefault("semantic", []).append(f"usb {connector_type.lower()} (-> Connector Type={connector_type})")
            return


# Coax connectors list "RF Series": SMA, RP-SMA, BNC, IPEX (U.FL), MCX, MMCX, N Type, F Type, FAKRA
_RF_SERIES = [
    (re.compile(r"\brp[- ]?sma\b", re.IGNORECASE), "RP-SMA"),
    (re.compile(r"\bsma\b", re.IGNORECASE), "SMA"),
    (re.compile(r"\b(?:u\.?fl|ipex|ipx)\b", re.IGNORECASE), "IPEX"),
    (re.compile(r"\bmmcx\b", re.IGNORECASE), "MMCX"),
    (re.compile(r"\bmcx\b", re.IGNORECASE), "MCX"),
    (re.compile(r"\bbnc\b", re.IGNORECASE), "BNC"),
    (re.compile(r"\bfakra\b", re.IGNORECASE), "FAKRA"),
    (re.compile(r"\bn[- ]?type\b", re.IGNORECASE), "N Type"),
    (re.compile(r"\bf[- ]?type\b", re.IGNORECASE), "F Type"),
]


def _add_rf_series(query: str, result: ParsedQuery, detected: dict[str, Any]) -> None:
    """"SMA connector ..." picked coax connectors but not the series, so U.FL ones came first."""
    for pattern, series in _RF_SERIES:
        if pattern.search(query):
            result.spec_filters.append(SpecFilter("RF Series", "=", series))
            detected.setdefault("semantic", []).append(f"{series} (-> RF Series={series})")
            return


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
