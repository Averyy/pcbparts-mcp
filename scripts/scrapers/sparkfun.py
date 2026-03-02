"""SparkFun sensor scraper (Magento GraphQL API)."""

import json
import logging
import re
from html import unescape
from pathlib import Path

import wafer

from .common import (
    has_ic_pattern,
    infer_measures,
    make_sensor_entry,
    normalize_sensor_id,
    write_source_json,
)

# Known IC → measures override. Checked BEFORE infer_measures to avoid
# false positives from marketing descriptions.
KNOWN_IC_MEASURES = {
    "ah1815": ["magnetic_field"],
    "us1881": ["magnetic_field"],
    "fs3000": ["flow"],
    "fs30001005": ["flow"],
    "fs30001015": ["flow"],
    "tmf8820": ["distance", "tof"],
    "tmf8821": ["distance", "tof"],
    "bme680": ["gas", "humidity", "pressure", "temperature", "voc"],
    "apds9960": ["color", "gesture", "light", "proximity"],
    "max30101": ["biometric"],
    "max30102": ["biometric"],
    "as3935": ["weather"],
    "temt6000": ["light"],
    "vl53l5cx": ["distance", "tof"],
    "hcsr04": ["distance", "ultrasonic"],
    "scd41": ["co2", "humidity", "temperature"],
    "adxl345": ["acceleration"],
    "amg8833": ["ir_temperature"],
    "mpu6050": ["acceleration", "gyroscope", "temperature"],
    "mq3": ["gas"],
    "mq4": ["gas"],
    "mq6": ["gas"],
    "mq7": ["gas"],
    "mq8": ["gas"],
    "paa5160e1": ["motion"],
}

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://www.sparkfun.com/graphql"
SENSORS_CATEGORY_UID = "OTUy"  # sensors category in Magento
PAGE_SIZE = 50

# SKU prefixes that are NOT sensors (kits, cables, wireless tags, etc.)
SKIP_SKU_PREFIXES = {"KIT-", "WRL-", "CAB-", "PRT-", "ROB-", "TOL-", "DD-"}

# Product name patterns to skip (non-sensor items in sensor category)
SKIP_PATTERNS = re.compile(
    r'(?i)(?:'
    r'vision\s+kit|starter\s+kit|rfid|nfc|fingerprint|camera\s+module|'
    r'raspberry\s+pi\s+(?:camera|ai\s+camera|global)|'
    r'lens\b|m12\s+mount|cable\b|adapter|shield\b.*(?:ding|dent)|'
    r'gradiometer\s+kit|code\s+reader|person\s+sensor|'
    r'potentiometer|magnetopot|wireless\s+shield|'
    r'motor\s+driver|servo|stepper|'
    r'barcode|qr\s*code|'
    r'stereo\s+camera|imaging\s+camera|cmos\s+imaging|openmv|'
    r'ir\s+receiver\s+diode|infrared\s+emitter|photo\s+interrupter|'
    r'coulomb\s+counter|'
    r'led\s+module|led\s+driver'
    r')'
)

# IC extraction patterns — ordered by specificity
# Pattern: "SparkFun [Type] - IC_NAME (Qwiic)" or "Name - IC_NAME"
_IC_AFTER_DASH = re.compile(r'[-–]\s*([A-Za-z][A-Za-z0-9]+-?[A-Za-z0-9]*\d[A-Za-z0-9]*)')
# Pattern: IC in parentheses: "(BME280)" but NOT "(Qwiic)" "(Color)" etc.
_IC_IN_PARENS = re.compile(r'\(([A-Za-z][A-Za-z0-9]+-?[A-Za-z0-9]*\d[A-Za-z0-9]*)\)')
# Pattern: any IC-like token in the name
_IC_ANYWHERE = re.compile(r'\b([A-Za-z]{2,}[\-]?\d+[A-Za-z0-9]*)\b')

# Known non-IC tokens that look like ICs but aren't
_FALSE_IC_PATTERNS = {
    "SR04",   # generic ultrasonic, keep but note
    "2MP", "5MP", "8MP", "12MP",  # megapixels
    "3V3", "5V0",  # voltages
    "2X2", "4X4", "8X8",  # matrix sizes
    "50MM", "100MM",  # sizes
    "20CM", "25CM",  # distances
    "3NOI",  # "3 NoIR" fragment
    "RT1062",  # OpenMV camera processor, not a sensor
    "FPC2534",  # Fingerprint sensor
    "SM24", "SM-24",  # Geophone element, very niche (not a sensor IC)
    "LTE302",  # IR emitter, not sensor
    "HM01B0",  # Camera sensor, not a traditional sensor
    "EX8036",  # Stereo camera
    "GP1A57HRJ00F",  # Photo interrupter
    "QRD1114",  # Optical detector/phototransistor
    "LTC4150",  # Coulomb counter, not a sensor
    "DE2120",  # Barcode scanner
}

# Combo board IC separators — products with multiple ICs like "ENS160/BME280"
_COMBO_SPLIT = re.compile(r'[/,&]\s*')


# Common IC package suffixes to strip (TI, Renesas, etc.)
# These appear in full MPNs: OPT4048DTSR → OPT4048, MS5803-14BA → MS580314BA
_PACKAGE_SUFFIXES = re.compile(r'(DTSR|DTSS|DGS|DBV|DGK|RGT|RSB|PWR|PW|NK|NR)$', re.IGNORECASE)


def _extract_ics(name: str) -> list[str]:
    """Extract IC part numbers from a SparkFun product name.

    Returns list of normalized sensor IDs, or empty list if none found.
    Handles combo boards like "ENS160/BME280".
    """
    results = []

    def _normalize_and_strip_pkg(raw: str) -> str | None:
        """Normalize IC name and strip common package suffixes."""
        # Strip package suffix before normalizing
        stripped = _PACKAGE_SUFFIXES.sub('', raw)
        normalized = normalize_sensor_id(stripped)
        if normalized and has_ic_pattern(normalized):
            return normalized
        # Try without stripping in case it's part of the actual IC name
        normalized = normalize_sensor_id(raw)
        if normalized and has_ic_pattern(normalized):
            return normalized
        return None

    # Strategy 1: IC after dash separator (most reliable)
    m = _IC_AFTER_DASH.search(name)
    if m:
        raw = m.group(1)
        # Check for combo boards
        parts = _COMBO_SPLIT.split(raw) if ("/" in raw or "," in raw) else [raw]
        for part in parts:
            part = part.strip()
            if part.upper() in _FALSE_IC_PATTERNS:
                continue
            normalized = _normalize_and_strip_pkg(part)
            if normalized:
                results.append(normalized)
        if results:
            return results

    # Strategy 2: IC in parentheses
    for m in _IC_IN_PARENS.finditer(name):
        raw = m.group(1)
        if raw.upper() in _FALSE_IC_PATTERNS:
            continue
        normalized = _normalize_and_strip_pkg(raw)
        if normalized:
            results.append(normalized)
    if results:
        return results

    # Strategy 3: Any IC-like pattern
    for m in _IC_ANYWHERE.finditer(name):
        raw = m.group(1)
        if raw.upper() in _FALSE_IC_PATTERNS:
            continue
        # Skip common non-IC words
        if raw.upper() in {"USB", "RFID", "LED", "LCD", "OLED", "RGB", "GPS", "NFC"}:
            continue
        normalized = _normalize_and_strip_pkg(raw)
        if normalized:
            results.append(normalized)
            break  # Only take first match for fallback

    return results


def _fetch_all_products() -> list[dict]:
    """Fetch all sensor products from SparkFun GraphQL API."""
    query = """
    {{
        products(
            filter: {{ category_uid: {{ eq: "{cat_uid}" }} }}
            pageSize: {page_size}
            currentPage: {page}
        ) {{
            total_count
            items {{
                name
                sku
                url_key
                short_description {{ html }}
            }}
        }}
    }}
    """

    all_items = []
    page = 1
    total = None

    while True:
        q = query.format(cat_uid=SENSORS_CATEGORY_UID, page_size=PAGE_SIZE, page=page)
        resp = wafer.post(
            GRAPHQL_URL,
            json={"query": q},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        products_data = data.get("data", {}).get("products", {})
        items = products_data.get("items", [])
        if total is None:
            total = products_data.get("total_count", 0)
            logger.info(f"SparkFun reports {total} sensor products")

        if not items:
            break

        all_items.extend(items)
        logger.info(f"  Page {page}: {len(items)} items (total so far: {len(all_items)})")

        if len(all_items) >= total:
            break
        page += 1

        # Safety limit
        if page > 20:
            logger.warning("SparkFun: hit page safety limit")
            break

    return all_items


def scrape_sparkfun(output_dir: Path) -> None:
    """Scrape SparkFun Magento store for sensor breakout boards."""
    logger.info("Fetching SparkFun sensor catalog via GraphQL...")
    products = _fetch_all_products()
    logger.info(f"Downloaded {len(products)} products")

    # Aggregate by IC — multiple products may use the same IC
    ic_data: dict[str, dict] = {}
    skipped_sku = 0
    skipped_pattern = 0
    skipped_no_ic = 0

    for product in products:
        name = product.get("name", "")
        sku = product.get("sku", "")
        url_key = product.get("url_key", "")
        short_desc_html = (product.get("short_description") or {}).get("html", "")

        # Filter by SKU prefix
        if any(sku.startswith(p) for p in SKIP_SKU_PREFIXES):
            skipped_sku += 1
            continue

        # Filter by name pattern
        if SKIP_PATTERNS.search(name):
            skipped_pattern += 1
            continue

        # Extract IC(s)
        ic_ids = _extract_ics(name)
        if not ic_ids:
            skipped_no_ic += 1
            continue

        # Build product URL
        product_url = f"https://www.sparkfun.com/{url_key}.html" if url_key else None

        # Clean description
        desc = re.sub(r'<[^>]+>', ' ', short_desc_html).strip()
        desc = unescape(desc)
        desc = re.sub(r'\s+', ' ', desc)
        if len(desc) > 200:
            desc = desc[:197] + "..."
        if not desc:
            desc = None

        # Detect protocol from name
        protocols = []
        name_lower = name.lower()
        if "qwiic" in name_lower or "i2c" in name_lower:
            protocols.append("i2c")
        if "spi" in name_lower:
            protocols.append("spi")
        if "uart" in name_lower or "serial" in name_lower:
            protocols.append("uart")
        # Also check description for protocols not in title
        desc_lower = (short_desc_html or "").lower()
        if "i2c" in desc_lower and "i2c" not in protocols:
            protocols.append("i2c")
        if "spi" in desc_lower and "spi" not in protocols:
            protocols.append("spi")

        # Infer measures from name + description
        combined_text = f"{name} {short_desc_html}"
        text_measures = infer_measures(combined_text)

        for ic_id in ic_ids:
            if ic_id not in ic_data:
                ic_data[ic_id] = {
                    "names": [],
                    "urls": [],
                    "descriptions": [],
                    "measures": set(),
                    "protocols": set(),
                    "has_override": False,
                }
            entry = ic_data[ic_id]
            entry["names"].append(name)
            if product_url and product_url not in entry["urls"]:
                entry["urls"].append(product_url)
            if desc:
                entry["descriptions"].append(desc)
            # Use known IC measures as override (more reliable than text inference)
            if ic_id in KNOWN_IC_MEASURES and not entry["has_override"]:
                entry["measures"].update(KNOWN_IC_MEASURES[ic_id])
                entry["has_override"] = True
            elif not entry["has_override"]:
                entry["measures"].update(text_measures)
            entry["protocols"].update(protocols)

    # Build sensor entries
    sensors = []
    skipped_no_measures = 0
    for ic_id, data in sorted(ic_data.items()):
        # Skip entries with no measures (dev boards, cameras, etc.)
        if not data["measures"]:
            skipped_no_measures += 1
            continue

        # Best name: shortest product name
        best_name = min(data["names"], key=len) if data["names"] else ic_id.upper()
        # Best description: longest available
        best_desc = max(data["descriptions"], key=len) if data["descriptions"] else None

        sensors.append(make_sensor_entry(
            sensor_id=ic_id,
            name=best_name,
            measures=sorted(data["measures"]),
            platforms=[],
            urls=data["urls"][:5],
            description=best_desc,
            protocol=sorted(data["protocols"]) or None,
        ))

    logger.info(
        f"Extracted {len(sensors)} unique ICs from {len(products)} products "
        f"(skipped: {skipped_sku} SKU, {skipped_pattern} pattern, {skipped_no_ic} no-IC)"
    )
    stats = {
        "sensor_count": len(sensors),
        "total_products": len(products),
        "skipped_sku_prefix": skipped_sku,
        "skipped_pattern": skipped_pattern,
        "skipped_no_ic": skipped_no_ic,
    }
    write_source_json("sparkfun", GRAPHQL_URL, sensors, stats, output_dir)
