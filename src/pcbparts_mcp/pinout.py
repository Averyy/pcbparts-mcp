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

    Multi-unit symbols keep their pins in ``subparts``, one dataStr per unit, and usually leave
    the top-level shape empty: MIMXRT1052CVL5B (BGA-196) has 153 + 43 pins there and returned
    "missing pin data". Some also draw the whole symbol at the top level; its pins win.

    Args:
        data: EasyEDA component response dict with dataStr.shape array (and optional subparts)

    Returns:
        List of pin dicts with number, name, and electrical type, sorted by pin number
        (BGA balls in natural order: A1, A2, ..., A10).
    """
    pins = list({(p["number"], p["name"]): p for p in _parse_unit(data)}.values())
    # Units only add pins the top-level symbol lacks. Some symbols have both a complete
    # top-level drawing and split units naming the same pins differently (LM358 C328566:
    # OUT1 and OUTA, VEE and GND), which listed every pin twice. A pin drawn in two units
    # (a shared supply) is listed once, from the first unit. A unit's electrical type
    # fills in a same-numbered pin that has none (same pad).
    by_number: dict[str, list[dict[str, Any]]] = {}
    for pin in pins:
        by_number.setdefault(pin["number"], []).append(pin)
    for unit in data.get("subparts") or []:
        if isinstance(unit, dict):
            for pin in _parse_unit(unit):
                known = by_number.get(pin["number"])
                if not known:
                    by_number[pin["number"]] = [pin]
                    pins.append(pin)
                elif "electrical" in pin:
                    for same in known:
                        same.setdefault("electrical", pin["electrical"])
    pins.sort(key=lambda p: _sort_key(p["number"]))
    return pins


def _parse_unit(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Pins of one symbol unit (the component itself or one of its subparts), unsorted."""
    pins: list[dict[str, Any]] = []
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

    return pins


def _segment_text(segments: list[str], index: int) -> str | None:
    """Text of a pin's name or number segment ({show}~x~y~rotation~{text}~{anchor}~...)."""
    if len(segments) <= index:
        return None
    fields = segments[index].split("~")
    if len(fields) < 6 or fields[5] not in ("start", "end", "middle"):
        return None
    return fields[4].strip() or None


_UNIT_MM = 0.254  # EasyEDA Standard canvas unit: 10 mil
_PAD_LAYERS = {"1": "top", "2": "bottom", "11": "through_hole"}


def parse_easyeda_footprint(data: dict[str, Any]) -> dict[str, Any] | None:
    """Footprint name, source link, pad summary and pads from an EasyEDA footprint (docType 4).

    A pad is PAD~{shape}~{x}~{y}~{width}~{height}~{layer}~{net}~{number}~{hole radius}~{points}~
    {rotation}~{id}~{slot length}~... in 10-mil units. Positions are mm from the footprint's
    origin, y growing downward as EasyEDA draws it; a 90/270 degree rotation swaps width and height.
    From design-session reports: a slide switch's pins had numbers only, so its common and throws
    couldn't be told apart without pad positions; a U.FL footprint was another maker's; and a "72P"
    module footprint had 77 pads.
    """
    data_str = data.get("dataStr", {})
    if isinstance(data_str, str):
        try:
            data_str = json.loads(data_str)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(data_str, dict):
        return None
    head = data_str.get("head") or {}
    try:
        ox, oy = float(head.get("x") or 0), float(head.get("y") or 0)
    except (TypeError, ValueError):
        ox = oy = 0.0
    pads = []
    for element in data_str.get("shape") or []:
        if not isinstance(element, str) or not element.startswith("PAD~"):
            continue
        f = element.split("~")
        try:
            x, y, w, h = (float(v) for v in f[2:6])
            hole_r = float(f[9] or 0) if len(f) > 9 else 0.0
            rotation = float(f[11] or 0) if len(f) > 11 else 0.0
            slot = float(f[13] or 0) if len(f) > 13 else 0.0
        except (ValueError, IndexError):
            continue
        if round(rotation) % 180 == 90:
            w, h = h, w
        pad: dict[str, Any] = {
            "number": f[8] if len(f) > 8 else "",
            "x": _mm(x - ox), "y": _mm(y - oy),
            "shape": f[1].lower(), "size": [_mm(w), _mm(h)],
            "layer": _PAD_LAYERS.get(f[6], f[6]),
        }
        if round(rotation) % 90:
            pad["rotation"] = rotation
        if hole_r > 0:
            pad["hole"] = _mm(2 * hole_r)
            if slot > 0:
                pad["slot_length"] = _mm(slot)
        pads.append(pad)
    if not pads:
        return None
    pads.sort(key=lambda p: _sort_key(p["number"]))
    sizes: dict[str, int] = {}
    for pad in pads:
        small, large = sorted(pad["size"])  # a pad turned 90 degrees is the same size
        key = f"{small:g}x{large:g} mm {pad['shape']}" + (
            f", hole {pad['hole']:g} mm" if "hole" in pad else "")
        sizes[key] = sizes.get(key, 0) + 1
    para = head.get("c_para") or {}
    result: dict[str, Any] = {
        "name": para.get("package") or data.get("title"),
        "pad_count": len(pads),
        "numbered_pads": len({p["number"] for p in pads if p["number"]}),
    }
    if pitch := _common_pitch(pads):
        result["pitch"] = pitch
    result["pad_sizes"] = [{"size": k, "count": n} for k, n in sorted(sizes.items(), key=lambda kv: -kv[1])]
    if link := para.get("link"):
        result["source_link"] = link
    result["pads"] = pads
    return result


def _mm(units: float) -> float:
    return round(units * _UNIT_MM, 3)


def _common_pitch(pads: list[dict[str, Any]]) -> float | None:
    """Most common distance from a pad to its nearest neighbour, in mm (None under 3 pads)."""
    if len(pads) < 3 or len(pads) > 2000:
        return None
    counts: dict[float, int] = {}
    for i, a in enumerate(pads):
        nearest = min(((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5
                      for j, b in enumerate(pads) if j != i)
        if nearest > 0:
            key = round(nearest, 2)
            counts[key] = counts.get(key, 0) + 1
    return max(counts, key=lambda k: (counts[k], -k)) if counts else None


def _sort_key(num: str | None) -> tuple:
    """Sort pin numbers numerically, and BGA balls by row then column (A2 before A10)."""
    try:
        return (0, int(num))  # type: ignore
    except (ValueError, TypeError):
        return (1, tuple((0, int(part), "") if part.isdigit() else (1, 0, part)
                         for part in re.findall(r"\d+|\D+", num or "")))
