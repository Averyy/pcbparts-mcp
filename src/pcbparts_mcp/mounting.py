"""Mounting type detection for electronic component packages."""

import re

# Categories that are NOT PCB-mountable components - return "not_applicable" for these
NON_PCB_CATEGORIES = frozenset({
    "Building materials / Building hardware",
    "Consumables and auxiliary materials",
    "Development Boards & Tools",
    "Hardware Fasteners",
    "Lathes and accessories",
    "Office Daily Use",
    "Pneumatic/hydraulic/valves/pumps",
    "Tool Equipment",
    "Wires and cables",
})

# Category/subcategory name patterns (highest priority - these are authoritative)
# Note: "Feed Through" is about signal path, not mounting. "Hot-dip" is coating process.
CATEGORY_SMD_PATTERNS = frozenset({
    "SMD", "SMT", "SURFACE MOUNT",
})

CATEGORY_THROUGH_HOLE_PATTERNS = frozenset({
    "THROUGH HOLE", "THROUGH-HOLE",
    # Note: "DIP" is NOT included here - "DIP Switches" refers to switch style, not mounting
    # Note: "Plugin" at category level is ambiguous - handled at package level instead
})

# SMD package patterns for mounting type detection
SMD_PATTERNS = frozenset({
    # Common SMD package prefixes
    "0201", "0402", "0603", "0805", "1206", "1210", "1812", "2010", "2512",  # Imperial sizes
    "01005", "008004",  # Tiny sizes
    "SOT", "SOD", "SOP", "SOIC", "SSOP", "TSSOP", "TSOP", "MSOP",  # Small outline
    "SO-",  # Small outline (SO-8, SO-14, etc.)
    "QFP", "TQFP", "LQFP", "PQFP", "VQFP", "SQFP",  # Quad flat
    "QFN", "DFN", "MLF", "SON", "WSON", "UDFN", "VDFN",  # No-lead
    "BGA", "CSP", "WLCSP", "FCBGA", "FBGA", "PBGA", "UBGA",  # Ball grid array
    "LGA", "PLCC",  # Land grid, chip carrier
    "TO-252", "TO-263", "TO-277", "DPAK", "D2PAK", "D3PAK",  # Power SMD
    "DO-214", "DO-218", "SMA", "SMB", "SMC",  # Diode SMD
    "SC-70", "SC-74", "SC-88", "SC-89",  # Small chip
    "LL-34", "LL-41", "MINIMELF", "MELF",  # Leadless cylindrical (MiniMELF)
    "MC-306", "MC-146", "MC-156", "DT-26", "DT-38",  # SMD crystal packages
    "CASE-",  # Tantalum capacitor SMD packages (CASE-A, CASE-B, CASE-C, etc.)
    "EIA-",  # EIA standard SMD packages (EIA-3216, etc.)
    "MBS", "MBF", "DBS",  # SMD bridge rectifiers (MBS = TO-269AA; also SMBF, TMBF, LMBS-1)
    # Read as not_sure before: about 2,000 stocked parts in these SMD families
    "LCC",  # Leadless chip carrier modules (A7670E: LCC-124)
    "TOLL", "HSOF", "POWERPAK", "POWERDI", "POWER-DI", "PRPAK",  # Power SMD (TOLL-8, PowerPAK1212-8)
    "SC70", "SC-59",  # Small chip without the SC- hyphen, and SC-59 (SOT-346)
    "WLP",  # Wafer-level packages (WLP-16)
    "DO-221",  # SMD power diodes (DO-221AC)
    "UMSB", "ABS",  # SMD bridge rectifiers
})

# Package families that are always surface mount, checked BEFORE the through-hole
# patterns because a through-hole token can sit inside them: "SIP" in TI's USIP
# (MicroSiP), "R-1" in "VQFN-HR-12" (TI's HotRod QFN), "R-6" in "UCSPR-6".
SMD_FIRST_PATTERNS = (
    "QFN", "DFN", "SON", "BGA", "CSP", "LGA",
    "USIP", "MICROSIP", "PICOSTAR",
)

# Through-hole package patterns
THROUGH_HOLE_PATTERNS = frozenset({
    "DIP", "PDIP", "CDIP", "CERDIP",  # Dual in-line
    "SIP",  # Single in-line
    "TO-92", "TO-126", "TO-220", "TO-247", "TO-264", "TO-3",  # Power through-hole
    "DO-41", "DO-35", "DO-201", "DO-15", "DO-27",  # Diode through-hole (axial)
    "DO-247", "P600",  # Through-hole power diodes (DO-247-2, axial P600)
    "TO-18", "TO-39", "TO-46", "TO-56",  # Metal-can photodiodes and laser diodes
    "PIN", "THT", "AXIAL", "RADIAL",  # Generic through-hole
    "PLUGIN",  # JLCPCB uses "Plugin" for through-hole parts
    "P=",  # Pitch specification (e.g., "P=2.54mm") indicates through-hole connectors
    "HC-49", "HC-50", "HC-51", "HC-52",  # Crystal packages (through-hole)
    "THROUGH HOLE", "THROUGH-HOLE",  # Explicit through-hole designation
    "PUSH-PULL",  # Push-pull headers are typically through-hole
    # Bridge rectifier packages (through-hole). MBS, MBF and DBS are SMD: see SMD_PATTERNS.
    "KBP", "KBL", "KBU", "KBPC", "GBU", "GBJ", "BR-", "GBL", "GBP", "KBJ",
    # Chinese through-hole indicators
    "插件",  # "chājian" = plugin/through-hole
    "弯插",  # "wān chā" = bent pin (through-hole)
    "直插",  # "zhí chā" = straight pin (through-hole)
})

# Axial diode packages R-1 and R-6 (incl. "R-6(P600)"), matched as whole tokens:
# as substrings they hit "VQFN-HR-12", "PicoStar-6", "SC-74R-6" and "UCSPR-6".
_THROUGH_HOLE_TOKEN = re.compile(r"(?<![A-Z0-9])R-[16](?![0-9])")


def detect_mounting_type(
    package: str | None,
    category: str | None = None,
    subcategory: str | None = None,
) -> str:
    """Determine mounting type based on category, subcategory, and package patterns.

    Priority order:
    1. Check if category is non-PCB (return "not_applicable")
    2. Subcategory name (most specific, e.g., "Through Hole Resistors")
    3. Category name (if it has mounting hint)
    4. Package name patterns (e.g., "DIP-8", "0402")
    5. Default to "not_sure" if no pattern matches

    Args:
        package: Package name/size string (e.g., "0402", "DIP-8", "LQFP48")
        category: Primary category name (e.g., "Resistors")
        subcategory: Subcategory name (e.g., "Through Hole Resistors")

    Returns:
        "smd" for surface mount, "through_hole" for through-hole,
        "not_sure" if uncertain, "not_applicable" if not a PCB-mountable component.
    """
    # Check if this is a non-PCB category (heat sinks, cables, tools, etc.)
    if category and category in NON_PCB_CATEGORIES:
        return "not_applicable"

    # Check subcategory first (most authoritative)
    if subcategory:
        sub_upper = subcategory.upper()
        # Check through-hole patterns first (more specific match needed)
        for pattern in CATEGORY_THROUGH_HOLE_PATTERNS:
            if pattern in sub_upper:
                return "through_hole"
        # Check SMD patterns
        for pattern in CATEGORY_SMD_PATTERNS:
            if pattern in sub_upper:
                return "smd"

    # Check category name
    if category:
        cat_upper = category.upper()
        for pattern in CATEGORY_THROUGH_HOLE_PATTERNS:
            if pattern in cat_upper:
                return "through_hole"
        for pattern in CATEGORY_SMD_PATTERNS:
            if pattern in cat_upper:
                return "smd"

    # Fall back to package-based detection
    if not package:
        return "not_sure"  # No package info available

    pkg_upper = package.upper()

    # Check for explicit "SMD" or "SMT" markers first - these are authoritative
    # e.g., "SMD,P=1.27mm" should be SMD even though it contains "P="
    if "SMD" in pkg_upper or "SMT" in pkg_upper:
        return "smd"

    for pattern in SMD_FIRST_PATTERNS:
        if pattern in pkg_upper:
            return "smd"

    # Check for explicit through-hole patterns
    for pattern in THROUGH_HOLE_PATTERNS:
        if pattern in pkg_upper:
            return "through_hole"
    if _THROUGH_HOLE_TOKEN.search(pkg_upper):
        return "through_hole"

    # Check for SMD patterns
    for pattern in SMD_PATTERNS:
        if pattern in pkg_upper:
            return "smd"

    # Packages starting with numbers are usually SMD metric/imperial sizes
    if pkg_upper and pkg_upper[0].isdigit():
        return "smd"

    # No pattern matched - return unknown instead of guessing
    return "not_sure"


# JLCPCB's English package field keeps some Chinese words and full-width characters: 2,975 parts
# read "插件,12.6x4.4mm" beside "Plugin" (C2681581), so a BOM's package column and package filters
# saw two spellings. They become the words the English listings already use.
_PACKAGE_WORDS = (
    ("插件", "Plugin"),  # "plug-in": through-hole
    ("直插", "Plugin"),  # "straight plug-in"
    ("交错脚", "Staggered pins"),  # English listings: "Plugin,P=1.27mm(Staggered pins)"
    ("卧贴", "Right Angle"),  # SMD lying flat, as in "SMD,P=0.5mm,Surface Mount,Right Angle"
    ("立贴", "Vertical"),  # SMD standing up
    ("母头", "Female"),
    ("公头", "Male"),
    ("插头", "Plug"),
    ("螺栓", "Bolt"),
    ("，", ","),  # full-width comma: "Surface Mount，Right Angle" on 17,370 SMD connectors
    ("×", "x"),
)
# Cyrillic capitals that look Latin: "SOТ23-6" (C5371028) matched no SOT23-6 filter
_CYRILLIC_LOOKALIKES = str.maketrans("АВСЕНКМОРТХ", "ABCEHKMOPTX")


def english_package(package: str | None) -> str | None:
    """A package string in the English listings' own words ("插件,12.6x4.4mm" → "Plugin,12.6x4.4mm").

    "弯插" ("bent plug-in", right-angle through-hole) becomes Plugin with ",Right Angle" at the end.
    Words with no English listing (colours, "15寸卷盘编带封装") stay as they are.
    """
    if not package or package.isascii():
        return package
    if package.startswith("弯插"):
        package = f"Plugin{package[2:]},Right Angle"
    for chinese, english in _PACKAGE_WORDS:
        package = package.replace(chinese, english)
    return package.translate(_CYRILLIC_LOOKALIKES)


# english_package's words back to JLCPCB's: each swap is tried on and off, then kept only if it
# translates back ("SMD,7.7x3.6mm,Right Angle" may be "SMD,7.7x3.6mm,卧贴" upstream). "×" and Cyrillic
# letters (one part each) aren't swapped back, which would double every package with an x or a T;
# the catalog's package_spellings table has them.
_PACKAGE_SWAPS = (
    ("Staggered pins", "交错脚"),
    ("Surface Mount,Right Angle", "Surface Mount，Right Angle"),
    (",Right Angle", ",卧贴"),
    (".Right Angle", ".卧贴"),  # "SMD,P=0.5mm.卧贴"
    (",Vertical", ",立贴"),
    ("Bolt", "螺栓"),
)
_WHOLE_PACKAGES = {"Female": "母头", "Male": "公头", "Plug": "插头"}


def jlcpcb_package_spellings(package: str) -> list[str]:
    """The spellings JLCPCB's live search may use for a package english_package gives, without the
    catalog: low- and out-of-stock parts aren't in it ("Plugin,12.6x4.4mm" is also "插件,12.6x4.4mm").
    English first; only spellings that english_package turns back into it."""
    english = english_package(package) or package
    bases = [english]
    if english.startswith("Plugin"):
        rest = english[len("Plugin"):]
        bases.append("插件" + rest)
        if rest.endswith(",Right Angle"):
            bases.append("弯插" + rest[:-len(",Right Angle")])
    if english in _WHOLE_PACKAGES:
        bases.append(_WHOLE_PACKAGES[english])
    spellings = dict.fromkeys(bases)
    for english_words, chinese in _PACKAGE_SWAPS:
        for spelling in list(spellings):
            if english_words in spelling:
                spellings[spelling.replace(english_words, chinese)] = None
    return [s for s in spellings if english_package(s) == english][:12]
