"""Shared utilities for sensor scrapers."""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

SCRAPER_VERSION = "1.0.0"

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
    "acceleration": ["accelerometer", "acceleration", "accel", "imu", "inertial", "dof", "six axis", "6 axis", "6-axis", "9 axis", "9-axis", "10 dof", "10dof", "9 dof", "9dof", "6 dof", "6dof"],
    "gyroscope": ["gyroscope", "gyro", "angular rate", "imu", "inertial", "dof", "six axis", "6 axis", "6-axis", "9 axis", "9-axis", "10 dof", "10dof", "9 dof", "9dof", "6 dof", "6dof"],
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
    "oxygen": ["oxygen sensor", "oxygen concentration", "o2 sensor"],
    "tilt": ["tilt sensor", "inclinometer"],
    "vibration": ["vibration sensor", "vibration detect", "shock sensor", "wake on shake"],
    "force": ["force sensor", "force sens", "strain gauge", "strain sensor", "flex sensor", "fsr"],
    "optical": ["optical sensor", "reflective sensor", "reflective optical"],
    "weather": ["weather station", "weather sensor"],
}


# ── Shared utilities ────────────────────────────────────────────────────────

def normalize_sensor_id(raw: str) -> str | None:
    """Normalize a raw name to a canonical sensor IC identifier, or None if not IC-like."""
    s = raw.lower()
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
    # "color temperature" is a light property (Kelvin), not thermal temperature
    ("temperature", re.compile(r'\bcolor\s+temperature', re.IGNORECASE)),
    # "thermopile-based" describes sensing mechanism, not temperature measurement
    ("temperature", re.compile(r'\bthermopile[- ]based\b', re.IGNORECASE)),
    # "radar altimeter" measures distance via radar, not barometric pressure
    ("pressure", re.compile(r'\bradar\s+altimeter', re.IGNORECASE)),
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

    return measures


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


def write_source_json(source: str, source_url: str, sensors: list[dict], stats: dict, output_dir: Path) -> None:
    """Write per-source JSON with metadata."""
    output = {
        "source": source,
        "source_url": source_url,
        "scraper_version": SCRAPER_VERSION,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "sensors": sensors,
    }
    path = output_dir / f"{source}.json"
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    logger.info(f"Wrote {len(sensors)} sensors to {path}")
