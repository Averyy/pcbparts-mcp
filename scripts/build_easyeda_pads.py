"""Collect EasyEDA footprint pads for land checks into data/easyeda/pads.csv, a committed seed.

jlc_find_alternatives(land_compatible=true) compares footprint pads (src/pcbparts_mcp/land.py).
The server fetches a footprint it doesn't have and keeps it on its volume; this seed gives every
server, self-hosted ones included, the footprints up front, so a land check needs no request.

Run it on your own machine: never on prod or in CI, and not while integration tests or
scripts/build_easyeda_seed.py run (they share your IP's EasyEDA limits). One /api/components request
per footprint, one attempt each, at most one every --interval seconds (default 2). It stops on
EasyEDA's first 403/429 and resumes where it left off on the next run, saving every --save-every
footprints and on exit (Ctrl-C included). See docs/ref-easyeda-api.md, "The pads seed".

Footprints come from components.db's EasyEDA seed (easyeda_footprints: data/easyeda/footprints.csv),
for the chosen categories, most-stocked parts first, so a stopped run already covers the parts
people use most. Build components.db first (scripts/build_database.py).

Usage:
    uv run python scripts/build_easyeda_pads.py                       # connectors: footprints not yet in the seed
    uv run python scripts/build_easyeda_pads.py --refresh-days 90     # also re-fetch rows fetched over 90 days ago
    uv run python scripts/build_easyeda_pads.py --max-requests 200 --interval 3
    uv run python scripts/build_easyeda_pads.py --categories all
"""

import argparse
import asyncio
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Awaitable, Callable
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pcbparts_mcp.client import JLCPCBClient  # noqa: E402
from pcbparts_mcp.config import EASYEDA_SYMBOL_URL  # noqa: E402
from pcbparts_mcp.easyeda_store import (  # noqa: E402
    PADS_SEED_FILE, PadsRow, format_checked, pack_pads, read_pads_csv, seed_checked_at, write_pads_csv,
)
from pcbparts_mcp.pinout import parse_easyeda_footprint  # noqa: E402

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_CATEGORIES = ("Connectors",)
# When each footprint was last confirmed unchanged (not committed: .gitignore), so --refresh-days
# skips footprints a recent refresh already checked while the CSV keeps their first-fetched dates.
STATE_NAME = "pads_state.json"


def load_state(path: Path) -> dict[str, str]:
    try:
        confirmed = json.loads(path.read_text(encoding="utf-8")).get("confirmed", {})
        return {k: v for k, v in confirmed.items() if isinstance(k, str) and isinstance(v, str)}
    except (OSError, ValueError, AttributeError):
        return {}


def save_state(path: Path, confirmed: dict[str, str]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps({"confirmed": confirmed}, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


class Blocked(Exception):
    """EasyEDA refused a request (403/429): stop and resume later."""


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%SZ")


def footprints_todo(conn: sqlite3.Connection, categories: tuple[str, ...] | None, have: dict[str, PadsRow],
                    refresh_days: float | None, now: float, confirmed: dict[str, str] | None = None) -> list[str]:
    """Footprint UUIDs to fetch, most-stocked part first: those not in the seed, plus (with
    refresh_days) those last fetched or confirmed longer ago than that."""
    where = "e.footprint_uuid IS NOT NULL AND e.footprint_uuid != ''"
    params: list[str] = []
    if categories:
        where += f" AND k.name IN ({','.join('?' for _ in categories)})"
        params += categories
    rows = conn.execute(
        "SELECT e.footprint_uuid, MAX(c.stock) AS stock FROM components c "
        "JOIN subcategories s ON s.id = c.subcategory_id JOIN categories k ON k.id = s.category_id "
        f"JOIN easyeda_footprints e ON e.lcsc = c.lcsc WHERE {where} "
        "GROUP BY e.footprint_uuid ORDER BY stock DESC, e.footprint_uuid",
        params,
    ).fetchall()
    todo = []
    confirmed = confirmed or {}
    for uuid, _ in rows:
        row = have.get(uuid)
        if row is None:
            todo.append(uuid)
        elif refresh_days is not None:
            last = max(seed_checked_at(row.fetched), seed_checked_at(confirmed[uuid]) if uuid in confirmed else 0)
            if now - last >= refresh_days * 86400:
                todo.append(uuid)
    return todo


async def fetch_pads(session, uuid: str) -> str | None:
    """Packed pads for a footprint ("[]" when EasyEDA has none), or None if the request failed.
    Raises Blocked on a 403/429."""
    try:
        response = await session.get(EASYEDA_SYMBOL_URL.format(uuid=quote(uuid, safe="")))
    except Exception as e:
        print(f"{stamp()} {uuid}: request failed ({type(e).__name__}: {e})", flush=True)
        return None
    if response.status_code in (403, 429):
        raise Blocked(f"HTTP {response.status_code} for {uuid}")
    data = response.json() if response.status_code == 200 else None
    if response.status_code == 404 or (isinstance(data, dict) and data.get("code") == 404):
        return "[]"
    if response.status_code != 200 or not isinstance(data, dict) or not data.get("success"):
        print(f"{stamp()} {uuid}: unexpected reply (HTTP {response.status_code})", flush=True)
        return None
    footprint = parse_easyeda_footprint(data.get("result") or {})
    return pack_pads(footprint["pads"] if footprint else [])


async def collect(session, todo: list[str], have: dict[str, PadsRow], out: Path, *, interval: float,
                  max_requests: int | None, save_every: int, confirmed: dict[str, str] | None = None,
                  state_path: Path | None = None,
                  sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
                  clock: Callable[[], float] = time.monotonic, wall: Callable[[], float] = time.time) -> dict:
    """Fetch each footprint in todo into have, saving to out as it goes. Returns counts; "blocked"
    is True when EasyEDA refused a request (everything before it is saved)."""
    counts = {"requests": 0, "added": 0, "changed": 0, "unchanged": 0, "no_pads": 0, "failed": 0, "blocked": False}
    last_start: float | None = None
    since_save = 0
    confirmed = {} if confirmed is None else confirmed
    try:
        for uuid in todo:
            if max_requests is not None and counts["requests"] >= max_requests:
                break
            if last_start is not None:
                wait = interval - (clock() - last_start)
                if wait > 0:
                    await sleep(wait)
            last_start = clock()
            counts["requests"] += 1
            try:
                packed = await fetch_pads(session, uuid)
            except Blocked as e:
                counts["blocked"] = True
                print(f"{stamp()} EasyEDA refused a request ({e}); stopping. Run again later to resume.", flush=True)
                break
            if packed is None:
                counts["failed"] += 1
                continue
            old = have.get(uuid)
            confirmed[uuid] = format_checked(wall())
            if old is not None and old.pads == packed:
                counts["unchanged"] += 1  # keep its fetched date: a refresh rewrites only changed rows
                continue
            counts["changed" if old is not None else "added"] += 1
            counts["no_pads"] += packed == "[]"
            have[uuid] = PadsRow(uuid, packed, format_checked(wall()))
            since_save += 1
            if since_save >= save_every:
                write_pads_csv(out, have.values())
                since_save = 0
            if counts["requests"] % 100 == 0:
                print(f"{stamp()} {counts['requests']:,}/{len(todo):,} requests: {counts['added']:,} added, "
                      f"{counts['changed']:,} changed, {counts['failed']:,} failed", flush=True)
    finally:
        if since_save:
            write_pads_csv(out, have.values())
        if state_path is not None and counts["requests"]:
            save_state(state_path, confirmed)
    return counts


async def main_async(args: argparse.Namespace) -> int:
    out = Path(args.out)
    have = read_pads_csv(out) if out.exists() else {}
    state_path = out.with_name(STATE_NAME)
    confirmed = load_state(state_path)
    db = sqlite3.connect(Path(args.db).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        categories = None if args.categories == "all" else tuple(c.strip() for c in args.categories.split(","))
        todo = footprints_todo(db, categories, have, args.refresh_days, time.time(), confirmed)
    finally:
        db.close()
    print(f"{stamp()} {len(have):,} footprints in {out}; {len(todo):,} to fetch "
          f"(about {len(todo) * args.interval / 3600:.1f} h at one per {args.interval:g}s)", flush=True)
    if not todo:
        return 0
    client = JLCPCBClient()  # no store or seed: only its one-attempt land session is used
    try:
        counts = await collect(client._get_easyeda_land_session(), todo, have, out, interval=args.interval,
                               max_requests=args.max_requests, save_every=args.save_every,
                               confirmed=confirmed, state_path=state_path)
    finally:
        await client.close()
    print(f"{stamp()} done: {counts}; {len(have):,} footprints in {out}", flush=True)
    return 2 if counts["blocked"] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--db", default=str(DATA_DIR / "components.db"), help="components.db to read footprints from")
    parser.add_argument("--out", default=str(DATA_DIR / PADS_SEED_FILE), help="pads seed CSV to update")
    parser.add_argument("--categories", default=",".join(DEFAULT_CATEGORIES),
                        help='comma-separated category names, or "all" (default: Connectors)')
    parser.add_argument("--interval", type=float, default=2.0, help="seconds between requests (default 2)")
    parser.add_argument("--max-requests", type=int, default=None, help="stop after this many requests")
    parser.add_argument("--refresh-days", type=float, default=None,
                        help="also re-fetch footprints fetched at least this many days ago")
    parser.add_argument("--save-every", type=int, default=200, help="save after this many new or changed rows")
    args = parser.parse_args(argv)
    if args.interval < 1:
        parser.error("--interval must be at least 1 second")
    try:
        return asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print(f"{stamp()} interrupted; progress up to the last save is kept", flush=True)
        return 130


if __name__ == "__main__":
    sys.exit(main())
