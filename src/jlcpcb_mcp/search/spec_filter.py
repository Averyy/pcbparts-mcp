"""Spec filter definitions and attribute mappings for parametric search."""

from dataclasses import dataclass
from typing import Any, Literal

from ..parsers import (
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


_VALID_OPERATORS = frozenset({"=", ">=", "<=", ">", "<", "!="})


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

    def __post_init__(self) -> None:
        """Validate operator is one of the allowed values."""
        if self.operator not in _VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator '{self.operator}'. "
                f"Must be one of: {', '.join(sorted(_VALID_OPERATORS))}"
            )

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "op": self.operator, "value": self.value}


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


def escape_like(value: str) -> str:
    """Escape SQL LIKE wildcards (%, _) in user input.

    Uses backslash as the escape character, which must be specified
    in the LIKE clause with ESCAPE '\\'.
    """
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# Keep private alias for backward compatibility within this module
_escape_like = escape_like


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
    - '%"Resistance", "82k%'   (matches "82kOhm", "82kohm")
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
    value_escaped = _escape_like(value.rstrip("OhmOHMohm"))

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
        # Tolerance uses +- prefix
        pct = parsed_value
        if _is_integer(pct):
            patterns.append(f'%"{name_escaped}", "\\\\u00b1{int(round(pct))}\\%%')

    return patterns[:3]  # Limit to 3 patterns max


def get_attribute_names(name: str) -> list[str]:
    """Get all possible attribute names for a given name (including aliases).

    Args:
        name: The attribute name or alias to look up

    Returns:
        List of possible attribute names
    """
    from ..alternatives import SPEC_PARSERS

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
