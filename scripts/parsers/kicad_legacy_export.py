"""Stage legacy symbols/wires for KiCad CLI, which does not link legacy libraries.

Only electrical data is translated. Pin coordinates come verbatim from the
project's symbol cache, transformed by each symbol's integer placement matrix.
KiCad still resolves all junctions, labels, power nets and sheet connections.
The source project is never modified; unsupported buses fail explicitly.
"""

from __future__ import annotations

import json
import re
import shlex
import uuid
from pathlib import Path


def stage_schematic(source: Path, destination: Path) -> Path:
    """Create a temporary modern schematic hierarchy using a complete legacy cache."""
    cache = source.with_name(source.stem + "-cache.lib")
    text = cache.read_text(encoding="utf-8")
    definitions = {}
    for block in re.findall(r"^DEF\s+(.*?)^ENDDEF", text, re.M | re.S):
        name = block.split()[0]
        definitions[name] = block
        alias = re.search(r"^ALIAS\s+(.+)", block, re.M)
        if alias:
            for name in alias[1].split():
                definitions[name] = block

    quote = lambda value: json.dumps(str(value), ensure_ascii=False)
    mm = lambda value: f"{int(value) * 0.0254:.6f}".rstrip("0").rstrip(".") or "0"
    uid = lambda: str(uuid.uuid4())
    effects = '(effects (font (size 1.27 1.27)))'
    boundary = source.parent.resolve()
    project = "legacy"
    root_id = uid()

    def visit(path: Path, sheet_ids: list[str], legacy_path: str, active: set[Path]) -> Path:
        path = path.resolve()
        if not path.is_relative_to(boundary) or path in active:
            raise ValueError(f"Invalid legacy sheet path: {path}")
        text = path.read_text(encoding="utf-8")
        if re.search(r"^(Wire Bus|Entry |BusAlias )", text, re.M):
            raise ValueError(f"Legacy buses are not supported by the CLI staging adapter: {path}")
        output = destination / (sheet_ids[-1] + ".kicad_sch")
        libraries, items = [], []
        for block in re.findall(r"^\$Comp\s*\n(.*?)^\$EndComp", text, re.M | re.S):
            lib_id, ref = re.search(r"^L\s+(\S+)\s+(\S+)", block, re.M).groups()
            unit, convert, stamp = re.search(r"^U\s+(\S+)\s+(\S+)\s+(\S+)", block, re.M).groups()
            if convert != "1":
                raise ValueError(f"Legacy alternate symbol body is unsupported: {ref}")
            annotations = dict(re.findall(r'^AR Path="([^"]+)" Ref="([^"]+)"', block, re.M))
            ref = {p.upper(): r for p, r in annotations.items()}.get(f"{legacy_path}/{stamp}".upper(), ref)
            definition = definitions.get(lib_id.replace(":", "_"))
            if definition is None:
                raise ValueError(f"Legacy symbol cache has no definition for {lib_id} ({ref})")
            header = shlex.split(definition.splitlines()[0])
            px, py = re.search(r"^P\s+(-?\d+)\s+(-?\d+)", block, re.M).groups()
            matrices = re.findall(r"^\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s*$", block, re.M)
            a, b, c, d = map(int, matrices[-1])
            if sorted((a*a + b*b, c*c + d*d)) != [1, 1] or a*c + b*d:
                raise ValueError(f"Invalid legacy symbol transform: {ref}")
            fields = dict(re.findall(r'^F\s+(\d+)\s+"([^"]*)"', block, re.M))
            symbol_name = f"S{sheet_ids[-1].replace('-', '')}_{len(libraries)}"
            symbol_id = f"Legacy:{symbol_name}"
            bodies = {}
            for line in re.findall(r"^X\s+(.+)", definition, re.M):
                pin = shlex.split(line)
                name, number, x, y = pin[:4]
                x, y = int(x), int(y)
                pin_unit, body = pin[8:10]
                # The modern symbol library has Y up; the placement matrix produces screen Y down.
                at = f'{mm(a*x+b*y)} {mm(-c*x-d*y)}'
                kind = {'I': 'input', 'O': 'output', 'B': 'bidirectional', 'T': 'tri_state',
                        'P': 'passive', 'U': 'unspecified', 'W': 'power_in', 'w': 'power_out',
                        'C': 'open_collector', 'E': 'open_emitter', 'N': 'no_connect'}[pin[10]]
                hidden = 'hide' if len(pin) > 11 and 'N' in pin[11] else ''
                bodies.setdefault((pin_unit, body), []).append(
                    f'(pin {kind} line (at {at} 0) (length 0) {hidden}'
                    f' (name {quote(name)} {effects}) (number {quote(number)} {effects}))')
            power = '(power)' if header[-1] == 'P' else ''
            drawings = ''.join(f'(symbol "{symbol_name}_{u}_{body}" {"".join(pins)})'
                               for (u, body), pins in bodies.items())
            libraries.append(f'(symbol {quote(symbol_id)} {power} (in_bom yes) (on_board yes)'
                             f' (property "Reference" {quote(header[1])} (at 0 0 0) {effects})'
                             f' (property "Value" {quote(fields.get("1", lib_id))} (at 0 0 0) {effects})'
                             f' {drawings})')
            properties = ''.join(f'(property {quote(key)} {quote(value)} (at {mm(px)} {mm(py)} 0) {effects})'
                                 for key, value in [('Reference', ref), ('Value', fields.get('1', lib_id)),
                                                    ('Footprint', fields.get('2', ''))])
            items.append(f'(symbol (lib_id {quote(symbol_id)}) (at {mm(px)} {mm(py)} 0) (unit {unit})'
                         f' (in_bom yes) (on_board yes) (uuid {uid()}) {properties}'
                         f' (instances (project {quote(project)} (path {quote("/" + "/".join(sheet_ids))}'
                         f' (reference {quote(ref)}) (unit {unit})))))')
        for match in re.finditer(r"^Wire Wire Line\s*\n\s*(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)", text, re.M):
            x1, y1, x2, y2 = map(mm, match.groups())
            items.append(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2}))'
                         f' (stroke (width 0) (type default)) (uuid {uid()}))')
        for kind, x, y in re.findall(r"^(Connection|NoConn) ~ (-?\d+) (-?\d+)", text, re.M):
            tag = 'junction' if kind == 'Connection' else 'no_connect'
            extra = '(diameter 0) (color 0 0 0 0)' if kind == 'Connection' else ''
            items.append(f'({tag} (at {mm(x)} {mm(y)}) {extra} (uuid {uid()}))')
        for kind, x, y, angle, size, shape, name in re.findall(
                r"^Text (Label|HLabel|GLabel)\s+(-?\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s+(\S+)[^\n]*\n([^\n]+)", text, re.M):
            tag = {'Label': 'label', 'HLabel': 'hierarchical_label', 'GLabel': 'global_label'}[kind]
            shape = {'Input': 'input', 'Output': 'output', 'BiDi': 'bidirectional',
                     '3State': 'tri_state', 'UnSpc': 'passive', '~': 'passive'}[shape]
            extra = f'(shape {shape})' if kind != 'Label' else ''
            items.append(f'({tag} {quote(name)} (at {mm(x)} {mm(y)} {int(angle)*90})'
                         f' {extra} {effects} (uuid {uid()}))')
        for block in re.findall(r"^\$Sheet\s*\n(.*?)^\$EndSheet", text, re.M | re.S):
            x, y, w, h = re.search(r"^S\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", block, re.M).groups()
            stamp = re.search(r"^U\s+(\S+)", block, re.M)[1]
            name = re.search(r'^F0\s+"([^"]+)"', block, re.M)[1]
            file = re.search(r'^F1\s+"([^"]+)"', block, re.M)[1]
            sheet_id = uid()
            child = visit(path.parent / file, sheet_ids + [sheet_id], f'{legacy_path}/{stamp}', active | {path})
            pins = []
            for label, direction, side, xx, yy in re.findall(
                    r'^F(?:[2-9]|\d{2,})\s+"([^"]+)"\s+(\S)\s+(\S)\s+(\d+)\s+(\d+)', block, re.M):
                shape = {'I': 'input', 'O': 'output', 'B': 'bidirectional', 'T': 'tri_state', 'U': 'passive'}[direction]
                angle = {'L': 180, 'R': 0, 'T': 90, 'B': 270}[side]
                pins.append(f'(pin {quote(label)} {shape} (at {mm(xx)} {mm(yy)} {angle}) {effects} (uuid {uid()}))')
            items.append(f'(sheet (at {mm(x)} {mm(y)}) (size {mm(w)} {mm(h)}) (uuid {sheet_id})'
                         f' (property "Sheetname" {quote(name)} (at {mm(x)} {mm(y)} 0) {effects})'
                         f' (property "Sheetfile" {quote(child.name)} (at {mm(x)} {mm(y)} 0) {effects})'
                         f' {"".join(pins)})')
        output.write_text(f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet_ids[-1]})'
                          f' (paper "A1") (lib_symbols {"".join(libraries)}) {"".join(items)})\n',
                          encoding="utf-8")
        return output

    return visit(source, [root_id], '', set())
