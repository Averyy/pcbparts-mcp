#!/usr/bin/env python3
"""
Build SQLite database from scraped JLCPCB component data.

Reads gzipped JSONL files from data/categories/ and creates a searchable
SQLite database with FTS5 full-text search.

Usage:
    python scripts/build_database.py [--data-dir PATH] [--output PATH]

The database is built on deploy/startup and used for parametric searches.
"""

import argparse
import gzip
import json
import sqlite3
import time
from pathlib import Path


def build_database(data_dir: Path, db_path: Path, verbose: bool = True) -> dict:
    """
    Build SQLite database from compressed JSON files.

    Returns stats dict with counts and timing.
    """
    start_time = time.time()

    if verbose:
        print(f"Building database from {data_dir}")
        print(f"Output: {db_path}")

    # Remove existing database
    if db_path.exists():
        db_path.unlink()

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # Create main components table
    conn.execute("""
        CREATE TABLE components (
            lcsc TEXT PRIMARY KEY,
            mpn TEXT,
            manufacturer TEXT,
            package TEXT,
            stock INTEGER,
            library_type TEXT CHECK(library_type IN ('b', 'p', 'e')),
            subcategory_id INTEGER,
            price REAL,
            description TEXT,
            attributes TEXT
        )
    """)

    # Create subcategories table
    conn.execute("""
        CREATE TABLE subcategories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            category_name TEXT NOT NULL
        )
    """)

    # Create categories table (derived from subcategories)
    conn.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT NOT NULL
        )
    """)

    # Load subcategories
    subcategories_file = data_dir / "subcategories.json"
    if subcategories_file.exists():
        with open(subcategories_file) as f:
            subcats = json.load(f)

        # Track unique categories
        categories_seen = {}

        for subcat_id, info in subcats.items():
            conn.execute(
                "INSERT INTO subcategories VALUES (?, ?, ?, ?)",
                (int(subcat_id), info["name"], info["category_id"], info["category_name"])
            )

            # Track category
            cat_id = info["category_id"]
            if cat_id not in categories_seen:
                categories_seen[cat_id] = info["category_name"]

        if verbose:
            print(f"Loaded {len(subcats)} subcategories")

    # Load manifest for category slugs
    manifest_file = data_dir / "manifest.json"
    if manifest_file.exists():
        with open(manifest_file) as f:
            manifest = json.load(f)

        for slug, cat_info in manifest.get("categories", {}).items():
            conn.execute(
                "INSERT OR REPLACE INTO categories VALUES (?, ?, ?)",
                (cat_info["id"], cat_info["name"], slug)
            )

    # Load all category files
    categories_dir = data_dir / "categories"
    total_parts = 0
    category_counts = {}
    BATCH_SIZE = 1000  # Insert in batches for better performance

    for gz_file in sorted(categories_dir.glob("*.jsonl.gz")):
        cat_slug = gz_file.stem.replace(".jsonl", "")
        count = 0
        batch = []

        with gzip.open(gz_file, "rt") as f:
            for line in f:
                if not line.strip():
                    continue

                part = json.loads(line)
                batch.append((
                    part["l"],
                    part.get("m"),
                    part.get("f"),
                    part.get("p"),
                    part.get("s"),
                    part.get("t"),
                    part.get("c"),
                    part.get("$"),
                    part.get("d"),
                    json.dumps(part.get("a", [])),
                ))
                count += 1

                # Insert batch when full
                if len(batch) >= BATCH_SIZE:
                    conn.executemany(
                        """INSERT INTO components
                           (lcsc, mpn, manufacturer, package, stock, library_type,
                            subcategory_id, price, description, attributes)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        batch
                    )
                    batch = []

        # Insert remaining parts
        if batch:
            conn.executemany(
                """INSERT INTO components
                   (lcsc, mpn, manufacturer, package, stock, library_type,
                    subcategory_id, price, description, attributes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                batch
            )

        category_counts[cat_slug] = count
        total_parts += count

        if verbose and count > 0:
            print(f"  {cat_slug}: {count:,} parts")

    if verbose:
        print(f"Total parts loaded: {total_parts:,}")
        print("Creating indexes...")

    # Create indexes for common queries
    conn.execute("CREATE INDEX idx_subcategory ON components(subcategory_id)")
    conn.execute("CREATE INDEX idx_stock ON components(stock)")
    conn.execute("CREATE INDEX idx_library_type ON components(library_type)")
    conn.execute("CREATE INDEX idx_package ON components(package)")
    conn.execute("CREATE INDEX idx_manufacturer ON components(manufacturer)")
    conn.execute("CREATE INDEX idx_price ON components(price)")

    # Composite indexes for common filter combinations
    conn.execute("CREATE INDEX idx_subcat_stock ON components(subcategory_id, stock)")
    conn.execute("CREATE INDEX idx_subcat_libtype ON components(subcategory_id, library_type)")

    if verbose:
        print("Creating FTS5 full-text search index...")

    # Create FTS5 index for text search
    # Store content directly for reliable searching
    conn.execute("""
        CREATE VIRTUAL TABLE components_fts USING fts5(
            lcsc,
            mpn,
            manufacturer,
            description
        )
    """)

    # Populate FTS index directly from components table
    conn.execute("""
        INSERT INTO components_fts(lcsc, mpn, manufacturer, description)
        SELECT lcsc, mpn, manufacturer, description FROM components
    """)

    if verbose:
        print("Optimizing database...")

    # Commit all changes first
    conn.commit()

    # Analyze for query optimization
    conn.execute("ANALYZE")

    # Vacuum to reclaim space and optimize (must be outside transaction)
    conn.execute("VACUUM")

    # Get final stats
    cursor = conn.execute("SELECT COUNT(*) FROM components")
    final_count = cursor.fetchone()[0]

    cursor = conn.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0]

    conn.close()

    elapsed = time.time() - start_time

    stats = {
        "total_parts": final_count,
        "categories": len(category_counts),
        "category_counts": category_counts,
        "db_size_bytes": db_size,
        "db_size_mb": round(db_size / (1024 * 1024), 2),
        "build_time_seconds": round(elapsed, 2),
    }

    if verbose:
        print()
        print("=" * 50)
        print("DATABASE BUILD COMPLETE")
        print("=" * 50)
        print(f"Parts: {final_count:,}")
        print(f"Categories: {len(category_counts)}")
        print(f"Database size: {stats['db_size_mb']} MB")
        print(f"Build time: {elapsed:.1f} seconds")
        print(f"Output: {db_path}")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Build component database")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Data directory with scraped files (default: data/)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("data/components.db"),
        help="Output database path (default: data/components.db)",
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

    categories_dir = args.data_dir / "categories"
    if not categories_dir.exists():
        print(f"Error: Categories directory not found: {categories_dir}")
        return 1

    build_database(args.data_dir, args.output, verbose=not args.quiet)
    return 0


if __name__ == "__main__":
    exit(main())
