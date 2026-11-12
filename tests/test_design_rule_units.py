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


# RF trace impedance examples in misc/rf-antenna.md came from a 2-D field solve (0.8.12) that left no
# artifact; design-rules audit B (2026-11-10) could not reproduce them from the cited sources. These
# closed-form models recompute them: conductor-backed CPW by conformal mapping (zero-thickness copper,
# and with the Gupta copper-thickness correction, which brackets the field solve), and Hammerstad microstrip.
def _ellip_k(k):
    from math import pi, sqrt
    a, b = 1.0, sqrt(1 - k * k)
    for _ in range(40):
        a, b = (a + b) / 2, sqrt(a * b)
    return pi / (2 * a)


def _gcpw_ohms(w, s, h, er, t=0.0):
    from math import log, pi, sqrt, tanh

    def ratios(w, s):
        a, b = w / 2, w / 2 + s
        k, k1 = a / b, tanh(pi * a / (2 * h)) / tanh(pi * b / (2 * h))
        return (_ellip_k(k) / _ellip_k(sqrt(1 - k * k)), _ellip_k(k1) / _ellip_k(sqrt(1 - k1 * k1)))

    q0, q1 = ratios(w, s)
    eeff = (1 + er * q1 / q0) / (1 + q1 / q0)
    if not t:
        return 60 * pi / sqrt(eeff) / (q0 + q1)
    d = 1.25 * t / pi * (1 + log(4 * pi * w / t))
    qe, q1e = ratios(w + d, s - d)
    eeff -= (eeff - 1) * 0.7 * t / s / (q0 + 0.7 * t / s)
    return 60 * pi / sqrt(eeff) / (qe + q1e)


def _microstrip_ohms(w, h, er):
    from math import log, pi, sqrt
    u = w / h
    eeff = (er + 1) / 2 + (er - 1) / 2 / sqrt(1 + 12 / u)
    return 120 * pi / (sqrt(eeff) * (u + 1.393 + 0.667 * log(u + 1.444)))


@pytest.mark.parametrize("stated, w, s, h, er, t", [
    ("trace 1.2mm, gap 0.25mm = 50 ohm", 1.2, 0.25, 1.5, 4.4, 0.035),
    ("trace 0.45mm, gap 0.64mm = 51 ohm", 0.45, 0.64, 0.26, 4.4, 0.018),
    ("with coplanar ground 0.2mm away it is 35 ohm", 2.8, 0.2, 1.5, 4.4, 0.035),
])
def test_rf_gcpw_examples_agree_with_closed_form_models(stated, w, s, h, er, t):
    text = (RULES / "misc" / "rf-antenna.md").read_text(encoding="utf-8")
    assert stated in text
    ohms = float(re.search(r"(\d+) ohm$", stated).group(1))
    thick, thin = _gcpw_ohms(w, s, h, er, t), _gcpw_ohms(w, s, h, er)
    # thickness-corrected and zero-thickness models straddle the field solve, within about 4 ohm
    assert thick - 1 <= ohms <= thin + 1
    assert max(abs(ohms - thick), abs(ohms - thin)) <= 4


def test_rf_microstrip_width_example():
    text = (RULES / "misc" / "rf-antenna.md").read_text(encoding="utf-8")
    assert "A 2.8mm trace is approximately the plain-microstrip 50 ohm width on 1.5mm FR4" in text
    assert abs(_microstrip_ohms(2.8, 1.5, 4.4) - 50) <= 2


# pcb-layout.md impedance examples (design-rule review 2026-11-10): the file told readers to narrow a
# 20 mil trace to 18 mil because MT-094's Eq. 3 reads 46 ohm, put 75 ohm at W/H 1:1, and gave the
# stripline B/W rule without its neglect-T condition. These recompute the stated numbers.
def _ipc_microstrip_ohms(w, h, er, t):
    from math import log, sqrt
    return 87 / sqrt(er + 1.41) * log(5.98 * h / (0.8 * w + t))


def _ipc_stripline_ohms(w, b, er, t):
    from math import log, sqrt
    return 60 / sqrt(er) * log(1.9 * b / (0.8 * w + t))


def test_pcb_layout_impedance_examples():
    text = (RULES / "guides" / "pcb-layout.md").read_text(encoding="utf-8")
    assert "decrease W to 18 mil" not in text and "W/H ~ 1:1 gives ~75 ohm" not in text
    assert "W/H ~ 0.83 (W = 8.3 mil at H = 10 mil, 1 oz) gives ~75 ohm" in text
    assert abs(_ipc_microstrip_ohms(8.3, 10, 4.0, 1.4) - 75) <= 1
    assert round(_ipc_microstrip_ohms(20, 10, 4.0, 1.4)) == 46
    # MT-094 calls the 20 mil line ~50 ohm; Hammerstad (zero thickness) agrees within 2 ohm
    assert abs(_microstrip_ohms(20, 10, 4.0) - 50) <= 2
    assert "B/W = 2-2.2 gives ~42-44 ohm and 50 ohm needs B/W ~2.8 (W ~7.2 mil)" in text
    assert [round(_ipc_stripline_ohms(20 / r, 20, 4.0, 1.4)) for r in (2, 2.2)] == [42, 44]
    assert abs(_ipc_stripline_ohms(7.2, 20, 4.0, 1.4) - 50) <= 0.5 and round(20 / 7.2, 1) == 2.8
    # neglecting T, the B/W 2-2.2 rule does land near 50 ohm
    assert 46 <= _ipc_stripline_ohms(10, 20, 4.0, 0) and _ipc_stripline_ohms(20 / 2.2, 20, 4.0, 0) <= 50.5
    assert round(_ipc_stripline_ohms(8, 20, 4.0, 1.4), 1) == 47.5


def test_pcb_layout_delay_figures():
    from math import sqrt
    text = (RULES / "guides" / "pcb-layout.md").read_text(encoding="utf-8")
    assert "Propagation delay depends only on dielectric constant, not trace dimensions" not in text
    assert round(85 * sqrt(0.475 * 4.0 + 0.67)) == 136  # MT-094 Eq. 6
    assert round(85 * sqrt(4.0)) == 170  # MT-094 Eq. 10
    assert "effective dielectric constant at about 3, which is ~147 ps/in" in text
    assert round(85 * sqrt(3)) == 147
