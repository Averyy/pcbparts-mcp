"""Shared utilities for schematic/board parsers.

Junk filtering, description filtering, and attribute mapping used by
Eagle, KiCad, and KiCad-legacy parsers.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Junk reference filtering
# ---------------------------------------------------------------------------

# Ref prefixes that are never real components
JUNK_REF_PREFIXES = ("FRAME", "LOGO", "FID", "FD", "STANDOFF", "TP", "MH", "H")


def is_junk_ref(ref: str) -> bool:
    """Check if a reference designator indicates a non-electrical part."""
    if not ref or ref in ("?", "*"):
        return True
    # Placeholder refs like "U?" or "R?"
    if ref.endswith("?"):
        return True
    prefix = ref.rstrip("0123456789$")
    return prefix in JUNK_REF_PREFIXES


# ---------------------------------------------------------------------------
# Description filtering
# ---------------------------------------------------------------------------

# Single-word and generic descriptions to suppress
USELESS_DESCRIPTIONS = {
    "resistors", "ceramic capacitors", "capacitors", "inductors",
    "supply symbol", "pin header", "schematic frame",
    "crystals", "crystal", "diode", "diodes", "test point", "test pad",
    "led", "leds", "switch", "switches", "connector", "connectors",
    "transistor", "transistors", "mosfet",
    # KiCad library generic descriptions
    "unpolarized capacitor", "polarized capacitor",
    "resistor", "inductor", "ferrite bead",
    "light emitting diode", "fuse",
    "mounting hole with connection", "mounting hole without connection",
}

# Boilerplate prefixes in descriptions to filter
BOILERPLATE_PREFIXES = (
    "multi connection point",
    "single connection point",
    "standard 2-pin",
    "standard 3-pin",
    "standard 4-pin",
    "standard 5-pin",
    "standard 6-pin",
    "standard 7-pin",
    "standard 8-pin",
    "header 2", "header 3", "header 4", "header 5",
    "header 6", "header 7", "header 8", "header 9", "header 10",
    "sparkfun has standardized",
    "sparkfun test point",
    "sparkfun products",
    "sparkfun i2c standard pinout",
    "on any of the 0.1 inch",
    "example sparkfun products",
    "sparkfun i 2 c",
    "various fiducial",
    "for new designs",
    "special notes",
    "open source hardware",
    "led 0603", "led 0805",
    "test point", "test pad",
    "schottky diodes in sfe",
    "diodes in sfe",
    # KiCad generic library prefixes
    "generic connector",
    "bipolar transistor symbol",
    "push button switch, generic",
    "generic screw",
)


def is_useful_description(text: str) -> bool:
    """Check if a description string adds value beyond generic noise."""
    if not text or len(text) < 4:
        return False
    lower = text.lower().strip()
    if lower in USELESS_DESCRIPTIONS:
        return False
    # Filter product IDs (RES-07857, CAP-08604, etc.)
    if re.match(r"^[A-Z]{2,}-\d+$", text):
        return False
    # Filter empty labels
    if lower in ("description:", "description", ""):
        return False
    # Filter boilerplate header/connector descriptions
    for prefix in BOILERPLATE_PREFIXES:
        if lower.startswith(prefix):
            return False
    # Filter descriptions that start with a generic type then dump table/spec text
    first_word = lower.split()[0] if lower.split() else ""
    if first_word in USELESS_DESCRIPTIONS and len(lower.split()) > 2:
        return False
    return True


def truncate(text: str, max_len: int) -> str:
    """Truncate text at a word boundary, stripping URLs and literal escapes."""
    text = text.replace("\\n", " ")
    text = re.sub(r"https?://\S+", "", text).strip()
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    truncated = text[:max_len].rsplit(" ", 1)[0]
    return truncated.rstrip(" ,;:-")


# ---------------------------------------------------------------------------
# Attribute mapping
# ---------------------------------------------------------------------------

# Maps raw attribute key → our standardized key.
# Checked both exact and uppercased key. First match wins per destination key.
_ATTR_KEY_MAP = {
    # Product/part IDs
    "PROD_ID": "prod_id",
    "MANUFACTURER_PART_NUMBER": "mpn",
    "MPN": "mpn",
    "MFR": "mpn",
    "MP": "mpn",                       # SnapEDA convention
    "Part Number": "mpn",
    "PART_NUMBER": "mpn",
    # Manufacturer
    "VENDOR": "manufacturer",
    "MANUFACTURER": "manufacturer",
    "MANUFACTURER_NAME": "manufacturer",
    "MF": "manufacturer",
    "MFN": "manufacturer",            # iCEBreaker convention
    # Specs
    "TOLERANCE": "tolerance",
    "VOLTAGERATING": "voltage",
    "VOLTAGE": "voltage",
    "OPERATING_TEMP": "temp_range",
    "DESCRIPTION": "description",
    "HEIGHT": "height",
    # Supplier part numbers
    "LCSC": "lcsc",
    "JLCPCB": "lcsc",
    "LCSC Part": "lcsc",              # space-separated variant
    "LCSC_PART": "lcsc",
    "PARTNO": "partno",
    "DIGIKEY": "digikey",
    "DIGIKEY#": "digikey",
    "DK": "digikey",                   # bitaxe convention
    "DigiKey_Part_Number": "digikey",  # SnapEDA convention
    "MOUSER": "mouser",
    "MOUSER#": "mouser",
    # Legacy KiCad board conventions
    "P/N": "mpn",                      # Tigard convention
    "PN": "mpn",                       # OrangeCrab convention
    "PartNumber": "mpn",               # LibreSolar convention
    "Mfg": "manufacturer",             # OrangeCrab convention
    "mfg#": "mpn",                     # Cheap FOCer convention
}


def build_attributes(raw_attrs: dict[str, str]) -> dict[str, str]:
    """Map raw attribute keys to standardized keys.

    First match wins — so MPN takes priority over MFR if both are present.
    Keys not in the mapping are silently dropped.
    """
    result: dict[str, str] = {}
    for raw_key, value in raw_attrs.items():
        if not value or not value.strip():
            continue
        # Skip template placeholders (e.g. "template_tolerance", "${TOLERANCE}")
        v = value.strip()
        if v.startswith("template_") or v.startswith("${"):
            continue
        # Try exact match first, then uppercase
        dst = _ATTR_KEY_MAP.get(raw_key) or _ATTR_KEY_MAP.get(raw_key.upper())
        if dst and dst not in result:
            result[dst] = v
    return result
