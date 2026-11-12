"""Sensor database search — FTS5 + parametric query builder."""

import copy
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

# Load IC aliases for query-time resolution (e.g., "sht31" → "sht3x")
_IC_ALIASES: dict[str, str] = {}
_aliases_path = Path(__file__).parent.parent.parent.parent / "data" / "sensors" / "ic_aliases.json"
if _aliases_path.exists():
    _IC_ALIASES = json.loads(_aliases_path.read_text(encoding="utf-8"))


# Added to these sensors' results: what the part really outputs, read from its datasheet. eco2 is
# calculated from other gases, so these parts aren't listed under co2.
CAPABILITY_NOTES: dict[str, dict[str, Any]] = {
    "max30105": {
        "capability_note": "Obsolete at Analog Devices; sold for smoke/particle detection. The listed voltage is VDD (1.7-2.0V); the LEDs require a separate 3.1-5.25V supply. Source: https://www.analog.com/en/products/max30105.html and its Rev 1 datasheet.",
    },
    "max30100": {"capability_note": "The listed voltage is VDD (1.7-2.0V); the LEDs require a separate 3.1-5.0V supply (Analog Devices MAX30100 datasheet, electrical characteristics)."},
    "as7262": {"capability_note": "Visible spectral sensor. The listed 2.7-3.6V supply range applies to I2C; UART requires 2.97-3.6V (ams AS7262 DS000486, electrical characteristics)."},
    "as7263": {"capability_note": "Near-infrared spectral sensor. The listed 2.7-3.6V supply range applies to I2C; UART requires 2.97-3.6V (ams AS7263 DS000476, electrical characteristics)."},
    "ccs811": {
        "capability_note": "VOC sensing with estimated eCO2 output; humidity and temperature are compensation inputs, not direct measurements.",
        "compensation_inputs": ["humidity", "temperature"],
        "voltage_evidence": {
            "recommended_operating": "1.8-3.3V", "absolute_maximum": "3.6V",
            "source_url": "https://cdn.sparkfun.com/assets/2/c/c/6/5/CN04-2019_attachment_CCS811_Datasheet_v1-06.pdf",
            "document": "ams CCS811 v1-06, 2019-02-07", "printed_pages": [1, 5, 6],
        },
    },
    "ens160": {
        "capability_note": "TVOC and eCO2 are calculated from measured VOCs and hydrogen, so eCO2 is an estimate; humidity and temperature are compensation inputs written by the host, not direct measurements. The listed voltage is VDD; VDDIO is separate, 1.71-3.6V.",
        "compensation_inputs": ["humidity", "temperature"],
        "voltage_evidence": {
            "recommended_operating": "VDD 1.71-1.98V; VDDIO 1.71-3.6V", "absolute_maximum": "VDD 1.98V; VDDIO 3.6V",
            "source_url": "https://www.sciosense.com/wp-content/uploads/2023/12/ENS160-Datasheet.pdf",
            "document": "ScioSense ENS160 v1.3, SC-001224-DS-9, 2023-03-29", "printed_pages": [2, 6, 7],
        },
    },
    "iaqcore": {"capability_note": "CO2 equivalent and TVOC equivalent are predictions from VOC sensing, not a direct CO2 measurement (ams iAQ-Core datasheet v1-00, p.1). Supply 3.3V ±0.1V with at most 20mV ripple, so not 5V (p.3)."},
    "sm300d2": {"capability_note": "CO2 and formaldehyde are equivalent values calculated from the TVOC reading, not measured (the module's parameter table). PM2.5/PM10 (laser), temperature and humidity are measured. Supply 5V ±0.2V."},
    "max32664": {"capability_note": "A sensor hub, not a sensor: a microcontroller with heart-rate and SpO2 firmware that reads a separate optical front end and accelerometer. Versions A and D read a MAX30101/MAX30102, B a MAX86140/MAX86141, C a MAX86140/MAX86141 or MAXM86161 (MAX32664 datasheet Rev 4, p.1)."},
    "max32664c": {"capability_note": "A sensor hub, not a sensor: Version C runs wrist and ear heart-rate firmware and reads a MAX86140/MAX86141 or MAXM86161 front end plus an accelerometer, which must be added (MAX32664 datasheet Rev 4, p.1)."},
    "bme680": {"capability_note": "IAQ and CO2 equivalent come from Bosch's BSEC library running on the host, calculated from the gas reading; the sensor does not measure CO2 directly (BME680 datasheet rev 1.9, p.25). Temperature, humidity and pressure are measured."},
    "bme688": {"capability_note": "IAQ and CO2 equivalent come from Bosch's BSEC2 library running on the host, calculated from the gas reading; CO2 is not measured directly (BME688 datasheet rev 1.3, p.31). Temperature, humidity and pressure are measured."},
    "apc1": {"capability_note": "eCO2 is a CO2 equivalent from the module's MOX gas sensor, not a direct CO2 measurement (ScioSense APC1 datasheet v2.1, p.8). Temperature, humidity and particulates are measured."},
    "pzem004t": {"capability_note": "Mains energy meter: its measuring side is powered by the 80-260VAC line it measures, so it needs mains isolation and clearances. The listed 5V is the external supply its isolated TTL interface needs from the host (Peacefair PZEM-004T V3.0 manual, 1.1.1 and 5.1)."},
    "ky040": {"capability_note": "Its CLK and DT outputs are pulled up to +V, so power it from the MCU's I/O voltage: 3.3V on a 3.3V MCU, or its GPIOs see 5V. Joy-IT's SensorKit wiring tables use 3.3V on Raspberry Pi and 5V on Arduino."},
    "sen6x": {"capability_note": "A family: only SEN63C, SEN66 and SEN69C have a CO2 sensor; SEN62, SEN65 and SEN68 do not (Sensirion SEN6x datasheet v1.0, p.1). Check the exact model."},
    "ens161": {"capability_note": "TVOC and eCO2 are calculated values. The listed voltage is VDD; VDDIO is separate, 1.71-3.6V (ScioSense ENS161 datasheet v1.1, p.7)."},
    "sciosenseens16x": {"capability_note": "Library for ENS160 and ENS161: TVOC and eCO2 are calculated values. The listed voltage is the chips' VDD; VDDIO is separate, 1.71-3.6V, and breakouts may regulate down from 3.3V."},
    "sgp30": {
        "capability_note": "TVOC and CO2eq are calculated from ethanol and H2 signals, so CO2eq is an estimate; absolute humidity is a compensation input written by the host, not a direct measurement.",
        "compensation_inputs": ["humidity"],
        "voltage_evidence": {
            "recommended_operating": "VDD and VDDH 1.62-1.98V", "absolute_maximum": "VDD and VDDH 2.16V",
            "source_url": "https://sensirion.com/file/datasheet_sgp30",
            "document": "Sensirion SGP30 v1.0, May 2020, D1", "printed_pages": [5, 6],
        },
    },
}


# Other supply rails a part needs besides the listed `voltage` (its main supply), from the
# maker sources recorded with each voltage in data/sensors/curated.json (2026-11-10 review).
SUPPLY_RAIL_NOTES: dict[str, str] = {
    "ad8495": "AD8495 supports a single supply of 2.7-36 V or dual supplies of ±2.7 to ±18 V; bipolar operation requires a negative rail.",
    "adpd188bi": "ADPD188BI requires VDD1/VDD2 1.7-1.9 V plus separate LED supplies: VLED1 5.0-6.0 V and VLED3 3.3-4.0 V.",
    "ads122c04": "ADS122C04 requires analog AVDD-AVSS 2.3-5.5 V and digital DVDD-DGND 2.3-5.5 V; bipolar analog operation needs the specified negative AVSS rail.",
    "amc1302": "AMC1302 requires isolated high-side VDD1 and low-side VDD2 supplies; both operate at 3-5.5 V relative to their respective grounds.",
    "apds9930": "APDS-9930 needs VDD 2.2-3.6 V and a separate LED supply VBATT 2.5-4.5 V.",
    "as7262x": "AS7262 and AS7263 require both VDD1 and VDD2: 2.7-3.6 V for I2C, at least 2.97 V for UART.",
    "as734x": "AS734x family main VDD common interval is 1.7-1.98 V. The TCS3448 member requires I2C bus pullups in 1.08-1.32 V or 1.62-1.98 V modes, selected at startup.",
    "bhi385": "BHI385 needs main VDD 1.71-3.6 V and VDDIO 1.71-1.89 V; VDDIO cannot be supplied from 3.3 V.",
    "bma250": "BMA250 needs VDD 1.62-3.6 V and a separate VDDIO rail of 1.2-3.6 V.",
    "bma456": "BMA456 needs VDD 1.62-3.6 V and separate VDDIO 1.2-3.6 V.",
    "bmi330": "BMI330 needs main VDD 1.71-3.63 V and separate VDDIO 1.08-3.63 V; the supplies are independent.",
    "bms36t001": "BMS36T001 logic supply is 3.0-5.5 V; its motor driver additionally needs 5-24 V motor power. Follow the vendor power-up/down order.",
    "bno086": "BNO086 requires sensor VDD 2.4-3.6 V and a separate core/I/O VDDIO rail of 1.65-3.6 V.",
    "bq76972": "BAT normal supply is 4.7-80 V, but 80 V requires charge pump off; reduce BAT with charge pump active to respect CP1/CHG/DSG limits. Separate REGIN LDO supply needs output-dependent headroom (BREG-generated nominal 5.5 V); OTP programming requires BAT 10-12 V.",
    "ds1821": "DS1821 runs on VDD 2.7-5.5 V, but its ±1 °C accuracy, 4 mA DQ sink current and 1-Wire timing are specified only at VDD 3.6-5.5 V.",
    "ds3501": "DS3501 needs VCC 2.7-5.5 V and a separate analog V+ rail of 4.5-15.5 V, with V+ greater than VCC.",
    "dts6012m": "Has a separate power input for its internal laser, which the maker says to filter to keep clean. No readable maker source states the main or laser supply voltages, so `voltage` is empty; get them from the maker's datasheet.",
    "icm20600": "ICM-20600 needs main VDD and separate VDDIO, each 1.71-3.45 V.",
    "icm42688p": "ICM-42688-P needs main VDD and separate VDDIO, each 1.71-3.6 V.",
    "k30": "K30 preferred operating range is 5.0-9 V. 4.5-14 V is its absolute maximum rating (stabilised to within 5%, no reverse-polarity protection); the maker says a 12 V ±10% supply can be used.",
    "l3g4200d": "L3G4200D uses main Vdd 2.4-3.6 V and separate Vdd_IO 1.71 V to Vdd+0.1 V.",
    "l3gd20h": "L3GD20H uses main Vdd 2.2-3.6 V and separate Vdd_IO 1.71 V to Vdd+0.1 V.",
    "l76k": "L76K needs main VCC 2.7-3.4 V and V_BCKP supplied no later than VCC; follow the maker RTC-backup circuit.",
    "lc26g": "LC26G (AB) needs VCC 2.55-3.6 V and V_BCKP 1.65-3.6 V supplied no later than VCC; V_BCKP is required for startup.",
    "lg290p": "LG290P (03) needs VCC 3.0-3.6 V and V_BCKP 2.0-3.6 V supplied no later than VCC; V_BCKP is required for startup.",
    "lidar07": "LIDAR07/SEN0413 exposes separate VCC/GND module and VCC_LED/GND_LED light-source supply pins; follow the vendor pinout and 4.8-5.2 V supply specification.",
    "max30009": "MAX30009 needs analog AVDD and digital DVDD, both 1.7-2.0 V; follow the AVDD/DVDD sequencing constraints.",
    "max3010x": "MAX30100/30101/30102 core VDD is 1.7-2.0 V. Separate LED rails: MAX30100/30102 3.1-5.0 V; MAX30101 red/IR 3.1-5.0 V and green 4.5-5.5 V.",
    "max78630": "MAX78630+PPM requires both analog V3P3A and digital V3P3D, operating at 3.0-3.6 V.",
    "maxm10s": "MAX-M10S main VCC is 1.76-3.6 V. V_IO is 1.76-1.98 V with VIO_SEL grounded or 2.7-3.6 V with VIO_SEL open, and must not exceed VCC. Optional V_BCKP is 1.65-3.6 V.",
    "meloperosamm8q": "Melopero SAM-M8Q breakout requires 3.3 V main power/logic; optional VBA backup input accepts 3.3-6 V and disables the coin cell.",
    "paa5160e1": "PAA5160E1-Q needs VDD 1.8-2.1 V, VDDIO 1.8-3.3 V, and VDD_VCSEL 2.8-3.3 V; follow the three-rail power-up sequence.",
    "pasco2v01auma3": "PASCO2V01 requires VDD3.3 3.0-3.6 V and a separate IR-emitter VDD12 rail of 10.8-13.2 V in recommended operation.",
    "pygp2y": "GP2Y1014AU0F main Vcc is 4.5-5.5 V; separately connect V-LED and LED-GND with the maker RC network and prescribed LED pulse timing.",
    "pzem6l24": "Three-phase mains energy meter powered from the lines it measures, so it needs mains isolation and clearances; check the maker's AC limits. Its UART/RS485 side runs at 3.3 V internally and accepts an optional 3-5.5 V interface supply.",
    "qmi8658a": "QMI8658A needs main VDD and separate VDDIO, each 1.71-3.6 V.",
    "rn8209d": "RN8209D requires analog AVDD and digital DVDD, both within the maker normal application range 3-5.5 V; follow nominal-voltage variation and decoupling requirements.",
    "rv3032": "RV-3032 keeps time down to 1.3 V, but its I2C interface needs VDD >= 1.4 V at 100 kHz and >= 2.0 V at 400 kHz.",
    "sd3031": "SD3031 main VDD is 2.7-5.5 V; the separate backup-battery VBAT input is 2.3-3.6 V.",
    "si1142": "Main VDD is 1.71-3.6 V. External IR LEDs need a suitable pulsed-current rail; maker recommends VLED from VDD to 4.3 V for nominal 1.0 V LED forward drop.",
    "st1vafe3bx": "ST1VAFE3BX needs VDD 1.62-3.6 V; VDDIO is 1.62-3.6 V for I2C/SPI or 1.08-3.6 V for I3C.",
    "tcs3448": "TCS3448 VDD is 1.7-1.98 V; I2C bus pullup supply is 1.08-1.32 V or 1.62-1.98 V depending on the startup-selected mode; 3.3 V pullups are unsuitable.",
    "tel0171": "TEL0171 uses 3.3-5 V through the Gravity interface; the 4G board requires a separate Type-C power supply.",
    "tmf8806": "VDD/VDDC/VDDV require 2.7-3.5 V. I2C host/pull-ups use 1.2 V or 1.8-3.3 V, selected by GPIO0 during startup.",
    "tmf8829": "Main VDD/VDDC/VDDV need 3.1-3.5 V for full performance. Separate VDDD is 1.65-3.5 V (1.8 V preferred); VIO options are 1.1-1.3 V, 1.65-1.95 V or 2.7-3.5 V.",
    "tsl2585": "Main VDD is 1.7-1.98 V; digital I/O supply/pull-up voltage is separately 1.62-3.3 V.",
    "um980": "UM980 uses main VCC 3.0-3.6 V, optional backup V_BCKP, and separate antenna bias. The maker does not recommend VCC_RF as the antenna-bias source.",
    "vcnl4030x01": "Main VDD is 2.5-3.6 V; separately wire the IR emitter anode supply per the application circuit. I2C pull-ups support 1.8-5.5 V.",
    "zedf9k": "ZED-F9K main VCC is 2.7-3.6 V; USB requires separate V_USB 3.0-3.6 V when used; optional backup V_BCKP is 1.65-3.6 V.",
    "zedf9p": "ZED-F9P main VCC is 2.7-3.6 V; USB requires separate V_USB 3.0-3.6 V when used; optional backup V_BCKP is 1.65-3.6 V.",
    "zedf9r": "ZED-F9R main VCC is 2.7-3.6 V; USB requires separate V_USB 3.0-3.6 V when used; optional backup V_BCKP is 1.65-3.6 V.",
    "zedx20p": "ZED-X20P main VCC is 2.7-3.6 V; USB requires V_USB 3.0-3.6 V when used; optional backup V_BCKP is 1.4-5.5 V.",
}
for _sid, _note in SUPPLY_RAIL_NOTES.items():
    CAPABILITY_NOTES[_sid] = {"capability_note": _note}

# Query-time measure expansions (OR logic — any match)
MEASURE_EXPANSIONS: dict[str, list[str]] = {
    "imu": ["acceleration", "gyroscope", "magnetic_field"],
}

# Query-time measure aliases (rename before searching)
# IMPORTANT: Only alias terms that DON'T exist as real measures in the DB.
# Sub-measures like pir, voc, lidar, tof, ultrasonic, radar exist in the DB
# and should NOT be aliased to their parent — that loses specificity.
MEASURE_QUERY_ALIASES: dict[str, str] = {
    "heart rate": "biometric",
    "blood oxygen": "biometric",
    "barometric": "pressure",
    "altimeter": "pressure",
    "barometer": "pressure",
    "range finder": "distance",
    "rangefinder": "distance",
    "encoder": "rotation",
    "carbon monoxide": "co",
    "compass": "magnetic_field",
    "magnetometer": "magnetic_field",
    "accelerometer": "acceleration",
    "gyro": "gyroscope",
    "lux": "light",
    "ambient light": "light",
    "thermometer": "temperature",
    "hygrometer": "humidity",
    "air quality": "gas",
    "dust": "particulate",
    "pm2.5": "particulate",
    "pm10": "particulate",
    "sonar": "ultrasonic",
}

# Protocol aliases (expand to multiple values — OR logic). The DB stores plain digital pins as
# "gpio" (54 sensors on 2026-10-16) and has no "digital" value; "gpio" used to leave itself out, so
# those sensors never matched it, and "digital" (offered in the tool description) matched nothing.
PROTOCOL_ALIASES: dict[str, list[str]] = {
    "1-wire": ["one_wire"],
    "one-wire": ["one_wire"],
    "gpio": ["gpio", "analog", "pwm", "one_wire"],
    "digital": ["gpio", "pwm", "one_wire"],
}


# Stop words filtered from FTS queries — too generic to require in AND matching.
# Includes common English stop words + conversational terms LLMs may pass.
_FTS_STOP_WORDS = frozenset({
    # English stop words
    "a", "an", "the", "and", "or", "of", "for", "with", "in", "on", "to", "is",
    "it", "by", "at", "from", "as", "be", "my", "me", "do", "no", "so", "up",
    "if", "am", "are", "was", "has", "have", "had", "not", "but", "can", "will",
    "would", "could", "should", "what", "which", "that", "this", "these", "those",
    "how", "when", "where", "who", "than", "then", "also", "just", "very", "really",
    "any", "some", "about", "like", "into", "over", "such",
    # Sensor search context words (too generic to require)
    "sensor", "sensors", "module", "modules", "board", "chip", "ic", "breakout",
    "give", "find", "show", "get", "list", "all", "best", "good", "recommend",
    "need", "want", "looking", "search", "use", "using", "used", "make", "work",
    "works", "detect", "measure", "monitor", "read", "reading",
})


def _sanitize_fts_query(query: str) -> str:
    """Wrap each term in quotes with prefix matching, AND together.

    Uses FTS5 prefix syntax ("term"*) so "BM22S" matches "BM22S2021",
    "smoke" matches "smokedetector", etc. Filters common stop words that
    would cause false negatives in AND queries.
    """
    clean = query.replace('"', '').replace("'", "")
    terms = clean.split()
    quoted = [f'"{t}"*' for t in terms if len(t) >= 2 and t.lower() not in _FTS_STOP_WORDS]
    return " AND ".join(quoted) if quoted else ""


def _resolve_measure(measure: str) -> tuple[list[str], str]:
    """Resolve a single measure string to actual measure values and mode.

    Returns:
        (measures, mode) where mode is "or" for expansions, "single" otherwise.
    """
    lower = measure.lower().strip()

    # Check expansions first (e.g., "imu" -> multiple measures with OR)
    if lower in MEASURE_EXPANSIONS:
        return MEASURE_EXPANSIONS[lower], "or"

    # Check aliases (rename)
    if lower in MEASURE_QUERY_ALIASES:
        return [MEASURE_QUERY_ALIASES[lower]], "single"

    return [lower], "single"


def search_sensors(
    conn: sqlite3.Connection,
    query: str | None = None,
    measure: str | list[str] | None = None,
    type: str | None = None,
    protocol: str | None = None,
    platform: str | None = None,
    limit: int = 15,
) -> dict[str, Any]:
    """Search sensors with FTS5 + parametric filters.

    Args:
        conn: SQLite connection
        query: Free-text search (FTS5)
        measure: Single measure or list of measures (AND if list)
        type: Sensing technology filter
        protocol: Interface protocol filter
        platform: Platform support filter
        limit: Max results

    Returns:
        {"total": N, "results": [...]}
    """
    # Validate against this catalog so new measures/protocols/platforms need no code release.
    for name, value, table, column, aliases in (
        ("platform", platform, "sensor_platforms", "platform", {}),
        ("protocol", protocol, "sensor_protocols", "protocol", PROTOCOL_ALIASES),
        ("measure", measure, "sensor_measures", "measure", {**MEASURE_QUERY_ALIASES, **MEASURE_EXPANSIONS}),
    ):
        if value is None:
            continue
        valid = sorted({row[0] for row in conn.execute(f"SELECT DISTINCT {column} FROM {table}")} | aliases.keys())
        values = value if isinstance(value, list) else [value]
        for item in values:
            if item.strip().lower() not in valid:
                return {"error": f"Unsupported value for {name}: '{item}'", "valid_values": valid, "results": [], "total": 0}

    # Build query dynamically
    select_cols = "s.id, s.name, s.manufacturer, s.type, s.voltage, s.datasheet_url, s.platform_count, s.description, s.source_tier"
    from_clause = "sensors s"
    where_clauses: list[str] = []
    params: list[Any] = []
    joins: list[str] = []

    # --- Measure filter ---
    if measure is not None:
        if isinstance(measure, str):
            # Single measure (might be expansion or alias)
            resolved, mode = _resolve_measure(measure)
            if mode == "or":
                # Expansion: OR across multiple measures
                placeholders = ", ".join("?" for _ in resolved)
                joins.append("JOIN sensor_measures sm ON sm.sensor_id = s.id")
                where_clauses.append(f"sm.measure IN ({placeholders})")
                params.extend(resolved)
            else:
                # Single resolved measure
                joins.append("JOIN sensor_measures sm ON sm.sensor_id = s.id")
                where_clauses.append("sm.measure = ?")
                params.append(resolved[0])
        elif isinstance(measure, list) and len(measure) == 1:
            # List with single item — same as single string
            resolved, mode = _resolve_measure(measure[0])
            if mode == "or":
                placeholders = ", ".join("?" for _ in resolved)
                joins.append("JOIN sensor_measures sm ON sm.sensor_id = s.id")
                where_clauses.append(f"sm.measure IN ({placeholders})")
                params.extend(resolved)
            else:
                joins.append("JOIN sensor_measures sm ON sm.sensor_id = s.id")
                where_clauses.append("sm.measure = ?")
                params.append(resolved[0])
        elif isinstance(measure, list) and len(measure) > 1:
            # Multiple measures: AND — sensor must have ALL
            resolved_all: list[str] = []
            for m in measure:
                resolved, _ = _resolve_measure(m)
                resolved_all.extend(resolved)
            resolved_all = list(dict.fromkeys(resolved_all))
            n = len(resolved_all)
            placeholders = ", ".join("?" for _ in resolved_all)
            joins.append(
                f"JOIN sensor_measures sm ON sm.sensor_id = s.id AND sm.measure IN ({placeholders})"
            )
            params.extend(resolved_all)
            # GROUP BY + HAVING to ensure ALL measures present
            # We'll handle this in the query assembly below
            where_clauses.append(f"1=1")  # placeholder — real filter is HAVING
            # Store for later
            _having_count = n

    # --- Type filter ---
    if type is not None:
        where_clauses.append("s.type = ?")
        params.append(type.lower().strip())

    # --- Protocol filter ---
    if protocol is not None:
        proto_lower = protocol.lower().strip()
        if proto_lower in PROTOCOL_ALIASES:
            expanded = PROTOCOL_ALIASES[proto_lower]
            placeholders = ", ".join("?" for _ in expanded)
            joins.append(f"JOIN sensor_protocols sp ON sp.sensor_id = s.id")
            where_clauses.append(f"sp.protocol IN ({placeholders})")
            params.extend(expanded)
        else:
            joins.append("JOIN sensor_protocols sp ON sp.sensor_id = s.id")
            where_clauses.append("sp.protocol = ?")
            params.append(proto_lower)

    # --- Platform filter ---
    if platform is not None:
        joins.append("JOIN sensor_platforms spl ON spl.sensor_id = s.id")
        where_clauses.append("spl.platform = ?")
        params.append(platform.lower().strip())

    # --- FTS5 query + ID prefix fallback + alias resolution ---
    no_terms_note = None
    if query is not None:
        fts_query = _sanitize_fts_query(query)
        if not fts_query and query.strip():
            # "é", "a", "-": nothing to search for, so only the filters apply. Say so, as
            # board_search does, instead of returning the filtered catalog as if it matched.
            no_terms_note = (f"query '{query.strip()[:60]}' has no searchable words (stop words, single "
                             "letters or symbols); results are filtered only by measure, type, protocol "
                             "and platform")
        if fts_query:
            # Normalize query to an ID-like form for LIKE + alias lookups
            normalized = re.sub(r"[^a-z0-9]", "", query.lower())
            id_pattern = "%" + normalized + "%"

            # Resolve IC aliases (e.g., "SHT31" → "sht3x")
            alias_target = _IC_ALIASES.get(normalized)

            if not normalized:
                # No ASCII letters or digits ("温度"): an ID pattern of "%%" matched every
                # sensor, so only the text index can match.
                where_clauses.append("s.id IN (SELECT id FROM sensors_fts WHERE sensors_fts MATCH ?)")
                params.append(fts_query)
            elif alias_target:
                where_clauses.append(
                    "(s.id IN (SELECT id FROM sensors_fts WHERE sensors_fts MATCH ?) OR s.id LIKE ? OR s.id = ?)"
                )
                params.append(fts_query)
                params.append(id_pattern)
                params.append(alias_target)
            else:
                where_clauses.append(
                    "(s.id IN (SELECT id FROM sensors_fts WHERE sensors_fts MATCH ?) OR s.id LIKE ?)"
                )
                params.append(fts_query)
                params.append(id_pattern)

    # Assemble SQL
    join_sql = "\n    ".join(joins)
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Exact-match boost: when a query is provided, sensors whose ID matches
    # the normalized query (or its alias target) sort first.
    # e.g., searching "DHT22" puts dht22 above dht11 even if dht11 has more platforms.
    order_boost = ""
    order_boost_params: list[Any] = []
    if query is not None:
        normalized = re.sub(r"[^a-z0-9]", "", query.lower())
        alias_target = _IC_ALIASES.get(normalized)
        if alias_target:
            order_boost = "CASE WHEN s.id = ? OR s.id = ? THEN 0 ELSE 1 END, "
            order_boost_params = [normalized, alias_target]
        elif normalized:
            order_boost = "CASE WHEN s.id = ? THEN 0 ELSE 1 END, "
            order_boost_params = [normalized]

    order_by = f"ORDER BY {order_boost}s.platform_count DESC, s.name ASC"

    # Check if we need GROUP BY for multi-measure AND
    need_group_by = (
        isinstance(measure, list) and len(measure) > 1
    )

    if need_group_by:
        count_sql = f"""
            SELECT COUNT(*) FROM (
                SELECT s.id
                FROM {from_clause}
                {join_sql}
                WHERE {where_sql}
                GROUP BY s.id
                HAVING COUNT(DISTINCT sm.measure) = ?
            )
        """
        count_params = params + [_having_count]

        data_sql = f"""
            SELECT {select_cols}
            FROM {from_clause}
            {join_sql}
            WHERE {where_sql}
            GROUP BY s.id
            HAVING COUNT(DISTINCT sm.measure) = ?
            {order_by}
            LIMIT ?
        """
        data_params = params + [_having_count] + order_boost_params + [limit]
    else:
        count_sql = f"""
            SELECT COUNT(DISTINCT s.id)
            FROM {from_clause}
            {join_sql}
            WHERE {where_sql}
        """
        count_params = params

        data_sql = f"""
            SELECT DISTINCT {select_cols}
            FROM {from_clause}
            {join_sql}
            WHERE {where_sql}
            {order_by}
            LIMIT ?
        """
        data_params = params + order_boost_params + [limit]

    # Execute count
    total = conn.execute(count_sql, count_params).fetchone()[0]

    # Execute data query
    rows = conn.execute(data_sql, data_params).fetchall()

    # Build results with junction table data
    results = []
    for row in rows:
        sensor_id = row[0]

        measures = [r[0] for r in conn.execute(
            "SELECT measure FROM sensor_measures WHERE sensor_id = ? ORDER BY measure", (sensor_id,)
        )]
        protocols = [r[0] for r in conn.execute(
            "SELECT protocol FROM sensor_protocols WHERE sensor_id = ? ORDER BY protocol", (sensor_id,)
        )]
        platforms = [r[0] for r in conn.execute(
            "SELECT platform FROM sensor_platforms WHERE sensor_id = ? ORDER BY platform", (sensor_id,)
        )]
        urls = [r[0] for r in conn.execute(
            "SELECT url FROM sensor_urls WHERE sensor_id = ? ORDER BY url", (sensor_id,)
        )]

        results.append({
            "id": row[0],
            "name": row[1],
            "manufacturer": row[2],
            "type": row[3],
            "voltage": row[4],
            "datasheet_url": row[5],
            "platform_count": row[6],
            "description": row[7],
            "source_tier": row[8],
            "measures": measures,
            "protocols": protocols,
            "platforms": platforms,
            "urls": urls,
        })

    for result in results:
        if extra := CAPABILITY_NOTES.get(result["id"]):
            result.update(copy.deepcopy(extra))
    reply = {"total": total, "results": results}
    if no_terms_note:
        reply["note"] = no_terms_note
    return reply
