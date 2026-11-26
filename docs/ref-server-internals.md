# Server internals reference

Reference notes on how the server's limits, stored data and statistics work, moved out of `CLAUDE.md`
(which holds rules only). Read the section you need when working in that area; the code and its
comments are the source of truth, and `CHANGELOG.md` has the history.

## Call log, failed queries and popular terms (0.10.5)

`CALL_LOG_DIR` enables two private stores (`/app/cache/call-log` in Docker; empty disables both).
Neither is served over HTTP. Recording uses bounded memory on the event loop; the minute task
and shutdown write detached batches through `asyncio.to_thread`. Recording failures cannot
change a tool reply; each failure streak logs once. There are no extra upstream requests.

`calls-YYYY-MM-DD.jsonl` holds one JSON object per tool call: UTC time to the second (`t`), `tool`,
`outcome`, final stats `reason` or null, `bad_request_reason` or null, integer `ms`, cleaned `app`
or null, `platform` (the rate limiter's exact AI-platform ranges), and `shape`. An app name survives
only when its cleaned name exactly matches `call_log.WELL_KNOWN_APPS` (case-insensitive) or has reached 10 distinct
callers that UTC day when the batch is flushed; otherwise it becomes `other`. Well-known matches
use the list's canonical spelling, including `<Cursor>` and `Cursor!` becoming `Cursor` in both
stateless HTTP and sessions. Other names use the same casefolded, whitespace-normalized
form for both caller-threshold evidence and the written row. AI-platform addresses
share one caller, and other IPv6 addresses share a /48. At most 50 app names and 10 salted hashes
per name per day are tracked in memory, for at most two recorded dates. Older app hashes can remain
for delayed row flushes, and normal flush cleanup drops dates no longer needed;
a restart resets this evidence. The daily `apps`, `tool_apps` and `distributor_apps` counts are unchanged.
Shape contains declared argument names and, since 0.10.9, unrecognized argument names kept as
given (case preserved) only when they are 1–30 ASCII letters or underscores; all other unknown names
become `unknown_argument`. Argument values are never kept with these names. This applies
to rejected calls and unknown tools too; `/mcp/stats` still uses fixed labels such as
`arg:unknown_argument:unexpected_keyword_argument`. Shape also contains batch sizes, LCSC/MPN
input forms, bounded booleans/enums and catalog-checked category, subcategory, package and spec
attribute names. Argument names are sorted and de-duplicated. Shape lists keep at most
20 argument names, 10 packages and 20 spec names;
`args_omitted`, `packages_omitted` and `spec_filters_omitted` count any remaining entries.
Shape names are limited to 40 characters. Unknown packages/attributes become `other`. It contains
no query, part-number or manufacturer argument values, IPs or caller IDs. IDs take precedence over conflicting category names,
as in the tools. Batch shapes inspect at most 50 entries while retaining the total batch size;
tool notes or rejection replies avoid reparsing rejected JSON strings. Timestamps reuse one formatted
string per whole second. Limiter refusals are counted per UTC minute and `(reason, platform)` pair,
with `t` at the minute start, `refused`, `platform` and `count`. Only completed minutes are flushed
during normal operation; shutdown also flushes the current minute. Example call row:

```json
{"t":"2026-11-21T03:04:05Z","tool":"jlc_stock_check","outcome":"not_found","reason":"no_results_words","bad_request_reason":null,"ms":123,"app":"backplane-check","platform":false,"shape":{"args":["query"]}}
```

The buffer holds at most 20,000 rows and 8 MiB of conservatively accounted row memory, including
a batch being written. Accounting includes Python containers and strings; recording does no JSON
serialization. A worker serializes append payloads in chunks of at most 64 KiB, rolling back the
whole day's append to its starting offset on any write failure before retrying it. If rollback
also fails, that offset stays in memory: no further rows append to that file and it is not
compressed until the repair succeeds (expired files are still deleted). `CALL_LOG_MAX_ROWS` also caps
each UTC day's admitted rows at 1,000,000 (minimum 1); startup counts today's existing file so a
restart cannot reset the budget. A startup preparation failure suppresses new rows until a later
flush retries preparation successfully and restores the remaining budget. Excess rows are dropped and counted in memory, with one warning
per UTC day and the day's dropped count logged at rollover; failed-query counts continue independently.
At startup and the first flush of a new UTC day, expired files are deleted before remaining completed
JSONL days become `.jsonl.gz`, using a closed temporary gzip file and atomic replace. A failed file
does not prevent processing others. `CALL_LOG_DAYS` defaults to 30 (minimum 1), including today.
Only exact dated call-log and failed-query filenames are rotated/pruned. The directory is mode 0700;
all files written (including temporary/replacement files) are 0600, and startup repairs existing modes.
Startup deletes abandoned `calls-YYYY-MM-DD.jsonl.tmp`, `calls-YYYY-MM-DD.jsonl.gz.tmp` and
`failed-YYYY-MM-DD.json.tmp` files only (valid dates, regular files, no symlinks); rotation also
applies the corresponding call/failed retention to these temporary files by their filename date.
Before counting today's JSONL rows, startup removes an incomplete final line if the file does not
end in a newline, scanning backwards in bounded chunks. Its WARNING contains only the number
of bytes removed, never the discarded contents.

The complete shape whitelist is loaded in one background database job after readiness. Existing
`package_spellings` covers only translations, the search package map covers only pin-count families,
and the lazy attribute cache lacks original spellings. None supplies the complete whitelist. Until
the job finishes, package/spec shapes use `other` and unresolved category names are omitted; no
database read runs on the recording path. Startup logs the call-log directory and both retention
periods, or `Call log: off (CALL_LOG_DIR unset)`.

`failed-YYYY-MM-DD.json` holds distinct `(tool, reason, normalized text)` counts, sorted by
descending count. It records failed calls and genuine no-match calls; excludes
`stock_below_minimum`, `offset_past_end`, `not_sent` and `placeholder_mpn` not-found outcomes;
and includes individual misses inside successful batches (`row_not_found` or
`row_lookup_failed`). Mouser's `lookup_failed` list is included; part/lifecycle row errors use
`row_not_found` for missing parts and `row_failed` for failures, skipping invalid input and limit
errors according to the shared pure `tool_outcomes.py` classifier (also re-exported by `server.py`). Batch text comes from the original entry, including `mpn | manufacturer`
when supplied. Filter-only searches have no text to keep. Text is casefolded, stripped of
control/format characters, whitespace-collapsed and capped at 200 characters. Example:

```json
{"date":"2026-11-21","dropped":0,"queries":[{"tool":"jlc_stock_check","reason":"no_results_words","text":"unlisted sensor","count":3}]}
```

There is no IP, app, caller ID or time finer than the date in this store. `FAILED_QUERY_CAP`
defaults to 5,000 distinct entries per UTC day; subsequent new entries increment `dropped`,
while retained entries keep counting. Changed days are written atomically (temporary file,
flush, fsync, close, replace) each minute and at shutdown. Today's file is loaded on startup;
an unreadable file is left intact and retried. `FAILED_QUERY_DAYS` defaults to 7, including
today; both numeric settings have minimum 1.

`usage_stats.json` also gains `popular_terms` (null before 0.10.5). It counts individual query
tokens for `jlc_search`, `jlc_stock_check`, `cse_search`, `board_search` and `sensor_recommend`,
excluding `bad_request`. Micro signs become `u`, Ω becomes `ohm`, text is casefolded, delimiters
split tokens and edge punctuation is stripped. Tokens must be 2–40 characters; a small English
stop list is removed. Each query contributes at most 20 distinct tokens, once each. No phrases
are counted. A token needs 10 distinct callers that UTC day before any aggregate is persisted:
all AI-platform addresses count as **one** caller, other IPv6 addresses by /48. This is a popularity
heuristic, not an anonymity guarantee against someone controlling many addresses. The daily
random salt and up to 10 caller hashes per token exist only in memory (20,000 tokens maximum)
and reset on restart. Already-retained tokens retain their stored count plus new occurrences
after a same-day restart; below-threshold tokens must meet the threshold again. Save/summary
refreshes the top 200 eligible tokens, and summary totals sum retained daily counts and keep
the top 200. Like `tool_apps` and `latency`, this field is cleared after `RECENT_DAYS` (30 days).
`tool_apps` writes only nonzero outcomes plus `calls`; summaries still supply every outcome.
Stats saves cache each closed day's JSON, invalidating it on changes (including late calls,
compaction and 30-day clearing). Subsequent saves encode only today and changed closed days;
the resulting bytes remain identical to `json.dumps({"days": ...}, sort_keys=True)`.

For a container text report (tools/outcomes, top app/tool pairs, exact row-based nearest-rank
latency percentiles, reasons, refusals and the top 50 failed queries):

```text
docker exec pcbparts-mcp python /app/scripts/usage_report.py --date 2026-11-21
docker exec pcbparts-mcp python /app/scripts/usage_report.py --days 7
python scripts/usage_report.py --dir ./call-log --days 7
```

The standard-library script reads both JSONL and gzip files; dates default to today UTC.
Malformed call-log lines, including incomplete JSON or UTF-8, are skipped and their count is
reported as `Malformed call-log lines skipped`; valid lines still contribute to the report.
Copy files to a laptop for deeper DuckDB analysis, for example:

```sql
SELECT tool, outcome, count(*) AS calls
FROM read_json('calls-*.jsonl.gz')
WHERE tool IS NOT NULL
GROUP BY tool, outcome ORDER BY calls DESC;
```

With both refusal and call rows, use DuckDB's `union_by_name = true` option if combining files
whose inferred columns differ. Current-day rows are in `calls-*.jsonl` until rotation.

## EasyEDA `/api/products` rate limit

**EasyEDA `/api/products` is rate-limited per IP**: about one request per 14.3 s sustained with a reserve of about 7, then a bare CloudFront 403 with no `Retry-After` that clears in a few minutes (2026-11-22; it allowed 24 at once in October). Stay at one per 15 s and bursts of 5. Since 0.5.6 the client enforces a budget per process (5 per 75 s since 0.10.8) (budget and cooldown in `_check_easyeda_footprint()`), but the budget is per client instance (the server has one; each integration test class has its own), so test runs and anything else running at the same time add up. On the first EasyEDA 403, STOP sending. Don't re-run tests or retry by hand: heavy traffic during a block appears to stretch it from ~2 minutes to over 30. Check prod with one `jlc_get_part(lcsc=..., live=true)` instead. Details and numbers: `docs/ref-easyeda-api.md`.

## EasyEDA footprint seed

**EasyEDA footprint seed** (`data/easyeda/footprints.csv`): built by `scripts/build_easyeda_seed.py` on your own machine only, never on prod or in CI, and never while integration tests run (both use your IP's EasyEDA limit). It paces search at one request per 10s and `/api/products` at one per 15s, waits 10 minutes after search traffic before any `/api/products` step (search counts toward that endpoint's block), stops on the first 403 and resumes on the next run. Since 0.6.0 the server also keeps live footprint answers in a SQLite store on the `pcbparts-cache` volume. Details: `docs/ref-easyeda-api.md`.

## EasyEDA pads seed

**EasyEDA pads seed** (`data/easyeda/pads.csv`, 0.9.5): footprint pads for `jlc_find_alternatives(land_compatible=true)`, collected by `scripts/build_easyeda_pads.py` on your own machine only (same rules as the footprint seed: never on prod or in CI, never alongside integration tests or `build_easyeda_seed.py`). One `/api/components` request per footprint every 2s by default, connectors only by default, most-stocked first; it stops on the first 403 and resumes on the next run. The first full run collected all 48,403 connector footprints (2026-11-17 12:18 PM to 2026-11-18 6:24 AM EST: one every 2 s, then every 1 s; no refusals). The server never re-fetches a footprint it has (seed or volume store), so refreshing is this script's job: `--refresh-days 90` re-fetches old rows and rewrites only those that changed. Details: `docs/ref-easyeda-api.md`.

## Price tiers

**Price tiers stay out of git** (`data/catalog/price_tiers.tsv.gz`, 0.10.0): each daily scrape writes every part's price breaks there, and `.gitignore` keeps it out of `git add data/catalog/` (never `git add -f` it: about 10 MB a day, kept forever). `scrape-components.yml` uploads it as the `price-tiers` artifact (7 days) after the data commit and push and before it triggers the deploy, so a failed upload can't cost the day's commit and the build it starts finds this artifact; `docker-build.yml` downloads the newest one from `main` before the image build. A missing or bad file never fails a build: replies then have `price_tiers_as_of: null` and the 1-piece price only. The weekly 1-piece `prices.tsv` stays in git, unchanged.

## Sold-out parts

**Sold-out parts are committed** (`data/catalog/sold_out/YYYY-MM.jsonl`, 0.10.0): the scrape's output step (`update_sold_out()` in `scripts/scrape_components.py`) adds each part the previous catalog had and today's doesn't (after scrape-gap carry-over), with gone_since, and drops it when a scrape lists it again; no extra requests. `build_database.py` loads them into the `sold_out` table, which stays out of component search, counts, full-text search and alternatives, except 0.10.5's label-only lookup after an empty `jlc_search` part-number search. That lookup changes usage labels only, never the reply. Don't edit the files by hand (a malformed row fails the scrape and the image build); `scripts/backfill_sold_out.py` rebuilds them offline from the catalogs in git history.

## Mouser and DigiKey limits and stored answers

**Mouser and DigiKey limits are shared by everyone using pcbparts.dev**: Mouser allows 30 requests a minute and 1,000 a day; DigiKey 120 a minute and 1,000 a day per DigiKey app (resetting at 00:00 UTC), and its API User Agreement suspends an app for 10 minutes (403s) for going over its per-second threshold, and can end the agreement after three suspensions. Prod used up DigiKey's day on 2026-10-16 while its in-memory counter kept resetting on restarts. Since 0.6.1: counts and pauses are kept in `DISTRIBUTOR_QUOTA_PATH` on the `pcbparts-cache` volume, we cap Mouser at 25 and DigiKey at 100 a minute. DigiKey limit refusals pause until its reset (429), or for 10 minutes (403). Mouser sends until its API refuses the day (`TooManyRequests` / `MaxCallPerDay`), whatever our local daily count says (`0` still disables live lookups); Mouser's day runs from 06:00 to 06:00 UTC, as observed in its daily refusals and resumed requests. `MOUSER_DAY_START_HOUR` sets that UTC hour (default `6`, range `0`–`23`, read through `config.number_setting`; invalid values use `6` and add a startup warning to `CONFIG_WARNINGS`). Whether Mouser moves to 05:00 UTC during daylight saving time is unconfirmed. Daily refusals schedule a check at the next day start plus 60 seconds after a count of at least half the daily limit, or hourly but never later than the next day start plus 60 seconds for a lower count; the rules below also cover delayed replies. Per-minute refusals still pause all Mouser requests. The limit errors tell users to self-host with their own key, and an hourly log line lists the top caller IPs. Since 0.6.3 DigiKey requests go out at most 5 a second (a burst waits) and DigiKey "not found" answers are cached for 10 minutes (found parts for the hour). Since 0.9.3 DigiKey lookups are one keyword search each. Since 0.10.0 Mouser and DigiKey answers are kept per part number, and every lifecycle status they state, in one SQLite store at `DISTRIBUTOR_STORE_PATH` on the volume (`distributor_store.py`; replies carry `observed_at`): answers 3 days (DigiKey's found ones a day since 0.10.4); lifecycle readings 90 days, obsolete a year (since 0.10.4 active 60, `nrnd`/`last_time_buy` 30; `_ttl()`, which `prune()` follows); a Mouser batch is kept part by part where its results can be matched to the numbers asked, and `part_lifecycle` answers BOMs from the store before asking either. Numbers no distributor lists (values such as "10k", LCSC codes, placeholders, non-ASCII, not 3-40 characters: `search/mpn.py` `not_sent_reason`) are never sent. Check `/mcp/stats` (`distributor_quota`, with `Authorization: Bearer <STATS_TOKEN>`) and `/health` (`distributor_stored`) before testing with the prod credentials. Since 0.10.10, `extensions.py` loads an optional deployment-specific extension module (`pcbparts_extensions`) when one is installed; none ships with this repository, and without one the server behaves exactly as described here.

**Per-address daily cap (0.10.3):** an address has a shared allowance of 300 lookups a UTC day (1,000 in 0.10.5–0.10.9, 200 before) to Mouser and DigiKey together (`DISTRIBUTOR_DAILY_PER_ADDRESS`, `0` = off; one `AddressDailyQuota` shared by both pools, IPv6 by /64, AI-platform addresses exempt). At most 20,000 addresses, cleared by a new UTC day. Since 0.10.6, when `DISTRIBUTOR_QUOTA_PATH` is set, a graceful restart carries counts of at least 100 in the private `distributor_address_counts.json` beside it, using HMAC-SHA256 with a random per-day secret instead of raw addresses; the secret is in the same file, so the file could reveal IPv4 addresses to whoever reads it (it exists only from shutdown to the next startup, which deletes it). Otherwise counts stay in memory only; a crash still loses them. uvicorn waits at most 6 s for running requests (`timeout_graceful_shutdown`) so the shutdown that writes the file runs within Docker's 10 s stop timeout. `QuotaPool.acquire` checks it after stored answers and before the minute budget, only on the first attempt of a lookup. Only that first attempt counts toward the address allowance; retries and a follow-up for numbers crowded out of a capped Mouser reply don't count. The one-by-one fallback after a rejected batch still counts each separate request. A refusal counts as `held_back.address_daily`. Each distributor logs an hourly `<name> calls held back ...` line (every cause; since 0.10.6 every held-back address, split over continuation lines that each fit the file log's 2,000-character messages; `requests sent` lines keep the top five): `grep 'held back'`. Since 0.10.6 an address reaching the cap also logs one `Mouser and DigiKey per-address limit: <address> reached its 300 lookups for <date> at <HH:MM> UTC (first lookup <HH:MM> UTC)` line, once a day (the first-lookup time since 0.10.10; `(first lookup <HH:MM> UTC, since a restart at <HH:MM> UTC)` when the server started that UTC day, so earlier uncarried lookups are missing; `(first lookup before a restart)` when its count was carried over). Addresses that keep reaching the cap, and each one's days with cap and first-lookup times (same-time-every-day scripts stand out):

```bash
docker exec pcbparts-mcp sh -c 'grep -ah "per-address limit" /app/cache/logs/application.log*' | awk '{print $9}' | sort | uniq -c | sort -rn
docker exec pcbparts-mcp sh -c 'grep -ah "per-address limit" /app/cache/logs/application.log*' | awk '{s = $9 " " $15 " capped " $17; for (i = 19; i <= NF; i++) s = s " " $i; print s}' | sort
```

**Block list (0.10.10):** `DISTRIBUTOR_BLOCKED_ADDRESSES` (comma-separated addresses or CIDR ranges, set only in the operator's env file; a bare IPv6 address stands for its /64 as the cap counts it, an explicit prefix is kept (`/128`: one address), and IPv4-mapped entries become IPv4 networks; `CONFIG_WARNINGS` lines name an entry's position only: an invalid entry is skipped, one with host bits past its prefix blocks the whole network) makes `AddressDailyQuota` treat a matching caller as capped and never counted, even when it is exempt or the cap is off: no live Mouser or DigiKey request, stored answers still served, and the error says live lookups are turned off for the address; `retry_after` still points at 00:00 UTC, so the reply shape matches the cap's. Its refusals count as `held_back.address_blocked` and still go into the hourly `calls held back` lines; startup logs only how many ranges are blocked.

**Mouser day counts:** Mouser's daily count uses this boundary; DigiKey and the shared `AddressDailyQuota` still reset at 00:00 UTC. The stored `date` names the UTC date on which the Mouser day started. On upgrade, a matching date keeps its count; before the configured hour, today's old UTC-date label also keeps its count and is rewritten to the Mouser-day label. Older or future dates start at zero. Stored absolute pauses remain unchanged. Authenticated `/mcp/stats`'s `distributor_quota.mouser.used_today` follows this day; `paused_until` and retry/error times give the next try when live lookups are paused, including an in-flight check’s 60-second hold. The authenticated `/mcp/stats` `distributor_quota` includes `paused_until` (null when not paused) and `resets_at`, with times in `YYYY-MM-DD HH:MM UTC` format. Public `/health` has no `distributor_quota`; distributor state is private. `resets_at` gives the next configured Mouser day start, or 00:00 UTC for DigiKey. The dashboard copies the stats quota state into its saved health sample and reads the UTC hour from Mouser’s `resets_at` for its budget, sample freshness and reset redraws, falling back to 6 for old health samples.

**Mouser daily refusals:** `TooManyRequests` for the daily limit, or a bare HTTP 429 with `x-ratelimit-remaining: 0`, schedules the next try using the count snapshotted when the request was sent. At or above half the configured limit (`limit // 2`), it uses the next Mouser day start after the send plus 60 seconds (06:01 UTC by default). Below half the limit, it retries hourly but never later than the first day start plus 60 seconds at or after the send: a request sent at 06:00:20 can retry at 06:01 that same day. If the chosen time has already passed when the reply arrives, it uses one hour after the reply. A late refusal from a request sent before the current refusal was recorded does not change the schedule or log again. A late accepted reply from before that refusal cannot resume lookups either.

The first lookup after a next try becomes due sends a check and holds further checks for 60 seconds. Lookups whose next try fits within the remaining shared 30-second waiting budget, or that are waiting on an in-flight check, poll within that budget, including first attempts and retries. Checks awaiting replies are tracked in memory. A hold restored after a restart blocks another check until it expires; lookups wait for that expiry only when it fits the remaining budget. If no lookup can send when that wait ends, the existing daily-limit error reports the next try time. A readable accepted reply resumes normal use. Another daily refusal uses the count and send time of the new check to schedule its next try. An otherwise unexplained HTTP 401/403 during a check uses the same retry schedule, but counts as `refusals.refused` and upstream `4xx`, not `refusals.daily`. Per-minute refusals and non-daily bare HTTP 429s apply the shared minute penalty and release the hold. Invalid-key replies keep their existing separate handling. A transient or unclassified outcome (5xx, unreadable reply, network failure or cancellation) releases the hold immediately, allowing the lookup's own retry or the next lookup to check again. A reply taking longer than 60 seconds may overlap another check. A configured `DISTRIBUTOR_DAILY_LIMIT=0` still disables live Mouser lookups.

The quota file keeps recent refusal episodes (`daily_refusals`: `at`, our Mouser-day `count` then, `last_refused_at`, `retries`, `resumed_at`) in their existing format. Each newly handled daily refusal logs one WARNING with the reply time, count snapshotted at send and next try time. The first acceptance afterwards closes the episode and logs an INFO; startup lists the last five kept episodes. These lines contain no API key, address or part number. Refusal history never appears in `/health`, `/mcp/stats` or tool replies; authenticated `/mcp/stats` exposes current state in `distributor_quota`, with `paused_until` giving the next try when no lookup can send and `resets_at` the next Mouser day start.

A follow-up for numbers crowded out of a capped Mouser reply still counts as a send toward the minute budget, daily count and usage stats. If it is held back by a limit or fails, those numbers are listed in `not_checked` or `lookup_failed`, respectively, with the first reply's other results retained; they are not reported as `not_found` or kept as misses. If an answered reply is still capped, unmatched numbers stay in `not_found` without keeping misses.

**Mouser temporary failures (0.10.9):** HTTP 5xx (apart from limit or `Errors` replies), unreadable replies (non-JSON, not an object, or no `SearchResults.Parts` list and no usable `Errors`), and non-timeout transport failures retry the entire request up to twice, after 3 then 10 seconds. A 5xx `Retry-After` in seconds or HTTP-date form replaces that delay. There are at most 30 seconds of waiting per lookup, across its requests: the first request, a capped-reply follow-up and any one-by-one fallback. A retry delay that exceeds the remaining budget stops retries; a spent budget prevents further retries. Timeouts, 4xx, key rejections and Mouser `Errors` keep their existing handling, including one-by-one fallback for a rejected batch. Every send counts toward the minute budget, daily send count, hourly requests-sent tally and usage stats; only each request's first attempt checks and counts the address allowance: retries and a capped-reply follow-up don't, and each one-by-one request does. A retry or continued lookup held back only by our own minute cap waits for a slot within the same budget. Waiting for a nearby scheduled daily-reset check or an in-flight check also uses this budget, including on a first attempt; other quota holds return the existing limit result. Checks after daily refusals follow the 60-second hold and outcome rules above. Retries run inside the shielded fetch: cancelling a caller still lets the answer be kept per part and shared with `part_lifecycle`. Exhausted retries keep the existing error text.

The client-wide retry guard disables retries when the last five minutes contain at least 10 transient failures and at least 90% of attempts with an outcome failed transiently. It uses at most 31 ten-second buckets, retaining the oldest overlapping bucket. Cancelled attempts have no outcome; HTTP/API refusals and non-retried errors count in the denominator. Initial attempts continue. The guard is checked after outcomes and before every retry send, so an idle window can expire it. Entering logs one WARNING and leaving one INFO, each with failure and outcome counts.

`pcbparts_mcp.mouser` logs the first transient failure in each UTC minute at WARNING: HTTP status or exception class (never the exception text/URL), attempt number, planned retry and delay, `Retry-After`, `Server`, `Content-Type`, and body byte length. For 5xx only, it includes the first 200 whitespace-collapsed body characters, redacting the API key before truncation. Unreadable successful replies log only JSON parse success and top-level field names, never body values. Later failures that minute are counted, and the next diagnostic adds `N more since HH:MM UTC`. The clock and sleep are injectable for offline tests. `/mcp/stats` counts each attempt's HTTP/transport class in `upstream_status.mouser`; a `TooManyRequests` body or HTTP 429 counts as `429` regardless of the HTTP status, so limit refusals do not also trigger the dashboard's HTTP error warning; `distributors.mouser.sent` counts every send and `distributors.mouser.retries` counts sent transient retries (also included in `sent`). A retry held by a quota is not counted as sent or retried. A closed client fails immediately with the existing network/connection error, without a send, upstream outcome or retry.

## SamacSys model downloads and wanted list

SamacSys answers a refused download with HTTP 200 and text (`Error: Daily part download quota exceeded`). The tool then says its daily limit is used up and gives the UTC end of its download pause (`CSE_QUOTA_RETRY_SECONDS`, 30 min; memory only), not a guaranteed source reset. Only downloads are paused: `cse_get_kicad` searches still run and stored KiCad files for the resolved part are returned. Searches with no matching part or model keep their usual errors; quota replies retain `part_id` and known part details, looking up metadata from the store at most once. Separate `cse_search` calls still work. Every non-ZIP reply is logged (status, type, size, cleaned text). `CSE daily download quota refused at ...: N downloads stored in the last 24 h` and `CSE downloads accepted again at ...` show the limit's size and window: `grep -E 'CSE daily download quota|CSE downloads accepted'`. SamacSys store reads and writes run off the event loop via `asyncio.to_thread`, with serialized access to the SQLite connection. A model that couldn't be delivered (`quota`, `refused`, `invalid_zip`) goes on the store's wanted list only if it is known from a stored CSE search (part ID, part number, maker, times asked; no addresses; `/health` `cse_stored.wanted`). Arbitrary IDs aren't queued. A completed download or import removes the entry, and a concurrent wanted-list write cannot re-add it. On the server:

```sh
docker exec pcbparts-mcp python -m pcbparts_mcp.cse_store wanted
docker cp LIB_LM358P.zip pcbparts-mcp:/tmp/LIB_LM358P.zip
docker exec pcbparts-mcp python -m pcbparts_mcp.cse_store import /tmp/LIB_LM358P.zip
docker exec pcbparts-mcp python -m pcbparts_mcp.cse_store import --part-id 12345 /tmp/LIB_LM358P.zip
```

`import` matches a ZIP's top folder or file name (without `LIB_`) to one wanted part number; otherwise pass `--part-id N` with a single ZIP (`-` reads stdin). A failed file exits 1.

## Datasheet redirects

`/mcp/datasheet/<lcsc>` reuses a held link, else asks JLCPCB: 20 at once when idle, then one every 3 s (`DATASHEET_SIGNINGS_PER_MINUTE`). A visit beyond that waits for its slot, up to `DATASHEET_MAX_WAIT` (30 s); only a slot further away gets the 429. Simultaneous visits for one part share a request.

`DATASHEET_LINK_BASE` controls links in replies: unset uses the request's Host (HTTPS for an allowlisted public host); an http(s) base URL uses `<base>/mcp/datasheet/<lcsc>`, trimming trailing slashes. Set it to a public address when a private proxy sends an internal Host. `direct` disables short links: live replies keep the provider's link and `datasheet_pdf_expires`, including `jlc_find_alternatives`' original; snapshot replies add no `datasheet_pdf` and leave any `datasheet` unchanged. `jlc_get_parts` adds short links only to present LCSC-code rows without `no_datasheet`, never MPN rows. No HTTP request means no short link, even with a configured base. Invalid settings add one startup warning and act as unset. Forwarded host headers are not trusted; keep uvicorn's `proxy_headers=False`.

## Stored lifecycle

Since 0.10.4 `jlc_get_part`/`jlc_get_parts` rows may carry `lifecycle` (`status`, `raw`, `source`, `observed_at`): the best unexpired, non-unknown stored reading for the catalog MPN and maker, store only. The batch reads each MPN once inside its database job.

The distributor store has one SQLite connection, shared by the event loop and the component pool's workers, and every use of it holds `DistributorStore._lock` (0.10.5). Without the lock, Python's sqlite3 shares one prepared statement between cursors running the same SQL, so concurrent `readings()` returned another part's reading, none, or a row of NULLs: 0.10.4 failed a `jlc_get_parts` call that way (`TypeError` in `readings()`), and `tests/test_distributor_store_threads.py` reproduces it.

## Application log files

The image sets `LOG_PATH=/app/cache/logs/application.log` (the cache volume): the application's INFO lines and every logger's warnings and errors, with UTC timestamps, in daily files due for deletion `LOG_KEEP_DAYS` (30; 7 before 0.10.6) days after their UTC day ends. uvicorn's per-request lines stay in `docker logs` only, which is still lost at each deploy. Today's file is `$LOG_PATH` itself, earlier days `$LOG_PATH.YYYY-MM-DD`: read today with `docker exec pcbparts-mcp sh -c 'grep -a "held back" "$LOG_PATH"'` (a `"$LOG_PATH"*` glob lists today's file first, so its `tail` shows the oldest day's end).

`sdk_logs.install()` (from `main()`) shortens what mcp 1.30 logs about callers to one WARNING line per record (no traceback), keeping the logger: a client that disconnects before its request body is complete (`Error handling POST request` with `ClientDisconnect`, `Received exception from stream` with no text, then `Stateless session crashed` with `ClosedResourceError`: about 60 lines before), and a method the SDK doesn't know, such as the 2026-07-28 spec's `server/discover` (root logger, `Failed to validate request: method '...', N validation errors`: about 95 lines before; the SDK still answers -32602 over HTTP 200). Anything else those loggers write is left as it is. mcp 1.27+ (pinned 1.30.0 from 0.10.5) already drops a reply whose client has gone at DEBUG; fastmcp 3.4.3 still runs the tool to the end.

`LOG_MAX_BYTES_PER_DAY` uses `number_setting` (default 50,000,000 bytes / 50 MB, minimum 1).
The handler counts UTF-8 bytes including timestamps, prefixes and newlines, starting from the
existing file size on restart. A record that would exceed the daily budget is dropped; its lines
are counted in memory. One console warning announces overflow per day, and rollover writes
the previous day's dropped-line count into the new file, subject to the same byte budget.
Each record's message, including any traceback, is truncated to 2,000 characters with a marker
in the file handler only; console records remain unchanged. The log directory is mode 0700,
and active/dated log files are created 0600 and repaired at startup. Rotations close files
before renaming them. A record waits up to 0.25 seconds for a busy file-handler lock; only a
timeout skips it for that file and increments the cumulative `lock_dropped_records` counter.
Rollover writes one warning with the newly dropped record count into the new file, subject to
the same byte budget. Console handlers still receive timed-out records, and minute-loop logging
cannot wait indefinitely behind a stalled file operation.

The minute task prunes application logs hourly, using the same date/backup rules as startup.
It rotates an idle active file before pruning, so old messages expire without a new log event.
Pruning runs off the event loop: it holds the handler's lock while checking/performing rollover,
then releases it before scanning for expired files and deleting them. Record-triggered rollover leaves
deletion to this maintenance. Cleanup runs even when a write failure has disabled the handler;
rollover and deletion failures are retried each hour without disabling retention.
The log path stays registered even if startup cannot create the handler or finish pruning.
Without a handler, hourly cleanup also expires the closed active file by its last-modified UTC day.

## Per-IP limiter, database queue and stuck-worker exit

Each minute runs the stuck-worker check before maintenance. Stats/call-log persistence and
hourly pruning run in a separate task, with at most one outstanding task: a hung disk cannot
block later watchdog ticks or accumulate write tasks. Graceful shutdown finishes that task
before its final flush.

Before a stuck-worker `os._exit`, the server waits up to two seconds for a dedicated daemon thread
to write its exit message to stderr with `os.write(2, ...)`, log that message and flush usage stats,
failed-call minute counts, call rows (including the current refusal minute), failed-query counts
and application handlers. The stderr write, logging and every store share this best-effort budget;
a full stderr pipe, held handler lock or stuck disk cannot make this final logging/flush wait indefinitely.

**Per-IP limiter refusals** (visible since 0.10.0): `RateLimitMiddleware` counts each 429 in `/mcp/stats` (`per_ip_refusals`, per UTC day, no IPs, split by `_refusal_group()` into `platform_ranges`, `everyone_else` and `too_many_clients`, plus `server_busy`, which only holds 0.10.0's stored counts and stays 0; `total` adds all four) and logs a `Per-IP rate limit refusals <hour> UTC: N from M IPs; top: …` line (the five most-refused IPs) for each hour that had any: `docker logs pcbparts-mcp 2>&1 | grep 'limit refusals'`. Those lines (the privacy page describes them) are the only place refused IPs appear, and their container-log copies go with each deploy; the application log file keeps them for 30 days across deploys, and the anonymous daily counts persist separately. uvicorn's access log still shows only Caddy's address (`172.18.0.2`) and Caddy keeps no access log: `main()` passes uvicorn `proxy_headers=False` (uvicorn's default is on, trusting `X-Forwarded-For` from 127.0.0.1): keep it, or every caller's IP could land on every access-log line. Days before 0.10.0 show `per_ip_refusals: null`; while an older version runs, count its refusals since the last deploy with `docker logs pcbparts-mcp 2>&1 | grep -c '" 429'`. Plan for the limits: `todo-platform-rate-limits.md`. Since 0.10.0 `_limit_for()` gives addresses in the AI platforms' published ranges `PLATFORM_RATE_LIMIT` (1,000 a minute, chosen at about half of the VPS estimate from `scripts/load_test.py` (run against a local container only, 2026-11-18): about 9,000 requests a minute sustained on an Apple Silicon core at prod's limits, about 1,800 with the container's CPU cut to 0.33 to stand in for the VPS; re-measure before raising it) and every other address `RATE_LIMIT_REQUESTS` (300): Anthropic's two ranges are in `config.py`, OpenAI's list is `data/platform_ranges/openai-chatgpt-connectors.json`, which `docker-build.yml` replaces with a fresh, checked download on every build (falling back to the committed copy, never failing the build; `platform_ranges.py` is the check, standard library only). The server never downloads it. Also since 0.10.0 the limiter's replies carry `X-RateLimit-Limit/Remaining/Reset` and its 429s a counted-down `Retry-After` and a JSON body `{error, retry_after, reason, resets_at, tell_user}` (`reason` from `RATE_LIMIT_REASONS`; clients read `retry_after`: keep it). The check, the headers and the 429 all use `_limit_for()` (a platform address never gets less than `RATE_LIMIT_REQUESTS`). An IPv6 caller is counted by its /64 (`_limit_key()`; IPv4 and platform addresses by the full address), the window runs on `time.monotonic()` (only `resets_at` reads the wall clock; tests inject `clock=` and `wall_clock=`), and `request_counts` stays in order of each key's last request, so stale cleanup and `too_many_clients` never scan the table; `too_many_clients` refusals log a warning at most once a minute instead of entering the hourly tally. Numeric limit settings go through `config.number_setting()`: a bad value falls back with a warning in `CONFIG_WARNINGS` (logged at startup) instead of failing the import. Also since 0.10.0, `run_db` tracks waiting database jobs per pool with a monotonic clock (`DatabasePressure`; live network waits never count), and since 0.10.2 running ones too (`running`, `longest_running_seconds`; measurement only, nothing refuses or times out on them): `/health` shows them as `database_pressure` and answers 503 once a pool has had jobs waiting and started none for `DB_STUCK_WAIT_SECONDS` (60; `stalled_seconds`, so a long queue that keeps moving under load never counts), and a pool stalled that long at two minute checks in a row makes the server exit (`_exit_if_stuck`) so Docker restarts it, since a stuck worker blocks every database call queued behind it (compose's `restart: unless-stopped` restarts exited containers, not unhealthy ones; `docker logs` shows the ERROR line). Since 0.10.2 component queries run up to 3 at once (`COMPONENT_POOL`), each worker thread on its own read connection (`ComponentDatabase`: no lock held while a query runs, no statement cache); the other catalogs (stock history, sensors, boards) stay serialized on one connection each. A code path that queues many `run_db` jobs at once should batch them into one (the alternatives' footprint seed lookups are one job). 0.10.0's busy cap (`server_busy` 429s when a pool's queue backed up) was removed in 0.10.1 because it refused normal load (about 0.5% of prod's calls at 80 a minute), and a refusal at normal load is a bug. `/health` isn't counted at all, while `/mcp/stats` counts against the per-IP limit as on main before 0.10.0. Every request is charged to its address as it starts, before its body is read, and the body goes to the SDK untouched, as before 0.10.0. `BodySizeLimitMiddleware` (pure ASGI) also counts streamed bytes on every request and replaces a cut-off body's reply with its 413, keeping that reply's X-RateLimit headers; preserve its size guard and streamed replies.

Since 0.10.3 `/mcp/stats` has `db_waits` per day: `jobs`, `waited` (queued at least `DB_WAIT_COUNTED_SECONDS`, 0.1 s), `longest_ms`, and `waited_hours`/`longest_ms_hours` by UTC hour; `components` repeats them for the component pool. Measurement only.

## Usage stats (`/mcp/stats`)

Since 0.10.5 this is a private GET/HEAD endpoint. Set `STATS_TOKEN` and send exactly
`Authorization: Bearer <token>`; the handler compares bytes with `hmac.compare_digest`.
A missing or wrong header, or a blank/unset `STATS_TOKEN`, returns HTTP 401 with
`{"error":"Unauthorized"}` and `WWW-Authenticate: Bearer`. Query-string tokens are ignored;
the handler never logs the token or header. Both 200 and 401 responses carry
`Cache-Control: private, no-store`. Startup warns once when the token is blank/unset.
`?days=` is clamped to 1–`stats.KEEP_DAYS` (365), defaulting to 30 when missing or invalid.
The per-IP limiter and same-origin CORS remain in place; `/mcp` and `/health` need no token.

Since 0.10.9, top-level `distributor_quota` gives current state per available distributor,
independent of `?days=`, `days` and `totals`: `used_today`, `limit`, `api_remaining` (null when
unreported), `paused_until` (null when not paused), `resets_at` and `kept_across_restarts`,
where available. Times use `YYYY-MM-DD HH:MM UTC`. Distributor state is private; public `/health` has no `distributor_quota`.

`usage_stats.json`, its `.tmp` and its `.corrupt` backup are mode 0600. Startup repairs existing
modes, and each save creates its temporary file privately before closing and atomically replacing
the stats file. An unreadable file is moved aside without changing its last-modified time; the
`.corrupt` backup is deleted when that time is more than 30 days old, at startup (including after
moving an unreadable file) and in hourly maintenance.
If chmod or rename prevents moving the original aside, saves remain disabled for that path while
hourly maintenance retries the move and continues pruning the backup. Saves resume only after the
original has been moved safely; its original modification time still determines backup expiry.

Since 0.10.5 these daily fields are additive-null (null on days saved before 0.10.5):

- `bad_request_reasons`: per tool, one fixed label per `bad_request`, separate from `reasons` (which still sums to `not_found + failed`). Error replies use `category_not_found`, `too_long`, `too_many`, `invalid_value`, `unsupported_exclusion`, `strict_unmet`, `unsupported_value`, `unsupported_sort`, `missing_argument`, `invalid_lcsc`, `query_unsearchable` or `invalid_id`; all-invalid lifecycle, part and history batches use `all_inputs_invalid`, unknown tools use `unknown_tool`, other cases use `other`. Argument errors use `arg:<declared parameter or unknown_argument>:<fixed Pydantic error type or other>` (`stats.ARG_ERROR_TYPES`). Since 0.10.6 the reply to an unknown argument names the tool's arguments, the closest one and advice for known mix-ups (`_unknown_argument_error`, `ArgumentAliasMiddleware`, which sits outside the usage counting so the label is unchanged); fastmcp's own WARNING keeps each rejected name and value in the log file. Other names are accepted before validation (`ARGUMENT_ALIASES`; `VALUE_ALIASES` where the target depends on the value; `cse_get_kicad(lcsc=)` through the catalog's MPN; `jlc_search(mounting_type=)` appended to the query when the query parser reads it as SMD or through hole) and stay out of the tool list. Names come from `list_tools` at startup; caller-supplied unknown names never become keys. FastMCP 3.4 wraps argument failures in its `ValidationError`, with the Pydantic exception as `__cause__`; `ArgumentAliasMiddleware` runs before validation and counting. Function-call types `missing_argument`, `unexpected_keyword_argument`, `unexpected_positional_argument`, `multiple_argument_values`, `missing_keyword_only_argument` and `missing_positional_only_argument` retain their own labels.
- `tool_apps`: each tool's `calls` and all six outcomes by app, using the same address-to-app link as `distributor_apps`. During the current UTC day, keep up to `MAX_APPS` (50) cleaned app names per tool, plus the reserved `other` bucket for later new names. Once a day is past, compact each tool to its 14 busiest named apps by calls (name breaks ties), summing all remaining calls and outcome counts into `other`: at most `MAX_TOOL_APPS` (15) keys. Compaction runs on rollover, load, save and summary; loading today's counts preserves its larger cap. `distributor_apps` keeps its existing meaning and cap.
- `latency`: per tool, `counts` in inclusive upper-bound buckets (50, 100, 250, 500, 1000, 2500, 5000, 10000, 30000, 60000 ms, then an open bucket), plus `p50_ms`, `p95_ms`, `p99_ms`. Bounds appear once as top-level `latency_bounds_ms`. Only `ok`, `similar_only`, `not_found` and `failed` count; instant `bad_request` and `rate_limited` replies do not. Percentiles use the bucket upper bound, null for an empty histogram or the open bucket. Totals combine bucket counts before computing percentiles.
- `versions`: server starts by running version, alongside `restarts`; only short version-like keys survive loading.
- `upstream_status`: per `UPSTREAM_STATUS_SOURCES` source (`UPSTREAM_SOURCES` plus `mouser` since 0.10.9), one class per HTTP request counted as sent: `2xx`, `3xx`, `4xx`, `429` (separate from `4xx`), `5xx`, `timeout`, `connection`, `challenge`, `too_large`, `cancelled`, `other_error`. Mouser `TooManyRequests` replies count as `429` regardless of HTTP status. Typed wafer failures take precedence over an attached HTTP status; httpx errors in CSE follow the same classes. A response with wafer's `challenge_type` set counts as `challenge` before its HTTP status is considered (including sessions with `max_rotations=0`). Cancellation after sending counts as `cancelled` and is re-raised. Ordinary wafer 4xx/5xx answers are response objects; `raise_for_status()` raises `WaferHTTPError` with `status_code`. No additional requests are sent.

- `popular_terms`: the top 200 query tokens meeting the 10-caller daily threshold; normalization, caller grouping and memory bounds are described in the call-log section above.

`tool_apps`, `latency` and `popular_terms` are kept for the last 30 days only: rollover, load, save and summary clear these fields to null on days at least 30 UTC dates before today. The same maintenance deletes whole days at least `KEEP_DAYS` (365) UTC dates before today, including their cached JSON; other counts within that window stay intact. This also runs when no calls arrive or the file already contains today; a cleanup marks the file for saving. The usage dashboard (`dashboard/`, behind a password) keeps every day it fetches, indefinitely. New daily fields resume counting on an upgrade day; hourly fields keep null for hours before counting began.

Label cutovers from 0.10.5: `mouser_get_part` misses with a nonempty `not_found` list and no results count `part_not_found` instead of `no_results` (`not_sent` still wins). Otherwise-unlabelled empty live `jlc_stock_check` searches count `no_results_filtered` when category/subcategory/package/manufacturer/library filters were given, else `no_results_part_number` using `looks_like_mpn`, else `no_results_words`. Empty `jlc_search` part-number misses count `part_number_sold_out` when `get_sold_out_by_mpn` finds a previously listed row, else `part_number_unknown`. These call-note splits apply only to `not_found` without an exception: the three `no_results_*` labels replace only `no_results`, and the two `part_number_*` labels replace only `part_number_not_in_stock`. More specific labels such as `blocked_by_min_stock`, and `exception`, remain intact. This is the only search read of `sold_out`, inside the existing offloaded job and for counting only; tool replies do not change. Old `no_results` and `part_number_not_in_stock` labels remain valid for historical days. `stats.note()` passes facts through a fresh call-local ContextVar dict, shared with `db_worker.run_db` via `copy_context().run`, then reset after counting.

Failed calls also accumulate by `(tool, reason)` in memory. The minute task emits one WARNING for each finished UTC minute that had failures, with counts and fixed labels only (no arguments); shutdown flushes the current minute too. Counting and label lookups remain guarded so a stats failure cannot fail a tool call.

Since 0.10.4 `lifecycle_inputs` counts usable `part_lifecycle` entries by form (`bare_number`, `with_manufacturer`, `lcsc_code`); labels only, null on earlier days.

Since 0.10.3 `datasheet_links` counts `visits`, `reused` (no JLCPCB request), `signed` (one was made), `waited` (of those, after waiting for a slot), `refused` (429), `failed` (502) and `not_found` (404).

Since 0.10.3 `distributor_limits` has, for `mouser` and `digikey`: `held_back` by cause (`minute_cap`, `daily_count`, `address_daily`, `address_blocked` from 0.10.10, `distributor_daily`, `distributor_minute`, `distributor_refused`, `other`), which adds up to `distributors.<name>.rate_limited`; `held_back_hours` (24 UTC hours); and `refusals` the distributor itself gave (`daily`, `minute`, `refused`). DigiKey's `refused` counts one per lookup or batch whose request was refused (0.10.5 counted each refused request; 0.10.6 restored 0.10.4's meaning), counted as the refusal happens, so a lookup cancelled afterwards keeps it. Null on earlier days; only distributor totals.

`/mcp/stats` (under `/mcp` because Caddy forwards only `/mcp*` and `/health`) serves private daily counts and qualifying popular search words from `stats.py`: per-tool calls = ok + similar_only + not_found + bad_request + rate_limited + failed (alternatives: ok means verified alternatives found; similar_only means manual comparison candidates without verified replacements), calls per UTC hour (since 0.10.1 also `failed_hours` and `refused_hours`: failed tool calls and every `per_ip_refusals` 429 per UTC hour, null on earlier days and, on the upgrade day, before the server started), apps, distinct callers, Mouser/DigiKey lookups, plus why calls found nothing or failed (`reasons`: one label a call from the fixed `stats.REASONS` list, so a tool's labels add up to its not_found + failed) and how `why_empty` checks went. Since 0.10.0 also `upstream`: for each service other than Mouser/DigiKey (`stats.UPSTREAM_SOURCES`: JLCPCB, LCSC, three EasyEDA endpoints, SamacSys, and since 0.10.4 DigiKey's HTTP requests; `waited`: sent after waiting for a request slot) the HTTP requests `sent` (not tool calls), wafer's own `retries`, `cached` answers and `rate_limited` (held back by our own budgets); counted with `_sent()`/`_count_upstream()` in `client.py` and in `cse.py`, so a new request or cache must be counted there too (`tests/test_usage_upstream.py` checks the names). `parts_asked`: part numbers looked up with Mouser/DigiKey, total and distinct by `mpn_key` (salted hashes in memory for the day, never written); `per_ip_refusals` (above); and `restarts` (server starts that UTC day: each resets the hashes, so `callers` and `parts_asked.distinct` can double-count on such a day). A day's fields this version doesn't know are carried through saves, and an unreadable file is moved to `usage_stats.json.corrupt` before counting starts from 0; still copy the stats file before rolling back to a version older than 0.10.0, which drops fields it doesn't know. The file (`USAGE_STATS_PATH` on the cache volume) keeps 365 days; authenticated callers can request up to 365, with 30 as the default. Error replies are sorted by `_ERROR_KINDS` in the pure `tool_outcomes.py` module (re-exported by `server.py`); every error message must be listed in `ERROR_REPLIES` in `tests/test_usage_stats.py` (the test enforces it), and not_found and failed ones need a reason in `_NOT_FOUND_ERRORS` or `_FAILED_REASONS` (`tests/test_usage_reasons.py` enforces that). Keep it same-origin: if another site ever needs it, allow that domain only, never `*`.
