#!/usr/bin/env python3
"""Scrape sensor data from multiple sources."""

import argparse
import logging
import sys
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

    for key, (name, fn) in SCRAPERS.items():
        if args.source and args.source != key:
            continue
        try:
            logger.info(f"Scraping {name}...")
            fn(args.output)
        except Exception as e:
            logger.error(f"FAILED {name}: {e}")
            continue


if __name__ == "__main__":
    main()
