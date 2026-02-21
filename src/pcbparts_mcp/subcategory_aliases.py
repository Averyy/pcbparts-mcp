"""Subcategory aliases and name resolution utilities.

This module provides:
- SUBCATEGORY_ALIASES: Maps common shorthand to actual subcategory names
- resolve_subcategory_name(): Resolves names/aliases to IDs with fuzzy matching

IMPORTANT: All alias targets must match actual subcategory names in the database.
Run validation script before committing changes to ensure all mappings are valid.
"""

from typing import Any


# Common subcategory aliases for frequently searched terms
# Maps common shorthand to the actual subcategory name (case-insensitive matching)
# These must match actual subcategory names in the database!
SUBCATEGORY_ALIASES: dict[str, str] = {
    # ==========================================================================
    # CAPACITORS
    # ==========================================================================
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
    # Through-hole electrolytic capacitors
    "radial electrolytic": "aluminum electrolytic capacitors - leaded",
    "radial electrolytic capacitor": "aluminum electrolytic capacitors - leaded",
    "radial capacitor": "aluminum electrolytic capacitors - leaded",
    "through hole electrolytic": "aluminum electrolytic capacitors - leaded",
    "pth electrolytic": "aluminum electrolytic capacitors - leaded",
    "leaded electrolytic": "aluminum electrolytic capacitors - leaded",
    "tantalum": "tantalum capacitors",
    "tantalum capacitor": "tantalum capacitors",
    "film capacitor": "film capacitors",
    # Note: supercapacitors not available as a JLCPCB subcategory
    # ==========================================================================
    # RESISTORS
    # ==========================================================================
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
    # Potentiometers / Trimmers / Variable Resistors
    "potentiometer": "potentiometers, variable resistors",
    "potentiometers": "potentiometers, variable resistors",
    "pot": "potentiometers, variable resistors",
    "trimmer": "potentiometers, variable resistors",
    "trimpot": "potentiometers, variable resistors",
    "trim pot": "potentiometers, variable resistors",
    "variable resistor": "potentiometers, variable resistors",
    "adjustable resistor": "potentiometers, variable resistors",
    # ==========================================================================
    # INDUCTORS
    # ==========================================================================
    "inductor": "inductors (smd)",
    "inductors": "inductors (smd)",
    "smd inductor": "inductors (smd)",
    "power inductor": "power inductors",
    "power inductors": "power inductors",
    "coil": "inductors (smd)",
    "ferrite bead": "ferrite beads",
    "ferrite": "ferrite beads",
    # ==========================================================================
    # DIODES
    # ==========================================================================
    "diode": "switching diodes",
    "diodes": "switching diodes",
    "schottky": "schottky diodes",
    "schottky diode": "schottky diodes",
    "zener": "zener diodes",
    "zener diode": "zener diodes",
    "tvs": "esd and surge protection (tvs/esd)",
    "tvs diode": "esd and surge protection (tvs/esd)",
    "esd diode": "esd and surge protection (tvs/esd)",
    "esd protection": "esd and surge protection (tvs/esd)",
    "surge protection": "esd and surge protection (tvs/esd)",
    "esd": "esd and surge protection (tvs/esd)",
    "rectifier": "bridge rectifiers",
    "rectifier diode": "diodes - general purpose",
    "fast recovery diode": "fast recovery / high efficiency diodes",
    "fast diode": "fast recovery / high efficiency diodes",
    "frd": "fast recovery / high efficiency diodes",
    "sic diode": "sic diodes",
    "silicon carbide diode": "sic diodes",
    # ==========================================================================
    # TRANSISTORS - MOSFETs
    # ==========================================================================
    "mosfet": "mosfets",
    "mosfets": "mosfets",
    "n-channel": "mosfets",
    "p-channel": "mosfets",
    "n-channel mosfet": "mosfets",
    "p-channel mosfet": "mosfets",
    "nmos": "mosfets",
    "pmos": "mosfets",
    "power mosfet": "mosfets",
    "gan mosfet": "gan transistors(gan hemt)",
    "gan transistor": "gan transistors(gan hemt)",
    "gan hemt": "gan transistors(gan hemt)",
    "gallium nitride": "gan transistors(gan hemt)",
    "sic mosfet": "silicon carbide field effect transistor (mosfet)",
    "sic transistor": "silicon carbide field effect transistor (mosfet)",
    "silicon carbide mosfet": "silicon carbide field effect transistor (mosfet)",
    # ==========================================================================
    # TRANSISTORS - BJT (actual DB name: "Bipolar (BJT)")
    # ==========================================================================
    "bjt": "bipolar (bjt)",
    "transistor": "bipolar (bjt)",
    "npn": "bipolar (bjt)",
    "pnp": "bipolar (bjt)",
    "npn transistor": "bipolar (bjt)",
    "pnp transistor": "bipolar (bjt)",
    # ==========================================================================
    # TRANSISTORS - Other types
    # ==========================================================================
    "phototransistor": "phototransistors",
    "photo transistor": "phototransistors",
    "darlington": "darlington transistors",
    "darlington transistor": "darlington transistors",
    "jfet": "jfets",
    "igbt": "igbt transistors / modules",
    # ==========================================================================
    # CRYSTALS / OSCILLATORS
    # ==========================================================================
    "crystal": "crystals",
    "crystals": "crystals",
    "xtal": "crystals",
    "oscillator": "crystal oscillators",
    "tcxo": "temperature compensated crystal oscillators (tcxo)",
    # ==========================================================================
    # CONNECTORS
    # ==========================================================================
    "usb connector": "usb connectors",
    "usb-c": "usb connectors",
    "usb type-c": "usb connectors",
    "type-c": "usb connectors",
    "type-c connector": "usb connectors",
    # Pin headers (DB: "Pin Headers", "Female Headers")
    "pin header": "pin headers",
    "header": "pin headers",
    "male header": "pin headers",
    "header pin": "pin headers",
    "straight header": "pin headers",
    "right angle header": "pin headers",
    "single row header": "pin headers",
    "dual row header": "pin headers",
    "double row header": "pin headers",
    # Female headers (note: "socket" alone is too generic - could be IC socket)
    "female header": "female headers",
    "socket header": "female headers",
    "receptacle header": "female headers",
    "female socket": "female headers",
    # IC/Transistor sockets (DB: "IC / Transistor Socket")
    "ic socket": "ic / transistor socket",
    "dip socket": "ic / transistor socket",
    "transistor socket": "ic / transistor socket",
    "plcc socket": "ic / transistor socket",
    "chip socket": "ic / transistor socket",
    # Wire-to-board connectors (JST, etc.)
    "jst": "wire to board connector",
    "jst connector": "wire to board connector",
    "jst sh": "wire to board connector",
    "jst ph": "wire to board connector",
    "jst xh": "wire to board connector",
    "jst zh": "wire to board connector",
    "wire to board": "wire to board connector",
    # Qwiic/STEMMA QT are JST SH 1.0mm 4-pin connectors (maker ecosystem)
    "qwiic": "wire to board connector",
    "qwiic connector": "wire to board connector",
    "stemma qt": "wire to board connector",
    "stemma": "wire to board connector",
    "easyc": "wire to board connector",
    # Terminal blocks (DB: "Screw Terminal Blocks", "Pluggable System Terminal Block", "Barrier Terminal Blocks")
    # Note: "terminal" alone could mean crimp terminals, but in PCB context it usually means terminal blocks
    "terminal": "screw terminal blocks",
    "terminal block": "screw terminal blocks",
    "screw terminal": "screw terminal blocks",
    "screw terminal block": "screw terminal blocks",
    "pluggable terminal": "pluggable system terminal block",
    "pluggable terminal block": "pluggable system terminal block",
    "barrier terminal": "barrier terminal blocks",
    "barrier terminal block": "barrier terminal blocks",
    "spring terminal": "spring clamp system terminal block",
    "spring clamp terminal": "spring clamp system terminal block",
    # IDC connectors (DB: "IDC Connectors")
    "idc": "idc connectors",
    "idc connector": "idc connectors",
    "ribbon connector": "idc connectors",
    # FFC/FPC connectors (DB: "FFC, FPC (Flat Flexible) Connector Assemblies")
    "ffc": "ffc, fpc (flat flexible) connector assemblies",
    "fpc": "ffc, fpc (flat flexible) connector assemblies",
    "ffc connector": "ffc, fpc (flat flexible) connector assemblies",
    "fpc connector": "ffc, fpc (flat flexible) connector assemblies",
    "flat flex": "ffc, fpc (flat flexible) connector assemblies",
    "flat flexible": "ffc, fpc (flat flexible) connector assemblies",
    "zif connector": "ffc, fpc (flat flexible) connector assemblies",
    # Board-to-board (DB: "Board-to-Board and Backplane Connector")
    "board to board": "board-to-board and backplane connector",
    "btb connector": "board-to-board and backplane connector",
    "mezzanine connector": "board-to-board and backplane connector",
    # Coaxial/RF connectors (DB: "Coaxial Connectors (RF)")
    "sma": "coaxial connectors (rf)",
    "sma connector": "coaxial connectors (rf)",
    "coax": "coaxial connectors (rf)",
    "coaxial": "coaxial connectors (rf)",
    "rf connector": "coaxial connectors (rf)",
    "u.fl": "coaxial connectors (rf)",
    "ipex": "coaxial connectors (rf)",
    "ipx": "coaxial connectors (rf)",
    "mhf": "coaxial connectors (rf)",
    # Audio connectors (DB: "Audio Connectors")
    "audio jack": "audio connectors",
    "headphone jack": "audio connectors",
    "3.5mm jack": "audio connectors",
    "phone jack": "audio connectors",
    # DC power connectors (DB: "DC Power Connectors")
    "dc jack": "dc power connectors",
    "barrel jack": "dc power connectors",
    "dc power jack": "dc power connectors",
    "power connector": "dc power connectors",
    # Ethernet/RJ45 (DB: "Ethernet Connectors / Modular Connectors (RJ45 RJ11)")
    "rj45": "ethernet connectors / modular connectors (rj45 rj11)",
    "rj11": "ethernet connectors / modular connectors (rj45 rj11)",
    "ethernet connector": "ethernet connectors / modular connectors (rj45 rj11)",
    "ethernet jack": "ethernet connectors / modular connectors (rj45 rj11)",
    "modular jack": "ethernet connectors / modular connectors (rj45 rj11)",
    # SD card connectors (DB: "SD Card / Memory Card Connector")
    "sd card": "sd card / memory card connector",
    "sd card connector": "sd card / memory card connector",
    "microsd": "sd card / memory card connector",
    "micro sd": "sd card / memory card connector",
    "tf card": "sd card / memory card connector",
    "memory card connector": "sd card / memory card connector",
    # SIM card connectors (DB: "SIM Card Connectors")
    "sim card": "sim card connectors",
    "sim connector": "sim card connectors",
    "nano sim": "sim card connectors",
    "micro sim": "sim card connectors",
    # HDMI connectors (DB: "HDMI Connectors")
    "hdmi": "hdmi connectors",
    "hdmi connector": "hdmi connectors",
    "mini hdmi": "hdmi connectors",
    "micro hdmi": "hdmi connectors",
    # D-Sub/VGA (DB: "D-Sub / VGA Connectors")
    "d-sub": "d-sub / vga connectors",
    "dsub": "d-sub / vga connectors",
    "vga": "d-sub / vga connectors",
    "vga connector": "d-sub / vga connectors",
    "db9": "d-sub / vga connectors",
    "db15": "d-sub / vga connectors",
    "db25": "d-sub / vga connectors",
    # Banana/alligator clips (DB: "Banana Connectors / Alligator Clips")
    "banana plug": "banana connectors / alligator clips",
    "banana connector": "banana connectors / alligator clips",
    "alligator clip": "banana connectors / alligator clips",
    "crocodile clip": "banana connectors / alligator clips",
    # Pogo pins (DB: "Pogo Pin Spring Probe Connector")
    "pogo pin": "pogo pin spring probe connector",
    "spring probe": "pogo pin spring probe connector",
    "test probe": "pogo pin spring probe connector",
    # ==========================================================================
    # ICs - VOLTAGE REGULATORS
    # ==========================================================================
    "ldo": "voltage regulators - linear, low drop out (ldo) regulators",
    "regulator": "voltage regulators - linear, low drop out (ldo) regulators",
    "linear regulator": "voltage regulators - linear, low drop out (ldo) regulators",
    "voltage regulator": "voltage regulators - linear, low drop out (ldo) regulators",
    # ==========================================================================
    # ICs - DC-DC CONVERTERS
    # ==========================================================================
    "dc-dc": "dc-dc converters",
    "dc dc": "dc-dc converters",
    "dc dc converter": "dc-dc converters",
    "dc-dc converter": "dc-dc converters",
    "buck": "dc-dc converters",
    "buck converter": "dc-dc converters",
    "boost": "dc-dc converters",
    "boost converter": "dc-dc converters",
    "buck-boost": "dc-dc converters",
    # ==========================================================================
    # ICs - OP AMPS
    # ==========================================================================
    "op amp": "operational amplifier",
    "opamp": "operational amplifier",
    "op-amp": "operational amplifier",
    "operational amplifier": "operational amplifier",
    # ==========================================================================
    # ICs - DATA CONVERTERS (actual DB names have singular ADC/DAC)
    # ==========================================================================
    "adc": "analog to digital converters (adc)",
    "dac": "digital to analog converters (dac)",
    # ==========================================================================
    # ICs - MICROCONTROLLERS (actual DB name: "Microcontrollers (MCU/MPU/SOC)")
    # ==========================================================================
    "mcu": "microcontrollers (mcu/mpu/soc)",
    "microcontroller": "microcontrollers (mcu/mpu/soc)",
    # ==========================================================================
    # LEDs
    # ==========================================================================
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
    # ==========================================================================
    # SWITCHES
    # ==========================================================================
    "tactile switch": "tactile switches",
    "tact switch": "tactile switches",
    "push button": "tactile switches",
    "pushbutton": "tactile switches",
    "button": "tactile switches",
    "pushbutton switch": "pushbutton switches",  # Panel-mount push buttons (distinct from PCB tactile)
    "panel button": "pushbutton switches",
    "dip switch": "dip switches",
    "toggle switch": "toggle switches",
    "slide switch": "slide switches",
    "rocker switch": "rocker switches",
    # ==========================================================================
    # SENSORS
    # ==========================================================================
    # Temperature and humidity sensors - handle multiple word orders
    # These must come before standalone "temperature sensor" to match first (longest-first sorting)
    "temperature and humidity sensor": "temperature and humidity sensor",
    "humidity and temperature sensor": "temperature and humidity sensor",
    "temperature humidity sensor": "temperature and humidity sensor",
    "humidity temperature sensor": "temperature and humidity sensor",
    "temp and humidity sensor": "temperature and humidity sensor",
    "humidity and temp sensor": "temperature and humidity sensor",
    "temp humidity sensor": "temperature and humidity sensor",
    "humidity temp sensor": "temperature and humidity sensor",
    # Popular sensor families (with "sensor" keyword)
    "dht sensor": "temperature and humidity sensor",  # DHT11/DHT22 family
    "sht sensor": "temperature and humidity sensor",  # SHT3x family (Sensirion)
    "bme sensor": "temperature and humidity sensor",  # BME280/BME680 family
    "aht sensor": "temperature and humidity sensor",  # AHT10/AHT20 family
    # Standalone temperature sensors (must come after combined sensors)
    "temperature sensor": "temperature sensors",
    "temp sensor": "temperature sensors",
    "thermistor": "ntc thermistors",
    "ntc": "ntc thermistors",
    "ptc thermistor": "ptc thermistors",
    # Other sensors
    "accelerometer": "accelerometers",
    "gyroscope": "accelerometers",  # Often combined as IMU
    "imu": "accelerometers",
    "hall sensor": "linear hall sensors",
    "hall effect": "linear hall sensors",
    "hall effect sensor": "linear hall sensors",
    "hall switch": "hall switches",
    "hall effect switch": "hall switches",
    "current sensor": "current sensors",
    "magnetic sensor": "magnetic angle sensors",
    "light sensor": "ambient light sensors",
    "ambient light": "ambient light sensors",
    "photodiode": "photodiodes",
    "photoresistor": "photoresistors",
    "ldr": "photoresistors",
    "pressure sensor": "pressure sensors",
    "gas sensor": "gas sensors",
    "proximity sensor": "proximity sensors",
    "ultrasonic sensor": "ultrasonic receivers, transmitters",
    "encoder": "rotary encoders",
    "rotary encoder": "rotary encoders",
    # ==========================================================================
    # ANTENNAS (actual DB names: "Antennas", "Antenna spring")
    # ==========================================================================
    "antenna": "antennas",
    "antennas": "antennas",
    "ceramic antenna": "antennas",
    "chip antenna": "antennas",
    "pcb antenna": "antennas",
    "external antenna": "antennas",
    "2.4ghz antenna": "antennas",  # Common WiFi/BLE frequency
    "wifi antenna": "antennas",
    "bluetooth antenna": "antennas",
    "ble antenna": "antennas",
    "gps antenna": "antennas",
    "lte antenna": "antennas",
    "5g antenna": "antennas",
    # ==========================================================================
    # MODULES
    # ==========================================================================
    "wifi module": "wifi modules",
    "bluetooth module": "bluetooth modules",
    "ble module": "bluetooth modules",
    "lora module": "lora modules",
    "gps module": "gnss modules",
    "rf module": "rf modules",
    # ==========================================================================
    # BATTERY MANAGEMENT
    # ==========================================================================
    "battery charger": "battery management",
    "battery management": "battery management",
    "lithium charger": "battery management",
    "li-ion charger": "battery management",
    "lipo charger": "battery management",
    "charge controller": "battery management",
    "bms": "battery management",
    # ==========================================================================
    # POWER MANAGEMENT
    # ==========================================================================
    "power switch": "power distribution switches",
    "load switch": "power distribution switches",
    "hot swap": "power distribution switches",
    # ==========================================================================
    # FUSES
    # ==========================================================================
    "fuse": "disposable fuses",
    "resettable fuse": "resettable fuses",
    "ptc fuse": "resettable fuses",
    "polyfuse": "resettable fuses",
    # ==========================================================================
    # OPTOCOUPLERS (actual DB: "Transistor, Photovoltaic Output Optoisolators")
    # ==========================================================================
    "optocoupler": "transistor, photovoltaic output optoisolators",
    "optoisolator": "transistor, photovoltaic output optoisolators",
    "opto": "transistor, photovoltaic output optoisolators",
    # ==========================================================================
    # MOTOR DRIVERS
    # ==========================================================================
    "motor driver": "motor driver ics",
    "h-bridge": "motor driver ics",
    "stepper driver": "motor driver ics",
    # ==========================================================================
    # RELAYS
    # ==========================================================================
    "relay": "signal relays",
    "solid state relay": "solid state relays",
    "ssr": "solid state relays",
    # ==========================================================================
    # TIMING (actual DB: "555 Timers / Counters", "Real Time Clocks")
    # ==========================================================================
    "555 timer": "555 timers / counters",
    "timer": "555 timers / counters",
    "rtc": "real time clocks",
    "real time clock": "real time clocks",
    # ==========================================================================
    # MEMORY
    # ==========================================================================
    "eeprom": "eeprom",
    "flash": "nor flash",
    "nor flash": "nor flash",
    "nand": "nand flash",
    "nand flash": "nand flash",
    "sram": "sram",
    "fram": "fram",
    # ==========================================================================
    # AUDIO (actual DB: "Audio Amplifiers", "Audio Interface ICs")
    # ==========================================================================
    "audio amplifier": "audio amplifiers",
    "class d": "audio amplifiers",
    "class d amplifier": "audio amplifiers",
    "codec": "audio interface ics",
    "audio codec": "audio interface ics",
    "buzzer": "buzzers",
    "speaker": "speakers",
    "microphone": "microphones",
    # ==========================================================================
    # DISPLAYS (actual DB: "LED Segment Displays", "LCD Screen", "OLED Display")
    # ==========================================================================
    "7 segment": "led segment displays",
    "seven segment": "led segment displays",
    "segment display": "led segment displays",
    "lcd": "lcd screen",
    "lcd display": "lcd screen",
    "oled": "oled display",
    "oled display": "oled display",
    "tft": "lcd screen",
    "tft lcd": "lcd screen",
    # ==========================================================================
    # INTERFACE ICs (actual DB: "Translators, Level Shifters", "UART")
    # ==========================================================================
    "level shifter": "translators, level shifters",
    "voltage translator": "translators, level shifters",
    "uart": "uart",
    # USB-to-UART converters (CH340, CP2102, FT232) are in "USB Converters", not "UART"
    "usb uart": "usb converters",
    "uart to usb": "usb converters",
    "usb to uart": "usb converters",
    "usb serial": "usb converters",
    "usb to serial": "usb converters",
    "serial to usb": "usb converters",
    "usb converter": "usb converters",
    # ==========================================================================
    # CURRENT SENSE AMPLIFIERS (actual DB: "Current Sense Amplifiers")
    # INA219, INA226, etc. are current sense amplifiers, not sensors
    # ==========================================================================
    "current sense amplifier": "current sense amplifiers",
    "current sense amp": "current sense amplifiers",
    "current monitor": "current sense amplifiers",
    "power monitor": "current sense amplifiers",
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
