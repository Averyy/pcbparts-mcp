"""Shared TTL cache with LRU eviction for distributor API clients, plus request budgets."""

import collections
import datetime
import json
import logging
import math
import os
import time
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Named in the distributor limit errors: running your own copy avoids this server's shared limits
SELF_HOSTING_URL = "https://github.com/Averyy/pcbparts-mcp#self-hosting"


class TTLCache:
    """Simple TTL cache with max size enforcement via LRU eviction.

    Thread-safe for single-threaded asyncio (no await between check and set).
    """

    def __init__(self, ttl: float, max_size: int = 5000):
        self._ttl = ttl
        self._max_size = max_size
        self._data: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        """Get a cached value, or None if missing/expired."""
        if key in self._data:
            ts, result = self._data[key]
            if time.time() - ts < self._ttl:
                return result
            del self._data[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Cache a value. Evicts expired entries first, then oldest if still over max_size."""
        self._data[key] = (time.time(), value)
        if len(self._data) > self._max_size:
            self._evict()

    def _evict(self) -> None:
        """Remove expired entries, then oldest entries if still over max_size."""
        now = time.time()
        # First pass: remove expired
        expired = [k for k, (ts, _) in self._data.items() if now - ts >= self._ttl]
        for k in expired:
            del self._data[k]
        # Second pass: LRU eviction if still over limit
        if len(self._data) > self._max_size:
            sorted_keys = sorted(self._data.keys(), key=lambda k: self._data[k][0])
            for k in sorted_keys[:len(self._data) - self._max_size]:
                del self._data[k]

    def __len__(self) -> int:
        return len(self._data)


def _utc_today() -> datetime.date:
    """Current date in UTC (not local time)."""
    return datetime.datetime.now(datetime.timezone.utc).date()


def _utc_text(timestamp: float) -> str:
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _next_utc_midnight(timestamp: float) -> float:
    today = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).date()
    return datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time(),
                                     datetime.timezone.utc).timestamp()


def _header_int(headers: Any, name: str) -> int | None:
    value = headers.get(name)
    return int(value) if isinstance(value, str) and value.strip().isdigit() else None


def _daily_reset(headers: Any, now: float) -> float:
    """When the API's daily limit resets: X-RateLimit-ResetTime (GMT), else Retry-After, else the
    next UTC midnight (DigiKey's reset was 00:00Z on 2026-10-16)."""
    value = headers.get("x-ratelimit-resettime")
    if isinstance(value, str):
        try:
            reset = datetime.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            pass
        else:
            if reset.tzinfo is None:
                reset = reset.replace(tzinfo=datetime.timezone.utc)
            return reset.timestamp()
    retry_after = _header_int(headers, "retry-after")
    if retry_after is not None:
        return now + retry_after
    return _next_utc_midnight(now)


class CallerTally:
    """Requests per caller IP in the current UTC hour, logged as one summary line once the hour is
    over (flush_if_due(), which the server calls every minute) or at shutdown (flush()). Hours
    without requests log nothing. At most max_callers IPs are tracked an hour; the rest count as
    "other"."""

    def __init__(self, name: str, clock: Callable[[], float] = time.time, max_callers: int = 1000, top: int = 5):
        self._name = name
        self._clock = clock
        self._max_callers = max_callers
        self._top = top
        self._hour = self._hour_of(clock())
        self._counts: collections.Counter[str] = collections.Counter()

    @staticmethod
    def _hour_of(timestamp: float) -> int:
        return int(timestamp // 3600) * 3600

    def record(self, caller: str | None) -> None:
        self.flush_if_due()
        key = caller or "unknown"
        if key not in self._counts and len(self._counts) >= self._max_callers:
            key = "other"
        self._counts[key] += 1

    def flush_if_due(self) -> None:
        if self._hour_of(self._clock()) != self._hour:
            self.flush()

    def flush(self) -> None:
        """Log the hour so far (if it had requests) and start a new one."""
        now = self._clock()
        if self._counts:
            start = datetime.datetime.fromtimestamp(self._hour, datetime.timezone.utc)
            end = datetime.datetime.fromtimestamp(min(now, self._hour + 3600), datetime.timezone.utc)
            end_text = "24:00" if end.date() > start.date() else end.strftime("%H:%M")
            top = ", ".join(f"{caller} {count}" for caller, count in self._counts.most_common(self._top))
            logger.info(f"{self._name} requests sent {start:%Y-%m-%d %H:%M}-{end_text} UTC: "
                        f"{sum(self._counts.values())} from {len(self._counts)} IPs; top: {top}")
        self._counts.clear()
        self._hour = self._hour_of(now)


class QuotaStore:
    """JSON file with each DailyQuota's state (today's count, and any pause the API itself asked
    for), so a restart such as a deploy doesn't reset them. Never raises: if the file can't be read
    or written, it logs a warning and the counts live in memory only, as before 0.6.1."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.ok = True  # False while writes are failing
        self._states: dict[str, dict] = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except (OSError, ValueError) as e:
            logger.warning(f"Distributor quota file {self.path} unreadable ({e}); today's counts start from 0")
            return
        if isinstance(data, dict):
            self._states = {name: state for name, state in data.items() if isinstance(state, dict)}
        else:
            logger.warning(f"Distributor quota file {self.path} isn't a JSON object; today's counts start from 0")

    def get(self, name: str) -> dict:
        return dict(self._states.get(name, {}))

    def put(self, name: str, state: dict) -> None:
        self._states[name] = state
        tmp = self.path.with_name(self.path.name + ".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps(self._states, sort_keys=True), encoding="utf-8")
            os.replace(tmp, self.path)  # atomic: a crash leaves the old file or the new one
        except OSError as e:
            if self.ok:  # once per failure streak, not on every request
                logger.warning(f"Distributor quota file {self.path} not writable ({e}); counts are kept in memory only")
            self.ok = False
            return
        self.ok = True


class DailyQuota:
    """Daily request quota counter that resets at UTC midnight.

    With a QuotaStore the count, and any pause the API asked for (pause()), survive restarts;
    without one they're memory only and a restart starts the day from 0.
    Synchronous — safe for single-threaded asyncio (no lock needed).
    """

    def __init__(self, name: str, daily_limit: int, store: QuotaStore | None = None,
                 clock: Callable[[], float] = time.time, per_minute: int | None = None, own_key: str = ""):
        """per_minute: our cap per rolling minute, kept below the API's own. own_key: what a user
        needs to run the server with their own credentials, named in the limit errors."""
        self._name = name
        self._limit = daily_limit
        self._store = store
        self._clock = clock
        self._per_minute = per_minute
        self._minute = SlidingWindowBudget(per_minute, 60, clock) if per_minute else None
        self._own_key = own_key
        self._count = 0
        self._date = self._today()
        self._paused_until = 0.0  # unix time; the API said its own limit is used up until then
        self._pause_reason = ""  # "daily" (until its reset), "burst" (its per-minute limit) or "refused" (403)
        self._api_remaining: int | None = None  # the API's own count of requests left today
        self._api_limit: int | None = None
        self.callers = CallerTally(name, clock)  # who sent them, logged hourly
        if store is not None:
            self._load(store.get(name))
            self._save()  # at startup, so status() shows whether the file is really writable

    def _today(self) -> datetime.date:
        return datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc).date()

    def now(self) -> float:
        return self._clock()

    def _load(self, state: dict) -> None:
        try:
            if state.get("date") == self._date.isoformat():
                self._count = int(state.get("count", 0))
                remaining, limit = state.get("api_remaining"), state.get("api_limit")
                self._api_remaining = None if remaining is None else int(remaining)
                self._api_limit = None if limit is None else int(limit)
            self._paused_until = float(state.get("paused_until", 0))
            self._pause_reason = str(state.get("pause_reason", ""))
        except (TypeError, ValueError):
            logger.warning(f"{self._name} quota state is malformed ({state!r}); today's count starts from 0")
            self._count, self._paused_until, self._pause_reason = 0, 0.0, ""
            self._api_remaining = self._api_limit = None

    def _save(self) -> None:
        if self._store is not None:
            self._store.put(self._name, {
                "date": self._date.isoformat(),
                "count": self._count,
                "paused_until": self._paused_until,
                "pause_reason": self._pause_reason,
                "api_remaining": self._api_remaining,
                "api_limit": self._api_limit,
            })

    def _maybe_reset(self) -> None:
        today = self._today()
        if today != self._date:
            self._count = 0
            self._date = today
            self._api_remaining = self._api_limit = None

    def check(self, caller: str | None = None) -> dict | None:
        """Return None if a request may go out (and count it), else an error dict: our daily
        limit is used up, our per-minute cap is, or the API asked us to pause. Nothing is counted
        or sent until the limit resets. caller (an IP) goes in the hourly log of who sent them."""
        self._maybe_reset()
        paused = self.paused_error()
        if paused:
            return paused
        if self._count >= self._limit:
            return {"error": f"{self._name} daily quota exceeded ({self._limit} requests/day on this shared server). "
                             f"It resets at {_utc_text(_next_utc_midnight(self._clock()))}.{self._advice()}"}
        if self._minute is not None and not self._minute.try_acquire():
            return {"error": f"{self._name} lookups are limited to {self._per_minute} a minute on this shared server. "
                             f"Try again in {math.ceil(self._minute.wait_seconds())} s.{self._advice()}"}
        self._count += 1
        self._save()
        self.callers.record(caller)
        return None

    def _advice(self) -> str:
        if self._own_key:
            return (f" To skip the shared limits, run pcbparts-mcp with your own {self._own_key}: {SELF_HOSTING_URL}."
                    " Meanwhile use jlc_search.")
        return " Meanwhile use jlc_search."

    def paused_error(self) -> dict | None:
        """The error dict to return while the API's own limit is used up, else None."""
        now = self._clock()
        if now >= self._paused_until:
            return None
        if self._pause_reason == "daily":
            limit = f"{self._api_limit} requests/day, counted by {self._name}" if self._api_limit else f"counted by {self._name}"
            return {"error": f"{self._name} daily quota exceeded ({limit}). "
                             f"It resets at {_utc_text(self._paused_until)}.{self._advice()}"}
        wait = math.ceil(self._paused_until - now)
        if self._pause_reason == "refused":
            return {"error": f"{self._name} refused this server's requests (HTTP 403). Try again in {wait} s.{self._advice()}"}
        return {"error": f"{self._name} is limiting requests per minute. Try again in {wait} s.{self._advice()}"}

    def pause(self, until: float, reason: str) -> None:
        """Send nothing until `until` (unix time): the API said its own limit is used up.
        reason is "daily" (until its reset), "burst" (its per-minute limit) or "refused" (403)."""
        if until > self._paused_until:
            self._paused_until, self._pause_reason = until, reason
            self._save()

    def note_response(self, status_code: int, headers: Any, refused_pause: float | None = None) -> None:
        """Follow the API's own limits from a response. DigiKey (and, by one client library's
        account, Mouser) put X-RateLimit-Limit/-Remaining (per day) on responses: record them and
        pause until the reset once none are left. A 429 without that is the per-minute limit:
        pause for Retry-After, else a minute. refused_pause: seconds to pause on a 403 (DigiKey
        suspends an app for 10 minutes for going over its per-second threshold)."""
        remaining = _header_int(headers, "x-ratelimit-remaining")
        if remaining is not None:
            self.note_api_usage(remaining, _header_int(headers, "x-ratelimit-limit"))
        now = self._clock()
        if remaining == 0:
            self.pause(_daily_reset(headers, now), "daily")
        elif status_code == 429:
            self.pause(now + (_header_int(headers, "retry-after") or 60), "burst")
        elif status_code == 403 and refused_pause:
            self.pause(now + refused_pause, "refused")

    def note_api_usage(self, remaining: int, limit: int | None) -> None:
        """Record the API's own count of requests left today (from its response headers)."""
        self._maybe_reset()
        self._api_remaining = remaining
        if limit is not None:
            self._api_limit = limit
        self._save()

    @property
    def remaining(self) -> int:
        self._maybe_reset()
        return max(0, self._limit - self._count)

    def status(self) -> dict[str, Any]:
        """For /health: today's count and our limit, the API's own count of requests left (None
        when it doesn't report one), when a pause ends (None when not paused), and whether the
        counts survive a restart."""
        self._maybe_reset()
        return {
            "used_today": self._count,
            "limit": self._limit,
            "api_remaining": self._api_remaining,
            "paused_until": _utc_text(self._paused_until) if self._clock() < self._paused_until else None,
            "kept_across_restarts": self._store is not None and self._store.ok,
        }


class SlidingWindowBudget:
    """At most ``limit`` requests in any rolling ``window`` seconds.

    Synchronous — safe for single-threaded asyncio (no await between check and record).
    """

    def __init__(self, limit: int, window: float, clock: Callable[[], float] = time.monotonic):
        self._limit = limit
        self._window = window
        self._clock = clock
        self._sent: collections.deque[float] = collections.deque()
        self._next_report = float("-inf")

    def _prune(self, now: float) -> None:
        while self._sent and now - self._sent[0] >= self._window:
            self._sent.popleft()

    def try_acquire(self) -> bool:
        """Record one request and return True, or return False (recording nothing) if over budget."""
        now = self._clock()
        self._prune(now)
        if len(self._sent) >= self._limit:
            return False
        self._sent.append(now)
        return True

    @property
    def used(self) -> int:
        self._prune(self._clock())
        return len(self._sent)

    def wait_seconds(self) -> float:
        """Seconds until a request fits again (0 if one fits now)."""
        now = self._clock()
        self._prune(now)
        if len(self._sent) < self._limit:
            return 0.0
        return self._sent[0] + self._window - now

    def report_due(self) -> bool:
        """True at most once per window, so running out can be logged without flooding the log."""
        now = self._clock()
        if now < self._next_report:
            return False
        self._next_report = now + self._window
        return True


class Cooldown:
    """Escalating pause after a block: ``base`` seconds, doubling per consecutive block, capped at ``cap``.

    A block reported while a pause is already running doesn't escalate it, so concurrent requests
    that were in flight when the block started count once. A success only clears the strike count
    when no pause is running, so a request from before the block that comes back 200 can't reset
    the escalation (the next block still doubles).

    Synchronous — safe for single-threaded asyncio.
    """

    def __init__(self, base: float, cap: float, clock: Callable[[], float] = time.monotonic):
        self._base = base
        self._cap = cap
        self._clock = clock
        self._until = 0.0
        self._strikes = 0

    @property
    def remaining(self) -> float:
        """Seconds left in the current pause (0 when not paused)."""
        return max(0.0, self._until - self._clock())

    @property
    def active(self) -> bool:
        return self.remaining > 0

    def trip(self) -> float:
        """Start a pause (or keep the running one) and return its remaining seconds."""
        if self.active:
            return self.remaining
        self._strikes += 1
        duration = min(self._base * 2 ** (self._strikes - 1), self._cap)
        self._until = self._clock() + duration
        return duration

    def record_success(self) -> None:
        if not self.active:
            self._strikes = 0
