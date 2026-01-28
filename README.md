# JLCPCB MCP Server

MCP server for searching JLCPCB electronic components directly from Claude, Cursor, and other AI coding assistants. Search 1.5M+ parts for PCB assembly with real-time stock and pricing.

**Website:** [jlcmcp.dev](https://jlcmcp.dev)

## Features

- Search 1.5M+ JLCPCB components by keyword, category, stock, package, manufacturer
- **Parametric search:** Filter by electrical specs (voltage, current, Rds(on), etc.)
- **Indexed numeric columns:** Fast SQL queries on 67 parsed specs (resistance, capacitance, voltage, MCU flash/RAM, TVS clamping voltage, etc.)
- **European notation support:** "4k7" = 4.7kΩ, "4R7" = 4.7Ω, "0R" = jumper
- **Connector aliases:** U.FL, IPEX, MHF, I-PEX all search the same connector family
- **Multi-select filters:** Search multiple packages or manufacturers at once (OR logic)
- **Key specs in results:** Electrical attributes included in search results
- **Manufacturer aliases:** Use common abbreviations like "TI", "STM", "Infineon"
- **Find alternatives:** Spec-aware compatibility checking for 120+ subcategories
- **Volume pricing:** Unit price and 10+ quantity pricing
- **Low stock warnings:** Parts with <500 units flagged
- **BOM validation:** Check stock, calculate costs, generate JLCPCB-compatible CSV
- **Pinout data:** Get component pin information from EasyEDA symbols
- Filter by library type (basic/preferred = no fee, extended = $3 fee)
- Browse 52 component categories and subcategories
- Real-time stock levels from JLCPCB
- No API key or authentication required

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

### Cursor

Add to `~/.cursor/mcp.json`:

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

### VSCode

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "jlcmcp": {
      "type": "http",
      "url": "https://jlcmcp.dev/mcp"
    }
  }
}
```

### Other MCP Clients (stdio via mcp-remote)

```json
{
  "mcpServers": {
    "jlcmcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://jlcmcp.dev/mcp"]
    }
  }
}
```

## Available Tools (11)

| Tool | Description |
|------|-------------|
| `search` | **Primary search** - smart parsing + parametric filters (local DB, 400K+ parts) |
| `search_api` | Live API search - real-time stock, full 1.5M catalog, basic filters |
| `list_attributes` | Discover filterable attributes for a subcategory (use before spec_filters) |
| `get_part` | Get full details for a specific LCSC part code |
| `get_pinout` | Get component pin information from EasyEDA symbol data |
| `find_alternatives` | Find spec-compatible alternatives with verification for 120+ subcategories |
| `list_categories` | Get all 52 primary component categories |
| `get_subcategories` | Get subcategories for a category |
| `validate_bom` | Validate BOM parts, check stock/availability, calculate costs |
| `export_bom` | Generate JLCPCB-compatible BOM CSV with validation and cost calculation |
| `get_version` | Server version and health status |

## JLCPCB Library Types

JLCPCB has three library types that affect PCB assembly fees:

| Type | Fee | Description |
|------|-----|-------------|
| `basic` | None | Common parts in JLCPCB's standard library |
| `preferred` | None | Recommended parts with good availability |
| `extended` | $3/unique | Less common parts |

Use `library_type="no_fee"` to search both basic and preferred parts combined.

---

## search

**Primary search tool** - use this for most component searches.

Supports two modes:
1. **Natural language:** "10k resistor 0603 1%" auto-parses into structured filters
2. **Parametric:** Explicit spec_filters for precise attribute-based searches

When to use `search_api` instead:
- Need real-time stock verification before ordering
- Need out-of-stock parts (stock < 100)
- Need the full 1.5M catalog (search indexes 400K+ with stock ≥ 100)

### Capabilities

Parametric filtering enables searches **impossible with the API**:
- "Find MOSFETs with Vgs(th) < 2.5V" (logic-level for 3.3V drive)
- "Find capacitors with voltage >= 25V"
- "Find Schottky diodes with Vr >= 100V and If >= 5A"

Uses a local SQLite database built from scraped JLCPCB data (400K+ parts).

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `subcategory_id` | int | Subcategory ID (e.g., 2954 for MOSFETs) |
| `subcategory_name` | string | Subcategory name or alias (see below) |
| `query` | string | Text search in part number, description |
| `spec_filters` | list | Attribute filters (see below) |
| `min_stock` | int | Minimum stock (default: 100) |
| `library_type` | string | "basic", "preferred", "extended", or null (default: no filter) |
| `prefer_no_fee` | bool | Sort basic/preferred first (default: true) |
| `package` | string | Single package filter |
| `packages` | list | Multiple packages with OR logic |
| `match_all_terms` | bool | FTS mode: true=AND, false=OR (default: true) |
| `sort_by` | string | "stock" (default) or "price" |
| `limit` | int | Max results (default: 50) |

### spec_filters Format

```json
[
  {"name": "Vgs(th)", "op": "<", "value": "2.5V"},
  {"name": "Voltage", "op": ">=", "value": "25V"}
]
```

**Supported operators:** `=`, `>=`, `<=`, `>`, `<`, `!=`

### Attribute Aliases

| Component | Attributes |
|-----------|-----------|
| MOSFETs | `Vgs(th)`, `Vds`, `Id`, `Rds(on)` |
| Diodes | `Vr`, `If`, `Vf` |
| BJTs | `Vceo`, `Ic` |
| Passives | `Capacitance`, `Resistance`, `Inductance`, `Voltage`, `Tolerance`, `Power`, `DCR` |
| Regulators | `Vout`, `Iout` |

### Subcategory Aliases (80+ supported)

| Category | Aliases |
|----------|---------|
| Capacitors | `mlcc`, `ceramic capacitor`, `electrolytic`, `tantalum`, `supercap` |
| Resistors | `resistor`, `chip resistor`, `smd resistor`, `current sense resistor` |
| Inductors | `inductor`, `ferrite bead`, `ferrite` |
| Diodes | `schottky`, `zener`, `tvs`, `esd diode`, `rectifier` |
| MOSFETs | `mosfet`, `n-channel mosfet`, `p-channel mosfet`, `nmos`, `pmos` |
| BJTs | `bjt`, `transistor`, `npn`, `pnp` |
| Regulators | `ldo`, `linear regulator`, `voltage regulator` |
| DC-DC | `dc-dc`, `buck`, `boost`, `buck converter` |
| Crystals | `crystal`, `xtal`, `oscillator`, `tcxo` |
| Connectors | `usb-c`, `type-c`, `pin header`, `jst`, `terminal block` |
| LEDs | `led`, `smd led`, `rgb led`, `ws2812`, `neopixel` |
| Switches | `tactile switch`, `push button`, `button`, `dip switch` |

### Package Family Expansion

Package filters automatically expand to include common variants:
- `"SOT-23"` → includes `SOT-23-3`, `SOT-23-3L`, `SOT-23(TO-236)`
- `"0603"` → includes `1608` (metric equivalent)
- `"TO-252"` → includes `TO-252-2`, `DPAK`
- Specific packages like `"QFN-24-EP(4x4)"` are NOT expanded

### Response Metadata

- `library_type_counts`: `{"basic": N, "preferred": N, "extended": N}`
- `no_fee_available`: `true`/`false` - whether basic/preferred parts exist
- `subcategory_resolved`: actual resolved subcategory name

### Examples

```python
# Logic-level MOSFETs for 3.3V GPIO
search(
    subcategory_name="MOSFETs",
    spec_filters=[
        {"name": "Vgs(th)", "op": "<", "value": "2V"},
        {"name": "Id", "op": ">=", "value": "3A"}
    ]
)

# 10uF 25V+ capacitors
search(
    subcategory_name="MLCC",
    query="10uF",
    spec_filters=[{"name": "Voltage", "op": ">=", "value": "25V"}]
)

# High-power MOSFETs for motor drive
search(
    subcategory_name="MOSFETs",
    spec_filters=[
        {"name": "Rds(on)", "op": "<", "value": "10mΩ"},
        {"name": "Id", "op": ">=", "value": "50A"},
        {"name": "Vds", "op": ">=", "value": "60V"}
    ]
)

# Same-value resistors in different packages
search(
    subcategory_name="Chip Resistor",
    query="10k 1%",
    packages=["0402", "0603", "0805"]
)
```

---

## search_api

**Live API search** - use when you need real-time data or the full catalog.

When to use instead of `search`:
- Real-time stock verification before ordering
- Out-of-stock parts (stock < 100)
- Full 1.5M catalog (search indexes 400K+ with stock ≥ 100)
- Pagination through large result sets

Limitations:
- No parametric filtering (can't do "Vgs(th) < 2V")
- No smart query parsing
- Basic keyword matching only

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Keywords, part numbers (e.g., "ESP32", "STM32F103") |
| `category_id` | int | Category ID from `list_categories` |
| `subcategory_id` | int | Subcategory ID from `get_subcategories` |
| `category_name` | string | Category name |
| `subcategory_name` | string | Subcategory name |
| `min_stock` | int | Minimum stock (default: 50, set 0 for all) |
| `library_type` | string | "basic", "preferred", "no_fee", "extended", or "all" |
| `package` | string | Package filter |
| `packages` | string[] | Multiple packages (OR logic) |
| `manufacturer` | string | Manufacturer filter |
| `manufacturers` | string[] | Multiple manufacturers (OR logic) |
| `sort_by` | string | "quantity" or "price" |
| `page` | int | Page number (default: 1) |
| `limit` | int | Results per page (default: 20, max: 100) |

---

## list_attributes

**Discover filterable attributes** for a subcategory. Use this to find out what `spec_filters` can be used with `search()`.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `subcategory_id` | int | Subcategory ID (e.g., 2954 for MOSFETs) |
| `subcategory_name` | string | Subcategory name or alias (e.g., "MOSFETs", "MLCC") |

### Response

```json
{
  "subcategory_id": 2954,
  "subcategory_name": "MOSFETs",
  "category_name": "Transistors/Thyristors",
  "attributes": [
    {
      "name": "Gate Threshold Voltage (Vgs(th))",
      "alias": "Vgs(th)",
      "type": "numeric",
      "count": 8500,
      "example_values": ["1V~2.5V", "0.5V", "1.5V~2.5V"]
    },
    {
      "name": "Type",
      "alias": null,
      "type": "string",
      "count": 10000,
      "values": ["N-Channel", "P-Channel"]
    }
  ]
}
```

### Attribute Types

| Type | Operators | Description |
|------|-----------|-------------|
| `numeric` | `=`, `>=`, `<=`, `>`, `<` | Values can be compared numerically |
| `string` | `=` | Exact match only |

### Usage Example

1. Call `list_attributes(subcategory_name="MOSFETs")`
2. Find attribute `"Gate Threshold Voltage (Vgs(th))"` with alias `"Vgs(th)"`
3. Use in search: `spec_filters=[{"name": "Vgs(th)", "op": "<", "value": "2.5V"}]`

**Tip:** Use the `alias` (short name) in spec_filters for convenience.

---

## find_alternatives

Uses **spec-aware compatibility checking** to find verified alternatives for 120+ supported subcategories. For unsupported categories, returns `similar_parts` for manual comparison.

### How It Works

1. Searches by primary spec value (resistance, capacitance, etc.)
2. Verifies `must_match` rules (e.g., capacitor dielectric, LED color, relay coil voltage)
3. Verifies `same_or_better` rules (e.g., higher voltage rating OK, lower tolerance OK)
4. Scores and ranks by library type (basic/preferred saves $3), stock, EasyEDA availability
5. Returns `alternatives` (verified compatible) or `similar_parts` (unsupported - verify manually)

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `lcsc` | string | LCSC part code to find alternatives for (e.g., "C82899") |
| `min_stock` | int | Minimum stock for alternatives (default: 100) |
| `same_package` | bool | Only return parts with the same package size |
| `library_type` | string | "basic", "preferred", "no_fee", or "all" (default) |
| `has_easyeda_footprint` | bool | Filter by EasyEDA footprint availability |
| `limit` | int | Max alternatives to return (default: 10, max: 50) |

### Response (Supported Categories)

- `original`: Original part details
- `alternatives`: List of verified-compatible alternatives with scores
- `summary`: Count of basic/preferred alternatives, savings message
- `comparison`: Side-by-side of original vs recommended with savings calculation
- `confidence`: "high" (all specs verified) or "medium" (some specs couldn't be parsed)

### Response (Unsupported Categories)

- `original`: Original part details
- `alternatives`: Empty list
- `similar_parts`: List of similar parts for manual comparison
- `manual_comparison`: Specs to verify manually

### Supported Subcategories

Resistors, capacitors (MLCC, electrolytic, tantalum, film), inductors, ferrite beads, MOSFETs, BJTs, JFETs, IGBTs, diodes (Schottky, Zener, general purpose, TVS), fuses, thermistors, LEDs, optocouplers, crystals, oscillators, LDO regulators, DC-DC converters (topology matching), voltage references, digital isolators, battery management ICs, level shifters, WiFi/Bluetooth/LoRa modules, switches (tactile, DIP, toggle, rocker), relays (power, signal, solid state), connectors (headers, terminals, USB, HDMI), and more.

---

## get_pinout

Fetches component pin information from EasyEDA symbol data.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `lcsc` | string | LCSC part code (e.g., "C8304") |
| `uuid` | string | EasyEDA symbol UUID (alternative to lcsc) |

### Response

```json
{
  "pin_count": 48,
  "pins": [
    {"number": "1", "name": "VBAT", "electrical": "undefined"},
    {"number": "2", "name": "PC13-TAMPER-RTC", "electrical": "undefined"}
  ]
}
```

### Electrical Types

- `undefined`: Not set by symbol creator (most common)
- `input`: Input pin
- `output`: Output pin
- `bidirectional`: I/O pin
- `power`: Power pin

---

## BOM Tools

### validate_bom

Validates BOM parts, checks stock/availability, calculates costs without generating CSV.

### export_bom

Generates JLCPCB-compatible BOM CSV with validation and cost calculation.

### Input Format

```python
parts = [
    {"lcsc": "C1525", "designators": ["C1", "C2", "C3"]},
    {"lcsc": "C25804", "designators": ["R1", "R2"]},
    {"designators": ["J1"], "comment": "USB-C", "footprint": "USB-C-SMD"},  # Manual part
]
board_qty = 100  # Optional: validates stock for 100 boards
```

### Features

- Auto-fetches part details (Comment, Footprint) from LCSC codes
- Merges duplicate LCSC codes (combines designators)
- Detects duplicate designators (error)
- Calculates tiered pricing based on order quantity
- Flags extended parts ($3 assembly fee each)
- Validates stock against `board_qty × quantity_per_board`
- Checks MOQ (minimum order quantity)
- Reports EasyEDA footprint availability

### CSV Output Format

```csv
Comment,Designator,Footprint,LCSC Part #
100nF 50V X7R 0402,"C1,C2,C3",0402,C1525
10K 1% 0603,"R1,R2",0603,C25804
```

---

## EasyEDA Footprint Availability

`get_part` and `find_alternatives` include EasyEDA footprint availability:
- `has_easyeda_footprint`: `true`/`false`/`null` (null = unknown)
- `easyeda_symbol_uuid` and `easyeda_footprint_uuid`: UUIDs for EasyEDA editor links

Use `find_alternatives(has_easyeda_footprint=True)` to only get parts with footprints available.

---

## Example Prompts

```
"Search for 100nF 25V capacitors in 0402 or 0603 packages"
"Find ESP32 modules in the basic library"
"Get details for part C82899"
"Search for 10k resistors from Yageo or UniOhm"
"Find STM32 or CH32 microcontrollers with 10000+ stock"
"Find logic-level MOSFETs with Vgs(th) < 2V and Id >= 5A"
"Find alternatives for C82899 in basic/preferred library"
"Validate my BOM and check for stock issues"
```

## Search Tips

- **Attribute Search:** Include specs in your query like "10uF 25V" or "100k 1%"
- **Multi-Select:** Use `packages` or `manufacturers` arrays for OR logic
- **Min Stock:** Results filtered to 50+ units by default. Set `min_stock=0` for all
- **Category Matching:** Single-word queries like "capacitor", "LED" auto-match categories
- **Sorting:** Use `sort_by="quantity"` for highest stock, `sort_by="price"` for cheapest
- **Parametric:** Use `search()` with spec_filters when you need to filter by electrical specs

---

## API Details

- **Endpoint:** `https://jlcmcp.dev/mcp`
- **Transport:** Streamable HTTP (MCP 2.0+)
- **Health:** `https://jlcmcp.dev/health`
- **Rate Limit:** 100 requests/minute per IP
- **Authentication:** None required

---

## Architecture

```
jlcpcb-mcp/
├── src/jlcpcb_mcp/
│   ├── __init__.py         # Version
│   ├── config.py           # Configuration, headers
│   ├── client.py           # JLCPCB API client (curl_cffi)
│   ├── server.py           # FastMCP server
│   ├── db.py               # SQLite database for parametric search
│   ├── bom.py              # BOM generation and validation
│   ├── pinout.py           # EasyEDA pinout parser
│   ├── mounting.py         # Mounting type detection
│   ├── alternatives.py     # Spec-aware alternative finding
│   └── categories.py       # 52 categories + subcategories
├── data/                   # Scraped component data
│   ├── components.db       # SQLite database
│   ├── manifest.json       # Scrape metadata
│   ├── subcategories.json  # Subcategory ID mappings
│   └── categories/         # Gzipped JSONL per category
├── scripts/
│   ├── scrape_components.py  # Weekly JLCPCB scraper
│   └── build_database.py     # Convert JSONL → SQLite
├── landing/                # Website at jlcmcp.dev
├── tests/
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Self-Hosting

### Running Locally

```bash
git clone https://github.com/Averyy/jlcpcb-mcp
cd jlcpcb-mcp
uv venv && uv pip install -e ".[dev]"
.venv/bin/python -m jlcpcb_mcp.server
```

Server runs at `http://localhost:8080/mcp`

### Docker Deployment

```bash
docker compose up -d
docker logs jlcpcb-mcp -f
curl https://jlcmcp.dev/health
```

---

## Development

### Running Tests

```bash
# All tests (unit + integration)
.venv/bin/pytest tests/ -v

# Unit tests only (no API calls)
.venv/bin/pytest tests/ -v -k "not Integration"

# Integration tests (hits real API)
.venv/bin/pytest tests/ -v -k "Integration"
```

### Reinstall After Changes

```bash
uv pip install -e ".[dev]"
```

### Quick API Test

```bash
.venv/bin/python -c "
import asyncio
from jlcpcb_mcp.client import JLCPCBClient

async def test():
    client = JLCPCBClient()
    result = await client.search(query='ESP32', limit=3)
    print(f'{result[\"total\"]} results')
    await client.close()

asyncio.run(test())
"
```

---

## License

MIT

## Links

- **Website:** [jlcmcp.dev](https://jlcmcp.dev)
- **JLCPCB Parts Library:** [jlcpcb.com/parts](https://jlcpcb.com/parts)
- **MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
