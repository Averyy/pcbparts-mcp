"""Shared TTL cache with LRU eviction for distributor API clients, plus request budgets."""

import asyncio
import collections
import datetime
import hmac
import ipaddress
import json
import logging
import math
import os
import secrets
import time
from pathlib import Path
from typing import Any, Callable, Iterable

from . import private_files, stats

logger = logging.getLogger(__name__)

# Named in the distributor limit errors: running your own copy avoids this server's shared limits
SELF_HOSTING_URL = "https://github.com/Averyy/pcbparts-mcp#self-hosting"

# Normal callers rarely reach this, so their addresses are never written.
CARRY_MIN = 100


class TTLCache:
    """Simple TTL cache with max size enforcement via LRU eviction.

    Thread-safe for single-threaded asyncio (no await between check and set).
    """

    def __init__(self, ttl: float, max_size: int = 5000):
        self._ttl = ttl
        self._max_size = max_size
        self._data: dict[str, tuple[float, Any]] = {}  # key -> (expiry time, value)

    def get(self, key: str) -> Any | None:
        """Get a cached value, or None if missing/expired."""
        if key in self._data:
            expires, result = self._data[key]
            if time.time() < expires:
                return result
            del self._data[key]
        return None

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Cache a value for ttl seconds (default: the cache's ttl). Evicts expired entries first,
        then the ones expiring soonest if still over max_size."""
        self._data[key] = (time.time() + (self._ttl if ttl is None else ttl), value)
        if len(self._data) > self._max_size:
            self._evict()

    def _evict(self) -> None:
        """Remove expired entries, then the ones expiring soonest if still over max_size."""
        now = time.time()
        # First pass: remove expired
        expired = [k for k, (expires, _) in self._data.items() if now >= expires]
        for k in expired:
            del self._data[k]
        # Second pass: LRU eviction if still over limit
        if len(self._data) > self._max_size:
            sorted_keys = sorted(self._data.keys(), key=lambda k: self._data[k][0])
            for k in sorted_keys[:len(self._data) - self._max_size]:
                del self._data[k]

    def __len__(self) -> int:
        return len(self._data)


def _utc_today() -> datetime.date:
    """Current date in UTC (not local time)."""
    return datetime.datetime.now(datetime.timezone.utc).date()


def _utc_text(timestamp: float) -> str:
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _next_utc_midnight(timestamp: float) -> float:
    today = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).date()
    return datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time(),
                                     datetime.timezone.utc).timestamp()


def _header_int(headers: Any, name: str) -> int | None:
    value = headers.get(name)
    return int(value) if isinstance(value, str) and value.strip().isdigit() else None


def retry_after_seconds(headers: Any, now: float) -> float | None:
    """A reply's Retry-After as seconds from now: whole seconds, or an HTTP date (UTC when it gives
    no zone; 0 once past). math.inf for more than two digits of seconds (also avoids parsing an
    unbounded integer); None when absent or unusable, so the caller keeps its own delay."""
    value = (headers.get("Retry-After") or "").strip()
    if not value:
        return None
    if value.isascii() and value.isdecimal():
        digits = value.lstrip("0")
        return math.inf if len(digits) > 2 else float(int(digits or "0"))
    from email.utils import parsedate_to_datetime
    try:
        date = parsedate_to_datetime(value)
        if date.tzinfo is None:
            date = date.replace(tzinfo=datetime.timezone.utc)
        return max(0.0, date.timestamp() - now)
    except (ValueError, TypeError, OverflowError):
        return None


class RetryGuard:
    """Stops a client's transient retries during an outage: at least 10 of the attempts in the last
    five minutes failed transiently, and 90% or more of them did. A bounded window of ten-second
    buckets (start, transient, total), keeping the one overlapping the cutoff. Record every sent
    attempt's outcome (cancelled ones have none; refusals and errors that aren't retried count in the
    total), and check after outcomes and before a retry's send, so an idle guard expires too.

    consecutive (off by default; CSE's is 2): retries are also off once that many recorded attempts
    in a row failed, until one that didn't fail (any answer, a 4xx too) is recorded. A failure is a
    transient outcome, or one recorded with failed=True (a timeout: not retried, but a hung service)."""

    def __init__(self, name: str, clock: Callable[[], float] = time.time, log: logging.Logger = logger,
                 *, consecutive: int | None = None):
        self._name, self._clock, self._log = name, clock, log
        self.outcomes: collections.deque[list[int]] = collections.deque(maxlen=31)
        self._active = False
        self._consecutive = consecutive
        self.failures_in_a_row = 0
        self._streak_active = False

    def record(self, *, transient: bool, failed: bool | None = None) -> None:
        start = int(self._clock() // 10) * 10
        if not self.outcomes or self.outcomes[-1][0] != start:
            self.outcomes.append([start, 0, 0])
        self.outcomes[-1][1] += int(transient)
        self.outcomes[-1][2] += 1
        if self._consecutive is not None:
            self._record_streak(transient if failed is None else failed)
        self.disabled()

    def _record_streak(self, failed: bool) -> None:
        assert self._consecutive is not None
        if failed:
            self.failures_in_a_row += 1
            if not self._streak_active and self.failures_in_a_row >= self._consecutive:
                self._streak_active = True
                self._log.warning("%s retries off after %d failures in a row", self._name, self.failures_in_a_row)
            return
        if self._streak_active:
            self._log.info("%s retries on again: a request was answered after %d failures in a row",
                           self._name, self.failures_in_a_row)
            self._streak_active = False
        self.failures_in_a_row = 0

    def disabled(self) -> bool:
        """Whether retries are off now; logs each change once."""
        cutoff = self._clock() - 300
        while self.outcomes and self.outcomes[0][0] + 10 <= cutoff:
            self.outcomes.popleft()
        failures = sum(row[1] for row in self.outcomes)
        attempts = sum(row[2] for row in self.outcomes)
        disabled = failures >= 10 and failures * 10 >= attempts * 9
        if disabled != self._active:
            log = self._log.warning if disabled else self._log.info
            log("%s retry guard %s: %d/%d transient failures over the last 5 minutes; retries %s",
                self._name, "entered" if disabled else "cleared", failures, attempts,
                "disabled" if disabled else "enabled")
            self._active = disabled
        return disabled or self._streak_active


def _daily_reset(headers: Any, now: float) -> float:
    """When the API's daily limit resets: X-RateLimit-ResetTime (GMT), else Retry-After, else the
    next UTC midnight (DigiKey's reset was 00:00Z on 2026-10-16)."""
    value = headers.get("x-ratelimit-resettime")
    if isinstance(value, str):
        try:
            reset = datetime.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            pass
        else:
            if reset.tzinfo is None:
                reset = reset.replace(tzinfo=datetime.timezone.utc)
            return reset.timestamp()
    retry_after = _header_int(headers, "retry-after")
    if retry_after is not None:
        return now + retry_after
    return _next_utc_midnight(now)


# Room for one hourly line's IP list under file_logging.MAX_MESSAGE_CHARS (2,000) after its heading
LINE_LIST_CHARS = 1500


def _line_parts(items: list[str]) -> list[str]:
    """items joined with ", " into as few strings as fit LINE_LIST_CHARS each (one item per string
    at least)."""
    parts, current = [], ""
    for item in items:
        if current and len(current) + 2 + len(item) > LINE_LIST_CHARS:
            parts.append(current)
            current = item
        else:
            current = f"{current}, {item}" if current else item
    if current:
        parts.append(current)
    return parts


class CallerTally:
    """Requests per caller IP in the current UTC hour, logged as one summary line once the hour is
    over (flush_if_due(), which the server calls every minute) or at shutdown (flush()). Hours
    without requests log nothing. At most max_callers IPs are tracked an hour; the rest count as
    "other". Requests sent with a later app or key (a QuotaPool's) are also counted by its number;
    unit names them in the line ("app" for DigiKey, "key" for Mouser). what says what was counted
    ("requests sent" for Mouser/DigiKey, "refusals" for the per-IP rate limit's). top=None names
    every IP (held-back calls), over as many lines as the file log's message limit needs."""

    def __init__(self, name: str, clock: Callable[[], float] = time.time, max_callers: int = 1000,
                 top: int | None = 5, what: str = "requests sent"):
        self._name = name
        self._what = what
        self._clock = clock
        self._max_callers = max_callers
        self._top = top
        self.unit = "app"
        self._hour = self._hour_of(clock())
        self._counts: collections.Counter[str] = collections.Counter()
        self._apps: collections.Counter[int] = collections.Counter()

    @staticmethod
    def _hour_of(timestamp: float) -> int:
        return int(timestamp // 3600) * 3600

    def record(self, caller: str | None, app_index: int = 0) -> None:
        self.flush_if_due()
        key = caller or "unknown"
        if key not in self._counts and len(self._counts) >= self._max_callers:
            key = "other"
        self._counts[key] += 1
        self._apps[app_index] += 1

    def flush_if_due(self) -> None:
        if self._hour_of(self._clock()) != self._hour:
            self.flush()

    def flush(self) -> None:
        """Log the hour so far (if it had requests) and start a new one."""
        now = self._clock()
        if self._counts:
            start = datetime.datetime.fromtimestamp(self._hour, datetime.timezone.utc)
            end = datetime.datetime.fromtimestamp(min(now, self._hour + 3600), datetime.timezone.utc)
            end_text = "24:00" if end.date() > start.date() else end.strftime("%H:%M")
            later = ", ".join(f"{self.unit} {index + 1}: {count}" for index, count in sorted(self._apps.items())
                              if index and count)
            head = (f"{self._name} {self._what} {start:%Y-%m-%d %H:%M}-{end_text} UTC: "
                    f"{sum(self._counts.values())} from {len(self._counts)} IPs")
            tail = f" ({later})" if later else ""
            if self._top is not None:
                top = ", ".join(f"{caller} {count}" for caller, count in self._counts.most_common(self._top))
                logger.info(f"{head}; top: {top}{tail}")
            else:
                parts = _line_parts([f"{caller} {count}" for caller, count in self._counts.most_common()])
                for number, part in enumerate(parts, 1):
                    label = head if number == 1 else f"{head} (continued, {number} of {len(parts)})"
                    logger.info(f"{label}; all: {part}" + (tail if number == 1 else ""))
        self._counts.clear()
        self._apps.clear()
        self._hour = self._hour_of(now)


class AddressDailyQuota:
    """Sent lookups per address and UTC day: one count for every pool it is given to
    (Mouser and DigiKey together on the server). key returns None for exempt callers.
    save/load carry busy addresses across a restart as hashes keyed with a per-day secret.
    Oldest addresses are dropped first when the bounded table fills. Check and record without
    awaiting between them, only recording after the shared quota lets the request through.
    blocked: networks whose callers are always capped (never counted), even when exempt or with
    the cap off."""

    def __init__(self, limit: int, key: Callable[[str], str | None],
                 clock: Callable[[], float] = time.time, max_addresses: int = 20_000,
                 blocked: Iterable[ipaddress.IPv4Network | ipaddress.IPv6Network] = ()):
        self.limit = limit
        self._key = key
        self._clock = clock
        self._max_addresses = max_addresses
        self._blocked = tuple(blocked)
        self._started = clock()  # a first lookup after a same-day restart may not be the day's first
        self._date = self._today()
        self._secret = secrets.token_bytes(32)
        self._counts: dict[str, int] = {}
        self._carried: dict[str, int] = {}
        # key -> its first recorded lookup today, for the cap's log line; none for a count carried
        # over a restart. Dropped with the key's count.
        self._first: dict[str, float] = {}

    def _today(self) -> datetime.date:
        return datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc).date()

    def reset_if_due(self) -> None:
        """Drop the previous day's addresses, also called by the server's minute task when quiet."""
        today = self._today()
        if today != self._date:
            self._counts.clear()
            self._carried.clear()
            self._first.clear()
            self._secret = secrets.token_bytes(32)
            self._date = today

    def _digest(self, key: str) -> str:
        return hmac.new(self._secret, key.encode("utf-8"), "sha256").hexdigest()

    def _caller_key(self, caller: str | None) -> str | None:
        self.reset_if_due()
        key = self._key(caller) if self.limit and caller is not None else None
        if key is not None and key not in self._counts and self._carried:
            if (count := self._carried.pop(self._digest(key), None)) is not None:
                self._counts[key] = count
        return key

    def save(self, path: str | Path) -> None:
        """Privately carry today's busy addresses over a restart; failures only warn."""
        try:
            path = Path(path)
            tmp = path.with_name(path.name + ".tmp")
            try:
                self.reset_if_due()
                counts = dict(self._carried) if self.limit else {}
                if self.limit:
                    counts.update((self._digest(key), count) for key, count in self._counts.items()
                                  if count >= CARRY_MIN)
                if not counts:
                    path.unlink(missing_ok=True)
                    return
                path.parent.mkdir(parents=True, exist_ok=True)
                with private_files.private_open(tmp, "w", encoding="utf-8") as out:
                    json.dump({"date": self._date.isoformat(), "secret": self._secret.hex(),
                               "counts": counts}, out)
                os.replace(tmp, path)
            finally:
                tmp.unlink(missing_ok=True)
        except Exception as exc:
            logger.warning("Per-address counts: could not save %s (%s)", path, type(exc).__name__)

    def load(self, path: str | Path) -> int:
        """Consume a restart file, keeping only today's valid hashes, bounded like live counts."""
        carried = 0
        try:
            path = Path(path)
            self.reset_if_due()
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(data, dict) or set(data) != {"date", "secret", "counts"}:
                    raise ValueError("invalid shape")
                if (not isinstance(data["date"], str)
                        or datetime.date.fromisoformat(data["date"]).isoformat() != data["date"]):
                    raise ValueError("invalid date")
                secret, counts = data["secret"], data["counts"]
                if not isinstance(secret, str) or len(secret) != 64 or len(bytes.fromhex(secret)) != 32:
                    raise ValueError("invalid secret")
                if not isinstance(counts, dict) or any(
                    len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)
                    or type(count) is not int or count < CARRY_MIN
                    for digest, count in counts.items()
                ):
                    raise ValueError("invalid counts")
                if self.limit and data["date"] == self._date.isoformat():
                    self._secret = bytes.fromhex(secret)
                    self._carried = dict(list(counts.items())[:self._max_addresses])
                    carried = len(self._carried)
            finally:
                try:
                    path.unlink(missing_ok=True)
                finally:
                    path.with_name(path.name + ".tmp").unlink(missing_ok=True)
        except FileNotFoundError:
            pass
        except Exception as exc:
            logger.warning("Per-address counts: could not load or remove %s (%s)", path, type(exc).__name__)
        return carried

    def blocked(self, caller: str | None) -> bool:
        """Whether caller's IP (IPv4-mapped IPv6 as IPv4) is in a blocked network; a non-IP caller isn't."""
        if not self._blocked or not isinstance(caller, str):
            return False
        try:
            address = ipaddress.ip_address(caller.strip())
        except ValueError:  # "unknown", a hostname, garbage
            return False
        addresses = [address]
        if address.version == 6 and address.ipv4_mapped is not None:
            addresses.append(address.ipv4_mapped)
        return any(a in network for a in addresses for network in self._blocked)

    def refusal_cause(self, caller: str | None) -> str:
        """The held-back cause when caller is capped: its address is blocked, or has used its day.
        Called as a live lookup is held back for it, so a blocked address is counted for
        /mcp/stats here (addresses.blocked_tried: once a day, never the address itself)."""
        if self.blocked(caller):
            stats.count_address("blocked_tried", self._stats_address(caller))
            return "address_blocked"
        return "address_daily"

    def _stats_address(self, caller: str) -> str:
        """What a blocked address counts as in addresses.blocked_tried: its key (an IPv6 address by
        its /64 on the server), else, when exempt, the address itself."""
        address = ipaddress.ip_address(caller.strip())
        if address.version == 6 and address.ipv4_mapped is not None:
            address = address.ipv4_mapped
        return self._key(caller) or str(address)

    def remaining(self, caller: str | None) -> int | None:
        """Lookups caller may still cause today: 0 when blocked; None when it isn't limited (exempt,
        or no cap)."""
        if self.blocked(caller):
            return 0
        key = self._caller_key(caller)
        return None if key is None else max(0, self.limit - self._counts.get(key, 0))

    def capped(self, caller: str | None) -> bool:
        return self.remaining(caller) == 0

    def record(self, caller: str | None, lookups: int = 1) -> None:
        if self.blocked(caller):
            return
        key = self._caller_key(caller)
        if key is None or lookups <= 0:
            return
        if key not in self._counts and len(self._counts) + len(self._carried) >= self._max_addresses:
            # The oldest carried (unclaimed) or oldest live entry, whichever has fewer lookups: a carried
            # count is 100 or more, so it isn't dropped for a live address with a handful
            carried = next(iter(self._carried), None)
            live = next(iter(self._counts), None)
            if carried is not None and (live is None or self._carried[carried] <= self._counts[live]):
                del self._carried[carried]
            elif live is not None:
                del self._counts[live]
                self._first.pop(live, None)
        if key not in self._counts:  # a count claimed from the carry-over file is already in _counts
            self._first[key] = self._clock()
        before = self._counts.get(key, 0)
        self._counts[key] = before + lookups
        if before < self.limit <= before + lookups:  # once a day per address: the moment it's capped
            moment = datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc)
            first = self._first.get(key)
            if first is None:
                started = "before a restart"
            else:
                started = f"{datetime.datetime.fromtimestamp(first, datetime.timezone.utc):%H:%M} UTC"
                restart = datetime.datetime.fromtimestamp(self._started, datetime.timezone.utc)
                if restart.date() == self._date and first >= self._started:
                    started += f", since a restart at {restart:%H:%M} UTC"
            # Ops commands read the address as the line's ninth field: keep the words before it
            logger.info(f"Mouser and DigiKey per-address limit: {key} reached its {self.limit} lookups "
                        f"for {self._date.isoformat()} at {moment:%H:%M} UTC (first lookup {started})")
            stats.count_address("cap_reached", key)  # /mcp/stats gets a count; only this log line names it

    def error(self, advice: str, caller: str | None = None) -> dict:
        """The reply once caller's address has used its day, or is blocked (advice: the
        distributor's own-key advice)."""
        if self.blocked(caller):
            return {"error": "Live Mouser and DigiKey lookups are turned off for this address on this shared "
                             f"server. Answers pcbparts already has stored still work.{advice}"}
        return {"error": f"This address has used its {self.limit} Mouser and DigiKey lookups "
                         "for today on this shared server; the count resets at 00:00 UTC. "
                         f"Answers pcbparts already has stored still work.{advice}"}


class QuotaStore:
    """JSON file with each DailyQuota's state (today's count, and any pause the API itself asked
    for), so a restart such as a deploy doesn't reset them. Never raises: if the file can't be read
    or written, it logs a warning and the counts live in memory only, as before 0.6.1."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.ok = True  # False while writes are failing
        self._states: dict[str, dict] = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except (OSError, ValueError) as e:
            logger.warning(f"Distributor quota file {self.path} unreadable ({e}); today's counts start from 0")
            return
        if isinstance(data, dict):
            self._states = {name: state for name, state in data.items() if isinstance(state, dict)}
        else:
            logger.warning(f"Distributor quota file {self.path} isn't a JSON object; today's counts start from 0")

    def get(self, name: str) -> dict:
        return dict(self._states.get(name, {}))

    def put(self, name: str, state: dict) -> None:
        self._states[name] = state
        tmp = self.path.with_name(self.path.name + ".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps(self._states, sort_keys=True), encoding="utf-8")
            os.replace(tmp, self.path)  # atomic: a crash leaves the old file or the new one
        except OSError as e:
            if self.ok:  # once per failure streak, not on every request
                logger.warning(f"Distributor quota file {self.path} not writable ({e}); counts are kept in memory only")
            self.ok = False
            return
        self.ok = True


class DailyQuota:
    """Daily request counter with a configurable UTC day start (midnight by default).

    With a QuotaStore the count, and any pause the API asked for (pause()), survive restarts;
    without one they're memory only and a restart starts the day from 0.
    Synchronous — safe for single-threaded asyncio (no lock needed).
    """

    def __init__(self, name: str, daily_limit: int, store: QuotaStore | None = None,
                 clock: Callable[[], float] = time.time, per_minute: int | None = None, own_key: str = "",
                 store_key: str | None = None, day_start_hour: int = 0):
        """per_minute: our cap per rolling minute, kept below the API's own. own_key: what a user
        needs to run the server with their own credentials, named in the limit errors."""
        self._name = name
        self._store_key = name if store_key is None else store_key
        self._limit = daily_limit
        self._store = store
        self._clock = clock
        self._day_start_hour = day_start_hour
        self._per_minute = per_minute
        self._minute = SlidingWindowBudget(per_minute, 60, clock) if per_minute else None
        self._own_key = own_key
        self._count = 0
        self._date = self._today()
        self._paused_until = 0.0  # unix time; the API said its own limit is used up until then
        # "daily" (until the reset the API named), "daily_unknown" (it didn't name one), "burst"
        # (its per-minute limit), "refused" (403) or "invalid_key" (Mouser rejected one of several
        # keys: out until the next Mouser day), or "checking" (a 60-second Mouser check hold)
        self._pause_reason = ""
        self._api_remaining: int | None = None  # the API's own count of requests left today
        self._api_limit: int | None = None
        # Pool-wide penalties are independent of a longer daily pause on this app.
        self._shared_paused_until = 0.0
        self._shared_pause_reason = ""
        self._daily_refusals: list[dict[str, Any]] = []  # private history, kept across UTC days
        self._mouser_state: dict[str, Any] = {}  # private current key index; unused by DigiKey
        self.callers = CallerTally(name, clock)  # who sent them, logged hourly
        if store is not None:
            self._load(store.get(self._store_key))
            self._save()  # at startup, so status() shows whether the file is really writable

    def _today(self) -> datetime.date:
        return datetime.datetime.fromtimestamp(self._clock() - self._day_start_hour * 3600,
                                                datetime.timezone.utc).date()

    def next_reset(self, timestamp: float | None = None) -> float:
        """Next distributor day start; date labels name the UTC date that day began."""
        now = self._clock() if timestamp is None else timestamp
        offset = self._day_start_hour * 3600
        return _next_utc_midnight(now - offset) + offset

    def now(self) -> float:
        return self._clock()

    def _load(self, state: dict) -> None:
        self._daily_refusals = self._clean_daily_refusals(state.get("daily_refusals"))
        if isinstance(state.get("mouser"), dict):
            self._mouser_state = {"current": state["mouser"].get("current", 0)}
        try:
            dates = [self._date.isoformat()]
            # Before the first reset after upgrade, old UTC-day labels can be one day ahead.
            # Only today's UTC date is eligible: a genuinely future label must not keep a count.
            if self._day_start_hour:
                dates.append(datetime.datetime.fromtimestamp(self._clock(), datetime.timezone.utc).date().isoformat())
            if state.get("date") in dates:
                self._count = int(state.get("count", 0))
                remaining, limit = state.get("api_remaining"), state.get("api_limit")
                self._api_remaining = None if remaining is None else int(remaining)
                self._api_limit = None if limit is None else int(limit)
            self._paused_until = float(state.get("paused_until", 0))
            self._pause_reason = str(state.get("pause_reason", ""))
            self._shared_paused_until = float(state.get("shared_paused_until", 0))
            self._shared_pause_reason = str(state.get("shared_pause_reason", ""))
        except (TypeError, ValueError):
            logger.warning(f"{self._name} quota state is malformed ({state!r}); today's count starts from 0")
            self._count, self._paused_until, self._pause_reason = 0, 0.0, ""
            self._api_remaining = self._api_limit = None

    @staticmethod
    def _clean_daily_refusals(value: Any) -> list[dict[str, Any]]:
        """Malformed history is discarded independently of today's counter and pause."""
        if not isinstance(value, list):
            return []
        clean = []
        for episode in value[-30:]:
            if not isinstance(episode, dict) or not {
                    "at", "count", "last_refused_at", "retries", "resumed_at"}.issubset(episode):
                return []
            for field in ("count", "retries"):
                number = episode.get(field)
                if type(number) is not int or number < 0:
                    return []
            for field in ("at", "last_refused_at", "resumed_at"):
                number = episode.get(field)
                if number is None and field == "resumed_at":
                    continue
                if type(number) not in (int, float):
                    return []
                try:
                    _utc_text(number)  # also rejects NaN, infinity and out-of-range timestamps
                except (ValueError, OverflowError, OSError):
                    return []
            clean.append({field: episode[field] for field in
                          ("at", "count", "last_refused_at", "retries", "resumed_at")})
        return clean

    def _save(self) -> None:
        if self._store is not None:
            self._store.put(self._store_key, {
                "date": self._date.isoformat(),
                "count": self._count,
                "paused_until": self._paused_until,
                "pause_reason": self._pause_reason,
                "api_remaining": self._api_remaining,
                "api_limit": self._api_limit,
                "shared_paused_until": self._shared_paused_until,
                "shared_pause_reason": self._shared_pause_reason,
                "daily_refusals": self._daily_refusals,
                **({"mouser": self._mouser_state} if self._mouser_state else {}),
            })

    def _maybe_reset(self) -> None:
        today = self._today()
        if today != self._date:
            self._count = 0
            self._date = today
            self._api_remaining = self._api_limit = None

    def check(self, caller: str | None = None) -> dict | None:
        """Return None if a request may go out (and count it), else an error dict: our daily
        limit is used up, our per-minute cap is, or the API asked us to pause. Nothing is counted
        or sent until the limit resets. caller (an IP) goes in the hourly log of who sent them."""
        self._maybe_reset()
        paused = self.paused_error()
        if paused:
            return paused
        if self._count >= self._limit:
            return self.count_error()
        if self._minute is not None and not self._minute.try_acquire():
            return {"error": f"{self._name} lookups are limited to {self._per_minute} a minute on this shared server. "
                             f"Try again in {math.ceil(self._minute.wait_seconds())} s.{self._advice()}"}
        self._count += 1
        self._save()
        self.callers.record(caller)
        return None

    def count_error(self) -> dict:
        """The error once our own count has used up the day."""
        return {"error": f"{self._name} daily quota exceeded ({self._limit} requests/day on this shared server). "
                         f"It resets at {_utc_text(self.next_reset())}.{self._advice()}"}

    def _advice(self) -> str:
        if self._own_key:
            return (f" To skip the shared limits, run pcbparts-mcp with your own {self._own_key}: {SELF_HOSTING_URL}."
                    " Meanwhile use jlc_search.")
        return " Meanwhile use jlc_search."

    def paused_error(self) -> dict | None:
        """The error dict to return while the API's own limit is used up, else None."""
        now = self._clock()
        if now >= self._paused_until:
            return None
        if self._pause_reason == "daily":
            limit = f"{self._api_limit} requests/day, counted by {self._name}" if self._api_limit else f"counted by {self._name}"
            return {"error": f"{self._name} daily quota exceeded ({limit}). "
                             f"It resets at {_utc_text(self._paused_until)}.{self._advice()}"}
        if self._pause_reason == "daily_unknown":
            return {"error": f"{self._name} daily quota exceeded (counted by {self._name}). "
                             f"This server tries again at {_utc_text(self._paused_until)}.{self._advice()}"}
        wait = math.ceil(self._paused_until - now)
        if self._pause_reason == "refused":
            return {"error": f"{self._name} refused this server's requests (HTTP 403). Try again in {wait} s.{self._advice()}"}
        return {"error": f"{self._name} is limiting requests per minute. Try again in {wait} s.{self._advice()}"}

    def pause(self, until: float, reason: str) -> None:
        """Send nothing until `until` (unix time): the API said its own limit is used up.
        reason is "daily", "daily_unknown", "burst" or "refused" (see __init__)."""
        if reason == "invalid_key" or until > self._paused_until:
            self._paused_until, self._pause_reason = until, reason
            self._save()

    def pause_daily_unknown_reset(self, until: float | None = None, *, sent_at: float | None = None,
                                  sent_count: int | None = None) -> bool:
        """The API refused for its daily limit without a reset header: pause until the supplied
        time, or for an hour. MouserKeyPool schedules its day-start retry and decides when to rotate
        back to this key. A refusal while a daily pause is running answers a request sent before that
        pause began (concurrent batches): it changes nothing, so two refusals together can't
        stretch the pause. Return whether a pause began; keep its refusal episode for logs."""
        now = self._clock()
        if self._pause_reason in ("daily", "daily_unknown") and now < self._paused_until:
            return False
        self._maybe_reset()
        until = now + 3600 if until is None else until
        if until <= self._paused_until:
            return False  # pause() would leave a longer, existing pause alone
        if not self._daily_refusals or self._daily_refusals[-1]["resumed_at"] is not None:
            self._daily_refusals.append({"at": now if sent_at is None else sent_at,
                                         "count": self._count if sent_count is None else sent_count,
                                         "last_refused_at": now,
                                         "retries": 0, "resumed_at": None})
            self._daily_refusals = self._daily_refusals[-30:]
        else:
            self._daily_refusals[-1]["last_refused_at"] = now
            self._daily_refusals[-1]["retries"] += 1
        self.pause(until, "daily_unknown")
        return True

    def clear_expired_pause(self) -> dict[str, Any] | None:
        """After a request went through: forget an ended pause; return any resumed episode."""
        resumed = None
        now = self._clock()
        if now < self._paused_until:  # an answer to a request sent before the pause began
            return None
        # Whatever the pause was last for (a per-minute one can replace an ended daily one's
        # reason): a request that went through ends the open daily-refusal episode
        if self._daily_refusals and self._daily_refusals[-1]["resumed_at"] is None:
            resumed = self._daily_refusals[-1]
            resumed["resumed_at"] = now
        if self._pause_reason or resumed is not None:
            self._pause_reason = ""
            self._save()
        return dict(resumed) if resumed is not None else None

    def daily_refusals(self) -> list[dict[str, Any]]:
        """The kept daily-refusal episodes, oldest first (copies): for the logs only, never a reply."""
        return [dict(episode) for episode in self._daily_refusals]

    def note_response(self, status_code: int, headers: Any, refused_pause: float | None = None) -> None:
        """Follow the API's own limits from its response headers. DigiKey puts
        X-RateLimit-Limit/-Remaining (per day) on every response: record them and pause until the
        reset once none are left. A 429 without that is the per-minute limit: pause for
        Retry-After, else a minute. refused_pause: seconds to pause on a 403 (DigiKey suspends an
        app for 10 minutes for going over its per-second threshold). Mouser sends no such headers
        and reports its limits in the body (MouserClient)."""
        remaining = _header_int(headers, "x-ratelimit-remaining")
        if remaining is not None:
            self.note_api_usage(remaining, _header_int(headers, "x-ratelimit-limit"))
        now = self._clock()
        if remaining == 0:
            self.pause(_daily_reset(headers, now), "daily")
        elif status_code == 429:
            self.pause(now + (_header_int(headers, "retry-after") or 60), "burst")
        elif status_code == 403 and refused_pause:
            self.pause(now + refused_pause, "refused")

    def note_api_usage(self, remaining: int, limit: int | None) -> None:
        """Record the API's own count of requests left today (from its response headers)."""
        self._maybe_reset()
        self._api_remaining = remaining
        if limit is not None:
            self._api_limit = limit
        self._save()

    def retry_after(self) -> int | None:
        """Whole seconds until check() can let a request out (a pause, the day's limit, our
        per-minute cap), or None when one may go now."""
        self._maybe_reset()
        now = self._clock()
        waits = [self._paused_until - now]
        if self._count >= self._limit:
            waits.append(self.next_reset(now) - now)
        if self._minute is not None:
            waits.append(self._minute.wait_seconds())
        wait = max(waits)
        return math.ceil(wait) if wait > 0 else None

    @property
    def remaining(self) -> int:
        self._maybe_reset()
        return max(0, self._limit - self._count)

    def status(self) -> dict[str, Any]:
        """For private stats: today's count and our limit, the API's own count of requests left (None
        when it doesn't report one), when a pause ends (None when not paused), and whether the
        counts survive a restart."""
        self._maybe_reset()
        return {
            "used_today": self._count,
            "limit": self._limit,
            "api_remaining": self._api_remaining,
            "paused_until": _utc_text(self._paused_until) if self._clock() < self._paused_until else None,
            "resets_at": _utc_text(self.next_reset()),
            "kept_across_restarts": self._store is not None and self._store.ok,
        }


class QuotaPool:
    """Use each app's day in order, with one minute budget and shared penalty pauses.

    Selection and reservation are synchronous, so concurrent asyncio callers cannot overdraw
    an app. Daily counts and pauses remain in the individual quotas' store entries. unit names an
    app or key in the logs only ("app" for DigiKey, "key" for Mouser).
    """

    def __init__(self, quotas: list[DailyQuota], per_minute: int | None = None, unit: str = "app",
                 address_daily: AddressDailyQuota | None = None):
        if not quotas:
            raise ValueError("A quota pool needs at least one app")
        self.quotas = quotas
        self._first = quotas[0]
        self._per_minute = per_minute if per_minute is not None else self._first._per_minute
        self._minute = SlidingWindowBudget(self._per_minute, 60, self._first.now) if self._per_minute else None
        self.callers = self._first.callers
        self.held_back = CallerTally(self._first._name, self._first.now, top=None, what="calls held back")
        self.address_daily = address_daily
        self.callers.unit = self._unit = unit
        # The day each later app was first used, so "requests moved to" is logged once a day (a
        # restart that day doesn't repeat it)
        self._switched_day = {index: quota._date for index, quota in enumerate(quotas) if index and quota._count}
        self.last_refusal_cause: str | None = None  # read immediately after acquire(), without await
        for quota in quotas:
            quota._minute = None
            quota.callers = self.callers

    def _active_index(self) -> int | None:
        for index, quota in enumerate(self.quotas):
            quota._maybe_reset()
            if not self._daily_reset_at(quota):
                return index
        return None

    def active_index(self) -> int | None:
        """The app the next request would use, or None when every app's day is spent. Reserves
        nothing."""
        return self._active_index()

    @staticmethod
    def _daily_reset_at(quota: DailyQuota) -> float:
        reset = quota.next_reset() if not quota.remaining else 0.0
        if quota._pause_reason in ("daily", "daily_unknown", "invalid_key") and quota.now() < quota._paused_until:
            reset = max(reset, quota._paused_until)
        return reset

    def _penalty(self) -> tuple[float, str]:
        # Include pauses saved before pools existed, as well as independent shared pauses.
        pauses = [(q._shared_paused_until, q._shared_pause_reason) for q in self.quotas]
        pauses.extend((q._paused_until, q._pause_reason) for q in self.quotas
                      if q._pause_reason in ("burst", "refused"))
        return max(pauses, key=lambda item: item[0])

    def daily_error(self) -> dict:
        resets = [self._daily_reset_at(q) or q.next_reset() for q in self.quotas]
        return {"error": f"{self._first._name} daily quota exceeded on this shared server. "
                         f"It resets at {_utc_text(min(resets))}.{self._first._advice()}"}

    def penalty_error(self) -> dict | None:
        until, reason = self._penalty()
        if self._first.now() < until:
            wait = math.ceil(until - self._first.now())
            if reason == "refused":
                return {"error": f"{self._first._name} refused this server's requests (HTTP 403). "
                                 f"Try again in {wait} s.{self._first._advice()}"}
            return {"error": f"{self._first._name} is limiting requests per minute. "
                             f"Try again in {wait} s.{self._first._advice()}"}
        return None

    def paused_error(self) -> dict | None:
        return self.penalty_error() or (self.daily_error() if self._active_index() is None else None)

    def address_error(self, caller: str | None) -> dict | None:
        if self.address_daily is not None and self.address_daily.capped(caller):
            return self.address_daily.error(self._first._advice(), caller)
        return None

    def pause_cause(self) -> str | None:
        """Anonymous cause of paused_error(), with the same penalty-before-daily precedence."""
        until, reason = self._penalty()
        if self._first.now() < until:
            return {"burst": "distributor_minute", "refused": "distributor_refused"}.get(reason, "other")
        if self._active_index() is None:
            if not any(q.remaining for q in self.quotas):
                return "daily_count"
            if any(q.remaining and q._pause_reason in ("daily", "daily_unknown")
                   and q.now() < q._paused_until for q in self.quotas):
                return "distributor_daily"
            return "other"
        return None

    def retry_after(self, caller: str | None = None) -> int | None:
        """Whole seconds until acquire() can let a request out (a shared penalty, every app's day,
        the shared minute or caller's day), or None when one may go now."""
        now = self._first.now()
        if self.address_error(caller):
            return math.ceil(_next_utc_midnight(now) - now)
        waits = [self._penalty()[0] - now]
        if self._active_index() is None:
            waits.append(min(self._daily_reset_at(q) for q in self.quotas) - now)
        if self._minute is not None:
            waits.append(self._minute.wait_seconds())
        wait = max(waits)
        return math.ceil(wait) if wait > 0 else None

    def acquire(self, caller: str | None = None, *, check_address: bool = True) -> tuple[int | None, dict | None]:
        """Charge every send, but check and count the address only for the first attempt."""
        self.last_refusal_cause = None
        if check_address and (error := self.address_error(caller)):
            self.last_refusal_cause = self.address_daily.refusal_cause(caller)
            return None, error
        error = self.paused_error()
        if error:
            self.last_refusal_cause = self.pause_cause()
            return None, error
        index = self._active_index()
        assert index is not None
        if self._minute is not None and not self._minute.try_acquire():
            self.last_refusal_cause = "minute_cap"
            return None, {"error": f"{self._first._name} lookups are limited to {self._per_minute} a minute on this shared server. "
                                   f"Try again in {math.ceil(self._minute.wait_seconds())} s.{self._first._advice()}"}
        quota = self.quotas[index]
        quota._count += 1
        quota._save()
        if check_address and self.address_daily is not None:
            self.address_daily.record(caller)
        self.callers.record(caller, index)
        if index and self._switched_day.get(index) != quota._date:
            day = (f"the day starting {quota._date} {quota._day_start_hour:02d}:00 UTC"
                   if self._unit == "key" else f"{quota._date} UTC")
            logger.info(f"{quota._name} requests moved to {self._unit} {index + 1} for {day}")
            self._switched_day[index] = quota._date
        return index, None

    def mark_sent(self) -> None:
        """Call right before sending the request acquire() just reserved, with no await between:
        the rolling minute then counts from the send, after any slow save or log write."""
        if self._minute is not None:
            self._minute.restamp_newest()

    def note_response(self, app_index: int, status: int, headers: Any) -> None:
        quota = self.quotas[app_index]
        quota.note_response(status, headers, refused_pause=600)
        remaining = _header_int(headers, "x-ratelimit-remaining")
        if status == 403 or (status == 429 and remaining != 0):
            reason = "refused" if status == 403 else "burst"
            self.share_penalty(quota.now() + (600 if status == 403 else (_header_int(headers, "retry-after") or 60)),
                               reason)

    def share_penalty(self, until: float, reason: str) -> None:
        """Pause every app or key until `until` for a per-minute ("burst") or 403 ("refused")
        refusal. Kept apart from each one's own pause, so a longer daily pause on the app that got
        it can't swallow it: that refusal says the whole pool is sending too fast."""
        for app in self.quotas:
            if until > app._shared_paused_until:
                app._shared_paused_until, app._shared_pause_reason = until, reason
                app._save()

    def _next_order(self) -> list[int]:
        """The quotas in the order _active_index() tries them."""
        return list(range(len(self.quotas)))

    def _next_index(self) -> tuple[int, bool]:
        """The quota the pool will use next, and whether it may be used now: the active one, else,
        with every day spent, the one whose day or pause ends first (ties: the order
        _active_index() tries them in, which then picks it)."""
        index = self._active_index()
        if index is not None:
            return index, True
        order = self._next_order()
        usable = [i for i in order if self.quotas[i]._limit] or order
        return min(usable, key=lambda i: self._daily_reset_at(self.quotas[i])), False

    def status(self) -> dict[str, Any]:
        """Private detail for the quota the pool uses next (_next_index), with the pool's effective
        pause, and from 0.10.12 budgets: each quota's own state in pool order, in_use marking that
        same quota, so the top-level fields always describe the budget in use."""
        selected, active = self._next_index()
        status = self.quotas[selected].status()
        until, _ = self._penalty()
        if not active:
            until = max(until, self._daily_reset_at(self.quotas[selected]))
        status["paused_until"] = _utc_text(until) if self._first.now() < until else None
        status["budgets"] = [{**{key: own[key] for key in ("used_today", "limit", "api_remaining", "paused_until")},
                              "in_use": number == selected}
                             for number, own in enumerate(quota.status() for quota in self.quotas)]
        return status


class MouserKeyPool(QuotaPool):
    """Sticky rotation using each key's pause as its next try; counts are telemetry unless zero."""

    def __init__(self, quotas: list[DailyQuota], per_minute: int | None = None,
                 address_daily: AddressDailyQuota | None = None):
        super().__init__(quotas, per_minute=per_minute, unit="key", address_daily=address_daily)
        current = self._first._mouser_state.get("current", 0)
        self._current = current if type(current) is int and 0 <= current < len(quotas) else 0
        self._checks: dict[int, tuple[float, float | None, bool]] = {}
        self._save_rotation()

    def _save_rotation(self) -> None:
        self._first._mouser_state = {"current": self._current}
        self._first._save()

    def _active_index(self) -> int | None:
        for offset in range(len(self.quotas)):
            index = (self._current + offset) % len(self.quotas)
            quota = self.quotas[index]
            quota._maybe_reset()
            if quota._limit and quota.now() >= self._daily_reset_at(quota):
                if index != self._current:
                    self._current = index
                    self._save_rotation()
                return index
        return None

    def _daily_reset_at(self, quota: DailyQuota) -> float:
        return quota._paused_until if quota._limit else quota.next_reset()

    def _next_order(self) -> list[int]:
        """Rotation order from the current key, as _active_index() tries them."""
        return [(self._current + offset) % len(self.quotas) for offset in range(len(self.quotas))]

    def checking(self) -> bool:
        """Whether a daily-reset check still holds a key while awaiting its reply."""
        return any(index in self._checks and q._pause_reason == "checking" and q.now() < q._paused_until
                   for index, q in enumerate(self.quotas))

    def pause_cause(self) -> str | None:
        cause = super().pause_cause()
        if (cause not in ("distributor_minute", "distributor_refused") and self._active_index() is None
                and any(q._limit for q in self.quotas)):
            return "distributor_daily"
        return cause

    def daily_error(self) -> dict:
        if not any(q._limit and q._pause_reason != "invalid_key" for q in self.quotas):
            return self._first.count_error() if len(self.quotas) == 1 else super().daily_error()
        until = min(self._daily_reset_at(q) for q in self.quotas if q._limit)
        name = self._first._name
        return {"error": f"{name} daily quota exceeded (counted by {name}). "
                         f"This server tries again at {_utc_text(until)}.{self._first._advice()}"}

    @staticmethod
    def _last_refusal(quota: DailyQuota) -> float | None:
        return quota._daily_refusals[-1]["last_refused_at"] if quota._daily_refusals else None

    def sent(self, index: int) -> tuple[float, float | None, bool]:
        quota = self.quotas[index]
        # Snapshot the latest refusal; late replies cannot undo or repeat a newer refusal.
        # An open refusal episode is a check too: a 0.10.8 file can hold one under a later
        # per-minute pause reason.
        open_episode = bool(quota._daily_refusals) and quota._daily_refusals[-1]["resumed_at"] is None
        token = (quota.now(), self._last_refusal(quota),
                 open_episode or quota._pause_reason in ("daily", "daily_unknown", "invalid_key", "checking"))
        if token[2]:
            self._checks[index] = token
            quota._paused_until, quota._pause_reason = token[0] + 60, "checking"
            quota._save()
        return token

    def finished(self, index: int, token: tuple[float, float | None, bool], *, accepted: bool = False) -> dict | None:
        if self._checks.get(index) == token:
            del self._checks[index]  # an older completion cannot remove a newer check
        quota = self.quotas[index]
        if token[1] != self._last_refusal(quota) or quota._pause_reason == "invalid_key":
            return None  # a refusal recorded after this send owns the pause
        if quota._pause_reason == "checking" and (accepted or quota._paused_until == token[0] + 60):
            quota._paused_until, quota._pause_reason = quota.now(), "daily_unknown"
            quota._save()
        if accepted:
            resumed = quota.clear_expired_pause()
            if self._current != index:
                self._current = index
                self._save_rotation()
            return resumed
        return None

    def refuse_daily(self, index: int, token: tuple[float, float | None, bool], sent_count: int) -> bool:
        if self._checks.get(index) == token:
            del self._checks[index]
        quota = self.quotas[index]
        if token[1] != self._last_refusal(quota) or quota._pause_reason == "invalid_key":
            return False
        day = quota.next_reset(token[0]) + 60
        until = day if sent_count >= quota._limit // 2 else min(quota.next_reset(token[0] - 60) + 60, quota.now() + 3600)
        if until <= quota.now():
            until = quota.now() + 3600
        quota._paused_until, quota._pause_reason = 0.0, ""
        quota.pause_daily_unknown_reset(until, sent_at=token[0], sent_count=sent_count)
        if self._current == index:
            self._current = (index + 1) % len(self.quotas)
        self._save_rotation()
        return True


class SlidingWindowBudget:
    """At most ``limit`` requests in any rolling ``window`` seconds.

    Synchronous — safe for single-threaded asyncio (no await between check and record).
    """

    def __init__(self, limit: int, window: float, clock: Callable[[], float] = time.monotonic):
        self._limit = limit
        self._window = window
        self._clock = clock
        self._sent: collections.deque[float] = collections.deque()
        self._next_report = float("-inf")

    def _prune(self, now: float) -> None:
        while self._sent and now - self._sent[0] >= self._window:
            self._sent.popleft()

    def try_acquire(self) -> bool:
        """Record one request and return True, or return False (recording nothing) if over budget."""
        now = self._clock()
        self._prune(now)
        if len(self._sent) >= self._limit:
            return False
        self._sent.append(now)
        return True

    def restamp_newest(self) -> None:
        """Move the newest request's time to now: it goes out later than it was recorded (after a
        synchronous save), and the window must count from when it actually leaves."""
        if self._sent:
            self._sent[-1] = max(self._sent[-1], self._clock())

    @property
    def used(self) -> int:
        self._prune(self._clock())
        return len(self._sent)

    def wait_seconds(self) -> float:
        """Seconds until a request fits again (0 if one fits now)."""
        now = self._clock()
        self._prune(now)
        if len(self._sent) < self._limit:
            return 0.0
        return self._sent[0] + self._window - now

    def report_due(self) -> bool:
        """True at most once per window, so running out can be logged without flooding the log."""
        now = self._clock()
        if now < self._next_report:
            return False
        self._next_report = now + self._window
        return True


class Pacer:
    """Spaces requests at least 1/per_second apart: a burst waits its turn instead of going out at
    once. Callers go one at a time (FIFO lock), each a full interval after the previous one
    actually left. Booking future slots instead would let a stalled event loop wake every
    overdue caller at once and send them together."""

    def __init__(self, per_second: float, clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], Any] = asyncio.sleep):
        self._interval = 1 / per_second
        self._clock = clock
        self._sleep = sleep
        self._last = float("-inf")  # when the previous caller left
        self._lock: asyncio.Lock | None = None  # created in the running loop

    async def wait(self) -> None:
        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            gap = self._last + self._interval - self._clock()
            if gap > 0:
                await self._sleep(gap)
            self._last = self._clock()

    def mark(self) -> None:
        """The request is leaving now: the next caller waits a full interval from here. Call it
        right before sending. Work between wait() and the send (a slow synchronous quota-file
        write, say) then can't shorten the gap: the next caller only runs once this one yields
        at the send, so it measures from this mark."""
        self._last = self._clock()


class Cooldown:
    """Escalating pause after a block: ``base`` seconds, doubling per consecutive block, capped at ``cap``.

    A block reported while a pause is already running doesn't escalate it, so concurrent requests
    that were in flight when the block started count once. A success only clears the strike count
    when no pause is running, so a request from before the block that comes back 200 can't reset
    the escalation (the next block still doubles).

    Synchronous — safe for single-threaded asyncio.
    """

    def __init__(self, base: float, cap: float, clock: Callable[[], float] = time.monotonic):
        self._base = base
        self._cap = cap
        self._clock = clock
        self._until = 0.0
        self._strikes = 0

    @property
    def remaining(self) -> float:
        """Seconds left in the current pause (0 when not paused)."""
        return max(0.0, self._until - self._clock())

    @property
    def active(self) -> bool:
        return self.remaining > 0

    def trip(self) -> float:
        """Start a pause (or keep the running one) and return its remaining seconds."""
        if self.active:
            return self.remaining
        self._strikes += 1
        duration = min(self._base * 2 ** (self._strikes - 1), self._cap)
        self._until = self._clock() + duration
        return duration

    def record_success(self) -> None:
        if not self.active:
            self._strikes = 0
