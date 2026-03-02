# Sensor Scrapers — Reference

## Overview

14 scrapers in `scripts/scrapers/` produce per-source JSON files in `data/sensors/`. Each scraper extracts sensor IC metadata from a different source. Orchestrated by `scripts/scrape_sensors.py`.

**Stats:** 1,517 sensors in DB | 56 measure types | 7 platforms | 136 IC aliases

## Architecture

```
scripts/
  scrape_sensors.py          # CLI orchestrator (--source X to run one)
  scrapers/
    __init__.py              # SCRAPERS registry dict
    common.py                # Shared: normalize_sensor_id, infer_measures, MEASURE_KEYWORDS, etc.
    arduino.py               # Arduino Library Index (JSON API)
    esphome.py               # ESPHome components (git clone + Python AST)
    circuitpython.py         # CircuitPython drivers (HTML)
    micropython.py           # Awesome-MicroPython readme (Markdown)
    tasmota.py               # Tasmota Supported Peripherals (HTML table)
    zephyr.py                # Zephyr RTOS devicetree bindings (YAML, sparse git clone)
    sparkfun.py              # SparkFun Magento GraphQL API
    dfrobot.py               # DFRobot GitHub repos
    maxbotix.py              # MaxBotix Shopify JSON
    benewake.py              # Benewake product pages (HTML)
    hilink.py                # Hi-Link product pages (HTML)
    atlas_scientific.py      # Atlas Scientific WooCommerce (HTML)
    winsen.py                # Winsen product pages (HTML, ~400 pages, slow)
    bestmodules.py           # Best Modules Corp/Holtek sensor modules (HTML)

data/sensors/
  {source}.json              # Per-source output
  ic_aliases.json            # IC name equivalence table
```

## Sources

### Platform sources (add platform tags to ICs)

| Source | ICs | Platform tag | What it provides |
|---|---|---|---|
| Arduino Library Index | 642 | `arduino` | IC names, popularity, descriptions, manufacturer, GitHub URLs |
| ESPHome | 173 | `esphome` | Protocol (i2c/spi/uart), I2C addresses |
| CircuitPython | 115 | `circuitpython` | Adafruit driver URLs |
| MicroPython | 165 | `micropython` | GitHub URLs, category-based measures |
| Tasmota | 103 | `tasmota` | Protocol, similar to ESPHome |
| Zephyr RTOS | 214 | `zephyr` | Protocol, manufacturer (from devicetree vendor prefixes) |

### Manufacturer sources (unique sensors, no platform tag)

| Source | ICs | What it provides |
|---|---|---|
| Winsen | 377 | Gas/environmental sensors. Voltage, sensor_type, datasheet URLs, protocol |
| MaxBotix | 125 | Ultrasonic distance sensors. All measure `distance` + `ultrasonic` |
| Hi-Link | 36 | mmWave radar modules. Motion/distance/biometric |
| Benewake | 19 | LiDAR sensors. All measure `distance` + `lidar` |
| Atlas Scientific | 28 | Water quality (pH, ORP, DO, EC, RTD). Protocol (i2c/uart) |
| Best Modules Corp | 81 | Holtek sensor modules. Voltage, protocol, sensor_type, datasheet URLs |

### Breakout board sources (IC discovery, no platform tag)

| Source | ICs | What it provides |
|---|---|---|
| SparkFun | 119 | IC extraction from product names, protocol from Qwiic/descriptions |
| DFRobot | 82 | IC extraction from GitHub repo names (`DFRobot_{IC}`) |

## Output Schema

Each `{source}.json` has this structure:

```json
{
  "source": "arduino",
  "source_url": "https://...",
  "scraper_version": "1.0.0",
  "scraped_at": "2026-03-01T...",
  "stats": { "sensor_count": 642, ... },
  "sensors": [
    {
      "id": "bme280",           // required, [a-z0-9]+ only
      "name": "BME280",         // required, display name
      "measures": ["humidity", "pressure", "temperature"],  // required, sorted
      "platforms": ["arduino"],  // required (may be empty for manufacturer sources)
      "popularity": 45,         // optional (Arduino only — library count)
      "description": "...",     // optional, max 200 chars
      "protocol": ["i2c", "spi"],  // optional, sorted
      "i2c_address": ["0x76", "0x77"],  // optional
      "manufacturer": "Bosch",  // optional
      "datasheet_url": "...",   // optional
      "voltage": "1.8-3.6",    // optional
      "type": "ndir",          // optional (Winsen sensor technology)
      "urls": ["https://..."]  // optional, max 5-10
    }
  ]
}
```

Fields are sparse — only included when the source provides them. Different sources contribute different fields.

## Measure Types (56)

### Primary measures
temperature (348), gas (289), distance (228), acceleration (146), pressure (134), humidity (125), gyroscope (96), motion (81), light (72), magnetic_field (68), particulate (58), co2 (57), current (55), proximity (40), voltage (40), color (30), water_quality (27), touch (25), flow (24), biometric (23), co (23), ir_temperature (20), flame (19), oxygen (18), weight (15), sound (13), uv (13), rotation (12), gesture (10), gps (9)

### Sub-measures (coexist with parent)
| Sub-measure | Parent | Count | Example ICs |
|---|---|---|---|
| ultrasonic | distance | 144 | HC-SR04, MaxBotix MB series |
| radar | motion | 45 | Hi-Link LD series |
| voc | gas | 35 | SGP40, CCS811, BME680 |
| lidar | distance | 31 | Benewake TF series |
| pir | motion | 31 | Winsen PIR series |
| formaldehyde | gas | 22 | Winsen CH2O sensors |
| nh3 | gas | 17 | Winsen ammonia sensors |
| tof | distance | 13 | VL53L0x, TMF88xx |
| ozone | gas | 13 | Winsen O3 sensors |
| h2s | gas | 10 | Winsen H2S sensors |

### Other measures
wind (7), soil_moisture (5), moisture (5), tilt (5), rain (4), dissolved_oxygen (4), orp (4), ph (4), radiation (3), force (3), optical (3), conductivity (3), weather (2), face_recognition (2), level (2), vibration (1)

## Key Utilities (common.py)

- **`normalize_sensor_id(raw)`** — Strips vendor prefixes (adafruit_, sparkfun_, etc.), suffixes (_library, _sensor, etc.), non-alphanumeric chars. Returns `[a-z0-9]+` or None.
- **`has_ic_pattern(s)`** — True if string has both letters and digits and len >= 3.
- **`infer_measures(text)`** — Keyword matching with word boundaries and morphological suffixes. Returns sorted measure list.
- **`make_sensor_entry(...)`** — Builds standardized entry dict (sparse — only includes non-empty fields).
- **`write_source_json(...)`** — Writes per-source JSON with metadata envelope.
- **`extract_manufacturer(text)`** — Pattern-matches manufacturer names from descriptions.
- **`MEASURE_KEYWORDS`** — Dict mapping measure type → keyword list. Used by `infer_measures`.

## Running

```bash
# All scrapers
.venv/bin/python -m scripts.scrape_sensors

# Single source
.venv/bin/python -m scripts.scrape_sensors --source arduino

# Winsen is slow (~10 min, crawls ~400 pages)
```

## Adding a New Scraper

1. Create `scripts/scrapers/{name}.py` with a `scrape_{name}(output_dir: Path)` function
2. Use `common.py` utilities: `normalize_sensor_id`, `has_ic_pattern`, `infer_measures`, `make_sensor_entry`, `write_source_json`
3. Register in `scripts/scrapers/__init__.py` (import + add to `SCRAPERS` dict)
4. Use `wafer` for all HTTP (per CLAUDE.md rules)
5. For known ICs, add `KNOWN_IC_MEASURES` dict to override text inference
6. IDs must be `[a-z0-9]+` only, max ~15 chars for IC-based sources

## Build Pipeline

Scraped JSONs are merged into `data/sensor.db` by `scripts/build_sensor_db.py`:

```bash
.venv/bin/python scripts/build_sensor_db.py [--data-dir data/] [--output data/sensor.db] [--quiet]
```

Merge pipeline: load sources in priority order → alias resolution → union multi-value fields → enrich manufacturers/types/voltages/protocols → build SQLite with FTS5.

Runtime module: `src/pcbparts_mcp/sensor_db/` exposes `sensor_recommend` MCP tool.
