"""Model number detection for smart query parsing."""

import re


# Common model number patterns (component-specific part numbers)
MODEL_PATTERNS = [
    # IC model numbers: STM32F103, ESP32-C3, TP4056, AMS1117
    re.compile(r'\b([A-Z]{2,5}\d{2,5}[A-Z]?\d*(?:-[A-Z0-9]+)?)\b', re.IGNORECASE),
    # Specific known patterns
    re.compile(r'\b(ESP32-[A-Z0-9]+|STM32[A-Z]\d+[A-Z0-9]*|RP2040|ATMEGA\d+[A-Z]*|PIC\d+[A-Z0-9]*)\b', re.IGNORECASE),
    re.compile(r'\b(TP[45]\d{3}|AMS\d{4}|LM\d{4}|NE555|TL\d{3}|LMV?\d{3,4}|TPS\d{4,5})\b', re.IGNORECASE),
    re.compile(r'\b(AO\d{4}|SI\d{4}|IRF\d{3,4}|IRLZ?\d{2,4}|2N\d{4}|BC\d{3})\b', re.IGNORECASE),
    re.compile(r'\b(WS2812[A-Z]*|SK6812|APA102|TLC5940)\b', re.IGNORECASE),
    # Diode/discrete model numbers: 1N4148, 1N5819, 1SS400
    re.compile(r'\b(1N\d{4}[A-Z]*|1SS\d{3}[A-Z]*|BAT\d{2}[A-Z]*|BAS\d{2}[A-Z]*|BAV\d{2}[A-Z]*)\b', re.IGNORECASE),
]


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
            # Verify it's not a common word or measurement
            if model.upper() not in ('LED', 'LCD', 'USB', 'SPI', 'I2C', 'ADC', 'DAC', 'MCU', 'CPU', 'GPU'):
                remaining = query[:match.start()] + query[match.end():]
                return model, remaining.strip()

    return None, query
