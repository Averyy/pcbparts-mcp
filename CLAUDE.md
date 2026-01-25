# Claude Guidelines

## Before Starting Work

**Always run `git pull` first** - Your local repo may be out of date.

## Git Commit Rules

**NEVER commit without explicit written permission** - Only commit when the user explicitly asks with phrases like "commit this", "push these changes", or "git commit". Never assume permission to commit.

**NEVER add Claude attribution to commits** - Do not include "Co-Authored-By: Claude" or any other attribution.

**Always bump version on commits** - Update the `version` field in `pyproject.toml` (the `__init__.py` reads it automatically via `importlib.metadata`).

Use semantic versioning (MAJOR.MINOR.PATCH):
- **PATCH** (x.x.X): Bug fixes, minor tweaks
- **MINOR** (x.X.0): New features, improvements
- **MAJOR** (X.0.0): Major milestones, significant new functionality, or breaking changes

## Project Overview

MCP server for searching JLCPCB electronic components for PCB assembly. Searches 1.5M+ parts across 52 categories with real-time stock and pricing.

**Website:** https://jlcmcp.dev
**MCP Endpoint:** https://jlcmcp.dev/mcp
**Health Check:** https://jlcmcp.dev/health

## Critical Rules

- **NEVER create mock data** unless explicitly told to
- **NEVER replace existing code with simplified versions** - fix the actual problem
- **ALWAYS find root cause** - don't create workarounds
- Update existing files, don't create new ones unless necessary

## Web Fetching

**Use fetchaller instead of WebFetch** (no domain restrictions). If a dedicated MCP exists (GitHub, Slack, etc.), use that instead.

## Reddit Searching and Browsing

Use `mcp__fetchaller__browse_reddit` to browse subreddits, `mcp__fetchaller__search_reddit` to find posts, and `mcp__fetchaller__fetch` to read full discussions.

## API Notes

**IMPORTANT:** The JLCPCB API has quirky field names:
- `firstSortName` = **subcategory** (not first/primary)
- `secondSortName` = **category** (the primary category)

This is counterintuitive but verified through testing. The client handles this mapping correctly.

**TLS Fingerprinting:** JLCPCB uses TLS fingerprint detection. We use `curl_cffi` for browser impersonation (Chrome 131/133/136/142) to avoid rate limiting. Regular HTTP clients like `httpx` or `requests` get 403 errors after several rapid requests.

## Python Environment

Python is managed via **uv**.

```bash
# Create venv and install dependencies
uv venv
uv pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
.venv/bin/pytest tests/ -v

# Run unit tests only (no API calls)
.venv/bin/pytest tests/ -v -k "not Integration"

# Run integration tests (hits real API)
.venv/bin/pytest tests/ -v -k "Integration"
```

## Docker Deployment

```bash
# Build and run
docker compose up -d

# View logs
docker logs jlcpcb-mcp -f

# Test health
curl https://jlcmcp.dev/health
```

## Architecture

```
jlcpcb-mcp/
├── src/jlcpcb_mcp/
│   ├── __init__.py         # Version
│   ├── config.py           # Configuration, headers
│   ├── client.py           # JLCPCB API client (curl_cffi)
│   ├── server.py           # FastMCP server
│   ├── bom.py              # BOM generation and validation
│   ├── categories.py       # 52 categories + subcategories
│   └── key_attributes.py   # Key specs mapping (758 subcategories)
├── landing/                # Website at jlcmcp.dev
│   └── index.html
├── tests/
│   ├── test_client.py      # Client unit + integration tests
│   └── test_bom.py         # BOM unit + integration tests
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `search_parts` | Search components by keyword, category, filters, sorting |
| `get_part` | Get full details for a specific LCSC part code |
| `find_alternatives` | Find similar parts in same subcategory with library_type, package, and EasyEDA filters |
| `list_categories` | Get all 52 primary component categories |
| `get_subcategories` | Get subcategories for a category |
| `validate_bom` | Validate BOM parts, check stock/availability, calculate costs (no CSV) |
| `export_bom` | Generate JLCPCB-compatible BOM CSV with validation and cost calculation |
| `get_version` | Get server version and health status |

### EasyEDA Footprint Availability

`get_part` and `find_alternatives` include EasyEDA footprint availability:
- `has_easyeda_footprint`: `true`/`false`/`null` (null = unknown)
- `easyeda_symbol_uuid` and `easyeda_footprint_uuid`: UUIDs for EasyEDA editor links

Use `find_alternatives(has_easyeda_footprint=True)` to only get parts with EasyEDA footprints available.

### find_alternatives Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `lcsc` | string | LCSC part code to find alternatives for (e.g., "C82899") |
| `min_stock` | int | Minimum stock for alternatives (default: 100) |
| `same_package` | bool | Only return parts with the same package size |
| `library_type` | string | "basic", "preferred", "no_fee", or "all" (default) |
| `has_easyeda_footprint` | bool | Filter by EasyEDA footprint availability |
| `limit` | int | Max alternatives to return (default: 10, max: 50) |

**Cost optimization:** Use `library_type="no_fee"` to find basic/preferred alternatives that avoid the $3 extended part fee.

### search_parts Filters

- **query**: Keywords including attribute values (e.g., "10uF 25V", "100k 1%")
- **package/packages**: Single or multiple package sizes (OR logic for arrays)
- **manufacturer/manufacturers**: Single or multiple manufacturers (OR logic for arrays)
- **category_id/subcategory_id**: Filter by category from `list_categories`
- **library_type**: "basic", "preferred", "no_fee", "extended", or "all"
- **min_stock**: Minimum stock quantity (default: 50)
- **sort_by**: "quantity" (highest first) or "price" (cheapest first). Default: relevance

## Library Types

JLCPCB has three library types that affect assembly fees:

- **basic**: No extra fee - common parts in JLCPCB's standard library
- **preferred**: No extra fee - recommended parts with good availability
- **extended**: $3 per unique part - less common parts

Use `library_type="no_fee"` to search both basic and preferred parts (merged results).

## BOM Export Tools

`validate_bom` and `export_bom` generate JLCPCB-compatible BOMs from LCSC part numbers.

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

## Maintaining key_attributes.py

Maps 758 subcategories to their key attributes for search results. Attribute names MUST match exact API field names - use `get_part` to verify.

**Common API naming patterns:**
- **No space before parentheses** (most common): `Resolution(Bits)`, `Voltage - Supply(VCCA)`, `Output Frequency(Max)`
- **Exceptions with space**: `Resistance Value (Ohms)`, `Resolution (Bits)` (DDS/Touch Screen only)
- **Case sensitive**: some are lowercase (`type`, `output type`, `number of channels`)

**Attribute selection (max 5 per subcategory):**
- Prioritize electrical specs (voltage, current, tolerance, speed)
- Avoid `Operating Temperature` unless no better options exist
- Check what the API actually returns - some subcategories have sparse data

See `fix-component-attributes.md` for verification history and fix patterns.

## Common Development Tasks

```bash
# Reinstall package after code changes
uv pip install -e ".[dev]"

# Quick API test
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
