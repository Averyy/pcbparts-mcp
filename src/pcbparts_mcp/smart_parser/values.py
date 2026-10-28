"""Value extraction patterns for smart query parsing."""

import re
from dataclasses import dataclass


@dataclass
class ExtractedValue:
    """A numeric value extracted from the query."""
    raw: str  # Original text (e.g., "10k", "100nF")
    value: float  # Parsed numeric value in base units
    unit_type: str  # "resistance", "capacitance", "voltage", etc.
    normalized: str  # Normalized form (e.g., "10kOhm", "100nF")


# Patterns for extracting values - order matters!

# Resistance: 10k, 100R, 4.7k, 1M, 100ohm, 4k7 (European notation)
_RES_EURO = re.compile(r'\b(\d+)([kKmMrR])(\d+)\b')
_RES_STD = re.compile(r'\b(\d+(?:\.\d+)?)\s*((?:meg|milliohm|[kKmM]ohm|ohm|[kKmMrR]))\b', re.IGNORECASE)

# Capacitance: 10uF, 100nF, 1pF, 4.7uF
_CAP = re.compile(r'\b(\d+(?:\.\d+)?)\s*(u[fF]|n[fF]|p[fF]|F)\b')

# Inductance: 10uH, 100nH, 1mH
_IND = re.compile(r'\b(\d+(?:\.\d+)?)\s*(u[hH]|n[hH]|m[hH]|[u]H|nH|mH)\b')

# Voltage: 25V, 50V, 3.3V, 5kV (but not in model numbers)
_VOLT = re.compile(r'\b(\d+(?:\.\d+)?)\s*([kK])?[vV]\b')

# Current: 5A, 10A, 100mA, 500mA, 10uA
# Require space or start before number to avoid matching model suffixes like "6.0A" in "SMBJ6.0A"
_CURR = re.compile(r'(?:^|(?<=\s))(\d+(?:\.\d+)?)\s*([u]?[mM]?)[aA]\b')

# Frequency: 8MHz, 32.768kHz, 2.4GHz
_FREQ = re.compile(r'\b(\d+(?:\.\d+)?)\s*([kKmMgG])?[hH][zZ]\b')

# Tolerance: 1%, 5%, 0.1%
_TOL = re.compile(r'\b(\d+(?:\.\d+)?)\s*%')

# Power: 1W, 0.25W, 100mW, 1/4W
_POWER_FRAC = re.compile(r'\b(\d+)/(\d+)\s*[wW]\b')
_POWER = re.compile(r'\b(\d+(?:\.\d+)?)\s*([mM])?[wW]\b')

# Temperature: 85C, -40C, 125C
_TEMP = re.compile(r'\b([+-]?\d+)\s*[C]?C\b', re.IGNORECASE)

# Pin count: 16 pin, 8-pin, 24pin
_PINS = re.compile(r'\b(\d+)\s*-?pins?\b', re.IGNORECASE)

# Dimensions: 6x6mm, 3.5x3.5mm
_DIM = re.compile(r'\b(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)\s*(?:mm)?\b')

# Pitch (connector spacing): 2.54mm pitch, 5.08mm, 1.27mm pitch
# Match patterns like "2.54mm", "5.08mm pitch", "1.27 mm"
# Common pitches: 1.0mm, 1.27mm, 2.0mm, 2.54mm, 3.5mm, 3.81mm, 5.0mm, 5.08mm
_PITCH = re.compile(r'\b(\d+(?:\.\d+)?)\s*mm(?:\s+pitch)?\b', re.IGNORECASE)

# Position count for connectors: 2-pos, 2 position, 2-position, 2P
_POSITION = re.compile(r'\b(\d+)\s*-?\s*(?:pos(?:ition)?|way|P)\b', re.IGNORECASE)

# Header pin structure: 1x7, 2x20, 1X40 (rows x pins per row)
_PIN_STRUCTURE = re.compile(r'\b([12])\s*[xX]\s*(\d+)\b')


def _parse_resistance_value(match: re.Match) -> tuple[float, str]:
    """Parse resistance match to (ohms, normalized_string)."""
    groups = match.groups()
    suffix = groups[1]
    value_str = f"{groups[0]}.{groups[2]}" if len(groups) == 3 else groups[0]
    value = float(value_str)
    if len(groups) == 3:
        scale = {"k": 1e3, "K": 1e3, "M": 1e6, "m": 1e-3, "r": 1, "R": 1}[suffix]
        normalized_suffix = "k" if suffix in ("k", "K") else "R" if suffix in ("r", "R") else suffix
        return value * scale, f"{groups[0]}{normalized_suffix}{groups[2]}"
    if suffix.lower() == "milliohm" or suffix.startswith("m") and suffix.lower() != "meg":
        return value * 1e-3, f"{value_str}mOhm"
    if suffix.lower() == "meg" or suffix.startswith("M"):
        return value * 1e6, f"{value_str}MOhm"
    if suffix.lower().startswith("k"):
        return value * 1e3, f"{value_str}kOhm"
    return value, f"{value_str}Ohm"


def normalize_value_notation(query: str) -> str:
    """Normalize electrical notation before extraction; callers retain the original query."""
    query = query.replace("µ", "u").replace("μ", "u").replace("Ω", "ohm")
    unit = "uH" if re.search(r"\b(inductor|inductors|coil|choke)\b", query, re.IGNORECASE) else "uF"
    query = re.sub(r"(?<![\w-])(\d+)u(\d+)(?![\w-])", rf"\1.\2{unit}", query)
    return re.sub(r"(?<![\w-])(\d+)[vV](\d+)(?![\w-])", r"\1.\2V", query)


def extract_values(query: str, *, connector_context: bool = False) -> tuple[list[ExtractedValue], str]:
    """Extract all numeric values from query, return (values, remaining_query).

    Args:
        query: The search query string

    Returns:
        Tuple of (list of ExtractedValue, remaining_query with values removed)
    """
    query = normalize_value_notation(query)
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
        # Bare farads must not consume a hyphenated model suffix such as ESP-12F.
        if match.group(2) == "F" and match.start() and query[match.start() - 1] == "-":
            continue
        value = float(match.group(1))
        suffix = match.group(2).lower()
        if suffix == 'uf':
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
        if suffix in ('uh', 'h'):
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
        if prefix == 'u':
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

    # Pin count (normalize to "XP" format to match database values like "8P", "16P")
    pin_matches = list(_PINS.finditer(query))
    if connector_context:
        pin_matches.extend(re.finditer(r'\b(\d+)\s*-?\s*contacts?\b', query, re.IGNORECASE))
    for match in pin_matches:
        pins = int(match.group(1))
        extractions.append((match.start(), match.end(), ExtractedValue(
            raw=match.group(0),
            value=pins,
            unit_type="pin_count",
            normalized=f"{pins}P"
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
    # This maps to the "Pin Structure" attribute (e.g., "1x16P"), not "Number of Pins"
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
            unit_type="pin_structure",  # Maps to "Pin Structure" attribute
            normalized=f"{rows}x{pins_per_row}P"
        )))

    # Pitch (connector spacing) - extract common connector pitches
    # Only extract specific common pitch values to avoid false positives
    COMMON_PITCHES = {0.5, 0.8, 1.0, 1.25, 1.27, 2.0, 2.54, 3.5, 3.81, 5.0, 5.08, 7.62}
    for match in _PITCH.finditer(query):
        # Skip if already matched by another pattern
        if any(s <= match.start() < e for s, e, _ in extractions):
            continue
        pitch_val = float(match.group(1))
        # Only extract if it's a known connector pitch value
        if pitch_val in COMMON_PITCHES or (connector_context and pitch_val > 0):
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

        # Skip if dimensions are unreasonably large (>100) - likely pixel counts, not mm
        # Display resolutions like "128x64" are handled in parser after subcategory is detected
        if x > 100 or y > 100:
            continue  # This is likely a display resolution, not a physical dimension

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
