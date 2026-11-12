"""Winsen gas sensor scraper.

Dynamic scraper that discovers all product pages from the sitemap,
then extracts model, specs, protocols, and datasheet URLs from each page.
"""

import logging
import re
import time
from html import unescape
from pathlib import Path
from urllib.parse import unquote

import wafer

from .common import infer_measures, make_sensor_entry, make_session, parse_supply_voltage, write_source_json

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
    # Vibration: piezoelectric acceleration and velocity sensors (WAP01, WAV0x, WVV01). Before
    # everything else: they otherwise fell through to the gas default.
    (r"\bpiezoelectric\s+acceleration\b", ["acceleration", "vibration"], "piezoelectric"),
    (r"\bpiezoelectric\s+velocity\b|\bvibration\s+velocity\b", ["vibration"], "piezoelectric"),
    # Water conductivity and residual chlorine probes/modules
    (r"(?<!thermal )\bconductivity\b", ["conductivity", "water_quality"], None),
    (r"\bresidual\s+chlorine\b", ["water_quality"], None),
    # Light sensors and aerosol (particle mass) monitors
    (r"\blight\s+sensor\b|\blx\b", ["light"], None),
    (r"\baerosol\b", ["particulate"], None),
    # CO2 sensors — thermal conduction type (e.g. MD62) before NDIR default
    (r"\bthermal\s+conduct\w*\b.*\bCO2\b|\bCO2\b.*\bthermal\s+conduct\w*\b", ["co2"], "thermal_conduction"),
    # CO2 sensors (NDIR — default for most Winsen CO2 sensors)
    (r"\bNDIR\b.*\bCO2\b|\bCO2\b.*\bNDIR\b", ["co2"], "ndir"),
    (r"\bCO2\b", ["co2"], "ndir"),
    # PM / dust / particulate
    (r"\bPM(?:1\.0|2\.5|4|10)\b|\bdust\b|\bparticulate\b", ["particulate"], "laser"),
    # PbS/PbSe flame sensors are photoconductive cells, not pyroelectric: "lead - salt type
    # infrared photoconductive sensor" (REF-X2212). Photoresistor is the catalog's photoconductor.
    (r"\bphoto-?conduct\w*", [], "photoresistor"),
    # Flame sensors (pyroelectric flame detectors — before PIR)
    (r"\bflame\b", ["flame"], "pyroelectric"),
    # PIR / pyroelectric (motion/presence — NOT flame)
    (r"\bPIR\b|\bpyroelectric\b", ["motion", "pir"], "pir"),
    # Non-contact (thermal radiation) temperature, e.g. the ZMT510-A boil-dry sensor
    (r"\bboil-dry\b|\bthermal\s+radiation\b", ["ir_temperature"], None),
    # Thermopile / IR temperature. A "Thermopile Gas Sensor" (RTGA71) is the IR detector inside an
    # NDIR gas sensor: it reads gas absorption, not an object's temperature.
    (r"\bthermopile\b(?!\s+gas\b)|\bIR\s+temperature\b|\binfrared\s+temperature\b", ["ir_temperature"], "thermopile"),
    # Flow sensors
    (r"\bflow\b", ["flow"], None),
    # Pressure sensors
    (r"\bpressure\b", ["pressure"], None),
    # Temperature & humidity
    (r"\btemperature\b.*\bhumidity\b|\bhumidity\b.*\btemperature\b", ["temperature", "humidity"], None),
    (r"\btemperature\b", ["temperature"], None),
    (r"\bhumidity\b", ["humidity"], None),
    # Water quality. pH, ORP and dissolved oxygen are their own measures (ZW-pH201 wasn't found under
    # "ph", and dissolved-oxygen modules were listed as oxygen gas sensors). The model names carry
    # pH/ORP where titles don't ("ZW-PH101 water quality sensor module"); three digits keep ME3-PH3
    # (phosphine) out. Ammonia nitrogen is dissolved ammonia, not ammonia gas (ZW-NH101).
    (r"\bdissolved\s+oxygen\b", ["dissolved_oxygen", "water_quality"], None),
    (r"\bORP\b|-ORP\d{3}", ["orp", "water_quality"], None),
    (r"\bpH\b.*(?:sensor|water|quality|module)|-pH\d{3}", ["ph", "water_quality"], None),
    (r"\bammonia\s*&?\s*nitrogen\b|\bNH3-N\b", ["water_quality"], None),
    (r"\bph\b.*(?:sensor|water|quality|module)|\bwater quality\b|\bturbidity\b", ["water_quality"], None),
    # Liquid level
    (r"\bliquid level\b|\blevel transmitter\b|\bwater level\b", ["level"], None),
    # Specific gas types (must be after CO2)
    (r"\bCO\b(?!\s*2).*(?:sensor|module|detect)", ["co"], "electrochemical"),
    (r"\bO2\b|(?<!dissolved )\boxygen\b", ["oxygen"], "electrochemical"),
    (r"\bO3\b|\bozone\b", ["gas", "ozone"], "electrochemical"),
    (r"\bNH3\b(?!-N)|\bammonia\b(?!\s*&?\s*nitrogen)", ["gas", "nh3"], "electrochemical"),
    (r"\bH2S\b|\bhydrogen sulfide\b", ["gas", "h2s"], "electrochemical"),
    (r"\bSO2\b|\bsulfur dioxide\b", ["gas"], "electrochemical"),
    (r"\bNO2\b|\bnitrogen dioxide\b", ["gas"], "electrochemical"),
    # Residual chlorine is dissolved in water (ZW-RCl201), not chlorine gas
    (r"\bCl2\b|(?<!residual )\bchlorine\b", ["gas"], "electrochemical"),
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
SKIP_KEYWORDS = {"accessory", "accessories", "adapter", "cable", "connector", "ion generator",
                 "evaluation board", "test board", "development board",
                 "calibration", "module holder"}


DISCOVERY_SECONDS = 900


def _discover_product_urls(session: wafer.SyncSession) -> list[str]:
    """Discover all product page URLs by crawling category listing pages.

    More reliable than sitemap.xml which hasn't been updated since ~2023.
    """
    seen = set()

    # Listing pages are large and the site is slow: at the product-page budget (15s, 5s per try)
    # 13 of 30 timed out on 2026-11-10 and their products went unscraped. Give them longer
    # tries, and retry the failures once after the first pass.
    pending = list(CATEGORY_URLS)
    deadline = time.monotonic() + DISCOVERY_SECONDS  # the whole sensor scrape job has 60 minutes
    for attempt in (1, 2):
        failed = []
        for cat_url in pending:
            if time.monotonic() > deadline:
                logger.warning(f"Category discovery passed {DISCOVERY_SECONDS}s; skipping {cat_url}")
                failed.append(cat_url)
                continue
            text = _fetch_category(session, cat_url)
            if text is None:
                failed.append(cat_url)
            else:
                _collect_product_links(text, seen)
        if not failed:
            break
        logger.warning(f"{len(failed)} category pages failed on pass {attempt}"
                       + (", retrying" if attempt == 1 else ": " + ", ".join(failed)))
        pending = failed

    logger.info(f"Discovered {len(seen)} unique product URLs from {len(CATEGORY_URLS)} category pages")
    return sorted(seen)


def _fetch_category(session: wafer.SyncSession, cat_url: str) -> str | None:
    try:
        resp = session.get(cat_url, timeout=60, attempt_timeout=20)
    except Exception as e:
        logger.warning(f"Failed to fetch category {cat_url}: {e}")
        return None
    if resp.status_code != 200:
        logger.warning(f"Category page {cat_url} returned {resp.status_code}")
        return None
    return resp.text


def _collect_product_links(text: str, seen: set[str]) -> None:
    """Add a listing page's product links (absolute, no query string) to `seen`."""
    # Product links: /product/{slug}.html
    product_links = re.findall(r'href="((?:https://www\.winsen-sensor\.com)?/product/[^"?]+\.html)', text)
    # Legacy paths like /semiconductor-gas-sensor/1806.html
    legacy_links = re.findall(r'href="((?:https://www\.winsen-sensor\.com)?/[a-z-]+/\d+\.html)', text)
    for link in product_links + legacy_links:
        if link.startswith("/"):
            link = BASE_URL + link
        seen.add(link.split("?")[0])


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


def _absolute_ratings(table: str) -> bool:
    text = _clean_html(table)
    if re.search(r"max(?:imum)? limit|absolute max", text, re.I):
        return True
    # Saved tables can omit their external heading. A Min/Max table with
    # storage-temperature limits and no typical column is a ratings table.
    return bool(re.search(r"storage\s*temperature", text, re.I)
                and re.search(r"\bmin\b.*\bmax\b", text, re.I)
                and not re.search(r"\btyp(?:ical)?\b", text, re.I))


def _table_supply_range(cells: list[str]) -> str | None:
    """Min/Typ/Max rows need both a supply label/symbol and a V unit."""
    if len(cells) < 4 or not any(re.fullmatch(r"V(?:DC|AC)?", c, re.I) for c in cells):
        return None
    numbers = [float(c) for c in cells[1:] if re.fullmatch(r"-?\d+(?:\.\d+)?", c)]
    if not numbers or min(numbers) <= 0:
        return None
    return parse_supply_voltage(" ".join(cells[:2]), f"{min(numbers):g}-{max(numbers):g} V")


def _table_grid(rows: list[str]) -> list[list[tuple[int, str]]]:
    """Rows as (origin row, text) per column, with rowspan'd cells repeated where they span."""
    carry: dict[int, tuple[int, int, str]] = {}  # column -> (rows left, origin row, text)
    grid = []
    for r, row in enumerate(rows):
        cells = iter(re.findall(r"<t[dh]([^>]*)>(.*?)</t[dh]>", row, re.DOTALL))
        line: list[tuple[int, str]] = []
        while True:
            col = len(line)
            if carry.get(col, (0,))[0] > 0:
                left, origin, text = carry[col]
                carry[col] = (left - 1, origin, text)
                line.append((origin, text))
                continue
            cell = next(cells, None)
            if cell is None:
                break
            span = re.search(r'rowspan\s*=\s*"?(\d+)', cell[0], re.I)
            text = _clean_html(cell[1]).strip()
            if span and int(span.group(1)) > 1:
                carry[col] = (int(span.group(1)) - 1, r, text)
            line.append((r, text))
        grid.append(line)
    return grid


def _spanned_values(rows: list[str], index: int, key_text: str) -> list[str]:
    """Values beside a rowspan'd label cell in the rows it covers below its own row.

    `<td rowspan="2">Output</td><td>UART_TTL Output</td>` is followed by
    `<tr><td>PWMOutput (3.3V level)</td></tr>`, and in two-pair tables (MH-Z1911A) by
    `<tr><td>PWM</td><td>Lifespan</td><td>&gt;10 years</td></tr>`: the second output is the
    cell next to the label's column. A label in an unspanned column (FRn20's "Output" under an
    "Output signal" group) has no continuation rows.
    """
    grid = _table_grid(rows)
    for col, (origin, text) in enumerate(grid[index]):
        if origin == index and text.lower().strip().rstrip(":") == key_text:
            values = []
            for line in grid[index + 1:]:
                if col + 1 >= len(line) or line[col][0] != index:
                    break
                if line[col + 1][1]:
                    values.append(line[col + 1][1])
            return values
    return []


def _add_output(specs: dict, values: list[str]) -> None:
    """Join every output the tables name; the summary and spec tables can each list some."""
    for value in values:
        if value and value.lower() not in specs.get("output", "").lower():
            specs["output"] = f"{specs['output']}; {value}" if specs.get("output") else value


# A row whose symbol cell is the heater's (VH) is a heater row whatever its label says: MQ303B's
# table pairs "Loop Voltage" with "V H | 0.9V±0.1V" and "Heater Voltage" with "V c | ≤6V DC".
_HEATER_SYMBOL_RE = re.compile(r"[VU]\s*H", re.IGNORECASE)


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
    rows = [] if _absolute_ratings(spec_table) else re.findall(r"<tr[^>]*>(.*?)</tr>", spec_table, re.DOTALL)

    for index, row in enumerate(rows):
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
            # "Signal Output | Output Mode | Digital I²C and Analog 0.5V～4.5VDC | (empty unit)"
            alt_val = _clean_html(cells[3]).strip() or _clean_html(cells[2]).strip()
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
        elif _is_supply_key(key):
            if any(_HEATER_SYMBOL_RE.fullmatch(_clean_html(c).strip()) for c in cells[1:-1]):
                continue
            # Three-cell rows can put the unit between the label and value.
            if any(re.fullmatch(r"V(?:DC|AC)?", _clean_html(c).strip(), re.I) for c in cells[1:]):
                key += " (V)"
            voltage = _table_supply_range([_clean_html(c).strip() for c in cells])
            if voltage is None:
                voltage = parse_supply_voltage(key, val)
            if voltage is None and re.fullmatch(r"V(?:DC|AC)?", val, re.I):
                voltage = parse_supply_voltage(key, " ".join(_clean_html(c) for c in cells[2:]))
            if voltage is not None and "voltage" not in specs:
                specs["voltage"] = voltage + "V"
        elif _is_output_key(key):
            _add_output(specs, [val, *_spanned_values(rows, index, key)])
        elif "detection principle" in key or "sensor type" in key:
            specs["detection_principle"] = val
        elif "detection range" in key or "measuring range" in key:
            specs["detection_range"] = val

    # Also try Table 0 for fields not found in Table 1
    if len(tables) >= 2 and not _absolute_ratings(tables[0]):
        rows0 = re.findall(r"<tr[^>]*>(.*?)</tr>", tables[0], re.DOTALL)
        for index, row in enumerate(rows0):
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
            if _is_output_key(key):
                _add_output(specs, [val, *_spanned_values(rows0, index, key)])
            # Summary conditions may contain several semicolon-separated rails.
            if ("working" in key or "condition" in key) and "voltage" not in specs:
                for match in re.finditer(
                    r"((?:loop|working|supply|circuit)\s*voltage)\s*[:：]\s*([^;；\n]+)",
                    val, re.IGNORECASE,
                ):
                    # Stop at the next labelled spec (e.g. Heater Voltage).
                    supply = re.split(r"\b(?:heater|heating|working current)\b", match[2], flags=re.I)[0]
                    voltage = parse_supply_voltage(match[1], supply)
                    if voltage is not None:
                        specs["voltage"] = voltage + "V"
                        break

    # Min/Typ/Max rows carry the unit in a separate cell. Require a supply
    # label/symbol AND an actual V unit; noise voltage in nV/Hz must never match.
    if "voltage" not in specs:
        for table in tables:
            if _absolute_ratings(table):
                continue
            for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.DOTALL):
                cells = [_clean_html(c).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.DOTALL)]
                voltage = _table_supply_range(cells)
                if voltage is not None:
                    specs["voltage"] = voltage + "V"
                    break

    # Features can state a supply range without a table row.
    if "voltage" not in specs:
        match = re.search(
            r"((?:supply|power|operating|working)\s*voltage)\s*(?:range)?[,:]?\s*"
            r"(?:from\s+)?(\d+(?:\.\d+)?\s*V?\s*(?:to|[-~～–])\s*\d+(?:\.\d+)?\s*V)",
            _clean_html(re.sub(r"<table[^>]*>.*?</table>",
                               lambda m: "" if _absolute_ratings(m[0]) else m[0], html, flags=re.S)), re.IGNORECASE,
        )
        if match:
            voltage = parse_supply_voltage(match[1], match[2])
            if voltage is not None:
                specs["voltage"] = voltage + "V"

    # The Features list can name outputs the tables leave out: MH-711A's says "Output method: UART,
    # analog voltage signal, etc." while its spec table gives only "IIC" and "0.4-2V DC".
    _add_output(specs, _feature_outputs(html))

    return specs


_FEATURE_OUTPUT_RE = re.compile(
    r"(?:\d+\.\s*)?(?:multiple\s+)?output\s+(?:method|signal|mode|type|interface)s?\s*[:：]\s*(.+)", re.IGNORECASE)


def _feature_outputs(html: str) -> list[str]:
    """Outputs named in the product's own Features list ("Output method: UART, ..."). Only the
    list under the page's Features heading: related-product cards repeat other parts' features."""
    section = re.search(r"<h4[^>]*>\s*Features\s*</h4>(.*?)(?:<h4|$)", html, re.DOTALL | re.IGNORECASE)
    if not section:
        return []
    outputs = []
    for item in re.findall(r"<li[^>]*>(.*?)</li>", section[1], re.DOTALL):
        match = _FEATURE_OUTPUT_RE.fullmatch(_clean_html(item).strip())
        if match:
            outputs.append(match[1].strip())
    return outputs


def _clean_title(raw: str) -> str:
    """Page title without the site name some pages append ("... Module | Winsen")."""
    return re.sub(r"\s*[|｜]\s*Winsen\s*$", "", unescape(raw).strip(), flags=re.I)


def _is_supply_key(key: str) -> bool:
    """A spec row naming the supply: "Working Voltage", or "Power Supply" (ZW-C1021)."""
    return "voltage" in key or re.fullmatch(r"(?:dc\s+)?power\s+supply", key) is not None


def _is_output_key(key: str) -> bool:
    """A spec row naming the output: "Output", "Signal Output" (ZW-C1021),
    "Output Interface" (ZW-ORP201), "Output Mode" (ZW-TUR1021), "OutputSignal" (MH-441D)."""
    return re.fullmatch(r"(?:signal\s+)?output(?:\s*(?:signal|interface|mode|modes|type))?", key) is not None


# Analog outputs as Winsen words them: "DAC (0.4~2V voltage ...)", a voltage span after the
# UART ("UART-TTL (3.3V compatible with 5V) 0.4~2.0V"), a current loop ("RS485 / (4-20) mA",
# but not "PWM, can be used as a 4-20mA control signal") and a bridge's millivolt output.
_ANALOG_OUTPUT_RE = re.compile(
    r"ANALOG|\bDAC\b|MILLIVOLT"
    r"|\b\d+(?:\.\d+)?\s*V?\s*[-~～–]\s*\d+(?:\.\d+)?\s*V(?:DC)?\b"
    r"|(?<!USED AS A )\(?\b4\s*[-–~～]\s*20\s*\)?\s*MA\b"
)
# A switching output ("High and low levels can be used to drive relays",
# "High Level, 3V; Low Level, 0V")
_LEVEL_OUTPUT_RE = re.compile(r"\bHIGH\s+(?:AND\s+LOW\s+)?LEVELS?\b|\bLOW\s+LEVEL\b|\bSWITCH(?:ING)?\s+(?:VALUE|OUTPUT|SIGNAL)\b")


def _extract_protocols(html: str, specs: dict) -> list[str]:
    """Extract communication protocols from specs and page content.

    "LIN" has no tag in the catalog vocabulary (MH-V1512A-LGC: "LIN / PWM, Customizable").
    """
    protocols = []

    # Check output signal spec first (most reliable)
    output = specs.get("output", "").upper()
    rs485 = "RS485" in output or "RS-485" in output
    if rs485:
        protocols.append("rs485")
    # "RS485 serial" needs a transceiver; it is not a UART pin
    if "UART" in output or "TTL" in output or ("SERIAL" in output and not rs485):
        protocols.append("uart")
    if "I2C" in output or "I²C" in output or re.search(r"\bIIC\b", output):
        protocols.append("i2c")
    if "SPI" in output and "DISPLAY" not in output:
        protocols.append("spi")
    if "PWM" in output:
        protocols.append("pwm")
    if _ANALOG_OUTPUT_RE.search(output):
        protocols.append("analog")
    # Case-sensitive: "High and low levels can be used to drive relays" is not a CAN bus
    if re.search(r"\bCAN\b", specs.get("output", "")):
        protocols.append("can")
    if not rs485 and re.search(r"(?<![\w.])485\b", output):  # "CAN, 485" (ZE-H100)
        protocols.append("rs485")
    if _LEVEL_OUTPUT_RE.search(output):
        protocols.append("gpio")

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

    # A bare sensing element has no output stage, so the host reads it through an analog front
    # end: an electrochemical cell's current ("Sensitivity | (0.8±0.15) µA/ppm", ME3-H2S;
    # "≥30nA/ppm"; "(80~130)uA") or a chemiresistor's resistance ("sensitive materials resistance
    # | RS | 1KΩ～30KΩ", GM-602B). Without this the build's type defaults gave cells a UART and
    # MEMS gas chips an I2C bus.
    if not protocols and _ELEMENT_SIGNAL_RE.search(_tables_text(html)):
        protocols.append("analog")

    return sorted(protocols)


_ELEMENT_SIGNAL_RE = re.compile(
    r"(?<![A-Za-z])[µμun]A\s*/\s*ppm"
    # A sensitivity given as a raw signal: "（4±2）µA/(mg/L)", "8-15mV (in air)", "0.10±0.02mA"
    r"|Sensitivity[^|]{0,30}\|[^|]{0,25}?\d\s*[)）]?\s*(?:[µμun]A|mA|mV)\b"
    r"|sensitive\s+(?:materials?\s+)?resistance"
    r"|\bresistance\b[^|]{0,40}\|\s*R\s*s\b",
    re.IGNORECASE,
)


def _tables_text(html: str) -> str:
    """Every table cell's text, cells separated by " | "."""
    cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", "".join(re.findall(r"<table[^>]*>(.*?)</table>", html, re.DOTALL)), re.DOTALL)
    return " | ".join(_clean_html(c) for c in cells)


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

    # The shared keyword rules before the gas default: Winsen also sells light, vibration and
    # water-quality parts, which the default listed as gas sensors.
    inferred = infer_measures(combined)
    if inferred:
        return (inferred, first_type)

    return (["gas"], None)  # Winsen is a gas sensor company — reasonable default


def _extract_datasheet_url(html: str) -> str | None:
    """Extract datasheet PDF URL from page."""
    # Direct PDF links in /d/files/manual/
    match = re.search(r'href="(/d/files/(?:manual|PDF)/[^"]+\.pdf)"', html, re.IGNORECASE)
    if match:
        return BASE_URL + match.group(1)
    return None


def _extract_voltage(specs: dict) -> str | None:
    """Extract a verified supply, excluding unitless numbers and heater fallbacks."""
    return parse_supply_voltage("supply voltage", specs.get("voltage", ""))


def _make_sensor_id(model: str) -> str:
    """Create sensor ID from model name. Simple lowercase, keep alphanumeric."""
    return re.sub(r"[^a-z0-9]", "", model.lower())


def _extract_product_model(html: str, title: str, url: str, specs: dict) -> str:
    """Prefer an explicit Model row corroborated by the product title.

    Old URL slugs survive manufacturer renames. Conversely, copied tables can
    name an unrelated device, so a table alone must not redefine the product.
    Search all tables: the summary often has the only Model row.
    """
    for table in re.findall(r"<table\b[^>]*>(.*?)</table>", html, re.I | re.S):
        for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", table, re.I | re.S):
            cells = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.I | re.S)
            if len(cells) < 2:
                continue
            key = _clean_html(cells[0]).lower().rstrip(": .")
            model = _clean_html(cells[1])
            if key in {"model", "model no"} and model:
                pattern = r"(?<![a-z0-9])" + re.escape(model) + r"(?![a-z0-9])"
                if re.search(pattern, title, re.I):
                    return model
    url_model = _extract_model_from_url(url)
    table_model = specs.get("model")
    if table_model:
        url_id, table_id = _make_sensor_id(url_model), _make_sensor_id(table_model)
        if table_id and (url_id.startswith(table_id) or table_id.startswith(url_id)):
            return table_model
    return url_model


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

    session = make_session(15)
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
        title = _clean_title(title_match.group(1))

        # Skip non-sensor items
        title_lower = title.lower()
        if any(kw in title_lower for kw in SKIP_KEYWORDS):
            skipped += 1
            continue

        # Extract specs from table
        specs = _extract_specs(html)

        model = _extract_product_model(html, title, url, specs)
        # Keep published IDs stable; Model/title agreement supplies the name.
        # The alias table also accepts the current designation at query time.
        legacy_model = _extract_model_from_url(url)
        table_model = specs.get("model")
        if table_model:
            url_id, table_id = _make_sensor_id(legacy_model), _make_sensor_id(table_model)
            if table_id and (url_id.startswith(table_id) or table_id.startswith(url_id)):
                legacy_model = table_model
        sensor_id = _make_sensor_id(legacy_model)

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
