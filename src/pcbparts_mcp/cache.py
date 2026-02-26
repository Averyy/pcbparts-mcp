"""Shared TTL cache with LRU eviction for distributor API clients."""

import datetime
import time
from typing import Any


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


class DailyQuota:
    """Daily request quota counter that resets at UTC midnight.

    Synchronous — safe for single-threaded asyncio (no lock needed).
    """

    def __init__(self, name: str, daily_limit: int):
        self._name = name
        self._limit = daily_limit
        self._count = 0
        self._date = datetime.date.today()

    def _maybe_reset(self) -> None:
        today = datetime.date.today()
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
