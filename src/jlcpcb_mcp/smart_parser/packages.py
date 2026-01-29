"""Package pattern detection for smart query parsing."""

import re


# Pre-compiled patterns for performance
PACKAGE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Imperial chip sizes (passives) - EIA standard format LLWW in 0.01"
    # e.g., 0603 = 0.06" x 0.03" = 1.6mm x 0.8mm
    (re.compile(r'\b(01005|0201|0402|0603|0805|1206|1210|1812|2010|2512)\b'), 'imperial'),

    # SMD metric dimensions (crystals, oscillators, LEDs) - format LLWW in 0.1mm
    # e.g., 3215 = 3.2mm x 1.5mm, 5032 = 5.0mm x 3.2mm
    # These expand to SMD{dim} variants like SMD3215-2P
    (re.compile(r'\b(1610|1612|2012|2016|2520|2835|3014|3020|3030|3215|3225|3528|3535|5032|5050|5730|6035|7050|7060|8045|8080|9070)\b'), 'smd_metric'),

    # Metric chip sizes (with M suffix)
    (re.compile(r'\b(0402M|0603M|0805M|1206M)\b', re.IGNORECASE), 'metric'),

    # SOT packages - comprehensive with any pin count suffix
    (re.compile(r'\b(SOT-?23(?:-\d+)?L?|SOT-?89(?:-\d+)?|SOT-?223(?:-\d+)?|SOT-?323(?:-\d+)?|SOT-?363(?:-\d+)?|SOT-?523(?:-\d+)?|SOT-?723(?:-\d+)?)\b', re.IGNORECASE), 'sot'),

    # SOD packages (Small Outline Diode) - critical for diodes!
    (re.compile(r'\b(SOD-?(?:123|323|523|923|128|882|80|110|123FL|323FL))\b', re.IGNORECASE), 'sod'),

    # DO packages (Diode Outline)
    (re.compile(r'\b(DO-?(?:35|41|201|204|214|215|218|219|220)(?:AA|AB|AC|AD|AE|AF|AG)?)\b', re.IGNORECASE), 'do'),

    # TO packages
    (re.compile(r'\b(TO-?92(?:S|L)?|TO-?220(?:F|FP|AB)?(?:-\d+)?|TO-?252(?:-\d+)?|TO-?263(?:-\d+)?|TO-?247(?:-\d+)?|TO-?251|TO-?3P(?:F)?|DPAK|D2PAK|D3PAK)\b', re.IGNORECASE), 'to'),

    # QFN/DFN packages with optional size
    (re.compile(r'\b((?:V)?QFN-?\d+(?:-EP)?(?:\([^)]+\))?|DFN-?\d+(?:-EP)?(?:\([^)]+\))?|WQFN-?\d+|TQFN-?\d+|UQFN-?\d+)\b', re.IGNORECASE), 'qfn'),

    # QFP/LQFP/TQFP packages
    (re.compile(r'\b((?:L|T|H|PQ)?QFP-?\d+(?:\([^)]+\))?)\b', re.IGNORECASE), 'qfp'),

    # BGA packages
    (re.compile(r'\b((?:FC|W|T|M|U|P|F)?BGA-?\d+(?:\([^)]+\))?)\b', re.IGNORECASE), 'bga'),

    # CSP packages (Chip Scale Package)
    # Includes WLCSP (Wafer-Level CSP), LFCSP (Lead Frame CSP), UCSP (Ultra CSP), bare CSP, etc.
    (re.compile(r'\b((?:WL|LF|U|FC|V)?CSP-?\d+(?:-EP)?(?:\([^)]+\))?)\b', re.IGNORECASE), 'csp'),

    # DIP/SIP packages
    (re.compile(r'\b((?:P|S|SK|C)?DIP-?\d+(?:\([^)]+\))?|SIP-?\d+)\b', re.IGNORECASE), 'dip'),

    # SOP/SOIC/SO/SSOP/TSSOP/MSOP packages (order matters - TSSOP before SOP, SO last)
    (re.compile(r'\b(TSSOP-?\d+|SSOP-?\d+|MSOP-?\d+|QSOP-?\d+|HTSSOP-?\d+|VSSOP-?\d+)\b', re.IGNORECASE), 'tssop'),
    (re.compile(r'\b(SOP-?\d+(?:-\d+)?(?:\([^)]+\))?|SOIC-?\d+(?:-\d+)?(?:\([^)]+\))?)\b', re.IGNORECASE), 'sop'),
    # SO-8 without P/IC suffix (must come after SOP/SOIC to avoid partial matches)
    (re.compile(r'\b(SO-?\d+)\b', re.IGNORECASE), 'so'),

    # Module packages (SMD-XX, LGA-XX) - NOT bare "MODULE" which is a common word
    # SMA/SMB/SMC are diode packages, but SMA is also a connector type
    # Only match SMA/SMB/SMC when NOT followed by "connector" to avoid conflict
    (re.compile(r'\b(SMD-?\d+|LGA-?\d+)\b', re.IGNORECASE), 'module'),
    # SMA/SMB/SMC diode packages - but exclude "SMA connector" patterns
    (re.compile(r'\b(SM[ABC])\b(?!\s*connector)', re.IGNORECASE), 'diode_pkg'),
    # Mxx diode package aliases (M4/M7 = SMA/DO-214AC, common in Asian datasheets)
    (re.compile(r'\b(M[478])\b', re.IGNORECASE), 'mxx_diode_pkg'),

    # Connector specific
    (re.compile(r'\b(USB-?[ABC]|TYPE-?[ABC]|MICRO-?USB|MINI-?USB)\b', re.IGNORECASE), 'usb'),
]


def extract_package(query: str) -> tuple[str | None, str, str | None]:
    """Extract package from query and return (package, remaining_query, suggested_subcategory).

    The suggested_subcategory is used for USB-C etc. where the package implies a component type.

    Args:
        query: The search query string

    Returns:
        Tuple of (package, remaining_query, suggested_subcategory)
    """
    for pattern, pkg_type in PACKAGE_PATTERNS:
        match = pattern.search(query)
        if match:
            package = match.group(1).upper()
            # Normalize: remove optional hyphen variations
            package = re.sub(r'SOT(\d)', r'SOT-\1', package)
            package = re.sub(r'SOD(\d)', r'SOD-\1', package)
            package = re.sub(r'TO(\d)', r'TO-\1', package)
            remaining = query[:match.start()] + query[match.end():]
            remaining = remaining.strip()

            # Map Mxx diode packages to SMA/SMB (M4/M7=SMA, M8=SMB)
            if pkg_type == 'mxx_diode_pkg':
                if package in ('M4', 'M7'):
                    package = 'SMA'
                elif package == 'M8':
                    package = 'SMB'

            # Suggest subcategory for connector packages
            suggested_subcat = None
            if pkg_type == 'usb':
                suggested_subcat = 'usb connectors'
                # USB-C/TYPE-C are NOT package names in JLCPCB (package is "SMD")
                # They're connector types, so don't use as package filter
                # Keep in query for text search instead
                return None, query, suggested_subcat

            return package, remaining, suggested_subcat
    return None, query, None
