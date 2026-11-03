"""Component type and mounting type extraction for smart query parsing."""

import re

from ..subcategory_aliases import ISOLATED_SIBLINGS, SUBCATEGORY_ALIASES, UNAVAILABLE_SUBCATEGORY_ALIASES


# Pre-sorted by length (longest first) for correct matching
_SUBCATEGORY_KEYWORDS_BY_LENGTH = sorted([*SUBCATEGORY_ALIASES, *UNAVAILABLE_SUBCATEGORY_ALIASES], key=len, reverse=True)

PD_ROLE_PATTERN = re.compile(r'\b(?:controllers?|sinks?|sources?|triggers?|receivers?|negotiat\w*)\b', re.IGNORECASE)
_PD_MARKER = re.compile(r'\b(?:pd|power[-\s]+delivery)\b', re.IGNORECASE)
_PD_INTERFACE = re.compile(r'\b(?:usb(?:[-\s]*(?:type[-\s]*)?c)?|type[-\s]*c)\b', re.IGNORECASE)

# Words and LED controller families that make an LED an addressable one (RGB LEDs(Built-in IC)).
_PLAIN_LED_KEYWORDS = frozenset({"led", "leds", "smd led", "indicator led", "rgb led"})
# The words are taken out of the text; part numbers (YS-SK6812MINI-E) stay in it.
_ADDRESSABLE_LED_MODEL = re.compile(r'(?:ws28|skc?68|sk98|apa10)\d', re.IGNORECASE)
_ADDRESSABLE_LED_WORDS = re.compile(
    r'\b(?:(?:individually\s+)?addressable|smart|intelligent|neo\s*pixels?|built[-\s]*in\s+ic)\b', re.IGNORECASE)
_ISOLATED_WORD = re.compile(r'\bisolated\b', re.IGNORECASE)
# "74HC132 quad NAND schmitt", "quad NAND gate": a NAND or NOR among gate words or with a 74/4000
# logic part number is a logic gate. Bare "nand" meant NAND FLASH, so these searched memory.
_GATE_FUNCTION = re.compile(r'\b(?:x?nor|n?and|x?or)[\s-]+gates?\b|\b(?:nand|x?nor|xor)\b', re.IGNORECASE)
_GATE_CONTEXT = re.compile(
    r'\b(?:gates?(?![\s-]*driv)|schmitt|single|dual|triple|quad|hex|octal|\d[\s-]*inputs?)\b', re.IGNORECASE)
_LOGIC_FAMILY = re.compile(r'^(?:[a-z]{0,4}74[a-z]{0,6}\d|(?:cd|hef|mc1)4\d{3})', re.IGNORECASE)
_MEMORY_CONTEXT = re.compile(r'\b(?:flash|memory|eeprom|q?spi|qpi|\d+\s*[kmg](?:bit|b))\b', re.IGNORECASE)
_PART_TOKEN = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*', re.IGNORECASE)
_NOT_PART_NUMBER = re.compile(r'^(?:\d+(?:\.\d+)?[a-z]+|\d-inputs?)$', re.IGNORECASE)  # "100mA", "74HC", "2-input"


def _logic_part_numbers_only(query: str, model: str | None) -> bool:
    """The query's part numbers, if any, are 74/4000-series logic ("W25Q128 quad NOR" is flash)."""
    tokens = [model] if model else [t for t in _PART_TOKEN.findall(query) if len(t) >= 4
                                     and re.search(r'\d', t) and re.search(r'[a-z]', t, re.IGNORECASE)
                                     and not _NOT_PART_NUMBER.match(t)]
    return all(_LOGIC_FAMILY.match(t) for t in tokens)
_NON_ISOLATED = re.compile(r'\bnon[-\s]?isolated\b', re.IGNORECASE)


def extract_component_type(
    query: str, *, memory_is_spec: bool = False, model: str | None = None,
) -> tuple[str | None, str, str | None]:
    """Extract component type from query.

    Args:
        query: The search query string
        model: Model number already taken out of the query, if any

    Returns:
        Tuple of (subcategory_name, remaining_query, matched_keyword)
    """
    # A requested PD controller role wins over the connector/interface spelling.
    # Bare PD is ambiguous; require a role rather than adding a global PD alias.
    if _PD_MARKER.search(query) and PD_ROLE_PATTERN.search(query):
        remaining = _PD_INTERFACE.sub(' ', _PD_MARKER.sub(' ', query))
        return "usb pd", re.sub(r'\s+', ' ', remaining).strip(), "usb pd"

    # A BOM's D reference describes an LED as a diode. Preserve the more specific
    # LED keyword (including RGB/IR variants) instead of letting the longer word win.
    if re.search(r'\bleds?\b', query, re.IGNORECASE) and re.search(r'\bdiodes?\b', query, re.IGNORECASE):
        query = re.sub(r'\bdiodes?\b', ' ', query, flags=re.IGNORECASE)
    # Likewise a RESPACK footprint is a resistor network, more specific than the R's "resistor".
    if re.search(r'\brespacks?\b', query, re.IGNORECASE):
        query = re.sub(r'\bresistors?\b', ' ', query, flags=re.IGNORECASE)
    # "non-isolated DC-DC module" is the plain kind; the isolated keywords would match inside it
    non_isolated = bool(_NON_ISOLATED.search(query))
    if non_isolated:
        query = _NON_ISOLATED.sub(' ', query)
    query_lower = query.lower()

    if (_GATE_FUNCTION.search(query) and not _MEMORY_CONTEXT.search(query)
            and _logic_part_numbers_only(query, model)
            and (_GATE_CONTEXT.search(query)
                 or any(_LOGIC_FAMILY.match(t) for t in [*_PART_TOKEN.findall(query), *([model] if model else [])]))):
        # The gate words stay in the text: the parser reads them as Logic Gates specs
        remaining = re.sub(r'\blogic\b', ' ', query, flags=re.IGNORECASE)
        return "logic gates", re.sub(r'\s+', ' ', remaining).strip(), "logic gate"

    # Resettable modifiers can be separated from "fuse" by ratings or packages.
    resettable = re.compile(r'\b(?:ptc|poly\s*fuse|polyswitch|resettable)\b', re.IGNORECASE)
    if re.search(r'\bfuses?\b', query_lower) and resettable.search(query_lower):
        remaining = resettable.sub(' ', query)
        remaining = re.sub(r'\bfuses?\b', ' ', remaining, flags=re.IGNORECASE)
        return "resettable fuses", re.sub(r'\s+', ' ', remaining).strip(), "resettable fuse"

    for keyword in _SUBCATEGORY_KEYWORDS_BY_LENGTH:
        # A controller without PD is not enough to infer a Type-C connector.
        if keyword in ("usb c", "usbc", "type c", "typec") and re.search(r'\b(?:pd|controller)\b', query_lower):
            continue
        if memory_is_spec and keyword in ("flash", "nor flash", "nand", "nand flash", "sram", "psram"):
            continue
        # Use word boundaries to avoid "sram" matching inside "PSRAM"
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        if pattern.search(query_lower):
            # "addressable RGB LED": the modifier can be separated from "led" by "RGB",
            # which would pick plain RGB LEDs (no controller) and drop the word.
            # "WS2812B LED" arrives with the model already taken out, so it comes as `model`.
            if keyword in _PLAIN_LED_KEYWORDS and (
                    _ADDRESSABLE_LED_WORDS.search(query_lower) or _ADDRESSABLE_LED_MODEL.search(query_lower)
                    or (model and _ADDRESSABLE_LED_MODEL.match(model))):
                remaining = _ADDRESSABLE_LED_WORDS.sub(' ', pattern.sub(' ', query))
                remaining = re.sub(r'\brgb\b', ' ', remaining, flags=re.IGNORECASE)
                return "rgb leds(built-in ic)", re.sub(r'\s+', ' ', remaining).strip(), "addressable led"
            target = SUBCATEGORY_ALIASES.get(keyword) or UNAVAILABLE_SUBCATEGORY_ALIASES[keyword]
            # "isolated 5V to 12V DC-DC converter": the modifier isn't next to the part word, which
            # would search plain buck ICs and drop "isolated" as text no part matched
            if not non_isolated and target in ISOLATED_SIBLINGS and _ISOLATED_WORD.search(query_lower):
                isolated_keyword = ISOLATED_SIBLINGS[target]
                remaining = _ISOLATED_WORD.sub(' ', pattern.sub(' ', query))
                return SUBCATEGORY_ALIASES[isolated_keyword], re.sub(r'\s+', ' ', remaining).strip(), isolated_keyword
            # Remove the keyword from query
            remaining = pattern.sub('', query).strip()
            remaining = re.sub(r'\s+', ' ', remaining)
            return target, remaining, keyword

    return None, query, None


# Mounting type patterns: PTH/THT -> Through Hole, SMD/SMT -> SMD
_MOUNTING_TYPE_PATTERNS = [
    (re.compile(r'\b(PTH|THT|through[- ]?hole|leaded)\b', re.IGNORECASE), "Through Hole"),
    (re.compile(r'\b(SMD|SMT|surface[- ]?mount)\b', re.IGNORECASE), "SMD"),
]


def extract_mounting_type(query: str) -> tuple[str | None, str]:
    """Extract mounting type from query.

    Args:
        query: The search query string

    Returns:
        Tuple of (mounting_type, remaining_query)
        Where mounting_type is "SMD" or "Through Hole" or None.
    """
    for pattern, mount_type in _MOUNTING_TYPE_PATTERNS:
        match = pattern.search(query)
        if match:
            remaining = query[:match.start()] + query[match.end():]
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            return mount_type, remaining
    return None, query
