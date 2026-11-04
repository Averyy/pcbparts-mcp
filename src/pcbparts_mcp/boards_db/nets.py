"""Board netlist helpers shared by the boards.db build (scripts/build_boards_db.py) and board_get's
focus view, so both read rails and roles the same way."""

# Power rail net names (they connect most of a board)
POWER_NET_NAMES = frozenset({
    "GND", "AGND", "DGND", "PGND", "SGND", "EGND",
    "VCC", "VDD", "3V3", "3.3V", "5V", "5V0", "12V", "24V",
    "VBAT", "VIN", "VMAIN", "VBUS", "V+", "V-",
    "+5V", "+3V3", "+3.3V", "+12V", "+24V", "+48V",
    "VSS", "AVCC", "AVDD", "DVCC", "DVDD",
    "VDDIO", "VDDA", "VDDCORE", "VCC_IO",
})


def is_power_net(name: str | None) -> bool:
    """A power rail, or an unnamed net (not useful in a neighborhood)."""
    if not name:
        return True
    upper = name.upper().strip()
    if upper in POWER_NET_NAMES:
        return True
    # Match patterns like N$123, GND1, VCC_3V3, +BATT, etc.
    if upper.startswith("GND") or upper.startswith("N$"):
        return True
    return False


def classify_role(ref: str, comp: dict, ic_ref: str) -> str:
    """A component's role relative to the part in focus."""
    if comp.get("decouples") == ic_ref:
        return "decoupling"
    if comp.get("pullup"):
        return "pullup"
    if comp.get("pulldown"):
        return "pulldown"
    # By ref prefix
    prefix = ref.rstrip("0123456789")
    role_map = {
        "R": "resistor", "RN": "resistor_network", "C": "capacitor", "L": "inductor",
        "D": "diode", "Q": "transistor", "SW": "switch",
        "LED": "led", "FB": "ferrite_bead", "F": "fuse",
    }
    if prefix in role_map:
        return role_map[prefix]
    if ref.upper().startswith("U") or ref.upper().startswith("IC"):
        return "ic"
    if ref.startswith("J") or ref.startswith("X") or ref.startswith("CONN") or prefix == "P":
        return "connector"
    return "other"
