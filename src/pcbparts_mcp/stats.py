"""Anonymous usage counts per UTC day, served at /mcp/stats.

Per day: calls to each tool, split by outcome (see OUTCOMES), with the average time; calls in each UTC
hour; the MCP apps that connected (by the name each app reports when it connects), the number of distinct
callers, and what happened to Mouser/DigiKey lookups (sent, answered from the cache, or turned away
by the shared limits). For calls that found nothing or failed, the reason, from a fixed list of labels
(REASONS); and how the checks behind jlc_search's why_empty went. From 0.10.0 also the requests sent to
the other services we call and the answers their caches saved (UPSTREAM_SOURCES), how many part numbers
were looked up with Mouser and DigiKey and how many of them were different, and the HTTP requests the
rate limit or the busy cap turned away. No IPs, queries or part numbers are kept: callers and distinct
part numbers are counted through salted hashes held in memory for the current day only, with a new
random salt each day. A restart starts a new set, so a caller or part seen before and after one on the
same day counts twice; each day's `restarts` (from 0.10.0) says how many there were.

The server writes the counts to USAGE_STATS_PATH (a JSON file on the cache volume) every minute and
at shutdown; unset means memory only. The file keeps a year; /mcp/stats shows the last 30 days. Nothing
here raises on a bad or unwritable file, like QuotaStore: a file that can't be read is moved aside
(USAGE_STATS_PATH.corrupt, one kept) before counting starts from 0, so the next save can't overwrite
it, and a day's fields this version doesn't know (a newer version's) are kept as they are.
"""

import datetime
import hashlib
import json
import logging
import math
import os
import re
import secrets
import time
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

KEEP_DAYS = 365  # in the file (about 1 MB for a busy year, at most about 3 MB)
PUBLIC_DAYS = 30  # the most /mcp/stats shows
MAX_CALLERS = 100_000  # distinct callers counted a day (bounds memory); later ones aren't counted
MAX_APPS = 50  # distinct app names a day; later ones count as "other"
APP_NAME_LENGTH = 40
_NOT_IN_APP_NAME = re.compile(r"[^A-Za-z0-9 ._()/+-]")  # app names are self-reported and shown publicly
# Each tool call counts under exactly one outcome, so a tool's outcomes add up to its calls:
# ok (found something), similar_only (manual comparison candidates, no verified alternatives),
# not_found (worked, found nothing), bad_request (the request was invalid),
# rate_limited (a limit turned it away) and failed (something broke here or in a service we call)
OUTCOMES = ("ok", "similar_only", "not_found", "bad_request", "rate_limited", "failed")
TOOL_COUNTS = ("calls", *OUTCOMES, "ms")
DISTRIBUTOR_EVENTS = ("sent", "cached", "rate_limited")
# From 0.10.0, on days that had any: part numbers not sent because no distributor can list them (a
# value such as "10k", a BOM placeholder, an LCSC code, non-ASCII, not 3-40 characters: search/mpn.py's
# NOT_SENT_REASONS). One a number, under the distributor it would have gone to first.
DISTRIBUTOR_SKIPPED = "skipped"
# Historical DigiKey counts from before 0.9.3: an all-digit number missed the direct lookup and
# went on to a keyword search, which found the part or didn't. Also counted in "sent".
DISTRIBUTOR_RETRY_EVENTS = ("retry_found", "retry_missed")
# Why a call counted as not_found or failed: one label a call, so a tool's labels add up to its not_found +
# failed. Only these can be stored, which keeps what users typed out of the counts and bounds the file.
REASONS = frozenset({
    # jlc_search and jlc_stock_check came back empty
    "offset_past_end", "blocked_by_library_type", "blocked_by_package", "blocked_by_min_stock", "blocked_by_several",
    "part_number_not_in_stock", "part_number_filtered_out", "words_unmatched", "no_part_type", "no_catalog_subcategory",
    "value_not_listed", "filter_ignored_or_sparse", "spec_filters_no_match", "stock_below_minimum",
    "part_number_fragment", "no_results",
    # lookups that found nothing
    "mpn_not_in_snapshot", "placeholder_mpn", "lcsc_code_as_mpn", "part_not_found", "lcsc_not_found", "board_not_found",
    "no_parts_for_query", "no_ecad_model", "no_kicad_in_archive", "no_easyeda_symbol", "no_alternatives",
    "not_sent",  # Mouser/DigiKey/part_lifecycle: no number worth a request (search/mpn.py's NOT_SENT_REASONS)
    # something failed
    "service_not_ready", "not_configured", "no_pcba_types", "query_too_complex", "board_db_failed", "jlcpcb_waf",
    "jlcpcb_unavailable", "easyeda_failed", "mouser_failed", "digikey_failed", "cse_auth_failed", "cse_lookup_failed",
    "cse_download_http_4xx", "cse_download_http_5xx", "cse_download_http", "cse_download_network",
    "cse_download_too_large", "cse_invalid_zip", "lifecycle_lookup_failed", "exception", "unexpected_error",
    "other",  # a label not listed above
})
# How the checks behind jlc_search's why_empty went
WHY_EMPTY_RESULTS = ("complete", "incomplete", "budget_exhausted_or_busy", "diagnostic_failed", "no_counterfactual")
# The services this server sends requests to, besides Mouser and DigiKey (DISTRIBUTOR_EVENTS counts
# those): JLCPCB's parts search, LCSC's product data, EasyEDA's /api/products (footprint checks),
# /api/components (symbols and footprints for pinouts) and /api/components again for land checks'
# footprint pads (its own budget), and SamacSys ComponentSearchEngine (searches and model downloads)
UPSTREAM_SOURCES = ("jlcpcb", "lcsc", "easyeda_products", "easyeda_components", "easyeda_pads", "cse")
# sent: HTTP requests our code sent, one each (a request it repeats, such as CSE's second try, counts
# again); retries: further attempts the HTTP client (wafer) made on its own for those, as it reports
# them on the reply (a request that ends in a timeout or a connection failure reports none);
# cached: answered without a request (a memory cache, the on-disk store or the seed); rate_limited: not
# sent because this server's own budget or pause for that source said no
UPSTREAM_EVENTS = ("sent", "retries", "cached", "rate_limited")
# Part numbers looked up with each distributor (from its stored answers or with a request): all of
# them, and the different ones (by mpn_key), counted through salted hashes kept in memory for the day
PARTS_ASKED = ("mouser", "digikey")
MAX_DISTINCT_PARTS = 100_000  # distinct part numbers counted a day per distributor; later ones aren't
# HTTP requests server.RateLimitMiddleware turned away (429), by RateLimitMiddleware._refusal_group():
# per_ip_rate_limit refusals by the group of the address, everyone_else at the normal limit and
# platform_ranges for the AI platforms' published addresses (Anthropic, OpenAI) at
# PLATFORM_RATE_LIMIT; server_busy (shared database pressure) and too_many_clients (the address
# table was full) regardless of address. All are in per_ip_refusals and its total (the name predates
# the last two); never stores IPs.
REFUSAL_GROUPS = ("everyone_else", "platform_ranges", "server_busy", "too_many_clients")


def _new_day() -> dict[str, Any]:
    return {"tools": {}, "hours": [0] * 24, "apps": {}, "callers": 0, "distributors": {}, "reasons": {}, "why_empty": {},
            "upstream": {}, "parts_asked": {}, "per_ip_refusals": {}, "restarts": 0}


# The fields of a day this version writes; any other field in the file is a newer version's, kept as is
_DAY_FIELDS = frozenset(_new_day())


# Far above any real count. A larger one (or 1e309, which JSON reads as infinity, or NaN) is malformed:
# int() can't take infinity or NaN, and summary()'s average time can't divide a huge one into a float.
_MAX_COUNT = 2**53


def _int(value: Any) -> int:
    """A count read from the file: 0 for anything that isn't a usable number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    if isinstance(value, float) and not math.isfinite(value):
        return 0
    return int(value) if abs(value) <= _MAX_COUNT else 0


def _dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _clean_day(day: dict) -> dict[str, Any]:
    """A day read from the file, with anything malformed dropped, so counting can't fail on it.
    Fields this version doesn't know are carried through untouched, so going back to an older
    version and forward again doesn't lose them."""
    clean = _new_day()
    for name, counts in _dict(day.get("tools")).items():
        if isinstance(counts, dict):
            clean["tools"][str(name)] = _clean_tool_counts(counts)
    for name, counts in _dict(day.get("distributors")).items():
        if isinstance(counts, dict):
            counts = {"rate_limited": counts.get("limited"), **counts}  # 0.6.3 called it "limited"
            clean["distributors"][str(name)] = {
                **{key: _int(counts.get(key)) for key in DISTRIBUTOR_EVENTS},
                **{key: _int(counts[key]) for key in (*DISTRIBUTOR_RETRY_EVENTS, DISTRIBUTOR_SKIPPED) if key in counts}}
    for name, counts in _dict(day.get("reasons")).items():
        if isinstance(counts, dict):
            clean["reasons"][str(name)] = {reason: _int(count) for reason, count in counts.items() if reason in REASONS}
    clean["why_empty"] = {result: _int(count) for result, count in _dict(day.get("why_empty")).items()
                          if result in WHY_EMPTY_RESULTS}
    for name, count in _dict(day.get("apps")).items():
        clean["apps"][str(name)] = _int(count)
    clean["callers"] = _int(day.get("callers"))
    # From 0.10.0; days saved before have none
    for name, counts in _dict(day.get("upstream")).items():
        if name in UPSTREAM_SOURCES and isinstance(counts, dict):
            clean["upstream"][name] = {key: _int(counts.get(key)) for key in UPSTREAM_EVENTS}
    for name, counts in _dict(day.get("parts_asked")).items():
        if name in PARTS_ASKED and isinstance(counts, dict):
            clean["parts_asked"][name] = {key: _int(counts.get(key)) for key in ("total", "distinct")}
    # None: not counted (a day saved before 0.10.0), so it shows as null rather than as no refusals
    refusals = day.get("per_ip_refusals")
    clean["per_ip_refusals"] = ({group: _int(count) for group, count in refusals.items() if group in REFUSAL_GROUPS}
                                if isinstance(refusals, dict) else None)
    hours = day.get("hours")
    # None: not recorded (0.6.3 had no hours), so record_call() marks the hours before it as unknown
    clean["hours"] = ([None if h is None else _int(h) for h in hours]
                      if isinstance(hours, list) and len(hours) == 24 else None)
    # None: not counted (a day saved before 0.10.0)
    clean["restarts"] = None if day.get("restarts") is None else _int(day["restarts"])
    clean.update({str(key): value for key, value in day.items() if key not in _DAY_FIELDS})
    return clean


def _clean_tool_counts(counts: dict) -> dict[str, int]:
    if "errors" in counts or "empty" in counts:
        # 0.6.3's columns: errors (any error reply), failed (raised: so far bad arguments) and empty.
        # Error replies can't be sorted after the fact, so they stay as "unsorted".
        calls, errors, raised, empty = (_int(counts.get(key)) for key in ("calls", "errors", "failed", "empty"))
        return {"calls": calls, "ok": max(0, calls - errors - raised - empty), "similar_only": 0, "not_found": empty,
                "bad_request": raised, "rate_limited": 0, "failed": 0, "ms": _int(counts.get("ms")), "unsorted": errors}
    clean = {key: _int(counts.get(key)) for key in TOOL_COUNTS}
    if "unsorted" in counts:
        clean["unsorted"] = _int(counts["unsorted"])
    return clean


class _SeenToday:
    """Which values were seen today, as salted hashes held in memory only. The salt is random and
    replaced with the first value of each new UTC day (and at every restart), so the hashes can't be
    matched with values or with another day's. At most `cap` values a day are kept; later new ones
    aren't counted."""

    def __init__(self, cap: int):
        self._cap = cap
        self._date = ""
        self._salt = b""
        self._seen: set[bytes] = set()

    def add(self, date: str, value: str) -> bool:
        """Whether value is new today (and was counted)."""
        if date != self._date:
            self._date, self._salt, self._seen = date, secrets.token_bytes(16), set()
        # surrogatepass: a part number can hold a lone surrogate (JSON's "\ud800"), which plain
        # UTF-8 can't encode
        digest = hashlib.blake2b(value.encode("utf-8", "surrogatepass"), key=self._salt, digest_size=8).digest()
        if digest in self._seen or len(self._seen) >= self._cap:
            return False
        self._seen.add(digest)
        return True


class UsageStats:
    """Today's and earlier days' counts (the last KEEP_DAYS days). Synchronous, safe for
    single-threaded asyncio."""

    def __init__(self, clock: Callable[[], float] = time.time):
        self._clock = clock
        self.path: Path | None = None
        self.ok = True  # False while writes are failing
        self.tools: set[str] | None = None  # the server's tool names; other names count as "unknown"
        self._days: dict[str, dict[str, Any]] = {}
        self._dirty = False
        self._callers = _SeenToday(MAX_CALLERS)
        self._parts = {name: _SeenToday(MAX_DISTINCT_PARTS) for name in PARTS_ASKED}

    def open(self, path: str | Path) -> None:
        """Load the counts kept in path and write them there from now on. A file that can't be
        read, or has no days, is moved aside to <path>.corrupt (replacing an older one) first, so
        the next save can't overwrite it; if it can't be moved either, nothing is written to path."""
        self.path = Path(path)
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except (OSError, ValueError, RecursionError) as e:
            if self.path.is_file():
                self._set_aside(f"unreadable ({type(e).__name__}: {e})")
            else:  # not a file (a directory, a path under a file): there's nothing to keep, and saves fail
                logger.warning(f"Usage stats file {self.path} unreadable ({e}); counting starts from 0")
            return
        days = data.get("days") if isinstance(data, dict) else None
        if not isinstance(days, dict):
            self._set_aside("has no days")
            return
        try:  # malformed values are dropped (_clean_day); anything that still fails here is corruption too
            self._days = {str(date): _clean_day(day) for date, day in days.items() if isinstance(day, dict)}
        except (ValueError, TypeError, OverflowError, RecursionError) as e:
            self._days = {}
            self._set_aside(f"unreadable ({type(e).__name__}: {e})")

    def _set_aside(self, problem: str) -> None:
        aside = self.path.with_name(self.path.name + ".corrupt")
        try:
            os.replace(self.path, aside)
        except OSError as e:
            logger.warning(f"Usage stats file {self.path} {problem}, and it can't be moved aside ({e}); counting "
                           "starts from 0, kept in memory only, so the file isn't overwritten")
            self.path = None
            return
        logger.warning(f"Usage stats file {self.path} {problem}; moved to {aside} and counting starts from 0")

    def record_start(self) -> None:
        """The server started: one more restart today (a restart resets the hashes behind callers
        and parts_asked.distinct, so those can count a caller or part twice on such a day)."""
        day = self._day()
        day["restarts"] = (day["restarts"] or 0) + 1

    def _today(self) -> str:
        return datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc).date().isoformat()

    def _day(self, date: str | None = None) -> dict[str, Any]:
        """The counts for date (default today), marked as changed."""
        date = date or self._today()
        day = self._days.get(date)
        if day is None:
            day = self._days[date] = _new_day()
            cutoff = (datetime.date.fromisoformat(date) - datetime.timedelta(days=KEEP_DAYS)).isoformat()
            for old in [d for d in self._days if d <= cutoff]:
                del self._days[old]
        if day["per_ip_refusals"] is None:  # a day saved before 0.10.0: refusals count from now on
            day["per_ip_refusals"] = {}
        self._dirty = True
        return day

    def record_call(self, tool: str, outcome: str, ms: float, caller: str | None = None,
                    reason: str | None = None) -> None:
        """One tool call. outcome is one of OUTCOMES (anything else counts as "failed"). caller is
        an IP, counted but not kept. reason says why it found nothing or failed: one of REASONS
        (anything else counts as "other"), on the same day as the call so the two add up."""
        if self.tools is not None and tool not in self.tools:
            tool = "unknown"
        now = datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc)  # one reading for date and hour
        date, hour = now.date().isoformat(), now.hour
        day = self._day(date)
        counts = day["tools"].setdefault(tool, dict.fromkeys(TOOL_COUNTS, 0))
        counts["calls"] += 1
        counts[outcome if outcome in OUTCOMES else "failed"] += 1
        counts["ms"] += round(ms)
        if reason is not None:
            reasons = day["reasons"].setdefault(tool, {})
            reason = reason if reason in REASONS else "other"
            reasons[reason] = reasons.get(reason, 0) + 1
        if day["hours"] is None:  # a day saved without hours: the ones before now are unknown
            day["hours"] = [None] * hour + [0] * (24 - hour)
        day["hours"][hour] = (day["hours"][hour] or 0) + 1
        if caller:
            self._count_caller(date, day, caller)

    def _count_caller(self, date: str, day: dict[str, Any], caller: str) -> None:
        if self._callers.add(date, caller):
            day["callers"] += 1

    def record_app(self, name: str | None) -> None:
        """An MCP app connected (the clientInfo name it sent with initialize)."""
        name = _NOT_IN_APP_NAME.sub("", str(name or "")).strip()[:APP_NAME_LENGTH] or "unknown"
        apps = self._day()["apps"]
        if name not in apps and len(apps) >= MAX_APPS:
            name = "other"
        apps[name] = apps.get(name, 0) + 1

    def record_distributor(self, name: str, event: str) -> None:
        """A Mouser/DigiKey lookup: "sent" to the API, "cached" (answered from the cache) or
        "rate_limited" (turned away by our limits or a pause the API asked for); or a part number
        "skipped" (DISTRIBUTOR_SKIPPED)."""
        counts = self._day()["distributors"].setdefault(name, dict.fromkeys(DISTRIBUTOR_EVENTS, 0))
        counts[event] = counts.get(event, 0) + 1

    def record_upstream(self, source: str, event: str, count: int = 1) -> None:
        """Requests to a service other than Mouser/DigiKey: source is one of UPSTREAM_SOURCES, event
        one of UPSTREAM_EVENTS (count: how many, for retries). Anything else isn't counted."""
        if source in UPSTREAM_SOURCES and event in UPSTREAM_EVENTS and count > 0:
            counts = self._day()["upstream"].setdefault(source, dict.fromkeys(UPSTREAM_EVENTS, 0))
            counts[event] += count

    def record_parts_asked(self, distributor: str, numbers: list[str]) -> None:
        """Part numbers a Mouser/DigiKey lookup asked for (distinct within the lookup), whether they
        were answered from the stored answers, with a request, or turned away by the limits (not
        the skipped ones, which aren't looked up at all): counted, and the ones not seen yet today
        (compared by mpn_key: case and - _ / ignored) counted as distinct. Neither the numbers nor
        their hashes are written anywhere."""
        if distributor not in PARTS_ASKED or not numbers:
            return
        from .search.mpn import mpn_key  # here: the search package is too much to load with this module

        now = datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc)
        date = now.date().isoformat()
        counts = self._day(date)["parts_asked"].setdefault(distributor, {"total": 0, "distinct": 0})
        seen = self._parts[distributor]
        for number in numbers:
            counts["total"] += 1
            if seen.add(date, mpn_key(str(number).strip())):
                counts["distinct"] += 1

    def record_refusal(self, group: str = "everyone_else") -> None:
        """One HTTP request admission control turned away (no IP is kept). group: one of
        REFUSAL_GROUPS; anything else counts as everyone_else."""
        refusals = self._day()["per_ip_refusals"]
        group = group if group in REFUSAL_GROUPS else "everyone_else"
        refusals[group] = refusals.get(group, 0) + 1

    def record_why_empty(self, result: str) -> None:
        """How the checks behind a why_empty reply went: one of WHY_EMPTY_RESULTS."""
        if result in WHY_EMPTY_RESULTS:
            counts = self._day()["why_empty"]
            counts[result] = counts.get(result, 0) + 1

    def save(self) -> None:
        """Write the counts if anything changed since the last save (atomic replace)."""
        if self.path is None or not self._dirty:
            return
        tmp = self.path.with_name(self.path.name + ".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as out:
                out.write(json.dumps({"days": self._days}, sort_keys=True))
                out.flush()
                os.fsync(out.fileno())  # on disk before it replaces the old file, so a crash can't leave it empty
            os.replace(tmp, self.path)
        except OSError as e:
            if self.ok:  # once per failure streak
                logger.warning(f"Usage stats file {self.path} not writable ({e}); counts are kept in memory only")
            self.ok = False
            return
        self.ok = True
        self._dirty = False

    def summary(self, days: int = 30) -> dict[str, Any]:
        """For /mcp/stats: totals over the newest `days` days that had any use, then each of those
        days, newest first."""
        dates = sorted(self._days, reverse=True)[:days]
        out = []
        total_tools: dict[str, dict[str, int]] = {}
        total_apps: dict[str, int] = {}
        total_distributors: dict[str, dict[str, int]] = {}
        total_reasons: dict[str, dict[str, int]] = {}
        total_why_empty: dict[str, int] = {}
        total_upstream: dict[str, dict[str, int]] = {}
        total_parts: dict[str, dict[str, int]] = {}  # totals only: distinct can't be added across days
        total_refusals: dict[str, int] = {}
        total_hours = [0] * 24
        for date in dates:
            day = self._days[date]
            for name, c in day["upstream"].items():
                total = total_upstream.setdefault(name, dict.fromkeys(UPSTREAM_EVENTS, 0))
                for key, value in c.items():
                    total[key] = total.get(key, 0) + value
            for name, c in day["parts_asked"].items():
                total = total_parts.setdefault(name, {"total": 0})
                total["total"] += c["total"]
            for group, count in (day["per_ip_refusals"] or {}).items():
                total_refusals[group] = total_refusals.get(group, 0) + count
            for hour, count in enumerate(day["hours"] or ()):
                total_hours[hour] += count or 0
            for name, c in day["tools"].items():
                total = total_tools.setdefault(name, {})
                for key, value in c.items():
                    total[key] = total.get(key, 0) + value
            for name, count in day["apps"].items():
                total_apps[name] = total_apps.get(name, 0) + count
            for name, c in day["distributors"].items():
                total = total_distributors.setdefault(name, dict.fromkeys(DISTRIBUTOR_EVENTS, 0))
                for key, value in c.items():
                    total[key] = total.get(key, 0) + value
            for name, c in day["reasons"].items():
                total = total_reasons.setdefault(name, {})
                for reason, count in c.items():
                    total[reason] = total.get(reason, 0) + count
            for result, count in day["why_empty"].items():
                total_why_empty[result] = total_why_empty.get(result, 0) + count
            tools = _tools_view(day["tools"])
            out.append({
                "date": date,
                "calls": sum(c["calls"] for c in tools.values()),
                "hours": day["hours"],
                "callers": day["callers"],
                "tools": tools,
                "apps": _by_count(day["apps"]),
                "distributors": day["distributors"],
                "reasons": _reasons_view(day["reasons"]),
                "why_empty": _by_count(day["why_empty"]),
                "upstream": _upstream_view(day["upstream"]),
                "parts_asked": dict(sorted(day["parts_asked"].items())),
                "per_ip_refusals": _refusals_view(day["per_ip_refusals"]),
                "restarts": day["restarts"],
            })
        totals_tools = _tools_view(total_tools)
        return {
            "about": ("Anonymous counts per UTC day, the last 30 days at most, newest first; totals adds up "
                      "the days listed (without callers, which can't be added across days). hours: calls in each UTC hour, "
                      "00 to 23 (null: not recorded); in totals, each hour added up across the days. Each tool's calls = ok (found "
                      "something; for alternatives, verified replacements) + similar_only (only similar parts for manual "
                      "comparison, no verified replacements) + not_found (worked, found nothing) + bad_request (the request was invalid) + "
                      "rate_limited (a limit turned it away) + failed (something broke on this server or a service "
                      "it calls), plus unsorted where shown (error replies from before 0.6.4, which weren't "
                      "sorted). callers counts distinct IPs, which isn't the number of people: hosted apps such "
                      "as claude.ai call from their own servers' IPs, and a caller seen before and after a restart "
                      "counts twice. apps are the names MCP apps send when they connect. The stats keep no IPs, "
                      "queries or part numbers. Cutover 2026-10-26: alternatives replies before that date counted "
                      "similar-parts-only replies as not found; historical counts have not been reclassified. reasons (from 0.9.0; "
                      "earlier days have none): for each tool, why calls came back not_found or failed, one fixed label a "
                      "call. why_empty: how the checks behind jlc_search's why_empty went (no_counterfactual: no library, "
                      "package or stock limit to test). distributors retry_found and retry_missed: before 0.9.3, DigiKey all-digit "
                      "numbers that missed the direct lookup and went on to a keyword search, also counted in sent. "
                      "distributors skipped (from 0.10.0, on days with any): part numbers not sent because no "
                      "distributor can list them (a value such as 10k, a BOM placeholder, an LCSC code, non-ASCII "
                      "text, not 3-40 characters); one a number. "
                      "From 0.10.0 (earlier days have none): upstream, for each service this server calls other than "
                      "Mouser and DigiKey (those are in distributors): jlcpcb (parts search), lcsc (product data), "
                      "easyeda_products (footprint checks), easyeda_components (symbols and footprints for pinouts), "
                      "easyeda_pads (footprint pads for land checks) and cse (SamacSys searches and model downloads); "
                      "sent is HTTP requests sent, one each, not tool calls; retries the further attempts the HTTP "
                      "client made on its own for them, where it reports them (a timeout reports none); cached "
                      "answers given without a request (memory cache, on-disk store or seed); rate_limited requests "
                      "this server's own budget or pause for that service kept back. parts_asked: part numbers "
                      "asked for with Mouser and DigiKey, whether stored answers gave them, a request did or the "
                      "limits turned them away (total; skipped ones aren't counted), and how many "
                      "were different that day (distinct, ignoring case and - _ /; counted through salted hashes "
                      "held in memory, so a restart counts them again; not in totals, which can't add them across "
                      "days). per_ip_refusals: HTTP requests admission control turned away (429): total (all "
                      "of the groups) and by group: per-address rate limit refusals by address group "
                      "(platform_ranges: addresses in the AI platforms' published ranges, which have a "
                      "higher limit; everyone_else: every other caller), then, regardless of address, "
                      "server_busy (shared database queue pressure) and too_many_clients (the server was "
                      "tracking as many addresses as it can); null on days before it was counted. "
                      "restarts (from 0.10.0; null before): how many times the server started that day; "
                      "callers and parts_asked distinct count a caller or part seen on both sides of a "
                      "restart twice."),
            "kept_across_restarts": self.path is not None and self.ok,
            "totals": {
                "from": dates[-1] if dates else None,
                "to": dates[0] if dates else None,
                "days": len(dates),
                "calls": sum(c["calls"] for c in totals_tools.values()),
                "hours": total_hours,
                "tools": totals_tools,
                "apps": _by_count(total_apps),
                "distributors": total_distributors,
                "reasons": _reasons_view(total_reasons),
                "why_empty": _by_count(total_why_empty),
                "upstream": _upstream_view(total_upstream),
                "parts_asked": dict(sorted(total_parts.items())),
                "per_ip_refusals": _refusals_view(total_refusals),
            },
            "days": out,
        }


def _tools_view(tools: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    """Tool counts as shown: the outcomes, unsorted when there is any, and the average time; busiest first."""
    return {
        name: {"calls": c["calls"], **{key: c.get(key, 0) for key in OUTCOMES},
               **({"unsorted": c["unsorted"]} if c.get("unsorted") else {}),
               "avg_ms": round(c["ms"] / c["calls"]) if c["calls"] else 0}
        for name, c in sorted(tools.items(), key=lambda item: (-item[1]["calls"], item[0]))
    }


def _upstream_view(upstream: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    """Each source's counts, in UPSTREAM_SOURCES order."""
    return {name: upstream[name] for name in UPSTREAM_SOURCES if name in upstream}


def _refusals_view(refusals: dict[str, int] | None) -> dict[str, int] | None:
    """The day's (or days') refusals: total, then each group; None when not counted."""
    if refusals is None:
        return None
    return {"total": sum(refusals.values()), **{group: refusals.get(group, 0) for group in REFUSAL_GROUPS}}


def _reasons_view(reasons: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    """Each tool's reasons, commonest first, tools in name order."""
    return {name: _by_count(counts) for name, counts in sorted(reasons.items())}


def _by_count(counts: dict[str, int]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


# The server's counts. Modules use stats.usage (not `from .stats import usage`) so tests can swap it.
usage = UsageStats()


# Counting never breaks a lookup: the clients call these instead of usage's methods
def count_distributor(name: str, event: str) -> None:
    try:
        usage.record_distributor(name, event)
    except Exception:
        logger.exception("Usage stats: couldn't count a distributor lookup")


def count_parts_asked(distributor: str, numbers: list[str]) -> None:
    try:
        usage.record_parts_asked(distributor, numbers)
    except Exception:
        logger.exception("Usage stats: couldn't count the part numbers asked")


def count_upstream(source: str, event: str, count: int = 1) -> None:
    try:
        usage.record_upstream(source, event, count)
    except Exception:
        logger.exception("Usage stats: couldn't count an upstream request")
