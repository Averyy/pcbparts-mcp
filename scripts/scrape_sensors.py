#!/usr/bin/env python3
"""Scrape sensor data from multiple sources."""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow importing scrapers package from this script's directory
sys.path.insert(0, str(Path(__file__).parent))

from scrapers import SCRAPERS

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Scrape sensor data from multiple sources")
    parser.add_argument("--output", "-o", type=Path, default=Path("data/sensors"))
    parser.add_argument("--quiet", "-q", action="store_true")
    parser.add_argument(
        "--source", "-s",
        choices=list(SCRAPERS.keys()),
        help="Run only a specific source scraper",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    args.output.mkdir(parents=True, exist_ok=True)

    run_at = datetime.now(timezone.utc).isoformat()
    statuses: dict[str, dict] = {}

    for key, (name, fn) in SCRAPERS.items():
        if args.source and args.source != key:
            continue
        output_file = args.output / f"{key}.json"
        mtime_before = output_file.stat().st_mtime_ns if output_file.exists() else None
        try:
            logger.info(f"Scraping {name}...")
            fn(args.output)
        except Exception as e:
            logger.error(f"FAILED {name}: {e}")
            statuses[key] = {"ok": False, "error": str(e)}
            continue
        # A scraper can return without writing its output file (e.g. an empty
        # sitemap or an API call that quietly yields nothing) — the previous
        # run's JSON would then be silently reused. Treat that as failure.
        if not output_file.exists():
            logger.error(f"FAILED {name}: returned without writing {output_file}")
            statuses[key] = {"ok": False, "error": "scraper returned without writing output file"}
        elif output_file.stat().st_mtime_ns == mtime_before:
            logger.error(f"FAILED {name}: did not update {output_file} (stale data left in place)")
            statuses[key] = {"ok": False, "error": "scraper returned without updating output file"}
        else:
            statuses[key] = {"ok": True, "error": None}

    status_path = args.output / "_scrape_status.json"
    status_path.write_text(
        json.dumps({"run_at": run_at, "sources": statuses}, indent=2) + "\n"
    )
    logger.info(f"Wrote scrape status to {status_path}")


if __name__ == "__main__":
    main()
