"""Anonymous usage counts per UTC day, served at /mcp/stats.

Per day: calls to each tool (with error replies, failures, empty answers and the average time), the
MCP apps that connected (by the name each app reports when it connects), the number of distinct
callers, and what happened to Mouser/DigiKey lookups (sent, answered from the cache, or turned away
by the shared limits). No IPs, queries or part numbers are kept: callers are counted through salted
hashes held in memory for the current day only, with a new random salt each day. A restart starts
a new set, so a caller seen before and after one on the same day counts twice.

The server writes the counts to USAGE_STATS_PATH (a JSON file on the cache volume) every minute and
at shutdown; unset means memory only. The file keeps a year; /mcp/stats shows the last 30 days. Nothing here raises on a bad or unwritable file, like
QuotaStore.
"""

import datetime
import hashlib
import json
import logging
import os
import re
import secrets
import time
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

KEEP_DAYS = 365  # in the file (about 650 KB for a busy year, at most about 1.5 MB)
PUBLIC_DAYS = 30  # the most /mcp/stats shows
MAX_CALLERS = 100_000  # distinct callers counted a day (bounds memory); later ones aren't counted
MAX_APPS = 50  # distinct app names a day; later ones count as "other"
APP_NAME_LENGTH = 40
_NOT_IN_APP_NAME = re.compile(r"[^A-Za-z0-9 ._()/+-]")  # app names are self-reported and shown publicly
TOOL_COUNTS = ("calls", "errors", "failed", "empty", "ms")
DISTRIBUTOR_EVENTS = ("sent", "cached", "limited")


def _new_day() -> dict[str, Any]:
    return {"tools": {}, "apps": {}, "callers": 0, "distributors": {}}


def _int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0


def _dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _clean_day(day: dict) -> dict[str, Any]:
    """A day read from the file, with anything malformed dropped, so counting can't fail on it."""
    clean = _new_day()
    for name, counts in _dict(day.get("tools")).items():
        if isinstance(counts, dict):
            clean["tools"][str(name)] = {key: _int(counts.get(key)) for key in TOOL_COUNTS}
    for name, counts in _dict(day.get("distributors")).items():
        if isinstance(counts, dict):
            clean["distributors"][str(name)] = {key: _int(counts.get(key)) for key in DISTRIBUTOR_EVENTS}
    for name, count in _dict(day.get("apps")).items():
        clean["apps"][str(name)] = _int(count)
    clean["callers"] = _int(day.get("callers"))
    return clean


class UsageStats:
    """Today's and earlier days' counts (the last KEEP_DAYS days). Synchronous, safe for
    single-threaded asyncio."""

    def __init__(self, clock: Callable[[], float] = time.time):
        self._clock = clock
        self.path: Path | None = None
        self.ok = True  # False while writes are failing
        self.tools: set[str] | None = None  # the server's tool names; other names count as "unknown"
        self._days: dict[str, dict[str, Any]] = {}
        self._dirty = False
        self._caller_date = ""
        self._caller_salt = b""
        self._callers: set[bytes] = set()

    def open(self, path: str | Path) -> None:
        """Load the counts kept in path and write them there from now on."""
        self.path = Path(path)
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except (OSError, ValueError) as e:
            logger.warning(f"Usage stats file {self.path} unreadable ({e}); counting starts from 0")
            return
        days = data.get("days") if isinstance(data, dict) else None
        if not isinstance(days, dict):
            logger.warning(f"Usage stats file {self.path} has no days; counting starts from 0")
            return
        self._days = {str(date): _clean_day(day) for date, day in days.items() if isinstance(day, dict)}

    def _today(self) -> str:
        return datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc).date().isoformat()

    def _day(self, date: str | None = None) -> dict[str, Any]:
        """The counts for date (default today), marked as changed."""
        date = date or self._today()
        day = self._days.get(date)
        if day is None:
            day = self._days[date] = _new_day()
            cutoff = (datetime.date.fromisoformat(date) - datetime.timedelta(days=KEEP_DAYS)).isoformat()
            for old in [d for d in self._days if d <= cutoff]:
                del self._days[old]
        self._dirty = True
        return day

    def record_call(self, tool: str, outcome: str, ms: float, caller: str | None = None) -> None:
        """One tool call. outcome: "ok", "error" (it replied with an error), "failed" (it raised,
        e.g. bad arguments) or "empty" (no results). caller is an IP, counted but not kept."""
        if self.tools is not None and tool not in self.tools:
            tool = "unknown"
        date = self._today()
        day = self._day(date)
        counts = day["tools"].setdefault(tool, dict.fromkeys(TOOL_COUNTS, 0))
        counts["calls"] += 1
        key = {"error": "errors", "failed": "failed", "empty": "empty"}.get(outcome)
        if key:
            counts[key] += 1
        counts["ms"] += round(ms)
        if caller:
            self._count_caller(date, day, caller)

    def _count_caller(self, date: str, day: dict[str, Any], caller: str) -> None:
        if date != self._caller_date:
            self._caller_date, self._caller_salt, self._callers = date, secrets.token_bytes(16), set()
        digest = hashlib.blake2b(caller.encode(), key=self._caller_salt, digest_size=8).digest()
        if digest not in self._callers and len(self._callers) < MAX_CALLERS:
            self._callers.add(digest)
            day["callers"] += 1

    def record_app(self, name: str | None) -> None:
        """An MCP app connected (the clientInfo name it sent with initialize)."""
        name = _NOT_IN_APP_NAME.sub("", str(name or "")).strip()[:APP_NAME_LENGTH] or "unknown"
        apps = self._day()["apps"]
        if name not in apps and len(apps) >= MAX_APPS:
            name = "other"
        apps[name] = apps.get(name, 0) + 1

    def record_distributor(self, name: str, event: str) -> None:
        """A Mouser/DigiKey lookup: "sent" to the API, "cached" (answered from the cache) or
        "limited" (turned away by our limits or a pause the API asked for)."""
        counts = self._day()["distributors"].setdefault(name, dict.fromkeys(DISTRIBUTOR_EVENTS, 0))
        counts[event] = counts.get(event, 0) + 1

    def save(self) -> None:
        """Write the counts if anything changed since the last save (atomic replace)."""
        if self.path is None or not self._dirty:
            return
        tmp = self.path.with_name(self.path.name + ".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps({"days": self._days}, sort_keys=True), encoding="utf-8")
            os.replace(tmp, self.path)
        except OSError as e:
            if self.ok:  # once per failure streak
                logger.warning(f"Usage stats file {self.path} not writable ({e}); counts are kept in memory only")
            self.ok = False
            return
        self.ok = True
        self._dirty = False

    def summary(self, days: int = 30) -> dict[str, Any]:
        """For /mcp/stats: the newest `days` days that had any use, newest first."""
        out = []
        for date in sorted(self._days, reverse=True)[:days]:
            day = self._days[date]
            tools = {
                name: {"calls": c["calls"], "errors": c["errors"], "failed": c["failed"], "empty": c["empty"],
                       "avg_ms": round(c["ms"] / c["calls"]) if c["calls"] else 0}
                for name, c in sorted(day["tools"].items(), key=lambda item: (-item[1]["calls"], item[0]))
            }
            out.append({
                "date": date,
                "calls": sum(c["calls"] for c in tools.values()),
                "callers": day["callers"],
                "tools": tools,
                "apps": dict(sorted(day["apps"].items(), key=lambda item: (-item[1], item[0]))),
                "distributors": day["distributors"],
            })
        return {
            "about": ("Anonymous counts per UTC day, the last 30 days at most. callers counts distinct IPs (hosted apps such as claude.ai "
                      "call from shared IPs, and a caller seen before and after a restart counts twice); apps are "
                      "the names MCP apps send when they connect. The stats keep no IPs, queries or part numbers."),
            "kept_across_restarts": self.path is not None and self.ok,
            "days": out,
        }


# The server's counts. Modules use stats.usage (not `from .stats import usage`) so tests can swap it.
usage = UsageStats()
