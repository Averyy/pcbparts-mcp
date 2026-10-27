"""Anonymous usage counts per UTC day, served at /mcp/stats.

Per day: calls to each tool, split by outcome (see OUTCOMES), with the average time; calls in each UTC
hour; the MCP apps that connected (by the name each app reports when it connects), the number of distinct
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
# Each tool call counts under exactly one outcome, so a tool's outcomes add up to its calls:
# ok (found something), similar_only (manual comparison candidates, no verified alternatives),
# not_found (worked, found nothing), bad_request (the request was invalid),
# rate_limited (a limit turned it away) and failed (something broke here or in a service we call)
OUTCOMES = ("ok", "similar_only", "not_found", "bad_request", "rate_limited", "failed")
TOOL_COUNTS = ("calls", *OUTCOMES, "ms")
DISTRIBUTOR_EVENTS = ("sent", "cached", "rate_limited")


def _new_day() -> dict[str, Any]:
    return {"tools": {}, "hours": [0] * 24, "apps": {}, "callers": 0, "distributors": {}}


def _int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0


def _dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _clean_day(day: dict) -> dict[str, Any]:
    """A day read from the file, with anything malformed dropped, so counting can't fail on it."""
    clean = _new_day()
    for name, counts in _dict(day.get("tools")).items():
        if isinstance(counts, dict):
            clean["tools"][str(name)] = _clean_tool_counts(counts)
    for name, counts in _dict(day.get("distributors")).items():
        if isinstance(counts, dict):
            counts = {"rate_limited": counts.get("limited"), **counts}  # 0.6.3 called it "limited"
            clean["distributors"][str(name)] = {key: _int(counts.get(key)) for key in DISTRIBUTOR_EVENTS}
    for name, count in _dict(day.get("apps")).items():
        clean["apps"][str(name)] = _int(count)
    clean["callers"] = _int(day.get("callers"))
    hours = day.get("hours")
    # None: not recorded (0.6.3 had no hours), so record_call() marks the hours before it as unknown
    clean["hours"] = ([None if h is None else _int(h) for h in hours]
                      if isinstance(hours, list) and len(hours) == 24 else None)
    return clean


def _clean_tool_counts(counts: dict) -> dict[str, int]:
    if "errors" in counts or "empty" in counts:
        # 0.6.3's columns: errors (any error reply), failed (raised: so far bad arguments) and empty.
        # Error replies can't be sorted after the fact, so they stay as "unsorted".
        calls, errors, raised, empty = (_int(counts.get(key)) for key in ("calls", "errors", "failed", "empty"))
        return {"calls": calls, "ok": max(0, calls - errors - raised - empty), "similar_only": 0, "not_found": empty,
                "bad_request": raised, "rate_limited": 0, "failed": 0, "ms": _int(counts.get("ms")), "unsorted": errors}
    clean = {key: _int(counts.get(key)) for key in TOOL_COUNTS}
    if "unsorted" in counts:
        clean["unsorted"] = _int(counts["unsorted"])
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
        """One tool call. outcome is one of OUTCOMES (anything else counts as "failed"). caller is
        an IP, counted but not kept."""
        if self.tools is not None and tool not in self.tools:
            tool = "unknown"
        now = datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc)  # one reading for date and hour
        date, hour = now.date().isoformat(), now.hour
        day = self._day(date)
        counts = day["tools"].setdefault(tool, dict.fromkeys(TOOL_COUNTS, 0))
        counts["calls"] += 1
        counts[outcome if outcome in OUTCOMES else "failed"] += 1
        counts["ms"] += round(ms)
        if day["hours"] is None:  # a day saved without hours: the ones before now are unknown
            day["hours"] = [None] * hour + [0] * (24 - hour)
        day["hours"][hour] = (day["hours"][hour] or 0) + 1
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
        "rate_limited" (turned away by our limits or a pause the API asked for)."""
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
        """For /mcp/stats: totals over the newest `days` days that had any use, then each of those
        days, newest first."""
        dates = sorted(self._days, reverse=True)[:days]
        out = []
        total_tools: dict[str, dict[str, int]] = {}
        total_apps: dict[str, int] = {}
        total_distributors: dict[str, dict[str, int]] = {}
        total_hours = [0] * 24
        for date in dates:
            day = self._days[date]
            for hour, count in enumerate(day["hours"] or ()):
                total_hours[hour] += count or 0
            for name, c in day["tools"].items():
                total = total_tools.setdefault(name, {})
                for key, value in c.items():
                    total[key] = total.get(key, 0) + value
            for name, count in day["apps"].items():
                total_apps[name] = total_apps.get(name, 0) + count
            for name, c in day["distributors"].items():
                total = total_distributors.setdefault(name, dict.fromkeys(DISTRIBUTOR_EVENTS, 0))
                for key in DISTRIBUTOR_EVENTS:
                    total[key] += c.get(key, 0)
            tools = _tools_view(day["tools"])
            out.append({
                "date": date,
                "calls": sum(c["calls"] for c in tools.values()),
                "hours": day["hours"],
                "callers": day["callers"],
                "tools": tools,
                "apps": _by_count(day["apps"]),
                "distributors": day["distributors"],
            })
        totals_tools = _tools_view(total_tools)
        return {
            "about": ("Anonymous counts per UTC day, the last 30 days at most, newest first; totals adds up "
                      "the days listed (without callers, which can't be added across days). hours: calls in each UTC hour, "
                      "00 to 23 (null: not recorded); in totals, each hour added up across the days. Each tool's calls = ok (found "
                      "something; for alternatives, verified replacements) + similar_only (only similar parts for manual "
                      "comparison, no verified replacements) + not_found (worked, found nothing) + bad_request (the request was invalid) + "
                      "rate_limited (a limit turned it away) + failed (something broke on this server or a service "
                      "it calls), plus unsorted where shown (error replies from before 0.6.4, which weren't "
                      "sorted). callers counts distinct IPs, which isn't the number of people: hosted apps such "
                      "as claude.ai call from their own servers' IPs, and a caller seen before and after a restart "
                      "counts twice. apps are the names MCP apps send when they connect. The stats keep no IPs, "
                      "queries or part numbers. Cutover 2026-10-26: alternatives replies before that date counted "
                      "similar-parts-only replies as not found; historical counts have not been reclassified."),
            "kept_across_restarts": self.path is not None and self.ok,
            "totals": {
                "from": dates[-1] if dates else None,
                "to": dates[0] if dates else None,
                "days": len(dates),
                "calls": sum(c["calls"] for c in totals_tools.values()),
                "hours": total_hours,
                "tools": totals_tools,
                "apps": _by_count(total_apps),
                "distributors": total_distributors,
            },
            "days": out,
        }


def _tools_view(tools: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    """Tool counts as shown: the outcomes, unsorted when there is any, and the average time; busiest first."""
    return {
        name: {"calls": c["calls"], **{key: c.get(key, 0) for key in OUTCOMES},
               **({"unsorted": c["unsorted"]} if c.get("unsorted") else {}),
               "avg_ms": round(c["ms"] / c["calls"]) if c["calls"] else 0}
        for name, c in sorted(tools.items(), key=lambda item: (-item[1]["calls"], item[0]))
    }


def _by_count(counts: dict[str, int]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


# The server's counts. Modules use stats.usage (not `from .stats import usage`) so tests can swap it.
usage = UsageStats()
