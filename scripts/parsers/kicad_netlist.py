"""Schematic connectivity via KiCad's native exporter, when no usable layout exists.

KiCad resolves wire junctions, labels, power pins, transforms, multi-unit symbols
and sheet instances. Do not approximate those rules from drawing coordinates.
This optional offline build dependency is never needed to read a board database.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from defusedxml import ElementTree as ET

from parse_boards import Net
from parsers.kicad import _pin_label


def read_netlist(path: Path, part_refs: set[str]
                 ) -> tuple[list[Net], dict[str, dict[str, str]], dict[str, set[str]]]:
    """Read native XML; return nets, all symbol pins, and connected pins.

    Keep pad numbers internally so stacked pins count once. Label pins using the
    same convention as PCB nets, and retain connectivity to excluded components
    when deciding which pins are NC.
    """
    root = ET.parse(path).getroot()
    parts = {c.get("ref", ""): c for c in root.findall("./components/comp")}
    missing = part_refs - parts.keys()
    if missing:
        raise ValueError("KiCad export is missing components (symbol libraries unavailable?): "
                         + ", ".join(sorted(missing)))
    libraries = {}
    for lib in root.findall("./libparts/libpart"):
        libraries[(lib.get("lib"), lib.get("part"))] = {
            p.get("num", ""): p.get("name", "") for p in lib.findall("./pins/pin")}
    pins: dict[str, dict[str, str]] = {}
    labels: dict[tuple[str, str], str] = {}
    for ref in part_refs:
        source = parts[ref].find("libsource")
        if source is None or (source.get("lib"), source.get("part")) not in libraries:
            raise ValueError(f"KiCad export has no pin definitions for {ref}")
        names = libraries[(source.get("lib"), source.get("part"))]
        counts = {name: list(names.values()).count(name) for name in set(names.values())}
        pins[ref] = {}
        for number, name in names.items():
            label = _pin_label(number, name if name != "~" else "", counts)
            pins[ref][label] = number
            labels[(ref, number)] = label
    merged: dict[str, set[str]] = {}
    connected: dict[str, set[str]] = {}
    for net in root.findall("./nets/net"):
        nodes = {(p.get("ref", ""), p.get("pin", "")) for p in net.findall("node")}
        # Native export includes singleton unconnected/NC nets. They are not connections.
        if len(nodes) < 2:
            continue
        for ref, number in nodes:
            if ref not in part_refs:
                continue
            if (ref, number) not in labels:
                raise ValueError(f"KiCad export has an undefined pin: {ref}.{number}")
            label = labels[(ref, number)]
            connected.setdefault(ref, set()).add(label)
            merged.setdefault(net.get("name", ""), set()).add(f"{ref}.{label}")
    nets = [Net(name=name, pins=sorted(members)) for name, members in merged.items() if len(members) >= 2]
    return nets, pins, connected


def export_schematic(sch_path: Path, part_refs: set[str]
                     ) -> tuple[list[Net], dict[str, dict[str, str]], dict[str, set[str]]]:
    """Export without changing source files or fetching libraries from the network.

    Missing tools, failed exports and incomplete legacy symbol caches are explicit
    errors. In particular, KiCad can exit successfully with an empty legacy export.
    """
    with tempfile.TemporaryDirectory(prefix="board-netlist-") as temp:
        if sch_path.suffix == ".sch":
            from parsers.kicad_legacy_export import stage_schematic
            sch_path = stage_schematic(sch_path, Path(temp))
        output = Path(temp) / "netlist.xml"
        result = subprocess.run(
            ["kicad-cli", "sch", "export", "netlist", "--format", "kicadxml",
             "--output", str(output), str(sch_path.resolve())],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode or not output.is_file():
            raise ValueError(f"KiCad netlist export failed: {result.stderr.strip() or result.stdout.strip()}")
        return read_netlist(output, part_refs)
