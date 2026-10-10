"""Shared TTL cache with LRU eviction for distributor API clients, plus request budgets."""

import collections
import datetime
import time
from typing import Any, Callable


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


class DailyQuota:
    """Daily request quota counter that resets at UTC midnight.

    Synchronous — safe for single-threaded asyncio (no lock needed).
    """

    def __init__(self, name: str, daily_limit: int):
        self._name = name
        self._limit = daily_limit
        self._count = 0
        self._date = _utc_today()

    def _maybe_reset(self) -> None:
        today = _utc_today()
        if today != self._date:
            self._count = 0
            self._date = today

    def check(self) -> dict | None:
        """Increment counter and return error dict if over limit, else None."""
        self._maybe_reset()
        self._count += 1
        if self._count > self._limit:
            return {
                "error": f"{self._name} daily quota exceeded ({self._limit} requests/day). Try again tomorrow or use jlc_search instead.",
            }
        return None

    @property
    def remaining(self) -> int:
        self._maybe_reset()
        return max(0, self._limit - self._count)


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
