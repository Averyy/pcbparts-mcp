# Contributing to pcbparts-mcp

Thanks for your interest! This project is MIT-licensed and welcomes issues and pull
requests. It powers a live hosted service ([pcbparts.dev/mcp](https://pcbparts.dev/mcp))
with real users, so the bar is: working code, tests, and no silent behavior changes.

## Before you start

- **For anything non-trivial, open an issue first** and describe the problem and your
  proposed approach. A short design discussion up front saves rework on both sides.
  Bug reports with a repro (tool call + arguments + actual vs. expected output) are gold.
- **Keep PRs small and focused.** One concern per PR, split into logical commits.
  [#4](https://github.com/Averyy/pcbparts-mcp/pull/4) is a model contribution: clear
  root-cause analysis, independently testable commits, before/after repro, tests.

## Development setup

Requirements: Python 3.12+ and [uv](https://docs.astral.sh/uv/) (never pip directly).

```bash
git clone https://github.com/Averyy/pcbparts-mcp.git
cd pcbparts-mcp
uv venv && uv pip install -e ".[dev]"
```

The SQLite databases are build artifacts (gitignored) generated from the committed
data files. They build automatically on first use, or explicitly:

```bash
uv run python scripts/build_database.py     # components.db (~730 MB, ~20s)
uv run python scripts/build_sensor_db.py    # sensor.db
uv run python scripts/build_boards_db.py    # boards.db
```

Run the server locally:

```bash
uv run python -m pcbparts_mcp.server        # http://localhost:8080/mcp
```

## Testing

```bash
uv run pytest tests/ -v                     # unit tests (default) — must be green
uv run pytest tests/ -v -m quality          # board-quality checks
uv run pytest tests/ -v -m integration      # integration tests (hit live APIs)
uv run pytest tests/ -v -m ""               # everything
```

- **The full unit suite must pass before you open a PR.**
- CI (`.github/workflows/tests.yml`) builds the databases and runs the unit suite on
  Linux and Windows for every PR, plus an explicit board-quality gate. Windows catches what Linux/macOS hide, so pass
  `encoding="utf-8"` to every text-mode `open()`/`read_text()`/`write_text()` (Windows
  defaults to cp1252) and use `as_posix()` when a path becomes a string key.
- Integration tests hit live JLCPCB/EasyEDA/distributor APIs. They can flake from
  residential IPs (WAF challenges) and burn API quotas — they are *not* required for
  PRs; maintainers run them before releases.
- EasyEDA blocks an IP from `/api/products` after about 24 requests in a short window, and
  one integration run sends about 20. Don't send other EasyEDA traffic for 3 minutes before or
  after a run. If the EasyEDA tests start failing with 403, stop and wait instead of
  re-running them: heavy traffic during a block appears to make it last much longer. See
  `docs/ref-easyeda-api.md`.
- `scripts/build_easyeda_seed.py` builds the EasyEDA footprint seed (`data/easyeda/footprints.csv`).
  Maintainers run it at home; don't run it alongside integration tests, and don't send a PR that
  regenerates the CSV unless asked.
- Bug-fix PRs should include a regression test that fails on the code before your fix.
- **Never test changes against the live server** (`pcbparts.dev`) — it runs the deployed
  code, not yours. Test locally against your built databases.

## Component scraper publication and local verification

The existing component scraper collects results and retries privately in
`<output>/.scrape-staging/`. It generates history only after every subcategory succeeds,
then validates and publishes the prepared files. An incomplete/tripped run exits nonzero
and leaves the published categories, subcategory map, manifest and history unchanged.
Use `--resume` with the same `--output` directory to load the staging progress and partial
records. A fresh run without `--resume` discards that directory and starts again.

Validation rejects remaining failed subcategories, invalid/inconsistent totals, a total
count drop over 5%, or a drop over 30% in a category that previously held at least 1,000
parts. `ALLOW_PART_DROP=true` deliberately bypasses the count-drop thresholds only;
it cannot bypass failed subcategories or invalid counts. The workflow passes its explicit
manual override to both the scraper and the same shared pre-commit validation helper.

Publication uses atomic file replacements and rolls completed replacements back on an
I/O error, retaining staged output. This does not claim a single filesystem transaction
or crash/power-loss recovery across all files. Run one scraper per output directory.

Local regression commands (no live scrape):

```bash
uv run pytest tests/test_component_publication.py tests/test_history.py -q
uv run pytest tests/test_do_now_20261108.py -q
```

For the 0.8.23 changes, local tests replay real catalog records and inject
transport/publication failures to verify success, retry, resume, rollback and the absence
of false history events. A full end-to-end scrape against JLCPCB **has not been run**.
A separate paced verification into an isolated output directory remains outstanding; these local tests do not establish live API pagination or completeness.

## Project conventions (read this — these are the review blockers)

**HTTP clients**
- All scraping and all JLCPCB/EasyEDA traffic goes through
  [wafer](https://pypi.org/project/wafer-py/) (`wafer.AsyncSession` /
  `wafer.SyncSession` — see `client.py` or `scripts/scrape_components.py` for proper
  config). Quick test scripts with raw `httpx`/`requests`/`aiohttp` against JLCPCB will
  get 403-blocked and can burn the shared IP reputation.
- Plain `httpx` is fine for clean REST APIs (Mouser, DigiKey).
- Note wafer's timeout semantics: session-level `timeout=` is a **total budget** across
  retries and rotations; pair it with `attempt_timeout=` to cap individual attempts.
  Unpaired, one hanging request eats the whole budget and the retries never fire — this
  failed a sensor scrape and blocked a deploy on 2026-08-01. Sensor scrapers get this
  from `scripts/scrapers/common.py`: use `make_session(request_timeout)` for sessions and
  `attempt_cap(total)` on one-shot `wafer.get`/`wafer.post` calls rather than hand-rolling.

**Behavior and errors**
- **Never change the semantics of a successful response** without discussing it in an
  issue first. Fixing a bug ≠ removing or redefining behavior.
- MCP tools return errors as dicts (`{"error": "..."}`), never raise user-facing
  exceptions — raised exceptions are masked to a generic message in production.
- A new or reworded error message also needs sorting for the usage stats
  (`/mcp/stats`): list it in `ERROR_REPLIES` in `tests/test_usage_stats.py` as
  `not_found`, `bad_request`, `rate_limited` or `failed`, and add a pattern to
  `_ERROR_KINDS` in `server.py` if none matches. The test names any message you missed.
- Library types are domain-critical: `basic`/`preferred` avoid the extended-type loading fee in Economic assembly. `extended` has a per-type fee; the savings calculator labels its rounded legacy $3 Economic assumption as an estimate, not a quote. Standard service differs.
- JLCPCB API gotcha: `firstSortName` is the **subcategory** and `secondSortName` is the
  **category**. Counterintuitive but verified; the client maps this correctly.

**Parametric filters**
- Range operators (`<`, `<=`, `>`, `>=`) on a spec field only work if the field has a
  numeric parser registered in `SPEC_PARSERS` (`src/pcbparts_mcp/alternatives.py`).
  Parsers live in `src/pcbparts_mcp/parsers.py` and need unit tests
  (see `tests/test_parsers.py`).
- A new unit in a parser must leave every value that already parsed unchanged (main's
  parsers vs yours over every attribute value in `components.db`): the database columns,
  search filters and alternatives all use them.

**Smart query parsing** (`src/pcbparts_mcp/smart_parser/`)
- A value in a query goes to the spec its part type lists (`CATEGORY_ATTRIBUTE_MAP`, keyed by
  keyword or subcategory name; give an operator when `>=` is wrong, as for a zener's voltage).
  `jlc_search` checks that at least 10% of the searched parts list the spec, tries a fallback
  (`_PARSED_FILTER_FALLBACKS` in `server.py`), or leaves the value out and says so in
  `parsed.adjusted_filters`. "5V relay" used to filter on Voltage Rating and find nothing.
- Alias targets and `SUBCATEGORY_GROUPS` members must be real subcategory names; a test checks.
- Check a parser change against a set of real queries before and after (`tests/test_search_queries.py`
  has the ones that broke).

**Alternatives rules** (`COMPATIBILITY_RULES` in `alternatives.py`)
- Keys and spec names must be JLCPCB's exactly ("Peak Pulse Power Dissipation (Ppp)",
  not "Peak Pulse Power"). A misspelled spec is never compared, and nothing fails: the
  check just lands in `specs_unparseable`. Copy names from `jlc_search_help(subcategory=...)`.
  A test checks every key against `data/subcategories.json`.

**Dependencies**
- All dependencies are pinned to exact versions (pyproject.toml, Dockerfile, and the
  scrape workflows must stay in sync). Don't loosen pins. Bumping a pin requires the
  full test suite plus a Docker build, and a note in the PR about what changed.

**Data**
- Everything under `data/` is machine-generated by the scrapers and refreshed by CI —
  don't hand-edit it. Databases (`data/*.db`) are gitignored build artifacts.
- Design-rule content (`data/design-rules/rules/`) must follow
  `data/design-rules/rules/DESIGN-STYLE-GUIDE.md`.
- If you change the landing page (`landing/index.html`), mirror the change in
  `landing/llms.txt`.

## Pull request checklist

1. Fork, create a feature branch off `main`, and rebase on latest `main` before opening
   (the daily scraper commits data to `main` every day).
2. Full unit suite green locally.
3. Tests included for any behavior change; regression test for bug fixes.
4. Bump the **patch** version in `pyproject.toml` (maintainer will adjust to
   minor/major if warranted) and add a `## X.Y.Z (YYYY-MM-DD)` entry to `CHANGELOG.md`.
   Reuse the current version and combine entries while changes remain unreleased.
   Merging publishes a GitHub release with that entry as its notes. Docs-only changes
   don't need a bump.
5. Match the existing code style; add comments only where the code can't speak for
   itself (constraints, gotchas — not narration).
6. PR description: what, why, and for bug fixes a before/after repro.
7. First-time contributors: CI workflow runs need maintainer approval — that's a GitHub
   safety default, not a review judgment.

## Reporting security issues

Please use GitHub's private vulnerability reporting ("Security" tab → "Report a
vulnerability") instead of a public issue.
