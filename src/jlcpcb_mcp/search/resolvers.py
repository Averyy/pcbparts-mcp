"""Query synonym expansion, package resolution, and manufacturer resolution."""

import re

from ..manufacturer_aliases import KNOWN_MANUFACTURERS, MANUFACTURER_ALIASES


# =============================================================================
# Query Synonyms
# =============================================================================
# Query synonyms - expand search terms to include equivalent names
# When any term in a group is searched, all terms in that group are searched
# Format: (primary_term, [patterns]) where patterns are pre-compiled regexes
# for all terms that should map to the primary term
_SYNONYM_GROUPS: list[tuple[str, list[re.Pattern[str]]]] = [
    # Miniature coaxial connectors - all names for the same connector family
    # IPEX gives the most search results, so we map all variants to it
    ("IPEX", [
        re.compile(r"u\.fl", re.IGNORECASE),
        re.compile(r"mhf", re.IGNORECASE),
        re.compile(r"i-pex", re.IGNORECASE),
        re.compile(r"hirose u\.fl", re.IGNORECASE),
        re.compile(r"ipx", re.IGNORECASE),
    ]),
]


def expand_query_synonyms(query: str) -> str:
    """Expand query with synonyms for better search results.

    For example, searching "U.FL" will also search for "IPEX" since they're
    the same connector type with different trade names.
    """
    for primary_term, patterns in _SYNONYM_GROUPS:
        for pattern in patterns:
            if pattern.search(query):
                # Found a match - replace with primary term
                query = pattern.sub(primary_term, query)
                break  # Only replace first match per group

    return query


# Package family mappings - expand common package names to include variants
# When user searches for "SOT-23", they likely want all SOT-23 variants
PACKAGE_FAMILIES: dict[str, list[str]] = {
    # Passives - Imperial to Metric mapping
    "0402": ["0402", "1005"],
    "0603": ["0603", "1608"],
    "0805": ["0805", "2012"],
    "1206": ["1206", "3216"],
    # SOT packages - include pin count variants
    "sot-23": ["SOT-23", "SOT-23-3", "SOT-23-3L", "SOT-23(TO-236)"],
    "sot-23-5": ["SOT-23-5", "SOT-23-5L"],
    "sot-23-6": ["SOT-23-6", "SOT-23-6L"],
    "sot-223": ["SOT-223", "SOT-223-3", "SOT-223-3L", "SOT-223-4"],
    "sot-89": ["SOT-89", "SOT-89-3", "SOT-89-3L"],
    # TO packages
    "to-252": ["TO-252", "TO-252-2", "TO-252-2L", "DPAK"],
    "to-263": ["TO-263", "TO-263-2", "D2PAK"],
    "to-220": ["TO-220", "TO-220-3", "TO-220F", "TO-220F-3"],
    # QFN common sizes
    "qfn-16": ["QFN-16", "QFN-16-EP(3x3)", "QFN-16-EP(4x4)", "QFN-16(3x3)", "VQFN-16"],
    "qfn-24": ["QFN-24", "QFN-24-EP(4x4)", "VQFN-24", "VQFN-24-EP(4x4)"],
    "qfn-32": ["QFN-32", "QFN-32-EP(5x5)", "VQFN-32", "VQFN-32-EP(5x5)"],
}

# Standard EIA imperial chip sizes used for passives (resistors, capacitors, inductors)
# These use the format LLWW where LL=length, WW=width in hundredths of an inch
# e.g., 0603 = 0.06" x 0.03" = 1.6mm x 0.8mm
# Reference: https://www.electronics-notes.com/articles/electronic_components/surface-mount-technology-smd-smt/packages.php
IMPERIAL_CHIP_SIZES: frozenset[str] = frozenset({
    "01005", "0201", "03015", "0402", "0603", "0612", "0805", "0806",
    "1008", "1206", "1210", "1212", "1218", "1806", "1808", "1812",
    "2010", "2220", "2410", "2512", "2920", "3920", "5930",
})

# SMD metric package families for crystals, oscillators, and LEDs
# These use the format LLWW where LL=length, WW=width in tenths of a millimeter
# e.g., 3215 = 3.2mm x 1.5mm, 5032 = 5.0mm x 3.2mm
# When user searches "3215", expand to all SMD3215 variants (SMD3215-2P, etc.)
# Reference: https://resources.pcb.cadence.com/blog/2024-crystal-oscillator-package-types
SMD_PACKAGE_FAMILIES: dict[str, list[str]] = {
    "1610": ["SMD1610", "SMD1610-2P"],
    "1612": ["SMD1612-4P"],
    "2012": ["SMD2012-2P", "SMD2012-4P", "SMD2012-8P"],
    "2016": ["SMD2016", "SMD2016-2P", "SMD2016-4P", "SMD2016-6P"],
    "2520": ["SMD2520", "SMD2520-2P", "SMD2520-4P", "SMD2520-6P"],
    "2835": ["SMD2835", "SMD2835-2P", "SMD2835-3P", "SMD2835-4P", "SMD2835-6P"],
    "3014": ["SMD3014-2P"],
    "3020": ["SMD3020", "SMD3020-3P"],
    "3030": ["SMD3030", "SMD3030-2P", "SMD3030-3P", "SMD3030-4P", "SMD3030-6P", "SMD3030-7P"],
    "3215": ["SMD3215", "SMD3215-2P", "SMD3215-4P", "SMD3215-8P"],
    "3225": ["SMD3225", "SMD3225-2P", "SMD3225-4P", "SMD3225-6P", "SMD3225-10P", "SMD3225-14P", "SMD-3225_4P"],
    "3528": ["SMD3528", "SMD3528-2P", "SMD3528-3P", "SMD3528-4P", "SMD3528-6P"],
    "3535": ["SMD3535", "SMD3535-2P", "SMD3535-3P", "SMD3535-4P", "SMD3535-5P", "SMD3535-6P"],
    "5032": ["SMD5032", "SMD5032-2P", "SMD5032-4P", "SMD5032-6P", "SMD-5032-4P"],
    "5050": ["SMD5050", "SMD5050-2P", "SMD5050-4P", "SMD5050-6P", "SMD5050-8P"],
    "5730": ["SMD5730", "SMD5730-3P"],
    "6035": ["SMD6035-2P", "SMD6035-4P"],
    "7050": ["SMD7050", "SMD7050-2P", "SMD7050-4P", "SMD7050-6P", "SMD7050-10P"],
    "7060": ["SMD7060", "SMD7060-2P", "SMD7060-3P"],
    "8045": ["SMD8045-2P"],
    "8080": ["SMD8080-2P", "SMD8080-3P", "SMD8080-4P", "SMD8080-5P", "SMD8080-6P"],
    "9070": ["SMD9070-8P"],
}

# Regex to detect bare 4-digit dimensions (e.g., "3215", "5032")
_BARE_DIMENSION_RE = re.compile(r"^\d{4}$")

# Build case-insensitive lookup for known manufacturers
_MANUFACTURER_LOWER_TO_EXACT: dict[str, str] = {
    name.lower(): name for name in KNOWN_MANUFACTURERS
}


def expand_package(package: str) -> list[str]:
    """Expand package name to include family variants.

    Examples:
        "SOT-23" -> ["SOT-23", "SOT-23-3", "SOT-23-3L", "SOT-23(TO-236)"]
        "0603" -> ["0603", "1608"]
        "3215" -> ["SMD3215", "SMD3215-2P", "SMD3215-4P", "SMD3215-8P"]
        "SMD3215" -> ["SMD3215", "SMD3215-2P", "SMD3215-4P", "SMD3215-8P"]
        "QFN-24-EP(4x4)" -> ["QFN-24-EP(4x4)"]  # Specific, no expansion
    """
    pkg_lower = package.lower()

    # Check if this is a known package family (SOT-23, 0603, etc.)
    if pkg_lower in PACKAGE_FAMILIES:
        return PACKAGE_FAMILIES[pkg_lower]

    # Check for bare 4-digit SMD metric dimensions (crystals, oscillators, LEDs)
    # e.g., "3215" -> expand to SMD3215 variants
    if _BARE_DIMENSION_RE.match(package) and package not in IMPERIAL_CHIP_SIZES:
        if package in SMD_PACKAGE_FAMILIES:
            return SMD_PACKAGE_FAMILIES[package]

    # Check for explicit SMD prefix: "SMD3215" or "smd-3215" -> expand to variants
    smd_match = re.match(r"^smd-?(\d{4,5})(?:-\d+p)?$", pkg_lower)
    if smd_match:
        dim = smd_match.group(1)
        if dim in SMD_PACKAGE_FAMILIES:
            return SMD_PACKAGE_FAMILIES[dim]

    # No expansion - return as-is
    return [package]


def resolve_manufacturer(name: str) -> str:
    """Resolve manufacturer alias to canonical name.

    Examples:
        "TI" -> "Texas Instruments"
        "texas instruments" -> "Texas Instruments"
        "YAGEO" -> "YAGEO" (already canonical)
    """
    name_lower = name.lower()

    # Check aliases first (e.g., "ti" -> "Texas Instruments")
    if name_lower in MANUFACTURER_ALIASES:
        return MANUFACTURER_ALIASES[name_lower]

    # Check case-insensitive match against known manufacturers
    if name_lower in _MANUFACTURER_LOWER_TO_EXACT:
        return _MANUFACTURER_LOWER_TO_EXACT[name_lower]

    # Return as-is (will use case-insensitive SQL match)
    return name
