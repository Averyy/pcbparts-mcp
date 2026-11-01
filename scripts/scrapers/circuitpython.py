"""CircuitPython driver list sensor scraper.

Reads the Adafruit bundle's ``docs/drivers.rst`` from GitHub, the source of
https://docs.circuitpython.org/projects/bundle/en/latest/drivers.html. The
rendered page sits behind Read the Docs' Cloudflare, which answered the
GitHub Actions runner with a managed challenge (HTTP 429) on 2026-11-01;
solving one takes a browser.
"""

import logging
import re
from pathlib import Path

import wafer

from .common import (
    attempt_cap,
    has_ic_pattern,
    infer_measures,
    make_sensor_entry,
    normalize_sensor_id,
    write_source_json,
)

logger = logging.getLogger(__name__)

SOURCE_URL = (
    "https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/"
    "main/docs/drivers.rst"
)

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
}

# CircuitPython section -> base measures (titles are rich enough for infer_measures to refine)
CIRCUITPYTHON_SECTION_MEASURES = {
    "motion-sensors": [],       # descriptions specify accel/gyro/mag/GPS
    "environmental-sensors": [],  # descriptions specify temp/humidity/pressure/gas
    "light-sensors": [],        # descriptions specify light/color/UV/proximity
    "distance-sensors": ["distance"],
}

# Outside the sensor sections, a title with one of these is not a sensor driver
NON_SENSOR_TITLE_WORDS = [
    'led driver', 'led matrix', 'display', 'motor', 'servo',
    'relay', 'dac ', 'eeprom', 'shift register', 'io expander',
    'neopixel', 'dotstar', 'pwm', 'lcd', 'oled', 'tft',
    'keyboard', 'keypad', 'rfid', 'nfc', 'gps receiver',
]

# A heading underline: one punctuation character repeated
_UNDERLINE_RE = re.compile(r'([=\-^~"\'`#*+.:_])\1{2,}\s*')
# A toctree entry with an explicit title: "    Title (adafruit_name) <url>"
_TOCTREE_ENTRY_RE = re.compile(r'\s+(.+?)\s*<(https?://[^\s>]+)>\s*')
_DRIVER_NAME_RE = re.compile(r'\(adafruit[_-]([\w-]+)\)')


def _section_id(title: str) -> str:
    """Sphinx's anchor for a heading: "E-Paper / E-Ink" -> "e-paper-e-ink"."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def parse_drivers_rst(text: str) -> list[tuple[str, str, str]]:
    """Return (section_id, url, title) for every toctree entry in drivers.rst.

    Each entry is filed under the nearest heading above it, at any level, so
    entries under "Displays" > "OLED" get "oled".
    """
    lines = text.splitlines()
    entries: list[tuple[str, str, str]] = []
    section_id = ""
    in_toctree = False
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        if not line[0].isspace():
            in_toctree = line.startswith(".. toctree::")
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if (
                not in_toctree
                and not _UNDERLINE_RE.fullmatch(line)
                and _UNDERLINE_RE.fullmatch(next_line)
            ):
                section_id = _section_id(line)
            continue
        if in_toctree:
            match = _TOCTREE_ENTRY_RE.fullmatch(line)
            if match:
                entries.append((section_id, match.group(2), match.group(1)))
    return entries


def extract_sensors(entries: list[tuple[str, str, str]]) -> tuple[list[dict], dict]:
    """Turn parsed driver entries into sensor entries and stats.

    Every entry in the four sensor sections is a candidate. Elsewhere
    (Miscellaneous, IO Expansion, Displays, Motor Helpers...) an entry is kept
    only when its title names something measured and isn't a display, motor
    or similar driver: MPR121 is listed under IO Expansion, TSC2007 under
    Displays > Other and EMC2101 under Motor Helpers.
    """
    sections = {section_id for section_id, _, _ in entries}
    missing = sorted(set(CIRCUITPYTHON_SECTION_MEASURES) - sections)
    if missing:
        raise ValueError(
            f"drivers.rst has no {', '.join(missing)} section; "
            "its layout changed, update CIRCUITPYTHON_SECTION_MEASURES"
        )

    ic_data: dict[str, dict] = {}
    total_entries = 0
    for section_id, entry_url, entry_title in entries:
        total_entries += 1
        is_sensor_section = section_id in CIRCUITPYTHON_SECTION_MEASURES
        base_measures = CIRCUITPYTHON_SECTION_MEASURES.get(section_id, [])

        # Extract driver name (adafruit_xxx)
        name_match = _DRIVER_NAME_RE.search(entry_title)
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

        # Outside the sensor sections, only include entries with detected measures
        # AND filter out non-sensor ICs (LED drivers, DACs, motor controllers, etc.)
        if not is_sensor_section:
            if not all_measures:
                continue
            title_lower = title_text.lower()
            if any(skip in title_lower for skip in NON_SENSOR_TITLE_WORDS):
                continue

        if ic_id not in ic_data:
            ic_data[ic_id] = {
                "name": driver_name,
                "title": title_text,
                "measures": set(),
                "urls": [],
            }
        entry = ic_data[ic_id]
        entry["measures"].update(all_measures)
        if entry_url and entry_url not in entry["urls"]:
            entry["urls"].append(entry_url)
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
    return sensors, stats


def scrape_circuitpython(output_dir: Path) -> None:
    """Scrape the CircuitPython driver list with per-section category awareness."""
    logger.info("Downloading CircuitPython driver list...")
    resp = wafer.get(SOURCE_URL, timeout=30, attempt_timeout=attempt_cap(30))
    resp.raise_for_status()
    sensors, stats = extract_sensors(parse_drivers_rst(resp.text))
    write_source_json("circuitpython", SOURCE_URL, sensors, stats, output_dir)
