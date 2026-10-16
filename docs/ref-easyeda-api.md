# EasyEDA API — Reference

## Endpoints we call

| Endpoint | Called from | Returns |
| --- | --- | --- |
| `GET https://easyeda.com/api/products/{lcsc}/components` | `_check_easyeda_footprint()` (behind `check_easyeda_footprint()`): every live `get_part()`, and up to 15 times per `find_alternatives(has_easyeda_footprint=...)` call | Whether EasyEDA has a symbol/footprint, plus their UUIDs |
| `GET https://easyeda.com/api/components/{uuid}` | `get_easyeda_component()` (`jlc_get_pinout`) | Symbol data and pins. A missing UUID is HTTP 200 with `{"success": false, "code": 404}` (`EasyEDAComponentNotFound`) |
| `POST https://easyeda.com/api/components/search` | `scripts/build_easyeda_seed.py` only, never the server | Up to thousands of LCSC-library parts per request, each with its symbol and footprint UUIDs |

Each has its own wafer session in `client.py`. `_get_easyeda_products_session()` sends exactly one
request per check (`max_retries=0, max_rotations=0`). `_get_easyeda_session()` keeps wafer's
retries for symbol data, with `attempt_timeout` paired to its `timeout`.

Where a footprint answer comes from, first match wins:

1. **Memory** (per process): live answers 24 hours (`EASYEDA_FOOTPRINT_CACHE_TTL`), errors 5 minutes
   (`EASYEDA_ERROR_CACHE_TTL`).
2. **Store or seed**, whichever answer is newer (`easyeda_store.pick_answer()`):
   - The store is a SQLite file of every live answer (`EASYEDA_STORE_PATH`). The image sets
     `/app/cache/easyeda.db` and both compose files mount the named volume `pcbparts-cache` there,
     so it survives restarts and deploys (`docker compose down` keeps named volumes). Unset or
     unwritable means memory only, as before 0.6.0. Only the server opens it: `JLCPCBClient` takes
     the path as an argument, so tests and scripts never write fake answers into a real store
     (`tests/conftest.py` also blanks it for tests that start the server).
   - The seed is `data/easyeda/footprints.csv`, built by `scripts/build_easyeda_seed.py` and loaded
     into the `easyeda_footprints` table of `components.db` at build time. Every row is validated
     on load, before the components load, so a malformed file fails the build within seconds
     instead of being served. The Dockerfile mounts the CSV for the DB build step only
     (BuildKit), so it isn't shipped in the image.
   - "Has a footprint" never expires: EasyEDA edits records in place and keeps their UUIDs (the
     STM32F103C8T6 symbol was edited in 2020 and 2025, its footprint in Aug 2026, same UUIDs).
     "No footprint" expires after 7 days (`EASYEDA_NOT_FOUND_TTL`): EasyEDA draws footprints for
     parts after they go on sale. Errors and blocks are never stored, and neither is a "has a
     footprint" answer without a usable symbol UUID: it's served as EasyEDA gave it and asked
     again once the memory cache expires (`easyeda_store.answer_problem()`; the seed script skips
     those too).
3. **Live** `/api/products`, under the budget and cooldown below.

At startup the server logs `EasyEDA footprints: N seeded, M stored in <path>`, or `no store (memory
only)` when the store can't be used. A store that fails to open also logs a warning.

`/health` shows the same counts, so a deploy can be checked without the server's logs:
`"easyeda_footprints": {"seeded": 397062, "stored": 12}`. `stored` is `null` when there's no usable
store, and it counts re-check markers too. It's recounted at most once a minute
(`HEALTH_STORE_COUNT_TTL` in `server.py`), since `/health` is public, isn't rate limited and is
fetched by every landing page visit. After a deploy: `seeded` matches the CSV's rows, `stored`
isn't `null`, it goes up within a minute of a live check on a part neither one has yet, and it
doesn't drop on the next deploy (the volume kept it).

Symbol data is cached 1 hour (`EASYEDA_CACHE_TTL`).

**Self-heal:** when `jlc_get_pinout` gets "not found" for a stored symbol UUID, it calls
`invalidate_easyeda_footprint()` (a re-check marker that overrides the store and seed, also
written to the store so it survives a restart), re-checks the part once and follows the new UUID.
The fresh answer goes to the store; without one it's kept in memory (`_easyeda_overrides`), so the
older seed answer can't come back when the memory cache expires. If `/api/products` named that
same dead UUID for the part within the last hour (`EASYEDA_RECHECK_INTERVAL`), it returns the
error without re-checking, so repeated calls don't spend the request budget.

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
5. **Stored answers are free.** Answers from the store or seed use no budget and are served during
   a cooldown.
6. **No pinned unknowns.** If a part was cached by `get_part()` while its footprint was unknown,
   the next cache hit re-checks the footprint through the footprint cache. The unknown no longer
   sticks for the part's 1-hour TTL.

Skipped and blocked checks return `has_easyeda_footprint: null`, the same shape as before, so
`jlc_get_part` responses don't change. `jlc_get_pinout` now reports an unknown status as "Couldn't
check EasyEDA for … right now … Try again in a few minutes" instead of "No EasyEDA symbol available",
which was wrong for parts that have one. Blocks are logged as warnings ("pausing footprint checks
for Ns"), and so is the budget running out (at most once per window). Both show in `docker logs`.

Tests: `tests/test_easyeda_guard.py` covers the guard, statuses, TTLs and the note.
`tests/test_easyeda_regressions.py` uses only the public API and fails on the pre-0.5.6 code.
`tests/test_easyeda_store.py` covers the store, seed, lookup order and self-heal;
`tests/test_easyeda_seed.py` covers the seed script.

## Library search (`/api/components/search`, measured 2026-10-10)

Form-encoded POST (wafer `body=`; wafer has no `data=`):
`type=3&doctype[]=2&uid=0819f05c4eef4c71ace90d822a990e87&returnListStyle=classifyarr&version=6.4.7&wd=<keyword>&page=<n>&pageSize=<n>`.
The `uid` is the owner of every LCSC-library component. Results are in `result.lists.lcsc`; each has
`lcsc.number`, the symbol `uuid` and the footprint `dataStr.head.puuid`. `result.facets.lcsc` is
the total count.

- **Same answers as `/api/products`.** C2040 and C8734 came back with identical UUIDs. A few LCSC
  codes have two library components (2 of ~1,000 sampled); `/api/products` returns one of them
  (C5278888: the newer "-1" entry) and search can't tell which, so the seed skips those.
- **Can't prove "no footprint".** 12 of our parts missing from keyword results were checked on
  `/api/products`: 6 had footprints anyway. Search only records "has a footprint".
- **`pageSize` works up to 5,000**; 10,000 and 15,000 return HTTP 500. So did 5,000-result pages
  for "Intel/Altera" (2026-10-12) while 2,000 worked; the script retries a keyword at 2,000 a page
  after a 5xx.
- **Results come back in a different order on every request**, so paging repeats some results and
  never returns others. Bigger pages help within the first 10,000 results: at 2,000 a page, 13.6%
  of the full run's multi-page results were repeats (44,270 of 324,716; Nexperia 45%), while
  Nexperia's first two 5,000-result pages had 4 repeats in 10,000. Past 10,000, pages are mostly
  repeats and vary per request (Nexperia's results 10,001-12,909 as page 3 at 5,000: 0 new on one
  try, 769 new on the next; as pages 6-7 at 2,000: 391 new of 2,909). In the `names` step, 23.9%
  of results on keywords over 5,000 were repeats. Each crawl's order is different, so repeated
  crawls add up: the seed holds 87% of our TI parts though no single "TI" crawl found more than
  74%. With the default 100 per page it's worst: paging PAKER 100 at a time returned 44 duplicates
  and found 283 of our 395 parts; one 500-result page found 325.
- **One keyword at a time.** Several words are ANDed; `|` and `OR` return nothing. It matches words
  in titles, MPNs and manufacturer names, so a part-number search returns loose matches.
- **Manufacturer names are LCSC's**, e.g. `TI(德州仪器)` for our "Texas Instruments" ("Texas
  Instruments" matches 219 parts, "TI" works). Each result carries it in
  `dataStr.head.c_para.Manufacturer` ("ADI(亚德诺)" for C9669; older records used `BOM_Manufacturer`,
  and some say "null"), which is how the `names` step finds it.
- **A name that doesn't match falls back to its common words.** Every "X Electronics" name that
  LCSC doesn't use returned the same 15,194 results, every "X Tech" about 8,800, and hyphenated
  names like "G-NiceRF" and "D-SWITCH" 71,000-78,000. EasyEDA also lists out-of-stock parts: "YAGEO"
  returns 44,495 for our 21,004, "Vishay" 29,907 for 11,743, "Murata" 11,134 for 7,427.
- **Rate limit not measured** (a burst test was refused). Never blocked at one per 10 s: 1,726
  requests over 4 h 47 min on 2026-10-10, and about 1,460 over 4 h on 2026-10-12. 133 requests at
  one per 7 s over 15 minutes weren't blocked either.
- **It counts toward `/api/products`' block.** Right after those 133 searches, `/api/products` at
  one per 7 s got a 403 on its 17th request (2026-10-10 14:28Z), below the 24 a quiet IP gets. The
  rule isn't pinned down (shared counter or a longer window), so the seed script waits 10 minutes
  after search traffic before any `/api/products` step and paces those at one per 15 s (65 went
  through at that pace afterwards). Search itself runs at one per 10 s.
- **Even a good keyword misses parts.** The "TI" crawl found 64% of our TI parts but missed C9864
  (TPS5430DDAR, a basic part with a footprint), which a direct search for its MPN returns. That's
  why basic and preferred parts get the per-part step.

Trial, 2026-10-10 (20 manufacturers: the 10 largest plus 10 random, 119,626 of our parts): 133
requests in 15 minutes, 67,337 parts recorded as "has a footprint" (6.0 MB of CSV, ~89 bytes a
row), 49 ambiguous parts skipped. Validation: 50 of 50 search answers matched `/api/products`
exactly (16 before the block above, 34 after a 17-minute pause at one per 15 s, no block). Of 30
random parts the big-10 searches didn't return, 7 had a footprint (23%): all the TI ones (TI's
"TI" keyword spans 72,524 results over 37 pages, where the order likely shifts), none of the TE
Connectivity ones (its connectors mostly have no footprint).
Per manufacturer: TI 64% (via "TI"), YAGEO 59%, Vishay 49%, UNI-ROYAL 68%, TE Connectivity 16%,
FH 56%, TECH PUBLIC 53%, XKB 57%, FOJAN 44%, Murata 52%. HX(hengjiaxing) found nothing: "HX" is too
broad and "hengjiaxing" matches nothing, so it needs a `KEYWORD_ALIASES` entry.

Full `manufacturers` run, 2026-10-10 15:13-20:00Z: 1,582 manufacturers, 1,726 requests at one per
10 s, never blocked. 291,586 of our 629,550 parts recorded as "has a footprint" (46%); validation
50 of 50. Three gaps:
- **Name mismatch:** 414 manufacturers had under 10% found (93,853 parts), mostly 0%, because LCSC
  names them differently: STMicroelectronics 0 of 5,347, Analog Devices 22 of 5,743, Walsin 0 of
  5,099, Jiangsu Changjing 0 of 3,220.
- **Too broad:** 121 manufacturers (49,858 parts) whose every keyword was skipped, including
  onsemi (30,564 results for 6,495 of ours), Microchip, TDK, ROHM and Infineon, and the
  generic-word matches above.
- **Paging:** the 13.6% repeats above.
The `names` step and the purity rule were added for the first two, and the page size went to
5,000 for the third.

Second pass, 2026-10-12 05:40-09:59Z, never blocked:
- `names`: 532 manufacturers, 1,296 requests. 371 lookups found EasyEDA's name (161 didn't, mostly
  manufacturers with 1-3 parts whose MPNs aren't in EasyEDA at all). STMicroelectronics went from
  0 to 79% ("ST"), Analog Devices 2% to 96% ("ADI"), Microchip 0 to 81% ("MICROCHIP"), Walsin 0 to
  73%, Samsung Electro-Mechanics 0 to 85% ("SAMSUNG"); onsemi (63%) and TDK (69%) came in under
  the purity rule. Chinese-only names work as keywords ("华星机电", 87%).
- `manufacturers --redo` at 5,000 a page for the 91 manufacturers first crawled in 2,000-result
  pages: 149 requests (Intel/Altera got the HTTP 500 above and was redone at 2,000 a page: 88%).
- `parts`: the 26 basic/preferred parts search still hadn't answered (from 994 before the second
  pass): 3 have a footprint, 23 don't.
Result: every basic and preferred part answered (basic 351 of 351 have a footprint, preferred 1,184
of 1,207), and 394,582 of 629,297 extended parts recorded as having one (234,715 unanswered,
checked live at runtime). Validation: 50 of 50 again. 397,062 rows, 39.6 MB of CSV with
timestamps (13.4 MB gzipped), 655 ambiguous parts skipped. The parts left under 50% are mostly connector makers whose single, complete result page
just doesn't cover them (TE Connectivity 19%, MOLEX 30%, Samtec 31%): those parts likely have no
EasyEDA footprint, which only `/api/products` can confirm.

## The seed (`scripts/build_easyeda_seed.py`)

Run it on your own machine: never on prod or in CI, and never alongside integration tests (both
count against your IP). It is driven by `components.db`, so each part ends up "has a footprint",
"none" or unanswered. Every step is resumable and stops on the first 403.

```bash
uv run python scripts/build_easyeda_seed.py manufacturers   # search each manufacturer, 5,000 per request, one per 10s
uv run python scripts/build_easyeda_seed.py names           # second pass with EasyEDA's names for the poorly matched ones
# wait at least 10 minutes
uv run python scripts/build_easyeda_seed.py validate        # re-check 50 search answers, one per 15s; any mismatch fails
uv run python scripts/build_easyeda_seed.py parts           # /api/products for unanswered basic/preferred parts, one per 15s
uv run python scripts/build_easyeda_seed.py report          # coverage and weak keywords
```

- `manufacturers` tries keywords in order (`KEYWORD_ALIASES`, the name before "(", the name in
  parentheses, the full name). A keyword returning over 4 results per part of ours plus 4,000 is
  too broad and skipped (its first page is still recorded), unless its first page is mostly this
  manufacturer's parts: at least half of that page's results in our DB, judged on 20 or more.
  Under 0.2 is narrow, so its results are kept and the next keyword is tried too. Paging stops at
  30 pages. `--only NAME ... --redo` searches those manufacturers again.
- `names` takes the manufacturers whose keywords found under 10% of their parts, searches up to 3
  of their MPNs (parts known to have a footprint first, then by stock), reads the manufacturer name
  EasyEDA's library gives the part, and searches that name's keywords. Keywords that were too broad
  are tried again under the purity rule.
- `parts` asks `/api/products` about unanswered parts (basic, then preferred; `--types bpe` adds
  extended by stock) and re-checks "none" answers older than `--refresh-days` (30). It and
  `validate` refuse to start within 10 minutes of a search request (`--force` overrides).
- Progress lives in `data/easyeda/seed_state.json` (not committed), including `crawl_seen`: the
  parts this crawl's searches returned, so a crawl resumed in a later run still spots a part with
  two different components. `--fresh` redoes every manufacturer, for a refresh; a crawl with no
  manufacturer progress starts a new `crawl_seen`.
- CSV columns: `lcsc,has_footprint,symbol_uuid,footprint_uuid,checked,source`, sorted by part
  number; `source` is `s` (search) or `p` (`/api/products`). `checked` is when the row's answer
  was recorded, in UTC (`2026-10-12T14:03:22Z`); the server compares it with stored answers to
  serve the newer one. A row whose answer doesn't change keeps its `checked`, so a refresh only
  rewrites the rows that changed. A "no footprint" answer takes the new time on each re-check,
  since the server re-checks those 7 days after it. The rows from 2026-10-10 and 2026-10-12 only
  had dates, so they're stamped midnight UTC.
