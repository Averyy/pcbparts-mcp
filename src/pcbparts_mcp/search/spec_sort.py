"""jlc_search sorted by a spec (sort_by="spec"): which specs sort, their SQL keys, and the value each
result shows.

Only specs whose column holds one comparable number per part are offered. The rest are refused with
the reason: ranges ("2.7V~5.5V" supplies, adjustable outputs), and figures whose units aren't
converted to one (slew rate in V/µs, V/ms and V/ns). A spec whose catalog figures carry test
conditions (RDS(on) at a gate voltage, dropout at a load, Vf at a current) can be sorted at one
condition, so the order compares like with like; without one, the reply says the order is the
catalog figures' own.
"""

import json
import re
from dataclasses import dataclass, replace
from typing import Any, Callable

from ..mosfet import rds_on_at_drive
from ..parsers import (
    parse_capacitance,
    parse_current,
    parse_decibels,
    parse_frequency,
    parse_inductance,
    parse_integer,
    parse_memory_size,
    parse_power,
    parse_ppm,
    parse_resistance,
    parse_tolerance,
    parse_voltage,
)
from .spec_filter import (
    _AT_LOAD, _DROPOUT_PAIR, dropout_at_load, dropout_at_load_json, dropout_loads, get_attribute_names,
)


@dataclass(frozen=True)
class SortableSpec:
    label: str
    column: str
    # Attributes that hold it: the database build fills the column from these, with the same parser
    names: tuple[str, ...]
    parser: Callable[[str], float | None]
    # Other names sort_spec accepts
    words: tuple[str, ...] = ()
    # Phrases a query names it by after "lowest"/"highest" (bare "power" in "lowest power MCU" means
    # consumption, not a power rating, so it isn't one)
    phrases: tuple[str, ...] = ()
    # Attributes that also fill the column but mean something else ("Voltage - Supply" in voltage_max_v):
    # a part listing one of them is read from its own attribute instead
    other_sources: tuple[str, ...] = ()
    # A listed 0 is a placeholder ("0uA" quiescent current); a 0Ω jumper's resistance isn't
    zero_is_missing: bool = True
    # The test conditions its listings carry, when they differ between parts
    conditions: str | None = None
    # Sortable at one condition: "gate" (V), "load" or "current" (A)
    at: str | None = None
    example_at: str | None = None
    # How its figures differ between listings, said with every sort on it
    caveat: str | None = None


_CURRENT_NAMES = ("Quiescent Current(Iq)", "Quiescent Current", "standby current", "Supply Current (Iq)")

SORTABLE_SPECS: tuple[SortableSpec, ...] = (
    SortableSpec("RDS(on)", "rds_on_ohms", ("RDS(on)",), parse_resistance,
                 words=("on resistance", "on-resistance", "drain-source on resistance"),
                 phrases=("rds(on)", "rdson", "rds on", "rds", "on resistance", "on-resistance"),
                 conditions="gate voltages and drain currents", at="gate", example_at="4.5V",
                 caveat="LCSC lists the typical figure on some parts and the maximum on others (AO3401A's 4.5 V "
                        "and 2.5 V entries are maxima, HL3415A's typicals), so compare the datasheets' max "
                        "columns before choosing."),
    SortableSpec("Gate Charge", "qg_nc", ("Total Gate Charge(Qg)", "Gate Charge(Qg)"), parse_capacitance,
                 words=("Qg", "total gate charge"), phrases=("gate charge", "qg"), conditions="gate voltages"),
    SortableSpec("Quiescent Current", "iq_ua", _CURRENT_NAMES, parse_current,
                 words=("Iq", "quiescent", "standby current", "supply current"),
                 phrases=("iq", "quiescent current", "standby current")),
    SortableSpec("Voltage Dropout", "vdropout_v", ("Voltage Dropout",), parse_voltage,
                 words=("Dropout", "dropout voltage", "Vdo"), phrases=("dropout", "dropout voltage"),
                 conditions="load currents", at="load", example_at="500mA"),
    SortableSpec("Vf", "vf_v", ("Voltage - Forward(Vf@If)",), parse_voltage,
                 words=("forward voltage", "forward drop", "forward voltage drop"),
                 phrases=("vf", "forward voltage", "forward drop", "forward voltage drop"),
                 conditions="forward currents", at="current", example_at="1A"),
    SortableSpec("Isat", "isat_a", ("Current - Saturation(Isat)", "Current - Saturation (Isat)", "Saturation Current"),
                 parse_current, words=("saturation current",), phrases=("isat", "saturation current")),
    SortableSpec("DCR", "dcr_ohms", ("DC Resistance(DCR)",), parse_resistance,
                 words=("dc resistance",), phrases=("dcr", "dc resistance")),
    SortableSpec("ESR", "esr_ohms", ("Equivalent Series Resistance(ESR)",), parse_resistance,
                 words=("equivalent series resistance",), phrases=("esr",), conditions="test frequencies"),
    SortableSpec("Ripple Current", "ripple_current_a", ("Ripple Current",), parse_current,
                 phrases=("ripple current", "ripple current rating"), conditions="frequencies"),
    SortableSpec("Lifetime", "lifetime_hours", ("Lifetime",), parse_integer,
                 words=("life", "endurance"), phrases=("lifetime", "life"), conditions="temperatures"),
    SortableSpec("GBW", "gbw_hz", ("Gain Bandwidth Product",), parse_frequency,
                 words=("gain bandwidth", "gain-bandwidth", "gain bandwidth product", "bandwidth"),
                 phrases=("gbw", "gain bandwidth", "gain-bandwidth", "gain bandwidth product", "bandwidth")),
    SortableSpec("CMRR", "cmrr_db", ("Common Mode Rejection Ratio(CMRR)",), parse_decibels,
                 words=("common mode rejection", "common mode rejection ratio"), phrases=("cmrr",)),
    SortableSpec("Noise Figure", "noise_figure_db", ("Noise Figure",), parse_decibels, phrases=("noise figure",)),
    SortableSpec("Load Capacitance", "load_capacitance_pf", ("Load Capacitance",), parse_capacitance,
                 phrases=("load capacitance",)),
    SortableSpec("Frequency Stability", "freq_tolerance_ppm", ("Frequency Stability",), parse_ppm,
                 words=("ppm", "stability"), phrases=("ppm", "frequency stability", "stability")),
    SortableSpec("Flash", "flash_size_bytes", ("Flash", "Program Memory Size", "Program Storage Size"),
                 parse_memory_size, words=("flash size", "program memory"),
                 phrases=("flash", "flash memory", "program memory")),
    SortableSpec("RAM", "ram_size_bytes", ("SRAM", "RAM Size"), parse_memory_size, phrases=("ram", "sram")),
    SortableSpec("CPU Speed", "clock_speed_hz", ("CPU Maximum Speed",), parse_frequency,
                 words=("clock", "clock speed", "max clock", "speed"), phrases=("clock", "clock speed", "cpu speed"),
                 other_sources=("Speed", "Max Frequency", "Operating Frequency")),  # FPGAs' "Speed" is a delay
    SortableSpec("Memory Size", "memory_capacity_bits", ("Capacity", "Memory Size"), parse_memory_size,
                 words=("density",), phrases=("memory size", "capacity", "density")),
    SortableSpec("Charge Current", "charge_current_a",
                 ("Charging Current", "Fast Charge Current", "Charge Current", "Charge Current - Max"), parse_current,
                 words=("charging current",), phrases=("charge current", "charging current")),
    SortableSpec("Clamping Voltage", "clamping_voltage_v", ("Clamping Voltage@Ipp", "Clamping Voltage"), parse_voltage,
                 words=("clamp voltage", "Vc"), phrases=("clamping voltage", "clamp voltage"),
                 conditions="peak pulse currents"),
    SortableSpec("Standoff Voltage", "standoff_voltage_v",
                 ("Reverse Stand-off Voltage(Vrwm)", "Reverse Stand-Off Voltage (Vrwm)"), parse_voltage,
                 words=("Vrwm", "stand-off voltage", "reverse standoff voltage"),
                 phrases=("standoff voltage", "stand-off voltage", "vrwm"),
                 other_sources=("Breakdown Voltage",)),  # reed switches
    SortableSpec("Peak Pulse Power", "surge_power_w",
                 ("Peak Pulse Power(Ppk)", "Peak Pulse Power (Ppk)", "Peak Pulse Power Dissipation (Ppp)"), parse_power,
                 words=("Ppk", "Ppp", "surge power"), phrases=("peak pulse power", "surge power"),
                 conditions="pulse waveforms"),
    SortableSpec("Voltage Rating", "voltage_max_v", ("Voltage Rating",), parse_voltage,
                 words=("Voltage", "rated voltage"), phrases=("voltage rating", "rated voltage"),
                 # a supply range's first number, and a resistor's working voltage
                 other_sources=("Voltage - Supply", "Voltage-Supply(Max)")),
    SortableSpec("Current Rating", "current_max_a", ("Current Rating",), parse_current,
                 words=("rated current",), phrases=("current rating", "rated current")),
    SortableSpec("Power", "power_w", ("Power(Watts)", "Pd - Power Dissipation"), parse_power,
                 words=("power rating", "power dissipation", "Pd"), phrases=("power rating", "power dissipation")),
    SortableSpec("Tolerance", "tolerance_pct", ("Tolerance",), parse_tolerance, phrases=("tolerance",)),
    SortableSpec("Resistance", "resistance_ohms", ("Resistance",), parse_resistance, zero_is_missing=False),
    SortableSpec("Capacitance", "capacitance_f", ("Capacitance",), parse_capacitance),
    SortableSpec("Inductance", "inductance_h", ("Inductance",), parse_inductance),
    SortableSpec("Vds", "vds_max_v", ("Drain to Source Voltage",), parse_voltage,
                 words=("drain to source voltage", "drain-source voltage", "Vdss"),
                 phrases=("vds", "vdss", "drain-source voltage")),
    SortableSpec("Id", "id_max_a", ("Current - Continuous Drain(Id)",), parse_current,
                 words=("drain current", "continuous drain current"), phrases=("drain current",)),
    SortableSpec("Vr", "vr_max_v", ("Voltage - DC Reverse(Vr)",), parse_voltage,
                 words=("reverse voltage",), phrases=("reverse voltage",)),
    SortableSpec("If", "if_max_a", ("Current - Rectified",), parse_current,
                 words=("rectified current", "forward current"), phrases=("forward current", "rectified current")),
    SortableSpec("Output Current", "iout_max_a", ("Output Current", "Output Current(Max)", "Iout"), parse_current,
                 phrases=("output current", "iout")),
)

# Specs refused, with the reason and what to do instead
_REFUSED: dict[tuple[str, ...], str] = {
    ("Output Voltage", "Vout"): "adjustable regulators list a range (\"0.8V~5V\"), so there's no one figure to "
                                "sort; filter it instead ({\"name\": \"Output Voltage\", \"op\": \"=\", \"value\": \"3.3V\"})",
    ("Supply Voltage", "Voltage - Supply", "Vcc", "Vin", "Input Voltage", "Operating Voltage", "Voltage-Supply(Max)"):
        "it's listed as a range (\"2.7V~5.5V\"); filter it instead ({\"name\": \"Supply Voltage\", \"op\": \"=\", "
        "\"value\": \"3.3V\"} keeps parts whose range includes 3.3V)",
    ("Frequency", "Frequency Range"): "many parts list a range; filter it instead",
    ("Operating Temperature", "Temperature"): "it's a range; filter it instead ({\"name\": \"Operating "
                                              "Temperature\", \"op\": \"<=\", \"value\": \"-40\"})",
    ("Sampling Rate", "Sample Rate"): "many converters list a range (\"16kHz~192kHz\")",
    ("Gain",): "many parts list a range (\"0dB~50dB\")",
    ("Slew Rate",): "the catalog lists it in V/µs, V/ms and V/ns, and these figures aren't converted to one unit",
    ("Vgs(th)", "Gate Threshold", "Gate Threshold Voltage", "Gate Threshold Voltage (Vgs(th))"):
        "it's a min~max range; filter it instead ({\"name\": \"Vgs(th)\", \"op\": \"<=\", \"value\": \"2.5V\"})",
    ("Luminous Intensity", "Brightness", "Wavelength", "Dominant Wavelength", "Wavelength - Dominant"):
        "many LEDs list one figure per colour or a range",
}


def _key(name: str) -> str:
    return re.sub(r"[\s\-_()]+", "", name.lower())


_BY_KEY: dict[str, SortableSpec] = {}
for _spec in SORTABLE_SPECS:
    for _name in (_spec.label, *_spec.names, *_spec.words, *_spec.phrases):
        _BY_KEY.setdefault(_key(_name), _spec)
_REFUSED_BY_KEY = {_key(name): (names[0], reason) for names, reason in _REFUSED.items() for name in names}
_BY_LABEL = {spec.label: spec for spec in SORTABLE_SPECS}
_ATTRIBUTE_SPEC = {name: spec for spec in SORTABLE_SPECS for name in spec.names}

SORTABLE_LABELS = [spec.label for spec in SORTABLE_SPECS]


class SortSpecError(ValueError):
    """A sort_spec that can't be sorted; str() is the reply's error, valid_values the choices."""

    def __init__(self, message: str):
        super().__init__(message)
        self.valid_values = SORTABLE_LABELS


def sort_spec_for_attribute(name: str) -> str | None:
    """The sort_spec label of a catalog attribute (jlc_search_help marks sortable attributes)."""
    spec = _ATTRIBUTE_SPEC.get(name)
    return spec.label if spec else None


def _lookup(name: str) -> SortableSpec | None:
    key = _key(name)
    if key in _BY_KEY:
        return _BY_KEY[key]
    # Short names the filters accept ("Vgs(th)" is refused above; "Rds(on)" etc. resolve)
    for full in get_attribute_names(name):
        if (spec := _ATTRIBUTE_SPEC.get(full)) is not None:
            return spec
    return None


def _format_amps(amps: float) -> str:
    return f"{amps * 1000:g}mA" if amps < 1 else f"{amps:g}A"


@dataclass(frozen=True)
class SpecSort:
    spec: SortableSpec
    descending: bool = False
    at: float | None = None
    at_source: str | None = None

    @classmethod
    def parse(cls, sort_spec: str, sort_order: str | None = None) -> "SpecSort":
        """A sort_spec ("Rds(on)", "Iq", "Dropout@500mA", "Rds(on) at 4.5V") and order ("asc"/"desc")."""
        text = str(sort_spec).strip()
        spec, condition = _lookup(text), None
        if spec is None and (match := _AT_LOAD.match(text)):
            spec, condition = _lookup(match.group(1)), match.group(2)
            text = match.group(1)
        if spec is None:
            refused = _REFUSED_BY_KEY.get(_key(text))
            if refused:
                raise SortSpecError(f"Can't sort by {refused[0]}: {refused[1]}.")
            raise SortSpecError(f"Unsupported sort_spec: '{sort_spec}'")
        at = None
        if condition is not None:
            if spec.at is None:
                raise SortSpecError(f"Can't sort {spec.label} at a condition: only RDS(on) (at a gate voltage, "
                                    "\"RDS(on)@4.5V\"), Voltage Dropout (at a load, \"Dropout@500mA\") and Vf "
                                    "(at a forward current, \"Vf@1A\") take one.")
            at = parse_voltage(condition) if spec.at == "gate" else parse_current(condition)
            if not at or at <= 0:
                unit = "a gate voltage" if spec.at == "gate" else "a current"
                raise SortSpecError(f"Can't sort {spec.label} at '{condition}': give {unit}, as in "
                                    f"\"{spec.label}@{spec.example_at}\".")
        return cls(spec, descending=sort_order == "desc", at=at)

    def with_condition(self, spec_filters: list[Any] | None, gate_drive_v: float | None) -> "SpecSort":
        """Take the condition from the search when sort_spec didn't give one: the query's gate drive for
        RDS(on), a Dropout filter's load or the Output Current wanted for dropout, the If wanted for Vf."""
        if self.at is not None or self.spec.at is None:
            return self
        if self.spec.at == "gate":
            if gate_drive_v is not None:
                return replace(self, at=gate_drive_v, at_source="the query's gate drive")
            return self
        if self.spec.at == "load" and (loads := dropout_loads(spec_filters)):
            return replace(self, at=loads[0], at_source="the Dropout filter")
        wanted = "Output Current" if self.spec.at == "load" else "Current - Rectified"
        for f in spec_filters or []:
            if (getattr(f, "operator", None) in (">=", ">", "=")
                    and wanted in [f.name, *get_attribute_names(f.name)]
                    and (amps := parse_current(str(f.value)))):
                return replace(self, at=amps, at_source=f"the {f.name} filter")
        return self

    def order_sql(self) -> tuple[str, list[Any]]:
        """The ORDER BY term (missing values last) and its parameters. The Python functions run only on
        parts whose column has a value (a catalog-wide RDS(on) sort ran them on all 640,000 parts)."""
        spec, column = self.spec, self.spec.column
        if self.at is not None and spec.at == "gate":
            key = f"CASE WHEN {column} IS NULL THEN NULL ELSE rds_on_at_drive_ohms(components.attributes, ?) END"
            params: list[Any] = [self.at]
        elif self.at is not None and spec.at == "load":
            # Parts rated below the load have no dropout there
            key = (f"CASE WHEN {column} IS NULL OR iout_max_a < ? THEN NULL "
                   "ELSE dropout_sort_value(components.attributes, ?) END")
            params = [self.at * (1 - 1e-9), self.at]
        elif self.at is not None and spec.at == "current":
            key, params = f"CASE WHEN {column} IS NULL THEN NULL ELSE vf_at_current(components.attributes, ?) END", [self.at]
        else:
            value = f"CASE WHEN {column} > 0 THEN {column} END" if spec.zero_is_missing else column
            if spec.other_sources:
                # The column is this spec's when the part lists it and none of the other sources
                listed = " OR ".join("instr(components.attributes, ?) > 0" for _ in spec.names)
                others = " OR ".join("instr(components.attributes, ?) > 0" for _ in spec.other_sources)
                key = (f"CASE WHEN {column} IS NULL OR NOT ({listed}) THEN NULL WHEN {others} "
                       f"THEN spec_sort_value(components.attributes, ?) ELSE {value} END")
                params = [*map(json.dumps, spec.names), *map(json.dumps, spec.other_sources), spec.label]
            else:
                key, params = value, []
        return f"{key} {'DESC' if self.descending else 'ASC'} NULLS LAST", params

    def value_text(self, specs: dict[str, str]) -> str | None:
        """What a result was sorted on, as listed (with its test condition), or None when it doesn't
        list it (those come last)."""
        spec = self.spec
        if self.at is not None and spec.at == "gate":
            entry = rds_on_at_drive(specs.get("RDS(on)", ""), self.at)
            return entry if entry and _valid(spec, parse_resistance(entry.split("@")[0])) is not None else None
        if self.at is not None and spec.at == "load":
            rated = next((parse_current(specs[n]) for n in ("Output Current", "Output Current(Max)", "Iout")
                          if specs.get(n)), None)
            found = dropout_at_load(specs.get("Voltage Dropout"), self.at)
            if found is None or (rated is not None and rated < self.at * (1 - 1e-9)):
                return None
            volts, listed, scaled = found
            if volts <= 0:
                return None
            return f"{volts * 1000:.0f}mV at {_format_amps(self.at)} (from {listed}{', scaled linearly' if scaled else ''})"
        if self.at is not None and spec.at == "current":
            found = vf_at_current(specs.get("Voltage - Forward(Vf@If)"), self.at)
            return found[1] if found else None
        for name in spec.names:
            if (text := specs.get(name)) is not None and _valid(spec, spec.parser(text)) is not None:
                return text
        return None

    def summary(self, prefer_no_fee: bool) -> dict[str, Any]:
        spec = self.spec
        out: dict[str, Any] = {"spec": spec.label, "order": "desc" if self.descending else "asc"}
        if self.at is not None:
            what = {"gate": f"{self.at:g}V gate drive", "load": f"{_format_amps(self.at)} load",
                    "current": f"{_format_amps(self.at)} forward current"}[spec.at]
            out["at"] = what + (f" (from {self.at_source})" if self.at_source else "")
        ties = "basic/preferred parts, then stock" if prefer_no_fee else "stock"
        notes = []
        if self.at is not None and spec.at == "gate":
            notes.append(f"RDS(on) as listed at the highest gate voltage at or below {self.at:g}V (sort_value); "
                         f"parts listing it only at higher gate voltages come last, since theirs at {self.at:g}V "
                         "isn't known.")
        elif self.at is not None and spec.at == "load":
            amps = _format_amps(self.at)
            notes.append(f"Dropout at {amps}: the figure listed at or above that load, or a lower test current's "
                         f"figure scaled up linearly (sort_value shows which); parts rated below {amps} come last.")
        elif self.at is not None and spec.at == "current":
            amps = _format_amps(self.at)
            notes.append(f"Vf as listed at {amps} or more (sort_value), which bounds it at {amps}; parts listing "
                         "it only at lower currents come last.")
        elif spec.conditions:
            note = (f"{spec.label} is listed at different {spec.conditions} (sort_value shows each part's), so this "
                    "is the order of the catalog figures, not a like-for-like comparison")
            if spec.at:
                note += f"; sort_spec=\"{spec.label}@{spec.example_at}\" compares them at one condition"
            notes.append(note + ".")
        if spec.caveat:
            notes.append(spec.caveat)
        notes.append(f"Parts that don't list it come last (sort_value null); ties go to {ties}. These are "
                     "JLCPCB's listed figures, and a mistyped one sorts to the top, so check the "
                     "datasheets of the parts you pick.")
        out["note"] = " ".join(notes)
        return out


def _valid(spec: SortableSpec, value: float | None) -> float | None:
    if value is None or (spec.zero_is_missing and value <= 0):
        return None
    return float(value)


def vf_at_current(value: str | None, amps: float) -> tuple[float, str] | None:
    """A diode's Vf at a forward current from its listed "450mV@1A" pairs: (volts, the pair used). Vf
    rises with current, so a figure listed at that current or above bounds it; the one listed at the
    lowest such current is used. None when no pair is listed at or above it."""
    pairs = []
    for v_text, a_text in _DROPOUT_PAIR.findall(str(value or "")):
        volts, current = parse_voltage(v_text), parse_current(a_text)
        if volts is not None and volts > 0 and current and current >= amps * (1 - 1e-9):
            pairs.append((current, volts, f"{v_text}@{a_text}"))
    if not pairs:
        return None
    _, volts, text = min(pairs)
    return volts, text


def _attributes(attributes: str | None) -> dict[str, str]:
    try:
        return {name: value for name, value in json.loads(attributes or "[]")}
    except (TypeError, ValueError):
        return {}


def rds_on_at_drive_ohms(attributes: str | None, drive: float) -> float | None:
    """SQLite rds_on_at_drive_ohms(attributes, V): the RDS(on) rds_on_at_drive() picks, in ohms."""
    entry = rds_on_at_drive(_attributes(attributes).get("RDS(on)", ""), drive)
    ohms = parse_resistance(entry.split("@")[0]) if entry else None
    return ohms if ohms and ohms > 0 else None  # "0mΩ" is a placeholder


def dropout_sort_value(attributes: str | None, load_a: float) -> float | None:
    """SQLite dropout_sort_value(attributes, A): dropout_at_load() for sorting, a listed 0 left out."""
    volts = dropout_at_load_json(attributes, load_a)
    return volts if volts and volts > 0 else None


def vf_at_current_json(attributes: str | None, amps: float) -> float | None:
    """SQLite vf_at_current(attributes, A): vf_at_current() of the listed Vf, in volts."""
    found = vf_at_current(_attributes(attributes).get("Voltage - Forward(Vf@If)"), amps)
    return found[0] if found else None


def spec_sort_value_json(attributes: str | None, label: str) -> float | None:
    """SQLite spec_sort_value(attributes, label): a spec read from its own attributes only, for columns
    also filled from attributes that mean something else."""
    spec = _BY_LABEL.get(label)
    if spec is None:
        return None
    specs = _attributes(attributes)
    for name in spec.names:
        if (text := specs.get(name)) is not None:
            return _valid(spec, spec.parser(text))
    return None


# Query words: "lowest Iq", "highest Isat", "smallest DCR", "most flash"
# Not "minimum"/"maximum": "minimum flash 64KB" is a floor, not a sort
_ASCENDING = ("lowest", "smallest", "least", "tightest", "lowest possible")
_DESCENDING = ("highest", "largest", "biggest", "most", "greatest", "longest")
_PHRASES = sorted({phrase: spec for spec in SORTABLE_SPECS for phrase in spec.phrases}.items(),
                  key=lambda item: -len(item[0]))
_SUPERLATIVE = re.compile(
    r"(?<!\bat\s)\b(?P<word>" + "|".join(map(re.escape, (*_ASCENDING, *_DESCENDING))) + r")\s+(?P<phrase>"
    + "|".join(re.escape(phrase) for phrase, _ in _PHRASES) + r")(?![\w(])",
    re.IGNORECASE,
)
_PHRASE_SPEC = {phrase: spec for phrase, spec in _PHRASES}


def extract_sort_phrase(query: str) -> tuple[SpecSort | None, str | None, str]:
    """A query's "lowest Iq" / "highest Isat": (the sort, the words, the query without them)."""
    match = _SUPERLATIVE.search(query)
    if not match:
        return None, None, query
    spec = _PHRASE_SPEC[match.group("phrase").lower()]
    descending = match.group("word").lower() in _DESCENDING
    remaining = re.sub(r"\s+", " ", query[:match.start()] + " " + query[match.end():]).strip()
    return SpecSort(spec, descending=descending), match.group(0), remaining
