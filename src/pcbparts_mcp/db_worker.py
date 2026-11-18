"""Bounded offloading and connection serialization for the runtime catalogs.

Keep one connection/cache per database. Every operation (including close) holds its
instance's reentrant lock; nested board consensus and lazy initialization use the
same lock. The process-wide pools survive repeated app lifespans in tests. Queued
or cancelled requests cannot create extra threads or connections.
"""

import asyncio
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from functools import partial, wraps
from typing import Any, Callable, NamedTuple, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

COMPONENT_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pcbparts-components")
BOARD_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcbparts-boards")
SENSOR_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcbparts-sensors")
RULES_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcbparts-rules")


class PoolPressure(NamedTuple):
    waiting: int
    oldest_wait: float  # seconds, on a monotonic clock


class DatabasePressure:
    """Only jobs waiting to START database work, per pool; running jobs and network waits aren't
    counted. One short lock protects updates from the event loop and worker threads. Ordered
    dictionaries make the oldest wait O(1), without inspecting executor internals."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._lock = threading.Lock()
        self._waiting: dict[ThreadPoolExecutor, dict[object, float]] = {}

    def enqueue(self, pool: ThreadPoolExecutor) -> object:
        token = object()
        with self._lock:
            self._waiting.setdefault(pool, {})[token] = self._clock()
        return token

    def discard(self, pool: ThreadPoolExecutor, token: object) -> None:
        """A job started, was cancelled before starting, or couldn't be submitted."""
        with self._lock:
            waiting = self._waiting.get(pool)
            if waiting is not None:
                waiting.pop(token, None)
                if not waiting:
                    del self._waiting[pool]

    def snapshot(self) -> dict[ThreadPoolExecutor, PoolPressure]:
        with self._lock:
            now = self._clock()
            return {pool: PoolPressure(len(waiting), max(0.0, now - next(iter(waiting.values()))))
                    for pool, waiting in self._waiting.items()}

    def retry_after(self, max_waiting: int, max_wait: float) -> int:
        """0 when healthy; otherwise a short 2-5s backoff, allowing max_wait per queued job.
        This is a retry hint, not a promise that a running query will finish by then."""
        return max((min(5, max(2, math.ceil(p.oldest_wait + p.waiting * max_wait)))
                    for p in self.snapshot().values()
                    if p.waiting >= max_waiting or p.oldest_wait >= max_wait), default=0)


database_pressure = DatabasePressure()


async def run_db(pool: ThreadPoolExecutor, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Run synchronous catalog work off-loop, preserving request context."""
    call = partial(func, *args, **kwargs)
    pressure = database_pressure
    token = pressure.enqueue(pool)

    def invoke():
        pressure.discard(pool, token)
        return call()

    try:
        future = pool.submit(copy_context().run, invoke)
    except BaseException:
        pressure.discard(pool, token)
        raise
    # Also discard cancelled jobs that never reach invoke(). A cancelled caller must not leave
    # phantom pressure behind; a running query still holds its existing worker/connection.
    future.add_done_callback(lambda _: pressure.discard(pool, token))
    return await asyncio.wrap_future(future)


def offload(pool: ThreadPoolExecutor) -> Callable[[Callable[P, T]], Callable[P, Any]]:
    """Keep a synchronous tool's signature/docstring while making its handler async."""
    def decorate(func: Callable[P, T]) -> Callable[P, Any]:
        @wraps(func)
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            return await run_db(pool, func, *args, **kwargs)
        return wrapped
    return decorate


def serialized(func: Callable[P, T]) -> Callable[P, T]:
    """Protect the entire operation, including cursor consumption and cache updates."""
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        with self._conn_lock:
            return func(self, *args, **kwargs)
    return wrapped
