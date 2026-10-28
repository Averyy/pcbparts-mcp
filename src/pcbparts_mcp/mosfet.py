"""Catalog RDS(on) test conditions shared by builds and gate-drive searches."""

import json
import re


_RDS_CONDITION = re.compile(
    r'\s*\d+(?:\.\d+)?\s*(?:[munpkM]?Ω|[munpkM]?(?:Ohm|ohm)s?)\s*'
    r'@\s*(?:VGS\s*=\s*)?([+-]?\d+(?:\.\d*)?)\s*(m?)V\s*', re.IGNORECASE,
)


def rds_on_conditions(value: str) -> list[tuple[float, str]]:
    """Return (gate-voltage magnitude, verbatim entry) for stated resistance tests."""
    conditions = []
    for entry in re.split(r'[、,;]', value):
        match = _RDS_CONDITION.fullmatch(entry)
        if match:
            voltage = abs(float(match[1])) / (1000 if match[2] else 1)
            conditions.append((voltage, entry.strip()))
    return conditions


def rds_gate_min(attributes: list[list[str]]) -> float | None:
    """Lowest listed RDS(on) gate voltage; absent/unspecified conditions are unknown."""
    # Match result transformation's last-value semantics if an attribute is repeated.
    conditions = rds_on_conditions(dict(attributes).get("RDS(on)", ""))
    return min((voltage for voltage, _ in conditions), default=None)


def rds_gate_min_json(attributes: str | None) -> float | None:
    """Older-database SQL fallback, evaluated only for gate-drive searches."""
    return rds_gate_min(json.loads(attributes or "[]"))


def rds_on_at_drive(value: str, drive: float) -> str | None:
    """Listed resistance at the highest test voltage no greater than the drive."""
    applicable = [(voltage, entry) for voltage, entry in rds_on_conditions(value) if voltage <= drive]
    return max(applicable, key=lambda condition: condition[0])[1] if applicable else None
