"""Bounded offloading and connection serialization for the runtime catalogs.

Keep one connection/cache per database. Every operation (including close) holds its
instance's reentrant lock; nested board consensus and lazy initialization use the
same lock. The process-wide pools survive repeated app lifespans in tests. Queued
or cancelled requests cannot create extra threads or connections.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from functools import partial, wraps
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

COMPONENT_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pcbparts-components")
BOARD_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcbparts-boards")
SENSOR_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcbparts-sensors")
RULES_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcbparts-rules")


async def run_db(pool: ThreadPoolExecutor, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Run synchronous catalog work off-loop, preserving request context."""
    call = partial(func, *args, **kwargs)
    return await asyncio.get_running_loop().run_in_executor(pool, copy_context().run, call)


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
