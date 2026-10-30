"""Category-aware attribute mapping for smart query parsing."""

from .values import ExtractedValue
from ..search.spec_filter import FUSE_ATTRIBUTE_MAP


# Maps (category_keyword, value_type) -> spec_name, or (spec_name, operator) where the default
# operator is wrong (a 5.1V zener is 5.1V, not >= 5.1V). Keys are keywords or subcategory names.
# This allows voltage to map to Vds for MOSFETs, Vr for diodes, etc.
# A 3.3V LDO outputs exactly 3.3V (Vout: the column, so adjustable LDOs don't match); a 5V DC-DC
# converter's output range covers 5V (most are adjustable: "0.8V~5.5V")
_LDO = {"voltage": ("Vout", "="), "current": "Output Current"}
_REGULATOR = {"voltage": ("Output Voltage", "="), "current": "Output Current"}
_ZENER = {"voltage": ("Zener Voltage(Nom)", "=")}
_RELAY = {"voltage": ("Coil Voltage", "=")}
_THERMISTOR = {"resistance": ("Resistance @ 25℃", "=")}
_SUPPLY = {"voltage": ("Supply Voltage", "=")}  # runs at that voltage: inside the supply range

CATEGORY_ATTRIBUTE_MAP: dict[str, dict[str, str | tuple[str, str]]] = {
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
    "zener": _ZENER,
    "zener diode": _ZENER,
    "zener diodes": _ZENER,
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
        "current": "Peak Pulse Current (Ipp)",
    },
    "tvs diode": {
        "voltage": "Reverse Stand-Off Voltage (Vrwm)",
        "current": "Peak Pulse Current (Ipp)",
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
        "resistance": "Impedance @ Frequency",  # "100 ohm" -> impedance at 100MHz
    },
    "ferrite beads": {
        "current": "Current Rating",
        "resistance": "Impedance @ Frequency",
    },
    "ferrite": {
        "current": "Current Rating",
        "resistance": "Impedance @ Frequency",
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
        "capacitance": "Load Capacitance",
        "frequency": "Frequency",
    },
    "crystals": {
        "capacitance": "Load Capacitance",
        "frequency": "Frequency",
    },
    "oscillator": {
        "capacitance": "Load Capacitance",
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

    # Battery Management / Chargers
    "battery charger": {
        "current": "Charge Current - Max",
        "voltage": "Charging Saturation Voltage",
    },
    "lipo charger": {
        "current": "Charge Current - Max",
        "voltage": "Charging Saturation Voltage",
    },
    "lithium charger": {
        "current": "Charge Current - Max",
        "voltage": "Charging Saturation Voltage",
    },
    "battery management": {
        "current": "Charge Current - Max",
        "voltage": "Charging Saturation Voltage",
    },
    "charging ic": {
        "current": "Charge Current - Max",
        "voltage": "Charging Saturation Voltage",
    },

    # Voltage Regulators
    "ldo": _LDO,
    "regulator": _LDO,
    "linear regulator": _LDO,
    "buck": _REGULATOR,
    "boost": _REGULATOR,
    "dc-dc": _REGULATOR,
    "dc-dc converters": _REGULATOR,
    "voltage regulators - linear, low drop out (ldo) regulators": _LDO,

    # Relays: "5V relay" is the coil voltage
    "relay": _RELAY,
    "relays": _RELAY,
    "signal relays": _RELAY,
    "power relays": _RELAY,

    # Thermistors list "Resistance @ 25℃", not Resistance
    "ntc": _THERMISTOR,
    "thermistor": _THERMISTOR,
    "ptc thermistor": _THERMISTOR,
    "ntc thermistors": _THERMISTOR,
    "ptc thermistors": _THERMISTOR,

    # A "5V buzzer" runs at 5V (its Voltage Rating is a list, "3V、5V、12V")
    "buzzer": _SUPPLY,
    "buzzers": _SUPPLY,

    # LEDs
    "led": {
        "current": "Forward Current",
        "voltage": "Voltage - Forward(Vf)",
    },
    "leds": {
        "current": "Forward Current",
        "voltage": "Voltage - Forward(Vf)",
    },

    # Fuses/PTCs
    "fuse": FUSE_ATTRIBUTE_MAP["disposable fuses"],
    **FUSE_ATTRIBUTE_MAP,
    "ptc": {
        "voltage": "Voltage - Max",
        "current": "Hold Current",
    },
    "resettable fuse": {
        "voltage": "Voltage - Max",
        "current": "Hold Current",
    },

    # Connectors - comprehensive mappings for all connector types
    # USB connectors use "Number of Contacts" not "Number of Pins"
    "usb connector": {
        "pin_count": "Number of Contacts",
        "pitch": "Pitch",
        "position_count": "Number of Contacts",
    },
    "usb connectors": {
        "pin_count": "Number of Contacts",
        "pitch": "Pitch",
        "position_count": "Number of Contacts",
    },
    "usb-c": {
        "pin_count": "Number of Contacts",
        "position_count": "Number of Contacts",
    },
    "type-c": {
        "pin_count": "Number of Contacts",
        "position_count": "Number of Contacts",
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
        "pin_count": "Number of Positions",
        "pitch": "Pitch",
        "position_count": "Number of Positions",
    },
    "female headers": {
        "pin_count": "Number of Positions",
        "pitch": "Pitch",
        "position_count": "Number of Positions",
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
        "pin_count": "Number of Positions or Pins",
        "pitch": "Pitch",
        "position_count": "Number of Positions or Pins",
    },
    "idc connectors": {
        "pin_count": "Number of Positions or Pins",
        "pitch": "Pitch",
        "position_count": "Number of Positions or Pins",
    },
    "ffc": {
        "pin_count": "Number of Contacts",
        "pitch": "Pitch",
        "position_count": "Number of Contacts",
    },
    "fpc": {
        "pin_count": "Number of Contacts",
        "pitch": "Pitch",
        "position_count": "Number of Contacts",
    },

    # Switches - Note: Tactile switches use Width/Length/Switch Height, not a generic "Size"
    # Dimension parsing would need specific handling for these attributes
}


# A value's spec and operator when no category mapping applies
DEFAULT_SPECS: dict[str, tuple[str, str]] = {
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
    "pin_structure": ("Pin Structure", "="),  # 1x16, 2x20, etc. for headers
    "pitch": ("Pitch", "="),
}


def map_value_to_spec(
    value: ExtractedValue,
    component_type: str | None,
    matched_keyword: str | None,
) -> tuple[str, str]:
    """Map an extracted value to the appropriate spec name based on context.

    Args:
        value: The ExtractedValue to map
        component_type: The detected component type/subcategory
        matched_keyword: The keyword that was matched

    Returns:
        Tuple of (spec_name, operator)
    """
    # Category-specific mapping: from the matched keyword, then from the subcategory (this handles
    # keywords without an entry, like "buck converter", and USB connectors whose subcategory is
    # set from the package pattern)
    # A known fuse subcategory takes precedence over the generic "fuse" keyword.
    keys = (matched_keyword, component_type)
    if (component_type or "").lower() in FUSE_ATTRIBUTE_MAP:
        keys = (component_type, matched_keyword)
    for key in keys:
        if not key or key.lower() not in CATEGORY_ATTRIBUTE_MAP:
            continue
        cat_map = CATEGORY_ATTRIBUTE_MAP[key.lower()]
        if value.unit_type not in cat_map:
            continue
        mapped = cat_map[value.unit_type]
        if mapped == "Output Current" and value.value < 1e-3:
            # No LDO or DC-DC converter lists an output current under 1mA: "LDO 1uA" is its idle current
            return "Quiescent Current", "<="
        if isinstance(mapped, tuple):
            return mapped
        # Determine operator based on spec type
        if value.unit_type in ("resistance", "capacitance", "inductance", "frequency", "tolerance", "pin_count", "position_count", "pin_structure", "pitch"):
            return mapped, "="
        return mapped, ">="

    # Fall back to defaults
    if value.unit_type in DEFAULT_SPECS:
        return DEFAULT_SPECS[value.unit_type]

    return value.unit_type.title(), "="


def infer_subcategory_from_values(values: list[ExtractedValue]) -> str | None:
    """Infer likely subcategory from extracted values.

    Used when no explicit component type is specified.

    Args:
        values: List of ExtractedValue objects

    Returns:
        Inferred subcategory name or None
    """
    value_types = {v.unit_type for v in values}

    # Strong indicators
    if "resistance" in value_types and "inductance" not in value_types and "capacitance" not in value_types:
        return "chip resistor - surface mount"
    if "capacitance" in value_types:
        return "multilayer ceramic capacitors mlcc - smd/smt"
    # NOTE: Inductance does NOT infer a subcategory because inductors are split
    # across multiple subcategories (Inductors (SMD), Power Inductors, etc.)
    # This allows text search to work across all inductor categories

    return None
