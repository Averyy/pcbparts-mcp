"""Maxbotix ultrasonic/LiDAR sensor scraper (Shopify API)."""

import logging
import re
from html import unescape
from pathlib import Path

import wafer

from .common import make_sensor_entry, normalize_sensor_id, write_source_json

logger = logging.getLogger(__name__)

# Products to skip (non-sensor items: accessories, mounting hardware, cables, etc.)
SKIP_KEYWORDS = {
    "subscription", "converter", "accessory", "cable", "bracket",
    "pin connector", "pin header", "discovery call", "options",
    "mounting", "hardware kit", "voltage regulator", "regulator",
    "maxtemp", "hr-maxtemp", "radio bridge", "power supply",
    "horn kit", "wr mounting", "snap-on horn",
}

# Product type -> sensor type mapping
PRODUCT_TYPE_MAP = {
    "tof lidar": "tof",
    "time of flight": "tof",
}

MB_MODEL_RE = re.compile(r'\b(MB\d{3,5}[A-Z]*)\b', re.IGNORECASE)


def scrape_maxbotix(output_dir: Path) -> None:
    """Scrape Maxbotix Shopify store for ultrasonic/LiDAR distance sensors."""
    url = "https://www.maxbotix.com/products.json?limit=250"
    logger.info("Downloading Maxbotix product catalog...")
    resp = wafer.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    products = data.get("products", [])
    logger.info(f"Found {len(products)} Maxbotix products")

    sensors = []
    skipped_retired = 0
    skipped_non_sensor = 0
    skipped_no_model = 0

    for product in products:
        title = product.get("title", "")
        handle = product.get("handle", "")
        product_type = product.get("product_type", "")

        # Skip retired products
        if "RETIRED" in title.upper():
            skipped_retired += 1
            continue

        # Skip non-sensor products
        title_lower = title.lower()
        if any(kw in title_lower for kw in SKIP_KEYWORDS):
            skipped_non_sensor += 1
            continue

        # Extract all MB model numbers from title and variant SKUs
        all_models = set()
        for m in MB_MODEL_RE.findall(title):
            all_models.add(m.upper())
        for variant in product.get("variants", []):
            sku = variant.get("sku") or ""
            for m in MB_MODEL_RE.findall(sku):
                all_models.add(m.upper())

        if not all_models:
            skipped_no_model += 1
            continue

        # Build product URL
        product_url = f"https://www.maxbotix.com/products/{handle}"

        # Determine sensor type from product_type
        sensor_type = "ultrasonic"  # default for Maxbotix
        pt_lower = product_type.lower()
        for pattern, stype in PRODUCT_TYPE_MAP.items():
            if pattern in pt_lower:
                sensor_type = stype
                break

        # Build description from body_html (strip tags, decode entities, truncate)
        body = product.get("body_html") or ""
        desc = re.sub(r'<[^>]+>', ' ', body).strip()
        desc = unescape(desc)
        desc = re.sub(r'\s+', ' ', desc)
        if len(desc) > 200:
            desc = desc[:197] + "..."
        if not desc:
            desc = None

        # Create one entry per model number
        for model in sorted(all_models):
            sensor_id = normalize_sensor_id(model)
            if not sensor_id:
                continue

            sensors.append(make_sensor_entry(
                sensor_id=sensor_id,
                name=model,
                measures=["distance", "ultrasonic"],
                platforms=[],
                urls=[product_url],
                description=desc,
                manufacturer="MaxBotix",
                sensor_type=sensor_type,
            ))

    # Deduplicate by sensor_id (same model can appear in multiple products)
    seen = {}
    deduped = []
    for s in sensors:
        sid = s["id"]
        if sid not in seen:
            seen[sid] = s
            deduped.append(s)
        else:
            # Merge URLs
            existing = seen[sid]
            for u in s.get("urls", []):
                if u not in existing.get("urls", []):
                    existing.setdefault("urls", []).append(u)
    sensors = deduped

    logger.info(f"Skipped {skipped_retired} retired, {skipped_non_sensor} non-sensor, {skipped_no_model} no-model products")
    stats = {
        "sensor_count": len(sensors),
        "total_products": len(products),
        "skipped_retired": skipped_retired,
        "skipped_non_sensor": skipped_non_sensor,
        "skipped_no_model": skipped_no_model,
    }
    write_source_json("maxbotix", url, sensors, stats, output_dir)
