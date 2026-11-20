"""KiCad extraction shared by SamacSys downloads and the operator's ZIP import."""

import io
import logging
import zipfile

logger = logging.getLogger(__name__)
MAX_ZIP_SIZE = 50 * 1024 * 1024
MAX_KICAD_FILE_SIZE = 10 * 1024 * 1024


def extract_kicad(content: bytes) -> dict[str, str]:
    """Read only .kicad_sym/.kicad_mod files under /kicad/, without writing archive paths."""
    if len(content) > MAX_ZIP_SIZE:
        raise ValueError(f"CSE model download too large ({len(content)} bytes, max {MAX_ZIP_SIZE})")
    files = {}
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        for info in archive.infolist():
            lower = info.filename.lower()
            if "/kicad/" not in lower:
                continue
            if info.file_size > MAX_KICAD_FILE_SIZE:
                logger.warning("Skipping oversized file in zip: %s (%s bytes)", info.filename, info.file_size)
                continue
            key = ("kicad_symbol" if lower.endswith(".kicad_sym") else
                   "kicad_footprint" if lower.endswith(".kicad_mod") else None)
            if key:
                files[key] = archive.read(info).decode("utf-8", errors="replace")
    return files
