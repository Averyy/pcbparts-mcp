"""KiCad S-expression schematic + PCB file parser.

Supports KiCad 6/7/8/9/10 (all use S-expression format).
Parses .kicad_sch for components/nets and .kicad_pcb for positions/outline/design rules.
Also parses .kicad_pro (JSON) for net classes and design rule constraints.

Net extraction uses the PCB file (pad → net assignments) rather than
tracing schematic wires, which is simpler and more reliable.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from parse_boards import (
    Component, Net, Position, BoardOutline, DesignRules, CopperPour,
    normalize_footprint, normalize_value,
    extract_inline_specs, normalize_connector_value,
)
from parsers.common import is_junk_ref, is_useful_description, truncate, build_attributes

log = logging.getLogger(__name__)

# Power symbol library names — symbols from these are supply markers, not components
_POWER_LIBS = {"power", "power_flag"}


# ---------------------------------------------------------------------------
# S-expression tokenizer + parser
# ---------------------------------------------------------------------------

def _tokenize(text: str):
    """Yield tokens from KiCad S-expression text.

    Tokens: '(', ')', or string values (quoted or unquoted).
    """
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in (' ', '\t', '\n', '\r'):
            i += 1
        elif c == '(':
            yield '('
            i += 1
        elif c == ')':
            yield ')'
            i += 1
        elif c == '"':
            # Quoted string — find matching close quote (handle escaped quotes)
            j = i + 1
            while j < n:
                if text[j] == '\\' and j + 1 < n:
                    j += 2
                elif text[j] == '"':
                    break
                else:
                    j += 1
            yield text[i + 1:j].replace('\\"', '"').replace('\\\\', '\\')
            i = j + 1
        else:
            # Unquoted token — read until whitespace or paren
            j = i
            while j < n and text[j] not in (' ', '\t', '\n', '\r', '(', ')'):
                j += 1
            yield text[i:j]
            i = j


def _parse_sexpr(text: str) -> list:
    """Parse S-expression text into nested lists.

    Each S-expression (a b c) becomes ['a', 'b', 'c'].
    Nested expressions become nested lists.
    """
    tokens = _tokenize(text)
    stack: list[list] = [[]]
    for tok in tokens:
        if tok == '(':
            new: list = []
            stack[-1].append(new)
            stack.append(new)
        elif tok == ')':
            if len(stack) > 1:
                stack.pop()
        else:
            stack[-1].append(tok)
    if len(stack) != 1:
        log.warning("Unbalanced S-expression: stack depth %d (expected 1)", len(stack))
    return stack[0]


# ---------------------------------------------------------------------------
# S-expression query helpers
# ---------------------------------------------------------------------------

def _find(node: list, tag: str) -> list | None:
    """Find first child node with given tag. Returns None if not found."""
    for child in node:
        if isinstance(child, list) and child and child[0] == tag:
            return child
    return None


def _find_all(node: list, tag: str):
    """Yield all child nodes with given tag."""
    for child in node:
        if isinstance(child, list) and child and child[0] == tag:
            yield child


def _get_str(node: list, tag: str, default: str = "") -> str:
    """Get string value of a simple (tag value) child node."""
    child = _find(node, tag)
    if child and len(child) >= 2 and isinstance(child[1], str):
        return child[1]
    return default


def _get_property(node: list, name: str) -> str:
    """Get a KiCad property value by name from a symbol/footprint node."""
    for child in _find_all(node, "property"):
        if len(child) >= 3 and child[1] == name:
            return child[2] if isinstance(child[2], str) else ""
    return ""


# ---------------------------------------------------------------------------
# Schematic parser
# ---------------------------------------------------------------------------

def parse_schematic(sch_path: Path, *, repo_root: Path | None = None) -> tuple[list[Component], list[Net]]:
    """Parse a KiCad S-expression schematic file.

    Returns (components, []) — nets come from PCB file.
    Multi-sheet schematics are handled by recursively parsing sub-sheets.
    ``repo_root`` bounds the path traversal check for sub-sheets (defaults to
    sch_path's parent when not given).
    """
    components: list[Component] = []
    seen_uuids: set[str] = set()
    seen_refs: set[str] = set()

    # Read root schematic to get project UUID for instance remapping
    text = sch_path.read_text(errors="replace")
    if "\ufffd" in text:
        log.warning("Replacement characters in %s — possible encoding issue", sch_path.name)
    tree = _parse_sexpr(text)
    root = tree[0] if tree and isinstance(tree[0], list) and tree[0] and tree[0][0] == "kicad_sch" else tree
    root_uuid = _get_str(root, "uuid")

    boundary = (repo_root or sch_path.parent).resolve()
    _parse_schematic_recursive(sch_path, components, seen_uuids, seen_refs,
                                root_uuid=root_uuid, inst_path=f"/{root_uuid}",
                                _cached=(root, text), boundary=boundary)

    log.info("Parsed KiCad schematic: %d components", len(components))
    return components, []


def _parse_schematic_recursive(sch_path: Path, components: list[Component],
                                seen_uuids: set[str], seen_refs: set[str], *,
                                root_uuid: str = "", inst_path: str = "",
                                _cached: tuple | None = None,
                                boundary: Path | None = None) -> None:
    """Parse a single .kicad_sch file, recursing into sub-sheets."""
    if _cached:
        root, text = _cached
    else:
        text = sch_path.read_text(errors="replace")
        tree = _parse_sexpr(text)
        root = tree[0] if tree and isinstance(tree[0], list) and tree[0] and tree[0][0] == "kicad_sch" else tree

    if boundary is None:
        boundary = sch_path.parent.resolve()

    # Parse symbol instances (actual placed components, not lib_symbols)
    for sym in _find_all(root, "symbol"):
        _process_symbol(sym, components, seen_uuids, seen_refs, inst_path=inst_path)

    # Recurse into sub-sheets
    for sheet in _find_all(root, "sheet"):
        sheet_file = _get_property(sheet, "Sheetfile") or _get_property(sheet, "Sheet file")
        if not sheet_file:
            sheet_file = _get_str(sheet, "file")
        if sheet_file:
            sub_path = (sch_path.parent / sheet_file).resolve()
            # Path containment check: sub-sheet must stay within the repo root
            if not sub_path.is_relative_to(boundary):
                log.warning("Sub-sheet path traversal blocked: %s", sheet_file)
            elif sub_path.exists() and sub_path != sch_path.resolve():
                sheet_uuid = _get_str(sheet, "uuid")
                sub_inst_path = f"{inst_path}/{sheet_uuid}" if sheet_uuid else inst_path
                _parse_schematic_recursive(sub_path, components, seen_uuids, seen_refs,
                                            root_uuid=root_uuid,
                                            inst_path=sub_inst_path,
                                            boundary=boundary)
            else:
                log.debug("Sub-sheet not found: %s", sub_path)


def _resolve_instance_ref(sym: list, inst_path: str) -> str | None:
    """Resolve project-specific reference from (instances) block.

    Sub-sheets reused across projects store per-project refs in:
      (instances (project "name" (path "/root_uuid/sheet_uuid" (reference "R8") ...)))

    Returns the resolved ref, or None if no remapping found.
    """
    instances = _find(sym, "instances")
    if not instances or not inst_path:
        return None

    for proj in _find_all(instances, "project"):
        for path_node in _find_all(proj, "path"):
            if len(path_node) >= 2 and path_node[1] == inst_path:
                ref_node = _find(path_node, "reference")
                if ref_node and len(ref_node) >= 2:
                    return ref_node[1]
    return None


def _process_symbol(sym: list, components: list[Component],
                     seen_uuids: set[str], seen_refs: set[str], *,
                     inst_path: str = "") -> None:
    """Process a single (symbol ...) block into a Component."""
    lib_id = _get_str(sym, "lib_id")

    # Skip power symbols
    lib_name = lib_id.split(":")[0] if ":" in lib_id else ""
    if lib_name.lower() in _POWER_LIBS:
        return

    # Skip DNP
    if _get_str(sym, "dnp") == "yes":
        return

    # Skip not-in-BOM components
    if _get_str(sym, "in_bom") == "no":
        return

    uuid = _get_str(sym, "uuid")
    if uuid in seen_uuids:
        return
    seen_uuids.add(uuid)

    # Resolve project-specific ref from instances block, fall back to property
    ref = _resolve_instance_ref(sym, inst_path) or _get_property(sym, "Reference")

    # Multi-unit components (e.g. resistor arrays) have multiple (symbol ...) blocks
    # with different (unit N) but the same Reference — deduplicate by ref
    if ref and ref in seen_refs:
        return

    # ref already resolved above
    value = _get_property(sym, "Value")
    footprint_raw = _get_property(sym, "Footprint")
    description = _get_property(sym, "Description")

    # Skip power symbols by ref prefix (#PWR, #FLG)
    if ref.startswith("#"):
        return

    # Skip symbols with no footprint (virtual/power symbols)
    if not footprint_raw:
        return

    # Skip junk references
    if is_junk_ref(ref):
        return

    # Track ref to deduplicate multi-unit components
    seen_refs.add(ref)

    # Strip library prefix from footprint: "Resistor_SMD:R_0402_1005Metric" → "R_0402_1005Metric"
    package = footprint_raw.split(":")[-1] if ":" in footprint_raw else footprint_raw
    fp = normalize_footprint(package, ref)

    # Collect custom properties → attributes
    raw_attrs: dict[str, str] = {}
    for prop in _find_all(sym, "property"):
        if len(prop) >= 3 and isinstance(prop[1], str) and isinstance(prop[2], str):
            key = prop[1]
            val = prop[2]
            # Skip standard KiCad properties
            if key in ("Reference", "Value", "Footprint", "Datasheet",
                       "Description", "ki_keywords", "ki_fp_filters",
                       "ki_description", "ki_locked"):
                continue
            if val and val != "~":
                raw_attrs[key] = val

    attrs = build_attributes(raw_attrs)

    # Add description if useful
    if description and is_useful_description(description) and "description" not in attrs:
        attrs["description"] = truncate(description, 80)

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

    components.append(Component(
        ref=ref,
        value=val,
        footprint=fp,
        package=package,
        attributes=attrs,
    ))


# ---------------------------------------------------------------------------
# PCB parser
# ---------------------------------------------------------------------------

def parse_pcb(pcb_path: Path, part_names: set[str], components: list[Component] | None = None
              ) -> tuple[list[Position], BoardOutline | None, DesignRules | None, list[Net], list[CopperPour]]:
    """Parse a KiCad PCB file in a single pass.

    Extracts positions, outline, design rules, nets, copper pours, and
    optionally enriches components with footprint properties (MPN, LCSC,
    DK, etc.) that may not be in the schematic.

    Returns (positions, outline, design_rules, nets, copper_pours).
    """
    text = pcb_path.read_text(errors="replace")
    if "\ufffd" in text:
        log.warning("Replacement characters in %s — possible encoding issue", pcb_path.name)
    tree = _parse_sexpr(text)
    root = tree[0] if tree and isinstance(tree[0], list) and tree[0] and tree[0][0] == "kicad_pcb" else tree

    positions = _extract_positions(root, part_names)
    outline = _extract_outline(root)
    design_rules = _extract_design_rules(root)
    nets = _extract_nets(root, part_names)
    copper_pours = _extract_copper_pours(root)

    if components:
        _enrich_from_footprints(root, components)

    log.info("Parsed KiCad PCB: %d positions, outline=%s, %d-layer, %d nets, %d pours",
             len(positions),
             f"{outline.width}x{outline.height}mm" if outline else "none",
             design_rules.layers if design_rules else 0,
             len(nets), len(copper_pours))
    return positions, outline, design_rules, nets, copper_pours


# Keep old API names as thin wrappers for backwards compat
def parse_board(pcb_path: Path, part_names: set[str]
                ) -> tuple[list[Position], BoardOutline | None, DesignRules | None]:
    """Parse PCB for positions/outline/rules only (legacy API)."""
    positions, outline, design_rules, _, _ = parse_pcb(pcb_path, part_names)
    return positions, outline, design_rules


def parse_pcb_nets(pcb_path: Path, part_names: set[str]) -> list[Net]:
    """Extract nets only (legacy API)."""
    _, _, _, nets, _ = parse_pcb(pcb_path, part_names)
    return nets


def enrich_from_pcb(pcb_path: Path, components: list[Component]) -> None:
    """Enrich components from PCB footprints (legacy API)."""
    parse_pcb(pcb_path, {c.ref for c in components}, components)


def _extract_nets(root: list, part_names: set[str]) -> list[Net]:
    """Extract nets from PCB pad→net assignments.

    KiCad PCBs can have multiple internal net IDs mapping to the same net name
    (e.g., after schematic edits). We merge all pins under the same name.
    """
    net_pins: dict[str, set[str]] = {}

    for fp_node in _iter_footprints(root):
        ref = _get_fp_ref(fp_node)
        if not ref or ref not in part_names:
            continue

        # Pass 1: collect (pad_num, pinfunction, net_name) tuples
        pad_info: list[tuple[str, str, str]] = []
        for pad in _find_all(fp_node, "pad"):
            if len(pad) < 2:
                continue
            pad_num = pad[1]
            net_node = _find(pad, "net")
            if net_node:
                # KiCad <=9: (net 42 "VCC") — index 2 is the name
                # KiCad 10+: (net "VCC")    — index 1 is the name (netcodes removed)
                if len(net_node) >= 3:
                    net_name = net_node[2]
                elif len(net_node) == 2:
                    net_name = net_node[1]
                else:
                    continue
                if net_name:
                    pinfunc = _get_str(pad, "pinfunction")
                    pad_info.append((pad_num, pinfunc, net_name))

        # Pass 2: detect duplicate pin labels, disambiguate with @pad_num
        label_counts: dict[str, int] = {}
        for pad_num, pinfunc, _ in pad_info:
            label = pinfunc if pinfunc else pad_num
            label_counts[label] = label_counts.get(label, 0) + 1

        for pad_num, pinfunc, net_name in pad_info:
            if pinfunc and label_counts.get(pinfunc, 0) <= 1:
                pin = f"{ref}.{pinfunc}"
            elif pinfunc and label_counts.get(pinfunc, 0) > 1:
                pin = f"{ref}.{pinfunc}@{pad_num}"
            else:
                pin = f"{ref}.{pad_num}"
            net_pins.setdefault(net_name, set()).add(pin)

    nets: list[Net] = []
    for net_name, pins in net_pins.items():
        if len(pins) >= 2:
            nets.append(Net(name=net_name, pins=sorted(pins)))
    return nets


def _extract_copper_pours(root: list) -> list[CopperPour]:
    """Extract copper pour/zone info from KiCad PCB.

    Aggregates zones by net name → unique layer list. Keepout zones
    (copperpour not_allowed) are flagged. Auto-named nets are skipped.
    """
    # net → set of layers, keepout net → set of layers
    pour_layers: dict[str, set[str]] = {}
    keepout_layers: dict[str, set[str]] = {}

    for zone in _find_all(root, "zone"):
        net_name = _get_str(zone, "net_name")
        layer = _get_str(zone, "layer")
        # Multi-layer zones use (layers ...) instead of (layer ...)
        if not layer:
            layers_node = _find(zone, "layers")
            if layers_node:
                layer_list = [s for s in layers_node[1:] if isinstance(s, str)]
            else:
                layer_list = []
        else:
            layer_list = [layer]

        # Check if this is a keepout zone
        keepout_node = _find(zone, "keepout")
        is_keepout = False
        if keepout_node:
            for child in keepout_node[1:]:
                if isinstance(child, list) and len(child) >= 2:
                    if child[0] == "copperpour" and child[1] == "not_allowed":
                        is_keepout = True
                        break

        target = keepout_layers if is_keepout else pour_layers
        for lyr in layer_list:
            if not lyr or not lyr.endswith(".Cu"):
                continue
            target.setdefault(net_name, set()).add(lyr)

    # Build result — skip auto-named nets (Net-(...)) and empty nets for pours
    _AUTO_NET = re.compile(r"^Net-\(")
    pours: list[CopperPour] = []
    for net_name, layers in sorted(pour_layers.items()):
        if not net_name or _AUTO_NET.match(net_name):
            continue
        pours.append(CopperPour(net=net_name, layers=sorted(layers)))
    for net_name, layers in sorted(keepout_layers.items()):
        pours.append(CopperPour(net=net_name or "", layers=sorted(layers), keepout=True))

    return pours


def _enrich_from_footprints(root: list, components: list[Component]) -> None:
    """Fill in component attributes from PCB footprint properties.

    KiCad copies custom properties (MPN, LCSC, DK, etc.) onto PCB footprints.
    If the schematic didn't have a property but the PCB does, fill it in.
    """
    comp_map: dict[str, Component] = {c.ref: c for c in components}

    enriched = 0
    for fp_node in _iter_footprints(root):
        ref = _get_fp_ref(fp_node)
        if not ref or ref not in comp_map:
            continue

        raw_attrs: dict[str, str] = {}
        for prop in _find_all(fp_node, "property"):
            if len(prop) >= 3 and isinstance(prop[1], str) and isinstance(prop[2], str):
                key = prop[1]
                val = prop[2]
                if key in ("Reference", "Value", "Footprint", "Datasheet",
                           "Description", "Sheetfile", "Sheetname",
                           "ki_description", "ki_keywords", "ki_fp_filters"):
                    continue
                if val and val != "~":
                    raw_attrs[key] = val

        if not raw_attrs:
            continue

        pcb_attrs = build_attributes(raw_attrs)
        comp = comp_map[ref]
        for key, val in pcb_attrs.items():
            if key not in comp.attributes:
                comp.attributes[key] = val
                enriched += 1

    if enriched:
        log.info("Enriched %d attributes from PCB footprint properties", enriched)


def _iter_footprints(root: list):
    """Iterate footprint/module nodes (KiCad 4/5 uses 'module', 6+ uses 'footprint')."""
    yield from _find_all(root, "footprint")
    yield from _find_all(root, "module")


def _get_fp_ref(fp_node: list) -> str:
    """Get Reference from a footprint node — handles KiCad 4/5/7/8+ formats.

    KiCad 8+: (property "Reference" "R1" ...)
    KiCad 7:  (fp_text reference "R1" ...)
    KiCad 4/5: (fp_text reference "R1" ...)  (inside module node)
    """
    ref = _get_property(fp_node, "Reference")
    if ref:
        return ref
    # KiCad 4/5/7 format: (fp_text reference "R1" ...)
    for child in _find_all(fp_node, "fp_text"):
        if len(child) >= 3 and child[1] == "reference":
            return child[2] if isinstance(child[2], str) else ""
    return ""


def _extract_positions(root: list, part_names: set[str]) -> list[Position]:
    """Extract component positions from (footprint ...) blocks."""
    positions: list[Position] = []
    seen: set[str] = set()

    for fp_node in _iter_footprints(root):
        ref = _get_fp_ref(fp_node)
        if not ref or ref not in part_names or ref in seen:
            continue
        seen.add(ref)

        at_node = _find(fp_node, "at")
        if not at_node or len(at_node) < 3:
            continue

        try:
            x = float(at_node[1])
            y = float(at_node[2])
            rotation = float(at_node[3]) if len(at_node) > 3 else 0.0
        except (ValueError, IndexError):
            continue

        # Determine component side from footprint layer
        layer = _get_str(fp_node, "layer")
        side = "back" if layer == "B.Cu" else ""

        positions.append(Position(ref=ref, x=round(x, 2), y=round(y, 2),
                                  rotation=rotation, side=side))

    return positions


def _extract_outline(root: list) -> BoardOutline | None:
    """Extract board dimensions from Edge.Cuts layer graphics."""
    xs: list[float] = []
    ys: list[float] = []

    for tag in ("gr_line", "gr_rect", "gr_arc", "gr_circle", "gr_poly"):
        for elem in _find_all(root, tag):
            layer = _get_str(elem, "layer")
            if layer != "Edge.Cuts":
                continue

            if tag == "gr_line":
                start = _find(elem, "start")
                end = _find(elem, "end")
                if start and len(start) >= 3:
                    xs.append(float(start[1]))
                    ys.append(float(start[2]))
                if end and len(end) >= 3:
                    xs.append(float(end[1]))
                    ys.append(float(end[2]))

            elif tag == "gr_rect":
                start = _find(elem, "start")
                end = _find(elem, "end")
                if start and len(start) >= 3:
                    xs.append(float(start[1]))
                    ys.append(float(start[2]))
                if end and len(end) >= 3:
                    xs.append(float(end[1]))
                    ys.append(float(end[2]))

            elif tag == "gr_arc":
                # Arcs have start, mid, end points
                for pt_tag in ("start", "mid", "end"):
                    pt = _find(elem, pt_tag)
                    if pt and len(pt) >= 3:
                        xs.append(float(pt[1]))
                        ys.append(float(pt[2]))

            elif tag == "gr_circle":
                center = _find(elem, "center")
                end = _find(elem, "end")
                if center and end and len(center) >= 3 and len(end) >= 3:
                    cx, cy = float(center[1]), float(center[2])
                    ex, ey = float(end[1]), float(end[2])
                    r = ((ex - cx) ** 2 + (ey - cy) ** 2) ** 0.5
                    xs.extend([cx - r, cx + r])
                    ys.extend([cy - r, cy + r])

            elif tag == "gr_poly":
                pts = _find(elem, "pts")
                if pts:
                    for xy in _find_all(pts, "xy"):
                        if len(xy) >= 3:
                            xs.append(float(xy[1]))
                            ys.append(float(xy[2]))

    if not xs or not ys:
        return None

    width = round(max(xs) - min(xs), 2)
    height = round(max(ys) - min(ys), 2)

    if width <= 0 or height <= 0:
        return None

    return BoardOutline(width=width, height=height)


def _fmt_mm(v: float) -> str:
    """Format a mm value for design rules output."""
    return f"{round(v, 3):g}mm"


def _extract_design_rules(root: list) -> DesignRules | None:
    """Extract design rules from KiCad PCB setup section and net classes.

    Sources (in priority order):
    1. Setup section: trace_min, trace_clearance, via_min_size, via_min_drill (KiCad 5)
    2. Default net_class: clearance, trace_width, via_dia, via_drill (KiCad 5/6)
    3. .kicad_pro enrichment fills remaining gaps (called separately)
    """
    setup = _find(root, "setup")

    # Count copper layers from (layers ...) section
    layers_node = _find(root, "layers")
    layer_count = 0
    if layers_node:
        for child in layers_node:
            if isinstance(child, list) and len(child) >= 3:
                name = child[1] if isinstance(child[1], str) else ""
                layer_type = child[2] if len(child) > 2 and isinstance(child[2], str) else ""
                if layer_type in ("signal", "power") or name.endswith(".Cu"):
                    layer_count += 1

    if layer_count == 0:
        layer_count = 2  # default

    min_trace = ""
    min_clearance = ""
    min_drill = ""
    min_via = ""

    # Extract from setup section (KiCad 5 stores these directly)
    if setup:
        trace_min = _get_str(setup, "trace_min")
        if trace_min and trace_min != "0":
            try:
                min_trace = _fmt_mm(float(trace_min))
            except ValueError:
                pass

        trace_clr = _get_str(setup, "trace_clearance")
        if trace_clr and trace_clr != "0":
            try:
                min_clearance = _fmt_mm(float(trace_clr))
            except ValueError:
                pass

        via_min_s = _get_str(setup, "via_min_size")
        if via_min_s and via_min_s != "0":
            try:
                min_via = _fmt_mm(float(via_min_s))
            except ValueError:
                pass

        via_min_d = _get_str(setup, "via_min_drill")
        if via_min_d and via_min_d != "0":
            try:
                min_drill = _fmt_mm(float(via_min_d))
            except ValueError:
                pass

    # Fallback: extract from Default net_class (KiCad 5/6 store these in PCB)
    for nc in _find_all(root, "net_class"):
        nc_name = nc[1] if len(nc) > 1 and isinstance(nc[1], str) else ""
        if nc_name != "Default":
            continue

        if not min_trace:
            tw = _get_str(nc, "trace_width")
            if tw and tw != "0":
                try:
                    min_trace = _fmt_mm(float(tw))
                except ValueError:
                    pass

        if not min_clearance:
            clr = _get_str(nc, "clearance")
            if clr and clr != "0":
                try:
                    min_clearance = _fmt_mm(float(clr))
                except ValueError:
                    pass

        if not min_via:
            vd = _get_str(nc, "via_dia")
            if vd and vd != "0":
                try:
                    min_via = _fmt_mm(float(vd))
                except ValueError:
                    pass

        if not min_drill:
            vdr = _get_str(nc, "via_drill")
            if vdr and vdr != "0":
                try:
                    min_drill = _fmt_mm(float(vdr))
                except ValueError:
                    pass
        break

    return DesignRules(
        layers=layer_count,
        min_trace=min_trace,
        min_clearance=min_clearance,
        min_via=min_via,
        min_drill=min_drill,
    )


# ---------------------------------------------------------------------------
# .kicad_pro parser (JSON project file)
# ---------------------------------------------------------------------------

def enrich_from_project(pro_path: Path, design_rules: DesignRules | None,
                         nets: list[Net]) -> DesignRules:
    """Enrich design rules and net classes from .kicad_pro JSON project file.

    The .kicad_pro contains:
    - board.design_settings.rules: min_track_width, min_clearance, min_via, min_drill
    - net_settings.classes: per-class track width, clearance, via size
    - board.design_settings.track_widths: available track width presets
    - board.design_settings.via_dimensions: available via presets
    """
    try:
        pro = json.loads(pro_path.read_text(errors="replace"))
    except (json.JSONDecodeError, OSError) as e:
        log.debug("Could not parse %s: %s", pro_path, e)
        return design_rules or DesignRules()

    dr = design_rules or DesignRules()

    # Extract design rules from board.design_settings.rules
    rules = pro.get("board", {}).get("design_settings", {}).get("rules", {})
    if rules:
        min_track = rules.get("min_track_width")
        if min_track and not dr.min_trace:
            dr.min_trace = _fmt_mm(min_track)
        min_clr = rules.get("min_clearance")
        if min_clr and min_clr > 0 and not dr.min_clearance:
            dr.min_clearance = _fmt_mm(min_clr)
        min_via = rules.get("min_via_diameter")
        if min_via and not dr.min_via:
            dr.min_via = _fmt_mm(min_via)
        min_drill = rules.get("min_through_hole_diameter")
        if min_drill and not dr.min_drill:
            dr.min_drill = _fmt_mm(min_drill)

    # Extract net classes and assign to nets
    net_classes = pro.get("net_settings", {}).get("classes", [])
    if net_classes:
        # Build net_name → class_info mapping
        class_map: dict[str, dict] = {}
        default_cls: dict = {}
        for cls in net_classes:
            cls_name = cls.get("name", "Default")
            if cls_name == "Default":
                default_cls = cls
            for net_name in cls.get("nets", []):
                class_map[net_name] = cls

        # Fallback: use Default net class for missing design rules
        if default_cls:
            if not dr.min_trace:
                tw = default_cls.get("track_width")
                if tw and tw > 0:
                    dr.min_trace = _fmt_mm(tw)
            if not dr.min_clearance:
                clr = default_cls.get("clearance")
                if clr and clr > 0:
                    dr.min_clearance = _fmt_mm(clr)
            if not dr.min_via:
                vd = default_cls.get("via_diameter")
                if vd and vd > 0:
                    dr.min_via = _fmt_mm(vd)
            if not dr.min_drill:
                vdr = default_cls.get("via_drill")
                if vdr and vdr > 0:
                    dr.min_drill = _fmt_mm(vdr)

        # Apply net class info to matching nets
        for net in nets:
            cls_info = class_map.get(net.name)
            if cls_info:
                cls_name = cls_info.get("name", "")
                if cls_name and cls_name != "Default":
                    net.net_class = cls_name
                track = cls_info.get("track_width")
                if track and track > 0:
                    net.trace_width = str(track)

    enriched_count = sum(1 for n in nets if n.net_class)
    if enriched_count:
        log.info("Enriched %d nets with class info from .kicad_pro", enriched_count)

    return dr
