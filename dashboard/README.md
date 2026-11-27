# PCB Parts dashboard

A private dashboard backed by SQLite. It collects PCB Parts MCP statistics,
retains daily detail indefinitely, and serves the frontend and `/api/data`.
Python 3.12 or newer and `uv` are required.

The page, top to bottom: "Worth a look" (failures, requests or lookups turned away by
limits, service errors), headline numbers with a 14-day trend, then Traffic, Tools, Apps,
Reasons, Services we call, Limits and queues, Popular search words, and Deploys, restarts
and new apps (with a scorecard per server version). Ranges are Today (compared with yesterday
at the same Eastern wall-clock time) or whole Eastern days ending yesterday. Every number
covers the selected range; where the range crosses the latest deploy, problem counts also
say how many came since that version.

Notices in "Worth a look" can be dismissed. Dismissals live in the dashboard's own database
(table `dismissals`), so they hold on every device: each notice has a stable key (its kind
and subject, such as `per_ip_refusals`, `failed:cse_get_kicad:cse_lookup_failed` or
`held_back:digikey:distributor_refused`), and a dismissal records the Eastern day of the data
shown and the notice's count on that day. A dismissed notice comes back once something new
happens after the dismissal, in the selected range: more of it later that day, or any of it on a
later day; a notice with a new key always shows. "Show dismissed" lists the hidden ones, and
each dismissal can be undone. Live state (a failed update, an unhealthy server, stats or
budget counts not kept across restarts) can't be dismissed: it clears itself.

The Traffic problems chart's tooltip lists, under Failed, which tools failed and why in that
hour, and the rejected arguments by tool: from the differences between the dashboard's own
hourly checks (`hour_problems` on each Eastern day). Across a missed check the breakdown covers
the hours between checks and says so; a day rebuilt from daily totals has totals only. Days
with more than seven in the range show each day's own breakdown. Pointer, touch and the arrow
keys all reach the tooltip, and the Table view lists the same breakdown.
All calendar days use `America/New_York`, including 23/25-hour DST days. What it tracks and why:
`docs/research.md`. Running it on the PCB Parts server: `docs/deploy.md`.

Mouser daily-limit refusals are informational: lookups retry hourly or just after
the next daily reset. Mouser limit replies count as 429 regardless of HTTP status and are excluded from
the HTTP error warning; their own notices remain. Mouser HTTP outcomes start in
0.10.9, so all recorded 4xx errors still contribute to the warning. The services table
keeps the recorded counts. Held-back lookups remain warnings.
Other Mouser refusals and all DigiKey refusals remain warnings. From server 0.10.9,
the services table includes Mouser HTTP outcomes, and its error notice includes
recorded retries over the same problems window. Older days need neither field.
From server 0.10.11, DigiKey's lookups and requests are shown split between its API
and ext (`distributors.digikey.ext_sent` and the `digikey_ext` source).
Older days keep their single DigiKey figure; the split is never estimated for them.
From server 0.10.12 the page also reads each day's server starts (`starts`), distinct
address counts (`addresses`), ext's own holds and refusals (`ext_held_back`,
`ext_refusals`) and each budget in `distributor_quota.<name>.budgets`; days and samples
without them read as before. A service's error answers are shown quietly when no lookup
tied to that service failed (they were resent or answered another way).

```sh
uv sync --extra dev
uv run pcbparts-dashboard serve
uv run pcbparts-dashboard collect --days 365
uv run pcbparts-dashboard import /path/to/mcp-stats_2026-11-21_1417-EST.json
```

`uv run python -m pcbparts_dashboard` accepts the same commands. `serve` prints
its URL (normally `http://127.0.0.1:8050`); use `--host`, `--port`, or `--no-poll`
to override serving options. The installed commands resolve settings and data
relative to the checkout's `pyproject.toml`, even when run from another working
directory. From outside the checkout, use `uv run --project dashboard ...` from the pcbparts-mcp repo root.

Set `STATS_TOKEN` in the environment or in a git-ignored `secrets.local` file in
the project root. That file accepts `KEY=VALUE` lines, optional surrounding quotes,
blank lines, and whole-line `#` comments. Environment variables take precedence,
including explicit empty values. The server can start without a stats token;
collection then records an error visible in the dashboard.

| Setting | Default | Meaning |
| --- | --- | --- |
| `STATS_TOKEN` | unset | Required to collect stats |
| `STATS_URL` | `https://pcbparts.dev/mcp/stats` | Stats endpoint |
| `HEALTH_URL` | `https://pcbparts.dev/health` | Public health endpoint |
| `DASHBOARD_DB` | `data/dashboard.db` | Absolute path or relative to the project root |
| `POLL_MINUTES` | `60` | Poll interval; values below 5 are rejected |
| `DASHBOARD_HOST` | `127.0.0.1` | Bind address |
| `DASHBOARD_PORT` | `8050` | HTTP port |
| `DASHBOARD_PASSWORD` | unset | HTTP Basic auth password |
| `DASHBOARD_USER` | `admin` | HTTP Basic auth username |
| `PROBLEMS_SINCE` | automatic | ISO timestamp with timezone; explicit problems-window cutoff |
| `PROBLEMS_VERSION` | automatic | Version label for the problems window |

Without a dashboard password the server only binds to loopback addresses.
With a password all requests except `GET /healthz` require Basic auth. For online
serving, terminate HTTPS at a reverse proxy so Basic auth travels over TLS.

Polling starts immediately, then follows UTC interval multiples offset by 30
seconds (`:00:30` each hour by default; `:00:30`, `:15:30`, `:30:30`, `:45:30` for 15 minutes).
Automatic collection requests 365 days initially and when the last successful
full fetch is more than 24 hours old; otherwise it requests 3 days.
`POST /api/refresh` collects immediately, or requests 365 days with `?full=1`;
a request a browser sends for another site gets 403.
`GET /api/dismissals` lists dismissed notices; `POST /api/dismissals` with JSON
`{"key", "count", "day"}` dismisses one, and `DELETE /api/dismissals?key=...` undoes it. Changes
need the same password, a same-origin request and an `X-Dashboard-Request: 1` header.
Without a password, requests whose `Host` isn't a loopback name (`localhost`, `127.x.x.x`,
`[::1]`, any port) get 403, so a page that resolves its own name to this computer can't use it.
Static URLs carry `?v=` and a hash of the static files (the page's own references and the
modules' imports), so browsers load new code after a deploy; versioned files are cached for
a year in the browser only (`private`), the page itself is checked every time.
Polling and refreshes share a lock and a 60-second cooldown; busy or rate-limited
refreshes return 429 with `retry_after` seconds. A poll inside the cooldown skips
that slot. CLI collection is a separate one-shot operation.

SQLite uses WAL, creates the database's parent directory, and sets the database
file mode to `0600`. Daily records are kept forever; a lower incoming call count
keeps the saved record and adds a warning (no warning when the reply is older than
the saved one, as with an imported file). Missing, null, or cleared detail fields
retain their saved values. Raw newest-day snapshots and health samples are pruned
after 45 days on successful collection. `days_stored` counts records processed,
including records preserved by the merge rules. Imports use Eastern time from
recognized filenames (including daylight saving time), or the file modification
time, and do not update live-fetch success metadata or prune imported history.

From server 0.10.9, quota counts, pauses and reset times come from authenticated `/mcp/stats`'s top-level
`distributor_quota` (current state, independent of the requested days). On a successful
health fetch the collector copies that poll's stats `distributor_quota` into the saved
health sample, replacing any public quota field. `/health` itself has no quota state.
The Mouser budget tile, pace chart and pause notes read this combined sample; older
stored health samples with counts still work. If the stats reply omits quotas, the new
health sample has no `distributor_quota` (a server before 0.10.9 keeps its own `/health`
field for that poll); a failed stats fetch ends the poll before health. A failed health
fetch keeps the previous sample and its timestamp, so fresh counts never make an old
health sample appear current.

`/api/data` returns `edays` (oldest first) and `compare_today` instead of the old
`days` and `compare` fields, plus `timezone`, `as_of`, `problems_since`,
`problems_version`, and `version_since: {version, since}` for the current health
version (null without a health version). `as_of` is the last successful fetch; an import-only store uses
its newest stored fetch time. Empty stores have `as_of: null`. Each Eastern day
includes UTC `start`/`end`, `hours_in_window`, `complete`, `partial_start`,
`partial_end`, `approx`, `exact_calls`, and a `problems` window. `partial_start`
marks the stub first Eastern day for exclusion from ranges/charts; `partial_end`
marks today. Counters are re-cut from UTC days and snapshots. Failures, refusals,
held-back distributor lookups and database waits follow their own hourly series;
other counters follow hourly tool calls. Recorded hourly bins determine their
family totals; missing bins use estimates and remain null in charts. Counters
are rounded once per window, with largest-remainder allocation keeping outcomes
and reason/refusal breakdowns consistent. `approx` means something was estimated;
`exact_calls` means the calls' hourly coverage needed no estimation (so both can
be true). Approximation belongs in the page's footer.

Complete days are saved in `eastern_days` before snapshot pruning. Saved estimates
are replaced when exact inputs arrive. Rows carry `rules_version` (currently 4);
older rules are recomputed when final UTC records and source snapshots for both
UTC days remain available, otherwise their saved counters and rule version remain.

Set `PROBLEMS_SINCE=2026-11-21T18:00:00Z` and `PROBLEMS_VERSION=0.10.5` to count
problems since the 1 PM EST deploy. Without an explicit cutoff, a successful
collection that observes a changed health version moves the problems window to
the last stored fetch that saw the old version, using its exact stats snapshot.
Without an old-version fetch it uses the first fetch of the new version.
The first observed version only establishes
the baseline; until a cutoff exists, problems cover the full day. `PROBLEMS_VERSION`
overrides the displayed version independently. A snapshot within 10 minutes after
the cutoff, before the first known fetch of the new version, is the exact problems
baseline: the 18:04 UTC snapshot for the configured 18:00 UTC deploy. Hourly lists
still start with the cutoff's hour and exclude events already in that baseline.
`version_since.since` uses the problems cutoff when the version labels match,
otherwise that version's first health fetch. From server 0.10.9, Mouser's daily
budget resets at 06:00 UTC (1 AM EST / 2 AM EDT); DigiKey's budget and per-address
allowances still reset at 00:00 UTC (7 PM EST / 8 PM EDT). The frontend reads Mouser's UTC reset hour from
`health.distributor_quota.mouser.resets_at` (copied from stats), falling back to 6 for older samples. Budget pace, health
sample freshness and reset redraws use these boundaries independently of Eastern
reporting days. Details: `docs/eastern-days-spec.md`, its overriding
`docs/eastern-days-spec-amendments.md`, and `docs/backend-spec.md`.

`secrets.local` and `data/` stay out of git. The frontend files are maintained
separately in `src/pcbparts_dashboard/static/`.

```sh
uv run --extra dev pytest -q -p no:cacheprovider
node --test tests/frontend/
```

The page's own arithmetic (`static/data.js`: range totals, comparisons) is checked by
`tests/frontend/data.test.mjs`, which the suite runs under Node when it is installed.

Tests use synthetic upstream fixtures, `httpx.MockTransport`, injected clocks, and
temporary databases. HTTP routing tests bind only to loopback on an ephemeral
port; they never contact the live PCB Parts service or sleep to test timing.
