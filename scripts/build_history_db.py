#!/usr/bin/env python3
"""
Build SQLite database from stock history JSONL files.

Reads gzipped JSONL files from data/history/ and creates a queryable
SQLite database of stock change events.

Usage:
    python scripts/build_history_db.py [--data-dir PATH] [--output PATH]
"""

import argparse
import gzip
import json
import os
import sqlite3
import time
from pathlib import Path

VALID_EVENT_TYPES = {"change", "new", "gone", "reappear", "type_change"}
VALID_LIBRARY_TYPES = {None, "b", "p", "e"}


def build_history_db(data_dir: Path, db_path: Path, verbose: bool = True) -> dict:
    """
    Build stock history SQLite database from compressed JSONL event files.

    Builds to a temp file and atomically renames on success.
    Returns stats dict with counts and timing.
    """
    start_time = time.time()

    if verbose:
        print(f"Building stock history database from {data_dir}")
        print(f"Output: {db_path}")

    # Build to temp path, rename on success (atomic replacement)
    tmp_path = db_path.with_suffix(".db.tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(tmp_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    conn.execute("""
        CREATE TABLE stock_events (
            lcsc TEXT NOT NULL,
            date TEXT NOT NULL,
            stock INTEGER,
            price REAL,
            library_type TEXT,
            event_type TEXT DEFAULT 'change',
            PRIMARY KEY (lcsc, date, event_type)
        )
    """)

    # Load all history files
    history_dir = data_dir / "history"
    total_events = 0
    file_count = 0

    if history_dir.exists():
        for gz_file in sorted(history_dir.glob("*.jsonl.gz")):
            count = 0
            skipped = 0
            batch = []
            had_error = False

            # Wrap entire file in a single transaction for performance
            conn.execute("BEGIN")
            try:
                with gzip.open(gz_file, "rt") as f:
                    for line in f:
                        if not line or line == "\n":
                            continue
                        try:
                            event = json.loads(line)

                            # Validate required fields and types
                            lcsc = event.get("l")
                            date = event.get("d")
                            if not lcsc or not isinstance(lcsc, str):
                                skipped += 1
                                continue
                            if not date or not isinstance(date, str) or len(date) != 10:
                                skipped += 1
                                continue

                            stock = event.get("s")
                            if stock is not None and (not isinstance(stock, int) or stock < 0):
                                skipped += 1
                                continue

                            lib_type = event.get("t")
                            if lib_type not in VALID_LIBRARY_TYPES:
                                skipped += 1
                                continue

                            event_type = event.get("e", "change")
                            if event_type not in VALID_EVENT_TYPES:
                                skipped += 1
                                continue

                            batch.append((
                                lcsc,
                                date,
                                stock,
                                event.get("$"),
                                lib_type,
                                event_type,
                            ))
                            count += 1
                        except (json.JSONDecodeError, KeyError) as e:
                            skipped += 1
                            if verbose and skipped <= 3:
                                print(f"  WARNING: skipping malformed line in {gz_file.name}: {e}")

                        if len(batch) >= 1000:
                            conn.executemany(
                                "INSERT OR REPLACE INTO stock_events VALUES (?, ?, ?, ?, ?, ?)",
                                batch,
                            )
                            batch = []
            except (EOFError, OSError) as e:
                had_error = True
                if verbose:
                    print(f"  WARNING: truncated gzip stream in {gz_file.name}: {e}")

            # Flush partial batch (including data recovered before truncation)
            if batch:
                conn.executemany(
                    "INSERT OR REPLACE INTO stock_events VALUES (?, ?, ?, ?, ?, ?)",
                    batch,
                )

            conn.commit()

            total_events += count
            file_count += 1
            if verbose:
                if count > 0 or had_error:
                    msg = f"  {gz_file.name}: {count:,} events"
                    if skipped:
                        msg += f" ({skipped} skipped)"
                    if had_error:
                        msg += " (truncated)"
                    print(msg)

    # Create indexes (must exist before MIN(date) query for index-only scan)
    conn.execute("CREATE INDEX idx_events_lcsc ON stock_events(lcsc)")
    conn.execute("CREATE INDEX idx_events_date ON stock_events(date)")

    # Tracking metadata (for Phase 2 analytics messaging)
    conn.execute("""
        CREATE TABLE tracking_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Derive tracking_started from earliest event date
    cursor = conn.execute("SELECT MIN(date) FROM stock_events")
    earliest = cursor.fetchone()[0]
    if earliest:
        conn.execute(
            "INSERT INTO tracking_meta VALUES ('tracking_started', ?)",
            (earliest,),
        )
        if verbose:
            print(f"  Tracking started: {earliest}")

    conn.commit()
    conn.execute("ANALYZE")
    conn.commit()

    # Get final stats
    cursor = conn.execute("SELECT COUNT(*) FROM stock_events")
    final_count = cursor.fetchone()[0]

    cursor = conn.execute(
        "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()"
    )
    db_size = cursor.fetchone()[0]

    conn.close()

    # Atomic rename: only replace old DB after successful build
    if db_path.exists():
        db_path.unlink()
    os.rename(tmp_path, db_path)

    elapsed = time.time() - start_time

    stats = {
        "total_events": final_count,
        "files": file_count,
        "db_size_bytes": db_size,
        "db_size_mb": round(db_size / (1024 * 1024), 2),
        "build_time_seconds": round(elapsed, 2),
    }

    if verbose:
        print()
        print("=" * 50)
        print("STOCK HISTORY DB BUILD COMPLETE")
        print("=" * 50)
        print(f"Events: {final_count:,}")
        print(f"Files processed: {file_count}")
        print(f"Database size: {stats['db_size_mb']} MB")
        print(f"Build time: {elapsed:.1f} seconds")
        print(f"Output: {db_path}")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Build stock history database")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Data directory with history files (default: data/)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("data/stock_history.db"),
        help="Output database path (default: data/stock_history.db)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output",
    )
    args = parser.parse_args()

    if not args.data_dir.exists():
        print(f"Error: Data directory not found: {args.data_dir}")
        return 1

    build_history_db(args.data_dir, args.output, verbose=not args.quiet)
    return 0


if __name__ == "__main__":
    exit(main())
