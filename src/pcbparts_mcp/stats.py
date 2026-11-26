"""Private usage counts per UTC day, served with bearer auth at /mcp/stats.

Per day: calls to each tool, split by outcome (see OUTCOMES), with the average time; calls in each UTC
hour; the MCP apps that connected (by the name each app reports when it connects), the number of distinct
callers, and what happened to Mouser/DigiKey lookups (sent, answered from the cache, or turned away
by the shared limits). For calls that found nothing or failed, the reason, from a fixed list of labels
(REASONS); and how the checks behind jlc_search's why_empty went. From 0.10.0 also the requests sent to
the other services we call and the answers their caches saved (UPSTREAM_SOURCES), how many part numbers
were looked up with Mouser and DigiKey and how many of them were different, and the HTTP requests the
rate limit turned away (and, in 0.10.0 only, the busy cap). From 0.10.1 also the failed calls and the turned-away requests
in each UTC hour. From 0.10.2 also how LCSC-code lookups were answered (snapshot, live or a
fallback), and which apps called the Mouser and DigiKey tools (distributor_apps; server.py links a
call to its app in memory). From 0.10.3 also why distributor lookups were held back, in each UTC
hour, and the limits distributors themselves refused for (distributor_limits). From 0.10.4 also
part_lifecycle input forms per entry (lifecycle_inputs). From 0.10.5 also bad_request_reasons
(separate from reasons), tool_apps (every outcome per app and tool), latency histograms and
bucket-bound percentiles (excluding bad_request and rate_limited), versions (starts per version),
upstream_status (one HTTP/transport class per sent request), and popular_terms (query tokens seen
from at least 10 distinct callers that UTC day, top 200); all null on days saved before.
tool_apps, latency and popular_terms keep only the last RECENT_DAYS days; older days are cleared on rollover, load,
save and summary. Today's tool_apps keeps MAX_APPS names; past days keep the busiest MAX_TOOL_APPS - 1
plus other, summing all outcomes from the remaining apps.
Call-local notes carry label-only facts from tools, including offloaded ones, without altering replies.
Cutovers in 0.10.5: Mouser misses become part_not_found; jlc_stock_check's otherwise-unlabelled
no_results splits into no_results_filtered, no_results_part_number and no_results_words;
jlc_search's historical part_number_not_in_stock becomes part_number_sold_out or part_number_unknown.
Retired labels remain valid.
Failed calls are also accumulated in memory and logged once per UTC minute, labels only.
No IPs or whole queries are kept. Below-threshold tokens are never written; their caller hashes
use a random daily/restart salt, capped at 10 per token and 20,000 tokens a day. Platform addresses
all count as one caller. Already-retained tokens keep their count through a same-day restart;
new tokens must reach the threshold again. Callers and distinct part
numbers are counted through salted hashes held in memory for the current day only, with a new random salt each
day. A restart starts a new set, so a caller or part seen before and after one on the same day counts
twice; each day's `restarts` (from 0.10.0) says how many there were.

The server writes the counts to USAGE_STATS_PATH (a JSON file on the cache volume) every minute and
at shutdown; unset means memory only. The file keeps a year; /mcp/stats defaults to 30 days, up to a year. Nothing
here raises on a bad or unwritable file, like QuotaStore: a file that can't be read is moved aside
(USAGE_STATS_PATH.corrupt, one kept until its mtime is over 30 days old) before counting starts
from 0, so the next save can't overwrite it. Stats and their temporary/backup files are 0600.
A day's fields this version doesn't know (a newer version's) are kept as they are.
"""

import asyncio
import contextvars
import datetime
import hashlib
import ipaddress
import json
import logging
import math
import os
import re
import secrets
import time
from pathlib import Path
from typing import Any, Callable

from . import __version__
from .config import DB_WAIT_COUNTED_SECONDS
from .private_files import private_open

logger = logging.getLogger(__name__)

KEEP_DAYS = 365  # daily aggregates; tool_apps, latency and popular_terms keep only RECENT_DAYS
RECENT_DAYS = 30  # retention for app-by-tool, latency and popular-term detail
MAX_TOOL_APPS = 15  # compacted past days: includes the reserved overflow name "other"
# From 0.10.5; daily, null before. Only calls that did work contribute to latency.
LATENCY_BOUNDS_MS = (50, 100, 250, 500, 1000, 2500, 5000, 10000, 30000, 60000)
LATENCY_OUTCOMES = ("ok", "similar_only", "not_found", "failed")
# From 0.10.5: one fixed HTTP/transport class per sent request; null on earlier days.
UPSTREAM_STATUS_CLASSES = ("2xx", "3xx", "4xx", "429", "5xx", "timeout", "connection", "challenge",
                           "too_large", "cancelled", "other_error")
# From 0.10.5: separate from REASONS; declared argument names plus these fixed types only.
BAD_REQUEST_REASONS = frozenset({
    "category_not_found", "too_long", "too_many", "invalid_value", "unsupported_exclusion", "strict_unmet",
    "unsupported_value", "unsupported_sort", "missing_argument", "invalid_lcsc", "query_unsearchable",
    "invalid_id", "all_inputs_invalid", "unknown_tool", "other",
})
ARG_ERROR_TYPES = ("missing", "extra_forbidden", "int_parsing", "int_type", "float_parsing", "string_type",
                   "bool_parsing", "list_type", "literal_error", "enum", "greater_than_equal", "less_than_equal",
                   "greater_than", "less_than", "string_too_long", "string_too_short", "too_long", "too_short",
                   "value_error", "json_invalid", "missing_argument", "unexpected_keyword_argument",
                   "unexpected_positional_argument", "multiple_argument_values", "missing_keyword_only_argument",
                   "missing_positional_only_argument")
_ARG_REASON = re.compile(r"arg:([A-Za-z_][A-Za-z0-9_]{0,63}):(" + "|".join((*ARG_ERROR_TYPES, "other")) + r")\Z")
# From 0.10.5: server starts by short version-like tag; null on earlier days.
_VERSION = re.compile(r"(?=.{1,32}\Z)[0-9]+(?:\.[0-9]+){1,3}(?:[A-Za-z0-9.+_-]*)\Z")
SINCE_0_10_5 = ("bad_request_reasons", "tool_apps", "latency", "versions", "upstream_status", "popular_terms")
QUERY_TOOLS = frozenset({"jlc_search", "jlc_stock_check", "cse_search", "board_search", "sensor_recommend"})
POPULAR_CALLERS = 10
MAX_POPULAR_TOKENS = 20_000
MAX_POPULAR_TERMS = 200
_TERM_SPLIT = re.compile(r"[\s,;|()\[\]{}\"'<>]+")
_TERM_EDGES = ".-_/ :+*#!?=&"
_STOP_WORDS = frozenset("a an the and or for with of to in on at by from".split())


def query_tokens(query: Any) -> list[str]:
    """At most 20 distinct normalized tokens; phrases and the English stop list are omitted."""
    if not isinstance(query, str):
        return []
    text = query.replace("µ", "u").replace("μ", "u").replace("Ω", "ohm").casefold()
    tokens = {}
    for part in _TERM_SPLIT.split(text):
        token = part.strip(_TERM_EDGES)
        if 2 <= len(token) <= 40 and token not in _STOP_WORDS:
            tokens[token] = None
            if len(tokens) == 20:
                break
    return list(tokens)


def _top_terms(counts: dict[str, int]) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:MAX_POPULAR_TERMS])

MAX_CALLERS = 100_000  # distinct callers counted a day (bounds memory); later ones aren't counted
MAX_APPS = 50  # distinct app names a day; later ones count as "other"
APP_NAME_LENGTH = 40
_NOT_IN_APP_NAME = re.compile(r"[^A-Za-z0-9 ._()/+-]")  # app names are self-reported
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
    # From 0.10.5; keep no_results and part_number_not_in_stock for historical days.
    "no_results_filtered", "no_results_part_number", "no_results_words", "part_number_sold_out", "part_number_unknown",
    # lookups that found nothing
    "mpn_not_in_snapshot", "placeholder_mpn", "lcsc_code_as_mpn", "part_not_found", "lcsc_not_found", "board_not_found",
    "no_parts_for_query", "no_ecad_model", "no_kicad_in_archive", "no_easyeda_symbol", "no_alternatives",
    "not_sent",  # Mouser/DigiKey/part_lifecycle: no number worth a request (search/mpn.py's NOT_SENT_REASONS)
    # something failed
    "service_not_ready", "not_configured", "no_pcba_types", "query_too_complex", "board_db_failed", "jlcpcb_waf",
    "jlcpcb_unavailable", "easyeda_failed", "mouser_failed", "digikey_failed", "cse_auth_failed", "cse_lookup_failed",
    "cse_download_http_4xx", "cse_download_http_5xx", "cse_download_http", "cse_download_network",
    "cse_download_too_large", "cse_invalid_zip", "cse_download_refused", "lifecycle_lookup_failed", "exception", "unexpected_error",
    "other",  # a label not listed above
})
# How the checks behind jlc_search's why_empty went
WHY_EMPTY_RESULTS = ("complete", "incomplete", "budget_exhausted_or_busy", "diagnostic_failed", "no_counterfactual")
# The services this server sends requests to: JLCPCB's parts search, LCSC's product data, EasyEDA's
# /api/products (footprint checks), /api/components (symbols and footprints for pinouts) and
# /api/components again for land checks' footprint pads (its own budget), SamacSys
# ComponentSearchEngine (searches and model downloads), and from 0.10.4 the HTTP requests behind
# DigiKey lookups (DISTRIBUTOR_EVENTS counts Mouser and DigiKey per lookup)
UPSTREAM_SOURCES = ("jlcpcb", "lcsc", "easyeda_products", "easyeda_components", "easyeda_pads", "cse", "digikey")
# Mouser's sends are counted in distributors; adding it to UPSTREAM_SOURCES would double-count them.
# Mouser's sends/retries remain in distributors; from 0.10.9 its HTTP outcomes are counted too.
UPSTREAM_STATUS_SOURCES = (*UPSTREAM_SOURCES, "mouser")
# sent: HTTP requests our code sent, one each (a request it repeats, such as CSE's second try, counts
# again); retries: further attempts the HTTP client (wafer) made on its own for those, as it reports
# them on the reply (a request that ends in a timeout or a connection failure reports none);
# cached: answered without a request (a memory cache, the on-disk store or the seed); rate_limited: not
# sent because this server's own budget or pause for that source said no; waited (from 0.10.4): sent
# after waiting for a free slot under this server's cap on requests in flight
UPSTREAM_EVENTS = ("sent", "retries", "cached", "rate_limited", "waited")
# Part numbers looked up with each distributor (from its stored answers or with a request): all of
# them, and the different ones (by mpn_key), counted through salted hashes kept in memory for the day
PARTS_ASKED = ("mouser", "digikey")
MAX_DISTINCT_PARTS = 100_000  # distinct part numbers counted a day per distributor; later ones aren't
# HTTP requests server.RateLimitMiddleware turned away (429), by RateLimitMiddleware._refusal_group():
# per_ip_rate_limit refusals by the group of the address, everyone_else at the normal limit and
# platform_ranges for the AI platforms' published addresses (Anthropic, OpenAI) at
# PLATFORM_RATE_LIMIT; too_many_clients (the address table was full) regardless of address.
# server_busy holds 0.10.0's busy-cap refusals: the cap was removed in 0.10.1 and nothing counts
# there now, but days already stored keep their counts, shown and added into totals (always 0 on
# later days). All are in per_ip_refusals and its total; never stores IPs.
REFUSAL_GROUPS = ("everyone_else", "platform_ranges", "server_busy", "too_many_clients")
# From 0.10.1, per UTC hour like hours: failed_hours, the tool calls whose outcome was failed, and
# refused_hours, the requests counted in per_ip_refusals (every group), so a burst can be placed in
# the day (before or after a deploy, say). None on a day saved before 0.10.1; on the day it started,
# None for the hours before that.
HOURLY_SINCE_0_10_1 = ("failed_hours", "refused_hours")
# From 0.10.2, per day (None on days saved before): how the LCSC-code lookups of jlc_get_part, and
# jlc_stock_check's one-code queries, were answered, one event a lookup: snapshot (from the database,
# no request), live (a live lookup answered, found or not, including its 1-hour cache), fallback
# (JLCPCB didn't answer; the database did, live_failed) and live_failed (the live lookup failed and
# nothing answered instead: the error)
LCSC_LOOKUP_TOOLS = ("jlc_get_part", "jlc_stock_check")
LCSC_LOOKUP_EVENTS = ("snapshot", "live", "fallback", "live_failed")
# From 0.10.2, per day (None on days saved before): calls to the tools that ask Mouser and DigiKey,
# by app (the name it sent with initialize, cleaned and capped per tool as in apps): calls, and how
# many of them were rate_limited (the call's outcome). A stateless server's tools/call carries no
# app name, so server.AppsByAddress links a call to the app its address last connected with, kept
# APP_LINK_MINUTES from that address's last initialize or call; none: "unknown".
DISTRIBUTOR_TOOLS = ("mouser_get_part", "digikey_get_part", "part_lifecycle")
DISTRIBUTOR_APP_COUNTS = ("calls", "rate_limited")
APP_LINK_MINUTES = 10
# From 0.10.3: fixed, anonymous labels only, never an app/key number or a per-key count.
DISTRIBUTOR_LIMIT_CAUSES = ("minute_cap", "daily_count", "address_daily", "address_blocked", "distributor_daily",
                            "distributor_minute", "distributor_refused", "other")
DISTRIBUTOR_LIMIT_REFUSALS = ("daily", "minute", "refused")
DATASHEET_LINK_EVENTS = ("visits", "reused", "signed", "waited", "refused", "failed", "not_found")
LIFECYCLE_INPUT_FORMS = ("bare_number", "with_manufacturer", "lcsc_code")


# A fresh shared dict per call: copy_context() in db_worker carries it into offloaded tools.
call_notes: contextvars.ContextVar[dict[str, Any] | None] = contextvars.ContextVar("usage_call_notes", default=None)


def note(**facts: Any) -> None:
    """Hand counting facts to the middleware without changing a tool's reply."""
    try:
        notes = call_notes.get()
        if notes is not None:
            notes.update(facts)
    except Exception:
        logger.exception("Usage stats: couldn't note call facts")


def _valid_bad_request_reason(label: str) -> bool:
    return label in BAD_REQUEST_REASONS or bool(_ARG_REASON.fullmatch(label))


def _new_distributor_limits() -> dict[str, Any]:
    return {"held_back": dict.fromkeys(DISTRIBUTOR_LIMIT_CAUSES, 0), "held_back_hours": [0] * 24,
            "refusals": dict.fromkeys(DISTRIBUTOR_LIMIT_REFUSALS, 0)}


def _new_db_waits(*, components: bool = True) -> dict[str, Any]:
    return {"jobs": 0, "waited": 0, "longest_ms": 0, "waited_hours": [0] * 24, "longest_ms_hours": [0] * 24,
            **({"components": _new_db_waits(components=False)} if components else {})}


def _clean_db_waits(value: Any, *, components: bool = True) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    clean = {key: max(0, _int(value.get(key))) for key in ("jobs", "waited", "longest_ms")}
    for field in ("waited_hours", "longest_ms_hours"):
        clean[field] = [max(0, h or 0) for h in (_hours(value.get(field)) or [0] * 24)]
    if components:
        clean["components"] = _clean_db_waits(value.get("components"), components=False) or _new_db_waits(components=False)
    return clean


def _add_db_waits(total: dict[str, Any], counts: dict[str, Any]) -> None:
    for field in ("jobs", "waited"):
        total[field] += counts[field]
    total["longest_ms"] = max(total["longest_ms"], counts["longest_ms"])
    for hour in range(24):
        total["waited_hours"][hour] += counts["waited_hours"][hour]
        total["longest_ms_hours"][hour] = max(total["longest_ms_hours"][hour], counts["longest_ms_hours"][hour])
    if "components" in counts:
        _add_db_waits(total["components"], counts["components"])


def _new_day() -> dict[str, Any]:
    return {"tools": {}, "hours": [0] * 24, "apps": {}, "callers": 0, "distributors": {}, "reasons": {}, "why_empty": {},
            "upstream": {}, "parts_asked": {}, "per_ip_refusals": {}, "restarts": 0,
            **{field: [0] * 24 for field in HOURLY_SINCE_0_10_1}, "lcsc_lookups": {}, "distributor_apps": {},
            "distributor_limits": {}, "datasheet_links": dict.fromkeys(DATASHEET_LINK_EVENTS, 0),
            "db_waits": _new_db_waits(), "lifecycle_inputs": dict.fromkeys(LIFECYCLE_INPUT_FORMS, 0),
            **{field: {} for field in SINCE_0_10_5}}


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


def _hours(value: Any) -> list[int | None] | None:
    """24 counts per UTC hour read from the file (None in it: that hour wasn't recorded); None
    for anything else (not recorded that day)."""
    return [None if h is None else _int(h) for h in value] if isinstance(value, list) and len(value) == 24 else None


def _clean_day(day: dict) -> dict[str, Any]:
    """A day read from the file, with anything malformed dropped, so counting can't fail on it.
    Fields this version doesn't know are carried through untouched, so going back to an older
    version and forward again doesn't lose them."""
    clean = _new_day()
    # From 0.10.5: additive-null, independently validated before tool parameters are known.
    for field in SINCE_0_10_5:
        clean[field] = {} if isinstance(day.get(field), dict) else None
    for tool, labels in _dict(day.get("bad_request_reasons")).items():
        if isinstance(labels, dict):
            clean["bad_request_reasons"][str(tool)] = {
                label: max(0, _int(count)) for label, count in labels.items() if _valid_bad_request_reason(label)}
    for tool, apps in _dict(day.get("tool_apps")).items():
        if isinstance(apps, dict):
            target = clean["tool_apps"][str(tool)] = {}
            for app, counts in apps.items():
                if isinstance(counts, dict):
                    name = _tool_app_name(target, app)
                    dest = target.setdefault(name, {"calls": 0})
                    for key in ("calls", *OUTCOMES):
                        count = max(0, _int(counts.get(key)))
                        if count:
                            dest[key] = dest.get(key, 0) + count
    for tool, counts in _dict(day.get("latency")).items():
        if isinstance(counts, list) and len(counts) == len(LATENCY_BOUNDS_MS) + 1:
            clean["latency"][str(tool)] = [max(0, _int(count)) for count in counts]
    for version, count in _dict(day.get("versions")).items():
        if _VERSION.fullmatch(version):
            clean["versions"][version] = max(0, _int(count))
    for source, counts in _dict(day.get("upstream_status")).items():
        if source in UPSTREAM_STATUS_SOURCES and isinstance(counts, dict):
            clean["upstream_status"][source] = {label: max(0, _int(count)) for label, count in counts.items()
                                                 if label in UPSTREAM_STATUS_CLASSES}
    if clean["popular_terms"] is not None:
        clean["popular_terms"] = _top_terms({token: _int(count) for token, count in day["popular_terms"].items()
                                             if query_tokens(token) == [token] and _int(count) > 0})
    for name, counts in _dict(day.get("tools")).items():
        if isinstance(counts, dict):
            clean["tools"][str(name)] = _clean_tool_counts(counts)
    for name, counts in _dict(day.get("distributors")).items():
        if isinstance(counts, dict):
            counts = {"rate_limited": counts.get("limited"), **counts}  # 0.6.3 called it "limited"
            clean["distributors"][str(name)] = {
                **{key: _int(counts.get(key)) for key in DISTRIBUTOR_EVENTS},
                **{key: _int(counts[key]) for key in (*DISTRIBUTOR_RETRY_EVENTS, DISTRIBUTOR_SKIPPED, "retries") if key in counts}}
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
    # None: not recorded (0.6.3 had no hours), so record_call() marks the hours before it as unknown
    clean["hours"] = _hours(day.get("hours"))
    # None: not recorded (a day saved before 0.10.1), so _day() marks the hours before now as unknown
    for field in HOURLY_SINCE_0_10_1:
        clean[field] = _hours(day.get(field))
    # None: not counted (a day saved before 0.10.0)
    clean["restarts"] = None if day.get("restarts") is None else _int(day["restarts"])
    # None: not counted (a day saved before 0.10.2), shown as null rather than as no lookups
    lookups = day.get("lcsc_lookups")
    clean["lcsc_lookups"] = ({name: {event: _int(counts.get(event)) for event in LCSC_LOOKUP_EVENTS}
                              for name, counts in lookups.items()
                              if name in LCSC_LOOKUP_TOOLS and isinstance(counts, dict)}
                             if isinstance(lookups, dict) else None)
    # None: not counted (a day saved before 0.10.2)
    by_tool = day.get("distributor_apps")
    clean["distributor_apps"] = ({tool: {str(app): {key: _int(counts.get(key)) for key in DISTRIBUTOR_APP_COUNTS}
                                         for app, counts in apps.items() if isinstance(counts, dict)}
                                  for tool, apps in by_tool.items()
                                  if tool in DISTRIBUTOR_TOOLS and isinstance(apps, dict)}
                                 if isinstance(by_tool, dict) else None)
    # None: not counted (a day saved before 0.10.3). Drop unknown names and labels on load.
    limits = day.get("distributor_limits")
    clean["distributor_limits"] = ({name: {
        "held_back": {label: _int(_dict(counts.get("held_back")).get(label)) for label in DISTRIBUTOR_LIMIT_CAUSES},
        "held_back_hours": [h or 0 for h in (_hours(counts.get("held_back_hours")) or [0] * 24)],
        "refusals": {label: _int(_dict(counts.get("refusals")).get(label)) for label in DISTRIBUTOR_LIMIT_REFUSALS}}
        for name, counts in limits.items() if name in PARTS_ASKED and isinstance(counts, dict)}
        if isinstance(limits, dict) else None)
    links = day.get("datasheet_links")
    clean["datasheet_links"] = ({event: _int(links.get(event)) for event in DATASHEET_LINK_EVENTS}
                                if isinstance(links, dict) else None)
    clean["db_waits"] = _clean_db_waits(day.get("db_waits"))
    forms = day.get("lifecycle_inputs")
    clean["lifecycle_inputs"] = ({form: max(0, _int(forms.get(form))) for form in LIFECYCLE_INPUT_FORMS}
                                  if isinstance(forms, dict) else None)
    clean.update({str(key): value for key, value in day.items() if key not in _DAY_FIELDS})
    return clean


def clean_app_name(name: Any) -> str:
    """An app's self-reported name (its clientInfo name) as kept in private counts: only plain
    characters, at most APP_NAME_LENGTH; "unknown" for none."""
    return _NOT_IN_APP_NAME.sub("", str(name or "")).strip()[:APP_NAME_LENGTH] or "unknown"


def popularity_caller(caller: str | None, *, platform: bool = False) -> str | None:
    """Popularity heuristic, not an anonymity guarantee: one platform or IPv6 /48 per caller."""
    if platform:
        return "platform"
    if caller and ":" in caller:
        try:
            return str(ipaddress.ip_network(caller.split("/", 1)[0] + "/48", strict=False))
        except ValueError:
            pass
    return caller


def _capped(apps: dict, name: str) -> str:
    """name, or "other" once apps has MAX_APPS names and name isn't one of them."""
    return "other" if name not in apps and len(apps) >= MAX_APPS else name


def _tool_app_name(apps: dict, app: Any) -> str:
    name = clean_app_name(app)
    return "other" if name not in apps and len(apps) - ("other" in apps) >= MAX_APPS else name


def _compact_tool_apps(apps: dict) -> bool:
    """Keep a past day's busiest named apps, folding every count from the rest into other."""
    if len(apps) - ("other" in apps) <= MAX_TOOL_APPS - 1:
        return False
    names = sorted((name for name in apps if name != "other"), key=lambda name: (-apps[name]["calls"], name))
    other = apps.setdefault("other", {"calls": 0})
    for name in names[MAX_TOOL_APPS - 1:]:
        for key, count in apps.pop(name).items():
            other[key] = other.get(key, 0) + count
    return True


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
        # Retention must survive disabling writes to protect an unreadable original.
        self._retention_path: Path | None = None
        self._aside_problem: str | None = None
        self.ok = True  # False while writes are failing
        self.tools: set[str] | None = None  # the server's tool names; other names count as "unknown"
        self.tool_params: dict[str, set[str]] = {}  # declared names only, from list_tools at startup
        self._failed_minutes: dict[str, dict[tuple[str, str], int]] = {}
        self._days: dict[str, dict[str, Any]] = {}
        self._dirty = False
        self._closed_json: dict[str, str] = {}
        self._callers = _SeenToday(MAX_CALLERS)
        self._parts = {name: _SeenToday(MAX_DISTINCT_PARTS) for name in PARTS_ASKED}
        self._term_date = ""
        self._term_salt = b""
        self._term_base: dict[str, int] = {}
        self._terms: dict[str, tuple[int, set[bytes]]] = {}

    def open(self, path: str | Path) -> None:
        """Load the counts kept in path and write them there from now on. A file that can't be
        read, or has no days, is moved aside to <path>.corrupt (replacing an older one) first, so
        the next save can't overwrite it; if it can't be moved either, nothing is written to path
        until hourly maintenance can move it safely."""
        self.path = self._retention_path = Path(path)
        self._aside_problem = None
        self._closed_json.clear()
        self.prune()
        try:
            for source in (self.path, self.path.with_name(self.path.name + ".tmp"),
                           self.path.with_name(self.path.name + ".corrupt")):
                if source.is_file():
                    source.chmod(0o600)
        except OSError as exc:
            self._save_failed(exc)
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
            self._maintain_recent(self._now())
        except (ValueError, TypeError, OverflowError, RecursionError) as e:
            self._days = {}
            self._set_aside(f"unreadable ({type(e).__name__}: {e})")

    def _set_aside(self, problem: str) -> None:
        self._aside_problem = problem
        self.path = None  # never overwrite the original before it has been moved safely
        self.prune()

    def prune(self) -> None:
        """Retry a blocked set-aside; expire unreadable backups after 30 days by mtime."""
        path = self._retention_path
        if path is None:
            return
        aside = path.with_name(path.name + ".corrupt")
        if self._aside_problem is not None:
            try:
                path.chmod(0o600)
                os.replace(path, aside)
            except OSError as exc:
                logger.warning(f"Usage stats file {path} {self._aside_problem}, and it can't be moved aside ({exc}); "
                               "counts stay in memory so the file isn't overwritten; will retry")
                self.ok = False
                self._dirty = True
            else:
                logger.warning(f"Usage stats file {path} {self._aside_problem}; moved to {aside}")
                self._aside_problem = None
                self.path = path
        try:
            if aside.stat().st_mtime < self._clock() - RECENT_DAYS * 86400:
                aside.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            logger.warning("Usage stats: couldn't prune corrupt backup (%s)", type(exc).__name__)

    def record_start(self) -> None:
        """The server started: one more restart today (a restart resets the hashes behind callers
        and parts_asked.distinct, so those can count a caller or part twice on such a day)."""
        day = self._day()
        day["restarts"] = (day["restarts"] or 0) + 1
        day["versions"][__version__] = day["versions"].get(__version__, 0) + 1

    def _now(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc)

    def _maintain_recent(self, now: datetime.datetime) -> None:
        """Expire days and recent detail even when no calls arrive or today was loaded from disk."""
        today = now.date().isoformat()
        keep_cutoff = (now.date() - datetime.timedelta(days=KEEP_DAYS)).isoformat()
        for old in [date for date in self._days if date <= keep_cutoff]:
            del self._days[old]
            self._closed_json.pop(old, None)
            self._dirty = True
        cutoff = (now.date() - datetime.timedelta(days=RECENT_DAYS)).isoformat()
        for date, day in self._days.items():
            if date <= cutoff:
                for field in ("tool_apps", "latency", "popular_terms"):
                    if day[field] is not None:
                        day[field] = None
                        self._dirty = True
                        self._closed_json.pop(date, None)
            elif date < today:
                for apps in (day["tool_apps"] or {}).values():
                    if _compact_tool_apps(apps):
                        self._dirty = True
                        self._closed_json.pop(date, None)

    def _day(self, now: datetime.datetime | None = None) -> dict[str, Any]:
        """The counts for now's UTC day (default: the clock's now), marked as changed. Callers that
        also need the hour pass the same reading, so a call just before midnight can't land on one
        day and another day's hour."""
        now = now or self._now()
        date = now.date().isoformat()
        day = self._days.get(date)
        if day is None:
            day = self._days[date] = _new_day()
            self._maintain_recent(now)
        for field in SINCE_0_10_5:
            if day[field] is None:
                day[field] = {}
        if day["per_ip_refusals"] is None:  # a day saved before 0.10.0: refusals count from now on
            day["per_ip_refusals"] = {}
        if day["lcsc_lookups"] is None:  # a day saved before 0.10.2: lookups count from now on
            day["lcsc_lookups"] = {}
        if day["distributor_apps"] is None:  # likewise
            day["distributor_apps"] = {}
        if day["distributor_limits"] is None:  # a day saved before 0.10.3: count from now on
            day["distributor_limits"] = {}
        if day["datasheet_links"] is None:
            day["datasheet_links"] = dict.fromkeys(DATASHEET_LINK_EVENTS, 0)
        if day["db_waits"] is None:
            day["db_waits"] = _new_db_waits()
        if day["lifecycle_inputs"] is None:
            day["lifecycle_inputs"] = dict.fromkeys(LIFECYCLE_INPUT_FORMS, 0)
        for field in HOURLY_SINCE_0_10_1:
            if day[field] is None:  # a day saved before 0.10.1: the hours before this one are unknown
                day[field] = [None] * now.hour + [0] * (24 - now.hour)
        self._dirty = True
        self._closed_json.pop(date, None)
        return day

    def record_call(self, tool: str, outcome: str, ms: float, caller: str | None = None,
                    reason: str | None = None, app: str | None = None,
                    bad_request_reason: str | None = None) -> None:
        """One tool call. outcome is one of OUTCOMES (anything else counts as "failed"). caller is
        an IP, counted but not kept. reason says why it found nothing or failed: one of REASONS
        (anything else counts as "other"), on the same day as the call so the two add up. app: the
        app behind the call (None: not known). bad_request_reason is separate from reasons."""
        if self.tools is not None and tool not in self.tools:
            tool = "unknown"
        now = self._now()  # one reading for date and hour
        date, hour = now.date().isoformat(), now.hour
        day = self._day(now)
        counts = day["tools"].setdefault(tool, dict.fromkeys(TOOL_COUNTS, 0))
        counts["calls"] += 1
        outcome = outcome if outcome in OUTCOMES else "failed"
        counts[outcome] += 1
        counts["ms"] += round(ms)
        if outcome == "failed":
            day["failed_hours"][hour] = (day["failed_hours"][hour] or 0) + 1
            minute = now.strftime("%Y-%m-%d %H:%M")
            failures = self._failed_minutes.setdefault(minute, {})
            key = (tool, reason if reason in REASONS else "other")
            failures[key] = failures.get(key, 0) + 1
        if outcome == "bad_request":
            label = bad_request_reason or "other"
            if not _valid_bad_request_reason(label):
                label = "other"
            elif label.startswith("arg:"):
                _, name, kind = label.split(":")
                if name not in self.tool_params.get(tool, set()):
                    label = f"arg:unknown_argument:{kind}"
            labels = day["bad_request_reasons"].setdefault(tool, {})
            labels[label] = labels.get(label, 0) + 1
        apps = day["tool_apps"].setdefault(tool, {})
        app_counts = apps.setdefault(_tool_app_name(apps, app), {"calls": 0})
        app_counts["calls"] += 1
        app_counts[outcome] = app_counts.get(outcome, 0) + 1
        if outcome in LATENCY_OUTCOMES:
            buckets = day["latency"].setdefault(tool, [0] * (len(LATENCY_BOUNDS_MS) + 1))
            bucket = next((i for i, bound in enumerate(LATENCY_BOUNDS_MS) if ms <= bound), len(LATENCY_BOUNDS_MS))
            buckets[bucket] += 1
        if reason is not None:
            reasons = day["reasons"].setdefault(tool, {})
            reason = reason if reason in REASONS else "other"
            reasons[reason] = reasons.get(reason, 0) + 1
        if day["hours"] is None:  # a day saved without hours: the ones before now are unknown
            day["hours"] = [None] * hour + [0] * (24 - hour)
        day["hours"][hour] = (day["hours"][hour] or 0) + 1
        if caller:
            self._count_caller(date, day, caller)
        if tool in DISTRIBUTOR_TOOLS:
            apps = day["distributor_apps"].setdefault(tool, {})
            counts = apps.setdefault(_capped(apps, clean_app_name(app)), dict.fromkeys(DISTRIBUTOR_APP_COUNTS, 0))
            counts["calls"] += 1
            if outcome == "rate_limited":
                counts["rate_limited"] += 1

    def _count_caller(self, date: str, day: dict[str, Any], caller: str) -> None:
        if self._callers.add(date, caller):
            day["callers"] += 1

    def record_terms(self, tool: str, outcome: str, query: Any, caller: str | None,
                     *, platform: bool = False) -> None:
        """One query's tokens. IPv6 callers share a /48, hashed only in memory.
        Every platform address shares one key; unknown callers cannot help reach the threshold.
        """
        if tool not in QUERY_TOOLS or outcome == "bad_request":
            return
        tokens = query_tokens(query)
        if not tokens:
            return
        now = self._now()
        date = now.date().isoformat()
        if date != self._term_date:
            self._refresh_terms(now)
            self._term_date, self._term_salt, self._terms = date, secrets.token_bytes(16), {}
            self._term_base = dict(self._day(now)["popular_terms"])
            self._terms = {token: (0, set()) for token in self._term_base}
        key = popularity_caller(caller, platform=platform)
        digest = (hashlib.blake2b(key.encode("utf-8", "surrogatepass"), key=self._term_salt, digest_size=8).digest()
                  if key else None)
        for token in tokens:
            if token not in self._terms and len(self._terms) >= MAX_POPULAR_TOKENS:
                continue
            count, seen = self._terms.setdefault(token, (0, set()))
            if digest is not None and len(seen) < POPULAR_CALLERS:
                seen.add(digest)
            self._terms[token] = count + 1, seen

    def _refresh_terms(self, now: datetime.datetime) -> None:
        day = self._days.get(self._term_date)
        today = now.date()
        cutoff = (today - datetime.timedelta(days=RECENT_DAYS)).isoformat()
        if day is not None and self._term_date > cutoff:
            published = dict(self._term_base)
            for token, (count, seen) in self._terms.items():
                if token in self._term_base or len(seen) >= POPULAR_CALLERS:
                    published[token] = self._term_base.get(token, 0) + count
            published = _top_terms(published)
            if day["popular_terms"] != published:
                day["popular_terms"] = published
                self._dirty = True
                self._closed_json.pop(self._term_date, None)
        if self._term_date and self._term_date != today.isoformat():
            self._term_date, self._term_salt, self._term_base, self._terms = "", b"", {}, {}

    def record_app(self, name: str | None) -> None:
        """An MCP app connected (the clientInfo name it sent with initialize)."""
        apps = self._day()["apps"]
        name = _capped(apps, clean_app_name(name))
        apps[name] = apps.get(name, 0) + 1

    def record_distributor(self, name: str, event: str) -> None:
        """A Mouser/DigiKey lookup: "sent" to the API, "cached" (answered from the cache) or
        "rate_limited" (turned away by our limits or a pause the API asked for); or a part number
        "skipped" (DISTRIBUTOR_SKIPPED). Mouser "retries" counts sent transient retries (also in sent)."""
        counts = self._day()["distributors"].setdefault(name, dict.fromkeys(DISTRIBUTOR_EVENTS, 0))
        counts[event] = counts.get(event, 0) + 1

    def record_upstream(self, source: str, event: str, count: int = 1) -> None:
        """Requests to a service other than Mouser/DigiKey: source is one of UPSTREAM_SOURCES, event
        one of UPSTREAM_EVENTS (count: how many, for retries). Anything else isn't counted."""
        if source in UPSTREAM_SOURCES and event in UPSTREAM_EVENTS and count > 0:
            counts = self._day()["upstream"].setdefault(source, dict.fromkeys(UPSTREAM_EVENTS, 0))
            counts[event] += count

    def record_upstream_status(self, source: str, label: str) -> None:
        """One class for each sent request, including errors; fixed labels only (from 0.10.5)."""
        if source in UPSTREAM_STATUS_SOURCES and label in UPSTREAM_STATUS_CLASSES:
            counts = self._day()["upstream_status"].setdefault(source, {})
            counts[label] = counts.get(label, 0) + 1

    def flush_failed_calls(self, *, shutdown: bool = False) -> None:
        """One WARNING per finished UTC minute with failures; shutdown also flushes this minute."""
        current = self._now().strftime("%Y-%m-%d %H:%M")
        for minute in sorted(self._failed_minutes):
            if shutdown or minute < current:
                counts = self._failed_minutes.pop(minute)
                labels = ", ".join(f"{tool} {reason} {count}" for (tool, reason), count in sorted(counts.items()))
                logger.warning("Failed tool calls %s UTC: %s", minute, labels)

    def record_distributor_limit(self, name: str, kind: str, label: str | None) -> None:
        """One unsent lookup (held_back) or sent request refused by the distributor (refusals).
        Only fixed labels are kept; unknown causes count as other. No credential details."""
        if name not in PARTS_ASKED or kind not in ("held_back", "refusals"):
            return
        if kind == "held_back":
            label = label if label in DISTRIBUTOR_LIMIT_CAUSES else "other"
        elif label not in DISTRIBUTOR_LIMIT_REFUSALS:
            return
        now = self._now()
        counts = self._day(now)["distributor_limits"].setdefault(name, _new_distributor_limits())
        counts[kind][label] += 1
        if kind == "held_back":
            counts["held_back_hours"][now.hour] += 1

    def record_parts_asked(self, distributor: str, numbers: list[str]) -> None:
        """Part numbers a Mouser/DigiKey lookup asked for (distinct within the lookup), whether they
        were answered from the stored answers, with a request, or turned away by the limits (not
        the skipped ones, which aren't looked up at all): counted, and the ones not seen yet today
        (compared by mpn_key: case and - _ / ignored) counted as distinct. Neither the numbers nor
        their hashes are written anywhere."""
        if distributor not in PARTS_ASKED or not numbers:
            return
        from .search.mpn import mpn_key  # here: the search package is too much to load with this module

        now = self._now()
        date = now.date().isoformat()
        counts = self._day(now)["parts_asked"].setdefault(distributor, {"total": 0, "distinct": 0})
        seen = self._parts[distributor]
        for number in numbers:
            counts["total"] += 1
            if seen.add(date, mpn_key(str(number).strip())):
                counts["distinct"] += 1

    def record_refusal(self, group: str = "everyone_else") -> None:
        """One HTTP request admission control turned away (no IP is kept), on its day and in its
        UTC hour. group: one of REFUSAL_GROUPS; anything else counts as everyone_else."""
        now = self._now()  # one reading for date and hour
        day = self._day(now)
        refusals = day["per_ip_refusals"]
        group = group if group in REFUSAL_GROUPS else "everyone_else"
        refusals[group] = refusals.get(group, 0) + 1
        day["refused_hours"][now.hour] = (day["refused_hours"][now.hour] or 0) + 1

    def record_lcsc_lookup(self, tool: str, event: str) -> None:
        """How one LCSC-code lookup was answered: tool one of LCSC_LOOKUP_TOOLS, event one of
        LCSC_LOOKUP_EVENTS. Anything else isn't counted."""
        if tool in LCSC_LOOKUP_TOOLS and event in LCSC_LOOKUP_EVENTS:
            counts = self._day()["lcsc_lookups"].setdefault(tool, dict.fromkeys(LCSC_LOOKUP_EVENTS, 0))
            counts[event] += 1

    def record_datasheet_link(self, event: str) -> None:
        """Anonymous /mcp/datasheet counts; no code or target link is kept."""
        if event in DATASHEET_LINK_EVENTS:
            self._day()["datasheet_links"][event] += 1

    def record_lifecycle_input(self, form: str) -> None:
        """One usable part_lifecycle input, before resolving its catalog identity. Fixed labels only."""
        if form in LIFECYCLE_INPUT_FORMS:
            self._day()["lifecycle_inputs"][form] += 1

    def record_db_wait(self, seconds: float, components: bool = False,
                       started_at: datetime.datetime | None = None) -> None:
        """One started database job; queue delay only, no query time or identifying data."""
        now = started_at or self._now()
        counts = self._day(now)["db_waits"]
        milliseconds = max(0, round(seconds * 1000))
        for target in (counts, counts["components"]) if components else (counts,):
            target["jobs"] += 1
            target["longest_ms"] = max(target["longest_ms"], milliseconds)
            target["longest_ms_hours"][now.hour] = max(target["longest_ms_hours"][now.hour], milliseconds)
            if seconds >= DB_WAIT_COUNTED_SECONDS:
                target["waited"] += 1
                target["waited_hours"][now.hour] += 1

    def record_why_empty(self, result: str) -> None:
        """How the checks behind a why_empty reply went: one of WHY_EMPTY_RESULTS."""
        if result in WHY_EMPTY_RESULTS:
            counts = self._day()["why_empty"]
            counts[result] = counts.get(result, 0) + 1

    def _save_snapshot(self) -> tuple[Path, str] | None:
        """Detached serialization on the event loop; workers never read live counting maps."""
        now = self._now()
        self._refresh_terms(now)
        self._maintain_recent(now)
        if self.path is None or not self._dirty:
            return None
        today = now.date().isoformat()
        entries = []
        for date in sorted(self._days):
            text = self._closed_json.get(date)
            if text is None:
                text = json.dumps(date) + ": " + json.dumps(self._days[date], sort_keys=True)
                if date < today:
                    self._closed_json[date] = text
            entries.append(text)
        # Exactly json.dumps({"days": self._days}, sort_keys=True), including spaces/escaping.
        snapshot = self.path, '{"days": {' + ", ".join(entries) + "}}"
        self._dirty = False
        return snapshot

    def _save_failed(self, error: Exception) -> None:
        if self.ok:
            logger.warning("Usage stats file %s not writable (%s); counts are kept in memory only",
                           self.path, type(error).__name__)
        self.ok = False
        self._dirty = True

    def save(self) -> None:
        """Synchronous atomic save for scripts/tests. The server uses save_async()."""
        try:
            if snapshot := self._save_snapshot():
                _write_usage(*snapshot)
                self.ok = True
        except Exception as exc:
            self._save_failed(exc)

    async def save_async(self) -> None:
        """Minute/shutdown save: file I/O off the loop, finishing even during cancellation."""
        task = asyncio.create_task(self._save_async())
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            await task
            raise

    async def _save_async(self) -> None:
        try:
            if snapshot := self._save_snapshot():
                await asyncio.to_thread(_write_usage, *snapshot)
                self.ok = True
        except Exception as exc:
            self._save_failed(exc)

    def summary(self, days: int = 30) -> dict[str, Any]:
        """For /mcp/stats: totals over the newest `days` days that had any use, then each of those
        days, newest first."""
        now = self._now()
        self._refresh_terms(now)
        self._maintain_recent(now)
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
        total_lookups: dict[str, dict[str, int]] = {}
        total_distributor_apps: dict[str, dict[str, dict[str, int]]] = {}
        total_distributor_limits: dict[str, dict[str, Any]] = {}
        total_datasheet_links = dict.fromkeys(DATASHEET_LINK_EVENTS, 0)
        total_db_waits = _new_db_waits()
        total_lifecycle_inputs = dict.fromkeys(LIFECYCLE_INPUT_FORMS, 0)
        total_hours = [0] * 24
        new_totals: dict[str, Any] = dict.fromkeys(SINCE_0_10_5)
        for date in dates:
            day = self._days[date]
            for field in SINCE_0_10_5:
                if day[field] is not None:
                    if new_totals[field] is None:
                        new_totals[field] = {}
                    _sum_counts(new_totals[field], day[field])
            for form, count in (day["lifecycle_inputs"] or {}).items():
                total_lifecycle_inputs[form] += count
            if day["db_waits"] is not None:
                _add_db_waits(total_db_waits, day["db_waits"])
            for event, count in (day["datasheet_links"] or {}).items():
                total_datasheet_links[event] += count
            for name, counts in (day["distributor_limits"] or {}).items():
                total = total_distributor_limits.setdefault(name, _new_distributor_limits())
                for kind in ("held_back", "refusals"):
                    for label, count in counts[kind].items():
                        total[kind][label] += count
                for hour, count in enumerate(counts["held_back_hours"]):
                    total["held_back_hours"][hour] += count
            for name, c in (day["lcsc_lookups"] or {}).items():
                total = total_lookups.setdefault(name, dict.fromkeys(LCSC_LOOKUP_EVENTS, 0))
                for key, value in c.items():
                    total[key] = total.get(key, 0) + value
            for name, apps in (day["distributor_apps"] or {}).items():
                for app, c in apps.items():
                    total = total_distributor_apps.setdefault(name, {}).setdefault(
                        app, dict.fromkeys(DISTRIBUTOR_APP_COUNTS, 0))
                    for key, value in c.items():
                        total[key] = total.get(key, 0) + value
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
                "failed_hours": day["failed_hours"],
                "refused_hours": day["refused_hours"],
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
                "lcsc_lookups": _lookups_view(day["lcsc_lookups"]),
                "distributor_apps": _distributor_apps_view(day["distributor_apps"]),
                "distributor_limits": day["distributor_limits"],
                "datasheet_links": day["datasheet_links"],
                "db_waits": day["db_waits"],
                "lifecycle_inputs": day["lifecycle_inputs"],
                **{field: _recent_view(field, day[field])
                   for field in SINCE_0_10_5},
            })
        totals_tools = _tools_view(total_tools)
        return {
            "about": (f"Private counts per UTC day, default 30 days, up to {KEEP_DAYS}, newest first; totals adds up "
                      "the days listed (without callers, which can't be added across days). "
                      "distributor_quota (from 0.10.9): current state per distributor, independent of days and totals; "
                      "used_today, limit, api_remaining (null when unreported), paused_until (null when not paused), "
                      "resets_at and kept_across_restarts where available. Quota times use YYYY-MM-DD HH:MM UTC. "
                      "hours: calls in each UTC hour, "
                      "00 to 23 (null: not recorded); in totals, each hour added up across the days. failed_hours (from "
                      "0.10.1): the calls whose outcome was failed, in each UTC hour; refused_hours (from 0.10.1): "
                      "the requests counted in per_ip_refusals, in each UTC hour; both null on days before 0.10.1 "
                      "and, on the day it started, for the hours before that; not in totals. Each tool's calls = ok (found "
                      "something; for alternatives, verified replacements) + similar_only (only similar parts for manual "
                      "comparison, no verified replacements) + not_found (worked, found nothing) + bad_request (the request was invalid) + "
                      "rate_limited (a limit turned it away) + failed (something broke on this server or a service "
                      "it calls), plus unsorted where shown (error replies from before 0.6.4, which weren't "
                      "sorted). callers counts distinct IPs, which isn't the number of people: hosted apps such "
                      "as claude.ai call from their own servers' IPs, and a caller seen before and after a restart "
                      "counts twice. apps are the names MCP apps send when they connect. The stats keep no IPs, "
                      "whole queries or individual lookup numbers; popular_terms can include part-number tokens "
                      "once they reach its caller threshold. Cutover 2026-10-26: alternatives replies before that date counted "
                      "similar-parts-only replies as not found; historical counts have not been reclassified. reasons (from 0.9.0; "
                      "earlier days have none): for each tool, why calls came back not_found or failed, one fixed label a "
                      "call. why_empty: how the checks behind jlc_search's why_empty went (no_counterfactual: no library, "
                      "package or stock limit to test). distributors retry_found and retry_missed: before 0.9.3, DigiKey all-digit "
                      "numbers that missed the direct lookup and went on to a keyword search, also counted in sent. "
                      "distributors mouser retries (from 0.10.9, on days with any): sent attempts after transient "
                      "failures, also counted in sent; each send counts once, including retries. "
                      "distributors skipped (from 0.10.0, on days with any): part numbers not sent because no "
                      "distributor can list them (a value such as 10k, a BOM placeholder, an LCSC code, non-ASCII "
                      "text, not 3-40 characters); one a number. "
                      "From 0.10.0 (earlier days have none): upstream, for each service this server calls: jlcpcb "
                      "(parts search), lcsc (product data), easyeda_products (footprint checks), easyeda_components "
                      "(symbols and footprints for pinouts), easyeda_pads (footprint pads for land checks), cse "
                      "(SamacSys searches and model downloads) and, from 0.10.4, digikey (DigiKey's HTTP requests; "
                      "distributors counts lookups); "
                      "sent is HTTP requests sent, one each, not tool calls; retries the further attempts the HTTP "
                      "client made on its own for them, where it reports them (a timeout reports none); cached "
                      "answers given without a request (memory cache, on-disk store or seed); rate_limited requests "
                      "this server's own budget or pause for that service kept back (for cse, also sent "
                      "model downloads SamacSys refused for quota); waited (from 0.10.4) requests sent after waiting "
                      "for a free request slot. parts_asked: part numbers "
                      "asked for with Mouser and DigiKey, whether stored answers gave them, a request did or the "
                      "limits turned them away (total; skipped ones aren't counted), and how many "
                      "were different that day (distinct, ignoring case and - _ /; counted through salted hashes "
                      "held in memory, so a restart counts them again; not in totals, which can't add them across "
                      "days). per_ip_refusals: HTTP requests admission control turned away (429): total (all "
                      "of the groups) and by group: per-address rate limit refusals by address group "
                      "(platform_ranges: addresses in the AI platforms' published ranges, which have a "
                      "higher limit; everyone_else: every other caller), then, regardless of address, "
                      "server_busy (0.10.0 only: shared database queue pressure; 0 from 0.10.1, which "
                      "removed that refusal) and too_many_clients (the server was "
                      "tracking as many addresses as it can); null on days before it was counted. "
                      "restarts (from 0.10.0; null before): how many times the server started that day; "
                      "callers and parts_asked distinct count a caller or part seen on both sides of a "
                      "restart twice. lcsc_lookups (from 0.10.2; null before): how jlc_get_part's LCSC-code "
                      "lookups and jlc_stock_check's one-code queries were answered, one each: snapshot (the "
                      "daily snapshot, no request), live (answered from a live lookup, including its 1-hour "
                      "cache), fallback (JLCPCB didn't answer and the snapshot did: live_failed in the reply) "
                      "and live_failed (the live lookup failed and nothing answered instead: the error). "
                      "distributor_apps (from 0.10.2; null before): calls to mouser_get_part, digikey_get_part "
                      "and part_lifecycle by app, and how many were rate_limited; a call counts under the app "
                      f"its address last connected with (remembered for {APP_LINK_MINUTES} minutes after the "
                      "address's last connection or tool call), else under unknown. "
                      "distributor_limits (from 0.10.3; null before): for mouser and digikey, held_back counts lookups "
                      "not sent, by cause: minute_cap and daily_count (this server's limits), address_daily (the "
                      "address's daily cap), address_blocked (from 0.10.10: the address is on the server's "
                      "block list), distributor_daily, distributor_minute and distributor_refused (pauses "
                      "after the distributor refused), other; it adds up to distributors rate_limited. "
                      "held_back_hours: the same by UTC hour. refusals: sent requests the distributor refused "
                      "(daily, minute, refused). "
                      "datasheet_links (from 0.10.3; null before): visits to datasheet_pdf links: reused (no "
                      "JLCPCB request), signed (one was made), waited (of those, after waiting for a slot), "
                      "refused (429), failed (502), not_found (404). "
                      "db_waits (from 0.10.3; null before): database jobs (jobs), those that waited at least "
                      f"{DB_WAIT_COUNTED_SECONDS:g} s for a worker (waited), the longest wait (longest_ms), and "
                      "waited_hours and longest_ms_hours by UTC hour; components: the same for the component "
                      "catalog alone. In totals the longest is the maximum. "
                      "lifecycle_inputs (from 0.10.4; null before): part_lifecycle entries by input form, "
                      "before catalog resolution: bare_number, with_manufacturer or lcsc_code; invalid inputs "
                      "aren't counted. Counts only, no part numbers or maker names. "
                      "bad_request_reasons (from 0.10.5; null before): one fixed label per bad_request, "
                      "separate from reasons; arg:<declared parameter or unknown_argument>:<fixed error type> "
                      "for argument validation, all_inputs_invalid for invalid batches, unknown_tool for unknown tools. "
                      "tool_apps (from 0.10.5; null before): each tool's calls and every outcome by app, "
                      f"up to {MAX_APPS} named apps per tool today, later new names count as other; "
                      f"past UTC days keep the {MAX_TOOL_APPS - 1} busiest apps by calls plus other, "
                      "which sums every outcome from the rest (compacted on rollover, load, save and summary); "
                      "same app attribution as distributor_apps. latency (from 0.10.5; null before): each tool's "
                      "bucket counts and p50_ms, p95_ms, p99_ms, counting ok, similar_only, not_found and failed only; "
                      "latency_bounds_ms gives inclusive upper bounds, with one final open bucket; percentiles "
                      "are bucket upper bounds (null for an empty histogram or the open bucket). tool_apps, "
                      "latency and popular_terms are kept for the last 30 days only, cleared from older days on rollover, load, "
                      "save and summary, even with no new calls. "
                      "popular_terms (from 0.10.5; null before): top 200 query tokens by occurrences, each counted "
                      "once per call, up to 20 tokens per query, for jlc_search, jlc_stock_check, cse_search, "
                      "board_search and sensor_recommend except bad_request. Only tokens from at least 10 distinct "
                      "callers that UTC day are retained; all platform addresses count as one caller, other IPv6 "
                      "addresses by /48. This is a popularity heuristic, not an anonymity guarantee against "
                      "someone controlling many addresses. Below-threshold tokens and salted caller hashes stay in memory only "
                      "(20,000 tokens, 10 hashes each). No phrases. A restart keeps retained counts but resets "
                      "the threshold for new tokens; totals sums retained daily counts, keeping the top 200. "
                      "versions (from 0.10.5; null before): server starts by running version. upstream_status "
                      "(from 0.10.5; null before): one class per sent request per source: 2xx, 3xx, 4xx, 429 "
                      "(separate from 4xx), 5xx, timeout, connection, challenge, too_large, cancelled or other_error. "
                      "From 0.10.9 also mouser, including every transient retry; its sends are in distributors. "
                      "Mouser TooManyRequests replies count as 429 regardless of HTTP status. "
                      "Cutovers from 0.10.5: mouser_get_part misses count part_not_found instead of no_results; "
                      "jlc_stock_check's no_results splits into no_results_filtered, no_results_part_number and "
                      "no_results_words; jlc_search's part_number_not_in_stock becomes part_number_sold_out or "
                      "part_number_unknown, using a label-only lookup of previously listed parts. Historical "
                      "labels and counts are kept. Failed calls also produce one labels-only WARNING per UTC minute."),
            "latency_bounds_ms": list(LATENCY_BOUNDS_MS),
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
                "lcsc_lookups": _lookups_view(total_lookups),
                "distributor_apps": _distributor_apps_view(total_distributor_apps),
                "distributor_limits": total_distributor_limits,
                "datasheet_links": total_datasheet_links,
                "db_waits": total_db_waits,
                "lifecycle_inputs": total_lifecycle_inputs,
                **{field: _recent_view(field, value)
                   for field, value in new_totals.items()},
            },
            "days": out,
        }


def _write_usage(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with private_open(tmp, "w", encoding="utf-8") as out:
        out.write(text)
        out.flush()
        os.fsync(out.fileno())
    os.replace(tmp, path)


def _recent_view(field: str, value: dict | None) -> dict | None:
    if value is None:
        return None
    if field == "latency":
        return _latency_view(value)
    if field == "popular_terms":
        return _top_terms(value)
    if field == "tool_apps":
        return {tool: {app: {key: counts.get(key, 0) for key in ("calls", *OUTCOMES)}
                       for app, counts in names.items()} for tool, names in value.items()}
    return value


def _sum_counts(total: dict, counts: dict) -> None:
    """Add the bounded 0.10.5 maps/histograms without mutating the stored days."""
    for key, value in counts.items():
        if isinstance(value, dict):
            _sum_counts(total.setdefault(key, {}), value)
        elif isinstance(value, list):
            dest = total.setdefault(key, [0] * len(value))
            for i, count in enumerate(value):
                dest[i] += count
        else:
            total[key] = total.get(key, 0) + value


def _latency_view(latency: dict | None) -> dict | None:
    if latency is None:
        return None
    result = {}
    for tool, counts in sorted(latency.items()):
        percentiles = {}
        for percentile in (50, 95, 99):
            rank, cumulative, bound = (sum(counts) * percentile + 99) // 100, 0, None
            if rank:
                for upper, count in zip((*LATENCY_BOUNDS_MS, None), counts):
                    cumulative += count
                    if cumulative >= rank:
                        bound = upper
                        break
            percentiles[f"p{percentile}_ms"] = bound
        result[tool] = {"counts": list(counts), **percentiles}
    return result


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


def _lookups_view(lookups: dict[str, dict[str, int]] | None) -> dict[str, dict[str, int]] | None:
    """Each tool's LCSC-code lookups, in LCSC_LOOKUP_TOOLS order; None when not counted."""
    if lookups is None:
        return None
    return {name: {event: lookups[name].get(event, 0) for event in LCSC_LOOKUP_EVENTS}
            for name in LCSC_LOOKUP_TOOLS if name in lookups}


def _distributor_apps_view(by_tool: dict[str, dict[str, dict[str, int]]] | None
                           ) -> dict[str, dict[str, dict[str, int]]] | None:
    """Each distributor tool's calls by app, tools in DISTRIBUTOR_TOOLS order, the app with the
    most calls first; None when not counted."""
    if by_tool is None:
        return None
    return {name: {app: {key: c.get(key, 0) for key in DISTRIBUTOR_APP_COUNTS}
                   for app, c in sorted(by_tool[name].items(), key=lambda item: (-item[1].get("calls", 0), item[0]))}
            for name in DISTRIBUTOR_TOOLS if name in by_tool}


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
def count_db_wait(seconds: float, components: bool, started_at: datetime.datetime) -> None:
    try:
        usage.record_db_wait(seconds, components, started_at)
    except Exception:
        logger.exception("Usage stats: couldn't count a database wait")


def count_distributor(name: str, event: str) -> None:
    try:
        usage.record_distributor(name, event)
    except Exception:
        logger.exception("Usage stats: couldn't count a distributor lookup")


def count_distributor_limit(name: str, kind: str, label: str | None) -> None:
    try:
        usage.record_distributor_limit(name, kind, label)
    except Exception:
        logger.exception("Usage stats: couldn't count a distributor limit")


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


def count_upstream_status(source: str, result: Any, *, status: str | None = None) -> None:
    """Count a response or exception, never propagating a counting failure to the request."""
    try:
        usage.record_upstream_status(source, status if status is not None else _upstream_status(result))
    except Exception:
        logger.exception("Usage stats: couldn't count an upstream status")


def _upstream_status(result: Any) -> str:
    # wafer returns ordinary HTTP errors as responses; raise_for_status() makes WaferHTTPError.
    # Classify typed transport failures first, even when they carry an HTTP status/response.
    import httpx
    from wafer import ChallengeDetected, ConnectionFailed, EmptyResponse, RateLimited, ResponseTooLarge

    if isinstance(result, asyncio.CancelledError):
        return "cancelled"
    if isinstance(result, (TimeoutError, httpx.TimeoutException)):
        return "timeout"
    if isinstance(result, (ConnectionFailed, EmptyResponse, httpx.TransportError)):
        return "connection"
    if isinstance(result, ChallengeDetected):
        return "challenge"
    if isinstance(result, ResponseTooLarge):
        return "too_large"
    if isinstance(result, RateLimited):
        return "429"
    # With max_rotations=0 wafer can return the challenge page instead of raising.
    if getattr(result, "challenge_type", None) is not None:
        return "challenge"
    code = getattr(result, "status_code", None)
    if code is None:
        code = getattr(getattr(result, "response", None), "status_code", None)
    if isinstance(code, int):
        if code == 429:
            return "429"
        if 200 <= code < 600:
            return f"{code // 100}xx"
    return "other_error"


def count_lcsc_lookup(tool: str, event: str) -> None:
    try:
        usage.record_lcsc_lookup(tool, event)
    except Exception:
        logger.exception("Usage stats: couldn't count an LCSC-code lookup")


def count_datasheet_link(event: str) -> None:
    try:
        usage.record_datasheet_link(event)
    except Exception:
        logger.exception("Usage stats: couldn't count a datasheet link")


def count_lifecycle_input(form: str) -> None:
    try:
        usage.record_lifecycle_input(form)
    except Exception:
        logger.exception("Usage stats: couldn't count a lifecycle input")
