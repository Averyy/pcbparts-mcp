"""Re-cut UTC counters into Eastern days without losing their hourly detail.

All interval arithmetic is in UTC; only calendar-day boundaries and yesterday's
wall-clock time use America/New_York. Inputs and cached records are never mutated.
"""

from copy import deepcopy
from datetime import UTC, date, datetime, time, timedelta
from functools import lru_cache
from math import floor
from zoneinfo import ZoneInfo

from .config import Settings
from .store import Store, parse_timestamp, timestamp, utc_datetime

TIMEZONE = "America/New_York"
EASTERN = ZoneInfo(TIMEZONE)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
NEAR = timedelta(seconds=90)
RULES_VERSION = 4  # Preserve legacy unsorted tool calls beside the classified outcomes.
FAILURE_REASONS = frozenset({
    "service_not_ready", "not_configured", "no_pcba_types", "query_too_complex",
    "board_db_failed", "jlcpcb_waf", "jlcpcb_unavailable", "easyeda_failed",
    "mouser_failed", "digikey_failed", "cse_auth_failed", "cse_lookup_failed",
    "cse_download_http_4xx", "cse_download_http_5xx", "cse_download_http",
    "cse_download_network", "cse_download_too_large", "cse_invalid_zip",
    "cse_download_refused", "lifecycle_lookup_failed", "exception", "unexpected_error",
})
OUTCOMES = ("ok", "similar_only", "not_found", "bad_request", "rate_limited", "failed")
# Lookups by path inside distributors.<d>.sent (from server 0.10.11: DigiKey's ext_sent; the API's
# are sent - ext_sent). A record without it counted its lookups unsplit, so a window that takes sent
# lookups from such a record keeps no split at all rather than one covering only part of its sent.
SENT_PATHS = ("ext_sent",)


def eastern_bounds(day: str | date) -> tuple[datetime, datetime]:
    day = date.fromisoformat(day) if isinstance(day, str) else day
    return (
        datetime.combine(day, time(), EASTERN).astimezone(UTC),
        datetime.combine(day + DAY, time(), EASTERN).astimezone(UTC),
    )


def _number(value) -> bool:
    return type(value) in (int, float)


def _hourly(path: tuple) -> bool:
    return (
        path in (("hours",), ("failed_hours",), ("refused_hours",))
        or (len(path) == 3 and path[0] == "distributor_limits" and path[-1] == "held_back_hours")
        or (path[:-1] in (("db_waits",), ("db_waits", "components"))
            and path[-1] in ("waited_hours", "longest_ms_hours"))
    )


def _sibling(path):
    if (len(path) == 3 and path[0] == "tools" and path[-1] == "failed") or (
        len(path) == 3 and path[0] == "reasons" and path[-1] in FAILURE_REASONS
    ):
        return ("failed_hours",)
    if path and path[0] == "per_ip_refusals":
        return ("refused_hours",)
    if (len(path) == 4 and path[0] == "distributor_limits" and path[2] == "held_back") or (
        len(path) == 3 and path[0] == "distributors" and path[-1] == "rate_limited"
    ):
        return ("distributor_limits", path[1], "held_back_hours")
    if path in (("db_waits", "waited"), ("db_waits", "components", "waited")):
        return path[:-1] + ("waited_hours",)
    return ("hours",)


def _get(record, path):
    for key in path:
        if not isinstance(record, dict):
            return None
        record = record.get(key)
    return record


def _put(record, path, value):
    for key in path[:-1]:
        if not isinstance(record.get(key), dict):
            record[key] = {}
        record = record[key]
    record[path[-1]] = value


def _hourly_paths(record, path=()):
    if _hourly(path):
        yield path
    elif isinstance(record, dict):
        for key, value in record.items():
            yield from _hourly_paths(value, path + (key,))


def _combine(lo, hi, operation, path=(), *, fold=False):
    """Arithmetic on nested counters, keeping all-unknown fields unknown."""
    if isinstance(lo, dict) or isinstance(hi, dict):
        lo = lo if isinstance(lo, dict) else {}
        hi = hi if isinstance(hi, dict) else {}
        if fold and (path in (("apps",), ("popular_terms",)) or (
            len(path) == 2 and path[0] in ("tool_apps", "distributor_apps")
        )):
            lo = deepcopy(lo)
            for key in list(lo):
                if key not in hi and key != "other":
                    value = lo.pop(key)
                    if len(path) == 2:
                        lo["other"] = _combine(lo.get("other"), value, lambda a, b, _: a + b)
                elif key not in hi and len(path) == 1:
                    lo.pop(key)  # apps/popular_terms discard vanished names, including other.
        return {
            key: _combine(lo.get(key), hi.get(key), operation, path + (key,), fold=fold)
            for key in dict.fromkeys((*lo, *hi))
        }
    if isinstance(lo, list) or isinstance(hi, list):
        lo = lo if isinstance(lo, list) else []
        hi = hi if isinstance(hi, list) else []
        return [
            _combine(lo[i] if i < len(lo) else None, hi[i] if i < len(hi) else None,
                     operation, path + (i,), fold=fold)
            for i in range(max(len(lo), len(hi)))
        ]
    if _number(lo) or _number(hi):
        return operation(lo if _number(lo) else 0, hi if _number(hi) else 0, path)
    return deepcopy(hi if hi is not None else lo)


def _counters(record, path=()):
    """Use total duration in avg_ms temporarily so subtraction/weighting is additive."""
    if _hourly(path) or path == ("callers",):
        return None
    if len(path) == 3 and path[0] == "parts_asked" and path[-1] == "distinct":
        return None
    if path in (("db_waits", "longest_ms"), ("db_waits", "components", "longest_ms")):
        return None
    if not isinstance(record, dict):
        return deepcopy(record)
    if len(path) == 2 and path[0] == "latency":
        return {"counts": deepcopy(record.get("counts"))}
    result = {
        key: _counters(value, path + (key,)) for key, value in record.items()
        if path or key not in ("date", "approx")
    }
    if len(path) == 2 and path[0] == "tools":
        avg, calls = record.get("avg_ms"), record.get("calls")
        result["avg_ms"] = avg * calls if _number(avg) and _number(calls) else None
    if len(path) == 2 and path[0] == "parts_asked":
        result["distinct"] = None
    return result


def _averages(record):
    for tool in (record.get("tools") or {}).values():
        if isinstance(tool, dict):
            duration, calls = tool.get("avg_ms"), tool.get("calls")
            tool["avg_ms"] = duration / calls if _number(duration) and calls else None
    return record


def _zero(record):
    return _combine(None, record, lambda _a, _b, _path: 0)


def _parts(start, end):
    if start >= end:
        return
    cursor = start.replace(hour=0, minute=0, second=0, microsecond=0)
    while cursor < end:
        yield cursor.date().isoformat(), max(start, cursor), min(end, cursor + DAY)
        cursor += DAY


def _window_only(record):
    return {key: deepcopy(value) for key, value in record.items()
            if key not in ("date", "complete", "partial_start", "partial_end", "problems")}


def _family_groups(record):
    """Each group sums to its hourly sibling (a series can have several views)."""
    yield ("hours",), [("calls",)]
    yield ("failed_hours",), [("tools", tool, "failed") for tool in record.get("tools") or {}]
    refusals = record.get("per_ip_refusals") or {}
    yield ("refused_hours",), [("per_ip_refusals", "total")]
    yield ("refused_hours",), [("per_ip_refusals", key) for key in refusals if key != "total"]
    names = dict.fromkeys((*(record.get("distributor_limits") or {}), *(record.get("distributors") or {})))
    for name in names:
        series = ("distributor_limits", name, "held_back_hours")
        yield series, [("distributors", name, "rate_limited")]
        held = _get(record, ("distributor_limits", name, "held_back")) or {}
        yield series, [("distributor_limits", name, "held_back", key) for key in held]
    for path in (("db_waits",), ("db_waits", "components")):
        yield path + ("waited_hours",), [path + ("waited",)]


def _rescale(record, paths, target, fallback=None) -> bool:
    """Scale the parts to sum to target; False when there is no basis to split it."""
    paths = [p for p in paths if _number(_get(record, p))]
    if not paths:
        return False
    weights = [max(0, _get(record, p)) for p in paths]
    if not sum(weights) and fallback:
        weights = [max(0, _get(fallback, p) or 0) for p in paths]
    total = sum(weights)
    if not total:
        # Nothing says how the total divides (no cause was recorded for it): put it under "other"
        # where the family has one rather than invent an even split; otherwise leave the parts.
        other = next((p for p in paths if p[-1] == "other"), None)
        if other is None:
            return False
        for path in paths:
            _put(record, path, target if path == other else 0)
        return True
    for path, weight in zip(paths, weights):
        _put(record, path, target * weight / total)
    return True


def _apportion(record, paths, target):
    """Largest remainder, with stable path order breaking equal remainders."""
    paths = [p for p in paths if _number(_get(record, p))]
    if not paths:
        return
    if not _rescale(record, paths, max(0, round(target))):
        return
    values = [_get(record, p) for p in paths]
    rounded = [floor(v) for v in values]
    remaining = max(0, round(target)) - sum(rounded)
    order = sorted(range(len(paths)), key=lambda i: values[i] - rounded[i], reverse=True)
    for index in order[:remaining]:
        rounded[index] += 1
    for path, value in zip(paths, rounded):
        _put(record, path, value)


def _finish(record):
    """Round only the finished window; keep family totals and partitions aligned."""
    # Partial bins can round differently from their combined fractional total.
    for series, paths in _family_groups(record):
        values = _get(record, series) or []
        delta = sum(round(v) - v for v in values if _number(v))
        known = [p for p in paths if _number(_get(record, p))]
        if known:
            _rescale(record, known, max(0, sum(_get(record, p) for p in known) + delta))
    tools = record.get("tools") or {}
    failures = [("tools", name, "failed") for name in tools]
    fixed_failures = any(_number(v) for v in record.get("failed_hours") or [])
    if fixed_failures:
        _apportion(record, failures, sum(_get(record, p) or 0 for p in failures))
    complete_tools = tools and all(
        isinstance(tool, dict) and all(_number(tool.get(key)) for key in ("calls", *OUTCOMES))
        for tool in tools.values()
    )
    if complete_tools and _number(record.get("calls")):
        _apportion(record, [("tools", name, "calls") for name in tools], record["calls"])
        if fixed_failures and any(tool["failed"] > tool["calls"] for tool in tools.values()):
            # Per-tool call shares are estimates too: make room for the recorded failures.
            remaining = round(record["calls"]) - sum(tool["failed"] for tool in tools.values())
            if remaining >= 0:
                for tool in tools.values():
                    tool["calls"] = max(0, tool["calls"] - tool["failed"])
                _apportion(record, [("tools", name, "calls") for name in tools], remaining)
                for tool in tools.values():
                    tool["calls"] += tool["failed"]
    for name, tool in (record.get("tools") or {}).items():
        if not isinstance(tool, dict):
            continue
        if all(_number(tool.get(key)) for key in ("calls", *OUTCOMES)):
            # Failure placement comes from failed_hours; balance other outcomes around it.
            tool["calls"] = round(tool["calls"])
            keys = [key for key in OUTCOMES if not fixed_failures or key != "failed"]
            if _number(tool.get("unsorted")):
                keys.append("unsorted")
            _apportion(tool, [(key,) for key in keys], tool["calls"] - (tool["failed"] if fixed_failures else 0))
        reasons = (record.get("reasons") or {}).get(name)
        if isinstance(reasons, dict) and _number(tool.get("not_found")) and _number(tool.get("failed")):
            # Keep failure labels in the same hours as failures, even when misses dominate.
            failed = [(key,) for key in reasons if key in FAILURE_REASONS]
            missed = [(key,) for key in reasons if key not in FAILURE_REASONS]
            if failed and missed:
                _apportion(reasons, failed, tool["failed"])
                _apportion(reasons, missed, tool["not_found"])
            else:
                _apportion(reasons, [(key,) for key in reasons], round(tool["not_found"]) + round(tool["failed"]))
    refusals = record.get("per_ip_refusals")
    if isinstance(refusals, dict) and _number(refusals.get("total")):
        _apportion(refusals, [(key,) for key in refusals if key != "total"], refusals["total"])
    for name, limits in (record.get("distributor_limits") or {}).items():
        held = limits.get("held_back") if isinstance(limits, dict) else None
        if isinstance(held, dict):
            total = _get(record, ("distributors", name, "rate_limited"))
            _apportion(held, [(key,) for key in held], total if _number(total) else sum(v for v in held.values() if _number(v)))

    def rounded(value, path=()):
        if isinstance(value, dict):
            return {key: rounded(v, path + (key,)) for key, v in value.items()}
        if isinstance(value, list):
            return [rounded(v, path + (i,)) for i, v in enumerate(value)]
        if _number(value) and not (len(path) == 3 and path[0] == "tools" and path[-1] == "avg_ms"):
            return round(value)
        return value

    result = rounded(record)
    for tool in (result.get("tools") or {}).values():
        if isinstance(tool, dict) and tool.get("calls") == 0:
            tool["avg_ms"] = None
    return result


class EasternRecords:
    """One consistent set of stored inputs and an injected data horizon."""

    def __init__(self, store: Store, as_of: datetime, problems_version: str | None = None):
        self.store = store
        self.as_of = utc_datetime(as_of)
        with store.lock:
            self.days = store.day_dates()
            self.snapshot_times = {
                day: [parse_timestamp(at) for at in times]
                for day, times in store.snapshot_times().items()
            }
            self.saved_versions = store.eastern_rules_versions()
            self.first_snapshot_date = store.first_snapshot_date()
            _, health = store.newest_health()
            current_version = health.get("version") if isinstance(health, dict) else None
            self.problems_version = problems_version or store.get_meta("problems_version") or current_version
        self._day = lru_cache(maxsize=3)(store.day_input)
        self._snapshots = lru_cache(maxsize=3)(store.snapshots_for)
        self._points = {}

    def _samples(self, day):
        return [(parse_timestamp(at), record) for at, record in self._snapshots(day)]

    def _record(self, day):
        if day in self.days:
            fetched, record = self.days[day], self._day(day)
            end = parse_timestamp(day + "T00:00:00Z") + DAY
            if end > self.as_of and parse_timestamp(fetched) > self.as_of:
                samples = [record for at, record in self._samples(day) if at <= self.as_of]
                return samples[-1] if samples else {}
            return record
        samples = self._samples(day)
        return samples[-1][1] if samples else {}

    def _final(self, day):
        end = parse_timestamp(day + "T00:00:00Z") + DAY
        return day in self.days and end <= self.as_of and parse_timestamp(self.days[day]) >= end

    def _known_points(self, day):
        start = parse_timestamp(day + "T00:00:00Z")
        end = start + DAY
        points = {start: _zero(self._record(day))}
        # A stored, unfinished day's fetch remains a useful point after a long outage.
        if day in self.days:
            fetched, record = self.days[day], self._day(day)
            fetched = parse_timestamp(fetched)
            if start < fetched < end and fetched <= self.as_of:
                points[fetched] = record
        points.update({
            at: record for at, record in self._samples(day)
            if start < at <= min(end, self.as_of)
        })
        if self._final(day):
            points[end] = self._day(day)
        return sorted(points.items())

    def _fraction(self, day, lo, hi, target, series=("hours",)):
        def total(path, start, end):
            hours = _get(self._record(day), path)
            if not isinstance(hours, list):
                return None
            total = 0
            cursor = start.replace(minute=0, second=0, microsecond=0)
            while cursor < end:
                value = hours[cursor.hour] if cursor.hour < len(hours) else None
                if not _number(value):
                    return None
                seconds = (min(cursor + HOUR, end) - max(cursor, start)).total_seconds()
                total += value * seconds / 3600
                cursor += HOUR
            return total

        before, whole = total(series, lo, target), total(series, lo, hi)
        if whole is None and series != ("hours",):
            return self._fraction(day, lo, hi, target)
        if before is not None and whole:
            return min(1, max(0, before / whole))
        return (target - lo) / (hi - lo)

    def at(self, day: str, moment: datetime) -> dict:
        """UTC day's cumulative record at moment, with an explicit approx flag."""
        moment = utc_datetime(moment)
        start = parse_timestamp(day + "T00:00:00Z")
        end = start + DAY
        if not start <= moment <= end:
            raise ValueError("at() requires a moment within its UTC day")
        key = (day, moment)
        if key in self._points:
            return deepcopy(self._points[key])
        if moment == start:
            result = _zero(self._record(day)) | {"approx": False}
        elif moment == end and self._final(day):
            result = deepcopy(self._day(day)) | {"approx": False}
        else:
            points = self._known_points(day)
            # The synthetic zero and final record are exact only at their boundaries.
            samples = [(at, record) for at, record in points if start < at < end]
            near = min(samples, key=lambda item: abs(item[0] - moment), default=None)
            if near is not None and abs(near[0] - moment) <= NEAR:
                result = deepcopy(near[1]) | {"approx": False}
            else:
                lo_at, lo = max((p for p in points if p[0] <= moment), key=lambda p: p[0])
                later = [p for p in points if p[0] > moment]
                if not later:
                    result = deepcopy(lo) | {"approx": True}
                else:
                    hi_at, hi = later[0]
                    fractions = {}

                    def blend(a, b, path):
                        series = _sibling(path)
                        if series not in fractions:
                            fractions[series] = self._fraction(day, lo_at, hi_at, moment, series)
                        return a + (b - a) * fractions[series]

                    result = _averages(_combine(_counters(lo), _counters(hi), blend, fold=True))
                    for path in _hourly_paths(self._record(day)):
                        _put(result, path, deepcopy(_get(self._record(day), path)))
                    result["approx"] = True
        result["date"] = day
        if len(self._points) >= 32:
            self._points.clear()
        self._points[key] = result
        return deepcopy(result)

    def _bins(self, path, start, end, *, scale_end=False, baseline=None):
        if start >= end:
            return
        cursor = start.replace(minute=0, second=0, microsecond=0)
        while cursor < end:
            hours = _get(self._record(cursor.date().isoformat()), path)
            value = hours[cursor.hour] if isinstance(hours, list) and cursor.hour < len(hours) else None
            estimated = False
            if _number(value):
                stop = min(cursor + HOUR, end) if scale_end else cursor + HOUR
                if baseline and cursor < baseline[0]:
                    # Keep the cutoff's hour labels, removing what the exact baseline saw.
                    at, record = baseline
                    old_hours = _get(record, path)
                    old = old_hours[cursor.hour] if isinstance(old_hours, list) and cursor.hour < len(old_hours) else None
                    if old is None and all(_number(v) for v in hours[:cursor.hour]):
                        # Older snapshots may omit the series but still have its cumulative total.
                        for series, paths in _family_groups(record):
                            values = [_get(record, p) for p in paths]
                            if series == path and values and all(_number(v) for v in values):
                                old = max(0, sum(values) - sum(hours[:cursor.hour]))
                                break
                    if cursor + HOUR <= at:
                        value = 0
                    elif path[-1] == "longest_ms_hours":
                        # Maxima cannot be subtracted. A larger maximum must be new;
                        # otherwise this partial bucket may still contain the old peak.
                        estimated = not _number(old) or (old > 0 and value <= old)
                    elif _number(old):
                        estimated = old > value
                        value = max(0, value - old)
                    else:
                        value *= max(timedelta(0), stop - at) / HOUR
                        estimated = True
                else:
                    fraction = (stop - max(cursor, start)) / HOUR
                    value *= fraction
                    estimated = start > cursor or (scale_end and stop < cursor + HOUR)
            yield cursor, value, estimated
            cursor += HOUR

    def _align_totals(self, part, day, start, end, *, scale_end=False, baseline=None):
        """Use recorded bins directly, estimating only gaps in a sibling series."""
        approx = False
        for series, paths in _family_groups(part):
            paths = [p for p in paths if _number(_get(part, p))]
            bins = list(self._bins(series, start, end, scale_end=scale_end, baseline=baseline))
            if not paths or not any(_number(value) for _, value, _ in bins):
                continue
            total = 0
            for cursor, value, _ in bins:
                if _number(value):
                    total += value
                else:
                    lo_at, hi_at = max(cursor, start), min(cursor + HOUR, end)
                    if baseline:
                        lo_at = max(lo_at, baseline[0])
                    if lo_at >= hi_at:
                        continue
                    lo = baseline[1] if baseline and lo_at == baseline[0] else self.at(day, lo_at)
                    hi = self.at(day, hi_at)
                    approx |= lo.get("approx", False) or hi["approx"]
                    total += sum(max(0, (_get(hi, p) or 0) - (_get(lo, p) or 0)) for p in paths)
            _rescale(part, paths, total, self._record(day))
        return approx

    def _unsplit(self, part, day, lo_at, hi_at, baseline=None):
        """(distributor, path) pairs one UTC day's part can't split: it sent lookups, and a real record
        its endpoints come from, or one between them, has that distributor's counts without the path.
        The subtracted part can't tell: a path in one endpoint only reads as a number there. The
        synthetic midnight zero takes its fields from the day's newest record, so it says nothing."""
        names = [name for name, counts in (part.get("distributors") or {}).items()
                 if isinstance(counts, dict) and _number(counts.get("sent")) and counts["sent"] > 0]
        if not names:
            return set()
        midnight = parse_timestamp(day + "T00:00:00Z")
        points = self._known_points(day)
        used = baseline is not None and lo_at == baseline[0]
        first = lo_at if used else max((at for at, _ in points if at <= lo_at), default=midnight)
        last = min((at for at, _ in points if at >= hi_at), default=max(at for at, _ in points))
        records = [record for at, record in points if first <= at <= last and at != midnight]
        if used:
            records.append(baseline[1])
        return {
            (name, key) for name in names for key in SENT_PATHS
            if any(isinstance(counts := _get(record, ("distributors", name)), dict) and not _number(counts.get(key))
                   for record in records)
        }

    def window(self, start: datetime, end: datetime, *, scale_end=False, baseline=None) -> dict:
        """Subtract endpoints; copy hourly bins (scale yesterday's last bin on request).

        A live partial end already has a partial observed bucket, so it is not scaled
        again. Non-hour-aligned starts are supported as proportional estimates.
        """
        start, end = utc_datetime(start), utc_datetime(end)
        if end < start:
            raise ValueError("window() end precedes start")
        approx = False
        result = {}
        records = []
        unsplit = set()
        for day, lo_at, hi_at in _parts(start, end):
            records.append(self._record(day))
            if day not in self.days:
                approx = True
            if baseline and lo_at < baseline[0]:
                lo_at = min(hi_at, baseline[0])
            lo = (deepcopy(baseline[1]) | {"approx": False}
                  if baseline and lo_at == baseline[0] else self.at(day, lo_at))
            hi = self.at(day, hi_at)
            approx |= lo["approx"] or hi["approx"]

            def subtract(a, b, _path):
                nonlocal approx
                if b < a:
                    approx = True
                return max(0, b - a)

            part = _combine(_counters(lo), _counters(hi), subtract, fold=True)
            approx |= self._align_totals(part, day, max(start, parse_timestamp(day + "T00:00:00Z")), hi_at,
                                        scale_end=scale_end, baseline=baseline)
            unsplit |= self._unsplit(part, day, lo_at, hi_at, baseline)
            result = _combine(result, part, lambda a, b, _: a + b)
        if start == end:
            record = self._record(start.date().isoformat())
            records.append(record)
            result = _counters(_zero(record))
        for name, key in unsplit:
            counts = _get(result, ("distributors", name))
            if isinstance(counts, dict):
                counts.pop(key, None)
        _averages(result)
        result.setdefault("calls", None)
        result["callers"] = None
        paths = {("hours",), ("failed_hours",), ("refused_hours",)}
        for record in records:
            paths.update(_hourly_paths(record))
        count = 0
        exact_calls = True
        for path in sorted(paths):
            values = []
            for _, value, estimated in self._bins(path, start, end, scale_end=scale_end, baseline=baseline):
                approx |= estimated
                if path == ("hours",):
                    exact_calls &= _number(value) and not estimated
                values.append(value)
            count = len(values)
            _put(result, path, values if any(v is not None for v in values) else None)
        for path in (("db_waits",), ("db_waits", "components")):
            waits = _get(result, path)
            if isinstance(waits, dict):
                values = waits.get("longest_ms_hours") or []
                waits["longest_ms"] = max((v for v in values if _number(v)), default=None)
        result.update(start=timestamp(start), end=timestamp(end), hours_in_window=count,
                      approx=bool(approx), exact_calls=bool(exact_calls))
        return _finish(result)

    def _problem_baseline(self, start, end):
        if start > min(end, self.as_of):
            return None
        first_new = self.store.version_fetch_at(self.problems_version) if self.problems_version else None
        first_new = parse_timestamp(first_new) if first_new else None
        stop = min(start + timedelta(minutes=10), end, self.as_of)
        candidates = [
            (at, record) for day, _, _ in _parts(start, stop + timedelta(microseconds=1))
            for at, record in self._samples(day)
            if start <= at <= stop
            and (first_new is None or at < first_new or at == start)
        ]
        return min(candidates, key=lambda item: item[0], default=None)

    def _exact_boundaries(self, start, end, baseline=None):
        def exact(day, moment):
            midnight = parse_timestamp(day + "T00:00:00Z")
            if moment == midnight or (moment == midnight + DAY and self._final(day)):
                return True
            samples = self.snapshot_times.get(day, [])
            if day in self.days:
                samples = [*samples, parse_timestamp(self.days[day])]
            return any(
                midnight < at < midnight + DAY and at <= self.as_of and abs(at - moment) <= NEAR
                for at in samples
            )

        return all(
            day in self.days and (exact(day, lo) or (baseline is not None and lo == start)) and exact(day, hi)
            for day, lo, hi in _parts(start, end)
        )

    def _can_recompute(self, start, end):
        # Without the source snapshots a new estimate could erase a better saved day. A UTC day from
        # before the first snapshot ever taken never had any: recomputing it from its final record
        # loses nothing.
        first = self.first_snapshot_date
        return all(
            self._final(day) and (bool(self.snapshot_times.get(day)) or first is None or day < first)
            for day, _, _ in _parts(start, end)
        )

    def eastern_day(self, day: str, problems_since: datetime | None = None) -> dict:
        self._points.clear()
        start, full_end = eastern_bounds(day)
        end = min(full_end, self.as_of)
        if end < start:
            raise ValueError("Eastern day starts after as_of")
        cached = self.store.eastern_day(day)
        if cached is not None and cached["end"] != timestamp(end):
            cached = None  # An older live as_of must not use a later import's complete day.
        old_rules = cached is not None and self.saved_versions.get(day, 1) < RULES_VERSION
        upgrade_rules = old_rules and self._can_recompute(start, end)
        result = None
        if cached is not None and not upgrade_rules:
            # This row was decoded for this call; only the top-level flags change.
            result = cached.copy()
            if not old_rules and cached["approx"] and self._exact_boundaries(start, end):
                candidate = self.window(start, end)
                if not candidate["approx"]:
                    result = candidate
        if result is None:
            result = self.window(start, end)
        first = parse_timestamp(min(self.days) + "T00:00:00Z") if self.days else start
        result.update(date=day, complete=full_end <= self.as_of,
                      partial_start=start < first, partial_end=full_end > self.as_of)
        # Legacy rows retained after pruning cannot certify exact calls under new rules.
        result.setdefault("exact_calls", False)
        problem_start = max(start, problems_since) if problems_since else start
        baseline = self._problem_baseline(problem_start, end) if problem_start == problems_since else None
        if problem_start >= end:
            problems = None
        else:
            previous = (cached or {}).get("problems")
            if not upgrade_rules and previous and (previous["start"], previous["end"]) == (timestamp(problem_start), timestamp(end)):
                problems = previous.copy()
                if not old_rules and previous["approx"] and self._exact_boundaries(problem_start, end, baseline):
                    candidate = self.window(problem_start, end, baseline=baseline)
                    if not candidate["approx"]:
                        problems = candidate
            elif problem_start == start and baseline is None:
                problems = _window_only(result)
            else:
                problems = self.window(problem_start, end, baseline=baseline)
            problems.setdefault("exact_calls", False)
        result["problems"] = problems
        # Wait for both UTC final records, even when the Eastern day has already ended.
        eligible = result["complete"] and all(self._final(d) for d, _, _ in _parts(start, full_end))
        if eligible and not (old_rules and not upgrade_rules) and (result != cached or upgrade_rules):
            self.store.save_eastern_day(result, timestamp(self.as_of), rules_version=RULES_VERSION)
            self.saved_versions[day] = RULES_VERSION
        return result

    def persist(self, problems_since: datetime | None = None) -> None:
        """Visit only rows that can change; never build a full payload for a poll."""
        if not self.days:
            return
        saved = self.store.eastern_index()
        day = parse_timestamp(min(self.days) + "T00:00:00Z").astimezone(EASTERN).date()
        while day <= self.as_of.astimezone(EASTERN).date():
            name = day.isoformat()
            start, end = eastern_bounds(day)
            # A partial Eastern day cannot be persisted, nor can a UTC input still in flight.
            if end <= self.as_of and all(self._final(d) for d, _, _ in _parts(start, end)):
                cached = saved.get(name)
                needs_update = cached is None
                if cached is not None:
                    version, approx, saved_end, problem_start, problem_end, problem_approx = cached
                    old_rules = version < RULES_VERSION
                    cutoff = max(start, problems_since) if problems_since else start
                    expected = (timestamp(cutoff), timestamp(end)) if cutoff < end else (None, None)
                    needs_update = (
                        saved_end != timestamp(end)
                        or (old_rules and self._can_recompute(start, end))
                        or (not old_rules and approx and self._exact_boundaries(start, end))
                        or (problem_start, problem_end) != expected
                    )
                    if not needs_update and not old_rules and problem_approx:
                        baseline = self._problem_baseline(cutoff, end) if cutoff == problems_since else None
                        needs_update = self._exact_boundaries(cutoff, end, baseline)
                if needs_update:
                    self.eastern_day(name, problems_since)
            day += DAY

    def all_days(self, problems_since: datetime | None = None) -> list[dict]:
        if not self.days:
            return []
        day = parse_timestamp(min(self.days) + "T00:00:00Z").astimezone(EASTERN).date()
        today = self.as_of.astimezone(EASTERN).date()
        result = []
        while day <= today:
            result.append(self.eastern_day(day.isoformat(), problems_since))
            day += DAY
        return result

    def compare_today(self) -> dict | None:
        local = self.as_of.astimezone(EASTERN)
        yesterday = local - DAY  # Calendar arithmetic, not 24 elapsed UTC hours.
        start, day_end = eastern_bounds(yesterday.date())
        if not any(self._record(day) for day, _, _ in _parts(start, day_end)):
            return None
        end = yesterday.astimezone(UTC)
        return self.window(start, end, scale_end=True) | {"date": yesterday.date().isoformat()}


def problems_settings(store: Store, settings: Settings | None = None) -> tuple[str | None, str | None]:
    return (
        (settings.problems_since if settings else None) or store.get_meta("problems_since"),
        (settings.problems_version if settings else None) or store.get_meta("problems_version"),
    )


def observe_version(store: Store, settings: Settings, health, moment: datetime) -> None:
    version = health.get("version") if isinstance(health, dict) else None
    if not isinstance(version, str) or not version:
        return
    with store.lock:
        previous = store.get_meta("seen_version")
        if settings.problems_since is None:
            if previous is None and store.get_meta("problems_since") is None:
                # A new store can't know when the running version was deployed: problems count from
                # its first look, so older ones (from code that may be long replaced) never show.
                store.set_meta("problems_since", timestamp(moment))
                store.set_meta("problems_version", version)
            elif previous is not None and previous != version:
                baseline = store.version_fetch_at(previous, last=True, before=timestamp(moment))
                store.set_meta("problems_since", baseline or store.version_fetch_at(version) or timestamp(moment))
                store.set_meta("problems_version", version)
        store.set_meta("seen_version", version)


def persist_eastern_days(store: Store, as_of: datetime, settings: Settings | None = None) -> None:
    with store.lock:
        since, version = problems_settings(store, settings)
        EasternRecords(store, as_of, version).persist(parse_timestamp(since) if since else None)
