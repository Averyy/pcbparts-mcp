"""Subcategory aliases and name resolution utilities.

This module provides:
- SUBCATEGORY_ALIASES: Maps common shorthand to actual subcategory names
- resolve_subcategory_name(): Resolves names/aliases to IDs with fuzzy matching
"""

from typing import Any


# Common subcategory aliases for frequently searched terms
# Maps common shorthand to the actual subcategory name (lowercase)
SUBCATEGORY_ALIASES: dict[str, str] = {
    # Capacitors
    "capacitor": "multilayer ceramic capacitors mlcc - smd/smt",
    "capacitors": "multilayer ceramic capacitors mlcc - smd/smt",
    "cap": "multilayer ceramic capacitors mlcc - smd/smt",
    "mlcc": "multilayer ceramic capacitors mlcc - smd/smt",
    "smd capacitor": "multilayer ceramic capacitors mlcc - smd/smt",
    "ceramic capacitor": "multilayer ceramic capacitors mlcc - smd/smt",
    "smd ceramic capacitor": "multilayer ceramic capacitors mlcc - smd/smt",
    "electrolytic": "aluminum electrolytic capacitors - smd",
    "electrolytic capacitor": "aluminum electrolytic capacitors - smd",
    "smd electrolytic": "aluminum electrolytic capacitors - smd",
    "tantalum": "tantalum capacitors",
    "tantalum capacitor": "tantalum capacitors",
    "film capacitor": "film capacitors",
    "supercap": "supercapacitors",
    "supercapacitor": "supercapacitors",
    # Resistors
    "resistor": "chip resistor - surface mount",
    "resistors": "chip resistor - surface mount",
    "smd resistor": "chip resistor - surface mount",
    "chip resistor": "chip resistor - surface mount",
    "through hole resistor": "through hole resistors",
    "tht resistor": "through hole resistors",
    "current sense resistor": "current sense resistors / shunt resistors",
    "shunt resistor": "current sense resistors / shunt resistors",
    "resistor array": "resistor networks, arrays",
    "resistor network": "resistor networks, arrays",
    # Inductors
    "inductor": "inductors (smd)",
    "inductors": "inductors (smd)",
    "smd inductor": "inductors (smd)",
    "power inductor": "inductors (smd)",
    "coil": "inductors (smd)",
    "ferrite bead": "ferrite beads",
    "ferrite": "ferrite beads",
    # Diodes
    "diode": "switching diodes",
    "diodes": "switching diodes",
    "schottky": "schottky diodes",
    "schottky diode": "schottky diodes",
    "zener": "zener diodes",
    "zener diode": "zener diodes",
    "tvs": "tvs",
    "tvs diode": "tvs",
    "esd diode": "tvs",
    "rectifier": "rectifiers",
    "rectifier diode": "rectifiers",
    # Transistors - MOSFETs
    "mosfet": "mosfets",
    "mosfets": "mosfets",
    "n-channel": "mosfets",
    "p-channel": "mosfets",
    "n-channel mosfet": "mosfets",
    "p-channel mosfet": "mosfets",
    "nmos": "mosfets",
    "pmos": "mosfets",
    "power mosfet": "mosfets",
    # Transistors - BJT
    "bjt": "bipolar transistors - bjt",
    "transistor": "bipolar transistors - bjt",
    "npn": "bipolar transistors - bjt",
    "pnp": "bipolar transistors - bjt",
    "npn transistor": "bipolar transistors - bjt",
    "pnp transistor": "bipolar transistors - bjt",
    # Transistors - Other types
    "phototransistor": "phototransistors",
    "photo transistor": "phototransistors",
    "darlington": "darlington transistors",
    "darlington transistor": "darlington transistors",
    "jfet": "jfets",
    "igbt": "igbts",
    # Crystals/Oscillators
    "crystal": "crystals",
    "crystals": "crystals",
    "xtal": "crystals",
    "oscillator": "crystal oscillators",
    "tcxo": "temperature compensated crystal oscillators (tcxo)",
    # Connectors
    "usb connector": "usb connectors",
    "usb-c": "usb connectors",
    "usb type-c": "usb connectors",
    "type-c": "usb connectors",
    "type-c connector": "usb connectors",
    "pin header": "pin headers",
    "header": "pin headers",
    "male header": "pin headers",
    "female header": "female headers",
    "socket": "female headers",
    "jst": "wire to board / wire to wire connector",
    "terminal block": "screw terminal/pluggable terminal",
    "screw terminal": "screw terminal/pluggable terminal",
    # ICs - Voltage Regulators
    "ldo": "voltage regulators - linear, low drop out (ldo) regulators",
    "regulator": "voltage regulators - linear, low drop out (ldo) regulators",
    "linear regulator": "voltage regulators - linear, low drop out (ldo) regulators",
    "voltage regulator": "voltage regulators - linear, low drop out (ldo) regulators",
    # ICs - DC-DC
    "dc-dc": "dc-dc converters",
    "dc dc": "dc-dc converters",
    "dc dc converter": "dc-dc converters",
    "dc-dc converter": "dc-dc converters",
    "buck": "dc-dc converters",
    "buck converter": "dc-dc converters",
    "boost": "dc-dc converters",
    "boost converter": "dc-dc converters",
    "buck-boost": "dc-dc converters",
    # ICs - Op Amps
    "op amp": "operational amplifier",
    "opamp": "operational amplifier",
    "op-amp": "operational amplifier",
    "operational amplifier": "operational amplifier",
    # ICs - Other
    "adc": "analog to digital converters (adcs)",
    "dac": "digital to analog converters (dacs)",
    "mcu": "microcontroller units (mcus/mpus/socs)",
    "microcontroller": "microcontroller units (mcus/mpus/socs)",
    # LEDs
    "led": "led indication - discrete",
    "leds": "led indication - discrete",
    "smd led": "led indication - discrete",
    "indicator led": "led indication - discrete",
    "rgb led": "rgb leds",
    "addressable led": "rgb leds(built-in ic)",
    "ws2812": "rgb leds(built-in ic)",
    "neopixel": "rgb leds(built-in ic)",
    "ir led": "infrared led emitters",
    "infrared led": "infrared led emitters",
    "uv led": "ultraviolet leds (uvled)",
    # Switches
    "tactile switch": "tactile switches",
    "tact switch": "tactile switches",
    "push button": "tactile switches",
    "pushbutton": "tactile switches",
    "button": "tactile switches",
    "dip switch": "dip switches",
    "toggle switch": "toggle switches",
    "slide switch": "slide switches",
    "rocker switch": "rocker switches",
    # Sensors
    "temperature sensor": "temperature sensors",
    "temp sensor": "temperature sensors",
    "thermistor": "ntc thermistors",
    "ntc": "ntc thermistors",
    "ptc thermistor": "ptc thermistors - polymer",
    "accelerometer": "accelerometers",
    "gyroscope": "gyroscopes",
    "imu": "accelerometers",
    "hall sensor": "linear hall sensors",
    "hall effect": "linear hall sensors",
    "hall effect sensor": "linear hall sensors",
    "current sensor": "current sensors",
    "magnetic sensor": "magnetic angle sensors",
    "light sensor": "ambient light sensors",
    "ambient light": "ambient light sensors",
    "photodiode": "photodiodes",
    "photoresistor": "photoresistors",
    "ldr": "photoresistors",
    "pressure sensor": "pressure sensors",
    "humidity sensor": "humidity sensors",
    "gas sensor": "gas sensors",
    "proximity sensor": "proximity sensors",
    "ultrasonic sensor": "ultrasonic sensors",
    "encoder": "encoders",
    "rotary encoder": "encoders",
    # Modules
    "wifi module": "wifi modules",
    "bluetooth module": "bluetooth modules",
    "ble module": "bluetooth modules",
    "lora module": "lora modules",
    "gps module": "gnss / gps modules",
    "rf module": "rf modules",
    # Battery Management
    "battery charger": "battery management",
    "battery management": "battery management",
    "lithium charger": "battery management",
    "li-ion charger": "battery management",
    "lipo charger": "battery management",
    "charge controller": "battery management",
    "bms": "battery management",
    # Power Management
    "power switch": "power distribution switches",
    "load switch": "power distribution switches",
    "hot swap": "power distribution switches",
    # Protection
    "esd protection": "tvs",
    "surge protection": "tvs",
    "esd": "tvs",
    # Fuses
    "fuse": "fuses",
    "resettable fuse": "polymeric positive temperature coefficient (pptc) fuses",
    "ptc fuse": "polymeric positive temperature coefficient (pptc) fuses",
    "polyfuse": "polymeric positive temperature coefficient (pptc) fuses",
    # Optocouplers
    "optocoupler": "optocouplers - phototransistor output",
    "optoisolator": "optocouplers - phototransistor output",
    "opto": "optocouplers - phototransistor output",
    # Motor drivers
    "motor driver": "motor driver ics",
    "h-bridge": "motor driver ics",
    "stepper driver": "motor driver ics",
    # Relays
    "relay": "signal relays",
    "solid state relay": "solid state relays",
    "ssr": "solid state relays",
    # Timing
    "555 timer": "timer ics",
    "timer": "timer ics",
    "rtc": "real-time clocks (rtc)",
    "real time clock": "real-time clocks (rtc)",
    # Memory
    "eeprom": "eeprom",
    "flash": "nor flash",
    "sram": "sram",
    "fram": "fram",
    # Audio
    "audio amplifier": "audio power amplifiers",
    "class d": "audio power amplifiers",
    "class d amplifier": "audio power amplifiers",
    "codec": "codecs",
    "audio codec": "codecs",
    "buzzer": "buzzers",
    "speaker": "speakers",
    # Interface ICs
    "uart to usb": "usb to uart",
    "usb uart": "usb to uart",
    "level shifter": "level translators / shifters",
    "voltage translator": "level translators / shifters",
    "io expander": "i/o expanders",
    "gpio expander": "i/o expanders",
    # Display
    "oled": "oled displays modules",
    "lcd": "lcd display modules",
    "tft": "tft lcd",
    "7 segment": "seven-segment displays",
    "seven segment": "seven-segment displays",
}


def resolve_subcategory_name(
    name: str,
    name_to_id: dict[str, int],
    aliases: dict[str, str] | None = None,
) -> int | None:
    """Resolve subcategory name to ID. Case-insensitive, supports aliases and partial match.

    Matching priority:
    1. Common alias (e.g., "MLCC" -> "Multilayer Ceramic Capacitors MLCC - SMD/SMT")
    2. Exact match (e.g., "crystals" -> "crystals")
    3. Shortest containing match (e.g., "crystal" -> "crystals" not "crystal oscillators")

    Args:
        name: Subcategory name or alias to resolve
        name_to_id: Dict mapping lowercase subcategory names to IDs
        aliases: Optional alias dict (defaults to SUBCATEGORY_ALIASES)

    Returns:
        Subcategory ID if found, None otherwise.
    """
    if not name:
        return None

    if aliases is None:
        aliases = SUBCATEGORY_ALIASES

    name_lower = name.lower()

    # Check aliases first (handles common abbreviations like MLCC, LDO, etc.)
    if name_lower in aliases:
        alias_target = aliases[name_lower]
        if alias_target in name_to_id:
            return name_to_id[alias_target]

    # Exact match
    if name_lower in name_to_id:
        return name_to_id[name_lower]

    # Collect all partial matches (query contained in subcategory name)
    matches: list[tuple[str, int]] = []
    for subcat_name_lower, subcat_id in name_to_id.items():
        if name_lower in subcat_name_lower:
            matches.append((subcat_name_lower, subcat_id))

    if not matches:
        return None

    # Return shortest match (most specific)
    # e.g., "crystal" matches both "crystals" and "crystal oscillators"
    # "crystals" (8 chars) is shorter, so it wins
    matches.sort(key=lambda x: len(x[0]))
    return matches[0][1]


def find_similar_subcategories(
    name: str,
    name_to_id: dict[str, int],
    subcategory_info: dict[int, dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Find subcategories similar to the given name (for error suggestions).

    Args:
        name: Search query
        name_to_id: Dict mapping lowercase subcategory names to IDs
        subcategory_info: Dict mapping subcategory ID to info dict with 'name' and 'category_name'
        limit: Max results to return

    Returns:
        List of similar subcategory dicts with id, name, category.
    """
    name_lower = name.lower()
    matches = []

    for subcat_name_lower, subcat_id in name_to_id.items():
        # Check if any word from the query appears in the subcategory name
        words = name_lower.split()
        for word in words:
            if len(word) >= 3 and word in subcat_name_lower:
                subcat_info = subcategory_info.get(subcat_id, {})
                matches.append({
                    "id": subcat_id,
                    "name": subcat_info.get("name", subcat_name_lower),
                    "category": subcat_info.get("category_name", ""),
                })
                break

    # Dedupe and limit
    seen: set[int] = set()
    unique = []
    for m in matches:
        if m["id"] not in seen:
            seen.add(m["id"])
            unique.append(m)
            if len(unique) >= limit:
                break

    return unique
