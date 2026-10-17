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

### JLCPCB (Local DB + Live API)

| Tool | Description |
|------|-------------|
| `jlc_search` | **Primary search** — smart query parsing + parametric spec filters (local DB, 630K+ in-stock parts, updated daily) |
| `jlc_stock_check` | Real-time stock verification via live JLCPCB API (use `jlc_search` first) |
| `jlc_get_part` | Full details for a specific LCSC part code or MPN lookup |
| `jlc_get_pinout` | Component pin information from EasyEDA symbols |
| `jlc_find_alternatives` | Find spec-compatible alternative parts with verification |
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
| Capacitors | `mlcc`, `ceramic capacitor`, `electrolytic`, `tantalum`, `supercap` |
| Resistors | `resistor`, `chip resistor`, `current sense resistor` |
| Inductors | `inductor`, `ferrite bead`, `ferrite` |
| Diodes | `schottky`, `zener`, `tvs`, `esd diode`, `rectifier` |
| MOSFETs | `mosfet`, `n-channel mosfet`, `p-channel mosfet`, `nmos`, `pmos` |
| Regulators | `ldo`, `buck`, `boost`, `dc-dc` |
| Crystals | `crystal`, `oscillator`, `tcxo` |
| Connectors | `usb-c`, `pin header`, `jst`, `terminal block`, `qwiic` |
| LEDs | `led`, `rgb led`, `ws2812`, `neopixel` |
| MCUs | `mcu`, `microcontroller` |

## Attribute Aliases

Short names for parametric spec filters:

| Component | Attributes |
|-----------|-----------|
| MOSFETs | `Vgs(th)`, `Vds`, `Id`, `Rds(on)` |
| Diodes | `Vr`, `If`, `Vf` |
| BJTs | `Vceo`, `Ic` |
| Regulators | `Vout`, `Iout` |
| Passives | `Capacitance`, `Resistance`, `Inductance`, `Voltage`, `Tolerance`, `Power`, `DCR`, `Isat` |
| Crystals, oscillators | `Frequency` |

Use `jlc_search_help(subcategory=...)` to discover all filterable specs for any subcategory.

## Package Expansion

Package filters auto-expand to include variants:
- `"SOT-23"` → includes `SOT-23-3`, `SOT-23-3L`, `SOT-23(TO-236)`
- `"0603"` → includes `1608` (metric equivalent)
- Specific packages like `"QFN-24-EP(4x4)"` are NOT expanded

## find_alternatives

Finds verified-compatible alternatives using spec-aware rules:

1. Matches primary spec (resistance, capacitance, etc.)
2. Verifies `must_match` specs (dielectric, LED color, relay coil voltage)
3. Verifies `same_or_better` specs (higher voltage OK, lower tolerance OK)
4. Ranks by library type (basic/preferred saves $3), stock, EasyEDA availability

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
- **Health:** `https://pcbparts.dev/health` (status, version, EasyEDA footprint answers seeded and stored, and each distributor's requests today)
- **Usage stats:** `https://pcbparts.dev/mcp/stats` (anonymous counts per UTC day, with totals for the days shown: calls per UTC hour, calls to each tool split into ok, not_found, bad_request, rate_limited and failed, with the average time, which MCP apps connect, the number of distinct callers, and Mouser/DigiKey lookups sent, cached or turned away by the limits; the stats keep no IPs, queries or part numbers; the last 30 days, `?days=N` for fewer)
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

Or with Docker:

```bash
docker compose up -d                                    # production (GHCR image)
docker compose -f docker-compose.local.yml up --build   # local dev (builds from source)
```

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

## LLM-Readable Documentation

An [`llms.txt`](https://pcbparts.dev/llms.txt) file is available for LLMs and AI agents to quickly understand this service. See [llmstxt.org](https://llmstxt.org/) for the spec.

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup,
testing, and project conventions.

## License

MIT

## Links

- [pcbparts.dev](https://pcbparts.dev)
- [JLCPCB Parts Library](https://jlcpcb.com/parts)
- [MCP Protocol](https://modelcontextprotocol.io)
