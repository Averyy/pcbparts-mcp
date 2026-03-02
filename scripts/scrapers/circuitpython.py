"""CircuitPython driver list sensor scraper."""

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

# Known IC → measures override. Checked BEFORE text inference to fix
# cases where CircuitPython driver titles trigger wrong keywords.
KNOWN_IC_MEASURES = {
    "pm25": ["particulate"],
    "scd4x": ["co2", "humidity", "temperature"],
    "ahtx0": ["humidity", "temperature"],
    "as3935": ["weather"],
    "bmp280": ["pressure", "temperature"],
    "ens160": ["gas", "voc"],
    "sen6x": ["gas", "humidity", "particulate", "temperature", "voc"],
    "as7341": ["color", "light"],
    "mlx90640": ["ir_temperature"],
    "opt4048": ["color", "light"],
    "dht": ["humidity", "temperature"],
    "mprls": ["pressure"],
    "ltr329ltr303": ["light"],
    "dht": ["humidity", "temperature"],
    "mprls": ["pressure"],
}

# CircuitPython section -> base measures (titles are rich enough for infer_measures to refine)
CIRCUITPYTHON_SECTION_MEASURES = {
    "motion-sensors": [],       # descriptions specify accel/gyro/mag/GPS
    "environmental-sensors": [],  # descriptions specify temp/humidity/pressure/gas
    "light-sensors": [],        # descriptions specify light/color/UV/proximity
    "distance-sensors": ["distance"],
}


def scrape_circuitpython(output_dir: Path) -> None:
    """Scrape CircuitPython driver list with per-section category awareness."""
    url = "https://docs.circuitpython.org/projects/bundle/en/latest/drivers.html"
    logger.info("Downloading CircuitPython driver list...")
    resp = wafer.get(url, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # Split HTML by section headers to get section -> entries mapping
    # Each section link: <a class="reference internal" href="#section-id">Title</a>
    # Each entry link: <a class="reference external" href="url">Title (adafruit_name)</a>
    entry_re = re.compile(
        r'<a class="reference external" href="([^"]+)">([^<]+)</a>'
    )
    driver_name_re = re.compile(r'\(adafruit[_-]([\w-]+)\)')

    # Parse sections: split on internal reference links
    parts = re.split(r'<a class="reference internal" href="#([^"]+)">', html)

    ic_data: dict[str, dict] = {}
    sensor_sections = set(CIRCUITPYTHON_SECTION_MEASURES.keys())
    # Also scrape miscellaneous, but only keep entries that match sensor keywords
    scrape_sections = sensor_sections | {"miscellaneous"}

    total_entries = 0
    for i in range(1, len(parts), 2):
        section_id = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""

        if section_id not in scrape_sections:
            continue

        is_sensor_section = section_id in sensor_sections
        base_measures = CIRCUITPYTHON_SECTION_MEASURES.get(section_id, [])

        for url_match in entry_re.finditer(content):
            entry_url, entry_title = url_match.groups()
            total_entries += 1

            # Extract driver name (adafruit_xxx)
            name_match = driver_name_re.search(entry_title)
            if not name_match:
                # Fallback: extract project name from URL path
                # e.g. "https://docs.circuitpython.org/projects/opt4048/en/latest/"
                url_name_match = re.search(r'/projects/([^/]+)/', entry_url)
                if not url_name_match:
                    continue
                driver_name = url_name_match.group(1)
            else:
                driver_name = name_match.group(1)

            # Normalize to IC id
            ic_id = normalize_sensor_id(driver_name)
            if not ic_id:
                continue
            # Skip IC pattern check for known overrides (e.g. "dht", "mprls")
            if ic_id not in KNOWN_IC_MEASURES and not has_ic_pattern(ic_id):
                continue

            # Extract title text before the (adafruit_xxx) part
            # Use rsplit on "(adafruit" to avoid truncating titles with other parentheses
            # e.g. "ENS160 (ScioSense) digital multi-gas sensor (adafruit_ens160)"
            title_text = re.split(r'\(adafruit[_-]', entry_title)[0].strip()

            # Measures: known IC override first, then title inference
            if ic_id in KNOWN_IC_MEASURES:
                all_measures = KNOWN_IC_MEASURES[ic_id]
            else:
                title_measures = infer_measures(title_text)
                all_measures = sorted(set(base_measures + title_measures))

            # For miscellaneous section, only include entries with detected measures
            # AND filter out non-sensor ICs (LED drivers, DACs, motor controllers, etc.)
            if not is_sensor_section:
                if not all_measures:
                    continue
                title_lower = title_text.lower()
                if any(skip in title_lower for skip in [
                    'led driver', 'led matrix', 'display', 'motor', 'servo',
                    'relay', 'dac ', 'eeprom', 'shift register', 'io expander',
                    'neopixel', 'dotstar', 'pwm', 'lcd', 'oled', 'tft',
                    'keyboard', 'keypad', 'rfid', 'nfc', 'gps receiver',
                ]):
                    continue

            # Build docs URL from entry URL
            docs_url = entry_url

            if ic_id not in ic_data:
                ic_data[ic_id] = {
                    "name": driver_name,
                    "title": title_text,
                    "measures": set(),
                    "urls": [],
                }
            entry = ic_data[ic_id]
            entry["measures"].update(all_measures)
            if docs_url and docs_url not in entry["urls"]:
                entry["urls"].append(docs_url)
            # Keep the more descriptive title
            if len(title_text) > len(entry["title"]):
                entry["title"] = title_text

    sensors = []
    skipped_no_measures = 0
    for ic_id, agg in sorted(ic_data.items()):
        if not agg["measures"]:
            skipped_no_measures += 1
            continue
        desc = agg["title"] if agg["title"] != agg["name"] else None
        if desc and len(desc) > 200:
            desc = desc[:197] + "..."
        sensors.append(make_sensor_entry(
            sensor_id=ic_id,
            name=agg["name"],
            measures=sorted(agg["measures"]),
            platforms=["circuitpython"],
            urls=agg["urls"][:5],
            description=desc,
        ))

    if skipped_no_measures:
        logger.info(f"Dropped {skipped_no_measures} sensors with no identifiable measures")
    stats = {
        "sensor_count": len(sensors),
        "total_entries_checked": total_entries,
        "skipped_no_measures": skipped_no_measures,
    }
    write_source_json("circuitpython", url, sensors, stats, output_dir)
