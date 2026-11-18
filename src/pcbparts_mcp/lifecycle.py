"""Part lifecycle from Mouser and DigiKey: their wording normalised to one set of statuses, maker
names compared across catalogs, and part_lifecycle's lookups.

Statuses: active, nrnd (not recommended for new designs), last_time_buy, obsolete and unknown. Each
reading keeps the distributor's own wording (raw) beside it. Readings live in the lifecycle table of
distributor_store.py for LIFECYCLE_TTL (90 days); "not listed" and unknown ones for a week.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import re
import unicodedata
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .search.mpn import mpn_key, same_jst_part
from .search.resolvers import resolve_manufacturer

if TYPE_CHECKING:
    from .digikey import DigiKeyClient
    from .distributor_store import DistributorStore
    from .mouser import MouserClient

logger = logging.getLogger(__name__)

STATUSES = ("active", "nrnd", "last_time_buy", "obsolete", "unknown")
# Mouser leaves the status blank for normal active parts (it states New Product, NRND, End of Life
# and Obsolete), so a part it lists with no status counts as active, with this as its wording
MOUSER_NOT_STATED = "not stated by Mouser"

_MOUSER_STATUSES = {
    "not recommended for new designs": "nrnd",
    "end of life": "last_time_buy",
    "obsolete": "obsolete",
    "new product": "active",
    "new at mouser": "active",
}
# "Discontinued at Digi-Key" is DigiKey's own stocking, not the maker's lifecycle
_DIGIKEY_STATUSES = {
    "active": "active",
    "not for new designs": "nrnd",
    "last time buy": "last_time_buy",
    "obsolete": "obsolete",
    "discontinued at digi-key": "unknown",
}


def mouser_status(lifecycle: str | None) -> tuple[str, str]:
    """(status, raw) for a Mouser result's lifecycle (None when Mouser states none). Mouser's
    "Discontinued" (IsDiscontinued) and anything unlisted are unknown."""
    if not lifecycle:
        return "active", MOUSER_NOT_STATED
    return _MOUSER_STATUSES.get(lifecycle.strip().casefold(), "unknown"), lifecycle


def digikey_status(status_text: str | None, discontinued: bool = False, end_of_life: bool = False) -> tuple[str, str]:
    """(status, raw) from DigiKey's ProductStatus.Status, Discontinued and EndOfLife. EndOfLife on a
    part whose status still says Active means its last orders are being taken; Discontinued
    (DigiKey stopped selling it) on an Active one says nothing sure about the maker."""
    text = (status_text or "").strip()
    status = _DIGIKEY_STATUSES.get(text.casefold(), "unknown")
    notes = []
    if end_of_life and status in ("active", "unknown"):
        status = "last_time_buy"
        notes.append("end of life")
    elif discontinued and status == "active":
        status = "unknown"
    if discontinued and "discontinued" not in text.casefold():
        notes.append("discontinued at DigiKey")
    raw = text or "Unknown"
    return status, raw + (f" ({', '.join(notes)})" if notes else "")


def last_buy_date(value: Any) -> str | None:
    """DigiKey's DateLastBuyChance as YYYY-MM-DD, or None when absent or a placeholder date."""
    if not isinstance(value, str) or not re.match(r"\d{4}-\d{2}-\d{2}", value.strip()):
        return None
    date = value.strip()[:10]
    return date if date >= "1990-01-01" else None


# Words left out when comparing maker names: company forms and regions ("NXP USA Inc." is NXP)
_NAME_NOISE = frozenset({
    "inc", "incorporated", "ltd", "limited", "llc", "co", "corp", "corporation", "company", "gmbh", "ag",
    "plc", "sa", "bv", "nv", "srl", "spa", "kk", "usa", "us", "america", "americas", "the",
})


def _words(text: str) -> tuple[str, ...]:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold()
    return tuple(word for word in re.findall(r"[a-z0-9]+", text) if word not in _NAME_NOISE)


def maker_names(name: str | None) -> list[tuple[str, ...]]:
    """The word lists a maker can be recognised by: its name without parentheses, and each
    parenthesised name (JLCPCB writes "UMW(Youtai Semiconductor Co., Ltd.)"). Aliases such as TI
    resolve first."""
    name = resolve_manufacturer((name or "").strip())
    outer = re.sub(r"\([^)]*\)", " ", name)
    names = [_words(outer), *(_words(inner) for inner in re.findall(r"\(([^)]*)\)", name))]
    return [words for words in names if words]


def maker_key(name: str | None) -> str:
    """One maker's key in the lifecycle store ("Texas Instruments Inc." and "Texas Instruments" share one)."""
    names = maker_names(name)
    return " ".join(names[0]) if names else ""


def _starts(short: tuple[str, ...], long: tuple[str, ...]) -> bool:
    """long begins with short's words, short's last word whole or the start of long's word there.
    "Microchip Tech" is Microchip Technology; a short word must be whole ("ST" isn't STMicroelectronics)."""
    if any(x != y for x, y in zip(short[:-1], long)):
        return False
    last, other = short[-1], long[len(short) - 1]
    return last == other or (len(last) >= 4 and other.startswith(last))


def _names_match(a: tuple[str, ...], b: tuple[str, ...]) -> bool:
    if len(a) > len(b):
        a, b = b, a
    return _starts(a, b) or (len(a) == len(b) and _starts(b, a))


def makers_match(a: str | None, b: str | None) -> bool:
    """Whether two catalogs' maker names name the same maker: JLCPCB's "NXP Semicon" and "Microchip
    Tech" are Mouser's NXP Semiconductors and Microchip Technology."""
    return any(_names_match(x, y) for x in maker_names(a) for y in maker_names(b))


def utc_text(timestamp: float) -> str:
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).isoformat(timespec="seconds")


@dataclass
class Reading:
    """One distributor's lifecycle for one maker's part, or (found=False) that the distributor
    doesn't list the part number at all."""
    mpn: str
    maker: str
    source: str  # "mouser" or "digikey"
    status: str
    raw: str | None
    observed_at: float
    found: bool = True
    last_buy_date: str | None = None

    @property
    def stated(self) -> bool:
        """The distributor stated a status (Mouser's blank isn't one)."""
        return self.found and self.status != "unknown" and self.raw != MOUSER_NOT_STATED

    def rank(self) -> tuple[int, float]:
        """Lower is better: a stated status, then Mouser's unstated active, then unknown; newest first."""
        tier = 0 if self.stated else 1 if self.status == "active" else 2
        return tier, -self.observed_at

    def as_reply(self) -> dict[str, Any]:
        reply = {"manufacturer": self.maker, "status": self.status, "raw": self.raw, "source": self.source,
                 "observed_at": utc_text(self.observed_at)}
        if self.last_buy_date:
            reply["last_buy_date"] = self.last_buy_date
        return reply


@dataclass
class Entry:
    """One part_lifecycle input: what was given, and the MPN and maker to look up (an LCSC code is
    resolved to both from the catalog)."""
    input: Any
    mpn: str | None = None
    maker: str | None = None
    lcsc: str | None = None
    error: dict[str, Any] | None = None


@dataclass
class _KeyState:
    """What's known about one MPN (by mpn_key) during a call, from the store and this call's lookups."""
    spelling: str
    readings: list[Reading] = field(default_factory=list)
    not_listed: dict[str, float] = field(default_factory=dict)  # source -> when it said so
    limited: dict[str, int] = field(default_factory=dict)  # source -> seconds until it may be asked
    failed: set[str] = field(default_factory=set)

    def add(self, reading: Reading) -> None:
        if reading.found:
            self.readings.append(reading)
        else:
            self.not_listed[reading.source] = max(self.not_listed.get(reading.source, 0.0), reading.observed_at)

    def knows(self, source: str) -> bool:
        """This source's answer for the number is known: a reading of any maker, or "not listed"."""
        return source in self.not_listed or any(r.source == source for r in self.readings)

    def matching(self, maker: str | None, source: str | None = None) -> list[Reading]:
        return [r for r in self.readings if (source is None or r.source == source)
                and (not maker or makers_match(r.maker, maker))]


def _best_per_maker(readings: list[Reading]) -> list[Reading]:
    """The best reading of each maker, with makers_match deciding which names are one maker (Mouser's
    "NXP Semiconductors" is DigiKey's "NXP USA Inc.")."""
    best: list[Reading] = []
    for reading in sorted(readings, key=Reading.rank):
        if not any(makers_match(kept.maker, reading.maker) for kept in best):
            best.append(reading)
    return best


class LifecycleLookup:
    """part_lifecycle: answers from the store; parts it doesn't have go to Mouser in 10-part
    requests, and to DigiKey when Mouser doesn't list them (or can't be asked). Both clients write
    what they fetch into the store and their 3-day answer cache, as for mouser_get_part and
    digikey_get_part."""

    def __init__(self, store: DistributorStore, mouser: MouserClient | None = None,
                 digikey: DigiKeyClient | None = None):
        self._store = store
        self._mouser = mouser
        self._digikey = digikey

    async def answer(self, entries: list[Entry], caller: str | None = None) -> list[dict[str, Any]]:
        states: dict[str, _KeyState] = {}
        for entry in entries:
            if entry.error is None:
                key = mpn_key(entry.mpn or "")
                if key not in states:
                    states[key] = state = _KeyState(entry.mpn or "")
                    for reading in self._store.readings(entry.mpn or ""):
                        state.add(reading)

        # Mouser first, then DigiKey for what it doesn't list; a part with a reading is never asked
        await self._ask_mouser(self._unanswered(entries, states, "mouser"), caller)
        await self._ask_digikey(self._unanswered(entries, states, "digikey"), caller)
        return [self._result(entry, states.get(mpn_key(entry.mpn or ""))) for entry in entries]

    @staticmethod
    def _unanswered(entries: list[Entry], states: dict[str, _KeyState], source: str) -> list[_KeyState]:
        """The numbers some entry has no reading for (for its maker, if given), that this source
        hasn't answered yet."""
        wanted: dict[str, _KeyState] = {}
        for entry in entries:
            if entry.error is None:
                key = mpn_key(entry.mpn or "")
                state = states[key]
                if not state.matching(entry.maker) and not state.knows(source):
                    wanted[key] = state
        return list(wanted.values())

    async def _ask_mouser(self, wanted: list[_KeyState], caller: str | None) -> None:
        if self._mouser is None or not wanted:
            return
        from .mouser import MOUSER_MAX_BATCH, MouserAPIError, MouserError

        states = {mpn_key(state.spelling): state for state in wanted}
        numbers = [state.spelling for state in wanted if 3 <= len(state.spelling) <= 40]
        chunks = [numbers[i:i + MOUSER_MAX_BATCH] for i in range(0, len(numbers), MOUSER_MAX_BATCH)]

        async def ask(chunk: list[str]) -> None:
            try:
                answers, error = await self._mouser.lookup(chunk, caller=caller)
            except (MouserError, MouserAPIError) as e:
                logger.warning(f"part_lifecycle: Mouser lookup failed: {type(e).__name__}: {e}")
                answers, error = None, None
            except Exception as e:  # anything else: DigiKey may still answer
                logger.error(f"part_lifecycle: Mouser lookup failed: {type(e).__name__}")
                answers, error = None, None
            for number in chunk:
                state = states[mpn_key(number)]
                if error is not None:
                    state.limited["mouser"] = self._mouser.retry_after()
                elif answers is None:
                    state.failed.add("mouser")
                else:
                    answer = answers[number]
                    # The part itself, or the JST part it names without the (LF)/(SN) endings
                    found = [r for r in answer.results if mpn_key(r.get("mfr_part_number") or "") == mpn_key(number)
                             or same_jst_part(r.get("mfr_part_number") or "", number, r.get("manufacturer") or "")]
                    for result in found:
                        status, raw = result.get("lifecycle_status") or "unknown", result.get("lifecycle") or MOUSER_NOT_STATED
                        state.add(Reading(result.get("mfr_part_number") or number, result.get("manufacturer") or "",
                                          "mouser", status, raw, answer.fetched_at))
                    if not found:
                        state.add(Reading(number, "", "mouser", "unknown", None, answer.fetched_at, found=False))

        await asyncio.gather(*(ask(chunk) for chunk in chunks))

    async def _ask_digikey(self, wanted: list[_KeyState], caller: str | None) -> None:
        if self._digikey is None or not wanted:
            return
        from .digikey import DigiKeyError

        async def ask(state: _KeyState) -> None:
            try:
                reply, kind, fetched_at = await self._digikey.lookup(state.spelling, caller=caller)
            except DigiKeyError as e:
                logger.warning(f"part_lifecycle: DigiKey lookup failed: {type(e).__name__}: {e}")
                state.failed.add("digikey")
                return
            except Exception as e:
                logger.error(f"part_lifecycle: DigiKey lookup failed: {type(e).__name__}")
                state.failed.add("digikey")
                return
            if kind == "limited":
                state.limited["digikey"] = self._digikey.retry_after()
            elif kind == "not_found":
                state.add(Reading(state.spelling, "", "digikey", "unknown", None, fetched_at, found=False))
            elif kind == "found":
                # The client filed each part's reading under this number too (with DigiKey's full
                # wording); from the reply only if the store couldn't keep them
                readings = [r for r in self._store.readings(state.spelling) if r.source == "digikey" and r.found]
                readings = readings or [
                    Reading(result.get("mfr_part_number") or state.spelling, result.get("manufacturer") or "",
                            "digikey", result.get("lifecycle_status") or "unknown", result.get("lifecycle"),
                            fetched_at, last_buy_date=result.get("last_buy_date"))
                    for result in reply.get("results") or []]
                for reading in readings:
                    state.add(reading)
            else:
                state.failed.add("digikey")

        await asyncio.gather(*(ask(state) for state in wanted))

    @staticmethod
    def _result(entry: Entry, state: _KeyState | None) -> dict[str, Any]:
        result: dict[str, Any] = {"input": entry.input}
        if entry.lcsc:
            result["lcsc"] = entry.lcsc
        if entry.error is not None or state is None:
            return {**result, "status": "unknown", **(entry.error or {})}
        result["mpn"] = entry.mpn
        matching = state.matching(entry.maker)
        # A maker given: its best reading, whatever each distributor calls it; else one per maker
        matching = sorted(matching, key=Reading.rank)[:1] if entry.maker else _best_per_maker(matching)
        if len(matching) == 1:
            return {**result, **matching[0].as_reply()}
        if matching:  # several makers list the number and none was given
            statuses = {r.status for r in matching}
            return {**result, "status": statuses.pop() if len(statuses) == 1 else "unknown",
                    "makers": [r.as_reply() for r in matching]}
        result["status"] = "unknown"
        if entry.maker:
            result["manufacturer"] = entry.maker
            others = _best_per_maker(state.readings)
            if others:  # listed, but only under other makers
                result["makers"] = [r.as_reply() for r in others]
        if state.limited:
            result["retry_after"] = min(state.limited.values())
        elif state.failed:
            result["lookup_failed"] = True
        elif not state.readings:
            if state.not_listed:
                result["not_found"] = True
                result["observed_at"] = utc_text(min(state.not_listed.values()))
            else:  # neither distributor could be asked about this number
                result["lookup_failed"] = True
        return result
