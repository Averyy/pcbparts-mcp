"""Bounded offloading for the runtime catalogs, and how long their jobs wait and run.

Component reads (ComponentDatabase) run up to COMPONENT_POOL's 3 at once, each worker thread on
its own read connection, with no lock held while a query runs. The other catalogs (stock history,
sensors, boards) keep one connection each: every operation (including close) holds its instance's
reentrant lock (@serialized), and nested board consensus and lazy initialization use the same lock.
The process-wide pools survive repeated app lifespans in tests. Queued or cancelled requests cannot
create extra threads or connections.
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from functools import partial, wraps
from typing import Any, Callable, NamedTuple, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

COMPONENT_POOL = ThreadPoolExecutor(max_workers=3, thread_name_prefix="pcbparts-components")
BOARD_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcbparts-boards")
SENSOR_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcbparts-sensors")
RULES_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcbparts-rules")


class PoolPressure(NamedTuple):
    waiting: int
    oldest_wait: float  # seconds, on a monotonic clock


class PoolRunning(NamedTuple):
    running: int
    longest: float  # seconds the longest-running job has run, on a monotonic clock


class DatabasePressure:
    """Per pool, the jobs waiting to START database work and the jobs running it (network waits
    aren't counted: they never go through run_db). One short lock protects updates from the event
    loop and worker threads. Ordered dictionaries make the oldest wait and the longest run O(1),
    without inspecting executor internals. For /health (database_pressure, 503 when stuck) and the
    stuck-worker exit (server._exit_if_stuck, on waiting jobs only); nothing refuses, caps or times
    out calls on it."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._lock = threading.Lock()
        self._waiting: dict[ThreadPoolExecutor, dict[object, float]] = {}
        self._running: dict[ThreadPoolExecutor, dict[object, float]] = {}  # token: when it started
        self._last_start: dict[ThreadPoolExecutor, float] = {}  # when each pool last started a job

    def enqueue(self, pool: ThreadPoolExecutor) -> object:
        token = object()
        with self._lock:
            self._waiting.setdefault(pool, {})[token] = self._clock()
        return token

    def started(self, pool: ThreadPoolExecutor, token: object) -> None:
        """A worker took this job: the pool's queue is moving, and the job runs until discard()."""
        with self._lock:
            now = self._last_start[pool] = self._clock()
            self._remove(self._waiting, pool, token)
            self._running.setdefault(pool, {})[token] = now

    def discard(self, pool: ThreadPoolExecutor, token: object) -> None:
        """A job is gone: it finished, was cancelled before starting, or couldn't be submitted."""
        with self._lock:
            self._remove(self._waiting, pool, token)
            self._remove(self._running, pool, token)

    @staticmethod
    def _remove(jobs: dict[ThreadPoolExecutor, dict[object, float]], pool: ThreadPoolExecutor, token: object) -> None:
        tokens = jobs.get(pool)
        if tokens is not None:
            tokens.pop(token, None)
            if not tokens:
                del jobs[pool]

    def snapshot(self) -> dict[ThreadPoolExecutor, PoolPressure]:
        """Pools with jobs waiting to start: how many, and the longest any has waited."""
        with self._lock:
            now = self._clock()
            return {pool: PoolPressure(len(waiting), max(0.0, now - next(iter(waiting.values()))))
                    for pool, waiting in self._waiting.items()}

    def running(self) -> dict[ThreadPoolExecutor, PoolRunning]:
        """Pools with jobs running: how many, and how long the longest has run."""
        with self._lock:
            now = self._clock()
            return {pool: PoolRunning(len(running), max(0.0, now - next(iter(running.values()))))
                    for pool, running in self._running.items()}

    def stalled_seconds(self) -> float:
        """How long the most stalled pool has had jobs waiting without starting any: since its
        last start, or since its oldest waiting job was queued if that is later. 0 with nothing
        waiting. A long queue that keeps moving (overload) stays near 0; a stuck worker doesn't."""
        with self._lock:
            now = self._clock()
            return max((max(0.0, now - max(next(iter(waiting.values())), self._last_start.get(pool, float("-inf"))))
                        for pool, waiting in self._waiting.items()), default=0.0)

    def summary(self) -> dict[str, int | float]:
        """For /health: jobs waiting to start in all pools, the longest any has waited, how long
        the most stalled pool has started none, the jobs running and the longest any has run
        (seconds)."""
        pools = self.snapshot().values()
        running = self.running().values()
        return {"waiting": sum(p.waiting for p in pools),
                "oldest_wait_seconds": round(max((p.oldest_wait for p in pools), default=0.0), 3),
                "stalled_seconds": round(self.stalled_seconds(), 3),
                "running": sum(r.running for r in running),
                "longest_running_seconds": round(max((r.longest for r in running), default=0.0), 3)}


database_pressure = DatabasePressure()


async def run_db(pool: ThreadPoolExecutor, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Run synchronous catalog work off-loop, preserving request context."""
    call = partial(func, *args, **kwargs)
    pressure = database_pressure
    token = pressure.enqueue(pool)

    def invoke():
        pressure.started(pool, token)
        try:
            return call()
        finally:
            pressure.discard(pool, token)  # no longer running

    try:
        future = pool.submit(copy_context().run, invoke)
    except BaseException:
        pressure.discard(pool, token)
        raise
    # Also discard cancelled jobs that never reach invoke(). A cancelled caller must not leave
    # phantom pressure behind; a running query still holds its worker (and its connection), and
    # counts as running until it returns.
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
    """Protect the entire operation, including cursor consumption and cache updates, with the
    instance's reentrant _conn_lock: for the single-connection catalogs (history, sensors, boards).
    ComponentDatabase uses its own per-thread connections instead (db._reads)."""
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        with self._conn_lock:
            return func(self, *args, **kwargs)
    return wrapped
