"""Shared spec parsers for electronic component values.

This module provides unified parsing functions for component specifications
like voltage, current, resistance, capacitance, etc. Used by both the
database builder and runtime spec comparison code.

All parsers return values in base SI units:
- Voltage: volts (V)
- Current: amps (A)
- Resistance: ohms (Ω)
- Capacitance: farads (F)
- Inductance: henries (H)
- Frequency: hertz (Hz)
- Power: watts (W)
- Temperature: celsius (°C)
- Memory: bytes
"""

import re
from typing import Any


# =============================================================================
# PRE-COMPILED REGEX PATTERNS
# =============================================================================
# Pre-compile for better performance - these are called many times per request.

_VOLTAGE_KV_PATTERN = re.compile(r"([\d.]+)\s*kV", re.IGNORECASE)
_VOLTAGE_PATTERN = re.compile(r"([\d.]+)\s*V", re.IGNORECASE)
_VOLTAGE_MV_PATTERN = re.compile(r"([\d.]+)\s*mV")
_TOLERANCE_PATTERN = re.compile(r"([\d.]+)\s*%")
_PPM_PATTERN = re.compile(r"[±]?([\d.]+)\s*pp([mb])", re.IGNORECASE)
_VF_AT_IF_PATTERN = re.compile(r"([\d.]+)\s*mV\s*@", re.IGNORECASE)
_POWER_FRACTION_PATTERN = re.compile(r"(\d+)/(\d+)\s*W", re.IGNORECASE)
_POWER_KW_PATTERN = re.compile(r"([\d.]+)\s*kW", re.IGNORECASE)
_POWER_MW_PATTERN = re.compile(r"([\d.]+)\s*mW", re.IGNORECASE)
_POWER_DBM_PATTERN = re.compile(r"([+-]?[\d.]+)\s*dBm", re.IGNORECASE)
_POWER_W_PATTERN = re.compile(r"([\d.]+)\s*W", re.IGNORECASE)
_CURRENT_UA_PATTERN = re.compile(r"([\d.]+)\s*[uµμ]A", re.IGNORECASE)
_CURRENT_MA_PATTERN = re.compile(r"([\d.]+)\s*mA", re.IGNORECASE)
_CURRENT_KA_PATTERN = re.compile(r"([\d.]+)\s*kA", re.IGNORECASE)
_CURRENT_A_PATTERN = re.compile(r"([\d.]+)\s*A", re.IGNORECASE)
_RESISTANCE_PATTERN = re.compile(r"([\d.]+)\s*([kKmM])?")
# European notation: 4k7 = 4.7k, 4R7 = 4.7Ω, 1M5 = 1.5M (suffix replaces decimal point)
_RESISTANCE_EURO_PATTERN = re.compile(r"(\d+)([kKmMrR])(\d+)")
_CAPACITANCE_PATTERN = re.compile(r"([\d.]+)\s*([pnuµm])?", re.IGNORECASE)
_INDUCTANCE_PATTERN = re.compile(r"([\d.]+)\s*([nuµm])?", re.IGNORECASE)
_FREQUENCY_PATTERN = re.compile(r"([\d.]+)\s*([kKmMgG])?")
_IMPEDANCE_AT_FREQ_PATTERN = re.compile(
    r"([\d.]+)\s*([kKmM])?Ohm\s*@\s*([\d.]+)\s*([kKmMgG])?Hz", re.IGNORECASE
)
_DECIBEL_PATTERN = re.compile(r"([\d.]+)\s*dB", re.IGNORECASE)
_TEMPERATURE_PATTERN = re.compile(r"([+-]?[\d.]+)\s*[°℃]?C?", re.IGNORECASE)
_TEMP_RANGE_PATTERN = re.compile(
    r"([+-]?\d+)\s*[°℃]?C?\s*~\s*[+]?([+-]?\d+)\s*[°℃]?C?", re.IGNORECASE
)
_MEMORY_BIT_PATTERN = re.compile(r"([\d.]+)\s*([KMG])?BIT", re.IGNORECASE)
_MEMORY_SHORT_BIT_PATTERN = re.compile(r"([\d.]+)\s*([KMG])b\b")
_MEMORY_BYTE_PATTERN = re.compile(r"([\d.]+)\s*([KMG])?B", re.IGNORECASE)
_WAVELENGTH_PATTERN = re.compile(r"([\d.]+)\s*nm", re.IGNORECASE)
_LUMINOSITY_PATTERN = re.compile(r"([\d.]+)\s*mcd", re.IGNORECASE)
_CAPACITANCE_PF_PATTERN = re.compile(r"([\d.]+)\s*([pn])?", re.IGNORECASE)
_LENGTH_MM_PATTERN = re.compile(r"([\d.]+)\s*mm", re.IGNORECASE)
_INTEGER_PATTERN = re.compile(r"(\d+)")
_BARE_NUMBER_PATTERN = re.compile(r"\s*\d+(?:\.\d+)?\s*")
_VGS_RANGE_PATTERN = re.compile(r"([\d.]+)\s*V?\s*~\s*([\d.]+)\s*V?", re.IGNORECASE)
_FREQ_RANGE_PATTERN = re.compile(
    r"([\d.]+)\s*([kKmMgG])?Hz?\s*~\s*([\d.]+)\s*([kKmMgG])?Hz?", re.IGNORECASE
)


# =============================================================================
# SPEC PARSERS
# =============================================================================
# Each parser returns a float in base units for comparison, or None if unparseable.


def parse_voltage(s: str) -> float | None:
    """Parse voltage: '25V' -> 25, '6.3V' -> 6.3, '5kV' -> 5000, '350mV@(100mA)' -> 0.35"""
    if not s:
        return None
    # Check kV first (must come before V check)
    match = _VOLTAGE_KV_PATTERN.search(s)
    if match:
        return float(match.group(1)) * 1000
    match = _VOLTAGE_PATTERN.search(s)
    if match:
        return float(match.group(1))
    # mV only when there's no V value, so "800mV~3.6V" still reads 3.6
    match = _VOLTAGE_MV_PATTERN.search(s)
    return float(match.group(1)) / 1000 if match else None


def parse_isolation_voltage(s: str) -> float | None:
    """Parse isolation voltage: '5000Vrms' -> 5000, '3.75kVrms' -> 3750, and the bare numbers
    Digital Isolators list ('5000' -> 5000)"""
    value = parse_voltage(s)
    if value is None and s and _BARE_NUMBER_PATTERN.fullmatch(s):
        return float(s)
    return value


def parse_tolerance(s: str) -> float | None:
    """Parse tolerance: '±1%' -> 1, '±10%' -> 10, '1%' -> 1"""
    if not s:
        return None
    match = _TOLERANCE_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_ppm(s: str) -> float | None:
    """Parse frequency stability in ppm: '±20ppm' -> 20, '30ppm' -> 30, '±500ppb' -> 0.5"""
    if not s:
        return None
    match = _PPM_PATTERN.search(s)
    if not match:
        return None
    return float(match.group(1)) / 1000 if match.group(2).lower() == "b" else float(match.group(1))


def parse_forward_voltage(s: str) -> float | None:
    """Parse forward voltage from Vf@If format: '550mV@3A' -> 0.55V, '1V@100mA' -> 1.0V"""
    if not s:
        return None
    # Try mV format first (e.g., "550mV@3A")
    match = _VF_AT_IF_PATTERN.search(s)
    if match:
        return float(match.group(1)) / 1000  # Convert mV to V
    # Try V format (e.g., "1V@100mA")
    match = _VOLTAGE_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_power(s: str) -> float | None:
    """Parse power in watts: '100mW' -> 0.1, '1/4W' -> 0.25, '0.25W' -> 0.25, '1.5kW' -> 1500,
    '20dBm' -> 0.1 (RF output power)"""
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
    # kW and dBm only when there's no W/mW value, so "600W@10/1000us、4kW@8/20us" still reads 600
    match = _POWER_KW_PATTERN.search(s)
    if match:
        return float(match.group(1)) * 1000
    match = _POWER_DBM_PATTERN.search(s)
    if match:
        return 10 ** (float(match.group(1)) / 10) / 1000
    return None


def parse_current(s: str) -> float | None:
    """Parse current in amps: '2A' -> 2, '500mA' -> 0.5, '100uA' -> 0.0001, '5kA' -> 5000"""
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
    # kA only when there's no A value, so "750A、10kA" still reads 750
    match = _CURRENT_KA_PATTERN.search(s)
    return float(match.group(1)) * 1000 if match else None


def parse_resistance(s: str) -> float | None:
    """Parse resistance in ohms: '10kΩ' -> 10000, '17mΩ' -> 0.017, '4.7MΩ' -> 4700000

    Also supports European notation where suffix replaces decimal point:
    - '4k7' -> 4700 (4.7kΩ)
    - '4R7' -> 4.7 (4.7Ω)
    - '1M5' -> 1500000 (1.5MΩ)
    - '470R' -> 470 (470Ω)
    - '0R' -> 0 (0Ω jumper)

    Handles milliohm notation:
    - '17mΩ' -> 0.017
    - '100mohm' -> 0.1
    """
    if not s:
        return None

    # Unit names are case-insensitive, but the SI prefix is not: M = mega, m = milli.
    s_clean = s.replace("Ω", "").replace("\\u03a9", "")
    s_clean = re.sub(r"milliohms?", "m", s_clean, flags=re.IGNORECASE)
    s_clean = re.sub(r"meg", "M", s_clean, flags=re.IGNORECASE)
    s_clean = re.sub(r"ohms?", "", s_clean, flags=re.IGNORECASE).strip()

    euro_match = _RESISTANCE_EURO_PATTERN.search(s_clean)
    if euro_match:
        int_part, suffix, frac_part = euro_match.groups()
        value = float(f"{int_part}.{frac_part}")
    else:
        match = _RESISTANCE_PATTERN.search(s_clean)
        if not match:
            return None
        value = float(match.group(1))
        suffix = match.group(2) or ""

    if suffix in ("k", "K"):
        return value * 1000
    if suffix == "M":
        return value * 1_000_000
    if suffix == "m":
        return value / 1000
    return value


# Resistors come in E96/E192 steps about 1% apart (990kΩ, 1MΩ, 1.01MΩ), so equal resistances
# must match closer than the 1-2% slack other values get.
RESISTANCE_MATCH_TOLERANCE = 0.001


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


def parse_temperature(s: str) -> float | None:
    """Parse temperature in Celsius: '85℃' -> 85, '-40°C' -> -40"""
    if not s:
        return None
    match = _TEMPERATURE_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_temp_range(s: str) -> tuple[float | None, float | None]:
    """Parse temperature range: '-40℃~+85℃' -> (-40, 85)"""
    if not s:
        return None, None
    match = _TEMP_RANGE_PATTERN.search(s)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None


def parse_memory_size(s: str) -> float | None:
    """Parse memory size in bytes: '128KB' -> 131072, '2MB' -> 2097152, '128Mbit' -> 16777216"""
    if not s:
        return None
    s_upper = s.upper()

    # Handle bits (Mbit, Kbit, Gbit, or case-sensitive Mb/Kb/Gb)
    match = _MEMORY_BIT_PATTERN.search(s_upper) or _MEMORY_SHORT_BIT_PATTERN.search(s)
    if match:
        value = float(match.group(1))
        suffix = match.group(2) or ""
        if suffix == "K":
            value *= 1024
        elif suffix == "M":
            value *= 1024 * 1024
        elif suffix == "G":
            value *= 1024 * 1024 * 1024
        return value / 8  # Convert bits to bytes

    # Handle bytes (KB, MB, GB)
    match = _MEMORY_BYTE_PATTERN.search(s_upper)
    if match:
        value = float(match.group(1))
        suffix = match.group(2) or ""
        if suffix == "K":
            value *= 1024
        elif suffix == "M":
            value *= 1024 * 1024
        elif suffix == "G":
            value *= 1024 * 1024 * 1024
        return value

    return None


def parse_percentage(s: str) -> float | None:
    """Parse percentage: '92%' -> 92"""
    if not s:
        return None
    match = _TOLERANCE_PATTERN.search(s)  # Reuse tolerance pattern
    return float(match.group(1)) if match else None


def parse_wavelength(s: str) -> float | None:
    """Parse wavelength in nm: '525nm' -> 525"""
    if not s:
        return None
    match = _WAVELENGTH_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_luminosity(s: str) -> float | None:
    """Parse luminous intensity in mcd: '1200mcd' -> 1200"""
    if not s:
        return None
    match = _LUMINOSITY_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_capacitance_pf(s: str) -> float | None:
    """Parse capacitance as pF: '100pF' -> 100, '1nF' -> 1000"""
    if not s:
        return None
    s = s.replace("F", "").strip()
    match = _CAPACITANCE_PF_PATTERN.search(s)
    if not match:
        return None
    value = float(match.group(1))
    suffix = (match.group(2) or "").lower()
    if suffix == "n":
        return value * 1000  # nF to pF
    return value  # pF


def parse_length_mm(s: str) -> float | None:
    """Parse length in mm: '2.54mm' -> 2.54"""
    if not s:
        return None
    match = _LENGTH_MM_PATTERN.search(s)
    return float(match.group(1)) if match else None


# Matches canned-aluminum / electrolytic dimension encoding in package strings:
# "SMD,D6.3xL5.7mm", "D10xL10.2mm", "D8 x L12.5mm". Group 1 = diameter, group 2 = height/length.
_PACKAGE_DIMENSIONS_PATTERN = re.compile(
    r"D\s*(\d+(?:\.\d+)?)\s*[x×X]\s*L?\s*(\d+(?:\.\d+)?)\s*mm",
    re.IGNORECASE,
)


def parse_dimensions_from_package(pkg: str) -> tuple[float | None, float | None]:
    """Extract (diameter_mm, height_mm) from a package string.

    JLCPCB often leaves the Height/Diameter spec fields as "-" for canned aluminum
    electrolytics and similar through-hole-style SMD parts, but the package column
    encodes the same info (e.g. "SMD,D6.3xL5.7mm"). This fallback recovers those
    dimensions so size-based filters don't silently exclude otherwise valid parts.
    """
    if not pkg:
        return None, None
    match = _PACKAGE_DIMENSIONS_PATTERN.search(pkg)
    if not match:
        return None, None
    return float(match.group(1)), float(match.group(2))


def parse_integer(s: str) -> int | None:
    """Parse integer: '8' -> 8, '16bit' -> 16"""
    if not s:
        return None
    match = _INTEGER_PATTERN.search(s)
    return int(match.group(1)) if match else None


def parse_vgs_range(s: str) -> tuple[float | None, float | None]:
    """Parse Vgs(th) range: '1.5V~2.5V' -> (1.5, 2.5), '2V' -> (2, 2)"""
    if not s:
        return None, None
    # Try range format first
    match = _VGS_RANGE_PATTERN.search(s)
    if match:
        return float(match.group(1)), float(match.group(2))
    # Single value
    single_match = _VOLTAGE_PATTERN.search(s)
    if single_match:
        val = float(single_match.group(1))
        return val, val
    return None, None


def parse_freq_range(s: str) -> tuple[float | None, float | None]:
    """Parse frequency range: '2.4GHz~2.5GHz' -> (2.4e9, 2.5e9)"""
    if not s:
        return None, None
    # Try range format
    match = _FREQ_RANGE_PATTERN.search(s)
    if match:
        val1 = float(match.group(1))
        suffix1 = (match.group(2) or "").upper()
        val2 = float(match.group(3))
        suffix2 = (match.group(4) or "").upper()

        mult_map = {"K": 1e3, "M": 1e6, "G": 1e9}
        mult1 = mult_map.get(suffix1, 1)
        mult2 = mult_map.get(suffix2, 1)
        return val1 * mult1, val2 * mult2
    # Single value
    single = parse_frequency(s)
    return single, single


def parse_vin_range(s: str) -> tuple[float | None, float | None]:
    """Parse input voltage range: '2.5V~5.5V' -> (2.5, 5.5)"""
    if not s:
        return None, None
    match = _VGS_RANGE_PATTERN.search(s)  # Same pattern as Vgs
    if match:
        return float(match.group(1)), float(match.group(2))
    # Single value (use as both min and max)
    single = parse_voltage(s)
    return single, single


def parse_impedance_at_freq(s: str) -> tuple[float, float] | None:
    """Parse impedance @ frequency: '600Ω @ 100MHz' -> (600, 100e6)
    Returns (impedance_ohms, frequency_hz) tuple for comparison.
    """
    if not s:
        return None
    # Normalize: Ω, Ohm, ohm -> unified
    s = s.replace("Ω", "Ohm").replace("ohm", "Ohm")
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
    mult_map = {"K": 1e3, "M": 1e6, "G": 1e9}
    freq_value *= mult_map.get(freq_suffix, 1)

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


_ESP32_MEMORY_PATTERN = re.compile(
    r"^ESP32(?:-[A-Z0-9]+)*-N(\d+)(?:R(\d+))?(?:[A-Z0-9]*)(?:$|-)", re.IGNORECASE
)


def parse_esp32_module_memory(mpn: str | None) -> tuple[int | None, int | None]:
    """Flash/PSRAM in MB from ESP32 N/R codes; N without R means zero PSRAM, no N stays unknown."""
    match = _ESP32_MEMORY_PATTERN.search(mpn or "")
    if not match:
        return None, None
    return int(match[1]), int(match[2]) if match[2] else 0
