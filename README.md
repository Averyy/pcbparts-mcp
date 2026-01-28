# JLCPCB MCP Server

MCP server for searching JLCPCB electronic components directly from Claude, Cursor, and other AI coding assistants. Search 400K+ in-stock parts for PCB assembly with parametric filtering.

**Website:** [jlcmcp.dev](https://jlcmcp.dev)

## Features

- **Parametric search:** Filter by electrical specs (Vgs(th) < 2V, Rds(on) < 10mΩ, etc.)
- **Smart query parsing:** "10k 0603 1%" auto-parses into structured filters
- **Find alternatives:** Spec-aware compatibility checking for 120+ component types
- **BOM validation:** Check stock, calculate costs, generate JLCPCB-compatible CSV
- **Pinout data:** Component pin information from EasyEDA symbols
- No API key required

## Quick Start

### Claude Code

```bash
claude mcp add --transport http jlcmcp https://jlcmcp.dev/mcp
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jlcmcp": {
      "type": "http",
      "url": "https://jlcmcp.dev/mcp"
    }
  }
}
```



## Available Tools

| Tool | Description |
|------|-------------|
| `search` | **Primary search** - smart parsing + parametric filters (local DB, 400K+ parts) |
| `search_api` | Live API search - real-time stock, full 1.5M catalog, basic filters only |
| `list_attributes` | Discover filterable attributes for a subcategory |
| `get_part` | Full details for a specific LCSC part code |
| `get_pinout` | Component pin information from EasyEDA symbols |
| `find_alternatives` | Spec-compatible alternatives with verification |
| `list_categories` | All 52 primary component categories |
| `get_subcategories` | Subcategories for a category |
| `validate_bom` | Validate BOM, check stock, calculate costs |
| `export_bom` | Generate JLCPCB-compatible BOM CSV |

## Library Types

| Type | Fee | Description |
|------|-----|-------------|
| `basic` | None | Common parts in JLCPCB's standard library |
| `preferred` | None | Recommended parts with good availability |
| `extended` | $3/unique | Less common parts |
| `no_fee` | None | Searches basic and preferred combined |

## search vs search_api

Use **`search`** (default) for:
- Parametric filtering ("Vgs(th) < 2V", "voltage >= 25V")
- Smart query parsing
- Most searches

Use **`search_api`** when you need:
- Real-time stock verification before ordering
- Out-of-stock parts (stock < 100)
- Full 1.5M catalog (search indexes 400K+ with stock ≥ 100)

## Subcategory Aliases

Natural language names that map to JLCPCB subcategories:

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

220+ aliases supported. Use `list_attributes` to discover filterable specs for any subcategory.

## Attribute Aliases

Short names for common electrical parameters:

| Component | Attributes |
|-----------|-----------|
| MOSFETs | `Vgs(th)`, `Vds`, `Id`, `Rds(on)` |
| Diodes | `Vr`, `If`, `Vf` |
| BJTs | `Vceo`, `Ic` |
| Passives | `Capacitance`, `Resistance`, `Inductance`, `Voltage`, `Tolerance`, `Power` |

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

**Supported:** Resistors, capacitors, inductors, ferrite beads, MOSFETs, BJTs, diodes (all types), LEDs, optocouplers, crystals, oscillators, LDOs, DC-DC converters, voltage references, WiFi/BT/LoRa modules, switches, relays, connectors, and more (120+ subcategories).

## BOM Tools

Input format for `validate_bom` and `export_bom`:

```python
parts = [
    {"lcsc": "C1525", "designators": ["C1", "C2", "C3"]},
    {"lcsc": "C25804", "designators": ["R1", "R2"]},
    {"designators": ["J1"], "comment": "USB-C", "footprint": "USB-C-SMD"},  # Manual
]
board_qty = 100  # Validates stock for 100 boards
```

Features: auto-fetches part details, merges duplicates, tiered pricing, flags extended parts, checks MOQ, reports EasyEDA footprint availability.

## Example Queries

```
"Find logic-level MOSFETs with Vgs(th) < 2V and Id >= 5A"
"100nF 25V capacitors in 0402 or 0603"
"Find alternatives for C82899 in basic library"
"STM32 microcontrollers with 10000+ stock"
"Validate my BOM and check for stock issues"
```

## API Details

- **Endpoint:** `https://jlcmcp.dev/mcp`
- **Health:** `https://jlcmcp.dev/health`
- **Rate Limit:** 100 requests/minute
- **Auth:** None required

## Self-Hosting

```bash
git clone https://github.com/Averyy/jlcpcb-mcp
cd jlcpcb-mcp
uv venv && uv pip install -e .
.venv/bin/python -m jlcpcb_mcp.server  # http://localhost:8080/mcp
```

Or with Docker: `docker compose up -d`

## License

MIT

## Links

- [jlcmcp.dev](https://jlcmcp.dev)
- [JLCPCB Parts Library](https://jlcpcb.com/parts)
- [MCP Protocol](https://modelcontextprotocol.io)
