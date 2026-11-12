#!/usr/bin/env python3
"""Verify the last sensor scrape produced fresh, sane data for every source.

Reads data/sensors/_scrape_status.json (written by scrape_sensors.py) and each
source's JSON, and exits 1 if any registered scraper failed, left stale data in
place, produced zero sensors, or logged too many errors. Used in CI to gate the
deploy. A temporary catalog build also gates publication so incompatible
scrapes cannot commit data that breaks the Docker build.
"""

import argparse
import json
import sys
import shutil
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

# Allow importing scrapers package from this script's directory
sys.path.insert(0, str(Path(__file__).parent))

from scrapers import SCRAPERS
from build_sensor_db import build

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
            data = json.loads(source_file.read_text(encoding="utf-8"))
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


def check_catalog_build(sensors_dir: Path, allow_stale: bool = False) -> list[str]:
    """Validate curated compatibility without replacing the deployed database.

    A curated ID with no record (a reviewed part that left every source) fails the check
    unless `allow_stale`. The pre-commit gate allows it, so the month's data still lands;
    the status check after the commit doesn't, so the deploy waits for curated.json.
    """
    try:
        with tempfile.TemporaryDirectory(prefix="sensor-catalog-") as directory:
            # build() reads <data_dir>/sensors; stage the given directory there so a custom
            # --sensors-dir is the one validated, whatever its name.
            data_dir = Path(directory) / "data"
            shutil.copytree(sensors_dir, data_dir / "sensors")
            output = Path(directory) / "sensor.db"
            build(data_dir, output, verbose=False)
            # closing(): sqlite3's own context manager doesn't close, and Windows can't delete
            # the temporary directory while the database is open.
            with closing(sqlite3.connect(output)) as conn:
                ids = {row[0] for row in conn.execute("SELECT id FROM sensors")}
    except Exception as error:
        return [f"catalog build failed: {error}"]
    curated_path = sensors_dir / "curated.json"
    curated = json.loads(curated_path.read_text(encoding="utf-8")) if curated_path.exists() else {}
    stale = sorted(sid for sid, fields in curated.items()
                   if sid not in ids and not (fields.get("exclude") or {}).get("value"))
    if not stale:
        return []
    message = f"curated sensor IDs with no catalog record: {', '.join(stale)}"
    if allow_stale:
        print(f"WARN: {message} (fix data/sensors/curated.json before deploying)")
        return []
    return [message]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the last sensor scrape run succeeded for all sources"
    )
    parser.add_argument("--sensors-dir", type=Path, default=Path("data/sensors"))
    parser.add_argument("--build-only", action="store_true",
                        help="Gate publication on a temporary catalog build; check freshness separately")
    args = parser.parse_args()

    if args.build_only:
        failures = check_catalog_build(args.sensors_dir, allow_stale=True)
        for failure in failures:
            print(f"FAIL: {failure}")
        if not failures:
            print("OK: sensor catalog builds successfully")
        return int(bool(failures))

    status_path = args.sensors_dir / "_scrape_status.json"
    if not status_path.exists():
        print(f"FAIL: {status_path} not found — did scrape_sensors.py run?")
        return 1
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: cannot read {status_path}: {e}")
        return 1

    failures = check_status(status, args.sensors_dir)
    failures.extend(check_catalog_build(args.sensors_dir))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"OK: all {len(SCRAPERS)} sensor sources scraped fresh data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
