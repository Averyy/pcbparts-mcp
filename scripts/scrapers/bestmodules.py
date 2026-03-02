"""Best Modules Corp (Holtek) sensor module scraper.

Scrapes sensor module product pages from bestmodulescorp.com.
Products are Holtek-based sensor modules (BM22S, BM25S, BM32S, BM42S, BM62S, BM92S series).

Site: Magento 2. Content is in raw HTML (no JS rendering needed).
Product specs are in a features list (<ol><li>) with "Key: value" patterns.
"""

import logging
import re
from pathlib import Path

import wafer

from .common import infer_measures, make_sensor_entry, write_source_json

logger = logging.getLogger(__name__)

BASE_URL = "https://www.bestmodulescorp.com"
LISTING_URL = f"{BASE_URL}/en/sensor-module.html?product_list_limit=100"

# Category keywords → measure types
CATEGORY_MEASURES: dict[str, list[str]] = {
    "smoke": ["gas"],
    "gas": ["gas"],
    "co ": ["co", "gas"],
    "carbon monoxide": ["co", "gas"],
    "alcohol": ["gas"],
    "voc": ["gas", "voc"],
    "co2": ["co2"],
    "carbon dioxide": ["co2"],
    "pm2.5": ["particulate"],
    "pm1.0": ["particulate"],
    "dust": ["particulate"],
    "temperature": ["temperature"],
    "humidity": ["humidity"],
    "pressure": ["pressure"],
    "air pressure": ["pressure"],
    "barometric": ["pressure"],
    "soil moisture": ["soil_moisture"],
    "water turbidity": ["water_quality"],
    "water quality": ["water_quality"],
    "ph value": ["ph"],
    " ph ": ["ph"],
    "ph0-14": ["ph"],
    "ph sensor": ["ph"],
    "pir": ["motion", "pir"],
    "motion": ["motion"],
    "microwave": ["motion", "radar"],
    "radar": ["motion", "radar"],
    "infrared thermometer": ["ir_temperature"],
    "proximity": ["proximity"],
    "gesture": ["gesture"],
    "fingerprint": ["biometric"],
    "weighing": ["weight"],
    "body composition": ["biometric"],
    "oximeter": ["biometric"],
    "flame": ["flame"],
    "light": ["light"],
    "uv": ["uv"],
    "color": ["color"],
    "flow": ["flow"],
}


def _clean_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&#160;", " ")
    text = text.replace("&plusmn;", "±").replace("&deg;", "°")
    text = text.replace("&sim;", "~").replace("&le;", "≤")
    return re.sub(r"\s+", " ", text).strip()


def _make_sensor_id(product_id: str) -> str:
    """Create sensor ID from product ID (e.g. 'BM22S2021-1' → 'bm22s2021')."""
    # Strip trailing "-1", "-A", etc. (variant suffixes)
    clean = re.sub(r"-\d+$|-[A-Z]$", "", product_id, flags=re.IGNORECASE)
    return re.sub(r"[^a-z0-9]", "", clean.lower())


def _discover_product_urls(session: wafer.SyncSession) -> list[str]:
    """Discover sensor module product URLs from the listing page."""
    resp = session.get(LISTING_URL, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # Extract product page URLs
    urls = set()
    for match in re.findall(
        r'href="(https://www\.bestmodulescorp\.com/en/[a-z0-9\-]+\.html)"', html
    ):
        # Skip category/navigation pages
        if any(x in match for x in [
            "sensor-module", "output-module", "wireless", "input-module",
            "product", "catalog", "customer", "checkout", "search", "ic/",
        ]):
            continue
        urls.add(match)

    return sorted(urls)


def _extract_features(html: str) -> list[str]:
    """Extract product features from the description tab's <ol><li> list."""
    # Find the description section
    desc_match = re.search(
        r'id="product\.info\.description"[^>]*>(.*?)</div>\s*</div>\s*</div>',
        html, re.DOTALL,
    )
    if not desc_match:
        # Fallback: find any <ol> after "PRODUCT FEATURES" or "Features"
        desc_match = re.search(
            r"(?:PRODUCT\s+FEATURES|Features)\s*</?\w[^>]*>\s*<ol[^>]*>(.*?)</ol>",
            html, re.DOTALL | re.IGNORECASE,
        )
    if not desc_match:
        return []

    content = desc_match.group(1)
    items = re.findall(r"<li[^>]*>(.*?)</li>", content, re.DOTALL)
    return [_clean_html(item) for item in items if _clean_html(item)]


def _extract_title(html: str) -> str:
    """Extract product title from <h1> or <title>."""
    h1 = re.search(r"<h1[^>]*>\s*<span[^>]*>(.*?)</span>", html, re.DOTALL)
    if h1:
        return _clean_html(h1.group(1))
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
    if h1:
        return _clean_html(h1.group(1))
    title = re.search(r"<title>(.*?)</title>", html)
    if title:
        return _clean_html(title.group(1)).split("|")[0].strip()
    return ""


def _extract_product_id(html: str, url: str) -> str | None:
    """Extract product ID from page content or URL slug."""
    # Try structured product info first
    pid_match = re.search(
        r"Product\s+ID[^<]*</\w+>\s*<\w+[^>]*>\s*([A-Z0-9][A-Z0-9\-]+)",
        html, re.IGNORECASE,
    )
    if pid_match:
        return pid_match.group(1).strip()

    # Fallback: extract from URL slug
    slug_match = re.search(r"/en/([a-z0-9\-]+)\.html$", url, re.IGNORECASE)
    if slug_match:
        return slug_match.group(1).upper()
    return None


def _extract_voltage(features: list[str]) -> str | None:
    """Extract operating voltage from features list."""
    for feat in features:
        if "voltage" not in feat.lower() and "power supply" not in feat.lower():
            continue
        # Range: "3.0V to 5.0V", "3V~5V", "2.7V - 5.5V"
        m = re.search(
            r"(\d+(?:\.\d+)?)\s*V?\s*(?:to|[-~–])\s*(\d+(?:\.\d+)?)\s*V",
            feat, re.IGNORECASE,
        )
        if m:
            lo, hi = m.group(1), m.group(2)
            if float(hi) >= float(lo) and float(hi) <= 48:
                return f"{lo}-{hi}"
        # Single value: "5V", "3.3V"
        m = re.search(r"(\d+(?:\.\d+)?)\s*V\b", feat)
        if m:
            val = float(m.group(1))
            if 1.0 <= val <= 48:
                return m.group(1)
    return None


def _extract_protocols(features: list[str], html: str) -> list[str]:
    """Extract communication protocols from features and page content."""
    protocols = set()
    text = " ".join(features) + " " + html

    if re.search(r"\bUART\b|\bserial\b", text, re.IGNORECASE):
        protocols.add("uart")
    if re.search(r"\bI2C\b|\bI²C\b", text):
        protocols.add("i2c")
    if re.search(r"\bSPI\b", text):
        protocols.add("spi")
    if re.search(r"\bRS-?485\b|\bModbus\b", text, re.IGNORECASE):
        protocols.add("rs485")
    if re.search(r"\banalog\b|\bADC\b", text, re.IGNORECASE):
        protocols.add("analog")
    if re.search(r"\bPWM\b", text):
        protocols.add("pwm")

    return sorted(protocols)


def _extract_measures(title: str, features: list[str]) -> list[str]:
    """Extract measurement types from title and key features.

    Only uses title + detection/measurement features for inference to avoid
    false positives from spec text like "Net weight: 7.8g" or dimension strings.
    """
    measures = set()

    # Filter features to only detection/measurement-related lines
    measure_features = []
    for feat in features:
        fl = feat.lower()
        # Skip spec lines that cause false positives
        if any(k in fl for k in [
            "net weight", "dimension", "operating voltage", "operating current",
            "standby current", "baud rate", "warm-up", "factory calibrat",
            "resolution:", "accuracy:", "interface:",
        ]):
            continue
        measure_features.append(feat)

    combined = (title + " " + " ".join(measure_features)).lower()

    for keyword, measure_list in CATEGORY_MEASURES.items():
        if keyword in combined:
            measures.update(measure_list)

    # Also use infer_measures from common.py for broader matching
    inferred = infer_measures(title.lower())  # Only infer from title, not all features
    measures.update(inferred)

    return sorted(measures) if measures else ["gas"]  # Default: most are gas sensors


def _extract_sensor_type(title: str, features: list[str]) -> str | None:
    """Infer sensor technology type from features."""
    combined = (title + " " + " ".join(features)).lower()

    type_keywords = {
        "mems": "mems",
        "ndir": "ndir",
        "electrochemical": "electrochemical",
        "semiconductor": "semiconductor",
        "catalytic": "catalytic",
        "photoelectric": "photodiode",
        "infrared": "pyroelectric",
        "pir": "pir",
        "pyroelectric": "pyroelectric",
        "capacitive": "capacitive",
        "radar": "radar",
        "microwave": "radar",
        "tof": "tof",
        "time of flight": "tof",
        "laser": "laser",
        "optical": "optical",
        "ultrasonic": "ultrasonic",
        "thermopile": "thermopile",
        "hall": "hall_effect",
        "strain gauge": "strain_gauge",
        "load cell": "strain_gauge",
        "piezoelectric": "piezoelectric",
    }

    for keyword, sensor_type in type_keywords.items():
        if keyword in combined:
            return sensor_type
    return None


def _extract_datasheet_url(html: str) -> str | None:
    """Extract datasheet/document PDF URL."""
    # Look for PDF links in the documents tab
    match = re.search(
        r'href="([^"]+\.pdf)"[^>]*>',
        html, re.IGNORECASE,
    )
    if match:
        url = match.group(1)
        if url.startswith("/"):
            return BASE_URL + url
        return url
    return None


def _build_description(title: str, features: list[str]) -> str | None:
    """Build a concise description from title and key features."""
    parts = [title]
    for feat in features:
        fl = feat.lower()
        # Add key spec features to description
        if any(k in fl for k in [
            "detection range", "resolution", "accuracy", "measuring range",
            "pressure range", "detect", "measure",
        ]):
            parts.append(feat)
            if len(". ".join(parts)) > 180:
                break

    desc = ". ".join(parts)
    if len(desc) > 200:
        desc = desc[:197] + "..."
    return desc if desc else None


def scrape_bestmodules(output_dir: Path) -> None:
    """Scrape Best Modules Corp sensor module product pages."""
    source_url = BASE_URL
    logger.info("Scraping Best Modules Corp sensors...")

    session = wafer.SyncSession(rate_limit=2.0, rate_jitter=1.0)

    logger.info("Discovering products from sensor module listing...")
    product_urls = _discover_product_urls(session)
    logger.info(f"Found {len(product_urls)} product pages")

    sensors = []
    errors = 0
    skipped = 0

    for i, url in enumerate(product_urls, 1):
        if i % 20 == 0:
            logger.info(f"  Processing {i}/{len(product_urls)}...")

        try:
            resp = session.get(url, timeout=20)
            if resp.status_code != 200:
                logger.warning(f"Best Modules {url}: HTTP {resp.status_code}")
                errors += 1
                continue

            html = resp.text
            title = _extract_title(html)
            product_id = _extract_product_id(html, url)

            if not product_id:
                logger.debug(f"Best Modules {url}: no product ID found")
                skipped += 1
                continue

            sensor_id = _make_sensor_id(product_id)
            if not sensor_id or len(sensor_id) < 3:
                skipped += 1
                continue

            features = _extract_features(html)
            voltage = _extract_voltage(features)
            protocols = _extract_protocols(features, html)
            measures = _extract_measures(title, features)
            sensor_type = _extract_sensor_type(title, features)
            datasheet_url = _extract_datasheet_url(html)
            description = _build_description(title, features)

            # Display name: use product ID without variant suffix
            name = re.sub(r"-\d+$|-[A-Z]$", "", product_id, flags=re.IGNORECASE)

            sensors.append(make_sensor_entry(
                sensor_id=sensor_id,
                name=name,
                measures=measures,
                platforms=[],
                urls=[url],
                description=description,
                manufacturer="Holtek",
                voltage=voltage,
                sensor_type=sensor_type,
                protocol=protocols or None,
                datasheet_url=datasheet_url,
            ))

        except Exception as e:
            logger.warning(f"Best Modules {url}: {e}")
            errors += 1

    # Deduplicate by sensor_id (keep first seen, which has the canonical URL)
    seen = {}
    deduped = []
    for s in sensors:
        sid = s["id"]
        if sid not in seen:
            seen[sid] = s
            deduped.append(s)
    sensors = deduped

    logger.info(
        f"Scraped {len(sensors)} Best Modules sensors "
        f"({skipped} skipped, {errors} errors)"
    )
    stats = {
        "sensor_count": len(sensors),
        "total_pages_checked": len(product_urls),
        "skipped": skipped,
        "errors": errors,
    }
    write_source_json("bestmodules", source_url, sensors, stats, output_dir)
