# PCB Parts MCP Server

MCP server that gives Claude, Cursor, and other AI coding assistants electronic component data from JLCPCB, Mouser, and DigiKey: parametric search over 630K+ in-stock JLCPCB parts, live stock and pricing on all three, KiCad footprints, reference boards, sensor picks, and design rules. No API key required.

**Website:** [pcbparts.dev](https://pcbparts.dev)

## Features

- **Three distributors:** search JLCPCB, and look up live price and stock for specific parts on Mouser and DigiKey
- **Parametric search:** Filter by electrical specs (Vgs(th) < 2V, Rds(on) < 10mΩ, etc.)
- **Smart query parsing:** "10k 0603 1%" auto-parses into structured filters
- **Find alternatives:** Spec-aware compatibility checking for 120+ component types
- **KiCad footprints:** Download symbols and footprints via SamacSys
- **Pinout data:** Component pin information from EasyEDA symbols
- **MPN lookup:** Find JLCPCB equivalents by manufacturer part number
- **Sensor recommendation:** Find sensor ICs by what they measure, protocol, or platform (1,600+ sensors, 56 measure types)
- **Reference boards:** Search ~285 OSHW board schematics, IC neighborhoods, cross-board consensus for design patterns
- **Design rules:** 41 curated PCB design reference files covering power, protection, interfaces, MCUs, layout, and EMC
- **14 MCP tools**
- No API key required for JLCPCB (Mouser/DigiKey optional)

## Quick Start

### Claude Code

```bash
claude mcp add -s user --transport http pcbparts https://pcbparts.dev/mcp
```

Optional — auto-approve all pcbparts tools in `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["mcp__pcbparts__*"]
  }
}
```

### Claude Desktop

Add via Settings → Connectors → "Add custom connector", or add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pcbparts": {
      "type": "http",
      "url": "https://pcbparts.dev/mcp"
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "pcbparts": {
      "type": "http",
      "url": "https://pcbparts.dev/mcp"
    }
  }
}
```

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "pcbparts": {
      "type": "http",
      "url": "https://pcbparts.dev/mcp"
    }
  }
}
```

### Copilot for Xcode

Add to Extensions config:

```json
{
  "mcpServers": {
    "pcbparts": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://pcbparts.dev/mcp"]
    }
  }
}
```

## Available Tools

Typical workflow: `get_design_rules` / `board_search` + `board_get(focus=IC)` → `jlc_search` → `jlc_get_part` (datasheet, footprint) → `jlc_find_alternatives` → `cse_get_kicad` (KiCad files).

Tool descriptions include reply-field guidance: `relaxed` names omitted query words, a query-only library preference or a dropped part type; `parsed.adjusted_filters` lists moved/omitted specs; `ignored_filters` explains unapplied/rare filters; `counts_complete=false` means partial counts; `valid_values` lists accepted inputs on errors. In `jlc_get_part`, `prices` lists quantity tiers, `datasheet` links the datasheet, and `has_easyeda_footprint=null` means unknown (false means absent); MPN lookups return `results` and `total`. In alternatives, `summary.found` counts verified alternatives, `unverified_alternatives` need manual comparison, `specs_unparseable` lists specs not verified, and `unchecked_requirements` includes pinout/circuit checks still needed. In `board_get`, `focus_match_type` is exact, partial or ref matching; `consensus.board_count` counts compared boards, and `passives_omitted` counts hidden plain passives.

### JLCPCB (Local DB + Live API)

| Tool | Description |
|------|-------------|
| `jlc_search` | **Primary search** — smart query parsing + parametric spec filters (local DB, 630K+ in-stock parts, updated daily; default shortlist 20, max 100) |
| `jlc_stock_check` | Real-time stock verification via live JLCPCB API (use `jlc_search` first) |
| `jlc_get_part` | Full details for a specific LCSC part code or MPN lookup |
| `jlc_get_pinout` | Component pin information from EasyEDA symbols |
| `jlc_find_alternatives` | Find catalog-checked alternatives and separate unverified candidates |
| `jlc_search_help` | Browse categories, subcategories, and filterable attributes |

### Mouser (requires `MOUSER_API_KEY`)

| Tool | Description |
|------|-------------|
| `mouser_get_part` | Price, stock, and datasheet for specific parts on Mouser; batch up to 10 per call (shared daily limit on pcbparts.dev) |

### DigiKey (requires `DIGIKEY_CLIENT_ID` + `DIGIKEY_CLIENT_SECRET`)

| Tool | Description |
|------|-------------|
| `digikey_get_part` | Price, stock, and datasheet for one part on DigiKey (shared daily limit on pcbparts.dev) |

### Sensor Recommendation (no key required)

| Tool | Description |
|------|-------------|
| `sensor_recommend` | Find sensor ICs/modules by measurement need, protocol, or platform (1,600+ sensors, 56 measure types) |

### Reference Boards (no key required)

| Tool | Description |
|------|-------------|
| `board_search` | Search ~285 OSHW reference board schematics by IC, tag, org, or free text. Cross-board consensus shows how ICs are typically used. |
| `board_get` | Get full board details — BOM, design rules, dimensions. Use `focus` param for pin-grouped IC neighborhoods (decoupling, bias, connections). |

### Design Rules (no key required)

| Tool | Description |
|------|-------------|
| `get_design_rules` | PCB design rules & best practices (41 curated reference files: power, protection, interfaces, MCUs, layout, EMC) |

### SamacSys (no key required)

| Tool | Description |
|------|-------------|
| `cse_search` | Search for ECAD models, datasheets, and footprint availability |
| `cse_get_kicad` | Download KiCad symbols and footprints for any part |

## search vs stock_check

Use **`jlc_search`** (default) for:
- Parametric filtering ("Vgs(th) < 2V", "voltage >= 25V")
- Smart query parsing ("10k 0603 1%" auto-detects value, package, tolerance)
- Most searches

Use **`jlc_stock_check`** only when you need:
- Real-time stock verification before ordering
- Out-of-stock or low-stock parts (stock < 10)
- The full catalog (7M+ parts; `jlc_search` covers the 630K+ with stock >= 10)

## Library Types

| Type | Assembly Fee | Description |
|------|-------------|-------------|
| `basic` | None | Common parts in JLCPCB's standard library |
| `preferred` | None | Recommended parts with good availability |
| `extended` | $3/unique part | Less common parts |
| `no_fee` | None | Filter shortcut: searches basic + preferred combined |

## Subcategory Aliases

Natural language names that map to JLCPCB subcategories (220+ aliases supported):

| Category | Aliases |
|----------|---------|
| Capacitors | `mlcc`, `ceramic capacitor`, `electrolytic`, `tantalum`, `polymer capacitor` |
| Resistors | `resistor`, `chip resistor`, `current sense resistor` |
| Inductors | `inductor`, `ferrite bead`, `ferrite` |
| Diodes | `schottky`, `zener`, `tvs`, `esd diode`, `rectifier` |
| MOSFETs | `mosfet`, `n-channel mosfet`, `p-channel mosfet`, `nmos`, `pmos` |
| Regulators | `ldo`, `buck`, `boost`, `dc-dc` |
| Crystals | `crystal`, `oscillator`, `tcxo` |
| Connectors | `usb-c`, `pin header`, `jst`, `terminal block`, `qwiic` |
| LEDs | `led`, `rgb led`, `ws2812`, `neopixel` |
| MCUs | `mcu`, `microcontroller` |
| Relays | `relay` |
| Interface ICs | `level shifter`, `rs485 transceiver`, `can transceiver` |
| Drivers, switches | `gate driver`, `mosfet driver`, `high side switch` |

`inductor`, `relay` and `diode` each cover several subcategories (SMD, power, molded and through-hole inductors; signal, power, automotive, reed and latching relays; switching, general-purpose, Schottky, fast-recovery and SBR diodes).

A value in the query goes to the spec that part type lists: "5V relay" is the coil voltage, "3.3V LDO" the exact output, "12V buck converter" an output range covering 12V (with Topology Buck), "3.3V level shifter" a supply range covering 3.3V. "24V input 3.3V output" and "12V to 5V" set both sides of a regulator. If the part type lists no such spec, the value is left out and `parsed.adjusted_filters` says so; words that match no part together with the rest of the query are left out and `relaxed` says so; filters that can't be applied are listed in `ignored_filters`.

`jlc_search` defaults to **20** results; an explicit `limit` can request up to 100. Component replies omit `description` when nonempty `specs` already provide the detail. `price_10` is removed from search, stock-check and part-detail replies; use the stated quantity tiers in `jlc_get_part.prices`.

`packages` (search/stock check) and `manufacturers` (stock check) accept a list, JSON array string, or one bare string. Values containing commas stay intact. Query package alternatives such as `100nF 25V capacitors in 0402 or 0603` apply an OR constraint, equivalent to `packages=["0402", "0603"]`; explicit package arguments take precedence.

Explicit `spec_filters` accept JSON arrays or JSON array strings, with text or numeric values. Attribute/alias names ignore case, `=>` normalizes to `>=`, and unitless numbers use the attribute's base unit (V, A, ohms, F, H, Hz, W, mm or bytes; tolerance/ppm follow their named scale). Malformed lists/filters and invalid operators return an error with `valid_values` instead of removing constraints. Unknown library/sort enum values list their valid choices. Explicit unsupported or rare attributes are reported in `ignored_filters` with `attribute_share` and suggested real names; the reason distinguishes “not applied” (with the query-builder reason) from “applied, but few or none of these parts list it”, where results may be incomplete or empty. Rare valid constraints are retained. `Gate Threshold` and `Vgs(th)` both alias `Gate Threshold Voltage (Vgs(th))` / `Gate Threshold Voltage`.

`library_type_counts` and `no_fee_available` describe the same matching population as `total`, after every spec and library restriction. Post-filter scans check at most 50,000 SQL candidates; if that cap is reached, `counts_complete=false` labels these counts and availability as applying only to checked matches.

Recovery hints use exposed calls such as `jlc_search_help()` and `jlc_search_help(subcategory="MOSFETs")`. Every returned design-rule key (for example `power/ldo`) can be passed back as `get_design_rules(topic="power/ldo")` for that exact file.

Board consensus pin choices use distinct-board votes: `count` is supporting boards and `pct` divides by `consensus.board_count`. Each choice adds `boards` (supporting slugs) and `quantities` (component occurrences per supporting board). Repeated components on a board do not add votes; the denominator includes all matching boards with an IC neighborhood.

## Attribute Aliases

Short names for parametric spec filters:

| Component | Attributes |
|-----------|-----------|
| MOSFETs | `Vgs(th)`, `Vds`, `Id`, `Rds(on)` |
| Diodes | `Vr`, `If`, `Vf` |
| BJTs | `Vceo`, `Ic` |
| Regulators | `Vout`, `Iout`, `Quiescent Current` (also `standby current`, `Supply Current (Iq)`) |
| ICs | `Supply Voltage` (`Voltage - Supply`, or a level shifter's VCCA/VCCB) |
| Passives | `Capacitance`, `Resistance`, `Inductance`, `Voltage`, `Tolerance`, `Power`, `DCR`, `Isat` |
| Crystals, oscillators | `Frequency`, `Load Capacitance` |

Supply and output voltages are often ranges ("2.7V~5.5V"): `=` matches a range that includes the value, `>=` one that reaches it, `<=` one that goes down to it.

Use `jlc_search_help(subcategory=...)` to discover all filterable specs for any subcategory.

Query values accept `u`/`µ`/`μ` and `Ω`: `2.2µF`, `10 kΩ`, `4u7` (4.7uF, or 4.7uH in an inductor query), `6V3` (6.3V), and `1F`. Resistance prefixes keep their case: `10M`/`10Meg`/`10MEG` mean megaohms; `10m`/`10mOhm`/`10 milliohm` mean milliohms. Query package `1005` means imperial `0402`. Crystal/oscillator capacitance means `Load Capacitance`. Named comparisons such as `3.3V LDO quiescent current < 10µA`, `standby current < 10uA`, `Iq < 10uA`, and `schottky diode 1A Vf < 0.3V` preserve the quantity and operator. Use a numeric limit for idle current; “low Iq” does not apply one. Unparsed numeric units such as `2.2qF` stay in the text search, are listed in `parsed.detected.unsupported_constraints`, and are named as unapplied in `relaxed.reason` if the default relaxed retry drops them. Relaxation remains the default; pass `strict=true` to keep query words and parsed requirements, disable both text and library retries, and return an actionable error with no results for unsupported constraints (`ignored_filters` / `parsed.adjusted_filters`). Strict replies never contain `relaxed`. Shorthand rewrites do not alter model tokens or hyphen-connected suffixes such as `AMS1117-3V3`.

Compound `buck-boost`/`buck boost` topology is retained. Regulator input phrases (`input up to 24V`, `Vin 24V`, `24V max input`, `from 24V`, `up to 24V in`) target the supply, separately from output voltage. `3.3V to 5V bidirectional level shifter` checks Channel Type and VCCA/VCCB independently; verify bus and signal-standard compatibility in the datasheet. Through-hole mounting selects the through-hole resistor or leaded electrolytic category when the default is SMD-only.

`motor driver` covers all four motor-driver categories; `dc motor driver`/`h-bridge`, `stepper driver`, and `bldc driver`/`esc` select brushed DC, stepper, and BLDC respectively. Hobby-part aliases include `USB PD`/`USB-PD`, `eFuse`, `fuel gauge` (Monitoring IC), `MEMS microphone`, and `polymer capacitor`. `supercap`/`supercapacitor` is recognized as unavailable in this JLCPCB catalog and points to Mouser/DigiKey; general unknown-part-type handling is unchanged.

Memory sizes are minimum capacities: `ESP32-S3 module 16MB flash 8MB PSRAM` checks module N/R ordering codes, `microcontroller 128KB flash` checks Program Storage Size, and `SPI flash 16MB` still searches NOR flash. ESP32 modules with unknown memory codes cannot satisfy a memory constraint. An N-code without an R-code has known zero PSRAM, so it cannot satisfy a PSRAM minimum or replace a module requiring PSRAM.

Query words `basic`/`basic part`, `preferred`, and `no assembly fee`/`no fee` set the library filter; `cheapest`/`lowest price` select price sorting (within library tiers when `prefer_no_fee=true`). These appear in `parsed.detected`; explicit `library_type` and `sort_by` arguments win. Library choices have a schema enum, with case and `no-fee` normalized before validation. If a query-only library preference finds nothing, the default search retries without it and explains that the library preference was left out in `relaxed.reason`. An explicit `library_type` never relaxes. Stock-check and alternatives library arguments accept the same spellings; sort choices ignore case too.

Sensor filters accept `1-wire`/`one-wire` as `one_wire`, and `heart rate`/`blood oxygen` as `biometric`. Sensor measures, protocols and platforms, and board tags, are validated against the local catalog; unknown values return an error with `valid_values`. ESP-IDF has no platform-support records in this catalog, so `platform="esp-idf"` reports the supported choices. Board tag `usb-c` maps to `usb`; tag matching ignores case and surrounding whitespace.



## Package Expansion

Package filters auto-expand to include variants:
- `"SOT-23"` → includes `SOT-23-3`, `SOT-23-3L`, `SOT-23(TO-236)`
- `"0603"` → includes `1608` (metric equivalent)
- Specific packages like `"QFN-24-EP(4x4)"` are NOT expanded

## find_alternatives

Finds alternatives checked against catalog compatibility rules (`summary.found` counts only verified alternatives). `unverified_alternatives` separately lists candidates missing a required match, with `verification_status`, `unverified_requirements` and `unchecked_requirements`; these require manual comparison. Unsupported categories continue to return `similar_parts`, with `summary.found=0` and `summary.similar_count`.

1. Matches the primary spec (resistance, capacitance, etc.) and required specs. Missing or unparseable required matches cannot enter `alternatives`.
2. Checks connector contacts, mounting orientation and stated wire-to-board reference series; battery IC function; transistor polarity/count; and module chip identity. An empty ESP32 chip attribute can be inferred from its MPN. ESP32 N/R flash and PSRAM capacities must be at least the original's; unknown capacities are unverified.
3. Checks same-or-better ratings. Dropout, Vf and RDS(on) use test conditions when available. Unchecked secondary specs stay in `specs_unparseable` and `unchecked_requirements` and lower confidence.
4. Requires regulator input/output ranges to cover the original's full ranges. A scalar supply rating proves only the maximum; minimum input voltage remains unchecked. Regulator pinout and external-circuit requirements always need manual review, so regulator confidence is never high.
5. Ranks no-fee parts (basic/preferred) first. Within each fee tier, passives and crystals prefer the original package, then the existing stock/footprint/manufacturer/price score. Other packages remain available; `same_package=true` filters them out. Each verified/unverified list has its own `limit` (default 10, max 50).

Candidates come from live JLCPCB search and the daily local database. Rule checks establish catalog compatibility, not a guaranteed drop-in replacement; review datasheets and `package_warning`. An empty `library_type="no_fee"` result states how many verified extended matches were evaluated (`summary.extended_count`), rather than claiming no savings are possible. Counts are bounded by the candidate search, not catalog totals.

Use an LCSC C-code for `lcsc`; for an MPN, first use `jlc_get_part(mpn=...)`. Project savings accept positive `board_quantity` and `placements_per_board` (both default 1). `comparison.savings` separates the one-time `assembly_fee` difference, `unit_price_diff`, `component_quantity` and `order_total`; the misleading `total_per_unit` field is removed. Fees include added as well as removed extended part types, assuming the original type is removed entirely and the replacement type is newly added to the order. Prices are qty-1 tier estimates; unknown prices leave unit/order savings null.

Supported: Resistors, capacitors, inductors, ferrite beads, MOSFETs, BJTs, diodes (all types), LEDs, optocouplers, crystals, oscillators, LDOs, DC-DC converters, voltage references, WiFi/BT/LoRa modules, switches, relays, connectors, and more (120+ subcategories).

## Example Queries

```
"Find logic-level MOSFETs with Vgs(th) < 2V and Id >= 5A"
"100nF 25V capacitors in 0402 or 0603"
"Find alternatives for C82899 in basic library"
"STM32 microcontrollers with 10000+ stock"
"Look up TPS63020 stock and pricing on Mouser"
"Get KiCad footprint for ESP32-S3-WROOM-1"
"What sensor should I use to measure CO2 on ESPHome?"
"Recommend an IMU sensor with I2C interface"
"Show me boards that use the MCP73831 charger"
"How is the RP2040 typically used? What decoupling and crystal do real boards use?"
"Get the ESP32-S3 neighborhood on the Adafruit Feather"
"What are the design rules for USB-C?"
"Show me LDO design best practices"
```

## API Details

- **Endpoint:** `https://pcbparts.dev/mcp`
- **Transport:** Streamable HTTP (stateless)
- **Health:** `https://pcbparts.dev/health` (status, version, EasyEDA footprint answers seeded and stored, CSE searches and KiCad parts stored, and each distributor's requests today)
- **Usage stats:** `https://pcbparts.dev/mcp/stats` (anonymous counts per UTC day, with totals for the days shown: calls per UTC hour, calls to each tool split into ok, similar_only (alternatives that returned only similar or unverified candidates to compare by hand), not_found, bad_request, rate_limited and failed, with the average time, which MCP apps connect, the number of distinct callers, and Mouser/DigiKey lookups sent, cached or turned away by the limits; the stats keep no IPs, queries or part numbers; the last 30 days, `?days=N` for fewer)
- **Rate limit:** 100 requests/minute per IP
- **Auth:** None required

## Self-Hosting

On pcbparts.dev, Mouser and DigiKey lookups share one API key each: 1,000 requests a day and 25 (Mouser) or 100 (DigiKey) a minute for everyone. Self-hosting with your own keys (`MOUSER_API_KEY`, `DIGIKEY_CLIENT_ID`/`DIGIKEY_CLIENT_SECRET`, free from Mouser's API hub and DigiKey's developer portal) gets you your own limits.

```bash
git clone https://github.com/Averyy/pcbparts-mcp
cd pcbparts-mcp
uv venv && uv pip install -e .
.venv/bin/python -m pcbparts_mcp.server  # http://localhost:8080/mcp
```

The server builds `data/components.db` only when it's missing. If yours is from before 0.6.0,
rebuild it (`.venv/bin/python scripts/build_database.py`) to get the EasyEDA footprint seed;
without it, footprint checks still work but each one asks EasyEDA.
The server logs a warning if the database predates this version; rebuilding with the same
command also fixes missing quiescent-current filter matches and slow MPN lookups.

Or with Docker:

```bash
docker compose up -d                                    # production (GHCR image)
docker compose -f docker-compose.local.yml up --build   # local dev (builds from source)
```

`docker-compose.yml` publishes the server on `127.0.0.1:8080` only, for a reverse proxy on the same
host (pcbparts.dev runs Caddy in front of it). To reach it from other machines, change the port
mapping to `"8080:8080"`.

Building the image needs BuildKit, the default builder since Docker 23 and the one Compose v2 uses.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HTTP_PORT` | `8080` | Server port |
| `RATE_LIMIT_REQUESTS` | `100` | Requests per minute per IP |
| `MCP_ALLOWED_HOSTS` | `pcbparts.dev` | Comma-separated Host headers accepted by the server (DNS-rebinding protection; localhost is always allowed) |
| `DISTRIBUTOR_DAILY_LIMIT` | `1000` | Daily API request quota per distributor (Mouser/DigiKey) |
| `DISTRIBUTOR_QUOTA_PATH` | `/app/cache/distributor_quota.json` in Docker, unset otherwise | JSON file that keeps each distributor's request count for the day, and any pause Mouser or DigiKey asked for, across restarts. Unset means memory only, so every restart starts the count from 0 |
| `USAGE_STATS_PATH` | `/app/cache/usage_stats.json` in Docker, unset otherwise | JSON file that keeps the `/mcp/stats` counts for a year (about 650 KB) across restarts; `/mcp/stats` shows the last 30 days. Unset means memory only |
| `MOUSER_API_KEY` | — | Mouser API key (optional, enables Mouser tools) |
| `DIGIKEY_CLIENT_ID` | — | DigiKey OAuth2 client ID (optional, enables DigiKey tools) |
| `DIGIKEY_CLIENT_SECRET` | — | DigiKey OAuth2 client secret |
| `EASYEDA_STORE_PATH` | `/app/cache/easyeda.db` in Docker, unset otherwise | SQLite file that keeps EasyEDA footprint answers across restarts. The compose files mount a named volume at `/app/cache`. Unset means memory only |
| `CSE_STORE_PATH` | `/app/cache/cse.db` in Docker, unset otherwise | SQLite file that keeps CSE searches and KiCad files across restarts (an uncached CSE search takes 11-15 s). A search where every part has a model, and KiCad files, are kept a year; a search with a part that has no model yet, or no parts, a week. Unset means memory only |

## LLM-Readable Documentation

An [`llms.txt`](https://pcbparts.dev/llms.txt) file is available for LLMs and AI agents to quickly understand this service. See [llmstxt.org](https://llmstxt.org/) for the spec.

## Changelog

See [CHANGELOG.md](CHANGELOG.md). Minor releases in 0.x can change replies; each lists what to check under **Breaking**.

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup,
testing, and project conventions.

## License

MIT

## Links

- [pcbparts.dev](https://pcbparts.dev)
- [JLCPCB Parts Library](https://jlcpcb.com/parts)
- [MCP Protocol](https://modelcontextprotocol.io)
