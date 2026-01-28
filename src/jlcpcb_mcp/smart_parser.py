"""Smart query parser for natural language component searches.

This module provides intelligent parsing of queries like:
- "TP4056 lithium battery charger" → searches for TP4056 model
- "100V mosfet" → subcategory=MOSFETs, Vds>=100V
- "10uH inductor 2A" → subcategory=Inductors, L=10uH, Current Rating>=2A
- "schottky diode SOD-123 1A" → subcategory=Schottky, package=SOD-123, If>=1A
- "n-channel mosfet low Vgs" → subcategory=MOSFETs, Type=N-Channel, Vgs(th)<2.5V

Key features:
1. Token classification (model numbers, values, packages, types, descriptors)
2. Category-aware attribute mapping (voltage→Vds for MOSFETs, →Vr for diodes)
3. Semantic descriptor interpretation ("low Vgs", "logic level", "bidirectional")
4. Smart FTS fallback (only search model numbers when structured filters exist)
"""

import re
from dataclasses import dataclass, field
from typing import Any, Literal

from .subcategory_aliases import SUBCATEGORY_ALIASES


# =============================================================================
# PACKAGE PATTERNS - Comprehensive coverage
# =============================================================================

# Pre-compiled patterns for performance
PACKAGE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Imperial chip sizes (passives)
    (re.compile(r'\b(01005|0201|0402|0603|0805|1206|1210|1812|2010|2512)\b'), 'imperial'),

    # Metric chip sizes
    (re.compile(r'\b(0402M|0603M|0805M|1206M)\b', re.IGNORECASE), 'metric'),

    # SOT packages - comprehensive with any pin count suffix
    (re.compile(r'\b(SOT-?23(?:-\d+)?L?|SOT-?89(?:-\d+)?|SOT-?223(?:-\d+)?|SOT-?323(?:-\d+)?|SOT-?363(?:-\d+)?|SOT-?523(?:-\d+)?|SOT-?723(?:-\d+)?)\b', re.IGNORECASE), 'sot'),

    # SOD packages (Small Outline Diode) - critical for diodes!
    (re.compile(r'\b(SOD-?(?:123|323|523|923|128|882|80|110|123FL|323FL))\b', re.IGNORECASE), 'sod'),

    # DO packages (Diode Outline)
    (re.compile(r'\b(DO-?(?:35|41|201|204|214|215|218|219|220)(?:AA|AB|AC|AD|AE|AF|AG)?)\b', re.IGNORECASE), 'do'),

    # TO packages
    (re.compile(r'\b(TO-?92(?:S|L)?|TO-?220(?:F|FP|AB)?(?:-\d+)?|TO-?252(?:-\d+)?|TO-?263(?:-\d+)?|TO-?247(?:-\d+)?|TO-?251|TO-?3P(?:F)?|DPAK|D2PAK|D3PAK)\b', re.IGNORECASE), 'to'),

    # QFN/DFN packages with optional size
    (re.compile(r'\b((?:V)?QFN-?\d+(?:-EP)?(?:\([^)]+\))?|DFN-?\d+(?:-EP)?(?:\([^)]+\))?|WQFN-?\d+|TQFN-?\d+|UQFN-?\d+)\b', re.IGNORECASE), 'qfn'),

    # QFP/LQFP/TQFP packages
    (re.compile(r'\b((?:L|T|H|PQ)?QFP-?\d+(?:\([^)]+\))?)\b', re.IGNORECASE), 'qfp'),

    # BGA packages
    (re.compile(r'\b((?:FC|W|T|M|U|P|F)?BGA-?\d+(?:\([^)]+\))?)\b', re.IGNORECASE), 'bga'),

    # DIP/SIP packages
    (re.compile(r'\b((?:P|S|SK|C)?DIP-?\d+(?:\([^)]+\))?|SIP-?\d+)\b', re.IGNORECASE), 'dip'),

    # SOP/SOIC/SSOP/TSSOP/MSOP packages (order matters - TSSOP before SOP)
    (re.compile(r'\b(TSSOP-?\d+|SSOP-?\d+|MSOP-?\d+|QSOP-?\d+|HTSSOP-?\d+|VSSOP-?\d+)\b', re.IGNORECASE), 'tssop'),
    (re.compile(r'\b(SOP-?\d+(?:-\d+)?(?:\([^)]+\))?|SOIC-?\d+(?:-\d+)?(?:\([^)]+\))?)\b', re.IGNORECASE), 'sop'),

    # Module packages (SMD-XX, LGA-XX) - NOT bare "MODULE" which is a common word
    # SMA/SMB/SMC are diode packages, but SMA is also a connector type
    # Only match SMA/SMB/SMC when NOT followed by "connector" to avoid conflict
    (re.compile(r'\b(SMD-?\d+|LGA-?\d+)\b', re.IGNORECASE), 'module'),
    # SMA/SMB/SMC diode packages - but exclude "SMA connector" patterns
    (re.compile(r'\b(SM[ABC])\b(?!\s*connector)', re.IGNORECASE), 'diode_pkg'),

    # Connector specific
    (re.compile(r'\b(USB-?[ABC]|TYPE-?[ABC]|MICRO-?USB|MINI-?USB)\b', re.IGNORECASE), 'usb'),
]


def extract_package(query: str) -> tuple[str | None, str, str | None]:
    """Extract package from query and return (package, remaining_query, suggested_subcategory).

    The suggested_subcategory is used for USB-C etc. where the package implies a component type.
    """
    for pattern, pkg_type in PACKAGE_PATTERNS:
        match = pattern.search(query)
        if match:
            package = match.group(1).upper()
            # Normalize: remove optional hyphen variations
            package = re.sub(r'SOT(\d)', r'SOT-\1', package)
            package = re.sub(r'SOD(\d)', r'SOD-\1', package)
            package = re.sub(r'TO(\d)', r'TO-\1', package)
            remaining = query[:match.start()] + query[match.end():]
            remaining = remaining.strip()

            # Suggest subcategory for connector packages
            suggested_subcat = None
            if pkg_type == 'usb':
                suggested_subcat = 'usb connectors'

            return package, remaining, suggested_subcat
    return None, query, None


# =============================================================================
# VALUE PATTERNS - Extract numeric values with units
# =============================================================================

@dataclass
class ExtractedValue:
    """A numeric value extracted from the query."""
    raw: str  # Original text (e.g., "10k", "100nF")
    value: float  # Parsed numeric value in base units
    unit_type: str  # "resistance", "capacitance", "voltage", etc.
    normalized: str  # Normalized form (e.g., "10kΩ", "100nF")


# Patterns for extracting values - order matters!
VALUE_PATTERNS: list[tuple[re.Pattern[str], str, callable]] = []

# Resistance: 10k, 100R, 4.7k, 1M, 100ohm, 4k7 (European notation)
_RES_EURO = re.compile(r'\b(\d+)([kKmMrR])(\d+)\b')
_RES_STD = re.compile(r'\b(\d+(?:\.\d+)?)\s*([kKmMrRΩ]|ohm|kohm|mohm)\b', re.IGNORECASE)

# Capacitance: 10uF, 100nF, 1pF, 4.7uF
_CAP = re.compile(r'\b(\d+(?:\.\d+)?)\s*(u[fF]|n[fF]|p[fF]|[uμ]F|nF|pF)\b')

# Inductance: 10uH, 100nH, 1mH
_IND = re.compile(r'\b(\d+(?:\.\d+)?)\s*(u[hH]|n[hH]|m[hH]|[uμ]H|nH|mH)\b')

# Voltage: 25V, 50V, 3.3V, 5kV (but not in model numbers)
_VOLT = re.compile(r'\b(\d+(?:\.\d+)?)\s*([kK])?[vV]\b')

# Current: 5A, 10A, 100mA, 500mA, 10uA
_CURR = re.compile(r'\b(\d+(?:\.\d+)?)\s*([uμ]?[mM]?)[aA]\b')

# Frequency: 8MHz, 32.768kHz, 2.4GHz
_FREQ = re.compile(r'\b(\d+(?:\.\d+)?)\s*([kKmMgG])?[hH][zZ]\b')

# Tolerance: 1%, 5%, 0.1%
_TOL = re.compile(r'\b(\d+(?:\.\d+)?)\s*%')

# Power: 1W, 0.25W, 100mW, 1/4W
_POWER_FRAC = re.compile(r'\b(\d+)/(\d+)\s*[wW]\b')
_POWER = re.compile(r'\b(\d+(?:\.\d+)?)\s*([mM])?[wW]\b')

# Temperature: 85°C, -40C, 125℃
_TEMP = re.compile(r'\b([+-]?\d+)\s*[°℃]?C\b', re.IGNORECASE)

# Pin count: 16 pin, 8-pin, 24pin
_PINS = re.compile(r'\b(\d+)\s*-?pins?\b', re.IGNORECASE)

# Dimensions: 6x6mm, 3.5x3.5mm
_DIM = re.compile(r'\b(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)\s*(?:mm)?\b')

# Pitch (connector spacing): 2.54mm pitch, 5.08mm, 1.27mm pitch
# Match patterns like "2.54mm", "5.08mm pitch", "1.27 mm"
# Common pitches: 1.0mm, 1.27mm, 2.0mm, 2.54mm, 3.5mm, 3.81mm, 5.0mm, 5.08mm
_PITCH = re.compile(r'\b(\d+(?:\.\d+)?)\s*mm(?:\s+pitch)?\b', re.IGNORECASE)

# Position count for connectors: 2-pos, 2 position, 2-position, 2P
_POSITION = re.compile(r'\b(\d+)\s*-?\s*(?:pos(?:ition)?|way|P)\b', re.IGNORECASE)

# Header pin structure: 1x7, 2x20, 1X40 (rows x pins per row)
_PIN_STRUCTURE = re.compile(r'\b([12])\s*[xX×]\s*(\d+)\b')


def _parse_resistance_value(match: re.Match) -> tuple[float, str]:
    """Parse resistance match to (ohms, normalized_string)."""
    groups = match.groups()
    if len(groups) == 3 and groups[2]:  # European notation: 4k7
        int_part, suffix, frac_part = groups
        value = float(f"{int_part}.{frac_part}")
        suffix = suffix.upper()
        if suffix == 'R':
            return value, f"{int_part}R{frac_part}"
        elif suffix == 'K':
            return value * 1000, f"{int_part}k{frac_part}"
        elif suffix == 'M':
            return value * 1_000_000, f"{int_part}M{frac_part}"
    else:  # Standard: 10k, 100R
        value_str = groups[0]
        suffix = (groups[1] or '').upper()
        value = float(value_str)
        if suffix in ('R', 'Ω', 'OHM'):
            return value, f"{value_str}Ω"
        elif suffix in ('K', 'KOHM'):
            return value * 1000, f"{value_str}kΩ"
        elif suffix in ('M', 'MOHM'):
            return value * 1_000_000, f"{value_str}MΩ"
        return value, f"{value_str}Ω"
    return 0, ""


def extract_values(query: str) -> tuple[list[ExtractedValue], str]:
    """Extract all numeric values from query, return (values, remaining_query)."""
    values = []
    remaining = query

    # Extract in specific order to avoid conflicts
    extractions = []

    # Tolerance first (before other numbers)
    for match in _TOL.finditer(query):
        pct = float(match.group(1))
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=pct,
            unit_type="tolerance",
            normalized=f"{match.group(1)}%"
        )))

    # Frequency (before generic numbers)
    for match in _FREQ.finditer(query):
        value = float(match.group(1))
        suffix = (match.group(2) or '').upper()
        if suffix == 'K':
            value *= 1e3
            norm = f"{match.group(1)}kHz"
        elif suffix == 'M':
            value *= 1e6
            norm = f"{match.group(1)}MHz"
        elif suffix == 'G':
            value *= 1e9
            norm = f"{match.group(1)}GHz"
        else:
            norm = f"{match.group(1)}Hz"
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=value,
            unit_type="frequency",
            normalized=norm
        )))

    # Resistance (European notation first)
    for match in _RES_EURO.finditer(query):
        ohms, norm = _parse_resistance_value(match)
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=ohms,
            unit_type="resistance",
            normalized=norm
        )))

    # Resistance (standard)
    for match in _RES_STD.finditer(query):
        # Skip if already matched by European pattern
        if any(s <= match.start() < e for s, e, _ in extractions):
            continue
        ohms, norm = _parse_resistance_value(match)
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=ohms,
            unit_type="resistance",
            normalized=norm
        )))

    # Capacitance
    for match in _CAP.finditer(query):
        value = float(match.group(1))
        suffix = match.group(2).lower()
        if suffix in ('uf', 'μf'):
            farads = value * 1e-6
            norm = f"{match.group(1)}uF"
        elif suffix == 'nf':
            farads = value * 1e-9
            norm = f"{match.group(1)}nF"
        elif suffix == 'pf':
            farads = value * 1e-12
            norm = f"{match.group(1)}pF"
        else:
            farads = value
            norm = f"{match.group(1)}F"
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=farads,
            unit_type="capacitance",
            normalized=norm
        )))

    # Inductance
    for match in _IND.finditer(query):
        value = float(match.group(1))
        suffix = match.group(2).lower()
        if suffix in ('uh', 'μh'):
            henries = value * 1e-6
            norm = f"{match.group(1)}uH"
        elif suffix == 'nh':
            henries = value * 1e-9
            norm = f"{match.group(1)}nH"
        elif suffix == 'mh':
            henries = value * 1e-3
            norm = f"{match.group(1)}mH"
        else:
            henries = value
            norm = f"{match.group(1)}H"
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=henries,
            unit_type="inductance",
            normalized=norm
        )))

    # Voltage (be careful not to match model numbers like STM32F103)
    for match in _VOLT.finditer(query):
        # Skip if preceded by letter (likely model number)
        if match.start() > 0 and query[match.start()-1].isalpha():
            continue
        value = float(match.group(1))
        kilo = match.group(2)
        if kilo:
            value *= 1000
            norm = f"{match.group(1)}kV"
        else:
            norm = f"{match.group(1)}V"
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=value,
            unit_type="voltage",
            normalized=norm
        )))

    # Current
    for match in _CURR.finditer(query):
        value = float(match.group(1))
        prefix = (match.group(2) or '').lower()
        if prefix in ('u', 'μ'):
            amps = value * 1e-6
            norm = f"{match.group(1)}uA"
        elif prefix == 'm':
            amps = value * 1e-3
            norm = f"{match.group(1)}mA"
        else:
            amps = value
            norm = f"{match.group(1)}A"
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=amps,
            unit_type="current",
            normalized=norm
        )))

    # Power (fraction first)
    for match in _POWER_FRAC.finditer(query):
        watts = float(match.group(1)) / float(match.group(2))
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=watts,
            unit_type="power",
            normalized=f"{match.group(1)}/{match.group(2)}W"
        )))

    # Power (standard)
    for match in _POWER.finditer(query):
        if any(s <= match.start() < e for s, e, _ in extractions):
            continue
        value = float(match.group(1))
        prefix = (match.group(2) or '').lower()
        if prefix == 'm':
            watts = value * 1e-3
            norm = f"{match.group(1)}mW"
        else:
            watts = value
            norm = f"{match.group(1)}W"
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=watts,
            unit_type="power",
            normalized=norm
        )))

    # Pin count
    for match in _PINS.finditer(query):
        pins = int(match.group(1))
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=pins,
            unit_type="pin_count",
            normalized=f"{pins} pin"
        )))

    # Position count (for connectors: 2-pos, 2 position, 2-way, 2P)
    for match in _POSITION.finditer(query):
        # Skip if already matched by another pattern
        if any(s <= match.start() < e for s, e, _ in extractions):
            continue
        positions = int(match.group(1))
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=positions,
            unit_type="position_count",
            normalized=f"{positions}P"
        )))

    # Pin structure for headers (1x7, 2x20, etc.)
    for match in _PIN_STRUCTURE.finditer(query):
        # Skip if already matched by dimension pattern
        if any(s <= match.start() < e for s, e, _ in extractions):
            continue
        rows = int(match.group(1))
        pins_per_row = int(match.group(2))
        total_pins = rows * pins_per_row
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=total_pins,
            unit_type="pin_count",
            normalized=f"{rows}x{pins_per_row}P"
        )))

    # Pitch (connector spacing) - extract common connector pitches
    # Only extract specific common pitch values to avoid false positives
    # 0.5mm and 1.0mm are common for FFC/FPC connectors
    COMMON_PITCHES = {0.5, 0.8, 1.0, 1.25, 1.27, 2.0, 2.54, 3.5, 3.81, 5.0, 5.08, 7.62}
    for match in _PITCH.finditer(query):
        # Skip if already matched by another pattern
        if any(s <= match.start() < e for s, e, _ in extractions):
            continue
        pitch_val = float(match.group(1))
        # Only extract if it's a known connector pitch value
        if pitch_val in COMMON_PITCHES:
            extractions.append((match.start(), match.end(), ExtractedValue(
                raw=match.group(0),
                value=pitch_val,
                unit_type="pitch",
                normalized=f"{match.group(1)}mm"
            )))

    # Dimensions
    for match in _DIM.finditer(query):
        # Store as tuple encoded in value (x*1000 + y for simple encoding)
        x, y = float(match.group(1)), float(match.group(2))
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=x * 1000 + y,  # Encoded
            unit_type="dimensions",
            normalized=f"{match.group(1)}x{match.group(2)}mm"
        )))

    # Sort by start position and remove overlaps
    extractions.sort(key=lambda x: x[0])
    non_overlapping = []
    last_end = -1
    for start, end, val in extractions:
        if start >= last_end:
            non_overlapping.append((start, end, val))
            last_end = end
            values.append(val)

    # Build remaining query by removing extracted parts
    if non_overlapping:
        parts = []
        last_end = 0
        for start, end, _ in non_overlapping:
            parts.append(query[last_end:start])
            last_end = end
        parts.append(query[last_end:])
        remaining = ' '.join(parts).strip()
        remaining = re.sub(r'\s+', ' ', remaining)

    return values, remaining


# =============================================================================
# MODEL NUMBER DETECTION
# =============================================================================

# Common model number patterns (component-specific part numbers)
MODEL_PATTERNS = [
    # IC model numbers: STM32F103, ESP32-C3, TP4056, AMS1117
    re.compile(r'\b([A-Z]{2,5}\d{2,5}[A-Z]?\d*(?:-[A-Z0-9]+)?)\b', re.IGNORECASE),
    # Specific known patterns
    re.compile(r'\b(ESP32-[A-Z0-9]+|STM32[A-Z]\d+[A-Z0-9]*|RP2040|ATMEGA\d+[A-Z]*|PIC\d+[A-Z0-9]*)\b', re.IGNORECASE),
    re.compile(r'\b(TP[45]\d{3}|AMS\d{4}|LM\d{4}|NE555|TL\d{3}|LMV?\d{3,4}|TPS\d{4,5})\b', re.IGNORECASE),
    re.compile(r'\b(AO\d{4}|SI\d{4}|IRF\d{3,4}|IRLZ?\d{2,4}|2N\d{4}|BC\d{3})\b', re.IGNORECASE),
    re.compile(r'\b(WS2812[A-Z]*|SK6812|APA102|TLC5940)\b', re.IGNORECASE),
    # Diode/discrete model numbers: 1N4148, 1N5819, 1SS400
    re.compile(r'\b(1N\d{4}[A-Z]*|1SS\d{3}[A-Z]*|BAT\d{2}[A-Z]*|BAS\d{2}[A-Z]*|BAV\d{2}[A-Z]*)\b', re.IGNORECASE),
]


def extract_model_number(query: str) -> tuple[str | None, str]:
    """Extract likely model number from query."""
    query_upper = query.upper()

    for pattern in MODEL_PATTERNS:
        match = pattern.search(query)
        if match:
            model = match.group(1)
            # Verify it's not a common word or measurement
            if model.upper() not in ('LED', 'LCD', 'USB', 'SPI', 'I2C', 'ADC', 'DAC', 'MCU', 'CPU', 'GPU'):
                remaining = query[:match.start()] + query[match.end():]
                return model, remaining.strip()

    return None, query


# =============================================================================
# COMPONENT TYPE DETECTION (with priority ordering)
# =============================================================================

# Pre-sorted by length (longest first) for correct matching
_SUBCATEGORY_KEYWORDS_BY_LENGTH = sorted(SUBCATEGORY_ALIASES.keys(), key=len, reverse=True)


def extract_component_type(query: str) -> tuple[str | None, str, str | None]:
    """Extract component type from query.

    Returns: (subcategory_name, remaining_query, matched_keyword)
    """
    query_lower = query.lower()

    for keyword in _SUBCATEGORY_KEYWORDS_BY_LENGTH:
        if keyword in query_lower:
            # Remove the keyword from query
            # Use word boundaries to avoid partial matches
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            remaining = pattern.sub('', query).strip()
            remaining = re.sub(r'\s+', ' ', remaining)
            return SUBCATEGORY_ALIASES[keyword], remaining, keyword

    return None, query, None


# =============================================================================
# SEMANTIC DESCRIPTORS - Interpret qualitative terms
# =============================================================================

@dataclass
class SemanticFilter:
    """A filter derived from semantic interpretation."""
    spec_name: str
    operator: Literal["=", ">=", "<=", ">", "<"]
    value: str
    source: str  # Original descriptor that generated this


# Semantic descriptor mappings
SEMANTIC_DESCRIPTORS: dict[str, list[SemanticFilter]] = {
    # MOSFET threshold voltage
    "low vgs": [SemanticFilter("Vgs(th)", "<", "2.5V", "low vgs")],
    "low vgs(th)": [SemanticFilter("Vgs(th)", "<", "2.5V", "low vgs(th)")],
    "logic level": [SemanticFilter("Vgs(th)", "<", "2.5V", "logic level")],
    "logic-level": [SemanticFilter("Vgs(th)", "<", "2.5V", "logic-level")],
    "low threshold": [SemanticFilter("Vgs(th)", "<", "2.5V", "low threshold")],
    "low rds": [SemanticFilter("RDS(on)", "<", "50mΩ", "low rds")],
    "low rds(on)": [SemanticFilter("RDS(on)", "<", "50mΩ", "low rds(on)")],
    "low on-resistance": [SemanticFilter("RDS(on)", "<", "50mΩ", "low on-resistance")],

    # TVS/Diode polarity (DB uses "Polarity" not "Type" for this)
    "bidirectional": [SemanticFilter("Polarity", "=", "Bidirectional", "bidirectional")],
    "unidirectional": [SemanticFilter("Polarity", "=", "Unidirectional", "unidirectional")],

    # Interface types
    "i2c": [SemanticFilter("Interface", "=", "I2C", "i2c")],
    "spi": [SemanticFilter("Interface", "=", "SPI", "spi")],
    "uart": [SemanticFilter("Interface", "=", "UART", "uart")],
    "i2s": [SemanticFilter("Interface", "=", "I2S", "i2s")],
    "can": [SemanticFilter("Interface", "=", "CAN", "can")],
    "rs485": [SemanticFilter("Interface", "=", "RS485", "rs485")],
    "rs232": [SemanticFilter("Interface", "=", "RS232", "rs232")],
    # Note: DS18B20 and similar use "Single-bus" not "1-Wire" in the Interface field
    "1-wire": [SemanticFilter("Interface", "=", "Single-bus", "1-wire")],
    "one-wire": [SemanticFilter("Interface", "=", "Single-bus", "one-wire")],
    "single-bus": [SemanticFilter("Interface", "=", "Single-bus", "single-bus")],

    # MOSFET channel type
    "n-channel": [SemanticFilter("Type", "=", "N-Channel", "n-channel")],
    "p-channel": [SemanticFilter("Type", "=", "P-Channel", "p-channel")],
    "n channel": [SemanticFilter("Type", "=", "N-Channel", "n channel")],
    "p channel": [SemanticFilter("Type", "=", "P-Channel", "p channel")],
    "nmos": [SemanticFilter("Type", "=", "N-Channel", "nmos")],
    "pmos": [SemanticFilter("Type", "=", "P-Channel", "pmos")],

    # BJT type
    "npn": [SemanticFilter("Type", "=", "NPN", "npn")],
    "pnp": [SemanticFilter("Type", "=", "PNP", "pnp")],

    # LED colors (DB uses "Illumination Color" not "Color")
    "red": [SemanticFilter("Illumination Color", "=", "Red", "red")],
    "green": [SemanticFilter("Illumination Color", "=", "Green", "green")],
    "blue": [SemanticFilter("Illumination Color", "=", "Blue", "blue")],
    "yellow": [SemanticFilter("Illumination Color", "=", "Yellow", "yellow")],
    "white": [SemanticFilter("Illumination Color", "=", "White", "white")],
    "orange": [SemanticFilter("Illumination Color", "=", "Orange", "orange")],
    "amber": [SemanticFilter("Illumination Color", "=", "Amber", "amber")],
    # Note: "ir"/"infrared" removed - IR LEDs are a separate subcategory, not a Type value

    # Capacitor temperature coefficients / dielectrics
    "c0g": [SemanticFilter("Temperature Coefficient", "=", "C0G", "c0g")],
    "np0": [SemanticFilter("Temperature Coefficient", "=", "NP0", "np0")],
    "x5r": [SemanticFilter("Temperature Coefficient", "=", "X5R", "x5r")],
    "x7r": [SemanticFilter("Temperature Coefficient", "=", "X7R", "x7r")],
    "x5s": [SemanticFilter("Temperature Coefficient", "=", "X5S", "x5s")],
    "x6s": [SemanticFilter("Temperature Coefficient", "=", "X6S", "x6s")],
    "x7s": [SemanticFilter("Temperature Coefficient", "=", "X7S", "x7s")],
    "y5v": [SemanticFilter("Temperature Coefficient", "=", "Y5V", "y5v")],
    "z5u": [SemanticFilter("Temperature Coefficient", "=", "Z5U", "z5u")],

    # Regulator output type
    "fixed": [SemanticFilter("Output Type", "=", "Fixed", "fixed")],
    "adjustable": [SemanticFilter("Output Type", "=", "Adjustable", "adjustable")],
    "variable": [SemanticFilter("Output Type", "=", "Adjustable", "variable")],

    # Precision
    "precision": [SemanticFilter("Tolerance", "<=", "0.1%", "precision")],
    "high precision": [SemanticFilter("Tolerance", "<=", "0.05%", "high precision")],

    # Note: Removed broken filters that don't match actual DB attributes:
    # - "fast", "fast switching" (no "Speed" attribute)
    # - "fast recovery", "ultrafast" (no such Type values in diodes)
    # - "low power", "low quiescent", "ultra low power" (LDOs use "standby current" not "Quiescent Current")
    # - "high efficiency" (no "Efficiency" attribute verified)
    # - "smd", "surface mount", "through hole", "tht" (mounting_type is a top-level field, not a spec)
}


def extract_semantic_descriptors(query: str) -> tuple[list[SemanticFilter], str]:
    """Extract semantic descriptors from query."""
    filters = []
    remaining = query
    query_lower = query.lower()

    # Sort by length (longest first) to match "ultra low power" before "low power"
    sorted_descriptors = sorted(SEMANTIC_DESCRIPTORS.keys(), key=len, reverse=True)

    for descriptor in sorted_descriptors:
        if descriptor in query_lower:
            filters.extend(SEMANTIC_DESCRIPTORS[descriptor])
            # Remove from query (case-insensitive)
            pattern = re.compile(re.escape(descriptor), re.IGNORECASE)
            remaining = pattern.sub('', remaining).strip()
            remaining = re.sub(r'\s+', ' ', remaining)
            query_lower = remaining.lower()

    return filters, remaining


# =============================================================================
# NOISE WORD REMOVAL
# =============================================================================

NOISE_WORDS = {
    'for', 'with', 'and', 'or', 'the', 'a', 'an', 'to', 'in', 'of',
    'type', 'chip', 'component', 'part', 'parts', 'electronic', 'electronics',
    'antenna',  # Common in RF connector context but not in part descriptions
}


def remove_noise_words(query: str) -> str:
    """Remove common noise words from query."""
    words = query.split()
    filtered = [w for w in words if w.lower() not in NOISE_WORDS]
    return ' '.join(filtered)


# =============================================================================
# CATEGORY-AWARE ATTRIBUTE MAPPING
# =============================================================================

# Maps (category_keyword, value_type) -> spec_name
# This allows voltage to map to Vds for MOSFETs, Vr for diodes, etc.
CATEGORY_ATTRIBUTE_MAP: dict[str, dict[str, str]] = {
    # MOSFETs
    "mosfet": {
        "voltage": "Vds",
        "current": "Id",
    },
    "mosfets": {
        "voltage": "Vds",
        "current": "Id",
    },
    "n-channel mosfet": {
        "voltage": "Vds",
        "current": "Id",
    },
    "p-channel mosfet": {
        "voltage": "Vds",
        "current": "Id",
    },
    "nmos": {
        "voltage": "Vds",
        "current": "Id",
    },
    "pmos": {
        "voltage": "Vds",
        "current": "Id",
    },

    # Diodes
    "diode": {
        "voltage": "Vr",
        "current": "If",
    },
    "schottky": {
        "voltage": "Vr",
        "current": "If",
    },
    "schottky diode": {
        "voltage": "Vr",
        "current": "If",
    },
    "zener": {
        "voltage": "Zener Voltage(Nom)",
        "current": "If",
    },
    "zener diode": {
        "voltage": "Zener Voltage(Nom)",
        "current": "If",
    },
    "rectifier": {
        "voltage": "Vr",
        "current": "If",
    },
    "rectifier diode": {
        "voltage": "Vr",
        "current": "If",
    },
    "tvs": {
        "voltage": "Reverse Stand-Off Voltage (Vrwm)",
        "current": "Peak Pulse Current-Ipp (10/1000us)",
    },
    "tvs diode": {
        "voltage": "Reverse Stand-Off Voltage (Vrwm)",
        "current": "Peak Pulse Current-Ipp (10/1000us)",
    },

    # Inductors
    "inductor": {
        "current": "Current Rating",
    },
    "inductors": {
        "current": "Current Rating",
    },
    "power inductor": {
        "current": "Current Rating",
    },
    "coil": {
        "current": "Current Rating",
    },
    "ferrite bead": {
        "current": "Current Rating",
    },

    # Capacitors
    "capacitor": {
        "voltage": "Voltage Rating",
    },
    "capacitors": {
        "voltage": "Voltage Rating",
    },
    "mlcc": {
        "voltage": "Voltage Rating",
    },
    "electrolytic": {
        "voltage": "Voltage Rating",
        "current": "Ripple Current",
    },
    "tantalum": {
        "voltage": "Voltage Rating",
    },

    # Crystals
    "crystal": {
        "frequency": "Frequency",
    },
    "crystals": {
        "frequency": "Frequency",
    },
    "oscillator": {
        "frequency": "Frequency",
    },

    # BJTs
    "bjt": {
        "voltage": "Vceo",
        "current": "Ic",
    },
    "transistor": {
        "voltage": "Vceo",
        "current": "Ic",
    },
    "npn": {
        "voltage": "Vceo",
        "current": "Ic",
    },
    "pnp": {
        "voltage": "Vceo",
        "current": "Ic",
    },

    # Voltage Regulators
    "ldo": {
        "voltage": "Output Voltage",
        "current": "Output Current",
    },
    "regulator": {
        "voltage": "Output Voltage",
        "current": "Output Current",
    },
    "linear regulator": {
        "voltage": "Output Voltage",
        "current": "Output Current",
    },
    "buck": {
        "voltage": "Output Voltage",
        "current": "Output Current",
    },
    "boost": {
        "voltage": "Output Voltage",
        "current": "Output Current",
    },
    "dc-dc": {
        "voltage": "Output Voltage",
        "current": "Output Current",
    },

    # LEDs
    "led": {
        "current": "Forward Current(If)",
        "voltage": "Voltage - Forward(Vf@If)",
    },
    "leds": {
        "current": "Forward Current(If)",
        "voltage": "Voltage - Forward(Vf@If)",
    },

    # Fuses/PTCs
    "fuse": {
        "voltage": "Voltage Rating",
        "current": "Hold Current",
    },
    "ptc": {
        "voltage": "Voltage Rating",
        "current": "Hold Current",
    },
    "resettable fuse": {
        "voltage": "Voltage Rating",
        "current": "Hold Current",
    },

    # Connectors - comprehensive mappings for all connector types
    "usb connector": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
    },
    "usb-c": {
        "pin_count": "Number of Pins",
    },
    "connector": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
    },
    "header": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
    },
    "pin header": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
    },
    "pin headers": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
    },
    "female header": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
    },
    "female headers": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
    },
    "terminal block": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
        "voltage": "Voltage Rating (Max)",
        "current": "Current Rating",
    },
    "screw terminal": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
        "voltage": "Voltage Rating (Max)",
        "current": "Current Rating",
    },
    "screw terminal blocks": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
        "voltage": "Voltage Rating (Max)",
        "current": "Current Rating",
    },
    "pluggable system terminal block": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
        "voltage": "Voltage Rating (Max)",
        "current": "Current Rating",
    },
    "jst": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
    },
    "wire to board connector": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
        "position_count": "Number of Pins",
    },
    "idc connector": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
    },
    "idc connectors": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
    },
    "ffc": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
    },
    "fpc": {
        "pin_count": "Number of Pins",
        "pitch": "Pitch",
    },

    # Switches
    "tactile switch": {
        "dimensions": "Size",
    },
    "push button": {
        "dimensions": "Size",
    },
}


def map_value_to_spec(
    value: ExtractedValue,
    component_type: str | None,
    matched_keyword: str | None,
) -> tuple[str, str]:
    """Map an extracted value to the appropriate spec name based on context.

    Returns: (spec_name, operator)
    """
    # Default mappings by value type
    default_specs = {
        "voltage": ("Voltage Rating", ">="),
        "current": ("Current Rating", ">="),
        "resistance": ("Resistance", "="),
        "capacitance": ("Capacitance", "="),
        "inductance": ("Inductance", "="),
        "frequency": ("Frequency", "="),
        "tolerance": ("Tolerance", "="),
        "power": ("Power", ">="),
        "pin_count": ("Number of Pins", "="),
        "position_count": ("Number of Pins", "="),  # Positions map to pin count
        "pitch": ("Pitch", "="),
    }

    # Try to get category-specific mapping
    if matched_keyword and matched_keyword.lower() in CATEGORY_ATTRIBUTE_MAP:
        cat_map = CATEGORY_ATTRIBUTE_MAP[matched_keyword.lower()]
        if value.unit_type in cat_map:
            spec_name = cat_map[value.unit_type]
            # Determine operator based on spec type
            if value.unit_type in ("resistance", "capacitance", "inductance", "frequency", "tolerance", "pin_count", "position_count", "pitch"):
                return spec_name, "="
            else:
                return spec_name, ">="

    # Fall back to defaults
    if value.unit_type in default_specs:
        return default_specs[value.unit_type]

    return value.unit_type.title(), "="


# =============================================================================
# MAIN PARSER
# =============================================================================

@dataclass
class ParsedQuery:
    """Result of parsing a smart query string."""
    original: str
    remaining_text: str  # For FTS search
    subcategory: str | None = None
    spec_filters: list[Any] = field(default_factory=list)  # List of SpecFilter
    package: str | None = None
    model_number: str | None = None
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
    """
    # Import SpecFilter here to avoid circular import
    from .db import SpecFilter

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
    elif pkg_suggested_subcat:
        # Use package-suggested subcategory (e.g., USB-C -> USB connectors)
        result.subcategory = pkg_suggested_subcat
        detected["subcategory_from_package"] = pkg_suggested_subcat

    # Step 4: Extract numeric values
    values, remaining = extract_values(remaining)
    if values:
        detected["values"] = [{"raw": v.raw, "type": v.unit_type, "normalized": v.normalized} for v in values]

    # Step 4b: Infer subcategory from values if not already set
    if not result.subcategory and values:
        inferred = infer_subcategory_from_values(values)
        if inferred:
            result.subcategory = inferred
            detected["subcategory_inferred"] = inferred

    # Step 5: Extract semantic descriptors
    semantic_filters, remaining = extract_semantic_descriptors(remaining)
    if semantic_filters:
        detected["semantic"] = [f.source for f in semantic_filters]

    # Step 6: Build spec filters from extracted values (category-aware)
    # Note: result.spec_filters may already have filters from Step 3 (keyword-based type filters)

    for value in values:
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

    # Step 7: Clean up remaining text
    remaining = remove_noise_words(remaining)
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

    result.detected = detected

    return result


# =============================================================================
# INFER SUBCATEGORY FROM VALUES
# =============================================================================

def infer_subcategory_from_values(values: list[ExtractedValue]) -> str | None:
    """Infer likely subcategory from extracted values.

    Used when no explicit component type is specified.
    """
    value_types = {v.unit_type for v in values}

    # Strong indicators
    if "resistance" in value_types and "inductance" not in value_types and "capacitance" not in value_types:
        return "chip resistor - surface mount"
    if "capacitance" in value_types:
        return "multilayer ceramic capacitors mlcc - smd/smt"
    if "inductance" in value_types:
        return "inductors (smd)"

    return None
