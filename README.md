# PCB Parts MCP Server

MCP server that gives Claude, Cursor and other AI assistants electronic component data from JLCPCB, Mouser and DigiKey: parametric search over 630K+ in-stock JLCPCB parts, live stock and pricing on all three, KiCad footprints, reference boards, sensor picks and design rules. No API key required.

**Website:** [pcbparts.dev](https://pcbparts.dev) · **Endpoint:** `https://pcbparts.dev/mcp`

## Features

- **Parametric search:** ask in plain words ("10k 0603 1%", "logic-level MOSFET Vgs(th) < 2V") and the query becomes spec, package and part-type filters
- **Three distributors:** search JLCPCB's catalog, and check live price and stock on JLCPCB, Mouser and DigiKey
- **Alternatives:** replacements checked against compatibility rules for 120+ part types, with no-assembly-fee parts first
- **Part details:** lookup by LCSC code or manufacturer part number, with price tiers, datasheet PDFs, pinouts and EasyEDA footprints
- **KiCad files:** symbols and footprints from SamacSys
- **Reference boards:** ~300 open-source boards and Espressif DevKits, showing how real designs wire an IC (decoupling, crystals, pull-ups)
- **Sensors:** 1,600+ sensor ICs and modules by what they measure, their bus and the platforms with drivers
- **Design rules:** 46 reference files on power, protection, interfaces, MCUs, layout and EMC

## Quick start

### Claude Code

```bash
claude mcp add -s user --transport http pcbparts https://pcbparts.dev/mcp
```

To skip the approval prompt on every call, add this to `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["mcp__pcbparts__*"]
  }
}
```

### Claude Desktop and Cursor

Claude Desktop: Settings → Connectors → "Add custom connector", or edit `~/Library/Application Support/Claude/claude_desktop_config.json`. Cursor: edit `~/.cursor/mcp.json`. Both take:

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

Add to the Extensions config:

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

## Tools (16)

| Tool | What it does |
|------|--------------|
| `jlc_search` | Main search: plain-words queries, spec filters and sorting by a spec over the daily catalog snapshot |
| `jlc_stock_check` | Live JLCPCB stock, including out-of-stock and low-stock parts |
| `jlc_stock_history` | Recorded low-stock events for one LCSC code, with scrape-gap warnings and snapshot stock |
| `jlc_get_part` | Full details for an LCSC code or manufacturer part number |
| `jlc_get_pinout` | Pin numbers and names from the EasyEDA symbol; `footprint=true` adds the footprint's pads |
| `jlc_find_alternatives` | Replacements checked against compatibility rules, with unverified candidates listed apart |
| `jlc_search_help` | Categories, subcategories and the specs each one can filter on |
| `mouser_get_part` | Mouser price, stock and datasheet, up to 10 parts per call |
| `digikey_get_part` | DigiKey price, stock and datasheet for one part |
| `cse_search` | SamacSys search for ECAD models and datasheets |
| `cse_get_kicad` | KiCad symbol and footprint download |
| `board_search` | Find reference boards by IC, tag, org or text; consensus shows how boards use an IC |
| `board_get` | A board's BOM, design rules and dimensions; `focus` gives one part's pin-by-pin neighborhood |
| `sensor_recommend` | Sensors by measurement, protocol or platform |
| `get_design_rules` | Design rules and checklists by topic |

A typical session goes `get_design_rules` or `board_search` → `jlc_search` → `jlc_get_part` → `jlc_find_alternatives` → `cse_get_kicad`.

## Example queries

```
"Find logic-level MOSFETs with Vgs(th) < 2V and Id >= 5A"
"100nF 25V capacitors in 0402 or 0603"
"Find alternatives for C82899 in the basic library"
"Look up TPS63020 stock and pricing on Mouser"
"Get the KiCad footprint for ESP32-S3-WROOM-1"
"What sensor should I use to measure CO2 on ESPHome?"
"How is the RP2040 typically used? What decoupling and crystal do real boards use?"
"What are the design rules for USB-C?"
```

## Good to know

- `jlc_search` covers parts with at least 10 in stock, from a snapshot taken daily (`data_as_of` in each reply). Its prices are refreshed weekly (`prices_as_of`). `jlc_get_part(lcsc=...)` and `jlc_stock_check` are live, and `jlc_stock_check` also reaches the rest of JLCPCB's 7M+ part catalog.
- For Economic assembly, **basic** and **preferred** parts avoid the extended-type loading fee. Alternatives savings use a rounded legacy **$3 estimate** per extended type, not a current quote; Standard assembly fees differ. `jlc_search` ranks basic and preferred parts first, and `library_type="no_fee"` keeps only those.
- Spec figures are JLCPCB's listings, and alternatives are checked against the catalog. Check the datasheet and pinout before you order.
- On pcbparts.dev, all users share one Mouser key and one DigiKey app: 1,000 requests a day each. Self-host with your own keys to get your own limits.

[docs/search-guide.md](docs/search-guide.md) covers how queries are read, spec filter syntax, package matching, sorting and the alternatives rules.

## Self-hosting

```bash
git clone --depth 1 https://github.com/Averyy/pcbparts-mcp  # current files only (~80 MB; full history ~7 GB)
cd pcbparts-mcp
uv venv && uv pip install -e .
uv run python -m pcbparts_mcp.server  # http://localhost:8080/mcp
```

Or with Docker (needs BuildKit, the default since Docker 23). `docker-compose.yml` joins an external network named `web`, so create it first:

```bash
docker network create web
docker compose up -d                                    # GHCR image
docker compose -f docker-compose.local.yml up --build   # built from source
```

`docker-compose.yml` publishes the server on `127.0.0.1:8080` for a reverse proxy on the same host. Change the mapping to `"8080:8080"` to reach it from other machines.

The server builds `data/components.db` on first run. After upgrading, it logs a warning if the database is too old for the new version; rebuild it with `uv run python scripts/build_database.py`.

Build recorded stock history with `uv run python scripts/build_history_db.py`. `jlc_stock_history(lcsc, days=180)` shows up to 100 events, newest first, over 1-366 days ending at the newest recorded date. Changes above 1,000 stock are not tracked, and a missing part in a scrape is not a confirmed stockout. `JLCPCB_DATA_DIR` sets the data directory; `JLCPCB_HISTORY_DB_PATH` can override the history DB path.

Mouser keys are free from Mouser's API hub, and DigiKey client credentials from DigiKey's developer portal. `cse_get_kicad` downloads need a SamacSys ComponentSearchEngine account; `cse_search` works without one.

| Variable | Default | Description |
|----------|---------|-------------|
| `MOUSER_API_KEY` | — | Enables `mouser_get_part` |
| `DIGIKEY_CLIENT_ID`, `DIGIKEY_CLIENT_SECRET` | — | Enable `digikey_get_part` |
| `CSEARCH_USER`, `CSEARCH_PASS` | — | SamacSys login for `cse_get_kicad` |
| `HTTP_PORT` | `8080` | Server port |
| `RATE_LIMIT_REQUESTS` | `100` | Requests per minute per IP |
| `MCP_ALLOWED_HOSTS` | `pcbparts.dev` | Comma-separated Host headers to accept (DNS-rebinding protection; localhost always works) |
| `DISTRIBUTOR_DAILY_LIMIT` | `1000` | Daily request quota for each of Mouser and DigiKey |
| `DISTRIBUTOR_QUOTA_PATH` | `/app/cache/distributor_quota.json` in Docker | Keeps the day's Mouser/DigiKey counts and pauses across restarts |
| `USAGE_STATS_PATH` | `/app/cache/usage_stats.json` in Docker | Keeps the `/mcp/stats` counts across restarts |
| `EASYEDA_STORE_PATH` | `/app/cache/easyeda.db` in Docker | Keeps EasyEDA footprint answers across restarts |
| `CSE_STORE_PATH` | `/app/cache/cse.db` in Docker | Keeps SamacSys searches and KiCad files across restarts |

These four cache and statistics paths are unset outside Docker, which keeps that data in memory only. The compose files mount a named volume at `/app/cache`.

## API

- **Endpoint:** `https://pcbparts.dev/mcp`, Streamable HTTP (stateless), no auth
- **Rate limit:** 100 requests a minute per IP
- **Health:** `https://pcbparts.dev/health` (version, cache sizes, each distributor's requests today)
- **Usage stats:** `https://pcbparts.dev/mcp/stats`, anonymous daily counts of calls per tool and per hour, apps and Mouser/DigiKey lookups (including DigiKey's keyword retries found and missed), and why calls found nothing or failed: one label a call from a fixed list (`reasons`), plus how the checks behind an empty search went (`why_empty`). No IPs, queries or part numbers are kept.

## More

- [llms.txt](https://pcbparts.dev/llms.txt): this service described for LLMs, with the defaults and limits they need
- [CHANGELOG.md](CHANGELOG.md): every release, also published as [GitHub releases](https://github.com/Averyy/pcbparts-mcp/releases) from 0.8.21. Minor releases in 0.x can change replies, and each lists what to check under **Breaking**.
- [CONTRIBUTING.md](CONTRIBUTING.md): development setup, tests and project conventions. Issues and PRs welcome.
- License: MIT
