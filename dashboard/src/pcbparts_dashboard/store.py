"""A single locked SQLite connection and loss-preserving daily merges."""

import json
import os
import sqlite3
import threading
import zlib
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# Notices the page's reader has dismissed (key -> the notice's count then); the oldest go first past this.
MAX_DISMISSALS = 500


def utc_datetime(value: datetime | None = None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def timestamp(value: datetime) -> str:
    return utc_datetime(value).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_timestamp(value: str) -> datetime:
    return utc_datetime(datetime.fromisoformat(value))


class Store:
    def __init__(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            os.fchmod(descriptor, 0o600)
        finally:
            os.close(descriptor)
        self.lock = threading.RLock()
        # Writes that change nothing /api/data shows (dismissals): left out of revision()
        self._ignored_changes = 0
        self._connection = sqlite3.connect(path, check_same_thread=False)
        with self.lock, self._connection:
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.executescript("""
                CREATE TABLE IF NOT EXISTS days (
                    date TEXT PRIMARY KEY, data TEXT NOT NULL, fetched_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS snapshots (
                    fetched_at TEXT PRIMARY KEY, date TEXT NOT NULL, data BLOB NOT NULL
                );
                CREATE INDEX IF NOT EXISTS snapshots_date ON snapshots(date);
                CREATE TABLE IF NOT EXISTS eastern_days (
                    date TEXT PRIMARY KEY, data TEXT NOT NULL,
                    approx INTEGER NOT NULL, computed_at TEXT NOT NULL,
                    rules_version INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS health (
                    fetched_at TEXT PRIMARY KEY, data TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS dismissals (
                    key TEXT PRIMARY KEY, count INTEGER NOT NULL, at TEXT NOT NULL, day TEXT
                );
            """)
            if "day" not in {row[1] for row in self._connection.execute("PRAGMA table_info(dismissals)")}:
                self._connection.execute("ALTER TABLE dismissals ADD COLUMN day TEXT")
            columns = {row[1] for row in self._connection.execute("PRAGMA table_info(eastern_days)")}
            if "rules_version" not in columns:
                self._connection.execute(
                    "ALTER TABLE eastern_days ADD COLUMN rules_version INTEGER NOT NULL DEFAULT 1"
                )

    def close(self) -> None:
        with self.lock:
            self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def get_meta(self, key: str, default: Any = None) -> Any:
        with self.lock:
            row = self._connection.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
            return json.loads(row[0]) if row else default

    def _set_meta(self, key: str, value: Any) -> None:
        self._connection.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, json.dumps(value))
        )

    def set_meta(self, key: str, value: Any) -> None:
        with self.lock, self._connection:
            self._set_meta(key, value)

    def _warn(self, at: str, message: str) -> None:
        warnings = self.get_meta("warnings", [])
        warnings.append({"at": at, "message": message})
        self._set_meta("warnings", warnings[-20:])

    def _merge_day(self, incoming: dict, fetched_at: str) -> dict:
        row = self._connection.execute(
            "SELECT data, fetched_at FROM days WHERE date = ?", (incoming["date"],)
        ).fetchone()
        merged = incoming.copy()
        if row:
            stored = json.loads(row[0])
            old_calls, new_calls = stored.get("calls"), incoming.get("calls")
            if old_calls is not None and new_calls is not None and new_calls < old_calls:
                # A reply older than the stored one (an imported file) has fewer calls because it
                # is older. Only a newer reply with fewer means the server's counts were reset.
                if fetched_at >= row[1]:
                    self._warn(
                        fetched_at,
                        f"{incoming['date']}: incoming calls {new_calls} below stored calls "
                        f"{old_calls}; kept stored record",
                    )
                return stored
            for key, value in stored.items():
                if (
                    key not in merged
                    or merged[key] is None
                    or (merged[key] in ({}, []) and value not in ({}, [], None))
                ):
                    merged[key] = value
            if merged == stored:
                end = timestamp(parse_timestamp(incoming["date"] + "T00:00:00Z") + timedelta(days=1))
                # Once final, another identical fetch adds no information. Partial rows
                # still need their newer timestamp, including the transition to final.
                if row[1] >= end or fetched_at <= row[1]:
                    return stored
                self._connection.execute("UPDATE days SET fetched_at = ? WHERE date = ?",
                                         (fetched_at, incoming["date"]))
                return stored
        self._connection.execute(
            "INSERT OR REPLACE INTO days(date, data, fetched_at) VALUES (?, ?, ?)",
            (incoming["date"], json.dumps(merged), fetched_at),
        )
        return merged

    def merge_day(self, incoming: dict, fetched_at: str) -> dict:
        with self.lock, self._connection:
            return self._merge_day(incoming, fetched_at)

    def _add_snapshot(self, record: dict, fetched_at: str) -> None:
        self._connection.execute(
            "INSERT OR REPLACE INTO snapshots(fetched_at, date, data) VALUES (?, ?, ?)",
            (fetched_at, record["date"], zlib.compress(json.dumps(record).encode())),
        )
        # Kept after pruning: UTC days before it never had snapshots (see first_snapshot_date()).
        first = self.get_meta("first_snapshot_date")
        if first is None or record["date"] < first:
            self._set_meta("first_snapshot_date", record["date"])

    def first_snapshot_date(self) -> str | None:
        """The earliest UTC day any snapshot was ever taken for; set on first use for older stores."""
        with self.lock, self._connection:
            first = self.get_meta("first_snapshot_date")
            if first is None:
                row = self._connection.execute("SELECT MIN(date) FROM snapshots").fetchone()
                if row and row[0]:
                    first = row[0]
                    self._set_meta("first_snapshot_date", first)
            return first

    def add_snapshot(self, record: dict, fetched_at: str) -> None:
        with self.lock, self._connection:
            self._add_snapshot(record, fetched_at)

    def save_stats(self, reply: dict, fetched_at: str) -> int:
        with self.lock, self._connection:
            for record in reply["days"]:
                self._merge_day(record, fetched_at)
            if reply["days"]:
                self._add_snapshot(reply["days"][0], fetched_at)
            for key in ("latency_bounds_ms", "about"):
                if key in reply:
                    self._set_meta(key, reply[key])
            # Whether the server's stats file survives a restart: the newest reply's word, so an
            # imported older file can't replace a later fetch's.
            kept = reply.get("kept_across_restarts")
            saved = self.get_meta("kept_across_restarts")
            if isinstance(kept, bool) and not (isinstance(saved, dict) and str(saved.get("at")) > fetched_at):
                self._set_meta("kept_across_restarts", {"value": kept, "at": fetched_at})
        return len(reply["days"])

    def all_days(self) -> list[dict]:
        with self.lock:
            return [
                json.loads(row[0])
                for row in self._connection.execute("SELECT data FROM days ORDER BY date")
            ]

    def day_inputs(self) -> dict[str, tuple[str, dict]]:
        """Include fetch times so a partial UTC day is never mistaken for a final one."""
        with self.lock:
            return {
                day: (at, json.loads(data))
                for day, at, data in self._connection.execute(
                    "SELECT date, fetched_at, data FROM days ORDER BY date"
                )
            }

    def day_dates(self) -> dict[str, str]:
        with self.lock:
            return dict(self._connection.execute("SELECT date, fetched_at FROM days ORDER BY date"))

    def day_input(self, day: str) -> dict:
        with self.lock:
            row = self._connection.execute("SELECT data FROM days WHERE date = ?", (day,)).fetchone()
            return json.loads(row[0]) if row else {}

    def snapshot_times(self) -> dict[str, list[str]]:
        with self.lock:
            result: dict[str, list[str]] = {}
            for day, at in self._connection.execute("SELECT date, fetched_at FROM snapshots ORDER BY fetched_at"):
                result.setdefault(day, []).append(at)
            return result

    def snapshots_for(self, day: str) -> list[tuple[str, dict]]:
        with self.lock:
            return [(at, json.loads(zlib.decompress(data))) for at, data in self._connection.execute(
                "SELECT fetched_at, data FROM snapshots WHERE date = ? ORDER BY fetched_at", (day,)
            )]

    def eastern_day(self, day: str) -> dict | None:
        with self.lock:
            row = self._connection.execute("SELECT data FROM eastern_days WHERE date = ?", (day,)).fetchone()
            return json.loads(row[0]) if row else None

    def eastern_index(self) -> dict[str, tuple]:
        """Eligibility metadata, without allocating every cached day's nested counters."""
        with self.lock:
            # stale: saved before 0.10.12's dashboard placed starts and bounded addresses; the last
            # field is NULL where the hourly breakdown was never worked out
            return {row[0]: row[1:] for row in self._connection.execute(
                "SELECT date, rules_version, approx, json_extract(data, '$.end'), "
                "json_extract(data, '$.problems.start'), json_extract(data, '$.problems.end'), "
                "json_extract(data, '$.problems.approx'), "
                "json_type(data, '$.starts_complete') IS NULL AND (json_type(data, '$.starts') IS NOT NULL "
                "OR json_type(data, '$.addresses') IS NOT NULL), json_type(data, '$.hour_problems') "
                "FROM eastern_days"
            )}

    def revision(self) -> tuple[int, int]:
        """Include writes through this connection and other processes (e.g. CLI imports), except
        dismissals, which /api/data doesn't carry."""
        with self.lock:
            return (self._connection.total_changes - self._ignored_changes,
                    self._connection.execute("PRAGMA data_version").fetchone()[0])

    def all_snapshots(self) -> dict[str, list[tuple[str, dict]]]:
        with self.lock:
            result: dict[str, list[tuple[str, dict]]] = {}
            for day, at, data in self._connection.execute(
                "SELECT date, fetched_at, data FROM snapshots ORDER BY fetched_at"
            ):
                result.setdefault(day, []).append((at, json.loads(zlib.decompress(data))))
            return result

    def all_eastern_days(self) -> dict[str, dict]:
        with self.lock:
            return {
                day: json.loads(data)
                for day, data in self._connection.execute("SELECT date, data FROM eastern_days")
            }

    def eastern_rules_versions(self) -> dict[str, int]:
        with self.lock:
            return dict(self._connection.execute("SELECT date, rules_version FROM eastern_days"))

    def save_eastern_day(self, record: dict, computed_at: str, *, rules_version: int) -> None:
        with self.lock, self._connection:
            self._connection.execute(
                "INSERT OR REPLACE INTO eastern_days(date, data, approx, computed_at, rules_version) "
                "VALUES (?, ?, ?, ?, ?)",
                (record["date"], json.dumps(record), int(record["approx"]), computed_at, rules_version),
            )

    def newest_stats_at(self) -> str | None:
        with self.lock:
            return self._connection.execute(
                "SELECT MAX(fetched_at) FROM (SELECT fetched_at FROM days "
                "UNION ALL SELECT fetched_at FROM snapshots)"
            ).fetchone()[0]

    def save_health(self, reply: Any, fetched_at: str) -> None:
        with self.lock, self._connection:
            self._connection.execute(
                "INSERT OR REPLACE INTO health(fetched_at, data) VALUES (?, ?)",
                (fetched_at, json.dumps(reply)),
            )
            version = reply.get("version") if isinstance(reply, dict) else None
            if isinstance(version, str) and version:
                first_seen = self.get_meta("version_first_seen", {})
                first_seen[version] = min(first_seen.get(version) or self.version_fetch_at(version) or fetched_at, fetched_at)
                self._set_meta("version_first_seen", first_seen)

    def version_fetch_at(self, version: str, *, last=False, before: str | None = None) -> str | None:
        """Read legacy health history too; first observations survive health pruning."""
        with self.lock:
            matches = [
                at for at, data in self._connection.execute("SELECT fetched_at, data FROM health")
                if (before is None or at < before)
                and isinstance(reply := json.loads(data), dict) and reply.get("version") == version
            ]
            if not last:
                first = self.get_meta("version_first_seen", {}).get(version)
                if first and (before is None or first < before):
                    matches.append(first)
            return (max(matches) if last else min(matches)) if matches else None

    def catalog_changes(self) -> list[dict]:
        """Each change of /health's snapshot.data_as_of between two stored health samples: the
        server loads a new catalog only when it starts, so a restart between them loaded it."""
        changes, previous, previous_at = [], None, None
        with self.lock:
            for at, data in self._connection.execute("SELECT fetched_at, data FROM health ORDER BY fetched_at"):
                reply = json.loads(data)
                snapshot = reply.get("snapshot") if isinstance(reply, dict) else None
                value = snapshot.get("data_as_of") if isinstance(snapshot, dict) else None
                if not isinstance(value, str) or not value:
                    continue
                if previous is not None and value != previous:
                    changes.append({"before": previous_at, "at": at, "data_as_of": value})
                previous, previous_at = value, at
        return changes

    def version_observations(self) -> list[tuple[str, str]]:
        """(fetched_at, version) for every stored health sample with a version, oldest first."""
        with self.lock:
            rows = self._connection.execute("SELECT fetched_at, data FROM health ORDER BY fetched_at").fetchall()
        result = []
        for at, data in rows:
            reply = json.loads(data)
            version = reply.get("version") if isinstance(reply, dict) else None
            if isinstance(version, str) and version:
                result.append((at, version))
        return result

    def dismissals(self) -> list[dict]:
        """day: the Eastern date of the data the notice was dismissed on; count: its count that day."""
        with self.lock:
            return [{"key": key, "count": count, "day": day, "at": at} for key, count, day, at in self._connection.execute(
                "SELECT key, count, day, at FROM dismissals ORDER BY at, key")]

    def _ignoring(self, write) -> None:
        before = self._connection.total_changes
        try:
            with self._connection:
                write()
        finally:
            self._ignored_changes += self._connection.total_changes - before

    def dismiss(self, key: str, count: int, at: str, day: str | None = None) -> None:
        def write():
            self._connection.execute(
                "INSERT OR REPLACE INTO dismissals(key, count, at, day) VALUES (?, ?, ?, ?)", (key, count, at, day))
            self._connection.execute(
                "DELETE FROM dismissals WHERE key NOT IN "
                "(SELECT key FROM dismissals ORDER BY at DESC, key LIMIT ?)", (MAX_DISMISSALS,))
        with self.lock:
            self._ignoring(write)

    def undismiss(self, key: str) -> None:
        with self.lock:
            self._ignoring(lambda: self._connection.execute("DELETE FROM dismissals WHERE key = ?", (key,)))

    def newest_health(self) -> tuple[str | None, Any]:
        with self.lock:
            row = self._connection.execute(
                "SELECT fetched_at, data FROM health ORDER BY fetched_at DESC LIMIT 1"
            ).fetchone()
            return (row[0], json.loads(row[1])) if row else (None, None)

    def closest_snapshot(self, date: str, target: datetime) -> dict | None:
        window = timedelta(minutes=90)
        with self.lock:
            rows = self._connection.execute(
                "SELECT fetched_at, data FROM snapshots "
                "WHERE date = ? AND fetched_at >= ? AND fetched_at <= ?",
                (date, timestamp(target - window), timestamp(target + window)),
            ).fetchall()
            if not rows:
                return None
            at, data = min(rows, key=lambda row: abs(parse_timestamp(row[0]) - target))
            if abs(parse_timestamp(at) - target) > window:
                return None
            return {"date": date, "snapshot_at": at, "record": json.loads(zlib.decompress(data))}

    def prune(self, now: datetime) -> None:
        cutoff = timestamp(now - timedelta(days=45))
        with self.lock, self._connection:
            self._connection.execute("DELETE FROM snapshots WHERE fetched_at < ?", (cutoff,))
            self._connection.execute("DELETE FROM health WHERE fetched_at < ?", (cutoff,))
