"""ComponentSearchEngine answers kept across restarts (CSE_STORE_PATH, on the pcbparts-cache
Docker volume next to the EasyEDA store).

An uncached CSE search takes 11-15 s; the in-memory caches in cse.py are emptied by every restart,
including each daily data deploy. The store sits behind them:
- Searches: one query's results. Kept CSE_FOUND_TTL (a year) when every part has a model; a part
  without one gets one when someone asks CSE to build it, so a search with such a part, or with no
  parts, is kept CSE_NOT_FOUND_TTL (a week).
- KiCad files: one part's symbol and footprint, kept CSE_FOUND_TTL. Nothing tells us a model was
  revised, so a year lets a new version come through.

Rows keep when they were fetched; the lifetime is applied when they're read, so changing a TTL
applies to rows already stored.
"""

import json
import logging
import sqlite3
import time
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
)


def query_key(query: str) -> str:
    """CSE search ignores case and extra spaces ("LM358P" and " lm358p" return the same parts)."""
    return " ".join(query.lower().split())


def search_ttl(result: dict[str, Any]) -> float:
    """A year when every part has a model; a week when one doesn't, or nothing was found."""
    parts = result.get("results") or []
    return CSE_FOUND_TTL if parts and all(p.get("has_model") for p in parts) else CSE_NOT_FOUND_TTL


class CSEStore:
    """SQLite file of CSE searches and KiCad files. Never raises: if the file can't be opened or
    written, it logs a warning and the client keeps working from memory, as before 0.6.6."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._conn: sqlite3.Connection | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.path, check_same_thread=False)
            try:
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

    def get_kicad(self, part_id: int | str, now: float | None = None) -> dict[str, str] | None:
        """A part's stored KiCad files ({"kicad_symbol", "kicad_footprint"}) less than a year old, or None."""
        if self._conn is None:
            return None
        try:
            row = self._conn.execute(
                "SELECT files, fetched_at FROM kicad WHERE part_id = ?", (str(part_id),)
            ).fetchone()
        except sqlite3.Error as e:
            logger.warning(f"CSE store read failed for part {part_id}: {e}")
            return None
        if row is None or (time.time() if now is None else now) - row[1] >= CSE_FOUND_TTL:
            return None
        try:
            return json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            return None

    def put_kicad(self, part_id: int | str, files: dict[str, str], fetched_at: float | None = None) -> bool:
        if self._conn is None:
            return False
        try:
            self._conn.execute(
                "INSERT OR REPLACE INTO kicad VALUES (?, ?, ?)",
                (str(part_id), json.dumps(files), time.time() if fetched_at is None else fetched_at),
            )
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            logger.warning(f"CSE store write failed for part {part_id}: {e}")
            return False

    def prune(self, now: float | None = None) -> None:
        """Delete rows past their TTL (they'd be refetched anyway), so the file doesn't keep them."""
        if self._conn is None:
            return
        now = time.time() if now is None else now
        try:
            self._conn.execute(
                "DELETE FROM searches WHERE fetched_at <= ? - CASE WHEN all_have_models THEN ? ELSE ? END",
                (now, CSE_FOUND_TTL, CSE_NOT_FOUND_TTL),
            )
            self._conn.execute("DELETE FROM kicad WHERE fetched_at <= ?", (now - CSE_FOUND_TTL,))
            self._conn.commit()
        except sqlite3.Error as e:
            logger.warning(f"CSE store prune failed: {e}")

    def counts(self) -> dict[str, int]:
        """Stored searches and KiCad parts (for /health)."""
        if self._conn is None:
            return {"searches": 0, "kicad": 0}
        try:
            return {
                "searches": self._conn.execute("SELECT COUNT(*) FROM searches").fetchone()[0],
                "kicad": self._conn.execute("SELECT COUNT(*) FROM kicad").fetchone()[0],
            }
        except sqlite3.Error:
            return {"searches": 0, "kicad": 0}

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
