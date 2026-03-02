"""Zephyr RTOS sensor driver scraper.

Parses devicetree binding YAML files from the Zephyr repository to extract
sensor ICs and their metadata. Adds "zephyr" as a platform tag.
"""

import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .common import (
    extract_manufacturer,
    has_ic_pattern,
    infer_measures,
    make_sensor_entry,
    normalize_sensor_id,
    write_source_json,
)

logger = logging.getLogger(__name__)

SOURCE_URL = "https://github.com/zephyrproject-rtos/zephyr"
BINDINGS_PATH = "dts/bindings/sensor"

# Vendor prefix -> manufacturer name mapping
VENDOR_MAP = {
    "adi": "Analog Devices",
    "allegro": "Allegro",
    "ams": "ams-OSRAM",
    "aosong": "Aosong",
    "asahi-kasei": "Asahi Kasei",
    "awinic": "Awinic",
    "bosch": "Bosch",
    "domintech": "Domintech",
    "espressif": "Espressif",
    "gss": "Gas Sensing Solutions",
    "honeywell": "Honeywell",
    "infineon": "Infineon",
    "invensense": "InvenSense",
    "maxim": "Maxim",
    "mcube": "mCube",
    "memsensing": "MEMSensing",
    "memsic": "Memsic",
    "microchip": "Microchip",
    "murata": "Murata",
    "nordic": "Nordic",
    "nxp": "NXP",
    "pixart": "PixArt",
    "renesas": "Renesas",
    "rohm": "ROHM",
    "sensirion": "Sensirion",
    "silabs": "Silicon Labs",
    "st": "STMicroelectronics",
    "te": "TE Connectivity",
    "ti": "Texas Instruments",
    "vishay": "Vishay",
    "we": "Würth Elektronik",
    "phosense": "Phosense",
    "broadcom": "Broadcom",
    "brcm": "Broadcom",
    "amd": "AMD",
    "atlas": "Atlas Scientific",
    "sensortek": "Sensortek",
    "amphenol": "Amphenol",
    "dfrobot": "DFRobot",
    "liteon": "Lite-On",
    "winsen": "Winsen",
    "avago": "Broadcom",
    "everlight": "Everlight",
    "epcos": "TDK",
    "fintek": "Fintek",
    "hoperf": "HopeRF",
    "isentek": "iSentek",
    "seeed": "Seeed Studio",
    "maxbotix": "MaxBotix",
    "national": "Texas Instruments",
    "pni": "PNI",
    "hamamatsu": "Hamamatsu",
    "semtech": "Semtech",
    "ist": "IST AG",
    "festo": "Festo",
    "meas": "TE Connectivity",
    "peacefair": "Peacefair",
    "ap": "Angst+Pfister",
    "microcrystal": "Micro Crystal",
}

# MCU-internal or non-IC sensor entries to skip
SKIP_COMPATIBLES = {
    # MCU-internal temperature sensors
    "espressif,esp32-temp",
    "nordic,nrf-temp",
    "nuvoton,npcx-adc-cmp",
    "nxp,kinetis-adc16",
    "nxp,tempmon",
    "st,stm32-temp",
    "st,stm32-temp-cal",
    "st,stm32-vbat",
    "st,stm32-vref",
    "zephyr,sensing",
    # Generic/virtual entries
    "ntc-thermistor-generic",
    "voltage-divider",
    "current-sense-amplifier",
    "current-sense-shunt",
    # Specific thermistor part numbers (not standard ICs)
    "epcos,b57861s0103a039",
    "tdk,ntcg163jf103ft1",
    # Generic Grove sensors (no IC)
    "seeed,grove-light",
    "seeed,grove-temperature",
    # MCU-internal (other vendors)
    "raspberrypi,pico-temp",
    "sifli,sf32lb-tsensor",
    # Industrial controller (not a sensor IC)
    "festo,veaa-x-3",
    # Energy meter (not a sensor IC)
    "peacefair,pzem004t",
    # MCU-internal temperature/qdec sensors
    "infineon,xmc4xxx-temp",
    "nxp,lpadc-temp40",
    "nxp,pmc-tmpsns",
    "nxp,tempsense",
    "nxp,qdec-s32",
    "nxp,mcux-qdec",
    "nxp,tpm-qdec",
    "nordic,nrf-qdec",
    "atmel,sam-tc-qdec",
    "st,stm32-qdec",
    "amd,sb-tsi",
    # Too-generic family compatibles (specific models covered by other sources)
    "ti,hdc",
    "honeywell,mpr",
    # Specific thermistor part numbers (passive components, not ICs)
    "murata,ncp15wb473",
    "murata,ncp15xh103",
}

# Prefixes that indicate MCU-internal (not a real sensor IC)
SKIP_PREFIXES = [
    "espressif,esp32",
    "nuvoton,",
    "nxp,kinetis",
    "nxp,lpc",
    "nxp,mcux",
    "nxp,tempmon",
    "nordic,nrf",
    "renesas,ra-",
    "renesas,rz-",
    "st,stm32",
    "ti,am3",
    "ti,cc1",
    "ti,cc2",
    "zephyr,",
    "sifli,",
]

# Known IC -> measures overrides
KNOWN_IC_MEASURES = {
    "bme280": ["humidity", "pressure", "temperature"],
    "bme680": ["gas", "humidity", "pressure", "temperature", "voc"],
    "bmp180": ["pressure", "temperature"],
    "bmp280": ["pressure", "temperature"],
    "bmp388": ["pressure", "temperature"],
    "bmp390": ["pressure", "temperature"],
    "bmp581": ["pressure", "temperature"],
    "ccs811": ["gas", "voc"],
    "ens160": ["gas", "voc"],
    "scd40": ["co2", "humidity", "temperature"],
    "scd41": ["co2", "humidity", "temperature"],
    "sgp40": ["gas", "voc"],
    "sps30": ["particulate"],
    "vl53l0x": ["distance", "tof"],
    "vl53l1x": ["distance", "tof"],
    "vl53l4cd": ["distance", "tof"],
    "tmag5170": ["magnetic_field"],
    "tmag5273": ["magnetic_field"],
    "als31300": ["magnetic_field"],
    "bmi160": ["acceleration", "gyroscope"],
    "bmi270": ["acceleration", "gyroscope"],
    "bmi323": ["acceleration", "gyroscope"],
    "bmi08x": ["acceleration", "gyroscope"],
    "mpu6050": ["acceleration", "gyroscope"],
    "icm20948": ["acceleration", "gyroscope", "magnetic_field"],
    "icm42605": ["acceleration", "gyroscope"],
    "icm42670": ["acceleration", "gyroscope"],
    "icm42688": ["acceleration", "gyroscope"],
    "icm45605": ["acceleration", "gyroscope"],
    "icm45686": ["acceleration", "gyroscope"],
    "fxos8700": ["acceleration", "magnetic_field"],
    "fxas21002": ["gyroscope"],
    "lsm6dso": ["acceleration", "gyroscope"],
    "lsm6dsl": ["acceleration", "gyroscope"],
    "lsm6dsv": ["acceleration", "gyroscope"],
    "lsm9ds1": ["acceleration", "gyroscope", "magnetic_field"],
    "lis2dh": ["acceleration"],
    "lis2dh12": ["acceleration"],
    "lis3dh": ["acceleration"],
    "adxl345": ["acceleration"],
    "adxl362": ["acceleration"],
    "adxl367": ["acceleration"],
    "adxl372": ["acceleration"],
    "bma280": ["acceleration"],
    "bma4xx": ["acceleration"],
    "bmg160": ["gyroscope"],
    "bmm150": ["magnetic_field"],
    "bmm350": ["magnetic_field"],
    "hmc5883l": ["magnetic_field"],
    "ak8975": ["magnetic_field"],
    "ak09918": ["magnetic_field"],
    "lis3mdl": ["magnetic_field"],
    "lsm303dlhc": ["acceleration", "magnetic_field"],
    "ism330dhcx": ["acceleration", "gyroscope"],
    "smi240": ["acceleration", "gyroscope"],
    "smi330": ["acceleration", "gyroscope"],
    "hts221": ["humidity", "temperature"],
    "sht3x": ["humidity", "temperature"],
    "sht4x": ["humidity", "temperature"],
    "shtcx": ["humidity", "temperature"],
    "sts4x": ["temperature"],
    "si7021": ["humidity", "temperature"],
    "sht21": ["humidity", "temperature"],
    "hdc1080": ["humidity", "temperature"],
    "hdc2010": ["humidity", "temperature"],
    "hdc3020": ["humidity", "temperature"],
    "lps22hb": ["pressure", "temperature"],
    "lps22hh": ["pressure", "temperature"],
    "lps25hb": ["pressure", "temperature"],
    "lps331ap": ["pressure", "temperature"],
    "ms5607": ["pressure", "temperature"],
    "ms5611": ["pressure", "temperature"],
    "ms5637": ["pressure", "temperature"],
    "ms8607": ["humidity", "pressure", "temperature"],
    "dps310": ["pressure", "temperature"],
    "icp10100": ["pressure", "temperature"],
    "apds9960": ["color", "gesture", "light", "proximity"],
    "tsl2540": ["light"],
    "tsl2561": ["light"],
    "tsl2591": ["light"],
    "tcs3400": ["color", "light"],
    "veml7700": ["light"],
    "bh1750": ["light"],
    "isl29035": ["light"],
    "opt3001": ["light"],
    "vcnl4040": ["light", "proximity"],
    "vcnl36825t": ["proximity"],
    "max30101": ["biometric"],
    "max30102": ["biometric"],
    "afe4404": ["biometric"],
    "hx711": ["weight"],
    "tmd2620": ["proximity"],
    "wsenhids": ["humidity", "temperature"],
    "wsenisds": ["acceleration", "gyroscope"],
    "wsenitds": ["acceleration"],
    "wsenpads": ["pressure", "temperature"],
    "wsenpdms": ["pressure"],
    "wsenpdus": ["pressure"],
    "wsentids": ["temperature"],
    "fdc2x1x": ["proximity", "touch"],
    "paa3905": ["optical"],
    "paa5100je": ["optical"],
    "ad2s1210": ["rotation"],
    "as5048": ["rotation"],
    "as5600": ["rotation"],
    "qdec": ["rotation"],
    "xbr818": ["motion"],
}


def _should_skip(compatible: str) -> bool:
    """Check if a compatible string represents an MCU-internal or non-sensor entry."""
    if compatible in SKIP_COMPATIBLES:
        return True
    # Don't skip real sensor ICs that happen to match vendor prefixes
    # Check against specific MCU-internal patterns
    for prefix in SKIP_PREFIXES:
        if compatible.startswith(prefix):
            # Allow through known real sensor ICs
            # e.g., "silabs,si7210" should NOT be skipped
            return True
    return False


def _parse_yaml_simple(text: str) -> dict:
    """Simple YAML parser for Zephyr binding files.

    Only extracts top-level string fields we care about: description, compatible, include.
    Avoids PyYAML dependency.
    """
    result = {}

    # Extract description (may be multi-line with |)
    desc_match = re.search(r'^description:\s*\|?\s*\n((?:\s{2,}.*\n?)+)', text, re.MULTILINE)
    if desc_match:
        lines = desc_match.group(1).strip().split('\n')
        result["description"] = ' '.join(line.strip() for line in lines if line.strip())
    else:
        desc_match = re.search(r'^description:\s*(.+)$', text, re.MULTILINE)
        if desc_match:
            result["description"] = desc_match.group(1).strip().strip('"').strip("'")

    # Extract compatible string
    compat_match = re.search(r'^compatible:\s*"([^"]+)"', text, re.MULTILINE)
    if compat_match:
        result["compatible"] = compat_match.group(1)

    # Extract includes to determine protocol
    include_match = re.search(r'^include:\s*\[([^\]]+)\]', text, re.MULTILINE)
    if include_match:
        # Parse array, handling quoted strings with commas (e.g., "vendor,part.yaml")
        raw = include_match.group(1)
        items = re.findall(r'"([^"]+)"|\'([^\']+)\'|([^,\s\[\]]+)', raw)
        result["includes"] = [next(g for g in groups if g) for groups in items]
    else:
        # Single-value include (e.g., "include: ti,ina2xx-common.yaml")
        single_match = re.search(r'^include:\s+(\S+\.yaml)\s*$', text, re.MULTILINE)
        if single_match:
            result["includes"] = [single_match.group(1)]
        else:
            # Multi-line include format (careful: only match YAML list items under include:)
            inc_section = re.search(r'^include:\s*\n((?:\s+-\s+.+\n?)+)', text, re.MULTILINE)
            if inc_section:
                includes = re.findall(r'^\s+-\s+(\S+\.yaml)', inc_section.group(1), re.MULTILINE)
                if includes:
                    result["includes"] = [s.strip().strip('"').strip("'") for s in includes]

    return result


def _extract_protocol(includes: list[str]) -> list[str]:
    """Extract communication protocol from include list."""
    protocols = []
    for inc in includes:
        if "i2c-device" in inc:
            protocols.append("i2c")
        elif "spi-device" in inc:
            protocols.append("spi")
        elif "uart-device" in inc:
            protocols.append("uart")
        elif "one-wire" in inc or "1wire" in inc or "w1-slave" in inc:
            protocols.append("one_wire")
    return sorted(set(protocols))


def _normalize_ic_from_compatible(compatible: str) -> str | None:
    """Extract IC identifier from a devicetree compatible string.

    e.g., "bosch,bme280" -> "bme280"
          "we,wsen-hids-2525020210002" -> "wsen-hids"
          "ti,tmag5273" -> "tmag5273"
          "bosch,bmi08x-accel" -> "bmi08x"
          "st,lsm303dlhc-accel" -> "lsm303dlhc"
          "meas,ms5837-30ba" -> "ms5837"
    """
    # Split on comma to get part after vendor prefix
    parts = compatible.split(",", 1)
    if len(parts) != 2:
        return None
    ic_part = parts[1].strip()

    # For Würth Elektronik WSEN-* sensors, keep the WSEN-XXXX base name
    wsen_match = re.match(r'(wsen-[a-z]+)', ic_part)
    if wsen_match:
        return normalize_sensor_id(wsen_match.group(1))

    # Strip bus suffixes
    ic_part = re.sub(r'[-_](i2c|spi|i3c|common)$', '', ic_part)

    # Strip sub-component suffixes (accel, gyro, magn, etc.)
    ic_part = re.sub(r'[-_](accel|gyro|magn|temp|press|hum)$', '', ic_part)

    # Strip variant/package suffixes from full part numbers
    # e.g., "ms5837-30ba" -> "ms5837", "b57861s0103a039" stays (handled by normalize)
    ic_part = re.sub(r'-\d+[a-z]{1,2}$', '', ic_part)

    return normalize_sensor_id(ic_part)


def scrape_zephyr(output_dir: Path) -> None:
    """Scrape Zephyr RTOS devicetree sensor bindings."""
    # Clone with sparse checkout for just the sensor bindings
    tmpdir = tempfile.mkdtemp(prefix="zephyr_")
    try:
        logger.info("Cloning Zephyr repository (sparse checkout)...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
             "https://github.com/zephyrproject-rtos/zephyr.git", tmpdir],
            capture_output=True, check=True, timeout=60,
        )
        subprocess.run(
            ["git", "sparse-checkout", "set", BINDINGS_PATH],
            capture_output=True, check=True, cwd=tmpdir, timeout=30,
        )

        bindings_dir = Path(tmpdir) / BINDINGS_PATH
        if not bindings_dir.exists():
            logger.error(f"Bindings directory not found: {bindings_dir}")
            return

        yaml_files = sorted(bindings_dir.glob("*.yaml"))
        logger.info(f"Found {len(yaml_files)} binding files")

        # Pre-parse all YAML files so we can resolve include chains
        all_parsed: dict[str, dict] = {}
        for yaml_file in yaml_files:
            text = yaml_file.read_text(errors="replace")
            all_parsed[yaml_file.name] = _parse_yaml_simple(text)

        ic_data: dict[str, dict] = {}
        skipped_internal = 0
        skipped_bus_variant = 0

        for yaml_file in yaml_files:
            parsed = all_parsed[yaml_file.name]

            compatible = parsed.get("compatible")
            if not compatible:
                # Bus-variant files (e.g., bme280-i2c.yaml) inherit from common
                # and may not have their own compatible - skip
                skipped_bus_variant += 1
                continue

            # Skip MCU-internal sensors
            if _should_skip(compatible):
                skipped_internal += 1
                continue

            # Extract IC identifier
            ic_id = _normalize_ic_from_compatible(compatible)
            if not ic_id:
                continue

            # Extract description
            description = parsed.get("description", "")

            # Extract protocol from includes, following include chains up to 3 levels
            includes = parsed.get("includes", [])
            protocol = _extract_protocol(includes)
            if not protocol:
                # Follow include chain to find bus type
                seen = set()
                to_check = list(includes)
                for _ in range(3):  # max depth
                    if not to_check or protocol:
                        break
                    next_check = []
                    for inc in to_check:
                        # inc might be "ti,hdc20xx.yaml" or "sensor-device.yaml"
                        inc_name = inc if inc.endswith(".yaml") else inc + ".yaml"
                        if inc_name in seen or inc_name not in all_parsed:
                            continue
                        seen.add(inc_name)
                        parent = all_parsed[inc_name]
                        parent_includes = parent.get("includes", [])
                        protocol = _extract_protocol(parent_includes)
                        if protocol:
                            break
                        next_check.extend(parent_includes)
                    to_check = next_check

            # Extract manufacturer from vendor prefix
            vendor = compatible.split(",")[0]
            manufacturer = VENDOR_MAP.get(vendor)
            if not manufacturer and description:
                manufacturer = extract_manufacturer(description)

            # Determine measures
            if ic_id in KNOWN_IC_MEASURES:
                measures = KNOWN_IC_MEASURES[ic_id]
            else:
                measures = infer_measures(description)

            # Must have measures or IC pattern
            if not measures and not has_ic_pattern(ic_id):
                continue

            if ic_id not in ic_data:
                ic_data[ic_id] = {
                    "name": ic_id.upper(),
                    "measures": set(),
                    "protocol": set(),
                    "description": description,
                    "manufacturer": manufacturer,
                    "compatible": compatible,
                }

            entry = ic_data[ic_id]
            entry["measures"].update(measures)
            if protocol:
                entry["protocol"].update(protocol)
            # Keep longer description
            if description and len(description) > len(entry.get("description", "")):
                entry["description"] = description
            # Fill manufacturer if not set
            if manufacturer and not entry.get("manufacturer"):
                entry["manufacturer"] = manufacturer

        # Build output
        sensors = []
        skipped_no_measures = 0
        for ic_id, agg in sorted(ic_data.items()):
            if not agg["measures"]:
                skipped_no_measures += 1
                continue

            desc = agg["description"]
            if desc and len(desc) > 200:
                desc = desc[:197] + "..."

            url = f"https://docs.zephyrproject.org/latest/build/dts/api/bindings/sensor/{agg['compatible']}.html"

            entry = make_sensor_entry(
                sensor_id=ic_id,
                name=agg["name"],
                measures=sorted(agg["measures"]),
                platforms=["zephyr"],
                urls=[url],
                description=desc if desc else None,
                protocol=sorted(agg["protocol"]) if agg["protocol"] else None,
                manufacturer=agg.get("manufacturer"),
            )
            sensors.append(entry)

        stats = {
            "sensor_count": len(sensors),
            "total_bindings": len(yaml_files),
            "skipped_internal": skipped_internal,
            "skipped_bus_variant": skipped_bus_variant,
            "skipped_no_measures": skipped_no_measures,
        }
        write_source_json("zephyr", SOURCE_URL, sensors, stats, output_dir)

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
