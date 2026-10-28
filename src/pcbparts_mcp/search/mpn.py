"""MPN (Manufacturer Part Number) normalization and detection.

This module handles MPN-related logic for search retry when the original query
returns no results. It's separate from query resolvers because MPN normalization
is a fallback behavior, not input transformation.
"""

import re
from dataclasses import dataclass
from functools import lru_cache


# Keep this expression identical in the build index and lookup predicates. In
# particular, decimal points and +/#/,/: carry ordering-code information.
MPN_KEY_SQL = "REPLACE(REPLACE(REPLACE(REPLACE(UPPER(mpn), '-', ''), ' ', ''), '_', ''), '/', '')"

LCSC_CODE = re.compile(r"C\d+", re.IGNORECASE)

# BOM entries for a part that isn't fitted or isn't chosen yet, compared without
# punctuation or case. Full-text search found JST ...-N-A connectors for "N/A".
_PLACEHOLDER_MPNS = frozenset({
    "", "na", "nc", "nf", "np", "dnp", "dnf", "dni", "dnl", "dns", "nofit", "notfitted",
    "nopop", "notpopulated", "donotpopulate", "donotfit", "notused", "tbd", "tba", "none", "null",
})


def is_placeholder_mpn(mpn: str) -> bool:
    """True for BOM placeholders such as N/A, DNP or TBD, which name no part."""
    return re.sub(r"[^0-9a-z]", "", mpn.casefold()) in _PLACEHOLDER_MPNS


_MAKER_SUFFIX = re.compile(r".+\(([A-Za-z]{2,})\)")
# Lead-free, tin plating and reel codes, which could otherwise spell a maker's initials.
_PACKING_TAGS = frozenset({"lf", "sn", "tr", "pbf", "rl"})


def is_maker_suffixed(part: dict) -> bool:
    """True when the MPN ends in its maker's name or initials, in order from the first letter:
    ICM-42688-P(TOKMAS) is Tokmas's, SP3485EEN(UMW) UMW's and TP4054(LX) lingxingic's part
    numbered after another maker's original."""
    suffix = _MAKER_SUFFIX.fullmatch(part.get("model") or "")
    maker = re.sub(r"[^a-z]", "", (part.get("manufacturer") or "").casefold())
    if not suffix or (tag := suffix[1].casefold()) in _PACKING_TAGS or not maker.startswith(tag[0]):
        return False
    letters = iter(maker)
    return all(letter in letters for letter in tag)


def mpn_key(mpn: str) -> str:
    """SQLite-compatible ASCII case folding and separator removal."""
    return mpn.translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "- _/"))


MPN_MATCH_NAMES = ("full", "same_suffix", "family")


@lru_cache(maxsize=256)
def _match_parts(part_number: str) -> tuple[str, tuple[str, ...]]:
    return mpn_key(part_number), tuple(re.split(r"[-/_\s]+", part_number.upper()))


def mpn_match_rank(mpn: str, part_number: str) -> int:
    """Rank a full ordering-code prefix, a preserved base/suffix, then family hits.

    Only a digit-ending base permits inserted letters (LM1117IMPX); later
    requested segments must occur whole, preserving voltage/package variants.
    """
    key, requested = _match_parts(part_number)
    if mpn_key(mpn or "").startswith(key):
        return 0
    segments = re.split(r"[-/_\s]+", (mpn or "").upper())
    base = requested[0]
    same_base = segments[0] == base or (
        base[-1:].isdigit() and re.fullmatch(re.escape(base) + r"[A-Z]+", segments[0]) is not None
    )
    if same_base and set(requested[1:]).issubset(segments[1:]):
        return 1
    return 2


@dataclass(frozen=True)
class PackingRule:
    """A vendor's packing codes around an otherwise unchanged device identity.

    `base` is also an indexed lookup prefix; `tail`, when present, preserves
    the value or automotive qualification after an embedded reel code.
    """

    manufacturers: tuple[str, ...]
    pattern: re.Pattern[str]

    def identity(self, match: re.Match[str]) -> str:
        return match['base'] + (match.groupdict().get('tail') or '')


PACKING_RULES = tuple(PackingRule(vendors, re.compile(pattern)) for vendors, pattern in [
    (("Analog Devices",), r"(?P<base>AD[A-Z]*\d[A-Z0-9]*?)(?:REEL7|REEL|R7)?"),
    (("Analog Devices",), r"(?P<base>LTC?\d[A-Z0-9]*)#(?:TR)?PBF"),
    (("Texas Instruments",), r"(?P<base>[A-Z]+\d[A-Z0-9]*[A-Z]{2})[RT](?P<tail>Q1)?(?:G4|E6)?"),
    (("Texas Instruments",), r"(?P<base>ISO7741FQDWW)[RT]?(?P<tail>Q1)"),
    (("Texas Instruments",), r"(?P<base>[A-Z]+\d[A-Z0-9]*?)(?:G4|E6)?"),
    (("Murata Electronics",), r"(?P<base>(?:GRM|GCM|GRJ|GRT)[A-Z0-9]{14})[DJKL]"),
    (("KEMET",), r"(?P<base>C\d{4}C[A-Z0-9]+RAC)(?:TU|TM|7800|7867)"),
    (("Infineon Technologies",), r"(?P<base>[A-Z]+\d[A-Z0-9]*?)H(?:6327|6433)(?:XTSA1|ATMA1|FTSA1|XTMA1)?"),
    (("Infineon Technologies",), r"(?P<base>[A-Z]+\d[A-Z0-9]*?)(?:XTSA1|ATMA1|FTSA1|XTMA1)?"),
    (("Nexperia", "NXP Semicon"), r"(?P<base>[A-Z]+\d[A-Z0-9]*)(?:,(?:115|118|125|135|215|218|225|235|315))?"),
    (("YAGEO",), r"(?P<base>(?:RC|AC)\d{4}[A-Z]{2}|YC\d{3}[A-Z]{2})(?:07|10|13)(?P<tail>[A-Z0-9]+)"),
    (("Winbond Elec", "Micron Tech"), r"(?P<base>(?:W25|MT\d)[A-Z0-9:]+?)(?:TR)?"),
    (("Microchip Tech",), r"(?P<base>ATSAM[A-Z0-9]+AF)T?"),
    (("Microchip Tech",), r"(?P<base>LAN8710A[A-Z]{3})(?:TR)?(?P<tail>ABC)"),
    (("SMC(Sangdest Microelectronicstronic (Nanjing))",), r"(?P<base>DSS\d+U)(?:TR)?"),
    (("Lattice",), r"(?P<base>ICE40[A-Z0-9]+[CI])(?:TR)?"),
    (("RENESAS",), r"(?P<base>ISL\d+[A-Z]+?)(?:T7A)?"),
    (("OSRAM Opto Semicon",), r"(?P<base>LGL29K[A-Z0-9]+?)(?:Z)?"),
    (("onsemi",), r"(?P<base>MC\d+[A-Z]+?)(?:R2)?(?P<tail>G)"),
    (("Qorvo",), r"(?P<base>RFFC\d+)TR(?:7|13)"),
    (("Vishay Intertech",), r"(?P<base>SMBJ\d+[A-Z0-9]*M3)[IH]"),
    (("Nichicon",), r"(?P<base>URZ[A-Z0-9]+MHD)(?:1TO)?"),
    (("Diodes Incorporated",), r"(?P<base>FL\d+)(?:TR)?(?:ND)?"),
])


# Explicit ordering aliases, never a fuzzy edit or a grade substitution. Values
# name both the catalog ordering code and the manufacturers allowed to supply it.
MPN_ALIASES = {
    mpn_key(source): (target, vendors) for source, target, vendors in [
        ("ABM3B-8.0-10-1UT", "ABM3B-8.000MHZ-10-1-U-T", ("Abracon LLC",)),
        ("AMS1117-33", "AMS1117-3.3", ("Advanced Monolithic Systems",)),
        ("BGS12PN10", "BGS 12PN10 E6327", ("Infineon Technologies",)),
        ("LD1117/3.3v", "LD1117-3.3", ("UMW(Youtai Semiconductor Co., Ltd.)",)),
        ("MS5611-01BA03", "MS561101BA03-50", ("TE Connectivity",)),
        ("MS8607-02BA01", "MS860702BA01-50", ("TE Connectivity",)),
        ("SCD-41", "SCD41-D-R2", ("Sensirion",)),
        ("VL53L0X", "VL53L0CXV0DH/1", ("STMicroelectronics",)),
        ("VL53L1X", "VL53L1CXV0FY/1", ("STMicroelectronics",)),
        ("NRF24L01+", "NRF24L01P-R", ("Nordic Semicon",)),
        # Voltage-unit annotations in the alternatives corpus, preserving 3.3V.
        ("AP2112K-3.3V", "AP2112K-3.3TRG1", ("Diodes Incorporated",)),
        ("AP2127K-3.3V", "AP2127K-3.3TRG1", ("Diodes Incorporated",)),
    ]
}

# These Wurth TVS ordering codes have only a TECH PUBLIC lookalike locally.
# Apply the identity guard to newly extracted alternatives; existing full-input
# lookups retain their behavior. Numeric ordering codes cannot imply any vendor
# in general, so this is deliberately an explicit allowlist.
ALTERNATIVE_MANUFACTURERS = {
    "824032815": ("Wurth Elektronik",),
    "824031815": ("Wurth Elektronik",),
}


def annotated_mpn_candidates(query: str) -> list[str]:
    """Extract explicit alternatives and clearly delimited BOM annotations.

    Short slash suffixes and no-space parentheticals are ordering information,
    e.g. /OT, /I, /VY+, ,118 and (LF)(SN), and stay intact.
    """
    def full_mpn(value: str) -> bool:
        return (len(re.sub(r'[^A-Za-z0-9]', '', value)) >= 6
                and bool(re.search(r'[A-Za-z]', value)) and bool(re.search(r'\d', value)))

    # A parenthetical may explicitly supply a usable alternative even when the
    # parts outside it are absent. Keep that candidate after the primary choices.
    extra = re.findall(r'\bcan (?:also )?use\s+([^()]+)', query, re.I)
    cleaned = re.sub(r'\([^()]*\s[^()]*\)', '', query)
    cleaned = re.sub(r'\bor (?:similar|equivalent)\b.*', '', cleaned, flags=re.I)
    cleaned = re.sub(r'\s+if\b.*', '', cleaned, flags=re.I)
    pieces = re.split(r'\s+or\s+|;|,(?!\d{1,3}(?:\b|$))(?![^()]*\))', cleaned, flags=re.I)
    candidates = []
    for piece in pieces + extra:
        piece = re.sub(r'^\s*(?:LDO:\s*|can (?:also )?use\s+|SOFNG\s+)', '', piece, flags=re.I)
        piece = re.split(r'\s+(?:OP AMP|EEPROM|IO EXPANDER|LED DRIVER|PIN OUT|preferred|if)\b', piece, flags=re.I)[0]
        piece = re.sub(r'\s+[A-Z]{1,4}\d+$', '', piece.strip(), flags=re.I)
        prefix = re.match(r'^(?:MCU[-_]|ISO[-_]|DUAL-OPTO[-_]|GSG[-_])(.+)$', piece, re.I)
        if prefix and full_mpn(prefix[1]):
            piece = prefix[1]
        # A slash separates alternatives only if both sides are complete MPNs.
        parts = re.split(r'/(?![^/]*\))', piece)
        if len(parts) > 1 and all(full_mpn(p) for p in parts):
            choices = parts
        else:
            choices = [piece]
        for candidate in choices:
            candidate = candidate.strip()
            # Never turn a note fragment, reference or numeric suffix into an
            # FTS query (e.g. "_IPEX", "TBC", or the ",1" in an ordering code).
            alphanumeric = re.sub(r'[^A-Za-z0-9]', '', candidate)
            orderable = (bool(re.search(r'\d', candidate)) and len(alphanumeric) >= 5
                         and (bool(re.search(r'[A-Za-z]', candidate)) or len(alphanumeric) >= 6))
            if orderable and candidate != query and candidate not in candidates:
                candidates.append(candidate)
    return candidates


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
