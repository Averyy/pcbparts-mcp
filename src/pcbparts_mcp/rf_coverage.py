"""Frequency coverage for RF similar parts in jlc_find_alternatives.

RF subcategories have no compatibility rules, so their similar parts were ranked by stock, maker and
price alone: for BP2G1+ (a 1.2-2 GHz splitter) 5 MHz-1 GHz CATV splitters came back next to parts
that cover its band. Here each candidate's listed band is compared with the original's.
"""

from typing import Any

from .parsers import parse_freq_bands

# Subcategories without compatibility rules whose parts list an operating band
RF_BAND_SUBCATEGORIES = frozenset({
    "RF Power Splitters / Combiners",
    "Balun",
    "RF Directional Coupler",
    "Low Noise Amplifiers (LNA) - RF",
    "RF Amplifiers",
    "RF Power Amplifiers",
    "RF Attenuators",
    "RF Detectors",
    "RF Front End Circuits",
    "RF Modulators and Demodulators",
    "RF Misc ICs and Modules",
    "RF Transceiver ICs",
    "RF Filters",
    "Ceramic Filters",
    "Tunable Filters",
})

# Where a part states its band, in order. "Bandwidth" is a width ("7.5kHz") unless it's a range.
BAND_ATTRIBUTES = (("Frequency Range", True), ("Absolute Bandwidth", False), ("Bandwidth", False))

# Share of the original's band a part must cover to count as full (float rounding only)
FULL_SHARE = 0.999

COVERAGE_ORDER = {"full": 3, "partial": 2, "unknown": 1, "none": 0}


def part_band(part: dict[str, Any]) -> tuple[str, list[tuple[float, float]]] | None:
    """The part's listed band as (value as listed, bands in Hz), or None if it lists none."""
    specs = part.get("specs") or {}
    for name, points in BAND_ATTRIBUTES:
        value = specs.get(name)
        bands = parse_freq_bands(value, points=points) if value else None
        if bands:
            return value, bands
    return None


def _merged(bands: list[tuple[float, float]]) -> list[tuple[float, float]]:
    merged: list[list[float]] = []
    for low, high in sorted(b for b in bands if b[1] > b[0]):
        if merged and low <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], high)
        else:
            merged.append([low, high])
    return [(low, high) for low, high in merged]


def _contains(bands: list[tuple[float, float]], frequency: float) -> bool:
    slack = frequency * 1e-6
    return any(low - slack <= frequency <= high + slack for low, high in bands)


def band_coverage(
    required: list[tuple[float, float]], offered: list[tuple[float, float]] | None
) -> tuple[str, float | None]:
    """How much of the required bands the offered ones cover: (status, share of the required).

    full: all of it; partial: some; none: no overlap; unknown: the part lists no band, or only a
    single frequency inside a required band (one frequency doesn't say how wide the part's band is).
    Each required band counts equally; a band of zero width is covered if an offered band holds it.
    """
    if not offered:
        return "unknown", None
    spans = _merged(offered)
    shares: list[float] = []
    for low, high in required:
        if high == low:
            shares.append(1.0 if _contains(offered, low) else 0.0)
            continue
        overlap = sum(max(0.0, min(high, b_high) - max(low, b_low)) for b_low, b_high in spans)
        if overlap == 0 and any(low < b_low == b_high < high for b_low, b_high in offered):
            return "unknown", None
        shares.append(min(1.0, overlap / (high - low)))
    share = sum(shares) / len(shares)
    if share >= FULL_SHARE:
        return "full", 1.0
    if share == 0:
        return "none", 0.0
    return "partial", round(share, 2)


def check_candidates(original: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Mark each candidate's frequency_coverage against the original's band, drop the ones that
    don't overlap it, and order the rest full, partial (most covered first), unknown, keeping the
    given order within a tier. Returns the summary for the reply; candidates is changed in place.

    None when the original's subcategory isn't an RF one. When the original lists no band, the
    candidates are left as they are and the summary says so.
    """
    if original.get("subcategory") not in RF_BAND_SUBCATEGORIES:
        return None
    band = part_band(original)
    if band is None:
        return {
            "required": None,
            "note": "The original lists no frequency range, so parts weren't checked against one.",
        }
    listed, required = band
    counts = {"full": 0, "partial": 0, "unknown": 0, "none": 0}
    kept = []
    for position, part in enumerate(candidates):
        status, share = band_coverage(required, (part_band(part) or (None, None))[1])
        counts[status] += 1
        if status == "none":
            continue
        part["frequency_coverage"] = {"status": status, **({"share": share} if share is not None else {})}
        kept.append((COVERAGE_ORDER[status], share or 0.0, -position, part))
    kept.sort(key=lambda item: item[:3], reverse=True)
    candidates[:] = [item[3] for item in kept]
    return {
        "required": listed,
        "full": counts["full"],
        "partial": counts["partial"],
        "unknown": counts["unknown"],
        "left_out_no_overlap": counts["none"],
        "note": (
            f"Similar parts are ordered by how much of the original's {listed} they cover (full, then "
            "partial by share, then unknown: no band listed), and parts that don't overlap it are left "
            "out. frequency_coverage on each part gives its status. Covering the band doesn't make a part "
            "a replacement: compare gain, loss, isolation, power and package in the datasheets."
        ),
    }
