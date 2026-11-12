"""Best Modules Corp (Holtek) sensor module scraper.

Scrapes sensor module product pages from bestmodulescorp.com.
Products are Holtek-based sensor modules (BM22S, BM25S, BM32S, BM42S, BM62S, BM92S series).

Site: Magento 2. Content is in raw HTML (no JS rendering needed).
Product specs are in a features list (<ol><li>) with "Key: value" patterns.
"""

import logging
import re
from html import unescape
from pathlib import Path

import wafer

from .common import infer_measures, make_sensor_entry, make_session, parse_supply_voltage, write_source_json

logger = logging.getLogger(__name__)

BASE_URL = "https://www.bestmodulescorp.com"
LISTING_URL = f"{BASE_URL}/en/sensor-module.html?product_list_limit=100"

# Keyword patterns (matched on word boundaries) → measure types. Plain substring
# matching found "light" in "time of flight" and "slightly", and "dust" in
# "dustproof".
CATEGORY_MEASURES: dict[str, list[str]] = {
    r"smoke": ["gas"],
    r"gas": ["gas"],
    r"co": ["co", "gas"],
    r"carbon monoxide": ["co", "gas"],
    r"alcohol": ["gas"],
    r"voc": ["gas", "voc"],
    r"co2": ["co2"],
    r"carbon dioxide": ["co2"],
    r"pm2\.5": ["particulate"],
    r"pm1\.0": ["particulate"],
    r"dust (?:sensor|detect\w*|concentration)": ["particulate"],
    r"temperature": ["temperature"],
    r"humidity": ["humidity"],
    r"pressure": ["pressure"],
    r"barometric": ["pressure"],
    r"soil (?:temperature and )?moisture": ["soil_moisture"],
    r"water level": ["level"],
    r"liquid level": ["level"],
    r"water turbidity": ["water_quality"],
    r"water quality": ["water_quality"],
    r"ph value": ["ph"],
    r"ph sensor": ["ph"],
    r"ph0-14": ["ph"],
    r"pir": ["motion", "pir"],
    # "zero motion interrupt" on an IMU is not presence sensing
    r"motion(?! interrupt)": ["motion"],
    r"microwave": ["motion", "radar"],
    r"radar": ["motion", "radar"],
    r"infrared thermometer": ["ir_temperature"],
    r"ir array": ["ir_temperature"],
    r"thermal imaging": ["ir_temperature"],
    r"thermopile": ["ir_temperature"],
    r"proximity": ["proximity"],
    r"gesture": ["gesture"],
    r"fingerprint": ["biometric"],
    r"weighing": ["weight"],
    r"body composition": ["biometric"],
    r"oximeter": ["biometric"],
    r"oximetry": ["biometric"],
    r"heart rate": ["biometric"],
    r"flame": ["flame"],
    r"light": ["light"],
    r"uv": ["uv"],
    r"color": ["color"],
    r"flow": ["flow"],
    # Same measures as the FS3000 air velocity sensor from other sources
    r"air velocity": ["wind", "flow"],
    r"shake": ["vibration"],
    r"adc module": ["voltage"],
}
_CATEGORY_PATTERNS = [
    (re.compile(rf"\b{pattern}\b", re.IGNORECASE), measures)
    for pattern, measures in CATEGORY_MEASURES.items()
]

# Feature phrases that mention a quantity without the module reporting it: an
# environmental rating, or compensation by an internal sensor
_NOT_A_MEASURE_RE = re.compile(
    r"temperature\s+sensors?\s+(?:for|with)\s+(?:automatic\s+)?temperature[\s-]+compensat\w*"
    r"|temperature(?:\s+and\s+drift)?[\s-]+compensat\w*"
    r"|(?:operating|storage|working)\s+(?:temperature|humidity)"
    r"|(?:operating|storage|working)\s+(?:environment|conditions?)\b.*",
    re.IGNORECASE,
)

# "Ultrasonic Oxygen Concentration & Flow": ultrasonic is how it measures, not
# a distance reading
_ULTRASONIC_TECHNIQUE_RE = re.compile(r"\bultrasonic\s+(?:oxygen|flow|gas)\b", re.IGNORECASE)

# Listed with the sensor modules but not a sensor
_NOT_A_SENSOR_RE = re.compile(r"\bdemo board\b", re.IGNORECASE)

# "Temperature measurement range: ... - Resolution: 0.1°C" or "Temperature
# Measurement - Recommended Range: ..." names a measure even though it carries
# spec words that otherwise rule a line out
_MEASUREMENT_LINE_RE = re.compile(r"[\w ]{0,30}\bmeasurement\b", re.IGNORECASE)

# Modules whose datasheet or user guide shows a temperature reading that their
# product page only calls compensation (checked 2026-11-01)
TEMPERATURE_OUTPUT_IDS = frozenset({
    # HT7M2126/27/36/56/76 datasheet V1.50: I2C register "Current Temperature (°C)"
    "ht7m2126", "ht7m2127", "ht7m2136", "ht7m2156", "ht7m2176",
    # BM22S4021-1 to BM22S4024-1 datasheet V1.00: UART command 0x10 reads temperature
    "bm22s4021", "bm22s4022", "bm22s4023", "bm22s4024",
    # BMA26M221 user's guide: "Temperature value output" (built on the BM22S402x)
    "bma26m221",
    # BM62S2201 datasheet V1.00: UART command 0x02 reads temperature
    "bm62s2201",
    # BM62S5601 datasheet V1.00: temperature bytes in the data frame
    "bm62s5601",
})

# Documents-tab file link: <a href="..." class="am-filelink">Datasheet V1.00</a>
_FILE_LINK_RE = re.compile(r'<a\b([^>]*\bclass="am-filelink"[^>]*)>(.*?)</a>', re.DOTALL)


def _clean_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    # Keep super/subscripts attached: I<sup>2</sup>C -> I2C, CO<sub>2</sub> -> CO2
    text = re.sub(r"<(su[pb])\b[^>]*>(.*?)</\1>", r"\2", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


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


_FEATURES_HEADING_RE = re.compile(r">\s*(?:PRODUCT\s+)?FEATURES\s*:?\s*<", re.IGNORECASE)
_LIST_TAG_RE = re.compile(r"<(/?)(?:ol|ul)\b[^>]*>", re.IGNORECASE)


def _features_list(html: str) -> str | None:
    """The lists under the description tab's "Features" heading, or None.

    Pages put other lists in the same tab (usage notes, related MCUs and
    application notes), and some close three <div>s before the features
    start, so the heading is what marks the list. Some pages split the
    features into several <ol>s in a row.
    """
    start = html.find('id="product.info.description"')
    if start < 0:
        return None
    heading = _FEATURES_HEADING_RE.search(html, start)
    if not heading:
        return None
    lists = []
    pos = heading.end()
    while True:
        opening = _LIST_TAG_RE.search(html, pos)
        if not opening or opening.group(1) or (lists and html[pos:opening.start()].strip()):
            break
        depth = 0
        for tag in _LIST_TAG_RE.finditer(html, opening.start()):
            depth += -1 if tag.group(1) else 1
            if depth == 0:
                lists.append(html[opening.end():tag.start()])
                pos = tag.end()
                break
        else:
            break
    return "\n".join(lists) if lists else None


def _extract_features(html: str) -> list[str]:
    """Extract product features from the description tab's features list."""
    features = _features_list(html)
    if features is not None:
        items = re.findall(r"<li[^>]*>(.*?)</li>", features, re.DOTALL)
        return [_clean_html(item) for item in items if _clean_html(item)]

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
        # Separate the supply heading from other specs later in the feature.
        heading = re.match(r"[^\d:：]+", feat)
        if heading:
            voltage = parse_supply_voltage(heading[0], feat[len(heading[0]):].lstrip(":： "))
            if voltage is not None:
                return voltage
    return None


def _extract_overview(html: str) -> str:
    """The short product summary above the add-to-cart form, as text."""
    start = html.find('class="product attribute overview"')
    if start < 0:
        return ""
    end = html.find('class="product-add-form"', start)
    return _clean_html(html[start:end if end > start else start + 5000].split(">", 1)[-1])


_PROTOCOL_PATTERNS = [
    ("uart", re.compile(r"\bUART\b|\bserial\b", re.IGNORECASE)),
    ("i2c", re.compile(r"\bI2C\b|\bI²C\b|\bIIC\b")),
    ("spi", re.compile(r"\bSPI\b")),
    ("rs485", re.compile(r"\bRS-?485\b|\bModbus\b", re.IGNORECASE)),
    ("one_wire", re.compile(r"\b(?:one|1)-wire\b", re.IGNORECASE)),
    # An analog output (the sound detector's audio pins), not the module's internal ADC
    ("analog", re.compile(r"\b(?:analog|audio)\s+(?:voltage\s+)?output\b", re.IGNORECASE)),
    ("pwm", re.compile(r"\bPWM\b")),
]


def _extract_protocols(features: list[str], overview: str = "") -> list[str]:
    """Interfaces named in the features list and the product summary.

    Not the whole page: it also holds comparison tables with sibling modules,
    pin tables ("ADC reference input"), wiring notes ("if your controller only
    supports UART, use the RS485 bridge") and related products.
    """
    text = " ".join(features) + " " + overview
    return sorted(name for name, pattern in _PROTOCOL_PATTERNS if pattern.search(text))


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
            "resolution:", "accuracy:", "interface:", "packing list",
        ]) and not _MEASUREMENT_LINE_RE.match(feat):
            continue
        measure_features.append(_NOT_A_MEASURE_RE.sub(" ", feat))

    combined = title + " " + " ".join(measure_features)

    for pattern, measure_list in _CATEGORY_PATTERNS:
        if pattern.search(combined):
            measures.update(measure_list)

    # Also use infer_measures from common.py for broader matching
    inferred = infer_measures(title.lower())  # Only infer from title, not all features
    measures.update(inferred)

    if _ULTRASONIC_TECHNIQUE_RE.search(title):
        measures -= {"distance", "ultrasonic"}
    if "soil_moisture" in measures:
        # Soil probes give moisture as "Humidity measurement: 0%RH~100%RH"
        measures.discard("humidity")

    # Empty for a page that names nothing we measure (a servo, an index page):
    # the caller skips it rather than guessing a measure
    return sorted(measures)


def _extract_sensor_type(title: str, features: list[str]) -> str | None:
    """Infer sensor technology type from features (first match wins)."""
    combined = title + " " + " ".join(features)

    # Matched on word boundaries: "hall" is in "shall", "pir" in "inspiration".
    # No "infrared": IR thermometers are thermopiles, proximity sensors use an
    # IR LED and photodiode, and PIR modules say "PIR".
    type_keywords = {
        "mems": "mems",
        "ndir": "ndir",
        "electrochemical": "electrochemical",
        "semiconductor": "semiconductor",
        "catalytic": "catalytic",
        "photoelectric": "photodiode",
        "thermopile": "thermopile",
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
        "hall": "hall_effect",
        "strain gauge": "strain_gauge",
        "load cell": "strain_gauge",
        "piezoelectric": "piezoelectric",
    }

    for keyword, sensor_type in type_keywords.items():
        if re.search(rf"\b{keyword}\b", combined, re.IGNORECASE):
            return sensor_type
    return None


def _document_rank(name: str) -> int | None:
    """How well a Documents-tab file serves as the datasheet (lower is better)."""
    if re.match(r"data\s*sheet", name, re.IGNORECASE):
        return 0  # "Datasheet V1.00": the module's own
    if re.match(r"(?:BM|HT|GTM)[\w-]*[\s-]+data\s*sheet", name, re.IGNORECASE):
        return 1  # "BM22S402x-1 datasheet": the Best Modules sensor a BMCOM module is built on
    if re.search(r"user'?s?\s+guide|使用手[冊册]", name, re.IGNORECASE) and not re.search(
        r"library|arduino|workshop", name, re.IGNORECASE
    ):
        return 2  # a BMCOM module's own spec document when it has no datasheet
    if re.search(r"data\s*sheet", name, re.IGNORECASE):
        # A part on the module ("LMV324 datasheet", "TDS-37 datasheet"): its
        # pins and interface aren't the module's
        return 3
    return None


def _extract_datasheet_url(html: str) -> str | None:
    """The module's datasheet from the page's Documents tab, or None.

    The page's only .pdf link is the site-wide module catalog, which is no
    module's datasheet.
    """
    ranked = []
    for attrs, text in _FILE_LINK_RE.findall(html):
        href = re.search(r'\bhref="([^"]+)"', attrs)
        rank = _document_rank(_clean_html(text))
        if href and rank is not None:
            ranked.append((rank, len(ranked), href.group(1)))
    if not ranked:
        return None
    url = min(ranked)[2]
    return BASE_URL + url if url.startswith("/") else url


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

    session = make_session(20)

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
            measures = _extract_measures(title, features)
            if sensor_id in TEMPERATURE_OUTPUT_IDS:
                measures = sorted(set(measures) | {"temperature"})
            if not measures or _NOT_A_SENSOR_RE.search(title):
                logger.info(f"Best Modules {url}: not a sensor ({title or 'no title'}), skipped")
                skipped += 1
                continue
            voltage = _extract_voltage(features)
            protocols = _extract_protocols(features, _extract_overview(html))
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
