"""ComponentSearchEngine (SamacSys) client using the alligator JSON API.

Uses rs.componentsearchengine.com/alligatorHandler.php — no auth required.
Returns ECAD model availability, datasheets, pin counts, and part metadata.

Authenticated endpoint for KiCad model downloads:
rs.componentsearchengine.com/ga/model.php — requires CSEARCH_USER/CSEARCH_PASS.
"""

import asyncio
import html
import io
import logging
import re
import time
import zipfile
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

import httpx

from . import stats
from .cache import RetryGuard, TTLCache, retry_after_seconds
from .client import _sent
from .cse_archive import MAX_ZIP_SIZE as _MAX_ZIP_SIZE, extract_kicad
from .cse_store import CSEStore, query_key
from .lifecycle import makers_match
from .search.mpn import mpn_key
from .config import (
    CSE_CONCURRENT_LIMIT,
    CSE_RATE_LIMIT,
    CSE_STATUS_RETRY_DELAY,
    CSE_QUOTA_RETRY_SECONDS,
    CSE_REQUEST_TIMEOUT,
    CSE_CACHE_TTL,
    CSE_KICAD_CACHE_TTL,
    CSE_KICAD_CACHE_MAX_SIZE,
    CSE_USER,
    CSE_PASS,
)

logger = logging.getLogger(__name__)

# RS subdomain works without auth (other subdomains block with "Irregular activity type 2")
_CSE_API_URL = "https://rs.componentsearchengine.com/alligatorHandler.php"
# Authenticated model download endpoint (HTTP Basic Auth)
_CSE_MODEL_URL = "https://rs.componentsearchengine.com/ga/model.php"

# Max results per page from the API
_PAGE_SIZE = 10

# A 5xx reply's Retry-After asking for longer than this means no retry (as DigiKey's)
_RETRY_AFTER_MAX = 3.0


def _transient_error(exc: httpx.HTTPError) -> bool:
    """A dropped or refused connection may pass; a timeout isn't sent again (as Mouser's and
    DigiKey's aren't): a slow SamacSys would cost a second wait as long as the first."""
    return isinstance(exc, httpx.TransportError) and not isinstance(exc, httpx.TimeoutException)


def _json_object(response: httpx.Response) -> dict[str, Any] | None:
    """The reply's JSON object; None when the body isn't one (empty, not JSON, or another JSON value)."""
    try:
        data = response.json()
    except (ValueError, RecursionError):  # JSONDecodeError, undecodable bytes, absurd nesting
        return None
    return data if isinstance(data, dict) else None


def _search_cache_key(query: str, offset: int) -> str:
    return f"cse:{query_key(query)}:{offset}"


def _body_text(content: bytes) -> str:
    return " ".join(re.sub(r"<[^>]*>", " ", html.unescape(content.decode("utf-8", errors="replace"))).split())


def _clean_body(content: bytes) -> str:
    """One safe log/reply line, with neither the Basic-auth login nor email addresses."""
    text = re.sub(r"[\w.!#$%&'*+/=?^`{|}~-]+@[\w.-]+\.[A-Za-z]{2,}", "***", _body_text(content))
    for secret in sorted((CSE_USER, CSE_PASS), key=len, reverse=True):
        if secret:
            for form in (secret, _body_text(secret.encode("utf-8"))):
                if form:
                    text = re.sub(re.escape(form), "***", text, flags=re.I)
    return text


def _utc_iso(at: float) -> str:
    return datetime.fromtimestamp(at, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _warn_nonzip(response: httpx.Response, part_id: int | str, elapsed: float) -> str:
    cleaned = _clean_body(response.content)
    logger.warning("CSE model download for part %s: HTTP %s; content type %s; %s bytes; %.3f seconds; %s",
                   part_id, response.status_code, response.headers.get("content-type", ""),
                   len(response.content), elapsed, cleaned[:200])
    return cleaned


def _normalize_part(part: dict) -> dict:
    """Normalize an alligator API part into our standard format."""
    # Has3D: "Y" = yes, "E" = external/exists, "N" or "" = no
    has_3d_val = part.get("Has3D", "")
    has_3d = has_3d_val in ("Y", "E")

    # ECAD model URL present means symbol/footprint available
    ecad_url = part.get("ECAD_M", "")
    has_model = bool(ecad_url)

    # Quality: 0-4 integer, 0 means no model
    quality = 0
    try:
        quality = int(part.get("Quality", 0))
    except (ValueError, TypeError):
        pass

    # Datasheet URL
    datasheet = part.get("Datasheet") or None

    # Image: prefer large, fall back to small
    image_url = part.get("ImageL") or part.get("ImageS") or None
    if image_url and not image_url.startswith("http"):
        image_url = f"https:{image_url}" if image_url.startswith("//") else None

    return {
        "source": "cse",
        "mfr_part_number": part.get("PartNo", ""),
        "manufacturer": part.get("Manuf", ""),
        "description": part.get("Desc", ""),
        "datasheet_url": datasheet,
        "has_model": has_model,
        "has_3d": has_3d,
        "model_quality": quality,
        "cse_part_id": part.get("PartID"),
        "pin_count": part.get("PinCount", 0),
        "image_url": image_url,
    }


_MPN_SEPARATORS = frozenset("- _/")
_PACKING_SUFFIX_MAX = 5  # key characters a query may add to a listed number: TR, -13, /OT, #PBF, -REEL7


def _clean_break(number: str, length: int) -> bool:
    """Whether a part number cut after `length` key characters (mpn_key's) breaks cleanly: at a
    separator, or anywhere but between two digits (ABS10 isn't ABS1 with a suffix)."""
    kept = [(i, ch) for i, ch in enumerate(number) if ch not in _MPN_SEPARATORS]
    if not 0 < length < len(kept):
        return True
    (before, last), (after, following) = kept[length - 1], kept[length]
    return after - before > 1 or not (last.isdigit() and following.isdigit())


def _match_tier(query: str, part: dict[str, Any]) -> int:
    """Exact number, an extension (ABS10 → ABS10_HF), then the query with a packing suffix
    (LM358PWR → LM358PW); 3 means unrelated, such as a row that names the query only in its
    description."""
    query_key = mpn_key(query.strip())
    number = (part.get("mfr_part_number") or "").strip()
    key = mpn_key(number)
    if query_key and key:
        if key == query_key:
            return 0
        if key.startswith(query_key) and _clean_break(number, len(query_key)):
            return 1
        if (query_key.startswith(key) and len(query_key) - len(key) <= _PACKING_SUFFIX_MAX
                and _clean_break(query.strip(), len(key))):
            return 2
    return 3


def _candidate(part: dict[str, Any]) -> dict[str, Any]:
    return {key: part.get(key) for key in ("mfr_part_number", "manufacturer", "description", "cse_part_id")}


class CSEClient:
    """Async client for ComponentSearchEngine (SamacSys) search.

    Uses the alligator JSON API on the RS subdomain.
    No API key or authentication required.
    """

    def __init__(self, store_path: str | None = None, *, clock: Callable[[], float] | None = None,
                 sleep: Callable[[float], Awaitable[Any]] | None = None):
        """sleep: the wait before a request goes out again (CSE_STATUS_RETRY_DELAY, or a 5xx's
        Retry-After up to 3 s); tests pass a fake."""
        self._clock = clock or time.time
        self._sleep = sleep or asyncio.sleep
        # No retries during an outage, as Mouser and DigiKey: every sent request's outcome counts
        self._guard = RetryGuard("CSE", self._clock, logger)
        self._quota_until = 0.0
        self._refused_since: float | None = None
        self._quota_probe: asyncio.Lock | None = None
        self._cache = TTLCache(ttl=CSE_CACHE_TTL)
        self._kicad_cache = TTLCache(ttl=CSE_KICAD_CACHE_TTL, max_size=CSE_KICAD_CACHE_MAX_SIZE)
        # Answers that outlive this process (cse_store.py), behind the memory caches. Only the server
        # passes a path, so tests and scripts never write to a real store.
        self._store = CSEStore(store_path) if store_path else None
        if self._store is not None:
            self._store.prune()
        self._semaphore: asyncio.Semaphore | None = None
        self._http: httpx.AsyncClient | None = None

    def _get_semaphore(self) -> asyncio.Semaphore:
        # Safe in single-threaded asyncio: no await between None check and assignment
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(CSE_CONCURRENT_LIMIT)
        return self._semaphore

    def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=CSE_REQUEST_TIMEOUT)
        return self._http

    async def _cached_search(self, query: str, offset: int = 0) -> dict[str, Any] | None:
        cache_key = _search_cache_key(query, offset)
        cached = self._cache.get(cache_key)
        if cached is None and self._store:
            cached = await asyncio.to_thread(self._store.get_search, query, offset)
            if cached is not None:
                self._cache.set(cache_key, cached)
        if cached is not None:
            stats.count_upstream("cse", "cached")
        return cached

    async def search(self, query: str, offset: int = 0) -> dict[str, Any]:
        """Search CSE by MPN or keyword.

        Args:
            query: Part number or keyword to search for
            offset: Result offset for pagination (increments of 10)

        Returns:
            Dict with results list and total count
        """
        cached = await self._cached_search(query, offset)
        if cached is not None:
            return cached

        params = {
            "searchString": query,
            "country": "US",
        }
        if offset > 0:
            params["offset"] = str(offset)

        # A first request for a query can come back with another status (F0R0, R0F0), holding real
        # parts or unrelated ones ("blorptastic9": 10 random parts); asking again gave "Success" in
        # all 8 checks, 2026-11-09. Reporting that first answer as empty made parts look missing.
        # A 5xx, a dropped connection or an unreadable reply is also asked once more, unless the
        # retry guard is on (_retry_wait). Either way a search sends at most two requests.
        statuses = 0  # answers with a status other than Success
        retrying = False  # this send repeats a transient failure: upstream.cse.retries
        for attempt in range(2):
            last = attempt == 1
            try:
                async with self._get_semaphore():
                    if retrying:
                        stats.count_upstream("cse", "retries")
                        retrying = False
                    response = await _sent("cse", self._get_http().get(_CSE_API_URL, params=params))
                    await asyncio.sleep(CSE_RATE_LIMIT)
            except httpx.HTTPError as exc:
                transient = _transient_error(exc)
                self._guard.record(transient=transient)
                failure = "CSE API request failed (network/connection error)"
                if transient and not last and await self._retry_wait(f"search: {type(exc).__name__}", None):
                    retrying = True
                    continue
                raise ValueError(failure) from None

            if response.status_code >= 400:
                transient = response.status_code >= 500
                self._guard.record(transient=transient)
                failure = f"CSE API returned HTTP {response.status_code}"
                if transient and not last and await self._retry_wait(f"search: HTTP {response.status_code}", response):
                    retrying = True
                    continue
                raise ValueError(failure)
            data = _json_object(response)
            if data is None:  # not JSON, or not an object: a redirect page, a cut-off body
                self._guard.record(transient=True)
                failure = f"CSE API returned an unreadable reply (HTTP {response.status_code})"
                if not last and await self._retry_wait(f"search: unreadable reply, HTTP {response.status_code}", None):
                    retrying = True
                    continue
                raise ValueError(failure)
            self._guard.record(transient=False)
            if data.get("status") == "Success":
                break
            logger.warning(f"CSE API returned non-success status: {data.get('status')}")
            statuses += 1
            if not last:  # SamacSys answered: asked again whatever the retry guard says, as before
                await self._sleep(CSE_STATUS_RETRY_DELAY)
        else:
            raise ValueError("CSE API gave no usable answer (status other than Success, twice)" if statuses == 2
                             else "CSE API gave no usable answer (status other than Success)")

        raw_parts = data.get("parts", [])

        # Deduplicate by MPN+manufacturer
        parts = []
        seen: set[tuple[str, str]] = set()
        for raw in raw_parts:
            normalized = _normalize_part(raw)
            key = (normalized["mfr_part_number"], normalized["manufacturer"])
            if key not in seen:
                seen.add(key)
                parts.append(normalized)

        # partCount is unreliable (often 0), so use len(parts) as fallback
        total = data.get("partCount", 0)
        if not total:
            total = len(parts)

        result = {
            "results": parts,
            "total": total,
        }

        self._cache.set(_search_cache_key(query, offset), result)
        if self._store:
            await asyncio.to_thread(self._store.put_search, query, offset, result)
        return result

    async def get_kicad(self, query: str | None = None, part_id: int | None = None,
                        manufacturer: str | None = None) -> dict[str, Any]:
        """Download and extract KiCad symbol + footprint for a part.

        Args:
            query: MPN to search for (used to find part_id if not provided)
            part_id: CSE part ID (from a previous cse_search result)
            manufacturer: Maker to match when resolving query

        Returns:
            Dict with kicad_symbol, kicad_footprint text content, plus part metadata
        """
        if not CSE_USER or not CSE_PASS:
            return {"error": "CSE credentials not configured. Set CSEARCH_USER and CSEARCH_PASS in environment."}

        # Resolve part_id from query if needed
        resolved_part_id = part_id
        part_info: dict[str, Any] = {}

        if not resolved_part_id:
            if not query:
                return {"error": "Must provide either query or part_id"}

            search_result = await self.search(query)
            results = search_result.get("results", [])
            manufacturer = (manufacturer or "").strip() or None
            if not results:
                return {"error": f"No parts found for '{query}'"}
            models = [r for r in results if r.get("has_model") and r.get("cse_part_id")]
            if not models:
                return {"error": f"No ECAD model available for '{query}'"}
            # sorted is stable: SamacSys's order decides between matches in the same tier.
            related = sorted((r for r in models if _match_tier(query, r) < 3),
                             key=lambda r: _match_tier(query, r))
            matches = [r for r in related if not manufacturer or makers_match(r.get("manufacturer"), manufacturer)]
            if not matches:
                maker = f" by '{manufacturer}'" if manufacturer else ""
                return {"error": f"No ECAD model available for '{query}'{maker} matching that part number. "
                                 "Pass a candidate's cse_part_id as part_id to choose it explicitly.",
                        "candidates": [_candidate(r) for r in (related or models)[:5]]}

            part_info = dict(matches[0])  # search rows are cached; never attach query-specific fields to them
            resolved_part_id = part_info["cse_part_id"]
            if not manufacturer:
                others = [_candidate(r) for r in related[1:]
                          if r.get("manufacturer") and part_info.get("manufacturer")
                          and not makers_match(r["manufacturer"], part_info["manufacturer"])][:5]
                if others:
                    part_info["other_matches"] = others
                    part_info["note"] = ("This part number is listed by several makers; pass another candidate's "
                                         "cse_part_id as part_id, or give manufacturer, to choose another one.")

        # Check kicad cache
        cache_key = f"kicad:{resolved_part_id}"
        cached = self._kicad_cache.get(cache_key)
        if cached is None and self._store:
            cached = await asyncio.to_thread(self._store.get_kicad, resolved_part_id)
            if cached is not None:
                self._kicad_cache.set(cache_key, cached)
        if cached is not None:
            stats.count_upstream("cse", "cached")
            return {
                "part_id": resolved_part_id,
                **part_info,
                "kicad_symbol": cached.get("kicad_symbol"),
                "kicad_footprint": cached.get("kicad_footprint"),
            }

        # Only one probe goes out after a quota pause; other callers still get stored files above.
        if self._refused_since is not None:
            if self._downloads_paused():
                return await self._quota_error(resolved_part_id, part_info)
            if self._quota_probe is None:
                self._quota_probe = asyncio.Lock()
            async with self._quota_probe:
                return await self._download_kicad(resolved_part_id, part_info)
        return await self._download_kicad(resolved_part_id, part_info)

    def _downloads_paused(self) -> bool:
        return (self._clock() < self._quota_until
                or self._quota_probe is not None and self._quota_probe.locked())

    async def _wanted(self, part_id: int | str, reason: str, part_info: dict[str, Any]) -> dict[str, Any]:
        """Keep backfill requests only for parts identified by a CSE search, never arbitrary IDs."""
        if self._store:
            if not part_info:
                part_info = await asyncio.to_thread(self._store.part_info, part_id)
            if part_info:
                await asyncio.to_thread(self._store.mark_wanted, part_id, reason, part_info, now=self._clock())
        return part_info

    async def _quota_error(self, part_id: int | str, part_info: dict[str, Any]) -> dict[str, Any]:
        stats.count_upstream("cse", "rate_limited")
        part_info = await self._wanted(part_id, "quota", part_info)
        retry = (f"Try again at {_utc_iso(self._quota_until)} (UTC), when this server next checks the quota."
                 if self._clock() < self._quota_until else
                 "This server is checking whether downloads are available again; try again shortly.")
        return {"part_id": part_id, **part_info,
                "error": "SamacSys's daily model download limit for this shared server is used up; "
                         f"the KiCad model couldn't be downloaded. {retry} "
                         "KiCad files pcbparts already has stored still work."}

    def _retry_delay(self, response: httpx.Response | None) -> float | None:
        """Seconds to wait before a failed request goes out again; None for no retry: the retry
        guard is on (an outage), or a 5xx's Retry-After asks for longer than _RETRY_AFTER_MAX."""
        if self._guard.disabled():
            return None
        if response is not None and response.status_code >= 500:
            after = retry_after_seconds(response.headers, self._clock())
            if after is not None:  # unusable: the usual delay
                return after if after <= _RETRY_AFTER_MAX else None
        return CSE_STATUS_RETRY_DELAY

    async def _retry_wait(self, what: str, response: httpx.Response | None) -> bool:
        """Whether a request that failed transiently goes out once more, after waiting (_retry_delay);
        False without waiting when there's no retry, or after it when an outage began meanwhile."""
        delay = self._retry_delay(response)
        if delay is None:
            return False
        logger.warning("CSE request failed (%s); sending it again in %g s", what, delay)
        await self._sleep(delay)
        return not self._guard.disabled()

    async def _download_kicad(self, resolved_part_id: int | str, part_info: dict[str, Any]) -> dict[str, Any]:
        # A 5xx (not one about the quota), a dropped connection or a reply that is neither a ZIP nor
        # SamacSys's own "Error: ..." text is sent once more (_retry_wait): at most two requests.
        retrying = False  # this send repeats a transient failure: upstream.cse.retries
        for attempt in range(2):
            last = attempt == 1
            # Check again inside the semaphore: a download ahead of this one may have refused quota.
            try:
                async with self._get_semaphore():
                    if self._clock() < self._quota_until:
                        return await self._quota_error(resolved_part_id, part_info)
                    if retrying:
                        stats.count_upstream("cse", "retries")
                        retrying = False
                    started = self._clock()
                    response = await _sent("cse", self._get_http().get(
                        _CSE_MODEL_URL,
                        params={"partID": str(resolved_part_id)},
                        auth=(CSE_USER, CSE_PASS),
                        timeout=30,
                    ))
                    elapsed = self._clock() - started
                    await asyncio.sleep(CSE_RATE_LIMIT)
            except httpx.HTTPError as exc:
                transient = _transient_error(exc)
                self._guard.record(transient=transient)
                if transient and not last and await self._retry_wait(f"model download: {type(exc).__name__}", None):
                    retrying = True
                    continue
                return {"error": "CSE model download failed (network/connection error)"}

            # Log non-ZIP HTTP errors too, while retaining their existing authentication/HTTP replies.
            nonzip_logged = False
            if isinstance(response.content, bytes) and not zipfile.is_zipfile(io.BytesIO(response.content)):
                _warn_nonzip(response, resolved_part_id, elapsed)
                nonzip_logged = True
            if response.status_code == 401:
                self._guard.record(transient=False)
                return {"error": "CSE authentication failed. Check CSEARCH_USER and CSEARCH_PASS."}
            if response.status_code != 200:
                # A quota refusal is never sent again, whatever its status
                transient = (response.status_code >= 500 and not (
                    isinstance(response.content, bytes) and "quota" in _body_text(response.content).lower()))
                self._guard.record(transient=transient)
                if transient and not last and await self._retry_wait(
                        f"model download: HTTP {response.status_code}", response):
                    retrying = True
                    continue
                return {"error": f"CSE model download failed (HTTP {response.status_code})"}

            # Check response size to prevent zip bombs
            content_length = len(response.content)
            if content_length > _MAX_ZIP_SIZE:
                self._guard.record(transient=False)
                return {"error": f"CSE model download too large ({content_length} bytes, max {_MAX_ZIP_SIZE})"}

            try:
                kicad_files = extract_kicad(response.content)
            except zipfile.BadZipFile:
                text = _body_text(response.content)
                cleaned = (_clean_body(response.content) if nonzip_logged else
                           _warn_nonzip(response, resolved_part_id, elapsed))
                if "quota" in text.lower():
                    self._guard.record(transient=False)
                    now = self._clock()
                    self._quota_until = now + CSE_QUOTA_RETRY_SECONDS
                    if self._refused_since is None:
                        self._refused_since = now
                    recent = await asyncio.to_thread(self._store.kicad_last_24h, now) if self._store else 0
                    logger.warning("CSE daily download quota refused at %s: %s downloads stored in the last 24 h; next try at %s",
                                   _utc_iso(now), recent, _utc_iso(self._quota_until))
                    return await self._quota_error(resolved_part_id, part_info)
                if text.lower().startswith("error:"):
                    self._guard.record(transient=False)
                    if re.search(r"no\s+part\s+data\s+(?:is\s+)?available", text, re.I):
                        return {"error": f"No ECAD model available for part {resolved_part_id}"}
                    await self._wanted(resolved_part_id, "refused", part_info)
                    return {"error": f"CSE refused the model download for part {resolved_part_id}: {cleaned[:150]}"}
                self._guard.record(transient=True)  # an HTML page or a cut-off archive
                if not last and await self._retry_wait("model download: not a ZIP file", None):
                    retrying = True
                    continue
                await self._wanted(resolved_part_id, "invalid_zip", part_info)
                return {"error": "CSE returned invalid zip file"}
            self._guard.record(transient=False)
            break

        if self._refused_since is not None:
            logger.info("CSE downloads accepted again at %s; refused since %s",
                        _utc_iso(self._clock()), _utc_iso(self._refused_since))
            self._refused_since = None
            self._quota_until = 0.0
        if not kicad_files:
            return {"error": f"No KiCad files found in model archive for part {resolved_part_id}"}

        # Cache the extracted text (zip is discarded)
        self._kicad_cache.set(f"kicad:{resolved_part_id}", kicad_files)
        if self._store:
            await asyncio.to_thread(self._store.put_kicad, resolved_part_id, kicad_files, fetched_at=self._clock())

        return {
            "part_id": resolved_part_id,
            **part_info,
            "kicad_symbol": kicad_files.get("kicad_symbol"),
            "kicad_footprint": kicad_files.get("kicad_footprint"),
        }

    def store_counts(self) -> dict[str, int] | None:
        """Stored searches and KiCad parts, or None when there's no usable store (memory only)."""
        return self._store.counts() if self._store is not None and self._store.enabled else None

    async def close(self) -> None:
        """Close the HTTP client and the store."""
        if self._http:
            await self._http.aclose()
            self._http = None
        if self._store is not None:
            await asyncio.to_thread(self._store.close)
