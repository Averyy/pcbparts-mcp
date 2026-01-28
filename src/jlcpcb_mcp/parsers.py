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
_TOLERANCE_PATTERN = re.compile(r"([\d.]+)\s*%")
_PPM_PATTERN = re.compile(r"[±]?([\d.]+)\s*ppm", re.IGNORECASE)
_VF_AT_IF_PATTERN = re.compile(r"([\d.]+)\s*mV\s*@", re.IGNORECASE)
_POWER_FRACTION_PATTERN = re.compile(r"(\d+)/(\d+)\s*W", re.IGNORECASE)
_POWER_MW_PATTERN = re.compile(r"([\d.]+)\s*mW", re.IGNORECASE)
_POWER_W_PATTERN = re.compile(r"([\d.]+)\s*W", re.IGNORECASE)
_CURRENT_UA_PATTERN = re.compile(r"([\d.]+)\s*[uµ]A", re.IGNORECASE)
_CURRENT_MA_PATTERN = re.compile(r"([\d.]+)\s*mA", re.IGNORECASE)
_CURRENT_A_PATTERN = re.compile(r"([\d.]+)\s*A", re.IGNORECASE)
_RESISTANCE_PATTERN = re.compile(r"([\d.]+)\s*([kKmM])?")
# European notation: 4k7 = 4.7k, 4R7 = 4.7Ω, 1M5 = 1.5M (suffix replaces decimal point)
# Note: Does NOT match milliohm European notation (e.g., "10m5") - check is_milliohm first
_RESISTANCE_EURO_PATTERN = re.compile(r"(\d+)([kKrR])(\d+)|(\d+)(M)(\d+)", re.IGNORECASE)
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
_MEMORY_BYTE_PATTERN = re.compile(r"([\d.]+)\s*([KMG])?B", re.IGNORECASE)
_WAVELENGTH_PATTERN = re.compile(r"([\d.]+)\s*nm", re.IGNORECASE)
_LUMINOSITY_PATTERN = re.compile(r"([\d.]+)\s*mcd", re.IGNORECASE)
_CAPACITANCE_PF_PATTERN = re.compile(r"([\d.]+)\s*([pn])?", re.IGNORECASE)
_LENGTH_MM_PATTERN = re.compile(r"([\d.]+)\s*mm", re.IGNORECASE)
_INTEGER_PATTERN = re.compile(r"(\d+)")
_VGS_RANGE_PATTERN = re.compile(r"([\d.]+)\s*V?\s*~\s*([\d.]+)\s*V?", re.IGNORECASE)
_FREQ_RANGE_PATTERN = re.compile(
    r"([\d.]+)\s*([kKmMgG])?Hz?\s*~\s*([\d.]+)\s*([kKmMgG])?Hz?", re.IGNORECASE
)


# =============================================================================
# SPEC PARSERS
# =============================================================================
# Each parser returns a float in base units for comparison, or None if unparseable.


def parse_voltage(s: str) -> float | None:
    """Parse voltage: '25V' -> 25, '6.3V' -> 6.3, '5kV' -> 5000"""
    if not s:
        return None
    # Check kV first (must come before V check)
    match = _VOLTAGE_KV_PATTERN.search(s)
    if match:
        return float(match.group(1)) * 1000
    match = _VOLTAGE_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_tolerance(s: str) -> float | None:
    """Parse tolerance: '±1%' -> 1, '±10%' -> 10, '1%' -> 1"""
    if not s:
        return None
    match = _TOLERANCE_PATTERN.search(s)
    return float(match.group(1)) if match else None


def parse_ppm(s: str) -> float | None:
    """Parse frequency stability in ppm: '±20ppm' -> 20, '30ppm' -> 30"""
    if not s:
        return None
    match = _PPM_PATTERN.search(s)
    return float(match.group(1)) if match else None


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

    # Check for milliohm (mΩ, mohm) BEFORE removing Ω symbol
    # This distinguishes mΩ (milli) from MΩ (mega)
    is_milliohm = "mΩ" in s or "mohm" in s.lower()

    # Normalize: remove Ω/ohm and escaped Unicode
    s_clean = s.replace("Ω", "").replace("\\u03a9", "").replace("ohm", "").strip()

    # Don't try European notation for milliohms - "10m5" should be milliohms, not megaohms
    if not is_milliohm:
        # Try European notation (e.g., "4k7", "4R7", "1M5")
        euro_match = _RESISTANCE_EURO_PATTERN.search(s_clean)
        if euro_match:
            # Pattern has two alternatives: (\d+)([kKrR])(\d+) or (\d+)(M)(\d+)
            if euro_match.group(1) is not None:
                int_part = euro_match.group(1)
                suffix = euro_match.group(2).upper()
                frac_part = euro_match.group(3)
            else:
                int_part = euro_match.group(4)
                suffix = euro_match.group(5).upper()
                frac_part = euro_match.group(6)

            value = float(f"{int_part}.{frac_part}")

            if suffix == "R":
                return value  # R = ohms
            elif suffix == "K":
                return value * 1000
            elif suffix == "M":
                return value * 1_000_000
            return value

    # Handle "0R" special case (jumper resistor)
    if s_clean.upper() == "0R" or s_clean == "0":
        return 0.0

    # Try standard notation (e.g., "10k", "4.7k", "470")
    match = _RESISTANCE_PATTERN.search(s_clean)
    if not match:
        return None
    value = float(match.group(1))

    if is_milliohm:
        return value / 1000  # mΩ = milliohm

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

    # Handle bits (Mbit, Kbit, Gbit)
    match = _MEMORY_BIT_PATTERN.search(s_upper)
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


# =============================================================================
# SPEC_PARSERS REGISTRY
# =============================================================================
# Map spec names to their parser functions for dynamic lookup.

SPEC_PARSERS: dict[str, Any] = {
    "Voltage Rating": parse_voltage,
    "Voltage - DC Reverse(Vr)": parse_voltage,
    "Drain to Source Voltage": parse_voltage,
    "Collector - Emitter Voltage VCEO": parse_voltage,
    "Reverse Stand-Off Voltage (Vrwm)": parse_voltage,
    "Clamping Voltage": parse_voltage,
    "Clamping Voltage@Ipp": parse_voltage,
    "Isolation Voltage(Vrms)": parse_voltage,
    "Voltage - Max": parse_voltage,
    "Output Voltage": parse_voltage,
    "Voltage Dropout": parse_voltage,
    "Zener Voltage(Nom)": parse_voltage,
    "Voltage - Forward(Vf@If)": parse_forward_voltage,
    "Tolerance": parse_tolerance,
    "Frequency Stability": parse_ppm,
    "Power(Watts)": parse_power,
    "Pd - Power Dissipation": parse_power,
    "Peak Pulse Power": parse_power,
    "Peak Pulse Power(Ppk)": parse_power,
    "Peak Pulse Power (Ppk)": parse_power,
    "Peak Pulse Power Dissipation (Ppp)": parse_power,
    "Current - Continuous Drain(Id)": parse_current,
    "Current - Collector(Ic)": parse_current,
    "Current - Rectified": parse_current,
    "Current Rating": parse_current,
    "Current - Saturation(Isat)": parse_current,
    "Current - Saturation (Isat)": parse_current,
    "Output Current": parse_current,
    "Hold Current": parse_current,
    "Trip Current": parse_current,
    "Charging Current": parse_current,
    "Fast Charge Current": parse_current,
    "Charge Current": parse_current,
    "Charge Current - Max": parse_current,
    "Forward Current(If)": parse_current,
    "Forward Current (If)": parse_current,
    "If - Forward Current": parse_current,
    "Quiescent Current(Iq)": parse_current,
    "Quiescent Current": parse_current,
    "DC Resistance(DCR)": parse_resistance,
    "RDS(on)": parse_resistance,
    "Resistance": parse_resistance,
    "Capacitance": parse_capacitance,
    "Load Capacitance": parse_capacitance,
    "Inductance": parse_inductance,
    "Frequency": parse_frequency,
    "Frequency Range": parse_frequency,
    "Gain Bandwidth Product": parse_frequency,
    "Sampling Rate": parse_frequency,
    "Speed": parse_frequency,
    "Max Frequency": parse_frequency,
    "Operating Frequency": parse_frequency,
    "CPU Maximum Speed": parse_frequency,
    "Resolution(Bits)": parse_integer,
    "Number of Bits": parse_integer,
    "Number of Pins": parse_integer,
    "Number of Rows": parse_integer,
    "Pitch": parse_length_mm,
    "Noise Figure": parse_decibels,
    "Gain": parse_decibels,
    "Common Mode Rejection Ratio(CMRR)": parse_decibels,
    "Ripple Current": parse_current,
    "Equivalent Series Resistance(ESR)": parse_resistance,
    "Lifetime": parse_integer,
    "Flash": parse_memory_size,
    "Program Memory Size": parse_memory_size,
    "Program Storage Size": parse_memory_size,
    "SRAM": parse_memory_size,
    "RAM Size": parse_memory_size,
    "Capacity": parse_memory_size,
    "Memory Size": parse_memory_size,
    "Operating Temperature": parse_temp_range,
    "Operating Temperature Range": parse_temp_range,
    "Dominant Wavelength": parse_wavelength,
    "Wavelength - Dominant": parse_wavelength,
    "Luminous Intensity": parse_luminosity,
    "Luminous Intensity (mcd)": parse_luminosity,
    "Input Capacitance(Ciss)": parse_capacitance_pf,
    "Input Capacitance (Ciss)": parse_capacitance_pf,
    "Ciss": parse_capacitance_pf,
    "Efficiency": parse_percentage,
    "Slew Rate": parse_voltage,
    "Input Offset Voltage": parse_voltage,
    "Input Voltage": parse_vin_range,
    "Gate Threshold Voltage (Vgs(th))": parse_vgs_range,
    "Gate Threshold Voltage": parse_vgs_range,
}
