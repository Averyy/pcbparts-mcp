"""ComponentSearchEngine (SamacSys) client using the alligator JSON API.

Uses rs.componentsearchengine.com/alligatorHandler.php — no auth required.
Returns ECAD model availability, datasheets, pin counts, and part metadata.

Authenticated endpoint for KiCad model downloads:
rs.componentsearchengine.com/ga/model.php — requires CSEARCH_USER/CSEARCH_PASS.
"""

import asyncio
import io
import logging
import zipfile
from typing import Any

import httpx

from .cache import TTLCache
from .config import (
    CSE_CONCURRENT_LIMIT,
    CSE_RATE_LIMIT,
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

# KiCad file extensions we extract from the model zip
_KICAD_EXTENSIONS = (".kicad_sym", ".kicad_mod")

# Max zip download size (50MB) to prevent zip bombs
_MAX_ZIP_SIZE = 50 * 1024 * 1024


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

    def __init__(self):
        self._cache = TTLCache(ttl=CSE_CACHE_TTL)
        self._kicad_cache = TTLCache(ttl=CSE_KICAD_CACHE_TTL, max_size=CSE_KICAD_CACHE_MAX_SIZE)
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
        cache_key = f"cse:{query.strip()}:{offset}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        params = {
            "searchString": query,
            "country": "US",
        }
        if offset > 0:
            params["offset"] = str(offset)

        try:
            async with self._get_semaphore():
                response = await self._get_http().get(_CSE_API_URL, params=params)
                await asyncio.sleep(CSE_RATE_LIMIT)
        except httpx.HTTPError:
            raise ValueError("CSE API request failed (network/connection error)")

        if response.status_code >= 400:
            raise ValueError(f"CSE API returned HTTP {response.status_code}")
        data = response.json()

        if data.get("status") != "Success":
            logger.warning(f"CSE API returned non-success status: {data.get('status')}")
            # Don't cache failed responses
            return {"results": [], "total": 0}

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
        if cached is not None:
            return {
                "part_id": resolved_part_id,
                **part_info,
                "kicad_symbol": cached.get("kicad_symbol"),
                "kicad_footprint": cached.get("kicad_footprint"),
            }

        # Download the model zip (authenticated)
        try:
            async with self._get_semaphore():
                response = await self._get_http().get(
                    _CSE_MODEL_URL,
                    params={"partID": str(resolved_part_id)},
                    auth=(CSE_USER, CSE_PASS),
                    timeout=30,
                )
                await asyncio.sleep(CSE_RATE_LIMIT)
        except httpx.HTTPError:
            return {"error": "CSE model download failed (network/connection error)"}

        if response.status_code == 401:
            return {"error": "CSE authentication failed. Check CSEARCH_USER and CSEARCH_PASS."}
        if response.status_code != 200:
            return {"error": f"CSE model download failed (HTTP {response.status_code})"}

        # Check response size to prevent zip bombs
        content_length = len(response.content)
        if content_length > _MAX_ZIP_SIZE:
            return {"error": f"CSE model download too large ({content_length} bytes, max {_MAX_ZIP_SIZE})"}

        # Extract KiCad files from zip in memory — no temp files
        kicad_files: dict[str, str] = {}
        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                for name in zf.namelist():
                    lower = name.lower()
                    # Only extract from the KiCad directory
                    if "/kicad/" not in lower:
                        continue
                    # Check decompressed size before reading
                    info = zf.getinfo(name)
                    if info.file_size > 10 * 1024 * 1024:  # 10MB per file max
                        logger.warning(f"Skipping oversized file in zip: {name} ({info.file_size} bytes)")
                        continue
                    if any(lower.endswith(ext) for ext in _KICAD_EXTENSIONS):
                        content = zf.read(name).decode("utf-8", errors="replace")
                        if lower.endswith(".kicad_sym"):
                            kicad_files["kicad_symbol"] = content
                        elif lower.endswith(".kicad_mod"):
                            kicad_files["kicad_footprint"] = content
        except zipfile.BadZipFile:
            return {"error": "CSE returned invalid zip file"}

        if not kicad_files:
            return {"error": f"No KiCad files found in model archive for part {resolved_part_id}"}

        # Cache the extracted text (zip is discarded)
        self._kicad_cache.set(cache_key, kicad_files)

        return {
            "part_id": resolved_part_id,
            **part_info,
            "kicad_symbol": kicad_files.get("kicad_symbol"),
            "kicad_footprint": kicad_files.get("kicad_footprint"),
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http:
            await self._http.aclose()
            self._http = None
