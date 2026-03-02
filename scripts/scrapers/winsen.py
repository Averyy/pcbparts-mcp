"""Winsen gas sensor scraper.

Dynamic scraper that discovers all product pages from the sitemap,
then extracts model, specs, protocols, and datasheet URLs from each page.
"""

import logging
import re
from html import unescape
from pathlib import Path
from urllib.parse import unquote

import wafer

from .common import make_sensor_entry, write_source_json

logger = logging.getLogger(__name__)

BASE_URL = "https://www.winsen-sensor.com"

# Product category listing pages — discovered from site navigation.
# Each category page lists products with links to /product/{slug}.html
CATEGORY_URLS = [
    # By target gas / measurand
    f"{BASE_URL}/co2-sensor/",
    f"{BASE_URL}/co-sensor/",
    f"{BASE_URL}/o2-sensor/",
    f"{BASE_URL}/o3-sensor/",
    f"{BASE_URL}/h2-sensor/",
    f"{BASE_URL}/ch2o-sensor/",
    f"{BASE_URL}/voc-sensor/",
    f"{BASE_URL}/nh3-sensor.html",  # note: .html not /
    f"{BASE_URL}/dust-sensor/",
    f"{BASE_URL}/combusitable-sensor/",  # typo is theirs
    f"{BASE_URL}/toxic-sensor/",
    f"{BASE_URL}/alcohol-sensor/",
    f"{BASE_URL}/refrigerant-sensor/",
    f"{BASE_URL}/temperature-and-humidity-sensor/",
    f"{BASE_URL}/flow-sensor/",
    f"{BASE_URL}/pressure-sensor/",
    f"{BASE_URL}/water-quality-sensor/",
    f"{BASE_URL}/pir-sensor/",
    f"{BASE_URL}/flame-sensor/",
    f"{BASE_URL}/thermopile-sensor/",
    f"{BASE_URL}/photoconductivity-sensor/",
    f"{BASE_URL}/piezoelectric-acceleration-sensor/",
    f"{BASE_URL}/automotive-sensor/",
    f"{BASE_URL}/multi-in-one-module/",
    # By detection technology (may overlap with above — deduped by URL)
    f"{BASE_URL}/semiconductor-gas-sensor/",
    f"{BASE_URL}/electrochemical-gas-sensor/",
    f"{BASE_URL}/infrared-gas-sensor/",
    f"{BASE_URL}/catalytic-gas-sensor/",
    f"{BASE_URL}/mems-gas-sensor/",
    f"{BASE_URL}/sensor-modle/",  # typo is theirs
]

# ── Sensor type classification from title/description keywords ───────────────
# Maps title keywords → (measures, sensor_type)
# Order: more specific first
TYPE_RULES = [
    # CO2 sensors — thermal conduction type (e.g. MD62) before NDIR default
    (r"\bthermal\s+conduct\w*\b.*\bCO2\b|\bCO2\b.*\bthermal\s+conduct\w*\b", ["co2"], "thermal_conduction"),
    # CO2 sensors (NDIR — default for most Winsen CO2 sensors)
    (r"\bNDIR\b.*\bCO2\b|\bCO2\b.*\bNDIR\b", ["co2"], "ndir"),
    (r"\bCO2\b", ["co2"], "ndir"),
    # PM / dust / particulate
    (r"\bPM(?:1\.0|2\.5|4|10)\b|\bdust\b|\bparticulate\b", ["particulate"], "laser"),
    # Flame sensors (pyroelectric flame detectors — before PIR)
    (r"\bflame\b", ["flame"], "pyroelectric"),
    # PIR / pyroelectric (motion/presence — NOT flame)
    (r"\bPIR\b|\bpyroelectric\b", ["motion", "pir"], "pir"),
    # Thermopile / IR temperature
    (r"\bthermopile\b|\bIR\s+temperature\b|\binfrared\s+temperature\b", ["ir_temperature"], "thermopile"),
    # Flow sensors
    (r"\bflow\b", ["flow"], None),
    # Pressure sensors
    (r"\bpressure\b", ["pressure"], None),
    # Temperature & humidity
    (r"\btemperature\b.*\bhumidity\b|\bhumidity\b.*\btemperature\b", ["temperature", "humidity"], None),
    (r"\btemperature\b", ["temperature"], None),
    (r"\bhumidity\b", ["humidity"], None),
    # Water quality / pH
    (r"\bph\b.*(?:sensor|water|quality|module)|\bwater quality\b|\bturbidity\b|\bdissolved oxygen\b", ["water_quality"], None),
    # Liquid level
    (r"\bliquid level\b|\blevel transmitter\b|\bwater level\b", ["level"], None),
    # Specific gas types (must be after CO2)
    (r"\bCO\b(?!\s*2).*(?:sensor|module|detect)", ["co"], "electrochemical"),
    (r"\bO2\b|\boxygen\b", ["oxygen"], "electrochemical"),
    (r"\bO3\b|\bozone\b", ["gas", "ozone"], "electrochemical"),
    (r"\bNH3\b|\bammonia\b", ["gas", "nh3"], "electrochemical"),
    (r"\bH2S\b|\bhydrogen sulfide\b", ["gas", "h2s"], "electrochemical"),
    (r"\bSO2\b|\bsulfur dioxide\b", ["gas"], "electrochemical"),
    (r"\bNO2\b|\bnitrogen dioxide\b", ["gas"], "electrochemical"),
    (r"\bCl2\b|\bchlorine\b", ["gas"], "electrochemical"),
    (r"\bHCN\b|\bhydrogen cyanide\b", ["gas"], "electrochemical"),
    (r"\bHF\b|\bhydrogen fluoride\b", ["gas"], "electrochemical"),
    (r"\bETO\b|\bethylene oxide\b", ["gas"], "electrochemical"),
    (r"\bH2\b|\bhydrogen\b(?!\s*(?:sulfide|cyanide|fluoride))", ["gas"], "electrochemical"),
    (r"\bCH2O\b|\bHCHO\b|\bformaldehyde\b", ["gas", "formaldehyde"], "electrochemical"),
    (r"\bPID\b|\bphotoionization\b", ["gas", "voc"], "pid"),
    (r"\bVOC\b|\bTVOC\b", ["gas", "voc"], "semiconductor"),
    (r"\bMEMS\b.*\bgas\b|\bgas\b.*\bMEMS\b", ["gas"], "mems"),
    # Alcohol
    (r"\balcohol\b|\bethanol\b", ["gas"], "semiconductor"),
    # Combustible / flammable / catalytic
    (r"\bcatalytic\b|\bcombustible\b", ["gas"], "catalytic"),
    (r"\bflammable\b|\bsmoke\b", ["gas"], "semiconductor"),
    # Refrigerant
    (r"\brefrigerant\b|\bfreon\b", ["gas"], "semiconductor"),
    # Generic semiconductor gas sensor (MQ series) — require explicit "gas" context
    (r"\bsemiconductor\b.*\bgas\b|\bgas\b.*\bsemiconductor\b", ["gas"], "semiconductor"),
    # Electrochemical gas sensor (generic) — require explicit "gas" context
    (r"\belectrochemical\b.*\bgas\b|\bgas\b.*\belectrochemical\b", ["gas"], "electrochemical"),
    # Infrared gas sensor (generic)
    (r"\binfrared\b.*\bgas\b|\bgas\b.*\binfrared\b", ["gas"], "ndir"),
]

# Compile patterns
_TYPE_RULES = [(re.compile(pat, re.IGNORECASE), measures, stype) for pat, measures, stype in TYPE_RULES]

# Skip non-sensor products
SKIP_KEYWORDS = {"accessory", "accessories", "adapter", "cable", "connector",
                 "evaluation board", "test board", "development board",
                 "calibration", "module holder"}


def _discover_product_urls(session: wafer.SyncSession) -> list[str]:
    """Discover all product page URLs by crawling category listing pages.

    More reliable than sitemap.xml which hasn't been updated since ~2023.
    """
    seen = set()

    for cat_url in CATEGORY_URLS:
        try:
            resp = session.get(cat_url, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"Category page {cat_url} returned {resp.status_code}")
                continue
        except Exception as e:
            logger.warning(f"Failed to fetch category {cat_url}: {e}")
            continue

        # Extract product links: /product/{slug}.html
        product_links = re.findall(
            r'href="((?:https://www\.winsen-sensor\.com)?/product/[^"?]+\.html)',
            resp.text,
        )
        # Also catch legacy paths like /semiconductor-gas-sensor/1806.html
        legacy_links = re.findall(
            r'href="((?:https://www\.winsen-sensor\.com)?/[a-z-]+/\d+\.html)',
            resp.text,
        )

        for link in product_links + legacy_links:
            # Normalize to absolute URL
            if link.startswith("/"):
                link = BASE_URL + link
            link = link.split("?")[0]  # strip query params
            seen.add(link)

    logger.info(f"Discovered {len(seen)} unique product URLs from {len(CATEGORY_URLS)} category pages")
    return sorted(seen)


def _extract_model_from_url(url: str) -> str:
    """Extract model name from product URL slug."""
    slug = url.rstrip("/").split("/")[-1]
    slug = slug.replace(".html", "")
    slug = unquote(slug)  # Decode %CF%86 → ϕ etc.
    return slug.upper()


def _clean_html(text: str) -> str:
    """Strip HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_specs(html: str) -> dict:
    """Extract key specs from the detailed specs table (Table 1).

    Returns dict with keys: model, target_gas, voltage, output, detection_principle,
    detection_range, description.
    """
    specs = {}

    tables = re.findall(r"<table[^>]*>(.*?)</table>", html, re.DOTALL)
    if not tables:
        return specs

    # Table 0 is summary, Table 1 is detailed specs — prefer Table 1 if available
    spec_table = tables[1] if len(tables) >= 2 else tables[0]
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", spec_table, re.DOTALL)

    for row in rows:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.DOTALL)
        if len(cells) < 2:
            continue
        key = _clean_html(cells[0]).lower().strip().rstrip(":")
        val = _clean_html(cells[1]).strip()

        # Handle multi-cell rows from rowspan grouping in Winsen spec tables.
        # Pattern A (4 cells): "Standard Circuit Conditions | Loop Voltage | VC | ≤24V DC"
        #   → key=cells[1], val=cells[3] (cells[2] is abbreviation like VC/VH/RL)
        # Pattern B (3 cells): "Heater Voltage | VH | 1.8V±0.1V AC or DC"
        #   → key=cells[0], val=cells[2] (cells[1] is abbreviation)
        # Pattern C (3 cells): "Other | Working Voltage | DC5V~14V"
        #   → key=cells[1], val=cells[2]
        if len(cells) >= 4:
            alt_key = _clean_html(cells[1]).lower().strip().rstrip(":")
            alt_val = _clean_html(cells[3]).strip()
            if alt_val and ("voltage" in alt_key or "model" in alt_key or "target" in alt_key
                           or "output" in alt_key or "detection" in alt_key or "measuring" in alt_key
                           or "resistance" in alt_key or "consumption" in alt_key):
                key, val = alt_key, alt_val
        elif len(cells) == 3:
            c0 = _clean_html(cells[0]).lower().strip().rstrip(":")
            c1 = _clean_html(cells[1]).lower().strip().rstrip(":")
            c2 = _clean_html(cells[2]).strip()
            # Pattern B: cells[0] is key, cells[1] is abbreviation, cells[2] is value
            if c2 and ("voltage" in c0 or "resistance" in c0 or "consumption" in c0):
                key, val = c0, c2
            # Pattern C: cells[0] is group header, cells[1] is key, cells[2] is value
            elif c2 and ("voltage" in c1 or "model" in c1 or "target" in c1
                         or "output" in c1 or "detection" in c1 or "measuring" in c1):
                key, val = c1, c2

        if not val:
            continue

        if key in ("model", "model no.", "model no"):
            specs["model"] = val
        elif "target" in key or "detection gas" in key or "detect gas" in key:
            specs["target_gas"] = val
        elif ("voltage" in key and "output" not in key
              and "source" not in key):
            if "heater" in key:
                # Heater voltage is the operating voltage for MEMS/semiconductor gas sensors
                # Store separately — use as fallback if no supply/working voltage found
                if "heater_voltage" not in specs:
                    specs["heater_voltage"] = val
            elif "voltage" not in specs:
                specs["voltage"] = val
        elif key in ("output", "output signal"):
            specs["output"] = val
        elif "detection principle" in key or "sensor type" in key:
            specs["detection_principle"] = val
        elif "detection range" in key or "measuring range" in key:
            specs["detection_range"] = val

    # Also try Table 0 for fields not found in Table 1
    if len(tables) >= 2:
        rows0 = re.findall(r"<tr[^>]*>(.*?)</tr>", tables[0], re.DOTALL)
        for row in rows0:
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.DOTALL)
            if len(cells) < 2:
                continue
            key = _clean_html(cells[0]).lower().strip().rstrip(":")
            val = _clean_html(cells[1]).strip()
            if not val:
                continue
            if key in ("model", "model no.", "model no") and "model" not in specs:
                specs["model"] = val
            if "target" in key and "target_gas" not in specs:
                specs["target_gas"] = val
            if ("detection principle" in key or "sensor type" in key) and "detection_principle" not in specs:
                specs["detection_principle"] = val
            # Table 0 "Working conditions" often embeds voltage inline
            if ("working" in key or "condition" in key) and "voltage" not in specs:
                # Extract "Loop Voltage：5±0.1V" or "Working voltage:3-15V"
                v_match = re.search(
                    r"(?:loop|working|supply|circuit)\s*voltage\s*[:：]\s*"
                    r"(\d+(?:\.\d+)?\s*[±~～–\-]?\s*\d*(?:\.\d+)?\s*V)",
                    val, re.IGNORECASE,
                )
                # Fallback: heater voltage inline
                if not v_match and "heater_voltage" not in specs:
                    v_match_h = re.search(
                        r"heater\s*voltage\s*[:：]\s*"
                        r"(\d+(?:\.\d+)?\s*[±~～–\-]?\s*\d*(?:\.\d+)?\s*V?)",
                        val, re.IGNORECASE,
                    )
                    if v_match_h:
                        specs["heater_voltage"] = v_match_h.group(1)
                if v_match:
                    specs["voltage"] = v_match.group(1)

    # Check ALL tables for Min/Typ/Max format (e.g. RDA223 PIR sensors)
    # Format: "Voltage | VDD | 2.7 | 3 | 3.3 | V" with Min/Typ/Max columns
    # Also runs if specs["voltage"] was set to garbage like "VDD" (not parseable)
    _has_parseable_voltage = bool(
        specs.get("voltage") and re.search(r"\d", specs["voltage"])
    )
    if not _has_parseable_voltage and "heater_voltage" not in specs:
        # Prefer LAST matching table (working conditions) over first (absolute max)
        best_voltage = None
        for table in tables:
            # Skip absolute max rating tables
            table_text = _clean_html(table).lower()
            is_max_table = "max limit" in table_text or "absolute max" in table_text
            rows_all = re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.DOTALL)
            for row in rows_all:
                cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.DOTALL)
                if len(cells) >= 4:
                    k = _clean_html(cells[0]).lower()
                    if "voltage" in k and "output" not in k and "high" not in k and "low" not in k:
                        vals = [_clean_html(c).strip() for c in cells[1:]]
                        nums = []
                        for v in vals:
                            m = re.search(r"(\d+(?:\.\d+)?)", v)
                            if m:
                                nums.append(float(m.group(1)))
                        if nums:
                            lo, hi = min(nums), max(nums)
                            if 0.5 <= hi <= 48:
                                candidate = f"{lo:g}-{hi:g}" if lo != hi else f"{hi:g}"
                                # Non-max-limit tables override max-limit tables
                                if not is_max_table or best_voltage is None:
                                    best_voltage = candidate
        if best_voltage:
            specs["voltage"] = best_voltage

    # Parse compound cells with voltage as dash-list within a single cell
    # e.g. "- Supply Voltage (Vc): <=24V DC\n- Heating Voltage (VH): 3.3V+-0.1V"
    if "voltage" not in specs and "heater_voltage" not in specs:
        for table in tables:
            for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.DOTALL):
                cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.DOTALL)
                for cell in cells:
                    cell_text = _clean_html(cell)
                    hv_match = re.search(
                        r"heat(?:er|ing)\s*voltage[^:：]*[:：]\s*"
                        r"(\d+(?:\.\d+)?)\s*V?\s*[±+\-]?\s*\d*(?:\.\d+)?\s*V?",
                        cell_text, re.IGNORECASE,
                    )
                    if hv_match:
                        specs["heater_voltage"] = hv_match.group(0)
                        break

    # Fallback: extract voltage from features/characteristics text (not in tables)
    # Pattern: "voltage range, from 2.0V to 5.5V" or "supply voltage: 3.3V-5V"
    if "voltage" not in specs and "heater_voltage" not in specs:
        v_text_match = re.search(
            r"(?:supply|power|operating|working)\s*voltage\s*(?:range)?[,:]?\s*"
            r"(?:from\s+)?(\d+(?:\.\d+)?)\s*V?\s*(?:to|[-~～–])\s*(\d+(?:\.\d+)?)\s*V",
            html, re.IGNORECASE,
        )
        if v_text_match:
            lo, hi = v_text_match.group(1), v_text_match.group(2)
            if float(hi) > float(lo) and float(hi) <= 48:
                specs["voltage"] = f"{lo}-{hi}"

    return specs


def _extract_protocols(html: str, specs: dict) -> list[str]:
    """Extract communication protocols from specs and page content."""
    protocols = []

    # Check output signal spec first (most reliable)
    output = specs.get("output", "").upper()
    if "UART" in output or "SERIAL" in output or "TTL" in output:
        protocols.append("uart")
    if "I2C" in output:
        protocols.append("i2c")
    if "SPI" in output and "DISPLAY" not in output:
        protocols.append("spi")
    if "PWM" in output:
        protocols.append("pwm")
    if "ANALOG" in output or "DAC" in output:
        protocols.append("analog")

    # If no output spec found, check the page title area (avoid full HTML noise)
    if not protocols:
        title_match = re.search(r"<title>([^<]+)</title>", html)
        title_text = title_match.group(1).upper() if title_match else ""
        h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
        h1_text = h1_match.group(1).upper() if h1_match else ""
        header = title_text + " " + h1_text

        if "UART" in header:
            protocols.append("uart")
        if "I2C" in header:
            protocols.append("i2c")

    return sorted(protocols)


def _type_from_principle(principle: str) -> str | None:
    """Derive sensor type from detection principle string."""
    p = principle.lower()
    if "ndir" in p or "non-dispersive" in p:
        return "ndir"
    if "thermal conduction" in p or "thermal conductivity" in p:
        return "thermal_conduction"
    if "electrochemical" in p:
        return "electrochemical"
    if "semiconductor" in p or "mos" in p.split():
        return "semiconductor"
    if "catalytic" in p:
        return "catalytic"
    if "laser" in p:
        return "laser"
    if "mems" in p:
        return "mems"
    return None


def _classify_sensor(title: str, specs: dict) -> tuple[list[str], str | None]:
    """Classify sensor into measures and type from title and specs.

    Collects ALL matching measures (for multi-function sensors like 4-in-1
    modules) but uses the FIRST matching type as primary.

    Returns (measures, sensor_type).
    """
    # Combine title + detection principle + target gas for matching
    combined = title
    if specs.get("detection_principle"):
        combined += " " + specs["detection_principle"]
    if specs.get("target_gas"):
        combined += " " + specs["target_gas"]

    all_measures = set()
    first_type = None

    for pattern, measures, stype in _TYPE_RULES:
        if pattern.search(combined):
            all_measures.update(measures)
            if first_type is None and stype:
                first_type = stype

    # Override type from detection_principle if available (more reliable)
    principle = specs.get("detection_principle", "")
    if principle:
        principle_type = _type_from_principle(principle)
        if principle_type:
            first_type = principle_type

    if all_measures:
        return (sorted(all_measures), first_type)

    # Fallback: if we have target_gas, it's probably a gas sensor
    if specs.get("target_gas"):
        return (["gas"], first_type)

    return (["gas"], None)  # Winsen is a gas sensor company — reasonable default


def _extract_datasheet_url(html: str) -> str | None:
    """Extract datasheet PDF URL from page."""
    # Direct PDF links in /d/files/manual/
    match = re.search(r'href="(/d/files/(?:manual|PDF)/[^"]+\.pdf)"', html, re.IGNORECASE)
    if match:
        return BASE_URL + match.group(1)
    return None


def _extract_voltage(specs: dict) -> str | None:
    """Extract working voltage from specs."""
    v = specs.get("voltage", "")
    # "≤24V DC" is a max loop voltage bound, not an operating voltage — prefer heater voltage
    if v and re.match(r"[≤<]", v.strip()):
        v = specs.get("heater_voltage", v)
    if not v:
        # Fall back to heater voltage for MEMS/semiconductor gas sensors
        v = specs.get("heater_voltage", "")
    if not v:
        return None
    # Range: "3.6~5V", "3-15V", "3.6–5.0V", "3～15V", "DC5V～14V", "DC 3.6~5V"
    # Handle optional DC prefix and optional V after first number
    m = re.search(
        r"(?:DC\s*)?(\d+(?:\.\d+)?)\s*V?\s*[~～–\-]\s*(\d+(?:\.\d+)?)\s*V",
        v, re.IGNORECASE,
    )
    if m:
        lo, hi = m.group(1), m.group(2)
        # Sanity: must be an actual range, and within reasonable supply voltage
        if float(hi) > float(lo) and float(hi) <= 48:
            return f"{lo}-{hi}"
    # Nominal with tolerance: "5.0±0.1V" or "5.0±0.1" (unitless) → "5.0"
    m = re.search(r"(\d+(?:\.\d+)?)\s*[±]\s*\d+(?:\.\d+)?\s*V?\b", v)
    if m:
        return m.group(1)
    # Plain value with unit: "5V", "3.3V DC"
    m = re.search(r"(\d+(?:\.\d+)?)\s*V\b", v)
    if m:
        val = float(m.group(1))
        if val <= 48:
            return m.group(1)
    # Bare numeric (no V unit) — trust it since the key already confirmed "voltage"
    m = re.search(r"(\d+(?:\.\d+)?)", v)
    if m:
        val = float(m.group(1))
        if 1.0 <= val <= 48:
            return m.group(1)
    return None


def _make_sensor_id(model: str) -> str:
    """Create sensor ID from model name. Simple lowercase, keep alphanumeric."""
    return re.sub(r"[^a-z0-9]", "", model.lower())


def _build_description(title: str, specs: dict) -> str:
    """Build a concise description from title and specs."""
    parts = [title]
    if specs.get("target_gas"):
        tg = specs["target_gas"]
        # Only add if not already obvious from title
        if tg.lower() not in title.lower():
            parts.append(f"Target: {tg}")
    if specs.get("detection_range"):
        parts.append(f"Range: {specs['detection_range']}")
    desc = ". ".join(parts)
    if len(desc) > 200:
        desc = desc[:197] + "..."
    return desc


def scrape_winsen(output_dir: Path) -> None:
    """Scrape Winsen for gas and environmental sensors."""
    source_url = BASE_URL
    logger.info("Discovering Winsen products from sitemap...")

    session = wafer.SyncSession(rate_limit=2.0, rate_jitter=1.0)
    product_urls = _discover_product_urls(session)
    logger.info(f"Found {len(product_urls)} product pages")

    if not product_urls:
        logger.error("No product URLs found — aborting")
        return

    # First pass: collect data, grouping size variants by sensor_id
    sensor_data: dict[str, dict] = {}  # sensor_id -> collected data
    skipped = 0
    errors = 0

    for i, url in enumerate(product_urls):
        if (i + 1) % 50 == 0:
            logger.info(f"  Processing {i + 1}/{len(product_urls)}...")

        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"HTTP {resp.status_code}: {url}")
                errors += 1
                continue
        except Exception as e:
            logger.warning(f"Fetch error {url}: {e}")
            errors += 1
            continue

        html = resp.text

        # Extract title
        title_match = re.search(r"<title>([^<]+)</title>", html)
        if not title_match:
            errors += 1
            continue
        title = unescape(title_match.group(1)).strip()

        # Skip non-sensor items
        title_lower = title.lower()
        if any(kw in title_lower for kw in SKIP_KEYWORDS):
            skipped += 1
            continue

        # Extract specs from table
        specs = _extract_specs(html)

        # Model: use table model but cross-validate with URL slug.
        # If the table model doesn't match the URL slug at all, the table
        # may be wrong (e.g., MQ316's table says "MQ303B") — use URL slug.
        url_model = _extract_model_from_url(url)
        table_model = specs.get("model")
        if table_model:
            url_id = _make_sensor_id(url_model)
            table_id = _make_sensor_id(table_model)
            # Table model is trusted only if the URL slug starts with
            # the table model ID (or vice versa). This catches cases like
            # MQ316 having table model MQ303B (completely different model).
            if url_id.startswith(table_id) or table_id.startswith(url_id):
                model = table_model
            else:
                model = url_model
        else:
            model = url_model
        sensor_id = _make_sensor_id(model)

        if (not sensor_id or len(sensor_id) < 2 or sensor_id.isdigit()
                or len(sensor_id) > 20
                or (not re.search(r'[0-9]', sensor_id) and len(sensor_id) > 12)):
            skipped += 1
            continue

        # Group size variants: if sensor_id already seen, just add URL
        if sensor_id in sensor_data:
            existing = sensor_data[sensor_id]
            if url not in existing["urls"]:
                existing["urls"].append(url)
            continue

        # Classify
        measures, sensor_type = _classify_sensor(title, specs)
        protocols = _extract_protocols(html, specs)
        datasheet = _extract_datasheet_url(html)
        voltage = _extract_voltage(specs)
        description = _build_description(title, specs)

        sensor_data[sensor_id] = {
            "model": model,
            "measures": measures,
            "urls": [url],
            "description": description,
            "protocols": protocols,
            "datasheet": datasheet,
            "voltage": voltage,
            "sensor_type": sensor_type,
        }

    # Build sensor entries
    sensors = []
    for sensor_id, data in sorted(sensor_data.items()):
        sensors.append(make_sensor_entry(
            sensor_id=sensor_id,
            name=data["model"],
            measures=data["measures"],
            platforms=[],
            urls=data["urls"][:5],
            description=data["description"],
            manufacturer="Winsen",
            protocol=data["protocols"] or None,
            datasheet_url=data["datasheet"],
            voltage=data["voltage"],
            sensor_type=data["sensor_type"],
        ))

    logger.info(f"Scraped {len(sensors)} Winsen sensors ({skipped} skipped, {errors} errors)")

    stats = {
        "sensor_count": len(sensors),
        "total_product_pages": len(product_urls),
        "skipped": skipped,
        "errors": errors,
    }
    write_source_json("winsen", source_url, sensors, stats, output_dir)
