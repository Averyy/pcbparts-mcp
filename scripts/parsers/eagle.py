"""Eagle XML schematic + board file parser.

Parses .sch for components/nets and .brd for PCB positions.
Handles brand-specific conventions:
  - SparkFun: specs in deviceset names (0.1UF-25V-5%(0603)), PROD_ID attributes
  - Adafruit: BOM="EXCLUDE" for non-electrical parts, microbuilder library
  - Generic: ref-prefix-based junk filtering (FRAME, LOGO, FID, etc.)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET  # fallback if defusedxml not installed

from parse_boards import (
    Component, Net, Position, BoardOutline, DesignRules, CopperPour,
    normalize_footprint, normalize_value,
    extract_inline_specs, normalize_connector_value,
)
from parsers.common import (
    is_useful_description, truncate, build_attributes, value_or_symbol, keep_source_specs,
)

log = logging.getLogger(__name__)

# Ref prefixes that are never real components (Eagle keeps its own list
# because it does NOT skip test points — those get filtered by package)
_JUNK_REF_PREFIXES = ("FRAME", "LOGO", "FID", "STANDOFF")

# Eagle library names that contain only aesthetic/non-electrical parts
_JUNK_LIBRARIES = {"SparkFun-Aesthetics"}

# Deviceset name substrings that indicate non-electrical parts
_JUNK_DEVICESET_SUBSTRINGS = ("LOGO", "PASSER", "FIDUCIAL", "STAND-OFF", "STANDOFF")


def _is_junk_part(ref: str, lib: str, deviceset: str = "",
                  bom_attr: str | None = None) -> bool:
    """Check if a part is non-electrical (logo, frame, fiducial, etc.)."""
    if bom_attr and bom_attr.upper() == "EXCLUDE":
        return True
    if lib in _JUNK_LIBRARIES:
        return True
    ref_prefix = ref.rstrip("0123456789$")
    if ref_prefix in _JUNK_REF_PREFIXES:
        return True
    # Check deviceset name for junk patterns
    ds_upper = deviceset.upper()
    for pattern in _JUNK_DEVICESET_SUBSTRINGS:
        if pattern in ds_upper:
            return True
    # Bare pads (PAD, PAD-0.6-1.1) but NOT solder jumpers (PAD-JUMPER-*)
    if ds_upper == "PAD" or (ds_upper.startswith("PAD-") and "JUMPER" not in ds_upper):
        return True
    return False


def _build_library_lookups(lib_elements: dict[str, ET.Element]) -> tuple[
    dict[tuple[str, str, str, str], dict[str, str]],  # (lib, deviceset, device, technology) → attrs
    dict[tuple[str, str], str],                    # (lib, deviceset) → description
]:
    """Pre-build lookup dicts for tech attributes and descriptions in one pass.

    Avoids O(N*D) scanning per part by building O(1) lookup tables up front.
    """
    tech_lookup: dict[tuple[str, str, str, str], dict[str, str]] = {}
    desc_lookup: dict[tuple[str, str], str] = {}

    for lib_name, lib_elem in lib_elements.items():
        for ds in lib_elem.iter("deviceset"):
            ds_name = ds.get("name", "")

            # Cache description
            desc_elem = ds.find("description")
            if desc_elem is not None and desc_elem.text:
                html = desc_elem.text.strip()
                if html:
                    desc_lookup[(lib_name, ds_name)] = _clean_html_description(html)

            # Cache tech attributes per device
            for dev in ds.iter("device"):
                dev_name = dev.get("name", "")
                for tech in dev.iter("technology"):
                    attrs: dict[str, str] = {}
                    for attr in tech.iter("attribute"):
                        name = attr.get("name", "")
                        value = attr.get("value", "")
                        if name and value:
                            attrs[name] = value
                    if attrs:
                        tech_lookup[(lib_name, ds_name, dev_name, tech.get("name", ""))] = attrs

    return tech_lookup, desc_lookup


def _clean_html_description(html: str) -> str:
    """Extract a clean one-line summary from Eagle HTML description."""
    # Try <h3> first (usually the best summary)
    m = re.search(r"<h3>(.*?)</h3>", html, re.DOTALL | re.IGNORECASE)
    if m:
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        text = re.sub(r"^Description:\s*", "", text)
        if is_useful_description(text):
            return truncate(text, 80)

    # Try first <b> tag
    m = re.search(r"<b>(.*?)</b>", html, re.DOTALL | re.IGNORECASE)
    if m:
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        text = re.sub(r"^Description:\s*", "", text)
        if is_useful_description(text):
            return truncate(text, 80)

    # Fallback: strip all HTML, take first sentence
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^Description:\s*", "", text)
    first = text.split(".")[0].strip()
    if is_useful_description(first):
        return truncate(first, 80)
    return ""


def _parse_deviceset_specs(deviceset: str, device: str = "") -> dict[str, str]:
    """Extract specs from Eagle deviceset and device names like '0.1UF-25V-5%(0603)'.

    SparkFun encodes value, voltage, tolerance, and package in deviceset names ('1.0UF50V10%(1206)')
    or in the device name ('0.1UF' with device '-0603-25V-(+80/-20%)').
    """
    specs: dict[str, str] = {}
    if device:
        device_specs = _parse_deviceset_specs(device)
        specs.update({k: v for k, v in device_specs.items() if k == "voltage"})
        # A plain tolerance token ("-0603-50V-5%"), not a range ("(+80/-20%)")
        m = re.search(r"(?:^|-)(\d+(?:\.\d+)?)%(?:-|$)", device)
        if m:
            specs["tolerance"] = f"{m.group(1)}%"

    # Voltage: -25V, -16V, 50V10% — FemtoBuck's 1.0UF50V10% lost its 50 V to a word-boundary check;
    # "3V3" is no 3 V rating
    m = re.search(r"(?<![\d.])(\d+(?:\.\d+)?)V(?=$|[^A-Za-z0-9]|\d+(?:\.\d+)?%)", deviceset)
    if m:
        specs["voltage"] = f"{m.group(1)}V"

    # Tolerance: -1%, -5%, -10%
    m = re.search(r"(\d+)%", deviceset)
    if m:
        specs["tolerance"] = f"{m.group(1)}%"

    # Power rating: 1/10W, 1/4W, 1W (require preceding dash/start or fraction)
    m = re.search(r"(?:^|-)(\d+/\d+W)(?:-|$|\()", deviceset)
    if m:
        specs["power"] = m.group(1)
    else:
        m = re.search(r"(?:^|-)(\d+W)(?:-|$|\()", deviceset)
        if m:
            specs["power"] = m.group(1)

    return specs


def parse_schematic(sch_path: Path) -> tuple[list[Component], list[Net]]:
    """Parse an Eagle XML schematic file.

    Returns (components, nets). Positions come from .brd file separately.
    """
    tree = ET.parse(sch_path)
    root = tree.getroot()

    # Build library lookup: libraries[lib_name][deviceset_name][device_name] → package
    lib_packages: dict[str, dict[str, dict[str, str]]] = {}
    lib_elements: dict[str, ET.Element] = {}
    for lib_elem in root.iter("library"):
        lib_name = lib_elem.get("name", "")
        lib_elements[lib_name] = lib_elem
        lib_packages[lib_name] = {}
        for ds_elem in lib_elem.iter("deviceset"):
            ds_name = ds_elem.get("name", "")
            lib_packages[lib_name][ds_name] = {}
            for dev_elem in ds_elem.iter("device"):
                dev_name = dev_elem.get("name", "")
                dev_package = dev_elem.get("package", "")
                lib_packages[lib_name][ds_name][dev_name] = dev_package

    # Managed libraries can share a display name; select their URN before the name alias.
    # The alias keeps older schematics without library_urn working.
    for lib_elem in root.iter("library"):
        if urn := lib_elem.get("urn"):
            lib_elements[urn] = lib_elem
            lib_packages[urn] = {ds.get("name", ""): {dev.get("name", ""): dev.get("package", "")
                                  for dev in ds.iter("device")} for ds in lib_elem.iter("deviceset")}

    # Pre-build lookup tables for tech attributes and descriptions (O(1) per part)
    tech_lookup, desc_lookup = _build_library_lookups(lib_elements)

    # Parse parts
    components: list[Component] = []
    part_names: set[str] = set()

    for part in root.iter("part"):
        name = part.get("name", "")
        lib = part.get("library_urn") or part.get("library", "")
        deviceset = part.get("deviceset", "")
        device = part.get("device", "")
        # An empty value attribute reads as the deviceset, as a missing one does: SAMD21 (an ATSAMD21G),
        # SparkFun's named solder jumpers (MEAS, VE) and 5 mm LED bulbs were dropped for having none.
        # A jumper's default state is in its device name: SparkFun's SOLDERJUMPER, device NO
        full_name = f"{deviceset}_{device.strip('-_')}" if "JUMPER" in deviceset.upper() and device else deviceset
        value = value_or_symbol(part.get("value", full_name), full_name)

        # Look up package
        package = ""
        try:
            package = lib_packages[lib][deviceset][device]
        except KeyError:
            pass

        # Skip supply symbols (no package)
        if not package:
            log.debug("Skipping supply/no-package: %s (%s)", name, deviceset)
            continue

        # Extract technology attributes (PROD_ID, MPN, BOM, etc.)
        tech_attrs = tech_lookup.get((lib, deviceset, device, part.get("technology", "")), {})
        instance_attrs = {a.get("name", ""): a.get("value", "") for a in part.findall("attribute")}

        # Skip non-electrical parts
        if _is_junk_part(name, part.get("library", ""), deviceset, tech_attrs.get("BOM")):
            log.debug("Skipping non-electrical: %s (lib=%s, ds=%s)", name, lib, deviceset)
            continue

        part_names.add(name)

        ref = name
        fp = normalize_footprint(package, ref)

        # Build useful attributes dict via shared attribute mapper
        # Map each layer separately so aliases (MPN / MANUFACTURER_PART_NUMBER,
        # VOLTAGE / VOLTAGERATING, etc.) obey the same precedence as exact keys.
        # A passive's device name can carry its rating (BNO080's 0.1UF caps: device -0603-25V-(+80/-20%));
        # on other parts a V there is a variant, such as a regulator's output
        passive = re.match(r"^(?:R|C|L|FB)\d", name, re.IGNORECASE)
        attrs = _parse_deviceset_specs(deviceset, device if passive else "")
        attrs.update(build_attributes(tech_attrs))
        placed = value

        # Extract inline specs from value for passives (e.g. "1uF 60V", "75K 1%")
        ref_prefix = re.match(r"^([A-Z]+)", ref, re.IGNORECASE)
        ref_prefix = ref_prefix.group(1) if ref_prefix else ""
        if ref_prefix in ("R", "C", "L", "FB"):
            cleaned_val, inline_specs = extract_inline_specs(value)
            # Explicit specs in the placed value take precedence over the library.
            attrs.update(inline_specs)
            value = cleaned_val

        attrs.update(build_attributes(instance_attrs))

        # Extract deviceset description for non-passives
        if ref_prefix not in ("R", "C", "L", "FB"):
            desc = attrs.get("description", desc_lookup.get((lib, deviceset), ""))
            if desc:
                # For solder jumpers: replace ugly/empty values with description, unless the name
                # says whether it is normally open or closed
                if ref_prefix == "SJ" and (
                    value.upper().startswith("SOLDERJUMPER")
                    or value in (deviceset, full_name)  # value defaulted to deviceset name
                    or not value.strip()
                ) and not normalize_value(value, ref).endswith(("(NO)", "(NC)")):
                    value = desc.lower()
                else:
                    attrs.setdefault("description", desc)

        # SparkFun's standard I2C pinout on a 1 mm four-pin package is the Qwiic JST-SH connector
        # (BNO080 J2/J4, value "SMD", read "1x4 header" like a 2.54 mm header)
        if (deviceset.upper().startswith("I2C_STANDARD") and re.search(r"(?:^|_)1MM(?:_|$)", package, re.I)
                and value.upper() in ("SMD", "I2C", "I2C_STANDARD", deviceset.upper())):
            value = "QWIIC"
        val = normalize_value(value, ref)
        keep_source_specs(placed, val, ref, attrs)
        val = normalize_connector_value(val, package, ref)

        components.append(Component(
            ref=ref,
            value=val,
            footprint=fp,
            package=package,
            attributes=attrs,
        ))

    # Parse net classes: number → (name, width)
    net_classes: dict[str, tuple[str, str]] = {}
    for cls in root.iter("class"):
        num = cls.get("number", "0")
        name = cls.get("name", "default")
        width = cls.get("width", "0")
        if name != "default" or width != "0":
            net_classes[num] = (name, width if width != "0" else "")

    # Pass 1: scan all pinrefs to identify multi-gate parts (2+ gates)
    multi_gate_parts = _multi_gate_parts(root, part_names)

    # Pass 2: parse nets — merge across sheets, qualify multi-gate pins
    merged_pins: dict[str, set[str]] = {}
    merged_class: dict[str, tuple[str, str]] = {}
    for net_elem in root.iter("net"):
        net_name = net_elem.get("name", "")
        net_class_num = net_elem.get("class", "0")

        for pinref in net_elem.iter("pinref"):
            part = pinref.get("part", "")
            pin = pinref.get("pin", "")
            gate = pinref.get("gate", "")
            if part in part_names:
                # Strip Eagle >NAME placeholder from gate names
                if gate and gate.startswith(">"):
                    gate = gate.lstrip(">")
                if part in multi_gate_parts and gate:
                    pin_str = f"{part}.{gate}.{pin}"
                else:
                    pin_str = f"{part}.{pin}"
                merged_pins.setdefault(net_name, set()).add(pin_str)

        if net_name not in merged_class:
            cls_name, cls_width = net_classes.get(net_class_num, ("", ""))
            if cls_name or cls_width:
                merged_class[net_name] = (cls_name, cls_width)

    nets: list[Net] = []
    for net_name, pins in merged_pins.items():
        if len(pins) >= 2:
            cls_name, cls_width = merged_class.get(net_name, ("", ""))
            nets.append(Net(name=net_name, pins=sorted(pins),
                           net_class=cls_name, trace_width=cls_width))

    log.info("Parsed Eagle schematic: %d components, %d nets", len(components), len(nets))
    return components, nets


def _multi_gate_parts(root: ET.Element, part_names: set[str]) -> set[str]:
    """Parts wired through two or more gates: their net pins are named "gate.pin"."""
    part_gates: dict[str, set[str]] = {}
    for net_elem in root.iter("net"):
        for pinref in net_elem.iter("pinref"):
            part = pinref.get("part", "")
            gate = pinref.get("gate", "")
            if part in part_names and gate:
                part_gates.setdefault(part, set()).add(gate)
    return {p for p, gates in part_gates.items() if len(gates) > 1}


def extract_part_pins(sch_path: Path, part_names: set[str]
                      ) -> tuple[dict[str, dict[str, str]], dict[str, set[str]]]:
    """Every pin of each part, {ref: {label: pads}}, labelled as nets label them, and the pins that
    are connected though the board data may show no net for them ({ref: {label}}).

    A pin is a symbol pin the device connects to pads ("1" or "1 2 3" when it joins several). Supply
    pins (direction pwr) join the net of their own name without a wire, as a hidden VCC/GND gate's do.
    A pin whose net reaches only parts the parser drops (a bare pad, a test point) is connected too.
    """
    root = ET.parse(sch_path).getroot()
    symbols: dict[tuple[str, str], dict[str, str]] = {}
    gates: dict[tuple[str, str], dict[str, str]] = {}
    connects: dict[tuple[str, str, str], list[tuple[str, str, str]]] = {}
    libraries = {lib.get("name", ""): lib for lib in root.iter("library")}
    libraries.update({lib.get("urn"): lib for lib in root.iter("library") if lib.get("urn")})
    for lib_name, lib in libraries.items():
        for sym in lib.iter("symbol"):
            symbols[(lib_name, sym.get("name", ""))] = {pin.get("name", ""): pin.get("direction", "io")
                                                         for pin in sym.iter("pin")}
        for ds in lib.iter("deviceset"):
            ds_name = ds.get("name", "")
            gates[(lib_name, ds_name)] = {g.get("name", ""): g.get("symbol", "") for g in ds.iter("gate")}
            for dev in ds.iter("device"):
                connects[(lib_name, ds_name, dev.get("name", ""))] = [
                    (c.get("gate", ""), c.get("pin", ""), c.get("pad", "")) for c in dev.iter("connect")]

    multi_gate_parts = _multi_gate_parts(root, part_names)
    wired: dict[str, set[tuple[str, str]]] = {}
    net_members: dict[str, set[tuple[str, str, str]]] = {}  # merged across sheets by name, as nets are
    for net_elem in root.iter("net"):
        for pinref in net_elem.iter("pinref"):
            member = (pinref.get("part", ""), pinref.get("gate", "").lstrip(">"), pinref.get("pin", ""))
            wired.setdefault(member[0], set()).add(member[1:])
            net_members.setdefault(net_elem.get("name", ""), set()).add(member)
    reaches_other = {member for members in net_members.values() if len(members) >= 2 for member in members}
    pins: dict[str, dict[str, str]] = {}
    connected: dict[str, set[str]] = {}
    for part in root.iter("part"):
        ref, lib = part.get("name", ""), part.get("library_urn") or part.get("library", "")
        key = (lib, part.get("deviceset", ""), part.get("device", ""))
        if ref not in part_names or ref in pins or key not in connects:
            continue
        names = [pin for _, pin, _ in connects[key]]
        mine: dict[str, str] = {}
        for gate, pin, pad in connects[key]:
            gate_name = gate.lstrip(">")
            qualified = ref in multi_gate_parts and gate_name
            # A name two gates share ("MT" on two mounting tabs): the nets' bare name is the wired gate's
            if not qualified and names.count(pin) > 1 and (gate_name, pin) not in wired.get(ref, set()):
                qualified = bool(gate_name)
            label = f"{gate_name}.{pin}" if qualified else pin
            mine[label] = pad
            if (ref, gate_name, pin) in reaches_other:
                connected.setdefault(ref, set()).add(label)
            symbol = gates.get(key[:2], {}).get(gate, "")
            if symbols.get((lib, symbol), {}).get(pin) == "pwr":
                connected.setdefault(ref, set()).add(label)
        if mine:
            pins[ref] = mine
    return pins, connected


def parse_board(brd_path: Path, part_names: set[str]) -> tuple[list[Position], BoardOutline | None, DesignRules | None, list[CopperPour]]:
    """Parse an Eagle XML board file for component positions, outline, design rules, and copper pours.

    Returns (positions, outline, design_rules, copper_pours).
    """
    tree = ET.parse(brd_path)
    root = tree.getroot()

    positions: list[Position] = []
    seen: set[str] = set()

    for elem in root.iter("element"):
        name = elem.get("name", "")
        if name not in part_names or name in seen:
            continue
        seen.add(name)

        x = float(elem.get("x", "0"))
        y = float(elem.get("y", "0"))
        rot_str = elem.get("rot", "R0")
        rotation = float(re.sub(r"[^0-9.]", "", rot_str) or "0")

        positions.append(Position(ref=name, x=round(x, 2), y=round(y, 2), rotation=rotation))

    # Extract board outline from dimension layer (layer 20)
    outline = _extract_outline(root)
    design_rules = _extract_design_rules(root)
    copper_pours = _extract_copper_pours(root)

    log.info("Parsed Eagle board: %d positions, outline=%s, %d-layer, %d pours",
             len(positions),
             f"{outline.width}x{outline.height}mm" if outline else "none",
             design_rules.layers if design_rules else 0,
             len(copper_pours))
    return positions, outline, design_rules, copper_pours


def _extract_design_rules(root: ET.Element) -> DesignRules | None:
    """Extract design rules from Eagle .brd file."""
    dr_elem = root.find(".//designrules")
    if dr_elem is None:
        return None

    params: dict[str, str] = {}
    for param in dr_elem.iter("param"):
        params[param.get("name", "")] = param.get("value", "")

    # Derive layer count from layerSetup: "(1*16)" = 2 layers, "(1*2*15*16)" = 4 layers
    layers = 2
    setup = params.get("layerSetup", "")
    if setup:
        # Count copper layer numbers (1-16)
        layer_nums = re.findall(r"\d+", setup)
        if layer_nums:
            layers = len(layer_nums)

    return DesignRules(
        layers=layers,
        min_trace=params.get("msWidth", ""),
        min_clearance=params.get("mdWireWire", ""),
        min_drill=params.get("msDrill", ""),
        min_via=params.get("rlMinViaOuter", ""),
    )


def _extract_outline(root: ET.Element) -> BoardOutline | None:
    """Extract board dimensions from layer 20 (Dimension) wires."""
    xs: list[float] = []
    ys: list[float] = []

    for wire in root.iter("wire"):
        if wire.get("layer") != "20":
            continue
        xs.extend([float(wire.get("x1", "0")), float(wire.get("x2", "0"))])
        ys.extend([float(wire.get("y1", "0")), float(wire.get("y2", "0"))])

    if not xs or not ys:
        return None

    width = round(max(xs) - min(xs), 2)
    height = round(max(ys) - min(ys), 2)

    if width <= 0 or height <= 0:
        return None

    return BoardOutline(width=width, height=height)


# Eagle copper layer number → name mapping
_EAGLE_CU_LAYERS = {
    "1": "F.Cu", "2": "In1.Cu", "3": "In2.Cu", "4": "In3.Cu",
    "5": "In4.Cu", "6": "In5.Cu", "7": "In6.Cu", "8": "In7.Cu",
    "9": "In8.Cu", "10": "In9.Cu", "11": "In10.Cu", "12": "In11.Cu",
    "13": "In12.Cu", "14": "In13.Cu", "15": "In14.Cu", "16": "B.Cu",
}


def _extract_copper_pours(root: ET.Element) -> list[CopperPour]:
    """Extract copper pour polygons from Eagle .brd signals.

    Eagle stores pours as <polygon> elements inside <signal> elements.
    Polygons on copper layers (1-16) are fill zones.
    """
    # net name → set of layer names
    pour_layers: dict[str, set[str]] = {}

    signals_elem = root.find(".//signals")
    if signals_elem is None:
        return []

    for signal in signals_elem.findall("signal"):
        net_name = signal.get("name", "")
        if not net_name:
            continue
        # Skip auto-named Eagle nets (N$1, N$2, ...)
        if re.match(r"^N\$\d+$", net_name):
            continue
        for polygon in signal.findall("polygon"):
            layer_num = polygon.get("layer", "")
            layer_name = _EAGLE_CU_LAYERS.get(layer_num)
            if layer_name:
                pour_layers.setdefault(net_name, set()).add(layer_name)

    pours: list[CopperPour] = []
    for net_name, layers in sorted(pour_layers.items()):
        pours.append(CopperPour(net=net_name, layers=sorted(layers)))
    return pours
