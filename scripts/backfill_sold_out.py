#!/usr/bin/env python3
"""Seed data/catalog/sold_out/ from the daily catalogs in this repository's git history.

Replays the scrape's sold-out step (scrape_components.update_sold_out) over each pair of consecutive
committed catalogs on HEAD's first-parent history, from the first with data/catalog/stock.tsv (the
catalog format of 0.9.0, 2026-11-12), and writes the result beside HEAD's catalog: each part gets the
date of the first scrape it was missing from, as the daily scrape would have given it. Offline: git
only. A part that left before the first of those catalogs isn't known, so it isn't seeded.

Run it on a checkout whose working catalog is HEAD's (no scrape output on top), after rebasing on the
newest main so the result matches the newest catalog, then review and commit data/catalog/sold_out/.
The daily scrape keeps the files up to date from then on.

Usage:
    uv run python scripts/backfill_sold_out.py
"""

import argparse
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from pcbparts_mcp.catalog_files import SOLD_OUT_DIR, read_catalog, write_sold_out  # noqa: E402
from scrape_components import update_sold_out  # noqa: E402

CATALOG = "data/catalog"


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, check=True).stdout


def catalog_codes(repo: Path, rev: str) -> set[str]:
    """The LCSC codes a commit's catalog lists (its stock.tsv)."""
    return {line.split(b"\t", 1)[0].decode() for line in git(repo, "show", f"{rev}:{CATALOG}/stock.tsv").splitlines()}


def scrape_date(repo: Path, rev: str) -> str:
    """The UTC date of the scrape a commit's catalog came from (its manifest's scraped_at)."""
    return json.loads(git(repo, "show", f"{rev}:data/manifest.json"))["scraped_at"][:10]


def extract_catalog(repo: Path, rev: str, target: Path) -> Path:
    """A commit's catalog files (parts, stock.tsv, prices.tsv) unpacked under target."""
    archive = subprocess.Popen(["git", "archive", "--format=tar", rev, CATALOG], cwd=repo, stdout=subprocess.PIPE)
    with tarfile.open(fileobj=archive.stdout, mode="r|") as tar:
        tar.extractall(target, filter="data")
    if archive.wait() != 0:
        raise RuntimeError(f"git archive {rev} failed")
    return target / CATALOG


def backfill(repo: Path) -> dict[str, dict]:
    revs = git(repo, "rev-list", "--first-parent", "--reverse", "HEAD", "--", f"{CATALOG}/stock.tsv").decode().split()
    if len(revs) < 2:
        raise SystemExit("Need at least two committed catalogs to compare")
    sold: dict[str, dict] = {}
    with tempfile.TemporaryDirectory() as temporary:
        for previous, current in zip(revs, revs[1:]):
            previous_dir = extract_catalog(repo, previous, Path(temporary) / previous)
            day = scrape_date(repo, current)
            sold, changes = update_sold_out(read_catalog(previous_dir), catalog_codes(repo, current), sold.values(), day)
            print(f"{day} ({current[:8]}): {changes['new']:,} gone, {changes['back']:,} back, {changes['kept']:,} sold out")
            shutil.rmtree(Path(temporary) / previous)  # about 350 MB each: free it before the next
    return sold


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed data/catalog/sold_out/ from the catalogs in git history")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    changed = git(args.repo, "status", "--porcelain", "--", CATALOG, f":!{CATALOG}/{SOLD_OUT_DIR}").decode()
    if changed.strip():
        raise SystemExit(f"{CATALOG} differs from HEAD's (a scrape's output?): the result would not match it")
    sold = backfill(args.repo)
    counts = write_sold_out(args.repo / CATALOG, sold)
    for name, count in counts.items():
        print(f"{CATALOG}/{SOLD_OUT_DIR}/{name}: {count:,} parts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
