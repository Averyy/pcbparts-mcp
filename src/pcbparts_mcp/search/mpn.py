"""MPN (Manufacturer Part Number) normalization and detection.

This module handles MPN-related logic for search retry when the original query
returns no results. It's separate from query resolvers because MPN normalization
is a fallback behavior, not input transformation.
"""

import re


# =============================================================================
# MPN Suffix Handling
# =============================================================================
# Common packaging/ordering suffixes that distributors add but aren't in BOMs
# These are stripped when searching to improve match rates

# Suffixes to strip from the END of a part number (all uppercase)
MPN_TRAILING_SUFFIXES = [
    "-TR",      # Tape & Reel
    "/TR",      # Tape & Reel (alternate format)
    "-T",       # Tape
    "-CT",      # Cut Tape
    "-ND",      # Digi-Key ordering suffix
    "-DK",      # Digi-Key ordering suffix
    "#PBF",     # Lead-free (Pb-free)
    "-PBF",     # Lead-free
    "#PBFREE",  # Lead-free
    "-PBFREE",  # Lead-free
    "+T",       # Tape (some manufacturers)
    "+TR",      # Tape & Reel (some manufacturers)
]

# Pattern to detect part numbers where "T" is inserted before the variant suffix
# e.g., MCP73831-2ACI/MC -> MCP73831T-2ACI/MC (Microchip tape & reel convention)
# Pattern: letters + numbers + optional letter + "-" + variant
_MPN_INSERT_T_PATTERN = re.compile(
    r'^([A-Z]{2,5}\d{2,5})(-[A-Z0-9/]+)$',
    re.IGNORECASE
)


def normalize_mpn(query: str) -> list[str]:
    """Generate normalized variants of an MPN query for better matching.

    Returns a list of query variants to try, in order of preference:
    1. Original query (always first)
    2. With trailing suffixes stripped
    3. With "T" inserted (for tape & reel variants)

    All variants are returned in consistent case (original case for first,
    uppercase for generated variants).

    Examples:
        "MCP73831-2ACI/MC" -> ["MCP73831-2ACI/MC", "MCP73831T-2ACI/MC"]
        "STM32F103C8T6-TR" -> ["STM32F103C8T6-TR", "STM32F103C8T6"]
        "LM1117-3.3" -> ["LM1117-3.3"] (no changes needed)
    """
    variants = [query]  # Original always first
    seen_upper: set[str] = {query.upper()}  # Track seen variants case-insensitively
    working = query.upper()

    # Strip trailing suffixes
    stripped = working
    for suffix in MPN_TRAILING_SUFFIXES:
        if stripped.endswith(suffix):
            stripped = stripped[:-len(suffix)]
            break  # Only strip one suffix

    if stripped.upper() not in seen_upper:
        variants.append(stripped)
        seen_upper.add(stripped.upper())

    # Try inserting "T" for tape & reel variant (Microchip convention)
    # MCP73831-2ACI/MC -> MCP73831T-2ACI/MC
    match = _MPN_INSERT_T_PATTERN.match(working)
    if match:
        base = match.group(1)
        suffix = match.group(2)
        # Only if base doesn't already end with T
        if not base.endswith('T'):
            with_t = f"{base}T{suffix}"
            if with_t.upper() not in seen_upper:
                variants.append(with_t)
                seen_upper.add(with_t.upper())

    # Also try with stripped version + T insertion
    match = _MPN_INSERT_T_PATTERN.match(stripped)
    if match:
        base = match.group(1)
        suffix = match.group(2)
        if not base.endswith('T'):
            with_t = f"{base}T{suffix}"
            if with_t.upper() not in seen_upper:
                variants.append(with_t)
                seen_upper.add(with_t.upper())

    return variants


def looks_like_mpn(query: str) -> bool:
    """Check if a query looks like a manufacturer part number.

    MPNs typically have:
    - Mix of letters and numbers
    - Often have dashes or slashes
    - Length typically 5-30 characters
    """
    if not query or len(query) < 4 or len(query) > 40:
        return False

    # Must have both letters and numbers
    has_letter = any(c.isalpha() for c in query)
    has_digit = any(c.isdigit() for c in query)

    if not (has_letter and has_digit):
        return False

    # Common MPN patterns
    # Alphanumeric starting with letters (IC style): STM32, MCP73831, etc.
    if re.match(r'^[A-Z]{1,5}\d{2,}', query, re.IGNORECASE):
        return True

    # Digit-starting with letters (diode style): 1N4148, 2N2222, etc.
    if re.match(r'^\d[A-Z]\d{3,}', query, re.IGNORECASE):
        return True

    # Has a dash or slash separator (common in MPNs)
    if '-' in query or '/' in query:
        return True

    return False
