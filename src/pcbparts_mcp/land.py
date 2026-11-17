"""Does a candidate's EasyEDA footprint land on the original's copper?

jlc_find_alternatives(land_compatible=true) compares footprints pad by pad, for a part on a board
whose copper is already made. From a design-session report (C295747, JST S2B-PH-SM4-TB, out of
stock on a released board): of 34 verified PH 2-pin alternatives, 16 matched the original's pads,
6 only when turned 180 degrees (the pick-and-place rotation would be off), 4 put pad 1 where the
original has pad 2, and 8 didn't fit (mounting tabs 0.24-0.83 mm away). The top-ranked one
(C23397052) swapped pads 1 and 2, which nobody had checked.

Pads come from pinout.parse_easyeda_footprint(): positions in mm, y down. The candidate is turned
0/90/180/270 degrees, its pad centres moved onto the original's, and every original pad matched to
the nearest candidate pad. Pad numbers are each footprint author's, so a renumbered pad says the
two footprints disagree, not which one matches the physical part.
"""

import math
import re
from typing import Any

LAND_TOLERANCE_MM = 0.15  # largest pad-centre distance that still counts as the same land
MAX_LAND_PADS = 300  # bigger footprints aren't compared (cost grows with pads squared)
_TURNS = (0, 90, 180, 270)


def _turned(x: float, y: float, turn: int) -> tuple[float, float]:
    # Turning the footprint counter-clockwise as drawn (y down), like EasyEDA's rotation
    return {0: (x, y), 90: (y, -x), 180: (-x, -y), 270: (-y, x)}[turn]


def _match(orig: list[tuple[str, float, float, bool]], cand: list[tuple[str, float, float, bool]]
           ) -> tuple[float, dict[str, str], int, bool]:
    """Worst pad-centre distance, renumbered pads, how many pairs have different numbers, and
    whether every pair has the same kind (surface or through-hole), after moving the candidate's pad
    centres onto the original's. Nearest free pad first, ties (stacked pads) going to the same kind
    and number; one refinement pass re-centres on the matched pairs, so one moved pad doesn't pull
    the others off."""
    def centre(points):
        return sum(p[1] for p in points) / len(points), sum(p[2] for p in points) / len(points)

    (ox, oy), (cx, cy) = centre(orig), centre(cand)
    dx, dy = ox - cx, oy - cy
    pairs: list[tuple[int, int]] = []
    for _ in range(2):
        moved = [(n, x + dx, y + dy, tht) for n, x, y, tht in cand]
        free = set(range(len(moved)))
        pairs = []
        for i, (number, x, y, tht) in enumerate(orig):
            j = min(free, key=lambda k: (round((moved[k][1] - x) ** 2 + (moved[k][2] - y) ** 2, 6),
                                         moved[k][3] != tht, moved[k][0] != number))
            free.discard(j)
            pairs.append((i, j))
        # Re-centre on the matched pairs: the mean residual is the best translation for them
        dx += sum(orig[i][1] - moved[j][1] for i, j in pairs) / len(pairs)
        dy += sum(orig[i][2] - moved[j][2] for i, j in pairs) / len(pairs)
    moved = [(n, x + dx, y + dy, tht) for n, x, y, tht in cand]
    worst = max(math.hypot(orig[i][1] - moved[j][1], orig[i][2] - moved[j][2]) for i, j in pairs)
    # Unnumbered original pads (mechanical) have no number to compare. Several pads can share a
    # number (mounting tabs, shields): every place a number lands on another counts.
    landed: dict[str, set[str]] = {}
    mismatched = 0
    for i, j in pairs:
        if orig[i][0]:
            landed.setdefault(orig[i][0], set()).add(moved[j][0])
            mismatched += orig[i][0] != moved[j][0]
    renumbered = {number: "/".join(sorted(found, key=_number_key))
                  for number, found in landed.items() if found != {number}}
    same_kind = all(orig[i][3] == moved[j][3] for i, j in pairs)
    return worst, renumbered, mismatched, same_kind


def _points(pads: list[dict[str, Any]]) -> list[tuple[str, float, float, bool]]:
    return [(str(p.get("number") or ""), float(p["x"]), float(p["y"]), "hole" in p) for p in pads]


def compare_land(original: list[dict[str, Any]], candidate: list[dict[str, Any]],
                 tolerance: float = LAND_TOLERANCE_MM) -> dict[str, Any] | None:
    """How a candidate's pads sit on the original's, or None when either has no pads or too many.

    fits: same pad count and kinds, every pad centre within tolerance after turning.
    turn: degrees counter-clockwise (top view) the candidate's footprint is turned to line up
        (0 if it lines up as drawn); a non-zero turn changes the pick-and-place rotation by that much.
    max_offset_mm: largest pad-centre distance at that turn.
    renumbered: original pad number -> the candidate's pad number in the same place, only for pads
        that differ (both footprints' own numbering); "1/2" when pads sharing a number land on both.
    """
    if not original or not candidate or len(original) > MAX_LAND_PADS or len(candidate) > MAX_LAND_PADS:
        return None
    orig = _points(original)
    if len(original) != len(candidate):
        return {"fits": False, "pads": f"{len(candidate)} pads, original has {len(original)}"}
    best: tuple | None = None
    for turn in _TURNS:
        cand = [(n, *_turned(x, y, turn), tht) for n, x, y, tht in _points(candidate)]
        worst, renumbered, mismatched, same_kind = _match(orig, cand)
        fits = same_kind and worst <= tolerance
        # A fitting turn first: the one that keeps the most numbers, then no turn. Else the closest.
        key = (0, mismatched, turn != 0, worst) if fits else (1, worst, 0, 0)
        if best is None or key < best[0]:
            best = (key, turn, worst, renumbered, fits, same_kind)
    _, turn, worst, renumbered, fits, same_kind = best
    result: dict[str, Any] = {"fits": fits, "turn": turn, "max_offset_mm": round(worst, 3)}
    if not same_kind:
        result["pads"] = "surface and through-hole pads don't line up"
    if renumbered:
        result["renumbered"] = dict(sorted(renumbered.items(), key=lambda kv: _number_key(kv[0])))
    return result


def _number_key(number: str) -> tuple:
    return tuple((0, int(part), "") if part.isdigit() else (1, 0, part) for part in re.findall(r"\d+|\D+", number))


def first_pad(pads: list[dict[str, Any]]) -> str | None:
    """Pad "1" if the footprint has one, else its first numbered pad (pin 1's stand-in)."""
    numbers = [str(p.get("number")) for p in pads if p.get("number")]
    if "1" in numbers:
        return "1"
    return min(numbers, key=_number_key) if numbers else None


def land_rank(land: dict[str, Any] | None, pin1: str | None) -> int:
    """Higher is a better drop-in on existing copper: same land and numbers (5), only other pads
    renumbered (4), fits only turned (3), pad 1 elsewhere (2), unknown (1), doesn't fit (0)."""
    if land is None:
        return 1
    if not land.get("fits"):
        return 0
    renumbered = land.get("renumbered") or {}
    if pin1 is not None and pin1 in renumbered:
        return 2
    if land.get("turn"):
        return 3
    return 4 if renumbered else 5


# jlc_find_alternatives summary.land_note: once per reply, not per part
LAND_NOTE = (
    "land compares each part's EasyEDA footprint with the original's: fits (same pad count, every pad "
    f"centre within {LAND_TOLERANCE_MM} mm), turn (degrees counter-clockwise, top view, the part's footprint "
    "is turned to line up; a non-zero turn changes the pick-and-place rotation), max_offset_mm, renumbered "
    "(original pad number -> this part's pad in the same place). Pad numbers are each footprint author's, "
    "so a renumbered pad 1 means the footprints disagree: check both datasheets. land null: not compared "
    "(summary.stages.land says why). Parts that fit as drawn with the same numbers are listed first."
)
CONNECTOR_LAND_HINT = (
    "Makers' footprints for one connector series differ: pads moved, drawn turned 180 degrees, or pads 1 "
    "and 2 numbered the other way round. For a board whose copper is already made, land_compatible=true "
    "compares each candidate's EasyEDA footprint with the original's."
)
# Each connector alternative's unchecked_requirements
CONNECTOR_LAND_UNCHECKED = "land pattern and pin 1 position"
