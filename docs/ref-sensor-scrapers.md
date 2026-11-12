# Sensor Scrapers — Reference

## Overview

14 scrapers in `scripts/scrapers/` produce per-source JSON files in `data/sensors/`. Each scraper extracts sensor IC metadata from a different source. Orchestrated by `scripts/scrape_sensors.py`.

**Counts vary with source snapshots.** Use `sensor_recommend` filter discovery for current measures and platforms; static per-measure counts below are historical, not current coverage.

## Architecture

```
scripts/
  scrape_sensors.py          # CLI orchestrator (--source X to run one)
  scrapers/
    __init__.py              # SCRAPERS registry dict
    common.py                # Shared: normalize_sensor_id, infer_measures, MEASURE_KEYWORDS, etc.
    arduino.py               # Arduino Library Index (JSON API)
    esphome.py               # ESPHome components (git clone + Python AST)
    circuitpython.py         # CircuitPython drivers (drivers.rst from GitHub)
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
  curated.json               # Reviewed field corrections, never written by scrapers
```

## Sources

### Platform sources (add platform tags to ICs)

| Source | ICs | Platform tag | What it provides |
|---|---|---|---|
| Arduino Library Index | 642 | `arduino` | IC names, popularity, descriptions, manufacturer, GitHub URLs |
| ESPHome | 224 | `esphome` | Protocol (i2c/spi/uart/one_wire, ble for BLE devices), I2C addresses. Clones `dev`; each link is the component's page on esphome.io, else next.esphome.io (merged for the next release), else its source on GitHub, found by listing the esphome.io docs repo |
| CircuitPython | 126 | `circuitpython` | Adafruit driver URLs. Reads `docs/drivers.rst` from the Adafruit bundle on GitHub, not docs.circuitpython.org: Read the Docs gives GitHub Actions runners a Cloudflare challenge (HTTP 429) |
| MicroPython | 165 | `micropython` | GitHub URLs, category-based measures |
| Tasmota | 103 | `tasmota` | Protocol, similar to ESPHome |
| Zephyr RTOS | 214 | `zephyr` | Protocol, manufacturer (from devicetree vendor prefixes) |

### Manufacturer sources (unique sensors, no platform tag)

| Source | ICs | What it provides |
|---|---|---|
| Winsen | 377 | Gas/environmental sensors. Voltage, sensor_type, datasheet URLs, protocol |
| MaxBotix | 125 | Ultrasonic distance sensors. All measure `distance` + `ultrasonic` |
| Hi-Link | 36 | mmWave radar modules. Motion/distance/biometric |
| Benewake | 19 | LiDAR sensors. All measure `distance` + `lidar`. Interfaces per model from the product menu's Interface row (I/O = `gpio`) |
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
  "stats": { "sensor_count": 642, "kept_missing": 1, ... },
  "missed_scrapes": { "bmp085": 1 },  // carried-over sensors: scrapes in a row that missed each
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

Measures describe the part's own sensing channels. ADC applications, external
transducers, host-supplied compensation inputs and calculated outputs do not add
physical measures. "IMU", "6-axis" and "9-DoF" are not measure keywords (they gave
magnetometers a gyroscope); `infer_measures` uses them only as a fallback, giving acceleration and
gyroscope when the text names no inertial or magnetic channel, and nine-axis wording always adds a
gyroscope to a named accelerometer.
Keep parent/sub-measure pairs such as distance/lidar and motion/radar where applicable.
CO2, particulate and power-monitor tags alone do not establish NDIR, laser or shunt
technology; type inference requires a device lookup or explicit mechanism text.
Atlas probe connections are distinct from their reader circuits. MaxBotix outputs
are model-specific (including I2C, USB and analog/serial variants), rather than a
manufacturer-wide analog/PWM/UART default.

### Curated field corrections

`data/sensors/curated.json` is an object keyed by **canonical merged record ID**.
Use it for individual, verified corrections; fix a scraper or general build rule
when the cause affects a class of records. Each corrected field has its own
`value`, `evidence`, and `review_date` (`YYYY-MM-DD`):

```json
{
  "ads1293": {
    "voltage": {
      "value": "2.7-5.5",
      "evidence": {
        "url": "https://www.ti.com/lit/ds/symlink/ads1293.pdf",
        "page": 4,
        "text": "Recommended Operating Conditions: analog supply VDD, 2.7 to 5.5 V"
      },
      "review_date": "2026-11-10"
    }
  }
}
```

Supported fields are `name`, `description` (up to 200 characters), `manufacturer`,
`type`, `voltage`, `datasheet_url`, `measures`, `protocols`, and `exclude`.
`measures` and `protocols` values are exact arrays, including `[]` to clear them;
they replace the scraped unions and any legacy additions/removals. Nullable
scalars (`manufacturer`, `type`, `voltage`, `datasheet_url`) accept `null` to clear
an incorrect value. Voltages use the existing DB string format in volts without
a unit suffix, including ranges such as `"2.4-2.6"`; `sensor_recommend` returns
that string unchanged. It currently has no supply-voltage input filter or range
parser. `exclude` takes a boolean and also requires a nonempty
`reason` alongside its evidence and review date.

Evidence must contain a source `url`, a `document` and positive `page`, or a
scraper `source` path and the supporting `text`. Include the relevant passage
and datasheet page when available; preserve scraped text in the correction so
its evidence survives later scrapes. Evidence is reviewed by a person, not
re-fetched during a build.

The builder validates the complete file, then applies corrections **after all
scrape merging, aliases and legacy enrichment tables**. Every curated field wins
unconditionally for that field only; other fields retain the existing behavior.
In particular, the description length guard cannot block a curated description,
and insertion-time measure rules cannot change a curated exact set. Excluded
records are removed after validation. A reviewed `exclude: true` entry may remain
after its source record disappears, so a later scrape cannot resurrect it. Other
unknown/stale IDs, missing evidence,
invalid review date, unsupported field or malformed value fails the build before
the existing database is replaced. A standalone data directory without this
optional file retains the legacy build behavior.

Voltage reviews retain the source passage, record identity, other supply rails
and the resolution rule in each curated field. Passive elements have no VDD and
use `null`; heater voltage, noise density, resistance and absolute limits are not
operating supplies. Nominal tolerances become intervals, conflicting maker
statements use their safe intersection, and unresolved identities/disjoint
variants retain their previous values without a verified voltage override.
Superseded entries are removed from `VOLTAGE_TABLE`.

The Winsen and Best Modules voltage extractors require an explicit supply label
and a volt unit (including a separate table unit column). They preserve voltage
tolerances, reject noise/bias/heater rows and upper bounds, and do not turn
discrete supply options into a continuous interval.

### Record identity and driver support

IDs identify physical parts, modules or explicitly named device families. Library
vendor prefixes (including joined names such as `MyLD2410` and `7SemiBME68x`)
are removed during scraping and building; complete model suffixes and family
wildcards are preserved. `ic_aliases.json` merges verified same-device wrappers
and misspellings into existing canonical IDs and also resolves their old display
names at query time. Decisions and source passages live in `ic_alias_evidence.json`.
Concrete models are not merged into families just because they share a driver.
Explicit alias targets take precedence over prefix stripping, preserving published
IDs for genuine manufacturer modules such as `7semico2th` and `hlkfm22x`.

Names use a complete model token matching the canonical ID, with source punctuation
when available. A shared three-character prefix or a library's shortest title is
insufficient. Reviewed exceptions, including legacy Winsen URL slugs whose current
title and Model row identify another designation, use per-record curated names.
The Winsen scraper requires title/Model agreement before trusting such a designation;
it preserves the prior ID convention for client compatibility.

`support_transfers.json` records evidence-backed multi-device driver relationships.
Before curated exclusions, the builder copies only platform tags, driver URLs and
source provenance to the specified physical parts. It never copies wrapper measures,
descriptions or electrical fields. Targets containing only an `id` refer to existing
parts; complete target metadata can introduce a verified part missing from all other
sources (for example a GNSS receiver explicitly named in a library's product links).
This keeps BSEC, RVC and generic PM2.5 software out of the part catalog without losing
their platform support. LSM303 accelerometer support applies to both AGR and DLHC;
the similarly named `lsm303dlh-mag` driver explicitly targets DLHC, not DLH.

Rebuild as Docker does with
`uv run python scripts/build_sensor_db.py --data-dir data --output data/sensor.db --quiet`.
Verify corrections with
`uv run pytest tests/test_sensor_merge.py tests/test_sensor_db.py tests/test_sensor_recommend.py -q`.
The repository excludes integration-marked tests by default; to also exercise
the local `sensor.db` integration tests, run
`uv run pytest tests/test_sensor_recommend.py -q -m integration` (these sensor
tests query the local database without calling the deployed MCP).

`write_source_json()` (common.py) keeps sensors that drop out of a scrape. A sensor in the previous `{source}.json` that this scrape didn't find is written again, unchanged, after the fresh ones, and `missed_scrapes` counts how many scrapes in a row have missed it. The third miss in a row (`REMOVE_AFTER_MISSED_SCRAPES`) drops it, and a sensor that comes back is written as scraped with its count cleared. New sensors are added straight away. A missed sensor whose own pages all answer 404 or 410 (a deleted driver repo) is dropped at once instead. The reason for carrying the rest is that sources flicker: on 2026-11-01 the Best Modules listing left out its five HT7M21xx modules for one run while their product pages were still up.

`stats.sensor_count` is still the number the scrape found, so the deploy gate still fails a source that finds nothing, while its last data stays in place. `stats.kept_missing` counts the carried sensors, and the scrape log names each one. A rerun within 20 hours of the last scrape (`SAME_SCRAPE_HOURS`: a re-dispatched job, a local run) is the same monthly scrape, so a sensor it misses again keeps its count. An old ID that today's `normalize_sensor_id()` maps to an ID this scrape found (Tasmota's hlkld2410 is ld2410) is a rename, not a miss, and isn't carried. Any other ID scheme change still carries the old IDs for two more scrapes, so delete `{source}.json` before that run.

## Measure Types (historical snapshot)

### Primary measures

Counts in this section predate the current merge corrections. `eco2` is now a separate tag for CCS811; plain `co2` tags on other families still need individual source audits.
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
uv run python -m scripts.scrape_sensors

# Single source
uv run python -m scripts.scrape_sensors --source arduino

# Winsen is slow (~25 min, ~400 pages from 30 category listings; a listing gets 60s with 20s tries,
# failed listings are retried once, and discovery stops after 15 min)
```

Each run writes `data/sensors/_scrape_status.json` (gitignored) recording per-source
success/failure — a scraper that raises, or returns without (re)writing its output file,
is marked failed. In CI, `scripts/check_scrape_status.py` reads it after the data commit
and fails the workflow if any registered source failed, left stale data, produced zero
sensors, or logged more than 5 errors. Note this blocks only the sensor workflow's own
deploy trigger (a loud alarm to fix the source): the committed data still ships on the
next deploy from the daily components workflow, where the only backstop is
`build_sensor_db.py`'s `MIN_SENSOR_COUNT` floor.

## Adding a New Scraper

1. Create `scripts/scrapers/{name}.py` with a `scrape_{name}(output_dir: Path)` function
2. Use `common.py` utilities: `normalize_sensor_id`, `has_ic_pattern`, `infer_measures`, `make_sensor_entry`, `write_source_json`
3. Register in `scripts/scrapers/__init__.py` (import + add to `SCRAPERS` dict)
4. Use `wafer` for all HTTP (per CLAUDE.md rules). Always pair a `timeout=` with an
   `attempt_timeout=` — pass `attempt_cap(total)` on one-shot `wafer.get`/`wafer.post`
   calls, or build the session with `make_session(request_timeout)`. wafer's `timeout`
   is a TOTAL budget across all retries and rotations, not a per-attempt cap, so
   without this one hanging request burns the whole budget, `max_retries` never fires,
   and the source hard-fails and gates the deploy (maxbotix, 2026-08-01)
5. For known ICs, add `KNOWN_IC_MEASURES` dict to override text inference
6. IDs must be `[a-z0-9]+` only, max ~15 chars for IC-based sources
7. The scraper must write `{key}.json` on every successful run (even if content is
   unchanged) — `scrape_sensors.py` treats a run that leaves the file untouched as a
   failure, and the CI gate checks `scraped_at` freshness and `stats.sensor_count > 0`

## Build Pipeline

Scraped JSONs are merged into `data/sensor.db` by `scripts/build_sensor_db.py`:

```bash
uv run python scripts/build_sensor_db.py [--data-dir data/] [--output data/sensor.db] [--quiet]
```

Merge pipeline: load sources in priority order → alias resolution → union multi-value fields → enrich manufacturers/types/voltages/protocols → build SQLite with FTS5.

The build refuses to produce a `sensor.db` with fewer than `MIN_SENSOR_COUNT` (1200)
sensors (guards the deploy path against a truncated dataset) and builds atomically via
`.db.tmp` + rename — a failed or interrupted build leaves the old DB in place.

Runtime module: `src/pcbparts_mcp/sensor_db/` exposes `sensor_recommend` MCP tool.

### Reviewed merge corrections (0.8.23)

Generic MCU/platform IDs such as RP2040 are excluded from physical sensor recommendations.
Description selection first prefers hardware facts over software prose (libraries, drivers,
wrappers, examples and APIs), then ranks device/integration sources above aggregated library
descriptions and breakout prose; length breaks ties within that authority. Generic breakout
marketing cannot displace a useful IC title. `scripts/build_sensor_db.py` shares guarded
software-prefix cleanup between the build and Arduino/MicroPython/DFRobot scrapers. These scrapers
mark cleaned titles with optional `description_is_library_title: true` so removing a prefix
does not promote the text's rank after the next scrape. Zephyr binding instructions are cut
at instruction/code boundaries, preserving preceding hardware sentences. The build applies
the same rules to existing source JSON. Curated corrections still win last. Source URLs remain available.
CCS811's `eco2` output is estimated, humidity/temperature are compensation inputs, and its
reviewed operating supply is 1.8–3.3 V (3.6 V absolute maximum). The runtime reply cites ams
CCS811 v1-06, pages 1/5/6. These corrections do not establish the accuracy of every merged
family: further capability/identity audits remain pending.

### Catalog audit corrections (0.9.0)

An audit of 80 records against maker sources found these general causes, fixed at the source:

- Arduino: a Deneyap board-library title ("Deneyap Temperature&Humidity, Barometer Sensor SHT4X")
  describes the whole board, so it supplies a chip's measures and description only when no other
  library describes that chip (`chip_texts()`).
- Winsen: every output the spec and summary tables name is kept, including rowspan continuation
  rows (ZH08 "UART_TTL Output" + "PWMOutput"). Voltage spans, DAC, millivolt and 4-20 mA outputs
  are `analog`, IIC/I²C `i2c`, a case-sensitive CAN `can`, high/low-level outputs `gpio`. LIN has
  no tag. A part whose page names no output but specifies a bare element's signal (µA/ppm, mV or a
  sensing resistance Rs) is `analog`. Rows whose symbol cell is VH are heater rows whatever their
  label. PbS/PbSe photoconductive flame cells are `photoresistor`, not pyroelectric. For a Winsen
  part whose page names its outputs, the build's legacy `IC_PROTOCOLS` guesses no longer add a bus.
  An "Output method:" item in the product's own Features list joins the table outputs (MH-711A:
  UART beside the table's IIC); related-product cards further down the page are not read. A
  "Thermopile Gas Sensor" (RTGA71) is an NDIR detector, not `ir_temperature`.
- Benewake: protocols come from the product menu's Interface row; the build's former blanket
  UART+I2C default is gone (TF02-i and TFmini-i are CAN/RS-485, TFA170-L RS-232, Horn Ethernet).
- MaxBotix: products with a detection/proximity zone output also measure `proximity`.
- SparkFun: a UART named in the product summary is a protocol; a load cell's "pressure (force)"
  is not a pressure measure.
- Build: a thermopile reporting temperature also measures `ir_temperature`; descriptions longer
  than the column end at their last complete sentence (else a whole word plus "...") instead of
  mid-word; brand names inside URLs are not stripped.
