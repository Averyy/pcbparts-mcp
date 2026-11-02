"""EasyEDA pinout parser for extracting pin information from component symbols."""

import json
import re
from typing import Any

# Pre-compiled regex patterns for extracting pin labels
_START_LABEL_PATTERN = re.compile(r"~([^~]+)~start~~~")
_END_LABEL_PATTERN = re.compile(r"~([^~]+)~end~~~")

# EasyEDA electrical type mapping
_ELECTRICAL_TYPES = {
    "": "undefined",
    "0": "undefined",
    "1": "input",
    "2": "output",
    "3": "bidirectional",
    "4": "power",
}


def parse_easyeda_pins(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse pin data from EasyEDA component response.

    Returns raw pin data exactly as EasyEDA provides it, with no interpretation.

    A pin is "^^"-separated segments: header (P~show~{electric}~{spice_pin}~x~y~...),
    pin dot, pin path, name text, number text, ... Each text segment is
    {show}~x~y~rotation~{text}~{anchor}~~~{color}. The number is the number text,
    not {spice_pin}: module symbols leave {spice_pin} at 0 or reuse low numbers
    (SIM7080G: VBAT is spice 0, number 35).

    Args:
        data: EasyEDA component response dict with dataStr.shape array

    Returns:
        List of pin dicts with number, name, and electrical type.
    """
    pins = []
    data_str = data.get("dataStr", {})

    # Handle both string and dict dataStr
    if isinstance(data_str, str):
        try:
            data_str = json.loads(data_str)
        except (json.JSONDecodeError, TypeError):
            return []

    # Type guard for non-dict dataStr
    if not isinstance(data_str, dict):
        return []

    shape = data_str.get("shape", [])
    if not shape:
        return []

    for element in shape:
        if not isinstance(element, str) or not element.startswith("P~"):
            continue

        # Electrical type (index 2) and SPICE pin number (index 3) from the header
        segments = element.split("^^")
        parts = segments[0].split("~")
        electric_code = parts[2] if len(parts) > 2 else ""
        pin_num = parts[3] if len(parts) > 3 else None

        name_text = _segment_text(segments, 3)
        num_text = _segment_text(segments, 4)
        if num_text is not None and name_text is not None:
            pin_num = num_text
            pin_name = name_text
        else:
            # Unexpected layout: fall back to the labels' anchors, name being
            # whichever label is not just a number
            start_match = _START_LABEL_PATTERN.search(element)
            end_match = _END_LABEL_PATTERN.search(element)
            start_label = start_match.group(1) if start_match else None
            end_label = end_match.group(1) if end_match else None
            if start_label and not start_label.isdigit():
                pin_name = start_label
            elif end_label and not end_label.isdigit():
                pin_name = end_label
            else:
                pin_name = pin_num  # Use pin number as name

        pin_data = {
            "number": pin_num,
            "name": pin_name,
        }
        # Only include electrical type if actually set (not undefined)
        electrical = _ELECTRICAL_TYPES.get(electric_code, "undefined")
        if electrical != "undefined":
            pin_data["electrical"] = electrical

        pins.append(pin_data)

    # Sort by pin number
    pins.sort(key=lambda p: _sort_key(p["number"]))
    return pins


def _segment_text(segments: list[str], index: int) -> str | None:
    """Text of a pin's name or number segment ({show}~x~y~rotation~{text}~{anchor}~...)."""
    if len(segments) <= index:
        return None
    fields = segments[index].split("~")
    if len(fields) < 6 or fields[5] not in ("start", "end", "middle"):
        return None
    return fields[4].strip() or None


def _sort_key(num: str | None) -> tuple:
    """Sort pin numbers numerically when possible."""
    try:
        return (0, int(num))  # type: ignore
    except (ValueError, TypeError):
        return (1, num or "")
