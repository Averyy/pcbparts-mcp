# Claude Guidelines

## Before Starting Work

**Always run `git pull` first** - Your local repo may be out of date.

## Git Commit Rules

- **GET LATEST FIRST** github actions runs automatically to commit new parts
- **NEVER commit without explicit permission** only commit when user explicitly asks ("commit this", "push these changes")
- **NEVER add Claude attribution** - No "Co-Authored-By: Claude" or similar
- **Always bump version** in `pyproject.toml` (PATCH/MINOR/MAJOR per semver, ask permission before bumping major/minor, patch is the default)

## Critical Rules

- **NEVER test changes using the live MCP** undeployed code changes NEEDS to be tested locally via the database
- **ALWAYS use wafer** when testing JLCPCB API - use `wafer.AsyncSession` with proper config (see `client.py` or `scrape_components.py`). Don't write quick test scripts with raw httpx/aiohttp - you'll get 403 blocked.
- **EasyEDA `/api/products` is rate-limited per IP**: measured at 24 requests, then a bare CloudFront 403 with no `Retry-After` that clears in about 2 minutes (2026-10-09). Stay under 20 requests per 2 minutes. Since 0.5.6 the client enforces that per process (budget and cooldown in `_check_easyeda_footprint()`), but the budget is per client instance (the server has one; each integration test class has its own), so test runs and anything else running at the same time add up. On the first EasyEDA 403, STOP sending. Don't re-run tests or retry by hand: heavy traffic during a block appears to stretch it from ~2 minutes to over 30. Check prod with one `jlc_get_part` instead. Details and numbers: `docs/ref-easyeda-api.md`.
- **EasyEDA footprint seed** (`data/easyeda/footprints.csv`): built by `scripts/build_easyeda_seed.py` on your own machine only, never on prod or in CI, and never while integration tests run (both use your IP's EasyEDA limit). It paces search at one request per 10s and `/api/products` at one per 15s, waits 10 minutes after search traffic before any `/api/products` step (search counts toward that endpoint's block), stops on the first 403 and resumes on the next run. Since 0.6.0 the server also keeps live footprint answers in a SQLite store on the `pcbparts-cache` volume. Details: `docs/ref-easyeda-api.md`.
- **Mouser and DigiKey limits are shared by everyone using pcbparts.dev**: Mouser allows 30 requests a minute and 1,000 a day per API key; DigiKey 120 a minute and 1,000 a day per DigiKey app (resetting at 00:00 UTC), and its API User Agreement suspends an app for 10 minutes (403s) for going over its per-second threshold, and can end the agreement after three suspensions. Prod used up DigiKey's day on 2026-10-16 while its in-memory counter kept resetting on restarts. Since 0.6.1: counts and pauses are kept in `DISTRIBUTOR_QUOTA_PATH` on the `pcbparts-cache` volume, we cap Mouser at 25 and DigiKey at 100 a minute, a limit refusal pauses that distributor until its reset (DigiKey: 429, or 403 for 10 minutes; Mouser: 403 or 429 with `TooManyRequests` in the body, until 00:00 UTC then hourly, since Mouser doesn't say when it resets), the limit errors tell users to self-host with their own key, and an hourly log line lists the top caller IPs. Since 0.6.3 DigiKey requests go out at most 5 a second (a burst waits) and DigiKey "not found" answers are cached for 10 minutes (found parts for the hour). Check `/health` (`distributor_quota`) before testing with the prod credentials.
- **ALWAYS pair wafer `timeout=` with `attempt_timeout=`** - `timeout` is a TOTAL budget across all retries/rotations, not a per-attempt cap. Unpaired, one hanging request eats the whole budget and retries never fire (this failed a sensor scrape and blocked a deploy on 2026-08-01). Sensor scrapers: use `make_session()`/`attempt_cap()` from `scripts/scrapers/common.py`.

## Library Types (Quick Reference)

- **basic/preferred** = no assembly fee
- **extended** = $3 per unique part type

## Project Overview

PCB Parts MCP server for electronic component search and sensor recommendation. See README.md for full tool documentation.

- **Sensor feature:** `sensor_recommend` tool — separate SQLite DB (`sensor.db`) from components. 14 scrapers produce `data/sensors/*.json`, merged by `scripts/build_sensor_db.py`, runtime at `src/pcbparts_mcp/sensor_db/`. Scraper reference: `docs/ref-sensor-scrapers.md`.

- **Design rules:** `get_design_rules` tool — 41 markdown reference files in `data/design-rules/rules/`, organized by category (guides, interfaces, power, protection, mcus, misc). Substring match on `category/filename`. Any edits to rule files must follow `data/design-rules/rules/DESIGN-STYLE-GUIDE.md`.

- **Website:** https://pcbparts.dev
- **Endpoint:** https://pcbparts.dev/mcp
- **Status:** Beta with real external users (self-hosters + hosted MCP + outside contributors) — breaking changes must be deliberate: semver bump, changelog note in the commit, and keep exact dependency pins

## Usage Stats

`/mcp/stats` (under `/mcp` because Caddy forwards only `/mcp*` and `/health`) serves anonymous daily counts from `stats.py`: per-tool calls = ok + not_found + bad_request + rate_limited + failed, calls per UTC hour, apps, distinct callers, Mouser/DigiKey lookups. The file (`USAGE_STATS_PATH` on the cache volume) keeps 365 days; the page shows 30. Error replies are sorted by `_ERROR_KINDS` in `server.py`; every error message must be listed in `ERROR_REPLIES` in `tests/test_usage_stats.py` (the test enforces it). Keep it same-origin: if another site ever needs it, allow that domain only, never `*`.

## API Gotcha

The JLCPCB API has backwards field names:
- `firstSortName` = **subcategory** (not first/primary)
- `secondSortName` = **category** (the primary category)

This is counterintuitive but verified. The client handles this mapping correctly.

## Development

```bash
uv venv && uv pip install -e ".[dev]"
.venv/bin/pytest tests/ -v                    # unit tests only (default)
.venv/bin/pytest tests/ -v -m integration     # integration tests (hits live APIs)
.venv/bin/pytest tests/ -v -m ""              # all tests
```

## Frontend & Design Work

**Always use the `/frontend-design` skill** for any frontend or design tasks (landing page, UI components, styling). Read `docs/branding-style-guide.md` before making any visual changes — it defines the PCB-inspired design language, color palette, typography, and component patterns.

## llms.txt

When updating the landing page (`landing/index.html`) with new features, tools, or setup instructions, also update `landing/llms.txt` to match. The llms.txt file is the LLM-readable version of the landing page content (tools list, setup instructions, feature descriptions, etc).

## Testing Local Changes

**The MCP tools in Claude Code connect to the deployed server (pcbparts.dev), not your local code.** Test local changes before deployment. Always git pull/fetch and then re-build the local database if its more than a day old.
