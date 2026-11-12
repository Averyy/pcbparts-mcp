"""KiCad legacy (.sch) text-format schematic parser.

Supports KiCad 4/5 era designs that use EESchema text files instead of
S-expression .kicad_sch files. Handles multi-sheet designs via $Sheet blocks.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from parse_boards import (
    Component, Net,
    normalize_footprint, normalize_value,
    extract_inline_specs, normalize_connector_value,
)
from parsers.common import is_junk_ref, build_attributes, value_from_properties, value_or_symbol, keep_source_specs

log = logging.getLogger(__name__)


def read_layout(pcb_path: Path, part_refs: set[str], paths: dict[str, str] | None = None
                ) -> tuple[list[Net], dict[str, dict[str, str]], dict[str, set[str]]]:
    """Connectivity and numbered pins from pre-S-expression Pcbnew layouts.

    AR is the schematic path; Sc is the footprint timestamp, not the symbol's.
    Count distinct pads, including excluded neighbors, when identifying NC pins.
    Geometry and footprint attributes are deliberately left to the schematic.
    """
    text = pcb_path.read_text(encoding="utf-8", errors="strict")
    if not text.startswith("PCBNEW-BOARD"):
        raise ValueError(f"Not a legacy KiCad layout: {pcb_path}")
    members: dict[str, set[tuple[int, str]]] = {}
    parts: dict[str, dict[str, str]] = {}
    assignments: list[tuple[str, str, str]] = []
    for index, block in enumerate(re.findall(r"^\$MODULE\b(.*?)^\$EndMODULE\b", text, re.M | re.S)):
        reference = re.search(r'^T0\s+[^\n]*?"([^"]+)"', block, re.M)
        path = re.search(r"^AR\s+(\S+)", block, re.M)
        ref = (paths or {}).get(path[1].upper() if path else "") or (reference[1] if reference else "")
        for pad in re.findall(r"^\$PAD\s*\n(.*?)^\$EndPAD", block, re.M | re.S):
            number = re.search(r'^Sh\s+"([^"]*)"', pad, re.M)
            net = re.search(r'^Ne\s+(\d+)\s+"([^"]*)"', pad, re.M)
            if not number or number[1] in ("", "~"):
                continue
            name = net[2] if net and net[1] != "0" else ""
            if name:
                members.setdefault(name, set()).add((index, number[1]))
            if ref in part_refs:
                parts.setdefault(ref, {})[number[1]] = number[1]
                if name:
                    assignments.append((ref, number[1], name))
    merged: dict[str, set[str]] = {}
    wired: dict[str, set[str]] = {}
    for ref, number, name in assignments:
        merged.setdefault(name, set()).add(f"{ref}.{number}")
        if len(members[name]) >= 2:
            wired.setdefault(ref, set()).add(number)
    nets = [Net(name=name, pins=sorted(pins)) for name, pins in merged.items() if len(pins) >= 2]
    return nets, parts, wired


def reference_paths(sch_path: Path) -> dict[str, str]:
    """Map stable sheet/symbol timestamps to current annotated references.

    A legacy PCB can retain old (even duplicate) reference text after schematic
    annotation. Its symbol path still identifies the component unambiguously.
    """
    refs: dict[str, str] = {}
    boundary = sch_path.parent.resolve()

    def visit(path: Path, prefix: str, active: set[Path]) -> None:
        path = path.resolve()
        if path in active or not path.is_relative_to(boundary) or not path.is_file():
            return
        text = path.read_text(encoding="utf-8", errors="replace")
        for block in re.findall(r"\$Comp\s*\n(.*?)\$EndComp", text, re.S):
            stamp = re.search(r"^U\s+\S+\s+\S+\s+(\S+)", block, re.M)
            ref = re.search(r'^F 0\s+"([^"]+)"', block, re.M)
            if stamp and ref:
                symbol_path = f"{prefix}/{stamp[1]}".upper()
                annotations = dict(re.findall(r'^AR Path="([^"]+)" Ref="([^"]+)"', block, re.M))
                annotations = {p.upper(): r for p, r in annotations.items()}
                # Reused sheets have a different reference per instance; F0 is only
                # the reference last displayed in the schematic editor.
                if not annotations or symbol_path in annotations:
                    refs[symbol_path] = annotations.get(symbol_path, ref[1])
        for block in re.findall(r"\$Sheet\s*\n(.*?)\$EndSheet", text, re.S):
            stamp = re.search(r"^U\s+(\S+)", block, re.M)
            file = re.search(r'^F1\s+"([^"]+)"', block, re.M)
            if stamp and file:
                visit(path.parent / file[1], f"{prefix}/{stamp[1]}", active | {path})

    visit(sch_path, "", set())
    return refs


def parse_schematic(sch_path: Path, *, property_aliases: dict | None = None) -> tuple[list[Component], list[Net]]:
    """Parse a KiCad legacy .sch file.

    Returns (components, []) — nets come from the layout or native schematic export.
    """
    components: list[Component] = []
    seen_refs: set[str] = set()
    visited_paths: set[str] = set()

    _parse_schematic_recursive(sch_path, components, seen_refs, visited_paths, property_aliases)

    log.info("Parsed KiCad legacy schematic: %d components", len(components))
    return components, []


def _parse_schematic_recursive(
    sch_path: Path,
    components: list[Component],
    seen_refs: set[str],
    visited_paths: set[str],
    property_aliases: dict | None = None,
) -> None:
    """Parse a single .sch file, recursing into sub-sheets."""
    resolved = str(sch_path.resolve())
    if resolved in visited_paths:
        return
    visited_paths.add(resolved)

    try:
        text = sch_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        log.warning("Could not read %s: %s", sch_path, e)
        return
    if "\ufffd" in text:
        log.warning("Replacement characters in %s — possible encoding issue", sch_path.name)

    lines = text.splitlines()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # Component block
        if line.startswith("$Comp"):
            block: list[str] = []
            i += 1
            while i < n and not lines[i].startswith("$EndComp"):
                block.append(lines[i])
                i += 1
            comp = _parse_comp_block(block, seen_refs, property_aliases)
            if comp:
                components.append(comp)
            i += 1
            continue

        # Sheet block — recurse into sub-sheets
        if line.startswith("$Sheet"):
            sheet_file = None
            i += 1
            while i < n and not lines[i].startswith("$EndSheet"):
                m = re.match(r'^F1\s+"([^"]+)"', lines[i])
                if m:
                    sheet_file = m.group(1)
                i += 1
            if sheet_file:
                sub_path = (sch_path.parent / sheet_file).resolve()
                # Path containment check: sub-sheet must stay within the repo
                if not sub_path.is_relative_to(sch_path.parent.resolve()):
                    log.warning("Sub-sheet path traversal blocked: %s", sheet_file)
                elif sub_path.exists():
                    _parse_schematic_recursive(sub_path, components, seen_refs, visited_paths, property_aliases)
                else:
                    log.warning("Sub-sheet not found: %s", sub_path)
            i += 1
            continue

        i += 1


def _parse_f_line(line: str) -> tuple[int, str, str] | None:
    """Parse an F-line from a component block.

    Returns (field_num, value, field_name) or None if unparseable.
    Field name is only present for F4+ custom fields.
    """
    m = re.match(r'^F\s+(\d+)\s+"([^"]*)"', line)
    if not m:
        return None
    num = int(m.group(1))
    value = m.group(2)

    # For custom fields (F4+), the field name is the last quoted string
    field_name = ""
    if num >= 4:
        quotes = re.findall(r'"([^"]*)"', line)
        if len(quotes) >= 2:
            field_name = quotes[-1]

    return num, value, field_name


def _parse_comp_block(lines: list[str], seen_refs: set[str], property_aliases: dict | None = None) -> Component | None:
    """Parse a $Comp/$EndComp block into a Component."""
    ref = ""
    symbol = ""
    value = ""
    footprint_raw = ""
    raw_attrs: dict[str, str] = {}

    # Fallback ref from L line
    l_ref = ""

    for line in lines:
        line = line.strip()

        # L line: symbol name + reference
        if line.startswith("L "):
            parts = line.split()
            if len(parts) >= 3:
                symbol = parts[1]
                l_ref = parts[2]
            elif len(parts) >= 2:
                symbol = parts[1]

        # F lines
        parsed = _parse_f_line(line)
        if parsed:
            num, val, field_name = parsed
            if num == 0:
                ref = val  # definitive reference
            elif num == 1:
                value = val
            elif num == 2:
                footprint_raw = val
            elif num == 3:
                pass  # datasheet — ignored
            elif num >= 4 and val and field_name:
                raw_attrs[field_name] = val

    # Use L-line ref as fallback if F0 didn't provide one
    if not ref:
        ref = l_ref

    # Skip power symbols and flags: "#PWR"/"#FLG" refs, or a power-library symbol re-annotated
    # with a plain ref. By symbol, not by a ref starting with + (Olimex names test pads +3.3V1).
    symbol_lib, _, symbol_name = symbol.rpartition(":")
    if ref.startswith("#") or symbol_lib.lower() == "power" or symbol_name.upper() == "PWR_FLAG":
        return None

    # Skip components with no footprint
    if not footprint_raw:
        return None

    # Skip junk references
    if is_junk_ref(ref):
        return None

    # Deduplicate multi-unit components (same ref, different U numbers)
    if ref in seen_refs:
        return None
    seen_refs.add(ref)

    # Strip footprint library prefix: "Capacitor_SMD:C_0805" → "C_0805"
    package = footprint_raw.split(":")[-1] if ":" in footprint_raw else footprint_raw
    fp = normalize_footprint(package, ref)

    attrs = build_attributes(raw_attrs, property_aliases, ref)
    # "~" is KiCad's empty value: name a fitted part by its symbol (Duet's X2 is CRYSTAL_4PIN)
    value = value_or_symbol(value, symbol, footprint_raw)
    value = value_from_properties(value, ref, raw_attrs, attrs, symbol=symbol)
    placed = value

    # Extract inline specs from value for passives
    ref_prefix = re.match(r"^([A-Z]+)", ref, re.IGNORECASE)
    ref_prefix_str = ref_prefix.group(1).upper() if ref_prefix else ""
    if ref_prefix_str in ("R", "C", "L", "FB"):
        cleaned_val, inline_specs = extract_inline_specs(value)
        for k, v in inline_specs.items():
            if k not in attrs:
                attrs[k] = v
        value = cleaned_val

    val = normalize_value(value, ref)
    keep_source_specs(placed, val, ref, attrs)
    val = normalize_connector_value(val, package, ref)

    return Component(
        ref=ref,
        value=val,
        footprint=fp,
        package=package,
        attributes=attrs,
    )
