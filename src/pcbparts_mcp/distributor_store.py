"""Mouser and DigiKey answers kept across restarts (DISTRIBUTOR_STORE_PATH, on the pcbparts-cache
Docker volume next to the EasyEDA and CSE stores).

Four tables in one SQLite file:
- answers: each part number's full answer (stock, prices, lifecycle), so asking again within
  MOUSER_CACHE_TTL / DIGIKEY_CACHE_TTL (3 days) costs no request; a "not found" is kept
  MOUSER_NOT_FOUND_TTL / DIGIKEY_NOT_FOUND_TTL (a day). mouser_get_part, digikey_get_part and
  part_lifecycle share these rows, so a part one of them fetched is free for the others.
- lifecycle: each part's lifecycle as Mouser or DigiKey stated it, by maker and MPN (lifecycle.py),
  kept LIFECYCLE_TTL (90 days); an unknown status LIFECYCLE_UNKNOWN_TTL (a week), and "this
  distributor doesn't list the number" LIFECYCLE_NOT_LISTED_TTL (30 days). Every Mouser/DigiKey
  answer writes here; part_lifecycle reads it. A part's reading is found by mpn_key ("LM358-P" finds
  LM358P), a "not listed" only by the spelling asked, ignoring case (DigiKey matches that spelling,
  so its miss for LM358-P says nothing about LM358P).
- maker_parts: per UTC day, maker (maker_key), distributor and part (mpn_key), whether
  part_lifecycle found the distributor listing that maker's part or freshly not listing the number
  at all, kept MAKER_SKIP_DAYS (30 days): part_lifecycle stops asking a distributor about a maker it
  never lists (maker_not_carried). Nothing about who asked.
- listed_makers: each maker name a distributor returned a part under, and when it last did, kept
  MAKER_SKIP_DAYS: every result of every Mouser and DigiKey answer, fresh or read from answers,
  whatever number it's put down to (note_listed_makers). A maker listed under any name that
  makers_match takes as the same one ("NXP USA Inc." for "NXP Semicon") is never maker_not_carried.
  A few thousand rows at most.

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
from .lifecycle import Reading, maker_key, makers_match, not_listed_key
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
    # Replaced by listed_makers before release (makers_not_carried compared exact keys with it)
    "DROP INDEX IF EXISTS lifecycle_maker",
    # day: whole UTC days since 1970 (observed_at // 86400); found: listed (1) or not listed (0).
    # One row per part a day, so a part counts once however often it's looked up.
    """CREATE TABLE IF NOT EXISTS maker_parts (
        source TEXT NOT NULL,
        maker_key TEXT NOT NULL,
        day INTEGER NOT NULL,
        mpn_key TEXT NOT NULL,
        found INTEGER NOT NULL,
        PRIMARY KEY (source, maker_key, day, mpn_key)
    )""",
    # observed_at: the newest listing under this name (put_readings)
    """CREATE TABLE IF NOT EXISTS listed_makers (
        source TEXT NOT NULL,
        maker_key TEXT NOT NULL,
        maker TEXT NOT NULL,
        observed_at REAL NOT NULL,
        PRIMARY KEY (source, maker_key, maker)
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
        "LM358-P" finds LM358P), and the sources' "not listed" for this spelling of it (ignoring
        case and outer spaces), that haven't expired."""
        key = mpn_key(mpn or "")
        if self._conn is None or not key:
            return []
        try:
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
        if self._conn is None or not readings:
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
            for key, maker, reading in rows:
                if reading.found:  # the source's "not listed" row for the number
                    self._conn.execute("DELETE FROM lifecycle WHERE mpn_key = ? AND source = ? AND NOT found",
                                       (key, reading.source))
                self._conn.execute(
                    "INSERT OR REPLACE INTO lifecycle (mpn_key, maker_key, source, found, observed_at, status, mpn, "
                    "maker, raw, last_buy_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (key, maker, reading.source, int(reading.found), reading.observed_at, reading.status,
                     reading.mpn, reading.maker, reading.raw, reading.last_buy_date),
                )
            self._put_listed([(reading.source, reading.maker, reading.observed_at)
                              for reading in readings if reading.found])
            self._conn.commit()
            return True
        except (sqlite3.Error, ValueError) as e:
            logger.warning(f"Lifecycle store write failed: {e}")
            return False

    def note_listed_makers(self, source: str, makers: list[str | None], observed_at: float) -> None:
        """Keep that this source returned parts under these maker names (as it names them) at
        observed_at: every result of an answer, whatever number it's put down to, so the maker is
        never maker_not_carried while it's in the window."""
        if self._conn is None or not makers:
            return
        try:
            self._put_listed([(source, maker, observed_at) for maker in makers])
            self._conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.warning(f"Distributor store maker listing failed: {e}")

    def _put_listed(self, listings: list[tuple[str, str | None, float]]) -> None:
        """listed_makers rows for (source, maker name, when) listings, newest kept; no commit."""
        listed: dict[tuple[str, str, str], float] = {}
        for source, maker, at in listings:
            if isinstance(maker, str) and (key := maker_key(maker)):
                name = (source, key, maker.strip())
                listed[name] = max(listed.get(name, 0.0), at)
        if listed:
            self._conn.executemany(
                "INSERT INTO listed_makers (source, maker_key, maker, observed_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT (source, maker_key, maker) DO UPDATE SET observed_at = excluded.observed_at "
                "WHERE excluded.observed_at > listed_makers.observed_at",
                [(*name, at) for name, at in listed.items()])

    def put_not_listed(self, mpn: str, source: str, observed_at: float | None = None) -> bool:
        """The source has no part with this number spelled so (kept LIFECYCLE_NOT_LISTED_TTL, 30
        days). Readings of parts it does list under the number stay."""
        return self.put_readings([Reading(mpn, "", source, "unknown", None,
                                          self._clock() if observed_at is None else observed_at, found=False)])

    # --- which makers a distributor carries (part_lifecycle) ---

    def _first_day(self) -> int:
        """The first UTC day of the maker counts' window (the last MAKER_SKIP_DAYS days)."""
        return int(self._clock() // 86400) - MAKER_SKIP_DAYS + 1

    def count_maker_parts(self, source: str, parts: list[tuple[str, str, bool, float]]) -> None:
        """Keep what part_lifecycle learned about makers' parts from this source: (maker key, part's
        mpn_key, listed, when), counted on the UTC day of when (a kept listing on the day it was
        observed; one older than the window isn't kept). Each part once a day per maker: listed
        wins over not listed."""
        if self._conn is None or not parts:
            return
        first = self._first_day()
        rows: dict[tuple[str, int, str], int] = {}
        for maker, key, found, at in parts:
            day = int(at // 86400)
            if maker and key and day >= first:
                rows[(maker, day, key)] = max(rows.get((maker, day, key), 0), int(found))
        try:
            self._conn.executemany(
                "INSERT INTO maker_parts (source, maker_key, day, mpn_key, found) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT (source, maker_key, day, mpn_key) DO UPDATE SET found = excluded.found "
                "WHERE excluded.found > maker_parts.found",
                [(source, maker, day, key, found) for (maker, day, key), found in rows.items()])
            self._conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.warning(f"Distributor store maker count failed: {e}")

    def makers_not_carried(self, source: str, makers: set[str], names: dict[str, set[str]] | None = None) -> set[str]:
        """The maker keys this source didn't list at least MAKER_SKIP_NOT_LISTED different parts of
        in the last MAKER_SKIP_DAYS days, while listing none: neither counted as listed by
        part_lifecycle nor listed in any answer it gave under a name makers_match takes as the
        maker's (listed_makers; checked only for makers the counts would skip). names: the names
        given for each key (part_lifecycle's makers as asked; the key itself when missing)."""
        makers = {maker for maker in makers if maker}
        if self._conn is None or not makers:
            return set()
        first = self._first_day()
        marks = ", ".join("?" * len(makers))
        try:
            rows = self._conn.execute(
                f"SELECT maker_key FROM maker_parts WHERE source = ? AND day >= ? AND maker_key IN ({marks}) "
                "GROUP BY maker_key HAVING MAX(found) = 0 AND COUNT(DISTINCT mpn_key) >= ?",
                (source, first, *sorted(makers), MAKER_SKIP_NOT_LISTED)).fetchall()
            skipped = {maker for (maker,) in rows}
            if skipped:
                listed = self._conn.execute("SELECT maker_key, maker FROM listed_makers WHERE source = ? "
                                            "AND observed_at >= ?", (source, first * 86400)).fetchall()
                skipped = {key for key in skipped if not any(
                    listed_key == key or any(makers_match(name, maker) for name in (names or {}).get(key) or {key})
                    for listed_key, maker in listed)}
        except (sqlite3.Error, ValueError) as e:
            logger.warning(f"Distributor store maker read failed: {e}")
            return set()
        return skipped

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
            self._conn.execute("DELETE FROM maker_parts WHERE day <= ?", (int(now // 86400) - MAKER_SKIP_DAYS,))
            self._conn.execute("DELETE FROM listed_makers WHERE observed_at < ?",
                               ((int(now // 86400) - MAKER_SKIP_DAYS + 1) * 86400,))
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
