# Claude Guidelines

## Before Starting Work

**Always run `git pull` first** - Your local repo may be out of date.

**Check GitHub issues and PRs in every session, at least once a day.** Run `gh issue list --repo Averyy/pcbparts-mcp --state open` and `gh pr list --repo Averyy/pcbparts-mcp --state open` before starting work and again on any day the session continues. Mention anything new to the user, even when the task is unrelated: users and contributors report real bugs there, and an issue may touch what you're changing.
- Reproduce a reported bug locally before fixing it, and test the fix with the reporter's own inputs.
- Reference the issue in the commit and `CHANGELOG.md` (`Fixes #17`), so merging closes it.
- Don't comment on, label or close issues or PRs without the user's go-ahead; draft the reply instead.

## Git Commit Rules

- **GET LATEST FIRST** github actions runs automatically to commit new parts
- **NEVER commit without explicit permission** only commit when user explicitly asks ("commit this", "push these changes")
- **NEVER add Claude attribution** - No "Co-Authored-By: Claude" or similar
- **Use one version for all unreleased work**: reuse and consolidate the current unreleased entry; bump only when starting work after that version has been released. **Bump version** in `pyproject.toml` and `uv.lock` (PATCH/MINOR/MAJOR per semver, ask permission before bumping major/minor, patch is the default), and add an entry to `CHANGELOG.md` with client-visible changes under **Breaking**. Head it `## X.Y.Z (YYYY-MM-DD)`: after the deploy, the `release` job in `docker-build.yml` publishes GitHub release `vX.Y.Z` with that section as its notes (no section, failed job). Don't create releases or tags by hand.

## Critical Rules

- **NEVER test changes using the live MCP** undeployed code changes NEEDS to be tested locally via the database
- **ALWAYS use wafer** when testing JLCPCB API - use `wafer.AsyncSession` with proper config (see `client.py` or `scrape_components.py`). Don't write quick test scripts with raw httpx/aiohttp - you'll get 403 blocked.
- **EasyEDA `/api/products` is rate-limited per IP**: measured at 24 requests, then a bare CloudFront 403 with no `Retry-After` that clears in about 2 minutes (2026-10-09). Stay under 20 requests per 2 minutes. Since 0.5.6 the client enforces that per process (budget and cooldown in `_check_easyeda_footprint()`), but the budget is per client instance (the server has one; each integration test class has its own), so test runs and anything else running at the same time add up. On the first EasyEDA 403, STOP sending. Don't re-run tests or retry by hand: heavy traffic during a block appears to stretch it from ~2 minutes to over 30. Check prod with one `jlc_get_part` instead. Details and numbers: `docs/ref-easyeda-api.md`.
- **EasyEDA footprint seed** (`data/easyeda/footprints.csv`): built by `scripts/build_easyeda_seed.py` on your own machine only, never on prod or in CI, and never while integration tests run (both use your IP's EasyEDA limit). It paces search at one request per 10s and `/api/products` at one per 15s, waits 10 minutes after search traffic before any `/api/products` step (search counts toward that endpoint's block), stops on the first 403 and resumes on the next run. Since 0.6.0 the server also keeps live footprint answers in a SQLite store on the `pcbparts-cache` volume. Details: `docs/ref-easyeda-api.md`.
- **EasyEDA pads seed** (`data/easyeda/pads.csv`, 0.9.5): footprint pads for `jlc_find_alternatives(land_compatible=true)`, collected by `scripts/build_easyeda_pads.py` on your own machine only (same rules as the footprint seed: never on prod or in CI, never alongside integration tests or `build_easyeda_seed.py`). One `/api/components` request per footprint every 2s by default, connectors only by default, most-stocked first; it stops on the first 403 and resumes on the next run. The first full run collected all 48,403 connector footprints (2026-11-17 12:18 PM to 2026-11-18 6:24 AM EST: one every 2 s, then every 1 s; no refusals). The server never re-fetches a footprint it has (seed or volume store), so refreshing is this script's job: `--refresh-days 90` re-fetches old rows and rewrites only those that changed. Details: `docs/ref-easyeda-api.md`.
- **Price tiers stay out of git** (`data/catalog/price_tiers.tsv.gz`, 0.10.0): each daily scrape writes every part's price breaks there, and `.gitignore` keeps it out of `git add data/catalog/` (never `git add -f` it: about 10 MB a day, kept forever). `scrape-components.yml` uploads it as the `price-tiers` artifact (7 days) before its push; `docker-build.yml` downloads the newest one from `main` before the image build. A missing or bad file never fails a build: replies then have `price_tiers_as_of: null` and the 1-piece price only. The weekly 1-piece `prices.tsv` stays in git, unchanged.
- **Mouser and DigiKey limits are shared by everyone using pcbparts.dev**: Mouser allows 30 requests a minute and 1,000 a day per API key; DigiKey 120 a minute and 1,000 a day per DigiKey app (resetting at 00:00 UTC), and its API User Agreement suspends an app for 10 minutes (403s) for going over its per-second threshold, and can end the agreement after three suspensions. Prod used up DigiKey's day on 2026-10-16 while its in-memory counter kept resetting on restarts. Since 0.6.1: counts and pauses are kept in `DISTRIBUTOR_QUOTA_PATH` on the `pcbparts-cache` volume, we cap Mouser at 25 and DigiKey at 100 a minute, a limit refusal pauses that distributor until its reset (DigiKey: 429, or 403 for 10 minutes; Mouser: 403 or 429 with `TooManyRequests` in the body, until 00:00 UTC then hourly, since Mouser doesn't say when it resets), the limit errors tell users to self-host with their own key, and an hourly log line lists the top caller IPs. Since 0.6.3 DigiKey requests go out at most 5 a second (a burst waits) and DigiKey "not found" answers are cached for 10 minutes (found parts for the hour). Since 0.9.3 an optional second DigiKey app (`DIGIKEY_CLIENT_ID_2`/`DIGIKEY_CLIENT_SECRET_2`) is used only after the first's day is spent, with burst limits, pauses and caches shared, and lookups are one keyword search each. Since 0.10.0 Mouser and DigiKey answers are kept per part number for 3 days (not found: a day), and every lifecycle status they state for 90 days (not listed or unknown: a week), in one SQLite store at `DISTRIBUTOR_STORE_PATH` on the volume (`distributor_store.py`; replies carry `observed_at`); a Mouser batch is kept part by part where its results can be matched to the numbers asked, concurrent one-part Mouser lookups share one request (100 ms window), and `part_lifecycle` answers BOMs from the store before asking either. Check `/health` (`distributor_quota`, `distributor_stored`) before testing with the prod credentials.
- **Per-IP limiter refusals** (visible since 0.10.0): `RateLimitMiddleware` counts each 429 in `/mcp/stats` (`per_ip_refusals`, per UTC day, no IPs, split by `_refusal_group()` into `platform_ranges` and `everyone_else`) and logs a `Per-IP rate limit refusals <hour> UTC: N from M IPs; top: …` line (the five most-refused IPs) for each hour that had any: `docker logs pcbparts-mcp 2>&1 | grep 'limit refusals'`. Those lines are the only place refused IPs appear, and they go with each deploy; the daily counts don't. uvicorn's access log still shows only Caddy's address (`172.18.0.2`) and Caddy keeps no access log: don't turn on uvicorn `proxy_headers`, which would put every caller's IP on every access-log line. Days before 0.10.0 show `per_ip_refusals: null`; while an older version runs, count its refusals since the last deploy with `docker logs pcbparts-mcp 2>&1 | grep -c '" 429'`. Plan for the limits: `todo-platform-rate-limits.md`. Since 0.10.0 `_limit_for()` gives addresses in the AI platforms' published ranges `PLATFORM_RATE_LIMIT` (1,000 a minute, chosen at about half of the VPS estimate from `scripts/load_test.py` (run against a local container only, 2026-11-18): about 9,000 requests a minute sustained on an Apple Silicon core at prod's limits, about 1,800 with the container's CPU cut to 0.33 to stand in for the VPS; re-measure before raising it) and every other address `RATE_LIMIT_REQUESTS` (100): Anthropic's two ranges are in `config.py`, OpenAI's list is `data/platform_ranges/openai-chatgpt-connectors.json`, which `docker-build.yml` replaces with a fresh, checked download on every build (falling back to the committed copy, never failing the build; `platform_ranges.py` is the check, standard library only). The server never downloads it. Also since 0.10.0 the limiter's replies carry `X-RateLimit-Limit/Remaining/Reset` and its 429s a counted-down `Retry-After` and a JSON body `{error, retry_after, reason, resets_at, tell_user}` (`reason` from `RATE_LIMIT_REASONS`; clients read `retry_after`: keep it). The check, the headers and the 429 all use `_limit_for()`.
- **ALWAYS pair wafer `timeout=` with `attempt_timeout=`** - `timeout` is a TOTAL budget across all retries/rotations, not a per-attempt cap. Unpaired, one hanging request eats the whole budget and retries never fire (this failed a sensor scrape and blocked a deploy on 2026-08-01). Sensor scrapers: use `make_session()`/`attempt_cap()` from `scripts/scrapers/common.py`.

## Library Types (Quick Reference)

- **basic/preferred** = no extended-type loading fee for Economic assembly
- **extended** = loading fee per unique part type; the alternatives calculator labels its legacy $3 Economic assumption as a rounded estimate, not a current quote (Standard service differs)

## Project Overview

PCB Parts MCP server for electronic component search and sensor recommendation. Tool docstrings document arguments and replies; README.md is a high-level overview (per-release detail goes in CHANGELOG.md, query rules in `docs/search-guide.md`).

- **Sensor feature:** `sensor_recommend` tool — separate SQLite DB (`sensor.db`) from components. 14 scrapers produce `data/sensors/*.json`, merged by `scripts/build_sensor_db.py`, runtime at `src/pcbparts_mcp/sensor_db/`. Hand corrections go in `data/sensors/curated.json`, per field with evidence (maker URL, page, quote); they always win over scraped data, so fix a general cause in the scraper or build rule instead and curate only per-record facts. The Docker image runs `build_sensor_db.py` from that file alone, so it must not import other `scripts/` modules (`tests/test_docker_build_scripts.py`). Scraper reference: `docs/ref-sensor-scrapers.md`.

- **Design rules:** `get_design_rules` tool — 46 markdown reference files in `data/design-rules/rules/`, organized by category (guides, interfaces, power, protection, mcus, misc). Exact normalized keys, aliases and token-boundary matching on `category/filename`, followed by scored text fallback. Any edits to rule files must follow `data/design-rules/rules/DESIGN-STYLE-GUIDE.md`.

- **Website:** https://pcbparts.dev
- **Endpoint:** https://pcbparts.dev/mcp
- **Status:** Beta with real external users (self-hosters + hosted MCP + outside contributors) — breaking changes must be deliberate: semver bump, changelog note in the commit, and keep exact dependency pins

## Usage Stats

`/mcp/stats` (under `/mcp` because Caddy forwards only `/mcp*` and `/health`) serves anonymous daily counts from `stats.py`: per-tool calls = ok + similar_only + not_found + bad_request + rate_limited + failed (alternatives: ok means verified alternatives found; similar_only means manual comparison candidates without verified replacements), calls per UTC hour, apps, distinct callers, Mouser/DigiKey lookups, plus why calls found nothing or failed (`reasons`: one label a call from the fixed `stats.REASONS` list, so a tool's labels add up to its not_found + failed) and how `why_empty` checks went. Since 0.10.0 also `upstream`: for each service other than Mouser/DigiKey (`stats.UPSTREAM_SOURCES`: JLCPCB, LCSC, three EasyEDA endpoints, SamacSys) the HTTP requests `sent` (not tool calls), wafer's own `retries`, `cached` answers and `rate_limited` (held back by our own budgets); counted with `_sent()`/`_count_upstream()` in `client.py` and in `cse.py`, so a new request or cache must be counted there too (`tests/test_usage_upstream.py` checks the names). `parts_asked`: part numbers looked up with Mouser/DigiKey, total and distinct by `mpn_key` (salted hashes in memory for the day, never written); and `per_ip_refusals` (above). The file (`USAGE_STATS_PATH` on the cache volume) keeps 365 days; the page shows 30. Error replies are sorted by `_ERROR_KINDS` in `server.py`; every error message must be listed in `ERROR_REPLIES` in `tests/test_usage_stats.py` (the test enforces it), and not_found and failed ones need a reason in `_NOT_FOUND_ERRORS` or `_FAILED_REASONS` (`tests/test_usage_reasons.py` enforces that). Keep it same-origin: if another site ever needs it, allow that domain only, never `*`.

## API Gotcha

The JLCPCB API has backwards field names:
- `firstSortName` = **subcategory** (not first/primary)
- `secondSortName` = **category** (the primary category)

This is counterintuitive but verified. The client handles this mapping correctly.

## Local backlog

Completed work is recorded in `CHANGELOG.md`. The local deferred backlog is `docs/do-later.md`, intentionally kept uncommitted.

## Development

```bash
uv venv && uv pip install -e ".[dev]"
uv run pytest tests/ -v                    # unit tests only (default)
uv run pytest tests/ -v -m integration     # integration tests (hits live APIs)
uv run pytest tests/ -v -m ""              # all tests
```

**Tests must pass on the Windows CI runner too**, which local macOS runs don't cover; a branch CI run catches failures that happen every time, not flaky ones. So: no wall-clock timing in tests (inject a fake clock; Windows clocks tick every ~15.6 ms), `encoding="utf-8"` on text reads and non-ASCII writes, close SQLite connections before deleting their files, keep test ids short, and don't run `bash` from a test (it starts WSL). `tests/test_windows_safe.py` enforces the first two.

## Frontend & Design Work

**Always use the `/frontend-design` skill** for any frontend or design tasks (landing page, UI components, styling). Read `docs/branding-style-guide.md` before making any visual changes — it defines the PCB-inspired design language, color palette, typography, and component patterns.

## llms.txt

`landing/llms.txt` holds every fact an AI needs to use the MCP (tools, arguments, defaults, limits, reply fields), and nothing else: no marketing, no changelog. Update it when a release changes any of those.

## Testing Local Changes

**The MCP tools in Claude Code connect to the deployed server (pcbparts.dev), not your local code.** Test local changes before deployment. Always git pull/fetch and then re-build the local database if its more than a day old.
