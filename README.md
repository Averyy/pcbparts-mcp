# PCB Parts MCP Server

MCP server for searching electronic components across JLCPCB, Mouser, and DigiKey directly from Claude, Cursor, and other AI coding assistants. 1.5M+ parts with parametric filtering and KiCad footprints. No API key required.

**Website:** [pcbparts.dev](https://pcbparts.dev)

## Features

- **Cross-distributor search:** JLCPCB, Mouser, and DigiKey from one MCP server
- **Parametric search:** Filter by electrical specs (Vgs(th) < 2V, Rds(on) < 10mΩ, etc.)
- **Smart query parsing:** "10k 0603 1%" auto-parses into structured filters
- **Find alternatives:** Spec-aware compatibility checking for 120+ component types
- **KiCad footprints:** Download symbols and footprints via SamacSys
- **Pinout data:** Component pin information from EasyEDA symbols
- **MPN lookup:** Find JLCPCB equivalents by manufacturer part number
- **10 MCP tools** across 4 data sources
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
| `jlc_search` | **Primary search** — smart query parsing + parametric spec filters (local DB, 468K+ in-stock parts) |
| `jlc_stock_check` | Real-time stock verification via live JLCPCB API (use `jlc_search` first) |
| `jlc_get_part` | Full details for a specific LCSC part code or MPN lookup |
| `jlc_get_pinout` | Component pin information from EasyEDA symbols |
| `jlc_find_alternatives` | Find spec-compatible alternative parts with verification |
| `jlc_search_help` | Browse categories, subcategories, and filterable attributes |

### Mouser (requires `MOUSER_API_KEY`)

| Tool | Description |
|------|-------------|
| `mouser_get_part` | Cross-reference a specific MPN on Mouser (daily quota applies) |

### DigiKey (requires `DIGIKEY_CLIENT_ID` + `DIGIKEY_CLIENT_SECRET`)

| Tool | Description |
|------|-------------|
| `digikey_get_part` | Cross-reference a specific MPN on DigiKey (daily quota applies) |

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
- Full 1.5M catalog (search indexes 400K+ with stock ≥ 10)

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
| Passives | `Capacitance`, `Resistance`, `Inductance`, `Voltage`, `Tolerance`, `Power` |

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
"Cross-reference TPS63020 on Mouser and compare with JLCPCB pricing"
"Get KiCad footprint for ESP32-S3-WROOM-1"
```

## API Details

- **Endpoint:** `https://pcbparts.dev/mcp`
- **Transport:** Streamable HTTP (stateless)
- **Health:** `https://pcbparts.dev/health`
- **Rate limit:** 100 requests/minute per IP
- **Auth:** None required

## Self-Hosting

```bash
git clone https://github.com/Averyy/pcbparts-mcp
cd pcbparts-mcp
uv venv && uv pip install -e .
.venv/bin/python -m pcbparts_mcp.server  # http://localhost:8080/mcp
```

Or with Docker:

```bash
docker compose up -d                                    # production (GHCR image)
docker compose -f docker-compose.local.yml up --build   # local dev (builds from source)
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HTTP_PORT` | `8080` | Server port |
| `RATE_LIMIT_REQUESTS` | `100` | Requests per minute per IP |
| `DISTRIBUTOR_DAILY_LIMIT` | `1000` | Daily API request quota per distributor (Mouser/DigiKey) |
| `MOUSER_API_KEY` | — | Mouser API key (optional, enables Mouser tools) |
| `DIGIKEY_CLIENT_ID` | — | DigiKey OAuth2 client ID (optional, enables DigiKey tools) |
| `DIGIKEY_CLIENT_SECRET` | — | DigiKey OAuth2 client secret |

## LLM-Readable Documentation

An [`llms.txt`](https://pcbparts.dev/llms.txt) file is available for LLMs and AI agents to quickly understand this service. See [llmstxt.org](https://llmstxt.org/) for the spec.

## License

MIT

## Links

- [pcbparts.dev](https://pcbparts.dev)
- [JLCPCB Parts Library](https://jlcpcb.com/parts)
- [MCP Protocol](https://modelcontextprotocol.io)
