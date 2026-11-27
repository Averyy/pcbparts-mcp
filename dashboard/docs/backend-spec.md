# Backend spec

A small Python package that polls the PCB Parts MCP server's private `/mcp/stats` endpoint, keeps every day it has seen in SQLite, and serves one static dashboard page plus a JSON payload. Standard library plus `httpx` only. Runs locally now; later it will be served online behind a password.

## Upstream data

- `GET https://pcbparts.dev/mcp/stats?days=N` with `Authorization: Bearer <STATS_TOKEN>`. `N` is 1..365 (default 30). Reply: `{about, latency_bounds_ms, kept_across_restarts, distributor_quota, totals, days: [...]}`; `distributor_quota` is current state, independent of the requested days; `days` is newest first, one record per UTC day with a `date` key (`YYYY-MM-DD`). Counters are cumulative within a UTC day and the day rolls over at 00:00 UTC. The server keeps 365 days but clears `tool_apps`, `latency` and `popular_terms` (sets them to null or `{}`) on days older than 30, and compacts a past day's `tool_apps` to its 14 busiest apps plus `other`. A 401 means a bad token. The endpoint counts against a per-IP limit of 300 requests a minute, so never poll it more than once a minute.
- `GET https://pcbparts.dev/health` (public, no auth): `{status, version, database_pressure, snapshot, ...}`. Since 0.10.9 `/health` has no `distributor_quota`; distributor counts, pauses and reset times are private in `/mcp/stats`.
- Sample replies in `tests/fixtures/` are entirely synthetic: `mcp-stats_2026-11-21_1417-EST_sample.json` (0.10.5 format) and `health_sample.json` (a stored health sample, with `distributor_quota` as the collector copies it from stats). Keep the corresponding schema and internally consistent counters without copying production data. Never call the live endpoints from tests.

## Settings (`config.py`)

Environment variables win; otherwise read `KEY=VALUE` lines from `secrets.local` in the project root (git-ignored; `#` comments and blank lines allowed; never log its values).

| Name | Default | |
|---|---|---|
| `STATS_TOKEN` | none | required for collecting; serving without it works but the poller reports the error |
| `STATS_URL` | `https://pcbparts.dev/mcp/stats` | |
| `HEALTH_URL` | `https://pcbparts.dev/health` | |
| `DASHBOARD_DB` | `data/dashboard.db` (relative to the project root) | parent directory created, file mode 0600 |
| `POLL_MINUTES` | `60` | minimum 5 |
| `DASHBOARD_HOST` | `127.0.0.1` | |
| `DASHBOARD_PORT` | `8050` | |
| `DASHBOARD_PASSWORD` | unset | when set, every request needs HTTP Basic auth with this password |
| `DASHBOARD_USER` | `admin` | the Basic auth user name |
| `PROBLEMS_SINCE` | unset | explicit ISO timestamp with timezone for the problems window; normalized to UTC |
| `PROBLEMS_VERSION` | unset | explicit problems-window version label |

The project root is the directory holding `pyproject.toml` (find it from `__file__`), so the commands work from any cwd.

## Store (`store.py`, SQLite, WAL, one connection guarded by a lock)

Tables:
- `days(date TEXT PRIMARY KEY, data TEXT NOT NULL, fetched_at TEXT NOT NULL)`: one merged record per UTC day, kept forever.
- `snapshots(fetched_at TEXT PRIMARY KEY, date TEXT NOT NULL, data BLOB NOT NULL)`: the newest day record (`days[0]`) at every fetch, zlib-compressed JSON. Pruned after 45 days.
- `eastern_days(date TEXT PRIMARY KEY, data TEXT NOT NULL, approx INTEGER NOT NULL, computed_at TEXT NOT NULL, rules_version INTEGER NOT NULL)`: completed Eastern-day windows, retained after their source snapshots expire. A day is eligible only after every UTC day it touches has a final stored record (fetched at or after that UTC day's end). Current computations use rules version **2**. Opening an existing store adds the column and marks legacy rows version 1. Older-rule rows (including formerly exact rows and their problems subwindows) are recomputed if final UTC inputs and source snapshots for each contributing UTC day remain available; otherwise the saved row and its old rule version are retained. Within the current rules, saved day counters are reused unless an approximate result can become exact; the attached problems subwindow is refreshed separately when its cutoff changes or exact inputs become available.
- `health(fetched_at TEXT PRIMARY KEY, data TEXT NOT NULL)`: each `/health` reply with `distributor_quota` copied from the same poll's stats, when available. Pruned after 45 days.
- `meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)`: JSON values: `latency_bounds_ms`, `about`, `last_fetch` (`{at, ok, error, days_requested, status_code}`), `last_success_at`, `last_full_fetch_at`, `warnings` (list of the last 20 `{at, message}`), `seen_version`, `problems_since`, `problems_version`, `version_first_seen` (version to first health-fetch timestamp, retained across health pruning).

Times are ISO 8601 UTC with `Z`, to the second.

**Merging a fetched day into `days`** (the core rule; test every branch):
1. No stored record: insert the incoming one.
2. Incoming `calls` is lower than the stored `calls` (the server's stats file was reset or replaced): keep the stored record, add a warning naming the date and both counts. No warning when the incoming reply's `fetched_at` is older than the stored record's (an imported file): fewer calls is expected then.
3. Otherwise the incoming record wins, except: for each key of the stored record, keep the stored value when the incoming record lacks the key, or its value is `null`, or it is an empty `{}`/`[]` while the stored one is not empty. This keeps `tool_apps`, `latency` and `popular_terms` after the server clears them at 30 days.

## Collector (`collector.py`)

`collect(settings, store, *, days=None, client=None, now=None) -> dict` (inject `client` (an `httpx.Client`) and `now` for tests):
- `days`: if not given, 365 when there is no `last_full_fetch_at` or it is more than 24 hours old, else 3.
- GET stats with the bearer header, `timeout=httpx.Timeout(30.0)`, a `User-Agent: pcbparts-dashboard/0.1` header. Non-200, invalid JSON or a missing `days` list: record `last_fetch` with `ok: false` and a short error (status code and at most 200 characters of the body; never the token), return it, don't raise.
- On success: merge every day record, store `days[0]` as a snapshot, save `latency_bounds_ms` and `about`, set `last_success_at` (and `last_full_fetch_at` when `days >= 365`).
- Then GET health (same client, timeout 15 s); on 200, replace any public `distributor_quota` with the stats reply's field and store with the same poll timestamp. If the stats reply omits quotas (a server before 0.10.9), keep that poll's own `/health` field, if any. Older stored health samples with counts still work. On a health failure, retain the previous sample and its timestamp and note the failure in `last_fetch.health_error`; never combine fresh counts with old health.
- Record a nonempty health `version` in `seen_version`. The first observation only establishes the baseline. On subsequent changes, when `PROBLEMS_SINCE` is unset, set meta `problems_since` to the **last stored fetch whose health reported the old version**, with that fetch's stats snapshot as the exact baseline, and `problems_version` to the new version. If no old-version fetch remains, use the first fetch that saw the new version. An explicit cutoff suppresses automatic moves but still tracks `seen_version`; `PROBLEMS_VERSION` independently overrides the label in the payload. Failed collections or unavailable health versions do not move the window or become its baseline.
- Compute and persist eligible Eastern days, including their current problems windows, **before** pruning snapshots and health rows older than 45 days.
- Return `{ok, error, days_requested, days_stored, fetched_at}`.

`import_files(store, paths, *, settings=None)`: load saved stats replies (same JSON as the endpoint) and merge them like a fetch. When a file name matches `mcp-stats_YYYY-MM-DD_HHMM-EST*.json`, use that Eastern time (America/New_York, via `zoneinfo`) converted to UTC as `fetched_at`; otherwise the file's modification time. Store its `days[0]` as a snapshot too. Compute/upgrade eligible Eastern days using the newest stored input time after importing the batch. The CLI passes settings so configured problems cutoffs apply. Don't touch `last_success_at` or version tracking, and don't prune imported snapshots.

## Poller

A daemon thread started by `serve` (unless `--no-poll`): collect at start, then sleep until the next slot (every `POLL_MINUTES` minutes, aligned to UTC interval multiples plus 30 seconds: `:00:30` each hour for 60 minutes), collect, repeat. `next_poll_at` uses the same slots. Exceptions are logged and never kill the thread. The clock and sleep function are injectable for tests (no real waiting in tests).

## Payload (`payload.py`)

`build_payload(store, settings, now) -> dict`, served as `GET /api/data`:

```json
{
  "generated_at": "2026-11-21T19:20:00Z",
  "poll_minutes": 60,
  "next_poll_at": "2026-11-21T20:00:30Z",
  "last_fetch": {"at": "...", "ok": true, "error": null, "days_requested": 3, "status_code": 200, "health_error": null},
  "last_success_at": "...",
  "warnings": [{"at": "...", "message": "..."}],
  "latency_bounds_ms": [50, 100, 250, 500, 1000, 2500, 5000, 10000, 30000, 60000],
  "about": "...",
  "timezone": "America/New_York",
  "as_of": "2026-11-21T19:20:00Z",
  "edays": [ {"date": "2026-10-23", "start": "2026-10-23T04:00:00Z", "end": "2026-10-24T04:00:00Z", "hours_in_window": 24, "complete": true, "partial_start": false, "partial_end": false, "approx": true, "exact_calls": true, "problems": null, "...": "..."}, "... oldest first ..." ],
  "compare_today": {"date": "2026-11-20", "start": "2026-11-20T05:00:00Z", "end": "2026-11-20T19:20:00Z", "hours_in_window": 15, "approx": true, "exact_calls": false, "...": "window counters"},
  "problems_since": "2026-11-21T18:00:00Z",
  "problems_version": "0.10.5",
  "version_since": {"version": "0.10.5", "since": "2026-11-21T18:00:00Z"},
  "health": { },
  "health_at": "..."
}
```

- `edays`: every Eastern date from the Eastern date of the first stored UTC midnight through `as_of`'s Eastern date, **oldest first**. `eastern.py` implements `eastern-days-spec.md` with **`eastern-days-spec-amendments.md` taking precedence**. Days contain re-cut nested counters, hourly lists in window order, `start`, `end`, `hours_in_window`, `approx`, `exact_calls`, `date`, `complete`, `partial_start`, `partial_end`, and `problems`. The stub first day gets `partial_start: true` when it starts before the first stored UTC midnight; the frontend should exclude it from ranges and charts. Today has `partial_end: true` and `complete: false`. DST days have 23 or 25 hours. Partial/missing UTC inputs mark the day approximate. `callers` and per-distributor distinct parts are null; latency objects contain only histogram counts; tool averages use call-weighted durations; database wait maxima come from hourly maxima.
- `as_of`: `last_success_at`; for an import-only store, the newest stored stats fetch timestamp; null when there are no inputs. Empty stores return `edays: []` and `compare_today: null`. Request time affects `generated_at` and scheduling, not the data's calendar date.
- `compare_today`: a window from yesterday's Eastern midnight through the same Eastern wall-clock time as `as_of`, plus `date`; null if yesterday has no UTC inputs. Its last hourly bin is scaled to the elapsed fraction of that hour and rounded. A snapshot within 90 seconds makes a counter endpoint exact; scaling a historical partial hourly bin still makes `approx: true`, `exact_calls: false`.
- `problems_since` and `problems_version`: settings override meta independently. With no cutoff, problems cover each entire day. Otherwise each day's `problems` is the intersection of that day with the cutoff through `as_of`, or null if empty. At the cutoff, use the earliest snapshot at or within **10 minutes after** it, before the first fetch of the new version when known, as the exact baseline without interpolation. A snapshot exactly at the cutoff is also valid when it is the first new-version fetch (the automatic fallback). For `2026-11-21T18:00:00Z`, use the `2026-11-21T18:04:00Z` snapshot. The hourly lists keep the hour containing the configured cutoff as their first label; subtract events already recorded by the baseline from the affected bins, rather than counting them again. Cached partial problems windows are reused when their boundaries match, including after snapshot pruning.
- `version_since`: `{version, since}` for the newest health reply's version; null without a nonempty version. `since` equals `problems_since` when `problems_version` matches, otherwise the first stored fetch that saw that version. First-version observations are retained in meta so pruning does not move the header date.
- `days` and `compare` are no longer present. `next_poll_at` is null when polling is disabled.
- `health`: the newest stored health reply, including private quota detail from the same poll when available, or `null`. The Mouser budget tile and pace chart read its counts; pause notes and `mouserDayStartHour` read the pause and reset times copied from stats.

Interpolation and rounding:
- `at()` keeps fractional counters. Each family uses its own hourly share: `tools.<t>.failed` and the failure labels listed in the amendments use `failed_hours`; all `per_ip_refusals` counters use `refused_hours`; `distributor_limits.<d>.held_back.*` and `distributors.<d>.rate_limited` use that distributor's `held_back_hours`; `db_waits.waited` and `db_waits.components.waited` use their matching `waited_hours`. Everything else uses `hours` (tool call counts). A missing/null sibling in the interpolation span falls back to `hours`; zero or missing call volume falls back to elapsed time. A recorded sibling with zero events also uses elapsed time for an otherwise inconsistent counter delta.
- Window family totals use the sum of recorded sibling bins, including when nearby snapshots disagree. With partial coverage, add estimates for the missing bins; those chart entries remain null. Failure totals are shared across tools, held-back totals across causes, and refusal totals across groups. Fields absent/null in every source remain unknown.
- Round once after endpoint subtraction and addition across UTC days. Use largest remainder for the six tool outcomes against rounded calls, reasons against `not_found + failed`, and refusal groups against their total. Preserve known hourly failure totals first, then apportion the remaining tool outcomes; failure labels and not-found labels are balanced against their corresponding outcomes. Complete tool-call breakdowns are also apportioned against total calls, making room for recorded failures where needed. Held-back causes are balanced against their distributor's rate-limited total. Unknown partitions are not invented. Python nearest-even rounding applies to scalar totals and partial hourly bins; family totals agree with the finished chart's rounded bins. Tool averages retain precision: interpolate `avg_ms * calls` by **call share**, subtract durations, then divide by the fractional window calls (null when the finished call count is zero).
- `approx` is true when any interpolation, proportional bucket estimate, missing-day contribution or negative-counter clamp was needed. `exact_calls` separately means `hours` covers the full window without proportionally estimated bins; it can be true alongside `approx`. Legacy cached rows that cannot be upgraded default to `exact_calls: false`. The page should explain approximation once in its footer.

Boundary conventions: `hours_in_window` counts represented hourly bins (including a partial final hour). A live partial bucket is copied as recorded, not scaled again; only the historical comparison scales its ending bucket. Non-hour-aligned cutoffs without an exact problems baseline estimate their first bucket proportionally. An exact baseline removes its observed partial bucket; if its hourly list is missing, its family total and complete preceding bins can recover that bucket, otherwise proportional estimation is necessary. Wait maxima cannot be subtracted: retain the partial bucket's maximum, marking it approximate if it might still be the pre-baseline peak. A zero-length midnight window has zero counters, zero bins, null hourly fields, and no problems. The stored unfinished UTC record can supply the newest known point if its snapshot is unavailable; an earlier data horizon must use an available earlier snapshot, not later imported hourly bins. Yesterday uses `zoneinfo` calendar arithmetic: an ambiguous time uses the first occurrence, and a nonexistent spring-forward time normalizes forward by the DST gap.

From server 0.10.9, Mouser's daily budget resets at **06:00 UTC** (1 AM EST / 2 AM EDT), matching the default `MOUSER_DAY_START_HOUR`. The frontend reads the UTC hour from `health.distributor_quota.mouser.resets_at` (copied from stats; `YYYY-MM-DD HH:MM UTC`), falling back to 6 for old samples. DigiKey's budget and per-address allowances keep **00:00 UTC** (7 PM EST / 8 PM EDT). Eastern-day recutting does not move these resets; budget pace, health-sample freshness and scheduled redraws follow the respective boundary.

Mouser HTTP outcomes (`upstream_status.mouser`) also start in 0.10.9. Its limit replies already count as `429`, regardless of HTTP status: the frontend excludes those from the HTTP-error warning and shows their own refusal notices. All `4xx` outcomes still contribute to the HTTP-error warning; daily-refusal counts are never subtracted from them. The services table keeps the recorded counts.

From server 0.10.11, `distributors.digikey.ext_sent` counts the DigiKey lookups sent through ext, inside `sent` (API lookups are `sent - ext_sent`), and the `digikey_ext` upstream source holds ext's requests apart from `digikey` (the API's). The server writes `ext_sent` when it creates a UTC day's DigiKey counts; a day whose DigiKey counts it found without it (older days, the deploy day when DigiKey had counts before the start) has none, and that day's lookups are unsplit, though its ext requests after the deploy are already under `digikey_ext`. A server rollback below 0.10.11 drops the field, and the `digikey_ext` counts in `upstream` and `upstream_status`, from every stored day (copy `usage_stats.json` first), so days the collector fetches again after that come back unsplit and without ext's request counts (a stored day's top-level fields are replaced as a whole). A window keeps `ext_sent` only when no real record (snapshot or stored day, not the synthetic midnight zero) between its UTC parts' endpoints lacks it while the part sent lookups (`eastern.SENT_PATHS`); otherwise it is dropped and `sent` stays the single figure. The frontend splits per Eastern day (`digikeyPaths`): API and ext lookup rows only when the range had ext lookups; requests per lookup pairs each split day's `digikey` requests with its API lookups and each unsplit day's `digikey` plus `digikey_ext` requests with all its lookups, labelled per API lookup only when the range has no unsplit lookups; `digikey` is labelled "DigiKey API" unless the range includes unsplit lookups, in which case a note dates the split from the first day with `digikey_ext` traffic; an empty `digikey_ext` row is hidden.

## HTTP server (`server.py`, `http.server.ThreadingHTTPServer`)

- `GET /` and `GET /index.html`: `static/index.html`. `GET /static/<name>`: files from `src/pcbparts_dashboard/static/` only (reject `..`, absolute paths and anything that resolves outside it; 404 otherwise). Correct `Content-Type` for `.html .js .css .svg .png .woff2 .json`.
- `GET /api/data`: the payload as JSON, gzip-compressed when the request's `Accept-Encoding` allows it.
- `POST /api/refresh`: run `collect()` now (full when `?full=1`) and return its result. At most one refresh per 60 seconds and never concurrently with the poller's collect (share a lock); otherwise 429 with `{"error": ..., "retry_after": seconds}`. A cross-site browser request (`Sec-Fetch-Site` other than `same-origin`/`none`, or without that header an `Origin` whose host isn't the request's `Host`) gets 403 before anything runs: Basic auth credentials are sent with any request the browser makes.
- `GET /healthz`: `{"ok": true}` (no auth, for a future reverse proxy).
- Everything else: 404 JSON.
- Headers on every reply: `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, `Content-Security-Policy: default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'`. API replies add `Cache-Control: no-store`.
- Auth: when `DASHBOARD_PASSWORD` is set, every route except `/healthz` requires Basic auth (compare user and password with `hmac.compare_digest`), else 401 with `WWW-Authenticate: Basic realm="pcbparts dashboard"`. When it is unset, refuse to start unless the host is a loopback address (`127.0.0.1`, `::1`, `localhost`), with a clear message.
- Access logging: one short line per request to stderr (method, path without query, status); never log headers.

## CLI (`cli.py`, `python -m pcbparts_dashboard` too)

- `pcbparts-dashboard serve [--host H] [--port P] [--no-poll]`: prints the URL.
- `pcbparts-dashboard collect [--days N]`: one fetch, prints the result line (no token).
- `pcbparts-dashboard import FILE...`.

## Tests (pytest, no network, no real sleeping, no wall-clock timing)

Merge rules (all three branches and the empty/null cases), the `days` choice (365 vs 3), collector success and failure with `httpx.MockTransport` (the bearer header is sent; the token never appears in `last_fetch` or the return value), Eastern `at()`/window arithmetic and 90-second snapshot tolerance, per-family hourly placement and null fallback, authoritative hourly totals, rounding after subtraction/across UTC days and largest-remainder partitions, hourly/null/compaction/average rules, 23/25-hour DST days, partial-day flags and `exact_calls`, persistence before 45-day pruning and later exact upgrades, rules-version migration/recomputation/preservation, the ten-minute problems baseline and its version guard, last-old-version automatic cutoffs, header `version_since`, `compare_today` and partial hours, new payload shape and poll slots, the import file-name time parsing, static path traversal rejection, Basic auth (401 without it, 200 with it, `/healthz` open), the loopback refusal without a password, the refresh rate limit, gzip on `/api/data`. Run the server on port 0 in tests. Verify with `uv run pytest -q -p no:cacheprovider`.

## Files

`src/pcbparts_dashboard/{__init__.py,__main__.py,cli.py,config.py,store.py,collector.py,eastern.py,payload.py,server.py}`, `tests/...`, and a short `README.md` (setup with `uv sync --extra dev`, the three commands, settings table, where data lives, and that `secrets.local` and `data/` stay out of git). The frontend (`static/index.html`, `static/app.js`, `static/style.css`) is written separately: don't create or edit files in `static/`.
