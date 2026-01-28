"""Semantic descriptor extraction for smart query parsing."""

import re
from dataclasses import dataclass
from typing import Literal


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
    "low rds": [SemanticFilter("RDS(on)", "<", "50mOhm", "low rds")],
    "low rds(on)": [SemanticFilter("RDS(on)", "<", "50mOhm", "low rds(on)")],
    "low on-resistance": [SemanticFilter("RDS(on)", "<", "50mOhm", "low on-resistance")],

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

# Pre-sort descriptors by length (longest first) at module load time
# This ensures "ultra low power" matches before "low power"
_SORTED_DESCRIPTORS = sorted(SEMANTIC_DESCRIPTORS.keys(), key=len, reverse=True)


def extract_semantic_descriptors(query: str) -> tuple[list[SemanticFilter], str]:
    """Extract semantic descriptors from query.

    Args:
        query: The search query string

    Returns:
        Tuple of (list of SemanticFilter, remaining_query)
    """
    filters = []
    remaining = query
    query_lower = query.lower()

    for descriptor in _SORTED_DESCRIPTORS:
        if descriptor in query_lower:
            filters.extend(SEMANTIC_DESCRIPTORS[descriptor])
            # Remove from query (case-insensitive)
            pattern = re.compile(re.escape(descriptor), re.IGNORECASE)
            remaining = pattern.sub('', remaining).strip()
            remaining = re.sub(r'\s+', ' ', remaining)
            query_lower = remaining.lower()

    return filters, remaining


# Noise words to remove from queries
NOISE_WORDS = {
    'for', 'with', 'and', 'or', 'the', 'a', 'an', 'to', 'in', 'of',
    'type', 'chip', 'component', 'part', 'parts', 'electronic', 'electronics',
    'antenna',  # Common in RF connector context but not in part descriptions
    # Generic connector terms not used in JLCPCB descriptions
    # JLCPCB uses "Female"/"Male" instead of "Receptacle"/"Plug"
    'receptacle', 'jack', 'plug',
}


def remove_noise_words(query: str) -> str:
    """Remove common noise words from query.

    Args:
        query: The search query string

    Returns:
        Query with noise words removed
    """
    words = query.split()
    filtered = [w for w in words if w.lower() not in NOISE_WORDS]
    return ' '.join(filtered)
