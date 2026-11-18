"""Mouser and DigiKey answers kept across restarts (DISTRIBUTOR_STORE_PATH, on the pcbparts-cache
Docker volume next to the EasyEDA and CSE stores).

Two tables in one SQLite file:
- answers: each part number's full answer (stock, prices, lifecycle), so asking again within
  MOUSER_CACHE_TTL / DIGIKEY_CACHE_TTL (3 days) costs no request; a "not found" is kept
  MOUSER_NOT_FOUND_TTL / DIGIKEY_NOT_FOUND_TTL (a day). mouser_get_part, digikey_get_part and
  part_lifecycle share these rows, so a part one of them fetched is free for the others.
- lifecycle: each part's lifecycle as Mouser or DigiKey stated it, by maker and MPN (lifecycle.py),
  kept LIFECYCLE_TTL (90 days); an unknown status, or "this distributor doesn't list the number",
  LIFECYCLE_UNKNOWN_TTL (a week). Every Mouser/DigiKey answer writes here; part_lifecycle reads it.

Rows keep when they were fetched; lifetimes are applied when they're read, so changing one applies to
rows already stored. Only part numbers and the distributors' answers are kept, nothing about who
asked. With no path (or one that can't be opened) the same tables live in memory and a restart
empties them. Never raises: a failed read is a miss and a failed write is logged.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
import weakref
from pathlib import Path
from typing import Any, Callable

from .config import (
    DIGIKEY_CACHE_TTL, DIGIKEY_NOT_FOUND_TTL, LIFECYCLE_TTL, LIFECYCLE_UNKNOWN_TTL, MOUSER_CACHE_TTL,
    MOUSER_NOT_FOUND_TTL,
)
from .lifecycle import Reading, maker_key
from .search.mpn import mpn_key

logger = logging.getLogger(__name__)

# (found, not found) lifetimes of each source's answers, in seconds
ANSWER_TTLS = {
    "mouser": (MOUSER_CACHE_TTL, MOUSER_NOT_FOUND_TTL),
    "digikey": (DIGIKEY_CACHE_TTL, DIGIKEY_NOT_FOUND_TTL),
}

_SCHEMA = (
    """CREATE TABLE IF NOT EXISTS answers (
        source TEXT NOT NULL,
        key TEXT NOT NULL,
        answer TEXT NOT NULL,
        found INTEGER NOT NULL,
        fetched_at REAL NOT NULL,
        PRIMARY KEY (source, key)
    )""",
    # maker_key is '' on a "not listed" row (found = 0): the distributor has no part with that number
    """CREATE TABLE IF NOT EXISTS lifecycle (
        mpn_key TEXT NOT NULL,
        maker_key TEXT NOT NULL,
        source TEXT NOT NULL,
        mpn TEXT NOT NULL,
        maker TEXT NOT NULL,
        status TEXT NOT NULL,
        raw TEXT,
        last_buy_date TEXT,
        found INTEGER NOT NULL,
        observed_at REAL NOT NULL,
        PRIMARY KEY (mpn_key, maker_key, source)
    )""",
)


def _ttl(found: bool, status: str) -> float:
    return LIFECYCLE_TTL if found and status != "unknown" else LIFECYCLE_UNKNOWN_TTL


class DistributorStore:
    """SQLite file (or memory) of Mouser/DigiKey answers and lifecycle readings."""

    def __init__(self, path: str | Path | None = None, clock: Callable[[], float] = time.time):
        self.path = Path(path) if path else None
        self._clock = clock
        self.persistent = False  # kept across restarts
        self._conn = self._open()
        if self._conn is not None:
            # Closed when the store is dropped, so a store no one closes doesn't leak its connection
            weakref.finalize(self, self._conn.close)

    def _open(self) -> sqlite3.Connection | None:
        if self.path is not None:
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                conn = self._connect(str(self.path), wal=True)
                self.persistent = True
                return conn
            except (sqlite3.Error, OSError) as e:
                logger.warning(f"Distributor store {self.path} unavailable ({e}); answers stay in memory only")
        try:
            return self._connect(":memory:", wal=False)
        except sqlite3.Error as e:  # not expected: then nothing is kept at all
            logger.warning(f"Distributor store unavailable in memory too ({e}); nothing is kept")
            return None

    @staticmethod
    def _connect(target: str, wal: bool) -> sqlite3.Connection:
        conn = sqlite3.connect(target, check_same_thread=False)
        try:
            if wal:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
            for statement in _SCHEMA:
                conn.execute(statement)
            conn.commit()
        except sqlite3.Error:
            conn.close()
            raise
        return conn

    def now(self) -> float:
        return self._clock()

    # --- full answers ---

    def get_answer(self, source: str, key: str) -> tuple[Any, float] | None:
        """A stored answer for this source and key that hasn't outlived its lifetime, and when it
        was fetched; else None."""
        if self._conn is None:
            return None
        try:
            row = self._conn.execute(
                "SELECT answer, found, fetched_at FROM answers WHERE source = ? AND key = ?", (source, key)
            ).fetchone()
        except sqlite3.Error as e:
            logger.warning(f"Distributor store read failed for {source} {key!r}: {e}")
            return None
        if row is None:
            return None
        answer, found, fetched_at = row
        found_ttl, not_found_ttl = ANSWER_TTLS[source]
        if self._clock() - fetched_at >= (found_ttl if found else not_found_ttl):
            return None
        try:
            return json.loads(answer), fetched_at
        except (json.JSONDecodeError, TypeError):
            return None

    def put_answer(self, source: str, key: str, answer: Any, found: bool, fetched_at: float | None = None) -> bool:
        if self._conn is None:
            return False
        try:
            self._conn.execute(
                "INSERT OR REPLACE INTO answers VALUES (?, ?, ?, ?, ?)",
                (source, key, json.dumps(answer, separators=(",", ":")), int(found),
                 self._clock() if fetched_at is None else fetched_at),
            )
            self._conn.commit()
            return True
        except (sqlite3.Error, TypeError, ValueError) as e:
            logger.warning(f"Distributor store write failed for {source} {key!r}: {e}")
            return False

    # --- lifecycle ---

    def readings(self, mpn: str) -> list[Reading]:
        """Every maker's and source's lifecycle reading for an MPN (compared with mpn_key, so
        "LM358-P" finds LM358P), and any "not listed" ones, that haven't expired."""
        key = mpn_key(mpn or "")
        if self._conn is None or not key:
            return []
        try:
            rows = self._conn.execute(
                "SELECT mpn, maker, source, status, raw, observed_at, found, last_buy_date "
                "FROM lifecycle WHERE mpn_key = ?", (key,)
            ).fetchall()
        except sqlite3.Error as e:
            logger.warning(f"Lifecycle store read failed for {mpn!r}: {e}")
            return []
        now = self._clock()
        return [Reading(mpn, maker, source, status, raw, observed_at, bool(found), last_buy)
                for mpn, maker, source, status, raw, observed_at, found, last_buy in rows
                if now - observed_at < _ttl(bool(found), status)]

    def put_readings(self, readings: list[Reading], also_as: str | None = None) -> bool:
        """Keep lifecycle readings (newest replaces older for the same maker, MPN and source). A
        part's reading drops any "not listed" row for its number from that source. also_as: another
        number to file them under too (DigiKey matched it to these parts by its own rules)."""
        if self._conn is None or not readings:
            return False
        rows = []
        for reading in readings:
            keys = {mpn_key(reading.mpn)} | ({mpn_key(also_as)} if also_as else set())
            for key in filter(None, keys):
                rows.append((key, maker_key(reading.maker) if reading.found else "", reading))
        try:
            for key, maker, reading in rows:
                if reading.found:
                    self._conn.execute("DELETE FROM lifecycle WHERE mpn_key = ? AND maker_key = '' AND source = ?",
                                       (key, reading.source))
                self._conn.execute(
                    "INSERT OR REPLACE INTO lifecycle VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (key, maker, reading.source, reading.mpn, reading.maker, reading.status, reading.raw,
                     reading.last_buy_date, int(reading.found), reading.observed_at),
                )
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            logger.warning(f"Lifecycle store write failed: {e}")
            return False

    def put_not_listed(self, mpn: str, source: str, observed_at: float | None = None) -> bool:
        """The source has no part with this number (kept a week). Readings of parts it does list
        under the number stay."""
        return self.put_readings([Reading(mpn, "", source, "unknown", None,
                                          self._clock() if observed_at is None else observed_at, found=False)])

    # --- upkeep ---

    def prune(self) -> None:
        """Delete rows past their lifetime (they'd be fetched again anyway), so the file doesn't keep them."""
        if self._conn is None:
            return
        now = self._clock()
        try:
            for source, (found_ttl, not_found_ttl) in ANSWER_TTLS.items():
                self._conn.execute(
                    "DELETE FROM answers WHERE source = ? AND fetched_at <= ? - CASE WHEN found THEN ? ELSE ? END",
                    (source, now, found_ttl, not_found_ttl))
            self._conn.execute(
                "DELETE FROM lifecycle WHERE observed_at <= ? - CASE WHEN found AND status != 'unknown' THEN ? ELSE ? END",
                (now, LIFECYCLE_TTL, LIFECYCLE_UNKNOWN_TTL))
            self._conn.commit()
        except sqlite3.Error as e:
            logger.warning(f"Distributor store prune failed: {e}")

    def counts(self) -> dict[str, Any]:
        """Stored answers and lifecycle readings, and whether they survive a restart (for /health)."""
        counts: dict[str, Any] = {"answers": 0, "lifecycle": 0, "kept_across_restarts": self.persistent}
        if self._conn is None:
            return counts
        try:
            counts["answers"] = self._conn.execute("SELECT COUNT(*) FROM answers").fetchone()[0]
            counts["lifecycle"] = self._conn.execute("SELECT COUNT(*) FROM lifecycle WHERE found").fetchone()[0]
        except sqlite3.Error:
            pass
        return counts

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
