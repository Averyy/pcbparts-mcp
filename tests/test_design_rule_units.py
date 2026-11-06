"""Unit conversions written side by side in the design rules agree.

A rule that gives a value in two units, "0.25mm (10mil)" or "136 ps/in (5.4 ps/mm)", states the
same quantity twice. pcb-layout.md gave microstrip delay as "136 ps/in (5.4 ns/100mm)", off by 10x
(the report in todo-bug-design-rule-accuracy-and-applicability.md, 2026-11-06).
"""

import re
from pathlib import Path

import pytest

RULES = Path(__file__).resolve().parent.parent / "data" / "design-rules" / "rules"
NUM = r"(\d+(?:\.\d+)?)"
INCH = r"(?:in|inch|inches|\")"

# name: (pattern for "<a> unit_a (<b> unit_b)", b expected from a, relative tolerance, absolute tolerance)
PAIRS = {
    "mm (mil)": (NUM + r"\s*mm\s*\(\s*" + NUM + r"\s*mils?\s*\)", lambda a: a / 0.0254, 0.12, 0.6),
    "mil (mm)": (NUM + r"\s*mils?\s*\(\s*" + NUM + r"\s*mm\s*\)", lambda a: a * 0.0254, 0.12, 0.051),
    "in (mm)": (NUM + r"\s*" + INCH + r"\s*\(\s*" + NUM + r"\s*mm\s*\)", lambda a: a * 25.4, 0.05, 0.0),
    "mm (in)": (NUM + r"\s*mm\s*\(\s*" + NUM + r"\s*" + INCH + r"\s*\)", lambda a: a / 25.4, 0.05, 0.0),
    "oz (um)": (NUM + r"\s*oz\s*\(\s*" + NUM + r"\s*(?:um|µm|μm)\s*\)", lambda a: a * 34.8, 0.05, 0.0),
    "ps/in (ps/mm)": (NUM + r"\s*ps/in\s*\(\s*" + NUM + r"\s*ps/mm\s*\)", lambda a: a / 25.4, 0.05, 0.0),
    "ps/in (ns/100mm)": (NUM + r"\s*ps/in\s*\(\s*" + NUM + r"\s*ns/100\s*mm\s*\)", lambda a: a / 254, 0.05, 0.0),
}


def _pairs():
    for path in sorted(RULES.rglob("*.md")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for name, (pattern, convert, rel, abs_tol) in PAIRS.items():
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    a, b = float(match.group(1)), float(match.group(2))
                    yield path.relative_to(RULES).as_posix(), number, name, match.group(0), b, convert(a), rel, abs_tol


def test_rule_files_have_paired_units():
    # 91 pairs on 2026-11-06; guards against the scan silently matching nothing
    assert sum(1 for _ in _pairs()) >= 80


def test_paired_units_agree():
    wrong = [f"{file}:{line} {name}: {text!r}, expected about {expected:.3g}"
             for file, line, name, text, stated, expected, rel, abs_tol in _pairs()
             if abs(stated - expected) > max(rel * expected, abs_tol)]
    assert not wrong, "\n".join(wrong)


VALUE = NUM + r"\s*(kohm|K|ohm)"
# "300e-9 / (0.8473 * 200e-12) = 1.77 kohm -> use 1.6 kohm": the chosen value must not exceed the maximum
RP_MAX = re.compile(NUM + r"\s*(?:e-9|ns)\s*/\s*\(\s*0\.8473\s*\*\s*" + NUM + r"\s*(?:e-12|pF)\s*\)\s*=\s*"
                    + VALUE + r"(?:\s*max)?\s*->\s*use\s*" + VALUE)
# "(3.3 - 0.4) / 0.003 = 967 ohm -> use 1 kohm": the chosen value must not be below the minimum
RP_MIN = re.compile(r"\(\s*" + NUM + r"\s*-\s*" + NUM + r"\s*\)\s*/\s*" + NUM + r"\s*=\s*"
                    + VALUE + r"\s*->\s*use\s*" + VALUE)


def _ohms(value, unit):
    return float(value) * (1 if unit == "ohm" else 1000)


def _pullup_errors(text):
    errors = []
    for m in RP_MAX.finditer(text):
        t_ns, c_pf = float(m.group(1)), float(m.group(2))
        limit, stated, chosen = t_ns * 1e-9 / (0.8473 * c_pf * 1e-12), _ohms(*m.group(3, 4)), _ohms(*m.group(5, 6))
        if abs(stated - limit) > 0.01 * limit or chosen > limit:
            errors.append(f"{m.group(0)!r}: max is {limit:.0f} ohm")
    for m in RP_MIN.finditer(text):
        vcc, vol, iol = (float(g) for g in m.group(1, 2, 3))
        limit, stated, chosen = (vcc - vol) / iol, _ohms(*m.group(4, 5)), _ohms(*m.group(6, 7))
        if abs(stated - limit) > 0.01 * limit or chosen < limit:
            errors.append(f"{m.group(0)!r}: min is {limit:.0f} ohm")
    return errors


def test_pullup_worked_examples_hold():
    # The I2C example said "= 1.77 kohm -> use 1.8 kohm", over its own maximum (todo-bug-design-rule-audit-followup.md)
    found = 0
    for path in sorted(RULES.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        found += len(RP_MAX.findall(text)) + len(RP_MIN.findall(text))
        errors = _pullup_errors(text)
        assert not errors, f"{path.relative_to(RULES).as_posix()}: " + "; ".join(errors)
    assert found >= 4  # 4 on 2026-11-06: i2c.md (2), level-shifting.md, DESIGN-STYLE-GUIDE.md


@pytest.mark.parametrize("text, ok", [
    ("300e-9 / (0.8473 * 200e-12) = 1.77 kohm -> use 1.6 kohm", True),
    ("300e-9 / (0.8473 * 200e-12) = 1.77 kohm -> use 1.8 kohm", False),
    ("300ns / (0.8473 * 200pF) = 1.77K max -> use 1.6K", True),
    ("(3.3 - 0.4) / 0.003 = 967 ohm -> use 1 kohm", True),
    ("(5 - 0.4) / 0.003 = 1533 ohm -> use 1.5 kohm", False),
])
def test_pullup_checker(text, ok):
    assert (RP_MAX.search(text) or RP_MIN.search(text)) and (not _pullup_errors(text)) == ok


@pytest.mark.parametrize("text, ok", [
    ("0.25mm (10mil)", True), ("0.1mm (4mil)", True), ("0.25mm (100mil)", False),
    ("136 ps/in (5.4 ps/mm)", True), ("136 ps/in (5.4 ns/100mm)", False), ("136 ps/in (0.54 ns/100mm)", True),
    ("1oz (35um)", True), ("2oz (35um)", False),
])
def test_checker_catches_tenfold_errors(text, ok):
    found = []
    for name, (pattern, convert, rel, abs_tol) in PAIRS.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            stated, expected = float(match.group(2)), convert(float(match.group(1)))
            found.append(abs(stated - expected) <= max(rel * expected, abs_tol))
    assert found == [ok]
