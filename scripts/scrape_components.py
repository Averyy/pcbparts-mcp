#!/usr/bin/env python3
"""
Scrape all JLCPCB components for local database.

Uses concurrent workers with wafer for anti-detection HTTP to avoid rate limiting.
Outputs a sorted catalog with separate stock and weekly price files.

Usage:
    python scripts/scrape_components.py [--resume] [--workers N]
"""

import argparse
import asyncio
import gzip
import json
import logging
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from collections.abc import Iterable
from typing import Any

import wafer
from wafer import ChallengeDetected, ConnectionFailed, RateLimited, WaferTimeout

# Add parent directory to path for imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pcbparts_mcp.config import DEFAULT_MIN_STOCK
from pcbparts_mcp.catalog_files import read_catalog, read_prices, write_catalog

# Configure logging for scraper output
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # Simple format for CLI output
)
logger = logging.getLogger(__name__)

# === Configuration ===

JLCPCB_SEARCH_URL = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
STOCK_THRESHOLD = DEFAULT_MIN_STOCK  # Minimum stock to include in database
PAGE_SIZE = 100
REQUEST_TIMEOUT = 30.0   # Total budget per call (wafer>=0.2 counts retries+rotations against it).
ATTEMPT_TIMEOUT = 10.0   # Per-attempt cap so the 10-rotation budget can actually fire under 403 storms.
MAX_RETRIES = 3
EMPTY_PAGE_RETRIES = 2   # Re-requests of a page that came back empty before the listed total
WORKER_STAGGER = 0.1
GZIP_LEVEL = 9


def create_scraper_session() -> wafer.AsyncSession:
    """Create a wafer session configured for JLCPCB scraping."""
    return wafer.AsyncSession(
        timeout=REQUEST_TIMEOUT,
        attempt_timeout=ATTEMPT_TIMEOUT,
        max_retries=MAX_RETRIES,
        max_rotations=10,
        max_failures=None,  # Disable session retirement — 403s during rotation are expected
        rate_limit=0.3,
        rate_jitter=0.0,
        cache_dir=None,
        rotate_every=1,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
        },
    )


# === Data Classes ===

@dataclass
class Subcategory:
    id: int
    name: str
    category_id: int
    category_name: str
    category_slug: str
    count: int = 0


@dataclass
class ScrapeProgress:
    """Tracks scrape progress for resume capability."""
    started_at: str = ""
    completed_subcategories: set[int] = field(default_factory=set)
    failed_subcategories: set[int] = field(default_factory=set)
    category_counts: dict[str, int] = field(default_factory=dict)
    total_parts: int = 0

    def to_dict(self) -> dict:
        return {
            "started_at": self.started_at,
            "completed_subcategories": list(self.completed_subcategories),
            "failed_subcategories": list(self.failed_subcategories),
            "category_counts": self.category_counts,
            "total_parts": self.total_parts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScrapeProgress":
        return cls(
            started_at=data.get("started_at", ""),
            completed_subcategories=set(data.get("completed_subcategories", [])),
            failed_subcategories=set(data.get("failed_subcategories", [])),
            category_counts=data.get("category_counts", {}),
            total_parts=data.get("total_parts", 0),
        )


# === Helper Functions ===

def slugify(name: str) -> str:
    """Convert category name to filename-safe slug."""
    # Lowercase, replace spaces and special chars with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower())
    # Remove leading/trailing hyphens
    return slug.strip("-")


def transform_part(item: dict[str, Any], subcategory_id: int) -> dict[str, Any]:
    """Transform API response to our compact schema."""
    # Get price from first tier (`or []` guards against componentPrices being null;
    # bracket access on the tier is deliberate — a malformed tier should fail loud)
    prices = item.get("componentPrices") or []
    price = prices[0]["productPrice"] if prices else None

    # Determine library type: b=basic, p=preferred (no fee), e=extended ($3)
    lib_type = item.get("componentLibraryType", "")
    preferred = item.get("preferredComponentFlag", False)

    if lib_type == "base":
        t = "b"
    elif preferred:
        t = "p"  # Extended but preferred = no fee
    else:
        t = "e"  # Extended, not preferred = $3 fee

    # Transform attributes to compact [name, value] array
    attrs = item.get("attributes") or []
    attributes = [
        [a.get("attribute_name_en", ""), a.get("attribute_value_name", "")]
        for a in attrs
        if a.get("attribute_name_en")
    ]

    part = {
        "l": item.get("componentCode"),  # lcsc
        "m": item.get("componentModelEn"),  # mpn
        "f": item.get("componentBrandEn"),  # manufacturer
        "p": item.get("componentSpecificationEn"),  # package
        "s": item.get("stockCount"),  # stock
        "t": t,  # type (b/p/e)
        "c": subcategory_id,  # subcategory_id (passed from scrape context)
        "$": round(price, 4) if price is not None else None,  # price
        "d": item.get("describe"),  # description
        "a": attributes,  # attributes
        # JLCPCB's PCBA type: 0 = Economic and Standard assembly, 2 = Standard only (checked against
        # 11 part pages and a whole subcategory, 2026-11-03). Its presence also marks data that has "n".
        "x": item.get("componentProductType"),
    }
    # No datasheet of any kind on JLCPCB (about 3% of parts): only then, to keep the files small
    if not any(item.get(k) for k in ("dataManualUrl", "dataManualFileAccessIdUrl", "dataManualOfficialLink")):
        part["n"] = 1
    return part


# === API Functions ===

async def make_request(
    params: dict[str, Any],
    session: wafer.AsyncSession,
) -> dict[str, Any]:
    """Make a single request. Wafer handles retries, rotation, and rate limiting."""
    try:
        response = await session.post(
            JLCPCB_SEARCH_URL,
            json=params,
            headers={
                "Origin": "https://jlcpcb.com",
                "Referer": "https://jlcpcb.com/parts",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
            },
        )
    except ChallengeDetected as e:
        raise ValueError(f"JLCPCB WAF challenge detected ({e.challenge_type})")
    except RateLimited:
        raise ValueError("JLCPCB rate limited (rotations exhausted)")
    except ConnectionFailed as e:
        raise ValueError(f"JLCPCB connection failed ({e.reason})")
    except WaferTimeout:
        raise ValueError("JLCPCB request timed out")
    response.raise_for_status()
    data = response.json()

    if data.get("code") != 200:
        raise ValueError(f"API error: {data.get('message', 'Unknown')}")

    return data


async def fetch_categories(session: wafer.AsyncSession) -> list[dict[str, Any]]:
    """Fetch all categories and subcategories from API."""
    params = {
        "currentPage": 1,
        "pageSize": 1,
        "searchSource": "search",
        "searchType": 3,
    }

    data = await make_request(params, session)
    sort_list = data.get("data", {}).get("sortAndCountVoList", [])

    categories = []
    for cat in sort_list:
        subcategories = []
        for sub in cat.get("childSortList") or []:
            subcategories.append({
                "id": sub.get("componentSortKeyId"),
                "name": sub.get("sortName"),
                "count": sub.get("componentCount", 0),
            })

        categories.append({
            "id": cat.get("componentSortKeyId"),
            "name": cat.get("sortName"),
            "count": cat.get("componentCount", 0),
            "subcategories": subcategories,
        })

    return categories


async def scrape_subcategory(
    subcat: Subcategory,
    session: wafer.AsyncSession,
) -> tuple[list[dict[str, Any]], int]:
    """Scrape all parts from a subcategory. Returns (parts, total_count)."""
    parts = []
    page = 1
    empty_retries = 0

    while True:
        params = {
            "currentPage": page,
            "pageSize": PAGE_SIZE,
            "searchSource": "search",
            "startStockNumber": STOCK_THRESHOLD,
            "searchType": 3,
            "firstSortId": subcat.category_id,
            "firstSortName": subcat.category_name,
            "secondSortId": subcat.id,
            "secondSortName": subcat.name,
        }

        data = await make_request(params, session)
        page_info = data.get("data", {}).get("componentPageInfo", {})
        items = page_info.get("list", [])
        total = page_info.get("total", 0)

        if not items:
            # An empty page while the API still lists more parts is a dropped page, not the end
            # of the subcategory: stopping here used to publish the subcategory short.
            if len(parts) < total and empty_retries < EMPTY_PAGE_RETRIES:
                empty_retries += 1
                logger.warning(f"  {subcat.name}: empty page {page} with {len(parts)} of {total} "
                               f"listed parts collected; retrying it")
                continue
            break
        empty_retries = 0  # per page: an earlier page's retries don't use up a later page's

        for item in items:
            parts.append(transform_part(item, subcat.id))

        # Check if more pages
        if page * PAGE_SIZE >= total:
            break

        page += 1

    if len(parts) < total:
        logger.warning(f"  {subcat.name}: collected {len(parts)} of {total} listed parts")
    return parts, len(parts)


# === Worker Functions ===

class CircuitBreaker:
    """Tracks consecutive failures and triggers abort if threshold exceeded."""
    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self.consecutive_failures = 0
        self.tripped = False
        self._lock = asyncio.Lock()

    async def record_success(self):
        async with self._lock:
            self.consecutive_failures = 0

    async def record_failure(self) -> bool:
        """Record failure. Returns True if circuit breaker tripped."""
        async with self._lock:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.threshold:
                self.tripped = True
            return self.tripped

    def is_tripped(self) -> bool:
        return self.tripped


async def worker(
    worker_id: int,
    session: wafer.AsyncSession,
    queue: asyncio.Queue[Subcategory | None],
    results: dict[str, list[dict[str, Any]]],
    progress: ScrapeProgress,
    results_lock: asyncio.Lock,
    circuit_breaker: CircuitBreaker,
):
    """Worker coroutine that processes subcategories from queue."""
    while True:
        # Check circuit breaker before processing
        if circuit_breaker.is_tripped():
            # Drain remaining items from queue
            try:
                while True:
                    queue.get_nowait()
                    queue.task_done()
            except asyncio.QueueEmpty:
                pass
            break

        subcat = await queue.get()

        if subcat is None:
            queue.task_done()
            break

        try:
            t0 = time.time()
            parts, count = await scrape_subcategory(subcat, session)
            elapsed = time.time() - t0

            async with results_lock:
                # Add parts to category bucket
                if subcat.category_slug not in results:
                    results[subcat.category_slug] = []
                results[subcat.category_slug].extend(parts)

                # Update progress
                progress.completed_subcategories.add(subcat.id)
                progress.failed_subcategories.discard(subcat.id)
                progress.category_counts[subcat.category_slug] = (
                    progress.category_counts.get(subcat.category_slug, 0) + count
                )
                progress.total_parts += count

            await circuit_breaker.record_success()
            if count == 0:
                status = "empty"
            elif elapsed < 60:
                status = f"{count:,} parts ({elapsed:.1f}s)"
            else:
                status = f"{count:,} parts ({elapsed/60:.1f}m)"
            logger.info(f"  [W{worker_id}] {subcat.name}: {status}")

        except Exception as e:
            async with results_lock:
                progress.failed_subcategories.add(subcat.id)

            tripped = await circuit_breaker.record_failure()
            logger.error(f"  [W{worker_id}] {subcat.name}: FAILED - {e}")

            if tripped:
                logger.error(f"\n  CIRCUIT BREAKER TRIPPED - {circuit_breaker.threshold} consecutive failures!")
                logger.error("  Aborting scrape...")

        queue.task_done()


# === Stock History ===

HISTORY_HIGH_STOCK_CAP = 1000  # Don't track stock changes for parts above this level

# Scrape gaps (carry_over_gaps), set from the 263 daily catalog snapshots in git (2026-02-21 to
# 2026-11-11). On the four gap days (03-03, 03-16, 03-18, 05-15) 5 to 42 subcategories each lost
# >=100 parts and >=10% at once, and 97-100% of every one of them was back the next day. On all
# other days at most 2 subcategories lost that much, never more than 320 parts each, and none
# came back: those were delistings (04-02 sub 2008 lost all 128, 07-17 sub 2090 320 of 865).
GAP_MIN_LOST = 100           # a bulk loss: at least this many parts...
GAP_MIN_FRACTION = 0.1       # ...and this share of the subcategory, missing at once
GAP_MIN_SUBCATEGORIES = 3    # a gap day has this many bulk losses...
GAP_SURE_LOST = 1000         # ...or a single bulk loss this large
GAP_MAX_DAYS = 2             # carried on the gap's first day and the next; then the loss is accepted


def generate_stock_history(
    previous_catalog_dir: Path,
    history_dir: Path,
    results: dict[str, list[dict[str, Any]]],
    *,
    now: datetime | None = None,
) -> dict[str, int]:
    """Compare the previous catalog with new scrape results and record stock changes.

    Writes data/history/YYYY-MM/YYYY-MM-DD.jsonl.gz as gzip multi-stream append.
    Returns stats dict with event counts.

    Note: Iterates results directly (no intermediate dict) to reduce peak memory.
    Cross-category duplicate LCSCs are deduplicated via seen_lcsc set.
    """
    today = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%Y-%m-%d")
    month = today[:7]  # YYYY-MM

    # Load the previous snapshot: {lcsc: (stock, price, lib_type)}
    old_data: dict[str, tuple[int, float | None, str | None]] = {}
    if (previous_catalog_dir / "stock.tsv").exists():
        # Without prices.tsv this scrape rebuilds every price (write_scrape_outputs); history still
        # compares stock, and gone events then carry no price.
        with_prices = (previous_catalog_dir / "prices.tsv").exists()
        for _, part in read_catalog(previous_catalog_dir, prices=with_prices):
            old_data[part["l"]] = (part.get("s") or 0, part.get("$"), part.get("t"))

    if not old_data:
        logger.info("No old data found — skipping history generation")
        return {"skipped": True}

    # Generate events by iterating results directly (avoids building a second large dict)
    events: list[dict] = []
    stats: dict[str, int] = {}
    seen_lcsc: set[str] = set()  # Track new LCSCs for "gone" detection + cross-category dedup

    def should_track_delta(stock: int, delta: int) -> bool:
        """Apply tiered thresholds — don't track high-stock noise."""
        if stock > HISTORY_HIGH_STOCK_CAP:
            return False
        if stock > 500:
            return abs(delta) > 100
        if stock > 100:
            return abs(delta) > 25
        return abs(delta) > 10

    def add_event(event: dict) -> None:
        """Append event and update stats inline."""
        # Actual previous snapshot stock, never inferred from the last event.
        # A newly seen part has no previous observation (not a known zero).
        previous = old_data.get(event["l"])
        event["before"] = previous[0] if previous is not None else None
        events.append(event)
        etype = event.get("e", "change")
        stats[etype] = stats.get(etype, 0) + 1

    # Check all parts in new data
    for parts_list in results.values():
        for part in parts_list:
            lcsc = part.get("l")
            if not lcsc or lcsc in seen_lcsc:
                continue
            seen_lcsc.add(lcsc)

            new_stock = part.get("s") or 0
            new_price = part.get("$")
            new_type = part.get("t")

            if lcsc in old_data:
                old_stock, old_price, old_type = old_data[lcsc]

                # Reappeared (was 0, now has stock) — takes priority over stock change
                if old_stock == 0 and new_stock > 0:
                    add_event({
                        "l": lcsc, "d": today,
                        "s": new_stock, "$": new_price, "t": new_type,
                        "e": "reappear",
                    })
                else:
                    # Stock change (skip if reappearing — that's already tracked)
                    delta = new_stock - old_stock
                    if delta != 0 and should_track_delta(new_stock, delta):
                        add_event({
                            "l": lcsc, "d": today,
                            "s": new_stock, "$": new_price, "t": new_type,
                        })

                # Library type change (independent of stock changes)
                if old_type and new_type and old_type != new_type:
                    add_event({
                        "l": lcsc, "d": today,
                        "s": new_stock, "$": new_price, "t": new_type,
                        "e": "type_change",
                    })
            else:
                # New part (not in old data)
                if 0 < new_stock <= HISTORY_HIGH_STOCK_CAP:
                    add_event({
                        "l": lcsc, "d": today,
                        "s": new_stock, "$": new_price, "t": new_type,
                        "e": "new",
                    })

    # Disappeared parts (in old, not in new) — mark as gone
    for lcsc, (old_stock, old_price, old_type) in old_data.items():
        if lcsc not in seen_lcsc:
            add_event({
                "l": lcsc, "d": today,
                "s": 0, "$": old_price, "t": old_type,
                "e": "gone",
            })

    if not events:
        logger.info("No stock history events to record")
        return {"events": 0}

    # Write events via gzip multi-stream append
    daily_dir = history_dir / month
    daily_dir.mkdir(parents=True, exist_ok=True)
    history_file = daily_dir / f"{today}.jsonl.gz"
    with open(history_file, "ab") as raw_f:
        with gzip.GzipFile(fileobj=raw_f, mode="wb") as gz:
            for event in events:
                gz.write((json.dumps(event, separators=(",", ":")) + "\n").encode())

    stats["events"] = len(events)
    logger.info(f"Stock history: {len(events)} events recorded to {history_file.name}")
    for etype, count in sorted(stats.items()):
        if etype != "events":
            logger.info(f"  {etype}: {count}")

    return stats


def carry_over_gaps(
    previous_parts: Iterable[tuple[str, dict[str, Any]]],
    results: dict[str, list[dict[str, Any]]],
    previous_carried: dict[str, dict[str, Any]],
    today: str,
    category_slugs: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    """Find subcategories whose parts went missing in a scrape gap and return the previous rows.

    A bulk loss is a subcategory missing at least GAP_MIN_LOST parts and GAP_MIN_FRACTION of its
    rows, counting only parts found nowhere in today's results (moved parts aren't lost). New bulk
    losses are carried when the day has at least GAP_MIN_SUBCATEGORIES of them, or alone when one
    is GAP_SURE_LOST or more: a single smaller one is a delisting. A subcategory carried the day
    before (in `previous_carried`) continues its own gap while it is still a bulk loss, without
    counting toward today's quorum. A gap is carried on its first day and the next (GAP_MAX_DAYS);
    after that the loss is accepted. Returns the parts to carry, by category slug, and the manifest
    record by subcategory id.
    """
    today_codes = {part.get("l") for parts in results.values() for part in parts}
    sizes: dict[int, int] = {}
    lost_by_sub: dict[int, list[tuple[str, dict[str, Any]]]] = {}
    for slug, part in previous_parts:  # streamed: only missing parts are kept in memory
        sizes[part["c"]] = sizes.get(part["c"], 0) + 1
        if part["l"] not in today_codes:
            lost_by_sub.setdefault(part["c"], []).append((slug, part))
    carried: dict[str, list[dict[str, Any]]] = {}
    record: dict[str, dict[str, Any]] = {}
    bulk = {sub_id: lost for sub_id, lost in lost_by_sub.items()
            if len(lost) >= GAP_MIN_LOST and len(lost) >= GAP_MIN_FRACTION * sizes[sub_id]}
    # Only new losses make a gap day: yesterday's carried subcategories would otherwise turn one
    # unrelated delisting on the gap's second day into a gap.
    gap_day = sum(str(sub_id) not in previous_carried for sub_id in bulk) >= GAP_MIN_SUBCATEGORIES
    for sub_id, lost in sorted(bulk.items()):
        size = sizes[sub_id]
        continuing = str(sub_id) in previous_carried
        if not continuing and not gap_day and len(lost) < GAP_SURE_LOST:
            logger.info(f"  Subcategory {sub_id}: {len(lost)} of {size} parts gone (a delisting, not a gap)")
            continue
        slugs = {slug for slug, _ in lost}
        since = (previous_carried.get(str(sub_id)) or {}).get("since", today)
        if (date.fromisoformat(today) - date.fromisoformat(since)).days >= GAP_MAX_DAYS:
            logger.warning(f"  Subcategory {sub_id}: {len(lost)} of {size} parts still missing "
                           f"since {since}; no longer carried")
            continue
        if len(slugs) != 1 or not slugs <= category_slugs:
            logger.warning(f"  Subcategory {sub_id}: {len(lost)} parts missing from categories "
                           f"{sorted(slugs)} not in today's list; not carried")
            continue
        slug = slugs.pop()
        carried.setdefault(slug, []).extend(part for _, part in lost)
        record[str(sub_id)] = {"category": slug, "parts": len(lost), "of": size, "since": since}
        logger.warning(f"  Subcategory {sub_id} ({slug}): {len(lost)} of {size} parts missing "
                       f"at once; keeping the previous scrape's rows (gap since {since})")
    return carried, record


# === Main Scraper ===

def write_scrape_outputs(
    output_dir: Path,
    categories: list[dict[str, Any]],
    results: dict[str, list[dict[str, Any]]],
    progress: ScrapeProgress,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Prepare catalog, history and manifest offline in an existing staging copy."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    catalog_dir = output_dir / "catalog"
    manifest_path = output_dir / "manifest.json"
    previous = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    prices_updated_at = previous.get("prices_updated_at")
    refresh_prices = not (catalog_dir / "prices.tsv").exists() or not prices_updated_at
    if not refresh_prices:
        last_refresh = datetime.fromisoformat(prices_updated_at).astimezone(timezone.utc)
        # Calendar days, not 7 x 24 hours: the daily run starts hours earlier or later from day to
        # day (19:42 and 22:30 UTC in one week), and elapsed time would push some refreshes to day 8.
        refresh_prices = (now.date() - last_refresh.date()).days >= 7
    previous_prices = {} if refresh_prices else read_prices(catalog_dir)
    if refresh_prices:
        prices_updated_at = now.isoformat()

    carried_record: dict[str, dict[str, Any]] = {}
    if results:
        try:
            if (catalog_dir / "stock.tsv").exists():
                carried, carried_record = carry_over_gaps(
                    read_catalog(catalog_dir, prices=(catalog_dir / "prices.tsv").exists()),
                    results, previous.get("carried_forward") or {}, now.date().isoformat(),
                    {slugify(cat["name"]) for cat in categories})
                if carried:
                    results = {slug: [*results.get(slug, []), *carried.get(slug, [])]
                               for slug in {*results, *carried}}
            history_stats = generate_stock_history(catalog_dir, output_dir / "history", results, now=now)
            if history_stats.get("events", 0) > 0:
                logger.info(f"Stock history: {history_stats['events']} events recorded")
        except Exception:
            raise RuntimeError("Stock history generation failed; published data unchanged") from None

    # Keep the first occurrence globally, visiting sorted category slugs as before.
    seen_lcsc: set[str] = set()
    total_dupes = 0
    unique_results = {slugify(cat["name"]): [] for cat in categories}
    for cat_slug, parts in sorted(results.items()):
        unique_parts = []
        duplicates = 0
        for part in parts:
            lcsc = part.get("l")
            if lcsc and lcsc not in seen_lcsc:
                seen_lcsc.add(lcsc)
                unique_parts.append(part)
            else:
                duplicates += 1
        unique_results[cat_slug] = unique_parts
        total_dupes += duplicates
        if duplicates:
            logger.info(f"  {cat_slug}: {len(unique_parts)} parts ({duplicates} duplicates removed)")
        else:
            logger.info(f"  {cat_slug}: {len(unique_parts)} parts")
    if total_dupes:
        logger.info(f"Deduplicated {total_dupes} LCSCs total (within + cross-category)")

    # 340k prices change daily, but 261k move <0.05% from currency drift (~2.3 MB/day).
    # Refresh weekly to keep git deltas small; new parts and stored None get prices immediately.
    prices = {}
    for parts in unique_results.values():
        for part in parts:
            code = part["l"]
            stored = previous_prices.get(code)
            prices[code] = stored if stored is not None else part.get("$")
    progress.category_counts = write_catalog(catalog_dir, unique_results, prices)
    progress.total_parts = sum(progress.category_counts.values())

    # Generate manifest
    logger.info("")
    logger.info("Generating manifest...")
    manifest = {
        "version": "1.0",
        "scraped_at": now.isoformat(),
        "prices_updated_at": prices_updated_at,
        "stock_threshold": STOCK_THRESHOLD,
        "total_parts": progress.total_parts,
        "categories": {},
    }

    for cat in categories:
        cat_slug = slugify(cat["name"])
        count = progress.category_counts.get(cat_slug, 0)
        manifest["categories"][cat_slug] = {
            "id": cat["id"],
            "name": cat["name"],
            "count": count,
            "status": "empty" if count == 0 else "complete",
        }

    # Subcategories published with the previous scrape's rows; the next scrape reads "since" from here,
    # and validate_manifest judges today's scraped counts without them.
    if carried_record:
        manifest["carried_forward"] = carried_record

    # Mark any still-failed subcategories
    if progress.failed_subcategories:
        manifest["failed_subcategories"] = list(progress.failed_subcategories)

    with open(output_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest


async def _run_scraper_staged(
    output_dir: Path,
    num_workers: int = 4,
    resume: bool = False,
):
    """Run the full scrape."""
    start_time = time.time()
    logger.info("JLCPCB Component Scraper")
    logger.info("========================")
    logger.info(f"Workers: {num_workers}")
    logger.info(f"Stock threshold: >= {STOCK_THRESHOLD}")
    logger.info(f"Output: {output_dir}")
    logger.info("")

    # Setup output directories
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load or create progress
    progress_file = output_dir / "progress.json"
    if resume and progress_file.exists():
        with open(progress_file, encoding="utf-8") as f:
            progress = ScrapeProgress.from_dict(json.load(f))
        logger.info(f"Resuming from {len(progress.completed_subcategories)} completed subcategories")
    else:
        progress = ScrapeProgress(
            started_at=datetime.now(timezone.utc).isoformat()
        )

    # Fetch categories
    logger.info("Fetching categories...")
    async with create_scraper_session() as init_session:
        categories = await fetch_categories(init_session)
    logger.info(f"Found {len(categories)} categories")

    # Build subcategory list
    subcategories: list[Subcategory] = []
    subcategory_map: dict[str, dict] = {}

    for cat in categories:
        cat_slug = slugify(cat["name"])
        for sub in cat.get("subcategories", []):
            subcat = Subcategory(
                id=sub["id"],
                name=sub["name"],
                category_id=cat["id"],
                category_name=cat["name"],
                category_slug=cat_slug,
                count=sub.get("count", 0),
            )
            subcategories.append(subcat)
            subcategory_map[str(sub["id"])] = {
                "name": sub["name"],
                "category_id": cat["id"],
                "category_name": cat["name"],
            }

    logger.info(f"Found {len(subcategories)} subcategories")

    # Save subcategory map
    with open(output_dir / "subcategories.json", "w", encoding="utf-8") as f:
        json.dump(subcategory_map, f, indent=2)

    # Filter out already completed subcategories
    pending = [s for s in subcategories if s.id not in progress.completed_subcategories]
    pending.sort(key=lambda s: s.count, reverse=True)
    logger.info(f"Pending: {len(pending)} subcategories")
    logger.info("")

    partial_dir = output_dir / "partial"
    partial_dir.mkdir(exist_ok=True)
    results: dict[str, list[dict[str, Any]]] = {}
    if resume:
        for gz_file in partial_dir.glob("*.jsonl.gz"):
            with gzip.open(gz_file, "rt", encoding="utf-8") as stream:
                results[gz_file.name.removesuffix(".jsonl.gz")] = [json.loads(line) for line in stream if line.strip()]

    if not pending:
        logger.info("All subcategories already scraped!")
    else:
        # Create work queue
        queue: asyncio.Queue[Subcategory | None] = asyncio.Queue()
        for subcat in pending:
            await queue.put(subcat)

        # Add sentinel values to stop workers
        for _ in range(num_workers):
            await queue.put(None)

        # Results storage
        results_lock = asyncio.Lock()
        circuit_breaker = CircuitBreaker(threshold=3)

        # Start workers with staggered launch — each gets its own wafer session
        logger.info(f"Starting {num_workers} workers...")
        worker_sessions = [create_scraper_session() for _ in range(num_workers)]
        workers = []
        for i in range(num_workers):
            task = asyncio.create_task(
                worker(i, worker_sessions[i], queue, results, progress, results_lock, circuit_breaker)
            )
            workers.append(task)
            await asyncio.sleep(WORKER_STAGGER)

        # Wait for all work to complete
        await queue.join()
        await asyncio.gather(*workers)

        # Drop worker session references (no close() needed — wafer manages resources)
        worker_sessions.clear()

        save_partial_results(partial_dir, results)
        # Check if circuit breaker tripped
        if circuit_breaker.is_tripped():
            logger.error("")
            logger.error("=" * 50)
            logger.error("SCRAPE ABORTED - Circuit breaker tripped!")
            logger.error("=" * 50)
            logger.error(f"Completed: {len(progress.completed_subcategories)} subcategories")
            logger.error(f"Failed: {len(progress.failed_subcategories)} subcategories")
            logger.error(f"Parts scraped before abort: {progress.total_parts:,}")

            # Save progress for resume
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress.to_dict(), f, indent=2)
            logger.info(f"\nProgress saved to {progress_file}")
            logger.info("Run with --resume to continue from where we left off.")
            raise RuntimeError("Component scrape aborted: circuit breaker tripped; published data unchanged")

        # Save progress periodically during scrape would be nice, but for now save at end
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(progress.to_dict(), f, indent=2)

    # Retry failed subcategories
    if progress.failed_subcategories:
        logger.info("")
        logger.info(f"Retrying {len(progress.failed_subcategories)} failed subcategories...")
        failed_subcats = [s for s in subcategories if s.id in progress.failed_subcategories]
        retry_session = create_scraper_session()

        for subcat in failed_subcats:
            try:
                parts, count = await scrape_subcategory(subcat, retry_session)

                results.setdefault(subcat.category_slug, []).extend(parts)
                new_count = count

                progress.failed_subcategories.remove(subcat.id)
                progress.completed_subcategories.add(subcat.id)
                progress.total_parts += new_count
                progress.category_counts[subcat.category_slug] = (
                    progress.category_counts.get(subcat.category_slug, 0) + new_count
                )

                dup_msg = f", {count - new_count} duplicates" if new_count < count else ""
                logger.info(f"  Retry OK: {subcat.name} ({new_count} parts{dup_msg})")

            except Exception as e:
                logger.error(f"  Retry FAILED: {subcat.name} - {e}")

        del retry_session  # No close() needed — wafer manages resources

    save_partial_results(partial_dir, results)
    with open(progress_file, "w", encoding="utf-8") as stream:
        json.dump(progress.to_dict(), stream, indent=2)
    if progress.failed_subcategories or {sub.id for sub in subcategories} - progress.completed_subcategories:
        raise RuntimeError("Component scrape incomplete; published data unchanged (resume with --resume)")

    manifest = write_scrape_outputs(output_dir, categories, results, progress)

    # Progress is retained until the outer validation/publication succeeds.

    # Summary
    elapsed = time.time() - start_time
    logger.info("")
    logger.info("=" * 50)
    logger.info("SCRAPE COMPLETE")
    logger.info("=" * 50)
    logger.info(f"Total parts: {progress.total_parts:,}")
    logger.info(f"Categories: {len(manifest['categories'])}")
    logger.info(f"Failed subcategories: {len(progress.failed_subcategories)}")
    logger.info(f"Time: {elapsed/60:.1f} minutes")
    logger.info(f"Output: {output_dir}")


def save_partial_results(directory: Path, results: dict[str, list[dict[str, Any]]]) -> None:
    for slug, parts in results.items():
        target = directory / f"{slug}.jsonl.gz"
        temporary = target.with_suffix(".tmp")
        with gzip.open(temporary, "wt", encoding="utf-8", compresslevel=GZIP_LEVEL) as stream:
            for part in parts:
                stream.write(json.dumps(part, separators=(",", ":")) + "\n")
        temporary.replace(target)


def publish_staged_files(output_dir: Path, staging: Path, files: list[Path]) -> None:
    """Atomic file replacements with rollback on publication I/O failure."""
    backup = staging / "publication-backup"
    backup.mkdir(exist_ok=True)
    published = []
    expected = {source.relative_to(staging) for source in files}
    stale = [p for p in (output_dir / "catalog").rglob("*")
             if p.is_file() and p.relative_to(output_dir) not in expected]
    try:
        for source in [*files, *stale]:
            relative = source.relative_to(output_dir) if source in stale else source.relative_to(staging)
            destination = output_dir / relative
            saved = backup / relative
            existed = destination.exists()
            if existed:
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, saved)
            if source in stale:
                destination.unlink()
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                source.replace(destination)
            published.append((destination, saved, existed, None if source in stale else source))
        parts_dir = output_dir / "catalog" / "parts"
        for directory in sorted((p for p in parts_dir.rglob("*") if p.is_dir()), reverse=True):
            if not any(directory.iterdir()):
                directory.rmdir()
    except OSError:
        for destination, saved, existed, source in reversed(published):
            if source is not None:
                shutil.copy2(destination, source)
            if existed:
                destination.parent.mkdir(parents=True, exist_ok=True)
                saved.replace(destination)
            else:
                destination.unlink(missing_ok=True)
        raise


async def run_scraper(output_dir: Path, num_workers: int = 4, resume: bool = False):
    """Build/retry privately, validate against the published baseline, then publish."""
    from check_component_scrape import validate_manifest
    output_dir.mkdir(parents=True, exist_ok=True)
    staging = output_dir / ".scrape-staging"
    if not resume and staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(exist_ok=True)
    # Outputs are always rebuilt from the published files, which stay untouched until publication;
    # a resume reuses only the scraped results (progress.json, partial/). Reused staging outputs
    # could be half-written (catalog files that disagree) or already hold today's history events.
    for name in ("catalog", "history"):
        if (staging / name).exists():
            shutil.rmtree(staging / name)
        if (output_dir / name).exists():
            shutil.copytree(output_dir / name, staging / name)
    (staging / "manifest.json").unlink(missing_ok=True)
    if (output_dir / "manifest.json").exists():
        shutil.copy2(output_dir / "manifest.json", staging / "manifest.json")
    await _run_scraper_staged(staging, num_workers, resume)
    current = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))
    previous_path = output_dir / "manifest.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else {}
    failures = validate_manifest(previous, current, allow_count_drop=os.environ.get("ALLOW_PART_DROP", "").lower() == "true")
    if failures:
        raise RuntimeError("Component scrape rejected; published data unchanged: " + "; ".join(failures))
    # Every byte is prepared and validated before the first published file is replaced.
    files = [*sorted(p for p in (staging / "catalog").rglob("*") if p.is_file()),
             *sorted((staging / "history").rglob("*.jsonl.gz")),
             staging / "subcategories.json", staging / "manifest.json"]
    publish_staged_files(output_dir, staging, files)
    shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description="Scrape JLCPCB components")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("data"),
        help="Output directory (default: data/)",
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="Number of concurrent workers (default: 4)",
    )
    parser.add_argument(
        "--resume", "-r",
        action="store_true",
        help="Resume from previous progress",
    )
    args = parser.parse_args()

    asyncio.run(run_scraper(args.output, args.workers, args.resume))


if __name__ == "__main__":
    main()
