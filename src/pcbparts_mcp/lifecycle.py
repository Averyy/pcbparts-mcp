"""Part lifecycle from Mouser and DigiKey: their wording normalised to one set of statuses, maker
names compared across catalogs, and part_lifecycle's lookups.

Statuses: active, nrnd (not recommended for new designs), last_time_buy, obsolete and unknown. Each
reading keeps the distributor's own wording (raw) beside it. Readings live in the lifecycle table of
distributor_store.py for LIFECYCLE_TTL (60 days) when active, 30 days when nrnd or last_time_buy
(LIFECYCLE_WINDING_DOWN_TTL), a year when obsolete (LIFECYCLE_OBSOLETE_TTL); unknown and "not
listed" ones 90 days.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from .search.mpn import mpn_key, not_sent_reason, same_jst_part
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
    "discontinued at digikey": "unknown",
}


def mouser_status(lifecycle: str | None) -> tuple[str, str]:
    """(status, raw) for a Mouser result's lifecycle (None when Mouser states none). Mouser's
    "Discontinued" (IsDiscontinued) and anything unlisted are unknown."""
    if not lifecycle:
        return "active", MOUSER_NOT_STATED
    return _MOUSER_STATUSES.get(lifecycle.strip().casefold(), "unknown"), lifecycle


def digikey_status(status_text: str | None, discontinued: bool = False, end_of_life: bool = False) -> tuple[str, str]:
    """(status, raw) from DigiKey's ProductStatus.Status, Discontinued and EndOfLife. EndOfLife on a
    part whose status still says Active (or Not For New Designs) means its last orders are being
    taken; Discontinued (DigiKey stopped selling it) on an Active one says nothing sure about the maker."""
    text = (status_text or "").strip()
    status = _DIGIKEY_STATUSES.get(text.casefold(), "unknown")
    notes = []
    if end_of_life and status in ("active", "nrnd", "unknown"):
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


# Words left out when comparing maker names: company forms and regions ("NXP USA Inc." is NXP,
# "GigaDevice Semicon Beijing" is DigiKey's "GigaDevice Semiconductor (HK) Limited"). Regions only
# when other words are left: JLCPCB's "HK" (HK32 MCUs) is a maker, not a region (_DROPS).
_COMPANY_WORDS = frozenset({
    "inc", "incorporated", "ltd", "limited", "llc", "co", "corp", "corporation", "company", "gmbh", "ag",
    "plc", "sa", "bv", "nv", "srl", "spa", "kk", "the",
})
_REGION_WORDS = frozenset({
    "usa", "us", "america", "americas", "hk", "beijing", "shanghai", "shenzhen", "china", "taiwan", "japan",
    "europe", "asia",
})
_NAME_NOISE = _COMPANY_WORDS | _REGION_WORDS
# The words left out, tried in turn until a name has some words left: "HK Ltd" is "hk", "Ltd" "ltd"
_DROPS = (_NAME_NOISE, _COMPANY_WORDS, frozenset())

# JLCPCB's short names that stand for a longer one, where the short name would match another maker
# by its first word: JLCPCB's "Seiko" is Seiko Instruments (SII's SC-20S, SSP-T7-F and VT-200-F
# crystals, MS412FE batteries), not Seiko Epson, which JLCPCB lists as "Seiko Epson".
_CATALOG_NAMES = {"seiko": "Seiko Instruments"}

# Names keyed (maker_key) as the maker JLCPCB means by them rather than by their alias, which names
# another maker: JLCPCB's "AMS" is ams OSRAM (AS5047P, AS7341, OSRAM LEDs; _MAKER_FAMILIES), while
# the alias "ams" (for jlc_search) is Advanced Monolithic Systems, JLCPCB's maker of AMS1117.
# makers_match still takes "AMS" as either (a BOM's "AMS" can mean an AMS1117's maker). Likewise
# JLCPCB's "Samsung" lists Samsung Semiconductor's DRAM and LEDs (the alias is Samsung
# Electro-Mechanics, MLCCs), its "FUJITSU" Fujitsu Components' relays (alias: RAMXEED/FUJITSU, FRAM),
# its "SEMTECH" the real Semtech (alias: "ST(Semtech)", generic diodes) and its "GD" HER rectifiers
# (alias: GigaDevice). Keyed by the alias, two companies' readings of one number in the lifecycle
# store would share a key, and one would replace the other.
_KEY_NAMES = {
    "ams": "ams OSRAM",
    "samsung": "Samsung Semiconductor",
    "fujitsu": "Fujitsu Components",
    "semtech": "Semtech Corporation",
    "gd": "GD (rectifiers)",
}

# Makers known under names the word rules can't tie together: one company's divisions, or a maker
# and its own sales arm. A name belongs to a family when it matches one of its names (by the word
# rules), and two names of one family are one maker: JLCPCB's "Vishay Intertech" is Mouser's
# "Vishay / Dale" and DigiKey's "Vishay Siliconix"; JLCPCB's "OSRAM Opto Semicon" is "ams OSRAM".
_MAKER_FAMILIES: tuple[tuple[str, ...], ...] = (
    ("Vishay",),
    ("OSRAM", "ams OSRAM", "AMS"),  # JLCPCB's "AMS" is ams OSRAM (AS5047P, AS7341, OSRAM LEDs)
    ("Nippon Chemi-Con", "United Chemi-Con"),  # United Chemi-Con is its US arm; JLCPCB: "NCC(Nippon Chemi-Con)"
    ("Epson", "Seiko Epson"),  # "EPSON", "Epson Timing"
    ("Infineon", "Cypress Semiconductor"),  # Infineon bought Cypress; JLCPCB: "Infineon/Cypress Semicon"
    ("Amphenol ICC", "Amphenol FCI"),  # FCI is Amphenol ICC since Amphenol bought it (2016)
    ("Bel Fuse", "Stewart Connector"),  # Stewart Connector is a Bel Fuse brand
)


def _words(text: str, drop: frozenset[str] = _NAME_NOISE) -> tuple[str, ...]:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold()
    return tuple(word for word in re.findall(r"[a-z0-9]+", text) if word not in drop)


def _resolved(name: str) -> str:
    """The name as its alias resolves, and as _CATALOG_NAMES spells out JLCPCB's short names."""
    resolved = resolve_manufacturer(name)
    return _CATALOG_NAMES.get(resolved.casefold(), resolved)


@dataclass(frozen=True)
class _Name:
    """One word list a maker can be recognised by. short: an abbreviation that stands for a longer
    name elsewhere: the one before a catalog's parenthesised full name ("ST" of "ST(Semtech)", "UMW"
    of "UMW(Youtai Semiconductor ...)"), or one an alias resolves ("ST" is STMicroelectronics). It
    matches only the same letters as a whole name, never another abbreviation and never as the
    start of a longer name: "ST(Semtech)" isn't ST Microelectronics."""
    words: tuple[str, ...]
    short: bool = False


def _is_abbreviation(words: tuple[str, ...]) -> bool:
    return len(words) == 1 and len(words[0]) <= 4


@lru_cache(maxsize=4096)
def _name_forms(name: str) -> tuple[_Name, ...]:
    """Every word list the maker can be recognised by, from its name as given and as its alias
    resolves (JLCPCB's "AMS" is ams OSRAM, while the alias "ams" is Advanced Monolithic Systems):
    the name without parentheses and each parenthesised name, each split at "/" ("SKYWORKS/SILICON
    LABS" is Skyworks and Silicon Labs, Mouser's "Vishay / Dale" is Vishay)."""
    name = _CATALOG_NAMES.get(name.casefold(), name)  # JLCPCB's "Seiko" never stands as "seiko" alone
    resolved = _resolved(name)
    forms: list[_Name] = []
    for text in dict.fromkeys((resolved, name)):
        aliased = text.casefold() != resolved.casefold()  # the name as given, which an alias resolved
        for drop in _DROPS:  # region words kept only for a spelling that is nothing else ("HK")
            if found := _text_forms(text, aliased, drop):
                forms += found
                break
    return tuple(dict.fromkeys(forms))


def _text_forms(text: str, aliased: bool, drop: frozenset[str]) -> list[_Name]:
    """_name_forms of one spelling, leaving out the words in drop."""
    inner = re.findall(r"\(([^)]*)\)", text)
    outer = [_words(part, drop) for part in re.sub(r"\([^)]*\)", " ", text).split("/")]
    forms = [_Name(words, _is_abbreviation(words) and (aliased or (bool(inner) and len(outer) == 1)))
             for words in outer if words]
    return forms + [_Name(words) for part in inner for words in (_words(p, drop) for p in part.split("/")) if words]


# The start of the lifecycle store's maker key for a "not listed" row (the distributor has no part
# with the number, whoever makes it), followed by the spelling asked (not_listed_key): never a
# maker_key, which is words of [a-z0-9], "#" and a name's text, or "" for no name (a reading
# without a maker), so a "not listed" row never replaces a reading.
NOT_LISTED_MAKER_KEY = "*"


def spelling_key(mpn: str | None) -> str:
    """A part number as a distributor's "not listed" applies to it: the spelling asked, ignoring
    case and outer spaces. DigiKey matches that spelling (a miss for LM358-P says nothing about
    LM358P), and whether Mouser's search sets separators aside isn't known, so a miss is kept for
    the spelling asked only; a part a distributor lists is found by mpn_key."""
    return (mpn or "").strip().casefold()


def not_listed_key(mpn: str | None) -> str:
    """The lifecycle store's maker key for a "not listed" row of this spelling."""
    return NOT_LISTED_MAKER_KEY + spelling_key(mpn)


def maker_key(name: str | None) -> str:
    """One maker's key in the lifecycle store ("Texas Instruments Inc." and "Texas Instruments"
    share one): its alias-resolved name without parentheses, by its words.
    Never empty for a name that isn't: a name of region words only keeps them (JLCPCB's maker "HK"
    is "hk"), and one without letters or digits (JLCPCB's "--") is "#" and its text. JLCPCB's
    "AMS" is ams OSRAM's (_KEY_NAMES)."""
    name = (name or "").strip()
    if not name:
        return ""
    resolved = _resolved(_KEY_NAMES.get(name.casefold(), name))
    outer, inner = re.sub(r"\([^)]*\)", " ", resolved), re.findall(r"\(([^)]*)\)", resolved)
    for drop in _DROPS:
        if words := _words(outer, drop) or next((w for part in inner if (w := _words(part, drop))), ()):
            return " ".join(words)
    return "#" + " ".join(resolved.casefold().split())


def _starts(short: tuple[str, ...], long: tuple[str, ...]) -> bool:
    """long begins with short's words, short's last word whole or the start of long's word there.
    "Microchip Tech" is Microchip Technology; a short word must be whole ("ST" isn't STMicroelectronics)."""
    if any(x != y for x, y in zip(short[:-1], long)):
        return False
    last, other = short[-1], long[len(short) - 1]
    return last == other or (len(last) >= 4 and other.startswith(last))


def _names_match(a: _Name, b: _Name) -> bool:
    if "".join(a.words) == "".join(b.words):  # "ST Microelectronics" is STMicroelectronics, "On Semi" onsemi
        return not (a.short and b.short)  # two abbreviations of the same letters can stand for two makers
    if a.short or b.short:
        return False
    x, y = (a.words, b.words) if len(a.words) <= len(b.words) else (b.words, a.words)
    return _starts(x, y) or (len(x) == len(y) and _starts(y, x))


_FAMILY_FORMS = [[_Name(_words(member)) for member in family] for family in _MAKER_FAMILIES]


@lru_cache(maxsize=4096)
def _families(name: str) -> frozenset[int]:
    """The _MAKER_FAMILIES the name belongs to (one of its names matches a member's)."""
    forms = _name_forms(name)
    return frozenset(index for index, members in enumerate(_FAMILY_FORMS)
                     if any(_names_match(form, member) for member in members for form in forms))


def makers_match(a: str | None, b: str | None) -> bool:
    """Whether two catalogs' maker names name the same maker: JLCPCB's "NXP Semicon" and "Microchip
    Tech" are Mouser's NXP Semiconductors and Microchip Technology, and its "Vishay Intertech" is
    DigiKey's "Vishay Siliconix" (_MAKER_FAMILIES)."""
    a, b = (a or "").strip(), (b or "").strip()
    if a and a.casefold() == b.casefold():
        return True
    if any(_names_match(x, y) for x in _name_forms(a) for y in _name_forms(b)):
        return True
    return bool(_families(a) & _families(b))


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
    resolved to both from the catalog). not_sent: why its number isn't worth a request at all
    (search/mpn.py's not_sent_reason)."""
    input: Any
    mpn: str | None = None
    maker: str | None = None
    lcsc: str | None = None
    error: dict[str, Any] | None = None
    not_sent: str | None = None


@dataclass(eq=False)
class _KeyState:
    """What's known about one spelling of an MPN during a call, from the store and this call's
    lookups. readings (parts listed under the number) are shared by every spelling of it (by
    mpn_key: LM358P's listing answers "LM358-P"); not_listed is this spelling's own (spelling_key).
    spelling: the one sent (sendable). An entry whose spelling may not be sent (not_sent) has its
    own state, never sent: in ["10k", "10-k"] only "10-k" goes out, and "10k" still shares the
    number's readings."""
    spelling: str
    sendable: bool = True
    readings: list[Reading] = field(default_factory=list)
    not_listed: dict[str, float] = field(default_factory=dict)  # source -> when it said so
    limited: dict[str, int] = field(default_factory=dict)  # source -> seconds until it may be asked
    day_spent: set[str] = field(default_factory=set)  # sources limited because their whole day is spent
    failed: set[str] = field(default_factory=set)

    def add(self, reading: Reading) -> None:
        if reading.found:
            if reading not in self.readings:  # a reading every spelling of the number shares
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
    requests, and to DigiKey only when Mouser doesn't list them (for the maker given) or can't be
    asked today: Mouser's daily limit is spent, or Mouser isn't configured. A Mouser per-minute
    pause leaves the part unknown with retry_after, and a failed Mouser lookup with lookup_failed,
    without asking DigiKey: a minute's wait or a fault isn't a reason to spend DigiKey's smaller day.
    Mouser listing the part with a status it can't name (unknown) doesn't send it to DigiKey either.

    When DigiKey's lookups spend no daily quota (DigiKeyClient.unmetered: no API credentials) the
    order turns round: DigiKey first, for every part at once (DigiKeyClient.lifecycle), then Mouser
    for the parts DigiKey doesn't list for the maker, couldn't be asked about or failed on.

    Nothing goes out for a number neither distributor can list (Entry.not_sent: a value such as
    "10k", a BOM placeholder, an LCSC code, non-ASCII, not 3-40 characters). Both clients write
    what they fetch into the store and their answer cache, as for mouser_get_part and
    digikey_get_part. Each spelling of a number is asked about until a distributor lists the part
    (spelling_key)."""

    def __init__(self, store: DistributorStore, mouser: MouserClient | None = None,
                 digikey: DigiKeyClient | None = None):
        self._store = store
        self._mouser = mouser
        self._digikey = digikey

    async def answer(self, entries: list[Entry], caller: str | None = None) -> list[dict[str, Any]]:
        from . import stats

        pairs = list(zip(entries, self._states(entries)))
        digikey_first = self._digikey is not None and getattr(self._digikey, "unmetered", False) is True
        for state in dict.fromkeys(state for _, state in pairs if state is not None):
            if not state.sendable and not state.readings and not state.not_listed:
                # No request: counted under the distributor it would have gone to first
                stats.count_distributor("mouser" if self._mouser is not None and not digikey_first else "digikey",
                                        "skipped")

        # A part with a reading is never asked
        if digikey_first:
            await self._ask_digikey_batch(self._unanswered(pairs, "digikey"), caller)
            await self._ask_mouser(self._unanswered(pairs, "mouser"), caller)
        else:  # Mouser first, then DigiKey for what it doesn't list or can't answer today
            await self._ask_mouser(self._unanswered(pairs, "mouser"), caller)
            await self._ask_digikey(self._unanswered(pairs, "digikey", self._digikey_may_ask), caller)
        return [self._result(entry, state) for entry, state in pairs]

    def _states(self, entries: list[Entry]) -> list[_KeyState | None]:
        """Each entry's _KeyState (None for an entry with an error), with what the store knows: one
        per spelling that may be sent (spelling_key), and one per number for the entries that may
        not, all sharing the number's readings (mpn_key)."""
        shared: dict[str, list[Reading]] = {}  # mpn_key -> the number's readings
        sendable: dict[tuple[str, str], _KeyState] = {}
        unsendable: dict[str, _KeyState] = {}

        def new_state(spelling: str, may_send: bool) -> _KeyState:
            state = _KeyState(spelling, may_send, shared.setdefault(mpn_key(spelling), []))
            for reading in self._store.readings(spelling):  # the number's readings, this spelling's misses
                state.add(reading)
            return state

        for entry in entries:
            if entry.error is None:
                entry.not_sent = not_sent_reason(entry.mpn or "")
                identity = (mpn_key(entry.mpn or ""), spelling_key(entry.mpn))
                if not entry.not_sent and identity not in sendable:
                    sendable[identity] = new_state(entry.mpn or "", True)
        states: list[_KeyState | None] = []
        for entry in entries:
            key = mpn_key(entry.mpn or "")
            if entry.error is not None:
                states.append(None)
            elif not entry.not_sent:
                states.append(sendable[(key, spelling_key(entry.mpn))])
            else:
                if key not in unsendable:
                    unsendable[key] = new_state(entry.mpn or "", False)
                states.append(unsendable[key])
        return states

    @staticmethod
    def _digikey_may_ask(state: _KeyState) -> bool:
        """DigiKey is asked unless Mouser failed or only paused for a minute (see the class)."""
        if "mouser" in state.failed:
            return False
        return "mouser" not in state.limited or "mouser" in state.day_spent

    @staticmethod
    def _unanswered(pairs: list[tuple[Entry, _KeyState | None]], source: str, may_ask: Any = None) -> list[_KeyState]:
        """The spellings that may be sent (Entry.not_sent) and that some entry has no reading for
        (for its maker, if given), that this source hasn't answered yet and may be asked (may_ask:
        a test of the spelling's state)."""
        wanted: dict[_KeyState, None] = {}
        for entry, state in pairs:
            if state is not None and not entry.not_sent:
                if not state.matching(entry.maker) and not state.knows(source) and (may_ask is None or may_ask(state)):
                    wanted[state] = None
        return list(wanted)

    async def _ask_mouser(self, wanted: list[_KeyState], caller: str | None) -> None:
        if self._mouser is None or not wanted:
            return
        from .mouser import MOUSER_MAX_BATCH, MouserAPIError, MouserError

        states = {spelling_key(state.spelling): state for state in wanted}
        # Each 3-40 characters already: _unanswered gives only spellings not_sent_reason lets through
        numbers = [state.spelling for state in wanted]
        chunks = [numbers[i:i + MOUSER_MAX_BATCH] for i in range(0, len(numbers), MOUSER_MAX_BATCH)]

        async def ask(chunk: list[str]) -> None:
            try:
                answers, error = await self._mouser.lookup(chunk, caller=caller)
            except (MouserError, MouserAPIError) as e:
                logger.warning(f"part_lifecycle: Mouser lookup failed: {type(e).__name__}: {e}")
                answers, error = None, None
            except Exception as e:  # anything else: those parts' lookups failed
                logger.error(f"part_lifecycle: Mouser lookup failed: {type(e).__name__}")
                answers, error = None, None
            for number in chunk:
                state = states[spelling_key(number)]
                answer = answers.get(number) if answers is not None else None
                # A limit held the number's request back (with the reply's error, or for that number
                # alone), or Mouser's 50-result cap crowded it out of a reply and a limit kept it from
                # being asked again (Mouser may list it); else it failed, or came back crowded again
                if answers is None:
                    state.failed.add("mouser")
                elif answer is None or isinstance(answer.problem, dict) or (
                        answer.problem is None and not answer.checked and self._mouser.held_back(caller)):
                    if answer is None and error is None:
                        state.failed.add("mouser")
                        continue
                    state.limited["mouser"] = self._mouser.retry_after(caller)
                    if self._mouser.day_spent(caller):
                        state.day_spent.add("mouser")
                elif not answer.checked:
                    state.failed.add("mouser")
                else:
                    for result in _own_listings(answer.results, number):
                        status, raw = result.get("lifecycle_status") or "unknown", result.get("lifecycle") or MOUSER_NOT_STATED
                        state.add(Reading(result.get("mfr_part_number") or number, result.get("manufacturer") or "",
                                          "mouser", status, raw, answer.fetched_at))
                    if not any(r.source == "mouser" for r in state.readings):
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
                state.limited["digikey"] = self._digikey.retry_after(caller)
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

    async def _ask_digikey_batch(self, wanted: list[_KeyState], caller: str | None = None) -> None:
        """DigiKey without a daily quota: every wanted spelling in one DigiKeyClient.lifecycle call
        (caller's address day still applies)."""
        if self._digikey is None or not wanted:
            return
        try:
            answers = await self._digikey.lifecycle([state.spelling for state in wanted], caller=caller)
        except Exception as e:  # those parts' lookups failed; Mouser is asked instead
            logger.error(f"part_lifecycle: DigiKey lookup failed: {type(e).__name__}")
            answers = {}
        for state in wanted:
            answer = answers.get(state.spelling.strip())
            if answer is None or answer.kind == "failed":
                state.failed.add("digikey")
            elif answer.kind == "limited":
                state.limited["digikey"] = answer.retry_after or 60
            elif answer.kind == "not_found":
                state.add(Reading(state.spelling, "", "digikey", "unknown", None, answer.fetched_at, found=False))
            else:
                for reading in answer.readings:
                    state.add(reading)

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
        # An entry with not_sent has a state of its own that no lookup goes out for (_states), so
        # no limit or failure of another spelling's lookup is its own
        if state.limited:
            result["retry_after"] = min(state.limited.values())
        elif state.failed:
            result["lookup_failed"] = True
        elif not state.readings:
            if state.not_listed:
                result["not_found"] = True
                result["observed_at"] = utc_text(min(state.not_listed.values()))
            elif not entry.not_sent:  # neither distributor could be asked about this number
                result["lookup_failed"] = True
        if entry.not_sent:  # no lookup went out for it: its number can't be one they list
            result["not_sent"] = entry.not_sent
        return result


def _own_listings(results: list[dict[str, Any]], number: str) -> list[dict[str, Any]]:
    """The results that are the part asked: its MPN or Mouser PN (mpn_key, as mouser._identifies
    compares them: 595-LM358P is Mouser's LM358P), and for a maker without one, the JST part the
    number names without the (LF)/(SN) endings. A JST part Mouser lists under both spellings is read
    from the one spelled as asked: the two can have different statuses."""
    key = mpn_key(number)
    exact = [r for r in results if key and key in (mpn_key(r.get("mfr_part_number") or ""),
                                                   mpn_key(r.get("part_number") or ""))]
    return exact + [r for r in results if r not in exact
                    and same_jst_part(r.get("mfr_part_number") or "", number, r.get("manufacturer") or "")
                    and not any(makers_match(r.get("manufacturer"), e.get("manufacturer")) for e in exact)]
