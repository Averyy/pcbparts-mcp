# JLCPCB MCP Server

MCP server for searching JLCPCB electronic components directly from Claude, Cursor, and other AI coding assistants. Search 1.5M+ parts for PCB assembly with real-time stock and pricing.

**Website:** [jlcmcp.dev](https://jlcmcp.dev)

## Features

- Search 1.5M+ JLCPCB components by keyword, category, stock, package, manufacturer
- **Multi-select filters:** Search multiple packages or manufacturers at once (OR logic)
- **Key specs in results:** Electrical attributes (voltage, current, etc.) included in search results
- **Manufacturer aliases:** Use common abbreviations like "TI", "STM", "Infineon" - auto-corrected to API names
- **Find alternatives:** Discover similar parts with better availability
- **Volume pricing:** See both unit price and 10+ quantity pricing
- **Low stock warnings:** Parts with <500 units flagged for attention
- Filter by library type (basic/preferred = no fee, extended = $3 fee)
- Get detailed part info including pricing tiers and datasheets
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

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `search_parts` | Search components with filters for category, stock, package(s), manufacturer(s), library type |
| `get_part` | Get full details for a specific LCSC part code |
| `find_alternatives` | Find similar parts in same subcategory with library_type, package, and EasyEDA filters |
| `list_categories` | Get all 52 primary component categories |
| `get_subcategories` | Get subcategories for a category |
| `validate_bom` | Validate BOM parts, check stock/availability, calculate costs |
| `export_bom` | Generate JLCPCB-compatible BOM CSV with validation and cost calculation |
| `get_version` | Server version and health status |

### search_parts Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Keywords, part numbers, or attribute values (e.g., "10uF 25V", "STM32F103") |
| `category_id` | int | Category ID from `list_categories` |
| `subcategory_id` | int | Subcategory ID from `get_subcategories` |
| `min_stock` | int | Minimum stock (default: 50, set 0 for all) |
| `library_type` | string | "basic", "preferred", "no_fee", "extended", or "all" |
| `package` | string | Single package filter (e.g., "0402") |
| `packages` | string[] | Multiple packages, OR logic (e.g., ["0402", "0603", "0805"]) |
| `manufacturer` | string | Single manufacturer filter |
| `manufacturers` | string[] | Multiple manufacturers, OR logic |
| `sort_by` | string | "quantity" (highest first) or "price" (cheapest first) |
| `page` | int | Page number (default: 1) |
| `limit` | int | Results per page (default: 20, max: 100) |

### find_alternatives Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `lcsc` | string | LCSC part code to find alternatives for (e.g., "C82899") |
| `min_stock` | int | Minimum stock for alternatives (default: 100) |
| `same_package` | bool | Only return parts with the same package size |
| `library_type` | string | "basic", "preferred", "no_fee", or "all" (default) to filter alternatives |
| `has_easyeda_footprint` | bool | Filter by EasyEDA footprint availability |
| `limit` | int | Max alternatives to return (default: 10, max: 50) |

## Example Prompts

```
"Search for 100nF 25V capacitors in 0402 or 0603 packages"
"Find ESP32 modules in the basic library" (no assembly fee)
"Get details for part C82899"
"Search for 10k resistors from Yageo or UniOhm"
"Find STM32 or CH32 microcontrollers with 10000+ stock"
"List all JLCPCB component categories"
```

## JLCPCB Library Types

JLCPCB has three library types that affect PCB assembly fees:

| Type | Fee | Description |
|------|-----|-------------|
| `basic` | None | Common parts in JLCPCB's standard library |
| `preferred` | None | Recommended parts with good availability |
| `extended` | $3/unique | Less common parts |

Use `library_type="no_fee"` to search both basic and preferred parts combined.

## Search Tips

- **Attribute Search:** Include specs in your query like "10uF 25V" or "100k 1%" - these search against component attributes
- **Multi-Select:** Use `packages` or `manufacturers` arrays to search multiple values with OR logic
- **Min Stock:** Results filtered to 50+ units by default. Set `min_stock=0` to include all parts
- **Category Matching:** Single-word queries like "capacitor", "LED", "ESD" auto-match to categories
- **Sorting:** Use `sort_by="quantity"` for highest stock, or `sort_by="price"` for cheapest first

## API Details

- **Endpoint:** `https://jlcmcp.dev/mcp`
- **Transport:** Streamable HTTP (MCP 2.0+)
- **Health:** `https://jlcmcp.dev/health`
- **Rate Limit:** 100 requests/minute per IP
- **Authentication:** None required

## Self-Hosting

### Running Locally

```bash
# Clone and setup
git clone https://github.com/Averyy/jlcpcb-mcp
cd jlcpcb-mcp
uv venv && uv pip install -e ".[dev]"

# Run server
.venv/bin/python -m jlcpcb_mcp.server
```

Server runs at `http://localhost:8080/mcp`

### Docker Deployment

```bash
docker compose up -d
```

## Running Tests

```bash
# All tests (unit + integration)
.venv/bin/pytest tests/ -v

# Unit tests only
.venv/bin/pytest tests/ -v -k "not Integration"
```

## License

MIT

## Links

- **Website:** [jlcmcp.dev](https://jlcmcp.dev)
- **JLCPCB Parts Library:** [jlcpcb.com/parts](https://jlcpcb.com/parts)
- **MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
