# Claude Guidelines

## Before Starting Work

**Always run `git pull` first** - Your local repo may be out of date.

## Git Commit Rules

- **NEVER commit without explicit permission** - Only commit when user explicitly asks ("commit this", "push these changes")
- **NEVER add Claude attribution** - No "Co-Authored-By: Claude" or similar
- **Always bump version** in `pyproject.toml` (PATCH/MINOR/MAJOR per semver)

## Critical Rules

- **NEVER create mock data** unless explicitly told to
- **NEVER replace existing code with simplified versions** - fix the actual problem
- **ALWAYS find root cause** - don't create workarounds
- **Update existing files** - don't create new ones unless necessary
- **ALWAYS use proper TLS fingerprinting** when testing JLCPCB API - use `curl_cffi` with browser impersonation, proper headers, jitter delays, and user agents from `scrape_components.py`. Don't write quick test scripts that skip these - you'll get 403 blocked.

## Library Types (Quick Reference)

- **basic/preferred** = no assembly fee
- **extended** = $3 per unique part type

## Project Overview

MCP server for JLCPCB component search. See README.md for full tool documentation.

- **Website:** https://jlcmcp.dev
- **Endpoint:** https://jlcmcp.dev/mcp
- **Status:** Beta - breaking changes acceptable (no external users yet)

## API Gotcha

The JLCPCB API has backwards field names:
- `firstSortName` = **subcategory** (not first/primary)
- `secondSortName` = **category** (the primary category)

This is counterintuitive but verified. The client handles this mapping correctly.

## Web Fetching

Use **fetchaller** instead of WebFetch (no domain restrictions). Use dedicated MCPs for GitHub, Slack, etc.

## Reddit

Use `mcp__fetchaller__browse_reddit`, `mcp__fetchaller__search_reddit`, and `mcp__fetchaller__fetch`.

## Development

```bash
uv venv && uv pip install -e ".[dev]"
.venv/bin/pytest tests/ -v                    # all tests
.venv/bin/pytest tests/ -v -k "not Integration"  # unit only
```
