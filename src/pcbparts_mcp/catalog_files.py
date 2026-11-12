"""Deterministic, lossless catalog files shared by the scraper and database build.

Only standard-library imports: the scrape workflow does not install the server.
"""

import json
import logging
import math
import re
import shutil
from collections.abc import Iterator
from pathlib import Path

logger = logging.getLogger(__name__)
MAX_FILE_BYTES = 95_000_000
WARN_FILE_BYTES = 50_000_000
# transform_part's order, excluding the independently stored stock and price.
_PART_KEYS = ("l", "m", "f", "p", "t", "c", "d", "a", "x", "n")


def _lcsc_key(code: str) -> tuple[int | float, str]:
    return (int(code[1:]) if code[1:].isdigit() else float("inf"), code)


def _check_size(path: Path) -> None:
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ValueError(f"{path}: {size} bytes exceeds catalog file limit ({MAX_FILE_BYTES})")
    if size > WARN_FILE_BYTES:
        logger.warning("%s: %s bytes exceeds GitHub's 50 MB warning size", path, size)


def _valid_code(code: object) -> bool:
    return isinstance(code, str) and bool(code) and not any(c.isspace() for c in code)


def write_catalog(
    catalog_dir: Path,
    parts_by_category: dict[str, list[dict]],
    prices: dict[str, float | None],
) -> dict[str, int]:
    """Replace a staging catalog, rejecting duplicate LCSCs and oversized files.

    ``prices`` supplies the chosen snapshot prices independently of scraped rows.
    Empty categories appear in the returned counts but have no part files.
    """
    all_parts = {}
    for slug, parts in parts_by_category.items():
        if not slug or Path(slug).name != slug or slug in (".", ".."):
            raise ValueError(f"Invalid category slug: {slug!r}")
        for part in parts:
            code = part.get("l")
            if not _valid_code(code):
                raise ValueError(f"{slug}: invalid LCSC {code!r}")
            if code in all_parts:
                raise ValueError(f"Duplicate LCSC {code} in {slug}")
            if type(part.get("c")) is not int or part["c"] < 0:
                raise ValueError(f"{slug}: invalid subcategory for {code}")
            if code not in prices:
                raise ValueError(f"prices: missing {code}")
            all_parts[code] = part

    parts_dir = catalog_dir / "parts"
    if parts_dir.exists():
        shutil.rmtree(parts_dir)
    catalog_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for slug, parts in sorted(parts_by_category.items()):
        counts[slug] = len(parts)
        subcategories: dict[int, list[dict]] = {}
        for part in parts:
            subcategories.setdefault(part["c"], []).append(part)
        for sub_id, rows in sorted(subcategories.items()):
            path = parts_dir / slug / f"{sub_id}.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="\n") as stream:
                for part in sorted(rows, key=lambda row: _lcsc_key(row["l"])):
                    row = {key: part[key] for key in _PART_KEYS if key in part}
                    # Preserve any additional fields rather than silently losing data.
                    row.update((key, part[key]) for key in sorted(part)
                               if key not in row and key not in ("s", "$"))
                    stream.write(json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n")
            _check_size(path)

    codes = sorted(all_parts, key=_lcsc_key)
    for name in ("stock", "prices"):
        path = catalog_dir / f"{name}.tsv"
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            for code in codes:
                value = all_parts[code].get("s") if name == "stock" else prices[code]
                if value is None:
                    text = ""
                elif name == "stock":
                    if type(value) is not int:
                        raise ValueError(f"{path}: invalid stock for {code}: {value!r}")
                    text = str(value)
                else:
                    if type(value) not in (int, float) or not math.isfinite(value):
                        raise ValueError(f"{path}: invalid price for {code}: {value!r}")
                    text = json.dumps(value)
                stream.write(f"{code}\t{text}\n")
        _check_size(path)
    return counts


def _lines(path: Path) -> Iterator[tuple[int, str]]:
    if not path.is_file():
        raise ValueError(f"{path}: missing catalog file")
    # Decode per line so malformed UTF-8 also identifies the file and line.
    with path.open("rb") as stream:
        for number, raw in enumerate(stream, 1):
            try:
                yield number, raw.decode("utf-8")
            except UnicodeError as exc:
                raise ValueError(f"{path} line {number}: invalid UTF-8") from exc


def _read_tsv(path: Path, *, stock: bool = False) -> dict:
    values = {}
    for number, line in _lines(path):
        try:
            code, text = line.removesuffix("\n").split("\t")
            if not _valid_code(code) or code in values or "\r" in text:
                raise ValueError("invalid or duplicate LCSC, or carriage return")
            if text == "":
                value = None
            elif stock:
                if not re.fullmatch(r"-?[0-9]+", text):
                    raise ValueError("stock must be an integer")
                value = int(text)
            else:
                value = json.loads(text)
                if type(value) not in (int, float) or not math.isfinite(value):
                    raise ValueError("price must be a finite number")
                value = float(value)
        except (ValueError, OverflowError) as exc:
            raise ValueError(f"{path} line {number}: malformed TSV ({exc})") from exc
        values[code] = value
    return values


def read_prices(catalog_dir: Path) -> dict[str, float | None]:
    """Read stored prices, rejecting malformed or duplicate TSV rows."""
    return _read_tsv(catalog_dir / "prices.tsv")


def read_catalog(catalog_dir: Path, *, prices: bool = True) -> Iterator[tuple[str, dict]]:
    """Yield category and merged row; exhaust the iterator to validate orphan TSV rows.

    Categories sort alphabetically, subcategory filenames numerically, and rows
    retain file order. Corruption always raises ValueError with file/row context.
    prices=False skips prices.tsv and yields "$" as None: the scraper's previous snapshot
    when that file is missing, which the scrape then rebuilds.
    """
    stocks = _read_tsv(catalog_dir / "stock.tsv", stock=True)
    with_prices = prices
    prices = read_prices(catalog_dir) if with_prices else {}
    seen = set()
    for category in sorted((catalog_dir / "parts").glob("*")):
        files = list(category.glob("*.jsonl"))
        for path in files:
            if not path.stem.isascii() or not path.stem.isdigit():
                raise ValueError(f"{path}: invalid numeric subcategory filename")
        for path in sorted(files, key=lambda path: (int(path.stem), path.name)):
            for number, line in _lines(path):
                try:
                    part = json.loads(line)
                    if not isinstance(part, dict) or not _valid_code(part.get("l")):
                        raise ValueError("part must be an object with an LCSC")
                    code = part["l"]
                    if type(part.get("c")) is not int or part["c"] != int(path.stem):
                        raise ValueError(f"{code}: subcategory does not match filename")
                    if "s" in part or "$" in part:
                        raise ValueError(f"{code}: stock/price must be stored in TSV")
                    if code in seen:
                        raise ValueError(f"duplicate LCSC {code}")
                    for name, values in (("stock.tsv", stocks), ("prices.tsv", prices)):
                        if code not in values and (name == "stock.tsv" or with_prices):
                            raise ValueError(f"{code}: missing row in {name}")
                except ValueError as exc:
                    raise ValueError(f"{path} line {number}: {exc}") from exc
                seen.add(code)
                part["s"] = stocks.pop(code)
                part["$"] = prices.pop(code) if with_prices else None
                yield category.name, part
    for name, values in (("stock.tsv", stocks), ("prices.tsv", prices)):
        if values:
            code = next(iter(values))
            raise ValueError(f"{catalog_dir / name}: {code} has no part")
