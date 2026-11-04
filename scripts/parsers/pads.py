"""PADS PowerPCB ASCII layout (.asc) + BOM spreadsheet → components, nets, positions, outline.

Espressif's DevKit reference designs ship a PADS layout, an OrCAD schematic (.DSN, binary) and a BOM
(.xlsx). The layout has every part's position and decal, and its *ROUTE* section lists each net's
connections as REF.PIN pairs (pad numbers, as KiCad PCBs give). The BOM gives values, makers and MPNs.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from parse_boards import (
    BoardOutline,
    Component,
    DesignRules,
    Net,
    Position,
    normalize_footprint,
    normalize_value,
)

log = logging.getLogger(__name__)

# PADS "basic" units: 38,100 per mil, 1,500,000 per mm
_UNITS_PER_MM = 1_500_000

_PART_LINE = re.compile(r"^(\S+)\s+(\S+)\s+(-?\d+)\s+(-?\d+)\s+(-?[\d.]+)\s+[GU]\s+([NM])\b")
_PIN_PAIR = re.compile(r"^(\S+?)\.(\S+)\s+(\S+?)\.(\S+)\s*$")
_SECTION = re.compile(r"^\*([A-Z]+)\*")
# "0.1uF/50V(10%)", "10K(1%)", "1uF/16V(10%)"
_BOM_VALUE = re.compile(r"^\s*([^/(]+?)\s*(?:/\s*([\d.]+\s*[kK]?V))?\s*(?:\(\s*([\d.]+\s*%)\s*\))?\s*$")


def _sections(text: str) -> dict[str, list[str]]:
    """Lines of each top-level *SECTION*, in order (*REMARK* lines dropped)."""
    sections: dict[str, list[str]] = {}
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        match = _SECTION.match(line)
        if match and match.group(1) not in ("REMARK", "SIGNAL"):
            current = match.group(1)
            sections.setdefault(current, [])
            continue
        if current and not line.startswith("*REMARK*"):
            sections[current].append(line)
    return sections


def _outline(lines: list[str]) -> BoardOutline | None:
    """The BOARD piece in *LINES*: its corner extents."""
    xs: list[int] = []
    ys: list[int] = []
    in_board = False
    for line in lines:
        tokens = line.split()
        if len(tokens) >= 2 and tokens[1] in ("BOARD", "COPPER", "LINES", "COPCUT", "KEEPOUT") and not tokens[0].isdigit():
            in_board = tokens[1] == "BOARD"
            continue
        if in_board and len(tokens) >= 2 and re.fullmatch(r"-?\d+", tokens[0]) and re.fullmatch(r"-?\d+", tokens[1]):
            xs.append(int(tokens[0]))
            ys.append(int(tokens[1]))
    if not xs:
        return None
    return BoardOutline(width=round((max(xs) - min(xs)) / _UNITS_PER_MM, 2),
                        height=round((max(ys) - min(ys)) / _UNITS_PER_MM, 2))


def read_bom(bom_path: Path) -> dict[str, dict[str, str]]:
    """{ref: {value, footprint, mpn, manufacturer, description, voltage, tolerance}} from an Espressif
    BOM sheet ("Part Reference" lists refs like "C2,C8,C9"; rows without an item number are alternates)."""
    import openpyxl

    sheet = openpyxl.load_workbook(bom_path, data_only=True, read_only=True).worksheets[0]
    rows = list(sheet.iter_rows(values_only=True))
    # Column names differ between Espressif's BOM templates (S3 DevKits / DevKitC V4)
    names = {"Part Reference": "refs", "Ref Des": "refs", "Item Number": "item", "ID": "item", "Value": "value",
             "PCB Footprint": "footprint", "Package": "footprint", "Manufacturer Part #": "mpn",
             "Manufacturer": "manufacturer", "Description": "description"}
    header_at = next(i for i, row in enumerate(rows) if row and ("Part Reference" in row or "Ref Des" in row))
    col = {names[str(c).strip()]: i for i, c in enumerate(rows[header_at]) if str(c or "").strip() in names}
    parts: dict[str, dict[str, str]] = {}
    for row in rows[header_at + 1:]:
        refs = row[col["refs"]] if row else None
        if not refs or row[col["item"]] is None:
            continue  # an alternate maker's row
        value = re.sub(r"\s+(?=[pnuµm]?F\b|[kKM]?\b)", "", str(row[col["value"]] or "").strip(), count=1) \
            if re.match(r"^[\d.]+\s+[pnuµmkKM]", str(row[col["value"]] or "").strip()) else str(row[col["value"]] or "").strip()
        entry: dict[str, str] = {"footprint": str(row[col["footprint"]] or "").strip()}
        match = _BOM_VALUE.match(value)
        if match and (match.group(2) or match.group(3)):
            entry["value"] = match.group(1)
            if match.group(2):
                entry["voltage"] = match.group(2).replace(" ", "")
            if match.group(3):
                entry["tolerance"] = match.group(3).replace(" ", "")
        else:
            entry["value"] = re.sub(r"\(\s*[\d.]+\s*%\s*\)$", "", value).strip()
        for key in ("mpn", "manufacturer", "description"):
            text = re.sub(r"\s+", " ", str(row[col[key]] or "")).strip() if key in col else ""
            if text and text != "-":
                entry[key] = text
        for ref in re.split(r"[,\s]+", str(refs)):
            if ref:
                parts[ref.strip()] = entry
    return parts


def parse_pads(asc_path: Path, bom_path: Path | None) -> tuple[
        list[Component], list[Net], list[Position], BoardOutline | None, DesignRules]:
    """Components (BOM parts placed on the board), nets, positions, outline and layer count."""
    text = asc_path.read_text(encoding="latin-1")
    sections = _sections(text)
    bom = read_bom(bom_path) if bom_path else {}

    placed: dict[str, tuple[str, Position]] = {}
    for line in sections.get("PART", []):
        match = _PART_LINE.match(line)
        if match:
            ref, part_type, x, y, rotation, mirror = match.groups()
            placed[ref] = (part_type.split("@")[0], Position(
                ref=ref, x=round(int(x) / _UNITS_PER_MM, 2), y=round(int(y) / _UNITS_PER_MM, 2),
                rotation=float(rotation), side="back" if mirror == "M" else "front"))

    pins_by_net: dict[str, set[str]] = {}
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("*SIGNAL*"):
            current = line.split()[1]
            continue
        if _SECTION.match(line):
            if current and not line.startswith("*SIGNAL*"):
                current = None if not line.startswith("*REMARK*") else current
            continue
        if current:
            match = _PIN_PAIR.match(line)
            if match:
                pins_by_net.setdefault(current, set()).update(
                    {f"{match.group(1)}.{match.group(2)}", f"{match.group(3)}.{match.group(4)}"})

    components: list[Component] = []
    for ref, (part_type, _) in sorted(placed.items()):
        info = bom.get(ref)
        if info is None:
            if not any(p.split(".")[0] == ref for pins in pins_by_net.values() for p in pins):
                continue  # a logo or fiducial
            info = {"value": part_type, "footprint": part_type}
        attributes = {k: v for k, v in info.items() if k not in ("value", "footprint")}
        components.append(Component(ref=ref, value=normalize_value(info["value"], ref),
                                    footprint=normalize_footprint(info.get("footprint") or part_type, ref),
                                    package=info.get("footprint") or part_type, attributes=attributes))

    refs = {c.ref for c in components}
    nets = [Net(name=name, pins=sorted(p for p in pins if p.split(".")[0] in refs))
            for name, pins in sorted(pins_by_net.items())]
    nets = [n for n in nets if len(n.pins) >= 2]

    layers = 2
    for line in sections.get("PCB", []):
        if line.startswith("MAXIMUMLAYER"):
            layers = int(line.split()[1])
    missing = sorted(set(bom) - set(placed))
    if missing:
        log.warning("BOM parts not on the layout: %s", ", ".join(missing))
    log.info("Parsed PADS layout: %d components, %d nets", len(components), len(nets))
    return (components, nets, [pos for ref, (_, pos) in sorted(placed.items()) if ref in refs],
            _outline(sections.get("LINES", [])), DesignRules(layers=layers))
