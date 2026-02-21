#!/usr/bin/env python3
"""
Scrape all JLCPCB components for local database.

Uses 4 concurrent workers with browser impersonation to avoid rate limiting.
Outputs gzipped JSONL files per category.

Usage:
    python scripts/scrape_components.py [--resume] [--workers N]
"""

import argparse
import asyncio
import gzip
import json
import logging
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from curl_cffi import requests as curl_requests

# Add parent directory to path for imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pcbparts_mcp.config import DEFAULT_MIN_STOCK

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
REQUEST_TIMEOUT = 15.0
MAX_RETRIES = 3
JITTER_RANGE = (0.2, 0.4)
WORKER_STAGGER = 0.1
GZIP_LEVEL = 9

# Browser fingerprints for TLS impersonation
BROWSER_FINGERPRINTS = ["chrome131", "chrome133a", "chrome136", "chrome142"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
]

SEC_CH_UA = [
    '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    '"Google Chrome";v="133", "Chromium";v="133", "Not_A Brand";v="24"',
]

REFERERS = [
    "https://jlcpcb.com/parts",
    "https://jlcpcb.com/parts/basic_parts",
    "https://jlcpcb.com/parts/componentSearch",
]


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


def get_headers() -> dict[str, str]:
    """Generate randomized headers that look like a real browser."""
    ua = random.choice(USER_AGENTS)
    is_firefox = "Firefox" in ua

    headers = {
        "Host": "jlcpcb.com",
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Origin": "https://jlcpcb.com",
        "Referer": random.choice(REFERERS),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    if not is_firefox:
        headers["Sec-Ch-Ua"] = random.choice(SEC_CH_UA)
        headers["Sec-Ch-Ua-Mobile"] = "?0"
        platform = '"Windows"' if "Windows" in ua else '"macOS"' if "Mac" in ua else '"Linux"'
        headers["Sec-Ch-Ua-Platform"] = platform
        headers["Priority"] = "u=1, i"

    return headers


def transform_part(item: dict[str, Any], subcategory_id: int) -> dict[str, Any]:
    """Transform API response to our compact schema."""
    # Get price from first tier
    prices = item.get("componentPrices", [])
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

    return {
        "l": item.get("componentCode"),  # lcsc
        "m": item.get("componentModelEn"),  # mpn
        "f": item.get("componentBrandEn"),  # manufacturer
        "p": item.get("componentSpecificationEn"),  # package
        "s": item.get("stockCount"),  # stock
        "t": t,  # type (b/p/e)
        "c": subcategory_id,  # subcategory_id (passed from scrape context)
        "$": round(price, 4) if price else None,  # price
        "d": item.get("describe"),  # description
        "a": attributes,  # attributes
    }


# === API Functions ===

async def make_request(
    params: dict[str, Any],
    fingerprint: str,
) -> dict[str, Any]:
    """Make a single request with retry logic."""
    last_error = None

    for attempt in range(MAX_RETRIES):
        session = curl_requests.AsyncSession(
            impersonate=fingerprint,
            timeout=REQUEST_TIMEOUT,
        )
        try:
            headers = get_headers()
            response = await session.post(
                JLCPCB_SEARCH_URL,
                json=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                raise ValueError(f"API error: {data.get('message', 'Unknown')}")

            # Jitter between requests
            await asyncio.sleep(random.uniform(*JITTER_RANGE))
            return data

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                wait = 1.0 * (2 ** attempt)
                await asyncio.sleep(wait)
        finally:
            await session.close()

    raise last_error  # type: ignore


async def fetch_categories(fingerprint: str) -> list[dict[str, Any]]:
    """Fetch all categories and subcategories from API."""
    params = {
        "currentPage": 1,
        "pageSize": 1,
        "searchSource": "search",
        "searchType": 3,
    }

    data = await make_request(params, fingerprint)
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
    fingerprint: str,
) -> tuple[list[dict[str, Any]], int]:
    """Scrape all parts from a subcategory. Returns (parts, total_count)."""
    parts = []
    page = 1

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

        data = await make_request(params, fingerprint)
        page_info = data.get("data", {}).get("componentPageInfo", {})
        items = page_info.get("list", [])
        total = page_info.get("total", 0)

        if not items:
            break

        for item in items:
            parts.append(transform_part(item, subcat.id))

        # Check if more pages
        if page * PAGE_SIZE >= total:
            break

        page += 1

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
    fingerprint: str,
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
            parts, count = await scrape_subcategory(subcat, fingerprint)
            elapsed = time.time() - t0

            async with results_lock:
                # Add parts to category bucket
                if subcat.category_slug not in results:
                    results[subcat.category_slug] = []
                results[subcat.category_slug].extend(parts)

                # Update progress
                progress.completed_subcategories.add(subcat.id)
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


# === Main Scraper ===

async def run_scraper(
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
    categories_dir = output_dir / "categories"
    categories_dir.mkdir(parents=True, exist_ok=True)

    # Load or create progress
    progress_file = output_dir / "progress.json"
    if resume and progress_file.exists():
        with open(progress_file) as f:
            progress = ScrapeProgress.from_dict(json.load(f))
        logger.info(f"Resuming from {len(progress.completed_subcategories)} completed subcategories")
    else:
        progress = ScrapeProgress(
            started_at=datetime.now(timezone.utc).isoformat()
        )

    # Fetch categories
    logger.info("Fetching categories...")
    fingerprint = BROWSER_FINGERPRINTS[0]
    categories = await fetch_categories(fingerprint)
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
    with open(output_dir / "subcategories.json", "w") as f:
        json.dump(subcategory_map, f, indent=2)

    # Filter out already completed subcategories
    pending = [s for s in subcategories if s.id not in progress.completed_subcategories]
    pending.sort(key=lambda s: s.count, reverse=True)
    logger.info(f"Pending: {len(pending)} subcategories")
    logger.info("")

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
        results: dict[str, list[dict[str, Any]]] = {}
        results_lock = asyncio.Lock()
        circuit_breaker = CircuitBreaker(threshold=3)

        # If resuming, load existing partial results
        if resume:
            for gz_file in categories_dir.glob("*.jsonl.gz"):
                cat_slug = gz_file.stem.replace(".jsonl", "")
                results[cat_slug] = []
                with gzip.open(gz_file, "rt") as f:
                    for line in f:
                        results[cat_slug].append(json.loads(line))

        # Start workers with staggered launch and different fingerprints
        logger.info(f"Starting {num_workers} workers...")
        workers = []
        for i in range(num_workers):
            fp = BROWSER_FINGERPRINTS[i % len(BROWSER_FINGERPRINTS)]
            task = asyncio.create_task(
                worker(i, fp, queue, results, progress, results_lock, circuit_breaker)
            )
            workers.append(task)
            await asyncio.sleep(WORKER_STAGGER)

        # Wait for all work to complete
        await queue.join()
        await asyncio.gather(*workers)

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
            with open(progress_file, "w") as f:
                json.dump(progress.to_dict(), f, indent=2)
            logger.info(f"\nProgress saved to {progress_file}")
            logger.info("Run with --resume to continue from where we left off.")
            return

        # Save progress periodically during scrape would be nice, but for now save at end
        with open(progress_file, "w") as f:
            json.dump(progress.to_dict(), f, indent=2)

        # Write category files (deduplicated by LCSC)
        logger.info("")
        logger.info("Writing category files...")
        for cat_slug, parts in results.items():
            # Deduplicate by LCSC part number
            seen_lcsc: set[str] = set()
            unique_parts = []
            duplicates = 0
            for part in parts:
                lcsc = part.get("l")
                if lcsc and lcsc not in seen_lcsc:
                    seen_lcsc.add(lcsc)
                    unique_parts.append(part)
                else:
                    duplicates += 1

            output_file = categories_dir / f"{cat_slug}.jsonl.gz"
            with gzip.open(output_file, "wt", compresslevel=GZIP_LEVEL) as f:
                for part in unique_parts:
                    f.write(json.dumps(part, separators=(",", ":")) + "\n")

            if duplicates > 0:
                logger.info(f"  {cat_slug}: {len(unique_parts)} parts ({duplicates} duplicates removed)")
            else:
                logger.info(f"  {cat_slug}: {len(unique_parts)} parts")

        # Create empty files for categories with no parts
        all_cat_slugs = {slugify(cat["name"]) for cat in categories}
        for cat_slug in all_cat_slugs:
            output_file = categories_dir / f"{cat_slug}.jsonl.gz"
            if not output_file.exists():
                with gzip.open(output_file, "wt", compresslevel=GZIP_LEVEL) as f:
                    pass  # Empty file
                logger.info(f"  {cat_slug}: 0 parts (empty)")

    # Retry failed subcategories
    if progress.failed_subcategories:
        logger.info("")
        logger.info(f"Retrying {len(progress.failed_subcategories)} failed subcategories...")
        failed_subcats = [s for s in subcategories if s.id in progress.failed_subcategories]

        for subcat in failed_subcats:
            try:
                parts, count = await scrape_subcategory(subcat, BROWSER_FINGERPRINTS[0])

                # Append to category file
                output_file = categories_dir / f"{subcat.category_slug}.jsonl.gz"

                # Read existing and collect LCSC codes
                existing = []
                seen_lcsc: set[str] = set()
                if output_file.exists():
                    with gzip.open(output_file, "rt") as f:
                        for line in f:
                            part = json.loads(line)
                            existing.append(part)
                            if part.get("l"):
                                seen_lcsc.add(part["l"])

                # Add new parts (deduplicated)
                new_count = 0
                for part in parts:
                    lcsc = part.get("l")
                    if lcsc and lcsc not in seen_lcsc:
                        seen_lcsc.add(lcsc)
                        existing.append(part)
                        new_count += 1

                # Write back
                with gzip.open(output_file, "wt", compresslevel=GZIP_LEVEL) as f:
                    for part in existing:
                        f.write(json.dumps(part, separators=(",", ":")) + "\n")

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

    # Generate manifest
    logger.info("")
    logger.info("Generating manifest...")
    manifest = {
        "version": "1.0",
        "scraped_at": datetime.now(timezone.utc).isoformat(),
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

    # Mark any still-failed subcategories
    if progress.failed_subcategories:
        manifest["failed_subcategories"] = list(progress.failed_subcategories)

    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Cleanup progress file on successful completion
    if not progress.failed_subcategories and progress_file.exists():
        progress_file.unlink()

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
