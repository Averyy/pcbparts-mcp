"""Benewake LiDAR/ToF distance sensor scraper."""

import logging
import re
from pathlib import Path

import wafer

from .common import make_sensor_entry, write_source_json

logger = logging.getLogger(__name__)

BASE_URL = "https://en.benewake.com"

# Regex for extracting model name from page text.
# Matches Benewake model patterns: TF-Luna, TF02-Pro-W, TFA1200-L, Horn-RT, VLS-H5
# Allows multiple hyphen+short-alphanum groups to handle "TF02-Pro-W".
# Each hyphen group is max 5 chars to avoid matching slugs like "tfa1200-kilometer-..."
MODEL_RE = re.compile(r'\b((?:TF|Horn|VL)[A-Za-z0-9]*(?:-[A-Za-z0-9]{1,5})*)\b', re.IGNORECASE)

# Some product titles use "TFMini Plus" (space-separated) — regex won't capture "Plus".
# Map known space-separated model names to their canonical forms.
TITLE_FIXUPS = {
    "TFMini Plus": "TFmini-Plus",
    "TFmini Plus": "TFmini-Plus",
    "Horn-X2 Pro": "Horn-X2-Pro",
    "Horn X2 Pro": "Horn-X2-Pro",
}

# Non-product slugs to skip
SKIP_SLUGS = {"IndustrialProduct", "about", "contact", "news", "support", "download"}


def _make_sensor_id(model_name: str) -> str:
    """Create a sensor ID from a Benewake model name.

    Simple lowercase + strip non-alphanumeric. No prefix/suffix stripping
    since Benewake product names ARE the sensor IDs.
    """
    return re.sub(r'[^a-z0-9]', '', model_name.lower())


def _discover_product_urls() -> list[str]:
    """Discover product page URLs from the Benewake homepage."""
    resp = wafer.get(BASE_URL + "/", timeout=15)
    resp.raise_for_status()
    html = resp.text

    urls = set()

    # Pattern 1: /Slug/index.html (most products)
    for slug in re.findall(r'href="/([^/"]+)/index\.html"', html):
        if slug not in SKIP_SLUGS:
            urls.add(f"/{slug}/index.html")

    # Pattern 2: /tf-something or /tfXXX-something (alternate product pages)
    for path in re.findall(r'href="(/(?:tf|TF|horn|Horn|vl|VL)[^"]*)"', html):
        # Skip index.html ones already captured
        if "/index.html" not in path:
            urls.add(path)

    return sorted(urls)


def _extract_protocols_from_meta(description: str) -> list[str]:
    """Extract protocols mentioned in the meta description."""
    if not description:
        return []
    protocols = set()
    if "UART" in description.upper():
        protocols.add("uart")
    if "I2C" in description.upper() or "I²C" in description:
        protocols.add("i2c")
    if "SPI" in description.upper():
        protocols.add("spi")
    if "RS-485" in description.upper() or "RS485" in description.upper() or "Modbus" in description:
        protocols.add("rs485")
    # CAN bus: case-sensitive for standalone "CAN", plus "can/" pattern (e.g. "can/rs485")
    if re.search(r'\bCAN\b|DroneCAN\b|\bcan/', description):
        protocols.add("can")
    return sorted(protocols)


def scrape_benewake(output_dir: Path) -> None:
    """Scrape Benewake product pages for LiDAR/ToF distance sensors."""
    source_url = BASE_URL
    logger.info("Discovering Benewake products from homepage...")

    product_paths = _discover_product_urls()
    logger.info(f"Found {len(product_paths)} product pages")

    session = wafer.SyncSession(rate_limit=2.0, rate_jitter=1.0)
    sensors = []
    errors = 0

    for path in product_paths:
        url = BASE_URL + path
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"Benewake {path}: HTTP {resp.status_code}")
                errors += 1
                continue

            html = resp.text

            # Extract title and meta description
            title_match = re.search(r'<title>([^<]+)', html)
            title = title_match.group(1) if title_match else ""
            meta_match = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html)
            description = meta_match.group(1).strip() if meta_match else None

            # Apply fixups for space-separated names (e.g., "TFMini Plus" → "TFmini-Plus")
            def apply_fixups(text: str) -> str:
                for old, new in TITLE_FIXUPS.items():
                    text = text.replace(old, new)
                return text

            # Extract model name: try meta description first (has canonical names),
            # then title, then URL slug
            model_match = None
            if description:
                model_match = MODEL_RE.search(apply_fixups(description))
            if not model_match:
                model_match = MODEL_RE.search(apply_fixups(title))
            if not model_match:
                slug = path.split("/")[1] if "/" in path else path.lstrip("/")
                model_match = MODEL_RE.search(slug)
            if not model_match:
                logger.debug(f"Benewake {path}: no model name found")
                errors += 1
                continue

            model_name = model_match.group(1)
            sensor_id = _make_sensor_id(model_name)
            if not sensor_id or len(sensor_id) < 3:
                errors += 1
                continue

            # Truncate description
            if description and len(description) > 200:
                description = description[:197] + "..."

            # Extract protocols from meta description
            protocols = _extract_protocols_from_meta(description)

            sensors.append(make_sensor_entry(
                sensor_id=sensor_id,
                name=model_name,
                measures=["distance", "lidar"],
                platforms=[],
                urls=[url],
                description=description,
                manufacturer="Benewake",
                sensor_type="tof",
                protocol=protocols or None,
            ))

        except Exception as e:
            logger.warning(f"Benewake {path}: {e}")
            errors += 1

    # Deduplicate by sensor_id (keep first seen)
    seen = {}
    deduped = []
    for s in sensors:
        sid = s["id"]
        if sid not in seen:
            seen[sid] = s
            deduped.append(s)
    sensors = deduped

    logger.info(f"Scraped {len(sensors)} Benewake sensors ({errors} errors)")
    stats = {
        "sensor_count": len(sensors),
        "total_pages_checked": len(product_paths),
        "errors": errors,
    }
    write_source_json("benewake", source_url, sensors, stats, output_dir)
