"""Connector series detection and brand alias expansion.

Handles JST connector series (SH, XH, PH, etc.) and maker ecosystem
brand names (Qwiic, STEMMA QT, easyC) that map to specific connector specs.
"""

import re
from dataclasses import dataclass


@dataclass
class ConnectorSpec:
    """Extracted connector specifications."""
    series: str | None = None  # e.g., "SH", "XH", "PH"
    pitch: float | None = None  # in mm, e.g., 1.0, 2.0, 2.54
    pins: int | None = None  # number of pins
    fts_term: str | None = None  # term to add to FTS search


# JST connector series with their pitch values (in mm)
# Source: JST datasheets
JST_SERIES_PITCH: dict[str, float] = {
    # Wire-to-board connectors
    "sh": 1.0,    # JST SH - 1.0mm pitch (Qwiic, STEMMA QT)
    "sr": 1.0,    # JST SR - 1.0mm pitch (vertical SH)
    "gh": 1.25,   # JST GH - 1.25mm pitch
    "zh": 1.5,    # JST ZH - 1.5mm pitch
    "pa": 2.0,    # JST PA - 2.0mm pitch
    "ph": 2.0,    # JST PH - 2.0mm pitch (common in batteries)
    "eh": 2.5,    # JST EH - 2.5mm pitch
    "xh": 2.5,    # JST XH - 2.5mm pitch (larger, common in power)
    "vh": 3.96,   # JST VH - 3.96mm pitch (high power)
    "vl": 6.2,    # JST VL - 6.2mm pitch
    # Board-to-board
    "bm": 1.0,    # JST BM - 1.0mm board-to-board
}

# Pattern to detect JST series in query
# Matches: "jst sh", "jst-sh", "sh connector", "sh series", standalone "sh" near "jst"
_JST_SERIES_PATTERN = re.compile(
    r'\bjst[\s-]*(sh|sr|gh|zh|pa|ph|eh|xh|vh|vl|bm)\b'
    r'|'
    r'\b(sh|sr|gh|zh|pa|ph|eh|xh|vh|vl|bm)\s*(?:series|connector|plug|socket|receptacle)\b',
    re.IGNORECASE
)

# Standalone series pattern - matches series codes that appear with JST context
_STANDALONE_SERIES = re.compile(r'\b(sh|gh|zh|ph|xh|vh|eh|pa)\b', re.IGNORECASE)


# Brand aliases that map to specific JST connector specs
# These are maker ecosystem standards that use JST SH connectors
BRAND_CONNECTOR_SPECS: dict[str, ConnectorSpec] = {
    # SparkFun Qwiic - JST SH 1.0mm 4-pin
    "qwiic": ConnectorSpec(series="SH", pitch=1.0, pins=4, fts_term="SH"),
    "qwiic connector": ConnectorSpec(series="SH", pitch=1.0, pins=4, fts_term="SH"),

    # Adafruit STEMMA QT - JST SH 1.0mm 4-pin (same as Qwiic)
    "stemma qt": ConnectorSpec(series="SH", pitch=1.0, pins=4, fts_term="SH"),
    "stemmaqt": ConnectorSpec(series="SH", pitch=1.0, pins=4, fts_term="SH"),

    # Adafruit STEMMA (original, larger) - JST PH 2.0mm 3 or 4-pin
    # Don't set pin count since it varies
    "stemma": ConnectorSpec(series="PH", pitch=2.0, fts_term="PH"),

    # M5Stack easyC/Grove compatible - JST SH 1.0mm 4-pin
    "easyc": ConnectorSpec(series="SH", pitch=1.0, pins=4, fts_term="SH"),
    "easy c": ConnectorSpec(series="SH", pitch=1.0, pins=4, fts_term="SH"),

    # Grove connectors use a different style (HY2.0-4P), but users searching
    # "grove connector" probably want something compatible
    # Grove uses 2.0mm pitch 4-pin but is not JST
    "grove": ConnectorSpec(pitch=2.0, pins=4, fts_term="HY2.0"),
}


def extract_connector_series(query: str) -> tuple[ConnectorSpec | None, str]:
    """Extract JST connector series and brand aliases from query.

    Args:
        query: The search query string

    Returns:
        Tuple of (ConnectorSpec if found, remaining query with series removed)
    """
    query_lower = query.lower()
    remaining = query

    # Check brand aliases first (Qwiic, STEMMA QT, easyC)
    for brand, spec in BRAND_CONNECTOR_SPECS.items():
        if brand in query_lower:
            # Remove the brand name from query
            pattern = re.compile(re.escape(brand), re.IGNORECASE)
            remaining = pattern.sub('', remaining)
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            return spec, remaining

    # Check for explicit JST series pattern (e.g., "jst sh", "jst-ph")
    match = _JST_SERIES_PATTERN.search(query)
    if match:
        # Get the series code from whichever group matched
        series = (match.group(1) or match.group(2)).upper()
        pitch = JST_SERIES_PITCH.get(series.lower())

        # Remove the matched pattern from query
        remaining = query[:match.start()] + query[match.end():]
        remaining = re.sub(r'\s+', ' ', remaining).strip()

        return ConnectorSpec(series=series, pitch=pitch, fts_term=series), remaining

    # Check for standalone series code if "jst" appears elsewhere in query
    if "jst" in query_lower:
        series_match = _STANDALONE_SERIES.search(query)
        if series_match:
            series = series_match.group(1).upper()
            pitch = JST_SERIES_PITCH.get(series.lower())

            # Remove both "jst" and the series code
            remaining = re.sub(r'\bjst\b', '', remaining, flags=re.IGNORECASE)
            remaining = remaining[:series_match.start()] + remaining[series_match.end():]
            remaining = re.sub(r'\s+', ' ', remaining).strip()

            return ConnectorSpec(series=series, pitch=pitch, fts_term=series), remaining

    return None, query


def get_pitch_for_series(series: str) -> float | None:
    """Get the pitch (in mm) for a JST series code.

    Args:
        series: Series code like "SH", "PH", "XH"

    Returns:
        Pitch in mm or None if unknown series
    """
    return JST_SERIES_PITCH.get(series.lower())
