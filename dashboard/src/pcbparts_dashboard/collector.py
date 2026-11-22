"""Fetch or import statistics without losing historical detail."""

import json
import math
import re
import zlib
from contextlib import nullcontext
from datetime import UTC, date, datetime, timedelta
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

from .config import Settings
from .eastern import observe_version, persist_eastern_days
from .store import Store, parse_timestamp, timestamp, utc_datetime

USER_AGENT = "pcbparts-dashboard/0.1"
STATS_MAX_BYTES = 16 * 1024 * 1024
HEALTH_MAX_BYTES = 1024 * 1024
MAX_COMPRESSED_BYTES = 16 * 1024 * 1024
COUNT_MAPS = frozenset({
    "tools", "apps", "reasons", "why_empty", "upstream", "parts_asked",
    "per_ip_refusals", "lcsc_lookups", "distributor_apps", "distributor_limits",
    "datasheet_links", "db_waits", "lifecycle_inputs", "bad_request_reasons",
    "tool_apps", "latency", "popular_terms", "distributors",
})
NESTED_COUNT_MAPS = frozenset({
    "tools", "reasons", "upstream", "parts_asked", "lcsc_lookups",
    "distributor_apps", "distributor_limits", "bad_request_reasons",
    "tool_apps", "latency", "distributors",
})


def _validate_field(value, path: tuple) -> None:
    """Check containers consumed by Eastern arithmetic; allow absent/unknown detail."""
    if value is None:
        return
    root, key = path[0], path[-1]
    is_map = (
        (len(path) == 1 and root in COUNT_MAPS)
        or (len(path) == 2 and root in NESTED_COUNT_MAPS)
        or (len(path) == 3 and root in ("tool_apps", "distributor_apps"))
        or (root == "distributor_limits" and len(path) == 3 and key in ("held_back", "refusals"))
        or path == ("db_waits", "components")
    )
    is_list = (
        path in (("hours",), ("failed_hours",), ("refused_hours",))
        or (root == "distributor_limits" and key == "held_back_hours")
        or (root == "db_waits" and key in ("waited_hours", "longest_ms_hours"))
        or (root == "latency" and key == "counts")
    )
    valid = True
    if is_map:
        valid = isinstance(value, dict)
        if valid:
            for name, child in value.items():
                _validate_field(child, path + (name,))
    elif is_list:
        valid = isinstance(value, list)
        if valid:
            for child in value:
                _validate_field(child, ("count",))
    elif root in COUNT_MAPS or root in ("calls", "callers", "restarts", "count"):
        valid = type(value) in (int, float) and 0 <= value <= 10**12
    elif isinstance(value, dict):
        for name, child in value.items():
            _validate_field(child, path + (name,))
    elif isinstance(value, list):
        for child in value:
            _validate_field(child, path)
    elif type(value) in (int, float):
        valid = math.isfinite(value)
    if not valid:
        # Field names may be supplied by upstream; the caller redacts the whole error.
        raise ValueError("Invalid nested field " + ".".join(path))


def _validate_stats(reply: object) -> dict:
    if not isinstance(reply, dict) or not isinstance(reply.get("days"), list):
        raise ValueError("Missing days list")
    for record in reply["days"]:
        if not isinstance(record, dict) or not isinstance(record.get("date"), str):
            raise ValueError("Invalid day record")
        if date.fromisoformat(record["date"]).isoformat() != record["date"]:
            raise ValueError("Invalid day date")
        calls = record.get("calls")
        if calls is not None and (type(calls) is not int or calls < 0):
            raise ValueError("Invalid day calls")
        for key, value in record.items():
            _validate_field(value, (key,))
    return reply


def _response_error(response: httpx.Response, reason: str, token: str, content: bytes) -> str:
    # Redact before truncating so even a token crossing the 200-character boundary is safe.
    body = content[:4096 + len(token.encode())].decode("utf-8", errors="replace")
    body = body.replace(token, "[redacted]") if token else body
    body = " ".join(body.split())[:200]
    return f"{reason} (HTTP {response.status_code}): {body}"


class ResponseLimitError(ValueError):
    pass


def _read_response(response: httpx.Response, limit: int, wire_limit: int) -> bytes:
    """Bound wire bytes and inflation independently, before HTTPX can decode gzip."""
    if response.is_stream_consumed:
        # Mock/custom transports can return an already buffered Response.
        if len(response.content) > limit:
            raise ResponseLimitError("decoded response exceeds byte limit")
        if len(response.content) > wire_limit:
            raise ResponseLimitError("compressed response exceeds byte limit")
        return response.content
    encoding = response.headers.get("Content-Encoding", "identity").strip().lower()
    if encoding not in ("identity", "gzip"):
        raise ValueError("Unsupported content encoding")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS) if encoding == "gzip" else None
    size = 0
    with BytesIO() as output:
        for chunk in response.iter_raw():
            size += len(chunk)
            if size > wire_limit:
                raise ResponseLimitError("compressed response exceeds byte limit")
            while chunk:
                if decoder is None:
                    decoded, chunk = chunk, b""
                else:
                    if decoder.eof:
                        # gzip permits concatenated members; they share the same limits.
                        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
                    decoded = decoder.decompress(chunk, min(65536, limit - output.tell() + 1))
                    chunk = decoder.unused_data if decoder.eof else decoder.unconsumed_tail
                if output.tell() + len(decoded) > limit:
                    raise ResponseLimitError("decoded response exceeds byte limit")
                output.write(decoded)
        if decoder is not None and not decoder.eof:
            raise ValueError("Incomplete gzip response")
        return output.getvalue()


def collect(settings: Settings, store: Store, *, days=None, client=None, now=None) -> dict:
    moment = utc_datetime(now() if callable(now) else now)
    at = timestamp(moment)
    if days is None:
        last_full = store.get_meta("last_full_fetch_at")
        try:
            full_due = not last_full or moment - parse_timestamp(last_full) > timedelta(hours=24)
        except (TypeError, ValueError):
            full_due = True
        days = 365 if full_due else 3
    last_fetch = {
        "at": at, "ok": False, "error": None, "days_requested": days,
        "status_code": None, "health_error": None,
    }
    result = {"ok": False, "error": None, "days_requested": days, "days_stored": 0, "fetched_at": at}

    def fail(error: str) -> dict:
        last_fetch["error"] = result["error"] = error
        store.set_meta("last_fetch", last_fetch)
        return result

    if type(days) is not int or not 1 <= days <= 365:
        return fail("days must be an integer between 1 and 365")
    if not settings.stats_token:
        return fail("STATS_TOKEN is required for collecting")

    with (nullcontext(client) if client is not None else httpx.Client()) as http:
        try:
            with http.stream(
                "GET", settings.stats_url,
                params={"days": days},
                headers={"Authorization": f"Bearer {settings.stats_token}", "User-Agent": USER_AGENT,
                         "Accept-Encoding": "gzip, identity"},
                timeout=httpx.Timeout(30.0),
                follow_redirects=False,
            ) as response:
                last_fetch["status_code"] = response.status_code
                body = _read_response(response, STATS_MAX_BYTES, MAX_COMPRESSED_BYTES)
        except ResponseLimitError as exc:
            return fail(f"Stats request failed: {exc}")
        except (httpx.HTTPError, httpx.InvalidURL, ValueError, zlib.error) as exc:
            return fail(f"Stats request failed ({type(exc).__name__})")
        if response.status_code != 200:
            return fail(_response_error(response, "Stats request failed", settings.stats_token, body))
        try:
            reply = json.loads(body)
        except (ValueError, RecursionError):
            return fail(_response_error(response, "Invalid stats JSON", settings.stats_token, body))
        try:
            reply = _validate_stats(reply)
        except (ValueError, TypeError, OverflowError, RecursionError) as exc:
            detail = str(exc).replace(settings.stats_token, "[redacted]")[:150]
            return fail(_response_error(response, f"Missing days list or invalid day record ({detail})", settings.stats_token, body))

        result["days_stored"] = store.save_stats(reply, at)
        store.set_meta("last_success_at", at)
        if days >= 365:
            store.set_meta("last_full_fetch_at", at)
        last_fetch["ok"] = result["ok"] = True

        try:
            with http.stream(
                "GET", settings.health_url,
                headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, identity"},
                timeout=httpx.Timeout(15.0), follow_redirects=False,
            ) as health:
                health_body = _read_response(health, HEALTH_MAX_BYTES, min(MAX_COMPRESSED_BYTES, 1024 * 1024))
            if health.status_code == 200:
                try:
                    reply_health = json.loads(health_body)
                    store.save_health(reply_health, at)
                    observe_version(store, settings, reply_health, moment)
                except (ValueError, RecursionError):
                    last_fetch["health_error"] = _response_error(health, "Invalid health JSON", settings.stats_token, health_body)
            else:
                last_fetch["health_error"] = _response_error(health, "Health request failed", settings.stats_token, health_body)
        except ResponseLimitError as exc:
            last_fetch["health_error"] = f"Health request failed: {exc}"
        except (httpx.HTTPError, httpx.InvalidURL, ValueError, zlib.error) as exc:
            last_fetch["health_error"] = f"Health request failed ({type(exc).__name__})"
        store.set_meta("last_fetch", last_fetch)
        persist_eastern_days(store, moment, settings)
        store.prune(moment)
    return result


def import_files(store: Store, paths, *, settings: Settings | None = None) -> dict:
    total = 0
    count = 0
    for raw_path in paths:
        path = Path(raw_path)
        reply = _validate_stats(json.loads(path.read_text()))
        match = re.fullmatch(r"mcp-stats_(\d{4}-\d{2}-\d{2})_(\d{4})-EST.*\.json", path.name)
        if match:
            local = datetime.strptime("_".join(match.groups()), "%Y-%m-%d_%H%M")
            moment = local.replace(tzinfo=ZoneInfo("America/New_York")).astimezone(UTC)
        else:
            moment = datetime.fromtimestamp(path.stat().st_mtime, UTC)
        total += store.save_stats(reply, timestamp(moment))
        count += 1
    latest = store.newest_stats_at()
    if latest:
        persist_eastern_days(store, parse_timestamp(latest), settings)
    return {"ok": True, "files_imported": count, "days_stored": total}
