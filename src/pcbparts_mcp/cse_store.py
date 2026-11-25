"""ComponentSearchEngine answers kept across restarts (CSE_STORE_PATH, on the pcbparts-cache
Docker volume next to the EasyEDA store).

An uncached CSE search takes 11-15 s; the in-memory caches in cse.py are emptied by every restart,
including each daily data deploy. The store sits behind them:
- Searches: one query's results. Kept CSE_FOUND_TTL (a year) when every part has a model; a part
  without one gets one when someone asks CSE to build it, so a search with such a part, or with no
  parts, is kept CSE_NOT_FOUND_TTL (a week).
- KiCad files: one part's symbol and footprint, kept for good. SamacSys limits an account's model
  downloads a day, so a file is never downloaded twice; a model SamacSys revises later doesn't
  come through (delete its row to fetch it again).

Rows keep when they were fetched; a search's lifetime is applied when it's read, so changing a TTL
applies to rows already stored.
"""

import json
import logging
import sqlite3
import threading
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any

from .config import CSE_FOUND_TTL, CSE_NOT_FOUND_TTL

logger = logging.getLogger(__name__)

_SCHEMA = (
    """CREATE TABLE IF NOT EXISTS searches (
        query TEXT NOT NULL,
        page_offset INTEGER NOT NULL,
        result TEXT NOT NULL,
        all_have_models INTEGER NOT NULL,
        fetched_at REAL NOT NULL,
        PRIMARY KEY (query, page_offset)
    )""",
    """CREATE TABLE IF NOT EXISTS kicad (
        part_id TEXT PRIMARY KEY,
        files TEXT NOT NULL,
        fetched_at REAL NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS wanted (
        part_id TEXT PRIMARY KEY,
        part_number TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        reason TEXT NOT NULL,
        first_asked REAL NOT NULL,
        last_asked REAL NOT NULL,
        times_asked INTEGER NOT NULL
    )""",
)


def query_key(query: str) -> str:
    """CSE search ignores case and extra spaces ("LM358P" and " lm358p" return the same parts)."""
    return " ".join(query.lower().split())


def search_ttl(result: dict[str, Any]) -> float:
    """A year when every part has a model; a week when one doesn't, or nothing was found."""
    parts = result.get("results") or []
    return CSE_FOUND_TTL if parts and all(p.get("has_model") for p in parts) else CSE_NOT_FOUND_TTL


def _serialized(method):
    """Workers share one connection: don't interleave cursors, transactions or close()."""
    @wraps(method)
    def locked(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return locked


class CSEStore:
    """SQLite file of CSE searches and KiCad files. Never raises: if the file can't be opened or
    written, it logs a warning and the client keeps working from memory, as before 0.6.6."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.path, check_same_thread=False)
            try:
                conn.execute("PRAGMA busy_timeout=5000")
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                for statement in _SCHEMA:
                    conn.execute(statement)
                conn.commit()
            except sqlite3.Error:
                conn.close()
                raise
            self._conn = conn
        except (sqlite3.Error, OSError) as e:
            logger.warning(f"CSE store {self.path} unavailable ({e}); answers stay in memory only")

    @property
    def enabled(self) -> bool:
        return self._conn is not None

    @_serialized
    def get_search(self, query: str, offset: int, now: float | None = None) -> dict[str, Any] | None:
        """A stored search that hasn't outlived its TTL, or None."""
        if self._conn is None:
            return None
        try:
            row = self._conn.execute(
                "SELECT result, all_have_models, fetched_at FROM searches WHERE query = ? AND page_offset = ?",
                (query_key(query), offset),
            ).fetchone()
        except sqlite3.Error as e:
            logger.warning(f"CSE store read failed for search {query!r}: {e}")
            return None
        if row is None:
            return None
        result, all_have_models, fetched_at = row
        ttl = CSE_FOUND_TTL if all_have_models else CSE_NOT_FOUND_TTL
        if (time.time() if now is None else now) - fetched_at >= ttl:
            return None
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            return None

    @_serialized
    def put_search(self, query: str, offset: int, result: dict[str, Any], fetched_at: float | None = None) -> bool:
        if self._conn is None:
            return False
        try:
            self._conn.execute(
                "INSERT OR REPLACE INTO searches VALUES (?, ?, ?, ?, ?)",
                (query_key(query), offset, json.dumps(result), int(search_ttl(result) == CSE_FOUND_TTL),
                 time.time() if fetched_at is None else fetched_at),
            )
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            logger.warning(f"CSE store write failed for search {query!r}: {e}")
            return False

    @_serialized
    def get_kicad(self, part_id: int | str) -> dict[str, str] | None:
        """A part's stored KiCad files ({"kicad_symbol", "kicad_footprint"}), however old, or None."""
        if self._conn is None:
            return None
        try:
            row = self._conn.execute(
                "SELECT files FROM kicad WHERE part_id = ?", (str(part_id),)
            ).fetchone()
        except sqlite3.Error as e:
            logger.warning(f"CSE store read failed for part {part_id}: {e}")
            return None
        if row is None:
            return None
        try:
            return json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            return None

    @_serialized
    def put_kicad(self, part_id: int | str, files: dict[str, str], fetched_at: float | None = None) -> bool:
        if self._conn is None:
            return False
        try:
            self._conn.execute(
                "INSERT OR REPLACE INTO kicad VALUES (?, ?, ?)",
                (str(part_id), json.dumps(files), time.time() if fetched_at is None else fetched_at),
            )
            self._conn.execute("DELETE FROM wanted WHERE part_id = ?", (str(part_id),))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            logger.warning(f"CSE store write failed for part {part_id}: {e}")
            return False

    @_serialized
    def part_info(self, part_id: int | str) -> dict[str, Any]:
        """Metadata from a stored search, when available (no upstream lookup)."""
        if self._conn is None:
            return {}
        try:
            # Stored JSON is written by json.dumps; narrow the pages before decoding them.
            rows = self._conn.execute(
                "SELECT result FROM searches WHERE result LIKE ? OR result LIKE ?",
                (f'%"cse_part_id": {part_id}%', f'%"cse_part_id": "{part_id}"%'),
            )
            for (raw,) in rows:
                try:
                    for part in json.loads(raw).get("results", []):
                        if str(part.get("cse_part_id")) == str(part_id):
                            return part
                except (ValueError, TypeError, AttributeError):
                    continue
        except sqlite3.Error as e:
            logger.warning("CSE store metadata read failed for part %s: %s", part_id, e)
        return {}

    @_serialized
    def mark_wanted(self, part_id: int | str, reason: str, part_info: dict[str, Any],
                    now: float | None = None) -> bool:
        """Remember one undelivered model, with no caller information. True on a successful write."""
        if self._conn is None:
            return False
        now = time.time() if now is None else now
        part_number = part_info.get("mfr_part_number") or ""
        manufacturer = part_info.get("manufacturer") or ""
        try:
            # A download/import may finish while the caller is looking up this part's metadata.
            added = self._conn.execute(
                "INSERT OR IGNORE INTO wanted SELECT ?, ?, ?, ?, ?, ?, 0 "
                "WHERE NOT EXISTS (SELECT 1 FROM kicad WHERE part_id = ?)",
                (str(part_id), part_number, manufacturer, reason, now, now, str(part_id)),
            ).rowcount
            self._conn.execute(
                "UPDATE wanted SET part_number = COALESCE(NULLIF(?, ''), part_number), "
                "manufacturer = COALESCE(NULLIF(?, ''), manufacturer), reason = ?, last_asked = ?, "
                "times_asked = times_asked + 1 WHERE part_id = ?",
                (part_number, manufacturer, reason, now, str(part_id)),
            )
            self._conn.commit()
            if added:
                logger.info("CSE model wanted: part %s%s: %s", part_id,
                            f" ({part_number})" if part_number else "", reason)
            return True
        except sqlite3.Error as e:
            logger.warning("CSE store wanted write failed for part %s: %s", part_id, e)
            return False

    @_serialized
    def wanted(self) -> list[dict[str, Any]]:
        """Wanted models, most recently asked first."""
        if self._conn is None:
            return []
        try:
            cursor = self._conn.execute("SELECT * FROM wanted ORDER BY last_asked DESC, part_id")
            fields = [column[0] for column in cursor.description]
            return [dict(zip(fields, row)) for row in cursor]
        except sqlite3.Error as e:
            logger.warning("CSE store wanted read failed: %s", e)
            return []

    @_serialized
    def kicad_last_24h(self, now: float | None = None) -> int:
        """KiCad rows fetched in the last 24 hours, for quota observations."""
        if self._conn is None:
            return 0
        now = time.time() if now is None else now
        try:
            return self._conn.execute(
                "SELECT COUNT(*) FROM kicad WHERE fetched_at > ? AND fetched_at <= ?", (now - 86400, now)
            ).fetchone()[0]
        except sqlite3.Error as e:
            logger.warning("CSE store recent KiCad count failed: %s", e)
            return 0

    @_serialized
    def prune(self, now: float | None = None) -> None:
        """Delete searches past their TTL (they'd be refetched anyway), so the file doesn't keep
        them. KiCad files stay: they have no TTL."""
        if self._conn is None:
            return
        now = time.time() if now is None else now
        try:
            self._conn.execute(
                "DELETE FROM searches WHERE fetched_at <= ? - CASE WHEN all_have_models THEN ? ELSE ? END",
                (now, CSE_FOUND_TTL, CSE_NOT_FOUND_TTL),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.warning(f"CSE store prune failed: {e}")

    @_serialized
    def counts(self) -> dict[str, int]:
        """Stored searches and KiCad parts (for /health)."""
        if self._conn is None:
            return {"searches": 0, "kicad": 0, "wanted": 0}
        try:
            return {
                "searches": self._conn.execute("SELECT COUNT(*) FROM searches").fetchone()[0],
                "kicad": self._conn.execute("SELECT COUNT(*) FROM kicad").fetchone()[0],
                "wanted": self._conn.execute("SELECT COUNT(*) FROM wanted").fetchone()[0],
            }
        except sqlite3.Error:
            return {"searches": 0, "kicad": 0, "wanted": 0}

    @_serialized
    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None


def main(argv: list[str] | None = None) -> int:
    """Inspect the wanted list or import hand-downloaded SamacSys libraries into CSE_STORE_PATH."""
    import argparse
    import io
    import sys
    import zipfile

    from .config import CSE_STORE_PATH
    from .cse_archive import MAX_ZIP_SIZE, extract_kicad

    parser = argparse.ArgumentParser(description=main.__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("wanted", help="print wanted models as tab-separated text, newest first")
    importer = commands.add_parser("import", help="store KiCad files from SamacSys library ZIPs")
    importer.add_argument("--part-id", type=int, metavar="N", help="part ID (one ZIP only; required for stdin)")
    importer.add_argument("zips", nargs="+", metavar="ZIP", help="ZIP paths, or a single - for stdin")
    args = parser.parse_args(argv)
    if args.command == "import":
        if args.part_id is not None and (len(args.zips) != 1 or args.part_id <= 0):
            parser.error("--part-id needs one ZIP and a positive part ID")
        if "-" in args.zips and (len(args.zips) != 1 or args.part_id is None):
            parser.error("a single - reads one ZIP from stdin and needs --part-id")
    if not CSE_STORE_PATH:
        parser.error("set CSE_STORE_PATH to the server's SQLite store")

    store = CSEStore(CSE_STORE_PATH)
    try:
        if not store.enabled:
            print("CSE store is unavailable", file=sys.stderr)
            return 1
        wanted = store.wanted()
        if args.command == "wanted":
            fields = ("part_id", "part_number", "manufacturer", "reason", "first_asked", "last_asked", "times_asked")
            print("\t".join(fields))
            for row in wanted:
                for field in ("first_asked", "last_asked"):
                    row[field] = datetime.fromtimestamp(row[field], timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
                print("\t".join(" ".join(str(row[field]).split()) for field in fields))
            return 0

        failed = False
        for source in args.zips:
            try:
                if source == "-":
                    content = sys.stdin.buffer.read(MAX_ZIP_SIZE + 1)
                else:
                    with open(source, "rb") as incoming:
                        content = incoming.read(MAX_ZIP_SIZE + 1)
                files = extract_kicad(content)
                if not files:
                    raise ValueError("No KiCad files found in model archive")
                part_id = args.part_id
                if part_id is None:
                    stem = Path(source).stem
                    if stem.lower().startswith("lib_"):
                        stem = stem[4:]
                    with zipfile.ZipFile(io.BytesIO(content)) as archive:
                        folders = {name.split("/", 1)[0].casefold() for name in archive.namelist() if "/" in name}
                    names = folders | {stem.casefold()}
                    matches = [row for row in wanted if row["part_number"] and row["part_number"].casefold() in names]
                    if len(matches) != 1:
                        raise ValueError("No unique wanted part matches this ZIP; pass --part-id N")
                    part_id = matches[0]["part_id"]
                if not store.put_kicad(part_id, files):
                    raise ValueError("Could not store KiCad files")
                print(f"{source}\t{part_id}\tstored {', '.join(sorted(files))}")
            except (OSError, ValueError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as e:
                failed = True
                print(f"{source}: {e}", file=sys.stderr)
        return int(failed)
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
