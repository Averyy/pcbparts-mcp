"""DFRobot sensor scraper (GitHub API)."""

import json
import logging
import re
import subprocess
from pathlib import Path

from .common import (
    has_ic_pattern,
    infer_measures,
    make_sensor_entry,
    normalize_sensor_id,
    write_source_json,
)

# Well-known IC → measures mapping.
# Used as OVERRIDE (checked before infer_measures) for ICs where text-based
# inference is unreliable due to generic/wrong descriptions.
KNOWN_IC_MEASURES = {
    "bme280": ["humidity", "pressure", "temperature"],
    "bme680": ["gas", "humidity", "pressure", "temperature"],
    "bme68x": ["gas", "humidity", "pressure", "temperature"],
    "bmp280": ["pressure", "temperature"],
    "bmp58x": ["pressure", "temperature"],
    "dht11": ["humidity", "temperature"],
    "dht22": ["humidity", "temperature"],
    "aht20": ["humidity", "temperature"],
    "sht3x": ["humidity", "temperature"],
    "sht20": ["humidity", "temperature"],
    "ads1115": ["current", "voltage"],
    "ads1115010v": ["voltage"],
    "ccs811": ["co2", "gas"],
    "sgp40": ["gas"],
    "sfa40": ["gas"],
    "ags01db": ["gas"],
    "bmi160": ["acceleration", "gyroscope"],
    "bmx160": ["acceleration", "gyroscope", "magnetic_field"],
    "bno055": ["acceleration", "gyroscope", "magnetic_field"],
    "icg20660l": ["acceleration", "gyroscope"],
    "icm42688": ["acceleration", "gyroscope"],
    "itg3200": ["gyroscope"],
    "adxl345": ["acceleration"],
    "lis2dh12": ["acceleration"],
    "10dof": ["acceleration", "gyroscope", "magnetic_field", "pressure"],
    "hmc5883l": ["magnetic_field"],
    "bmm150": ["magnetic_field"],
    "vl53l0x": ["distance"],
    "vl53l1x": ["distance"],
    "tmf8x01": ["distance"],
    "lidar07": ["distance"],
    "urm09": ["distance"],
    "urm13": ["distance"],
    "mlx90621": ["ir_temperature"],
    "max30102": ["biometric"],
    "hx711": ["weight"],
    "paj7620u2": ["gesture"],
    "apds9960": ["color", "gesture", "proximity"],
    "tcs3430": ["color", "light"],
    "as7341": ["color", "light"],
    "bluxv30b": ["light"],
    "ltr308": ["light"],
    "as3935": ["weather"],
    "as6221": ["temperature"],
    "scd4x": ["co2", "humidity", "temperature"],
    "wt61pc": ["acceleration", "gyroscope"],
    "pav3000": ["flow"],
    "ina219": ["current", "voltage"],
    "mics4514": ["gas"],
    "shtc3": ["humidity", "temperature"],
    "tcs34725": ["color", "light"],
    "lis2dw12": ["acceleration"],
    "lwlp5000": ["pressure"],
}

logger = logging.getLogger(__name__)

SOURCE_URL = "https://github.com/DFRobot"

# Repos with proprietary names that map to known sensor ICs
# DFRobot_Name -> canonical IC id (lowercase, no separators)
PROPRIETARY_MAP = {
    "AnalogACurrentSensor": None,  # generic analog, skip
    "ColorWaveSensorAPDS9960": "apds9960",
    "MultiGasSensor": None,  # proprietary multi-gas, skip — no standard IC
    "EnvironmentalSensor": None,  # generic, skip
    "HumanDetection": None,  # C4001 radar, proprietary
    "Gesture": None,  # no IC in name
    "Heartrate": None,  # no IC in name
    "IRDM_Sensor": None,  # proprietary
    "IMU_Show": None,  # visualization tool, not sensor
    "Capacitance": None,  # generic
    # Short family names that lack digits (fail has_ic_pattern)
    "MICS": "mics4514",
    "SHT": "shtc3",
    "TCS": "tcs34725",
    "LIS": "lis2dw12",
    "LWLP": "lwlp5000",
}

# Non-sensor repo name fragments to skip (case-insensitive match against IC part)
SKIP_REPO_FRAGMENTS = {
    # Communication modules
    "relay", "sim808", "sim7000", "sim7600", "sim", "lora", "sx1278",
    "nrf24l01", "wifi", "bluetooth", "bluno", "can", "mcp2515", "w5100s",
    "dmx512", "bt401", "l218", "bc20", "nb", "rtk",
    # Motor/actuator
    "motor", "stepper", "servo", "gmr", "4wd",
    # Display/LED
    "display", "oled", "lcd", "eink", "epaper", "led", "rgb", "neopixel",
    "st7687s", "ili9488", "ssd1306", "tft", "panel", "screen", "touch_screen",
    "lightcube", "osd", "rgbmatrix", "rgblcd", "rgbpanel",
    # Audio/voice (NOT sensors)
    "speaker", "mp3", "dfplayer", "df1101s", "df1201s", "su03t",
    "speechsynthesis", "voice", "df2301q",
    # DAC/ADC/IO (NOT sensors)
    "digitalpot", "mcp4725", "gp8302", "gp8403", "gp8xxx", "pcf8591",
    "ad9837", "i2cmultiplexer", "ch423", "mcp23017",
    # NFC/RFID/fingerprint
    "pn532", "pn7150", "fm17550", "id809",
    # RTC
    "rtc", "ds1307", "ds3231", "ds323x",
    # Storage
    "sd", "flash", "eeprom",
    # Other non-sensor
    "gps", "gnss", "firmware", "raspberry", "utility", "tools", "3d-design",
    "demo", "sample", "testbed", "softwaretools", "4drawing", "basicdemo",
    "accessoryshield", "3v-relay", "ec11",
    # Vision/AI modules (not standard sensor ICs)
    "huskylen", "ai10", "gm60", "rp2040_sci", "isrmodule",
    # Barcode/QR
    "de2120",
    # Camera
    "hm01b0", "ex8036",
    # Amplifier (not sensor)
    "max98357a",
    # Battery gauge (not sensor)
    "max17043",
    # LiDAR (proprietary module, no standard IC)
    "ce30c",
    # Unknown/too generic
    "scw8916b", "tm6605",
    # I2C multiplexer (not sensor)
    "i2c_multiplexer", "i2cmultiplexer",
}

# Suffixes to strip from repo IC part
STRIP_SUFFIXES = {"_old", "_i2c", "_rpi", "_raspberrypi", "_micropython"}


def _run_gh_api(endpoint: str) -> list[dict]:
    """Run gh api command and return parsed JSON."""
    result = subprocess.run(
        ["gh", "api", endpoint, "--paginate"],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh api failed: {result.stderr}")
    # gh --paginate concatenates JSON arrays, need to handle
    text = result.stdout.strip()
    if text.startswith("["):
        # May have multiple arrays concatenated
        # gh --paginate with -q outputs newline-delimited, but raw JSON is arrays
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Multiple arrays concatenated: [...][\n][...]
            all_items = []
            for chunk in re.split(r'\]\s*\[', text):
                chunk = chunk.strip()
                if not chunk.startswith("["):
                    chunk = "[" + chunk
                if not chunk.endswith("]"):
                    chunk = chunk + "]"
                all_items.extend(json.loads(chunk))
            return all_items
    return json.loads(f"[{text}]")


def _should_skip_repo(name: str) -> bool:
    """Check if repo name suggests non-sensor content."""
    name_lower = name.lower().replace("dfrobot_", "")
    return any(frag in name_lower for frag in SKIP_REPO_FRAGMENTS)


def _extract_ic_from_repo(repo_name: str) -> str | None:
    """Extract IC identifier from DFRobot repo name.

    DFRobot_BME280 -> bme280
    DFRobot_VL53L0X -> vl53l0x
    DFRobot_ColorWaveSensorAPDS9960 -> apds9960 (via PROPRIETARY_MAP)
    """
    # Strip DFRobot_ prefix
    if not repo_name.startswith("DFRobot_"):
        return None
    ic_part = repo_name[8:]  # len("DFRobot_") == 8

    # Strip known suffixes
    for suffix in STRIP_SUFFIXES:
        if ic_part.lower().endswith(suffix):
            ic_part = ic_part[:len(ic_part) - len(suffix)]

    # Check proprietary map first
    if ic_part in PROPRIETARY_MAP:
        mapped = PROPRIETARY_MAP[ic_part]
        return mapped  # May be None (skip)

    # Normalize
    normalized = normalize_sensor_id(ic_part)
    if normalized and has_ic_pattern(normalized):
        return normalized

    return None


def _fetch_library_properties(repo_name: str) -> dict | None:
    """Fetch library.properties from a DFRobot repo for description data."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/DFRobot/{repo_name}/contents/library.properties",
             "-q", ".content"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return None

        import base64
        content = base64.b64decode(result.stdout.strip()).decode("utf-8", errors="replace")

        props = {}
        for line in content.splitlines():
            if "=" in line:
                key, _, value = line.partition("=")
                props[key.strip()] = value.strip()
        return props
    except Exception:
        return None


def scrape_dfrobot(output_dir: Path) -> None:
    """Scrape DFRobot GitHub org for sensor breakout board repos."""
    logger.info("Fetching DFRobot repos from GitHub API...")
    repos = _run_gh_api("orgs/DFRobot/repos?per_page=100")
    logger.info(f"Found {len(repos)} total DFRobot repos")

    # Filter to DFRobot_ prefixed repos
    dfrobot_repos = [r for r in repos if r.get("name", "").startswith("DFRobot_")]
    logger.info(f"Found {len(dfrobot_repos)} DFRobot_ prefixed repos")

    # Deduplicate _old repos
    repo_names = set()
    filtered_repos = []
    for repo in dfrobot_repos:
        name = repo["name"]
        # Skip _old if non-old version exists
        if name.endswith("_old"):
            base = name[:-4]
            if any(r["name"] == base for r in dfrobot_repos):
                continue
        if name not in repo_names:
            repo_names.add(name)
            filtered_repos.append(repo)

    logger.info(f"After dedup: {len(filtered_repos)} repos")

    # Extract sensors
    ic_data: dict[str, dict] = {}
    skipped_non_sensor = 0
    skipped_no_ic = 0

    for repo in filtered_repos:
        name = repo["name"]

        # Skip non-sensor repos
        if _should_skip_repo(name):
            skipped_non_sensor += 1
            continue

        # Extract IC
        ic_id = _extract_ic_from_repo(name)
        if ic_id is None:
            skipped_no_ic += 1
            continue

        repo_url = f"https://github.com/DFRobot/{name}"
        desc = repo.get("description") or ""
        topics = repo.get("topics") or []

        if ic_id not in ic_data:
            ic_data[ic_id] = {
                "repo_name": name,
                "urls": [],
                "descriptions": [],
                "topics": set(),
                "stars": 0,
            }
        entry = ic_data[ic_id]
        entry["urls"].append(repo_url)
        if desc:
            entry["descriptions"].append(desc)
        entry["topics"].update(topics)
        entry["stars"] = max(entry["stars"], repo.get("stargazers_count", 0))

    logger.info(f"Found {len(ic_data)} unique ICs, fetching library.properties...")

    # Fetch library.properties for each IC to get better descriptions
    sensors = []
    props_fetched = 0

    for ic_id, data in sorted(ic_data.items()):
        # Try to get library.properties for description
        props = _fetch_library_properties(data["repo_name"])
        if props:
            props_fetched += 1

        # Best description: library.properties sentence > repo description
        desc = None
        if props and props.get("sentence"):
            desc = props["sentence"]
        elif data["descriptions"]:
            desc = max(data["descriptions"], key=len)
        if desc and len(desc) > 200:
            desc = desc[:197] + "..."

        # Use known IC measures as override (reliable), fall back to text inference
        if ic_id in KNOWN_IC_MEASURES:
            measures = KNOWN_IC_MEASURES[ic_id]
        else:
            text_for_measures = f"{data['repo_name']} {desc or ''} {' '.join(data['descriptions'])}"
            measures = infer_measures(text_for_measures)

        # Detect real software platforms from GitHub topics
        platforms = []
        topic_set = {t.lower() for t in data["topics"]}
        if "arduino-library" in topic_set or "arduino" in topic_set:
            platforms.append("arduino")
        if "raspberry-pi" in topic_set or "raspberrypi" in topic_set:
            platforms.append("raspberry_pi")

        # Best name: extract clean IC name from repo
        ic_part = data["repo_name"].replace("DFRobot_", "")
        for suffix in STRIP_SUFFIXES:
            if ic_part.lower().endswith(suffix):
                ic_part = ic_part[:len(ic_part) - len(suffix)]

        sensors.append(make_sensor_entry(
            sensor_id=ic_id,
            name=ic_part,
            measures=measures,
            platforms=sorted(set(platforms)),
            urls=data["urls"][:5],
            description=desc,
        ))

    logger.info(
        f"Extracted {len(sensors)} sensors from {len(dfrobot_repos)} repos "
        f"(skipped: {skipped_non_sensor} non-sensor, {skipped_no_ic} no-IC, "
        f"fetched {props_fetched} library.properties)"
    )
    stats = {
        "sensor_count": len(sensors),
        "total_repos": len(repos),
        "dfrobot_repos": len(dfrobot_repos),
        "skipped_non_sensor": skipped_non_sensor,
        "skipped_no_ic": skipped_no_ic,
        "library_properties_fetched": props_fetched,
    }
    write_source_json("dfrobot", SOURCE_URL, sensors, stats, output_dir)
