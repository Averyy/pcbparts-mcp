#!/usr/bin/env python3
"""Parse reference board schematics into structured YAML.

Shared infrastructure: data model, CLI, BOARDS.md parser, value/footprint
normalization, YAML output, repo cloning. Format-specific parsers live in
scripts/parsers/ (eagle.py, kicad.py, etc.).

Usage:
    python scripts/parse_boards.py --board sparkfun-bme280 --verbose
    python scripts/parse_boards.py --list
    python scripts/parse_boards.py --board sparkfun-bme280 --dry-run
"""

from __future__ import annotations

import argparse
import logging
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Ensure scripts/ is on sys.path so parsers/ and board_overrides can be imported
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

try:
    import yaml
except ImportError:
    print("PyYAML required: uv pip install pyyaml", file=sys.stderr)
    sys.exit(1)

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
BOARDS_MD = ROOT / "data" / "boards" / "BOARDS.md"
CACHE_DIR = ROOT / ".cache" / "repos"
OUTPUT_DIR = ROOT / "data" / "boards"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Component:
    ref: str
    value: str
    footprint: str
    package: str = ""       # raw package name before normalization
    attributes: dict[str, str] = field(default_factory=dict)  # PROD_ID, MPN, specs, etc.


@dataclass
class Net:
    name: str
    pins: list[str] = field(default_factory=list)  # ["R1.1", "U1.VCC"]
    net_class: str = ""  # routing class name (e.g. "power", "RF")
    trace_width: str = ""  # class-specific trace width (e.g. "0.3048")


@dataclass
class Position:
    ref: str
    x: float
    y: float
    rotation: float = 0.0
    side: str = ""  # "front" or "back" (empty = unknown/front)


@dataclass
class BoardOutline:
    width: float   # mm
    height: float  # mm


@dataclass
class DesignRules:
    layers: int = 2            # copper layer count
    min_trace: str = ""        # minimum trace width (e.g. "8mil")
    min_clearance: str = ""    # minimum trace-to-trace clearance
    min_drill: str = ""        # minimum drill size
    min_via: str = ""          # minimum via outer diameter


@dataclass
class CopperPour:
    net: str               # net name (e.g. "GND", "+3V3")
    layers: list[str]      # copper layers (e.g. ["F.Cu", "B.Cu"])
    keepout: bool = False  # true if this is a keepout zone


@dataclass
class BoardData:
    name: str
    slug: str
    source: str  # org/repo
    format: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    key_ics: list[str] = field(default_factory=list)
    components: list[Component] = field(default_factory=list)
    nets: list[Net] = field(default_factory=list)
    positions: list[Position] = field(default_factory=list)
    outline: BoardOutline | None = None
    design_rules: DesignRules | None = None
    copper_pours: list[CopperPour] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    """Convert board name to URL-friendly slug."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ---------------------------------------------------------------------------
# BOARDS.md parser
# ---------------------------------------------------------------------------

def parse_boards_md(path: Path | None = None) -> dict[str, dict]:
    """Parse BOARDS.md table into {slug: {name, org, repo, format, schematic_path, key_coverage}}."""
    path = path or BOARDS_MD
    boards: dict[str, dict] = {}
    in_table = False

    for line in path.read_text().splitlines():
        line = line.strip()
        # Detect table rows (skip header separator)
        if line.startswith("|") and not line.startswith("|---"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) < 6:
                continue
            name, org, repo_raw, fmt, sch_path, key_coverage = (
                cells[0], cells[1], cells[2], cells[3], cells[4], cells[5]
            )
            # Skip header row
            if name == "Board":
                in_table = True
                continue
            if not in_table:
                continue

            # Clean repo field: strip backticks
            repo = repo_raw.strip("`")
            # Clean schematic path: remove backticks, remove size/sheet annotations
            sch_path_clean = sch_path.replace("`", "")
            sch_path_clean = re.sub(r"\s*\(.*?\)\s*$", "", sch_path_clean).strip()

            slug = slugify(name)
            boards[slug] = {
                "name": name,
                "org": org,
                "repo": repo,
                "format": fmt,
                "schematic_path": sch_path_clean,
                "key_coverage": key_coverage,
            }

    return boards


# ---------------------------------------------------------------------------
# Key coverage → description, tags, key_ics
# ---------------------------------------------------------------------------

# Tag derivation rules: keyword patterns → tag name
_TAG_RULES: dict[str, list[str]] = {
    "battery-charging": ["charger", "charging", "lipo", "li-ion", "battery charger",
                         "MCP73831", "BQ24210", "BQ24295", "TP4056", "CN3791"],
    "battery-management": ["BMS", "cell balancing", "battery monitor", "fuel gauge",
                           "LTC6813", "LTC6811", "MAX17048", "BQ27441", "LC709203"],
    "usb-pd": ["USB-C PD", "USB PD", "power delivery", "STUSB4500", "CYPD3177",
               "HUSB238", "PD sink", "PD source"],
    "lora": ["LoRa", "SX1262", "SX1276", "SX1280", "RFM95", "RFM96", "LR1121"],
    "can-bus": ["CAN bus", "CAN transceiver", "CAN FD", "CAN controller",
                "MCP2515", "MCP2518", "MCP25625", "MCP2551", "MCP2558",
                "TJA1050", "TCAN", "SN65HVD", "PESD1CAN"],
    "rs485": ["RS-485", "RS485"],
    "rs232": ["RS-232", "RS232", "MAX3232"],
    "wifi": ["WiFi", "Wi-Fi", "ATWINC", "ESP8266"],
    "bluetooth": [" BLE ", "Bluetooth", "BLE,", "BLE5"],
    "zigbee-thread": ["Zigbee", "Thread", "CC2652", "CC1352"],
    "gps-gnss": ["GPS", "GNSS", "u-blox", "RTK", "L86", "NEO-F10", "PA1616",
                 "ZED-F9", "MAX-M10"],
    "motor-control": ["motor", "BLDC", "FOC", "stepper", " ESC", "DRV83", "TMC2",
                      "A4988", "TB6612", "H-bridge"],
    "power-supply": ["buck", "boost", "LDO", " regulator", "DC-DC", "SMPS",
                     "TPS6", "LMR1", "AP2112", "MIC5504", "RT9080"],
    "sensors": ["sensor", " IMU", "BME280", "BMP280", "BME680", "accelerometer",
                "gyroscope", "barometer", "thermocouple", "RTD",
                "temperature", "humidity", "pressure sensor", "spectral",
                "time-of-flight", "ToF ", "gesture", "proximity"],
    "display": ["OLED", "TFT", "LCD", "e-Paper", "e-ink", "LED matrix",
                "SSD1306", "ILI9341", "charlieplex"],
    "audio": ["audio", "codec", " DAC ", "I2S", "Class D", "amplifier",
              "WM8960", "MAX98357", "TLV320"],
    "rf-sdr": ["SDR", "RF front-end", "RF frontend", "RF board",
               "RFFC5072", "MAX2837", "MAX5864", "FMCW", "radar", "ADS-B",
               "Doppler", "balun", "10.525 GHz", "HB100"],
    "fpga": ["FPGA", "iCE40", "ECP5", "Lattice"],
    "level-shifting": ["level shift", "BSS138", "TXB0108", "TXS0102",
                       "74LVC", "74HC4050"],
    "esd-protection": ["ESD", "TVS diode", "PESD", "TPD4E"],
    "isolation": ["isolated", "galvanic", "optocoupler", "ADuM", "isoSPI"],
    "current-sensing": ["current sense", "current sensor", "current monitor",
                        "INA219", "INA228", "INA260", "ACS712", "shunt"],
    "nfc-rfid": ["NFC", "RFID", "PN532", "ST25DV", "ISO 14443",
                 "contactless", "smartcard"],
    "ethernet": ["Ethernet", "LAN8720", "W5500", "PoE", "RJ45"],
    "energy-harvesting": ["energy harvest", "BQ25570", "solar input", "MPPT"],
    "3d-printer": ["3D printer", "stepper driver", "heated bed",
                   "TMC2660", "print controller"],
    "drone-uav": ["flight controller", "drone", "quadcopter", "ESC ",
                  "autopilot", "PX4"],
    "keyboard": ["keyboard", "Cherry MX", "QMK", "macro pad", "split keyboard"],
    "usb": ["USB hub", "USB host", "FT2232", "CH340", "USB-UART", "FTDI"],
    "haptic": ["haptic", "DRV2605"],
    "led-driver": ["LED driver", "NeoPixel", "WS2812", "SK6812",
                   "constant-current", "IS31FL"],
    "security": ["fault injection", "EMFI", "glitch", "pentest",
                 "emulator", "sniff"],
    "ham-radio": ["ham radio", "SDR receiver", "transmitter", "QSD", "QSE"],
    "eurorack": ["eurorack", "synth voice", "VCO", "VCF", "VCA", "envelope",
                 "analog synth"],
    "inverter": ["inverter", "3-phase", "gate driver"],
    "robotics": ["robot", "ROV", "underwater", "thruster"],
    "adc-dac": ["ADC", " DAC", "ADS1115", "ADS1262", "MCP4725", "NAU7802",
                "ADS1015", "HX711"],
    "relay": ["relay", "relay driver"],
    "sub-ghz": ["Sub-GHz", "sub-GHz", "433MHz", "868MHz", "915MHz",
                "RFM69", "CC1111", "M-Bus"],
    "rtc": ["real-time clock", "RTC", "RV-8803", "DS3231"],
    "power-protection": ["protection IC", "over-charge", "over-discharge",
                         "crowbar", "OVP"],
    "automotive": ["LIN bus", "automotive", "LIN transceiver"],
    "pwm-servo": ["PWM driver", "servo", "PCA9685"],
    "energy-monitoring": ["energy meter", "energy monitoring", "CT channel",
                          "metering", "ATM90E"],
    "data-logging": ["data logger", "logging", "OpenLog"],
    "signal-conditioning": ["op-amp", "signal conditioning", "555 timer",
                           "Wheatstone", "comparator"],
    "video": ["HDMI", "MIPI", "DSI", " DVI", "GPDI"],
    "sbc": [" SBC", "single board computer", "SiP", "Linux SBC"],
    "debug-tool": ["bus tool", "bus pirate", "interface explorer",
                   "logic analyzer", "programmer", "GreatFET"],
    "power-distribution": ["power distribution", "power board"],
    "pressure-sensor": ["barometric", "pressure ("],
    "ham-radio-rf": ["sampling detector", "quadrature", "transmitter board",
                     "receiver board", "wideband LNA"],
}


def extract_tags(key_coverage: str) -> list[str]:
    """Derive subsystem tags from BOARDS.md Key Coverage text."""
    tags: list[str] = []
    for tag, keywords in _TAG_RULES.items():
        for kw in keywords:
            if kw.lower() in key_coverage.lower():
                tags.append(tag)
                break
    return sorted(tags)


def extract_key_ics(key_coverage: str) -> list[str]:
    """Extract notable IC/module names from Key Coverage text.

    Looks for IC names in parentheses like (BQ24210) or (ESP32-S3-MINI-1),
    and standalone IC name patterns.
    """
    ics: list[str] = []
    seen: set[str] = set()

    # Words that look like IC names but aren't
    _SKIP = {"GPIO", "UART", "MEMS", "CERN", "OSHWA", "RISC", "OLED",
             "HDMI", "TRRS", "PMOD", "JTAG", "SPI", "I2C", "USB",
             "LED", "RGB", "PWM", "ADC", "DAC", "DVI", "CAN",
             "PLL", "VCO", "LNA", "ISM", "SAW", "EMI", "ESD",
             "TVS", "LDO", "BOM", "PCB", "SMD", "QFN", "DIP",
             "SOT", "NFC", "PoE", "PPS", "ESC", "RTK", "FOC",
             "OVP", "DMX", "VOC", "GPL", "CERN"}

    def _add_ic(ic: str):
        base = re.sub(r"[-_].*", "", ic)  # BQ24210DQCT → BQ24210DQCT (no dash)
        if len(base) < 3 or base.upper() in _SKIP:
            return
        if base not in seen:
            ics.append(ic)
            seen.add(base)

    # Pattern 1: IC names in parentheses — "(BQ24210)", "(ESP32-S3-MINI-1)"
    for m in re.finditer(r"\(([A-Z][A-Z0-9][\w.-]{2,})\)", key_coverage):
        _add_ic(m.group(1))

    # Pattern 2: well-known IC families / alphanumeric part numbers not in parens
    _IC_PATTERNS = [
        r"\bESP32[-\w]*",
        r"\bRP2040\b", r"\bRP2350\w*",
        r"\bSTM32[A-Z]\d+\w*", r"\bSTM32\b",
        r"\bnRF52\d+\w*",
        r"\bATmega\d+\w*", r"\bATSAMD\d+\w*",
        r"\bCC[12]\d{3}\w*", r"\bLPC\d{4}\w*",
        # TI power/analog: BQ, TPS, TLV, INA, DRV, LM
        r"\bBQ\d{4,}\w*", r"\bTPS\d{4,}\w*", r"\bINA\d{3}\w*",
        r"\bDRV\d{4}\w*", r"\bLMR?\d{4,}\w*",
        # Maxim: MAX
        r"\bMAX\d{4,}\w*",
        # Microchip: MCP, ATWINC
        r"\bMCP\d{4,}\w*", r"\bATWINC\d+\w*",
        # Analog Devices, NXP, etc.
        r"\bAD[a-z]?\d{4}\w*",
        r"\bSX1\d{3}\w*", r"\bRFM\d{2}\w*",
        r"\bSI5\d{3}\w*",
        # Common sensor/IC patterns
        r"\bBME\d{3}\w*", r"\bBNO\d{3}\w*", r"\bBMP\d{3}\w*",
        r"\bMPU\d{3,}\w*", r"\bICM[-]?\d{3,}\w*",
        r"\bSHTC\d\w*", r"\bSCD[-]?\d{2}\w*",
        # FPGA
        r"\biCE40\w*", r"\bECP5\w*", r"\bLFE5\w+",
        # USB PHY/controllers
        r"\bFT2232\w*", r"\bCH340\w*", r"\bFUSB302\w*",
        # Radio
        r"\bCC2400\b", r"\bW25Q\d+\w*",
        # TMC stepper drivers
        r"\bTMC\d{4}\w*",
        # TI CAN/RS: SN65HVD, SN65176
        r"\bSN65\w+",
        # NXP CAN: TJA1050, PESD1CAN
        r"\bTJA\d{4}\w*",
        # ADF PLL
        r"\bADF\d{4}\w*",
        # HMC RF
        r"\bHMC\d{3}\w*",
        # RF frontend ICs
        r"\bRFFC\d{4}\w*", r"\bMGA[-]?\d+\w*",
        r"\bSKY\d{4,}\w*", r"\bBGA\d{3,}\w*",
        # A4988 stepper
        r"\bA4988\w*",
        # Sensirion
        r"\bSHTR?\w?\d\w*",
        # AP regulators
        r"\bAP\d{4}\w*",
        # OSD SiP
        r"\bOSD\d{4}\w*",
        # TI PCM audio codecs
        r"\bPCM\d{4}\w*",
        # TI USB hub/mux/PHY: TUSB, TS3USB
        r"\bTUSB\d{4}\w*", r"\bTS3USB\d+\w*",
        # TI power monitor
        r"\bPAC\d{4}\w*",
        # FTDI
        r"\bFT230\w*", r"\bFT231\w*", r"\bFT260\w*",
        # Lattice/Gowin FPGAs
        r"\bGW\d[A-Z]+\w*",
        # Cypress/Infineon USB controllers
        r"\bCY7C\d+\w*",
        # Bosch sensors
        r"\bBMI\d{3}\w*",
        # NXP I2C expanders
        r"\bPCA\d{4}\w*",
        # Qorvo
        r"\bQPE\d{4}\w*",
    ]
    for pat in _IC_PATTERNS:
        for m in re.finditer(pat, key_coverage):
            _add_ic(m.group(0))

    return ics


def build_description(key_coverage: str) -> str:
    """Build a concise board description from Key Coverage text.

    Takes the first meaningful clause/sentence from the coverage.
    """
    if not key_coverage:
        return ""
    # Split on comma — first part is usually the best summary
    parts = key_coverage.split(", ")
    # Take first 1-2 parts, up to ~120 chars
    desc = parts[0]
    if len(parts) > 1 and len(desc) + len(parts[1]) < 120:
        desc = f"{parts[0]}, {parts[1]}"
    # Clean up
    desc = re.sub(r"\s+", " ", desc).strip()
    return desc


# ---------------------------------------------------------------------------
# Value + footprint normalization
# ---------------------------------------------------------------------------

_SI_PREFIXES = {
    "p": 1e-12, "P": 1e-12, "n": 1e-9, "N": 1e-9,
    "u": 1e-6, "U": 1e-6, "µ": 1e-6,
    "m": 1e-3, "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9,
}


def _parse_eng_value(raw: str) -> tuple[float | None, str | None]:
    """Parse engineering notation like '4.7K', '100n', '2u2' into (value, prefix_char).

    Returns (None, None) if not parseable as a number with SI prefix.
    Handles leading dot: '.1u' → (0.1, 'u'), '.22' → (0.22, None)
    """
    raw = raw.strip()

    # Handle embedded prefix: '2u2' → 2.2µ, '4k7' → 4.7k, '1R5' → 1.5 (R=1)
    m = re.match(r"^(\d+)([pPnNuUµmkKMGR])(\d+)$", raw)
    if m:
        whole, prefix, frac = m.groups()
        value = float(f"{whole}.{frac}")
        if prefix in ("R", "Ω"):
            return value, None  # R means ×1 for resistors
        return value, prefix

    # Standard: '4.7K', '100n', '0.1u', '10', '.1u', '.22', '33P'
    m = re.match(r"^(\d*\.?\d+)\s*([pPnNuUµmkKMGR])?$", raw)
    if m:
        value = float(m.group(1))
        prefix = m.group(2)
        if prefix in ("R", "Ω"):
            return value, None
        return value, prefix

    return None, None


def _format_value(value: float, unit: str) -> str:
    """Format a value with Atopile-style units."""
    prefixes_for_unit = {
        "ohm": [("G", 1e9), ("M", 1e6), ("k", 1e3), ("", 1), ("m", 1e-3)],
        "F": [("u", 1e-6), ("n", 1e-9), ("p", 1e-12)],
        "H": [("m", 1e-3), ("u", 1e-6), ("n", 1e-9)],
    }

    # Zero is always base unit
    if value == 0:
        return f"0{unit}"

    unit_prefixes = prefixes_for_unit.get(unit, [])
    for prefix, scale in unit_prefixes:
        scaled = value / scale
        if scaled >= 1:
            if scaled == int(scaled):
                return f"{int(scaled)}{prefix}{unit}"
            else:
                return f"{scaled:g}{prefix}{unit}"

    # Use smallest prefix even if scaled < 1 (e.g. 0.5pF)
    if unit_prefixes:
        prefix, scale = unit_prefixes[-1]
        scaled = value / scale
        return f"{scaled:g}{prefix}{unit}"

    return f"{value:g}{unit}"


def _decode_eia_cap(code: str) -> str:
    """Decode 3-digit EIA capacitor code to formatted value.

    Code format: 2 significant digits + multiplier (power of 10).
    Multiplier 8 = ×0.01, 9 = ×0.1 (for sub-picofarad values).
    Result in picofarads, then formatted to best unit.
    Examples: '475' → 4.7uF, '104' → 100nF, '226' → 22uF
    """
    d1, d2, exp = int(code[0]), int(code[1]), int(code[2])
    sig = d1 * 10 + d2
    if exp == 8:
        picofarads = sig * 0.01
    elif exp == 9:
        picofarads = sig * 0.1
    else:
        picofarads = sig * (10 ** exp)
    return _format_value(picofarads * 1e-12, "F")


def _decode_mpn_value(mpn: str, ref_prefix: str) -> str | None:
    """Decode a manufacturer part number into an electrical value.

    Fallback for boards (e.g., Soldered) that put MPNs in the Value field.
    Uses EIA capacitor/inductor value encoding from Murata, Samsung, TDK, etc.
    """
    upper = mpn.upper()

    # === Capacitor MPN decoding ===
    if ref_prefix == "C":
        # Manufacturer-specific patterns for precise value extraction.

        # Murata GRM/GCM/GQM: value code after voltage code, before tolerance
        # GRM21BR71C475KE51K — value is 475, tolerance is K
        # Format: GRM + size(2) + height(1) + tempcoeff(varies) + value(3) + tolerance(1)
        # Use LAST 3-digit group followed by tolerance letter
        if re.match(r"^G[RCQ]M", upper):
            matches = list(re.finditer(r"(\d{3})[KJMGFD]", upper))
            if matches:
                return _decode_eia_cap(matches[-1].group(1))

        # Samsung CL: CL + size(2) + height(1) + value(3) + tolerance(1) + ...
        # CL10B473KO8NNNC — value at pos 4-6
        m = re.match(r"^CL\d{2}\w(\d{3})[KJMGFD]", upper)
        if m:
            return _decode_eia_cap(m.group(1))

        # Taiyo Yuden xMK: xMK + size(3) + tempcoeff(2) + voltage(1) + value(3) + tolerance(1)
        # EMK316BB7226ML-T — value at position after voltage digit
        if re.match(r"^[A-Z]MK", upper):
            matches = list(re.finditer(r"(\d{3})[KJMGFD]", upper))
            if matches:
                return _decode_eia_cap(matches[-1].group(1))

        # Nippon Chemi-Con EDK: EDK + value(3) + tolerance(1) + voltage(3) + ...
        m = re.match(r"^EDK(\d{3})[KJMGFD]", upper)
        if m:
            return _decode_eia_cap(m.group(1))

        # Nippon Chemi-Con polymer VKMD: EIA code in µF base
        # VKMD1451H221MV — "221" = 22 × 10^1 = 220µF
        m = re.search(r"(\d{3})[MKJG]V?$", upper)
        if upper.startswith("VKMD") and m:
            d1, d2, exp = int(m.group(1)[0]), int(m.group(1)[1]), int(m.group(1)[2])
            microfarads = (d1 * 10 + d2) * (10 ** exp)
            return _format_value(microfarads * 1e-6, "F")

        # Panasonic electrolytic EEEFK: EEEFK1H470P → 47µF
        # Format: EEEFK + voltage(2-3) + value(3) + tolerance
        m = re.match(r"^EEEFK\w+?(\d{3})[A-Z]$", upper)
        if m:
            d1, d2, exp = int(m.group(1)[0]), int(m.group(1)[1]), int(m.group(1)[2])
            microfarads = (d1 * 10 + d2) * (10 ** exp)
            return _format_value(microfarads * 1e-6, "F")

        # Panasonic polymer 50SVPF: 50SVPF18M → 18µF (direct µF value)
        m = re.match(r"^\d+SVPF(\d+)M$", upper)
        if m:
            microfarads = int(m.group(1))
            return _format_value(microfarads * 1e-6, "F")

    # === Resistor MPN decoding ===
    if ref_prefix == "R":
        # Current sense resistors with embedded R-as-decimal: KRL3216T4-M-R003-F-T1 → 3mohm
        # R means decimal point: R003 = 0.003Ω, R004 = 0.004Ω, R0100 = 0.0100Ω
        m = re.search(r"[-_]R(\d{3,4})[-A-Z]", upper)
        if m:
            code = m.group(1)
            ohms = float(f"0.{code}")
            if ohms > 0:
                return _format_value(ohms, "ohm")

    # === Inductor MPN decoding ===
    if ref_prefix in ("L", "FB"):
        # Bourns SRN: SRN5020TA__2R2M → 2R2 → 2.2uH
        # Murata LQH: LQH44PN4R7MP0L → 4R7 → 4.7uH
        # Taiyo Yuden NR: NR4012T2R2M → 2R2 → 2.2uH
        # YAGEO YPRH: YPRH1209-470M → 470 → 47uH
        # TDK MMZ (ferrite): MMZ1608S601ATA00 → 601 → 600ohm (@ 100MHz)

        # Look for embedded value with R as decimal point: 2R2 = 2.2, 4R7 = 4.7
        m = re.search(r"(\d+)R(\d+)", upper)
        if m:
            val = float(f"{m.group(1)}.{m.group(2)}")
            unit = "ohm" if ref_prefix == "FB" else "H"
            return _format_value(val * 1e-6, unit) if unit == "H" else _format_value(val, unit)

        # Ferrite bead: TDK MMZ series — MMZ1608S601ATA00
        #   MMZ + 4-digit size + letter + [3-digit impedance] + ...
        if upper.startswith("MMZ"):
            m = re.match(r"^MMZ\d{4}\w(\d{3})", upper)
            if m:
                d1, d2, exp = int(m.group(1)[0]), int(m.group(1)[1]), int(m.group(1)[2])
                ohms = (d1 * 10 + d2) * (10 ** exp)
                return _format_value(ohms, "ohm")

        # Bourns DR73: DR73-100-R → 10uH (3-digit code with R suffix)
        m = re.match(r"^DR\d+-(\d{3})-R$", upper)
        if m:
            d1, d2, exp = int(m.group(1)[0]), int(m.group(1)[1]), int(m.group(1)[2])
            microhenries = (d1 * 10 + d2) * (10 ** exp)
            return _format_value(microhenries * 1e-6, "H")

        # Standard 3-digit inductor code (like YPRH series): 470 = 47uH
        m = re.search(r"[-_](\d)(\d)(\d)[MKJG]", upper)
        if m:
            d1, d2, exp = int(m.group(1)), int(m.group(2)), int(m.group(3))
            microhenries = (d1 * 10 + d2) * (10 ** exp)
            return _format_value(microhenries * 1e-6, "H")

        # TDK MLZ ferrite bead: MLZ2012M150WT → 15uH (M150 = 15 × 10^0)
        m = re.match(r"^MLZ\d{4}[A-Z](\d{3})", upper)
        if m:
            d1, d2, exp = int(m.group(1)[0]), int(m.group(1)[1]), int(m.group(1)[2])
            microhenries = (d1 * 10 + d2) * (10 ** exp)
            return _format_value(microhenries * 1e-6, "H")

        # Würth WE-HCI / WE-PD: 7443551331 → last 4 digits encode value
        # 744355XYYY where YYY = value code: 1331 → 133 × 10^1 = 1330? No, 33uH per datasheet
        # Actually: last 3-4 digits, standard EIA code. 1331 → 133 * 10^1 µH = 1330µH? Wrong.
        # Verified: Würth 7443551331 = 33µH. Encoding: penultimate 2 digits + multiplier = 33*10^1? No.
        # The actual encoding varies by series. Skip complex Würth decoding for now.

    # === Fuse MPN decoding ===
    if ref_prefix in ("F", "PTC", "FUSE"):
        # Littelfuse PTC 1206L: 1206L012THR → 120mA PTC, 1206L300SLTHYR → 3A PTC
        m = re.match(r"^\d{4}L(\d{3,4})", upper)
        if m:
            code = int(m.group(1))
            amps = code / 100
            if amps >= 1:
                return f"{amps:g}A PTC"
            else:
                return f"{int(amps * 1000)}mA PTC"

        # Fuzetec FSMD: FSMD035-1206 → 350mA PTC (code = hold current in 10mA units)
        m = re.match(r"^FSMD(\d{3})", upper)
        if m:
            milliamps = int(m.group(1)) * 10
            if milliamps >= 1000:
                return f"{milliamps / 1000:g}A PTC"
            return f"{milliamps}mA PTC"

    return None


_EMPTY_DEFAULTS = {
    "TP": "test point", "H": "mounting hole", "MH": "mounting hole",
    "JP": "solder jumper", "SJ": "solder jumper",
}
_DNP_PREFIXES = {"R", "C", "L", "D", "FB", "F", "LED"}

# KiCad symbol names → human-readable
_SYMBOL_NAME_MAP = {
    "D_Schottky": "schottky",
    "D_TVS": "TVS",
    "D_Zener": "zener",
    "D_TVS_5V": "TVS 5V",
    "D_TVS_3.3V": "TVS 3.3V",
    "Filter_EMI_CommonMode": "common mode filter",
    "RotaryEncoder_Switch": "rotary encoder",
    "SPST_TACT": "tactile switch",
    "SW_Push": "tactile switch",
    "SW_Push_DPDT": "DPDT switch",
    "SW_SPST": "switch",
    "SW_SP3T": "3-position switch",
    "NMOS-DUAL": "dual NMOS",
    "S_MODE": "solder jumper",
    "USB_C_Plug_USB2.0": "USB-C",
    "SWITCH": "switch",
    "TVS_USB": "USB TVS",
    "FerriteBead": "ferrite bead",
    "Fuse": "fuse",
    "VCO": "VCO",
    "PIN": "pin diode",
    "R_Potentiometer": "potentiometer",
    "V_REG_LDO": "LDO regulator",
    "RESONATOR": "resonator",
    "Amp": "op-amp",
    "RX_AMP": "RX amplifier",
    "TX_AMP": "TX amplifier",
}
_Q_MAP = {"PMOS": "P-channel MOSFET", "NMOS": "N-channel MOSFET",
           "PNP": "PNP transistor", "NPN": "NPN transistor"}
_BARE_TRANSISTORS = {
    "NPN": "NPN transistor", "PNP": "PNP transistor",
    "NMOS": "N-channel MOSFET", "PMOS": "P-channel MOSFET",
}
_BARE_COLORS = {
    "RED": "red", "GREEN": "green", "BLUE": "blue", "YELLOW": "yellow",
    "WHITE": "white", "ORANGE": "orange", "AMBER": "amber", "PURPLE": "purple",
    "PINK": "pink", "BLU": "blue", "GRN": "green", "YEL": "yellow",
    "WHT": "white", "ORG": "orange",
}
_JST_SERIES = {"SRSS": "SH", "GHS": "GH", "SURS": "UR", "PH": "PH", "XH": "XH", "ZR": "ZR"}
_FUNCTIONAL_SUFFIXES = {"ADJ", "ADJ1", "HV", "LP", "EN"}


def normalize_value(value: str, ref: str) -> str:
    """Normalize component value to Atopile syntax.

    Resistors: 4.7K → 4.7kohm, 100 → 100ohm, 10kR → 10kohm, 5k1R → 5.1kohm
    Capacitors: 0.1u → 100nF, 100n → 100nF, 27p → 27pF
    Inductors: 2u2 → 2.2uH
    ICs/other: returned verbatim
    """
    if not ref:
        return value
    # Default values for empty-value components based on ref prefix
    if not value:
        ref_prefix = re.match(r"^([A-Za-z]+)", ref)
        rp = ref_prefix.group(1).upper() if ref_prefix else ""
        if rp in _EMPTY_DEFAULTS:
            return _EMPTY_DEFAULTS[rp]
        if rp in _DNP_PREFIXES:
            return "DNP"
        return value

    # Extract alphabetic prefix (handles C7A, R6, FB1, rC1, rR1, etc.)
    m = re.match(r"^([A-Za-z]+)", ref)
    prefix = m.group(1).upper() if m else ""

    # Strip leading lowercase 'r' prefix (split keyboard right-half convention: rC1, rR1, rL1)
    if len(prefix) >= 2 and ref[0] == "r" and ref[1].isupper():
        prefix = prefix[1:]

    # Map resistor network and thermistor prefixes
    if prefix in ("RN", "RT"):
        prefix = "R"

    # Universal cleanups (apply to all component types)
    cleaned = value.strip()
    cleaned = cleaned.replace("\\n", "")
    # Unicode normalization: μ→u, Ω→ohm, −→-
    cleaned = cleaned.replace("\u03BC", "u").replace("\u00B5", "u")  # Greek mu, micro sign
    cleaned = cleaned.replace("\u03A9", "ohm")  # Greek capital omega
    cleaned = cleaned.replace("\u2212", "-")  # Unicode minus → ASCII hyphen
    cleaned = cleaned.replace("\u2013", "-").replace("\u2014", "-")  # en/em dash
    # NA(...) pattern (Olimex boards): NA(47uF C0805) → extract inner value
    # Must run BEFORE generic paren stripping
    m_na = re.match(r"^NA\((.+)\)$", cleaned)
    if m_na:
        inner = m_na.group(1).strip()
        inner = re.sub(r"\([^)]*\)$", "", inner).strip()  # strip inner parens
        parts = inner.split()
        cleaned = parts[0] if parts else ""
    else:
        # Strip trailing parenthetical specs like (25V), (SSOP) but preserve (NC)/(NO)
        if not re.search(r"\((?:NC|NO)\)\s*$", cleaned):
            cleaned = re.sub(r"\([^)]+\)$", "", cleaned).strip()
    # Strip LaTeX-style subscripts: V_{CC} → VCC, V_{BK} → VBK
    cleaned = re.sub(r"_\{([^}]+)\}", r"\1", cleaned)
    # Strip KiCad active-low notation: ~{RESET} → nRESET
    cleaned = re.sub(r"~\{([^}]+)\}", r"n\1", cleaned)
    # KiCad escape sequences: {slash} → /
    cleaned = cleaned.replace("{slash}", "/")
    # Strip trailing ? artifact from values: DF13-4P-1.25? → DF13-4P-1.25
    cleaned = cleaned.rstrip("?")
    # Strip embedded footprint in value: 1N4148W/SOD123 → 1N4148W
    m = re.match(r"^([A-Z0-9][-A-Z0-9]+)/(?:SOD|SOT|SMA|SMB|SMC|DO)\d", cleaned, re.IGNORECASE)
    if m:
        cleaned = m.group(1)
    # Strip embedded DCR/dimensions from inductor values:
    # "1.0uH DCR=35mR 2.00x1.60x1.00mm L2016" → "1.0uH"
    # "3.3uH 8x8mm" → "3.3uH"
    cleaned = re.sub(r"\s+DCR=\S+", "", cleaned)
    cleaned = re.sub(r"\s+\d+\.?\d*x\d+\.?\d*(?:x\d+\.?\d*)?mm\b.*$", "", cleaned)
    cleaned = re.sub(r"\s+[A-Z]\d{4}$", "", cleaned)  # trailing footprint codes like " L2016"
    # Olimex crystal values: Q25MHz/18pF/30ppm/4P/3.2x2.5mm → 25MHz
    m_crystal = re.match(r"^Q(\d+\.?\d*[kM]?Hz)", cleaned, re.IGNORECASE)
    if m_crystal:
        cleaned = m_crystal.group(1)
    # Strip trailing power rating from resistor values: "1.27k 62.5mW R0402" → "1.27k"
    cleaned = re.sub(r"\s+\d+\.?\d*m?W\b.*$", "", cleaned)
    # SMD_5.2x5.2mm_h2.5mm → "switch" (footprint used as value for switches)
    if re.match(r"^SMD_\d", cleaned):
        cleaned = "switch"
    # LOGO_ / SparkFun_Logo / Ordering_Instructions → junk components
    if re.match(r"^(LOGO_|SparkFun_Logo|Ordering)", cleaned, re.IGNORECASE):
        return "logo"

    # FIDUCIAL / Fiducial_1mm → filter as junk
    if re.match(r"^FIDUCIAL", cleaned, re.IGNORECASE):
        return "FIDUCIAL"

    # oshw_logo / OSHW_* → filter as junk
    if re.match(r"^OSHW", cleaned, re.IGNORECASE):
        return "logo"

    # KiCad symbol names → human-readable for non-passives
    if cleaned in _SYMBOL_NAME_MAP:
        cleaned = _SYMBOL_NAME_MAP[cleaned]

    # Q_PMOS_GSD / Q_NMOS_GSD → proper transistor names (KiCad symbol names)
    m = re.match(r"^Q_(PMOS|NMOS|PNP|NPN)(?:_\w+)?$", cleaned, re.IGNORECASE)
    if m:
        cleaned = _Q_MAP.get(m.group(1).upper(), cleaned)

    # Bare transistor type names: NPN, NMOS, PMOS, PNP → normalize
    if cleaned.upper() in _BARE_TRANSISTORS:
        cleaned = _BARE_TRANSISTORS[cleaned.upper()]

    # WIREPAD / PAD_NxN → filter (solder pads, not real components)
    if re.match(r"^(WIREPAD|PAD[_-]\d)", cleaned, re.IGNORECASE):
        return "pad"

    # TPPAD / TPB → test point (Eagle footprint names used as values)
    if re.match(r"^(TPPAD|TPB)\d", cleaned, re.IGNORECASE):
        return "test point"

    # TestPoint / TESTPOINT / TP / TestPoint_2Pole / TEST-POINT3 → "test point"
    if cleaned.upper() in ("TESTPOINT", "TEST_POINT", "TP", "TEST POINT"):
        cleaned = "test point"
    elif re.match(r"^(TestPoint|TEST[-_]POINT)", cleaned):
        cleaned = "test point"

    # MH (mounting hole abbreviation) → "mounting hole"
    if cleaned == "MH":
        cleaned = "mounting hole"

    # STEMMA_I2C / QWIIC_RIGHT_ANGLE → Adafruit/SparkFun I2C connectors
    if re.match(r"^STEMMA", cleaned, re.IGNORECASE):
        cleaned = "STEMMA QT"
    elif re.match(r"^QWIIC", cleaned, re.IGNORECASE):
        cleaned = "Qwiic connector"

    # RF_SHIELD_FRAME → "RF shield"
    if re.match(r"^RF_SHIELD", cleaned):
        cleaned = "RF shield"

    # LDO_2V5 / LDO_3V3 etc. → "2.5V LDO"
    m = re.match(r"^LDO[_-](\d+)V(\d+)$", cleaned)
    if m:
        cleaned = f"{m.group(1)}.{m.group(2)}V LDO"

    # REFLOWABLE_BATTERY / RELOWABLE_BATTERY → "reflowable battery"
    if re.match(r"^RE?LOWABLE_BATTERY", cleaned, re.IGNORECASE):
        cleaned = "reflowable battery"

    # ANTENNA-SMA-GROUNDED → "SMA antenna"
    if re.match(r"^ANTENNA[-_]SMA", cleaned, re.IGNORECASE):
        cleaned = "SMA antenna"

    # 4P_button_sw / button_sw → "tactile switch"
    if re.match(r"^\d*P?_?button_sw$", cleaned, re.IGNORECASE):
        cleaned = "tactile switch"

    # DISP_OLED_... → "OLED display"
    if re.match(r"^DISP_OLED", cleaned):
        cleaned = "OLED display"

    # Tilde '~' means "no value" in KiCad — return early with sensible default
    if cleaned == "~":
        if re.match(r"^(SJ|JP)", ref, re.IGNORECASE):
            return "solder jumper"
        elif re.match(r"^H", ref, re.IGNORECASE):
            return "mounting hole"
        elif re.match(r"^TP", ref, re.IGNORECASE):
            return "test point"
        else:
            return ""

    # NC/nc = "No Connect" / "Do Not Populate" — normalize and return early
    if cleaned.upper() == "NC":
        return "NC"

    # TP_SHORT / TP_OPEN → "test point"
    if re.match(r"^TP[_-](SHORT|OPEN)$", cleaned, re.IGNORECASE):
        cleaned = "test point"

    # TYPE-C-31-M-12, TYPEC-305-ACP16H458 and similar USB-C MPNs → "USB-C"
    if re.match(r"^TYPE[-_]?C[-_]\d", cleaned, re.IGNORECASE):
        cleaned = "USB-C"

    # USB symbol names → "USB-C", "USB-A", etc.
    if re.match(r"^USB[-_]C", cleaned):
        cleaned = "USB-C"
    elif re.match(r"^USB[-_]A", cleaned):
        cleaned = "USB-A"
    elif re.match(r"^USB[-_]B", cleaned):
        if "MICRO" in cleaned.upper():
            cleaned = "USB Micro-B"
        else:
            cleaned = "USB-B"

    # Speaker_ → "speaker"
    if re.match(r"^Speaker_", cleaned):
        cleaned = "speaker"

    # MountingHole_Pad → "mounting hole"
    if cleaned.startswith("MountingHole"):
        cleaned = "mounting hole"

    # LED naming conventions: LED_G_0603_MPN → "green LED", LED_Small → "LED"
    m = re.match(r"^LED[_-]([RGBYWO])(?:[_-]|$)", cleaned)
    if m:
        _LED_COLORS = {"R": "red", "G": "green", "B": "blue", "Y": "yellow",
                        "W": "white", "O": "orange"}
        cleaned = f"{_LED_COLORS.get(m.group(1), '')} LED".strip()
    elif re.match(r"^LED[_-](Small|PWR|RED|GREEN|BLUE|YELLOW|WHITE)$", cleaned, re.IGNORECASE):
        color = cleaned.split("_")[-1].split("-")[-1].lower()
        if color in ("small", "pwr"):
            cleaned = "LED"
        else:
            cleaned = f"{color} LED"
    elif re.match(r"^(RED|GREEN|BLUE|YELLOW|WHITE|ORANGE)[_-]LED$", cleaned, re.IGNORECASE):
        cleaned = f"{cleaned.split('_')[0].split('-')[0].lower()} LED"
    # LED_BAGR / LED_RGBA → "multicolor LED"; 0603LED_SIDE → "LED"
    # LED_0603_GN → "green LED" (Eagle library naming)
    elif re.match(r"^LED[_-]\d{4}[_-]?(GN|RD|BL|YL|WH|OR)$", cleaned, re.IGNORECASE):
        _EC = {"GN": "green", "RD": "red", "BL": "blue", "YL": "yellow", "WH": "white", "OR": "orange"}
        c = re.search(r"(GN|RD|BL|YL|WH|OR)$", cleaned, re.IGNORECASE)
        cleaned = f"{_EC.get(c.group(1).upper(), '')} LED".strip() if c else "LED"
    elif re.match(r"^LED[_-][RGBAYWO]{2,}$", cleaned, re.IGNORECASE):
        cleaned = "multicolor LED"
    elif re.match(r"^\d{4}LED", cleaned):
        cleaned = "LED"
    # LED_<label> catch-all (LED_VIN, LED_XT30, etc.) → "LED"
    elif re.match(r"^LED_\w+$", cleaned):
        cleaned = "LED"

    # NetTie_2 / NetTie_3 → "net tie" (copper bridge between zones)
    if re.match(r"^NetTie", cleaned, re.IGNORECASE):
        cleaned = "net tie"

    # MOSFET symbol names: MOSFET-NCHANNEL, MOSFET-PCHANNEL, MOSFETSO-8, etc.
    m = re.match(r"^MOSFET[-_]?(N[-_]?CH|P[-_]?CH|NCHANNEL|PCHANNEL)?", cleaned, re.IGNORECASE)
    if m and m.group(0) == cleaned[:len(m.group(0))]:
        ch = (m.group(1) or "").upper()
        if "N" in ch:
            cleaned = "N-channel MOSFET"
        elif "P" in ch:
            cleaned = "P-channel MOSFET"
        else:
            cleaned = "MOSFET"

    # Transistor symbol names: Q_PNP_BEC, Q_NPN_ECB, etc.
    m = re.match(r"^Q_(PNP|NPN)", cleaned, re.IGNORECASE)
    if m:
        cleaned = f"{m.group(1).upper()} transistor"

    # Dual transistor symbol names: TRANS_PNP_DUAL, TRANS_NPN_DUAL
    m = re.match(r"^TRANS_(PNP|NPN)_DUAL$", cleaned, re.IGNORECASE)
    if m:
        cleaned = f"dual {m.group(1).upper()} transistor"

    # MOMENTARY-SWITCH-SPST*, SWITCH-SPDT, SWITCH-DPDT, SWITCH_SPST_4_PIN, SWITCH_SP3T_SMD
    if re.match(r"^MOMENTARY[-_]SWITCH", cleaned, re.IGNORECASE):
        cleaned = "tactile switch"
    elif re.match(r"^SWITCH[-_]DPDT", cleaned, re.IGNORECASE):
        cleaned = "DPDT switch"
    elif re.match(r"^SWITCH[-_]SPDT", cleaned, re.IGNORECASE):
        cleaned = "SPDT switch"
    elif re.match(r"^SWITCH[-_]SP3T", cleaned, re.IGNORECASE):
        cleaned = "3-position switch"
    elif re.match(r"^SWITCH[-_]SPST", cleaned, re.IGNORECASE):
        cleaned = "tactile switch"

    # RELAY-SPDT, RELAY-DPDT → "SPDT relay", "DPDT relay"
    m = re.match(r"^RELAY[-_](SPDT|DPDT|SPST)$", cleaned, re.IGNORECASE)
    if m:
        cleaned = f"{m.group(1).upper()} relay"

    # Spring/pogo contacts: SPRING_CONTACT → "spring contact"
    if re.match(r"^SPRING[-_]CONTACT", cleaned, re.IGNORECASE):
        cleaned = "spring contact"

    # Battery_Cell → "coin cell holder"
    if cleaned == "Battery_Cell":
        cleaned = "coin cell holder"

    # LOWPASS_FILTER, HIGHPASS_FILTER, BANDPASS_FILTER → human names
    _FILTER_MAP = {
        "LOWPASS_FILTER": "lowpass filter", "HIGHPASS_FILTER": "highpass filter",
        "BANDPASS_FILTER": "bandpass filter",
    }
    if cleaned.upper() in _FILTER_MAP:
        cleaned = _FILTER_MAP[cleaned.upper()]

    # SHIELD_GND → "shield ground"
    if cleaned == "SHIELD_GND":
        cleaned = "shield ground"

    # TO220_HEATSINK → "heatsink"
    if re.match(r"^TO\d+_HEATSINK", cleaned, re.IGNORECASE):
        cleaned = "heatsink"

    # CORTEX_JTAG / ARM_JTAG_HEADER → "JTAG"
    if re.match(r"^CORTEX[-_]JTAG", cleaned, re.IGNORECASE):
        cleaned = "JTAG"

    # MICRO_USB_5P → "USB Micro-B"
    if re.match(r"^MICRO[-_]USB", cleaned, re.IGNORECASE):
        cleaned = "USB Micro-B"

    # CR1220_HOLDER, CR2032_HOLDER → "CR1220 battery holder" etc.
    m = re.match(r"^(CR\d+)[-_]HOLDER$", cleaned, re.IGNORECASE)
    if m:
        cleaned = f"{m.group(1).upper()} battery holder"

    # PJ301_THONKICONN*, THONKICONN → "3.5mm audio jack" (eurorack convention)
    if re.match(r"^(PJ301|THONKICONN)", cleaned, re.IGNORECASE):
        cleaned = "3.5mm audio jack"

    # JST connector MPNs: SM04B-SRSS-TB → "JST SH 4-pin", BM02B-SRSS-TBT → "JST SH 2-pin"
    # SM07B-GHS-TB → "JST GH 7-pin", S3B-PH-SM4-TB → "JST PH 3-pin"
    m = re.match(r"^[BS]M?(\d{2})B-([A-Z]{2,4})", cleaned)
    if m:
        pins = int(m.group(1))
        series_code = m.group(2)
        series = _JST_SERIES.get(series_code)
        if series:
            cleaned = f"JST {series} {pins}-pin"
    # S2B-PH-SM4-TB, S3B-PH-SM4-TB, S6B-ZR-SM4A-TF etc.
    if not re.match(r"^JST", cleaned):
        m = re.match(r"^S(\d+)B-([A-Z]{2})", cleaned)
        if m:
            pins = int(m.group(1))
            series_code = m.group(2)
            series = _JST_SERIES.get(series_code)
            if series:
                cleaned = f"JST {series} {pins}-pin"

    # Rotary encoder MPNs: PEC11J-*, PEC12R-* → "rotary encoder"
    if re.match(r"^PEC\d+[A-Z]?[-_]", cleaned, re.IGNORECASE):
        cleaned = "rotary encoder"

    # WE-CBF_0603, WE-CBF → "ferrite bead" (Würth CBF series)
    # Also bare "Ferrite" / "FERRITE" → "ferrite bead"
    if re.match(r"^WE[-_]CBF", cleaned, re.IGNORECASE):
        cleaned = "ferrite bead"
    elif cleaned.upper() == "FERRITE":
        cleaned = "ferrite bead"

    # Polyfuse → "PTC fuse"
    if cleaned.upper() == "POLYFUSE":
        cleaned = "PTC fuse"

    # Conn_Coaxial → "coaxial connector"
    if cleaned == "Conn_Coaxial":
        cleaned = "coaxial connector"

    # U.FL → preserve (antenna connector name)
    # Conn_01x01_Pin → "1-pin header" (KiCad auto-name)
    m = re.match(r"^Conn_(\d+)x(\d+)(?:_Pin|_Socket)?$", cleaned)
    if m:
        cleaned = f"{int(m.group(1))}x{int(m.group(2))} header"

    # FLASH-SPI / SPI-FLASH → "SPI flash"
    if re.match(r"^(FLASH[-_]SPI|SPI[-_]FLASH)$", cleaned, re.IGNORECASE):
        cleaned = "SPI flash"

    # BALUN_MPN → "balun"
    if re.match(r"^BALUN[-_]", cleaned, re.IGNORECASE):
        cleaned = "balun"

    # GENERIC-SOIC8, GENERIC_QFN → strip GENERIC prefix (footprint used as value)
    if re.match(r"^GENERIC[-_](SOIC|QFN|SOT|TSSOP|DIP)", cleaned, re.IGNORECASE):
        cleaned = re.sub(r"^GENERIC[-_]", "", cleaned)

    # TC2030_SWD → "Tag-Connect SWD" (debug connector)
    if re.match(r"^TC2030", cleaned, re.IGNORECASE):
        cleaned = "Tag-Connect SWD"

    # ARTEMIS_MODULE → "Artemis module"
    if cleaned.upper() == "ARTEMIS_MODULE":
        cleaned = "Artemis module"

    # SENSOR-PD* → "photodiode" (light sensor)
    if re.match(r"^SENSOR[-_]PD\d", cleaned, re.IGNORECASE):
        cleaned = "photodiode"

    # Ref-based opaque MPN normalization
    # Buzzer refs (BUZ, LS, SP): opaque MPNs → "buzzer"
    if prefix in ("BUZ", "LS") and re.match(r"^[A-Z][A-Z0-9]{4,}[-_]", cleaned):
        cleaned = "buzzer"
    # Microphone refs (MIC): opaque MPNs → "MEMS microphone"
    if prefix == "MIC" and re.match(r"^[A-Z]\d{4}", cleaned):
        cleaned = "MEMS microphone"

    # RJ45 MagJack MPNs: RJLBC-060TC1 → "RJ45"
    if re.match(r"^RJLBC", cleaned, re.IGNORECASE):
        cleaned = "RJ45"

    # USB-B connector MPNs: USBB1-FRWH-4A → "USB-B"
    if re.match(r"^USBB\d", cleaned, re.IGNORECASE):
        cleaned = "USB-B"

    # MicroSD socket MPNs: HYC77-TF09-200 → "microSD socket"
    if re.match(r"^HYC\d+[-_]TF", cleaned, re.IGNORECASE):
        cleaned = "microSD socket"

    # FFC/FPC connector MPNs: SFV33R-... → "33-pin FFC", AFA07-S15FCC → "15-pin FFC"
    m = re.match(r"^SFV(\d+)R", cleaned)
    if m:
        cleaned = f"{m.group(1)}-pin FFC"
    m = re.match(r"^AFA\d+-S(\d+)FCC", cleaned)
    if m:
        cleaned = f"{m.group(1)}-pin FFC"

    # MTA connector: MTA02-100 → "1x2 MTA-100"
    m = re.match(r"^MTA(\d+)-100$", cleaned)
    if m:
        cleaned = f"1x{int(m.group(1))} MTA-100"

    # ZL303-NNP terminal blocks: ZL303-03P → "1x3 header"
    m = re.match(r"^ZL\d+-(\d+)P$", cleaned)
    if m:
        cleaned = f"1x{int(m.group(1))} header"

    # PKS micro HDMI: PKS019-4011-0 → "micro HDMI"
    if re.match(r"^PKS\d+-\d+", cleaned):
        cleaned = "micro HDMI"

    # Crystal with embedded frequency in MPN: NX3225SA-12MHZ-STD-CSR-3 → "12MHz"
    m = re.search(r"(\d+\.?\d*)\s*MHZ", cleaned, re.IGNORECASE)
    if m and prefix in ("Y", "X") and re.match(r"^[A-Z]{2}\d{4}", cleaned):
        cleaned = f"{m.group(1)}MHz"

    # Rechargeable backup battery: ML414H-IV01E → "rechargeable battery"
    if re.match(r"^ML\d{3}H", cleaned) and prefix == "C":
        cleaned = "rechargeable battery"

    # Common mode choke MPNs (on L refs): ACT45B-510-2P-TL003, PCAQ4520MB-142
    if prefix == "L" and re.match(r"^(ACT\d+|PCAQ\d+)", cleaned):
        cleaned = "common mode choke"

    # LENSMOUNT_M12 → "M12 lens mount"
    m = re.match(r"^LENSMOUNT[-_](M\d+)$", cleaned, re.IGNORECASE)
    if m:
        cleaned = f"{m.group(1)} lens mount"

    # HEADER_NP / HEADER_16P → extract pin count
    m = re.match(r"^HEADER[-_](\d+)P$", cleaned, re.IGNORECASE)
    if m:
        cleaned = f"1x{m.group(1)} header"

    # CON2P_SMT, CON_2P → "2-pin connector"
    m = re.match(r"^CON[-_]?(\d+)P", cleaned, re.IGNORECASE)
    if m:
        cleaned = f"{m.group(1)}-pin connector"

    # CP210X_USB_UART → "CP210x USB-UART"
    if re.match(r"^CP210X", cleaned, re.IGNORECASE):
        cleaned = "CP210x USB-UART"

    # WS2812B_3535FULL / WS2812B_SK6805_1515 → strip package suffix
    # Keep the actual LED part name, not the package variant
    m = re.match(r"^(WS2812\w?)[-_]", cleaned, re.IGNORECASE)
    if m:
        cleaned = m.group(1)
    elif re.match(r"^(SK68\d+\w?)[-_]", cleaned, re.IGNORECASE):
        m2 = re.match(r"^(SK68\d+\w?)[-_]", cleaned, re.IGNORECASE)
        if m2:
            cleaned = m2.group(1)

    # MOUNT-HOLE → "mounting hole"
    if re.match(r"^MOUNT[-_]HOLE", cleaned, re.IGNORECASE):
        cleaned = "mounting hole"

    # Aux_flush → "3.5mm audio jack" (FIHDI/Eurorack convention)
    if re.match(r"^Aux[-_]flush", cleaned, re.IGNORECASE):
        cleaned = "3.5mm audio jack"

    # M4_DIODA → "diode" (Soldered Electronics convention)
    if re.match(r"^M\d_DIODA$", cleaned, re.IGNORECASE):
        cleaned = "diode"

    # DISP_LCD_* → "TFT LCD"
    if re.match(r"^DISP_LCD", cleaned):
        cleaned = "TFT LCD"

    # FEATHERWING_* → "Featherwing headers"
    if re.match(r"^FEATHERWING", cleaned, re.IGNORECASE):
        cleaned = "Featherwing headers"

    # ARM_MINI_JTAG → "ARM JTAG"
    if re.match(r"^ARM[-_](?:MINI[-_])?JTAG", cleaned, re.IGNORECASE):
        cleaned = "ARM JTAG"

    # KiCad connector symbol names
    m = re.match(r"^Conn_ARM_JTAG_SWD_(\d+)$", cleaned)
    if m:
        cleaned = f"SWD {m.group(1)}-pin"
    # Conn_01x02, Conn_01x03_Male, Conn_02x02_Top_Bottom → "1x2 header" etc.
    m = re.match(r"^Conn_(\d+)x(\d+)", cleaned)
    if m:
        cleaned = f"{int(m.group(1))}x{int(m.group(2))} header"
    # Screw_Terminal_01x02 → "1x2 screw terminal"
    m = re.match(r"^Screw_Terminal_(\d+)x(\d+)$", cleaned)
    if m:
        cleaned = f"{int(m.group(1))}x{int(m.group(2))} screw terminal"

    # Spacer_Drill3.7mm_H3mm_MPN → "spacer"
    if cleaned.startswith("Spacer_"):
        cleaned = "spacer"

    # Mounting_hole_* / HOLE_3.2mm → "mounting hole"
    if re.match(r"^Mounting_hole", cleaned, re.IGNORECASE):
        cleaned = "mounting hole"
    if re.match(r"^HOLE_\d", cleaned):
        cleaned = "mounting hole"

    # HEADER_MALE_9X1 / HEADER_FEMALE_... → extract dims
    m = re.match(r"^HEADER_(?:MALE|FEMALE)[_-](\d+)X(\d+)", cleaned, re.IGNORECASE)
    if m:
        cleaned = f"{int(m.group(2))}x{int(m.group(1))} header"

    # pkl_jumper, pkl_* library prefixes → "solder jumper"
    if re.match(r"^pkl_jumper", cleaned, re.IGNORECASE):
        cleaned = "solder jumper"

    # Socket_Hirose_... → extract connector type
    if cleaned.startswith("Socket_"):
        cleaned = "connector"

    # MicroSD_MPN → "microSD"
    if cleaned.startswith("MicroSD"):
        cleaned = "microSD"

    # SW_MPN_SMD → "switch", SW_DPDT → "DPDT switch"
    if re.match(r"^SW_\w+_SMD$", cleaned):
        cleaned = "switch"
    elif re.match(r"^SW_[A-Z]", cleaned) and cleaned not in ("SW_Push", "SW_SPST", "SW_SP3T", "SW_Push_DPDT"):
        cleaned = "switch"

    # USB-C_MFR_MPN → "USB-C", USB_C_Plug_USB2.0 → "USB-C"
    if re.match(r"^USB[-_]C[-_]", cleaned):
        cleaned = "USB-C"

    # Choke_MPN → "choke"
    if cleaned.startswith("Choke_"):
        cleaned = "choke"

    # Resonator/crystal with frequency: Resonator_12MHz_ABM8G → "12MHz"
    m = re.match(r"^(?:Resonator|Crystal)[_-](\d+\.?\d*[kM]?Hz)", cleaned, re.IGNORECASE)
    if m:
        cleaned = m.group(1)

    # Battery_Holder_MPN → "battery holder"
    if re.match(r"^Battery_Holder", cleaned):
        cleaned = "battery holder"

    # Bus_RJ45_... → "RJ45", Bus_M.2_... → "M.2"
    m = re.match(r"^Bus_(RJ45|M\.2|PCI[Ee]|USB)", cleaned)
    if m:
        cleaned = m.group(1)

    # Molex/JST connector with type: Molex_Nano-Fit_1x2_... → "Molex Nano-Fit 1x2"
    m = re.match(r"^(Molex|JST|Hirose|TE|Amphenol)[_-]([A-Za-z-]+)[_-](\d+x\d+)", cleaned)
    if m:
        cleaned = f"{m.group(1)} {m.group(2)} {m.group(3)}"
    # Shorter: Molex_Nano-Fit_MPN → "Molex Nano-Fit"
    elif re.match(r"^(Molex|JST|Hirose)[_-]([A-Za-z-]+)[_-]\d", cleaned):
        m2 = re.match(r"^(Molex|JST|Hirose)[_-]([A-Za-z-]+)", cleaned)
        if m2:
            cleaned = f"{m2.group(1)} {m2.group(2)}"

    # Conn_FFC_... → "FFC connector"
    if re.match(r"^Conn_FFC", cleaned):
        cleaned = "FFC connector"

    # TERMINAL_MPN → "screw terminal"
    if re.match(r"^TERMINAL_", cleaned):
        cleaned = "screw terminal"

    # Strip trailing _package from IC values: TPD1E0B04_XDFN-2 → TPD1E0B04
    # Also: MCP23017T-E_QFN → MCP23017T-E, AP62301_TSOT → AP62301, 93AA66C_SOIC → 93AA66C
    # Also: MP4541_SOP8-EP → MP4541, PN7160A1_VFQFN → PN7160A1
    m = re.match(r"^([A-Z0-9][A-Z0-9][-A-Z0-9]*)_(XDFN|XSON|DFN|V?QFN|UQFN|UFQFN|DHVQFN|VFQFN|SOT\d*|SOIC|TSSOP|TSOT\d*|MSOP|BGA|WLCSP|SOP\d*|PASS|RGET|RGTT|DSBGA)[-_]?\d*(?:[-_]EP)?$",
                 cleaned, re.IGNORECASE)
    if m:
        cleaned = m.group(1)

    # Strip ordering/package suffixes from IC MPNs:
    # BM1366_mode1 → BM1366, 93C46B-SOT-23-6 → 93C46B
    m = re.match(r"^([A-Z0-9][A-Z0-9]+)[_-](?:mode\d|SOT[-_]?\d)", cleaned, re.IGNORECASE)
    if m:
        cleaned = m.group(1)

    # Strip IC ordering suffixes: TPS63020DSJR → TPS63020, MAX17225ELT+ → MAX17225
    # DGQ2788AEN-T1-GE4 → DGQ2788A, TPS62748YFPT → TPS62748
    # DRV2605LDGS → DRV2605L, AP2112K-3.3TRG1 → AP2112K-3.3
    # MCP73831T-2ACI/OT → MCP73831, IS31FL3731-SALS2 → IS31FL3731
    # Only apply for IC-like refs to avoid mangling other values
    if prefix in ("U", "IC", "PS", "MOD", "CP", "X") and re.match(r"^[A-Z]", cleaned):
        # Strip manufacturer prefix: ANALOG_DEVICES_AD8630ARZ → AD8630ARZ
        cleaned = re.sub(r"^(ANALOG_DEVICES|TEXAS_INSTRUMENTS|MICROCHIP|MAXIM|ONSEMI|ST_MICRO)_",
                         "", cleaned, flags=re.IGNORECASE)
        # Strip /OT, /MC, /CHY, /NOPB, /TR etc. (package suffixes after slash)
        cleaned = re.sub(r"/[A-Z]{2,4}\d?$", "", cleaned)
        # Strip tape-and-reel: -TR suffix (early, before other patterns)
        cleaned = re.sub(r"[-_]TR$", "", cleaned, flags=re.IGNORECASE)
        # Strip MORNSUN R3 packaging: K7805-3AR3 → K7805-3A, F0505S-1WR3 → F0505S-1W
        cleaned = re.sub(r"R3$", "", cleaned)
        # Strip common IC ordering suffixes
        # Base pattern: IC name (letters+digits, possibly with embedded letters) then suffix
        m = re.match(r"^([A-Z]+\d+[A-Z]*\d*(?:[-\.]\d+)?)(?:ELT\+?|DSJR|RGET|RGWR|YFPT|YFPR|EN-T\d-\w+|AEN-T\d-\w+|DCUR|DQCT|DQCR|IDGST|IPWR|DGS|TRG\d?|LDGS)$",
                     cleaned, re.IGNORECASE)
        if m:
            cleaned = m.group(1)
        # Strip -SALS, -QALS, -REEL suffix (LED driver / IC packaging variants)
        cleaned = re.sub(r"[-_](SALS|QALS|REEL)\d*$", "", cleaned, flags=re.IGNORECASE)
        # Strip T-suffix + package code: MCP73831T-2ACI → MCP73831
        # Pattern: IC_NAME + T- + ordering (2ACI, 2ATI, etc.)
        m = re.match(r"^([A-Z]+\d+)T-\d+\w+$", cleaned, re.IGNORECASE)
        if m:
            cleaned = m.group(1)
        # Strip LCSC catalog suffix: BC847_C2910145 → BC847
        cleaned = re.sub(r"_C\d{7}$", "", cleaned)
        # Strip board-specific suffixes: CC1352P-LeashPCB → CC1352P
        cleaned = re.sub(r"-[A-Z][a-z]+PCB$", "", cleaned)
        # Strip Lattice FPGA package: ICE40UP5K-SG48 → ICE40UP5K, ECP5-BGA256 → ECP5
        cleaned = re.sub(r"-(SG|BG|BGA|CB)\d+$", "", cleaned, flags=re.IGNORECASE)
        # Strip TI full ordering suffix: CC1352P1F3RGZT → CC1352P, CC2652R1FRGZ → CC2652R
        m = re.match(r"^(CC\d{4}[A-Z])\d*F\d?[A-Z]{2,4}$", cleaned)
        if m:
            cleaned = m.group(1)
        # Strip IC ordering/package suffixes: AT25256B-SSHL-B → AT25256B, M24C64-RMN6TP → M24C64
        # IS25LP128-JBLE → IS25LP128, LAN8710A-EZC → LAN8710A, AS5047P-ATSM → AS5047P
        # Suffix must start with a letter and be 3+ chars. Preserve functional suffixes.
        m = re.match(r"^([A-Z]+\d+[A-Z]*\d*[A-Z]?)-([A-Z][A-Z0-9]{2,6})(?:-[A-Z])?$", cleaned)
        if m and len(m.group(1)) >= 4 and m.group(2) not in _FUNCTIONAL_SUFFIXES:
            cleaned = m.group(1)
        # Strip TI ordering: BQ27441DRZR-G1A → BQ27441
        m = re.match(r"^([A-Z]+\d+)[A-Z]{2,4}R?-[A-Z]\d[A-Z]$", cleaned)
        if m:
            cleaned = m.group(1)
        # Strip generic trailing package codes after voltage dash:
        # RT9080-33GJ5 → RT9080-33, RT9013-33GB → RT9013-33, AP7361C-33E-13 → AP7361C-33
        # MIC2005A-2YM5 → MIC2005A-2
        m = re.match(r"^([A-Z]+\d+[A-Z]?-\d+\.?\d*)[A-Z]{1,2}\d?[A-Z]?(?:-\d+)?$", cleaned)
        if m:
            cleaned = m.group(1)
        # Strip Microchip -NACI ordering: MCP73831-2ACI → MCP73831
        # Only match single-digit + 3+ letters (to avoid stripping voltage like -33GB)
        m = re.match(r"^([A-Z]+\d+)-\d[A-Z]{3,4}$", cleaned)
        if m:
            cleaned = m.group(1)
        # Strip ARZ/ARW ordering suffix on op-amps: AD8630ARZ → AD8630
        m = re.match(r"^([A-Z]+\d+)AR[ZW]$", cleaned, re.IGNORECASE)
        if m:
            cleaned = m.group(1)
        # Strip _MR module variant: ATWINC1500_MR210PA → ATWINC1500
        cleaned = re.sub(r"_MR\d+\w*$", "", cleaned)
        # Strip _SN/_SS/_MN package codes: MCP1501-10E_SN → MCP1501-10
        m = re.match(r"^(.+?)E?_(SN|SS|MN|ML)$", cleaned)
        if m:
            cleaned = m.group(1)
        # Strip Cypress -NNLTX pin+package: CY7C68013A-56LTX → CY7C68013A
        cleaned = re.sub(r"-\d+LTX$", "", cleaned)
        # Strip charger/regulator voltage+package: BL4054B-42TPRN → BL4054B
        m = re.match(r"^([A-Z]+\d+[A-Z])-\d+TPRN$", cleaned)
        if m:
            cleaned = m.group(1)
        # Strip PSRAM multi-part suffix: APS6404L-3SQR-SN → APS6404L
        m = re.match(r"^(APS\d+[A-Z])-\d\w+-\w+$", cleaned)
        if m:
            cleaned = m.group(1)
        # Strip ESP32 flash size suffix: ESP32-WROOM-32E-N4 → ESP32-WROOM-32E
        cleaned = re.sub(r"-N\d+$", "", cleaned)
        # Strip _PACKAGE suffix: STM32F40X_LQFP64 → STM32F40X
        cleaned = re.sub(r"[_-](?:LQFP|TQFP|QFP|QFN|VQFN|BGA|WLCSP|SOIC|SSOP|TSSOP|MSOP|DFN|SON)\d+$",
                         "", cleaned, flags=re.IGNORECASE)

    # Fuse symbol with embedded rating: F_7A_1206 → "7A fuse"
    if prefix == "F":
        m = re.match(r"^F[_-](\d+\.?\d*[mk]?A)", cleaned, re.IGNORECASE)
        if m:
            cleaned = f"{m.group(1)} fuse"

    # LED value with footprint suffix: BLUE-0603, RED-0805 → "blue LED"
    m = re.match(r"^(RED|GREEN|BLUE|YELLOW|WHITE|ORANGE|AMBER)[-_]\d{4}$", cleaned, re.IGNORECASE)
    if m:
        cleaned = f"{m.group(1).lower()} LED"

    # Bare color names → "color LED" (any ref — Eagle uses functional names like CHG, DONE)
    if cleaned.upper() in _BARE_COLORS:
        cleaned = f"{_BARE_COLORS[cleaned.upper()]} LED"

    # Frequency-only oscillator values for U/IC refs: "25MHz" / "12MHz" → "25MHz oscillator"
    if prefix in ("U", "IC", "Y"):
        m = re.match(r"^(\d+\.?\d*\s*[kMG]?Hz)$", cleaned, re.IGNORECASE)
        if m and prefix in ("U", "IC"):
            cleaned = f"{m.group(1)} oscillator"
        # Crystal: "24M" → "24MHz"
        elif re.match(r"^\d+\.?\d*[kMG]$", cleaned):
            cleaned = f"{cleaned}Hz"

    # Eagle/KiCad solder jumper deviceset names → "solder jumper"
    if re.match(r"^(JUMPER-?(SMT_?|PAD-?|COMBO)?|SOLDERJUMPER|SMD[_-]?JUMPER)", cleaned, re.IGNORECASE):
        if "NO" in cleaned.upper() and "NC" not in cleaned.upper():
            cleaned = "solder jumper (NO)"
        elif "NC" in cleaned.upper() or "CONNECTED" in cleaned.upper() or "TRACE" in cleaned.upper():
            cleaned = "solder jumper (NC)"
        else:
            cleaned = "solder jumper"

    # Strip ordering suffixes on diode/transistor refs
    if prefix in ("D", "Q", "TR", "ZD"):
        # Strip -GE3 (Vishay), -GTR (Rohm), -TR (tape-and-reel)
        cleaned = re.sub(r"-(GE\d|GTR|TR)$", "", cleaned, flags=re.IGNORECASE)
        # Strip LCSC catalog suffix: BC847_C2910145 → BC847
        cleaned = re.sub(r"_C\d{7}$", "", cleaned)
        # Littelfuse SP ESD: SP1001-04XTG → SP1001-04, SP3012-06UTG → SP3012-06
        m = re.match(r"^(SP\d{4}-\d{2})[A-Z]{2,3}$", cleaned)
        if m:
            cleaned = m.group(1)
        # Strip DT ESD package: DT1042-04SO → DT1042-04
        m = re.match(r"^(DT\d+-\d+)[A-Z]{2}$", cleaned)
        if m:
            cleaned = m.group(1)

    # Zener diode voltage normalization: "24±2%" → "24V", "6.2±2%" → "6.2V"
    if prefix == "D":
        m = re.match(r"^(\d+\.?\d*)\s*[±+/-]+\s*\d+%?$", cleaned)
        if m:
            return f"{m.group(1)}V zener"

    # Decode fuse/PTC MPNs for non-standard fuse ref prefixes (PTC1, FUSE1, etc.)
    if prefix in ("PTC", "FUSE") and re.match(r"^[A-Z0-9]", cleaned):
        decoded = _decode_mpn_value(cleaned, "F")
        if decoded:
            return decoded

    # Only normalize passives further
    if prefix not in ("R", "C", "L", "FB", "F"):
        return cleaned

    # If prior cleanups already produced a clear human-readable value, return it
    # (e.g. "FerriteBead" → "ferrite bead", "Fuse" → "fuse", "F_7A_1206" → "7A fuse")
    if cleaned != value.strip() and re.search(r"[a-z]{2,}", cleaned):
        return cleaned

    stripped = cleaned

    # Soldered Electronics convention: value-MPN suffix (4u7-TMK212AB7475KG-T → 4u7)
    # Pattern: value part has digits+SI prefix, then dash, then MPN (caps+digits)
    m = re.match(r"^(\d+\.?\d*[pnuμmkMGRr]\d*)-[A-Z][A-Z0-9]", stripped)
    if m:
        stripped = m.group(1)

    # Package-prefixed fuse: 1206FUSE-500mA → 500mA
    m = re.match(r"^\d{4}FUSE[-_](\d+\.?\d*[mkμ]?A)", stripped, re.IGNORECASE)
    if m:
        stripped = m.group(1)

    # Resistor array: R_4x100R_0402_array → "4x100ohm"
    m = re.match(r"^R_(\d+)x(\d+\.?\d*[kKMm]?)[RΩ]", stripped)
    if m:
        count, val = m.group(1), m.group(2)
        parsed_v, parsed_p = _parse_eng_value(val)
        if parsed_v is not None:
            abs_v = parsed_v * _SI_PREFIXES.get(parsed_p, 1) if parsed_p else parsed_v
            return f"{count}x{_format_value(abs_v, 'ohm')}"

    # Decode KiCad naming-convention values: C_100n_0402 → 100n, R_10k_0603 → 10k
    # Also handles: L_1u_5.5A_Bourns-SRP3212A → 1u, R_0R_1206 → 0R
    # Also handles polarized: C_Pol_330u_6.3V_KEMET → 330u
    # Also handles ferrite: FB_220Z_2.2A_TDK-MPZ_0603 → 220Z (impedance)
    m = re.match(r"^[CRLFB]{1,2}_(?:Pol_)?([^_]+)(?:_.*)?$", stripped)
    if m and re.match(r"^\d", m.group(1)):
        stripped = m.group(1)

    # Ferrite bead: strip 'Z' suffix (impedance notation): 220Z → 220
    if prefix == "FB":
        stripped = re.sub(r"Z$", "", stripped)

    # L prefix with R-notation (600R, 220R) or OHM notation: ferrite bead impedance
    # Treat as ohms — these are ferrite beads on L refs
    if prefix == "L" and re.match(r"^\d+R\d*$", stripped):
        val_str = stripped.replace("R", ".", 1).rstrip(".")
        return f"{_format_value(float(val_str), 'ohm')}"
    if prefix == "L" and re.match(r"^\d+\.?\d*[kKMm]?OHM", stripped, re.IGNORECASE):
        m_ohm = re.match(r"^(\d+\.?\d*[kKMm]?)OHM", stripped, re.IGNORECASE)
        if m_ohm:
            return f"{m_ohm.group(1)}ohm"

    # P7: Strip trailing package suffix from values: "10k R0402" → "10k"
    stripped = re.sub(r"\s+[RCL]?\d{4}$", "", stripped)
    # Strip embedded MPN after value+unit: "600OHM UPZ2012E-601-2R0TF" → "600OHM"
    stripped = re.sub(r"^(\d+\.?\d*\s*(?:OHM|ohm|Ω|[kKMG]?[HFΩ]|[munpkKMG])\w*)\s+[A-Z][A-Z0-9].*$",
                      r"\1", stripped, flags=re.IGNORECASE)

    # Fix common typo: O.1uF → 0.1uF (capital O instead of zero)
    stripped = re.sub(r"^O\.", "0.", stripped)

    # Handle R-EU_, R-US_, C-EU_ etc. (Eagle default deviceset names with no real value)
    # Also handles R-EU_R2010, R-EU_0204_7, R-US_0207_10 etc. (symbol + footprint)
    if re.match(r"^[RCL]-(?:EU|US)_", stripped):
        return ""  # empty — source schematic has no value set

    # Handle bare library symbol names used as values (no real value set)
    # e.g. "C" for a capacitor, "R" for a resistor, "D" for a diode, "L" for an inductor
    if stripped in ("C", "R", "L", "D", "FB"):
        return value  # pass through — can't normalize without a real value

    # Handle R_Potentiometer, C_Polarized, etc. — KiCad lib symbol names
    if re.match(r"^[RCLD]_[A-Za-z]", stripped):
        return value  # pass through

    # European notation for resistors BEFORE scientific notation check:
    # 100E = 100 ohm, 330E = 330 ohm, 4E7 = 4.7 ohm (E as decimal separator)
    if prefix in ("R", "RN"):
        m = re.match(r"^(\d+)E(\d+)?$", stripped)
        if m:
            if m.group(2):
                stripped = f"{m.group(1)}.{m.group(2)}"  # 4E7 → 4.7
            else:
                stripped = m.group(1)  # 100E → 100

    # Handle scientific notation: 5e-13F → normalize to pF
    _unit_map = {"R": "ohm", "FB": "ohm", "C": "F", "L": "H"}
    m = re.match(r"^(\d+\.?\d*)[eE]([+-]?\d+)\s*[FHΩ]?\s*$", stripped)
    if m:
        sci_val = float(f"{m.group(1)}e{m.group(2)}")
        unit = _unit_map.get(prefix, "")
        return _format_value(sci_val, unit) if unit else value

    # Strip leading package-size prefix: "R0805 0R11" → "0R11"
    stripped = re.sub(r"^[RCL]\d{4}\s+", "", stripped)
    # Strip trailing package-size suffix: "10uF_0603" → "10uF", "10uF 0805" → "10uF"
    stripped = re.sub(r"[_ ]\d{4}$", "", stripped)
    # Strip "Pack" suffix for resistor packs: "220 Pack" → "220"
    stripped = re.sub(r"\s+Pack$", "", stripped, flags=re.IGNORECASE)

    # Try to extract value from complex deviceset names: "220KOHM-0402T-1 16W-1%" → "220K"
    if re.match(r"^\d+\.?\d*[KkMm]?OHM", stripped, re.IGNORECASE):
        m2 = re.match(r"^(\d+\.?\d*[KkMm]?)OHM", stripped, re.IGNORECASE)
        if m2:
            stripped = m2.group(1)

    # Handle KiCad kR/kΩ notation: "10kR" → "10k", "5k1R" → "5k1", "22R1" → "22R1"
    # Also handles "kΩ" suffix
    stripped = re.sub(r"[RΩ]$", "", stripped)

    # Shorthand cap notation: u1 = 0.1uF, u01 = 0.01uF, u47 = 0.47uF
    if prefix == "C":
        m = re.match(r"^u(\d+)$", stripped, re.IGNORECASE)
        if m:
            stripped = f"0.{m.group(1)}u"  # u1 → 0.1u, u47 → 0.47u

    # Strip trailing comma from values: 600R, → 600R
    stripped = stripped.rstrip(",")

    # Strip tolerance suffixes: "2M1%" → "2M1", "8.06k±1%" → "8.06k", "100n±5%" → "100n"
    stripped = re.sub(r"[±\+/-]+\s*\d+\.?\d*%$", "", stripped).strip()
    # Strip bare trailing tolerance: "10k 1%" → "10k", "4.7k5%" → "4.7k"
    stripped = re.sub(r"\s+\d+\.?\d*%$", "", stripped).strip()
    stripped = re.sub(r"(?<=\d[kKMmnpu])\d+%$", "", stripped)
    # Strip potentiometer taper notation: "10kB" → "10k", "50kA" → "50k"
    # Only strip single A/B/C/W after SI prefix — these denote taper type
    stripped = re.sub(r"(?<=\d[kKMm])[ABCW]$", "", stripped)

    # Normalize "Meg" → "M" before parsing (1Meg = 1M = 1 megaohm)
    raw = re.sub(r"Meg\b", "M", stripped)
    raw = re.sub(r"(ohm|ohms|Ω|[FH])\s*$", "", raw, flags=re.IGNORECASE).strip()

    parsed_val, parsed_prefix = _parse_eng_value(raw)
    if parsed_val is None:
        # Fallback: try to decode MPN-as-value for passives
        decoded = _decode_mpn_value(stripped, prefix)
        if decoded:
            return decoded
        return value

    if parsed_prefix and parsed_prefix in _SI_PREFIXES:
        abs_val = parsed_val * _SI_PREFIXES[parsed_prefix]
    else:
        abs_val = parsed_val

    unit_map = {"R": "ohm", "FB": "ohm", "C": "F", "L": "H"}
    unit = unit_map.get(prefix, "")

    if not unit:
        return value

    # Sanity bounds: reject impossible values
    if unit == "F" and abs_val > 10:
        return value  # cap > 10F is impossible
    if unit == "H" and abs_val > 100:
        return value  # inductor > 100H is impossible
    if unit == "ohm" and abs_val > 1e9:
        return value  # resistor > 1Gohm is impossible

    return _format_value(abs_val, unit)


def extract_inline_specs(value: str) -> tuple[str, dict[str, str]]:
    """Extract voltage/tolerance/power specs embedded in value strings.

    Only splits on whitespace or slash separators. Single-token values pass through.

    Examples:
        '1uF 60V'   → ('1uF', {'voltage': '60V'})
        '100n/50V'  → ('100n', {'voltage': '50V'})
        '75K 1%'    → ('75K', {'tolerance': '1%'})
        '100n/6V3'  → ('100n', {'voltage': '6.3V'})
    """
    specs: dict[str, str] = {}
    # Protect fractional power ratings (1/4W, 1/10W) from being split on /
    protected = re.sub(r"(\d+/\d+W)", lambda m: m.group(1).replace("/", "\x00"), value.strip())
    parts = re.split(r"[\s/]+", protected)
    parts = [p.replace("\x00", "/") for p in parts]
    if len(parts) <= 1:
        return value, specs

    core_parts = []
    for part in parts:
        # Voltage: 60V, 25V, 6.3V, 6V3 (European embedded: 6.3V)
        m = re.match(r"^(\d+\.?\d*)V(\d+)?$", part, re.IGNORECASE)
        if m:
            if m.group(2):
                specs["voltage"] = f"{m.group(1)}.{m.group(2)}V"
            else:
                specs["voltage"] = f"{m.group(1)}V"
            continue
        # SMD package size embedded in value: strip "0805", "0603" etc.
        if re.match(r"^\d{4}$", part):
            continue
        # Tolerance: 1%, 5%, 10%, ±20%
        m = re.match(r"^[±]?(\d+)%$", part)
        if m:
            specs["tolerance"] = f"{m.group(1)}%"
            continue
        # Current rating: 1.4A, 2A (for inductors)
        m = re.match(r"^(\d+\.?\d*A)$", part)
        if m:
            specs["current"] = m.group(1)
            continue
        # Power rating: 2W, 0.25W, 1/4W
        m_pwr = re.match(r"^(\d+/\d+W|\d+\.?\d*W)$", part)
        if m_pwr:
            specs["power"] = m_pwr.group(1)
            continue
        # Ceramic capacitor dielectric: X5R, X7R, C0G, NP0, Y5V
        if re.match(r"^(X[57]R|C0G|NP0|Y5V)$", part, re.IGNORECASE):
            specs["dielectric"] = part.upper()
            continue
        core_parts.append(part)

    return (" ".join(core_parts) if core_parts else value), specs


# Connector ref prefixes
_CONNECTOR_REFS = ("J", "JP", "CN", "X", "P", "CON")

# Named connector types to preserve as-is
_NAMED_CONNECTOR_KEYWORDS = {
    "USB", "JTAG", "SWD", "BARREL", "JACK", "SCREW", "TERMINAL",
    "JST", "MOLEX", "MICRO", "HDMI", "RJ45", "RJ11", "DB9", "DB25",
    "DIN", "BNC", "SMA", "AUDIO", "PHONE", "QWIIC", "STEMMA",
}


def _extract_header_dims(s: str) -> tuple[int, int] | None:
    """Extract (rows, cols) from header patterns like M06, 1X04, CONN_01X04."""
    # M06, M04
    m = re.match(r"^M(\d+)$", s)
    if m:
        return (1, int(m.group(1)))
    # MA08-1
    m = re.match(r"^MA(\d+)", s)
    if m:
        return (1, int(m.group(1)))
    # NxM: 1X04, 2X03, CONN_01X04, 1X06_NO_SILK
    m = re.search(r"(\d+)X(\d+)", s, re.IGNORECASE)
    if m:
        rows, cols = int(m.group(1)), int(m.group(2))
        if 1 <= rows <= 3 and 1 <= cols <= 40:
            return (rows, cols)
    # CONN_02, CONN_03 — simple N-pin connector
    m = re.match(r"^CONN[_-]?(\d+)$", s, re.IGNORECASE)
    if m:
        return (1, int(m.group(1)))
    return None


def normalize_connector_value(value: str, footprint: str, ref: str) -> str:
    """Normalize generic connector values to 'NxM header' format.

    Preserves named connector types (USB, JTAG, etc.). For generic
    Eagle deviceset names (M06, I2C_STANDARD), extracts pin layout
    from value or footprint.
    """
    m = re.match(r"^([A-Za-z]+)", ref)
    prefix = m.group(1).upper() if m else ""

    # Check if value or footprint names a specific connector type
    upper_val = value.upper()
    upper_fp = footprint.upper()
    val_has_named = any(kw in upper_val for kw in _NAMED_CONNECTOR_KEYWORDS)
    fp_has_named = any(kw in upper_fp for kw in _NAMED_CONNECTOR_KEYWORDS)

    # Value itself is a named type (USB-C, JST SH, etc.) — preserve it
    if val_has_named:
        return value

    # Crystal/oscillator: skip connector normalization if footprint or value indicates crystal
    if any(kw in upper_fp or kw in upper_val
           for kw in ("XTAL", "CRYSTAL", "OSC", "MHZ", "KHZ")):
        return value

    # Generic interface names used as values — normalize with pin layout
    if upper_val in ("I2C", "SPI", "I2C_STANDARD", "SPI_STANDARD"):
        dims = _extract_header_dims(footprint)
        if dims:
            return f"{dims[0]}x{dims[1]} header"
        return value

    # For known connector refs, extract pin layout
    if prefix in _CONNECTOR_REFS:
        dims = _extract_header_dims(value) or _extract_header_dims(footprint)
        if dims:
            rows, cols = dims
            # Use footprint info for connector type
            if "SCREW" in upper_fp or "TERMINAL" in upper_fp:
                return f"{rows}x{cols} screw terminal"
            return f"{rows}x{cols} header"

    # For any ref, normalize pin header deviceset names: PINHD-1X9, HEADER-1X1, CONN_02
    if not val_has_named and not fp_has_named:
        m = re.match(r"^(?:PINHD|HEADER|CONN)[_-]?", value, re.IGNORECASE)
        if m:
            dims = _extract_header_dims(value) or _extract_header_dims(footprint)
            if dims:
                rows, cols = dims
                return f"{rows}x{cols} header"

    return value


def normalize_footprint(footprint: str, ref: str = "") -> str:
    """Normalize footprint to compact form.

    KiCad-style:
        R_0402_1005Metric → 0402
        SOIC-8_3.9x... → SOIC-8
    Eagle-style:
        0603-CAP / 0603-RES → 0603
        PAD-JUMPER-3-... → SJ-3
    """
    if not footprint:
        return footprint

    fp = footprint.strip()

    # Strip Eagle @N variant suffix: 1X02@1 → 1X02
    fp = re.sub(r"@\d+$", "", fp)

    # Wurth long connector names: Wurth_619...-1x02_P2.54mm_... → 1X02
    m = re.match(r"^Wurth_\w+-(\d+x\d+)", fp, re.IGNORECASE)
    if m:
        return m.group(1).upper()

    # Strip KiCad library prefix if it leaked through: "Resistor_SMD:R_0402_..." → "R_0402_..."
    if ":" in fp:
        fp = fp.split(":")[-1]

    # Unicode normalization in footprints: − → -
    fp = fp.replace("\u2212", "-").replace("\u2013", "-")

    # Strip _HandSolder/_HandSoldering suffix: SOT-23-5_HandSoldering → SOT-23-5
    fp = re.sub(r"_Hand[Ss]older(?:ing)?$", "", fp)

    # Strip _Pad dimensions suffix: LED_0805_2012Metric_Pad1.15x1.40mm → LED_0805_2012Metric
    fp = re.sub(r"_Pad\d+\.?\d*x\d+\.?\d*mm$", "", fp)

    # GSG (Great Scott Gadgets) custom prefix: GSG-QFN48-6 → QFN-48, GSG-SOT363 → SOT-363
    m = re.match(r"^GSG-([A-Z]+?)(\d+)(?:-\d+)?$", fp, re.IGNORECASE)
    if m:
        pkg, pins = m.group(1), m.group(2)
        return f"{pkg.upper()}-{pins}"

    # D_ prefix (KiCad diode footprints): D_SOD-123 → SOD-123
    fp = re.sub(r"^D_", "", fp)
    # Fuse_ prefix: Fuse_0805_2012Metric → 0805_2012Metric (handled by later rules)
    fp = re.sub(r"^Fuse_", "", fp)

    # SO08/SO14/SO16 → SOIC-8/SOIC-14/SOIC-16 (Eagle convention)
    m = re.match(r"^SO0?(\d+)$", fp)
    if m:
        return f"SOIC-{m.group(1)}"

    # SOT23-NL → SOT-23-N (strip trailing L, add dash)
    m = re.match(r"^SOT23-?(\d+)L?$", fp, re.IGNORECASE)
    if m:
        return f"SOT-23-{m.group(1)}"

    # Strip _PHILIPS, _TEX, _NICHICON etc. manufacturer suffixes from packages
    fp = re.sub(r"[_-](PHILIPS|TEX|NICHICON|MURATA|TDK|VISHAY|KEMET|YAGEO)$", "", fp, flags=re.IGNORECASE)

    # Strip -1EP (exposed pad) suffix: QFN-32-1EP → QFN-32
    fp = re.sub(r"-\d*EP$", "", fp)

    # Eagle angle suffix: 2X05/90 → 2X05
    fp = re.sub(r"/\d+$", "", fp)

    # KiCad jumper: SMD-JUMPER-CONNECTED_TRACE_* → SJ-2
    if re.match(r"^SMD[-_]JUMPER", fp, re.IGNORECASE):
        return "SJ-2"

    # Bare SMD size with metric suffix: 0805_2012Metric → 0805
    m = re.match(r"^(\d{4})_\d{4}Metric$", fp)
    if m:
        return m.group(1)

    # SMD size with letter suffix: 0603C, 0805C, 0402R, 0402LED → strip suffix
    m = re.match(r"^(\d{4})[A-Za-z]+$", fp)
    if m:
        return m.group(1)

    # USB-C connector: anything with USB_C or USB-C → "USB-C"
    if re.match(r"^USB[_-]C", fp, re.IGNORECASE):
        return "USB-C"

    # KiCad PinHeader/PinSocket: PinHeader_1x06_P2.54mm_Vertical → 1X06
    # Also Pin_Header_Straight_1x08_Pitch2.54mm
    m = re.match(r"^Pin[_ ]?(?:Header|Socket)\w*_(\d+)x(\d+)", fp, re.IGNORECASE)
    if m:
        rows, cols = m.group(1), m.group(2)
        return f"{rows}X{cols.lstrip('0') or '0'}"

    # KiCad through-hole axial/radial: R_Axial_DIN0204_..., C_Axial_..., C_Radial_...
    m = re.match(r"^[RCLD]_(Axial|Radial)", fp, re.IGNORECASE)
    if m:
        return m.group(1).capitalize()

    # KiCad polarized cap with EIA size: CP_EIA-XXXX-YY_... → EIA-XXXX
    m = re.match(r"^CP_EIA-(\d{4})", fp)
    if m:
        return f"EIA-{m.group(1)}"

    # KiCad electrolytic: CP_Elec_XXXX → Electrolytic, CP_Elec → Electrolytic
    if fp.startswith("CP_Elec"):
        m = re.match(r"^CP_Elec_(\d+x\d+)", fp)
        if m:
            return f"Electrolytic-{m.group(1)}"
        return "Electrolytic"

    # Crystal: Crystal_SMD_3225-4Pin_... → SMD3225, Crystal_SMD_2012-... → SMD2012
    m = re.match(r"^Crystal_SMD_(\d{4})", fp)
    if m:
        return f"SMD{m.group(1)}"

    # TO-92 package variants: TO-92L_Inline_Wide, TO-92_Inline → TO-92
    m = re.match(r"^(TO-\d+)\w*[_-]", fp, re.IGNORECASE)
    if m:
        return m.group(1).upper()

    # DIP with pin count: DIP-8_W7.62mm, DIP-14_W7.62mm → DIP-8, DIP-14
    m = re.match(r"^(DIP-\d+)", fp, re.IGNORECASE)
    if m:
        return m.group(1).upper()

    # KiCad: R_0402_1005Metric, C_0805_2012Metric, also C_0402 (pkl_dipol convention)
    m = re.match(r"^[RCL]_(\d{4})(?:_\d{4}|$)", fp)
    if m:
        return m.group(1)

    # EIA tantalum case sizes: EIA-7343, EIA-3216, EIA-6032 → preserve as-is
    if re.match(r"^EIA-\d{4}$", fp):
        return fp

    # Blues/custom: CS-C-0402, RS-0402, FS-0603, LS-1206 (prefix-dash-SMD size)
    m = re.match(r"^[A-Z]{1,3}-(?:[A-Z]-)?(\d{4})(?:[_-]|$)", fp)
    if m:
        return m.group(1)

    # SMD size with suffix: 0603-CAP, 0603-RES, 0805-NO, 0402-ARD
    m = re.match(r"^(\d{4})-\w+$", fp)
    if m:
        return m.group(1)

    # Leading underscore + SMD: _0805MP → 0805
    m = re.match(r"^_(\d{4})", fp)
    if m:
        return m.group(1)

    # Electrolama/custom: _PKG_C_0402 → 0402
    m = re.match(r"^_?PKG_[A-Z]_(\d{4})", fp)
    if m:
        return m.group(1)

    # Known passive/LED prefix + SMD size: C0402, R0603, C0603K, L2012C, EC1206, SML0805
    # Restrict to known prefixes to avoid matching IC part numbers (TXB0104 → 0104 is WRONG)
    m = re.match(r"^(C|R|L|M|EC|SML|LED)(\d{4})[A-Z]?$", fp, re.IGNORECASE)
    if m:
        return m.group(2)

    # Letter-dash-size: C-0402, R-0603 (Particle convention)
    m = re.match(r"^[A-Z]-(\d{4})$", fp)
    if m:
        return m.group(1)

    # Package with pin count + dimensions: SOIC-8_3.9x..., QFN-48_7x7mm...
    m = re.match(r"^([A-Z][\w]+-\d+)[_\s]\d+\.?\d*[xX]", fp)
    if m:
        return m.group(1)

    # Package with pin count, no dimensions (already compact): SOT-23, SOIC-8
    # But if trailing number is 4-digit SMD size, extract it: CHIPLED-0603 → 0603
    # Exclude manufacturer names (Molex, JST etc.) — their trailing digits are part numbers
    m = re.match(r"^([A-Z][\w]+-\d+)$", fp)
    if m:
        if re.match(r"^(Molex|JST|Hirose|Amphenol|TE_|Wurth)", fp, re.IGNORECASE):
            return fp  # connector footprint — keep as-is
        trail = re.search(r"-(\d{4})$", fp)
        if trail:
            return trail.group(1)
        return m.group(1)

    # Eagle/Adafruit jumper pads → compact form
    m = re.match(r"^PAD-JUMPER-(\d+)", fp)
    if m:
        return f"SJ-{m.group(1)}"
    # SparkFun: SJ_2S-NO, SJ_2S, SJ_3S
    m = re.match(r"^SJ_(\d+)", fp)
    if m:
        return f"SJ-{m.group(1)}"

    # Adafruit: SOLDERJUMPER, SOLDERJUMPER_2WAY, SOLDERJUMPER_CLOSEDWIRE
    if fp.upper().startswith("SOLDERJUMPER"):
        if "2WAY" in fp.upper() or "2_WAY" in fp.upper():
            return "SJ-3"  # 3-pad, 2-way selection
        return "SJ-2"  # simple 2-pad jumper

    # SparkFun: SMT-JUMPER_2_NC_TRACE, SMT-JUMPER_3_2-NC_TRACE
    m = re.match(r"^SMT-JUMPER_(\d+)", fp)
    if m:
        return f"SJ-{m.group(1)}"

    # Watterott/generic: JUMPER3-0402_NC, COMBO-JUMPER_2_NC_TRACE → SJ-N
    m = re.match(r"^(?:COMBO-)?JUMPER[_-]?(\d+)", fp, re.IGNORECASE)
    if m:
        return f"SJ-{m.group(1)}"

    # Electrolama _PKG_ prefix: _PKG_C_0402, _PKG_SOT886_JEDEC, _PKG_LED_0603
    m = re.match(r"^_?PKG_", fp)
    if m:
        remainder = fp[m.end():]
        parts = remainder.split("_")
        if len(parts) >= 2 and len(parts[0]) == 1 and re.match(r"^\d{4}$", parts[1]):
            return parts[1]  # C_0402 → 0402
        if len(parts) >= 2 and parts[0].upper() == "LED" and re.match(r"^\d{4}$", parts[1]):
            return parts[1]  # LED_0603 → 0603
        return parts[0]  # SOT886, MSOP10

    # IPC-7351: QFN50P700X700X100-49N → QFN-49, SOT65P212X110-5N → SOT-5
    m = re.match(r"^([A-Z]{2,4})\d+P\d+X\d+(?:X\d+)?-(\d+)[A-Z]?$", fp)
    if m:
        return f"{m.group(1)}-{m.group(2)}"

    # Connector footprint: 1X04_NO_SILK, 1X05_ROUND_76 → 1X04, 1X05
    m = re.match(r"^(\d+X\d+)(?:[_-]\w+)+$", fp, re.IGNORECASE)
    if m:
        return m.group(1)

    # Embedded SMD size: CHIPLED_0603_NOOUTLINE, LED_0805_NOOUTLINE → 0603, 0805
    m = re.match(r"^\w+_(\d{4})(?:_\w+)+$", fp)
    if m:
        return m.group(1)

    # Strip trailing dimension info: SOMETHING_3.2x1.6mm → SOMETHING
    m = re.match(r"^(\S+?)_\d+\.?\d*[xX]\d+", fp)
    if m:
        return m.group(1)

    return fp


# ---------------------------------------------------------------------------
# Repo cloning
# ---------------------------------------------------------------------------

def clone_repo(org_repo: str, fmt: str, cache_dir: Path | None = None,
               force: bool = False) -> Path:
    """Sparse-clone a GitHub repo for schematic files."""
    import shutil

    cache_dir = cache_dir or CACHE_DIR
    dir_name = org_repo.replace("/", "--")
    repo_dir = cache_dir / dir_name

    if repo_dir.exists() and not force:
        log.info("Using cached repo: %s", repo_dir)
        return repo_dir

    if repo_dir.exists() and force:
        # Safety: only delete if inside cache dir
        if repo_dir.resolve().parent == cache_dir.resolve():
            shutil.rmtree(repo_dir)
        else:
            raise ValueError(f"Refusing to delete {repo_dir}: not inside cache dir")

    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://github.com/{org_repo}.git"

    log.info("Cloning %s → %s", url, repo_dir)

    subprocess.run(
        ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", url, str(repo_dir)],
        check=True, capture_output=True, text=True, timeout=120,
    )

    if fmt == "eagle":
        patterns = ["*.sch", "*.brd"]
    elif fmt.startswith("kicad"):
        patterns = ["*.kicad_sch", "*.kicad_pcb", "*.kicad_pro", "*.sch"]
    else:
        patterns = ["*"]

    try:
        subprocess.run(
            ["git", "sparse-checkout", "set", "--no-cone"] + patterns,
            cwd=repo_dir, check=True, capture_output=True, text=True, timeout=60,
        )

        subprocess.run(
            ["git", "checkout"],
            cwd=repo_dir, check=True, capture_output=True, text=True, timeout=120,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        # Clean up broken repo on failure so next run doesn't use partial cache
        log.warning("Sparse checkout failed for %s, cleaning up", org_repo)
        shutil.rmtree(repo_dir, ignore_errors=True)
        raise

    return repo_dir


# ---------------------------------------------------------------------------
# Board-specific overrides (imported from board_overrides.py)
# ---------------------------------------------------------------------------

from board_overrides import (
    BOARD_OVERRIDES as _BOARD_OVERRIDES,
    BOARD_META_OVERRIDES as _BOARD_META_OVERRIDES,
    TAG_OVERRIDES as _TAG_OVERRIDES,
    NET_PIN_FIXES as _NET_PIN_FIXES,
)


def _apply_overrides(slug: str, components: list[Component]) -> int:
    """Apply board-specific overrides to fix known source-data errors.

    Returns count of overrides applied.
    """
    count = 0
    for comp in components:
        overrides = _BOARD_OVERRIDES.get((slug, comp.ref))
        if not overrides:
            continue
        for field, new_val in overrides.items():
            if field == "value":
                old = comp.value
                comp.value = new_val
                log.info("Override %s.%s value: %s → %s", slug, comp.ref, old, new_val)
            else:
                old = comp.attributes.get(field, "")
                comp.attributes[field] = new_val
                log.info("Override %s.%s %s: %s → %s", slug, comp.ref, field, old, new_val)
            count += 1
    return count



def _clean_pin_name(pin: str) -> str:
    """Strip LaTeX subscripts, KiCad active-low, and escape sequences from pin names.

    V_{CC} → VCC, ~{RESET} → nRESET, A5{slash}CC1 → A5/CC1
    """
    cleaned = re.sub(r"_\{([^}]+)\}", r"\1", pin)
    # KiCad active-low: ~{PIN} → nPIN (standard EE convention for active-low)
    cleaned = re.sub(r"~\{([^}]+)\}", r"n\1", cleaned)
    # KiCad escape sequences: {slash} → /
    cleaned = cleaned.replace("{slash}", "/")
    return cleaned


def _apply_net_pin_fixes(slug: str, nets: list[Net]) -> int:
    """Fix known pin name typos in nets and clean formatting. Returns count of fixes applied."""
    count = 0
    for net in nets:
        # Clean LaTeX from net name
        net.name = _clean_pin_name(net.name)
        new_pins = []
        for pin in net.pins:
            fixed = _NET_PIN_FIXES.get((slug, pin))
            if fixed:
                new_pins.append(fixed)
                count += 1
                log.info("Net pin fix %s: %s → %s", slug, pin, fixed)
            else:
                cleaned_pin = _clean_pin_name(pin)
                # Filter power flag footprint pins that leaked from PCB
                # e.g., +3.3V1.Pad, +5V1.Pad, GND1.Pad, VBUS1.Pad, +1V1.Pad
                ref_part = cleaned_pin.split(".")[0]
                if re.match(r"^[+\-]", ref_part):
                    count += 1
                    continue  # skip power flag pin
                new_pins.append(cleaned_pin)
        net.pins = sorted(new_pins)
    # Remove nets that became single-pin or empty after cleanup
    nets[:] = [n for n in nets if len(n.pins) >= 2]
    return count


# ---------------------------------------------------------------------------
# MPN / value conflict detection
# ---------------------------------------------------------------------------

def _check_mpn_conflicts(components: list[Component]) -> None:
    """Warn when MPN and Value disagree for IC-like components.

    When the value field looks like a part number and the MPN field contains
    a different part family, log a warning.
    """
    for comp in components:
        mpn = comp.attributes.get("mpn", "")
        if not mpn or not comp.value:
            continue
        # Only check IC-like components (value looks like a part number)
        if not re.match(r"^[A-Z][A-Z0-9]", comp.value):
            continue
        # Extract family prefix from each (first alphanumeric segment before dash)
        val_family = re.match(r"^([A-Z]+\d+)", comp.value.upper())
        mpn_family = re.match(r"^([A-Z]+\d+)", mpn.upper())
        if val_family and mpn_family and val_family.group(1) != mpn_family.group(1):
            log.warning("MPN conflict on %s: value=%s but mpn=%s",
                        comp.ref, comp.value, mpn)


# ---------------------------------------------------------------------------
# Circuit analysis (post-parse annotation)
# ---------------------------------------------------------------------------

_POWER_NET_NAMES = {
    "VCC", "VDD", "VDDIO", "3.3V", "3V3", "5V", "5V0", "1.8V", "1V8",
    "12V", "VBUS", "VIN", "VBAT", "VSYS", "V+", "VOUT", "AVCC", "AVDD",
    "DVCC", "DVDD", "V_USB", "VUSB",
}

_GND_NET_NAMES = {"GND", "VSS", "AGND", "DGND", "PGND", "GND1", "GND2", "GNDA", "GNDD"}


def _is_power_net(name: str) -> bool:
    upper = name.upper().replace(" ", "")
    if upper in _POWER_NET_NAMES:
        return True
    # Match patterns like 3.3V, +5V, +3V3
    if re.match(r"^\+?\d+\.?\d*V\d*$", upper):
        return True
    # Match VCC_*, VDD_* variants
    if re.match(r"^V(CC|DD|BAT|BUS|IN|OUT|SYS|USB)", upper):
        return True
    return False


def _is_gnd_net(name: str) -> bool:
    upper = name.upper().replace(" ", "")
    return upper in _GND_NET_NAMES or "GND" in upper


def _get_ref_prefix(ref: str) -> str:
    m = re.match(r"^([A-Z]+)", ref, re.IGNORECASE)
    return m.group(1).upper() if m else ""


def annotate_circuit_roles(components: list[Component], nets: list[Net],
                           positions: list[Position] | None = None) -> None:
    """Add decoupling/pullup/pulldown annotations based on net analysis.

    Modifies component attributes in-place.
    """
    # Build lookup structures
    pin_to_net: dict[str, str] = {}
    net_pins: dict[str, set[str]] = {}

    for net in nets:
        pin_set = set(net.pins)
        net_pins[net.name] = pin_set
        for pin in net.pins:
            pin_to_net[pin] = net.name

    # Classify nets
    power_nets = {name for name in net_pins if _is_power_net(name)}
    gnd_nets = {name for name in net_pins if _is_gnd_net(name)}

    if not power_nets and not gnd_nets:
        return

    # Build position map for proximity filtering
    pos_map: dict[str, tuple[float, float]] = {}
    if positions:
        for p in positions:
            pos_map[p.ref] = (p.x, p.y)

    # IC prefixes — components that get decoupled
    ic_prefixes = {"U", "IC", "MOD"}

    for comp in components:
        prefix = _get_ref_prefix(comp.ref)

        if prefix == "C":
            # Decoupling cap detection: one pin on power, one on GND
            _annotate_decoupling(comp, pin_to_net, net_pins, power_nets, gnd_nets,
                                 ic_prefixes, pos_map)

        elif prefix in ("R", "FB"):
            # Pull-up/pull-down detection: one pin on power/GND, other on signal
            _annotate_pull(comp, pin_to_net, power_nets, gnd_nets, net_pins)


def _find_component_nets(ref: str, pin_to_net: dict[str, str]) -> list[str]:
    """Find all nets connected to a component, handling both numbered and named pins."""
    prefix = f"{ref}."
    # Try numbered pins first (most common)
    net1 = pin_to_net.get(f"{ref}.1")
    net2 = pin_to_net.get(f"{ref}.2")
    if net1 and net2:
        return [net1, net2]
    # Fallback: scan for any pins matching this ref (handles pinfunction names)
    nets = []
    for pin, net in pin_to_net.items():
        if pin.startswith(prefix):
            if net not in nets:
                nets.append(net)
    return nets


def _annotate_decoupling(cap: Component, pin_to_net: dict[str, str],
                         net_pins: dict[str, set[str]], power_nets: set[str],
                         gnd_nets: set[str], ic_prefixes: set[str],
                         pos_map: dict[str, tuple[float, float]] | None = None) -> None:
    """Annotate a cap with 'decouples: <IC ref>' if it bridges power and GND."""
    cap_nets = _find_component_nets(cap.ref, pin_to_net)
    if len(cap_nets) < 2:
        return

    # Identify which net is power and which is ground
    power_net = None
    has_gnd = False
    for n in cap_nets:
        if n in power_nets:
            power_net = n
        if n in gnd_nets:
            has_gnd = True
    if not power_net or not has_gnd:
        return

    # Find ICs that share this power net
    ics: set[str] = set()
    for pin in net_pins.get(power_net, set()):
        ref = pin.split(".")[0]
        if ref != cap.ref and _get_ref_prefix(ref) in ic_prefixes:
            ics.add(ref)

    if not ics:
        return

    # Pick the single closest IC by position
    cap_pos = pos_map.get(cap.ref) if pos_map else None
    if cap_pos and pos_map:
        def _ic_dist(ic: str) -> float:
            ic_pos = pos_map.get(ic)
            if not ic_pos:
                return float("inf")
            return ((cap_pos[0] - ic_pos[0]) ** 2 + (cap_pos[1] - ic_pos[1]) ** 2) ** 0.5

        closest = min(ics, key=_ic_dist)
        # Only annotate if the closest IC is within 15mm
        if _ic_dist(closest) <= 15.0:
            cap.attributes["decouples"] = closest
    elif len(ics) == 1:
        # No position data but only one IC on this rail — unambiguous
        cap.attributes["decouples"] = next(iter(ics))


_RAW_NET_RE = re.compile(
    r"^(?:N\$\d+|Net-\(.+\)|unconnected-.+)$"
)


def _resolve_net_name(net_name: str, net_pins: dict[str, set[str]],
                      res_ref: str) -> str:
    """Resolve auto-generated net names to meaningful signal names.

    For nets named N$10, Net-(R3-Pad2), etc., look at the other pins on the
    net and pick the best label — an IC/active-component pin function, or a
    named component pin.  Falls back to the raw net name if nothing better.
    """
    cleaned = _clean_pin_name(net_name)
    if not _RAW_NET_RE.match(net_name):
        return cleaned

    pins = net_pins.get(net_name, set())
    # Filter out the resistor's own pins
    other_pins = [p for p in pins if not p.startswith(f"{res_ref}.")]
    if not other_pins:
        return cleaned

    # Prefer IC/active component pins (U, IC, MOD, Q, etc.) over passives
    ic_pins = []
    active_pins = []
    for pin in other_pins:
        ref = pin.split(".")[0]
        prefix = _get_ref_prefix(ref)
        if prefix in ("U", "IC", "MOD"):
            ic_pins.append(pin)
        elif prefix in ("Q", "D", "SW", "S", "CONN"):
            active_pins.append(pin)

    # Best: IC pin with a function name (e.g. "U1.RESET")
    best = ic_pins or active_pins or other_pins
    # Pick the pin with the most descriptive name (has a non-numeric suffix)
    for pin in sorted(best):
        parts = pin.split(".", 1)
        if len(parts) == 2 and not parts[1].isdigit():
            return _clean_pin_name(pin)

    # Fallback: first other pin as "REF.PIN"
    return _clean_pin_name(sorted(best)[0])


def _annotate_pull(res: Component, pin_to_net: dict[str, str],
                   power_nets: set[str], gnd_nets: set[str],
                   net_pins: dict[str, set[str]]) -> None:
    """Annotate a resistor with 'pullup: <net>' or 'pulldown: <net>'.

    Only annotates resistors ≥ 1kohm — lower values are likely current sense,
    series termination, or other non-pull functions.
    """
    # Skip low-value resistors — real pull-ups are ≥ 1kohm
    val_str = res.value.lower().replace("ohm", "").strip()
    parsed_val, parsed_prefix = _parse_eng_value(val_str)
    if parsed_val is not None:
        abs_val = parsed_val * _SI_PREFIXES.get(parsed_prefix, 1) if parsed_prefix else parsed_val
        if abs_val < 1000:  # < 1kohm → not a pull-up
            return
    else:
        # Can't parse value (empty, text like SHUNT/FILTER/NTC) — skip annotation
        return

    res_nets = _find_component_nets(res.ref, pin_to_net)
    if len(res_nets) < 2:
        return

    net1, net2 = res_nets[0], res_nets[1]

    if net1 in power_nets and net2 not in gnd_nets and net2 not in power_nets:
        res.attributes["pullup"] = _resolve_net_name(net2, net_pins, res.ref)
    elif net2 in power_nets and net1 not in gnd_nets and net1 not in power_nets:
        res.attributes["pullup"] = _resolve_net_name(net1, net_pins, res.ref)
    elif net1 in gnd_nets and net2 not in power_nets and net2 not in gnd_nets:
        res.attributes["pulldown"] = _resolve_net_name(net2, net_pins, res.ref)
    elif net2 in gnd_nets and net1 not in power_nets and net1 not in gnd_nets:
        res.attributes["pulldown"] = _resolve_net_name(net1, net_pins, res.ref)


# ---------------------------------------------------------------------------
# YAML output
# ---------------------------------------------------------------------------

class _BoardDumper(yaml.Dumper):
    """Custom YAML dumper for board output — avoids mutating the global yaml.Dumper."""
    pass


def _str_representer(dumper: yaml.Dumper, data: str) -> yaml.Node:
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _list_representer(dumper: yaml.Dumper, data: list) -> yaml.Node:
    if all(isinstance(item, str) for item in data) and len(data) <= 6:
        return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data)


_BoardDumper.add_representer(str, _str_representer)
_BoardDumper.add_representer(list, _list_representer)


# ---------------------------------------------------------------------------
# Net name inference — rename auto-numbered nets using IC pin names
# ---------------------------------------------------------------------------

# Patterns that identify auto-generated net names
_AUTO_NET_EAGLE = re.compile(r"^N\$\d+$")
_AUTO_NET_KICAD = re.compile(r"^Net-\(.*-Pad\d+\)$")

# IC/active component ref prefixes (these have meaningful pin names)
_IC_PREFIXES = {"U", "IC", "Q", "T"}

# Pin names that are too generic to use
_GENERIC_PIN = re.compile(
    r"^(\d+|GPIO\d+|P[A-Z]\d+|IO\d+|PAD\d*|NC|DNC|EP|GND|VCC|VDD|VSS|VBAT|"
    r"[BCESGD])$",  # single-letter transistor pins (Base/Collector/Emitter/Gate/Source/Drain)
    re.IGNORECASE,
)


def _is_auto_net(name: str) -> bool:
    """Check if a net name is auto-generated (no semantic meaning)."""
    return bool(_AUTO_NET_EAGLE.match(name) or _AUTO_NET_KICAD.match(name))


def _pin_ref_prefix(pin: str) -> str:
    """Extract the reference prefix from a pin string like 'U1.SW' → 'U'."""
    ref = pin.split(".")[0]
    return ref.rstrip("0123456789$")


def _pin_function(pin: str) -> str:
    """Extract the pin function from 'U1.SW' → 'SW', 'R1.2' → '2'."""
    parts = pin.split(".", 1)
    return parts[1] if len(parts) > 1 else ""


def infer_net_names(nets: list[Net]) -> int:
    """Rename auto-numbered nets in-place using IC pin function heuristics.

    Only renames when a single unambiguous IC pin name is found.
    Returns count of nets renamed.
    """
    # Build set of all existing net names to avoid collisions
    existing = {n.name for n in nets}
    renamed = 0

    for net in nets:
        if not _is_auto_net(net.name):
            continue

        # Find IC pins with meaningful names
        candidates: list[str] = []
        for pin in net.pins:
            prefix = _pin_ref_prefix(pin)
            if prefix not in _IC_PREFIXES:
                continue
            func = _pin_function(pin)
            if not func or _GENERIC_PIN.match(func):
                continue
            # Strip @pad_num disambiguation suffix
            func = re.sub(r"@\d+$", "", func)
            candidates.append(func)

        if not candidates:
            continue

        # Pick the best candidate: prefer non-numeric, shortest
        candidates.sort(key=lambda c: (c[0].isdigit(), len(c)))
        best = candidates[0]

        # Sanitize for YAML: replace non-alphanumeric with _
        clean = re.sub(r"[^A-Za-z0-9_]", "_", best).strip("_")
        if not clean:
            continue

        # Avoid collisions by appending a suffix
        final = clean
        suffix = 2
        while final in existing:
            final = f"{clean}_{suffix}"
            suffix += 1

        existing.discard(net.name)
        existing.add(final)
        net.name = final
        renamed += 1

    return renamed


def board_to_dict(board: BoardData) -> dict:
    """Convert BoardData to a dict suitable for YAML output."""
    d: dict = {
        "name": board.name,
        "slug": board.slug,
        "source": board.source,
        "format": board.format,
    }

    if board.description:
        d["description"] = board.description
    if board.tags:
        d["tags"] = board.tags
    if board.key_ics:
        d["key_ics"] = board.key_ics

    if board.outline:
        d["outline"] = {"width_mm": board.outline.width, "height_mm": board.outline.height}

    if board.design_rules:
        dr = board.design_rules
        rules: dict = {"layers": dr.layers}
        if dr.min_trace:
            rules["min_trace"] = dr.min_trace
        if dr.min_clearance:
            rules["min_clearance"] = dr.min_clearance
        if dr.min_drill:
            rules["min_drill"] = dr.min_drill
        if dr.min_via:
            rules["min_via"] = dr.min_via
        d["design_rules"] = rules

    if board.components:
        d["components"] = []
        # Filter junk components (logos, pads, ordering instructions, etc.)
        _JUNK_VALUES = {
            "logo", "pad", "test point", "mounting hole",
            "NC", "DNP", "NF", "NI", "DNI", "NOFIT", "NOPOP",
            "FIDUCIAL", "heatsink",
        }
        _JUNK_VALUE_PATTERNS = re.compile(
            r"^(mounting\s*hole|tooling\s*hole|standoff|spacer|mouse\s*bite|"
            r"jlc\s*tooling|test\s*point|fiducial|oshw[_-]?logo)",
            re.IGNORECASE,
        )
        _JUNK_FOOTPRINTS = {"Ordering_Instructions"}
        for c in sorted(board.components, key=lambda c: c.ref):
            if not c.value or c.value in _JUNK_VALUES:
                continue
            if c.value and _JUNK_VALUE_PATTERNS.match(c.value):
                continue
            if c.footprint in _JUNK_FOOTPRINTS:
                continue
            comp: dict = {"ref": c.ref, "value": c.value, "footprint": c.footprint}
            if c.attributes:
                comp.update(c.attributes)
            d["components"].append(comp)

    if board.nets:
        d["nets"] = []
        for n in sorted(board.nets, key=lambda n: n.name):
            net_dict: dict = {"name": n.name, "pins": n.pins}
            if n.net_class and n.net_class != "default":
                net_dict["class"] = n.net_class
            if n.trace_width:
                net_dict["trace_width"] = n.trace_width
            d["nets"].append(net_dict)

    if board.positions:
        # Only include positions for refs that are in the component list
        comp_refs = {c["ref"] for c in d.get("components", [])}
        d["positions"] = []
        for p in sorted(board.positions, key=lambda p: p.ref):
            if p.ref not in comp_refs:
                continue  # skip orphaned positions (fiducials, mounting holes, etc.)
            pos: dict = {"ref": p.ref, "x": p.x, "y": p.y}
            if p.rotation:
                pos["rot"] = p.rotation
            if p.side == "back":
                pos["side"] = "back"
            d["positions"].append(pos)

    if board.copper_pours:
        d["copper_pours"] = []
        for cp in board.copper_pours:
            pour_dict: dict = {"net": cp.net, "layers": cp.layers}
            if cp.keepout:
                pour_dict["keepout"] = True
            d["copper_pours"].append(pour_dict)

    return d


def write_yaml(board: BoardData, output_dir: Path | None = None) -> Path:
    """Write board data to YAML file."""
    output_dir = output_dir or OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{board.slug}.yaml"

    data = board_to_dict(board)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=_BoardDumper, default_flow_style=False, sort_keys=False, width=120)

    log.info("Wrote %s", out_path)
    return out_path


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def _extract_key_ics_from_components(components: list[Component]) -> list[str]:
    """Auto-extract key ICs from component values when BOARDS.md Key Coverage is empty.

    Scans U/IC refs, matches IC name patterns, deduplicates by family, caps at 5.
    MCU/FPGA/SoC families are prioritized over other ICs.
    """
    _SKIP_VALUES = {"DNP", "NF", "NC", "DNI", "NOFIT", "NOPOP", "",
                     "AMP", "OPAMP", "COMPARATOR", "BUFFER"}
    # IC name: 2+ uppercase letters then optional hyphen then digit
    # Matches: ESP32, BME280, STM32F103, ZED-F9P, RV-8803, MAX-M10S
    _IC_PAT = re.compile(r"^[A-Z]{2,}[-_]?[A-Z]*[-_]?[0-9]", re.IGNORECASE)
    # MCU/FPGA/SoC families — these get priority placement
    _MCU_PAT = re.compile(
        r"^(ESP32|RP2040|RP2350|STM32|nRF52|ATmega|ATSAM|LPC|PIC|GD32|"
        r"iCE40|ECP5|LFE5|GW1N|XC[0-9]|CYUSB|CY7C|CC[12]\d{3})",
        re.IGNORECASE,
    )

    def _get_family(val: str) -> str:
        family_m = re.match(r"^([A-Za-z]+\d+)", val)
        return family_m.group(1).upper() if family_m else val.upper()

    mcu_ics: list[str] = []
    other_ics: list[str] = []
    seen_families: set[str] = set()

    for comp in sorted(components, key=lambda c: c.ref):
        prefix = _get_ref_prefix(comp.ref)
        if prefix not in ("U", "IC"):
            continue
        val = comp.value.strip()
        if not val or val.upper() in _SKIP_VALUES:
            continue
        # Skip voltage regulator output values like "3.3V", "5V"
        if re.match(r"^\d+\.?\d*V\d*$", val):
            continue
        if not _IC_PAT.match(val.upper()):
            continue
        family = _get_family(val)
        if family in seen_families:
            continue
        seen_families.add(family)
        if _MCU_PAT.match(val):
            mcu_ics.append(val)
        else:
            other_ics.append(val)

    return (mcu_ics + other_ics)[:5]


def process_board(slug: str, board_info: dict, dry_run: bool = False,
                  force_clone: bool = False) -> BoardData | None:
    """Process a single board: clone → parse → write YAML."""
    fmt = board_info["format"]

    # Clone repo
    repo_dir = clone_repo(board_info["repo"], fmt, force=force_clone)

    # Find schematic file
    sch_path = repo_dir / board_info["schematic_path"]
    if not sch_path.exists():
        parent = sch_path.parent
        # Search for schematic files matching the format
        if fmt.startswith("kicad") and fmt != "kicad_legacy":
            candidates = list(parent.glob("*.kicad_sch"))
        else:
            candidates = list(parent.glob("*.sch"))
        if candidates:
            sch_path = candidates[0]
            log.warning("Exact path not found, using: %s", sch_path)
        else:
            log.error("Schematic not found: %s", sch_path)
            return None

    log.info("Parsing schematic: %s", sch_path)

    # Dispatch to format-specific parser
    positions: list[Position] = []
    outline: BoardOutline | None = None
    design_rules: DesignRules | None = None
    copper_pours: list[CopperPour] = []

    if fmt == "eagle":
        from parsers.eagle import parse_schematic, parse_board as eagle_parse_board
        components, nets = parse_schematic(sch_path)

        # Try to find matching .brd file for PCB positions + outline + design rules + pours
        brd_path = sch_path.with_suffix(".brd")
        if brd_path.exists():
            positions, outline, design_rules, copper_pours = eagle_parse_board(
                brd_path, {c.ref for c in components})
        else:
            log.info("No .brd file found, skipping positions")

    elif fmt in ("kicad6", "kicad7", "kicad8", "kicad9", "kicad10"):
        from parsers.kicad import parse_schematic as kicad_parse_sch
        from parsers.kicad import parse_pcb, enrich_from_project

        components, _ = kicad_parse_sch(sch_path, repo_root=repo_dir)

        # KiCad PCB file has same stem, different extension
        pcb_path = sch_path.with_suffix(".kicad_pcb")
        if pcb_path.exists():
            part_refs = {c.ref for c in components}
            positions, outline, design_rules, nets, copper_pours = parse_pcb(
                pcb_path, part_refs, components)
        else:
            nets = []
            log.info("No .kicad_pcb file found, skipping positions/nets")

        # Enrich from .kicad_pro (net classes, design rules)
        pro_path = sch_path.with_suffix(".kicad_pro")
        if pro_path.exists():
            design_rules = enrich_from_project(pro_path, design_rules, nets)

    elif fmt == "kicad_legacy":
        from parsers.kicad_legacy import parse_schematic as legacy_parse_sch
        from parsers.kicad import parse_pcb

        components, _ = legacy_parse_sch(sch_path)

        pcb_path = sch_path.with_suffix(".kicad_pcb")
        if pcb_path.exists():
            part_refs = {c.ref for c in components}
            positions, outline, design_rules, nets, copper_pours = parse_pcb(
                pcb_path, part_refs, components)
        else:
            nets = []
            log.info("No .kicad_pcb file found, skipping positions/nets")
        # No .kicad_pro files for legacy boards

    else:
        log.warning("Format '%s' not yet supported, skipping %s", fmt, slug)
        return None

    # Apply board-specific overrides for known source-data errors
    _apply_overrides(slug, components)

    # Apply net pin fixes
    _apply_net_pin_fixes(slug, nets)

    # Check for MPN/value conflicts
    _check_mpn_conflicts(components)

    # Post-parse circuit analysis
    annotate_circuit_roles(components, nets, positions)

    # Infer meaningful names for auto-numbered nets
    n_renamed = infer_net_names(nets)
    if n_renamed:
        log.info("Inferred names for %d auto-numbered nets", n_renamed)

    # Extract metadata from BOARDS.md Key Coverage
    key_coverage = board_info.get("key_coverage", "")
    description = build_description(key_coverage)
    tags = extract_tags(key_coverage)
    key_ics = extract_key_ics(key_coverage)

    # Apply tag overrides (replacement)
    if slug in _TAG_OVERRIDES:
        tags = _TAG_OVERRIDES[slug]

    # Apply metadata overrides
    meta = _BOARD_META_OVERRIDES.get(slug, {})
    if "key_ics" in meta:
        key_ics = meta["key_ics"]
    if "description" in meta:
        description = meta["description"]

    # Auto-populate key_ics from components if still empty
    if not key_ics:
        key_ics = _extract_key_ics_from_components(components)

    board = BoardData(
        name=board_info["name"],
        slug=slug,
        source=board_info["repo"],
        format=fmt,
        description=description,
        tags=tags,
        key_ics=key_ics,
        components=components,
        nets=nets,
        positions=positions,
        outline=outline,
        design_rules=design_rules,
        copper_pours=copper_pours,
    )

    if dry_run:
        outline_str = f", {outline.width}x{outline.height}mm" if outline else ""
        print(f"\n[DRY RUN] {board.name}: {len(components)} components, "
              f"{len(nets)} nets, {len(positions)} positions{outline_str}")
        for c in sorted(components, key=lambda c: c.ref):
            attrs = f" {c.attributes}" if c.attributes else ""
            print(f"  {c.ref}: {c.value} [{c.footprint}]{attrs}")
        return board

    write_yaml(board)
    return board


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Parse reference board schematics into YAML")
    parser.add_argument("--board", "-b", help="Board slug to process")
    parser.add_argument("--all", "-a", action="store_true", help="Process all boards from BOARDS.md")
    parser.add_argument("--list", "-l", action="store_true", help="List all boards")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Parse but don't write files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--force-clone", action="store_true", help="Force re-clone repos")
    parser.add_argument("--format", "-f", help="Filter --list/--all by format (eagle, kicad7, etc.)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    boards = parse_boards_md()
    log.info("Loaded %d boards from BOARDS.md", len(boards))

    if args.list:
        fmt_filter = args.format
        for slug, info in sorted(boards.items()):
            if fmt_filter and info["format"] != fmt_filter:
                continue
            print(f"  {slug:40s} {info['format']:12s} {info['org']}/{info['name']}")
        return

    if args.all:
        fmt_filter = args.format
        succeeded, failed, skipped = 0, 0, 0
        failures: list[tuple[str, str]] = []
        for slug, info in sorted(boards.items()):
            if fmt_filter and info["format"] != fmt_filter:
                skipped += 1
                continue
            try:
                result = process_board(slug, info, dry_run=args.dry_run,
                                       force_clone=args.force_clone)
                if result:
                    succeeded += 1
                else:
                    skipped += 1
            except Exception as e:
                failed += 1
                failures.append((slug, str(e)))
                log.error("FAILED %s: %s", slug, e)

        print(f"\n{'='*60}")
        print(f"Summary: {succeeded} succeeded, {failed} failed, {skipped} skipped")
        if failures:
            print(f"\nFailures:")
            for slug, err in failures:
                print(f"  {slug}: {err}")
        return

    if not args.board:
        parser.error("--board <slug> or --all required (use --list to see available boards)")

    slug = args.board
    if slug not in boards:
        matches = [s for s in boards if slug in s]
        if len(matches) == 1:
            slug = matches[0]
            log.info("Matched slug: %s", slug)
        elif matches:
            print(f"Ambiguous slug '{slug}', matches: {', '.join(sorted(matches))}")
            return
        else:
            print(f"Unknown board slug: '{slug}'. Use --list to see available boards.")
            return

    result = process_board(slug, boards[slug], dry_run=args.dry_run, force_clone=args.force_clone)
    if result and not args.dry_run:
        print(f"\nDone: {len(result.components)} components, {len(result.nets)} nets, "
              f"{len(result.positions)} positions")
        print(f"Output: data/boards/{result.slug}.yaml")


if __name__ == "__main__":
    main()
