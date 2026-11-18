"""Mouser and DigiKey answers kept across restarts (DISTRIBUTOR_STORE_PATH, on the pcbparts-cache
Docker volume next to the EasyEDA and CSE stores).

Three tables in one SQLite file:
- answers: each part number's full answer (stock, prices, lifecycle), so asking again within
  MOUSER_CACHE_TTL / DIGIKEY_CACHE_TTL (3 days) costs no request; a "not found" is kept
  MOUSER_NOT_FOUND_TTL / DIGIKEY_NOT_FOUND_TTL (a day). mouser_get_part, digikey_get_part and
  part_lifecycle share these rows, so a part one of them fetched is free for the others.
- lifecycle: each part's lifecycle as Mouser or DigiKey stated it, by maker and MPN (lifecycle.py),
  kept LIFECYCLE_TTL (90 days); an unknown status LIFECYCLE_UNKNOWN_TTL (a week), and "this
  distributor doesn't list the number" LIFECYCLE_NOT_LISTED_TTL (30 days). Every Mouser/DigiKey
  answer writes here; part_lifecycle reads it.
- maker_lookups: per UTC day, maker (maker_key) and distributor, how many of part_lifecycle's
  lookups for that maker's parts the distributor didn't list and how many it did, kept
  MAKER_SKIP_DAYS (30 days): part_lifecycle stops asking a distributor about a maker it never lists
  (maker_not_carried). No part numbers.

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
    DIGIKEY_CACHE_TTL, DIGIKEY_NOT_FOUND_TTL, LIFECYCLE_NOT_LISTED_TTL, LIFECYCLE_TTL, LIFECYCLE_UNKNOWN_TTL,
    MAKER_SKIP_DAYS, MAKER_SKIP_NOT_LISTED, MOUSER_CACHE_TTL, MOUSER_NOT_FOUND_TTL,
)
from .lifecycle import Reading, maker_key
from .search.mpn import mpn_key

logger = logging.getLogger(__name__)

# (found, not found) lifetimes of each source's answers, in seconds
ANSWER_TTLS = {
    "mouser": (MOUSER_CACHE_TTL, MOUSER_NOT_FOUND_TTL),
    "digikey": (DIGIKEY_CACHE_TTL, DIGIKEY_NOT_FOUND_TTL),
}

# Small columns first: a scan by source and time (prune) doesn't read a large answer's overflow pages
_SCHEMA = (
    """CREATE TABLE IF NOT EXISTS answers (
        source TEXT NOT NULL,
        key TEXT NOT NULL,
        found INTEGER NOT NULL,
        fetched_at REAL NOT NULL,
        answer TEXT NOT NULL,
        PRIMARY KEY (source, key)
    )""",
    "CREATE INDEX IF NOT EXISTS answers_age ON answers (source, found, fetched_at)",
    # maker_key is '' on a "not listed" row (found = 0): the distributor has no part with that number
    """CREATE TABLE IF NOT EXISTS lifecycle (
        mpn_key TEXT NOT NULL,
        maker_key TEXT NOT NULL,
        source TEXT NOT NULL,
        found INTEGER NOT NULL,
        observed_at REAL NOT NULL,
        status TEXT NOT NULL,
        mpn TEXT NOT NULL,
        maker TEXT NOT NULL,
        raw TEXT,
        last_buy_date TEXT,
        PRIMARY KEY (mpn_key, maker_key, source)
    )""",
    "CREATE INDEX IF NOT EXISTS lifecycle_age ON lifecycle (observed_at)",
    # day: whole UTC days since 1970 (observed_at // 86400)
    """CREATE TABLE IF NOT EXISTS maker_lookups (
        source TEXT NOT NULL,
        maker_key TEXT NOT NULL,
        day INTEGER NOT NULL,
        not_listed INTEGER NOT NULL DEFAULT 0,
        found INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (source, maker_key, day)
    )""",
)


def _ttl(found: bool, status: str) -> float:
    if not found:
        return LIFECYCLE_NOT_LISTED_TTL
    return LIFECYCLE_TTL if status != "unknown" else LIFECYCLE_UNKNOWN_TTL


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
                "INSERT OR REPLACE INTO answers (source, key, found, fetched_at, answer) VALUES (?, ?, ?, ?, ?)",
                (source, key, int(found), self._clock() if fetched_at is None else fetched_at,
                 json.dumps(answer, separators=(",", ":"))),
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
        number to file them under too (DigiKey matched it to these parts by its own rules), except
        where one of the readings is that number's own for the same maker and source: a JST part
        listed both as B2B-PH-K-S and B2B-PH-K-S(LF)(SN) keeps the second's reading under the second."""
        if self._conn is None or not readings:
            return False
        rows, own = [], set()
        for reading in readings:
            maker = maker_key(reading.maker) if reading.found else ""
            if key := mpn_key(reading.mpn):
                rows.append((key, maker, reading))
                own.add((key, maker, reading.source))
        if also_as and (extra := mpn_key(also_as)):
            for reading in readings:
                maker = maker_key(reading.maker) if reading.found else ""
                if mpn_key(reading.mpn) != extra and (extra, maker, reading.source) not in own:
                    rows.append((extra, maker, reading))
        try:
            for key, maker, reading in rows:
                if reading.found:
                    self._conn.execute("DELETE FROM lifecycle WHERE mpn_key = ? AND maker_key = '' AND source = ?",
                                       (key, reading.source))
                self._conn.execute(
                    "INSERT OR REPLACE INTO lifecycle (mpn_key, maker_key, source, found, observed_at, status, mpn, "
                    "maker, raw, last_buy_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (key, maker, reading.source, int(reading.found), reading.observed_at, reading.status,
                     reading.mpn, reading.maker, reading.raw, reading.last_buy_date),
                )
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            logger.warning(f"Lifecycle store write failed: {e}")
            return False

    def put_not_listed(self, mpn: str, source: str, observed_at: float | None = None) -> bool:
        """The source has no part with this number (kept LIFECYCLE_NOT_LISTED_TTL, 30 days). Readings
        of parts it does list under the number stay."""
        return self.put_readings([Reading(mpn, "", source, "unknown", None,
                                          self._clock() if observed_at is None else observed_at, found=False)])

    # --- which makers a distributor carries (part_lifecycle) ---

    def count_maker_lookups(self, source: str, counts: dict[str, tuple[int, int]], at: float | None = None) -> None:
        """Add part_lifecycle's lookups to today's counts: counts maps a maker key to (not listed,
        listed) for this source."""
        if self._conn is None or not counts:
            return
        day = int((self._clock() if at is None else at) // 86400)
        try:
            for maker, (not_listed, found) in counts.items():
                if maker and (not_listed or found):
                    self._conn.execute(
                        "INSERT INTO maker_lookups (source, maker_key, day, not_listed, found) VALUES (?, ?, ?, ?, ?) "
                        "ON CONFLICT (source, maker_key, day) DO UPDATE SET not_listed = not_listed + excluded.not_listed, "
                        "found = found + excluded.found", (source, maker, day, int(not_listed), int(found)))
            self._conn.commit()
        except sqlite3.Error as e:
            logger.warning(f"Distributor store maker count failed: {e}")

    def makers_not_carried(self, source: str, makers: set[str]) -> set[str]:
        """The maker keys this source didn't list a part of at least MAKER_SKIP_NOT_LISTED times in
        the last MAKER_SKIP_DAYS days, while listing none."""
        makers = {maker for maker in makers if maker}
        if self._conn is None or not makers:
            return set()
        since = int(self._clock() // 86400) - MAKER_SKIP_DAYS + 1
        marks = ", ".join("?" * len(makers))
        try:
            rows = self._conn.execute(
                f"SELECT maker_key FROM maker_lookups WHERE source = ? AND day >= ? AND maker_key IN ({marks}) "
                "GROUP BY maker_key HAVING SUM(found) = 0 AND SUM(not_listed) >= ?",
                (source, since, *sorted(makers), MAKER_SKIP_NOT_LISTED)).fetchall()
        except sqlite3.Error as e:
            logger.warning(f"Distributor store maker read failed: {e}")
            return set()
        return {maker for (maker,) in rows}

    # --- upkeep ---

    def prune(self) -> None:
        """Delete rows past their lifetime (they'd be fetched again anyway), so the file doesn't keep
        them. Each delete is a range on an index (answers_age, lifecycle_age)."""
        if self._conn is None:
            return
        now = self._clock()
        try:
            for source, (found_ttl, not_found_ttl) in ANSWER_TTLS.items():
                for found, ttl in ((1, found_ttl), (0, not_found_ttl)):
                    self._conn.execute("DELETE FROM answers WHERE source = ? AND found = ? AND fetched_at <= ?",
                                       (source, found, now - ttl))
            shortest = min(LIFECYCLE_TTL, LIFECYCLE_UNKNOWN_TTL, LIFECYCLE_NOT_LISTED_TTL)
            self._conn.execute(
                "DELETE FROM lifecycle WHERE observed_at <= ? AND observed_at <= ? - CASE WHEN NOT found THEN ? "
                "WHEN status = 'unknown' THEN ? ELSE ? END",
                (now - shortest, now, LIFECYCLE_NOT_LISTED_TTL, LIFECYCLE_UNKNOWN_TTL, LIFECYCLE_TTL))
            self._conn.execute("DELETE FROM maker_lookups WHERE day <= ?", (int(now // 86400) - MAKER_SKIP_DAYS,))
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
