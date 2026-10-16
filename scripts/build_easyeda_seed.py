#!/usr/bin/env python3
"""Build data/easyeda/footprints.csv: which of our parts have an EasyEDA symbol and footprint.

Run it on your own machine, never on prod or in CI, and not while integration tests run (both use
your IP's EasyEDA rate limit). See docs/ref-easyeda-api.md.

Everything is driven by components.db, so each of our parts ends up with a state: has a
footprint, has none, or not answered yet.

Steps (each resumable; Ctrl-C saves progress):
  manufacturers  For each manufacturer in our DB, most parts first, search EasyEDA's LCSC library
                 5,000 results per request and keep the results that are parts in our DB. Search
                 only finds parts that HAVE a footprint.
  names          Second pass over manufacturers that search found under 10% of: look up the name
                 EasyEDA's library gives them (LCSC's naming, e.g. "ST" for STMicroelectronics)
                 from one of their MPNs, and search that. Big keywords are searched when their
                 first page is mostly that manufacturer's parts.
  parts          Ask /api/products about our parts that are still unanswered, one at a time:
                 basic, then preferred, then extended by stock. The only way to confirm "no
                 footprint".
  validate       Re-check a random sample of search answers on /api/products. Any mismatch fails.
  report         Coverage by library type, and manufacturers whose keyword matched poorly.

Pacing: one EasyEDA request every --delay seconds: 10 for the search steps, 15 for the
/api/products steps. Search traffic counts toward /api/products' block (on 2026-10-10 products got
a 403 on its 17th request at one per 7s, right after 133 searches at one per 7s; afterwards 65
products requests at one per 15s went through), so the parts and validate steps won't start
within 10 minutes of a search request. On the first 403 or 429 it saves and exits with
code 2; wait and run it again later.

Usage:
  uv run python scripts/build_easyeda_seed.py manufacturers [--only NAME ... [--redo]] [--max-manufacturers N] [--fresh]
  uv run python scripts/build_easyeda_seed.py names [--only NAME ...] [--max-manufacturers N]
  uv run python scripts/build_easyeda_seed.py parts [--types b,p] [--max-requests N] [--refresh-days 30]
  uv run python scripts/build_easyeda_seed.py validate [--sample 50]
  uv run python scripts/build_easyeda_seed.py report
"""

import argparse
import asyncio
import datetime
import json
import math
import os
import random
import re
import sqlite3
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pcbparts_mcp.client import JLCPCBClient  # noqa: E402
from pcbparts_mcp.easyeda_store import (  # noqa: E402
    SEED_FILE, SeedRow, answer_problem, format_checked, lcsc_number, read_seed_csv, seed_checked_at, write_seed_csv,
)

SEARCH_URL = "https://easyeda.com/api/components/search"
LCSC_OWNER_UUID = "0819f05c4eef4c71ace90d822a990e87"  # owner of every component in the LCSC library
SEARCH_FORM = (f"type=3&doctype%5B%5D=2&uid={LCSC_OWNER_UUID}&returnListStyle=classifyarr&version=6.4.7")
SEARCH_HEADERS = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://easyeda.com/editor",
    "origin": "https://easyeda.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
}

# Search keywords for manufacturers whose JLCPCB name differs from LCSC's (EasyEDA's library uses
# LCSC's names, e.g. "TI(德州仪器)" for Texas Instruments). Checked before the derived keywords.
KEYWORD_ALIASES: dict[str, str] = {
    "Texas Instruments": "TI",
}
# A keyword is too broad when it returns more than this many results per part of ours plus
# BROAD_SLACK (EasyEDA also lists out-of-stock parts: 1.3-2.5x is normal), and too narrow below the
# low ratio.
MAX_RESULTS_PER_PART = 4.0
MIN_RESULTS_PER_PART = 0.2
BROAD_SLACK = 4000
# A keyword over that ratio is still searched when its first page is mostly this manufacturer:
# LCSC lists far more parts than JLCPCB stocks for big makers (onsemi: 30,564 results for 6,495 of
# ours). A name that only matched a generic word ("Ensheng Electronics" and every other "X
# Electronics" returned the same 15,194 results) has a first page of other manufacturers' parts.
MIN_PURITY = 0.5  # share of the first page's results in our DB that are this manufacturer's
PURITY_SAMPLE = 20  # first-page results in our DB needed to judge
# Search results come back in an unstable order (2026-10-12, Nexperia, 12,909 results). Within
# the first 10,000, 5,000-result pages are nearly consistent (pages 1-2: 9,996 unique; at 2,000 a
# page about 2,900 were lost to repeats). Past 10,000, pages are mostly repeats of the first 10,000
# and vary per request: page 3 at 5,000 had 0 new results on one try and 769 of 2,909 on another.
# So a keyword over RESULT_WINDOW is only partly covered. pageSize 10,000 returns HTTP 500.
RESULT_WINDOW = 10_000
MAX_PAGE_SIZE = 5000
FALLBACK_PAGE_SIZE = 2000  # some keywords' 5,000-result pages get HTTP 500 (Intel/Altera); 2,000 works
MAX_PAGES = 30  # never page through more than this for one keyword
# names step: manufacturers whose keywords found fewer than this share of their parts get their
# EasyEDA name looked up from one of their MPNs, NAME_LOOKUPS parts at most.
LOW_COVERAGE = 0.10
NAME_LOOKUPS = 3
NAME_PAGE_SIZE = 50
SAVE_EVERY = 25  # requests between saves in the parts and validate steps
SEARCH_DELAY = 10.0
PRODUCTS_DELAY = 15.0
QUIET_AFTER_SEARCH = 600  # seconds between the last search request and a /api/products step

DEFAULT_DB = Path("data/components.db")
DEFAULT_CSV = Path("data") / SEED_FILE
DEFAULT_STATE = DEFAULT_CSV.parent / "seed_state.json"


class Blocked(Exception):
    """EasyEDA answered 403/429: stop sending."""


class SearchFailed(Exception):
    pass


class ServerError(Exception):
    """EasyEDA answered HTTP 5xx."""


def today() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def checked_now() -> str:
    """Now, as a seed row's checked value (UTC)."""
    return format_checked(time.time())


def stamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%SZ")


class Pacer:
    """At most one request per `delay` seconds."""

    def __init__(self, delay: float, clock: Callable[[], float] = time.monotonic, sleep=asyncio.sleep):
        self.delay = delay
        self._clock = clock
        self._sleep = sleep
        self._last: float | None = None
        self.requests = 0

    async def wait(self) -> None:
        if self._last is not None:
            remaining = self._last + self.delay - self._clock()
            if remaining > 0:
                await self._sleep(remaining)
        self._last = self._clock()
        self.requests += 1


@dataclass
class SearchPage:
    facet: int  # total LCSC-library results for the keyword
    items: list[tuple[str, str, str | None]]  # (lcsc, symbol_uuid, footprint_uuid)
    makers: dict[str, str] = field(default_factory=dict)  # lcsc -> manufacturer name in EasyEDA's library


def parse_search_item(item: dict[str, Any]) -> tuple[str, str, str | None] | None:
    """(lcsc, symbol_uuid, footprint_uuid) of an LCSC-library search result, or None."""
    if item.get("ownerUuid") not in (None, LCSC_OWNER_UUID):
        return None
    head = (item.get("dataStr") or {}).get("head") or {}
    lcsc = (item.get("lcsc") or {}).get("number") or (head.get("c_para") or {}).get("Supplier Part")
    symbol_uuid = item.get("uuid")
    if not lcsc or not re.fullmatch(r"C\d+", lcsc) or not symbol_uuid:
        return None
    return lcsc, symbol_uuid, head.get("puuid") or None


def search_item_maker(item: dict[str, Any]) -> str | None:
    """The manufacturer name EasyEDA's LCSC library gives a search result (LCSC's naming, e.g.
    "ADI(亚德诺)"), or None. It's `c_para.Manufacturer` now; older records used `BOM_Manufacturer`,
    and some say "null"."""
    c_para = ((item.get("dataStr") or {}).get("head") or {}).get("c_para") or {}
    for key in ("Manufacturer", "BOM_Manufacturer"):
        name = c_para.get(key)
        if isinstance(name, str) and name.strip() and name.strip().lower() != "null":
            return name.strip()
    return None


class EasyEDA:
    """The two EasyEDA calls the seed needs, one attempt each, paced."""

    def __init__(self, client: JLCPCBClient, pacer: Pacer):
        self.client = client
        self.pacer = pacer

    async def search(self, keyword: str, page: int, page_size: int) -> SearchPage:
        await self.pacer.wait()
        # Same one-attempt wafer session as the footprint checks (no retries or rotations)
        session = self.client._get_easyeda_products_session()
        body = f"{SEARCH_FORM}&wd={quote(keyword)}&page={page}&pageSize={page_size}"
        response = await session.post(SEARCH_URL, body=body, headers=SEARCH_HEADERS)
        if response.status_code in (403, 429):
            raise Blocked(f"search HTTP {response.status_code}")
        if response.status_code >= 500:
            raise ServerError(f"search HTTP {response.status_code}")
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            raise SearchFailed(f"{keyword!r} page {page}: {data.get('code')} {data.get('message')}")
        result = data.get("result") or {}
        items, makers = [], {}
        for raw in (result.get("lists") or {}).get("lcsc") or []:
            parsed = parse_search_item(raw)
            if parsed:
                items.append(parsed)
                maker = search_item_maker(raw)
                if maker:
                    makers[parsed[0]] = maker
        return SearchPage(int((result.get("facets") or {}).get("lcsc") or 0), items, makers)

    async def products(self, lcsc: str) -> SeedRow | None:
        """Live /api/products answer as a seed row; None if the lookup failed (try again later)."""
        await self.pacer.wait()
        result, status = await self.client._check_easyeda_footprint(lcsc)
        if status in ("blocked", "cooldown", "budget"):
            raise Blocked(f"/api/products {status}")
        if status != "checked":
            return None
        has = bool(result["has_easyeda_footprint"])
        problem = answer_problem(has, result["easyeda_symbol_uuid"], result["easyeda_footprint_uuid"])
        if problem is not None:  # the CSV couldn't be loaded back with this row
            print(f"{stamp()} {lcsc}: /api/products answer can't be kept ({problem}); left unanswered", flush=True)
            return None
        return SeedRow(lcsc, has, result["easyeda_symbol_uuid"], result["easyeda_footprint_uuid"], checked_now(), "p")


def make_client() -> JLCPCBClient:
    return JLCPCBClient()  # no store or seed: every check asks EasyEDA


# --- Data -------------------------------------------------------------------------------------


@dataclass
class Seed:
    """The CSV rows plus progress, saved together."""

    csv_path: Path
    state_path: Path
    rows: dict[str, SeedRow] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    ambiguous: set[str] = field(default_factory=set)  # parts with two LCSC-library components
    # Search answers seen in this crawl (a crawl spans runs), to spot parts with two different
    # LCSC-library components. Answers from an older crawl may have legitimately changed.
    seen: dict[str, tuple[str, str | None]] = field(default_factory=dict)

    @classmethod
    def load(cls, csv_path: Path, state_path: Path) -> "Seed":
        rows = read_seed_csv(csv_path) if csv_path.exists() else {}
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
        state.setdefault("manufacturers", {})
        # Rows hold the answer each part was seen with; ones /api/products answered since don't count
        seen = {lcsc: (row.symbol_uuid, row.footprint_uuid)
                for lcsc in (f"C{n}" for n in state.get("crawl_seen", []))
                if (row := rows.get(lcsc)) is not None and row.source == "s"}
        return cls(csv_path, state_path, rows, state, set(state.get("ambiguous", [])), seen)

    def save(self) -> None:
        write_seed_csv(self.csv_path, self.rows.values())
        self.state["ambiguous"] = sorted(self.ambiguous)
        self.state["crawl_seen"] = sorted(lcsc_number(lcsc) for lcsc in self.seen)
        tmp = self.state_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self.state, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        os.replace(tmp, self.state_path)

    def add_search_answer(self, lcsc: str, symbol_uuid: str, footprint_uuid: str | None) -> None:
        """Record "has a footprint" from search, unless the part is ambiguous or /api/products
        answered it on the same day or later (it's authoritative for the exact part)."""
        if lcsc in self.ambiguous or answer_problem(True, symbol_uuid, footprint_uuid) is not None:
            return  # an unusable result (malformed UUID) leaves the part to the parts step
        previous = self.seen.setdefault(lcsc, (symbol_uuid, footprint_uuid))
        if previous != (symbol_uuid, footprint_uuid):
            # Two LCSC-library components for one part: /api/products picks one, search can't tell
            # which. Leave it to the parts step.
            self.ambiguous.add(lcsc)
            existing = self.rows.get(lcsc)
            if existing is not None and existing.source == "s":
                del self.rows[lcsc]
            return
        existing = self.rows.get(lcsc)
        if existing is not None and existing.source == "p" and existing.checked[:10] >= today():
            return
        if existing is not None and existing.source == "p" and existing.has_footprint:
            return
        if existing is not None and _same_answer(existing, True, symbol_uuid, footprint_uuid):
            return  # unchanged: keep its date, so a refresh only rewrites rows whose answer changed
        self.rows[lcsc] = SeedRow(lcsc, True, symbol_uuid, footprint_uuid, checked_now(), "s")

    def add_products_answer(self, row: SeedRow) -> None:
        """Record an /api/products answer, which is authoritative. A "has a footprint" answer the
        row already holds keeps its date; "no footprint" takes the new one, since the server
        re-checks those a week after it."""
        existing = self.rows.get(row.lcsc)
        if existing is not None and row.has_footprint and _same_answer(
                existing, True, row.symbol_uuid, row.footprint_uuid):
            row = row._replace(checked=existing.checked)
        self.rows[row.lcsc] = row


def _same_answer(row: SeedRow, has_footprint: bool, symbol_uuid: str | None, footprint_uuid: str | None) -> bool:
    return (row.has_footprint, row.symbol_uuid, row.footprint_uuid) == (has_footprint, symbol_uuid, footprint_uuid)


def open_db(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise SystemExit(f"{path} not found; build it first: uv run python scripts/build_database.py")
    return sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)  # file:///C:/... on Windows


def manufacturers_by_size(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    return conn.execute(
        "SELECT manufacturer, COUNT(*) FROM components WHERE manufacturer IS NOT NULL AND manufacturer != '' "
        "GROUP BY manufacturer ORDER BY COUNT(*) DESC, manufacturer"
    ).fetchall()


def keyword_candidates(manufacturer: str) -> list[str]:
    """Search keywords to try for a manufacturer, best first.

    JLCPCB names often read "SHORT(Long Name)"; EasyEDA indexes LCSC's name, which usually shares
    the short form.
    """
    candidates = []
    if manufacturer in KEYWORD_ALIASES:
        candidates.append(KEYWORD_ALIASES[manufacturer])
    base, _, rest = manufacturer.partition("(")
    candidates.append(base.strip())
    inner = rest.rsplit(")", 1)[0].strip() if rest else ""
    if inner:
        candidates.append(inner.partition("(")[0].strip())
    candidates.append(manufacturer.strip())
    seen: list[str] = []
    for c in candidates:
        if len(c) >= 2 and c not in seen:
            seen.append(c)
    return seen


def keyword_fit(facet: int, our_parts: int, purity: float | None = None) -> str:
    """"ok", "broad" or "narrow" for a keyword's result count against our part count. `purity` is
    from first_page_purity(); a keyword over the ratio is still ok when it's pure enough."""
    if facet > MAX_RESULTS_PER_PART * our_parts + BROAD_SLACK:
        if purity is not None and purity >= MIN_PURITY:
            return "ok"
        return "broad"
    if our_parts >= 50 and facet < MIN_RESULTS_PER_PART * our_parts:
        return "narrow"
    return "ok"


def first_page_purity(page: SearchPage, ours: dict[str, str], manufacturer: str) -> float | None:
    """Share of the page's results in our DB that belong to `manufacturer`; None when too few of
    them are in our DB to judge."""
    in_ours = [lcsc for lcsc, _, _ in page.items if lcsc in ours]
    if len(in_ours) < PURITY_SAMPLE:
        return None
    return sum(ours[lcsc] == manufacturer for lcsc in in_ours) / len(in_ours)


# --- Steps ------------------------------------------------------------------------------------


async def run_manufacturers(seed: Seed, db: sqlite3.Connection, easyeda: EasyEDA, page_size: int,
                            only: list[str] | None, max_manufacturers: int | None, redo: bool = False) -> None:
    ours = {lcsc: mfr for lcsc, mfr in db.execute("SELECT lcsc, manufacturer FROM components")}
    manufacturers = manufacturers_by_size(db)
    if only:
        wanted = set(only)
        manufacturers = [m for m in manufacturers if m[0] in wanted]
        missing = wanted - {m[0] for m in manufacturers}
        if missing:
            print(f"Not in our DB (check the exact name): {sorted(missing)}")
    progress = seed.state["manufacturers"]
    todo = [m for m in manufacturers if redo or not progress.get(m[0], {}).get("done")]
    if max_manufacturers is not None:
        todo = todo[:max_manufacturers]
    print(f"{stamp()} manufacturers: {len(todo)} to do ({len(manufacturers) - len(todo)} done or skipped)")
    if not progress:
        seed.seen.clear()  # a new crawl
    failures = 0

    for index, (manufacturer, our_parts) in enumerate(todo, 1):
        entry = progress.setdefault(manufacturer, {})
        entry.update(our_parts=our_parts, date=today())
        try:
            tried, used, matched = await _search_manufacturer(seed, easyeda, manufacturer, our_parts, page_size,
                                                              ours)
        except Blocked:
            raise
        except Exception as e:  # timeout, connection, odd response: skip it, it stays "to do"
            failures += 1
            print(f"{stamp()} [{index}/{len(todo)}] {manufacturer}: failed ({type(e).__name__}: {e}); "
                  "will retry next run", flush=True)
            if failures >= 5:
                raise SystemExit("5 manufacturers failed in a row; check the connection and run again") from e
            continue
        failures = 0
        seed.state["last_search_at"] = time.time()
        entry.update(tried=tried, keywords=used, matched=len(matched), coverage=round(len(matched) / our_parts, 3),
                     done=True)
        if used:
            pages = ", ".join(f"{t['keyword']!r}: {t['returned']} results, {t['unique']} unique"
                              for t in tried if "returned" in t)
            print(f"{stamp()} [{index}/{len(todo)}] {manufacturer}: {len(matched)}/{our_parts} of its parts found "
                  f"({len(matched) / our_parts:.0%}) via {pages}", flush=True)
        else:
            print(f"{stamp()} [{index}/{len(todo)}] {manufacturer}: every keyword too broad {tried}; "
                  "left to the parts step", flush=True)
        seed.save()


async def _search_manufacturer(seed: Seed, easyeda: EasyEDA, manufacturer: str, our_parts: int, page_size: int,
                               ours: dict[str, str], candidates: list[str] | None = None,
                               ) -> tuple[list[dict], list[str], set[str]]:
    """Search a manufacturer's keywords (default: keyword_candidates) until one fits; returns
    (tried, keywords used, its parts found)."""
    tried: list[dict] = []
    used: list[str] = []
    matched: set[str] = set()
    for keyword in keyword_candidates(manufacturer) if candidates is None else candidates:
        try:
            attempt, found = await _search_keyword(seed, easyeda, keyword, manufacturer, our_parts, page_size,
                                                   ours)
        except ServerError:
            if page_size <= FALLBACK_PAGE_SIZE:
                raise
            attempt, found = await _search_keyword(seed, easyeda, keyword, manufacturer, our_parts,
                                                   FALLBACK_PAGE_SIZE, ours)
            attempt["page_size"] = FALLBACK_PAGE_SIZE
        tried.append(attempt)
        if attempt["fit"] == "broad":
            continue  # too many requests for too few of our parts; try a narrower keyword
        used.append(keyword)
        matched |= found
        if attempt["fit"] == "ok":
            break  # a narrow keyword keeps its results, but the next candidate may find more
    return tried, used, matched


async def _search_keyword(seed: Seed, easyeda: EasyEDA, keyword: str, manufacturer: str, our_parts: int,
                          page_size: int, ours: dict[str, str]) -> tuple[dict, set[str]]:
    """Judge a keyword on its first page and, unless it's too broad, record all its pages.
    Returns (the attempt for the manufacturer's "tried" list, its parts found)."""
    first = await easyeda.search(keyword, 1, page_size)
    purity = first_page_purity(first, ours, manufacturer)
    fit = keyword_fit(first.facet, our_parts, purity)
    pages = min(math.ceil(first.facet / page_size), MAX_PAGES)
    attempt = {"keyword": keyword, "facet": first.facet, "pages": pages, "fit": fit}
    if purity is not None:
        attempt["purity"] = round(purity, 2)
    if first.facet > RESULT_WINDOW:
        attempt["capped"] = True  # results past RESULT_WINDOW are only partly reachable
    if fit == "broad":
        # The first page is already here, and its answers are as good as any
        for lcsc, symbol_uuid, footprint_uuid in first.items:
            if lcsc in ours:
                seed.add_search_answer(lcsc, symbol_uuid, footprint_uuid)
        return attempt, set()
    found, attempt["returned"], attempt["unique"] = await _fetch_pages(
        seed, easyeda, keyword, first, pages, page_size, ours, manufacturer)
    return attempt, found


async def _fetch_pages(seed: Seed, easyeda: EasyEDA, keyword: str, first: SearchPage, pages: int, page_size: int,
                       ours: dict[str, str], manufacturer: str) -> tuple[set[str], int, int]:
    """Record every result that's one of our parts. Returns (the ones that belong to `manufacturer`,
    results returned, unique parts among them). Fewer unique than returned means the result order
    shifted between pages, so some results were skipped."""
    matched: set[str] = set()
    returned = 0
    unique: set[str] = set()
    page_items = first.items
    for page in range(1, pages + 1):
        if page > 1:
            page_items = (await easyeda.search(keyword, page, page_size)).items
        returned += len(page_items)
        for lcsc, symbol_uuid, footprint_uuid in page_items:
            unique.add(lcsc)
            if lcsc in ours:
                seed.add_search_answer(lcsc, symbol_uuid, footprint_uuid)
                if ours[lcsc] == manufacturer:
                    matched.add(lcsc)
    return matched, returned, len(unique)


def describe_tried(tried: list[dict]) -> str:
    return "; ".join(
        f"{t['keyword']!r}: {t['returned']} results, {t['unique']} unique" if "returned" in t
        else f"{t['keyword']!r}: {t['fit']} ({t['facet']} results"
             + (f", purity {t['purity']}" if "purity" in t else "") + ")"
        for t in tried) or "nothing new to search"


async def run_names(seed: Seed, db: sqlite3.Connection, easyeda: EasyEDA, page_size: int,
                    only: list[str] | None, max_manufacturers: int | None) -> None:
    """Second pass over manufacturers whose keywords found under LOW_COVERAGE of their parts, or were
    all too broad. EasyEDA's library uses LCSC's manufacturer names, which often differ from
    JLCPCB's ("ST" for STMicroelectronics), so search a few of their MPNs, read the name EasyEDA
    gives the part, and search that. Keywords that were too broad are tried again under the purity
    rule."""
    ours: dict[str, str] = {}
    by_maker: dict[str, list[str]] = {}
    for lcsc, maker in db.execute("SELECT lcsc, manufacturer FROM components"):
        ours[lcsc] = maker
        by_maker.setdefault(maker, []).append(lcsc)
    todo = sorted(((m, e) for m, e in seed.state["manufacturers"].items()
                   if e.get("done") and e.get("coverage", 0) < LOW_COVERAGE and "lcsc_name" not in e
                   and m in by_maker),
                  key=lambda me: (-len(by_maker[me[0]]), me[0]))
    if only:
        todo = [me for me in todo if me[0] in set(only)]
    if max_manufacturers is not None:
        todo = todo[:max_manufacturers]
    print(f"{stamp()} names: {len(todo)} manufacturer(s) with under {LOW_COVERAGE:.0%} of their parts found")
    failures = 0

    for index, (manufacturer, entry) in enumerate(todo, 1):
        our_parts = len(by_maker[manufacturer])
        used_before = entry.get("keywords") or []
        try:
            name = await _lookup_lcsc_name(seed, db, easyeda, manufacturer, ours)
            retry = [t["keyword"] for t in entry.get("tried", []) if t.get("fit") == "broad"]
            candidates = [k for k in dict.fromkeys([*(keyword_candidates(name) if name else []), *retry])
                          if k not in used_before]
            tried, used, _ = await _search_manufacturer(seed, easyeda, manufacturer, our_parts, page_size, ours,
                                                        candidates)
        except Blocked:
            raise
        except Exception as e:  # timeout, connection, odd response: skip it, it stays "to do"
            failures += 1
            print(f"{stamp()} [{index}/{len(todo)}] {manufacturer}: failed ({type(e).__name__}: {e}); "
                  "will retry next run", flush=True)
            if failures >= 5:
                raise SystemExit("5 manufacturers failed in a row; check the connection and run again") from e
            continue
        failures = 0
        seed.state["last_search_at"] = time.time()
        found = sum(1 for lcsc in by_maker[manufacturer] if (row := seed.rows.get(lcsc)) and row.has_footprint)
        entry.update(lcsc_name=name, tried=entry.get("tried", []) + tried, keywords=used_before + used,
                     matched=found, coverage=round(found / our_parts, 3), date=today())
        print(f"{stamp()} [{index}/{len(todo)}] {manufacturer}: EasyEDA name {name!r}, {found}/{our_parts} of its "
              f"parts found ({found / our_parts:.0%}); {describe_tried(tried)}", flush=True)
        seed.save()


async def _lookup_lcsc_name(seed: Seed, db: sqlite3.Connection, easyeda: EasyEDA, manufacturer: str,
                            ours: dict[str, str]) -> str | None:
    """The name EasyEDA's library gives `manufacturer`, from a search for one of its MPNs (parts
    already known to have a footprint first, then by stock), or None if NAME_LOOKUPS of them
    don't turn up. Any results that are our parts are recorded on the way."""
    parts = db.execute("SELECT lcsc, mpn FROM components WHERE manufacturer = ? AND mpn IS NOT NULL AND mpn != '' "
                       "ORDER BY stock DESC, lcsc", (manufacturer,)).fetchall()
    parts.sort(key=lambda p: not ((row := seed.rows.get(p[0])) and row.has_footprint))  # stable sort
    for lcsc, mpn in parts[:NAME_LOOKUPS]:
        page = await easyeda.search(mpn, 1, NAME_PAGE_SIZE)
        for item_lcsc, symbol_uuid, footprint_uuid in page.items:
            if item_lcsc in ours:
                seed.add_search_answer(item_lcsc, symbol_uuid, footprint_uuid)
        if lcsc in page.makers:
            return page.makers[lcsc]
    return None


def parts_todo(seed: Seed, db: sqlite3.Connection, types: str, refresh_days: int) -> list[str]:
    """Our parts to ask /api/products about: unanswered first, then stale "no footprint" answers.
    Basic, then preferred, then extended, each by stock."""
    rank = {t: i for i, t in enumerate(types)}
    ordered = sorted(
        ((lcsc, lib, stock or 0) for lcsc, lib, stock in
         db.execute("SELECT lcsc, library_type, stock FROM components") if lib in rank),
        key=lambda p: (rank[p[1]], -p[2]),
    )
    cutoff = format_checked(seed_checked_at(checked_now()) - refresh_days * 86400)
    unanswered = [lcsc for lcsc, _, _ in ordered if lcsc not in seed.rows]
    stale = [lcsc for lcsc, _, _ in ordered
             if lcsc in seed.rows and not seed.rows[lcsc].has_footprint and seed.rows[lcsc].checked < cutoff]
    return unanswered + stale


async def run_parts(seed: Seed, db: sqlite3.Connection, easyeda: EasyEDA, types: str, max_requests: int | None,
                    refresh_days: int) -> None:
    todo = parts_todo(seed, db, types, refresh_days)
    if max_requests is not None:
        todo = todo[:max_requests]
    eta = datetime.timedelta(seconds=round(len(todo) * easyeda.pacer.delay))
    print(f"{stamp()} parts: {len(todo)} to check (types {types}), about {eta} at one per {easyeda.pacer.delay:g}s")
    found = none = failed = 0
    for index, lcsc in enumerate(todo, 1):
        row = await easyeda.products(lcsc)
        if row is None:
            failed += 1
        else:
            seed.add_products_answer(row)
            found += row.has_footprint
            none += not row.has_footprint
        if index % SAVE_EVERY == 0 or index == len(todo):
            seed.save()
            print(f"{stamp()} parts {index}/{len(todo)}: {found} have a footprint, {none} don't, {failed} failed",
                  flush=True)


async def run_validate(seed: Seed, easyeda: EasyEDA, sample: int) -> int:
    """Check search answers against /api/products; returns the number of mismatches."""
    pool = sorted(lcsc for lcsc, r in seed.rows.items() if r.source == "s")
    picks = random.sample(pool, min(sample, len(pool)))
    print(f"{stamp()} validate: {len(picks)} of {len(pool)} search answers")
    mismatches = checked = 0
    for index, lcsc in enumerate(picks, 1):
        expected = seed.rows[lcsc]
        live = await easyeda.products(lcsc)
        if live is None:
            continue
        checked += 1
        same = (live.has_footprint, live.symbol_uuid, live.footprint_uuid) == (
            expected.has_footprint, expected.symbol_uuid, expected.footprint_uuid)
        if not same:
            mismatches += 1
            print(f"  MISMATCH {lcsc}: search {expected.symbol_uuid}/{expected.footprint_uuid}, "
                  f"/api/products has={live.has_footprint} {live.symbol_uuid}/{live.footprint_uuid}")
        seed.add_products_answer(live)  # /api/products is authoritative either way
        if index % SAVE_EVERY == 0 or index == len(picks):
            seed.save()
    print(f"{stamp()} validate: {checked} checked, {mismatches} mismatch(es)")
    return mismatches


def report(seed: Seed, db: sqlite3.Connection) -> str:
    lines = []
    rows = seed.rows
    by_type: dict[str, list[int]] = {}
    by_maker: dict[str, list[int]] = {}  # parts, has a footprint
    for lcsc, lib, maker in db.execute("SELECT lcsc, library_type, manufacturer FROM components"):
        counts = by_type.setdefault(lib, [0, 0, 0, 0])  # parts, has, none, unanswered
        counts[0] += 1
        row = rows.get(lcsc)
        counts[1 if row and row.has_footprint else 2 if row else 3] += 1
        found = by_maker.setdefault(maker, [0, 0])
        found[0] += 1
        found[1] += bool(row and row.has_footprint)
    names = {"b": "basic", "p": "preferred", "e": "extended"}
    lines.append(f"{'type':<10}{'parts':>9}{'has':>9}{'none':>9}{'unanswered':>12}")
    for lib in ("b", "p", "e"):
        parts, has, none, unanswered = by_type.get(lib, [0, 0, 0, 0])
        lines.append(f"{names[lib]:<10}{parts:>9,}{has:>9,}{none:>9,}{unanswered:>12,}")
    sources = {"s": 0, "p": 0}
    for r in rows.values():
        sources[r.source] = sources.get(r.source, 0) + 1
    size = seed.csv_path.stat().st_size if seed.csv_path.exists() else 0
    lines.append(f"rows: {len(rows):,} ({sources['s']:,} from search, {sources['p']:,} from /api/products), "
                 f"ambiguous skipped: {len(seed.ambiguous)}, CSV {size / 1e6:.1f} MB")
    # Found counts come from the seed: crawls return results in a different order each time, so
    # the seed holds more than any one crawl's "matched".
    done = {m: e for m, e in seed.state["manufacturers"].items() if e.get("done") and m in by_maker}
    low = sorted((m for m in done if by_maker[m][0] >= 100 and by_maker[m][1] < 0.5 * by_maker[m][0]),
                 key=lambda m: -by_maker[m][0])
    lines.append(f"manufacturers done: {len(done):,}; under 50% with a footprint (100+ parts): {len(low)}")
    for m in low[:25]:
        e = done[m]
        lines.append(f"  {m}: {by_maker[m][1]}/{by_maker[m][0]} via {e.get('keywords')} (tried {e.get('tried')})")
    return "\n".join(lines)


# --- CLI --------------------------------------------------------------------------------------


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("step", choices=["manufacturers", "names", "parts", "validate", "report"])
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--delay", type=float,
                        help=f"seconds between EasyEDA requests (default {SEARCH_DELAY:g} for search, "
                             f"{PRODUCTS_DELAY:g} for /api/products steps)")
    parser.add_argument("--force", action="store_true",
                        help=f"start a /api/products step within {QUIET_AFTER_SEARCH // 60} min of a search request")
    parser.add_argument("--page-size", type=int, default=MAX_PAGE_SIZE)
    parser.add_argument("--only", nargs="+", help="manufacturers and names steps: just these (exact DB names)")
    parser.add_argument("--max-manufacturers", type=int)
    parser.add_argument("--fresh", action="store_true", help="manufacturers step: redo every manufacturer")
    parser.add_argument("--redo", action="store_true", help="manufacturers step: search the --only ones again")
    parser.add_argument("--types", default="bp", help="parts step: library types in order (default bp; bpe for all)")
    parser.add_argument("--max-requests", type=int)
    parser.add_argument("--refresh-days", type=int, default=30,
                        help="parts step: re-check 'no footprint' answers older than this")
    parser.add_argument("--sample", type=int, default=50)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(line_buffering=True)  # progress shows up live when redirected to a log
    if args.delay is None:
        args.delay = SEARCH_DELAY if args.step in ("manufacturers", "names") else PRODUCTS_DELAY
    if args.delay < 6:
        parser.error("--delay under 6s can cross EasyEDA's limit (24 requests per 2 minutes)")
    if args.redo and not args.only:
        parser.error("--redo needs --only (use --fresh to redo every manufacturer)")
    if not 1 <= args.page_size <= MAX_PAGE_SIZE:
        parser.error(f"--page-size must be 1-{MAX_PAGE_SIZE} (EasyEDA answers HTTP 500 to 10,000)")

    seed = Seed.load(args.csv, args.state)
    db = open_db(args.db)
    if args.step == "report":
        print(report(seed, db))
        return 0
    if args.fresh:
        seed.state["manufacturers"] = {}
        seed.ambiguous.clear()
    if args.step in ("parts", "validate") and not args.force:
        since = time.time() - seed.state.get("last_search_at", 0)
        if since < QUIET_AFTER_SEARCH:
            print(f"Last search request was {since / 60:.0f} min ago; /api/products steps wait "
                  f"{QUIET_AFTER_SEARCH // 60} min after search traffic (or pass --force).")
            return 3

    async def run() -> int:
        client = make_client()
        easyeda = EasyEDA(client, Pacer(args.delay))
        try:
            if args.step == "manufacturers":
                await run_manufacturers(seed, db, easyeda, args.page_size, args.only, args.max_manufacturers,
                                        args.redo)
            elif args.step == "names":
                await run_names(seed, db, easyeda, args.page_size, args.only, args.max_manufacturers)
            elif args.step == "parts":
                await run_parts(seed, db, easyeda, args.types.replace(",", ""), args.max_requests, args.refresh_days)
            elif args.step == "validate":
                return 1 if await run_validate(seed, easyeda, args.sample) else 0
            return 0
        except Blocked as e:
            print(f"{stamp()} EasyEDA blocked this IP ({e}) after {easyeda.pacer.requests} request(s). Progress "
                  "saved; stop all EasyEDA traffic and run this again in a few minutes.")
            return 2
        finally:
            seed.save()
            await client.close()
            print(f"{stamp()} {easyeda.pacer.requests} EasyEDA request(s) this run")

    try:
        return asyncio.run(run())
    except KeyboardInterrupt:
        print("Interrupted; progress saved.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
