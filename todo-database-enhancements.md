# Database Enhancement TODO

Bugs and improvements discovered during testing.

---

## Critical Bugs

### Spec Filter Pagination Bug

**Status:** ✅ DONE (2026-01-27)
**Priority:** High
**Discovered:** Notecarrier-A BOM testing (2026-01-27)
**Fixed:** Implemented Option A - SQL value patterns in `generate_value_patterns()` function

**Problem**: `spec_filters=[SpecFilter("Resistance", "=", "82k")]` returns 0 results even though 82k resistors exist.

**Root Cause Analysis**:
1. SQL only checks if attribute NAME exists: `AND (attributes LIKE '%"Resistance"%')`
2. This matches ALL 13,095 resistors with any Resistance attribute
3. Results sorted by stock (high→low): 10k, 1M, 1k, 100Ω come first
4. `fetch_limit = min(limit * 10, 500)` - with `limit=3`, we only fetch 30 rows
5. 82k resistors appear at position 115 in stock-sorted results
6. Post-filter never sees them → returns 0 results

**Evidence**:
```
limit=  3 → fetch_limit= 30 → returned=0
limit= 10 → fetch_limit=100 → returned=0
limit= 20 → fetch_limit=200 → returned=1
limit= 50 → fetch_limit=500 → returned=2
```

**Fix Options**:

| Option | Query Time | Accuracy | Effort |
|--------|-----------|----------|--------|
| A. SQL value patterns | ~5ms | 99%+ | Low |
| B. Two-phase query | ~500ms | 100% | Medium |
| C. Indexed columns | ~1ms | 100% | High (schema change) |

**Recommended Fix: Option A (SQL value patterns)**

Generate SQL LIKE patterns that match the actual value, not just the attribute name:

```python
def generate_value_patterns(spec_name: str, value: str) -> list[str]:
    """Generate SQL LIKE patterns for spec value matching.

    For Resistance="82k", generates:
    - '%"Resistance", "82k%'   (matches "82kΩ", "82kohm")
    - '%"Resistance", "82K%'   (case variant)
    - '%"Resistance", "82000%' (raw ohms)
    """
    parser = SPEC_PARSERS.get(spec_name)
    parsed = parser(value) if parser else None
    if parsed is None:
        return []

    patterns = []
    if spec_name == "Resistance":
        ohms = parsed
        if ohms >= 1_000_000:
            m_val = int(ohms / 1_000_000)
            patterns.append(f'%"{spec_name}", "{m_val}M%')
            patterns.append(f'%"{spec_name}", "{m_val}m%')
        if ohms >= 1_000:
            k_val = int(ohms / 1_000)
            patterns.append(f'%"{spec_name}", "{k_val}k%')
            patterns.append(f'%"{spec_name}", "{k_val}K%')
        patterns.append(f'%"{spec_name}", "{int(ohms)}%')

    # Similar logic for Capacitance (uF/nF/pF), Inductance (uH/nH/mH), etc.
    return patterns
```

Then in `search()`, replace:
```python
# OLD (broken):
sql_parts.append("AND (attributes LIKE '%\"Resistance\"%')")

# NEW (fixed):
patterns = generate_value_patterns("Resistance", "82k")
or_clauses = " OR ".join([f"attributes LIKE '{p}' ESCAPE '\\'" for p in patterns])
sql_parts.append(f"AND ({or_clauses})")
```

**Test case**: After fix, this should return 2 results:
```python
db.search(subcategory_name="resistor", package="0402",
          spec_filters=[SpecFilter("Resistance", "=", "82k")], limit=3)
```

---

## Schema Enhancement: Pre-Parsed Numeric Columns

**Status:** ✅ DONE (2026-01-27)
**Priority:** High
**Breaking Changes:** OK (single user)
**Fixed:** Added 45 numeric columns with parsers in `build_database.py`, indexed for efficient parametric search

### Problem

SQLite stores specs as JSON strings like `"1.5V~2.5V"`. Can't do `WHERE vgs_th < 2.0` because it's not a number.

Current workaround is broken:
1. SQL narrows with `LIKE '%"Vgs(th)"%'` (just checks attribute exists, not value)
2. Fetches 10x requested limit (up to 500 rows)
3. Parses each row's spec value in Python
4. Filters in Python → misses results that exist but weren't fetched

### Schema Changes

Based on actual JLCPCB attribute analysis (100 samples per category):

```sql
-- Universal (high coverage across categories)
ALTER TABLE components ADD COLUMN voltage_max_v REAL;        -- caps, MOSFETs, diodes, connectors
ALTER TABLE components ADD COLUMN current_max_a REAL;        -- inductors, diodes, LEDs, connectors
ALTER TABLE components ADD COLUMN power_w REAL;              -- resistors, LEDs, transistors
ALTER TABLE components ADD COLUMN tolerance_pct REAL;        -- R, C, L
ALTER TABLE components ADD COLUMN temp_min_c REAL;           -- everything (767/1200 samples)
ALTER TABLE components ADD COLUMN temp_max_c REAL;           -- everything

-- Passives
ALTER TABLE components ADD COLUMN resistance_ohms REAL;      -- resistors (100%)
ALTER TABLE components ADD COLUMN capacitance_f REAL;        -- capacitors (100%)
ALTER TABLE components ADD COLUMN inductance_h REAL;         -- inductors (100%)
ALTER TABLE components ADD COLUMN dcr_ohms REAL;             -- inductors (100%)
ALTER TABLE components ADD COLUMN isat_a REAL;               -- inductors (94%)
ALTER TABLE components ADD COLUMN irms_a REAL;               -- inductors

-- MOSFETs (all 100% coverage)
ALTER TABLE components ADD COLUMN vds_max_v REAL;            -- Drain to Source Voltage
ALTER TABLE components ADD COLUMN vgs_th_min_v REAL;         -- Gate Threshold (min)
ALTER TABLE components ADD COLUMN vgs_th_max_v REAL;         -- Gate Threshold (max)
ALTER TABLE components ADD COLUMN id_max_a REAL;             -- Continuous Drain Current
ALTER TABLE components ADD COLUMN rds_on_ohms REAL;          -- RDS(on)
ALTER TABLE components ADD COLUMN qg_nc REAL;                -- Gate Charge
ALTER TABLE components ADD COLUMN ciss_pf REAL;              -- Input Capacitance

-- Diodes
ALTER TABLE components ADD COLUMN vf_v REAL;                 -- Forward Voltage (100%)
ALTER TABLE components ADD COLUMN vr_max_v REAL;             -- Reverse Voltage (100%)
ALTER TABLE components ADD COLUMN if_max_a REAL;             -- Rectified Current (100%)

-- Voltage Regulators (LDO, DC-DC)
ALTER TABLE components ADD COLUMN vout_v REAL;               -- Output Voltage (100%)
ALTER TABLE components ADD COLUMN iout_max_a REAL;           -- Output Current (100%)
ALTER TABLE components ADD COLUMN vdropout_v REAL;           -- Dropout Voltage (100%)
ALTER TABLE components ADD COLUMN vin_min_v REAL;            -- Input Voltage min
ALTER TABLE components ADD COLUMN vin_max_v REAL;            -- Input Voltage max

-- RF / Frequency
ALTER TABLE components ADD COLUMN freq_min_hz REAL;          -- RF, crystals, oscillators (95-99%)
ALTER TABLE components ADD COLUMN freq_max_hz REAL;          -- RF, op-amps, oscillators, connectors
ALTER TABLE components ADD COLUMN output_power_dbm REAL;     -- RF transmitters (81%)
ALTER TABLE components ADD COLUMN sensitivity_dbm REAL;      -- RF receivers (76%)
ALTER TABLE components ADD COLUMN data_rate_bps REAL;        -- RF transceivers (80%)

-- LNA / RF Amplifier specific (37-46 occurrences in samples)
ALTER TABLE components ADD COLUMN noise_figure_db REAL;      -- LNA, RF amps (100% coverage)
ALTER TABLE components ADD COLUMN gain_db REAL;              -- LNA, RF amps, antennas (100%)
ALTER TABLE components ADD COLUMN p1db_dbm REAL;             -- RF amps - 1dB compression (81%)
ALTER TABLE components ADD COLUMN ip3_dbm REAL;              -- RF amps - 3rd order intercept (51%)

-- ADC/DAC
ALTER TABLE components ADD COLUMN resolution_bits INTEGER;   -- ADCs, DACs (100%)
ALTER TABLE components ADD COLUMN sample_rate_hz REAL;       -- ADCs, DACs (97%)
ALTER TABLE components ADD COLUMN num_channels INTEGER;      -- ADCs, DACs (100%)

-- Crystals / Oscillators
ALTER TABLE components ADD COLUMN load_capacitance_pf REAL;  -- Crystals (99%)
ALTER TABLE components ADD COLUMN freq_tolerance_ppm REAL;   -- Crystals (96%)
ALTER TABLE components ADD COLUMN esr_ohms REAL;             -- Crystals

-- Connectors
ALTER TABLE components ADD COLUMN num_pins INTEGER;          -- Connectors (100%)
ALTER TABLE components ADD COLUMN pitch_mm REAL;             -- Connectors (100%)
ALTER TABLE components ADD COLUMN num_rows INTEGER;          -- Connectors (100%)

-- LEDs
ALTER TABLE components ADD COLUMN wavelength_nm REAL;        -- LEDs (78%)
ALTER TABLE components ADD COLUMN luminous_intensity_mcd REAL; -- LEDs (76%)
ALTER TABLE components ADD COLUMN forward_current_ma REAL;   -- LEDs (83%)

-- Op-Amps
ALTER TABLE components ADD COLUMN gbw_hz REAL;               -- Gain Bandwidth Product (3934)
ALTER TABLE components ADD COLUMN slew_rate_vus REAL;        -- Slew Rate V/µs (4106)
ALTER TABLE components ADD COLUMN vos_uv REAL;               -- Input Offset Voltage (4930)
ALTER TABLE components ADD COLUMN ib_na REAL;                -- Input Bias Current (4899)
ALTER TABLE components ADD COLUMN cmrr_db REAL;              -- Common Mode Rejection Ratio (4548)
ALTER TABLE components ADD COLUMN noise_nv_rthz REAL;        -- Noise Density nV/√Hz (3849)
ALTER TABLE components ADD COLUMN num_amps INTEGER;          -- Number of Channels/Amps (4784)

-- Capacitors (electrolytic-specific)
ALTER TABLE components ADD COLUMN ripple_current_a REAL;     -- Ripple Current (9952)
ALTER TABLE components ADD COLUMN esr_ohms REAL;             -- ESR (9269) - also crystals
ALTER TABLE components ADD COLUMN lifetime_hours REAL;       -- Lifetime at temp (11519)

-- Power / Efficiency
ALTER TABLE components ADD COLUMN iq_ua REAL;                -- Quiescent Current (4112)
ALTER TABLE components ADD COLUMN efficiency_pct REAL;       -- Efficiency % (156)

-- Audio / RF
ALTER TABLE components ADD COLUMN impedance_ohms REAL;       -- Speakers, antennas (183)
ALTER TABLE components ADD COLUMN bandwidth_hz REAL;         -- Amplifiers, filters (282)

-- Indexes for common queries
CREATE INDEX idx_resistance ON components(resistance_ohms) WHERE resistance_ohms IS NOT NULL;
CREATE INDEX idx_capacitance ON components(capacitance_f) WHERE capacitance_f IS NOT NULL;
CREATE INDEX idx_inductance ON components(inductance_h) WHERE inductance_h IS NOT NULL;
CREATE INDEX idx_voltage_max ON components(voltage_max_v) WHERE voltage_max_v IS NOT NULL;
CREATE INDEX idx_current_max ON components(current_max_a) WHERE current_max_a IS NOT NULL;
CREATE INDEX idx_vds ON components(vds_max_v) WHERE vds_max_v IS NOT NULL;
CREATE INDEX idx_rds_on ON components(rds_on_ohms) WHERE rds_on_ohms IS NOT NULL;
CREATE INDEX idx_freq_max ON components(freq_max_hz) WHERE freq_max_hz IS NOT NULL;
CREATE INDEX idx_resolution ON components(resolution_bits) WHERE resolution_bits IS NOT NULL;
CREATE INDEX idx_num_pins ON components(num_pins) WHERE num_pins IS NOT NULL;
CREATE INDEX idx_ripple_current ON components(ripple_current_a) WHERE ripple_current_a IS NOT NULL;
CREATE INDEX idx_esr ON components(esr_ohms) WHERE esr_ohms IS NOT NULL;
CREATE INDEX idx_iq ON components(iq_ua) WHERE iq_ua IS NOT NULL;
CREATE INDEX idx_gbw ON components(gbw_hz) WHERE gbw_hz IS NOT NULL;
```

**Total: ~59 columns** covering resistors, capacitors, inductors, MOSFETs, diodes, regulators, RF, ADC/DAC, crystals, connectors, LEDs, and op-amps.

### Attribute → Column Mapping

| JLCPCB Attribute | Column |
|------------------|--------|
| `Resistance` | `resistance_ohms` |
| `Capacitance` | `capacitance_f` |
| `Inductance` | `inductance_h` |
| `Voltage Rating` | `voltage_max_v` |
| `Voltage - Supply` | `voltage_max_v` |
| `Current Rating` | `current_max_a` |
| `Current - Saturation(Isat)` | `isat_a` |
| `DC Resistance(DCR)` | `dcr_ohms` |
| `Drain to Source Voltage` | `vds_max_v` |
| `Gate Threshold Voltage (Vgs(th))` | `vgs_th_min_v`, `vgs_th_max_v` |
| `Current - Continuous Drain(Id)` | `id_max_a` |
| `RDS(on)` | `rds_on_ohms` |
| `Voltage - Forward(Vf@If)` | `vf_v` |
| `Voltage - DC Reverse(Vr)` | `vr_max_v` |
| `Current - Rectified` | `if_max_a` |
| `Output Voltage` | `vout_v` |
| `Output Current` | `iout_max_a` |
| `Voltage Dropout` | `vdropout_v` |
| `Frequency` / `Frequency Range` | `freq_min_hz`, `freq_max_hz` |
| `Resolution(Bits)` | `resolution_bits` |
| `Sampling Rate` | `sample_rate_hz` |
| `Load Capacitance` | `load_capacitance_pf` |
| `Number of Pins` | `num_pins` |
| `Pitch` | `pitch_mm` |
| `Ripple Current` | `ripple_current_a` |
| `Equivalent Series Resistance(ESR)` | `esr_ohms` |
| `Lifetime` | `lifetime_hours` |
| `Quiescent Current` / `Quiescent Current(Iq)` | `iq_ua` |
| `Common Mode Rejection Ratio(CMRR)` | `cmrr_db` |
| `Noise density(eN)` | `noise_nv_rthz` |
| `Number of Channels` | `num_amps` / `num_channels` |
| `Efficiency` | `efficiency_pct` |
| `Impedance` | `impedance_ohms` |
| `Bandwidth` | `bandwidth_hz` |
| `Noise Figure` | `noise_figure_db` |
| `Gain` | `gain_db` |
| `P1dB` | `p1db_dbm` |
| `IP3` | `ip3_dbm` |

### Implementation Notes

1. Parse during scrape using extended `SPEC_PARSERS`
2. Handle ranges: `"1.5V~2.5V"` → `min=1.5, max=2.5`
3. Handle units: `"82kΩ"` → `82000`, `"10uF"` → `0.00001`
4. Keep JSON `attributes` column for display and edge cases
5. Query: use SQL `WHERE` for indexed columns, accurate counts

### Benefits

- Parametric search that actually works
- Queries like `WHERE resistance_ohms = 82000 AND tolerance_pct <= 1`
- Queries like `WHERE freq_max_hz > 10e9` (find mmWave parts)
- Accurate result counts
- No over-fetching hack

### Impact: Needle-in-Haystack Problem

Current part counts make keyword search useless for parametric needs:

| Category | Parts | Problem |
|----------|-------|---------|
| Resistors | 67,043 | Finding 82kΩ 1% among 67K parts |
| Capacitors | 40,933 | Finding low-ESR cap for SMPS |
| Inductors | 29,153 | Finding 10µH with 5A saturation |
| MOSFETs | 18,024 | Finding low Rds(on) for motor driver |
| LDOs | 8,866 | Finding <10µA quiescent for battery |
| Crystals | 7,872 | Finding specific load capacitance |

### Search Scenarios: Before vs After

**Low-ESR cap for SMPS:**
- Before: Search "capacitor low ESR" → random results
- After: `WHERE capacitance_f = 10e-6 AND esr_ohms < 0.1 AND voltage_max_v >= 25`

**Low-power LDO for battery:**
- Before: Search "LDO 3.3V" → 500+ parts, can't filter Iq
- After: `WHERE vout_v = 3.3 AND iq_ua < 10 AND iout_max_a >= 0.1`

**Precision op-amp:**
- Before: Search "precision op amp" → keyword only
- After: `WHERE vos_uv < 100 AND ib_na < 10 AND gbw_hz >= 1e6`

**MOSFET for motor:**
- Before: Search "N-channel 30V" → can't filter Rds(on)
- After: `WHERE vds_max_v >= 30 AND id_max_a >= 10 AND rds_on_ohms < 0.01`

**High-current inductor:**
- Before: Search "10uH inductor" → returns 1.3A parts
- After: `WHERE inductance_h = 10e-6 AND isat_a >= 5 AND dcr_ohms < 0.05`

**mmWave RF:**
- Before: Search "24GHz" → false positives from "2.4GHz"
- After: `WHERE freq_max_hz >= 24e9`

---

## Testing Results

### RD-Detector Parts Audit (2026-01-27)

#### FOUND - Working Well

| Component | LCSC | Status | Notes |
|-----------|------|--------|-------|
| nRF52840 BLE chip | C190794 | **FOUND** | 5 variants, good stock |
| CC2652P BLE/Zigbee | C1852232 | **FOUND** | 3 variants |
| ESP32 WiFi/BLE | C2913202 | **FOUND** | 93 variants! |
| RTL8812BRH WiFi | C2830109 | **FOUND** | Low stock (168) |
| LNA (2.4GHz) | C42432110 | **FOUND** | Multiple options |
| RF Power Detector | C208240 | **FOUND** | ADL5501, 20 options |
| RF Mixers | - | **FOUND** | 7 parts in subcategory |
| SMA Connectors | C496549 | **FOUND** | Many options |
| IPEX/U.FL | C2987682 | **FOUND** | 480K+ stock |

#### NOT FOUND - Analysis & Search Improvements

| Component | Verified Query | Exists in DB? | Can We Improve Search? |
|-----------|---------------|---------------|------------------------|
| RTL2832U SDR chip | `RTL2832`, `RTL2832U` | **NO** | N/A - genuinely not stocked |
| R820T/R820T2 tuner | `R820T`, `R820T2` | **NO** | N/A - genuinely not stocked |
| CC2400 (Ubertooth) | `CC2400` | **NO** | N/A - genuinely not stocked |
| AR9271 WiFi | `AR9271` | **NO** | N/A - genuinely not stocked |
| Ka-band LNA (30+ GHz) | `33GHz`, `35GHz` | **NO** (false positives) | See FTS bug below |
| mmWave (60GHz) | `60GHz` | **YES** - C2871887 | YES - see "High-Freq RF" improvement |
| Waveguide parts | `waveguide` | **NO** | N/A - not a PCB component |
| 24GHz radar | `24GHz`, `BGT24` | **PARTIAL** - C534093 | YES - see "High-Freq RF" improvement |

**Search Improvements Identified:**

1. **High-Frequency RF Parts Exist But Hard to Find**
   - C2871887: 60-64GHz radar transceiver IC (RF Transceiver ICs subcategory)
   - C50176497: 10-35GHz RF switch
   - C534093: 24GHz NPN transistor
   - **Improvement**: Add `frequency_hz` numeric column to enable `frequency > 10e9` queries

2. **SDR-Specific Parts (genuinely unavailable)**
   - RTL2832U, R820T, CC2400, AR9271 are niche/EOL parts
   - These cannot be found because JLCPCB doesn't stock them
   - Alternatives: Use ESP32-S2/S3 for WiFi sniffing, nRF52840 for BLE

#### PARTIALLY FOUND - Our Search Could Be Better

| Component | Issue | Improvement Needed |
|-----------|-------|-------------------|
| High-freq RF amps | Found 28 parts mentioning 6+ GHz but can't filter by frequency | Add frequency range to searchable specs |
| SMA connector freq | Frequency spec shows "N/A" for all | Extract frequency rating to key_specs |
| LNA specs | Noise figure/gain not in search results | Extract to key_specs from attributes |

### Notecarrier-A BOM Testing (2026-01-27)

**Coverage**: 81.5% (22/27 component types found)

| Category | Basic/Preferred | Extended Only |
|----------|-----------------|---------------|
| Capacitors | 5/5 | 0 |
| Resistors | 3/5 | 0 |
| Inductors | 1/2 | 1 |
| MOSFETs | 0 | 1/1 |
| Diodes/TVS | 3/3 | 0 |
| ICs | 0 | 3/3 |
| Connectors | 0 | 5/7 |

---

## Other Bugs

### FTS5 Numeric Tokenization Bug

**Status:** TODO
**Priority:** Medium

**Problem**: Searching for `35GHz` returns parts with `2.35GHz` in the description.

**Root Cause**: FTS5 tokenizes decimal numbers incorrectly:
- `2.35GHz` becomes tokens: `["2", "35", "ghz"]`
- Query `35GHz` matches because `35` and `ghz` are present

**Evidence**:
```python
db.search(query="35GHz", min_stock=0)  # Returns:
# C18221151: "2.35GHz 25@250MHz 30nH..."  ← FALSE POSITIVE (2.35 GHz, not 35 GHz)
# C7501981: "2.35GHz 50Ω SMD-5P..."       ← FALSE POSITIVE
# C50176497: "10GHz~35GHz 2.5V..."        ← TRUE POSITIVE (actually 35 GHz)
```

**Fix Options**:
1. **Phrase matching**: Use `"35GHz"` as exact phrase (won't match `2.35GHz`)
2. **Pre-parse frequencies**: Extract numeric frequency values during scrape (see Schema Enhancement)

**Recommended**: Option 2 - solved by adding `freq_min_hz`, `freq_max_hz` columns.

---

### Key Specs Not Extracted to Search Results
- **LNA chips**: `Noise Figure`, `Gain`, `P1dB` → ✅ FIXED by schema columns
- **RF Amplifiers/Mixers/Detectors**: `Frequency Range` → ✅ FIXED by freq_min/max_hz
- **Crystals**: `Load Capacitance` → ✅ FIXED by load_capacitance_pf

### Inductor Current Rating Not Searchable
- **Problem**: "2.2uH 3A" search returns 1.3A inductors
- → ✅ FIXED by `isat_a` column

### Search Query Parsing Issues
1. ✅ **"470R" notation** - ~~Doesn't parse correctly~~ FIXED: European notation support added
2. ✅ **"0R" jumper resistors** - ~~Search for "0R jumper" returns 0 results~~ FIXED: 0R parses to 0Ω
3. **"M.2 key E"** - FTS5 tokenization splits "M.2" incorrectly - **TODO**

### Connector Alias Mapping ~~Missing~~ ✅ FIXED
- ~~**U.FL/IPEX/MHF** are the same connector but different names~~
- ✅ All now return 281 results via `expand_query_synonyms()`

### MOSFET Spec Extraction Wrong Field
- **AO3420 search** - specs like `Vds` showed as "60pF" (pulled wrong attribute)
- MOSFET attribute aliases may be mapping to wrong fields
- → ⚠️ Need to verify attribute→column mapping during schema implementation

### Attribute Value Normalization
- Frequency specs have inconsistent formats: "2.4GHz~2.4835GHz" vs "2.4GHz" vs "DC~6GHz"
- → ✅ FIXED by parsing to numeric `freq_min_hz`, `freq_max_hz` during scrape

### Natural Language Parsing Gaps
- Query "ADC 10-bit 40MSPS" returned 0 results
- → ✅ FIXED by `resolution_bits`, `sample_rate_hz` columns

---

## Feature Requests

### High Priority

1. ✅ **Pre-parsed numeric columns** (see Schema Enhancement section above)
   - ~67 columns covering all major component types (expanded from initial 45)
   - Enables true parametric search: `WHERE resistance_ohms = 82000`
   - Fixes: spec_filter bug, frequency search, inductor current, LNA specs, etc.
   - **DONE 2026-01-27**
   - **EXPANDED 2026-01-27**: Added IoT/hobby-focused columns:
     - MCU: `flash_size_bytes` (2,006 parts), `ram_size_bytes` (1,413), `clock_speed_hz` (1,938)
     - TVS/ESD: `clamping_voltage_v` (21,014), `standoff_voltage_v` (19,496), `surge_power_w` (14,014)
     - Battery chargers: `charge_current_a` (696)
     - Memory ICs: `memory_capacity_bits` (1,501)
     - LEDs: `wavelength_nm` (3,392), `luminous_intensity_mcd` (3,059), `forward_current_ma` (1,635)
     - MOSFETs: `ciss_pf` (16,056)
     - Universal: `temp_min_c`, `temp_max_c` (253,287 parts each)
     - Power: `efficiency_pct` (151)

### Medium Priority

2. ✅ **European resistance notation** - "470R" → 470Ω, "4k7" → 4.7kΩ, "4R7" → 4.7Ω
   - Added `RESISTANCE_EURO_PATTERN` in db.py and alternatives.py
   - **DONE 2026-01-27**

3. ✅ **Connector alias mapping** - U.FL = IPEX = MHF = I-PEX
   - Added `expand_query_synonyms()` in db.py
   - **DONE 2026-01-27**

4. ✅ **"0R" jumper resistor alias** - "0R" should find 0Ω resistors
   - Handled by European notation fix (0R parses to 0Ω)
   - **DONE 2026-01-27**

5. **"M.2 key E" tokenization** - FTS splits "M.2" incorrectly
   - Could use phrase matching or token mapping
   - **TODO**
