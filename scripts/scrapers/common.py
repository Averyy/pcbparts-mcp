"""Shared utilities for sensor scrapers."""

import json
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

import wafer

logger = logging.getLogger(__name__)

SCRAPER_VERSION = "1.0.0"


def parse_supply_voltage(label: str, value: str) -> str | None:
    """Parse an explicitly labelled supply in volts, never noise/bias/heater ratings.

    A voltage unit may be in the heading (e.g. Working voltage (V)) or value.
    Preserve tolerances as intervals. Reject one-sided bounds and unqualified
    discrete options. Preserve explicit "or" alternatives and supplies marked
    "compatible" or "either" as separate modes, without filling their gaps;
    overlapping alternatives give the range they all support.
    A bare comma or slash can describe unrelated specifications and is rejected.
    """
    def fmt(n: Decimal) -> str:
        return format(n.normalize(), "f")

    if re.search(r"noise|output|bias|heater|heating|source|excitation|absolute|reference|vddio|i/o|interface", label, re.I):
        return None
    if not re.search(
        r"\b(?:supply|power|operating|operation|working|work|input|loop|circuit|nominal)\s*(?:dc\s*)?voltage\b"
        r"|\bpower\s+supply\b|\b(?:[ad]?vdd\w*|vcc|vs)\b", label, re.I,
    ):
        return None
    unit = r"(?<![a-zA-Zµμ/])V(?:DC|AC)?(?![a-zA-Z/])"
    v = value.replace("\u00a0", " ").replace("％", "%").replace("+/-", "±").replace("+-", "±")
    # Ripple/current limits are separate specs, not bounds on the supply.
    v = re.split(r"[,，]?\s*\bripple\b|\bcarrying capacity\b", v, flags=re.I)[0]
    # A separately labelled auxiliary IC rail is not a selectable supply for
    # the sensor module (e.g. fingerprint module VCC, then touch IC VDD).
    clauses = re.split(r"[,，]", v, maxsplit=1)
    if (len(clauses) == 2
            and re.search(r"\bfor\b.*\bsensor module\b", clauses[0], re.I)
            and re.search(r"\bfor\b.*\b(?:touch|interface) IC\b", clauses[1], re.I)):
        v = clauses[0]
    # "3.3VDC for I²C; 3.6VDC for 0.2-2.3V" (Winsen WPCK68): a "for ..." clause names what a
    # supply is for, here the output range; its numbers are not the supply.
    v = re.sub(r"\bfor\b[^;；,，]*", "", v, flags=re.I)
    # "5V DC; 0.5-4.5V output": a clause about the output or signal is not the supply.
    clauses = [c for c in re.split(r"[;；]", v) if c.strip()]
    if len(clauses) > 1:
        v = ";".join(c for c in clauses
                     if not re.search(r"\b(?:output|signal|analog|logic|interface|i/o)\b", c, re.I))
    v = re.sub(r"AC\s*/\s*DC|\(?\b(?:AC\s+or\s+DC|DC\s+or\s+AC)\b\)?", "", v, flags=re.I)
    if not re.search(unit, f"{label} {v}", re.I):
        return None
    # A ceiling alone is not an operating interval, in symbols or words.
    if re.search(r"[<>≤≥]", v) or re.search(
            r"\b(?:up\s+to|less\s+than|lower\s+than|higher\s+than|greater\s+than|more\s+than|below|under|at\s+most"
            r"|not\s+(?:to\s+)?exceed\w*|within|limit\w*)\b",
            v, re.I):
        return None
    # A negative number ("-5V", an absolute-maximum "-0.3~3.6V") is not a supply range, and
    # mV/kV/µV values aren't volts. A hyphen after a number (or its V) is a range, not a sign.
    if re.search(r"(?:^|[^\dVv.\s])\s*[-−]\s*\d", v) or re.search(r"\d\s*(?:m|k|µ|μ|u)V\b", v):
        return None
    number = r"(\d+(?:\.\d+)?)"
    # "5V DC; 4-20mA", "3.3V 10-20mA": a value or range in another unit is not a voltage.
    other_unit = r"\s*(?:m|µ|μ|u|k)?(?:A|W|Hz|Ω|ohm)(?![a-zA-Z])"
    v = re.sub(r"\d+(?:\.\d+)?\s*(?:to|[-~～–—…])\s*\d+(?:\.\d+)?" + other_unit + r"|\d+(?:\.\d+)?" + other_unit, " ", v)
    minimum = re.search(r"\bmin(?:imum)?\s*:?\s*" + number, v, re.I)
    maximum = re.search(r"\bmax(?:imum)?\s*:?\s*" + number, v, re.I)
    tolerance = re.search(
        number + r"\s*(?:V(?:\s*(?:DC|AC))?)?\s*\(?\s*(?:regulated\s*)?\(?\s*±\s*" + number + r"\s*(%)?", v, re.I,
    )
    if re.search(r"\b(?:max(?:imum)?|min(?:imum)?)\b", v, re.I) and not (minimum and maximum):
        return None
    options = None if (minimum and maximum) else re.search(r"[,，/]|\bor\b", v, re.I)
    if options:
        if not re.search(r"\b(?:compatible|either|or)\b", v, re.I):
            return None
        alternatives = re.split(r"[,，/]|\bor\b", v, flags=re.I)
        modes = [parse_supply_voltage(f"{label} (V)", option) for option in alternatives]
        if any(mode is None for mode in modes):
            return None
        bounds = sorted({tuple(map(Decimal, (mode.split("-") * 2)[:2])) for mode in modes})
        # " or " means separate versions/modes. Overlapping alternatives can't
        # be told apart, so give the range every alternative supports.
        if any(hi >= lo for (_, hi), (lo, _) in zip(bounds, bounds[1:])):
            lo, hi = max(b[0] for b in bounds), min(b[1] for b in bounds)
            if lo > hi:
                return None
        else:
            return " or ".join(
                fmt(lo) if lo == hi else f"{fmt(lo)}-{fmt(hi)}" for lo, hi in bounds)
    elif minimum and maximum:
        lo, hi = Decimal(minimum[1]), Decimal(maximum[1])
    elif tolerance:
        # "3.3~5V ±5%", "3.3V ±5% to 5V ±5%": a tolerance on a range, or on two values not
        # joined by "or", can't be read as one interval.
        if v.count("±") > 1 or re.search(number + r"\s*V?\s*(?:to|[-~～–—…])\s*" + number, v, re.I):
            return None
        nominal, delta = Decimal(tolerance[1]), Decimal(tolerance[2])
        if tolerance[3]:
            delta *= nominal / 100
        lo, hi = nominal - delta, nominal + delta
    else:
        interval = re.search(number + r"\s*V?\s*(?:to|[-~～–—…])\s*" + number, v, re.I)
        if interval:
            lo, hi = Decimal(interval[1]), Decimal(interval[2])
            # Another voltage beside the range: a nominal inside it ("12V DC (9～16V DC)",
            # "6–14 V (12 V recommended)") is fine; one outside or at its edge ("DC 5V 0.5-4.5V",
            # "5V; 1-5V") leaves the supply unclear.
            others = re.findall(r"(\d+(?:\.\d+)?)\s*V", v[:interval.start()] + " " + v[interval.end():], re.I)
            if any(not lo < Decimal(other) < hi for other in others):
                return None
        else:
            numbers = re.findall(number, v)
            if len(numbers) != 1 or "±" in v:
                return None
            lo = hi = Decimal(numbers[0])
    if not 0 < lo <= hi <= 48:
        return None
    return f"{fmt(lo)}-{fmt(hi)}" if lo != hi else fmt(lo)


# ── HTTP timeouts ───────────────────────────────────────────────────────────
# wafer's `timeout` is a TOTAL budget covering every retry, rotation and backoff
# — not a per-attempt cap like requests/httpx. Without an `attempt_timeout` a
# single hanging request eats the whole budget, so `max_retries`/`max_rotations`
# never fire and the source hard-fails. That is exactly how maxbotix.com killed
# the 2026-08-01 scrape: one tarpitted request burned all 30s on a single try,
# failed the source, and gated the deploy for all 14 sources.

def attempt_cap(total: float) -> float:
    """Per-attempt cap fitting ~3 bounded tries inside a `total` wafer budget.

    Costs no extra worst-case wall time — the total budget is unchanged — but
    turns one long hang into several bounded tries on rotated TLS identities.
    """
    return round(total / 3, 1)


def make_session(request_timeout: float, **kwargs) -> wafer.SyncSession:
    """Build a SyncSession for product-page scraping whose retries can fire.

    `request_timeout` is the per-request total the caller passes to session.get();
    each attempt is capped at a third of it (see `attempt_cap`).
    """
    kwargs.setdefault("rate_limit", 2.0)
    kwargs.setdefault("rate_jitter", 1.0)
    kwargs.setdefault("attempt_timeout", attempt_cap(request_timeout))
    return wafer.SyncSession(**kwargs)

# ── Skip words: normalized results that are NOT sensor ICs ──────────────────

SKIP_WORDS = {
    "sensor", "sensors", "library", "driver", "arduino", "esp32", "esp8266",
    "module", "board", "kit", "test", "example", "demo", "generic", "simple",
    "basic", "advanced", "helper", "util", "utils", "tool", "tools", "core",
    "base", "common", "shield", "hat", "cape", "wing", "feather", "phat",
}

# ── IC manufacturer names: regex pattern -> canonical name ────────────────────
# Used to extract manufacturer from Arduino library descriptions.
# All patterns use word boundaries to avoid substring matches
# (e.g. "maxim" in "maximum", "sharp" in "sharpness").
# Order: longer/more specific patterns first.
MANUFACTURER_PATTERNS = [
    (r"\btexas instruments\b", "Texas Instruments"),
    (r"\banalog devices\b", "Analog Devices"),
    (r"\bstmicroelectronics\b", "STMicroelectronics"),
    (r"\bsilicon labs\b", "Silicon Labs"),
    (r"\bon semiconductor\b", "ON Semiconductor"),
    (r"\bte connectivity\b", "TE Connectivity"),
    (r"\bmeasurement specialties\b", "TE Connectivity"),
    (r"\baustria micro\w*\b", "ams-OSRAM"),
    (r"\bsciosense\b", "ScioSense"),
    (r"\binvensense\b", "InvenSense"),
    (r"\bbosch\b", "Bosch"),
    (r"\bsensirion\b", "Sensirion"),
    (r"\bhoneywell\b", "Honeywell"),
    (r"\bvishay\b", "Vishay"),
    (r"\bmaxim integrated\b", "Maxim"),
    (r"\bdallas[/\s]+maxim\b", "Maxim"),
    (r"\bmelexis\b", "Melexis"),
    (r"\binfineon\b", "Infineon"),
    (r"\bmicrochip\b", "Microchip"),
    (r"\bbroadcom\b", "Broadcom"),
    (r"\brenesas\b", "Renesas"),
    (r"\ballegro\b", "Allegro"),
    (r"\bpanasonic\b", "Panasonic"),
    (r"\bplantower\b", "Plantower"),
    (r"\brohm\b", "ROHM"),
    (r"\bmurata\b", "Murata"),
    (r"\bomron\b", "Omron"),
    (r"\bwinsen\b", "Winsen"),
    (r"\bamphenol\b", "Amphenol"),
    (r"\bsharp\b(?!\s*(?:edge|turn|corner|increase))", "Sharp"),
    # Short names last — require word boundaries
    (r"\bst\b", "STMicroelectronics"),
    (r"\bnxp\b", "NXP"),
    (r"\bams\b", "ams-OSRAM"),
    (r"\btdk\b", "TDK"),
    (r"\bti\b", "Texas Instruments"),
]

# Pre-compile for performance
_MANUFACTURER_RE = [(re.compile(pat, re.IGNORECASE), canonical) for pat, canonical in MANUFACTURER_PATTERNS]


def extract_manufacturer(text: str) -> str | None:
    """Extract IC manufacturer from text using known manufacturer patterns."""
    for pattern, canonical in _MANUFACTURER_RE:
        if pattern.search(text):
            return canonical
    return None


# ── Measure keywords: text patterns -> measure types ─────────────────────────

MEASURE_KEYWORDS = {
    "temperature": ["temperature", "thermometer", "thermocouple", "thermopile", "thermistor", "pyrometer", "rtd"],
    "humidity": ["humidity", "hygrometer"],
    "pressure": ["pressure", "barometric", "barometer", "altimeter"],
    "distance": ["distance", "rangefinder", "ranging", "range sensor", "range finder", "time of flight", "ultrasonic", "lidar", "tof sensor"],
    "ultrasonic": ["ultrasonic", "sonar sensor", "sonar range"],
    "lidar": ["lidar", "laser range", "laser distance", "laser ranging"],
    "tof": ["time of flight", "tof sensor", "tof module"],
    "acceleration": ["accelerometer", "acceleration", "accel"],
    "gyroscope": ["gyroscope", "gyro", "angular rate"],
    "magnetic_field": ["magnetometer", "magnetic", "compass", "heading", "geomagnetic", "hall.effect"],
    "light": ["light sensor", "lux", "luminosity", "ambient light", "photodiode", "phototransistor", "light intensity", "light to digital", "light to frequency"],
    "color": ["color sensor", "color sensing", "colour sensor", "colour light", "color spectrum", "rgb sensor", "spectral sensor", "spectroscopy", "spectrometer", "tristimulus"],
    "uv": ["uv", "ultraviolet"],
    "gas": ["gas sensor", "gas detect", "voc", "tvoc", "air quality", "air purif", "hydrogen", "methane", "ozone", "alcohol sensor", "alcohol detect", "smoke detect", "h2 sensor", "ch4 sensor", "chemical sens", "lpg", "ethanol sensor", "formaldehyde", "hcho"],
    "voc": ["voc", "tvoc", "volatile organic"],
    "nh3": ["nh3", "ammonia"],
    "formaldehyde": ["formaldehyde", "hcho", "ch2o"],
    "ozone": ["ozone", "o3 sensor", "o3 detect"],
    "h2s": ["h2s", "hydrogen sulfide"],
    "co2": ["co2", "co₂", "carbon dioxide"],
    "particulate": ["particulate", "pm2.5", "pm10", "dust sensor", "dust detect", "particle sensor", "particle matter"],
    "current": ["current sensor", "current monitor", "power monitor", "energy monitor", "energy meter", "current and voltage", "current and power", "power, current"],
    "voltage": ["voltage sensor", "voltage monitor", "voltage and current", "current and voltage", "current, and voltage"],
    "sound": ["sound", "noise", "microphone", "spl"],
    "weight": ["weight", "load cell", "scale", "weighing"],
    "touch": ["touch sensor", "capacitive touch", "touch screen", "touchscreen", "capacitive sensor"],
    "ir_temperature": ["ir temperature", "infrared temperature", "non-contact temperature", "thermal imaging", "thermal sensor", "ir camera", "infrared sensor"],
    "proximity": ["proximity", "presence sensor", "presence detect"],
    "gesture": ["gesture"],
    "biometric": ["heart rate", "pulse oximeter", "pulse sensor", "spo2", "oximeter", "ecg", "eeg", "emg", "ppg", "biomedical", "bio-impedance"],
    "motion": ["pir", "motion detect", "motion sensor", "radar sensor", "radar module", "presence detect", "human presence", "object is moving"],
    "pir": ["pir", "pyroelectric infrared", "pyroelectric sensor", "passive infrared"],
    "radar": ["radar sensor", "radar module", "mmwave", "millimeter wave", "fmcw radar", "doppler radar"],
    "flow": ["flow meter", "flow sensor"],
    "soil_moisture": ["soil moisture", "soil sensor"],
    "moisture": ["moisture sensor", "moisture detect"],
    "gps": ["gps", "gnss"],
    "rotation": ["rotary encoder", "angle sensor", "angle position", "angle measurement", "rotary position", "quadrature encoder"],
    "co": ["carbon monoxide", "co sensor", "co detect"],
    "radiation": ["geiger", "radiation"],
    "rain": ["rain sensor", "rain gauge", "rainfall"],
    "wind": ["wind sensor", "wind speed", "anemometer", "wind direction"],
    "water_quality": ["tds", "water quality", "conductivity sensor", "ph sensor", "ph4502", "turbidity", "dissolved oxygen"],
    # pH, ORP, dissolved oxygen and electrical conductivity are measures of their own (Atlas uses them);
    # water_quality alone left DFRobot's SEN0161 pH meter out of measure="ph". Not "thermal conductivity".
    "ph": ["ph sensor", "ph meter", "ph probe", "ph electrode", "ph value", "ph4502"],
    "orp": ["orp sensor", "orp meter", "orp probe", "redox potential", "oxidation reduction potential", "oxidation-reduction potential"],
    "dissolved_oxygen": ["dissolved oxygen"],
    "conductivity": ["electrical conductivity", "ec sensor", "ec meter", "ec probe", "conductivity probe", "conductivity meter", "water conductivity"],
    "oxygen": ["oxygen sensor", "oxygen concentration", "o2 sensor"],
    "tilt": ["tilt sensor", "inclinometer"],
    "vibration": ["vibration sensor", "vibration detect", "shock sensor", "wake on shake"],
    "force": ["force sensor", "force sens", "strain gauge", "strain sensor", "flex sensor", "fsr"],
    "optical": ["optical sensor", "reflective sensor", "reflective optical"],
    "weather": ["weather station", "weather sensor"],
}


# ── Shared utilities ────────────────────────────────────────────────────────

def strip_identity_prefixes(raw: str, known_ids=()) -> str:
    """Prefer known identities after removing vendor/library wrappers.

    Lookup also accepts digit-first models (24GHzRadar) and short stems
    (A02YYUW). Unknown models retain the conservative shape-based rule.
    Kept identical in the standalone database builder for Docker builds.
    """
    normalize = lambda value: re.sub(r"[^a-z0-9]", "", value.lower())
    library_prefixes = (
        "adafruit", "sparkfun", "dfrobot", "micropython", "esp", "circuitpython",
        "grove", "seeed", "closedcube", "bluedot", "artronshop", "sensirion",
        "protocentral", "stm32duino", "reefwing", "pwfusion", "arduino",
        "smarteverything", "bolderflight_systems", "bolderflightsystems",
    )
    prefixes = ("7semi", "microfire", "ioty", "hlk", "omron", "my") + library_prefixes
    pending = [raw]
    seen = set()
    while pending:
        candidate = pending.pop(0)
        key = normalize(candidate)
        if candidate != raw and key in known_ids:
            return candidate
        if key in seen:
            continue
        seen.add(key)
        for prefix in prefixes:
            if candidate.lower().startswith(prefix):
                rest = candidate[len(prefix):].lstrip(" _. -")
                if rest:
                    pending.append(rest)
    # For new models, strip library prefixes only at a separator boundary.
    stripped = re.sub(
        r"^(?:" + "|".join(library_prefixes) + r")[\s_.-]+", "", raw, flags=re.I,
    )
    if stripped != raw:
        return strip_identity_prefixes(stripped, known_ids)
    return re.sub(
        r"^(?:(?:7semi|microfire|ioty|hlk|omron)[\s_.-]*|my[\s_.-]*(?=[a-z]{2,}\d))"
        r"(?=[a-z]+[\s_.-]*\d)", "", raw, flags=re.IGNORECASE,
    )


@lru_cache(maxsize=1)
def _known_sensor_ids() -> frozenset[str]:
    """Published/source identities, including persistent curated exclusions."""
    directory = Path(__file__).resolve().parents[2] / "data" / "sensors"
    known = set()
    for path in directory.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if path.stem in {"ic_aliases", "curated"}:
            known.update(data)
            if path.stem == "ic_aliases":
                known.update(data.values())
        elif isinstance(data, dict):
            known.update(sensor["id"] for sensor in data.get("sensors", []))
    return frozenset(re.sub(r"[^a-z0-9]", "", sid.lower()) for sid in known)


def normalize_sensor_id(raw: str) -> str | None:
    """Normalize a raw name to a canonical sensor IC identifier, or None if not IC-like."""
    s = strip_identity_prefixes(raw, _known_sensor_ids()).lower()
    # Normalize all separators to underscore so prefix/suffix stripping works
    s = re.sub(r'[\s\-_.]+', '_', s).strip('_')
    # Strip common prefixes (may need multiple passes: "adafruit_circuitpython_bme280")
    changed = True
    while changed:
        changed = False
        for prefix in ("adafruit_", "sparkfun_", "dfrobot_", "micropython_", "esp_",
                        "circuitpython_", "grove_", "seeed_", "closedcube_", "bluedot_",
                        "artronshop_", "sensirion_", "protocentral_", "stm32duino_",
                        "reefwing_", "pwfusion_", "arduino_", "smarteverything_",
                        "bolderflight_systems_", "bolderflightsystems_"):
            if s.startswith(prefix):
                s = s[len(prefix):]
                changed = True
        stripped = strip_identity_prefixes(s, _known_sensor_ids())
        if stripped != s:
            s = stripped
            changed = True
    # Strip common suffixes (may need multiple passes)
    changed = True
    while changed:
        changed = False
        for suffix in ("_library", "_sensor", "_driver", "_lib", "_arduino", "_breakout",
                        "_i2c", "_spi", "_uart", "_we", "_rt", "_asukiaaa", "_dev",
                        "_mi", "_lite", "_mini", "_micropython", "_lopy", "_pyboard",
                        "_py", "_puremp", "_esp32", "_esp8266", "_mqtt", "_mpy", "_upy",
                        "_pico", "_minimal", "_nb", "_streamer", "_mqtt_streamer",
                        "_mqtt_micropython", "_with_pyboard", "_with", "_pure_mp",
                        "_mpy_driver"):
            if s.endswith(suffix):
                s = s[:-len(suffix)]
                changed = True
    # Remove non-alphanumeric
    s = re.sub(r'[^a-z0-9]', '', s)
    if len(s) < 2 or s in SKIP_WORDS or s.isdigit():
        return None
    return s


def has_ic_pattern(s: str) -> bool:
    """Check if a string looks like an IC identifier (has both letters and digits)."""
    return bool(re.search(r'[a-z]', s) and re.search(r'[0-9]', s) and len(s) >= 3)


# Patterns that produce false positives in keyword matching.
# Each tuple: (measure, regex_pattern) — if measure matched AND regex matches, remove it.
_FALSE_POSITIVE_PATTERNS = [
    # Compensation data supplied by the host is not a sensor measurement.
    # ...including coordinated ("temperature and humidity compensation", "humidity/temperature compensated")
    ("temperature", re.compile(
        r'\b(?:(?:humidity|RH)\s*(?:and|&|/)\s*)?temperature(?:\s*(?:and|&|/)\s*(?:humidity|RH))?[- ]compensat(?:ion|ed|ing)\b',
        re.IGNORECASE)),
    ("humidity", re.compile(
        r'\b(?:temperature\s*(?:and|&|/)\s*)?humidity(?:\s*(?:and|&|/)\s*temperature)?[- ]compensat(?:ion|ed|ing)\b',
        re.IGNORECASE)),
    # Oxygen dissolved in water is dissolved_oxygen, not the oxygen gas measure
    ("oxygen", re.compile(r'\bdissolved\s+oxygen\b', re.IGNORECASE)),
    # Thermal conductivity (gas sensing, e.g. STC31) is not water conductivity
    ("water_quality", re.compile(r'\bthermal\s+conductivity\b', re.IGNORECASE)),
    # Thermal/infrared radiation is heat sensing (Winsen ZMT510-A boil-dry sensor), not ionizing radiation
    ("radiation", re.compile(r'\b(?:thermal|infrared|heat)\s+radiation\b', re.IGNORECASE)),
    # "color temperature" is a light property (Kelvin), not thermal temperature
    ("temperature", re.compile(r'\bcolor\s+temperature', re.IGNORECASE)),
    # "thermopile-based" describes sensing mechanism, not temperature measurement
    ("temperature", re.compile(r'\bthermopile[- ]based\b', re.IGNORECASE)),
    # "radar altimeter" measures distance via radar, not barometric pressure
    ("pressure", re.compile(r'\bradar\s+altimeter', re.IGNORECASE)),
    # A load cell's "5kg of pressure (force)" / "(e.g. pressure or force)" is the applied load,
    # not a fluid or barometric pressure (SparkFun TAL220B, TAL221)
    ("pressure", re.compile(r'\bpressure\s*\(force\)|\bpressure\s+or\s+force\b', re.IGNORECASE)),
    # "low noise" describes an ADC or magnetometer (AD7193, ADS122C04, BMM150), not a sound sensor
    ("sound", re.compile(r'\blow[- ]noise\b', re.IGNORECASE)),
    # "scaled" values and the company Iowa Scaled Engineering are not a weighing scale
    ("weight", re.compile(r'\bscaled\b', re.IGNORECASE)),
    # An ADC's "PGA/FSR" is its full-scale range, not a force-sensing resistor (TLA2021)
    ("force", re.compile(r'\bPGA\s*/\s*FSR\b', re.IGNORECASE)),
]


def _remove_gas_if_only_air_quality(text: str, measures: list[str]) -> list[str]:
    """Remove 'gas' from measures if it was only triggered by 'air quality'
    and 'particulate' is already present (PM sensors marketed as air quality)."""
    if "gas" in measures and "particulate" in measures:
        # Check if "air quality" is the only gas keyword that matched
        text_lower = text.lower()
        gas_keywords = MEASURE_KEYWORDS["gas"]
        non_aq_match = any(
            kw != "air quality" and re.search(
                rf'\b{re.escape(kw)}(?:e?s|e?rs?|ors?|e?d|ing|ion)?\b', text_lower
            )
            for kw in gas_keywords
        )
        if not non_aq_match:
            measures = [m for m in measures if m != "gas"]
    return measures


def infer_measures(text: str) -> list[str]:
    """Scan text for MEASURE_KEYWORDS using word-boundary matching.

    Uses \\b at word start and allows optional morphological suffixes
    (s/es/er/ers/or/ors/ed/ing/ion) to handle 'accelerometers',
    'detector', 'detection' etc., while still preventing 'lightweight'
    from matching 'light'.
    """
    text_lower = text.lower()
    measures = sorted(set(
        measure for measure, keywords in MEASURE_KEYWORDS.items()
        if any(re.search(rf'\b{re.escape(kw)}(?:e?s|e?rs?|ors?|e?d|ing|ion)?\b', text_lower) for kw in keywords)
    ))

    # Remove false positives
    for fp_measure, fp_pattern in _FALSE_POSITIVE_PATTERNS:
        if fp_measure in measures and fp_pattern.search(text):
            # Only remove if the false positive pattern is the ONLY reason for the match
            # Check if there's a legitimate match without the false positive context
            cleaned = fp_pattern.sub('', text)
            cleaned_lower = cleaned.lower()
            still_matches = any(
                re.search(rf'\b{re.escape(kw)}(?:e?s|e?rs?|ors?|e?d|ing|ion)?\b', cleaned_lower)
                for kw in MEASURE_KEYWORDS[fp_measure]
            )
            if not still_matches:
                measures.remove(fp_measure)

    # Remove spurious "gas" when only triggered by "air quality" on PM sensors
    measures = _remove_gas_if_only_air_quality(text, measures)

    # "IMU", "6-axis" and "9-DoF" don't say which inertial sensors a part has, so they
    # aren't keywords (they gave magnetometers a gyroscope). But a text that names no
    # inertial or magnetic measure at all ("6-axis IMU", "inertial measurement unit")
    # still describes at least an accelerometer and gyroscope; without this the
    # scrapers dropped LSM6DSV16X, ICM-42688, BMI088 and others as non-sensors.
    if not {"acceleration", "gyroscope", "magnetic_field"} & set(measures) and _IMU_TEXT.search(text):
        measures = sorted(set(measures) | {"acceleration", "gyroscope"})
    # Nine axes are always 3 accelerometer + 3 gyroscope + 3 magnetometer, so a 9-DoF text
    # naming only its accelerometer still has a gyroscope (SparkFun BNO086). A 6-DoF part can be
    # accelerometer + magnetometer, and board libraries name 9-DoF boards after a 6-axis chip, so
    # neither the magnetometer nor 6-axis texts get this.
    if "acceleration" in measures and "gyroscope" not in measures and _NINE_AXIS_TEXT.search(text):
        measures = sorted(set(measures) | {"gyroscope"})

    return measures


_IMU_TEXT = re.compile(
    r"\bimus?\b|\binertial[- ]measurement\b|\b(?:6|six|9|nine|10|ten)[- ]?(?:axis|dof)\b", re.IGNORECASE)
_NINE_AXIS_TEXT = re.compile(r"\b(?:9|nine|10|ten)[- ]?(?:axis|dof)\b", re.IGNORECASE)


def make_sensor_entry(
    sensor_id: str,
    name: str,
    *,
    measures: list[str] | None = None,
    popularity: int = 0,
    platforms: list[str] | None = None,
    urls: list[str] | None = None,
    description: str | None = None,
    protocol: list[str] | None = None,
    i2c_address: list[str] | None = None,
    manufacturer: str | None = None,
    datasheet_url: str | None = None,
    voltage: str | None = None,
    sensor_type: str | None = None,
) -> dict:
    """Create a standardized sensor entry dict.

    Only includes fields that have values — no null padding.
    Different sources provide different fields (e.g. ESPHome has protocol/i2c,
    Arduino has manufacturer/popularity).
    """
    entry: dict = {
        "id": sensor_id,
        "name": name,
        "measures": measures or [],
        "platforms": platforms or [],
    }
    # Only include fields that have values
    if popularity:
        entry["popularity"] = popularity
    if urls:
        entry["urls"] = urls
    if description:
        entry["description"] = description
    if protocol:
        entry["protocol"] = protocol
    if i2c_address:
        entry["i2c_address"] = i2c_address
    if manufacturer:
        entry["manufacturer"] = manufacturer
    if datasheet_url:
        entry["datasheet_url"] = datasheet_url
    if voltage:
        entry["voltage"] = voltage
    if sensor_type:
        entry["type"] = sensor_type
    return entry


# A sensor that drops out of a scrape is kept until this many scrapes in a row
# miss it. Sources flicker: on 2026-11-01 the Best Modules listing left out its
# five HT7M21xx PIR modules for one run, though their pages were still up.
REMOVE_AFTER_MISSED_SCRAPES = 3


# A rerun this soon after the last scrape (a re-dispatched job, a local run) is the same
# monthly scrape again: a sensor it misses again does not use up another of its three misses.
SAME_SCRAPE_HOURS = 20


def _previous_source(path: Path) -> tuple[list[dict], dict[str, int], datetime | None]:
    """Sensors, miss counts and scrape time from the last run's file, or nothing if unreadable."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        sensors = [s for s in data.get("sensors", []) if isinstance(s, dict) and s.get("id")]
        missed = {k: v for k, v in data.get("missed_scrapes", {}).items() if isinstance(v, int)}
    except (OSError, ValueError, AttributeError):
        return [], {}, None
    try:
        scraped_at = datetime.fromisoformat(data["scraped_at"])
        if scraped_at.tzinfo is None:
            scraped_at = scraped_at.replace(tzinfo=timezone.utc)
    except (KeyError, TypeError, ValueError):
        scraped_at = None
    return sensors, missed, scraped_at


LINK_CHECK_LIMIT = 25
LINK_CHECK_SECONDS = 120


def _links_gone(urls: list[str]) -> bool:
    """Whether every one of a sensor's own pages answers 404/410 (deleted repo or doc page).

    Anything else (timeouts, 403/429 blocks, 5xx) is not proof, so the sensor stays carried.
    """
    if not urls:
        return False
    with wafer.SyncSession(rate_limit=1.0) as session:
        for url in urls:
            try:
                status = session.get(re.sub(r"\.git$", "", url), timeout=15, attempt_timeout=7).status_code
            except wafer.WaferError:
                return False
            if status not in (404, 410):
                return False
    return True


def write_source_json(source: str, source_url: str, sensors: list[dict], stats: dict, output_dir: Path,
                      links_gone=_links_gone) -> None:
    """Write per-source JSON with metadata.

    Sensors in the previous file but not in `sensors` are carried over, and
    `missed_scrapes` counts how many scrapes in a row have missed each one; the
    REMOVE_AFTER_MISSED_SCRAPES-th miss drops it. A missed sensor whose own pages
    are all gone (404/410: the driver repo was deleted) is dropped at once rather
    than listed for three more months. A sensor that comes back is written as
    scraped and its count cleared. A rerun within SAME_SCRAPE_HOURS of the last
    scrape doesn't add to a count already started, and a sensor found under the
    id today's rules give its old one (hlkld2410 is ld2410) isn't a miss. `stats.sensor_count` stays the number this
    scrape found (the deploy gate fails a source on 0), and `stats.kept_missing`
    counts the carried ones.
    """
    path = output_dir / f"{source}.json"
    previous, previous_missed, previous_at = _previous_source(path)
    rerun = (previous_at is not None
             and datetime.now(timezone.utc) - previous_at < timedelta(hours=SAME_SCRAPE_HOURS))
    found = {s["id"] for s in sensors}

    kept: list[dict] = []
    missed: dict[str, int] = {}
    dropped: list[str] = []
    gone: list[str] = []
    renamed: list[str] = []
    # Link checks are bounded: a source that collapsed (found under half of last time's sensors)
    # keeps everything without checking, and at most LINK_CHECK_LIMIT sensors within
    # LINK_CHECK_SECONDS are checked, so a bad month can't push the job past its time limit.
    checks_left = LINK_CHECK_LIMIT if len(found) * 2 >= len(previous) else 0
    deadline = time.monotonic() + LINK_CHECK_SECONDS
    for sensor in previous:
        sensor_id = sensor["id"]
        if sensor_id in found or sensor_id in missed:
            continue
        # Found under the id today's rules give it (hlkld2410 is now ld2410): not a miss.
        if normalize_sensor_id(sensor_id) in found:
            renamed.append(sensor_id)
            continue
        count = previous_missed.get(sensor_id, 0) + 1
        if rerun and sensor_id in previous_missed:
            count -= 1
        if count >= REMOVE_AFTER_MISSED_SCRAPES:
            dropped.append(sensor_id)
            continue
        if checks_left and time.monotonic() < deadline and sensor.get("urls"):
            checks_left -= 1
            if links_gone(sensor["urls"]):
                gone.append(sensor_id)
                continue
        missed[sensor_id] = count
        kept.append(sensor)

    if kept:
        logger.warning(
            f"{source}: kept {len(kept)} sensors this scrape didn't find: "
            + ", ".join(f"{sensor_id} ({count}/{REMOVE_AFTER_MISSED_SCRAPES})" for sensor_id, count in missed.items())
        )
    if dropped:
        logger.warning(
            f"{source}: dropped {len(dropped)} sensors missing from {REMOVE_AFTER_MISSED_SCRAPES} "
            f"scrapes in a row: {', '.join(dropped)}"
        )

    if gone:
        logger.warning(f"{source}: dropped {len(gone)} sensors whose pages are gone (404/410): {', '.join(gone)}")

    if renamed:
        logger.info(f"{source}: {len(renamed)} sensors found under a new id: {', '.join(renamed)}")

    output = {
        "source": source,
        "source_url": source_url,
        "scraper_version": SCRAPER_VERSION,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "stats": {**stats, "kept_missing": len(kept)},
        "missed_scrapes": missed,
        "sensors": sensors + kept,
    }
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Wrote {len(sensors)} sensors to {path}" + (f" (+{len(kept)} kept)" if kept else ""))
