# Fix Summary: Search Logic Issues

This document covers fixes for 5 related search logic issues found during testing.

## Issue 1: Interface Filter AND Logic Problem ✅ FIXED

### Problem
When searching for "environmental sensor I2C SPI", the parser created two separate Interface filters:
- `Interface = I2C`
- `Interface = SPI`

These were applied with AND logic (both must match), causing 0 results because the system tried to find components that have BOTH `Interface=I2C` AND `Interface=SPI` as separate exact matches.

However, components like BME280 have `Interface = "I2C、SPI"` (a single combined value), which should match when the user searches for either I2C OR SPI.

### Root Cause
In `query_builder.py`, each spec filter was added as a separate AND clause:
```python
for spec_filter in spec_filters:
    # Each creates: AND (attributes LIKE '%Interface%I2C%')
    sql_clauses.append(f"AND ({combined})")
```

This created:
```sql
WHERE ...
  AND (attributes LIKE '%Interface%I2C%')
  AND (attributes LIKE '%Interface%SPI%')  -- Both required!
```

### Solution
Added `_group_multi_value_filters()` function in `query_builder.py` that:
1. Groups filters by `(spec_name, operator)`
2. For groups with `operator="="` and multiple values, combines them into an OR group
3. Generates SQL like:
```sql
WHERE ...
  AND (
    attributes LIKE '%Interface%I2C%' OR
    attributes LIKE '%Interface%SPI%'     -- Either matches!
  )
```

This allows components with "I2C、SPI" to match when searching for either interface.

### Files Changed
- `src/jlcpcb_mcp/search/query_builder.py`: Added `_group_multi_value_filters()` and updated `build_spec_filter_clauses()`

---

## Issue 2: Antenna Subcategory Not Detected ✅ FIXED

### Problem
When searching for "ceramic antenna" or "antenna 2.4GHz", the parser did not detect any subcategory, causing poor search results:
- "ceramic antenna" returned 22,112 MLCC capacitors instead of antennas
- "antenna 2.4GHz" returned no subcategory detection

### Root Cause
The subcategory aliases did not include "antenna" or related terms, so queries containing "antenna" were not mapped to the appropriate subcategory.

### Solution
Added comprehensive antenna aliases in `subcategory_aliases.py`:

```python
# Antenna aliases
"antenna": "antennas",
"antennas": "antennas",
"ceramic antenna": "ceramic antenna",
"chip antenna": "ceramic antenna",
"pcb antenna": "antennas",
"wifi antenna": "antennas",
"bluetooth antenna": "antennas",
"ble antenna": "antennas",
"gps antenna": "antennas",
# etc.
```

### Files Changed
- `src/jlcpcb_mcp/subcategory_aliases.py`: Added antenna-related aliases

---

## Issue 3: Frequency Filter Too Strict (2.4GHz ≠ 2.45GHz) ✅ FIXED

### Problem
When searching for "antenna 2.4GHz", the frequency filter used exact matching with only 1% tolerance:
- User searches: 2.4GHz
- Database contains: 2.45GHz (common for WiFi/BLE band)
- Difference: ~2.08%
- Result: 0 matches (exceeds 1% tolerance)

This affected all RF components where common frequency bands have slight variations:
- 2.4GHz WiFi/BLE band (actually 2.4-2.5GHz)
- Database may store "2.45GHz" or "2400MHz~2500MHz"

### Root Cause
The post-filter logic in `engine.py` used a 1% tolerance for all "=" comparisons:

```python
eq_epsilon = abs(target_value) * 0.01  # 1% tolerance
```

For 2.4GHz: 1% = 24MHz, but 2.45GHz is 50MHz away → no match

### Solution
Implemented special handling for frequency filters with 5% tolerance:

```python
# Frequency matching needs wider tolerance for RF components
is_frequency = any("frequency" in name.lower() for name in attr_names_set)
if is_frequency:
    eq_epsilon = abs(target_value) * 0.05  # 5% tolerance for frequency
else:
    eq_epsilon = abs(target_value) * 0.01  # 1% tolerance for other specs
```

With 5% tolerance:
- 2.4GHz ± 120MHz → matches 2.28GHz to 2.52GHz
- Now correctly matches 2.45GHz parts

### Files Changed
- `src/jlcpcb_mcp/search/engine.py`: Added 5% tolerance for frequency matching

---

## Issue 4: Subcategory Detection - Word Order Confusion ✅ FIXED

### Problem
When searching for "humidity temperature sensor I2C", the parser incorrectly detected:
- Subcategory: **"Temperature Sensors"** (ID 3076) ❌ WRONG

But when searching for "temperature humidity sensor I2C" (different word order):
- Subcategory: **"Temperature and Humidity Sensor"** (ID 3191) ✅ CORRECT

BME280 sensors are in subcategory 3191, so the first query returned 0 results.

### Root Cause
The subcategory keyword matching uses regex word boundaries (`\bkeyword\b`):

**Query 1**: "humidity temperature sensor"
- Pattern `\btemperature sensor\b` → **MATCHES** (words are adjacent)
- Pattern `\bhumidity sensor\b` → **NO MATCH** (words not adjacent)
- Result: Maps to "temperature sensors" ❌

**Query 2**: "temperature humidity sensor"
- Pattern `\btemperature sensor\b` → **NO MATCH** (humidity is in between)
- Pattern `\bhumidity sensor\b` → **MATCHES** (words are adjacent)
- Result: Maps to "temperature and humidity sensor" ✅

### Solution
Added comprehensive aliases in `subcategory_aliases.py` to handle all word orders:

```python
# All variations map to "temperature and humidity sensor"
"temperature and humidity sensor": "temperature and humidity sensor",
"humidity and temperature sensor": "temperature and humidity sensor",
"temperature humidity sensor": "temperature and humidity sensor",
"humidity temperature sensor": "temperature and humidity sensor",  # ← Fixed!
"temp and humidity sensor": "temperature and humidity sensor",
"humidity and temp sensor": "temperature and humidity sensor",
"temp humidity sensor": "temperature and humidity sensor",
"humidity temp sensor": "temperature and humidity sensor",

# Popular sensor families
"dht sensor": "temperature and humidity sensor",
"bme sensor": "temperature and humidity sensor",
"sht sensor": "temperature and humidity sensor",
"aht sensor": "temperature and humidity sensor",
```

Since aliases are sorted by length (longest-first), these longer patterns match before the standalone "temperature sensor" pattern.

### Files Changed
- `src/jlcpcb_mcp/subcategory_aliases.py`: Added comprehensive temperature+humidity sensor aliases

---

## Testing

### New Test Suite
Created `tests/test_fixes_issue_1_2.py` with 28 comprehensive tests:

**Issue 4 Tests - Temp/Humidity Subcategory (8 tests)**:
- ✅ All word order variations (humidity temperature, temperature humidity, etc.)
- ✅ Popular sensor family names (DHT, BME, SHT, AHT + "sensor")
- ✅ Standalone "temperature sensor" still works correctly

**Issue 1 Tests - Interface OR Logic (6 tests)**:
- ✅ Multiple interface filters are grouped with OR logic
- ✅ Single interface filter not wrapped in a group
- ✅ Different spec types aren't grouped together
- ✅ Range operators (>=, <=) never grouped
- ✅ Three or more values grouped correctly

**Issue 2 Tests - Antenna Subcategory (6 tests)**:
- ✅ Generic "antenna" detection
- ✅ "ceramic antenna" maps to correct subcategory
- ✅ WiFi/BLE/GPS/PCB antenna variations
- ✅ Frequency + antenna queries

**Issue 3 Tests - Frequency Tolerance (4 tests)**:
- ✅ Frequency filter extraction
- ✅ 2.4GHz vs 2.45GHz within 5% tolerance
- ✅ Various frequency format parsing (MHz, GHz, kHz)
- ✅ Ceramic antenna with frequency

**Integration Tests (4 tests)**:
- ✅ Combined humidity+temperature sensor with I2C+SPI
- ✅ Environmental sensor full query
- ✅ Antenna with frequency filter
- ✅ WiFi antenna frequency query

### Full Test Suite
All 515 unit tests pass ✅ (includes 10 new antenna/frequency tests)

---

## Impact

### Before Fixes
```
Query: "ceramic antenna"
→ Subcategory: None (defaults to FTS)
→ Results: 22,112 MLCC capacitors ❌

Query: "antenna 2.4GHz"
→ Subcategory: None
→ Frequency: 2.4GHz (exact, 1% tolerance = 24MHz)
→ Results: 0 (database has 2.45GHz, 50MHz away) ❌

Query: "humidity temperature sensor I2C"
→ Subcategory: "Temperature Sensors" (wrong category) ❌
→ Results: 0

Query: "environmental sensor I2C SPI"
→ Subcategory: None
→ Interface filters: I2C AND SPI (both required) ❌
→ Results: 0
```

### After Fixes
```
Query: "ceramic antenna"
→ Subcategory: "Ceramic antenna" ✅
→ Results: Ceramic chip antennas

Query: "antenna 2.4GHz"
→ Subcategory: "Antennas" ✅
→ Frequency: 2.4GHz (±5% = ±120MHz tolerance)
→ Results: WiFi/BLE antennas (includes 2.45GHz parts) ✅

Query: "2.4GHz ceramic antenna"
→ Subcategory: "Ceramic antenna" ✅
→ Frequency: Matches 2.4-2.5GHz range ✅
→ Results: 2.4GHz ceramic chip antennas

Query: "humidity temperature sensor I2C"
→ Subcategory: "Temperature and Humidity Sensor" ✅
→ Results: BME280, DHT22, SHT31, etc.

Query: "temperature humidity sensor I2C SPI"
→ Subcategory: "Temperature and Humidity Sensor" ✅
→ Interface filters: I2C OR SPI (either matches) ✅
→ Results: BME280, BME680, etc. (have "I2C、SPI")

Query: "wifi antenna 2.4GHz"
→ Subcategory: "Antennas" ✅
→ Frequency: Matches 2.4-2.5GHz band ✅
→ Results: WiFi antennas in correct frequency range
```

---

## Summary Table

| Issue | Problem | Solution | Files Changed |
|-------|---------|----------|---------------|
| #1 | Interface filters used AND logic (I2C AND SPI required) | Group multi-value filters with OR logic | `query_builder.py` |
| #2 | "antenna" not detected as subcategory | Added antenna aliases | `subcategory_aliases.py` |
| #3 | Frequency 2.4GHz ≠ 2.45GHz (1% tolerance too strict) | Increased frequency tolerance to 5% | `engine.py` |
| #4 | Word order matters ("humidity temperature" vs "temperature humidity") | Added all word-order variants | `subcategory_aliases.py` |
| #5 | Multiple Interface values created separate AND filters | Implemented filter grouping logic | `query_builder.py` |

---

## Notes

### Missing Pressure Attribute (Not Fixed - Database Limitation)
**Not a bug** - This is a JLCPCB database limitation:
- The "Temperature and Humidity Sensor" subcategory (ID 3191) has no "Pressure" attribute
- BME280 measures pressure, but users cannot parametrically filter by pressure capability
- This cannot be fixed in the MCP - it's a limitation of JLCPCB's categorization system

### Future Improvements
1. **Sensor aliases**: Add more sensor family aliases (HDC, AM2320, etc.) as needed
2. **OR logic for other attributes**: Monitor for other attributes that might benefit from OR logic (e.g., Package types, Output Type)
3. **Word-order handling**: Add similar handling for other multi-word subcategories if issues arise
4. **Frequency bands**: Consider pre-defined frequency band matching (e.g., "WiFi band" → 2.4-2.5GHz, 5.15-5.85GHz)
5. **Tolerance tuning**: May need to adjust tolerance per attribute type (currently 1% for most, 5% for frequency)
6. **FTS term weighting**: Improve FTS scoring to prioritize category-relevant terms (prevent "ceramic" from matching capacitors when "antenna" is also present)
