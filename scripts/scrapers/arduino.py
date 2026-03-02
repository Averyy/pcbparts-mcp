"""Arduino Library Index sensor scraper."""

import logging
import re
from pathlib import Path

import wafer

from .common import (
    extract_manufacturer,
    has_ic_pattern,
    infer_measures,
    make_sensor_entry,
    normalize_sensor_id,
    write_source_json,
)

logger = logging.getLogger(__name__)

# Known IC → measures override. Checked BEFORE NON_SENSOR_PATTERNS and
# infer_measures to rescue popular sensor-adjacent ICs whose descriptions
# are too generic (e.g. ADS1115 described only as "ADC").
KNOWN_IC_MEASURES = {
    "ads1115": ["current", "voltage"],
    "ads1015": ["current", "voltage"],
    "ads1x15": ["current", "voltage"],
    "ads1110": ["current", "voltage"],
    "ads1220": ["current", "voltage"],
    "max30102": ["biometric"],
    "as3935": ["weather"],
    "sr04": ["distance", "ultrasonic"],
    "hcsr04": ["distance", "ultrasonic"],
    "usd1": ["distance", "radar"],
    "vl53l0x": ["distance", "tof"],
    "vl53l1x": ["distance", "tof"],
    "vl53l4cd": ["distance", "tof"],
    "vl53l5cx": ["distance", "tof"],
    "vl6180x": ["distance", "tof"],
    "vl6180": ["distance", "tof"],
    "tmf8801": ["distance", "tof"],
    "tmf8820": ["distance", "tof"],
    "tmf8821": ["distance", "tof"],
    "tof10120": ["distance", "tof"],
    "opt3101": ["distance", "tof"],
}

# ICs that are NOT sensors — explicitly skip even if measures are detected.
# These are display drivers, DACs, etc. that get false positive measure matches.
SKIP_ICS = {"tm1637", "max7219", "ht16k33", "pca9685"}


def scrape_arduino(output_dir: Path) -> None:
    """Scrape Arduino Library Index for sensor ICs."""
    url = "https://downloads.arduino.cc/libraries/library_index.json"
    logger.info(f"Downloading Arduino Library Index...")
    resp = wafer.get(url, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    # Dedup to latest version per library name
    latest = {}
    for lib in data["libraries"]:
        name = lib["name"]
        version_str = lib.get("version", "0.0.0")
        try:
            version_tuple = tuple(int(x) for x in version_str.split("."))
        except (ValueError, AttributeError):
            version_tuple = (0,)
        if name not in latest or version_tuple > latest[name][0]:
            latest[name] = (version_tuple, lib)

    # Filter to Sensors category
    sensor_libs = [lib for _, (_, lib) in latest.items() if lib.get("category") == "Sensors"]
    logger.info(f"Found {len(sensor_libs)} unique sensor libraries")

    # Extract ICs and aggregate
    ic_regex = re.compile(r'\b([A-Z]{2,}[\-]?[0-9]+[A-Z0-9]*)\b')
    ic_data: dict[str, dict] = {}  # normalized_id -> aggregated data

    _html_tag_re = re.compile(r'<[^>]+>')
    for lib in sensor_libs:
        lib_name = lib["name"]
        sentence = _html_tag_re.sub('', lib.get("sentence", "")).strip()
        paragraph = _html_tag_re.sub('', lib.get("paragraph", "")).strip()
        repo = lib.get("repository", "")

        # Strategy 1: regex on sentence (most specific — finds the actual IC model)
        ic_id = None
        if sentence:
            m = ic_regex.search(sentence)
            if m:
                candidate = normalize_sensor_id(m.group(1))
                if candidate and has_ic_pattern(candidate):
                    ic_id = candidate

        # Strategy 2: regex on library name (extracts IC from multi-word names)
        if not ic_id:
            m = ic_regex.search(lib_name)
            if m:
                candidate = normalize_sensor_id(m.group(1))
                if candidate and has_ic_pattern(candidate):
                    ic_id = candidate

        # Strategy 3: normalize full library name (fallback for names like "BME280")
        # Max 15 chars — longer results are mangled library names, not IC IDs
        if not ic_id:
            normalized = normalize_sensor_id(lib_name)
            if normalized and has_ic_pattern(normalized) and len(normalized) <= 15:
                ic_id = normalized

        if not ic_id:
            continue

        # Aggregate
        if ic_id not in ic_data:
            ic_data[ic_id] = {
                "names": [],
                "sentences": [],
                "paragraphs": [],
                "urls": [],
                "count": 0,
            }
        entry = ic_data[ic_id]
        entry["names"].append(lib_name)
        if sentence:
            entry["sentences"].append(sentence)
        if paragraph:
            entry["paragraphs"].append(paragraph)
        if repo and repo not in entry["urls"]:
            entry["urls"].append(repo)
        entry["count"] += 1

    # Non-sensor description patterns — ICs in the "Sensors" category that aren't sensors.
    # Note: no trailing \b — many patterns are prefixes (e.g. "conver" matching "converter")
    NON_SENSOR_PATTERNS = re.compile(
        r'(?:^|\W)(?:'
        r'digital.?potentiometer|digipot|'
        r'digital.?analog.?conver|(?<!\w)dac\b|d/a conver|da conversion|'
        r'analog.?(?:to.?)?digital.?conver|(?<!\w)adc\b|a/d conver|precision analog conver|'
        r'real.?time.?clock|(?<!\w)rtc\b|'
        r'fuel.?gauge|battery.?monitor|battery.?charger|battery.?gas.?gauge|battery shield|'
        r'decoder|demultiplexer|multiplexer|analogue? switch|'
        r'matrix.?switch|cross.?point|'
        r'display.?driver|led.?driver|lcd.?driver|oled.?driver|led.?sink|'
        r'pwm.?driver|constant.?current.?led|rgb.?led(?!\s*sensor)|'
        r'(?<!\w)rfid\b|nfc.?reader|'
        r'barcode|qr.?code|'
        r'fingerprint|'
        r'haptic.?driver|'
        r'motor.?driver|motor.?control|servo.?driver|stepper|'
        r'bluetooth.?module|ble.?module|'
        r'(?<!\w)eeprom\b|(?<!\w)fram\b|flash.?memory|'
        r'io.?expander|port.?expander|gpio.?expander|i/o.?expander|'
        r'speech.?recogn|voice.?recogn|'
        r'ir.?(?:remote|receiver|transmit|library)|rmt.?(?:pheripheral|peripheral)|'
        r'binary.?counter|shift.?register|'
        r'relay.?driver|relay.?module|'
        r'power.?supply|voltage.?regulator|'
        r'clock.?generator|oscillator.?driver|'
        r'(?<!\w)can\b.?(?:controller|transceiver|bus)|'
        r'usb.?(?:hub|switch|controller)|'
        r'ethernet.?(?:controller|switch)|'
        r'audio.?(?:codec|amplifier|dac|player)|stereo.?audio|'
        r'gps.?receiver.?module|'
        r'(?<!\w)camera\b|capture.?image|'
        r'joystick(?!\s*sensor)|game.?port|ps2.?(?:shield|library)|'
        r'i2c.?(?:hub|scanner|adapter|bus.?device|to.?1.?wire|switch|toggle|button)|'
        r'1.?wire.?adapter|'
        r'(?<!\w)encryption\b|'
        r'(?<!\w)lin.?bus\b|'
        r'unique.?identif|(?<!\w)uid\b|'
        r'test.?platform|design.?project|'
        r'colored.?light|neopixel|dotstar|'
        r'4.?20ma.?receiver|'
        r'(?<!\w)lcd\b|'
        r'(?<!\w)i2c.?gpio\b|'
        r'(?:12|24).?(?:bit|channel).?(?:pwm|dac)|'
        r'expansion.?(?:board|module)|'
        r'mouse.?sensor|trackpad'
        r')', re.IGNORECASE)

    # Build sensor entries
    sensors = []
    skipped_nonsensor = 0
    skipped_no_measures = 0
    for ic_id, agg in sorted(ic_data.items()):
        if ic_id in SKIP_ICS:
            skipped_nonsensor += 1
            continue

        # Best description: longest sentence, capped at 200 chars
        best_desc = max(agg["sentences"], key=len) if agg["sentences"] else None
        if best_desc and len(best_desc) > 200:
            best_desc = best_desc[:197] + "..."

        # Check KNOWN_IC_MEASURES first (overrides text inference and NON_SENSOR_PATTERNS)
        if ic_id in KNOWN_IC_MEASURES:
            measures = KNOWN_IC_MEASURES[ic_id]
        else:
            # Use the single most descriptive sentence for each IC: the sentence that
            # matches the most measure keywords is likely the one describing the IC's
            # actual capabilities, not an application-level library description.
            # This avoids aggregation noise (e.g., "gesture recognition with MPU6050").
            best_measures = []
            for sentence in agg["sentences"]:
                m = infer_measures(sentence)
                if len(m) > len(best_measures):
                    best_measures = m
            measures = best_measures

            # If no measures from sentences, try combined text of all descriptions
            if not measures:
                combined = " ".join(agg["sentences"] + agg["paragraphs"])
                measures = infer_measures(combined)

            # Filter out non-sensor ICs: if no measures AND description matches non-sensor patterns, skip
            if not measures:
                all_text = " ".join(agg["sentences"] + agg["paragraphs"])
                if NON_SENSOR_PATTERNS.search(all_text):
                    skipped_nonsensor += 1
                    continue
                # Drop entries with no identifiable measures — quality over quantity.
                # These will be recovered in M2 via cross-referencing with other sources.
                skipped_no_measures += 1
                continue

        # Best name: shortest original library name (closest to IC name)
        best_name = min(agg["names"], key=len) if agg["names"] else ic_id.upper()

        # Extract manufacturer from descriptions
        manufacturer = None
        for sentence in agg["sentences"]:
            manufacturer = extract_manufacturer(sentence)
            if manufacturer:
                break
        if not manufacturer:
            for paragraph in agg["paragraphs"]:
                manufacturer = extract_manufacturer(paragraph)
                if manufacturer:
                    break

        sensors.append(make_sensor_entry(
            sensor_id=ic_id,
            name=best_name,
            measures=measures,
            popularity=agg["count"],
            platforms=["arduino"],
            urls=agg["urls"][:10],
            description=best_desc,
            manufacturer=manufacturer,
        ))

    logger.info(f"Filtered out {skipped_nonsensor} non-sensor ICs, dropped {skipped_no_measures} with no identifiable measures")
    stats = {
        "sensor_count": len(sensors),
        "total_libs_checked": len(sensor_libs),
        "skipped_no_ic": len(sensor_libs) - sum(e["count"] for e in ic_data.values()),
        "skipped_nonsensor": skipped_nonsensor,
        "skipped_no_measures": skipped_no_measures,
    }
    write_source_json("arduino", url, sensors, stats, output_dir)
