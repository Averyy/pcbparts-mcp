"""DigiKey lookups for an instance run without API credentials (only where enabled()).

A lookup is one part number: the product list for it (suggestions; the keyword search as well when
that list has no exact match, or 5 or more), then each exact product's page, 4 at a time at most.
More than DIGIKEY_MAX_RESULTS exact products: one comparison request gives every maker's status and
stock, and pages are read for the ones with most stock. The reply is in DigiKeyClient's usual shape.

Requests: at most DIGIKEY_SITE_CONCURRENCY in flight and DIGIKEY_SITE_PER_SECOND starts a second,
across all lookups; a request that finds every slot taken waits up to DIGIKEY_SITE_SLOT_WAIT. A
refusal (challenge, 403, 429, a second F5 400, HTML where JSON was expected) pauses every lookup
for DIGIKEY_SITE_PAUSE, doubling at each refusal in a row up to DIGIKEY_SITE_PAUSE_MAX, with one
ERROR log line; after the pause the first lookup tests it while the others wait for its answer.
Anything else that goes wrong (a timeout, a 5xx or other 4xx, an answer of a shape this code
doesn't know) fails that lookup only; three in a row count as a refusal.
The pause lives in memory: a restart clears it.
"""

from __future__ import annotations

import asyncio
import contextvars
import datetime
import json
import logging
import math
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable
from urllib.parse import quote

import wafer

from .cache import Cooldown, Pacer
from .client import _count_upstream, _sent
from .config import (
    DIGIKEY_LOCALE_CURRENCY, DIGIKEY_LOCALE_LANGUAGE, DIGIKEY_LOCALE_SITE, DIGIKEY_MAX_RESULTS, number_setting,
)
from .lifecycle import digikey_status, maker_key, makers_match
from .search.mpn import mpn_key, same_jst_part

logger = logging.getLogger(__name__)


def enabled() -> bool:
    """Whether this instance looks DigiKey parts up this way when it has no API credentials
    (DIGIKEY_LOOKUP=site); off by default, when DigiKey needs credentials as always."""
    return (os.getenv("DIGIKEY_LOOKUP") or "").strip().casefold() == "site"


# Requests in flight and starts a second across all lookups, the longest a request waits for a
# free slot (a 100-part BOM sent at once is about 230 requests, 46 s at 5 a second: callers wait
# rather than get "busy"), and the pause after a refusal: 5 minutes, doubling at each refusal in a
# row (10, 20, 40 minutes...) up to 12 hours, so a block that lasts is tried again twice a day; a
# lookup that works starts the doubling over
DIGIKEY_SITE_CONCURRENCY = number_setting("DIGIKEY_LOOKUP_CONCURRENCY", 4, 1)
DIGIKEY_SITE_PER_SECOND = number_setting("DIGIKEY_LOOKUP_PER_SECOND", 5.0, 0.1)
DIGIKEY_SITE_SLOT_WAIT = 90.0
DIGIKEY_SITE_PAUSE = 300.0
DIGIKEY_SITE_PAUSE_MAX = 12 * 3600.0
DIGIKEY_SITE_TIMEOUT = 20.0  # wafer's total budget per request...
DIGIKEY_SITE_ATTEMPT_TIMEOUT = 8.0  # ...and per attempt, so its one retry fits

BASE_URL = "https://www.digikey.com/products/api/v5"
# F5's answer to a session's first request: it sets the cookie the next request carries
_F5_REFUSAL = b'"Invalid Request."'
SUGGESTIONS = 20  # the most the product list gives
SEARCH_WHEN_EXACT = 5  # this many exact products in it may not be all: ask the search too
MAX_HOPS = 4  # keyword-search redirects followed (category -> listing -> ...)
COMPARE_CHUNK = 250  # product ids per comparison request (the site takes 500)
FAILURES_BEFORE_PAUSE = 3  # failed lookups of this many different numbers in a row pause like a refusal
# Attributes that are reply fields of their own, not parameters
_NOT_PARAMETERS = frozenset({"mfr", "manufacturer", "series", "base product number", "packaging", "part status",
                             "product status"})
_DETAIL_URL = re.compile(r"/products/detail/([^/]+)/[^/]+/(\d+)")
_LISTING_URL = re.compile(r"/products/(?:category|filter)/(?:[^/?]+/)*(\d+)\?s=([^&#]+)")


class SiteRefused(Exception):
    """The site refused this server: a challenge, 403, 429, F5's 400 twice, or a page (HTML) where
    JSON was expected. Every lookup pauses at once."""


class SiteFailed(Exception):
    """One lookup's failure: a timeout, no connection, a 5xx, another 4xx, or an answer this code
    doesn't know (one number's oddity, or a change on DigiKey's side, which then fails every
    lookup). That lookup fails; FAILURES_BEFORE_PAUSE in a row pause as a refusal does."""


class SiteUnavailable(Exception):
    """No lookup can be made now: paused after a refusal, or every request slot stayed taken.
    retry_after: seconds until one may be; sent: whether any of this lookup's requests went out;
    refused: whether DigiKey refused one of them (a pause after a run of failures isn't one)."""

    def __init__(self, retry_after: int, paused: bool, sent: bool = False, refused: bool = False):
        super().__init__("paused" if paused else "busy")
        self.retry_after = retry_after
        self.paused = paused
        self.sent = sent
        self.refused = refused


# What reading an answer of an unexpected shape raises: the site changed (or this code is wrong)
_UNREADABLE = (KeyError, TypeError, ValueError, AttributeError, IndexError)

# The running lookup's count of requests sent (a one-item list, shared with the tasks it starts)
_lookup_sends: contextvars.ContextVar[list[int] | None] = contextvars.ContextVar("digikey_lookup_sends", default=None)




@dataclass
class SiteAnswer:
    """A lookup's answer: results in DigiKeyClient's reply shape (most stock first, at most
    DIGIKEY_MAX_RESULTS), statuses (mpn, maker, Part Status text, last-buy date) for every exact
    product, beyond the results too, and the results' product ids. No results: not listed."""
    results: list[dict[str, Any]] = field(default_factory=list)
    statuses: list[tuple[str, str, str | None, str | None]] = field(default_factory=list)
    product_ids: list[int] = field(default_factory=list)


# --- lz-string's URI-safe form, as the site encodes its state parameter (lz-string 1.5) ---

_LZ_KEYS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$"
_LZ_INDEX = {char: index for index, char in enumerate(_LZ_KEYS)}


def lz_encode(text: str) -> str:
    """lz-string's compressToEncodedURIComponent (6 bits a character)."""
    dictionary: dict[str, int] = {}
    to_create: set[str] = set()
    out: list[str] = []
    value = position = 0
    enlarge_in, dict_size, num_bits = 2, 3, 2

    def write(number: int, bits: int) -> None:
        nonlocal value, position
        for _ in range(bits):
            value = (value << 1) | (number & 1)
            if position == 5:
                out.append(_LZ_KEYS[value])
                value = position = 0
            else:
                position += 1
            number >>= 1

    def emit(word: str) -> None:
        nonlocal enlarge_in, num_bits
        if word in to_create:
            code = ord(word[0])
            if code < 256:
                write(0, num_bits)
                write(code, 8)
            else:
                write(1, num_bits)
                write(code, 16)
            enlarge_in -= 1
            if enlarge_in == 0:
                enlarge_in, num_bits = 2 ** num_bits, num_bits + 1
            to_create.discard(word)
        else:
            write(dictionary[word], num_bits)
        enlarge_in -= 1
        if enlarge_in == 0:
            enlarge_in, num_bits = 2 ** num_bits, num_bits + 1

    word = ""
    for char in text:
        if char not in dictionary:
            dictionary[char] = dict_size
            dict_size += 1
            to_create.add(char)
        if word + char in dictionary:
            word += char
        else:
            emit(word)
            dictionary[word + char] = dict_size
            dict_size += 1
            word = char
    if word:
        emit(word)
    write(2, num_bits)
    while True:  # flush the last character
        value <<= 1
        if position == 5:
            out.append(_LZ_KEYS[value])
            break
        position += 1
    return "".join(out)


def lz_decode(text: str) -> str | None:
    """lz-string's decompressFromEncodedURIComponent; None for text that isn't such a string."""
    text = text.replace(" ", "+")  # a "+" that came through a URL as a space
    if not text or any(char not in _LZ_INDEX for char in text):
        return None
    index, position, value = 1, 32, _LZ_INDEX[text[0]]

    def read(bits: int) -> int:
        nonlocal index, position, value
        number, power = 0, 1
        for _ in range(bits):
            bit = value & position
            position >>= 1
            if position == 0:
                position = 32
                value = _LZ_INDEX[text[index]] if index < len(text) else 0
                index += 1
            if bit:
                number |= power
            power <<= 1
        return number

    dictionary: dict[int, str] = {0: "", 1: "", 2: ""}
    first = read(2)
    if first == 2:
        return ""
    if first not in (0, 1):
        return None
    word = chr(read(8 if first == 0 else 16))
    dictionary[3] = word
    result = [word]
    enlarge_in, dict_size, num_bits = 4, 4, 3
    while True:
        if index > len(text):
            return None
        code = read(num_bits)
        if code in (0, 1):
            dictionary[dict_size] = chr(read(8 if code == 0 else 16))
            code = dict_size
            dict_size += 1
            enlarge_in -= 1
        elif code == 2:
            return "".join(result)
        if enlarge_in == 0:
            enlarge_in, num_bits = 2 ** num_bits, num_bits + 1
        if code in dictionary and code > 2:
            entry = dictionary[code]
        elif code == dict_size:
            entry = word + word[0]
        else:
            return None
        result.append(entry)
        dictionary[dict_size] = word + entry[0]
        dict_size += 1
        enlarge_in -= 1
        word = entry
        if enlarge_in == 0:
            enlarge_in, num_bits = 2 ** num_bits, num_bits + 1


def encode_state(state: dict[str, Any]) -> str:
    return lz_encode(json.dumps(state, separators=(",", ":"), ensure_ascii=True))


def decode_state(text: str) -> dict[str, Any] | None:
    decoded = lz_decode(text)
    try:
        state = json.loads(decoded) if decoded else None
    except ValueError:
        return None
    return state if isinstance(state, dict) else None


# --- reading the site's answers ---

def _number(text: Any) -> float | None:
    """A price or quantity as the site writes it ("$0.10991", "1,000", "CA$1.20"), or None."""
    if isinstance(text, (int, float)) and not isinstance(text, bool):
        return float(text)
    if not isinstance(text, str):
        return None
    digits = re.sub(r"[^0-9.,]", "", text)
    if "," in digits and "." not in digits and re.search(r",\d{1,2}$", digits):
        digits = digits.replace(",", ".")  # a decimal comma
    digits = digits.replace(",", "")
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


def _quantity(text: Any) -> int:
    """A stock figure, 0 when it isn't one (a made-to-order item has only a label)."""
    number = _number(text)
    return int(number) if number is not None else 0


def _price_breaks(tiers: Any) -> list[dict[str, Any]]:
    breaks = []
    for tier in tiers if isinstance(tiers, list) else []:
        quantity, price = _number(tier.get("brkQty")), _number(tier.get("unitPrice"))
        if quantity is not None and price is not None:
            breaks.append({"qty": int(quantity), "price": price})
    return breaks


def _reel_fee(messages: Iterable[Any]) -> float | None:
    """The Digi-Reel fee from message 43 ("* All Digi-Reel orders will add a $7.00 reeling fee.")."""
    for message in messages:
        if isinstance(message, dict) and str(message.get("code")) == "43":
            if match := re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)", str(message.get("message") or "")):
                return float(match.group(1))
    return None


def _last_buy_date(messages: Iterable[Any]) -> str | None:
    """Message 49 ("Last Time Buy Date: 7/29/2027") as 2027-07-29."""
    for message in messages:
        if isinstance(message, dict) and str(message.get("code")) == "49":
            if match := re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", str(message.get("message") or "")):
                month, day, year = (int(part) for part in match.groups())
                try:
                    return datetime.date(year, month, day).isoformat()
                except ValueError:
                    return None
    return None


def _same_mpn(listed: str, asked: str, maker: str) -> bool:
    """As digikey._same_mpn: equal ignoring case and outer spaces, or JST's (LF)(SN) endings aside."""
    return listed.strip().casefold() == asked.strip().casefold() or same_jst_part(listed, asked, maker)


def _is_exact(asked: str, mpn: str, maker: str, digikey_numbers: Iterable[str]) -> bool:
    """The product is the part asked for: its MPN (_same_mpn, or the same but for separators, which
    the API's exact matches accepted too: MR06X223 JTL for MR06X223JTL, EEU-FS1H221L for
    EEUFS1H221L; mpn_key, so a "+" or "." still counts), or one of its DigiKey numbers."""
    wanted = asked.strip().casefold()
    key = mpn_key(asked.strip())
    return _same_mpn(mpn or "", asked, maker or "") or (bool(key) and mpn_key((mpn or "").strip()) == key) or any(
        (number or "").strip().casefold() == wanted for number in digikey_numbers)


def _digikeys_pick(asked: str, mpn: str) -> bool:
    """For a product DigiKey's own search chose for the number: its MPN is the number with leading
    zeros (Molex's 0039012045 for 39012045). A near match stays out (MA2C700A0F for MA2C700A)."""
    asked_key, listed_key = mpn_key(asked.strip()).lstrip("0"), mpn_key((mpn or "").strip()).lstrip("0")
    return bool(asked_key) and asked_key == listed_key


@dataclass
class _Variation:
    """One packaging of a product (cut tape, reel, Digi-Reel, a Marketplace seller's offer)."""
    part_number: str
    packaging: str
    min_qty: int
    price_breaks: list[dict[str, Any]]
    reel_fee: float | None = None
    marketplace: bool = False


# Without prices (DigiKey no longer sells the part) the smallest order is unknown: cut tape first
_PACKAGING_ORDER = {"cut tape (ct)": 0, "digi-reel®": 2, "tape & reel (tr)": 3}


def _pick_key(variation: _Variation) -> tuple:
    """digikey._pick_variation's order (smallest order, DigiKey's own stock before Marketplace, no
    Digi-Reel fee), priced packagings first."""
    return (not variation.price_breaks, variation.min_qty, variation.marketplace, bool(variation.reel_fee),
            _PACKAGING_ORDER.get(variation.packaging.casefold(), 1))


@dataclass
class _Product:
    """One product page, read."""
    product_id: int
    mpn: str
    maker: str
    status: str | None
    stock: int
    variations: list[_Variation]
    marketplace_only: bool
    fields: dict[str, Any]  # the reply's other fields
    last_buy_date: str | None = None

    @property
    def digikey_numbers(self) -> list[str]:
        return [v.part_number for v in self.variations]


def _attributes(data: dict[str, Any]) -> list[tuple[str, list[str]]]:
    attributes = (data.get("productAttributes") or {}).get("attributes") or []
    return [(str(a.get("label") or ""), [str(v.get("value")) for v in a.get("values") or [] if v.get("value") is not None])
            for a in attributes if isinstance(a, dict)]


def _environment(data: dict[str, Any], name: str) -> str | None:
    for row in (data.get("environmental") or {}).get("dataRows") or []:
        cells = [((cell.get("data") or {}).get("value") or {}).get("value") for cell in row.get("dataCells") or []]
        if len(cells) >= 2 and isinstance(cells[0], str) and cells[0].strip().casefold() == name.casefold():
            return cells[1] if isinstance(cells[1], str) else None
    return None


def _canonical_url(data: dict[str, Any]) -> str | None:
    for meta in data.get("pageMetaCollection") or []:
        pairs = meta.get("metaPairs") or {}
        if meta.get("type") == "link" and pairs.get("rel") == "canonical":
            return pairs.get("href")
    return None


def _variations(price_quantity: dict[str, Any], labels: list[tuple[str, str]], fee: float | None,
                marketplace: bool) -> list[_Variation]:
    """A product's packagings from its price rows. The site shows cut tape and Digi-Reel as one row
    ("Cut Tape (CT) & Digi-Reel®"): the Digi-Reel packaging is rebuilt from it, with cut tape's
    prices and minimum 1 and the reel fee, under the Digi-Reel number from the labels."""
    variations = []
    for row in price_quantity.get("pricing") or []:
        number, packaging = str(row.get("digikeyProductNumber") or ""), str(row.get("packaging") or "")
        breaks = _price_breaks(row.get("mergedPricingTiers"))
        min_qty = int(_number(row.get("minOrderQuantity")) or 1)
        if "digi-reel" in packaging.casefold() and "&" in packaging:
            variations.append(_Variation(number, "Cut Tape (CT)", min_qty, breaks, marketplace=marketplace))
            reel = next((n for n, label in labels if "digi-reel" in label.casefold() and n != number), None)
            if reel:
                variations.append(_Variation(reel, "Digi-Reel®", 1, breaks, reel_fee=fee, marketplace=marketplace))
        elif number:
            variations.append(_Variation(number, packaging, min_qty, breaks, marketplace=marketplace))
    return variations


def parse_detail(body: Any, product_id: int) -> _Product | None:
    """A product page (detail-page), or None for one DigiKey no longer offers (isUnavailable).
    Raises SiteFailed for a shape it doesn't know (that lookup's failure, not a refusal)."""
    data = body.get("data") if isinstance(body, dict) else None
    overview = data.get("productOverview") if isinstance(data, dict) else None
    if not isinstance(overview, dict):
        raise SiteFailed("detail: no productOverview")
    if data.get("isUnavailable"):
        return None
    mpn = overview.get("manufacturerProductNumber")
    if not isinstance(mpn, str):
        raise SiteFailed("detail: no manufacturerProductNumber")
    maker = str(overview.get("manufacturer") or "")
    messages = [m for m in data.get("messages") or [] if isinstance(m, dict)]
    price_quantity = data.get("priceQuantity") or {}
    labels = []
    for entry in (overview.get("digikeyProductNumbers") or {}).get("value") or []:
        if isinstance(entry, dict) and entry.get("value"):
            label = str(entry.get("label") or "")
            labels.append((str(entry["value"]), label.split(" - ", 1)[1] if " - " in label else ""))
    pricing_messages = [m for row in price_quantity.get("pricing") or [] for m in row.get("pricingMessages") or []]
    fee = _reel_fee(messages + pricing_messages)
    marketplace_only = bool(data.get("isMarketplaceOnly"))
    variations = _variations(price_quantity, labels, fee, marketplace_only)
    attributes = _attributes(data)
    packaging_values = next((values for label, values in attributes if label.casefold() == "packaging"), [])
    # DigiKey numbers with no price row (a part DigiKey no longer sells): packagings without prices
    known = {v.part_number for v in variations}
    for number, packaging in labels:
        if number not in known:
            packaging = packaging or (packaging_values[0] if len(packaging_values) == 1 else "")
            variations.append(_Variation(number, packaging, 1, [], marketplace=marketplace_only))
            known.add(number)
    stock = _quantity(price_quantity.get("qtyAvailable"))
    # Other sellers' offers of this product (Rochester's stock of an obsolete part): Marketplace packagings
    for offer in data.get("productAlternatives") or []:
        offer_quantity = (offer or {}).get("priceQuantity") or {}
        for variation in _variations(offer_quantity, [], None, True):
            if variation.part_number not in known:
                variations.append(variation)
                known.add(variation.part_number)
        stock += _quantity(offer_quantity.get("qtyAvailable"))

    status = next((values[0] for label, values in attributes if label.casefold() == "part status" and values), None)
    parameters = {label: ", ".join(values) for label, values in attributes
                  if label and label.casefold() not in _NOT_PARAMETERS and values and ", ".join(values) != "-"}
    categories = (data.get("productAttributes") or {}).get("categories") or []
    rohs = _environment(data, "RoHS Status")
    fields = {
        "description": str(overview.get("description") or ""),
        "category": str((categories[0] or {}).get("label") or "") if categories else "",
        "datasheet_url": overview.get("datasheetUrl") or None,
        "product_url": _canonical_url(data),
        "rohs": "Unknown" if not rohs else "Not Applicable" if rohs.casefold() == "not applicable" else rohs,
        "parameters": parameters,
    }
    return _Product(product_id, mpn, maker, status, stock, variations, marketplace_only, fields,
                    last_buy_date=_last_buy_date(messages))


def _merge(products: list[_Product]) -> list[_Product]:
    """One product per maker and MPN: a reseller's Marketplace listing of a DigiKey product adds its
    packagings (as Marketplace) and stock to that product, whose status stands (the API files them
    so). The DigiKey product is the one not Marketplace-only, else the one with most stock."""
    groups: dict[tuple[str, str], list[_Product]] = {}
    for product in products:
        groups.setdefault((maker_key(product.maker), product.mpn.strip().casefold()), []).append(product)
    merged = []
    for group in groups.values():
        group.sort(key=lambda p: (p.marketplace_only, -p.stock))
        main = group[0]
        for other in group[1:]:
            known = set(main.digikey_numbers)
            for variation in other.variations:
                if variation.part_number not in known:
                    variation.marketplace = True
                    main.variations.append(variation)
            main.stock += other.stock
        merged.append(main)
    return merged


def to_result(product: _Product, asked: str) -> dict[str, Any]:
    """The product in digikey._normalize_product's shape."""
    wanted = asked.strip().upper()
    variations = product.variations
    chosen = next((v for v in variations if wanted and v.part_number.upper() == wanted), None)
    if chosen is None and variations:
        chosen = min(variations, key=_pick_key)
    status, _ = digikey_status(product.status)
    result: dict[str, Any] = {
        "source": "digikey",
        "part_number": chosen.part_number if chosen else "",
        "mfr_part_number": product.mpn,
        "manufacturer": product.maker,
        "description": product.fields["description"],
        "category": product.fields["category"],
        "stock": product.stock,
        "price": chosen.price_breaks[0]["price"] if chosen and chosen.price_breaks else None,
        "price_breaks": list(chosen.price_breaks) if chosen else [],
        "datasheet_url": product.fields["datasheet_url"],
        "product_url": product.fields["product_url"],
        "rohs": product.fields["rohs"],
        "lifecycle": product.status or "Unknown",
        "lifecycle_status": status,
        "parameters": product.fields["parameters"],
        "min_qty": chosen.min_qty if chosen else 1,
        "currency": DIGIKEY_LOCALE_CURRENCY,
    }
    if product.last_buy_date:
        result["last_buy_date"] = product.last_buy_date
    if chosen is None:
        return result
    if chosen.packaging:
        result["packaging"] = chosen.packaging
    if chosen.reel_fee:
        result["reel_fee"] = chosen.reel_fee
    if chosen.marketplace:
        result["marketplace"] = True
    others, seen = [], {chosen.part_number}
    for variation in variations:
        if variation.part_number in seen:
            continue
        seen.add(variation.part_number)
        other: dict[str, Any] = {"part_number": variation.part_number, "packaging": variation.packaging,
                                 "min_qty": variation.min_qty,
                                 "price": variation.price_breaks[0]["price"] if variation.price_breaks else None}
        if variation.reel_fee:
            other["reel_fee"] = variation.reel_fee
        if variation.marketplace:
            other["marketplace"] = True
        others.append(other)
    if others:
        result["other_packaging"] = others
    return result


@dataclass
class _Row:
    """One product of a comparison request."""
    product_id: int
    mpn: str
    maker: str
    supplier: str
    status: str | None
    stock: int
    digikey_numbers: list[str]


def parse_compare(body: Any) -> list[_Row]:
    """A comparison answer (compare-page): one row per product it still offers (it leaves out the
    others). Raises SiteFailed for a shape it doesn't know (that lookup's failure, not a refusal)."""
    data = body.get("data") if isinstance(body, dict) else None
    if not isinstance(data, dict) or not isinstance(data.get("compareIds"), list):
        raise SiteFailed("compare: no compareIds")
    rows = {row.get("name"): row.get("data") for row in (data.get("compareHeaderRows") or []) + (data.get("compareDataRows") or [])
            if isinstance(row, dict) and isinstance(row.get("data"), list)}
    if "Mfr Part #" not in rows or "Mfr" not in rows:
        raise SiteFailed("compare: no Mfr Part # or Mfr row")

    def cell(name: str, index: int) -> Any:
        column = rows.get(name) or []
        return column[index] if index < len(column) else None

    def text(value: Any, key: str = "value") -> str:
        return str(value.get(key) or value.get("value") or "") if isinstance(value, dict) else ""

    parsed = []
    for index, product_id in enumerate(data["compareIds"]):
        stock = cell("Stock", index)
        numbers = cell("DK Part #", index)
        parsed.append(_Row(
            int(product_id), text(cell("Mfr Part #", index), "label"), text(cell("Mfr", index)),
            text(cell("Supplier", index), "label"), text(cell("Product Status", index)) or None,
            _quantity(stock[0].get("value") if isinstance(stock, list) and stock and isinstance(stock[0], dict) else None),
            [text(n) for n in numbers if text(n)] if isinstance(numbers, list) else []))
    return parsed


def _listing_matches(body: dict[str, Any], asked: str) -> list[int] | None:
    """The exact products of a listing answer (filter-page), or None when it isn't a listing."""
    data = body.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("products"), list):
        return None
    ids = []
    for row in data["products"]:
        compare = next((c.get("value") for c in row if isinstance(c, dict) and c.get("type") == "compare"), None) \
            if isinstance(row, list) else None
        if not isinstance(compare, dict):
            raise SiteFailed("listing: a row without its product cell")
        maker = str((compare.get("manufacturer") or {}).get("name") or "")
        if _is_exact(asked, str(compare.get("manufacturerPartNumber") or ""), maker, [str(compare.get("productNumber") or "")]):
            ids.append(int(compare["productId"]))
    return ids


def _new_session() -> Any:
    """One retry for a 5xx or a dropped connection. No identity rotation (max_rotations=0): a 403,
    429 or challenge comes back as the reply, so it pauses after its one request, without wafer
    sending it again under a new identity (which also drops F5's cookie) or sleeping out a long
    Retry-After until the budget is gone."""
    return wafer.AsyncSession(timeout=DIGIKEY_SITE_TIMEOUT, attempt_timeout=DIGIKEY_SITE_ATTEMPT_TIMEOUT,
                              max_retries=1, max_rotations=0, cache_dir=None)


class DigiKeySite:
    """Lookups by part number, paced and paused as the module says. One long-lived wafer session:
    F5's cookie lives in it."""

    def __init__(self, session_factory: Callable[[], Any] | None = None, clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], Any] = asyncio.sleep, concurrency: int = DIGIKEY_SITE_CONCURRENCY,
                 per_second: float = DIGIKEY_SITE_PER_SECOND, slot_wait: float = DIGIKEY_SITE_SLOT_WAIT,
                 pause: float = DIGIKEY_SITE_PAUSE, pause_max: float = DIGIKEY_SITE_PAUSE_MAX):
        self._session_factory = session_factory  # None: _new_session, looked up when first needed
        self._session: Any = None
        self._clock = clock
        self._concurrency = concurrency
        self._slots: asyncio.Semaphore | None = None  # created in the running loop
        self._pacer = Pacer(per_second, clock=clock, sleep=sleep)
        self._slot_wait = slot_wait
        self._pause = Cooldown(pause, pause_max, clock=clock)
        self._failing: set[str] = set()  # the numbers whose lookups failed since the last that worked
        self._test_due = False  # the next lookup tests the site after a pause
        self._testing: asyncio.Event | None = None  # set when the testing lookup is done

    # --- state ---

    def retry_after(self) -> int:
        """Seconds until a lookup may be made (a short wait when only busy)."""
        return max(1, math.ceil(self._pause.remaining)) if self._pause.active else math.ceil(self._slot_wait)

    def status(self) -> dict[str, Any]:
        """For /health: when the pause ends (None when not paused). Why stays in the log."""
        if not self._pause.active:
            return {"paused_until": None}
        until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=self._pause.remaining)
        return {"paused_until": until.strftime("%Y-%m-%d %H:%M UTC")}

    def _refused(self, reason: str) -> None:
        if self._pause.active:  # an answer to a request sent before the pause began
            return
        seconds = self._pause.trip()
        self._failing.clear()
        self._test_due = True
        length = f"{seconds / 3600:g} h" if seconds >= 7200 else f"{seconds / 60:.0f} min"
        logger.error(f"DigiKey lookups paused for {length}: {reason}")

    def _failed(self, reason: str, key: str) -> None:
        """A lookup failed. Lookups of FAILURES_BEFORE_PAUSE different numbers failing in a row (an
        outage, or a change on DigiKey's side) pause as a refusal does; one number asked again and
        again, whatever answers it gets, never does."""
        self._failing.add(key)
        if len(self._failing) >= FAILURES_BEFORE_PAUSE:
            self._refused(f"lookups of {len(self._failing)} numbers failed in a row, the last: {reason}")
        else:
            logger.warning(f"DigiKey lookup failed: {reason}")

    def _succeeded(self, testing: bool) -> None:
        self._failing.clear()
        self._pause.record_success()
        if testing:
            logger.info("DigiKey lookups resumed after a pause")

    async def _admit(self) -> bool:
        """Before a lookup: SiteUnavailable while paused. After a pause the first lookup tests the
        site (True) and the others wait for its answer, up to the slot wait, then look again: a test
        that didn't pass leaves the next one due."""
        while True:
            if self._pause.active:
                raise SiteUnavailable(self.retry_after(), paused=True)
            if self._testing is not None:
                try:
                    await asyncio.wait_for(self._testing.wait(), self._slot_wait)
                except TimeoutError:
                    raise SiteUnavailable(self.retry_after(), paused=False) from None
                continue
            if self._test_due:
                self._test_due = False
                self._testing = asyncio.Event()
                return True
            return False

    async def _all(self, coroutines: Iterable[Any]) -> list[Any]:
        """Run them together; on the first failure cancel the rest (their answers can't be used) and
        raise it. A refusal pauses at once, before the failure reaches _guarded: a sibling request
        waiting its turn then sees the pause and never goes out."""
        async def one(coroutine: Any) -> Any:
            try:
                return await coroutine
            except SiteRefused as e:
                self._refused(str(e))
                raise

        tasks = [asyncio.ensure_future(one(c)) for c in coroutines]
        try:
            return await asyncio.gather(*tasks)
        except BaseException:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise

    async def _guarded(self, work: Callable[[], Any], key: str) -> Any:
        """Run one lookup's requests with the pause rules around them. key: the number (or the
        batch's numbers) for counting failures."""
        testing = await self._admit()
        sends = [0]
        token = _lookup_sends.set(sends)
        passed = False
        try:
            result = await work()
            passed = True
        except SiteRefused as e:
            self._refused(str(e))
            raise SiteUnavailable(self.retry_after(), paused=True, sent=True, refused=True) from None
        except SiteFailed as e:
            self._failed(str(e), key)
            if self._pause.active:  # the failure that made it a run of them: paused, as for a refusal
                raise SiteUnavailable(self.retry_after(), paused=True, sent=True) from None
            raise
        except SiteUnavailable as e:  # paused by another lookup meanwhile, or no slot in time
            raise SiteUnavailable(e.retry_after, e.paused, sent=sends[0] > 0) from None
        except _UNREADABLE as e:
            # An answer this code can't read: that number's oddity, or DigiKey changed (then every
            # lookup fails, and the run of failures pauses)
            logger.exception("DigiKey answer not understood")
            self._failed(f"answer not understood ({type(e).__name__})", key)
            if self._pause.active:
                raise SiteUnavailable(self.retry_after(), paused=True, sent=True) from None
            raise SiteFailed(f"answer not understood ({type(e).__name__})") from None
        finally:
            _lookup_sends.reset(token)
            if testing:
                if not passed:
                    self._test_due = True  # still untested (or paused again): the next lookup tests
                if self._testing is not None:
                    self._testing.set()
                    self._testing = None
        self._succeeded(testing)
        return result

    # --- requests ---

    def _headers(self) -> dict[str, str]:
        return {"lang": DIGIKEY_LOCALE_LANGUAGE.lower(), "site": DIGIKEY_LOCALE_SITE.upper(),
                "x-currency": DIGIKEY_LOCALE_CURRENCY.upper(), "authorization": "Bearer",
                "accept": "application/json, text/plain, */*"}

    async def _send(self, path: str) -> Any:
        """One GET within the slots and the pacer; wafer's own failures sorted into ours. Nothing
        goes out once a pause has begun, however long the request had been waiting its turn."""
        if self._slots is None:
            self._slots = asyncio.Semaphore(self._concurrency)
        waited = self._slots.locked()
        if waited:
            try:
                await asyncio.wait_for(self._slots.acquire(), self._slot_wait)
            except TimeoutError:
                raise SiteUnavailable(self.retry_after(), paused=False) from None
        else:
            await self._slots.acquire()
        try:
            await self._pacer.wait()
            if self._pause.active:
                raise SiteUnavailable(self.retry_after(), paused=True)
            if self._session is None:
                self._session = (self._session_factory or _new_session)()
            if waited:
                _count_upstream("digikey", "waited")
            if (sends := _lookup_sends.get()) is not None:
                sends[0] += 1
            self._pacer.mark()
            return await _sent("digikey", self._session.get(BASE_URL + path, headers=self._headers()))
        except (wafer.ChallengeDetected, wafer.RateLimited) as e:
            raise SiteRefused(f"{type(e).__name__} ({getattr(e, 'challenge_type', None) or 'no type'})") from None
        except wafer.WaferError as e:
            raise SiteFailed(type(e).__name__) from None
        finally:
            self._slots.release()

    async def _get(self, kind: str, path: str) -> Any:
        """The JSON answer to one GET, or None for 204 (no such product)."""
        response = await self._send(path)
        if response.status_code == 400 and (response.content or b"").strip() == _F5_REFUSAL:
            response = await self._send(path)  # the refusal set F5's cookie: once more with it
            if response.status_code == 400 and (response.content or b"").strip() == _F5_REFUSAL:
                raise SiteRefused(f"{kind}: refused twice (HTTP 400)")
        status = response.status_code
        if getattr(response, "challenge_type", None):
            raise SiteRefused(f"{kind}: challenge {response.challenge_type} (HTTP {status})")
        if status in (403, 429):
            raise SiteRefused(f"{kind}: HTTP {status}")
        if status >= 500:
            raise SiteFailed(f"{kind}: HTTP {status}")
        if status == 204:
            return None
        if status != 200:  # a 404 or a plain 400: this request's own, not a refusal of the server
            raise SiteFailed(f"{kind}: HTTP {status}")
        content_type = str((response.headers or {}).get("content-type") or "")
        if "json" not in content_type:
            raise SiteRefused(f"{kind}: not JSON ({content_type[:40] or 'no content type'})")
        try:
            return response.json()
        except ValueError:
            raise SiteFailed(f"{kind}: unreadable JSON") from None

    # --- lookups ---

    async def _suggested(self, number: str) -> tuple[list[int], int]:
        """The exact products in the product list for the number, and how many it listed."""
        body = await self._get("suggestions", f"/suggestions?keywordSearch={quote(number, safe='')}&limit={SUGGESTIONS}")
        items = ((body or {}).get("data") or {}).get("suggestedProductNumbers") if isinstance(body, dict) else None
        if not isinstance(items, list):
            raise SiteFailed("suggestions: no suggestedProductNumbers")
        ids = []
        for item in items:
            slug = _DETAIL_URL.search(str(item.get("navigationUrl") or ""))
            maker = slug.group(1).replace("-", " ") if slug else ""
            if _is_exact(number, str(item.get("manufacturerProductNumber") or ""), maker,
                         [str(item.get("digiKeyProductNumber") or "")]):
                ids.append(int(item["productId"]))
        return ids, len(items)

    async def _searched(self, number: str) -> tuple[list[int], set[int]]:
        """The products the keyword search gives for the number (its product page, a listing's
        exact rows, or its exact matches), and those DigiKey chose itself (the page, the exact
        matches); ([], set()) for none. A product page may be a near match (MA2C700A is answered
        with MA2C700A0F): the caller checks it."""
        body = await self._get("search", f"/result-page?s={encode_state({'2': [number]})}")
        seen: set[str] = set()
        for hop in range(MAX_HOPS + 1):
            if not isinstance(body, dict):
                raise SiteFailed("search: not an object")
            redirect = body.get("redirect")
            if isinstance(redirect, dict):
                url = str(redirect.get("url") or "")
                if match := _DETAIL_URL.search(url):
                    return [int(match.group(2))], {int(match.group(2))}
                match = _LISTING_URL.search(url)
                state = decode_state(match.group(2)) if match else None
                if state is None:
                    raise SiteFailed("search: a redirect it doesn't know")
                if url in seen or hop == MAX_HOPS:  # a category that redirects to itself, or a long chain
                    return [], set()
                seen.add(url)
                state["5"] = {"p": 1, "pp": 100}
                state["6"] = {"id": "-100", "pt": "", "type": "asc"}  # by MPN: exact ones first, stable pages
                body = await self._get("listing", f"/filter-page/{match.group(1)}?s={encode_state(state)}")
                continue
            if (ids := _listing_matches(body, number)) is not None:
                return ids, set()
            data = body.get("data")
            if not isinstance(data, dict):
                raise SiteFailed("search: no data")
            if isinstance(data.get("exactMatch"), list) and data["exactMatch"]:
                ids = [int(entry["id"]) for entry in data["exactMatch"]]
                return ids, set(ids)
            if "productCount" in data:
                return [], set()
            raise SiteFailed("search: an answer it doesn't know")
        return [], set()

    async def _candidates(self, number: str) -> tuple[list[int], set[int]]:
        """The ids of the products that may be the part asked, in order (exact ones found so far),
        and those DigiKey's search chose itself (_digikeys_pick applies to them)."""
        ids, _ = await self._suggested(number)
        picked: set[int] = set()
        if not ids or len(ids) >= SEARCH_WHEN_EXACT:
            found, picked = await self._searched(number)
            ids += found
        return list(dict.fromkeys(ids)), picked

    async def _compare(self, ids: list[int]) -> list[_Row]:
        chunks = [ids[i:i + COMPARE_CHUNK] for i in range(0, len(ids), COMPARE_CHUNK)]
        answers = await self._all(self._get("compare", "/compare-page?s=" + encode_state(
            {"9": [{"id": i, "productId": i} for i in chunk]})) for chunk in chunks)
        return [row for body in answers for row in parse_compare(body)]

    async def _details(self, ids: list[int]) -> list[_Product]:
        bodies = await self._all(self._get("detail", f"/detail-page/{i}") for i in ids)
        return [product for i, body in zip(ids, bodies) if body is not None
                and (product := parse_detail(body, i)) is not None]

    async def lookup(self, number: str) -> SiteAnswer:
        """The part's answer (SiteAnswer; no results: DigiKey doesn't list it). Raises
        SiteUnavailable (paused, busy) or SiteFailed (this lookup only)."""
        return await self._guarded(lambda: self._lookup(number.strip()), number.strip().casefold())

    async def _lookup(self, number: str) -> SiteAnswer:
        ids, picked = await self._candidates(number)

        def is_part(product_id: int, mpn: str, maker: str, numbers: list[str]) -> bool:
            return _is_exact(number, mpn, maker, numbers) or (product_id in picked and _digikeys_pick(number, mpn))

        statuses: dict[tuple[str, str], tuple[str, str, str | None, str | None]] = {}
        if len(ids) > DIGIKEY_MAX_RESULTS:
            # Every maker's status and stock in one request; pages for the makers with most stock,
            # every listing of each (a reseller's beside the maker's own, merged as for fewer)
            rows = [r for r in await self._compare(ids) if is_part(r.product_id, r.mpn, r.maker, r.digikey_numbers)]
            groups: dict[tuple[str, str], list[_Row]] = {}
            for row in _dealer_last(rows):
                groups.setdefault((maker_key(row.maker), mpn_key(row.mpn)), []).append(row)
            for key, group in groups.items():
                row = group[-1]  # the maker's own listing where there is one
                statuses[key] = (row.mpn, row.maker, row.status, None)
            top = sorted(groups.values(), key=lambda g: -sum(r.stock for r in g))[:DIGIKEY_MAX_RESULTS]
            ids = [row.product_id for group in top for row in group]
        products = [p for p in await self._details(ids) if is_part(p.product_id, p.mpn, p.maker, p.digikey_numbers)]
        products = sorted(_merge(products), key=lambda p: -p.stock)[:DIGIKEY_MAX_RESULTS]
        for product in products:
            statuses[(maker_key(product.maker), mpn_key(product.mpn))] = (
                product.mpn, product.maker, product.status, product.last_buy_date)
        return SiteAnswer([to_result(p, number) for p in products], list(statuses.values()),
                          [p.product_id for p in products])

    async def statuses(self, numbers: list[str]) -> dict[str, list[tuple[str, str, str | None, str | None]] | Exception]:
        """Lifecycle only, for many numbers at once: each number's product list, one comparison
        request for every product (status and maker), and a product page only for Last Time Buy
        parts (the date). Per number: its statuses ([] when DigiKey doesn't list it), or the
        SiteFailed / busy SiteUnavailable that number met, so one number's trouble doesn't lose
        the others (a Last Time Buy page that fails only loses its date). A refusal or a pause
        stops the batch, and a batch where every number failed raises, both as lookup() does."""
        numbers = [n.strip() for n in numbers]
        return await self._guarded(lambda: self._statuses(numbers), "|".join(sorted(n.casefold() for n in numbers)))

    async def _isolated(self, coroutine: Any) -> Any:
        """The coroutine's result, or the trouble that is one number's alone within a batch (a
        SiteFailed, no request slot in time, an answer this code can't read) as the result. A
        refusal or a pause still stops the whole batch."""
        try:
            return await coroutine
        except SiteFailed as e:
            return e
        except SiteUnavailable as e:
            if e.paused:
                raise
            return e
        except _UNREADABLE as e:
            logger.exception("DigiKey answer not understood")
            return SiteFailed(f"answer not understood ({type(e).__name__})")

    async def _statuses(self, numbers: list[str]) -> dict[str, Any]:
        candidates = await self._all(self._isolated(self._candidates(number)) for number in numbers)
        every_id = list(dict.fromkeys(i for found in candidates if not isinstance(found, Exception) for i in found[0]))
        chunks = [every_id[i:i + COMPARE_CHUNK] for i in range(0, len(every_id), COMPARE_CHUNK)]
        bodies = await self._all(self._isolated(self._get("compare", "/compare-page?s=" + encode_state(
            {"9": [{"id": i, "productId": i} for i in chunk]}))) for chunk in chunks)
        rows: dict[int, _Row] = {}
        lost: dict[int, Exception] = {}  # ids whose comparison failed, and how
        for chunk, body in zip(chunks, bodies):
            if not isinstance(body, Exception):
                try:
                    rows.update((row.product_id, row) for row in parse_compare(body))
                    continue
                except (SiteFailed, *_UNREADABLE) as e:
                    body = e if isinstance(e, SiteFailed) else SiteFailed(f"compare: {type(e).__name__}")
            lost.update(dict.fromkeys(chunk, body))
        results: dict[str, Any] = {}
        for number, found in zip(numbers, candidates):
            if isinstance(found, Exception):
                results[number] = found
                continue
            ids, picked = found
            if failed := next((lost[i] for i in ids if i in lost), None):
                results[number] = failed  # some of its makers unknown: no partial answer
            else:
                kept: dict[tuple[str, str], _Row] = {}
                for row in _dealer_last([rows[i] for i in ids if i in rows and (_is_exact(
                        number, rows[i].mpn, rows[i].maker, rows[i].digikey_numbers)
                        or (i in picked and _digikeys_pick(number, rows[i].mpn)))]):
                    kept[(maker_key(row.maker), mpn_key(row.mpn))] = row
                results[number] = list(kept.values())
        last_time_buy = list(dict.fromkeys(row.product_id for found in results.values() if isinstance(found, list)
                                           for row in found if digikey_status(row.status)[0] == "last_time_buy"))
        pages = await self._all(self._isolated(self._get("detail", f"/detail-page/{i}")) for i in last_time_buy)
        dates: dict[int, str | None] = {}
        for product_id, body in zip(last_time_buy, pages):
            if body is not None and not isinstance(body, Exception):
                try:
                    if (product := parse_detail(body, product_id)) is not None:
                        dates[product_id] = product.last_buy_date
                except (SiteFailed, *_UNREADABLE):
                    pass  # only the date is lost
        answer = {number: [(r.mpn, r.maker, r.status, dates.get(r.product_id)) for r in found]
                  if isinstance(found, list) else found for number, found in results.items()}
        failures = [value for value in answer.values() if isinstance(value, SiteFailed)]
        if failures and len(failures) == len(answer):  # nothing worked: the batch failed, counted once
            raise failures[0]
        return answer

    async def close(self) -> None:
        self._session = None


def _dealer_last(rows: list[_Row]) -> list[_Row]:
    """Rows in the order to keep them by maker and MPN, the later winning: a reseller's listing
    (supplier isn't the maker) before the maker's own, so the maker's status stands."""
    return sorted(rows, key=lambda r: bool(r.supplier) and makers_match(r.supplier, r.maker))
