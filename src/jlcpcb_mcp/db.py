"""Database module for parametric component search.

Provides SQL-based search with attribute filtering that's impossible with the API:
- Range queries: "Vgs(th) < 2.5V", "Capacitance >= 10uF"
- Multi-attribute: "N-channel MOSFET with Id >= 5A AND Rds(on) < 50mΩ"

The database is built from scraped JSONL data on first use.
"""

import json
import logging
import os
import re
import sqlite3
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .alternatives import SPEC_PARSERS
from .manufacturer_aliases import KNOWN_MANUFACTURERS, MANUFACTURER_ALIASES
from .mounting import detect_mounting_type
from .parsers import (
    parse_resistance,
    parse_capacitance,
    parse_inductance,
    parse_voltage,
    parse_current,
    parse_tolerance,
    parse_power,
    parse_frequency,
    parse_ppm,
)
from .subcategory_aliases import (
    SUBCATEGORY_ALIASES,
    resolve_subcategory_name as _resolve_subcategory_name,
    find_similar_subcategories as _find_similar_subcategories,
)

logger = logging.getLogger(__name__)

# Pre-sorted subcategory aliases keys by length (longest first)
# Sorted once at module load for O(1) access instead of sorting per query
_SUBCATEGORY_KEYWORDS_BY_LENGTH = sorted(SUBCATEGORY_ALIASES.keys(), key=len, reverse=True)


# =============================================================================
# SPEC TO COLUMN MAPPING
# =============================================================================
# Maps spec filter names (and aliases) to pre-computed database columns.
# When a spec filter matches a column, we use SQL numeric queries instead of
# LIKE patterns on JSON, which is much faster and uses indexes.
#
# Format: spec_name -> (column_name, parser_function)

SPEC_TO_COLUMN: dict[str, tuple[str, Any]] = {
    # Passives - Resistance
    "Resistance": ("resistance_ohms", parse_resistance),

    # Passives - Capacitance
    "Capacitance": ("capacitance_f", parse_capacitance),

    # Passives - Inductance
    "Inductance": ("inductance_h", parse_inductance),
    "DC Resistance(DCR)": ("dcr_ohms", parse_resistance),
    "DCR": ("dcr_ohms", parse_resistance),
    "Current - Saturation(Isat)": ("isat_a", parse_current),
    "Current - Saturation (Isat)": ("isat_a", parse_current),
    "Isat": ("isat_a", parse_current),

    # Voltage
    "Voltage Rating": ("voltage_max_v", parse_voltage),
    "Voltage": ("voltage_max_v", parse_voltage),

    # Current
    "Current Rating": ("current_max_a", parse_current),

    # Tolerance
    "Tolerance": ("tolerance_pct", parse_tolerance),

    # Power
    "Power(Watts)": ("power_w", parse_power),
    "Power": ("power_w", parse_power),
    "Pd - Power Dissipation": ("power_w", parse_power),

    # MOSFETs
    "Drain to Source Voltage": ("vds_max_v", parse_voltage),
    "Vds": ("vds_max_v", parse_voltage),
    "Current - Continuous Drain(Id)": ("id_max_a", parse_current),
    "Id": ("id_max_a", parse_current),
    "RDS(on)": ("rds_on_ohms", parse_resistance),
    "Rds(on)": ("rds_on_ohms", parse_resistance),

    # Diodes
    "Voltage - DC Reverse(Vr)": ("vr_max_v", parse_voltage),
    "Vr": ("vr_max_v", parse_voltage),
    "Current - Rectified": ("if_max_a", parse_current),
    "If": ("if_max_a", parse_current),
    "Voltage - Forward(Vf@If)": ("vf_v", parse_voltage),
    "Vf": ("vf_v", parse_voltage),

    # Voltage Regulators
    "Output Voltage": ("vout_v", parse_voltage),
    "Vout": ("vout_v", parse_voltage),
    "Output Current": ("iout_max_a", parse_current),
    "Iout": ("iout_max_a", parse_current),
    "Voltage Dropout": ("vdropout_v", parse_voltage),
    "Quiescent Current(Iq)": ("iq_ua", parse_current),
    "Quiescent Current": ("iq_ua", parse_current),

    # ADC/DAC
    "Sampling Rate": ("sample_rate_hz", parse_frequency),

    # Crystals
    "Load Capacitance": ("load_capacitance_pf", parse_capacitance),
    "Frequency Stability": ("freq_tolerance_ppm", parse_ppm),

    # Op-Amps
    "Gain Bandwidth Product": ("gbw_hz", parse_frequency),

    # Capacitors
    "Ripple Current": ("ripple_current_a", parse_current),
    "Equivalent Series Resistance(ESR)": ("esr_ohms", parse_resistance),
    "ESR": ("esr_ohms", parse_resistance),

    # MCU
    "Flash": ("flash_size_bytes", None),  # Special: memory size parser
    "Program Memory Size": ("flash_size_bytes", None),
    "SRAM": ("ram_size_bytes", None),
    "RAM Size": ("ram_size_bytes", None),
    "Speed": ("clock_speed_hz", parse_frequency),
    "CPU Maximum Speed": ("clock_speed_hz", parse_frequency),

    # Memory ICs
    "Capacity": ("memory_capacity_bits", None),
    "Memory Size": ("memory_capacity_bits", None),

    # Battery Chargers
    "Charging Current": ("charge_current_a", parse_current),
    "Charge Current - Max": ("charge_current_a", parse_current),

    # TVS / ESD
    "Clamping Voltage": ("clamping_voltage_v", parse_voltage),
    "Reverse Stand-Off Voltage (Vrwm)": ("standoff_voltage_v", parse_voltage),
    "Peak Pulse Power(Ppk)": ("surge_power_w", parse_power),
}


# =============================================================================
# Smart Query Parsing
# =============================================================================
# Patterns for extracting values from natural language queries like "10k resistor 0603 1%"

# Resistance patterns: 10k, 100R, 4.7k, 1M, 100ohm, 10kohm
# Also supports European notation: 4k7 = 4.7kΩ, 4R7 = 4.7Ω, 1M5 = 1.5MΩ
RESISTANCE_PATTERN = re.compile(
    r'\b(\d+(?:\.\d+)?)\s*([kKmMrRΩ]|ohm|kohm|mohm)\b',
    re.IGNORECASE
)
# European notation: digit + suffix + digit (e.g., 4k7, 4R7, 1M5)
RESISTANCE_EURO_PATTERN = re.compile(
    r'\b(\d+)([kKmMrR])(\d+)\b'
)

# Capacitance patterns: 10uF, 100nF, 1pF, 4.7uF, 100pf
CAPACITANCE_PATTERN = re.compile(
    r'\b(\d+(?:\.\d+)?)\s*(u[fF]|n[fF]|p[fF]|[uμ]F|nF|pF)\b'
)

# Inductance patterns: 10uH, 100nH, 1mH, 4.7uH
INDUCTANCE_PATTERN = re.compile(
    r'\b(\d+(?:\.\d+)?)\s*(u[hH]|n[hH]|m[hH]|[uμ]H|nH|mH)\b'
)

# Voltage patterns: 25V, 50V, 100V (but not in model numbers like STM32F103)
VOLTAGE_PATTERN = re.compile(
    r'\b(\d+(?:\.\d+)?)\s*[vV]\b'
)

# Current patterns: 5A, 10A, 100mA, 500mA
CURRENT_PATTERN = re.compile(
    r'\b(\d+(?:\.\d+)?)\s*(m[aA]|[aA])\b'
)

# Tolerance patterns: 1%, 5%, 10%, 0.1%
TOLERANCE_PATTERN = re.compile(
    r'\b(\d+(?:\.\d+)?)\s*%'
)

# Package patterns (common sizes)
PACKAGE_PATTERNS = [
    # Imperial sizes
    re.compile(r'\b(0201|0402|0603|0805|1206|1210|1812|2010|2512)\b'),
    # SOT packages
    re.compile(r'\b(SOT-?23(?:-[356])?|SOT-?89|SOT-?223)\b', re.IGNORECASE),
    # TO packages
    re.compile(r'\b(TO-?220[A-Z]?|TO-?252|TO-?263|TO-?92|DPAK|D2PAK)\b', re.IGNORECASE),
    # QFN/QFP
    re.compile(r'\b(QFN-?\d+|TQFP-?\d+|LQFP-?\d+|QFP-?\d+)\b', re.IGNORECASE),
    # DIP/SOP
    re.compile(r'\b(DIP-?\d+|SOP-?\d+|SOIC-?\d+|TSSOP-?\d+|MSOP-?\d+)\b', re.IGNORECASE),
]

# SUBCATEGORY_ALIASES defined below (after SpecFilter) is used for component type detection

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


@dataclass
class ParsedQuery:
    """Result of parsing a smart query string."""
    # Original query
    original: str
    # Remaining text after extracting structured parts (for FTS search)
    remaining_text: str
    # Detected subcategory (from component type keywords)
    subcategory: str | None = None
    # Extracted spec filters
    spec_filters: list["SpecFilter"] = field(default_factory=list)
    # Extracted package
    package: str | None = None
    # What was detected (for debugging/transparency)
    detected: dict[str, Any] = field(default_factory=dict)


def parse_smart_query(query: str) -> ParsedQuery:
    """Parse a natural language query into structured filters.

    Examples:
        "10k resistor 0603 1%" -> subcategory=resistor, resistance=10k, package=0603, tolerance=1%
        "100nF 25V capacitor" -> subcategory=capacitor, capacitance=100nF, voltage=25V
        "n-channel mosfet SOT-23" -> subcategory=mosfets, package=SOT-23

    Returns:
        ParsedQuery with extracted components and remaining text for FTS search.
    """
    result = ParsedQuery(original=query, remaining_text=query)
    detected: dict[str, Any] = {}
    tokens_to_remove: list[str] = []

    query_lower = query.lower()

    # 1. Detect component type (longest match first to handle "ceramic capacitor" before "capacitor")
    # Uses pre-sorted list for O(1) access instead of sorting per query
    for keyword in _SUBCATEGORY_KEYWORDS_BY_LENGTH:
        if keyword in query_lower:
            result.subcategory = SUBCATEGORY_ALIASES[keyword]
            detected["component_type"] = keyword
            tokens_to_remove.append(keyword)
            break

    # 2. Extract tolerance (do before other patterns since 1% could conflict)
    tol_match = TOLERANCE_PATTERN.search(query)
    if tol_match:
        tolerance = f"{tol_match.group(1)}%"
        result.spec_filters.append(SpecFilter("Tolerance", "=", tolerance))
        detected["tolerance"] = tolerance
        tokens_to_remove.append(tol_match.group(0))

    # 3. Extract resistance (only if likely a resistor context)
    # Try European notation first (e.g., 4k7 = 4.7kΩ, 4R7 = 4.7Ω)
    euro_res_match = RESISTANCE_EURO_PATTERN.search(query)
    res_match = RESISTANCE_PATTERN.search(query)

    if euro_res_match:
        int_part = euro_res_match.group(1)
        suffix = euro_res_match.group(2).upper()
        frac_part = euro_res_match.group(3)
        value = f"{int_part}.{frac_part}"

        if suffix == 'R':
            normalized = f"{value}Ω"
        elif suffix == 'K':
            normalized = f"{value}kΩ"
        elif suffix == 'M':
            normalized = f"{value}MΩ"
        else:
            normalized = f"{value}{suffix}"

        result.spec_filters.append(SpecFilter("Resistance", "=", normalized))
        detected["resistance"] = normalized
        tokens_to_remove.append(euro_res_match.group(0))
        if not result.subcategory:
            result.subcategory = "chip resistor - surface mount"
            detected["component_type"] = "resistor (inferred)"
    elif res_match:
        value = res_match.group(1)
        unit = res_match.group(2).upper()
        # Normalize unit
        if unit in ('R', 'Ω', 'OHM'):
            normalized = f"{value}Ω"
        elif unit in ('K', 'KOHM'):
            normalized = f"{value}kΩ"
        elif unit in ('M', 'MOHM'):
            normalized = f"{value}MΩ"
        else:
            normalized = f"{value}{unit}"

        result.spec_filters.append(SpecFilter("Resistance", "=", normalized))
        detected["resistance"] = normalized
        tokens_to_remove.append(res_match.group(0))
        # Auto-detect subcategory if not already set
        if not result.subcategory:
            result.subcategory = "chip resistor - surface mount"
            detected["component_type"] = "resistor (inferred)"

    # 4. Extract capacitance
    cap_match = CAPACITANCE_PATTERN.search(query)
    if cap_match:
        value = cap_match.group(1)
        unit = cap_match.group(2)
        # Normalize unit
        if unit.lower() in ('uf', 'μf'):
            normalized = f"{value}uF"
        elif unit.lower() == 'nf':
            normalized = f"{value}nF"
        elif unit.lower() == 'pf':
            normalized = f"{value}pF"
        else:
            normalized = f"{value}{unit}"

        result.spec_filters.append(SpecFilter("Capacitance", "=", normalized))
        detected["capacitance"] = normalized
        tokens_to_remove.append(cap_match.group(0))
        # Auto-detect subcategory if not already set
        if not result.subcategory:
            result.subcategory = "multilayer ceramic capacitors mlcc - smd/smt"
            detected["component_type"] = "capacitor (inferred)"

    # 5. Extract inductance
    ind_match = INDUCTANCE_PATTERN.search(query)
    if ind_match:
        value = ind_match.group(1)
        unit = ind_match.group(2)
        if unit.lower() in ('uh', 'μh'):
            normalized = f"{value}uH"
        elif unit.lower() == 'nh':
            normalized = f"{value}nH"
        elif unit.lower() == 'mh':
            normalized = f"{value}mH"
        else:
            normalized = f"{value}{unit}"

        result.spec_filters.append(SpecFilter("Inductance", "=", normalized))
        detected["inductance"] = normalized
        tokens_to_remove.append(ind_match.group(0))
        # Auto-detect subcategory
        if not result.subcategory:
            result.subcategory = "inductors (smd)"
            detected["component_type"] = "inductor (inferred)"

    # 6. Extract voltage (common for capacitors, diodes, MOSFETs)
    volt_match = VOLTAGE_PATTERN.search(query)
    if volt_match:
        voltage = f"{volt_match.group(1)}V"
        result.spec_filters.append(SpecFilter("Voltage", ">=", voltage))
        detected["voltage"] = voltage
        tokens_to_remove.append(volt_match.group(0))

    # 7. Extract current
    curr_match = CURRENT_PATTERN.search(query)
    if curr_match:
        value = curr_match.group(1)
        unit = curr_match.group(2).upper()
        if unit == 'MA':
            normalized = f"{value}mA"
        else:
            normalized = f"{value}A"
        # Use Id for MOSFETs, If for diodes, generic otherwise
        spec_name = "Id" if result.subcategory == "mosfets" else "If"
        result.spec_filters.append(SpecFilter(spec_name, ">=", normalized))
        detected["current"] = normalized
        tokens_to_remove.append(curr_match.group(0))

    # 8. Extract package
    for pkg_pattern in PACKAGE_PATTERNS:
        pkg_match = pkg_pattern.search(query)
        if pkg_match:
            result.package = pkg_match.group(1).upper()
            detected["package"] = result.package
            tokens_to_remove.append(pkg_match.group(0))
            break

    # 9. Build remaining text (remove extracted tokens)
    remaining = query
    for token in tokens_to_remove:
        # Case-insensitive removal
        remaining = re.sub(re.escape(token), '', remaining, flags=re.IGNORECASE)
    # Clean up whitespace
    remaining = ' '.join(remaining.split())
    result.remaining_text = remaining
    result.detected = detected

    return result

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

# Build case-insensitive lookup for known manufacturers
_MANUFACTURER_LOWER_TO_EXACT: dict[str, str] = {
    name.lower(): name for name in KNOWN_MANUFACTURERS
}

# Database paths - configurable via environment variables
_PACKAGE_DATA_DIR = Path(__file__).parent.parent.parent / "data"
DEFAULT_DATA_DIR = Path(os.environ.get("JLCPCB_DATA_DIR", str(_PACKAGE_DATA_DIR)))
DEFAULT_DB_PATH = Path(os.environ.get("JLCPCB_DB_PATH", str(DEFAULT_DATA_DIR / "components.db")))


def _escape_like(value: str) -> str:
    """Escape SQL LIKE wildcards (%, _) in user input.

    Uses backslash as the escape character, which must be specified
    in the LIKE clause with ESCAPE '\\'.
    """
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _is_integer(value: float, tol: float = 1e-9) -> bool:
    """Check if a float value is effectively an integer.

    Args:
        value: The float to check
        tol: Tolerance for floating point comparison

    Returns:
        True if value is within tolerance of its rounded value
    """
    return abs(value - round(value)) < tol


def generate_value_patterns(spec_name: str, value: str, parsed_value: float | None) -> list[str]:
    """Generate SQL LIKE patterns that match the actual spec value in JSON.

    For Resistance="82k", generates patterns like:
    - '%"Resistance", "82k%'   (matches "82kΩ", "82kohm")
    - '%"Resistance", "82K%'   (case variant)

    NOTE: Most numeric specs now use pre-computed columns via SPEC_TO_COLUMN,
    which is faster than LIKE patterns. This function is used as a fallback
    for specs without dedicated columns.

    Args:
        spec_name: Attribute name (e.g., "Resistance")
        value: User-provided value (e.g., "82k")
        parsed_value: Numeric value in base units (e.g., 82000)

    Returns:
        List of SQL LIKE patterns (limit 3 per attribute for query efficiency)
    """
    if parsed_value is None:
        return []

    name_escaped = _escape_like(spec_name)

    # Generate only the most likely patterns (limit to 3 for SQL efficiency)
    # Post-filtering will handle edge cases
    value_escaped = _escape_like(value.rstrip("ΩωOHMohm"))

    # Primary pattern: user's input as-is
    patterns = [f'%"{name_escaped}", "{value_escaped}%']

    # Secondary pattern: opposite case for the suffix (k/K, m/M)
    value_lower = value_escaped.lower()
    value_upper = value_escaped.upper()
    if value_lower != value_upper:
        # Add the opposite case variant
        if value_escaped == value_lower:
            patterns.append(f'%"{name_escaped}", "{value_upper}%')
        else:
            patterns.append(f'%"{name_escaped}", "{value_lower}%')

    # Tertiary pattern: normalized value (for edge cases)
    spec_name_lower = spec_name.lower()
    if "resistance" in spec_name_lower and parsed_value >= 1000:
        k_val = parsed_value / 1000
        if _is_integer(k_val):
            patterns.append(f'%"{name_escaped}", "{int(round(k_val))}k%')
    elif "capacitance" in spec_name_lower:
        uf = parsed_value * 1e6
        if uf >= 1:
            if _is_integer(uf):
                patterns.append(f'%"{name_escaped}", "{int(round(uf))}u%')
    elif "tolerance" in spec_name_lower:
        # Tolerance uses ± prefix
        pct = parsed_value
        if _is_integer(pct):
            patterns.append(f'%"{name_escaped}", "\\\\u00b1{int(round(pct))}\\%%')

    return patterns[:3]  # Limit to 3 patterns max


# REMOVED: Old verbose pattern generation - the above is sufficient
# with post-filtering handling edge cases. Most specs now use
# pre-computed columns (SPEC_TO_COLUMN) which bypasses this entirely.


@dataclass
class SpecFilter:
    """Filter for a component specification/attribute.

    Examples:
        SpecFilter("Capacitance", ">=", "10uF")
        SpecFilter("Voltage Rating", "<=", "50V")
        SpecFilter("Resistance", "=", "10k")
        SpecFilter("Type", "=", "N-Channel")
    """
    name: str
    operator: Literal["=", ">=", "<=", ">", "<", "!="]
    value: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "op": self.operator, "value": self.value}


# Use SPEC_PARSERS from alternatives.py as the source of truth
# This mapping has all attribute names and their parser functions

# Attribute name aliases - maps user-friendly names to actual DB attribute names
# This allows users to use short names like "Vgs(th)" instead of "Gate Threshold Voltage (Vgs(th))"
ATTRIBUTE_ALIASES: dict[str, list[str]] = {
    # MOSFETs
    "Vgs(th)": ["Gate Threshold Voltage (Vgs(th))", "Gate Threshold Voltage"],
    "Vds": ["Drain to Source Voltage"],
    "Id": ["Current - Continuous Drain(Id)"],
    "Rds(on)": ["RDS(on)"],

    # Diodes
    "Vr": ["Voltage - DC Reverse(Vr)"],
    "If": ["Current - Rectified"],
    "Vf": ["Voltage - Forward(Vf@If)"],

    # Passives
    "Capacitance": ["Capacitance"],
    "Voltage": ["Voltage Rating"],
    "Tolerance": ["Tolerance"],
    "Power": ["Power(Watts)", "Pd - Power Dissipation"],
    "Resistance": ["Resistance"],
    "Inductance": ["Inductance"],
    "DCR": ["DC Resistance(DCR)"],
    "Isat": ["Current - Saturation(Isat)", "Current - Saturation (Isat)"],

    # Timing
    "Frequency": ["Frequency"],

    # BJTs
    "Vceo": ["Collector - Emitter Voltage VCEO"],
    "Ic": ["Current - Collector(Ic)"],

    # LDOs/Regulators
    "Vout": ["Output Voltage"],
    "Iout": ["Output Current"],
}

# Reverse lookup: full attribute name -> list of aliases
# Built once at module load for O(1) lookup instead of O(n) iteration
_ATTR_FULL_TO_ALIASES: dict[str, list[str]] = {}
for _alias, _full_names in ATTRIBUTE_ALIASES.items():
    for _full_name in _full_names:
        if _full_name not in _ATTR_FULL_TO_ALIASES:
            _ATTR_FULL_TO_ALIASES[_full_name] = []
        _ATTR_FULL_TO_ALIASES[_full_name].append(_alias)


# SUBCATEGORY_ALIASES is imported from subcategory_aliases.py


class ComponentDatabase:
    """SQLite database for parametric component search.

    Thread safety: Uses WAL mode + check_same_thread=False.
    Concurrent reads are safe; writes are serialized by SQLite.
    The _conn_lock protects lazy initialization of the connection.
    """

    def __init__(self, db_path: Path | None = None, data_dir: Path | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        self._conn: sqlite3.Connection | None = None
        self._conn_lock = threading.Lock()  # Protects _conn initialization
        self._subcategories: dict[int, dict[str, Any]] = {}  # id -> {name, category_id, category_name}
        self._categories: dict[int, dict[str, Any]] = {}  # id -> {name, slug}
        # Reverse lookups for name -> id resolution
        self._subcategory_name_to_id: dict[str, int] = {}  # lowercase name -> id
        self._category_name_to_id: dict[str, int] = {}  # lowercase name -> id

    def _ensure_db(self) -> None:
        """Ensure database exists, build if missing. Thread-safe."""
        if self._conn is not None:
            return

        with self._conn_lock:
            # Double-check after acquiring lock
            if self._conn is not None:
                return

            if not self.db_path.exists():
                # Ensure parent directory exists
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Database not found at {self.db_path}, building...")
                self._build_database()

            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row

            # Load subcategory cache
            self._load_caches()

    def _build_database(self) -> None:
        """Build the database from scraped data."""
        import importlib.util
        script_path = Path(__file__).parent.parent.parent / "scripts" / "build_database.py"

        # Validate script path exists
        if not script_path.exists():
            raise FileNotFoundError(
                f"Build script not found: {script_path}\n"
                f"The build_database.py script is required to create the component database."
            )

        # Load the build script module
        try:
            spec = importlib.util.spec_from_file_location("build_database", script_path)
            if spec is None or spec.loader is None:
                raise ImportError(
                    f"Cannot create module spec for {script_path}\n"
                    f"The script may have syntax errors or missing dependencies."
                )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except SyntaxError as e:
            logger.error(f"Syntax error in build script: {e}")
            raise ImportError(f"Syntax error in {script_path}: {e}") from e
        except ImportError as e:
            logger.error(f"Failed to load build script: {e}")
            raise

        # Execute the build function
        try:
            if not hasattr(module, "build_database"):
                raise AttributeError(
                    f"build_database function not found in {script_path}\n"
                    f"The script must define a build_database(data_dir, output, verbose) function."
                )
            module.build_database(self.data_dir, self.db_path, verbose=True)
        except Exception as e:
            logger.error(f"Database build failed: {e}")
            raise RuntimeError(
                f"Failed to build database from {self.data_dir}: {e}\n"
                f"Check that the data directory contains valid component data files."
            ) from e

    def _load_caches(self) -> None:
        """Load subcategory and category caches with reverse name lookups."""
        if not self._conn:
            return

        # Load subcategories
        for row in self._conn.execute("SELECT * FROM subcategories"):
            self._subcategories[row["id"]] = {
                "name": row["name"],
                "category_id": row["category_id"],
                "category_name": row["category_name"],
            }
            # Build reverse lookup (lowercase for case-insensitive matching)
            self._subcategory_name_to_id[row["name"].lower()] = row["id"]

        # Load categories
        for row in self._conn.execute("SELECT * FROM categories"):
            self._categories[row["id"]] = {
                "name": row["name"],
                "slug": row["slug"],
            }
            # Build reverse lookup
            self._category_name_to_id[row["name"].lower()] = row["id"]

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _get_attribute_names(self, name: str) -> list[str]:
        """Get all possible attribute names for a given name (including aliases)."""
        # Check if this is an alias (e.g., "Vds" -> ["Drain to Source Voltage"])
        if name in ATTRIBUTE_ALIASES:
            return ATTRIBUTE_ALIASES[name]
        # Check if this is already a full attribute name (has parser)
        if name in SPEC_PARSERS:
            return [name]
        # Check if this full name maps to any aliases using O(1) reverse lookup
        if name in _ATTR_FULL_TO_ALIASES:
            # Get all names in the alias group
            first_alias = _ATTR_FULL_TO_ALIASES[name][0]
            return ATTRIBUTE_ALIASES[first_alias]
        # No alias found, return as-is
        return [name]

    def get_subcategory_name(self, subcategory_id: int) -> str | None:
        """Get subcategory name by ID."""
        self._ensure_db()
        subcat = self._subcategories.get(subcategory_id)
        return subcat["name"] if subcat else None

    def get_category_for_subcategory(self, subcategory_id: int) -> tuple[int, str] | None:
        """Get category (id, name) for a subcategory."""
        self._ensure_db()
        subcat = self._subcategories.get(subcategory_id)
        if subcat:
            return subcat["category_id"], subcat["category_name"]
        return None

    def resolve_subcategory_name(self, name: str) -> int | None:
        """Resolve subcategory name to ID. Case-insensitive, supports partial match.

        Matching priority:
        1. Common alias (e.g., "MLCC" -> "Multilayer Ceramic Capacitors MLCC - SMD/SMT")
        2. Exact match (e.g., "crystals" -> "crystals")
        3. Shortest containing match (e.g., "crystal" -> "crystals" not "crystal oscillators")

        Returns:
            Subcategory ID if found, None otherwise.
        """
        self._ensure_db()
        return _resolve_subcategory_name(name, self._subcategory_name_to_id)

    def resolve_category_name(self, name: str) -> int | None:
        """Resolve category name to ID. Case-insensitive, supports partial match.

        Matching priority:
        1. Exact match
        2. Shortest containing match (most specific)

        Returns:
            Category ID if found, None otherwise.
        """
        self._ensure_db()
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

    def _expand_package(self, package: str) -> list[str]:
        """Expand package name to include family variants.

        Examples:
            "SOT-23" -> ["SOT-23", "SOT-23-3", "SOT-23-3L", "SOT-23(TO-236)"]
            "0603" -> ["0603", "1608"]
            "QFN-24-EP(4x4)" -> ["QFN-24-EP(4x4)"]  # Specific, no expansion
        """
        pkg_lower = package.lower()

        # Check if this is a known package family
        if pkg_lower in PACKAGE_FAMILIES:
            return PACKAGE_FAMILIES[pkg_lower]

        # No expansion - return as-is
        return [package]

    def _resolve_manufacturer(self, name: str) -> str:
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
        """
        Search components with parametric filtering.

        Args:
            query: Text search (FTS) for lcsc, mpn, manufacturer, description
            subcategory_id: Filter by subcategory ID (takes precedence over subcategory_name)
            subcategory_name: Filter by subcategory name (case-insensitive, partial match).
                Uses shortest-match priority (e.g., "crystal" -> "crystals" not "crystal oscillators")
            category_id: Filter by category ID (takes precedence over category_name)
            category_name: Filter by category name (case-insensitive, partial match)
            spec_filters: List of SpecFilter for attribute-based filtering
            library_type: Filter by library type - "basic", "preferred", or "extended".
                None (default) means no filtering.
            prefer_no_fee: Sort preference (default True). When True, sorts results with
                basic parts first, then preferred, then extended. This is a sort order
                preference, not a filter.
            min_stock: Minimum stock quantity
            package: Package filter (exact match, single value)
            packages: Package filter (exact match, multiple values with OR logic)
            manufacturer: Manufacturer filter (exact match)
            match_all_terms: FTS matching mode (default True).
                True = AND logic: all query terms must match (e.g., "hall effect" requires both words)
                False = OR logic: any term can match (e.g., "hall effect" matches parts with either word)
                Tip: Use False for multi-word queries when AND returns too few results.
            sort_by: "stock" (default), "price", or "relevance" (requires query)
            limit: Max results (default 50)
            offset: Pagination offset

        Returns:
            {
                "results": [...],
                "total": <count matching filters>,
                "page_info": {...},
                "filters_applied": {...},
                "library_type_counts": {"basic": N, "preferred": N, "extended": N}
            }
        """
        self._ensure_db()
        if not self._conn:
            return {"error": "Database not available", "results": [], "total": 0}

        # Expand query synonyms for better search coverage
        # e.g., "U.FL" -> "IPEX" since IPEX has more indexed parts
        if query:
            query = expand_query_synonyms(query)

        # Resolve subcategory_name to ID if needed (ID takes precedence)
        resolved_subcategory_id = subcategory_id
        resolved_subcategory_display_name: str | None = None
        if subcategory_name and not subcategory_id:
            resolved_subcategory_id = self.resolve_subcategory_name(subcategory_name)
            if resolved_subcategory_id is None:
                # Find similar subcategory names to suggest
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
            # Store the actual resolved name for the response
            resolved_subcategory_display_name = self._subcategories[resolved_subcategory_id]["name"]

        # Resolve category_name to ID if needed (ID takes precedence)
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
            # Store the actual resolved name for the response
            resolved_category_display_name = self._categories[resolved_category_id]["name"]

        # Build query
        sql_parts = ["SELECT * FROM components WHERE 1=1"]
        count_parts = ["SELECT COUNT(*) FROM components WHERE 1=1"]
        params: list[Any] = []
        count_params: list[Any] = []

        # Text search via FTS
        if query:
            # Validate query length to prevent abuse
            if len(query) > 500:
                return {
                    "error": "Query too long (max 500 characters)",
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }

            # Validate query for control characters and null bytes
            # FTS5 can behave unexpectedly with these characters
            if any(ord(c) < 32 and c not in '\t\n\r' for c in query) or '\x00' in query:
                return {
                    "error": "Query contains invalid characters",
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }

            # Use FTS for text search, get matching LCSCs
            fts_sql = """
                AND lcsc IN (
                    SELECT lcsc FROM components_fts
                    WHERE components_fts MATCH ?
                )
            """
            # Build FTS5 query: tokenize, quote each term, add prefix matching
            # AND mode: "capacitor 10uF" -> '"capacitor"* "10uF"*' (both terms required)
            # OR mode: "hall effect" -> '"hall"* OR "effect"*' (either term matches)
            #
            # This handles:
            # - Multi-word queries with configurable AND/OR logic
            # - Prefix matching (10uF matches 10uF, 10uF/25V, etc.)
            # - Special characters (quoted terms are safe in FTS5)
            tokens = query.split()
            fts_parts = []
            for token in tokens:
                # Skip empty tokens
                if not token:
                    continue
                # Quote the token to escape special FTS5 characters
                # Inside double quotes, FTS5 operators (AND, OR, NOT, NEAR) are literal
                escaped = token.replace('"', '""')
                fts_parts.append(f'"{escaped}"*')

            # Handle case where all tokens were empty/filtered
            if not fts_parts:
                return {
                    "error": "Query contains no searchable terms",
                    "results": [],
                    "total": 0,
                    "library_type_counts": {"basic": 0, "preferred": 0, "extended": 0},
                    "no_fee_available": False,
                }

            # Join with space (AND) or OR based on match_all_terms
            if match_all_terms:
                fts_query = " ".join(fts_parts)  # Space = AND in FTS5
            else:
                fts_query = " OR ".join(fts_parts)  # Explicit OR

            sql_parts.append(fts_sql)
            count_parts.append(fts_sql)
            params.append(fts_query)
            count_params.append(fts_query)

        # Subcategory filter (use resolved IDs from name lookups)
        if resolved_subcategory_id:
            sql_parts.append("AND subcategory_id = ?")
            count_parts.append("AND subcategory_id = ?")
            params.append(resolved_subcategory_id)
            count_params.append(resolved_subcategory_id)
        elif resolved_category_id:
            # Get all subcategory IDs for this category
            subcat_ids = [
                sid for sid, info in self._subcategories.items()
                if info["category_id"] == resolved_category_id
            ]
            if subcat_ids:
                placeholders = ",".join("?" * len(subcat_ids))
                sql_parts.append(f"AND subcategory_id IN ({placeholders})")
                count_parts.append(f"AND subcategory_id IN ({placeholders})")
                params.extend(subcat_ids)
                count_params.extend(subcat_ids)

        # Library type filter (actual filter - use prefer_no_fee for sort preference)
        if library_type:
            if library_type == "basic":
                sql_parts.append("AND library_type = 'b'")
                count_parts.append("AND library_type = 'b'")
            elif library_type == "preferred":
                sql_parts.append("AND library_type = 'p'")
                count_parts.append("AND library_type = 'p'")
            elif library_type == "extended":
                sql_parts.append("AND library_type = 'e'")
                count_parts.append("AND library_type = 'e'")

        # Stock filter
        if min_stock > 0:
            sql_parts.append("AND stock >= ?")
            count_parts.append("AND stock >= ?")
            params.append(min_stock)
            count_params.append(min_stock)

        # Package filter (packages array takes precedence if both provided)
        # Expand package families (e.g., "SOT-23" -> ["SOT-23", "SOT-23-3", "SOT-23-3L", ...])
        expanded_packages: list[str] = []
        if packages:
            for pkg in packages:
                expanded_packages.extend(self._expand_package(pkg))
        elif package:
            expanded_packages = self._expand_package(package)

        if expanded_packages:
            placeholders = ",".join("?" * len(expanded_packages))
            sql_parts.append(f"AND package IN ({placeholders})")
            count_parts.append(f"AND package IN ({placeholders})")
            params.extend(expanded_packages)
            count_params.extend(expanded_packages)

        # Manufacturer filter (with alias resolution and case-insensitive matching)
        if manufacturer:
            resolved_manufacturer = self._resolve_manufacturer(manufacturer)
            # Use case-insensitive matching via LOWER()
            sql_parts.append("AND LOWER(manufacturer) = LOWER(?)")
            count_parts.append("AND LOWER(manufacturer) = LOWER(?)")
            params.append(resolved_manufacturer)
            count_params.append(resolved_manufacturer)

        # Spec filters (the main feature!)
        # OPTIMIZATION: Use pre-computed numeric columns when available (SPEC_TO_COLUMN)
        # This uses SQL indexes and is much faster than LIKE patterns on JSON.
        # Fall back to LIKE patterns for specs without dedicated columns.
        if spec_filters:
            for spec_filter in spec_filters:
                # Get all possible attribute names (including aliases)
                attr_names = self._get_attribute_names(spec_filter.name)

                # First, check if we have a pre-computed column for this spec
                # This is much faster than LIKE patterns on JSON
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
                            # Add 1% tolerance for = operator to handle floating point
                            if spec_filter.operator == "=":
                                tolerance = abs(parsed_value) * 0.01 if parsed_value != 0 else 1e-9
                                sql_parts.append(f"AND {column_name} BETWEEN ? AND ?")
                                count_parts.append(f"AND {column_name} BETWEEN ? AND ?")
                                params.extend([parsed_value - tolerance, parsed_value + tolerance])
                                count_params.extend([parsed_value - tolerance, parsed_value + tolerance])
                            elif spec_filter.operator == ">=":
                                sql_parts.append(f"AND {column_name} >= ?")
                                count_parts.append(f"AND {column_name} >= ?")
                                params.append(parsed_value)
                                count_params.append(parsed_value)
                            elif spec_filter.operator == "<=":
                                sql_parts.append(f"AND {column_name} <= ?")
                                count_parts.append(f"AND {column_name} <= ?")
                                params.append(parsed_value)
                                count_params.append(parsed_value)
                            elif spec_filter.operator == ">":
                                sql_parts.append(f"AND {column_name} > ?")
                                count_parts.append(f"AND {column_name} > ?")
                                params.append(parsed_value)
                                count_params.append(parsed_value)
                            elif spec_filter.operator == "<":
                                sql_parts.append(f"AND {column_name} < ?")
                                count_parts.append(f"AND {column_name} < ?")
                                params.append(parsed_value)
                                count_params.append(parsed_value)
                            continue  # Skip to next filter, we handled this one

                # Fall back to LIKE patterns for specs without pre-computed columns
                # Check if we have a parser for any of these names
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
                                count_params.append(pattern)
                        if or_conditions:
                            combined = " OR ".join(or_conditions)
                            sql_parts.append(f"AND ({combined})")
                            count_parts.append(f"AND ({combined})")
                    else:
                        # For range comparisons, check attribute exists
                        or_conditions = []
                        for name in attr_names:
                            or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                            pattern = f'%"{_escape_like(name)}"%'
                            params.append(pattern)
                            count_params.append(pattern)
                        if or_conditions:
                            combined = " OR ".join(or_conditions)
                            sql_parts.append(f"AND ({combined})")
                            count_parts.append(f"AND ({combined})")
                elif spec_filter.operator == "=":
                    # String exact value match (non-numeric) - use LIKE patterns
                    or_conditions = []
                    for name in attr_names:
                        pattern = f'%"{_escape_like(name)}", "{_escape_like(spec_filter.value)}"%'
                        or_conditions.append("attributes LIKE ? ESCAPE '\\'")
                        params.append(pattern)
                        count_params.append(pattern)
                    if or_conditions:
                        combined = " OR ".join(or_conditions)
                        sql_parts.append(f"AND ({combined})")
                        count_parts.append(f"AND ({combined})")

        # Sorting
        # When prefer_no_fee=True, prioritize: basic > preferred > extended
        # CASE returns 1 for basic, 2 for preferred, 3 for extended
        lib_type_order = "CASE library_type WHEN 'b' THEN 1 WHEN 'p' THEN 2 ELSE 3 END"

        if sort_by == "price":
            if prefer_no_fee:
                sql_parts.append(f"ORDER BY {lib_type_order}, price ASC NULLS LAST")
            else:
                sql_parts.append("ORDER BY price ASC NULLS LAST")
        elif sort_by == "relevance" and query:
            # FTS rank - simple ordering by match
            if prefer_no_fee:
                sql_parts.append(f"ORDER BY {lib_type_order}, stock DESC")
            else:
                sql_parts.append("ORDER BY stock DESC")  # Fallback to stock for now
        else:
            if prefer_no_fee:
                sql_parts.append(f"ORDER BY {lib_type_order}, stock DESC")
            else:
                sql_parts.append("ORDER BY stock DESC")

        # Determine if we need to over-fetch for post-filtering
        # Specs that use pre-computed columns (SPEC_TO_COLUMN) don't need post-filtering
        # Only specs falling back to LIKE patterns need Python post-filtering
        def needs_numeric_filter(sf: SpecFilter) -> bool:
            # First check if this spec has a pre-computed column - if so, no post-filter needed
            attr_names = self._get_attribute_names(sf.name)
            for name in [sf.name] + attr_names:
                if name in SPEC_TO_COLUMN:
                    return False  # SQL handles this with indexed column query
            # Otherwise, check if we need post-filtering for numeric comparison
            if sf.operator in (">=", "<=", ">", "<"):
                return True
            if sf.operator == "=":
                for name in attr_names:
                    if SPEC_PARSERS.get(name):
                        return True
            return False
        has_numeric_filters = spec_filters and any(needs_numeric_filter(sf) for sf in spec_filters)

        # If we have numeric filters, fetch more rows to ensure we get enough after filtering
        # Heuristic: fetch 10x more rows (up to 500) then trim after post-filter
        fetch_limit = limit * 10 if has_numeric_filters else limit
        fetch_limit = min(fetch_limit, 500)

        # Pagination
        sql_parts.append("LIMIT ? OFFSET ?")
        params.extend([fetch_limit, offset])

        # Execute queries - use 2 queries instead of 3 by combining count + distribution
        sql = " ".join(sql_parts)
        count_sql = " ".join(count_parts)

        cursor = self._conn.execute(sql, params)
        rows = cursor.fetchall()

        # Combined count + library type distribution query
        # This replaces two separate queries with one GROUP BY query
        lib_count_sql = count_sql.replace("SELECT COUNT(*)", "SELECT library_type, COUNT(*)")
        # Remove the library_type filter if present for the distribution query
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
            total += count  # Sum up for total count

        # Pre-compute filter metadata for post-filtering (avoid repeated lookups)
        # Skip filters that used pre-computed SQL columns (already filtered in SQL)
        filter_metadata: list[tuple[SpecFilter, set[str], Any, float | None]] = []
        if spec_filters:
            for spec_filter in spec_filters:
                attr_names = self._get_attribute_names(spec_filter.name)

                # Check if this spec used a pre-computed column - skip post-filtering
                has_column = False
                for name in [spec_filter.name] + attr_names:
                    if name in SPEC_TO_COLUMN:
                        has_column = True
                        break
                if has_column and spec_filter.operator in (">=", "<=", ">", "<", "="):
                    continue  # SQL already handled this filter

                # Find parser for any of these names
                parser = None
                for name in attr_names:
                    parser = SPEC_PARSERS.get(name)
                    if parser:
                        break
                # Pre-parse target value if we have a parser
                target_value = None
                if parser and spec_filter.operator in (">=", "<=", ">", "<", "="):
                    target_value = parser(spec_filter.value)
                # Convert attr_names to a set for O(1) lookup
                attr_names_set = set(attr_names)
                filter_metadata.append((spec_filter, attr_names_set, parser, target_value))

        # Post-filter for numeric spec comparisons (only for specs without pre-computed columns)
        results = []
        for row in rows:
            part = self._row_to_dict(row)

            # Apply numeric spec filters using pre-computed metadata
            if filter_metadata:
                passes = True
                part_specs = part.get("specs", {})

                for spec_filter, attr_names_set, parser, target_value in filter_metadata:
                    if parser and spec_filter.operator in (">=", "<=", ">", "<", "="):
                        if target_value is None:
                            continue

                        # Find attribute value in part (check all possible names)
                        part_value = None
                        for attr_name, attr_value in part_specs.items():
                            if attr_name in attr_names_set:
                                part_value = parser(attr_value)
                                if part_value is not None:
                                    break

                        if part_value is None:
                            # Attribute not found or unparseable - exclude
                            passes = False
                            break

                        # Apply comparison with small tolerance for floating point
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

            # Stop if we have enough results
            if len(results) >= limit:
                break

        # Check if no-fee alternatives exist
        no_fee_available = library_type_counts["basic"] > 0 or library_type_counts["preferred"] > 0

        return {
            "results": results[:limit],  # Ensure we don't exceed limit
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

    def get_by_lcsc(self, lcsc: str) -> dict[str, Any] | None:
        """Get a single component by LCSC code."""
        self._ensure_db()
        if not self._conn:
            return None

        cursor = self._conn.execute(
            "SELECT * FROM components WHERE lcsc = ?",
            [lcsc.upper()]
        )
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def get_by_lcsc_batch(self, lcsc_codes: list[str]) -> dict[str, dict[str, Any] | None]:
        """Get multiple components by LCSC codes in a single query.

        More efficient than calling get_by_lcsc() multiple times.
        Useful for BOM validation.

        Args:
            lcsc_codes: List of LCSC codes (e.g., ["C1525", "C25804", "C19702"])

        Returns:
            Dict mapping LCSC code to component data (or None if not found).
            Example: {"C1525": {...}, "C25804": {...}, "C99999": None}
        """
        self._ensure_db()
        if not self._conn or not lcsc_codes:
            return {}

        # Normalize codes (uppercase, dedupe while preserving order)
        seen = set()
        normalized = []
        for code in lcsc_codes:
            upper = code.upper()
            if upper not in seen:
                seen.add(upper)
                normalized.append(upper)

        # Single query with IN clause
        placeholders = ",".join("?" * len(normalized))
        cursor = self._conn.execute(
            f"SELECT * FROM components WHERE lcsc IN ({placeholders})",
            normalized
        )

        # Build result dict
        results: dict[str, dict[str, Any] | None] = {code: None for code in normalized}
        for row in cursor:
            part = self._row_to_dict(row)
            results[part["lcsc"]] = part

        return results

    def find_by_subcategory(
        self,
        subcategory_id: int,
        primary_spec: str | None = None,
        primary_value: Any = None,
        min_stock: int = 100,
        library_type: str | None = None,
        prefer_no_fee: bool = True,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Find components in a subcategory, optionally matching a primary spec value.

        Used by find_alternatives to get candidates.

        Args:
            subcategory_id: Subcategory to search in
            primary_spec: Primary spec name to match (e.g., "Resistance")
            primary_value: Value to match for primary spec
            min_stock: Minimum stock (default 100)
            library_type: Filter by library type - "basic", "preferred", or "extended".
                None (default) means no filtering.
            prefer_no_fee: Sort preference (default True). When True, sorts results with
                basic parts first, then preferred, then extended.
            limit: Max results to return
        """
        self._ensure_db()
        if not self._conn:
            return []

        sql_parts = ["SELECT * FROM components WHERE subcategory_id = ?"]
        params: list[Any] = [subcategory_id]

        if min_stock > 0:
            sql_parts.append("AND stock >= ?")
            params.append(min_stock)

        # Library type filter (actual filter - use prefer_no_fee for sort preference)
        if library_type:
            if library_type == "basic":
                sql_parts.append("AND library_type = 'b'")
            elif library_type == "preferred":
                sql_parts.append("AND library_type = 'p'")
            elif library_type == "extended":
                sql_parts.append("AND library_type = 'e'")

        # If primary spec value provided, filter by it
        if primary_spec and primary_value:
            parser = SPEC_PARSERS.get(primary_spec)
            if parser:
                # Numeric spec - will post-filter
                pass
            else:
                # String match
                sql_parts.append("AND attributes LIKE ? ESCAPE '\\'")
                pattern = f'%"{_escape_like(primary_spec)}","{_escape_like(primary_value)}"%'
                params.append(pattern)

        # Sorting: prefer_no_fee sorts basic/preferred first
        if prefer_no_fee:
            lib_type_order = "CASE library_type WHEN 'b' THEN 1 WHEN 'p' THEN 2 ELSE 3 END"
            sql_parts.append(f"ORDER BY {lib_type_order}, stock DESC")
        else:
            sql_parts.append("ORDER BY stock DESC")
        sql_parts.append("LIMIT ?")
        params.append(limit * 2)  # Fetch more for post-filtering

        sql = " ".join(sql_parts)
        cursor = self._conn.execute(sql, params)

        results = []
        for row in cursor.fetchall():
            part = self._row_to_dict(row)

            # Post-filter for numeric primary spec
            if primary_spec and primary_value:
                parser = SPEC_PARSERS.get(primary_spec)
                if parser:
                    target = parser(str(primary_value))
                    if target is not None:
                        part_value = part.get("specs", {}).get(primary_spec)
                        if part_value:
                            parsed = parser(part_value)
                            if parsed is None:
                                continue
                            # Allow 2% tolerance
                            if target == 0:
                                if parsed != 0:
                                    continue
                            elif abs(parsed - target) / abs(target) > 0.02:
                                continue
                        else:
                            continue  # No matching attribute

            results.append(part)
            if len(results) >= limit:
                break

        return results

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a database row to a component dict.

        Returns format matching client.py's _transform_part() for consistency.
        """
        # Parse attributes JSON back to specs dict (with error handling)
        specs: dict[str, str] = {}
        if row["attributes"]:
            try:
                attrs = json.loads(row["attributes"])
                specs = {name: value for name, value in attrs}
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to parse attributes for {row['lcsc']}: {e}")
                # Continue with empty specs rather than failing

        # Map library_type codes
        lib_type_map = {"b": "basic", "p": "preferred", "e": "extended"}
        library_type = lib_type_map.get(row["library_type"], row["library_type"])

        # Get subcategory info
        subcat_info = self._subcategories.get(row["subcategory_id"], {})
        package = row["package"]
        category = subcat_info.get("category_name")
        subcategory = subcat_info.get("name")

        return {
            "lcsc": row["lcsc"],
            "model": row["mpn"],
            "manufacturer": row["manufacturer"],
            "package": package,
            "stock": row["stock"],
            "price": row["price"],
            "price_10": None,  # Volume pricing not available in DB
            "library_type": library_type,
            "preferred": library_type in ("basic", "preferred"),
            "category": category,
            "subcategory": subcategory,
            "subcategory_id": row["subcategory_id"],
            "mounting_type": detect_mounting_type(package, category=category, subcategory=subcategory),
            "description": row["description"],
            "specs": specs,
        }

    def get_categories_for_client(self) -> list[dict[str, Any]]:
        """Export categories in format expected by JLCPCBClient.set_categories().

        Returns list of categories with nested subcategories, matching API format.
        """
        self._ensure_db()
        if not self._conn:
            return []

        # Group subcategories by category
        categories_dict: dict[int, dict[str, Any]] = {}

        for subcat_id, info in self._subcategories.items():
            cat_id = info["category_id"]
            cat_name = info["category_name"]

            if cat_id not in categories_dict:
                categories_dict[cat_id] = {
                    "id": cat_id,
                    "name": cat_name,
                    "count": 0,
                    "subcategories": [],
                }

            categories_dict[cat_id]["subcategories"].append({
                "id": subcat_id,
                "name": info["name"],
                "count": 0,  # Count not stored, but not needed for name resolution
            })

        return list(categories_dict.values())

    def list_attributes(
        self,
        subcategory_id: int | None = None,
        subcategory_name: str | None = None,
        sample_size: int = 1000,
    ) -> dict[str, Any]:
        """List available filterable attributes for a subcategory.

        Scans components in the subcategory to discover what attributes exist
        and their value ranges. Useful for understanding what spec_filters
        can be used with search().

        Args:
            subcategory_id: Subcategory ID (e.g., 2954 for MOSFETs)
            subcategory_name: Subcategory name (alternative to ID)
            sample_size: How many parts to sample (default 1000)

        Returns:
            {
                "subcategory_id": 2954,
                "subcategory_name": "MOSFETs",
                "attributes": [
                    {
                        "name": "Gate Threshold Voltage (Vgs(th))",
                        "alias": "Vgs(th)",  # Short name to use in spec_filters
                        "type": "numeric",   # Can use >=, <=, >, <, = operators
                        "count": 850,        # How many parts have this attribute
                        "example_values": ["1V~2.5V", "0.5V", "1.5V~2.5V"]
                    },
                    {
                        "name": "Type",
                        "alias": null,
                        "type": "string",    # Use = operator only
                        "count": 1000,
                        "values": ["N-Channel", "P-Channel"]  # All distinct values
                    }
                ]
            }
        """
        self._ensure_db()
        if not self._conn:
            return {"error": "Database not available"}

        # Resolve subcategory name to ID
        resolved_id = subcategory_id
        if subcategory_name and not subcategory_id:
            resolved_id = self.resolve_subcategory_name(subcategory_name)
            if resolved_id is None:
                similar = self._find_similar_subcategories(subcategory_name, limit=5)
                return {
                    "error": f"Subcategory not found: '{subcategory_name}'",
                    "similar_subcategories": similar,
                }

        if not resolved_id:
            return {"error": "Must provide subcategory_id or subcategory_name"}

        subcat_info = self._subcategories.get(resolved_id)
        if not subcat_info:
            return {"error": f"Subcategory ID {resolved_id} not found"}

        # Sample components from this subcategory
        cursor = self._conn.execute(
            "SELECT attributes FROM components WHERE subcategory_id = ? LIMIT ?",
            [resolved_id, sample_size]
        )

        # Collect attribute statistics
        attr_counts: dict[str, int] = {}
        attr_values: dict[str, set[str]] = {}

        for row in cursor:
            if not row["attributes"]:
                continue
            try:
                attrs = json.loads(row["attributes"])
                for attr in attrs:
                    # Handle malformed attributes gracefully
                    if not isinstance(attr, (list, tuple)) or len(attr) != 2:
                        continue
                    name, value = attr
                    attr_counts[name] = attr_counts.get(name, 0) + 1
                    if name not in attr_values:
                        attr_values[name] = set()
                    # Only collect up to 100 unique values per attribute
                    if len(attr_values[name]) < 100:
                        attr_values[name].add(value)
            except (json.JSONDecodeError, TypeError, ValueError):
                # Skip malformed JSON
                continue

        # Build reverse alias lookup
        alias_lookup: dict[str, str] = {}
        for alias, full_names in ATTRIBUTE_ALIASES.items():
            for full_name in full_names:
                alias_lookup[full_name] = alias

        # Build attribute list
        attributes = []
        for name, count in sorted(attr_counts.items(), key=lambda x: -x[1]):
            # Determine if this is a numeric attribute
            is_numeric = name in SPEC_PARSERS or any(
                name in full_names for full_names in ATTRIBUTE_ALIASES.values()
                if any(fn in SPEC_PARSERS for fn in ATTRIBUTE_ALIASES.get(alias_lookup.get(name, ""), [name]))
            )

            # Simpler check: see if any value parses as numeric
            values = list(attr_values.get(name, []))
            parser = SPEC_PARSERS.get(name)
            if not parser:
                # Check aliases
                alias = alias_lookup.get(name)
                if alias and alias in ATTRIBUTE_ALIASES:
                    for alias_target in ATTRIBUTE_ALIASES[alias]:
                        if alias_target in SPEC_PARSERS:
                            parser = SPEC_PARSERS[alias_target]
                            break

            # Test if values are numeric
            if parser and values:
                numeric_count = sum(1 for v in values[:10] if parser(v) is not None)
                is_numeric = numeric_count >= len(values[:10]) * 0.5

            attr_info: dict[str, Any] = {
                "name": name,
                "alias": alias_lookup.get(name),
                "type": "numeric" if is_numeric else "string",
                "count": count,
            }

            if is_numeric:
                # For numeric, show example values
                attr_info["example_values"] = values[:5]
            else:
                # For string, show all distinct values (up to limit)
                attr_info["values"] = sorted(values)[:20]

            attributes.append(attr_info)

        return {
            "subcategory_id": resolved_id,
            "subcategory_name": subcat_info["name"],
            "category_name": subcat_info["category_name"],
            "sample_size": sample_size,
            "attributes": attributes,
        }

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        self._ensure_db()
        if not self._conn:
            return {"error": "Database not available"}

        stats = {}

        # Total parts
        cursor = self._conn.execute("SELECT COUNT(*) FROM components")
        stats["total_parts"] = cursor.fetchone()[0]

        # By library type
        cursor = self._conn.execute("""
            SELECT library_type, COUNT(*) as cnt
            FROM components
            GROUP BY library_type
        """)
        lib_counts = {}
        for row in cursor:
            lib_type = {"b": "basic", "p": "preferred", "e": "extended"}.get(
                row["library_type"], row["library_type"]
            )
            lib_counts[lib_type] = row["cnt"]
        stats["by_library_type"] = lib_counts

        # Categories count
        stats["categories"] = len(self._categories)
        stats["subcategories"] = len(self._subcategories)

        return stats


# Global instance with thread safety
_db: ComponentDatabase | None = None
_db_lock = threading.Lock()


def get_db() -> ComponentDatabase:
    """Get or create the global database instance (thread-safe)."""
    global _db
    if _db is None:
        with _db_lock:
            # Double-check locking pattern
            if _db is None:
                _db = ComponentDatabase()
    return _db


def close_db() -> None:
    """Close the global database instance (thread-safe)."""
    global _db
    with _db_lock:
        if _db:
            _db.close()
            _db = None
