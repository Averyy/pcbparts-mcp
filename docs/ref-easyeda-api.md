# EasyEDA API — Reference

## Endpoints we call

| Endpoint | Called from | Returns |
| --- | --- | --- |
| `GET https://easyeda.com/api/products/{lcsc}/components` | `_check_easyeda_footprint()` (behind `check_easyeda_footprint()`): every live `get_part()`, and up to 15 times per `find_alternatives(has_easyeda_footprint=...)` call | Whether EasyEDA has a symbol/footprint, plus their UUIDs |
| `GET https://easyeda.com/api/components/{uuid}` | `get_easyeda_component()` (`jlc_get_pinout`) | Symbol data and pins |

Each has its own wafer session in `client.py`. `_get_easyeda_products_session()` sends exactly one
request per check (`max_retries=0, max_rotations=0`). `_get_easyeda_session()` keeps wafer's
retries for symbol data, with `attempt_timeout` paired to its `timeout`.

Caches (per process, keyed by LCSC / UUID): footprint answers 24 hours
(`EASYEDA_FOOTPRINT_CACHE_TTL`), symbol data 1 hour (`EASYEDA_CACHE_TTL`), errors 5 minutes
(`EASYEDA_ERROR_CACHE_TTL`).

## Rate limit on `/api/products` (measured 2026-10-09)

EasyEDA doesn't publish a limit and sends no rate-limit headers. Measured from a residential IP
(CloudFront POP YTO53, Toronto), one attempt per request (wafer `max_retries=0, max_rotations=0`):

| What | Result |
| --- | --- |
| Threshold | Sequential requests at 1/s: **24 returned 200, the 25th got 403** (about 28s in). One request 9 minutes earlier was probably in the same window. |
| Block response | Bare **403**, `x-cache: Error from cloudfront`, CloudFront's "The request could not be satisfied" HTML page. **No 429, no `Retry-After`, no `x-amzn-waf-action`**, so there's no challenge to solve and nothing says how long it lasts. |
| Scope | **Per IP and per path.** While blocked, any LCSC on `/api/products` gets 403; `/api/components/{uuid}` on the same host still returns 200. Prod's IP was unaffected while this machine was blocked. |
| Fingerprint | Doesn't matter. While blocked, wafer's Chrome emulation, its Firefox rotation and plain curl all got 403. |
| Recovery | **About 2 minutes.** Blocked at 23:48:22Z; a check 70s later still got 403, one at 131s got 200. On 2026-10-10 a request 123s after the last one of a run that crossed the limit was still blocked. Behaves like a ~2-minute rolling window (or a fixed ~2-minute ban). Three requests sent during that block didn't extend it. |

**Practical budget: stay under 20 requests per rolling 2 minutes** (about one every 6s sustained).

Earlier the same day, a block lasted **38–89 minutes**. It started during an integration run,
which turned out to send about 26 requests by itself (the count above was found later). The tests
were then re-run for about 11 minutes while blocked, with each 403 retried and rotated 4–6 times by
the session, so dozens of requests went out. The likely explanation is that heavy traffic during a
block extends it. That isn't confirmed.

Other people's measurements of the same endpoint:

- [part2kicad](https://pypi.org/project/part2kicad/) (Aug 2026): blocks after "roughly 45 fetches
  within a few minutes, cumulatively, not by peak rate", clears after about 2 minutes, and the
  block is tied to the path. They space requests at least 3s apart and back off 120s → 240s on a 403.
- [kicad-jlcpcb](https://github.com/BeckhamLabsLLC/kicad-jlcpcb): "tolerates roughly 1 req/minute
  per IP after an initial burst". They space requests 12s apart.
- [easyeda2kicad #191](https://github.com/uPesy/easyeda2kicad.py/issues/191) (Apr 2026): non-browser
  User-Agents get a 403 regardless of rate. wafer always sends a browser UA, so this doesn't affect us.

## What that means for this project

- One `pytest -m integration` run sends about 20 `/api/products` requests in under a minute: 6 pinout
  tests, 4 footprint-filter checks, and about 10 `get_part`/find-alternatives originals (each test
  class has its own client and cache, so some parts get looked up twice). That's close to the limit
  on its own. Before 0.5.6 the filter test checked 10 parts and a run sent about 26. On 2026-10-10
  that crossed the limit at the very end of a run, and a request 2:03 later was still blocked.
  A smoke test of the tools sends 1–2.
- Before 0.5.6, one `jlc_find_alternatives(has_easyeda_footprint=..., limit=50)` call could fire
  100 checks at 10/s, and wafer retried and rotated every 403 (3 requests each), which kept a block
  alive. A block on prod's IP turns `has_easyeda_footprint` into `null` for every user until it
  clears. The guard below exists to stop that.

## Rules

- **On the first EasyEDA 403, stop sending.** Don't re-run the integration tests, run single tests,
  or retry by hand. A few stray requests don't seem to extend a block, but heavy retry traffic
  during one probably turned a 2-minute block into a 38–89 minute one. Confirm prod is fine with one `jlc_get_part`
  call on pcbparts.dev (`has_easyeda_footprint` should be `true`), then wait.
- Give integration runs the endpoint to themselves: no other EasyEDA traffic (smoke tests, other
  runs, manual calls) for 3 minutes before a full `-m integration` run, and none for 3 minutes after.
  It sends about 20 requests, and a block lasts a bit over 2 minutes.
- Never route around the block (proxies, other IPs). It's EasyEDA's limit; we stay under it.
- When adding a code path that calls `/api/products`, go through `_check_easyeda_footprint()` so the
  budget and cooldown apply. Count how many requests one tool call can make and keep it well under 20.

## How the client stays under it (0.5.6)

All of this lives in `_check_easyeda_footprint()`. The budget and cooldown belong to the
`JLCPCBClient` instance; the server creates one, so they're process-wide there. Settings are in
`config.py`.

1. **One request per check.** A 403 or 429 is EasyEDA's block. wafer would retry and rotate it,
   so the products session doesn't.
2. **Cooldown on the first block** (`Cooldown` in `cache.py`). All `/api/products` calls pause for
   `EASYEDA_COOLDOWN_BASE` (2 min), doubling on each repeat block up to `EASYEDA_COOLDOWN_MAX`
   (30 min). A success after the pause clears the strikes.
   - Checks already in flight when the block lands count as one block.
   - A request from before the block that comes back 200 can't reset the escalation.
   - Blocked answers aren't cached per part; the cooldown covers them.
3. **Budget** (`SlidingWindowBudget` in `cache.py`). At most `EASYEDA_PRODUCTS_BUDGET` (20) requests
   per rolling `EASYEDA_PRODUCTS_WINDOW` (120s). Cached answers don't count. Over budget, the
   check returns unknown immediately. A tool call never waits for budget. Running out logs one
   warning per window ("request budget spent"), so prod logs show if real traffic outgrows it.
4. **Footprint filter cap.** `find_alternatives(has_easyeda_footprint=...)` checks at most
   `EASYEDA_MAX_FOOTPRINT_CHECKS` (15) candidates (it was 2×limit, up to 100). Limits up to 7
   behave as before.
   - When the cap, the budget, a cooldown or an EasyEDA error limited the results, the response
     says so in `summary.footprint_filter`: `candidates`, `checked`, `unknown` and a `note`.
   - Candidates with an unknown footprint are left out of filtered results, as before.
5. **No pinned unknowns.** If a part was cached by `get_part()` while its footprint was unknown,
   the next cache hit re-checks the footprint through the footprint cache. The unknown no longer
   sticks for the part's 1-hour TTL.

Skipped and blocked checks return `has_easyeda_footprint: null`, the same shape as before, so
`jlc_get_part` responses don't change. `jlc_get_pinout` now reports an unknown status as "Couldn't
check EasyEDA for … right now … Try again in a few minutes" instead of "No EasyEDA symbol available",
which was wrong for parts that have one. Blocks are logged as warnings ("pausing footprint checks
for Ns"), and so is the budget running out (at most once per window). Both show in `docker logs`.

Tests: `tests/test_easyeda_guard.py` covers the guard, statuses, TTLs and the note.
`tests/test_easyeda_regressions.py` uses only the public API and fails on the pre-0.5.6 code.
