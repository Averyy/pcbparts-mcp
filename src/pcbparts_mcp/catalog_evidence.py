"""Catalog limitations and reviewed manufacturer evidence, independent of catalog rebuilds.

Evidence is attached only to an exact LCSC/model/manufacturer identity. Catalog values are never
rewritten: cited values describe a particular document, not an inferred catalog correction.
"""

from copy import deepcopy
import re
from typing import Any

from .parsers import parse_resistance

def multi_diode(specs: dict[str, str]) -> bool:
    configuration = specs.get("Diode Configuration") or ""
    return bool(re.search(r"\b(?:pair|dual|double|array|bridge)\b|\b[2-9]\s*(?:diodes?|independent)\b",
                          configuration, re.IGNORECASE))


_CLASS_II_DIELECTRIC = re.compile(r"\b(?:X[5-8][RSTPUV]|Y5[PUV]|Z5U)\b", re.IGNORECASE)
_ISAT_NOTE = ("Isat is each maker's own figure: the inductance drop it's measured at (commonly 10% to 30%) and "
              "whether it's typical or minimum differ, so compare Isat on the datasheets before treating two "
              "parts as equal.")
# Bourns SRP4020TA-1R0M (C913245): LCSC lists DCR 27 mOhm (its max; 22 typical) and Current Rating 5 A
# (its Irms at a 40 C rise; Isat is 8.5 A at a 20% drop), neither labelled
_INDUCTOR_DCR_NOTE = ("DCR is the typical figure on some listings and the maximum on others (SRP4020TA-1R0M lists "
                      "27 mOhm, its maximum; 22 typical), and Current Rating is usually the Irms for the maker's "
                      "temperature rise (often 40 C), a heating limit rather than saturation; check the datasheet's "
                      "columns.")
_MLCC_DC_BIAS_NOTE = ("Capacitance is the nominal value at 0 V. Class II dielectrics (X5R, X7R, Y5V) lose "
                      "capacitance under DC bias, more in small cases, often half or more near the rated voltage; "
                      "the maker's DC-bias curve (Murata SimSurfing, Samsung, TDK, KEMET K-SIM) gives the "
                      "effective value at your voltage.")
_MOSFET_NOTE = ("LCSC takes RDS(on) and Vgs(th) from different datasheet columns on different listings: AO3401A "
                "lists 47mOhm@10V (its 4.5 V typical) and its 4.5 V and 2.5 V maxima, HL3415A lists typicals, "
                "LBSS84LT1G's Vgs(th) is the maximum and AO3401A's the typical. Compare the datasheets' max columns "
                "(and Vgs(th) min for a threshold detector). The Vgs rating (the \"Vgs\" spec) is on about a third "
                "of listings, and gate leakage (IGSS) on none.")
_RF_CABLE_NOTE = ("The listing doesn't say each end's style: bulkhead with nut and washer or PCB-mount (straight or "
                  "right angle), jack or plug, SMA or RP-SMA. Check the maker's drawing.")


def catalog_gap_note(subcategory: str | None, specs: dict[str, str]) -> str | None:
    """What a part type's listing leaves out that its users need (jlc_get_part's specs_note).

    From design-session reports: an Isat filter treated a 30%-drop figure like a 10%-drop one; a
    100 uF 6.3 V X5R bank was sized at its nominal value; an IPEX-to-SMA pigtail listed only as
    "IPEX to SMA" went into a design as a bulkhead when its SMA end is PCB-mount; a P-FET ranked 2.1x better
    than AO3401A at 2.5 V compared its typical against AO3401A's maximum (1.5x max against max).
    """
    sub = (subcategory or "").lower()
    listed = {name for name, value in specs.items() if value not in ("", "-")}
    dcr = "DC Resistance(DCR)" in listed and "inductor" in sub
    if any(name.startswith("Current - Saturation") for name in listed):
        return f"{_ISAT_NOTE} {_INDUCTOR_DCR_NOTE}" if dcr else _ISAT_NOTE
    if dcr:
        return _INDUCTOR_DCR_NOTE
    if sub.startswith("multilayer ceramic capacitors") and _CLASS_II_DIELECTRIC.search(
            specs.get("Temperature Coefficient") or ""):
        return _MLCC_DC_BIAS_NOTE
    if sub == "rf cables":
        return _RF_CABLE_NOTE
    if sub == "mosfets" and (specs.get("RDS(on)") or specs.get("Gate Threshold Voltage (Vgs(th))")):
        return _MOSFET_NOTE
    if multi_diode(specs) and "Current - Rectified" in listed:
        return ("Multi-diode current ratings can depend on how many diodes are loaded. "
                "This listing does not state the loading condition; check the datasheet's "
                "per-diode limits and thermal conditions.")
    return None


_SOREDE = {
    "source_url": "https://atta.szlcsc.com/upload/public/pdf/source/20260105/328ADD47764ED393E25740070F708D1C.pdf",
    "document": "SRD-WI-22770 Rev A, 2024-06-14", "printed_page": "2/8",
    "reviewed_on": "2026-11-08",
}
_BOURNS = {
    "source_url": "https://www.bourns.com/docs/product-datasheets/srp4020ta.pdf",
    "document": "SRP4020TA Series", "printed_page": "1",
    "reviewed_on": "2026-11-08",
}
_NEXPERIA = {
    "source_url": "https://assets.nexperia.com/documents/data-sheet/BAV99.pdf",
    "document": "BAV99 v.9, 2022-07-01, Table 5", "printed_page": "3/10",
    "reviewed_on": "2026-11-08",
}

# A missing basis is deliberately not filled from convention. Bourns states its Isat
# drop criterion, but does not label that column typical or minimum.
_REVIEWED = {
    ("C53308978", "SRYC.0420.YF1R0MT00", "sorede"): {
        "DC Resistance(DCR)": {**_SOREDE, "value": "27mΩ", "basis": "maximum"},
        "Current - Saturation(Isat)": {**_SOREDE, "value": "8.5A", "basis": "typical",
                                        "inductance_drop_pct": 30},
        "Current Rating": {**_SOREDE, "value": "5A", "basis": "typical",
                           "temperature_rise_c": 40, "ambient_c": 25},
    },
    ("C913245", "SRP4020TA-1R0M", "bourns"): {
        "DC Resistance(DCR)": {**_BOURNS, "value": "27mΩ", "basis": "maximum"},
        "Current - Saturation(Isat)": {**_BOURNS, "value": "8.5A", "inductance_drop_pct": 20},
        "Current Rating": {**_BOURNS, "value": "5A", "temperature_rise_c": 40},
    },
    ("C2500", "BAV99,215", "nexperia"): {
        "Current - Rectified": {**_NEXPERIA, "basis": "absolute maximum",
                                "single_loaded": "215mA", "both_loaded_per_diode": "125mA",
                                "note": "Limiting values; observe the document's thermal and mounting conditions."},
    },
}


def reviewed_specs(part: dict[str, Any]) -> dict[str, Any]:
    key = (part.get("lcsc"), part.get("model"), (part.get("manufacturer") or "").casefold())
    return deepcopy(_REVIEWED.get(key, {}))


def annotate_catalog(part: dict[str, Any]) -> None:
    """Add source-scoped warnings/evidence to both live and snapshot part results."""
    specs = part.get("specs") or {}
    if note := catalog_gap_note(part.get("subcategory"), specs):
        previous = part.get("specs_note") or ""
        if note not in previous:
            part["specs_note"] = f"{previous} {note}".strip()
    if evidence := reviewed_specs(part):
        part["spec_evidence"] = evidence
        # Keep the reported catalog claim visible, including after a daily rebuild.
        dcr = evidence.get("DC Resistance(DCR)")
        if (dcr and specs.get("DC Resistance(DCR)")
                and parse_resistance(specs["DC Resistance(DCR)"]) != parse_resistance(dcr["value"])):
            part["spec_discrepancies"] = [{
                "spec": "DC Resistance(DCR)", "catalog_value": specs["DC Resistance(DCR)"],
                "datasheet_value": dcr["value"], "datasheet_basis": dcr["basis"],
                "source_url": dcr["source_url"], "document": dcr["document"],
                "printed_page": dcr["printed_page"],
            }]
    if part.get("no_datasheet"):
        part["no_datasheet_note"] = (
            "JLCPCB lists no datasheet; this flag does not describe availability from LCSC or the manufacturer. "
            "jlc_get_part checks LCSC when JLCPCB has none."
        )
