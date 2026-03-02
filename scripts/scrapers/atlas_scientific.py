"""Atlas Scientific water quality sensor scraper."""

import logging
import re
from pathlib import Path

import wafer

from .common import make_sensor_entry, write_source_json

logger = logging.getLogger(__name__)

BASE_URL = "https://atlas-scientific.com"

# Category pages to scrape for products
CATEGORY_PAGES = [
    "/probes/",
    "/embedded-solutions/",
    "/ezo-complete/",
]

# Product name patterns → (sensor_id, measures, display_name)
# Order matters: more specific patterns first
PRODUCT_PATTERNS = [
    # EZO embedded circuits (the main boards)
    (r"EZO.*pH\b", "ezo-ph", ["ph"], "EZO-pH"),
    (r"EZO.*ORP\b", "ezo-orp", ["orp"], "EZO-ORP"),
    (r"EZO.*Dissolved Oxygen", "ezo-do", ["dissolved_oxygen"], "EZO-DO"),
    (r"EZO.*Conductivity", "ezo-ec", ["conductivity"], "EZO-EC"),
    (r"EZO.*RTD|EZO.*Temperature", "ezo-rtd", ["temperature"], "EZO-RTD"),
    (r"EZO-CO2|EZO.*CO2", "ezo-co2", ["co2"], "EZO-CO2"),
    (r"EZO-HUM|EZO.*Humidity", "ezo-hum", ["humidity"], "EZO-HUM"),
    (r"EZO-O2|EZO.*Oxygen Sensor", "ezo-o2", ["oxygen"], "EZO-O2"),
    (r"EZO-RGB|EZO.*Color", "ezo-rgb", ["color"], "EZO-RGB"),
    (r"EZO.*Flow", "ezo-flo", ["flow"], "EZO-FLO"),
    (r"EZO.*Pressure", "ezo-prs", ["pressure"], "EZO-PRS"),
    (r"EZO Complete.*pH", "ezo-complete-ph", ["ph"], "EZO Complete-pH"),
    (r"EZO Complete.*ORP", "ezo-complete-orp", ["orp"], "EZO Complete-ORP"),
    (r"EZO Complete.*Dissolved Oxygen", "ezo-complete-do", ["dissolved_oxygen"], "EZO Complete-DO"),
    (r"EZO Complete.*Conductivity", "ezo-complete-ec", ["conductivity"], "EZO Complete-EC"),
    (r"EZO Complete.*Temperature", "ezo-complete-rtd", ["temperature"], "EZO Complete-RTD"),
    # ENV sensors
    (r"ENV-CO2", "env-co2", ["co2"], "ENV-CO2"),
    # OEM circuits
    (r"pH OEM", "ph-oem", ["ph"], "pH OEM"),
    (r"ORP OEM", "orp-oem", ["orp"], "ORP OEM"),
    (r"Dissolved Oxygen OEM", "do-oem", ["dissolved_oxygen"], "DO OEM"),
    (r"Conductivity OEM", "ec-oem", ["conductivity"], "EC OEM"),
    (r"RTD.*OEM|Temperature OEM", "rtd-oem", ["temperature"], "RTD OEM"),
    # Surveyor analog meters
    (r"Surveyor.*pH", "surveyor-ph", ["ph"], "Surveyor pH"),
    (r"Surveyor.*ORP", "surveyor-orp", ["orp"], "Surveyor ORP"),
    (r"Surveyor.*Dissolved Oxygen", "surveyor-do", ["dissolved_oxygen"], "Surveyor DO"),
    (r"Surveyor.*Temperature", "surveyor-rtd", ["temperature"], "Surveyor Temperature"),
    # Probes (physical sensors)
    (r"pH Probe|pH Flow Cell", "ph-probe", ["ph"], "pH Probe"),
    (r"ORP Probe", "orp-probe", ["orp"], "ORP Probe"),
    (r"Dissolved Oxygen Probe", "do-probe", ["dissolved_oxygen"], "DO Probe"),
    (r"Conductivity Probe", "ec-probe", ["conductivity"], "Conductivity Probe"),
    (r"PT-1000|Temperature Probe", "pt1000-probe", ["temperature"], "PT-1000 Probe"),
    (r"Flow Meter", "flow-meter", ["flow"], "Flow Meter"),
    (r"Pressure Sensor", "pressure-sensor", ["pressure"], "Pressure Sensor"),
    (r"CO2 Sensor", "co2-sensor", ["co2"], "CO2 Sensor"),
    (r"Color Sensor", "color-sensor", ["color"], "Color Sensor"),
    (r"Humidity Probe", "humidity-probe", ["humidity"], "Humidity Probe"),
    (r"Oxygen Sensor", "o2-sensor", ["oxygen"], "Oxygen Sensor"),
]

# Skip items that aren't sensors
SKIP_KEYWORDS = {"replacement", "soaker", "reference electrode", "tip cap",
                 "calibration", "solution", "reagent"}


def _discover_products(session: wafer.SyncSession) -> list[tuple[str, str]]:
    """Discover product URLs and names from category pages."""
    all_products = {}  # url -> name

    for cat_path in CATEGORY_PAGES:
        try:
            resp = session.get(BASE_URL + cat_path, timeout=15)
            if resp.status_code != 200:
                continue
            html = resp.text

            # Extract product links with image alt text (WooCommerce pattern)
            items = re.findall(
                r'<a[^>]*href="(https://atlas-scientific\.com/[^"]+)"[^>]*>\s*<img[^>]*alt="([^"]+)"',
                html,
            )
            for url, name in items:
                name = name.strip()
                if name and url not in all_products:
                    all_products[url] = name

            # Also try product title links (h2 > a pattern in WooCommerce)
            title_items = re.findall(
                r'<h2[^>]*>\s*<a[^>]*href="(https://atlas-scientific\.com/[^"]+)"[^>]*>([^<]+)</a>',
                html,
            )
            for url, name in title_items:
                name = name.strip()
                if name and url not in all_products:
                    all_products[url] = name

        except Exception as e:
            logger.warning(f"Atlas Scientific {cat_path}: {e}")

    return sorted(all_products.items())


def _classify_product(name: str) -> tuple[str, list[str], str] | None:
    """Classify a product by name into (sensor_id, measures, display_name)."""
    for pattern, sid, measures, display in PRODUCT_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return (sid, measures, display)
    return None


def scrape_atlas_scientific(output_dir: Path) -> None:
    """Scrape Atlas Scientific for water quality sensors and circuits."""
    source_url = BASE_URL
    logger.info("Discovering Atlas Scientific products...")

    session = wafer.SyncSession(rate_limit=2.0, rate_jitter=1.0)
    products = _discover_products(session)
    logger.info(f"Found {len(products)} products")

    # Group products by sensor_id
    sensor_data: dict[str, dict] = {}
    skipped = 0

    for prod_url, name in products:
        name_lower = name.lower()

        # Skip non-sensor items
        if any(kw in name_lower for kw in SKIP_KEYWORDS):
            skipped += 1
            continue

        classification = _classify_product(name)
        if not classification:
            skipped += 1
            continue

        sid, measures, display = classification
        clean_id = re.sub(r'[^a-z0-9]', '', sid.lower())

        if clean_id not in sensor_data:
            sensor_data[clean_id] = {
                "name": display,
                "measures": measures,
                "urls": [],
                "variants": [],
            }
        entry = sensor_data[clean_id]
        if prod_url not in entry["urls"]:
            entry["urls"].append(prod_url)
        entry["variants"].append(name)

    # Visit one detail page per sensor to get protocols
    # Prefer embedded-solutions URLs (have I2C/UART info) over ezo-complete
    sensors = []
    errors = 0

    for sensor_id, data in sorted(sensor_data.items()):
        detail_url = data["urls"][0]
        for u in data["urls"]:
            if "/embedded-solutions/" in u:
                detail_url = u
                break
        protocols = []

        try:
            resp = session.get(detail_url, timeout=15)
            if resp.status_code == 200:
                html = resp.text
                text_upper = html.upper()
                if "I2C" in text_upper:
                    protocols.append("i2c")
                if "UART" in text_upper:
                    protocols.append("uart")
                if "SPI" in text_upper and "DISPLAY" not in text_upper:
                    protocols.append("spi")

                # Get meta description
                meta = re.search(r'<meta[^>]+(?:name|property)="description"[^>]+content="([^"]+)"', html, re.IGNORECASE)
                desc = meta.group(1).strip() if meta else None
            else:
                desc = None
                errors += 1
        except Exception as e:
            logger.warning(f"Atlas Scientific {sensor_id}: {e}")
            desc = None
            errors += 1

        if desc and len(desc) > 200:
            desc = desc[:197] + "..."

        sensors.append(make_sensor_entry(
            sensor_id=sensor_id,
            name=data["name"],
            measures=data["measures"],
            platforms=[],
            urls=data["urls"][:5],
            description=desc,
            manufacturer="Atlas Scientific",
            protocol=protocols or None,
        ))

    logger.info(f"Scraped {len(sensors)} Atlas Scientific sensors ({errors} errors)")
    stats = {
        "sensor_count": len(sensors),
        "total_products": len(products),
        "skipped": skipped,
        "errors": errors,
    }
    write_source_json("atlas_scientific", source_url, sensors, stats, output_dir)
