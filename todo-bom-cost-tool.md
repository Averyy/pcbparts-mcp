# BOM Cost Optimization

**Goal**: Help users save money by finding basic/preferred alternatives for extended parts.

**User Value**: High ($5-50 savings per BOM depending on extended parts count)

---

## The Real Problem

The `find_alternatives` tool is broken. It returns useless and potentially dangerous results.

### Current behavior

```python
find_alternatives("C25804")  # 10kΩ 0603 resistor
# Returns: 1kΩ, 100Ω, 100kΩ, 10kΩ, 100kΩ resistors
# Only 1 out of 5 actually matches. Useless and dangerous.
```

**Why it's broken:**
1. **No spec matching** - Searches by subcategory only, ignoring the actual component value
2. **No compatibility checks** - Could suggest 6.3V cap as replacement for 25V cap
3. **Dumb sorting** - Just returns highest stock parts, not best alternatives
4. **No library type preference** - Doesn't prioritize basic/preferred (which save $3)

### What it should do

```python
find_alternatives("C25804")  # 10kΩ ±1% 0603 resistor
# Returns: Only 10kΩ resistors with ±1% or better tolerance, ranked by:
#   1. Basic/preferred first (saves $3 assembly fee)
#   2. Good availability (>1000 stock)
#   3. Lower price (tiebreaker)
```

---

## The Fix

### Step 1: Match by Primary Spec

Use `KEY_ATTRIBUTES` to search for parts with the same primary spec value:

```python
# After fetching original part:
if subcategory_name in KEY_ATTRIBUTES:
    primary_attr = KEY_ATTRIBUTES[subcategory_name][0]
    primary_value = original.get("specs", {}).get(primary_attr)
    if primary_value:
        search_params["query"] = primary_value
```

### Step 2: Compatibility Filtering (CRITICAL)

**We must not suggest incompatible parts.** After search, filter results to ensure compatibility.

The logic is driven by `COMPATIBILITY_RULES` dict (defined once in Step 6). Each rule specifies:
- `must_match`: Specs that must be identical (e.g., dielectric type, color)
- `same_or_better`: Specs where candidate must be ≥ or ≤ original

```python
def is_compatible_alternative(original: dict, candidate: dict, subcategory: str) -> tuple[bool, dict]:
    """
    Check if candidate is a compatible alternative for original.
    Returns (is_compatible, verification_info) tuple.
    verification_info contains specs_verified and specs_unparseable lists.
    """
    rules = COMPATIBILITY_RULES.get(subcategory)
    if not rules:
        return True, {"specs_verified": [], "specs_unparseable": []}

    orig_specs = original.get("specs", {})
    cand_specs = candidate.get("specs", {})

    specs_verified = []
    specs_unparseable = []

    # Check must_match specs (exact equality required)
    for spec in rules.get("must_match", []):
        orig_val = orig_specs.get(spec)
        cand_val = cand_specs.get(spec)
        if orig_val and cand_val:
            if not _values_match(orig_val, cand_val, spec):
                return False, {"specs_verified": specs_verified, "specs_unparseable": specs_unparseable}
            specs_verified.append(spec)
        elif orig_val or cand_val:
            specs_unparseable.append(spec)  # One side missing

    # Check same_or_better specs
    for spec, direction in rules.get("same_or_better", {}).items():
        orig_val = orig_specs.get(spec)
        cand_val = cand_specs.get(spec)
        if orig_val and cand_val:
            parser = SPEC_PARSERS.get(spec)
            if parser and parser(orig_val) is not None and parser(cand_val) is not None:
                if not _spec_ok(orig_val, cand_val, spec, direction):
                    return False, {"specs_verified": specs_verified, "specs_unparseable": specs_unparseable}
                specs_verified.append(spec)
            else:
                specs_unparseable.append(spec)  # Couldn't parse
        elif orig_val or cand_val:
            specs_unparseable.append(spec)  # One side missing

    return True, {"specs_verified": specs_verified, "specs_unparseable": specs_unparseable}
```

### Step 3: Spec Parsing Helpers

Unified parsing approach - each parser returns a float in base units for comparison:

```python
def parse_voltage(s: str) -> float | None:
    """Parse voltage: '25V' → 25, '6.3V' → 6.3, '3.3V' → 3.3"""
    if not s:
        return None
    match = re.search(r"([\d.]+)\s*V", s, re.IGNORECASE)
    return float(match.group(1)) if match else None

def parse_tolerance(s: str) -> float | None:
    """Parse tolerance: '±1%' → 1, '±10%' → 10, '1%' → 1"""
    if not s:
        return None
    match = re.search(r"([\d.]+)\s*%", s)
    return float(match.group(1)) if match else None

def parse_power(s: str) -> float | None:
    """Parse power in watts: '100mW' → 0.1, '1/4W' → 0.25, '0.25W' → 0.25"""
    if not s:
        return None
    # Handle fraction format: 1/4W, 1/10W
    match = re.search(r"(\d+)/(\d+)\s*W", s, re.IGNORECASE)
    if match:
        return float(match.group(1)) / float(match.group(2))
    # Handle mW
    match = re.search(r"([\d.]+)\s*mW", s, re.IGNORECASE)
    if match:
        return float(match.group(1)) / 1000
    # Handle W
    match = re.search(r"([\d.]+)\s*W", s, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None

def parse_current(s: str) -> float | None:
    """Parse current in amps: '2A' → 2, '500mA' → 0.5, '100µA' → 0.0001"""
    if not s:
        return None
    match = re.search(r"([\d.]+)\s*[uµ]A", s, re.IGNORECASE)
    if match:
        return float(match.group(1)) / 1_000_000
    match = re.search(r"([\d.]+)\s*mA", s, re.IGNORECASE)
    if match:
        return float(match.group(1)) / 1000
    match = re.search(r"([\d.]+)\s*A", s, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None

def parse_resistance(s: str) -> float | None:
    """Parse resistance in ohms: '10kΩ' → 10000, '10K' → 10000, '4.7MΩ' → 4700000"""
    if not s:
        return None
    # Normalize: remove Ω/ohm, handle k/K/M suffixes
    s = s.replace("Ω", "").replace("ohm", "").strip()
    match = re.search(r"([\d.]+)\s*([kKmM])?", s)
    if not match:
        return None
    value = float(match.group(1))
    suffix = (match.group(2) or "").upper()
    if suffix == "K":
        return value * 1000
    elif suffix == "M":
        return value * 1_000_000
    return value

def parse_capacitance(s: str) -> float | None:
    """Parse capacitance in farads: '100nF' → 1e-7, '10µF' → 1e-5, '1pF' → 1e-12"""
    if not s:
        return None
    s = s.replace("F", "").strip()
    match = re.search(r"([\d.]+)\s*([pnuµm])?", s, re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    suffix = (match.group(2) or "").lower()
    if suffix == "p":
        return value * 1e-12
    elif suffix == "n":
        return value * 1e-9
    elif suffix in ("u", "µ"):
        return value * 1e-6
    elif suffix == "m":
        return value * 1e-3
    return value  # Assume farads if no suffix

def parse_inductance(s: str) -> float | None:
    """Parse inductance in henries: '10µH' → 1e-5, '100nH' → 1e-7, '1mH' → 1e-3"""
    if not s:
        return None
    s = s.replace("H", "").strip()
    match = re.search(r"([\d.]+)\s*([nuµm])?", s, re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    suffix = (match.group(2) or "").lower()
    if suffix == "n":
        return value * 1e-9
    elif suffix in ("u", "µ"):
        return value * 1e-6
    elif suffix == "m":
        return value * 1e-3
    return value  # Assume henries if no suffix

def parse_frequency(s: str) -> float | None:
    """Parse frequency in Hz: '8MHz' → 8e6, '32.768kHz' → 32768"""
    if not s:
        return None
    s = s.replace("Hz", "").strip()
    match = re.search(r"([\d.]+)\s*([kKmMgG])?", s)
    if not match:
        return None
    value = float(match.group(1))
    suffix = (match.group(2) or "").upper()
    if suffix == "K":
        return value * 1e3
    elif suffix == "M":
        return value * 1e6
    elif suffix == "G":
        return value * 1e9
    return value

def parse_impedance_at_freq(s: str) -> tuple[float, float] | None:
    """Parse impedance @ frequency: '600Ω @ 100MHz' → (600, 100e6)
    Returns (impedance_ohms, frequency_hz) tuple for comparison.
    """
    if not s:
        return None
    # Normalize: Ω, Ohm, ohm → unified
    s = s.replace("Ω", "Ohm").replace("ohm", "Ohm")
    # Pattern: <impedance><unit> @ <frequency><unit>
    match = re.search(r"([\d.]+)\s*([kKmM])?Ohm\s*@\s*([\d.]+)\s*([kKmMgG])?Hz", s, re.IGNORECASE)
    if not match:
        return None

    # Parse impedance
    imp_value = float(match.group(1))
    imp_suffix = (match.group(2) or "").upper()
    if imp_suffix == "K":
        imp_value *= 1000
    elif imp_suffix == "M":
        imp_value *= 1_000_000

    # Parse frequency
    freq_value = float(match.group(3))
    freq_suffix = (match.group(4) or "").upper()
    if freq_suffix == "K":
        freq_value *= 1e3
    elif freq_suffix == "M":
        freq_value *= 1e6
    elif freq_suffix == "G":
        freq_value *= 1e9

    return (imp_value, freq_value)

def impedance_at_freq_match(orig: str, cand: str) -> bool:
    """Check if two 'Impedance @ Frequency' values match.
    Both impedance AND frequency must match (within 2% each).
    """
    orig_parsed = parse_impedance_at_freq(orig)
    cand_parsed = parse_impedance_at_freq(cand)

    if orig_parsed is None or cand_parsed is None:
        # Can't parse, fall back to normalized string match
        return orig.replace("Ω", "Ohm").lower() == cand.replace("Ω", "Ohm").lower()

    orig_imp, orig_freq = orig_parsed
    cand_imp, cand_freq = cand_parsed

    # Both impedance and frequency must be within 2%
    if orig_imp == 0 or orig_freq == 0:
        return cand_imp == orig_imp and cand_freq == orig_freq

    imp_ok = abs(orig_imp - cand_imp) / orig_imp < 0.02
    freq_ok = abs(orig_freq - cand_freq) / orig_freq < 0.02

    return imp_ok and freq_ok
```

### Step 4: Generic Comparison Functions

Two helper functions that work with any spec, driven by COMPATIBILITY_RULES:

```python
# Map spec names to their parser functions
SPEC_PARSERS = {
    "Voltage Rating": parse_voltage,
    "Voltage - DC Reverse(Vr)": parse_voltage,
    "Drain to Source Voltage": parse_voltage,
    "Collector - Emitter Voltage VCEO": parse_voltage,
    "Reverse Stand-Off Voltage (Vrwm)": parse_voltage,
    "Clamping Voltage": parse_voltage,
    "Isolation Voltage(Vrms)": parse_voltage,
    "Voltage - Max": parse_voltage,
    "Output Voltage": parse_voltage,
    "Voltage Dropout": parse_voltage,
    "Zener Voltage(Nom)": parse_voltage,
    "Tolerance": parse_tolerance,
    "Frequency Stability": parse_tolerance,  # ±ppm is like tolerance
    "Power(Watts)": parse_power,
    "Pd - Power Dissipation": parse_power,
    "Peak Pulse Power": parse_power,
    "Current - Continuous Drain(Id)": parse_current,
    "Current - Collector(Ic)": parse_current,
    "Current - Rectified": parse_current,
    "Current Rating": parse_current,
    "Current - Saturation(Isat)": parse_current,
    "Current - Saturation (Isat)": parse_current,  # Variant with space
    "Output Current": parse_current,
    "Hold Current": parse_current,
    "Trip Current": parse_current,
    "DC Resistance(DCR)": parse_resistance,
    "RDS(on)": parse_resistance,  # Stored as mΩ
    "Voltage - Forward(Vf@If)": parse_voltage,
    "Resistance": parse_resistance,
    "Capacitance": parse_capacitance,
    "Inductance": parse_inductance,
    "Frequency": parse_frequency,
    "Impedance @ Frequency": "special",  # Uses impedance_at_freq_match()
    "Load Capacitance": parse_capacitance,
    # Additional specs for expanded subcategories
    "Current - Average Rectified": parse_current,
    "Drain Current (Idss)": parse_current,
    "Collector-Emitter Breakdown Voltage (Vces)": parse_voltage,
    "Vce Saturation(VCE(sat))": parse_voltage,
    "Peak Wavelength": None,  # String match (850nm, 940nm)
    "Resistance @ 25℃": parse_resistance,
    "B Constant (25℃/100℃)": None,  # String match
    "Varistor Voltage": parse_voltage,
    "Energy": None,  # Complex format (Joules), string match
    "Temperature Coefficient": parse_tolerance,  # ppm/°C similar to tolerance
    "FET Type": None,  # String match (N-Channel, P-Channel)
    # Switches and relays
    "Contact Current": parse_current,
    "Contact Rating": parse_current,  # Often in Amps
    "Coil Voltage": parse_voltage,
    "Switching Voltage(Max)": parse_voltage,
    "Switching Current(Max)": parse_current,
    "Load Voltage": parse_voltage,
    "Load Current": parse_current,
    "Voltage Rating (DC)": parse_voltage,
    "Voltage Rating (Max)": parse_voltage,
    # Connectors
    "Number of Positions": None,  # Integer, string match
    "Number of Pins": None,  # Integer, string match
    "Number of Positions or Pins": None,  # Integer, string match
    "Number of Rows": None,  # Integer, string match
    "Pitch": None,  # String match (2.54mm, 1.27mm, etc)
    # Switches
    "Circuit": None,  # String match (SPST, SPDT, DPDT)
    "Contact Form": None,  # String match for relays
    "Mounting Type": None,  # String match
    "Self Lock / No Lock": None,  # String match
    "Positions": None,  # Integer for rotary switches
    "Number of Poles Per Deck": None,  # Integer
    "Type": None,  # Generic string match
    "Connector Type": None,  # String match
    "Gender": None,  # String match (Male, Female)
    "Rated Functioning Temperature": None,  # String match
    # More voltages/currents
    "Reverse Voltage": parse_voltage,
    "Average Rectified Current": parse_current,
    "Voltage(AC)": parse_voltage,
    "Voltage Rating (AC)": parse_voltage,
    "Voltage Rating - DC": parse_voltage,
    "Output Current(Max)": parse_current,
    "Data Rate": None,  # String match (Mbps)
    "Data Rate(Max)": None,  # String match
    "Impulse Discharge Current": parse_current,
    "Peak Pulse Current-Ipp (10/1000us)": parse_current,
    "Isolation Voltage(Vrms)": parse_voltage,
    "Rated Power": parse_power,
    "Sound Pressure Level": None,  # dB, string match
    "Cell Resistance @ Illuminance": parse_resistance,
    # Arrays
    "Number of Resistors": None,  # Integer, string match
    "Number of Capacitors": None,  # Integer, string match
    "Number of Lines": None,  # Integer, string match
    "Number of Forward Channels": None,  # Integer, string match
    "Number of Reverse Channels": None,  # Integer, string match
    "Number of Poles": None,  # Integer, string match
    "Number of Turns": None,  # Integer, string match
    "Number of Coils": None,  # Integer, string match
    # Misc
    "Impedance": None,  # String match (for RF/audio)
    "Ratings": None,  # String match (X1, X2, Y1, Y2)
    "Driver Circuitry": None,  # String match (Active, Passive)
    "Pins Structure": None,  # String match
    "Peak off - state voltage(Vdrm)": parse_voltage,
    "Trigger Voltage": parse_voltage,
    # More misc
    "Rated Voltage (Max)": parse_voltage,
    "Current Rating (Max)": parse_current,
    "Output Current": parse_current,
    "Color": None,  # String match
    "Number of Segments": None,  # Integer, string match
    "Direction": None,  # String match (Omnidirectional, Unidirectional)
    "Encoder Type": None,  # String match
}

def _values_match(orig_val: str, cand_val: str, spec: str) -> bool:
    """Check if two spec values match (for must_match rules)."""
    # Special handler for complex formats
    if spec == "Impedance @ Frequency":
        return impedance_at_freq_match(orig_val, cand_val)

    # String-based specs: exact match (case-insensitive)
    STRING_MATCH_SPECS = {
        "Temperature Coefficient", "Illumination Color", "type", "Output Type",
        "Peak Wavelength", "FET Type", "B Constant (25℃/100℃)",
        # Connectors
        "Number of Positions", "Number of Pins", "Number of Positions or Pins",
        "Number of Rows", "Pitch", "Connector Type", "Gender", "Pins Structure",
        # Switches
        "Circuit", "Contact Form", "Mounting Type", "Self Lock / No Lock",
        "Positions", "Number of Poles Per Deck", "Type",
        # Fuses
        "Rated Functioning Temperature",
        # Arrays/Networks
        "Number of Resistors", "Number of Capacitors", "Number of Lines",
        "Number of Forward Channels", "Number of Reverse Channels",
        "Number of Poles", "Number of Turns", "Number of Coils",
        # Audio/RF
        "Impedance", "Driver Circuitry",
        # Capacitors
        "Ratings",  # X1, X2, Y1, Y2 safety class
        # Data rates (string format varies too much)
        "Data Rate", "Data Rate(Max)",
        # Opto/misc
        "Color", "Number of Segments", "Direction", "Encoder Type",
    }
    if spec in STRING_MATCH_SPECS:
        return orig_val.strip().lower() == cand_val.strip().lower()

    # Numeric specs: parse and compare with tolerance
    parser = SPEC_PARSERS.get(spec)
    if parser:
        orig_parsed = parser(orig_val)
        cand_parsed = parser(cand_val)
        if orig_parsed is None or cand_parsed is None:
            return True  # Can't parse, allow through
        # 2% tolerance for matching (handles rounding differences in display)
        if orig_parsed == 0:
            return cand_parsed == 0
        return abs(orig_parsed - cand_parsed) / abs(orig_parsed) < 0.02

    # Fallback: string match
    return orig_val.strip().lower() == cand_val.strip().lower()

def _spec_ok(orig_val: str, cand_val: str, spec: str, direction: str) -> bool:
    """Check if candidate spec meets same_or_better requirement."""
    parser = SPEC_PARSERS.get(spec)
    if not parser:
        return True  # Can't parse, allow through

    orig_parsed = parser(orig_val)
    cand_parsed = parser(cand_val)

    if orig_parsed is None or cand_parsed is None:
        return True  # Can't parse, allow through

    if direction == "higher":
        return cand_parsed >= orig_parsed * 0.98  # 2% tolerance
    elif direction == "lower":
        return cand_parsed <= orig_parsed * 1.02  # 2% tolerance
    else:
        return True
```

### Step 5: Verify Primary Spec Match

JLCPCB search may return fuzzy matches. After search, verify the primary spec actually matches:

```python
def verify_primary_spec_match(original: dict, candidate: dict, primary_attr: str) -> bool:
    """Verify candidate has same primary spec value as original."""
    orig_value = original.get("specs", {}).get(primary_attr)
    cand_value = candidate.get("specs", {}).get(primary_attr)

    if not orig_value or not cand_value:
        return True  # Can't verify, allow through

    # Use _values_match for consistent comparison
    return _values_match(orig_value, cand_value, primary_attr)
```

### Step 6: Smart Ranking

After filtering to compatible parts only, rank by usefulness:

```python
def score_alternative(part, original, min_price_in_results):
    score = 0
    breakdown = {}

    # Library type (biggest factor - $3 savings)
    if part["library_type"] in ("basic", "preferred"):
        score += 1000
        breakdown["library_type"] = 1000
    else:
        breakdown["library_type"] = 0

    # Availability (user controls floor via min_stock param)
    stock = part["stock"]
    if stock >= 10000:
        avail_score = 70   # Excellent availability
    elif stock >= 1000:
        avail_score = 50   # Good availability
    elif stock >= 100:
        avail_score = 30   # Acceptable
    else:
        avail_score = -10  # Minor penalty for <100
    score += avail_score
    breakdown["availability"] = avail_score

    # EasyEDA footprint bonus (easier for users)
    if part.get("has_easyeda_footprint"):
        score += 20
        breakdown["easyeda"] = 20
    else:
        breakdown["easyeda"] = 0

    # Same manufacturer bonus (consistency)
    if part.get("manufacturer") == original.get("manufacturer"):
        score += 10
        breakdown["same_manufacturer"] = 10
    else:
        breakdown["same_manufacturer"] = 0

    # Price (minor factor, tiebreaker only)
    if part["price"] and min_price_in_results:
        price_ratio = min_price_in_results / part["price"]
        price_score = int(10 * price_ratio)  # 0-10 points
        score += price_score
        breakdown["price"] = price_score
    else:
        breakdown["price"] = 0

    return score, breakdown
```

**Priority order:**
1. **Compatible specs** (must pass) - filter, not score
2. **Primary spec verified** (must match) - filter, not score
3. **Library type** (+1000 for basic/preferred) - $3 savings dwarfs price differences
4. **Availability** (+70/+50/+30/-10) - supply chain reliability
5. **EasyEDA footprint** (+20) - easier to use in designs
6. **Same manufacturer** (+10) - consistency bonus
7. **Price** (+0-10) - minor tiebreaker

Note: The `min_stock` parameter (default 100) controls the hard filter. Scoring just ranks parts that pass the filter.

### Step 7: Response Enhancement

Make the response genuinely helpful, not just raw data.

**Key distinction:** For unsupported subcategories, return `similar_parts` (not `alternatives`) to make clear these aren't verified suggestions.

```python
def build_response(original, scored_alternatives, subcategory, primary_attr, primary_value, limit):
    # Check if this is a supported subcategory
    is_supported = subcategory in COMPATIBILITY_RULES

    # For unsupported subcategories, return different response structure
    if not is_supported:
        return build_unsupported_response(original, scored_alternatives, subcategory, primary_attr, limit)

    # Supported subcategory - return verified alternatives
    alternatives = scored_alternatives[:limit]

    # Count basic/preferred alternatives
    no_fee_count = sum(1 for _, p, _, _ in alternatives
                       if p["library_type"] in ("basic", "preferred"))

    # Determine confidence based on verification coverage
    all_specs_verified = all(len(v["specs_unparseable"]) == 0 for _, _, _, v in alternatives) if alternatives else True
    confidence = "high" if all_specs_verified else "medium"
    confidence_reason = "All critical specs verified compatible" if all_specs_verified else "Some specs could not be parsed - verify manually"

    # Build human-readable summary
    if not alternatives:
        if original["library_type"] in ("basic", "preferred"):
            message = "Original part is already basic/preferred - no assembly fee savings possible"
        else:
            message = f"No compatible alternatives found matching {primary_value}"
    elif no_fee_count > 0:
        message = f"Found {no_fee_count} basic/preferred alternative(s) that save $3 assembly fee"
    else:
        message = f"Found {len(alternatives)} alternative(s), but all are extended library"

    # Calculate savings vs best alternative
    # Note: price is unit price at qty 1 tier
    best_part = alternatives[0][1] if alternatives else None  # (score, part, breakdown, verify_info)
    savings = None
    if best_part:
        assembly_savings = 3.0 if (
            original["library_type"] == "extended" and
            best_part["library_type"] in ("basic", "preferred")
        ) else 0.0
        price_diff = (original.get("price") or 0) - (best_part.get("price") or 0)
        savings = {
            "assembly_fee": assembly_savings,
            "unit_price_diff": round(price_diff, 4),  # Price at qty 1
            "total_per_unit": round(assembly_savings + price_diff, 4),
        }

    # Comparison helper
    comparison = None
    if best_part:
        comparison = {
            "original": {
                "lcsc": original["lcsc"],
                "library_type": original["library_type"],
                "price": original.get("price"),
                "stock": original.get("stock"),
            },
            "recommended": {
                "lcsc": best_part["lcsc"],
                "library_type": best_part["library_type"],
                "price": best_part.get("price"),
                "stock": best_part.get("stock"),
            },
            "savings": savings,
        }

    # Build alternatives list with verification info and MOQ warnings
    alternatives_output = []
    for score, part, breakdown, verify_info in alternatives:
        alt = {
            **part,
            "score": score,
            "score_breakdown": breakdown,
            "datasheet": part.get("datasheet"),  # Include for verification
            "specs_verified": verify_info["specs_verified"],
            "specs_unparseable": verify_info["specs_unparseable"],
        }
        # Add MOQ warning if high
        moq = part.get("moq", 1)
        if moq > 100:
            alt["moq_warning"] = f"High MOQ: {moq} units minimum"
        alternatives_output.append(alt)

    return {
        "original": original,
        "alternatives": alternatives_output,
        "summary": {
            "found": len(alternatives),
            "basic_preferred_count": no_fee_count,
            "message": message,
            "is_supported_category": True,
            "price_note": "Prices shown are unit price at qty 1 tier",
        },
        "comparison": comparison,
        "confidence": {
            "level": confidence,
            "reason": confidence_reason,
        },
        "search_criteria": {
            "primary_attribute": primary_attr,
            "matched_value": primary_value,
            "subcategory": subcategory,
            "compatibility_rules_applied": subcategory in COMPATIBILITY_RULES,
        },
    }
```

### Step 7b: Unsupported Subcategory Response

For subcategories without COMPATIBILITY_RULES, return `similar_parts` instead of `alternatives`:

```python
def build_unsupported_response(original, scored_parts, subcategory, primary_attr, limit):
    """Build response for unsupported subcategories - similar parts, not alternatives."""
    similar = scored_parts[:limit]

    # Get the key specs to verify from KEY_ATTRIBUTES
    specs_to_verify = KEY_ATTRIBUTES.get(subcategory, [])

    # Note: scored_parts has 4-tuple but unsupported has empty verify_info
    return {
        "original": original,
        "alternatives": [],  # Empty - we can't verify compatibility
        "similar_parts": [
            {
                **part,
                "score": score,
                "score_breakdown": breakdown,
                "moq_warning": f"High MOQ: {part.get('moq', 1)} units minimum" if part.get('moq', 1) > 100 else None,
            }
            for score, part, breakdown, _ in similar
        ],
        "summary": {
            "found": len(similar),
            "message": "No compatibility rules for this category. Showing similar parts for manual comparison.",
            "is_supported_category": False,
            "price_note": "Prices shown are unit price at qty 1 tier",
        },
        "manual_comparison": {
            "original_specs": original.get("specs", {}),
            "specs_to_verify": specs_to_verify,
            "guidance": f"Compare these specs manually: {', '.join(specs_to_verify[:5])}" if specs_to_verify else "Review datasheets for compatibility",
        },
        "search_criteria": {
            "primary_attribute": primary_attr,
            "matched_value": original.get("specs", {}).get(primary_attr) if primary_attr else None,
            "subcategory": subcategory,
            "compatibility_verified": False,
        },
    }
```

**Why this matters:**
- `alternatives` implies verified interchangeability - we shouldn't claim that
- `similar_parts` is honest - these are parts in the same subcategory
- `manual_comparison` helps user know what to check
- Clear `is_supported_category: False` flag for programmatic use

### Step 8: Graceful Edge Case Handling

```python
def get_no_alternatives_reason(original, subcategory, primary_value, search_results, compatible_results):
    """Explain why no alternatives were found (for supported categories only)."""

    if original["library_type"] in ("basic", "preferred"):
        return "already_optimal", "Original part is already basic/preferred - no assembly fee savings available"

    if not search_results:
        return "no_search_results", f"No parts found matching '{primary_value}' in {subcategory}"

    if search_results and not compatible_results:
        return "none_compatible", f"Found {len(search_results)} parts but none meet compatibility requirements (same specs or better)"

    return "unknown", "No alternatives found"
```

Note: Unsupported categories are handled separately by `build_unsupported_response()` - they return `similar_parts` instead of `alternatives`.

### Step 9: Implementation Flow

```python
async def find_alternatives(lcsc, min_stock=100, same_package=True, library_type=None, limit=10, ...):
    # 1. Get original part
    original = await get_part(lcsc)
    if not original:
        return {"error": f"Part {lcsc} not found"}

    # 2. Check if category is supported
    subcategory = original.get("subcategory")
    rules = COMPATIBILITY_RULES.get(subcategory)
    is_supported = rules is not None

    # 3. Get primary spec for search query
    # For supported: use rules["primary"]
    # For unsupported: use first KEY_ATTRIBUTE as best guess
    if is_supported:
        primary_attr = rules["primary"]
    else:
        key_attrs = KEY_ATTRIBUTES.get(subcategory, [])
        primary_attr = key_attrs[0] if key_attrs else None

    primary_value = None
    if primary_attr:
        primary_value = original.get("specs", {}).get(primary_attr)

    # 4. Search with primary spec (fetch extra for filtering)
    # Always search all library types - scoring handles basic/preferred priority
    search_params = {
        "subcategory_id": original.get("subcategory_id"),
        "min_stock": min_stock,
        "limit": limit * 5,  # Fetch 5x extra, compatibility filtering removes many
        "library_type": "all",  # Don't filter here - let scoring prioritize
    }
    if primary_value:
        search_params["query"] = primary_value
    if same_package:
        search_params["package"] = original["package"]

    search_results = await search(**search_params)

    # 5. Exclude original part, verify primary spec matches
    verified = [
        p for p in search_results
        if p["lcsc"] != original["lcsc"]
        and (not primary_attr or verify_primary_spec_match(original, p, primary_attr))
    ]

    # 6. For SUPPORTED categories: filter to compatible alternatives
    # For UNSUPPORTED categories: skip compatibility filtering (we'll return as similar_parts)
    compatible = []
    verification_info_map = {}  # lcsc -> verification_info
    if is_supported:
        for p in verified:
            is_compat, verify_info = is_compatible_alternative(original, p, subcategory)
            if is_compat:
                compatible.append(p)
                verification_info_map[p["lcsc"]] = verify_info
    else:
        compatible = verified  # No filtering for unsupported
        # Empty verification info for unsupported categories
        for p in compatible:
            verification_info_map[p["lcsc"]] = {"specs_verified": [], "specs_unparseable": []}

    # 7. Score and rank
    min_price = min((p["price"] for p in compatible if p.get("price")), default=None)
    scored = []
    for part in compatible:
        score, breakdown = score_alternative(part, original, min_price)
        verify_info = verification_info_map[part["lcsc"]]
        scored.append((score, part, breakdown, verify_info))
    scored.sort(key=lambda x: -x[0])  # Highest score first

    # 8. Build response (different structure for supported vs unsupported)
    return build_response(original, scored, subcategory, primary_attr, primary_value, limit)
```

---

## Compatibility Rules Summary

### Passives

| Subcategory | Must Match Exactly | Same or Better |
|-------------|-------------------|----------------|
| **Resistors** (Chip, Through-hole) | Resistance | Tolerance (≤%), Power (≥W) |
| **Capacitors** (MLCC, Electrolytic, etc.) | Capacitance, Dielectric (X7R/X5R/C0G) | Voltage (≥V), Tolerance (≤%) |
| **Inductors** (SMD, Power) | Inductance | Current Rating (≥A), Saturation Current (≥A), DCR (≤Ω) |
| **Ferrite Beads** | Impedance @ Frequency | Current Rating (≥A), DCR (≤Ω) |

### Semiconductors - Discrete

| Subcategory | Must Match Exactly | Same or Better |
|-------------|-------------------|----------------|
| **MOSFETs** | - | Vds (≥V), Id (≥A), Rds(on) (≤Ω) |
| **BJTs** | Type (NPN/PNP) | Vceo (≥V), Ic (≥A), hFE (similar range) |
| **Schottky Diodes** | - | Vr (≥V), If (≥A), Vf (≤V preferred) |
| **Zener Diodes** | Zener Voltage (exact) | Power Dissipation (≥W) |
| **Switching Diodes** | - | Vr (≥V), If (≥A) |
| **TVS/ESD Protection** | Standoff Voltage (Vrwm) | Clamping Voltage (≤V), Peak Power (≥W) |

### Optoelectronics

| Subcategory | Must Match Exactly | Same or Better |
|-------------|-------------------|----------------|
| **LEDs** | Color | - |
| **Optocouplers** | - | Isolation Voltage (≥V), CTR (similar range) |

### Timing

| Subcategory | Must Match Exactly | Same or Better |
|-------------|-------------------|----------------|
| **Crystals** | Frequency, Load Capacitance | Frequency Stability (≤ppm) |
| **Crystal Oscillators** | Frequency, Output Type | Frequency Stability (≤ppm) |

### Power

| Subcategory | Must Match Exactly | Same or Better |
|-------------|-------------------|----------------|
| **LDO Regulators** | Output Voltage | Output Current (≥A), Dropout Voltage (≤V) |
| **DC-DC Converters** | Output Voltage, Topology | Output Current (≥A), Input Voltage Range (covers original) |

### Protection

| Subcategory | Must Match Exactly | Same or Better |
|-------------|-------------------|----------------|
| **Fuses** | Current Rating (exact!), Type (fast/slow) | Voltage Rating (≥V) |
| **Resettable Fuses (PTC)** | Hold Current, Trip Current | Voltage (≥V) |

### Switches

| Subcategory | Must Match Exactly | Same or Better |
|-------------|-------------------|----------------|
| **Tactile Switches** | Mounting Type | Voltage (≥V), Current (≥A) |
| **Toggle/Rocker/Slide Switches** | Circuit Config (SPST/SPDT/DPDT) | Voltage (≥V), Current (≥A) |

---

## Supported Subcategories

The following 120+ subcategories have compatibility rules defined. Parts in other subcategories will return `similar_parts` instead of verified `alternatives`.

### Passives
- Chip Resistor - Surface Mount
- Through Hole Resistors
- Current Sense Resistors / Shunt Resistors
- Resistor Networks, Arrays
- Potentiometers, Variable Resistors
- Multilayer Ceramic Capacitors MLCC - SMD/SMT
- Multilayer Ceramic Capacitors MLCC - Leaded
- Through Hole Ceramic Capacitors
- Aluminum Electrolytic Capacitors - SMD
- Aluminum Electrolytic Capacitors - Leaded
- Aluminum Electrolytic Capacitors (Can - Screw Terminals)
- Tantalum Capacitors
- Film Capacitors
- Polypropylene Film Capacitors (CBB)
- Polymer Aluminum Capacitors
- Hybrid Aluminum Electrolytic Capacitors
- Horn-Type Electrolytic Capacitors
- Niobium Oxide Capacitors
- Mica and PTFE Capacitors
- Safety Capacitors
- Capacitor Networks, Arrays
- Inductors (SMD)
- Power Inductors
- Color Ring Inductors / Through Hole Inductors
- Ferrite Beads
- Common Mode Filters
- Wireless Charging Coils

### Semiconductors - Discrete
- MOSFETs
- Silicon Carbide Field Effect Transistor (MOSFET)
- JFETs
- Bipolar (BJT)
- Darlington Transistors
- Digital Transistors
- IGBT Transistors / Modules
- Phototransistors
- Schottky Diodes
- Switching Diodes
- Zener Diodes
- Diodes - General Purpose
- Diodes - Rectifiers - Fast Recovery
- Fast Recovery / High Efficiency Diodes
- Bridge Rectifiers
- Super Barrier Rectifiers (SBR)
- Avalanche Diodes
- High Effic Rectifier
- SiC Diodes

### Protection
- ESD and Surge Protection (TVS/ESD)
- Varistors
- Gas Discharge Tube Arresters (GDT)
- Semiconductor Discharge Tubes (TSS)
- LED Protection
- Resettable Fuses
- Automotive Fuses
- Thermal Fuses (TCO)
- Disposable fuses
- NTC Thermistors
- PTC Thermistors

### Optoelectronics
- LED Indication - Discrete
- LED - High Brightness
- Infrared (IR) LEDs
- Ultraviolet LEDs (UVLED)
- Light Bars, Arrays
- Transistor, Photovoltaic Output Optoisolators
- Logic Output Optoisolators
- Triac, SCR Output Optoisolators
- Gate Drive Optocoupler
- Photointerrupters - Slot Type - Transistor Output
- Reflective Optical Interrupters
- Photoresistors

### Timing
- Crystals
- Crystal Oscillators
- Ceramic Resonators
- SAW Resonators
- Temperature Compensated Crystal Oscillators (TCXO)
- Voltage-Controlled Crystal Oscillators (VCXOs)
- Oven Controlled Crystal Oscillators (OCXOs)

### Power
- Voltage Regulators - Linear, Low Drop Out (LDO) Regulators
- Voltage Reference

### Digital Isolators
- Digital Isolators

### Switches
- Tactile Switches
- DIP Switches
- Slide Switches
- Toggle Switches
- Rocker Switches
- Pushbutton Switches
- Rotary Switches

### Relays
- Power Relays
- Signal Relays
- Automotive Relays
- Reed Relays
- Solid State Relays (MOS Output)
- Solid State Relays (Triac Output)

### Connectors
- Pin Headers
- Female Headers
- Screw Terminal Blocks
- Barrier Terminal Blocks
- Pluggable System Terminal Block
- USB Connectors
- HDMI Connectors
- DisplayPort (DP) Connector
- Audio Connectors
- Coaxial Connectors (RF)
- IDC Connectors
- Wire To Board Connector
- Circular Connectors & Cable Connectors
- XLR (Cannon) Connectors
- DIN41612 Connectors
- Shunts, Jumpers

### Audio
- Speakers
- Buzzers
- Microphones
- MEMS Microphones

### Misc
- Vibration Motors
- Rotary Encoders

### NOT Supported (returns `similar_parts` for manual verification)
- **ICs** (MCUs, op-amps, ADCs, etc.) - too complex, no simple equivalence
- **Modules** (WiFi, Bluetooth, GPS, etc.) - pinout, firmware, certification
- **Sensors** - too varied, application-specific
- **FFC/FPC Connectors** - mechanical fit too specific
- **Board-to-Board Connectors** - mating part dependencies
- **Card Edge Connectors** - mechanical compatibility

---

## Spec Parsing - Field Names

Based on KEY_ATTRIBUTES, here are the actual field names to parse:

```python
COMPATIBILITY_RULES = {
    # ============== RESISTORS ==============
    "Chip Resistor - Surface Mount": {
        "primary": "Resistance",
        "same_or_better": {
            "Tolerance": "lower",      # ±1% can replace ±5%
            "Power(Watts)": "higher",  # 1/4W can replace 1/10W
        }
    },
    "Through Hole Resistors": {
        "primary": "Resistance",
        "same_or_better": {
            "Tolerance": "lower",
            "Power(Watts)": "higher",
        }
    },

    # ============== CAPACITORS ==============
    "Multilayer Ceramic Capacitors MLCC - SMD/SMT": {
        "primary": "Capacitance",
        "must_match": ["Temperature Coefficient"],  # X7R != X5R
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        }
    },
    "Aluminum Electrolytic Capacitors - SMD": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            # Note: Electrolytic caps don't have "Tolerance" in specs
        }
    },
    "Aluminum Electrolytic Capacitors - Leaded": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        }
    },
    "Tantalum Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        }
    },

    # ============== INDUCTORS ==============
    "Inductors (SMD)": {
        "primary": "Inductance",
        "same_or_better": {
            "Current Rating": "higher",
            "Current - Saturation (Isat)": "higher",  # Note: space before parentheses
            "DC Resistance(DCR)": "lower",
        }
    },
    "Power Inductors": {
        "primary": "Inductance",
        "same_or_better": {
            "Current Rating": "higher",
            "Current - Saturation(Isat)": "higher",
            "DC Resistance(DCR)": "lower",
        }
    },
    "Color Ring Inductors / Through Hole Inductors": {
        "primary": "Inductance",
        "same_or_better": {
            "Current Rating": "higher",
            "DC Resistance(DCR)": "lower",
        }
    },

    # ============== FERRITE BEADS ==============
    "Ferrite Beads": {
        "primary": "Impedance @ Frequency",
        "same_or_better": {
            "Current Rating": "higher",
            "DC Resistance(DCR)": "lower",
        }
    },

    # ============== MOSFETs ==============
    "MOSFETs": {
        "primary": "Drain to Source Voltage",  # Search by Vds
        "same_or_better": {
            "Drain to Source Voltage": "higher",
            "Current - Continuous Drain(Id)": "higher",
            "RDS(on)": "lower",
        }
    },

    # ============== BJTs ==============
    "Bipolar (BJT)": {
        "primary": "type",  # NPN or PNP
        "must_match": ["type"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
            "Current - Collector(Ic)": "higher",
        }
    },

    # ============== DIODES ==============
    "Schottky Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
            "Voltage - Forward(Vf@If)": "lower",  # Lower Vf is better
        }
    },
    "Switching Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        }
    },
    "Zener Diodes": {
        "primary": "Zener Voltage(Nom)",
        "must_match": ["Zener Voltage(Nom)"],  # Must be exact
        "same_or_better": {
            "Pd - Power Dissipation": "higher",
        }
    },

    # ============== ESD/TVS ==============
    "ESD and Surge Protection (TVS/ESD)": {
        "primary": "Reverse Stand-Off Voltage (Vrwm)",
        "same_or_better": {
            "Clamping Voltage": "lower",
            "Peak Pulse Power": "higher",
        }
    },

    # ============== OPTOELECTRONICS ==============
    "LED Indication - Discrete": {
        "primary": "Illumination Color",
        "must_match": ["Illumination Color"],
    },
    "Transistor, Photovoltaic Output Optoisolators": {
        "primary": "Isolation Voltage(Vrms)",
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            # Note: CTR not checked - too application-specific
        }
    },

    # ============== TIMING ==============
    "Crystals": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Load Capacitance"],
        "same_or_better": {
            "Frequency Stability": "lower",  # ±10ppm better than ±20ppm
        }
    },
    "Crystal Oscillators": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],  # CMOS vs Clipped Sine etc
        "same_or_better": {
            "Frequency Stability": "lower",
        }
    },

    # ============== VOLTAGE REGULATORS ==============
    "Voltage Regulators - Linear, Low Drop Out (LDO) Regulators": {
        "primary": "Output Voltage",
        "must_match": ["Output Voltage"],
        "same_or_better": {
            "Output Current": "higher",
            "Voltage Dropout": "lower",
        }
    },

    # ============== FUSES ==============
    "Resettable Fuses": {
        "primary": "Hold Current",
        "must_match": ["Hold Current", "Trip Current"],  # Fuse ratings are exact!
        "same_or_better": {
            "Voltage - Max": "higher",
        }
    },

    # ============== MORE RESISTORS ==============
    "Current Sense Resistors / Shunt Resistors": {
        "primary": "Resistance",
        "same_or_better": {
            "Tolerance": "lower",
            "Power(Watts)": "higher",
        }
    },

    # ============== MORE CAPACITORS ==============
    "Multilayer Ceramic Capacitors MLCC - Leaded": {
        "primary": "Capacitance",
        "must_match": ["Temperature Coefficient"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        }
    },
    "Film Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        }
    },
    "Polypropylene Film Capacitors (CBB)": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        }
    },
    "Polymer Aluminum Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        }
    },
    "Hybrid Aluminum Electrolytic Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        }
    },

    # ============== MORE DIODES ==============
    "Diodes - General Purpose": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        }
    },
    "Bridge Rectifiers": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
            "Voltage - Forward(Vf@If)": "lower",
        }
    },
    "Diodes - Rectifiers - Fast Recovery": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Average Rectified": "higher",
        }
    },
    "Fast Recovery / High Efficiency Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        }
    },
    "Super Barrier Rectifiers (SBR)": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
            "Voltage - Forward(Vf@If)": "lower",
        }
    },

    # ============== MORE TRANSISTORS ==============
    "JFETs": {
        "primary": "FET Type",  # N-Channel or P-Channel
        "must_match": ["FET Type"],
        "same_or_better": {
            "Drain Current (Idss)": "higher",
            "RDS(on)": "lower",
        }
    },
    "IGBT Transistors / Modules": {
        "primary": "Collector-Emitter Breakdown Voltage (Vces)",
        "same_or_better": {
            "Collector-Emitter Breakdown Voltage (Vces)": "higher",
            "Current - Collector(Ic)": "higher",
            "Vce Saturation(VCE(sat))": "lower",
        }
    },

    # ============== MORE LEDS ==============
    "LED - High Brightness": {
        "primary": "Illumination Color",
        "must_match": ["Illumination Color"],
    },
    "Infrared (IR) LEDs": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],  # 850nm != 940nm
    },
    "Ultraviolet LEDs (UVLED)": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],  # UV wavelength matters
    },

    # ============== THERMISTORS ==============
    "NTC Thermistors": {
        "primary": "Resistance @ 25℃",
        "must_match": ["Resistance @ 25℃", "B Constant (25℃/100℃)"],
    },
    "PTC Thermistors": {
        "primary": "Resistance @ 25℃",
        "must_match": ["Resistance @ 25℃"],
    },

    # ============== PROTECTION ==============
    "Varistors": {
        "primary": "Varistor Voltage",
        "must_match": ["Varistor Voltage"],
        "same_or_better": {
            "Clamping Voltage": "lower",
            "Energy": "higher",
        }
    },

    # ============== VOLTAGE REFERENCES ==============
    "Voltage Reference": {
        "primary": "Output Voltage",
        "must_match": ["Output Voltage"],
        "same_or_better": {
            "Tolerance": "lower",
            "Temperature Coefficient": "lower",
        }
    },

    # ============== SWITCHES ==============
    "Tactile Switches": {
        "primary": "Mounting Type",
        "must_match": ["Mounting Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Contact Current": "higher",
        }
    },
    "DIP Switches": {
        "primary": "Number of Positions",
        "must_match": ["Number of Positions", "Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        }
    },
    "Slide Switches": {
        "primary": "Circuit",
        "must_match": ["Circuit", "Mounting Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        }
    },
    "Toggle Switches": {
        "primary": "Circuit",
        "must_match": ["Circuit"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
            "Current Rating": "higher",
        }
    },
    "Rocker Switches": {
        "primary": "Circuit",
        "must_match": ["Circuit"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
            "Current Rating": "higher",
        }
    },
    "Pushbutton Switches": {
        "primary": "Self Lock / No Lock",
        "must_match": ["Self Lock / No Lock"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Contact Current": "higher",
        }
    },
    "Rotary Switches": {
        "primary": "Positions",
        "must_match": ["Positions", "Number of Poles Per Deck"],
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
            "Current Rating": "higher",
        }
    },

    # ============== RELAYS ==============
    "Power Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],  # SPST, SPDT, DPDT etc
        "same_or_better": {
            "Contact Rating": "higher",
            "Switching Voltage(Max)": "higher",
        }
    },
    "Signal Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Contact Rating": "higher",
            "Switching Current(Max)": "higher",
        }
    },
    "Automotive Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Contact Rating": "higher",
            "Switching Voltage(Max)": "higher",
        }
    },
    "Reed Relays": {
        "primary": "Coil Voltage",
        "must_match": ["Coil Voltage", "Contact Form"],
        "same_or_better": {
            "Switching Voltage(Max)": "higher",
            "Switching Current(Max)": "higher",
        }
    },
    "Solid State Relays (MOS Output)": {
        "primary": "Load Voltage",
        "same_or_better": {
            "Load Voltage": "higher",
            "Load Current": "higher",
            "RDS(on)": "lower",
        }
    },
    "Solid State Relays (Triac Output)": {
        "primary": "Load Voltage",
        "must_match": ["Contact Form"],
        "same_or_better": {
            "Load Voltage": "higher",
            "Load Current": "higher",
        }
    },

    # ============== CONNECTORS (mechanical - exact matches) ==============
    "Pin Headers": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Number of Pins", "Number of Rows"],
        "same_or_better": {
            "Current Rating": "higher",
        }
    },
    "Female Headers": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Number of Positions", "Number of Rows"],
        "same_or_better": {
            "Current Rating": "higher",
        }
    },
    "Screw Terminal Blocks": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Number of Positions or Pins"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        }
    },
    "Barrier Terminal Blocks": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Pitch", "Number of Positions or Pins"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        }
    },
    "Pluggable System Terminal Block": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Pitch", "Number of Positions or Pins"],
        "same_or_better": {
            "Voltage Rating (Max)": "higher",
            "Current Rating": "higher",
        }
    },
    "USB Connectors": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Gender"],  # USB-A, USB-C, etc + Male/Female
    },

    # ============== MORE FUSES ==============
    "Automotive Fuses": {
        "primary": "Current Rating",
        "must_match": ["Current Rating", "Type"],  # Blade, mini, etc
        "same_or_better": {
            "Voltage Rating (DC)": "higher",
        }
    },
    "Thermal Fuses (TCO)": {
        "primary": "Rated Functioning Temperature",
        "must_match": ["Rated Functioning Temperature"],
        "same_or_better": {
            "Current Rating": "higher",
            "Voltage Rating": "higher",
        }
    },
    "Disposable fuses": {
        "primary": "Current Rating",
        "must_match": ["Current Rating", "Type"],
        "same_or_better": {
            "Voltage Rating (AC)": "higher",
        }
    },

    # ============== MORE TRANSISTORS ==============
    "Darlington Transistors": {
        "primary": "Type",
        "must_match": ["Type"],  # NPN or PNP
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
            "Current - Collector(Ic)": "higher",
        }
    },
    "Digital Transistors": {
        "primary": "type",
        "must_match": ["type"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
        }
    },
    "Phototransistors": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],
        "same_or_better": {
            "Collector - Emitter Voltage VCEO": "higher",
            "Current - Collector(Ic)": "higher",
        }
    },
    "Silicon Carbide Field Effect Transistor (MOSFET)": {
        "primary": "Drain to Source Voltage",
        "same_or_better": {
            "Drain to Source Voltage": "higher",
            "Current - Continuous Drain(Id)": "higher",
            "RDS(on)": "lower",
        }
    },

    # ============== MORE DIODES ==============
    "Avalanche Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        }
    },
    "High Effic Rectifier": {
        "primary": "Reverse Voltage",
        "same_or_better": {
            "Reverse Voltage": "higher",
            "Average Rectified Current": "higher",
        }
    },
    "SiC Diodes": {
        "primary": "Voltage - DC Reverse(Vr)",
        "same_or_better": {
            "Voltage - DC Reverse(Vr)": "higher",
            "Current - Rectified": "higher",
        }
    },

    # ============== MORE CAPACITORS ==============
    "Aluminum Electrolytic Capacitors (Can - Screw Terminals)": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        }
    },
    "Horn-Type Electrolytic Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
        }
    },
    "Niobium Oxide Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        }
    },
    "Mica and PTFE Capacitors": {
        "primary": "Capacitance",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        }
    },
    "Through Hole Ceramic Capacitors": {
        "primary": "Capacitance",
        "must_match": ["Temperature Coefficient"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Tolerance": "lower",
        }
    },
    "Safety Capacitors": {
        "primary": "Capacitance",
        "must_match": ["Ratings"],  # X1, X2, Y1, Y2 class
        "same_or_better": {
            "Voltage(AC)": "higher",
            "Tolerance": "lower",
        }
    },

    # ============== MORE TIMING ==============
    "Ceramic Resonators": {
        "primary": "Frequency",
        "must_match": ["Frequency"],
    },
    "SAW Resonators": {
        "primary": "Frequency",
        "must_match": ["Frequency"],
    },
    "Temperature Compensated Crystal Oscillators (TCXO)": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        }
    },
    "Voltage-Controlled Crystal Oscillators (VCXOs)": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        }
    },
    "Oven Controlled Crystal Oscillators (OCXOs)": {
        "primary": "Frequency",
        "must_match": ["Frequency", "Output Type"],
        "same_or_better": {
            "Frequency Stability": "lower",
        }
    },

    # ============== MORE OPTOCOUPLERS ==============
    "Logic Output Optoisolators": {
        "primary": "Isolation Voltage(Vrms)",
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            "Data Rate": "higher",
        }
    },
    "Triac, SCR Output Optoisolators": {
        "primary": "Load Voltage",
        "same_or_better": {
            "Load Voltage": "higher",
            "Load Current": "higher",
            "Isolation Voltage(Vrms)": "higher",
        }
    },
    "Gate Drive Optocoupler": {
        "primary": "Isolation Voltage(Vrms)",
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            "Output Current(Max)": "higher",
        }
    },

    # ============== DIGITAL ISOLATORS ==============
    "Digital Isolators": {
        "primary": "Number of Forward Channels",
        "must_match": ["Number of Forward Channels", "Number of Reverse Channels"],
        "same_or_better": {
            "Isolation Voltage(Vrms)": "higher",
            "Data Rate(Max)": "higher",
        }
    },

    # ============== PROTECTION ==============
    "Gas Discharge Tube Arresters (GDT)": {
        "primary": "Voltage - DC Spark Over",
        "must_match": ["Number of Poles"],
        "same_or_better": {
            "Impulse Discharge Current": "higher",
        }
    },
    "Semiconductor Discharge Tubes (TSS)": {
        "primary": "Peak off - state voltage(Vdrm)",
        "same_or_better": {
            "Peak Pulse Current-Ipp (10/1000us)": "higher",
        }
    },
    "LED Protection": {
        "primary": "Trigger Voltage",
        "must_match": ["Trigger Voltage"],
        "same_or_better": {
            "Hold Current": "higher",
        }
    },

    # ============== MORE CONNECTORS ==============
    "HDMI Connectors": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Gender"],
    },
    "DisplayPort (DP) Connector": {
        "primary": "Connector Type",
        "must_match": ["Connector Type"],
    },
    "Audio Connectors": {
        "primary": "Connector Type",
        "must_match": ["Connector Type"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        }
    },
    "Coaxial Connectors (RF)": {
        "primary": "Connector Type",
        "must_match": ["Connector Type", "Impedance"],
    },
    "IDC Connectors": {
        "primary": "Number of Positions or Pins",
        "must_match": ["Number of Positions or Pins", "Pitch"],
        "same_or_better": {
            "Current Rating": "higher",
        }
    },
    "Wire To Board Connector": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Pins Structure"],
        "same_or_better": {
            "Current Rating": "higher",
            "Voltage Rating": "higher",
        }
    },
    "Circular Connectors & Cable Connectors": {
        "primary": "Number of Pins",
        "must_match": ["Number of Pins", "Gender"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        }
    },
    "XLR (Cannon) Connectors": {
        "primary": "Number of Pins",
        "must_match": ["Number of Pins", "Gender"],
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        }
    },
    "DIN41612 Connectors": {
        "primary": "Number of Pins",
        "must_match": ["Pitch", "Number of Pins", "Number of Rows"],
        "same_or_better": {
            "Current Rating": "higher",
        }
    },

    # ============== ARRAYS/NETWORKS ==============
    "Resistor Networks, Arrays": {
        "primary": "Resistance",
        "must_match": ["Number of Resistors"],
        "same_or_better": {
            "Tolerance": "lower",
            "Power(Watts)": "higher",
        }
    },
    "Capacitor Networks, Arrays": {
        "primary": "Capacitance",
        "must_match": ["Number of Capacitors"],
        "same_or_better": {
            "Voltage Rating": "higher",
        }
    },

    # ============== FILTERS ==============
    "Common Mode Filters": {
        "primary": "Impedance @ Frequency",
        "must_match": ["Number of Lines"],
        "same_or_better": {
            "Current Rating": "higher",
            "Voltage Rating - DC": "higher",
        }
    },

    # ============== SPEAKERS/AUDIO ==============
    "Speakers": {
        "primary": "Impedance",
        "must_match": ["Impedance"],
        "same_or_better": {
            "Rated Power": "higher",
        }
    },
    "Buzzers": {
        "primary": "Voltage - Supply",
        "must_match": ["Driver Circuitry"],  # Active vs Passive
        "same_or_better": {
            "Sound Pressure Level": "higher",
        }
    },

    # ============== MISC ==============
    "Photoresistors": {
        "primary": "Cell Resistance @ Illuminance",
        "same_or_better": {
            "Voltage - Max": "higher",
        }
    },
    "Potentiometers, Variable Resistors": {
        "primary": "Resistance",
        "must_match": ["Number of Turns"],
        "same_or_better": {
            "Power(Watts)": "higher",
            "Tolerance": "lower",
        }
    },
    "Wireless Charging Coils": {
        "primary": "Inductance",
        "must_match": ["Number of Coils"],
        "same_or_better": {
            "DC Resistance(DCR)": "lower",
        }
    },

    # ============== MORE OPTO ==============
    "Photointerrupters - Slot Type - Transistor Output": {
        "primary": "Peak Wavelength",
        "must_match": ["Peak Wavelength"],
        "same_or_better": {
            "Load Voltage": "higher",
            "Output Current": "higher",
        }
    },
    "Reflective Optical Interrupters": {
        "primary": "Output Type",
        "must_match": ["Output Type"],
        "same_or_better": {
            "Current - Collector(Ic)": "higher",
        }
    },
    "Light Bars, Arrays": {
        "primary": "Color",
        "must_match": ["Color", "Number of Segments"],
    },

    # ============== MECHANICAL/MISC ==============
    "Shunts, Jumpers": {
        "primary": "Pitch",
        "must_match": ["Pitch", "Number of Positions"],
        "same_or_better": {
            "Current Rating": "higher",
        }
    },
    "Vibration Motors": {
        "primary": "Voltage Rating",
        "same_or_better": {
            "Voltage Rating": "higher",
            "Current Rating": "higher",
        }
    },
    "Rotary Encoders": {
        "primary": "Encoder Type",
        "must_match": ["Encoder Type"],
        "same_or_better": {
            "Rated Voltage (Max)": "higher",
            "Current Rating (Max)": "higher",
        }
    },
    "Microphones": {
        "primary": "Direction",
        "must_match": ["Direction"],
    },
    "MEMS Microphones": {
        "primary": "Output Type",
        "must_match": ["Output Type"],
    },
}
```

**Subcategory names must match KEY_ATTRIBUTES exactly.** The names above are based on actual API responses.

**If we can't parse a spec, we allow the part through** but show all specs so user can verify. This is safer than silently filtering based on bad parsing.

---

## Phase 1: Fix find_alternatives

### New File: `src/jlcpcb_mcp/alternatives.py`

Create a new module to keep `client.py` focused on API interaction:

- [ ] Define `COMPATIBILITY_RULES` dict
- [ ] Define `SPEC_PARSERS` mapping
- [ ] Implement spec parsers: `parse_voltage`, `parse_tolerance`, `parse_power`, `parse_current`, `parse_resistance`, `parse_capacitance`, `parse_inductance`, `parse_frequency`
- [ ] Implement `_values_match()` for must_match comparisons
- [ ] Implement `_spec_ok()` for same_or_better comparisons
- [ ] Implement `is_compatible_alternative()` using the rules dict
- [ ] Implement `verify_primary_spec_match()`
- [ ] Implement `score_alternative()`
- [ ] Implement `build_response()`
- [ ] Implement `get_no_alternatives_reason()`

### Update `client.py`

- [ ] Import `alternatives` module
- [ ] Modify `find_alternatives()` to:
  - [ ] Look up `COMPATIBILITY_RULES` for the subcategory
  - [ ] Extract primary spec value from `specs`
  - [ ] Add primary spec as `query` parameter to search
  - [ ] Fetch extra results (3x limit) for filtering
  - [ ] Call `verify_primary_spec_match()` on results
  - [ ] Call `is_compatible_alternative()` to filter
  - [ ] Call `score_alternative()` and sort
  - [ ] Call `build_response()` to format output

### Tests: `tests/test_alternatives.py`

- [ ] Unit tests for each parser function
- [ ] Unit tests for `_values_match()` and `_spec_ok()`
- [ ] Unit tests for `is_compatible_alternative()` with various subcategories
- [ ] Unit tests for `score_alternative()`
- [ ] Integration tests with real API calls

### Documentation

- [ ] Update CLAUDE.md with new behavior
- [ ] Document supported vs unsupported subcategories

### Test cases

```python
# 10kΩ ±1% resistor should only find ±1% or better alternatives
result = await client.find_alternatives("C25804")  # 10kΩ ±1%
for alt in result["alternatives"]:
    assert alt["specs"].get("Resistance") == "10kΩ"
    tol = parse_tolerance(alt["specs"].get("Tolerance"))
    assert tol is None or tol <= 1  # Same or better tolerance

# 25V capacitor should not suggest 16V or 6.3V alternatives
result = await client.find_alternatives("C12345")  # 100nF 25V
for alt in result["alternatives"]:
    voltage = parse_voltage(alt["specs"].get("Voltage Rating"))
    assert voltage is None or voltage >= 25

# Red LED should only find red LEDs
result = await client.find_alternatives("C2286")  # Red LED
for alt in result["alternatives"]:
    color = alt["specs"].get("Illumination Color", "").lower()
    assert "red" in color or color == ""

# X7R capacitor should not suggest X5R/Y5V alternatives
result = await client.find_alternatives("C1525")  # X7R cap
for alt in result["alternatives"]:
    tc = alt["specs"].get("Temperature Coefficient", "").upper()
    assert tc == "" or tc == "X7R"
```

---

## Phase 2: Enhance validate_bom (Future)

Once find_alternatives works properly, add optional suggestions to validate_bom:

```python
validate_bom(parts, board_qty=100, suggest_alternatives=True)
```

---

## Edge Cases

### Subcategories without KEY_ATTRIBUTES
Fall back to current behavior (subcategory-only search). Mark results as `"compatibility_checked": False`.

### ICs and complex components
No simple compatibility rules exist. Options:
- Don't suggest alternatives for ICs (safest)
- Match by model family prefix (e.g., "STM32F103" finds variants)
- Return results with `"compatibility_checked": False, "requires_manual_verification": True`

### Missing specs on original part
Fall back to subcategory search. Mark as `"compatibility_checked": False`.

### Unparseable spec values
If a spec can't be parsed (weird format), allow the part through but show specs for user verification. Log a warning for us to improve parsing.

---

## Why This Approach is Better

| Original Proposal | New Approach |
|-------------------|--------------|
| New `optimize_bom` tool | Fix existing `find_alternatives` |
| Trust search results blindly | Validate compatibility before suggesting |
| Risk suggesting bad parts | Only suggest verified-compatible alternatives |
| ~16 hours estimated | ~4-5 hours |
| Liability risk | Safe suggestions only |

The tool will only suggest parts that pass compatibility checks. If we can't verify compatibility, we either don't suggest or clearly mark it as requiring manual verification.
