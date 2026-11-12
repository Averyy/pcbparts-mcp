"""Bounded, read-only access to recorded stock observations (not a stock ledger)."""

import sqlite3
import threading
from datetime import date, timedelta
from pathlib import Path

from .config import STOCK_HISTORY_DB_PATH
from .db_worker import serialized

# Scrape gap days. Their bulk-missing subcategories were corrected in the history files (the
# parts carried from the day before, as the scraper now does), but smaller losses that day may still
# be part of the gap, so disappearances on them stay labelled. Other dates are not certified complete.
SUSPECT_SCRAPES = ("2026-03-03", "2026-03-16", "2026-03-18", "2026-05-15")
EVENT_LIMIT = 100

WHAT_IS_RECORDED = {
    "changes": "Only changes leaving stock at 1,000 or below are recorded: absolute change >10 at 0-100, >25 at 101-500, >100 at 501-1,000, compared with the previous scrape.",
    "limits": "Stock above 1,000 is not tracked for changes. No events says nothing about stability above that level or between events; small changes are omitted too.",
    "other_events": "New records require 0 < stock <= 1,000. Reappear (a previously listed zero) and library-type changes can be recorded above 1,000. New does not mean first-ever listing.",
    "gone": "Gone means missing from that day's scrape: delisted, below the scrape's 10-unit floor, or a scrape gap. It is not a confirmed stockout; returns above 1,000 may be unrecorded. A gap that empties whole subcategories at once is not recorded as gone: those parts keep their previous stock for up to two days.",
    "before": "Past events have no before-values. stock_before appears only when the recorder stored the actual previous snapshot stock; it is never inferred from an earlier event.",
    "dates": "Dates are UTC recording days. Scrapes can be incomplete; 2026-08-07 has no recorded data. current_stock is a separate catalog snapshot, not live stock.",
}


class StockHistoryDatabase:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path if db_path is not None else STOCK_HISTORY_DB_PATH
        self._conn: sqlite3.Connection | None = None
        self._conn_lock = threading.RLock()
        self._has_before = False
        self._history_start: str | None = None
        self._history_end: str | None = None

    @serialized
    def _ensure_db(self) -> None:
        if self._conn is not None:
            return
        # mode=ro prevents a missing database from silently becoming an empty one.
        conn = sqlite3.connect(self.db_path.resolve().as_uri() + "?mode=ro", uri=True, check_same_thread=False)
        try:
            conn.execute("PRAGMA query_only=ON")
            conn.row_factory = sqlite3.Row
            self._has_before = any(row[1] == "stock_before" for row in conn.execute("PRAGMA table_info(stock_events)"))
            # The build stores the first and last dates; a database built before 0.9.0 has no
            # history_start/history_end, and its date index makes MIN/MAX cheap there.
            meta = {}
            if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='tracking_meta'").fetchone():
                meta = dict(conn.execute("SELECT key, value FROM tracking_meta").fetchall())
            if "history_end" in meta:
                self._history_start, self._history_end = meta.get("history_start"), meta["history_end"]
            else:
                self._history_start = conn.execute("SELECT MIN(date) FROM stock_events").fetchone()[0]
                self._history_end = conn.execute("SELECT MAX(date) FROM stock_events").fetchone()[0]
        except BaseException:
            conn.close()
            raise
        self._conn = conn

    @serialized
    def history(self, lcsc: str, days: int = 180) -> dict:
        self._ensure_db()
        end = self._history_end
        start = (date.fromisoformat(end) - timedelta(days=days - 1)).isoformat() if end else None
        events = []
        more_events = False
        if end:
            before_column = "stock_before" if self._has_before else "NULL AS stock_before"
            rows = self._conn.execute(
                f"SELECT date, event_type, stock, {before_column} FROM stock_events "
                "WHERE lcsc = ? AND date >= ? AND date <= ? "
                "ORDER BY date DESC, event_type DESC LIMIT ?",
                (lcsc, start, end, EVENT_LIMIT + 1),
            ).fetchall()
            more_events = len(rows) > EVENT_LIMIT
            # Look beyond the requested window/cap so a return at its edge still
            # carries the warning about the preceding suspect disappearance.
            gaps = [date.fromisoformat(row[0]) for row in self._conn.execute(
                "SELECT date FROM stock_events WHERE lcsc = ? AND event_type = 'gone' "
                f"AND date IN ({','.join('?' for _ in SUSPECT_SCRAPES)})",
                (lcsc, *SUSPECT_SCRAPES),
            )]
            for row in rows[:EVENT_LIMIT]:
                day, kind = row["date"], row["event_type"]
                note = None
                if kind == "gone":
                    note = "Missing from this scrape; not a confirmed stockout or evidence it is still unavailable."
                    if day in SUSPECT_SCRAPES:
                        note = "suspect_scrape: possible scrape gap on a known incomplete or suspect scrape date; not a confirmed stockout. Returns above 1,000 may be unrecorded."
                elif kind in {"new", "reappear"}:
                    if any(1 <= (date.fromisoformat(day) - gap).days <= 2 for gap in gaps):
                        note = "suspect_scrape: observed again after a possible scrape gap; not a confirmed restock."
                event = {"date": day, "type": kind,
                         "stock_after": None if kind == "gone" else row["stock"], "note": note}
                if row["stock_before"] is not None:
                    event["stock_before"] = row["stock_before"]
                events.append(event)
        return {
            "lcsc": lcsc,
            "window": {"start": start, "end": end,
                       "history_start": self._history_start, "history_end": end},
            "events": events,
            "more_events": more_events,
            "what_is_recorded": dict(WHAT_IS_RECORDED),
        }

    @serialized
    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None


_db = StockHistoryDatabase()


def get_history_db() -> StockHistoryDatabase:
    return _db


def close_history_db() -> None:
    _db.close()
