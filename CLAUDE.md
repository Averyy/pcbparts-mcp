# Claude Guidelines

Rules and gotchas only. History goes in `CHANGELOG.md`; how things work goes in the code and `docs/ref-*.md`.

## Before starting work

- Run `git pull` first: GitHub Actions commits new parts data daily.
- Check issues and PRs once a day (`gh issue list --repo Averyy/pcbparts-mcp --state open`, `gh pr list ...`) and mention anything new, even when the task is unrelated.
- Reproduce a reported bug locally before fixing it, and test the fix with the reporter's inputs.
- Reference the issue in the commit and `CHANGELOG.md` (`Fixes #17`).
- Don't comment on, label or close issues or PRs without the user's go-ahead; draft the reply instead.

## Commits and releases

- Never commit without explicit permission. Never push, merge or deploy without the user.
- No Claude attribution in commits or PRs.
- One version for all unreleased work; bump only after that version has been released. Bump in `pyproject.toml` and `uv.lock`. Patch is the default; ask before a minor or major bump.
- `CHANGELOG.md`: head the entry `## X.Y.Z (YYYY-MM-DD)` (the `release` job publishes that section as the GitHub release; without it the job fails). Short bullets of one or two lines under `### Breaking`/`Added`/`Changed`/`Fixed`: no paragraphs, rationale or measurements. Client-visible changes go under Breaking.
- Don't create releases or tags by hand.
- The project is in beta with real external users and contributors: breaking changes must be deliberate, and dependency pins stay exact.

## Commands

```bash
uv venv && uv pip install -e ".[dev]"
uv run pytest tests/ -q -p no:cacheprovider     # unit tests (default)
uv run pytest tests/ -v -m integration          # hits live APIs: see the rules below first
uv run python scripts/build_database.py         # rebuild data/components.db (about 30 s)
```

Python runs through `uv`, never pip.

## Testing

- The MCP tools in Claude Code talk to the deployed server, not local code. Never test undeployed changes through the live MCP: test locally, and rebuild the local database if it's more than a day old.
- Tests must pass on the Windows CI runner: no wall-clock timing (inject a fake clock), `encoding="utf-8"` on text reads and non-ASCII writes, close SQLite connections before deleting their files, short test ids, no `bash` from a test. `tests/test_windows_safe.py` enforces the first two.
- After a merge, watch `main`'s own Tests run too: it runs against newer scrape data.
- Catalog-backed tests must survive stock changes (skip or adapt when a recorded part is no longer stocked).

## Rules that protect outside services

- **JLCPCB:** use `wafer.AsyncSession` configured as in `client.py`; raw httpx/aiohttp gets 403s. Always pair wafer's `timeout=` (a total budget) with `attempt_timeout=`. Sensor scrapers use `make_session()`/`attempt_cap()` from `scripts/scrapers/common.py`.
- **EasyEDA `/api/products`:** stay under 20 requests per 2 minutes per IP. On the first 403, stop sending: don't retry or re-run tests. Details: `docs/ref-easyeda-api.md`.
- **EasyEDA seed scripts** (`scripts/build_easyeda_seed.py`, `scripts/build_easyeda_pads.py`): run on your own machine only, never on prod or in CI, and never while integration tests or the other seed script run.
- **Mouser and DigiKey:** their daily limits are shared by everyone using pcbparts.dev. Never call them from tests or probes. Check `/health` (`distributor_quota`) before any test with the prod credentials. DigiKey suspends an app that goes over its per-second threshold.
- Don't run `scripts/load_test.py` against anything but a local container.

## Rules for limits and refusals

- A refusal at normal load is a bug. Prefer making a caller wait to refusing it.
- Never add or tune a limit, cap or queue threshold from the synthetic load test alone: its traffic has neither prod's slow searches nor its bursts. Check prod's `/mcp/stats` (`per_ip_refusals`, `refused_hours`) after any limiter change.
- 429 bodies keep the JSON `retry_after` field: clients read it.
- Keep uvicorn's `proxy_headers=False`: otherwise callers' IPs could land on every access-log line.
- Refused IPs appear only in the hourly log lines; stats stay anonymous (counts only, no IPs, queries or part numbers).

## Data rules

- `data/catalog/price_tiers.tsv.gz` stays out of git: never `git add -f` it.
- Don't hand-edit `data/catalog/sold_out/*.jsonl` (a malformed row fails the scrape and the image build); `scripts/backfill_sold_out.py` rebuilds them. Nothing that reads `components` (search, counts, alternatives) may see the `sold_out` table.
- Sensor corrections go in `data/sensors/curated.json`, per field with evidence, and always win over scraped data: fix a general cause in the scraper or build rule instead. `scripts/build_sensor_db.py` runs alone in the Docker image, so it must not import other `scripts/` modules.
- Edits to design-rule files follow `data/design-rules/rules/DESIGN-STYLE-GUIDE.md`.
- The daily scrape is started by a cron job on the server; GitHub's schedule is only a backup. See `docs/ref-scrape-schedule.md`.

## Code rules

- Every error message a tool returns must be listed in `ERROR_REPLIES` (`tests/test_usage_stats.py`), with a reason for not-found and failed ones (`tests/test_usage_reasons.py`).
- A new upstream request or cache must be counted for `/mcp/stats` (`_sent()`/`_count_upstream()`; `tests/test_usage_upstream.py`).
- Tool docstrings: only the first text section and `Args` reach clients (`tests/test_release_0817.py`). They are sent on every session: keep them short.
- A code path that queues many `run_db` jobs at once should batch them into one.
- `/mcp/stats` stays same-origin; if another site ever needs it, allow that domain only, never `*`.
- Don't do server-side work the calling AI can already do (for example downloading or parsing PDFs).

## Gotchas

- The JLCPCB API's field names are backwards: `firstSortName` is the **subcategory**, `secondSortName` the **category**. The client maps them.
- `basic` and `preferred` parts have no extended-type loading fee for Economic assembly; `extended` parts are charged per unique type. The alternatives calculator's $3 figure is a rounded estimate, not a quote.
- Prod's container logs are lost at every deploy; `/mcp/stats` survives.

## Docs

- `landing/llms.txt`: every fact an AI needs to use the MCP (tools, arguments, defaults, limits, reply fields) as a terse reference, and nothing else. Update it when a release changes any of those.
- `README.md` is a high-level overview; query rules go in `docs/search-guide.md`.
- Reference: `docs/ref-server-internals.md` (limits, stored data, stats), `docs/ref-easyeda-api.md`, `docs/ref-sensor-scrapers.md`, `docs/ref-scrape-schedule.md`.
- The deferred backlog is `docs/do-later.md`, intentionally uncommitted.
- Frontend or design work: use the `/frontend-design` skill and read `docs/branding-style-guide.md` first.

## Project

PCB Parts MCP server: electronic component search (JLCPCB snapshot plus live lookups, Mouser, DigiKey), sensor recommendation, reference boards and design rules. Site https://pcbparts.dev, endpoint https://pcbparts.dev/mcp.
