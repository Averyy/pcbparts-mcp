"""Model number detection for smart query parsing."""

import re


# Common model number patterns (component-specific part numbers)
# Order matters! More specific patterns must come before generic ones.
MODEL_PATTERNS = [
    # ESP32 modules use compound naming: ESP32-{variant}-{formfactor}-{version}
    # e.g., ESP32-S3-MINI-1, ESP32-C3-WROOM-1, ESP32-S3-MINI-1-N8
    # Must be FIRST to match full compound names before generic pattern truncates them
    re.compile(r'\b(ESP32(?:-[A-Z0-9]+)+)\b', re.IGNORECASE),
    # Other specific MCU/IC patterns
    re.compile(r'\b(STM32[A-Z]\d+[A-Z0-9]*|RP2040|ATMEGA\d+[A-Z]*|PIC\d+[A-Z0-9]*)\b', re.IGNORECASE),
    re.compile(r'\b(TP[45]\d{3}|AMS\d{4}|LM\d{4}|NE555|TL\d{3}|LMV?\d{3,4}|TPS\d{4,5})\b', re.IGNORECASE),
    re.compile(r'\b(AO\d{4}|SI\d{4}|IRF\d{3,4}|IRLZ?\d{2,4}|2N\d{4}|BC\d{3})\b', re.IGNORECASE),
    re.compile(r'\b(WS2812[A-Z]*|SK6812|APA102|TLC5940)\b', re.IGNORECASE),
    # Diode/discrete model numbers: 1N4148, 1N5819, 1SS400
    re.compile(r'\b(1N\d{4}[A-Z]*|1SS\d{3}[A-Z]*|BAT\d{2}[A-Z]*|BAS\d{2}[A-Z]*|BAV\d{2}[A-Z]*)\b', re.IGNORECASE),
    # Generic IC model numbers (last resort): STM32F103, TP4056, AMS1117
    # This is intentionally last to avoid truncating specific patterns above
    re.compile(r'\b([A-Z]{2,5}\d{2,5}[A-Z]?\d*(?:-[A-Z0-9]+)?)\b', re.IGNORECASE),
]

# Package-like patterns that should NOT be treated as model numbers
# These match common package names without hyphens (SOT23, SOD323, etc.)
PACKAGE_LIKE_PATTERNS = (
    'SOT', 'SOD', 'SOP', 'SOIC', 'SSOP', 'TSSOP', 'MSOP', 'QSOP',
    'QFN', 'DFN', 'QFP', 'LQFP', 'TQFP', 'BGA', 'DIP', 'SIP',
    'CSP', 'WLCSP', 'LFCSP', 'UCSP', 'VCSP',  # Chip Scale Package variants
)


def extract_model_number(query: str) -> tuple[str | None, str]:
    """Extract likely model number from query.

    Args:
        query: The search query string

    Returns:
        Tuple of (model_number, remaining_query)
    """
    for pattern in MODEL_PATTERNS:
        match = pattern.search(query)
        if match:
            model = match.group(1)
            model_upper = model.upper()
            # Verify it's not a common word or measurement
            if model_upper in ('LED', 'LCD', 'USB', 'SPI', 'I2C', 'ADC', 'DAC', 'MCU', 'CPU', 'GPU',
                              'RJ45', 'RJ11', 'RJ12', 'RJ9', 'RJ22', 'RJ25'):  # Connector type codes
                continue
            # Verify it's not a package name without hyphen (e.g., SOT23, SOD323, QFN32)
            # Check if model starts with a known package prefix followed by digits
            for pkg_prefix in PACKAGE_LIKE_PATTERNS:
                if model_upper.startswith(pkg_prefix) and len(model_upper) > len(pkg_prefix):
                    # Check if rest is digits or digits with suffix
                    rest = model_upper[len(pkg_prefix):]
                    if rest.isdigit() or (rest[0].isdigit() and all(c.isdigit() or c == 'L' for c in rest)):
                        break  # This is a package, not a model
            else:
                # Not a package - this is a valid model number
                remaining = query[:match.start()] + query[match.end():]
                return model, remaining.strip()

    return None, query
