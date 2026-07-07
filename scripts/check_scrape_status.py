#!/usr/bin/env python3
"""Verify the last sensor scrape produced fresh, sane data for every source.

Reads data/sensors/_scrape_status.json (written by scrape_sensors.py) and each
source's JSON, and exits 1 if any registered scraper failed, left stale data in
place, produced zero sensors, or logged too many errors. Used in CI to gate the
deploy — fresh data from good sources is still committed either way.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow importing scrapers package from this script's directory
sys.path.insert(0, str(Path(__file__).parent))

from scrapers import SCRAPERS

MAX_SOURCE_ERRORS = 5


def _parse_iso(value) -> datetime | None:
    """Parse an ISO timestamp, treating naive values as UTC. None if invalid."""
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def check_status(status: dict, sensors_dir: Path, keys=None) -> list[str]:
    """Return one failure message per problem source. Empty list = all good.

    Checks, for each scraper key:
    - a status entry exists and reports ok
    - {key}.json exists, parses, and its scraped_at is not older than run_at
      (stale = the scraper silently left last run's data in place)
    - stats.sensor_count > 0 and stats.errors <= MAX_SOURCE_ERRORS
    """
    failures: list[str] = []
    sources = status.get("sources", {})
    run_at = _parse_iso(status.get("run_at"))
    if run_at is None:
        failures.append(f"status file has no valid run_at: {status.get('run_at')!r}")

    for key in (keys if keys is not None else SCRAPERS):
        entry = sources.get(key)
        if entry is None:
            failures.append(f"{key}: no status entry (scraper did not run)")
            continue
        if not entry.get("ok"):
            failures.append(f"{key}: scrape failed: {entry.get('error') or 'unknown error'}")
            continue

        source_file = sensors_dir / f"{key}.json"
        if not source_file.exists():
            failures.append(f"{key}: {source_file.name} is missing")
            continue
        try:
            data = json.loads(source_file.read_text())
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
            failures.append(f"{key}: cannot read {source_file.name}: {e}")
            continue

        scraped_at = _parse_iso(data.get("scraped_at"))
        if scraped_at is None:
            failures.append(f"{key}: {source_file.name} has no valid scraped_at")
        elif run_at is not None and scraped_at < run_at:
            failures.append(
                f"{key}: stale data — scraped_at {data.get('scraped_at')} "
                f"predates run_at {status.get('run_at')}"
            )

        stats = data.get("stats", {})
        if stats.get("sensor_count", 0) == 0:
            failures.append(f"{key}: sensor_count is 0")
        errors = stats.get("errors", 0)
        if errors > MAX_SOURCE_ERRORS:
            failures.append(f"{key}: {errors} scrape errors (max {MAX_SOURCE_ERRORS})")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the last sensor scrape run succeeded for all sources"
    )
    parser.add_argument("--sensors-dir", type=Path, default=Path("data/sensors"))
    args = parser.parse_args()

    status_path = args.sensors_dir / "_scrape_status.json"
    if not status_path.exists():
        print(f"FAIL: {status_path} not found — did scrape_sensors.py run?")
        return 1
    try:
        status = json.loads(status_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: cannot read {status_path}: {e}")
        return 1

    failures = check_status(status, args.sensors_dir)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"OK: all {len(SCRAPERS)} sensor sources scraped fresh data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
