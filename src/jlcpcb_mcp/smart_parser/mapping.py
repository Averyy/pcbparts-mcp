"""Category-aware attribute mapping for smart query parsing."""

from .values import ExtractedValue


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

    Args:
        value: The ExtractedValue to map
        component_type: The detected component type/subcategory
        matched_keyword: The keyword that was matched

    Returns:
        Tuple of (spec_name, operator)
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
        "pin_structure": ("Pin Structure", "="),  # 1x16, 2x20, etc. for headers
        "pitch": ("Pitch", "="),
    }

    # Try to get category-specific mapping from matched keyword
    if matched_keyword and matched_keyword.lower() in CATEGORY_ATTRIBUTE_MAP:
        cat_map = CATEGORY_ATTRIBUTE_MAP[matched_keyword.lower()]
        if value.unit_type in cat_map:
            spec_name = cat_map[value.unit_type]
            # Determine operator based on spec type
            if value.unit_type in ("resistance", "capacitance", "inductance", "frequency", "tolerance", "pin_count", "position_count", "pin_structure", "pitch"):
                return spec_name, "="
            else:
                return spec_name, ">="

    # Try to get category-specific mapping from component_type (subcategory)
    # This handles cases like USB connectors where subcategory is set from package pattern
    if component_type and component_type.lower() in CATEGORY_ATTRIBUTE_MAP:
        cat_map = CATEGORY_ATTRIBUTE_MAP[component_type.lower()]
        if value.unit_type in cat_map:
            spec_name = cat_map[value.unit_type]
            if value.unit_type in ("resistance", "capacitance", "inductance", "frequency", "tolerance", "pin_count", "position_count", "pin_structure", "pitch"):
                return spec_name, "="
            else:
                return spec_name, ">="

    # Fall back to defaults
    if value.unit_type in default_specs:
        return default_specs[value.unit_type]

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
