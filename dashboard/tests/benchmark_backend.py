"""Local, synthetic 365-day benchmark: python tests/benchmark_backend.py.

CPU is measured without tracemalloc; a separate invocation measures peak Python
allocations. The API handler runs without a socket, including JSON and gzip.
"""

import gc
import json
import tempfile
import threading
import time
import tracemalloc
from copy import deepcopy
from datetime import timedelta
from pathlib import Path

import httpx

from pcbparts_dashboard.collector import collect
from pcbparts_dashboard.config import Settings
from pcbparts_dashboard.eastern import persist_eastern_days
from pcbparts_dashboard.server import CollectionRunner, DashboardHandler, DashboardHTTPServer
from pcbparts_dashboard.store import Store, parse_timestamp, timestamp


def api_handler(store, settings, now):
    server = DashboardHTTPServer.__new__(DashboardHTTPServer)
    server.store, server.settings = store, settings
    server.runner = CollectionRunner(settings, store, clock=lambda: now)
    server.polling = True
    server._data_cache = None
    server._data_lock = threading.Lock()
    handler = DashboardHandler.__new__(DashboardHandler)
    handler.server, handler.path = server, "/api/data"
    handler.headers = {"Accept-Encoding": "gzip"}
    handler._send = lambda status, body, *_args: len(body)
    return handler


def seed(store, now):
    fixture = Path(__file__).with_name("fixtures") / "mcp-stats_2026-11-21_1417-EST_sample.json"
    reply = json.loads(fixture.read_text(encoding="utf-8"))
    template = reply["days"][0]
    # Split the busiest app into five apps, preserving every counter total.
    for apps in template["tool_apps"].values():
        counts = apps.pop("app-alpha")
        for i in range(5):
            apps[f"app-alpha-{i}"] = {k: v // 5 + (i < v % 5) for k, v in counts.items()}
    recent = []
    for age in reversed(range(365)):
        moment = now - timedelta(days=age)
        record = deepcopy(template) | {"date": moment.date().isoformat()}
        store.merge_day(record, timestamp(now))
        if age < 3:
            recent.insert(0, record)
        if age < 45:
            for hour in range(1, 24 if age else now.hour + 1):
                def scale(value):
                    if isinstance(value, dict):
                        return {k: scale(v) for k, v in value.items()}
                    if isinstance(value, list):
                        return [scale(v) for v in value]
                    return round(value * hour / 24) if type(value) in (int, float) else value
                sample = scale(record)
                store.add_snapshot(sample, timestamp(moment.replace(hour=hour, minute=0, second=30)))
    store.set_meta("last_success_at", timestamp(now))
    store.set_meta("last_full_fetch_at", timestamp(now))
    store.set_meta("problems_since", timestamp(now - timedelta(days=7)))
    store.set_meta("problems_version", "0.10.5")
    store.set_meta("seen_version", "0.10.5")
    store.save_health({"version": "0.10.5"}, timestamp(now))
    persist_eastern_days(store, now)
    return reply | {"days": recent}, len(json.dumps(template).encode())


def measure(operation):
    gc.collect()
    started = time.process_time()
    operation()
    cpu = time.process_time() - started
    gc.collect()
    tracemalloc.start()
    operation()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"cpu_seconds": round(cpu, 4), "peak_mib": round(peak / 1024 ** 2, 2)}


def main():
    now = parse_timestamp("2026-11-21T19:20:00Z")
    with tempfile.TemporaryDirectory() as directory:
        settings = Settings(project_root=Path(directory), stats_token="synthetic")
        with Store(settings.db_path) as store:
            reply, size = seed(store, now)
            with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
                200, json=reply if request.url.path == "/mcp/stats" else {"version": "0.10.5"}
            ))) as client:
                poll = measure(lambda: collect(settings, store, client=client, now=now))
            api = measure(lambda: api_handler(store, settings, now).do_GET())
            handler = api_handler(store, settings, now)
            handler.do_GET()
            cached_api = measure(handler.do_GET)
            print(json.dumps({"days": 365, "day_bytes": size, "poll": poll,
                              "api_uncached": api, "api_repeated": cached_api}))


if __name__ == "__main__":
    main()
