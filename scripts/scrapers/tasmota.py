"""Tasmota supported peripherals sensor scraper.

Parses the Tasmota Supported Peripherals documentation page to extract
sensor ICs and their interfaces. Adds "tasmota" as a platform tag.
"""

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

SOURCE_URL = "https://tasmota.github.io/docs/Supported-Peripherals/"
DOCS_BASE = "https://tasmota.github.io/docs/"

# Known IC → measures overrides for cases where description text is ambiguous
KNOWN_IC_MEASURES = {
    "ads111x": ["voltage"],
    "aht1x": ["humidity", "temperature"],
    "aht2x": ["humidity", "temperature"],
    "am2301": ["humidity", "temperature"],
    "am2302": ["humidity", "temperature"],
    "am2320": ["humidity", "temperature"],
    "am2321": ["humidity", "temperature"],
    "am2301b": ["humidity", "temperature"],
    "apds9960": ["color", "gesture", "light", "proximity"],
    "bh1750": ["light"],
    "bme280": ["humidity", "pressure", "temperature"],
    "bme680": ["gas", "humidity", "pressure", "temperature", "voc"],
    "bme688": ["gas", "humidity", "pressure", "temperature", "voc"],
    "bmp180": ["pressure", "temperature"],
    "bmp280": ["pressure", "temperature"],
    "ccs811": ["gas", "voc"],
    "dht11": ["humidity", "temperature"],
    "dht21": ["humidity", "temperature"],
    "dht22": ["humidity", "temperature"],
    "ds18x20": ["temperature"],
    "ds18b20": ["temperature"],
    "ens160": ["gas", "voc"],
    "ens161": ["gas", "voc"],
    "ens210": ["humidity", "temperature"],
    "hdc1080": ["humidity", "temperature"],
    "hdc2010": ["humidity", "temperature"],
    "hp303b": ["pressure", "temperature"],
    "htu21": ["humidity", "temperature"],
    "ina219": ["current", "voltage"],
    "ina226": ["current", "voltage"],
    "ina3221": ["current", "voltage"],
    "lm75ad": ["temperature"],
    "lmt01": ["temperature"],
    "max17043": ["voltage"],
    "max31855": ["temperature"],
    "max31865": ["temperature"],
    "max44009": ["light"],
    "mcp9808": ["temperature"],
    "mhz19b": ["co2"],
    "mlx90614": ["ir_temperature"],
    "mlx90640": ["ir_temperature"],
    "mpu6050": ["acceleration", "gyroscope"],
    "mpu6886": ["acceleration", "gyroscope"],
    "paj7620": ["gesture"],
    "pmsa003i": ["particulate"],
    "pms3003": ["particulate"],
    "pms5003": ["particulate"],
    "pms7003": ["particulate"],
    "qmc5883l": ["magnetic_field"],
    "scd30": ["co2", "humidity", "temperature"],
    "scd40": ["co2", "humidity", "temperature"],
    "scd41": ["co2", "humidity", "temperature"],
    "sds011": ["particulate"],
    "sen0390": ["light"],
    "sen5x": ["gas", "humidity", "particulate", "temperature", "voc"],
    "sgp30": ["gas", "voc"],
    "sgp40": ["gas", "voc"],
    "sgp41": ["gas", "voc"],
    "sht1x": ["humidity", "temperature"],
    "sht30": ["humidity", "temperature"],
    "sht3x": ["humidity", "temperature"],
    "sht4x": ["humidity", "temperature"],
    "si114x": ["light", "uv"],
    "si7021": ["humidity", "temperature"],
    "sps30": ["particulate"],
    "t6703": ["co2"],
    "t6713": ["co2"],
    "tc74": ["temperature"],
    "tfmini": ["distance", "lidar"],
    "tsl2561": ["light"],
    "tsl2591": ["light"],
    "veml6070": ["uv"],
    "veml6075": ["uv"],
    "veml7700": ["light"],
    "vl53l0x": ["distance", "tof"],
    "vl53l1x": ["distance", "tof"],
    "hx711": ["weight"],
    "as3935": ["weather"],
    "ags02ma": ["gas", "voc"],
    "icp10125": ["pressure", "temperature"],
    "spl06007": ["pressure", "temperature"],
}

# Non-sensor peripherals to skip
SKIP_PERIPHERALS = {
    "74x595", "a4988", "adc", "as608", "mcp23008", "mcp23017", "mcp23s17",
    "mcp2515", "mfrc522", "nrf24l01", "pca9557", "pca9685", "pca9632",
    "pcf8574", "pcf8574a", "pn532", "rdm6300", "sk6812", "tm1638",
    "vid6608", "ws2812b", "ws2813b", "ws2812bws2813b", "rcwl0516",
    "opentherm", "nepool", "neopool",
}


# Map Tasmota interface strings to normalized protocol names
PROTOCOL_MAP = {
    "i2c": "i2c",
    "spi": "spi",
    "serial": "uart",
    "1wire": "one_wire",
    "1-wire": "one_wire",
    "one wire": "one_wire",
    "gpio": "gpio",
    "analog": "analog",
}


def _parse_protocol(interface_str: str) -> list[str]:
    """Parse Tasmota interface string into normalized protocol list."""
    if not interface_str:
        return []
    protocols = []
    lower = interface_str.lower().strip()
    for key, value in PROTOCOL_MAP.items():
        if key in lower and value not in protocols:
            protocols.append(value)
    return sorted(protocols)


def _extract_ic_ids(name_cell: str) -> list[str]:
    """Extract one or more IC identifiers from a Tasmota peripheral name cell.

    Handles cases like:
    - "AHT1x" -> ["aht1x"]
    - "AM2301 / DHT21 AM2302 / DHT22AM2321" -> ["am2301", "dht21", "am2302", "dht22", "am2321"]
    - "MAX31855MAX6675" -> ["max31855", "max6675"]
    - "PMS3003PMS5003PMS7003PMSx003T" -> ["pms3003", "pms5003", "pms7003"]
    - "SCD40SCD41" -> ["scd40", "scd41"]
    """
    # Clean up separators
    text = name_cell.replace("/", " ").replace(",", " ").replace(";", " ")
    text = re.sub(r'\s+', ' ', text).strip()

    # Split concatenated IC names (e.g., "MAX31855MAX6675" -> "MAX31855 MAX6675")
    text = re.sub(r'([0-9])([A-Z]{2,})', r'\1 \2', text)
    # Also handle single-letter prefix ICs (e.g., "T6703T6713" -> "T6703 T6713")
    text = re.sub(r'([0-9])([A-Z]\d{3,})', r'\1 \2', text)

    # Also split on spaces
    parts = text.split()
    ids = []
    for part in parts:
        ic_id = normalize_sensor_id(part)
        if ic_id and ic_id not in ids:
            ids.append(ic_id)
    return ids


def scrape_tasmota(output_dir: Path) -> None:
    """Scrape Tasmota Supported Peripherals page for sensor ICs."""
    logger.info("Downloading Tasmota Supported Peripherals page...")
    resp = wafer.get(SOURCE_URL, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # Extract table rows: <tr><td>Name</td><td>Description</td><td>Interface</td></tr>
    rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)

    ic_data: dict[str, dict] = {}
    total_rows = 0
    skipped_non_sensor = 0

    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if not cells or len(cells) < 2:
            continue

        total_rows += 1

        # Extract doc URL from name cell before stripping HTML
        # Relative links: href=../AHT1x/ -> https://tasmota.github.io/docs/AHT1x/
        # Absolute links: href=https://github.com/... -> use as-is
        href_match = re.search(r'href=["\']?(\.\./([\w%-]+)/|https?://\S+)', cells[0])
        if href_match:
            if href_match.group(2):
                doc_url = f"{DOCS_BASE}{href_match.group(2)}/"
            else:
                doc_url = href_match.group(1).rstrip("> ")
        else:
            doc_url = None

        # Clean HTML tags from cells
        name_cell = re.sub(r'<[^>]+>', '', cells[0]).strip()
        desc_cell = re.sub(r'<[^>]+>', '', cells[1]).strip()
        iface_cell = re.sub(r'<[^>]+>', '', cells[2]).strip() if len(cells) > 2 else ""

        # Extract IC IDs from name cell
        ic_ids = _extract_ic_ids(name_cell)
        if not ic_ids:
            continue

        # Skip known non-sensor peripherals
        if all(ic_id in SKIP_PERIPHERALS for ic_id in ic_ids):
            skipped_non_sensor += 1
            continue

        # Skip obvious non-sensors by description
        desc_lower = desc_cell.lower()
        if any(skip in desc_lower for skip in [
            'led controller', 'led driver', 'shift register', 'i/o expander',
            'io expander', 'can bus', 'nfc', 'rfid', 'rf sensor receiver',
            'ir receiver', 'ir transmitter', 'stepper motor', 'pwm',
            'addressable led', 'energy monitor', 'energy meter', 'modbus',
            'inverter', 'smart meter', 'fingerprint',
        ]):
            skipped_non_sensor += 1
            continue

        # Parse protocol
        protocol = _parse_protocol(iface_cell)

        # Build combined text for measure inference
        combined_text = f"{name_cell} {desc_cell}"

        for ic_id in ic_ids:
            if ic_id in SKIP_PERIPHERALS:
                continue

            # Determine measures
            if ic_id in KNOWN_IC_MEASURES:
                measures = KNOWN_IC_MEASURES[ic_id]
            else:
                measures = infer_measures(combined_text)
                if not measures:
                    continue

            # Check IC pattern (unless in known overrides)
            if ic_id not in KNOWN_IC_MEASURES and not has_ic_pattern(ic_id):
                continue

            if ic_id not in ic_data:
                ic_data[ic_id] = {
                    "name": ic_id.upper(),
                    "measures": set(),
                    "protocol": set(),
                    "description": desc_cell,
                    "url": doc_url,
                }

            entry = ic_data[ic_id]
            entry["measures"].update(measures)
            if protocol:
                entry["protocol"].update(protocol)
            # Keep longer description
            if len(desc_cell) > len(entry.get("description", "")):
                entry["description"] = desc_cell

    # Build output
    sensors = []
    skipped_no_measures = 0
    for ic_id, agg in sorted(ic_data.items()):
        if not agg["measures"]:
            skipped_no_measures += 1
            continue

        desc = agg["description"]
        if desc and len(desc) > 200:
            desc = desc[:197] + "..."

        urls = [agg["url"]] if agg.get("url") else None
        entry = make_sensor_entry(
            sensor_id=ic_id,
            name=agg["name"],
            measures=sorted(agg["measures"]),
            platforms=["tasmota"],
            description=desc if desc else None,
            protocol=sorted(agg["protocol"]) if agg["protocol"] else None,
            urls=urls,
        )
        sensors.append(entry)

    stats = {
        "sensor_count": len(sensors),
        "total_rows_checked": total_rows,
        "skipped_non_sensor": skipped_non_sensor,
        "skipped_no_measures": skipped_no_measures,
    }
    write_source_json("tasmota", SOURCE_URL, sensors, stats, output_dir)
