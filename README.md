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

- `jlc_search` covers parts with at least 10 in stock, from a snapshot taken daily (`data_as_of` in each reply). Its 1-piece prices are refreshed weekly (`prices_as_of`). `jlc_get_parts` reads the same snapshot for up to 50 parts at once, with every quantity price tier from the daily scrape (`price_tiers_as_of`), as does `jlc_get_part(mpn=...)`. Both also answer parts that have left the snapshot since 2026-11-12 (stock under 10, or no longer listed), with stock unknown, their last stock and the date they left, until a scrape lists them again; `jlc_search` never shows those. `jlc_get_part(lcsc=...)` and `jlc_stock_check` are live, and `jlc_stock_check` also reaches the rest of JLCPCB's 7M+ part catalog.
- For Economic assembly, **basic** and **preferred** parts avoid the extended-type loading fee. Alternatives savings use a rounded legacy **$3 estimate** per extended type, not a current quote; Standard assembly fees differ. `jlc_search` ranks basic and preferred parts first, and `library_type="no_fee"` keeps only those.
- Spec figures are JLCPCB's listings, and alternatives are checked against the catalog. Check the datasheet and pinout before you order.
- The Mouser and DigiKey daily limits are shared by everyone on pcbparts.dev. Their answers are kept 3 days per part and lifecycle readings 90 days, so repeat lookups cost no request. Self-host with your own keys to get your own limits.

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

Quantity price tiers come from `data/catalog/price_tiers.tsv.gz`, which isn't in git: each daily scrape publishes it as the `price-tiers` Actions artifact, kept 7 days. The GHCR image has them; a database or image built from a clone has the 1-piece prices only, unless you download the file first (it needs a GitHub login, `gh auth login`) and then build:

```bash
run=$(gh run list -R Averyy/pcbparts-mcp -w scrape-components.yml -b main -s success -L 1 --json databaseId -q '.[0].databaseId')
gh run download "$run" -R Averyy/pcbparts-mcp -n price-tiers -D data/catalog
```

Build recorded stock history with `uv run python scripts/build_history_db.py`. `JLCPCB_DATA_DIR` sets the data directory; `JLCPCB_HISTORY_DB_PATH` can override the history DB path. Only changes leaving stock at 1,000 or below are recorded; [llms.txt](https://pcbparts.dev/llms.txt) has the tool's limits.

Mouser keys are free from Mouser's API hub, and DigiKey client credentials from DigiKey's developer portal. `cse_get_kicad` downloads need a SamacSys ComponentSearchEngine account; `cse_search` works without one.

| Variable | Default | Description |
|----------|---------|-------------|
| `MOUSER_API_KEY` | — | Enables `mouser_get_part` (and `part_lifecycle`) |
| `DIGIKEY_CLIENT_ID`, `DIGIKEY_CLIENT_SECRET` | — | Enable `digikey_get_part` (and `part_lifecycle`) |
| `CSEARCH_USER`, `CSEARCH_PASS` | — | SamacSys login for `cse_get_kicad` |
| `HTTP_HOST` | `0.0.0.0` | Bind address: `127.0.0.1` or `::1` for localhost only, `::` for every IPv6 interface, or a specific IPv4 or IPv6 address. In Docker keep `0.0.0.0`: `docker-compose.yml` already publishes the port on 127.0.0.1 only, and a localhost bind inside the container can't be reached from outside it |
| `HTTP_PORT` | `8080` | Server port |
| `RATE_LIMIT_REQUESTS` | `100` | Requests per minute per IP |
| `PLATFORM_RATE_LIMIT` | `1000` | Requests per minute per IP for addresses in the AI platforms' published ranges (many users share each one) |
| `ANTHROPIC_IP_RANGES` | `160.79.104.0/21,153.61.208.0/20` | Anthropic's outbound ranges, comma-separated; empty gives them the normal limit |
| `OPENAI_IP_RANGES_FILE` | `data/platform_ranges/openai-chatgpt-connectors.json` | OpenAI's ChatGPT connectors list ([openai.com/chatgpt-connectors.json](https://openai.com/chatgpt-connectors.json)); the image build refreshes the committed copy; empty gives them the normal limit |
| `MCP_ALLOWED_HOSTS` | `pcbparts.dev` | Comma-separated Host headers to accept (DNS-rebinding protection; localhost always works) |
| `DISTRIBUTOR_DAILY_LIMIT` | `1000` | Daily request quota for each of Mouser and DigiKey |
| `DISTRIBUTOR_QUOTA_PATH` | `/app/cache/distributor_quota.json` in Docker | Keeps the day's Mouser/DigiKey counts and pauses across restarts |
| `USAGE_STATS_PATH` | `/app/cache/usage_stats.json` in Docker | Keeps the `/mcp/stats` counts across restarts |
| `EASYEDA_STORE_PATH` | `/app/cache/easyeda.db` in Docker | Keeps EasyEDA footprint answers across restarts |
| `CSE_STORE_PATH` | `/app/cache/cse.db` in Docker | Keeps SamacSys searches and KiCad files across restarts |
| `DISTRIBUTOR_STORE_PATH` | `/app/cache/distributor.db` in Docker | Keeps Mouser/DigiKey answers (3 days) and lifecycle readings (90 days) across restarts |

These five cache and statistics paths are unset outside Docker, which keeps that data in memory only. The compose files mount a named volume at `/app/cache`.

## API

- **Endpoint:** `https://pcbparts.dev/mcp`, Streamable HTTP (stateless), no auth
- **Rate limit:** 100 requests a minute per IP; 1,000 for addresses in Anthropic's and OpenAI's published ranges (claude.ai and ChatGPT connectors), which many users share
- **Health:** `https://pcbparts.dev/health` (version, cache sizes, each distributor's requests today)
- **Usage stats:** `https://pcbparts.dev/mcp/stats`, anonymous daily counts of calls per tool and per hour, apps and Mouser/DigiKey lookups (including historical DigiKey keyword retries from before 0.9.3), and why calls found nothing or failed: one label a call from a fixed list (`reasons`), plus how the checks behind an empty search went (`why_empty`), requests sent to JLCPCB, LCSC, EasyEDA and SamacSys and the answers caches gave instead (`upstream`), Mouser/DigiKey part numbers asked in total and distinct (`parts_asked`), and requests the per-IP rate limit turned away (`per_ip_refusals`). No IPs, queries or part numbers are kept.

## Privacy

The hosted server at pcbparts.dev needs no account and sets no cookies. It uses tool arguments only to answer each call, and uses IP addresses for rate limiting and in server logs; part numbers and search text, never your IP, go to the parts providers it queries. Links in its answers, such as datasheet links, go straight to those providers' sites. The [privacy policy](https://pcbparts.dev/privacy.html) covers what is kept, for how long, and who it is shared with. A self-hosted copy is covered by whoever runs it.

## More

- [llms.txt](https://pcbparts.dev/llms.txt): this service described for LLMs, with the defaults and limits they need
- [CHANGELOG.md](CHANGELOG.md): every release, also published as [GitHub releases](https://github.com/Averyy/pcbparts-mcp/releases) from 0.8.21. Minor releases in 0.x can change replies, and each lists what to check under **Breaking**.
- [CONTRIBUTING.md](CONTRIBUTING.md): development setup, tests and project conventions. Issues and PRs welcome.
- License: MIT
