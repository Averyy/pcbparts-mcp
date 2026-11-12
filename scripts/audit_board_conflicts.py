"""Offline audit of placed board values against ordering codes and descriptions.

This reports candidates for source review; it never changes a placed value or
assumes that two different ICs are approved substitutes. Unknown MPN schemes
remain unchecked. Run with --output to retain the complete row-level inventory.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import yaml

from parse_boards import _decode_eia_cap, _decode_mpn_value, _format_value


_TOLERANCE = {"F": "1%", "G": "2%", "J": "5%", "K": "10%", "M": "20%"}
_VOLTAGE = {"0J": "6.3V", "1A": "10V", "1C": "16V", "1E": "25V",
            "1H": "50V", "1V": "35V", "1J": "63V", "2A": "100V",
            "2D": "200V", "2E": "250V", "2J": "630V", "3A": "1000V"}
_DIELECTRIC = {"R6": "X5R", "R7": "X7R", "C7": "X7S", "D7": "X7T", "5C": "C0G"}


def _cap(code: str, tolerance: str, voltage: str | None = None,
         dielectric: str | None = None) -> dict[str, str]:
    value = (_format_value(float(code.replace("R", ".")) * 1e-12, "F")
             if "R" in code else _decode_eia_cap(code))
    result = {"value": value}
    tol = {"B": "0.1pF", "C": "0.25pF", "D": "0.5pF", **_TOLERANCE}.get(tolerance)
    for field, spec in (("tolerance", tol), ("voltage", voltage), ("dielectric", dielectric)):
        if spec:
            result[field] = spec
    return result


def _resistance(code: str) -> str | None:
    if re.fullmatch(r"\d+[RKM]\d*", code):
        number = re.sub(r"[RKM]", ".", code)
        scale = 1e6 if "M" in code else 1e3 if "K" in code else 1
        return _format_value(float(number) * scale, "ohm")
    if re.fullmatch(r"\d{3,4}", code):
        return _format_value(int(code[:-1]) * 10 ** int(code[-1]), "ohm")
    return None


def decode_passive_mpn(mpn: str, prefix: str) -> dict[str, str]:
    """Decode only identified maker families with fixed field boundaries.

    Capacitor EIA codes are in pF (8/9 are fractional multipliers); resistor
    numeric codes are in ohms. B/C/D capacitor tolerances are absolute pF,
    unlike the same letters on precision resistors. No generic digit search.
    """
    upper = mpn.strip().upper()
    if prefix == "C":
        # Murata: series + size/height + temperature + voltage + value + tolerance.
        m = re.fullmatch(r"(?:GRM|GCM|GQM|GJM|GRJ|GCJ|GRT|ZRB|KRM)[A-Z0-9]{3}"
                         r"([A-Z0-9]{2})([0-3][A-Z])(\d{3}|\dR\d)([BCDFGJKMW])[A-Z0-9]*", upper)
        if m:
            temp, voltage, code, tol = m.groups()
            return _cap(code, tol, _VOLTAGE.get(voltage), _DIELECTRIC.get(temp))
        # Samsung CL: size, temperature, value, tolerance, voltage, construction.
        m = re.fullmatch(r"CL\d{2}([A-Z])(\d{3}|\dR\d)([BCDFGJKM])([A-Z])[A-Z0-9]{4,5}", upper)
        if m:
            temp, code, tol, voltage = m.groups()
            return _cap(code, tol, {"A": "25V", "B": "50V", "C": "100V", "O": "16V",
                                   "P": "10V", "Q": "6.3V", "M": "63V"}.get(voltage),
                        {"A": "X5R", "B": "X7R", "C": "C0G", "F": "Y5V"}.get(temp))
        # Yageo CC/CX/AC: size, tolerance, termination, dielectric, voltage, BB/BN, value.
        m = re.fullmatch(r"(?:CC|CX|AC)\d{4}([BCDFGJKM])R(X[578][RST]|NPO)([5-9])B[BN]"
                         r"(\d{3}|\dR\d|R\d{2})(?:\d)?", upper)
        if m:
            tol, temp, voltage, code = m.groups()
            return _cap(code, tol, {"5": "6.3V", "6": "10V", "7": "16V", "8": "25V", "9": "50V"}[voltage],
                        "C0G" if temp == "NPO" else temp)
        # TDK C/CGA: dielectric and voltage fields precede the capacitance.
        m = re.fullmatch(r"(?:C\d{4}|CGA[A-Z0-9]{3})(X[578][RST]|C0G|CH|NP0)"
                         r"([0-3][A-Z])(\d{3}|\dR\d)([BCDFGJKM])[A-Z0-9]*", upper)
        if m:
            temp, voltage, code, tol = m.groups()
            return _cap(code, tol, _VOLTAGE.get(voltage), "C0G" if temp == "NP0" else temp)
        # KEMET C: imperial size, style, capacitance, tolerance, voltage, dielectric.
        m = re.fullmatch(r"C\d{4}[CX](\d{3}|\dR\d)([BCDFGJKM])([1-9])([GRX])[A-Z0-9]*", upper)
        if m:
            code, tol, voltage, temp = m.groups()
            return _cap(code, tol, {"1": "100V", "2": "200V", "3": "25V", "4": "16V",
                                   "5": "50V", "8": "10V", "9": "6.3V"}.get(voltage),
                        {"G": "C0G", "R": "X7R", "X": "X5R"}[temp])
        # Panasonic ECJ: size + thickness + dielectric + voltage + value + tolerance.
        m = re.fullmatch(r"ECJ-[A-Z0-9]([A-Z0-9]{2})([0-3][A-Z])(\d{3})([JKM])", upper)
        if m:
            temp, voltage, code, tol = m.groups()
            return _cap(code, tol, _VOLTAGE.get(voltage), {"VB": "X7R", "VF": "Y5V"}.get(temp))
        # Taiyo Yuden: voltage series + size + temperature + capacitance/tolerance.
        m = re.fullmatch(r"([A-Z]MK)\d{3}(?:[AB]?B[7J]|CG)(\d{3}|\dR\d)([BCDFGJKM])[A-Z0-9-]+", upper)
        if m:
            series, code, tol = m.groups()
            return _cap(code, tol, {"JMK": "6.3V", "LMK": "10V", "EMK": "16V", "TMK": "25V",
                                   "GMK": "35V", "UMK": "50V", "HMK": "100V"}.get(series))
        # Nichicon radial aluminum series: voltage and capacitance in uF.
        m = re.fullmatch(r"U(?:RZ|WT|HW|UR)([0-3][A-Z])(\d{3})M[A-Z0-9]+", upper)
        if m:
            voltage, code = m.groups()
            return {"value": _format_value(int(code[:2]) * 10 ** int(code[2]) * 1e-6, "F"),
                    "tolerance": "20%", **({"voltage": _VOLTAGE[voltage]} if voltage in _VOLTAGE else {})}
    if prefix == "R":
        code = tol = None
        # Yageo RC/AC thick film and RT thin film; packaging precedes resistance.
        m = re.fullmatch(r"(?:RC|AC|RL)\d{4}([FGJK])R-\d{2}(\d+[RKM]\d*)L", upper)
        if m:
            tol, code = m.groups()
        m = re.fullmatch(r"RT\d{4}([BDF])R[A-Z]\d{2}(\d+[RKM]\d*)L", upper)
        if m:
            tol, code = m.groups()
        # Panasonic ERJ/ERA: tolerance immediately before 3/4-digit resistance.
        m = re.fullmatch(r"(?:ERJ|ERA)-?[A-Z0-9]+?([BDFJ])(\d{3,4}|\d+[R]\d*)[A-Z]", upper)
        if m:
            tol, code = m.groups()
        # Vishay CRCW: imperial size + explicit engineering resistance + tolerance.
        m = re.fullmatch(r"CRCW\d{4}(\d+[RKM]\d*)([FJK])[A-Z0-9]+", upper)
        if m:
            code, tol = m.groups()
        # Bourns CR and Stackpole RMCF use distinct, bounded resistance fields.
        m = re.fullmatch(r"CR\d{4}-([FJ])X-(\d{3,4})[A-Z]+", upper)
        if m:
            tol, code = m.groups()
        m = re.fullmatch(r"RMCF\d{4}([FJZ])T(\d+[RKM]\d*)", upper)
        if m:
            tol, code = m.groups()
        # ROHM MCR/ESR; KOA RK73; Multicomp MCMR; Walsin WR.
        m = re.fullmatch(r"(?:MCR|ESR)\d{2}[A-Z0-9]*?([FJ])X?(\d{3,4})", upper)
        if m:
            tol, code = m.groups()
        m = re.fullmatch(r"RK73[HB][A-Z0-9]+T(?:TP|TD)(\d{3,4})([FJ])", upper)
        if m:
            code, tol = m.groups()
        m = re.fullmatch(r"(?:MCMR|MR)\d{2}X(\d{4})([FJ])TL", upper)
        if m:
            code, tol = m.groups()
        m = re.fullmatch(r"WR\d{2}X(\d{3,4})([FJ])TL", upper)
        if m:
            code, tol = m.groups()
        # UniRoyal numeric resistance variants only (not EIA-96 letter codes).
        m = re.fullmatch(r"\d{4}W[A-Z0-9]{0,2}([FJ])(\d{4})T[0-9A-Z]+", upper)
        if m:
            tol, code = m.groups()
        if code and (value := _resistance(code)) is not None:
            return {"value": value, **({"tolerance": {"B": "0.1%", "D": "0.5%", **_TOLERANCE}[tol]}
                                      if tol in {"B", "D", *_TOLERANCE} else {})}
    if prefix == "L":
        m = re.fullmatch(r"HPC\s*3012BMV-(\d{3})M", upper)
        if m:
            code = m.group(1)
            return {"value": _format_value(int(code[:2]) * 10 ** int(code[2]) * 1e-6, "H"), "tolerance": "20%"}
        # Reuse the existing decoder only for its bounded, known series. Do not
        # invoke its generic inductor digit search on arbitrary ordering codes.
        if re.fullmatch(r"(?:LQ[WP][A-Z0-9]{2}[A-Z]{2}(?:\dN\d|\d{2}N)[A-Z][A-Z0-9]{2}[A-Z]?|"
                        r"MAKK2520H\d{3}M|(?:XFL|XEL|MSS)\d+-\d{3}[MKJG][A-Z0-9]*|"
                        r"DR\d+-\d{3}-R|MLZ\d{4}[A-Z]\d{3}[A-Z0-9]*)", upper):
            if value := _decode_mpn_value(upper, "L"):
                return {"value": value}
        # TDK SPM/Bourns SRN/SRR: explicit EIA code in uH after the separator.
        m = re.fullmatch(r"(?:SPM\d+[A-Z]*|SRN\d+|SRR\d+)-(\d{3})[MK][A-Z0-9-]*", upper)
        if m:
            code = m[1]
            return {"value": _format_value(int(code[:2]) * 10 ** int(code[2]) * 1e-6, "H")}
    return {}


def _number(value: str) -> float | None:
    m = re.fullmatch(r"([\d.]+)\s*([pnuµmkMG]?)(?:F|H|ohm|V|%)", value)
    if not m:
        return None
    return float(m[1]) * {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3,
                         "": 1, "k": 1e3, "M": 1e6, "G": 1e9}[m[2]]


def _equal(a: str, b: str) -> bool:
    a, b = a.replace("NP0", "C0G").replace("NPO", "C0G"), b.replace("NP0", "C0G").replace("NPO", "C0G")
    if a == b:
        return True
    x, y = _number(a), _number(b)
    return x is not None and y is not None and math.isclose(x, y, rel_tol=1e-6, abs_tol=1e-18)


def _placed(value: str, prefix: str) -> str:
    # Uberamp's "t" labels precision resistors; preserve it in the board data.
    if prefix == "R" and re.fullmatch(r"t\d+(?:\.\d+)?[kM]?", value):
        return value[1:] + "ohm"
    return value


def component_conflicts(component: dict) -> tuple[list[dict], bool]:
    """Return candidate conflicts and whether an MPN comparison was possible."""
    prefix = re.sub(r"[\d_].*", "", component["ref"])
    value, mpn = str(component.get("value", "")), str(component.get("mpn", ""))
    specs = decode_passive_mpn(mpn, prefix)
    hits = []
    checked = False
    for field, decoded in specs.items():
        placed = _placed(str(component.get(field, "")), prefix)
        if field == "value":
            placed = placed.split(" ")[0]
        if not placed or (field in ("value", "voltage", "tolerance") and _number(placed) is None):
            continue
        checked = True
        if not _equal(placed, decoded):
            hits.append({"field": field, "placed": component[field], "other": decoded, "evidence": mpn})
    if mpn and prefix in {"U", "IC", "Q", "D"}:
        # These families have functional digits beyond the first digit run.
        family = r"^(STM32[A-Z]\d{3}[A-Z]{2}|W25[QX]\d+[A-Z]{2}|24(?:AA|LC)\d+|ESP32-WROOM-32[DE]|STPS\d+L\d+|1N\d+|(?:SN)?74[A-Z]+\d+(?:G\d+)?|[A-Z]+\d+)"
        a, b = re.match(family, value.upper()), re.match(family, mpn.upper())
        if a and b:
            checked = True
            if a[1].removeprefix("SN") != b[1].removeprefix("SN") and not mpn.upper().startswith(value.upper()):
                hits.append({"field": "mpn", "placed": value, "other": mpn, "evidence": "different base part numbers"})
    # Explicit capacitor/resistor specs in the source description are independently
    # compared, including rows with no MPN (e.g. S3XY C42).
    description = str(component.get("description", ""))
    if prefix in {"C", "R", "L"} and description and specs:
        for field, pattern in (
            ("voltage", r"(?<![\w.])(\d+(?:\.\d+)?)\s*V(?:OLTS)?\b"),
            ("tolerance", r"(?<![\w.])(\d+(?:\.\d+)?)\s*%"),
            ("dielectric", r"\b(X[578][RST]|C0G|NP0|NPO|Y5V)\b"),
        ):
            m = re.search(pattern, description, re.I)
            if m and field in specs:
                described = m[1].upper() + {"voltage": "V", "tolerance": "%", "dielectric": ""}[field]
                if not _equal(described, specs[field]):
                    hits.append({"field": "description", "spec": field, "placed": described,
                                 "other": specs[field], "evidence": mpn + ": " + description})
    if prefix in {"C", "R", "L"} and description:
        unit = {"C": "F", "R": "ohm", "L": "H"}[prefix]
        m = re.search(r"(?<![\w.])(\d+(?:\.\d+)?)\s*([PNUµMK]?)(" + unit + r")(?![A-Za-z])", description, re.I)
        if m and not re.search(r"(?:±|\+/-)\s*$", description[:m.start()]):
            scale = m[2].lower() if unit != "ohm" else m[2]
            described = m[1] + scale + unit
            placed = _placed(value, prefix).split(" ")[0]
            if _number(placed) is not None and not _equal(placed, described):
                hits.append({"field": "description", "placed": value, "other": described, "evidence": description})
    return hits, checked


def audit(boards: list[dict]) -> dict:
    report = {"boards": len(boards), "rows": 0, "rows_with_mpn": 0, "mpn_rows_checked": 0,
              "mpn_rows_consistent": 0, "hits": [], "unchecked_mpn_rows": []}
    for board in boards:
        for comp in board.get("components", []):
            report["rows"] += 1
            report["rows_with_mpn"] += bool(comp.get("mpn"))
            hits, checked = component_conflicts(comp)
            report["mpn_rows_checked"] += checked
            report["mpn_rows_consistent"] += checked and not hits
            if hits:
                report["hits"].append({"board": board["slug"], "ref": comp["ref"], "conflicts": hits})
            if comp.get("mpn") and not checked:
                report["unchecked_mpn_rows"].append({"board": board["slug"], "ref": comp["ref"], "mpn": comp["mpn"]})
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boards-dir", type=Path, default=Path("data/boards"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit([yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(args.boards_dir.glob("*.yaml"))])
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: len(v) if isinstance(v, list) else v for k, v in report.items()}))


if __name__ == "__main__":
    main()
