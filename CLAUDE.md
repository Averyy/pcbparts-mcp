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
- **ALWAYS use wafer** when testing JLCPCB API - use `wafer.AsyncSession` with embed="xhr" and proper config (see `client.py` or `scrape_components.py`). Don't write quick test scripts with raw httpx/aiohttp - you'll get 403 blocked.

## Library Types (Quick Reference)

- **basic/preferred** = no assembly fee
- **extended** = $3 per unique part type

## Project Overview

PCB Parts MCP server for electronic component search and sensor recommendation. See README.md for full tool documentation.

- **Sensor feature:** `sensor_recommend` tool — separate SQLite DB (`sensor.db`) from components. 14 scrapers produce `data/sensors/*.json`, merged by `scripts/build_sensor_db.py`, runtime at `src/pcbparts_mcp/sensor_db/`. Scraper reference: `docs/ref-sensor-scrapers.md`.

- **Design rules:** `get_design_rules` tool — 41 markdown reference files in `data/design-rules/rules/`, organized by category (guides, interfaces, power, protection, mcus, misc). Substring match on `category/filename`. Any edits to rule files must follow `data/design-rules/rules/DESIGN-STYLE-GUIDE.md`.

- **Website:** https://pcbparts.dev
- **Endpoint:** https://pcbparts.dev/mcp
- **Status:** Beta - breaking changes acceptable (no external users yet)

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
