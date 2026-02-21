# Claude Guidelines

## Before Starting Work

**Always run `git pull` first** - Your local repo may be out of date.

## Git Commit Rules

- **GET LATEST FIRST** github actions runs automatically to commit new parts
- **NEVER commit without explicit permission** only commit when user explicitly asks ("commit this", "push these changes")
- **NEVER add Claude attribution** - No "Co-Authored-By: Claude" or similar
- **Always bump version** in `pyproject.toml` (PATCH/MINOR/MAJOR per semver, ask permission before bumping major/minor, patch is the default)

## Critical Rules

- **NEVER blame external services** (Claude, Anthropic, Google, Reddit, etc.) for issues. If something isn't working, the problem is in THIS codebase. Investigate our code first, add logging, and find the real cause. Blaming external parties wastes time.
- **NEVER test changes using the live MCP** undeployed code changes NEEDS to be tested locally via the database
- **NEVER create mock data** unless explicitly told to
- **NEVER replace existing code with simplified versions** - fix the actual problem
- **ALWAYS find root cause** - don't create workarounds
- **ALWAYS fix or note pre-existing issues** - if you discover failing tests or bugs unrelated to your current task, fix them or flag them to the user. Never dismiss them as "pre-existing"
- **Update existing files** - don't create new ones unless necessary
- **ALWAYS use proper TLS fingerprinting** when testing JLCPCB API - use `curl_cffi` with browser impersonation, proper headers, jitter delays, and user agents from `scrape_components.py`. Don't write quick test scripts that skip these - you'll get 403 blocked.

## Library Types (Quick Reference)

- **basic/preferred** = no assembly fee
- **extended** = $3 per unique part type

## Project Overview

PCB Parts MCP server for electronic component search. See README.md for full tool documentation.

- **Website:** https://pcbparts.dev
- **Endpoint:** https://pcbparts.dev/mcp
- **Status:** Beta - breaking changes acceptable (no external users yet)

## API Gotcha

The JLCPCB API has backwards field names:
- `firstSortName` = **subcategory** (not first/primary)
- `secondSortName` = **category** (the primary category)

This is counterintuitive but verified. The client handles this mapping correctly.

## Web Fetching

**CRITICAL: NEVER use WebFetch directly. ALWAYS use fetchaller first.**
Load via `ToolSearch("fetchaller")` then use `mcp__fetchaller__fetch`. It has no domain restrictions.
Add `raw: true` for raw HTML instead of markdown. If raw:true fails, use `curl` via Bash as fallback.
Only fall back to WebFetch if fetchaller fails entirely.
If a dedicated MCP exists (GitHub, Slack, etc.), use that instead.

## Reddit Searching and Browsing

Load via `ToolSearch("fetchaller")` first. Use `mcp__fetchaller__browse_reddit` to browse subreddits, `mcp__fetchaller__search_reddit` to find posts, and `mcp__fetchaller__fetch` to read full discussions.

## Development

```bash
uv venv && uv pip install -e ".[dev]"
.venv/bin/pytest tests/ -v                    # all tests
.venv/bin/pytest tests/ -v -k "not Integration"  # unit only
```

## Frontend & Design Work

**Always use the `/frontend-design` skill** for any frontend or design tasks (landing page, UI components, styling). Read `branding-style-guide.md` before making any visual changes — it defines the PCB-inspired design language, color palette, typography, and component patterns.

## llms.txt

When updating the landing page (`landing/index.html`) with new features, tools, or setup instructions, also update `landing/llms.txt` to match. The llms.txt file is the LLM-readable version of the landing page content (tools list, setup instructions, feature descriptions, etc).

## Testing Local Changes

**The MCP tools in Claude Code connect to the deployed server (pcbparts.dev), not your local code.** Test local changes before deployment. Always git pull/fetch and then re-build the local database if its more than a day old.
