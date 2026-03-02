"""Awesome-MicroPython sensor scraper."""

import logging
import re
from pathlib import Path

import wafer

from .common import (
    has_ic_pattern,
    infer_measures,
    make_sensor_entry,
    normalize_sensor_id,
    write_source_json,
)

logger = logging.getLogger(__name__)

# Known IC → measures override. Checked BEFORE category/text inference to fix
# cases where MicroPython library descriptions trigger wrong keywords.
KNOWN_IC_MEASURES = {
    "qmc5883l": ["magnetic_field"],
    "pms5003": ["particulate"],
    "pms7003": ["particulate"],
    "sds011": ["particulate"],
    "scd30": ["co2", "humidity", "temperature"],
    "scd4x": ["co2", "humidity", "temperature"],
    "max30102": ["biometric"],
    "as3935": ["weather"],
    "bmp280": ["pressure", "temperature"],
    "sht3x": ["humidity", "temperature"],
    "ina219": ["current", "voltage"],
    "mpu6050": ["acceleration", "gyroscope", "temperature"],
}

# MicroPython category -> measures mapping
MICROPYTHON_CATEGORY_MEASURES = {
    "Accelerometer": ["acceleration"],
    "Accelerometer Digital": ["acceleration"],
    "Air Quality": ["gas"],
    "Barometer": ["pressure"],
    "Biometric": ["biometric"],
    "Colour": ["color"],
    "Compass": ["magnetic_field"],
    "Current": ["current"],
    "Distance IR": ["distance"],
    "Distance Laser": ["distance"],
    "Distance Ultrasonic": ["distance"],
    "Dust": ["particulate"],
    "Energy": ["current", "voltage"],
    "Fingerprint": ["biometric"],
    "Flow": ["flow"],
    "Gaseous": ["gas"],
    "Heart Rate": ["biometric"],
    "Human Presence": ["proximity"],
    "Humidity": ["humidity"],
    "Light": ["light"],
    "Load Cell": ["weight"],
    "Magnetic": ["magnetic_field"],
    "Magnetometer": ["magnetic_field"],
    "Motion Inertial": ["acceleration", "gyroscope"],
    "Pressure": ["pressure"],
    "Proximity": ["proximity"],
    "Radiation": ["radiation"],
    "Soil Moisture": ["soil_moisture"],
    "Sound": ["sound"],
    "Spectral": ["color"],
    "Temperature Analog": ["temperature"],
    "Temperature Digital": ["temperature"],
    "Temperature IR": ["ir_temperature"],
    "Touch Capacitive": ["touch"],
    "Touch Resistive": ["touch"],
    "Weight": ["weight"],
}


def scrape_micropython(output_dir: Path) -> None:
    """Scrape awesome-micropython for sensor entries with category-inferred measures."""
    source_url = "https://raw.githubusercontent.com/mcauser/awesome-micropython/master/readme.md"
    logger.info("Downloading awesome-micropython readme...")
    resp = wafer.get(source_url, timeout=30)
    resp.raise_for_status()
    md_text = resp.text

    lines = md_text.split("\n")

    # Find the Sensors section (could be ## or ### depending on nesting)
    in_sensors = False
    sensor_level = 0
    current_category = None
    entry_re = re.compile(r'\*\s+\[([^\]]+)\]\(([^)]+)\)\s*[-\u2013\u2014]\s*(.+)')
    ic_data: dict[str, dict] = {}

    for line in lines:
        stripped = line.strip()

        # Detect Sensors section start (## or ###)
        sensor_match = re.match(r'^(#{2,3})\s+Sensors\b', stripped)
        if sensor_match and not in_sensors:
            in_sensors = True
            sensor_level = len(sensor_match.group(1))
            continue
        if not in_sensors:
            continue

        # Detect end of Sensors section: same or higher level heading that isn't a subsection
        end_match = re.match(r'^(#{2,})\s+', stripped)
        if end_match:
            level = len(end_match.group(1))
            if level <= sensor_level and 'Sensors' not in stripped:
                break
            # Subsection header (one level deeper = category)
            if level == sensor_level + 1:
                # Strip common suffixes from category for better matching
                cat_text = stripped.lstrip('#').strip()
                # Try to match "Barometer - Air and Water Pressure" -> "Barometer"
                cat_key = cat_text.split(' - ')[0].strip()
                current_category = cat_key
                continue

        # Parse entries
        m = entry_re.match(stripped)
        if not m:
            continue

        entry_name, entry_url, description = m.group(1), m.group(2), m.group(3)

        # Strip micropython and i2c/spi/uart prefixes
        clean_name = re.sub(r'^micropython[_-]', '', entry_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'^(?:i2c|spi|uart)[_-]', '', clean_name, flags=re.IGNORECASE)

        # Try normalize on name first (max 15 chars — longer means mangled name)
        ic_id = normalize_sensor_id(clean_name)
        if ic_id and (not has_ic_pattern(ic_id) or len(ic_id) > 15):
            ic_id = None

        # Fallback: regex on description
        if not ic_id:
            ic_match = re.search(r'\b([A-Z]{2,}[\-]?[0-9]{2,}[A-Z0-9]*)\b', description)
            if ic_match:
                candidate = normalize_sensor_id(ic_match.group(1))
                if candidate and has_ic_pattern(candidate):
                    ic_id = candidate

        # Fallback: regex on name
        if not ic_id:
            ic_match = re.search(r'\b([A-Za-z]{2,}[\-]?[0-9]{2,}[A-Za-z0-9]*)\b', clean_name)
            if ic_match:
                candidate = normalize_sensor_id(ic_match.group(1))
                if candidate and has_ic_pattern(candidate):
                    ic_id = candidate

        if not ic_id:
            continue

        # Skip non-sensor categories
        skip_categories = {"Camera", "Battery", "Radar"}
        if current_category in skip_categories:
            continue

        # Measures: known IC override first, then category + description
        if ic_id in KNOWN_IC_MEASURES:
            all_measures = KNOWN_IC_MEASURES[ic_id]
        else:
            category_measures = []
            if current_category and current_category in MICROPYTHON_CATEGORY_MEASURES:
                category_measures = MICROPYTHON_CATEGORY_MEASURES[current_category]
            desc_measures = infer_measures(description)
            all_measures = sorted(set(category_measures + desc_measures))

        if ic_id not in ic_data:
            ic_data[ic_id] = {
                "name": clean_name,
                "measures": set(),
                "urls": [],
                "descriptions": [],
            }
        entry = ic_data[ic_id]
        entry["measures"].update(all_measures)
        if entry_url and entry_url not in entry["urls"]:
            entry["urls"].append(entry_url)
        if description:
            entry["descriptions"].append(description)

    sensors = []
    for ic_id, agg in sorted(ic_data.items()):
        best_desc = max(agg["descriptions"], key=len) if agg["descriptions"] else None
        if best_desc and len(best_desc) > 200:
            best_desc = best_desc[:197] + "..."
        sensors.append(make_sensor_entry(
            sensor_id=ic_id,
            name=agg["name"],
            measures=sorted(agg["measures"]),
            platforms=["micropython"],
            urls=agg["urls"][:10],
            description=best_desc,
        ))

    stats = {
        "sensor_count": len(sensors),
    }
    write_source_json("micropython", source_url, sensors, stats, output_dir)
