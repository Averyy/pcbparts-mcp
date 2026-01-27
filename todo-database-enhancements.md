# Database Enhancement TODO

Bugs and improvements discovered during testing.

---

## Critical Bugs

### Spec Filter Pagination Bug

**Status:** TODO
**Priority:** High
**Discovered:** Notecarrier-A BOM testing (2026-01-27)

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

**Status:** TODO (deploy current version first)
**Breaking Changes:** OK (single user)

### Problem

SQLite stores specs as JSON strings like `"1.5V~2.5V"`. Can't do `WHERE vgs_th < 2.0` because it's not a number.

Current workaround:
1. SQL narrows with `LIKE '%"Vgs(th)"%'` (just checks attribute exists)
2. Fetches 10x requested limit (up to 500 rows)
3. Parses each row's spec value in Python
4. Filters in Python: `if parsed_value < target_value`
5. Returns first N matches

Issues:
- Wastes memory/CPU parsing rows that get thrown away
- If fewer than N of fetched rows match, returns fewer results than actually exist
- Can't get accurate total counts for parametric queries

### Schema Changes

```sql
ALTER TABLE components ADD COLUMN resistance_ohms REAL;
ALTER TABLE components ADD COLUMN capacitance_f REAL;
ALTER TABLE components ADD COLUMN inductance_h REAL;
ALTER TABLE components ADD COLUMN voltage_v REAL;
ALTER TABLE components ADD COLUMN voltage_min_v REAL;
ALTER TABLE components ADD COLUMN voltage_max_v REAL;
ALTER TABLE components ADD COLUMN current_a REAL;
ALTER TABLE components ADD COLUMN power_w REAL;
ALTER TABLE components ADD COLUMN tolerance_pct REAL;
ALTER TABLE components ADD COLUMN vgs_th_min_v REAL;
ALTER TABLE components ADD COLUMN vgs_th_max_v REAL;
ALTER TABLE components ADD COLUMN vds_max_v REAL;
ALTER TABLE components ADD COLUMN id_max_a REAL;
ALTER TABLE components ADD COLUMN rds_on_ohms REAL;
ALTER TABLE components ADD COLUMN vf_v REAL;
ALTER TABLE components ADD COLUMN vr_max_v REAL;
ALTER TABLE components ADD COLUMN if_max_a REAL;

CREATE INDEX idx_resistance ON components(resistance_ohms) WHERE resistance_ohms IS NOT NULL;
CREATE INDEX idx_capacitance ON components(capacitance_f) WHERE capacitance_f IS NOT NULL;
-- etc for each column
```

### Work Estimate

| Task | Time |
|------|------|
| Schema change | ~2 hours |
| Scraper update (parse during scrape) | ~3 hours |
| Query logic (SQL instead of Python) | ~2 hours |
| Migration/rebuild | ~1 hour |
| **Total** | **~8 hours** |

### Implementation Notes

1. Reuse `SPEC_PARSERS` from `alternatives.py` for unit parsing
2. Extract min/max from ranges: `"1.5V~2.5V"` → `min=1.5, max=2.5`
3. Keep JSON `attributes` column for display and non-indexed specs
4. Query logic: use SQL `WHERE` for indexed specs, fall back to Python for others

### Benefits

- 10x faster parametric queries
- Accurate result counts
- No over-fetching
- Simpler query code

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
2. **Pre-parse frequencies**: Extract numeric frequency values during scrape
3. **Custom tokenizer**: Configure FTS5 to keep decimals together

**Recommended**: Option 2 (pre-parse) since we need frequency filtering anyway.

---

### Key Specs Not Extracted to Search Results
- **LNA chips**: `Noise Figure`, `Gain`, `P1dB` exist in get_part() but don't appear in search key_specs
  - Example: C42432110 (MLNA0622G) - full specs in detail view, empty in search
- **RF Amplifiers/Mixers/Detectors**: `Frequency Range` not in key_specs
- **Crystals**: `Load Capacitance` shows as N/A in search results
  - Data exists in attributes, just not extracted to key_specs

### Inductor Current Rating Not Searchable
- **Problem**: "2.2uH 3A" search returns 1.3A inductors
- **Cause**: Current rating (`Isat`, `Irms`) not extracted or not filterable
- **Fix needed**: Add `Current - Saturation(Isat)` to spec filters for inductors

### Search Query Parsing Issues
1. **"470R" notation** - Doesn't parse correctly, need to support "470R" = "470Ω"
2. **"0R" jumper resistors** - Search for "0R jumper" returns 0 results, need alias
3. **"M.2 key E"** - FTS5 tokenization splits "M.2" incorrectly

### Connector Alias Mapping Missing
- **U.FL/IPEX/MHF** are the same connector but different names
  - `query='U.FL'` finds 11, `query='IPEX'` finds different results
  - Need alias mapping: U.FL = IPEX = MHF = I-PEX

### MOSFET Spec Extraction Wrong Field
- **AO3420 search** - specs like `Vds` showed as "60pF" (pulled wrong attribute)
- MOSFET attribute aliases may be mapping to wrong fields

### Attribute Value Normalization
- Frequency specs have inconsistent formats that break filtering:
  - "2.4GHz~2.4835GHz" vs "2.4GHz" vs "DC~6GHz"
  - Range queries don't work across these formats

### Natural Language Parsing Gaps
- Query "ADC 10-bit 40MSPS" returned 0 results
  - Should parse resolution (10-bit) and sample rate (40MSPS) as specs
- Could add smart parsing for ADC/DAC specs similar to how we do resistors/capacitors

---

## Feature Requests

### High Priority (enables new use cases)

1. **Frequency range filter** for RF components
   - Extract `frequency_min_hz`, `frequency_max_hz` from descriptions
   - Enable queries like `frequency_max > 10e9` for mmWave parts
   - Would properly surface C2871887 (60GHz), C50176497 (35GHz switch)

2. **Pre-parsed numeric columns** (see Schema Enhancement section)
   - Resistance, capacitance, inductance, voltage, current
   - Enables true parametric search without over-fetching

### Medium Priority (improves existing search)

3. **Inductor current rating filter** - extract Isat/Irms
4. **Crystal load capacitance filter** - extract from attributes
5. **European resistance notation** - support "470R", "4k7", "4R7"
6. **Connector alias mapping** - U.FL = IPEX = MHF = I-PEX

### Low Priority (nice to have)

7. **ADC/DAC parametric search** - parse resolution (bits) and sample rate
8. **LNA key specs** - extract noise figure, gain, P1dB to search results
9. **RF amp key specs** - extract frequency range to search results
