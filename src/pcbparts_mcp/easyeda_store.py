"""Persistent EasyEDA footprint answers (docs/ref-easyeda-api.md).

Two sources sit behind the in-memory footprint cache in client.py:
- EasyEDAStore: a read-write SQLite file holding every live /api/products answer. On a Docker
  volume it survives restarts and redeploys.
- The seed: data/easyeda/footprints.csv (built by scripts/build_easyeda_seed.py), loaded into the
  easyeda_footprints table of components.db at build time and read through ComponentDatabase.

pick_answer() decides which answer, if any, can be served without asking EasyEDA.
"""

import csv
import datetime
import logging
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Iterable, NamedTuple

logger = logging.getLogger(__name__)

# Seed file, relative to the data dir. One row per LCSC part, sorted by part number. has_footprint
# is 1/0; checked is when the row's answer was recorded (UTC, CHECKED_FORMAT), and a row whose
# answer hasn't changed keeps it, so a refresh only rewrites the rows that changed; source is "s"
# (EasyEDA library search, can only say "has one") or "p" (/api/products).
SEED_FILE = Path("easyeda") / "footprints.csv"
SEED_COLUMNS = ("lcsc", "has_footprint", "symbol_uuid", "footprint_uuid", "checked", "source")
CHECKED_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_LCSC_RE = re.compile(r"C\d+")
_UUID_RE = re.compile(r"[0-9a-fA-F]{32}")


class SeedRow(NamedTuple):
    lcsc: str
    has_footprint: bool
    symbol_uuid: str | None
    footprint_uuid: str | None
    checked: str  # CHECKED_FORMAT, UTC
    source: str  # "s" or "p"


def lcsc_number(lcsc: str) -> int:
    """Numeric part of an LCSC code, for sorting (C2040 before C10000)."""
    return int(lcsc[1:]) if lcsc[1:].isdigit() else 0


def seed_checked_at(checked: str) -> int:
    """Unix time of a seed row's checked value."""
    moment = datetime.datetime.strptime(checked, CHECKED_FORMAT).replace(tzinfo=datetime.timezone.utc)
    return int(moment.timestamp())


def format_checked(timestamp: float) -> str:
    """A unix time as a seed row's checked value."""
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).strftime(CHECKED_FORMAT)


def answer_problem(has_footprint: bool, symbol_uuid: str | None, footprint_uuid: str | None) -> str | None:
    """Why a footprint answer can't be kept in the store or the seed, or None if it can. "Has a
    footprint" never expires, so it must carry a symbol UUID that jlc_get_pinout can use."""
    if has_footprint:
        if not symbol_uuid or not _UUID_RE.fullmatch(symbol_uuid):
            return f"has_footprint=1 needs a 32-hex symbol_uuid, got {symbol_uuid!r}"
        if footprint_uuid and not _UUID_RE.fullmatch(footprint_uuid):
            return f"footprint_uuid {footprint_uuid!r} isn't 32 hex"
    elif symbol_uuid or footprint_uuid:
        return "has_footprint=0 with UUIDs"
    return None


def _row_problem(lcsc: str, has: str, symbol_uuid: str, footprint_uuid: str, checked: str, source: str) -> str | None:
    """Why a seed CSV row can't be served, or None if it's fine."""
    if not _LCSC_RE.fullmatch(lcsc):
        return f"part number {lcsc!r} isn't an LCSC code"
    if has not in ("0", "1"):
        return f"has_footprint must be 0 or 1, got {has!r}"
    problem = answer_problem(has == "1", symbol_uuid or None, footprint_uuid or None)
    if problem is not None:
        return problem
    try:
        seed_checked_at(checked)
    except ValueError:
        return f"checked must look like 2026-10-12T14:03:22Z, got {checked!r}"
    if source not in ("s", "p"):
        return f"source must be s or p, got {source!r}"
    return None


def read_seed_csv(path: str | Path) -> dict[str, SeedRow]:
    """The seed's rows by part number. Raises ValueError on any malformed row, so a bad file fails
    the DB build instead of being served."""
    rows: dict[str, SeedRow] = {}
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if tuple(header or ()) != SEED_COLUMNS:
            raise ValueError(f"{path}: expected columns {','.join(SEED_COLUMNS)}, got {header}")
        for line, fields in enumerate(reader, 2):
            if len(fields) != len(SEED_COLUMNS):
                raise ValueError(f"{path} line {line}: expected {len(SEED_COLUMNS)} fields, got {len(fields)}")
            lcsc, has, symbol_uuid, footprint_uuid, checked, source = fields
            problem = _row_problem(lcsc, has, symbol_uuid, footprint_uuid, checked, source)
            if problem is None and lcsc in rows:
                problem = f"{lcsc} appears twice"
            if problem is not None:
                raise ValueError(f"{path} line {line}: {problem}")
            rows[lcsc] = SeedRow(lcsc, has == "1", symbol_uuid or None, footprint_uuid or None, checked, source)
    return rows


def write_seed_csv(path: str | Path, rows: Iterable[SeedRow]) -> None:
    """Write rows sorted by part number, atomically (temp file, then replace)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(SEED_COLUMNS)
        for r in sorted(rows, key=lambda r: lcsc_number(r.lcsc)):
            writer.writerow((r.lcsc, int(r.has_footprint), r.symbol_uuid or "", r.footprint_uuid or "",
                             r.checked, r.source))
    os.replace(tmp, path)

_SCHEMA = """
    CREATE TABLE IF NOT EXISTS footprints (
        lcsc TEXT PRIMARY KEY,
        has_footprint INTEGER,  -- 1 has one, 0 has none, NULL = re-check (its symbol UUID stopped working)
        symbol_uuid TEXT,
        footprint_uuid TEXT,
        checked_at REAL NOT NULL  -- unix time of the answer
    )
"""


class FootprintAnswer(NamedTuple):
    has_footprint: bool | None  # None marks a part to re-check
    symbol_uuid: str | None
    footprint_uuid: str | None
    checked_at: float

    def as_result(self) -> dict[str, bool | str | None]:
        return {
            "has_easyeda_footprint": self.has_footprint,
            "easyeda_symbol_uuid": self.symbol_uuid,
            "easyeda_footprint_uuid": self.footprint_uuid,
        }


def pick_answer(
    candidates: Iterable[FootprintAnswer | None], now: float, not_found_ttl: float
) -> FootprintAnswer | None:
    """The newest answer if it can still be served, else None (ask EasyEDA).

    "Has a footprint" never expires. "No footprint" expires after not_found_ttl. A re-check
    marker means the stored IDs stopped working, so nothing older counts.
    """
    newest = max((c for c in candidates if c is not None), key=lambda c: c.checked_at, default=None)
    if newest is None or newest.has_footprint is None:
        return None
    if newest.has_footprint is False and now - newest.checked_at >= not_found_ttl:
        return None
    return newest


class EasyEDAStore:
    """SQLite file of live footprint answers. Never raises: if the file can't be opened or
    written, it logs a warning and the client keeps working from memory, as before 0.6.0."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._conn: sqlite3.Connection | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.path, check_same_thread=False)
            try:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute(_SCHEMA)
                conn.commit()
            except sqlite3.Error:
                conn.close()
                raise
            self._conn = conn
        except (sqlite3.Error, OSError) as e:
            logger.warning(f"EasyEDA footprint store {self.path} unavailable ({e}); answers stay in memory only")

    @property
    def enabled(self) -> bool:
        return self._conn is not None

    def get(self, lcsc: str) -> FootprintAnswer | None:
        if self._conn is None:
            return None
        try:
            row = self._conn.execute(
                "SELECT has_footprint, symbol_uuid, footprint_uuid, checked_at FROM footprints WHERE lcsc = ?",
                (lcsc,),
            ).fetchone()
        except sqlite3.Error as e:
            logger.warning(f"EasyEDA footprint store read failed for {lcsc}: {e}")
            return None
        if row is None:
            return None
        has, symbol_uuid, footprint_uuid, checked_at = row
        return FootprintAnswer(None if has is None else bool(has), symbol_uuid, footprint_uuid, checked_at)

    def _write(self, lcsc: str, has: int | None, symbol_uuid: str | None, footprint_uuid: str | None,
               checked_at: float) -> bool:
        if self._conn is None:
            return False
        try:
            self._conn.execute(
                "INSERT OR REPLACE INTO footprints VALUES (?, ?, ?, ?, ?)",
                (lcsc, has, symbol_uuid, footprint_uuid, checked_at),
            )
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            logger.warning(f"EasyEDA footprint store write failed for {lcsc}: {e}")
            return False

    def put(self, lcsc: str, result: dict, checked_at: float | None = None) -> bool:
        """Store a real answer (has_easyeda_footprint True or False). Unknowns aren't stored, and
        neither is an answer answer_problem() rejects. Returns whether the answer was written."""
        has = result.get("has_easyeda_footprint")
        if has is None:
            return False
        symbol_uuid, footprint_uuid = result.get("easyeda_symbol_uuid"), result.get("easyeda_footprint_uuid")
        problem = answer_problem(bool(has), symbol_uuid, footprint_uuid)
        if problem is not None:
            logger.warning(f"Not storing EasyEDA footprint answer for {lcsc}: {problem}")
            return False
        return self._write(lcsc, int(bool(has)), symbol_uuid, footprint_uuid,
                           time.time() if checked_at is None else checked_at)

    def mark_stale(self, lcsc: str, checked_at: float | None = None) -> bool:
        """Make the next lookup ask EasyEDA, overriding any older stored or seed answer. Returns
        whether the marker was written."""
        return self._write(lcsc, None, None, None, time.time() if checked_at is None else checked_at)

    def __len__(self) -> int:
        if self._conn is None:
            return 0
        try:
            return self._conn.execute("SELECT COUNT(*) FROM footprints").fetchone()[0]
        except sqlite3.Error:
            return 0

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
