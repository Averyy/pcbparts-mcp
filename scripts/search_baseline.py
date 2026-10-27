#!/usr/bin/env python3
"""Snapshot local MCP calls and review changes against a frozen components DB.

Run with .venv/bin/python scripts/search_baseline.py snapshot --db
 data/baseline/components.frozen.db --out data/baseline/main.json
Then: .venv/bin/python scripts/search_baseline.py diff BEFORE.json AFTER.json

The query set is tests/baseline/queries.jsonl. Sensor/board databases and design
rules come from this checkout; keep those unchanged between snapshots too.
Network access is blocked, including native wafer sessions. A blocked attempt
aborts the snapshot even if the server catches the resulting exception.
The CLI fixes PYTHONHASHSEED so set-based search-help examples are repeatable;
it preserves the server's returned order, including ranked result lists.
"""

import argparse
import asyncio
from collections import defaultdict
from contextlib import ExitStack, contextmanager
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ROOT / "tests" / "baseline" / "queries.jsonl"
# Keep filter lists intact; only shorten returned shortlists / board detail lists.
RESULT_LISTS = (
    "results", "alternatives", "similar_parts", "unverified_alternatives", "matched_files", "components",
    "neighborhoods", "available_ics", "focus_alternatives",
)


@contextmanager
def offline():
    """Block both Python networking and wafer's native HTTP transport."""
    import httpx
    import wafer

    attempts = []

    def blocked(*args, **kwargs):
        message = "Network access forbidden in search baseline"
        attempts.append(message)
        raise RuntimeError(message)

    with ExitStack() as stack:
        stack.enter_context(patch.object(wafer, "AsyncSession", blocked))
        stack.enter_context(patch.object(httpx.AsyncClient, "send", blocked))
        stack.enter_context(patch.object(httpx.Client, "send", blocked))
        for name in ("connect", "connect_ex", "sendto", "sendmsg"):
            if hasattr(socket.socket, name):
                stack.enter_context(patch.object(socket.socket, name, blocked))
        stack.enter_context(patch.object(socket, "getaddrinfo", blocked))
        try:
            yield attempts
        finally:
            if attempts:
                raise RuntimeError(f"{attempts[0]}; snapshot aborted ({len(attempts)} attempts)")


def summarize_response(response):
    """Retain response metadata and specs, plus ten entries and count per list."""
    result = dict(response)
    for key in RESULT_LISTS:
        if isinstance(result.get(key), list):
            result[f"{key}_count"] = len(result[key])
            result[key] = result[key][:10]
    return result


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


@contextmanager
def local_alternatives(client, database):
    """Exercise the real alternatives pipeline with frozen DB details/search, never live APIs."""
    async def get_part(lcsc):
        return database.get_by_lcsc(lcsc)

    async def search(**kwargs):
        kwargs["sort_by"] = "stock"
        kwargs["prefer_no_fee"] = False
        return database.search(**kwargs)

    with patch.object(client, "get_part", get_part), patch.object(client, "search", search):
        yield


async def snapshot(db_path):
    # Patch the module default used by get_db(); no production code changes.
    from fastmcp import Client
    from pcbparts_mcp import boards_db, db, sensor_db, server

    sources = {
        "components": db_path.resolve(),
        "boards": ROOT / "data" / "boards.db",
        "sensors": ROOT / "data" / "sensor.db",
    }
    for path in sources.values():
        if not path.is_file():
            raise FileNotFoundError(f"Required baseline database missing: {path}")
    queries = [json.loads(line) for line in QUERIES.read_text(encoding="utf-8").splitlines()]
    result = {
        "format_version": 1,
        "sources_sha256": {name: file_hash(path) for name, path in sources.items()},
        "queries_sha256": file_hash(QUERIES),
        "calls": [],
    }
    db.close_db()
    boards_db.close_boards_db()
    sensor_db.close_sensor_db()
    with ExitStack() as stack:
        stack.enter_context(offline())
        for module, name in ((db, "components"), (boards_db, "boards"), (sensor_db, "sensors")):
            stack.enter_context(patch.object(module, "DEFAULT_DB_PATH", sources[name]))
        # Ignore shell credentials and persistent service stores.
        for name in (
            "EASYEDA_STORE_PATH", "CSE_STORE_PATH", "DISTRIBUTOR_QUOTA_PATH",
            "USAGE_STATS_PATH", "MOUSER_API_KEY", "DIGIKEY_CLIENT_ID", "DIGIKEY_CLIENT_SECRET",
        ):
            stack.enter_context(patch.object(server, name, ""))
        async with Client(server.mcp) as client:
            for index, query in enumerate(queries, 1):
                with ExitStack() as call_stack:
                    if query["tool"] == "jlc_find_alternatives":
                        call_stack.enter_context(local_alternatives(server._client, db.get_db()))
                    reply = await client.call_tool(query["tool"], query["args"], raise_on_error=False)
                response = reply.structured_content
                if response is None:
                    response = {"error" if reply.is_error else "content": [
                        block.text for block in reply.content if hasattr(block, "text")
                    ]}
                result["calls"].append({
                    **query, "response": summarize_response(response), "is_error": reply.is_error,
                })
                if index % 25 == 0:
                    print(f"Completed {index}/{len(queries)} calls", flush=True)
    return result


def index_calls(snapshot):
    """Identify duplicate calls by occurrence, without depending on line numbers."""
    counts = defaultdict(int)
    indexed = {}
    for call in snapshot["calls"]:
        identity = json.dumps([call["tool"], call["args"]], sort_keys=True)
        counts[identity] += 1
        indexed[(identity, counts[identity])] = call
    return indexed


def short(value):
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return text if len(text) <= 160 else text[:157] + "..."


def value_changes(old, new, path=""):
    """Report the differing leaf, even when only the tenth result changed."""
    if type(old) is type(new) and isinstance(old, dict):
        for key in sorted(old.keys() | new.keys()):
            child = f"{path}.{key}" if path else key
            if key not in old:
                yield f"{child}: <absent> -> {short(new[key])}"
            elif key not in new:
                yield f"{child}: {short(old[key])} -> <absent>"
            else:
                yield from value_changes(old[key], new[key], child)
    elif isinstance(old, list) and isinstance(new, list):
        if len(old) != len(new):
            yield f"{path} length: {len(old)} -> {len(new)}"
        for index, (previous, current) in enumerate(zip(old, new)):
            yield from value_changes(previous, current, f"{path}[{index}]")
    elif old != new or type(old) is not type(new):
        yield f"{path}: {short(old)} -> {short(new)}"


def describe_change(before, after):
    if before is None:
        return "call added"
    if after is None:
        return "call removed"
    changes = list(value_changes(before["response"], after["response"]))
    if before.get("is_error") != after.get("is_error"):
        changes.append(f"is_error: {before.get('is_error')} -> {after.get('is_error')}")
    summary = "; ".join(changes[:8])
    if len(changes) > 8:
        summary += f"; {len(changes) - 8} more changed fields"
    return summary


def diff_snapshots(before, after):
    """Print changed calls grouped by their expected bug item; always succeed."""
    old, new = index_calls(before), index_calls(after)
    groups = defaultdict(list)
    for identity in dict.fromkeys([*old, *new]):
        previous, current = old.get(identity), new.get(identity)
        description = describe_change(previous, current)
        if not description:
            continue
        call = current or previous
        tag = call.get("expect_change") or (previous or {}).get("expect_change")
        group = f"expected for item {tag}" if tag else "untagged (possible regression)"
        groups[group].append(f"{call['tool']} {short(call['args'])}: {description}")
    for key in ("sources_sha256", "queries_sha256", "format_version"):
        if before.get(key) != after.get(key):
            print(f"Snapshot metadata changed ({key}); check inputs before interpreting changes")
    for group, changes in sorted(groups.items()):
        print(f"\n{group} ({len(changes)} changed calls):")
        for change in changes:
            print(f"  {change}")
    changed = sum(map(len, groups.values()))
    untagged = len(groups.get("untagged (possible regression)", []))
    print(f"\n{changed} changed calls: {changed - untagged} expected, {untagged} untagged "
          f"({len(old)} before, {len(new)} after)")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture = commands.add_parser("snapshot", help="Run all baseline calls offline")
    capture.add_argument("--db", type=Path, required=True)
    capture.add_argument("--out", type=Path, required=True)
    compare = commands.add_parser("diff", help="Explain changed calls (always exits 0)")
    compare.add_argument("before", type=Path)
    compare.add_argument("after", type=Path)
    args = parser.parse_args()
    if args.command == "diff":
        return diff_snapshots(json.loads(args.before.read_text(encoding="utf-8")),
                              json.loads(args.after.read_text(encoding="utf-8")))
    if os.environ.get("PYTHONHASHSEED") != "0":
        # Hash randomization is chosen at interpreter startup, not at assignment.
        os.execve(sys.executable, [sys.executable, *sys.argv],
                  {**os.environ, "PYTHONHASHSEED": "0"})
    start = time.monotonic()
    result = asyncio.run(snapshot(args.db))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"Saved {len(result['calls'])} calls to {args.out} in {time.monotonic() - start:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
