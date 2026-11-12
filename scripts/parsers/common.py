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
JUNK_REF_PREFIXES = ("FRAME", "LOGO", "FID", "FD", "STANDOFF", "TP", "MH", "H", "Box")  # Box: an enclosure drawing (1590A)


def is_junk_ref(ref: str) -> bool:
    """Check if a reference designator indicates a non-electrical part."""
    if not ref or ref in ("?", "*"):
        return True
    # Placeholder refs like "U?" or "R?"
    if "?" in ref:
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
# Checked both exact and uppercased key; explicit identities take precedence.
_ATTR_KEY_MAP = {
    # Product/part IDs
    "PROD_ID": "prod_id",
    "MANUFACTURER_PART_NUMBER": "mpn",
    "MPN": "mpn",
    "MFR": "manufacturer",           # maker in AXIOM and AQEye sources
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


# Cached-source aliases. Keep ambiguous names explicit: Mfg is a maker,
# while uppercase MFG is an ordering code in LDO Leviathan's library.
_ATTR_KEY_MAP.update({
    "MFG": "mpn",
    "SUPPLIER": "manufacturer",  # Eagle library convention; title-case Supplier is a retailer
})
_ATTRIBUTE_ALIASES = {
    "mpn": (
        "MANF#", "MANUFACTURE #", "MANUFACTURER NO", "MANUFACTURER P/N",
        "MANUFACTURER PART", "MANUFACTURER PART NUMBER", "MANU_PART",
        "MFG PN", "MFG#", "MFGPN", "MFG_PART", "MFR PART #",
        "MFR PART NUMBER", "MFR. #", "MFR. PART#", "MFR.PART #",
        "PART #", "PART#", "PART-NUMBER", "PART NUM", "PART", "SNAPEDA_PN",
        "DESIGN MPN", "MPN1", "PN_1", "GENERIC_PART_NUMBER",
    ),
    "manufacturer": (
        "MANF", "MAND", "MANUFACTURE", "MFG_NAME", "MFR_NAME",
        "DESIGN MANUFACTURER", "VENDOR1", "MFG_1",
    ),
    "prod_id": (
        "PROD-ID", "SEEED PN", "SKU", "SF_ID", "SF_SKU", "STOREFRONT_ID",
        "STOREFRONT_SKU",
    ),
    "digikey": (
        "DIG#", "DIGI-KEY#", "DIGI-KEY PN", "DIGI-KEY_PN",
        "DIGI-KEY_PART_NUMBER", "DIGI-KEY_PART_NUMBER_1", "DIGIKEY PART NUMBER",
        "DIGIKEY_PART_NUMBER", "DIGIKEY_PART", "SPN", "DIGIKE_Y",
    ),
    "mouser": (
        "MOUSER PART NO", "MOUSER PART NUMBER", "MOUSER_PART", "MOUSER_PART_NUMBER",
        "MOUSE_PART", "MOUSE_R",
    ),
    "lcsc": (
        "LCSC#", "LCSC MPN", "LCSC PN", "LCSC PART #", "LCSC PART#",
        "JLCPCB PART #", "JLC_MPN",
    ),
    "farnell": ("FARNELL", "OC_FARNELL"),
    "newark": ("NEWARK", "OC_NEWARK"),
    "rs": ("RS_PART_NUMBER", "RS PART NUMBER"),
    "allied": ("ALLIED_NUMBER",),
    "arrow": ("ARROW PART NUMBER", "ARROW_PART_NUMBER"),
    "tme": ("TME",),
    "description": (
        "DESC", "DESCRIPTION_1", "DESIGN DESCRIPTION", "MFR DESCRIPTION",
        "PART DESCRIPTION", "SEEED DESCRIPTION", "SHORT DESCRIPTION",
        "DIGIKEY DESCRIPTION", "MOUSER DESCRIPTION",
    ),
    "voltage": ("VOLTAGE RATING", "MIN. VOLTAGE RATING", "VAUX"),
}
for _destination, _aliases in _ATTRIBUTE_ALIASES.items():
    _ATTR_KEY_MAP.update(dict.fromkeys(_aliases, _destination))


# Spec fields with no electrical identity of their own: kept under a standard key.
_ATTR_KEY_MAP.update({
    "TEMPERATURE": "temp_range",       # Blues: "-55°..+125°"
    "CLOAD": "load_capacitance",       # Antmicro crystals: "10pF"
})

# Fields whose unit-labelled tokens are ratings: Duet's Rating holds "2A", "0.2W" or a part number
# (L3's "MPZ2012S221A"); Seeed's "Power Rating" holds tolerances.
_RATING_KEYS = {"RATING", "POWER RATING", "POWER", "MIN. POWER RATING", "CURRENT", "CURRENT RATING"}
_RATING_TOKENS = (
    ("voltage", r"(?:^|[/,; ])(\d+(?:\.\d+)?)\s*V(?=$|[/,; ])", "V"),
    ("tolerance", r"(?:^|[/,; ±])(\d+(?:\.\d+)?)\s*%(?=$|[/,; ])", "%"),
    ("current", r"(?:^|[/,; ])(\d+(?:\.\d+)?\s*[mµu]?)A(?=$|[/,; ])", "A"),
    ("power", r"(?:^|[/,; ])(\d+/\d+|\d+(?:\.\d+)?\s*m?)W(?=$|[/,; ])", "W"),
)

# Zero-width and bidirectional marks copied in from distributor pages: HEEV's DigiKey numbers
# ended in U+200E, OrangeCrab's makers were wrapped in it.
_INVISIBLE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")


def clean_text(text: str) -> str:
    """Text without invisible marks, non-breaking spaces as spaces."""
    return _INVISIBLE.sub("", text).replace("\u00a0", " ") if text else text


def value_or_symbol(value: str, symbol: str, footprint: str = "") -> str:
    """The placed value, or the symbol's (deviceset's) name when it is empty or KiCad's empty "~".

    A fitted part with no value is still on the board: PocketPD's BOOT button SW5 and
    OpenAirScope's RF-match capacitors C53/C54 were dropped with their nets for having none.
    An unvalued part on a test-point footprint stays a test point (the guitar pedals' wiring pads).
    """
    if value and value.strip() not in ("", "~"):
        return value
    if re.match(r"^(?:[\w.-]+:)?TestPoint", footprint or ""):
        return "test point"
    name = symbol.split(":", 1)[-1].strip() if symbol else ""
    return name or value


# Package names that follow a slash in a value ("1N4148W/SOD123"), not part of an ordering code
_PACKAGE_WORD = r"(?:SOD|SOT|SMA|SMB|SMC|DO|SOIC|SOP|SSOP|TSSOP|MSOP|QFN|DFN|QFP|LQFP|TQFP|BGA|TO|DIP|SON)"
# Library symbol and deviceset names, which look like part numbers but name a generic part
_GENERIC_NAME = re.compile(r"^(?:PINHD|HEADER|CONN|JUMPER|SOLDERJUMPER|TEST|TP|LED|RES|CAP|IND|FUSE|DIODE|"
                           r"MOSFET|SWITCH|MOMENTARY|RELAY|CRYSTAL|XTAL|TRANS|PAD|FIDUCIAL|MOUNT|USB|HDMI|SENSOR|"
                           r"NPN|PNP)[-_]", re.IGNORECASE)
# A package named after the part: BAT54S-SOT-23-3, ADS1292R-TQFP, a 5.2MM body
_PACKAGE_SUFFIX = re.compile(r"[-_](?:SOT|SOD|TQFP|LQFP|QFN|SOIC|SSOP|TSSOP|MSOP|DFN|BGA)(?:[-_]?\d|$)|"
                             r"\d(?:\.\d+)?MM(?![A-Z])", re.IGNORECASE)
# Package names, as Olimex writes them in parentheses after the part: BAT54C(SOT23-3), (SOD-123)
_PACKAGE_NAME = re.compile(r"^(?:SOD|SOT|SOIC|SOP|SSOP|TSSOP|HTSSOP|MSOP|QFN|DFN|QFP|LQFP|TQFP|BGA|TO|DIP|SON|"
                           r"USON|WSON|VQFN|UQFN|LGA|PLCC|WLCSP|TSOT|SC-?70)[-_]?\d|^DO-\d", re.IGNORECASE)


def looks_like_part_number(token: str) -> bool:
    """A manufacturer ordering code: one token of letters and digits (M95256-WMN6P, 2920L110/60MR,
    MCP73831-2ACI/MC), not an electrical value (10uF-16V), a value list (Q12MHz/20pF), a symbol name
    (Conn_01x04, PINHD-1X9) or a part with its package (1N4148W/SOD123). Würth numbers are all
    digits (74405042022)."""
    if re.fullmatch(r"\d{8,14}", token):
        return True
    if not 6 <= len(token) <= 40 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+/#,=-]*", token):
        return False
    if "/" in token:
        # One ordering suffix after a slash (/NOPB, /TR, MCP73831-2ACI/MC; a Littelfuse PTC's 2920L110/60MR),
        # not a value list (Olimex's FB0805/600R/2A, 4.7M/R0402, 150p/NP0)
        head, _, tail = token.rpartition("/")
        if "/" in head or not re.fullmatch(r"[A-Z0-9]{1,5}", tail):
            return False
        return bool(re.fullmatch(r"\d{4}L\d{3,4}", head)) or looks_like_part_number(head)
    if sum(c.isdigit() for c in token) < 2 or sum(c.isalpha() for c in token) < 2:
        return False
    if token.upper() != token and not re.search(r"[A-Z]{2}", token):
        return False
    if re.match(r"\d+(?:\.\d+)?\s*[pnuµμmkKMG]?(?:F|H|Ω|ohms?|R|V|A|W|Hz)\b", token, re.IGNORECASE):
        return False
    if re.search(r"\d(?:[pnuµμm](?:F|H)|[kMG]?Hz|ppm)\b", token):  # case-sensitive: 20pF, 12MHz, 10ppm
        return False
    if re.search(rf"/{_PACKAGE_WORD}\d", token, re.IGNORECASE) or _GENERIC_NAME.match(token):
        return False
    if _PACKAGE_NAME.match(token) or re.fullmatch(r"\d{4}[A-Za-z]+", token):  # SOT23-5, 0402LED
        return False
    if re.search(r"\dx\d", token) or re.search(r"[a-z]{3}", token):  # 6x3,8x2,5MM; CC1352P-LeashPCB
        return False
    if _PACKAGE_SUFFIX.search(token):
        return False
    return True


def keep_source_specs(raw: str, value: str, ref: str, attrs: dict[str, str]) -> None:
    """Keep what normalizing the placed value discarded: the part number it was decoded or shortened
    from, and ratings it spelled out.

    dc-poe-injector's F1 "2920L110/60MR" became "1.1A PTC" with its 60 V rating and part number gone;
    OpenAirScope's U6 "M95256-WMN6P" became "M95256"; Olimex's "Q12MHz/20pF/10ppm/..." crystals kept
    only 12MHz. The value stays as normalized; the part number goes to mpn when the source gave none.
    Called with normalize_value's result, before a connector's value becomes "1x4 header" from its
    footprint: a connector's value often names what plugs in (HEEV's "TMC4671 USART").
    """
    raw = clean_text(raw or "").strip()
    if not raw or raw == value:
        return
    # A Littelfuse PTC code ends in its maximum voltage: 2920L110/60MR is 1.1 A hold, 60 V
    fuse = re.match(r"^\d{4}L\d{3,4}/(\d+)", raw, re.IGNORECASE)
    if fuse:
        attrs.setdefault("voltage", f"{fuse.group(1)}V")
    # A frequency's stability spelled into the value (Olimex: "Q12MHz/20pF/10ppm/4P/3.2x2.5mm")
    if re.match(r"^\d+(?:\.\d+)?\s*[kMG]?Hz\b", value):
        ppm = re.search(r"(?:^|[/\s(])(\d+(?:\.\d+)?)\s*ppm\b", raw, re.IGNORECASE)
        if ppm:
            attrs.setdefault("tolerance", f"{ppm.group(1)}ppm")
    if attrs.get("mpn") or value in ("", "DNP", "NC", "test point", "logo", "pad", "mounting hole", "FIDUCIAL"):
        return
    candidates: list[str] = []
    # One trailing parenthesis: Olimex's "...(ABM8-12.000MHZ-D2Y-T)", "8MHz 10ppm (X50328MSB2GI)";
    # not "39k (LT8361) 52.3k (LT8362)", which names the alternative builds
    paren = re.search(r"\(([^()]+)\)\s*$", raw) if raw.count("(") == 1 else None
    if paren and looks_like_part_number(paren.group(1).strip()):
        candidates = [paren.group(1).strip()]
    else:
        head = re.sub(r"\([^()]*\)\s*$", "", raw).strip()
        tokens = head.split()
        if len(tokens) == 1:
            # Soldered's value-then-part-number convention: "4u7-TMK212AB7475KG-T"
            soldered = re.match(r"^\d+(?:\.\d+)?[pnuµμmkKMGRr]\d*-([A-Z][A-Z0-9].+)$", tokens[0])
            tokens = [soldered.group(1)] if soldered else tokens
        elif not re.match(r"^(?:R|C|L|FB|F|PTC|FUSE)\d", ref, re.IGNORECASE):
            tokens = []  # several words on an IC or connector are a label, not a part number
        candidates = [t for t in tokens if looks_like_part_number(t)]
    if len(candidates) != 1:
        return
    part = candidates[0]
    if part.upper() == value.upper():
        return
    # A unit is not an ordering suffix: ProtoCentral's "AP2112K-3.3V" is the value AP2112K-3.3
    if re.fullmatch(re.escape(value) + r"\s*V", part, re.IGNORECASE) and value[-1:].isdigit():
        return
    attrs["mpn"] = part


def _attribute_destination(key: str, raw_attrs: dict[str, str]) -> str | None:
    # A Seeed internal PN is distinct from the explicitly named manufacturer PN.
    if key.upper() == "PN" and any(k.upper() == "MANUFACTURER PART NUMBER" for k in raw_attrs):
        return "prod_id"
    # Supplier numbers only have meaning together with their supplier's name.
    supplier_keys = {
        "SUPPLIER P/N": "Supplier", "SUPPLIER PART": "Supplier",
        "SUPPLIER PN": "Supplier", "DESIGN ORDER CODE": "Design Supplier",
        "DIST_ID": "DIST",
    }
    if key.upper() in supplier_keys:
        supplier = raw_attrs.get(supplier_keys[key.upper()], "").strip().lower().replace("-", "")
        destination = {"digikey": "digikey", "mouser": "mouser", "lcsc": "lcsc", "tme": "tme"}.get(supplier)
        if destination:
            return destination
        number = raw_attrs[key].strip()
        if number.upper().endswith("-ND"):
            return "digikey"
        if re.fullmatch(r"C\d{3,}", number):
            return "lcsc"
        return "partno"
    # Unlike the all-uppercase Eagle convention, these name the retailer.
    if key in ("Supplier", "supplier"):
        return None
    return _ATTR_KEY_MAP.get(key) or _ATTR_KEY_MAP.get(key.upper().strip())


def _attribute_priority(key: str, dst: str) -> int:
    key = key.upper().strip()
    # A numbered alternate (PN_1, Mfg_1) is a second source: OrangeCrab J3 lists GCT USB4105-GF-A
    # as Mfg/PN and an LCSC code as PN_1, and the alternate's maker had replaced the primary.
    if re.search(r"_\d+$", key):
        return -1
    if dst == "mpn":
        return 0 if key in ("PN", "PART NUMBER", "PART_NUMBER", "PARTNUMBER", "P/N", "PART", "MPN1") else 1
    if dst == "manufacturer":
        return 0 if key in ("VENDOR", "SUPPLIER", "VENDOR1") else 1
    if dst == "description":
        return 2 if key == "DESCRIPTION" else (1 if key == "DESIGN DESCRIPTION" else 0)
    return 0


def build_attributes(raw_attrs: dict[str, str], property_aliases: dict | None = None,
                     ref: str = "") -> dict[str, str]:
    """Map raw attribute keys to standardized keys.

    Explicit manufacturer part numbers outrank generic PN/internal codes,
    independently of property order. Equal-priority aliases keep the first value.
    Keys not in the mapping are silently dropped.
    """
    if property_aliases:
        raw_attrs = raw_attrs.copy()
        aliases = {**property_aliases.get("*", {}), **property_aliases.get(ref, {})}
        for source, target in aliases.items():
            value = raw_attrs.get(source, "").strip()
            if target == "PART_OR_SPECS":
                target = "MPN" if re.fullmatch(r"(?=.*[A-Za-z])(?=.*\d)[\w.+/=,#-]{5,}", value) else "Description"
            if value.lower() not in {"nf", "dnp", "unavailable", "general", "genaral", "general inductor"}:
                raw_attrs.setdefault(target, value)
    raw_attrs = {k: clean_text(v) if isinstance(v, str) else v for k, v in raw_attrs.items()}
    result: dict[str, str] = {}
    rating_part = ""
    # Mixed Rating fields contain volts, percent, watts or amps depending on
    # the part. Only extract explicitly unit-labelled tokens; a bare part number
    # there (Duet L3's "MPZ2012S221A") is the part's MPN when nothing else names one.
    for key, value in raw_attrs.items():
        if key.upper() not in _RATING_KEYS or not value:
            continue
        for dst, pattern, unit in _RATING_TOKENS:
            match = re.search(pattern, value, re.IGNORECASE)
            if match:
                result.setdefault(dst, re.sub(r"\s+", "", match[1]) + unit)
        if looks_like_part_number(value.strip()):
            rating_part = rating_part or value.strip()
    priorities: dict[str, int] = dict.fromkeys(result, -1)
    for raw_key, value in raw_attrs.items():
        if not value or not value.strip():
            continue
        # Skip template placeholders (e.g. "template_tolerance", "${TOLERANCE}")
        v = value.strip()
        if v.startswith("template_") or v.startswith("${") or v.lower() in {"~", "n/a", "none", "unknown", "null"}:
            continue
        # Try exact match first, then uppercase
        dst = _attribute_destination(raw_key, raw_attrs)
        # A dimension needs a magnitude: some Eagle libraries use HEIGHT="mm".
        if dst == "height" and re.fullmatch(r"mm|cm|m|mils?|in(?:ch(?:es)?)?|[uµμ]m", v, re.IGNORECASE):
            continue
        if dst == "voltage":
            # KiCad's "Voltage Rating" often appends a dielectric after a comma.
            rating = re.fullmatch(r"(\d+(?:\.\d+)?)\s*V(?:[,/].*)?", v, re.IGNORECASE)
            if rating:
                v = rating[1] + "V"
        priority = _attribute_priority(raw_key, dst) if dst else 0
        if dst and (dst not in result or priority > priorities[dst]):
            result[dst] = v
            priorities[dst] = priority
    if rating_part:
        result.setdefault("mpn", rating_part)
    return result


# These carry electrical values in cached KiCad designs, but "id" and "Val"
# can also be arbitrary identifiers. Never treat them as unconditional values.
_VALUE_PROPERTY_KEYS = {"ID", "VAL", "RESISTANCE", "INDUCTANCE", "CAPACITANCE", "RVALUE", "CATV"}


def value_from_properties(value: str, ref: str, raw_attrs: dict[str, str],
                          attrs: dict[str, str], symbol: str = "") -> str:
    """Recover an electrical value when the placed Value holds an ordering code or the symbol's
    own name: Duet's X2 is CRYSTAL_4PIN with Frequency=12MHz. A symbol name isn't a part number."""
    prefix = re.match(r"[A-Za-z]+", ref)
    if not prefix or prefix[0].upper() not in {"R", "C", "L", "FB", "Y", "X"}:
        return value
    prefix = prefix[0].upper()
    keys = _VALUE_PROPERTY_KEYS | ({"FREQUENCY"} if prefix in ("Y", "X") else set())
    generic = (bool(symbol) and value.strip().upper() == symbol.split(":", 1)[-1].strip().upper()
               and not looks_like_part_number(value.strip()))
    units = {"R": r"(?:[mkKMGR]|[mkKM]?ohm|[mkM]?Ω)?",
             "C": r"[pnuµμm]F?", "L": r"[pnuµμm]H?",
             "FB": r"(?:[kK]?ohm|[kKRZ])", "Y": r"[kKM]?Hz", "X": r"[kKM]?Hz"}
    scalar = rf"(?:\d+(?:\.\d+)?|\.\d+)\s*{units[prefix]}"
    embedded = r"\d+[RkKM]\d+" if prefix == "R" else r"\d+[pnuµμm]\d+"
    def electrical(v: str) -> bool:
        return bool(re.fullmatch(rf"(?:{scalar}|{embedded})", v.strip(), re.IGNORECASE))
    # A concrete ordering code (letters and digits, or a Würth all-digit number such as MTE's L3
    # 74405042022) or the symbol's own name, not an already electrical value.
    ordering_code = re.fullmatch(r"\d{8,14}", value.strip()) or (
        len(value) >= 5 and re.fullmatch(r"[\w.+/=,#-]+", value) and re.search(r"[A-Za-z]", value)
        and re.search(r"\d", value))
    if electrical(value) or not (generic or ordering_code):
        return value
    for key, candidate in raw_attrs.items():
        if key.upper() in keys and electrical(candidate):
            if not generic:
                attrs.setdefault("mpn", value.strip())
            return candidate.strip()
    return value
