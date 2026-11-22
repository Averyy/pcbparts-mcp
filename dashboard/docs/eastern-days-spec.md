# Eastern days and the problems window (backend spec)

The user wants every day and time on the page in Eastern time (America/New_York), and wants problems (failures, refusals, held-back lookups, rejected arguments, upstream errors) counted only from a given moment: the 0.10.5 deploy, 1:00 PM EST on 2026-11-21. The server's counters are per UTC day (they reset at 7 PM EST, 8 PM EDT), so the backend re-cuts them. This replaces `days` and `compare` in `/api/data`; everything else in `docs/backend-spec.md` stays.

## Inputs already stored

- `days`: one record per UTC day `D`; counters accumulate during `D` and are final once `D` is over (the record merged from the first fetch after 00:00 UTC of `D+1`).
- `snapshots`: the current UTC day's record at each fetch (`fetched_at`, `date`).
- Hourly fields (exact by UTC hour, index 0 = 00:00–01:00 UTC, `null` = not recorded): `hours`, `failed_hours`, `refused_hours`, `distributor_limits.<name>.held_back_hours`, `db_waits.waited_hours`, `db_waits.longest_ms_hours`, `db_waits.components.waited_hours`, `db_waits.components.longest_ms_hours`.

## Counter value at a moment

`at(D, t)`: day `D`'s counters accumulated from 00:00 UTC of `D` up to `t` (00:00 ≤ t ≤ 24:00 of `D`).
- `t` = 00:00 of `D`: an all-zero record.
- `t` = 24:00 of `D` and `D` is over: the stored record `days[D]`.
- A snapshot of `D` within 90 seconds of `t`: that snapshot, exact.
- Otherwise interpolate between the nearest known points around `t` in `D`: the latest of {00:00 zero record, snapshots of `D` before `t`} as `lo`, and the earliest of {snapshots of `D` after `t`, the final record if `D` is over, else the newest snapshot of `D`} as `hi`. Each additive counter becomes `lo + (hi − lo) × f`, where `f` is the share of `D`'s tool calls between `lo` and `hi` that happened before `t`, from `hours` (linear within an hour); fall back to the time fraction when those calls are 0 or `hours` is missing. When `t` is after the newest point and `D` isn't over, use the newest point (and mark approximate if it's more than 90 seconds away). Round to integers. Mark the result approximate.

## Window records

`window(t1, t2)`, for `t1 < t2`, both on UTC hour boundaries (Eastern midnights always are): for each UTC day `D` overlapping `[t1, t2)`, add `at(D, min(t2, end of D)) − at(D, max(t1, start of D))`.

Field rules:
- Additive numbers anywhere in the nested dicts: subtract, then add across days. Clamp negative results to 0 and mark the window approximate.
- `tool_apps`, `distributor_apps`, `apps`, `popular_terms`: a past day's later record may have folded some names into `"other"` (the server compacts `tool_apps` to 14 apps plus `other` at rollover). Before subtracting `lo` from `hi`, move any key of `lo` that `hi` lacks into `lo`'s `"other"` (for `tool_apps`, per tool; for `distributor_apps`, per tool; for `apps` and `popular_terms`, drop such keys instead), then clamp at 0.
- Hourly fields: never interpolated. In a window record each becomes a list with one entry per hour of the window (index 0 = the hour starting at `t1`), copied from the UTC days' lists; a `null` entry stays `null`; the whole field is `null` when every entry is.
- `tools.<tool>.avg_ms`: `(avg_hi × calls_hi − avg_lo × calls_lo) / (calls_hi − calls_lo)` per day part, combined weighted by calls; `null` when there were no calls.
- `latency.<tool>`: keep only `counts` (the page recomputes percentiles).
- `db_waits.longest_ms` and `db_waits.components.longest_ms`: the maximum of the window's `longest_ms_hours` entries (`null` if none).
- `callers` and `parts_asked.<name>.distinct`: not divisible; `null` in window records.
- A field that is `null` or absent in every contributing day stays `null`.
- Each window record adds `start`, `end` (ISO UTC with `Z`), `hours_in_window` (int) and `approx` (bool).

## Eastern days

An Eastern day `E` runs from 00:00 America/New_York on `E` to 00:00 on the next day: 24 hours, or 23/25 on DST change days (2026-03-08 has 23, 2026-11-01 has 25).

`eastern_day(E) = window(start(E), min(end(E), as_of))` plus `date` (E, `YYYY-MM-DD`), `complete` (`end(E) <= as_of`) and, see below, `problems`. `as_of` is `last_success_at` (the time the newest data was fetched).

- Persist complete Eastern days in a new table `eastern_days(date TEXT PRIMARY KEY, data TEXT NOT NULL, approx INTEGER NOT NULL, computed_at TEXT NOT NULL)` once every UTC day they touch is over and stored. Recompute a persisted day only if it was approximate and the inputs now allow an exact result (a later import, say); otherwise reuse it, because snapshots are pruned after 45 days.
- Eastern days are produced for every date from the Eastern date of the first stored UTC day's 00:00 to today. A day whose UTC inputs are partly missing is computed from what exists and marked approximate.

## The problems window

`problems_since`: the start of the problems window (ISO UTC). The setting `PROBLEMS_SINCE` (environment or `secrets.local`) wins. Otherwise meta `problems_since` is updated automatically: on a successful collect, if `/health`'s `version` differs from meta `seen_version`, set `problems_since` to the start of the UTC hour of that fetch (an hour boundary, so hourly fields stay exact), `problems_version` to the new version, and `seen_version`. On the first collect ever, just record `seen_version` without moving `problems_since`. `problems_version` is also settable with `PROBLEMS_VERSION`.

For the current setup put `PROBLEMS_SINCE=2026-11-21T18:00:00Z` and `PROBLEMS_VERSION=0.10.5` in `secrets.local` (1:00 PM EST, the 0.10.5 deploy; append the two lines, don't print or change the token line).

Each Eastern day record gets `problems`: `window(max(start(E), problems_since), min(end(E), as_of))` when that interval is non-empty, else `null`. Its hourly lists cover only that interval (index 0 = the hour starting at its own `start`).

## Comparing today

`compare_today`: yesterday from Eastern midnight up to the same Eastern wall-clock time as `as_of`, i.e. `window(start(yesterday_E), t)` with `t` = `as_of` moved back one calendar day in America/New_York. `t` is usually not on an hour boundary: the additive counters use `at()` for the end point as usual, and each hourly list covers the whole hours from `start(yesterday_E)` plus the hour containing `t`, with that last entry scaled by the fraction of the hour before `t` and rounded. `null` when yesterday has no data.

## Polling on the hour

Poll slots move from `:02` to 30 seconds past each slot (`:00:30` for 60 minutes), so snapshots fall on hour boundaries and Eastern midnights get an exact snapshot from now on. `next_poll_at` follows.

## Payload changes

```json
{
  "...": "everything else as before, minus days and compare",
  "timezone": "America/New_York",
  "as_of": "2026-11-21T20:13:50Z",
  "edays": [ {"date": "2026-11-20", "start": "2026-11-20T05:00:00Z", "end": "2026-11-21T05:00:00Z",
              "hours_in_window": 24, "complete": true, "approx": true, "calls": 81234, "hours": [ ... 24 ... ],
              "tools": { }, "apps": { }, "problems": null, "...": "same fields as a UTC day record" } ],
  "compare_today": { },
  "problems_since": "2026-11-21T18:00:00Z",
  "problems_version": "0.10.5"
}
```

`edays` is oldest first. `latency_bounds_ms`, `health`, `last_fetch`, `next_poll_at`, `warnings` stay.

## Tests (no network, injected clocks, no real sleeps)

- `at()`: exact snapshot, interpolation weighted by `hours`, time-fraction fallback, day start and end, approximate flag.
- `window()` across a UTC midnight (an Eastern day = 19 hours of `D` + 5 of `D+1` in winter, 20 + 4 in summer), hourly-list slicing and `null` handling, clamping, `"other"` folding, `avg_ms`, `latency`, `longest_ms`, non-divisible fields `null`.
- Eastern days on 2026-11-01 (25 hours) and 2026-03-08 (23 hours).
- Persistence: complete days stored once and reused after their snapshots are pruned; approximate days recomputed when exact inputs appear.
- `problems`: `null` before `problems_since`, partial on the deploy day, whole on later days; `PROBLEMS_SINCE` overrides; automatic update on a version change, not on the first collect.
- `compare_today` with and without a snapshot near the same time yesterday.
- Poll slots at `:00:30`.
- Payload shape: `edays`, `compare_today`, `problems_since`, `problems_version`, `as_of`, `timezone`; no `days`/`compare`.
