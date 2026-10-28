"""Component type and mounting type extraction for smart query parsing."""

import re

from ..subcategory_aliases import SUBCATEGORY_ALIASES, UNAVAILABLE_SUBCATEGORY_ALIASES


# Pre-sorted by length (longest first) for correct matching
_SUBCATEGORY_KEYWORDS_BY_LENGTH = sorted([*SUBCATEGORY_ALIASES, *UNAVAILABLE_SUBCATEGORY_ALIASES], key=len, reverse=True)

PD_ROLE_PATTERN = re.compile(r'\b(?:controllers?|sinks?|sources?|triggers?|receivers?|negotiat\w*)\b', re.IGNORECASE)
_PD_MARKER = re.compile(r'\b(?:pd|power[-\s]+delivery)\b', re.IGNORECASE)
_PD_INTERFACE = re.compile(r'\b(?:usb(?:[-\s]*(?:type[-\s]*)?c)?|type[-\s]*c)\b', re.IGNORECASE)


def extract_component_type(query: str, *, memory_is_spec: bool = False) -> tuple[str | None, str, str | None]:
    """Extract component type from query.

    Args:
        query: The search query string

    Returns:
        Tuple of (subcategory_name, remaining_query, matched_keyword)
    """
    # A requested PD controller role wins over the connector/interface spelling.
    # Bare PD is ambiguous; require a role rather than adding a global PD alias.
    if _PD_MARKER.search(query) and PD_ROLE_PATTERN.search(query):
        remaining = _PD_INTERFACE.sub(' ', _PD_MARKER.sub(' ', query))
        return "usb pd", re.sub(r'\s+', ' ', remaining).strip(), "usb pd"

    # A BOM's D reference describes an LED as a diode. Preserve the more specific
    # LED keyword (including RGB/IR variants) instead of letting the longer word win.
    if re.search(r'\bleds?\b', query, re.IGNORECASE) and re.search(r'\bdiodes?\b', query, re.IGNORECASE):
        query = re.sub(r'\bdiodes?\b', ' ', query, flags=re.IGNORECASE)
    # Likewise a RESPACK footprint is a resistor network, more specific than the R's "resistor".
    if re.search(r'\brespacks?\b', query, re.IGNORECASE):
        query = re.sub(r'\bresistors?\b', ' ', query, flags=re.IGNORECASE)
    query_lower = query.lower()

    # Resettable modifiers can be separated from "fuse" by ratings or packages.
    resettable = re.compile(r'\b(?:ptc|poly\s*fuse|polyswitch|resettable)\b', re.IGNORECASE)
    if re.search(r'\bfuses?\b', query_lower) and resettable.search(query_lower):
        remaining = resettable.sub(' ', query)
        remaining = re.sub(r'\bfuses?\b', ' ', remaining, flags=re.IGNORECASE)
        return "resettable fuses", re.sub(r'\s+', ' ', remaining).strip(), "resettable fuse"

    for keyword in _SUBCATEGORY_KEYWORDS_BY_LENGTH:
        # A controller without PD is not enough to infer a Type-C connector.
        if keyword in ("usb c", "usbc", "type c", "typec") and re.search(r'\b(?:pd|controller)\b', query_lower):
            continue
        if memory_is_spec and keyword in ("flash", "nor flash", "nand", "nand flash", "sram", "psram"):
            continue
        # Use word boundaries to avoid "sram" matching inside "PSRAM"
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        if pattern.search(query_lower):
            # Remove the keyword from query
            remaining = pattern.sub('', query).strip()
            remaining = re.sub(r'\s+', ' ', remaining)
            return (SUBCATEGORY_ALIASES.get(keyword) or UNAVAILABLE_SUBCATEGORY_ALIASES[keyword]), remaining, keyword

    return None, query, None


# Mounting type patterns: PTH/THT -> Through Hole, SMD/SMT -> SMD
_MOUNTING_TYPE_PATTERNS = [
    (re.compile(r'\b(PTH|THT|through[- ]?hole|leaded)\b', re.IGNORECASE), "Through Hole"),
    (re.compile(r'\b(SMD|SMT|surface[- ]?mount)\b', re.IGNORECASE), "SMD"),
]


def extract_mounting_type(query: str) -> tuple[str | None, str]:
    """Extract mounting type from query.

    Args:
        query: The search query string

    Returns:
        Tuple of (mounting_type, remaining_query)
        Where mounting_type is "SMD" or "Through Hole" or None.
    """
    for pattern, mount_type in _MOUNTING_TYPE_PATTERNS:
        match = pattern.search(query)
        if match:
            remaining = query[:match.start()] + query[match.end():]
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            return mount_type, remaining
    return None, query
