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
from parsers.common import is_junk_ref, build_attributes

log = logging.getLogger(__name__)


def parse_schematic(sch_path: Path) -> tuple[list[Component], list[Net]]:
    """Parse a KiCad legacy .sch file.

    Returns (components, []) — nets come from .kicad_pcb via the existing PCB parser.
    """
    components: list[Component] = []
    seen_refs: set[str] = set()
    visited_paths: set[str] = set()

    _parse_schematic_recursive(sch_path, components, seen_refs, visited_paths)

    log.info("Parsed KiCad legacy schematic: %d components", len(components))
    return components, []


def _parse_schematic_recursive(
    sch_path: Path,
    components: list[Component],
    seen_refs: set[str],
    visited_paths: set[str],
) -> None:
    """Parse a single .sch file, recursing into sub-sheets."""
    resolved = str(sch_path.resolve())
    if resolved in visited_paths:
        return
    visited_paths.add(resolved)

    try:
        text = sch_path.read_text(errors="replace")
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
            comp = _parse_comp_block(block, seen_refs)
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
                    _parse_schematic_recursive(sub_path, components, seen_refs, visited_paths)
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


def _parse_comp_block(lines: list[str], seen_refs: set[str]) -> Component | None:
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

    # Skip power symbols
    if ref.startswith("#"):
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

    attrs = build_attributes(raw_attrs)

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
    val = normalize_connector_value(val, package, ref)

    return Component(
        ref=ref,
        value=val,
        footprint=fp,
        package=package,
        attributes=attrs,
    )
