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

### Claude Desktop and claude.ai

Customize → Connectors → "+ Add" → "Add custom connector", with the URL `https://pcbparts.dev/mcp`. Remote servers are added this way; `claude_desktop_config.json` only runs local servers.

### Cursor

Edit `~/.cursor/mcp.json`:

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

## Tools (17)

| Tool | What it does |
|------|--------------|
| `jlc_search` | Main search: plain-words queries, spec filters and sorting by a spec over the daily catalog snapshot |
| `jlc_stock_check` | Live JLCPCB stock, including out-of-stock and low-stock parts |
| `jlc_stock_history` | Recorded low-stock events for one LCSC code or a list of up to 50, with scrape-gap warnings and snapshot stock |
| `jlc_get_part` | Full details for an LCSC code or manufacturer part number |
| `jlc_get_parts` | Up to 50 LCSC codes or part numbers at once from the daily snapshot (stock, price, library type), for BOM refreshes |
| `jlc_get_pinout` | Pin numbers and names from the EasyEDA symbol; `footprint=true` adds the footprint's pads |
| `jlc_find_alternatives` | Replacements checked against compatibility rules, with unverified candidates listed apart |
| `jlc_search_help` | Categories, subcategories and the specs each one can filter on |
| `mouser_get_part` | Mouser price, stock and datasheet, up to 10 parts per call |
| `digikey_get_part` | DigiKey price, stock and datasheet for one part |
| `part_lifecycle` | Lifecycle status (active, NRND, last time buy, obsolete) for up to 50 parts, from Mouser and DigiKey |
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

- `jlc_search`, `jlc_get_parts` and `jlc_get_part` read a daily snapshot of parts with at least 10 in stock (1-piece prices weekly). `jlc_stock_check` and `jlc_get_part(lcsc=..., live=true)` are live (as is `jlc_get_part` for a code the snapshot doesn't list, or on a server without price tiers), and `jlc_stock_check` reaches JLCPCB's whole 7M+ part catalog; [llms.txt](https://pcbparts.dev/llms.txt) has the details.
- For Economic assembly, **basic** and **preferred** parts avoid the extended-type loading fee. Alternatives savings use a rounded legacy **$3 estimate** per extended type, not a current quote; Standard assembly fees differ. `jlc_search` ranks basic and preferred parts first, and `library_type="no_fee"` keeps only those.
- Spec figures are JLCPCB's listings, and alternatives are checked against the catalog. Check the datasheet and pinout before you order.
- The Mouser and DigiKey daily limits are shared by everyone on pcbparts.dev. Each address gets 200 Mouser and DigiKey lookups combined a day; stored answers are free. Self-host with your own keys to get your own limits.

[docs/search-guide.md](docs/search-guide.md) covers how queries are read, spec filter syntax, package matching, sorting and the alternatives rules.

## Self-hosting

```bash
git clone https://github.com/Averyy/pcbparts-mcp  # about 160 MB with full history
cd pcbparts-mcp
uv venv && uv pip install -e .
uv run python -m pcbparts_mcp.server  # http://localhost:8080/mcp; listens on all interfaces, HTTP_HOST=127.0.0.1 for this machine only
```

Or with Docker (needs BuildKit, the default since Docker 23). `docker-compose.yml` joins an external network named `web`, so create it first:

```bash
docker network create web
docker compose up -d                                    # GHCR image
docker compose -f docker-compose.local.yml up --build   # built from source
```

`docker-compose.yml` publishes the server on `127.0.0.1:8080` for a reverse proxy on the same host. Change the mapping to `"8080:8080"` to reach it from other machines.

The server builds `data/components.db` on first run. After upgrading, it logs a warning if the database is too old for the new version; rebuild it with `uv run python scripts/build_database.py`.

Quantity price tiers (`data/catalog/price_tiers.tsv.gz`) aren't in git. The GHCR image has them; a build from a clone has 1-piece prices only unless you first download the daily scrape's `price-tiers` artifact (kept 7 days; needs `gh auth login`). This tries the newest runs until one has it:

```bash
for run in $(gh run list -R Averyy/pcbparts-mcp -w scrape-components.yml -b main -s success -L 7 --json databaseId -q '.[].databaseId'); do
  gh run download "$run" -R Averyy/pcbparts-mcp -n price-tiers -D data/catalog && break
done
```

Build recorded stock history with `uv run python scripts/build_history_db.py`. `JLCPCB_DATA_DIR` sets the data directory; `JLCPCB_HISTORY_DB_PATH` can override the history DB path. Only changes leaving stock at 1,000 or below are recorded; [llms.txt](https://pcbparts.dev/llms.txt) has the tool's limits.

Mouser keys are free from Mouser's API hub, and DigiKey client credentials from DigiKey's developer portal. `cse_get_kicad` downloads need a SamacSys ComponentSearchEngine account; `cse_search` works without one.

| Variable | Default | Description |
|----------|---------|-------------|
| `MOUSER_API_KEY` | — | Enables `mouser_get_part` and `part_lifecycle` |
| `DIGIKEY_CLIENT_ID`, `DIGIKEY_CLIENT_SECRET` | — | Enable `digikey_get_part` and `part_lifecycle` |
| `CSEARCH_USER`, `CSEARCH_PASS` | — | SamacSys login for `cse_get_kicad` |
| `HTTP_HOST` | `0.0.0.0` | Bind address (`127.0.0.1` or `::1`: localhost only; `::`: all IPv6); keep `0.0.0.0` in Docker, whose compose file already publishes on 127.0.0.1 |
| `HTTP_PORT` | `8080` | Server port |
| `RATE_LIMIT_REQUESTS` | `300` | Requests per minute per IP or IPv6 /64 |
| `PLATFORM_RATE_LIMIT` | `1000` | Per-IP limit for the AI platforms' published ranges (at least `RATE_LIMIT_REQUESTS`) |
| `DB_STUCK_WAIT_SECONDS` | `60` | A database queue that starts no call for this many seconds makes `/health` 503, then the server exits for Docker to restart |
| `ANTHROPIC_IP_RANGES` | `160.79.104.0/21,153.61.208.0/20` | Anthropic's outbound ranges (empty: normal limit) |
| `OPENAI_IP_RANGES_FILE` | `data/platform_ranges/openai-chatgpt-connectors.json` | OpenAI's [ChatGPT connectors list](https://openai.com/chatgpt-connectors.json), refreshed at image build (empty: normal limit) |
| `MCP_ALLOWED_HOSTS` | `pcbparts.dev` | Accepted Host headers, comma-separated (localhost always works) |
| `DISTRIBUTOR_DAILY_LIMIT` | `1000` | Daily requests to each of Mouser and DigiKey (`0`: kept answers only) |
| `DISTRIBUTOR_DAILY_PER_ADDRESS` | `200` | Mouser and DigiKey lookups per address per UTC day, combined (`0`: off) |
| `DISTRIBUTOR_QUOTA_PATH` | `/app/cache/distributor_quota.json` in Docker | Mouser/DigiKey daily counts and pauses |
| `USAGE_STATS_PATH` | `/app/cache/usage_stats.json` in Docker | `/mcp/stats` counts |
| `LOG_PATH` | set in Docker; else empty | Application log file, kept across deploys (empty: none) |
| `LOG_KEEP_DAYS` | `7` | Days of log files to keep |
| `EASYEDA_STORE_PATH` | `/app/cache/easyeda.db` in Docker | EasyEDA footprint answers |
| `CSE_STORE_PATH` | `/app/cache/cse.db` in Docker | SamacSys searches and KiCad files |
| `DISTRIBUTOR_STORE_PATH` | `/app/cache/distributor.db` in Docker | Mouser/DigiKey answers and lifecycle readings |

The `_PATH` settings keep that data across restarts; outside Docker they're unset, data stays in memory and logs go only to the console. The compose files mount a named volume at `/app/cache`. An unusable or out-of-range number falls back to its default or nearest allowed value, with a warning at startup.

## API

- **Endpoint:** `https://pcbparts.dev/mcp`, Streamable HTTP (stateless), no auth
- **Rate limit:** 300 requests a minute per IP or IPv6 /64; 1,000 for Anthropic's and OpenAI's published connector ranges
- **Health:** `https://pcbparts.dev/health`: version, caches, distributor quotas and database status as JSON; HTTP 503 when a database call is stuck
- **Usage stats:** `https://pcbparts.dev/mcp/stats`: anonymous daily counts of tool calls, outcomes, upstream requests and refusals (the endpoint lists every field). No IPs, queries or part numbers are kept.

## Privacy

The hosted server at pcbparts.dev needs no account and sets no cookies. It uses tool arguments only to answer each call, and uses IP addresses for rate limiting and in server logs; part numbers and search text, never your IP, go to the parts providers it queries. Links in its answers, such as datasheet links, go straight to those providers' sites. The [privacy policy](https://pcbparts.dev/privacy.html) covers what is kept, for how long, and who it is shared with. A self-hosted copy is covered by whoever runs it.

## More

- [llms.txt](https://pcbparts.dev/llms.txt): this service described for LLMs, with the defaults and limits they need
- [CHANGELOG.md](CHANGELOG.md): every version; minor versions are also published as [GitHub releases](https://github.com/Averyy/pcbparts-mcp/releases). Minor releases in 0.x can change replies, and each lists what to check under **Breaking**.
- [CONTRIBUTING.md](CONTRIBUTING.md): development setup, tests and project conventions. Issues and PRs welcome.
- License: MIT
