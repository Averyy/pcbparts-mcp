"""ESPHome component sensor scraper."""

import logging
import re
import subprocess
import tempfile
from pathlib import Path

from .common import (
    make_sensor_entry,
    normalize_sensor_id,
    write_source_json,
)

logger = logging.getLogger(__name__)

# Known IC → measures override. Checked AFTER source code analysis but REPLACES
# the extracted measures when present. Fixes cases where ESPHome component code
# exposes CONF_DISTANCE for altitude (which is derived from pressure, not distance).
KNOWN_IC_MEASURES = {
    "sps30": ["particulate"],
    "mpl3115a2": ["pressure", "temperature"],
    "sds011": ["particulate"],
    "as3935": ["weather"],
    "ads1115": ["current", "voltage"],
    "ads1118": ["temperature", "voltage"],
}

# ── ESPHome measure extraction: multiple signal sources ─────────────────────

# CONF_* keys that indicate measurement channels (most reliable signal)
ESPHOME_CONF_MEASURES = {
    "CONF_TEMPERATURE": "temperature",
    "CONF_HUMIDITY": "humidity",
    "CONF_PRESSURE": "pressure",
    "CONF_CO2": "co2",
    "CONF_PM_1_0": "particulate",
    "CONF_PM_2_5": "particulate",
    "CONF_PM_10_0": "particulate",
    "CONF_ILLUMINANCE": "light",
    "CONF_DISTANCE": "distance",
    "CONF_VOC": "gas",
    "CONF_TVOC": "gas",
    "CONF_NOX": "gas",
    "CONF_ACCELERATION_X": "acceleration",
    "CONF_ACCELERATION_Y": "acceleration",
    "CONF_ACCELERATION_Z": "acceleration",
    "CONF_FIELD_STRENGTH_X": "magnetic_field",
    "CONF_FIELD_STRENGTH_Y": "magnetic_field",
    "CONF_FIELD_STRENGTH_Z": "magnetic_field",
    "CONF_HEADING": "magnetic_field",
    "CONF_MOISTURE": "humidity",
    "CONF_GAS_RESISTANCE": "gas",
    "CONF_WIND_SPEED": "wind",
    "CONF_WIND_DIRECTION_DEGREES": "wind",
    "CONF_PROXIMITY_GAIN": "proximity",
    "CONF_GESTURE_GAIN": "gesture",
    "CONF_GESTURE_LED_DRIVE": "gesture",
    "CONF_FACE_COUNT": "face_recognition",
    "CONF_GYRO_X": "gyroscope",
    "CONF_GYRO_Y": "gyroscope",
    "CONF_GYRO_Z": "gyroscope",
    "CONF_ACCEL_X": "acceleration",
    "CONF_ACCEL_Y": "acceleration",
    "CONF_ACCEL_Z": "acceleration",
    "CONF_RED_CHANNEL": "color",
    "CONF_GREEN_CHANNEL": "color",
    "CONF_BLUE_CHANNEL": "color",
    "CONF_COLOR_TEMPERATURE": "color",
}

# UNIT_* constants -> measures (backup for components without standard CONF names)
ESPHOME_UNIT_MEASURES = {
    "UNIT_METER_PER_SECOND_SQUARED": "acceleration",
    "UNIT_G": "acceleration",
    "UNIT_DEGREE_PER_SECOND": "gyroscope",
    "UNIT_MICROTESLA": "magnetic_field",
    "UNIT_LUX": "light",
    "UNIT_HECTOPASCAL": "pressure",
    "UNIT_PASCAL": "pressure",
    "UNIT_PARTS_PER_MILLION": None,  # ambiguous (CO2 or VOC) — skip
    "UNIT_MICROGRAMS_PER_CUBIC_METER": "particulate",
    "UNIT_BEATS_PER_MINUTE": "biometric",
    "UNIT_BECQUEREL_PER_CUBIC_METER": "radiation",
    "UNIT_MICROSILVERTS_PER_HOUR": "radiation",
    "UNIT_PH": None,  # pH is its own thing, not in our measure list
    "UNIT_UVI": "uv",
    "UNIT_METER": "distance",
    "UNIT_MILLIMETER": "distance",
    "UNIT_CENTIMETER": "distance",
    "UNIT_KILOMETER": None,  # too ambiguous
    "UNIT_OHM": None,  # resistance reading, not a measure type
    "UNIT_KILOGRAM": "weight",
    "UNIT_KILOMETER_PER_HOUR": "wind",
}

# DEVICE_CLASS_* -> measures (fills remaining gaps)
ESPHOME_DEVICE_CLASS_MAP = {
    "TEMPERATURE": "temperature",
    "HUMIDITY": "humidity",
    "PRESSURE": "pressure",
    "ATMOSPHERIC_PRESSURE": "pressure",
    "ILLUMINANCE": "light",
    "DISTANCE": "distance",
    "CO2": "co2",
    "CARBON_DIOXIDE": "co2",
    "CARBON_MONOXIDE": "co",
    "VOLATILE_ORGANIC_COMPOUNDS": "gas",
    "VOLATILE_ORGANIC_COMPOUNDS_PARTS": "gas",
    "AQI": "gas",
    "NITROGEN_DIOXIDE": "gas",
    "CURRENT": "current",
    "VOLTAGE": "voltage",
    "PM25": "particulate",
    "PM10": "particulate",
    "PM1": "particulate",
    "GAS": "gas",
    "SOUND_PRESSURE": "sound",
    "WIND_SPEED": "wind",
    "PRECIPITATION": None,
}

# ICON_* -> measures (last resort, only very specific icons)
ESPHOME_ICON_MEASURES = {
    "ICON_SCALE": "weight",
    "ICON_SCALE_BATHROOM": "weight",
    "ICON_MAGNET": "magnetic_field",
    "ICON_HEART_PULSE": "biometric",
    "ICON_RADIOACTIVE": "radiation",
    "ICON_FINGERPRINT": "biometric",
    "ICON_ACCOUNT": "face_recognition",
    "ICON_GAS_CYLINDER": "gas",
    "ICON_CHEMICAL_WEAPON": "gas",
    "ICON_MOLECULE_CO2": "co2",
    "ICON_MOLECULE_CO": "co",
    # ICON_LIGHTBULB omitted — used for power/energy, not light sensing
    "ICON_BRIGHTNESS_5": "light",
    "ICON_BRIGHTNESS_6": "light",
    "ICON_BRIGHTNESS_7": "light",
    "ICON_PROXIMITY": "proximity",
    "ICON_HUMAN_GREETING_PROXIMITY": "proximity",
    "ICON_MOTION_SENSOR": "proximity",
    "ICON_MAP_MARKER_DISTANCE": "distance",
    "ICON_RULER": "distance",
    "ICON_ARROW_EXPAND_VERTICAL": "distance",
    "ICON_WEATHER_WINDY": None,
}

# ESPHome component names that are NOT hardware sensor ICs — filter these out
ESPHOME_SKIP_COMPONENTS = {
    # Virtual/calculated
    "absolute_humidity", "adc", "aqi", "binary_sensor_map", "combination",
    "copy", "debug", "duty_cycle", "duty_time", "integration", "internal_temperature",
    "ntc", "pid", "pulse_counter", "pulse_meter", "pulse_width", "resistance",
    "rotary_encoder", "template", "total_daily_energy", "uptime", "wifi_signal",
    # Software/protocol, not a specific IC
    "ble_rssi", "dsmr", "modbus_controller", "packet_transport", "wireguard",
    # BLE consumer devices (not ICs you'd put on a PCB)
    "airthings_wave_mini", "airthings_wave_plus", "alpha3",
    "atc_mithermometer", "b_parasite", "bthome_mithermometer",
    "inkbird_ibsth1_mini", "mopeka_pro_check", "mopeka_std_check",
    "pvvx_mithermometer", "radon_eye_rd200", "ruuvitag", "thermopro_ble",
    "xiaomi_cgd1", "xiaomi_cgdk2", "xiaomi_cgg1", "xiaomi_cgpr1",
    "xiaomi_gcls002", "xiaomi_hhccjcy01", "xiaomi_hhccjcy10",
    "xiaomi_hhccpot002", "xiaomi_jqjcy01ym", "xiaomi_lywsd02",
    "xiaomi_lywsd03mmc", "xiaomi_lywsdcgq", "xiaomi_mhoc303",
    "xiaomi_mhoc401", "xiaomi_miscale", "xiaomi_mjyd02yla",
    "xiaomi_rtcgq02lm", "xiaomi_wx08zm",
    # Industrial/utility meters (not sensor ICs)
    "growatt_solar", "havells_solar", "kamstrup_kmp", "kuntze",
    "sdm_meter", "selec_meter", "pzem004t", "pzemac", "pzemdc",
    # Comms/network modules (not sensors)
    "sim800l",
    # Pure ADCs (not sensors, they just sample voltage)
    "mcp3008", "mcp3204", "mcp3221", "adc128s102",
    # Sensor-dir components that are NOT sensor ICs
    "am43",             # blind motor controller
    "bedjet",           # climate appliance
    "ble_client",       # generic BLE protocol
    "copy",             # virtual copy sensor
    "custom",           # custom component
    "dlms_meter",       # utility meter protocol
    "haier",            # climate appliance
    "homeassistant",    # HA integration
    "lvgl",             # UI framework
    "m5stack_8angle",   # rotary encoder module
    "micronova",        # pellet stove controller
    "mqtt_subscribe",   # MQTT protocol
    "nextion",          # display
    "opentherm",        # heating protocol
    "pipsolar",         # solar inverter
    "pylontech",        # battery BMS
    "sml",              # smart meter protocol
    "sun",              # virtual sun position
    "sy6970",           # battery charger IC
    "teleinfo",         # French utility meter
    "tuya",             # Tuya protocol
    "uponor_smatrix",   # underfloor heating
    "vbus",             # solar thermal protocol
}

# ESPHome names that should map to standard IC names
ESPHOME_NAME_OVERRIDES = {
    "dallas_temp": "ds18b20",
    "sht3xd": "sht3x",
}


def _extract_esphome_measures(all_content: str) -> set[str]:
    """Extract measures from ESPHome component source using all available signals.

    Checks (in order): CONF_* keys, UNIT_* constants, DEVICE_CLASS_*, ICON_*.
    """
    measures = set()

    # 1. CONF_* keys — most reliable (actual sensor output channels)
    for const_name, measure in ESPHOME_CONF_MEASURES.items():
        if re.search(rf'\b{const_name}\b', all_content):
            measures.add(measure)

    # 2. UNIT_* constants — catches accel/gyro/magnetic from unit types
    #    Use word boundary to avoid UNIT_METER matching inside UNIT_METER_PER_SECOND_SQUARED
    for const_name, measure in ESPHOME_UNIT_MEASURES.items():
        if measure and re.search(rf'\b{const_name}\b', all_content):
            measures.add(measure)

    # 3. DEVICE_CLASS_* — fills remaining gaps
    for m in re.finditer(r'DEVICE_CLASS_(\w+)', all_content):
        dc = m.group(1).upper()
        measure = ESPHOME_DEVICE_CLASS_MAP.get(dc)
        if measure:
            measures.add(measure)

    # 4. ICON_* — last resort for specific icons
    for const_name, measure in ESPHOME_ICON_MEASURES.items():
        if measure and re.search(rf'\b{const_name}\b', all_content):
            measures.add(measure)

    # 5. Detect color sensor channels from string literal arrays (e.g., TYPES = ["red", "green", "blue"])
    if re.search(r'"red".*"green".*"blue"', all_content) or re.search(r'"clear".*"red"', all_content):
        measures.add("color")

    return measures


def scrape_esphome(output_dir: Path) -> None:
    """Scrape ESPHome components for sensor protocol, i2c, and measures."""
    source_url = "https://github.com/esphome/esphome"

    with tempfile.TemporaryDirectory() as tmpdir:
        clone_dir = Path(tmpdir) / "esphome"
        logger.info("Cloning ESPHome repository...")
        result = subprocess.run(
            ["git", "clone", "--depth=1", source_url + ".git", str(clone_dir)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git clone failed: {result.stderr}")

        components_dir = clone_dir / "esphome" / "components"
        # Match both */sensor.py and */sensor/__init__.py patterns
        sensor_file_hits = list(components_dir.glob("*/sensor.py"))
        sensor_dir_hits = list(components_dir.glob("*/sensor/__init__.py"))
        # Build list of (sensor_py_path, component_dir) tuples
        sensor_entries = [(f, f.parent) for f in sensor_file_hits]
        sensor_entries += [(f, f.parent.parent) for f in sensor_dir_hits]
        # Deduplicate by component dir (some may have both)
        seen_dirs = set()
        unique_entries = []
        for sensor_py, comp_dir in sensor_entries:
            if comp_dir not in seen_dirs:
                seen_dirs.add(comp_dir)
                unique_entries.append((sensor_py, comp_dir))
        sensor_entries = unique_entries
        logger.info(f"Found {len(sensor_entries)} components with sensor support ({len(sensor_file_hits)} file, {len(sensor_dir_hits)} dir)")

        # Aggregate by normalized IC id (to merge _i2c/_spi variants)
        ic_data: dict[str, dict] = {}
        skipped = 0

        for sensor_py, comp_dir in sensor_entries:
            comp_name = comp_dir.name

            # Skip *_base dirs
            if comp_name.endswith("_base"):
                continue

            # Skip non-sensor components (virtual, BLE consumer, utility meters)
            if comp_name in ESPHOME_SKIP_COMPONENTS:
                skipped += 1
                continue

            # Read sensor.py content
            content = sensor_py.read_text(errors="ignore")

            # Skip fully deprecated components (CONFIG_SCHEMA = cv.invalid(...))
            # but NOT components that only deprecate individual options
            if re.search(r'CONFIG_SCHEMA\s*=\s*cv\.invalid\(', content):
                continue

            # Also read __init__.py if exists
            init_py = comp_dir / "__init__.py"
            init_content = init_py.read_text(errors="ignore") if init_py.exists() else ""
            all_content = content + "\n" + init_content

            # Check for base component and read its __init__.py too
            base_name = re.sub(r'_(i2c|spi|uart)$', '_base', comp_name)
            if base_name != comp_name:
                base_init = components_dir / base_name / "__init__.py"
                if base_init.exists():
                    all_content += "\n" + base_init.read_text(errors="ignore")
                # Also read the base's sensor.py if it exists
                base_sensor = components_dir / base_name / "sensor.py"
                if base_sensor.exists():
                    all_content += "\n" + base_sensor.read_text(errors="ignore")

            # Strip variant suffix to get base IC name
            base_ic = re.sub(r'_(i2c|spi|uart)$', '', comp_name)
            # Apply name overrides (e.g., dallas_temp -> ds18b20)
            ic_id = ESPHOME_NAME_OVERRIDES.get(base_ic, base_ic)
            normalized = normalize_sensor_id(ic_id)
            if normalized:
                ic_id = normalized

            # Protocol detection
            protocols = set()
            if 'i2c.I2CDevice' in all_content or re.search(r'DEPENDENCIES\s*=\s*\[.*"i2c"', all_content):
                protocols.add("i2c")
            if 'spi.SPIDevice' in all_content or re.search(r'DEPENDENCIES\s*=\s*\[.*"spi"', all_content):
                protocols.add("spi")
            if 'uart.UARTDevice' in all_content or re.search(r'DEPENDENCIES\s*=\s*\[.*"uart"', all_content):
                protocols.add("uart")
            if 'one_wire.OneWireDevice' in all_content or re.search(r'DEPENDENCIES\s*=\s*\[.*"one_wire"', all_content):
                protocols.add("one_wire")

            # I2C address
            i2c_addresses = set()
            for m in re.finditer(r'i2c_device_schema\((?:default_address=)?(0x[0-9a-fA-F]+)', all_content):
                addr = m.group(1).lower()
                if addr != "0x00":  # filter invalid
                    i2c_addresses.add(addr)
            for m in re.finditer(r'cv\.Optional.*CONF_ADDRESS.*default\s*=\s*(0x[0-9a-fA-F]+)', all_content):
                addr = m.group(1).lower()
                if addr != "0x00":
                    i2c_addresses.add(addr)

            # Measures: known IC override or source code analysis
            if ic_id in KNOWN_IC_MEASURES:
                measures = set(KNOWN_IC_MEASURES[ic_id])
            else:
                measures = _extract_esphome_measures(all_content)

            # Aggregate variants
            if ic_id not in ic_data:
                ic_data[ic_id] = {
                    "comp_name": base_ic,
                    "protocols": set(),
                    "i2c_addresses": set(),
                    "measures": set(),
                }
            entry = ic_data[ic_id]
            entry["protocols"].update(protocols)
            entry["i2c_addresses"].update(i2c_addresses)
            entry["measures"].update(measures)

        # Build sensor entries — drop sensors with no measures
        sensors = []
        skipped_no_measures = 0
        for ic_id, agg in sorted(ic_data.items()):
            if not agg["measures"]:
                skipped_no_measures += 1
                continue
            docs_url = f"https://esphome.io/components/sensor/{agg['comp_name']}.html"
            sensors.append(make_sensor_entry(
                sensor_id=ic_id,
                name=agg["comp_name"],
                measures=sorted(agg["measures"]),
                platforms=["esphome"],
                urls=[docs_url],
                protocol=sorted(agg["protocols"]),
                i2c_address=sorted(agg["i2c_addresses"]),
            ))

        if skipped_no_measures:
            logger.info(f"Dropped {skipped_no_measures} sensors with no identifiable measures")
        stats = {
            "sensor_count": len(sensors),
            "total_components_checked": len(sensor_entries),
            "skipped_non_sensor": skipped,
            "skipped_no_measures": skipped_no_measures,
        }
        write_source_json("esphome", source_url, sensors, stats, output_dir)
