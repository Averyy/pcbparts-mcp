"""Mouser and DigiKey answers kept across restarts (DISTRIBUTOR_STORE_PATH, on the pcbparts-cache
Docker volume next to the EasyEDA and CSE stores).

Two tables in one SQLite file:
- answers: each part number's full answer (stock, prices, lifecycle), so asking again within
  MOUSER_CACHE_TTL / DIGIKEY_CACHE_TTL (3 days / a day) costs no request; a "not found" is kept
  MOUSER_NOT_FOUND_TTL / DIGIKEY_NOT_FOUND_TTL (3 days). mouser_get_part, digikey_get_part and
  part_lifecycle share these rows, so a part one of them fetched is free for the others.
- lifecycle: each part's lifecycle as Mouser or DigiKey stated it, by maker and MPN (lifecycle.py),
  kept LIFECYCLE_TTL (60 days) when active; nrnd and last_time_buy LIFECYCLE_WINDING_DOWN_TTL (30
  days), an obsolete one LIFECYCLE_OBSOLETE_TTL (a year), an unknown status LIFECYCLE_UNKNOWN_TTL
  and "this distributor doesn't list the number" LIFECYCLE_NOT_LISTED_TTL (90 days each; _ttl).
  Every Mouser/DigiKey answer writes here; part_lifecycle and catalog lookups read it. A reply's
  observed_at is when the reading was fetched. A reading is found by mpn_key ("LM358-P" finds
  LM358P), a "not listed" only by the spelling asked, ignoring case (DigiKey matches that spelling,
  so its miss for LM358-P says nothing about LM358P).

Rows keep when they were fetched; lifetimes are applied when they're read, so changing one applies to
rows already stored. Only part numbers and the distributors' answers are kept, nothing about who
asked. With no path (or one that can't be opened) the same tables live in memory and a restart
empties them. Never raises: a failed read is a miss and a failed write is logged.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
import weakref
from pathlib import Path
from typing import Any, Callable

from .config import (
    DIGIKEY_CACHE_TTL, DIGIKEY_NOT_FOUND_TTL, LIFECYCLE_NOT_LISTED_TTL, LIFECYCLE_OBSOLETE_TTL, LIFECYCLE_TTL,
    LIFECYCLE_UNKNOWN_TTL, LIFECYCLE_WINDING_DOWN_TTL, MOUSER_CACHE_TTL, MOUSER_NOT_FOUND_TTL,
)
from .lifecycle import Reading, maker_key, not_listed_key
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
    # maker_key is not_listed_key(the spelling asked) on a "not listed" row (found = 0): the
    # distributor has no part with that number spelled so (a key no maker has, so neither row
    # replaces the other, and each spelling has its own)
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
)


def _ttl(found: bool, status: str) -> float:
    """How long a lifecycle reading is used: by whether the source lists the number, then its
    status. prune() deletes by the same rule (_PRUNE_LIFECYCLE)."""
    if not found:
        return LIFECYCLE_NOT_LISTED_TTL
    if status == "obsolete":
        return LIFECYCLE_OBSOLETE_TTL
    if status in ("nrnd", "last_time_buy"):
        return LIFECYCLE_WINDING_DOWN_TTL
    return LIFECYCLE_UNKNOWN_TTL if status == "unknown" else LIFECYCLE_TTL


# Deletes the lifecycle rows _ttl has expired. The first bound (now minus the shortest lifetime) is
# the range on lifecycle_age; the rows it leaves to the CASE are those with a longer lifetime (an
# obsolete reading between 30 days and a year old), which stay.
_PRUNE_LIFECYCLE = (
    "DELETE FROM lifecycle WHERE observed_at <= ? AND observed_at <= ? - CASE WHEN NOT found THEN ? "
    "WHEN status = 'obsolete' THEN ? WHEN status IN ('nrnd', 'last_time_buy') THEN ? "
    "WHEN status = 'unknown' THEN ? ELSE ? END"
)
_LIFECYCLE_TTLS = (LIFECYCLE_NOT_LISTED_TTL, LIFECYCLE_OBSOLETE_TTL, LIFECYCLE_WINDING_DOWN_TTL,
                   LIFECYCLE_UNKNOWN_TTL, LIFECYCLE_TTL)


class DistributorStore:
    """SQLite file (or memory) of Mouser/DigiKey answers and lifecycle readings."""

    def __init__(self, path: str | Path | None = None, clock: Callable[[], float] = time.time):
        self.path = Path(path) if path else None
        self._clock = clock
        self.persistent = False  # kept across restarts
        # Every use of the connection holds this: the event loop and the component pool's workers
        # (jlc_get_parts reads lifecycle inside its job) share it, and Python's sqlite3 shares one
        # prepared statement between cursors running the same SQL, so two readers at once could get
        # each other's rows, none, or a row of NULLs
        self._lock = threading.Lock()
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
        # One connection for the event loop and the database workers, used under self._lock
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
        try:
            with self._lock:
                if self._conn is None:
                    return None
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
        try:
            row = (source, key, int(found), self._clock() if fetched_at is None else fetched_at,
                   json.dumps(answer, separators=(",", ":")))
            with self._lock:
                if self._conn is None:
                    return False
                self._conn.execute(
                    "INSERT OR REPLACE INTO answers (source, key, found, fetched_at, answer) VALUES (?, ?, ?, ?, ?)", row)
                self._conn.commit()
            return True
        except (sqlite3.Error, TypeError, ValueError) as e:
            logger.warning(f"Distributor store write failed for {source} {key!r}: {e}")
            return False

    # --- lifecycle ---

    def readings(self, mpn: str) -> list[Reading]:
        """Every maker's and source's lifecycle reading for an MPN (compared with mpn_key, so
        "LM358-P" finds LM358P), and the sources' "not listed" for this spelling of it (ignoring
        case and outer spaces), that haven't expired."""
        key = mpn_key(mpn or "")
        if not key:
            return []
        try:
            with self._lock:
                if self._conn is None:
                    return []
                rows = self._conn.execute(
                    "SELECT mpn, maker, source, status, raw, observed_at, found, last_buy_date "
                    "FROM lifecycle WHERE mpn_key = ? AND (found OR maker_key = ?)", (key, not_listed_key(mpn))
                ).fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.warning(f"Lifecycle store read failed for {mpn!r}: {e}")
            return []
        now = self._clock()
        return [Reading(mpn, maker, source, status, raw, observed_at, bool(found), last_buy)
                for mpn, maker, source, status, raw, observed_at, found, last_buy in rows
                if now - observed_at < _ttl(bool(found), status)]

    def put_readings(self, readings: list[Reading], also_as: str | None = None) -> bool:
        """Keep lifecycle readings (newest replaces older for the same maker, MPN and source; a "not
        listed" one for the same spelling and source). A part's reading drops any "not listed" row
        for its number (every spelling) from that source. also_as: another number to file them under
        too (DigiKey matched it to these parts by its own rules), except where one of the readings
        is that number's own for the same maker and source: a JST part listed both as B2B-PH-K-S and
        B2B-PH-K-S(LF)(SN) keeps the second's reading under the second."""
        if not readings:
            return False
        rows, own = [], set()
        for reading in readings:
            maker = maker_key(reading.maker) if reading.found else not_listed_key(reading.mpn)
            if key := mpn_key(reading.mpn):
                rows.append((key, maker, reading))
                own.add((key, maker, reading.source))
        if also_as and (extra := mpn_key(also_as)):
            for reading in readings:
                maker = maker_key(reading.maker) if reading.found else not_listed_key(also_as)
                if mpn_key(reading.mpn) != extra and (extra, maker, reading.source) not in own:
                    rows.append((extra, maker, reading))
        try:
            with self._lock:
                if self._conn is None:
                    return False
                for key, maker, reading in rows:
                    if reading.found:  # the source's "not listed" row for the number
                        self._conn.execute("DELETE FROM lifecycle WHERE mpn_key = ? AND source = ? AND NOT found",
                                           (key, reading.source))
                    self._conn.execute(
                        "INSERT OR REPLACE INTO lifecycle (mpn_key, maker_key, source, found, observed_at, status, "
                        "mpn, maker, raw, last_buy_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (key, maker, reading.source, int(reading.found), reading.observed_at, reading.status,
                         reading.mpn, reading.maker, reading.raw, reading.last_buy_date),
                    )
                self._conn.commit()
            return True
        except (sqlite3.Error, ValueError) as e:
            logger.warning(f"Lifecycle store write failed: {e}")
            return False

    def put_not_listed(self, mpn: str, source: str, observed_at: float | None = None) -> bool:
        """The source has no part with this number spelled so (kept LIFECYCLE_NOT_LISTED_TTL, 90
        days). Readings of parts it does list under the number stay."""
        return self.put_readings([Reading(mpn, "", source, "unknown", None,
                                          self._clock() if observed_at is None else observed_at, found=False)])

    # --- upkeep ---

    def prune(self) -> None:
        """Delete rows past their lifetime (they'd be fetched again anyway), so the file doesn't keep
        them. Each delete is a range on an index (answers_age, lifecycle_age)."""
        now = self._clock()
        try:
            with self._lock:
                if self._conn is None:
                    return
                for source, (found_ttl, not_found_ttl) in ANSWER_TTLS.items():
                    for found, ttl in ((1, found_ttl), (0, not_found_ttl)):
                        self._conn.execute("DELETE FROM answers WHERE source = ? AND found = ? AND fetched_at <= ?",
                                           (source, found, now - ttl))
                self._conn.execute(_PRUNE_LIFECYCLE, (now - min(_LIFECYCLE_TTLS), now, *_LIFECYCLE_TTLS))
                self._conn.commit()
        except sqlite3.Error as e:
            logger.warning(f"Distributor store prune failed: {e}")

    def counts(self) -> dict[str, Any]:
        """Stored answers and lifecycle readings, and whether they survive a restart (for /health)."""
        counts: dict[str, Any] = {"answers": 0, "lifecycle": 0, "kept_across_restarts": self.persistent}
        try:
            with self._lock:
                if self._conn is None:
                    return counts
                counts["answers"] = self._conn.execute("SELECT COUNT(*) FROM answers").fetchone()[0]
                counts["lifecycle"] = self._conn.execute("SELECT COUNT(*) FROM lifecycle WHERE found").fetchone()[0]
        except sqlite3.Error:
            pass
        return counts

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None
