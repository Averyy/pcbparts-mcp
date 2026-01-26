"""Alternative component finding with spec-aware compatibility checking.

This module provides intelligent alternative finding that:
1. Matches parts by primary spec value (not just subcategory)
2. Verifies compatibility using same_or_better rules
3. Scores and ranks alternatives by usefulness
4. Returns verified alternatives for supported categories, similar_parts for unsupported
"""

import re
from typing import Any, Callable

from .key_attributes import KEY_ATTRIBUTES


# =============================================================================
# PRE-COMPILED REGEX PATTERNS
# =============================================================================
# Pre-compile for better performance - these are called many times per request.

_VOLTAGE_PATTERN = re.compile(r"([\d.]+)\s*V", re.IGNORECASE)
_TOLERANCE_PATTERN = re.compile(r"([\d.]+)\s*%")
_POWER_FRACTION_PATTERN = re.compile(r"(\d+)/(\d+)\s*W", re.IGNORECASE)
_POWER_MW_PATTERN = re.compile(r"([\d.]+)\s*mW", re.IGNORECASE)
_POWER_W_PATTERN = re.compile(r"([\d.]+)\s*W", re.IGNORECASE)
_CURRENT_UA_PATTERN = re.compile(r"([\d.]+)\s*[uµ]A", re.IGNORECASE)
_CURRENT_MA_PATTERN = re.compile(r"([\d.]+)\s*mA", re.IGNORECASE)
_CURRENT_A_PATTERN = re.compile(r"([\d.]+)\s*A", re.IGNORECASE)
_RESISTANCE_PATTERN = re.compile(r"([\d.]+)\s*([kKmM])?")
_CAPACITANCE_PATTERN = re.compile(r"([\d.]+)\s*([pnuµm])?", re.IGNORECASE)
_INDUCTANCE_PATTERN = re.compile(r"([\d.]+)\s*([nuµm])?", re.IGNORECASE)
_FREQUENCY_PATTERN = re.compile(r"([\d.]+)\s*([kKmMgG])?")
_IMPEDANCE_AT_FREQ_PATTERN = re.compile(
    r"([\d.]+)\s*([kKmM])?Ohm\s*@\s*([\d.]+)\s*([kKmMgG])?Hz", re.IGNORECASE
)
_DECIBEL_PATTERN = re.compile(r"([\d.]+)\s*dB", re.IGNORECASE)


# =============================================================================
# SPEC PARSERS
# =============================================================================
# Each parser returns a float in base units for comparison, or None if unparseable.


def parse_voltage(s: str) -> float | None:
    """Parse voltage: '25V' -> 25, '6.3V' -> 6.3, '3.3V' -> 3.3"""
    if not s:
        return None
    match = _VOLTAGE_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_tolerance(s: str) -> float | None:
    """Parse tolerance: '±1%' -> 1, '±10%' -> 10, '1%' -> 1"""
    if not s:
        return None
    match = _TOLERANCE_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_power(s: str) -> float | None:
    """Parse power in watts: '100mW' -> 0.1, '1/4W' -> 0.25, '0.25W' -> 0.25"""
    if not s:
        return None
    # Handle fraction format: 1/4W, 1/10W
    match = _POWER_FRACTION_PATTERN.search(s)
    if match:
        return float(match.group(1)) / float(match.group(2))
    # Handle mW
    match = _POWER_MW_PATTERN.search(s)
    if match:
        return float(match.group(1)) / 1000
    # Handle W
    match = _POWER_W_PATTERN.search(s)
    if match:
        return float(match.group(1))
    return None


def parse_current(s: str) -> float | None:
    """Parse current in amps: '2A' -> 2, '500mA' -> 0.5, '100uA' -> 0.0001"""
    if not s:
        return None
    match = _CURRENT_UA_PATTERN.search(s)
    if match:
        return float(match.group(1)) / 1_000_000
    match = _CURRENT_MA_PATTERN.search(s)
    if match:
        return float(match.group(1)) / 1000
    match = _CURRENT_A_PATTERN.search(s)
    if match:
        return float(match.group(1))
    return None


def parse_resistance(s: str) -> float | None:
    """Parse resistance in ohms: '10kΩ' -> 10000, '10K' -> 10000, '4.7MΩ' -> 4700000"""
    if not s:
        return None
    # Normalize: remove Ω/ohm, handle k/K/M suffixes
    s = s.replace("Ω", "").replace("ohm", "").strip()
    match = _RESISTANCE_PATTERN.search(s)
    if not match:
        return None
    value = float(match.group(1))
    suffix = (match.group(2) or "").upper()
    if suffix == "K":
        return value * 1000
    elif suffix == "M":
        return value * 1_000_000
    return value


def parse_capacitance(s: str) -> float | None:
    """Parse capacitance in farads: '100nF' -> 1e-7, '10uF' -> 1e-5, '1pF' -> 1e-12"""
    if not s:
        return None
    s = s.replace("F", "").strip()
    match = _CAPACITANCE_PATTERN.search(s)
    if not match:
        return None
    value = float(match.group(1))
    suffix = (match.group(2) or "").lower()
    if suffix == "p":
        return value * 1e-12
    elif suffix == "n":
        return value * 1e-9
    elif suffix in ("u", "µ"):
        return value * 1e-6
    elif suffix == "m":
        return value * 1e-3
    return value  # Assume farads if no suffix


def parse_inductance(s: str) -> float | None:
    """Parse inductance in henries: '10uH' -> 1e-5, '100nH' -> 1e-7, '1mH' -> 1e-3"""
    if not s:
        return None
    s = s.replace("H", "").strip()
    match = _INDUCTANCE_PATTERN.search(s)
    if not match:
        return None
    value = float(match.group(1))
    suffix = (match.group(2) or "").lower()
    if suffix == "n":
        return value * 1e-9
    elif suffix in ("u", "µ"):
        return value * 1e-6
    elif suffix == "m":
        return value * 1e-3
    return value  # Assume henries if no suffix


def parse_frequency(s: str) -> float | None:
    """Parse frequency in Hz: '8MHz' -> 8e6, '32.768kHz' -> 32768"""
    if not s:
        return None
    s = s.replace("Hz", "").strip()
    match = _FREQUENCY_PATTERN.search(s)
    if not match:
        return None
    value = float(match.group(1))
    suffix = (match.group(2) or "").upper()
    if suffix == "K":
        return value * 1e3
    elif suffix == "M":
        return value * 1e6
    elif suffix == "G":
        return value * 1e9
    return value


def parse_decibels(s: str) -> float | None:
    """Parse sound pressure level in dB: '85dB' -> 85, '90 dB' -> 90"""
    if not s:
        return None
    match = _DECIBEL_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_impedance_at_freq(s: str) -> tuple[float, float] | None:
    """Parse impedance @ frequency: '600Ω @ 100MHz' -> (600, 100e6)
    Returns (impedance_ohms, frequency_hz) tuple for comparison.
    """
    if not s:
        return None
    # Normalize: Ω, Ohm, ohm -> unified
    s = s.replace("Ω", "Ohm").replace("ohm", "Ohm")
    # Pattern: <impedance><unit> @ <frequency><unit>
    match = _IMPEDANCE_AT_FREQ_PATTERN.search(s)
    if not match:
        return None

    # Parse impedance
    imp_value = float(match.group(1))
    imp_suffix = (match.group(2) or "").upper()
    if imp_suffix == "K":
        imp_value *= 1000
    elif imp_suffix == "M":
        imp_value *= 1_000_000

    # Parse frequency
    freq_value = float(match.group(3))
    freq_suffix = (match.group(4) or "").upper()
    if freq_suffix == "K":
        freq_value *= 1e3
    elif freq_suffix == "M":
        freq_value *= 1e6
    elif freq_suffix == "G":
        freq_value *= 1e9

    return (imp_value, freq_value)


def impedance_at_freq_match(orig: str, cand: str) -> bool:
    """Check if two 'Impedance @ Frequency' values match.
    Both impedance AND frequency must match (within 2% each).
    """
    orig_parsed = parse_impedance_at_freq(orig)
    cand_parsed = parse_impedance_at_freq(cand)

    if orig_parsed is None or cand_parsed is None:
        # Can't parse, fall back to normalized string match
        return orig.replace("Ω", "Ohm").lower() == cand.replace("Ω", "Ohm").lower()

    orig_imp, orig_freq = orig_parsed
    cand_imp, cand_freq = cand_parsed

    # Both impedance and frequency must be within 2%
    if orig_imp == 0 or orig_freq == 0:
        return cand_imp == orig_imp and cand_freq == orig_freq

    imp_ok = abs(orig_imp - cand_imp) / orig_imp < 0.02
    freq_ok = abs(orig_freq - cand_freq) / orig_freq < 0.02

    return imp_ok and freq_ok


# =============================================================================
# SPEC PARSERS MAPPING
# =============================================================================
# Map spec names to their parser functions. "special" means use custom logic.

SPEC_PARSERS: dict[str, Callable[[str], float | None] | str | None] = {
    # Voltages
    "Voltage Rating": parse_voltage,
    "Voltage - DC Reverse(Vr)": parse_voltage,
    "Drain to Source Voltage": parse_voltage,
    "Collector - Emitter Voltage VCEO": parse_voltage,
    "Reverse Stand-Off Voltage (Vrwm)": parse_voltage,
    "Clamping Voltage": parse_voltage,
    "Isolation Voltage(Vrms)": parse_voltage,
    "Voltage - Max": parse_voltage,
    "Output Voltage": parse_voltage,
    "Voltage Dropout": parse_voltage,
    "Zener Voltage(Nom)": parse_voltage,
    "Voltage Rating (DC)": parse_voltage,
    "Voltage Rating (Max)": parse_voltage,
    "Reverse Voltage": parse_voltage,
    "Voltage(AC)": parse_voltage,
    "Voltage Rating (AC)": parse_voltage,
    "Voltage Rating - DC": parse_voltage,
    "Coil Voltage": parse_voltage,
    "Switching Voltage(Max)": parse_voltage,
    "Load Voltage": parse_voltage,
    "Varistor Voltage": parse_voltage,
    "Peak off - state voltage(Vdrm)": parse_voltage,
    "Trigger Voltage": parse_voltage,
    "Rated Voltage (Max)": parse_voltage,
    "Collector-Emitter Breakdown Voltage (Vces)": parse_voltage,
    "Vce Saturation(VCE(sat))": parse_voltage,
    "Voltage - Forward(Vf@If)": parse_voltage,
    "Voltage - DC Spark Over": parse_voltage,
    "Voltage - Supply": parse_voltage,  # For buzzers, etc.
    # Tolerances (percentage-based)
    "Tolerance": parse_tolerance,
    "Frequency Stability": parse_tolerance,  # ±ppm is like tolerance
    # Power
    "Power(Watts)": parse_power,
    "Pd - Power Dissipation": parse_power,
    "Peak Pulse Power": parse_power,
    "Rated Power": parse_power,
    # Currents
    "Current - Continuous Drain(Id)": parse_current,
    "Current - Collector(Ic)": parse_current,
    "Current - Rectified": parse_current,
    "Current Rating": parse_current,
    "Current - Saturation(Isat)": parse_current,
    "Current - Saturation (Isat)": parse_current,  # Variant with space
    "Output Current": parse_current,
    "Hold Current": parse_current,
    "Trip Current": parse_current,
    "Contact Current": parse_current,
    "Contact Rating": parse_current,
    "Switching Current(Max)": parse_current,
    "Load Current": parse_current,
    "Current - Average Rectified": parse_current,
    "Drain Current (Idss)": parse_current,
    "Output Current(Max)": parse_current,
    "Impulse Discharge Current": parse_current,
    "Peak Pulse Current-Ipp (10/1000us)": parse_current,
    "Current Rating (Max)": parse_current,
    "Average Rectified Current": parse_current,
    # Resistance
    "DC Resistance(DCR)": parse_resistance,
    "RDS(on)": parse_resistance,
    "Resistance": parse_resistance,
    "Resistance @ 25℃": parse_resistance,
    "Cell Resistance @ Illuminance": parse_resistance,
    # Capacitance
    "Capacitance": parse_capacitance,
    "Load Capacitance": parse_capacitance,
    # Inductance
    "Inductance": parse_inductance,
    # Frequency
    "Frequency": parse_frequency,
    # Special handling
    "Impedance @ Frequency": "special",  # Uses impedance_at_freq_match()
    # String-match specs (no parser - use exact match)
    "Temperature Coefficient": None,
    "Illumination Color": None,
    "type": None,
    "Type": None,
    "Output Type": None,
    "Peak Wavelength": None,
    "FET Type": None,
    "B Constant (25℃/100℃)": None,
    "Number of Positions": None,
    "Number of Pins": None,
    "Number of Positions or Pins": None,
    "Number of Rows": None,
    "Pitch": None,
    "Connector Type": None,
    "Gender": None,
    "Pins Structure": None,
    "Circuit": None,
    "Contact Form": None,
    "Mounting Type": None,
    "Self Lock / No Lock": None,
    "Positions": None,
    "Number of Poles Per Deck": None,
    "Rated Functioning Temperature": None,
    "Number of Resistors": None,
    "Number of Capacitors": None,
    "Number of Lines": None,
    "Number of Forward Channels": None,
    "Number of Reverse Channels": None,
    "Number of Poles": None,
    "Number of Turns": None,
    "Number of Coils": None,
    "Impedance": None,
    "Driver Circuitry": None,
    "Ratings": None,
    "Data Rate": None,
    "Data Rate(Max)": None,
    "Color": None,
    "Number of Segments": None,
    "Direction": None,
    "Encoder Type": None,
    "Energy": None,
    "Sound Pressure Level": parse_decibels,
}

# Specs that use exact string matching (case-insensitive)
STRING_MATCH_SPECS = {
    "Temperature Coefficient",
    "Illumination Color",
    "type",
    "Type",
    "Output Type",
    "Peak Wavelength",
    "FET Type",
    "B Constant (25℃/100℃)",
    # Connectors
    "Number of Positions",
    "Number of Pins",
    "Number of Positions or Pins",
    "Number of Rows",
    "Pitch",
    "Connector Type",
    "Gender",
    "Pins Structure",
    # Switches
    "Circuit",
    "Contact Form",
    "Mounting Type",
    "Self Lock / No Lock",
    "Positions",
    "Number of Poles Per Deck",
    # Fuses
    "Rated Functioning Temperature",
    # Arrays/Networks
    "Number of Resistors",
    "Number of Capacitors",
    "Number of Lines",
    "Number of Forward Channels",
    "Number of Reverse Channels",
    "Number of Poles",
    "Number of Turns",
    "Number of Coils",
    # Audio/RF
    "Impedance",
    "Driver Circuitry",
    # Capacitors
    "Ratings",  # X1, X2, Y1, Y2 safety class
    # Data rates (string format varies too much)
    "Data Rate",
    "Data Rate(Max)",
    # Opto/misc
    "Color",
    "Number of Segments",
    "Direction",
    "Encoder Type",
}


# =============================================================================
# COMPATIBILITY RULES
# =============================================================================
# Defines what makes a part a valid alternative for each supported subcategory.
# - primary: The main spec to search by
# - must_match: Specs that must be exactly equal
# - same_or_better: Specs where candidate must be >= or <= original

COMPATIBILITY_RULES: dict[str, dict[str, Any]] = {
    # ============== RESISTORS ==============
    "Chip Resistor - Surface Mount": {
        "primary": "Resistance",
        "same_or_better": {
            "Tolerance": "lower",  # ±1% can replace ±5%
            "Power(Watts)": "higher",  # 1/4W can replace 1/10W
        },
    },
    "Through Hole Resistors": {
        "primary": "Resistance",
        "same_or_better": {
            "Tolerance": "lower",
            "Power(Watts)": "higher",
        },
    },
    "Current Sense Resistors / Shunt Resistors": {
        "primary": "Resistance",
        "same_or_better": {
            "Tolerance": "lower",
            "Power(Watts)": "higher",
        },
    },
    "Resistor Networks, Arrays": {
        "primary": "Resistance",
        "must_match": ["Number of Resistors"],
        "same_or_better": {
            "Tolerance": "lower",
            "Power(Watts)": "higher",
        },
    },
    "Potentiometers, Variable Resistors": {
        "primary": "Resistance",
        "must_match": ["Number of Turns"],
        "same_or_better": {
            "Power(Watts)": "higher",
            "Tolerance": "lower",
        },
    },
    # ============== CAPACITORS ==============
    "Multilayer Ceramic Capacitors MLCC - SMD/SMT": {
        "primary": "Capacitance",
        "must_match": ["Temperature Coefficient"],  # X7R != X5R
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Multilayer Ceramic Capacitors MLCC - Leaded": {
        "primary": "Capacitance",
        "must_match": ["Temperature Coefficient"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Through Hole Ceramic Capacitors": {
        "primary": "Capacitance",
        "must_match": ["Temperature Coefficient"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Aluminum Electrolytic Capacitors - SMD": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Aluminum Electrolytic Capacitors - Leaded": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Aluminum Electrolytic Capacitors (Can - Screw Terminals)": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Tantalum Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Film Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Polypropylene Film Capacitors (CBB)": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Polymer Aluminum Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Hybrid Aluminum Electrolytic Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Horn-Type Electrolytic Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    "Niobium Oxide Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Mica and PTFE Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        },
    },
    "Safety Capacitors": {
        "primary": "Capacitance",
        "must_match": ["Ratings"],  # X1, X2, Y1, Y2 class
        "same_or_better": {
            "Voltage(AC)": "higher",
            "Tolerance": "lower",
        },
    },
    "Capacitor Networks, Arrays": {
        "primary": "Capacitance",
        "must_match": ["Number of Capacitors"],
        "same_or_better": {
            "Voltage Rating": "higher",
        },
    },
    # ============== INDUCTORS ==============
    "Inductors (SMD)": {
        "primary": "Inductance",
        "same_or_better": {
            "Current Rating": "higher",
            "Current - Saturation (Isat)": "higher",
            "DC Resistance(DCR)": "lower",
        },
    },
    "Power Inductors": {
        "primary": "Inductance",
        "same_or_better": {
            "Current Rating": "higher",
            "Current - Saturation(Isat)": "higher",
            "DC Resistance(DCR)": "lower",
        },
    },
    "Color Ring Inductors / Through Hole Inductors": {
        "primary": "Inductance",
        "same_or_better": {
            "Current Rating": "higher",
            "DC Resistance(DCR)": "lower",
        },
    },
    "Wireless Charging Coils": {
        "primary": "Inductance",
        "must_match": ["Number of Coils"],
        "same_or_better": {
            "DC Resistance(DCR)": "lower",
        },
    },
    # ============== FERRITE BEADS ==============
    "Ferrite Beads": {
        "primary": "Impedance @ Frequency",
        "same_or_better": {
            "Current Rating": "higher",
            "DC Resistance(DCR)": "lower",
        },
    },
    "Common Mode Filters": {
        "primary": "Impedance @ Frequency",
        "must_match": ["Number of Lines"],
        "same_or_better": {
            "Current Rating": "higher",
            "Voltage Rating - DC": "higher",
        },
    },
    # ============== MOSFETs ==============
    "MOSFETs": {
        "primary": "Drain to Source Voltage",
        "same_or_better": {
            "Drain to Source Voltage": "higher",
            "Current - Continuous Drain(Id)": "higher",
            "RDS(on)": "lower",
        },
    },
    "Silicon Carbide Field Effect Transistor (MOSFET)": {
        "primary": "Drain to Source Voltage",
        "same_or_better": {
            "Drain to Source Voltage": "higher",
            "Current - Continuous Drain(Id)": "higher",
            "RDS(on)": "lower",
        },
    },
    # ============== JFETs ==============
    "JFETs": {
        "primary": "FET Type",
        "must_match": ["FET Type"],
        "same_or_better": {
            "Drain Current (Idss)": "higher",
            "RDS(on)": "lower",
        },
    },
    # ============== BJTs ==============
    "Bipolar (BJT)": {
        "primary": "type",
        "must_match": ["type"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
            "Current - Collector(Ic)": "higher",
        },
    },
    "Darlington Transistors": {
        "primary": "Type",
        "must_match": ["Type"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
            "Current - Collector(Ic)": "higher",
        },
    },
    "Digital Transistors": {
        "primary": "type",
        "must_match": ["type"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
        },
    },
    "Phototransistors": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
            "Current - Collector(Ic)": "higher",
        },
    },
    # ============== IGBTs ==============
    "IGBT Transistors / Modules": {
        "primary": "Collector-Emitter Breakdown Voltage (Vces)",
        "same_or_better": {
            "Collector-Emitter Breakdown Voltage (Vces)": "higher",
            "Current - Collector(Ic)": "higher",
            "Vce Saturation(VCE(sat))": "lower",
        },
    },
    # ============== DIODES ==============
    "Schottky Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
            "Voltage - Forward(Vf@If)": "lower",
        },
    },
    "Switching Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    "Zener Diodes": {
        "primary": "Zener Voltage(Nom)",
        "must_match": ["Zener Voltage(Nom)"],
        "same_or_better": {
            "Pd - Power Dissipation": "higher",
        },
    },
    "Diodes - General Purpose": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    "Diodes - Rectifiers - Fast Recovery": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Average Rectified": "higher",
        },
    },
    "Fast Recovery / High Efficiency Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    "Bridge Rectifiers": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
            "Voltage - Forward(Vf@If)": "lower",
        },
    },
    "Super Barrier Rectifiers (SBR)": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
            "Voltage - Forward(Vf@If)": "lower",
        },
    },
    "Avalanche Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    "High Effic Rectifier": {
        "primary": "Reverse Voltage",
        "same_or_better": {
            "Reverse Voltage": "higher",
            "Average Rectified Current": "higher",
        },
    },
    "SiC Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        },
    },
    # ============== ESD/TVS PROTECTION ==============
    "ESD and Surge Protection (TVS/ESD)": {
        "primary": "Reverse Stand-Off Voltage (Vrwm)",
        "same_or_better": {
            "Clamping Voltage": "lower",
            "Peak Pulse Power": "higher",
        },
    },
    "Varistors": {
        "primary": "Varistor Voltage",
        "must_match": ["Varistor Voltage"],
        "same_or_better": {
            "Clamping Voltage": "lower",
            "Energy": "higher",
        },
    },
    "Gas Discharge Tube Arresters (GDT)": {
        "primary": "Voltage - DC Spark Over",
        "must_match": ["Number of Poles"],
        "same_or_better": {
            "Impulse Discharge Current": "higher",
        },
    },
    "Semiconductor Discharge Tubes (TSS)": {
        "primary": "Peak off - state voltage(Vdrm)",
        "same_or_better": {
            "Peak Pulse Current-Ipp (10/1000us)": "higher",
        },
    },
    "LED Protection": {
        "primary": "Trigger Voltage",
        "must_match": ["Trigger Voltage"],
        "same_or_better": {
            "Hold Current": "higher",
        },
    },
    # ============== FUSES ==============
    "Resettable Fuses": {
        "primary": "Hold Current",
        "must_match": ["Hold Current", "Trip Current"],
        "same_or_better": {
            "Voltage - Max": "higher",
        },
    },
    "Automotive Fuses": {
        "primary": "Current Rating",
        "must_match": ["Current Rating", "Type"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
        },
    },
    "Thermal Fuses (TCO)": {
        "primary": "Rated Functioning Temperature",
        "must_match": ["Rated Functioning Temperature"],
        "same_or_better": {
            "Current Rating": "higher",
            "Voltage Rating": "higher",
        },
    },
    "Disposable fuses": {
        "primary": "Current Rating",
        "must_match": ["Current Rating", "Type"],
        "same_or_better": {
            "Voltage Rating (AC)": "higher",
        },
    },
    # ============== THERMISTORS ==============
    "NTC Thermistors": {
        "primary": "Resistance @ 25℃",
        "must_match": ["Resistance @ 25℃", "B Constant (25℃/100℃)"],
    },
    "PTC Thermistors": {
        "primary": "Resistance @ 25℃",
        "must_match": ["Resistance @ 25℃"],
    },
    # ============== LEDs ==============
    "LED Indication - Discrete": {
        "primary": "Illumination Color",
        "must_match": ["Illumination Color"],
    },
    "LED - High Brightness": {
        "primary": "Illumination Color",
        "must_match": ["Illumination Color"],
    },
    "Infrared (IR) LEDs": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],
    },
    "Ultraviolet LEDs (UVLED)": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],
    },
    "Light Bars, Arrays": {
        "primary": "Color",
        "must_match": ["Color", "Number of Segments"],
    },
    # ============== OPTOCOUPLERS ==============
    "Transistor, Photovoltaic Output Optoisolators": {
        "primary": "Isolation Voltage(Vrms)",
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
        },
    },
    "Logic Output Optoisolators": {
        "primary": "Isolation Voltage(Vrms)",
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            "Data Rate": "higher",
        },
    },
    "Triac, SCR Output Optoisolators": {
        "primary": "Load Voltage",
        "same_or_better": {
            "Load Voltage": "higher",
            "Load Current": "higher",
            "Isolation Voltage(Vrms)": "higher",
        },
    },
    "Gate Drive Optocoupler": {
        "primary": "Isolation Voltage(Vrms)",
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            "Output Current(Max)": "higher",
        },
    },
    "Photointerrupters - Slot Type - Transistor Output": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],
        "same_or_better": {
            "Load Voltage": "higher",
            "Output Current": "higher",
        },
    },
    "Reflective Optical Interrupters": {
        "primary": "Output Type",
        "must_match": ["Output Type"],
        "same_or_better": {
            "Current - Collector(Ic)": "higher",
        },
    },
    "Photoresistors": {
        "primary": "Cell Resistance @ Illuminance",
        "same_or_better": {
            "Voltage - Max": "higher",
        },
    },
    # ============== TIMING ==============
    "Crystals": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Load Capacitance"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    "Crystal Oscillators": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    "Ceramic Resonators": {
        "primary": "Frequency",
        "must_match": ["Frequency"],
    },
    "SAW Resonators": {
        "primary": "Frequency",
        "must_match": ["Frequency"],
    },
    "Temperature Compensated Crystal Oscillators (TCXO)": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    "Voltage-Controlled Crystal Oscillators (VCXOs)": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    "Oven Controlled Crystal Oscillators (OCXOs)": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        },
    },
    # ============== VOLTAGE REGULATORS ==============
    "Voltage Regulators - Linear, Low Drop Out (LDO) Regulators": {
        "primary": "Output Voltage",
        "must_match": ["Output Voltage"],
        "same_or_better": {
            "Output Current": "higher",
            "Voltage Dropout": "lower",
        },
    },
    "Voltage Reference": {
        "primary": "Output Voltage",
        "must_match": ["Output Voltage"],
        "same_or_better": {
            "Tolerance": "lower",
            "Temperature Coefficient": "lower",
        },
    },
    # ============== DIGITAL ISOLATORS ==============
    "Digital Isolators": {
        "primary": "Number of Forward Channels",
        "must_match": ["Number of Forward Channels", "Number of Reverse Channels"],
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            "Data Rate(Max)": "higher",
        },
    },
    # ============== SWITCHES ==============
    "Tactile Switches": {
        "primary": "Mounting Type",
        "must_match": ["Mounting Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Contact Current": "higher",
        },
    },
    "DIP Switches": {
        "primary": "Number of Positions",
        "must_match": ["Number of Positions", "Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "Slide Switches": {
        "primary": "Circuit",
        "must_match": ["Circuit", "Mounting Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "Toggle Switches": {
        "primary": "Circuit",
        "must_match": ["Circuit"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
            "Current Rating": "higher",
        },
    },
    "Rocker Switches": {
        "primary": "Circuit",
        "must_match": ["Circuit"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
            "Current Rating": "higher",
        },
    },
    "Pushbutton Switches": {
        "primary": "Self Lock / No Lock",
        "must_match": ["Self Lock / No Lock"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Contact Current": "higher",
        },
    },
    "Rotary Switches": {
        "primary": "Positions",
        "must_match": ["Positions", "Number of Poles Per Deck"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
            "Current Rating": "higher",
        },
    },
    # ============== RELAYS ==============
    "Power Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Contact Rating": "higher",
            "Switching Voltage(Max)": "higher",
        },
    },
    "Signal Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Contact Rating": "higher",
            "Switching Current(Max)": "higher",
        },
    },
    "Automotive Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Contact Rating": "higher",
            "Switching Voltage(Max)": "higher",
        },
    },
    "Reed Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Switching Voltage(Max)": "higher",
            "Switching Current(Max)": "higher",
        },
    },
    "Solid State Relays (MOS Output)": {
        "primary": "Load Voltage",
        "same_or_better": {
            "Load Voltage": "higher",
            "Load Current": "higher",
            "RDS(on)": "lower",
        },
    },
    "Solid State Relays (Triac Output)": {
        "primary": "Load Voltage",
        "must_match": ["Contact Form"],
        "same_or_better": {
            "Load Voltage": "higher",
            "Load Current": "higher",
        },
    },
    # ============== CONNECTORS ==============
    "Pin Headers": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Number of Pins", "Number of Rows"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    "Female Headers": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Number of Positions", "Number of Rows"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    "Screw Terminal Blocks": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Number of Positions or Pins"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        },
    },
    "Barrier Terminal Blocks": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Pitch", "Number of Positions or Pins"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        },
    },
    "Pluggable System Terminal Block": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Pitch", "Number of Positions or Pins"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        },
    },
    "USB Connectors": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Gender"],
    },
    "HDMI Connectors": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Gender"],
    },
    "DisplayPort (DP) Connector": {
        "primary": "Connector Type",
        "must_match": ["Connector Type"],
    },
    "Audio Connectors": {
        "primary": "Connector Type",
        "must_match": ["Connector Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "Coaxial Connectors (RF)": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Impedance"],
    },
    "IDC Connectors": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Number of Positions or Pins", "Pitch"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    "Wire To Board Connector": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Pins Structure"],
        "same_or_better": {
            "Current Rating": "higher",
            "Voltage Rating": "higher",
        },
    },
    "Circular Connectors & Cable Connectors": {
        "primary": "Number of Pins",
        "must_match": ["Number of Pins", "Gender"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "XLR (Cannon) Connectors": {
        "primary": "Number of Pins",
        "must_match": ["Number of Pins", "Gender"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "DIN41612 Connectors": {
        "primary": "Number of Pins",
        "must_match": ["Pitch", "Number of Pins", "Number of Rows"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    "Shunts, Jumpers": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Number of Positions"],
        "same_or_better": {
            "Current Rating": "higher",
        },
    },
    # ============== AUDIO ==============
    "Speakers": {
        "primary": "Impedance",
        "must_match": ["Impedance"],
        "same_or_better": {
            "Rated Power": "higher",
        },
    },
    "Buzzers": {
        "primary": "Voltage - Supply",
        "must_match": ["Driver Circuitry"],
        "same_or_better": {
            "Sound Pressure Level": "higher",
        },
    },
    "Microphones": {
        "primary": "Direction",
        "must_match": ["Direction"],
    },
    "MEMS Microphones": {
        "primary": "Output Type",
        "must_match": ["Output Type"],
    },
    # ============== MISC ==============
    "Vibration Motors": {
        "primary": "Voltage Rating",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        },
    },
    "Rotary Encoders": {
        "primary": "Encoder Type",
        "must_match": ["Encoder Type"],
        "same_or_better": {
            "Rated Voltage (Max)": "higher",
            "Current Rating (Max)": "higher",
        },
    },
}


# =============================================================================
# COMPATIBILITY CHECKING FUNCTIONS
# =============================================================================


def _values_match(orig_val: str, cand_val: str, spec: str) -> bool:
    """Check if two spec values match (for must_match rules)."""
    # Special handler for complex formats
    if spec == "Impedance @ Frequency":
        return impedance_at_freq_match(orig_val, cand_val)

    # String-based specs: exact match (case-insensitive)
    if spec in STRING_MATCH_SPECS:
        return orig_val.strip().lower() == cand_val.strip().lower()

    # Numeric specs: parse and compare with tolerance
    parser = SPEC_PARSERS.get(spec)
    if parser and parser != "special" and callable(parser):
        orig_parsed = parser(orig_val)
        cand_parsed = parser(cand_val)
        if orig_parsed is None or cand_parsed is None:
            return True  # Can't parse, allow through
        # 2% tolerance for matching (handles rounding differences in display)
        if orig_parsed == 0:
            return cand_parsed == 0
        return abs(orig_parsed - cand_parsed) / abs(orig_parsed) < 0.02

    # Fallback: string match
    return orig_val.strip().lower() == cand_val.strip().lower()


def _spec_ok(orig_val: str, cand_val: str, spec: str, direction: str) -> bool:
    """Check if candidate spec meets same_or_better requirement."""
    parser = SPEC_PARSERS.get(spec)
    if not parser or parser == "special" or not callable(parser):
        return True  # Can't parse, allow through

    orig_parsed = parser(orig_val)
    cand_parsed = parser(cand_val)

    if orig_parsed is None or cand_parsed is None:
        return True  # Can't parse, allow through

    if direction == "higher":
        return cand_parsed >= orig_parsed * 0.98  # 2% tolerance
    elif direction == "lower":
        return cand_parsed <= orig_parsed * 1.02  # 2% tolerance
    else:
        return True


def is_compatible_alternative(
    original: dict[str, Any], candidate: dict[str, Any], subcategory: str
) -> tuple[bool, dict[str, Any]]:
    """Check if candidate is a compatible alternative for original.

    Returns (is_compatible, verification_info) tuple.
    verification_info contains specs_verified and specs_unparseable lists.
    """
    rules = COMPATIBILITY_RULES.get(subcategory)
    if not rules:
        return True, {"specs_verified": [], "specs_unparseable": []}

    orig_specs = original.get("key_specs", {})
    cand_specs = candidate.get("key_specs", {})

    specs_verified: list[str] = []
    specs_unparseable: list[str] = []

    # Check must_match specs (exact equality required)
    for spec in rules.get("must_match", []):
        orig_val = orig_specs.get(spec)
        cand_val = cand_specs.get(spec)
        if orig_val and cand_val:
            if not _values_match(orig_val, cand_val, spec):
                return False, {
                    "specs_verified": specs_verified,
                    "specs_unparseable": specs_unparseable,
                }
            specs_verified.append(spec)
        elif orig_val or cand_val:
            specs_unparseable.append(spec)  # One side missing

    # Check same_or_better specs
    for spec, direction in rules.get("same_or_better", {}).items():
        orig_val = orig_specs.get(spec)
        cand_val = cand_specs.get(spec)
        if orig_val and cand_val:
            parser = SPEC_PARSERS.get(spec)
            if parser and parser != "special" and callable(parser):
                if parser(orig_val) is not None and parser(cand_val) is not None:
                    if not _spec_ok(orig_val, cand_val, spec, direction):
                        return False, {
                            "specs_verified": specs_verified,
                            "specs_unparseable": specs_unparseable,
                        }
                    specs_verified.append(spec)
                else:
                    specs_unparseable.append(spec)  # Couldn't parse
            else:
                specs_unparseable.append(spec)  # No parser
        elif orig_val or cand_val:
            specs_unparseable.append(spec)  # One side missing

    return True, {"specs_verified": specs_verified, "specs_unparseable": specs_unparseable}


def verify_primary_spec_match(
    original: dict[str, Any], candidate: dict[str, Any], primary_attr: str
) -> bool:
    """Verify candidate has same primary spec value as original."""
    orig_value = original.get("key_specs", {}).get(primary_attr)
    cand_value = candidate.get("key_specs", {}).get(primary_attr)

    if not orig_value or not cand_value:
        return True  # Can't verify, allow through

    # Use _values_match for consistent comparison
    return _values_match(orig_value, cand_value, primary_attr)


# =============================================================================
# SCORING AND RANKING
# =============================================================================


def score_alternative(
    part: dict[str, Any],
    original: dict[str, Any],
    min_price_in_results: float | None,
) -> tuple[int, dict[str, int]]:
    """Score an alternative part for ranking.

    Returns (total_score, breakdown_dict) tuple.
    Higher score = better alternative.
    """
    score = 0
    breakdown: dict[str, int] = {}

    # Library type (biggest factor - $3 savings)
    if part.get("library_type") in ("basic", "preferred"):
        score += 1000
        breakdown["library_type"] = 1000
    else:
        breakdown["library_type"] = 0

    # Availability (user controls floor via min_stock param)
    stock = part.get("stock", 0)
    if stock >= 10000:
        avail_score = 70  # Excellent availability
    elif stock >= 1000:
        avail_score = 50  # Good availability
    elif stock >= 100:
        avail_score = 30  # Acceptable
    else:
        avail_score = -10  # Minor penalty for <100
    score += avail_score
    breakdown["availability"] = avail_score

    # EasyEDA footprint bonus (easier for users)
    if part.get("has_easyeda_footprint"):
        score += 20
        breakdown["easyeda"] = 20
    else:
        breakdown["easyeda"] = 0

    # Same manufacturer bonus (consistency)
    if part.get("manufacturer") == original.get("manufacturer"):
        score += 10
        breakdown["same_manufacturer"] = 10
    else:
        breakdown["same_manufacturer"] = 0

    # Price (minor factor, tiebreaker only)
    part_price = part.get("price")
    if part_price and part_price > 0 and min_price_in_results and min_price_in_results > 0:
        price_ratio = min_price_in_results / part_price
        price_score = min(10, int(10 * price_ratio))  # 0-10 points, capped
        score += price_score
        breakdown["price"] = price_score
    else:
        breakdown["price"] = 0

    return score, breakdown


# =============================================================================
# RESPONSE BUILDING
# =============================================================================


def build_response(
    original: dict[str, Any],
    scored_alternatives: list[tuple[int, dict[str, Any], dict[str, int], dict[str, Any]]],
    subcategory: str,
    primary_attr: str | None,
    primary_value: str | None,
    limit: int,
) -> dict[str, Any]:
    """Build the find_alternatives response for a supported subcategory."""
    alternatives = scored_alternatives[:limit]

    # Count basic/preferred alternatives
    no_fee_count = sum(
        1
        for _, p, _, _ in alternatives
        if p.get("library_type") in ("basic", "preferred")
    )

    # Determine confidence based on verification coverage
    all_specs_verified = (
        all(len(v["specs_unparseable"]) == 0 for _, _, _, v in alternatives)
        if alternatives
        else True
    )
    confidence = "high" if all_specs_verified else "medium"
    confidence_reason = (
        "All critical specs verified compatible"
        if all_specs_verified
        else "Some specs could not be parsed - verify manually"
    )

    # Build human-readable summary
    if not alternatives:
        if original.get("library_type") in ("basic", "preferred"):
            message = (
                "Original part is already basic/preferred - no assembly fee savings possible"
            )
        else:
            message = f"No compatible alternatives found matching {primary_value}"
    elif no_fee_count > 0:
        message = (
            f"Found {no_fee_count} basic/preferred alternative(s) that save $3 assembly fee"
        )
    else:
        message = f"Found {len(alternatives)} alternative(s), but all are extended library"

    # Calculate savings vs best alternative
    best_part = alternatives[0][1] if alternatives else None
    savings = None
    if best_part:
        assembly_savings = (
            3.0
            if (
                original.get("library_type") == "extended"
                and best_part.get("library_type") in ("basic", "preferred")
            )
            else 0.0
        )
        orig_price = original.get("price") or 0
        best_price = best_part.get("price") or 0
        price_diff = orig_price - best_price
        savings = {
            "assembly_fee": assembly_savings,
            "unit_price_diff": round(price_diff, 4),
            "total_per_unit": round(assembly_savings + price_diff, 4),
        }

    # Comparison helper
    comparison = None
    if best_part:
        comparison = {
            "original": {
                "lcsc": original.get("lcsc"),
                "library_type": original.get("library_type"),
                "price": original.get("price"),
                "stock": original.get("stock"),
            },
            "recommended": {
                "lcsc": best_part.get("lcsc"),
                "library_type": best_part.get("library_type"),
                "price": best_part.get("price"),
                "stock": best_part.get("stock"),
            },
            "savings": savings,
        }

    # Build alternatives list with verification info and MOQ warnings
    alternatives_output = []
    for score, part, breakdown, verify_info in alternatives:
        alt: dict[str, Any] = {
            **part,
            "score": score,
            "score_breakdown": breakdown,
            "specs_verified": verify_info["specs_verified"],
            "specs_unparseable": verify_info["specs_unparseable"],
        }
        # Add MOQ warning if high
        moq = part.get("min_order", 1)
        if moq and moq > 100:
            alt["moq_warning"] = f"High MOQ: {moq} units minimum"
        alternatives_output.append(alt)

    return {
        "original": original,
        "alternatives": alternatives_output,
        "summary": {
            "found": len(alternatives),
            "basic_preferred_count": no_fee_count,
            "message": message,
            "is_supported_category": True,
            "price_note": "Prices shown are unit price at qty 1 tier",
        },
        "comparison": comparison,
        "confidence": {
            "level": confidence,
            "reason": confidence_reason,
        },
        "search_criteria": {
            "primary_attribute": primary_attr,
            "matched_value": primary_value,
            "subcategory": subcategory,
            "compatibility_verified": True,
        },
    }


def build_unsupported_response(
    original: dict[str, Any],
    scored_parts: list[tuple[int, dict[str, Any], dict[str, int], dict[str, Any]]],
    subcategory: str,
    primary_attr: str | None,
    limit: int,
) -> dict[str, Any]:
    """Build response for unsupported subcategories - similar parts, not alternatives."""
    similar = scored_parts[:limit]

    # Get the key specs to verify from KEY_ATTRIBUTES
    specs_to_verify = KEY_ATTRIBUTES.get(subcategory, [])

    similar_parts_output = []
    for score, part, breakdown, _ in similar:
        item: dict[str, Any] = {
            **part,
            "score": score,
            "score_breakdown": breakdown,
        }
        moq = part.get("min_order", 1)
        if moq and moq > 100:
            item["moq_warning"] = f"High MOQ: {moq} units minimum"
        similar_parts_output.append(item)

    primary_value = None
    if primary_attr:
        primary_value = original.get("key_specs", {}).get(primary_attr)

    return {
        "original": original,
        "alternatives": [],  # Empty - we can't verify compatibility
        "similar_parts": similar_parts_output,
        "summary": {
            "found": len(similar),
            "message": "No compatibility rules for this category. Showing similar parts for manual comparison.",
            "is_supported_category": False,
            "price_note": "Prices shown are unit price at qty 1 tier",
        },
        "manual_comparison": {
            "original_specs": original.get("key_specs", {}),
            "specs_to_verify": specs_to_verify[:5],
            "guidance": (
                f"Compare these specs manually: {', '.join(specs_to_verify[:5])}"
                if specs_to_verify
                else "Review datasheets for compatibility"
            ),
        },
        "search_criteria": {
            "primary_attribute": primary_attr,
            "matched_value": primary_value,
            "subcategory": subcategory,
            "compatibility_verified": False,
        },
    }
