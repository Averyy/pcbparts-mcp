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
from typing import Any, Callable

import httpx

from . import stats
from .cache import TTLCache
from .cse_archive import MAX_ZIP_SIZE as _MAX_ZIP_SIZE, extract_kicad
from .cse_store import CSEStore, query_key
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


class CSEClient:
    """Async client for ComponentSearchEngine (SamacSys) search.

    Uses the alligator JSON API on the RS subdomain.
    No API key or authentication required.
    """

    def __init__(self, store_path: str | None = None, *, clock: Callable[[], float] | None = None):
        self._clock = clock or time.time
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

    async def search(self, query: str, offset: int = 0) -> dict[str, Any]:
        """Search CSE by MPN or keyword.

        Args:
            query: Part number or keyword to search for
            offset: Result offset for pagination (increments of 10)

        Returns:
            Dict with results list and total count
        """
        cache_key = f"cse:{query_key(query)}:{offset}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            stats.count_upstream("cse", "cached")
            return cached
        stored = self._store.get_search(query, offset) if self._store else None
        if stored is not None:
            self._cache.set(cache_key, stored)
            stats.count_upstream("cse", "cached")
            return stored

        params = {
            "searchString": query,
            "country": "US",
        }
        if offset > 0:
            params["offset"] = str(offset)

        # A first request for a query can come back with another status (F0R0, R0F0), holding real
        # parts or unrelated ones ("blorptastic9": 10 random parts); asking again gave "Success" in
        # all 8 checks, 2026-11-09. Reporting that first answer as empty made parts look missing.
        for attempt in range(2):
            try:
                async with self._get_semaphore():
                    stats.count_upstream("cse", "sent")
                    response = await self._get_http().get(_CSE_API_URL, params=params)
                    await asyncio.sleep(CSE_RATE_LIMIT)
            except httpx.HTTPError:
                raise ValueError("CSE API request failed (network/connection error)")

            if response.status_code >= 400:
                raise ValueError(f"CSE API returned HTTP {response.status_code}")
            data = response.json()
            if data.get("status") == "Success":
                break
            logger.warning(f"CSE API returned non-success status: {data.get('status')}")
            if attempt == 0:
                await asyncio.sleep(CSE_STATUS_RETRY_DELAY)
        else:
            raise ValueError("CSE API gave no usable answer (status other than Success, twice)")

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

        self._cache.set(cache_key, result)
        if self._store:
            self._store.put_search(query, offset, result)
        return result

    async def get_kicad(self, query: str | None = None, part_id: int | None = None) -> dict[str, Any]:
        """Download and extract KiCad symbol + footprint for a part.

        Args:
            query: MPN to search for (used to find part_id if not provided)
            part_id: CSE part ID (from a previous cse_search result)

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
            if not results:
                return {"error": f"No parts found for '{query}'"}

            # Find first result with a model available
            for r in results:
                if r.get("has_model") and r.get("cse_part_id"):
                    resolved_part_id = r["cse_part_id"]
                    part_info = r
                    break

            if not resolved_part_id:
                return {"error": f"No ECAD model available for '{query}'"}

        # Check kicad cache
        cache_key = f"kicad:{resolved_part_id}"
        cached = self._kicad_cache.get(cache_key)
        if cached is None and self._store:
            cached = self._store.get_kicad(resolved_part_id)
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
            if self._clock() < self._quota_until or self._quota_probe is not None and self._quota_probe.locked():
                return self._quota_error(resolved_part_id, part_info)
            if self._quota_probe is None:
                self._quota_probe = asyncio.Lock()
            async with self._quota_probe:
                return await self._download_kicad(resolved_part_id, part_info)
        return await self._download_kicad(resolved_part_id, part_info)

    def _wanted(self, part_id: int | str, reason: str, part_info: dict[str, Any]) -> None:
        if self._store:
            self._store.mark_wanted(part_id, reason, part_info or self._store.part_info(part_id), now=self._clock())

    def _quota_error(self, part_id: int | str, part_info: dict[str, Any]) -> dict[str, Any]:
        stats.count_upstream("cse", "rate_limited")
        self._wanted(part_id, "quota", part_info)
        return {"error": "SamacSys's daily model download limit for this shared server is used up; try again later. KiCad files pcbparts already has stored still work."}

    async def _download_kicad(self, resolved_part_id: int | str, part_info: dict[str, Any]) -> dict[str, Any]:
        # Check again inside the semaphore: a download ahead of this one may have refused quota.
        try:
            async with self._get_semaphore():
                if self._clock() < self._quota_until:
                    return self._quota_error(resolved_part_id, part_info)
                started = self._clock()
                stats.count_upstream("cse", "sent")
                response = await self._get_http().get(
                    _CSE_MODEL_URL,
                    params={"partID": str(resolved_part_id)},
                    auth=(CSE_USER, CSE_PASS),
                    timeout=30,
                )
                elapsed = self._clock() - started
                await asyncio.sleep(CSE_RATE_LIMIT)
        except httpx.HTTPError:
            return {"error": "CSE model download failed (network/connection error)"}

        # Log non-ZIP HTTP errors too, while retaining their existing authentication/HTTP replies.
        nonzip_logged = False
        if isinstance(response.content, bytes) and not zipfile.is_zipfile(io.BytesIO(response.content)):
            _warn_nonzip(response, resolved_part_id, elapsed)
            nonzip_logged = True
        if response.status_code == 401:
            return {"error": "CSE authentication failed. Check CSEARCH_USER and CSEARCH_PASS."}
        if response.status_code != 200:
            return {"error": f"CSE model download failed (HTTP {response.status_code})"}

        # Check response size to prevent zip bombs
        content_length = len(response.content)
        if content_length > _MAX_ZIP_SIZE:
            return {"error": f"CSE model download too large ({content_length} bytes, max {_MAX_ZIP_SIZE})"}

        try:
            kicad_files = extract_kicad(response.content)
        except zipfile.BadZipFile:
            text = _body_text(response.content)
            cleaned = (_clean_body(response.content) if nonzip_logged else
                       _warn_nonzip(response, resolved_part_id, elapsed))
            if "quota" in text.lower():
                now = self._clock()
                self._quota_until = now + CSE_QUOTA_RETRY_SECONDS
                if self._refused_since is None:
                    self._refused_since = now
                recent = self._store.kicad_last_24h(now) if self._store else 0
                logger.warning("CSE daily download quota refused at %s: %s downloads stored in the last 24 h; next try at %s",
                               _utc_iso(now), recent, _utc_iso(self._quota_until))
                return self._quota_error(resolved_part_id, part_info)
            if text.lower().startswith("error:"):
                if re.search(r"no\s+part\s+data\s+(?:is\s+)?available", text, re.I):
                    return {"error": f"No ECAD model available for part {resolved_part_id}"}
                self._wanted(resolved_part_id, "refused", part_info)
                return {"error": f"CSE refused the model download for part {resolved_part_id}: {cleaned[:150]}"}
            self._wanted(resolved_part_id, "invalid_zip", part_info)
            return {"error": "CSE returned invalid zip file"}

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
            self._store.put_kicad(resolved_part_id, kicad_files, fetched_at=self._clock())

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
            self._store.close()
