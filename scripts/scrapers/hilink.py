"""Hi-Link mmWave radar sensor scraper."""

import logging
import re
from pathlib import Path

import wafer

from .common import make_sensor_entry, write_source_json

# Keywords in Hi-Link titles/descriptions that indicate additional measures
HILINK_EXTRA_MEASURES = {
    "distance": ["liquid level", "ranging", "range measurement", "distance"],
    "biometric": ["heartbeat", "respiratory", "breathing", "heart rate", "sleep monitor"],
    "magnetic_field": ["magnetometer", "magnetic", "compass", "9-axis", "9 axis", "10-axis", "10 axis"],
    "pressure": ["barometer", "barometric", "pressure", "10-axis", "10 axis"],
}


logger = logging.getLogger(__name__)

BASE_URL = "https://www.hlktech.net"

# Categories to scrape — each has its own listing URL pattern
CATEGORIES = {
    "RadarModule": {
        "default_measures": ["motion", "radar"],
        "sensor_type": "radar",
    },
    "GyroscopeModule": {
        "default_measures": ["acceleration", "gyroscope"],
        "sensor_type": "imu",
    },
}
LISTING_URL = BASE_URL + "/index.php?id=product&cate={category}&pageid={page}"

# Regex for Hi-Link model numbers (LD-series radar + AS-series IMU)
MODEL_RE = re.compile(
    r'\b(LD\d{3,5}[A-Z0-9]*|HLK-LD\d{3,5}[A-Z0-9]*|'
    r'AS\d{3}(?:-\d+)?|HLK-AS\d{3}(?:-\d+)?)\b',
    re.IGNORECASE,
)

# Non-sensor products to skip
SKIP_KEYWORDS = {"test kit", "testing kit", "testing board", "test board",
                 "bracket", "cable", "adapter", "power supply"}


def _make_sensor_id(model_name: str) -> str:
    """Create sensor ID from Hi-Link model name.

    Normalizes HLK-LD2410 → ld2410, HLK-AS201-9 → as2019 (strip HLK- prefix, lowercase).
    """
    s = model_name.lower()
    s = re.sub(r'^hlk-', '', s)
    return re.sub(r'[^a-z0-9]', '', s)


def _discover_products(session: wafer.SyncSession, category: str) -> list[tuple[str, str]]:
    """Discover all product pages from the paginated listing for a category.

    Returns list of (url, title) tuples.
    """
    all_products = []
    seen_urls = set()

    for page in range(1, 20):  # safety limit
        url = LISTING_URL.format(category=category, page=page)
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            break

        html = resp.text
        # Extract product links with titles
        products = re.findall(
            r'<a href="(https://www\.hlktech\.net/index\.php\?id=\d+)" title="([^"]+)">',
            html,
        )
        if not products:
            break

        page_count = 0
        for prod_url, title in products:
            if prod_url not in seen_urls:
                seen_urls.add(prod_url)
                all_products.append((prod_url, title))
                page_count += 1

        if page_count == 0:
            break  # No new products on this page

    return all_products


def _extract_protocols(html: str) -> list[str]:
    """Extract communication protocols from product page."""
    protocols = set()
    text_upper = html.upper()
    if "UART" in text_upper:
        protocols.add("uart")
    if "GPIO" in text_upper:
        protocols.add("gpio")
    if "I2C" in text_upper:
        protocols.add("i2c")
    if "SPI" in text_upper and "DISPLAY" not in text_upper:
        protocols.add("spi")
    return sorted(protocols)


def _infer_hilink_measures(title: str) -> list[str]:
    """Infer measures from Hi-Link product title. All radar sensors measure motion;
    some also measure distance (liquid level, ranging) or biometric (heartbeat)."""
    measures = {"motion"}
    text_lower = title.lower()
    for measure, keywords in HILINK_EXTRA_MEASURES.items():
        if any(kw in text_lower for kw in keywords):
            measures.add(measure)
    return sorted(measures)


def _detect_frequency(title: str) -> str | None:
    """Detect radar frequency band from product title text.

    Uses title (not full HTML) to avoid false matches from navigation links.
    """
    text = title.lower()
    # Check most specific patterns first
    if "5.8g" in text:
        return "5.8GHz"
    if "60g" in text:
        return "60GHz"
    if "79g" in text or "80g" in text:
        return "79GHz"
    if "10g" in text:
        return "10GHz"
    if "24g" in text:
        return "24GHz"
    return None


def scrape_hilink(output_dir: Path) -> None:
    """Scrape Hi-Link sensor product pages (radar + gyroscope modules)."""
    source_url = BASE_URL + "/index.php?id=product"
    logger.info("Discovering Hi-Link sensor products...")

    session = wafer.SyncSession(rate_limit=2.0, rate_jitter=1.0)

    # Discover products across all categories
    all_products = []
    product_categories = {}  # url -> category name
    for category in CATEGORIES:
        cat_products = _discover_products(session, category)
        logger.info(f"  {category}: {len(cat_products)} products")
        for prod_url, title in cat_products:
            product_categories[prod_url] = category
        all_products.extend(cat_products)

    logger.info(f"Found {len(all_products)} total sensor products")

    # First pass: extract model names from listing titles
    model_data: dict[str, dict] = {}
    skipped_non_sensor = 0

    for prod_url, title in all_products:
        title_lower = title.lower()
        category = product_categories.get(prod_url, "RadarModule")
        cat_config = CATEGORIES.get(category, CATEGORIES["RadarModule"])

        # Skip test kits, accessories
        if any(kw in title_lower for kw in SKIP_KEYWORDS):
            skipped_non_sensor += 1
            continue

        # Extract model names from title
        models = MODEL_RE.findall(title)
        if not models:
            continue

        # Use the FIRST model match
        model = models[0].upper()
        if model.startswith("HLK-"):
            model = model[4:]

        sensor_id = _make_sensor_id(model)
        if not sensor_id or len(sensor_id) < 3:
            continue

        if sensor_id not in model_data:
            model_data[sensor_id] = {
                "model": model,
                "urls": [],
                "titles": [],
                "detail_url": None,
                "category": category,
                "sensor_type": cat_config["sensor_type"],
                "default_measures": cat_config["default_measures"],
            }
        entry = model_data[sensor_id]
        if prod_url not in entry["urls"]:
            entry["urls"].append(prod_url)
        entry["titles"].append(title)
        if not entry["detail_url"]:
            entry["detail_url"] = prod_url

    logger.info(f"Found {len(model_data)} unique models, {skipped_non_sensor} non-sensor skipped")

    # Second pass: visit detail pages for richer data
    sensors = []
    errors = 0

    for sensor_id, data in sorted(model_data.items()):
        detail_url = data["detail_url"]
        if not detail_url:
            continue

        try:
            resp = session.get(detail_url, timeout=15)
            if resp.status_code != 200:
                errors += 1
                sensors.append(make_sensor_entry(
                    sensor_id=sensor_id,
                    name=data["model"],
                    measures=data["default_measures"],
                    platforms=[],
                    urls=data["urls"][:3],
                    manufacturer="Hi-Link",
                    sensor_type=data["sensor_type"],
                ))
                continue

            html = resp.text

            # Extract frequency from product title (radar only)
            freq = _detect_frequency(data["titles"][0]) if data["category"] == "RadarModule" else None

            # Extract protocols from detail page
            protocols = _extract_protocols(html)

            # Build description
            desc = data["titles"][0]
            if freq:
                desc = f"{freq} {desc}"
            if len(desc) > 200:
                desc = desc[:197] + "..."

            # Infer measures: start with category defaults, add extras from title
            measures = set(data["default_measures"])
            text_lower = desc.lower()
            for measure, keywords in HILINK_EXTRA_MEASURES.items():
                if any(kw in text_lower for kw in keywords):
                    measures.add(measure)

            sensors.append(make_sensor_entry(
                sensor_id=sensor_id,
                name=data["model"],
                measures=sorted(measures),
                platforms=[],
                urls=data["urls"][:3],
                description=desc,
                manufacturer="Hi-Link",
                sensor_type=data["sensor_type"],
                protocol=protocols or None,
            ))

        except Exception as e:
            logger.warning(f"Hi-Link {sensor_id}: {e}")
            errors += 1
            sensors.append(make_sensor_entry(
                sensor_id=sensor_id,
                name=data["model"],
                measures=data["default_measures"],
                platforms=[],
                urls=data["urls"][:3],
                manufacturer="Hi-Link",
                sensor_type=data["sensor_type"],
            ))

    logger.info(f"Scraped {len(sensors)} Hi-Link sensors ({errors} errors)")
    stats = {
        "sensor_count": len(sensors),
        "total_products": len(all_products),
        "skipped_non_sensor": skipped_non_sensor,
        "errors": errors,
    }
    write_source_json("hilink", source_url, sensors, stats, output_dir)
