"""Private, bounded call rows and deduplicated failed text, separate from aggregate counts.

Recording is synchronous on the event loop, with no file access. open()/flush() do I/O in
workers using detached snapshots; no worker touches the recorder's mutable state. A cancelled
flush finishes before shutdown can start another. Failures never propagate to tool callers.
"""

import asyncio
import datetime as dt
import gzip
import hashlib
import json
import logging
import os
import re
import secrets
import shutil
import sys
import time
import unicodedata
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import Any, Callable

from . import stats
from .config import CALL_LOG_DAYS, CALL_LOG_MAX_ROWS, FAILED_QUERY_CAP, FAILED_QUERY_DAYS, MAX_REQUEST_BODY_BYTES
from .search.mpn import LCSC_CODE
from .tool_outcomes import _error_kind
from .private_files import private_open as _private_open

logger = logging.getLogger(__name__)
_CALL_FILE = re.compile(r"calls-([0-9]{4}-[0-9]{2}-[0-9]{2})\.jsonl(\.gz)?")
_FAILED_FILE = re.compile(r"failed-([0-9]{4}-[0-9]{2}-[0-9]{2})\.json")
_EXCLUDED = {"stock_below_minimum", "offset_past_end", "not_sent", "placeholder_mpn"}
_PRIMARY = {**dict.fromkeys(stats.QUERY_TOOLS, "query"), "jlc_find_alternatives": "lcsc",
            "digikey_get_part": "part_number", "get_design_rules": "topic", "board_get": "slug"}
_LIBRARIES = {"basic", "preferred", "no_fee", "extended", "all"}
WELL_KNOWN_APPS = {name.casefold(): name for name in (
    "codex-mcp-client", "claude-code", "backplane-check", "mcp", "Anthropic/ClaudeAI",
    "claude-ai", "opencode", "antigravity-client", "openai-mcp (Responses API)", "Cursor")}
MAX_TRACKED_APPS = 50
_BATCH_LIMIT = 50
_REJECTED_BATCH = re.compile(r"Too many \w+ \(max \d+, got (\d+)\)")
_MOUSER_PARTS = re.compile(r"[^|\s][^|]*")
BUFFER_BYTES = 8 * 1024 * 1024
WRITE_CHUNK_BYTES = 64 * 1024
_SHAPE_NAME_CHARS = 40
_UNKNOWN_ARG_NAME = re.compile(r"[A-Za-z_]{1,30}")


def _safe_unknown_arg_name(name: str) -> bool:
    return _UNKNOWN_ARG_NAME.fullmatch(name) is not None


def _shape_list(shape: dict, key: str, values: list, cap: int) -> None:
    shape[key] = [value[:_SHAPE_NAME_CHARS] for value in values[:cap]]
    if len(values) > cap:
        shape[key + "_omitted"] = len(values) - cap


def _row_bytes(value: Any) -> int:
    """Conservative resident-size accounting, including containers and shared strings.

    The margin covers list slots and growth of a refusal counter while it is buffered.
    No JSON encoding or file access runs on the recording path.
    """
    size = sys.getsizeof(value) + 32
    if isinstance(value, dict):
        size += sum(_row_bytes(k) + _row_bytes(v) for k, v in value.items())
    elif isinstance(value, list):
        size += sum(_row_bytes(item) for item in value)
    return size


def _items(value: Any) -> list:
    """The tools accept a single entry or a JSON array/object string. Bound parsing work."""
    if isinstance(value, str) and value.lstrip().startswith(("[", "{")):
        if len(value) > MAX_REQUEST_BODY_BYTES:
            return []
        try:
            value = json.loads(value)
        except (ValueError, RecursionError):
            return []
    return value if isinstance(value, list) else [] if value is None else [value]


def _part(item: Any) -> tuple[str | None, str | None]:
    """Input form and original text; an explicit MPN stays an MPN even if code-shaped."""
    if isinstance(item, str):
        text = item.strip()
        return ("lcsc" if LCSC_CODE.fullmatch(text) else "mpn"), text
    if isinstance(item, dict):
        code, mpn, maker = (item.get(key) for key in ("lcsc", "mpn", "manufacturer"))
        if isinstance(code, str) and LCSC_CODE.fullmatch(code.strip()):
            return "lcsc", code
        if isinstance(mpn, str):
            return "mpn", mpn + (" | " + maker if isinstance(maker, str) and maker.strip() else "")
    return None, None


def _batch(value: Any, content: dict, notes: dict, *, rejected: bool = False) -> tuple[list, int]:
    """Keep the total, inspect only a tool-sized prefix, and never reparse a rejected argument."""
    if "batch_count" in notes:
        return notes.get("batch_items", []), notes["batch_count"]
    if isinstance(value, list):
        return value[:_BATCH_LIMIT], len(value)
    if not isinstance(value, str) or not value.lstrip().startswith(("[", "{")):
        items = _items(value)
        return items[:_BATCH_LIMIT], len(items)
    if content.get("error") or rejected:
        match = _REJECTED_BATCH.match(str(content.get("error", "")))
        return [], int(match[1]) if match else 0
    items = _items(value)
    return items[:_BATCH_LIMIT], len(items)


def normalize_text(value: Any) -> str:
    """No control/format characters, collapsed whitespace, casefolded, at most 200 chars."""
    if value is None:
        return ""
    text = "".join(c for c in str(value) if unicodedata.category(c) not in {"Cc", "Cf", "Cs"})
    return " ".join(text.split()).strip().casefold()[:200]


def failed_texts(tool: str, outcome: str, reason: str | None, args: dict, content: dict, notes: dict | None = None):
    """Yield (reason, original text), including misses in otherwise successful batches."""
    if outcome == "bad_request":
        return
    if tool == "mouser_get_part":
        missing = content.get("not_found")
        if isinstance(missing, list):
            not_sent = content.get("not_sent") or {}
            for text in missing[:10]:
                if isinstance(text, str) and not isinstance(not_sent, str) and text not in not_sent:
                    yield "row_not_found", text
        lookup_failed = content.get("lookup_failed")
        if isinstance(lookup_failed, list):
            for text in lookup_failed[:10]:
                if isinstance(text, str):
                    yield "row_lookup_failed", text
        if not isinstance(missing, list) and not isinstance(lookup_failed, list) and outcome == "failed":
            value = args.get("part_number")
            if isinstance(value, str):
                for match in islice(_MOUSER_PARTS.finditer(value), 10):
                    yield reason, match[0]
        return
    if tool in {"jlc_get_parts", "part_lifecycle"}:
        items, _ = _batch(args.get("parts"), content, notes or {})
        rows = content.get("results")
        if isinstance(rows, list):
            for item, row in zip(items, rows):
                if not isinstance(row, dict):
                    continue
                label = None
                if row.get("error"):
                    # Share the actual tool-error classifier, including invalid input exclusions.
                    label = {"not_found": "row_not_found", "failed": "row_failed"}.get(_error_kind(str(row["error"])))
                elif tool == "part_lifecycle" and row.get("lookup_failed") is True:
                    label = "row_lookup_failed"
                elif row.get("not_found") is True:
                    label = "row_not_found"
                if label:
                    yield label, _part(item)[1]
        elif outcome == "failed":
            for item in items[:50]:
                yield reason, _part(item)[1]
        return
    if outcome != "failed" and (outcome != "not_found" or reason in _EXCLUDED):
        return
    if tool == "jlc_get_part":
        text = args.get("lcsc") or args.get("mpn")
    elif tool == "jlc_get_pinout":
        text = args.get("lcsc") or args.get("uuid")
    elif tool == "cse_get_kicad":
        text = None if args.get("part_id") is not None else args.get("query")
    else:
        text = args.get(_PRIMARY.get(tool))
    if text is not None:
        yield reason, text


@dataclass(frozen=True)
class ShapeCatalog:
    """Trusted catalog spellings only. Populated by one background database job."""

    categories: dict[int, str] = field(default_factory=dict)
    subcategories: dict[int, tuple[str, str]] = field(default_factory=dict)
    category_names: dict[str, str] = field(default_factory=dict)
    subcategory_names: dict[str, str] = field(default_factory=dict)
    packages: frozenset[str] = frozenset()
    attributes: frozenset[str] = frozenset()

    def shape(self, tool: str, args: dict, content: dict, notes: dict, params: set[str], *, rejected: bool = False) -> dict:
        shape: dict[str, Any] = {}
        _shape_list(shape, "args", sorted({name if name in params or _safe_unknown_arg_name(name) else "unknown_argument"
                                         for name, value in args.items() if value is not None}), 20)
        if tool in {"jlc_get_parts", "part_lifecycle"}:
            items, shape["batch"] = _batch(args.get("parts"), content, notes, rejected=rejected)
            shape["input"] = {"lcsc": 0, "mpn": 0}
            for item in items:
                form = _part(item)[0]
                if form is not None:
                    shape["input"][form] += 1
        elif tool == "jlc_stock_history":
            _, shape["batch"] = _batch(args.get("lcsc"), content, notes, rejected=rejected)
        elif tool == "mouser_get_part" and isinstance(args.get("part_number"), str):
            value = args["part_number"]
            match = re.search(r"; got (\d+)\.", str(content.get("error", "")))
            shape["batch"] = int(match[1]) if match else sum(1 for _ in islice(_MOUSER_PARTS.finditer(value), 10))
        elif tool == "jlc_get_part":
            if args.get("lcsc") or args.get("mpn"):
                shape["input"] = "lcsc" if args.get("lcsc") else "mpn"
            if type(args.get("live", False)) is bool:
                shape["live"] = args.get("live", False)
            source = content.get("data_source")
            kind = source.get("kind") if isinstance(source, dict) else None
            if isinstance(kind, str) and kind in {"snapshot", "live_lookup"}:
                shape["source"] = kind
            if type(content.get("live_failed")) is bool:
                shape["live_failed"] = content["live_failed"]
        if tool not in {"jlc_search", "jlc_stock_check"}:
            return shape
        filters = content.get("filters_applied") if tool == "jlc_search" else notes.get("stock_shape")
        filters = filters if isinstance(filters, dict) else {}
        for key, names, ids in (("category", self.category_names, self.categories),
                                ("subcategory", self.subcategory_names, self.subcategories)):
            name = filters.get(key + "_resolved") or args.get(key + "_name")
            known = names.get(name.casefold()) if isinstance(name, str) else None
            ident = filters.get(key + "_id", args.get(key + "_id"))
            if type(ident) is int and ident in ids:
                shape[key] = (ids[ident][0] if key == "subcategory" else ids[ident])[:_SHAPE_NAME_CHARS]
            elif known and not ident:
                shape[key] = known[:_SHAPE_NAME_CHARS]
            if key == "subcategory" and type(ident) is int and ident in ids:
                shape.setdefault("category", ids[ident][1][:_SHAPE_NAME_CHARS])
        for key in ("package", "packages"):
            value = filters.get(key, args.get(key))
            if value is not None:
                items = _items(value)
                safe = [v if isinstance(v, str) and v in self.packages else "other" for v in items[:10]]
                if key == "packages":
                    _shape_list(shape, key, safe, 10)
                    if len(items) > 10:
                        shape[key + "_omitted"] = len(items) - 10
                else:
                    shape[key] = safe[0][:_SHAPE_NAME_CHARS] if safe else "other"
        library = filters.get("library_type", args.get("library_type"))
        if isinstance(library, str) and library in _LIBRARIES:
            shape["library_type"] = library
        if tool == "jlc_search":
            specs = filters.get("spec_filters", args.get("spec_filters"))
            if specs is not None:
                items = _items(specs)
                names = [s.get("name") if isinstance(s, dict) else None for s in items[:20]]
                _shape_list(shape, "spec_filters", [n if isinstance(n, str) and n in self.attributes else "other"
                                                   for n in names], 20)
                if len(items) > 20:
                    shape["spec_filters_omitted"] = len(items) - 20
            for key in ("strict", "match_all_terms"):
                value = filters.get(key, args.get(key))
                if type(value) is bool:
                    shape[key] = value
            sort = args.get("sort_by")
            if isinstance(sort, str) and sort in {"stock", "price", "relevance"}:
                shape["sort_by"] = sort
        return shape


def load_catalog(db) -> ShapeCatalog:
    """One background run_db job, no per-call SQL. Attributes in the DB are [name, value] pairs.

    package_spellings contains only translations, the search package map only pin-count families,
    and _attribute_names is lazy, partial and casefolded. None is a complete spelling whitelist;
    until this scan finishes, recording uses the empty catalog's content-free fallbacks.
    """
    db._ensure_db()
    categories = {key: value["name"] for key, value in db._categories.items()}
    subcategories = {key: (value["name"], value["category_name"]) for key, value in db._subcategories.items()}
    packages = frozenset(row[0] for row in db._conn.execute("SELECT DISTINCT package FROM components") if row[0])
    attributes = frozenset(row[0] for row in db._conn.execute(
        "SELECT DISTINCT json_extract(a.value, '$[0]') FROM components c, json_each(c.attributes) a") if row[0])
    return ShapeCatalog(categories, subcategories, {v.casefold(): v for v in categories.values()},
                        {v[0].casefold(): v[0] for v in subcategories.values()}, packages, attributes)


class CallLog:
    def __init__(self, *, clock: Callable[[], float] = time.time, call_days: int = CALL_LOG_DAYS,
                 failed_days: int = FAILED_QUERY_DAYS, failed_cap: int = FAILED_QUERY_CAP, row_cap: int = 20_000,
                 max_rows: int = CALL_LOG_MAX_ROWS, buffer_bytes: int = BUFFER_BYTES):
        self.clock = clock
        self.path: Path | None = None
        self.catalog = ShapeCatalog()
        self.call_days, self.failed_days, self.failed_cap, self.row_cap = call_days, failed_days, failed_cap, row_cap
        self._rows: list[dict] = []
        self._rollbacks: dict[str, int] = {}  # unacknowledged append offsets, repaired before retry
        self._inflight = 0
        self.buffer_bytes = buffer_bytes
        self._buffered_bytes = self._inflight_bytes = 0
        self._prepared = False
        self.dropped_rows = 0
        self._overflow_date = ""
        self.max_rows = max_rows
        self._budget_date = ""
        self._day_rows = self._day_dropped = 0
        self._timestamp_second: int | None = None
        self._timestamp_text = ""
        self._refusal_minute = ""
        self._refusals: dict[tuple[str, bool], dict | None] = {}
        self._app_days: dict[str, tuple[bytes, dict[str, set[bytes]]]] = {}
        self._failed: dict[str, dict[tuple[str, str, str], int]] = {}
        self._dropped: dict[str, int] = {}
        self._changed: dict[str, int] = {}
        self._loaded_dates: set[str] = set()
        self._rotated_date = ""
        self._errors: set[str] = set()
        self._lock = asyncio.Lock()

    def _now(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.clock(), dt.timezone.utc)

    def _error(self, operation: str, error: Exception | str) -> None:
        if operation not in self._errors:
            # No exception messages: they could contain failed query text or arguments.
            logger.warning("Call log: %s failed (%s); will retry", operation,
                           error if isinstance(error, str) else type(error).__name__)
        self._errors.add(operation)

    async def open(self, path: str | Path) -> None:
        self.path = Path(path) if path else None
        self._prepared = False
        if self.path is not None:
            await self.flush()
            logger.info("Call log: kept in %s (rows %d days, failed searches %d days)",
                        self.path, self.call_days, self.failed_days)
        else:
            logger.info("Call log: off (CALL_LOG_DIR unset)")

    def _timestamp(self) -> str:
        second = int(self.clock())
        if second != self._timestamp_second:
            self._timestamp_text = dt.datetime.fromtimestamp(second, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._timestamp_second = second
        return self._timestamp_text

    def _roll_day(self, date: str) -> None:
        if date != self._budget_date:
            if self._day_dropped:
                logger.info("Call log: %s: %d rows dropped", self._budget_date, self._day_dropped)
            self._budget_date, self._day_rows, self._day_dropped = date, 0, 0

    def _track_app(self, date: str, app: str | None, caller: str | None, platform: bool) -> str | None:
        if app is None:
            return None
        # Clean first, as AppsByAddress does for HTTP callers, so both paths agree ("Cur\tsor": Cursor)
        name = " ".join(stats.clean_app_name(app).split())
        if name.casefold() in WELL_KNOWN_APPS:
            return WELL_KNOWN_APPS[name.casefold()]
        name = " ".join(name.casefold().split())
        if date not in self._app_days:
            # Only current/previous-day hashes, even if writes have failed for many days.
            self._app_days[date] = secrets.token_bytes(16), {}
            while len(self._app_days) > 2:
                del self._app_days[min(self._app_days)]
        salt, seen = self._app_days[date]
        key = name
        if key not in seen and len(seen) >= MAX_TRACKED_APPS:
            return "other"
        callers = seen.setdefault(key, set())
        if len(callers) < stats.POPULAR_CALLERS:
            address = stats.popularity_caller(caller, platform=platform)
            if address:
                callers.add(hashlib.blake2b(address.encode("utf-8", "surrogatepass"), key=salt, digest_size=8).digest())
        return name

    def _redact_apps(self, rows: list[dict]) -> None:
        for row in rows:
            name = row.get("app")
            if name is not None and name.casefold() not in WELL_KNOWN_APPS:
                _, seen = self._app_days.get(row["t"][:10], (b"", {}))
                if len(seen.get(name.casefold(), ())) < stats.POPULAR_CALLERS:
                    row["app"] = "other"

    def _append(self, row: dict) -> bool:
        date = row["t"][:10]
        self._roll_day(date)
        size = _row_bytes(row)
        full = (len(self._rows) + self._inflight >= self.row_cap
                or self._buffered_bytes + self._inflight_bytes + size > self.buffer_bytes)
        if full or not self._prepared or self._day_rows >= self.max_rows:
            self.dropped_rows += 1
            self._day_dropped += 1
            if self._overflow_date != date:
                self._overflow_date = date
                logger.warning("Call log: %s on %s; excess rows dropped (cap %d)",
                               "row buffer full" if full else "daily row budget reached", date,
                               self.row_cap if full else self.max_rows)
            return False
        self._rows.append(row)
        self._buffered_bytes += size
        self._day_rows += 1
        return True

    def record(self, tool: str, outcome: str, reason: str | None, bad_request_reason: str | None,
               ms: float, app: str | None, platform: bool, args: dict, content: dict, notes: dict,
               params: set[str], *, caller: str | None = None) -> None:
        if self.path is None:
            return
        try:
            timestamp = self._timestamp()
            date = timestamp[:10]
            self._append({"t": timestamp, "tool": tool, "outcome": outcome,
                          "reason": reason, "bad_request_reason": bad_request_reason, "ms": max(0, round(ms)),
                          "app": self._track_app(date, app, caller, platform), "platform": bool(platform),
                          "shape": self.catalog.shape(tool, args, content, notes, params, rejected=outcome == "bad_request")})
            for label, text in failed_texts(tool, outcome, reason, args, content, notes):
                self._add_failed(date, tool, label or "other", text)
            self._errors.discard("record")
        except Exception as exc:
            self._error("record", exc)

    def refusal(self, reason: str, platform: bool) -> None:
        if self.path is None:
            return
        try:
            if reason in {"per_ip_rate_limit", "too_many_clients"}:
                minute = self._timestamp()[:16] + ":00Z"
                if minute != self._refusal_minute:
                    self._refusal_minute, self._refusals = minute, {}
                key = reason, bool(platform)
                if key not in self._refusals:
                    row = {"t": minute, "refused": reason, "platform": bool(platform), "count": 0}
                    self._refusals[key] = row if self._append(row) else None
                if (row := self._refusals[key]) is not None:
                    row["count"] += 1
            self._errors.discard("refusal")
        except Exception as exc:
            self._error("refusal", exc)

    def _add_failed(self, date: str, tool: str, reason: str, value: Any, count: int = 1) -> None:
        text = normalize_text(value)
        if not text:
            return
        entries = self._failed.setdefault(date, {})
        key = tool, reason, text
        if key in entries or len(entries) < self.failed_cap:
            entries[key] = entries.get(key, 0) + count
        else:
            self._dropped[date] = self._dropped.get(date, 0) + count
        self._changed[date] = self._changed.get(date, 0) + 1

    async def flush(self, *, shutdown: bool = False) -> None:
        if self.path is None:
            return
        # Cancellation must not leave an unacknowledged append running beside shutdown's flush.
        task = asyncio.create_task(self._flush(shutdown=shutdown))
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            await task
            raise

    async def _flush(self, *, shutdown: bool = False) -> None:
        async with self._lock:
            try:
                await self._flush_locked(shutdown=shutdown)
                self._errors.discard("flush")
            except Exception as exc:
                self._error("flush", exc)

    async def _flush_locked(self, *, shutdown: bool = False) -> None:
        today = self._now().date()
        date = today.isoformat()
        self._roll_day(date)
        if not self._prepared:
            # Until startup preparation succeeds, the on-disk day's budget is unknown.
            self._day_rows = self.max_rows
            try:
                count = await asyncio.to_thread(_prepare_directory, self.path, date)
                self._day_rows = count + sum(row["t"][:10] == date for row in self._rows)
                self._prepared = True
                self._errors.discard("open")
            except Exception as exc:
                self._error("open", exc)
        cutoff = (today - dt.timedelta(days=self.failed_days)).isoformat()
        load_error = None
        for loading in sorted(({date} | set(self._changed)) - self._loaded_dates):
            if loading <= cutoff:
                continue
            try:
                data = await asyncio.to_thread(_load_failed, self.path, loading)
                # Merge disk first, so a restart preserves the entries that already used the cap.
                entries = {}
                dropped = max(0, stats._int(data.get("dropped"))) + self._dropped.get(loading, 0)
                for row in data.get("queries", []):
                    if (isinstance(row, dict) and isinstance(row.get("tool"), str)
                            and isinstance(row.get("reason"), str)
                            and row.get("reason") in stats.REASONS | {"row_not_found", "row_lookup_failed", "row_failed"}
                            and type(row.get("count")) is int and row["count"] > 0):
                        text = normalize_text(row.get("text"))
                        if not text:
                            continue
                        key = row["tool"], row["reason"], text
                        if key in entries or len(entries) < self.failed_cap:
                            entries[key] = entries.get(key, 0) + row["count"]
                        else:
                            dropped += row["count"]
                for key, count in self._failed.get(loading, {}).items():
                    if key in entries or len(entries) < self.failed_cap:
                        entries[key] = entries.get(key, 0) + count
                    else:
                        dropped += count
                if entries:
                    self._failed[loading] = entries
                if dropped:
                    self._dropped[loading] = dropped
                self._loaded_dates.add(loading)
            except Exception as exc:
                load_error = exc
        if load_error is not None:
            self._error("load", load_error)
        else:
            self._errors.discard("load")
        self._loaded_dates = {d for d in self._loaded_dates if d > cutoff}
        for old in set(self._failed) | set(self._changed) | set(self._dropped):
            if old <= cutoff:
                self._failed.pop(old, None)
                self._dropped.pop(old, None)
                self._changed.pop(old, None)
        revisions = {d: revision for d, revision in self._changed.items() if d in self._loaded_dates}
        snapshots = {d: {"date": d, "dropped": self._dropped.get(d, 0),
                         "queries": [{"tool": t, "reason": r, "text": text, "count": n}
                                     for (t, r, text), n in self._failed.get(d, {}).items()]}
                     for d in revisions}
        rows, pending = [], []
        minute = self._timestamp()[:16]
        for row in self._rows:
            (pending if not shutdown and "refused" in row and row["t"][:16] >= minute else rows).append(row)
        self._rows = pending
        self._redact_apps(rows)  # the whole day's evidence so far, including the rest of this batch
        self._app_days = {d: info for d, info in self._app_days.items() if d == date or any(r["t"][:10] == d for r in rows)}
        self._inflight = len(rows)
        self._buffered_bytes = sum(map(_row_bytes, pending))
        self._inflight_bytes = sum(map(_row_bytes, rows))
        rotate = self._rotated_date != date or any(row["t"][:10] != date for row in rows)
        rollbacks = self._rollbacks.copy()  # only this detached copy is touched by the worker
        try:
            remaining, saved, errors = await asyncio.to_thread(
                _persist, self.path, rows, snapshots, today, self.call_days, self.failed_days, rotate, rollbacks)
        except Exception:
            self._rows = rows + self._rows
            raise
        finally:
            self._rollbacks = rollbacks
            self._inflight = 0
            self._inflight_bytes = 0
            self._buffered_bytes = sum(map(_row_bytes, self._rows))
        self._rows = remaining + self._rows
        self._buffered_bytes = sum(map(_row_bytes, self._rows))
        for d in saved:
            if self._changed.get(d) == revisions[d]:
                self._changed.pop(d, None)
        for operation in ("append", "failed queries", "rotation"):
            if operation in errors:
                self._error(operation, errors[operation])
            else:
                self._errors.discard(operation)
        if rotate and "rotation" not in errors:
            self._rotated_date = date


def _prepare_directory(path: Path, date: str) -> int:
    """Worker-only startup repair and restart budget, without parsing private row contents."""
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)
    for source in path.iterdir():
        name = source.name.removesuffix(".tmp")
        match = _CALL_FILE.fullmatch(name) or _FAILED_FILE.fullmatch(name)
        if match and not source.is_symlink() and source.is_file():
            try:
                dt.date.fromisoformat(match[1])
            except ValueError:
                continue
            if source.name.endswith(".tmp"):
                source.unlink()
                continue
            source.chmod(0o600)
    source = path / f"calls-{date}.jsonl"
    if source.exists():
        _repair_tail(source)
        with source.open("rb") as incoming:
            return sum(1 for _ in incoming)
    compressed = source.with_suffix(".jsonl.gz")
    if compressed.exists():
        with gzip.open(compressed, "rb") as incoming:
            return sum(1 for _ in incoming)
    return 0


def _repair_tail(source: Path) -> None:
    """Discard only an unterminated final line, scanning backwards in bounded chunks."""
    with source.open("r+b") as stream:
        end = stream.seek(0, os.SEEK_END)
        position = end
        keep = 0
        while position:
            start = max(0, position - WRITE_CHUNK_BYTES)
            stream.seek(start)
            chunk = stream.read(position - start)
            newline = chunk.rfind(b"\n")
            if newline >= 0:
                keep = start + newline + 1
                break
            position = start
        if keep < end:
            stream.truncate(keep)
    if keep < end:
        logger.warning("Call log: removed incomplete tail (%d bytes)", end - keep)


def _load_failed(path: Path, date: str) -> dict:
    try:
        data = json.loads((path / f"failed-{date}.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict) or data.get("date") != date or not isinstance(data.get("queries"), list):
        raise ValueError("invalid failed-query file")
    return data


@contextmanager
def _temporary(dest: Path):
    """Remove our own temporary on failure too, after all writers have closed it."""
    tmp = dest.with_name(dest.name + ".tmp")
    try:
        yield tmp
    finally:
        tmp.unlink(missing_ok=True)


def _persist(path: Path, rows: list[dict], snapshots: dict, today: dt.date,
             call_days: int, failed_days: int, rotate: bool, rollbacks: dict[str, int]) -> tuple[list, set, dict]:
    """Worker-only detached data. Each day's failed append is rolled back before retrying."""
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)
    groups: dict[str, list] = defaultdict(list)
    for row in rows:
        groups[row["t"][:10]].append(row)
    remaining, saved, errors = [], set(), {}
    for date, batch in groups.items():
        try:
            dest = path / f"calls-{date}.jsonl"
            compressed = dest.with_suffix(".jsonl.gz")
            if not dest.exists() and compressed.exists():
                # An old day's buffered write may be retried after its earlier rows were rotated.
                with _temporary(dest) as tmp:
                    with gzip.open(compressed, "rb") as previous, _private_open(tmp, "wb") as restored:
                        shutil.copyfileobj(previous, restored)
                    os.replace(tmp, dest)
            with _private_open(dest, "ab", buffering=0) as out:
                if date in rollbacks:
                    # Do not append after surviving bytes from an unacknowledged batch.
                    # A removed file must not be padded back up to the old offset either.
                    out.truncate(min(rollbacks[date], out.tell()))
                    out.seek(0, os.SEEK_END)
                    del rollbacks[date]
                start = out.tell()
                rollbacks[date] = start
                try:
                    for payload in _row_chunks(batch):
                        pending = memoryview(payload)
                        while pending:
                            written = out.write(pending)
                            if not written:
                                raise OSError("append made no progress")
                            pending = pending[written:]
                    out.flush()
                except Exception:
                    out.truncate(start)
                    del rollbacks[date]
                    raise
            rollbacks.pop(date, None)
        except Exception as exc:
            remaining.extend(batch)
            errors["append"] = type(exc).__name__
    for date, data in snapshots.items():
        try:
            data["queries"].sort(key=lambda row: (-row["count"], row["tool"], row["reason"], row["text"]))
            dest = path / f"failed-{date}.json"
            with _temporary(dest) as tmp:
                with _private_open(tmp, "w", encoding="utf-8") as out:
                    json.dump(data, out, separators=(",", ":"))
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(tmp, dest)
            saved.add(date)
        except Exception as exc:
            errors["failed queries"] = type(exc).__name__
    if rotate:
        try:
            _rotate(path, today, call_days, failed_days, rollbacks)
        except Exception as exc:
            errors["rotation"] = type(exc).__name__
    return remaining, saved, errors


def _row_chunks(rows: list[dict]):
    chunk = bytearray()
    for row in rows:
        payload = (json.dumps(row, separators=(",", ":")) + "\n").encode("utf-8")
        for start in range(0, len(payload), WRITE_CHUNK_BYTES):
            part = payload[start:start + WRITE_CHUNK_BYTES]
            if len(chunk) + len(part) > WRITE_CHUNK_BYTES:
                yield chunk
                chunk = bytearray()
            chunk.extend(part)
    if chunk:
        yield chunk


def _rotate(path: Path, today: dt.date, call_days: int, failed_days: int,
            rollbacks: dict[str, int] | None = None) -> None:
    compress = []
    errors = []
    for source in path.iterdir():
        name = source.name.removesuffix(".tmp")
        call, failed = _CALL_FILE.fullmatch(name), _FAILED_FILE.fullmatch(name)
        match = call or failed
        if match is None or source.is_symlink() or not source.is_file():
            continue
        try:
            date = dt.date.fromisoformat(match[1])
        except ValueError:
            continue
        if date <= today - dt.timedelta(days=call_days if call else failed_days):
            try:
                source.unlink()
            except OSError as exc:
                errors.append(exc)
        elif (call and not call[2] and not source.name.endswith(".tmp") and date < today
              and match[1] not in (rollbacks or {})):
            compress.append(source)
    # Free expired bytes before allocating gzip output; one bad file cannot block other days.
    for source in compress:
        try:
            dest = source.with_suffix(".jsonl.gz")
            with _temporary(dest) as tmp:
                with _private_open(tmp, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as out:
                    with source.open("rb") as incoming:
                        shutil.copyfileobj(incoming, out)
                os.replace(tmp, dest)
            source.unlink()
        except Exception as exc:
            errors.append(exc)
    if errors:
        raise errors[0]


# Looked up at each call, so tests can substitute a recorder with an injected clock.
recorder = CallLog()
